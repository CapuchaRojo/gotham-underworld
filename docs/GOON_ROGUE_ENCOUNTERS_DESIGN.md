# Gotham: The Goon — Rogue Encounters design foundation

## Status, authority and scope

**Mission 015 preservation update:** this retains the Mission 014 proposal and
extends its research pool to 27 roles. The companion
[Gotham After Dark, law and Bat-Family proposal](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md)
coordinates time, institutions and information flow. Neither document authorizes
implementation or selects a final continuity. The metadata repair is separately
committed at `03e6cb5cfa667077b15274fb0ef4b83682ffb88a`.

**Mission 014 Part B: proposed canonical design document, not implemented
gameplay or an approved continuity pack.** Every presence category, difficulty
band, recruitment policy, organization model, example event, number and future
interface in this document is **proposed** unless explicitly labeled verified
source or existing project contract. The word canon below distinguishes a
campaign's recorded world truth from rumors; it does not claim DC authorization.

The independently rechecked M016-A source is locally preserved at
`0e2162e33bae56d5f28dae0e92b2fa861ab94968` on
`feature/m016a-mobility-pilot`. This document originated as separate, uncommitted
Mission 014 design work and is now preserved in the Mission 015 documentation
commit. No Rogue Encounter command, scheduler, actor,
save field, faction, asset or narrative scene is added to the executable.
PR #15 remains open and unmerged. No push or new PR is authorized.

Use the [narrative bible](GOON_NARRATIVE_DESIGN_BIBLE.md),
[career web](GOON_CRIMINAL_CAREER_WEB.md),
[employer matrix](GOON_FACTION_EMPLOYER_MATRIX.md),
[conditional opportunities](GOON_CONDITIONAL_OPPORTUNITIES.md),
[minor criminal ecosystem](GOON_MINOR_CRIMINAL_ECOSYSTEM.md),
[35-entry rogue registry](GOON_ROGUES_GALLERY_REGISTRY.md),
[content architecture](GOON_CONTENT_ARCHITECTURE.md),
[Joker recruitment contract](GOON_JOKER_RECRUITMENT.md),
[influence/recovery contract](GOON_VILLAIN_INFLUENCE_SYSTEM.md) and
[prologue contract](GOON_PLAYABLE_PROLOGUE_CONTRACT.md). This proposal coordinates
them, not a replacement roster or a duplicate runtime engine. Earlier documents
contain historical pre-M014/M015 wording; the actual source and
[M016-A report](M016_A_IMPLEMENTATION_VALIDATION.md) establish what runs today.

The player is an ordinary worker/criminal/civilian, not a guaranteed villain
collector. Famous actors have their own aims, availability and other commitments.
A complete worthwhile career can avoid every personal rogue encounter, reject
all recruitment and still retain lawful work, home/support and campaign agency.
All scenes and chains below are original proposals; no dialogue, comic panels,
scripts, videos, assets or published plots are reproduced. Rights/distribution
review remains separate from these internal fan-prototype design choices.

## 1. Verified integration inventory

