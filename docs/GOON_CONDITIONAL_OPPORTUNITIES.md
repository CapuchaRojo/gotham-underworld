# Gotham: The Goon — Conditional Opportunities

**Status: future design proposal, unimplemented in M013.1.** Current jobs do not
have this opportunity lifecycle. This document proposes how the
[career web](GOON_CRIMINAL_CAREER_WEB.md), employers, influence stories and
institutions can share eligibility without promising a collectible villain roster.
The [rogue registry](GOON_ROGUES_GALLERY_REGISTRY.md) is a pool of proposed
versioned content; the [minor ecosystem](GOON_MINOR_CRIMINAL_ECOSYSTEM.md)
distinguishes actors, crews and full factions. Neither listing nor fame creates
an available offer, treasury, district owner or guaranteed encounter.
The [atlas](GOON_GOTHAM_ATLAS.md) supplies proposed place IDs and
[travel rules](GOON_TRAVEL_NETWORK.md), not current player-location state.
Future offers should disclose known commute/return requirements and viable local
alternatives; geography alone cannot spawn a contact or retrospectively gate
old jobs. Route/permission changes follow explicit atomic outcomes and the
[map migration contract](GOON_MAP_SIMULATION_INTEGRATION.md).

## Eligible does not mean available or encountered

An opportunity has a stable definition ID and a career-specific instance ID,
source, prerequisites, known/unknown information, bounded offer terms, simulation-
day expiry, capacity and terminal outcomes. Meeting an eligible employer can still
fail to occur because demand is absent, a contact is unavailable or a seeded
selection excludes the opportunity. Never advertise a probability as a promise.

| Input | Proposed use | Player-facing information boundary |
| --- | --- | --- |
| Skills / qualifications | Require a capability or allow an alternate approach | Show known skill routes; do not invent hidden class locks |
| Reputation | Use the relevant audience's actual knowledge | A private success is not instantly citywide renown |
| Faction affiliation | Permit, complicate or exclude a contract | Explain known conflicts and an independent alternative |
| Employer demand | Open only useful work within resources/capacity | A rare skill does not guarantee a vacancy |
| NPC recommendation | Refer to a specific kept promise or relationship | Preserve source and credibility; referral is not acceptance |
| Relationships | A contact can sponsor, refuse or warn | Explain the response using facts that contact knows |
| Location | Require presence or reachable access under future travel rules | No travel system is added now; avoid teleporting to a named villain |
| Criminal history | An employer or civilian program may consider documented acts | Records and rumors are separate; allow lawful reintegration |
| Legal status | Respect custody, future supervision and conflicting commitments | No contract silently bypasses release or court rules |
| World events | Demand/capacity change with finite incidents | Publish known expiry/stage effects; no online event calendar |
| Prior decisions / personal code | Honor promises and refusal boundaries | Explain exclusions without treating expression as an irrevocable class |
| Deterministic probability | Select among eligible offers on a defined trigger | Unknown exact odds may remain unknown, but refresh/load never rerolls |

## Proposed lifecycle and revalidation

`candidate -> offered -> accepted -> resolved` is the ordinary path.
Candidates may be suppressed; offers may be declined, expired or withdrawn.
Accepted work may complete, fail or be cancelled under its pinned terms. These
are conceptual states, not today's save fields or commands.

Evaluate on explicit simulation triggers, such as a day transition, completed
contract or referral event. Sort definitions/participants by stable IDs before
evaluation. Use an isolated RNG keyed by seed, opportunity rules version, trigger
ID, definition ID and actor ID. Persist the evaluation result and offer instance.
Do not derive the trigger ID from event-list length, clock time or dictionary order.
One trigger produces at most one instance per definition and consumes capacity
once. Opening a screen, a rejected command and a reload generate no new draw.
Asking for the same referral again does not create a new causal trigger; the
underlying recommendation/promise ID is reused. A later genuinely changed demand
or relationship needs its own recorded event, not a new ID minted on request.

Revalidate volatile facts at acceptance: available budget, employer/actor status,
legal access, capacity and conflicting commitments. If invalid, reject atomically
with a reason; do not substitute another employer or reroll for a better offer.
Mark withdrawal through an explicit successful world transition, rather than
mutating state inside a read-only report or rejected acceptance. Accepted terms
remain pinned; any later cancellation must identify its cause and declared losses.

Expiry uses advanced game days, not elapsed real time. Warn when known offers will
expire, preserve their outcomes and explain missed demand when the player could
know it. Offer neutral work, another contact, training or a later unrelated route.
An opportunity can remain permanently inaccessible without making campaign
completion impossible. Do not secretly reserve every named-villain encounter for
every career or force one to occur as a pity reward.

## Proposed Joker-specific campaign gate

The [Joker recruitment contract](GOON_JOKER_RECRUITMENT.md) uses this general
lifecycle with an additional necessary gate: formal initiation requires an actual
direct Joker encounter during an Arkham storyline, a valid authored offer and
explicit acceptance. Street work, a cell's recommendation, a recording or a
relationship threshold cannot substitute. Joker's presence and role must fit
world state and pinned continuity; the encounter still need not yield an offer.

Represent this as content-defined predicates over episode/actor/encounter facts,
not `if employer_name` engine logic. Persist the actual encounter and offer cause;
revalidate actor availability and consent at acceptance. Citywide cell work remains
possible without formal membership and during Joker's absence. Refusal or no
encounter leaves independent and non-Joker completion routes. Treatment/admission
must not become a repeatable recruitment farm or a prerequisite for finishing.

## Illustrative rule, not a registered definition

A dispatch referral might require a driving qualification, a sponsor who knows a
kept promise, an open employer slot and no custody restriction. On one recorded
referral trigger it has a provisional 40% offer chance, independent of unrelated
job RNG. If selected, the offer lasts two advanced days. An employer losing the
contract before acceptance causes an explained withdrawal, not a different
villain appearing. Missing it leaves civilian transport and independent work.
No particular named employer is guaranteed even if all prerequisites are met.

## Ten-field review

| Criterion | Opportunity contract |
| --- | --- |
| Meaningful decisions | Pursue, verify, negotiate, accept, refuse or let an offer expire. |
| Observable consequences | Show eligibility information the player knows, costs, source, deadline and acceptance/withdrawal reasons. |
| Persistent state | Evaluation/instance IDs, pinned terms, deadlines, capacity, decisions and outcome. |
| Alternative outcomes | No offer, disputed information, acceptance, refusal, cancellation, expiry or another career route. |
| Replayability | Skills, demand, relationships, location, records and prior choices interact with stable seeded selection. |
| Grind risk | Repeated referral requests could become a slot machine; cap evaluations per causal trigger and avoid mandatory rare drops. |
| Determinism | Recorded domain-specific draws and sorted eligibility; verify identical scripts across resume and processes. |
| Save compatibility | Later additive empty opportunity state; no retroactive rolls/expiry on load or promised villain meetings; pin active definitions. |
| Offline operation | Local predicates, content and schedules; a complete career needs no server time/account. |
| Exploits and agency | Prevent refresh farming, duplicate capacity/rewards, hidden substitutions and a missed-offer campaign softlock. |

Future acceptance tests must exercise no-offer careers, expired/withdrawn offers,
stale eligibility without mutation, unavailable/dead actors, repeat triggers,
read isolation, save/resume across deadlines and multiple viable endings without
any named encounter. This milestone adds neither state nor tests for that future
system. Worked examples are in the career web.
