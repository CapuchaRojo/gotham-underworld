# Gotham: The Goon — Map and Simulation Integration

**M013.1 migration design source.** [M014's runtime contract](GOON_WORLD_RUNTIME.md)
implements explicit historical adoption/next-day activation and a pinned optional
navigation extension, retaining the three territory accounts. Broader economic
repartition remains deferred. The sequence below retains M013.1's original proposal;
the runtime contract governs the implemented subset. The [atlas](GOON_GOTHAM_ATLAS.md)
and [location registry](GOON_LOCATION_REGISTRY.md) describe geography; they are
not new economic districts. [Travel](GOON_TRAVEL_NETWORK.md) and
[visual layers](GOON_MAP_VISUAL_SPEC.md) depend on this separation.

## Verified current model

[`city_economy.py`](../city_economy.py) defines three default districts with a
single owner, wealth and control. [`faction_profiles.py`](../faction_profiles.py)
and [`faction_competition.py`](../faction_competition.py) use holdings, funded
income/upkeep, recovery and operations. Daily markers prevent duplicate phases.
[`territory.py`](../territory.py) changes ownership only for an exhausted-control
district and a different known faction, resetting control to 35.

[`district_missions.py`](../district_missions.py) targets those same district
keys, uses sorted numbering, records district intelligence and permits one district
mission daily. [`game_service.py`](../game_service.py) enforces three shared daily
actions and atomic candidate-world commands; its current arguments are named
strings. [`career_state.py`](../career_state.py) validates owner/target references,
phase markers and historical state. Reports and future interfaces must still use
detached read models, not mutate the world to prepare a map.

The default labels and values below are initialization constants, not a claim
that an existing save still has those owners/resources after play:

| Preserved legacy key | Initial owner / wealth / control | Proposed optional geographic display footprint |
| --- | --- | --- |
| `Harbor Docks` | Harbor Syndicate / 60 / 65 | East Harbor n31 and Drydock Ward n33, R06 |
| `Carnival Row` | Carnival Crew / 45 / 65 | Amusement Mile n15, R03 |
| `Ironworks` | Iron Mask Outfit / 50 / 65 | Iron Quay n32, R06 |

These footprints are original adaptation proposals, not established DC geography
or mappings of Carnival to Joker / Iron Mask to Black Mask. Actual saved values
and faction identities always win over the initialization table.

## Separate layers and authorities

| Concept | Proposed identity / authority | Explicit non-equivalence |
| --- | --- | --- |
| Geographic neighborhood | Stable location ID, parent region, access/services and condition overlays | Not a capturable income unit merely because it has a name |
| Faction territory | A separately identified economic/control area with a versioned footprint and exactly one authoritative controller under its rules | Not legal ownership of all buildings or universal loyalty of residents |
| Minor-crew influence | Directed contacts, access, promises and incident effects with provenance | Not full faction power/treasury, capture, police authority or daily income |
| Individual property | Legal/contractual owner, tenancy, permitted use and explicit finances if later approved | Not the district's political controller; a tenant is not an asset |
| Building / interior | Parent property/place, entrances and specific permissions | A public map pin is not permission to enter a ward, home or safehouse |
| Police jurisdiction | Agency/service boundaries and explicit incident responsibility | Not player heat, faction borders, a guaranteed patrol or automatic guilt |
| Mission location | Particular place/entrance/participants, accepted terms and outcome IDs | Not a requirement to own the location or change territory on completion |
| Actor presence / knowledge | Actual availability separately from what each observer knows | A rumor, roster entry or known address does not spawn a villain |

The existing district dictionary requires valid known faction owners. Do not
stuff `null`, “unclaimed” or “contested” into it and assume validation supports
those values. Unmapped geography can have no *territory-area binding* in the
future geographic layer, without altering the legacy owner's schema. Police and
care facilities, parks, homes and businesses need no major-faction assignment.

## Safe incremental strategy

### 1. Static definitions and read-only reference view

When separately authorized, introduce a small local definition loader with unique
IDs, parent/reference validation and pinned content/continuity metadata. Geography
can be browsed as a labeled planning reference without inventing the player's
current location or revealing hidden campaign facts. Never call mutable preparation
reducers from a report. Current M013 remains fully playable without opting in.

No implementation or new data file is added now; the current Markdown registry
is a specification, not a silently loaded content pack.

### 2. Preserve three authoritative territory accounts

Retain `Harbor Docks`, `Carnival Row` and `Ironworks` and all saved owner/wealth/
control, cash, action usage, intelligence, plans, case sources, relationships,
RNG counters and daily markers. A proposed adapter can bind them to separate
stable area IDs such as `legacy.territory.harbor_docks`, with a geographic footprint
for display. Historical events retain their exact district strings and order.

The area, not each covered neighborhood/POI, receives the existing economic tick
once. A shared capture changes that area's controller once, then read models
derive the footprint overlay. Do not apply control deltas independently to every
rendered polygon or create a second hidden owner. Mission selection can resolve
an area ID to the legacy key until a later explicit territory migration.

### 3. Versioned, explicit travel opt-in

Propose an independently versioned geography/travel extension only in its approved
milestone. Validate pinned definitions, actual versus known state, location and
permissions, TU counters, route outcomes and references before play. Unsupported
versions/required missing definitions fail clearly; never reset an existing career
or silently substitute a new neighborhood. Unknown legacy history remains unknown.

An old save has no proved physical location. Do not infer a home or historical
journey from a faction name or warehouse memory. Offer an explicit safe public
anchor selection when enabling geography, record that adaptation choice and
schedule activation on the next normal day transition. Until activation, legacy
commands keep their previous behavior and geography imposes no location gate.
If custody/episode state prevents a valid anchor, defer activation instead of
inventing admission, release or an escape.

Loading and opting in cannot replay income, relocate known actors, refresh the
three actions or grant travel twice. The proposed 18 TU first becomes usable at
the scheduled activation transition; subsequent resets occur only with ordinary
`wait`. A later implementation must specify the activation phase after existing
court resolution and before the service returns refreshed allowances, preserving
the established daily sequence and once-per-day markers. That phase is not added now.

For a future new career using the new rules from creation, choose a declared
starting public anchor and the initial allowance explicitly. Keep old-rule saves
on their pinned contract unless the player chooses a reviewed upgrade. Save/load
mid-journey only at committed safe-node outcomes; no UI animation writes state.

### 4. Expand activity before expanding territory

Add approved places, employers, minor crews and finite missions as content. They
can use geography and travel without requiring 48 warfare/economy turns. Separate
actual demand, known opportunities and local conditions. Original geography never
forces a district owner, a named rogue, police evidence or an institutional entry.

Current jobs have no physical location prerequisite. Do not globally gate all old
jobs to a new POI, alter old risk draws or charge retroactive commute time. A later
career-aware job definition can opt into explicit locations/commute terms while
the legacy resolver and tests retain their original contract.

### 5. Only later repartition economic territory

A separate approved balance/migration milestone may replace or split the three
accounts. It must define conservation/redistribution of saved resources, footprint
overlap, area-level control, paid attack targets and source-compatible mission
events. Integer income rounding, holding upkeep and treasury caps mean splitting
one wealth number across many areas does **not** automatically preserve behavior.

Require a documented before/after resource audit and new long campaigns before
activation. New geography gets no free wealth or prior-day income. Never copy
60/45/50 wealth into every child neighborhood. Preserve provenance of historical
transfers and old references through an adapter rather than rewriting old events.
No map-driven repartition, profile rebalance or elimination rule is approved here.

## Conditions and deterministic city processing

Neighborhood condition overlays can later record a service closure, flood damage,
employment demand, repair stage or sourced alert with bounded values, causal IDs
and review/end conditions. They do not mutate immutable geography definitions.
One department owns each effect: transport closes an edge, a property manages its
approved terms, legal rules own cases, and territory uses the shared capture path.
The same incident cannot pay compensation or apply control once per view/layer.

Every new phase needs an explicit position, marker and canonical ID ordering.
Keep legacy job/feud random streams intact; use isolated domain seeds only for
new approved stochastic rules. Reports, previews, inactive neighborhoods and
cosmetic map labels consume no RNG. No simulation step relies on dictionary order,
wall clock, Python `hash` or the length of an event log.

Future GUI/narrative adapters issue serial game-service commands, show detached
snapshots and use existing persistence/backup publication. No graph library,
GIS dependency, network map API, online geocoder, database or framework is needed.
Licensed labels/landmarks stay in local versioned content, outside core rules.

## Ten-field review and required future checks

| Criterion | Integration contract |
| --- | --- |
| Decision | Keep an old contract or explicitly adopt geography; select work/location commitments |
| Feedback | Show pinned rules, adaptation anchor, activation day, actual territory account and known footprint |
| Persistence | Optional versioned geography/travel state and area bindings, preserving old records |
| Alternatives | Legacy play, geography without new territories, independent/minor-crew or civilian activity |
| Replayability | Conditions, contacts and missions change while stable place identity remains |
| Grind risk | Inflated income/warfare ticks and location-gating old jobs; expand activity before mandatory commuting/territory |
| Determinism | Ordered adapters/phases, no replay on load, unique incident/transfer effects and isolated RNG |
| Save compatibility | Historical keys/events/resources/markers preserved; explicit unsupported-version failure and opt-in activation |
| Offline | Self-contained approved definitions and current standard-library service/persistence |
| Agency / exploits | No false home/admission, duplicated wealth, forced faction control, hidden upgrade or reset allowance |

Before implementation, test every historical fixture; byte-equivalent legacy
behavior while geography is off; preserved cash/power/wealth/control/events on
load; no double account from a multi-neighborhood footprint; existing mission IDs;
failed migration/save rollback; unknown fields; unsupported versions; sparse
territory coverage; no-owner geographic nodes; missing definitions; custody-safe
activation; repeated loads/waits; explicit origin selection; detached reports;
and fresh-process deterministic replay/resume. A later economic repartition needs
its own four-seed/year and long-campaign audits. These are future criteria, not
executed migration claims for a feature that this milestone does not implement.
