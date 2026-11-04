"""Explicit two-adapter dispatch; historical slots/events stay byte-compatible."""
from copy import deepcopy

import choice_engine
import incident_lifecycle as lifecycle
from simulation import event

NIGHT_SHIFT = 'goon.incident.night_shift.v1'
WRONG_NOTICE = 'goon.incident.wrong_notice.v1'


def bindings():
    import world_incidents
    import wrong_notice
    return {
        NIGHT_SHIFT: dict(version='incident_version', state='incidents', enabled='incident_enabled', adapter=world_incidents),
        WRONG_NOTICE: dict(version='notice_version', state='wrong_notice', enabled='notice_enabled', adapter=wrong_notice)}


def binding(definition_id):
    if definition_id not in bindings():
        raise ValueError('Unknown incident definition')
    return bindings()[definition_id]


def selected(world, incident_id):
    matches = [(ident, spec) for ident, spec in bindings().items()
               if spec['version'] in world and world.get(spec['state'], {}).get('id') == incident_id]
    if len(matches) != 1:
        raise ValueError('Unknown or ambiguous adopted incident')
    return matches[0]


def owns_command(command, definition_id, state):
    if command['command'] == 'enable_incidents':
        return definition_id == NIGHT_SHIFT
    if command['command'] == 'enable_incident':
        return command['arguments'].get('definition_id') == definition_id
    return command['command'] in ('discover_incident', 'incident_choose') and isinstance(state, dict) and command['arguments'].get('incident_id') == state.get('id')


def validate_ownership(world):
    """Reject unclaimed typed history; no adapter may silently ignore another ID."""
    specs = bindings()
    active = {ident: world.get(s['state']) for ident, s in specs.items() if s['version'] in world}
    ids = [s.get('id') for s in active.values() if isinstance(s, dict)]
    if len(ids) != len(set(ids)):
        raise ValueError('Invalid save: duplicate incident identity')
    for e in world['events']:
        kind = e['kind']
        if kind == 'player_command' and e['command'] in ('enable_incidents', 'enable_incident', 'discover_incident', 'incident_choose'):
            if sum(owns_command(e, ident, active.get(ident)) for ident in specs) != 1:
                raise ValueError('Invalid save: incident command has no registered owner')
        elif kind == 'incident_transition':
            if e.get('incident_id') not in ids:
                raise ValueError('Invalid save: transition has no adopted incident owner')
        elif kind.startswith(('incident_', 'notice_')) and kind not in {s['enabled'] for s in specs.values()}:
            raise ValueError('Invalid save: unsupported incident event kind')


def contacts(world):
    result = {}
    for ident, spec in sorted(bindings().items()):
        if spec['version'] not in world:
            continue
        data = spec['adapter'].load()
        definitions = data['contacts'] if 'contacts' in data else {data['contact_id']: data['contact']}
        for key, definition in definitions.items():
            if key in result and result[key] != definition:
                raise ValueError('Conflicting incident contact definitions')
            result[key] = definition
    return deepcopy(result)


def fact_definitions(world):
    result = {}
    for ident, spec in sorted(bindings().items()):
        if spec['version'] in world:
            data = spec['adapter'].load()
            for contact in data.get('contacts', {data.get('contact_id'): None}):
                result[contact] = set(spec['adapter'].FACT_DELTAS)
    return result


def enable(world, definition_id):
    spec = binding(definition_id)
    if spec['version'] in world:
        raise ValueError('Incident already adopted; no repeated enrollment')
    if definition_id == NIGHT_SHIFT:
        return spec['adapter'].enable_incidents(world)
    return spec['adapter'].enable(world)


def publish(world, definition_id, operation, arguments, ctx=None):
    import daily_life
    spec = binding(definition_id)
    state = world[spec['state']]
    start, before = len(state['receipts']), state['world_status']
    result = spec['adapter'].reduce(state, operation, world['day'], arguments, ctx)
    for receipt in state['receipts'][start:]:
        world['player']['cash'] += receipt['pay']
        contact = receipt.get('contact_id', spec['adapter'].load().get('contact_id'))
        daily_life._memory(world, contact, receipt['fact'], receipt['delta'], receipt['source_id'])
    event(world, 'incident_transition', result['message'], schema_version=1,
        transition_id=lifecycle.transition_id(state, operation, world['day'], arguments),
        incident_id=state['id'], source_id=state['source_id'], before=before, after=state['world_status'],
        effect_ids=[r['id'] for r in state['receipts'][start:]], operation=operation,
        arguments=deepcopy(arguments), context=deepcopy(ctx), command_id=ctx['command_id'] if ctx else None,
        result=deepcopy(result))
    return result


def begin_day(world):
    for ident, spec in sorted(bindings().items()):
        if spec['version'] not in world:
            continue
        state = world[spec['state']]
        if state['last_tick_day'] < world['day'] and not lifecycle.terminal(state):
            publish(world, ident, 'tick', {})


def discover(world, incident_id, channel):
    from world_incidents import context
    ident, _ = selected(world, incident_id)
    return publish(world, ident, 'discover', dict(incident_id=incident_id, channel=channel), context(world))


def choice_cost(world, incident_id, stage, option_id):
    from world_incidents import context
    _, spec = selected(world, incident_id)
    adapter, state = spec['adapter'], world[spec['state']]
    if stage not in state['stages']:
        raise ValueError('Unknown incident stage')
    return choice_engine.eligible(world, state['stages'][stage], adapter.load()['stages'][stage], option_id,
        lambda o: adapter._assess(state, stage, o, context(world)))['actions']


def choose(world, incident_id, stage, option_id):
    from world_incidents import context
    ident, _ = selected(world, incident_id)
    return publish(world, ident, 'choose', dict(incident_id=incident_id, stage=stage, option_id=option_id), context(world))


def report(world, incident_id=''):
    import world_incidents
    if incident_id:
        _, spec = selected(world, incident_id)
        return spec['adapter'].report(world)
    # Preserve old response shapes whenever the new incident is not adopted.
    if 'notice_version' not in world:
        return world_incidents.report(world)
    return dict(enabled=True, incidents=[spec['adapter'].report(world) for _, spec in sorted(bindings().items())
        if spec['version'] in world])


def definitions():
    return [dict(id=ident, title=spec['adapter'].load()['title']) for ident, spec in sorted(bindings().items())]


def private_receipts(world):
    """Visibility derives from validated causal receipts, not a saved UI flag."""
    state = world.get('wrong_notice')
    if state is None or state['review_received']:
        return []
    return [r for r in state['receipts'] if r['command_id'] is None]


def player_events(world, events):
    private = private_receipts(world)
    sources, effects = {r['source_id'] for r in private}, {r['id'] for r in private}
    result = []
    for e in events:
        if e['kind'] == 'life_memory' and e.get('source_id') in sources:
            continue
        row = deepcopy(e)
        if row['kind'] == 'incident_transition':
            row['effect_ids'] = [ident for ident in row['effect_ids'] if ident not in effects]
        result.append(row)
    return result


def contact_view(world, ident, person):
    hidden = {r['source_id'] for r in private_receipts(world) if r.get('contact_id') == ident}
    memories = [m for m in person['memories'] if m['source_id'] not in hidden]
    standing = memories[-1]['after'] if memories else 0
    return (standing if hidden else person['standing']), memories
