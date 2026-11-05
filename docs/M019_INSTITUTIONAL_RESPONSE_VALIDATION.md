# M019 — Institutional Knowledge & Response: executed validation

Mission 023. Local implementation only; no push, PR or merge is authorized.
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
for unpublished local work. Implementation commit identity is recorded after
the validated local commit; no self-referential commit hash is fabricated.
Changed Python/JSON parse successfully, Markdown fences balance and all **175
relative file links in eight changed Markdown documents** resolve. The fixture
SHA and its LF attributes were checked; `git diff --check` passed. No external
Markdown linter or other dependency was installed.
