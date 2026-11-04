# Gotham: The Goon

*A Living Gotham Crime RPG*

> Everybody wants to rule Gotham. You're just trying to survive it.

A deterministic, offline, single-player crime-city simulation and terminal RPG
prototype about an ordinary criminal surviving work, loyalties, and a changing
city. Python 3.14 standard library only: no packages, external AI services,
or paid APIs are required. The local executable includes **M016-A — optional
versioned mobility and a two-station monorail pilot**, alongside M015 daily life
and the merged M014 navigation foundation. This is an isolated implementation
for review; M015 PR #15 remains open and unmerged. Broader M016 vehicle systems
and combat are not implemented.

This is an independent, unofficial prototype. Its intended future creative
setting is the DC universe; it has no endorsement, authorization, or affiliation
with DC, Warner Bros., or their partners. The executable retains its original
placeholder characters, factions, and districts. M013 introduces no DC characters,
new storylines, combat, or imported assets. The working title and setting are
subject to future licensing and title clearance. Any proposed public distribution,
commercial release, fundraising, or external pitch materials need separate
rights and legal review.
No DC license is claimed, and the working title is not legally cleared.

## Design foundation and status

Ordinary goons are the protagonists. Professional henchman, lieutenant,
independent operator, boss, informant, reformed citizen, and tragic casualty are
future career possibilities, not an implemented campaign or a single promotion
ladder. The intended tone combines dark workplace comedy, street-level crime
drama, survival, and occasional horror. Current gameplay is described below;
the first local work, room obligations and two original contacts are implemented
in M015. Broader careers, combat and DC character content remain design work.

M014 loads the complete documented atlas as local data and implements a small
home/store/return slice with public navigation. See the
[runtime contract](docs/GOON_WORLD_RUNTIME.md),
[current roadmap](docs/GOON_MILESTONE_ROADMAP.md), and
[future prologue contract](docs/GOON_PLAYABLE_PROLOGUE_CONTRACT.md).
Older design documents describe M013.1 proposals; the runtime contract identifies
the implemented subset and supersedes their historical M014 combat numbering.

