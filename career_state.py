"""M011 save contract and additive state defaults; no gameplay or I/O."""
from city_economy import GANGS
from relationship_engine import METRICS
from simulation import FACTIONS, new_world
from legal_state import prepare as prepare_legal, validate as validate_legal
from faction_profiles import prepare as prepare_competition, validate as validate_competition

SAVE_VERSION = 1
DAILY_ACTION_ALLOWANCE = 3
SUBSYSTEM_VERSIONS = ('consequence_version', 'npc_action_version',
                      'district_mission_version', 'warfare_version', 'strategy_version')


def _require(condition, path, expectation):
    if not condition:
        raise ValueError(f'Invalid save: {path} {expectation}')


def _integer(value, path, minimum=None, maximum=None):
    _require(type(value) is int, path, 'must be an integer')
    if minimum is not None:
        _require(value >= minimum, path, f'must be >= {minimum}')
    if maximum is not None:
        _require(value <= maximum, path, f'must be <= {maximum}')


def _mapping(value, path):
    _require(isinstance(value, dict), path, 'must be an object')
    _require(all(isinstance(k, str) and k for k in value), path, 'must have nonempty string keys')


def _text(value, path):
    _require(isinstance(value, str) and bool(value), path, 'must be a nonempty string')


def _records(value, path):
    _require(isinstance(value, list), path, 'must be a list')
    for index, item in enumerate(value):
        _mapping(item, f'{path}[{index}]')
    return value


def prepare(world):
    """Add M011 fields without replaying ticks or replenishing spent actions."""
    if world.get('save_version', 0) == 0:
        world['save_version'] = SAVE_VERSION
    world['player'].setdefault('custody', 'pretrial' if world['player']['arrested'] else 'free')
    world.setdefault('action_day', world['day'])
    # Count legacy same-day work so loading an old career is not a free refresh.
    used = sum(e.get('day') == world['day'] and e.get('kind') in ('job', 'district_mission')
               for e in world['events']) if 'actions_used' not in world else 0
    world.setdefault('actions_used', min(DAILY_ACTION_ALLOWANCE, used))
    world.setdefault('command_sequence', 0)
    for case in world['cases']:
        if case['status'] == 'pending':
            case.setdefault('last_investigated_day', world['day'])
    prepare_legal(world)
    prepare_competition(world)
    return world


