"""M002 interactive career layer, compatible with the M001.1 simulation."""
import argparse
import json
from pathlib import Path
from simulation import new_world, advance, resolve_case, event, remember
from consequence_engine import execute_job, investigate, prepare as prepare_consequences
from relationship_engine import prepare as prepare_relationships, on_join, decision
from npc_actions import act as npc_act, prepare as prepare_npc_actions
from city_economy import prepare as prepare_economy, advance as economy_advance, on_job as economy_on_job, summary as district_summary

from district_missions import prepare as prepare_missions, mission as run_mission, available as mission_districts
from faction_warfare import prepare as prepare_warfare, advance as warfare_advance

GANGS = ('Harbor Syndicate', 'Carnival Crew', 'Iron Mask Outfit')
JOBS = {
    'courier': {'reward': 25, 'heat': 0, 'reputation': 1},
    'collection': {'reward': 60, 'heat': 2, 'reputation': 2},
}


def prepare(world):
    player = world['player']
    player.setdefault('faction', None)
    player.setdefault('reputation', {name: 0 for name in GANGS})
    player.setdefault('jobs_completed', 0)
    prepare_consequences(world)
    prepare_relationships(world)
    prepare_npc_actions(world)
    prepare_economy(world)
    prepare_missions(world)
    prepare_warfare(world)
    return world


def join(world, faction):
    prepare(world)
    if faction not in GANGS:
        raise ValueError('Unknown recruitable faction')
    if world['player']['arrested']:
        raise ValueError('Cannot join while detained')
    if world['player']['faction'] is not None:
        raise ValueError('Already affiliated; switching is not implemented')
    world['player']['faction'] = faction
    world['player']['reputation'][faction] += 1
    for person, data in world['people'].items():
        if data['faction'] == faction:
            remember(world, person, f'Rookie joined {faction}.')
    result = event(world, 'recruitment', f'Rookie joined {faction}.')
    on_join(world, faction)
    return result


def job(world, kind):
    prepare(world)
    if kind not in JOBS:
        raise ValueError('Unknown job')
    player = world['player']
    if player['arrested']:
        raise ValueError('Cannot work while detained')
    if player['faction'] is None:
        raise ValueError('Join a faction first')
    result = execute_job(world, kind, JOBS[kind])
    economy_on_job(world, result)
    return result


def next_day(world):
    advance(world)
    investigate(world)
    npc_act(world)
    economy_advance(world)
    warfare_advance(world)
    if world['player']['arrested']:
        resolve_case(world)
    return world


def save(world, filename):
    path = Path(filename)
    path.write_text(json.dumps(world, indent=2), encoding='utf-8')
    return path


def load(filename):
    world = json.loads(Path(filename).read_text(encoding='utf-8'))
    if not isinstance(world, dict) or not all(k in world for k in ('player', 'factions', 'people', 'events', 'cases', 'day', 'seed')):
        raise ValueError('Invalid saved world')
    return prepare(world)


def show(world):
    p = world['player']
    print(f'Day {world["day"]} | Cash ${p["cash"]} | Heat {p["heat"]} | Faction {p.get("faction") or "None"}')
    print('Reputation:', p.get('reputation', {}))
    print('Cases:', [(c['id'], c['status']) for c in world['cases']])


def play(world, filename):
    prepare(world)
    print('UNDERWORLD - M008 autonomous faction warfare prototype. Type help for commands.')
    while True:
        try:
            command = input('underworld> ').strip().split()
        except (EOFError, KeyboardInterrupt):
            print('\nSession ended; use save to persist changes next time.')
            break
        if not command:
            continue
        verb, *args = command
        try:
            if verb == 'help':
                print('status | factions | districts | missions | mission <scout|fortify|expand> <district-number> | relationships | join <number> | jobs | job <courier|collection> | wait | events | save | quit')
            elif verb == 'status':
                show(world)
            elif verb == 'relationships':
                for name, person in world['people'].items():
                    choice = decision(world, name)
                    print(f'{name}: {person["relationship"]} | {choice["action"]} ({choice["reason"]})')
            elif verb == 'districts':
                for name, data in district_summary(world):
                    print(f'{name}: {data["owner"]} | wealth {data["wealth"]} | control {data["control"]}')
            elif verb == 'missions':
                for index, name in mission_districts(world):
                    print(f'{index}. {name}')
                print('Mission costs: scout $5 | fortify $15 | expand $30; one mission per day')
            elif verb == 'mission' and len(args) == 2:
                index = int(args[1])
                names = list(world['districts'])
                if not 1 <= index <= len(names):
                    raise ValueError('Invalid district number')
                print(run_mission(world, args[0], names[index - 1])['message'])
            elif verb == 'factions':
                for i, faction in enumerate(GANGS, 1):
                    print(f'{i}. {faction} (power {world["factions"][faction]["power"]})')
            elif verb == 'join' and len(args) == 1:
                index = int(args[0])
                if not 1 <= index <= len(GANGS):
                    raise ValueError('Choose faction 1, 2, or 3')
                print(join(world, GANGS[index - 1])['message'])
            elif verb == 'jobs':
                for name, data in JOBS.items():
                    print(f'{name}: ${data["reward"]}, heat +{data["heat"]}, reputation +{data["reputation"]}')
            elif verb == 'job' and len(args) == 1:
                print(job(world, args[0])['message'])
            elif verb == 'wait':
                before = len(world['events'])
                next_day(world)
                for e in world['events'][before:]:
                    print(f'Day {e["day"]}: {e["message"]}')
            elif verb == 'events':
                for e in world['events'][-10:]:
                    print(f'Day {e["day"]} [{e["kind"]}] {e["message"]}')
            elif verb == 'save':
                print(f'Saved to {save(world, filename)}')
            elif verb == 'quit':
                print(f'Saved to {save(world, filename)}')
                break
            else:
                print('Unknown command. Type help.')
        except (ValueError, OSError) as exc:
            print(f'Cannot complete command: {exc}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', action='store_true', help='Resume an existing save')
    parser.add_argument('--save', default='career_save.json')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    try:
        world = load(args.save) if args.load else prepare(new_world(args.seed))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f'Could not load save: {exc}')
    play(world, args.save)


if __name__ == '__main__':
    main()
