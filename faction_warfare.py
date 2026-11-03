"""M008: auditable, deterministic daily faction strategy for district warfare."""
from city_economy import GANGS, prepare as prepare_economy
from relationship_engine import prepare as prepare_relationships
from simulation import event, remember

ATTACK_COST = 12
DEFENSE_COST = 8
DEFENSE_THRESHOLD = 35


def prepare(world):
    """Initialize warfare without replaying actions in migrated career saves."""
    prepare_economy(world)
    prepare_relationships(world)
    world.setdefault('warfare_version', 1)
    world.setdefault('warfare_last_day', world['day'] - 1)
    return world


def _representative(world, faction):
    """An affiliated NPC may advise their faction, not act omnisciently."""
    for name in ('Mara Voss', 'Eli Crowe'):
        person = world['people'].get(name)
        if person and person['faction'] == faction:
            return name
    return None


def advance(world):
    """At most one deterministic action per gang per day; repeat calls do nothing."""
    prepare(world)
    # Day one is mobilization; preserve the original first-day economy baseline.
    if world['day'] < 2 or world['warfare_last_day'] >= world['day']:
        return []
    emitted = []
    for faction in GANGS:
        treasury = world['factions'].get(faction)
        if treasury is None:
            continue
        owned = [(name, d) for name, d in world['districts'].items() if d['owner'] == faction]
        rivals = [(name, d) for name, d in world['districts'].items()
                  if d['owner'] in GANGS and d['owner'] != faction]
        # Defend the most vulnerable holding before pursuing expansion.
        weak = min(owned, key=lambda item: (item[1]['control'], item[0])) if owned else None
        actor = _representative(world, faction)
        if weak and weak[1]['control'] <= DEFENSE_THRESHOLD and treasury['cash'] >= DEFENSE_COST:
            name, district = weak
            before = district['control']
            gain = min(100 - before, 6 + treasury['power'] // 25)
            treasury['cash'] -= DEFENSE_COST
            district['control'] += gain
            message = f'{faction} defended {name} (+{gain} control).'
            data = dict(district=name, faction=faction, action='defend', cost=DEFENSE_COST,
                        control_delta=gain, cause='faction_defense', npc=actor)
        elif rivals and treasury['cash'] >= ATTACK_COST:
            name, district = min(rivals, key=lambda item: (item[1]['control'], item[0]))
            previous_owner = district['owner']
            before = district['control']
            damage = min(before, 4 + treasury['power'] // 25)
            treasury['cash'] -= ATTACK_COST
            district['control'] -= damage
            captured = district['control'] == 0
            if captured:
                district['owner'] = faction
                district['control'] = 35
                message = f'{faction} captured {name} from {previous_owner} in a faction offensive.'
            else:
                message = f'{faction} attacked {name} held by {previous_owner} (-{damage} control).'
            data = dict(district=name, faction=faction, action='attack', cost=ATTACK_COST,
                        control_delta=-damage, previous_owner=previous_owner,
                        captured=captured, cause='faction_offensive', npc=actor)
        else:
            continue
        if actor:
            remember(world, actor, message)
        emitted.append(event(world, 'faction_warfare', message, **data))
    world['warfare_last_day'] = world['day']
    return emitted
