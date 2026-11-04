"""Replay validation for optional version-1 incident state and delegated effects."""
import json

from incident_content import fingerprint, load
from world_incidents import initial, reduce, transition_id

COMMANDS = {'enable_incidents', 'discover_incident', 'incident_choose'}


def _same(left, right):
    # JSON distinguishes bool from int, unlike Python dictionary equality.
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def replay(world):
    from career_state import _integer, _mapping, _require
    history = [e for e in world['events'] if e['kind'].startswith('incident_')]
    commands = {e['command_id']: e for e in world['events'] if e['kind'] == 'player_command' and e['command'] in COMMANDS}
    if 'incident_version' not in world:
        _require('incidents' not in world and not history and not commands, 'incident_version', 'is required with state/history')
        return None
    _integer(world['incident_version'], 'incident_version', 1, 1)
    _mapping(world.get('incidents'), 'incidents')
    _require('daily_life_version' in world and isinstance(world.get('daily_life'), dict), 'incidents', 'requires active daily life')
    _require(bool(history) and history[0]['kind'] == 'incident_enabled', 'incidents.history', 'requires initial explicit enrollment')
    first = history[0]
    _integer(first.get('schema_version'), 'incidents.schema_version', 1, 1)
    _integer(first.get('day'), 'incidents.enabled_day', world['daily_life']['activation_day'], world['day'])
    _integer(first.get('command_id'), 'incidents.command_id', 1)
    command = commands.get(first['command_id'])
    _require(command is not None and command['command'] == 'enable_incidents' and command['day'] == first['day'] and
             command['arguments'] == {} and type(command['action_cost']) is int and command['action_cost'] == 0,
             'incidents.enrollment', 'must reference one explicit zero-cost command')
    _require(first.get('content_fingerprint') == fingerprint(), 'incidents.content', 'requires pinned local definitions')
    state, used = initial(world['seed'], first['day']), {first['command_id']}
    previous_day = first['day']
    for item in history[1:]:
        _require(item['kind'] == 'incident_transition', 'incidents.history', 'has an unsupported or duplicate enrollment')
        _integer(item.get('schema_version'), 'incidents.schema_version', 1, 1)
        _integer(item.get('day'), 'incidents.day', previous_day, world['day'])
        previous_day = item['day']
        operation, arguments, ctx = item.get('operation'), item.get('arguments'), item.get('context')
        _mapping(arguments, 'incidents.arguments')
        if operation == 'tick':
            _require(item.get('command_id') is None, 'incidents.tick', 'cannot be a player decision')
            _require(any(e['kind'] == 'life_day' and e['day'] == item['day'] for e in world['events'][:world['events'].index(item)]),
                     'incidents.tick', 'must follow actual daily-life processing')
        else:
            _require(operation in ('discover', 'choose'), 'incidents.operation', 'is unsupported')
            _mapping(ctx, 'incidents.context')
            _require(set(ctx) == {'command_id', 'location', 'free', 'accessible', 'actions', 'tess_reference'}, 'incidents.context', 'has unsupported fields')
            _integer(ctx.get('command_id'), 'incidents.command_id', 1)
            _integer(ctx.get('actions'), 'incidents.actions', 0, 3)
            _require(all(type(ctx.get(k)) is bool for k in ('free', 'accessible', 'tess_reference')), 'incidents.context', 'flags must be boolean')
            _require(isinstance(ctx.get('location'), str), 'incidents.location', 'must be a location ID')
            names = ('incident_id', 'channel') if operation == 'discover' else ('incident_id', 'stage', 'option_id')
            _require(set(arguments) == set(names) and all(isinstance(arguments[k], str) for k in names), 'incidents.arguments', 'must match its operation')
            ident = ctx['command_id']
            _require(type(item.get('command_id')) is int and item['command_id'] == ident and ident not in used,
                     'incidents.command_id', 'must settle a unique command')
            command = commands.get(ident)
            expected_command = 'discover_incident' if operation == 'discover' else 'incident_choose'
            _require(command is not None and command['command'] == expected_command and command['day'] == item['day'] and
                     command['arguments'] == arguments, 'incidents.command', 'must match committed arguments/day')
            if operation == 'choose':
                from world_incidents import _assess
                import choice_engine
                stage = arguments['stage']
                _require(stage in state['stages'], 'incidents.stage', 'is unsupported')
                cost = choice_engine.eligible({'day': item['day']}, state['stages'][stage], load()['stages'][stage],
                    arguments['option_id'], lambda o: _assess(state, stage, o, ctx))['actions']
            else:
                cost = 0
            _require(type(command['action_cost']) is int and command['action_cost'] == cost, 'incidents.action_cost', 'must match the option')
            used.add(ident)
        try:
            before, start = state['world_status'], len(state['receipts'])
            result = reduce(state, operation, item['day'], arguments, ctx)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('Invalid save: incidents contains an invalid transition: ' + str(exc)) from exc
        _require(_same(item.get('result'), result) and item['message'] == result['message'], 'incidents.result', 'must match deterministic replay')
        expected = dict(transition_id=transition_id(state, operation, item['day'], arguments),
            incident_id=state['id'], source_id=state['source_id'], before=before,
            after=state['world_status'], effect_ids=[r['id'] for r in state['receipts'][start:]])
        _require(all(_same(item.get(k), v) for k, v in expected.items()),
                 'incidents.transition', 'must retain unique identity, source, phases and effect references')
    _require(used == set(commands), 'incidents.commands', 'must settle every incident command exactly once')
    _require(_same(world['incidents'], state), 'incidents.state', 'must match pinned deterministic history')
    return state


def memories(world):
    state = replay(world)
    if state is None:
        return {}
    contact = load()['contact_id']
    return {(contact, r['fact'], r['source_id']): r for r in state['receipts']}


def validate(world):
    from career_state import _require
    state = replay(world)
    if state is None:
        return
    life, contact = world['daily_life'], load()['contact_id']
    expected = {(r['fact'], r['source_id'], r['day']) for r in state['receipts']}
    actual = {(m['fact'], m['source_id'], m['day']) for m in life['contacts'][contact]['memories']}
    _require(actual == expected and len(actual) == len(life['contacts'][contact]['memories']), 'incidents.memories', 'must delegate every effect once')
    for receipt in state['receipts']:
        if receipt['pay']:
            transactions = [t for t in life['transactions'] if t['command_id'] == receipt['command_id']]
            _require(len(transactions) == 1 and transactions[0]['amount'] == receipt['pay'] and
                     transactions[0]['cause'] == 'existing_rules' and
                     transactions[0]['source_id'] == f'goon.command.{receipt["command_id"]}',
                     'incidents.payment', 'must match one actual cash-ledger receipt')
