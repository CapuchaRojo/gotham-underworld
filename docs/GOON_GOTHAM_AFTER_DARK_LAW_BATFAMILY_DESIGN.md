# Gotham: The Goon — Gotham After Dark, Law and Bat-Family

## Authority and scope

**Broader proposal from Mission 015, November 4, 2026; implemented slices updated through Mission 023.**
Sections 1–11 preserve the prior proposal/evidence; the implemented Night Shift
subset and current limitations are explicitly recorded in section 12. Section 13
records the implemented M018 two-incident extension; section 14 adds M019 intake. No global
clock, DC encounter or institutional career is implemented. This document selects
no DC continuity and authorizes no future implementation. The user-approved direction is a reactive,
offline city with ordinary people as protagonists, independent institutions,
predominantly nighttime dramatic incidents and meaningful lawful careers.
The mechanisms, role assignments, weights, schemas and sequencing below remain
**proposed** outside the expressly implemented sections 12–14, including future
numerical policies beyond the existing budgets.

Companion contracts: [Rogue Encounters](GOON_ROGUE_ENCOUNTERS_DESIGN.md),
[narrative bible](GOON_NARRATIVE_DESIGN_BIBLE.md),
[career web](GOON_CRIMINAL_CAREER_WEB.md),
[conditional opportunities](GOON_CONDITIONAL_OPPORTUNITIES.md),
[content separation](GOON_CONTENT_ARCHITECTURE.md),
[Joker recruitment](GOON_JOKER_RECRUITMENT.md) and
[playable prologue](GOON_PLAYABLE_PROLOGUE_CONTRACT.md).
The existing prologue/adoption boundaries must remain intact: no retroactive
encounters, forced affiliation, mandatory Batman meeting or surprise obligations.
This is an unofficial prototype, without claimed DC authorization. No published
dialogue, assets or story sequence is reproduced; public distribution and pitch
materials need separate rights review.

## 1. Actual time system and integration inventory

Legend: **I** = implemented in inspected source; **T** = existing behavior exercised
by executed tests, not proof of this proposal; **A** = user-approved direction;
**P** = proposed contract requiring implementation approval; **M** = missing
dependency. A table entry may contain more than one status with different scope.

