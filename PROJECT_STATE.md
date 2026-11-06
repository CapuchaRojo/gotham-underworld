# Gotham: The Goon — Project State

- Working title: **Gotham: The Goon**; subtitle: *A Living Gotham Crime RPG*
- Positioning: "Everybody wants to rule Gotham. You're just trying to survive it."
- Current runtime slice: **M020 — Ordinary Gotham**, Mission 026 implementation,
  independently hardened in Mission 027; PR #21 merged at `74a5fab` in Mission 028
- Mission 029: documentation-only underworld/rogue research on
  `feature/m029-underworld-registry`, from verified master
  `74a5fab57fa52ad21b53bb1f565d77a38b2ac7a1`; no new gameplay or M021
- Mission 029 addendum continues that branch from local research commit
  `4a9818697c77e526d76cb27d1d79a253ad1701c8`: master index and optional DARK
  canon/progression documentation only; no runtime, UI or save changes
- Task Force X design addendum continues from
  `f8f43ecce769bd8706e765ad6ccf356940f69818`: restricted recruitment canon,
  five-condition proposal and institutional provenance only; no implementation
- Implementation branch: `feature/m020-ordinary-gotham`, from verified master
  `6682019857ccad4553fcdc04f7a7e7e046b2def0`; isolated baseline 476 tests passed
- PR #17 first merged into the audit branch. PR #18 subsequently integrated that
  provenance history into master (`8bc9700`); PR #19 merged M018 (`d0723b1`).
  M019 PR #20 merged at `6682019` with successful master CI. Existing branches
  and commits are preserved. M020 PR #21 is now merged; prior local-only
  publication statements in historical reports describe their original missions.
- PR #15 (M015) and #16 (M016-A) are merged. The prior open-PR requirement was
  superseded explicitly; both original feature branches remain unchanged.
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

- [Registry](docs/GOON_ROGUES_GALLERY_REGISTRY.md): 36 research entries after
  Mission 029 (the original 35 retained plus Jane Doe), stable proposed
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
PR #15 subsequently merged; this paragraph preserves the M015 audit's test evidence.

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
real-time timers or commuting reward. This section records the prior M016-A
slice, now merged. Do not push the new implementation without authorization.

## Mission 016 — independent overnight incident, local M017 branch

- Explicit `enable_incidents` after active daily life; no historical auto-adoption,
  clock, retroactive incident, fee or allowance refresh.
- One original alarm at p032, with a pinned seed-selected break-in, faulty alarm
  or delivery error. Occurs one or two future day transitions after enrollment;
  evidence follows next day; independent resolution four days after occurrence.
- A new idempotent phase follows daily life, preserving every preceding phase.
  One-shot terminal state freezes; no endless daily incident spam or respawning.
- World truth, owner knowledge, desk reports and player knowledge are separate.
  Explicit local notice/contact discovery; no automatic player proximity or true
  cause in the initial report. No rogue, Batman or new legal-case source.
- Shared choice assessment, three actions and 18 TU; current eligibility checked
  on execution. Inspection completion/partial/failure, lawful safety help,
  refusal, disclosure/withholding, ignored known offers and missed unknown events.
- Existing contact authority owns Ada's bounded standing/memories; player cash
  and the existing life ledger own all compensation. At most $12 inspection +
  $8 distinct follow-up; no double collection. Ordinary work/home remain viable.
- Optional `incident_version: 1`, pinned content, deterministic transition replay,
  exact command/effect references and cross-checked delegated memories/payments.
  Outer save/navigation/mobility schemas and old content fingerprints unchanged.
- [After Dark](docs/GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) distinguishes
  this implemented slice from future proposals. [Rogue Encounters](docs/GOON_ROGUE_ENCOUNTERS_DESIGN.md)
  had exactly 35 proposed distinct roles at that checkpoint; Mission 026 removes
  Milo below. No rogue gameplay was added.
- **371 tests passed**, including all 336 baseline tests and 35 new acceptance
  cases. Exact campaigns/results and current limitations belong in the
  [Mission 016 validation report](docs/M017_NIGHT_SHIFT_VALIDATION.md).

## M018 implemented scope and current limits

- Explicit two-definition dispatch, shared day/stage/receipt settlement and common
  replay validation; Night Shift keeps its old slot, IDs, content and event shape.
  Original mobility and Night Shift replay hashes remain unchanged.
