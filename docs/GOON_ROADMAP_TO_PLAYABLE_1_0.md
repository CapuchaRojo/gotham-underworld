# Gotham: The Goon — Roadmap to a Fully Playable 1.0

**Status:** Proposed planning baseline; not an implementation or merge authorization  
**Prepared:** 2026-11-06  
**Suggested repository location:** `docs/GOON_ROADMAP_TO_PLAYABLE_1_0.md`  
**Tagline:** *Everybody wants to rule Gotham. You're just trying to survive it.*

## 1. Vision and finish line

Build an offline-first, deterministic, visually appealing, deeply reactive Gotham crime/life RPG in which the protagonist is an ordinary person. The game supports lawful employment, criminal opportunity, reform, precarious survival, hybrid lifestyles, failure, and recovery. Choices must create **different futures**, not merely different dialogue. Gotham's residents have independent routines, limited knowledge, goals, and memories; the player is not the center of every event.

**1.0 acceptance definition:** A new player can create a character, experience a coherent Blackgate-release opening, navigate Gotham, pursue several viable lifestyles, form relationships, work or commit crimes, face proportionate consequences, save and resume offline, and play at least **30 meaningful in-game days** without a softlock or repetitive quest treadmill. Thirty days is an acceptance benchmark, **not** a gameplay limit; open-ended play must continue beyond it.

The game must be enjoyable on an ordinary Tuesday, even if no famous villain appears.

### Non-negotiable engineering and narrative rules

- Python standard library remains the authoritative gameplay engine unless a change is explicitly approved.
- React/TypeScript is a presentation and interaction client, not an independent gameplay authority.
- Preserve offline execution, deterministic RNG/replay, stable event IDs, exactly-once effects, service-authoritative mutations, backward-compatible saves, explicit historical-save adoption, and read-only inspection.
- Recheck eligibility at action execution; prevent duplicate rewards, contradictory state, resource exploits, and ordinary-life softlocks.
- Preserve **3 gameplay actions/day** and **18 travel units/day** until a separate, tested design change is approved.
- Separate world truth, NPC knowledge, and narrative/player-facing display. Rumors require plausible transmission.
- Never equate geography with faction control; respect the existing navigation architecture.
- No mandatory kingpin trajectory, forced criminality, forced commuting, punitive grind, or forced supernatural path.
- Court of Owls, Talons, related symbols, rumors, and foreshadowing are **fully quarantined** until the final third of meaningful progression, not elapsed days.
- The project is unofficial and DC-inspired. Public release and especially monetization require intellectual-property and licensing review.
- Work proceeds **Inspect → Diagnose → Design → Implement → Test → Playtest → Audit → Merge**. No merge without explicit owner authorization.

## 2. Verified and reported starting point

These facts are based on the project's recent user-provided Git and Builder outputs, not a fresh independent code audit:

- Git `master` synchronized with `origin/master` at **`50a11f1`**, merging M029 through **PR #22**; working tree clean at the last reported check.
- Seven M029 canonical reference documents are present in `docs/` and text-match their Native.Builder export copies.
- M001–M020 are reported merged. M020 included ordinary-life systems; M019 included institutional response. Their current runtime behavior still requires source/test verification for this roadmap.
- Established atlas: **8 regions, 48 neighborhoods, 120 POIs, 176 places**; station-gated monorail overlay exists in the reported navigation architecture.
- Native.Builder's React/Vite/TypeScript preview includes Today, Streets, My Life, and My Story, with player/developer presentation modes. It is **not yet proven connected** to the authoritative Python engine.
- Builder reported Mission 003 complete (VS-0, VS-1, VS-2, VS-5), **64 frontend tests passing**, typecheck/build/smoke pass. An independent acceptance audit is pending.
- M029 roster is a **198-record planning index**, not 198 implemented deep NPCs. Builder reports 11 employer cultures (3 anchored, 8 design-only) and 26 organization records (none directly anchored); these claims are pending independent review.
- The Builder workspace reportedly lacks Git history and could not independently diff its runtime source against a baseline.
- Export artifacts tracked in the repository are duplicates of canonical documentation; cleanup is optional and must be reviewed separately.

