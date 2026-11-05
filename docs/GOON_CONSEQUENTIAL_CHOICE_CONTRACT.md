# Consequential choice contract — M015

Mission 009 authorizes a bounded neighborhood slice. The [prologue](GOON_PLAYABLE_PROLOGUE_CONTRACT.md) remains a future content milestone. This contract refines the [M015 proposal](GOON_M015_DAILY_LIFE_CONTRACT.md); actual executed results belong in [validation](M015_VALIDATION_REPORT.md).

## Ownership and integration

The game service is the only player command boundary. A choice has a stable instance ID, definition ID and source ID, an opening/expiration day, and one terminal selection or expiration. Display letters are temporary labels for stable option IDs. The generic choice engine handles visibility, eligibility, action cost, terminal settlement and structured choice events; neighborhood adapters own actual effects. Text never grants an effect.

Each authored option specifies intent, known prerequisites, location, action cost, money/risk, an effect adapter, persistent consequences, delayed consequences and continuation. Available options may be selected. Unavailable visible options explain a **known** obstacle. Hidden options are omitted entirely until an observed interaction justifies presenting them. No predicate consults hidden police investigations, secret NPC intentions or unrelated private player actions. A criminal option says “try”; the established seeded resolver decides success and exposure.

Preview is detached and advisory. Selection rechecks current day, state, knowledge, location, freedom, affiliation, roster slot and action allowance on the service candidate. Failure changes nothing. Selecting once closes the source opportunity; save/load cannot reopen it. A refusal has no action cost or repeatable reward. Completed work and help consume one action; the optional referenced audit shift consumes two. All use the same three actions as legal responses and existing jobs. Movement still costs only the existing 18 TU.

## Initial authored neighborhood

The content pack uses existing p031 (home), p032 (store) and n13 (public hub). Tess Navarro coordinates repair shifts and the housing cooperative; she values keeping a realistic promise over exaggerated loyalty. Cal Mercer is a runner who keeps a careful account of work and pay while overstating his confidence. Both are original characters. Their records are separate from the legacy faction NPC roster, which requires faction membership and fixed policies.

| Source | Intent, trade-off and immediate effect | Persistent / delayed consequence and continuation |
| --- | --- | --- |
| Opening shift | Work a funded $20 lawful shift at p032 for one action, or decline it. | One wage; Tess remembers attendance. Refusal/expiration leaves the next local offer available. |
| Tess's invitation | Promise to help on Day 2, or honestly decline. | Acceptance records a dated promise; an ignored invitation creates no promise. A kept promise earns a reference; a broken promise causes a proportionate, bounded reaction. |
| Cal's introduction | Ask about his work at n13, or decline. | Only the conversation discloses his referral. No affiliation, payout or police knowledge is invented. |
| Day-2 roster | Choose a lawful shift, try a known criminal collection referral, keep the promise, negotiate another day, or withdraw. | These share one disclosed morning roster slot. Work pays once; help earns no money; negotiation moves the favor to Day 4 once; withdrawal forgoes the slot. An accepted but unkept promise breaks at its deadline. |
| Midweek and late offers | Work, refuse, or use a reference/known quieter referral when offered. | Tess's reference opens a two-action $25 audit shift; Cal's observed successful collection opens existing courier work. Ordinary lawful work remains available at low standing. All offers expire. |
| Room review | Offer one action of maintenance against up to $10 of arrears, or ask to retain grace. | No cash is generated. Arrears remain bounded; home, saving, waiting and local lawful work remain accessible. |

Criminal referrals require an explicitly chosen existing faction and use `legal_engine.job` once. They preserve its reward, heat, witness, case, reputation and territory effects. The life ledger records that payout and never pays it again. Tess does not react to Cal's private jobs. Cal learns the result of his own referral, not the player's legal responses or household finances.

An earned reference remains a known fact, while current standing governs whether
it can be used: Tess requires standing 2 for the audit, Cal standing 1 for the
quieter referral. A hold is visible only after that work is known; it does not
reveal an unknown offer. Ordinary repair work and honest refusals remain available.
Mixed-source choices are presented by the player's planner, rather than attributing
knowledge of another contact's work to an NPC.

## Housing, money and time

`settle_in` explicitly accepts the disclosed $30/seven-day cooperative arrangement at p031/n13. It activates next day and first comes due seven day advances after acceptance: acceptance on day 0 means due on day 7. Historical careers receive no state on load. They first adopt navigation if needed, visit n13, and explicitly accept this arrangement; an unknown home may then become p031 without teleportation, refunded actions or invented history. An existing different home is never overwritten.

