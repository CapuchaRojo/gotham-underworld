"""Reproducible M015 acceptance campaigns, using public service commands only."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from career_state import validate
from game_service import (advance_day, choice_report, create_career, execute_command,
                          load_career, save_career)

BRANCH_SEEDS = {'lawful': 42, 'criminal': 3, 'relationship': 17, 'low_cash': 17, 'mixed': 42}


def _go(world, destination):
    target = {'home': 'goon.poi.p031', 'store': 'goon.poi.p032', 'hub': 'goon.neighborhood.n13'}[destination]
    if world['navigation']['location_id'] != target:
        execute_command(world, 'travel', destination=target, mode='auto')


def _select(world, week, definition, option):
    return execute_command(world, 'choose', choice_id=f'goon.choice.{week}.{definition}', option_id=option)


def play_day(world, branch):
    """A policy for validation, not an autoplay mechanic in the game CLI."""
    day = world['day']
    week, offset = divmod(day - world['daily_life']['activation_day'], 7)
    policy = 'lawful' if branch == 'low_cash' and week > 0 else branch
    if offset == 0:
        _go(world, 'home')
        _select(world, week, 'promise', 'promise' if policy in ('relationship', 'mixed', 'low_cash') else 'decline')
        if policy in ('criminal', 'low_cash') and not any(m['fact'] == 'terms_disclosed' for m in world['daily_life']['contacts']['goon.contact.cal']['memories']):
            _go(world, 'hub')
            _select(world, week, 'cal_intro', 'ask')
        if policy in ('criminal', 'low_cash'):
            _select(world, week, 'opening_shift', 'decline')
        else:
            _go(world, 'store')
            _select(world, week, 'opening_shift', 'work')
        if branch == 'low_cash' and week > 0 and world['daily_life']['housing']['arrears']:
            _go(world, 'home')
            execute_command(world, 'pay_room')
    elif offset == 1:
        if policy in ('criminal', 'low_cash'):
            _go(world, 'hub')
            if world['player']['faction'] is None:
                execute_command(world, 'join', faction='Harbor Syndicate')
            _select(world, week, 'crossroads', 'collection')
        elif policy == 'relationship':
            _go(world, 'home')
            _select(world, week, 'crossroads', 'help')
        elif policy == 'mixed':
            _go(world, 'home')
            _select(world, week, 'crossroads', 'renegotiate')
        else:
            _go(world, 'store')
            _select(world, week, 'crossroads', 'lawful')
    elif offset == 3:
        if policy in ('criminal', 'low_cash'):
            _select(world, week, 'midweek_shift', 'decline')
        else:
            _go(world, 'store')
            _select(world, week, 'midweek_shift', 'work')
    elif offset == 4:
        if policy == 'low_cash':
            _select(world, week, 'late_work', 'decline')
        elif policy == 'criminal':
            _go(world, 'hub')
            report = choice_report(world, f'goon.choice.{week}.late_work')
            if any(o['id'] == 'courier' and o['availability'] == 'available' for o in report['options']):
                _select(world, week, 'late_work', 'courier')
            else:
                _select(world, week, 'late_work', 'decline')
        else:
            _go(world, 'store')
            _select(world, week, 'late_work', 'audit' if policy == 'relationship' else 'work')
    if branch == 'low_cash' and world['daily_life']['housing']['arrears']:
        reviews = [r for r in world['daily_life']['choices'].values() if r['definition_id'] == 'room_review' and
                   r['state'] == 'open' and r['open_day'] <= day < r['expires_day']]
        if reviews:
            _go(world, 'home')
            execute_command(world, 'choose', choice_id=sorted(reviews, key=lambda r: r['id'])[0]['id'], option_id='help')


def run_campaign(branch, *, seed=None, days=7, resume=False):
    if branch not in BRANCH_SEEDS or type(days) is not int or days < 1:
        raise ValueError('Choose a known branch and a positive day count')
    world = create_career(BRANCH_SEEDS[branch] if seed is None else seed)
    execute_command(world, 'settle_in')
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'campaign.json'
        for _ in range(days):
            advance_day(world)
            play_day(world, branch)
            validate(world)
            if resume:
                save_career(world, path)
                restored = load_career(path)
                if restored != world:
                    raise AssertionError('Disk resume changed the campaign')
                world = restored
    return world


def summary(world):
    life = world['daily_life']
    return dict(day=world['day'], cash=world['player']['cash'], heat=world['player']['heat'],
        arrears=life['housing']['arrears'], prepaid=life['housing']['prepaid'],
        contacts={k: p['standing'] for k, p in sorted(life['contacts'].items())},
        promises={status: sum(p['status'] == status for p in life['promises'].values()) for status in ('pending', 'kept', 'broken')},
        cases=[c['status'] for c in world['cases']], jobs=world['job_attempts'],
        transactions=len(life['transactions']),
        sha256=hashlib.sha256(json.dumps(world, sort_keys=True).encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    for branch in BRANCH_SEEDS:
        print(json.dumps(dict(branch=branch, **summary(run_campaign(branch, days=args.days, resume=args.resume))), sort_keys=True))


if __name__ == '__main__':
    main()
