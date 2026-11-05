"""Bounded source-backed civilian service and police intake, with no legal effects."""
from copy import deepcopy
import hashlib
import json

from institution_content import load, fingerprint
from institution_sources import catalogue
from simulation import event

COMMANDS = {'enable_institutions': (0, ()),
    'institution_submit': (1, ('institution_id','source_id')),
    'institution_correct': (1, ('institution_id','report_id','source_id')),
    'institution_followup': (1, ('institution_id','incident_id')),
    'institution_withhold': (0, ('institution_id','incident_id'))}
RANK = {'printed': 0, 'limited': 1, 'documented': 2}


def initial(day, command_id):
    return dict(rules_version=1, content_fingerprint=fingerprint(), enabled_day=day,
        enabled_command=command_id, last_process_day=day, reports={}, matters={},
        credibility={ident: 'unestablished' for ident in sorted(load()['actors'])},
        receipts=[], withheld=[])


def context(world):
    import daily_life
    daily_life._state(world)
    from world_incidents import context as incident_context
    return {k: v for k,v in incident_context(world).items() if k != 'tess_reference'}


def _actor(ident):
    actor = load()['actors'].get(ident)
    if actor is None:
        raise ValueError('Unknown institutional recipient')
    return actor


def matter_id(actor, incident):
    return actor + '.matter.' + incident


def report_id(actor, source, sender):
    return actor + '.report.' + source + '.' + sender


def _known_matter(sources, incident):
    return any(s['incident_id'] == incident for s in sources.player.values())


def _counter(actor, ctx, cost):
    if not ctx['free'] or not ctx['accessible'] or ctx['location'] != actor['place']:
        raise ValueError('Visit the lawful public counter at ' + actor['place'] + ' while free')
    if ctx['actions'] < cost:
        raise ValueError('Insufficient shared daily actions')


def _received(state, actor, source, day, sender, route, correction=None):
    ident = report_id(actor, source['id'], sender)
    if correction:
        ident += '.correction.' + hashlib.sha256(correction.encode()).hexdigest()[:16]
    if ident in state['reports']:
        raise ValueError('This source has already been submitted to this recipient')
    record = dict(id=ident, institution_id=actor, incident_id=source['incident_id'],
        source_id=source['id'], origin_event=source['origin_event'], observed_day=source['observed_day'],
        learned_command=source['learned_command'] if sender == 'player' else None,
        sender=sender, observer=source['observer'], route=route, received_day=day,
        topic=source['topic'], value=source['value'], credibility=source['credibility'],
        limitation=source['limitation'], correction_of=correction,
        due_day=day + _actor(actor)['delay'], processed_day=None)
    state['reports'][ident] = record
    key = matter_id(actor, source['incident_id'])
    if key not in state['matters']:
        state['matters'][key] = dict(id=key, institution_id=actor, incident_id=source['incident_id'],
            report_ids=[], version=0, status='queued', beliefs={}, contradictions=[],
            clarification_until=None, classification='unprocessed', assistance_issued=False)
    case = state['matters'][key]
    case['report_ids'].append(ident)
    case['version'] += 1
    return record


def _beliefs(records):
    beliefs, contradictions, unresolved = {}, [], False
    for topic in sorted({r['topic'] for r in records}):
        rows = [r for r in records if r['topic'] == topic]
        documented = [r for r in rows if RANK[r['credibility']] == 2]
        decisive = documented or rows
        values = {json.dumps(r['value'], sort_keys=True) for r in decisive}
        all_values = {json.dumps(r['value'], sort_keys=True) for r in rows}
        certain = bool(documented) and len(values) == 1
        if len(values) == 1:
            beliefs[topic] = dict(value=deepcopy(decisive[0]['value']),
                confidence='documented' if certain else 'unconfirmed',
                report_ids=sorted(r['id'] for r in decisive))
        else:
            unresolved = True
        if len(all_values) > 1:
            contradictions.append(dict(topic=topic, report_ids=sorted(r['id'] for r in rows),
                resolved_by=sorted(r['id'] for r in documented) if certain else []))
    # A documented cause can coexist with an explicitly unconfirmed alarm
    # report; receipt of one does not authenticate every other topic.
    return beliefs, contradictions, unresolved or not any(RANK[r['credibility']]==2 for r in records)


def _profile(state, actor):
    rows = [r for r in state['reports'].values() if r['institution_id'] == actor and r['processed_day'] is not None]
    for r in rows:
        if r['sender'] != 'player' or RANK[r['credibility']] == 2:
            continue
        conflicting = any(x['incident_id'] == r['incident_id'] and x['topic'] == r['topic'] and
            RANK[x['credibility']] == 2 and x['value'] != r['value'] for x in rows)
        repaired = any(x['sender'] == 'player' and x['correction_of'] == r['id'] for x in rows)
        if conflicting and not repaired:
            return 'needs_documentation'
    return 'documented' if any(r['sender'] == 'player' and RANK[r['credibility']] == 2 for r in rows) else 'unestablished'


