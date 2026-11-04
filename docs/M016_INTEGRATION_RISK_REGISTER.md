# M016 integration risk register — review draft

**Current status — Mission 013:** M016-A implements the station subset locally.
The design-risk register below is preserved. Current disposition at the end and
the [implementation/validation report](M016_A_IMPLEMENTATION_VALIDATION.md)
supersede earlier no-implementation status for that subset only. PR #15 remains
open/unmerged; broader vehicles and schedules are still proposals.

**Mission 012 update:** the same preserved draft now records the hardened
rail-C recommendation, atlas-backed p039/p071 pilot, concrete paired state and
transaction protocol in the companion architecture. These are still unapproved
design choices. The unchanged full suite was executed: **283 tests passed in
45.228 seconds**. PR #15 remains open at the same head; no production/test/atlas
changes, commit, push or PR write operation was performed.

## Status and verified baseline

Mission 011, November 4, 2026. Verified source:
`3251381177bf11c0b07cd940329ebd0be3a7bb52`; remote M015 feature head matches,
master is `fa2f9f5bbf081bde080c6d8b2e46512487027c66`. These three documentation
drafts live on local `docs/m016-mobility-architecture`, separate from PR
[#15](https://github.com/CapuchaRojo/gotham-underworld/pull/15), which remains
**open and unmerged**. No implementation, tests, atlas or schemas changed.

**Verified evidence:** source/test inspection, successful existing GitHub checks
on the exact head and the [M015 audit](M015_INDEPENDENT_ACCEPTANCE_AUDIT.md)'s
283-test record. This mission did not rerun that suite. In-memory diagnostics
confirmed station-free n22–n30 rail travel and 47-public-neighborhood connectivity
without rail. They do not validate M016. No M016 PDFs were available to inspect.
The existing CI log was also inspected directly: 283 tests in 31.786 seconds,
OK. No new CI run was triggered for these local uncommitted drafts.

**Proposed design:** every mitigation, new field, price, route bound, integration
adapter and acceptance scenario in this register is a recommendation for review,
not a verified runtime capability or implementation authorization. Read with the
[architecture](M016_MOBILITY_ARCHITECTURE.md) and
[acceptance matrix](M016_MOBILITY_ACCEPTANCE_MATRIX.md). Severity ranks potential
impact of a future integration error, not a claim of an existing baseline defect.

## Integration readiness and state ownership

Labels: **Implemented** = verified behavior; **Interface available** = existing
seam, new adapter still needed; **Approved direction** = user-endorsed intent,
not a runtime/implementation contract; **Proposed** = unapproved mechanism.

| Connection | Status and source evidence | Recommended boundary / missing dependency |
| --- | --- | --- |
| Command transaction, budgets and snapshots | Implemented: [service](../game_service.py#L70), detached [snapshot](../game_service.py#L56); three actions/18 TU. | Keep one mutation boundary and root transaction. New request retry receipt is proposed, not an existing service feature. |
| Navigation content/history | Implemented: [registry](../location_registry.py#L19), [nav validator](../navigation.py#L29), base atlas pin. | Overlay/dual reader/checkpoint are proposed. No base-file edits or old-event rewriting. |
| Housing and obligations | Implemented: [enrollment](../daily_life.py#L22), [daily phase](../daily_life.py#L172); bounded rent, promises and home entitlement. | Navigation owns position/home permission; life owns debt/deadlines. Mobility may lower cash but must not create a second housing record or automatic home benefits. |
| Lawful employment/criminal opportunities | Implemented: [choice eligibility](../daily_life.py#L230), source windows and real existing-risk jobs. | Interface available: existing place/action checks. Mobility changes reachability, not payouts/job RNG; no automatic arrival-to-work resolution. |
| Contacts and relationship commitments | Implemented: Tess/Cal observed memories, standing and day-based promise windows. | Interface available for explicit choice consequences. Full NPC schedules, hourly lateness, remote messaging and autonomous travel are not implemented. |
| Legal heat, evidence and custody | Implemented: existing legal commands/cases and detention travel block. | Interface available for custody reads. No generic non-job offense/evidence source; licensing, theft and impound need approved adapters. Never disguise them as a job. |
| Possessions and cash transactions | Implemented: `player.cash`, [life ledger](../daily_life.py#L53) when enrolled. | Generic personal inventory, vehicle title/rights/fuel/storage are proposed. Debit cash once; ledger records it. No dependency on life enrollment. |
| Blackgate release and supervision | Approved direction/future [prologue](GOON_PLAYABLE_PROLOGUE_CONTRACT.md), [institutions](GOON_INSTITUTIONS_AND_RECOVERY.md); actual legal custody is implemented. | Physical release, parole/probation and their conditions are not implemented. Do not equate a court release with a Blackgate teleport, vehicle impound or license grant. |
| Skills/attributes | Approved direction for later RPG development. | Cost policy may later accept a pinned read-only capability projection. No new attribute progression engine or transport XP loop in the pilot. |
| Multimodal travel/vehicles/stations | Approved direction in Mission 011; architecture only authorized now. | Hybrid modes, specific stations/fares/state versions and algorithms remain proposed. Existing station names are not operating services. |
| GUI/content separation | Interface available: detached reports/command result envelope; approved content-independent direction. | Use explicit station/vehicle IDs and public projections; no DC names in reducers. Full debug snapshot intentionally contains world truth. |

## Risk register — potential future integration failures

| ID / severity | Verified trigger or boundary | Proposed prevention / proof required | Gate |
| --- | --- | --- | --- |
| I01 / Critical | Nav1 validates only base IDs, rules1 and schema1; last journey must match current location. | Dual reader + pre-reset legacy checkpoint and post-reset activation budget; validate old values/base rules, then v2 continuity. Include pending v1 trips; reject missing/forged checkpoint, retroactive schema1 or downgrade. | S01–S07 |
| I02 / Critical | Atlas pin covers current content; editing/reordering file arrays changes it. | Immutable base + independent overlay pin/version with archived definitions. Fail clearly on missing required content, never substitute latest/reset career. | S05–S06 |
| I03 / Critical | Current service is atomic, but sequence IDs alone do not protect a retried client command. Global event validation already rejects duplicate player-command IDs. | Unique accepted request/source receipts; preserve global uniqueness before per-family dictionaries and one outcome per command. Reject retry unchanged; detached receipt lookup recovers original. No double settlement. | A01, A09–A11, S17 |
| I04 / High | Current `rail` boards at neighborhood nodes; station POIs cannot be intermediate. | New typed gate/platform transitions, distinct monorail mode, rules2 masks only old rail entries. Preserve old reader/graph. Assert no legacy-command bypass. | R02–R04 |
| I05 / High | Current reverse quote starts with the same world; no resource projection exists. | Return from outbound ending placement/fuel/cash/permissions; keep distinct placement labels. Disclose return target/caps, not a guaranteed reservation. | P01–P03 |
| I06 / High | There is no asset placement/possession owner today. | Single tagged placement per asset; with-actor location derived from authoritative actor position. Title/use rights/physical custody/observation distinct. No asset summoning. | R07–R10, A02–A05 |
| I07 / High | Current hidden closure commits a safe prefix using only TU. | Typed prefix execution, exact charge receipts, safe car parking reserve/station stop, no suffix resources. Hidden missing asset observed at actual retrieval point. | P07–P10, A05 |
| I08 / High | Every new resource dimension multiplies Dijkstra states. | One selected ground vehicle, one pickup/parking interval, two boardings, 64 transitions, 8,192 labels. Explicit planning-limit result and tested simpler alternative; no silent pruning. | R11–R17, benchmarks |
| I09 / High | Car licensing, confiscation and non-job legal evidence do not exist. | Gate car on an approved lawful credential source; defer criminal acquisition/impound incidents. Preserve existing evidence/job IDs and RNG. Arrest is not guilt or confiscation. | A04, A06–A08 |
| I10 / High | M015 room settlement consumes actual player cash; life may be absent. | Mobility owns its receipt, `player.cash` sole cash balance; existing ledger projects actual debit once. No life prerequisite and no second wallet. | A11, S11 |
| I11 / High | Current free graph connectedness does not prove daily affordability under closures. | Validate free escape topology, local work budget and bounded reopening per start; explicit remote-station7-TU/$0 after outbound versus free bus8 needs conscious wait. No vehicle/license purchase, automatic wait, teleport or paid rescue. | P11–P12, P15, S13–S14 |
| I12 / High | Current day phase ordering is legal/investigation/NPC/economy/warfare/court/nav/life. | Capture legacy boundary before navigation's reset, then activate after its one reset and before life. Preserve scheduled versus actual activation day. Pending save/read never activates; no second tick. | S03–S04, S10–S12 |
| I13 / High | Full snapshot exposes truth; future asset absence and closures can be secret. | Separate observed placement from truth; public projections and quote tokens use only known facts. No secret revision in stale-token rejection. Full snapshot remains debug-only for secret-sensitive UI. | P04–P06, A05 |
| I14 / Medium | `car` metadata exists but has no usable parking/fuel/road-surface contract; `boat` does not mean car ferry. | Author explicit road/parking/cargo overlay attributes; validate safe checkpoints and mode-specific gates. Default unknown surface to no skateboard bonus. | R05–R10, P09 |
| I15 / Medium | Existing promises use days, not hours; separate journeys currently each re-board. | Keep TU abstract and no hourly appointment inference. Disclose line/setup costs for each journey. Schedule expansion requires separate contract. | S11–S12 |
| I16 / Medium | Base zero-cost POI spurs are safe because intermediate use is forbidden. | Permit only specific station/retrieval anchors; monotonic handling phases, positive ride costs and 1-TU movement floor. No benefit on inspect/arrival/park loop. | R01, R14–R15, P13 |
| I17 / Medium | Present save validation retains unknown metadata; new enums/references may be malformed. | Strict known nested invariants/types/references and unsupported-version checks before play/write; retain only harmless unknown extensions. Never erase unsupported asset state. | P14, A10, S05–S09 |
| I18 / Medium | Local atomic save protects current state, but new long history can increase validation time. | Reuse staging/backup guarantees; validate structured receipts without per-label whole-history copies. Benchmark save/load separately; no audit truncation to hit target. | S09, benchmarks |
| I19 / Medium | Transport convenience can dominate every local choice or force repetitive errands. | Tuning fixtures where walk/bike/mono/car differ; free fallback, disclosed round-trip budget, bulk fuel/condition bands, no commute XP or mandatory repeated repair/parking menus. | R16, P11–P13, S14 |
| I20 / Low | Station branding, vehicle titles or continuity may change later. | Stable namespaced technical IDs separate from labels; immutable released definitions and explicit migration on later replacement. Keep licensed content out of generic reducers. | S05–S06 |
| I21 / High | Current service constructs a candidate/response and commits without calling full career validation after every command. | Add a narrow pre-commit mobility/resource/receipt invariant gate for new commands. Any unexpected error before root replacement discards candidate; no fallible effects afterward. Do not call whole-history validation per search label or treat current service behavior as a confirmed defect. | A09–A11, S07–S09 |

No listed item is a newly confirmed M015 defect. They are concrete hazards of
adding mobility to verified interfaces. The current rail abstraction is a
verified limitation relative to proposed station travel, not a claim that it
violates the existing M014 contract.

## Reproducibility, validation and performance policy — proposed

Routing/adoption must not draw from job/global RNG. First slices have no random
breakdown/theft generator. If incidents are later approved, use explicit source
identity and a separate deterministic incident stream/version, not wall time or
calls made by preview; preserve exactly-once incident effects across reload.
No new daily expense/tick is needed merely to support vehicles.

Reconstruct new resource deltas and placement transitions from committed events,
with original command/day identities. Serialize interrupted journeys only after
the transaction finishes. Perform field-level corruption and I/O failure tests;
do not count an in-memory `json.dumps` as proof of backup/failure behavior.
Schema evolution must retain the current no-silent-overwrite and previous-good
backup guarantees. New-reader historical compatibility is required; old-reader
support for opt-in nav2 is intentionally a clear rejection, never silent loss.

Planner caches may hold immutable pinned graphs only. Extract a thin routing
context once, not a full world/event deepcopy per label. Bound fleet selection,
transfers and labels; explicit bounds are preferable to hidden route truncation.
The matrix proposes reference-hardware p95/max timings and persistence targets;
these have not been measured. Deterministic label bounds can be CI assertions;
hardware-sensitive timing thresholds need measurements before becoming gates.

## Architectural decisions requiring approval before implementation

| Decision | Recommended default / rationale | Approval consequence |
| --- | --- | --- |
| D01: versions and opt-in | Adoption requires paired nav2/mobility1 even with empty assets; base immutable, rules1 while pending. Capture before nav reset, activate afterward on real wait. Defaults remain v1. | Approve old-binary forward rejection and local overlay support/archive obligation. No save conversion now. |
| D02: legacy rail | Recommend C from the explicit A/B/C comparison: v1 graph/history retained, legacy rail masked only for active rules2, new station service. | Approve an opt-in routing-policy change, not retrospective relabeling. B's coexistence remains an alternative with balance/UX costs. |
| D03: pilot geography | p039/p071 frontages, two added platform nodes, one two-stop ride backed by n17–n18–n23–n22–n30 via the four verified corridors. Earlier p022/p081 candidate superseded. | Approve service identity/topology and directed closure bindings. Atlas proves adjacency, not an existing monorail or equipment compatibility. No invented intermediate stops. |
| D04: fares and handling | Pilot: access/alight0, boarding1 TU/$2, atomic ride6 TU; frontage round trip14 TU/$4. Legacy bus8 one way stays free. Bike/car costs remain later paper tuning only. | Approve pilot economics; 18 TU and local livelihoods remain authoritative. Free bus may require next-day recovery if only7 TU remain. No actual prices changed. |
| D05: equipment model/cargo | Car/bike located vehicles; board portable capability. One ground vehicle/query; bike push supported, explicit station/ferry cargo rules. | Approve handling/parking restrictions and limits; no fleet optimizer or car-carrying ferry assumed. |
| D06: public route grammar | Exact journey fields include return_to and retry request ID; enable_mobility takes overlay_id/request_id. Pilot rejects nonempty vehicle IDs. Tokens bind known state only. Old travel reserved for v1/pending. | Approve the exact section-13 service/CLI contract, receipt semantics and cross-family validation. No client request signature is a hidden-state/security oracle. |
| D07: driver credentials/legal source | Single mobility-owned credential/restriction record with future legal adapter; lawful source needed before car gameplay. Non-job criminal acquisition adapter separate. | Decide credential issuance/expiry/restriction authority. Do not fabricate licenses, probation, theft evidence or court rules. |
| D08: algorithm bounds | Resource-constrained stable labels; 64 transitions, two boardings, one vehicle, 8,192 expansions, explicit limit failure. | Approve bounded initial route expressiveness and benchmark/tuning process; no silent optimality guarantee outside bounds. |
| D09: scope and sequence | Compatibility seam then station-only playable pilot, board, bike, car; incident/impound/release adapters conditional later. | Explicitly authorize each delivery contract. No hidden requirement for full inventory, hourly schedules, prologue or attributes. |

Mission 011 requests these decisions be surfaced, not answered by implementation.
Mission 012 further hardens them without granting implementation approval.
The engine/content boundary, offline execution, determinism, no paid services and
existing budgets are constraints already given; they do not need reapproval.

## Recommended first implementation contract — proposal only

Begin with compatibility slice 0: capture golden schema-1 history and current
fixtures, implement overlay validation and dual-reader/checkpoint tests behind
explicit adoption, without changing default career behavior. Then deliver a
two-stop p039/p071 station-only playable slice after D01–D04/D06/D08 approval: walk to
station, board/pay once, ride/alight, walk to destination, preview projected
return, handle a hidden closure, and save/resume. Use existing free modes as
fallback. No vehicle grant, license, criminal acquisition, new opportunity,
subday clock or prologue dependency belongs to that slice.

The [architecture](M016_MOBILITY_ARCHITECTURE.md), section 13, is now the exact
future file/test contract: four small new runtime/content files, narrow
navigation/service/CLI edits and two new test modules. Reuse existing career
validator hook, persistence and daily-life observer; no change to their behavior
is required. Keep generalized bike/car state-search dimensions out of the pilot.
The line's four-segment availability is checked before boarding its atomic ride;
an unknown interruption stops at an actual departure frontage after any real
approach. P08's later-line fixture does not imply extra pilot stations.

The reviewed matrix now has 61 prospective scenarios. Only three were added:
P15 (remote poverty plus remaining-TU return shortfall), A12 (detention while a
vehicle stays parked elsewhere), S17 (global player-command collision across
schemas). Other requested edge cases strengthened existing rows rather than
inflating the count. No M016 test, simulation or performance benchmark has been
executed; Mission 012's 283 passing tests are the existing production suite.

Meaningful choices are cash versus TU, detour versus a real deadline, and later
asset positioning versus convenience. Persistent consequences are resources,
placement and observed closures; variety comes from geography, access and real
commitments. Risks of grind are fixed commutes and repeated vehicle upkeep.
Mitigate with complete-route commands, free local work and coarse upkeep, not
real-time waiting or premium currency. Transport remains mechanically shallow
without later social/economic content, and must still be worthwhile on its own.

Before submitting a future implementation: preserve all 283 baseline tests,
execute applicable matrix cases, fresh-process replay/resume, malformed-save and
failed-save tests, four 365-day campaigns and one 1,000-day campaign; report actual
commands, results, meaningful decisions, persistent consequences, repetitive
loops and a short manual scenario. Keep PR #15 unmodified by this documentation
mission and stop here for human architecture review.

## M016-A risk disposition — Mission 013

| Priority / status | Current evidence / remaining work |
| --- | --- |
| P0: none confirmed | No known save-loss, duplication or custody/legacy-rail bypass remains in the implemented pilot after tested failure paths. This is not proof of absence. |
| P1: none confirmed | Mixed-version checkpoint, exact settlement, same-day limits, private quote provenance and later housing entitlement are regression-tested. Old M001–M015 saves remain readable; opt-in nav2 intentionally requires the new reader and pinned overlay. |
| P2: history scaling | Full career validation runs before every opted-in commit; persistence and transaction copying scale with history. Definitions are reused inside history validation; no per-label world copy. Larger careers still need profiling before adding assets/schedules. Reference timing targets are not certified benchmarks. |
| P2: bounded planning | A required-service query retains simple-path signatures; complex requests may hit8,192 labels. Error asks for simpler mode/waypoint rather than silently dropping states. Two boardings/64 legs are pilot limits. |
| P2: limited depth | Two frontages offer a7/$2 versus8/free trade-off; no traffic, hourly schedules, random theft or generated citywide disruptions. Repeated commute stress is not authored opportunity variety or a reward source. |
| P2: release/cargo/vehicles | No physical Blackgate release, cargo, credentials or vehicle gameplay. Existing custody/free alternatives are preserved; future slices need their own source/state contracts. |

I01–I07/I10–I13/I15–I18/I21 have implemented pilot mitigations and focused tests;
they remain review areas as content grows. I08 has bounded search and explicit
failure but not a certified large-graph timing result. I09/I14/I20 and vehicle
approval decisions remain future work. D01–D04/D06/D08 were authorized for the
pilot by Mission 013; D05/D07 and later vehicle/incident economics are not silently
approved. See architecture section14 for the actual origin-default return target
and v1-compatible empty-history checkpoint behavior, which clarify older drafts.

Implementation stays on `feature/m016a-mobility-pilot`, not M015's submitted
branch. Existing drafts were preserved before edits. No merge/rebase/force-push,
dependency, asset import or PR write occurred. Exact validation evidence and
remaining coverage limits are in the report; broader M016 is incomplete.
