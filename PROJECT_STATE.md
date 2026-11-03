# Project State

- Milestone: **M013 — Sustainable Faction Competition**
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

## Validation

Run `python -B -m unittest discover -s tests -v`.

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

Review the M013 feature PR before any M014 work. Do not merge automatically.
`INSTALL_M002.md` through `INSTALL_M010.md` describe historical installations,
not the current setup workflow.
