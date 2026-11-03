# Gotham: The Goon — Project State

- Working title: **Gotham: The Goon**; subtitle: *A Living Gotham Crime RPG*
- Positioning: "Everybody wants to rule Gotham. You're just trying to survive it."
- Documentation milestone: **M013.1 — Branding & Narrative Foundation**, for review
- Runtime baseline: **M013 — Sustainable Faction Competition**, merged via PR #12
  at `eb931ce33c079018159aad14c2327561d9fa195f`; 198 regression tests
- Stack: Python 3.14 standard library; offline; no mandatory services or packages
- Entry point: `python gameplay.py`; resume with `python gameplay.py --load`
- Save contract: version 1; additive migration of unversioned M001-M010 saves
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

This milestone changes Markdown documentation only. Repository/module names,
package structure, save identifiers, runtime definitions, CLI/workflow labels,
and all existing gameplay remain intact. Historical Gotham Underworld references
are retained where they identify an existing interface or past milestone.

- [Narrative bible](docs/GOON_NARRATIVE_DESIGN_BIBLE.md): ordinary workers as
  protagonists; workplace comedy, crime drama, survival, relationships, and many
  possible careers. Separates implemented behavior, endorsed creative direction,
  proposed mechanics, and speculative concepts. Endorsed direction is not
  implementation authorization or a delivery schedule.
- [Employer matrix](docs/GOON_FACTION_EMPLOYER_MATRIX.md): nine proposed DC employer
  cultures; recruitment, compensation, risk, loyalty, advancement and fallout.
  Broad canonical anchors are sourced; workplace mechanics are original proposals.
- [Gameplay principles](docs/GOON_GAMEPLAY_PRINCIPLES.md): sourced historical
  criticism, seven feature gates, current mechanical shallows, a current-game
  reproduction recipe and paper exercises. No new player decisions or consequences
  are implemented by M013.1.
- [Content architecture](docs/GOON_CONTENT_ARCHITECTURE.md): future stable IDs and
  definitions, separate runtime facts/knowledge/presentation, service-driven GUI
  and narrative, and the legal case-source integration prerequisite for combat.
- [M014 combat contract](docs/M014_COMBAT_DESIGN_CONTRACT.md): proposed bounded
  solo turns, health/stamina, injury/recovery, exits, legal/reputation outcomes,
  deterministic resume, high-threat survival and future crew extension points.
  Numerical rules and acceptance criteria await review; combat is not implemented.

## Validation

Run `python -B -m unittest discover -s tests -v`.

The M013.1 scope retains all 198 existing tests and adds no runtime tests for
documentation-only changes. The complete suite must be rerun before its PR;
future combat scenarios and acceptance criteria are not passing-test claims.

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

M013 is merged. Review the M013.1 feature PR and M014 contract before authorizing
any M014 implementation. Review tactical/daily action separation, exit/recovery
guarantees, tuning/style modifiers, initial fixture scope and the compatible
legal-source migration. No large content migration or new gameplay is authorized
by these documents. Do not merge automatically or begin M014 in this milestone.
`INSTALL_M002.md` through `INSTALL_M010.md` describe historical installations,
not the current setup workflow.
