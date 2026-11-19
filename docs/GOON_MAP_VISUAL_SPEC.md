# Gotham: The Goon — Future Layered Map Interface

**Status: written interface specification only.** No GUI, wireframe image, rendered
map, frontend dependency or licensed map asset is created. This defines how a
future interface could consume the existing service safely. Refer to the
[atlas](GOON_GOTHAM_ATLAS.md), [registry](GOON_LOCATION_REGISTRY.md),
[travel proposal](GOON_TRAVEL_NETWORK.md) and
[integration contract](GOON_MAP_SIMULATION_INTEGRATION.md).

## View hierarchy and player decisions

| View | Information shown from the permitted read model | Useful decision / next view |
| --- | --- | --- |
| City overview | Known regions, public transport backbone, current location if established, observed incidents and action/TU allowances | Choose a region, nearby work, care or a saved contact; no teleport on selection |
| Region selection | Known neighborhood names, broad services, sparse territory bindings and source/uncertainty legend | Compare different obligations or services; inspect a neighborhood |
| Neighborhood inspection | Known POIs, available public services, sourced conditions, relevant contacts and work | Select a useful destination, verify a claim or stay local |
| POI detail | Public description, known entry requirements, actual offered terms versus claims, opening/closure information and contact confidence | Visit the public frontage, request an eligible service, plan a route or decline |
| Route planning | Modes, quoted TU, remaining three actions, permissions, known disruptions, uncertainty and return feasibility | Commit a permitted journey, choose another route or change the day's commitments |

A POI description is not its building interior. Selecting Arkham's reception does
not admit the player, grant ward access or reveal Joker. Selecting a private home
does not enter it. Opportunity acceptance, consent, travel and mission resolution
are distinct service commands under later contracts. The user need not inspect
technical IDs or save-version details to make an ordinary decision.

The atlas is schematic and not to scale. A future renderer should use original
vector/layout definitions and local authored symbols, with costs from the graph,
never pixel distances. No copied shoreline, traced licensed map, ripped game tile
or externally hosted map is a prerequisite. The current milestone contains no
such renderer or vector asset.

## Layer definitions

| Layer | Proposed display and filter | Knowledge / authority rule |
| --- | --- | --- |
| Public geography | City, region and neighborhood hierarchy with readable labels | Approved public names can be initially known; no implied ownership or private access |
| POIs | Service-type symbols, selected filters and public entrances | Unknown/private entrances stay absent; a public building's secret interior is not inferred |
| Routes / modes | Candidate routes, transfers, TU and explicit restricted segments | Use player-known graph, mark stale/uncertain links, revalidate on commitment |
| Faction territory | Known controller of an actual economic area and its footprint | No fill implying all places are owned; areas without a binding remain unassigned |
| Minor-crew influence | Specific known contacts, work and local claims, visually distinct from territorial fill | A rumor or contract is not control, income or full faction membership |
| Police activity / jurisdiction | Known service jurisdictions, observed activity and alerts | Personal M012 heat is a separate player badge; no hidden case or patrol location leak |
| Known NPC contacts | Last known place/region, source, observation day and contact method | Roster presence is not exact live tracking; unavailable actors are not spawned by a pin |
| Available work | Known eligible offers with terms, expiry and commute preview | No guarantee of selection, invitation or named employer; refresh cannot reroll |
| Rumors / uncertain information | Claim, source, observation age and uncertainty markers | A claim can be false; never recolor the true-world layer as if it were verified |
| Incident alerts | Known disruption, affected services and review/end information | Hidden incidents remain hidden until an approved discovery; alerts do not tick time |
| Housing / safehouses | Player-known lawful access, tenancy/consent and disclosed safety limits | A saved address is not ownership, faction immunity or knowledge of every resident |
| Civilian services | Clinics, voluntary care, shelter/referrals, shops, work, education and social venues | Support remains easy to find; treatment or public consultation is not criminal guilt |
| Neighborhood conditions | Known service availability, repair state or environmental concerns | Bounded observed effects with provenance; no ethnicity/poverty-to-crime score |

Filters compose without turning one layer into another's authority. A clinic may
sit inside a faction's known footprint while its property/consent and medical
confidentiality remain independent. A minor crew can be active at an unassigned
market. Police jurisdiction is not a painted heat value for each neighborhood.

## Facts, observations, claims and public information

The engine owns authoritative geography, permissions, actual actor presence and
incidents. A future player-knowledge model separately records known public data,
observations and sourced claims. Rendering receives a detached, appropriately
filtered view; it never uses arbitrary hidden state then merely hides a label.

