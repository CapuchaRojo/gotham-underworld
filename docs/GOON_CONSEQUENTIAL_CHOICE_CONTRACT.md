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
