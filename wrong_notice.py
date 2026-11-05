"""Wrong Notice adapter: contradictory sources, targeted transmission and repair."""
from copy import deepcopy
import hashlib

import choice_engine
import incident_lifecycle as lifecycle
from notice_content import load, fingerprint
from simulation import event

VERSION = 1
CLERK = 'goon.contact.notice_clerk'
NEIGHBOR = 'goon.contact.notice_neighbor'
FACT_DELTAS = {'notice_ledger_checked': 0, 'notice_source_heard': 0,
    'notice_desk_notified': 1, 'notice_warning_received': 1, 'notice_retracted': 0,
    'notice_priority_claimed': -1, 'notice_claim_disproved': -1,
    'notice_public_help_confirmed': 1, 'notice_standby_completed': 0}


def initial(seed, day):
    content = load()
    source = f'{content["id"]}.enrollment.{day}'
    digest = hashlib.sha256(f'{seed}:{fingerprint()}:{source}'.encode()).digest()
    occurrence = day + 1 + digest[0] % 2
    ident, resolution = source + '.notice', occurrence + 5
    actual = occurrence + 3 + digest[1] % 2
    posted, witness = (occurrence + 2, occurrence + 5) if digest[2] % 2 else (occurrence + 5, occurrence + 2)
    claims = {
        'poster': dict(id=ident + '.claim.poster', source='shop_board', delivery_day=posted,
            credibility='unverified_print', limitation='The printed notice predates the dispatch ledger.'),
        'handbill': dict(id=ident + '.claim.handbill', source=NEIGHBOR, delivery_day=witness,
            credibility='limited_witness', limitation='Sam saw an earlier handbill, not the dispatch ledger.'),
        'ledger': dict(id=ident + '.claim.ledger', source=CLERK, delivery_day=actual,
            credibility='authenticated_local_record', limitation='Applies only to this neighborhood delivery.')}
    windows = {stage: (occurrence, resolution) for stage in content['stages']}
    windows['verify'] = (occurrence + 1, resolution)
    for stage in ('followup', 'aftermath'):
        windows[stage] = (resolution + 1, resolution + 4)
    return dict(rules_version=1, content_fingerprint=fingerprint(), enabled_day=day,
        last_tick_day=day, id=ident, source_id=source, occurrence_day=occurrence,
        information_day=occurrence + 1, resolution_day=resolution, timing='day_based',
        world_status='eligible', truth=dict(delivery_day=actual, standby_slot=bool(digest[3] % 2)),
        claims=claims, audiences=dict(board=None, tenants=None, desk=None), transmissions=[], observations=[],
        player_claims=[], discovery=None, stages=lifecycle.stages(ident, content['id'], windows),
        receipts=[], desk_post_day=None, impact=None, aftermath=None, followup=None, review_received=False)


def _choice(state, stage):
    selection = state['stages'][stage]['selection']
    return selection['option_id'] if selection else None


def _learn(state, claim):
    if claim not in state['player_claims']:
        state['player_claims'].append(claim)


def _transmit(state, key, day, source, recipient, claim, cause, command_id=None):
    # Authenticated corrections cannot be displaced by a later unchecked claim.
    accepted = state['audiences'][recipient] != 'ledger' or claim == 'ledger'
    state['transmissions'].append(dict(id=state['id'] + '.transmission.' + key, kind='claim', day=day,
        source=source, recipient=recipient, claim_id=state['claims'][claim]['id'],
        claim=claim, cause_id=cause, command_id=command_id, accepted=accepted))
    if accepted:
        state['audiences'][recipient] = claim


def _effect(state, stage, day, command, contact, fact, pay=0):
    lifecycle.receipt(state, stage, day, command, fact, FACT_DELTAS[fact], pay, contact)


