"""Public-command institutional campaigns with whole-world replay and disk resume."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time

from game_service import (actions_remaining,advance_day,execute_command,institution_report,
    incident_report,save_career,load_career,plan_route)
from institution_content import CIVILIAN,INTAKE,fingerprint
from incident_dispatch import NIGHT_SHIFT,WRONG_NOTICE
from notice_campaigns import start as incident_start


def start(seed):
    world=incident_start(seed)
    execute_command(world,'enable_institutions')
    return world


def go(world,destination):
    if world['navigation']['location_id']==destination:
        return
    quote=plan_route(world,destination,'auto')
    if quote['affordable']:
        execute_command(world,'travel',destination=destination,mode='auto')


def choice(world,incident,stage,option):
    view=incident_report(world,incident)
    if any(r['stage']==stage and any(o['id']==option for o in r['options']) for r in view['choices']):
        execute_command(world,'incident_choose',incident_id=incident,stage=stage,option_id=option)


def play_day(world,mode):
    go(world,'goon.poi.p032')
    for row in incident_report(world)['incidents']:
        if 'public_notice' in row['discovery_channels']:
            execute_command(world,'discover_incident',incident_id=row['id'],channel='public_notice')
        if row['id'].startswith(NIGHT_SHIFT):
            choice(world,row['id'],'offer','refuse' if mode=='withhold' else 'accept')
            choice(world,row['id'],'work','verify')
            choice(world,row['id'],'report','withhold')
        elif row['known']:
            choice(world,row['id'],'response','refuse')
    for row in incident_report(world)['incidents']:
        if row['id'].startswith(WRONG_NOTICE) and row['known']:
            journal=row['journal']
            if mode=='documented' and journal['finding'] is None and world['day']<journal['deadline']:
                go(world,'goon.neighborhood.n13')
                choice(world,row['id'],'verify','ledger')
            if mode=='repair' and journal['deadline']<world['day']<journal['deadline']+4 and journal['decisions']['aftermath'] is None:
                go(world,'goon.neighborhood.n13')
                choice(world,row['id'],'aftermath','read')
    for actor in (CIVILIAN,INTAKE):
        view=next(a for a in institution_report(world)['actors'] if a['id']==actor)
        rows=[r for r in incident_report(world)['incidents'] if r['known']]
        if mode=='withhold':
            for row in rows:
                if desks_key(actor,row['id']) not in view['withheld']:
                    execute_command(world,'institution_withhold',institution_id=actor,incident_id=row['id'])
            continue
        suffix=('.claim.ledger' if mode=='documented' else '.claim.poster') if actor==CIVILIAN else '.source.cause_verified'
        pending_submit=any(s['source_id'].endswith(suffix) and not any(r['source_id']==s['source_id'] for r in view['submissions']) for s in view['sources'])
        pending_follow=any((r['id'].startswith(NIGHT_SHIFT) if actor==INTAKE else r['id'].startswith(WRONG_NOTICE)) and
            world['day']>=r['journal']['deadline']+2 and not any(p['incident_id']==r['id'] for p in view['responses']) for r in rows)
        pending_repair=actor==CIVILIAN and mode=='repair' and any(s['source_id'].endswith('.claim.review') for s in view['sources']) and not any(r['correction_of'] for r in view['submissions'])
        if not (pending_submit or pending_follow or pending_repair):
            continue
        go(world,view['place'])
        view=next(a for a in institution_report(world)['actors'] if a['id']==actor)
        source=next((s for s in view['sources'] if s['source_id'].endswith(suffix) and s['available']),None)
        if source is not None:
            execute_command(world,'institution_submit',institution_id=actor,source_id=source['source_id'])
        # Follow-up knowledge comes from an actual counter response, not state
        # beliefs or world truth. Deadlines were disclosed in incident journals.
        for row in incident_report(world)['incidents']:
            if not row['known'] or actions_remaining(world)<1:
                continue
            if actor==INTAKE and not row['id'].startswith(NIGHT_SHIFT):
                continue
            if actor==CIVILIAN and not row['id'].startswith(WRONG_NOTICE):
                continue
            view=next(a for a in institution_report(world)['actors'] if a['id']==actor)
            if not any(r['incident_id']==row['id'] for r in view['responses']) and world['day']>=row['journal']['deadline']+2:
                execute_command(world,'institution_followup',institution_id=actor,incident_id=row['id'])
        if actor==CIVILIAN and mode=='repair' and actions_remaining(world)>=1:
            view=next(a for a in institution_report(world)['actors'] if a['id']==actor)
            original=next((r for r in view['submissions'] if r['source_id'].endswith('.claim.poster') and r['correction_of'] is None),None)
            correction=next((s for s in view['sources'] if s['source_id'].endswith('.claim.review')),None)
            if original and correction and not any(r['correction_of']==original['id'] for r in view['submissions']):
                execute_command(world,'institution_correct',institution_id=actor,report_id=original['id'],source_id=correction['source_id'])
    go(world,'goon.poi.p032')
    from daily_life import opportunities
    for row in opportunities(world):
        if any(o['id']=='work' and o['availability']=='available' for o in row['options']):
            execute_command(world,'choose',choice_id=row['id'],option_id='work')
            break
    advance_day(world)


def desks_key(actor,incident):
    from institutional_response import matter_id
    return matter_id(actor,incident)


def run(seed,mode='documented',days=365,resume_every=30):
    started=time.perf_counter()
    a,b=start(seed),start(seed)
    resumes=0
    with tempfile.TemporaryDirectory(prefix='goon-institution-campaign-') as folder:
        path=Path(folder)/'career.json'
        for index in range(days):
            play_day(a,mode);play_day(b,mode)
            if (index+1)%resume_every==0 or index+1==days:
                save_career(b,path);b=load_career(path);resumes+=1
            if a!=b:
                raise AssertionError(('institution campaign replay diverged',seed,mode,index))
    state=a['institutions']
    return dict(seed=seed,mode=mode,days=days,resumes=resumes,content_fingerprint=fingerprint(),
        credibility=state['credibility'],reports=len(state['reports']),responses=len(state['receipts']),
        matters={k:c['status'] for k,c in sorted(state['matters'].items())},
        correction_copies=sum(r['assistance']=='dated_correction_copy' for r in state['receipts']),
        cash=a['player']['cash'],arrears=a['daily_life']['housing']['arrears'],
        heat=a['player']['heat'],arrested=a['player']['arrested'],
        world_sha256=hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        elapsed_seconds=round(time.perf_counter()-started,3))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days',type=int,default=365)
    parser.add_argument('--seed',type=int,default=211)
    parser.add_argument('--mode',choices=('documented','unchecked','repair','withhold'),default='documented')
    parser.add_argument('--resume-every',type=int,default=30)
    args=parser.parse_args()
    if not 20<=args.days<=1000 or not 1<=args.resume_every<=args.days:
        parser.error('days must be 20-1000; resume-every must be 1-days')
    print(json.dumps(run(args.seed,args.mode,args.days,args.resume_every),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