**Status terminology:** *Implemented* means present in inspected source; *tested* means exercised with evidence; *merged* means Git history proves integration; *approved design* means authorized but not necessarily built; *proposed* means not yet authorized. Do not substitute one label for another.

## 3. Delivery structure: four phases, twelve sections

### PHASE I — CONNECT THE GAME

#### Section 01 — Foundation, architecture, and engine-to-UI integration

**Priority:** Immediate, after Mission 003 acceptance.

**Scope:** Audit current Python modules and tests; map the real engine entry points and save/replay boundaries; reconcile Builder workspace against the repository; select an offline React↔Python bridge and packaging architecture; define versioned action/state/error contracts; route all mutations through Python game services; build end-to-end action → resolution → state update → save → reload → replay tests. Avoid speculative APIs and duplicate TypeScript game rules.

**Distinct player value:** A visible choice produces a real, durable change in the authoritative game.

**Exit gate:** An ordinary-life action initiated in the UI is resolved by Python, updates the display, survives restart, and replays deterministically without duplicate effects.

#### Section 02 — Character creation, identity, attributes, and progression

**Related proposed milestone:** M023.

**Scope:** Inclusive stylized appearance; starting possessions and personal circumstances; attributes relevant to lawful and criminal paths; background and starting contacts; skills developed through experience; behavior-shaped personality rather than fixed morality or class locks. Keep legacy-character and save flows compatible.

**Distinct player value:** Character identity changes opportunities and trade-offs without dictating destiny.

**Exit gate:** Two different starting characters experience materially different first-week opportunities and obstacles, while both retain viable paths.

#### Section 03 — Blackgate release and the first playable week

**Related proposed milestone:** M024.

**Scope:** A contextual release from Blackgate; appropriate identification, clothing, phone, transportation, housing, supervision, and support conditions; credible introductions to work, relationships, shelter, and street risk. Supervision depends on sentence circumstances, not a universal ex-prisoner penalty. Arkham and Blackgate remain distinct. Provide refusal, negotiation, lawful options, and recovery.

**Distinct player value:** The opening creates a personal situation with meaningful agency rather than a forced tutorial questline.

**Exit gate:** A newcomer can complete seven in-game days through at least three credible approaches: legitimate rebuilding, opportunistic crime, and independent survival.

### PHASE II — MAKE GOTHAM LIVE

#### Section 04 — Daily life, economy, possessions, and survival

**Scope:** Deepen and integrate M020's housing, rent, employment, weekly allocation, contacts, and support mechanics with food/rest/health, clothing/tools/phone/storage, debt, recreation, emergency expenses, and realistic recovery options. Prefer interdependent consequences over isolated meters. Keep mundane weeks interesting without forcing major crimes.

**Distinct player value:** Everyday choices have believable knock-on effects; financial setbacks open difficult alternatives rather than instant failure.

**Exit gate:** Thirty-day ordinary-life campaigns remain playable and varied, without dominant exploits, repetitive busywork, or unavoidable poverty spirals.

#### Section 05 — Geography, multimodal mobility, and exploration

**Related proposed milestone:** M022.

**Scope:** Extend the existing atlas and station-gated monorail without rewriting navigation. Distinguish walking, skateboard, bicycle, car, and citywide transit by access, ownership, time, cost, risk, and route constraints. Integrate mobility with employment, neighborhood opportunities, law, equipment, and discoveries.

**Distinct player value:** Travel method and route selection change costs, exposure, and future access.

**Exit gate:** A representative trip supports multiple legitimate modes with correct prerequisites, deterministic costs, and no teleportation or resource exploits.

#### Section 06 — NPC autonomy, social relationships, and memory

**Related proposed milestone:** M021.

