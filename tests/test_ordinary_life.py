"""M020 source-backed work, conditional support and ordinary survival regressions."""
from copy import deepcopy
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from career_state import validate
from game_service import (create_career,execute_command,advance_day,save_career,load_career)
import ordinary_life as ordinary


class OrdinaryLifeTests(unittest.TestCase):
    def ready(self, work=True, cash=40, seed=17):
        w=create_career(seed);w['player']['cash']=cash
        execute_command(w,'settle_in');advance_day(w)
        execute_command(w,'enable_ordinary');advance_day(w)
        if work:self.repair(w)
        return w

    def go(self,w,place='home'):
        target={'home':'goon.poi.p031','store':'goon.poi.p032','hub':'goon.neighborhood.n13'}[place]
        if w['navigation']['location_id']!=target:
            execute_command(w,'travel',destination=target,mode='auto')

    def until(self,w,day):
        while w['day']<day:advance_day(w)

    def repair(self,w):
        week,offset=divmod(w['day']-w['daily_life']['activation_day'],7)
        key,option={0:('opening_shift','work'),1:('crossroads','lawful'),3:('midweek_shift','work'),4:('late_work','work')}[offset]
        self.go(w,'store');execute_command(w,'choose',choice_id=f'goon.choice.{week}.{key}',option_id=option);self.go(w)

    def choose(self,w,option,ident='goon.ordinary.batch.0'):
        return execute_command(w,'ordinary_choose',offer_id=ident,option_id=option)

    def reject(self,w,command='ordinary_choose',**args):
        before,rng=deepcopy(w),random.getstate()
        with self.assertRaises(ValueError):execute_command(w,command,**args)
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def reject_choice(self,w,option,ident='goon.ordinary.batch.0'):
        self.reject(w,offer_id=ident,option_id=option)

    def roundtrip(self,w):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'career.json';save_career(w,p);self.assertEqual(load_career(p),w)

    def test_explicit_pending_adoption_does_not_refresh_or_pay(self):
        w=create_career();before=deepcopy(w)
        self.assertFalse(ordinary.report(w)['enabled']);self.assertEqual(w,before)
        self.reject(w,'enable_ordinary')
        execute_command(w,'settle_in');advance_day(w);before=deepcopy(w)
        execute_command(w,'enable_ordinary')
        for k in ('player','daily_life','navigation','actions_used'):self.assertEqual(w[k],before[k])
        self.assertTrue(ordinary.report(w)['pending']);self.reject_choice(w,'work')
        self.reject(w,'enable_ordinary');advance_day(w);self.roundtrip(w)

    def test_old_repair_observed_once_without_another_wage_or_memory(self):
        w=self.ready(False);before=deepcopy(w['player']);self.repair(w)
        self.assertEqual(w['player']['cash'],before['cash']+20)
        self.assertEqual(w['ordinary']['employment'],1)
        self.assertEqual(len(w['daily_life']['contacts']['goon.contact.tess']['memories']),1)
        snapshot=deepcopy(w);ordinary.synchronize(w);self.assertEqual(w,snapshot)

    def test_no_retroactive_employment_credit_on_historical_adoption(self):
        w=create_career();execute_command(w,'settle_in');advance_day(w);self.repair(w)
        execute_command(w,'enable_ordinary');advance_day(w)
        self.assertEqual(w['ordinary']['employment'],0);self.assertEqual(w['ordinary']['observed_work'],[])

    def test_home_batch_wage_is_once_two_actions_and_no_travel(self):
        w=self.ready();self.until(w,3);cash=w['player']['cash'];nav=deepcopy(w['navigation'])
        r=self.choose(w,'work');self.assertEqual(r['actions_remaining'],1)
        self.assertEqual(w['player']['cash'],cash+24);self.assertEqual(w['navigation'],nav)
        self.assertEqual(w['ordinary']['employment'],2);self.roundtrip(w);self.reject_choice(w,'work')

    def test_successful_reschedule_pins_wage_and_future_deadline(self):
        w=self.ready();self.until(w,3);cash=w['player']['cash'];self.choose(w,'negotiate')
        row=w['ordinary']['offers']['goon.ordinary.batch.0']
        self.assertEqual((row['state'],row['open_day'],row['expires_day'],row['pay']),('reserved',4,6,24))
        self.assertEqual(w['player']['cash'],cash);self.reject_choice(w,'work');self.reject_choice(w,'negotiate')
        advance_day(w);self.choose(w,'work');self.assertEqual(w['player']['cash'],cash+24)

    def test_failed_negotiation_is_bounded_and_does_not_destroy_work(self):
        w=self.ready(False);self.until(w,3);before=deepcopy(w['daily_life']['contacts'])
        result=self.choose(w,'negotiate');self.assertIn('declines',result['result']['message'])
        self.assertEqual(result['actions_remaining'],2);self.assertEqual(w['daily_life']['contacts'],before)
        self.reject_choice(w,'negotiate');advance_day(w);self.repair(w);self.choose(w,'work')

    def test_missed_accepted_delivery_has_one_consequence_and_recovery(self):
        w=self.ready();self.until(w,3);self.choose(w,'negotiate');self.until(w,6)
        self.assertEqual(w['ordinary']['employment'],0)
        facts=w['daily_life']['contacts']['goon.contact.tess']['memories']
        self.assertEqual(sum(m['fact']=='delivery_missed' for m in facts),1)
        self.reject_choice(w,'work');self.until(w,8);self.repair(w)
        self.assertEqual(w['ordinary']['employment'],1);self.assertFalse(w['player']['arrested'])

    def test_reserved_work_can_be_withdrawn_before_delivery_once(self):
        w=self.ready();self.until(w,3);self.choose(w,'negotiate');cash=w['player']['cash']
        self.choose(w,'withdraw')
        self.assertEqual(w['player']['cash'],cash)
        self.assertEqual(w['ordinary']['employment'],0)
        self.reject_choice(w,'withdraw');self.until(w,8);self.repair(w);self.roundtrip(w)
        memories=w['daily_life']['contacts']['goon.contact.tess']['memories']
        self.assertEqual(sum(m['fact']=='delivery_withdrawn' for m in memories),1)
        self.assertFalse(any(m['fact']=='delivery_missed' for m in memories))

    def test_refusal_and_unaccepted_expiration_have_no_morality_penalty(self):
        a=self.ready();b=deepcopy(a);self.until(a,3);self.until(b,3)
        before=deepcopy(a['daily_life']['contacts']);self.choose(a,'decline');self.until(a,7);self.until(b,7)
        self.assertEqual(a['daily_life']['contacts'],before);self.assertEqual(b['daily_life']['contacts'],before)
        self.assertEqual(a['ordinary']['employment'],b['ordinary']['employment'])
        self.reject_choice(a,'decline');self.reject_choice(b,'work')

    def test_cancellation_is_seeded_disclosed_and_basic_work_remains(self):
        w=self.ready();self.until(w,9)
        self.assertEqual(w['ordinary']['offers']['goon.ordinary.batch.1']['state'],'cancelled')
        self.reject_choice(w,'work','goon.ordinary.batch.1');self.repair(w)

    def test_support_requires_real_shortfall_place_and_availability(self):
        w=self.ready(False,0)
        self.reject_choice(w,'borrow',ordinary.SUPPORT)
        self.until(w,7);self.go(w,'store');self.reject_choice(w,'borrow',ordinary.SUPPORT)
        self.go(w);before=w['player']['cash'];self.choose(w,'borrow',ordinary.SUPPORT)
        self.assertEqual(w['player']['cash'],before+20)
        self.assertEqual(w['ordinary']['assistance'],dict(status='owed',amount=20,due_day=14))
        self.reject_choice(w,'borrow',ordinary.SUPPORT);self.roundtrip(w)

    def test_overdue_support_does_not_compound_or_block_repayment(self):
        w=self.ready(False,0);self.until(w,7);self.choose(w,'borrow',ordinary.SUPPORT);self.until(w,14)
        self.assertEqual(w['ordinary']['assistance']['status'],'overdue')
        self.reject_choice(w,'repay',ordinary.REPAY)
        self.until(w,15);self.repair(w);self.choose(w,'repay',ordinary.REPAY)
        self.assertEqual(w['ordinary']['assistance']['status'],'repaid')
        self.assertEqual(w['player']['cash'],0);self.reject_choice(w,'repay',ordinary.REPAY)
        self.reject_choice(w,'borrow',ordinary.SUPPORT);self.until(w,28)
        facts=w['daily_life']['contacts']['goon.contact.tess']['memories']
        self.assertEqual(sum(m['fact']=='support_overdue' for m in facts),1)

    def test_declining_support_has_no_debt_or_contact_penalty(self):
        w=self.ready(False,0);before=deepcopy(w['daily_life']['contacts'])
        self.choose(w,'decline_help',ordinary.SUPPORT);self.until(w,20)
        self.assertEqual(w['daily_life']['contacts'],before)
        self.assertEqual(w['ordinary']['assistance']['amount'],0)

    def test_room_notice_existing_maintenance_and_partial_payment(self):
        w=self.ready(False,0);self.until(w,5);self.assertIn(7,w['ordinary']['notices']);self.until(w,7)
        self.assertEqual(w['daily_life']['housing']['arrears'],30)
        self.choose(w,'borrow',ordinary.SUPPORT);execute_command(w,'pay_room')
        self.assertEqual(w['daily_life']['housing']['arrears'],10)
        execute_command(w,'choose',choice_id='goon.choice.room.1',option_id='help')
        self.assertEqual(w['daily_life']['housing']['arrears'],0);self.roundtrip(w)

    def test_three_action_budget_and_rejected_state_rng_purity(self):
        w=self.ready();self.until(w,3)
        execute_command(w,'join',faction='Harbor Syndicate')
        for _ in range(3):execute_command(w,'job',kind='courier')
        self.reject_choice(w,'work');self.choose(w,'decline')

    def test_eighteen_tu_is_not_refreshed_by_home_work(self):
        w=self.ready();self.until(w,3)
        for _ in range(9):self.go(w,'store');self.go(w)
        before=deepcopy(w['navigation']);self.choose(w,'work')
        self.assertEqual(w['navigation'],before)
        self.reject(w,'travel',destination='p032',mode='auto')
        advance_day(w);self.go(w,'store')

    def test_work_requires_execution_time_location(self):
        w=self.ready();self.until(w,3);self.go(w,'store')
        self.reject_choice(w,'work');self.reject_choice(w,'negotiate')
        self.go(w);self.choose(w,'work')

    def test_views_are_detached_readonly_and_do_not_reroll(self):
        w=self.ready();self.until(w,3);before,rng=deepcopy(w),random.getstate()
        ordinary.report(w)['history'].clear();ordinary.choice_report(w,'goon.ordinary.batch.0')['options'].clear()
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def test_malformed_versions_states_context_and_effects_reject(self):
        original=self.ready();self.until(original,3);self.choose(original,'work')
        for kind in ('version','missing_version','employment','wage','location','actions','npc','duplicate','missing_source','reordered_source'):
            with self.subTest(kind=kind):
                w=deepcopy(original);e=next(x for x in w['events'] if x['kind']=='ordinary_transition' and x['operation']=='choose')
                source=next(x for x in w['events'] if x['kind']=='ordinary_transition' and x['operation']=='observe_work')
                if kind=='version':w['ordinary_version']=True
                elif kind=='missing_version':del w['ordinary_version']
                elif kind=='employment':w['ordinary']['employment']=6
                elif kind=='wage':e['result']['cash_delta']=240
                elif kind=='location':e['context']['location']='goon.poi.p032'
                elif kind=='actions':e['context']['actions']=2
                elif kind=='npc':next(x for x in w['events'] if x['kind']=='player_command' and x['command_id']==e['command_id'])['actor']='npc'
                elif kind=='duplicate':w['events'].insert(w['events'].index(e)+1,deepcopy(e))
                elif kind=='missing_source':w['events'].remove(source)
                else:
                    w['events'].remove(source);receipt=next(x for x in w['events'] if x['kind']=='player_command' and x['command']=='choose');w['events'].insert(w['events'].index(receipt)+1,source)
                before,rng=deepcopy(w),random.getstate()
                with self.assertRaises(ValueError):validate(w)
                self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def test_failure_after_delegated_effect_rolls_back_whole_command(self):
        w=self.ready();self.until(w,3);before,rng=deepcopy(w),random.getstate()
        with patch('ordinary_life.life._memory',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):self.choose(w,'work')
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def test_failed_save_publication_keeps_primary_and_backup(self):
        w=self.ready();self.until(w,3)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'career.json';save_career(w,p);old=p.read_bytes();self.choose(w,'work')
            import career_persistence as persistence
            real=persistence.os.replace
            def fail(source,target):
                if Path(target)==p:raise OSError('interrupted publication')
                return real(source,target)
            with patch('career_persistence.os.replace',side_effect=fail):
                with self.assertRaises(OSError):save_career(w,p)
            self.assertEqual(p.read_bytes(),old);self.assertEqual(p.with_name(p.name+'.bak').read_bytes(),old)
            save_career(w,p);self.assertEqual(load_career(p),w)

    def test_historical_fixtures_do_not_adopt_and_remain_playable(self):
        root=Path(__file__).parent
        paths=list((root/'fixtures').rglob('*.json'))+list((root/'mobility_fixtures').rglob('*.json'))+[root/'institution_fixtures'/'m018_notice.json']
        for p in paths:
            w=load_career(p);advance_day(w);self.assertNotIn('ordinary_version',w)

    def test_all_five_policies_replay_daily_for_multiple_weeks(self):
        from ordinary_campaigns import run
        hashes=[]
        for policy in ('stability','negotiation','support','recovery','refusal'):
            result=run(101,policy,21,1);hashes.append(result['world_sha256'])
        self.assertEqual(len(set(hashes)),5)

    def test_reserved_wage_does_not_reprice_after_standing_improves(self):
        w=self.ready();self.until(w,3);self.choose(w,'negotiate')
        advance_day(w);self.repair(w);advance_day(w);self.repair(w)
        self.assertEqual(w['ordinary']['employment'],3)
        before=w['player']['cash'];self.choose(w,'work')
        self.assertEqual(w['player']['cash']-before,24)

    def test_modern_journey_roundtrip_then_home_work(self):
        import mobility
        from mobility_content import OVERLAY_ID
        w=create_career(17);execute_command(w,'settle_in');advance_day(w)
        execute_command(w,'enable_ordinary')
        execute_command(w,'enable_mobility',overlay_id=OVERLAY_ID,request_id='ordinary.mobility')
        advance_day(w)
        execute_command(w,'journey',**mobility.plan_route(w,'p032','free')['arguments'])
        execute_command(w,'choose',choice_id='goon.choice.0.crossroads',option_id='lawful')
        execute_command(w,'journey',**mobility.plan_route(w,'home','free')['arguments'])
        advance_day(w);self.choose(w,'work');self.roundtrip(w)

    def test_old_navigation_anchor_supports_explicit_adoption(self):
        w=load_career(Path(__file__).parent/'fixtures'/'career_m011.json')
        execute_command(w,'enable_navigation',anchor='n13');advance_day(w)
        execute_command(w,'settle_in');advance_day(w);before=deepcopy(w['daily_life'])
        execute_command(w,'enable_ordinary');self.assertEqual(w['daily_life'],before)
        advance_day(w);self.roundtrip(w)

    def test_work_and_support_do_not_transmit_institutional_knowledge(self):
        w=self.ready();execute_command(w,'enable_incidents')
        execute_command(w,'enable_incident',definition_id='goon.incident.wrong_notice.v1')
        execute_command(w,'enable_institutions');self.until(w,3)
        before={k:deepcopy(w[k]) for k in ('institutions','incidents','wrong_notice','legal','cases','factions')}
        self.choose(w,'work')
        for k,v in before.items():self.assertEqual(w[k],v,k)

    def test_forged_shortfall_cannot_authorize_unsupported_work(self):
        from simulation import event
        w=self.ready(False);self.until(w,3);ctx=ordinary.context(w);ctx['arrears']=30
        ordinary._emit(w,'choose',dict(offer_id='goon.ordinary.batch.0',option_id='work'),
            ctx=ctx,command_id=w['command_sequence']+1)
        w['command_sequence']+=1;w['actions_used']=2
        event(w,'player_command','forged receipt',command='ordinary_choose',command_id=w['command_sequence'],
            actor='player',arguments=dict(offer_id='goon.ordinary.batch.0',option_id='work'),action_cost=2,cause='player_command')
        before,rng=deepcopy(w),random.getstate()
        with self.assertRaises(ValueError):validate(w)
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def test_edited_support_balances_and_due_dates_reject_on_disk(self):
        w=self.ready(False,0);self.until(w,7);self.choose(w,'borrow',ordinary.SUPPORT)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'edited.json'
            for key,value in (('amount',0),('amount',-20),('due_day',999),('status','unused')):
                bad=deepcopy(w);bad['ordinary']['assistance'][key]=value
                p.write_text(json.dumps(bad),encoding='utf-8')
                with self.assertRaises(ValueError):load_career(p)

    def test_malformed_base_life_inside_adopted_save_has_clear_validation_error(self):
        w=self.ready()
        for field in ('home_id','opening_cash','contacts','housing','transactions'):
            for missing in (False,True):
                with self.subTest(field=field,missing=missing):
                    bad=deepcopy(w)
                    if missing:del bad['daily_life'][field]
                    else:bad['daily_life'][field]=None
                    with self.assertRaises(ValueError):validate(bad)


if __name__=='__main__':unittest.main()