| Document | Purpose |
| --- | --- |
| [Narrative design bible](docs/GOON_NARRATIVE_DESIGN_BIBLE.md) | Player fantasy, tone, 16 design areas, feature-status legend, and originality boundaries |
| [Criminal career web](docs/GOON_CRIMINAL_CAREER_WEB.md) | Nineteen overlapping specializations, lawful work, informing, rehabilitation, retirement and three worked scenarios |
| [Conditional opportunities](docs/GOON_CONDITIONAL_OPPORTUNITIES.md) | Eligibility, demand, recorded probability, expiry and viable careers without guaranteed villain meetings |
| [Faction and employer matrix](docs/GOON_FACTION_EMPLOYER_MATRIX.md) | Eleven proposed employer cultures, entry, pay, risk, advancement, and consequences |
| [Rogues gallery registry](docs/GOON_ROGUES_GALLERY_REGISTRY.md) | Thirty-five versioned entries with lore/source boundaries and original jobs/roles; no guaranteed active roster |
| [Minor criminal ecosystem](docs/GOON_MINOR_CRIMINAL_ECOSYSTEM.md) | Major factions, minor crews and individuals; original workers and rise/fall/exit proposals without universal territory simulation |
| [Joker recruitment contract](docs/GOON_JOKER_RECRUITMENT.md) | Original campaign proposal: street association differs from formal Arkham/direct-encounter initiation |
| [Metropolitan atlas](docs/GOON_GOTHAM_ATLAS.md) | Original 8-region geography and source/continuity decisions; no traced or rendered map |
| [Location registry](docs/GOON_LOCATION_REGISTRY.md) | 48 neighborhoods and 120 POIs with IDs, access, economy, security, civilian/criminal activities and potential contacts |
| [Travel network](docs/GOON_TRAVEL_NETWORK.md) | Source design for M014's implemented modes, closures and separate TU allowance; vehicles/schedules deferred |
| [Map/simulation integration](docs/GOON_MAP_SIMULATION_INTEGRATION.md) | Preserve the three territory accounts while adding optional hierarchical geography through a future reviewed migration |
| [Career geography](docs/GOON_CAREER_GEOGRAPHY.md) | Location-dependent work, civilian life, care and meaningful commitments rather than commute grind |
| [Map visual specification](docs/GOON_MAP_VISUAL_SPEC.md) | Future layered views with player-knowledge boundaries; no GUI or map image |
| [Villain influence and recovery](docs/GOON_VILLAIN_INFLUENCE_SYSTEM.md) | Fictional exposure, coercion, resistance, consent and credible recovery; no clinical implementation |
| [Institutions and recovery](docs/GOON_INSTITUTIONS_AND_RECOVERY.md) | Distinct Blackgate, Arkham, voluntary care, review and reentry paths with continuity/agency rules |
| [Gameplay principles](docs/GOON_GAMEPLAY_PRINCIPLES.md) | Sourced reference-game lessons, meaningful-choice gates, current limits, and manual scenarios |
| [Content architecture](docs/GOON_CONTENT_ARCHITECTURE.md) | Proposed definition/state separation and service integration; no content migration |
| [Deferred combat design contract](docs/M014_COMBAT_DESIGN_CONTRACT.md) | Retained historical M014 proposal; future milestone unassigned, no combat implementation |
| [Project state](PROJECT_STATE.md) | Runtime capabilities, compatibility, limitations, and next review |
| [Final integration audit](docs/M013_1_FINAL_INTEGRATION_AUDIT.md) | Verified corrections, compatibility findings, reproducible graph/document checks and conditional merge gates |
| [M014 validation](docs/M014_VALIDATION_REPORT.md) | Executed regressions, historical compatibility, real CLI walkthrough and reproducible navigation campaigns |
| [M014 final audit](docs/M014_FINAL_AUDIT.md) | Independent acceptance gates, corrections, compatibility results and PR disposition |
| [M015 daily-life contract](docs/GOON_M015_DAILY_LIFE_CONTRACT.md) | Implemented scope and historical readiness proposal |
| [Consequential choices](docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md) | Stable choices, known prerequisites, settlement, branches and recovery |
| [M015 validation](docs/M015_VALIDATION_REPORT.md) | Executed campaigns, regressions, compatibility, economy findings and limits |

M013.1 preserves the `gotham-underworld` repository name, Python modules, package
layout, save filenames/identifiers, and historical milestone documents. The CLI
banner and prompt use the new working title; historical and workflow labels still
identify Gotham Underworld. Technical renames require a separately approved
migration plan. None of the proposed DC employers is added to the executable or
substituted for an existing faction.
M014 is navigation only; combat and the prologue remain future design work.
The rogues addendum changes documentation only. Its roster is not assumed to
coexist in every continuity, and no minor crew automatically becomes a district
owner. Formal Joker initiation is optional and conditional; a career can finish
without it. That addendum implemented no rogue, recruitment gate or save field.
The M013.1 city-atlas design supplied 176 place records (8 regions, 48 neighborhoods,
120 POIs) and an original network specification, now loaded as M014 content.
Geography, faction territory, minor-crew influence, properties and police coverage
are separate. Existing jobs, legal rules and faction accounting retain M013 behavior;
M014 implements the bounded subset documented below, with a CLI and no GUI.

## World navigation and the playable slice

New careers start at **East Side Housing Cooperative** in Upper East Side,
with recorded home access and the existing $40 start. Enter:

```text
look
nearby
route p032
travel p032
look
join 1
job courier
travel home
wait
save
quit
```

The store visit and return cost **2 travel TU**; the existing courier costs one
gameplay action. Saving/resuming preserves the home, location, spent TU, jobs and
day. `look` inspects a frontage, not a shop transaction or institutional admission.
The optional M015 slice below adds local wages and room obligations. No prologue,
health, combat or NPC scheduling is implemented.