- `enable_incident(definition_id)` adds only the requested definition after life
  activates. `enable_incidents` retains its historical Night Shift-only meaning.
  Optional `notice_version: 1` / `wrong_notice` state has its own content pin.
  No outer save-version bump, implicit adoption, fresh budgets or retroactive event.
- One independent Wrong Notice: delivery dates in a board notice and handbill
  disagree with the actual local ledger. Nora Reed and Sam Ortega are original
  local contacts under the existing life memory/standing authority.
- Separate truth, source limitations, recipient beliefs, source transmissions,
  player observations and reconciliation. Board-only help, delayed desk posting,
  private tenant warnings and retractions reach only their actual recipients.
  Delivery-day impact persists after late corrections.
- Success, partial help, failed sharing, refusal, ignored-known, missed-unknown
  and selfish lawful reservation have distinct aftermath. No automatic wage;
  a verified vacancy permits one optional $5 shift with a social cost.
  Existing ordinary work, room grace, legal rules, 3 actions and 18 TU are unchanged.
- Player reports/events hide unreceived automatic reactions until the local final
  circular is read. Full save/debug snapshots remain an audit view of world truth.
- [M018 validation](docs/M018_WRONG_NOTICE_VALIDATION.md) records exact commands,
  historical bytes/hashes, failed saves, deterministic campaigns and CLI evidence.
  No new GitHub CI is claimed for local work.

This is one versioned episode per definition per career, not recurring citywide
content. There is no global rumor network, police case, clock, recruitment or
new rogue gameplay. Abstract tenant/board audiences have small local consequences;
there is no individual resident schedule, inventory loss or business economy.
The future prologue and broader creative proposals remain unimplemented.
Mission 022 integrated M018 using a merge commit after verifying provenance
ancestry and the exact 20-file tree diff. Both PR checks, post-merge CI and all
426 local regressions passed. The original feature branch remains preserved.

## M019 merged scope

- Explicit `institution_version: 1` / `institutions`; future NPC intake only,
  with source-backed earlier player observations eligible for explicit submission.
- Original staff at a civilian n13 service desk and existing p044 public police
  counter. Separate mandates, received reports, beliefs, contradictions, queues,
  local credibility and receipt-time player knowledge. No broad NPC simulation.
- Bounded source adapters consume actual incident events; they never infer
  receipt from world truth. Old incident reducers, content pins and IDs remain.
- One-/two-day processing, three-day unanswered clarification closure, documented
  correction/reopening, exactly-once submission and one correction copy.
- A received copy can document a later explicit desk correction after old
  incident windows expire; it grants no primary inspection credit or new reward.
- Service-owned submit/correct/follow-up actions cost one; withholding is free,
  private and bounded. Reporting access consequences remain local. No wage,
  prosecution, warrant, arrest, rent change or travel/action allowance refresh.
- Canonical [institution contract](docs/GOON_INSTITUTIONS_AND_RECOVERY.md) and
  [validation report](docs/M019_INSTITUTIONAL_RESPONSE_VALIDATION.md) describe
  actual behavior, source rules, executed evidence and limitations.
- Mission 024 independent validation: **476 tests passed** (all 468 preserved,
  eight audit regressions); 50 focused institutional tests passed. Confirmed
  acquisition-order, player-attribution, unsubmitted-source and historical-anchor
  validation gaps were repaired without changing producers or the save schema.
  Two additional 365-day institutional campaigns, two 90-day daily disk-resume
  campaigns, all six historical fingerprints, four real CLI paths and interrupted
  writer recovery passed. No `WinError 32` was reproduced; restricted-sandbox
  temporary-directory access failures are recorded separately in the report.

Replies are secondhand records, not primary inspection credit. There is no global
rumor propagation, inventory simulation for correction copies, new legal AI,
care/prison episode, canon character, combat or global clock. The separate M020
extension follows; it was not part of M019's historical scope.

## M020 local implemented scope

- Optional `ordinary_version: 1` / `ordinary`, explicitly adopted through
  `enable_ordinary` after active daily life at home/n13; starts the next day.
  No retroactive shift credit, rent, debt or automatic historical adoption.
- Existing repair completions build employment standing 0–6 without another
  wage or personal reward. One separate two-action home allocation per week pays
  $24/$28, with posted supply cancellations and a one-request rescheduling path.
