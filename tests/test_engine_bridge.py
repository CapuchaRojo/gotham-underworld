"""Real engine effects plus durable boundary faults; no frontend fixtures."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import bridge_checkpoint as disk
from bridge_projection import player_view
from engine_bridge import Bridge
import game_service as engine
from mobility_content import OVERLAY_ID

ROOT = Path(__file__).resolve().parents[1]
CHOICE = 'goon.choice.0.opening_shift'


class EngineBridgeTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'bridge.json'
        self.bridge = Bridge.create(self.path)
        self.addCleanup(lambda: self.bridge.close())
        self.counter = 0

    def request(self, command, **args):
        state = self.bridge.state()
        self.counter += 1
        return dict(protocol_version=1, career_id=state['career_id'], lineage_id=state['lineage_id'],
                    request_id=f'op-{self.counter}', expected_revision=state['revision'],
                    command=command, arguments=args)

    def send(self, command, **args):
        return self.bridge.execute(self.request(command, **args))

    def checkpoint(self):
        return disk.validate(disk.decode_json(self.path.read_text(encoding='utf-8')))

    def ready(self):
        self.send('settle_in')
        self.send('wait')
        self.send('travel', destination='p032', mode='walk')

    def unchanged_rejection(self, request, code):
        before, rng = self.path.read_bytes(), random.getstate()
        state = self.bridge.state()
        with self.assertRaises(disk.BridgeError) as caught:
            self.bridge.execute(request)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.bridge.state(), state)
        self.assertEqual(random.getstate(), rng)

    def test_real_repair_is_durable_and_not_a_fixture(self):
        self.ready()
        response = self.send('choose', choice_id=CHOICE, option_id='work')
        state = response['state']
        self.assertEqual((state['player']['cash'], state['budgets']['actions_remaining'],
                          state['budgets']['travel_units_remaining']), (60, 2, 17))
        tess = next(c for c in state['contacts'] if c['id'] == 'goon.contact.tess')
        self.assertEqual(tess['standing'], 1)
        self.assertEqual(state['outcomes'][-1]['choice_id'], CHOICE)
        world = self.checkpoint()['world']
        self.assertEqual(disk.digest(world), 'c0f74312014e5cd2dbc930493d2cee61936f8e459096250400a03672cc1cc352')
        self.assertEqual(len(world['daily_life']['transactions']), 1)
        self.assertEqual(world['daily_life']['transactions'][0]['amount'], 20)
        self.assertEqual(response['receipt']['command_sequence'], world['command_sequence'])

    def test_duplicate_wage_returns_original_receipt_before_stale_check(self):
        self.ready()
        request = self.request('choose', choice_id=CHOICE, option_id='work')
        original = self.bridge.execute(request)
        before = self.path.read_bytes()
        duplicate = self.bridge.execute(request)
        self.assertEqual(duplicate['receipt'], original['receipt'])
        self.assertTrue(duplicate['duplicate'])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(duplicate['state']['player']['cash'], 60)

    def test_new_request_cannot_pay_a_resolved_offer_again(self):
        self.ready()
        self.send('choose', choice_id=CHOICE, option_id='work')
        self.unchanged_rejection(self.request('choose', choice_id=CHOICE, option_id='work'), 'COMMAND_REJECTED')

    def test_duplicate_wait_does_not_advance_twice_even_after_restart(self):
        request = self.request('wait')
        original = self.bridge.execute(request)
        self.bridge.close()
        self.bridge = Bridge.open(self.path)
        duplicate = self.bridge.execute(request)
        self.assertEqual(duplicate['receipt'], original['receipt'])
        self.assertEqual(duplicate['state']['day'], 1)

    def test_lost_ack_recovered_by_operation_after_later_commands(self):
        request = self.request('wait')
        original = self.bridge.execute(request)
        self.send('wait')
        self.bridge.close()
        self.bridge = Bridge.open(self.path)
        recovery = self.bridge.operation(request['request_id'])
        self.assertEqual(recovery['receipt'], original['receipt'])
        self.assertEqual(recovery['revision'], 2)
        self.assertEqual(recovery['state']['day'], 2)

    def test_payload_conflict_and_stale_new_intent_are_pure(self):
        request = self.request('wait')
        self.bridge.execute(request)
        changed = deepcopy(request)
        changed['command'] = 'settle_in'
        self.unchanged_rejection(changed, 'REQUEST_ID_REUSED')
        stale = deepcopy(request)
        stale['request_id'] = 'different-intent'
        self.unchanged_rejection(stale, 'STALE_REVISION')

    def test_wrong_lineage_and_protocol_are_rejected(self):
        request = self.request('wait')
        for value in ('other-career', 'other-lineage'):
            altered = deepcopy(request)
            altered['career_id' if value == 'other-career' else 'lineage_id'] = value
            self.unchanged_rejection(altered, 'WRONG_CAREER')
        for version in (True, 0, 2, '1'):
            altered = deepcopy(request)
            altered['protocol_version'] = version
            self.unchanged_rejection(altered, 'PROTOCOL_MISMATCH')

    def test_forged_money_cost_location_and_unknown_fields(self):
        self.ready()
        for field in ('pay', 'cash', 'action_cost', 'location', 'world'):
            request = self.request('choose', choice_id=CHOICE, option_id='work')
            request['arguments'][field] = '999'
            self.unchanged_rejection(request, 'INVALID_ARGUMENTS')
        for args in ({'choice_id': CHOICE}, {'choice_id': CHOICE, 'option_id': True},
                     {'choice_id': CHOICE, 'option_id': 'x' * 257}):
            request = self.request('choose', choice_id=CHOICE, option_id='work')
            request['arguments'] = args
            self.unchanged_rejection(request, 'INVALID_ARGUMENTS')
        request = self.request('wait')
        request['developer'] = True
        self.unchanged_rejection(request, 'INVALID_REQUEST')
        request = self.request('wait')
        request['command'] = '__import__'
        self.unchanged_rejection(request, 'COMMAND_NOT_ALLOWED')

    def test_wrong_place_and_expired_work_cannot_pay(self):
        self.send('settle_in')
        self.send('wait')
        self.unchanged_rejection(self.request('choose', choice_id=CHOICE, option_id='work'), 'COMMAND_REJECTED')
        self.send('wait')
        self.send('travel', destination='p032', mode='walk')
        self.unchanged_rejection(self.request('choose', choice_id=CHOICE, option_id='work'), 'COMMAND_REJECTED')

    def test_refusal_is_free_and_inspection_never_adopts_or_refreshes(self):
        before, rng = self.path.read_bytes(), random.getstate()
        for _ in range(3):
            state = self.bridge.state()
            self.assertEqual(state['state']['systems']['daily_life'], 'not_adopted')
            self.bridge.route('p032', 'walk')
            self.bridge.operation('never-submitted')
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(random.getstate(), rng)
        self.send('settle_in')
        self.assertEqual(self.bridge.state()['state']['systems']['daily_life'], 'pending')
        self.send('wait')
        result = self.send('choose', choice_id=CHOICE, option_id='decline')
        self.assertEqual(result['state']['player']['cash'], 40)
        self.assertEqual(result['state']['budgets']['actions_remaining'], 3)

    def test_hidden_incidents_and_private_npc_state_never_cross_projection(self):
        world = engine.create_career(42)
        engine.execute_command(world, 'settle_in')
        engine.advance_day(world)
        engine.execute_command(world, 'enable_incidents')
        engine.execute_command(world, 'enable_incident', definition_id='goon.incident.wrong_notice.v1')
        engine.execute_command(world, 'enable_institutions')
        for _ in range(4):
            engine.advance_day(world)
        world['private_annotation'] = 'PRIVATE_SENTINEL'
        world['people']['Mara Voss']['private_note'] = 'PRIVATE_SENTINEL'
        source = Path(self.folder.name) / 'historical.json'
        engine.save_career(world, source, overwrite=False)
        other = Path(self.folder.name) / 'adopted.json'
        with Bridge.import_legacy(source, other) as bridge:
            before = deepcopy(world)
            public = bridge.state()
            for _ in range(3):
                bridge.state()
            text = json.dumps(public)
            for forbidden in ('PRIVATE_SENTINEL', 'Ada Quinn', 'Mara Voss', 'owner_facts', 'world_status',
                              'goon.incident.', 'incident_transition', 'content_fingerprint', 'request_command_id'):
                self.assertNotIn(forbidden, text)
            self.assertEqual(world, before)
            self.assertNotIn('incidents', public['state'])
            # Hidden criminal options cannot be inferred by reading a choice row.
            options = [o['id'] for r in public['state']['opportunities'] for o in r['options']]
            self.assertNotIn('collection', options)
            self.assertNotIn('courier', options)

    def test_response_is_detached_and_has_no_raw_events(self):
        self.ready()
        response = self.send('choose', choice_id=CHOICE, option_id='work')
        self.assertNotIn('events', response)
        response['receipt']['status'] = 'forged'
        response['state']['player']['cash'] = 999
        response['state']['contacts'].clear()
        self.assertEqual(self.bridge.state()['state']['player']['cash'], 60)
        self.assertEqual(self.bridge.operation('op-4')['receipt']['status'], 'committed')

    def test_failure_before_publication_preserves_disk_live_world_and_backup(self):
        request = self.request('wait')
        before = self.path.read_bytes()
        replace = disk.os.replace
        def fail_primary(source, target):
            if Path(target) == self.path:
                raise OSError('injected before primary replacement')
            return replace(source, target)
        with patch('bridge_checkpoint.os.replace', side_effect=fail_primary):
            with self.assertRaises(disk.BridgeError) as caught:
                self.bridge.execute(request)
        self.assertEqual(caught.exception.code, 'OUTCOME_UNKNOWN')
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(Path(str(self.path) + '.bak').read_bytes(), before)
        with self.assertRaises(disk.BridgeError):
            self.bridge.execute(request)
        recovery = self.bridge.operation(request['request_id'])
        self.assertEqual(recovery['operation_status'], 'not_found')
        self.assertEqual(recovery['state']['day'], 0)
        self.assertEqual(self.bridge.execute(request)['state']['day'], 1)
        self.assertFalse(list(self.path.parent.glob('*.tmp')))

    def test_failure_after_publication_recovers_world_and_receipt_after_restart(self):
        request = self.request('wait')
        replace = disk.os.replace
        def replace_then_fail(source, target):
            replace(source, target)
            if Path(target) == self.path:
                raise OSError('acknowledgment lost after replacement')
        with patch('bridge_checkpoint.os.replace', side_effect=replace_then_fail):
            with self.assertRaises(disk.BridgeError) as caught:
                self.bridge.execute(request)
        self.assertEqual(caught.exception.code, 'OUTCOME_UNKNOWN')
        self.assertEqual(self.bridge._checkpoint['revision'], 0)
        self.assertEqual(self.checkpoint()['revision'], 1)
        self.bridge.close()
        self.bridge = Bridge.open(self.path)
        original = self.bridge.operation(request['request_id'])
        duplicate = self.bridge.execute(request)
        self.assertEqual(original['receipt'], duplicate['receipt'])
        self.assertEqual(duplicate['state']['day'], 1)

    def test_uncertain_unreadable_disk_blocks_mutation_until_recovered(self):
        request = self.request('wait')
        with patch('bridge_checkpoint._stage', side_effect=OSError('disk full')):
            with self.assertRaises(disk.BridgeError):
                self.bridge.execute(request)
        with patch.object(self.bridge._store, 'read', side_effect=OSError('unreadable')):
            for read in (self.bridge.state, lambda: self.bridge.operation(request['request_id'])):
                with self.assertRaises(disk.BridgeError) as caught:
                    read()
                self.assertEqual(caught.exception.code, 'OUTCOME_UNKNOWN')
            with self.assertRaises(disk.BridgeError):
                self.bridge.execute(request)
        self.assertEqual(self.bridge.operation(request['request_id'])['operation_status'], 'not_found')

    def test_flush_and_backup_failures_leave_previous_world(self):
        for target in ('bridge_checkpoint.os.fsync', 'bridge_checkpoint.os.replace'):
            with self.subTest(target=target):
                request = self.request('wait')
                before = self.path.read_bytes()
                with patch(target, side_effect=OSError('injected failure')):
                    with self.assertRaises(disk.BridgeError):
                        self.bridge.execute(request)
                self.assertEqual(self.path.read_bytes(), before)
                self.assertEqual(self.bridge.operation(request['request_id'])['operation_status'], 'not_found')

    def test_bad_primary_is_not_silently_rewound_to_backup(self):
        self.send('wait')
        self.bridge.close()
        self.path.write_text('broken', encoding='utf-8')
        with self.assertRaises(disk.BridgeError):
            Bridge.open(self.path)

    def test_external_valid_checkpoint_change_is_not_overwritten(self):
        before = self.checkpoint()
        request = self.request('wait')
        self.send('wait')
        self.path.write_bytes(disk.canonical(before))
        newer = self.request('wait')
        self.unchanged_rejection(newer, 'CHECKPOINT_CHANGED')

    def test_checkpoint_rejects_forged_receipts_and_metadata(self):
        self.send('wait')
        valid = self.checkpoint()
        changes = [lambda c: c.update(bridge_version=True), lambda c: c.update(revision=0),
                   lambda c: c.update(world_hash='bad'), lambda c: c['operations'].append(c['operations'][0]),
                   lambda c: c['operations'][0]['receipt'].update(status='pending'),
                   lambda c: c['operations'][0]['request']['arguments'].update(cash='99'),
                   lambda c: c.update(unexpected=True)]
        for change in changes:
            with self.subTest(change=change):
                value = deepcopy(valid)
                change(value)
                with self.assertRaises(disk.BridgeError):
                    disk.validate(value)

    def test_transport_receipts_require_ordered_player_owned_source_commands(self):
        self.send('wait')
        self.send('wait')
        original = self.checkpoint()
        positions = [i for i, e in enumerate(original['world']['events']) if e['kind'] == 'player_command']
        for alteration in ('reorder', 'actor', 'fixed_cost'):
            value = deepcopy(original)
            events = value['world']['events']
            if alteration == 'reorder':
                a, b = positions
                events[a], events[b] = events[b], events[a]
            elif alteration == 'actor':
                events[positions[0]]['actor'] = 'another_actor'
            else:
                events[positions[0]]['action_cost'] = 1
            value['world_hash'] = disk.digest(value['world'])
            with self.subTest(alteration=alteration), self.assertRaises(disk.BridgeError):
                disk.validate(value)

    def test_json_duplicates_nonfinite_and_optimized_validation(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}', '[] nope'):
            with self.assertRaises(disk.BridgeError):
                disk.decode_json(text)
        code = ('from bridge_checkpoint import validate,BridgeError; import json,sys; '
                'c=json.load(open(sys.argv[1])); c["bridge_version"]=True;\n'
                'try: validate(c)\n'
                'except BridgeError: print("REJECTED")\n'
                'else: raise RuntimeError("validation disabled")')
        run = subprocess.run([sys.executable, '-O', '-B', '-c', code, str(self.path)],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(run.stdout.strip(), 'REJECTED')

    def test_simultaneous_duplicate_and_stale_requests_have_one_effect(self):
        request = self.request('wait')
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(self.bridge.execute, [request] * 6))
        self.assertEqual(len({r['receipt']['command_sequence'] for r in results}), 1)
        self.assertEqual(self.bridge.state()['state']['day'], 1)
        self.assertEqual(sum(not r['duplicate'] for r in results), 1)

    def test_exclusive_creation_export_and_cross_process_writer_lock(self):
        before = self.path.read_bytes()
        code = ('from engine_bridge import Bridge; from bridge_checkpoint import BridgeError; import sys;\n'
                'try: Bridge.open(sys.argv[1])\n'
                'except BridgeError as e: print(e.code)\n'
                'else: raise RuntimeError("second writer admitted")')
        run = subprocess.run([sys.executable, '-B', '-c', code, str(self.path)], cwd=ROOT,
                             capture_output=True, text=True, check=True)
        self.assertEqual(run.stdout.strip(), 'CAREER_IN_USE')
        exported = self.path.parent / 'engine.json'
        self.bridge.export_legacy(exported)
        self.assertEqual(engine.load_career(exported), self.checkpoint()['world'])
        old = exported.read_bytes()
        with self.assertRaises(FileExistsError):
            self.bridge.export_legacy(exported)
        self.assertEqual(exported.read_bytes(), old)
        self.bridge.close()
        with self.assertRaises(disk.BridgeError):
            Bridge.create(self.path)
        self.assertEqual(self.path.read_bytes(), before)

    def test_historical_import_preserves_original_and_does_not_adopt(self):
        sources = sorted((ROOT / 'tests/fixtures').glob('*.json'))
        for index, source in enumerate(sources):
            with self.subTest(source=source.name):
                before = source.read_bytes()
                path = self.path.parent / f'import-{index}.json'
                with Bridge.import_legacy(source, path) as bridge:
                    public = bridge.state()
                    prepared = engine.load_career(source)
                    self.assertEqual(disk.decode_json(path.read_text())['world'], prepared)
                    for version, name in [('navigation_version', 'navigation'), ('daily_life_version', 'daily_life')]:
                        if version not in prepared:
                            self.assertEqual(public['state']['systems'][name], 'not_adopted')
                self.assertEqual(source.read_bytes(), before)
        with self.assertRaises(disk.BridgeError):
            Bridge.import_legacy(sources[0], sources[0])

    def test_exhausted_actions_and_day_transition_preserve_budgets(self):
        world = engine.create_career(42)
        engine.execute_command(world, 'settle_in')
        engine.advance_day(world)
        engine.execute_command(world, 'travel', destination='p032', mode='walk')
        engine.execute_command(world, 'join', faction='Harbor Syndicate')
        for _ in range(3):
            engine.execute_command(world, 'job', kind='courier')
        source = self.path.parent / 'spent.json'
        engine.save_career(world, source)
        self.bridge.close()
        self.bridge = Bridge.import_legacy(source, self.path.parent / 'spent-bridge.json')
        self.path = self.path.parent / 'spent-bridge.json'
        self.assertEqual(self.bridge.state()['state']['budgets']['actions_remaining'], 0)
        self.unchanged_rejection(self.request('choose', choice_id=CHOICE, option_id='work'), 'COMMAND_REJECTED')
        response = self.send('wait')
        self.assertEqual(response['state']['budgets']['actions_remaining'], 3)
        self.assertEqual(response['state']['budgets']['travel_units_remaining'], 18)

    def test_mobility_pending_and_active_quotes_reuse_existing_journey(self):
        self.send('enable_mobility', overlay_id=OVERLAY_ID, request_id='mobility-adoption')
        self.assertEqual(self.bridge.state()['state']['systems']['mobility'], 'pending')
        self.send('wait')
        quote = self.bridge.route('p032', 'walk')['quote']
        self.assertEqual(quote['command'], 'journey')
        self.assertNotIn('graph', quote)
        self.send(quote['command'], **quote['arguments'])
        self.assertEqual(self.bridge.state()['state']['location']['id'], 'goon.poi.p032')

    def test_two_seed_thirty_day_restart_and_replay(self):
        for seed in (17, 93):
            with self.subTest(seed=seed):
                path = self.path.parent / f'campaign-{seed}.json'
                replay = engine.create_career(seed)
                with Bridge.create(path, seed) as bridge:
                    start = bridge.state()
                for day in range(30):
                    with Bridge.open(path) as bridge:
                        request = dict(protocol_version=1, career_id=start['career_id'], lineage_id=start['lineage_id'],
                                       request_id=f'day-{day}', expected_revision=day, command='wait', arguments={})
                        bridge.execute(request)
                        bridge.execute(request)
                    engine.advance_day(replay)
                    checkpoint = disk.validate(disk.decode_json(path.read_text()))
                    self.assertEqual(checkpoint['world'], replay)
                self.assertEqual(checkpoint['revision'], 30)

    def test_actual_process_exit_before_and_after_primary_publication(self):
        code = '''
import json, os, sys
from pathlib import Path
from unittest.mock import patch
import bridge_checkpoint as disk
from engine_bridge import Bridge
path, phase = Path(sys.argv[1]), sys.argv[2]
request = json.loads(sys.argv[3])
replace = disk.os.replace
def crash(source, target):
    primary = Path(target) == path
    if primary and phase == 'before':
        os._exit(71)
    replace(source, target)
    if primary and phase == 'after':
        os._exit(72)
with Bridge.open(path) as bridge:
    with patch('bridge_checkpoint.os.replace', side_effect=crash):
        bridge.execute(request)
raise RuntimeError('crash injection did not run')
'''
        for phase, exit_code in [('before', 71), ('after', 72)]:
            with self.subTest(phase=phase):
                path = self.path.parent / f'process-{phase}.json'
                with Bridge.create(path) as bridge:
                    state = bridge.state()
                request = dict(protocol_version=1, career_id=state['career_id'], lineage_id=state['lineage_id'],
                               request_id='crashed-request', expected_revision=0, command='wait', arguments={})
                result = subprocess.run([sys.executable, '-B', '-c', code, str(path), phase, json.dumps(request)],
                                        cwd=ROOT, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, exit_code, result.stderr)
                with Bridge.open(path) as recovered:
                    status = recovered.operation('crashed-request')
                    self.assertEqual(status['operation_status'], 'not_found' if phase == 'before' else 'committed')
                    self.assertEqual(status['state']['day'], 0 if phase == 'before' else 1)
                    answer = recovered.execute(request)
                    self.assertEqual(answer['state']['day'], 1)
                    self.assertEqual(answer['duplicate'], phase == 'after')

    def test_initial_creation_and_import_never_replace_an_existing_file(self):
        with self.assertRaises(disk.BridgeError):
            self.bridge.export_legacy(Path(str(self.path) + '.bak'))
        self.assertFalse(Path(str(self.path) + '.bak').exists())
        source = ROOT / 'tests/fixtures/m010.json'
        before = source.read_bytes()
        occupied = self.path.parent / 'occupied.json'
        occupied.write_text('preserve me', encoding='utf-8')
        with self.assertRaises(disk.BridgeError):
            Bridge.import_legacy(source, occupied)
        self.assertEqual(occupied.read_text(), 'preserve me')
        self.assertEqual(source.read_bytes(), before)
        # Also protect a path that appears between the existence check and link.
        target = self.path.parent / 'race.json'
        link = disk.os.link
        def late_creation(staged, destination):
            target.write_text('another writer', encoding='utf-8')
            return link(staged, destination)
        with patch('bridge_checkpoint.os.link', side_effect=late_creation):
            with self.assertRaises(FileExistsError):
                Bridge.create(target)
        self.assertEqual(target.read_text(), 'another writer')

    def test_imports_of_navigation_life_and_incident_historical_saves(self):
        for index, name in enumerate(('tests/fixtures/m014/career.json',
                                      'tests/mobility_fixtures/m015/career.json',
                                      'tests/institution_fixtures/m018_notice.json')):
            source = ROOT / name
            before = source.read_bytes()
            path = self.path.parent / f'subsystem-{index}.json'
            with self.subTest(source=name), Bridge.import_legacy(source, path) as bridge:
                expected = engine.load_career(source)
                self.assertEqual(disk.decode_json(path.read_text())['world'], expected)
                bridge.state()
                self.assertEqual(disk.decode_json(path.read_text())['world'], expected)
            self.assertEqual(source.read_bytes(), before)

    def test_import_source_cannot_be_a_future_checkpoint_backup_or_lock(self):
        original = (ROOT / 'tests/fixtures/m010.json').read_bytes()
        for suffix in ('.bak', '.lock'):
            target = self.path.parent / ('alias' + suffix.replace('.', '-') + '.json')
            source = Path(str(target) + suffix)
            source.write_bytes(original)
            with self.subTest(suffix=suffix), self.assertRaises(disk.BridgeError):
                with Bridge.import_legacy(source, target):
                    pass
            self.assertFalse(target.exists())
            self.assertEqual(source.read_bytes(), original)

    def test_partial_handler_failure_cannot_publish_candidate_changes(self):
        request = self.request('wait')
        def fail(world, command, **args):
            world['player']['cash'] += 9999
            world['events'].clear()
            raise ValueError('PRIVATE_ENGINE_DIAGNOSTIC')
        with patch('engine_bridge.game_service.execute_command', side_effect=fail):
            self.unchanged_rejection(request, 'COMMAND_REJECTED')

    def test_home_work_projection_and_execution_use_two_actions(self):
        self.bridge.close()
        self.path = self.path.parent / 'home-work.json'
        self.bridge = Bridge.create(self.path, seed=41)  # This existing roster has supplies.
        self.ready()
        self.send('choose', choice_id=CHOICE, option_id='work')
        self.send('travel', destination='home', mode='walk')
        self.send('enable_ordinary')
        self.send('wait')
        self.send('travel', destination='p032', mode='walk')
        self.send('choose', choice_id='goon.choice.0.crossroads', option_id='lawful')
        self.send('travel', destination='home', mode='walk')
        self.send('wait')
        state = self.bridge.state()['state']
        row = next(r for r in state['opportunities'] if r['id'] == 'goon.ordinary.batch.0')
        option = next(o for o in row['options'] if o['id'] == 'work')
        self.assertEqual((option['action_cost'], option['availability']), (2, 'available'))
        result = self.send(row['command'], **option['arguments'])['state']
        self.assertEqual(result['player']['cash'], state['player']['cash'] + 24)
        self.assertEqual(result['budgets']['actions_remaining'], 1)
        self.assertEqual(result['budgets']['travel_units_remaining'], 18)


    def housing_fixture(self, cash):
        self.bridge.close()
        source = self.path.parent / f'seed-{cash}.json'
        world = engine.create_career()
        world['player']['cash'] = cash
        engine.save_career(world, source)
        self.path = self.path.parent / f'housing-{cash}.json'
        self.bridge = Bridge.import_legacy(source, self.path)
        self.send('settle_in')
        self.send('wait')

    def settlement(self, day, kind, paid, credit, cash, arrears, prepaid, next_due_day):
        return dict(day=day, kind=kind, paid=paid, credit_applied=credit,
                    balance_after=dict(cash=str(cash), arrears=arrears, prepaid=prepaid, next_due_day=next_due_day))

    def settlement_read(self, response, expected):
        receipt = response['receipt']
        result = self.bridge.housing_operation(receipt['request_id'])
        self.assertEqual(result, dict(protocol_version=1, career_id=response['career_id'],
                                      lineage_id=response['lineage_id'], revision=self.bridge.state()['revision'],
                                      receipt=receipt, settlements=expected))
        return result

    def test_housing_full_and_partial_arrears_payment_and_new_prepayment(self):
        for opening_cash, paid, arrears, cash in ((15, 15, 0, 5), (5, 20, 5, 0)):
            with self.subTest(opening_cash=opening_cash):
                self.housing_fixture(opening_cash)
                for _ in range(7):
                    self.send('wait')
                self.send('travel', destination='p032', mode='walk')
                self.send('choose', choice_id='goon.choice.1.opening_shift', option_id='work')
                self.send('travel', destination='p031', mode='walk')
                before = self.checkpoint()['world']['daily_life']
                response = self.send('pay_room')
                expected = self.settlement(8, 'arrears_payment', paid, 0, cash, arrears, 0, 14)
                self.settlement_read(response, [expected])
                self.assertEqual(self.bridge.housing()['latest_settlement'], expected)
                after = self.checkpoint()['world']['daily_life']
                self.assertEqual(len(after['transactions']), len(before['transactions']) + 1)
                self.assertEqual(len(after['housing']['history']), len(before['housing']['history']) + 1)
                self.assertEqual(after['transactions'][-1]['amount'], -paid)
                self.assertEqual(after['transactions'][-1]['command_id'], response['receipt']['command_sequence'])
                if arrears == 0:
                    self.assertEqual(self.bridge.housing()['pay_room'], 'eligible')
                    prepay = self.send('pay_room')
                    self.settlement_read(prepay, [self.settlement(8, 'prepay', 5, 0, 0, 0, 5, 14)])

    def test_housing_prepaid_due_and_concurrent_payment_recovery(self):
        self.send('settle_in')
        self.send('wait')
        request = self.request('pay_room')
        changed = dict(request, command='wait')
        stale = dict(request, request_id='new-payment')
        backup = Path(str(self.path) + '.bak')
        with ThreadPoolExecutor(2) as threads:
            copies = list(threads.map(self.bridge.execute, (request, request)))
        self.assertEqual(sorted(r['duplicate'] for r in copies), [False, True])
        self.assertEqual(copies[0]['receipt'], copies[1]['receipt'])
        self.assertEqual(self.bridge.state()['revision'], 3)
        self.assertEqual(len(self.checkpoint()['world']['daily_life']['transactions']), 1)
        self.unchanged_rejection(changed, 'REQUEST_ID_REUSED')
        self.unchanged_rejection(stale, 'STALE_REVISION')
        self.unchanged_rejection(self.request('pay_room'), 'COMMAND_REJECTED')
        self.assertEqual(self.bridge.housing()['pay_room'], 'no_payable_balance')
        for _ in range(5):
            neighbor = self.send('wait')
        due = self.send('wait')
        self.settlement_read(neighbor, [])
        expected_due = self.settlement(7, 'due', 0, 30, 10, 0, 0, 14)
        self.settlement_read(due, [expected_due])
        self.assertEqual(self.bridge.housing()['latest_settlement'], expected_due)
        self.settlement_read(self.send('wait'), [])
        before, old_backup = self.path.read_bytes(), backup.read_bytes()
        self.bridge.close()
        self.bridge = Bridge.open(self.path)
        duplicate = self.bridge.execute(request)
        self.assertTrue(duplicate['duplicate'])
        self.assertEqual(duplicate['receipt'], copies[0]['receipt'])
        expected_prepay = self.settlement(1, 'prepay', 30, 0, 10, 0, 30, 7)
        self.settlement_read(duplicate, [expected_prepay])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(backup.read_bytes(), old_backup)

    def test_housing_automatic_cash_and_zero_cash_dues_with_carried_arrears(self):
        for starting_cash, next_cash, owed in ((0, 0, 30), (40, 10, 0)):
            with self.subTest(cash=starting_cash):
                self.housing_fixture(starting_cash)
                if starting_cash == 0:
                    denied = self.request('pay_room')
                    self.unchanged_rejection(denied, 'COMMAND_REJECTED')
                    self.assertEqual(self.bridge.operation(denied['request_id'])['operation_status'], 'not_found')
                    with self.assertRaises(disk.BridgeError) as detail:
                        self.bridge.housing_operation(denied['request_id'])
                    self.assertEqual((detail.exception.status, detail.exception.code), (404, 'NOT_FOUND'))
                for _ in range(6):
                    due = self.send('wait')
                self.settlement_read(due, [self.settlement(7, 'due', starting_cash - next_cash, 0,
                                                           next_cash, owed, 0, 14)])
                self.assertEqual(self.checkpoint()['world']['daily_life']['transactions'][-1]['command_id'], None)
                if starting_cash == 0:
                    for day in (14, 21, 28):
                        for _ in range(7):
                            due = self.send('wait')
                        self.settlement_read(due, [self.settlement(day, 'due', 0, 0, 0, 30, 0, day + 7)])
                        housing = self.checkpoint()['world']['daily_life']['housing']
                        self.assertEqual(housing['history'][-1]['assessed'], 0)
                        self.assertEqual(housing['arrears'], 30)

    def test_housing_ignores_maintenance_and_returns_no_unrelated_settlement(self):
        fresh = self.bridge.state()
        self.assertEqual(self.bridge.housing(), dict(protocol_version=1, career_id=fresh['career_id'],
                                                     lineage_id=fresh['lineage_id'], revision=0,
                                                     pay_room='not_adopted', latest_settlement=None))
        self.settlement_read(self.send('wait'), [])
        self.housing_fixture(0)
        for _ in range(6):
            due = self.send('wait')
        maintenance = self.send('choose', choice_id='goon.choice.room.1', option_id='help')
        self.assertEqual(maintenance['state']['housing']['arrears'], 20)
        self.settlement_read(maintenance, [])
        self.assertEqual(self.bridge.housing()['latest_settlement'], self.settlement_read(
            due, [self.settlement(7, 'due', 0, 0, 0, 30, 0, 14)])['settlements'][0])

    def test_ambiguous_housing_details_leave_original_operation_committed(self):
        self.send('settle_in')
        for _ in range(7):
            due = self.send('wait')
        before = self.checkpoint()
        sequence = due['receipt']['command_sequence']
        ident = due['receipt']['request_id']

        def misplaced_event(world):
            events = world['events']
            housing = next(e for e in events if e['kind'] == 'life_housing')
            events.remove(housing)
            closing = next(i for i, e in enumerate(events) if e.get('kind') == 'player_command'
                           and e.get('command_id') == sequence)
            events.insert(closing + 1, housing)

        def retag_transaction(world):
            for row in world['daily_life']['transactions'] + world['events']:
                if row.get('id') == 'goon.transaction.1':
                    row['command_id'] = sequence

        for label, mutate in (
            ('misplaced receipt event', misplaced_event), ('non-null due command', retag_transaction),
            ('missing transaction', lambda w: w['daily_life']['transactions'].clear()),
            ('duplicated transaction', lambda w: w['daily_life']['transactions'].extend(w['daily_life']['transactions'])),
            ('wrong cycle', lambda w: w['daily_life']['housing']['history'][0].update(source_id='invalid')),
        ):
            with self.subTest(label=label):
                world = deepcopy(before['world'])
                mutate(world)
                if mutate in (misplaced_event, retag_transaction):
                    disk.validate(dict(before, world=world, world_hash=disk.digest(world)))
                with patch.dict(self.bridge._checkpoint, world=world):
                    with self.assertRaises(disk.BridgeError) as caught:
                        self.bridge.housing_operation(ident)
                    self.assertEqual((caught.exception.status, caught.exception.code, str(caught.exception)),
                                     (503, 'INVALID_CHECKPOINT', 'Housing settlement details are unavailable.'))
                    original = self.bridge.operation(ident)
                    self.assertEqual(original['operation_status'], 'committed')
                    self.assertEqual(original['receipt'], due['receipt'])
        self.assertEqual(self.checkpoint(), before)

        self.housing_fixture(40)
        paid = self.send('pay_room')
        world = deepcopy(self.checkpoint()['world'])
        world['daily_life']['transactions'][-1]['command_id'] -= 1
        with patch.dict(self.bridge._checkpoint, world=world):
            with self.assertRaises(disk.BridgeError) as caught:
                self.bridge.housing_operation(paid['receipt']['request_id'])
            self.assertEqual(caught.exception.code, 'INVALID_CHECKPOINT')

    def test_housing_recovers_publication_in_memory_without_writing(self):
        self.send('settle_in')
        self.send('wait')
        request = self.request('pay_room')
        replace = disk.os.replace

        def lost_ack(source, target):
            replace(source, target)
            if Path(target) == self.path:
                raise OSError('acknowledgment lost after replacement')

        with patch('bridge_checkpoint.os.replace', side_effect=lost_ack):
            with self.assertRaises(disk.BridgeError) as caught:
                self.bridge.execute(request)
            self.assertEqual(caught.exception.code, 'OUTCOME_UNKNOWN')
        with patch.object(self.bridge._store, 'read', side_effect=OSError('unreadable')):
            for read in (self.bridge.housing, lambda: self.bridge.housing_operation(request['request_id'])):
                with self.assertRaises(disk.BridgeError) as caught:
                    read()
                self.assertEqual(caught.exception.code, 'OUTCOME_UNKNOWN')
        before = self.path.read_bytes()
        backup = Path(str(self.path) + '.bak')
        old_backup = backup.read_bytes()
        with patch.object(self.bridge._store, 'write', side_effect=AssertionError('read attempted to write')):
            expected = self.settlement(1, 'prepay', 30, 0, 10, 0, 30, 7)
            self.assertEqual(self.bridge.housing()['latest_settlement'], expected)
            recovered = self.bridge.housing_operation(request['request_id'])
            self.assertEqual(recovered['settlements'], [expected])
        self.bridge.close()
        self.bridge = Bridge.open(self.path)
        self.assertEqual(self.bridge.housing_operation(request['request_id']), recovered)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(backup.read_bytes(), old_backup)

    def test_housing_reads_preserve_deterministic_checkpoint_bytes(self):
        commands = ('settle_in', 'wait', 'pay_room') + ('wait',) * 7
        starting = self.path.read_bytes()
        comparison = self.path.with_name('without-reads.json')
        comparison.write_bytes(starting)
        with Bridge.open(comparison) as without:
            for command in commands:
                request = self.request(command)
                self.assertEqual(self.bridge.execute(request), without.execute(request))
                self.bridge.housing()
                self.bridge.housing_operation(request['request_id'])
            self.assertEqual(self.bridge.state(), without.state())
        self.assertEqual(self.path.read_bytes(), comparison.read_bytes())
        self.assertEqual(Path(str(self.path) + '.bak').read_bytes(), Path(str(comparison) + '.bak').read_bytes())

    def test_housing_legacy_import_keeps_history_and_exact_large_balance(self):
        legacy = ROOT / 'tests' / 'fixtures' / 'm002.json'
        original = legacy.read_bytes()
        with Bridge.import_legacy(legacy, self.path.with_name('old.json')) as imported:
            self.assertEqual(imported.housing()['pay_room'], 'not_adopted')
            self.assertIsNone(imported.housing()['latest_settlement'])
            self.assertEqual(imported.housing()['revision'], 0)
        self.assertEqual(legacy.read_bytes(), original)

        cash = 9007199254740993
        self.housing_fixture(cash + 30)
        paid = self.send('pay_room')
        expected = self.settlement(1, 'prepay', 30, 0, cash, 0, 30, 7)
        self.settlement_read(paid, [expected])
        saved = self.path.with_name('housing-history.json')
        self.bridge.export_legacy(saved)
        original = saved.read_bytes()
        with Bridge.import_legacy(saved, self.path.with_name('imported-history.json')) as imported:
            self.assertEqual(imported.housing()['latest_settlement'], expected)
            self.assertEqual(imported.housing()['revision'], 0)
            with self.assertRaises(disk.BridgeError) as caught:
                imported.housing_operation(paid['receipt']['request_id'])
            self.assertEqual(caught.exception.code, 'NOT_FOUND')
        self.assertEqual(saved.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
