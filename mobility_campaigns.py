"""Offline M016-A stress/replay evidence using public player commands only."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time

from game_service import create_career, execute_command, advance_day, save_career, load_career
import mobility
from mobility_content import OVERLAY_ID, fingerprint


def start(seed):
    world = create_career(seed)
    execute_command(world, 'settle_in')
    execute_command(world, 'travel', destination='p039', mode='auto')
    execute_command(world, 'enable_mobility', overlay_id=OVERLAY_ID, request_id='campaign.adoption')
    advance_day(world)
    return world


def run(seed, days, resume_every):
    started = time.perf_counter()
    a, b = start(seed), start(seed)
    with tempfile.TemporaryDirectory(prefix='goon-mobility-replay-') as directory:
        # TemporaryDirectory cleanup is confined to this explicitly verified target.
        assert Path(directory).resolve().parent == Path(tempfile.gettempdir()).resolve()
        path = Path(directory) / 'career.json'
        resumes = 0
        for day in range(days):
            for destination in ('p071', 'p039'):
                for world in (a, b):
                    quote = mobility.plan_route(world, destination, 'fastest')
                    if not quote['affordable']:
                        raise AssertionError('ordinary free fallback became unaffordable')
                    execute_command(world, 'journey', **quote['arguments'])
                assert a == b, ('command replay divergence', seed, day, destination)
            for world in (a, b):
                advance_day(world)
            if (day + 1) % resume_every == 0 or day == days - 1:
                save_career(b, path)
                b = load_career(path)
                resumes += 1
            assert a == b, ('day/resume divergence', seed, day)
    trips = [e for e in a['events'] if e['kind'] == 'travel' and e.get('schema_version') == 2]
    return dict(seed=seed, days=days, resumed_checkpoints=resumes,
        journeys=len(trips), monorail_boardings=sum(l['kind'] == 'board' for t in trips for l in t['legs']),
        total_fare=sum(t['resources']['cash']['cost'] for t in trips),
        cash=a['player']['cash'], arrears=a['daily_life']['housing']['arrears'],
        home=a['navigation']['home_id'], location=a['navigation']['location_id'],
        day=a['day'], overlay_fingerprint=fingerprint(),
        world_sha256=hashlib.sha256(json.dumps(a, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        elapsed_seconds=round(time.perf_counter() - started, 3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=30)
    parser.add_argument('--seeds', type=int, nargs='+', default=[17, 42])
    parser.add_argument('--resume-every', type=int, default=7)
    args = parser.parse_args()
    if not 1 <= args.days <= 1000 or not 1 <= args.resume_every <= args.days:
        parser.error('days must be 1-1000; resume-every must be 1-days')
    for seed in args.seeds:
        print(json.dumps(run(seed, args.days, args.resume_every), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
