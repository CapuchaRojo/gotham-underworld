# Milestone scope and implementation plan

Mission 007 supersedes the earlier proposed M014 combat numbering. M013.1 is
merged at `8b68e1e`; its atlas and narrative documents remain design provenance.

| Milestone | Scope / approval |
| --- | --- |
| M014 | Authorized world runtime/navigation foundation: local validated atlas, optional versioned location state, deterministic public movement, CLI and regression coverage. No combat or prologue implementation. |
| M015, Mission 009 | Authorized [Living Gotham slice](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md): optional room terms, local lawful/criminal work, finite choices, two original contacts, promises, cash ledger and idempotent day processing. Submit an open PR; no merge authorization. |
| Subsequent verified integration | M015 PR #15 and M016-A PR #16 merged. Night Shift is on master at `43d8197`; provenance integration PR #18 merged at `8bc9700`; M018 PR #19 merged at `d0723b1`, preserving original ancestry. Historical instructions above describe their original mission scope. |
| M019, Mission 023 | Local-only bounded institutional knowledge/response from `d0723b1`: civilian desk, police intake, explicit adoption, causal reporting/correction, delayed independent queues, replay tests and documentation. No push, PR, merge or further milestone authorized. |
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
