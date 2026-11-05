"""M015 neighborhood adapters: finite opportunities, room terms and known contacts."""
from copy import deepcopy

import choice_engine
from life_content import fingerprint, load
from simulation import event

VERSION = 1
TESS = 'goon.contact.tess'
CAL = 'goon.contact.cal'


def _state(world):
    life = world.get('daily_life')
    if life is None:
        raise ValueError('Daily life is not enabled; inspect life and explicitly settle_in')
    if world['day'] < life['activation_day']:
        raise ValueError('Daily life activates after the next wait; loading does not activate it')
    return life


def settle_in(world):
    import navigation
    if 'daily_life_version' in world:
        raise ValueError('Daily life is already enabled or scheduled')
    nav, content = navigation._active(world), load()
    if world['player']['arrested']:
        raise ValueError('Cannot accept a room arrangement while detained')
    if nav['location_id'] not in (content['home_id'], content['hub_id']):
        raise ValueError('Visit the cooperative home or its n13 public hub to settle in')
    if nav['home_id'] not in (None, content['home_id']):
        raise ValueError('An existing different home needs a separate housing contract')
    nav['home_id'] = content['home_id']
    if nav['home_id'] not in nav['permissions']:
        nav['permissions'].append(nav['home_id'])
        nav['permissions'].sort()
    day = world['day']
    world['daily_life_version'] = VERSION
    world['daily_life'] = dict(rules_version=1, content_fingerprint=fingerprint(),
        enabled_day=day, activation_day=day + 1, last_tick_day=day,
        home_id=nav['home_id'], opening_cash=world['player']['cash'],
        housing=dict(next_due_day=day + content['room_period'], arrears=0, prepaid=0, history=[]),
        contacts={ident: dict(standing=0, memories=[]) for ident in sorted(content['contacts'])},
        promises={}, choices={}, transactions=[])
    return event(world, 'life_enabled',
        f'Accepted the cooperative arrangement: $30 every seven days, first due day {day + 7}; '
        'available cash is charged, unpaid balance is capped at $30, and basic room access continues. '
        'Local opportunities begin after the next wait.',
        schema_version=1, activation_day=day + 1, due_day=day + 7,
        home_id=nav['home_id'], command_id=world['command_sequence'] + 1, cause='explicit_enrollment')


def record_balance(world, cause, source_id, *, command_id=None, force=False):
    """Record actual cash; never pay a second time for an existing domain outcome."""
    life = world.get('daily_life')
    if life is None:
        return None
    before = life['transactions'][-1]['after'] if life['transactions'] else life['opening_cash']
    after = world['player']['cash']
    if before == after and not force:
        return None
    item = dict(id=f'goon.transaction.{len(life["transactions"]) + 1}', day=world['day'],
        before=before, after=after, amount=after - before, cause=cause,
        source_id=source_id, command_id=command_id)
    life['transactions'].append(item)
    event(world, 'life_transaction', f'{cause}: cash ${before} -> ${after}.', schema_version=1, **deepcopy(item))
    return item['id']


def _memory(world, contact, fact, delta, source):
    person = world['daily_life']['contacts'][contact]
    before = person['standing']
    person['standing'] = max(-10, min(10, before + delta))
    item = dict(id=f'{contact}.memory.{len(person["memories"]) + 1}', day=world['day'],
        fact=fact, source_id=source, before=before, after=person['standing'], delta=person['standing'] - before)
    person['memories'].append(item)
    event(world, 'life_memory', f'{contact_definitions(world)[contact]["name"]} remembers {fact.replace("_", " ")}.',
          schema_version=1, contact_id=contact, **deepcopy(item))
    return item['id']


def _knows(life, fact):
    contact, observations = {
        'cal_terms': (CAL, ('terms_disclosed',)),
        'tess_reference': (TESS, ('promise_kept',)),
        'cal_quiet_work': (CAL, ('collection_completed',)),
    }[fact]
    return any(m['fact'] in observations for m in life['contacts'][contact]['memories'])


def _open(world, ident, definition, week, open_day, expires_day, source):
    life = world['daily_life']
    if ident not in life['choices']:
        life['choices'][ident] = dict(id=ident, definition_id=definition, source_id=source,
            week=week, open_day=open_day, expires_day=expires_day, state='open', selection=None)
        event(world, 'life_opportunity', f'Opportunity recorded: {load()["choices"][definition]["title"]}.',
              schema_version=1, choice_id=ident, source_id=source, open_day=open_day,
              expires_day=expires_day, cause='local_roster')


