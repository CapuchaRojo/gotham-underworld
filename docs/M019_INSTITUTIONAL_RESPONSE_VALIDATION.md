# M019 — Institutional Knowledge & Response: executed validation

Mission 023 implementation and Mission 024 independent acceptance. Local only;
no push, PR or merge is authorized.
The canonical design lives in [Institutions and Recovery](GOON_INSTITUTIONS_AND_RECOVERY.md),
with [architecture](GOON_CONTENT_ARCHITECTURE.md) and
[incident integration](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md).
This report records actual execution, not proposed future acceptance claims.

## Verified baseline and history correction

Fetched `origin/master` at `d0723b1551fc4e1aedf2d0fa4a5b5e3758902f49`; local
master matched and the worktree was clean. Baseline command:

```text
python -B -m unittest discover -s tests -q
```

**426 tests passed, 104.539s**, before edits. Created
`feature/m019-institutional-response` from that verified master. Existing branches
and commits were preserved. README/project/roadmap now reflect actual history:
PR #17 first merged to the audit branch; PR #18 brought provenance into master
at `8bc9700`; PR #19 merged M018 at `d0723b1`. M018 is no longer unpublished
or missing its dependency. M019 itself remains local and unpublished.

## Implemented slice and authority

The civilian desk at public n13 and intake at the existing p044 public counter
have separate mandates, source transmissions, received reports, processing
queues, beliefs, contradictions, local administrative credibility and player
response snapshots. Ruth Bell and Niko Shah are original staff definitions.
The GCPD display name is content data; engine rules use stable IDs/types.

The optional `institution_version: 1` / `institutions` extension requires active
daily life and explicit `enable_institutions`. It preserves the outer save version,
historical careers, three actions/day and eighteen travel TU/day. It creates no
money, legal case, offender identity, warrant, arrest, heat or faction resource.

The source adapter replays actual incident events into ephemeral source records.
It uses public board/handbill records, received owner reports/reviews, the issued
notice circular and observations actually acquired by player commands. A source
has an identity, observer, origin event/day, credibility and limitation. An
institution learns only through an explicit receipt with recipient, route,
received day and due day. World truth alone is never a received report.

NPC transmission starts only for source events after adoption. Historical player
observations remain eligible for explicit submission. Civilian rounds collect
local public/resident claims; intake receives a next-day forwarded copy of the
old desk's owner alarm report and review. This does not rename the old desk or
share all its information. Neither reads private player choices or the other
institution's records. Live synchronization follows old incident processing;
service commands synchronize on their private candidate before commit.

Civil processing takes one day, intake two. Contradictory unchecked sources
request clarification; an unanswered record closes after three clarification
days. Extra unchecked submissions do not refresh that deadline. Documented
evidence can resolve/reopen the record without erasing earlier claims. A
documented cause remains a local observation, not legal guilt. Idle closed
queues produce no daily notification/history spam.

## Meaningful player choices and persistent consequences

| Decision | Cost / consequence |
| --- | --- |
| Submit an acquired notice or observation | One action at the appropriate counter. It can be false/incomplete despite being a real source. Acknowledgment is not endorsement; no wage. |
| Submit documentary evidence | One action. Establishes supported beliefs and local documented reporting access after processing; other audiences remain unchanged. |
| Correct a known unsupported original claim | One action with a documented, conflicting source for the same incident/topic/recipient. Queued originals can be corrected. Another sender's report needs actual local follow-up first. Correction chains and repeat corrections reject. |
| Follow up | One action for an unread version at the counter. Receives the actual queued, clarification, insufficient or documented response. Remote views retain receipt-time information. |
| Receive a dated correction copy | One civilian assistance receipt per matter. No money or inventory system. This actual response supplies one explicit documentary source for later record repair, including after old incident windows expire. Replay reconstructs its basis before allowing reuse; a saved flag cannot prove itself. |
| Withhold involvement | Zero actions, once per known matter. Private journal intent; no institutional receipt, promise, debt, legal punishment or lost ordinary career. NPC reporting continues independently. |

