"""M011 CLI and legacy career reducers; player commands use game_service."""
import argparse
from copy import deepcopy
from pathlib import Path
from career_state import prepare as prepare_career, validate
from career_persistence import read as read_career, write as write_career
from simulation import new_world, advance, resolve_case, event, remember
from consequence_engine import execute_job, investigate, prepare as prepare_consequences
from relationship_engine import prepare as prepare_relationships, on_join, decision
from npc_actions import act as npc_act, prepare as prepare_npc_actions
from city_economy import prepare as prepare_economy, advance as economy_advance, on_job as economy_on_job, summary as district_summary

from district_missions import prepare as prepare_missions, available as mission_districts
from faction_warfare import prepare as prepare_warfare, advance as warfare_advance
from city_strategy import prepare as prepare_strategy, advance as strategy_advance, summary as strategy_summary

from city_intelligence import dashboard as intelligence_dashboard, briefing as intelligence_briefing
from legal_state import report as legal_report
from faction_competition import active as competition_active
from faction_profiles import summary as competition_summary

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
    prepare_strategy(world)
    prepare_career(world)
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


def job(world, kind, *, scrutiny=None):
    prepare(world)
    if kind not in JOBS:
        raise ValueError('Unknown job')
    player = world['player']
    if player['arrested']:
        raise ValueError('Cannot work while detained')
    if player['faction'] is None:
        raise ValueError('Join a faction first')
    result = execute_job(world, kind, JOBS[kind], scrutiny=scrutiny)
    economy_on_job(world, result)
    return result


def next_day(world, *, legal_rules=False):
    # Explicit case choices must survive callers of the legacy daily reducer.
    legal_rules = legal_rules or bool(world.get('legal', {}).get('responses'))
    advance(world)
    if legal_rules:
        from legal_engine import begin_day
        pressure, deferred = begin_day(world)
    else:
        pressure, deferred = 0, ()
    investigate(world, pressure=pressure, deferred_cases=deferred)
    npc_act(world, deferred_cases=deferred)
    competition_rules = competition_active(world)
    economy_advance(world, competition=competition_rules)
    strategy_advance(world, competition=competition_rules)
    warfare_advance(world, competition=competition_rules)
    if world['player']['arrested']:
        from legal_engine import resolve
        resolve(world, legacy=not legal_rules)
    from navigation import begin_day as navigation_day
    navigation_day(world)
    return world


def save(world, filename, *, overwrite=True):
    validate(world)
    candidate = prepare(deepcopy(world))
    return write_career(candidate, filename, overwrite=overwrite)


def load(filename):
    world = prepare(read_career(filename))
    validate(world)
    return world


def show(world):
    p = world['player']
    print(f'Day {world["day"]} | Cash ${p["cash"]} | Heat {legal_report(world)["heat"]} | Faction {p.get("faction") or "None"}')
    print('Reputation:', p.get('reputation', {}))
    print('Cases:', [(c['id'], c['status']) for c in world['cases']])