def _week_roster(world):
    life, content = world['daily_life'], load()
    week = (world['day'] - life['activation_day']) // 7
    base = life['activation_day'] + week * 7
    for key, definition in sorted(content['choices'].items()):
        if definition.get('dynamic') or (key == 'cal_intro' and _knows(life, 'cal_terms')):
            continue
        open_day = base + definition['start']
        expires_day = open_day + definition['duration']
        # A supported legacy clock-only save may resume partway through a new
        # roster week. Do not create already-expired offers at its next tick.
        if expires_day <= world['day']:
            continue
        _open(world, f'goon.choice.{week}.{key}', key, week,
              open_day, expires_day,
              f'goon.roster.{week}.{key}')


def _housing_snapshot(housing):
    return {k: housing[k] for k in ('next_due_day', 'arrears', 'prepaid')}


def _housing_receipt(world, kind, source, before, *, paid=0, transaction_id=None, assessed=0, credit=0):
    housing = world['daily_life']['housing']
    item = dict(id=f'goon.room.receipt.{len(housing["history"]) + 1}', day=world['day'],
        operation=kind, source_id=source, before=before, after=_housing_snapshot(housing),
        paid=paid, transaction_id=transaction_id, assessed=assessed, credit=credit)
    housing['history'].append(item)
    event(world, 'life_housing', f'Room {kind}: paid ${paid}, prepaid ${housing["prepaid"]}, '
          f'unpaid ${housing["arrears"]}; next review day {housing["next_due_day"]}.',
          schema_version=1, **deepcopy(item))
    return item['id']


def _room_due(world):
    life, content = world['daily_life'], load()
    housing = life['housing']
    while housing['next_due_day'] <= world['day']:
        before = _housing_snapshot(housing)
        due = housing['next_due_day']
        cycle = (due - life['enabled_day']) // 7
        source = f'goon.obligation.room.{cycle}'
        assessed = 0 if housing['arrears'] else content['room_amount']
        balance = housing['arrears'] + assessed
        credit = min(balance, housing['prepaid'])
        paid = min(world['player']['cash'], balance - credit)
        world['player']['cash'] -= paid
        housing['arrears'] = balance - credit - paid
        housing['prepaid'] -= credit
        housing['next_due_day'] += 7
        tx = record_balance(world, 'room_payment', source, force=True)
        _housing_receipt(world, 'due', source, before, paid=paid, transaction_id=tx, assessed=assessed, credit=credit)
        if housing['arrears']:
            _open(world, f'goon.choice.room.{cycle}', 'room_review', (due - life['activation_day']) // 7,
                  world['day'], world['day'] + 7, source)


def _promise_id(week):
    return f'goon.promise.{week}.tess'


def _finish_promise(world, promise, status, source):
    if promise['status'] != 'pending':
        raise ValueError('This promise is already closed')
    promise.update(status=status, resolved_day=world['day'], resolution_source=source)
    fact, delta = ('promise_kept', 3) if status == 'kept' else ('promise_broken', -2)
    _memory(world, TESS, fact, delta, source)
    event(world, 'life_promise', f'Tess promise {status}; no cash awarded.', schema_version=1,
          promise_id=promise['id'], status=status, source_id=source, due_day=promise['due_day'], cause='personal_commitment')


def begin_day(world):
    """One phase after existing court/navigation; never called by a read or load."""
    life = world.get('daily_life')
    if life is None or life['last_tick_day'] >= world['day']:
        return
    record_balance(world, 'existing_rules', f'goon.day.{world["day"]}')
    life['last_tick_day'] = world['day']
    if world['day'] < life['activation_day']:
        return
    _room_due(world)
    for ident, promise in sorted(life['promises'].items()):
        if promise['status'] == 'pending' and world['day'] >= promise['due_day']:
            _finish_promise(world, promise, 'broken', ident)
    for ident, record in sorted(life['choices'].items()):
        if record['state'] == 'open' and world['day'] >= record['expires_day']:
            record['state'] = 'expired'
            event(world, 'life_expired', 'An unselected opportunity expired; no payout.', schema_version=1,
                  choice_id=ident, source_id=record['source_id'], cause='offer_deadline')
    _week_roster(world)
    event(world, 'life_day', 'Neighborhood obligations and opportunities reviewed once.',
          schema_version=1, processed_day=world['day'], cause='day_transition')


