# Milestone scope and implementation plan

Mission 007 supersedes the earlier proposed M014 combat numbering. M013.1 is
merged at `8b68e1e`; its atlas and narrative documents remain design provenance.

| Milestone | Scope / approval |
| --- | --- |
| M014 | Authorized world runtime/navigation foundation: local validated atlas, optional versioned location state, deterministic public movement, CLI and regression coverage. No combat or prologue implementation. |
| M015, proposed after M014 audit | [Daily Life & Opportunity Engine](GOON_M015_DAILY_LIFE_CONTRACT.md): one explicit room obligation, local lawful/criminal work offers, finite opportunities, two original recurring contacts, and one idempotent day phase. Planning only; no implementation in Mission 008. |
| Future combat milestone, number unassigned | Preserve the [historical M014 combat proposal](M014_COMBAT_DESIGN_CONTRACT.md). Requires a separate approved contract, health/recovery policy and compatible non-job legal-case source. |
| Future opening/content milestone, number unassigned | Review the [playable prologue contract](GOON_PLAYABLE_PROLOGUE_CONTRACT.md) and implement bounded employment/relationship choices using real systems. No guaranteed villain meeting or new faction tick. |

M014 implementation sequence:

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
