"""Optional deterministic incidents: world truth, delivery, decisions and aftermath.

The reducer is pure apart from its supplied state. Only service/day adapters
publish it and delegate cash/contact effects to the existing M015 authorities.
"""
from copy import deepcopy
import hashlib

import choice_engine
from incident_content import fingerprint, load
from simulation import event
import incident_lifecycle as lifecycle
from incident_lifecycle import transition_id

VERSION = 1
FACT_DELTAS = {'inspection_complete': 2, 'inspection_partial': 0, 'inspection_failed': -1,
               'agreement_unfinished': -1, 'shop_secured': 2, 'statement_received': 1,
               'followup_completed': 1}


def initial(seed, day):
    content = load()
    source = f'{content["id"]}.enrollment.{day}'
    digest = hashlib.sha256(f'{seed}:{fingerprint()}:{source}'.encode()).digest()
    occurrence = day + 1 + digest[0] % 2
    ident = source + '.alarm'
    stages = lifecycle.stages(ident, content['id'], {stage:
        (occurrence + (5 if stage == 'followup' else 0 if stage == 'offer' else 1),
         occurrence + (8 if stage == 'followup' else 4)) for stage in content['stages']})
    return dict(rules_version=VERSION, content_fingerprint=fingerprint(), enabled_day=day,
        last_tick_day=day, id=ident, source_id=source, occurrence_day=occurrence,
        information_day=occurrence + 1, resolution_day=occurrence + 4,
        timing='overnight', world_status='eligible',
        truth=sorted(content['causes'])[digest[1] % len(content['causes'])],
        owner_facts=[], desk_facts=[], player_facts=[], discovery=None,
        stages=stages, receipts=[], aftermath=None, followup=None)


def _selection(state, stage):
    selected = state['stages'][stage]['selection']
    return selected['option_id'] if selected else None


def _receipt(state, stage, day, command_id, fact, pay=0):
    lifecycle.receipt(state, stage, day, command_id, fact, FACT_DELTAS[fact], pay)


def _assess(state, stage, option, context):
    content = load()
    if not state['discovery']:
        return 'hidden', None
    if stage == 'work' and _selection(state, 'offer') != 'accept':
        return 'hidden', None
    if stage == 'report' and not any(f in state['player_facts'] for f in ('cause_verified', 'limited_observations')):
        return 'hidden', None
    if stage == 'followup' and state['followup'] is None:
        return 'hidden', None
    if option['id'] not in ('refuse', 'withhold'):
        if not context['free'] or not context['accessible']:
            return 'unavailable', 'Requires lawful access while free; refuse, save or wait remain possible'
        if context['location'] != content['place']:
            return 'unavailable', f'Visit {content["place"]}; travel is separate'
    if context['actions'] < option['actions']:
        return 'unavailable', 'Insufficient daily actions; no additional allowance is granted'
    return 'available', None


