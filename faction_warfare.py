"""M008: auditable, deterministic daily faction strategy for district warfare."""
from city_economy import GANGS, prepare as prepare_economy
from relationship_engine import prepare as prepare_relationships
from simulation import event, remember
from territory import capture

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


def _hold(world, faction, plan, reason, actor):
    """A changed target must not turn a defense plan into a mislabeled attack."""
    return event(world, 'faction_warfare', f'{faction} held position: {reason}.',
                 faction=faction, district=plan.get('district'), action='hold',
                 cost=0, control_delta=0, cause='strategy_fallback', npc=actor,
                 strategy_objective='hold', strategy_reason=reason,
                 planned_objective=plan.get('objective'), fallback_reason=reason)


def advance(world, *, competition=False):
    """At most one deterministic action per gang per day; repeat calls do nothing."""
    prepare(world)
    if competition:
        from faction_competition import warfare
        return warfare(world)
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
        plan = world.get('faction_strategy', {}).get(faction)
        fallback_reason = None
        planned_objective = plan.get('objective') if isinstance(plan, dict) else None
        if not isinstance(plan, dict) or plan.get('day') != world['day']:
            if plan is not None:
                fallback_reason = 'no valid current-day strategy; legacy warfare policy applied'
            plan = None
        if plan:
            objective = plan['objective']
            target_name = plan.get('district')
            if objective == 'recover':
                continue
            if objective in ('defend', 'consolidate'):
                weak = next(((n, d) for n, d in owned if n == target_name), None)
                if weak is None:
                    emitted.append(_hold(world, faction, plan, 'planned defense target is no longer owned', actor))
                    continue
                if weak[1]['control'] >= 100 or treasury['cash'] < DEFENSE_COST:
                    emitted.append(_hold(world, faction, plan, 'planned defense has no capacity or funding', actor))
                    continue
            elif objective == 'expand':
                rivals = [(n, d) for n, d in rivals if n == target_name]
                weak = None
                if not rivals or treasury['cash'] < ATTACK_COST:
                    emitted.append(_hold(world, faction, plan, 'planned expansion target or funding is no longer available', actor))
                    continue
            else:
                emitted.append(_hold(world, faction, plan, 'planned objective is unsupported', actor))
                continue
        if weak and (plan is not None or weak[1]['control'] <= DEFENSE_THRESHOLD) and treasury['cash'] >= DEFENSE_COST:
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
                transfer = capture(world, name, faction)
                message = f'{faction} captured {name} from {previous_owner} in a faction offensive.'
            else:
                message = f'{faction} attacked {name} held by {previous_owner} (-{damage} control).'
            data = dict(district=name, faction=faction, action='attack', cost=ATTACK_COST,
                        control_delta=-damage, previous_owner=previous_owner,
                        captured=captured, cause='faction_offensive', npc=actor)
            if captured:
                data.update(transfer)
        else:
            continue
        if plan:
            data['strategy_objective'] = plan['objective']
            data['strategy_reason'] = plan['reason']
        elif fallback_reason:
            data['strategy_objective'] = 'defend' if data['action'] == 'defend' else 'expand'
            data['strategy_reason'] = fallback_reason
            data['planned_objective'] = planned_objective
            data['fallback_reason'] = fallback_reason
        if actor:
            remember(world, actor, message)
        emitted.append(event(world, 'faction_warfare', message, **data))
    world['warfare_last_day'] = world['day']
    return emitted
