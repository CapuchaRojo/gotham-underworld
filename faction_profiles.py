"""M013 configurable economic identities and additive competition save state."""
from copy import deepcopy

COMPETITION_VERSION = 1
PROFILES = {
    'trade_network': dict(revenue_percent=125, recovery_income=6, recovery_power=2,
                         operating_cost=1, holding_cost=1, upkeep_divisor=35,
                         recruitment_cost=6, recruitment_gain=7, attack_cost=12,
                         defense_cost=8, attack_base=5, defense_base=6,
                         defense_threshold=45, consolidation_threshold=75,
                         attack_reserve=36, min_attack_power=25,
                         treasury_cap=240, recovery_cap=60),
    'street_network': dict(revenue_percent=100, recovery_income=8, recovery_power=3,
                          operating_cost=1, holding_cost=1, upkeep_divisor=40,
                          recruitment_cost=4, recruitment_gain=6, attack_cost=10,
                          defense_cost=9, attack_base=5, defense_base=5,
                          defense_threshold=35, consolidation_threshold=65,
                          attack_reserve=28, min_attack_power=20,
                          treasury_cap=180, recovery_cap=50),
    'industrial_network': dict(revenue_percent=135, recovery_income=5, recovery_power=2,
                              operating_cost=1, holding_cost=1, upkeep_divisor=30,
                              recruitment_cost=5, recruitment_gain=9, attack_cost=13,
                              defense_cost=7, attack_base=4, defense_base=7,
                              defense_threshold=55, consolidation_threshold=85,
                              attack_reserve=40, min_attack_power=30,
                              treasury_cap=220, recovery_cap=70),
}
# Content bindings are data; the competition engine only reads configured IDs.
DEFAULT_BINDINGS = {'Harbor Syndicate': 'trade_network',
                    'Carnival Crew': 'street_network',
                    'Iron Mask Outfit': 'industrial_network'}


def prepare(world):
    if 'competition_version' not in world:
        world['competition_version'] = COMPETITION_VERSION
        world['competition'] = {'activation_day': max(2, world['day'] + 1),
                                'profiles': deepcopy(PROFILES),
                                'factions': {name: profile for name, profile in DEFAULT_BINDINGS.items()
                                             if name in world['factions']}}
    return world


def validate(world):
    from career_state import _integer, _mapping, _require
    if 'competition_version' not in world:
        _require('competition' not in world, 'competition_version', 'is required with competition state')
        _require(not any(e['kind'] == 'faction_economy' or
                         ('profile' in e and e['kind'] in ('economy', 'faction_strategy', 'faction_warfare'))
                         for e in world['events']), 'competition_version', 'is required with competition history')
        return
    _integer(world['competition_version'], 'competition_version')
    _require(world['competition_version'] == COMPETITION_VERSION, 'competition_version',
             f'{world["competition_version"]} is unsupported; supported: {COMPETITION_VERSION}')
    state = world.get('competition')
    _mapping(state, 'competition')
    _integer(state.get('activation_day'), 'competition.activation_day', 2, max(2, world['day'] + 1))
    for key in ('profiles', 'factions'):
        _mapping(state.get(key), 'competition.' + key)
        _require(bool(state[key]), 'competition.' + key, 'must not be empty')
    for name, profile in state['profiles'].items():
        path = 'competition.profiles.' + name
        _mapping(profile, path)
        for key in PROFILES['trade_network']:
            maximum = 1000 if key in ('treasury_cap', 'recovery_cap') else 300 if key == 'revenue_percent' else 100
            _integer(profile.get(key), path + '.' + key, 1, maximum)
        _require(profile['treasury_cap'] >= profile['recovery_cap'] >= profile['attack_reserve'] >= profile['attack_cost'],
                 path, 'must fund expansion within its recovery and treasury caps')
        _require(profile['recovery_income'] > profile['operating_cost'] + 100 // profile['upkeep_divisor'],
                 path, 'must allow positive displaced recovery after maximum-power upkeep')
        _require(profile['consolidation_threshold'] >= profile['defense_threshold'],
                 path, 'must consolidate above its defense threshold')
    for faction, profile in state['factions'].items():
        _require(faction in world['factions'], 'competition.factions', 'must reference existing factions')
        _require(isinstance(profile, str) and profile in state['profiles'], 'competition.factions.' + faction,
                 'must reference an economic profile')
    for item in world['events']:
        if 'profile' not in item or item['kind'] not in ('economy', 'faction_economy', 'faction_warfare'):
            continue
        _require(isinstance(item['profile'], str), 'competition.events.profile', 'must be an identifier')
        for key in ('cash_before', 'cash_after'):
            _integer(item.get(key), 'competition.events.' + key, 0)
        if item['kind'] == 'economy':
            _require(item['cash_after'] == item['cash_before'] + item['income'],
                     'competition.events.income', 'must match treasury changes')
            continue
        for key in ('power_before', 'power_after'):
            _integer(item.get(key), 'competition.events.' + key, 0, 100)
        if item['kind'] == 'faction_economy':
            _integer(item.get('upkeep'), 'competition.events.upkeep', 1)
            _integer(item.get('paid'), 'competition.events.paid', 0, item['upkeep'])
            _require(item['cash_after'] == item['cash_before'] - item['paid'],
                     'competition.events.paid', 'must match treasury changes')
        else:
            _integer(item.get('cost'), 'competition.events.cost', 0)
            _integer(item.get('income', 0), 'competition.events.income', 0)
            _require(item['cash_after'] == item['cash_before'] - item['cost'] + item.get('income', 0),
                     'competition.events.cost/income', 'must match treasury changes')
            action = item.get('action')
            objective = item.get('strategy_objective')
            _require((action, objective) in (('attack', 'expand'), ('defend', 'defend'),
                     ('consolidate', 'consolidate'), ('recover', 'recover'), ('regroup', 'regroup'), ('hold', 'hold')),
                     'competition.events.action', 'must agree with the strategic objective')
            if action == 'hold':
                _require(isinstance(item.get('fallback_reason'), str) and bool(item['fallback_reason']),
                         'competition.events.fallback_reason', 'is required for a hold')


def summary(world):
    """Detached profile and resource view; never initialize a queried world."""
    state = world.get('competition', {})
    result = []
    for faction, profile in sorted(state.get('factions', {}).items()):
        data = world['factions'][faction]
        holdings = sum(d['owner'] == faction for d in world.get('districts', {}).values())
        result.append({'faction': faction, 'profile': profile,
                       'rules': deepcopy(state['profiles'][profile]), 'cash': data['cash'],
                       'power': data['power'], 'districts': holdings,
                       'status': 'established' if holdings else 'displaced'})
    return result