def needs_processing(state, day):
    return state['last_process_day'] < day and (any(r['processed_day'] is None and r['due_day'] <= day
        for r in state['reports'].values()) or any(c['status'] == 'clarification_requested' and
        c['clarification_until'] <= day for c in state['matters'].values()))


def next_delivery(state, sources, day, enabled_position):
    for (actor, key), delivery in sorted(sources.automatic.items(), key=lambda pair:
            (pair[1]['available_day'], pair[0])):
        source = delivery['source']
        if source['position'] > enabled_position and delivery['available_day'] <= day and (
                report_id(actor, key, 'npc') not in state['reports']):
            return dict(institution_id=actor, source_id=key)
    return None


def reduce(state, operation, day, arguments, sources, ctx=None):
    if operation == 'receive':
        actor, key = arguments['institution_id'], arguments['source_id']
        delivery = sources.automatic[(actor,key)]
        if delivery['available_day'] > day:
            raise ValueError('Source transmission has not arrived')
        _received(state, actor, delivery['source'], day, 'npc', delivery['route'])
        return dict(message='A bounded institutional transmission was received.')
    if operation == 'process':
        if arguments or ctx is not None or not needs_processing(state, day):
            raise ValueError('No due institutional work, or day already processed')
        changed = set()
        for ident, record in sorted(state['reports'].items()):
            if record['processed_day'] is None and record['due_day'] <= day:
                record['processed_day'] = day
                changed.add(matter_id(record['institution_id'],record['incident_id']))
        for key, case in sorted(state['matters'].items()):
            if key not in changed and not (case['status'] == 'clarification_requested' and case['clarification_until'] <= day):
                continue
            rows = [state['reports'][r] for r in sorted(case['report_ids']) if state['reports'][r]['processed_day'] is not None]
            beliefs, contradictions, unresolved = _beliefs(rows)
            case.update(beliefs=beliefs, contradictions=contradictions)
            if unresolved:
                if case['clarification_until'] is None:
                    case['clarification_until'] = day + load()['clarification_days']
                case['status'] = 'closed_insufficient' if day >= case['clarification_until'] else 'clarification_requested'
            else:
                case['status'] = 'documented'
            actor = _actor(case['institution_id'])
            case['classification'] = ('administrative_notice' if 'delivery_day' in beliefs else 'local_safety') if actor['kind'] == 'civilian' else (
                'observations_logged' if case['status'] == 'documented' else 'unverified_incident')
            case['version'] += 1
        for actor in sorted(state['credibility']):
            state['credibility'][actor] = _profile(state, actor)
        state['last_process_day'] = day
        return dict(message='Due institutional records were processed; no legal finding or automatic player notification.')

    actor_id = arguments['institution_id']
    actor = _actor(actor_id)
    if operation != 'withhold':
        _counter(actor, ctx, 1)
    if operation in ('submit','correct'):
        source = sources.player.get(arguments['source_id'])
        if source is None or source['topic'] not in actor['topics']:
            raise ValueError('No supported observed source for this recipient')
        correction = arguments.get('report_id')
        if operation == 'correct':
            target = state['reports'].get(correction)
            known = any(r['institution_id'] == actor_id and correction in r['report_ids'] for r in state['receipts'])
            if target is None or target['institution_id'] != actor_id or (
                    target['sender'] != 'player' and not known):
                raise ValueError('Correction requires a known report at the same recipient')
            if (target['incident_id'],target['topic']) != (source['incident_id'],source['topic']) or RANK[source['credibility']] != 2:
                raise ValueError('Correction needs a documented source for the same incident and topic')
            if target['correction_of'] is not None or RANK[target['credibility']]==2 or target['value']==source['value']:
                raise ValueError('Correct only an unsupported conflicting original claim; no correction chains')
            if any(r['sender'] == 'player' and r['correction_of'] == correction for r in state['reports'].values()):
                raise ValueError('This report already has your correction')
        elif state['credibility'][actor_id] == 'needs_documentation' and RANK[source['credibility']] < 2:
            raise ValueError('This desk requires documentary support; provide a verified correction to restore access')
        record = _received(state,actor_id,source,day,'player','counter_correction' if correction else 'counter_submission',correction)
        return dict(message='Received your supported source; processing is delayed, acknowledgment is not endorsement.',
            report_id=record['id'], due_day=record['due_day'], claim=dict(topic=record['topic'],value=record['value'],credibility=record['credibility']))

    incident = arguments['incident_id']
    if not _known_matter(sources, incident):
        raise ValueError('No source-backed player knowledge of this incident')
    key = matter_id(actor_id, incident)
    if operation == 'withhold':
        if key in state['withheld']:
            raise ValueError('Withholding already recorded; no repeated effect')
        state['withheld'].append(key)
        return dict(message='You withheld further involvement. The desk was not told of this private decision; no penalty or promise.')
    if operation != 'followup' or key not in state['matters']:
        raise ValueError('No received matter to follow up')
    case = state['matters'][key]
    if any(r['matter_id'] == key and r['version'] == case['version'] for r in state['receipts']):
        raise ValueError('You already received this response; no repeat follow-up action')
    assistance = None
    if actor['kind'] == 'civilian' and 'delivery_day' in case['beliefs'] and case['status'] == 'documented' and not case['assistance_issued']:
        case['assistance_issued'] = True
        assistance = 'dated_correction_copy'
    receipt = dict(id=key+'.response.'+str(case['version']), matter_id=key,
        institution_id=actor_id, incident_id=incident, day=day, command_id=ctx['command_id'],
        version=case['version'], status=case['status'], beliefs=deepcopy(case['beliefs']),
        contradictions=deepcopy(case['contradictions']), classification=case['classification'],
        credibility=state['credibility'][actor_id], assistance=assistance,
        report_ids=sorted(case['report_ids']), reports=[deepcopy(state['reports'][r]) for r in sorted(case['report_ids'])])
    state['receipts'].append(receipt)
    return dict(message='The desk delivered its current record, not a finding of guilt. No wage or allowance refresh.', response=deepcopy(receipt))


