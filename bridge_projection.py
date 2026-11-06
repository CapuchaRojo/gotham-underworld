"""C1 player projection: explicit fields, no world snapshots or raw events."""
from copy import deepcopy

import daily_life
import game_service
from career_state import DAILY_ACTION_ALLOWANCE
from location_registry import load
from navigation import DAILY_TU
import ordinary_life


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
