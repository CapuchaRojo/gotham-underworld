"""M014 deterministic navigation and optional career state; no economic ticks."""
from copy import deepcopy
import heapq

from location_registry import MODES, RESTRICTED_ACCESS, fingerprint, load
from simulation import event

VERSION = 1
DAILY_TU = 18
MAX_CLOSURE_DAYS = 2


def _definitions():
    data = load()
    return {p['id']: p for p in data['places']}, {e['id']: e for e in data['edges']}


def initialize(world, *, home=None, anchor=None):
    """Only called for new careers or an explicit service-command adoption."""
    places, _ = _definitions()
    world['navigation_version'] = VERSION
    world['navigation'] = dict(atlas_version=1, atlas_fingerprint=fingerprint(), rules_version=1,
        enabled_day=world['day'], activation_day=world['day'] if home else world['day'] + 1,
        anchor_id=places[home]['parent_id'] if home else anchor, home_id=home,
        location_id=home, tu_day=world['day'], tu_used=0, journey_sequence=0,
        permissions=[home] if home else [], closures=[])


def validate(world):
    from career_state import _integer, _mapping, _require
    version = world.get('navigation_version')
    history = [e for e in world['events'] if e['kind'] in ('navigation_enabled', 'navigation_activated', 'travel')]
    commands = {e.get('command_id'): e for e in world['events'] if e['kind'] == 'player_command' and e.get('command') in ('travel', 'enable_navigation')}
    if 'navigation_version' not in world:
        _require('navigation' not in world and not history and not commands, 'navigation_version', 'is required with navigation state/history')
        return
    _integer(version, 'navigation_version')
    _require(version == VERSION, 'navigation_version', 'is unsupported; supported: 1')
    nav = world.get('navigation')
    _mapping(nav, 'navigation')
    for key in ('atlas_version', 'rules_version'):
        _integer(nav.get(key), 'navigation.' + key)
        _require(nav[key] == 1, 'navigation.' + key, 'is unsupported; supported: 1')
    _require(nav.get('atlas_fingerprint') == fingerprint(), 'navigation.atlas_fingerprint', 'requires the pinned local atlas; no substitution allowed')
    places, edges = _definitions()
    day = world['day']
    _integer(nav.get('enabled_day'), 'navigation.enabled_day', 0, day)
    _integer(nav.get('activation_day'), 'navigation.activation_day', nav['enabled_day'], nav['enabled_day'] + 1)
    # Legacy batch tools may advance their clock before invoking a whole-day
    # reducer. Retain their saved budget; only begin_day refreshes it, never load.
    _integer(nav.get('tu_day'), 'navigation.tu_day', nav['enabled_day'], day)
    _integer(nav.get('tu_used'), 'navigation.tu_used', 0, DAILY_TU)
    _integer(nav.get('journey_sequence'), 'navigation.journey_sequence', 0)
    _require(isinstance(nav.get('anchor_id'), str), 'navigation.anchor_id', 'must be a string')
    anchor = places.get(nav['anchor_id'])
    _require(anchor is not None and anchor['kind'] == 'neighborhood' and anchor['access'] == ['PUB'], 'navigation.anchor_id', 'must be a public neighborhood')
    home = nav.get('home_id')
    _require(home is None or (isinstance(home, str) and home in places and 'HOME' in places[home]['access']), 'navigation.home_id', 'must be a home or null')
    current = nav.get('location_id')
    if day < nav['activation_day']:
        _require(current is None and home is None and nav['tu_used'] == nav['journey_sequence'] == 0, 'navigation', 'pending adoption cannot contain travel or an invented home')
    else:
        _require(isinstance(current, str) and current in places and places[current]['kind'] != 'region', 'navigation.location_id', 'must be a travel node')
    permissions = nav.get('permissions')
    _require(isinstance(permissions, list) and all(isinstance(p, str) and p in places and places[p]['kind'] != 'region' for p in permissions) and
             len(permissions) == len(set(permissions)), 'navigation.permissions', 'must contain unique valid place IDs')
    closures = nav.get('closures')
    _require(isinstance(closures, list), 'navigation.closures', 'must be a list')
    ids = set()
    for c in closures:
        _mapping(c, 'navigation.closures[]')
        ident = c.get('id')
        _require(isinstance(ident, str) and bool(ident) and ident not in ids, 'navigation.closures.id', 'must be unique')
        ids.add(ident)
        edge_id = c.get('edge_id')
        _require(isinstance(edge_id, str) and edge_id in edges and edges[edge_id]['kind'] == 'corridor', 'navigation.closures.edge_id', 'must reference a corridor; access spurs cannot close')
        e = edges[edge_id]
        _require(c.get('from_id') in (e['from'], e['to']) and (e['bidirectional'] or c['from_id'] == e['from']), 'navigation.closures.from_id', 'must be a valid direction')
        _require(isinstance(c.get('mode'), str) and c['mode'] in e['modes'] and c['mode'] in MODES, 'navigation.closures.mode', 'must be a supported edge mode')
        _integer(c.get('start_day'), 'navigation.closures.start_day', 0, day)
        _integer(c.get('end_day'), 'navigation.closures.end_day', c['start_day'] + 1, c['start_day'] + MAX_CLOSURE_DAYS)
        _require(type(c.get('known')) is bool, 'navigation.closures.known', 'must be a boolean')
        _require(isinstance(c.get('cause'), str) and bool(c['cause']), 'navigation.closures.cause', 'must identify a cause')
    journeys, journey_commands, travel_history = set(), set(), []
    for item in history:
        if item['kind'] == 'travel':
            _require(type(item.get('schema_version')) is int and item['schema_version'] == 1, 'travel.schema_version', 'must be 1')
            _integer(item.get('command_id'), 'travel.command_id', 1, world.get('command_sequence', 0))
            _require(item['command_id'] in commands and commands[item['command_id']]['command'] == 'travel', 'travel.command_id', 'must reference its committed command')
            _require(item['command_id'] not in journey_commands, 'travel.command_id', 'must have exactly one journey outcome')
            _require(item['day'] == commands[item['command_id']]['day'], 'travel.day', 'must match its committed command')
            journey_commands.add(item['command_id'])
            travel_history.append(item)
            _integer(item.get('journey_id'), 'travel.journey_id', 1, nav['journey_sequence'])
            _require(item['journey_id'] not in journeys, 'travel.journey_id', 'must be unique')
            journeys.add(item['journey_id'])
            for key in ('origin', 'destination', 'arrived'):
                _require(isinstance(item.get(key), str) and item[key] in places and places[item[key]]['kind'] != 'region', 'travel.' + key, 'must reference a node')
            _integer(item.get('tu_before'), 'travel.tu_before', 0, DAILY_TU)
            _integer(item.get('tu_cost'), 'travel.tu_cost', 0, DAILY_TU)
            _integer(item.get('tu_after'), 'travel.tu_after', 0, DAILY_TU)
            _require(item['tu_before'] + item['tu_cost'] == item['tu_after'], 'travel.tu_after', 'must match the charged cost')
            _require(type(item.get('interrupted')) is bool, 'travel.interrupted', 'must be a boolean')
            legs = item.get('legs')
            _require(isinstance(legs, list), 'travel.legs', 'must be a list')
            node, previous, cost = item['origin'], 'walk', 0
            traversed = []
            for leg in legs:
                _mapping(leg, 'travel.legs[]')
                eid = leg.get('edge_id')
                _require(isinstance(eid, str) and eid in edges, 'travel.legs.edge_id', 'must reference an edge')
                e = edges[eid]
                target = e['to'] if node == e['from'] else e['from'] if e['bidirectional'] and node == e['to'] else None
                mode = leg.get('mode')
                _require(target is not None and leg.get('from_id') == node and leg.get('to_id') == target and
                         isinstance(mode, str) and mode in MODES and mode in e['modes'], 'travel.legs', 'must be a contiguous permitted traversal')
                tu = e['modes'][mode] + int(mode != 'walk' and mode != previous)
                _integer(leg.get('tu'), 'travel.legs.tu', tu, tu)
                node, previous, cost = target, mode, cost + tu
                traversed.append(eid)
            _require(node == item['arrived'] and item.get('traversed') == traversed and
                     item['tu_cost'] == (max(1, cost) if node != item['origin'] else 0), 'travel', 'must match actual prefix and cost')
            discoveries = item.get('discoveries')
            _require(isinstance(discoveries, list) and all(isinstance(d, str) and d in ids for d in discoveries) and
                     len(discoveries) == len(set(discoveries)) and bool(discoveries) == item['interrupted'], 'travel.discoveries', 'must identify the bounded interruption')
            _require(item['interrupted'] or node == item['destination'], 'travel.arrived', 'must reach destination when uninterrupted')
    _require(len(journeys) == nav['journey_sequence'], 'navigation.journey_sequence', 'must agree with committed travel history')
    _require(journey_commands == {ident for ident, command in commands.items() if command['command'] == 'travel'},
             'travel.command_id', 'must provide one outcome for every travel command')
    if travel_history:
        last = max(travel_history, key=lambda item: item['journey_id'])
        _require(current == last['arrived'], 'navigation.location_id', 'must match the last committed journey')
        # A retained older TU-day marker is supported for legacy batch tools.
        # Loading must preserve its expenditure, not silently refresh it.
        expected_used = last['tu_after'] if last['day'] >= nav['tu_day'] else 0
        _require(nav['tu_used'] == expected_used, 'navigation.tu_used', 'must match the last journey or a later day reset')


