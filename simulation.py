"""Gotham Underworld M001: original-IP, deterministic, dependency-free simulation."""
import argparse
import json
import random
from pathlib import Path

FACTIONS = {
    'Harbor Syndicate': {'power': 70, 'cash': 80},
    'Carnival Crew': {'power': 45, 'cash': 35},
    'Iron Mask Outfit': {'power': 60, 'cash': 65},
    'Civic Police': {'power': 75, 'cash': 70},
    'Night Watch': {'power': 35, 'cash': 20},
}


def new_world(seed=42):
    return {'seed': seed, 'day': 0, 'factions': {k: dict(v) for k, v in FACTIONS.items()},
            'people': {'Mara Voss': {'faction': 'Harbor Syndicate', 'memory': []},
                       'Eli Crowe': {'faction': 'Carnival Crew', 'memory': []},
                       'Detective Vale': {'faction': 'Civic Police', 'memory': []}},
            'player': {'name': 'Rookie', 'heat': 0, 'cash': 40, 'arrested': False, 'custody': 'free'},
            'cases': [], 'events': []}


def event(world, kind, message, **details):
    item = {'day': world['day'], 'kind': kind, 'message': message, **details}
    world['events'].append(item)
    return item


def remember(world, person, fact):
    world['people'][person]['memory'].append({'day': world['day'], 'fact': fact})


def robbery(world):
    if world['player']['arrested']:
        return event(world, 'blocked', 'Cannot commit a robbery while in custody.')
    world['player']['cash'] += 75
    world['player']['heat'] += 3
    case = {'id': len(world['cases']) + 1, 'crime': 'warehouse robbery', 'evidence': 1,
            'status': 'open', 'suspect': 'Rookie'}
    world['cases'].append(case)
    remember(world, 'Mara Voss', 'Rookie robbed a warehouse.')
    return event(world, 'crime', 'Rookie robbed a warehouse; a witness reported it.', case_id=case['id'])


def advance(world):
    world['day'] += 1
    rng = random.Random(world['seed'] * 1000003 + world['day'])
    gangs = ['Harbor Syndicate', 'Carnival Crew', 'Iron Mask Outfit']
    attacker, defender = rng.sample(gangs, 2)
    damage = rng.randint(1, 5)
    world['factions'][defender]['power'] = max(0, world['factions'][defender]['power'] - damage)
    world['factions'][attacker]['power'] = min(100, world['factions'][attacker]['power'] + 1)
    event(world, 'feud', f'{attacker} struck {defender}; {defender} lost {damage} power.')
    for case in world['cases']:
        if case['status'] == 'open':
            case['evidence'] += 1
            remember(world, 'Detective Vale', f'Case {case["id"]}: new evidence recovered.')
            event(world, 'investigation', f'Detective Vale found evidence in case {case["id"]}.')
            if case['evidence'] >= 3 and not world['player']['arrested']:
                world['player']['arrested'] = True
                world['player']['custody'] = 'pretrial'
                case['status'] = 'charged'
                event(world, 'arrest', 'Rookie arrested and charged; hearing pending.')
    return world


def resolve_case(world):
    charged = next((c for c in world['cases'] if c['status'] == 'charged'), None)
    if not charged:
        return event(world, 'court', 'No charged case is awaiting a hearing.')
    charged['status'] = 'convicted' if charged['evidence'] >= 3 else 'dismissed'
    event(world, 'court', f'Case {charged["id"]} outcome: {charged["status"]}.')
    if charged['status'] == 'convicted':
        world['player']['custody'] = 'sentenced'
        event(world, 'sentencing', 'Rookie sentenced to accelerated custody.')
        world['player']['cash'] = max(0, world['player']['cash'] - 50)
        world['player']['heat'] = max(0, world['player']['heat'] - 2)
        event(world, 'prison', 'Rookie completed an accelerated sentence; the city kept changing.')
    else:
        event(world, 'release', 'Rookie released after dismissal.')
    world['player']['arrested'] = False
    world['player']['custody'] = 'free'
    return world['events'][-1]


def run(seed=42, days=5, commit_crime=True):
    world = new_world(seed)
    if commit_crime:
        robbery(world)
    for _ in range(days):
        advance(world)
        if world['player']['arrested']:
            resolve_case(world)
    return world


def main():
    parser = argparse.ArgumentParser(description='Living crime city simulation')
    parser.add_argument('--days', type=int, default=5)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--no-crime', action='store_true')
    parser.add_argument('--save', default='world_save.json')
    args = parser.parse_args()
    if args.days < 0:
        parser.error('--days must be >= 0')
    world = run(args.seed, args.days, not args.no_crime)
    for item in world['events']:
        print(f'Day {item["day"]:02d} [{item["kind"]}] {item["message"]}')
    print('\nFACTION POWER:')
    for name, info in world['factions'].items():
        print(f'  {name}: {info["power"]}')
    print('\nNPC MEMORY:')
    for name, info in world['people'].items():
        print(f'  {name}: {len(info["memory"])} memories')
    path = Path(args.save)
    path.write_text(json.dumps(world, indent=2), encoding='utf-8')
    print(f'\nSaved world to {path}')

if __name__ == '__main__':
    main()
