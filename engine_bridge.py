"""Single-writer, durable command broker. HTTP and future clients share this boundary."""
from copy import deepcopy
from pathlib import Path
import secrets
import threading

import game_service
import mobility
import navigation
from bridge_checkpoint import (BridgeError, COMMANDS, Store, VERSION, digest,
                               identifier, receipt, storage_paths, validate_request)
from bridge_projection import housing_view, operation_housing_settlements, player_view


class Bridge:
    def __init__(self, store, checkpoint):
        self._store, self._checkpoint = store, checkpoint
        self._mutex = threading.RLock()
        self._uncertain = False
        self._possible = set()
        self._closed = False

    @classmethod
    def _new(cls, path, world):
        store = Store(path)
        try:
            if store.path.exists():
                raise BridgeError('CHECKPOINT_EXISTS', 'Refusing to overwrite an existing checkpoint.', 409)
            checkpoint = dict(bridge_version=VERSION, career_id=secrets.token_hex(16),
                              lineage_id=secrets.token_hex(16), revision=0,
                              base_sequence=world['command_sequence'], world=world,
                              world_hash=digest(world), operations=[])
            store.write(checkpoint, create=True)
            return cls(store, checkpoint)
        except BaseException:
            store.close()
            raise

    @classmethod
    def create(cls, path, seed=42):
        return cls._new(path, game_service.create_career(seed))

    @classmethod
    def import_legacy(cls, source, path):
        if Path(source).resolve() in storage_paths(path):
            raise BridgeError('INVALID_PATH', 'Import source must be separate from checkpoint, backup and lock paths.')
        return cls._new(path, game_service.load_career(source))

    @classmethod
    def open(cls, path):
        store = Store(path)
        try:
            return cls(store, store.read())
        except BaseException:
            store.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        with self._mutex:
            self._closed = True
            self._store.close()

    def _ready(self):
        if self._closed:
            raise BridgeError('SESSION_CLOSED', 'Bridge session is closed.', 409)

    def _recover(self):
        self._ready()
        if not self._uncertain:
            return
        try:
            checkpoint = self._store.read()
            if digest(checkpoint) not in self._possible:
                raise ValueError('unexpected checkpoint')
        except (OSError, BridgeError, ValueError) as exc:
            raise BridgeError('OUTCOME_UNKNOWN', 'Checkpoint recovery is required; commands remain blocked.', 503) from exc
        self._checkpoint = checkpoint
        self._uncertain = False
        self._possible.clear()

    def _response(self, operation=None, duplicate=False):
        c = self._checkpoint
        return dict(protocol_version=VERSION, career_id=c['career_id'], lineage_id=c['lineage_id'],
                    revision=c['revision'], allowed_commands=sorted(COMMANDS),
                    receipt=deepcopy(operation['receipt']) if operation else None,
                    duplicate=duplicate, state=player_view(c['world']))

    def state(self):
        with self._mutex:
            self._recover()
            return self._response()

    def operation(self, request_id):
        if not identifier(request_id):
            raise BridgeError('INVALID_REQUEST', 'Invalid request identifier.')
        with self._mutex:
            self._recover()
            operation = next((o for o in self._checkpoint['operations']
                              if o['request']['request_id'] == request_id), None)
            result = self._response(operation)
            result['operation_status'] = 'committed' if operation else 'not_found'
            return result

    def housing(self):
        with self._mutex:
            self._recover()
            c = self._checkpoint
            return dict(protocol_version=VERSION, career_id=c['career_id'], lineage_id=c['lineage_id'],
                        revision=c['revision'], **housing_view(c['world']))

    def housing_operation(self, request_id):
        if not identifier(request_id):
            raise BridgeError('INVALID_REQUEST', 'Invalid request identifier.')
        with self._mutex:
            self._recover()
            c = self._checkpoint
            operation = next((o for o in c['operations'] if o['request']['request_id'] == request_id), None)
            if operation is None:
                raise BridgeError('NOT_FOUND', 'Unknown operation.', 404)
            committed = operation['receipt']
            return dict(protocol_version=VERSION, career_id=c['career_id'], lineage_id=c['lineage_id'],
                        revision=c['revision'], receipt=deepcopy(committed),
                        settlements=operation_housing_settlements(c['world'], committed))

    def execute(self, request):
        request = deepcopy(validate_request(request))
        with self._mutex:
            self._ready()
            if self._uncertain:
                raise BridgeError('OUTCOME_UNKNOWN', 'Recover state or operation before submitting another command.', 503)
            c = self._checkpoint
            if any(request[k] != c[k] for k in ('career_id', 'lineage_id')):
                raise BridgeError('WRONG_CAREER', 'Career or lineage does not match this session.', 409)
            previous = next((o for o in c['operations'] if o['request']['request_id'] == request['request_id']), None)
            if previous:
                if previous['digest'] != digest(request):
                    raise BridgeError('REQUEST_ID_REUSED', 'Request identity already belongs to a different payload.', 409)
                return self._response(previous, duplicate=True)
            if request['expected_revision'] != c['revision']:
                raise BridgeError('STALE_REVISION', 'Refresh player state before making a new decision.', 409)
            # Refuse external replacement/rewind instead of overwriting another lineage.
            if digest(self._store.read()) != digest(c):
                raise BridgeError('CHECKPOINT_CHANGED', 'Checkpoint changed outside this session; reopen it explicitly.', 409)
            candidate = deepcopy(c)
            try:
                game_service.execute_command(candidate['world'], request['command'], **request['arguments'])
            except ValueError as exc:
                raise BridgeError('COMMAND_REJECTED', 'Command is not currently eligible; refresh player state.', 422) from exc
            candidate['revision'] += 1
            candidate['world_hash'] = digest(candidate['world'])
            operation = dict(request=request, digest=digest(request),
                             receipt=receipt(request, candidate['revision'], candidate['world']))
            candidate['operations'].append(operation)
            # Construct the safe response before publication; projection errors cannot
            # leave a successfully saved action masquerading as a rejected command.
            response = dict(protocol_version=VERSION, career_id=candidate['career_id'],
                            lineage_id=candidate['lineage_id'], revision=candidate['revision'],
                            allowed_commands=sorted(COMMANDS), receipt=deepcopy(operation['receipt']),
                            duplicate=False, state=player_view(candidate['world']))
            try:
                self._store.write(candidate)
            except BaseException as exc:
                self._uncertain = True
                self._possible = {digest(c), digest(candidate)}
                if not isinstance(exc, Exception):
                    raise
                raise BridgeError('OUTCOME_UNKNOWN', 'Publication was not acknowledged; recover this operation before retrying.', 503) from exc
            self._checkpoint = candidate
            return response

    def route(self, destination, mode='auto'):
        if not all(isinstance(v, str) and len(v) <= 128 for v in (destination, mode)):
            raise BridgeError('INVALID_ARGUMENTS', 'Destination and mode must be bounded strings.')
        with self._mutex:
            self._recover()
            world = self._checkpoint['world']
            try:
                quote = navigation.plan_route(world, destination, mode)
            except ValueError as exc:
                raise BridgeError('ROUTE_UNAVAILABLE', 'No currently permitted quote; inspect your location and travel terms.', 422) from exc
            keys = ('origin', 'destination', 'mode', 'cost', 'fare', 'affordable', 'remaining_tu',
                    'return_cost', 'return_fare', 'return_fits_today', 'can_return_today', 'return_uncertain')
            result = {k: deepcopy(quote[k]) for k in keys if k in quote}
            active = mobility.active(world)
            result['command'] = 'journey' if active else 'travel'
            result['arguments'] = deepcopy(quote['arguments']) if active else dict(destination=quote['destination'], mode=mode)
            return dict(protocol_version=VERSION, career_id=self._checkpoint['career_id'],
                        lineage_id=self._checkpoint['lineage_id'], revision=self._checkpoint['revision'], quote=result)

    def export_legacy(self, path):
        """Local operator API only; exclusive export never rewrites a historical file."""
        with self._mutex:
            self._recover()
            if Path(path).resolve() in storage_paths(self._store.path):
                raise BridgeError('INVALID_PATH', 'Export requires a path outside checkpoint, backup and lock files.')
            return game_service.save_career(self._checkpoint['world'], path, overwrite=False)
