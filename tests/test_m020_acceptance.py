"""Mission 027 independent regressions for inherited work/housing provenance."""
from copy import deepcopy
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from career_state import validate
from game_service import create_career,execute_command,advance_day,load_career,save_career
from simulation import event
import choice_engine
import daily_life
from life_content import load
import ordinary_life
import test_ordinary_life as scenarios


class M020AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.h=scenarios.OrdinaryLifeTests()

    def forge_choice(self,w,key,option,week=0):
        """Generate edited-save records with native output but bypass eligibility.

        This is an adversarial fixture generator, never a player command path.
        """
        ident=f'goon.choice.{week}.{key}';record=w['daily_life']['choices'][ident]
        spec=load()['choices'][key];cost=next(o['actions'] for o in spec['options'] if o['id']==option)
        choice_engine.resolve(w,record,spec,option,lambda o:('available',None),
            lambda o:daily_life._apply(w,w['daily_life'],record,spec,o))
        ordinary_life.synchronize(w);w['command_sequence']+=1
        w['actions_used']=min(3,w['actions_used']+cost)
        event(w,'player_command','Edited source receipt',command='choose',command_id=w['command_sequence'],
            actor='player',arguments=dict(choice_id=ident,option_id=option),action_cost=cost,cause='player_command')

    def assert_edited_rejects(self,w):
        before,rng=deepcopy(w),random.getstate()
        with self.assertRaises(ValueError):validate(w)
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'edited.json';p.write_text(json.dumps(w),encoding='utf-8')
            with self.assertRaises(ValueError):load_career(p)

    def reference_world(self,away=False):
        w=create_career(17);execute_command(w,'settle_in');advance_day(w)
        execute_command(w,'choose',choice_id='goon.choice.0.promise',option_id='promise')
        execute_command(w,'enable_ordinary');advance_day(w)
        if away:
            self.h.go(w,'store');self.forge_choice(w,'crossroads','help')
        else:execute_command(w,'choose',choice_id='goon.choice.0.crossroads',option_id='help')
        self.h.until(w,4);self.h.repair(w);self.h.until(w,5);self.h.go(w,'store')
        self.forge_choice(w,'late_work','audit')
        return w

    def clone_reviews(self,w):
        source=w['daily_life']['choices']['goon.choice.room.1']['source_id']
        for suffix in ('998','999'):
            daily_life._open(w,'goon.choice.room.'+suffix,'room_review',0,7,14,source)

    def test_remote_repair_cannot_grant_employment_or_wages(self):
        w=self.h.ready(False);self.forge_choice(w,'crossroads','lawful')
        self.assert_edited_rejects(w)

    def test_fourth_action_repair_cannot_grant_employment(self):
        w=self.h.ready(False);self.h.go(w,'store');execute_command(w,'join',faction='Harbor Syndicate')
        for _ in range(3):execute_command(w,'job',kind='courier')
        self.forge_choice(w,'crossroads','lawful');self.assert_edited_rejects(w)

    def test_unearned_audit_cannot_be_used_as_an_employment_source(self):
        w=self.h.ready(False);self.h.until(w,5);self.h.go(w,'store')
        self.forge_choice(w,'late_work','audit');self.assert_edited_rejects(w)

    def test_future_real_reference_cannot_justify_earlier_audit(self):
        w=self.h.ready(False);self.h.until(w,5);self.h.go(w,'store');self.forge_choice(w,'late_work','audit')
        # Build the rest of a contradictory save without asking the validator
        # under test to bless the deliberately edited earlier command.
        with patch('game_service.validate',side_effect=lambda world:world):
            self.h.until(w,8);self.h.go(w)
            execute_command(w,'choose',choice_id='goon.choice.1.promise',option_id='promise')
            advance_day(w);execute_command(w,'choose',choice_id='goon.choice.1.crossroads',option_id='help')
        self.assertTrue(any(m['fact']=='promise_kept' for m in w['daily_life']['contacts'][daily_life.TESS]['memories']))
        self.assert_edited_rejects(w)

    def test_reference_invitation_and_delivery_require_player_receipts(self):
        original=self.reference_world()
        for key in ('promise','crossroads'):
            with self.subTest(source=key):
                w=deepcopy(original);cid=w['daily_life']['choices']['goon.choice.0.'+key]['selection']['command_id']
                next(e for e in w['events'] if e['kind']=='player_command' and e['command_id']==cid)['actor']='unrelated_npc'
                self.assert_edited_rejects(w)

    def test_reference_delivery_needs_its_historical_home_location(self):
        self.assert_edited_rejects(self.reference_world(away=True))

    def test_counterfeit_room_allocations_reject_before_play(self):
        w=self.h.ready(False,0);self.h.until(w,7);self.clone_reviews(w)
        self.assert_edited_rejects(w)

    def test_counterfeit_credit_rejection_cannot_mutate_the_original_world(self):
        w=self.h.ready(False,0);self.h.until(w,7);self.clone_reviews(w)
        before,rng=deepcopy(w),random.getstate()
        with self.assertRaises(ValueError):execute_command(w,'choose',choice_id='goon.choice.room.998',option_id='help')
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def test_room_review_requires_its_real_due_source_and_window(self):
        original=self.h.ready(False,0);self.h.until(original,7)
        for edit in ('source','window','week'):
            with self.subTest(edit=edit):
                w=deepcopy(original);r=w['daily_life']['choices']['goon.choice.room.1']
                if edit=='source':r['source_id']='goon.obligation.room.999'
                elif edit=='window':r.update(open_day=6,expires_day=13)
                else:r['week']=1
                self.assert_edited_rejects(w)

    def test_genuine_reference_and_audit_roundtrip_unchanged(self):
        w=self.reference_world();before,rng=deepcopy(w),random.getstate();validate(w)
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng);self.h.roundtrip(w)

    def test_genuine_catchup_reviews_remain_separate_funded_allocations(self):
        w=create_career(17);w['player']['cash']=0;execute_command(w,'settle_in');advance_day(w)
        w['day']=14;advance_day(w)
        self.assertEqual(w['daily_life']['housing']['arrears'],30)
        for cycle in (1,2):execute_command(w,'choose',choice_id=f'goon.choice.room.{cycle}',option_id='help')
        self.assertEqual(w['daily_life']['housing']['arrears'],10);self.h.roundtrip(w)

    def forged_repayment(self,attribution):
        w=self.h.ready(False,0);self.h.until(w,7)
        self.h.choose(w,'borrow',ordinary_life.SUPPORT);execute_command(w,'pay_room')
        cid=w['command_sequence']+1;previous=cid-1
        w['player']['cash']=20
        tx=daily_life.record_balance(w,'existing_rules',f'goon.command.{cid}',
            command_id=None if attribution in ('null','day_frame') else previous if attribution=='other' else cid)
        if attribution in ('previous_frame','day_frame'):
            item=next(e for e in w['events'] if e['kind']=='life_transaction' and e['id']==tx)
            w['events'].remove(item)
            receipt=(next(e for e in reversed(w['events']) if e['kind']=='player_command' and
                e['command']=='wait' and e['day']==w['day']) if attribution=='day_frame' else
                next(e for e in w['events'] if e['kind']=='player_command' and e['command_id']==previous))
            w['events'].insert(w['events'].index(receipt),item)
        ordinary_life.choose(w,ordinary_life.REPAY,'repay');w['command_sequence']+=1;w['actions_used']+=1
        event(w,'player_command','Edited repayment receipt',command='ordinary_choose',command_id=cid,
            actor='player',arguments=dict(offer_id=ordinary_life.REPAY,option_id='repay'),action_cost=1,cause='player_command')
        return w

    def test_repayment_cannot_be_financed_by_an_extra_closed_command_credit(self):
        for attribution in ('current','null','other','previous_frame','day_frame'):
            with self.subTest(attribution=attribution):self.assert_edited_rejects(self.forged_repayment(attribution))

    def test_saved_action_counter_cannot_erase_committed_daily_costs(self):
        original=self.h.ready(False);execute_command(original,'join',faction='Harbor Syndicate')
        for _ in range(3):execute_command(original,'job',kind='courier')
        for field,value in (('actions_used',0),('action_day',original['day']-1)):
            with self.subTest(field=field):
                w=deepcopy(original);w[field]=value;self.assert_edited_rejects(w)

    def test_fourth_job_after_erased_counter_rejects_atomically(self):
        w=self.h.ready(False);execute_command(w,'join',faction='Harbor Syndicate')
        for _ in range(3):execute_command(w,'job',kind='courier')
        w['actions_used']=0;before,rng=deepcopy(w),random.getstate()
        with self.assertRaises(ValueError):execute_command(w,'job',kind='courier')
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def test_pending_work_rent_and_support_have_separate_valid_settlements(self):
        w=self.h.ready(True,0);self.h.until(w,6);self.h.choose(w,'negotiate')
        advance_day(w);self.assertEqual(w['daily_life']['housing']['arrears'],10)
        self.h.choose(w,'borrow',ordinary_life.SUPPORT);self.h.choose(w,'work')
        self.assertEqual(w['player']['cash'],44);self.assertEqual(w['actions_used'],3)
        execute_command(w,'pay_room');advance_day(w);self.h.repair(w)
        self.h.choose(w,'repay',ordinary_life.REPAY)
        self.assertEqual(w['player']['cash'],34);self.assertEqual(w['daily_life']['housing']['arrears'],0)
        self.h.roundtrip(w);self.h.reject_choice(w,'work');self.h.reject_choice(w,'borrow',ordinary_life.SUPPORT)

    def test_institution_enrollment_cannot_sponsor_a_fictitious_cash_credit(self):
        w=self.h.ready(False,0);w['player']['cash']=20
        # Native enrollment currently labels the unexplained extra cash as an
        # existing-rules transaction. It must not become a valid saved source.
        before,rng=deepcopy(w),random.getstate()
        with self.assertRaises(ValueError):execute_command(w,'enable_institutions')
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)


if __name__=='__main__':unittest.main()
