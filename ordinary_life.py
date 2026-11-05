"""Bounded M020 work/support adapters over existing life, money and contacts."""
from copy import deepcopy

import choice_engine
import daily_life as life
from ordinary_content import fingerprint, load
from simulation import event

FACT_DELTAS = {'kits_delivered':1, 'delivery_missed':-1, 'delivery_withdrawn':-1,
               'support_received':0, 'support_overdue':-1, 'support_repaid':1}
SUPPORT = 'goon.ordinary.support'
REPAY = 'goon.ordinary.repayment'


def initial(seed, day):
    return dict(seed=seed, enabled_day=day, activation_day=day+1, last_tick_day=day,
        employment=0, observed_work=[], offers={}, notices=[],
        assistance=dict(status='unused', amount=0, due_day=None))


def _state(world):
    state = world.get('ordinary')
    if state is None:
        raise ValueError('Inspect ordinary terms, then explicitly enable_ordinary at home or n13')
    if world['day'] < state['activation_day']:
        raise ValueError('Ordinary-life terms activate after the next wait')
    return state


def context(world):
    from game_service import actions_remaining
    import navigation
    daily = life._state(world)
    nav = navigation._active(world)
    return dict(location=nav['location_id'], home=daily['home_id'], free=not world['player']['arrested'],
        cash=world['player']['cash'], arrears=daily['housing']['arrears'],
        due_day=daily['housing']['next_due_day'], actions=actions_remaining(world))


def definition(state, ident, day):
    terms = load()
    if ident == SUPPORT:
        keys = ('borrow','decline_help')
        record = dict(id=ident,source_id=ident,open_day=state['activation_day'],expires_day=day+1,
            state='open' if state['assistance']['status']=='unused' else 'closed',selection=None)
        title, situation = "Tess's finite support fund", 'A short-term advance is a debt, not wages. It is optional and available only at the cooperative on disclosed roster days.'
    elif ident == REPAY:
        keys = ('repay',)
        record = dict(id=ident,source_id=ident,open_day=state['activation_day'],expires_day=day+1,
            state='open' if state['assistance']['status'] in ('owed','overdue') else 'closed',selection=None)
        title, situation = 'Close the support obligation', 'Repay at the home account box; no trip to a distant counter and no new borrowing entitlement.'
    else:
        if ident not in state['offers']:
            raise ValueError('Unknown work allocation; inspect ordinary')
        saved = state['offers'][ident]
        record = dict(saved,source_id=ident,selection=None,
            state='open' if saved['state'] in ('open','reserved') else saved['state'])
        if saved['state']=='reserved':
            record['open_day']=saved['open_day']-1  # Withdrawal starts at acceptance.
        keys = ('work','withdraw') if saved['state']=='reserved' else ('work','negotiate','decline')
        title, situation = terms['batch_title'], terms['batch_situation']
        if saved['state']=='cancelled':
            situation += ' This week is cancelled: no supplies, no accepted responsibility and no penalty.'
        if saved['state']=='reserved':
            situation += f' Reserved: complete on days {saved["open_day"]}-{saved["expires_day"]-1}; agreed wage ${saved["pay"]}.'
    options = [dict(id=k,**terms['options'][k]) for k in keys]
    return record, dict(title=title,situation=situation,speaker='Tess Navarro',options=options)


def assess(state, ident, day, ctx, option):
    key = option['id']
    if key in ('decline','decline_help'):
        return 'available', None
    if not ctx['free']:
        return 'unavailable', 'Work and account visits require freedom; wait and existing legal responses remain available'
    if ctx['location'] != ctx['home']:
        return 'unavailable', 'Visit your recorded home; no automatic travel or TU refresh'
    if ctx['actions'] < option['actions']:
        return 'unavailable', 'Daily actions exhausted for this option'
    if key=='work' and state['offers'][ident]['state']=='reserved' and day<state['offers'][ident]['open_day']:
        return 'unavailable', 'The agreed delivery date has not begun; withdrawal remains available now'
    if key == 'work' and state['employment']==0 and ctx['arrears']==0:
        return 'unavailable', 'Needs an observed repair completion or existing room arrears; basic store work needs neither'
    if key == 'negotiate' and state['offers'][ident]['negotiated']:
        return 'unavailable', 'This allocation already had its one negotiation request'
    if key == 'borrow':
        if (day-state['activation_day'])%7 not in (0,2,5):
            return 'unavailable', 'Tess is at the cooperative only on ordinary roster days 0, 2 and 5'
        if not (ctx['arrears'] or (ctx['cash'] < 30 and ctx['due_day']-day<=2)):
            return 'unavailable', 'Advance is reserved for a room shortfall or a low-cash review within two days'
    if key == 'repay' and ctx['cash'] < state['assistance']['amount']:
        return 'unavailable', 'Need the actual $20 repayment; work and room grace remain available'
    return 'available', None


