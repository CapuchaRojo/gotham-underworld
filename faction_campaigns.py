"""Repeatable idle-city audit: python -B faction_campaigns.py (JSON to stdout)."""
import argparse
from collections import Counter
import hashlib
import json

from career_state import validate
from game_service import create_career
from gameplay import next_day


def run_campaign(seed, days):
    """Use the same daily reducer as wait, without interface transaction copies.

    No player commands, state edits, balance assertions, or external services.
    A faction is active when it performs a non-hold operation in the last 30 days.
    Sole-lead counts exclude days tied on district holdings.
    """
    if type(days) is not int or days < 1:
        raise ValueError('days must be a positive integer')
    world = create_career(seed)
    factions = sorted(world['competition']['factions'])
    sole_lead, tied_days, violations = Counter(), 0, 0
    for _ in range(days):
        next_day(world, legal_rules=True)
        holdings = Counter(d['owner'] for d in world['districts'].values())
        maximum = max(holdings.values())
        leaders = [name for name in factions if holdings[name] == maximum]
        if len(leaders) == 1:
            sole_lead[leaders[0]] += 1
        else:
            tied_days += 1
        for name in factions:
            profile = world['competition']['profiles'][world['competition']['factions'][name]]
            data = world['factions'][name]
            violations += not (0 <= data['cash'] <= profile['treasury_cap'] and 0 <= data['power'] <= 100)
    validate(world)
    recent = [e for e in world['events'] if e['day'] > days - 30 and e['kind'] == 'faction_warfare']
    rows = {}
    for name in factions:
        actions = Counter(e['action'] for e in recent if e['faction'] == name)
        rows[name] = {'cash': world['factions'][name]['cash'], 'power': world['factions'][name]['power'],
                      'districts': sum(d['owner'] == name for d in world['districts'].values()),
                      'active': any(action != 'hold' and count for action, count in actions.items()),
                      'last_30_days': dict(sorted(actions.items())), 'sole_lead_days': sole_lead[name]}
    return {'seed': seed, 'days': days, 'factions': rows, 'tied_lead_days': tied_days,
            'captures': sum(e.get('captured') is True or e.get('cause') == 'control_exhausted' for e in world['events']),
            'bound_violations': violations,
            'state_sha256': hashlib.sha256(json.dumps(world, sort_keys=True).encode('utf-8')).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description='Audit deterministic faction campaigns')
    parser.add_argument('--seeds', type=int, nargs='+', default=[1, 17, 42, 99])
    parser.add_argument('--days', type=int, default=365)
    parser.add_argument('--long-seed', type=int, default=42)
    parser.add_argument('--long-days', type=int, default=1000)
    args = parser.parse_args()
    if args.days < 1 or args.long_days < 1:
        parser.error('campaign lengths must be positive')
    print(json.dumps([run_campaign(seed, args.days) for seed in args.seeds] +
                     [run_campaign(args.long_seed, args.long_days)], indent=2))


if __name__ == '__main__':
    main()