**Scope:** Three simulation tiers—deep recurring NPCs, lightweight secondary NPCs, aggregate crowds. Implement schedules, goals, independent changes, contact availability, bounded memories, relationships, witness knowledge, and plausible rumor transmission. Keep inspection read-only and narrative claims grounded in what characters know.

**Distinct player value:** People remember, pursue their own lives, and respond differently weeks later.

**Exit gate:** Two-week campaigns yield explainable persistent social divergence; no NPC gains implausible omniscience.

### PHASE III — GIVE GOTHAM DEPTH

#### Section 07 — Careers, skills, and opportunity networks

**Scope:** Interlocking lawful employment, gig/survival work, street crime, specialized criminal roles, organized-crime relationships, civic/reform work, and hybrid paths. Gate opportunities through skills, equipment, contacts, reliability, reputation, and history. Support quitting, retraining, failure, and recovery.

**Distinct player value:** Careers differ in stability, pay, risk, social access, and future opportunities—not merely labels.

**Exit gate:** At least five substantially different trajectories support meaningful 30-day campaigns without a mandatory kingpin endpoint.

#### Section 08 — Crime, law, institutional response, and recovery

**Scope:** Connect crime planning and opportunity to witnesses, evidence, delayed reporting, GCPD response, legal exposure, institutional memory/corrections, supervision where applicable, and practical rehabilitation. Batman and GCPD act independently and cannot magically know private actions. Preserve bounded and exactly-once processing.

**Distinct player value:** Risk is legible, success and failure are causal, and setbacks do not permanently eliminate agency.

**Exit gate:** Representative criminal and lawful scenarios resolve consistently, respect evidence provenance, and retain credible recovery routes after arrest or other serious loss.

#### Section 09 — Factions, rogues, optional DARK, and emergent narrative

**Scope:** Convert prioritized M029 designs into selective, integrated gameplay. Distinguish employer cultures, organizations, gangs, individual actors, and territorial influence. Start with a small number of deeply reactive recurring characters and faction arcs, not a blanket implementation of 198 roster records. Batman/Bat-family and institutions have independent agendas. DARK encounters are optional; Slaughter Swamp/Grundy are conditional; Task Force X recruitment is rare and earned. Court of Owls remains quarantined until the final third of meaningful progression.

**Distinct player value:** Relationships and past decisions cause multi-week storylines with genuine refusal, negotiation, alternative resolution, and changing loyalties.

**Exit gate:** At least three multi-week arcs have persistent, causally distinct outcomes, and optional content does not hijack ordinary-life play.

### PHASE IV — FINISH THE EXPERIENCE

#### Section 10 — Visual identity, UX, sound, and immersion

**Proposed direction, subject to approval:** Stylized illustrated 2D noir with layered environmental art, not full 3D. Prioritize coherent Gotham neighborhood identity, expressive portraits, accessible typography, readable navigation, cinematic yet efficient dialogue, atmospheric lighting, responsive transitions, sound, and mobile/narrow viewport behavior where relevant. Avoid a corporate dashboard aesthetic and avoid beautiful but disconnected mock interfaces.

**Distinct player value:** The player feels present in Gotham and understands choices, costs, and consequences without developer documentation.

**Exit gate:** New players can identify location, available actions, resources, and changes after acting; player mode reveals no developer internals.

#### Section 11 — Balance, content completion, and human playtesting

**Scope:** Deterministic automated campaigns and human playtests across lawful, criminal, reform, mixed, isolated, employed, unemployed, financially precarious, and recovering characters. Detect repetition, dominant strategies, impossible obligations, duplicate rewards, social amnesia, bad pacing, softlocks, and false choice. Expand content only where playtests show thin or repetitive loops.

**Distinct player value:** Multiple lives feel surprising, fair, and replayable rather than grind-heavy.

**Exit gate:** Independent testers complete 30-day campaigns, can explain major consequences, and report materially different stories; long-run tests remain stable.

#### Section 12 — Offline packaging, release readiness, and support

