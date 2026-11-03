# Gotham: The Goon — Narrative Design Bible

*A Living Gotham Crime RPG*

> Everybody wants to rule Gotham. You're just trying to survive it.

Status: M013.1 design foundation for human review. Runtime baseline: merged M013,
commit `eb931ce`. Working title and DC setting remain subject to future licensing
and title clearance. This is an independent, unofficial prototype without DC or
Warner Bros. endorsement, authorization, or affiliation.

## Authority and feature status

This bible governs creative intent, not implementation authorization. Read it with
[gameplay principles](GOON_GAMEPLAY_PRINCIPLES.md), the
[employer matrix](GOON_FACTION_EMPLOYER_MATRIX.md),
[content architecture](GOON_CONTENT_ARCHITECTURE.md), and the
[proposed M014 contract](M014_COMBAT_DESIGN_CONTRACT.md).

| Label | Meaning |
| --- | --- |
| **Implemented** | Present in M013 executable code and its regression suite. |
| **Endorsed direction** | The user's approved creative direction; delivery, mechanics, and milestone scheduling remain unapproved. |
| **Proposal** | An original design option requiring review before implementation. |
| **Speculative** | A possible later branch, not a dependency or roadmap commitment. |

M013.1 authorizes documentation and minimal documentation branding. It does not
authorize M014 implementation, content migration, a licensed-character content
pack, a repository rename, or a public release. Future approval must name a
bounded milestone and acceptance criteria.

## 1. Core player fantasy

**Endorsed direction:** an ordinary criminal is the protagonist. Famous villains
control access to work, impose dangerous demands, disrupt the city, and sometimes
need people the player cares about. They do not replace the player's agency.
Becoming a supervillain is one possible ambition, never the universal objective.

Success may mean reliable wages, surviving an employer, earning a coworker's
trust, getting a dependent somewhere safe, becoming indispensable, or leaving
crime. A boss ending must carry responsibilities and liabilities rather than
merely larger numbers. Failure should create a recoverable situation or a
clearly signaled ending, not erase hours through an arbitrary surprise.

**Implemented:** one placeholder player, three recruitable factions, two jobs,
district missions, heat, case responses, relationships, and autonomous competition.
There is no selectable career path, employment contract, lieutenant rank, or ending.

## 2. Tone and genre identity

**Endorsed direction:** persistent single-player crime RPG, living-city simulation,
dark workplace comedy, crime drama, and survival. Ordinary concerns remain legible
inside extraordinary danger: a missed wage, a stolen work uniform, a broken heater,
a supervisor who calls an evacuation a scheduling problem.

Humor targets institutions, vanity, exploitation, and the gap between managerial
language and actual risk. Coworkers and civilians have dignity. Injury, poverty,
disability, mental illness, and victimization are not automatic punchlines.
Consequences can outlast a joke; the game must allow a quiet or tragic aftermath.

**Proposal:** short original scenes alternate practical comedy and grounded
consequences. Example, written for this document: a loading-bay worker notices
something moving behind a sealed wall and says, "Put it on the maintenance sheet.
I don't get paid for anything that isn't on the sheet." The player's choices are
to report the hazard, protect the next shift, refuse the job, or exploit the delay.
**Speculative:** psychological or supernatural incidents occasionally make the
worker's mundane explanation inadequate. They are not the default tone of every job.

## 3. Gotham as a living city

**Implemented:** three districts have ownership, wealth, and control. Factions earn
income, pay upkeep, recover, recruit, defend, and expand. These are abstract city
systems, not simulated streets, residents, businesses, or travel.

**Endorsed direction:** Gotham is a place to live as well as a map to exploit.
Civilian employers, infrastructure, housing, transport, and social networks give
criminal choices opportunity costs. A disrupted business affects its workers and
customers as well as faction revenue. Important developments should be visible
through reports, witnesses, changed access, and individual memories.

**Proposal:** author small district situations with several affected parties:
an unpaid night shift, interrupted deliveries, a damaged apartment entrance.
State changes should be bounded and attributable. Do not add a universal
"city morality" score that lets one cash donation erase unrelated harm.

## 4. Character creation and backgrounds

**Implemented:** the player starts as Rookie with cash, heat, and no affiliation.
There is no appearance editor, background selection, skill tree, or character sheet.

**Proposal:** begin with three original backgrounds: repair apprentice, casual
warehouse worker, and courier. Each grants one useful contact or approach, one
obligation, and a different opening information set. None requires violence or
locks a player permanently out of legal work. Names and appearance are separate
from capability. Demographics do not determine criminality or morality.