def _bump(state, delta):
    state['employment'] = max(0,min(6,state['employment']+delta))


def reduce(state, operation, day, arguments, ctx=None):
    """Pure bounded reducer. Its caller alone applies delegated cash/memories."""
    terms = load()
    result = dict(cash_delta=0,memories=[],message='')
    def remember(fact):result['memories'].append(dict(fact=fact,delta=FACT_DELTAS[fact]))
    if operation == 'observe_work':
        ident = arguments['choice_id']
        if ident in state['observed_work']:raise ValueError('Repair completion already observed')
        state['observed_work'].append(ident);_bump(state,1)
        result['message'] = 'Actual repair completion recorded in employment standing; no second wage or Tess reward.'
    elif operation == 'tick':
        if day < state['activation_day'] or day<=state['last_tick_day']:
            raise ValueError('Ordinary day already processed or not active')
        state['last_tick_day'] = day
        for _,row in sorted(state['offers'].items()):
            if row['state'] in ('open','reserved') and day>=row['expires_day']:
                if row['state']=='reserved':
                    _bump(state,-1);remember('delivery_missed');row['state']='missed'
                else:row['state']='expired'
        debt = state['assistance']
        if debt['status']=='owed' and day>=debt['due_day']:
            debt['status']='overdue';remember('support_overdue')
        week = (day-state['activation_day'])//7
        ident = f'goon.ordinary.batch.{week}'
        if ident not in state['offers']:
            base = state['activation_day']+week*7
            state['offers'][ident] = dict(id=ident,week=week,open_day=base+1,expires_day=base+5,
                state='cancelled' if (state['seed']+week)%3==0 else 'open',negotiated=False,pay=None)
        due = arguments['due_day']
        notice = due-day<=2 and due not in state['notices']
        if notice:state['notices'].append(due)
        result['message'] = ('Room review in two days or less: $30 less actual prepayment, or the existing bounded unpaid balance. ' if notice else '')+'Work and support commitments reviewed once; basic home access continues.'
    elif operation == 'choose':
        ident, key = arguments['offer_id'], arguments['option_id']
        record, spec = definition(state,ident,day)
        choice_engine.eligible(dict(day=day),record,spec,key,
            lambda option:assess(state,ident,day,ctx,option))
        if key=='borrow':
            state['assistance']=dict(status='owed',amount=terms['support_amount'],due_day=day+terms['support_days'])
            result['cash_delta']=terms['support_amount'];remember('support_received')
            result['message']=f'Received $20 once; repay by day {day+7}. No interest or automatic collection.'
        elif key=='repay':
            result['cash_delta']=-state['assistance']['amount'];state['assistance']['status']='repaid'
            remember('support_repaid');result['message']='Repaid $20; the obligation is closed and the one advance remains used.'
        elif key=='decline_help':
            state['assistance']['status']='declined';result['message']='Support declined without a debt or relationship penalty.'
        else:
            row=state['offers'][ident]
            if key=='negotiate':
                row['negotiated']=True
                if state['employment']>=1:
                    row.update(state='reserved',open_day=day+1,expires_day=day+3,
                        pay=terms['regular_pay'] if state['employment']>=3 else terms['batch_pay'])
                    result['message']=f'Rescheduled once: deliver on days {day+1}-{day+2} for ${row["pay"]}; no advance pay.'
                else:result['message']='Tess declines a reserved date without an observed work record. The current allocation remains open; no relationship penalty.'
            elif key=='work':
                result['cash_delta']=row['pay'] if row['state']=='reserved' else (terms['regular_pay'] if state['employment']>=3 else terms['batch_pay'])
                row['state']='completed';_bump(state,1);remember('kits_delivered')
                result['message']=f'Delivered the funded kits for ${result["cash_delta"]}; employment standing {state["employment"]}. No second allocation this week.'
            elif key=='withdraw':
                row['state']='withdrawn';_bump(state,-1);remember('delivery_withdrawn')
                result['message']='Reserved work withdrawn; one bounded reliability consequence, no cash debt or loss of basic work.'
            else:
                row['state']='declined';result['message']='Allocation declined with no debt or standing penalty.'
    else:raise ValueError('Unsupported ordinary-life operation')
    return result


