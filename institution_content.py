"""Pinned institutional mandates and presentation; no character-name policies."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

CIVILIAN = 'goon.institution.civilian_desk'
INTAKE = 'goon.institution.police_intake'
PATH = Path(__file__).parent / 'content' / 'institutions_v1.json'


@lru_cache(maxsize=1)
def _pack():
    from career_persistence import _unique_object
    from location_registry import load as atlas
    def require(ok):
        if not ok:
            raise ValueError('Unsupported institution definition')
    try:
        data = json.loads(PATH.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
        require(type(data['version']) is int and data['version'] == 1)
        require(type(data['clarification_days']) is int and data['clarification_days'] == 3)
        require(set(data['actors']) == {CIVILIAN, INTAKE})
        places = {p['id']: p for p in atlas()['places']}
        for ident, actor in data['actors'].items():
            require(all(isinstance(actor[k], str) and actor[k] for k in ('name','staff','routine','mandate')))
            require(actor['place'] in places and places[actor['place']]['access'] == ['PUB'])
            require(actor['kind'] == ('civilian' if ident == CIVILIAN else 'police_intake'))
            require(type(actor['delay']) is int and actor['delay'] == (1 if ident == CIVILIAN else 2))
            require(sorted(actor['topics']) == (['alarm','cause','delivery_day'] if ident == CIVILIAN else ['alarm','cause']))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError('Invalid or unavailable pinned institution definitions') from exc
    pin = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return data, pin


def load():
    return deepcopy(_pack()[0])


def fingerprint():
    return _pack()[1]
