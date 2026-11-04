# Gotham: The Goon — Project State

- Working title: **Gotham: The Goon**; subtitle: *A Living Gotham Crime RPG*
- Positioning: "Everybody wants to rule Gotham. You're just trying to survive it."
- Current local slice: **M016-A — versioned mobility and two-station monorail pilot**, for review
- Implementation branch: `feature/m016a-mobility-pilot`; baseline audited M015
  `3251381177bf11c0b07cd940329ebd0be3a7bb52`, 283 existing tests preserved
- PR #15 remains open and unmerged; its submitted branch is unchanged. Last
  merged baseline remains M014 at `fa2f9f5bbf081bde080c6d8b2e46512487027c66`
- Stack: Python 3.14 standard library; offline; no mandatory services or packages
- Entry point: `python gameplay.py`; resume with `python gameplay.py --load`
- Save contract: version 1; additive migration of unversioned M001-M010 saves
- Mobility contract: optional paired nav2/mobility1; explicit next-wait adoption,
  immutable legacy checkpoint/schema1 history, typed schema2 journeys and receipts
- Legal contract: independent `legal_version: 1`; additive M001-M011 migration
- Competition contract: `competition_version: 1`; persisted profiles/bindings,
  additive M001-M012 migration, and activation on the next advanced day
- Validation: nested state, versions, references, and custody consistency
- Persistence: staged writes, atomic replacement, previous-valid `.bak`, exclusive
  first-save publication, and protection against silent new-career overwrites
- Action economy: three shared daily job/mission/legal actions through `game_service`;
  legacy low-level job resolution remains unchanged
- Command interface: create/load/save, execute commands, advance one day, detached
  snapshots, persisted command sequence, and structured command events
- Investigation: per-case daily idempotency while preserving NPC acceleration
- Warfare: target/funding validation and explicitly attributed hold fallbacks
- Intelligence: detached reports and non-mutating strategy assessments
- Heat: effective 0–100; four tiers affect job exposure and documented-case scrutiny;
  zero-cash recovery through lay low and quiet days
- Legal choices: lay low, cooperate, contest, accept; explicit prerequisites/costs,
  one committed response per case, two-day review, and unique outcome records
- Event integrity: heat transitions, scrutiny, responses, payments, and outcomes
- Economic identity: trade, street, and industrial profiles with distinct revenue,
  recovery, upkeep, recruitment, reserves, aggression, and defensive thresholds
- Sustainability: bounded daily recovery and paid recruitment, funded readiness,
  capped new income, no negative cash, power 0–100, and credible displaced operations
- Territory: pressure stops at one in modern play; paid attacks/player missions
  use a shared capture operation and auditable ownership/control transitions
- Strategy: recover/regroup/defend/expand/consolidate; deterministic rotating
  initiative and explicit fallback reasons when current plans become invalid

## M013.1 design foundation

This section records the prior documentation milestone. Mission 007 now authorizes
world/navigation implementation; historical references to proposed M014 combat
are deferred under the [current roadmap](docs/GOON_MILESTONE_ROADMAP.md).

This milestone changes Markdown documentation and CLI display strings only.
Repository/module names, package structure, save identifiers, runtime content
definitions, workflow labels and all existing gameplay remain intact. The CLI
banner and prompt use the working title; historical Gotham Underworld references
remain where they identify technical interfaces or past milestones.

- [Narrative bible](docs/GOON_NARRATIVE_DESIGN_BIBLE.md): ordinary workers as
  protagonists; workplace comedy, crime drama, survival, relationships, and many
  possible careers. Separates implemented behavior, endorsed creative direction,
  proposed mechanics, and speculative concepts. Endorsed direction is not
  implementation authorization or a delivery schedule.
- [Career web](docs/GOON_CRIMINAL_CAREER_WEB.md): nineteen overlapping criminal
  specializations plus lawful work, informing, rehabilitation and retirement;
  references and commitments matter alongside skills. Three original paper
  scenarios show divergent work, recovery and post-custody careers.
