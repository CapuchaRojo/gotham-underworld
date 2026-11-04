# Mission 016 / M017 branch — The Night Shift validation

## Baseline, authority and implementation plan

The user accepted the dependency audit and superseded the old requirement to keep
PR #15 open. `git fetch origin` confirmed remote master unchanged at
`37fc4b502e43ac3d241898b7d6a017c2906badc7`. It contains merged PRs #15 and #16;
its tree equals M016-A snapshot `e5c72c78c7cf04734a162f5ebb534e73fa3c11d8`.
There is no `main` branch. The starting worktree was clean and the requested new
name did not exist. Created `feature/m017-night-shift-event` from `origin/master`;
no stacked PR is needed, and no previous branch was moved.

Plan followed: inspect actual phase/choice/contact/law/navigation/save seams;
add an explicit optional source and pure transition reducer; append one phase
after daily life; reuse existing choice assessment, contact and cash authorities;
add the CLI and replay validation; exercise acceptance cases and long campaigns;
expand the existing proposed registry; review the diff and commit locally only.
No new global clock, Bat-Family, rogue gameplay, transportation mode, external
service, dependency, repository rename or asset was introduced.

## Implemented boundary and files

| File | Change |
| --- | --- |
| [content/night_shift_v1.json](../content/night_shift_v1.json) | Original shop incident, owner, three causes, finite work terms and four choice stages. |
| [incident_content.py](../incident_content.py) | Offline validation and canonical SHA-256 pin. |
| [world_incidents.py](../world_incidents.py) | Seeded eligibility/occurrence, pure reducer, separate recipient facts, explicit discovery, current choice assessment, independent resolution and terminal aftermath. |
| [incident_state.py](../incident_state.py) | Strict optional version, deterministic replay and exact transition identity/source/phase/effect plus command/result/payment/memory checks. |
| [incident_campaigns.py](../incident_campaigns.py) | Public-command campaign policy and actual disk resume comparison. |
| [tests/test_world_incidents.py](../tests/test_world_incidents.py) | 35 acceptance cases, with malformed-data subcases and a 120-day replay regression. |
| [career_state.py](../career_state.py) | Calls optional incident validation, preserving historical versions. |
| [daily_life.py](../daily_life.py) | Optional owner definition in the existing contact authority; unchanged legacy contact definitions. |
| [daily_life_state.py](../daily_life_state.py) | Validates the delegated owner's source-backed memories within the existing bounded standing history. |
| [game_service.py](../game_service.py) | Three named incident commands, detached report export and candidate validation for incident-adopted worlds. |
| [gameplay.py](../gameplay.py) | One post-life daily phase and thin CLI routing through the service. |
| [README.md](../README.md) | Current baseline, commands, terms, adoption and compatibility. |
| [PROJECT_STATE.md](../PROJECT_STATE.md) | Current branch, merged dependencies, runtime state and executed results. |
| [choice contract](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md) | Explains separate stages and shared authoritative effects. |
| [After Dark](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) | Section 12 records implemented behavior; remaining clock/law/Bat-Family designs remain proposed. |
| [Rogue Encounters](GOON_ROGUE_ENCOUNTERS_DESIGN.md) | Exactly 35 proposed distinct roles, explicit discovery and milestone policies, primary continuity anchors. |
| This validation report | Commands, observed outcomes, coverage, hashes and limits. |

Source/content schemas and their complete transition rules are described in the
existing After Dark document rather than a second design bible. Original atlas,
life and mobility content files/fingerprints, old tests, workflows and dependencies
are unchanged. The outer career save version remains 1; incidents use an explicit
optional version 1. Historical fixtures have no incident state added on load/day
advance. One M014 fixture was explicitly adopted and round-tripped without
rewriting historical events, jobs, factions, legal state or navigation resources.

## Acceptance coverage