def _active(world):
    nav = world.get('navigation')
    if nav is None:
        raise ValueError('Navigation is not enabled; choose a public anchor with enable_navigation')
    if world['day'] < nav['activation_day']:
        raise ValueError('Navigation activates after the next wait; loading does not activate it')
    return nav


def _resolve(value, nav, places):
    if value == 'home':
        value = nav['home_id']
    if isinstance(value, str):
        prefix = 'goon.neighborhood.' if value.startswith('n') else 'goon.poi.' if value.startswith('p') else ''
        value = prefix + value
    if value not in places or places[value]['kind'] == 'region':
        raise ValueError('Unknown travel destination; use a neighborhood or known place ID')
    if 'HOME' in places[value]['access'] and value != nav['home_id'] and value not in nav['permissions']:
        raise ValueError('Private residence: no known entry permission')
    return value


def _allowed(place, nav):
    restricted = set(place['access']) & RESTRICTED_ACCESS
    return not restricted or place['id'] == nav['home_id'] or place['id'] in nav['permissions']


def _closed(nav, edge, origin, mode, day, *, known_only):
    return [c for c in sorted(nav['closures'], key=lambda c: c['id'])
            if c['edge_id'] == edge and c['from_id'] == origin and c['mode'] == mode and
            c['start_day'] <= day < c['end_day'] and (c['known'] or not known_only)]