| Navigation command | Behavior |
| --- | --- |
| `look [place]` | Current or known place metadata, entry requirements and free help |
| `nearby`, `places` | Known local destinations or public atlas; private homes need permission |
| `route <place> [mode]` | Detached preview of outbound/return TU and affordability |
| `travel <place> [mode]` | Atomic movement; before mobility adoption: `auto`, `walk`, `bus`, `rail`, `ferry`; adopted profiles below |
| `enable_navigation <neighborhood>` | Historical career opt-in at a public hub, active after next `wait` |

Use short IDs such as `p032`/`n13`, their full stable IDs, or `home` when a recorded
home exists. Regions are containers, not travel destinations. All mutations use
the game service. Read APIs are `location_report`, `nearby_destinations`,
`known_places`, and `plan_route`; commands take named string arguments, for example
`execute_command(world, 'travel', destination='p032', mode='auto')`.

Travel uses a separate **18-TU/day** initial policy and zero daily gameplay actions.
Walking/transit costs follow the atlas, with one TU per transit-mode boarding.
A completed local journey costs at least one TU, deliberately bounding the earlier
zero-cost-approach proposal. Inspections remain free; no travel grants rewards.
Known failures reject without mutation. A hidden closure stops a valid journey
at its last safe node and charges only its traversed prefix. Controlled closures
expire within two advanced days; there is no closure-editing player command or
random incident generator. Direction, mode and restricted entry are enforced.
Free visitors retain lawful egress; travel never bypasses custody or admits a
patient/prisoner. Cars, boats, schedules and emergency transport remain future work.

Not every journey fits eighteen TU: n01→n40 costs 19 one way. Preview the return,
choose nearby work or an explicit safe waypoint. Waiting advances the real city
once and refreshes both allowances; loading/reporting never does. Help, saving,
reports and explicit waiting remain available when broke or exhausted. Existing
jobs/missions remain location-independent, preserving legacy RNG and accounting.

Historical saves load with **no invented location/home** and unchanged budgets,
resources and events. Opt in explicitly, for example `enable_navigation n13`,
then `wait`. No navigation is imposed by migration or loading. The independent
`navigation_version: 1` extension pins atlas/rules/content fingerprint; missing or
incompatible required content fails clearly. All three existing territory accounts
remain authoritative; 176 places do not multiply income or warfare turns.

## Optional station mobility — M016-A

New and historical careers keep their existing navigation until explicit
adoption. Loading or inspecting never enrolls a career. Historical careers
without navigation first use `enable_navigation n17`, then `wait`.

| Command | Behavior |
| --- | --- |
| `mobility` | Detached status, adoption availability, stations and known service disruption information |
| `adopt_mobility` | Schedule mobility once; it activates during the next explicit `wait`, with no resource grant |
| `route <place> [profile]` | Read-only door-to-door TU/fare quote, policy return and free-return alternatives |
| `travel <place> [profile]` | Commit the quoted journey atomically using the existing CLI verb |
| `receipt <request-id>` | Inspect a detached accepted-request receipt without repeating effects |

After activation, profiles are `auto` (alias `fastest`), `free`, `walk`, `bus`,
`ferry`, `monorail`. Legacy abstract `rail` is retired **only for adopters**.
Old rail journeys and all non-adopted routing keep their original interpretation.
The pilot links **p039 Highbridge Metro Stop → p071 South Gate Subway Stop**,
following n17–n18–n23–n22–n30 via four existing atlas corridors. Only these two
public frontages have monorail gates; neighborhoods cannot board directly.

The **7 TU/$2** scope is frontage-to-frontage: zero-cost gates/alighting,
1-TU boarding and 6-TU ride. Actual approach/onward travel is additional. From
home, a walking-only approach to p039 adds 4 TU; `free` can use the existing
3-TU bus approach separately. Current p039↔p071 bus costs **8 TU/$0** each way;
walking costs 18. No fare is charged for merely previewing or reaching a station.

```text
mobility
travel p039
adopt_mobility
wait
route p071 monorail
travel p071 monorail
route p039 bus
travel p039 bus
save
```

