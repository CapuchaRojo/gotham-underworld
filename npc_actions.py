"""M005: deterministic daily NPC actions with causal records and cooldowns."""
from relationship_engine import decision, prepare as prepare_relationships
from simulation import event, remember

COOLDOWNS = {'offer_support': 3, 'refuse_cooperation': 3,
             'prioritize_investigation': 2}


def prepare(world):
    prepare_relationships(world)
    world.setdefault('npc_action_version', 1)
    world.setdefault('npc_action_last_day', {})
    return world


def act(world):
    """Process NPCs once per day; only documented facts authorize police action."""
    prepare(world)
    emitted = []
    for name in ('Mara Voss', 'Eli Crowe', 'Detective Vale'):
        if name not in world['people']:
            continue
        choice = decision(world, name)
        action = choice['action']
        if action not in COOLDOWNS:
            continue
        last = world['npc_action_last_day'].get(name)
        if last is not None and world['day'] - last < COOLDOWNS[action]:
            continue
        player = world['player']
        faction = player.get('faction')
        person = world['people'][name]
        details = {'npc': name, 'action': action, 'cause': 'relationship_policy',
                   'reason': choice['reason']}
        if name == 'Mara Voss' and action == 'offer_support':
            if faction != person['faction'] or player['arrested']:
                continue
            player['cash'] += 15
            message = 'Mara Voss provided $15 in faction support.'
        elif name == 'Eli Crowe' and action == 'refuse_cooperation':
            if faction is None or faction == person['faction']:
                continue
            world['factions'][faction]['power'] = max(0, world['factions'][faction]['power'] - 2)
            message = f'Eli Crowe obstructed {faction}; it lost 2 power.'
        elif name == 'Detective Vale' and action == 'prioritize_investigation':
            # Only an existing documented witness case can be accelerated.
            pending = next((c for c in world['cases']
                            if c['status'] == 'pending' and c.get('witnessed')
                            and c.get('evidence', 0) > 0), None)
            if pending is None or player['arrested']:
                continue
            pending['evidence'] += 1
            details['case_id'] = pending['id']
            details['source_attempt'] = pending.get('source_attempt')
            message = f'Detective Vale prioritized evidence review in case {pending["id"]}.'
            if pending['evidence'] >= 3:
                pending['status'] = 'charged'
                player['arrested'] = True
                player['custody'] = 'pretrial'
                event(world, 'arrest', f'Rookie arrested on case {pending["id"]}.',
                      case_id=pending['id'], source_attempt=pending.get('source_attempt'),
                      cause='npc_evidence_review')
        else:
            continue
        world['npc_action_last_day'][name] = world['day']
        remember(world, name, message)
        emitted.append(event(world, 'npc_action', message, **details))
    return emitted
