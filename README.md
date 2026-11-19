# Gotham: The Goon

*A Living Gotham Crime RPG*

> Everybody wants to rule Gotham. You're just trying to survive it.

A deterministic, offline, single-player crime-city simulation and terminal RPG
prototype about an ordinary criminal surviving work, loyalties, and a changing
city. Python 3.14 standard library only: no packages, external AI services,
or paid APIs are required. The local executable includes **The Night Shift and
The Wrong Notice**, two optional independent incidents, alongside M016-A mobility,
M015 daily life and M014 navigation. Provenance integration PR #18 and M018 PR #19
are merged into master at `8bc9700` and `d0723b1`. M019 civilian service and police
intake merged through PR #20 at `6682019`. M020 ordinary work, housing planning
and conditional support merged through PR #21 at `74a5fab` with 522 passing tests.
Mission 029 expands the existing design registries and organization contract
only; no faction or rogue gameplay is added. A global clock, rogue/Bat-Family
encounters, broader vehicle systems and combat are not implemented.

This is an independent, unofficial prototype. Its intended future creative
setting is the DC universe; it has no endorsement, authorization, or affiliation
with DC, Warner Bros., or their partners. The executable retains its original
placeholder characters, factions, and districts. M013 introduces no DC characters,
new storylines, combat, or imported assets. The working title and setting are
subject to future licensing and title clearance. Any proposed public distribution,
commercial release, fundraising, or external pitch materials need separate
rights and legal review.
No DC license is claimed, and the working title is not legally cleared.

## Current integration caution — 2026-11-07 worktree snapshot

The `feature/m030-c2b-frontend-integration` worktree contains imported frontend source and local-host inspection tooling that Codex was implementing when its run stopped; as of the latest owner-supplied as-is ZIP, it is **uncommitted**. Reported frontend/browser test progress is not a completed merge or a fully playable game. Preserve that branch and finish GTG-13B security/reproducibility/real-host acceptance separately. See [PROJECT_STATE.md](PROJECT_STATE.md).

## Long-term presentation direction — decision of 2026-11-07

**Selected creative target:** a third-person, open-world crime/life RPG, built incrementally from **one living block**. This is a direction decision and a proposed Godot feasibility track, **not** an implemented 3D game, approval to rewrite gameplay, or a claim that React is obsolete. The terminal/Python game and the React local-engine integration remain the active delivery path. Godot 4 is a *candidate* client for an isolated visual prototype; no Godot runtime or 3D gameplay exists in this inspected source snapshot.

See [the proposed One Living Block vertical-slice contract](docs/GOON_THIRD_PERSON_VERTICAL_SLICE.md) for physical scope, controls, authority boundary, location/time policy, staged feasibility gates and security. Python remains the deterministic gameplay/save authority; 3 actions/day and 18 travel TU/day remain unchanged. The long-term presentation decision supersedes earlier 2D-only *visual target* proposals, **not** historical milestones or current React acceptance work. Ownership/merger of future 3D code requires separate explicit authorization.

## Durable local engine bridge — Mission 030-C1

The opt-in [C1.3 browser host](docs/M030_C1_3_BROWSER_HOST.md) adds pinned local
asset serving, one-time authorization and stable-port resume for existing bridge
careers. It requires an independently approved compiled bundle; actual React
compatibility and browser gameplay integration remain blocked and unimplemented.
The headless API below remains available.

The standard-library [C1 bridge](docs/M030_C1_DURABLE_ENGINE_BRIDGE.md) provides a
loopback JSON API, player-safe projection and atomic world/request-receipt
checkpoints. It reuses authoritative Python commands and preserves three actions
and 18 TU. Durable request identities prevent duplicate effects across retries,
lost acknowledgments and restart. Historical engine JSON is explicitly imported
into a new checkpoint; exclusive legacy export preserves CLI compatibility.

Run `python -B bridge_http.py --checkpoint "C:\private-data\career.bridge.json" --new`
with an existing private data directory, or omit `--new` to resume. The launcher
prints the loopback address and private capability. No React interface, assets,
Native.Builder changes or public server are included. The contract documents exact
headers/endpoints, import/export, recovery, tests and limitations.

## Design foundation and status

Ordinary goons are the protagonists. Professional henchman, lieutenant,
independent operator, boss, informant, reformed citizen, and tragic casualty are
future career possibilities, not an implemented campaign or a single promotion
ladder. The intended tone combines dark workplace comedy, street-level crime
drama, survival, and occasional horror. Current gameplay is described below;
the first local work, room obligations and two original contacts are implemented
in M015. Broader careers, combat and DC character content remain design work.

M014 loads the complete documented atlas as local data and implements a small
home/store/return slice with public navigation. See the
[runtime contract](docs/GOON_WORLD_RUNTIME.md),
[current roadmap](docs/GOON_MILESTONE_ROADMAP.md), and
[future prologue contract](docs/GOON_PLAYABLE_PROLOGUE_CONTRACT.md).
Older design documents describe M013.1 proposals; the runtime contract identifies
the implemented subset and supersedes their historical M014 combat numbering.

