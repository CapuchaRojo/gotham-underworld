# M020 Ordinary Gotham — implementation and validation

Mission 026 authorizes local implementation, testing and commits only. No push,
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
