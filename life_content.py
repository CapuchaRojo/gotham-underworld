"""Small offline content pack; narrative and definitions are separate from rules."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

PATH = Path(__file__).parent / 'content' / 'neighborhood_life_v1.json'
EFFECTS = frozenset(('lawful_work', 'criminal_work', 'decline', 'make_promise',
                     'introduction', 'keep_promise', 'move_promise', 'break_promise', 'room_help'))


def _unique(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError('Invalid life content: duplicate key ' + key)
        data[key] = value
    return data


def validate(data):
    from location_registry import load as atlas
    def require(ok, message):
        if not ok:
            raise ValueError('Invalid life content: ' + message)
    require(isinstance(data, dict) and type(data.get('content_version')) is int and data['content_version'] == 1, 'unsupported version')
    places = {p['id']: p for p in atlas()['places']}
    require(isinstance(data.get('home_id'), str) and data['home_id'] in places and 'HOME' in places[data['home_id']]['access'], 'home required')
    require(isinstance(data.get('hub_id'), str) and data['hub_id'] in places and places[data['hub_id']]['kind'] == 'neighborhood', 'hub required')
    require(type(data.get('room_amount')) is int and data['room_amount'] == 30 and
            type(data.get('room_period')) is int and data['room_period'] == 7, 'unsupported room policy')
    contacts, choices = data.get('contacts'), data.get('choices')
    require(isinstance(contacts, dict) and bool(contacts), 'contacts required')
    require(set(contacts) == {'goon.contact.tess', 'goon.contact.cal'}, 'version-1 contact bindings required')
    for ident, person in contacts.items():
        require(isinstance(ident, str) and isinstance(person, dict) and all(isinstance(person.get(k), str) and person[k]
                for k in ('name', 'role', 'personality', 'need', 'knowledge')), 'invalid contact')
    require(isinstance(choices, dict) and bool(choices), 'choices required')
    require(set(choices) == {'opening_shift', 'promise', 'cal_intro', 'crossroads', 'midweek_shift',
                            'late_work', 'rescheduled_help', 'room_review'}, 'version-1 choice bindings required')
    for ident, choice in choices.items():
        require(isinstance(ident, str) and isinstance(choice, dict), 'invalid choice')
        require(isinstance(choice.get('speaker'), str) and choice['speaker'] in (*contacts, 'player') and all(isinstance(choice.get(k), str) and choice[k] for k in ('title', 'situation')), 'choice text/speaker required')
        require(type(choice.get('start')) is int and 0 <= choice['start'] < 7 and
                type(choice.get('duration')) is int and 1 <= choice['duration'] <= 7, 'invalid window')
        require(choice.get('slot') is None or isinstance(choice['slot'], str), 'invalid slot')
        options = choice.get('options')
        require(isinstance(options, list) and len(options) >= 2, 'distinct options required')
        seen = set()
        for option in options:
            require(isinstance(option, dict), 'option must be an object')
            key = option.get('id')
            require(isinstance(key, str) and bool(key) and key not in seen, 'unique option IDs required')
            seen.add(key)
            require(isinstance(option.get('effect'), str) and option['effect'] in EFFECTS and type(option.get('actions')) is int and 0 <= option['actions'] <= 3, 'unsupported effect/action cost')
            require(all(isinstance(option.get(k), str) and option[k] for k in ('label', 'tradeoff')), 'option text required')
            require(option.get('place') is None or (isinstance(option['place'], str) and (option['place'] == 'home' or option['place'] in places)), 'invalid option place')
            require(option.get('known') in (None, 'cal_terms', 'tess_reference', 'cal_quiet_work'), 'unsupported known fact')
            if 'minimum_standing' in option or 'standing_contact' in option:
                require(isinstance(option.get('standing_contact'), str) and option['standing_contact'] in contacts and
                        type(option.get('minimum_standing')) is int and -10 <= option['minimum_standing'] <= 10, 'invalid standing prerequisite')
            if option['effect'] == 'lawful_work':
                require(option['actions'] >= 1 and type(option.get('pay')) is int and 1 <= option['pay'] <= 25, 'invalid funded wage/action cost')
            if option['effect'] == 'criminal_work':
                require(option['actions'] >= 1 and option.get('job') in ('collection', 'courier'), 'unsupported legacy job/action cost')
    return data


@lru_cache(maxsize=1)
def _pack():
    try:
        data = validate(json.loads(PATH.read_text(encoding='utf-8'), object_pairs_hook=_unique))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('Cannot load required life content: ' + str(exc)) from exc
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return data, digest


def load():
    return deepcopy(_pack()[0])


def fingerprint():
    return _pack()[1]
