"""Pinned, offline M020 terms; no executable content or new NPC definitions."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path


@lru_cache(maxsize=1)
def _pack():
    data = json.loads((Path(__file__).parent/'content'/'ordinary_life_v1.json').read_text(encoding='utf-8'))
    expected = {'work': 2, 'negotiate': 1, 'decline': 0, 'withdraw': 0,
                'borrow': 1, 'decline_help': 0, 'repay': 1}
    if (type(data.get('content_version')) is not int or data['content_version'] != 1 or
            data.get('contact_id') != 'goon.contact.tess' or
            any(type(data.get(k)) is not int or data[k] != v for k,v in
                {'batch_pay':24,'regular_pay':28,'support_amount':20,'support_days':7}.items()) or
            set(data.get('options', {})) != set(expected)):
        raise ValueError('Unsupported ordinary-life content contract')
    for key,cost in expected.items():
        o = data['options'][key]
        if type(o.get('actions')) is not int or o['actions'] != cost or not all(
                isinstance(o.get(k), str) and o[k] for k in ('label','tradeoff')):
            raise ValueError('Invalid ordinary-life option')
    for k in ('batch_title','batch_situation'):
        if not isinstance(data.get(k),str) or not data[k]:
            raise ValueError('Invalid ordinary-life text')
    return data, hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def load():
    return deepcopy(_pack()[0])


def fingerprint():
    return _pack()[1]
