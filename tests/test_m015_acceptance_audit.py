"""Mission 010: independent acceptance cases and confirmed integrity regressions."""
from copy import deepcopy
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from career_state import validate
import daily_life
from game_service import (actions_remaining, advance_day, choice_report, contact_report,
                          create_career, execute_command, load_career, save_career)
from life_content import load
from simulation import advance as legacy_clock


class M015AcceptanceAuditTests(unittest.TestCase):
    def fresh(self, *, seed=3, cash=40):
        w = create_career(seed)
        w['player']['cash'] = cash  # a prior-career resource fixture, before adoption
        execute_command(w, 'settle_in')
        advance_day(w)
        return w

    def pick(self, w, definition, option, week=0):
        return execute_command(w, 'choose', choice_id=f'goon.choice.{week}.{definition}', option_id=option)

    def go(self, w, destination):
        ident = {'home': 'goon.poi.p031', 'store': 'goon.poi.p032', 'hub': 'goon.neighborhood.n13'}[destination]
        if w['navigation']['location_id'] != ident:
            execute_command(w, 'travel', destination=ident, mode='auto')

    def until(self, w, day):
        while w['day'] < day:
            advance_day(w)

    def reject(self, w, command, **args):
        before = deepcopy(w)
        with self.assertRaises(ValueError):
            execute_command(w, command, **args)
        self.assertEqual(w, before)

    def assert_bad_disk_save(self, w, pattern):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'malformed.json'
            path.write_text(json.dumps(w), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, pattern):
                load_career(path)

    def test_missing_accepted_promise_is_rejected_on_load(self):
        w = self.fresh()
        self.pick(w, 'promise', 'promise')
        w['daily_life']['promises'].clear()
        self.assert_bad_disk_save(w, 'promises')

    def test_promise_cannot_reference_another_weeks_accepted_invitation(self):
        w = self.fresh()
        self.pick(w, 'promise', 'promise')
        self.until(w, 8)
        self.pick(w, 'promise', 'promise', week=1)
        w['daily_life']['promises']['goon.promise.1.tess']['source_id'] = 'goon.choice.0.promise'
        self.assert_bad_disk_save(w, 'promises')

    def test_renegotiation_flag_cannot_contradict_its_committed_choice(self):
        w = self.fresh()
        self.pick(w, 'promise', 'promise')
        advance_day(w)
        self.pick(w, 'crossroads', 'renegotiate')
        w['daily_life']['promises']['goon.promise.0.tess'].update(renegotiated=False, due_day=3)
        self.assert_bad_disk_save(w, 'renegotiated')

    def test_skipped_legacy_clock_days_resume_without_backdated_open_offers(self):
        w = self.fresh()
        for _ in range(7):
            legacy_clock(w)
        validate(w)  # retained old daily markers are explicitly loadable
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(w, path)
            resumed = load_career(path)
            self.assertEqual(resumed, w)
            self.assertEqual(resumed['daily_life']['last_tick_day'], 1)
            advance_day(resumed)
            self.assertEqual(resumed['day'], 9)
            validate(resumed)
            self.assertTrue(all(r['state'] != 'open' or r['expires_day'] > 9 for r in resumed['daily_life']['choices'].values()))
            self.assertNotIn('goon.choice.1.opening_shift', resumed['daily_life']['choices'])
            self.reject(resumed, 'choose', choice_id='goon.choice.1.opening_shift', option_id='work')
            self.go(resumed, 'store')
            self.pick(resumed, 'crossroads', 'lawful', week=1)
            self.assertEqual(resumed['player']['cash'], 30)  # actual $30 room settlement, then $20 wage
            save_career(resumed, path)
            self.assertEqual(load_career(path), resumed)
            before = deepcopy(resumed)
            daily_life.begin_day(resumed)
            self.assertEqual(resumed, before)

    def test_nested_memory_metadata_is_preserved_but_not_public(self):
        w = self.fresh()
        self.pick(w, 'promise', 'promise')
        memory = w['daily_life']['contacts'][daily_life.TESS]['memories'][0]
        memory['private_note'] = 'unobserved internal metadata'
        validate(w)
        before = deepcopy(w)
        for person in contact_report(w):
            for row in person['memories']:
                self.assertNotIn('private_note', row)
        self.assertEqual(w, before)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(w, path)
            restored = load_career(path)
            self.assertEqual(restored, w)
            self.assertEqual(restored['daily_life']['contacts'][daily_life.TESS]['memories'][0]['private_note'], memory['private_note'])

    def test_stale_cli_letters_keep_their_displayed_stable_ids(self):
        script = Path(__file__).resolve().parents[1] / 'gameplay.py'
        # B initially means decline. A successful Cal referral later inserts
        # courier before decline, but the old displayed B must still decline.
        commands = '\n'.join(('settle_in', 'wait', 'choices goon.choice.0.late_work', 'save',
            'choose goon.choice.0.late_work work', 'choose goon.choice.0.opening_shift work', 'save',
            'travel n13', 'choose goon.choice.0.cal_intro ask', 'join 1', 'wait',
            'choose goon.choice.0.crossroads collection', 'wait', 'wait', 'wait',
            'choose goon.choice.0.late_work B', 'quit', ''))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            run = subprocess.run([sys.executable, '-B', str(script), '--seed', '3', '--save', str(path)],
                input=commands, text=True, capture_output=True, cwd=folder, check=True)
            self.assertIn('B. Leave the allocation for someone else', run.stdout)
            self.assertEqual(run.stdout.count('Cannot complete command:'), 2)
            self.assertIn('Available on days 5 through 6', run.stdout)
            self.assertIn('Visit goon.poi.p032', run.stdout)
            rejected_checkpoint = load_career(path.with_suffix('.json.bak'))
            self.assertEqual((rejected_checkpoint['day'], rejected_checkpoint['command_sequence']), (1, 2))
            self.assertEqual((rejected_checkpoint['player']['cash'], actions_remaining(rejected_checkpoint),
                              rejected_checkpoint['navigation']['tu_used']), (40, 3, 0))
            w = load_career(path)
            self.assertEqual(w['daily_life']['choices']['goon.choice.0.late_work']['selection']['option_id'], 'decline')
            self.assertEqual(w['job_attempts'], 1)
            self.assertTrue(w['daily_life']['choices']['goon.choice.0.crossroads']['selection']['outcome']['success'])
            resumed = subprocess.run([sys.executable, '-B', str(script), '--load', '--save', str(path)],
                input='choose goon.choice.0.late_work B\nquit\n', text=True,
                capture_output=True, cwd=folder, check=True)
            self.assertIn('Display choices first', resumed.stdout)
            self.assertEqual(load_career(path), w)

    def test_room_credit_rechecks_balance_after_preview_and_payment(self):
        w = self.fresh(cash=25)
        self.until(w, 7)
        ident = 'goon.choice.room.1'
        self.assertEqual(w['daily_life']['housing']['arrears'], 5)
        self.assertEqual(choice_report(w, ident)['options'][0]['availability'], 'available')
        advance_day(w)
        self.go(w, 'store')
        self.pick(w, 'opening_shift', 'work', week=1)
        self.go(w, 'home')
        execute_command(w, 'pay_room')
        self.assertEqual(w['daily_life']['housing']['arrears'], 0)
        self.reject(w, 'choose', choice_id=ident, option_id='help')
        validate(w)

    def test_pending_m014_adoption_roundtrip_keeps_spent_actions_and_tu(self):
        path = Path(__file__).parent / 'fixtures' / 'm014' / 'career.json'
        w = load_career(path)
        self.assertNotIn('daily_life', w)
        self.go(w, 'home')
        before = deepcopy(w)
        execute_command(w, 'settle_in')
        with tempfile.TemporaryDirectory() as folder:
            save = Path(folder) / 'career.json'
            save_career(w, save)
            resumed = load_career(save)
            self.assertEqual(resumed, w)
            self.assertEqual(resumed['player'], before['player'])
            self.assertEqual(resumed['navigation'], before['navigation'])
            self.assertEqual(actions_remaining(resumed), 0)
            self.reject(resumed, 'choose', choice_id='goon.choice.0.promise', option_id='promise')
            advance_day(resumed)
            self.assertEqual(actions_remaining(resumed), 3)
            self.assertEqual(resumed['daily_life']['housing']['next_due_day'], 7)
            validate(resumed)

    def prepare_option(self, definition, option):
        w = self.fresh(cash=0 if definition == 'room_review' else 40)
        if definition in ('rescheduled_help',) or (definition == 'crossroads' and option in ('help', 'renegotiate', 'withdraw')) or (definition == 'late_work' and option == 'audit'):
            self.pick(w, 'promise', 'promise')
        if (definition == 'crossroads' and option == 'collection') or (definition == 'late_work' and option == 'courier'):
            self.go(w, 'hub')
            self.pick(w, 'cal_intro', 'ask')
            execute_command(w, 'join', faction='Harbor Syndicate')
        if definition == 'rescheduled_help':
            self.until(w, 2)
            self.pick(w, 'crossroads', 'renegotiate')
        if definition == 'late_work' and option in ('audit', 'courier'):
            self.until(w, 2)
            self.pick(w, 'crossroads', 'help' if option == 'audit' else 'collection')
        day = dict(opening_shift=1, promise=1, cal_intro=1, crossroads=2,
                   midweek_shift=4, late_work=5, rescheduled_help=4, room_review=7)[definition]
        self.until(w, day)
        content = load()['choices'][definition]
        row = next(o for o in content['options'] if o['id'] == option)
        if row.get('place'):
            self.go(w, {'home': 'home', 'goon.poi.p032': 'store', 'goon.neighborhood.n13': 'hub'}[row['place']])
        ident = 'goon.choice.room.1' if definition == 'room_review' else f'goon.choice.0.{definition}'
        return w, ident, row

    def test_all_twenty_one_options_settle_once_and_have_saveable_continuations(self):
        count = 0
        for definition, content in sorted(load()['choices'].items()):
            for option in content['options']:
                with self.subTest(definition=definition, option=option['id']):
                    w, ident, row = self.prepare_option(definition, option['id'])
                    public = next(o for o in choice_report(w, ident)['options'] if o['id'] == option['id'])
                    self.assertEqual(public['availability'], 'available')
                    actions, tu, day, rng = actions_remaining(w), w['navigation']['tu_used'], w['day'], random.getstate()
                    execute_command(w, 'choose', choice_id=ident, option_id=option['id'])
                    self.assertEqual(actions_remaining(w), actions - row['actions'])
                    self.assertEqual((w['navigation']['tu_used'], w['day']), (tu, day))
                    self.assertEqual(random.getstate(), rng)
                    self.reject(w, 'choose', choice_id=ident, option_id=option['id'])
                    validate(w)
                    with tempfile.TemporaryDirectory() as folder:
                        path = Path(folder) / 'career.json'
                        save_career(w, path)
                        resumed = load_career(path)
                        self.assertEqual(resumed, w)
                        self.reject(resumed, 'choose', choice_id=ident, option_id=option['id'])
                        self.until(resumed, resumed['daily_life']['choices'][ident]['expires_day'])
                        validate(resumed)
                        self.assertEqual(len([e for e in resumed['events'] if e['kind'] == 'life_choice' and e['choice_id'] == ident]), 1)
                    count += 1
        self.assertEqual(count, 21)


if __name__ == '__main__':
    unittest.main()
