"""Mission 024 test policies; no game commands or mechanics are introduced."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import random
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game_service import (actions_remaining, advance_day, execute_command,
    incident_report, institution_report)
from incident_dispatch import WRONG_NOTICE
from institution_content import CIVILIAN
import institution_campaigns as campaigns


def run(seed, policy, days, resume_every):
    original_play = campaigns.play_day
    last_world = None
    rejected_polls = 0

    def play(world, unused_mode):
        nonlocal last_world, rejected_polls
        last_world = world
        if policy == 'unattended':
            campaigns.go(world, 'goon.poi.p032')
            from daily_life import opportunities
            for row in opportunities(world):
                if any(o['id'] == 'work' and o['availability'] == 'available' for o in row['options']):
                    execute_command(world, 'choose', choice_id=row['id'], option_id='work')
                    break
            advance_day(world)
            return

        original_play(world, 'unchecked')
        view = institution_report(world, CIVILIAN)['actors'][0]
        originals = [r for r in view['submissions'] if r['correction_of'] is None
            and r['source_id'].endswith('.claim.poster')]
        if not originals:
            return
        own_corrections = [r for r in view['submissions'] if r['correction_of']]
        last_response = view['responses'][-1] if view['responses'] else None
        if len(own_corrections) == 3 and last_response is not None and all(
                any(r['id'] == c['id'] and r['processed_day'] is not None
                    for r in last_response['reports']) for c in own_corrections):
            return
        campaigns.go(world, view['place'])
        incident = next(r for r in incident_report(world)['incidents'] if r['id'].startswith(WRONG_NOTICE))
        campaigns.choice(world, incident['id'], 'verify', 'ledger')
        if actions_remaining(world) >= 1:
            before, rng = deepcopy(world), random.getstate()
            try:
                execute_command(world, 'institution_followup', institution_id=CIVILIAN,
                    incident_id=incident['id'])
            except ValueError:
                if world != before or random.getstate() != rng:
                    raise AssertionError('Rejected response poll changed world/RNG')
                rejected_polls += 1
        view = institution_report(world, CIVILIAN)['actors'][0]
        source = next((s for s in view['sources'] if s['source_id'].endswith('.claim.ledger')), None)
        if source is None or actions_remaining(world) < 1:
            return
        corrected = {r['correction_of'] for r in view['submissions'] if r['correction_of']}
        candidates = originals + [r for reply in view['responses'] for r in reply['reports']
            if r['sender'] == 'npc' and r['topic'] == 'delivery_day' and r['credibility'] != 'documented']
        target = next((r for r in candidates if r['id'] not in corrected), None)
        if target is not None:
            execute_command(world, 'institution_correct', institution_id=CIVILIAN,
                report_id=target['id'], source_id=source['source_id'])

    with patch.object(campaigns, 'play_day', side_effect=play):
        result = campaigns.run(seed, policy, days, resume_every)
    commands = [e for e in last_world['events'] if e['kind'] == 'player_command'
        and e['command'].startswith('institution_')]
    result['player_institution_commands'] = len(commands)
    result['legitimate_corrections'] = sum(e['command'] == 'institution_correct' for e in commands)
    result['rejected_polls_pure'] = rejected_polls
    if policy == 'unattended':
        if commands or last_world['institutions']['receipts']:
            raise AssertionError('Unattended policy contacted an institution')
    elif result['legitimate_corrections'] != 3 or result['responses'] < 3 or result['correction_copies'] != 1:
        raise AssertionError(('Correction/follow-up scenario incomplete', result))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', choices=('unattended', 'corrections'), required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--days', type=int, default=90)
    parser.add_argument('--resume-every', type=int, default=1)
    args = parser.parse_args()
    if not 20 <= args.days <= 1000 or not 1 <= args.resume_every <= args.days:
        parser.error('days must be 20-1000; resume-every must be 1-days')
    print(json.dumps(run(args.seed, args.policy, args.days, args.resume_every), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
