# Mission 016 / M017 branch — The Night Shift validation

**Mission 017 independent acceptance audit:** the implementation evidence below
is retained as historical delivery evidence. The appended audit records current
Git reality, separately executed checks and one confirmed P2 save-context gap.
The original implementation is already on remote master; this supersedes the
earlier local-only status. No runtime repair or feature expansion was made.

**Mission 018 / M017-B update:** the appended provenance-integrity repair closes
that confirmed discovery-context gap using existing historical sources. Earlier
delivery/audit evidence is retained; current repair results and compatibility
policy appear at the end. No new incident or gameplay system was implemented.

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

## Mission 017 — independent acceptance audit

### Verified source, remote state and scope

Audited actual `43d81973e03c63d0ac8b4c759b5dd95b9e884c6d`, initially on
`feature/m017-night-shift-event`, with a clean worktree. `git show --stat` and
the complete parent diff confirm exactly the reported 17 implementation files.
No dependencies, workflow edits, new movement modes or rogue runtime were hidden
in that diff. All runtime/content changes remain exactly that implementation.

`git ls-remote --heads origin` independently returned the same commit for
`refs/heads/master`. The local feature branch tracks `origin/master`; there is
no remote M017 feature branch. Both the branch-filtered PR query and GitHub's
commit-associated pull-request query returned `[]`. Therefore the commit has
been published to the default branch, but **no M017 PR or PR-merge event was
established**. A matching tracking ref alone was not treated as merge evidence.
The original branch/commit is preserved, as are local master and older feature
branches. Created separate local `audit/m017-independent-acceptance` for this
documentation-only audit. No fetch/reset/rebase/push/PR/merge was performed by
this audit; remote state was read without changing it.