| Mission gate | Executed evidence in the focused suite |
| --- | --- |
| Deterministic occurrence | Twelve seeds; all three causes observed; same-source replay and reversed world/definition dictionary order. |
| Occurrence without discovery | Unaware career reaches independent resolution, missed-unknown outcome and no penalty/reward. |
| Plausible discovery | Local shop notice; Tess at the hub only after a real M015 kept-promise reference; premature/remote/invented channels reject. |
| Hidden information | No true cause or unearned report/work options in the initial player projection or world-only incident event payloads. Partial/failed work does not reveal the cause. |
| Execution eligibility | Wrong IDs/types, stale place/window, premature evidence, custody and exhausted actions reject without world/RNG mutation. |
| Lawful participation | Complete $12 work, safety help, optional accurate disclosure and lawful withholding; no fabricated job attempt, case, heat, charge or faction effect. |
| Refusal / partial / failure / missed | Distinct refusal, $6 incomplete work, $0 failed work, failed accepted commitment, ignored-known and missed-unknown outcomes. |
| Independent resolution | Owner review/reopening and actual later delivery to incident desk, even without player participation. Legacy clock catch-up grants no retroactive work. |
| Exactly once | Duplicate work/report/follow-up rejects; daily reprocessing inert; terminal state/history stops growing; total incident wages capped at $20. |
| Save/reload | Real disk round-trip at each of 14 lifecycle/day checkpoints; historical fixtures; unsupported/bool metadata, missing content, duplicate events, altered receipts/knowledge/memories reject. |
| Read-only purity | Repeated detached reports/contact views do not adopt, discover, acknowledge, draw RNG or mutate live references. |
| Resource safety | Injected effect failure rolls back cash and memory; failed save keeps primary/world intact; no duplicate compensation, free travel or allowance refresh. |
| Recovery | Zero cash, exhausted TU, failed commitments, custody and ignored offers retain real day advance and ordinary housing/work; actual movement restores after next day. |
| Budgets/mobility | Three shared actions and 18 TU, unchanged route preview/closure behavior; active M016-A adoption/journeys coexist without incident charges touching mobility. |
| Long replay | Focused 120-day campaign plus two separate 365-day campaigns, new-process hash-seed comparison and unchanged M016-A daily-resume hashes. |

## Executed commands and actual results

