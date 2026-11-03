# Gotham: The Goon — Travel and Navigation Design

**Status: proposal only.** No graph loader, movement command, time budget,
vehicle, transit or location state is implemented. All costs are provisional
design values requiring later approval. See the [atlas](GOON_GOTHAM_ATLAS.md),
[location IDs/profiles](GOON_LOCATION_REGISTRY.md),
[migration contract](GOON_MAP_SIMULATION_INTEGRATION.md) and
[map read model](GOON_MAP_VISUAL_SPEC.md).

## Typed graph and containment

The planning graph contains 8 region, 48 neighborhood and 120 POI nodes. The city
root contains regions; regions contain neighborhoods; neighborhoods contain POIs.
Those **containment edges are not travel edges**. Selecting a region cannot
teleport the player into its offices, hospitals or private homes.

Travel uses neighborhood arrival hubs and explicit POI access links. Hubs abstract
local streets/stops; they are not another 48 named buildings counted as POIs.
A public POI access link has zero additional TU because the local approach is
included in the neighborhood abstraction. Access checks still apply. An interior
requires an explicit later node/permission, not a free connection through a map pin.
The initial design provides no hidden service tunnels or private safehouse entries.

Every physical corridor has a stable ID, endpoints, direction, type, permitted
modes, positive travel TU, baseline access, and versioned descriptive data.
Actual closures, incident causes and known observations are separate state.
Crossings below are bidirectional by proposal; closures can affect one direction
or mode. An unlisted water crossing is unavailable, not an inferred straight line.

## Named crossings and regional links

IDs abbreviate `goon.edge.eXX`; endpoints abbreviate `goon.neighborhood.nXX`.
All names, endpoints and costs are original proposals. Cost lists are per mode,
before any boarding/vehicle pickup cost. Bus/rail/ferry are distinct modes.

| Edge / name | Endpoints | Type / water | Modes and TU | Baseline access |
| --- | --- | --- | --- | --- |
| e01 Northgate Bridge | n04–n17 | bridge / north West Channel | walk 4; car 2; bus 2; rail 2 | Public arrival route; highway carriageway and sidewalk are distinct |
| e02 Westbank Bridge | n07–n13 | bridge / West Channel | walk 4; car 2; bus 2 | Public |
| e03 Union Bridge | n09–n22 | bridge / West Channel | walk 4; car 2; bus 2; rail 2 | Public |
| e04 Old Dock Bridge | n12–n28 | bridge / West Channel | walk 4; car 2; bus 2 | Public |
| e05 Garden Bridge | n14–n19 | bridge / North Cut | walk 4; car 2; bus 2 | Public |
| e06 Quay Tunnel | n18–n23 | road/rail tunnel / North Cut | car 2; bus 2; rail 2 | Public transport/road; no walking lane |
| e07 Market Bridge | n24–n29 | bridge / South Cut | walk 4; car 2; bus 2 | Public |
| e08 Civic Rail Tunnel | n22–n30 | subway tunnel / South Cut | rail 2 | Public passenger service; no track-walking shortcut |
| e09 East Channel Bridge | n23–n31 | bridge / East Channel | walk 4; car 2; bus 2; rail 2 | Public |
| e10 Tide Tunnel | n36–n28 | road tunnel / East Channel | car 2; bus 2 | Public road/service; no walking lane |
| e11 South Bay Causeway | n30–n37 | causeway / South Bay | walk 5; car 3; bus 3 | Public with separate walking path |
| e12 Marsh Rail Tunnel | n41–n33 | regional rail / bay approaches | rail 3 | Public passenger service; freight authorization separate |
| e13 Breakwater Public Ferry | n31–n43 | water / Outer Roadstead | ferry 3; boat 3 | Public ferry; private boat needs lawful berth/access |
| e14 Coastal Ferry | n18–n43 | water / East Channel/Outer Roadstead | ferry 4; boat 4 | Public ferry; lawful private boat access |
| e15 Arkham Access Bridge | n43–n45 | bridge / Outer Roadstead local reach | walk 2; car 1; bus 1 | Public arrival/intake frontage only; institution perimeter is a separate gate |
| e16 Blackgate Controlled Ferry | n43–n46 | controlled water connection | ferry 2; boat 2 | Valid visitor/work/representation/authorized-transfer purpose and receiving permission |
| e17 Outer Service Ferry | n37–n43 | water / South Bay/Outer Roadstead | ferry 4; boat 4 | Public/service route; lawful private boat access |

Local street corridors complete the specification without copying a street map:

- In each of R01–R07, connect its six numbered neighborhood hubs in a ring:
  first–second–third–fourth–fifth–sixth–first. IDs are `goon.edge.local.rXX.01`
  through `.06` in that order. Each permits walking 2 TU, car 1 TU and bus 1 TU.