| Example | Actual fact | Player-visible representation |
| --- | --- | --- |
| Unobserved bridge closure | Edge is currently closed | Last observed status plus uncertainty; preview cannot reveal the secret closure |
| Known ferry suspension | A sourced notice/discovery is recorded | Closed mode, observation day and known review/alternate route |
| Rumored rogue sighting | Actor may be somewhere else or unavailable | Sourced rumor at its known granularity, never an authoritative live marker |
| Claimed safehouse | Someone claims an address is safe | Claim and confidence; consent/security remain unverified until an actual outcome |
| Private treatment | Care episode and permissions exist | Only information the player is entitled to know; another person's records are not an employer filter |
| Unsurveyed territory | Controller unknown to the player | Unknown/unassigned knowledge symbol, not the true owner read from the full dashboard |

Default public transit knowledge can make navigation usable without omniscience.
Do not require repetitive scouting for every ordinary street. Confidence labels
describe the source/observation, not an infallible probability shown by the engine.
Contradictions should be inspectable without overwriting either the claim or truth.

Current [`city_intelligence.py`](../city_intelligence.py) reports actual world
state. It is **not** already this restricted knowledge model. A later map must
introduce a deliberate read adapter; relabeling an omniscient report “rumor” is
insufficient. A developer/debug full-state view must be explicit and separate
from the ordinary campaign UI. No new adapter is implemented now.

## Service interaction and accessibility

Keep one serial owner of the world. Views request detached snapshots/read models;
player choices call the existing game service and render its detached result and
structured events. A map pan, hover, filter, preview or animation neither advances
days nor initializes state, rolls outcomes, spends TU or edits knowledge. Save/
resume uses the same validated atomic persistence API as the CLI.

On a known-invalid route, show an actionable reason without mutation. A valid
attempt that discovers an unknown blockage can commit a safe-prefix arrival and
knowledge event, as specified by travel. Do not replay it when an animation ends.
Revision mismatches require re-preview or a clearly explained domain outcome,
not accidental partial costs or disclosure of an actor's hidden location.

Provide keyboard navigation, a text list equivalent to every map choice, scalable
labels, symbols/patterns in addition to color, and explicit focus/order by stable
data. Distinguish observed, reported, stale, unknown and restricted with text as
well as style. Do not stack 120 unreadable markers at city overview; aggregate by
neighborhood and expand on request without losing access to the text list.

Use neutral locally authored icons/categories until assets receive independent
approval. “Crime,” “danger,” “care,” faction control and player heat must not share
one ambiguous red overlay. Accessibility options change presentation, never RNG,
cost or the information available to the player.

## Ten-field review and future checks

| Criterion | Map-interface contract |
| --- | --- |
| Decisions | Compare work, care, contacts, route and return costs; choose or decline a commitment |
| Feedback | Explain known requirements, events, confidence, costs and outcomes without hidden-state leaks |
| Persistence | Only committed service outcomes change knowledge/location/obligations; UI state is cosmetic |
| Alternatives | Text lists, public services, local work, verification or a changed plan |
| Replayability | Different known contacts, rumors, conditions and goals make the same geography useful differently |
| Grind risk | Marker collection, mandatory street scouting and repeated previews; keep useful public information and batch travel |
| Determinism | Stable ordering/read revisions; no randomness or time advancement from presentation |
| Save compatibility | No UI-created schema; preserve historical careers and unresolved physical origins through the migration adapter |
| Offline | Local definitions, rendering and routing; no required tile server, geocoder or external AI |
| Agency / exploits | No omniscient NPC tracking, private-record leaks, ownership from pins or free teleport/preview reroll |

Future tests should compare read models before/after repeated views; mutate returned
objects to prove isolation; check hidden closures/NPCs/safehouses remain hidden;
distinguish rumors from facts; verify text/visual parity and deterministic order;
exercise stale route outcomes and save/resume; and cover color-independent/keyboard
presentation. This document is not evidence that a GUI, accessibility audit or
player-knowledge system has been implemented or tested.

## 2026-11-07 addendum — third-person streets and 2D navigation coexist

The user has selected third-person open-world gameplay as the **long-term presentation** target; the existing layered map specification remains useful as a local minimap, pause-map and accessibility/text companion rather than the only future world presentation. No such 3D map, free-roam player controller or route-to-animation binding is implemented by this addendum. See [M031-3D proposed vertical slice](GOON_THIRD_PERSON_VERTICAL_SLICE.md).

The first visual test uses a single stylized block with ordinary free exploration, one store and home interiors; every rendered entrance/exit must have a known mapping to its canonical atlas location or be explicitly cosmetic. **World-space position is not automatically authoritative**: do not change the Python location on collision or distance alone. At canonical boundaries, defer to Python permission, route cost, revision and outcome. A UI pin, cursor, camera pan, minimap zoom or proximity prompt is read-only. No omniscient pedestrian markers, faction ownership overlays or backstage route disruptions may leak from raw engine snapshots.

Provide an accessible alternative list/map for travel and interactions, including gamepad/keyboard remapping proposals and descriptive labels. The visual client's frame rate is independent from deterministic world time. Commercial/offline tile services are not required. This supersedes 2D-only *presentation aspirations*, not the current content atlas or movement authority.
