"""Replay validation for optional version-1 incident state and delegated effects."""
import json

from incident_lifecycle import transition_id

def _same(left, right):
    # JSON distinguishes bool from int, unlike Python dictionary equality.
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def _discovery_sources(world, state, item, position, enabled_kind='incident_enabled'):
    """Check a discovery snapshot against existing domain records, without I/O.

    Sources precede discovery by both append order and completed command ID.
    Domain validators still own travel paths, life choices, promises and deltas.
    Nothing here persists an alternative location or contact history.
    """
    from career_state import _integer, _mapping, _records, _require
    events, ctx = world['events'], item['context']
    discovery_id = item['command_id']
    path = 'incidents.discovery.provenance'
    receipts = [(i, e) for i, e in enumerate(events) if e['kind'] == 'player_command']
    commands = {e['command_id']: (i, e, receipts[n - 1][0] if n else -1,
                 receipts[n - 1][1]['command_id'] if n else 0)
                for n, (i, e) in enumerate(receipts)}

    def require(condition, message):
        _require(condition, path, message)

    def one(kind, key, value):
        matches = [(i, e) for i, e in enumerate(events) if e['kind'] == kind and e.get(key) == value]
        require(len(matches) == 1, 'requires one supporting ' + kind + ' event')
        return matches[0]

    def frame(index, event, command_id, expected):
        _integer(command_id, path + '.command_id', 1)
        require(command_id in commands, 'requires its committed source command')
        end, command, start, previous_id = commands[command_id]
        require(command['command'] == expected and command['actor'] == 'player' and
                start < index < end and previous_id < command_id and event['day'] == command['day'],
                'source must precede its own receipt inside the correct command frame')
        if command_id < discovery_id:
            require(end < position and event['day'] <= item['day'], 'source cannot follow discovery')
        elif command_id > discovery_id:
            require(index > commands[discovery_id][0], 'future source cannot precede discovery')
        return end, command

    frame(position, item, discovery_id, 'discover_incident')
    enabled_index, enabled = one(enabled_kind, 'kind', enabled_kind)
    enabled_command = commands[enabled['command_id']][1]['command']
    enabled_end, _ = frame(enabled_index, enabled, enabled['command_id'], enabled_command)
    require(enabled['command_id'] < discovery_id, 'enrollment must finish before discovery')
    require(state['world_status'] != 'eligible' and item['day'] >= state['occurrence_day'],
            'requires prior incident occurrence, not a snapshot claim')
    for tick_index, tick in enumerate(events[:position]):
        if tick['kind'] == 'incident_transition' and tick.get('operation') == 'tick' and tick.get('incident_id') == state['id']:
            day_index, _ = one('life_day', 'day', tick['day'])
            require(enabled_end < day_index < tick_index, 'occurrence must follow enrollment and daily processing')

    # Both journey schemas expose actual arrival and a committed command. Never
    # use a requested destination, later journey or current location as proof.
    location, last_command = None, 0
    for index, trip in enumerate(events):
        if trip['kind'] != 'travel':
            continue
        command_id = trip['command_id']
        if command_id >= discovery_id:
            require(index > position, 'a future arrival cannot support discovery')
            continue
        expected = 'journey' if trip['schema_version'] == 2 else 'travel'
        frame(index, trip, command_id, expected)
        require(command_id > last_command, 'movement sources must retain command order')
        location, last_command = trip['arrived'], command_id
    if location is None:
        activation_index, activation = one('navigation_activated', 'kind', 'navigation_activated')
        adoption_index, adoption = one('navigation_enabled', 'kind', 'navigation_enabled')
        source = next(((i, e) for i, e in receipts if i > adoption_index), None)
        require(source is not None, 'navigation origin has no completed adoption source')
        adoption_end, command = frame(adoption_index, adoption, source[1]['command_id'], 'enable_navigation')
        import navigation
        places, _ = navigation._definitions()
        anchor = navigation._resolve(command['arguments'].get('anchor'), dict(home_id=None, permissions=[]), places)
        require(adoption_end < activation_index < position and activation['day'] <= item['day'] and
                activation.get('location_id') == adoption.get('anchor_id') == anchor,
                'historical origin cannot be reconstructed from the saved current position')
        location = anchor
    require(ctx['location'] == location, 'location must match the last completed historical arrival/activation')

    life, reference = world['daily_life'], False
    person = life['contacts'].get('goon.contact.tess')
    _mapping(person, path + '.tess')
    for memory in _records(person.get('memories'), path + '.tess.memories'):
        if memory.get('fact') != 'promise_kept':
            continue
        source = memory.get('source_id')
        choice = life['choices'].get(source) if isinstance(source, str) else None
        require(isinstance(choice, dict) and isinstance(choice.get('selection'), dict), 'reference needs its resolving choice')
        selection = choice['selection']
        _integer(selection.get('command_id'), path + '.reference.command_id', 1)
        # A later real reference must not change earlier knowledge, even if both
        # interactions share a day. Its own life domain is validated separately.
        if selection['command_id'] >= discovery_id:
            continue
        memory_index, observed = one('life_memory', 'id', memory.get('id'))
        choice_index, chosen = one('life_choice', 'choice_id', source)
        require(observed.get('contact_id') == 'goon.contact.tess' and
                all(_same(observed.get(k), memory.get(k))
                    for k in ('id', 'day', 'fact', 'source_id', 'before', 'after', 'delta')) and
                selection['outcome'].get('effect') == 'keep_promise' and
                all(_same(chosen.get(k), v) for k, v in selection.items()),
                'reference must match its observed memory and selected keep_promise effect')
        resolution_end, command = frame(choice_index, chosen, selection['command_id'], 'choose')
        frame(memory_index, observed, selection['command_id'], 'choose')
        require(command['arguments'] == dict(choice_id=source, option_id=selection['option_id']), 'reference command arguments disagree')
        promises = [p for p in life['promises'].values() if p.get('status') == 'kept' and p.get('resolution_source') == source]
        require(len(promises) == 1, 'reference needs its unique kept promise')
        promise = promises[0]
        promise_index, kept = one('life_promise', 'promise_id', promise['id'])
        frame(promise_index, kept, selection['command_id'], 'choose')
        require(kept.get('status') == 'kept' and kept.get('source_id') == source, 'reference promise source disagrees')
        invitation = life['choices'][promise['source_id']]['selection']
        invitation_index, accepted = one('life_choice', 'choice_id', promise['source_id'])
        invitation_end, command = frame(invitation_index, accepted, invitation['command_id'], 'choose')
        require(invitation['outcome'].get('effect') == 'make_promise' and
                all(_same(accepted.get(k), v) for k, v in invitation.items()) and
                command['arguments'] == dict(choice_id=promise['source_id'], option_id=invitation['option_id']) and
                invitation['command_id'] < selection['command_id'] and
                invitation_end < memory_index < promise_index < choice_index < resolution_end < position,
                'accepted promise and kept-reference evidence must precede discovery in causal order')
        reference = True
    require(ctx['tess_reference'] is reference, 'Tess reference must match source-backed knowledge at discovery')