- On Breakwater Island connect n43–n44–n47–n48–n43 with local R08 IDs `.01`–`.04`,
  with the same costs. **Do not** run a six-node R08 street ring through Arkham or
  Blackgate water. Their only base links are e15/e16.
- Rail additionally uses local pairs n04–n05, n05–n06, n09–n10, n17–n18,
  all six R04 ring pairs, and n31–n32/n32–n33, at 1 TU. No other local edge silently
  becomes railway. Airport/rail/metro access is represented at these hubs.

This defines **63 physical neighborhood corridors**: 17 named links plus 46 local
ones. Add 120 gated POI access links, distinct from containment. The 48 neighborhood
network is connected when all applicable permissions/modes are available; a public
visitor without Blackgate authorization cannot assume access to n46. Future routes
may extend the graph with new IDs, not reuse an unrelated closed edge's ID.

Subway/road tunnels already support underground travel. A future authorized
maintenance or underground walking route needs its own explicit positive-cost,
permission-gated edge and safety review. It cannot be deduced from owning a map
or a relevant skill, and no real bypass/escape technique is supplied here.

## Modes, travel time and the three daily actions

**Proposed minimum: preserve three daily gameplay actions and add a separate
18-TU daily travel allowance.** One TU is an abstract planning increment, roughly
ten fictional minutes for presentation only, not a measured metropolitan distance
or a new real-time clock. This proposal changes no current allowance/save field.

| Mode | Availability | Additional route-entry / transfer cost | Initial fare policy |
| --- | --- | --- | --- |
| Walk | Public walk edges and actual permission; always a basic mobility option | 0 TU | Free |
| Bus / rail | Service available at the hub/edge and not closed | 1 TU each time entering a different transit mode | Zero cash in the minimum design; no paid rescue gate |
| Ferry | Published service and any required destination permission | 1 TU on boarding | Zero cash in the minimum design |
| Car | Authorized available vehicle at the actual pickup node, road permission | 1 TU on entering/picking up the vehicle | No new fuel/debt system in the minimum; ownership/use is separate future state |
| Boat | Authorized available vessel, safe permitted route/berth | 1 TU on entering/picking up the vessel | No new fuel/cargo economy in the minimum |

Continued edges in one mode do not repeatedly charge boarding. Separate travel
commands charge a new boarding/pickup when appropriate; staying inside a vehicle
requires explicit state, not an assumed free car at any destination. Future fares,
accessibility or vehicle costs require a funded economic contract and zero-cash
alternatives, not silently changing these rules.

- A successful journey consumes quoted actual TU, **zero of the three daily
  actions**, and no gameplay RNG for ordinary movement. Taking a job/mission/legal
  response retains its existing daily action cost. Local public exploration is free.
- If insufficient TU, permission or vehicle availability is known, reject without
  changing world state, cash, action usage, location, events, knowledge or counters.
  Do not consume a fourth action, partial cost or a hidden day to complete a route.
- `wait` explicitly advances one day through the existing pipeline, refreshing
  both future travel allowance and the existing three actions once. Load/report/
  route preview never refreshes either. No automatic travel overnight.
- An over-budget long journey can be planned to a safe explicit waypoint, or a
  nearer/alternate job can be chosen. Preview the return trip and service access.
  No required campaign chain should consist of repeated empty wait-and-travel days.
- Each public neighborhood hub must offer basic zero-cash wayfinding/help, a
  safe decision boundary and meaningful local alternatives. Help is an abstract
  hub service, not additional POIs counted in the registry or automatic healing.
  Exhausting TU never disables saving, reports, waiting or reachable local care.
- Institutions, custody transfers and active encounters have their own command
  constraints. A later implementation must keep lawful exit/review/support routes;
  travel cannot bypass detention, admission, combat or a completed mission's terms.

These values favor useful activities over charging one whole action per street.
Travel still changes which commitments fit together. Three actions are an abstract
gameplay allowance, not a promise that every activity lasts exactly eight hours.
Hour-by-hour calendars, daily wages/rent, ambushes and vehicle inventories are
separate future contracts. No compulsory online timetable or upgrade timer.

## Disruptions, law and faction influence

A closure identifies edge/mode/direction, causal incident, start/review day,
known status and a finite end/reassessment condition. Repairs, weather, service
failure or a declared perimeter change can alter routes. Do not freeze a city
until a real-world timer expires. Before withdrawing an accepted mission's only
route, supply an alternate, an explained cancellation/review, or useful local play.

GCPD jurisdiction, observed patrol activity and the player's M012 heat are distinct.
High heat remains bounded personal state; a map overlay is not a second heat
counter and walking into a neighborhood does not automatically create a case.
Any later documented crime or legal intervention needs an approved event/case
source and existing court/custody invariants. No per-move evidence farm.