- Reserved work pins its later wage/window. Missed/withdrawn accepted deliveries
  have bounded consequences; refusal and unaccepted expiration have none.
- One conditional $20 Tess advance per career, seven-day repayment obligation,
  no interest/automatic collection, and existing source-backed contact memories.
- Existing housing/ledger/navigation remain authoritative: $30 weekly review,
  capped arrears, maintenance/prepayment and basic home access; advance planning
  notices; three actions and eighteen TU. No new transport or institutional feed.
- `ordinary`, `ordinary_choices`, `ordinary_choose`, and the adopted home report
  expose eligibility, costs, actual terms, debt, standing and recovery routes.
- **522 tests passed** (all 506 preserved, 16 independent audit tests added);
  46 focused M020 tests passed; all six historical hashes retained. Mission 027
  repaired inherited work/reference eligibility, counterfeit maintenance offers,
  unsupported repayment funding and erased action-counter validation. Two new
  365-day and two 90-day daily-resume campaigns, five real CLI paths, genuine
  historical save compatibility and interrupted-writer recovery are recorded in
  [M020 validation](docs/M020_ORDINARY_GOTHAM_VALIDATION.md).
- Approved design only: Milo remains excluded; the post-M026 encounter pool had
  34 individual/mantle entries. Mission 029 adds Jane Doe and Crazy-Quilt for 36,
  with a separate optional Court organization that is entirely
  undiscoverable before the final third of meaningful progression. No Court
  runtime state, clues, dialogue, triggers or implementation exists.

Limitations: bounded abstract employer funding, predictable posted allocations,
one existing cooperative arrangement and limited NPC availability. Full employment,
eviction, dialogue, prologue, Court mechanics and M021 remain unimplemented.

## Mission 029 — underworld research and documentation reconciliation

Starting branch/HEAD: clean `master` / `74a5fab57fa52ad21b53bb1f565d77a38b2ac7a1`;
fetched `origin/master` matched. Dedicated local branch:
`feature/m029-underworld-registry`. M020 integration/ancestry is preserved.
No runtime code, content JSON, tests, save schemas, event IDs, RNG, navigation,
mobility, three-action/eighteen-TU budgets, frontend or Builder package changed.

### Document ownership and inventory

- `docs/GOON_ROGUES_GALLERY_REGISTRY.md`: retains all original 35 research entries
  and IDs; adds Jane Doe (36 entries, including the pre-existing Terrible Trio
  group). Calendar Man is enriched in place; Crazy-Quilt naming/mantle evidence
  clarified without changing its ID. "Quilt Man" is not a verified canon alias.
- `docs/GOON_ROGUE_ENCOUNTERS_DESIGN.md`: preserves all 34 post-M026 table rows;
  appends Jane Doe and the existing Crazy-Quilt identity for 36 proposed roles.
  It is an overlapping encounter selection, not the same set as the minor registry.
  Milo stays excluded; no approved character behavior is silently replaced.
- `docs/GOON_FACTION_EMPLOYER_MATRIX.md`: preserves both original employer tables;
  extends this existing authority with 26 sourced candidate/category records,
  leadership/status/confidence, continuity reconciliation and a bounded future
  organization contract. Four umbrellas are not actors; not every candidate is
  a faction, district owner, starting presence or joinable employer. Beretti and
  Inzerillo are included on indexed Five Families/Cry for Blood evidence.
- `docs/GOON_MINOR_CRIMINAL_ECOSYSTEM.md`, `docs/GOON_CONTENT_ARCHITECTURE.md`,
  `docs/GOON_NARRATIVE_DESIGN_BIBLE.md`, `docs/GOON_CRIMINAL_CAREER_WEB.md`,
  `docs/GOON_CONDITIONAL_OPPORTUNITIES.md`, `docs/GOON_MILESTONE_ROADMAP.md`:
  cross-references, source ownership, strict player-knowledge boundaries and
  approval-gated priorities. No separate general-character or organized-crime
  registry was invented; the existing specialized documents remain authoritative.
- `README.md` and this file: current counts, M020 merge status and Mission 029 scope.

### Research conclusions and limitations

