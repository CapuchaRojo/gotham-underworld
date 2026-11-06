"""Versioned transport checkpoints; the nested engine save is unchanged."""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

import game_service
from career_state import validate as validate_world

VERSION = 1
COMMANDS = frozenset(('settle_in', 'wait', 'choose', 'pay_room', 'travel',
                      'enable_navigation', 'enable_mobility', 'journey',
                      'enable_ordinary', 'ordinary_choose'))
ID_PATTERN = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}')


class BridgeError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def decode_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result

    def constant(value):
        raise ValueError('non-finite number')

    def floating(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("non-finite number")
        return number

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant, parse_float=floating)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise BridgeError('MALFORMED_JSON', 'Expected finite JSON with unique keys.') from exc


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def identifier(value):
    return isinstance(value, str) and ID_PATTERN.fullmatch(value) is not None


def storage_paths(path):
    primary = Path(path).resolve()
    return {p.resolve() for p in (primary, Path(str(primary) + '.bak'), Path(str(primary) + '.lock'))}


def validate_request(request):
    keys = {'protocol_version', 'career_id', 'lineage_id', 'request_id',
            'expected_revision', 'command', 'arguments'}
    if type(request) is not dict or set(request) != keys:
        raise BridgeError('INVALID_REQUEST', 'Command envelope has incorrect fields.')
    if type(request['protocol_version']) is not int or request['protocol_version'] != VERSION:
        raise BridgeError('PROTOCOL_MISMATCH', 'Supported protocol version: 1.', 409)
    if not all(identifier(request[k]) for k in ('career_id', 'lineage_id', 'request_id')):
        raise BridgeError('INVALID_REQUEST', 'Invalid career, lineage or request identifier.')
    if type(request['expected_revision']) is not int or request['expected_revision'] < 0:
        raise BridgeError('INVALID_REQUEST', 'Revision must be a nonnegative integer.')
    command, args = request['command'], request['arguments']
    if not isinstance(command, str) or command not in COMMANDS:
        raise BridgeError('COMMAND_NOT_ALLOWED', 'Command is outside the C1 allowlist.')
    names = game_service.COMMANDS[command][1]
    if (type(args) is not dict or set(args) != set(names) or
            any(not isinstance(v, str) or len(v) > 256 for v in args.values())):
        raise BridgeError('INVALID_ARGUMENTS', 'Command requires its exact bounded string arguments.')
    return request


def receipt(request, revision, world):
    return dict(request_id=request['request_id'], revision=revision,
                command_sequence=world['command_sequence'], command=request['command'],
                day=world['day'], status='committed')


def _require(condition):
    if not condition:
        raise ValueError("invalid checkpoint contract")


def validate(checkpoint):
    """Read-only integrity checks, including receipt links to engine commands."""
    try:
        _require(type(checkpoint) is dict)
        _require(set(checkpoint) == {'bridge_version', 'career_id', 'lineage_id', 'revision',
                                    'base_sequence', 'world', 'world_hash', 'operations'})
        _require(type(checkpoint['bridge_version']) is int and checkpoint['bridge_version'] == VERSION)
        _require(identifier(checkpoint['career_id']) and identifier(checkpoint['lineage_id']))
        revision, base, world = checkpoint['revision'], checkpoint['base_sequence'], checkpoint['world']
        _require(type(revision) is int and revision >= 0)
        _require(type(base) is int and base >= 0)
        validate_world(world)
        _require(world['save_version'] == 1 and world['command_sequence'] == base + revision)
        _require(checkpoint['world_hash'] == digest(world))
        operations = checkpoint['operations']
        _require(type(operations) is list and len(operations) == revision)
        commands = {e['command_id']: e for e in world['events'] if e['kind'] == 'player_command'}
        owned = [e for e in world['events'] if e['kind'] == 'player_command' and e['command_id'] > base]
        _require([e['command_id'] for e in owned] == list(range(base + 1, base + revision + 1)))
        _require(all(e['actor'] == 'player' for e in owned))
        seen = set()
        for index, operation in enumerate(operations, 1):
            _require(type(operation) is dict and set(operation) == {'request', 'digest', 'receipt'})
            request = validate_request(operation['request'])
            _require(request['request_id'] not in seen)
            seen.add(request['request_id'])
            _require(request['career_id'] == checkpoint['career_id'])
            _require(request['lineage_id'] == checkpoint['lineage_id'])
            _require(request['expected_revision'] == index - 1)
            _require(operation['digest'] == digest(request))
            command = commands[base + index]
            _require(command['command'] == request['command'] and command['arguments'] == request['arguments'])
            cost = game_service.COMMANDS[request['command']][0]
            if type(cost) is int:
                _require(command['action_cost'] == cost)
            expected = dict(request_id=request['request_id'], revision=index,
                            command_sequence=base + index, command=request['command'],
                            day=command['day'], status='committed')
            _require(canonical(operation['receipt']) == canonical(expected))
        return checkpoint
    except (AssertionError, ValueError, KeyError, TypeError, OverflowError, RecursionError, BridgeError) as exc:
        raise BridgeError('INVALID_CHECKPOINT', 'Checkpoint is invalid or unsupported.', 503) from exc


class CareerLock:
    """OS-released advisory lock; never unlink a live lock-file inode."""
    def __init__(self, path):
        self.stream = Path(str(path) + '.lock').open('a+b')
        try:
            if os.name == 'nt':
                import msvcrt
                self.stream.seek(0, 2)
                if self.stream.tell() == 0:
                    self.stream.write(b'0')
                    self.stream.flush()
                self.stream.seek(0)
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.stream.close()
            raise BridgeError('CAREER_IN_USE', 'Another bridge owns this checkpoint.', 409) from exc

    def close(self):
        if not self.stream.closed:
            self.stream.close()


def _stage(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent, prefix='.' + path.name + '.',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return temporary
    except BaseException:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def _sync_directory(path):
    if os.name != 'nt':
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


class Store:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.lock = CareerLock(self.path)

    def read(self):
        try:
            return validate(decode_json(self.path.read_text(encoding='utf-8')))
        except (UnicodeError, BridgeError) as exc:
            raise BridgeError('INVALID_CHECKPOINT', 'Checkpoint is invalid or unsupported.', 503) from exc

    def write(self, checkpoint, *, create=False):
        validate(checkpoint)
        payload = canonical(checkpoint) + b'\n'
        temporary = backup_temporary = None
        try:
            temporary = _stage(self.path, payload)
            if create:
                os.link(temporary, self.path)  # Exclusive, including a competing late creation.
            else:
                previous = self.path.read_bytes()
                validate(decode_json(previous.decode('utf-8')))
                backup = Path(str(self.path) + '.bak')
                backup_temporary = _stage(backup, previous)
                os.replace(backup_temporary, backup)
                os.replace(temporary, self.path)
            _sync_directory(self.path.parent)
        finally:
            for path in (temporary, backup_temporary):
                if path is not None:
                    path.unlink(missing_ok=True)

    def close(self):
        self.lock.close()
