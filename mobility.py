"""M016-A: opt-in station travel, bounded deterministic quotes and reducers.

Player mutation is committed only by game_service. No vehicle or incident system.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import heapq
import re

import navigation
from mobility_content import OVERLAY_ID, digest, fingerprint, load
from simulation import event

MAX_LABELS = 8192
MAX_LEGS = 64
MAX_BOARDINGS = 2
PROFILES = ('fastest', 'free', 'walk', 'bus', 'ferry', 'monorail')
JOURNEY_ARGUMENTS = ('destination', 'profile', 'vehicle_id', 'max_tu', 'max_cash',
                     'return_to', 'quote_token', 'request_id')
_WAIT_COMMAND = ContextVar('mobility_wait_command', default=None)


@contextmanager
def command_scope(command, sequence):
    token = _WAIT_COMMAND.set(sequence if command == 'wait' else None)
    try:
        yield
    finally:
        _WAIT_COMMAND.reset(token)


def active(world):
    return world.get('mobility', {}).get('adoption', {}).get('status') == 'active'


def request_digest(arguments):
    return digest({k: v for k, v in arguments.items() if k != 'quote_token'})


def _request_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,128}', value):
        raise ValueError('request_id requires 1-128 letters, digits, periods, underscores or hyphens')


def _number(value, name, maximum):
    if not isinstance(value, str) or len(value) > 7 or not re.fullmatch(r'0|[1-9][0-9]*', value) or int(value) > maximum:
        raise ValueError(f'{name} must be a canonical integer from 0 to {maximum}')
    return int(value)


def _ready(world):
    nav = navigation._active(world)
    if not active(world):
        raise ValueError('Mobility is not active; inspect mobility, explicitly adopt, then wait')
    if world['player']['arrested']:
        raise ValueError('Cannot travel while detained; existing court and wait remain available')
    return nav


def enable_mobility(world, overlay_id, request_id):
    _request_id(request_id)
    if overlay_id != OVERLAY_ID:
        raise ValueError('Unsupported mobility overlay')
    if 'mobility_version' in world:
        raise ValueError('Mobility already enabled or scheduled; adoption cannot be repeated')
    navigation._active(world)
    if world['player']['arrested']:
        raise ValueError('Cannot adopt mobility while detained')
    load()
    sequence = world['command_sequence'] + 1
    world['navigation_version'] = 2
    world['mobility_version'] = 1
    world['mobility'] = dict(rules_version=1, overlay_id=overlay_id, overlay_version=1,
        overlay_fingerprint=fingerprint(), assets={}, access_tokens={}, driver_authorizations={},
        restrictions=[], disruptions=[], knowledge=dict(service_disruptions=[], assets={}),
        adoption=dict(status='pending', request_id=request_id, request_command_id=sequence,
            requested_day=world['day'], scheduled_activation_day=world['day'] + 1,
            activation_day=None, activation_command_id=None, legacy_checkpoint=None,
            activation_budget=None),
        receipts={request_id: dict(command_id=sequence, kind='adoption',
            payload_digest=request_digest(dict(overlay_id=overlay_id, request_id=request_id)))})
    return event(world, 'mobility_requested', 'Station mobility scheduled after the next wait; no resources granted.',
                 schema_version=1, command_id=sequence, request_id=request_id,
                 overlay_id=overlay_id, overlay_fingerprint=fingerprint(),
                 scheduled_activation_day=world['day'] + 1, cause='explicit_mobility_adoption')


def checkpoint(world):
    """Called by navigation before its existing reset, only in a service wait."""
    life = world.get('mobility')
    if not life or life['adoption']['status'] != 'pending' or _WAIT_COMMAND.get() is None:
        return None
    nav = world['navigation']
    legacy = [e for e in world['events'] if e['kind'] == 'travel']
    last = max(legacy, key=lambda e: e['journey_id']) if legacy else None
    return dict(location_id=nav['location_id'], tu_day=nav['tu_day'], tu_used=nav['tu_used'],
                last_journey_id=last['journey_id'] if last else None,
                last_travel_command_id=last['command_id'] if last else None)


def activate(world, boundary):
    if boundary is None:
        return
    adoption = world['mobility']['adoption']
    if world['day'] < adoption['scheduled_activation_day']:
        return
    adoption.update(status='active', activation_day=world['day'], activation_command_id=_WAIT_COMMAND.get(),
                    legacy_checkpoint=deepcopy(boundary),
                    activation_budget=dict(tu_day=world['navigation']['tu_day'], tu_used=0))
    world['navigation']['rules_version'] = 2
    event(world, 'mobility_activated', 'Station mobility active; legacy journeys retained under their original rules.',
          schema_version=1, command_id=_WAIT_COMMAND.get(), request_command_id=adoption['request_command_id'],
          scheduled_activation_day=adoption['scheduled_activation_day'],
          legacy_checkpoint=deepcopy(boundary), activation_budget=deepcopy(adoption['activation_budget']),
          cause='explicit_mobility_adoption')


def graph_pin():
    return dict(atlas_version=1, atlas_fingerprint=navigation.fingerprint(), overlay_id=OVERLAY_ID,
                overlay_version=1, overlay_fingerprint=fingerprint(), routing_rules_version=2)


def ride_legs(origin, destination, journey_id=0, boarding=1, *, definitions=None):
    data = load() if definitions is None else definitions
    stations = {s['place_id']: s for s in data['stations']}
    a, b, line = stations[origin], stations[destination], data['line']
    def leg(kind, ident, start, end, tu=0, cash=0, **extra):
        return dict(kind=kind, transition_id=ident, from_id=start, to_id=end,
                    mode='monorail' if kind in ('board', 'ride', 'alight') else 'walk',
                    tu=tu, cash_cost=cash, **extra)
    return [leg('walk_gate', a['gate_id'], origin, a['platform_id']),
            leg('board', a['id'] + '.board', a['platform_id'], a['platform_id'],
                line['boarding_tu'], line['fare'], line_id=line['id'],
                charge_id=f'goon.mobility.charge.{journey_id}.board.{boarding}'),
            leg('ride', line['ride_id'], a['platform_id'], b['platform_id'],
                line['ride_tu'], line_id=line['id']),
            leg('alight', b['id'] + '.alight', b['platform_id'], b['platform_id'], line_id=line['id']),
            leg('walk_gate', b['gate_id'], b['platform_id'], destination)]


def _line_blocked(world, origin, *, known_only):
    data = load()
    line = data['line']
    segments = line['segments'] if origin == line['from_id'] else [
        dict(edge_id=s['edge_id'], from_id=s['to_id'], to_id=s['from_id']) for s in reversed(line['segments'])]
    blocked = []
    for segment in segments:
        blocked.extend(navigation._closed(world['navigation'], segment['edge_id'], segment['from_id'],
                                          'rail', world['day'], known_only=known_only))
    observed = any(k['from_id'] == origin and k['until_day'] > world['day']
                   for k in world['mobility']['knowledge']['service_disruptions'])
    return bool(blocked) or (known_only and observed), sorted({c['id']: c for c in blocked}.values(), key=lambda c: c['id'])


class PlanningLimit(ValueError):
    pass


def _search(world, origin, destination, profile, cash_limit):
    """Bounded labels over node, prior mode, cash and boarding count. No RNG."""
    if origin == destination:
        return dict(cost=0, fare=0, legs=[], mode_changes=0)
    places, edges = navigation._definitions()
    nav = world['navigation']
    if not navigation._allowed(places[destination], nav):
        raise ValueError('Restricted destination; specific permission required')
    data = load()
    stations = {s['place_id'] for s in data['stations']}
    if profile == 'monorail' and origin in stations and _line_blocked(world, origin, known_only=True)[0]:
        raise ValueError('No known monorail departure at this station; use free/bus/walk or wait for reopening')
    adjacency = {p: [] for p in places}
    for eid, edge in sorted(edges.items()):
        if edge['kind'] == 'access' and edge['to'] not in {origin, destination} | stations:
            continue
        directions = [(edge['from'], edge['to'])]
        if edge['bidirectional']:
            directions.append((edge['to'], edge['from']))
        for start, end in directions:
            if not navigation._allowed(places[end], nav):
                continue
            for mode, tu in sorted(edge['modes'].items()):
                if mode not in ('walk', 'bus', 'ferry'):
                    continue
                allowed = profile in ('fastest', 'free') or mode == profile or (
                    mode == 'walk' and (edge['kind'] == 'access' or profile == 'monorail'))
                if not allowed or navigation._closed(nav, eid, start, mode, world['day'], known_only=True):
                    continue
                adjacency[start].append((eid, end, mode, tu, 0, None))
    if profile in ('fastest', 'monorail'):
        line = data['line']
        for start, end in ((line['from_id'], line['to_id']), (line['to_id'], line['from_id'])):
            if navigation._allowed(places[start], nav) and navigation._allowed(places[end], nav) and not _line_blocked(world, start, known_only=True)[0]:
                adjacency[start].append((line['ride_id'], end, 'monorail', line['ride_tu'] + line['boarding_tu'], line['fare'], True))
    initial = (0, 0, 0, (), ())
    queue = [(initial, origin, 'walk', 0, False, (origin,))]
    def state_key(node, previous, cash, boardings, rail, visited):
        # A required-service query must not use a paid circuit to pretend that
        # a closed outward departure is usable. Preserve visited signatures so
        # different simple-path labels are not incorrectly dominated.
        return (node, previous, cash, boardings, rail,
                frozenset(visited) if profile == 'monorail' else None)
    best = {state_key(origin, 'walk', 0, 0, False, (origin,)): initial}
    expanded = 0
    while queue:
        rank, node, previous, boardings, used_rail, visited = heapq.heappop(queue)
        key = state_key(node, previous, rank[1], boardings, used_rail, visited)
        if best.get(key) != rank:
            continue
        expanded += 1
        if expanded > MAX_LABELS:
            raise PlanningLimit('Planning limit reached; choose a simpler mode or nearer waypoint')
        if node == destination and (profile != 'monorail' or used_rail):
            legs, at, prev, boarding = [], origin, 'walk', 0
            for eid, mode in zip(rank[3], rank[4]):
                if mode == 'monorail':
                    line = data['line']
                    end = line['to_id'] if at == line['from_id'] else line['from_id']
                    boarding += 1
                    legs.extend(ride_legs(at, end, boarding=boarding, definitions=data))
                    at, prev = end, 'walk'
                else:
                    e = edges[eid]
                    end = e['to'] if at == e['from'] else e['from']
                    cost = e['modes'][mode] + int(mode != 'walk' and mode != prev)
                    legs.append(dict(kind='move', edge_id=eid, from_id=at, to_id=end,
                                     mode=mode, tu=cost, cash_cost=0))
                    at, prev = end, mode
            if len(legs) > MAX_LEGS:
                raise PlanningLimit('Route exceeds transition limit; choose a nearer waypoint')
            return dict(cost=max(1, rank[0]), fare=rank[1], legs=legs, mode_changes=rank[2])
        if len(rank[3]) >= MAX_LEGS:
            continue
        for eid, end, mode, tu, fare, rail in sorted(adjacency[node]):
            if end in visited:
                continue
            change = int(mode != previous)
            boards = boardings + int(mode in ('bus', 'ferry', 'monorail') and (mode != previous or bool(rail)))
            paid = rank[1] + fare
            if boards > MAX_BOARDINGS or paid > cash_limit:
                continue
            next_rank = (rank[0] + tu + int(not rail and mode != 'walk' and change), paid,
                         rank[2] + change + int(bool(rail)), rank[3] + (eid,), rank[4] + (mode,))
            prev = 'walk' if rail else mode
            next_visited = visited + (end,)
            key = state_key(end, prev, paid, boards, used_rail or bool(rail), next_visited)
            if next_rank < best.get(key, (float('inf'),)):
                best[key] = next_rank
                heapq.heappush(queue, (next_rank, end, prev, boards, used_rail or bool(rail), next_visited))
    raise ValueError('No known accessible route in this profile; try free/bus/walk or a published reopening')


def _quote_token(world, parameters):
    nav = world['navigation']
    closure_keys = ('edge_id', 'from_id', 'mode', 'start_day', 'end_day')
    known = [{k: c[k] for k in closure_keys} for c in nav['closures'] if c['known']]
    known.sort(key=lambda c: tuple(c[k] for k in closure_keys))
    public = dict(parameters=parameters, graph=graph_pin(), day=world['day'], sequence=world['command_sequence'],
        location=nav['location_id'], tu_day=nav['tu_day'], tu_used=nav['tu_used'],
        permissions=sorted(nav['permissions']), cash=world['player']['cash'],
        arrested=world['player']['arrested'], custody=world['player']['custody'],
        closures=known,
        observed=[{k: v for k, v in row.items() if k != 'source_ids'}
                  for row in world['mobility']['knowledge']['service_disruptions']])
    return digest(public)


def plan_route(world, destination, profile='fastest', *, max_tu='18', max_cash='1000000', return_to=''):
    nav = _ready(world)
    profile = 'fastest' if profile == 'auto' else profile
    if profile not in PROFILES:
        raise ValueError('Supported mobility profiles: fastest, free, walk, bus, ferry, monorail; legacy rail is retired after adoption')
    tu_cap, cash_cap = _number(max_tu, 'max_tu', 18), _number(max_cash, 'max_cash', 1000000)
    places, _ = navigation._definitions()
    for value in (destination, return_to):
        if not isinstance(value, str) or len(value) > 128:
            raise ValueError('Destination/return IDs must be strings of at most 128 characters')
    target = navigation._resolve(destination, nav, places)
    back = navigation._resolve(return_to, nav, places) if return_to else nav['location_id']
    parameters = dict(destination=target, profile=profile, vehicle_id='', max_tu=max_tu,
                      max_cash=max_cash, return_to=back)
    remaining = min(tu_cap, 18 - nav['tu_used'])
    money = min(cash_cap, world['player']['cash'])
    result = dict(origin=nav['location_id'], destination=target, return_to=back, mode=profile,
        remaining_tu=18 - nav['tu_used'], remaining_cash=world['player']['cash'],
        cost=None, fare=None, legs=[], affordable=False, status='no_known_route',
        return_cost=None, return_fare=None, return_fits_today=False, free_return_cost=None,
        free_return_fits_today=False, can_return_today=False, return_uncertain=True,
        graph=graph_pin(), restrictions=['Known access and closures enforced; unobserved disruptions may interrupt.'])
    try:
        route = _search(world, nav['location_id'], target, profile, 1000000 if profile == 'monorail' else money)
    except PlanningLimit:
        raise
    except ValueError as exc:
        result['reason'] = str(exc)
    else:
        result.update(route, affordable=route['cost'] <= remaining and route['fare'] <= money, status='quoted')
        # Caps limit this outbound transaction, not the resources physically
        # remaining for a later, separately authorized return command.
        left_tu = 18 - nav['tu_used'] - route['cost']
        left_cash = world['player']['cash'] - route['fare']
        for policy, prefix in ((profile, 'return'), ('free', 'free_return')):
            try:
                reverse = _search(world, target, back, policy, 1000000 if policy == 'monorail' else max(0, left_cash))
                fits = left_tu >= reverse['cost'] and left_cash >= reverse['fare']
                result[prefix + '_cost'] = reverse['cost']
                result[prefix + '_fits_today'] = result['affordable'] and fits
                if prefix == 'return':
                    result['return_fare'] = reverse['fare']
            except PlanningLimit:
                raise
            except ValueError:
                pass
        result['can_return_today'] = result['return_fits_today'] or result['free_return_fits_today']
        result['status'] = 'affordable' if result['affordable'] else 'unaffordable'
    result['arguments'] = dict(parameters, quote_token=_quote_token(world, parameters),
                               request_id=f'goon.request.journey.{world["command_sequence"] + 1}')
    return deepcopy(result)


def journey(world, destination, profile, vehicle_id, max_tu, max_cash, return_to, quote_token, request_id):
    arguments = dict(zip(JOURNEY_ARGUMENTS, (destination, profile, vehicle_id, max_tu, max_cash,
                                            return_to, quote_token, request_id)))
    _request_id(request_id)
    _ready(world)
    if request_id in world['mobility']['receipts']:
        raise ValueError('Duplicate mobility request; inspect its receipt instead of settling again')
    if vehicle_id:
        raise ValueError('Vehicles are not implemented in the station pilot')
    if not re.fullmatch(r'[0-9a-f]{64}', quote_token):
        raise ValueError('Invalid quote token; preview the route again')
    quote = plan_route(world, destination, profile, max_tu=max_tu, max_cash=max_cash, return_to=return_to)
    if quote_token != quote['arguments']['quote_token']:
        raise ValueError('Stale quote; preview the route again')
    if quote['origin'] == quote['destination']:
        raise ValueError('Already at that destination')
    if not quote['affordable']:
        raise ValueError(quote.get('reason', f'Journey needs {quote["cost"]} TU and ${quote["fare"]}; choose free transport, a nearer destination or explicit wait'))
    nav, mob = world['navigation'], world['mobility']
    journey_id = nav['journey_sequence'] + 1
    legs, discoveries, arrival, index, boards = [], [], quote['origin'], 0, 0
    while index < len(quote['legs']):
        leg = quote['legs'][index]
        if leg['kind'] == 'walk_gate':
            blocked, causes = _line_blocked(world, arrival, known_only=False)
            if blocked:
                observation = dict(kind='line', from_id=arrival, line_id=load()['line']['id'],
                    until_day=max(c['end_day'] for c in causes), source_ids=[c['id'] for c in causes])
                discoveries.append(observation)
                mob['knowledge']['service_disruptions'].append(deepcopy(observation))
                break
            boards += 1
            ride_destination = quote['legs'][index + 4]['to_id']
            legs.extend(ride_legs(arrival, ride_destination, journey_id, boards))
            arrival = ride_destination
            index += 5
        else:
            blocked = navigation._closed(nav, leg['edge_id'], leg['from_id'], leg['mode'], world['day'], known_only=False)
            if blocked:
                for closure in blocked:
                    closure['known'] = True
                discoveries.append(dict(kind='corridor', source_ids=[c['id'] for c in blocked],
                    edge_id=leg['edge_id'], from_id=leg['from_id'], mode=leg['mode']))
                break
            legs.append(deepcopy(leg))
            arrival = leg['to_id']
            index += 1
    cost = max(sum(l['tu'] for l in legs), int(any(l['from_id'] != l['to_id'] for l in legs)))
    fare = sum(l['cash_cost'] for l in legs)
    before_tu, before_cash = nav['tu_used'], world['player']['cash']
    nav.update(location_id=arrival, tu_used=before_tu + cost, journey_sequence=journey_id)
    world['player']['cash'] -= fare
    sequence = world['command_sequence'] + 1
    mob['receipts'][request_id] = dict(command_id=sequence, kind='journey', journey_id=journey_id,
        payload_digest=request_digest(arguments), charge_ids=[l['charge_id'] for l in legs if 'charge_id' in l])
    return event(world, 'travel', f'Arrived at {arrival}; spent {cost} TU and ${fare}.' +
                 (' Interrupted at a safe location; disruption observed.' if discoveries else ''),
        schema_version=2, journey_id=journey_id, command_id=sequence, request_id=request_id,
        graph=graph_pin(), origin=quote['origin'], destination=quote['destination'], arrived=arrival,
        interrupted=bool(discoveries), legs=legs, resources=dict(
            tu=dict(day=nav['tu_day'], before=before_tu, cost=cost, after=nav['tu_used']),
            cash=dict(before=before_cash, cost=fare, after=world['player']['cash']), fuel={}),
        asset_changes=[], discoveries=discoveries, cause='player_journey')


def mobility_report(world):
    mob = world.get('mobility')
    if mob is None:
        available = 'navigation' in world and world['navigation']['location_id'] is not None and not world['player']['arrested']
        return dict(status='disabled', adoption_available=available,
                    help='Use adopt_mobility explicitly; navigation must already be active. No vehicle purchase required.')
    return deepcopy(dict(status=mob['adoption']['status'], adoption_available=False,
        activation_day=mob['adoption']['activation_day'], scheduled_activation_day=mob['adoption']['scheduled_activation_day'],
        overlay_id=mob['overlay_id'], stations=load()['stations'], fare=load()['line']['fare'],
        station_cost=load()['line']['boarding_tu'] + load()['line']['ride_tu'],
        known_disruptions=[{k: v for k, v in row.items() if k != 'source_ids'} for row in mob['knowledge']['service_disruptions']],
        help='Free walk/bus/ferry remain. Only explicit wait refreshes 18 TU and three actions.'))


def mobility_receipt(world, request_id):
    receipt = world.get('mobility', {}).get('receipts', {}).get(request_id)
    if receipt is None:
        raise ValueError('Unknown mobility request receipt')
    return deepcopy(receipt)
