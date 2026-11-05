"""M020 reproducible public-command playtests; not in-game autoplay."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import time

from game_service import (create_career,execute_command,advance_day,save_career,load_career,
    actions_remaining,plan_route)
from daily_life import opportunities
from ordinary_life import report, choice_report, SUPPORT, REPAY

POLICIES=('stability','negotiation','support','recovery','refusal')


def start(seed,policy,incidents=False):
    w=create_career(seed)
    # Explicit poor starting profiles exercise recovery; no game command grants
    # money and no ledger is edited after enrollment.
    if policy in ('support','recovery'):w['player']['cash']=0
    execute_command(w,'settle_in');advance_day(w)
    execute_command(w,'enable_ordinary')
    if incidents:
        execute_command(w,'enable_incidents')
        execute_command(w,'enable_incident',definition_id='goon.incident.wrong_notice.v1')
        execute_command(w,'enable_institutions')
    advance_day(w)
    return w


def go(w,destination):
    if w['navigation']['location_id']==destination:return True
    if plan_route(w,destination,'auto')['affordable']:
        execute_command(w,'travel',destination=destination,mode='auto');return True
    return False


def take(w,ident,option):
    row=choice_report(w,ident)
    if any(o['id']==option and o['availability']=='available' for o in row['options']):
        execute_command(w,'ordinary_choose',offer_id=ident,option_id=option);return True
    return False


def repair(w):
    if not go(w,'goon.poi.p032'):return False
    for row in opportunities(w):
        option=next((o for o in row['options'] if o['id'] in ('work','lawful') and o['availability']=='available'),None)
        if option is not None:
            execute_command(w,'choose',choice_id=row['id'],option_id=option['id']);return True
    return False


def play_day(w,policy):
    day=w['day'];offset=(day-w['daily_life']['activation_day'])%7
    active=policy!='refusal' and (policy not in ('support','recovery') or day>=(8 if policy=='support' else 16))
    if active and offset in (1,4):repair(w)
    if policy=='support' and day==8:repair(w)
    if policy=='recovery' and day==2:repair(w)
    go(w,w['daily_life']['home_id'])
    view=report(w)
    if policy=='refusal':
        for row in view['offers']:
            take(w,row['id'],'decline_help' if row['id']==SUPPORT else 'decline')
    else:
        if policy in ('support','recovery') and view['assistance']['status']=='unused':
            take(w,SUPPORT,'borrow')
        for row in report(w)['offers']:
            if not row['id'].startswith('goon.ordinary.batch.'):continue
            if policy=='recovery' and day==3:
                take(w,row['id'],'negotiate');continue
            if not active:continue
            keys={o['id'] for o in row['options'] if o['availability']=='available'}
            if policy=='negotiation' and 'negotiate' in keys:
                take(w,row['id'],'negotiate')
            else:take(w,row['id'],'work')
        debt=report(w)['assistance']
        if debt['status'] in ('owed','overdue') and active:take(w,REPAY,'repay')
        if active and report(w)['arrears'] and w['player']['cash']:
            execute_command(w,'pay_room')
    advance_day(w)


def run(seed,policy,days,resume_every=1,incidents=False):
    if policy not in POLICIES or type(days) is not int or days<1 or resume_every<1:
        raise ValueError('Choose a supported policy and positive duration/checkpoint interval')
    started=time.perf_counter();a=start(seed,policy,incidents);b=deepcopy(a);resumes=0
    with tempfile.TemporaryDirectory(prefix='goon-ordinary-campaign-') as folder:
        path=Path(folder)/'career.json'
        for n in range(days):
            play_day(a,policy);play_day(b,policy)
            if (n+1)%resume_every==0 or n+1==days:
                save_career(b,path);b=load_career(path);resumes+=1
            if a!=b:raise AssertionError(('M020 resume divergence',seed,policy,n))
    state=a['ordinary'];daily=a['daily_life']
    return dict(seed=seed,policy=policy,days=days,resumes=resumes,incidents=incidents,
        cash=a['player']['cash'],arrears=daily['housing']['arrears'],employment=state['employment'],
        support=state['assistance'],tess_standing=daily['contacts']['goon.contact.tess']['standing'],
        allocations={s:sum(r['state']==s for r in state['offers'].values()) for s in ('completed','reserved','missed','declined','cancelled','expired')},
        heat=a['player']['heat'],arrested=a['player']['arrested'],cases=len(a['cases']),
        world_sha256=hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        elapsed_seconds=round(time.perf_counter()-started,3))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seed',type=int,default=101);p.add_argument('--policy',choices=POLICIES,default='stability')
    p.add_argument('--days',type=int,default=30);p.add_argument('--resume-every',type=int,default=1)
    p.add_argument('--incidents',action='store_true');args=p.parse_args()
    print(json.dumps(run(args.seed,args.policy,args.days,args.resume_every,args.incidents),sort_keys=True),flush=True)


if __name__=='__main__':main()