Background selection changes starting relationships and available approaches,
not just a stat bonus. Cosmetic choices consume no RNG. Existing saves retain
their player identity; adding a background later must not fabricate past events.
Numerical skills and any creation menu require separate implementation approval.

## 5. Criminal employment and advancement

**Implemented:** joining is immediate; courier and collection jobs grant payouts
on success. Those payouts are not a wage contract or guaranteed salary. Repeated
jobs affect reputation and relationships; there is no formal promotion system.

**Endorsed direction:** work has terms: expected duties, pay basis, hazards, refusal
rights, secrecy, equipment responsibility, and advancement criteria. A promotion
changes obligations and influence over other people. It should create decisions
about who receives protection and who absorbs risk.

**Proposal:** a small contract can offer a guaranteed shift payment plus a stated
completion bonus, or a higher but uncertain share. Claims about reliability are
information with a source, not an omniscient UI promise. Offer renegotiation,
refusal, departure, and alternative work; do not make repeated identical shifts
the only route to seeing the next story. Contract completion must settle once.

## 6. Faction recruitment and workplace cultures

**Implemented:** Harbor, Carnival, and Iron use different economic profiles.
Recruitment requirements, employer cultures, and DC organizations are not present.
Affiliation switching is currently rejected.

**Endorsed direction:** employers differ in what they value, what they conceal,
how they reward competence, and what they do when a worker refuses. Employment,
personal allegiance, and criminal affiliation are distinct concepts. A trusted
coworker can matter more than an official superior.

**Proposal:** recruitment tests allow several approaches and explain commitments
before acceptance. The [matrix](GOON_FACTION_EMPLOYER_MATRIX.md) contains DC-facing
proposals, not a replacement mapping for existing saved faction keys. Dangerous
employers may lie, but the game must communicate uncertainty and possible loss.

## 7. Ordinary NPC relationships and personal loyalty

**Implemented:** trust, respect, fear, hostility, and suspicion have bounded scores
and causal histories. Named policies trigger limited support, obstruction, and
investigation. There are no NPC-to-NPC relationship graphs or general personalities.

**Endorsed direction:** coworkers have material needs, preferences, boundaries,
contradictions, and lives beyond serving the player. Personal loyalty is not
identical to employer reputation. Refusal can preserve a friendship while damaging
a career. Different people may interpret the same act differently.

**Proposal:** original draft coworkers, not runtime additions: Tess Navarro is a
repair worker who values dependable pay and refuses avoidable civilian harm;
Cal Mercer is a runner who exaggerates his confidence but keeps records of unpaid
wages. Each needs more than a single trait before content approval. Neither is
adapted from a video narrator's cast. A favor creates a remembered obligation,
not a repeatable affection purchase. Bereavement and abandonment need authored
responses rather than a generic numeric hostility increase.

## 8. Civilian life, finances, housing, and recovery

**Implemented:** cash, job income, mission costs, and cash-limited legal fines.
There are no rent payments, dependents, food needs, housing slots, or health systems.

**Endorsed direction:** ordinary financial pressure gives work meaning without
turning poverty into an unavoidable death spiral. Civilian routes must remain
credible. Recovery offers a zero-cash path and meaningful use of in-game time.

**Proposal:** housing initially provides safety, a contact, or information access;
it should not require a daily login. A lost room opens temporary shelter or a
negotiated alternative. Injury recovery can compete with a paid shift while the
city advances, with effects previewed. Do not require real-time waiting, premium
currency, repetitive chores, or maintaining several survival meters for their own sake.

## 9. Law, courts, incarceration, and rehabilitation

**Implemented:** documented collection cases, heat tiers, legal records, laying
low, cooperation, contest review, acceptance, and accelerated court outcomes.
Unanswered cases resolve automatically. These are simplified game rules.

**Endorsed direction:** legal responses express values and survival choices, not
just the cheapest fine. Informing, reform, restitution, and civilian rebuilding
are valid career directions; they are not present systems. Individual witnesses
know specific facts. Heat alone must not manufacture evidence or universal knowledge.

**Proposal:** future legal episodes connect a witnessed act, a specific allegation,
representation or response, and a persistent result. Imprisonment should contain
bounded choices or explicit time advancement with city consequences. Probation,
parole, warrants, and rehabilitation mechanics require later contracts; this bible
does not add their rules. No real-world legal advice is intended.

## 10. Batman and Bat-family intervention

