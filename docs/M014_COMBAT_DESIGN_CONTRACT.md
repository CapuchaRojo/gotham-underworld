# Deferred combat design contract (historical M014 proposal)

**Mission 007 scope update:** M014 is now World Runtime and Navigation Foundation.
This retained combat proposal is deferred to an unassigned future milestone; every
M014 reference below describes its historical proposed numbering, not the current
implementation scope. See the [current roadmap](GOON_MILESTONE_ROADMAP.md).
No combat implementation is authorized by Mission 007.

**Status: proposal for human review; no combat is implemented in M013.1.**
This contract describes the smallest prospective M014. It is not authorization
to start M014, add named DC characters, migrate current content, or change saves.
All numerical values below are provisional tuning proposals. The goon-centered
[narrative bible](GOON_NARRATIVE_DESIGN_BIBLE.md),
[gameplay principles](GOON_GAMEPLAY_PRINCIPLES.md), and
[content architecture](GOON_CONTENT_ARCHITECTURE.md) supply its constraints.

## Player promise and bounded scope

An ordinary worker chooses whether to stand their ground, disable an opponent,
withdraw, or surrender. Surviving with an injury or losing the job can be a
meaningful outcome. Victory must not require killing, and losing cannot trap a
career in an unwinnable command state.

The minimum is **one player against one NPC**, turn-based, with compact text
intent and outcome feedback. Use neutral prototype opponents and data-defined
policies. No grid, pathfinding, real-time input, group combat, drugs, crafting,
weapon economy, campaign arc, probation, parole, undercover system, or Bat-family
spawn/investigation system belongs in this slice. No paid or online service.
Crews and named high-threat content are future integration targets.
The expanded M013.1 [career web](GOON_CRIMINAL_CAREER_WEB.md),
[influence](GOON_VILLAIN_INFLUENCE_SYSTEM.md) and
[institution/recovery](GOON_INSTITUTIONS_AND_RECOVERY.md) proposals are separate
future domains. M014 does not implement career qualifications, dependency,
psychiatric mechanics, incarceration or treatment plans to connect to them.

## State, daily allowance, and transaction boundary

Proposed state consists of a versioned player health/injury extension, a bounded
combat counter, and at most one active encounter with participant IDs, rules and
definition versions, turn index, stamina, intent, objective, surrender terms,
and settlement status. Persist everything needed to resume between turns.

Proposed command names below are illustrative and **are not current commands**:

| Command | Cost and prerequisites | Committed effect |
| --- | --- | --- |
| `combat_start` with opponent/encounter reference | One daily action; health >0, not detained, no active encounter, eligible unconsumed opportunity | Pin participants, parameters, objective and exit terms; show threat and available actions |
| `combat_act` with action and lethal/nonlethal intent | Zero daily actions; active encounter; valid action/intent; adequate stamina where required | One complete player turn plus at most one opponent response, or terminal settlement |
| `recover_health` | One daily action; no active encounter, not detained, damaged health or injury | Free basic recovery; no cash prerequisite |

Use the existing game service transaction and string argument validation. Starting
combat consumes an action only on success. Continuing it must work when all three
daily actions are used. Stamina is the tactical budget, separate from daily actions.
Rejected commands consume no stamina, action, turn, RNG counter, or events.

While an encounter is active, reject jobs, district missions, faction joining,
day advancement and legal responses; allow reports, saving, combat actions, and
surrender. No daily phase runs inside combat. A completed encounter restores the
ordinary command boundary; custody still follows existing legal rules.
An inactive player at zero health can save, view reports, wait, and recover; jobs,
missions, and new combat are unavailable until health is positive. Existing
automatic court resolution on day advancement remains the custody escape path.

## Health, stamina, injury, and recovery

Proposed player health is an integer **0–100**, initially 100 for a migrated career.
This default means no recorded damage, not a reconstruction of historical health.
NPC health is defined by its profile; a basic test opponent has 40. Encounter
stamina is an integer **0–6**, initialized at entry and capped by current injury.
Health persists across encounters; encounter stamina does not become free health.

Keep one simple persistent injury grade: 0, 1, or 2. Maximum stamina is respectively
6, 5, or 4. At settlement, reaching zero health applies grade 2; otherwise health
at or below 25 applies at least grade 1. Retain a worse existing grade. Do not
stack unbounded injuries or roll permanent disability in this minimum. Provide
plain descriptions explaining the penalty and recovery route.

