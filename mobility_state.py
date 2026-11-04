"""Validation of the additive M016-A pair and mixed travel history. No effects."""
from copy import deepcopy
import re

from mobility_content import OVERLAY_ID, fingerprint, load


def validate(world):
    from career_state import _integer, _mapping, _require, _records
    import navigation
    import mobility
    content = load()
    station_places = {s['place_id'] for s in content['stations']}
    graph = mobility.graph_pin()

    def require(ok, detail):
        _require(ok, 'mobility', detail)

    require(type(world.get('navigation_version')) is int and world['navigation_version'] == 2,
            'requires navigation_version 2; unsupported or missing paired state')
    require(type(world.get('mobility_version')) is int and world['mobility_version'] == 1,
            'requires mobility_version 1; unsupported or missing paired state')
    nav, mob = world.get('navigation'), world.get('mobility')
    _mapping(nav, 'navigation')
    _mapping(mob, 'mobility')
    for key in ('rules_version', 'overlay_version'):
        require(type(mob.get(key)) is int and mob[key] == 1, 'unsupported ' + key)
    require(mob.get('overlay_id') == OVERLAY_ID and mob.get('overlay_fingerprint') == fingerprint(),
            'requires the pinned local mobility overlay; no substitution allowed')
    for key, empty in (('assets', {}), ('access_tokens', {}), ('driver_authorizations', {}),
                       ('restrictions', []), ('disruptions', [])):
        require(type(mob.get(key)) is type(empty) and mob[key] == empty,
                key + ' must be empty; vehicles and new incident systems are not implemented')
    knowledge = mob.get('knowledge')
    _mapping(knowledge, 'mobility.knowledge')
    require(knowledge.get('assets') == {} and isinstance(knowledge.get('assets'), dict), 'asset knowledge must be empty')
    _records(knowledge.get('service_disruptions'), 'mobility.knowledge.service_disruptions')
    commands = {}
    for e in world['events']:
        if e['kind'] == 'player_command':
            ident = e.get('command_id')
            require(type(ident) is int and ident > 0 and ident not in commands, 'duplicate/invalid player command ID')
            commands[ident] = e
    adoption = mob.get('adoption')
    _mapping(adoption, 'mobility.adoption')
    require(adoption.get('status') in ('pending', 'active'), 'invalid adoption status')
    request_id, request_command = adoption.get('request_id'), adoption.get('request_command_id')
    mobility._request_id(request_id)
    _integer(request_command, 'mobility.adoption.request_command_id', 1, world['command_sequence'])
    request = commands.get(request_command, {})
    require(request.get('command') == 'enable_mobility' and request.get('action_cost') == 0
            and request.get('arguments') == dict(overlay_id=OVERLAY_ID, request_id=request_id), 'adoption must reference its exact command')
    require(adoption.get('requested_day') == request.get('day'), 'adoption requested day must match command')
    _integer(adoption.get('requested_day'), 'mobility.adoption.requested_day', 0, world['day'])
    _integer(adoption.get('scheduled_activation_day'), 'mobility.adoption.scheduled_activation_day',
             request['day'] + 1, request['day'] + 1)
    requested = [e for e in world['events'] if e['kind'] == 'mobility_requested']
    require(len(requested) == 1, 'requires one adoption request event')
    req = requested[0]
    _integer(req.get('command_id'), 'mobility_requested.command_id', request_command, request_command)
    require(type(req.get('schema_version')) is int and req['schema_version'] == 1
            and req.get('command_id') == request_command and req.get('request_id') == request_id
            and req['day'] == request['day'] and req.get('overlay_id') == OVERLAY_ID
            and req.get('overlay_fingerprint') == fingerprint()
            and req.get('scheduled_activation_day') == adoption['scheduled_activation_day'], 'inconsistent adoption request event')
    require({c['command_id'] for c in commands.values() if c['command'] == 'enable_mobility'} == {request_command}, 'adoption can occur only once')
    trips = [e for e in world['events'] if e['kind'] == 'travel']
    for trip in trips:
        require(type(trip.get('schema_version')) is int and trip['schema_version'] in (1, 2), 'unsupported travel schema')
        _integer(trip.get('journey_id'), 'travel.journey_id', 1)
        _integer(trip.get('command_id'), 'travel.command_id', 1, world['command_sequence'])
    legacy = [e for e in trips if e['schema_version'] == 1]
    modern = sorted([e for e in trips if e['schema_version'] == 2], key=lambda e: e.get('journey_id', -1) if type(e.get('journey_id')) is int else -1)
    activations = [e for e in world['events'] if e['kind'] == 'mobility_activated']
    # Check the original metadata before the legacy projection replaces it.
    _integer(nav.get('rules_version'), 'navigation.rules_version', 1, 2)
    _integer(nav.get('journey_sequence'), 'navigation.journey_sequence', 0)
    projection = dict(world)
    projection['navigation_version'] = 1
    projection['navigation'] = dict(nav, rules_version=1, journey_sequence=len(legacy))
    projection['events'] = [e for e in world['events'] if e['kind'] != 'travel' or e['schema_version'] == 1]
    expected_receipts = {request_id: dict(command_id=request_command, kind='adoption',
        payload_digest=mobility.request_digest(request['arguments']))}
    is_active = adoption['status'] == 'active'
    if not is_active:
        require(not modern and not activations and nav.get('rules_version') == 1, 'pending adoption cannot contain new journeys or active rules')
        require(all(adoption.get(k) is None for k in ('activation_day', 'activation_command_id', 'legacy_checkpoint', 'activation_budget')),
                'pending adoption contains activation effects')
        require(nav.get('journey_sequence') == len(legacy), 'pending journey sequence mismatch')
        navigation._validate_v1(projection)
        require(not any(c['command'] == 'journey' for c in commands.values()), 'pending journey command is invalid')
        require(mob.get('receipts') == expected_receipts and knowledge['service_disruptions'] == [], 'pending receipts/knowledge mismatch')
        return
    require(type(nav.get('rules_version')) is int and nav['rules_version'] == 2, 'active navigation rules must be 2')
    day = adoption.get('activation_day')
    _integer(day, 'mobility.adoption.activation_day', adoption['scheduled_activation_day'], world['day'])
    activation_id = adoption.get('activation_command_id')
    _integer(activation_id, 'mobility.adoption.activation_command_id', request_command + 1, world['command_sequence'])
    activation_command = commands.get(activation_id, {})
    require(activation_command.get('command') == 'wait' and activation_command.get('day') == day, 'activation requires its real wait command')
    checkpoint = adoption.get('legacy_checkpoint')
    _mapping(checkpoint, 'mobility.adoption.legacy_checkpoint')
    require(set(checkpoint) == {'location_id', 'tu_day', 'tu_used', 'last_journey_id', 'last_travel_command_id'}, 'invalid checkpoint shape')
    for key in ('last_journey_id', 'last_travel_command_id'):
        if checkpoint.get(key) is not None:
            _integer(checkpoint[key], 'mobility.adoption.legacy_checkpoint.' + key, 1)
    last_legacy = max(legacy, key=lambda e: e['journey_id']) if legacy else None
    require(checkpoint.get('last_journey_id') == (last_legacy['journey_id'] if last_legacy else None)
            and checkpoint.get('last_travel_command_id') == (last_legacy['command_id'] if last_legacy else None), 'checkpoint must include the final legacy journey')
    require(all(e.get('command_id', 0) < activation_id for e in legacy), 'schema1 journey after activation is invalid')
    require(adoption.get('activation_budget') == dict(tu_day=day, tu_used=0), 'activation cannot grant a second budget')
    require(len(activations) == 1, 'requires one activation event')
    activation = activations[0]
    _integer(activation.get('command_id'), 'mobility_activated.command_id', activation_id, activation_id)
    _integer(activation.get('request_command_id'), 'mobility_activated.request_command_id', request_command, request_command)
    require(type(activation.get('schema_version')) is int and activation['schema_version'] == 1
            and activation.get('command_id') == activation_id and activation.get('request_command_id') == request_command
            and activation['day'] == day and activation.get('legacy_checkpoint') == checkpoint
            and activation.get('activation_budget') == adoption['activation_budget']
            and activation.get('scheduled_activation_day') == adoption['scheduled_activation_day'], 'activation event/checkpoint mismatch')
    projection['navigation'].update(location_id=checkpoint['location_id'], tu_day=checkpoint['tu_day'], tu_used=checkpoint['tu_used'])
    navigation._validate_v1(projection)
    require(checkpoint['tu_day'] < day, 'activation requires a valid new day transition')
    # With an empty legacy history, retain v1's validated position/budget as the
    # activation snapshot. Current home entitlement cannot reconstruct it:
    # settle_in may legitimately grant a home later without moving the player.
    places, edges = navigation._definitions()
    location, budget_day, used = checkpoint['location_id'], day, 0
    expected_knowledge, journey_commands, charges = [], set(), set()
    last_command = activation_id
    for offset, trip in enumerate(modern, len(legacy) + 1):
        _integer(trip.get('journey_id'), 'travel.journey_id', offset, offset)
        command_id = trip.get('command_id')
        _integer(command_id, 'travel.command_id', last_command + 1, world['command_sequence'])
        command = commands.get(command_id, {})
        args = command.get('arguments', {})
        require(command.get('command') == 'journey' and command.get('day') == trip['day']
                and command.get('action_cost') == 0 and set(args) == set(mobility.JOURNEY_ARGUMENTS)
                and all(isinstance(v, str) for v in args.values()), 'journey must match its exact command')
        require(trip['day'] >= day and command_id not in journey_commands, 'invalid journey command/day')
        journey_commands.add(command_id)
        last_command = command_id
        rid = trip.get('request_id')
        mobility._request_id(rid)
        require(rid == args['request_id'] and rid not in expected_receipts, 'duplicate/mismatched request ID')
        require(args['profile'] in mobility.PROFILES and args['vehicle_id'] == ''
                and re.fullmatch(r'[0-9a-f]{64}', args['quote_token']), 'invalid journey profile/vehicle/quote')
        cap = mobility._number(args['max_tu'], 'max_tu', 18)
        cash_cap = mobility._number(args['max_cash'], 'max_cash', 1000000)
        def resolve(value):
            if value == 'home':
                return nav['home_id']
            return ('goon.neighborhood.' if value.startswith('n') else 'goon.poi.' if value.startswith('p') else '') + value
        require(trip.get('graph') == graph, 'journey requires its pinned graph/rules')
        require(trip.get('origin') == location and trip.get('destination') == resolve(args['destination']), 'journey endpoints/continuity mismatch')
        require(trip.get('destination') in places and places[trip['destination']]['kind'] != 'region', 'invalid destination')
        require(type(trip.get('interrupted')) is bool and isinstance(trip.get('legs'), list)
                and len(trip['legs']) <= mobility.MAX_LEGS, 'invalid interruption/legs')
        node, previous, raw_tu, fare, index, boards, charge_ids = location, 'walk', 0, 0, 0, 0, []
        visited, service_boardings = {location}, 0
        moved = False
        while index < len(trip['legs']):
            leg = trip['legs'][index]
            _mapping(leg, 'travel.legs[]')
            if leg.get('kind') == 'walk_gate':
                require(index + 5 <= len(trip['legs']), 'partial monorail transaction')
                group = trip['legs'][index:index + 5]
                end = group[-1].get('to_id') if isinstance(group[-1], dict) else None
                require(node in station_places and end in station_places and node != end, 'monorail requires real station endpoints')
                require(args['profile'] in ('fastest', 'monorail') and end not in visited,
                        'monorail conflicts with requested profile or repeats a node')
                visited.add(end)
                boards += 1
                service_boardings += 1
                require(group == mobility.ride_legs(node, end, trip['journey_id'], boards, definitions=content), 'monorail transition/fare mismatch')
                for item in group:
                    require(type(item.get('tu')) is int and type(item.get('cash_cost')) is int, 'leg costs must be integers')
                raw_tu += sum(l['tu'] for l in group)
                fare += sum(l['cash_cost'] for l in group)
                charge_ids.append(group[1]['charge_id'])
                node, previous, index, moved = end, 'walk', index + 5, True
            else:
                eid, mode = leg.get('edge_id'), leg.get('mode')
                require(leg.get('kind') == 'move' and isinstance(eid, str) and eid in edges
                        and mode in ('walk', 'bus', 'ferry'), 'invalid base move or legacy rail bypass')
                edge = edges[eid]
                end = edge['to'] if node == edge['from'] else edge['from'] if edge['bidirectional'] and node == edge['to'] else None
                require(end is not None and leg.get('from_id') == node and leg.get('to_id') == end
                        and mode in edge['modes'], 'noncontiguous/unsupported leg')
                require(end not in visited, 'journey contains a movement cycle')
                visited.add(end)
                require(args['profile'] in ('fastest', 'free') or mode == args['profile']
                        or (mode == 'walk' and (edge['kind'] == 'access' or args['profile'] == 'monorail')),
                        'base move conflicts with requested profile')
                require(edge['kind'] != 'access' or edge['to'] in {trip['origin'], trip['destination']} | station_places, 'unapproved intermediate POI shortcut')
                cost = edge['modes'][mode] + int(mode != 'walk' and mode != previous)
                require(type(leg.get('tu')) is int and leg['tu'] == cost
                        and type(leg.get('cash_cost')) is int and leg['cash_cost'] == 0, 'base move cost mismatch')
                raw_tu += cost
                service_boardings += int(mode in ('bus', 'ferry') and mode != previous)
                node, previous, index, moved = end, mode, index + 1, True
        require(service_boardings <= mobility.MAX_BOARDINGS, 'journey exceeds boarding limit')
        require(args['profile'] != 'monorail' or boards > 0 or trip['interrupted'], 'monorail profile requires actual boarding')
        require(node == trip.get('arrived') and (trip['interrupted'] or node == trip['destination']), 'actual arrival mismatch')
        require(trip.get('asset_changes') == [], 'vehicle effects not supported')
        resources = trip.get('resources')
        _mapping(resources, 'travel.resources')
        tu, cash = resources.get('tu'), resources.get('cash')
        _mapping(tu, 'travel.resources.tu')
        _mapping(cash, 'travel.resources.cash')
        _integer(tu.get('day'), 'travel.resources.tu.day', budget_day, trip['day'])
        before = used if tu['day'] == budget_day else 0
        cost = max(raw_tu, int(moved))
        require(tu == dict(day=tu['day'], before=before, cost=cost, after=before + cost)
                and all(type(v) is int for v in tu.values()) and before + cost <= 18 and cost <= cap, 'TU accounting mismatch')
        _integer(cash.get('before'), 'travel.resources.cash.before', fare)
        require(cash == dict(before=cash['before'], cost=fare, after=cash['before'] - fare)
                and all(type(v) is int for v in cash.values()) and fare <= cash_cap
                and resources.get('fuel') == {}, 'cash/fuel accounting mismatch')
        require(not (set(charge_ids) & charges), 'duplicate boarding charge')
        charges.update(charge_ids)
        discoveries = trip.get('discoveries')
        require(isinstance(discoveries, list) and len(discoveries) <= 1 and bool(discoveries) == trip['interrupted'], 'interruption needs exactly one observation')
        for observation in discoveries:
            _mapping(observation, 'travel.discoveries[]')
            sources = observation.get('source_ids')
            require(isinstance(sources, list) and bool(sources) and all(isinstance(s, str) for s in sources)
                    and len(sources) == len(set(sources)), 'invalid discovery sources')
            closures = {c['id']: c for c in nav['closures']}
            require(all(s in closures for s in sources), 'missing discovery closure')
            causes = [closures[s] for s in sources]
            require(all(c['start_day'] <= trip['day'] < c['end_day'] for c in causes), 'discovery outside closure dates')
            if observation.get('kind') == 'line':
                line = content['line']
                require(node in (line['from_id'], line['to_id']) and observation.get('from_id') == node
                        and observation.get('line_id') == line['id']
                        and observation.get('until_day') == max(c['end_day'] for c in causes), 'line observation mismatch')
                _integer(observation.get('until_day'), 'travel.discoveries.until_day', trip['day'] + 1, trip['day'] + 2)
                segments = line['segments'] if node == line['from_id'] else [dict(edge_id=s['edge_id'], from_id=s['to_id']) for s in line['segments']]
                require(all(c['mode'] == 'rail' and any(c['edge_id'] == s['edge_id'] and c['from_id'] == s['from_id'] for s in segments) for c in causes), 'unrelated line closure source')
                expected_knowledge.append(deepcopy(observation))
            else:
                require(observation.get('kind') == 'corridor' and observation.get('from_id') == node
                        and all(c['edge_id'] == observation.get('edge_id') and c['from_id'] == node
                                and c['mode'] == observation.get('mode') and c['known'] for c in causes), 'corridor discovery mismatch')
        expected_receipts[rid] = dict(command_id=command_id, kind='journey', journey_id=trip['journey_id'],
            payload_digest=mobility.request_digest(args), charge_ids=charge_ids)
        location, budget_day, used = node, tu['day'], tu['after']
    require(journey_commands == {c['command_id'] for c in commands.values() if c['command'] == 'journey'}, 'every journey command needs one outcome')
    _integer(nav.get('journey_sequence'), 'navigation.journey_sequence', len(trips), len(trips))
    require(nav.get('location_id') == location, 'current location must match mixed history')
    _integer(nav.get('tu_day'), 'navigation.tu_day', budget_day, world['day'])
    _integer(nav.get('tu_used'), 'navigation.tu_used', 0, 18)
    require(nav['tu_used'] == (used if nav['tu_day'] == budget_day else 0), 'current TU must match history or a later reset')
    require(mob.get('receipts') == expected_receipts, 'request receipt index must match committed effects exactly')
    require(knowledge['service_disruptions'] == expected_knowledge, 'observed disruptions must match journey history')
    if modern and world['command_sequence'] == modern[-1]['command_id']:
        require(world['player']['cash'] == modern[-1]['resources']['cash']['after'], 'current cash contradicts final journey')
