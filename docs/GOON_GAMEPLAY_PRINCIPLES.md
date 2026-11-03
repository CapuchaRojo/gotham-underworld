# Gotham: The Goon — Gameplay Principles and Differentiation

Status: M013.1 design policy. This document adds evaluation criteria, not gameplay.
The [bible](GOON_NARRATIVE_DESIGN_BIBLE.md) defines feature-status labels; the
[combat contract](M014_COMBAT_DESIGN_CONTRACT.md) is a proposal awaiting approval.

## Historical reference and evidence limits

Batman: Arkham Underworld explored a mobile criminal-mastermind/base-management
fantasy. Our player fantasy concerns the worker living inside that economy.
Shared setting or villain recognition is not sufficient differentiation.

Contemporary criticism was mixed, not a unanimous finding of failure:

- Gamezebo criticized grind and limited originality while also praising polish,
  tactical elements, and some new ideas. Our inference is that recognizable
  characters and presentation cannot carry a repetitive decision loop.
  [Gamezebo review](https://www.gamezebo.com/reviews/batman-arkham-underworld-review-wonderful-toys/).
- Gagan Gupta's July 26, 2016 review criticized limited building choices and weak
  AI missions, while praising accessibility and comparatively generous premium
  currency. Our inference is to prioritize varied problems and legible behavior,
  rather than simply more unlocks. [Gadgets 360 review](https://www.gadgets360.com/apps/reviews/batman-arkham-underworld-review-865489).
- Jim Franklin's review, published July 23, 2016 and updated in 2020, questioned
  replay incentives and how much the game distinguished itself. Our inference is
  to make a different career produce different commitments and opportunities.
  [EIP Gaming review](https://eip.gg/reviews/batman-arkham-underworld-review/).
- A later firsthand mechanics account describes upgrade/recruitment timers and
  diamonds used to bypass delays. This is a 2017 account, not a 2016 review or
  proof of every player's experience. Our rule rejects monetized waiting gates.
  [SigTrent Games, August 20, 2017](https://www.sigtrent.com/batman-arkham-underworld-game-review/).

Sources consulted November 3, 2026. These are limited critical observations and
design inferences, not audience research, a commercial forecast, or a claim that
any one mechanic caused the reference game's commercial outcome. No review text,
mission scripts, video-narrator material, or assets are copied into game content.

## The feature admission gate

Before approving a new gameplay feature, its contract must answer all seven:

1. What meaningful alternatives does the player have, including refusal or exit?
2. What observable feedback explains what happened and why?
3. Which future opportunity, relationship, obligation, or world fact can change?
4. Which repeated situations change the decision, not only its reward or numbers?
5. What makes the loop interesting without real-time waiting or monetization pressure?
6. How does the complete single-player path work offline?
7. How are deterministic replay, rejection atomicity, and old saves tested?

If the answers are only "bigger payout," "higher enemy level," and "repeat until
unlocked," revise or defer the feature. Do not expand an active milestone merely
to fill this checklist. A necessary technical foundation can explicitly add no
new player decision, with the future decision it enables and its limits stated.

## Non-negotiable anti-patterns

| Anti-pattern | Required alternative |
| --- | --- |
| Base-management progression reskin | Personal obligations, employment terms, relationships, and several viable careers. |
| Artificial real-time timers | Explicit in-game actions/time with visible city consequences and useful alternatives. Closing the app does not gate progress. |
| Pay-to-win or premium-currency dependency | Complete offline progression and recovery using ordinary play; no paid advantage or purchased bypass. |
| Repetitive numerical grinding | Change the affected people, knowledge, constraints, or approach; cap repeatable settlement and favor rewards. |
| Passive villain collection | Employers have goals, demands, unreliable promises, refusal rules, and consequences. |
| Generic stronger-number AI | Different goals, information, risk thresholds, resource limits, retreat conditions, and explainable priorities. |
| Unchanging organizations | Work terms and opportunities respond to losses, leadership decisions, labor relationships, and city incidents. |
| Story detached from simulation | Authored outcomes invoke the same lawful state transitions and audited events as ordinary play. |
| Meaningless dialogue choice | Distinct, persisted consequences or honestly label the line as expressive flavor. |
| Mandatory single-player services | Local authored content, local deterministic policies, and self-contained saves; no external AI requirement. |

Recovery days or an investigation review can be legitimate fictional time costs.
The player must see what advances, which commitments are affected, and how to
continue without paying real money. A button that exists only to repeat empty
waiting is still a failed design, even when the clock is an in-game clock.

## Evaluation of proposed major features

Every row is future design, not a claim of implementation. Apply this same schema
to any major feature added later. Each deterministic strategy is a proposal;
the content architecture specifies the integration and migration gates.

| Feature | Player decision | Observable consequence | Persistent world effect | Replayability consideration | Deterministic strategy | Offline compatibility |
| --- | --- | --- | --- | --- | --- | --- |
| Backgrounds | Select a contact and an obligation, not a best-stat preset. | Opening introductions and responsibilities differ. | Starting access and commitments. | Different ties change the same job's stakes. | Versioned starting-state templates and stable IDs. | Local templates; no account dependency. |
| Employment | Choose guaranteed pay, a risky share, renegotiation, or refusal. | Terms and actual settlement are shown separately. | References, obligations, and employer access. | Conflicting contracts and worker needs. | Persist accepted terms and settle each contract once. | Local contract definitions and ledger. |
| Recruitment/culture | Accept or reject a test and its commitments. | Sponsor and employer respond to the chosen approach. | Affiliation, references, and personal promises. | Skill, loyalty, and information approaches. | Predicate-based eligibility and authored outcomes. | Local policies and content. |
| Coworker loyalty | Protect, expose, help, or refuse a person. | The person explains a reaction grounded in known facts. | Specific trust, debt, boundaries, and access. | Personality plus prior history changes interpretation. | Bounded deltas, knowledge checks, causal event links. | Authored policies; no conversational AI service. |
| Civilian work/housing | Spend time on stable work or accept a risky opportunity. | Pay, access, and missed commitments are visible. | Shelter and social support, with a recovery path. | District disruptions and household obligations. | Bounded accounting and explicit daily transitions. | No daily login, online rent clock, or paid rescue. |
| Combat/recovery | Fight, guard, escape, surrender, or spend an action recovering. | Health, stamina, risk, and resolution are explained. | Injury, witnessed cases, reputation, and memories. | Goals and constraints vary; combat is not the only solution. | Stable encounter IDs, bounded turns, isolated RNG streams. | Local turns and saveable encounter state. |
| Legal responses | Preserve a defense, cooperate, accept, or leave a case unanswered. | Evidence, cost, and the recorded outcome are visible. | Criminal record and later opportunities. | Evidence strength, obligations, and known witnesses. | Case IDs, scheduled game-day reviews, one settlement. | Local court rules; no external legal service. |
| Rumors | Verify, act, withhold, or transmit a claim. | Source/confidence are visible; contradictions can be found. | Each actor's knowledge and trust in the source. | Changed sources and timing alter decisions. | Persist truth and beliefs separately; no UI rerolls. | Local claims and provenance. |
| City incidents | Evacuate, work, help, or exploit a disruption. | Affected services and people visibly change. | Finite incident stages and local consequences. | Different obligations and event combinations. | Seeded selection, explicit stage state, bounded modifiers. | Trigger from simulation state, not a server calendar. |
| Career paths/endings | Choose commitments and an exit, not only a rank increase. | Conditions and irreversible stakes are legible. | Different living arrangements, responsibilities, and endings. | Several viable success definitions. | Versioned predicates over recorded commitments. | Campaign complete without online unlocks. |
| High-threat intervention | Abandon an order, protect someone, escape, or surrender. | The threat is signaled; survival objectives are clear. | Employer reaction, injury, specific evidence or lost access. | Context changes who or what can be saved. | Content-defined objectives and bounded resolution. | Local policy; no live-service event requirement. |

## Current mechanical shallows

M013 is a foundation, not evidence that these future experiences already exist:

- Courier and collection repeat a small set of outcomes; reward/heat differences
  alone do not create a rich employment game.
- Joining has no initiation or negotiated terms; faction switching is unavailable.
- NPC policies are threshold rules, not persistent general personalities or
  NPC-to-NPC relationships. Memories are not a full belief/reasoning system.
- Scouting stores facts already visible in current reports; information acquisition
  therefore has limited value.
- Legal review is a small deterministic evidence rule; custody is accelerated.
- Faction competition has three districts and static wealth. Iron leads the
  one-year samples; the [report](../M013_SIMULATION_REPORT.md) does not prove universal balance.
- There is no health, tactical combat, housing, employer payroll, rumor model,
  branching campaign, or named DC encounter implementation.

Keep these limits visible rather than write narrative descriptions that imply
the systems already exist. M013.1 deliberately leaves all runtime behavior intact.

## Manual current-game walkthrough

This is a reproduction recipe for **existing M013 choices**, not a new mission:

1. Choose a fresh filename and launch `python gameplay.py --seed 42 --save career_goon_review_save.json`.
2. Run `join 1`, then `job collection` three times. Inspect `status` and `legal`.
   The shared action allowance is exhausted, so another costly response must wait.
3. Run `wait`. On the unchanged seed-42 baseline a documented case is pending
   with evidence 2. Read its actual case ID rather than assuming all seeds match.
4. Compare alternatives in separate fresh repetitions: `accept <id>` resolves a
   conviction immediately with an assessed $35 fine; `cooperate <id>` adds evidence
   and sets an eventual $30 conviction fine; `contest <id>` costs $20 and schedules
   a two-day review. Evidence 2 is too strong for the weak-evidence dismissal rule.
5. Inspect `events`, `legal`, and `intel`; advance days as necessary, save, and
   resume. Verify the chosen response and outcome remain, and the city keeps changing.

Fines are capped by available cash. This script has no health, wages, named
employer, or combat. Its limits help explain what future design must add.
Run the automated regression suite separately; this text is not itself a test result.

M013.1 verification used the service API in memory for steps 2–4 and two subsequent
day advances on each branch. Case 1 had evidence 2 after waiting; accept, cooperate
and contest produced assessed fines of $35, $30 and $50 respectively (contest also
cost $20). Each resulting world passed state validation. The CLI/save steps above
remain reproduction instructions; automated CLI/resume checks belong to the suite.

## Manual paper exercise for a proposed feature

For a proposed employment episode, give the reviewer a guaranteed-pay offer, a
larger uncertain offer, a coworker's request, and a sourced hazard report. Ask
for a choice, show the immediate result, then show a later job affected by it.
Repeat with one changed obligation. If the reviewer still makes the same choice
for the same reason every time, investigate a dominant strategy or insufficient
context. This is a design exercise, not a shipped gameplay scenario.

## Required milestone report

Every future milestone report must state:

- New meaningful player decisions, or explicitly that a foundation adds none.
- New persistent consequences and how they are exposed.
- Sources of variety across repeated situations.
- Potential repetitive, dominant-strategy, or grind-heavy loops.
- A short manual scenario, labeled executed, reproduction recipe, or paper-only.
- Areas still mechanically shallow and anything deferred.
- Actual automated checks run, deterministic replay/resume evidence, migration
  coverage, and offline constraints. Never infer a passing test from a written contract.

Readiness is assessed from these answers and the bounded milestone contract,
not the number of features or famous names listed in a document.
