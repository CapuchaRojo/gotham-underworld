"""M015 player choices, receipts, knowledge boundaries and ordinary recovery."""
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
from daily_life_campaigns import BRANCH_SEEDS, play_day, run_campaign
from game_service import (actions_remaining, advance_day, choice_report, contact_report,
                          create_career, execute_command, home_report, life_report,
                          load_career, opportunities, save_career)
import life_content
from life_presentation import render_choice, render_contacts, render_life

FIXTURES = Path(__file__).parent / 'fixtures'


class DailyLifeTests(unittest.TestCase):
    def world(self, seed=42, cash=40):
        world = create_career(seed)
        world['player']['cash'] = cash  # initial-state boundary fixture, before enrollment
        execute_command(world, 'settle_in')
        advance_day(world)
        return world

    def go(self, world, destination):
        target = {'home': 'goon.poi.p031', 'store': 'goon.poi.p032', 'hub': 'goon.neighborhood.n13'}[destination]
        if world['navigation']['location_id'] != target:
            execute_command(world, 'travel', destination=target, mode='auto')

    def pick(self, world, definition, option, week=0):
        return execute_command(world, 'choose', choice_id=f'goon.choice.{week}.{definition}', option_id=option)

    def until(self, world, day):
        while world['day'] < day:
            advance_day(world)

    def rejected(self, world, command, *, message=None, **args):
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, message or '.'):
            execute_command(world, command, **args)
        self.assertEqual(world, before)

    def test_reports_do_not_adopt_or_mutate_unprepared_careers(self):
        w = create_career()
        before = deepcopy(w)
        self.assertFalse(life_report(w)['enabled'])
        for read in (home_report, contact_report, opportunities):
            with self.assertRaises(ValueError):
                read(w)
        with self.assertRaises(ValueError):
            choice_report(w, 'missing')
        self.assertEqual(w, before)

    def test_disclosed_enrollment_is_pending_and_does_not_refresh_resources(self):
        w = create_career()
        execute_command(w, 'join', faction='Harbor Syndicate')
        for _ in range(3):
            execute_command(w, 'job', kind='courier')
        before = deepcopy(w)
        result = execute_command(w, 'settle_in')['result']
        self.assertIn('$30', result['message'])
        self.assertEqual(w['player'], before['player'])
        self.assertEqual(w['navigation'], before['navigation'])
        self.assertEqual(actions_remaining(w), 0)
        self.assertEqual(w['daily_life']['housing']['next_due_day'], 7)
        with self.assertRaises(ValueError):
            opportunities(w)
        self.rejected(w, 'settle_in')
        validate(w)

    def test_eligibility_uses_stable_ids_current_place_and_window(self):
        w = self.world()
        ident = 'goon.choice.0.opening_shift'
        row = choice_report(w, ident)
        self.assertEqual([o['id'] for o in row['options']], ['work', 'decline'])
        self.assertEqual(row['options'][0]['availability'], 'unavailable')
        self.rejected(w, 'choose', choice_id=ident, option_id='work', message='Visit')
        self.go(w, 'store')
        self.assertEqual(choice_report(w, ident)['options'][0]['availability'], 'available')
        self.go(w, 'home')
        self.rejected(w, 'choose', choice_id=ident, option_id='work', message='Visit')
        self.rejected(w, 'choose', choice_id='goon.choice.0.crossroads', option_id='withdraw', message='days')
        self.rejected(w, 'choose', choice_id=ident, option_id='missing')
        self.rejected(w, 'choose', choice_id='missing', option_id='work')

    def test_hidden_options_are_absent_until_terms_are_actually_disclosed(self):
        w = self.world()
        ident = 'goon.choice.0.crossroads'
        self.assertNotIn('collection', [o['id'] for o in choice_report(w, ident)['options']])
        self.go(w, 'hub')
        self.pick(w, 'cal_intro', 'ask')
        advance_day(w)
        row = next(o for o in choice_report(w, ident)['options'] if o['id'] == 'collection')
        self.assertEqual(row['availability'], 'unavailable')
        self.assertIn('explicitly chosen faction', row['reason'])
        execute_command(w, 'join', faction='Harbor Syndicate')
        self.assertEqual(next(o for o in choice_report(w, ident)['options'] if o['id'] == 'collection')['availability'], 'available')

    def test_exactly_once_wage_survives_save_resume_and_repeated_selection(self):
        w = self.world()
        self.go(w, 'store')
        self.pick(w, 'opening_shift', 'work')
        self.assertEqual(w['player']['cash'], 60)
        self.assertEqual(actions_remaining(w), 2)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(w, path)
            resumed = load_career(path)
            self.assertEqual(w, resumed)
            self.rejected(resumed, 'choose', choice_id='goon.choice.0.opening_shift', option_id='work')
        self.assertEqual(len(w['daily_life']['transactions']), 1)
        validate(w)

    def test_criminal_referral_reuses_legal_resolution_without_second_payment(self):
        w = self.world(seed=17)
        self.go(w, 'hub')
        self.pick(w, 'cal_intro', 'ask')
        execute_command(w, 'join', faction='Harbor Syndicate')
        advance_day(w)
        legacy = deepcopy(w)
        from legal_engine import job
        expected = job(legacy, 'collection')
        result = self.pick(w, 'crossroads', 'collection')['result']['outcome']
        for key in ('player', 'people', 'factions', 'districts', 'cases', 'legal', 'job_attempts'):
            self.assertEqual(w[key], legacy[key], key)
        self.assertEqual(result['source_attempt'], expected['attempt'])
        self.assertEqual(result['payout'], expected['payout'])
        self.assertEqual(len(w['cases']), 1)
        self.assertTrue(w['cases'][0]['witnessed'])
        self.assertEqual(w['daily_life']['contacts'][daily_life.TESS]['memories'], [])
        self.until(w, 4)
        self.assertEqual(w['cases'][0]['status'], 'convicted')
        self.assertEqual(w['player']['cash'], 0)
        self.assertTrue(any(tx['cause'] == 'existing_rules' and tx['amount'] == -40 for tx in w['daily_life']['transactions']))
        validate(w)

    def test_private_legacy_jobs_and_legal_choices_do_not_inform_contacts(self):
        w = self.world(seed=17)
        advance_day(w)
        execute_command(w, 'join', faction='Harbor Syndicate')
        before = deepcopy(w['daily_life']['contacts'])
        execute_command(w, 'job', kind='collection')
        self.assertEqual(w['daily_life']['contacts'], before)
        self.assertTrue(w['cases'])
        execute_command(w, 'contest', case_id=str(w['cases'][0]['id']))
        self.assertEqual(w['daily_life']['contacts'], before)
        self.assertNotIn('collection', [o['id'] for o in choice_report(w, 'goon.choice.0.crossroads')['options']])
        self.assertNotIn('case', render_contacts(contact_report(w)).lower())
        validate(w)

    def test_unknown_saved_contact_fields_neither_override_identity_nor_leak(self):
        w = self.world()
        person = w['daily_life']['contacts'][daily_life.TESS]
        person.update(id='future_metadata', name='hidden alias', private_intent='unobserved plan')
        validate(w)  # additive unknown fields are deliberately retained in saves
        report = next(p for p in contact_report(w) if p['id'] == daily_life.TESS)
        self.assertEqual(report['name'], 'Tess Navarro')
        self.assertNotIn('private_intent', report)
        self.assertEqual(person['private_intent'], 'unobserved plan')

    def test_future_work_reference_is_an_observed_consequence(self):
        w = self.world()
        self.pick(w, 'promise', 'promise')
        advance_day(w)
        self.pick(w, 'crossroads', 'help')
        self.assertEqual(w['player']['cash'], 40)
        self.assertEqual(w['daily_life']['contacts'][daily_life.TESS]['standing'], 3)
        self.until(w, 5)
        self.go(w, 'store')
        row = choice_report(w, 'goon.choice.0.late_work')
        audit = next(o for o in row['options'] if o['id'] == 'audit')
        self.assertEqual((audit['availability'], audit['action_cost']), ('available', 2))
        self.pick(w, 'late_work', 'audit')
        self.assertEqual((w['player']['cash'], actions_remaining(w)), (65, 1))
        self.assertEqual(w['daily_life']['promises']['goon.promise.0.tess']['status'], 'kept')
        validate(w)

    def test_known_reference_can_be_held_and_restored_after_broken_commitments(self):
        w = run_campaign('relationship')
        while w['day'] < 26:
            advance_day(w)
            week, offset = divmod(w['day'] - 1, 7)
            if offset == 0:
                self.go(w, 'home')
                self.pick(w, 'promise', 'promise', week=week)
        self.go(w, 'store')
        report = choice_report(w, 'goon.choice.3.late_work')
        self.assertEqual(report['speaker'], 'Your neighborhood planner')
        audit = next(o for o in report['options'] if o['id'] == 'audit')
        self.assertEqual(audit['availability'], 'unavailable')
        self.assertIn('standing', audit['reason'])
        self.assertEqual(w['daily_life']['contacts'][daily_life.TESS]['standing'], 0)
        self.pick(w, 'late_work', 'work', week=3)
        self.until(w, 29)
        self.pick(w, 'opening_shift', 'work', week=4)
        self.until(w, 33)
        audit = next(o for o in choice_report(w, 'goon.choice.4.late_work')['options'] if o['id'] == 'audit')
        self.assertEqual(audit['availability'], 'available')
        validate(w)

    def test_choice_cost_shares_the_existing_three_actions(self):
        w = self.world()
        self.pick(w, 'promise', 'promise')
        advance_day(w)
        self.pick(w, 'crossroads', 'help')
        self.until(w, 5)
        self.go(w, 'store')
        execute_command(w, 'join', faction='Harbor Syndicate')
        for _ in range(2):
            execute_command(w, 'job', kind='courier')
        self.rejected(w, 'choose', choice_id='goon.choice.0.late_work', option_id='audit', message='exhausted')
        self.pick(w, 'late_work', 'work')
        self.assertEqual(actions_remaining(w), 0)
        validate(w)

    def test_refusal_is_available_after_actions_are_exhausted(self):
        w = self.world()
        execute_command(w, 'join', faction='Harbor Syndicate')
        for _ in range(3):
            execute_command(w, 'job', kind='courier')
        before_cash = w['player']['cash']
        self.pick(w, 'opening_shift', 'decline')
        self.assertEqual((w['player']['cash'], actions_remaining(w)), (before_cash, 0))
        validate(w)

    def test_offer_expiration_and_daily_processing_are_idempotent(self):
        w = self.world()
        advance_day(w)
        record = w['daily_life']['choices']['goon.choice.0.opening_shift']
        self.assertEqual(record['state'], 'expired')
        before = deepcopy(w)
        daily_life.begin_day(w)
        daily_life.begin_day(w)
        self.assertEqual(w, before)
        self.rejected(w, 'choose', choice_id=record['id'], option_id='decline')
        self.assertEqual(len([e for e in w['events'] if e['kind'] == 'life_expired' and e['choice_id'] == record['id']]), 1)
        validate(w)

    def test_unaccepted_invitation_never_invents_a_broken_promise(self):
        w = self.world()
        self.until(w, 4)
        self.assertEqual(w['daily_life']['promises'], {})
        self.assertEqual(w['daily_life']['contacts'][daily_life.TESS]['standing'], 0)
        validate(w)

    def test_broken_promise_is_proportionate_and_remembered_once(self):
        w = self.world()
        self.pick(w, 'promise', 'promise')
        self.until(w, 3)
        self.assertEqual(w['daily_life']['contacts'][daily_life.TESS]['standing'], -2)
        before = deepcopy(w['daily_life']['contacts'])
        self.until(w, 4)
        self.assertEqual(w['daily_life']['contacts'], before)
        self.go(w, 'store')
        self.pick(w, 'midweek_shift', 'work')
        self.assertEqual(w['player']['cash'], 60)
        validate(w)

    def test_renegotiation_has_a_real_followup_and_can_be_kept(self):
        w = self.world()
        self.pick(w, 'promise', 'promise')
        advance_day(w)
        self.pick(w, 'crossroads', 'renegotiate')
        self.until(w, 3)
        p = w['daily_life']['promises']['goon.promise.0.tess']
        self.assertEqual((p['status'], p['due_day']), ('pending', 5))
        self.until(w, 4)
        self.pick(w, 'rescheduled_help', 'help')
        self.assertEqual(w['daily_life']['promises'][p['id']]['status'], 'kept')
        self.go(w, 'store')
        self.rejected(w, 'choose', choice_id='goon.choice.0.midweek_shift', option_id='work', message='slot')
        validate(w)

    def test_work_can_displace_a_rescheduled_favor_without_orphaning_it(self):
        w = run_campaign('mixed')
        p = w['daily_life']['promises']['goon.promise.0.tess']
        self.assertEqual((p['status'], p['renegotiated'], p['resolved_day']), ('broken', True, 5))
        self.assertEqual(w['daily_life']['choices']['goon.choice.0.rescheduled_help']['state'], 'expired')
        validate(w)

    def test_room_is_due_on_seventh_transition_and_never_on_inspection(self):
        w = self.world()
        self.until(w, 6)
        before = deepcopy(w)
        for _ in range(3):
            life_report(w); home_report(w); opportunities(w)
        self.assertEqual(w, before)
        advance_day(w)
        self.assertEqual(w['player']['cash'], 10)
        self.assertEqual(w['daily_life']['housing']['next_due_day'], 14)
        self.assertEqual(len(w['daily_life']['housing']['history']), 1)
        before = deepcopy(w)
        daily_life.begin_day(w)
        self.assertEqual(w, before)
        validate(w)

    def test_room_payment_plan_and_reducer_share_order_and_existing_rejections(self):
        unenrolled = create_career()
        pending = create_career()
        execute_command(pending, 'settle_in')
        away = self.world()
        self.go(away, 'store')
        detained_home = self.world()
        detained_away = deepcopy(away)
        for detained in (detained_home, detained_away):
            detained['cases'].append(dict(id=1, crime='fixture', suspect='Rookie', status='charged', evidence=3))
            detained['player'].update(arrested=True, custody='pretrial')
        full = self.world()
        full_without_cash = self.world(cash=30)
        for paid in (full, full_without_cash):
            execute_command(paid, 'pay_room')
        at_home = 'Visit home while free to make a room payment'
        no_funds = 'No payable balance or no cash; basic home access remains available'
        cases = (
            (unenrolled, 'not_adopted', 'Daily life is not enabled; inspect life and explicitly settle_in'),
            (pending, 'pending', 'Daily life activates after the next wait; loading does not activate it'),
            (detained_home, 'detained', at_home), (detained_away, 'detained', at_home),
            (away, 'away_from_home', at_home), (self.world(cash=0), 'no_cash', no_funds),
            (full, 'no_payable_balance', no_funds), (full_without_cash, 'no_payable_balance', no_funds),
        )
        for world, reason, message in cases:
            with self.subTest(reason=reason):
                validate(world)
                before, rng = deepcopy(world), random.getstate()
                self.assertEqual(daily_life.room_payment_plan(world), (reason, None, 0))
                with self.assertRaises(ValueError) as caught:
                    execute_command(world, 'pay_room')
                self.assertEqual(str(caught.exception), message)
                self.assertEqual(world, before)
                self.assertEqual(random.getstate(), rng)

        world = self.world()
        world['actions_used'] = 3
        before = deepcopy(world)
        self.assertEqual(daily_life.room_payment_plan(world), ('eligible', 'prepay', 30))
        self.assertEqual(world, before)
        result = execute_command(world, 'pay_room')
        self.assertEqual(result['command'], 'pay_room')
        self.assertEqual((world['player']['cash'], actions_remaining(world)), (10, 0))
        self.assertEqual(world['navigation'], before['navigation'])
        self.assertEqual(world['daily_life']['housing']['next_due_day'], 7)

    def test_home_prepayment_has_receipt_and_is_not_charged_twice(self):
        w = self.world()
        execute_command(w, 'pay_room')
        self.assertEqual((w['player']['cash'], w['daily_life']['housing']['prepaid']), (10, 30))
        self.rejected(w, 'pay_room')
        self.until(w, 7)
        self.assertEqual((w['player']['cash'], w['daily_life']['housing']['prepaid']), (10, 0))
        self.assertEqual([r['operation'] for r in w['daily_life']['housing']['history']], ['prepay', 'due'])
        validate(w)

    def test_zero_cash_grace_is_bounded_and_maintenance_is_not_farmable(self):
        w = self.world(cash=0)
        self.until(w, 7)
        self.assertEqual((w['player']['cash'], w['daily_life']['housing']['arrears']), (0, 30))
        self.assertTrue(home_report(w))
        execute_command(w, 'choose', choice_id='goon.choice.room.1', option_id='help')
        self.assertEqual(w['daily_life']['housing']['arrears'], 20)
        self.rejected(w, 'choose', choice_id='goon.choice.room.1', option_id='help')
        self.until(w, 28)
        self.assertEqual((w['player']['cash'], w['daily_life']['housing']['arrears']), (0, 20))
        self.assertEqual(w['daily_life']['contacts'][daily_life.TESS]['standing'], 0)
        self.assertTrue(opportunities(w))
        validate(w)

    def test_partial_payment_and_low_cash_continuation(self):
        w = self.world(cash=5)
        self.until(w, 7)
        self.assertEqual((w['player']['cash'], w['daily_life']['housing']['arrears']), (0, 25))
        advance_day(w)
        self.go(w, 'store')
        self.pick(w, 'opening_shift', 'work', week=1)
        self.go(w, 'home')
        execute_command(w, 'pay_room')
        self.assertEqual((w['player']['cash'], w['daily_life']['housing']['arrears']), (0, 5))
        self.assertEqual(w['navigation']['home_id'], 'goon.poi.p031')
        validate(w)

    def test_custody_does_not_allow_work_or_home_payment(self):
        w = self.world()
        w['cases'].append(dict(id=1, crime='fixture', suspect='Rookie', status='charged', evidence=3))
        w['player'].update(arrested=True, custody='pretrial')
        self.rejected(w, 'choose', choice_id='goon.choice.0.promise', option_id='promise', message='detained')
        self.rejected(w, 'pay_room')
        self.assertTrue(home_report(w))
        advance_day(w)
        self.assertFalse(w['player']['arrested'])
        validate(w)

    def test_travel_consumes_tu_and_never_auto_performs_work(self):
        w = self.world()
        before = (w['player']['cash'], actions_remaining(w), len(w['daily_life']['transactions']))
        self.go(w, 'store')
        self.assertEqual((w['player']['cash'], actions_remaining(w), len(w['daily_life']['transactions'])), before)
        self.pick(w, 'opening_shift', 'work')
        self.go(w, 'home')
        self.assertEqual((w['navigation']['tu_used'], actions_remaining(w)), (2, 2))
        validate(w)

    def test_exhausted_travel_and_zero_cash_have_a_local_work_continuation(self):
        w = self.world(cash=0)
        for index in range(18):
            self.go(w, 'store' if index % 2 == 0 else 'home')
        self.rejected(w, 'travel', destination='p032', mode='auto', message='TU')
        self.rejected(w, 'choose', choice_id='goon.choice.0.opening_shift', option_id='work', message='Visit')
        self.assertEqual(w['player']['cash'], 0)
        advance_day(w)
        self.go(w, 'store')
        self.pick(w, 'crossroads', 'lawful')
        self.assertEqual((w['player']['cash'], w['navigation']['tu_used']), (20, 1))
        validate(w)

    def test_detached_views_and_pure_renderer_consume_no_randomness(self):
        w = self.world()
        before, rng = deepcopy(w), random.getstate()
        report = life_report(w)
        report['housing']['arrears'] = 999
        contacts = contact_report(w)
        contacts[0]['memories'].append({'secret': 'invented'})
        row = choice_report(w, 'goon.choice.0.opening_shift')
        text, letters = render_choice(row)
        self.assertEqual(letters, {'A': 'work', 'B': 'decline'})
        self.assertIn('Tess Navarro', text)
        self.assertIn('Unavailable', text)
        row['options'][0]['label'] = 'edited'
        render_life(life_report(w)); render_contacts(contact_report(w)); opportunities(w)
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)

    def test_every_historical_fixture_stays_opt_in_and_keeps_progress(self):
        for path in sorted(FIXTURES.rglob('*.json')):
            with self.subTest(path=path.name):
                w = load_career(path)
                self.assertNotIn('daily_life', w)
                if path.parent.name == 'm014':
                    self.assertEqual(w, json.loads(path.read_text(encoding='utf-8')))
                original = deepcopy(w)
                life_report(w)
                self.assertEqual(w, original)
                if 'navigation' not in w:
                    execute_command(w, 'enable_navigation', anchor='n13')
                    advance_day(w)
                self.go(w, 'home' if w['navigation']['home_id'] else 'hub')
                before = deepcopy(w)
                execute_command(w, 'settle_in')
                self.assertEqual(w['player'], before['player'])
                self.assertEqual(w['actions_used'], before['actions_used'])
                self.assertEqual(w['navigation']['location_id'], before['navigation']['location_id'])
                self.assertEqual(w['daily_life']['housing']['next_due_day'], before['day'] + 7)
                validate(w)

    def test_invalid_enrollment_and_command_shapes_are_atomic(self):
        w = create_career()
        self.go(w, 'store')
        self.rejected(w, 'settle_in', message='Visit')
        self.rejected(w, 'settle_in', unexpected='x')
        self.rejected(w, 'choose', choice_id=1, option_id='work')
        self.rejected(w, 'choose', choice_id='x', option_id='work', extra='x')

    def test_failed_effect_cannot_commit_cash_memory_or_choice(self):
        w = self.world()
        self.go(w, 'store')
        before = deepcopy(w)
        def fail(*args, **kwargs):
            raise RuntimeError('injected event failure')
        with patch('daily_life._memory', side_effect=fail):
            with self.assertRaises(RuntimeError):
                self.pick(w, 'opening_shift', 'work')
        self.assertEqual(w, before)

    def test_malformed_nested_saves_are_rejected_on_disk(self):
        w = run_campaign('relationship')
        mutations = [lambda x: x.update(daily_life_version=True), lambda x: x.update(daily_life_version=2),
            lambda x: x.pop('daily_life_version'), lambda x: x['daily_life'].update(rules_version=2),
            lambda x: x['daily_life'].update(content_fingerprint='changed'),
            lambda x: x['daily_life'].update(contacts=[]), lambda x: x['daily_life']['contacts'].pop(daily_life.TESS),
            lambda x: x['daily_life']['contacts'][daily_life.TESS].update(standing=11),
            lambda x: x['daily_life']['housing'].update(arrears=-1),
            lambda x: x['daily_life']['housing'].update(next_due_day=7),
            lambda x: x['daily_life']['promises']['goon.promise.0.tess'].update(due_day=100),
            lambda x: x['daily_life']['promises']['goon.promise.0.tess'].update(status='pending'),
            lambda x: x['daily_life']['transactions'][0].update(amount=999),
            lambda x: x['daily_life']['transactions'].append(deepcopy(x['daily_life']['transactions'][0])),
            lambda x: x['daily_life']['choices']['goon.choice.0.opening_shift']['selection'].update(option_id='invented'),
            lambda x: x['daily_life'].update(last_tick_day=6), lambda x: x['player'].update(cash=999),
            lambda x: x.update(events=[e for e in x['events'] if e['kind'] != 'life_housing'])]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.json'
            for index, mutation in enumerate(mutations):
                malformed = deepcopy(w)
                mutation(malformed)
                path.write_text(json.dumps(malformed), encoding='utf-8')
                with self.subTest(index=index), self.assertRaises(ValueError):
                    load_career(path)

    def test_invented_wage_without_an_opportunity_is_rejected(self):
        w = self.world()
        self.go(w, 'store')
        self.pick(w, 'opening_shift', 'work')
        fake = deepcopy(w['daily_life']['transactions'][0])
        fake.update(id='goon.transaction.2', before=60, after=80, source_id='invented')
        w['daily_life']['transactions'].append(fake)
        w['player']['cash'] = 80
        e = next(e for e in w['events'] if e['kind'] == 'life_transaction')
        w['events'].append(dict(deepcopy(e), **fake))
        with self.assertRaisesRegex(ValueError, 'unique outcome'):
            validate(w)

    def test_life_content_is_detached_pinned_and_validated(self):
        data = life_content.load()
        data['contacts'][daily_life.TESS]['name'] = 'changed'
        self.assertEqual(life_content.load()['contacts'][daily_life.TESS]['name'], 'Tess Navarro')
        mutations = [lambda x: x.update(content_version=True), lambda x: x.update(home_id=[]),
            lambda x: x['choices']['opening_shift'].update(speaker=[]),
            lambda x: x['choices']['opening_shift']['options'][0].update(actions=-1),
            lambda x: x['choices']['opening_shift']['options'][0].update(actions=0),
            lambda x: x['choices']['opening_shift']['options'][0].update(effect=[]),
            lambda x: x['choices']['opening_shift']['options'][0].update(pay=-1),
            lambda x: x['choices']['opening_shift']['options'].append(deepcopy(x['choices']['opening_shift']['options'][0]))]
        for index, mutation in enumerate(mutations):
            data = life_content.load()
            mutation(data)
            with self.subTest(index=index), self.assertRaises(ValueError):
                life_content.validate(data)
        w = self.world()
        with patch('daily_life_state.fingerprint', return_value='incompatible'):
            with self.assertRaisesRegex(ValueError, 'pinned'):
                validate(w)

    def test_failed_save_keeps_previous_good_room_receipts(self):
        w = self.world()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(w, path)
            previous = path.read_bytes()
            execute_command(w, 'pay_room')
            before = deepcopy(w)
            with patch('career_persistence.os.fsync', side_effect=OSError('injected flush failure')):
                with self.assertRaises(OSError):
                    save_career(w, path)
            self.assertEqual(path.read_bytes(), previous)
            self.assertEqual(w, before)

    def test_five_campaigns_replay_and_resume_exactly_with_distinct_outcomes(self):
        worlds = {}
        for branch in BRANCH_SEEDS:
            with self.subTest(branch=branch):
                a = run_campaign(branch)
                b = run_campaign(branch, resume=True)
                self.assertEqual(a, b)
                worlds[branch] = a
                validate(a)
        self.assertEqual([worlds[b]['player']['cash'] for b in BRANCH_SEEDS], [90, 110, 75, 0, 70])
        self.assertEqual(worlds['relationship']['daily_life']['promises']['goon.promise.0.tess']['status'], 'kept')
        self.assertEqual(worlds['low_cash']['daily_life']['housing']['arrears'], 20)
        self.assertEqual(worlds['criminal']['daily_life']['contacts'][daily_life.TESS]['standing'], 0)

    def test_dictionary_insertion_order_does_not_change_replay(self):
        def reverse(value):
            if isinstance(value, dict):
                return {k: reverse(v) for k, v in reversed(list(value.items()))}
            if isinstance(value, list):
                return [reverse(v) for v in value]
            return value
        a = self.world(seed=17)
        b = reverse(deepcopy(a))
        for world in (a, b):
            play_day(world, 'mixed')
        for _ in range(13):
            for world in (a, b):
                advance_day(world)
                play_day(world, 'mixed')
            b = reverse(b)
            self.assertEqual(a, b)
        validate(a)

    def test_long_continuation_does_not_stick_debt_or_leave_expired_offers_open(self):
        for branch in ('lawful', 'relationship', 'low_cash'):
            with self.subTest(branch=branch):
                # All five paths resume daily for their first week above; keep
                # one longer disk path here and exercise the other policies in memory.
                w = run_campaign(branch, days=56, resume=branch == 'lawful')
                self.assertGreaterEqual(w['player']['cash'], 0)
                self.assertEqual(w['daily_life']['housing']['arrears'], 0)
                self.assertTrue(all(r['state'] != 'open' or r['expires_day'] > w['day'] for r in w['daily_life']['choices'].values()))
                self.assertTrue(all(-10 <= p['standing'] <= 10 for p in w['daily_life']['contacts'].values()))
                validate(w)

    def test_independent_process_hashseeds_produce_the_same_story(self):
        code = ('import json,hashlib; from daily_life_campaigns import run_campaign; '
                'w=run_campaign("mixed"); print(hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest())')
        digests = [subprocess.check_output([sys.executable, '-B', '-c', code],
                   env=dict(os.environ, PYTHONHASHSEED=seed), text=True).strip() for seed in ('0', '17', '99')]
        self.assertEqual(len(set(digests)), 1)

    def test_cli_displays_context_letters_and_resumes_real_outcome(self):
        script = Path(__file__).resolve().parents[1] / 'gameplay.py'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            commands = 'life\nsettle_in\nwait\ntravel p032\nchoices goon.choice.0.opening_shift\nchoose goon.choice.0.opening_shift A\ntravel home\nhome\ncontacts\nsave\nquit\n'
            run = subprocess.run([sys.executable, '-B', str(script), '--save', str(path)], input=commands,
                                 text=True, capture_output=True, cwd=folder, check=True)
            self.assertIn('Tess Navarro | A place on the repair roster', run.stdout)
            self.assertIn('A. Work the repair shift', run.stdout)
            self.assertIn('Earned $20', run.stdout)
            w = load_career(path)
            self.assertEqual((w['player']['cash'], w['day'], w['navigation']['tu_used']), (60, 1, 2))
            resumed = subprocess.run([sys.executable, '-B', str(script), '--load', '--save', str(path)],
                input='life\nchoose goon.choice.0.opening_shift work\nquit\n', text=True,
                capture_output=True, cwd=folder, check=True)
            self.assertIn('already closed', resumed.stdout)
            self.assertEqual(load_career(path), w)


if __name__ == '__main__':
    unittest.main()
