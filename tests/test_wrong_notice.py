"""M018: two dispatched incidents, contradictory claims and targeted correction."""
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
from game_service import (actions_remaining, advance_day, create_career, execute_command,
                          incident_report, load_career, save_career)
from incident_dispatch import NIGHT_SHIFT, WRONG_NOTICE, definitions
import incident_dispatch
import notice_content
import wrong_notice


class WrongNoticeTests(unittest.TestCase):
    def start(self, seed=2, both=False):
        w = create_career(seed)
        execute_command(w, 'settle_in')
        advance_day(w)
        if both:
            execute_command(w, 'enable_incidents')
        execute_command(w, 'enable_incident', definition_id=WRONG_NOTICE)
        return w

    def until(self, w, day):
        while w['day'] < day:
            advance_day(w)

    def go(self, w, destination):
        target = {'store': 'goon.poi.p032', 'hub': 'goon.neighborhood.n13', 'home': 'goon.poi.p031'}[destination]
        if w['navigation']['location_id'] != target:
            execute_command(w, 'travel', destination=target, mode='walk')

    def discover(self, w, channel='public_notice'):
        self.go(w, 'store' if channel == 'public_notice' else 'hub')
        return execute_command(w, 'discover_incident', incident_id=w['wrong_notice']['id'], channel=channel)

    def ready(self, seed=2, both=False, channel='public_notice'):
        w = self.start(seed, both)
        self.until(w, w['wrong_notice']['information_day'])
        self.discover(w, channel)
        return w

    def choose(self, w, stage, option):
        return execute_command(w, 'incident_choose', incident_id=w['wrong_notice']['id'], stage=stage, option_id=option)

    def verify(self, w):
        self.go(w, 'hub')
        return self.choose(w, 'verify', 'ledger')

    def report(self, w):
        return incident_report(w, w['wrong_notice']['id'])

    def reject(self, w, command, **arguments):
        before, rng = deepcopy(w), random.getstate()
        with self.assertRaises(ValueError):
            execute_command(w, command, **arguments)
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)

    def rejected_choice(self, w, stage, option):
        self.reject(w, 'incident_choose', incident_id=w['wrong_notice']['id'], stage=stage, option_id=option)

    def roundtrip(self, w):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(w, path)
            self.assertEqual(load_career(path), w)

    def test_definitions_readonly_and_no_implicit_adoption(self):
        w = create_career()
        before = deepcopy(w)
        self.assertEqual([d['id'] for d in definitions()], [NIGHT_SHIFT, WRONG_NOTICE])
        self.assertFalse(incident_report(w)['enabled'])
        self.assertEqual(w, before)
        self.reject(w, 'enable_incident', definition_id=WRONG_NOTICE)
        advance_day(w)
        self.assertNotIn('notice_version', w)

    def test_explicit_adoption_preserves_existing_resources_and_old_slot(self):
        w = self.start(both=True)
        self.assertEqual(w['player']['cash'], 40)
        self.assertEqual(actions_remaining(w), 3)
        self.assertEqual(w['navigation']['tu_used'], 0)
        self.assertIn('incident_version', w)
        self.assertIn('notice_version', w)
        self.assertNotEqual(w['incidents']['id'], w['wrong_notice']['id'])
        self.reject(w, 'enable_incident', definition_id=WRONG_NOTICE)
        self.reject(w, 'enable_incident', definition_id='unknown')
        self.reject(w, 'enable_incident', definition_id=NIGHT_SHIFT)
        self.roundtrip(w)

    def test_generic_night_shift_adoption_uses_same_old_definition(self):
        w = create_career()
        execute_command(w, 'settle_in')
        advance_day(w)
        execute_command(w, 'enable_incident', definition_id=NIGHT_SHIFT)
        self.assertEqual(w['incidents']['id'], NIGHT_SHIFT + '.enrollment.1.alarm')
        self.assertNotIn('notice_version', w)
        self.roundtrip(w)

    def test_deterministic_occurrence_without_discovery_or_payment(self):
        a, b = self.start(73), self.start(73)
        b = dict(reversed(list(b.items())))
        for _ in range(14):
            advance_day(a)
            advance_day(b)
        self.assertEqual(a, b)
        state = a['wrong_notice']
        self.assertEqual(state['world_status'], 'resolved')
        self.assertEqual(state['aftermath']['outcome'], 'missed_unknown')
        self.assertEqual(state['receipts'], [])
        self.assertEqual(state['audiences'], dict(board='ledger', tenants='ledger', desk='ledger'))
        self.assertEqual(state['player_claims'], [])

    def test_board_and_handbill_disagree_but_reveal_no_true_answer(self):
        w = self.ready()
        first = self.report(w)['journal']
        self.assertIsNone(first['finding'])
        self.assertEqual(len(first['observed_claims']), 1)
        self.go(w, 'hub')
        self.choose(w, 'compare', 'residents')
        report = self.report(w)['journal']
        self.assertEqual(len({c['delivery_day'] for c in report['observed_claims']}), 2)
        self.assertTrue(all(c['delivery_day'] != w['wrong_notice']['truth']['delivery_day'] for c in report['observed_claims']))
        self.assertTrue(all(c['limitation'] and c['credibility'] for c in report['observed_claims']))
        self.assertIsNone(report['finding'])

    def test_direct_resident_discovery_needs_no_tess_reference(self):
        w = self.ready(channel='contact')
        self.assertEqual(w['wrong_notice']['player_claims'], ['handbill'])
        self.assertFalse(any(m['fact'] == 'promise_kept' for m in w['daily_life']['contacts']['goon.contact.tess']['memories']))
        self.assertIsNone(self.report(w)['journal']['finding'])
        self.roundtrip(w)

    def test_verification_only_informs_player_and_clerk(self):
        w = self.ready()
        before = deepcopy(w['wrong_notice']['audiences'])
        self.verify(w)
        self.assertEqual(w['wrong_notice']['audiences'], before)
        self.assertEqual(self.report(w)['journal']['finding'], w['wrong_notice']['truth']['delivery_day'])
        self.assertEqual(w['player']['cash'], 40)
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.NEIGHBOR]['memories'], [])

    def test_premature_verification_remote_discovery_and_expired_choices_reject(self):
        w = self.start()
        self.reject(w, 'discover_incident', incident_id=w['wrong_notice']['id'], channel='public_notice')
        self.until(w, w['wrong_notice']['occurrence_day'])
        self.discover(w)
        self.rejected_choice(w, 'verify', 'ledger')
        self.until(w, w['wrong_notice']['resolution_day'])
        self.rejected_choice(w, 'response', 'repeat_notice')

    def test_correcting_board_does_not_update_tenant_beliefs(self):
        w = self.ready()
        self.verify(w)
        self.go(w, 'store')
        self.choose(w, 'response', 'correct_board')
        self.assertEqual(w['wrong_notice']['audiences']['board'], 'ledger')
        self.assertEqual(w['wrong_notice']['audiences']['tenants'], 'handbill')
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.CLERK]['standing'], 0)
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.NEIGHBOR]['standing'], 0)

    def test_desk_correction_has_delay_and_targeted_delivery(self):
        w = self.ready()
        self.verify(w)
        self.choose(w, 'response', 'notify_desk')
        self.assertEqual(w['wrong_notice']['audiences']['board'], 'poster')
        self.assertEqual(w['wrong_notice']['audiences']['tenants'], 'handbill')
        advance_day(w)
        self.assertEqual(w['wrong_notice']['audiences']['board'], 'ledger')
        self.assertEqual(w['wrong_notice']['audiences']['tenants'], 'handbill')
        self.assertEqual(len([t for t in w['wrong_notice']['transmissions'] if t['id'].endswith('.desk_post')]), 1)

    def test_success_corrects_both_before_delivery_without_wages(self):
        w = self.ready()
        self.verify(w)
        self.choose(w, 'response', 'notify_desk')
        self.choose(w, 'repair', 'warn_group')
        self.assertEqual(actions_remaining(w), 0)
        self.until(w, w['wrong_notice']['resolution_day'])
        self.assertEqual(w['wrong_notice']['aftermath']['outcome'], 'success')
        self.assertEqual(w['wrong_notice']['impact']['misdirected'], [])
        self.assertEqual(sum(r['pay'] for r in w['wrong_notice']['receipts']), 0)

    def test_partial_help_leaves_other_audience_misdirected(self):
        w = self.ready()
        self.verify(w)
        self.go(w, 'store')
        self.choose(w, 'response', 'correct_board')
        self.until(w, w['wrong_notice']['resolution_day'])
        self.assertEqual(w['wrong_notice']['aftermath']['outcome'], 'partial')
        self.assertEqual(w['wrong_notice']['impact']['misdirected'], ['tenants'])
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.CLERK]['standing'], 1)

    def test_late_correction_does_not_undo_delivery_day_harm(self):
        w = self.ready()
        self.verify(w)
        self.until(w, w['wrong_notice']['truth']['delivery_day'] + 1)
        self.choose(w, 'response', 'notify_desk')
        self.choose(w, 'repair', 'warn_group')
        self.until(w, w['wrong_notice']['resolution_day'])
        self.assertEqual(w['wrong_notice']['aftermath']['outcome'], 'partial')
        self.assertEqual(w['wrong_notice']['impact']['misdirected'], ['board', 'tenants'])

    def test_unverified_sharing_has_recipient_specific_failure(self):
        w = self.ready()
        self.go(w, 'hub')
        self.choose(w, 'response', 'repeat_notice')
        self.assertEqual(w['wrong_notice']['audiences']['tenants'], 'poster')
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.CLERK]['memories'], [])
        self.until(w, w['wrong_notice']['resolution_day'])
        self.assertEqual(w['wrong_notice']['aftermath']['outcome'], 'failed')
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.NEIGHBOR]['standing'], -1)
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.CLERK]['standing'], 0)
        self.assertEqual(w['cases'], [])

    def test_retraction_corrects_only_original_recipients_without_bonus(self):
        w = self.ready()
        self.go(w, 'hub')
        self.choose(w, 'response', 'repeat_notice')
        self.verify(w)
        self.choose(w, 'repair', 'retract')
        self.assertEqual(w['wrong_notice']['audiences']['tenants'], 'ledger')
        self.assertEqual(w['wrong_notice']['audiences']['board'], 'poster')
        self.until(w, w['wrong_notice']['resolution_day'])
        self.assertEqual(w['wrong_notice']['aftermath']['outcome'], 'partial')
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.NEIGHBOR]['standing'], 0)

    def test_refusal_and_missed_known_are_not_broken_promises(self):
        for refuse in (False, True):
            w = self.ready()
            if refuse:
                self.choose(w, 'response', 'refuse')
            self.until(w, w['wrong_notice']['resolution_day'])
            self.assertEqual(w['wrong_notice']['aftermath']['outcome'], 'refused' if refuse else 'ignored_known')
            self.assertEqual(w['wrong_notice']['receipts'], [])
            self.assertEqual(w['daily_life']['promises'], {})

    def test_no_vacancy_option_is_not_presented_before_or_without_evidence(self):
        seed = next(s for s in range(20) if not wrong_notice.initial(s, 1)['truth']['standby_slot'])
        w = self.ready(seed)
        self.verify(w)
        options = [o['id'] for row in self.report(w)['choices'] for o in row['options']]
        self.assertNotIn('reserve_slot', options)
        self.rejected_choice(w, 'response', 'reserve_slot')

    def test_selfish_opportunity_is_bounded_optional_and_not_a_crime(self):
        seed = next(s for s in range(20) if wrong_notice.initial(s, 1)['truth']['standby_slot'])
        w = self.ready(seed)
        self.verify(w)
        before = w['player']['cash']
        self.choose(w, 'response', 'reserve_slot')
        self.assertEqual(w['player']['cash'], before)
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.CLERK]['standing'], -1)
        self.until(w, w['wrong_notice']['resolution_day'] + 1)
        before = w['player']['cash']
        self.choose(w, 'followup', 'work')
        self.assertEqual(w['player']['cash'], before + 5)
        self.roundtrip(w)
        self.rejected_choice(w, 'followup', 'work')
        self.assertEqual(sum(r['pay'] for r in w['wrong_notice']['receipts']), 5)
        self.assertEqual(w['cases'], [])
        self.assertEqual(w['job_attempts'], 0)
        self.assertEqual(w['player']['heat'], 0)

    def test_desk_cannot_be_told_of_a_poster_never_observed(self):
        w = self.ready(channel='contact')
        self.verify(w)
        self.rejected_choice(w, 'response', 'notify_desk')
        self.rejected_choice(w, 'response', 'reserve_slot')
        self.go(w, 'store')
        self.choose(w, 'compare', 'board')
        self.go(w, 'hub')
        self.choose(w, 'response', 'notify_desk')

    def test_player_does_not_magically_receive_autonomous_correction(self):
        w = self.ready()
        self.until(w, w['wrong_notice']['resolution_day'] + 1)
        report = self.report(w)['journal']
        self.assertIsNone(report['finding'])
        self.assertIsNone(report['aftermath'])
        self.go(w, 'hub')
        self.choose(w, 'aftermath', 'read')
        self.assertIsNotNone(self.report(w)['journal']['finding'])
        self.assertEqual(len(w['wrong_notice']['observations']), 2)
        self.assertTrue(any(t.get('recipient') == 'public_circular' for t in w['wrong_notice']['transmissions']))
        self.rejected_choice(w, 'aftermath', 'read')

    def test_private_automatic_reaction_is_not_a_player_event_or_contact_fact(self):
        import daily_life
        w = self.ready()
        self.go(w, 'hub')
        self.choose(w, 'response', 'repeat_notice')
        self.until(w, w['wrong_notice']['resolution_day'] - 1)
        response = advance_day(w)
        self.assertEqual(w['daily_life']['contacts'][wrong_notice.NEIGHBOR]['standing'], -1)
        known = next(r for r in daily_life.contact_report(w) if r['id'] == wrong_notice.NEIGHBOR)
        self.assertEqual(known['standing'], 0)
        self.assertEqual(known['memories'], [])
        self.assertNotIn('notice_claim_disproved', json.dumps(response['events']))
        self.assertNotIn('resolution.disproved', json.dumps(response['events']))
        before = deepcopy(w)
        incident_dispatch.player_events(w, w['events']).clear()
        self.assertEqual(w, before)
        advance_day(w)
        self.choose(w, 'aftermath', 'read')
        known = next(r for r in daily_life.contact_report(w) if r['id'] == wrong_notice.NEIGHBOR)
        self.assertEqual(known['standing'], -1)
        self.assertEqual(known['memories'][0]['fact'], 'notice_claim_disproved')

    def test_late_discovery_reads_an_actual_corrected_source_without_reopening_work(self):
        w = self.start()
        self.until(w, w['wrong_notice']['resolution_day'] + 1)
        self.discover(w)
        self.assertEqual(w['wrong_notice']['player_claims'], ['ledger'])
        self.assertEqual(self.report(w)['journal']['finding'], w['wrong_notice']['truth']['delivery_day'])
        self.rejected_choice(w, 'response', 'correct_board')
        self.assertEqual(w['wrong_notice']['receipts'], [])

    def test_preview_is_detached_readonly_and_does_not_acknowledge(self):
        w = self.ready(both=True)
        before, rng = deepcopy(w), random.getstate()
        for _ in range(4):
            self.report(w).clear()
            incident_report(w)['incidents'].clear()
            definitions().clear()
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)

    def test_new_content_dictionary_order_does_not_change_decisions(self):
        a = self.ready()
        content = notice_content.load()
        content['stages'] = dict(reversed(list(content['stages'].items())))
        content['contacts'] = dict(reversed(list(content['contacts'].items())))
        with patch('wrong_notice.load', side_effect=lambda: deepcopy(content)):
            b = self.ready()
            self.verify(b)
        self.verify(a)
        self.assertEqual(a, b)

    def test_invalid_or_cross_definition_commands_leave_state_and_rng(self):
        w = self.ready(both=True)
        self.rejected_choice(w, 'work', 'verify')
        self.reject(w, 'incident_choose', incident_id='unknown', stage='verify', option_id='ledger')
        self.reject(w, 'discover_incident', incident_id=w['wrong_notice']['id'], channel='contact')
        self.reject(w, 'enable_incident', definition_id=True)

    def test_daily_processing_and_terminal_history_exactly_once(self):
        w = self.ready(both=True)
        before = deepcopy(w)
        incident_dispatch.begin_day(w)
        self.assertEqual(w, before)
        self.until(w, max(w['wrong_notice']['resolution_day'] + 5, w['incidents']['resolution_day'] + 5))
        frozen = deepcopy(w['wrong_notice']), deepcopy(w['incidents'])
        count = len([e for e in w['events'] if e['kind'] == 'incident_transition'])
        for _ in range(10):
            advance_day(w)
        self.assertEqual(frozen, (w['wrong_notice'], w['incidents']))
        self.assertEqual(count, len([e for e in w['events'] if e['kind'] == 'incident_transition']))

    def test_two_incidents_discover_and_resolve_through_same_commands(self):
        w = self.ready(both=True)
        night_id = w['incidents']['id']
        self.until(w, max(w['day'], w['incidents']['information_day']))
        execute_command(w, 'discover_incident', incident_id=night_id, channel='public_notice')
        execute_command(w, 'incident_choose', incident_id=night_id, stage='offer', option_id='refuse')
        self.choose(w, 'response', 'refuse')
        self.until(w, max(w['wrong_notice']['resolution_day'], w['incidents']['resolution_day']))
        self.assertEqual(w['incidents']['world_status'], w['wrong_notice']['world_status'])
        self.roundtrip(w)

    def test_discovery_uses_historical_source_and_later_tess_reference_is_not_invented(self):
        w = self.ready()
        self.go(w, 'home')
        self.roundtrip(w)
        bad = deepcopy(w)
        event = next(e for e in bad['events'] if e['kind'] == 'incident_transition' and e.get('operation') == 'discover')
        event['context']['location'] = 'goon.neighborhood.n13'
        event['context']['tess_reference'] = True
        event['arguments']['channel'] = 'contact'
        for e in bad['events']:
            if e['kind'] == 'player_command' and e['command_id'] == event['command_id']:
                e['arguments']['channel'] = 'contact'
        bad['wrong_notice']['discovery']['channel'] = 'contact'
        with self.assertRaises(ValueError):
            validate(bad)

    def test_malformed_knowledge_transmissions_ownership_and_markers_reject(self):
        w = self.ready(both=True)
        self.verify(w)
        mutations = [lambda x: x.update(notice_version=True),
            lambda x: x['wrong_notice'].update(content_fingerprint='unknown'),
            lambda x: x['wrong_notice']['player_claims'].append('review'),
            lambda x: x['wrong_notice']['audiences'].update(tenants='ledger'),
            lambda x: x['wrong_notice']['transmissions'][0].update(source='player'),
            lambda x: x['wrong_notice']['receipts'][0].update(contact_id=wrong_notice.NEIGHBOR),
            lambda x: x['wrong_notice'].update(id=x['incidents']['id']),
            lambda x: x.pop('notice_version'),
            lambda x: x['events'].append(dict(day=x['day'],kind='incident_transition',message='unknown',incident_id='unknown'))]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.json'
            for index, mutate in enumerate(mutations):
                bad = deepcopy(w)
                mutate(bad)
                path.write_text(json.dumps(bad), encoding='utf-8')
                with self.subTest(index=index), self.assertRaises(ValueError):
                    load_career(path)

    def test_save_resume_at_every_stage_and_no_duplicate_relation_reward(self):
        w = self.ready()
        for stage, option in [('verify','ledger'), ('response','notify_desk'), ('repair','warn_group')]:
            self.go(w, 'hub')
            self.choose(w, stage, option)
            self.roundtrip(w)
            self.rejected_choice(w, stage, option)
        self.until(w, w['wrong_notice']['resolution_day'] + 1)
        self.roundtrip(w)
        self.choose(w, 'aftermath', 'read')
        self.roundtrip(w)

    def test_correction_requires_prior_verification_and_unique_ordered_sources(self):
        w = self.ready()
        self.go(w, 'hub')
        self.rejected_choice(w, 'response', 'notify_desk')
        self.verify(w)
        self.choose(w, 'response', 'notify_desk')
        advance_day(w)
        self.roundtrip(w)
        verify_index = next(i for i,e in enumerate(w['events']) if e['kind']=='incident_transition'
            and e.get('operation')=='choose' and e['arguments']['stage']=='verify')
        response_index = next(i for i,e in enumerate(w['events']) if e['kind']=='incident_transition'
            and e.get('operation')=='choose' and e['arguments']['stage']=='response')
        for mode in ('reorder_verification', 'missing_transmission', 'duplicate_transmission'):
            bad = deepcopy(w)
            if mode == 'reorder_verification':
                bad['events'][verify_index], bad['events'][response_index] = bad['events'][response_index], bad['events'][verify_index]
            elif mode == 'missing_transmission':
                bad['wrong_notice']['transmissions'].pop()
            else:
                bad['wrong_notice']['transmissions'].append(deepcopy(bad['wrong_notice']['transmissions'][-1]))
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                validate(bad)

    def test_existing_saves_never_auto_adopt_notice(self):
        root = Path(__file__).parent
        paths = list((root/'fixtures').rglob('*.json')) + list((root/'mobility_fixtures').rglob('*.json'))
        for path in sorted(paths):
            w = load_career(path)
            self.assertNotIn('notice_version', w)
            advance_day(w)
            self.assertNotIn('notice_version', w)

    def test_zero_cash_and_refusal_preserve_ordinary_lawful_career(self):
        import daily_life
        w = create_career(73)
        w['player']['cash'] = 0
        execute_command(w,'settle_in')
        advance_day(w)
        execute_command(w,'enable_incident',definition_id=WRONG_NOTICE)
        self.until(w,w['wrong_notice']['resolution_day']+5)
        self.go(w,'store')
        for _ in range(8):
            offered = [r for r in daily_life.opportunities(w) if any(o['id']=='work' and o['availability']=='available' for o in r['options'])]
            if offered:
                break
            advance_day(w)
        self.assertTrue(offered)
        execute_command(w,'choose',choice_id=offered[0]['id'],option_id='work')
        self.assertGreater(w['player']['cash'],0)
        self.assertFalse(w['player']['arrested'])
        self.assertEqual(w['navigation']['home_id'],'goon.poi.p031')

    def test_contact_effect_failure_rolls_back_entire_candidate(self):
        w = self.ready()
        self.go(w,'hub')
        before = deepcopy(w)
        with patch('daily_life._memory',side_effect=ValueError('injected')):
            with self.assertRaises(ValueError):
                self.verify(w)
        self.assertEqual(w,before)

    def test_failed_disk_replacement_preserves_both_adapters_and_recoverable_save(self):
        w = self.ready(both=True)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(w, path)
            original = path.read_bytes()
            self.verify(w)
            before = deepcopy(w)
            replace = os.replace
            def fail_publication(source, target):
                if Path(target) == path:
                    raise OSError('injected replacement failure')
                return replace(source, target)
            with patch('career_persistence.os.replace', side_effect=fail_publication):
                with self.assertRaises(OSError):
                    save_career(w, path)
            self.assertEqual(w, before)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(path.with_name(path.name + '.bak').read_bytes(), original)
            self.assertEqual(list(Path(folder).glob('*.tmp')), [])
            self.assertEqual(load_career(path), load_career(path.with_name(path.name + '.bak')))
            save_career(w, path)
            self.assertEqual(load_career(path), w)

    def test_long_two_incident_campaign_with_daily_disk_resume(self):
        from notice_campaigns import run
        for seed, mode, outcome in [(73, 'help', 'success'), (191, 'unchecked', 'failed')]:
            result = run(seed, mode, days=90, resume_every=1)
            self.assertEqual(result['resumes'], 90)
            self.assertEqual(result['notice_outcome'], outcome)
            self.assertEqual(result['night_shift_outcome'], 'refuse')
            self.assertEqual(result['incident_compensation'], 0)
            self.assertEqual(result['arrears'], 0)

    def test_fresh_process_replay_ignores_hash_seed(self):
        code = ('import json; from game_service import *; from incident_dispatch import WRONG_NOTICE; '
            'w=create_career(73); execute_command(w,"settle_in"); advance_day(w); '
            'execute_command(w,"enable_incidents"); execute_command(w,"enable_incident",definition_id=WRONG_NOTICE); '
            '[advance_day(w) for _ in range(14)]; print(json.dumps(w,sort_keys=True))')
        values = [subprocess.check_output([sys.executable,'-B','-c',code],env=dict(os.environ,PYTHONHASHSEED=s)) for s in ('1','997')]
        self.assertEqual(*values)


if __name__ == '__main__':
    unittest.main()