Publisher references include DC's Calendar Man profile, Jane Doe/Ventriloquist
comics-versus-TV comparison, Crazy Quilt/Batman #54 preview, Falcone profile,
Cry for Blood collection, Black Mask history, Intergang/52 account, Penitente/
Neon Dragon creator commentary, Mutants adaptation comparison and Gotham TV
retrospectives. Secondary DCU Guide/GCD bibliographic records and clearly marked
Fandom/Wikipedia indexes support obscure candidates. Supporting links and
H/M/L confidence appear beside claims in the registries. No complete comic,
episode or licensed sourcebook was inspected; blocked pages/search excerpts
are disclosed, not upgraded to primary verification.

Unresolved: exact Lo Boyz issue/leadership, Gilzean episode-level hierarchy,
Cassamento/other source spellings, Odessa labels and the actual campaign era,
leaders, deaths, alliances and fronts. Burnley absorption remains secondary
speculation. East Side Dragons is distinct from Ghost Dragons. TV organizations
and alternate-future Mutants are not merged into a comics starting cast. An
ethnic/category label never supplies criminal membership, guilt or one treasury.

All named-organization statuses and mechanics are proposed; no continuity pack
or playable criminal career is selected. Lawful/civilian and independent paths
remain valid. Batman/GCPD independence does not imply knowledge without sources;
no Batman actor or new legal/information system is implemented. The existing
Court restriction is preserved in author-only policy, with no early/middle
triggers, symbols, rumors, Talons, references, public discovery or foreshadowing.

### Executed documentation validation

- Standard-library Python checks against Git baseline `74a5fab`: gallery 35 → 36,
  all old IDs/numbered entries retained (only the requested Crazy-Quilt display
  spelling normalized); encounter rows 34 → 36, all original rows byte-for-byte
  retained; Milo absent from current roster rows.
- Both employer tables' 26 original Markdown lines retained; all 26 new O01–O26
  candidate IDs unique/sequential, with sources, confidence, status and six table
  columns; four umbrella categories explicitly non-actor.
- All 247 relative file/heading link occurrences in changed documents checked
  with no broken target; table-width, UTF-8 and code-fence checks passed. New
  links target the existing canonical files.
- `git diff --check` passed. Full changed-file inventory is 11 Markdown files;
  no runtime, definition, fixture, test or UI file changed and no untracked output.
- Regression suite **not rerun** for this documentation-only mission. The last
  actual merged-master run remains Mission 028: 522 tests, local 562.088s and
  master CI 198.934s, both OK; that is historical executed evidence, not a new run.

No new player decision or persistent effect is implemented. The matrix's
paper-only invoice/authority scenario evaluates meaningful lawful involvement,
specific recipient consequences, variety, grind risk and remaining shallowness.
Recommended next step: approve a small continuity subset/source reconciliation,
then separately scope one original funded minor-crew commitment with refusal,
independent resolution and sourced memory. No M021 number or implementation is
authorized here. Documentation is prepared for human review; no push, PR or merge.

## Mission 029 addendum — master roster and optional DARK design

Inspected clean branch `feature/m029-underworld-registry`, HEAD
`4a9818697c77e526d76cb27d1d79a253ad1701c8`. No comprehensive master index existed.
The addendum creates one navigation authority pointing to existing detail owners;
it does not replace registries, select a continuity, expose a player codex or
implement a cast. Master remains `74a5fab`; all prior branches/commits are preserved.

### Deliverables and changed-file inventory

- [Master character/faction index](docs/GOON_MASTER_ROSTER.md): **188 unique
  reference records**, not 188 active people. Covers existing rogues/ambiguous
  actors, heroes/role holders, family/gang leadership, organizations/categories,
  original contacts/staff, civic institutions/professional roles and DARK.
  Each row tracks identity/key, aliases, continuity, affiliation/relationship
  pointers, role, availability, implementation type and authoritative source.
  Vacant roles and staff labels are not fabricated named NPCs; aliases, personas,
  bound wills, mantles, crews and categories cannot become duplicate actors.
- [DARK canon registry](docs/GOON_DARK_CANON_REGISTRY.md): seven requested
  candidates with publisher-supported motivation/power anchors, limits and
  continuity differences; separate proposed roles/availability. Existing Ivy,
  Crane, Deacon Blackfire and Strange remain under their original identity
  authorities. "Reverend Blackfire" is unverified user wording, not a new person.
- [DARK discovery contract](docs/GOON_DARK_PROGRESSION_CONTRACT.md): proposed
  late optional involvement, independent occurrence versus discovery, alternate
  lawful/relationship/investigative/civilian routes, the nonmandatory four-encounter
  achievement idea, seven-row behavior/outcome matrix, ordinary recovery, future
  dependencies and eight explicit approval questions. No moral score/faction lock.
