"""One offline Wrong Notice definition, pinned separately from Night Shift."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

PATH = Path(__file__).parent / 'content' / 'wrong_notice_v1.json'


@lru_cache(maxsize=1)
def _pack():
    from career_persistence import _unique_object
    from location_registry import load as atlas
    def require(ok):
        if not ok:
            raise ValueError('Unsupported Wrong Notice definition')
    try:
        data = json.loads(PATH.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
        require(type(data['version']) is int and data['version'] == 1)
        require(data['id'] == 'goon.incident.wrong_notice.v1')
        places = {p['id'] for p in atlas()['places']}
        require(data['place'] in places and data['hub'] in places)
        require(set(data['contacts']) == {'goon.contact.notice_clerk', 'goon.contact.notice_neighbor'})
        for contact in data['contacts'].values():
            require(all(isinstance(contact.get(k), str) and contact[k] for k in ('name', 'role', 'personality', 'need', 'knowledge')))
        require(type(data['standby_pay']) is int and data['standby_pay'] == 5)
        bindings = {'compare': {'board': 1, 'residents': 1}, 'verify': {'ledger': 1},
            'response': {'correct_board': 1, 'notify_desk': 1, 'repeat_notice': 1, 'reserve_slot': 1, 'refuse': 0},
            'repair': {'warn_group': 1, 'retract': 1}, 'followup': {'work': 1}, 'aftermath': {'read': 0}}
        require(set(data['stages']) == set(bindings))
        for stage, costs in bindings.items():
            definition = data['stages'][stage]
            require(all(isinstance(definition.get(k), str) and definition[k] for k in ('title', 'speaker', 'situation')))
            require(len(definition['options']) == len(costs) and {o['id'] for o in definition['options']} == set(costs))
            for option in definition['options']:
                require(type(option['actions']) is int and option['actions'] == costs[option['id']])
                require(all(isinstance(option.get(k), str) and option[k] for k in ('label', 'tradeoff')))
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        raise ValueError('Invalid or unavailable pinned Wrong Notice content') from exc
    return data, hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load():
    return deepcopy(_pack()[0])


def fingerprint():
    return _pack()[1]
