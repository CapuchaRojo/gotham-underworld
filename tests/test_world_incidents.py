"""Mission 016: autonomous source, knowledge, choices, delegated effects and replay."""
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

from career_state import validate
import daily_life
from game_service import (actions_remaining, advance_day, create_career, execute_command,
                          incident_report, load_career, save_career)
import incident_content
import world_incidents as incidents


class WorldIncidentTests(unittest.TestCase):
    def start(self, seed=17):
        w = create_career(seed)
        execute_command(w, 'settle_in')
        advance_day(w)
        execute_command(w, 'enable_incidents')
        return w

    def until(self, w, day):
        while w['day'] < day:
            advance_day(w)

    def go(self, w):
        if w['navigation']['location_id'] != 'goon.poi.p032':
            execute_command(w, 'travel', destination='p032', mode='walk')

    def discover(self, w):
        self.go(w)
        execute_command(w, 'discover_incident', incident_id=w['incidents']['id'], channel='public_notice')

    def choose(self, w, stage, option):
        return execute_command(w, 'incident_choose', incident_id=w['incidents']['id'], stage=stage, option_id=option)

    def reject(self, w, command, **arguments):
        before, rng = deepcopy(w), random.getstate()
        with self.assertRaises(ValueError):
            execute_command(w, command, **arguments)
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)

    def work(self, delay=0, seed=17):
        w = self.start(seed)
        self.until(w, w['incidents']['information_day'] + delay)
        self.discover(w)
        self.choose(w, 'offer', 'accept')
        self.choose(w, 'work', 'verify')
        return w

    def test_explicit_adoption_no_refresh_or_unrelated_state_change(self):
        w = create_career()
        before = deepcopy(w)
        self.assertFalse(incident_report(w)['enabled'])
        self.assertEqual(w, before)
        self.reject(w, 'enable_incidents')
        execute_command(w, 'settle_in')
        self.reject(w, 'enable_incidents')
        advance_day(w)
        self.go(w)
        execute_command(w, 'choose', choice_id='goon.choice.0.opening_shift', option_id='work')
        before = deepcopy(w)
        execute_command(w, 'enable_incidents')
        for key in ('player', 'factions', 'cases', 'navigation', 'actions_used', 'day'):
            self.assertEqual(w[key], before[key])
        self.assertEqual(actions_remaining(w), 2)
        self.reject(w, 'enable_incidents')
        self.assertGreater(w['incidents']['occurrence_day'], w['day'])

    def test_occurrence_deterministic_across_seed_and_dictionary_order(self):
        seen = set()
        for seed in range(12):
            a, b = self.start(seed), self.start(seed)
            b = dict(reversed(list(b.items())))
            for _ in range(8):
                advance_day(a)
                advance_day(b)
            self.assertEqual(a, b)
            seen.add(a['incidents']['truth'])
            self.assertEqual(a['incidents']['world_status'], 'resolved')
        self.assertEqual(seen, set(incident_content.load()['causes']))

    def test_definition_dictionary_order_does_not_change_replay(self):
        expected = self.work()
        content = incident_content.load()
        content['causes'] = dict(reversed(list(content['causes'].items())))
        content['stages'] = dict(reversed(list(content['stages'].items())))
        with patch('world_incidents.load', side_effect=lambda: deepcopy(content)):
            actual = self.work()
            self.assertEqual(incident_report(actual), incident_report(expected))
        self.assertEqual(actual, expected)

    def test_historical_m014_career_can_explicitly_adopt_without_rewriting_history(self):
        w = load_career(Path(__file__).parent / 'fixtures/m014/career.json')
        history = deepcopy(w['events'])
        execute_command(w, 'travel', destination='home', mode='walk')
        execute_command(w, 'settle_in')
        advance_day(w)
        before = deepcopy(w)
        execute_command(w, 'enable_incidents')
        self.assertEqual(w['events'][:len(history)], history)
        for key in ('player', 'cases', 'factions', 'navigation', 'actions_used', 'job_attempts'):
            self.assertEqual(w[key], before[key])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'adopted.json'
            save_career(w, path)
            self.assertEqual(w, load_career(path))

    def test_world_occurs_and_resolves_without_discovery(self):
        w = self.start()
        self.until(w, w['incidents']['resolution_day'])
        self.assertEqual(w['incidents']['world_status'], 'resolved')
        self.assertIsNone(w['incidents']['discovery'])
        self.assertEqual(w['incidents']['aftermath']['player_outcome'], 'missed_unknown')
        self.assertEqual(w['incidents']['receipts'], [])
        self.assertIsNone(incident_report(w)['journal'])
        self.assertEqual(w['incidents']['desk_facts'], ['owner_alarm_report', 'owner_review_received'])

    def test_discovery_needs_real_local_channel_and_cannot_create_occurrence(self):
        w = self.start()
        ident = w['incidents']['id']
        self.reject(w, 'discover_incident', incident_id=ident, channel='public_notice')
        self.until(w, w['incidents']['occurrence_day'])
        self.reject(w, 'discover_incident', incident_id=ident, channel='public_notice')
        self.reject(w, 'discover_incident', incident_id=ident, channel='telepathy')
        self.discover(w)
        self.assertEqual(w['incidents']['world_status'], 'occurred')
        self.assertEqual(w['incidents']['player_facts'], ['alarm_reported'])
        self.reject(w, 'discover_incident', incident_id=ident, channel='public_notice')

    def test_contact_discovery_requires_observed_reference(self):
        w = self.start()
        execute_command(w, 'travel', destination='n13', mode='walk')
        self.until(w, w['incidents']['occurrence_day'])
        self.reject(w, 'discover_incident', incident_id=w['incidents']['id'], channel='contact')
        # Earn Tess's actual promise reference through existing M015 commands.
        a = create_career(17)
        execute_command(a, 'settle_in')
        advance_day(a)
        execute_command(a, 'choose', choice_id='goon.choice.0.promise', option_id='promise')
        advance_day(a)
        execute_command(a, 'choose', choice_id='goon.choice.0.crossroads', option_id='help')
        execute_command(a, 'enable_incidents')
        execute_command(a, 'travel', destination='n13', mode='walk')
        self.until(a, a['incidents']['occurrence_day'])
        execute_command(a, 'discover_incident', incident_id=a['incidents']['id'], channel='contact')
        self.assertEqual(a['incidents']['discovery']['channel'], 'contact')

    def test_hidden_truth_and_unearned_options_never_appear_in_player_view(self):
        w = self.start()
        self.until(w, w['incidents']['information_day'])
        self.discover(w)
        report = incident_report(w)
        self.assertIsNone(report['journal']['finding'])
        self.assertEqual([r['stage'] for r in report['choices']], ['offer'])
        self.assertNotIn(w['incidents']['truth'], json.dumps(report))
        self.reject(w, 'incident_choose', incident_id=w['incidents']['id'], stage='report', option_id='disclose')
        for e in w['events']:
            if e['kind'].startswith('incident_'):
                self.assertNotIn(incident_content.load()['causes'][w['incidents']['truth']], json.dumps(e))

    def test_complete_verification_real_payment_reference_and_no_legal_fabrication(self):
        w = self.work()
        state = w['incidents']
        self.assertIn('cause_verified', state['player_facts'])
        self.assertEqual(state['stages']['work']['selection']['outcome']['pay'], 12)
        self.assertEqual(w['player']['cash'], 52)
        self.assertEqual(w['daily_life']['contacts']['goon.contact.ada']['standing'], 2)
        self.assertEqual(state['desk_facts'], ['owner_alarm_report'])
        self.assertEqual(w['cases'], [])
        self.assertEqual(w['job_attempts'], 0)
        self.assertEqual(w['player']['heat'], 0)
        validate(w)

    def test_partial_completion_reduced_pay_without_guessing_cause(self):
        w = self.work(delay=1)
        self.assertEqual(w['incidents']['stages']['work']['selection']['outcome']['quality'], 'partial')
        self.assertEqual(w['player']['cash'], 46)
        self.assertIn('limited_observations', w['incidents']['player_facts'])
        self.assertIsNone(incident_report(w)['journal']['finding'])
        self.choose(w, 'report', 'disclose')
        self.assertIn('player_limited_statement', w['incidents']['desk_facts'])

    def test_failed_attempt_no_pay_and_bounded_relationship_damage(self):
        w = self.work(delay=2)
        self.assertEqual(w['incidents']['stages']['work']['selection']['outcome']['quality'], 'failed')
        self.assertEqual(w['player']['cash'], 40)
        self.assertEqual(w['daily_life']['contacts']['goon.contact.ada']['standing'], -1)
        self.assertEqual(w['incidents']['player_facts'], ['alarm_reported'])
        self.assertFalse(any(r['stage'] == 'report' for r in incident_report(w)['choices']))

    def test_refusal_creates_no_promise_or_penalty(self):
        w = self.start()
        self.until(w, w['incidents']['occurrence_day'])
        self.discover(w)
        before = deepcopy(w['player'])
        self.choose(w, 'offer', 'refuse')
        self.assertEqual(w['player'], before)
        self.until(w, w['incidents']['resolution_day'])
        self.assertEqual(w['incidents']['receipts'], [])
        self.assertEqual(w['incidents']['aftermath']['player_outcome'], 'refuse')

    def test_known_ignored_opportunity_differs_from_unfinished_agreement(self):
        ignored, failed = self.start(), self.start()
        for w in (ignored, failed):
            self.until(w, w['incidents']['information_day'])
            self.discover(w)
        self.choose(failed, 'offer', 'accept')
        for w in (ignored, failed):
            self.until(w, w['incidents']['resolution_day'])
        self.assertEqual(ignored['incidents']['aftermath']['player_outcome'], 'ignored_known')
        self.assertEqual(ignored['daily_life']['contacts']['goon.contact.ada']['standing'], 0)
        self.assertEqual(failed['daily_life']['contacts']['goon.contact.ada']['standing'], -1)
        self.assertEqual(failed['incidents']['receipts'][0]['fact'], 'agreement_unfinished')

    def test_lawful_help_changes_independent_aftermath_and_future_work(self):
        w = self.start()
        self.until(w, w['incidents']['occurrence_day'])
        self.discover(w)
        self.choose(w, 'offer', 'help')
        self.assertEqual(w['player']['cash'], 40)
        self.until(w, w['incidents']['resolution_day'] + 1)
        self.assertEqual(w['incidents']['aftermath']['shop_status'], 'reopened_with_safety_help')
        self.assertEqual(w['incidents']['followup'], 'safety_preparation_shift')
        before = w['player']['cash']
        self.choose(w, 'followup', 'work')
        self.assertEqual(w['player']['cash'], before + 8)

    def test_disclosure_and_withholding_have_distinct_future_access(self):
        a, b = self.work(), self.work()
        self.choose(a, 'report', 'disclose')
        self.choose(b, 'report', 'withhold')
        self.assertIn('player_cause_statement', a['incidents']['desk_facts'])
        self.assertNotIn('player_cause_statement', b['incidents']['desk_facts'])
        for w in (a, b):
            self.until(w, w['incidents']['resolution_day'] + 1)
            self.assertEqual(w['cases'], [])
        self.assertEqual(a['incidents']['followup'], 'statement_review')
        self.assertEqual(b['incidents']['followup'], 'private_records_shift')

    def test_duplicate_choices_and_followup_cannot_farm_resources(self):
        w = self.work()
        self.reject(w, 'incident_choose', incident_id=w['incidents']['id'], stage='work', option_id='verify')
        self.choose(w, 'report', 'disclose')
        self.reject(w, 'incident_choose', incident_id=w['incidents']['id'], stage='report', option_id='withhold')
        self.until(w, w['incidents']['resolution_day'] + 1)
        self.choose(w, 'followup', 'work')
        for _ in range(3):
            self.reject(w, 'incident_choose', incident_id=w['incidents']['id'], stage='followup', option_id='work')
        self.assertEqual(sum(r['pay'] for r in w['incidents']['receipts']), 20)

    def test_eligibility_revalidated_after_move_or_deadline(self):
        w = self.start()
        self.until(w, w['incidents']['information_day'])
        self.discover(w)
        self.assertTrue(incident_report(w)['choices'])
        execute_command(w, 'travel', destination='home', mode='walk')
        self.reject(w, 'incident_choose', incident_id=w['incidents']['id'], stage='offer', option_id='help')
        self.until(w, w['incidents']['resolution_day'])
        self.go(w)
        self.reject(w, 'incident_choose', incident_id=w['incidents']['id'], stage='offer', option_id='accept')

    def test_three_actions_and_18_tu_preserved(self):
        w = self.work()
        self.assertEqual(actions_remaining(w), 1)
        before = deepcopy(w['navigation'])
        self.choose(w, 'report', 'disclose')
        self.assertEqual(actions_remaining(w), 0)
        self.assertEqual(w['navigation'], before)
        self.reject(w, 'lay_low')
        advance_day(w)
        self.assertEqual(actions_remaining(w), 3)
        self.assertEqual(w['navigation']['tu_used'], 0)
        from navigation import DAILY_TU
        self.assertEqual(DAILY_TU, 18)

    def test_readonly_views_detached_and_cannot_discover_or_change_rng(self):
        for w in (create_career(), self.start(), self.work()):
            before, rng = deepcopy(w), random.getstate()
            for _ in range(3):
                row = incident_report(w)
                row.clear()
                if 'incident_version' in w:
                    daily_life.contact_report(w)[-1]['memories'].clear()
            self.assertEqual(w, before)
            self.assertEqual(random.getstate(), rng)

    def test_daily_processing_exactly_once_and_terminal_history_bounded(self):
        w = self.work()
        before = deepcopy(w)
        incidents.begin_day(w)
        incidents.begin_day(w)
        self.assertEqual(w, before)
        self.until(w, w['incidents']['resolution_day'] + 5)
        state, count = deepcopy(w['incidents']), len([e for e in w['events'] if e['kind'].startswith('incident_')])
        for _ in range(20):
            advance_day(w)
        self.assertEqual(w['incidents'], state)
        self.assertEqual(len([e for e in w['events'] if e['kind'].startswith('incident_')]), count)

    def test_zero_cash_tu_and_failed_commitment_leave_ordinary_life_viable(self):
        w = create_career(17)
        w['player']['cash'] = 0
        execute_command(w, 'settle_in')
        advance_day(w)
        execute_command(w, 'enable_incidents')
        self.until(w, w['incidents']['resolution_day'] + 5)
        self.assertFalse(w['player']['arrested'])
        self.assertEqual(w['player']['cash'], 0)
        self.assertEqual(w['navigation']['home_id'], 'goon.poi.p031')
        self.go(w)
        row = next(r for r in daily_life.opportunities(w) if any(o['id'] == 'work' and o['availability'] == 'available' for o in r['options']))
        execute_command(w, 'choose', choice_id=row['id'], option_id='work')
        self.assertGreater(w['player']['cash'], 0)

    def test_save_resume_every_lifecycle_stage(self):
        w = self.start()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            for _ in range(14):
                save_career(w, path)
                restored = load_career(path)
                self.assertEqual(w, restored)
                self.assertEqual(incident_report(w), incident_report(restored))
                if w['day'] == w['incidents']['information_day']:
                    for item in (w, restored):
                        self.discover(item)
                        self.choose(item, 'offer', 'accept')
                        self.choose(item, 'work', 'verify')
                        self.choose(item, 'report', 'disclose')
                    self.assertEqual(w, restored)
                advance_day(w)
                advance_day(restored)
                self.assertEqual(w, restored)

    def test_malformed_state_versions_events_payments_and_memories_reject(self):
        valid = self.work()
        mutations = [lambda w: w.update(incident_version=True),
            lambda w: w['incidents'].update(rules_version=True),
            lambda w: w['incidents'].update(content_fingerprint='missing'),
            lambda w: w['incidents'].update(last_tick_day=True),
            lambda w: w['incidents']['receipts'][0].update(pay=1200),
            lambda w: w['incidents']['stages']['work']['selection'].update(action_cost=False),
            lambda w: w['incidents']['owner_facts'].append('unearned'),
            lambda w: w['incidents']['player_facts'].append('unearned'),
            lambda w: next(e for e in w['events'] if e['kind'] == 'incident_transition').update(transition_id='forged'),
            lambda w: next(e for e in w['events'] if e['kind'] == 'incident_transition').update(effect_ids=['forged']),
            lambda w: w['events'].append(deepcopy(next(e for e in w['events'] if e['kind'] == 'incident_transition'))),
            lambda w: w['daily_life']['contacts']['goon.contact.ada']['memories'].clear(),
            lambda w: w.pop('incident_version')]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.json'
            for mutate in mutations:
                w = deepcopy(valid)
                mutate(w)
                path.write_text(json.dumps(w), encoding='utf-8')
                with self.subTest(mutation=mutations.index(mutate)), self.assertRaises(ValueError):
                    load_career(path)

    def test_failed_save_preserves_primary_backup_and_in_memory_state(self):
        w = self.work()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(w, path)
            original, before = path.read_bytes(), deepcopy(w)
            with patch('career_persistence.os.replace', side_effect=OSError('injected failure')):
                with self.assertRaises(OSError):
                    save_career(w, path)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(w, before)
            self.assertEqual(load_career(path), w)

    def test_historical_fixtures_no_implicit_incident_adoption(self):
        root = Path(__file__).parent
        for path in sorted((root / 'fixtures').rglob('*.json')) + sorted((root / 'mobility_fixtures').rglob('*.json')):
            with self.subTest(path=str(path)):
                w = load_career(path)
                original_events = deepcopy(w['events'])
                self.assertNotIn('incident_version', w)
                self.assertFalse(incident_report(w)['enabled'])
                self.assertEqual(w['events'], original_events)
                advance_day(w)
                self.assertNotIn('incident_version', w)

    def test_unadopted_world_legal_faction_and_travel_behavior_unchanged(self):
        a, b = create_career(3), create_career(3)
        for w in (a, b):
            execute_command(w, 'settle_in')
            advance_day(w)
            execute_command(w, 'join', faction='Harbor Syndicate')
            execute_command(w, 'job', kind='collection')
        execute_command(b, 'enable_incidents')
        for _ in range(12):
            for w in (a, b):
                advance_day(w)
            for key in ('player', 'factions', 'faction_strategy', 'cases', 'legal', 'navigation', 'districts'):
                self.assertEqual(a[key], b[key], key)

    def test_fresh_process_replay_ignores_python_hash_seed(self):
        code = ('import json; from game_service import *; w=create_career(17); '
                'execute_command(w,"settle_in"); advance_day(w); execute_command(w,"enable_incidents"); '
                '[advance_day(w) for _ in range(10)]; print(json.dumps(w,sort_keys=True))')
        outputs = [subprocess.check_output([sys.executable, '-B', '-c', code], env=dict(os.environ, PYTHONHASHSEED=s))
                   for s in ('1', '999')]
        self.assertEqual(*outputs)

    def test_zero_tu_local_help_and_next_day_recovery(self):
        w = self.start()
        self.until(w, w['incidents']['information_day'])
        self.discover(w)
        while w['navigation']['tu_used'] < 18:
            target = 'home' if w['navigation']['location_id'] == 'goon.poi.p032' else 'p032'
            execute_command(w, 'travel', destination=target, mode='walk')
        # Eighteen one-TU hops from the initial home end at home. Wait is still
        # available there; local refusal needs no movement or additional TU.
        before = deepcopy(w['navigation'])
        self.choose(w, 'offer', 'refuse')
        self.assertEqual(w['navigation'], before)
        self.reject(w, 'travel', destination='p032', mode='walk')
        advance_day(w)
        execute_command(w, 'travel', destination='p032', mode='walk')
        self.assertEqual(w['navigation']['location_id'], 'goon.poi.p032')

    def test_injected_effect_failure_rolls_back_cash_memory_and_rng(self):
        w = self.start()
        self.until(w, w['incidents']['information_day'])
        self.discover(w)
        self.choose(w, 'offer', 'accept')
        before, rng = deepcopy(w), random.getstate()
        with patch('daily_life._memory', side_effect=ValueError('injected effect failure')):
            with self.assertRaisesRegex(ValueError, 'injected'):
                self.choose(w, 'work', 'verify')
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)

    def test_unknown_ids_arguments_and_premature_work_reject_atomically(self):
        w = self.start()
        self.until(w, w['incidents']['occurrence_day'])
        self.discover(w)
        self.choose(w, 'offer', 'accept')
        for args in (dict(incident_id=w['incidents']['id'], stage='work', option_id='verify'),
                     dict(incident_id='unknown', stage='offer', option_id='refuse'),
                     dict(incident_id=w['incidents']['id'], stage='unknown', option_id='refuse'),
                     dict(incident_id=w['incidents']['id'], stage='offer', option_id='unknown'),
                     dict(incident_id=w['incidents']['id'], stage='offer', option_id=True)):
            self.reject(w, 'incident_choose', **args)

    def test_unrelated_closure_does_not_change_preview_or_grant_movement(self):
        import navigation
        a, b = create_career(), self.start()
        # Match day and normal navigation resources; event adoption never moves.
        advance_day(a)
        for w in (a, b):
            w['navigation']['closures'].append(dict(id='test.closed', edge_id='goon.edge.e06',
                from_id='goon.neighborhood.n18', mode='rail', start_day=w['day'],
                end_day=w['day'] + 1, known=False, cause='test closure'))
        self.assertEqual(navigation.plan_route(a, 'p032'), navigation.plan_route(b, 'p032'))
        self.go(a)
        self.go(b)
        self.assertEqual(a['navigation'], b['navigation'])

    def test_legacy_clock_catchup_does_not_offer_retroactive_participation(self):
        from simulation import advance
        w = self.start()
        for _ in range(10):
            advance(w)
        advance_day(w)
        self.assertEqual(w['incidents']['world_status'], 'resolved')
        self.discover(w)
        self.assertEqual(incident_report(w)['choices'], [])
        self.assertEqual(w['incidents']['receipts'], [])
        validate(w)

    def test_detention_blocks_new_involvement_without_blocking_world_resolution(self):
        w = self.start()
        self.until(w, w['incidents']['information_day'])
        self.discover(w)
        # A valid pretrial boundary fixture, not a new gameplay crime/source.
        w['cases'].append(dict(id=1, crime='fixture', suspect='Rookie', evidence=3, status='charged'))
        w['player'].update(arrested=True, custody='pretrial')
        validate(w)
        self.reject(w, 'incident_choose', incident_id=w['incidents']['id'], stage='offer', option_id='help')
        self.choose(w, 'offer', 'refuse')
        self.until(w, w['incidents']['resolution_day'])
        self.assertEqual(w['incidents']['world_status'], 'resolved')
        self.assertFalse(w['player']['arrested'])

    def test_adopted_mobility_keeps_atomic_journeys_and_incident_costs_separate(self):
        import mobility
        from mobility_content import OVERLAY_ID
        w = self.start()
        execute_command(w, 'travel', destination='p039', mode='auto')
        execute_command(w, 'enable_mobility', overlay_id=OVERLAY_ID, request_id='incident.mobility')
        advance_day(w)
        quote = mobility.plan_route(w, 'p032', 'free')
        execute_command(w, 'journey', **quote['arguments'])
        self.until(w, w['incidents']['information_day'])
        execute_command(w, 'discover_incident', incident_id=w['incidents']['id'], channel='public_notice')
        before = deepcopy(w['navigation']), deepcopy(w['mobility'])
        self.choose(w, 'offer', 'help')
        self.assertEqual(before, (w['navigation'], w['mobility']))
        validate(w)

    def test_long_running_campaign_disk_replay(self):
        from incident_campaigns import run
        result = run(17, days=120, resume_every=15)
        self.assertEqual(result['resumes'], 8)
        self.assertEqual(result['world_status'], 'resolved')
        self.assertLessEqual(result['total_compensation'], 20)


if __name__ == '__main__':
    unittest.main()
