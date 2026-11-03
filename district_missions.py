"""M007: deterministic district missions; all state changes are auditable."""
from city_economy import prepare as prepare_economy
from simulation import event

MISSIONS = {
    'scout': {'cost': 5, 'control': 0, 'reputation': 0},
    'fortify': {'cost': 15, 'control': 8, 'reputation': 1},
    'expand': {'cost': 30, 'control': 12, 'reputation': 2},
}


def prepare(world):
    prepare_economy(world)
    world.setdefault('district_mission_version', 1)
    world.setdefault('district_mission_last_day', -1)
    world.setdefault('district_intel', {})
    return world


def available(world):
    prepare(world)
    return list(enumerate(world['districts'], 1))


def mission(world, kind, district_name):
    prepare(world)
    if kind not in MISSIONS:
        raise ValueError('Unknown district mission')
    if district_name not in world['districts']:
        raise ValueError('Unknown district')
    player = world['player']
    faction = player.get('faction')
    if player['arrested']:
        raise ValueError('Cannot run missions while detained')
    if faction is None:
        raise ValueError('Join a faction first')
    if world['district_mission_last_day'] == world['day']:
        raise ValueError('One district mission per day; use wait')
    district = world['districts'][district_name]
    owner = district['owner']
    if kind == 'fortify' and owner != faction:
        raise ValueError('Can only fortify your faction territory')
    if kind == 'expand' and owner == faction:
        raise ValueError('Expansion requires a rival-controlled district')
    cost = MISSIONS[kind]['cost']
    if player['cash'] < cost:
        raise ValueError(f'Need ${cost} for {kind}')
    player['cash'] -= cost
    world['district_mission_last_day'] = world['day']
    details = {'district': district_name, 'faction': faction, 'mission': kind,
               'previous_owner': owner, 'cost': cost, 'cause': 'player_district_mission'}
    if kind == 'scout':
        world['district_intel'][district_name] = {'day': world['day'], 'owner': owner,
                                                   'control': district['control']}
        message = f'Rookie scouted {district_name}; owner {owner}, control {district["control"]}.'
    elif kind == 'fortify':
        before = district['control']
        district['control'] = min(100, before + 8)
        details['control_delta'] = district['control'] - before
        message = f'{faction} fortified {district_name} (+{details["control_delta"]} control).'
    else:
        before = district['control']
        district['control'] = max(0, before - 12)
        details['control_delta'] = district['control'] - before
        if district['control'] == 0:
            district['owner'] = faction
            district['control'] = 35
            details['captured'] = True
            message = f'{faction} captured {district_name} from {owner}.'
        else:
            details['captured'] = False
            message = f'{faction} challenged {owner} in {district_name} (-{before - district["control"]} control).'
    player['reputation'][faction] = player['reputation'].get(faction, 0) + MISSIONS[kind]['reputation']
    return event(world, 'district_mission', message, **details)
