"""Validation for the optional M015 extension; no migration, effects or I/O."""
from copy import deepcopy

from life_content import fingerprint, load


def validate(world):
    from career_state import _integer, _mapping, _records, _require, _text
    path = 'daily_life'
    history = [e for e in world['events'] if e['kind'].startswith('life_')]
    commands = {e['command_id']: e for e in world['events'] if e['kind'] == 'player_command'}
    life_commands = {k: e for k, e in commands.items() if e['command'] in ('settle_in', 'choose', 'pay_room')}
    if 'daily_life_version' not in world:
        _require('daily_life' not in world and not history and not life_commands, 'daily_life_version', 'is required with life state/history')
        return
    _integer(world['daily_life_version'], 'daily_life_version')
    _require(world['daily_life_version'] == 1, 'daily_life_version', 'is unsupported; supported: 1')
    life, content, day = world.get('daily_life'), load(), world['day']
    _mapping(life, path)
    _integer(life.get('rules_version'), path + '.rules_version')
    _require(life['rules_version'] == 1, path + '.rules_version', 'is unsupported; supported: 1')
    _require(life.get('content_fingerprint') == fingerprint(), path + '.content_fingerprint', 'requires the pinned local life content')
    for key in ('enabled_day', 'last_tick_day'):
        _integer(life.get(key), path + '.' + key, 0, day)
    _integer(life.get('activation_day'), path + '.activation_day', life['enabled_day'] + 1, life['enabled_day'] + 1)
    _require(life['last_tick_day'] >= life['enabled_day'], path + '.last_tick_day', 'cannot precede enrollment')
    _require(life.get('home_id') == content['home_id'] and world.get('navigation', {}).get('home_id') == life['home_id'],
             path + '.home_id', 'must agree with the recorded navigation home')
    _integer(life.get('opening_cash'), path + '.opening_cash', 0)
    for key in ('contacts', 'promises', 'choices', 'housing'):
        _mapping(life.get(key), path + '.' + key)

    def check_command(ident, expected, event_day):
        _integer(ident, path + '.command_id', 1, world['command_sequence'])
        _require(ident in commands and commands[ident]['command'] == expected and commands[ident]['day'] == event_day,
                 path + '.command_id', 'must reference its committed command on the same day')
        return commands[ident]

    def match_events(kind, records, keys):
        events = [e for e in history if e['kind'] == kind]
        _require(len(events) == len(records), path + '.' + kind, 'must have exactly one event per record')
        seen = set()
        for e in events:
            ident = e.get('id')
            _require(isinstance(ident, str) and ident in records and ident not in seen,
                     path + '.' + kind, 'must identify a unique record')
            seen.add(ident)
            _require(type(e.get('schema_version')) is int and e['schema_version'] == 1 and
                     all(e.get(k) == records[ident][k] for k in keys), path + '.' + kind, 'must match its saved record')

    transactions = _records(life.get('transactions'), path + '.transactions')
    balance, txs = life['opening_cash'], {}
    for index, tx in enumerate(transactions, 1):
        _require(tx.get('id') == f'goon.transaction.{index}', path + '.transactions.id', 'must have contiguous unique identities')
        _integer(tx.get('day'), path + '.transactions.day', life['enabled_day'], day)
        for key in ('before', 'after'):
            _integer(tx.get(key), path + '.transactions.' + key, 0)
        _integer(tx.get('amount'), path + '.transactions.amount')
        _require(tx['before'] == balance and tx['after'] - tx['before'] == tx['amount'], path + '.transactions', 'must form a continuous actual-cash ledger')
        _require(tx.get('cause') in ('existing_rules', 'room_payment', 'lawful_wage', 'criminal_job'), path + '.transactions.cause', 'is unsupported')
        _text(tx.get('source_id'), path + '.transactions.source_id')
        _require('command_id' in tx, path + '.transactions.command_id', 'is required (null for a day phase)')
        if tx['command_id'] is not None:
            _integer(tx['command_id'], path + '.transactions.command_id', 1)
            _require(tx['command_id'] in commands and commands[tx['command_id']]['day'] == tx['day'], path + '.transactions.command_id', 'must reference a same-day command')
        balance, txs[tx['id']] = tx['after'], tx
    _require(balance == world['player']['cash'], path + '.transactions', 'must agree with authoritative player cash')
    match_events('life_transaction', txs, ('day', 'before', 'after', 'amount', 'cause', 'source_id', 'command_id'))

    choices, used_slots, used_commands, work_txs = life['choices'], set(), set(), set()
    max_week = max(0, (day - life['activation_day']) // 7)
    for ident, r in choices.items():
        _mapping(r, path + '.choices[]')
        _require(r.get('id') == ident, path + '.choices.id', 'must match its key')
        key = r.get('definition_id')
        _require(isinstance(key, str) and key in content['choices'], path + '.choices.definition_id', 'must reference pinned content')
        definition = content['choices'][key]
        _text(r.get('source_id'), path + '.choices.source_id')
        _integer(r.get('week'), path + '.choices.week', 0, max_week)
        _integer(r.get('open_day'), path + '.choices.open_day', life['activation_day'])
        _integer(r.get('expires_day'), path + '.choices.expires_day', r['open_day'] + 1)
        if key == 'room_review':
            _require(ident.startswith('goon.choice.room.') and r['expires_day'] == r['open_day'] + 7,
                     path + '.choices', 'must retain the room review window')
        else:
            expected_day = life['activation_day'] + r['week'] * 7 + definition['start']
            _require(ident == f'goon.choice.{r["week"]}.{key}' and r['open_day'] == expected_day and
                     r['expires_day'] == expected_day + definition['duration'], path + '.choices', 'must retain its source window/identity')
            expected_source = f'goon.promise.{r["week"]}.tess' if key == 'rescheduled_help' else f'goon.roster.{r["week"]}.{key}'
            _require(r['source_id'] == expected_source, path + '.choices.source_id', 'must match its source')
        state = r.get('state')
        _require(state in ('open', 'resolved', 'expired') and 'selection' in r, path + '.choices.state', 'is unsupported or missing selection')
        if state != 'resolved':
            _require(r['selection'] is None, path + '.choices.selection', 'must be null until resolved')
            if state == 'expired':
                _require(r['expires_day'] <= life['last_tick_day'], path + '.choices', 'cannot expire before its deadline')
            else:
                _require(r['expires_day'] > life['last_tick_day'], path + '.choices', 'cannot remain open after daily processing of its deadline')
            continue
        selection = r['selection']
        _mapping(selection, path + '.choices.selection')
        option = next((o for o in definition['options'] if o['id'] == selection.get('option_id')), None)
        _require(option is not None, path + '.choices.option_id', 'must reference a pinned option')
        _integer(selection.get('day'), path + '.choices.selection.day', r['open_day'], min(day, r['expires_day'] - 1))
        command = check_command(selection.get('command_id'), 'choose', selection['day'])
        _require(command['arguments'] == dict(choice_id=ident, option_id=option['id']) and
                 command['action_cost'] == option['actions'] and selection.get('action_cost') == option['actions'],
                 path + '.choices.selection', 'must match command arguments and action cost')
        _require(selection['command_id'] not in used_commands, path + '.choices.command_id', 'cannot settle multiple choices')
        used_commands.add(selection['command_id'])
        outcome = selection.get('outcome')
        _mapping(outcome, path + '.choices.outcome')
        _require(outcome.get('effect') == option['effect'], path + '.choices.outcome', 'must match the selected effect')
        _text(outcome.get('feedback'), path + '.choices.feedback')
        expected_slot = f'goon.slot.{r["week"]}.{definition["slot"]}' if option['actions'] and definition['slot'] else None
        _require(outcome.get('slot') == expected_slot, path + '.choices.slot', 'must match the disclosed roster slot')
        if expected_slot:
            _require(expected_slot not in used_slots, path + '.choices.slot', 'cannot be committed twice')
            used_slots.add(expected_slot)
        if option['effect'] in ('lawful_work', 'criminal_work'):
            tx = txs.get(outcome.get('transaction_id')) if isinstance(outcome.get('transaction_id'), str) else None
            _require(tx is not None and tx['source_id'] == ident and tx['command_id'] == selection['command_id'], path + '.choices.transaction', 'must identify its own settlement')
            _require(tx['id'] not in work_txs, path + '.choices.transaction', 'cannot settle multiple opportunities')
            work_txs.add(tx['id'])
            if option['effect'] == 'lawful_work':
                _require(tx['cause'] == 'lawful_wage' and tx['amount'] == option['pay'], path + '.choices.transaction', 'must match its funded wage')
            else:
                _integer(outcome.get('source_attempt'), path + '.choices.source_attempt', 0)
                job = next((e for e in world['events'] if e['kind'] == 'job' and e.get('attempt') == outcome['source_attempt']), None)
                _require(job is not None and job['day'] == selection['day'] and job['job'] == option['job'] and
                         tx['cause'] == 'criminal_job' and tx['amount'] == job['payout'] == outcome.get('payout') and
                         type(outcome.get('success')) is bool and outcome['success'] == job['success'], path + '.choices.transaction', 'must match the existing job result without a second payout')
    _require(used_commands == {k for k, e in life_commands.items() if e['command'] == 'choose'}, path + '.choices.command_id', 'must settle every choose command once')
    choice_events = [e for e in history if e['kind'] == 'life_choice']
    _require(len(choice_events) == len(used_commands), path + '.choices.events', 'must match committed choices')
    seen = set()
    for e in choice_events:
        ident = e.get('choice_id')
        _require(isinstance(ident, str) and ident in choices and ident not in seen and choices[ident]['state'] == 'resolved', path + '.choices.events', 'must identify one resolved choice')
        seen.add(ident)
        r = choices[ident]
        _require(e.get('source_id') == r['source_id'] and all(e.get(k) == v for k, v in r['selection'].items()), path + '.choices.events', 'must match the saved selection')
    for kind, expected in (('life_opportunity', set(choices)), ('life_expired', {k for k, r in choices.items() if r['state'] == 'expired'})):
        events = [e for e in history if e['kind'] == kind]
        _require(len(events) == len(expected) and {e.get('choice_id') for e in events if isinstance(e.get('choice_id'), str)} == expected,
                 path + '.' + kind, 'must identify each source exactly once')

    promises = life['promises']
    accepted = {f'goon.promise.{r["week"]}.tess': r['id'] for r in choices.values()
                if r['selection'] and r['selection']['outcome']['effect'] == 'make_promise'}
    _require(set(promises) == set(accepted), path + '.promises',
             'must retain one commitment for every accepted invitation')
    for ident, p in promises.items():
        _mapping(p, path + '.promises[]')
        _integer(p.get('week'), path + '.promises.week', 0, max_week)
        _require(ident == p.get('id') == f'goon.promise.{p["week"]}.tess' and p.get('contact_id') == 'goon.contact.tess', path + '.promises.id', 'must identify the original commitment')
        _require(type(p.get('renegotiated')) is bool, path + '.promises.renegotiated', 'must be boolean')
        due = life['activation_day'] + p['week'] * 7 + (4 if p['renegotiated'] else 2)
        _integer(p.get('due_day'), path + '.promises.due_day', due, due)
        source = choices.get(p.get('source_id')) if isinstance(p.get('source_id'), str) else None
        _require(p.get('source_id') == accepted[ident] and source is not None and source['selection'] is not None and
                 source['selection']['outcome']['effect'] == 'make_promise', path + '.promises.source_id', 'must reference its own accepted invitation')
        _require(p.get('status') in ('pending', 'kept', 'broken'), path + '.promises.status', 'is unsupported')
        if p['status'] == 'pending':
            _require(p.get('resolved_day') is None and p.get('resolution_source') is None and p['due_day'] > life['last_tick_day'], path + '.promises', 'must await a future deadline')
        else:
            _integer(p.get('resolved_day'), path + '.promises.resolved_day', source['selection']['day'], day)
            _require(p.get('resolution_source') == ident or (isinstance(p.get('resolution_source'), str) and p['resolution_source'] in choices), path + '.promises.resolution_source', 'must reference its resolution')
            if p['resolution_source'] == ident:
                _require(p['status'] == 'broken' and p['resolved_day'] >= due, path + '.promises', 'must break only at its recorded deadline')
            else:
                resolution = choices[p['resolution_source']]['selection']
                effect = 'keep_promise' if p['status'] == 'kept' else 'break_promise'
                _require(resolution is not None and resolution['outcome']['effect'] == effect and resolution['day'] == p['resolved_day'], path + '.promises', 'must match its selected resolution')
        moved = choices.get(f'goon.choice.{p["week"]}.crossroads', {}).get('selection')
        was_moved = moved is not None and moved['outcome']['effect'] == 'move_promise'
        _require(p['renegotiated'] == was_moved, path + '.promises.renegotiated', 'must match its committed renegotiation choice')
    terminal_promises = {k: p for k, p in promises.items() if p['status'] != 'pending'}
    promise_events = [e for e in history if e['kind'] == 'life_promise']
    _require(len(promise_events) == len(terminal_promises), path + '.promises.events', 'must record each terminal promise once')
    seen = set()
    for e in promise_events:
        ident = e.get('promise_id')
        _require(isinstance(ident, str) and ident in terminal_promises and ident not in seen, path + '.promises.events', 'must identify a unique promise')
        seen.add(ident)
        p = terminal_promises[ident]
        _require(e['day'] == p['resolved_day'] and e.get('status') == p['status'] and e.get('due_day') == p['due_day'] and
                 e.get('source_id') == p['resolution_source'], path + '.promises.events', 'must match its recorded resolution')

    from daily_life import contact_definitions
    from incident_state import memories as incident_memories
    external_memories = incident_memories(world)
    _require(set(life['contacts']) == set(contact_definitions(world)), path + '.contacts', 'must retain the declared contacts')
    memories = {}
    allowed = {'goon.contact.tess': {'work_completed', 'promise_accepted', 'promise_kept', 'promise_broken', 'promise_moved'},
               'goon.contact.cal': {'terms_disclosed', 'collection_completed', 'collection_failed', 'courier_completed', 'courier_failed'}}
    if 'incident_version' in world:
        from incident_content import load as incident_content
        from world_incidents import FACT_DELTAS
        allowed[incident_content()['contact_id']] = set(FACT_DELTAS)
    facts_seen = set()
    for ident, person in life['contacts'].items():
        _mapping(person, path + '.contacts[]')
        _integer(person.get('standing'), path + '.contacts.standing', -10, 10)
        before = 0
        for index, m in enumerate(_records(person.get('memories'), path + '.contacts.memories'), 1):
            _require(m.get('id') == f'{ident}.memory.{index}', path + '.contacts.memory.id', 'must have contiguous identities')
            _integer(m.get('day'), path + '.contacts.memory.day', life['activation_day'], day)
            _require(isinstance(m.get('fact'), str) and m['fact'] in allowed[ident], path + '.contacts.memory.fact', 'must be an observed fact appropriate to this contact')
            external = external_memories.get((ident, m.get('fact'), m.get('source_id'))) if isinstance(m.get('source_id'), str) else None
            _require(isinstance(m.get('source_id'), str) and (m['source_id'] in choices or m['source_id'] in promises or external is not None), path + '.contacts.memory.source', 'must reference an interaction or promise')
            fact_source = (ident, m['fact'], m['source_id'])
            _require(fact_source not in facts_seen, path + '.contacts.memory.source', 'cannot reward an interaction twice')
            facts_seen.add(fact_source)
            for key in ('before', 'after'):
                _integer(m.get(key), path + '.contacts.memory.' + key, -10, 10)
            _integer(m.get('delta'), path + '.contacts.memory.delta', -3, 3)
            _require(m['before'] == before and m['after'] - before == m['delta'], path + '.contacts.memory', 'must form a bounded standing history')
            expected_delta = external['delta'] if external else {'work_completed': 1, 'promise_accepted': 0, 'promise_moved': 0,
                'promise_kept': 3, 'promise_broken': -2, 'terms_disclosed': 0,
                'collection_completed': 2, 'collection_failed': -1, 'courier_completed': 2, 'courier_failed': -1}[m['fact']]
            _require(m['after'] == max(-10, min(10, before + expected_delta)), path + '.contacts.memory.delta', 'must match the observed interaction')
            source = choices.get(m['source_id'])
            if external is not None:
                _require(m['day'] == external['day'], path + '.contacts.memory.source', 'must match the incident effect day')
            elif source is not None:
                selection = source['selection']
                expected_effect = {'work_completed': 'lawful_work', 'promise_accepted': 'make_promise', 'promise_moved': 'move_promise',
                    'promise_kept': 'keep_promise', 'promise_broken': 'break_promise', 'terms_disclosed': 'introduction'}.get(m['fact'], 'criminal_work')
                _require(selection is not None and selection['day'] == m['day'] and selection['outcome']['effect'] == expected_effect,
                         path + '.contacts.memory.source', 'must match an observed interaction on that day')
            else:
                p = promises[m['source_id']]
                _require(m['fact'] == 'promise_broken' and p['status'] == 'broken' and p['resolved_day'] == m['day'], path + '.contacts.memory.source', 'must match an observed missed promise')
            before = m['after']
            memories[m['id']] = dict(m, contact_id=ident)
        _require(person['standing'] == before, path + '.contacts.standing', 'must match its interaction history')
    match_events('life_memory', memories, ('day', 'contact_id', 'fact', 'source_id', 'before', 'after', 'delta'))

    housing = life['housing']
    expected = dict(next_due_day=life['enabled_day'] + 7, arrears=0, prepaid=0)
    receipts, room_txs, room_help_sources, payment_commands = {}, set(), set(), set()
    for index, r in enumerate(_records(housing.get('history'), path + '.housing.history'), 1):
        _require(r.get('id') == f'goon.room.receipt.{index}', path + '.housing.history.id', 'must have contiguous unique identities')
        _integer(r.get('day'), path + '.housing.history.day', life['activation_day'], day)
        _require(r.get('before') == expected, path + '.housing.history.before', 'must match the prior housing balance')
        for key in ('paid', 'assessed', 'credit'):
            _integer(r.get(key), path + '.housing.history.' + key, 0, 30)
        _text(r.get('source_id'), path + '.housing.history.source_id')
        after = deepcopy(expected)
        kind = r.get('operation')
        if kind == 'due':
            assessed = 0 if expected['arrears'] else 30
            credit = min(expected['arrears'] + assessed, expected['prepaid'])
            _require(expected['next_due_day'] <= r['day'] <= life['last_tick_day'] and r['assessed'] == assessed and r['credit'] == credit,
                     path + '.housing.history', 'must match the disclosed bounded due policy')
            after.update(next_due_day=expected['next_due_day'] + 7,
                arrears=expected['arrears'] + assessed - credit - r['paid'], prepaid=expected['prepaid'] - credit)
            cycle = (expected['next_due_day'] - life['enabled_day']) // 7
            _require(r['source_id'] == f'goon.obligation.room.{cycle}', path + '.housing.history.source_id', 'must identify its due cycle')
        elif kind == 'prepay':
            _require(not expected['arrears'] and r['paid'] > 0 and r['assessed'] == r['credit'] == 0, path + '.housing.history', 'must be a real bounded prepayment')
            after['prepaid'] += r['paid']
        elif kind == 'arrears_payment':
            _require(expected['arrears'] > 0 and r['paid'] > 0 and r['assessed'] == r['credit'] == 0, path + '.housing.history', 'must pay an existing balance')
            after['arrears'] -= r['paid']
        elif kind == 'work_credit':
            _require(r['paid'] == r['assessed'] == 0 and r['credit'] == min(10, expected['arrears']) and r['credit'] > 0 and r.get('transaction_id') is None,
                     path + '.housing.history', 'must credit existing arrears without cash')
            source = choices.get(r['source_id'])
            _require(source is not None and source['selection'] is not None and source['selection']['outcome']['effect'] == 'room_help', path + '.housing.history', 'must reference one maintenance choice')
            _require(r['source_id'] not in room_help_sources, path + '.housing.history', 'cannot credit maintenance twice')
            room_help_sources.add(r['source_id'])
            after['arrears'] -= r['credit']
        else:
            _require(False, path + '.housing.history.kind', 'is unsupported')
        for key in ('arrears', 'prepaid'):
            _integer(after[key], path + '.housing.' + key, 0, 30)
        _require(not (after['arrears'] and after['prepaid']) and r.get('after') == after, path + '.housing.history.after', 'must match the bounded receipt')
        if kind != 'work_credit':
            tx = txs.get(r.get('transaction_id')) if isinstance(r.get('transaction_id'), str) else None
            _require(tx is not None and tx['amount'] == -r['paid'] and tx['cause'] == 'room_payment' and tx['source_id'] == r['source_id'], path + '.housing.history.transaction_id', 'must match its actual payment once')
            _require(tx['id'] not in room_txs, path + '.housing.history.transaction_id', 'cannot fund two receipts')
            room_txs.add(tx['id'])
            remaining = expected['arrears'] + r['assessed'] - r['credit'] if kind == 'due' else expected['arrears'] or (30 - expected['prepaid'])
            _require(r['paid'] == min(tx['before'], remaining), path + '.housing.history.paid', 'must charge only the disclosed available amount')
            if kind != 'due':
                command = check_command(tx['command_id'], 'pay_room', r['day'])
                _require(r['source_id'] == f'goon.command.{command["command_id"]}', path + '.housing.history.source_id', 'must reference its payment command')
                payment_commands.add(command['command_id'])
        expected, receipts[r['id']] = after, r
    _require(all(housing.get(k) == v for k, v in expected.items()), path + '.housing', 'must match its receipt history')
    if life['last_tick_day'] >= life['activation_day']:
        _require(housing['next_due_day'] > life['last_tick_day'], path + '.housing.next_due_day', 'must follow the processed day')
    match_events('life_housing', receipts, ('day', 'operation', 'source_id', 'before', 'after', 'paid', 'transaction_id', 'assessed', 'credit'))
    _require(work_txs == {k for k, tx in txs.items() if tx['cause'] in ('lawful_wage', 'criminal_job')} and
             room_txs == {k for k, tx in txs.items() if tx['cause'] == 'room_payment'}, path + '.transactions', 'must tie every settlement to its unique outcome/receipt')
    _require(payment_commands == {k for k, e in life_commands.items() if e['command'] == 'pay_room'}, path + '.housing.history', 'must settle each payment command once')
    _require(room_help_sources == {k for k, r in choices.items() if r['selection'] and r['selection']['outcome']['effect'] == 'room_help'}, path + '.housing.history', 'must credit each selected maintenance task once')
    enabled = [e for e in history if e['kind'] == 'life_enabled']
    _require(len(enabled) == 1 and enabled[0]['day'] == life['enabled_day'] and enabled[0].get('due_day') == life['enabled_day'] + 7,
             path + '.enrollment', 'must have one disclosed enrollment')
    check_command(enabled[0].get('command_id'), 'settle_in', life['enabled_day'])
    _require({k for k, e in life_commands.items() if e['command'] == 'settle_in'} == {enabled[0]['command_id']}, path + '.enrollment', 'cannot be repeated')
    ticks = [e for e in history if e['kind'] == 'life_day']
    _require(all(type(e.get('processed_day')) is int and e['processed_day'] == e['day'] and life['activation_day'] <= e['day'] <= day for e in ticks)
             and len({e['day'] for e in ticks}) == len(ticks) and
             max((e['day'] for e in ticks), default=life['enabled_day']) == life['last_tick_day'],
             path + '.last_tick_day', 'must match unique daily processing events')
    if day < life['activation_day']:
        _require(not choices and not promises and not receipts and not memories, path, 'pending enrollment cannot invent active opportunities/history')