`recover_health` restores up to 20 health and reduces injury grade by one, costs
one daily action, and requires no money, home, item, or real-world wait. Reject it
without mutation if already healthy and uninjured. It also works from zero health.
The free `wait` command can refresh the allowance after an encounter; the city
continues normally. Thus a broke, injured player always has a recovery route.
No passive recovery on load, report, or clock redraw. No clinic/housing system is
needed to make this minimum safe.

## Tactical actions and finite resolution

For a neutral fixture, propose base player damage 20, NPC damage 10, and hit chance
70%. Apply only declared, bounded equipment/style modifiers, then clamp hit chance
to 5–95%. Integer damage is nonnegative; a successful damaging hit deals at least
one health point and cannot lower health below zero. These numbers are testable
starting values, not a claim of balanced combat.

| Action | Stamina | Effect and tradeoff |
| --- | --- | --- |
| Strike | Spend 2; aggressive style spends 3 | Roll the declared hit chance; damage on success; exposes the player to one response if the opponent can still act |
| Guard | Restore 2 up to injury cap | No attack; halve damage from the next response in this turn, using `max(1, damage // 2)` for a damaging hit |
| Withdraw | Spend 1 | Attempt escape using a declared, bounded profile chance; neutral default 60%, clamp 20–95%; failure permits one response |
| Surrender | Free; always available | End the encounter under visible, pinned terms, without a hit roll or extra opponent attack |

Guard at zero stamina is valid. Withdraw is unavailable at zero, with guard and
surrender still valid. There is no distinct free escape reroll: **escape** is the
successful outcome of withdraw. If an opponent is incapacitated, escapes, or
accepts surrender, do not run an extra NPC attack. The opponent's own guard protects
it from the next player strike; it expires at the end of that next player turn.
The UI must show this defensive state before the player commits.

Use at most **six complete player turns** per encounter. If still unresolved,
settle a disengagement/standoff after the sixth response: no victory reward,
objective failed, health/injuries retained. This cap prevents infinite guarding
or tactical farming. A consumed mission encounter cannot be restarted for more
reward or fresh RNG. Trigger/cause IDs, not repeat UI clicks, identify opportunities.

Show current health/stamina, threat, opponent visible intent, projected costs,
active defense, exit options, and known consequences before commitment. A failed
roll shows its threshold and resulting state. Hidden future consequences should
be represented as uncertain information, not presented as guaranteed outcomes.

## Nonlethal, lethal, retreat, and defeat outcomes

Nonlethal intent is the default. Reducing an NPC to zero health incapacitates them;
it does not kill, erase legal exposure, or promise that no injury occurred.
Lethal intent requires explicit selection and an eligible scenario/profile. An
eligible opponent reaching zero under lethal intent dies; persist that outcome
and disable their future opportunities. Named/story-protected content needs
authored outcome rules before it can participate; do not revive actors on reload.

Player zero health means incapacitation and terminal defeat in this minimum,
not automatic career deletion or surprise permanent death. The player retains
health zero until recovery. Display any authored loss before entry and settle it
once; never take more cash than the player has. No arbitrary confiscation or loot
system is needed for the first fixture. Surrender terms may specify a bounded loss
or objective failure, but cannot depend on an unimplemented legal/debt mechanic.

Retreat preserves an opponent's state and records the unfinished objective.
The minimal slice offers no rematch/reset loop. Any later rematch needs explicit
continuation rules and cannot resurrect a dead actor or repay an old objective.
Future permanent-death campaigns require separate approval and clear player consent.

## Equipment, styles, and NPC behavior

Use one held-item slot and one protective tag, defined by neutral local data.
Modifiers are bounded and pinned when combat starts; no inventory exchange,
shops, durability, loot tables, or online equipment service is required. A basic
fixture can use an unarmed/default loadout. Do not encode licensed gadgets in
damage resolution.

Proposed style modifiers, for review alongside the base numbers:

| Style | Outgoing damage adjustment | Incoming damage adjustment | Strike stamina cost |
| --- | --- | --- | --- |
| Balanced | 0 | 0 | 2 |
| Cautious | -5 | -2 | 2 |
| Aggressive | +5 | +3 | 3 |