An uncorrected player claim later contradicted by received documentary evidence
puts only that desk's unchecked submission route under `needs_documentation`.
Documented submissions remain available. A processed correction restores the
record; it does not improve every NPC/faction relationship. Credibility is an
institution-owned access policy, not a stacking reward meter. Primary incident
evidence and expired work are never backfilled by a desk reply.

Variety comes from timing, contradictory channels, two mandates/delays, unknown
versus documented sources, private withholding, and repair versus leaving a bad
record. There is no reporting income loop or real-time waiting. The slice is
still shallow: authored local claims, three abstract matters and no broader
institutional career. Existing weekly wage work can remain repetitive; M019 does
not require repeated commuting or reporting to survive.

## Automated results

All existing tests are unchanged. `tests/test_institutions.py` adds **42 methods**.

| Exact executed command | Actual result |
| --- | --- |
| `python -B -m unittest discover -s tests -q` | **468 passed**, 162.280s, after the timestamp repair: all 426 baseline plus 42 M019 regressions. |
| `python -B -m unittest discover -s tests -p 'test_institutions.py' -q` | **42 passed**, 51.898s, final standalone run. |
| `python -B -m unittest discover -s tests -p 'test_*incident*.py' -q` | **53 passed**, 16.222s, after initial hooks; also covered by final full suite. |

Coverage includes explicit/late/idle adoption; unsupported and wrong-recipient
reports; duplicates; queued and late corrections; documentary-before-unchecked
ordering; contradictory witnesses; real Tess provenance; delayed processing;
missing participation; clarification closure; scoped credibility/recovery;
one-shot assistance across versions; recovery after old scene expiry;
forged/unreceived copies; forged contexts/records; missing/reordered/duplicate
sources; read-only/detached reports; rejected-command world/RNG purity;
failure rollback; failed disk replacement; zero-cash ordinary survival;
insertion order, fresh-process hash seeds, historical saves and save/resume.

The long regression inside the focused/full suite runs **60 days for each of
211/documented and 509/unchecked, with 60 real daily save/reloads per seed**.
Whole worlds are compared every day. Additional executed service probe: active
M016-A adoption, schema-2 journeys to p032/n13, public discovery, institutional
submission and disk resume passed, with two actions remaining and two TU used.

## Final-code campaigns and replay hashes

Each campaign runs an uninterrupted world beside a disk-resumed world through
public reports and service commands, comparing complete worlds after every day.
Ordinary available lawful work continues. Policies stop institutional commutes
once their finite work is done and do not use hidden truth to select evidence.

| Exact command | Actual result |
| --- | --- |
| `python -B institution_campaigns.py --days 365 --seed 211 --mode documented --resume-every 30` | 13 checkpoints; both desks documented; eight reports, two responses, one correction copy; cash $1,632, arrears $0, heat 0, not arrested; 122.714s, after timestamp repair. |
| `python -B institution_campaigns.py --days 365 --seed 509 --mode unchecked --resume-every 30` | 13 checkpoints; civilian needs documentation, intake documented; eight reports, two responses, one copy; cash $1,632, arrears $0, heat 0, not arrested; 121.769s, after timestamp repair. |

Those balances include existing wages, room charges and the old Night Shift
inspection payment, never institutional compensation. The civilian alarm record
closes insufficient while the delivery record and intake observations are
documented: the same city does not give every desk identical information.

Institution content fingerprint:
`76791f5121a5c76020385d617a56e9bb9443b53a6956725b6ce69774a630be03`.

| Campaign | Full sorted-JSON world SHA-256 |
| --- | --- |
| M019 211/documented/365 | `84a9a72d457ec226c5938536aa4e6807c9a2011dae3910f8b0cf5e96d0255cd6` |
| M019 509/unchecked/365 | `926c4eed5c5c79536d233742a3c7b65791fec4fbaf84883be2126db57daf77f4` |

