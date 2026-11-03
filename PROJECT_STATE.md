# Project State

- Milestone: **M012 — Meaningful Crime & Consequences**
- Stack: Python 3.14 standard library; offline; no mandatory services or packages
- Entry point: `python gameplay.py`; resume with `python gameplay.py --load`
- Save contract: version 1; additive migration of unversioned M001-M010 saves
- Legal contract: independent `legal_version: 1`; additive M001-M011 migration
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

## Validation

Run `python -B -m unittest discover -s tests -v`.

All 131 M011 tests remain unchanged. Coverage includes persistence failure
injection, malformed/current-version state, M001-M010 migration fixtures, bounded
commands and rollback, CLI protection/resume, report isolation, warfare fallbacks,
investigation replay protection, fresh-process determinism, a 365-day campaign,
and M012 heat bounds, legal invariants/atomicity, M011 migration, multi-day reviews,
zero-cash recovery, and a 90-day legal replay/resume.
Execution results belong in the feature PR rather than a permanently current claim.

## Architecture and creative constraints

Daily processing adds legal reviews/cooling before career investigation. Existing
job RNG draws and low-level job rules are preserved. Player interfaces use
`game_service.execute_command`; views use detached snapshots. Dictionary saves
and current content names are retained. Legal rules have no character-name policies.
M012 adds no combat, drugs, probation/parole, undercover officers, Bat-family
encounters, storylines, imported assets, or M013 systems.

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
and defeated-faction recovery remain simplified. Commands copy the world.
Saves assume one writer and a
filesystem supporting hard links and replacement. Recovery is explicit; no GUI
is included.

Review the M012 feature PR before any M013 work. Do not merge automatically.
`INSTALL_M002.md` through `INSTALL_M010.md` describe historical installations,
not the current setup workflow.