def _assess(state, stage, option, context):
    if state['discovery'] is None:
        return 'hidden', None
    content, option_id = load(), option['id']
    verified = 'ledger' in state['player_claims']
    response = _choice(state, 'response')
    if stage == 'compare':
        wanted = 'poster' if option_id == 'board' else 'handbill'
        if wanted in state['player_claims']:
            return 'hidden', None
    if stage == 'verify' and verified:
        return 'hidden', None
    if stage == 'response':
        if option_id in ('correct_board', 'notify_desk', 'reserve_slot') and not verified:
            return 'hidden', None
        if option_id in ('notify_desk', 'reserve_slot') and 'poster' not in state['player_claims']:
            return 'hidden', None
        if option_id == 'reserve_slot' and not state['truth']['standby_slot']:
            return 'hidden', None
        if option_id == 'repeat_notice' and ('poster' not in state['player_claims'] or verified):
            return 'hidden', None
    if stage == 'repair':
        if not verified or (option_id == 'retract' and response != 'repeat_notice') or (
                option_id == 'warn_group' and response not in ('correct_board', 'notify_desk')):
            return 'hidden', None
    if stage == 'followup' and state['followup'] is None:
        return 'hidden', None
    if option_id != 'refuse':
        place = content['place'] if (stage == 'compare' and option_id == 'board') or option_id == 'correct_board' else content['hub']
        if not context['free'] or not context['accessible']:
            return 'unavailable', 'Requires lawful access while free; saving, waiting and refusal remain available'
        if context['location'] != place:
            return 'unavailable', 'Visit ' + place + '; no automatic travel'
    if context['actions'] < option['actions']:
        return 'unavailable', 'Insufficient shared daily actions'
    return 'available', None