Historical commands were also executed without M019 adoption:

```text
python -B incident_campaigns.py --days 365 --seeds 17 42 --resume-every 30
python -B notice_campaigns.py --days 365 --seed 73 --mode help --resume-every 30
python -B notice_campaigns.py --days 365 --seed 191 --mode unchecked --resume-every 30
python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1
```

All six recorded fingerprints match exactly:

| Historical campaign | Unchanged SHA-256 |
| --- | --- |
| Night Shift 17 | `6bcad488e55c01db05cc5e83d6e1f370ede3bd7780bb0cdee5bb8813327566ed` |
| Night Shift 42 | `578b6ae0543e40242b088e37700dfe64be28fbebc7a5f8f043873b7dcf1fff9f` |
| Wrong Notice 73/help | `593386231e6df47bac4d9c279a10bd011b67d0f6a08e63d6f56ab3c68245bc09` |
| Wrong Notice 191/unchecked | `ca5996dd6800bdd349f082b02ee67ff85d418673311d613ed9a2e51e806bbcae` |
| Mobility 17 | `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3` |
| Mobility 42 | `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d` |

Night Shift final times: 73.555s / 64.620s; Wrong Notice: 86.395s / 74.877s;
mobility: 6.676s / 6.891s. Night/notice runs resumed 13 times per seed;
mobility resumed daily 30 times per seed. Original incident reducers, pins and
IDs were not edited.

## Historical saves and interruption evidence

All 15 existing historical fixture files load/advance without institutional
adoption. A genuine pre-M019 M018 save was generated in an isolated `git archive`
of `d0723b1`, not by the new executable. The [fixture provenance](../tests/institution_fixtures/README.md)
records its exact recipe and SHA-256
`befd147e7e1ea1b83ac8db0803c006461afd3b3bab67f0401cdc18b89e1bb246`.
It round-trips **byte-for-byte**, then explicitly adopts and submits its existing
ledger observation successfully. Local attributes preserve its LF JSON bytes
across checkouts without changing existing fixture conventions.

The actual preserved pre-M017-B public/contact files also round-trip byte-for-byte:
`c10c4bf18e4c6e41fd97150de6661c336333842d9e5197d3d2544444e249f3ef`
and `a5aead0e3e5fc9de5f3185f8e263dbc5a614561d6542d0cef5accff489e6bb36`.
The exact original forged file still rejects under discovery provenance.
No originals were overwritten. Compatibility is old-to-new, not forward play
of an adopted M019 career in an older executable.

Beyond mocked replacement failure, an actual writer subprocess was terminated
immediately before primary replacement while saving a valid M019 career with a
received copy. The old primary and `.bak` retained identical valid bytes; both
loaded as the old career. Restart/save/load of the new career succeeded. A
duplicate follow-up then rejected without changing world or RNG. Forced process
termination left one staged temporary file; no primary/backup corruption occurred.
All evidence used disposable temporary folders, cleaned after the probe.

**Windows concern:** no `WinError 32` occurred in the executed M019 baseline,
focused/full tests, campaigns, CLI or crash probes. The prior intermittent sharing
violation remains an unresolved platform concern; no root-cause fix is claimed.

## Actual CLI scenarios

Real subprocesses ran `python -B gameplay.py --seed <seed> --save <temp-path>`,
then separate `--load --save <same-path>` invocations. No mocked CLI input.

Both seeds: settle in on day 0, activate on day 1, explicitly enable both incidents
and institutions, advance to day 4, visit p032, discover both public notices,
refuse the old alarm offer, then visit n13. Stable instance IDs are
`goon.incident.night_shift.v1.enrollment.1.alarm` and
`goon.incident.wrong_notice.v1.enrollment.1.notice`.