def _search(places, edges, nav, day, origin, destination, policy):
    if not _allowed(places[destination], nav):
        raise ValueError('Restricted destination: requires specific work, visit or staff authorization')
    adj = {k: [] for k, p in places.items() if p['kind'] != 'region'}
    for ident, e in sorted(edges.items()):
        if e['kind'] == 'access' and e['to'] not in (origin, destination):
            continue
        directions = [(e['from'], e['to'])]
        if e['bidirectional']:
            directions.append((e['to'], e['from']))
        for a, b in directions:
            if not _allowed(places[b], nav):
                continue
            for mode, cost in sorted(e['modes'].items()):
                if mode not in MODES or (policy != 'auto' and mode != policy and not (mode == 'walk' and e['kind'] == 'access')):
                    continue
                if not _closed(nav, ident, a, mode, day, known_only=True):
                    adj[a].append((ident, b, mode, cost))
    initial = (0, 0, (), ())
    queue, best = [(initial, origin, 'walk')], {(origin, 'walk'): initial}
    while queue:
        rank, node, previous = heapq.heappop(queue)
        if best.get((node, previous)) != rank:
            continue
        if node == destination:
            legs, node, previous = [], origin, 'walk'
            for ident, mode in zip(rank[2], rank[3]):
                e = edges[ident]
                target = e['to'] if node == e['from'] else e['from']
                cost = e['modes'][mode] + int(mode != 'walk' and mode != previous)
                legs.append(dict(edge_id=ident, from_id=node, to_id=target, mode=mode, tu=cost))
                node, previous = target, mode
            return dict(cost=max(1, rank[0]) if origin != destination else 0, legs=legs, mode_changes=rank[1])
        for ident, target, mode, cost in adj[node]:
            change = int(mode != previous)
            next_rank = (rank[0] + cost + int(mode != 'walk' and change), rank[1] + change,
                         rank[2] + (ident,), rank[3] + (mode,))
            if next_rank < best.get((target, mode), (10**9, 10**9, (), ())):
                best[target, mode] = next_rank
                heapq.heappush(queue, (next_rank, target, mode))
    raise ValueError('No known accessible route in this mode; choose another mode/destination or wait for a published reopening')


def plan_route(world, destination, mode='auto'):
    nav = _active(world)
    if world['player']['arrested']:
        raise ValueError('Cannot plan current travel while detained; wait for the existing court process')
    if mode not in ('auto', *MODES):
        raise ValueError('Supported modes: auto, walk, bus, rail, ferry; vehicles are not implemented')
    places, edges = _definitions()
    target = _resolve(destination, nav, places)
    route = _search(places, edges, nav, world['day'], nav['location_id'], target, mode)
    try:
        return_cost = _search(places, edges, nav, world['day'], target, nav['location_id'], mode)['cost']
    except ValueError:
        return_cost = None
    remaining = DAILY_TU - nav['tu_used']
    return deepcopy(dict(origin=nav['location_id'], destination=target, mode=mode,
        remaining_tu=remaining, affordable=route['cost'] <= remaining,
        return_cost=return_cost, return_fits_today=return_cost is not None and route['cost'] + return_cost <= remaining,
        atlas_fingerprint=nav['atlas_fingerprint'], **route))