**Endorsed direction:** early Batman encounters are overwhelming survival threats.
The ordinary worker's objective is usually escape, surrender, protecting someone,
or abandoning an employer's demand. Recognizable competence must survive the
translation into game rules. Do not turn him into a routine high-HP loot source.

**Implemented:** no Batman or Bat-family actors, investigation systems, or encounters.
Night Watch is an existing placeholder, not a silent Batman alias.

**Proposal:** high-threat pressure is signaled through sourced reports and visible
changes before confrontation. Distinct family members would need individual
content policies and knowledge boundaries, not color-swapped statistics.
The [M014 contract](M014_COMBAT_DESIGN_CONTRACT.md) describes only a generic
survival-threat design fixture. Named implementation remains separately gated.

## 11. Rumors, misinformation, and street intelligence

**Implemented:** intelligence reports read actual recorded state. They are not a
rumor system and currently reveal information that a street worker might not know.

**Endorsed direction:** a report can be true, stale, incomplete, mistaken, or
deliberately manipulated. The player can check a source, spend an opportunity to
verify, act despite uncertainty, or pass information onward with consequences.

**Proposal:** separate actual facts from each actor's knowledge and beliefs.
Rumors need source, acquisition day, confidence, subject, and contradictory claims.
The UI identifies uncertainty without revealing hidden truth. Reopening a screen
cannot reroll truth. A wrong rumor should leave a traceable explanation, not
retroactively change the world to punish a choice.

## 12. Major citywide villain events

**Implemented:** feuds and faction operations; no authored citywide villain arcs.

**Proposal:** disruptions create ordinary decisions across several jobs: reject a
shift during an evacuation, help stranded neighbors, move fragile equipment, or
sell a scarce service. Events have entry conditions, stages, affected locations,
bounded economic effects, and an end condition. They persist across saves and
do not require the player to be online at a real-world date.

**Speculative:** theatrical villain campaigns, civic emergencies, or unsettling
phenomena can form later incident packs. Do not recreate an existing comic/game
plot beat for beat or import its dialogue. Missed events should produce a changed
city and later accounts, not permanently lock the only campaign route.

## 13. Long-term paths and endings

**Endorsed direction:** professional henchman, trusted lieutenant, independent
operator, criminal boss, informant, reformed citizen, and tragic casualty are all
valid possibilities. None is implemented or scheduled by this document.

**Proposal:** evaluate an ending from concrete commitments and relationships:
who relies on the player, what obligations remain, how money is earned, who knows
what, and whether departure is possible. Advancement is not one villain ladder.
Leaving an employer need not reset every friendship. A tragic ending requires
clear stakes and an explicit campaign death policy, not an unannounced random roll.

## 14. Replayability and emergent storytelling

**Implemented:** seeded differences, player job/mission/legal choices, and
persisted faction competition. M013 samples show a defensive-profile advantage;
the [campaign report](../M013_SIMULATION_REPORT.md) is evidence, not a balance guarantee.

**Proposal:** vary obligations, available contacts, employer terms, knowledge,
district conditions, and approaches. A repeated delivery should change who it
helps, what is known, or which commitment it threatens, not only the reward.
Bound authored variants so consequences remain understandable and testable.
Procedural text variety alone does not create a new decision.

Original paper scenario, not a playable mission: Tess asks the player to cover a
shift while an employer demands an urgent pickup. Covering her shift preserves
her job but forfeits a bonus; taking the pickup can damage trust; negotiating
help depends on an earlier favor. The changed relationship affects a later safe
contact. Repeat with different wages, source reliability, and city disruption,
then check whether the decision actually changes. Technical/reporting checks
come from [gameplay principles](GOON_GAMEPLAY_PRINCIPLES.md).

## 15. Original content and IP boundaries

Write new workers, dialogue, scenes, jokes, mission structures, and incidents.
DC character names and broad motifs are reference material for a proposed setting,
not project-owned creations. Official character references are linked in the
employer matrix; proposed wages and mechanics are our design inferences, not canon.
Choose and document a continuity before shipping any character content.

Do not reproduce third-party video transcripts, distinctive narrator characters,
jokes, comic panels, copied scripts, ripped models, extracted audio, or voice
imitation assets. No supplied video transcript was used to draft these documents.
Future assets need a provenance record and the applicable permission review.

The title, subtitle, and positioning are working creative choices. This milestone
performs no licensing, trademark, or title-clearance analysis. Distribution,
commercial release, fundraising, and external pitch materials require the
separate rights/legal review mandated by the project. Documentation, executable
readiness, and authorization are separate decisions.