- **211/documented:** verify the notice ledger, submit its `.claim.ledger` at
  civilian, travel to p044 and submit the actually heard alarm report
  (`.source.alarm_reported`) at intake. This uses three actions. Save, EOF,
  resume/retry and save; the rejected retry preserves the checkpoint world.
- **509/unchecked:** submit `.claim.poster` at civilian and privately withhold
  the alarm statement at intake. Save, EOF, then resume and repeat submission;
  duplicate rejection preserves the checkpoint exactly.
- Advance to day 13 in another process; follow up at each actual counter. Both
  runs exit successfully, have $10 after the old room charge, zero heat/cases,
  and intake classification `observations_logged`. Civilian credibility differs:
  `documented` versus `needs_documentation`. Each receives exactly one copy.
  Three processes per scenario exited 0; final stdout counts were 317 / 315 lines.
- **Late recovery continuation:** resume seed 509, travel to civilian and provide
  the actually received `.copy.delivery_day` source as an explicit correction of
  the original report. Wait, then follow up: day 14 credibility is `documented`,
  with no second copy. Cash is $0 and arrears $20 due to the pre-existing day-14
  room review, not an institutional fee. Basic home access and work remain viable.

The first development harness included redundant travel to the current location;
the CLI correctly rejected it. The corrected final scripts above passed without
unexpected command errors. The only intentional failures were the retry checks.

## Findings, limitations and exact inventory

Before delivery, review closed correction-of-correction history growth and loss
of a documentary repair route after old incident windows expired. A final
adversarial probe also **confirmed a receipt-time provenance defect**: a coherent
edit backdated a day-4 submission/receipt to day 3 despite its source being
observed on day 4. One new regression was executed before repair and failed
because validation wrongly accepted it; the same regression passed after repair.
The validator now checks prior domain-event day, completed arrival/source days
and receipt ordering without adding a clock or changing valid outcomes. Final
focused/full/yearly checks were rerun. No existing test was relaxed.
No P0 or unresolved P1 finding remains in the exercised scope; the receipt-time
validation defect was confirmed and repaired before local delivery.

P2 limits: full-history copying/replay cost; authored source/mandate adapters;
no generic rumor network or individual staff schedules; separate player journals
without automatic primary-evidence backfill; no broader housing/employment/legal
effects from assistance. Debug snapshots intentionally expose audit world truth.
Validation checks historical source/command/movement consistency, not authenticity
against coordinated rewriting of every domain, nor every past legal/access/action
predicate. Old custody/legal restrictions are checked live on the service candidate.
The existing Windows sharing concern and orphan cleanup after forced termination
remain documented. No M020, combat, care/prison episode or new rogue gameplay.

Exactly **21 files**:

| Files | Purpose |
| --- | --- |
| `content/institutions_v1.json`, `institution_content.py` | New pinned mandates, original staff, places, delays and loader. |
| `institution_sources.py` | New ephemeral incident/received-copy source adapters. |
| `institutional_response.py` | New bounded queue/reducer, records, local access, commands and read views. |
| `institution_state.py` | New deterministic source-backed replay validation. |
| `career_state.py`, `game_service.py`, `gameplay.py`, `incident_dispatch.py` | Validation/service/day/CLI hooks and private automatic-event filtering. |
| `institution_campaigns.py`, `tests/test_institutions.py` | New public-command replay runner and 42 focused tests. |
| `tests/institution_fixtures/m018_notice.json`, `tests/institution_fixtures/README.md`, `tests/institution_fixtures/.gitattributes` | Genuine compatibility fixture, provenance and byte preservation. |
| `README.md`, `PROJECT_STATE.md` | Current architecture, commands, capabilities and corrected Git history. |
| `docs/GOON_CONTENT_ARCHITECTURE.md`, `docs/GOON_INSTITUTIONS_AND_RECOVERY.md`, `docs/GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md`, `docs/GOON_MILESTONE_ROADMAP.md` | Canonical extension and scope/history integration. |
| This report | Executed validation and limitations. |

