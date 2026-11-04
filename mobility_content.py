"""Pinned additive station pilot. The historical atlas is never edited."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import location_registry

OVERLAY_PATH = Path(__file__).parent / 'content' / 'mobility_station_pilot_v1.json'
OVERLAY_ID = 'goon.mobility.overlay.station_pilot.v1'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def validate(data):
    def require(ok, reason):
        if not ok:
            raise ValueError('Invalid mobility overlay: ' + reason)
    require(isinstance(data, dict), 'expected object')
    require(data.get('overlay_id') == OVERLAY_ID, 'unsupported overlay_id')
    for key in ('overlay_version', 'rules_version', 'base_atlas_version'):
        require(type(data.get(key)) is int and data[key] == 1, 'unsupported ' + key)
    require(data.get('base_atlas_fingerprint') == location_registry.fingerprint(), 'requires pinned base atlas')
    base = location_registry.load()
    places = {p['id']: p for p in base['places']}
    edges = {e['id']: e for e in base['edges']}
    stations = data.get('stations')
    require(isinstance(stations, list) and len(stations) == 2, 'requires two stations')
    ids, anchors = set(), set()
    for station in stations:
        require(isinstance(station, dict), 'invalid station')
        for key in ('id', 'platform_id', 'gate_id'):
            ident = station.get(key)
            require(isinstance(ident, str) and ident.startswith('goon.mobility.') and ident not in ids
                    and ident not in places and ident not in edges, 'duplicate/invalid ' + key)
            ids.add(ident)
        anchor = station.get('place_id')
        require(isinstance(anchor, str) and anchor in places and anchor not in anchors, 'invalid station anchor')
        require(places[anchor]['kind'] == 'poi' and places[anchor]['access'] == ['PUB'], 'station must have public frontage')
        anchors.add(anchor)
    line = data.get('line')
    require(isinstance(line, dict), 'line required')
    for key in ('id', 'ride_id'):
        ident = line.get(key)
        require(isinstance(ident, str) and ident.startswith('goon.mobility.') and ident not in ids,
                'invalid line identity')
        ids.add(ident)
    require(isinstance(line.get('from_id'), str) and isinstance(line.get('to_id'), str)
            and {line['from_id'], line['to_id']} == anchors, 'line endpoints must be stations')
    for key in ('boarding_tu', 'fare', 'ride_tu'):
        require(type(line.get(key)) is int and 1 <= line[key] <= 18, 'invalid ' + key)
    segments = line.get('segments')
    require(isinstance(segments, list) and len(segments) == 4, 'requires four underlying segments')
    node, total, visited = places[line['from_id']]['parent_id'], 0, set()
    for segment in segments:
        require(isinstance(segment, dict), 'invalid segment')
        eid = segment.get('edge_id')
        require(isinstance(eid, str) and eid in edges and eid not in visited, 'invalid underlying edge')
        visited.add(eid)
        edge = edges[eid]
        target = edge['to'] if node == edge['from'] else edge['from'] if edge['bidirectional'] and node == edge['to'] else None
        require(edge['kind'] == 'corridor' and edge['access'] == 'public' and edge['bidirectional']
                and segment.get('from_id') == node and segment.get('to_id') == target
                and 'rail' in edge['modes'], 'noncontiguous/restricted underlying rail')
        node, total = target, total + edge['modes']['rail']
    require(node == places[line['to_id']]['parent_id'] and total == line['ride_tu'], 'ride endpoint/cost mismatch')
    return data


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('Invalid mobility overlay: duplicate JSON key ' + key)
        out[key] = value
    return out


@lru_cache(maxsize=1)
def _catalog():
    try:
        data = validate(json.loads(OVERLAY_PATH.read_text(encoding='utf-8'), object_pairs_hook=_unique))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('Cannot load required local mobility overlay: ' + str(exc)) from exc
    canonical = deepcopy(data)
    canonical['stations'].sort(key=lambda s: s['id'])
    return data, digest(canonical)


def load():
    return deepcopy(_catalog()[0])


def fingerprint():
    return _catalog()[1]
