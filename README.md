# Gotham Underworld — M013 Sustainable Faction Competition

A deterministic, offline, single-player crime-city simulation and terminal RPG
prototype. Python 3.14 standard library only: no packages, external AI services,
or paid APIs are required.

This is an independent, unofficial prototype. Its intended future creative
setting is the DC universe; it has no endorsement, authorization, or affiliation
with DC, Warner Bros., or their partners. The executable retains its original
placeholder characters, factions, and districts. M013 introduces no DC characters,
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

## Faction economics and competition

From day two in a new career, factions use the economic profiles saved in
`competition.profiles`, bound through `competition.factions`. Existing careers
begin these rules on the day after migration, without replaying earlier turns.
The first-day income/mobilization contract and low-level legacy resolvers remain
compatible. Player commands and M012 heat/legal rules keep their existing budget.

Profiles are data, not character-name policies. New organizations can bind to an
independent profile without changing the engine. Defaults are copied into each
career, so customizing one save does not change another or the global defaults.
No new DC organizations or story content are included.

| Faction / profile | District revenue | Recovery income / power | Recruitment cost / gain | Treasury / recovery cap |
| --- | --- | --- | --- | --- |
| Harbor / `trade_network` | 125% | $6 / +2 | $6 / +7 | $240 / $60 |
| Carnival / `street_network` | 100% | $8 / +3 | $4 / +6 | $180 / $50 |
| Iron / `industrial_network` | 135% | $5 / +2 | $5 / +9 | $220 / $70 |

| Profile | Attack / defense cost | Expansion reserve | Minimum attack power | Defense / consolidation threshold |
| --- | --- | --- | --- | --- |
| Trade | $12 / $8 | $36 | 25 | 45 / 75 |
| Street | $10 / $9 | $28 | 20 | 35 / 65 |
| Industrial | $13 / $7 | $40 | 30 | 55 / 85 |

Daily district revenue is `max(1, wealth // 15) * revenue_percent // 100`,
credited only up to the treasury cap. Upkeep is operating cost + holdings times
holding cost + power divided by the upkeep divisor (integer division). Defaults
use $1 operating cost, $1 per holding, and divisors 35/40/30. Payment is limited
by available cash. Fully funded upkeep restores one power; a shortfall loses one.
Existing above-cap reserves are retained and spent normally, while receiving no
additional income until they fall below the cap.

Each faction gets **one operation per day**, in a deterministic rotating order
derived from seed, day, and sorted faction identifiers:

- **Recover:** spend the turn rebuilding an off-map network; add the profile's
  recovery income up to its recovery cap, and bounded organizational power.
- **Regroup:** pay the recruitment cost for faster power recovery.
- **Defend:** pay for control restoration in a threatened holding.
- **Expand:** pay for an offensive against an explicitly selected rival district.
- **Consolidate:** pay the defense cost for slower control improvement and some
  recruitment when there is no funded expansion target.

Low operating strength prioritizes regroup/recovery. Otherwise threatened owned
districts take priority, then insufficient reserves trigger recovery, funded
rival targets permit expansion, and secure holdings permit consolidation or
recruitment. Recent player expansion pressure affects defense assessment.
Invalidated targets, missing funding, changed profiles, or exhausted recovery
capacity produce explicit fallback reasons. Stale/missing plans are reassessed
from current resources and record that fallback.

Pressure reduces district control by 1–3 daily, stopping at one; it cannot hand
territory to an unfunded challenger. Modern transfers require a paid offensive
or player expansion, exhaust control, and reset it to 35 through one shared
ownership operation. The compatibility first-day/legacy pressure claim also
requires money and power. Attacks consume one attacker power and up to two
defender power, abstract organizational losses rather than a combat system.
All power changes remain within 0–100. Legacy seeded feuds continue; upkeep,
recovery, and recruitment counter their former long-term power collapse.

Faction income, upkeep, operations, captures, and fallbacks have structured
before/after values. `factions`, `strategy`, `intel`, and `briefing` expose the
results through detached reports. District numbering and targeting use stable
sorting rather than dictionary insertion order. Modern economy/strategy/warfare
resolvers share the existing daily markers and do not execute twice in a day.

Reproduce the idle-city audit with `python -B faction_campaigns.py`. See
[M013_SIMULATION_REPORT.md](M013_SIMULATION_REPORT.md) for the actual four
365-day campaigns and one 1,000-day campaign. Iron leads every one-year sample;
Harbor leads at day 1,000 in seed 42. All factions remain operational, including
displaced organizations. Tests enforce bounds and recovery, not equal outcomes.

This remains a three-district economy with static wealth and abstract power.
Defensive identity has a strong early advantage in the tested seeds; recovering
factions often approach maximum readiness while still poor or displaced. There
is no elimination mechanic: default profiles all have a funded rebuilding path.
No rank-based handicap, forced turnover, or equalizing grant is applied.
The economic/strategic roster is configurable; the retained legacy feud sampler
still uses the original three gangs. Expanding that sampler is separate from
adding economic profile bindings.

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
M013 adds `competition_version: 1` with persisted economic definitions/bindings
and an activation day. M001-M012 careers keep their existing values and event
history on load; competition starts on the following advanced day. Unsupported
versions, missing profile state, invalid economic parameters, and inconsistent
economic event metadata are rejected. Profile edits are local to that career.

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
| Economic identities and modern faction operations | `faction_profiles.py`, `faction_competition.py` |
| Shared ownership mutation | `territory.py` |
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
modules. M013 does not migrate content. Future registries should separate stable
IDs from display names and keep character/faction, dialogue, mission/event,
asset, and progression data separate from mechanics. New systems should extend
the command/event interfaces and explicit additive save migrations, without
requiring a particular fictional property.

## Determinism, tests, and scope

RNG remains local to seeded operations. M013 preserves legacy job outcomes and
adds no random draws. Command history, action usage, investigation markers,
committed responses, and review dates
survive saving. Reports and snapshots expose no mutable world references.

Tests include all 166 M012 regressions, real M001-M012 fixtures, persistence failure
injection, malformed saves, command atomicity, CLI save/resume, fresh-process
hash-seed checks, a 365-day campaign with disk resumes, and a 90-day legal-choice
replay/resume. M012 covers heat/risk bounds, legal atomicity, event integrity,
and multi-day review/court outcomes. M013 adds economic identity, recovery,
recruitment, profile validation, transfer reconstruction, phase idempotency,
insertion-order independence, and the required multi-seed long campaigns. See
`tests/fixtures/README.md` for provenance.

Economic balance, courts, NPC policies, and the three-district geography remain simplified.
Unanswered cases still resolve automatically; responses support documented
collection cases and charged cases. No attorneys, warrants, probation, parole,
undercover officers, combat, drugs, Bat-family encounters, or M014 systems are
included. The prototype remains offline-capable.
