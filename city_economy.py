"""District income: legacy resolver and explicit M013 daily competition policy."""
from copy import deepcopy
from simulation import event
from territory import capture

DISTRICTS = {
    'Harbor Docks': {'owner': 'Harbor Syndicate', 'wealth': 60, 'control': 65},
    'Carnival Row': {'owner': 'Carnival Crew', 'wealth': 45, 'control': 65},
    'Ironworks': {'owner': 'Iron Mask Outfit', 'wealth': 50, 'control': 65},
}
GANGS = ('Harbor Syndicate', 'Carnival Crew', 'Iron Mask Outfit')


def prepare(world):
    """Migrate old saves without replaying any past economic ticks."""
    if 'districts' not in world:
        world['districts'] = {name: dict(data) for name, data in DISTRICTS.items()}
    world.setdefault('economy_last_day', world['day'] - 1)
    return world


def on_job(world, result):
    """Successful jobs reinforce one district owned by the player's faction."""
    prepare(world)
    if not result.get('success'):
        return None
    faction = world['player'].get('faction')
    owned = [(name, d) for name, d in world['districts'].items() if d['owner'] == faction]
    target = min(owned, key=lambda item: (item[1]['control'], item[0]))[0] if owned else None
    if target is None:
        return None
    district = world['districts'][target]
    before = district['control']
    district['control'] = min(100, before + 2)
    return event(world, 'territory', f'{faction} reinforced {target}.',
                 district=target, faction=faction, control_delta=district['control'] - before,
                 source_attempt=result['attempt'], cause='successful_job')


def advance(world, *, competition=False):
    """Apply exactly one economic tick per day; no effect on unrelated RNG."""
    prepare(world)
    if competition:
        from faction_competition import economy
        return economy(world)
    if world['economy_last_day'] >= world['day']:
        return []
    emitted = []
    for name, district in sorted(world['districts'].items()):
        owner = district['owner']
        if owner not in world['factions']:
            continue
        income = max(1, district['wealth'] // 15)
        world['factions'][owner]['cash'] += income
        emitted.append(event(world, 'economy', f'{owner} earned ${income} from {name}.',
                             district=name, faction=owner, income=income,
                             cause='district_income'))
        # One rotating challenger applies bounded pressure, deterministically.
        if owner in GANGS:
            challenger = GANGS[(GANGS.index(owner) + 1 + world['day'] % 2) % len(GANGS)]
            if challenger == owner:
                challenger = GANGS[(GANGS.index(owner) + 1) % len(GANGS)]
            pressure = 1 + (world['day'] + len(name)) % 3
            before_control = district['control']
            district['control'] = max(0, district['control'] - pressure)
            if district['control'] == 0:
                claimant = world['factions'][challenger]
                if claimant['cash'] < 12 or claimant['power'] == 0:
                    district['control'] = 1
                    emitted.append(event(world, 'territory_pressure', f'{challenger} could not fund a claim on {name}.',
                                         district=name, faction=owner, challenger=challenger,
                                         control_before=before_control, control_after=1,
                                         cause='unfunded_pressure_claim'))
                    continue
                before_cash = claimant['cash']
                claimant['cash'] -= 12
                transfer = capture(world, name, challenger)
                emitted.append(event(world, 'territory',
                                     f'{challenger} took control of {name} from {owner}.',
                                     district=name, faction=challenger, **transfer,
                                     cost=12, cash_before=before_cash, cash_after=claimant['cash'],
                                     control_before=before_control,
                                     cause='control_exhausted'))
    world['economy_last_day'] = world['day']
    return emitted


def summary(world):
    prepare(world)
    return [(name, deepcopy(data)) for name, data in sorted(world['districts'].items())]