def replay(world, definition_id='goon.incident.night_shift.v1'):
    from career_state import _integer, _mapping, _require
    from incident_dispatch import binding, owns_command, validate_ownership
    validate_ownership(world)
    spec = binding(definition_id)
    adapter = spec['adapter']
    saved = world.get(spec['state'])
    ident = saved.get('id') if isinstance(saved, dict) else None
    history = [(i, e) for i, e in enumerate(world['events']) if e['kind'] == spec['enabled'] or
               (e['kind'] == 'incident_transition' and ident is not None and e.get('incident_id') == ident)]
    commands = {e['command_id']: e for e in world['events'] if e['kind'] == 'player_command' and owns_command(e, definition_id, saved)}
    if spec['version'] not in world:
        _require(spec['state'] not in world and not history and not commands, spec['version'], 'is required with state/history')
        return None
    _integer(world[spec['version']], spec['version'], 1, 1)
    _mapping(saved, spec['state'])
    _require('daily_life_version' in world and isinstance(world.get('daily_life'), dict), 'incidents', 'requires active daily life')
    _require(bool(history) and history[0][1]['kind'] == spec['enabled'], 'incidents.history', 'requires initial explicit enrollment')
    first = history[0][1]
    _integer(first.get('schema_version'), 'incidents.schema_version', 1, 1)
    _integer(first.get('day'), 'incidents.enabled_day', world['daily_life']['activation_day'], world['day'])
    _integer(first.get('command_id'), 'incidents.command_id', 1)
    command = commands.get(first['command_id'])
    legacy_enable = command is not None and definition_id == 'goon.incident.night_shift.v1' and command['command'] == 'enable_incidents'
    _require(command is not None and command['command'] == ('enable_incidents' if legacy_enable else 'enable_incident') and command['day'] == first['day'] and
             command['arguments'] == ({} if legacy_enable else dict(definition_id=definition_id)) and type(command['action_cost']) is int and command['action_cost'] == 0,
             'incidents.enrollment', 'must reference one explicit zero-cost command')
    _require(first.get('content_fingerprint') == adapter.fingerprint(), 'incidents.content', 'requires pinned local definitions')
    state, used = adapter.initial(world['seed'], first['day']), {first['command_id']}
    previous_day = first['day']
    for position, item in history[1:]:
        _require(item['kind'] == 'incident_transition', 'incidents.history', 'has an unsupported or duplicate enrollment')
        _integer(item.get('schema_version'), 'incidents.schema_version', 1, 1)
        _integer(item.get('day'), 'incidents.day', previous_day, world['day'])
        previous_day = item['day']
        operation, arguments, ctx = item.get('operation'), item.get('arguments'), item.get('context')
        _mapping(arguments, 'incidents.arguments')
        if operation == 'tick':
            _require(item.get('command_id') is None, 'incidents.tick', 'cannot be a player decision')
            _require(any(e['kind'] == 'life_day' and e['day'] == item['day'] for e in world['events'][:position]),
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
                import choice_engine
                stage = arguments['stage']
                _require(stage in state['stages'], 'incidents.stage', 'is unsupported')
                cost = choice_engine.eligible({'day': item['day']}, state['stages'][stage], adapter.load()['stages'][stage],
                    arguments['option_id'], lambda o: adapter._assess(state, stage, o, ctx))['actions']
            else:
                _discovery_sources(world, state, item, position, spec['enabled'])
                cost = 0
            _require(type(command['action_cost']) is int and command['action_cost'] == cost, 'incidents.action_cost', 'must match the option')
            used.add(ident)
        try:
            before, start = state['world_status'], len(state['receipts'])
            result = adapter.reduce(state, operation, item['day'], arguments, ctx)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('Invalid save: incidents contains an invalid transition: ' + str(exc)) from exc
        _require(_same(item.get('result'), result) and item['message'] == result['message'], 'incidents.result', 'must match deterministic replay')
        expected = dict(transition_id=transition_id(state, operation, item['day'], arguments),
            incident_id=state['id'], source_id=state['source_id'], before=before,
            after=state['world_status'], effect_ids=[r['id'] for r in state['receipts'][start:]])
        _require(all(_same(item.get(k), v) for k, v in expected.items()),
                 'incidents.transition', 'must retain unique identity, source, phases and effect references')
    _require(used == set(commands), 'incidents.commands', 'must settle every incident command exactly once')
    _require(_same(saved, state), 'incidents.state', 'must match pinned deterministic history')
    return state


def memories(world):
    from incident_dispatch import bindings
    result = {}
    for ident, spec in sorted(bindings().items()):
        state = replay(world, ident)
        if state is not None:
            default = spec['adapter'].load().get('contact_id')
            for receipt in state['receipts']:
                key = (receipt.get('contact_id', default), receipt['fact'], receipt['source_id'])
                if key in result:
                    raise ValueError('Duplicate delegated incident memory')
                result[key] = receipt
    return result


def validate(world):
    from career_state import _require
    from incident_dispatch import bindings
    for ident, spec in sorted(bindings().items()):
        state = replay(world, ident)
        if state is None:
            continue
        life, data = world['daily_life'], spec['adapter'].load()
        for contact in data.get('contacts', {data.get('contact_id'): None}):
            expected = {(r['fact'], r['source_id'], r['day']) for r in state['receipts'] if r.get('contact_id', data.get('contact_id')) == contact}
            actual = {(m['fact'], m['source_id'], m['day']) for m in life['contacts'][contact]['memories']}
            _require(actual == expected and len(actual) == len(life['contacts'][contact]['memories']), 'incidents.memories', 'must delegate every effect once')
        for receipt in state['receipts']:
            if receipt['pay']:
                transactions = [t for t in life['transactions'] if t['command_id'] == receipt['command_id']]
                _require(len(transactions) == 1 and transactions[0]['amount'] == receipt['pay'] and
                         transactions[0]['cause'] == 'existing_rules' and
                         transactions[0]['source_id'] == f'goon.command.{receipt["command_id"]}',
                         'incidents.payment', 'must match one actual cash-ledger receipt')