def reduce(state, operation, day, arguments, context=None):
    content = load()
    if operation == 'tick':
        if arguments or context is not None:
            raise ValueError('Invalid incident day operation')
        def occur():
            _transmit(state, 'initial_board', state['occurrence_day'], 'printer', 'board', 'poster', state['source_id'])
            _transmit(state, 'initial_handbill', state['occurrence_day'], NEIGHBOR, 'tenants', 'handbill', state['source_id'])
        def inform():
            _transmit(state, 'ledger_available', state['information_day'], CLERK, 'desk', 'ledger', state['source_id'])
        def process():
            post_day = state['desk_post_day']
            if post_day is not None and day >= post_day and not any(t['id'].endswith('.desk_post') for t in state['transmissions']):
                _transmit(state, 'desk_post', post_day, CLERK, 'board', 'ledger', state['id'] + '.response')
            if day >= state['truth']['delivery_day'] and state['impact'] is None:
                at_delivery = dict(board=None, tenants=None)
                for transmission in sorted(enumerate(state['transmissions']), key=lambda pair: (pair[1]['day'], pair[0])):
                    t = transmission[1]
                    if t['day'] <= state['truth']['delivery_day'] and t['recipient'] in at_delivery:
                        who = t['recipient']
                        if at_delivery[who] != 'ledger' or t['claim'] == 'ledger':
                            at_delivery[who] = t['claim']
                state['impact'] = dict(delivery_day=state['truth']['delivery_day'],
                    misdirected=sorted(who for who, claim in at_delivery.items() if claim != 'ledger'))
        def resolve():
            response = _choice(state, 'response')
            corrected = sorted(who for who in ('board', 'tenants') if state['audiences'][who] == 'ledger')
            if state['discovery'] is None:
                outcome = 'missed_unknown'
            elif response == 'refuse':
                outcome = 'refused'
            elif response is None:
                outcome = 'ignored_known'
            elif response == 'reserve_slot':
                outcome = 'exploited_confusion'
                state['followup'] = 'reserved_standby_shift'
            elif response == 'repeat_notice' and _choice(state, 'repair') is None:
                outcome = 'failed'
                _effect(state, 'resolution.disproved', day, None, NEIGHBOR, 'notice_claim_disproved')
            elif not state['impact']['misdirected']:
                outcome = 'success'
            else:
                outcome = 'partial' if corrected else 'failed'
            if response == 'correct_board':
                # Nora's independent signed-board review, not instant omniscience.
                _effect(state, 'resolution.board_review', day, None, CLERK, 'notice_public_help_confirmed')
            state['aftermath'] = dict(resolved_day=day, outcome=outcome,
                corrected_before_reconciliation=corrected, misdirected=deepcopy(state['impact']['misdirected']))
            # Separate actual local observations, reports to the desk, and its
            # public circular. The player receives that summary only by reading.
            for audience, observer in (('board', CLERK), ('tenants', NEIGHBOR)):
                observation = dict(id=state['id'] + '.observation.' + audience,
                    observer=observer, day=state['resolution_day'], audience=audience,
                    misdirected=audience in state['impact']['misdirected'],
                    limitation='Local delivery experience, not knowledge of private player decisions.')
                state['observations'].append(observation)
                state['transmissions'].append(dict(id=observation['id'] + '.report', kind='observation_report',
                    day=state['resolution_day'], source=observer, recipient='desk_reports',
                    observation_id=observation['id'], command_id=None, cause_id=state['id'] + '.resolution'))
            state['claims']['review'] = dict(id=state['id'] + '.claim.review', source=CLERK,
                delivery_day=state['truth']['delivery_day'], credibility='local_reconciliation',
                limitation='Collates local board/tenant reports, not private motives or police evidence.',
                misdirected=deepcopy(state['impact']['misdirected']), corrected_before_reconciliation=corrected)
            state['transmissions'].append(dict(id=state['id'] + '.transmission.review', kind='claim',
                day=state['resolution_day'], source=CLERK, recipient='public_circular',
                claim='review', claim_id=state['claims']['review']['id'], command_id=None,
                cause_id=state['id'] + '.resolution', accepted=True))
            _transmit(state, 'official_board', state['resolution_day'], CLERK, 'board', 'ledger', state['id'] + '.resolution')
            _transmit(state, 'official_circular', state['resolution_day'], CLERK, 'tenants', 'ledger', state['id'] + '.resolution')
        lifecycle.advance(state, day, occur, inform, resolve, process)
        return dict(message='Independent notice sources and correction deliveries processed.')

    if arguments.get('incident_id') != state['id']:
        raise ValueError('Unknown incident')
    if operation == 'discover':
        if state['world_status'] == 'eligible' or day < state['occurrence_day']:
            raise ValueError('No notice has occurred')
        if state['discovery'] is not None:
            raise ValueError('Notice already discovered; use an eligible source comparison')
        channel = arguments['channel']
        audience = 'board' if channel == 'public_notice' else 'tenants' if channel == 'contact' else None
        place = content['place'] if audience == 'board' else content['hub']
        if audience is None or not context['free'] or not context['accessible'] or context['location'] != place:
            raise ValueError('Read the shop board at p032 or speak to Sam at n13')
        claim = state['audiences'][audience]
        _learn(state, claim)
        state['discovery'] = dict(day=day, channel=channel, command_id=context['command_id'])
        return dict(message=f'This source reports delivery day {state["claims"][claim]["delivery_day"]}. '
            + state['claims'][claim]['limitation'])
    if operation != 'choose' or arguments.get('stage') not in state['stages']:
        raise ValueError('Unknown notice operation/stage')
    stage = arguments['stage']
    record = state['stages'][stage]
    option = choice_engine.eligible({'day': day}, record, content['stages'][stage], arguments['option_id'],
        lambda o: _assess(state, stage, o, context))
    selected, command = option['id'], context['command_id']
    source = state['id'] + '.' + stage
    outcome = dict(pay=0, feedback='')
    if stage == 'compare':
        audience = 'board' if selected == 'board' else 'tenants'
        claim = state['audiences'][audience]
        _learn(state, claim)
        if audience == 'tenants':
            _effect(state, stage, day, command, NEIGHBOR, 'notice_source_heard')
        outcome['feedback'] = f'This source says day {state["claims"][claim]["delivery_day"]}. ' + state['claims'][claim]['limitation']
    elif stage == 'verify':
        _learn(state, 'ledger')
        _effect(state, stage, day, command, CLERK, 'notice_ledger_checked')
        outcome['feedback'] = f'Nora shows the authenticated ledger: day {state["truth"]["delivery_day"]}. Standby vacancy: {state["truth"]["standby_slot"]}. No wage or automatic public correction.'
    elif stage == 'response':
        if selected == 'correct_board':
            _transmit(state, 'player_board', day, 'player', 'board', 'ledger', source, command)
            outcome['feedback'] = 'Signed correction posted. The board is corrected; Sam and the tenant group have not been told.'
        elif selected == 'notify_desk':
            state['desk_post_day'] = day + 1
            state['transmissions'].append(dict(id=source + '.desk_report', kind='discrepancy_report', day=day,
                source='player', recipient='desk_reports', claim_id=state['claims']['poster']['id'],
                cause_id=source, command_id=command))
            _effect(state, stage, day, command, CLERK, 'notice_desk_notified')
            outcome['feedback'] = 'Nora received the discrepancy and ordered a board correction for tomorrow. No message was sent to the tenant group.'
        elif selected == 'repeat_notice':
            _transmit(state, 'player_unchecked', day, 'player', 'tenants', 'poster', source, command)
            outcome['feedback'] = 'Sam received your explicitly unchecked posted date. The desk knows nothing of this private conversation; a wrong date may later damage Sam\'s trust.'
        elif selected == 'reserve_slot':
            state['transmissions'].append(dict(id=source + '.reservation_report', kind='discrepancy_report', day=day,
                source='player', recipient='desk_reports', claim_id=state['claims']['poster']['id'],
                cause_id=source, command_id=command))
            _effect(state, stage, day, command, CLERK, 'notice_priority_claimed')
            outcome['feedback'] = 'You disclosed the bad notice but requested the lawful standby slot instead of a correction order. Nora noted the selfish priority (-1 standing). No money paid; no residents were corrected.'
        else:
            outcome['feedback'] = 'Involvement refused. No promise, debt or relationship reward; independent reconciliation continues.'
    elif stage == 'repair':
        _transmit(state, 'player_group', day, 'player', 'tenants', 'ledger', source, command)
        fact = 'notice_retracted' if selected == 'retract' else 'notice_warning_received'
        _effect(state, stage, day, command, NEIGHBOR, fact)
        outcome['feedback'] = 'Verified correction delivered to Sam and the tenant group only. ' + ('Your unchecked claim was retracted without a bonus.' if selected == 'retract' else 'Sam acknowledges your warning.')
    elif stage == 'aftermath':
        _learn(state, 'ledger')
        _learn(state, 'review')
        state['review_received'] = True
        outcome['feedback'] = f'You read the issued correction: delivery day {state["truth"]["delivery_day"]}. No reward or refresh.'
    else:
        pay = content['standby_pay']
        _effect(state, stage, day, command, CLERK, 'notice_standby_completed', pay)
        outcome.update(pay=pay, feedback=f'Completed the actually reserved standby shift: ${pay} once.')
    lifecycle.settle(record, option, day, context, outcome)
    return dict(message=outcome['feedback'], stage=stage, **deepcopy(outcome))


