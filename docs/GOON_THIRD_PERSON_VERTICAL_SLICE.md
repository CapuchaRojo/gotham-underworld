# Third-Person Open-World Direction — One Living Block

**Decision date:** 2026-11-07. **Status:** Approved *long-term creative direction* and **proposed** M031-3D prototype contract; not an authorized implementation, merged milestone, production engine choice, or replacement for M030-C2/GTG-13B. Owner has selected a third-person, open-world crime/life RPG. The existing Python game remains authoritative; React is the interim UI. Godot 4 is the preferred **evaluation candidate**, not yet a committed production dependency.

**Player promise:** *Everybody wants to rule Gotham. You're just trying to survive it.* The player controls an ordinary person in a city that has interests, routines and consequences beyond the player's missions. Lawful employment, crime, reform and simply surviving must remain satisfying. Physical freedom must not silently grant free money, travel or information.

## 1. The smallest testable slice

**M031-3D / P0: movement feel.** In a standalone, disposable Godot prototype, create one stylized noir block (illustrative greybox about 100 × 100 m), a controllable third-person capsule/person, mouse-look camera with collision, walk/run, reliable locomotion/collision, interact prompt, and one ordinary door. Keyboard/mouse first. No Python integration, combat, vehicle system, commercial art pipeline, or changes to the authoritative repo. Measure responsiveness, camera obstruction, input latency, frame pacing on the owner's Windows PC and whether free exploration is enjoyable.

**P1: living-block presentation.** Illustratively add a home interior, a general-store interior, and three lightweight NPC **representations** (employer, resident, passerby). Give each an idle/route loop and an observable contextual interaction; these routines are visual prototypes only unless explicitly driven by real Python NPC state. No invented wages, standing, allegations, or private knowledge. Identifiers for Tess/store/home must be mapped to inspected atlas IDs before binding; do not assume that a plausible physical prop is an existing canonical POI.

**P2: transport contract.** Review a separately versioned Godot-to-Python adapter, authentication/bootstrap, command IDs, replay and state projection. The current M030 browser host is specifically designed for an authenticated browser; **it is not an approved Godot client protocol**. Do not bypass Origin/Host validation, place process credentials in resources or add a raw-world-state endpoint. Consider a protected local IPC bridge or minimal standard-library server adapter, reusing existing validation and authoritative game services, with security/restart tests before activation.

**P3: one engine-backed choice.** Once P2 passes, demonstrate the real Tess Navarro opportunity using its current option-level projection and command arguments. For an explicitly initialized eligible seed-42 career, the existing reference scenario uses travel to `goon.poi.p032` and `choose` with `choice_id=goon.choice.0.opening_shift`, `option_id=work`. Historical measured outcome is $40→$60, 2 actions left, 17 TU left and Tess standing +1, **only when that scenario and its prerequisites match**. Do not fabricate the option for other careers. Test refusal/leave without forced progression and stale/unavailable cases. Lost-ack/restart recovers a single committed receipt; never double-pay.

**Physical scope:** one block, two interiors, approximately three NPC stand-ins, one persistent choice. All counts and dimensions are design caps, not established atlas data. Use placeholders or properly licensed/original assets. Exclude city-scale streaming, combat, parkour, drivable vehicles, crowd simulation, extensive interiors, full Blackgate prologue, and any late-game restricted content. A pretty empty street does not satisfy acceptance.

## 2. Player control and interaction model

| Intent | Proposed control | Initial authority |
| --- | --- | --- |
| Walk / look / sprint | WASD, mouse, Shift | Godot local presentation and collision within the current approved local space |
| Context interaction | E | Godot selection; Python authority for consequential action |
| Phone / character view | Tab | Read-only validated projection; no hidden world truth |
| Local map | M | Player-known location data only; navigation is not teleportation |
| Pause | Esc | Presentation only; no implicit `wait` |
| Accept an offered option | Explicit UI selection | Python `choose` or `ordinary_choose` with exact supplied IDs/arguments |

Prototype controls are not final accessibility bindings. Add remapping, controller and accessibility audits later. Exploration, looking and noncommittal dialogue are not each one of three gameplay actions; ordinary local animation is not itself the canonical travel command.

## 3. Simulation authority and location/time contract

**Godot owns:** rendering, camera, collision, temporary animation state, input, local navigation mesh, presentation-only crowd loops and visible interactions. It cannot award pay, alter world RNG, infer private NPC knowledge, approve a crime, make up an opportunity, settle a day or save authoritative world truth.

**Python owns:** career/lineage, revision, daily actions, travel TU, canonical locations and edge permissions, resources, event identity, choice eligibility/outcomes, NPC memory/knowledge, law, deterministic day processing, world checkpoint and exactly-once receipts.

**Seam rule:** Physical motion **inside** an explicitly bounded canonical location/interior may be continuous and locally free. Crossing a canonical POI/neighborhood boundary requires a documented, validated movement/transition policy consistent with Python travel authority. If a visual doorway is blocked by engine travel/entry rules, do not display successful entry or silently teleport. A prototype-only visual crossing must not be represented as committed canonical movement. There is no implemented authoritative 3D position schema. Proposal to persist coordinates, continuous time, stamina, or encounter outcomes requires a separate migration/replay policy.

**Keep existing budgets unchanged:** 3 gameplay actions/day and 18 travel units/day; reading, looking, panning and animation do not advance the simulation. `wait` is a distinct explicit command. Real-time action combat/stealth/chase mechanics and deterministic capture/resolution are **future design**, not implemented.