- [Conditional opportunities](docs/GOON_CONDITIONAL_OPPORTUNITIES.md): prerequisites,
  demand, capacity, seeded selection, expiry and revalidation; no named encounter
  is guaranteed or required to complete a campaign.
- [Employer matrix](docs/GOON_FACTION_EMPLOYER_MATRIX.md): eleven proposed DC employer
  cultures; recruitment, compensation, risk, loyalty, advancement and fallout.
  Broad canonical anchors are sourced; workplace mechanics are original proposals.
- [Gameplay principles](docs/GOON_GAMEPLAY_PRINCIPLES.md): sourced historical
  criticism, seven feature gates, ten-field design reviews, current mechanical
  shallows, a current-game reproduction recipe and paper exercises. No new player
  decisions or consequences are implemented by M013.1.
- [Villain influence](docs/GOON_VILLAIN_INFLUENCE_SYSTEM.md): fictional exposure,
  coercion and vulnerability separated from chosen allegiance; meaningful choices,
  bounded conditions, credible recovery and ethical alternatives. Unimplemented.
- [Institutions/recovery](docs/GOON_INSTITUTIONS_AND_RECOVERY.md): distinct criminal
  custody, psychiatric admission, voluntary care and supervision; lawful fictional
  entry/review/exit rules require continuity approval. No conviction-only Arkham
  commitment, guaranteed villain, forced treatment grind or villain-exclusive cure.
- [Content architecture](docs/GOON_CONTENT_ARCHITECTURE.md): future stable IDs and
  definitions, separate runtime facts/knowledge/presentation, service-driven GUI
  and narrative, and the legal case-source integration prerequisite for combat.
- [M014 combat contract](docs/M014_COMBAT_DESIGN_CONTRACT.md): proposed bounded
  solo turns, health/stamina, injury/recovery, exits, legal/reputation outcomes,
  deterministic resume, high-threat survival and future crew extension points.
  Numerical rules and acceptance criteria await review; combat is not implemented.

### Rogues gallery addendum

This addition changes Markdown only; it adds no further CLI, gameplay, schema,
dependency or module changes. All concepts below are unimplemented proposals.

- [Registry](docs/GOON_ROGUES_GALLERY_REGISTRY.md): 35 entries, stable proposed
  IDs, variant/source boundaries, conservative canon anchors and original work,
  behavioral, faction-relationship and consequence ideas. Terrible Trio contains
  three actors. Secondary factual references are labeled; primary-edition and
  continuity review remains necessary before implementation.
- [Minor ecosystem](docs/GOON_MINOR_CRIMINAL_ECOSYSTEM.md): major district factions,
  minor crews and individuals; ordinary original workers, bounded contracts,
  optional strategic participation, growth, setbacks, defection, arrest and exits.
- [Joker recruitment](docs/GOON_JOKER_RECRUITMENT.md): an original campaign gate,
  not DC canon. Citywide cell work can occur without membership; formal initiation
  requires a direct Joker encounter during an Arkham storyline, a valid offer
  and explicit acceptance. No guarantee of presence, encounter or invitation;
  refusal and non-Joker career completion remain viable. Cells can work during
  Joker's absence; care/release never depends on his cooperation.

These documents are integrated into the bible, career web, opportunity rules,
employer matrix, institution design and architecture. No rogue is mapped onto
an existing faction or assumed to own a district merely because they are a boss.

## City atlas and world-map design submission

The [atlas](docs/GOON_GOTHAM_ATLAS.md) and
[registry](docs/GOON_LOCATION_REGISTRY.md) propose 8 regions, 48 neighborhoods and
120 POIs (176 place records). Brown's design account is the primary geographical
inspiration; Arkham Knight, Gotham Knights and Monolith publisher material provide
secondary organizational/atmospheric references. No source map is traced/rendered;
the full commercial RPG map was not inspected. Borrowed names and original
placements/profiles are explicitly distinguished, with continuity questions open.