| Existing system / evidence | Verified behavior | Proposed extension boundary |
| --- | --- | --- |
| [Service](../game_service.py#L74) | Named commands, exact string arguments, private candidate, shared three-action allowance; adopted mobility validates before commit. | Encounter accept/resolve/decline must use this boundary. No UI/world-reference mutation or separate transaction manager. |
| [World day/event](../simulation.py#L25), [pipeline](../gameplay.py#L77) | Structured event append; real wait advances legal/investigation/NPC/economic/warfare/court/navigation/life phases. No general rogue scheduler. | One optional idempotent encounter phase after the existing life phase; retain existing ordering and clocks. Its position needs approval before implementation. |
| [Choice engine](../choice_engine.py#L35) | Revalidates an open, eligible option, invokes an injected effect adapter, records one terminal selection and structured life_choice result. | Reuse the assessment/selection pattern. Current event kind and records are life-specific; a small explicit encounter adapter/event family is still needed. |
| [Daily life](../daily_life.py#L172) | Finite rosters/windows, original contacts, observed memories, promises and cash/housing receipts, once per day. | A recurring contact may deliver a sourced lead; do not rewrite an old roster, convert Tess/Cal into a rogue, or require life enrollment for world events. |
| [Relations](../relationship_engine.py#L16) | Bounded trust/respect/fear/hostility/suspicion toward the player; named policies for three legacy NPCs. | New directed actor/contact knowledge and relationships need stable IDs and explicit adapters. There is no general NPC-to-NPC rumor network or personality engine. |
| [NPC actions](../npc_actions.py#L16) | Named support/obstruction/investigation policies and cooldowns; police accelerate documented cases. | Do not insert DC actors into those name checks or interpret existing cooldowns as a universal event scheduler. |
| [Reputation/join](../gameplay.py#L45) | One current faction, immediate join among existing GANGS, reputation changes; switching not implemented. | New organization affiliation/contracts need separate consent/terms. Keep existing saves/faction identifiers and join behavior unchanged. |
| [Economy](../city_economy.py), [strategy](../city_strategy.py), [profiles](../faction_profiles.py), [territory](../territory.py) | Existing original factions have bounded economic/strategic behavior; territorial transfers share an operation. | An individual/minor crew has no automatic treasury/power/district tick. Only an approved adapter can fund contracts or alter a full faction's territory. |
| [Legal jobs](../legal_engine.py#L17), [evidence](../consequence_engine.py#L73), [legal state](../legal_state.py) | Heat, witnessed job evidence, responses/court/custody; pending cases require job-source data. | A rumor, encounter, refusal or affiliation cannot create guilt. A compatible non-job evidence-source adapter is prerequisite for new player crimes, not a fabricated collection job. |
| [Mobility](../mobility.py), [navigation](../navigation.py) | Explicit travel, station gates/closures, 18 TU/day, custody/access enforcement and conditional return quotes. | Events disclose actual location/access/TU/action needs. No teleport, free commute, budget refresh or unrestricted Arkham visit. |
| [Persistence](../career_persistence.py), [career validation](../career_state.py) | Historical migrations, version checks, atomic publication and last-good backup. | Future optional encounter version must pin definitions and validate effects/knowledge/uniqueness. No current schema modification or retrospective encounter history. |

The current engine still has some name-keyed content; it is not fully
content-independent. Reuse its seams without claiming that proposed employment,
rumor, injuries, combat, probation/parole or dynamic rogues already exist.

## 2. Presence, discovery and continuity are separate axes

**All categories here are proposed.** Do not force every rogue into one mutually
exclusive rarity bucket. A core actor can have a hidden operation; a persistent
optional actor can cause a public special event.

| Axis / category | Meaning in a future selected campaign | What it must not imply |
| --- | --- | --- |
| Core world-canon rogue | The selected pack establishes this identity/history and an initial state such as active, imprisoned, away, dead or retired. | Guaranteed local presence, survival, employment or a personal meeting. A dead core actor is not respawned. |
| Persistent optional rogue | If the pack's initialization/causal inclusion permits this actor, persist their identity, resources/commitments and outcomes across days. If absent, remain absent until an approved cause introduces them. | Rerolling presence on every look, a duplicate actor, or an available district-owning faction. |
| Conditional special event | An eligible world cause, actor availability and a recorded schedule/demand produce a bounded episode. | Spawn whenever the player needs XP, nearby spectacle only, real-world holiday/online availability or a guaranteed offer. |
| Deep-hidden encounter | Legitimate evidence/referrals reveal a guarded episode. Several credible clue routes may exist; some careers never discover it. | An arbitrary click/password/grind ritual, mandatory career completion, or punishment for information never delivered. |
| Continuity-specific adaptation | An explicit variant/era changes identity, role, powers, affiliations or availability under pinned content. | A mixed anthology of incompatible biographies, deaths, relationships or powers in one actor. |

Initialization records world truth once. For optional actors, use a pinned seed/
pack decision or a real causal introduction, not player menu order. Initial
presence and discovery probability are different draws/facts. A selected pack
can exclude a character entirely; exclusion is not an unresolved missing quest.

No pack is chosen by this document. Proposed starting default is a reviewed
comics-derived subset with original scenarios, not a claimed official Earth or
an automatic mixture of Arkham games, DCAU, television Gotham and the screen DCU.
The complete 27-row registry is a content research pool, not a simultaneous cast.

## 3. Initial registry — 27 proposed encounter roles

**Canon-anchor column:** conservative paraphrases of publisher sources consulted
November 4, 2026. Profiles/solicitations can cover different eras and are not
proof that every event or relationship occurs in the selected pack. A page's
Related Characters/gallery cards are not alliance evidence. No source grants
endorsement or has been treated as an inspected complete comic script.

**All other columns are proposed:** C = core; P = persistent optional;
E = conditional event presence; H = deep-hidden discovery. Difficulty is the
risk of a particular role, not a character's level. Stable candidate IDs are
content IDs, never new current save keys. Reuse existing registry identities
where applicable; a future actor instance additionally pins its continuity/era.

| Rogue / proposed ID | Source-backed anchor and continuity caution | Proposed presence / visibility | Proposed organization / access | Proposed player role / risk |
| --- | --- | --- | --- | --- |
| Bane — `dc.character.bane.comics_candidate` | [DC profile](https://www.dc.com/characters/bane): strategist, formidable strength, Venom history and territorial ambitions. Current dependence/physical state must be selected, not combined across eras. | P; local leads, special operational events. | Temporary disciplined crew/network; conditional employment, no automatic full faction. | Reliable worker, witness or evacuation helper; Challenging support, Hard/Extreme direct exposure, Knightmare confrontation/escape. |
| Deadshot — `dc.character.deadshot.floyd_lawton` | [DC profile](https://www.dc.com/characters/deadshot): Floyd Lawton, marksman/mercenary; Task Force X history does not mean permanent free availability. | P; E when an actual assignment brings him into scope. | Individual contractor, not a default joinable Deadshot gang; client contract is not Squad recruitment. | Brokered service, bystander warning or witnessed cancellation; Challenging periphery, Extreme direct operation. |
| Poison Ivy — `dc.character.poison_ivy.comics_candidate` | [DC profile](https://www.dc.com/characters/poison-ivy): plant-centered motives/capabilities and fictional influence. Ethical stance, powers and relationships vary by selected era. | P; E with public ecological footprint and guarded personal access. | Optional stewardship/support network; voluntary work separate from allegiance or coercion. | Lawful caretaker, community helper, disputed commission; Accessible support through Extreme hazardous exposure. |
| Killer Moth — `dc.character.killer_moth.drury_walker` (existing candidate) | [DC mantle overview](https://www.dc.com/blog/2017/04/26/miles-to-go-the-un-familiar-faces-of-all-star-batman): costume/gear lineage and transformed variants differ. Existing registry's Walker candidate needs edition approval; Charaxes is not a default power. | P; local/common referrals. | Independent contractor or small crew; conditional associate contract. | Verify a work claim, negotiate a responsibility, become a dependable associate; Accessible/Challenging, not guaranteed harmless. |
| Ra's al Ghul — `dc.character.ras_al_ghul.comics_candidate` | [DC profile](https://www.dc.com/characters/ras-al-ghul): League of Assassins leader, long-range strategy/Lazarus history; Talia is his daughter in this account. | E with H discovery; no required Gotham residency. | League not joinable in the initial design; later participation requires a separate career/continuity contract. | Refuse recruitment pressure, protect information, avoid an operation; Hard periphery, Extreme/Knightmare direct stakes. |
| Talia al Ghul — `dc.character.talia_al_ghul.comics_candidate` | [DC profile](https://www.dc.com/characters/talia-al-ghul): strategist, Ra's's daughter; Leviathan is an era-specific organizational development. | E/H; agency and availability independently recorded. | League/Leviathan affiliation cannot be collapsed into one employer. No initial general recruitment. | Brokered dispute or guarded intermediary encounter; Hard/Extreme. |
| Man-Bat — `dc.character.man_bat.kirk_langstrom` | [DC collection](https://www.dc.com/graphic-novels/batman-arkham-2015/batman-arkham-man-bat): Kirk Langstrom/serum transformation. [A later solicitation](https://www.dc.com/comics/batman-the-brave-and-the-bold/batman-the-brave-and-the-bold-10) explicitly raises identity uncertainty around a new Man-Bat. | E; civilian incident first, identity only when evidenced. | Individual; not an automatic gang or default hostile employment. | Witness, evacuation support or ethical research referral; Challenging periphery, Extreme uncontrolled encounter. |
| Mad Hatter — `dc.character.mad_hatter.jervis_tetch` | [DC solicitation](https://www.dc.com/comics/harley-quinn-and-poison-ivy-2019/harley-quinn-and-poison-ivy-2): Jervis Tetch/Wonderland motif in that story. Exact influence technology and behavior require a chosen edition; an Arkham-game scene is not imported. | P; guarded/hidden lead, E only with actual cause. | Bounded support contract may exist; coercion is never consent or membership. | Verify a dubious invitation, help someone leave, refuse a demand; Hard/Extreme. |
| Ventriloquist/Scarface — `dc.character.arnold_wesker.comics` + `dc.persona.scarface.arnold_wesker.comics` | [DC's version comparison](https://www.dc.com/blog/2019/04/09/easter-egg-hunt-a-dummy-a-wig-and-a-famously-funky-costume): comics Arnold and TV Arthur Penn are distinct handlers. Puppet/persona is not a second payer or a settled clinical/supernatural diagnosis. | P; local crew disputes. | Conditional minor crew access; one actual authority/payment source per contract. | Clarify conflicting orders or refuse a false authorization; Challenging/Hard. |
| Catwoman — `dc.character.catwoman.selina_kyle` | [DC profile](https://www.dc.com/characters/catwoman): thief with heroic as well as criminal roles. Her relationship state must fit the selected period. | P; guarded individual access. | Independent contractor/associate; no universal joinable Catwoman faction. | Return a claim, choose discretion versus disclosure, lawful recovery commission; Challenging/Hard. |
| Killer Croc — `dc.character.killer_croc.waylon_jones` | [DC profile](https://www.dc.com/characters/killer-croc): Waylon Jones, strength/swimming/wrestling; transformation/affiliations vary. Appearance never determines guilt or automatic hostility. | P; local network/territorial encounters without district assignment. | Individual or optional small crew; no default gang membership. | Keep a practical promise, negotiate access, help a coworker; Challenging/Hard, Extreme threat. |
| Doctor Phosphorus — `dc.character.doctor_phosphorus.comics_candidate` | [DC comics solicitation](https://www.dc.com/comics/batman-battle-for-the-cowl-2009/batman-battle-for-the-cowl-man-bat-1) establishes a Gotham villain seeking greater power. Exact identity/hazard biography needs edition selection; the DCU Creature Commandos version is a separate adaptation. | E; guarded hazardous-incident source. | Nonjoinable individual in initial proposal. | Civilian warning, displacement/support episode; Hard/Extreme. No radiation/health engine is implied. |
| Hugo Strange — `dc.character.hugo_strange.comics_candidate` | [DC comics collection](https://www.dc.com/graphic-novels/batman-arkham-2015/batman-arkham-hugo-strange) anchors his Batman investigations. Arkham-game administrative power is not a universal comics office. | C as an available history/identity; operations can be H/E. | Nonjoinable initial operation; no monopolized treatment/referral path. | Verify professional claims, refuse unethical work, protect a witness; Challenging periphery to Extreme. |
| Joker — `dc.character.joker.comics_candidate` | [DC profile](https://www.dc.com/characters/the-joker): dangerous theatrical criminal identity. Do not assign a composite definitive real name or every published origin. | C; street-cell footprint may be public; personal presence independently gated. | Conditional gang initiation only under the existing direct-Arkham-encounter contract; street association is separate. | Accessible street-level coworkers, Extreme/Knightmare direct episode; no guaranteed invitation or compulsory membership. |
| Penguin — `dc.character.penguin.oswald_cobblepot` | [DC profile](https://www.dc.com/characters/the-penguin): criminal fixer and information leverage. No omniscient knowledge or assumed ownership of every broker. | C; public business footprint, guarded private access. | Conditional commercial/criminal network work; exact organization data proposed. | Legitimate-looking shift, disputed fee, confidential referral; Accessible/Challenging through Hard sensitive work. |
| Two-Face — `dc.character.two_face.harvey_dent` | [DC profile](https://www.dc.com/characters/two-face): Harvey Dent, legal knowledge, coin/chance motif. No diagnosis is inferred from a gameplay meter. | C; visible operation, conditional personal availability. | Conditional crew contract with disclosed terms; no legal immunity. | Follow, renegotiate or refuse a rule with competing obligations; Challenging/Hard, Extreme direct threat. |
| Riddler — `dc.character.riddler.comics_candidate` | [DC profile](https://www.dc.com/characters/riddler): Edward Nygma/Nashton and puzzle-centered crime. [Publisher discussion](https://www.dc.com/blog/2022/02/23/who-is-the-riddler) also distinguishes noncriminal detective periods. | C; public clues, guarded source. | Conditional specialist cell; role/era determines whether work is criminal. | Verify a clue, practical alternative or sourced hint; Challenging/Hard, not a compulsory trivia test. |
| Scarecrow — `dc.character.scarecrow.jonathan_crane` | [DC profile](https://www.dc.com/characters/scarecrow): fear-focused antagonist and fictional toxin motif. Do not turn diagnosis or distress into automatic violence. | C; specific hazard episode E, source may be H. | Nonjoinable initial incident actor; any later employment requires a separately approved influence contract. | Warn/assist, refuse a dangerous commission, seek independent support; Hard/Extreme/Knightmare exposure. |
| Mr. Freeze — `dc.character.mister_freeze.comics_candidate` | [DC comics collection](https://www.dc.com/graphic-novels/batman-arkham-2015/batman-arkham-mr-freeze) spans multiple stories/eras. A particular personal objective, equipment state and relationships require explicit version choice. | P; specialist work/E. | Conditional technical-support cell is an existing project proposal, not an established universal employer. | Lawful specialist handoff versus disputed emergency request; Challenging/Hard, Extreme environmental danger. |
| Harley Quinn — `dc.character.harley_quinn.comics_candidate` | [DC profile](https://www.dc.com/characters/harley-quinn): Harleen Quinzel, including an independent phase after Joker. No automatic permanent subordination to him. | P; independent/local activities or E. | Associate/team relationships require era-specific consent and availability; not proxy Joker initiation. | Civilian help, conflicting loyalties or a bounded independent commission; Accessible/Challenging through Hard. |
| Black Mask — `dc.character.black_mask.roman_sionis` | [DC profile](https://www.dc.com/characters/black-mask): Roman Sionis and underworld control; Jeremiah Arkham is another mantle holder, not the same actor. | C; coercive criminal network footprint. | Conditional organization access under existing employer proposal; paid work and formal affiliation separate. | Contest a deduction, protect a coworker, decline an order; Challenging/Hard, Extreme retaliation risk. |
| Clayface — `dc.mantle.clayface.pending_actor` | [DC profile](https://www.dc.com/characters/clayface): multiple mantle holders and very different histories. This catalogue row cannot instantiate a physical actor until a holder/version is approved. | P/E, identity discovery guarded. | Individual/associate; no default army, faction or guilt by disguise. | Corroborate identity, refuse impersonation, lawful assistance in an appropriate era; Challenging to Extreme. |
| Firefly — `dc.character.firefly.garfield_lynns` | [DC's comics/television comparison](https://www.dc.com/blog/2016/05/09/the-dctv-secrets-of-gotham-ep-2-20-unleashed) distinguishes comics Garfield Lynns, later mantle holder Ted Carson and the television adaptation. Fire-themed equipment/operations are the conservative anchor; Firebug is a different character. | P/E; sourced fire incident or contractor lead, not automatic citywide arson. | Individual contractor; nonjoinable organization by default. Any associate work needs a separately approved, voluntary contract. | Warning, evacuation support, witness account or refusal of a dangerous commission; Challenging safe periphery, Hard/Extreme direct exposure. No fire/health engine is implied. |
| Professor Pyg — `dc.character.professor_pyg.lazlo_valentin` | [DC editorial](https://www.dc.com/blog/2019/01/09/professor-pyg-will-make-you-r-nightmares-perfect): Lazlo Valentin, coercive perfection motif and victimization. Select an edition before specifying capabilities; no clinical diagnosis or copied horror scene. | E/H; credible missing-person or victim-support lead, not guaranteed discovery. | Nonjoinable initial incident actor; coerced victims are not consenting gang recruits. | Verify a warning, seek help, refuse complicity, support survivors; Accessible indirect assistance, Extreme/Knightmare direct encounter. Graphic harm and medical mechanics are outside this proposal. |
| Victor Zsasz — `dc.character.victor_zsasz.comics_candidate` | [DC profile](https://www.dc.com/characters/victor-zsasz): individual serial killer and tally motif. Do not invent a themed gang, shared identity with another adaptation or a relationship from a gallery card. | P/E; evidence-dependent warning and incident availability. | Nonjoinable individual; no recruitment or advancement ladder. | Sourced witness cooperation, neighborhood warning or safe assistance; Accessible indirect support, Hard through Knightmare direct danger. No victim collectibles, kill rewards or guilt by association. |
| Hush — `dc.character.hush.thomas_elliot` | [DC profile](https://www.dc.com/characters/hush): Thomas Elliot and a personal campaign against Bruce Wayne. Adaptations' identity reveals/alliances are not interchangeable with this comics candidate. | E/H; not a mandatory every-career conspiracy. | Nonjoinable initial antagonist operation. | Verify an intermediary, protect private information or leave; Hard/Extreme. |
| Deathstroke — `dc.character.deathstroke.slade_wilson` | [DC profile](https://www.dc.com/characters/deathstroke): Slade Wilson, enhanced mercenary distinct from Floyd Lawton. Visiting Gotham needs an actual mission/availability cause. | E/H; no default residence or standing alliance. | Individual contractor; no initial automatic recruitment ladder. | Disputed support contract or civilian avoidance; Hard periphery, Extreme/Knightmare direct threat. |

These are operating possibilities, not promises that a powerful actor behaves
kindly or honors an agreement. No standing Bane–Joker, Deadshot–Penguin,
Ivy–Ra's, Croc–Black Mask or Moth–Riddler relationship is asserted. If an original
episode introduces a temporary deal, record its terms/source and label it our
proposal rather than established canon. Other majors/minor rogues remain in the
existing registry/research pool; no need to activate all of them at once.

## 4. Joinability and separate milestones

| Organization/relationship — all classifications proposed | Initial access model | Guardrail |
| --- | --- | --- |
| Penguin/Black Mask/Two-Face/Riddler networks | Potential contract, trial association and later separately accepted affiliation. | Employment is not instant faction ownership; do not rename Harbor/Carnival/Iron or reuse their join slot silently. |
| Joker cells/gang | Cell work without membership; formal initiation follows the existing Arkham contract. | Actual direct encounter with the correct available Joker, valid episode/location, valid offer and explicit acceptance. Proxy/recording/rumor/reputation is insufficient. Decline stays viable. |
| Bane crew | Optional time-bounded worker/crew role. | A logistics success cannot make the player his lieutenant or guarantee personal trust. |
| Ivy support network | Voluntary stewardship/technical collaboration, where the chosen phase permits it. | Coercion/exposure is not allegiance; no automatic romance or exclusive access to recovery. |
| Killer Moth / Ventriloquist small crews | Possible associate contract; distinct payer/authorization. | No full treasury/warfare simulation by default; one real payer for the Scarface/handler arrangement. |
| Deadshot/Catwoman/Croc/Deathstroke individual relationships | Contract, ally, rival or acquaintance. | No fictitious universal joinable gang named after each individual. |
| League/Leviathan | Nonjoinable in the first encounter slice. | Future career access needs a separate contract, era and voluntary acceptance; Talia's autonomy is not merged into Ra's. |
| Task Force X / Creature Commandos | Not a freely joinable player organization in this proposal. | A penal/coerced assignment is not normal recruitment; no arrest-farming reward. Their versions/handlers are continuity-specific. |
| Man-Bat/Phosphorus/Strange/Scarecrow incident actors | No membership path in initial encounters. | They can still affect civilian/criminal work and recovery without an employer ladder. |

Track milestones as separate sourced facts, not one linear score:

1. **Encounter:** actual meeting/direct observation with a specific actor instance.
   A letter, proxy or rumor records contact/knowledge, not a personal meeting.
2. **Survival/resolution:** leave/avoid/end a particular hazardous episode; it can
   occur without fighting, meeting or winning favor. No repeat survival XP.
3. **Trust:** directed, contextual assessment based on what that actor knows.
   A coworker reference is not the boss's trust, and fear is not trust.
4. **Recruitment:** explicit valid offer/acceptance into a particular organization
   or contract, with current availability, terms and consent. A high number alone
   cannot complete it; some actors never recruit the player.
5. **Advancement:** later concrete authority, compensation, obligations and access
   actually delegated. It can be refused, disputed or lost without deleting the
   earlier encounter or rewriting prior consent.

No milestone requires the next one. A respectful refusal can preserve trust
while leaving recruitment absent; a coerced task can end in survival without
trust or affiliation. Famous-villain employment is not the only successful career.

## 5. Proposed Accessible → Knightmare progression

These are **encounter-role bands**, not implemented settings, a canonical power
ranking or an automatic promotion chain. Core actors do not level-scale to the
player. UI accessibility, hints and presentation skips are separate choices and
remain available at every band.

| Proposed band | Readiness / meaningful problem | Stakes and viable response |
| --- | --- | --- |
| Accessible | Understand a sourced local offer; no faction/vehicle or advanced statistic needed. | Choose a lawful commission, verify, decline or redirect. One action at most for the first slice; bounded money/contact consequence, no lethal surprise. |
| Challenging | Conflicting promises, limited TU/cash, unreliable intermediary or incomplete evidence. | Negotiate timing, choose whom to inform, accept a partial result. Useful local/free alternatives remain. |
| Hard | Sensitive authority, coercive employer, rival obligations or a carefully gated dangerous role. | Substantive preparation/support/reference; retreat can cost this opportunity, never all ordinary life. |
| Extreme | Direct exposure to an actor whose capabilities vastly exceed an ordinary goon. | Survival, assistance, concealment of one's location in fiction, de-escalation or withdrawal; no required conventional boss victory. |
| Knightmare | Optional, expressly signaled high-consequence survival/loyalty dilemma with very limited safe plans. | Multiple warned approaches and a finite safe decision boundary; no automatic career deletion, compulsory death or unannounced permanent lockout. Irreversible end-state rules need separate approval. |

Progress comes from relevant references, kept commitments, corroborated knowledge,
permissions/support and accepted responsibility, not killing minor rogues for XP.
A low-stakes Joker-cell coworker job can be Accessible while Joker's personal
episode is Extreme/Knightmare. Bane remains dangerous even if peripheral work is
Challenging. The same band changes choices and information, not merely enemy HP.

### Separate milestone difficulty examples — all proposed

These bands describe a disclosed role, not numerical unlock thresholds. Encounter
does not require trust, trust does not promise recruitment, and no number of repeat
jobs guarantees advancement. Survival can mean avoiding a direct confrontation.

| Example | Encounter / survival | Trust | Recruitment | Advancement |
| --- | --- | --- | --- | --- |
| Killer Moth, reviewed costume variant | Accessible referral; Challenging disputed handoff. | Challenging: corroborated reference and one meaningful commitment. | Challenging associate offer, only if crew and vacancy exist. | Hard: delegated responsibility with negotiated obligations. |
| Penguin network | Accessible workplace access; Hard private operation. | Hard: discretion versus a competing, legitimate obligation. | Challenging/Hard explicit contract; meeting the boss unnecessary. | Hard/Extreme responsibility and exposure, not repeated shift count. |
| Joker organization | Accessible street coworkers; Extreme/Knightmare direct encounter. | Extreme, contextual and unstable; never a safety guarantee. | Extreme/Knightmare Arkham encounter, actual offer and voluntary acceptance under the existing contract; no guaranteed offer. | Knightmare optional responsibility; refusal retains other careers. |
| Bane | Challenging support; Extreme/Knightmare direct danger. | Hard: reliable conduct known to the actual decision-maker. | Hard/Extreme temporary crew contract if available. | Extreme delegated authority, distinct from personal favor. |
| Poison Ivy, selected era | Accessible lawful support; Extreme hazardous proximity. | Challenging/Hard informed stewardship choice. | Conditional Hard support affiliation if this version permits it; coercion never qualifies. | Hard/Extreme responsibility, not mandatory criminal escalation. |
| Deadshot | Challenging intermediary; Extreme direct operation. | Hard professional confidence tied to actual knowledge. | N/A: no generic Deadshot gang or Squad admission. | N/A organization ladder; a later independent commission is a new contract. |
| Professor Pyg / Victor Zsasz | Accessible indirect help; Extreme/Knightmare direct danger. | N/A initial design: do not reward cultivating these actors. | N/A: nonjoinable. | N/A: nonjoinable; survivor/community trust is a different relationship. |

Firefly's possible contractor association remains a separate approval decision;
an individual hire must never silently become organization membership. Any future
roster may omit an actor or change these proposed bands after continuity review.

## 6. Proposed scheduling, causal triggers and persistence

**Independent of the player** means actors/events advance on real simulation-day
transitions even when the player is elsewhere, declines, is detained or never
learns of them. It does not mean wall-clock time, a background server or immunity
to genuine player-caused changes. Pausing/closing the offline game pauses time.

Proposed optional phase runs once after the existing daily-life phase. Reuse the
existing day transition; do not reorder legal/economic/navigation phases or add
extra day advances for an encounter. New notices/encounter choices have their
own source instances; old M015 roster definitions/selections stay untouched.
Legal/court source integration and newly scheduled territorial/economic effects
need explicit ordering adapters, not a direct write that bypasses the old phases.

Proposed lifecycle:

`eligible world cause → scheduled instance → active world stages → aftermath`

Player projection is separate:

`unknown → sourced notice/lead → optional involvement → terminal participation`

A city event can finish without a player projection. Discovery need not delay its
world timetable. An accepted commitment pins its own fair deadline/outcome rules;
late discovery must not offer an already impossible bargain or backdate guilt.

| Proposed record | Minimum authority / invariant |
| --- | --- |
| Definition | Stable ID/version, continuity pack, actor variants, causal predicates, phase ordering, local place references, bounded stages, permitted adapters, risk/exit policy, uniqueness/cooldown scope. Local data, no executable expressions. |
| World instance | Durable instance ID from definition + actual source/cycle; actor availability, real cause IDs, scheduled/actual days, phase marker, reserved capacity/funding and outcome. Exists independently of discovery. |
| Player involvement | Sourced delivery/notice, eligible offer, accepted terms/role, explicit selections, action/location costs, refusal/expiry/outcome and applied effect keys. No inferred acceptance. |
| Knowledge/claim | Claim ID, referenced truth where any, issuer/observer/audience, observation/channel, date, confidence category, expiry/retraction and provenance parents. False claims need no corresponding true fact. |
| Settlement | Command/world-phase ID, instance/stage/selection, unique effect key, before/after values, payer/resource/source references and actual informed recipients. Reports reconstruct views only. |

Use deterministic sorted-ID eligibility and a private keyed selection such as
SHA-256 of `(world_seed, rules_version, continuity_pack, definition_id,
causal_trigger_id, cycle_index)`. Record the eligible context/result once.
Never use Python hash(), event-list length, wall time, global/job RNG or a new
ID minted by repeated requests. Same seed/actions/content reproduce the same
world; different genuine actions may change later prerequisites meaningfully.

Uniqueness scope is explicit: once per career, once per actor/episode, or one
instance per actual source/cycle. A rumor referring to the same incident cannot
spawn another incident/reward. A cooldown controls a new justified opportunity,
not an artificial waiting/grind gate. Failed selection and ignored candidates
are not rerolled by menu, reload or travel. Arrest/death/retirement invalidates
future presence under actual world state; absence never spawns an understudy
without a separately defined actor and introduction.

If eventually implemented, use an optional pinned encounter version, explicit
historical adoption and future-only stages. No old save gains retroactive rogue
meetings, debt, affiliations, claims or lost opportunities. Missing required
content/version must fail clearly; keep all released definitions available for
offline resume. These are proposed fields, not a schema migration now.

## 7. Proposed NPC knowledge and rumor propagation

World truth, a speaker's belief, a claim and what the player knows are separate.
Existing legacy relationships are NPC-to-player metrics, not a rumor network.
Tess/Cal already record observed facts; they do not know every police file or
faction transaction. A new encounter extension must respect that distinction.

- Deliver information by an actual witnessed event, known participant,
  authorized record, public bulletin or explicit contact interaction. A report
  only displays previously delivered knowledge; opening it does not create a
  notice, rumor roll, relationship change or acknowledgement.
- Propagate at most once per `(claim, sender, recipient, channel, cycle)` after
  a real contact/channel opportunity. Bound daily transmissions and keep parent
  provenance; relays of one source do not become independent corroboration.
- Store source reliability and corroboration separately. A confident false claim
  stays false; learning it may change a belief but never world truth, guilt or
  actor availability. Contradictions can remain unresolved and have useful verify/
  refuse options. Correcting a rumor records a retraction, not an erased history.
- NPC reactions require their actual received facts. A private betrayal cannot
  reduce citywide reputation instantly. An employer can *believe* lawful reporting
  was betrayal without the engine declaring that the report was a crime.
- Keep true identities/private intentions in world truth. Public predicates,
  option visibility, route metadata, quote tokens and rumors must not leak them.
  The existing debug snapshot intentionally exposes full truth and is unsuitable
  as a secret-sensitive player read model.

No real-time chat, generative AI service or paid API is needed. Dialogue is
authored presentation of choices/facts. A bounded deterministic relay model can
support lies and rumors without inventing autonomous conversational intelligence.

## 8. Proposed outcomes and lasting consequences

World resolution and player participation can have different results. For
example, a warehouse closes without the player; the player successfully warned a
coworker, failed a delivery promise and never met Bane. Do not collapse that into
one success/failure checkbox.

| Proposed participation tag | Evidence / distinction | Possible persistent effects and safeguard |
| --- | --- | --- |
| Missed | No delivered notice/involvement before closure. | World changes still occur; later sourced news may explain it. No invented refusal, broken promise or relationship penalty for ignorance. |
| Ignored | A notice was actually delivered, no commitment made, deadline passed. | Opportunity expires, not a fabricated psychological intention. Another informed actor reacts only if a response was reasonably expected; no mind-reading screen telemetry. |
| Refused | Explicit decline of specific disclosed terms. | Close that offer, possibly preserve independence/standing; no acceptance debt or guaranteed punishment. Avoid repeat-decline rewards. |
| Failed | Accepted commitment could not meet its pinned condition. | Explain actual cause/lost pay/access, respect force-majeure terms and disclose a recovery route. A known ineligible command rejects atomically instead of silently failing a story. |
| Partial | Some independently defined deliverables/people helped. | Settle only achieved funded terms; distinct later references. Do not pay full success plus partial reward. |
| Betrayed | Specific agreement was deliberately broken or information passed, with explicit actor/action facts. | Directed informed trust/hostility/contract effects. Label who considers it betrayal; legality and narrator moral judgment remain separate. |
| Cheated | Identify which party withheld/altered payment, misrepresented authority or exploited terms. | Record actual nonpayment/dispute and verification routes. No imaginary cash debit or unbounded debt; future suspicion is source/audience-specific. |
| Successful | The selected role's actual terms were completed. | Pay once from valid funding, reference actual contribution and known audience; not automatic encounter, survival, trust, membership and promotion together. |

Outcomes may combine (partial work + cheated by payer, successful rescue + failed
criminal contract). Store objective acts, outcome tags, responsible parties and
audience knowledge rather than allowing contradictory terminal selections.
Exactly one terminal selection/settlement per accepted source stage; a later
appeal/aftermath has a new justified cause, not a retry of the old payout.

Consequences may affect specific relationships, known reputation, permissions,
contract availability, bounded cash/obligations, real faction resources or a
district transfer. Each needs an approved owner/adapter, before/after values and
cause. Fame/affiliation/rumor alone is not evidence, a charge or conviction.
Non-job criminal acts require the future source adapter before playable use;
never fake a job attempt to satisfy current legal validators. The atlas's176
places are not new district-income accounts. Story text cannot transfer territory.

## 9. Ordinary-life recovery and agency safeguards — proposed

Keep three gameplay actions/day and18 TU/day. Disclose actual meeting place,
action cost, window, known hazard and door-to-door/return quote before commitment.
Travel is separate; no automatic movement, free TU/action refresh, custody bypass
or unrestricted institution entry. A valid refusal/read/save costs no action and
grants no reward. A costly commitment cannot exceed the remaining allowance.

Every dangerous role needs a known finite decision/exit boundary. Exhaustion,
zero cash, refused criminal work, absent actor, failed offer or incomplete rumor
must leave inspect/save/wait and an ordinary local/support route. Event-caused
closures need a proven free escape or bounded reopening; repeated short closure
leases must not create an indefinite siege loophole. No forced vehicle purchase,
mandatory repeated commute, premium currency, real-time timer or one-villain cure.

Housing, lawful work and civilian contacts are not universally revoked because
one rogue dislikes the player. A specific witness/employer can react, with a
disclosed alternative. Arbitrary global poverty spirals, secret unavoidable death
or deletion of a career are not default Knightmare mechanics. Later irreversible
career endings require explicit separate approval and informed participation.

Influence/exposure is fictional condition state, never consent, romance,
membership or a psychiatric identity. Preserve the influence/recovery contract:
independent ethical help and non-Arkham support remain possible. Institutional
admission is not a recruitment farm. Existing health/combat/treatment systems
are not implemented just because an encounter names them.

Lawful involvement can mean paid verification, repair/support or documented
cooperation. Civilian involvement can mean aiding workers, choosing public
information channels or avoiding a hazard. Criminal involvement requires an
explicit chosen act and its consequences; the same city event must not silently
classify everyone nearby as an accomplice. Refusing crime is a meaningful branch,
not an inferior route designed only to grind reputation before the real game.

## 10. Three original example chains — proposed, not executable

These demonstrate the model, not reproduced DC stories. Workplaces/contacts are
original draft content; exact locations, cash terms and actor variants require
approval. No new statistics, goods inventory, combat, legal adapter, schedule or
condition subsystem is assumed implemented. Shared actors do not imply existing
canonical alliances. All three events can run without player involvement.

### A. Bane — A Count That Does Not Add Up

**Canon anchor:** the [publisher profile](https://www.dc.com/characters/bane)
supports strategy and territorial ambition; our dispute, coworkers and outcomes
are original. Choose a compatible active Bane variant and a genuinely available
local operation. This is not Knightfall or an invitation to defeat Bane.

| Stage | Proposed prerequisite, discovery and choices | World / persistent result |
| --- | --- | --- |
| Autonomous cause | A documented short-term warehouse contract approaches a fixed dispatch day; a Bane-associated coordinator actually controls a reserved limited crew allocation. Competing work creates a genuine discrepancy, not a random player tax. | The coordinator proceeds, postpones or cancels by actor/resources/world state even if the player is detained or elsewhere. No automatic district ownership. |
| Discover | An original coworker delivers a specific discrepancy report; a public schedule change provides another lead. Verify its authority or leave it uninvestigated. | Player learns only what that source can observe. Rumored Bane approval is not a personal meeting/trust fact. |
| Involvement | Lawful role: reconcile a limited work record. Civilian role: warn coworkers about a credible unsafe demand. Criminal role: knowingly accept a separate unlawful diversion commission, only after legal/source adapters exist. | Disclose payer, deadline, actual commute and known exposure. Accept only the selected responsibility; do not replace an existing M015 job or award its payout too. |
| Pressure / meeting | Evidence conflicts with a supervisor's order. Corroborate, request revised terms, comply within terms or withdraw. A personal briefing occurs only if Bane is available and physically present in the approved episode. | One authored verification may support a real relationship fact; successful paperwork alone does not fabricate Bane contact or promotion. |
| Failure / partial | Miss the accepted count, or help workers but leave the commission unresolved. Explain whether travel closure, withheld authority or the player's chosen breach caused it. | Settle only achieved terms; one recorded loss/reference. A blameless external blockage follows its contract clause rather than inventing betrayal. |
| Refusal / betrayal / cheated | Decline before commitment; report a verified threat through a chosen channel; or discover the coordinator falsely promised extra pay. | Refusal creates no debt. Only informed parties react to disclosure. Cheated wages become a dispute, not an automatic second payment or global vendetta. Bane's favor/mercy is not guaranteed. |
| Aftermath | The dispatch goes ahead with another worker, is cancelled or loses a documented resource. | Coworker reference/hostility, future employment eligibility and actual funded resources persist. Full-faction power/territory changes need the shared adapter; no story-only capture. Ordinary work/home survives a closed Bane offer. |

Ignoring the lead loses this role, not the entire career. An accessible records
choice can lead to a Hard responsibility; direct violent confrontation would be
Extreme/Knightmare survival content outside the first slice. No work repetition
guarantees becoming a lieutenant or immunizes a goon against a dangerous employer.

### B. Deadshot — The Deposit Nobody Authorized

**Canon anchor:** [Floyd Lawton](https://www.dc.com/characters/deadshot) is a
mercenary with a particular Task Force X history. This disputed commission and
its participants are original; no assassination plan or published mission is
adapted. Current custody/assignment can make him unavailable in this campaign.

| Stage | Proposed prerequisite, discovery and choices | World / persistent result |
| --- | --- | --- |
| Autonomous cause | A brokered commission has a real payer, reserved deposit and cancellation window; the selected Lawton actor has actual capacity. If he is unavailable, cancel/suppress with a real cause. | Window advances independently of player proximity. No mandatory spawning, substitute Deadshot or freedom from Waller assumed. |
| Discover | An original bookkeeper reports an inconsistent authorization. The player receives a claim of Deadshot involvement, not proof or automatic criminal knowledge. | Verify through an allowed contact/record; a corroborated lead can open an optional later handoff. No rumor becomes legal evidence by being repeated. |
| Involvement | Lawful: help unwind the disputed payment under valid authority. Civilian: communicate a credible threat to an appropriate source. Criminal: knowingly conceal material participation for the broker, gated on future legal-source rules. | Pin role, payment/escrow authority and risks. No firearms, combat or covert-operation system is created by this paper branch. |
| Direct encounter | If the commission and actor remain available, an authored public-boundary handoff can become a real Lawton encounter. A missed handoff or proxy is not one. | Surviving or completing it does not join Task Force X or make Lawton a permanent ally. Do not invent a universal promise that he protects civilians. |
| Failure / partial | Cancellation deadline passes, or the player verifies authority but cannot recover the deposit. | No full refund invented; record partial reference and real losses once. A fee is paid only from agreed valid funding. |
| Refusal / betrayal / cheated | Refuse the role; disclose a known conflict; or learn that the broker forged a promised authorization. | Offer closes without guilt/debt. An informed broker may label disclosure betrayal, while the objective record remains a report of facts; legal status follows acts/evidence, not the broker's accusation. |
| Aftermath | Deposit settles or remains disputed; another intermediary acts; Lawton leaves for his next valid assignment. | Specific trust/suspicion and future broker access change. City/legal effects require witnessed sources/adapters. A lost commission cannot forbid all lawful employment or force a duel with Deadshot. |

Successful support earns, at most, its concrete fee/reference and actual contact
fact. A direct operation can be Extreme; civilian warning/verification is a
Challenging alternative, not a compulsory climb into killing-for-hire gameplay.

### C. Poison Ivy — The Greenhouse Has Two Owners

**Canon anchor:** [Ivy's plant-centered concerns and capabilities](https://www.dc.com/characters/poison-ivy)
support this original property/stewardship dispute; no current alliance, romance
or fixed villain/hero phase is presumed. Select a compatible actor/era first.

| Stage | Proposed prerequisite, discovery and choices | World / persistent result |
| --- | --- | --- |
| Autonomous cause | A public-facing greenhouse maintenance window overlaps a real ownership/access dispute; the selected Ivy actor has an actual local interest. | Owners/caretakers act on their own timetable. An absent Ivy produces an ordinary dispute or a different approved source, not a look-generated appearance. |
| Discover | A caretaker delivers two conflicting claims; public work restrictions are another source. | Player can corroborate ownership/authority or decline involvement. A contact's sympathy for Ivy is a belief, not proof of her presence or criminal guilt. |
| Involvement | Lawful: accept an authorized care/records shift. Civilian: help displaced workers or preserve a public notice. Criminal: knowingly assist an unlawful removal only if that act has a supported future legal/economic source. | Terms specify access, responsibility, capacity, known hazard, TU/actions and a bounded completion window. No botanical inventory/economy is silently introduced. |
| Direct contact / condition | A real meeting occurs only if Ivy is present and consent/access permits it. Question an instruction, request independent review or leave. Any fictional influence exposure is separate future condition content. | Voluntary ecological agreement, exposure, trust and affiliation are separate. Coercion never selects permanent allegiance or romance; recovery has non-Ivy/non-Arkham alternatives. |
| Failure / partial | Preserve worker access but fail the accepted commission, or complete care while the ownership dispute remains unresolved. | Distinct references and only funded achieved pay. Do not grant complete ecological victory, free items or universal resistance to fictional powers. |
| Refusal / betrayal / cheated | Refuse unsafe/unverified terms, disclose a verified threat, or discover a false ownership/payment claim. | No automatic hostility for all communities. Each actor learns through a source; a disagreement can cost one offer without rewriting consent or creating a diagnosis/case. |
| Aftermath | The greenhouse reopens under valid authority, remains disputed or loses one scheduled service window. | Authored opportunities/permissions, worker relationships and verified public knowledge persist. A rumor of Ivy cannot transfer a district or make the player a criminal. Home, independent care and ordinary work remain viable. |

The stakes are stewardship, authority and livelihoods, not a seductive collectible
or an automatic aggression modifier. Accessible/Challenging support can coexist
with Extreme hazardous contact without forcing the player into it.

## 11. Contradictions and decisions requiring approval

| Potential contradiction | Required resolution / approval |
| --- | --- |
| Current original GANGS/NPCs versus proposed DC employers | Preserve existing faction/save keys and immediate legacy join behavior. No Harbor→Penguin, Carnival→Joker or Iron→Black Mask reinterpretation. New actors/organizations need approved IDs/adapters. |
| All catalogue rogues assumed simultaneously alive/available | Approve one continuity/era manifest with lifecycle/availability and incompatible variant exclusions. A source's related-character list is not a relationship graph. |
| Arkham-branded books confused with Arkham-game continuity | DC's Batman: Arkham collections include comics from multiple eras. They are research anchors, not proof of game-universe biography. Explicitly separate source work, universe and selected variant. |
| Deadshot incarnations / Deadshot versus Deathstroke | Pin Floyd's exact variant; do not merge Lawton with Slade. [DC's Arkhamverse discussion](https://www.dc.com/blog/2024/03/11/suicide-squad-kill-the-justice-league-reveals-whatever-happened-to-the-arkhamverse) explicitly distinguishes Deadshot counterparts; it is not this project's default canon. |
| Arnold/Scarface versus TV Arthur Penn | The cited publisher comparison distinguishes handlers. Preserve actor/persona IDs, one authority/payment source and unknown supernatural/clinical interpretation. |
| Talia/League/Leviathan | Ra's–Talia family tie is source-supported, but organizational authority and era are not interchangeable. Approve the specific phase; no generic patriarchal obedience assumption. |
| Harley permanently treated as Joker's subordinate / Ivy as universally hostile | Publisher profiles include more than one phase/role. Choose the period; do not infer present alliances, romance or employment from a gallery card. |
| Joker's identity/availability/recruitment | Keep variant identity unresolved until selected. Preserve the direct Arkham encounter + valid offer + explicit acceptance project contract; it is our campaign rule, not universal DC lore. No proxy initiation or admission farming. |
| Clayface/Killer Moth mantle powers combined | Select holder and transformation state; a costume version does not automatically gain every monster power. A mantle row is not an instantiated actor. |
| Phosphorus comics versus screen Creature Commandos | Pin identity/hazard details from the selected edition before writing mechanics. [DC's team comparison](https://www.dc.com/blog/2024/12/02/no-wonder-james-gunn-loves-the-creature-commandos-dc-s-weirdest-war-heroes) expressly describes different incarnations; do not import the screen assignment into the comics candidate. |
| Current job-specific legal cases versus new encounter crimes | Approve non-job source, investigation/court ordering and exact responsibility/evidence rules before a criminal option can execute. No invented witnesses, guilt by rumor or fake job attempts. |
| Current no health/combat/rumor scheduler versus severe story stakes | Keep these as gated proposals. Approve finite noncombat exits and knowledge rules first; do not claim those missing systems from narrative text. |

Still to approve: roster/era manifest and core presence choices; organization
joinability; exact difficulty stakes and irreversible-ending policy; world-phase
position; sources/cooldowns/capacity and bounded funding; rumor visibility and
corroboration; one initial actor/contact/place; legal/influence prerequisites; and
the smallest slice below. None is approved for implementation by this mission.

## 12. Smallest future slice and acceptance contract — proposed only

**Recommend one minor-crew verification episode, not the three major chains.**
Use one original contact and the reviewed costumed Killer Moth candidate as an
optional individual. One autonomous work-notice source matures on a fixed
simulation-day window after explicit future encounter adoption. An optional
public-frontage verification/handoff can establish actual contact; a rumor or
letter cannot. No combat, goods inventory, new player crime, condition, full
dialogue tree, organization membership or faction simulation is needed.

Choices: verify the source, accept a bounded lawful records task, refuse, pass
corroborated information to a chosen contact, or let the known offer lapse.
Provide a fixed funded fee/reference for actual work, one bounded trust/dispute
effect for an informed contact, and one different next-day follow-up whose
eligibility reflects the selected outcome. A false claim can yield a cheated/
partial outcome under disclosed terms. The world notice expires independently
if never discovered; no player missed-quest penalty or fake broken promise.

Future implementation would add a tiny local encounter definition pack, optional
validated instance/knowledge state and one explicit service adapter around the
existing choice pattern. Append one idempotent world phase, narrow detached
views and thin CLI presentation. Reuse existing travel/cash owners and preserve
old saves with no retroactive events. Do not add DC name checks to reducers.
Generic tests can use entirely original stand-in actors; licensed definitions
remain optional local content, never required by generic engine logic.

| Proposed acceptance gate | Required evidence after separate authorization |
| --- | --- |
| Compatibility / replay | Current 336 tests stay green; old saves remain without encounter state; explicit future adoption, pinned missing content and resume at every stage. No retroactive rogue meetings or expenses. |
| Autonomous world | Same world source starts/finishes on the same cause/day while the player is away, detained, unaware or refusing. Personal discovery/decisions may differ; real interventions can change later causes. |
| Knowledge / secrecy | Public truth and belief views are distinct; false rumor has provenance, no omniscient reputation/evidence. Read/format/reload does not draw, acknowledge, propagate or mutate. |
| Choice / consequences | Verify/accept/refuse/known-lapse plus partial/cheated variants have real, different follow-up eligibility. Missed unknown source grants no blame; no duplicate decline/verification reward. |
| Atomicity / identity | Same source/request/selection settles once, rejections leave whole world/RNG unchanged, resource receipts reference actual funding, simultaneous causal triggers sorted deterministically. |
| Budget / recovery | Three actions and18 TU preserved; zero cash/TU, missing actor, closure and expired access retain ordinary work/support/save/wait and a finite safe route. No vehicle requirement or automatic commute. |
| Legal / agency | Unsupported crime/condition/recruitment effect rejects before mutation. No guilt, exposure or consent inferred from presence/rumor. No access/admission coercion loophole. |
| Long run / variety | Several seeds, insertion orders/fresh processes, actual save failures, cooldown/uniqueness and extended replay. Report repetition honestly; do not force all rogues to appear to pass a balance test. |

Recommended sequencing: retain the preserved M016-A and Mission 015 metadata
repair commits, approve the encounter
identity/knowledge/source contract, then build this one episode. Portable mobility
and encounter research may remain separate proposals; neither justifies skipping
the other's acceptance gates. Expand independent contacts/crews before Bane,
Deadshot/Ivy chains, advanced combat or citywide antagonist arcs. Do not assign
M017/M018 numbers or start either implementation without a new instruction.

## 13. Verification and limits of this design work

Reviewed actual faction/economy/strategy, careers/reputation/join, NPC/relationship,
law/evidence, choice, daily-life, navigation, service and event seams, plus the
existing narrative contracts linked above. Character anchors use primary
publisher profiles/solicitations/editorials with specific continuity cautions;
unavailable profile pages were not treated as inspected. Some publisher text was
available only through search excerpts; those support the narrow anchor stated,
not an inspected full issue. Exact editions, alternative continuities and unresolved
identity/power details still require content review. Some sources use dated clinical
language; no diagnosis, disability
or appearance is used as proof of evil or a gameplay consent flag here.

Mission 014 originally added only this Markdown proposal after its preservation
commit. Mission 015 preserves that body, adds Firefly, Professor Pyg and Victor
Zsasz plus milestone distinctions, and adds the companion After Dark proposal.
No Rogue Encounter behavior or narrative tests were implemented/executed.
Mission 015's actual 53 focused / 336 full tests and unchanged two-seed daily
resume hashes validate the separate mobility repair, not these future systems.