Existing tests/fixtures, incident reducers/state validator/content, daily-life
contacts, persistence writer, navigation/mobility, economy/legal systems, rogue
registry, workflows and dependencies are unchanged. No new GitHub CI is claimed
for unpublished local work. Validated local implementation commit:
`fe4a7667230ab0fd3e69a9ee5a8f95fd95668499`, parent
`d0723b1551fc4e1aedf2d0fa4a5b5e3758902f49`. The subsequent documentation-only
commit records this identity; runtime and tests are unchanged after validation.
Changed Python/JSON parse successfully, Markdown fences balance and all **175
relative file links in eight changed Markdown documents** resolve. The fixture
SHA and its LF attributes were checked; `git diff --check` passed. No external
Markdown linter or other dependency was installed.

## Mission 024 — independent hardening and acceptance audit

This section records a separate execution against the completed implementation;
the Mission 023 results above are retained as historical evidence, not counted as
new independent runs. No additional gameplay or M020 work was undertaken.

### Starting Git state and inventory reconciliation

Verified repository `C:\Users\mich3\Projects\gotham_underworld_m001`, clean worktree,
branch `feature/m019-institutional-response`, HEAD
`b6dc7bf4dc025c3b4e72f53248785ffa04e43569`, no upstream. Fetch confirmed both
`origin/master` and local master at
`d0723b1551fc4e1aedf2d0fa4a5b5e3758902f49`, an ancestor of HEAD. The implementation
is `fe4a7667230ab0fd3e69a9ee5a8f95fd95668499`; b6dc7bf only stamps that identity
in this report. No published history or other branch was modified.

Reviewed the complete master-to-HEAD diff. Git records **21 distinct files**,
exactly the inventory above, including this validation report. Excluding the report
would give 20; that reconciles the arithmetic of the prior inventory discrepancy.
Git proves the final 21-file scope, not the contents of an earlier uncommitted
inventory. There is no unexpected 22nd implementation file or dependency change.

### Confirmed P1 defects and minimal repair

The original validator proved that an acquisition command completed before a
submission, but did not fully bind the acquisition transition to that command's
own interval, player actor and historical position. Confirmed accepted edits:

1. Move a notice-ledger `verify` transition just after its own command receipt.
2. Move that transition before the completed arrival at its acquisition place.
3. Attribute its acquisition receipt to an unrelated NPC.
4. Attribute the arrival used to prove player counter location to an unrelated NPC.
5. Leave a reordered, invalid observation unsubmitted: loading still succeeded and
   the institutional preview offered its ledger as available evidence.
6. Explicitly adopt institutions after an NPC-attributed historical acquisition:
   adoption promoted that unverifiable observation into the catalogue.
7. Attribute historical navigation-anchor adoption to an NPC: it still proved
   player origin when no subsequent trip existed.

Each case has a regression in
[test_institution_acceptance.py](../tests/test_institution_acceptance.py).
Initial four tests **failed before repair** (0.458s), then passed (0.549s).
The expanded eight-test run then exposed the remaining three gaps: **three
failures**, 0.939s. After the final repair, **eight passed**, 0.960s. The eighth
test is a valid schema-2 journey/acquisition/submission/read-only/disk-resume
control; no existing assertion was weakened.

Only production change: [institution_state.py](../institution_state.py).
It reuses one historical-location proof for institutional commands and source
acquisitions; requires completed player-attributed travel/journey frames; binds
each acquisition to its own player command and acquisition-time location; checks
the complete player catalogue, including unused and pre-adoption entries; and
binds legacy anchor adoption to its first subsequent command receipt. Existing
incident validators still establish channel, source-event and contact provenance.
The repair adds no persisted authority, schema version, RNG call, clock, command,
content, fee or outcome. Invalid input is rejected read-only rather than repaired.

### Architecture, adversarial evidence and authority