The two committed station trips above use **15 TU/$2**, zero gameplay actions
and no day advance. Return previews target the journey origin by default,
preserving `route` semantics. The API can specify another `return_to`. They use
the actual cash/TU left after outbound settlement and distinguish policy return
from a free alternative. An outbound cap limits that transaction, not the actual
resources available for a later return command. Returns remain conditional on
known access/disruptions; a quote is not a reservation.

Known closures affect planning. An unknown underlying rail closure is observed
at the departure station before boarding; only an actual approach prefix is
charged, never the untraveled fare/ride. Free bus/walking remain available where
the atlas permits. With $0 and insufficient TU for the return, inspect/save and
explicitly wait; only a real day transition restores the normal 18 TU and three
actions. Waiting can expire an existing promise/offer. No paid rescue or vehicle
purchase is required; restricted institutions and custody remain enforced.

Service integrations use `execute_command(world, 'enable_mobility',
overlay_id=OVERLAY_ID, request_id='client.adopt.1')`, then `advance_day(world)`.
For travel, call `mobility.plan_route(world, 'p071', 'monorail')` and pass its
`arguments` to `execute_command(world, 'journey', **quote['arguments'])`.
Reuse the same request ID only to detect a retry: duplicates reject unchanged;
`mobility_receipt` retrieves the old receipt. Route views and responses are detached.

Outer save version stays 1. Opt-in pairs `navigation_version: 2` with
`mobility_version: 1`; pending routing remains rules1 until activation, then
rules2. Schema1 travel events are unchanged and checked at the legacy checkpoint;
schema2 events record typed legs, resource deltas, discoveries and charge/receipt
IDs. The base atlas fingerprint stays unchanged. Separately pinned overlay:
`d59fe323290fd1216d8b5e1ffdcde5924b123cedc0404ce22215d538779ec7ee`.
Missing/changed required content fails clearly; old binaries reject nav2 instead
of ignoring mobility. Existing atomic replacement/backup behavior is reused.

See the [implementation/validation report](docs/M016_A_IMPLEMENTATION_VALIDATION.md),
[architecture](docs/M016_MOBILITY_ARCHITECTURE.md),
[acceptance matrix](docs/M016_MOBILITY_ACCEPTANCE_MATRIX.md) and
[risk register](docs/M016_INTEGRATION_RISK_REGISTER.md). Repeat deterministic
campaign evidence with `python -B mobility_campaigns.py --days 365 --seeds 17 42
--resume-every 30`. These stress commutes are test policies, not reward-generating
missions. Vehicles, theft, licensing, impound, expanded schedules and the full
prologue remain unimplemented. The broader M016 milestone is not complete.

Local M016-A verification: **332 tests pass** (283 existing plus49 new), with
seeded365-day replay and final30-day daily disk-resume checks. Exact commands,
hashes, limitations and the distinction from existing GitHub CI are in the report.

## Living in the neighborhood — M015

Daily life is **explicitly optional** for every career, including a new one. Run
`life` to inspect terms, then `settle_in` at p031/home or n13 to accept them.
Offers activate after the next `wait`. Starting on day 0 preserves the real $40
and makes the first $30 cooperative room contribution due on day 7. Every later
review is seven days apart. Available cash is charged, prepaid contributions are
applied once, and an unpaid balance never exceeds $30. Basic home access continues
in grace, with no stacked rent/fees while that balance remains. One maintenance
opportunity per unpaid review can reduce it by up to $10 for one action, without cash.

| Command | Behavior |
| --- | --- |
| `life` | Detached terms, cash history, room dates, promises and a state-grounded thought |
| `settle_in` | Accept the disclosed room arrangement; activate next day without budget refresh |
| `home`, `pay_room` | Inspect home/deadlines, or prepay/pay a bounded amount at home |
| `contacts` | Tess and Cal's known roles, standing and observed interaction memories |
| `opportunities` | Finite local offers with stable IDs and opening/expiration days |
| `choices <id>` | Context, speaker, available options, known disabled reasons and action costs |
| `choose <id> <option-id>` | Revalidate and resolve once through the game service |
| `choose <id> A` | Use the letter mapped by your last `choices <id>` display; stable IDs remain authoritative |

