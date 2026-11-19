# M014 world runtime and navigation contract

The runtime loads [version-1 local content](../content/gotham_atlas_v1.json),
converted from the [place registry](GOON_LOCATION_REGISTRY.md) and
[travel specification](GOON_TRAVEL_NETWORK.md). All 176 place records retain
their stable IDs, names, parent chains, profile codes and source designations.
The 63 neighborhood corridors and 120 physical POI spurs preserve their
documented topology, modes and costs. Metadata is not a simulated salary,
police probability, NPC spawn, property deed or admission permission.

## Initial time policy and useful choices

M014 selects **18 travel TU per day**, separate from three gameplay actions.
Street/crossing costs are from the atlas; entering bus, rail or ferry adds one
TU. Each command starts off board. Cars/boats remain definition metadata only:
no vehicle ownership, pickup, fare, timetable or fuel system is implemented.

One deliberate change to the M013.1 hypothesis: a successful move costs at least
**1 TU**, even when its POI approach spurs sum to zero. This bounds local
home/store shuttling to eighteen journeys, without changing physical spur costs
or charging a daily gameplay action. Inspections are free. Same-location travel
is rejected. No movement pays money, XP or relationships; no report/load refreshes
TU. A real `wait` runs the entire existing city day, then resets TU after court.
Legacy low-level batch tools can retain an older TU-day marker; loading preserves
that marker and spent budget until the next genuine day transition.

The home/store/return loop costs 2 TU. From the n13 public hub, bus travel to n31
costs 6 each way; with e06 bus closure it costs 8 each way. n01 to n40 costs 19
one way and is rejected even with a full allowance. A nearer explicit waypoint
is possible; no automatic overnight leg or compulsory distant campaign chain.
Route views show outbound/return costs, affordability and whether both fit today.
An unavailable return is explicit. Eighteen TU remains an initial tuning choice,
not proof that all future work/care schedules fit.

Meaningful current decisions are destination, route mode, daily travel budget,
return commitment and choosing local work instead of an unaffordable trip.
Position, spent TU, journeys and discovered closures persist. Existing jobs may
be attempted from the slice through their unchanged service commands; their
rewards/risks are not reinterpreted as local wages. Travel neither creates an
extra faction account nor changes current three-district missions.

## Location and access scope

New careers begin at East Side Housing Cooperative, p031/n13, with a declared
home-entry entitlement and the existing $40/cash, affiliation and relationship
defaults. This supplies a valid starting room, not ownership, rent simulation,
employment, invented past events or a completed prologue. `home` resolves only
when such a recorded home exists.

Neighborhoods represent safe arrival hubs. POIs represent the documented public
frontage/reception; they never imply a ward, cell, staff room or private residence
interior. PUB/HELP public access, ENT customer frontage and CARE request/intake
frontage are available in this unscheduled slice, with no ticket purchase or
treatment effect. HOME/WORK/VIS/SEC require explicit place permission. Permission
can be stored by a later authorized domain; there is no player cheat command to
grant it. Blackgate n46 requires its own receiving authorization. A valid visit
does not admit the player to prison or authorize a different POI. Normal outward
departure remains possible after entry permission is revoked. Detained players
cannot travel; existing legal responses/automatic court handling retain authority.

The known public atlas is immediately usable; other private residences are omitted
unless permission is recorded. This is a small public-knowledge model, not rumors,
NPC tracking or secret entrances. Reports are detached. The generic full snapshot
is still authoritative/debug state; a future GUI must use the restricted location
views for navigation. Locations do not spawn villains or reveal treatment records.

## Deterministic routes and bounded disruption

Standard-library Dijkstra ranks total integer cost, mode changes, edge-ID sequence,
then mode sequence as the final tie-break. Only walking/public transit participates.
Containment edges never route; zero-cost POI spurs are used only at the journey's
endpoints, preventing free intermediate shortcuts/cycles. Regions are containers,
not movement destinations. One-way definitions and mode/direction closures are
honored; current atlas physical corridors are all bidirectional.

`route` is advisory, from current known conditions; `travel` plans again and
validates on the service's private candidate world at commitment. It does not
hold/resume an old quote or animate an uncommitted journey. Known unaffordable,
restricted, no-path or same-location requests reject the entire command unchanged.
There is no asynchronous world writer or route-preview mutation.

