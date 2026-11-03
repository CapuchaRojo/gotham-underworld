"""M012 heat, job exposure, legal choices, and multi-day outcomes."""
from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import gameplay
from career_state import validate
from consequence_engine import investigate
from game_service import (actions_remaining, advance_day, create_career,
                          execute_command, load_career, save_career)
from legal_engine import begin_day, change_heat
from legal_state import attention, report


class LegalConsequenceTests(unittest.TestCase):
    def world(self, *, heat=0, cash=100, evidence=None):
        world = create_career(42)
        execute_command(world, 'join', faction='Harbor Syndicate')
        world['player']['heat'] = heat
        world['player']['cash'] = cash
        if evidence is not None:
            world['cases'].append({'id': 1, 'crime': 'collection intimidation', 'suspect': 'Rookie',
                                   'status': 'pending', 'evidence': evidence, 'witnessed': True,
                                   'source_attempt': 0, 'investigation_days': 0,
                                   'last_investigated_day': 0})
            world['job_attempts'] = 1
        return world

    def test_heat_tier_boundaries_and_effects(self):
        for heat, tier, bonus, evidence in ((0, 'low', 0, 0), (19, 'low', 0, 0),
                (20, 'elevated', 5, 0), (49, 'elevated', 5, 0), (50, 'high', 10, 1),
                (79, 'high', 10, 1), (80, 'critical', 15, 1), (100, 'critical', 15, 1)):
            with self.subTest(heat=heat):
                view = attention(heat)
                self.assertEqual((view['tier'], view['risk_bonus'], view['evidence_bonus']), (tier, bonus, evidence))
        self.assertEqual(attention(1000)['heat'], 100)
        self.assertEqual(attention(-1)['heat'], 0)

    def test_heat_change_clamps_and_records_actual_delta(self):
        world = self.world(heat=95)
        result = change_heat(world, 50, 'test')
        self.assertEqual((result['before'], result['after'], result['delta']), (95, 100, 5))
        result = change_heat(world, -500, 'test')
        self.assertEqual((result['after'], result['delta']), (0, -100))
        before = deepcopy(world)
        self.assertIsNone(change_heat(world, 0, 'test'))
        self.assertEqual(world, before)

    def test_heat_modifies_chance_without_rerolling_job(self):
        cold, hot = self.world(), self.world(heat=80)
        a = execute_command(cold, 'job', kind='collection')['result']
        b = execute_command(hot, 'job', kind='collection')['result']
        self.assertEqual(a['roll'], b['roll'])
        self.assertEqual(a['witness_roll'], b['witness_roll'])
        self.assertEqual(b['failure_chance'] - a['failure_chance'], 15)
        self.assertEqual(b['witness_chance'] - a['witness_chance'], 15)
        self.assertEqual(b['heat_tier'], 'critical')
        self.assertGreater(hot['player']['heat'] - 80, cold['player']['heat'])

    def test_jobs_have_distinct_exposure_and_risk_cap(self):
        courier, collection = self.world(heat=100), self.world(heat=100)
        courier['player']['reputation']['Harbor Syndicate'] = -1000
        a = execute_command(courier, 'job', kind='courier')['result']
        b = execute_command(collection, 'job', kind='collection')['result']
        self.assertEqual(a['failure_chance'], 75)
        self.assertEqual((a['witness_chance'], a['witnessed'], a['witness_roll']), (0, False, None))
        self.assertFalse(courier['cases'])
        self.assertGreater(b['witness_chance'], 0)
        self.assertLessEqual(collection['player']['heat'], 100)

    def test_police_pressure_requires_a_documented_case(self):
        clean = self.world(heat=100)
        advance_day(clean)
        self.assertFalse(clean['cases'])
        self.assertFalse(clean['player']['arrested'])
        self.assertFalse(any(e['kind'] == 'police_attention' for e in clean['events']))
        cold, hot = self.world(heat=20, evidence=1), self.world(heat=80, evidence=1)
        advance_day(cold); advance_day(hot)
        self.assertEqual(cold['cases'][0]['status'], 'pending')
        self.assertEqual(hot['cases'][0]['status'], 'convicted')
        self.assertTrue(any(e['kind'] == 'police_attention' and e['case_ids'] == [1] for e in hot['events']))
        validate(hot)

    def test_legal_daily_tick_and_investigation_are_idempotent(self):
        world = self.world(heat=80, evidence=1)
        world['day'] = 1
        pressure, deferred = begin_day(world)
        investigate(world, pressure=pressure, deferred_cases=deferred)
        before = deepcopy(world)
        begin_day(world)
        investigate(world, pressure=pressure, deferred_cases=deferred)
        self.assertEqual(world, before)

    def test_lay_low_costs_action_not_cash_and_keeps_evidence(self):
        world = self.world(heat=20, cash=0, evidence=1)
        execute_command(world, 'lay_low')
        self.assertEqual(world['player']['heat'], 8)
        self.assertEqual(world['player']['cash'], 0)
        self.assertEqual(world['cases'][0]['evidence'], 1)
        self.assertEqual(actions_remaining(world), 2)
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, 'once per day'):
            execute_command(world, 'lay_low')
        self.assertEqual(world, before)

    def test_zero_cash_high_heat_has_a_recovery_path(self):
        world = self.world(heat=100, cash=0)
        for _ in range(8):
            if world['player']['heat']:
                execute_command(world, 'lay_low')
            advance_day(world)
        self.assertEqual(world['player']['heat'], 0)
        self.assertFalse(world['player']['arrested'])

    def test_quiet_day_decay_requires_a_complete_crime_free_day(self):
        world = self.world(heat=20)
        world['legal']['last_crime_day'] = 0
        advance_day(world)
        self.assertEqual(world['player']['heat'], 20)
        advance_day(world)
        self.assertEqual(world['player']['heat'], 18)

    def test_cooperation_adds_evidence_and_reduces_court_fine(self):
        world = self.world(heat=20, evidence=1)
        execute_command(world, 'cooperate', case_id='1')
        self.assertEqual(world['cases'][0]['evidence'], 2)
        self.assertEqual(world['player']['heat'], 12)
        self.assertEqual(world['player']['cash'], 100)
        advance_day(world)
        record = world['legal']['record'][0]
        self.assertEqual((record['outcome'], record['fine_assessed'], record['fine_paid']), ('convicted', 30, 30))
        self.assertEqual(world['player']['cash'], 70)
        self.assertEqual(world['player']['custody'], 'free')
        self.assertEqual(record['response'], 'cooperate')
        validate(world)

    def test_weak_contest_defers_npc_and_police_then_dismisses(self):
        world = self.world(heat=100, evidence=1)
        world['people']['Detective Vale']['relationship']['suspicion'] = 100
        execute_command(world, 'contest', case_id='1')
        self.assertEqual(world['player']['cash'], 80)
        advance_day(world)
        self.assertEqual(world['cases'][0]['evidence'], 1)
        self.assertEqual(world['cases'][0]['status'], 'pending')
        validate(world)
        advance_day(world)
        self.assertEqual(world['cases'][0]['status'], 'dismissed')
        self.assertEqual(world['legal']['record'][0]['fine_paid'], 0)
        self.assertFalse(world['player']['arrested'])
        self.assertEqual(world['legal']['responses']['1']['review_day'], 2)
        validate(world)

    def test_strong_contest_is_denied_without_erasing_evidence(self):
        world = self.world(heat=20, evidence=2)
        execute_command(world, 'contest', case_id='1')
        advance_day(world); advance_day(world)
        self.assertEqual(world['cases'][0]['status'], 'convicted')
        self.assertEqual(world['player']['cash'], 30)
        self.assertEqual(world['legal']['record'][0]['fine_paid'], 50)
        self.assertTrue(any(e['kind'] == 'legal_review' and e['outcome'] == 'denied' for e in world['events']))
        validate(world)

    def test_acceptance_resolves_immediately_without_debt(self):
        for cash in (0, 10, 100):
            world = self.world(heat=20, cash=cash, evidence=1)
            result = execute_command(world, 'accept', case_id='1')
            self.assertEqual(world['day'], 0)
            self.assertEqual(world['player']['cash'], max(0, cash - 35))
            self.assertEqual(world['player']['heat'], 10)
            self.assertEqual(world['player']['custody'], 'free')
            self.assertEqual(world['cases'][0]['status'], 'convicted')
            self.assertEqual(result['result']['fine_paid'], min(cash, 35))
            self.assertEqual(actions_remaining(world), 2)
            validate(world)

    def test_acceptance_of_loaded_charged_case_restores_free_custody(self):
        world = self.world(heat=20, evidence=3)
        world['cases'][0]['status'] = 'charged'
        world['player'].update(arrested=True, custody='pretrial')
        execute_command(world, 'accept', case_id='1')
        self.assertFalse(world['player']['arrested'])
        self.assertEqual(world['player']['custody'], 'free')
        validate(world)

    def test_default_court_remains_available_without_player_response(self):
        world = self.world(evidence=1)
        advance_day(world); advance_day(world)
        self.assertEqual(world['cases'][0]['status'], 'convicted')
        self.assertEqual(world['legal']['record'][0]['fine_assessed'], 50)
        self.assertEqual(world['legal']['record'][0]['response'], 'none')

    def test_legal_rejections_are_atomic(self):
        world = self.world(heat=20, cash=0, evidence=1)
        commands = [('contest', {'case_id': '1'}), ('accept', {'case_id': '999'}),
                    ('cooperate', {'case_id': '-1'}), ('contest', {'case_id': 'bad'}),
                    ('accept', {'case_id': 1}), ('lay_low', {'extra': 'argument'})]
        for command, arguments in commands:
            before = deepcopy(world)
            with self.subTest(command=command, arguments=arguments), self.assertRaises(ValueError):
                execute_command(world, command, **arguments)
            self.assertEqual(world, before)
        world['player']['heat'] = 0
        before = deepcopy(world)
        with self.assertRaises(ValueError):
            execute_command(world, 'lay_low')
        self.assertEqual(world, before)

    def test_only_one_committed_response_per_case(self):
        world = self.world(heat=20, evidence=1)
        execute_command(world, 'cooperate', case_id='1')
        for choice in ('cooperate', 'contest', 'accept'):
            before = deepcopy(world)
            with self.assertRaisesRegex(ValueError, 'already committed'):
                execute_command(world, choice, case_id='1')
            self.assertEqual(world, before)

    def test_exhausted_legal_action_does_not_mutate(self):
        world = self.world(heat=20, evidence=1)
        for _ in range(3):
            execute_command(world, 'job', kind='courier')
        before = deepcopy(world)
        for command, args in [('lay_low', {}), ('cooperate', {'case_id': '1'}),
                              ('contest', {'case_id': '1'}), ('accept', {'case_id': '1'})]:
            with self.assertRaisesRegex(ValueError, 'exhausted'):
                execute_command(world, command, **args)
            self.assertEqual(world, before)

    def test_detained_and_resolved_cases_reject_investigative_responses(self):
        world = self.world(evidence=3)
        world['cases'][0]['status'] = 'charged'
        world['player'].update(arrested=True, custody='pretrial')
        before = deepcopy(world)
        for command, args in [('lay_low', {}), ('cooperate', {'case_id': '1'}), ('contest', {'case_id': '1'})]:
            with self.assertRaises(ValueError):
                execute_command(world, command, **args)
            self.assertEqual(world, before)

    def test_legal_report_is_detached_and_does_not_prepare(self):
        world = self.world(evidence=1)
        before = deepcopy(world)
        view = report(world)
        view['profile']['record'].append({'edited': True})
        view['cases'][0]['evidence'] = 999
        self.assertEqual(world, before)
        world.pop('legal'); world.pop('legal_version')
        before = deepcopy(world)
        self.assertIsNone(report(world)['profile'])
        self.assertEqual(world, before)

    def test_m011_save_migrates_without_replay_or_action_refresh(self):
        path = Path(__file__).parent / 'fixtures' / 'career_m011.json'
        old = json.loads(path.read_text(encoding='utf-8'))
        world = load_career(path)
        for key in old:
            self.assertEqual(world[key], old[key])
        self.assertEqual(world['legal_version'], 1)
        self.assertEqual(world['legal']['record'][0]['response'], 'historical')
        self.assertIsNone(world['legal']['record'][0]['day'])
        self.assertEqual(world['command_sequence'], old['command_sequence'])
        before = deepcopy(world)
        gameplay.prepare(world)
        self.assertEqual(world, before)

    def test_legacy_large_heat_loads_and_normalizes_only_on_success(self):
        world = self.world(heat=250)
        for key in ('legal', 'legal_version'):
            world.pop(key)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            path.write_text(json.dumps(world), encoding='utf-8')
            restored = load_career(path)
        self.assertEqual(restored['player']['heat'], 250)
        before = deepcopy(restored)
        with self.assertRaises(ValueError):
            execute_command(restored, 'cooperate', case_id='999')
        self.assertEqual(restored, before)
        execute_command(restored, 'lay_low')
        self.assertEqual(restored['player']['heat'], 88)
        self.assertTrue(any(e.get('cause') == 'legacy_heat_normalization' for e in restored['events']))

    def test_save_resume_preserves_pending_review_and_outcome(self):
        for choice, outcome, fine in (('contest', 'dismissed', 0), ('cooperate', 'convicted', 30), ('accept', 'convicted', 35)):
            with self.subTest(choice=choice), tempfile.TemporaryDirectory() as folder:
                a = self.world(heat=80, evidence=1)
                execute_command(a, choice, case_id='1')
                if choice == 'contest':
                    advance_day(a)
                path = Path(folder) / 'career.json'
                save_career(a, path)
                b = load_career(path)
                self.assertEqual(a, b)
                advance_day(a); advance_day(b)
                self.assertEqual(a, b)
                self.assertEqual(a['cases'][0]['status'], outcome)
                self.assertEqual(a['legal']['record'][0]['fine_paid'], fine)
                save_career(a, path)
                self.assertEqual(load_career(path), a)

    def test_legal_extension_data_survives_round_trip(self):
        world = self.world(heat=20, evidence=1)
        execute_command(world, 'accept', case_id='1')
        world['legal']['extension'] = {'example_id': 'extension.test'}
        world['legal']['record'][0]['extension'] = {'note': 'retained'}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(world, path)
            self.assertEqual(load_career(path), world)

    def test_malformed_legal_state_is_rejected_before_play(self):
        mutations = [lambda w: w.update(legal_version=999), lambda w: w.update(legal_version=True),
                     lambda w: w.pop('legal'), lambda w: w.pop('legal_version'),
                     lambda w: w['legal'].update(record=None),
                     lambda w: w['legal'].update(last_lay_low_day=1),
                     lambda w: w['legal'].update(responses={'999': {}}),
                     lambda w: w['legal'].update(record=[{'case_id': 99}])]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            for mutate in mutations:
                world = self.world(evidence=1); mutate(world)
                path.write_text(json.dumps(world), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'legal'):
                    load_career(path)

    def test_contested_review_invariants_and_duplicate_records_rejected(self):
        world = self.world(evidence=1)
        execute_command(world, 'contest', case_id='1')
        for field, value in [('review_day', 1), ('reviewed', True), ('action', 'unknown')]:
            broken = deepcopy(world); broken['legal']['responses']['1'][field] = value
            with self.assertRaises(ValueError):
                validate(broken)
        advance_day(world); advance_day(world)
        world['legal']['record'].append(deepcopy(world['legal']['record'][0]))
        with self.assertRaisesRegex(ValueError, 'unique'):
            validate(world)

    def test_legal_history_cannot_be_reloaded_without_its_profile(self):
        world = self.world(evidence=1)
        execute_command(world, 'contest', case_id='1')
        world.pop('legal'); world.pop('legal_version')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            path.write_text(json.dumps(world), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'legal history'):
                load_career(path)

    def test_many_cases_and_responses_have_unique_consistent_records(self):
        world = self.world(heat=80, evidence=1)
        for case_id in (2, 3):
            case = deepcopy(world['cases'][0]); case['id'] = case_id
            world['cases'].append(case)
        execute_command(world, 'contest', case_id='1')
        execute_command(world, 'cooperate', case_id='2')
        execute_command(world, 'accept', case_id='3')
        for _ in range(4):
            advance_day(world)
            validate(world)
        records = world['legal']['record']
        self.assertEqual({r['case_id'] for r in records}, {1, 2, 3})
        self.assertEqual(len(records), 3)
        self.assertFalse(world['player']['arrested'])

    def test_legacy_daily_entry_honors_committed_review(self):
        world = self.world(heat=80, evidence=1)
        execute_command(world, 'contest', case_id='1')
        gameplay.next_day(world)
        self.assertEqual(world['cases'][0]['evidence'], 1)
        gameplay.next_day(world)
        self.assertEqual(world['cases'][0]['status'], 'dismissed')
        validate(world)

    def test_heat_and_outcome_event_tampering_is_rejected(self):
        world = self.world(heat=20, evidence=1)
        execute_command(world, 'accept', case_id='1')
        for kind, field, value in [('heat_change', 'delta', 999), ('legal_outcome', 'fine_paid', 99),
                                    ('legal_response', 'cash_cost', 99)]:
            broken = deepcopy(world)
            next(e for e in broken['events'] if e['kind'] == kind)[field] = value
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                validate(broken)

    def test_legal_record_cannot_mislabel_response_or_fine(self):
        world = self.world(evidence=1)
        execute_command(world, 'accept', case_id='1')
        for field, value in [('response', 'none'), ('fine_assessed', 50), ('fine_paid', 36)]:
            broken = deepcopy(world)
            broken['legal']['record'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(broken)

    def test_multi_month_legal_replay_and_disk_resume(self):
        a, b = self.world(heat=80), self.world(heat=80)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            for day in range(90):
                for world in (a, b):
                    execute_command(world, 'job', kind='collection' if day % 3 == 0 else 'courier')
                    pending = next((c for c in world['cases'] if c['status'] == 'pending' and
                                    str(c['id']) not in world['legal']['responses']), None)
                    if pending:
                        choice = ('contest', 'cooperate', 'accept')[(day // 3) % 3]
                        if choice == 'contest' and world['player']['cash'] < 20:
                            choice = 'accept'
                        execute_command(world, choice, case_id=str(pending['id']))
                    if world['player']['heat'] and actions_remaining(world):
                        execute_command(world, 'lay_low')
                    advance_day(world)
                    self.assertTrue(0 <= world['player']['heat'] <= 100)
                if day % 13 == 0:
                    save_career(b, path)
                    b = load_career(path)
                    validate(a); validate(b)
            self.assertEqual(a, b)
            self.assertTrue(a['legal']['record'])
            self.assertEqual({r['action'] for r in a['legal']['responses'].values()}, {'contest', 'cooperate', 'accept'})
            validate(a)

    def test_legal_choices_match_in_fresh_hashseed_processes(self):
        import os
        code = (
            'import hashlib,json; from game_service import create_career,execute_command,advance_day; '
            'from career_state import validate; w=create_career(42); '
            'execute_command(w,"join",faction="Harbor Syndicate"); '
            '[execute_command(w,"job",kind="collection") for _ in range(3)]; advance_day(w); '
            'c=next(c for c in w["cases"] if c["status"]=="pending"); '
            'execute_command(w,"contest",case_id=str(c["id"])); advance_day(w); advance_day(w); validate(w); '
            'print(hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest())'
        )
        digests = [subprocess.check_output([sys.executable, '-B', '-c', code],
                   cwd=Path(__file__).resolve().parents[1],
                   env=dict(os.environ, PYTHONHASHSEED=seed), text=True).strip()
                   for seed in ('1', '42')]
        self.assertEqual(digests[0], digests[1])

    def test_replay_legal_choices_has_no_global_rng_effect(self):
        state = random.getstate()
        a, b = self.world(heat=80, evidence=1), self.world(heat=80, evidence=1)
        for world in (a, b):
            execute_command(world, 'contest', case_id='1')
            execute_command(world, 'lay_low')
            advance_day(world); advance_day(world)
        self.assertEqual(a, b)
        self.assertEqual(random.getstate(), state)

    def test_actual_cli_legal_choice_and_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            world = self.world(heat=80, evidence=1)
            save_career(world, path)
            script = Path(__file__).resolve().parents[1] / 'gameplay.py'
            completed = subprocess.run([sys.executable, '-B', str(script), '--load', '--save', str(path)],
                                       input='legal\ncontest 1\nwait\nwait\nlegal\nquit\n',
                                       text=True, capture_output=True, cwd=folder)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('Case 1: dismissed', completed.stdout)
            self.assertEqual(load_career(path)['cases'][0]['status'], 'dismissed')


if __name__ == '__main__':
    unittest.main()