def pay_room(world):
    life = _state(world)
    if world['player']['arrested'] or world['navigation']['location_id'] != life['home_id']:
        raise ValueError('Visit home while free to make a room payment')
    housing = life['housing']
    kind = 'arrears_payment' if housing['arrears'] else 'prepay'
    remaining = housing['arrears'] or (30 - housing['prepaid'])
    paid = min(world['player']['cash'], remaining)
    if paid <= 0:
        raise ValueError('No payable balance or no cash; basic home access remains available')
    before = _housing_snapshot(housing)
    world['player']['cash'] -= paid
    if kind == 'prepay':
        housing['prepaid'] += paid
    else:
        housing['arrears'] -= paid
    source = f'goon.command.{world["command_sequence"] + 1}'
    tx = record_balance(world, 'room_payment', source, command_id=world['command_sequence'] + 1)
    _housing_receipt(world, kind, source, before, paid=paid, transaction_id=tx)
    return event(world, 'life_payment', f'Paid ${paid} toward the room; no action or travel allowance refreshed.',
                 transaction_id=tx, cause='voluntary_room_payment')


def _context(world, choice_id):
    life = _state(world)
    record = life['choices'].get(choice_id)
    if record is None:
        raise ValueError('Unknown opportunity; inspect opportunities')
    return life, record, load()['choices'][record['definition_id']]


def _slot(record, definition):
    return f'goon.slot.{record["week"]}.{definition["slot"]}' if definition['slot'] else None


def _assess(world, life, record, definition, option):
    if option.get('known') and not _knows(life, option['known']):
        return 'hidden', None
    contact = option.get('standing_contact')
    if contact and life['contacts'][contact]['standing'] < option['minimum_standing']:
        return 'unavailable', (f'{load()["contacts"][contact]["name"]} requires standing {option["minimum_standing"]}; '
                               f'current known standing is {life["contacts"][contact]["standing"]}. Inspect the other listed options.')
    effect = option['effect']
    if effect != 'decline' and world['player']['arrested']:
        return 'unavailable', 'Unavailable while detained; existing court and wait remain available'
    place = life['home_id'] if option.get('place') == 'home' else option.get('place')
    if place and world['navigation']['location_id'] != place:
        return 'unavailable', f'Visit {place} first; travel is separate and never automatic'
    promise = life['promises'].get(_promise_id(record['week']))
    if effect in ('keep_promise', 'move_promise', 'break_promise'):
        if not promise or promise['status'] != 'pending':
            return 'unavailable', 'No pending personal promise for this roster'
        if effect == 'move_promise' and promise['renegotiated']:
            return 'unavailable', 'The promise was already moved once'
    if effect == 'criminal_work' and world['player']['faction'] is None:
        return 'unavailable', 'Requires an explicitly chosen faction; use the existing join command if desired'
    if effect == 'room_help' and life['housing']['arrears'] <= 0:
        return 'unavailable', 'No unpaid room balance to work against'
    slot = _slot(record, definition)
    if option['actions'] and slot and any(r['selection'] and r['selection']['outcome'].get('slot') == slot for r in life['choices'].values()):
        return 'unavailable', 'That roster slot is already committed; another daily action cannot duplicate it'
    from game_service import actions_remaining
    if option['actions'] > actions_remaining(world):
        return 'unavailable', 'Daily actions exhausted for this option; wait or decline'
    return 'available', None


def choice_report(world, choice_id):
    life, record, definition = _context(world, choice_id)
    report = choice_engine.present(world, record, definition,
        lambda option: _assess(world, life, record, definition, option))
    report['speaker'] = 'Your neighborhood planner' if definition['speaker'] == 'player' else load()['contacts'][definition['speaker']]['name']
    report['promise'] = deepcopy(life['promises'].get(_promise_id(record['week'])))
    return report


def choice_cost(world, choice_id, option_id):
    life, record, definition = _context(world, choice_id)
    return choice_engine.eligible(world, record, definition, option_id,
        lambda option: _assess(world, life, record, definition, option))['actions']