First-day example, from a fresh home career:

```text
life
settle_in
wait
choices goon.choice.0.promise
choose goon.choice.0.promise promise
travel p032
choices goon.choice.0.opening_shift
choose goon.choice.0.opening_shift A
travel home
home
save
```

On day 2, inspect `goon.choice.0.crossroads`. A lawful shift pays $20 at the store;
keeping Tess's promise at home pays nothing but earns a reference; negotiation
moves the favor once to day 4; withdrawal forgoes the morning roster. These share
a disclosed roster slot. Cal's collection option appears only after his own
introduction at n13 and requires an explicitly chosen existing faction. It calls
the original legal job resolver once: up to $60, failure, heat and possible case
consequences. His observed successful referral may open quieter courier work.
No contact learns unrelated private work or police facts from these menus.

The referenced stock-audit shift pays $25 for two actions; ordinary repair work
pays $20 for one. Known follow-up offers also depend on current recorded standing;
broken commitments can put a reference on hold without removing basic work.
Offers expire and each settles once. Refusal is free, the shared
three-action/18-TU rules remain, and a week has a finite roster rather than a wage
button at every location. Save/load, reports and staying home grant no resources.
All five branches—lawful, criminal, relationship-first, low cash, and mixed—are
reproducible with `python -B daily_life_campaigns.py --days 7 --resume`.

Existing saves load without daily-life state or retroactive rent. Pre-navigation
careers first use `enable_navigation n13` and `wait`, then accept the room locally.
An unknown home can become p031 through that explicit agreement without moving
the player. An existing different home is never silently overwritten. The optional
`daily_life_version: 1` extension pins its own content and validates receipts,
cash, choices, promises and contact memories. Existing jobs remain available and
retain their rules. The five-chapter playable prologue remains future content.

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
| Local geography and navigation | `location_registry.py`, `navigation.py` |
| Contextual choices | `choice_engine.py`; stable records, visibility and effect callbacks |
| Neighborhood rules and save invariants | `daily_life.py`, `daily_life_state.py` |
| Original local content and presentation | `content/neighborhood_life_v1.json`, `life_content.py`, `life_presentation.py` |

Daily order is: base clock/feuds/legacy investigations, legal reviews/quiet-day
cooling, career investigations with heat scrutiny,
NPC actions, economy, planning, warfare, court, navigation reset, then the optional
daily-life phase. Investigation runs once per
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

Legacy content definitions and named NPC policies remain in their original
modules. M015's two original contacts and opportunity text use a separate local
content pack; they are not added to the faction NPC policy roster. Future registries should separate stable
IDs from display names and keep character/faction, dialogue, mission/event,
asset, and progression data separate from mechanics. New systems should extend
the command/event interfaces and explicit additive save migrations, without
requiring a particular fictional property.
The [content architecture proposal](docs/GOON_CONTENT_ARCHITECTURE.md) identifies
the remaining name coupling, version/ID requirements, and the case-source adapter
needed before non-job incidents can create compatible legal cases.

## Determinism, tests, and scope

RNG remains local to seeded operations. M013 preserves legacy job outcomes and
adds no random draws. Command history, action usage, investigation markers,
committed responses, and review dates
survive saving. Reports and snapshots expose no mutable world references.
M013.1 changed only Markdown and CLI display strings. M014 adds the optional
navigation extension, local definitions, service/CLI integration and navigation
tests while preserving the 198 existing regressions. M015 preserves all 237 M014
regressions and adds neighborhood choice, ledger, housing, migration and campaign tests.
The audited M015 baseline passed **283 tests** (237 M014, 37 M015 and nine audit
regressions); see the [M015 validation report](docs/M015_VALIDATION_REPORT.md) and
[independent acceptance audit](docs/M015_INDEPENDENT_ACCEPTANCE_AUDIT.md) for evidence.
Full prologue, combat, broader career, influence and institutional
acceptance checks are future requirements, not executed feature tests.

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
undercover officers, combat, drugs, Bat-family encounters, or playable prologue are
included. The prototype remains offline-capable.