Faction influence can affect known work, willingness to vouch for access or a
specific declared obstruction. It cannot silently erase public roads, grant a
prison pass or turn minor-crew presence into district ownership. Restrictions
require actual actors, resources and explicit rules. Choosing an alternate route
is an abstract game decision, not instructions for evading real law enforcement.

## Deterministic selection and atomic execution

Route queries use a detached **player-known graph**, mark stale/uncertain edges
and consume no RNG. Return quoted TU, mode changes, permissions, known disruptions,
return options and the knowledge/network revision used. Never reveal a hidden
safehouse or closure by displaying the full authoritative graph in an ordinary UI.

Use standard-library graph search with stable sorted adjacency. A valid approach
is bounded Dijkstra over `(node_id, mode_id, TU_spent)` states, including boarding
costs and the 18-TU limit. Default ranking is total TU, then mode changes, then
lexicographic edge-ID sequence. An accessible/avoid-known-closure policy filters
eligible edges before search. Future monetary/risk budgets require additional
state or nondominated labels; a naive single-best-node label may discard a valid
route under several constraints.

Containment never enters search. POI zero-cost access links are endpoint spurs;
never revisit an identical search state through a zero-cost loop. Travel corridors
have strictly positive TU. Sorted IDs and explicit queue tie-breaking, never Python
`hash`, insertion order or coordinates, determine equal-cost choices.

A future command revalidates the quoted route on a private candidate world and
commits through `game_service`. Known-invalid input is rejected atomically. An
unknown obstruction discovered during an otherwise valid attempt can instead be
a **successful bounded domain outcome**: arrive at the last safe hub, charge only
the traversed prefix within the quote, and record the discovery/knowledge event
once. That is not an exception leaving accidental partial state. Never place an
actor in the middle of a bridge or charge an untraversed suffix. UI animations
consume no time and cannot apply the outcome again.

No daily phase runs per edge or route preview. Actual world/knowledge revisions,
route IDs, causal discoveries and any later encounter draws need persisted
versioned state. Use a separate seeded namespace only if a separately approved
incident mechanic actually needs randomness; ordinary navigation needs none.

## Structured example and paper arithmetic

Illustrative future definition, **not a registered schema or current save**:

```json
{
  "definition_version": 1,
  "id": "goon.edge.e05",
  "from": "goon.neighborhood.n14",
  "to": "goon.neighborhood.n19",
  "bidirectional": true,
  "kind": "bridge",
  "modes": {"walk": {"tu": 4}, "car": {"tu": 2}, "bus": {"tu": 2}},
  "access": "public"
}
```

**Paper example:** n13–n14–n19–n24–n23–n31 by bus uses edge TU
`1 + 2 + 1 + 1 + 2 = 7`, plus one boarding TU: **8 TU**. A separate return is
another 8 TU, leaving two of the proposed eighteen TU and all three gameplay
actions before activities. Walking the same route is `2 + 4 + 2 + 2 + 4 = 14 TU`,
so a walking round trip does not fit that day. If e05 closes, a bus alternative
through n07–n08–n09–n22–n23 uses `2 + 1 + 1 + 2 + 1 + 2 + 1 boarding = 10 TU`.
The player can change commitments or use local work; movement is not a source
of cash or skill XP. These are specification calculations, not executed travel tests.

## Ten-field review and future acceptance

| Criterion | Travel contract |
| --- | --- |
| Decisions | Choose route/mode, commitments, waypoint, verification or local alternative |
| Feedback | Show costs, permissions, return feasibility, known closures and uncertainty |
| Persistent state | Future location, TU usage, pinned graph, valid discoveries and route outcome IDs |
| Alternatives | Public transit, walking, changed work, bounded cancellation or local support |
| Replayability | Demand, contacts, closures, vehicle availability and knowledge change useful plans |
| Grind risk | Repeated commute/wait clicks, XP loops and unneeded traversal; batch a route and keep local exploration free |
| Determinism | Canonical graph/queue, integer costs, explicit revisions and atomic outcomes |
| Save compatibility | Additive opted-in geography state; no old career relocation, extra clock tick or budget refresh |
| Offline | Local graph, schedules, routing and definitions; no map/geocoding API |
| Agency / exploits | No free region teleport, gate bypass, reward per move, duplicate boarding/refund or over-budget stranded campaign |

Future tests must cover all endpoints/modes, base connectivity and gated exceptions,
tie ordering, return costs, zero cash, TU exhaustion, no-path results, stale/unknown
closures, safe-prefix outcomes, blocked interiors, repeat commands, report isolation,
historical migrations and fresh-process/save-resume determinism. They are not
implemented by this documentation milestone.
