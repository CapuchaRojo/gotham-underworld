"""Read-only proof of M020 settlements against the existing life/command log."""
import json

import ordinary_life as ordinary
from ordinary_content import fingerprint


def _same(a,b):
    return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)


def validate(world):
    from career_state import _require, _integer, _mapping, _text
    def require(ok,message):_require(ok,'ordinary.provenance',message)
    events=world['events']
    related=[e for e in events if e['kind'].startswith('ordinary_') or
        (e['kind']=='player_command' and e['command'] in ('enable_ordinary','ordinary_choose'))]
    daily=world.get('daily_life')
    transactions=daily.get('transactions',[]) if isinstance(daily,dict) else []
    own_rows=[t for t in transactions if isinstance(t,dict) and t.get('cause')=='ordinary_settlement'] if isinstance(transactions,list) else []
    if 'ordinary_version' not in world:
        require('ordinary' not in world and not related and not own_rows,'requires explicit versioned adoption')
        return {}
    _integer(world['ordinary_version'],'ordinary_version',1,1)
    require('daily_life_version' in world and isinstance(daily,dict),'requires existing daily life')
    require(all(k in daily for k in ('home_id','opening_cash','enabled_day','activation_day',
        'last_tick_day','contacts','housing','transactions')),'missing required base-life field')
    _text(daily['home_id'],'daily_life.home_id')
    for k in ('opening_cash','enabled_day','activation_day','last_tick_day'):
        _integer(daily[k],'daily_life.'+k,0)
    _mapping(daily['contacts'],'daily_life.contacts')
    _mapping(daily['housing'],'daily_life.housing')
    require(isinstance(transactions,list) and all(isinstance(t,dict) for t in transactions),'invalid cash ledger')
    require(all(isinstance(t.get('source_id'),str) for t in own_rows),'invalid settlement identity')
    own_txs={t['source_id']:t for t in own_rows}
    receipts=[(i,e) for i,e in enumerate(events) if e['kind']=='player_command']
    frames={e['command_id']:(i,e,receipts[n-1][0] if n else -1) for n,(i,e) in enumerate(receipts)}
    state=None;used=set();effects={};paid=set();observed={};spent={};arrivals={}
    location=(daily['home_id'] if world['navigation']['enabled_day']==world['navigation']['activation_day']==0
        and not any(e['kind']=='navigation_enabled' for e in events) else None)
    cash=daily['opening_cash'];due=daily['enabled_day']+7;arrears=0;free=True;known_day=0

    def frame(i,e,name,args,cost):
        ident=e['command_id'];_integer(ident,'ordinary.command_id',1)
        require(ident in frames and ident not in used,'requires a unique committed command')
        end,c,start=frames[ident]
        require(start<i<end and c['actor']=='player' and c['command']==name and c['day']==e['day'] and
            _same(c['arguments'],args) and type(c['action_cost']) is int and c['action_cost']==cost,
            'command frame, actor, day, arguments or cost mismatch')
        ctx=e['context'];tx=own_txs.get(e.get('transition_id'))
        before=tx['before'] if tx else cash
        expected=dict(location=location,home=daily['home_id'],free=free,cash=before,
            arrears=arrears,due_day=due,actions=3-spent.get(e['day'],0))
        require(_same(ctx,expected),'context must match prior movement, money, housing, custody and action sources')
        require(ctx['actions']>=cost,'daily action allowance exhausted')
        used.add(ident)
        return ctx,start,end

    try:
        for i,e in enumerate(events):
            kind=e['kind']
            if kind.startswith('ordinary_'):
                require(e['day']==known_day,'cannot backdate a command or use future domain facts')
            known_day=max(known_day,e['day'])
            if kind=='life_transaction':cash=e['after']
            elif kind=='life_housing':
                due=e['after']['next_due_day'];arrears=e['after']['arrears']
            elif kind in ('arrest','charge'):free=False
            elif kind in ('release','prison'):free=True
            elif kind=='navigation_activated':
                adoptions=[(j,a) for j,a in enumerate(events[:i]) if a['kind']=='navigation_enabled']
                require(len(adoptions)==1,'historical navigation needs one original anchor adoption')
                j,a=adoptions[0];source=next(((n,c) for n,c in receipts if n>j),None)
                require(source is not None,'anchor needs its own completed command')
                end,c=source
                require(frames[c['command_id']][2]<j<end<i and c['actor']=='player' and
                    c['command']=='enable_navigation' and c['day']==a['day'] and
                    e['location_id']==a['anchor_id'],'anchor adoption provenance mismatch')
                location=e['location_id']
            elif kind=='travel':
                f=frames.get(e['command_id']);require(f is not None,'travel needs its committed command')
                end,c,start=f
                require(start<i<end and c['actor']=='player' and c['day']==e['day'] and
                    c['command']==('journey' if e['schema_version']==2 else 'travel'),'arrival source mismatch')
                arrivals[e['command_id']]=e['arrived']
            elif kind=='player_command':
                if e['command_id'] in arrivals:location=arrivals[e['command_id']]
                spent[e['day']]=spent.get(e['day'],0)+e['action_cost']
            elif kind=='life_choice' and e['outcome']['effect']=='lawful_work':
                observed[e['choice_id']]=(i,e)
            if not kind.startswith('ordinary_'):continue
            _integer(e.get('schema_version'),'ordinary.schema_version',1,1)
            if kind=='ordinary_enabled':
                require(state is None and e['day']>=daily['activation_day'],'requires one active-life adoption')
                ctx,_,_=frame(i,e,'enable_ordinary',{},0)
                from life_content import load
                require(ctx['free'] and ctx['location'] in (ctx['home'],load()['hub_id']), 'invalid adoption place or custody')
                require(e['content_fingerprint']==fingerprint(),'requires pinned local terms')
                state=ordinary.initial(world['seed'],e['day']);continue
            require(kind=='ordinary_transition' and state is not None,'missing adoption or unknown event')
            op,args,ctx=e['operation'],e['arguments'],e['context']
            if op=='choose':
                record,spec=ordinary.definition(state,args['offer_id'],e['day'])
                option=next(o for o in spec['options'] if o['id']==args['option_id'])
                require(set(args)=={'offer_id','option_id'} and all(isinstance(v,str) for v in args.values()),'invalid choice arguments')
                ctx,start,end=frame(i,e,'ordinary_choose',args,option['actions'])
                ident='goon.ordinary.command.'+str(e['command_id'])
            else:
                require(ctx is None and e['command_id'] is None,'automatic work cannot impersonate a player command')
                if op=='tick':
                    require(_same(args,dict(due_day=due)),'room notice must use the real current obligation')
                    require(any(x['kind']=='life_day' and x['day']==e['day'] for x in events[:i]),'tick needs prior life-day processing')
                    ident='goon.ordinary.day.'+str(e['day'])
                elif op=='observe_work':
                    require(set(args)=={'choice_id'} and args['choice_id'] in observed,'needs an actual prior repair completion')
                    pos,source=observed[args['choice_id']];end,c,start=frames[source['command_id']]
                    require(start<pos<i<end and c['actor']=='player' and c['command']=='choose' and
                        c['day']==source['day']==e['day']>=state['activation_day'], 'repair source frame/order mismatch')
                    ident='goon.ordinary.work.'+args['choice_id']
                else:raise ValueError('Unknown ordinary operation')
            result=ordinary.reduce(state,op,e['day'],args,ctx)
            require(e['transition_id']==ident and _same(e['result'],result) and e['message']==result['message'],
                'effect, identity or message differs from source-backed replay')
            if result['cash_delta']:
                tx=own_txs.get(ident)
                require(tx is not None and tx['amount']==result['cash_delta'] and tx['day']==e['day'] and
                    tx['command_id']==e['command_id'] and tx['before']==ctx['cash'] and tx['after']>=0,
                    'cash effect needs exactly one real funded ledger settlement')
                txevents=[(n,t) for n,t in enumerate(events) if t['kind']=='life_transaction' and t['id']==tx['id']]
                require(len(txevents)==1 and start<txevents[0][0]<i<end,'payment must precede its own effect inside the command')
                require(ident not in paid,'duplicate settlement');paid.add(ident)
            for m in result['memories']:
                key=('goon.contact.tess',m['fact'],ident)
                require(key not in effects,'duplicate delegated memory')
                effects[key]=dict(day=e['day'],delta=m['delta'])
        require(state is not None and _same(state,world.get('ordinary')),'saved ordinary state contradicts replay')
        require(state['last_tick_day']==max(state['enabled_day'],daily['last_tick_day']),'daily processing was omitted')
        require(set(state['observed_work'])=={k for k,(_,s) in observed.items() if s['day']>=state['activation_day']},'work observation omitted')
        require(used=={c['command_id'] for _,c in receipts if c['command'] in ('enable_ordinary','ordinary_choose')},'every ordinary command must settle once')
        require(paid==set(own_txs) and len(own_txs)==sum(t['cause']=='ordinary_settlement' for t in transactions),'extra/duplicate ordinary settlement')
        actual={(person,m['fact'],m['source_id']) for person,p in daily['contacts'].items() for m in p['memories'] if m['fact'] in ordinary.FACT_DELTAS}
        require(actual==set(effects),'missing or invented delegated contact effect')
        return effects
    except (KeyError,TypeError,IndexError,AttributeError,StopIteration) as exc:
        raise ValueError('Invalid save: malformed ordinary-life history') from exc
