# M018 — The Wrong Notice: implementation and executed validation

Mission 019, November 4, 2026. Local implementation only; no push, PR or merge.
This report distinguishes executed evidence from future design proposals.

## Verified baseline and dependency

The initial worktree was clean on `feature/m017b-provenance-integrity`, HEAD
`6e6779341351b39bdbaeed383f7c005efd79aee4`. `git fetch origin` and
`gh pr view 17 --json number,state,baseRefName,headRefName,mergeCommit,mergedAt,url`
verified [PR #17](https://github.com/CapuchaRojo/gotham-underworld/pull/17) is
**MERGED**, but into **`audit/m017-independent-acceptance`, not master**.
Its merge commit is `14bfc5084b1f9f50fb305a69ac2f6c64f0412739`, with parents
`aaacba012dee705eac39f56009f3252d496c3f16` and
`6e6779341351b39bdbaeed383f7c005efd79aee4`.
`git diff --exit-code 6e6779341351b39bdbaeed383f7c005efd79aee4 14bfc5084b1f9f50fb305a69ac2f6c64f0412739`
confirmed identical source trees.

Created separate `feature/m018-wrong-notice` from that verified integration
commit. Existing branch tips were preserved. A final fetch still found remote
master at `43d81973e03c63d0ac8b4c759b5dd95b9e884c6d`. The audit/provenance
history is **not yet on master**. No attempt was made to merge it or change
either prior PR. A future PR against master must explicitly account for this
ancestry; do not imply that M018's baseline was master or that syncing is merging.

## Implemented boundaries

- Two explicit adapter bindings share `incident_lifecycle`, dispatch, effect
  publication, service commands and replay validation. Domain facts/rules remain
  in `world_incidents` and `wrong_notice`; no universal quest language or framework.
- Night Shift keeps its existing marker/slot, definition, IDs, content pin,
  event/receipt shape, costs and rewards. Old `enable_incidents` still enables
  only Night Shift. Generic `enable_incident(definition_id)` adopts only its
  requested definition after daily life activates.
- Wrong Notice uses optional `notice_version: 1` / `wrong_notice`, its own pin,
  stable enrollment/instance/stage/transmission/effect IDs and one bounded episode.
  No outer save version, atlas, mobility, legal or old content changes.
- Deterministic occurrence and delivery facts precede participation. Both
  incidents progress after daily life even undiscovered, expire/resolve once,
  and stop ticking after their final windows close.
- Original local contacts Nora Reed and Sam Ortega delegate standing/memories
  to daily life. Cash remains `player.cash`; the existing ledger records actual
  changes. There is no duplicate payout or second reputation authority.
- Player mutation uses candidate-copy `execute_command`; read-only projections
  cannot change state/RNG or grant knowledge. Rejections leave the world intact.
  Three actions/day, 18 TU/day and existing mobility behavior remain unchanged.

The canonical [architecture](GOON_CONTENT_ARCHITECTURE.md),
[After Dark contract](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) and
[choice contract](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md) specify the adapter,
information, eligibility, timing and compatibility policies.

Wrong Notice pin:
`f90c10c7cb1b47cae8d83f402012d316bb93e117415e2c3193a8b6eb8d09abe8`.

## Information and meaningful outcomes

The obsolete board notice and Sam's handbill disagree. Neither source gives
the authenticated answer. Nora's later ledger establishes the actual day and
whether a standby vacancy exists. Separate claims carry credibility/limitations;
transmissions name source, recipient, cause, day and command. The player learns
only actually observed sources. Authentic corrections cannot be overwritten
by later unchecked reports.

| Choice | Observable persistent consequence |
| --- | --- |
| Verify, notify desk and warn group | Three actions; tomorrow's board correction and an immediate warning only to Sam's group. Timely delivery to both prevents harm; no wages. Nora/Sam each +1. |
| Correct only the board | One audience remains wrong: partial success. Nora acknowledges signed help at her later board review. |
| Correct late | Earlier delivery-day harm remains recorded even after a valid correction. |
| Pass on unchecked date | Sam's group receives the actual false report. Independent reconciliation can cost Sam trust; Nora never learns that private conversation. |
| Verify and retract | Corrects original recipients; no bonus or erased prior harm. |
| Request lawful standby vacancy | Disclose the discrepancy but choose personal priority: Nora -1; no immediate money. One optional later action earns $5 once. No invented crime or police case. |
| Refuse, ignore or never discover | Distinct refused/ignored-known/missed-unknown aftermath; no promise penalty, lost housing, forced affiliation or blocked ordinary career. |

Independent resolution contains actual local observations by Nora and Sam,
their reports to the desk, and a final circular. It corrects the board/tenant
group only when delivered. It does not retroactively inform the player. Reading
the circular locally receives the aftermath; private automatic reactions stay
out of command/CLI events and contact summaries before then. The complete save
and detached debug snapshot intentionally retain audit truth.

## Executed automated checks

All 389 baseline tests remain unedited. New `tests/test_wrong_notice.py` has
**37 methods**. No skipped or disabled cases were added.

| Exact command | Result |
| --- | --- |
| `python -B -m unittest discover -s tests -q` | **426 passed**, 105.195s. |
| `python -B -m unittest discover -s tests -p 'test_wrong_notice.py' -q` | **37 passed**, 39.701s. |
| `python -B -m unittest discover -s tests -p 'test_*incident*.py' -q` | **53 passed**, 16.111s after shared dispatch extraction: original Night Shift and provenance tests. Also included in the final full suite. |

New coverage includes independent opt-in and generic legacy enrollment;
deterministic occurrence/independent resolution; contradictory bounded sources;
direct Sam discovery without a Tess reference; no early verification; targeted
and delayed correction; success/partial/late/failure/retraction/refusal/missed
outcomes; vacancy gating; duplicate pay and trust prevention; no invented crime;
historical source-backed discovery; malformed flags/state/history; reordered,
missing and duplicate sources; read-only/detached reports and fresh-process hash
seeds; wrong/cross-definition/expired commands; terminal idempotency; zero-cash
ordinary continuation; injected memory failure rollback; and disk-replacement
failure preserving the destination, recoverable backup, world and temporary-file
cleanup. Both adapters coexist in saved careers.

The long regression executes two **90-day** campaigns (73/help and 191/unchecked)
with **90 real daily disk save/reloads each**, compares whole worlds every day,
and asserts success/failure, Night Shift refusal, zero notice compensation and
no arrears. This runs inside both focused and full suite commands above.

## Long campaigns and exact replay evidence

`notice_campaigns.py` explicitly adopts both incidents and plays through public
reports/service commands. It refuses Night Shift while independently responding
to the notice. It continues ordinary available lawful work; it does not use
private truth to select corrections or force vacancies. Each resumed world is
compared with its uninterrupted counterpart after every day, not just at the end.

| Exact command | Actual result |
| --- | --- |
| `python -B notice_campaigns.py --days 365 --seed 73 --mode help --resume-every 30` | Success; Night Shift refused; 13 disk resumes; $0 notice compensation; cash $1,620; arrears $0; 76.317s. |
| `python -B notice_campaigns.py --days 365 --seed 191 --mode unchecked --resume-every 30` | Failed unchecked claim; Night Shift refused; 13 disk resumes; $0 notice compensation; cash $1,620; arrears $0; 75.068s. |
| `python -B notice_campaigns.py --days 30 --seed 73 --mode reserve --resume-every 1` | Selfish reservation; 30 daily resumes; exactly $5 notice compensation; cash $185; arrears $0; 4.333s. |
| `python -B notice_campaigns.py --days 30 --seed 191 --mode missed --resume-every 1` | Missed unknown; 30 daily resumes; $0 notice compensation; cash $180; arrears $0; 3.347s. |

| Campaign | Sorted-JSON full-world SHA-256 |
| --- | --- |
| Two incidents, 73/help/365 | `593386231e6df47bac4d9c279a10bd011b67d0f6a08e63d6f56ab3c68245bc09` |
| Two incidents, 191/unchecked/365 | `ca5996dd6800bdd349f082b02ee67ff85d418673311d613ed9a2e51e806bbcae` |
| Two incidents, 73/reserve/30 | `1116a33bc22e3980d79c8a33b49dfc95bab4278abed6d1e5f4f611c16e8e9969` |
| Two incidents, 191/missed/30 | `5c2d7dbd3b25abaff2b61c3b13b78739422c862acccb21ebbff12c9eca21f49a` |

Original runners were executed to check historical behavior:

```text
python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1
python -B incident_campaigns.py --days 365 --seeds 17 42 --resume-every 30
```

All four exact pre-M018 hashes match, with 30 daily resumes per mobility seed
and 13 checkpoints per Night Shift seed. Final-code repeat timings were
6.249s / 6.319s for mobility and 58.990s / 56.531s for Night Shift:

| Campaign | Unchanged SHA-256 |
| --- | --- |
| Mobility 17 | `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3` |
| Mobility 42 | `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d` |
| Night Shift 17 | `6bcad488e55c01db05cc5e83d6e1f370ede3bd7780bb0cdee5bb8813327566ed` |
| Night Shift 42 | `578b6ae0543e40242b088e37700dfe64be28fbebc7a5f8f043873b7dcf1fff9f` |

### Historical-save compatibility

The 15 historical fixtures in `tests/fixtures` / `tests/mobility_fixtures` load
and advance without auto-adopting Wrong Notice. Valid actual M017 public/contact
saves captured before M017-B were separately loaded and written to different
temporary files, matching their original **bytes**, not just selected fields:

- `public.json`: `c10c4bf18e4c6e41fd97150de6661c336333842d9e5197d3d2544444e249f3ef`.
- `contact.json`: `a5aead0e3e5fc9de5f3185f8e263dbc5a614561d6542d0cef5accff489e6bb36`.

The exact original forged file still rejects under
`incidents.discovery.provenance`: historical location mismatch. Originals in
the prior report's temporary evidence directory were not modified. New Notice
saves round-trip at every stage. Compatibility is old-to-new; playing an adopted
Notice career with an older executable is unsupported.

## Actual CLI playthroughs

A Python here-string invoked real `subprocess.run([sys.executable, '-B',
'gameplay.py', ...], input=..., text=True, capture_output=True, check=True)`;
no mocked input or reducer-only substitute. Each run had a fresh temp save,
EOF after an explicit save on day 3, a separate `--load` retry process, and
a separate `--load` continuation to day 8. All six subprocesses exited **0**.
The one deliberately repeated response was rejected; its resulting save equaled
the checkpoint world exactly, including command sequence. No other command failed.

Reproduction, seed 73, fresh day 0:

```text
settle_in
wait
enable_incident goon.incident.wrong_notice.v1
wait
travel goon.poi.p032 walk
discover_incident goon.incident.wrong_notice.v1.enrollment.1.notice public_notice
wait
travel goon.neighborhood.n13 walk
incident_choose goon.incident.wrong_notice.v1.enrollment.1.notice verify ledger
incident_choose goon.incident.wrong_notice.v1.enrollment.1.notice response notify_desk
incident_choose goon.incident.wrong_notice.v1.enrollment.1.notice repair warn_group
save
```

EOF, then resume with `python -B gameplay.py --load --save <same-temp-path>`.
Attempt `response notify_desk` again to verify rejection. Advance five days to
day 8; inspect incidents/contacts/events before reading, then use
`incident_choose <id> aftermath read`, inspect again and `quit`.
Actual outcome: **success**, Nora +1, Sam +1, $0 incident money, cash $10 after
the existing day-7 $30 room charge; 244 total stdout lines across the processes.

The seed-191 alternative replaced verify/notify/warn with `response repeat_notice`.
Actual outcome: **failed**, Nora 0, Sam -1, $0 incident money, cash $10; 237
stdout lines. The negative reaction did **not** appear in events/contact output
before the final circular was read. Those day-8 reads changed knowledge, not
allowances, wages, history settlement or ordinary work access.

## Review findings and limitations

**P0/P1:** no unresolved defect observed in the exercised scope. During review,
private automatic reactions were found to leak through generic event/contact
views; player projections were corrected before delivery and regression-tested.

**Integration prerequisite:** remote master does not contain the audited
M017-B integration. Future PR review must address the verified ancestry above.
This local mission neither promotes it nor authorizes a merge.

**P2 / bounded design limits:**

- One episode per definition per career; no repeatable event scheduler or global
  rumor/NPC network. Source beliefs are three abstract local audiences.
- Consequences are information, bounded contact standing and one optional shift.
  No simulated resident inventory, long business closure, prosecution or faction
  resource transfer. This is intentionally a second distinct event path.
- Verification is a reliable authored ledger, not an investigative deduction
  puzzle. Only timing/vacancy and choices vary; repeating fresh campaigns will
  eventually feel familiar. Daily-life work remains a repetitive source of money;
  the incident adds no upgrade timers, real-time waiting or monetization.
- Receiving the final review has a finite local window. Missing it leaves the
  player journal incomplete; it does not block ordinary survival or careers.
- Save validation proves consistency with recorded sources, not authenticity
  against coordinated rewriting of the entire save. Existing M017-B limitations
  on independently reconstructing non-discovery legal/access contexts remain.
- Full candidate copying and repeated history replay scale with career length.
  Measured long campaigns pass; no performance redesign or history compaction
  is included. Debug snapshots are intentionally not player-knowledge projections.

The smallest next step is independent M018 acceptance review and an explicitly
approved integration plan, not more event content. No M019, rogue gameplay,
Bat-Family behavior, global clock, assets or dependencies were implemented.

## Exact changed-file inventory

| Files | Purpose |
| --- | --- |
| `incident_lifecycle.py`, `incident_dispatch.py` (new) | Shared bounded lifecycle, explicit ownership/dispatch, delegated effects and player visibility. |
| `world_incidents.py`, `incident_state.py` | Preserve legacy adapter behavior; shared replay and per-definition provenance/effect validation. |
| `wrong_notice.py`, `notice_content.py`, `content/wrong_notice_v1.json` (new) | Original second incident, pinned local content and validated definition. |
| `game_service.py`, `gameplay.py` | Generic opt-in, shared commands, two-incident inspection and player event projection. |
| `daily_life.py`, `daily_life_state.py` | Adopted contact/fact definitions, existing memory ownership, private-reaction projection. |
| `notice_campaigns.py`, `tests/test_wrong_notice.py` (new) | Public-command campaigns and 37 focused regressions. |
| `README.md`, `PROJECT_STATE.md` | Current baseline, commands, behavior and limitations. |
| `docs/GOON_CONTENT_ARCHITECTURE.md`, `docs/GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md`, `docs/GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md` | Canonical implemented adapter/source/choice contract. |
| `docs/M017_NIGHT_SHIFT_VALIDATION.md`, this new report | Preserve historical evidence and record M018 acceptance checks. |

Exactly 20 files. Existing tests, fixtures, rogue registry, navigation/mobility,
save writer, legal/economy rules, workflows and dependencies are unchanged.
No new GitHub CI result is claimed for this local branch.
Changed Python files parse, JSON definitions decode, Markdown fences balance,
and all **200 relative file links** in the seven changed Markdown documents
resolve. `git diff --check` passed; no Markdown lint dependency was installed.
