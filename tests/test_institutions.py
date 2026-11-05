"""M019 institutional knowledge, response, provenance, and bounded consequences."""
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
from game_service import (actions_remaining,advance_day,create_career,execute_command,
    institution_report,load_career,save_career)
from incident_dispatch import WRONG_NOTICE, player_events
from institution_content import CIVILIAN, INTAKE, fingerprint, load
from institution_sources import catalogue
import institutional_response as desks


class InstitutionTests(unittest.TestCase):
    def start(self, seed=73, enabled=True, both=True):
        w=create_career(seed)
        execute_command(w,'settle_in');advance_day(w)
        if both:
            execute_command(w,'enable_incidents')
        execute_command(w,'enable_incident',definition_id=WRONG_NOTICE)
        if enabled:
            execute_command(w,'enable_institutions')
        return w

    def until(self,w,day):
        while w['day']<day:
            advance_day(w)

    def go(self,w,target='n13'):
        resolved={'n13':'goon.neighborhood.n13','p032':'goon.poi.p032','p044':'goon.poi.p044','home':'goon.poi.p031'}[target]
        if w['navigation']['location_id']!=resolved:
            execute_command(w,'travel',destination=target,mode='auto')

    def ready(self,seed=73):
        w=self.start(seed)
        self.until(w,w['wrong_notice']['information_day'])
        self.go(w,'p032')
        execute_command(w,'discover_incident',incident_id=w['wrong_notice']['id'],channel='public_notice')
        return w

    def claim(self,w,key):
        return w['wrong_notice']['claims'][key]['id']

    def verify(self,w):
        self.go(w)
        execute_command(w,'incident_choose',incident_id=w['wrong_notice']['id'],stage='verify',option_id='ledger')

    def submit(self,w,key='poster',actor=CIVILIAN):
        self.go(w,'p044' if actor==INTAKE else 'n13')
        return execute_command(w,'institution_submit',institution_id=actor,source_id=self.claim(w,key))['result']['report_id']

    def correction(self,w,target,key='ledger',actor=CIVILIAN):
        return execute_command(w,'institution_correct',institution_id=actor,report_id=target,source_id=self.claim(w,key))

    def follow(self,w,actor=CIVILIAN,incident=None):
        self.go(w,'p044' if actor==INTAKE else 'n13')
        return execute_command(w,'institution_followup',institution_id=actor,
            incident_id=incident or w['wrong_notice']['id'])['result']['response']

    def reject(self,w,command,**arguments):
        before,rng=deepcopy(w),random.getstate()
        with self.assertRaises(ValueError):execute_command(w,command,**arguments)
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def roundtrip(self,w):
        before=deepcopy(w)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'career.json';save_career(w,path)
            self.assertEqual(load_career(path),w)
        self.assertEqual(w,before)

    def case(self,w,actor=CIVILIAN,incident=None):
        return w['institutions']['matters'][desks.matter_id(actor,incident or w['wrong_notice']['id'])]

    def test_definition_and_disabled_views_are_detached_and_nonadopting(self):
        w=create_career();before=deepcopy(w)
        self.assertFalse(institution_report(w)['enabled'])
        institution_report(w)['definitions'].clear();load()['actors'].clear()
        self.assertEqual(w,before)
        self.reject(w,'enable_institutions')
        self.reject(w,'institution_submit',institution_id=CIVILIAN,source_id='fake')

    def test_explicit_adoption_preserves_resources_and_contacts(self):
        w=self.start(enabled=False);before=deepcopy(w)
        execute_command(w,'enable_institutions')
        self.assertEqual(w['player'],before['player'])
        self.assertEqual(w['daily_life'],before['daily_life'])
        self.assertEqual(w['navigation'],before['navigation'])
        self.assertEqual(actions_remaining(w),3)
        self.assertEqual(w['institutions']['reports'],{})
        self.reject(w,'enable_institutions');self.roundtrip(w)

    def test_pending_life_cannot_adopt(self):
        w=create_career();execute_command(w,'settle_in')
        self.reject(w,'enable_institutions')

    def test_institutions_can_start_idle_before_incident_adoption(self):
        w=create_career(211);execute_command(w,'settle_in');advance_day(w)
        execute_command(w,'enable_institutions');self.until(w,4)
        self.assertEqual(w['institutions']['reports'],{})
        execute_command(w,'enable_incidents')
        execute_command(w,'enable_incident',definition_id=WRONG_NOTICE)
        self.until(w,20)
        self.assertEqual(len(w['institutions']['reports']),6)
        self.roundtrip(w)

    def test_independent_contradictions_do_not_reveal_authentic_date(self):
        w=self.start();self.until(w,w['wrong_notice']['information_day']+1)
        case=self.case(w)
        self.assertEqual(case['status'],'clarification_requested')
        self.assertNotIn('delivery_day',case['beliefs'])
        self.assertEqual(len(case['contradictions']),1)
        self.assertFalse(case['contradictions'][0]['resolved_by'])
        self.assertIsNone(w['wrong_notice']['discovery'])
        self.assertFalse(institution_report(w,CIVILIAN)['actors'][0]['responses'])
        self.roundtrip(w)

    def test_institutions_receive_different_reports_not_shared_omniscience(self):
        w=self.start();self.until(w,max(w['incidents']['information_day']+1,w['wrong_notice']['information_day']+1))
        rows=list(w['institutions']['reports'].values())
        self.assertTrue(any(r['institution_id']==INTAKE and r['topic']=='alarm' for r in rows))
        self.assertFalse(any(r['institution_id']==INTAKE and r['topic'] in ('delivery_day','cause') for r in rows))
        self.assertTrue(any(r['institution_id']==CIVILIAN and r['topic']=='delivery_day' for r in rows))
        self.assertTrue(all(r['origin_event'] and r['route'] and r['observed_day']<r['received_day'] for r in rows))

    def test_independent_review_reaches_only_supported_recipient(self):
        w=self.start();self.until(w,max(w['incidents']['resolution_day']+3,w['wrong_notice']['resolution_day']+2))
        police=self.case(w,INTAKE,w['incidents']['id'])
        civil=self.case(w)
        self.assertEqual(police['status'],'documented')
        self.assertEqual(police['beliefs']['cause']['value'],w['incidents']['truth'])
        self.assertNotIn('delivery_day',police['beliefs'])
        self.assertEqual(civil['beliefs']['delivery_day']['value'],w['wrong_notice']['truth']['delivery_day'])
        self.assertIsNone(w['incidents']['discovery']);self.assertIsNone(w['wrong_notice']['discovery'])
        self.assertEqual(w['cases'],[]);self.assertEqual(w['player']['heat'],0)
        self.assertEqual(w['institutions']['receipts'],[])

    def test_unanswered_matter_closes_insufficient_without_truth_invention(self):
        w=self.start();self.until(w,w['incidents']['resolution_day']+8)
        case=self.case(w,CIVILIAN,w['incidents']['id'])
        self.assertEqual(case['status'],'closed_insufficient')
        self.assertNotIn('cause',case['beliefs'])
        self.assertEqual(case['beliefs']['alarm']['confidence'],'unconfirmed')
        self.roundtrip(w)

    def test_supported_but_false_source_is_logged_without_endorsement(self):
        w=self.ready();ident=self.submit(w)
        report=w['institutions']['reports'][ident]
        self.assertEqual(report['value'],w['wrong_notice']['claims']['poster']['delivery_day'])
        self.assertNotEqual(report['value'],w['wrong_notice']['truth']['delivery_day'])
        self.assertEqual(report['credibility'],'printed')
        self.assertIsNone(report['processed_day'])
        self.assertEqual(w['player']['cash'],40)
        self.roundtrip(w)

    def test_duplicate_and_unsupported_reports_reject_without_mutation(self):
        w=self.ready();self.submit(w)
        for source in (self.claim(w,'poster'),'fabricated_evidence',self.claim(w,'ledger')):
            self.reject(w,'institution_submit',institution_id=CIVILIAN,source_id=source)
        self.reject(w,'institution_submit',institution_id='unknown',source_id=self.claim(w,'poster'))

    def test_wrong_recipient_and_remote_counter_cannot_be_bypassed(self):
        w=self.ready();self.go(w,'p044')
        self.reject(w,'institution_submit',institution_id=INTAKE,source_id=self.claim(w,'poster'))
        self.reject(w,'institution_submit',institution_id=CIVILIAN,source_id=self.claim(w,'poster'))

    def test_verified_ledger_is_not_automatically_transmitted(self):
        w=self.ready();before=deepcopy(w['institutions']);self.verify(w)
        self.assertEqual(w['institutions'],before)
        ident=self.submit(w,'ledger')
        self.assertIsNone(w['institutions']['reports'][ident]['processed_day'])
        self.assertNotIn('delivery_day',self.case(w)['beliefs'])
        advance_day(w)
        self.assertEqual(self.case(w)['beliefs']['delivery_day']['value'],w['wrong_notice']['truth']['delivery_day'])

    def test_correction_while_original_is_queued_and_three_action_budget(self):
        w=self.ready();ident=self.submit(w);self.verify(w);self.correction(w,ident)
        self.assertEqual(actions_remaining(w),0)
        self.assertLessEqual(w['navigation']['tu_used'],18)
        self.reject(w,'institution_followup',institution_id=CIVILIAN,incident_id=w['wrong_notice']['id'])
        advance_day(w)
        self.assertEqual(self.case(w)['status'],'documented')
        self.assertEqual(w['institutions']['credibility'][CIVILIAN],'documented')
        self.assertEqual(w['player']['cash'],40)
        self.roundtrip(w)

    def test_late_unchecked_claim_cannot_overwrite_documented_belief(self):
        w=self.ready();self.verify(w);self.submit(w,'ledger');advance_day(w)
        truth=w['wrong_notice']['truth']['delivery_day']
        ident=self.submit(w,'poster');advance_day(w)
        self.assertEqual(self.case(w)['beliefs']['delivery_day']['value'],truth)
        self.assertEqual(w['institutions']['credibility'][CIVILIAN],'needs_documentation')
        self.reject(w,'institution_submit',institution_id=CIVILIAN,source_id=self.claim(w,'poster'))
        self.correction(w,ident);advance_day(w)
        self.assertEqual(w['institutions']['credibility'][CIVILIAN],'documented')
        self.roundtrip(w)

    def test_unrepaired_false_claim_has_local_access_consequence(self):
        w=self.ready();ident=self.submit(w)
        self.until(w,w['wrong_notice']['resolution_day']+2)
        self.assertEqual(w['institutions']['credibility'][CIVILIAN],'needs_documentation')
        self.assertEqual(w['institutions']['credibility'][INTAKE],'unestablished')
        self.assertEqual(w['daily_life']['contacts']['goon.contact.notice_neighbor']['standing'],0)
        self.verify_after_resolution_source(w)
        self.correction(w,ident,'review');advance_day(w)
        self.assertEqual(w['institutions']['credibility'][CIVILIAN],'documented')

    def verify_after_resolution_source(self,w):
        self.go(w)
        execute_command(w,'incident_choose',incident_id=w['wrong_notice']['id'],stage='aftermath',option_id='read')

    def test_correction_needs_known_target_recipient_and_documentary_source(self):
        w=self.ready();ident=self.submit(w)
        self.reject(w,'institution_correct',institution_id=CIVILIAN,report_id=ident,source_id=self.claim(w,'poster'))
        self.verify(w)
        self.reject(w,'institution_correct',institution_id=CIVILIAN,report_id='unknown',source_id=self.claim(w,'ledger'))
        self.go(w,'p044')
        self.reject(w,'institution_correct',institution_id=INTAKE,report_id=ident,source_id=self.claim(w,'ledger'))

    def test_known_npc_report_can_be_corrected_after_followup(self):
        w=self.ready();self.go(w)
        npc=desks.report_id(CIVILIAN,self.claim(w,'poster'),'npc')
        self.verify(w)
        self.reject(w,'institution_correct',institution_id=CIVILIAN,report_id=npc,source_id=self.claim(w,'ledger'))
        response=self.follow(w)
        self.assertIn(npc,response['report_ids'])
        self.correction(w,npc);advance_day(w)
        self.assertEqual(self.case(w)['status'],'documented')

    def test_documented_reports_and_corrections_cannot_spawn_unbounded_corrections(self):
        w=self.ready();ident=self.submit(w);self.verify(w)
        correction=self.correction(w,ident)['result']['report_id']
        advance_day(w)
        self.reject(w,'institution_correct',institution_id=CIVILIAN,report_id=correction,source_id=self.claim(w,'ledger'))
        documented=self.submit(w,'ledger')
        self.reject(w,'institution_correct',institution_id=CIVILIAN,report_id=documented,source_id=self.claim(w,'ledger'))
        self.roundtrip(w)

    def test_correction_and_assistance_cannot_be_collected_twice_after_reload(self):
        w=self.ready();ident=self.submit(w);self.verify(w);self.correction(w,ident);advance_day(w)
        response=self.follow(w)
        self.assertEqual(response['assistance'],'dated_correction_copy')
        before=w['player']['cash'];self.roundtrip(w)
        self.reject(w,'institution_correct',institution_id=CIVILIAN,report_id=ident,source_id=self.claim(w,'ledger'))
        self.reject(w,'institution_followup',institution_id=CIVILIAN,incident_id=w['wrong_notice']['id'])
        self.assertEqual(w['player']['cash'],before)

    def test_new_response_version_does_not_issue_duplicate_assistance(self):
        w=self.ready();self.verify(w);self.submit(w,'ledger');advance_day(w)
        self.assertEqual(self.follow(w)['assistance'],'dated_correction_copy')
        self.until(w,w['wrong_notice']['resolution_day']+2)
        self.assertIsNone(self.follow(w)['assistance'])
        self.assertEqual(sum(r['assistance']=='dated_correction_copy' for r in w['institutions']['receipts']),1)
        self.roundtrip(w)

    def test_received_copy_repairs_access_even_after_old_incident_windows_expire(self):
        w=self.ready();target=self.submit(w)
        self.until(w,w['wrong_notice']['resolution_day']+5)
        old_journal=deepcopy(w['wrong_notice'])
        response=self.follow(w)
        self.assertEqual(response['credibility'],'needs_documentation')
        self.assertEqual(response['assistance'],'dated_correction_copy')
        source=next(s for s in institution_report(w,CIVILIAN)['actors'][0]['sources'] if s['source_id'].endswith('.copy.delivery_day'))
        execute_command(w,'institution_correct',institution_id=CIVILIAN,report_id=target,source_id=source['source_id'])
        advance_day(w)
        self.assertEqual(w['institutions']['credibility'][CIVILIAN],'documented')
        self.assertEqual(w['wrong_notice'],old_journal)
        self.roundtrip(w)

    def test_unreceived_or_forged_copy_cannot_support_a_correction(self):
        w=self.ready();target=self.submit(w);self.until(w,w['wrong_notice']['resolution_day']+2)
        key=desks.matter_id(CIVILIAN,w['wrong_notice']['id'])+'.response.unknown.copy.delivery_day'
        self.reject(w,'institution_correct',institution_id=CIVILIAN,report_id=target,source_id=key)
        response=self.follow(w)
        bad=deepcopy(w)
        event=next(e for e in bad['events'] if e['kind']=='institution_transition' and e['operation']=='followup')
        event['result']['response']['beliefs']['delivery_day']['value']=999
        bad['institutions']['receipts'][-1]['beliefs']['delivery_day']['value']=999
        with self.assertRaises(ValueError):validate(bad)
        self.assertEqual(response['beliefs']['delivery_day']['value'],w['wrong_notice']['truth']['delivery_day'])

    def test_extra_unverified_report_does_not_extend_clarification_forever(self):
        w=self.ready();self.go(w);advance_day(w)
        deadline=self.case(w)['clarification_until']
        self.submit(w);advance_day(w)
        self.assertEqual(self.case(w)['clarification_until'],deadline)
        self.until(w,deadline)
        self.assertEqual(self.case(w)['status'],'closed_insufficient')

    def test_zero_cash_withholding_and_insufficient_records_preserve_survival(self):
        from daily_life import opportunities
        w=create_career(211);w['player']['cash']=0
        execute_command(w,'settle_in');advance_day(w)
        execute_command(w,'enable_incident',definition_id=WRONG_NOTICE)
        execute_command(w,'enable_institutions');self.until(w,20)
        self.assertEqual(w['player']['cash'],0)
        self.assertEqual(actions_remaining(w),3)
        self.assertLessEqual(w['daily_life']['housing']['arrears'],30)
        self.go(w,'p032')
        for _ in range(8):
            rows=[r for r in opportunities(w) if any(o['id']=='work' and o['availability']=='available' for o in r['options'])]
            if rows:break
            advance_day(w)
        self.assertTrue(rows)
        execute_command(w,'choose',choice_id=rows[0]['id'],option_id='work')
        self.assertGreater(w['player']['cash'],0)
        self.go(w,'home');self.assertFalse(w['player']['arrested'])

    def test_private_processing_does_not_update_player_receipt_or_events(self):
        w=self.ready();self.submit(w);response=self.follow(w)
        self.assertEqual(response['status'],'queued')
        known=deepcopy(institution_report(w,CIVILIAN))
        advanced=advance_day(w)
        self.assertFalse(any(e['kind']=='institution_transition' for e in advanced['events']))
        self.assertEqual(institution_report(w,CIVILIAN)['actors'][0]['responses'],known['actors'][0]['responses'])
        before=deepcopy(w);player_events(w,w['events']).clear();self.assertEqual(w,before)

    def test_withholding_is_private_bounded_and_not_a_promise(self):
        w=self.ready();before=deepcopy(w['player'])
        execute_command(w,'institution_withhold',institution_id=INTAKE,incident_id=w['wrong_notice']['id'])
        self.assertEqual(actions_remaining(w),3)
        self.assertEqual(w['player'],before)
        self.assertEqual(w['daily_life']['promises'],{})
        self.reject(w,'institution_withhold',institution_id=INTAKE,incident_id=w['wrong_notice']['id'])
        self.reject(w,'institution_withhold',institution_id=INTAKE,incident_id='unknown')
        self.roundtrip(w)

    def test_no_retroactive_npc_adoption_but_old_observations_can_be_submitted(self):
        w=self.start(enabled=False);self.until(w,w['wrong_notice']['resolution_day']+4)
        self.go(w,'p032');execute_command(w,'discover_incident',incident_id=w['wrong_notice']['id'],channel='public_notice')
        execute_command(w,'enable_institutions');self.until(w,w['day']+3)
        self.assertEqual(w['institutions']['reports'],{})
        self.submit(w,'ledger');advance_day(w)
        self.assertEqual(self.case(w)['status'],'documented')
        self.roundtrip(w)

    def test_world_and_resources_unchanged_by_institutional_interactions(self):
        w=self.ready();self.go(w);before=deepcopy(w)
        execute_command(w,'institution_submit',institution_id=CIVILIAN,source_id=self.claim(w,'poster'))
        for key in ('incidents','wrong_notice','daily_life','player','factions','cases','navigation','legal'):
            self.assertEqual(w[key],before[key],key)

    def test_daily_processing_idempotent_and_terminal_history_bounded(self):
        w=self.start();self.until(w,20)
        before=deepcopy(w['institutions']);count=len([e for e in w['events'] if e['kind'].startswith('institution_')])
        desks.synchronize(w);self.assertEqual(w['institutions'],before)
        self.until(w,35)
        self.assertEqual(w['institutions'],before)
        self.assertEqual(count,len([e for e in w['events'] if e['kind'].startswith('institution_')]))
        self.assertLessEqual(len(before['reports']),6)

    def test_readonly_views_are_detached_and_do_not_receive_responses(self):
        w=self.ready();self.submit(w)
        before,rng=deepcopy(w),random.getstate()
        institution_report(w)['actors'].clear();institution_report(w,CIVILIAN)['actors'][0]['sources'].clear()
        self.assertEqual(w,before);self.assertEqual(random.getstate(),rng)

    def test_police_only_logs_acquired_observations_not_guilt(self):
        w=self.start();self.until(w,w['incidents']['information_day']);self.go(w,'p032')
        incident=w['incidents']['id']
        execute_command(w,'discover_incident',incident_id=incident,channel='public_notice')
        execute_command(w,'incident_choose',incident_id=incident,stage='offer',option_id='accept')
        execute_command(w,'incident_choose',incident_id=incident,stage='work',option_id='verify')
        self.go(w,'p044')
        execute_command(w,'institution_submit',institution_id=INTAKE,source_id=incident+'.source.cause_verified')
        self.until(w,w['day']+2)
        response=self.follow(w,INTAKE,incident)
        self.assertEqual(response['beliefs']['cause']['value'],w['incidents']['truth'])
        self.assertEqual(response['classification'],'observations_logged')
        self.assertIsNone(response['assistance'])
        self.assertEqual(w['cases'],[]);self.assertFalse(w['player']['arrested'])
        self.assertEqual(w['player']['heat'],0)
        self.roundtrip(w)

    def test_contact_report_retains_actual_tess_source_without_giving_cause(self):
        w=self.start(seed=211)
        execute_command(w,'choose',choice_id='goon.choice.0.promise',option_id='promise')
        advance_day(w)
        execute_command(w,'choose',choice_id='goon.choice.0.crossroads',option_id='help')
        self.until(w,w['incidents']['information_day']);self.go(w)
        incident=w['incidents']['id']
        execute_command(w,'discover_incident',incident_id=incident,channel='contact')
        self.go(w,'p044')
        result=execute_command(w,'institution_submit',institution_id=INTAKE,source_id=incident+'.source.alarm_reported')['result']
        record=w['institutions']['reports'][result['report_id']]
        self.assertEqual(record['observer'],'goon.contact.tess')
        self.assertEqual(record['topic'],'alarm')
        self.assertNotIn('cause_verified',w['incidents']['player_facts'])
        self.roundtrip(w)

    def test_malformed_or_forged_records_cannot_be_saved_or_loaded(self):
        w=self.ready();self.submit(w)
        mutations=[lambda x:x.update(institution_version=True),lambda x:x.update(institution_version=2),
            lambda x:x['institutions'].update(content_fingerprint='forged'),
            lambda x:next(iter(x['institutions']['reports'].values())).update(value=999),
            lambda x:next(iter(x['institutions']['reports'].values())).update(institution_id=INTAKE),
            lambda x:next(iter(x['institutions']['reports'].values())).update(route='telepathy'),
            lambda x:x['institutions']['credibility'].update({CIVILIAN:'documented'}),
            lambda x:x.pop('institution_version'),lambda x:x['institutions']['receipts'].append({'fake':True}),
            lambda x:x['events'].append(dict(kind='institution_forged',message='forged',day=x['day']))]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.json'
            for i,mutate in enumerate(mutations):
                bad=deepcopy(w);mutate(bad);before=deepcopy(bad)
                with self.subTest(i=i),self.assertRaises(ValueError):validate(bad)
                self.assertEqual(bad,before)
                path.write_text(json.dumps(bad),encoding='utf-8')
                with self.subTest(load=i),self.assertRaises(ValueError):load_career(path)

    def test_forged_historical_counter_context_rejects(self):
        w=self.ready();self.submit(w)
        bad=deepcopy(w)
        e=next(e for e in bad['events'] if e['kind']=='institution_transition' and e['operation']=='submit')
        e['context']['location']='goon.poi.p032'
        with self.assertRaises(ValueError):validate(bad)

    def test_backdated_receipt_cannot_precede_observed_source_or_world_day(self):
        w=self.ready(211);self.verify(w);ident=self.submit(w,'ledger')
        bad=deepcopy(w)
        event=next(e for e in bad['events'] if e['kind']=='institution_transition' and e['operation']=='submit')
        command=next(e for e in bad['events'] if e['kind']=='player_command' and e['command_id']==event['command_id'])
        event['day']-=1;command['day']-=1;event['result']['due_day']-=1
        record=bad['institutions']['reports'][ident]
        record['received_day']-=1;record['due_day']-=1
        self.assertGreater(record['observed_day'],record['received_day'])
        with self.assertRaises(ValueError):validate(bad)

    def test_reordered_source_acquisition_and_duplicate_transmissions_reject(self):
        w=self.ready();self.submit(w)
        for mode in ('duplicate','reorder','missing'):
            bad=deepcopy(w)
            i=next(i for i,e in enumerate(bad['events']) if e['kind']=='institution_transition' and e['operation']=='submit')
            if mode=='duplicate':bad['events'].insert(i,deepcopy(bad['events'][i]))
            else:
                j=next(j for j,e in enumerate(bad['events']) if e['kind']=='incident_transition' and e.get('operation')=='discover')
                source=bad['events'].pop(j)
                if mode=='reorder':bad['events'].append(source)
            with self.subTest(mode=mode),self.assertRaises(ValueError):validate(bad)

    def test_failed_effect_rolls_back_candidate(self):
        w=self.ready();self.go(w);before=deepcopy(w)
        with patch('institutional_response._received',side_effect=ValueError('injected')):
            with self.assertRaises(ValueError):execute_command(w,'institution_submit',institution_id=CIVILIAN,source_id=self.claim(w,'poster'))
        self.assertEqual(w,before)

    def test_failed_save_publication_preserves_primary_and_backup(self):
        w=self.ready();self.go(w)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'career.json';save_career(w,path);original=path.read_bytes()
            self.submit(w);before=deepcopy(w);replace=os.replace
            def fail_primary(source,target):
                if Path(target)==path:raise OSError('injected publication interruption')
                return replace(source,target)
            with patch('career_persistence.os.replace',side_effect=fail_primary):
                with self.assertRaises(OSError):save_career(w,path)
            self.assertEqual(path.read_bytes(),original)
            self.assertEqual(path.with_name(path.name+'.bak').read_bytes(),original)
            self.assertEqual(w,before);self.assertEqual(list(Path(folder).glob('*.tmp')),[])
            save_career(w,path);self.assertEqual(load_career(path),w)

    def test_historical_fixtures_do_not_adopt_institutions(self):
        root=Path(__file__).parent
        for path in sorted((root/'fixtures').rglob('*.json'))+sorted((root/'mobility_fixtures').rglob('*.json')):
            w=load_career(path);self.assertNotIn('institution_version',w)
            advance_day(w);self.assertNotIn('institution_version',w)

    def test_genuine_m018_fixture_roundtrips_bytes_and_explicitly_adopts(self):
        original=Path(__file__).parent/'institution_fixtures'/'m018_notice.json'
        w=load_career(original)
        self.assertNotIn('institution_version',w)
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'copy.json';save_career(w,output)
            self.assertEqual(output.read_bytes(),original.read_bytes())
        execute_command(w,'enable_institutions')
        self.assertEqual(w['institutions']['reports'],{})
        self.submit(w,'ledger');advance_day(w)
        self.assertEqual(self.case(w)['status'],'documented')
        self.roundtrip(w)

    def test_long_replay_with_daily_disk_resumes(self):
        from institution_campaigns import run
        for seed,mode in [(211,'documented'),(509,'unchecked')]:
            result=run(seed,mode,days=60,resume_every=1)
            self.assertEqual(result['resumes'],60)
            self.assertEqual(result['credibility'][CIVILIAN],'documented' if mode=='documented' else 'needs_documentation')
            self.assertFalse(result['arrested']);self.assertEqual(result['heat'],0)
            self.assertEqual(result['arrears'],0)
            self.assertLessEqual(result['reports'],10)

    def test_hash_seed_and_insertion_order_replay(self):
        code=('import json; from game_service import *; from incident_dispatch import WRONG_NOTICE; '
            'w=create_career(211); execute_command(w,"settle_in"); advance_day(w); '
            'execute_command(w,"enable_incidents"); execute_command(w,"enable_incident",definition_id=WRONG_NOTICE); '
            'execute_command(w,"enable_institutions"); [advance_day(w) for _ in range(20)]; print(json.dumps(w,sort_keys=True))')
        output=[subprocess.check_output([sys.executable,'-B','-c',code],env=dict(os.environ,PYTHONHASHSEED=s)) for s in ('1','997')]
        self.assertEqual(*output)
        a=self.start();b=deepcopy(a);b['institutions']['credibility']=dict(reversed(list(b['institutions']['credibility'].items())))
        for _ in range(15):advance_day(a);advance_day(b)
        self.assertEqual(a,b)


if __name__=='__main__':
    unittest.main()