def play(world, filename, *, new_career=False):
    from game_service import actions_remaining, execute_command
    from game_service import location_report, nearby_destinations, known_places, plan_route
    prepare(world)
    print('Gotham: The Goon - A Living Gotham Crime RPG')
    print("Everybody wants to rule Gotham. You're just trying to survive it.")
    print('Unofficial DC-inspired prototype; no claimed endorsement or license. Working title not legally cleared.')
    print('M014 world navigation. Three actions and 18 travel TU per day; wait to refresh.')
    print('Type help for commands.')
    while True:
        try:
            command = input('goon> ').strip().split()
        except (EOFError, KeyboardInterrupt):
            print('\nSession ended; use save to persist changes next time.')
            break
        if not command:
            continue
        verb, *args = command
        try:
            if verb == 'help':
                print('look [place] | nearby | places | route <place> [auto|walk|bus|rail|ferry] | travel <place> [mode] | enable_navigation <neighborhood>')
                print('status | legal | lay_low | cooperate <case-id> | contest <case-id> | accept <case-id> | intel | briefing [day] | factions | strategy | districts | missions | mission <scout|fortify|expand> <district-number> | relationships | join <number> | jobs | job <courier|collection> | wait | events | save | quit')
            elif verb == 'look' and len(args) <= 1:
                report = location_report(world, args[0] if args else None)
                place = report['place']
                print(f'{place["label"]} ({place["id"]}) | {place["type"]} | access {"/".join(place["access"])}')
                print(f'Parent: {place["parent_id"]} | {report["remaining_tu"]} TU remain | entry {"available" if report["accessible"] else "restricted"}')
                print('Activities:', '; '.join(report['activities']))
                print('Entry:', '; '.join(report['entry_requirements']))
                print(report['scope'])
                print(report['help'])
            elif verb in ('nearby', 'places') and not args:
                rows = nearby_destinations(world) if verb == 'nearby' else known_places(world)
                for place in rows:
                    print(f'{place["id"]}: {place["label"]} | {place["type"]} | access {"/".join(place["access"])}')
            elif verb == 'route' and 1 <= len(args) <= 2:
                quote = plan_route(world, args[0], args[1] if len(args) == 2 else 'auto')
                print(f'{quote["cost"]} TU outbound; {quote["return_cost"]} TU return; {quote["remaining_tu"]} remain | affordable: {quote["affordable"]} | round trip fits: {quote["return_fits_today"]}')
                for leg in quote['legs']:
                    print(f'{leg["mode"]}: {leg["from_id"]} -> {leg["to_id"]} ({leg["tu"]} TU)')
                print('Local journeys cost at least 1 TU. Unobserved disruptions may interrupt a journey at a safe node.')
            elif verb == 'travel' and 1 <= len(args) <= 2:
                print(execute_command(world, 'travel', destination=args[0], mode=args[1] if len(args) == 2 else 'auto')['result']['message'])
            elif verb == 'enable_navigation' and len(args) == 1:
                print(execute_command(world, 'enable_navigation', anchor=args[0])['result']['message'])
            elif verb == 'status':
                show(world)
                print('Daily actions remaining:', actions_remaining(world))
                print('Police attention:', legal_report(world)['tier'])
            elif verb == 'legal' and not args:
                report = legal_report(world)
                print(f'LEGAL | Heat {report["heat"]}/100 | attention {report["tier"]} | job risk +{report["risk_bonus"]} points | case scrutiny +{report["evidence_bonus"]} evidence/day')
                for case in report['cases']:
                    response = report['profile']['responses'].get(str(case['id']))
                    choice = response['action'] if response else 'none'
                    if response and choice == 'contest' and not response['reviewed']:
                        choice += f' (review day {response["review_day"]})'
                    print(f'Case {case["id"]}: {case["status"]} | evidence {case["evidence"]} | response {choice}')
                print('Each legal response costs one action. lay_low: free, once/day, heat -12. cooperate: free, heat -8, evidence +1, conviction fine $30.')
                print('contest: $20, two-day review, evidence <=1 dismissed; stronger cases continue. accept: immediate conviction, fine up to $35, heat -10.')
                print('One committed response per case. Ignoring a case retains automatic court resolution; fines are capped by available cash.')
            elif verb == 'lay_low' and not args:
                print(execute_command(world, 'lay_low')['result']['message'])
            elif verb in ('cooperate', 'contest', 'accept') and len(args) == 1:
                print(execute_command(world, verb, case_id=args[0])['result']['message'])
            elif verb == 'intel':
                report = intelligence_dashboard(world)
                print(f'CITY INTELLIGENCE | Day {report["day"]}')
                for rank, entry in enumerate(report['rankings'], 1):
                    print(f'{rank}. {entry["faction"]}: districts {entry["districts"]} | control {entry["control"]} | power {entry["power"]} | treasury ${entry["cash"]}')
                influence = report['player_influence']
                print(f'PLAYER INFLUENCE | faction {influence["faction"] or "none"} | missions {influence["missions"]} | expansions {influence["expansions"]} | captures {influence["captures"]} | jobs {influence["jobs"]} | successes {influence["successful_jobs"]}')
                print('TERRITORY HISTORY')
                for item in report['territory_history']:
                    print(f'Day {item["day"]}: {item["message"]}')
                if not report['territory_history']:
                    print('No recorded transfers yet.')
            elif verb == 'briefing' and len(args) <= 1:
                report = intelligence_briefing(world, int(args[0]) if args else None)
                print(f'DAY {report["day"]} BRIEFING | events {report["event_count"]} | district income ${report["income"]}')
                for message in report['highlights']:
                    print(f'- {message}')
                if not report['highlights']:
                    print('No major recorded developments.')
            elif verb == 'relationships':
                for name, person in world['people'].items():
                    choice = decision(world, name)
                    print(f'{name}: {person["relationship"]} | {choice["action"]} ({choice["reason"]})')
            elif verb == 'strategy':
                for faction, plan in strategy_summary(world):
                    if plan:
                        print(f'{faction}: {plan["objective"]} | target {plan["district"] or "none"} | {plan["reason"]}')
                    else:
                        print(f'{faction}: no strategy assessed yet')
            elif verb == 'districts':
                for name, data in district_summary(world):
                    print(f'{name}: {data["owner"]} | wealth {data["wealth"]} | control {data["control"]}')
            elif verb == 'missions':
                for index, name in mission_districts(world):
                    print(f'{index}. {name}')
                print('Mission costs: scout $5 | fortify $15 | expand $30; one mission per day')
            elif verb == 'mission' and len(args) == 2:
                index = int(args[1])
                names = sorted(world['districts'])
                if not 1 <= index <= len(names):
                    raise ValueError('Invalid district number')
                print(execute_command(world, 'mission', kind=args[0], district=names[index - 1])['result']['message'])
            elif verb == 'factions':
                for i, faction in enumerate(GANGS, 1):
                    print(f'{i}. {faction} (power {world["factions"][faction]["power"]})')
                for row in competition_summary(world):
                    rules = row['rules']
                    identity = row['profile'].replace('_', ' ')
                    print(f'{row["faction"]}: {identity} | treasury ${row["cash"]} | {row["districts"]} districts | {row["status"]}')
                    print(f'  Income {rules["revenue_percent"]}% | recovery up to ${rules["recovery_income"]}/turn | attack ${rules["attack_cost"]} | defend ${rules["defense_cost"]}')
            elif verb == 'join' and len(args) == 1:
                index = int(args[0])
                if not 1 <= index <= len(GANGS):
                    raise ValueError('Choose faction 1, 2, or 3')
                print(execute_command(world, 'join', faction=GANGS[index - 1])['result']['message'])
            elif verb == 'jobs':
                scrutiny = legal_report(world)
                for name, data in JOBS.items():
                    heat = data['heat'] + (scrutiny['collection_heat_bonus'] if name == 'collection' else 0)
                    exposure = 'witness exposure' if name == 'collection' else 'no new criminal case'
                    print(f'{name}: ${data["reward"]}, heat +{heat} (+1 on failure), reputation +{data["reputation"]} | {exposure}')
            elif verb == 'job' and len(args) == 1:
                print(execute_command(world, 'job', kind=args[0])['result']['message'])
            elif verb == 'wait':
                before = len(world['events'])
                execute_command(world, 'wait')
                for e in world['events'][before:]:
                    print(f'Day {e["day"]}: {e["message"]}')
            elif verb == 'events':
                for e in world['events'][-10:]:
                    print(f'Day {e["day"]} [{e["kind"]}] {e["message"]}')
            elif verb == 'save':
                print(f'Saved to {save(world, filename, overwrite=not new_career)}')
                new_career = False
            elif verb == 'quit':
                print(f'Saved to {save(world, filename, overwrite=not new_career)}')
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
    if not args.load and Path(args.save).exists():
        parser.error('Career already exists; use --load or choose a different --save path')
    try:
        from game_service import create_career, load_career
        world = load_career(args.save) if args.load else create_career(args.seed)
    except (OSError, ValueError) as exc:
        parser.error(f'Could not load save: {exc}')
    play(world, args.save, new_career=not args.load)


if __name__ == '__main__':
    main()