**Scope:** Reproducible build/install; clean-machine offline launch; save migration and crash recovery; release test suite; input/accessibility documentation; asset attribution and licensing; IP/legal review; performance budgets; backup/restore; issue triage and patch strategy. Treat private playable builds separately from any public or commercial release.

**Distinct player value:** The game is an actual self-contained product that can be installed, played, saved, and resumed reliably.

**Exit gate:** A clean supported machine installs and runs offline without developer tools or external services; release/legal gates are documented and satisfied for the chosen distribution scope.

## 4. Five playable build gates

| Build | Target | Required demonstration |
|---|---|---|
| **A — Connected Prototype** | After Section 01 | Real Python action through React, durable state, deterministic replay |
| **B — First Week in Gotham** | After Section 03 | Character creation, Blackgate opening, seven playable days and three viable approaches |
| **C — Living Gotham Alpha** | After Section 06 | Ordinary life, travel, autonomous NPCs, relationships, 30-day survival |
| **D — Complete Systems Beta** | After Section 09 | Careers, crime, law, factions, and emergent narrative working together |
| **E — Gotham 1.0** | After Section 12 | Polished, balanced, accessible, offline, packaged, and extensively playtested |

Build gates are evidence-driven, not calendar-driven. No milestone passes merely because its task cards are marked Done.

## 5. Parallel workstreams and handoff contracts

**Codex / Python:** authoritative simulation, rules, events, state changes, save/replay, migrations, tests.  
**Native.Builder / React:** presentation, player interactions, UX, visuals, accessibility, frontend tests.  
**Architecture / QA:** interface contracts, canon reconciliation, cross-layer tests, playtesting, risk and acceptance audits.

Before parallel development, agree on a versioned interface describing action identifiers, eligibility, input validation, resolved events, display state, errors, persistence boundaries, and compatibility. The UI may request an action; the Python service must recheck it and decide the outcome. The frontend may not independently award resources, change institutional standing, or bypass game time/travel accounting.

Every vertical slice must answer:
1. What new decision does the player gain?
2. What distinct costs, risks, opportunities, and lasting consequences follow?
3. Which existing systems are integrated?
4. How can it fail, be refused, or be recovered from?
5. What exploits, knowledge leaks, softlocks, and save/replay regressions are possible?
6. What tests and human playtest scenarios prove it works?

## 6. Immediate work queue and stop gates

1. **Mission 003 acceptance:** Review independent Builder QA; confirm VS-0 registry, VS-1 roster↔`npcPool`, VS-2 faction↔trajectory matrix, and VS-5 Court quarantine; resolve any FAIL/BLOCKED items. Reported 64 tests do not verify Python integration.
2. **Authoritative Python audit:** Inspect the current source, tests, actual save schemas, service APIs, event semantics, and replay coverage. Reconcile code with `PROJECT_STATE.md` and contracts. Do not assume ZIP snapshots are live Git state.
3. **Offline integration architecture decision:** Prototype and approve a minimal React↔Python bridge and distribution strategy before broader UI development.
4. **One full vertical slice:** Execute a mundane player choice from the UI through Python and verify consequence, persistence, replay, and visual feedback.
5. **Character/prologue contract and implementation:** Begin only after the integrated runtime is stable.

**Do not do yet:** blanket-implement all roster records; rewrite navigation; expand major villains before ordinary-life play works; replace Python authority with TypeScript fixtures; build elaborate UI disconnected from engine; publish a commercial DC-based release without appropriate rights review.

## 7. Release-quality acceptance matrix

| Dimension | Minimum 1.0 evidence |
|---|---|
| Agency | Lawful, criminal, reform, survival, and mixed choices remain viable |
| Consequence | Choices cause persistent, explainable differences weeks later |
| Ordinary life | 30-day mundane campaigns are interesting without major villain events |
| NPC causality | Limited knowledge, routines, and memory; no omniscience |
| World | Coherent geography, destinations, travel prerequisites, and neighborhood identity |
| Integrity | No duplicate rewards, replay drift, resource exploits, or silent save corruption |
| Recovery | Failure, refusal, job loss, legal exposure, and housing crises have credible alternatives |
| UX | Readable, responsive, atmospheric, accessible, no debug clutter in player mode |
| Offline | Launch, play, save, exit, resume, and replay without network dependency |
| Distribution | Licensing, assets, documentation, and release scope reviewed |