The held-item definition may adjust damage by 0–5 and hit chance by -5 to +5
percentage points; the protective tag may reduce incoming damage by 0–2.
Apply base damage, attacker's style/item, then defender's style/protection,
clamp a damaging hit to at least one, and finally apply guard's reduction.
Unarmed/default equipment has zero modifiers. These are proposed validation
bounds, not approved item lists. Test that the style tradeoffs matter across
scenarios; do not assume this small table proves balance. No modifier may remove
guard/surrender exits. Never change an active encounter's pinned parameters.

NPC policies use bounded parameters and available knowledge: pragmatic opponents
withdraw when badly hurt, defensive ones favor guard against an aggressive style,
and aggressive ones spend stamina on offense and must guard when exhausted.
Implement a small deterministic priority list with stable tie-breaking; no LLM,
neural model, or behavior framework. A policy can surrender or withdraw on its
response instead of attacking. It cannot receive both a recovery action and an
attack unless that combination is explicitly the single action's effect.
Visible policy cues and different objectives should change player decisions;
increased health alone is not adequate variety. No NPC can inspect future RNG
or facts the scenario declares unknown to it.
For a concrete initial policy proposal: pragmatic first attempts withdrawal at
health <=25% if it has stamina; otherwise it guards if unable to afford its strike,
then strikes. Defensive first guards against a visible aggressive style unless
already guarding, then follows the same stamina/strike rule. Aggressive ignores
withdrawal and follows that stamina/strike rule. Failed NPC withdrawal consumes
its one response. Record the selected rule/reason; identical inputs select the
same rule. Future personalities should not be claimed from these three policies.

## Legal, personal, and world consequences

An encounter outcome may affect the job objective, employer reputation, a known
participant's relationship metrics, and a documented legal case. Show the reason
and before/after values. No automatic faction-wide knowledge of a private fight.
Defending a coworker can earn personal trust while frightening another witness;
this is a scenario proposal, not a general NPC personality system.

**Required integration work before combat can open cases:** the current case
schema/investigation expects a witnessed job's `source_attempt`. Add and test the
small compatible case-source adapter described in the architecture proposal.
A witnessed combat event references its actual encounter ID, never a fabricated
job attempt. Eligibility/evidence is authored data; heat alone cannot create a
case. Preserve M012 heat bounds, daily investigation idempotency, NPC acceleration
cooldowns, committed responses, court/custody consistency and unique legal records.
Keep existing jobs' seeded behavior unchanged. No probation, parole, undercover
investigators, or new criminal sentencing system in M014.

Do not award cash, loot, or experience for each strike. Settle objective rewards,
injuries, reputation and case creation once using the encounter's outcome ID.
Any optional territorial consequence must go through the existing shared capture
rules; the first combat fixture need not change district ownership.

## Batman and future crews

Batman is an endorsed future **overwhelming survival threat**, not a routine boss
or a source of repeatable equipment. A future licensed encounter should reward
avoiding detection, escaping, or surviving surrender rather than beating him in
an ordinary fair fight. Show the threat before entry; never require victory for
career recovery. Character-specific capabilities and nonlethal behavior belong
in content/policies, not `if name == ...` checks.

M014 can test a neutral high-threat profile with superior bounded statistics,
an explicit unwinnable-objective warning, and guaranteed surrender safety. This
validates the exit contract without spawning Batman or implementing Bat-family
investigations, city pursuit, stealth, or gadget systems. Exact licensed portrayal,
capture terms and encounters remain separately reviewable content proposals.

Use stable participant IDs, actor-attributed actions and an explicit initiative
list so later crew combat has a migration path. M014 accepts exactly two
participants and rejects larger encounters. Do not implement group turns,
friendly fire, formation, command AI, or crew recruitment in this slice.

## Determinism, events, and save compatibility

Resolve a complete turn atomically: validate, apply player action, determine
whether a response is permitted, apply one NPC response, check the turn cap,
settle if terminal, and commit. Save only at committed boundaries. Reloading
cannot repeat the response or pay an outcome twice.

Use a new local RNG namespace, independent of existing job/feud streams. Encode
seed, combat rules version, encounter counter, turn, actor ID and effect ID in
a stable format. Persist the counter and pinned parameters. No global RNG,
Python `hash`, event-count seeds, wall-clock time or rendering-time draws. Log
material rolls and thresholds so a result is explainable, not secretly rerolled.

Proposed structured kinds include encounter started, action resolved, encounter
settled, injury changed and recovery applied. Each carries its schema version,
encounter/turn/actor IDs where relevant, command cause, reason, before/after values
and declared costs. A terminal settlement marker prevents duplicate effects.
Keep authoritative world saves; do not replace persistence with replay of prose.

