# Milestone scope and implementation plan

Mission 007 supersedes the earlier proposed M014 combat numbering. M013.1 is
merged at `8b68e1e`; its atlas and narrative documents remain design provenance.

| Milestone | Scope / approval |
| --- | --- |
| Mission 030-C1, local bridge foundation | Implement the [durable engine bridge](M030_C1_DURABLE_ENGINE_BRIDGE.md): loopback-only standard-library JSON, private candidates, atomic world/receipt checkpoint, source-backed request recovery, explicit legacy import/export, strict player projection and security tests. No React, packaging, gameplay changes, publication or C2 implementation. |
| M014 | Authorized world runtime/navigation foundation: local validated atlas, optional versioned location state, deterministic public movement, CLI and regression coverage. No combat or prologue implementation. |
| M015, Mission 009 | Authorized [Living Gotham slice](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md): optional room terms, local lawful/criminal work, finite choices, two original contacts, promises, cash ledger and idempotent day processing. Submit an open PR; no merge authorization. |
| Subsequent verified integration | M015 PR #15 and M016-A PR #16 merged. Night Shift is on master at `43d8197`; provenance integration PR #18 merged at `8bc9700`; M018 PR #19 merged at `d0723b1`, preserving original ancestry. Historical instructions above describe their original mission scope. |
| M019, Mission 023 | Local-only bounded institutional knowledge/response from `d0723b1`: civilian desk, police intake, explicit adoption, causal reporting/correction, delayed independent queues, replay tests and documentation. No push, PR, merge or further milestone authorized. |
| Verified M019 integration | PR #20 merged at `6682019` after independent Mission 024 hardening and draft publication/CI verification. Historical local-only instructions above describe the original mission. |
| M020, Mission 026 | Authorized local-only Ordinary Gotham: extend actual repair/housing/contact systems with employment standing, one home-work allocation, negotiated timing, conditional support and persistent recovery/refusal paths. Explicit adoption, compatibility, budgets, CLI, deterministic campaigns and source-backed validation. No publication, eviction, general scheduler or M021. |
| Verified M020 integration, Mission 028 | PR #21 merged at `74a5fab57fa52ad21b53bb1f565d77a38b2ac7a1`, preserving M019 and audited M020 ancestry. Master CI and local regression both passed 522 tests. Earlier local-only statements record original mission boundaries. |
| Mission 029, documentation only | Extend the existing minor-character/encounter and employer registries with sourced continuity/confidence, 26 organization/category candidates, and a bounded integration proposal. No gameplay, save, budget, RNG, UI or faction-system implementation; no selected licensed pack, push or merge. |
| Mission 029 addenda, documentation only | Maintain the [198-record author-only master index](GOON_MASTER_ROSTER.md), [seven initial DARK candidates plus G01 Grundy and Slaughter Swamp research](GOON_DARK_CANON_REGISTRY.md), and [optional discovery/behavior contract](GOON_DARK_PROGRESSION_CONTRACT.md). Preserve grounded play, original identities/exclusions and the separate protected gate; no runtime, atlas or UI changes. |
| Task Force X design addendum, documentation only | Preserve the [special five-condition route](GOON_TASK_FORCE_X_RECRUITMENT_DESIGN.md#3-special-five-condition-eligibility-contract), canon/continuity limits, scoped government provenance and voluntary four-stage assessment. No actual recruitment, prison transfer, supervision, combat, program backend, UI or save changes. |
| Restricted institutional assessment, number unassigned | After separately approved sentence/supervision/access and named-encounter/source contracts, consider one verified intermediary assessment with negotiation, refusal/reporting and ordinary recovery. [Dependencies and approval](GOON_TASK_FORCE_X_RECRUITMENT_DESIGN.md#9-future-roadmap-dependencies-and-acceptance--not-implementation) precede special-route completion or operations. No M021 implementation or guaranteed Squad career. |
| Optional late DARK slice, number unassigned | After a mature grounded arc and separately approved continuity, opt-in, source/power, cost and recovery policies, consider one bounded discrepancy/consultation with a credible ordinary alternative. The four-encounter achievement is optional, not an access gate. See [approval questions](GOON_DARK_PROGRESSION_CONTRACT.md#9-unresolved-decisions-requiring-user-approval). No M021 or supernatural implementation is authorized. |
| Future organization slice, number unassigned | First resolve continuity/source gaps; then separately approve one original, funded minor-crew commitment with consent, refusal, limited knowledge and independent resolution. See the [priorities](GOON_FACTION_EMPLOYER_MATRIX.md#future-priorities--approval-required). This is a recommendation, not M021 authorization. |
| Future combat milestone, number unassigned | Preserve the [historical M014 combat proposal](M014_COMBAT_DESIGN_CONTRACT.md). Requires a separate approved contract, health/recovery policy and compatible non-job legal-case source. |
| Future opening/content milestone, number unassigned | Review the [playable prologue contract](GOON_PLAYABLE_PROLOGUE_CONTRACT.md) and implement bounded employment/relationship choices using real systems. No guaranteed villain meeting or new faction tick. |

M015 implementation sequence: verify M014/237 tests; audit service/state and approve
the bounded choice contract; implement optional compatible state and actual local
settlements; add CLI views; execute five seven-day paths and longer replay/resume
campaigns; document results, review the diff, commit/push and open an unmerged PR.
The full five-chapter prologue remains future content, using these actual systems.

Historical M014 implementation sequence:

1. Verify clean master/198 tests; inspect service, persistence, legal/economic
   phases and atlas/audit contracts before coding.
2. Convert the 176 documented place rows, 63 corridors and 120 access spurs into
   local version-1 content; validate identities, metadata, hierarchy and costs.
3. Add versioned location state and read views; explicit historical adoption and
   post-court next-day activation preserve old history and all territory accounts.
4. Implement public-mode routing and service movement, separate TU accounting,
   restricted entry/lawful departure and finite closure/discovery outcomes.
5. Expose the home/store/return slice through the CLI; retain current job rules.
6. Test malformed content/saves, migrations, budgets, closures, isolation,
   insertion order, replay/resume and multi-day economic equivalence. Update
   README/state, review the diff, commit/push and open a PR; do not merge.

Compatibility constraints: outer save version 1 and all existing identifiers
remain; navigation owns no district income, faction power, evidence or job RNG.
No mandatory third-party package, service, graphical asset or wall-clock timer.
Later content/continuity changes must respect pinned definitions and historical
unknowns; merging M014 does not authorize the next milestone.

Mission 026 also removes Milo from the proposed future roster. The Court of Owls
is a separate optional late-game hidden organization, entirely undiscoverable
before the final third of **meaningful progression**, never elapsed days alone.
This is documentation only; no events, clues, rumors, symbols, dialogue, Talons,
encounters or runtime triggers are implemented. See the
[approved restriction](GOON_ROGUE_ENCOUNTERS_DESIGN.md#mission-026-approved-roster-restriction--design-only).

## 2026-11-07 direction addendum — third-person open world (future proposal)

The owner selected **third-person open-world** as the long-term game experience. React/terminal remain active interim clients and Python remains the sole authoritative simulation. The proposed [M031-3D / One Living Block](GOON_THIRD_PERSON_VERTICAL_SLICE.md) is a **parallel, isolated Godot 4 feasibility prototype**, not a replacement for M030-C2/GTG-13B, a milestone already implemented, or approval to start Godot integration. Earlier 2D-only presentation proposals are superseded as end-state direction, but historical contracts and test/merge records are unchanged.

| Track / gate | Proposed work | Must not be claimed until |
| --- | --- | --- |
| Active React/Python integration | Import latest QA-accepted frontend, restricted build, manifest/pin, actual host pairing, browser recovery and end-to-end acceptance | Verified on merged Python host and real browser; Builder mock QA alone is insufficient |
| M031-3D P0 (separate feasibility) | One stylized block greybox, third-person controller/camera/collision/door on Windows, no Python connection | Playtested offline build and measured camera/movement quality |
| M031-3D P1 | Home/store, three lightweight ambient NPC stand-ins and context prompts | Observable free exploration, accurate labeling of cosmetic vs simulated behavior |
| M031-3D P2 | Bounded Godot↔Python authenticated adapter and canonical location policy | Separate approved security/replay/migration contract and tests |
| M031-3D P3 | Tess real option, persistent choice and restart/lost-ack recovery | Actual service receipt with exactly-once effects, no fixture fallback |

Keep 3 gameplay actions and 18 travel TU unchanged until a tested amendment. Combat/chases, vehicles, seamless districts, continuous time and 3D coordinate persistence are **excluded** from P0–P3 unless later authorized. No new engine-dependent Python runtime requirement. Do not delay the current playable-week roadmap on an exploratory visual milestone; do not merge the exploratory client into the main runtime without its own architecture and acceptance evidence.


### 2026-11-07 interim GTG-13B source caution

An uploaded as-is working-tree snapshot at HEAD `f2e75dd959c5` contains the uncommitted `frontend/` import and local-host read-only inspection changes on `feature/m030-c2b-frontend-integration`. Codex reported frontend/local browser progress before hitting its usage limit, but final Python regression, independently approved release pin, reproducibility, review and commit were not completed. **GTG-13B remains in progress/unaccepted; GTG-14 and GTG-15 remain blocked.** This docs-only 3D addendum does not endorse or overwrite those files.

## M030-C2B isolated stabilization — 2026-11-19

The isolated `stabilize/m030-c2b-20261118` candidate preserves the interrupted frontend and repairs session, outbox and packaging failures. Local mode remains explicitly read-only; preview remains synthetic. This supersedes the earlier interrupted-work status for the isolated candidate only: the original branch remains unchanged and uncommitted, and no GitHub merge or release approval is claimed. See [the stabilization report](M030_C2B_FINDINGS_AND_REPAIR_REPORT.md) and its exact test evidence. Python gameplay, 3 actions/day, 18 TU/day, saves and RNG are unchanged. Godot P1V-B/P1W remain separate protected work. Gameplay integration is a future approved mission.