| Status / exact seam | What exists | What must still be built or approved |
| --- | --- | --- |
| I/T — [service](../game_service.py#L79), [snapshots](../game_service.py#L65) | Commands execute on a private candidate, produce detached results and retain three gameplay actions/day. Adopted mobility candidates receive final validation. | P: encounter commands use the same boundary and resource owners; no narrative side channel. This is not a universal pre-command validator for arbitrary externally corrupted dictionaries. |
| I — [day increment](../simulation.py#L47), [daily pipeline](../gameplay.py#L77) | One integer world day. Advance, legal pressure, investigation, NPCs, economy, strategy, warfare, court when arrested, navigation and life execute in that order. | M: time of day, actor shifts and a general world-incident scheduler. P: one idempotent incident phase after life, without reordering existing phases. |
| I/T — [daily travel reset](../navigation.py#L299), [route preview](../mobility.py#L268), [journey](../mobility.py#L321) | 18 TU/day, explicit travel, closure/access checks, conditional return quotes, two-station mobility pilot and atomic fare effects. | M: time-dependent transit and facility schedules. No new walking/vehicle costs or timetable is established here. |
| I — [life day](../daily_life.py#L172), [slot key](../daily_life.py#L226), [life definitions](../content/neighborhood_life_v1.json) | Opportunity windows use integer days. `morning.1`, `morning.3` and `late.roster` distinguish roster slots, not timestamps. Housing, contacts and promises have existing owners. | M: morning/evening elapsed time, sleeping hours, actor availability and business opening hours. Keep historical slot keys and windows unchanged. |
| I — [choice resolution](../choice_engine.py#L35) | Reassesses eligibility, applies an injected adapter and records one terminal life choice. | P: reuse the pattern through a new explicit event adapter. Existing life events are not a generic encounter protocol. |
| I/T — [heat/responses](../legal_engine.py#L17), [court](../legal_engine.py#L101), [evidence](../consequence_engine.py#L73), [legal validation](../legal_state.py#L49) | Bounded heat, job-source evidence, responses, court/custody records. Accelerated sentences resolve without a physical prison stay. | M: non-job evidence sources, independent institutional cases, served-time schedules and profession/credential rules. Do not manufacture a job to legalize a story crime. |
| I — [NPC policies](../npc_actions.py#L16), [relations](../relationship_engine.py#L16) | Legacy named NPC actions, bounded player relations and memories; no general actor-to-actor knowledge network. | M: directed claims, beliefs, institutional inboxes, NPC positions and bounded rumor transmission. No automatic Vale-to-Gordon or Night Watch-to-Batman mapping. |
| I — [economy](../city_economy.py), [strategy](../city_strategy.py), [territory](../territory.py) | Original factions have existing economic and territorial authority. | P: incident effects call those owners with causal receipts. A rogue, patrol or small crew has no automatic district, treasury or warfare tick. |
| I/T — [save validation](../career_state.py#L62), [atomic persistence](../career_persistence.py#L64), [mobility validation](../mobility_state.py#L8) | Outer save version 1, historical migrations, atomic publication and recoverable backups. The Mission 015 repair validates original integer metadata before projection. | P: future optional content/version adoption, pinned definitions and a reader compatibility gate; no schema change in this mission. |
| A/P/M — independent night city | Independence, deterministic replay and meaningful civilian agency are approved direction. | All nighttime scheduling, new DC actors, rumor channels, institutional calendars and encounter consequences below are proposed and absent at runtime. |

**Finding:** there is no genuine clock. Jobs and journeys resolve immediately;
TU measures a daily travel budget, not minutes. Reading a location, saving or
loading is not a passage of time. `wait` performs the actual next-day pipeline
and resets allowances through their existing owners. It must not be repurposed
silently as an hours-only operation. Existing custody can pass through sentence
and release within one resolution; a prison map point does not implement hours
served, visitation or lawful physical release.

## 2. Compatible future time model — proposed, staged

### Stage 0: incident timing without a global clock

The smallest future slice gives a world incident an authored **night occurrence
tag** and a day-based aftermath. One real day transition can record an overnight
incident and expose its next-day evidence. The tag describes that incident; it
does not put the entire city or the player at a simulated hour. Existing jobs,
transit, courts and daily life retain their rules. No new period command, sleep
requirement, action refresh, TU conversion or real-time timer is needed.

The incident runs independently of proximity and discovery. Unknown incidents
can resolve without the player. Enrolling in a future optional feature starts
its history from an explicit boundary; it cannot recreate old nights or charge
backdated expenses. A notice must say whether it describes an overnight event,
an open current offer or completed aftermath, rather than offering impossible
retroactive intervention.

### Stage 1: separately approved coarse Day/Night model

If later gameplay needs actual night presence, adopt a versioned global two-period
model, not a full minute clock. This requires a separate implementation contract.

| Proposed transition | Budgets and authoritative daily effects |
| --- | --- |
| Day N to Night N | Zero action/TU refresh. No daily economy, rent, investigation, custody or faction tick. Process each eligible phase event once. |
| Night N to Day N+1 | Run the real daily pipeline once; existing owners reset three actions and 18 TU exactly once. Process new phase events in an approved order. |
| Existing `wait` | Preserve one whole logical day's advance, retaining period. Process skipped phases chronologically; do not grant retroactive choices or penalize an unknown offer. Exact event/daily ordering needs approval. |
| Read/save/load/repeated transition request | No refresh, timer advancement, resampling, acknowledgment or additional daily processing. Duplicate transition identity cannot settle twice. |

A logical day starts with its Day period. Budgets span Day and Night together;
night is not an extra set of three actions. Period advance should be an explicit
safe option, available even at zero cash/actions/TU, but advances world events
and disclosed commitments. No wall-clock waiting or paid acceleration. TU must
remain effort/routing cost; do not infer time from old travel or spend gameplay
actions merely to inspect a clock. New period windows belong to new definitions;
M015 roster names must not acquire new historical restrictions.

**Compatibility decision:** a time sidecar alone is unsafe if an old version-1
reader silently retains unknown fields while ignoring clock semantics. Recommend
an explicit future reader gate for clock-adopted saves (for example outer version
2), while the new reader continues loading historical versions. The exact gate
requires approval and inspection of all old-reader paths; do not bump navigation
rules just to encode time. No gate/schema is added now. Stage 0 also needs normal
optional-state validation and defined old-reader behavior before implementation.

## 3. Major dramatic incident timing — proposed 80/20 target

The denominator is **eligible major dramatic rogue, vigilante and crisis
incidents**. It excludes routine crime, patrols, investigations, ordinary jobs,
civilian life, medical calls, court administration and all events in aggregate.
An 80/20 target is a long-run content/scheduling aim, never a universal curfew.

Proposed default: weight flexible eligible major incidents 4 for night and 1 for
day, using a pinned deterministic per-source draw. First respect event type,
location access, actor continuity/availability and institutional constraints.
Authored daytime crises, Duke's daytime role, hearings and public civic events
override the generic weighting. A fixed daytime event must not be moved to night
to satisfy a quota. No reroll-until-night, guaranteed daily crisis, or exact four
night events in every five. Suppressed/capacity-limited events do not become
player debt or repeatedly reroll on inspection.

Future balance reports must distinguish eligible, selected, scheduled, suppressed
and occurred counts, list exceptions, seeds and content pins, and state the
denominator. Short samples need not hit 80%. Ordinary city activity can have a
very different distribution. During Stage 0 the tag is descriptive metadata,
not evidence that the player can currently take a night shift.

## 4. Continuity-aware Bat-Family roles — all operational policy proposed

Primary publisher pages below support narrow identity/role anchors, not a merged
continuity or a final active roster. Select actor, mantle, era, availability and
relationship state in content. Never infer alliances from related-character
cards or choose contradictory biographies because two sources mention a mantle.

| Actor / sourced anchor | Proposed operation and limits |
| --- | --- |
| [Batman / Bruce Wayne](https://www.dc.com/characters/batman) — detective, training and technology | Mostly nighttime field work, with dangerous daytime cases possible. Finite attention and commitments. Needs observation, evidence, a witness, a real surveillance channel or delivered information. A criminal career is not an automatic personal Batman pursuit. |
| [Nightwing / Dick Grayson](https://www.dc.com/characters/nightwing), including [Blüdhaven duties](https://www.dc.com/graphic-novels/nightwing-1996/nightwing-a-knight-in-bludhaven) | Independent objectives and home responsibilities. A Gotham assignment requires a cause and capacity; not a spare Batman permanently waiting nearby. Mostly night field work. |
| [Robin mantle](https://www.dc.com/characters/robin) — several distinct holders; the profile foregrounds Damian | Pin the current holder and era. Historical Robins are not duplicated as simultaneously current Robin. Agency, training and constraints differ; no automatic availability, fixed ordinal or universally obedient child sidekick. |
| [Batgirl](https://www.dc.com/characters/batgirl) — Barbara's history is one mantle account | Select Barbara, Cassandra, Stephanie or another specifically sourced version. Field work mostly night, daytime obligations matter. Mantle identity cannot be substituted silently in the middle of an incident. |
| [Red Hood / Jason Todd](https://www.dc.com/characters/red-hood) — divergent methods and changing family relations | Pin era-specific limits and cooperation. Neither universal executioner nor automatically obedient deputy. His intervention may conflict with another actor's objective; no assumed player friendship or immunity. |
| [Oracle / Barbara Gordon](https://www.dc.com/blog/2025/03/05/in-what-comic-did-barbara-gordon-officially-become-oracle) — information role distinct from Batgirl history | One Barbara actor with versioned roles, not two physical people. Receives finite, attributable information; no access to all world truth or automatic successful authentication. An information lead is not a personal Batman meeting. |
| [Duke Thomas / The Signal](https://www.dc.com/characters/signal) — daytime protector, light-related capabilities | Explicit daytime field exception. Pin power scope, training and commitments; no interpretation of light perception as citywide omniscience. Useful daylight assistance remains optional and capacity-limited. |
| Alfred Pennyworth — guardian/support role in the Batman profile; [City of Bane account](https://www.dc.com/blog/2021/02/25/the-black-knights-meet-the-black-heroes-of-gotham-city) includes his death | Support only if alive and available in the selected era. Do not resurrect him or promise free medical treatment from his name. No automatic field patrol, player employment or unrestricted access to Wayne facilities. |
| [Cassandra Cain](https://www.dc.com/characters/cassandra-cain) — Batgirl/Orphan roles across versions | Distinct actor and chosen persona, with her own priorities. Specific observation expertise is not mind-reading. No inheritance of a parent's guilt or automatic alliance with every family operation. |
| [Stephanie Brown](https://www.dc.com/characters/stephanie-brown) — Spoiler/Robin/Batgirl history | Select the active role; keep actor identity stable. Local knowledge needs sources. Do not run three independent Stephanie actors or assign her every historical role concurrently. |
| [Batwoman / Kate Kane](https://www.dc.com/characters/batwoman) — independent crimefighter | Independent objectives and methods, predominantly nighttime field work. Family association does not make Bruce her universal commander or authorize sharing every confidential source. |

Identity, life state, custody, injuries (only once such a system exists), off-city
duties, cover, prior commitments and continuity all constrain availability.
Actors may decline, delegate, investigate elsewhere or arrive after an incident.
No roster requires all these people simultaneously; other family members need
their own sourced identity/era review. Relationships can be unknown to the player.

Batman must be an overwhelming possible survival threat to an ordinary goon,
not an early damage-scaled boss or a mandatory patron for reform. Escaping one
incident does not defeat or recruit him. A public tip goes to an actual channel;
receipt, credibility review, response and personal contact are separate facts.
Neither a Bat-Signal nor an Oracle message guarantees access or rescue.

## 5. Law and civic institutions operate independently — proposed

Use generic institution mechanics with selected Gotham content. Current Civic
Police, Detective Vale and Night Watch remain their original saved identities;
none is retrospectively Gordon, GCPD or Batman. A core faction meter must not
become a universal institutional knowledge or conviction meter.

| Institution / actor | Independent activity and access policy |
| --- | --- |
| GCPD patrol officers | 24/7 response and patrol, finite staffing, local observations and recorded dispatch. Coverage varies by district/incident, not a universal nighttime absence. A report starts a lead; it is not proof. |
| GCPD detectives | Independently investigate assigned evidence, interview and corroborate; capacity and delay have causal records. No access to undiscovered world secrets just because a case exists. |
| [James Gordon](https://www.dc.com/characters/james-gordon) | Commissioner/ally in the cited portrayal, subject to selected era and office. Policies, priorities and exceptional liaison differ from personally handling every case. Not an omniscient route from all police to Batman. |
| [Renee Montoya](https://www.dc.com/characters/renee-montoya), [Harvey Bullock](https://www.dc.com/characters/harvey-bullock) | Pin Montoya's police/Question phase and actual office; do not clone roles. Bullock's judgment and methods require the chosen portrayal, not a blanket corrupt/good flag. Both need actual case knowledge. |
| Prosecutors | Review attributable evidence and decide allegations/charges under authored fictional rules and independent capacity. No automatic conviction from high heat or faction affiliation. Original personnel are sufficient. |
| Defense attorneys | Offer understandable terms, contest evidence, advise or represent within authorized access. Affordable/public support alternatives must remain; no paid-only path out of an ordinary legal problem. |
| Judges and courts | Independent decisions with recorded reasons; ordinary hearings/administration predominantly daytime. Authored emergency/on-call proceedings can differ. No real-world jurisdiction or legal advice is implied. |
| Corrections | 24/7 custody and safety operations; administrative release/visits have separate permissions. Sentence, custody, transfer and release are distinct proposed facts. A navigation gate is not a release order; no confinement without a finite recovery policy. |
| Emergency responders | 24/7 calls with local capacity, safe handoffs and documented response. Requesting aid need not cost money; no guarantee of instant arrival or teleport. Medical treatment mechanics are a missing dependency. |
| Social services/community organizations | Daytime offices plus authored outreach/crisis coverage; referrals, shelter, reentry and practical help independent of vigilante approval. Civilian institutions must not all be secret criminal fronts. |
| Journalists | Seek sources, corroborate, publish/withhold and protect confidentiality. Reporting affects informed audiences through actual publication, not immediate global reputation. Rumor and verified reporting remain distinct. |
| Civilian witnesses | Partial observations, mistaken inference, reluctance and voluntary testimony. Witnessing is not the same as filing a report; a report is not automatically accepted evidence or a criminal record. |

Keep **observation, allegation, investigation, evidence, arrest, charge,
conviction and sentence** causally distinct. This is a graph of authorized facts,
not a universal fixed sequence: an emergency arrest can precede a charging
decision in authored rules. A later dismissal must not erase the arrest's history
or leave custody flags stuck. Evidence references its source, acquisition and
case; allegations can be false. Membership, proximity, appearance, distress or
refusal alone cannot prove a crime. Arkham placement is not a generic poverty,
disability or high-heat penalty.

The existing accelerated legal flow is not this future model. Non-job player
crimes must wait for a real evidence-source adapter and compatible validation;
no fake courier attempt or invented witness. A future story may expose an
institution's misconduct only through attributable authored acts. Existing law
costs, heat tiers and case outcomes remain unchanged until explicitly amended.
Harvey Dent cannot be assumed both current district attorney and Two-Face boss
without an approved era/story explanation.

## 6. Meaningful justice, civilian and reform paths — proposed

These careers work without Batman's permission, favor or personal involvement.
Access depends on lawful credentials/terms where relevant, not a hidden vigilante
approval score. Neither cooperation nor reform instantly expunges a record or
guarantees employment. Do not prematurely implement probation, parole or undercover
work as narrative labels.

| Path | Meaningful choice | Persistent, observable consequence and alternative |
| --- | --- | --- |
| Community protection | Share a corroborated warning, accompany a consenting neighbor, or protect a source's privacy. | Actual recipients change trust/preparation; disclosure may close a confidential lead. Public services remain available without joining a patrol. |
| Legal employment/public service | Keep a shift or negotiate release to meet another obligation. | Wages, reference and future shifts reflect the actual promise. Credentials constrain skilled roles; nearby legitimate work remains a baseline. |
| Witness cooperation | Give what was observed, distinguish uncertainty, decline or seek advice. | Investigation receives a sourced statement, not automatic conviction; future contact and confidentiality consequences follow actual disclosure. No compulsory dangerous confrontation. |
| Investigation/journalism | Verify before publication versus delay or decline a weak claim. | Credibility, source trust and follow-up access change for informed actors. Correction can repair an error without rewriting the original publication. |
| Emergency assistance | Request professionals, offer permitted practical help or withdraw from danger. | A credible referral or safe handoff affects a local outcome/reference. No instant clinical credentials, free health effect or mandatory heroics. |
| Neighborhood organizing | Fund/attend a local effort versus spend time on personal income. | Bounded participation changes a real local service/relationship and a later opportunity; no automatic district capture or limitless donation rewards. |
| Rehabilitation/reentry support | Accept a voluntary plan, disclose relevant constraints or negotiate terms. | Kept appointments/obligations support later references and housing/work access. Missed known commitments have bounded recovery, not permanent exclusion. |
| Nonviolent conflict resolution | Mediate, document a dispute, refer to a neutral party or decline responsibility. | A particular agreement/reference can persist or fail; no magical universal hostility reset or compelled forgiveness. |

Existing `cooperate` is a case response, not an implemented witness-protection
career. Existing contact memories can inform a pattern but do not supply these
professions, institutions or directed knowledge. Original workers, neighbors and
professionals should carry most ordinary encounters; licensed heroes are not
needed to make these choices worthwhile.

## 7. World occurrence and player knowledge — proposed seven-stage lifecycle

| Stage | Authority and invariant |
| --- | --- |
| 1. Eligibility | Pinned definition/variant, actual causal prerequisite, day/phase, place, cooldown, capacity and resources. Deterministic sorted IDs; player location is a condition only where explicitly necessary. |
| 2. Independent occurrence | Record one stable world instance and actual cause. May happen while the player is elsewhere, detained, unaware or refusing; world truth is independent of the player journal. |
| 3. Evidence/rumor transmission | Create bounded observations/claims, with observer, audience, source, channel, confidence, availability and expiry/retraction. A false claim need not map to a true fact. No automatic GCPD-to-Gordon-to-Oracle-to-Batman broadcast. |
| 4. Discovery | Actual delivery/observation unlocks only what that channel supports. Read-only views neither transmit nor acknowledge. Debug world snapshots are not an in-fiction knowledge API. |
| 5. Involvement eligibility | Recheck location, access, remaining window, consent, role, three-action and 18-TU budgets, real funding and current actor availability. No retroactive consent, teleport or forced encounter. |
| 6. Resolution | World and player outcomes may differ. Revalidate, settle once through authoritative adapters, and record independent intervention or nonparticipation accurately. |
| 7. Persistent consequences | Effect identity, cause, before/after values, informed audiences, resources and follow-up eligibility. Repeated requests/load/phase processing cannot repeat the effect. |

Suggested instance identity uses definition/version + actual source/cycle + pack,
not event-list length or a newly generated ID per menu visit. Private scheduling
can key SHA-256 on seed, rules/content pin, source and cycle; never Python's
process-randomized `hash`, dictionary insertion order, global job RNG or wall time.
Pin the selected result once. Source uniqueness, per-actor capacity, bounded
cooldowns and a deterministic conflict order prevent duplicate or incompatible
episodes. A rumor about one source does not mint another source/reward.

Transmission has bounded hops, delivery count and expiration; confidence is not
an oracle's truth percentage. NPCs act on their received beliefs, can be mistaken,
and need a new cause to correct them. No real-time or online service is required.
Confidential sharing can be refused; absent permission cannot become global
reputation, a police case or a new identity reveal. Public claims can have wider
audiences only through a recorded public channel.

Success, partial success, refusal, failure, betrayal, being cheated, outside
intervention and independent world outcomes require distinct terminal facts.
**Missed unknown** means no delivered opportunity and no blame. **Ignored known**
means a delivered offer expired, not a broken promise unless explicitly accepted.
**Refused** requires an actual decision. Betrayal requires a real prior commitment
and an actor that learned of the act. An autonomous intervention may resolve the
world problem without falsely crediting or punishing the player.

Relationship effects target actual informed actors; faction/cash/territory/legal
effects call their owners with causal references. Never directly edit a district
or invent a treasury to fund a scene. New unsupported effects reject before any
world, allowance or RNG change. Exactly-once keys should include instance, stage,
selection and effect identity; definition migration must not reopen settled stages.

Example: an overnight shop alarm occurs; a shopkeeper reports a suspected break-in.
The claim reaches a local notice/contact, then a player who may verify it. Police
receive information only through a real report. Batman receives none unless a
separate credible channel reaches him and he chooses to investigate. An authored
false alarm must not fabricate a player offense. Daytime evidence/support can
matter without any hero appearing.

## 8. Night risk, daylight value and recovery — proposed

Night should be more dangerous **on average in eligible contexts**, not universally
lethal, empty, mandatory or more profitable. Risks need disclosed cues, bounded
outcomes and avoidance before commitment. No combat, injury or mortality system
is implied merely by writing a dangerous scene.

| Area | Proposed night variation | Daylight value / safeguard |
| --- | --- | --- |
| Criminal activity | Some covert operations and major incidents favor night; ordinary crime can happen anytime. | Daytime work, planning and disputes remain meaningful; night premiums cannot be mandatory to afford baseline life. |
| Witnesses | Fewer pedestrians in some areas; residents, workers and authored cameras may still observe. | Day offers interviews and public corroboration. Darkness never erases every witness or existing evidence. |
| Patrols | Local coverage/dispatch varies with staffing and events, not universal police disappearance. | Police operate 24/7. Daylight is not immunity; night is not automatic arrest. |
| Mobility | Future authored service schedules/closures require versioned route and return previews for the projected period. | Current bus/rail/ferry/monorail rules remain unchanged. No silent last-service trap, time-cost conversion or TU refresh. |
| Civilian vulnerability | Specific hazards affect workers/residents with agency, social networks and access to aid. | Safe public activity continues. Do not make poverty, identity or being outdoors a guaranteed victim flag. |
| Business access | Separate public frontage, physical entry permission and whether a service is open. | Housing remains reachable under valid access; ordinary services have disclosed alternatives. Institution entry/exit still requires actual authority. |
| Emergency response | Capacity may be strained by an actual incident, with a bounded authored handoff. | Aid requests remain possible 24/7 without a compulsory fee or vigilante favor. No endless real-time wait or guaranteed instant rescue. |
| Vigilantes | Most field incidents favor night, subject to actual availability and credible knowledge. | Signal and justified emergencies support daytime encounters; no universal all-night omniscient patrol. |
| Lawful work | Optional disclosed night roles, credentials and finite funding; not every shift is a crime. | Court/admin appointments, wages, community contacts, reporting and ordinary life give independent reasons to use daylight. |

Before a voluntary departure, disclose known access, budget and return risks;
hidden changes charge only actual travel under existing mobility rules. A failed
offer cannot consume an action or strand the player through a narrative teleport.
At zero cash/TU retain safe local support, save, decline and real day advance.
Any future timed closure must have a finite reopening/assistance path, not an
ever-renewed blockade. Use current route owners; safe assistance is not a free
travel reward or restriction bypass. Restricted institutions still need lawful
release/access, not a story exit button that cancels custody.

Ordinary setbacks should affect a particular opportunity, relationship, debt or
reference, with recovery. Never gate housing, all legal work, all contacts or day
advancement behind one rogue meeting. An ignored unknown event creates no debt.
Difficulty controls information/support and optional stakes, not unavoidable
death; irreversible career endings require separate explicit approval.

## 9. Smallest future vertical slice and acceptance contract — proposed

Recommend **one original overnight shop-alarm incident with a daylight aftermath**,
building the same generic source/knowledge lifecycle needed by the minor-crew
verification proposal. These are alternatives for a first slice, not two mandatory
systems to implement together. Prefer the original incident first: it needs no
continuity choice or direct rogue/hero appearance and proves the night tag without
claiming a city clock. A later Killer Moth pack can reuse the reviewed interface.

Use one existing public store frontage after atlas/access review, one original
contact and a bounded day window after explicit adoption. World occurrence and
expiry must not depend on inspection. Offer verify, provide safe lawful assistance,
refuse or allow a known offer to lapse. One funded fee/reference and one changed
next-day lead give observable consequences; no endless verification reward.
Keep a branch for incomplete/false information and partial resolution. Do not
add a player crime, institutional custody, employment profession, health, combat,
organization membership or personal Batman encounter to this slice.

| Future acceptance gate | Required evidence after separate authorization |
| --- | --- |
| Historical compatibility | All current 336 tests; historical fixtures and legal/faction outcomes unchanged with the feature absent. Explicit adoption, no backdated events, pinned content and defined old-reader rejection/handling. |
| Independent world / knowledge | Same incident source/day when player is absent, unaware or refuses; discovery differs appropriately. No debug truth leak, omniscient reputation, automatic police case or guaranteed Batman response. |
| Decisions / consequences | Verify, help, refuse and known-lapse have different sourced follow-up eligibility; unknown expiry causes no blame. Actual resources fund rewards. Partial/false-report outcomes retain recovery. |
| Budgets / atomicity | Three gameplay actions and 18 TU remain. Rejected/duplicate commands, unknown locations, closed routes, expired offers and insufficient resources leave world/RNG unchanged. No automatic movement or extra daily tick. |
| Replay / exactly once | Fresh-process and insertion-order tests; actual disk resume at every stage; same instance/effects after repeated reads, loads and daily calls. Save-failure tests preserve the last good career. |
| Timing honesty | Overnight tag is event metadata only. No new morning restrictions, clock UI, periodic refresh or altered legacy `wait`. Flexible-pool weights are tested separately from hard phase constraints; no forced exact short-run 80/20 balance. |
| Recovery / careers | Zero cash/TU/actions, missed window, custody, unavailable contact and a false rumor preserve ordinary work/support, legal responses, safe location and day advance. Meaningful lawful play succeeds with no hero involvement. |
| Long run / repetition | Multiple seeds and repeated source cycles show bounded claims, cooldowns and funding. Report repeated content honestly; do not spawn a crisis nightly to manufacture engagement. |

Manual future scenario: Day 1 earn lawful income and preserve a contact's privacy;
advance the day. An independently scheduled overnight alarm leaves a next-day
claim. Day 2 choose verification over a competing paid task; a false detail is
corrected, granting a bounded reference rather than invented guilt. Save/resume.
Day 3 use the changed follow-up or decline it, then continue ordinary life. A
parallel unaware career gets the same world incident without a missed-quest fine.
This is a proposed acceptance walkthrough, **not an executed gameplay test**.

New decisions concern trust in information, opportunity costs and who receives a
report. Consequences persist as provenance, a relationship/reference and altered
follow-up access. Variety comes from actual source truth, discovery channel,
availability and competing commitments, rather than larger reward numbers.
The first slice remains mechanically shallow: one contact, short windows and no
embodied night movement, institutional casework or actor schedule. Repeated
verify/collect loops are a grind risk; cap one settlement per cause and introduce
different consequences before increasing encounter frequency.

## 10. Decisions, sequencing and remaining risks

| Decision needing approval | Recommendation / reason |
| --- | --- |
| Continuity/era and active identities | Approve a small manifest before DC-specific content. Preserve Alfred's selected life state, Robin/Batgirl holders and Barbara's role without combining incompatible eras. |
| First implementation scope | Approve one original night-tagged incident, knowledge projection and explicit choice adapter; defer direct rogues and Bat-Family. No implementation authorized here. |
| Clock semantics / old-reader gate | Defer global Day/Night until a real gameplay need. Approve skip ordering, day boundaries, adoption and reader rejection before changing saves. A clock sidecar ignored by old readers is unsafe. |
| Scheduler order / ownership | Incident phase after daily life is a proposal. Do not alter previous legal/faction outcomes; cross-system effects require explicit owner adapters and ordering tests. |
| Information / privacy | Approve claim schema, visibility, delivery/correction rules, finite propagation and capacity. Default debug snapshots are unsuitable as player knowledge views. |
| Stakes / recovery | Approve bounded fees, funding, cooldowns, finite safe alternatives and irreversible-ending policy; no mandatory nightly income or hero approval. |
| Future legal expansion | Separate non-job evidence and institutional source contracts before any new player crime or formal accusation path. No implicit probation/parole implementation. |

Sequence: preserve repair and design commits; review the first-slice contract;
implement only after a new instruction; validate its lifecycle and historical
compatibility; then consider minor-crew content. Add the non-job legal adapter
before criminal event effects. A coarse clock, institutional schedules and broader
rogue/Bat-Family incidents are later separate approvals, not prerequisites that
justify a large rewrite now. No new milestone number is assigned here.

**Risk assessment:** no new P0/P1 defect was confirmed in the bounded metadata
repair audit. That is not a certification of unimplemented narrative systems.
Remaining P2 concerns include whole-history copy/validation scaling, bounded
route search and limited two-station pilot depth. Future design hazards include
old readers ignoring time semantics, information leaks, duplicated phase effects,
unfunded rewards and unsafe timed return paths; they are gates, not current
implemented defects. Combat/health, general schedules, directed NPC knowledge,
new institutional cases and profession mechanics are missing dependencies.
Historical malformed dictionaries are not supported service inputs; load/save
validation rejects boolean metadata, while some reducers may normalize a corrupt
in-memory counter before final validation. A universal input-validation policy
would be a separate hardening decision, not a navigation rewrite in this repair.

## 11. Verification provenance and limitations

Source seams above were inspected, including real pipeline ordering, roster keys,
save gates, legal resolution and mobility ownership. Publisher sources support
only the stated character anchors; exact continuity and editions remain open.
No source establishes the proposed schedule, 80/20 policy or recruitment rules.
No real-world law, diagnosis or third-party dialogue is reproduced as game canon.

The separate repair commit is `03e6cb5cfa667077b15274fb0ef4b83682ffb88a`.
Executed commands/results for that tested source:

| Command | Actual result |
| --- | --- |
| `python -B -m unittest discover -s tests -p 'test_mobility*.py' -q` | 53 passed, 5.774 seconds. |
| `python -B -m unittest discover -s tests -q` | 336 passed, 49.656 seconds. |
| `python -B mobility_campaigns.py --days 30 --seeds 17 42 --resume-every 1` | Both campaigns completed; equality at every command/day and 30 real daily disk resumes per seed. 6.188 / 5.875 seconds. |

Unchanged day-31 world SHA-256 values:

- Seed 17: `659df819879a25fc3d7db2939fffbd0b7d34101a922f4ec61c650e87c8f0a1e3`.
- Seed 42: `afe4aac5a636b8aafbfb3acfbf0d41f7c09306c64b3ac7bd6de282335bfb851d`.

These results validate the mobility repair and existing engine, not this proposed
clock, rumor, law, rogue or Bat-Family design. No narrative runtime/test was
added. The documentation commit preserves this proposal and the expanded Rogue
Encounters draft separately. No push, new PR, merge or M015 branch change is
authorized; PR #15 must remain open and unchanged.

Documentation checks executed before preservation: 27 registry rows, all 25
explicitly requested names, 61 local links with existing targets and in-range
source line references, balanced fences and no trailing whitespace. This is a
local structural/link check, not a third-party Markdown linter or a live check
of every external URL. Read-only GitHub verification found PR #15 still OPEN at
`3251381177bf11c0b07cd940329ebd0be3a7bb52`, unchanged from the initial check.

## 12. Mission 016 — implemented independent Night Shift subset

The approved baseline correction supersedes the historical PR restrictions:
PRs #15 and #16 are merged, remote `master` is `37fc4b5`, and the new local
branch is `feature/m017-night-shift-event`. Neither earlier branch/PR is changed.
Current executed evidence is in [validation](M017_NIGHT_SHIFT_VALIDATION.md).
The rest of this document's global clock, 80/20 scheduling policy, licensed
actors, institutional careers and broader rogue chains remain **PROPOSED**.

### Implemented lifecycle and definitions

[`night_shift_v1.json`](../content/night_shift_v1.json) is one original definition
pack. [`incident_content.py`](../incident_content.py) validates it and pins its
sorted-JSON SHA-256. [`world_incidents.py`](../world_incidents.py) separates a pure
versioned transition reducer from service/day publication and player projections.
[`incident_state.py`](../incident_state.py) reconstructs the state from explicit
enrollment and transitions, checks exact committed commands/costs/results and
cross-checks payments/memories. This is a reusable lifecycle seam with one bound
adapter, not an arbitrary mission scripting language or general NPC scheduler.

| Stage | Implemented cause, identity and boundary |
| --- | --- |
| Eligibility | Active M015 life plus explicit zero-cost `enable_incidents`. Adds one original owner, Ada Quinn, to the existing contact authority. No affiliation to Harley or other DC actors; no old-contact personality change. |
| Occurrence | Source is definition + enrollment day; instance is that source's alarm. SHA-256 over seed, content pin and source chooses one of three causes and occurrence one/two future days later. No global RNG or insertion-order dependence. |
| Information | Next day, owner inspection establishes the cause; the desk receives only an alarm report. These are separate recipient facts. No player knowledge is added. |
| Discovery | Explicit `discover_incident`: read p032's local public notice, or ask Tess at n13 after an actual kept-promise reference. No guaranteed remote delivery, proximity teleport, true-cause disclosure or acknowledgment by inspection. |
| Participation eligibility | Shared choice assessment on current day/location/access, freedom, known stage, prior acceptance and three-action budget. Travel remains explicit under existing navigation/mobility. |
| Decision/nonparticipation | Accept/inspect, help, disclose observed findings, withhold optional statement, refuse, let a known offer lapse, or remain unaware. Each stage settles once. |
| Independent resolution | Four days after occurrence, owner completes review/reopening and actually supplies that review to the Civic Police desk. Does not require player discovery, work or a police case. |
| Aftermath | Shop safety status, accepted-work outcome, actual owner memories, scoped desk receipt and an earned follow-up persist. After all stage windows close/settle, terminal state freezes; no respawn or daily incident-log growth. |

The three hidden causes are a real break-in with unidentified offender, faulty
alarm contact, or authorized delivery using the wrong entrance. Nothing implies
the player committed the incident. The initial public claim confirms an alarm
only. World truth lives in debug/save state; the player projection reveals the
cause only after actual complete inspection. Raw developer snapshots are not
the player journal. New world-only event messages/results never disclose that
hidden cause; inspection feedback is based on the player's acquired evidence.

There is still no clock: `overnight` is occurrence metadata. The existing daily
pipeline is unchanged through daily life, followed by one idempotent incident
phase. Skipped legacy clock days can catch up without retroactive offers.
Neither 80/20 weighting nor institutional hours were introduced.

### Choices, commitments and observable consequences

| Player act | Cost / effect | Distinct persistent future |
| --- | --- | --- |
| Accept inspection | One action; disclosed $12/$6/$0 agreement. | Work stage becomes eligible from evidence day. Acceptance is not automatic delivery or knowledge. |
| Inspect first evidence day | One action, $12, owner standing +2. True cause learned and delivered to owner. | Complete private work can open a private-records shift; optional accurate disclosure can instead open statement review. |
| Inspect second evidence day | One action, $6, owner standing unchanged; limited observations only. | May submit an honestly incomplete statement for a later review; never learns the hidden cause by guessing. |
| Inspect third evidence day | One action, $0, owner standing -1. No useful findings. | No earned event follow-up; ordinary life remains available. |
| Leave accepted work unfinished | One deadline reaction, $0, owner standing -1. | Recorded failed commitment, not unknown/refused work. No extra fine or fabricated guilt. |
| Help secure shop | One action, no immediate pay, owner standing +2. | Different shop reopening status and safety-preparation follow-up. |
| Disclose actual findings | One action, owner standing +1 after desk acknowledgment. | Desk knows only the complete/limited statement actually supplied; scoped statement-review access, no private police-case access. |
| Lawfully withhold optional statement | Zero actions, no guilt or standing penalty. | Desk does not acquire player findings; a complete private reference remains useful. Later independent owner review is a different source. |
| Refuse / ignored known / missed unknown | Refusal zero actions; no reward or promise. | Separate outcome records; no automatic debt, blame, global hostility or career lock. |
| Earned follow-up | Opens day after independent resolution for three days; one action, $8 and owner standing +1. | One safety shift, private-records shift or statement review according to actual prior acts. Never repeats. |

Only player cash is spendable. The finite authored work agreement pays at most
$20 total; there is no new account, currency, treasury, reputation score or
relationship meter. M015 owns Ada's standing/memories; the existing cash ledger
observes the real payment. The incident keeps auditable causal receipts, not a
second balance. An inspection and follow-up have separate effect keys and costs.
Each structured transition records a stable transition ID, source/incident IDs,
before/after world phase and the exact delegated effect IDs. Validation replays
and checks these causal links as well as command arguments and outcomes.
An ordinary lawful career can ignore the whole episode, keep its room and use
the existing work roster. No mandatory commuting, waiting for pay, criminal act,
rogue meeting or vigilante approval was added.

### Persistence and remaining integration limits

The optional `incident_version: 1` state is absent from all non-adopted careers.
Enrollment does not refresh actions/TU, replay old nights or migrate old events.
The outer save schema, original atlas, life and mobility fingerprints are
unchanged. JSON round-trip and current-reader disk resume preserve every stage.
Older executables do not know the phase and are unsupported for advancing
incident-adopted careers; compatibility here is historical saves loading into
the new reader, not a promise of forward-compatible play in old binaries.

No new legal evidence source exists. Civic Police facts are incident-local
records of actual reports/review, not warrants, cases, charges or proof of player
guilt. Owner standing is the existing contact score; statement credibility is
the sourced acknowledgment/reference, not an invented global witness meter.
There is no citywide rumor graph, NPC movement, combat, health, court calendar,
institutional staffing, membership or licensed character behavior.

Meaningful decisions trade limited actions, current wages, information sharing
and different future work. Variety comes from three grounded causes, discovery
channels, evidence age, commitments and disclosure. The single authored event
and fixed performance windows remain shallow; do not increase frequency into
repetitive inspect/collect grinding. A future second original incident should
reuse this seam only after an independent contract review; richer non-job law
and licensed actor content require separate source/continuity approval.

### M017-B discovery provenance contract — specified before implementation

Mission 018 closes the independent audit's discovery-context gap. This contract
was recorded after reproducing the unchanged M017 forged-reference save and
preserving valid original public/contact saves, **before changing validator code**.
It adds read-only proof checks, not another history, save schema, clock or NPC
knowledge system. The existing version-1 definition and emitted records stay pinned.

**Authority:** existing navigation outcomes, contact memories, selected life
choices/promises and their structured events and committed player-command
receipts. Incident replay establishes incident eligibility. A context dictionary
is a claim to check against those sources, not a source that proves itself.
Current cash, standing, location or a later fact cannot establish an earlier fact.
Only canonical fact fields participate in source equality; unrelated optional
metadata remains preserved under the existing additive save contract.

| Historical fact | Required evidence at discovery |
| --- | --- |
| Player location | Latest completed schema-1/schema-2 `travel` outcome before discovery, using `arrived`, not requested destination. It must match its actual `travel`/`journey` command, day and command frame. Earlier public navigation activation may establish an anchor when no later movement exists. Never substitute final `navigation.location_id` or a journey that happened later. |
| Tess reference | An actual Tess `promise_kept` memory with one matching `life_memory` event, a kept promise, its resolving `keep_promise` life choice/event and completed `choose` command, plus the original accepted promise choice/event/command. These must be consistent with the existing life validator and causally ordered before discovery. Standing alone, a forged memory label or `tess_reference: true` is insufficient. |
| Knowledge available then | Only references already earned in completed earlier commands can justify contact discovery. A genuine reference earned later, even on the same logical day, must not be backfilled into earlier knowledge. A false snapshot also cannot deny a reference that already existed. Discovery still grants only the alarm report; cause knowledge remains tied to actual inspection. |
| Public notice | The pinned incident's occurrence day has arrived, and prior incident replay has actually processed occurrence. Its tick must follow same-day `life_day` processing. Local discovery additionally requires the historically proven shop location; a contact reference is not a public-notice bypass. |
| Command ordering | Each supporting command-bound outcome lies inside its own command frame: after the preceding completed command and before its matching receipt. Supporting command IDs and receipts precede discovery; the discovery transition precedes its own receipt. Relevant source days cannot lie in the future. Sorting a contradictory history to make it appear valid is forbidden. |

Day-driven source events may legitimately come from an existing low-level daily
pipeline without a service `wait` receipt; preserve that established batch-tool
behavior. A same-day `life_day` then incident tick is the daily source proof;
do not fabricate a wait command. Player choices and travel, however, already
require their committed service receipts under the current save contracts.

The reference proof follows the existing M015 authority rather than accepting a
second incident-owned reference flag. The existing life validator continues to
validate promise dates, option semantics, memory deltas and unique matching
events. Provenance adds the missing historical identity/order checks and must
not recursively invoke that validator. All indexes/proof facts are ephemeral;
validation must not append, reorder, normalize, initialize or mutate any state.

**Compatibility:** careers without discovery are not asked to invent a discovery
trace, and non-adopted historical careers remain unchanged. Published valid M017
public/contact histories already contain the required source events; no new
field, content fingerprint or schema version is needed. Later travel, later
references and custody changes do not invalidate an earlier valid discovery.
Legacy origin information outside the recorded navigation era is not invented.
If an adopted discovery has no sufficient recorded location/reference source,
reject it clearly as unverifiable/contradictory; do not grant knowledge, silently
erase the encounter or create retroactive source events. A current-position or
boolean fallback would preserve the defect rather than compatibility.

This checks internal consistency with independent domain records. It does not
authenticate a save against coordinated rewriting of all supporting histories,
nor reconstruct every legacy legal/action/access predicate. No general rumor
graph, multi-incident framework or new legal authority is part of this repair.

**Implementation/verification:** M017-B now enforces this contract in
[`incident_state._discovery_sources`](../incident_state.py#L15), using existing
domain records only. All 371 prior tests plus 18 new provenance regressions pass
(389 total); both preserved original public/contact saves round-trip byte-for-byte
and all four recorded mobility/Night Shift campaign hashes are unchanged. See
the appended Mission 018 section of [validation](M017_NIGHT_SHIFT_VALIDATION.md)
for actual commands, red/green evidence and compatibility limits.

## 13. Implemented M018 — The Wrong Notice

Mission 019 authorizes one original neighborhood delivery dispute and reusable
dispatch. It does not authorize the broader law, Bat-Family, clock or rogue systems.
Night Shift retains its definition, content fingerprint, stable IDs, histories
and payouts. Its prior provenance contract above remains in force.

### Lifecycle and authoritative boundaries

After daily life activates, `enable_incident` with
`goon.incident.wrong_notice.v1` explicitly adds `notice_version: 1` and
`wrong_notice`. No retroactive occurrence, expense, action or TU refresh is given.
A hash of seed, content fingerprint and enrollment identity fixes occurrence one
or two **future** day transitions later, the authentic date and a lawful standby
vacancy. This consumes no shared RNG. A local ledger becomes available the next
day; actual delivery is three or four days after occurrence; independent
reconciliation occurs five days after occurrence. No command silently waits.

The game service owns all player mutations. `incident_dispatch` selects an explicit
adapter, publishes transition/effect references and delegates memory/cash changes.
The small shared lifecycle owns stage creation, day guards, progression/expiry,
terminal settlement, receipt shape and choice projection. Adapter reducers own
domain facts only. The same replay validator reconstructs each definition from
its own events. Exactly-once effects cross-check against actual life memories
and the existing cash ledger. There is no parallel journal that proves itself.

### Information contract

| Layer | Implemented authority and scope |
| --- | --- |
| World truth | Seed-pinned authentic delivery day/vacancy; hidden from initial player reports. |
| Source claims | Obsolete printed board notice, Sam's earlier handbill and Nora's authenticated local ledger. Each carries a source, credibility and limitation; neither initial date is authoritative. |
| Audience knowledge | Separate board, tenant group and desk beliefs. The desk initially receives its own ledger only. No police knowledge or broader faction propagation. |
| Transmission | Stable source/recipient/claim/cause/command/day records. Authentic corrections cannot be overwritten by later unchecked claims. A desk notification orders tomorrow's board posting; it never instantly updates tenants. |
| Discovery | Actual p032 board read or conversation with Sam at n13, after occurrence, justified by prior command/travel sources. Sam needs no Tess reference; the original Night Shift Tess gate is unchanged. |
| Player knowledge | Only observed source claims; verification exposes the actual ledger. Independent correction does not rewrite the journal. |
| Independent observations | Nora reviews the board; Sam reports local delivery experience. Their explicit limited observations reach the desk, which issues a public reconciliation circular. No character learns private motives. |
| Receipt of aftermath | At n13 during resolution+1 through resolution+3, `aftermath read` receives the circular. Before that, player reports and service/CLI event/contact views hide unreceived automatic trust reactions and review details. Raw save/debug snapshots retain audit truth. |

### Decisions, costs and consequences

Every source comparison or ledger verification costs one shared action. Refusal
and reading the final circular cost zero; neither pays or refreshes anything.
Travel remains explicit and uses the existing separate 18 TU. Execution rechecks
lawful access, freedom, location, knowledge, dates, prior stages and actions.

| Response | Eligibility and cost | Persistent consequence |
| --- | --- | --- |
| Verify ledger | Discovered, ledger available, n13; 1 action | Player learns authenticated date/vacancy. No money or public correction. |
| Post signed correction | Verified, p032; 1 action | Board corrected only. Nora acknowledges the signed help at her later independent review (+1). |
| Notify desk | Verified and poster observed, n13; 1 action | Nora receives a genuine discrepancy (+1) and orders tomorrow's board correction. Tenants stay uninformed. |
| Warn tenant group | Verified after board/desk help, n13; 1 action | Sam's recipients corrected (+1); no board change or wage. |
| Repeat unchecked notice | Poster observed, ledger not checked, n13; 1 action | Only Sam's group receives the unchecked date. If left unretracted, actual reconciliation disproves it and Sam loses 1 trust; Nora does not learn that conversation. |
| Retract | Previously shared unchecked date, now verified, n13; 1 action | Original recipients receive correction; no trust bonus. Delivery-day harm still persists if too late. |
| Reserve lawful standby slot | Verified vacancy and observed poster, n13; 1 action | Player discloses the error but requests personal priority instead of help; Nora -1. One optional $5 shift opens after resolution, costs 1 action and expires after three days. No crime, automatic wage or faction membership. |
| Refuse / ignore / miss | Free refusal, or no participation | No invented promise, debt, prosecution or lost ordinary career. Delivery and independent reconciliation still happen. |

Delivery-day impact is captured during the day transition, before that day's
player commands. Corrections must arrive before that transition to prevent harm;
later work may still help future understanding but cannot undo a missed delivery.
Resolution distinguishes success, partial, failed, refused, ignored-known,
missed-unknown and selfish reservation. The desk's final correction reaches board
and tenants only then. The state freezes once the bounded follow-up/read windows
close; neither event recurs or grows an endless incident history.

Nora and Sam are original local contacts in the existing daily-life authority,
not the strategic faction NPC roster. No resident inventory losses, legal cases,
global rumors, individual schedules or permanent shop lock are simulated.
See [M018 validation](M018_WRONG_NOTICE_VALIDATION.md) for actual tests, CLI and
save/resume evidence and [content architecture](GOON_CONTENT_ARCHITECTURE.md)
for the internal adapter contract. Broader future proposals remain unimplemented.

## 14. Implemented M019 — bounded institutional knowledge and response

The [institution contract](GOON_INSTITUTIONS_AND_RECOVERY.md) now specifies a
Neighborhood Civilian Desk and GCPD Intake Desk. They receive different explicit
sources, process delayed queues independently, retain contradictory claims and
deliver new response versions through actual local follow-up. They cannot
identify an offender or create a legal case. No Bat-Family, court, care, prison,
global rumor or time-of-day system is added.

An ephemeral adapter reads the actual M017/M018 event history: shop alarm notices,
received owner reports/reviews, Wrong Notice claims, the issued circular and
player observations acquired by real commands. Automatic sources enter only
after explicit M019 adoption. Private observations require a player submission;
withholding is a private choice. Desk replies do not rewrite old incident primary
evidence, update other recipients, or reopen expired incident options.

M019 appends its own stable transmissions/processing/receipts and leaves both
incident definitions, reducers and IDs untouched. Player commands share the
existing three actions; counter travel uses the existing eighteen TU. Documented
corrections can restore that desk's reporting access; assistance is one recorded
correction copy without automatic cash or legal effects. Ordinary work and home
remain viable after refusal, false claims or insufficient records.

See [architecture](GOON_CONTENT_ARCHITECTURE.md) and
[M019 validation](M019_INSTITUTIONAL_RESPONSE_VALIDATION.md) for the implemented
boundaries and executed compatibility/replay evidence.
