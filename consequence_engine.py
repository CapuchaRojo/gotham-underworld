"""M003: reproducible job outcomes and traceable consequences (original IP)."""
import random
from simulation import event, remember
from relationship_engine import on_job, on_investigation

GANGS = ('Harbor Syndicate', 'Carnival Crew', 'Iron Mask Outfit')
RISKS = {'courier': 18, 'collection': 40}


def prepare(world):
    world.setdefault('job_attempts', 0)
    world.setdefault('consequence_version', 1)
    return world


def execute_job(world, kind, details):
    """Resolve one job; no global random state, all rolls stored in event metadata."""
    prepare(world)
    player = world['player']
    faction = player['faction']
    attempt = world['job_attempts']
    world['job_attempts'] += 1
    rng = random.Random(f'{world["seed"]}:{world["day"]}:{attempt}:{kind}')
    chance = min(95, max(10, RISKS[kind] - min(15, player['reputation'][faction] * 2)))
    roll = rng.randrange(100)
    success = roll >= chance
    payout = details['reward'] if success else 0
    player['cash'] += payout
    player['heat'] += details['heat'] + (1 if not success else 0)
    player['reputation'][faction] += details['reputation'] if success else -1
    if success:
        player['jobs_completed'] += 1
    result = event(world, 'job', f'Rookie {"completed" if success else "failed"} {kind} for {faction}; earned ${payout}.',
                   job=kind, attempt=attempt, success=success, roll=roll, failure_chance=chance,
                   payout=payout, cause='player_job')
    for name, person in world['people'].items():
        if person['faction'] == faction:
            remember(world, name, f'Rookie {"completed" if success else "failed"} {kind} for {faction} (attempt {attempt}).')
    rival = next((g for g in GANGS if g != faction), None)
    on_job(world, faction, kind, success, attempt, rival=rival)
    if kind == 'collection':
        witnessed = rng.randrange(100) < (65 if not success else 35)
        if witnessed:
            case_id = max((c['id'] for c in world['cases']), default=0) + 1
            case = {'id': case_id, 'crime': 'collection intimidation', 'evidence': 1,
                    'status': 'pending', 'suspect': player['name'], 'source_attempt': attempt,
                    'witnessed': True, 'investigation_days': 0,
                    'last_investigated_day': world['day']}
            world['cases'].append(case)
            event(world, 'witness', f'Witness reported collection job attempt {attempt}; case {case_id} opened.',
                  case_id=case_id, source_attempt=attempt, cause='witness_report')
        if not success:
            player['reputation'][rival] = player['reputation'].get(rival, 0) - 1
            world['factions'][faction]['power'] = max(0, world['factions'][faction]['power'] - 1)
            event(world, 'retaliation', f'{rival} exploited the failed collection; {faction} lost 1 power.',
                  source_attempt=attempt, cause='failed_collection')
    return result


def investigate(world):
    """Advance M003 cases once per day, keeping legacy M001 cases untouched."""
    prepare(world)
    for case in world['cases']:
        if case['status'] != 'pending':
            continue
        if case.get('last_investigated_day', -1) >= world['day']:
            continue
        case['last_investigated_day'] = world['day']
        case['investigation_days'] += 1
        case['evidence'] += 1
        remember(world, 'Detective Vale', f'Case {case["id"]}: evidence from job attempt {case["source_attempt"]}.')
        on_investigation(world, case)
        event(world, 'investigation', f'Detective Vale recovered evidence in case {case["id"]}.',
              case_id=case['id'], source_attempt=case['source_attempt'], cause='witness_followup')
        if case['evidence'] >= 3 and not world['player']['arrested']:
            case['status'] = 'charged'
            world['player']['arrested'] = True
            world['player']['custody'] = 'pretrial'
            event(world, 'arrest', f'Rookie arrested on case {case["id"]}.',
                  case_id=case['id'], source_attempt=case['source_attempt'], cause='evidence_threshold')