Closures have a causal ID, edge/mode/direction, start/end day and player-known flag.
M014 permits corridor closures only and guarantees reopening after at most **two
advanced days**. There are no random closures, indefinite extensions or closure
editing CLI. These are a validated runtime input for future approved incidents,
exercised with controlled test fixtures. POI spurs cannot close in this slice.
At every arrival, free inspection/help, saving and explicit waiting remain usable,
even with no cash/actions/TU. Existing work remains location-independent. This
bounded input contract avoids permanent transport isolation without inventing
emergency healing, paid rescue, forced relocation or institutional release.

An unobserved closure is omitted from previews. Discovering it is a successful
domain outcome: stop before the blocked edge at the last safe node, charge only
the traversed prefix (minimum 1 TU if actually moved), mark the closure known,
and emit one structured travel event. With no movement the discovery costs zero;
that cannot yield free movement/rewards or repeat the same hidden discovery.
No suffix is charged. A saved interrupted result is a committed location, never
a character stranded mid-bridge. Replanning respects the newly known closure.

## Persistence and command boundary

New careers add `navigation_version: 1` and `navigation`. The extension pins
atlas version, SHA-256 content fingerprint and rules version, home/location,
explicit historical anchor/adoption dates, TU day/usage, permissions, journey
sequence and closure observations. Unsupported versions, changed/missing pinned
content, malformed hierarchy/references, illegal costs and unbounded closures
fail clearly before gameplay. Existing outer save identifiers/version stay intact;
atomic saves and recoverable backups use the existing persistence path.

Historical M001–M013.1 careers acquire no navigation state on load. Explicit
`enable_navigation n13` chooses a public anchor and schedules next-day activation;
no home/admission/history, income, job attempt, spent action or RNG draw is invented.
Save/load while pending does not activate it. Adoption is unavailable in custody
and cannot be repeated. The post-court day phase owns activation/reset once.

All player mutation uses `game_service.execute_command`. Commands are
`travel(destination=<string>, mode=<string>)` and
`enable_navigation(anchor=<string>)`, each zero gameplay actions. Travel cost
uses TU. `location_report`, `nearby_destinations`, `known_places`, `plan_route`
and `snapshot` return detached reads. Movement emits a schema-versioned travel
event with journey/command identity, endpoints, cost before/after, traversed edges
and discovery IDs. Reports and legacy simulation RNG are untouched.

## Manual playable slice and limits

Run `python gameplay.py --seed 42 --save career_m014_review_save.json` with a
fresh filename. Enter `look`, `nearby`, `route p032`, `travel p032`, `look`,
`join 1`, `job courier`, `travel home`, `wait`, `save`, `quit`. Resume with
`python gameplay.py --load --save career_m014_review_save.json`, then `look`.
The store visit and home return cost 2 TU; the job costs one gameplay action;
waiting advances the city once and refreshes both allowances. Location remains
p031 after resume. Regression tests execute this slice with temporary save files.

Travel is mechanically shallow while destinations mainly supply profiles and
frontages. There are no shop purchases, housing bills, care sessions, NPC schedules,
new local missions, combat or playable prologue. Larger routes vary by mode,
permissions and known disruptions; they do not yet offer authored encounter variety.
Repeated commute/wait clicks remain a design risk. Future work must add actual
obligations and consequences rather than rewards for moving or marker collection.

## Future third-person world seam — proposal, not M014 runtime behavior

The owner selected third-person open-world presentation on 2026-11-07. **No 3D coordinates, continuous walking controller, Godot client, real-time NPC movement or gameplay clock is implemented in this M014 contract.** The proposal is documented in [One Living Block](GOON_THIRD_PERSON_VERTICAL_SLICE.md). The existing 176-place atlas, route budgets and authoritative travel API remain unchanged.

A future Godot environment would map a physically explorable block and interiors to **explicit inspected canonical location IDs**. Free local locomotion/inspection inside an authorized area must not consume gameplay actions or create route events. A transition across canonical location boundaries must obtain and commit a versioned Python-authorized travel/entry outcome, or remain explicitly prototype-only and not claim a changed canonical position. Movement animations cannot advance a day, call `wait`, reroll a route, reveal a hidden closure or rewrite saved history. Continuous time or persisted coordinates would need a separate backwards-compatible contract and tests.

Existing React browser-host security is not a generic Godot IPC contract. Any Godot communication must be separately threat-modeled and preserve strict identity, player-safe projections, one authority for mutation, exact request recovery, deterministic replay and explicit historical-save adoption. Keep M014 budgets of three actions and 18 TU per day; do not reinterpret them as steps, animation frames or button presses.