## 8. Decision log — proposed, not yet approved

- **P1:** Adopt the twelve-section/four-phase roadmap as the planning baseline.
- **P2:** Prioritize Section 01 integration immediately after Mission 003 acceptance.
- **P3:** Target stylized illustrated 2D noir art direction; final visual style and asset pipeline require approval.
- **P4:** Use 30 meaningful in-game days as the initial minimum playtest benchmark, with open-ended gameplay beyond.
- **P5:** Maintain one canonical documentation tree under `docs/`; Builder export packs are delivery artifacts, not competing sources of truth.
- **P6:** Do not start major content expansion until Build A's end-to-end Python integration passes.

## 9. Definition of success

A player can say: *“I planned to get a legitimate job, but I helped a neighbor, missed an interview, got into debt, made a friend who knows someone at the docks, and now I have a choice I never expected.”*

That story should arise from interconnected simulation and persistent decisions—not a scripted illusion or a chain of disconnected menus.

## November 7, 2026 — third-person long-term direction addendum

**New owner decision:** The eventual Goon experience should be a **third-person, open-world crime/life RPG**. The earlier roadmap's 2D noir presentation remains an **interim React/UI and map-accessibility path**, not the final visual target. This changes creative direction but **does not change** the 1.0 requirement for 30 meaningful, open-ended in-game days, the first playable-week acceptance, or the existing Python engine authority and budget/replay rules.

**Parallel proposed milestone M031-3D — One Living Block:** A separate Godot 4 feasibility experiment (candidate tool, not selected production engine) should first prove third-person camera/movement/collision and an ordinary interaction within a single stylized block. Only after P0 acceptance add an apartment/store and three lightweight NPC representations (P1). A separately reviewed, secure Godot↔Python adapter and canonical location policy are P2, and a real durable Tess work choice is P3. P0/P1 are deliberately not dependent on real Python integration and must not be misrepresented as connected gameplay. Detailed contract: [GOON_THIRD_PERSON_VERTICAL_SLICE.md](GOON_THIRD_PERSON_VERTICAL_SLICE.md).

**Near-term priority remains Build A / GTG-13B:** Import the latest corrected Builder React source into the authoritative repo; prove the pinned local build works under the merged Python browser host and show real authenticated state. Then complete the Tess React slice and exactly-once end-to-end acceptance. Do not replace, stall or weaken those gates for the Godot prototype. No new gameplay commands, time model, save schema or 3D transport are authorized by this direction decision.

**Freedom policy:** Camera, walking, local visual exploration and ambient inspection must not each cost one gameplay action. Crossing canonical locations must still respect Python travel authority and the existing 18 TU budget, while meaningful commitments continue to use the 3-action budget. Future real-time combat, vehicles, continuous time, animated NPC autonomy and city-scale streaming need separate engineering contracts, not aspirational acceptance claims.

**IP/budget:** A free/open tool plus simple original greybox assets can make the initial prototype affordable, but no cost or schedule estimate is validated. DC/Gotham licensing is unresolved; public release/commercialization requires rights review or an original-setting strategy. Keep secrets and late-progression restricted content out of all prototypes and asset bundles.


## 2026-11-07 source-snapshot qualification

An as-is local worktree export shows ongoing, uncommitted GTG-13B `frontend/` import and local browser-inspection implementation at Git HEAD `f2e75dd959c5`. Interim Codex-reported frontend and Edge smoke progress does not establish GTG-13B acceptance, a completed Python regression, or a merged integration. GTG-14/GTG-15 remain blocked. The third-person direction changes the eventual visualization target, not the active acceptance gates or the deterministic backend.
