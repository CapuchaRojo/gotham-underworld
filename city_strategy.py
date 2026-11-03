"""M009: explainable, deterministic faction strategic planning."""
from copy import deepcopy
from city_economy import GANGS, prepare as prepare_economy
from simulation import event


def prepare(world):
    prepare_economy(world)
    world.setdefault('strategy_version', 1)
    # Migrated worlds begin planning on the next advanced day.
    world.setdefault('strategy_last_day', world['day'])
    world.setdefault('faction_strategy', {})
    return world


def _recent_pressure(world, faction):
    """Only recorded, recent events count as evidence of player pressure."""
    pressure = {}
    for item in world['events']:
        if item.get('day', -100) < world['day'] - 3:
            continue
        if item.get('kind') != 'district_mission' or item.get('mission') != 'expand':
            continue
        if item.get('faction') == faction:
            continue
        district = item.get('district')
        if district in world.get('districts', {}) and world['districts'][district]['owner'] == faction:
            pressure[district] = pressure.get(district, 0) + 8
    return pressure


def assess(world, faction, *, competition=False):
    """Read-only, stable strategic assessment; no random draws."""
    if competition:
        from faction_competition import assess as economic_assessment
        if faction not in world.get('competition', {}).get('factions', {}):
            raise ValueError('Unknown configured faction')
        return economic_assessment(world, faction, _recent_pressure(world, faction))
    if faction not in GANGS or faction not in world['factions']:
        raise ValueError('Unknown faction')
    treasury = world['factions'][faction]
    owned = [(n, d) for n, d in world.get('districts', {}).items() if d['owner'] == faction]
    rivals = [(n, d) for n, d in world.get('districts', {}).items()
              if d['owner'] in GANGS and d['owner'] != faction]
    pressure = _recent_pressure(world, faction)
    threatened = sorted(owned, key=lambda x: (x[1]['control'] - pressure.get(x[0], 0), x[0]))
    weakest = threatened[0] if threatened else None
    target = min(rivals, key=lambda x: (x[1]['control'], -x[1]['wealth'], x[0])) if rivals else None
    cash = treasury['cash']
    if weakest and weakest[1]['control'] - pressure.get(weakest[0], 0) <= 45 and cash >= 8:
        objective, district = 'defend', weakest[0]
        reason = f'control={weakest[1]["control"]}, recent_pressure={pressure.get(district, 0)}; defense threshold 45'
    elif cash < 24:
        objective, district = 'recover', None
        reason = f'treasury=${cash} below reserve $24'
    elif target and cash >= 36:
        objective, district = 'expand', target[0]
        reason = f'treasury=${cash}; target control={target[1]["control"]}, wealth={target[1]["wealth"]}'
    elif weakest and cash >= 8 and weakest[1]['control'] < 80:
        objective, district = 'consolidate', weakest[0]
        reason = f'no funded expansion; weakest control={weakest[1]["control"]}'
    else:
        objective, district = 'recover', None
        reason = f'preserve treasury=${cash} and holdings'
    return {'faction': faction, 'objective': objective, 'district': district,
            'reason': reason, 'treasury': cash, 'power': treasury['power'],
            'owned_count': len(owned), 'day': world['day']}


def advance(world, *, competition=False):
    """Commit a daily plan once; planning never spends or moves territory."""
    prepare(world)
    if competition:
        from faction_competition import active
        if not active(world):
            return []
    if world['day'] < 2 or world['strategy_last_day'] >= world['day']:
        return []
    emitted = []
    factions = sorted(world['competition']['factions']) if competition else GANGS
    for faction in factions:
        if faction not in world['factions']:
            continue
        if competition:
            from faction_competition import assess as economic_assessment
            plan = economic_assessment(world, faction, _recent_pressure(world, faction))
        else:
            plan = assess(world, faction)
        world['faction_strategy'][faction] = plan
        emitted.append(event(world, 'faction_strategy',
                             f'{faction} chose {plan["objective"]}' +
                             (f' at {plan["district"]}' if plan['district'] else '') + '.',
                             faction=faction, objective=plan['objective'],
                             district=plan['district'], reason=plan['reason'],
                             cause='strategic_assessment'))
        if competition:
            emitted[-1].update(profile=plan['profile'], treasury=plan['treasury'], power=plan['power'])
    world['strategy_last_day'] = world['day']
    return emitted


def summary(world):
    factions = sorted(world['competition']['factions']) if 'competition' in world else GANGS
    return [(faction, deepcopy(world.get('faction_strategy', {}).get(faction))) for faction in factions]
