# M016 mobility architecture — review draft

**Current status — Mission 013:** M016-A is implemented locally on
`feature/m016a-mobility-pilot`, based on `3251381177bf11c0b07cd940329ebd0be3a7bb52`.
See section 14 and the [implementation/validation report](M016_A_IMPLEMENTATION_VALIDATION.md)
for the executable contract. Sections 1–13 preserve Mission 011/012 reconnaissance,
examples and future proposals; their earlier no-implementation instructions and
approval gates describe those missions. They do not imply that broader M016
vehicles are implemented. PR #15 remains open/unmerged; no push/merge is authorized.

**Mission 012 hardening:** this is the same preserved Mission 011 draft, extended
with the decision contract, atlas-backed pilot, concrete schema/event examples,
transaction protocol and exact first-slice files in sections 8–13. Those sections
resolve earlier provisional choices; they remain proposals, not implementation.
On the same HEAD/branch, Mission 012 executed the unchanged regression suite:
`python -B -m unittest discover -s tests -q` — **283 tests, 45.228 seconds, OK**.
PR #15 was rechecked open at the same head. Only these three M016 documents are
being updated; original pre-edit drafts were also preserved in a temporary backup.

## Status, evidence and scope

Mission 011, November 4, 2026. **Proposal only; no M016 runtime, schema,
atlas or test changes have been made.** Implementation requires a separate
authorization. PR [#15](https://github.com/CapuchaRojo/gotham-underworld/pull/15)
remains open and unmerged.

Verified source baseline: `3251381177bf11c0b07cd940329ebd0be3a7bb52`, on
`feature/m015-living-gotham`; fetched remote head matches. Master is
`fa2f9f5bbf081bde080c6d8b2e46512487027c66`. These drafts were prepared on the
separate local branch `docs/m016-mobility-architecture` from that baseline.
The [M015 independent audit](M015_INDEPENDENT_ACCEPTANCE_AUDIT.md) records the
corrected 283-test baseline. Both GitHub checks on the exact head are successful;
the inspected [CI log](https://github.com/CapuchaRojo/gotham-underworld/actions/runs/41873861331/job/126727886517)
reports **283 tests in 31.786 seconds, OK**.
This planning mission inspected source/tests and ran in-memory navigation
diagnostics; it did not rerun the regression suite or test proposed M016 behavior.

No M016 design PDFs were supplied or found in the repository or provided
attachment directory. Nothing below attributes rules to unseen PDFs. Labels
**Verified** and **Proposed** distinguish implementation from recommendations.
Creative direction is approved direction, not approval of these schema, price,
content or algorithm choices. All mechanics remain content-independent,
standard-library-only and offline; no licensed assets or story content is added.

Companion drafts: [acceptance matrix](M016_MOBILITY_ACCEPTANCE_MATRIX.md) and
[integration risk register](M016_INTEGRATION_RISK_REGISTER.md). Existing contracts:
[runtime](GOON_WORLD_RUNTIME.md), [roadmap](GOON_MILESTONE_ROADMAP.md),
[M015 choices](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md) and
[future prologue](GOON_PLAYABLE_PROLOGUE_CONTRACT.md). This draft does not
supersede their implemented rules or authorize the prologue.

## 1. Verified navigation and ownership map

| Owner / source | Actual behavior at the audited commit |
| --- | --- |
| [Registry validation](../location_registry.py#L19), [loader](../location_registry.py#L97) | Local atlas v1: 176 places (8 regions, 48 neighborhoods, 120 POIs); 183 edges (63 corridors, 120 POI access spurs). Regions are not travel nodes: 168 usable nodes. IDs, hierarchy, costs, access and references are validated. Public `load()` returns detached definitions. |
| [Pinned atlas](../content/gotham_atlas_v1.json), [fingerprint](../location_registry.py#L111) | SHA-256 `14a38c5376989351d83bf90ed172c557a3dbf13c1323a115d2c2144f5136860a`. JSON object keys are canonicalized; array ordering still affects the pin. Reordering a runtime lookup is different from editing the pinned file. |
| [Initialization](../navigation.py#L18), [service creation](../game_service.py#L38) | New careers start at recorded home p031. Historical loading does not invent navigation. Explicit `enable_navigation` accepts a public neighborhood, leaves home/location null while pending, and activates after a real day transition. |
| [State validator](../navigation.py#L29) | Navigation format/rules/atlas versions are all 1. It checks location, home/permissions, TU, closures, journey identities and structured history against the pinned base registry. Unsupported versions fail clearly. |
| [Access](../navigation.py#L161) | HOME/WORK/VIS/SEC need home entitlement or permission. Public frontage does not grant institutional admission, a job or a release. Outward departure remains possible after a visit permission is revoked. |
| [Search](../navigation.py#L172) | Dijkstra over `(node, previous_mode)` with integer cost; rank is `(TU, mode changes, edge-ID sequence, mode sequence)`. Stable sorted choices avoid dictionary insertion-order decisions. |
| [Preview](../navigation.py#L215) | Detached, known-state outbound and reverse searches; reports cost, affordability and whether both fit current remaining TU. It has no fuel, cash or vehicle end state to project today. |
| [Travel](../navigation.py#L235) | Replans, enforces budget/access and commits either arrival or a safe actual prefix at an unknown closure. Same-location travel rejects. Travel costs zero gameplay actions and never advances the day/economy. |
| [Day phase](../navigation.py#L283), [pipeline](../gameplay.py#L77) | 18 TU/day; reset once after court processing, before daily life. Reads and loads never refresh it. Historical low-level clock-only tools may retain an older TU-day marker until a real whole-day phase. |
| [Command boundary](../game_service.py#L70) | Strict string arguments, private candidate, no commit on rejection, monotonic command sequence, detached response. Three daily actions are separate from TU. All player-facing mutations must pass here; low-level reducers still exist for legacy tools. |
| [Career validation](../career_state.py#L223), [persistence](../career_persistence.py#L64) | Nested validation before play/write; staged flushed/fsynced writes, atomic replacement, previous-good backup, exclusive first save. Failed I/O must preserve primary, caller world and recoverability. |

### Modes, costs and closures — verified

Runtime modes are `walk`, `bus`, `rail`, `ferry`. `car` and `boat` appear in
atlas metadata but are not executable modes. Corridor availability counts are
walk 55, bus 57, rail 18, ferry 4; metadata car 57 and boat 4. All existing
corridors are bidirectional, though definitions and tests support one-way travel.

Corridor costs are positive integers. POIs have zero-cost walking spurs to their
parent neighborhood. Spurs are permitted only at the journey origin/destination,
so intermediate POIs cannot form free shortcuts. Any completed movement costs
at least 1 TU. Entering bus/rail/ferry from a different previous mode adds 1 TU;
continuing that mode does not. Every separate journey starts with previous mode
`walk`. Explicit mode policy filters corridors but permits walking POI spurs;
a same-neighborhood `rail` request can therefore contain no rail at all.

Closures are directed, mode-specific corridor records with known/unknown status,
cause and dates; maximum duration is two advanced days. There is no implemented
random closure generator. Preview avoids known closures without revealing
unknown ones. Execution observes a hidden closure, records discovery and charges
only actually traversed legs; a blocked first edge can cost zero. It stops at a
valid node, not halfway across an edge. Insufficient budget/known failure rejects
without mutation. Custody blocks preview/travel; inspection and explicit wait
remain available. Finite reopening offers recovery, not free teleportation.

### Events and validation — verified

`travel` schema 1 records command/journey IDs, requested destination, actual
arrival, legs, TU before/cost/after, traversed IDs, discoveries and interruption.
Validation requires one outcome per committed `travel` command, unique journey
IDs/count, contiguous base-graph legs with reconstructed costs, matching command
day, and latest location/TU consistent with history and subsequent day resets.
It accepts neither overlay IDs nor schema-2 travel today. Adding an unknown
mobility dictionary alone would not extend this validator safely.

### Daily life and legal integration — verified

[Daily life](../daily_life.py#L22) is a separate explicit enrollment, even for
new careers. Its home agrees with navigation; current work/appointments require
specific base places and day windows. [Eligibility](../daily_life.py#L230) never
travels automatically. A journey does not expire a promise, earn a wage, refresh
an action, change a faction account or consume a job RNG attempt. `wait` runs the
existing world pipeline, including room review/offer expiration once per day.
There is no hourly clock, license, vehicle theft, impound or physical prison
release system. Arrest/custody is legal state, not proof the player is physically
inside the Blackgate POI. The prologue and supervision remain future proposals.

## 2. Rail and station reconnaissance

**Verified:** all 18 rail edges join neighborhoods directly. No boarding station,
service line, platform, fare or station permission participates in search.

| Base edge suffix | Endpoints (neighborhood suffixes) | Rail TU before boarding |
| --- | --- | ---: |
| e01 | n04–n17 | 2 |
| e03 | n09–n22 | 2 |
| e06 | n18–n23 | 2 |
| e08 | n22–n30 | 2 |
| e09 | n23–n31 | 2 |
| e12 | n41–n33 | 3 |
| local.r01.04 / local.r01.05 | n04–n05 / n05–n06 | 1 each |
| local.r02.03 / local.r03.05 | n09–n10 / n17–n18 | 1 each |
| local.r04.01 / .02 / .03 | n19–n20 / n20–n21 / n21–n22 | 1 each |
| local.r04.04 / .05 / .06 | n22–n23 / n23–n24 / n24–n19 | 1 each |
| local.r06.01 / .02 | n31–n32 / n32–n33 | 1 each |

Full IDs use `goon.edge.`. e08/e12 are rail-only; masking entire mixed edges
elsewhere would unnecessarily remove road modes.

Public POI candidates include p002 Bristol Station (n01), p022 West Regional
Station (n10), p039 Highbridge Metro Stop (n17), p071 South Gate Subway Stop
(n30), p072 South Gate Bus Terminal (n30), p081 East Mainland Regional Station
(n33), p091 South Exchange Coach Station (n37), and p099 South Rail Passenger
Station (n41). Names/types are descriptive metadata, **not monorail services**.
Freight/maintenance POIs have WORK restrictions; police/fire stations are not
transit stations. Ferry frontages p026/p041/p054/p106 similarly do not imply
vehicle-carrying ferry service. No station identity may be inferred from a name
substring or assumed to exist in every DC continuity.

**Executed diagnostic:** with seed 42, service travel to n22 followed by a
read-only rail preview to n30 returned e08 directly, 3 TU outbound and 3 return,
without visiting a POI. A graph traversal excluding rail and authorized corridors
reached all 47 public neighborhoods from n13; only restricted n46 was excluded.
This proves structural connectivity of the unchanged free graph, not daily
affordability or closure resilience of a future overlay.

**Proposed:** create a small additive overlay with explicit station entrance,
platform, line and boarding/alighting transitions. A two-stop pilot may co-locate
platforms at existing public station frontages. The earlier p022/p081 candidate
is superseded by the atlas-backed p039/p071 pilot in section 9; neither is an
existing monorail service. Transit gate
nodes must be usable intermediate nodes; current POI-spur rules cannot simply
be reused unchanged. Author specific station access transitions while preserving
the ban on arbitrary intermediate POI shortcuts.

## 3. Recommended model — proposed, not implemented

### Choose a hybrid, rather than merely extending MODES

| Approach | Fit / problem in this engine |
| --- | --- |
| Every item is a mode | Leg descriptions are clear, but adding bike/car to current `MODES` grants universal availability and generic boarding penalties without ownership, parking, fuel or stations. |
| Everything is a capability | Useful for carried equipment; insufficient to distinguish a parked bike/car, a passenger service and a personal vehicle's ending location. |
| Uniform route-cost modifiers | Small code change, but hides access/provenance and can wrongly accelerate water crossings, restricted gates or travel without the actual item. |
| Recommended hybrid | Walk baseline; carried skateboard capability with explicit leg propulsion; bicycle/car as located ground vehicles; monorail as typed station-service transitions. Bus/ferry remain supported services. |

| Principal mode | Proposed prerequisites and trade-off |
| --- | --- |
| Walking | No fare, vehicle, fuel or license. Uses only permitted foot edges; cannot cross water or institutional gates by assertion. Flexible fallback, slower on long routes. |
| Skateboard | Actual carried instance, usable condition, authored rideable surface. Faster only on suitable edges; carry at walking speed on rough/forbidden edges and through permitted transit gates. No spontaneous item at each node. |
| Bicycle | Reach its storage/parking node; right to use, usable condition. Ride permitted cycle/road links or push on permitted foot links at walking cost. Park/store explicitly or finish with bike in hand. Theft exposure is a future incident hook, not an automatic daily RNG tax. |
| Car | Reach a parked instance, keys/right to use, valid driving authorization and no applicable restriction, sufficient fuel/condition, road path and valid parking. Retrieval/setup and terminal parking can make short trips worse. |
| Monorail | Reach accessible station entrance/platform, pay disclosed fare and board a specific line. Alight at a real arrival platform and walk out. Rapid trunk travel does not imply an express doorway-to-doorway edge. |

Initially passengers may carry a skateboard; bikes require an explicit cargo rule,
and cars cannot silently board monorail/bus/passenger ferry. Unknown road-surface
metadata defaults to walking/carrying, not a skateboard speed grant. Existing car
metadata is a road-topology candidate, not sufficient proof of safe parking,
legal access or fuel cost. Author/validate those overlay attributes first.

### Authoritative state and identity

The proposed `navigation_version: 2` continues to own **one player location**,
18-TU accounting, permissions, closures and global journey sequence. An optional
`mobility_version: 1` owns assets, use rights, driving credentials/restrictions,
adoption metadata and player observations. This is a conceptual ownership
contract, not a schema change made by this mission.

Require the nav2/mobility1 pair even when the asset inventory is empty; reject
active mobility under nav1 or missing paired state. The initial `with_actor`
placement supports the player only. Other mobile custodians require an actual
authoritative actor-location contract first; current NPC definitions are not
evidence of implemented NPC movement.

Each asset has a stable instance ID distinct from its reusable definition ID,
legal owner-party ID, right-to-use grant/provenance, bounded condition 0–100,
and exactly one tagged physical placement:

- `parked/stored`: node ID and physical custodian ID;
- `with_actor`: actor ID and carried/pushed/operated role; position derives from
  that actor's authoritative location, with no duplicate absolute location;
- `impounded`: facility node and custodian ID, only after an explicit supported
  transfer event.

World-truth missing/stolen assets still have a physical placement. Player
observations hold last-known position/status separately; a public view must not
reveal a hidden thief or actual location. Possession and availability are derived
from placement and rights, not contradictory `owned/available/with_player` flags.
Legal title does not grant keys, physical access, fuel or a license. A borrowed
asset can be in possession without title; an expired grant forbids further
unauthorized operation but never teleports or deletes the asset.

Cars have integer fuel units/capacity; bikes/boards do not acquire meaningless
fuel fields. Conditions use coarse usable bands, not a repair chore every trip.
Future skills may alter authored integer costs under a pinned rules version;
do not add a second attribute system now. Ground selection is one vehicle per
request, plus at most one carried board. Search must not enumerate the fleet.

| Acquisition source | Proposed effect / boundary |
| --- | --- |
| Purchase | Disclosed price, existing player cash debited once, title and placement transferred from a unique source stock instance. |
| Loan | Time/permission-limited use grant; original title retained; return terms disclosed. Day-based expiry only because travel does not advance days. |
| Gift | Explicit donor/source transfer once; no repeated gift on inspection or reload. |
| Discovery | Observation/retrieval opportunity, not automatic legal title, keys or permission. |
| Fictional criminal acquisition | Represent provenance and contested title, but gate acquisition gameplay until a compatible non-job legal-source adapter is approved. Never invent a collection job, payout or witness merely to create evidence. |

Instance/source IDs, transfer receipts and accepted request IDs enforce
idempotency. The same asset cannot be acquired twice, belong to multiple stock
entries or be both parked and carried. No grants occur on load or adoption.
Driving authorization needs one owner and a lawful acquisition source approved
before the car slice; legal adapters may read/issue that record, not mirror it.
Arrest is not automatic confiscation: impound requires its own causal event.

## 4. Door-to-door routing and execution — proposed

### Small bounded extension

Current `(node, previous_mode)` is insufficient: two arrivals at the same node
with different parked-car locations, fuel, fare money or line context are not
interchangeable. Use resource-constrained label-setting Dijkstra, with explicit
typed transitions rather than a large transport framework.

A label contains node, service/line context, selected ground-vehicle phase
(`unused`, `with_player`, `parked`), its placement signature, portable-item state,
TU spent, cash spent and fuel remaining. Include any condition band that affects
feasibility. Keep different ending placements separate for dominance. For the
initial scope allow one ground pickup, one continuous ride/push interval, and
one final parking; after parking, finish by walking/transit. More elaborate
multi-vehicle tours require waypoints or a separately approved expansion.

For `fastest`, deterministically rank feasible plans by `(TU, cash, transfers,
equipment handling, edge-ID sequence, transition-ID sequence, propulsion-ID
sequence)`. A `free` profile constrains cash spend to zero. Explicit allowed
modes and vehicle selection constrain feasibility; they do not grant assets.
Do not use a hidden weighted score. Preserve v1 rank exactly for non-adopters.
All costs are integer/nonnegative; completed movement has a 1-TU floor.

Only authored station transitions may board/alight/change lines. Boarding/setup
charges belong to these transitions, not the old generic non-walk surcharge.
Alight before ordinary walking; a new fare-paying line boarding is explicit.
Station/vehicle pickup access can be intermediate only where the overlay
authorizes it. Monotonic pickup/parking phases, non-rewarding transitions and
dominance checks eliminate beneficial zero-cost handling/access loops.
Reject a repeated identical structural state within a candidate path when no
resource improves, including zero-cost station-access cycles; lexicographic edge
tie-breaking alone is not a cycle guard. Resource replenishment is a separate
command, never a negative-cost routing edge.

Proposed bounds: 168 base nodes plus at most 24 pilot overlay nodes (at most
12 stations), 64 transitions per plan, two service boardings, one ground vehicle,
8,192 expanded labels per query. Return search has its own same bound. On bound
exhaustion return an explicit planning-limit result; never silently prune a
feasible alternative and claim no physical route. Offer a verified simpler/free
plan or waypoint suggestion when possible. These limits need acceptance tuning.

### Preview and command boundary

Read-only preview receives destination, allowed modes/profile, selected vehicle,
TU/cash caps and optional return target (default home when present, otherwise
origin). It returns full approach/retrieval/board/ride/park/alight/egress legs,
known prerequisites, TU/fare/fuel deltas, endpoint and equipment placement,
affordability, and **return from the projected outbound end state**. Return uses
remaining fuel/cash, new vehicle placement, direction/access and known closures.
Separate route existence, outbound affordability, same-day return feasibility
and next-day recovery. A quote is not a reservation or guaranteed safe return.

Proposed service command `journey` has explicit string arguments consistent with
the current service: destination, profile, vehicle ID (or empty), maximum TU,
maximum cash, quote token and request ID. Validate/canonicalize bounded numeric
strings; no arbitrary options/eval. A detached preview can produce those fields
for the CLI. Exact grammar is an approval item. New acquisition/handling commands
also need source/request identities, without creating a second mutation API.

A quote token binds known request, pins and relevant observed resources/state,
not secret closures or the entire hidden world revision. No persistent quote
cache, RNG draw or world mutation on preview. Reject publicly stale quotes before
effects; discover hidden changes only at legitimate observation points. Execution
revalidates on the service candidate. Accepted request IDs are unique: repeating
one rejects unchanged; a separate receipt view can recover its detached outcome.
This adds retry protection deliberately; current service command sequencing
alone is not a client retry/idempotency token.

`travel` remains available for v1/pending-routing careers. For active rules2 it
must clearly direct callers to `journey`, preventing legacy rail bypass. New UI
may hide this distinction, but validation must link both command families to
exactly one outcome each. The three-action and 18-TU limits remain unchanged;
journeys use TU and zero gameplay actions. No implicit wait, wages, job draw or
faction tick. Purchasing/repairing must have separately approved action prices.

### Failure, closure and resource contract

- Known lack of rights, custody, fuel, fare, access, budget or known vehicle
  absence rejects with the entire world, RNG, event/command sequence unchanged.
- Unknown closure or unknown vehicle loss may yield one committed interrupted
  outcome: traverse/observe a real prefix, end at a safe valid node, update only
  legitimately learned facts, charge actual prefix resources. If loss was
  already known, reject before movement. Do not expose hidden truth in preview.
- Check a blocked departure before charging the setup/fare for that departure;
  approaching a station/last-known vehicle location is still real travel. A
  first blocked departure without movement costs no fare/fuel/TU. Previously
  completed boarding/riding is not refunded if a later leg becomes blocked.
- Each car checkpoint must support safe stopping and parking/alighting. Reserve
  terminal parking TU in the quote so an interrupted prefix never exceeds its
  approved cap. Player/vehicle move together during operation; no mid-bridge
  stranding, split placement or charge for an untraveled suffix. Train interruption
  ends at a real safe station, not an arbitrary neighborhood halfway along a line.
- No cash/fuel overdrafts; consuming prepaid fuel is not a second cash debit.
  Actual refueling is a separate transaction, not mandatory before every trip.
  Save only the committed outcome, not a half-applied in-flight transaction.
- Zero remaining TU rejects travel without knowledge farming. Reading, saving,
  court/wait and recovery information remain available. No automatic allowance
  reset. An isolated safe node needs a bounded reopening or free exit plan;
  graph publication must prove that fallback. Waiting can still expire a real
  M015 opportunity, and must be presented as a consequential choice.

## 5. Save compatibility and explicit adoption — proposed

1. **Freeze the base.** Keep atlas v1 and its fingerprint unchanged. Publish an
   independently versioned/fingerprinted local overlay keyed by stable base IDs,
   with namespaced station, platform, line, transition and vehicle-definition IDs.
   Asset instance IDs use durable sequences/source IDs, never display names or
   process hashes. Validate overlay endpoints, permissions, nonnegative costs,
   safe stops, reciprocal assumptions, surfaces and zero-cash escape topology.
2. **Dual readers.** New engine reads historical no-navigation, nav1 and opt-in
   nav2 careers. Keep outer save version 1 if its optional-subsystem contract
   remains adequate; do not silently treat an unknown nav version as absent.
   Nav2 pins both base and overlay/rules. Missing/mismatched content fails with
   recovery guidance; archive released overlays locally rather than substitute
   latest definitions. Forward compatibility with old binaries is not promised.
3. **No auto-conversion.** Keep `create_career()` v1 behavior by default initially;
   offer explicit mobility enrollment for new or old careers. A historical career
   without navigation first follows existing enable/activation. No new home,
   vehicle, fuel, fare money, actions or free travel is granted.
4. **Pending adoption.** An authorized command upgrades the format to nav2
   immediately, records a pinned pending mobility request, and retains routing
   rules1 until the next real `wait`. This makes the M015 binary reject the
   unsupported navigation version rather than ignore assets. Loading/repeating
   enrollment never activates or refreshes. Pending v1 travel remains valid.
5. **Activate once.** Inside the existing post-court navigation day phase, capture
   the final legacy checkpoint before resetting TU; activate rules2 after that
   one reset and before daily life. Retain both pre-reset and activation TU
   markers, position and journey/command IDs. Existing lawful day reset is
   the only replenishment. Respect detention and existing permission revocation;
   do not teleport. A stale low-level clock marker is not an activation trigger.
6. **Preserve history.** Keep every schema-1 event byte-for-byte as JSON values.
   Validate it under base v1 rules, including pending-period v1 journeys. Check
   their final arrival at the immutable activation checkpoint, rather than
   incorrectly requiring the latest v2 location to equal the last v1 arrival.
   Checkpoint is audit evidence, not another live player-location field.
7. **New outcomes.** Recommend `travel` schema2 for new journeys, carrying graph/
   rules pins, complete typed legs, actual prefix, per-resource before/after,
   asset placements, discovered facts and causal charge/transfer references.
   Continue the global journey sequence; exactly one outcome per `travel` or
   `journey` command, no duplicate accepted request/receipt. Validate continuity
   across checkpoint, resets and both event versions, not two disconnected logs.
8. **Retire shortcuts only on adoption.** Rules2 masks legacy `rail` mode entries
   in its composed active graph, retaining walk/bus/ferry on mixed edges. e08/e12
   become inactive legacy links. `monorail` is a new distinct service; do not
   relabel old rail events. Unadopted/pending routing stays identical. No changes
   to bus/ferry fares or legacy job/legal/faction rules. Confirm connectivity and
   budgeted local livelihood before publishing the overlay.
9. **Validation and recovery.** Reject contradictory placement, unknown instance/
   content IDs, duplicate receipts, forged balances, impossible fuel, missing
   journey effects and unsupported versions before gameplay/I/O. Reuse atomic
   write/backup behavior and test its failure paths with the new nested state.
   Public projections omit secret asset locations; full debug snapshots remain
   explicitly world-truth tools. Arrest blocks movement, not ownership history.
   Impound/release transfers require future supported events, not guessed defaults.

## 6. Balance fixtures and meaningful choices — paper only

These are **illustrative synthetic route arithmetic, not implemented prices,
atlas routes or benchmark measurements**. Compare TU and cash separately.
Assume monorail boards for 1 TU and $2, car retrieval 1 TU plus terminal parking
1 TU, bike mounting/retrieval 1 TU, free basic parking, no per-trip repair chore.
Fuel figures consume already-owned units; no implied double cash charge.
All durations are abstract TU, not hours or real-time waiting.

| Situation | Illustrative alternatives | Meaningful decision / persistent consequence |
| --- | --- | --- |
| Short neighborhood trip | Walk 1; board carry/ride 1; bike 1 setup + 1 ride = 2; car 1 + 1 drive + 1 park = 3. | Walk wins simplicity and avoids relocating assets. No arrival reward or zero-cost loop. |
| Medium commute | Walk 6; smooth board 4; bike at hand 1 + 2 = 3; car 1 + 2 + 1 = 4, 1 fuel. | Bike wins free speed where actually available; ends at work/in hand, not magically at home. |
| Cross-city, nearby stations | Monorail 1 approach + 1 board + 3 ride + 1 egress = 6, $2; bus 9, $0; car 1 + 3 + 1 = 5, 3 fuel. | Mono return 12 TU/$4 fits 18 if cash permits; car wins speed with resources; bus preserves money. |
| Station far away | Mono 5 approach + 1 + 3 + 2 egress = 11, $2; bike 1 + 6 = 7; bus 8. | Station access removes the express advantage. Choose reachable service or bike, not abstract nearest line. |
| Car parked elsewhere | Walk 4 to car + 1 retrieve + 2 drive + 1 park = 8, 2 fuel; carried board 5; bus 6. | Car ownership alone is no shortcut. Retrieving it today changes tomorrow's options. |
| Bicycle stored at home | Walk 3 home + 1 mount + 2 ride = 6; walk directly 5. | Leave bike stored or spend extra TU to position it at destination. No remote summon. |
| Zero cash | Mono unavailable; walk 6, bus 4 or permitted ferry remain free; bike 3 if already usable. | Free public travel remains viable without borrowing/stealing or mandatory wage farming. |
| Missed appointment | Outbound 6 leaves 12 TU but does not itself advance day. Explicit wait across due day can break an existing promise once. | Re-route/renegotiate where an existing option allows it, or accept its recorded consequence. No invented hourly lateness. |
| Closed line | Known mono line omitted; bus 8 or walk 12; unknown closure after 1-TU approach stops at station. | Only actual prefix charged, discovery persists; no legacy rail bypass. Choose detour or explicit wait. |
| License restriction | Car plan fails known prerequisite; board 4/bus 5 remain. | Ownership retained; neither a license grant nor automatic impound. Clear reason and accessible alternative. |
| Lost/stolen vehicle | Known missing bike unavailable; unknown loss found after 2-TU walk to last-known parking, no bike setup charged. | Observation changes later plans; actual title/placement persist separately. Theft generation is not part of the first slice. |
| Limited return TU | Start with 10 TU; mono outbound 6 leaves 4, return needs 6 and another $2. | Outbound affordable, same-day return false. Choose a nearer task/free alternative or disclosed safe wait; no reset by home inspection. |

Walking, bicycle and monorail each win a plausible situation; cars win some long
road journeys, and boards suit flexible smooth short/medium trips. No mode is
universally fastest and cheapest. Variety comes from actual asset placement,
terrain, access, fare budget, obligations and disruptions. Persistent effects are
cash/fuel use, parked assets and learned closures, not commute XP. The shallow
part remains transport logistics: no traffic personalities, hourly schedules or
theft simulation is promised. A planner should expose complete routes and clear
alternatives; avoid obligatory fuel/parking/repair menus for every leg. Local
M015 work and free mobility must survive without purchasing a vehicle. A newly
released character needs permitted walking/free transit and basic support,
independent of possessions; physical Blackgate release needs a separate contract.

## 7. Proposed implementation slices — do not execute in Mission 011

| Slice | Small deliverable | Required evidence before proceeding |
| --- | --- | --- |
| 0. Compatibility seam | Golden v1 journeys/saves, independent overlay validator, dual-version reader/checkpoint contract; no active gameplay change. | Existing 283 tests unchanged; schema-1 reconstruction, missing pins and failed saves tested. |
| 1. First playable pilot | Two approved stations, walking + station-only monorail, explicit opt-in, quote/commit, fare, closure prefix and projected return; versioned events/save resume. | Station-only boarding, free fallback, no rail bypass, exactly-once charges, pending/active adoption and M015 equivalence. No vehicle or license dependency. |
| 2. Portable capability | One authored skateboard source/surface set, actual carried instance, carry/ride transitions. | No remote asset use or surface shortcuts; costs, condition, receipt retry and transit carrying tests. |
| 3. Bicycle | One lawful acquisition/loan source, storage/retrieval, ride/push/park and projected return placement. | Ownership/use-right distinction, expiry, zero-cash fallback and save-consistent vehicle position. No random theft engine. |
| 4. Car | Approved lawful driver-credential source, one car, road/parking/fuel rules and bounded query extension. | Fuel/condition/access restrictions, safe interrupted parking, legal/custody checks and economic receipts. |
| 5. Conditional later adapters | Non-job legal source, authored loss/theft/impound/release hooks only after their own approval. | Truth/knowledge separation, causal legal records and post-release free mobility. Not an implicit M016 commitment. |

The first implementation assignment should be slice 0 with a narrowly approved
slice-1 contract, not all five modes at once. See the matrix for executable future
acceptance obligations and the risk register for approval decisions. Stop this
mission at reviewable documentation; leave M015 open and all runtime files intact.

## 8. Hardened decision contract — proposed, approval required

### Rail policy comparison

| Policy | Gameplay coherence | Historical compatibility / determinism | Complexity / maintenance |
| --- | --- | --- | --- |
| A. Separate historical and adopted cohorts | Historical careers retain abstract rail; new mobility adopters use stations. Clear only if the cohort boundary is explicit. | Safe if cohort is recorded and graph/rules pinned; unsafe if inferred from save age, creation date or current engine default. | Two routing policies still required; an implicit cohort can become an irreversible permanent classification. |
| B. Keep legacy rail as a distinct active service alongside monorail | Offers more services, but a free neighborhood-boarded shortcut often defeats paid station access. Could be coherent only with an approved identity/rules contract for that service. | Preserves all current routes and can be deterministic with typed service IDs. No old-event rewriting needed. | Lowest initial masking work, highest continuing balance/UX burden; two overlapping abstractions need explanations and tests. |
| C. Replace abstract rail only after explicit adoption | Station requirements apply consistently to all adopters, including old careers; unadopted careers keep current play. | Dual-version history preserves old journeys; pinned adoption checkpoint and separate active graph prevent reinterpretation. Replay depends on recorded adoption, never save age. | Small explicit policy switch plus dual readers; avoids permanently duplicating a competing shortcut in new rules. |

**Recommend C.** It is the precise implementation contract for the cohort outcome
described loosely by A. New careers also remain v1 until explicit enrollment;
there is no automatic save-age cohort. B remains a possible user choice, but is
not the recommended pilot. Mask only `rail` mode entries under active rules2;
never remove mixed walk/bus edges or rewrite schema1 events. This is a proposed
policy change for consenting adopters, not an assertion that existing rail is
defective or that adoption has been approved.

| Decision | Recommended contract / unresolved approval |
| --- | --- |
| Rail/monorail | C; retain v1 execution/history, station-gate active rules2 and reject legacy `travel` as a rules2 bypass. |
| Pilot topology | p039 Highbridge Metro Stop to p071 South Gate Subway Stop, using the exact existing rail-corridor chain in section 9, two added platform nodes and one bidirectional line. Approve its fictional monorail service identity. |
| Fare | $2 per actual boarding, 1 TU setup; ride costs 6 TU, access/alight 0. No transfer discount, timetable or vehicle cargo in the pilot. Existing free bus/ferry unchanged. |
| Historical adoption | Paired nav2/mobility1, explicit pending request, one activation during the next valid navigation day phase, no grants. Both old and new careers use this path. |
| Vehicle authority | One tagged physical placement; title/use rights/security/knowledge separate; player position/TU remain navigation-owned. Empty inventory in the station pilot. |
| Search | Pilot needs only node/service context plus TU/cash labels; defer ground-vehicle dimensions until bike/car slices. Bounds: 64 transitions, two boardings, 8,192 expanded labels per outbound/return query, explicit limit result. |
| Performance | Complexity bounds are acceptance assertions; p95 100 ms/max 500 ms and save/load 2 s are unmeasured reference targets, not promised results. |
| Outstanding approval | Versions/forward rejection, C versus B, pilot identity/topology/closure bindings, $2 fare, command grammar and route bounds. Vehicle cargo, licensing and acquisition economics can wait until their own slices. |

**Verified conflicts and smallest seams:** [nav validation](../navigation.py#L29)
rejects nav2/schema2/overlay nodes and currently compares live location to the last
v1 event. Add version dispatch and validate a legacy boundary snapshot; do not
weaken v1 checks globally. [Search](../navigation.py#L172) forbids intermediate
POIs; permit only authored station gates, not all POIs. [Service](../game_service.py#L70)
requires exact string argument names; add small named commands rather than a
second transaction layer. [Daily navigation](../navigation.py#L283) resets TU
before life; capture the pre-reset boundary inside that phase. [Cash ledger](../daily_life.py#L53)
already observes command cash changes; fares debit `player.cash` once and never
invoke a second payment. [Career event validation](../career_state.py#L158)
already rejects duplicate player-command IDs; preserve that global check before
building per-domain dictionaries. None of these seams has been changed here.

## 9. First station pilot — atlas-backed proposal

**Verified:** p039 is public, parent n17; p071 is public, parent n30. Existing
walking approaches are `goon.edge.access.p039` and `goon.edge.access.p071`, each
bidirectional with cost 0. The following contiguous public, bidirectional rail
chain exists in the actual atlas; its nominal rail costs total 6:

| Order | Base corridor | Direction toward p071 | Rail TU |
| --- | --- | --- | ---: |
| 1 | `goon.edge.local.r03.05` | n17 → n18 | 1 |
| 2 | `goon.edge.e06` (Quay Tunnel) | n18 → n23 | 2 |
| 3 | `goon.edge.local.r04.04` | n23 → n22 (reverse definition) | 1 |
| 4 | `goon.edge.e08` (Civic Rail Tunnel) | n22 → n30 | 2 |

Executed **current-code** previews from p039 to p071 returned rail/auto 7 TU,
bus 8 TU and walk 18 TU. These are verified v1 results, not new pilot tests.
p022→p081 instead has current bus and rail costs both 9 TU; it is a less useful
first paid express comparison. No corridor, station label or base pin is edited.

**Proposed overlay** `goon.mobility.overlay.station_pilot.v1`, with sorted-ID
canonical records and a separately computed SHA-256:

Sort unordered node/line/transition collections by stable ID for the pin; retain
the explicit order of each ride's underlying segments and directions. Reordering
an authored set is harmless, but reordering a path changes its meaning and pin.

- Station IDs `goon.mobility.station.p039` and `goon.mobility.station.p071`
  reference existing POI frontages and inherit their public access. They are
  definitions, not additional player-position fields.
- Only new travel nodes are `goon.mobility.node.p039.platform` and
  `goon.mobility.node.p071.platform`. Authored bidirectional walking gates
  `goon.mobility.gate.p039` / `.p071` connect frontage to platform for 0 TU.
  A public traveler must still reach the actual frontage via permitted walking
  or compatible transit. Gates grant no institutional access or free rewards.
  Pilot command destinations are base places, not internal platforms; interruptions
  stop at frontages. Do not expose platform hops as independent reward-bearing trips.
- Line `goon.mobility.line.highbridge_south_gate.v1` has two service stops and
  one ride link `goon.mobility.ride.highbridge_south_gate.v1`, 6 TU each way.
  Its ordered underlying corridor references/directions are exactly the table
  above; reverse travel reverses every direction. Boarding is a station-specific
  self-transition, 1 TU/$2, and alighting is 0 TU. No intermediate boarding at
  n18/n23/n22 and no ride from a neighborhood. Departures are abstract immediate
  service, not real-time waiting or an hourly schedule.
- A full station-frontage journey costs **7 TU/$2**, round trip **14 TU/$4**,
  before any extra neighborhood approach. For nearby riders it buys 1 TU against
  the current free 8-TU bus path; cash-constrained riders may prefer bus. It is
  not claimed that every home-to-station itinerary fits 18 TU.

The existing rail chain proves adjacency, not that monorail equipment/service
already operates there. Quay/Civic tunnels and station types are retained as
geographic constraints. A new guided passenger service using that alignment is
an original proposed content configuration requiring approval, not an invented
direct cross-city shortcut or a claim about DC canon/engineering specifications.

### Closure, knowledge and recovery policy

The pilot ride is one atomic station-to-station transition. Inspect availability
of **all four underlying segments at departure**, before paid boarding. No
clock/random disruption is introduced midway through an atomic ride. Therefore
no player is deposited at an unmodeled intermediate platform. A later, multi-line
fixture may be interrupted before a subsequent boarding after a completed ride;
that is what P08 covers, not an invented intermediate pilot stop.

Explicitly pin a disruption binding from directed underlying `rail` closures to
the line direction that traverses them. A closure of bus/walk alone does not
silently close monorail. New service closures have line/direction/date/cause IDs;
preserve legacy closure records and old discovery references. This binding is a
new rules2 policy for future travel, not reinterpretation of an old journey.

Known disruptions exclude that departure in preview. Unknown disruptions do not
change public quote/token; at the station the operational departure check can
report line unavailability. Stop at the frontage before entering/charging the
blocked service. Record only an observed line-level disruption and its disclosed
reopening window, not an unexplained hidden segment/cause. Detailed underlying
truth stays in the debug/event audit boundary unless actually observed. The
knowledge record references the cause ID; it is not a duplicate physical closure.
As in current finite closures, reopening must occur within two advanced days.

If already at the departure frontage, discovery before boarding costs 0 TU/$0.
If approaching from another node, charge the actual safe prefix, including the
1-TU completed-movement floor for a zero-cost spur; never charge the unpaid
boarding/ride suffix. Repeating a now-known failed request rejects unchanged.
No denial/discovery reward is granted. Zero remaining TU cannot start discovery.

Return preview starts with outbound cash reduced by $2 and TU reduced by 7,
at p071, checking the reverse direction and current known state. Starting with
only $2 makes paid outbound affordable and paid return unaffordable; show the
free 8-TU bus return where available. At $0, the public station still permits
walking departure/free bus. With 7 TU remaining the 8-TU bus does not fit: disclose
safe save/explicit wait and its actual obligation consequences, then restore
only the normal next-day allowance. No purchased vehicle, debt, paid rescue or
automatic day transition is required. Closures of that fallback still require
a proven alternative or bounded reopening; graph connectivity alone is no proof.

Save after discovery or arrival persists exact node/TU/cash, pins, request receipt
and observed disruption. Reload is neither a ticket refund nor a new departure,
and does not activate pending adoption. See the concrete examples below and P15.

## 10. Concrete state and event proposal — not a production save

The following are JSON **excerpts/templates**, not complete careers. Prefix
events/fields are omitted explicitly. `EXAMPLE_...` strings are placeholders for
future canonical digests/tokens; a production validator must reject those as
content hashes. No proposed data is written into runtime fixtures or the atlas.

### Paired state, after the first schema2 pilot trip

Assume a valid legacy prefix through journey 7/command 98 at p039 on day 12,
mobility request command 99 that day, then wait command 100 to day 13. Journey 8
is command 101 to p071. No wages, vehicle or allowance was granted by adoption.

```json
{
  "save_version": 1,
  "command_sequence": 101,
  "action_day": 13,
  "actions_used": 0,
  "player": {"cash": 38, "arrested": false, "custody": "free"},
  "navigation_version": 2,
  "navigation": {
    "atlas_version": 1,
    "atlas_fingerprint": "14a38c5376989351d83bf90ed172c557a3dbf13c1323a115d2c2144f5136860a",
    "rules_version": 2,
    "enabled_day": 0,
    "activation_day": 1,
    "anchor_id": "goon.neighborhood.n17",
    "home_id": null,
    "location_id": "goon.poi.p071",
    "tu_day": 13,
    "tu_used": 7,
    "journey_sequence": 8,
    "permissions": [],
    "closures": []
  },
  "mobility_version": 1,
  "mobility": {
    "rules_version": 1,
    "overlay_id": "goon.mobility.overlay.station_pilot.v1",
    "overlay_version": 1,
    "overlay_fingerprint": "EXAMPLE_APPROVED_OVERLAY_SHA256",
    "adoption": {
      "status": "active",
      "request_id": "goon.request.adopt.99",
      "request_command_id": 99,
      "requested_day": 12,
      "scheduled_activation_day": 13,
      "activation_day": 13,
      "activation_command_id": 100,
      "legacy_checkpoint": {
        "last_journey_id": 7,
        "last_travel_command_id": 98,
        "location_id": "goon.poi.p039",
        "tu_day": 12,
        "tu_used": 3
      },
      "activation_budget": {"tu_day": 13, "tu_used": 0}
    },
    "assets": {},
    "access_tokens": {},
    "driver_authorizations": {},
    "restrictions": [],
    "disruptions": [],
    "knowledge": {"service_disruptions": [], "assets": {}},
    "receipts": {
      "goon.request.adopt.99": {"command_id": 99, "kind": "adoption", "payload_digest": "EXAMPLE_CANONICAL_ADOPTION_SHA256"},
      "goon.request.pilot.101": {
        "command_id": 101,
        "kind": "journey",
        "journey_id": 8,
        "payload_digest": "EXAMPLE_CANONICAL_REQUEST_SHA256",
        "charge_ids": ["goon.mobility.charge.8.board.1"]
      }
    }
  }
}
```

Pending state uses `status: pending`, null checkpoint/activation budget/activation
command/activation day, nav format2 but routing rules1. Required
`scheduled_activation_day` equals request day + 1; actual `activation_day` may be
later if old tools skipped whole-day phases, and must be at least the scheduled
day. The example is an ordinary next-day activation.
Neither inspection nor loading a stale day marker authorizes activation. Capture
the checkpoint inside nav day processing **before** its existing reset, then
record activation budget after that reset. This avoids comparing the legacy
last trip's spent 3 TU against a post-reset zero as if either were corrupt.

No legacy journeys means checkpoint journey/command IDs are null; validate its
location against the actual previous activation/home/anchor state. A checkpoint
never invents missing earlier events. Adopt once only; no unversioned mobility
state or active rules2 under nav1. Keep navigation's original enabled/activation
dates distinct from mobility adoption dates. Unsupported versions/pins fail.

`enable_mobility` requires already-active navigation and no current detention.
It emits one `mobility_requested` schema1 event with request/command IDs, overlay
pin, scheduled day and format1→2 transition, with no resource grant. Its receipt
binds the canonical request. That request has at most one `mobility_activated`
event, linked to the actual wait command. Activation can record the format/rules
transition while custody persists, but cannot move the player or enable travel
through detention; the normal legal/day pipeline remains authoritative.

### Future vehicle record (not part of the station pilot)

```json
{
  "instance_id": "goon.asset.17",
  "definition_id": "goon.vehicle.definition.bicycle.utility.v1",
  "owner_party_id": "goon.party.lender.1",
  "provenance": {"kind": "loan", "source_id": "goon.loan.4", "command_id": 120},
  "use_grants": [{"actor_id": "player", "source_id": "goon.loan.4", "from_day": 13, "through_day": 20, "permissions": ["retrieve", "ride", "park", "return"]}],
  "placement": {"kind": "stored", "node_id": "goon.poi.p031", "custodian_id": "player"},
  "security": {"locked": false, "required_access_token_id": null},
  "condition": 80
}
```

The player's known observation is stored separately by this instance ID with
last-seen node/day/source, never overwriting physical truth. Retrieval requires
permission to the storage place and asset, plus a key/token if locked; title
alone suffices for neither. `with_actor` replaces this placement with actor/role
only. Car definitions additionally require bounded fuel/capacity and driving
authorization; boards/bikes omit fuel. Receipt-derived indexes may speed lookup,
but cannot settle effects again or contradict their source events.

### Unchanged historical event envelope

This is a representative valid schema1 fragment in the assumed prefix, not an
event to backfill into an existing save. Its zero-cost spur still cost 1 TU.

```json
{
  "day": 12, "kind": "travel", "message": "Historical frontage arrival.",
  "schema_version": 1, "journey_id": 7, "command_id": 98,
  "origin": "goon.neighborhood.n17", "destination": "goon.poi.p039", "arrived": "goon.poi.p039",
  "tu_before": 2, "tu_cost": 1, "tu_after": 3, "interrupted": false,
  "mode": "walk",
  "legs": [{"edge_id": "goon.edge.access.p039", "from_id": "goon.neighborhood.n17", "to_id": "goon.poi.p039", "mode": "walk", "tu": 0}],
  "traversed": ["goon.edge.access.p039"], "discoveries": [], "cause": "player_travel"
}
```

Validate the complete schema1 prefix, including any rules1 trips while pending,
against base1 and the checkpoint. Validate activation/reset once, then schema2
in global journey-ID order; never apply platform/fare rules to this old event.
No schema1 trips may appear after active rules2. Preserve global uniqueness of
player-command IDs **before** building command dictionaries; domain events may
share their parent's ID, but two `player_command` envelopes may not.

### New command and outcome envelopes

Activation has its own once-only domain event inside wait100, not a fake journey
or fare. Its checkpoint/budget must equal the adoption state and the validated
legacy boundary; schedule and actual day are separate even when equal here.

```json
{
  "day": 13, "kind": "mobility_activated", "message": "Mobility activated after the normal day reset.",
  "schema_version": 1, "command_id": 100, "request_command_id": 99,
  "activation_id": "goon.mobility.adoption.99", "scheduled_activation_day": 13,
  "legacy_checkpoint": {"last_journey_id": 7, "last_travel_command_id": 98, "location_id": "goon.poi.p039", "tu_day": 12, "tu_used": 3},
  "activation_budget": {"tu_day": 13, "tu_used": 0},
  "cause": "explicit_mobility_adoption"
}
```

```json
{
  "day": 13, "kind": "player_command", "message": "Player command 101: journey.",
  "command": "journey", "command_id": 101, "actor": "player", "action_cost": 0,
  "arguments": {
    "destination": "goon.poi.p071", "profile": "monorail", "vehicle_id": "",
    "max_tu": "18", "max_cash": "4", "return_to": "goon.poi.p039",
    "quote_token": "EXAMPLE_PUBLIC_QUOTE", "request_id": "goon.request.pilot.101"
  },
  "cause": "player_command"
}
```

```json
{
  "day": 13, "kind": "travel", "message": "Arrived at South Gate frontage.",
  "schema_version": 2, "journey_id": 8, "command_id": 101,
  "request_id": "goon.request.pilot.101",
  "graph": {"atlas_version": 1, "atlas_fingerprint": "14a38c5376989351d83bf90ed172c557a3dbf13c1323a115d2c2144f5136860a", "overlay_id": "goon.mobility.overlay.station_pilot.v1", "overlay_version": 1, "overlay_fingerprint": "EXAMPLE_APPROVED_OVERLAY_SHA256", "routing_rules_version": 2},
  "origin": "goon.poi.p039", "destination": "goon.poi.p071", "arrived": "goon.poi.p071",
  "interrupted": false,
  "legs": [
    {"kind": "walk_gate", "transition_id": "goon.mobility.gate.p039", "from_id": "goon.poi.p039", "to_id": "goon.mobility.node.p039.platform", "tu": 0, "cash_cost": 0},
    {"kind": "board", "transition_id": "goon.mobility.board.p039.south", "from_id": "goon.mobility.node.p039.platform", "to_id": "goon.mobility.node.p039.platform", "line_id": "goon.mobility.line.highbridge_south_gate.v1", "tu": 1, "cash_cost": 2, "charge_id": "goon.mobility.charge.8.board.1"},
    {"kind": "ride", "transition_id": "goon.mobility.ride.highbridge_south_gate.v1", "from_id": "goon.mobility.node.p039.platform", "to_id": "goon.mobility.node.p071.platform", "line_id": "goon.mobility.line.highbridge_south_gate.v1", "tu": 6, "cash_cost": 0},
    {"kind": "alight", "transition_id": "goon.mobility.alight.p071", "from_id": "goon.mobility.node.p071.platform", "to_id": "goon.mobility.node.p071.platform", "tu": 0, "cash_cost": 0},
    {"kind": "walk_gate", "transition_id": "goon.mobility.gate.p071", "from_id": "goon.mobility.node.p071.platform", "to_id": "goon.poi.p071", "tu": 0, "cash_cost": 0}
  ],
  "resources": {"tu": {"day": 13, "before": 0, "cost": 7, "after": 7}, "cash": {"before": 40, "cost": 2, "after": 38}, "fuel": {}},
  "asset_changes": [], "discoveries": [], "cause": "player_journey"
}
```

The service currently emits domain events before the command envelope; readers
must join by identity, not demand the opposite list order. One boarding charge
is inside this outcome, not a second cash-reducer event. If life is enrolled its
existing balance observer adds a ledger projection of the same actual $2 debit.
For an unknown blocked departure already at p039, the schema2 outcome instead
has arrival p039, no performed legs/charges, TU and cash costs 0,
`interrupted: true`, and one service-disruption observation. It still consumes
one new command/journey/request identity; retry cannot charge or discover again.
An actual walking prefix appears in legs/resources if performed. A bare reject
has no envelope/receipt at all.

## 11. Atomic transaction and validation protocol — proposed

Pilot grammar is exact string fields as listed in section 13. `max_tu` is a
canonical decimal 0–18 and `max_cash` a canonical decimal 0–1,000,000; the spend
ceiling is still the smaller of the cap and current funds. Profiles are
`fastest`, `free`, `walk`, `bus`, `ferry`, `monorail`; active rules2 rejects
`rail`. IDs/request IDs are bounded to 128 characters and tokens to 64 hex
characters; request IDs use letters/digits/period/underscore/hyphen, never paths.
Resolve destination/return/overlay IDs against pinned definitions, not a supplied
filename. The pilot requires empty vehicle_id. Report actual leg modes even
when a requested policy ultimately selects walking only; do not label it a train
ride or charge fare without boarding. Base bus/ferry costs and switching rules
remain their existing rules; the new station exception must not change old v1
queries or open arbitrary POI transit shortcuts.

1. Validate exact command grammar/profile/caps and existing global IDs. Reject
   duplicate accepted request IDs even when payload differs; do not overwrite a
   receipt. Canonical request digest binds semantic fields, not a hidden-world
   hash. Quote tokens are known-state fingerprints, not security credentials.
2. On the existing private candidate, check custody, navigation activation,
   access, observed resources/rights, quote freshness and whole-outbound budget
   including safe parking reserve. Known failure discards candidate unchanged.
3. Execute typed transitions against truth only when legitimately observable.
   Check service departure before its paid boarding; record all actual walking,
   fares, fuel, selected-vehicle movement/retrieval/parking and observations.
   No RNG/time advance or unrelated day/economic phase runs here.
4. A hidden obstruction commits only a safe observed prefix, including zero-cost
   first-departure discovery if otherwise eligible. Roll back speculative suffix
   legs/resources/vehicle changes. It is a successful interrupted domain outcome,
   not an exception after a partial external mutation. Unexpected reducer errors
   discard the whole candidate, including already-computed prefix effects.
5. Construct one schema2 outcome and receipt, then the standard command envelope
   and detached response using the prospective sequence. Validate the candidate's
   touched mobility/resource/command invariants **before** replacing the caller
   root. This is an added future gate: current service does not call full world
   validation after every command. Do not add full-history work per search label.
6. Commit via the existing root replacement. No I/O, callbacks to external
   services or fallible effect processing after commit. A lost UI response does
   not authorize retry effects; receipt lookup recovers the committed result.
7. Saving remains a separate explicit operation. Failed save preserves last-good
   disk state/backup and current in-memory committed world; it does not undo a
   completed journey. Reloading an older successful checkpoint naturally resumes
   that checkpoint, not an invented cross-save global receipt database.

Reconstruct each resource delta from actual legs, with the completed-movement
floor, and link fuel/placement changes to one selected instance. Cash cost equals
actual boarding charges, fuel cannot go below zero, and parked assets do not
follow a player who travels by bus or is detained. Validate receipt/outcome/
command bijections, pin/version dispatch and checkpoint continuity once at load
and appropriate command boundaries. Indexes are checked projections, never a
second authoritative source of spendable cash or physical location.

## 12. Three consequential transport examples — proposed fixtures

| Player goal / available modes | Preferred choice and cost | What can go wrong / persistent consequence |
| --- | --- | --- |
| Reach nearby local work with only 1 TU left; walk, owned bike and car available at home. | Walk 1 TU/$0; bike setup+ride 2 and car setup+drive+park 3 do not fit. | A restricted destination or existing expired offer still rejects work. Arrival alone pays nothing; the actual subsequent choice spends its action and records work. Vehicle stays home. |
| Commute over a smooth medium route; walk6, carried board4, bike at hand3, car4 with fuel. | Bike 3 TU/$0 preserves time and cash for rent. | Parking/permission or condition may invalidate it; pushing is slower. Bike ends at work/in hand, altering the return and tomorrow's access. No random theft mechanic assumed. |
| Reach p071 from p039 with a commitment to return today; bus and pilot mono available, 14 TU/$4. | Mono7 each way/$2 per boarding fits exactly14; free bus8 each way would need16. | Unknown line closure can force free bus8, so preview is conditional. Fare cash/actual prefix and discovered service status persist; the player may choose to wait and accept a real day-window consequence. |

With at least16 TU and little money, bus wins the third example instead. No mode
is universally dominant. These choices spend resources or reposition assets to
preserve an opportunity; they award no transport XP or arrival bonus. Use one
door-to-door command and coarse optional maintenance, not repeated compulsory
unlock/refuel/repair/parking menus. Walking remains generally available on foot
edges and free transit bridges geographic gaps; 'universal' does not invent a
walkway through water or a restricted gate.

## 13. Smallest implementation-ready vertical slice — not executed

**Gate:** approve the station-pilot decisions in section 8 first. Keep assets
empty and every career default v1. Compatibility work is part of this same small
deliverable; do not first build a general fleet, crime or schedule framework.

| Exact intended file | Bounded future change |
| --- | --- |
| `content/mobility_station_pilot_v1.json` (new) | Two platforms/gates, typed boarding/alighting, one 6-TU ride backed by the four exact base corridors, $2 fare, closure binding and canonical pin. No atlas edit. |
| `mobility_content.py` (new) | Local detached overlay loader, sorted-ID fingerprint and topology/access/cost/underlay validation; immutable cache only. |
| `mobility.py` (new) | Pending adoption, narrow walking/service preview and journey reducer, knowledge/receipt handling; no vehicle gameplay. |
| `mobility_state.py` (new) | Paired nav2/mobility1 invariants, checkpoint/version dispatch, schema2 resource/history/receipt validation. Empty asset schema may be reserved but cannot grant use. |
| `navigation.py` | Keep v1 implementations/costs unchanged; delegate nav2 validation/views and capture pre-reset checkpoint/activate once inside existing begin-day seam. No new daily pipeline. |
| `career_state.py` (verify/reuse) | No behavior change required: existing navigation-validation hook reaches the version dispatcher; retain global duplicate player-command-ID checks before domain indexes. |
| `game_service.py` | Register exact `enable_mobility(overlay_id, request_id)` and `journey(destination, profile, vehicle_id, max_tu, max_cash, return_to, quote_token, request_id)` string fields; guarded candidate validation; detached mobility views. Pilot rejects nonempty vehicle IDs. |
| `gameplay.py` | Thin CLI commands/preview/receipt presentation; dispatch to service. Do not edit next-day phase ordering or old jobs. |
| `tests/test_mobility_pilot.py` (new) | Pilot topology/cost, station-only entry, bus fallback, known/unknown closures, read isolation, equal-rank/order and bounded search tests. |
| `tests/test_mobility_compatibility.py` (new) | Mixed-version/checkpoint, pending/active resume, old-reader rejection, request/global-ID collisions, failed-save and legal/life equivalence tests. Generate schema2 fixtures only after schema approval. |
| `README.md`, `PROJECT_STATE.md`, these three documents | Mark actual commands/versions/results and limitations only after implementation/testing. No such production documentation change in Mission 012. |

`career_state.py`, `location_registry.py`, `career_persistence.py`, `daily_life.py`, existing atlas
and all existing tests need no behavior changes in this slice. Reuse their seams;
if implementation proves otherwise, explain the bounded deviation before adding
scope. Intended new test methods include `test_legacy_prefix_survives_adoption`,
`test_pending_travel_checkpoint_precedes_single_reset`,
`test_duplicate_player_command_id_across_schemas_rejects`,
`test_station_pilot_underlay_chain_and_7tu_2dollar_fare`,
`test_hidden_line_closure_commits_only_actual_approach`,
`test_remote_station_zero_cash_bus_recovery`,
`test_projected_return_uses_remaining_cash_and_tu`,
`test_retry_after_interrupted_resume_cannot_settle_twice`,
`test_quote_reference_isolation_and_hashseed_parity`, and
`test_failed_save_preserves_previous_mobility_checkpoint`.
These names are a work contract, not files/tests created or executed now.

## 14. M016-A executable contract — Mission 013

Implemented: paired nav2/mobility1, one explicit pending adoption, activation in
the existing service-wait/nav-reset phase, station-only pilot, typed journeys,
atomic fares/TU, known-state quotes, projected return and safe closure prefixes.
No vehicle, acquisition, theft, license, impound, timetable or NPC scheduling
system is implemented. Default new careers stay nav1; historical loading never
opts in. Existing modules/atlas/save outer version are retained.

### Actual ownership, versions and history

- [Overlay](../content/mobility_station_pilot_v1.json), loaded/validated by
  [mobility_content](../mobility_content.py), pins the unchanged base atlas.
  Its fingerprint is `d59fe323290fd1216d8b5e1ffdcde5924b123cedc0404ce22215d538779ec7ee`.
  Sorted station records are canonicalized; ordered corridor references are not
  reordered. Public loaders return copies; only immutable definitions are cached.
- [Mobility reducers/views](../mobility.py) own enrollment, request receipts,
  observed line status and quotes. Navigation still owns one live player
  location, TU and journey sequence. Reserved vehicle-related collections must
  be empty; unsupported nonempty vehicle state fails rather than being discarded.
- `enable_mobility(overlay_id, request_id)` requires active navigation and free
  custody. It records one `mobility_requested` schema1 event, nav format2 but
  routing rules1, and the pinned optional mobility1 extension. It grants nothing.
  Repeated enrollment rejects for either the same or a different request ID.
- The next service `wait` captures the legacy checkpoint before navigation's
  existing reset, then records one `mobility_activated` schema1 event after it,
  before life processing. A small scoped command context carries the wait ID;
  there is no temporary persistent world field or independent day pipeline.
  Reads, loads and low-level clock-only reducers do not activate pending mobility.
- [Validation](../mobility_state.py) runs the unchanged v1 validator on a
  checkpoint projection and original schema1 events, then checks schema2 legs,
  resource/receipt identities, command bijections and current continuity.
  Schema1 journeys after activation, missing paired state, stale pins, duplicate
  global command IDs and forged fare/TU/placement are rejected. Historical event
  values are never rewritten. Old binaries clearly reject nav2.
- Empty legacy histories preserve the location/budget accepted by v1 and bind
  the checkpoint to its activation event. They are not reconstructed from the
  current home: M015 can legitimately grant a home later without moving the
  player. This corrects section 10's provisional home/anchor inference, while
  retaining v1 compatibility and no migration grant.

### Pilot, quotes and execution

Actual topology and price are section 9's p039/p071 four-corridor alignment:
zero-TU gates/alight, 1-TU/$2 boarding, 6-TU ride. Internal platforms appear in
typed legs, not selectable persistent destinations. The complete frontage
journey is **7 TU/$2**; walking-only home→p039 approach is 4 TU, hence home→p071
under explicit monorail profile is 11 TU, not 7 or 10. A separate free bus
approach to p039 costs 3; inter-station bus costs 8/$0. No approach is double billed.

The CLI reuses `route`/`travel` and adds `mobility`, `adopt_mobility`, `receipt`.
`auto` maps to `fastest`. The service uses the exact eight journey string fields
in section 13; nonempty vehicle_id is rejected. All mutations use its private
candidate. Full candidate validation occurs before root replacement for opted-in
careers. There is no second economic ledger: fare reduces `player.cash` once,
and an enrolled life ledger observes that real balance change.

API quote return target defaults to **origin**, matching existing `route` CLI
semantics; explicit `return_to` selects home/another known place. This is a small
presentation clarification from the earlier proposed home default, not a rail
policy change. Outbound caps bound that transaction only; return feasibility
uses actual remaining cash/TU. The quote separately reports policy return,
free return and whether any shown return fits. Unknown future disruptions are
always possible, never inferred from hidden world data.

Search uses stable ranked labels with TU/cash/mode/boarding context, at most two
boardings, 64 typed legs and 8,192 expanded labels per search. Mandatory-monorail
queries retain visited-node signatures to prevent paid circuits around closed
departures; walking/free queries do not acquire vehicle dimensions. Limits raise
an explicit error with simpler-profile/waypoint recovery, not a fabricated
physical-disconnection claim. Known line outages omit boarding; an unknown
outage is discovered at the departure frontage before any paid gate/ride bundle.
Only performed approach legs/floor are charged. Underlying private cause IDs
remain out of public reports and quote tokens. Base bus/ferry closure discovery
retains its ordinary safe-prefix behavior. No new disruption generator exists.

Retries of accepted request IDs reject unchanged; a detached receipt recovers
the old result. Failed saves preserve previous disk state/backup and committed
memory; they do not roll back a completed journey. File publication remains the
existing persistence implementation. Tests include the frozen M015 fixture
generated by baseline code, historical rail/pending history, later housing
adoption, interruptions/resume, corruption and I/O failures. Exact results and
remaining performance/gameplay limits are in the report; proposed vehicle and
1,000-day/full-matrix gates remain future work.