- Existing cross-reference/status updates: `README.md`, this file,
  `docs/GOON_CONTENT_ARCHITECTURE.md`, `docs/GOON_FACTION_EMPLOYER_MATRIX.md`,
  `docs/GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md`,
  `docs/GOON_MILESTONE_ROADMAP.md`, `docs/GOON_NARRATIVE_DESIGN_BIBLE.md`,
  `docs/GOON_ROGUES_GALLERY_REGISTRY.md`, `docs/GOON_ROGUE_ENCOUNTERS_DESIGN.md`.
  Total: **12 Markdown files**, three new and nine updated. No detailed registry
  entry or canonical organization classification was replaced.

### Research and reconciliation findings

New character research uses DC profiles, creator commentary, collections and
specific issue/film solicitations linked beside claims. No full comic, episode,
film or licensed sourcebook was inspected; blocked direct pages versus accessible
indexed excerpts remain disclosed. Existing indexed facts inherit their prior
confidence, rather than being newly declared primary-verified by inclusion here.

Zatanna is not universally disabled by silence: the cited 2025 account includes
sign-language casting. Swamp Thing's Olsen, Alec-related and Levi histories need
an actor/era choice. Creeper's science-transformation and host-based portrayals
cannot be merged into one presumed occult origin. Jason Blood and Etrigan are
distinct bound wills, not an analogy for a clinical diagnosis or Scarface's persona.
Xanadu's visions and Deadman's possession do not mean unlimited access to save
truth; proposed participation limits are explicitly game policy, not invented
universal canonical weaknesses. No automatic seven-person team/allegiance exists.

The four Gotham encounters may remain entirely grounded, and neither one nor
all four prove magic or summon an ally. The achievement is optional and proposed,
not an access gate or reason to schedule danger. Players can refuse occult
involvement, remain civilian/lawful/independent, or return to ordinary life after
failure without permanent hero/villain affiliation. Assistance cannot become a
general solution to housing, wages, employment or law enforcement.

The Court remains wholly separate, with one **author-only policy pointer** in
the master index. No early/middle symbols, rumors, Talons, references, visions,
metadata hints or foreshadowing are introduced into player content. DARK and its
achievement supply no unlock or route around the existing final-third meaningful-
progression restriction. Milo stays excluded; no roster entry reinstates him.

### Validation and next approval boundary

Standard-library documentation checks verified unique/nonempty nine-field master
records, coverage of existing source IDs, seven DARK entries, four optional
achievement outcomes, seven consequence rows and eight approval questions.
All 515 relative file/heading links, 63 Markdown tables, UTF-8/code fences and
`git diff --check` passed. All original lines/IDs in the
three detailed registries are retained. Existing minor/encounter counts stay 36
and organization/category records stay 26; categories and linked identities are
not counted as additional active characters. No Python, content JSON, fixture,
test, event, schema, budget, navigation, RNG, frontend or Builder package changes.

Regression tests were **not rerun** for this documentation-only addendum. The last
actual 522-test results remain Mission 028's merged-master verification, not a
new claim. No new gameplay decision, persistent effect, occult power or event is
implemented. The contract's paper scenario evaluates variety, source-specific
consequences, refusal, grind risks and remaining shallow/unapproved mechanics.

Before any implementation, approve continuity/character subset, meaningful late
milestones, opt-in/withdrawal policy, achievement terms, power/knowledge scope,
possession/horror consent, bounded costs/zero-cash recovery and one small slice
with its adoption/replay contract. These remain open design decisions, not a
request to implement now. Roadmap placement is optional/late and unnumbered;
no M021, broad magic engine, Court content, GitHub publication or merge is begun.

## Task Force X design addendum — research and approval contract only

Starting clean branch/HEAD: `feature/m029-underworld-registry` /
`f8f43ecce769bd8706e765ad6ccf356940f69818`. Master remains `74a5fab`.
No Task Force X contract or gameplay existed. The prior encounter proposal's
“not freely joinable” policy remains: special assessment, consent, membership
and deployment are distinct. Creature Commandos, DARK and Joker initiation are
separate and receive no automatic recruitment or cross-unlock.

### Exact changed-file inventory and deliverables

