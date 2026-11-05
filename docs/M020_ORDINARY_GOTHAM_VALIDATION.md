# M020 Ordinary Gotham — implementation and validation

Mission 026 implementation and Mission 027 independent acceptance are local
implementation, testing, targeted repairs and commits only. No push,
PR, merge, M021, prologue, transportation mode or Court gameplay is authorized.
This report is execution evidence; the existing daily-life contract remains the
canonical design rather than a duplicate design bible.

## Verified baseline

Fetched master at `6682019857ccad4553fcdc04f7a7e7e046b2def0`, the merge of M019
PR #20 on 2026-11-05. GitHub run `42035644057` succeeded: 476 tests, 162.187s.
The original local feature was clean at audited M019 `48b4af9`; its tree exactly
matched merged master. Existing branches and commits are preserved. New local
branch: `feature/m020-ordinary-gotham`, from verified `origin/master`.

## Inspection and bounded implementation plan

Implemented before M020: explicit daily-life adoption; $30 weekly cooperative
room contribution, $30 arrears cap and continued home access; prepayment and
maintenance credits; four weekly repair allocations and a reference-gated audit;
Tess/Cal standing, promises, finite choices, actual cash receipts; 18 travel TU,
three shared actions; two independent incidents and recipient-specific desks.
Full employment, arbitrary rent terms, eviction and NPC scheduling are absent.

1. Preserve all old content pins, IDs, rent receipts and non-adopter behavior.
2. Add optional, explicitly adopted ordinary-life version 1, active next day.
   Observe future actual repair completions for bounded employment standing.
3. Add one funded home-work allocation per week: prerequisites, two-action pay,
   deterministic disclosed cancellations and one rescheduling request. A reserved
   completion becomes an explicit, dated commitment, with bounded missed-work
   consequences. Existing repair work remains the dependable alternative.
4. Add one conditional $20 Tess support advance per career, a seven-day repayment
   obligation and bounded late/repaid memories. No interest or automatic seizure.
   Reuse the cash ledger, room grace/maintenance and existing contact authority.
5. Reuse service candidates, the existing day pipeline and choice assessment.
   Validate all new effects against source events, completed command frames,
   historical position, actual cash transactions and contact memories.
6. Test adversarial settlements, budgets, histories, compatibility and disk
   interruptions; run five campaign policies, old hashes and real CLI paths.
7. Update canonical documentation, review scope, commit locally and stop.

Court direction is documentation only: remove Milo from the proposed future
roster; keep the Court a separate optional organization, entirely undiscoverable
before the final third of meaningful progression. No runtime reference or trigger.

## Execution evidence