The [network](docs/GOON_TRAVEL_NETWORK.md) specifies 63 physical neighborhood
corridors plus 120 POI access links. Its provisional separate 18-TU travel allowance
preserves three daily gameplay actions, free basic public mobility and useful local
alternatives; no travel command, vehicle or schedule is implemented.
The [integration proposal](docs/GOON_MAP_SIMULATION_INTEGRATION.md) retains all
legacy territory keys/resources/events, uses optional display footprints, and
requires explicit versioned opt-in/activation before a future geography feature.
Geographic expansion does not automatically multiply income, upkeep or warfare.

[Career geography](docs/GOON_CAREER_GEOGRAPHY.md) connects all established work
specializations with civilian services and three paper scenarios.
The [visual specification](docs/GOON_MAP_VISUAL_SPEC.md) separates actual world
facts from public data, observations and rumors; no GUI/read adapter is added.
This submission changes Markdown only. No active district, save schema, faction
rule, dependency, gameplay/CLI behavior or M014 scope changes.

## Validation

Run `python -B -m unittest discover -s tests -v`.

The M013.1 scope retained all 198 existing tests and added no runtime tests for
documentation/display-only changes. Its
[final integration audit](docs/M013_1_FINAL_INTEGRATION_AUDIT.md) records executed
regression, compatibility and specification checks. Future scenarios and acceptance
criteria are not passing-test claims.

All 166 M012 tests remain unchanged. Coverage includes persistence failure
injection, malformed/current-version state, M001-M010 migration fixtures, bounded
commands and rollback, CLI protection/resume, report isolation, warfare fallbacks,
investigation replay protection, fresh-process determinism, a 365-day campaign,
and M012 heat bounds, legal invariants/atomicity, M011 migration, multi-day reviews,
zero-cash recovery, and a 90-day legal replay/resume. M013 adds profile economics,
power and resource limits, displaced recovery, transfer history reconstruction,
ordering independence, migration, daily idempotency, and deterministic resumes.
Run `python -B faction_campaigns.py` for four 365-day campaigns and one 1,000-day
campaign. Actual outcomes and fingerprints are in `M013_SIMULATION_REPORT.md`.
Execution results belong in the feature PR rather than a permanently current claim.

## Architecture and creative constraints

Daily processing retains legal reviews/cooling before career investigation and
uses profile economy/strategy/operations after the compatibility first day. Existing
job RNG draws and low-level job rules are preserved. Player interfaces use
`game_service.execute_command`; views use detached snapshots. Dictionary saves
and current content names are retained. Legal rules have no character-name policies.
M013 adds no combat, drugs, probation/parole, undercover officers, Bat-family
encounters, storylines, imported assets, or M014 systems. Economic profile
definitions are independent of fictional organizations and configurable per save.

The creative direction is an independent, unofficial prototype intended for a
future DC-universe crime RPG pitch, without endorsement, authorization, or
affiliation. Executable content remains original placeholders. Future content
should use stable identifiers and definitions separated from mechanics, dialogue,
missions/events, assets, and progression. Proposed distribution, commercialization,
fundraising, or pitch materials require separate rights review.
The new working title remains subject to future licensing and title clearance;
this milestone performs neither. No third-party scripts, copied narrator
characters/jokes, or extracted media are introduced. No named DC actor is added
to runtime content, and no existing placeholder is silently reinterpreted as one.
No DC license is claimed and the working title is not legally cleared. Fictional
institutional rules and influence conditions are design proposals, not real-world
medical/legal guidance or a selected universal DC continuity.

## Known limits and next review

Unanswered cases retain automatic court resolution; contests receive two-day
reviews. Fines cannot create debt. Historic unknown dates/fines remain unknown.
Legacy heat >100 is normalized only on a successful command. Economic balance
remains a tuning question: Iron leads all four one-year samples, while Harbor
leads at day 1,000 in seed 42. Every sampled faction remains operational, including
displaced organizations. Recovery is time-based and capped; there is no elimination
or rank-based equalization. Static wealth, three districts, and abstract readiness
limit realism. Commands copy the world.
Saves assume one writer and a
filesystem supporting hard links and replacement. Recovery is explicit; no GUI
is included.

