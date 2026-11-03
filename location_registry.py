"""Validated local place definitions. No simulation, save state or network I/O."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

ATLAS_PATH = Path(__file__).parent / 'content' / 'gotham_atlas_v1.json'
MODES = ('walk', 'bus', 'rail', 'ferry')


def _require(condition, reason):
    if not condition:
        raise ValueError('Invalid atlas: ' + reason)


def validate(data):
    _require(isinstance(data, dict), 'expected an object')
    _require(type(data.get('atlas_version')) is int and data['atlas_version'] == 1,
             'unsupported atlas_version; supported: 1')
    root = data.get('root_id')
    _require(isinstance(root, str) and bool(root), 'root_id required')
    places, edges = {}, {}
    _require(isinstance(data.get('places'), list) and bool(data['places']), 'places required')
    patterns = dict(access=r'PUB|ENT|WORK|HOME|CARE|VIS|SEC|HELP', economy=r'E[1-8]',
                    security=r'S[1-5]', criminal=r'C[0-7]', civilian=r'V[1-8]', npc_pool=r'N(?:10|[1-9])')
    descriptions = data.get('profile_descriptions')
    _require(isinstance(descriptions, dict), 'profile descriptions required')
    for p in data['places']:
        _require(isinstance(p, dict), 'place must be an object')
        ident = p.get('id')
        _require(isinstance(ident, str) and bool(ident) and ident != root and ident not in places, 'duplicate/invalid place ID')
        _require(p.get('kind') in ('region', 'neighborhood', 'poi'), ident + ': invalid kind')
        for key in ('label', 'parent_id', 'region_id', 'type', 'source'):
            _require(isinstance(p.get(key), str) and bool(p[key]), ident + ': missing ' + key)
        for key, pattern in patterns.items():
            values = p.get(key)
            _require(isinstance(values, list) and bool(values) and
                     all(isinstance(v, str) and re.fullmatch(pattern, v) for v in values) and
                     len(set(values)) == len(values), ident + ': invalid ' + key)
            _require(isinstance(descriptions.get(key), dict) and all(isinstance(descriptions[key].get(v), str) and bool(descriptions[key][v]) for v in values), ident + ': missing profile description')
        places[ident] = p
    for ident, p in places.items():
        parent = places.get(p['parent_id'])
        if p['kind'] == 'region':
            _require(p['parent_id'] == root and p['region_id'] == ident, ident + ': invalid root/region')
        else:
            expected = 'region' if p['kind'] == 'neighborhood' else 'neighborhood'
            _require(parent is not None and parent['kind'] == expected, ident + ': invalid parent kind')
            _require(p['region_id'] == parent['region_id'], ident + ': inconsistent region')
    home = data.get('starting_home_id')
    _require(isinstance(home, str) and home in places and 'HOME' in places[home]['access'], 'starting_home_id must reference a home')
    _require(isinstance(data.get('edges'), list), 'edges required')
    access_targets = set()
    for e in data['edges']:
        _require(isinstance(e, dict), 'edge must be an object')
        ident = e.get('id')
        _require(isinstance(ident, str) and bool(ident) and ident not in edges, 'duplicate/invalid edge ID')
        _require(isinstance(e.get('from'), str) and isinstance(e.get('to'), str), ident + ': invalid endpoints')
        a, b = places.get(e['from']), places.get(e['to'])
        _require(a is not None and b is not None and a['id'] != b['id'], ident + ': invalid endpoints')
        _require(type(e.get('bidirectional')) is bool, ident + ': direction required')
        _require(e.get('access') in ('public', 'authorized', 'location'), ident + ': invalid access')
        _require(e.get('kind') in ('corridor', 'access'), ident + ': invalid kind')
        _require(all(isinstance(e.get(k), str) and bool(e[k]) for k in ('label', 'description')), ident + ': metadata required')
        modes = e.get('modes')
        _require(isinstance(modes, dict) and bool(modes) and
                 all(m in (*MODES, 'car', 'boat') and type(t) is int and 0 <= t <= 100 for m, t in modes.items()), ident + ': invalid modes/cost')
        if e['kind'] == 'access':
            _require(a['kind'] == 'neighborhood' and b['kind'] == 'poi' and b['parent_id'] == a['id'] and
                     b['id'] not in access_targets and modes == {'walk': 0} and e['bidirectional'] and
                     e['access'] == 'location', ident + ': invalid POI spur')
            access_targets.add(b['id'])
        else:
            _require(a['kind'] == b['kind'] == 'neighborhood' and all(t > 0 for t in modes.values()), ident + ': invalid corridor')
        edges[ident] = e
    _require(access_targets == {k for k, p in places.items() if p['kind'] == 'poi'}, 'every POI needs one access spur')
    return data


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'duplicate JSON key ' + key)
        result[key] = value
    return result


@lru_cache(maxsize=1)
def _catalog():
    try:
        data = validate(json.loads(ATLAS_PATH.read_text(encoding='utf-8'), object_pairs_hook=_unique))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('Cannot load required local atlas: ' + str(exc)) from exc
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()
    return data, digest


def load():
    """A detached catalog; callers cannot alter the pinned cached definitions."""
    return deepcopy(_catalog()[0])


def fingerprint():
    return _catalog()[1]