The bounded architecture is sound for these two incident adapters. Incident
events establish observations; explicit recipient-specific receipts establish
institutional knowledge; queues establish local beliefs; counter follow-ups
establish player receipt-time knowledge. An allegation remains a claim rather
than world truth or guilt. A civilian correction is not automatically a police
correction. Source documents acquired earlier do not expire merely because the
original incident's participation window closed.

All live effects are reduced on the private `game_service.execute_command`
candidate, validated and committed together. Daily synchronization runs within
the existing day boundary. `institutional_response` owns its reports, matters,
local access and receipts; incident adapters own original incident effects.
Read-only reports return detached data and do not grant follow-up knowledge.
Replay checks source/recipient/route/order/due processing, exact transition output
and final state. Stable receipt/source and correction identities bound effects.

Sixteen additional malformed-history probes rejected without changing world or
global RNG: unsupported police credibility; printed-to-documented promotion;
wrong recipient; wrong route; forged copy value; duplicate response; omitted
report; future due date; reset processing marker; unknown, boolean or missing
version; invented offender value; erased contradiction; duplicate delivery;
duplicate processing. An injected exception **after actual candidate report and
matter mutation** also left the original world and RNG unchanged.

No duplicate money, assistance copy, credibility stacking, legal punishment,
cross-desk knowledge transfer, or ordinary-life softlock was reproduced. Existing
tests exercise duplicate submissions/corrections/follow-ups, finite histories,
expiry, queue boundaries, detached inspection, delayed responses and late repair.
Historical proof is consistency checking, not authentication against a coordinated
rewrite of the whole career; not every past legal/access/action predicate is
reconstructed. Those limitations remain explicit rather than claimed solved.

### Independently executed tests

| Command | Actual result |
| --- | --- |
| `python -B -m unittest discover -s tests -q` before edits | **468 passed**, 146.725s. |
| Same full command after final production repair | **476 passed**, 161.052s. |
| `python -B -m unittest discover -s tests -p 'test_institution*.py' -q` | **50 passed**, 48.639s, final code. |
| `python -B -m unittest discover -s tests -p 'test_*incident*.py' -q` | **53 passed**, 16.547s after the initial repair; also included in the final full suite. |

### Independent uninterrupted-versus-disk-resumed campaigns

Each compares complete worlds after every day, not just final statistics.
New test-only policies live in
[institution_acceptance_campaigns.py](../tests/institution_acceptance_campaigns.py).
They use public views/service commands and the original campaign runner; they
introduce no game mechanics. The unattended policy never issues an institutional
player command after explicit adoption. The corrections policy corrects three
different original reports and stops after their processed responses arrive.

| Exact command | Final-code result |
| --- | --- |
| `python -B institution_campaigns.py --days 365 --seed 313 --mode documented --resume-every 30` | 116.828s; 13 checkpoints; 8 reports, 2 responses, 1 copy; both desks documented; cash $1,632, arrears $0. |
| `python -B institution_campaigns.py --days 365 --seed 887 --mode unchecked --resume-every 30` | 114.949s; 13 checkpoints; 8 reports, 2 responses, 1 copy; civilian needs documentation, intake documented; cash $1,632, arrears $0. |
| `python -B tests/institution_acceptance_campaigns.py --policy unattended --seed 443 --days 90 --resume-every 1` | 20.899s; 90 checkpoints; **0 institutional player commands**, 6 automatic reports, 0 responses/copies; both profiles unestablished; cash $430, arrears $0. |
| `python -B tests/institution_acceptance_campaigns.py --policy corrections --seed 557 --days 90 --resume-every 1` | 37.241s; 90 checkpoints; 10 institutional commands, **3 legitimate corrections**, 11 reports, 5 responses, **1 copy**; both profiles documented; cash $422, arrears $0. |

All four end with heat 0, no arrest; the civilian alarm matter closes insufficient
while the notice and police alarm records become documented through their own
sources. Existing lawful work, not institutions, provides income. The correction
policy's rejected-poll counter is zero; rejected retries were exercised separately
in the CLI and regression tests, not inferred from that counter.