Add a separately versioned combat/health extension with additive defaults, strict
range/reference validation, and clear rejection of unsupported versions. Old saves
have no active encounter; migration must not replay fights, invent injuries, reset
the three-action budget, rewrite events, or change existing legal records.
An active encounter pins sufficient definitions to resume offline after defaults
change. Malformed state fails before play. Use existing atomic save/backup behavior.

## Proposed acceptance criteria for implementation review

The [ten-field review](GOON_GAMEPLAY_PRINCIPLES.md#the-ten-field-design-review)
applies to this minimal contract:

| Criterion | Combat contract |
| --- | --- |
| Meaningful decisions | Strike, guard, withdraw, surrender; choose intent/style and later recovery. |
| Observable consequences | Health/stamina, pinned costs, threat, rolls, reasons and objective result. |
| Persistent state | Health, injury, encounter result, specific reputation and documented case effects. |
| Alternative outcomes | Incapacitation, lethal outcome where eligible, escape, surrender, defeat or standoff. |
| Replayability | Policy, objective, equipment/style, witnesses and conflicting obligations. |
| Grind risk | Guard/strike alternation, recovery cycling and repeat encounters; finite turns and unique settlement. |
| Determinism | Isolated encounter/turn/actor/effect RNG and complete atomic turns. |
| Save compatibility | Versioned additive health/encounter state, pinned definitions, no invented historical fights. |
| Offline operation | Local rules/opponents and saveable decision boundaries. |
| Exploits and agency | No duplicate rewards, forced death, zero-action combat trap or broke-player recovery lock. |

- All 198 baseline tests remain passing; no edits that weaken legacy expectations.
- Tests cover every action, exhausted stamina, zero daily allowance during combat,
  every terminal outcome, the six-turn cap and free surrender from every live state.
- Rejected actions and conflicting city commands preserve the full world byte-for-
  byte in canonical JSON, including counters, events, health, stamina and actions.
- Health/stamina/injury bounds, zero-cash recovery from defeat, and healthy recovery
  rejection are exercised. Waiting after settlement always remains available.
- Lethal/nonlethal outcomes differ persistently; dead actors cannot be reset by
  resume. Objective reward, reputation and legal consequences settle exactly once.
- Migration fixtures cover every historical generation; malformed/unsupported
  health, encounter and legal-source data are rejected with useful errors.
- Identical command scripts reproduce from seed, across save/resume at every turn,
  across dictionary insertion orders and fresh processes/hash seeds. Reports and
  snapshots cannot change outcomes. Legacy RNG streams remain unchanged.
- A multi-day scenario includes injury, free recovery, documented case investigation
  and existing legal responses/court; no duplicate evidence or custody dead end.
- High-threat and varied-policy fixtures exercise escape, surrender and different
  choices; a deterministic long campaign still validates resource/legal invariants.
- CLI exposes the same commands/costs/events as the service. No GUI dependency,
  licensed assets, new named DC actor, or mandatory external service is introduced.

These are future tests to write, not test results from M013.1.

## Paper walkthrough and remaining decisions

**Paper-only scenario:** a neutral courier's delivery is threatened. The player
sees the job's reward, ordinary opponent, nonlethal default and safe surrender
terms. A cautious guard recovers stamina; a strike may disable the opponent,
while a failed withdrawal allows one response. The player escapes injured and
loses the delivery reward. Injury and the failed objective persist. A free,
action-costed recovery competes with paid work tomorrow. If a witness documented
the fight, the existing legal choices address the resulting case. Repeat with a
fearful opponent who withdraws; the changed behavior should change the choice.

This adds no current player decisions or consequences. M013.1 supplies a reviewable
contract, not a playable encounter. The proposed minimum remains mechanically
shallow: few actions, no geometry, one opponent, coarse injuries and threshold AI.
Guard/strike alternation and repeated recovery could become grind; the turn cap,
objective settlement, differing exit terms/policies and scenario variation must
be evaluated during implementation rather than assumed to solve it.

Before authorizing M014, review daily/tactical cost separation, the six-turn cap,
provisional numerical tuning and style modifiers, defeat/recovery guarantees,
the case-source migration, and exact initial fixture scope. Rights/title clearance
and any licensed content/distribution are separate decisions. **Stop at M013.1
review; do not begin M014 from this document alone.**
