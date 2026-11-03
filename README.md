# Gotham Underworld — M011 Career Integrity & RPG Foundation

A deterministic, offline, single-player crime-city simulation and terminal RPG
prototype. Python 3.14 standard library only: no packages, external AI services,
or paid APIs are required.

This is an independent, unofficial prototype. Its intended future creative
setting is the DC universe; it has no endorsement, authorization, or affiliation
with DC, Warner Bros., or their partners. The executable retains its original
placeholder characters, factions, and districts. M011 introduces no DC characters,
new storylines, combat, or imported assets. Any proposed public distribution,
commercial release, fundraising, or external pitch materials need separate
rights and legal review.

## Start or resume a career

From the repository directory in PowerShell:

```powershell
python gameplay.py
python gameplay.py --load
python gameplay.py --seed 17 --save career_second_save.json
python gameplay.py --load --save career_second_save.json
python -B -m unittest discover -s tests -v
```

The default save is `career_save.json`. Starting a new game refuses an existing
save path: resume with `--load` or choose another `--save` filename. A file
appearing after startup is also protected on the first save.

`save` persists the career; `quit` saves before exiting. EOF or Ctrl+C at the
prompt exits without saving unsaved changes. The seed initializes a new career;
loading retains the seed stored in the save.

## Career commands and actions

| Command | Behavior |
| --- | --- |
| `help`, `status` | Commands, cash, heat, affiliation, reputation, cases, and remaining actions |
| `factions`, `join <1-3>` | View or join an existing faction; recruitment is free |
| `jobs`, `job courier`, `job collection` | View jobs or attempt one; each attempt costs one action, including failures |
| `districts`, `missions` | Inspect districts and mission numbers |
| `mission <kind> <district-number>` | Scout, fortify, or expand; costs one action plus its cash price |
| `relationships`, `strategy` | View NPC policies and faction plans |
| `intel`, `briefing [day]`, `events` | View city reports and recent events |
| `wait` | Advance exactly one day and refresh the daily allowance |
| `save`, `quit` | Save the career; quit also exits |

There are **three shared actions per day** for jobs and district missions.
The existing one-district-mission-per-day restriction also applies. Reports,
recruitment, saving, and waiting are free. Invalid, unaffordable, or exhausted
commands do not change game state or consume RNG attempts.

Loading does not refresh actions. Legacy migration counts recorded jobs and
district missions on the current day, capped at three.

## Safe saves and compatibility

M011 uses `save_version: 1`; unversioned M001-M010 careers receive additive
defaults. Unknown fields are retained. Unsupported save/subsystem versions,
malformed nested data, duplicate case IDs, invalid references, and inconsistent
custody state are rejected before play.

Versioned M011 saves must contain their required subsystem state. Missing
territory or relationship data is an error rather than a reason to reset it.
Migrations do not replay events, pay old income, or execute old faction turns.

Saving stages and flushes UTF-8 JSON in the destination directory, then uses
`os.replace` to publish it. Overwriting first preserves the previous valid bytes
at `<save filename>.bak`. If staging or backup fails, the destination is untouched.
If replacement fails, the old destination and a recoverable backup remain.
An invalid existing destination cannot replace a good backup.

To recover a damaged career, preserve it separately, copy its `.bak` file back
to the original filename, then resume with `--load`. Recovery is explicit; the
loader does not silently substitute an older save.

First-save publication uses a hard link to avoid replacing a competing file.
The destination filesystem must support that operation and same-directory
replacement; unsupported operations fail without an unsafe overwrite fallback.
Save directories must exist. Saves assume one writer per career; cross-process
conflict resolution is not implemented. Power-loss durability depends on the
operating system and filesystem.

## Architecture and extension points

`game_service.py` is the player-facing boundary for the CLI and future interfaces:

```python
from game_service import (
    create_career, load_career, save_career,
    execute_command, advance_day, snapshot,
)

world = create_career(seed=42)
execute_command(world, 'join', faction='Harbor Syndicate')
result = execute_command(world, 'job', kind='courier')
advance_day(world)
view = snapshot(world)  # Detached; edits cannot affect the career.
save_career(world, 'career_example_save.json', overwrite=False)
```

Stable command IDs are `join`, `job`, `mission`, and `wait`; arguments are named
JSON-shaped fields. Successful commands return detached results, emitted events,
a persisted sequence number, and remaining actions. A `player_command` event
records the command ID, arguments, actor, and action cost. Consumers should use
event kinds and structured fields rather than parse narrative messages.

Commands execute against a private world copy and commit only on success.
Callers may retain the root dictionary, but should use snapshots rather than
retain live nested references across commands. Copying favors correctness over
large-world performance at this prototype scale.

| Layer | Modules |
| --- | --- |
| CLI and command boundary | `gameplay.py`, `game_service.py` |
| Save contract, defaults, persistence | `career_state.py`, `career_persistence.py` |
| Base world, events, legacy feuds and courts | `simulation.py` |
| Jobs, investigation, NPC relationships/actions | `consequence_engine.py`, `relationship_engine.py`, `npc_actions.py` |
| Economy, missions, strategy, warfare | `city_economy.py`, `district_missions.py`, `city_strategy.py`, `faction_warfare.py` |
| Detached reports | `city_intelligence.py`, strategy assessment/summary |

Daily order remains: base clock/feuds/legacy investigations, career investigations,
NPC actions, economy, planning, warfare, then court. Investigation runs once per
case per day; NPC acceleration remains separate with its existing cooldown.
Warfare revalidates current targets; invalidated or unfunded plans emit an
explicitly explained hold action.

The legacy `gameplay.job` reducer intentionally remains unbounded for existing
simulation tools/tests. Player-facing integrations must use `execute_command`.
The original `python simulation.py --days 10 --seed 42` batch demonstration
remains available; it is not the career interface.

Current content definitions and named NPC policies remain in their original
modules. M011 does not migrate content. Future registries should separate stable
IDs from display names and keep character/faction, dialogue, mission/event,
asset, and progression data separate from mechanics. New systems should extend
the command/event interfaces and explicit additive save migrations, without
requiring a particular fictional property.

## Determinism, tests, and scope

RNG remains local to seeded operations. M011 preserves legacy job outcomes and
adds no random draws. Command history, action usage, and investigation markers
survive saving. Reports and snapshots expose no mutable world references.

Tests include all 86 M010 regressions, real M001-M010 fixtures, persistence failure
injection, malformed saves, command atomicity, CLI save/resume, fresh-process
hash-seed checks, and a 365-day deterministic campaign with disk resumes. See
`tests/fixtures/README.md` for provenance.

Economy balance, heat, instant court outcomes, NPC policies, and faction recovery
remain simplified. Combat, crews, health, contraband, legal supervision, campaign
arcs, vigilantes, and a graphical interface are outside M011.
