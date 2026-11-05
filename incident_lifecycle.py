"""Small shared incident lifecycle; explicit adapters own domain facts/effects."""
from copy import deepcopy
import choice_engine


def stages(ident, definition_id, windows):
    return {stage: dict(id=ident + '.' + stage, source_id=ident,
        definition_id=definition_id + '.' + stage, open_day=start, expires_day=end,
        state='open', selection=None) for stage, (start, end) in sorted(windows.items())}


def advance(state, day, occur, inform, resolve, process=None):
    if day <= state['last_tick_day']:
        raise ValueError('Incident day already processed or invalid')
    if terminal(state):
        raise ValueError('Incident lifecycle is already finished')
    if day >= state['occurrence_day'] and state['world_status'] == 'eligible':
        state['world_status'] = 'occurred'
        occur()
    if day >= state['information_day'] and state['world_status'] == 'occurred':
        state['world_status'] = 'evidence_available'
        inform()
    if process:
        process()
    if day >= state['resolution_day'] and state['world_status'] != 'resolved':
        state['world_status'] = 'resolved'
        resolve()
    for record in state['stages'].values():
        if record['state'] == 'open' and day >= record['expires_day']:
            record['state'] = 'expired'
    state['last_tick_day'] = day


def terminal(state):
    return state['world_status'] == 'resolved' and all(r['state'] != 'open' for r in state['stages'].values())


def receipt(state, stage, day, command_id, fact, delta, pay=0, contact_id=None):
    source = state['id'] + '.' + stage + ('.' + contact_id if contact_id else '')
    item = dict(id=source + '.effect', source_id=source, day=day,
        command_id=command_id, fact=fact, delta=delta, pay=pay)
    if contact_id:
        item['contact_id'] = contact_id
    state['receipts'].append(item)


def settle(record, option, day, context, outcome):
    record['state'] = 'resolved'
    record['selection'] = dict(option_id=option['id'], day=day,
        command_id=context['command_id'], action_cost=option['actions'], outcome=outcome)


def choices(world, state, definitions, assess):
    result = []
    for stage, definition in sorted(definitions.items()):
        row = choice_engine.present(world, state['stages'][stage], definition,
            lambda o, stage=stage: assess(stage, o))
        row['options'] = [o for o in row['options'] if o['availability'] == 'available']
        if row['options']:
            result.append(dict(stage=stage, **row))
    return deepcopy(result)


def transition_id(state, operation, day, arguments):
    suffix = str(day) if operation == 'tick' else arguments['stage'] if operation == 'choose' else 'notice'
    return f'{state["id"]}.{operation}.{suffix}'