def _state(world):
    if 'institution_version' not in world:
        raise ValueError('Institutions are not enabled; explicitly enable_institutions after daily life activates')
    return world['institutions']


def enable(world):
    import daily_life
    daily_life._state(world)
    ctx = context(world)
    if 'institution_version' in world or not ctx['free']:
        raise ValueError('Institutions already adopted or unavailable while detained')
    world['institution_version'] = 1
    world['institutions'] = initial(world['day'],ctx['command_id'])
    return event(world,'institution_enabled','Enabled bounded institutional intake; no retroactive reports or budget refresh.',
        schema_version=1, command_id=ctx['command_id'], context=ctx, content_fingerprint=fingerprint())


def _publish(world, operation, arguments, sources, ctx=None):
    result = reduce(_state(world),operation,world['day'],arguments,sources,ctx)
    suffix = 'command.'+str(ctx['command_id']) if ctx else ('process.'+str(world['day']) if operation=='process' else
        'receive.'+report_id(arguments['institution_id'],arguments['source_id'],'npc'))
    event(world,'institution_transition',result['message'],schema_version=1,
        transition_id='goon.institutions.'+suffix,operation=operation,arguments=deepcopy(arguments),
        context=deepcopy(ctx),command_id=ctx['command_id'] if ctx else None,result=deepcopy(result))
    return result


def synchronize(world):
    if 'institution_version' not in world:
        return
    state, sources = _state(world), catalogue(world)
    enabled_position = next(i for i,e in enumerate(world['events']) if e['kind']=='institution_enabled')
    while True:
        arguments = next_delivery(state,sources,world['day'],enabled_position)
        if arguments is None:
            break
        _publish(world,'receive',arguments,sources)
    if needs_processing(state,world['day']):
        _publish(world,'process',{},sources)


def submit(world,institution_id,source_id):
    return _publish(world,'submit',dict(institution_id=institution_id,source_id=source_id),catalogue(world),context(world))


def correct(world,institution_id,report_id,source_id):
    return _publish(world,'correct',dict(institution_id=institution_id,report_id=report_id,source_id=source_id),catalogue(world),context(world))


def followup(world,institution_id,incident_id):
    return _publish(world,'followup',dict(institution_id=institution_id,incident_id=incident_id),catalogue(world),context(world))


def withhold(world,institution_id,incident_id):
    return _publish(world,'withhold',dict(institution_id=institution_id,incident_id=incident_id),catalogue(world),context(world))


def report(world,institution_id=''):
    definitions = load()['actors']
    if institution_id:
        definitions = {institution_id: _actor(institution_id)}
    result = dict(enabled='institution_version' in world, actors=[])
    if not result['enabled']:
        return dict(result,terms='Explicit enable_institutions after active daily life. Submissions, corrections and new local follow-ups cost one action; withholding is free. No automatic money or legal effects.',definitions=definitions)
    state, sources, ctx = _state(world), catalogue(world), context(world)
    for ident, actor in sorted(definitions.items()):
        receipts = [r for r in state['receipts'] if r['institution_id']==ident]
        own = [r for r in state['reports'].values() if r['sender']=='player' and r['institution_id']==ident]
        # Only receipt-time information is remotely visible. Private processing
        # and other senders' reports appear after an actual local follow-up.
        own_view = [{k:deepcopy(v) for k,v in r.items() if k!='processed_day'} for r in sorted(own,key=lambda r:r['id'])]
        options = []
        for key,source in sorted(sources.player.items()):
            if source['topic'] not in actor['topics']:
                continue
            args = dict(institution_id=ident,source_id=key)
            try:
                reduce(deepcopy(state),'submit',world['day'],args,sources,ctx)
                available, reason = True, None
            except ValueError as exc:
                available, reason = False, str(exc)
            options.append(dict(source_id=key,incident_id=source['incident_id'],topic=source['topic'],value=source['value'],
                credibility=source['credibility'],limitation=source['limitation'],actions=1,available=available,reason=reason))
        result['actors'].append(dict(id=ident,**actor,known_credibility=receipts[-1]['credibility'] if receipts else 'unestablished',
            submissions=own_view,responses=deepcopy(receipts),sources=options,
            withheld=[key for key in state['withheld'] if key.startswith(ident+'.matter.')]))
    return deepcopy(result)
