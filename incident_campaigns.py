"""Offline Night Shift campaign replay, with actual disk resume checkpoints."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time

from game_service import (advance_day, create_career, execute_command, incident_report,
                          load_career, save_career)
from incident_content import fingerprint


def start(seed):
    world = create_career(seed)
    execute_command(world, 'settle_in')
    advance_day(world)
    execute_command(world, 'enable_incidents')
    return world


def play_day(world):
    """Public knowledge and service commands only; ordinary work continues."""
    if world['navigation']['location_id'] != 'goon.poi.p032':
        execute_command(world, 'travel', destination='p032', mode='walk')
    report = incident_report(world)
    if report['discovery_channels']:
        execute_command(world, 'discover_incident', incident_id=report['id'], channel='public_notice')
    for stage in ('offer', 'work', 'report', 'followup'):
        report = incident_report(world)
        row = next((r for r in report['choices'] if r['stage'] == stage), None)
        if row:
            desired = {'offer': 'accept', 'work': 'verify', 'report': 'disclose', 'followup': 'work'}[stage]
            if any(o['id'] == desired for o in row['options']):
                execute_command(world, 'incident_choose', incident_id=report['id'], stage=stage, option_id=desired)
    from daily_life import opportunities
    for row in opportunities(world):
        option = next((o for o in row['options'] if o['availability'] == 'available' and o['id'] == 'work'), None)
        if option:
            execute_command(world, 'choose', choice_id=row['id'], option_id=option['id'])
            break
    advance_day(world)


def run(seed, days=180, resume_every=30):
    started = time.perf_counter()
    a, b = start(seed), start(seed)
    resumes = 0
    with tempfile.TemporaryDirectory(prefix='goon-incident-replay-') as folder:
        path = Path(folder) / 'career.json'
        for index in range(days):
            play_day(a)
            play_day(b)
            if (index + 1) % resume_every == 0 or index + 1 == days:
                save_career(b, path)
                b = load_career(path)
                resumes += 1
            if a != b:
                raise AssertionError(('campaign replay diverged', seed, index))
    state = a['incidents']
    return dict(seed=seed, days=days, resumes=resumes, content_fingerprint=fingerprint(),
        world_status=state['world_status'], player_outcome=state['aftermath']['player_outcome'],
        followup=state['followup'], total_compensation=sum(r['pay'] for r in state['receipts']),
        cash=a['player']['cash'], arrears=a['daily_life']['housing']['arrears'],
        world_sha256=hashlib.sha256(json.dumps(a, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        elapsed_seconds=round(time.perf_counter() - started, 3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=180)
    parser.add_argument('--seeds', type=int, nargs='+', default=[17, 42])
    parser.add_argument('--resume-every', type=int, default=30)
    args = parser.parse_args()
    if not 10 <= args.days <= 1000 or not 1 <= args.resume_every <= args.days:
        parser.error('days must be 10-1000; resume-every must be 1-days')
    for seed in args.seeds:
        print(json.dumps(run(seed, args.days, args.resume_every), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