def enable(world):
    import daily_life
    life = daily_life._state(world)
    if 'notice_version' in world or world['player']['arrested']:
        raise ValueError('Notice already adopted or unavailable while detained')
    content = load()
    if any(ident in life['contacts'] for ident in content['contacts']):
        raise ValueError('Notice contact identity already exists without its adoption')
    world['notice_version'] = 1
    world['wrong_notice'] = initial(world['seed'], world['day'])
    for ident in sorted(content['contacts']):
        life['contacts'][ident] = dict(standing=0, memories=[])
    return event(world, 'notice_enabled', 'Adopted one independent notice dispute; no cost, clock or budget refresh.',
        schema_version=1, command_id=world['command_sequence'] + 1, content_fingerprint=fingerprint())


def report(world):
    from world_incidents import context
    state, content = world['wrong_notice'], load()
    ctx = context(world)
    channels = []
    if state['discovery'] is None and state['world_status'] != 'eligible' and ctx['free'] and ctx['accessible']:
        if ctx['location'] == content['place']:
            channels.append('public_notice')
        if ctx['location'] == content['hub']:
            channels.append('contact')
    result = dict(enabled=True, id=state['id'], discovery_channels=channels,
        known=state['discovery'] is not None, journal=None, choices=[])
    if state['discovery'] is not None:
        result['journal'] = dict(title=content['title'], observed_claims=[deepcopy(state['claims'][key]) for key in state['player_claims']],
            finding=state['claims']['ledger']['delivery_day'] if 'ledger' in state['player_claims'] else None,
            information_day=state['information_day'], deadline=state['resolution_day'],
            aftermath=deepcopy(state['aftermath']) if state['review_received'] else None, followup=state['followup'],
            decisions={stage: deepcopy(r['selection']) for stage, r in sorted(state['stages'].items())})
        result['choices'] = lifecycle.choices(world, state, content['stages'], lambda stage, o: _assess(state, stage, o, ctx))
    return deepcopy(result)
