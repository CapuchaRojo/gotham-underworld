# Project State

- Milestone: **M011 — Career Integrity & RPG Foundation**
- Stack: Python 3.14 standard library; offline; no mandatory services or packages
- Entry point: `python gameplay.py`; resume with `python gameplay.py --load`
- Save contract: version 1; additive migration of unversioned M001-M010 saves
- Validation: nested state, versions, references, and custody consistency
- Persistence: staged writes, atomic replacement, previous-valid `.bak`, exclusive
  first-save publication, and protection against silent new-career overwrites
- Action economy: three shared daily job/mission actions through `game_service`;
  legacy low-level job resolution remains unchanged
- Command interface: create/load/save, execute commands, advance one day, detached
  snapshots, persisted command sequence, and structured command events
- Investigation: per-case daily idempotency while preserving NPC acceleration
- Warfare: target/funding validation and explicitly attributed hold fallbacks
- Intelligence: detached reports and non-mutating strategy assessments

## Validation

Run `python -B -m unittest discover -s tests -v`.

The original 86 tests remain unchanged. New coverage includes persistence failure
injection, malformed/current-version state, M001-M010 migration fixtures, bounded
commands and rollback, CLI protection/resume, report isolation, warfare fallbacks,
investigation replay protection, fresh-process determinism, and a 365-day campaign.
Execution results belong in the feature PR rather than a permanently current claim.

## Architecture and creative constraints

Daily phase order and existing job RNG rules are preserved. Player interfaces use
`game_service.execute_command`; views use detached snapshots. Dictionary saves
and current content names are retained. M011 adds no combat, DC characters,
storylines, imported assets, or M012 systems.

The creative direction is an independent, unofficial prototype intended for a
future DC-universe crime RPG pitch, without endorsement, authorization, or
affiliation. Executable content remains original placeholders. Future content
should use stable identifiers and definitions separated from mechanics, dialogue,
missions/events, assets, and progression. Proposed distribution, commercialization,
fundraising, or pitch materials require separate rights review.

## Known limits and next review

Court timing, heat, economic balance, and defeated-faction recovery remain
simplified. Command transactions copy the world. Saves assume one writer and a
filesystem supporting hard links and replacement. Recovery is explicit; no GUI
is included.

Review the M011 feature PR before any M012 work. Do not merge automatically.
`INSTALL_M002.md` through `INSTALL_M010.md` describe historical installations,
not the current setup workflow.