Home inspection exposes terms, receipts, deadlines and local opportunities. `pay_room` at home may prepay up to one contribution or pay existing arrears; each receipt corresponds to one real cash deduction. On the due day, credit is applied and only available cash is charged. Unpaid balance is capped at $30; while arrears remain, the cooperative retains a basic grace arrangement instead of stacking further rent or fees. Due reviews continue weekly. No instant eviction or resource reward for staying home. Maintenance is a finite room-review opportunity, not an unlimited conversion loop.

Player cash is authoritative. A continuous ledger begins at explicit enrollment and records M015 wages/payments plus net cash changes from existing commands/day rules. Legacy legal fines and NPC support retain their own detailed domain events. Receipts, contact memories and choice outcomes reference their source and command/day identity. They are auditable records rather than independent cash balances.

One post-court/post-navigation daily phase activates enrollment, settles due room reviews, expires offers, resolves missed promises and opens the current finite weekly roster. A day marker makes repeated processing inert. Reports, loads, movement and conversations never advance time. One roster slot can be used once; other daily actions remain available for legal decisions and other systems. There is no hourly scheduler or mandatory round-trip commute.

## Persistence and acceptance

The optional `daily_life_version: 1` extension pins its content/rules and validates nested housing, ledger, contacts, promises, choices and event references. M001–M014 saves remain valid without it. Unsupported versions, changed required content, malformed receipts, duplicated settlements and inconsistent cash fail before play. The outer save version and atlas fingerprint remain unchanged.

Tests must cover visibility, stale previews, zero actions/TU/cash, custody, travel, every branch/refusal, changed deadlines, exactly-once money and memory, ordinary missed-obligation recovery, malformed saves, historical opt-in, independent-process determinism and disk resume. Five seven-day campaigns and longer continuations must execute through service commands. Meaningful differences are actual money/risk, a kept/broken/moved promise, access to different work, and bounded household debt; flavor alone is not a branch.

## Mission 016 extension — implemented optional Night Shift

The existing `choice_engine.present/eligible` assessment pattern also serves the
incident adapter. Its four stage records settle independently: offer, work,
optional report and earned follow-up. They use `incident_choose`, with explicit
stable incident/stage/option IDs. The adapter records `incident_transition`
events instead of pretending these are M015 roster selections or reusing a slot.
Current place, lawful access, freedom, disclosed dates, knowledge and remaining
shared actions are rechecked; only currently eligible options are offered.

Ada is an optional original shop owner added only by incident enrollment. Her
standing and memory history remain under `daily_life`, with incident receipts
validated as delegated sources. Tess/Cal's existing facts, rewards, rosters and
content fingerprint are unchanged. The player cash balance and life ledger
remain authoritative. A report is scoped information, never a fabricated job,
automatic charge or additional reputation meter.

Complete inspection, partial observations, failed inspection, unfinished accepted
work, lawful safety help, refusal, optional disclosure/withholding, ignored known
offers and missed unknown incidents are distinct. The world review and shop
reopening happen independently. At most one $12 inspection and one separate $8
follow-up can settle. See the implemented section of
[After Dark](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) and
[executed validation](M017_NIGHT_SHIFT_VALIDATION.md). No generic rogue dialogue,
membership, clock, citywide rumor or non-job prosecution system is implied.

## M018 extension — sources and targeted corrections

`incident_dispatch` now routes both independently adopted definitions through
the same discovery/choice commands and `incident_lifecycle` stage settlement.
Night Shift keeps its original stage records and source IDs. Wrong Notice uses
compare, verify, response, repair, followup and aftermath stages rather than
copying a daily-life roster/job. Each stage settles once or expires.

World truth is not a UI prerequisite. Initially the journal offers conflicting
limited claims, not the correct answer. Verification reveals only the local
ledger; it does not correct residents. A board correction, tomorrow's desk posting
and a warning to Sam's group have distinct recipients/timing. Unchecked sharing
can hurt trust; a verified retraction earns no bonus. Late correction cannot erase
delivery-day harm. Refusal invents no promise and preserves ordinary work/home.

