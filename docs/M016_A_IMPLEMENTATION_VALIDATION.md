# M016-A implementation and validation — Mission 013

**Preservation update — Mission 014:** the independent local re-verification
below supersedes the earlier uncommitted delivery status. The implementation
and associated documentation are being preserved in a focused local commit;
the exact commit is available in Git history and the Mission 014 delivery report.
No push, new PR or merge is authorized. Earlier Mission 013 records remain intact.

## Delivery state

November 4, 2026. Verified baseline and current uncommitted HEAD:
`3251381177bf11c0b07cd940329ebd0be3a7bb52`. Implementation branch:
`feature/m016a-mobility-pilot`, created from that exact baseline. The three
uncommitted M016 design drafts were preserved in place and copied to a separate
temporary backup before implementation. Their historical proposals remain in
the updated documents; new implementation sections identify what runs now.

[PR #15](https://github.com/CapuchaRojo/gotham-underworld/pull/15) remains OPEN,
head `feature/m015-living-gotham` at the same baseline commit. It was not modified,
merged or rebased. No commit, push, new PR or dependency installation was made.
Existing CI success belongs to the M015 head; no new GitHub CI run is claimed
for this uncommitted local slice. Broader M016 is incomplete.

## Implemented contract and source evidence

| Boundary | Implemented behavior |
| --- | --- |
| [Content](../mobility_content.py) / [overlay](../content/mobility_station_pilot_v1.json) | Separately pinned two-station overlay validated against the unchanged atlas; public loader copies, canonical station ordering, contiguous directed four-edge rail alignment and positive price validation. |
| [Adoption](../mobility.py#L61) | Explicit once-only enable command, no resource grant, paired nav2/mobility1, pending rules1 until actual service wait; checkpoint before the existing navigation reset, activation afterward before life. |
| [Routing and preview](../mobility.py#L160) | Stable resource-aware labels, station gates, no legacy rail in active graph, physical walking approaches, free bus/ferry, bounded search, projected paid/free return and known-state quote token. |
| [Execution](../mobility.py#L321) | Service candidate revalidates location/custody/access/TU/cash/pins/known token and actual closures; one safe actual prefix, one fare, one result and request receipt. Duplicate accepted request rejects without effects. |
| [History validation](../mobility_state.py) / [dispatch](../navigation.py#L29) | Original v1 validator retained and applied to unchanged history at checkpoint; separate schema2 validation reconstructs typed costs/legs, continuity, receipt/command identities and public observation sources. |
| [Service](../game_service.py) / [CLI](../gameplay.py) | Existing atomic root transaction, three actions/day and 18 TU/day retained; opted-in candidates validated before root commit. Reuse route/travel, add status/adopt/receipt. |
| Persistence / daily life | Original persistence and life reducers unchanged. Fare debits player.cash once; existing life observer records its actual balance change. Stage/fsync/backup/final replacement failures tested. |

### Schemas and pins

- Outer `save_version` stays1. Default new careers and old saves remain nav1.
- Explicit adoption requires paired `navigation_version: 2`, `mobility_version: 1`.
  Mobility rules/overlay versions are1. Pending nav routing is rules1; active is2.
  No mutable vehicle system exists: reserved vehicle collections must remain empty.
- `mobility_requested` / `mobility_activated` events use schema1, real request/
  command/day identities and the legacy pre-reset checkpoint/activation budget.
- Old `travel` schema1 events remain exact original JSON values and keep base1
  interpretation, including travel while adoption is pending. New `travel`
  schema2 records graph pin, actual endpoints, typed legs, resources before/cost/
  after, discoveries, charge IDs, request ID and parent journey command ID.
- Receipt indexes are checked projections of accepted effects, not a second
  wallet. Global duplicate command IDs are rejected before building domain indexes.
- Base atlas SHA-256 remains
  `14a38c5376989351d83bf90ed172c557a3dbf13c1323a115d2c2144f5136860a`.
  Overlay SHA-256 is
  `d59fe323290fd1216d8b5e1ffdcde5924b123cedc0404ce22215d538779ec7ee`.
- Missing/mismatched required content fails clearly. Existing binaries reject
  nav2 explicitly; they do not silently ignore mobility. New engine reads old
  fixtures without adopting, refreshing resources or replaying events.

Empty historical navigation histories retain the state accepted by the old
validator. Current home entitlement is not used to invent the prior location:
historical players can accept M015 housing later. No assumption of full event
sourcing or cryptographic anti-cheat is added to the local JSON game.

### Station scope and transport decision

Public p039 Highbridge Metro Stop and p071 South Gate Subway Stop receive
internal platform/gate definitions. Ride alignment:
`local.r03.05` n17→n18 (1), `e06` n18→n23 (2), `local.r04.04` n23→n22 (1),
`e08` n22→n30 (2). These are exact existing atlas corridor IDs under `goon.edge.`;
reverse service reverses directions. The overlay adds an original proposed
service identity, not a claim that old rail already enforced monorail stations.

Frontage→frontage cost is **1 boarding + 6 ride = 7 TU and $2**, with zero-TU
gates/alighting. Actual street approach/onward movement is extra. Home→p039
walking approach4 makes explicit home→p071 monorail11 TU; a separate free bus
approach3 is also available. Current station bus8/$0 and walk18/$0 remain viable.
Paid round trip14/$4 versus free bus16/$0 creates a resource choice without XP,
reward farming, real-time waiting or a vehicle purchase.

Policy C is applied only after adoption. The old atlas rail definitions remain;
legacy careers still use them, active rules2 cannot bypass station gates with
the old travel command. CLI route/travel dispatch transparently to the appropriate
version. API return target defaults to origin for existing route semantics;
explicit return_to can select home. Outbound caps limit this transaction only;
return uses the actual remaining budget and cash, with a free alternative shown.

All four segments are checked at departure before the atomic pilot ride. Unknown
closure discovered after approach charges that real prefix only, ending at the
frontage with no train fare; a first departure block at the frontage costs0.
Known outages affect planning. No intermediate stop or random disruption system
was invented. Observed line status does not expose private closure provenance
through the public report or quote token.

## Exact files changed or added

| Files | Purpose |
| --- | --- |
| `navigation.py`, `game_service.py`, `gameplay.py` | Narrow version dispatch, existing day/reset seam, service registration/candidate validation and CLI. |
| `mobility.py`, `mobility_state.py`, `mobility_content.py` | Reducers/read models, strict mixed-history validation, pinned local overlay loader. |
| `content/mobility_station_pilot_v1.json` | Two stations, one service and four underlying corridor references. |
| `mobility_campaigns.py` | Reproducible offline command/replay/resume evidence utility, not an extra simulation. |
| `tests/test_mobility_pilot.py`, `tests/test_mobility_compatibility.py` | 49 new focused regression methods, including parameterized malformed and failure cases. |
| `tests/mobility_fixtures/m015/career.json`, `tests/mobility_fixtures/m015/README.md` | Frozen M015 fixture/provenance generated by baseline modules in isolation; kept outside legacy pre-life fixture discovery. |
| `README.md`, `PROJECT_STATE.md` | Exact commands, versions, prices, scope and status. |
| `docs/M016_MOBILITY_ARCHITECTURE.md`, `docs/M016_MOBILITY_ACCEPTANCE_MATRIX.md`, `docs/M016_INTEGRATION_RISK_REGISTER.md` | Preserve/hardened design history with current implementation and coverage/risk disposition. |
| `docs/M016_A_IMPLEMENTATION_VALIDATION.md` | This evidence report. |

No atlas, existing test, persistence reducer, legal/job/faction rule, dependency
or workflow was changed. The existing career validator hook is reused unchanged.

## Executed tests and corrected findings

| Executed command / scope | Actual result |
| --- | --- |
| Before changes: `python -B -m unittest discover -s tests -q` | 283 passed, 46.289s. |
| Focused discover `python -B -m unittest discover -s tests -p 'test_mobility*.py' -q` | Corrected focused runs passed; the last standalone focused run before the final three cases had46 methods, 5.732s. All49 new methods are included in the final full run. |
| Final `python -B -m unittest discover -s tests -q` | **332 passed, 74.446s; zero failures/errors**: all283 original methods plus49 new. Concurrent campaign work affects elapsed time. |
| Independent processes, PYTHONHASHSEED0/42 | Test compares identical canonical world hashes after adoption and actual paid travel. Global RNG/read isolation and reversed lookup ordering also pass. |
| Frozen historical fixtures and disk checks | All old fixture generations, genuine M014 plus separately generated M015 data, pending/active/interrupted careers and later historical housing pass. Bad mixed data rejected by disk loader; fsync/backup/final-replace failures preserve recoverability and committed memory. |

Initial runs were intentionally allowed to fail: the first42-method focused run
had four failures and one error, exposing the closed-line paid-circuit planner
case, an incorrect10-TU approach expectation (actual11) and missing ferry gate
permission in a fixture. The first327-method full run had one failure because
the new active-life M015 fixture was placed in a collection deliberately reserved
for pre-life saves. It was moved to a separate collection without changing any
old test. These failures are corrected; none remains in the final332-test run.

Further review fixes are regression-covered: None transition flags cannot enter
boarding arithmetic; caps do not erase actual return funds/TU; later housing
does not reinterpret an empty legacy history; profile/boarding/loop invariants
are validated; private source IDs/causes do not enter public quote hashes.
Candidate exceptions discard all effects. No test claim is based only on the
design matrix: vehicle, multi-line and broader M016 cases remain unimplemented.

## Campaign evidence

Executed twice during implementation (before and after validator definition
reuse optimization):

```text
python -B mobility_campaigns.py --days 365 --seeds 17 42 --resume-every 30
```

Each seed has two worlds: uninterrupted versus periodic real save/load. Both
take two actual journeys per day using fastest affordable travel, advance once,
and compare full world equality after every journey and day. Existing M015 life
is enrolled. Thirteen resumed checkpoints per campaign include the final day.

| Seed / days | Actual journey outcomes | Paid boardings / total fare | Final cash / arrears / home | Canonical world SHA-256 |
| --- | ---: | --- | --- | --- |
| 17 /365 | 730 | 12 /$24 | $0 /$14 /p031 retained | `8c7b15c3c866413e3f32e9c5544112f26791ec7edc540a9e06b60879afe56bde` |
| 42 /365 | 730 | 12 /$24 | $0 /$14 /p031 retained | `704f4adbd438a587ae1fed8ca68b56f1148b6914fc479d9e500197f21e55a3c1` |

Repeated hashes matched exactly across the optimization. Second-run elapsed
times were206.386s and240.284s respectively; these paired, validating stress
runs are not route latency benchmarks. The final location is p039, day366.
Once fare funds ran out the planner selected free bus; no negative cash, allowance
refresh, duplicate charge or lost home occurred. The remaining $14 obligation
is existing M015 hardship behavior, not new transport debt or a fare loan.

After the final housing/private-provenance fixes, a fresh final-code replay also
ran both seeds with disk save/resume **every day**:

```text
python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1
```

Each produced60 outcomes,30 resumed checkpoints,12 paid boardings/$24, then free
bus continuation with cash0, arrears14 and home p031. Complete worlds matched
after every command/day. No four-distinct-seed or1,000-day mobility campaign is
claimed; those larger-matrix goals remain future gates.

| Final-code daily-resume seed | Actual elapsed | Canonical day31 SHA-256 |
| --- | ---: | --- |
| 17 | 5.953s | `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3` |
| 42 | 6.565s | `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d` |

Final structural documentation checks passed for six changed Markdown files:
149 links,41 source-line bounds and six parsed JSON examples, zero errors.
Historical M014/M015 fixtures also loaded successfully with the optional overlay
path deliberately unavailable; unadopted careers do not depend on new content.
`git diff --check` passed, and the pinned atlas, persistence, life, career and
existing test files were verified unchanged.

## Scripted CLI scenario and gameplay assessment

The actual CLI regression supplies `mobility`, `travel p039`, `adopt_mobility`,
`wait`, `route p071 monorail`, `travel p071 monorail`, `travel p039 bus`, `quit`.
The quit save is reopened through the real loader and exactly matches memory.
Station-day result:15 TU, $2 spent (cash38), zero actions spent and no implicit
day advancement. Both preview and rejection reasons are visible in the CLI.

Player decisions: buy1 TU of inter-station speed for$2, preserve cash with free
bus, select a safe partial/next-day plan after closure, or decline an outbound
whose return does not fit. These change cash, spent TU, recorded history and
disruption knowledge; an explicit wait can change existing opportunities/promises.
The tests also execute the remote7-TU/$0 state and next-day free bus recovery.

Variety is currently modest: asset positioning, personalities and schedules are
not implemented. The stress policy repeats a commute and deliberately performs
no work; it demonstrates reliability, not a fun365-day campaign. There is no
reward for commuting, fare refund loop or forced vehicle grind. Local lawful
work and room-support rules remain their existing opportunities, not new jobs.

## Remaining risks, limits and next slice

- **P0/P1: none confirmed in the tested pilot.** This is a local implementation
  for review, not a claim of exhaustive proof or a merged release.
- **P2:** full candidate/save validation and transaction copies scale with history;
  the two long paired runs show this cost. No p95/maximum route-time certification
  or1,000-journey persistence timing claim is made. Search has deterministic
  bounds and explicit failure, not unlimited citywide multi-service optimization.
- **P2:** only two stops, modest price/speed difference, no new incident generator,
  and conditional return knowledge. A quote is advisory, not a ticket reservation.
- Vehicles, cargo, theft, impound, physical Blackgate release, licensing, new
  schedules and full prologue remain outside this slice. Public UI should use
  public reports, not the existing full world-truth debug snapshot.

Recommended next step is human review of M016-A and its balance/performance
limits. A later portable-skateboard slice is the smallest next gameplay extension,
after its acquisition/surface/carrying contract is separately approved. Do not
start it here. There is no commit hash or PR URL for this local delivery because
no commit/new PR was made and pushing was not authorized.

## Mission 014 preservation and independent audit

Verified branch `feature/m016a-mobility-pilot`, initial HEAD
`3251381177bf11c0b07cd940329ebd0be3a7bb52`, and all18 working files listed above:
five tracked modifications and13 additions, including the three architecture
drafts. Every pre-audit file was copied with a SHA-256 manifest to a separate
temporary preservation directory before editing this report. No implementation
or test was discarded, replaced or changed during this audit.

Fresh executed checks:

| Command / review | Result |
| --- | --- |
| `python -B -m unittest discover -s tests -p 'test_mobility*.py' -q` | **49 passed, 6.454s**. |
| `python -B -m unittest discover -s tests -q` | **332 passed, 59.860s**, zero failures/errors. |
| `python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1` | Both passed with30 actual daily disk resumes,60 journey outcomes each; every command/day exactly matches uninterrupted play. Seed17 6.222s, seed42 6.512s. Both day31 hashes exactly match the Mission 013 table above. |
| Source and contract review | Mixed-version checkpoint/projection, receipts and charge reconstruction, pre-commit candidate validation, known-state quote projection, closure-prefix settlement and service-wait adoption agree with the stated pilot. Atlas/persistence/life/job/legal/faction rules remain unchanged. |
| PR #15 | OPEN, original head `3251381177bf11c0b07cd940329ebd0be3a7bb52`; no PR write, push, merge, rebase or force-push. |

**Disposition: no blocking P0/P1 confirmed; local preservation commit gate passes.**
This is an independent fresh review/execution, not a claim to repeat the full
365-day campaigns. Reported earlier365-day results are historical evidence.

**Confirmed P2 follow-up:** in [pending validation](../mobility_state.py#L87),
`navigation.rules_version == 1` and `journey_sequence == len(legacy)` use equality
before a v1 projection overwrites these fields. In a pending career with no
legacy trips, `rules_version: true` and `journey_sequence: false` are accepted
by `career_state.validate`. A read-only in-memory malformed-data probe reproduced
this; no normal player command creates it. Active rules and command/effect IDs
have separate integer checks. Add strict integer checks and malformed pending
disk regressions in the next reliability patch; no resource duplication,
save-loss or normal-gameplay failure was reproduced. The original implementation
is preserved unchanged rather than silently repairing it during this mission.

Existing P2 concerns remain: whole-history validation/copy cost, bounded route
search, two-station depth and future vehicle/release integration. The local
commit deliberately excludes the separate Rogue Encounters design proposal.

Staging exposed one cosmetic pre-existing warning that the earlier tracked-only
diff check did not see: an extra blank line at EOF in the newly added
`tests/test_mobility_compatibility.py`. It is retained to preserve the tested
source byte-for-byte; no test behavior or runtime file changed. This P3 formatting
warning does not block the local preservation commit or the unittest workflow.
