"""C1 player projection: explicit fields, no world snapshots or raw events."""
from copy import deepcopy

import daily_life
import game_service
from career_state import DAILY_ACTION_ALLOWANCE
from location_registry import load
from navigation import DAILY_TU
import ordinary_life
from bridge_checkpoint import BridgeError


RENT_SETTLEMENTS = ('prepay', 'arrears_payment', 'due')


def _status(world, version, slot):
    if version not in world:
        return 'not_adopted'
    return 'pending' if world['day'] < world[slot]['activation_day'] else 'active'


def _choice(report, command):
    result = {key: deepcopy(report[key]) for key in
              ('id', 'title', 'situation', 'speaker', 'open_day', 'expires_day', 'state', 'options')}
    result['command'] = command
    name = 'choice_id' if command == 'choose' else 'offer_id'
    for option in result['options']:
        option['arguments'] = {name: report['id'], 'option_id': option['id']}
    return result


def player_view(world):
    """Never initialize state; deliberately omit incident/institution narratives."""
    day = world['day']
    systems = dict(navigation=_status(world, 'navigation_version', 'navigation'),
                   daily_life=_status(world, 'daily_life_version', 'daily_life'),
                   ordinary=_status(world, 'ordinary_version', 'ordinary'))
    systems['mobility'] = world['mobility']['adoption']['status'] if 'mobility_version' in world else 'not_adopted'
    nav = world.get('navigation')
    active_nav = systems['navigation'] == 'active'
    location = None
    if active_nav:
        place = next(p for p in load()['places'] if p['id'] == nav['location_id'])
        location = dict(id=place['id'], label=place['label'])
    result = dict(day=day, player={k: world['player'][k] for k in ('cash', 'heat', 'custody')},
                  budgets=dict(daily_actions=DAILY_ACTION_ALLOWANCE, actions_remaining=game_service.actions_remaining(world),
                               daily_travel_units=DAILY_TU,
                               travel_units_remaining=DAILY_TU - nav['tu_used'] if active_nav else None),
                  location=location, systems=systems, housing=None, contacts=[],
                  opportunities=[], outcomes=[])
    if 'daily_life_version' in world:
        report = daily_life.life_report(world)
        result['housing'] = dict(status=report['status'], home_id=report['home_id'],
                                 **{k: report['housing'][k] for k in ('next_due_day', 'arrears', 'prepaid')})
    if systems['daily_life'] == 'active':
        # Only the two life-enrollment contacts; no incident actors or private memories.
        result['contacts'] = [{k: p[k] for k in ('id', 'name', 'role', 'standing')}
                              for p in daily_life.contact_report(world)
                              if p['id'] in (daily_life.TESS, daily_life.CAL)]
        result['opportunities'] = [_choice(r, 'choose') for r in daily_life.opportunities(world)]
        selections = [(r['selection']['command_id'], r) for r in world['daily_life']['choices'].values()
                      if r['selection'] is not None]
        for _, row in sorted(selections)[-10:]:
            selection = row['selection']
            result['outcomes'].append(dict(choice_id=row['id'], option_id=selection['option_id'],
                                           day=selection['day'], feedback=selection['outcome']['feedback']))
    if systems['ordinary'] == 'active':
        report = ordinary_life.report(world)
        result['ordinary'] = dict(employment=report['employment'],
                                  assistance={k: report['assistance'][k] for k in ('status', 'amount', 'due_day')})
        result['opportunities'].extend(_choice(r, 'ordinary_choose') for r in report['offers'])
    return deepcopy(result)


def _require_housing(condition):
    if not condition:
        raise BridgeError('INVALID_CHECKPOINT', 'Housing settlement details are unavailable.', 503)


def _rent_rows(life):
    return [row for row in life.get('housing', {}).get('history', ()) if row['operation'] in RENT_SETTLEMENTS]


def _rent_transactions(life):
    transactions = [row for row in life.get('transactions', ()) if row['cause'] == 'room_payment']
    by_id = {row['id']: row for row in transactions}
    _require_housing(len(by_id) == len(transactions))
    return by_id


def _settlement(life, row, transactions):
    transaction = transactions.get(row['transaction_id'])
    _require_housing(transaction is not None and transaction['source_id'] == row['source_id']
                     and transaction['day'] == row['day'] and transaction['amount'] == -row['paid'])
    if row['operation'] == 'due':
        cycle = (row['before']['next_due_day'] - life['enabled_day']) // 7
        _require_housing(transaction['command_id'] is None and row['source_id'] == f'goon.obligation.room.{cycle}')
    else:
        ident = transaction['command_id']
        _require_housing(type(ident) is int and row['source_id'] == f'goon.command.{ident}')
    return dict(day=row['day'], kind=row['operation'], paid=row['paid'], credit_applied=row['credit'],
                balance_after=dict(cash=str(transaction['after']), arrears=row['after']['arrears'],
                                   prepaid=row['after']['prepaid'], next_due_day=row['after']['next_due_day']))


def housing_view(world):
    """Read the contextual gate and the most recent cash-linked settlement."""
    life = world.get('daily_life', {})
    rows = _rent_rows(life)
    latest = _settlement(life, rows[-1], _rent_transactions(life)) if rows else None
    return dict(pay_room=daily_life.room_payment_plan(world)[0], latest_settlement=latest)


def _command_frame(events, receipt):
    """The frame ends at the recorded player command, after its effects."""
    start = 0
    frame = None
    for index, event in enumerate(events):
        if event['kind'] != 'player_command':
            continue
        if event['command_id'] == receipt['command_sequence']:
            _require_housing(frame is None and event['actor'] == 'player'
                             and event['command'] == receipt['command'] and event['day'] == receipt['day'])
            frame = events[start:index]
        start = index + 1
    _require_housing(frame is not None)
    return frame


def operation_housing_settlements(world, receipt):
    """Attribute recorded rent rows to the exact durable command frame."""
    frame = _command_frame(world['events'], receipt)
    housing_events = [(i, e) for i, e in enumerate(frame)
                      if e['kind'] == 'life_housing' and e['operation'] in RENT_SETTLEMENTS]
    transaction_events = [(i, e) for i, e in enumerate(frame)
                          if e['kind'] == 'life_transaction' and e['cause'] == 'room_payment']
    life = world.get('daily_life', {})
    command = receipt['command']
    if command == 'pay_room':
        source = f'goon.command.{receipt["command_sequence"]}'
        rows = [row for row in _rent_rows(life)
                if row['operation'] in ('prepay', 'arrears_payment') and row['source_id'] == source]
        _require_housing(len(rows) == 1)
    elif command == 'wait':
        # Day identifies records to check for displaced links, never the
        # operation that owns them. Both events must match inside this frame.
        rows = [row for row in _rent_rows(life) if row['operation'] == 'due' and row['day'] == receipt['day']]
    else:
        rows = []
    _require_housing(len(rows) == len(housing_events) == len(transaction_events))
    if not rows:
        return []
    transactions = _rent_transactions(life)
    result = []
    seen = set()
    for row, (housing_index, housing_event), (tx_index, tx_event) in zip(rows, housing_events, transaction_events):
        ident = row['transaction_id']
        _require_housing(ident not in seen and tx_index < housing_index and row['day'] == receipt['day']
                         and all(housing_event.get(k) == v for k, v in row.items()))
        result.append(_settlement(life, row, transactions))
        _require_housing(all(tx_event.get(k) == v for k, v in transactions[ident].items()))
        if command == 'pay_room':
            _require_housing(transactions[ident]['command_id'] == receipt['command_sequence'])
        seen.add(ident)
    return result