| Campaign | Full sorted compact-JSON world SHA-256 |
| --- | --- |
| 313/documented/365 | `0eefea9b3da989bec30362c06d0af7980fc7c829deb2e9715909b0b3682072a1` |
| 887/unchecked/365 | `3a4974c4fff8342bccec6594e5c398f07b0328c01bb94b0ce06fbd5635fc0b34` |
| 443/unattended/90 | `d756802c07282340280507299dec8d73ad763ef646e183b5d5d50334671b7bb3` |
| 557/corrections/90 | `a56b15371dad483e72f75061f809f2b541ddaed00136bd043864c65df68829fe` |

Reran all four historical commands listed earlier in this report **after the
final repair**. All **six exact historical hashes in that table match again**.
Actual runtimes: Night Shift 17/42, 71.796s/62.560s (13 checkpoints each);
Wrong Notice 73/help and 191/unchecked, 76.746s/78.730s (13 each);
mobility 17/42, 7.140s/7.275s (30 daily checkpoints each). The old reducers,
content, identities and mobility policies were not modified.

### Independent persistence and compatibility evidence

- All **15 recursively enumerated** historical fixture files load and advance
  without institutional adoption. Thirteen top-level fixtures additionally
  underwent a separate disk round trip; the full suite covers the nested files.
- The genuine M018 fixture retains SHA-256
  `befd147e7e1ea1b83ac8db0803c006461afd3b3bab67f0401cdc18b89e1bb246`
  through **20** load/resaves, then explicitly adopts version 1 successfully.
- Generated two genuine M019 saves with the **original b6dc7bf executable** in an
  isolated `git archive`, then loaded with the repaired executable and performed
  20 byte-identical resaves each: documented record
  `ff3c294e0aef323fc37bf75c6a7b3a9dfe9b3241a61603d83934c7637542d123`;
  late copy
  `57411a337a6ea302efdd40146777b5bb2a02d06a17d7bb339e6c570d29bee21a`.
- Rechecked the actual preserved pre-M017-B public/contact files: both hashes
  listed above remain byte-identical; the original forged Tess file rejects.
- Terminated an actual disposable writer subprocess just before primary
  replacement, after backup publication. Old primary and `.bak` remained
  byte-identical, valid and recoverable. Restart/save/load succeeded; duplicate
  follow-up rejected with world/RNG unchanged. One staged orphan remained inside
  the disposable directory until cleanup. No original career was overwritten.
- No `WinError 32` was reproduced. Restricted-sandbox attempts encountered
  temporary-directory `WinError 5` and non-completing runs; those attempts were
  interrupted and are **not** successful evidence. The isolated checkout, CLI,
  focused and historical/daily disk probes were rerun successfully with required
  temporary-directory access. No speculative persistence rewrite was made.

### Four actual CLI paths, same seed 313

Each used real `python -B gameplay.py --seed 313 --save <temporary-path>`, then
separate `--load --save <same-path>` processes, saved EOF interruptions and a
deliberately rejected retry. The final harness recognizes the actual
`Cannot complete command:` message; its earlier `Error:` matcher was corrected.
Final runs had no unexpected command failures. After every rejected retry, the
loaded world matched the prior checkpoint exactly.

Common route: settle in; day 1 enable both incidents and institutions; day 4
travel p032, discover both public notices, refuse the old alarm job, visit n13.
Use the stable Night Shift/notice instance IDs recorded earlier. Save and resume;
advance nine days to day 13. No gameplay state was injected into these careers.