| Command/check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests -p 'test_world_incidents.py' -q` | Final **35 passed**, 15.658 seconds. |
| `python -B -m unittest discover -s tests -q` | Final **371 passed**, 70.773 seconds: all 336 original cases plus 35 new cases. |
| `python -B incident_campaigns.py --days 365 --seeds 17 42 --resume-every 30` | Both completed; exact uninterrupted/resumed world equality after each daily policy; 13 real disk checkpoints per seed. |
| `python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1` | Both completed; exact prior hashes; 30 daily disk resumes per seed. |
| Actual CLI-loop smoke harness | Executed help/inspection, settle/wait/enroll, travel/notice, accept/verify/disclose, real save and reload; no runtime error and full saved world equality. |
| Registry/Markdown checks | 35 unique role names and primary IDs, Hush once; 164 local links/line references, table columns/fences, whitespace and Python AST checks passed. No third-party linter installed. |
| Git review | Expected files only; no dependency, workflow, old content or unrelated gameplay edit. No new CI run claimed: branch is local only. |

Initial new-test runs failed due to three fixture assumptions: `lay_low` on a
zero-heat career (one error in the initial 26-case suite), and a closure missing
its required cause plus forbidden same-location travel (two errors in an expanded
31-case suite). Corrected fixtures use a real lawful shift, a valid closure and
actual home/store hops. Reruns passed; final focused/full results above include
all corrections. A documentation check also caught a missing new table-column
separator and two missing explicit recruitment labels; they were corrected before final validation. No baseline test was changed
or disabled to accommodate these issues.

Final review added explicit stable transition/source IDs, before/after phases
and effect references to improve auditing without changing gameplay. Focused,
full and 365-day campaign checks were rerun against those final event records;
the final hashes below include that metadata. The original mobility hash checks
remain applicable because non-adopted worlds emit no new incident records.

## Deterministic campaign results

Pinned incident content SHA-256:
`c0b504780e5793fc1f6d7b2e05a30f45dce7daeac33b8fb4509d88bf4b78e1df`.

| Seed / run | Outcome | Final sorted-JSON world SHA-256 |
| --- | --- | --- |
| 17, 365 incident days | Complete inspection; statement review; $20 total incident compensation; cash $1640, arrears $0; 13 resumes; 56.146s. | `6bcad488e55c01db05cc5e83d6e1f370ede3bd7780bb0cdee5bb8813327566ed` |
| 42, 365 incident days | Complete inspection; statement review; $20 total incident compensation; cash $1640, arrears $0; 13 resumes; 52.758s. | `578b6ae0543e40242b088e37700dfe64be28fbebc7a5f8f043873b7dcf1fff9f` |
| 17, 30 preserved mobility days | 60 journeys, 12 boardings, $24 fares, 30 resumes; 6.392s. | `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3` |
| 42, 30 preserved mobility days | 60 journeys, 12 boardings, $24 fares, 30 resumes; 6.509s. | `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d` |

The campaign policy visits the local store, acts only on available public
information, does the incident once, then continues existing lawful roster work.
Most long-run cash comes from ordinary M015 wages, not incident generation.
The long campaigns exercise one public/disclosure branch; focused tests exercise
all other outcome classes. No 1,000-day or new GitHub CI result is claimed.

## Rogue registry preservation and expansion

Inspected the actual 27 existing rows. Added eight distinct roles: Calendar Man,
Anarky, Deacon Blackfire, Professor Milo, Great White Shark, Ratcatcher,
Electrocutioner and Maxie Zeus. **Hush was already present**, so Maxie replaces
that requested addition. No alternate alias/holder is counted as a second actor.
The existing broader minor-rogue research document remains unchanged.

The 35-role pool is: Bane; Deadshot; Poison Ivy; Killer Moth; Ra's al Ghul;
Talia al Ghul; Man-Bat; Mad Hatter; Ventriloquist/Scarface; Catwoman; Killer Croc;
Doctor Phosphorus; Hugo Strange; Joker; Penguin; Two-Face; Riddler; Scarecrow;
Mr. Freeze; Harley Quinn; Black Mask; Clayface; Firefly; Professor Pyg;
Victor Zsasz; Hush; Deathstroke; Calendar Man; Anarky; Deacon Blackfire;
Professor Milo; Great White Shark; Ratcatcher; Electrocutioner; Maxie Zeus.

Every classification/role remains proposed. The original 27 source anchors and
policies remain, with explicit proposed trust/recruitment/advancement fields
added. No continuity is selected or incompatible mantle holders instantiated.
New sources distinguish classic/seasonal Calendar Man, comics/screen Anarky,
Milo's Academy employment, Otis versus screen Ratcatcher II, Electrocutioner
holders, and Maxie's claims versus a real DC god. Great White is not King Shark.
All hooks are original proposals; source citations support only narrow anchors,
not copied scenes or guaranteed meetings/membership.

## Gameplay scenario, decisions and remaining limitations

Executed service scenario (seed 17): enroll after daily life activates; alarm
occurs day 3 elsewhere; visit the store and acknowledge its notice; day 4 accept
the work, inspect and disclose using all three actions. The inspection discovers
a faulty contact rather than inventing a burglar. It pays $12; police receive
only the actual statement. Independent review occurs day 7. Day 8's statement
review pays $8 once. Save/resume preserves the full outcome. Travel remains
separate throughout; an unaware parallel career gets independent review without
a missed-quest fine.

Other executed branches produce partial $6 work without cause knowledge; failed
$0 work and bounded damaged owner standing; unpaid safety help and a different
reopening/follow-up; lawful withholding and private reference work; refusal or
unknown expiry without debt. Choices change actual information recipients,
standing, cash, evidence quality and later opportunity type, not just flavor.

Variety is bounded: three grounded causes, evidence age, discovery channels,
commitments and disclosure. One contact and fixed evidence-age outcomes remain
mechanically shallow. There is no actual night movement, dynamic staff, dialogue
tree, rumor network, health/combat, criminal recruitment or generalized legal
source. One-shot closure prevents an inspect/collect grind; increasing frequency
without new choices would reintroduce repetition. No artificial real-time wait,
online dependency or premium currency exists.

No confirmed P0/P1 blocker remained after these checks. P2 limits: growing core
history copy/validation costs; incident replay depends on pinned rules/content;
one-shot adapter is not a general event language; existing bounded route search
and two-station depth remain. Historical compatibility is old-to-new loading;
old executables must not advance adopted incident careers because they lack its
phase. Debug snapshots/save JSON contain world truth and are not player views.
Full institutional casework still needs a reviewed non-job evidence adapter.

Recommended next slice: independently review this local commit, then authorize
one second original incident using the same source/knowledge/choice boundary with
a genuinely different consequence. Keep a global clock and licensed actors
deferred; review non-job law sources before adding player crime. No further
implementation, push, PR or merge is authorized by this report.