M013.1 is merged. Mission 007 reserves M014 for world/navigation, with no combat
or playable prologue. The deferred combat contract still requires review of
tactical/daily costs, exits, tuning and compatible legal sources before separate
implementation approval. Do not merge the M014 feature PR automatically.
`INSTALL_M002.md` through `INSTALL_M010.md` describe historical installations,
not the current setup workflow.

## M014 implemented scope

- [Local atlas](content/gotham_atlas_v1.json): 176 validated places, 63 corridors,
  120 gated POI spurs, source/profile metadata and a declared new-career home.
- [Registry loader](location_registry.py): unique IDs, hierarchy, references,
  profile tokens, modes/directions/costs, detached definitions and content fingerprint.
- [Navigation](navigation.py): stable public-mode routing, entry/lawful egress,
  separate 18 TU, minimum 1 TU for completed local travel, advisory return previews,
  finite direction/mode closures and safe-prefix discovery. No vehicle mechanic.
- New careers start at p031; old saves stay navigation-free until an explicit
  public anchor choice and next-day post-court activation. Load never refreshes TU.
- Independent `navigation_version: 1`; outer save version, historical keys,
  atomic backup behavior, legacy RNG/legal/faction rules and three actions remain.
- Commands: `travel(destination, mode)`, `enable_navigation(anchor)` through the
  existing service. Detached reads: location, nearby, known places and route.
- CLI: `look`, `nearby`, `places`, `route`, `travel`, `enable_navigation`; current
  jobs can be used from the slice without a mission rewrite or location gate.
- [Runtime policy](docs/GOON_WORLD_RUNTIME.md), [roadmap](docs/GOON_MILESTONE_ROADMAP.md)
  and [future five-chapter prologue](docs/GOON_PLAYABLE_PROLOGUE_CONTRACT.md).

No combat, prologue scenes, rent/payroll, NPC schedule, private institutional
interior, new major faction or district revenue is added. Public frontages and
static services remain mechanically shallow; future work must make place and
commitments matter without mandatory commute grind. No licensed map assets are
included. Tests and actual simulation results are reported in the feature PR.

[M014 submission evidence](docs/M014_VALIDATION_REPORT.md): 229 passing regressions
(198 unchanged plus 31 new), actual historical fixtures, real CLI resume and two
100-day navigation/reference campaigns. The independent [Mission 008 final audit](docs/M014_FINAL_AUDIT.md)
records additional corrections, the final test count, CI and PR disposition.
Mission 008 proposed the [M015 daily-life contract](docs/GOON_M015_DAILY_LIFE_CONTRACT.md).
Mission 009 authorizes the bounded implementation below.

## M015 implemented scope

- Optional `daily_life_version: 1`, explicitly enrolled with `settle_in` and activated
  on the next day. No automatic defaults, retroactive charges, invented history,
  free actions or TU on historical load. Existing `create_career` behavior stays compatible.
- A disclosed $30/seven-day room arrangement at p031; first due seven advances
  after acceptance. Prepayment, cash-limited settlement, receipts, $30 arrears cap,
  basic grace access, and one bounded maintenance credit per unpaid review.
- Original Tess Navarro and Cal Mercer contact definitions in a separate local
  pack, with event-backed observed memories and standing bounded to -10..10.
  Neither reads private legal/household actions unrelated to their own work.
- Generic consequential choices, stable option/source IDs, hidden/visible-disabled
  states, advisory detached previews and current-state revalidation. Effect
  adapters settle actual work/promises; CLI letters map to displayed stable IDs.
- Finite weekly store shifts, a real personal promise, one renegotiation/follow-up,
  Cal's explicitly disclosed criminal referral and observed later courier offer.
  References change future work; refusals and misses have coherent continuations.