def _apply(world, life, record, definition, option):
    effect = option['effect']
    source, result = record['id'], dict(effect=effect, slot=_slot(record, definition) if option['actions'] else None)
    command_id = world['command_sequence'] + 1
    promise = life['promises'].get(_promise_id(record['week']))
    if effect == 'lawful_work':
        world['player']['cash'] += option['pay']
        result['transaction_id'] = record_balance(world, 'lawful_wage', source, command_id=command_id)
        _memory(world, TESS, 'work_completed', 1, source)
        result['feedback'] = f'Earned ${option["pay"]} from the store roster. Tess records the completed shift.'
    elif effect == 'criminal_work':
        from legal_engine import job
        outcome = job(world, option['job'])
        result.update(source_attempt=outcome['attempt'], success=outcome['success'], payout=outcome['payout'])
        result['transaction_id'] = record_balance(world, 'criminal_job', source, command_id=command_id, force=True)
        _memory(world, CAL, option['job'] + ('_completed' if outcome['success'] else '_failed'), 2 if outcome['success'] else -1, source)
        result['feedback'] = outcome['message'] + ' Cal knows the result of his referral; no second payment was made.'
    elif effect == 'introduction':
        _memory(world, CAL, 'terms_disclosed', 0, source)
        result['feedback'] = 'Cal disclosed collection terms. Affiliation remains your decision; success and police exposure are uncertain.'
    elif effect == 'make_promise':
        ident = _promise_id(record['week'])
        base = life['activation_day'] + record['week'] * 7
        life['promises'][ident] = dict(id=ident, week=record['week'], contact_id=TESS,
            due_day=base + 2, status='pending', renegotiated=False, source_id=source,
            resolved_day=None, resolution_source=None)
        _memory(world, TESS, 'promise_accepted', 0, source)
        result['feedback'] = f'Promised the second-morning favor, before day {base + 2}. No wage is attached.'
    elif effect in ('keep_promise', 'break_promise'):
        _finish_promise(world, promise, 'kept' if effect == 'keep_promise' else 'broken', source)
        result['feedback'] = 'Promise kept; Tess offers a stock-audit reference. No money awarded.' if effect == 'keep_promise' else 'Promise closed as broken; Tess remembers, and ordinary work remains possible.'
    elif effect == 'move_promise':
        base = life['activation_day'] + record['week'] * 7
        promise.update(due_day=base + 4, renegotiated=True)
        _memory(world, TESS, 'promise_moved', 0, source)
        _open(world, f'goon.choice.{record["week"]}.rescheduled_help', 'rescheduled_help', record['week'],
              base + 3, base + 4, promise['id'])
        result['feedback'] = f'Tess agrees once: help on day {base + 3}, before day {base + 4}. This morning\'s roster is forgone.'
    elif effect == 'room_help':
        housing = life['housing']
        before = _housing_snapshot(housing)
        credit = min(10, housing['arrears'])
        housing['arrears'] -= credit
        _housing_receipt(world, 'work_credit', source, before, credit=credit)
        result['feedback'] = f'Maintenance reduced the unpaid balance by ${credit}. No cash or standing reward.'
    else:
        result['feedback'] = 'Opportunity declined. No money, standing reward, or time refresh; other paths remain open.'
    return result


def choose(world, choice_id, option_id):
    life, record, definition = _context(world, choice_id)
    return choice_engine.resolve(world, record, definition, option_id,
        lambda option: _assess(world, life, record, definition, option),
        lambda option: _apply(world, life, record, definition, option))


def opportunities(world):
    life = _state(world)
    return [choice_report(world, ident) for ident, r in sorted(life['choices'].items())
            if r['state'] == 'open' and r['expires_day'] > world['day']]


def contact_definitions(world):
    definitions = load()['contacts']
    from incident_dispatch import contacts
    definitions.update(contacts(world))
    return definitions


def contact_report(world):
    life, definitions = _state(world), contact_definitions(world)
    from incident_dispatch import contact_view
    public_fields = ('name', 'role', 'personality', 'need', 'knowledge')
    memory_fields = ('id', 'day', 'fact', 'source_id', 'before', 'after', 'delta')
    return deepcopy([dict(id=ident, standing=standing,
                         memories=[{key: memory[key] for key in memory_fields} for memory in memories],
                         **{key: definitions[ident][key] for key in public_fields})
                     for ident, person in sorted(life['contacts'].items())
                     for standing, memories in [contact_view(world, ident, person)]])


def life_report(world):
    life = world.get('daily_life')
    if life is None:
        return dict(enabled=False, terms='$30 every seven days after explicit settle_in; first due seven days after acceptance. '
                    'Available cash is charged; arrears cap $30 with continued basic home access. No retroactive charges.')
    pending = world['day'] < life['activation_day']
    housing = deepcopy(life['housing'])
    return deepcopy(dict(enabled=True, pending=pending, activation_day=life['activation_day'], day=world['day'],
        home_id=life['home_id'], cash=world['player']['cash'], housing=housing,
        status='grace' if housing['arrears'] else 'current', promises=list(life['promises'].values()),
        transactions=life['transactions'],
        monologue=f'The room review is on day {housing["next_due_day"]}; ${housing["prepaid"]} is already set aside.'))


def home_report(world):
    life = _state(world)
    if world['navigation']['location_id'] != life['home_id']:
        raise ValueError('Visit the recorded home for the home review; life shows your terms remotely')
    report = life_report(world)
    report['opportunities'] = opportunities(world)
    if 'ordinary_version' in world:
        from ordinary_life import report as ordinary_report
        report['ordinary'] = ordinary_report(world)
    report['help'] = 'pay_room sets aside cash once per payment toward the bounded balance. Inspection grants no cash, actions, or TU.'
    return report