def _emit(world, operation, arguments, *, ctx=None, command_id=None):
    ident = ('goon.ordinary.command.'+str(command_id) if command_id is not None else
        'goon.ordinary.work.'+arguments['choice_id'] if operation=='observe_work' else 'goon.ordinary.day.'+str(world['day']))
    result = reduce(world['ordinary'],operation,world['day'],arguments,ctx)
    if result['cash_delta']:
        world['player']['cash']+=result['cash_delta']
        life.record_balance(world,'ordinary_settlement',ident,command_id=command_id)
    for memory in result['memories']:
        life._memory(world,life.TESS,memory['fact'],memory['delta'],ident)
    return event(world,'ordinary_transition',result['message'],schema_version=1,transition_id=ident,
        operation=operation,arguments=deepcopy(arguments),context=deepcopy(ctx),
        command_id=command_id,result=deepcopy(result),cause='ordinary_life')


def enable(world):
    if 'ordinary_version' in world:raise ValueError('Ordinary-life terms already adopted')
    ctx=context(world)
    from life_content import load as life_terms
    if not ctx['free'] or ctx['location'] not in (ctx['home'],life_terms()['hub_id']):
        raise ValueError('Visit home or n13 while free to adopt ordinary-life terms')
    world['ordinary_version']=1;world['ordinary']=initial(world['seed'],world['day'])
    return event(world,'ordinary_enabled','Ordinary work/support begins after the next wait; existing room terms and history are unchanged.',
        schema_version=1,command_id=world['command_sequence']+1,context=ctx,content_fingerprint=fingerprint())


def synchronize(world):
    state=world.get('ordinary')
    if state is None or world['day']<state['activation_day']:return
    for item in list(world['events']):
        if (item['kind']=='life_choice' and item['day']>=state['activation_day'] and
                item['outcome']['effect']=='lawful_work' and item['choice_id'] not in state['observed_work']):
            _emit(world,'observe_work',dict(choice_id=item['choice_id']))
    if state['last_tick_day']<world['daily_life']['last_tick_day']:
        _emit(world,'tick',dict(due_day=world['daily_life']['housing']['next_due_day']))


def choose(world, offer_id, option_id):
    _state(world)
    return _emit(world,'choose',dict(offer_id=offer_id,option_id=option_id),ctx=context(world),
        command_id=world['command_sequence']+1)


def cost(world, offer_id, option_id):
    state=_state(world);record,spec=definition(state,offer_id,world['day']);ctx=context(world)
    return choice_engine.eligible(world,record,spec,option_id,
        lambda option:assess(state,offer_id,world['day'],ctx,option))['actions']


def choice_report(world, offer_id):
    state=_state(world);record,spec=definition(state,offer_id,world['day']);ctx=context(world)
    result=choice_engine.present(world,record,spec,lambda o:assess(state,offer_id,world['day'],ctx,o))
    result['promise']=None
    return result


def report(world):
    if 'ordinary_version' not in world:
        return dict(enabled=False,terms='Optional: one weekly home-work allocation, observed employment standing and one repayable $20 support advance. Existing $30 room terms remain. Use enable_ordinary at home/n13 after settle_in activates.')
    state=world['ordinary'];housing=world['daily_life']['housing']
    pending=world['day']<state['activation_day']
    ids=[i for i,r in sorted(state['offers'].items()) if r['state'] in ('open','reserved') and r['expires_day']>world['day']]
    if state['assistance']['status']=='unused':ids.append(SUPPORT)
    if state['assistance']['status'] in ('owed','overdue'):ids.append(REPAY)
    return deepcopy(dict(enabled=True,pending=pending,activation_day=state['activation_day'],
        employment=state['employment'],housing_status='grace' if housing['arrears'] else 'current',
        due_day=housing['next_due_day'],arrears=housing['arrears'],prepaid=housing['prepaid'],
        assistance=state['assistance'],offers=[] if pending else [choice_report(world,i) for i in ids],
        history=state['offers'],recovery='Existing store shifts need no employment standing; pay_room and once-per-review maintenance remain. Basic home access and wait are preserved.'))