All substantive choices cost one of the existing three actions; refusal and
receiving the local final circular are zero-cost, one-shot informational choices.
Helping guarantees no wages. A verified vacancy permits a selfish lawful
reservation with a disclosed social cost and one optional $5 shift. No new crime,
job-risk roll, prosecution or automatic membership is fabricated for this episode.
Player projections do not receive automatic private reactions before a source
delivers them. Full audit state remains available to save validation/debugging.

The [After Dark contract](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) specifies
exact eligibility/timing and [M018 validation](M018_WRONG_NOTICE_VALIDATION.md)
records executed acceptance, replay and CLI evidence.

## M020 extension — ordinary work, housing and support

**Implemented locally by Mission 026**, from merged M019 `6682019`. This is an
opt-in extension of the same neighborhood, not another daily-life engine.
`enable_ordinary` at home/n13 after active life pins `ordinary_version: 1` /
`ordinary` and activates next day. No old work, debt or relationship is backfilled.
The outer save, old content pins, home permission, three actions and eighteen TU
remain unchanged. Post-life day processing reuses the existing clock boundary.

| Source / intent | Eligibility, cost and effect | Persistent consequence / recovery |
| --- | --- | --- |
| Dependable repair employment | Existing $20 store shifts and reference audit retain their original rules. Future actual repair choices build employment standing 0–6. | Observe each source once, without another wage or personal reward. Refusal/unknown expiry does not reduce standing. All basic shifts stay available regardless of employment or support status. |
| Cooperative kits at home | One allocation per ordinary week, open days base+1 through base+4. Two actions; $24, or $28 at employment 3. Needs a future observed repair or actual arrears. Seed+week divisible by three means posted supply cancellation. | One funded settlement. Tess records delivery once; employment rises at most one. No travel or cash advance. Supply cancellation creates no player blame. |
| Later delivery request | One action at the home ledger while open. Tess's preauthorized posted terms accept employment 1, or deny employment 0; one request, no RNG. A recorded request does not claim a personal meeting with Tess. | Acceptance pins the current wage and delivery days tomorrow/the following day. Pay only on completion. Missed or withdrawn accepted work loses at most one employment and one personal standing; no cash debt. A denied request leaves ordinary completion open. |
| Conditional social support | One $20 reserve per career, one action at home. Tess handles the fund on ordinary roster days 0, 2 and 5. Needs arrears, or cash below $30 with review in at most two days. | Explicit $20 repayment due in seven days. Once overdue, one -1 memory; no interest, seizure, warrant, eviction or rolling deadline. One-action home repayment closes it with one +1 memory and does not refill the fund. |
| Refuse work/help | Free and once for that allocation/assistance offer; explicit withdrawal from already reserved work is distinct from refusal before accepting. | No new debt or morality penalty. Home, repair shifts, maintenance and wait remain available. |

The existing cooperative room is the sole housing arrangement. Its $30 review,
prepayment, capped arrears, once-per-review maintenance and basic access are not
replaced. `ordinary`/adopted `home` expose actual housing and record an advance
review notice within two days; neither creates another charge or benefit for
inspection. A late support obligation is separate from room arrears.
Due days are processed at the start of that day: repay before the transition
that reaches the agreed due day. Withdrawal is available as soon as a reservation
is accepted; only paid completion is gated to its later delivery window.

The pure ordinary reducer returns effects; only its service-owned adapter applies
cash via `daily_life.record_balance` and personal facts via `_memory`.
`ordinary_state` replays actual repair sources, user frames, completed schema-1/2
arrivals, available actions, prior money/housing/custody facts and stable effect
identities. Real transactions and every delegated memory are checked against those
effects. Rejected commands and returned reports cannot mutate state or RNG.
No work/help/loan information is sent to either M019 institution automatically.

The finite employer allocation and $20 assistance reserve are authored funding,
not district treasury withdrawals or a new lending economy. Rates and limits are
separate JSON content; mechanics do not depend on fictional-property names.
Existing incident discovery still requires its own real knowledge sources; a kits
completion is not a promise-kept reference or an institutional report.

Five futures are demonstrated rather than guaranteed careers: reliable wages and
current rent; shifted work with an accepted obligation; conditional support and
repayment; missed work/overdue support followed by recovery; and refusal with
continued ordinary access. Equal eventual cash does not erase different accepted
terms, deadlines or records. There is no combat, general employment simulation,
dialogue system, new transportation mode, Court content or implemented prologue.
See [M020 executed evidence](M020_ORDINARY_GOTHAM_VALIDATION.md).