| Document | Purpose |
| --- | --- |
| [Master character/faction index](docs/GOON_MASTER_ROSTER.md) | Author-only navigation to existing identities, organizations, roles, implementation status and source authorities; no public discovery roster |
| [DARK canon registry](docs/GOON_DARK_CANON_REGISTRY.md) | Seven initial candidates plus Solomon Grundy and four existing-Gotham bridges, with source/continuity limits and Slaughter Swamp research; no supernatural gameplay |
| [Optional DARK contract](docs/GOON_DARK_PROGRESSION_CONTRACT.md) | Proposed late discovery, consent, optional four-encounter achievement, behavior consequences, grounded recovery and DARK-gated Grundy outcomes; no implemented unlock |
| [Restricted Task Force X proposal](docs/GOON_TASK_FORCE_X_RECRUITMENT_DESIGN.md) | Canon/continuity context, original five-condition assessment route, scoped government knowledge, voluntary decisions, alternatives and future dependencies; no implemented recruitment |
| [Narrative design bible](docs/GOON_NARRATIVE_DESIGN_BIBLE.md) | Player fantasy, tone, 16 design areas, feature-status legend, and originality boundaries |
| [Criminal career web](docs/GOON_CRIMINAL_CAREER_WEB.md) | Nineteen overlapping specializations, lawful work, informing, rehabilitation, retirement and three worked scenarios |
| [Conditional opportunities](docs/GOON_CONDITIONAL_OPPORTUNITIES.md) | Eligibility, demand, recorded probability, expiry and viable careers without guaranteed villain meetings |
| [Faction and employer matrix](docs/GOON_FACTION_EMPLOYER_MATRIX.md) | Eleven proposed employer cultures, entry, pay, risk, advancement, and consequences |
| [Rogues gallery registry](docs/GOON_ROGUES_GALLERY_REGISTRY.md) | 36 research entries, including the Terrible Trio group; Jane Doe added, Calendar Man and Crazy-Quilt enriched, no guaranteed active roster |
| [Organization/leadership catalogue](docs/GOON_FACTION_EMPLOYER_MATRIX.md#mission-029-organized-crime-candidate-registry) | 26 source-qualified family, gang, network and umbrella records; proposed statuses, continuity reconciliation and a bounded future integration contract |
| [Minor criminal ecosystem](docs/GOON_MINOR_CRIMINAL_ECOSYSTEM.md) | Major factions, minor crews and individuals; original workers and rise/fall/exit proposals without universal territory simulation |
| [Joker recruitment contract](docs/GOON_JOKER_RECRUITMENT.md) | Original campaign proposal: street association differs from formal Arkham/direct-encounter initiation |
| [Metropolitan atlas](docs/GOON_GOTHAM_ATLAS.md) | Original 8-region geography and source/continuity decisions; no traced or rendered map |
| [Location registry](docs/GOON_LOCATION_REGISTRY.md) | 48 neighborhoods and 120 POIs with IDs, access, economy, security, civilian/criminal activities and potential contacts |
| [Travel network](docs/GOON_TRAVEL_NETWORK.md) | Source design for M014's implemented modes, closures and separate TU allowance; vehicles/schedules deferred |
| [Map/simulation integration](docs/GOON_MAP_SIMULATION_INTEGRATION.md) | Preserve the three territory accounts while adding optional hierarchical geography through a future reviewed migration |
| [Career geography](docs/GOON_CAREER_GEOGRAPHY.md) | Location-dependent work, civilian life, care and meaningful commitments rather than commute grind |
| [Map visual specification](docs/GOON_MAP_VISUAL_SPEC.md) | Future layered views with player-knowledge boundaries; no GUI or map image |
| [Villain influence and recovery](docs/GOON_VILLAIN_INFLUENCE_SYSTEM.md) | Fictional exposure, coercion, resistance, consent and credible recovery; no clinical implementation |
| [Institutions and recovery](docs/GOON_INSTITUTIONS_AND_RECOVERY.md) | Distinct Blackgate, Arkham, voluntary care, review and reentry paths with continuity/agency rules |
| [Gameplay principles](docs/GOON_GAMEPLAY_PRINCIPLES.md) | Sourced reference-game lessons, meaningful-choice gates, current limits, and manual scenarios |
| [Content architecture](docs/GOON_CONTENT_ARCHITECTURE.md) | Proposed definition/state separation and service integration; no content migration |
| [Deferred combat design contract](docs/M014_COMBAT_DESIGN_CONTRACT.md) | Retained historical M014 proposal; future milestone unassigned, no combat implementation |
| [Project state](PROJECT_STATE.md) | Runtime capabilities, compatibility, limitations, and next review |
| [Final integration audit](docs/M013_1_FINAL_INTEGRATION_AUDIT.md) | Verified corrections, compatibility findings, reproducible graph/document checks and conditional merge gates |
| [M014 validation](docs/M014_VALIDATION_REPORT.md) | Executed regressions, historical compatibility, real CLI walkthrough and reproducible navigation campaigns |
| [M014 final audit](docs/M014_FINAL_AUDIT.md) | Independent acceptance gates, corrections, compatibility results and PR disposition |
| [M015 daily-life contract](docs/GOON_M015_DAILY_LIFE_CONTRACT.md) | Implemented scope and historical readiness proposal |
| [Consequential choices](docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md) | Stable choices, known prerequisites, settlement, branches and recovery |
| [M015 validation](docs/M015_VALIDATION_REPORT.md) | Executed campaigns, regressions, compatibility, economy findings and limits |

M013.1 preserves the `gotham-underworld` repository name, Python modules, package
layout, save filenames/identifiers, and historical milestone documents. The CLI
banner and prompt use the new working title; historical and workflow labels still
identify Gotham Underworld. Technical renames require a separately approved
migration plan. None of the proposed DC employers is added to the executable or
substituted for an existing faction.
M014 is navigation only; combat and the prologue remain future design work.
The rogues addendum changes documentation only. Its roster is not assumed to
coexist in every continuity, and no minor crew automatically becomes a district
owner. Formal Joker initiation is optional and conditional; a career can finish
without it. That addendum implemented no rogue, recruitment gate or save field.
The M013.1 city-atlas design supplied 176 place records (8 regions, 48 neighborhoods,
120 POIs) and an original network specification, now loaded as M014 content.
Geography, faction territory, minor-crew influence, properties and police coverage
are separate. Existing jobs, legal rules and faction accounting retain M013 behavior;
M014 implements the bounded subset documented below, with a CLI and no GUI.

## World navigation and the playable slice

New careers start at **East Side Housing Cooperative** in Upper East Side,
with recorded home access and the existing $40 start. Enter:

```text
look
nearby
route p032
travel p032
look
join 1
job courier
travel home
wait
save
quit
```

The store visit and return cost **2 travel TU**; the existing courier costs one
gameplay action. Saving/resuming preserves the home, location, spent TU, jobs and
day. `look` inspects a frontage, not a shop transaction or institutional admission.
The optional M015 slice below adds local wages and room obligations. No prologue,
health, combat or NPC scheduling is implemented.

| Navigation command | Behavior |
| --- | --- |
| `look [place]` | Current or known place metadata, entry requirements and free help |
| `nearby`, `places` | Known local destinations or public atlas; private homes need permission |
| `route <place> [mode]` | Detached preview of outbound/return TU and affordability |
| `travel <place> [mode]` | Atomic movement; before mobility adoption: `auto`, `walk`, `bus`, `rail`, `ferry`; adopted profiles below |
| `enable_navigation <neighborhood>` | Historical career opt-in at a public hub, active after next `wait` |

Use short IDs such as `p032`/`n13`, their full stable IDs, or `home` when a recorded
home exists. Regions are containers, not travel destinations. All mutations use
the game service. Read APIs are `location_report`, `nearby_destinations`,
`known_places`, and `plan_route`; commands take named string arguments, for example
`execute_command(world, 'travel', destination='p032', mode='auto')`.

Travel uses a separate **18-TU/day** initial policy and zero daily gameplay actions.
Walking/transit costs follow the atlas, with one TU per transit-mode boarding.
A completed local journey costs at least one TU, deliberately bounding the earlier
zero-cost-approach proposal. Inspections remain free; no travel grants rewards.
Known failures reject without mutation. A hidden closure stops a valid journey
at its last safe node and charges only its traversed prefix. Controlled closures
expire within two advanced days; there is no closure-editing player command or
random incident generator. Direction, mode and restricted entry are enforced.
Free visitors retain lawful egress; travel never bypasses custody or admits a
patient/prisoner. Cars, boats, schedules and emergency transport remain future work.

Not every journey fits eighteen TU: n01→n40 costs 19 one way. Preview the return,
choose nearby work or an explicit safe waypoint. Waiting advances the real city
once and refreshes both allowances; loading/reporting never does. Help, saving,
reports and explicit waiting remain available when broke or exhausted. Existing
jobs/missions remain location-independent, preserving legacy RNG and accounting.

Historical saves load with **no invented location/home** and unchanged budgets,
resources and events. Opt in explicitly, for example `enable_navigation n13`,
then `wait`. No navigation is imposed by migration or loading. The independent
`navigation_version: 1` extension pins atlas/rules/content fingerprint; missing or
incompatible required content fails clearly. All three existing territory accounts
remain authoritative; 176 places do not multiply income or warfare turns.

## Optional station mobility — M016-A

New and historical careers keep their existing navigation until explicit
adoption. Loading or inspecting never enrolls a career. Historical careers
without navigation first use `enable_navigation n17`, then `wait`.

| Command | Behavior |
| --- | --- |
| `mobility` | Detached status, adoption availability, stations and known service disruption information |
| `adopt_mobility` | Schedule mobility once; it activates during the next explicit `wait`, with no resource grant |
| `route <place> [profile]` | Read-only door-to-door TU/fare quote, policy return and free-return alternatives |
| `travel <place> [profile]` | Commit the quoted journey atomically using the existing CLI verb |
| `receipt <request-id>` | Inspect a detached accepted-request receipt without repeating effects |

After activation, profiles are `auto` (alias `fastest`), `free`, `walk`, `bus`,
`ferry`, `monorail`. Legacy abstract `rail` is retired **only for adopters**.
Old rail journeys and all non-adopted routing keep their original interpretation.
The pilot links **p039 Highbridge Metro Stop → p071 South Gate Subway Stop**,
following n17–n18–n23–n22–n30 via four existing atlas corridors. Only these two
public frontages have monorail gates; neighborhoods cannot board directly.

The **7 TU/$2** scope is frontage-to-frontage: zero-cost gates/alighting,
1-TU boarding and 6-TU ride. Actual approach/onward travel is additional. From
home, a walking-only approach to p039 adds 4 TU; `free` can use the existing
3-TU bus approach separately. Current p039↔p071 bus costs **8 TU/$0** each way;
walking costs 18. No fare is charged for merely previewing or reaching a station.

```text
mobility
travel p039
adopt_mobility
wait
route p071 monorail
travel p071 monorail
route p039 bus
travel p039 bus
save
```

The two committed station trips above use **15 TU/$2**, zero gameplay actions
and no day advance. Return previews target the journey origin by default,
preserving `route` semantics. The API can specify another `return_to`. They use
the actual cash/TU left after outbound settlement and distinguish policy return
from a free alternative. An outbound cap limits that transaction, not the actual
resources available for a later return command. Returns remain conditional on
known access/disruptions; a quote is not a reservation.

Known closures affect planning. An unknown underlying rail closure is observed
at the departure station before boarding; only an actual approach prefix is
charged, never the untraveled fare/ride. Free bus/walking remain available where
the atlas permits. With $0 and insufficient TU for the return, inspect/save and
explicitly wait; only a real day transition restores the normal 18 TU and three
actions. Waiting can expire an existing promise/offer. No paid rescue or vehicle
purchase is required; restricted institutions and custody remain enforced.

Service integrations use `execute_command(world, 'enable_mobility',
overlay_id=OVERLAY_ID, request_id='client.adopt.1')`, then `advance_day(world)`.
For travel, call `mobility.plan_route(world, 'p071', 'monorail')` and pass its
`arguments` to `execute_command(world, 'journey', **quote['arguments'])`.
Reuse the same request ID only to detect a retry: duplicates reject unchanged;
`mobility_receipt` retrieves the old receipt. Route views and responses are detached.

Outer save version stays 1. Opt-in pairs `navigation_version: 2` with
`mobility_version: 1`; pending routing remains rules1 until activation, then
rules2. Schema1 travel events are unchanged and checked at the legacy checkpoint;
schema2 events record typed legs, resource deltas, discoveries and charge/receipt
IDs. The base atlas fingerprint stays unchanged. Separately pinned overlay:
`d59fe323290fd1216d8b5e1ffdcde5924b123cedc0404ce22215d538779ec7ee`.
Missing/changed required content fails clearly; old binaries reject nav2 instead
of ignoring mobility. Existing atomic replacement/backup behavior is reused.

See the [implementation/validation report](docs/M016_A_IMPLEMENTATION_VALIDATION.md),
[architecture](docs/M016_MOBILITY_ARCHITECTURE.md),
[acceptance matrix](docs/M016_MOBILITY_ACCEPTANCE_MATRIX.md) and
[risk register](docs/M016_INTEGRATION_RISK_REGISTER.md). Repeat deterministic
campaign evidence with `python -B mobility_campaigns.py --days 365 --seeds 17 42
--resume-every 30`. These stress commutes are test policies, not reward-generating
missions. Vehicles, theft, licensing, impound, expanded schedules and the full
prologue remain unimplemented. The broader M016 milestone is not complete.

Local M016-A verification: **336 tests pass** (332 preserved plus4 metadata-repair cases), with
seeded365-day replay and final30-day daily disk-resume checks. Exact commands,
hashes, limitations and the distinction from existing GitHub CI are in the report.

## The Night Shift — optional independent world incident

After `settle_in` activates, `incidents` explains enrollment; `enable_incidents`
adopts exactly one original shop-alarm episode, starting on a future day. This
adds neither a global clock nor extra actions/TU. The alarm occurs and the shop
resolves it even if you never learn of it. A local public notice at p032, or Tess
at n13 after an actual kept-promise reference, can disclose a report of the alarm.
Reading `incidents` does not acknowledge it or reveal its cause.

Use the stable incident ID shown by `incidents`:

```text
discover_incident <incident-id> public_notice
incident_choose <incident-id> offer accept
incident_choose <incident-id> work verify
incident_choose <incident-id> report disclose
```

Discovery costs no action. Acceptance, inspection, lawful safety help, disclosure
and a later follow-up each cost one of the existing three actions; refusal and
lawful withholding cost zero and cannot repeat. Travel remains explicit, costing
the existing 18 TU allowance. The journal gives the first evidence day and deadline:
inspection on the first evidence day pays $12, on the next $6 for partial work,
and on the last $0 for unusable evidence. Only a complete inspection reveals the
true cause. Unfinished accepted work causes one bounded owner reaction; unknown
or refused work creates no debt, crime or global reputation penalty.

Alternative: choose `offer help` for unpaid lawful safety work and a different
reference. Complete private work, actual disclosure and safety help can each open
a different one-shot $8 follow-up after independent resolution. Inspect `incidents`
for current eligible stages/options; `followup work` is never an infinite wage.
Ada Quinn is an original shop owner, using M015's existing contact/standing
authority; no relation to a DC character is implied. Compensation changes only
player cash and is observed by the existing life ledger. The Civic Police desk
records scoped incident facts, not fabricated job evidence, charges or guilt.

Version-1 optional incident state pins definitions, replays its transitions during
validation and checks delegated payments/memories. Historical careers do not
adopt on load. New readers preserve historical saves; older executables are not
supported for advancing incident-adopted saves because they lack this phase.
Use the current executable throughout an adopted career. See the implemented
section of [After Dark](docs/GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md),
[choice contract](docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md), and
[Mission 016 evidence](docs/M017_NIGHT_SHIFT_VALIDATION.md).

## The Wrong Notice — M018

After daily life activates, explicitly enroll with:

```text
incident_definitions
enable_incident goon.incident.wrong_notice.v1
incidents
```

Enrollment costs nothing and refreshes neither actions nor travel. It schedules
one future neighborhood delivery dispute. It does not enable Night Shift for
you; the existing `enable_incidents` command still enables only Night Shift.
Use `incidents <incident-id>` for one detached player journal, or `incidents`
for both when both are adopted. Discovery and choices use the same commands:

```text
discover_incident <incident-id> public_notice
incident_choose <incident-id> verify ledger
incident_choose <incident-id> response notify_desk
incident_choose <incident-id> repair warn_group
```

The public board is at p032; Sam's tenant group and Nora's delivery desk are at
n13. The board and handbill initially give conflicting dates. Hearing either
does not reveal the true delivery day. Verification costs one action at the
desk after its ledger arrives. Posting a verified correction reaches the board
only; notifying Nora orders a board correction for **tomorrow**, and warning
Sam reaches only his group. Each costs one action. Correcting late cannot undo
delivery-day harm. Ordinary jobs, home access and lawful careers remain available.

Passing on the unchecked date saves checking effort but may later cost Sam's
trust. A verified retraction costs another action and earns no bonus. If the
ledger shows a vacancy, requesting it instead of helping costs Nora's trust and
opens one optional $5 standby shift after resolution. There is no guaranteed
money for helping. Refusing is free and creates no promise or debt. Ignoring the
incident does not prevent independent delivery/reconciliation.

The issued circular can be read at n13 during the three days following resolution
(`aftermath read`, zero actions). The journal and contact summaries do not learn
private reactions or the final review remotely. Full saves/debug snapshots remain
world truth; a frontend should use player reports and projected service events.
Both incidents use explicit dispatch and a small shared lifecycle, not roster
jobs or a quest language. Historical saves gain no notice state until explicit
enrollment. See [architecture](docs/GOON_CONTENT_ARCHITECTURE.md),
[After Dark](docs/GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) and
[M018 validation](docs/M018_WRONG_NOTICE_VALIDATION.md) for costs, limits and evidence.

## Institutional intake — M019

After daily life activates, use `institutions` to inspect terms and
`enable_institutions` to adopt explicitly. Old saves gain nothing automatically.
The Neighborhood Civilian Desk is at public n13; the GCPD Intake Desk uses the
existing p044 public counter. They have separate records and one-/two-day
processing delays. The civilian desk handles delivery administration and local
safety; police intake logs alarm observations without deciding guilt or creating
arrests, warrants or cases. Names and mandates are separate local content data.

```text
institutions civilian
institution_submit civilian <observed-source-id>
institution_followup civilian <incident-id>
institution_correct civilian <known-report-id> <documented-source-id>
institution_withhold intake <incident-id>
```

Source IDs come from `institutions [civilian|intake]`. Submitting an observed
notice can still pass on bad information. Checking the old incident's ledger or
doing a genuine alarm inspection supplies stronger evidence. A desk learns only
what reaches it; correcting its record does not update every resident or the
other institution. Public-source rounds and owner forwarding continue without
player involvement, while unanswered records close for insufficient information.

Submissions, corrections and unread local follow-ups each cost one shared action;
withholding is free and private. No reporting wage or allowance refresh exists.
A contradicted, uncorrected report restricts that desk's unchecked submissions;
a verified correction restores access after processing. Ordinary work, housing
and legal choices remain available. A documented civilian matter can provide one
dated correction copy recorded in its response, not a cash/inventory reward.
That received copy appears as a documentary source and can repair the desk's
old record even after the original incident's evidence window has closed.

Remote views retain what the player actually received. Read-only inspection
does not acknowledge replies; use an explicit local follow-up to receive them.
Desk responses are separate secondhand records, not retroactive inspection credit
in old incident journals. See the canonical [institution contract](docs/GOON_INSTITUTIONS_AND_RECOVERY.md)
and [M019 validation](docs/M019_INSTITUTIONAL_RESPONSE_VALIDATION.md).
M019 and its independent hardening pass **476 tests** (426 preserved plus 50
institutional tests). PR #20 and merged-master CI passed. Two
365-day institutional disk-resume campaigns and all six recorded historical
Night Shift/Wrong Notice/mobility fingerprints passed; exact evidence and limits
are in that report. M020 remains unpublished; no M020 GitHub CI is claimed.

## Living in the neighborhood — M015

Daily life is **explicitly optional** for every career, including a new one. Run
`life` to inspect terms, then `settle_in` at p031/home or n13 to accept them.
Offers activate after the next `wait`. Starting on day 0 preserves the real $40
and makes the first $30 cooperative room contribution due on day 7. Every later
review is seven days apart. Available cash is charged, prepaid contributions are
applied once, and an unpaid balance never exceeds $30. Basic home access continues
in grace, with no stacked rent/fees while that balance remains. One maintenance
opportunity per unpaid review can reduce it by up to $10 for one action, without cash.

| Command | Behavior |
| --- | --- |
| `life` | Detached terms, cash history, room dates, promises and a state-grounded thought |
| `settle_in` | Accept the disclosed room arrangement; activate next day without budget refresh |
| `home`, `pay_room` | Inspect home/deadlines, or prepay/pay a bounded amount at home |
| `contacts` | Tess and Cal's known roles, standing and observed interaction memories |
| `opportunities` | Finite local offers with stable IDs and opening/expiration days |
| `choices <id>` | Context, speaker, available options, known disabled reasons and action costs |
| `choose <id> <option-id>` | Revalidate and resolve once through the game service |
| `choose <id> A` | Use the letter mapped by your last `choices <id>` display; stable IDs remain authoritative |

First-day example, from a fresh home career:

```text
life
settle_in
wait
choices goon.choice.0.promise
choose goon.choice.0.promise promise
travel p032
choices goon.choice.0.opening_shift
choose goon.choice.0.opening_shift A
travel home
home
save
```

On day 2, inspect `goon.choice.0.crossroads`. A lawful shift pays $20 at the store;
keeping Tess's promise at home pays nothing but earns a reference; negotiation
moves the favor once to day 4; withdrawal forgoes the morning roster. These share
a disclosed roster slot. Cal's collection option appears only after his own
introduction at n13 and requires an explicitly chosen existing faction. It calls
the original legal job resolver once: up to $60, failure, heat and possible case
consequences. His observed successful referral may open quieter courier work.
No contact learns unrelated private work or police facts from these menus.

The referenced stock-audit shift pays $25 for two actions; ordinary repair work
pays $20 for one. Known follow-up offers also depend on current recorded standing;
broken commitments can put a reference on hold without removing basic work.
Offers expire and each settles once. Refusal is free, the shared
three-action/18-TU rules remain, and a week has a finite roster rather than a wage
button at every location. Save/load, reports and staying home grant no resources.
All five branches—lawful, criminal, relationship-first, low cash, and mixed—are
reproducible with `python -B daily_life_campaigns.py --days 7 --resume`.

Existing saves load without daily-life state or retroactive rent. Pre-navigation
careers first use `enable_navigation n13` and `wait`, then accept the room locally.
An unknown home can become p031 through that explicit agreement without moving
the player. An existing different home is never silently overwritten. The optional
`daily_life_version: 1` extension pins its own content and validates receipts,
cash, choices, promises and contact memories. Existing jobs remain available and
retain their rules. The five-chapter playable prologue remains future content.

## Ordinary work and support — M020 (local)

After `settle_in` activates, visit home or n13 and explicitly use
`enable_ordinary`. New terms activate after the next `wait`. Loading an older
career does not adopt them or award employment credit for earlier shifts.

```text
ordinary
enable_ordinary
wait
ordinary_choices goon.ordinary.batch.0
ordinary_choose goon.ordinary.batch.0 work
```

The week number belongs to the new arrangement; inspect `ordinary` for actual
IDs and windows. Existing `opportunities`/`choose` still provide store shifts,
personal promises and room maintenance. `home` now also shows the adopted plan.

| Decision | Terms and lasting consequence |
| --- | --- |
| Existing store repair work | $20 for one action at p032; no employment prerequisite. Future actual completions build bounded employment standing, without paying again or duplicating Tess's memory. |
| Home repair kits | One separate funded allocation per ordinary week; two actions at home, $24 or $28 with employment standing 3. Requires one observed completion or existing room arrears. Every third allocation is visibly cancelled for supplies, determined from seed/week; dependable store shifts remain. |
| Request a later delivery | One action and one request at the home ledger. Tess's posted terms accept standing 1, or refuse standing 0 without a relationship penalty. Acceptance pins the wage and tomorrow's two-day delivery window. No advance wage; missed/withdrawn commitments lose at most one employment and one Tess standing. |
| Tess support advance | $20 once per career, one action at home on ordinary roster days 0, 2 or 5. Needs arrears, or cash below $30 with review within two days. Repay exactly $20 within seven days, using one action at home. Late status creates one bounded memory; no interest or automatic collection. Repayment closes the debt but unlocks no second advance. |
| Decline | Free, once per offer; no money, promise or morality penalty. Refusing support creates no debt. |

This extends the **same** cooperative room: $30 every seven days, actual
prepayment, arrears capped at $30, one maintenance credit per existing review,
and continued basic access. The plan displays the next review and records an
advance notice within two days. It creates no eviction system or new rent charge.
Employment standing caps at 6; personal standing still uses the existing Tess
record. Home work reduces commuting, while limited allocations keep wages bounded.
Three actions and eighteen travel units per day remain separate and unchanged.
As with existing dated promises, a due day begins at the day transition: repay
before the `wait` that reaches it. Withdrawal from an accepted reservation is
available immediately; paid completion still waits for its agreed date.

No incident participation or criminal work is needed. Institutions do not learn
about employment, help or debts automatically. Save compatibility is old-to-new;
use an M020-capable executable after adopting its independent version 1 state.
See the [daily-life contract](docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md#m020-extension--ordinary-work-housing-and-support)
and [executed validation](docs/M020_ORDINARY_GOTHAM_VALIDATION.md).

## Start or resume a career

From the repository directory in PowerShell:

```powershell
python gameplay.py
python gameplay.py --load
python gameplay.py --seed 17 --save career_second_save.json
python gameplay.py --load --save career_second_save.json
python -B -m unittest discover -s tests -v
```

The default save is `career_save.json`. Starting a new game refuses an existing
save path: resume with `--load` or choose another `--save` filename. A file
appearing after startup is also protected on the first save.

`save` persists the career; `quit` saves before exiting. EOF or Ctrl+C at the
prompt exits without saving unsaved changes. The seed initializes a new career;
loading retains the seed stored in the save.

## Career commands and actions

| Command | Behavior |
| --- | --- |
| `help`, `status` | Commands, cash, heat, affiliation, reputation, cases, and remaining actions |
| `factions`, `join <1-3>` | View or join an existing faction; recruitment is free |
| `jobs`, `job courier`, `job collection` | View jobs or attempt one; each attempt costs one action, including failures |
| `districts`, `missions` | Inspect districts and mission numbers |
| `mission <kind> <district-number>` | Scout, fortify, or expand; costs one action plus its cash price |
| `relationships`, `strategy` | View NPC policies and faction plans |
| `legal` | Inspect heat, police attention, cases, and committed responses |
| `lay_low` | Reduce heat; one action, no cash cost, once per day |
| `cooperate <case-id>` | Document evidence and reduce the eventual conviction fine |
| `contest <case-id>` | Pay for a two-day review of a documented pending case |
| `accept <case-id>` | Admit a pending/charged case and resolve consequences immediately |
| `intel`, `briefing [day]`, `events` | View city reports and recent events |
| `wait` | Advance exactly one day and refresh the daily allowance |
| `save`, `quit` | Save the career; quit also exits |

There are **three shared actions per day** for jobs, district missions, and legal responses.
The existing one-district-mission-per-day restriction also applies. Reports,
recruitment, saving, and waiting are free. Invalid, unaffordable, or exhausted
commands do not change game state or consume RNG attempts.

Loading does not refresh actions. Legacy migration counts recorded jobs and
district missions on the current day, capped at three.

## Heat, exposure, and legal choices

Player commands keep effective heat between **0 and 100**. Attention is derived
from heat, not hidden rolls:

| Heat | Attention | Added job failure / collection witness chance | Extra daily evidence |
| --- | --- | --- | --- |
| 0–19 | Low | 0 percentage points | 0 |
| 20–49 | Elevated | 5 percentage points | 0 |
| 50–79 | High | 10 percentage points | 1 |
| 80–100 | Critical | 15 percentage points | 1 |

Extra investigation applies only to existing documented pending cases. Heat
alone never creates a case or authorizes arrest. NPC acceleration still requires
a documented case and retains its cooldown.

Courier work pays $25 on success and creates no new criminal case. It adds one
heat only on failure. Collection pays $60 but adds 2/3/4/5 heat across the four
tiers, plus one on failure. Witness chance starts at 35% on success or 65% on
failure, adds the tier modifier, and caps at 90%. Job failure chance uses existing
reputation plus the modifier, capped at 75% for player commands. Outcomes use the
existing seeded draws without rerolls or global RNG. Failed collections retain
their existing faction consequences.

`legal` shows case IDs and evidence. Each response costs one daily action:

| Action | Prerequisites and cash cost | Effects |
| --- | --- | --- |
| `lay_low` | Free, not detained, positive heat, once/day | Heat -12; existing evidence remains |
| `cooperate <id>` | Free, not detained, documented pending witness case | Heat -8, evidence +1, eventual conviction fine $30 instead of $50; court reduces heat by 4 |
| `contest <id>` | $20, not detained, documented pending witness case | Freeze that case's ordinary/NPC investigation until review two days later; evidence <=1 dismisses it; stronger evidence continues, adds 3 heat, and retains the normal $50 conviction fine |
| `accept <id>` | Pending/charged case; cannot bypass a different charged case | Immediate admission and conviction, fine $35, heat -10, custody released; no city-day advancement |

One response is committed per case; it cannot be stacked or switched. Contesting
does not stop other investigations or city activity. Fines are capped by cash on
hand and never create debt. Ignoring a case preserves automatic court handling
on arrest, so an exhausted allowance cannot trap the player in custody. Lay low
requires no cash. A complete day without collection/crime provides another 2 heat
reduction on the following daily tick. These are simplified game rules, not a
model of real legal procedure.

The persisted `legal_version: 1` / `legal` extension stores responses, review
dates, daily processing markers, and unique outcome records. New outcomes record
their dates, assessed fines, actual payments, and response. Migrated convictions
and dismissals retain unknown historical dates/fines as null. No warrants,
probation, parole, supervision, undercover agents, or vigilante encounters are
implemented; later versions can add sections without character-name rules.

## Faction economics and competition

From day two in a new career, factions use the economic profiles saved in
`competition.profiles`, bound through `competition.factions`. Existing careers
begin these rules on the day after migration, without replaying earlier turns.
The first-day income/mobilization contract and low-level legacy resolvers remain
compatible. Player commands and M012 heat/legal rules keep their existing budget.

Profiles are data, not character-name policies. New organizations can bind to an
independent profile without changing the engine. Defaults are copied into each
career, so customizing one save does not change another or the global defaults.
No new DC organizations or story content are included.

| Faction / profile | District revenue | Recovery income / power | Recruitment cost / gain | Treasury / recovery cap |
| --- | --- | --- | --- | --- |
| Harbor / `trade_network` | 125% | $6 / +2 | $6 / +7 | $240 / $60 |
| Carnival / `street_network` | 100% | $8 / +3 | $4 / +6 | $180 / $50 |
| Iron / `industrial_network` | 135% | $5 / +2 | $5 / +9 | $220 / $70 |

| Profile | Attack / defense cost | Expansion reserve | Minimum attack power | Defense / consolidation threshold |
| --- | --- | --- | --- | --- |
| Trade | $12 / $8 | $36 | 25 | 45 / 75 |
| Street | $10 / $9 | $28 | 20 | 35 / 65 |
| Industrial | $13 / $7 | $40 | 30 | 55 / 85 |

Daily district revenue is `max(1, wealth // 15) * revenue_percent // 100`,
credited only up to the treasury cap. Upkeep is operating cost + holdings times
holding cost + power divided by the upkeep divisor (integer division). Defaults
use $1 operating cost, $1 per holding, and divisors 35/40/30. Payment is limited
by available cash. Fully funded upkeep restores one power; a shortfall loses one.
Existing above-cap reserves are retained and spent normally, while receiving no
additional income until they fall below the cap.

Each faction gets **one operation per day**, in a deterministic rotating order
derived from seed, day, and sorted faction identifiers:

- **Recover:** spend the turn rebuilding an off-map network; add the profile's
  recovery income up to its recovery cap, and bounded organizational power.
- **Regroup:** pay the recruitment cost for faster power recovery.
- **Defend:** pay for control restoration in a threatened holding.
- **Expand:** pay for an offensive against an explicitly selected rival district.
- **Consolidate:** pay the defense cost for slower control improvement and some
  recruitment when there is no funded expansion target.

Low operating strength prioritizes regroup/recovery. Otherwise threatened owned
districts take priority, then insufficient reserves trigger recovery, funded
rival targets permit expansion, and secure holdings permit consolidation or
recruitment. Recent player expansion pressure affects defense assessment.
Invalidated targets, missing funding, changed profiles, or exhausted recovery
capacity produce explicit fallback reasons. Stale/missing plans are reassessed
from current resources and record that fallback.

Pressure reduces district control by 1–3 daily, stopping at one; it cannot hand
territory to an unfunded challenger. Modern transfers require a paid offensive
or player expansion, exhaust control, and reset it to 35 through one shared
ownership operation. The compatibility first-day/legacy pressure claim also
requires money and power. Attacks consume one attacker power and up to two
defender power, abstract organizational losses rather than a combat system.
All power changes remain within 0–100. Legacy seeded feuds continue; upkeep,
recovery, and recruitment counter their former long-term power collapse.

Faction income, upkeep, operations, captures, and fallbacks have structured
before/after values. `factions`, `strategy`, `intel`, and `briefing` expose the
results through detached reports. District numbering and targeting use stable
sorting rather than dictionary insertion order. Modern economy/strategy/warfare
resolvers share the existing daily markers and do not execute twice in a day.

Reproduce the idle-city audit with `python -B faction_campaigns.py`. See
[M013_SIMULATION_REPORT.md](M013_SIMULATION_REPORT.md) for the actual four
365-day campaigns and one 1,000-day campaign. Iron leads every one-year sample;
Harbor leads at day 1,000 in seed 42. All factions remain operational, including
displaced organizations. Tests enforce bounds and recovery, not equal outcomes.

This remains a three-district economy with static wealth and abstract power.
Defensive identity has a strong early advantage in the tested seeds; recovering
factions often approach maximum readiness while still poor or displaced. There
is no elimination mechanic: default profiles all have a funded rebuilding path.
No rank-based handicap, forced turnover, or equalizing grant is applied.
The economic/strategic roster is configurable; the retained legacy feud sampler
still uses the original three gangs. Expanding that sampler is separate from
adding economic profile bindings.

## Safe saves and compatibility

M011 uses `save_version: 1`; unversioned M001-M010 careers receive additive
defaults. Unknown fields are retained. Unsupported save/subsystem versions,
malformed nested data, duplicate case IDs, invalid references, and inconsistent
custody state are rejected before play.

Versioned M011 saves must contain their required subsystem state. Missing
territory or relationship data is an error rather than a reason to reset it.
Migrations do not replay events, pay old income, or execute old faction turns.
M012 retains that outer contract and independently versions legal state. M001-M011
careers initialize it without refreshing actions or rewriting historical events.
Unsupported legal versions and inconsistent responses, records, or legal/heat
event metadata are rejected; unknown extension fields are retained. An old raw
heat counter above 100 is preserved on load, displayed as effective heat 100,
then normalized with an audit event on the next successful player command.
M013 adds `competition_version: 1` with persisted economic definitions/bindings
and an activation day. M001-M012 careers keep their existing values and event
history on load; competition starts on the following advanced day. Unsupported
versions, missing profile state, invalid economic parameters, and inconsistent
economic event metadata are rejected. Profile edits are local to that career.

Saving stages and flushes UTF-8 JSON in the destination directory, then uses
`os.replace` to publish it. Overwriting first preserves the previous valid bytes
at `<save filename>.bak`. If staging or backup fails, the destination is untouched.
If replacement fails, the old destination and a recoverable backup remain.
An invalid existing destination cannot replace a good backup.

To recover a damaged career, preserve it separately, copy its `.bak` file back
to the original filename, then resume with `--load`. Recovery is explicit; the
loader does not silently substitute an older save.

First-save publication uses a hard link to avoid replacing a competing file.
The destination filesystem must support that operation and same-directory
replacement; unsupported operations fail without an unsafe overwrite fallback.
Save directories must exist. Saves assume one writer per career; cross-process
conflict resolution is not implemented. Power-loss durability depends on the
operating system and filesystem.

## Architecture and extension points

`game_service.py` is the player-facing boundary for the CLI and future interfaces:

```python
from game_service import (
    create_career, load_career, save_career,
    execute_command, advance_day, snapshot,
)

world = create_career(seed=42)
execute_command(world, 'join', faction='Harbor Syndicate')
result = execute_command(world, 'job', kind='courier')
advance_day(world)
view = snapshot(world)  # Detached; edits cannot affect the career.
save_career(world, 'career_example_save.json', overwrite=False)
```

Stable command IDs are `join`, `job`, `mission`, `wait`, `lay_low`, `cooperate`,
`contest`, and `accept`; arguments are named string fields. Legal case IDs are
positive number strings: `execute_command(world, 'contest', case_id='1')`.
Successful commands return detached results, emitted events,
a persisted sequence number, and remaining actions. A `player_command` event
records the command ID, arguments, actor, and action cost. Consumers should use
event kinds and structured fields rather than parse narrative messages.

Commands execute against a private world copy and commit only on success.
Callers may retain the root dictionary, but should use snapshots rather than
retain live nested references across commands. Copying favors correctness over
large-world performance at this prototype scale.

| Layer | Modules |
| --- | --- |
| CLI and command boundary | `gameplay.py`, `game_service.py` |
| Save contract, defaults, persistence | `career_state.py`, `career_persistence.py` |
| Base world, events, legacy feuds and courts | `simulation.py` |
| Jobs, investigation, NPC relationships/actions | `consequence_engine.py`, `relationship_engine.py`, `npc_actions.py` |
| Heat policy, legal choices, profile schema | `legal_engine.py`, `legal_state.py` |
| Economic identities and modern faction operations | `faction_profiles.py`, `faction_competition.py` |
| Shared ownership mutation | `territory.py` |
| Economy, missions, strategy, warfare | `city_economy.py`, `district_missions.py`, `city_strategy.py`, `faction_warfare.py` |
| Detached reports | `city_intelligence.py`, strategy assessment/summary |
| Local geography and navigation | `location_registry.py`, `navigation.py` |
| Contextual choices | `choice_engine.py`; stable records, visibility and effect callbacks |
| Neighborhood rules and save invariants | `daily_life.py`, `daily_life_state.py` |
| Original local content and presentation | `content/neighborhood_life_v1.json`, `life_content.py`, `life_presentation.py` |
| Independent incident lifecycle and dispatch | `incident_lifecycle.py`, `incident_dispatch.py`, `incident_state.py` |
| Explicit incident adapters and pinned content | `world_incidents.py` / `incident_content.py`; `wrong_notice.py` / `notice_content.py`; separate JSON definitions |
| Source-backed institutional intake and replay | `institution_sources.py`, `institutional_response.py`, `institution_state.py`; `institution_content.py` / `content/institutions_v1.json` |

Daily order is: base clock/feuds/legacy investigations, legal reviews/quiet-day
cooling, career investigations with heat scrutiny,
NPC actions, economy, planning, warfare, court, navigation reset, then the optional
daily-life phase, sorted adopted incident adapters, then optional institutional intake. Investigation runs once per
case per day; contested cases defer ordinary and NPC evidence until review.
NPC acceleration otherwise retains its existing cooldown.
Warfare revalidates current targets; invalidated or unfunded plans emit an
explicitly explained hold action.

The legacy `gameplay.job` reducer remains unbounded with its original risk/heat
rules for existing tools/tests. Player interfaces must use `execute_command` for
M012 risk and legal rules. Explicit case choices are also honored by the legacy
daily reducer.
The original `python simulation.py --days 10 --seed 42` batch demonstration
remains available; it is not the career interface.

Legacy content definitions and named NPC policies remain in their original
modules. M015's two original contacts and opportunity text use a separate local
content pack; they are not added to the faction NPC policy roster. Future registries should separate stable
IDs from display names and keep character/faction, dialogue, mission/event,
asset, and progression data separate from mechanics. New systems should extend
the command/event interfaces and explicit additive save migrations, without
requiring a particular fictional property.
The [content architecture proposal](docs/GOON_CONTENT_ARCHITECTURE.md) identifies
the remaining name coupling, version/ID requirements, and the case-source adapter
needed before non-job incidents can create compatible legal cases.

## Determinism, tests, and scope

RNG remains local to seeded operations. M013 preserves legacy job outcomes and
adds no random draws. Command history, action usage, investigation markers,
committed responses, and review dates
survive saving. Reports and snapshots expose no mutable world references.
M013.1 changed only Markdown and CLI display strings. M014 adds the optional
navigation extension, local definitions, service/CLI integration and navigation
tests while preserving the 198 existing regressions. M015 preserves all 237 M014
regressions and adds neighborhood choice, ledger, housing, migration and campaign tests.
M017-B preserved 371 tests and added 18 provenance regressions (389 total).
M018 passes **426 tests** (389 preserved plus 37 new). Its four preserved legacy replay hashes,
two 365-day two-incident campaigns, daily resumes and actual CLI playthroughs are
recorded in [M018 validation](docs/M018_WRONG_NOTICE_VALIDATION.md).
The audited M015 baseline passed **283 tests** (237 M014, 37 M015 and nine audit
regressions); see the [M015 validation report](docs/M015_VALIDATION_REPORT.md) and
[independent acceptance audit](docs/M015_INDEPENDENT_ACCEPTANCE_AUDIT.md) for evidence.
Full prologue, combat, broader career, influence and institutional
acceptance checks are future requirements, not executed feature tests.

Tests include all 166 M012 regressions, real M001-M012 fixtures, persistence failure
injection, malformed saves, command atomicity, CLI save/resume, fresh-process
hash-seed checks, a 365-day campaign with disk resumes, and a 90-day legal-choice
replay/resume. M012 covers heat/risk bounds, legal atomicity, event integrity,
and multi-day review/court outcomes. M013 adds economic identity, recovery,
recruitment, profile validation, transfer reconstruction, phase idempotency,
insertion-order independence, and the required multi-seed long campaigns. See
`tests/fixtures/README.md` for provenance.

Economic balance, courts, NPC policies, and the three-district geography remain simplified.
Unanswered cases still resolve automatically; responses support documented
collection cases and charged cases. No attorneys, warrants, probation, parole,
undercover officers, combat, drugs, Bat-family encounters, or playable prologue are
included. The prototype remains offline-capable.

## M030-C2B isolated stabilization ? 2026-11-19

The isolated `stabilize/m030-c2b-20261118` candidate preserves the interrupted frontend and repairs session, outbox and packaging failures. Local mode remains explicitly read-only; preview remains synthetic. This supersedes the earlier interrupted-work status for the isolated candidate only: the original branch remains unchanged and uncommitted, and no GitHub merge or release approval is claimed. See [the stabilization report](docs/M030_C2B_FINDINGS_AND_REPAIR_REPORT.md) and its exact test evidence. Python gameplay, 3 actions/day, 18 TU/day, saves and RNG are unchanged. Godot P1V-B/P1W remain separate protected work. Gameplay integration is a future approved mission.
