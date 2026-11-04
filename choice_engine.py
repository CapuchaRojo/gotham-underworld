"""Deterministic contextual choices with injected assessment/effect adapters."""
from copy import deepcopy
from simulation import event


def present(world, record, definition, assess):
    """Assess only player-known prerequisites; hidden options have no public row."""
    rows = []
    for option in definition['options']:
        status, reason = assess(option)
        if status == 'hidden':
            continue
        if record['state'] != 'open':
            status, reason = 'unavailable', 'This opportunity is already closed'
        elif not record['open_day'] <= world['day'] < record['expires_day']:
            status, reason = 'unavailable', f'Available on days {record["open_day"]} through {record["expires_day"] - 1}'
        rows.append(dict(id=option['id'], label=option['label'], availability=status,
                         reason=reason, action_cost=option['actions'], tradeoff=option['tradeoff']))
    return deepcopy(dict(id=record['id'], source_id=record['source_id'],
        title=definition['title'], situation=definition['situation'], speaker=definition['speaker'],
        open_day=record['open_day'], expires_day=record['expires_day'], state=record['state'],
        selection=record['selection'], options=rows))


def eligible(world, record, definition, option_id, assess):
    report = present(world, record, definition, assess)
    row = next((o for o in report['options'] if o['id'] == option_id), None)
    if row is None:
        raise ValueError('Unknown or unavailable option')
    if row['availability'] != 'available':
        raise ValueError(row['reason'])
    return next(o for o in definition['options'] if o['id'] == option_id)


def resolve(world, record, definition, option_id, assess, apply):
    option = eligible(world, record, definition, option_id, assess)
    outcome = apply(option)
    record['state'] = 'resolved'
    record['selection'] = dict(option_id=option_id, day=world['day'],
        command_id=world['command_sequence'] + 1, action_cost=option['actions'], outcome=deepcopy(outcome))
    return event(world, 'life_choice', f'{option["label"]}: {outcome["feedback"]}',
        schema_version=1, choice_id=record['id'], source_id=record['source_id'],
        definition_id=record['definition_id'], **deepcopy(record['selection']), cause='player_choice')