| Path | Actual choices and persistent result |
| --- | --- |
| A Responsible | Verify `.claim.ledger`, submit at civilian; travel p044 and submit actually heard `.source.alarm_reported` at intake. Follow up at both counters day 13. Civilian documented; 8 reports, 2 responses, 1 copy; no correction/withholding. |
| B Unchecked | Submit `.claim.poster` at civilian, then follow up day 13. Civilian needs documentation; 7 reports, 1 response, 1 copy. Intake responses remain unread. |
| C Withholding | Withhold notice at civilian and alarm at intake; no submissions/follow-ups. Two private withholding entries, 6 independent NPC reports, 0 responses/copies; player profile unestablished. Institutions still progress. |
| D Late recovery | Follow B, then explicitly correct its original report using the actually received `.copy.delivery_day` source; wait and follow up day 14. Civilian documented, 8 reports, 2 responses, 1 correction, still only 1 copy. Original claim and correction trail remain. |

A/B/C each have $10, no arrears on day 13. D has $0 and $20 arrears on day 14
from the existing weekly room charge. A further real CLI continuation advanced
to day 15, accepted an available lawful work offer, earned cash and returned
home successfully. All four have zero heat/cases and no arrest. In B/C/D, private
police cause information never appeared as a player source or received response.

| CLI path | Checkpoint full-world SHA-256 |
| --- | --- |
| A/day 13 | `d7809dcea16d19d8a8fdda222ffe3b0591fcfcf286bbfc67e1d15ac49884b3da` |
| B/day 13 | `b2a682245a5f5d87a96578f9ebfc84c286f547876c7b3ee259b8e044d911ce4d` |
| C/day 13 | `1828e4b5f8f2323de69d15bb518b0c1d7c44fe825be17b7fee5eb7426ed83df0` |
| D/day 14, before ordinary-work continuation | `f01bcdae6e72872e116671fc67f7455eedc474fbbf22f8b3d09f844d88ba8586` |

These are genuinely different persistent records/access/knowledge states, not
four exclusive career endings. A and D can converge on documented access through
different histories and action costs. Reporting is not profitable. Variety remains
bounded by two authored incidents; repeated trips and wage work can still feel
repetitive. No compulsory reporting grind was added.

### Performance, risk and publication recommendation

Executed standard-library `cProfile` around
`institution_campaigns.run(613, 'documented', 30, 1)`: 31.114s, 89,720,136 calls,
30 disk checkpoints, parity hash
`60f7607b5a806e594be0ffde45041772fb561062909f25a978fe7398de729469`.
Cumulative times overlap: deepcopy 24.564s; career validation 16.491s;
atlas loading/detachment 12.883s; old incident replay 5.826s; institutional
validation 5.506s. Repeated detached atlas/context construction and full career
copy/replay dominate this sample. These are profiled, instrumented times, not
unprofiled latency estimates. No caching shortcut or weaker validation introduced.

- **P0:** none confirmed.
- **P1:** seven demonstrated provenance bypass cases repaired and regression
  tested; no confirmed unresolved P1 in the exercised M019 scope.
- **P2:** full-history/copy/atlas costs at scale; limited authored source adapters;
  consistency rather than cryptographic authenticity or exhaustive reconstruction
  of past custody/access/action predicates; intermittent Windows sharing concern
  not reproduced; staged orphan after forced termination. Wider institutions,
  staff autonomy and careers remain future design, not hidden implementation.

**Recommendation: ready for PR review**, with those P2 limits disclosed. No push,
PR creation, merge, history rewrite or M020 implementation was performed. No new
GitHub CI result is claimed for this unpublished audit.

Audit changes are exactly six files: `institution_state.py`,
`tests/test_institution_acceptance.py`, `tests/institution_acceptance_campaigns.py`,
this report, `docs/GOON_INSTITUTIONS_AND_RECOVERY.md`, and `PROJECT_STATE.md`.
Combined master-to-audited-M019 scope is **23 files**: the original 21 plus two
test/tool additions. Protected gameplay producers, persistence writer, schemas,
content pins, action/travel allowances and existing tests remain unchanged.
All three changed Python files parse, changed Markdown fences balance, all 52
relative file links in the three audit documents resolve, and `git diff --check`
passes. No third-party validator or dependency was installed.