1. `docs/GOON_TASK_FORCE_X_RECRUITMENT_DESIGN.md` — new canonical specialized
   contract: inspected implementation limits, twelve canon/context records,
   all five original special-route conditions, government/character provenance,
   four stages, eight distinct outcome rows, seven alternative/softlock cases,
   future dependencies/acceptance and ten explicit approval decisions.
2. `docs/GOON_MASTER_ROSTER.md` — nine new source-linked references, bringing
   the author-only index from 188 to **197**, not 197 active people. Includes
   Waller, Junior/Senior Flag as distinct records, Economos, Harcourt, Task Force X,
   A.R.G.U.S., Belle Reve and a vacant original government-liaison role. Existing
   Lawton/Harley/White and all earlier records remain unchanged.
3. `docs/GOON_ROGUE_ENCOUNTERS_DESIGN.md` — reconcile the restricted new proposal
   with prior non-free-join policy; no actor or generic Squad admission added.
4. `docs/GOON_INSTITUTIONS_AND_RECOVERY.md` — cross-reference actual Arkham access,
   distinct prison/care/supervision authority and explicit modifications/relief.
5. `docs/GOON_FACTION_EMPLOYER_MATRIX.md` — point to specialized government context
   without turning programs/agencies into more district gangs or White into a handler.
6. `docs/GOON_CRIMINAL_CAREER_WEB.md` — optional ordinary-person pathway and viable
   refusal, reform, lawful work and survival; no forced graduation into combat.
7. `docs/GOON_CONTENT_ARCHITECTURE.md` — keep source/identity owners, service,
   historical unknowns and recipient views; no new backend/schema/event hooks.
8. `docs/GOON_MILESTONE_ROADMAP.md` — design milestone and unnumbered later bounded
   assessment recommendation, with foundations before recruitment or operations.
9. `README.md` — contract navigation/status only.
10. `PROJECT_STATE.md` — this source/validation/delivery record and scope status.

### Findings and source limits

The user route remains **E1 AND E2 AND E3 AND E4 AND E5**: substantial documented
criminal record, several consequential Deadshot encounters, appropriate Harley
interaction during a lawfully accessed Arkham story, no unresolved severe White
hostility, and compliance with actual applicable parole/probation conditions.
No arbitrary conviction/heat, encounter-count or relationship-score threshold
is chosen. Proven/not-satisfied/unknown and supported non-applicability must be
distinguished; absence of fields cannot prove any condition.

Actual code supplies validated legal outcomes/fines and accelerated custody,
not offense gravity, full sentences, probation/parole, named rogue histories or
government access. Historical null dates/fines remain unknown. A record of a
dismissal, heat, job count, free custody or paid fine cannot substitute for a
substantial conviction record, lawful Arkham access or supervision compliance.
Current M019 intake is not a government recruitment/record service.

Publisher research includes DC's Waller, Squad, Flag, Deadshot and Harley profiles;
White financial-crime account; Economos/Harcourt comics-versus-screen comparison;
Flag Sr. history; later Waller/Harcourt office/life-state premises; Arkham-game
identity/recruitment material. Citations and scope limits accompany each claim in
the new contract. No full comic, episode or film was reviewed. Profiles/solicitations
are not a universal current roster; blocked direct pages/indexed excerpts are
disclosed. No reviewed source makes White a compulsory Squad recruiter or grants
Waller omniscience. His special-route condition is original operational-risk design.

Canon coercion/danger is acknowledged without authorizing surprise implantation,
forced acceptance or compulsory deployment. World truth, sources, government
intelligence, actual Waller briefings, criminal rumors and player knowledge remain
separate. Corrections reach named recipients. No dossier reads every private
memory, medical record, legal event or source merely because Waller is powerful.

The proposed A–D event identifies, assesses, offers a decision and records an
aftermath. Acceptance, negotiation, investigation, refusal, reporting, partial
failure, missed/canceled offers and betrayal/deception have distinct futures.
Neither assessment nor signing automatically grants freedom, immunity, wealth,
expungement, superpowers, sentence changes or hero/villain affiliation. An approved
alternative could enable later consideration after a missed famous encounter,
but cannot falsely complete a condition or promise eventual membership.

### Validation and approval boundary

