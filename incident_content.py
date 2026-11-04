"""Pinned offline incident definitions, independent of engine/character names."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

PATH = Path(__file__).parent / 'content' / 'night_shift_v1.json'


@lru_cache(maxsize=1)
def _pack():
    from career_persistence import _unique_object
    from location_registry import load as places
    def require(condition):
        if not condition:
            raise ValueError('Unsupported incident definition')
    try:
        data = json.loads(PATH.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
        require(type(data['version']) is int and data['version'] == 1)
        ids = {p['id'] for p in places()['places']}
        require(data['place'] in ids and data['hub'] in ids)
        require(all(isinstance(data[k], str) and data[k] for k in ('id', 'title', 'contact_id')))
        require(set(data['causes']) == {'break_in', 'faulty_alarm', 'delivery_error'})
        require(all(isinstance(v, str) and v for v in data['causes'].values()))
        require(all(isinstance(data['contact'][k], str) and data['contact'][k]
                    for k in ('name', 'role', 'personality', 'need', 'knowledge')))
        require(all(type(data[k]) is int and 0 <= data[k] <= 20
                    for k in ('complete_pay', 'partial_pay', 'followup_pay')))
        bindings = {'offer': {'accept': 1, 'help': 1, 'refuse': 0}, 'work': {'verify': 1},
                    'report': {'disclose': 1, 'withhold': 0}, 'followup': {'work': 1}}
        require(set(data['stages']) == set(bindings))
        for stage, costs in bindings.items():
            definition = data['stages'][stage]
            require(all(isinstance(definition[k], str) and definition[k] for k in ('title', 'situation', 'speaker')))
            require(len(definition['options']) == len(costs))
            require({o['id'] for o in definition['options']} == set(costs))
            for option in definition['options']:
                require(type(option['actions']) is int and option['actions'] == costs[option['id']])
                require(all(isinstance(option[k], str) and option[k] for k in ('label', 'tradeoff')))
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        raise ValueError('Invalid or unavailable pinned incident content') from exc
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return data, digest


def load():
    return deepcopy(_pack()[0])


def fingerprint():
    return _pack()[1]
