"""M012 heat, documented scrutiny, and bounded legal choices; no character policy."""
from legal_state import HEAT_LIMIT, RESPONSE_RULES, attention
from simulation import event, resolve_case


def change_heat(world, delta, cause, **source):
    before = world['player']['heat']
    after = max(0, min(HEAT_LIMIT, before + delta))
    world['player']['heat'] = after
    if before != after:
        return event(world, 'heat_change', f'Heat changed from {before} to {after}: {cause}.',
                     before=before, after=after, delta=after - before,
                     tier_before=attention(before)['tier'], tier_after=attention(after)['tier'],
                     cause=cause, **source)


def job(world, kind):
    from gameplay import job as legacy_job
    before = world['player']['heat']
    result = legacy_job(world, kind, scrutiny=attention(before))
    delta = world['player']['heat'] - before
    world['player']['heat'] = before
    change_heat(world, delta, 'player_job', source_attempt=result['attempt'])
    if kind == 'collection':
        world['legal']['last_crime_day'] = world['day']
    return result


def lay_low(world):
    player, legal = world['player'], world['legal']
    if player['arrested']:
        raise ValueError('Cannot lay low while detained')
    if player['heat'] <= 0:
        raise ValueError('No heat to reduce')
    if legal['last_lay_low_day'] == world['day']:
        raise ValueError('Can only lay low once per day')
    legal['last_lay_low_day'] = world['day']
    change_heat(world, -RESPONSE_RULES['lay_low']['heat_relief'], 'lay_low')
    return event(world, 'legal_response', 'Laid low; heat reduced without erasing documented evidence.',
                 action='lay_low', cash_cost=0, cause='player_legal_response')


def _case(world, case_id, action):
    if not case_id.isascii() or not case_id.isdecimal() or int(case_id) <= 0:
        raise ValueError('case_id must be a positive case number')
    case = next((c for c in world['cases'] if c['id'] == int(case_id)), None)
    if case is None:
        raise ValueError('Unknown case')
    if str(case['id']) in world['legal']['responses']:
        raise ValueError('A legal response is already committed for this case')
    if action == 'accept':
        if case['status'] not in ('pending', 'charged'):
            raise ValueError('Can only accept a pending or charged case')
        if world['player']['arrested'] and case['status'] != 'charged':
            raise ValueError('Resolve the charged case before another case')
    elif (world['player']['arrested'] or case['status'] != 'pending' or
          not case.get('witnessed') or case['evidence'] <= 0):
        raise ValueError('Requires freedom and a documented pending witness case')
    return case


def _response(world, case, action):
    response = {'action': action, 'day': world['day'], 'reviewed': action != 'contest',
                'review_day': world['day'] + RESPONSE_RULES['contest']['review_days'] if action == 'contest' else None}
    world['legal']['responses'][str(case['id'])] = response
    return response


def cooperate(world, case_id):
    case = _case(world, case_id, 'cooperate')
    _response(world, case, 'cooperate')
    before = case['evidence']
    case['evidence'] += 1
    fine = RESPONSE_RULES['cooperate']['fine']
    change_heat(world, -RESPONSE_RULES['cooperate']['heat_relief'], 'cooperation', case_id=case['id'])
    return event(world, 'legal_response', f'Cooperated on case {case["id"]}; evidence documented, potential fine reduced to ${fine}.',
                 action='cooperate', case_id=case['id'], evidence_before=before,
                 evidence_after=case['evidence'], fine_assessed=fine, cash_cost=0, cause='player_legal_response')


def contest(world, case_id):
    case = _case(world, case_id, 'contest')
    cost = RESPONSE_RULES['contest']['cash_cost']
    if world['player']['cash'] < cost:
        raise ValueError(f'Need ${cost} to contest allegations')
    world['player']['cash'] -= cost
    response = _response(world, case, 'contest')
    return event(world, 'legal_response', f'Contested case {case["id"]}; review scheduled for day {response["review_day"]}.',
                 action='contest', case_id=case['id'], cash_cost=cost,
                 review_day=response['review_day'], evidence=case['evidence'], cause='player_legal_response')