def travel(world, destination, mode):
    nav = _active(world)
    if world['player']['arrested']:
        raise ValueError('Cannot travel while detained; wait for the existing court process')
    quote = plan_route(world, destination, mode)
    if quote['origin'] == quote['destination']:
        raise ValueError('Already at that destination')
    if not quote['affordable']:
        raise ValueError(f'Need {quote["cost"]} TU; {quote["remaining_tu"]} remain. Choose a nearer waypoint or explicitly wait')
    arrival, raw_cost, traversed, actual_legs, discovered = quote['origin'], 0, [], [], []
    for leg in quote['legs']:
        blocked = _closed(nav, leg['edge_id'], leg['from_id'], leg['mode'], world['day'], known_only=False)
        if blocked:
            discovered = [c['id'] for c in blocked]
            for c in blocked:
                c['known'] = True
            break
        arrival = leg['to_id']
        raw_cost += leg['tu']
        traversed.append(leg['edge_id'])
        actual_legs.append(deepcopy(leg))
    cost = max(1, raw_cost) if arrival != quote['origin'] else 0
    before = nav['tu_used']
    nav['tu_used'] += cost
    nav['location_id'] = arrival
    nav['journey_sequence'] += 1
    places, _ = _definitions()
    return event(world, 'travel', f'Arrived at {places[arrival]["label"]}; spent {cost} TU.' + (' Route interrupted; closure discovered.' if discovered else ''),
        schema_version=1, journey_id=nav['journey_sequence'], command_id=world['command_sequence'] + 1,
        origin=quote['origin'], destination=quote['destination'], arrived=arrival,
        tu_before=before, tu_cost=cost, tu_after=nav['tu_used'], interrupted=bool(discovered),
        mode=mode, legs=actual_legs, traversed=traversed, discoveries=discovered, cause='player_travel')


def enable_navigation(world, anchor):
    if 'navigation_version' in world:
        raise ValueError('Navigation is already enabled or scheduled')
    if world['player']['arrested']:
        raise ValueError('Cannot adopt navigation while detained')
    places, _ = _definitions()
    target = _resolve(anchor, dict(home_id=None, permissions=[]), places)
    if places[target]['kind'] != 'neighborhood' or places[target]['access'] != ['PUB']:
        raise ValueError('Choose a public neighborhood anchor; no historical home will be invented')
    initialize(world, anchor=target)
    return event(world, 'navigation_enabled', 'Navigation scheduled for the next day; historical location remains unknown.',
                 anchor_id=target, activation_day=world['navigation']['activation_day'], cause='explicit_adoption')


def begin_day(world):
    """Called after court, once on a real day transition; never by load or a view."""
    nav = world.get('navigation')
    if nav is None or nav['tu_day'] >= world['day']:
        return
    nav['tu_day'], nav['tu_used'] = world['day'], 0
    if nav['location_id'] is None and world['day'] >= nav['activation_day']:
        nav['location_id'] = nav['anchor_id']
        event(world, 'navigation_activated', 'Navigation activated at the selected public anchor.',
              location_id=nav['location_id'], cause='scheduled_adoption')


def location_report(world, destination=None):
    nav = _active(world)
    places, _ = _definitions()
    ident = _resolve(destination, nav, places) if destination is not None else nav['location_id']
    descriptions = load()['profile_descriptions']
    return deepcopy(dict(place=places[ident], current=ident == nav['location_id'],
        activities=[descriptions['civilian'][v] for v in places[ident]['civilian']],
        entry_requirements=[descriptions['access'][v] for v in places[ident]['access']],
        accessible=_allowed(places[ident], nav), home_id=nav['home_id'], remaining_tu=DAILY_TU - nav['tu_used'],
        scope='Frontage/reception only; no admission, treatment, encounter or ownership granted.',
        help='Saving, reports, existing work and explicit wait remain available. No cash is required for mobility.'))


def known_places(world):
    nav = _active(world)
    places, _ = _definitions()
    return deepcopy([p for _, p in sorted(places.items()) if 'HOME' not in p['access'] or p['id'] == nav['home_id'] or p['id'] in nav['permissions']])


def nearby_destinations(world):
    nav = _active(world)
    places, edges = _definitions()
    here = places[nav['location_id']]
    hub = here['parent_id'] if here['kind'] == 'poi' else here['id']
    neighbors = {hub}
    for e in edges.values():
        if e['from'] == hub:
            neighbors.add(e['to'])
        if e['bidirectional'] and e['to'] == hub:
            neighbors.add(e['from'])
    return deepcopy([dict(p, accessible=_allowed(p, nav)) for p in known_places(world) if p['id'] in neighbors and p['id'] != here['id']])
