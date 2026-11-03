"""M004 deterministic, explainable NPC relationship decisions."""

METRICS = ('trust', 'respect', 'fear', 'hostility', 'suspicion')


def prepare(world):
    """Initialize legacy worlds without changing historical NPC memories."""
    for person in world['people'].values():
        person.setdefault('relationship', {metric: 0 for metric in METRICS})
        for metric in METRICS:
            person['relationship'].setdefault(metric, 0)
        person.setdefault('relationship_history', [])
    return world


def change(world, name, deltas, cause, source_attempt=None, case_id=None):
    """Apply bounded changes and store a traceable reason."""
    prepare(world)
    person = world['people'][name]
    applied = {}
    for metric, amount in deltas.items():
        if metric not in METRICS:
            raise ValueError(f'Unknown relationship metric: {metric}')
        old = person['relationship'][metric]
        new = max(-100, min(100, old + amount))
        person['relationship'][metric] = new
        applied[metric] = new - old
    entry = {'day': world['day'], 'cause': cause, 'changes': applied}
    if source_attempt is not None:
        entry['source_attempt'] = source_attempt
    if case_id is not None:
        entry['case_id'] = case_id
    person['relationship_history'].append(entry)
    return entry


def on_join(world, faction):
    for name, person in world['people'].items():
        if person['faction'] == faction:
            change(world, name, {'trust': 5, 'respect': 2}, 'recruitment')


def on_job(world, faction, kind, success, attempt, rival=None):
    for name, person in world['people'].items():
        if person['faction'] == faction:
            change(world, name, {'trust': 3 if success else -5,
                                 'respect': 2 if success else -3},
                   'job_success' if success else 'job_failure', source_attempt=attempt)
        elif not success and kind == 'collection' and person['faction'] == rival:
            change(world, name, {'hostility': 5}, 'rival_retaliation', source_attempt=attempt)


def on_investigation(world, case):
    if 'Detective Vale' in world['people']:
        change(world, 'Detective Vale', {'suspicion': 8},
               'evidence_recovered', source_attempt=case.get('source_attempt'), case_id=case['id'])


def decision(world, name):
    """A small deterministic policy; no NPC omniscience or random draws."""
    prepare(world)
    if name not in world['people']:
        raise ValueError('Unknown NPC')
    r = world['people'][name]['relationship']
    if name == 'Detective Vale':
        action = 'prioritize_investigation' if r['suspicion'] >= 16 else 'monitor'
        reason = f'suspicion={r["suspicion"]} (threshold 16)'
    elif r['hostility'] >= 5:
        action = 'refuse_cooperation'
        reason = f'hostility={r["hostility"]} (threshold 5)'
    elif r['trust'] >= 10:
        action = 'offer_support'
        reason = f'trust={r["trust"]} (threshold 10)'
    else:
        action = 'neutral'
        reason = f'trust={r["trust"]}, hostility={r["hostility"]}'
    return {'npc': name, 'action': action, 'reason': reason}
