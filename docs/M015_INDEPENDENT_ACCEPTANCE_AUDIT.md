# M015 independent acceptance audit — Mission 010

November 4, 2026. PR [#15](https://github.com/CapuchaRojo/gotham-underworld/pull/15),
`feature/m015-living-gotham` into `master`. Inspected submission:
`94455aa4ad4ff6383fb1ddac18ef7e93550ec80f`. Fetched master and verified merge base:
`fa2f9f5bbf081bde080c6d8b2e46512487027c66`. Local and remote feature heads matched;
the initial working tree was clean. The submitted diff contained 19 files and
no dependency, workflow, navigation, legacy job/legal rule or faction-policy changes.

**Verdict:** the bounded M015 foundation is suitable for a user-authorized merge
after the corrected final head passes CI. No P0 or P1 issue remains in the audited
local implementation. The remaining P2/P3 limitations below concern gameplay depth,
presentation and balance. **This mission does not authorize merging or closing
PR #15. It must remain open and unmerged. M016 is not implemented.**

## Method and verified inventory

Read the state, README, both M015 contracts, roadmap and submitted validation report;
reviewed every new runtime/content/test file and existing service, CLI, career,
navigation, legal, economy, NPC, persistence and event integration. Re-executed
the baseline and documented campaigns, exercised all 21 options, injected specific
malformations, played additional decisions/seeds, compared fresh/resumed worlds,
and generated ten saves with the unmodified submission's modules in isolation.
Findings are confirmed reproductions, not deductions from a green test count.

| Status | Verified scope |
| --- | --- |
| Implemented | Explicit next-day enrollment; p031 home, $30 weekly contribution, prepayment/cash-limited settlement, receipts, bounded arrears and maintenance alternative. |
| Implemented | Eight contextual definitions/21 options, finite source windows, known/disabled/hidden presentation, stable IDs, current eligibility and shared three-action/18-TU boundaries. |
| Implemented | Local lawful shifts, existing-risk collection/courier referrals, one promise per week with one renegotiation, bounded observed memories/standing, and history-dependent later work. |
| Implemented | Separate local content, generic choice callbacks, detached service views, CLI letters, auditable cash and exactly-once effects, historical opt-in, validated saves and deterministic resume. |
| Partial integration | Work resolves immediately; there is no separate accepted/running employment contract, employer treasury, hourly appointment model, or NPC communication simulation. Roster conflicts are explicit source rules. |
| Design only | Full prologue, backgrounds, broader careers/recruitment, transport expansion, combat, health/hobbies, advanced schedules, DC actors and graphical frontend. Historical proposal wording is not evidence that these exist. |

## Architecture and state ownership

| Fact / boundary | Owner and verified interaction |
| --- | --- |
| Player mutation | [Service](../game_service.py#L70) validates command names/arguments/cost, executes a private candidate, then commits. CLI mutations all use it. Internal reducers remain callable by legacy tools; they are not alternative player interfaces. |
| Time/actions/travel | `simulation.advance` owns day/legacy feuds; [daily pipeline](../gameplay.py#L77) runs legal review, investigations, NPCs, economy/strategy/warfare, court, navigation and daily life. Service resets actions on real `wait`; navigation owns TU. Choices spend actions without implicit travel or day advancement. |
| Cash | `player.cash` is authoritative. [Ledger](../daily_life.py#L53) records actual cash; existing fines/support retain detailed legacy events and net ledger entries. Lawful wages are bounded external roster allocations, not a simulated business treasury. Criminal work calls `legal_engine.job` once and records its existing payout. |
| Housing | `daily_life.housing` owns due day, arrears and prepaid balance; receipts reconstruct these values and link real deductions. `navigation.home_id` owns home entitlement; the life reference must match it. No second spendable account is created. |
| Choices/promises | [Choice engine](../choice_engine.py#L35) owns one terminal selection per source. Promise records own deadlines/status; source selections and events are checked against them. Committed roster slots prevent overlapping work despite spare abstract actions. |
| Relationships/knowledge | Contact memories record observed interactions; standing is a bounded materialized value checked against that history. `_knows` derives referrals from those facts. Legacy faction NPCs remain separate. Tess can observe a missed appointment and her own shifts/account, not Cal's private crime or police evidence. |
| Public presentation | [Reports](../daily_life.py#L262) return detached data; formatting consumes no gameplay RNG or world mutation. Mixed-source menus are the player's planner. The full debug snapshot intentionally exposes world truth; future UI should use the narrower views. |
| Persistence/content | Career validation includes life invariants before I/O; existing atomic replacement/backup behavior remains. Both content fingerprints and outer/subsystem identifiers are unchanged. New careers also opt in explicitly; historical loading never invents rent, location, wages or contact history. |

World truth, contact observation, and presentation are distinct in this slice:
the legal resolver may create evidence; Cal records only his referral's result;
Tess records her own work/promises; public option predicates use those observations
and known player conditions. There are no hidden-intention or rumor mechanics to
claim as verified. The nested projection gap below was a real boundary issue in
allowed extension metadata, not proof of implemented secret NPC intentions.

## Confirmed findings and bounded corrections

| ID / severity | Reproduction on submitted head | Correction / evidence |
| --- | --- | --- |
| A1 — P1, fixed | Accept a day-1 promise, remove its pending record, and load the JSON. Validation accepted it; waiting past the deadline produced no broken promise. A week-1 promise could also reference week 0's invitation. | [Promise validation](../daily_life_state.py#L149) now requires exactly one matching record for every accepted invitation and its own source. Two disk-load regressions reject both corruptions. No normal command caused this omission; it was an insufficient malformed-save check. |
| A2 — P1, fixed | Renegotiate on day 2, then change `renegotiated` to false and due day to 3. Validation accepted a record contradicting its committed choice and day-4 follow-up. | [Flag check](../daily_life_state.py#L175) is now bidirectional against the source choice, preserving the actual selected deadline. A disk-load regression covers it. |
| A3 — P1, fixed | From active day 1, advance seven days with the existing clock-only reducer. This retained-marker career validates and saves at day 8. Its next service `wait` to day 9 opened week-1 offers already expiring on day 9, leaving a world that could not validate/save. | [Roster construction](../daily_life.py#L101) omits never-opened windows already past their deadline. The regression loads the original stale-marker save, waits, works an actually live offer and saves/resumes successfully. No backdated wage or fictional missed interaction is created. Ordinary daily campaigns are unchanged. |
| A4 — P2, fixed (small projection fix) | Add unknown `private_note` metadata to an existing observed memory. Validation correctly retains unknown fields, but `contact_report` exposed that extra key. The shipped templates do not currently create that field. | [Public memory projection](../daily_life.py#L340) now selects known public keys at both contact and memory levels. Save data remains unchanged; a regression checks isolation and preservation across disk resume. |

The five targeted pre-fix tests produced **four failures and one error**, while
the submitted 274 tests passed. After correction all nine audit tests pass.
No content migration, field reset, price/risk change or broad rewrite was needed.
Save validation is consistency checking, not a cryptographic anti-cheat system.

## Every contextual option

IDs below are definition/option IDs; instances retain week/cycle and source IDs.
All rows were actually selected in the new parameterized acceptance test, then
saved/resumed, rejected on repeat selection, and advanced to a valid continuation.
Common gates are: unselected/open source, actual day window, known predicates,
the displayed location, freedom for non-refusal effects, sufficient actions and
any shared roster slot. Hidden options have no public row or selectable API bypass.
The [content](../content/neighborhood_life_v1.json) pins exact terms; selection
[rechecks](../daily_life.py#L230) them rather than trusting a preview.

| Option | Motivation, prerequisite and cost | Actual result, future difference and continuation |
| --- | --- | --- |
| `opening_shift/work` | Safe cash; store, one action. | $20 and one observed Tess attendance. Can restore use of a known reference; later basic work remains available. |
| `opening_shift/decline` | Preserve time/avoid work; free. | Forgoes this wage, closes this allocation. No relationship reward/penalty; later offers remain. Same economic future as ignoring this offer. |
| `promise/promise` | Invest in Tess/cooperative; home, free commitment. | Pending dated promise, no money/standing reward. Later help, renegotiation or a remembered breach produces a different future. |
| `promise/decline` | Avoid an obligation honestly; free. | No promise or penalty. Refusal is persisted as a selection, not an NPC memory; future state matches an unaccepted expired invitation. |
| `cal_intro/ask` | Learn a risky work route; n13, free. | Cal observes disclosure; collection becomes known. No automatic affiliation/pay; player may still decline or choose lawful work. |
| `cal_intro/decline` | Avoid Cal's economy; free. | No disclosed terms or referral reward. A later week's introduction remains possible. |
| `crossroads/lawful` | Predictable income; store, one action. | $20/Tess attendance. Uses the shared morning; an accepted unkept promise later breaks. |
| `crossroads/collection` | More potential pay; known Cal terms, chosen faction, n13, one action. | Existing seeded job pays up to $60, creates heat and possible witness/case/faction effects. Cal records success/failure; successful work can reveal quieter work. No false guarantee of arrest or success. |
| `crossroads/help` | Keep a personal commitment; pending promise, home, one action. | No cash, promise kept, Tess +3 and known audit reference. Forfeits morning wages; later reference also needs current standing. |
| `crossroads/renegotiate` | Preserve a realistic promise; pending unmoved promise, home, free. | Moves its deadline once and opens day-4 help; closes this morning's source, forgoing its wages. Later shift/help still conflict. |
| `crossroads/withdraw` | Attend to other priorities; free. | No wage or free recovery. Source closes; a pending promise still expires. It is an agency exit, not another reward branch. |
| `midweek_shift/work` | Earn $20; store, one action. | Tess attendance; consumes the same morning as moved help. Missing that accepted favor remains consequential. |
| `midweek_shift/decline` | Retain time for the favor/other play; free. | No wage; moved help must still actually be performed. |
| `late_work/work` | Accessible reliable pay; store, one action. | $20/Tess attendance once. No reference required, including after low standing. |
| `late_work/audit` | Higher single-allocation pay; known reference, Tess standing >=2, store, two actions. | $25/Tess attendance; costs an extra action versus repair work. Uses this source once; can conflict with legal responses. |
| `late_work/courier` | Quieter known criminal work; observed Cal collection success, standing >=1, chosen faction, n13, one action. | Existing up-to-$25 courier resolution/failure/faction effects; no new collection case. Cal records the actual result. |
| `late_work/decline` | Pass on the remaining slot; free. | No cash/standing; next week's basic work remains. Economically equivalent to letting this allocation expire. |
| `rescheduled_help/help` | Keep the changed commitment; pending promise, home, one action. | Original promise kept/reference earned once, no money; blocks the conflicting midweek slot. |
| `rescheduled_help/decline` | Admit withdrawal from a promise; free. | Promise breaks immediately with Tess -2; future basic work and later promises allow recovery. This differs from declining an unaccepted invitation. |
| `room_review/help` | Reduce existing debt without cash; unpaid balance, home, one action. | Up to $10 actual arrears credit, no cash/friendship points. Only once per review; changed balance is rechecked. |
| `room_review/grace` | Retain basic housing without today's maintenance; free. | Arrears remain, home/work continue. Source closes, so this review's maintenance is forgone; the wording issue below remains. |

The stale-letter CLI regression previews a future menu before Cal's work is
known (B = decline), unlocks courier before selection, and verifies B still
declines. Resume without a displayed map rejects the letter; stable option IDs
remain usable subject to eligibility. Direct API checks reject disabled, expired,
detained, exhausted, moved-location and already-selected options without mutation.
Real CLI attempts at future/wrong-location work and repeated settlement also reject;
the saved checkpoint confirms no cash, action, TU or command-sequence change.
Repeated home inspection/formatting has no reward, RNG draw or allowance reset.

## Campaign and exploratory results

Required commands were independently run on the corrected implementation:

```powershell
python -B -m unittest discover -s tests -q
python -B daily_life_campaigns.py --days 7 --resume
python -B daily_life_campaigns.py --days 56
```

| Day-7 policy / seed | Cash / arrears | Legal state | Tess / Cal | Opportunity states | Persistent distinction |
| --- | --- | --- | --- | --- | --- |
| Lawful / 42 | $90 / $0 | No cases | 4 / 0 | 5 resolved, 1 expired | Four lawful shifts; no accepted promise. |
| Criminal / 3 | $110 / $0 | No cases | 0 / 4 | 6 resolved | Two referrals and chosen affiliation; includes existing $15 faction support. |
| Relationship / 17 | $75 / $0 | No cases | 6 / 0 | 5 resolved, 1 expired | Kept promise and used audit reference. |
| Hardship / 17 | $0 / $20 | One conviction | -2 / -1 | 7 resolved | Failed witnessed collection, broken promise, room maintenance credit; home retained. |
| Mixed / 42 | $70 / $0 | No cases | 1 / 0 | 5 resolved, 2 expired | Moved promise displaced by work, then broken once. |

Every path has prepaid balance zero and next room review day 14. Day-7 heat is
zero after the existing quiet-day cooling, not evidence that crime generated no
heat earlier. All five sorted-world fingerprints exactly match the submitted
[validation report](M015_VALIDATION_REPORT.md#five-actual-seven-day-paths).
Every daily disk resume was exactly equal; no payout, memory or selection repeated.

| Day-56 policy | Cash / arrears | Legal outcomes | Tess / Cal | Promise history |
| --- | --- | --- | --- | --- |
| Lawful | $440 / $0 | None | 10 / 0 | No accepted promises |
| Criminal | $440 / $0 | Three convictions | 0 / 10 | No accepted promises |
| Relationship | $320 / $0 | None | 10 / 0 | Eight kept |
| Hardship recovery | $330 / $0 | One conviction | 10 / -1 | One broken, then lawful work |
| Mixed | $280 / $0 | None | 8 / 0 | Eight moved, then broken |

All next reviews are day 63, with bounded standing/debt and no expired open offers.
The mixed history never supplies a kept-promise reference merely because standing
is positive. Records still distinguish its future from relationship-first play.

Additional `python -B -` service scenarios, beyond the runner:

- **Crime to lawful work:** seed 17, failed witnessed day-2 collection, then
  cooperate or contest immediately and work days 4/5/8/9/11/12. At day 14,
  cooperation ended with $70, one conviction and no arrears; contest ended with
  $80, dismissal and no arrears. Both had Tess 6/Cal -1, and next review day 21.
  Each uninterrupted run equaled its daily disk-resumed version. Legal mitigation
  uses real action/cash costs and does not require continued crime.
- **Inactivity:** fresh nonaffiliate waiting to day 56 had $0, $20 arrears, no cases,
  standing 0/0 and one live maintenance review (54 expired sources). Basic home
  and next week's lawful work remain. Waiting after the successful criminal week
  ended with $140/current housing, unchanged local contacts and 16 existing faction
  support payments; active work earned more, but passive affiliation remains generous.
- **Different seeds:** first-week criminal paths with 5/8/23/51/101 ended with
  cash $0/$70/$60/$70/$60; seeds 5/23/101 had convictions, and only seed 5 had
  $30 arrears. Each fresh run equaled daily resume. These small selected samples
  establish variation, not universal expected values or balance.

## Remaining P2/P3 observations and gameplay assessment

| Severity / status | Evidence and implication |
| --- | --- |
| P2, open — repeated rosters | [Pack](../content/neighborhood_life_v1.json) repeats the same weekly templates. Timing, promises, known work and legal risk change decisions; many repair offers still differ only in dates. A useful vertical slice, not sustained authored variety. |
| P2, open — generous hardship/passive support | Bounded arrears/basic access are intentional anti-softlock policy. Existing [faction support](../npc_actions.py#L35) can exceed the ongoing room cost without new work. Idle tests above quantify this; no new M015 rent/wage exploit or universal dominance was inferred. Balance changes need a separate contract. |
| P2, open — grace wording | [Room option](../content/neighborhood_life_v1.json#L86) says keep grace “for now”, but [terminal selection](../choice_engine.py#L35) also declines that review's maintenance. Later cash payment/next review remain possible, so it is not a softlock. Clarify the opportunity cost in a future compatible content revision. Pinned content was deliberately preserved here. |
| P2, open — historical CLI discovery | [Formatting](../life_presentation.py#L23) shows pending promises, five transactions and three contact memories; `opportunities` lists open sources. Older results persist in APIs and `choices <known-old-id>`, but discovering them through the CLI is awkward. This is presentation depth, not lost records. |
| P3 / scope — limited social/content model | Two observed-memory templates, current standing and references are not autonomous personalities/schedules or a general story planner. The content loader binds this version's eight adapters. Preserve those limits; no rewrite or new NPC system is justified by this audit. |

**Meaningful choices exist:** accepting a promise creates a later obligation;
keeping it forfeits wages but opens different work; moving it creates another
conflict; failure/breach persists; legal choices change outcomes and finances;
credit, prepayment and lawful recovery provide continuations. These are different
futures. Refusal/expiry variants often have the same economic future and provide
agency rather than additional progression. There is no demonstrated need to force
every option to reward the player or invent a new mechanic for each refusal.
The week is playable without a villain, combat, mandatory daily chores or round-trip
commutes. Long-term repetition and mild survival pressure remain visible limitations.

## Regression, compatibility and CI evidence

| Check | Actual result |
| --- | --- |
| Submitted baseline `python -B -m unittest discover -s tests -q` | 274 passed in 50.096 s. |
| Five targeted new tests against the uncorrected submission | Four failures/one error reproduced the findings above. No existing assertions were weakened. |
| `python -B -m unittest discover -s tests -p test_m015_acceptance_audit.py -v` after fixes | Nine passed in 1.493 s; includes 21 option subtests, stale CLI mapping, disabled CLI attempts, pending M014 disk adoption and changed room eligibility. |
| Complete corrected suite | **283 passed in 45.118 s**: all 274 existing tests plus nine new tests. |
| Required seven-day resume / 56-day commands | All five paths completed for each command; documented outcomes and fingerprints preserved. |
| Original-head save compatibility (`python -B -` isolated git-source check) | Ten saves generated by exact original modules loaded JSON-equivalently: five campaign branches, pending enrollment, accepted promise, moved promise, prepaid room and stale clock. The stale career then continued/saved correctly at day 9. |
| `python -B -` documentation/AST checker | 31 documents, 272 local links, four Python fences and 46 Python modules; both JSON content files parse, zero failures. |
| `git diff --check` | Passed. |

The complete suite also actually ran historical fixtures, failed saves/atomic
backups, budget/travel restrictions, independent hash-seed processes and reversed
dictionary replay. New checks reject inconsistent promise state rather than
inventing a repair or erasing history. Valid M001–M015 saves require no new field,
ID, content fingerprint or version migration. Unknown metadata is retained in saves
and excluded from the public memory projection. No dependency was added.

**CI independently verified at audit start:** both submitted runs succeeded at
`94455aa`; the [PR run log](https://github.com/CapuchaRojo/gotham-underworld/actions/runs/41863383724)
reported 274 tests in 30.792 s. The corrected final-head checks are a separate gate;
their actual disposition is recorded in PR #15 and the Mission 010 final response.
Do not infer a corrected-head CI pass from these baseline results.

The next step is human review and separately authorized M015 merge. Afterwards,
define a small M016 transportation contract around meaningful destinations,
transparent outbound/return costs and zero-cash recovery using the existing service
and navigation rules. This report authorizes no M016 implementation, prologue,
combat, character-system expansion or graphical work.
