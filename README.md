# Gotham Underworld — M012 Meaningful Crime & Consequences

A deterministic, offline, single-player crime-city simulation and terminal RPG
prototype. Python 3.14 standard library only: no packages, external AI services,
or paid APIs are required.

This is an independent, unofficial prototype. Its intended future creative
setting is the DC universe; it has no endorsement, authorization, or affiliation
with DC, Warner Bros., or their partners. The executable retains its original
placeholder characters, factions, and districts. M012 introduces no DC characters,
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
| `legal` | Inspect heat, police attention, cases, and committed responses |
| `lay_low` | Reduce heat; one action, no cash cost, once per day |
| `cooperate <case-id>` | Document evidence and reduce the eventual conviction fine |
| `contest <case-id>` | Pay for a two-day review of a documented pending case |
| `accept <case-id>` | Admit a pending/charged case and resolve consequences immediately |
| `intel`, `briefing [day]`, `events` | View city reports and recent events |
| `wait` | Advance exactly one day and refresh the daily allowance |
| `save`, `quit` | Save the career; quit also exits |

There are **three shared actions per day** for jobs, district missions, and legal responses.
The existing one-district-mission-per-day restriction also applies. Reports,
recruitment, saving, and waiting are free. Invalid, unaffordable, or exhausted
commands do not change game state or consume RNG attempts.

Loading does not refresh actions. Legacy migration counts recorded jobs and
district missions on the current day, capped at three.

## Heat, exposure, and legal choices

Player commands keep effective heat between **0 and 100**. Attention is derived
from heat, not hidden rolls:

| Heat | Attention | Added job failure / collection witness chance | Extra daily evidence |
| --- | --- | --- | --- |
| 0–19 | Low | 0 percentage points | 0 |
| 20–49 | Elevated | 5 percentage points | 0 |
| 50–79 | High | 10 percentage points | 1 |
| 80–100 | Critical | 15 percentage points | 1 |

Extra investigation applies only to existing documented pending cases. Heat
alone never creates a case or authorizes arrest. NPC acceleration still requires
a documented case and retains its cooldown.

Courier work pays $25 on success and creates no new criminal case. It adds one
heat only on failure. Collection pays $60 but adds 2/3/4/5 heat across the four
tiers, plus one on failure. Witness chance starts at 35% on success or 65% on
failure, adds the tier modifier, and caps at 90%. Job failure chance uses existing
reputation plus the modifier, capped at 75% for player commands. Outcomes use the
existing seeded draws without rerolls or global RNG. Failed collections retain
their existing faction consequences.

`legal` shows case IDs and evidence. Each response costs one daily action:

| Action | Prerequisites and cash cost | Effects |
| --- | --- | --- |
| `lay_low` | Free, not detained, positive heat, once/day | Heat -12; existing evidence remains |
| `cooperate <id>` | Free, not detained, documented pending witness case | Heat -8, evidence +1, eventual conviction fine $30 instead of $50; court reduces heat by 4 |
| `contest <id>` | $20, not detained, documented pending witness case | Freeze that case's ordinary/NPC investigation until review two days later; evidence <=1 dismisses it; stronger evidence continues, adds 3 heat, and retains the normal $50 conviction fine |
| `accept <id>` | Pending/charged case; cannot bypass a different charged case | Immediate admission and conviction, fine $35, heat -10, custody released; no city-day advancement |

One response is committed per case; it cannot be stacked or switched. Contesting
does not stop other investigations or city activity. Fines are capped by cash on
hand and never create debt. Ignoring a case preserves automatic court handling
on arrest, so an exhausted allowance cannot trap the player in custody. Lay low
requires no cash. A complete day without collection/crime provides another 2 heat
reduction on the following daily tick. These are simplified game rules, not a
model of real legal procedure.

The persisted `legal_version: 1` / `legal` extension stores responses, review
dates, daily processing markers, and unique outcome records. New outcomes record
their dates, assessed fines, actual payments, and response. Migrated convictions
and dismissals retain unknown historical dates/fines as null. No warrants,
probation, parole, supervision, undercover agents, or vigilante encounters are
implemented; later versions can add sections without character-name rules.

## Safe saves and compatibility

M011 uses `save_version: 1`; unversioned M001-M010 careers receive additive
defaults. Unknown fields are retained. Unsupported save/subsystem versions,
malformed nested data, duplicate case IDs, invalid references, and inconsistent
custody state are rejected before play.

Versioned M011 saves must contain their required subsystem state. Missing
territory or relationship data is an error rather than a reason to reset it.
Migrations do not replay events, pay old income, or execute old faction turns.
M012 retains that outer contract and independently versions legal state. M001-M011
careers initialize it without refreshing actions or rewriting historical events.
Unsupported legal versions and inconsistent responses, records, or legal/heat
event metadata are rejected; unknown extension fields are retained. An old raw
heat counter above 100 is preserved on load, displayed as effective heat 100,
then normalized with an audit event on the next successful player command.

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

Stable command IDs are `join`, `job`, `mission`, `wait`, `lay_low`, `cooperate`,
`contest`, and `accept`; arguments are named string fields. Legal case IDs are
positive number strings: `execute_command(world, 'contest', case_id='1')`.
Successful commands return detached results, emitted events,
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
| Heat policy, legal choices, profile schema | `legal_engine.py`, `legal_state.py` |
| Economy, missions, strategy, warfare | `city_economy.py`, `district_missions.py`, `city_strategy.py`, `faction_warfare.py` |
| Detached reports | `city_intelligence.py`, strategy assessment/summary |

Daily order is: base clock/feuds/legacy investigations, legal reviews/quiet-day
cooling, career investigations with heat scrutiny,
NPC actions, economy, planning, warfare, then court. Investigation runs once per
case per day; contested cases defer ordinary and NPC evidence until review.
NPC acceleration otherwise retains its existing cooldown.
Warfare revalidates current targets; invalidated or unfunded plans emit an
explicitly explained hold action.

The legacy `gameplay.job` reducer remains unbounded with its original risk/heat
rules for existing tools/tests. Player interfaces must use `execute_command` for
M012 risk and legal rules. Explicit case choices are also honored by the legacy
daily reducer.
The original `python simulation.py --days 10 --seed 42` batch demonstration
remains available; it is not the career interface.

Current content definitions and named NPC policies remain in their original
modules. M012 does not migrate content. Future registries should separate stable
IDs from display names and keep character/faction, dialogue, mission/event,
asset, and progression data separate from mechanics. New systems should extend
the command/event interfaces and explicit additive save migrations, without
requiring a particular fictional property.

## Determinism, tests, and scope

RNG remains local to seeded operations. M012 preserves legacy job outcomes and
adds no random draws. Command history, action usage, investigation markers,
committed responses, and review dates
survive saving. Reports and snapshots expose no mutable world references.

Tests include all 131 M011 regressions, real M001-M011 fixtures, persistence failure
injection, malformed saves, command atomicity, CLI save/resume, fresh-process
hash-seed checks, a 365-day campaign with disk resumes, and a 90-day legal-choice
replay/resume. M012 covers heat/risk bounds, legal atomicity, event integrity,
and multi-day review/court outcomes. See
`tests/fixtures/README.md` for provenance.

Economy balance, courts, NPC policies, and faction recovery remain simplified.
Unanswered cases still resolve automatically; responses support documented
collection cases and charged cases. No attorneys, warrants, probation, parole,
undercover officers, combat, drugs, Bat-family encounters, or M013 systems are
included. The prototype remains offline-capable.