Documentation checks verify full old-row/ID preservation, unique nonempty master
records, all five conditions, twelve context records, four stages, eight outcome
rows, seven alternative cases, ten approval questions, local file/heading links,
Markdown tables, UTF-8/fences and `git diff --check`: **479 relative file/heading/
code links and 59 tables passed**. Minor/encounter rosters stay
36; the general criminal catalogue stays 26; seven DARK records remain unchanged.
Milo stays excluded. The separate Court gate is preserved, with no early/middle
symbols, rumors, Talons, references, agency clues, public discovery or foreshadowing.

Exactly ten Markdown files change (one new, nine updated). No Python, content JSON,
tests, fixtures, saves, event IDs, RNG, navigation, budgets, backend, Native.Builder
UI or handoff package changed. Regression tests were **not rerun** for this design
mission; prior 522-test results are historical, not new execution. No new gameplay
choice, persistent effect, source adapter or recruitment event is implemented.

Approval remains required for continuity/personnel, record interpretation,
distinct Deadshot evidence, Harley access, White conflict/negative-evidence scope,
actual supervision authority, alternate route scope, costs/terms/recovery,
coercion/consent and one future adoption/replay slice. Recommend that assessment
slice only after the missing institutional/encounter foundations are approved.
No M021, deployment, push, PR creation or merge is begun by these documents.

## Mission 030-C1 — durable offline bridge foundation

Subsequent local infrastructure: [M030-C1.3 browser host](docs/M030_C1_3_BROWSER_HOST.md)
adds release-pinned assets, one-time same-origin bootstrap and stable-port resume.
It preserves the C1 gameplay/checkpoint boundary. Synthetic host tests do not
approve the actual React bundle or unblock GTG-13; browser integration remains
outside this implementation. See its contract for executed results and BLOCKED gates.

Verified clean master at `50a11f18046bccbb379a843ebb52364e7045b936` (PR #22
integration); all 522 baseline tests passed in 159.535s. Implementation is isolated
on `feature/m030-c1-durable-engine-bridge`, with no publication or merge authorized.

- New `bridge_checkpoint.py`, `engine_bridge.py`, `bridge_projection.py` and
  `bridge_http.py` provide a standard-library checkpoint/broker/projection and
  loopback JSON interface. Existing gameplay, service, navigation, content and
  engine persistence/schema files remain unchanged.
- Checkpoint version 1 stores the validated engine world and ordered source-backed
  transport receipts in one atomic publication, with previous-good backup and an
  OS single-writer lock. Explicit legacy import/export never overwrites originals.
- Protocol 1 enforces career/lineage, exact bounded arguments, expected revision,
  committed-ID payload matching and replay of original receipts without effects.
  Candidates become live only after durable publication. Uncertain publication
  quarantines mutations until operation/state recovery proves old or new primary.
- Player projection omits world snapshots, raw events, hidden incident identities,
  NPC memories, faction strategies and institutional processing. C1 exposes personal
  resources/location, limited Tess/Cal standing and existing ordinary-life choices.
- HTTP binds only 127.0.0.1, requires private per-launch capabilities and exact
  Host/Origin checks, limits JSON bodies to 16 KiB, rejects unsafe framing and
  exposes no filesystem/static/debug routes. Commands are serialized.
- New tests cover actual subprocess crashes, dropped HTTP acknowledgments,
  duplicate wages/waits, conflicting requests, historical saves, malformed data,
  filesystem failures, writer exclusion, security and projection boundaries.
  Two 30-day restart/replay campaigns match direct engine worlds. Tess's actual
  repair retains the frozen 030-B world hash, $20 wage and one-action cost;
  separate home work retains its two-action rule. Three actions/18 TU are unchanged.
- Focused validation: 44 tests passed in 37.502s, with the final path-guard change
  also checked by its targeted regression. Final full suite: **566 tests passed
  in 538.975s** (all 522 unchanged baseline tests plus 44 new bridge tests).
  A real CLI create/HTTP repair/restart/receipt-recovery/legacy-export smoke run
  passed with $60 cash, two actions, 17 TU and the frozen engine hash retained.

See [C1 protocol, checkpoint and validation contract](docs/M030_C1_DURABLE_ENGINE_BRIDGE.md)
for exact commands, recovery policy, evidence and limits. No React/Native.Builder
work, assets, desktop host, deployment, new NPC, gameplay mechanic or C2
implementation is included. Receipt/history growth, filesystem power-loss limits,
explicit corrupt-primary recovery and non-Windows verification remain open limits.
