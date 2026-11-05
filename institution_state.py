"""Read-only replay of institutional transmissions against prior domain sources."""
import json


def _same(a,b):
    return json.dumps(a,sort_keys=True,allow_nan=False) == json.dumps(b,sort_keys=True,allow_nan=False)


def validate(world):
    from career_state import _require, _integer
    from institution_content import fingerprint
    from institution_sources import Sources
    import institutional_response as engine
    events = world['events']
    related = [e for e in events if e['kind'].startswith('institution_') or
        (e['kind']=='player_command' and (e['command'].startswith('institution_') or e['command']=='enable_institutions'))]
    if 'institution_version' not in world:
        _require('institutions' not in world and not related,'institutions','requires explicit versioned adoption')
        return
    _integer(world['institution_version'],'institution_version',1,1)
    _require('daily_life_version' in world and world['day']>=world['daily_life']['activation_day'],
        'institutions','requires active daily life')

    def require(ok,detail):
        _require(ok,'institutions.provenance',detail)

    receipts = [(i,e) for i,e in enumerate(events) if e['kind']=='player_command']
    frames = {e['command_id']:(i,e,receipts[n-1][0] if n else -1) for n,(i,e) in enumerate(receipts)}
    used = set()

    def historical_location(position,command_id,day):
        # Use completed historical arrivals, never final position or a claimed flag.
        arrival = None
        for i,trip in enumerate(events[:position]):
            if trip['kind']!='travel':
                continue
            source_command = frames.get(trip['command_id'])
            require(source_command is not None,'arrival has no committed command')
            trip_end,trip_cmd,trip_start = source_command
            require(trip_start<i<trip_end and trip_cmd['command'] in ('travel','journey') and
                trip_cmd['actor']=='player' and trip_cmd['day']==trip['day'],
                'arrival source is outside its player command frame')
            if trip['command_id']<command_id and trip_end<position:
                require(trip['day']<=day,'arrival cannot follow the receiving command day')
                arrival = trip['arrived']
        if arrival is None:
            activations = [(i,e) for i,e in enumerate(events[:position]) if e['kind']=='navigation_activated']
            if activations:
                i,activation = activations[-1]
                adoptions = [(j,e) for j,e in enumerate(events[:i]) if e['kind']=='navigation_enabled']
                require(len(adoptions)==1,'activation needs its original public-anchor adoption')
                j,adoption = adoptions[0]
                matching = next(((n,e) for n,e in receipts if n>j),None)
                require(matching is not None,'anchor adoption needs a completed player command')
                end,command = matching
                require(frames[command['command_id']][2]<j<end<i and
                    command['command']=='enable_navigation' and command['actor']=='player' and
                    command['day']==adoption['day'] and command['command_id']<command_id and
                    command['arguments'].get('anchor') is not None and activation['day']<=day,
                    'anchor adoption must finish inside its player command frame before activation')
                require(activation['location_id']==adoption['anchor_id'],'activation/anchor mismatch')
                arrival = activation['location_id']
            else:
                from location_registry import load as atlas
                nav = world['navigation']
                require(nav['enabled_day']==nav['activation_day']==0 and
                    not any(e['kind']=='navigation_enabled' for e in events),'no supported historical origin')
                arrival = atlas()['starting_home_id']
        return arrival

    def frame(position,item,command_name,arguments):
        ctx = item['context']
        require(isinstance(ctx,dict) and set(ctx)=={'command_id','location','free','accessible','actions'},'invalid command context')
        _integer(ctx['command_id'],'institutions.command_id',1)
        _integer(ctx['actions'],'institutions.actions',0,3)
        require(all(type(ctx[k]) is bool for k in ('free','accessible')) and isinstance(ctx['location'],str),'invalid context types')
        command_id = ctx['command_id']
        require(command_id==item['command_id'] and command_id not in used and command_id in frames,'requires one unique committed command')
        end, command, start = frames[command_id]
        cost, names = engine.COMMANDS[command_name]
        require(start<position<end and command['command']==command_name and command['actor']=='player' and
            command['day']==item['day'] and _same(command['arguments'],arguments) and set(arguments)==set(names) and
            all(isinstance(v,str) for v in arguments.values()) and type(command['action_cost']) is int and
            command['action_cost']==cost and ctx['actions']>=cost,'command frame, arguments or cost mismatch')
        require(ctx['location']==historical_location(position,command_id,item['day']),
            'location must match completed historical movement or supported origin')
        used.add(command_id)
        return ctx

    def observation_frame(source):
        source_frame = frames.get(source['learned_command'])
        require(source_frame is not None,'source observation needs a committed acquisition command')
        acquisition = events[source['position']]
        require(source_frame[2]<source['position']<source_frame[0] and
            source_frame[1]['actor']=='player' and acquisition.get('command_id')==source['learned_command'] and
            acquisition['day']==source_frame[1]['day'],
            'source observation must occur inside its own player acquisition command frame')
        require(acquisition['context']['location']==historical_location(
            source['position'],source['learned_command'],source['observed_day']),
            'source acquisition location must match its own completed historical arrivals')
        return source_frame

    def replay():
        sources, state, enabled_position, known_day = Sources(world['seed']), None, None, 0
        for position,item in enumerate(events):
            sources.observe(item,position)
            if item['kind'].startswith('institution_'):
                require(item['day']==known_day,'receipt/processing must use the day already established by prior domain events')
            known_day = max(known_day,item['day'])
            if not item['kind'].startswith('institution_'):
                continue
            require(type(item.get('schema_version')) is int and item['schema_version']==1,'unsupported event schema')
            if item['kind']=='institution_enabled':
                require(state is None,'duplicate adoption')
                ctx = frame(position,item,'enable_institutions',{})
                require(ctx['free'] and item['day']>=world['daily_life']['activation_day'],'invalid adoption eligibility')
                require(item['content_fingerprint']==fingerprint(),'requires pinned institution definitions')
                state = engine.initial(item['day'],ctx['command_id'])
                enabled_position = position
                continue
            require(item['kind']=='institution_transition' and state is not None,'unknown event or missing adoption')
            op,args,ctx = item['operation'],item['arguments'],item['context']
            require(isinstance(args,dict),'arguments must be an object')
            if op in ('receive','process'):
                require(ctx is None and item['command_id'] is None,'background work cannot be a player command')
                life_days = [i for i,e in enumerate(events[:position]) if e['kind']=='life_day' and e['day']==item['day']]
                require(len(life_days)==1 and life_days[0]>enabled_position,'background work needs post-adoption daily processing')
                delivery = engine.next_delivery(state,sources,item['day'],enabled_position)
                require(_same(args,delivery) if op=='receive' else delivery is None,'delivery source, order or recipient mismatch')
                suffix = ('receive.'+engine.report_id(args['institution_id'],args['source_id'],'npc')) if op=='receive' else 'process.'+str(item['day'])
            else:
                command_name = 'institution_'+op
                require(command_name in engine.COMMANDS,'unsupported institution command')
                ctx = frame(position,item,command_name,args)
                if op in ('submit','correct'):
                    source = sources.player.get(args['source_id'])
                    require(source is not None and source['position']<position,'requires a previously acquired source')
                    source_frame = observation_frame(source)
                    require(source_frame[0]<position and
                        source['learned_command']<ctx['command_id'] and
                        source['observed_day']<=item['day'] and source_frame[1]['day']<=item['day'],
                        'source acquisition must finish before transmission in event order and simulation day')
                suffix = 'command.'+str(ctx['command_id'])
            result = engine.reduce(state,op,item['day'],args,sources,ctx)
            require(item['transition_id']=='goon.institutions.'+suffix and
                _same(result,item['result']) and item['message']==result['message'],'transition result or stable identity mismatch')
            if op=='followup':
                sources.receive_response(result['response'],item['transition_id'],position)
        require(state is not None,'missing explicit adoption event')
        # Unsubmitted observations are still exposed by the player preview.
        # Validate the complete catalogue, including genuine pre-adoption facts.
        for source in sources.player.values():
            observation_frame(source)
        commands = {e['command_id'] for _,e in receipts if e['command'].startswith('institution_') or e['command']=='enable_institutions'}
        require(commands==used,'every institutional command must settle exactly once')
        require(engine.next_delivery(state,sources,world['day'],enabled_position) is None and
            not engine.needs_processing(state,world['day']),'due institutional work was omitted')
        require(_same(state,world.get('institutions')),'saved knowledge, records or responses contradict source-backed replay')

    try:
        replay()
    except (KeyError,TypeError,IndexError,AttributeError) as exc:
        raise ValueError('Invalid save: institutions contains malformed source/history data') from exc