def reduce(state, operation, day, arguments, context=None):
    """Apply one version-1 transition; no world, I/O, RNG or resource references."""
    content = load()
    if operation == 'tick':
        if arguments or context is not None:
            raise ValueError('Incident day already processed or invalid')
        def occur():
            state['owner_facts'] = ['alarm_observed']
        def inform():
            state['owner_facts'].append('cause_verified')
            state['desk_facts'].append('owner_alarm_report')
        def resolve():
            # The owner supplies her independent review, not magical police knowledge.
            state['desk_facts'].append('owner_review_received')
            offer, work = _selection(state, 'offer'), state['stages']['work']['selection']
            if offer == 'accept' and work is None:
                _receipt(state, 'unfinished', day, None, 'agreement_unfinished')
            outcome = work['outcome']['quality'] if work else None
            if _selection(state, 'report') == 'disclose':
                state['followup'] = 'statement_review'
            elif outcome == 'complete':
                state['followup'] = 'private_records_shift'
            elif offer == 'help':
                state['followup'] = 'safety_preparation_shift'
            state['aftermath'] = dict(resolved_day=day,
                shop_status='reopened_with_safety_help' if offer == 'help' else 'reopened_by_owner',
                disruption=state['truth'], player_outcome=(outcome or ('failed_commitment' if offer == 'accept' else offer) or
                    ('ignored_known' if state['discovery'] else 'missed_unknown')))
        lifecycle.advance(state, day, occur, inform, resolve)
        return dict(message='Independent incident processing completed.')

    if arguments.get('incident_id') != state['id']:
        raise ValueError('Unknown incident')
    if operation == 'discover':
        if state['world_status'] == 'eligible' or day < state['occurrence_day']:
            raise ValueError('No alarm report is available')
        if state['discovery'] is not None:
            raise ValueError('This incident was already discovered')
        channel = arguments['channel']
        public = channel == 'public_notice' and context['location'] == content['place']
        contact = channel == 'contact' and context['location'] == content['hub'] and context['tess_reference']
        if not context['free'] or not context['accessible'] or not (public or contact):
            raise ValueError('Read the shop notice locally, or ask Tess at the hub after earning her reference')
        state['discovery'] = dict(day=day, channel=channel, command_id=context['command_id'])
        state['player_facts'].append('alarm_reported')
        return dict(message='An overnight shop alarm was reported. The cause and any offender are unconfirmed.')

    if operation != 'choose':
        raise ValueError('Unknown incident operation')
    stage = arguments['stage']
    if stage not in state['stages']:
        raise ValueError('Unknown incident stage')
    record, definition = state['stages'][stage], content['stages'][stage]
    option = choice_engine.eligible({'day': day}, record, definition, arguments['option_id'],
        lambda o: _assess(state, stage, o, context))
    selected = option['id']
    outcome = dict(feedback='', quality=None, pay=0)
    if stage == 'offer':
        if selected == 'help':
            _receipt(state, stage, day, context['command_id'], 'shop_secured')
            outcome['feedback'] = 'The shop is secured lawfully. Ada records a safety-work reference; no immediate wage.'
        elif selected == 'accept':
            outcome['feedback'] = 'Inspection agreement accepted. Submit work before the disclosed deadline; pay depends on useful evidence.'
        else:
            outcome['feedback'] = 'Refused without a promise, debt or trust penalty. The owner will proceed independently.'
    elif stage == 'work':
        elapsed = day - state['information_day']
        quality = 'complete' if elapsed == 0 else 'partial' if elapsed == 1 else 'failed'
        pay = content['complete_pay'] if quality == 'complete' else content['partial_pay'] if quality == 'partial' else 0
        fact = {'complete': 'inspection_complete', 'partial': 'inspection_partial', 'failed': 'inspection_failed'}[quality]
        _receipt(state, stage, day, context['command_id'], fact, pay)
        if quality == 'complete':
            state['player_facts'].append('cause_verified')
            finding = content['causes'][state['truth']]
        elif quality == 'partial':
            state['player_facts'].append('limited_observations')
            finding = 'Only the alarm activation could be corroborated; the cause remains unconfirmed.'
        else:
            finding = 'The useful inspection evidence is gone. No cause or offender can be established from your work.'
        outcome.update(quality=quality, pay=pay, feedback=f'{finding} Delivered to Ada; earned ${pay}.')
    elif stage == 'report':
        if selected == 'disclose':
            fact = 'player_cause_statement' if 'cause_verified' in state['player_facts'] else 'player_limited_statement'
            state['desk_facts'].append(fact)
            _receipt(state, stage, day, context['command_id'], 'statement_received')
            outcome['feedback'] = 'The Civic Police incident desk received only your observations and acknowledged receipt to Ada. No player case or charge was created.'
        else:
            outcome['feedback'] = 'The optional statement was lawfully withheld. No automatic police knowledge, guilt or legal penalty.'
    else:
        pay = content['followup_pay']
        _receipt(state, stage, day, context['command_id'], 'followup_completed', pay)
        outcome.update(pay=pay, feedback=f'Completed {state["followup"].replace("_", " ")}; earned ${pay} once.')
    lifecycle.settle(record, option, day, context, outcome)
    return dict(message=outcome['feedback'], stage=stage, **deepcopy(outcome))