Implemented on the verified local branch. No publication is authorized or
claimed. The [choice contract](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md#m020-extension--ordinary-work-housing-and-support)
is canonical for actual terms; the [architecture](GOON_CONTENT_ARCHITECTURE.md)
describes ownership. Existing prologue and broad employment proposals are not
implemented by this slice.

### Baseline discrepancy and final tests

The first quiet local baseline attempt ran unusually long and was interrupted;
it is not a passing result. An unchanged, verbose diagnostic run executed all
476 original tests in 763.498s, with **one failure**: the old M015 stale-letter
CLI test counted three rejections instead of two. Delayed traceback diagnostics
showed active copying/JSON work, not a demonstrated file-lock hang. The failure
did not capture its extra CLI message, so no root cause or `WinError 32` fix is
claimed. No existing runtime had been changed during that run; only unimported
new modules/tests and documentation were being drafted.

The unchanged nine-test M015 module then passed in 1.635s. Thirty additional
actual CLI repetitions each produced exactly its two intended rejections. An
isolated, unmodified `git archive` of `6682019` then passed the full **476 tests
in 148.482s**. This establishes the baseline independently of in-progress files.
The original tests and their assertions were never edited or weakened.

| Exact command | Executed result |
| --- | --- |
| `python -B -m unittest discover -s tests -q` in isolated merged-master archive | 476 passed, 148.482s. |
| Same full command after initial integration | 504 passed, 182.495s. |
| Same full command after malformed-base validation repair | 505 passed, 178.894s: 476 baseline plus 29 new methods. |
| Same full command after final withdrawal repair | **506 passed, 181.836s**: all 476 baseline plus 30 new methods. |
| `python -B -m unittest discover -s tests -p test_ordinary_life.py -q` after final withdrawal repair | **30 passed, 9.219s**, final source. |

Focused coverage includes adoption without refresh/backfill, pending activation,
observed repair provenance, two-action home wages, duplicate work, pinned-rate
rescheduling, denied negotiation, missed and withdrawn eligibility, no-penalty
refusal/expiry, posted cancellation, one-shot support prerequisites, overdue
non-compounding debt, repayment, maintenance/prepayment integration, three actions,
18 TU, execution-time place, schema-2 journeys, actual historical navigation
anchors, institutional isolation, detached reports, failure rollback, failed
publication, historical fixtures and five 21-day daily-resume policies.

Adversarial history checks reject changed versions/employment/pay/location/action
snapshots, an NPC-attributed command, duplicate or missing transitions, reordered
repair observation and a forged shortfall authorizing unsupported work. Edited
support balances/status/deadlines reject on disk. Validation preserves world/RNG.

One new integration defect was demonstrated before final delivery: missing
`home_id` or `opening_cash` inside an adopted save escaped as `KeyError` before
ordinary replay's error guard. The expanded malformed-base test **failed in two
subcases** before repair (29 methods, 10.855s). Required base-life shape/type
checks now reject with `ValueError`; the same test covers missing/null fields,
the focused suite passes and the final full suite was rerun. This change does
not alter a valid career or its replay hash.

A final review found that a reserved offer's future work window also blocked
immediate withdrawal. One new regression **failed before repair** (1 test, 0.069s,
`Available on days 4 through 5`). Reservation management now starts at acceptance;
paid work has a separate assessment gate to the actual delivery date. The same
regression passes, withdrawal has exactly one bounded consequence, future wages
still reject, and focused/full suites and both year campaigns were rerun.
This changes no existing campaign's selected action or saved state.

### Implemented decisions and authority

There is one new optional `ordinary_version: 1` / `ordinary` arrangement, active
next day. It observes actual **future** repair choices for employment 0–6; neither
adds an old wage nor duplicates a personal memory. One distinct weekly funded
home-kit allocation costs two actions and pays $24, or $28 with standing 3. It
requires a source-backed completion or real room arrears. Seed+week divisible by
three cancels that allocation publicly for supplies, with no player blame.

One action requests a later delivery at home under Tess's posted reservation
terms: standing 1 accepts; standing 0 declines without a relationship penalty.
It is a ledger request under preauthorized terms, not a claim that an NPC is
physically present. A successful request pins its current wage and tomorrow's
two-day window. A denied request leaves immediate completion open. One request
per allocation prevents negotiation farming. Missed/withdrawn **accepted** work
costs at most one employment and one Tess standing; ordinary shifts remain viable.

One conditional support reserve supplies $20 **once per career**, never as a
wage. Tess handles it at home on ordinary roster days 0, 2 and 5. The player
needs arrears or cash below $30 with a review within two days. Repay $20 at the
home account box within seven days, one action. A late obligation has one -1
memory, no interest or automatic debit. Repayment has one +1 memory, closes the
obligation and never replenishes the reserve. Refusing support creates no debt.

Housing remains the original p031 cooperative arrangement, with $30 weekly
reviews, actual prepayment, $30 capped arrears, maintenance credit and continued
basic access. The new planner displays the real account and records advance
notices within two days; it does not own another rent balance or evict anyone.

Every player mutation uses the existing service candidate. `ordinary_life.reduce`
returns explicit effects; its adapter delegates money to the actual life ledger
and observed personal facts to Tess's existing memory authority. Source-backed
replay validates command intervals/actor/arguments/cost, completed actual travel,
cash, housing, custody and action facts, each funded effect, every delegated memory
and final state. Daily/source processing is idempotent; reports/load never tick.
Institutional knowledge receives no employment, support or loan transmission.
Existing incident reducers, content pins and settlement identities are untouched.

This is a small work/support adapter, not a universal scheduler or another quest
engine. It reuses `choice_engine` visibility/eligibility; no new transport, clock,
character creation, legal source, institution or narrative episode was introduced.

### Thirty-day and long campaigns

Runner: [ordinary_campaigns.py](../ordinary_campaigns.py). Every day compares
complete uninterrupted and resumed worlds. Each campaign starts at day 2 after
explicit life/ordinary adoption, then performs the stated number of transitions.
Support/recovery policies explicitly configure $0 **before** life enrollment to
exercise poor starting profiles; the CLI's default $40 start is unchanged.
No ledger is edited after enrollment and no criminal or incident job is used.

Common exact invocation:

```text
python -B ordinary_campaigns.py --seed 101 --policy stability --days 30 --resume-every 1
python -B ordinary_campaigns.py --seed 211 --policy recovery --days 30 --resume-every 1
python -B ordinary_campaigns.py --seed 307 --policy refusal --days 30 --resume-every 1
python -B ordinary_campaigns.py --seed 887 --policy negotiation --days 30 --resume-every 1
python -B ordinary_campaigns.py --seed 997 --policy support --days 30 --resume-every 1
python -B ordinary_campaigns.py --seed 431 --policy stability --days 365 --resume-every 30 --incidents
python -B ordinary_campaigns.py --seed 613 --policy recovery --days 365 --resume-every 30 --incidents
```

| Policy/seed/days | Actual result | Seconds |
| --- | --- | --- |
| Stability/101/30 | 30 daily checkpoints; cash $180, arrears $0, employment 6, three completed kits, two supply cancellations, support unused. | 3.130 |
| Recovery/211/30 | 30 daily checkpoints; cash $86, arrears $0, employment 6, one accepted delivery missed, two later kits completed, overdue advance repaid. | 2.964 |
| Refusal/307/30 | 30 daily checkpoints; cash $0, arrears $20, employment/Tess 0, four allocations declined, support declined with $0 debt. Basic home access retained. | 2.145 |
| Negotiation/887/30 | 30 daily checkpoints; cash $180, arrears $0, employment 6, three completed allocations through reserved windows, no advance used. | 2.792 |
| Support/997/30 | 30 daily checkpoints; cash $120, arrears $0, employment 6, one $20 advance repaid; no further borrowing. | 2.837 |
| Stability/431/365 | 13 checkpoints; cash $1,556, arrears $0, employment 6, 35 completed allocations, 18 cancelled, support unused. | 190.591 |
| Recovery/613/365 | 13 checkpoints; cash $1,434, arrears $0, employment 6, 33 completed, 17 cancelled, one missed, one expired, overdue support repaid. | 189.786 |

All seven finish with heat 0, no cases and no arrest. The three required short
campaigns, plus negotiation/support, do not adopt either incident or institutions.
Both year campaigns explicitly adopt both incidents and M019, but never discover
or participate; independent progression and resume still match. Earlier year
runs before the malformed-field guard gave the **same hashes** (192.711s and
191.559s), as did the intermediate field-guard runs (179.291s and 181.901s).
The table records reruns after the final withdrawal correction. No balance was forced.

| Campaign | Full sorted compact-JSON SHA-256 |
| --- | --- |
| Stability/101/30 | `5d424d06205ddee69e43adf02c108c71c1f5e34641f82f6f15f35b20ecb46d11` |
| Recovery/211/30 | `890bfc52c24bd6d7a7bffd11c6610e924c4d2c092a176dbc47315c2729caf32a` |
| Refusal/307/30 | `d137d361a7d3ee14595c53262a450283bde169e007b643262501a0cf4c70ba66` |
| Negotiation/887/30 | `d58b4b33a6e65129d1e94629e7748fef22c170c57126b2277a17b00de94421c3` |
| Support/997/30 | `c439e0b113b025b64620d090dfbabb7937ae2cae32ab711f6b3e5430d9af1a45` |
| Stability/431/365 | `8b35c0cf8abb7b0a202f2461418124350be316a0d04b115a3f9c0e8d466996a4` |
| Recovery/613/365 | `e086ab3ae55b75e4febf81106c46cb2bf1fb92bd5901fceb44ed39e2d3924c19` |

Two separate Python processes with `PYTHONHASHSEED=1` and `77` ran the
887/negotiation/30 daily-resume policy. A third run reversed faction, people and
contact dictionary insertion order. All matched its hash above. New decisions
use no random draw or dictionary insertion order.

### Six historical replay hashes

Executed after integration and malformed-base hardening, without ordinary adoption:

```text
python -B incident_campaigns.py --days 365 --seeds 17 42 --resume-every 30
python -B notice_campaigns.py --days 365 --seed 73 --mode help --resume-every 30
python -B notice_campaigns.py --days 365 --seed 191 --mode unchecked --resume-every 30
python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1
```

| Historical campaign | Unchanged SHA-256 | Seconds |
| --- | --- | --- |
| Night Shift 17 | `6bcad488e55c01db05cc5e83d6e1f370ede3bd7780bb0cdee5bb8813327566ed` | 74.542 |
| Night Shift 42 | `578b6ae0543e40242b088e37700dfe64be28fbebc7a5f8f043873b7dcf1fff9f` | 63.543 |
| Wrong Notice 73/help | `593386231e6df47bac4d9c279a10bd011b67d0f6a08e63d6f56ab3c68245bc09` | 83.341 |
| Wrong Notice 191/unchecked | `ca5996dd6800bdd349f082b02ee67ff85d418673311d613ed9a2e51e806bbcae` | 83.362 |
| Mobility 17 | `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3` | 7.118 |
| Mobility 42 | `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d` | 7.613 |

Night/notice resumed 13 times per seed; mobility 30 times each. No historical
fixture or expected hash was edited. Only explicitly adopted M020 worlds change.
The later withdrawal correction is confined to adopted reservations; it does not
execute in these historical careers. Final full regression also retains their
original compatibility tests.

### Actual CLI playthroughs and different futures

Real subprocess invocations of `python -B gameplay.py --seed 17 --save <temp>`
and separate `--load --save <same-temp>` sessions supplied actual stdin commands,
saved EOF interruptions and deliberate retries. No Python mutation of those
careers, poverty preset, criminal job or incident adoption was used.

Common beginning: `settle_in`, `wait`, `enable_ordinary`, `wait`, `ordinary`.
The arrangement activates on day 2. All five used actual home/store movement.
`ordinary_choices` displayed costs/eligibility before substantive selections.

| Path | Executed choices and persistent outcome |
| --- | --- |
| A Stability | Day 2 travel p032, `choose goon.choice.0.crossroads lawful`, return home, wait; day 3 complete `goon.ordinary.batch.0 work`. Resume and advance to day 14: cash $24, no arrears, employment/Tess 2, support unused. |
| B Negotiation | Same real repair prerequisite; day 3 choose `negotiate`, save/EOF with a live reservation, resume, wait and deliver day 4. Day 14 cash/standing equal A but the allocation retains its negotiated flag and pinned later delivery history; the action and deadline commitments were different. |
| C Social support | No wages through day 14; existing room shortfall $20. Borrow `goon.ordinary.support`, use `pay_room`; next day work `goon.choice.2.opening_shift`, return home and repay `goon.ordinary.repayment`. Day 15 cash $0, arrears $0, employment 1, Tess 2; one closed $20 obligation, never another advance. |
| D Setback/recovery | Reach day-14 shortfall and borrow, then miss the seven-day repayment. The actual day-21 room charge uses available funds; one overdue memory persists. Day 22 work `goon.choice.3.opening_shift`, return home and repay; day 24 complete batch 3. Cash $24, arrears $0, employment/Tess 2; overdue/repaid history remains. |
| E Refusal | Day 2 decline support; day 3 decline batch 0. Day 14 cash $0, arrears $20, employment/Tess 0, support declined with no debt. A further real CLI continuation worked the day-15 opening shift, returned home and cleared arrears with `pay_room`. |

All five exit successfully with zero heat/cases/arrest and no faction affiliation.
An intentional repeated closed allocation/support request rejects once per path;
save/reload after retry leaves the entire world unchanged. These are distinct
records and obligations, not five permanently exclusive endings. Negotiation can
converge economically after fulfillment; support and late records cannot be
erased or turned into a second grant. The automated recovery policy additionally
demonstrates an accepted delivery missed before later work.

| CLI checkpoint | Full-world SHA-256 |
| --- | --- |
| A/day 14 | `4773f74d9f2f47c2d53dce94866ed683330e94639531fa025f95b72eacb429a2` |
| B/day 14 | `2f65957160e7e8106442331d0f9a79d2494016c99228c741e009abeef24173b7` |
| C/day 15 | `bb8125c92ddabf2728d8c950471198e26c4a9df219d3c0f126129b5d40100d85` |
| D/day 24 | `81b24ece9406ccd6277a5ef170f6ed125fc4b02f4c45d9c9683cdd518fad8329` |
| E/day 14, before recovery continuation | `47bed1b09a9c706937f8751236e79380b93445596eafb40b9d325d521347a2b2` |

### Save compatibility and interrupted publication

The focused suite loads/advances all 15 existing historical fixtures plus the
genuine M018 institution fixture without ordinary adoption. A pre-M011 career
can follow existing navigation/settle-in adoption then explicitly adopt ordinary
terms. Modern schema-2 journeys and later home work also round-trip successfully.

Generated a genuine pre-M020 save with the unmodified **6682019 executable** in
an isolated archive: known notice ledger, M019 documented submission and received
copy on day 14. SHA-256:
`4a3cfb4b1b3a066244880f24d068c5929b748dd99c08039d19192169b3e541ea`.
Twenty new-executable load/resaves were byte-identical and did not adopt ordinary
state. Explicit adoption then preserved the entire player, daily-life, institution
and navigation state, with zero employment and unused support. Compatibility is
old-to-new; an adopted career requires an M020-capable executable.

Beyond replacement-failure tests, an actual disposable writer with an M020
support debt was killed immediately before primary replacement, after backup
publication. Old primary and `.bak` remained byte-identical and both loaded as
the old world. Restart/save/load of the candidate succeeded; another support
request rejected with world/RNG preserved. One staged orphan remained until the
disposable directory was cleaned. No original save or persistence implementation
was modified. No new reproducible Windows sharing root cause was established.

### Economy, variety, remaining findings and limits

- **P0:** none confirmed.
- **P1:** the demonstrated malformed-base error escape was repaired; no confirmed
  unresolved P1 in the exercised slice. No duplicate wages, assistance, rent
  credit, negative transfer, budget bypass or ordinary-career softlock reproduced.
- **P2:** the old intermittent CLI extra-error observation remains unexplained;
  it did not reproduce in 30 exact retries or final full tests. Full-history
  replay/copying remains a long-career cost. Provenance proves consistency, not
  cryptographic authenticity of a fully rewritten history or exhaustive old-world
  replay. Source adapters and employee/funding models remain deliberately bounded.
  The premature withdrawal lock was also reproduced and corrected before delivery.

Income is finite by source/window: old funded shifts plus at most one $24/$28
kit allocation per week. No action can pay again after completion; cancellation
and expired opportunities do not generate money. The separate assistance reserve
is exactly $20 once, with actual repayment rather than replenishment. Unpaid rent
does not pay the player or compound, and the old cap/grace policy is preserved.
Employer funds are authored allocations, not simulated treasuries or a claim of
economic realism. Multi-week lawful life remains viable without either incident.

Variety comes from dependable store versus home work, present versus reserved
action commitments, supply availability, real housing dates, conditional support,
repayment and relationships. Main shallow areas: one cooperative arrangement,
no employer autonomy/contracts market, simple preauthorized negotiations and
bounded contact availability. Weekly work/maintenance can still feel repetitive;
no daily commuting requirement or reporting grind was added. There are no real-time
waits, premium currencies, external services or paid APIs.

The future prologue contract is preserved. Court policy is **design only**:
verified current roster has **34 distinct individual/mantle IDs**, Milo absent,
and the Court is a separate optional organization, not counted as a rogue row.
It is entirely undiscoverable before the final third of meaningful progression;
elapsed days alone never qualify. No Court/Talon/owl/Milo reference exists in
Python or JSON runtime content, and no clue/trigger/gameplay was introduced.

### Exact changed-file inventory

Exactly **19 files** from verified master:

| Files | Purpose |
| --- | --- |
| `ordinary_life.py`, `ordinary_state.py`, `ordinary_content.py` | New bounded reducer/service adapter, source-backed read-only validation and pinned content loader. |
| `content/ordinary_life_v1.json` | Original work/support text, stable terms and action costs; no new character or asset. |
| `game_service.py`, `gameplay.py` | Two service commands, read-only CLI views and one existing day-phase hook. |
| `daily_life.py`, `daily_life_state.py`, `life_presentation.py` | Adopted home projection, actual-ledger/new-memory validation and pure presentation. |
| `ordinary_campaigns.py`, `tests/test_ordinary_life.py` | Public-command deterministic campaigns and 30 meaningful regressions. |
| `README.md`, `PROJECT_STATE.md` | Actual integration history, commands, terms, current scope and results. |
| `docs/GOON_CONTENT_ARCHITECTURE.md`, `docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md`, `docs/GOON_M015_DAILY_LIFE_CONTRACT.md`, `docs/GOON_MILESTONE_ROADMAP.md` | Canonical architecture/daily-life/roadmap integration without a duplicate design bible. |
| `docs/GOON_ROGUE_ENCOUNTERS_DESIGN.md` | Approved roster removal and strictly hidden, future Court restriction only. |
| This report | Actual validation, limitations and commit provenance. |

No existing test/fixture, incident/institution reducer or content pin, atlas,
mobility schema, legal/faction economy, persistence writer, workflow or dependency
was changed. No M021, push, PR creation or merge was performed.

Final static review: all ten changed Python files parse; the new JSON parses;
Markdown fences balance and all 179 relative file links in eight changed Markdown
documents resolve. `git diff --check` passes. The pinned ordinary content hash is
`319e3e02a40af98603e5490b2f7a209e29a69406b53c2bf7bf1d7f440818efb4`.
No linter, package or external service was installed. Final fetch still shows
`origin/master` at `6682019`; the old local master at `d0723b1` and every prior
feature branch remain preserved. The M020 branch has no publication upstream.

## Local commit provenance

Validated implementation and accompanying tests/documentation:
`a0ab17ff80407a0ea1e7bba38673f280c78ce403`, parent
`6682019857ccad4553fcdc04f7a7e7e046b2def0`.
The following report-only commit records that identity; runtime, content, tests
and replay hashes are unchanged. Its final HEAD SHA is supplied in the Mission
026 delivery, avoiding a self-referential commit hash inside its own file.
Both commits are local only; no publication or M021 work was performed.

## Mission 027 — independent acceptance and economy/persistence audit

The earlier results above are retained as Mission 026 evidence. Everything in
this section was independently executed against the actual completed branch,
not inferred from that report. No feature/content expansion was undertaken.

### Verified checkpoint and scope

Initial worktree clean; branch `feature/m020-ordinary-gotham`, HEAD
`cd20633db82132f38aeb9bd465ba93206394d111`, with implementation parent
`a0ab17ff80407a0ea1e7bba38673f280c78ce403`. Fetch confirmed origin/master remains
`6682019857ccad4553fcdc04f7a7e7e046b2def0`, the M019 PR #20 merge and M020 merge
base. Local master remains preserved at `d0723b1`. The remote is the expected
CapuchaRojo/gotham-underworld repository; no branch or history was rewritten.
Reviewed the full **19-file** master-to-feature inventory above and its runtime,
content, tests, integration and canonical documentation. No unrelated dependency,
workflow, transport or gameplay change was present.

Read-only preflight used `git status --porcelain=v1`, `git branch --show-current`,
`git rev-parse HEAD origin/master master`, `git merge-base origin/master HEAD`,
`git log --oneline origin/master..HEAD`, `git diff --name-status origin/master...HEAD`,
`git remote -v`, `git fetch origin` and `gh pr view 20 --json state,mergeCommit,mergedAt`.
The untouched baseline command `python -B -m unittest discover -s tests -q`
passed **506 tests, 181.799s**, before audit source changes.

### Confirmed P1 findings, reproductions and repairs

The normal command boundary already prevented straightforward duplicate
completion/borrowing. The confirmed defects involved **edited saves** whose
contradictions passed validation, followed in several cases by real commands
granting benefits. Test fixture generators bypass live eligibility deliberately;
they do not represent a public CLI shortcut.

| Finding | Reproduced behavior before repair | Minimal correction |
| --- | --- | --- |
| Inherited work eligibility | Native-looking repair records created at home, after three other paid actions, or as an unqualified stock audit loaded successfully and earned employment. An earlier false audit was accepted even with its real reference acquired only later. NPC-attributed invitations/deliveries or a delivery made away from home also qualified. | `ordinary_state.py` now checks consumed repair/reference sources against their actual historical place, freedom, window, remaining actions, own player frame, prior standing and prior invitation/delivery. It never uses the wage's own memory or future knowledge to qualify work. |
| Counterfeit maintenance allocations | Two copied room offers with different IDs but the same actual obligation loaded. Three **real** help commands then credited $30 against one review rather than its funded $10. Unknown source IDs and moved review windows were also accepted. | `daily_life_state.py` binds every room review to its real unpaid due receipt, canonical cycle identity, actual processed opening day, expiry and original roster week. Real catchup reviews remain separate valid allocations. |
| Unsupported repayment funding | After the legitimate $20 advance was spent on rent, one fabricated `existing_rules` credit inside the repayment frame financed a fake repayment. Null/wrong command attribution and moving the row into the previous payment frame also passed. Merely restricting closed frames still allowed relocating its event into an earlier wait while leaving the ledger order unchanged. | Known M015/M020/M019 commands now have exact financial transaction footprints and physical frame ownership. Cash-event order must equal the continuous ledger's order. No invented legacy credit can ride those commands or masquerade as earlier money through reordered events. |
| Erased action costs | Editing only `actions_used=0` or an older `action_day` loaded. A real fourth same-day courier command then earned another payout. | Recorded command costs from adoption onward cannot exceed three/day. Effective saved usage must be at least the known committed cost, preserving unknown extra legacy usage rather than fabricating an exact missing history. |

All new checks are read-only. They add no schema/version, balance, clock,
content, event, RNG draw, wage, fee or gameplay rule. Only two production files
changed: `ordinary_state.py` and `daily_life_state.py`.
Code references: [consumed work/reference proof](../ordinary_state.py#L46),
[saved action-cost proof](../ordinary_state.py#L185),
[cash chronology](../daily_life_state.py#L72),
[funded room review](../daily_life_state.py#L95), and
[closed financial commands](../daily_life_state.py#L329).

### Executed red/green regressions

New file: [test_m020_acceptance.py](../tests/test_m020_acceptance.py), **16 methods**.
It also includes positive qualified-audit, actual catchup and simultaneous
work/rent/support controls. Original tests remain unchanged.

| Command / stage | Actual result |
| --- | --- |
| `python -B -m unittest discover -s tests -p test_m020_acceptance.py -q`, original source | 11 methods, **11 failing assertions/subcases**, 0.553s: work/reference and counterfeit-room cases accepted. |
| Same command after the first repair | 11 passed, 0.663s. |
| Expanded same command before funding/counter repair | 16 methods, **8 failing assertions/subcases**, 1.067s. |
| `PYTHONPATH=tests python -B -m unittest test_m020_acceptance.M020AcceptanceTests.test_repayment_cannot_be_financed_by_an_extra_closed_command_credit -q` after the first funding repair | One method, **one remaining failure**, 0.319s: event relocated into earlier wait. |
| Original focused command after cash-order repair | **16 passed, 1.205s**. |
| `PYTHONPATH=tests python -B -m unittest test_ordinary_life test_m020_acceptance -q` | **46 passed, 10.472s**, final source. |
| `python -B -m unittest discover -s tests -q` | **522 passed, 205.102s**, final source: all 506 preserved plus 16 audit regressions. |

The `PYTHONPATH=tests` notation above describes process-local configuration; on
PowerShell it was `$env:PYTHONPATH = 'tests'` followed by the stated Python command.
Intermediate existing-module checks also passed: 30 original M020 tests and 42
institution tests; final full regression includes both after all repairs.

Additional executed probes: four malformed command shapes reject with world/RNG
unchanged; twelve saved contract-date mutations (boolean, null, string, negative,
float and list for opening/expiry) reject on disk. A stale home-work preview
rejects after leaving home. Eighteen TU remain exhausted after actual home work,
and another trip rejects purely. Repeated reads/synchronization do not process
misses twice. No early wage, paid withdrawal, duplicate completion, repeat
rescheduling or deadline escape was reproduced through normal commands.

### Independent extended campaigns

Each campaign compares entire uninterrupted/resumed worlds after every day.
These seeds are additional to Mission 026's seeds. The two 90-day campaigns also
serve as the required extended low-income recovery and extended refusal runs;
they are **four campaigns**, not six separately counted scenarios.

```text
python -B ordinary_campaigns.py --seed 1291 --policy stability --days 365 --resume-every 30 --incidents
python -B ordinary_campaigns.py --seed 1543 --policy recovery --days 365 --resume-every 30 --incidents
python -B ordinary_campaigns.py --seed 1723 --policy recovery --days 90 --resume-every 1
python -B ordinary_campaigns.py --seed 1901 --policy refusal --days 90 --resume-every 1
```

| Campaign | Actual final state | Runtime |
| --- | --- | --- |
| 1291/stability/365 | 13 disk checkpoints; cash $1,556, arrears $0, employment 6, 35 completed kits, 17 supply cancellations, support unused. | 217.521s |
| 1543/recovery/365 | 13 checkpoints; cash $1,434, arrears $0, employment 6, 33 kits completed, 17 cancelled, one expired, one accepted delivery missed; support repaid. | 214.714s |
| 1723/recovery/90 | **90 daily checkpoints**; cash $296, arrears $0, employment 6, seven kits completed, one missed commitment, one $20 advance repaid. | 24.242s |
| 1901/refusal/90 | **90 daily checkpoints**; cash $0, arrears $20, employment/Tess 0; nine allocations declined, support declined with no debt. | 16.282s |

All four end with heat 0, no case/arrest and no criminal employment. Year runs
enable both incidents/M019 but never discover or participate; both incidents
progress independently. Short runs adopt neither incident. After a separate
90-day refusal replay, **one actual lawful shift** followed by home payment
cleared the $20 shortfall. No faction/crime, permanent loss of home or impossible
qualification was required to recover.

| Campaign | Full sorted compact-JSON world SHA-256 |
| --- | --- |
| 1291/stability/365 | `91a6017bac16f684ff84fecb5c5bc8c08bef2638e3dc4dabfc66ae6fc4d8458c` |
| 1543/recovery/365 | `e0e2771112ffa734b02dfd84d9420d70b8e293e7919b82fd9855b5a512cd5eb2` |
| 1723/recovery/90 | `9efbfa43bea868277f45af572645b598a3a0fdb1fc5cfcf09d30dda86beff3b9` |
| 1901/refusal/90 | `0deac28742b158506653742774f1644dd87c31d601e120a7808e6c04d1023ae8` |

A further 2333/negotiation/30/daily-resume probe in separate processes with
`PYTHONHASHSEED=3` and `313`, and a run reversing faction/people/contact dictionary
insertion order, all produced
`cbc0591ac8bfb13243fe865c4cec89ac9a21c560a5bdd6ce5e80073cde225b26`.

### Independently re-executed six historical fingerprints

Executed all four historical commands already printed in Mission 026's section
on the repaired source. Night/notice resumed 13 times/seed; mobility 30 times/seed.

| Campaign | Unchanged SHA-256 | Actual runtime |
| --- | --- | --- |
| Night Shift 17 | `6bcad488e55c01db05cc5e83d6e1f370ede3bd7780bb0cdee5bb8813327566ed` | 69.239s |
| Night Shift 42 | `578b6ae0543e40242b088e37700dfe64be28fbebc7a5f8f043873b7dcf1fff9f` | 58.881s |
| Wrong Notice 73/help | `593386231e6df47bac4d9c279a10bd011b67d0f6a08e63d6f56ab3c68245bc09` | 79.724s |
| Wrong Notice 191/unchecked | `ca5996dd6800bdd349f082b02ee67ff85d418673311d613ed9a2e51e806bbcae` | 77.978s |
| Mobility 17 | `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3` | 6.591s |
| Mobility 42 | `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d` | 7.221s |

No original fixture, golden hash, content pin or valid event outcome was edited.

### Five real CLI audit scenarios — seed 23

Executed actual `python -B gameplay.py --seed 23 --save <temporary-path>` sessions,
then separate `--load --save <same-path>` processes with stdin, saved EOF
interruptions, public choices/home reports and a deliberate closed-offer retry.
No Python state edits, poor-start preset, criminal work or incident adoption.

Common start: `settle_in`, `wait`, `enable_ordinary`, `wait`, `ordinary` (day 2).
For worker paths, travel p032, take the actual day-2 lawful crossroads shift,
and return home. Every intentional failed retry was followed by save/load and
an exact whole-world comparison; none changed state.

| Path | Actual choices and persistent differences |
| --- | --- |
| A Stable worker | Complete batch 0 on day 3, prepay with `pay_room`, then advance to day 14. Cash $24, arrears $0, employment/Tess 2; completed, unnegotiated kit and real prepayment/credit history. |
| B Negotiator | Save at day 6 after requesting later delivery; resume into day 7, incur the real room charge while work is pending, then deliver. Day 14 cash/standing equal A, but negotiated date/wage and due-payment history differ. The future obligation was real, not a flavor label. |
| C Support recipient | No wages until the day-14 $20 shortfall; borrow the actual support advance and pay the room. Day 15 opening shift funds repayment. Cash $0, arrears $0, employment 1, Tess 2, one repaid advance. |
| D Recovery | Reserve day 3, miss its deadline day 6. Exhaust initial money through real room reviews, borrow day 21, and miss repayment day 28. Actual day-29/day-30 shifts repay the loan and clear room arrears. Ends cash $10, arrears $0, employment/Tess 2, missed accepted kit and overdue/repaid loan history retained. |
| E Refusal | Decline support day 2 and kit day 3. Day 14 cash $0, arrears $20, employment/Tess 0, no loan debt. A further actual CLI continuation works day 15 and clears the shortfall at home. |

All have zero heat/cases/arrest and no faction affiliation. A and B may converge
financially while their obligations/history differ; no claim of five exclusive
career endings is made. C/D retain the closed advance and cannot borrow again.
E's change of direction needs no criminal participation or narrative forgiveness.

| CLI checkpoint | Full-world SHA-256 |
| --- | --- |
| A/day 14 | `1248ba444de838b99a3577d1299914fbf931c99aa7df0b10c4fc3e29c7ed1789` |
| B/day 14 | `4c8242de66215b7df799ab5587eb8b6bf38771c810325916722b17020c0422a8` |
| C/day 15 | `408ff9d62d6ab41d54882cd5b6b81695130d350beec733816d6690bff47ca898` |
| D/day 30 | `3cf23d7cc975e59e6e71d9d458eca7240164e97ccc3fe8e63f8b67dc9387ce21` |
| E/day 14, before lawful recovery continuation | `ae8730769d90f9413b1f0be632c813753a304b872707831b57c0cd7af467bb97` |

### Persistence, adoption and institutional isolation

Generated genuine **pre-audit** files with original executables in disposable
`git archive` checkouts, not the repaired producer. Each file underwent 20
new-executable load/resaves with **byte-identical output**:

| Source executable / state | Original file SHA-256 |
| --- | --- |
| cd20633 / pending reservation and owed support | `65d56aef484ef5a8b1cc32687506ca055120dda7c13b2431ba608734a2811fdb` |
| cd20633 / completed work and repaid support | `947cb591daa35d70aa922dcc429afc4e0bba434132e569f69073e01b71018244` |
| cd20633 / actual earlier promise/reference and qualified audit | `ffec58d4e62fb8b9aa509b78bcd27cc9665c5f9f0b96ebeafb4cfd52a89bb267` |
| 6682019 / genuine M019 documented notice/copy | `4a3cfb4b1b3a066244880f24d068c5929b748dd99c08039d19192169b3e541ea` |

The M019 file remained without ordinary state until explicit adoption, which
preserved its player, old life, institution and navigation records and started
employment at zero. Existing historical-fixture tests also passed in full;
early unversioned fixtures retain their documented additive migrations, not a
claim of byte identity before migration.

An actual writer with a real loan **and** reserved work was killed just before
primary replacement, after backup publication. Primary and `.bak` retained the
old valid bytes, debt and reservation. Restart published the candidate's one
completed wage; 25 additional load/resaves retained its owed $20 debt. Paid-work
and second-advance retries rejected with world/RNG unchanged. One staged orphan
remained until disposable-directory cleanup. No original career was overwritten.

Thirty matched days with/without actual ordinary work/support produced exactly
equal private institutional states despite different wages, loans and arrears.
An actual loan followed by civilian submission, follow-up, documentary copy and
correction left M020 wages, housing and loan state unchanged. The initial probe
incorrectly assumed support was available on day 12; the engine correctly
rejected it. Reading actual availability yielded day 13, and valid report/copy/
correction actions then passed. Read-only institutional views remained detached
and preserved world/RNG. No police receipt, rumor or guilt was inferred from
work, debt or personal standing.

Fifty exact repetitions of the old seed-3 stale-letter CLI scenario produced
only its two intended errors (premature work and wrong location). No new
unexpected baseline error or `WinError 32` reproduced anywhere in this audit;
no speculative persistence/platform rewrite was made. Runtimes are actual
observations under parallel testing, not controlled performance benchmarks.

### Final assessment, remaining limits and exact audit inventory

- **P0:** none confirmed.
- **P1:** four demonstrated defect groups above repaired; no confirmed unresolved
  P1 in the exercised, documented boundary. Normal/replayed duplicate wages,
  support, funded review credit and repayment cannot survive these checks.
- **P2:** full-history copying/replay cost; authored funding/availability; simple
  negotiation and one cooperative arrangement. Grace/capped arrears are deliberately
  forgiving and currently impose limited housing pressure; this audit neither
  trivialized rent further nor added eviction or punitive locks. The previous
  intermittent platform symptom remains unroot-caused, although not reproduced.
  Legacy net financial authorities outside the known closed handlers are not a
  universal replay of every economy/legal/NPC effect. Coordinated rewriting of
  those facts or a whole career is not authenticated; no tamper-proof guarantee.

**Ready for draft PR publication review**, with these P2 limits disclosed. Ordinary
lawful survival/recovery, refusal, exactly-once effects, pending commitments,
explicit adoption, historical compatibility, three actions, eighteen TU and M019
information separation remain intact. No push, PR, merge, Court gameplay,
early clue or M021 work was performed; no new GitHub CI result is claimed.

Exactly **six audit files**: `ordinary_state.py`, `daily_life_state.py`,
`tests/test_m020_acceptance.py`, this report,
`docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md`, and `PROJECT_STATE.md`.
Combined master-to-audited-M020 scope is **20 files**: the original 19 plus one
new audit test file. Existing tests, fixtures, producers, rules/content pins,
schemas, persistence, navigation, incidents, institutions and dependencies are
unchanged. Final audit commit identity is supplied in the Mission 027 delivery.

Final scope/static verification found exactly these six audit files. All three
changed Python files parse, Markdown fences balance and all relative file links
resolve; `git diff --check` passes. No dependency or external validator was
installed. A final fetch still places origin/master at `6682019`; prior local
branches/master and the unpublished M020 source history are preserved.