def _record(world, case, fine, paid, choice):
    record = {'case_id': case['id'], 'day': world['day'], 'outcome': case['status'],
              'fine_assessed': fine, 'fine_paid': paid, 'response': choice}
    world['legal']['record'].append(record)
    return event(world, 'legal_outcome', f'Case {case["id"]}: {case["status"]}; fine paid ${paid}.',
                 **record, evidence=case['evidence'], cause='case_resolution')


def resolve(world, *, legacy=False):
    case = next((c for c in world['cases'] if c['status'] == 'charged'), None)
    if case is None:
        return resolve_case(world)
    choice = world['legal']['responses'].get(str(case['id']), {}).get('action', 'none')
    fine = 50 if legacy else RESPONSE_RULES.get(choice, {}).get('fine', 50)
    relief = 2 if legacy else (RESPONSE_RULES['accept']['heat_relief'] if choice == 'accept' else
                              RESPONSE_RULES['cooperate']['court_heat_relief'] if choice == 'cooperate' else 2)
    before_cash = world['player']['cash']
    start = len(world['events'])
    resolve_case(world, fine=fine, heat_relief=0)
    paid = before_cash - world['player']['cash']
    if case['status'] == 'convicted':
        change_heat(world, -relief, 'court_resolution', case_id=case['id'])
    else:
        fine = 0
    for item in world['events'][start:]:
        if item['kind'] == 'court':
            item.update(case_id=case['id'], outcome=case['status'], fine_assessed=fine, fine_paid=paid, response=choice)
    return _record(world, case, fine, paid, choice)


def accept(world, case_id):
    case = _case(world, case_id, 'accept')
    _response(world, case, 'accept')
    before = case['evidence']
    was_charged = case['status'] == 'charged'
    case['evidence'] = max(3, before)
    case['status'] = 'charged'
    world['player']['arrested'] = True
    world['player']['custody'] = 'pretrial'
    fine = RESPONSE_RULES['accept']['fine']
    event(world, 'legal_response', f'Accepted consequences for case {case["id"]}; an immediate ${fine} fine is assessed.',
          action='accept', case_id=case['id'], cash_cost=0, evidence_before=before,
          evidence_after=case['evidence'], cause='player_legal_response')
    if not was_charged:
        event(world, 'charge', f'Voluntary admission recorded for case {case["id"]}.',
              case_id=case['id'], custody_before='free', custody_after='pretrial', cause='voluntary_admission')
    return resolve(world)


def begin_day(world):
    """Process legal reviews/quiet-day cooling once, before ordinary investigation."""
    legal = world['legal']
    if legal['last_tick_day'] < world['day']:
        legal['last_tick_day'] = world['day']
        for case in world['cases']:
            response = legal['responses'].get(str(case['id']))
            if not response or response['action'] != 'contest' or response['reviewed']:
                continue
            if world['day'] >= response['review_day']:
                response['reviewed'] = True
                if case['evidence'] <= RESPONSE_RULES['contest']['weak_evidence']:
                    case['status'] = 'dismissed'
                    _record(world, case, 0, 0, 'contest')
                else:
                    change_heat(world, 3, 'contest_denied', case_id=case['id'])
                    event(world, 'legal_review', f'Case {case["id"]}: contest denied; documented evidence remains.',
                          case_id=case['id'], evidence=case['evidence'], outcome='denied', cause='contested_review')
        if legal['last_crime_day'] < world['day'] - 1:
            change_heat(world, -2, 'quiet_day')
        scrutiny = attention(world['player']['heat'])
        active = [c['id'] for c in world['cases'] if c['status'] == 'pending' and
                  not _deferred(world, c)]
        if scrutiny['evidence_bonus'] and active:
            event(world, 'police_attention', f'{scrutiny["tier"]} heat increased scrutiny of documented cases.',
                  tier=scrutiny['tier'], evidence_bonus=scrutiny['evidence_bonus'],
                  case_ids=active, cause='heat_scrutiny')
    return attention(world['player']['heat'])['evidence_bonus'], {
        c['id'] for c in world['cases'] if _deferred(world, c)}


def _deferred(world, case):
    response = world['legal']['responses'].get(str(case['id']), {})
    return response.get('action') == 'contest' and not response['reviewed']


def advance_day(world):
    from gameplay import next_day
    return next_day(world, legal_rules=True)