Observed existing GitHub check for the audited SHA: **test, completed, success**,
[existing CI job](https://github.com/CapuchaRojo/gotham-underworld/actions/runs/41914104555/job/126869080928).
This is the already published implementation's check, not CI for this unpushed
audit document. Queries used `gh pr list --state all --head
feature/m017-night-shift-event`, `gh api repos/CapuchaRojo/gotham-underworld/commits/43d81973e03c63d0ac8b4c759b5dd95b9e884c6d/pulls`
and the matching `check-runs` endpoint; all were read-only.

### Lifecycle and authoritative effects traced

| Boundary | Actual implementation / independent finding |
| --- | --- |
| Eligibility and source | [initial](../world_incidents.py#L19) pins one definition and enrollment source, selects cause/date using SHA-256, sorts cause/stage keys and starts with no recipient facts. Explicit adoption follows active M015 life; load does not subscribe a career. |
| Independent progression | [daily pipeline](../gameplay.py#L77) retains the previous legal/NPC/economy/warfare/court/navigation/life ordering, then calls [incident day](../world_incidents.py#L237). [Reducer](../world_incidents.py#L74) advances eligibility, occurrence, information and resolution without any discovery prerequisite. |
| Evidence and knowledge | Owner observation precedes verified owner findings. The desk receives an alarm report, later actual player observations if submitted, and an independent owner review at resolution. The player initially learns only an alarm report and only learns the cause through complete inspection. No new job-source evidence or player case is fabricated. |
| Discovery | Local notice or Tess's real kept-promise reference at the hub are checked on the service path. No delivery from simply viewing a remote report. The saved-context validation caveat below is a separate P2 issue. |
| Participation | [Assessment](../world_incidents.py#L54), shared choice assessment and [choice cost](../world_incidents.py#L250) recheck current knowledge, stage, day window, location/access, custody and remaining actions. Expiration and duplicate selections reject. |
| Outcomes | Complete/partial/failed work, unfinished commitments, safety help, refusal, withholding/disclosure, ignored known offers and missed unknown incidents have different recorded outcomes. External assertions verified the actual compensation table, not merely replay against the same reducer. |
| Resolution and aftermath | Owner reopening/review happens without player involvement. Help changes shop status; actual work/disclosure selects a later private-record, safety or statement-review opportunity. No unknown/refused offer creates a promise, debt, global hostility or career lock. Terminal incident history stops growing. |
| World publication | [execute_command](../game_service.py#L79) owns candidate creation and final root-world publication; [publisher](../world_incidents.py#L212) and all effect adapters run on that candidate. A handler exception/interruption discards its cash, memories, stage changes and events. Low-level reducers remain simulation APIs, not alternative player boundaries. |
| Cash | `_publish` credits the single `player.cash` field from one receipt. [Existing balance observer](../daily_life.py#L53) records the command's actual net change. [Incident validation](../incident_state.py#L223) ties each nonzero payout to one ledger receipt; the incident receipt is not a second account. |
| Relationships / references | [Existing contact memory reducer](../daily_life.py#L70) owns Ada's bounded standing/history; [life validation](../daily_life_state.py#L7) checks delegated sources and deltas. Reference/follow-up facts belong to the incident, not a new numeric reputation authority. |
| Persistence / inspection | [Atomic writer](../career_persistence.py#L64) validates before staging and preserves the primary on failure. [Player report](../world_incidents.py#L263) returns detached known information; save/debug state deliberately includes world truth and is not a player projection. |

This is **more than a daily-life job/menu**: an undiscovered source occurs,
changes recipient facts, resolves and leaves independent aftermath. It does not
reuse a life roster slot or require the player to activate its occurrence by
opening a choice. The payable participation/follow-up components are deliberately
job-like, but do not control the world's lifecycle.

It is also **not yet a general multi-incident engine**. There is one state object,
one content loader and one enrollment; content validation fixes four stage
bindings and three causes, while the reducer contains Night Shift-specific
quality/follow-up logic. Tess and the owner are bound explicitly in the adapter.
A second genuinely different incident is not a data-file-only addition. It can
reuse service transactions, seed identities, choice assessment, contact/cash
owners, projections and receipts **without copying the whole implementation**,
but requires a separately reviewed definition/instance dispatch and small effect
adapter boundary. No such refactor was made in this audit.

### Independent commands and executed results

| Executed command / harness | Actual result |
| --- | --- |
| `python -B -m unittest discover -s tests -p 'test_world_incidents.py' -q` | **35 passed**, 13.562s. |
| `python -B -m unittest discover -s tests -q` | **371 passed**, 68.416s; unchanged tests, none disabled. |
| `python -B incident_campaigns.py --days 365 --seeds 73 191 --resume-every 1` | Both passed, **365 actual daily disk checkpoints each**, full resumed/uninterrupted equality after each daily policy. |
| `python -B "$env:TEMP\goon_m017_independent_audit.py"` | **228 independent assertions passed**, ten outcome paths, repeated previews, duplicate/retry attempts, actual stage saves, interruptions, all historical fixtures and six real CLI processes. The contradictory-context acceptance described below was deliberately reproduced and classified, not silently counted as rejection. |
| Separate seed 0–11 cause-projection probe | All 12 passed: initial finding hidden, complete inspection reveals exactly the corresponding definition. Break-in seeds 1/3/4/5/6/11; delivery-error 2/7/8/10; faulty alarm 0/9. |
| Registry comparison with `git show e5c72c7:docs/GOON_ROGUE_ENCOUNTERS_DESIGN.md` | Exactly 35 unique primary IDs/names; original 27 retained; eight additions and Hush substitution confirmed. |

The temporary harness is an audit probe, **not 228 additional unittest cases** or
a permanent regression file. Its source remains at
`C:\Users\mich3\AppData\Local\Temp\goon_m017_independent_audit.py`, SHA-256
`36376a0745c2fa94fb69ff033d332ea0c42f74a9f1f920667e06fa7153cf74ce`.
It uses the public service and real temporary careers, plus explicit fault/JSON
mutations for the interruption and save-validation probes. No historical fixture
was overwritten. No new gameplay code or automated regression test was necessary
because no P0/P1 repair was identified.

| Independent campaign | Observed result | Sorted-JSON world SHA-256 |
| --- | --- | --- |
| Seed 73, 365 days | 365 resumes, 121.050s; resolved; complete work + statement review; $20 incident wages; cash $1640, arrears $0. | `bfc4337ac880037196c0b6acf718580b30ac2143c9725be67583512c5954b2e6` |
| Seed 191, 365 days | 365 resumes, 118.001s; resolved; complete work + statement review; $20 incident wages; cash $1640, arrears $0. | `63fbec1d718b1d348cb890291ebbe29c3c981ae4cba2ebc2a3d69123f5b1db3d` |

Both happened to select `delivery_error`; no seed reroll or forced balancing was
used. The separate 12-seed projection checks exercise all three grounded causes.
The daily long-run policy still exercises one successful branch; the independent
matrix below exercises non-success paths. No 1,000-day claim is made.

### Exploit, interruption and CLI evidence

| Independent path | Actual total incident compensation | Persistent result |
| --- | --- | --- |
| Complete / disclose | $20 | Complete work, actual scoped desk statement and statement-review follow-up. |
| Complete / withhold | $20 | Complete work, no player statement, private-record follow-up. |
| Partial / disclose | $14 | Limited findings, no cause knowledge, honest partial statement and review. |
| Partial / withhold | $6 | Limited findings only; no earned follow-up. |
| Failed inspection | $0 | Failed work and bounded owner reaction. |
| Accepted but unfinished | $0 | Failed commitment, distinct from ignored/unknown work. |
| Safety help | $8 | Safety reopening and different one-shot follow-up. |
| Refusal | $0 | No promise/debt/standing penalty; world proceeds. |
| Ignored known | $0 | Known offer lapses without a fabricated commitment. |
| Never discovered | $0 | Missed-unknown outcome; owner and desk progress independently. |

After stage payments/decisions, the harness wrote/reloaded the actual career
and attempted the same command again: duplicate $12, $6 and $8 payment paths,
reference effects and contradictory repeated choices were rejected with complete
world/RNG equality. It also rejected expired involvement, repeated daily
processing and remote public-notice discovery. Known/unknown previews and
returned contact data were modified externally without affecting the world.
The desk acquired only supplied player statements plus the separate autonomous
owner reports; no cases, job attempts or heat were created. Every branch retained
access to an actual M015 lawful shift after refusal/failure/expiry.

An injected `KeyboardInterrupt` during the contact effect left the authoritative
world and RNG unchanged; retry succeeded once. A second interruption at primary
save publication preserved the previous primary and loadable state despite
successful backup preparation; retry saved the new state exactly. This checks
actual interruption/retry, in addition to the existing OSError/ValueError tests.

CLI checks launched **six actual subprocesses**, using `python -B gameplay.py
--seed <seed> --save <temporary-career>` and later `--load --save <same-career>`.
Input was piped to the real CLI, not a mocked `input` function. Each initial
process explicitly saved, then ended through EOF; each resume finished through
`quit`. All six exit codes were 0 with no unexpected `Cannot complete command`.

| CLI playthrough | Executed behavior / inspected saved result |
| --- | --- |
| Success, seed 73 | Settle, wait, enroll, travel, discover notice, accept/verify/disclose, inspect and save; EOF/resume; advance to earned follow-up, work and quit. Complete outcome, $20 total, resolved world. |
| Refusal, seed 191 | Same actual notice path, explicitly refuse, save/EOF/resume, advance and quit. Refuse outcome, $0, resolved world. |
| Missed, seed 907 | Ordinary home day, enroll, never visit/discover incident, save/EOF/resume, advance and quit. Still undiscovered, missed-unknown outcome, $0, resolved world. |

All **15 historical career fixtures** were independently loaded, compared against
their original event arrays, advanced three real days without incident adoption,
and disk round-tripped. Existing explicit historical-adoption tests also passed
in the focused suite. This verifies old-to-new compatibility; it does not promise
that older executables can advance a new incident-adopted career.

### Confirmed findings and disposition

**P0/P1: none confirmed by the executed checks. No gameplay repair applied.**
No normal-service duplicate reward, premature cause disclosure, automatic police
guilt, rejected-command mutation, repeated resolution or ordinary-career lock
was reproduced. This is scoped acceptance evidence, not proof against every
possible state edit or future incident.

**P2 — cross-domain save context is trusted, not independently reconstructed.**
[Replay](../incident_state.py#L137), as audited before M017-B, checked recorded location/reference flags for
shape and runs eligibility against that snapshot, but does not derive them from
the historical travel/contact events. Reproducer used a valid public-notice
discovery with no Tess reference, then edited its transition's channel to
`contact`, context location to n13 and `tess_reference` to true; changed the
matching command argument and saved discovery channel accordingly. No actual
Tess memory or hub visit was added. The contradictory JSON still loaded while
the real navigation history placed the player at p032 and Tess had no kept
promise. Legitimate `discover_incident` commands do not grant this route.

This is a **confirmed malformed-save integrity limitation**, not a reproduced
normal-play money/knowledge exploit. It is deferred under the mission's P2
rule: a complete cross-domain historical proof contract needs explicit source/
ordering rules; this audit does not silently introduce a partial provenance
framework or change valid existing histories. Before multi-source incidents,
specify and test source-backed context validation. Replay consistency alone must
not be described as independent proof of every historical context predicate.

Other P2 limitations remain: the singleton/one-definition adapter; fixed authored
inspection-age outcomes and one contact; whole-career copy/validation growth;
debug snapshots exposing world truth by design; existing bounded route search.
Independent incident history itself was bounded and terminal, not unbounded.
No new dependency or broad NPC/law/clock implementation is justified by these
findings. Inactive eligible options are omitted from the current thin CLI, so
the documentation/journal remains important for understanding location/windows.

### Registry, readiness and next incident recommendation

The actual proposed registry has exactly **35 distinct names/primary IDs**.
Compared to the real 27-row snapshot, additions are Calendar Man, Anarky,
Deacon Blackfire, Professor Milo, Great White Shark, Ratcatcher, Electrocutioner
and Maxie Zeus. Hush occurs once in both snapshots; Maxie replaces the requested
Hush addition. Original rows were retained; no aliases were counted twice.
Ventriloquist/Scarface is explicitly one actor/persona entry, and mantle rows
require a selected holder/era before instantiation.

All 35 rows have publisher-source anchors and separate proposed presence,
discovery, participation, recruitment and advancement policies. Continuity
cautions distinguish versions rather than instantiate them together; joinable,
conditional contracts and N/A/nonjoinable roles remain different. This audit
confirms those documentation boundaries, not a finalized continuity or exhaustive
verification of every published biography. No registry or rogue runtime changed.

**Readiness:** the bounded M017 implementation passes acceptance and is ready
for human technical review with these nonblocking P2 findings. It is already on
remote master, so there is no outstanding unmerged M017 PR to approve; do not
create or infer one from this audit. The new local audit commit changes only
this report. Acceptance does not authorize another event or certify a generic
multi-incident content pipeline.

Recommended second incident for a separate contract: **The Wrong Notice**.
An outdated public delivery-date notice conflicts with a later authenticated
correction. Two original contacts hold different, sourced versions. The player
may publish a verified correction, warn only one consenting contact, refuse,
repeat an unverified claim or miss the issue. A scheduled independent correction
eventually resolves the public error. Consequences concern who received which
claim, corrected credibility and later access, rather than another paid forensic
inspection. Dates use logical days, not a new clock; no inventory, crime, combat
or licensed actor is required. Review the P2 provenance rules and minimal adapter
boundary before authorizing it; do not copy the entire Night Shift reducer.
This is a recommendation only. No M018 implementation was begun.

## Mission 018 — M017-B provenance integrity repair

### Starting state and contract recorded before code

Started on clean `audit/m017-independent-acceptance` at known audit commit
`aaacba012dee705eac39f56009f3252d496c3f16`. Remote master was verified at
`43d81973e03c63d0ac8b4c759b5dd95b9e884c6d`; no M017 feature PR was found.
The audit branch now has its own remote tracking ref, an external publication
after the prior mission; this mission did not push it. Created separate local
`feature/m017b-provenance-integrity` from the audit commit, preserving every
existing branch and commit. No merge, rebase, reset, push or PR is authorized.

Read actual incident replay, context production, life choices/promises/memories,
navigation schemas 1/2 and activation records, and the career validator's order.
The exact original forged-context edit was reproduced against unchanged source
before repair. Actual valid public-notice and Tess-contact saves were preserved
before any validator change. Then the
[canonical provenance contract](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md)
was written **before implementation**, specifying authority, event/command
ordering and the missing-history policy. Regression tests were run red first.

### Focused repair and authority

Only [incident_state.py](../incident_state.py#L15) changes runtime validation.
It derives discovery proof from existing records and compares the context claim:

- Location comes from the last completed historical travel arrival, including
  schema-1 legacy travel and schema-2 journeys. Uses actual `arrived`, never the
  requested destination, current saved position or a later journey. When needed,
  a uniquely supported public navigation activation/adoption establishes an anchor.
- Tess knowledge follows the original accepted promise choice and receipt, kept
  promise, resolving choice/effect and receipt, and matching actual Tess memory/
  event. It does not derive a reference from current standing or a boolean.
- Source records must lie within their own completed command frames and precede
  discovery by event order, command ID and day. The discovery itself precedes
  its receipt. Same-day future references are deliberately not backfilled.
- The pinned occurrence must actually have been replayed before discovery;
  its earlier ticks follow real same-day life processing after enrollment.
  Existing low-level daily pipelines without a `wait` receipt remain supported.
- Existing life/navigation validators retain ownership of option meanings,
  promise dates, memory deltas, route paths, costs and duplicate settlements.
  New proof checks do not recursively call those validators or write a parallel
  history. Replay now uses enumerated event offsets rather than equality-based
  `list.index` lookups for source ordering.

This is strictly read-only. No context/event field, pin, save version, content
definition, command, action/TU limit, cost, reward, NPC or incident was added.
There is no global NPC/knowledge/legal/time reconstruction. The Wrong Notice
remains a proposal and was not implemented.

**Compatibility policy:** non-adopted/non-discovered careers need no new trace.
Valid published M017 discovery histories already carry the required sources and
load unchanged. A later real reference, later travel or changed custody does
not invalidate an earlier source-backed discovery. Contradictory or insufficient
adopted discovery history fails clearly under `incidents.discovery.provenance`;
do not fabricate source events, infer an old location from the current one, erase
an encounter or grant missing knowledge. This rejects unverifiable edited saves,
not an actual supported historical schema. Old-to-new compatibility remains;
forward play in older executables is not promised.

### Red/green regression evidence

New [test_incident_provenance.py](../tests/test_incident_provenance.py) contains
18 methods with adversarial subcases. The first 15 methods were executed before
repair: **12 reported failures**, including subtest failures, because edited
histories were wrongly accepted. All now pass. Missing/duplicate domain-source
tests also retain previously working rejections rather than weakening them.

Coverage includes valid public/contact/rescheduled-reference histories; the exact
forged Tess case and an isolated forged reference with a genuine hub arrival;
coherent forged channel/location edits; future legacy/modern
arrival substitution; source-memory, choice, original-invitation and receipt
reordering; discovery after its receipt; missing/duplicate memory/promise/choice/
travel sources; absent location trace; later same-day reference knowledge; read-only
validation; historical M011 navigation adoption and contact discovery; low-level
daily advancement; normal round-trip parity; and rejected-command world/RNG
preservation. Existing M017 cases continue covering costs, deadlines, custody,
independent occurrence, settlement, failure, ordinary recovery and information
visibility. No existing test was edited or disabled.

Final compatibility review added an unrelated annotation to a valid reference
memory. The first proof implementation rejected it (one targeted method, two
subcase errors). The equality check was narrowed to canonical memory fields,
preserving optional metadata rather than demanding it be copied into an event.
Both regular/rescheduled annotated references now pass. An isolated probe also
confirmed that every other domain accepts the genuine-hub forgery and the new
proof rejects it specifically for missing Tess source-backed knowledge. Final
focused/full/campaign checks below were rerun after this correction.

| Executed command / check | Actual final result |
| --- | --- |
| `python -B -m unittest discover -s tests -p 'test_*incident*.py' -q` | **53 passed**, 17.549s: original 35 Night Shift + 18 provenance methods. |
| `python -B -m unittest discover -s tests -q` | **389 passed**, 73.025s: all original 371 cases preserved. |
| `python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1` | Both exact original hashes; 30 real daily save/reloads per seed; 6.847s / 6.594s. |
| `python -B incident_campaigns.py --days 365 --seeds 17 42 --resume-every 30` | Both exact original hashes and resumed/uninterrupted equality; 13 real disk checkpoints per seed; 59.724s / 53.812s. |
| Actual pre-repair M017 files | Valid public/contact careers load and save **byte-for-byte identically**; exact original forged file now rejects. |
| Compatibility / history | Existing 15 historical fixture cases pass without automatic incident adoption; new M011 explicit adoption and preserved M017 saves pass. |

All four replay hashes match the pre-repair values recorded earlier in this file:

| Campaign | Unchanged sorted-JSON world SHA-256 |
| --- | --- |
| Mobility 17 / 30 days | `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3` |
| Mobility 42 / 30 days | `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d` |
| Night Shift 17 / 365 days | `6bcad488e55c01db05cc5e83d6e1f370ede3bd7780bb0cdee5bb8813327566ed` |
| Night Shift 42 / 365 days | `578b6ae0543e40242b088e37700dfe64be28fbebc7a5f8f043873b7dcf1fff9f` |

Pre-repair evidence remains in the temporary directory
`C:\Users\mich3\AppData\Local\Temp\goon-m017b-before-89d0c8d3165545f58061e3ceb9775eaf`.
Original file SHA-256 values, verified again after repair:

- `public.json`: `c10c4bf18e4c6e41fd97150de6661c336333842d9e5197d3d2544444e249f3ef`.
- `contact.json`: `a5aead0e3e5fc9de5f3185f8e263dbc5a614561d6542d0cef5accff489e6bb36`.
- `forged.json`: `88b485e5c5a1ed30e26e95fb4a33b85958772e79a86799429c38cc49c7ea0549`.

The first two were round-tripped to different temporary output files and matched
their original bytes, not merely selected fields. The third's rejection was
executed against the exact unchanged file captured before the repair. No new
GitHub CI result is claimed for the local repair.

### Changed files and remaining limits

Exactly four focused files: `incident_state.py`,
`tests/test_incident_provenance.py`, this validation report, and the canonical
After Dark provenance contract. No gameplay producer, history fixture, registry,
asset, dependency, workflow, movement rule or persistence writer changed.

The confirmed discovery location/reference gap is closed. No P0/P1 regression
was observed. Remaining P2 limits are explicit: this proves consistency with
independent domain records, not authenticity against coordinated rewriting of
all histories; it does not independently rebuild every past legal/access/action
predicate or all non-discovery contexts. Scanning/copying large histories still
grows with career length. The single-incident adapter and broader event design
limits remain. None warrants adding another history authority or implementing
The Wrong Notice in this repair. Stop after local validation and commit.

## M018 compatibility cross-reference — Mission 019

The later authorized [Wrong Notice implementation/validation](M018_WRONG_NOTICE_VALIDATION.md)
adds explicit two-adapter dispatch while retaining the Night Shift slot, IDs,
content and event shapes above. The preserved public/contact saves were again
round-tripped byte-for-byte, the original forgery still rejects, and all four
recorded mobility/Night Shift hashes remain unchanged. This does not rewrite the
historical M017/M017-B results or imply they were merged into master: PR #17
merged to the audit branch, and M018 starts from its actual merge commit.
The canonical [After Dark](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) section 13
describes the now-implemented second incident; earlier proposed/repair-only
scope statements are historical. No rogue or Bat-Family gameplay was added.
