# M016 mobility acceptance matrix — prospective contract

**Current status — Mission 013:** the M016-A station subset is implemented.
The 61-row design matrix below is preserved; it is not a claim that every future
vehicle scenario has been implemented or executed. Current coverage, commands
and counts are recorded in the [implementation/validation report](M016_A_IMPLEMENTATION_VALIDATION.md)
and the mapping at the end. Earlier execution statements remain historical.

**Mission 012 hardening:** reviewed all original 58 scenarios against the new
concrete contract. Clarified existing rows and added only P15, A12 and S17 for
distinct missing combinations: remote-station poverty after outbound travel,
detention with a separately parked asset, and duplicate global command IDs
across schemas. The matrix now has **61 prospective scenarios**, none implemented
or executed as M016 tests. The unchanged regression suite was actually run in
Mission 012: `python -B -m unittest discover -s tests -q` — **283 tests in
45.228 seconds, OK**. No production or test file was changed.

## Status and verified evidence

Mission 011, November 4, 2026. **All M016 scenarios below are proposed tests,
not executed tests or implemented features.** Source inspected at
`3251381177bf11c0b07cd940329ebd0be3a7bb52`; the separate local documentation
branch is `docs/m016-mobility-architecture`. PR
[#15](https://github.com/CapuchaRojo/gotham-underworld/pull/15) remains open and
unmerged. No source/test/schema/atlas changes belong to this mission.

Verified baseline evidence: the [M015 audit](M015_INDEPENDENT_ACCEPTANCE_AUDIT.md)
records 283 passing tests, and both checks for the exact head are successful.
Mission 011 did not rerun that suite. It inspected navigation/persistence tests
and executed in-memory base-graph diagnostics only: n22 to n30 via rail e08 costs
3 TU without a station; non-rail/free-mode graph traversal reaches 47 public
neighborhoods and excludes restricted n46. Those checks do not test M016.
No referenced M016 design PDF was available; no acceptance result is inferred
from an unseen design or a green older suite.

Mission 011 evidence commands included `git fetch origin master
feature/m015-living-gotham`, `git status --short`, `git rev-parse HEAD`,
`gh pr view 15 --repo CapuchaRojo/gotham-underworld --json
state,headRefName,headRefOid,statusCheckRollup`, and
`gh run view 41873861331 --repo CapuchaRojo/gotham-underworld --log`.
The inspected existing CI log reports **283 tests in 31.786 seconds, OK**;
both checks are successful, not newly triggered by these drafts. Source/graph
diagnostics and local Markdown checks ran through `python -B -`, with inline
read-only scripts. Markdown checks covered local targets, source line bounds,
fence pairing, table row terminators, trailing whitespace and unique scenario IDs.
They are structural checks, not a third-party Markdown lint or rendered review.

The [architecture draft](M016_MOBILITY_ARCHITECTURE.md) defines the proposed
hybrid modes, versions, state ownership and resource rules. The
[risk register](M016_INTEGRATION_RISK_REGISTER.md) identifies prerequisites and
approval decisions. M016 gates apply only after their slice is authorized;
car/theft/impound tests are conditional gates, not permission to build those
systems during planning or the station pilot.

## Existing coverage — verified source, not a new execution report

| Existing tests | What is covered / what is not |
| --- | --- |
| [Navigation registry tests](../tests/test_navigation.py#L23) | Atlas counts, endpoints, positive costs, permissions, spurs, duplicate JSON and detached content. No mobility overlay/station graph. |
| [Basic navigation](../tests/test_navigation.py#L85) | Home/store/day/resume, separate actions/TU, 18-move limit, read isolation, atomic rejections and custody. No fuel, possession, fare or parking. |
| [Routes and closures](../tests/test_navigation.py#L135) | Costs, return TU, exact budget, reachability, directional/mode closures, actual prefix, finite island recovery and revoked-permission departure. No station transitions or projected vehicle end state. |
| [Order/adoption/history](../tests/test_navigation.py#L222) | Reversed definitions, daily idempotency, historical fixtures, nested corruption, failed save, pinned atlas, 40-day replay/resume and hash-seed/global-RNG isolation. No v2 adoption/checkpoint. |
| [M014 audit](../tests/test_m014_audit.py#L19) | Last-location/TU consistency, missing/duplicate outcomes, command day, custody, receiving gates, directional return quote, unused-nav legal/economic equivalence. No second journey command family. |
| [Persistence suite](../tests/test_career_persistence.py#L41) | Malformed/unsupported versions, duplicate/nonfinite JSON, UTF-8, custody, staging/flush/backup/replace failures, exclusive creation, fixture migrations and command IDs. New assets must be validated too. |
| [M015 audit tests](../tests/test_m015_acceptance_audit.py), [daily-life tests](../tests/test_daily_life.py) | Existing choice, promise, receipts, projection and stale-marker integrity; historical enrollment and resumed campaigns. They cannot prove new travel charges preserve those invariants. |

Future baseline command: `python -B -m unittest discover -s tests -q`.
Run the existing tests unchanged; do not replace expected legacy outputs to make
a new mode pass. Add focused tests using tiny authored graphs for exact routing
and actual pinned content for integration. Synthetic fixtures must be explicitly
identified; station/vehicle examples do not become atlas facts by appearing here.

## Common assertions for every future scenario

For each known rejection compare the complete world before/after, not only TU:
cash, actions, day/markers, command/journey/asset sequences, events, legal state,
job attempts, factions, vehicle placement/fuel and knowledge. Global RNG must
also remain unchanged. For every success validate the career, serialize/restore
through the real persistence API, compare detached response/state and prove
exactly one result per accepted command/source/request identity.

Use integer boundary cases including bools masquerading as ints, negative and
oversized values. Run reverse insertion order and independent Python hash seeds
without rewriting pinned content. Compare schema-1 history as exact JSON values;
byte layout of a reserialized whole file need not match its original formatting.
Observe secret closures/loss only at legitimate discovery points; public report
equality must hold for indistinguishable known states. Debug snapshots expose
world truth intentionally and are not the public-view oracle.

## Proposed scenarios: routing and all modes

| ID / slice | Setup and action | Expected observable result / invariant |
| --- | --- | --- |
| R01 / 1 | Walk between distinct local nodes, including zero-cost base spurs. | Correct permitted path; completed movement at least 1 TU; no cash/actions/day change. Same-place request rejects with no reward. |
| R02 / 1 | Request reachable and inaccessible station journeys from a neighborhood, POI and restricted institution. | Approach, platform boarding, real line ride, arrival platform and egress are explicit. No neighborhood/unauthorized boarding. |
| R03 / 1 | Place a faster v1 rail-only edge parallel to proposed monorail; adopt rules2. | Active planner/command cannot use the legacy rail shortcut. Unadopted/pending v1 costs/history stay identical. Mixed edges retain bus/walk. |
| R04 / 1 | Preview/commit existing bus and ferry, pure and mixed routes. | Still supported with zero legacy fares; no unapproved vehicle cargo. No general walking-across-water fallback. |
| R05 / 2 | Carried usable skateboard, smooth versus rough/forbidden edges. | Authored smooth benefit only; carry at walk cost elsewhere. Explicit propulsion/item ID; no board when absent/unusable. |
| R06 / 2 | Board carried through station/ferry gates with permitted/prohibited cargo. | Respect specific cargo/access rule. No drop/duplication/remote retrieval and no hidden boarding-cost shortcut. |
| R07 / 3 | Bike parked away from player; ride to a destination with legal storage. | Pay actual approach/setup/ride, update one placement and emit receipt. No teleporting bike to origin or returning it home automatically. |
| R08 / 3 | Push bike on permitted foot link, then ride a cycle link and park. | Bike follows actor while pushed/ridden; no forbidden ride, no double location. Handling cannot yield repeatable free movement or benefit. |
| R09 / 4 | Car at public safe parking, valid authorization, exact fuel/TU. | Approach/unlock/road/park/egress costs disclosed; fuel deducted once. No POI-spur driving or assumed parking on arbitrary road endpoints. |
| R10 / 4 | Car remote, empty/insufficient fuel, unusable condition or no parking. | Known impossibility rejects or alternative is offered without auto-refuel, repair, relocation or cash overdraft. Fuel/condition boundaries are strict. |
| R11 / 1–4 | Equal-cost alternatives; reverse nodes/edges/modes/assets/maps; PYTHONHASHSEED 0 and 42. | Exact same legs, rank, resource deltas, IDs and outcome. Compare under pinned data, not a changed file fingerprint. |
| R12 / 1–4 | Same endpoint with different line, cash/fuel or parked-vehicle signature. | Keep nondominated feasible labels; never discard a usable return state just because the player node matches. |
| R13 / 1–4 | Directed edges, restricted receiving gate, revoked permission, water crossing. | Direction/access enforced on each transition. Legitimate outward exit remains; revoked access does not permit reentry. |
| R14 / 1–4 | Repeated zero-cost station access, board/alight, vehicle mount/park and POI cycles. | No negative costs, resource creation, free movement reward or endless search. No arbitrary POI transit shortcut. Bound failure is explicit. |
| R15 / 1–4 | Exactly 18 TU, one TU short, and request cap smaller than daily remaining. | Exact cap succeeds; overspend rejects unchanged. Handling/terminal parking counts. No action or day reset by route/inspect/save. |
| R16 / 1–4 | Fastest/free profiles and explicit equipment/mode restrictions. | Stable disclosed ranking; free spends $0. Restrictions cannot grant a car/board or override service station/cargo/access requirements. |
| R17 / 1–4 | Route exceeds 64 transitions, two boardings or 8,192 expanded labels, including equal-cost zero-cycle stress. | Typed planning-limit explanation; no unbounded search, false claim of physical disconnection or silent feasible-label pruning. Provide tested simpler/waypoint fallback where available; pilot carries no ground-vehicle dimensions. |

## Proposed scenarios: previews, resources and interruptions

| ID / slice | Setup and action | Expected observable result / invariant |
| --- | --- | --- |
| P01 / 1 | Outbound affordable, combined return exceeds remaining TU or fare cash. | Distinguish outbound affordability from same-day return. Project cash after outbound fare; no double use of initial money. |
| P02 / 3–4 | Park vehicle at destination, or leave it at an intermediate node before transit. | Return begins from projected placement/fuel/condition, not original placement. Different feasible return may walk or retrieve vehicle. |
| P03 / 1 | Directional known closure affects only return; later day reopening. | Preview reflects current known return direction/date, not assumed symmetry. Next-day recovery is separate from same-day return. |
| P04 / 1–4 | Read previews/reports 100 times; mutate every returned nested value. | Entire world, counters, RNG and hidden knowledge unchanged; no persistent quote cache or asset initialization. |
| P05 / 1–4 | Change publicly known cash/permission/custody/vehicle status after quote. | Commit rejects stale/unmet prerequisites atomically, with a useful reason; never spends stale quoted resources. |
| P06 / 1–4 | Two worlds with same observations but different hidden closure/loss. | Equal public quotes/tokens/reports before discovery. No hidden revision/hash oracle; differences arise only after actual observation. |
| P07 / 1 | Unknown departure closure, with sufficient TU to attempt. | Stop before unaffordable/blocked departure setup; zero phantom fare/fuel. If no movement occurred, zero TU. One bounded discovery outcome. |
| P08 / 1 | Synthetic two-line fixture: hidden second-line closure after a completed first ride. Also test the actual two-stop pilot with a blocked underlying segment discovered after approach. | General fixture ends at the real interchange, charging completed first ride only. Pilot checks the entire chain before boarding and stops at departure frontage; it has no invented intermediate station. Save/resume both outcomes. |
| P09 / 4 | Hidden road closure after car pickup, close to TU/fuel cap. | Player and car remain together at safe checkpoint, parking reserve honored, no mid-edge split or negative resource. Actual prefix receipts reconstruct final placement. |
| P10 / 1 | Known closure, closure on opposite direction/mode, closure expiry. | Known blocked plan rejects/detours unchanged; unrelated direction/mode usable. Actual wait reopens once; read/load does not. |
| P11 / 1–4 | Zero cash; all three actions spent; positive travel TU. | Permitted walk/bus/ferry remains usable; no requirement to steal, buy a vehicle or earn money. Paid mode rejects without side effects. |
| P12 / 1–4 | Zero TU, zero cash, safe isolated location and ordinary bounded closure. | Travel rejects unchanged; saving, inspection and explicit wait remain. Proven free route after bounded reopening; no teleport, paid rescue or resource refresh exploit. |
| P13 / 1–4 | Return home repeatedly, preview return or re-enroll mobility same day. | No TU/actions, wages, home benefit, fuel or condition refresh. Repeated enrollment rejects. |
| P14 / 1–4 | Token/request contains invalid numeric string, bool-like data, unknown IDs or excessive lengths. | Boundary rejects before effects; deterministic error, no dynamic evaluation, filesystem path use or dependency call. |
| P15 / 1 | Begin at p039 with 14 TU remaining and $2; take proposed pilot7/$2 to p071, then save/resume with 7 TU/$0. | Quote shows paid return unaffordable and free bus8 beyond same-day budget; current physical free fallback must be retained in rules2. Reads cannot refund fare/reset TU. Explicit wait restores normal18 TU once; bus8 reaches p039 without a purchase. Known alternative closure requires another proven route or <=2-day reopening. |

## Proposed scenarios: assets, legality and exactly-once effects

| ID / slice | Setup and action | Expected observable result / invariant |
| --- | --- | --- |
| A01 / 2–4 | Lawful purchase/gift of one source instance; repeat source/request before and after resume. | One title/placement transfer, one actual debit if any, one receipt. Duplicate rejects unchanged; no regenerated stock or acquisition ID. |
| A02 / 3 | Borrow then operate/return asset; original owner remains. Separately test title without storage permission, locked asset without a key, and a grant without possession. | Title, use rights, security and physical access are independently enforced; unauthorized retrieval rejects unchanged. Expired loan disables unauthorized use but never deletes/teleports asset. |
| A03 / later | Discover an unattended asset without keys/title grant. | Knowledge/opportunity only; no automatic ownership. Acquisition requires approved source and permission/legal adapter. |
| A04 / later | Fixture with contested/stolen title and real placement; query as owner or possessor. | Rights/knowledge and world truth remain distinct; known unavailable asset rejects. No invented job/evidence/payout. Gate criminal-acquisition gameplay until adapter approved. |
| A05 / 3–4 | Hidden loss at last-known parking; approach then attempt retrieval. | Charge only performed approach, record observed absence once, no mount/drive cost or disclosed hidden thief location. Repeated known use rejects unchanged. |
| A06 / 4 | License absent, suspended or incompatible; vehicle legal owner is player. | Cannot drive; ownership remains; free alternatives available. Reads cannot grant authorization. Unknown future restriction types fail clearly. |
| A07 / 1–4 | Arrest/pretrial/sentenced custody before quote or commit. | Existing custody blocks travel; reports/save/court/wait remain. No escape through station, equipment or pending adoption. |
| A08 / later | Explicit impound then release transfer fixture. | Causal event and single facility placement required; no automatic arrest-to-impound inference. Release does not imply vehicle recovery, teleport or license reinstatement. |
| A09 / 1–4 | Retry an accepted journey request after success/interruption and after resume. | No duplicate fuel/fare/TU/discovery/result; duplicate request rejects unchanged, detached prior receipt remains inspectable. One outcome per command. |
| A10 / 1–4 | Tamper with fuel, cash delta, placement tag, title source, request receipt or journey IDs. | Validation rejects contradiction before play/save, including parked-and-carried, duplicated asset ID and missing causal receipt. Unknown metadata retained only where safe. |
| A11 / 1–4 | Same fare/fuel purchase with daily life absent, pending and active. | `player.cash` debited once. Mobility charge receipt works without life; existing life ledger projects the change without charging again. Existing room payment still reconciles. |
| A12 / 3–4 | Park a vehicle at node A, move elsewhere, enter valid custody, save/resume and resolve the existing legal case. | Custody blocks travel/retrieval but leaves title, rights, fuel and physical parking at A unchanged. Legal release grants no car teleport, implicit impound or license; actual later retrieval still needs access, condition and valid rights. |

## Proposed scenarios: saves, M014/M015 and recovery

| ID / slice | Setup and action | Expected observable result / invariant |
| --- | --- | --- |
| S01 / 0–1 | Load every historical fixture M001–M014 plus the audited M015 career; never enroll. | Existing migrations/behavior/events/home/budgets unchanged; no mobility grant or automatic rules2. Existing 283 tests remain unchanged and pass. |
| S02 / 0–1 | Historical no-nav career requests mobility; active nav1 career enrolls after travel. | No-nav path requires existing navigation adoption first. Nav2 pending preserves resources and rules1; no backdated journey/vehicle/home. |
| S03 / 0–1 | Save/load pending request; travel under rules1 while pending; repeat adoption with same and different request IDs; actual wait. | Both repeats reject unchanged. Capture latest v1 location/TU checkpoint before the single nav reset; record activation budget after it, before life. Neither load nor clock-only day change activates. |
| S04 / 0–1 | Use legacy clock-only tool before save/load/next whole-day phase. | Stale marker remains without activation/reset on load; next actual wait applies each phase once, using existing marker policy. |
| S05 / 0–1 | Read nav2 pending/active in M015 binary; remove/mismatch required overlay or base pin. | Clear unsupported-version/content error, never silently ignore mobility, substitute latest graph or reset location. Original v1 saves still open in old binary. |
| S06 / 0–1 | Preserve schema1 history including a pending-adoption trip, activate, perform schema2 journeys/returns. Also test an empty legacy prefix and forged schema1 after activation. | Original events remain equal JSON values and base1 costs; compare against pre-reset checkpoint then validate actual activation reset and schema2 continuity. Empty prefix uses real prior position. Reject retroactive schema1 trips, forged checkpoint and version downgrade; latest v2 location need not equal last v1 arrival. |
| S07 / 0–1 | Delete/duplicate outcome for either travel command family; forge command day or checkpoint. | Validation rejects; global journey sequence and command links unambiguous. Enrollment has its own receipt, not a fake journey. |
| S08 / 1–4 | Save/resume before/after each command and interrupted outcome for 30-day itinerary. | Exact state/events/IDs/quotes match uninterrupted run; no unpaid suffix, repeated transfer, daily charge or resource restoration. |
| S09 / 0–4 | Force serialization/fsync/backup/final replace failure with mobility assets and current position. | Existing primary/backup guarantees hold; caller world unchanged by save attempt; reload last successful checkpoint, not partially staged state. |
| S10 / 1–4 | Identical legal/jobs/faction scripts: non-adopter, adopted-unused, and walks-only adopter. | Existing job attempts, cases, heat, courts, faction cash/power/territory identical after removing only documented mobility events/state. No navigation RNG contamination. |
| S11 / 1–4 | Existing M015 lawful work/crime/promise/room review with travel and fare cash use. | Location and three-action eligibility remain authoritative. Travel neither pays work nor expires day windows; wait can break promise once. Actual lower cash affects room settlement normally. |
| S12 / 1–4 | Pending promise/offer at deadline; preview/travel/save then explicit wait. | No hourly lateness invented. Real day transition expires/breaks once; no automatic commute, catch-up wages or refreshed source. |
| S13 / 1–4 | Newly released, no home vehicle/license/cash; restricted gate visit revoked. | Permitted walking/free transit and useful recovery information; departure without unauthorized reentry. Physical Blackgate release test waits for a separately approved release contract. |
| S14 / 1–4 | Publish overlay; enumerate all allowed starts, destinations and closure fixtures. | Every public start has a free safe fallback; local livelihood remains budget-reachable. Distinguish connected graph from 18-TU feasibility; no mandatory repeated commute grind. |
| S15 / 1–4 | Fresh processes, reversed runtime lookups, fixed scripts and resume at every day. | Identical canonical final state/event hashes across order/hash seeds; canonical overlay fingerprint independent of authoring order if specified as sorted records. No wall-clock/RNG-dependent routing. |
| S16 / 1–4 | Four 365-day seeds and one 1,000-day campaign with fixed travel/choice policies. | Validate every day; resource/ID/event bounds, no trapping, no repeated daily/acquisition effects; resumed checkpoints match. Report actual gameplay consequences and limitations, not just pass count. |
| S17 / 0–1 | Duplicate a `player_command` ID across legacy travel, adoption, wait or journey envelopes while keeping domain IDs/receipts distinct; try both array orders. | Global duplicate-ID rejection precedes dictionary indexing; no envelope silently overwrites another. Domain events legitimately share their parent command ID. This is distinct from duplicate outcomes S07 and request retries A09. |

## Mission 012 gap review and implementation gate

| Requested coverage | Existing scenario retained/hardened | Genuine gap decision |
| --- | --- | --- |
| Historical v1 journeys after adoption / mixed histories | S01–S06, S08; concrete paired state and legacy/schema2 examples in architecture sections 10–11. | Clarified checkpoint before reset, pending v1 trips, empty prefix, downgrade and rejection of new schema1 after activation; no duplicate scenario. |
| Duplicate command IDs | S07 covers outcome/command links; A09 covers accepted-request retries. | Add S17 because global envelope collision is neither case. Current code already rejects it; future dispatch must preserve that check. |
| Closure discovered during travel / interrupted resume | P07–P10, S08–S09. | Clarify real pilot departure check versus synthetic later-line interruption; existing cases suffice. |
| Zero cash at remote station | P11/P12 cover generic poverty/exhaustion separately. | Add P15 to combine irreversible outbound fare, remaining-TU shortfall, actual station fallback and resumed recovery. |
| Vehicle stranded elsewhere / detention while parked | R07/R10, P02, A07. | Existing retrieval tests suffice for stranding; add A12 for custody preserving parked placement through legal release. |
| Outbound versus actual return feasibility | P01–P03 and P15. | Explicit remaining fare/fuel/placement projection; no duplicate case. |
| Repeated adoption / unauthorized access | P13, S03, A02, A06. | Strengthen pending/active retry and independent keys/title/place rights in existing rows. |
| Read-only mutation / deterministic ties / performance | P04–P06, R11/R12/R14/R17, S15 and benchmark table. | Retain and specify full-world equality, secret equivalence, label-bound behavior and zero-cycle stress. |

For the first authorized station slice use only applicable scenarios from slices
0–1 plus new P15/S17; A12 is a later vehicle gate. Keep all 283 baseline tests
unchanged. Planned methods/files are listed in architecture section 13, not
created here. Test exact pilot topology7/$2 and its real free bus8 fallback,
mixed-version history, single-reset enrollment, pre/post-discovery save/load,
known rejection equality, duplicate IDs/receipts and observer-isolated cash.

**Mission 012 execution record:** full regression command above exited 0;
read-only `python -B -` scripts validated the actual p039/p071 POIs, access
spurs, contiguous four-corridor chain and current v1 auto/rail7, bus8, walk18
previews. Test fixture setup changed only in-memory copies, not saved careers.
PR metadata read with `gh pr view 15 --repo CapuchaRojo/gotham-underworld --json
state,headRefName,headRefOid,baseRefName,url,statusCheckRollup` confirmed OPEN,
unchanged head `3251381177bf11c0b07cd940329ebd0be3a7bb52` and both existing checks
successful. No M016 CI run, campaign, performance benchmark or gameplay test is
claimed. Final documentation checks passed: **60 links, 37 source-line bounds,
61 unique scenario IDs and six parsed JSON templates; zero structural errors**.
Static checks also reconciled template command/journey IDs, pre/post-reset
checkpoints, contiguous legs and cash/TU arithmetic against the actual four-edge
atlas chain. These validate the written examples, not an M016 implementation.

## Proposed performance gates — not measured yet

| Benchmark | Input / proposed bound | Evidence to record |
| --- | --- | --- |
| Planner complexity | 168 base nodes + at most 24 pilot nodes; 64 transitions; two boardings; one selected ground vehicle; 8,192 expanded labels per outbound/return query. | Expanded/dominated labels, peak frontier, result/limit reason. Same limits for all insertion orders; assert deterministic resource bound in CI. |
| Warm interactive preview | 1,000 fixed-seed origin/destination/resource queries, including no-route and projected return. Candidate target p95 <=100 ms, maximum <=500 ms on recorded reference hardware. | Python/OS/CPU, graph pins, each query class and tail times. Hardware-sensitive timing is initially diagnostic; investigate outliers before setting CI thresholds. |
| Long history isolation | Repeat the same query at 0 and 1,000 recorded journeys. | Planner should consume a thin detached mobility context, not copy/replay full world history per label. Measure separately from service transaction/save overhead. |
| Persistence overhead | Career with 1,000 journeys and bounded asset inventory; proposed reference target <=2 s per save/load. | File bytes, validation/staging time, replay parity and backup integrity. No truncating audit history to pass; profile before introducing caches/checkpoints. |
| Worst case / safe fallback | Dense equal-cost graph, zero spurs, low fuel/cash and many nondominated labels. | Bounded finish or explicit limit result, no recursion blowup or silent optimality claim; verified simpler route offered where one exists. |

Cache only immutable definitions keyed by complete content/rules pins. Do not
cache mutable world/custody/cash/secret facts across quotes. No network, dependency
installation, time-based timetable or external pathfinding service is necessary.

## Future validation procedure and human scenario

After implementation is separately approved: run unchanged full suite, then
focused matrix tests with actual command names, migration failure injection,
fresh-process replay, 30-day resume and long campaigns. Re-run full suite once
after the final changes and inspect CI on the exact submitted head. Record exact
commands, counts, failures, seeds, pins and limitations; do not predeclare results.

Proposed manual pilot scenario, using fixture routes/prices only:

1. Inspect existing p031 home/actions/TU, enroll mobility explicitly, save/load
   pending, then advance once. Confirm only the normal 18-TU/three-action reset.
2. At an approved public origin compare free walking/bus with a station-only
   itinerary. Inspect $2 boarding and outbound/return totals; commit one journey.
3. Retry its request ID; observe rejection without a second fare. Save/resume;
   verify actual location, money, TU, command and journey receipt.
4. Introduce an authored unknown departure closure through the test fixture, not
   a player cheat command. Travel toward it; stop safely, pay only actual prefix,
   learn the closure once and take a free alternative or consciously wait.
5. Complete an eligible existing local M015 choice with its own action and
   location check. Review the real promise/room deadline, then advance explicitly.
   No job pays merely because a station/doorstep was reached.

The player chooses money versus travel budget, detour versus a deadline and
whether retrieving equipment is worth tomorrow's position. Variety comes from
placement, surfaces, lines and actual obligations; persistent consequences are
receipts, resource depletion and knowledge. Remaining shallowness is deliberate:
no hourly schedules, transit crowds, theft generation, combat or narrative
prologue. The first slice must remain useful without those future systems.

## M016-A implemented test mapping — Mission 013

The new [pilot tests](../tests/test_mobility_pilot.py) and
[compatibility tests](../tests/test_mobility_compatibility.py) preserve all existing
tests. Parameterized corruption/access/failure cases share methods; a method count
is not a claim to execute every future matrix row. Notable mapping:

| Matrix / required behavior | Actual evidence |
| --- | --- |
| R01–R04, R13–R17: modes, gates, costs, restrictions and bounds | Exact7/$2, actual approach, no remote boarding, free bus8, existing ferries with real gate permissions, same-place rejection, exhausted TU/actions independence, explicit planner limit and order/hash-seed tests. |
| P01–P06: return and public/read-only isolation | Outbound resources deducted before return; outbound caps do not erase real return resources; nested reference isolation, stale token, identical public tokens for indistinguishable private disruption causes. |
| P07/P08/P10/P15: disruptions and recovery | Pilot entire chain checked before boarding; zero-cost first departure discovery, actual walking/bus prefix, directed/reopening policy, remote7-TU/$0 state needing explicit wait before free bus8. No multi-line pilot or intermediate stops claimed. |
| A07/A09/A11: custody, retry and money | Custody rejection; duplicate request receipt without repeat charge; life ledger observes one real $2 debit. |
| S01–S09/S17: compatibility and corruption | All old fixtures plus baseline-generated M015 career; pending/active reload, historical rail, mixed schemas, duplicate global IDs, forged resources/legs/checkpoints, missing overlay/pair, fsync/backup/final-replace failures. |
| S10–S12/S15: gameplay/time integration | Unused-adoption legal/job/faction comparison, daily-life fare/housing integration, actual CLI save/resume, same-day limits, retained stale TU markers, low-level reducer cannot activate pending adoption. |
| S14/S16 subset: long-run and ordinary continuation | Campaigns use existing daily life, exhaust fare money, continue by free bus and retain home. Periodic save/resume matches uninterrupted worlds after every command. Full four-seed/1,000-day gate is not claimed. |

R05–R10, P02/P09, A01–A06/A08/A10/A12 and other vehicle/impound integrations
remain proposed. Reserved vehicle state is rejected, not simulated. P08's
synthetic multi-line extension also remains future; the actual pilot interruption
is tested. See the report for exact executed commands/counts rather than treating
this mapping as 61 independent passing tests.