def validate(world):
    """Validate known engine state, retaining unknown fields for future extensions.

    Unversioned M001-M010 saves may omit additive subsystem state. Present
    fields must always be valid; a versioned M011 save must include its contract.
    """
    _mapping(world, 'world')
    for key in ('seed', 'day', 'player', 'factions', 'people', 'cases', 'events'):
        _require(key in world, key, 'is required')
    version = world.get('save_version', 0)
    _integer(version, 'save_version', 0)
    _require(version in (0, SAVE_VERSION), 'save_version', f'{version} is unsupported; supported: 0, {SAVE_VERSION}')
    for key in SUBSYSTEM_VERSIONS:
        if key in world:
            _integer(world[key], key)
            _require(world[key] == 1, key, f'{world[key]} is unsupported; supported: 1')
    _integer(world['seed'], 'seed')
    _integer(world['day'], 'day', 0)
    day = world['day']
    for key in ('player', 'factions', 'people'):
        _mapping(world[key], key)
    player, factions, people = world['player'], world['factions'], world['people']
    for name in FACTIONS:
        _require(name in factions, 'factions', f'is missing required faction {name}')
    for name, data in factions.items():
        path = f'factions.{name}'
        _mapping(data, path)
        _integer(data.get('power'), path + '.power', 0, 100)
        _integer(data.get('cash'), path + '.cash', 0)
    _text(player.get('name'), 'player.name')
    for key in ('cash', 'heat'):
        _integer(player.get(key), 'player.' + key, 0)
    _require(type(player.get('arrested')) is bool, 'player.arrested', 'must be a boolean')
    custody = player.get('custody', 'pretrial' if player['arrested'] else 'free')
    _require(custody == ('pretrial' if player['arrested'] else 'free'), 'player.custody', 'must agree with arrested state')
    faction = player.get('faction')
    _require(faction is None or faction in GANGS, 'player.faction', 'must be a recruitable faction or null')
    if 'reputation' in player:
        _mapping(player['reputation'], 'player.reputation')
        for name in GANGS:
            _integer(player['reputation'].get(name), 'player.reputation.' + name)
    if 'jobs_completed' in player:
        _integer(player['jobs_completed'], 'player.jobs_completed', 0)
    if 'job_attempts' in world:
        _integer(world['job_attempts'], 'job_attempts', 0)
    for name in new_world()['people']:
        _require(name in people, 'people', f'is missing required NPC {name}')
    for name, data in people.items():
        path = 'people.' + name
        _mapping(data, path)
        _require(isinstance(data.get('faction'), str) and data['faction'] in factions, path + '.faction', 'must reference a faction')
        for item in _records(data.get('memory'), path + '.memory'):
            _integer(item.get('day'), path + '.memory.day', 0, day)
            _text(item.get('fact'), path + '.memory.fact')
        if 'relationship' in data:
            _mapping(data['relationship'], path + '.relationship')
            for metric, score in data['relationship'].items():
                _require(metric in METRICS, path + '.relationship', 'contains an unknown metric')
                _integer(score, path + '.relationship.' + metric, -100, 100)
        if version == SAVE_VERSION:
            _require('relationship_history' in data, path + '.relationship_history', 'is required for M011 saves')
            _require('relationship' in data and all(metric in data['relationship'] for metric in METRICS),
                     path + '.relationship', 'must include every relationship metric')
        for item in _records(data.get('relationship_history', []), path + '.relationship_history'):
            _integer(item.get('day'), path + '.relationship_history.day', 0, day)
            _text(item.get('cause'), path + '.relationship_history.cause')
            _mapping(item.get('changes'), path + '.relationship_history.changes')
            for metric, delta in item['changes'].items():
                _require(metric in METRICS, path + '.relationship_history', 'contains an unknown metric')
                _integer(delta, path + '.relationship_history.' + metric, -200, 200)
    ids, charged = set(), []
    for case in _records(world['cases'], 'cases'):
        _integer(case.get('id'), 'cases.id', 1)
        _require(case['id'] not in ids, 'cases.id', 'must be unique')
        ids.add(case['id'])
        _text(case.get('crime'), 'cases.crime')
        _text(case.get('suspect'), 'cases.suspect')
        _integer(case.get('evidence'), 'cases.evidence', 0)
        _require(case.get('status') in ('open', 'pending', 'charged', 'convicted', 'dismissed'), 'cases.status', 'is unsupported')
        if case['status'] == 'charged':
            charged.append(case)
            _require(case['evidence'] >= 3, 'cases.evidence', 'must be >= 3 for a charged case')
        if case['status'] == 'pending':
            _require(case.get('witnessed') is True, 'cases.witnessed', 'must be true for a pending case')
            _integer(case.get('source_attempt'), 'cases.source_attempt', 0)
            _integer(case.get('investigation_days'), 'cases.investigation_days', 0)
            if version == SAVE_VERSION:
                _require('last_investigated_day' in case, 'cases.last_investigated_day', 'is required for M011 pending cases')
        for key in ('source_attempt', 'investigation_days'):
            if key in case:
                _integer(case[key], 'cases.' + key, 0)
        if 'witnessed' in case:
            _require(type(case['witnessed']) is bool, 'cases.witnessed', 'must be a boolean')
        if 'last_investigated_day' in case:
            _integer(case['last_investigated_day'], 'cases.last_investigated_day', -1, day)
    _require(len(charged) <= 1 and bool(charged) == player['arrested'], 'cases/player.arrested', 'must identify exactly one charged case while detained')
    command_ids = set()
    for item in _records(world['events'], 'events'):
        _integer(item.get('day'), 'events.day', 0, day)
        _text(item.get('kind'), 'events.kind')
        _text(item.get('message'), 'events.message')
        if 'income' in item:
            _integer(item['income'], 'events.income', 0)
        for key in ('district', 'faction'):
            if key in item:
                _require(item[key] is None or isinstance(item[key], str), 'events.' + key, 'must be a string or null')
        for key in ('captured', 'success'):
            if key in item:
                _require(type(item[key]) is bool, 'events.' + key, 'must be a boolean')
        if item['kind'] == 'player_command':
            _integer(item.get('command_id'), 'events.command_id', 1)
            _require(item['command_id'] not in command_ids, 'events.command_id', 'must be unique')
            command_ids.add(item['command_id'])
            _text(item.get('command'), 'events.command')
            _text(item.get('actor'), 'events.actor')
            _mapping(item.get('arguments'), 'events.arguments')
            _integer(item.get('action_cost'), 'events.action_cost', 0)
    for key in ('economy_last_day', 'warfare_last_day', 'strategy_last_day', 'district_mission_last_day'):
        if key in world:
            _integer(world[key], key, -1, day)
    if 'districts' in world:
        _mapping(world['districts'], 'districts')
        _require(bool(world['districts']), 'districts', 'must not be empty')
        for name, data in world['districts'].items():
            _district(data, 'districts.' + name, factions)
    for key in ('district_intel', 'npc_action_last_day', 'faction_strategy'):
        if key in world:
            _mapping(world[key], key)
    for name, data in world.get('district_intel', {}).items():
        _require(name in world.get('districts', {}), 'district_intel', 'must reference a district')
        _district(data, 'district_intel.' + name, factions, wealth=False)
        _integer(data.get('day'), 'district_intel.day', 0, day)
    for name, last in world.get('npc_action_last_day', {}).items():
        _require(name in people, 'npc_action_last_day', 'must reference an NPC')
        _integer(last, 'npc_action_last_day.' + name, 0, day)
    for name, plan in world.get('faction_strategy', {}).items():
        _mapping(plan, 'faction_strategy.' + name)
        _require(name in factions and plan.get('faction') == name, 'faction_strategy.faction', 'must match a known faction')
        _integer(plan.get('day'), 'faction_strategy.day', 0, day)
        _require(plan.get('objective') in ('recover', 'defend', 'consolidate', 'expand', 'regroup'), 'faction_strategy.objective', 'is unsupported')
        target = plan.get('district')
        _require((target is None and plan['objective'] in ('recover', 'regroup')) or
                 (isinstance(target, str) and target in world.get('districts', {})), 'faction_strategy.district', 'must reference a district or be null for recovery/regrouping')
        _text(plan.get('reason'), 'faction_strategy.reason')
        for key in ('treasury', 'owned_count', 'power'):
            _integer(plan.get(key), 'faction_strategy.' + key, 0)
    if version == SAVE_VERSION:
        for key in (*SUBSYSTEM_VERSIONS, 'action_day', 'actions_used', 'command_sequence',
                    'job_attempts', 'districts', 'economy_last_day', 'warfare_last_day',
                    'strategy_last_day', 'district_mission_last_day', 'district_intel',
                    'npc_action_last_day', 'faction_strategy'):
            _require(key in world, key, 'is required for M011 saves')
        for key in ('custody', 'faction', 'reputation', 'jobs_completed'):
            _require(key in player, 'player.' + key, 'is required for M011 saves')
    for key, minimum, maximum in (('action_day', 0, day), ('actions_used', 0, DAILY_ACTION_ALLOWANCE), ('command_sequence', 0, None)):
        if key in world:
            _integer(world[key], key, minimum, maximum)
    if command_ids:
        _integer(world.get('command_sequence'), 'command_sequence', max(command_ids))
    validate_legal(world)
    validate_competition(world)
    from navigation import validate as validate_navigation
    validate_navigation(world)
    from daily_life_state import validate as validate_life
    validate_life(world)
    from incident_state import validate as validate_incidents
    validate_incidents(world)
    from institution_state import validate as validate_institutions
    validate_institutions(world)
    return world


def _district(data, path, factions, wealth=True):
    _mapping(data, path)
    _require(isinstance(data.get('owner'), str) and data['owner'] in factions, path + '.owner', 'must reference a faction')
    _integer(data.get('control'), path + '.control', 0, 100)
    if wealth:
        _integer(data.get('wealth'), path + '.wealth', 0)