**Knowledge boundary:** Player-visible NPC locations and rumors must come from permitted projections and plausible observations, not developer snapshots. Repeated visual inspection may not roll extra outcomes or expose hidden faction, legal or NPC information. A render tick may never trigger a world mutation. NPCs should eventually have their own goals and memory, but simple cosmetic loops are not simulated autonomy.

## 4. Security, persistence and replay

- No duplicate engine: all consequential mutations go through the validated game-service boundary; maintain protocol version, identity, request ID, expected revision, strict argument keys and exactly-once receipts.
- The client persistently records the *exact* request envelope **before** transmission; interrupted acknowledgments recover via original ID before any revision-based retry decision. Never transform an old request into a new one automatically.
- Reload/restart cannot create a career, adopt historical saves, grant wages, spend TU or trigger a mission. UI errors must be fail-closed, not replaced with synthetic outcomes.
- Browser-host auth is **not** automatically reusable by a Godot process; define and threat-model P2 transport separately.
- Offline-only acceptance: no mandatory commercial asset CDN, hosted tile server, AI model, telemetry or game-service dependency.
- Distinguish reported tests from executed local/browser/Godot acceptance evidence.

## 5. Gameplay test: is one block actually fun?

A useful 10–15-minute session: explore the modest room; leave, walk a street, observe people; enter the store; assess a real offer; make or decline a consequential choice; receive truthful feedback; return or continue without being forced onto a criminal path. **P0/P1 are movement/interaction feasibility tests, not a claim that this real Python loop is already playable.**

Target playtest measures: camera and character feel (no frequent obstruction or stuck collisions), time until a player discovers a meaningful optional interaction, whether players understand costs and consequences, whether the block has believable ambient behavior, no involuntary quest/start/end, and whether returning after a committed choice reveals a persisted difference. Prefer tightening movement and the social decision loop over building more empty streets.

## 6. Dependencies, phase gates and acceptance

| Gate | Required proof | Stage |
| --- | --- | --- |
| P0 movement feasibility | Godot project runs offline on target Windows hardware; responsive camera/movement/collision, door interaction; honest playtest notes | Proposed; standalone |
| P1 visual life | Block/home/store explorable; three lightweight NPC representations have observable routines; no fake authoritative state | Proposed |
| P2 backend adapter | Reviewed client authentication/transport; authoritative projection; canonical location binding; deterministic replay/restart and known rejection paths | Proposed; separately approved design first |
| P3 Tess slice | Explicit source-backed offer and movement; real Python receipt, persist/restart, duplicate safety; refusal remains possible | Proposed |
| Expansion | Original assets, streaming/LOD, accessibility, broader NPC behavior, lawful/criminal alternatives and viable ordinary weeks | Unapproved future scope |

**Development budget hypothesis:** initial P0 may target $0–$100 out-of-pocket with a capable existing PC and free tooling; labor/hardware/assets are excluded, and this is not a validated cost forecast. Engine choice and time estimates require measurement. Keep core Python runtime stdlib-only; using Godot as a separate client would be an explicitly approved new toolchain, not a Python runtime dependency.

**IP:** DC-inspired Gotham is an unofficial fan concept without permission assumed; commercial release, public promotion, licensing or sales require rights review or an original-setting alternative. No restricted late-progression organization content, clues, symbols, images or metadata may enter early playable runtime bundles.

## 7. Integration with active delivery and next owner approval

M030-C1/C1.3 Python bridge/browser host is merged per the inspected `f2e75dd959c5` source snapshot. GTG-13A was subsequently reported QA-accepted in Builder and GTG-13B is in progress as a separate source-integration/real-browser acceptance gate; those newer Builder reports are **not represented in the inspected HEAD ZIP**. GTG-14 (Tess React slice) and GTG-15 (real-browser exactly-once acceptance) remain blocked until their respective prerequisites pass. **Finish the React/Python integration track independently; a Godot visual experiment must not destabilize it.**

Before any Godot repository work, approve: the P0 prototype target, separate branch/repo and scope, license/asset policy, target PC performance baseline, and success measures. Before P2, approve a dedicated client/transport security contract. Before real-time combat or a changed clock/travel model, approve separate simulation migrations and regression tests.

Related canonical documents: [milestones](GOON_MILESTONE_ROADMAP.md), [runtime/navigation](GOON_WORLD_RUNTIME.md), [visual map](GOON_MAP_VISUAL_SPEC.md), [gameplay principles](GOON_GAMEPLAY_PRINCIPLES.md), [first-week roadmap](GOON_ROADMAP_TO_PLAYABLE_1_0.md), and [prologue](GOON_PLAYABLE_PROLOGUE_CONTRACT.md).

## 8. Current implementation boundary (2026-11-07 as-is working tree)

The active GTG-13B React/Python integration is still in an **uncommitted** local feature worktree in the owner-provided November 7 snapshot. The test results and Edge smoke are reported by Codex as interim evidence only; its final reproducibility/full-Python-suite/commit steps did not finish. This proposed M031-3D prototype must not be embedded into or replace `frontend/`, alter the existing Python host or save format, or delay finalizing GTG-13B. Neither P0 nor any Godot code is present in the inspected source.

**Approval sequence:** first authorize an isolated P0 movement-only experiment, then assess camera feel and block exploration, then separately design and security-review a Godot client bridge (P2). The current HTTP browser capability is not permission to bypass origin restrictions for a native executable.