def context(world):
    from game_service import actions_remaining
    import navigation
    nav = navigation._active(world)
    places, _ = navigation._definitions()
    tess = world['daily_life']['contacts']['goon.contact.tess']
    return dict(location=nav['location_id'], free=not world['player']['arrested'],
        accessible=navigation._allowed(places[nav['location_id']], nav),
        actions=actions_remaining(world), command_id=world['command_sequence'] + 1,
        tess_reference=any(m['fact'] == 'promise_kept' for m in tess['memories']))


def enable_incidents(world):
    import daily_life
    if 'incident_version' in world:
        raise ValueError('Incidents are already enabled; there is no re-enrollment or repeat reward')
    life = daily_life._state(world)
    if world['player']['arrested']:
        raise ValueError('Cannot enroll while detained')
    world['incident_version'] = VERSION
    world['incidents'] = initial(world['seed'], world['day'])
    life['contacts'][load()['contact_id']] = dict(standing=0, memories=[])
    return event(world, 'incident_enabled', 'Enabled one optional neighborhood incident; no clock or budget refresh.',
        schema_version=VERSION, command_id=world['command_sequence'] + 1, content_fingerprint=fingerprint())


def _state(world):
    if 'incident_version' not in world:
        raise ValueError('Incidents are not enabled; inspect incidents and explicitly enable_incidents after settle_in activates')
    return world['incidents']


def _publish(world, operation, arguments, ctx=None):
    from incident_dispatch import publish, NIGHT_SHIFT
    return publish(world, NIGHT_SHIFT, operation, arguments, ctx)


def begin_day(world):
    from incident_dispatch import begin_day as dispatch_day
    dispatch_day(world)


def discover_incident(world, incident_id, channel):
    return _publish(world, 'discover', dict(incident_id=incident_id, channel=channel), context(world))


def choice_cost(world, incident_id, stage, option_id):
    state = _state(world)
    if incident_id != state['id'] or stage not in state['stages']:
        raise ValueError('Unknown incident or stage')
    option = choice_engine.eligible(world, state['stages'][stage], load()['stages'][stage], option_id,
        lambda o: _assess(state, stage, o, context(world)))
    return option['actions']


def choose(world, incident_id, stage, option_id):
    return _publish(world, 'choose', dict(incident_id=incident_id, stage=stage, option_id=option_id), context(world))


def report(world):
    """Player knowledge projection only; never adopts, discovers or propagates."""
    if 'incident_version' not in world:
        return dict(enabled=False, terms='Optional one-shot overnight shop alarm. Requires active daily life; enable_incidents explicitly. No new clock, costs or allowance.')
    state, content = world['incidents'], load()
    ctx = context(world)
    available = []
    if not state['discovery'] and world['day'] >= state['occurrence_day'] and state['world_status'] != 'eligible' and ctx['free'] and ctx['accessible']:
        if ctx['location'] == content['place']:
            available.append('public_notice')
        if ctx['location'] == content['hub'] and ctx['tess_reference']:
            available.append('contact')
    result = dict(enabled=True, id=state['id'], discovery_channels=available,
        known=state['discovery'] is not None, journal=None, choices=[])
    if state['discovery'] is not None:
        result['journal'] = dict(title=content['title'], timing='overnight',
            notice='An overnight alarm was reported; no offender is identified.',
            information_day=state['information_day'], deadline=state['resolution_day'],
            discovered=deepcopy(state['discovery']), facts=deepcopy(state['player_facts']),
            finding=content['causes'][state['truth']] if 'cause_verified' in state['player_facts'] else None,
            shop_status=state['aftermath']['shop_status'] if state['aftermath'] else None,
            followup=state['followup'] if state['aftermath'] else None)
        result['choices'] = lifecycle.choices(world, state, content['stages'],
            lambda stage, o: _assess(state, stage, o, ctx))
    return deepcopy(result)
