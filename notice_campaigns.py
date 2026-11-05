"""Two-incident public-command campaigns, deterministic replay and disk resume."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time

from game_service import (create_career, execute_command, advance_day, incident_report,
                          save_career, load_career)
from incident_dispatch import WRONG_NOTICE
from notice_content import fingerprint


def start(seed):
    w = create_career(seed)
    execute_command(w, 'settle_in')
    advance_day(w)
    execute_command(w, 'enable_incidents')
    execute_command(w, 'enable_incident', definition_id=WRONG_NOTICE)
    return w


def go(w, destination):
    ident = {'store': 'goon.poi.p032', 'hub': 'goon.neighborhood.n13'}[destination]
    if w['navigation']['location_id'] != ident:
        execute_command(w, 'travel', destination=ident, mode='walk')


def rows(w):
    return incident_report(w)['incidents']


def option(w, ident, stage, selection):
    row = incident_report(w, ident)
    if any(r['stage'] == stage and any(o['id'] == selection for o in r['options']) for r in row['choices']):
        execute_command(w, 'incident_choose', incident_id=ident, stage=stage, option_id=selection)
        return True
    return False


def play_day(w, mode):
    go(w, 'store')
    for row in rows(w):
        if row['discovery_channels'] and (mode != 'missed' or not row['id'].startswith(WRONG_NOTICE)):
            execute_command(w, 'discover_incident', incident_id=row['id'], channel='public_notice')
    for row in rows(w):
        if not row['id'].startswith(WRONG_NOTICE):
            option(w, row['id'], 'offer', 'refuse')
            continue
        if not row['known']:
            continue
        journal, ident = row['journal'], row['id']
        if w['day'] < journal['deadline']:
            go(w, 'hub')
            if mode in ('help', 'reserve'):
                option(w, ident, 'verify', 'ledger')
            if mode == 'help':
                option(w, ident, 'response', 'notify_desk')
                option(w, ident, 'repair', 'warn_group')
            elif mode == 'unchecked':
                option(w, ident, 'response', 'repeat_notice')
            elif mode == 'reserve':
                if not option(w, ident, 'response', 'reserve_slot'):
                    # A known unavailable vacancy creates no retry/reroll loop.
                    if incident_report(w, ident)['journal']['finding'] is not None:
                        option(w, ident, 'response', 'refuse')
        elif journal['deadline'] < w['day'] < journal['deadline'] + 4 and (
                journal['decisions']['aftermath'] is None or
                (journal['followup'] is not None and journal['decisions']['followup'] is None)):
            go(w, 'hub')
            option(w, ident, 'followup', 'work')
            option(w, ident, 'aftermath', 'read')
    go(w, 'store')
    from daily_life import opportunities
    for row in opportunities(w):
        if any(o['id'] == 'work' and o['availability'] == 'available' for o in row['options']):
            execute_command(w, 'choose', choice_id=row['id'], option_id='work')
            break
    advance_day(w)


def run(seed, mode='help', days=365, resume_every=30):
    started = time.perf_counter()
    a, b = start(seed), start(seed)
    resumes = 0
    with tempfile.TemporaryDirectory(prefix='goon-two-incident-') as folder:
        path = Path(folder) / 'career.json'
        for index in range(days):
            play_day(a, mode)
            play_day(b, mode)
            if (index + 1) % resume_every == 0 or index + 1 == days:
                save_career(b, path)
                b = load_career(path)
                resumes += 1
            if a != b:
                raise AssertionError(('two-incident replay diverged', seed, mode, index))
    notice = a['wrong_notice']
    return dict(seed=seed, mode=mode, days=days, resumes=resumes, content_fingerprint=fingerprint(),
        night_shift_outcome=a['incidents']['aftermath']['player_outcome'],
        notice_outcome=notice['aftermath']['outcome'], audience_beliefs=notice['audiences'],
        incident_compensation=sum(r['pay'] for r in notice['receipts']), cash=a['player']['cash'],
        arrears=a['daily_life']['housing']['arrears'],
        world_sha256=hashlib.sha256(json.dumps(a, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        elapsed_seconds=round(time.perf_counter() - started, 3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=365)
    parser.add_argument('--seed', type=int, default=73)
    parser.add_argument('--mode', choices=('help','unchecked','reserve','missed'), default='help')
    parser.add_argument('--resume-every', type=int, default=30)
    args = parser.parse_args()
    if not 15 <= args.days <= 1000 or not 1 <= args.resume_every <= args.days:
        parser.error('days must be 15-1000; resume-every must be 1-days')
    print(json.dumps(run(args.seed, args.mode, args.days, args.resume_every), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
