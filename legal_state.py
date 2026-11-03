"""M012 legal-state schema and property-independent heat definitions."""
from copy import deepcopy

LEGAL_VERSION = 1
HEAT_LIMIT = 100
# Minimum heat, public tier name, job/exposure bonus, daily evidence bonus.
HEAT_TIERS = ((0, 'low', 0, 0), (20, 'elevated', 5, 0),
              (50, 'high', 10, 1), (80, 'critical', 15, 1))
RESPONSE_RULES = {
    'lay_low': {'cash_cost': 0, 'heat_relief': 12},
    'cooperate': {'cash_cost': 0, 'heat_relief': 8, 'court_heat_relief': 4, 'fine': 30},
    'contest': {'cash_cost': 20, 'review_days': 2, 'weak_evidence': 1},
    'accept': {'cash_cost': 0, 'heat_relief': 10, 'fine': 35},
}


def attention(heat):
    """A bounded read model; historical unbounded counters remain loadable."""
    bounded = max(0, min(HEAT_LIMIT, heat))
    index = max(i for i, tier in enumerate(HEAT_TIERS) if bounded >= tier[0])
    _, name, risk, evidence = HEAT_TIERS[index]
    return {'heat': bounded, 'tier': name, 'risk_bonus': risk,
            'witness_bonus': risk, 'collection_heat_bonus': index,
            'evidence_bonus': evidence}


def prepare(world):
    """Initialize old careers without replay, guessing historical dates, or resets."""
    if 'legal_version' not in world:
        world['legal_version'] = LEGAL_VERSION
        crimes = [e['day'] for e in world['events'] if e.get('kind') == 'crime' or
                  (e.get('kind') == 'job' and e.get('job') == 'collection')]
        world['legal'] = {'last_tick_day': world['day'], 'last_lay_low_day': -1,
                          'last_crime_day': max(crimes, default=-1),
                          'responses': {}, 'record': [
                              {'case_id': case['id'], 'day': None, 'outcome': case['status'],
                               'fine_assessed': None, 'fine_paid': None, 'response': 'historical'}
                              for case in world['cases'] if case['status'] in ('convicted', 'dismissed')]}
    return world


def report(world):
    """Detached, non-initializing legal status for interfaces."""
    return {**attention(world['player']['heat']),
            'profile': deepcopy(world.get('legal')),
            'cases': deepcopy(world['cases'])}