- A continuous actual-cash ledger from enrollment. Criminal referrals invoke the
  existing legal job resolver once; the ledger records the payout without paying again.
  Legacy legal fines/NPC support retain detailed domain events plus a net ledger entry.
- Shared three actions, separate 18 TU, explicit travel, and one idempotent
  post-court/post-navigation daily phase. No chore or cash reward for home inspection.
- Commands: `settle_in`, `pay_room`, `choose(choice_id, option_id)`. Detached views:
  `life_report`, `home_report`, `contact_report`, `opportunities`, `choice_report`.
  CLI adds `life`, `home`, `contacts`, `opportunities`, `choices` and contextual menus.
- [Choice contract](docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md), reproducible
  [campaign runner](daily_life_campaigns.py) and [validation evidence](docs/M015_VALIDATION_REPORT.md).

The original submission passed 274 tests (237 M014 plus 37 new). Mission 010's
[independent acceptance audit](docs/M015_INDEPENDENT_ACCEPTANCE_AUDIT.md) corrected
promise-source validation, stale-clock roster creation and public memory projection.
The corrected M015 baseline passed **283 tests**, including nine audit regressions;
the five seven-day/daily-resume and 56-day campaign results remain unchanged.
PR #15 remains open and unmerged pending explicit user authorization.

This is one neighborhood with two original contacts and finite roster templates.
The full prologue, background selection, broad employment economy, combat, advanced
NPC schedules, new DC actors, graphical frontend and future milestones remain unimplemented.
Weekly repetition and the legacy faction-support advantage are recorded limitations;
low cash does not erase home access or block ordinary continuation.

## M016-A implemented scope and limits

- Explicit service adoption, pending save/resume without activation, and one
  activation inside the existing post-court navigation reset before daily life.
  Three actions/day and 18 TU/day remain separate and unchanged.
- Additive overlay only: p039/p071 platforms, four existing underlying rail
  corridors, 7-TU/$2 station-frontage journey versus free 8-TU bus. No atlas edit.
- Policy C: abstract rail remains for non-adopters and old history; active rules2
  requires the station service and prevents old travel/rail command bypass.
- Atomic candidate execution, per-request retry rejection, one boarding charge,
  safe-prefix closure observations, detached status/quotes/receipts and projected
  return using remaining resources. Reuse CLI `route`/`travel`; new `mobility`,
  `adopt_mobility`, `receipt` expose status, enrollment and accepted receipts.
- Existing persistence/backup and daily-life cash observer reused. Frozen M015
  fixture generated from baseline source is outside the legacy fixture collection
  so existing pre-life fixture tests retain their intended scope.
- Overlay fingerprint:
  `d59fe323290fd1216d8b5e1ffdcde5924b123cedc0404ce22215d538779ec7ee`.
- Executed results and exact files are maintained in the
  [M016-A implementation/validation report](docs/M016_A_IMPLEMENTATION_VALIDATION.md).
  The three preserved M016 contracts distinguish this slice from future proposals.
- Final local regression: **336 passing tests** (283 existing,49 M016-A and4 metadata-repair cases),
  two365-day seeded replay campaigns and final-code30-day daily disk-resume
  checks; full worlds match at every command/day. These are local results,
  not new GitHub CI on this unpushed implementation.
- Mission015 repairs the two pending metadata type checks before legacy
  projection: booleans cannot substitute for integer rules_version/journey_sequence.
  No travel cost, schema, allowance or valid historical event changes.

No skateboards, bicycles, cars, acquisition gameplay, licensing, theft, impound,
new citywide disruption generator, advanced schedules or prologue are implemented.
Search is bounded; it can return an explicit planning limit requiring a simpler
profile/waypoint. Full candidate validation and save history grow with career
length. Only two stations and a modest cash/TU trade-off exist; no transport XP,
real-time timers or commuting reward. Keep PR #15 unmerged and do not push this
isolated implementation without explicit authorization.