def validate(world):
    """Validate an optional M012 extension; its marker makes missing state invalid."""
    # Shared primitive validators live in the owning career schema. Importing
    # here keeps schema initialization acyclic and error paths consistent.
    from career_state import _integer, _mapping, _records, _require
    if 'legal_version' not in world:
        _require('legal' not in world, 'legal_version', 'is required when legal state is present')
        _require(not any(e['kind'] in ('heat_change', 'police_attention', 'legal_response',
                                      'legal_review', 'legal_outcome') for e in world['events']),
                 'legal_version', 'is required when legal history is present')
        return
    _integer(world['legal_version'], 'legal_version')
    _require(world['legal_version'] == LEGAL_VERSION, 'legal_version',
             f'{world["legal_version"]} is unsupported; supported: {LEGAL_VERSION}')
    legal = world.get('legal')
    _mapping(legal, 'legal')
    day = world['day']
    for key in ('last_tick_day', 'last_lay_low_day', 'last_crime_day'):
        _integer(legal.get(key), 'legal.' + key, -1, day)
    _mapping(legal.get('responses'), 'legal.responses')
    cases = {str(c['id']): c for c in world['cases']}
    for key, response in legal['responses'].items():
        path = 'legal.responses.' + key
        _require(key in cases, path, 'must reference an existing case')
        _mapping(response, path)
        _require(all(k in response for k in ('action', 'day', 'reviewed', 'review_day')), path, 'is missing required response fields')
        choice = response.get('action')
        _require(choice in ('cooperate', 'contest', 'accept'), path + '.action', 'is unsupported')
        _integer(response.get('day'), path + '.day', 0, day)
        _require(type(response.get('reviewed')) is bool, path + '.reviewed', 'must be a boolean')
        if choice == 'contest':
            review_day = response['day'] + RESPONSE_RULES['contest']['review_days']
            _integer(response.get('review_day'), path + '.review_day', review_day, review_day)
            if not response['reviewed']:
                _require(cases[key]['status'] == 'pending' and day < response['review_day'], path,
                         'must be a pending case awaiting its future review')
            else:
                _require(day >= response['review_day'], path + '.reviewed', 'cannot precede the review day')
        else:
            _require(response.get('review_day') is None and response['reviewed'], path,
                     'must be an immediate response without a review day')
            if choice == 'accept':
                _require(cases[key]['status'] == 'convicted', path, 'must reference an accepted conviction')
            else:
                _require(cases[key]['status'] in ('pending', 'charged', 'convicted'), path,
                         'must reference a live or convicted cooperation case')
    seen = set()
    for item in _records(legal.get('record'), 'legal.record'):
        _require(all(k in item for k in ('case_id', 'day', 'outcome', 'fine_assessed', 'fine_paid', 'response')),
                 'legal.record', 'is missing required record fields')
        case_id = item.get('case_id')
        _integer(case_id, 'legal.record.case_id', 1)
        _require(str(case_id) in cases and case_id not in seen, 'legal.record.case_id', 'must reference a unique existing case')
        seen.add(case_id)
        _require(item.get('outcome') in ('convicted', 'dismissed') and
                 cases[str(case_id)]['status'] == item['outcome'], 'legal.record.outcome', 'must agree with the resolved case')
        choice = item.get('response')
        _require(choice in ('none', 'historical', 'cooperate', 'contest', 'accept'), 'legal.record.response', 'is unsupported')
        if choice == 'historical':
            _require(all(item.get(key) is None for key in ('day', 'fine_assessed', 'fine_paid')),
                     'legal.record', 'must retain unknown historical dates and fines as null')
        else:
            _integer(item.get('day'), 'legal.record.day', 0, day)
            _integer(item.get('fine_assessed'), 'legal.record.fine_assessed', 0, 50)
            _integer(item.get('fine_paid'), 'legal.record.fine_paid', 0, item['fine_assessed'])
            _require(legal['responses'].get(str(case_id), {}).get('action', 'none') == choice,
                     'legal.record.response', 'must match the recorded case response')
            expected_fine = RESPONSE_RULES.get(choice, {}).get('fine', 50) if item['outcome'] == 'convicted' else 0
            _require(item['fine_assessed'] == expected_fine, 'legal.record.fine_assessed', 'must match the case outcome and response')
    outcomes = {item['case_id']: item for item in legal['record']}
    for item in world['events']:
        if item['kind'] == 'heat_change':
            _integer(item.get('before'), 'events.heat_change.before', 0)
            _integer(item.get('after'), 'events.heat_change.after', 0, HEAT_LIMIT)
            _integer(item.get('delta'), 'events.heat_change.delta')
            _require(item['after'] - item['before'] == item['delta'], 'events.heat_change.delta', 'must match before/after heat')
            for key, heat in (('tier_before', item['before']), ('tier_after', item['after'])):
                _require(item.get(key) == attention(heat)['tier'], 'events.heat_change.' + key, 'must match recorded heat')
        elif item['kind'] == 'police_attention':
            _integer(item.get('evidence_bonus'), 'events.police_attention.evidence_bonus', 1, 1)
            _require(item.get('tier') in ('high', 'critical') and item.get('evidence_bonus') == 1,
                     'events.police_attention', 'must record a supported tier and evidence bonus')
            ids = item.get('case_ids')
            _require(isinstance(ids, list), 'events.police_attention.case_ids', 'must be a list')
            for case_id in ids:
                _integer(case_id, 'events.police_attention.case_ids', 1)
                _require(str(case_id) in cases, 'events.police_attention.case_ids', 'must reference existing cases')
        elif item['kind'] == 'legal_response':
            choice = item.get('action')
            _require(isinstance(choice, str) and choice in RESPONSE_RULES, 'events.legal_response.action', 'is unsupported')
            _integer(item.get('cash_cost'), 'events.legal_response.cash_cost', 0)
            _require(item['cash_cost'] == RESPONSE_RULES[choice]['cash_cost'], 'events.legal_response.cash_cost', 'must match its action')
            if choice != 'lay_low':
                _integer(item.get('case_id'), 'events.legal_response.case_id', 1)
                _require(str(item['case_id']) in cases, 'events.legal_response.case_id', 'must reference an existing case')
        elif item['kind'] == 'legal_outcome':
            _integer(item.get('case_id'), 'events.legal_outcome.case_id', 1)
            record = outcomes.get(item['case_id'])
            _require(record is not None and all(item.get(key) == record[key] for key in
                     ('case_id', 'day', 'outcome', 'fine_assessed', 'fine_paid', 'response')),
                     'events.legal_outcome', 'must match its persistent legal record')
