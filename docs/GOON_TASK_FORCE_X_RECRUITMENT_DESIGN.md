# Gotham: The Goon — Restricted Task Force X Recruitment Design

**Mission 029 design addendum; documentation only, November 5, 2026.**
Inspected clean feature/m029-underworld-registry at
f8f43ecce769bd8706e765ad6ccf356940f69818. No Task Force X implementation or
dedicated contract existed. This document owns Squad-specific canon context and
the proposed special recruitment route; existing character registries still own
their identities. The [master index](GOON_MASTER_ROSTER.md) provides navigation,
not another biography, government intelligence feed or public discovery list.

The protagonist remains ordinary. This is a rare optional institutional bargain,
not a class upgrade, guaranteed encounter, combat tutorial or required criminal
ending. No Python, JSON definition, save migration, event, RNG, budget, navigation,
backend or Native.Builder change is made. Three actions/day and eighteen TU/day,
offline play and historical saves remain unchanged.

## 1. Inspected sources and actual implementation boundary

| Authority inspected | Existing facts that may later be reused | What cannot be inferred |
| --- | --- | --- |
| [Legal state](../legal_state.py#L27), [record validation](../legal_state.py#L96) | legal_version 1; legal.record entries link case_id, day, outcome, assessed/paid fine and response. Convicted and dismissed outcomes are distinct; historical date/fine fields deliberately remain null. | No offense-gravity classification, complete sentence, expungement, parole/probation, sentence conditions or government access permission. Missing history is not a clean record. |
| [Case creation](../consequence_engine.py#L48) | Current witnessed collection cases carry source_attempt, suspect, evidence and investigation state. Legacy robbery has a separate source. | Job count, payout, heat or a witness report is not a conviction, violent-offense history or operational competence. No invented “substantial record” threshold follows. |
| [Court outcome](../legal_engine.py#L93), [accelerated custody](../simulation.py#L69) | Structured outcome/fine receipts; the current accelerated sentence returns custody to free. | A prison chapter, physical presence at Blackgate/Arkham, lawful transfer, completed supervision or a continuing sentence available for commutation. Unpaid assessed-versus-paid fine amounts are not a new supervision/debt system. |
| [Relationships](../relationship_engine.py#L3), [original world](../simulation.py#L16) | Bounded trust/respect/fear/hostility/suspicion and causal history for existing named people. | No Warren White, Deadshot or Harley actor state; no justified hostility score threshold or automatic transfer of legacy NPC feelings to DC people. |
| [Rogue encounter contract](GOON_ROGUE_ENCOUNTERS_DESIGN.md#4-joinability-and-separate-milestones) and its [Deadshot paper chain](GOON_ROGUE_ENCOUNTERS_DESIGN.md#b-deadshot--the-deposit-nobody-authorized) | Proposed source-backed encounters, distinct survival/trust/recruitment milestones and conditional availability. Existing Task Force X/Creature Commandos row says not freely joinable. | No implemented Deadshot episodes, Squad admission, permanent loyalty or general faction-switching system. One commission is not several encounters. |
| [Harley/care contract](GOON_INSTITUTIONS_AND_RECOVERY.md#b-arkham-as-a-distinct-care-institution), [legal/care distinctions](GOON_INSTITUTIONS_AND_RECOVERY.md#continuity-and-fictional-legal-contract) | Approved design direction separates care, custody, supervision, visitor/work roles and consent. Named staffing/era remains a proposal. | Conviction does not authorize psychiatric confinement or make Harley perpetually present. Joker initiation is a different campaign proposal, not this route. |
| [Warren White identity](GOON_ROGUES_GALLERY_REGISTRY.md#24-great-white-shark), [organization O07](GOON_FACTION_EMPLOYER_MATRIX.md#organization-classification-and-leadership-matrix) | Existing research distinguishes Warren White from King Shark and proposes bounded business/network relations. | A canon Waller alliance, government office, Squad membership requirement or personal veto over federal policy. |
| [M019 source adapter](../institution_sources.py#L1), [institution contract](GOON_INSTITUTIONS_AND_RECOVERY.md#m019-implemented-intake-and-knowledge-contract) | Source observations, receipt/order, credibility/limits and targeted corrections for two existing incidents/desks. | A universal criminal-record database, government inbox, medical-record permission, recruitment report topic or Waller knowledge. Existing desks cannot accept arbitrary new sources. |
| [Service](../game_service.py), [persistence](../career_persistence.py), [content architecture](GOON_CONTENT_ARCHITECTURE.md) | Atomic candidate commands, rejection purity, read-only projections, separate travel, versioned optional adoption and validated historical saves. | A new command/event/marker is not authorized by this document; raw snapshots are not actor/player knowledge. |

No numeric qualification is selected. Several necessary domains are absent;
the route cannot currently be truthfully evaluated or enabled. All later
qualification results must support **proven / not satisfied / unknown**, not
default missing fields to success.

## 2. Canon and continuity context

Narrow **publisher-backed anchors** below were researched for this addendum.
Profiles can compress eras; solicitations support their stated premise, not an
inspected full story. No full comic, film, episode or licensed sourcebook was
reviewed, and no dialogue, scenes, assets or mission plot is copied. Some direct
pages returned 403 after indexed text was available. Identities, offices, custody,
deaths and roster membership require an approved compatible era before use.

| Context / identity | Source-supported anchor | Continuity limit and original proposed use |
| --- | --- | --- |
| C01 **Amanda Waller**, proposed dc.character.amanda_waller.comics_candidate | Political operator associated with the modern Task Force X and incarcerated recruits; not a superhuman omniscient observer. [DC profile](https://www.dc.com/characters/amanda-waller). | The later [Secret Six #1 premise](https://www.dc.com/comics/secret-six-2025/secret-six-1) puts Waller in jail. Do not assume the profile is a current universal office roster. Proposed remote decision-maker only when available and actually briefed. |
| C02 **Task Force X / Suicide Squad**, proposed dc.organization.task_force_x.waller_era_candidate | Covert dangerous operations, expendable personnel and sentence-related bargains in the [DC team profile](https://www.dc.com/characters/suicide-squad). | Historical first-appearance/earlier-team material is not one unchanged Waller-era program. This route is an original voluntary assessment proposal, not a universal canon recruitment rule. It is not a normal street faction, free join menu or Creature Commandos membership. |
| C03 **Rick Flag Jr.**, proposed dc.character.rick_flag_jr.comics_candidate | The [publisher profile](https://www.dc.com/characters/rick-flag) distinguishes a younger military leader from his father. His expertise is not a criminal-history qualification shared by all members. | Select era/life state and authority. Proposed assessor/operational liaison, not a guaranteed chaperone, personally available rescuer or shortcut to training. |
| C04 **Rick Flag Sr.**, index.character.rick_flag_sr.context_only | [DC's separate history](https://www.dc.com/blog/2025-08-15/the-ballad-of-suicide-squad-founder-rick-flag-sr) distinguishes the father and his screen-universe roles. | Context-only alternate handler/office reference. Never merge father/son, all adaptations or Task Force M with this proposed Task Force X route. No new playable roster is implied. |
| C05 **John Economos**, proposed dc.character.john_economos.comics_candidate | DC identifies a comics Belle Reve warden history and a distinct screen technical/handler role. [Publisher comparison](https://www.dc.com/blog/2022/01/12/peace-posse-meet-the-characters-of-hbo-maxs-peacemaker). | The chosen role/era determines actual record/custody authority. Potential records intermediary, not both every warden and every agency's omniscient system administrator. |
| C06 **Emilia Harcourt**, proposed dc.character.emilia_harcourt.pending_continuity | The [same DC comparison](https://www.dc.com/blog/2022/01/12/peace-posse-meet-the-characters-of-hbo-maxs-peacemaker) describes screen agency work and a different comics history; [a later comics solicitation](https://www.dc.com/comics/batman-the-brave-and-the-bold/batman-the-brave-and-the-bold-5) changes her life-state premise. | Do not combine jobs, allegiance, death/return or orders across portrayals. Optional liaison candidate only after approval, never automatically present. |
| C07 **A.R.G.U.S.**, proposed dc.organization.argus.pending_continuity | An agency association is explicit in the [screen personnel account](https://www.dc.com/blog/2022/01/12/peace-posse-meet-the-characters-of-hbo-maxs-peacemaker); Flag Sr.'s [later office is version-specific](https://www.dc.com/blog/2025-08-15/the-ballad-of-suicide-squad-founder-rick-flag-sr). | No assumption that it supervises all police, courts, prisons or health care. Specific mandate/authorization and message path must be authored. It is not another criminal district owner. |
| C08 **Belle Reve**, proposed dc.institution.belle_reve.squad_candidate | Associated with the program in [DC's team profile](https://www.dc.com/characters/suicide-squad). | Not Blackgate, Arkham, a new atlas record, current player prison or automatic transfer destination. A proposed custodial/administrative role needs an approved location/access/transfer contract. |
| C09 **Government recruitment liaison**, index.role.task_force_x_liaison | **Original vacant role**, not a newly invented canonical named officer or existing implemented staff member. | A verified ordinary intermediary can carry a limited file/invitation; no need for Waller to personally visit every candidate. Documents must establish identity, mandate and reporting scope. |
| C10 **Floyd Lawton / Deadshot**, existing dc.character.deadshot.floyd_lawton | Expert non-superhuman marksman and a Waller-era recruit in [DC's profile](https://www.dc.com/characters/deadshot). | Non-superhuman does not mean an untrained worker equals Lawton. A referral can report only actual experience. Later [Arkham-game identity history](https://www.dc.com/blog/2024/03/11/suicide-squad-kill-the-justice-league-reveals-whatever-happened-to-the-arkhamverse) must not overwrite the comics candidate. |
| C11 **Harleen Quinzel / Harley Quinn**, existing dc.character.harley_quinn.comics_candidate | Arkham professional history, independent phases and Squad association in [DC's profile](https://www.dc.com/characters/harley-quinn). | Former practitioner, patient, visitor and current Squad member are not simultaneous default jobs. Arkham-game recruitment in [DC's tie-in FAQ](https://www.dc.com/suicide-squad-faq) is adaptation-specific, not this game's confinement law. |
| C12 **Warren White / Great White Shark**, existing dc.character.great_white_shark.warren_white | Financial criminal/underworld influence, distinct from King Shark, in [DC's account](https://www.dc.com/blog/2023/07/24/seven-dc-sharks-who-are-not-king-shark-and-may-not-even-be-sharks). | No reviewed source establishes him as this program's handler, mandatory recruiter or government veto-holder. Merchandise, a related-character card or themed in-game item is not membership/authority proof. His eligibility condition below is an original Goon risk check. |

**Canon coercion versus player agency:** published portrayals include coercion,
expendability and lethal control devices; this design does not pretend Waller is
a benevolent employer. Nevertheless, the user's proposed player pathway requires
informed, voluntary acceptance. No surprise implant, compelled deployment,
irreversible agreement or punishment for merely refusing screening is authorized.
Any later depiction/mechanic involving coercive control requires separate approval
and a recovery/consent contract. No such device, combat or mission is designed
as an executable feature here.

## 3. Special five-condition eligibility contract

**Preserve all five as a conjunction for this special route.** They are original
campaign prerequisites, not claims that DC canon requires every Squad member to
have these experiences. Meeting them permits consideration, not guaranteed
identification, invitation, acceptance, sentence relief or deployment.

| Condition | Proposed meaning and proof | Reusable state versus missing authority |
| --- | --- | --- |
| E1 **Substantial documented criminal record** | Distinct corroborated resolved convictions, relevant conduct/context and an attributable record review; dismissals, allegations, raw heat and repeated copies of one case cannot qualify. “Substantial” requires an approved qualitative gravity/variety/relevance policy, not invented numbers or crime grinding. | Existing legal.record/cases/outcome receipts supply a limited starting record. They lack severity, full sentence/conditions and authorized government transmission. Preserve unknown historical dates/fines; do not infer serious violence from collection jobs or fine size. |
| E2 **Several consequential Deadshot encounters** | Multiple distinct actual Lawton event contexts with decisions and lasting, evidenced consequences: e.g. reliability, discretion, safe refusal or a disputed obligation. Repeated greetings, stage selections within one episode, proxies and the same retold outcome do not multiply encounters. Number/variety remain approval items; no mission completion guarantees friendship/referral. | Existing Deadshot chain is paper-only; incident receipt/source patterns are reusable, but no qualifying encounters exist in runtime. Ordinary job success, NPC metrics and rumors are not substitutes. |
| E3 **Appropriate Harley Quinn interaction in an Arkham storyline** | An actual meaningful interaction with the selected available Harley under a documented lawful visitor, professional, investigative or separately justified narrative access basis. Specify what was observed/earned and who may transmit it. No romance, violence, loyalty to Joker or patient status is required. | No present Arkham encounter/admission/work history or Harley actor. Navigation frontage/permission cannot prove a meeting. Conviction alone never authorizes psychiatric confinement. A remote proxy is not falsely labeled this encounter. |
| E4 **No unresolved severe hostility with Great White Shark** | Proposed operational interpretation: no current, corroborated severe conflict/threat or major unresolved breach affecting the contemplated role; not a requirement for affection, payment or friendship. Define severity, scope, closure and stale/contested evidence before implementation. Do not read an unobservable private feeling as a government fact. | Current relationship metrics are not White-specific. A scalar cutoff, missing actor, quiet days or a self-authenticating “cleared” boolean cannot prove the condition. Use actual sourced dispute/closure history and an appropriately limited review. This is risk assessment, not White controlling Waller. |
| E5 **Compliance with applicable parole/probation conditions** | Link the actual sentence/order, issuer, dates, current conditions and recorded review/completion/approved changes. Only applicable conditions count. A supported finding that no active order applies is **not applicable**, not an obligation to obtain probation first. Missing/unknown records are not compliance. | Neither probation nor parole is implemented. Current free custody, paid fines, low heat and absence of a condition field cannot certify compliance. No new supervision or historical violations are fabricated. An assessed/paid fine difference alone creates no new breach. |

Each condition needs a source-backed **proven / not satisfied / unknown** result.
For E5, supported “not applicable” satisfies only applicability, without granting
a sentence reduction. False or contradictory documents remain claims until
reviewed; an assessment can be provisional or wrong without rewriting world truth.
Unknown is a reason for verification/deferment, never silent success or permanent
failure. No present career can automatically satisfy this future route.

Qualification and government knowledge are distinct: a private history does not
brief Waller. Formal route certification must cite legitimately received,
corroborated evidence with known scope/order; hidden truths cannot secretly drive
her rejection reason or invitation timing. A limited risk review does not prove
universal absence of hostility. New contradictions prompt a sourced review,
not an omniscient retroactive rewrite of a prior receipt. Exact E4 coverage/
negative-evidence rules remain an explicit approval dependency.

General safeguards still apply: actual program need/capacity and lawful
institutional authority, actor availability, fit for a bounded ordinary role,
legitimate access, and the player's separate informed choice. Assessment,
qualification, invitation, consent, institutional clearance, assignment and
membership are different milestones. No predicate creates an offer by itself.

## 4. Institutional logic, access and supervision

Arkham is a care institution; Blackgate is a prison in the existing contract;
Belle Reve is a separately researched program setting. One is not an alias or
automatic next level of another. A criminal record can coexist with voluntary
care, or no psychiatric care at all. Treatment, custody, release and supervision
have independent authorities and reviews.

For the special Harley condition, a plausible approved episode could use an
authorized service job, witnessed visit, advocate-supported investigation or
other specifically justified story access. Record role, permitted area, purpose,
receiving authority, actual Harley availability and exit. A public reception
visit is not inpatient access, Harley may decline, and care/release continues if
she is absent. No repeated voluntary admission, manufactured symptoms, crime
spree or institutional cycling should improve eligibility. Existing Joker
initiation is separate and cannot substitute for this route.

An assessment invitation does **not** waive curfew, prohibited contacts, travel
limits, appointments, custody or other actual conditions. If terms conflict,
request an explicit authorized modification/temporary permission/transfer under
the future fictional institutional rules, defer, use an eligible local channel,
or decline. A handler's promise is not a release order. Any later relief must
identify issuer, authority, scope, timing, conditions and actual decision; old
convictions/history are not erased and no broad immunity is granted.

These are fictional project rules, not real-world legal advice or a claim that
all DC depictions give government operatives lawful authority. A shady proposal
can be investigated or reported; its existence does not validate its claims.
Do not implement a universal legal or medical access bypass.

## 5. Knowledge, recruitment provenance and causal ordering

Reuse existing domain sources where sufficient, but do not create another
authoritative history or copy a whole career into an agency dossier. The model
below is conceptual, not a proposed current save schema.

| Layer | What belongs there | Required channel / limitation |
| --- | --- | --- |
| World truth | Actual cases/outcomes, encounters, available actors, disputes, conditions and decisions | Domain-owned facts; a player command receipt is not automatically a government observation |
| Source observations | A dated/order-backed record copy, actual interview, witnessed act or consented referral with author/limits | Link to the originating authority/episode; a saved boolean, copied summary or identical second transmission is not independent corroboration |
| Government intelligence | Information a particular authorized office actually receives, with scope, credibility, disputed parts and correction status | Court/corrections record request or permitted referral; no automatic access to therapy, all faction memories, undiscovered events or every police record |
| Waller's knowledge | Specific briefing and decisions that reach the selected available Waller | Received subset, delivery timing and permitted scope; she can distrust, misread, decline or lack capacity, never query raw world truth |
| Criminal-network rumors | What a named criminal/contact heard, including false/partial/stale recruitment stories | Actual transmission/observer; White, Harley and Lawton do not share one mind or learn all government decisions |
| Player knowledge | Received invitation, verified issuer details, disclosed terms, known prerequisites and actual replies | Do not reveal covert rosters, private screening notes or secret hostility through previews, unavailable reasons or the master index |
| Corrections / actions | Named recipients receive a correction or authority decision after a source-backed action | Update that recipient's view prospectively; preserve original receipt/history and do not silently correct all audiences |

**Example provenance chain, original:** a permitted officer receives a court
outcome copy. A later, specifically authorized Lawton reference states only the
work/reliability he witnessed. An Arkham episode yields a limited statement of
the actual Harley interaction through an allowed participant/record channel,
not a confidential medical-file dump. A role-specific risk review checks
attributable White conflict/closure evidence. The responsible officer obtains
the actual supervision order/review or supported non-applicability finding.
Only the authorized selection packet reaches Waller; a mission brief later
given to the player is another distinct transmission.

If Harley or Lawton does not transmit private experience, it is not in the file.
Verification may seek an independently permitted witness/source; it cannot fake
the encounter or force either character's cooperation. A rumor from White can
trigger inquiry, not prove criminal guilt or a clean operational relationship.
Medical confidentiality and a document's legal authority must be stated, not
assumed from a seal, name or the word “classified.”

Order matters: an officer cannot rely on a document before receipt, Waller cannot
use a later corrected fact in an earlier decision, and a player cannot accept an
offer not yet delivered. Duplicate/reordered/unsupported references must fail
future source validation. No prototype M019 desk is silently expanded to process
this file; a narrow new approved source/mandate adapter would be necessary.

## 6. Recruitment event — four bounded stages

One independent demand/candidate-selection cause can proceed without the player
discovering it. Sort stable identities and record any approved deterministic
selection; viewing/declining/reloading cannot reroll it. This is a lifecycle
proposal, not new event IDs, implementation or a general government simulator.

| Stage | Independent facts / player choices | Costs, risks, possible reward and authority |
| --- | --- | --- |
| **A — Identification** | An authorized intermediary receives scoped records/referrals, identifies possible role fit and records unresolved checks. Waller need not personally know or meet the candidate. Demand can vanish before contact. | No cash, membership, completed prerequisite or government omniscience from a background scan. Selection may remain unknown to the player. No arrest-farming invitation guarantee. |
| **B — Assessment** | Deliver an attributable discreet invitation through a plausible accessible channel. Player can inspect known terms, authenticate issuer, seek an advocate, ask for a local/authorized interview or ignore it. Check actual consent/access/custody and source timing. | Active verification/interview uses a bounded disclosed commitment from the existing action allowance; exact per-option costs require approval. No fee to view/refuse, hidden automatic agreement, mandatory commute, implant or free stat training. Contact may create a specific confidentiality/relationship issue only when actually communicated. |
| **C — Decision** | Investigate, negotiate role/terms, refuse, report to an appropriate authorized recipient, or accept a specific offer. Read back actual obligations, uncertainty, exit/review, funding and any required institutional permission. Acceptance is separate from assignment/deployment. | Negotiation/reporting competes with ordinary time/opportunities; exact costs remain unapproved. A genuine revised offer has the same causal history, not a reward/reroll loop. Refusal remains possible without money or remaining actions. No valid permission means defer/decline, never automatic breach of supervision. |
| **D — Consequences** | Record one explicit outcome and actual recipients. A consented provisional arrangement still requires qualification, lawful/fictional institutional clearance and a separately authorized bounded role. Program withdrawal, partial assessment or player absence can close the episode independently. | Possible funded expense/pay/reference or a specifically approved review request, never guaranteed relief/reward. Preserve costs already legitimately incurred and unresolved disputes. No universal criminal/hero alignment or deletion of prior cases. |

### Consequence matrix — distinct futures, not reward colors

| Outcome | Observable consequence | Persistent future / recovery |
| --- | --- | --- |
| **Accept specified terms** | Acknowledged consent, role boundaries, known secrecy obligations and clearance status; no immediate battlefield deployment | Limited future consideration/assignment under actual authority; ordinary obligations, history and right to reject a different undisclosed role persist. Payment/relief only if actually authorized and achieved. |
| **Negotiate** | A recorded request and a specific revised offer, denial or deferral | Different role, narrower disclosure or later lawful interview may be possible; no guaranteed concession, payoff or reroll. Original terms are not accepted by asking questions. |
| **Investigate / seek advice** | A permitted issuer/authority/source check supplies information or remains unresolved | Better-informed acceptance/refusal/report, one recipient's credibility change; no penalty for discovering a forgery, and no disclosure of private agency notes. |
| **Refuse / withdraw before accepting** | This opportunity closes or is explicitly deferred | No new sentence, implant, fine, debt, forced crime or retaliation solely for refusal. Specific officials may remember the decision, but lawful work/reform/survival remain. No implied promise to the program. |
| **Report a credible concern** | A real oversight/advocacy recipient receives the actual statement and its limits | Review or a protected alternate channel may follow; not automatic immunity, global scandal, promotion or punishment. Future secrecy consequences require actual accepted terms/acts and compatible rules. M019 intake is not already that recipient. |
| **Fail / partial assessment** | A specific competency, authority, capacity or source gap is explained within what the player can know | Narrower support role, new evidence review or ordinary exit; no death sentence, psychiatric admission or faction lock for failing an interview. Distinguish a capability limit from bad faith. |
| **Miss / ignore / independent cancellation** | Offer expires or issuer capacity changes on its recorded cause/window | No invented acceptance, desertion or promise failure. A later genuine need can create another review; not daily rerolls or permanent loss of all future consideration. |
| **Betray accepted terms / be cheated** | Record actual disclosure, harm, false claim or breached undertaking and who learned it; an accusation is not proof | Specific trust/access loss or a supported future investigation, with review and bounded safe exit. No omniscient agency/White revenge, retroactive new terms or global outlaw status. Someone else's deception does not equal player consent. |

## 7. Ordinary-person balance and restricted operations

The first credible role would be bounded support/verification/liaison work tied
to demonstrated knowledge or reliability, not being sent alongside superhumans
because a crime counter rose. Lawton and Flag are highly trained non-metahumans;
their existence is not evidence that the protagonist receives their training,
gear, combat skill, powers or survivability by signing a form.

Potential future operations carry danger, limited extraction/communications,
uncertain support and competing obligations. A disclosed support role can still
fail or be canceled, but reassignment into undisclosed high-threat combat needs
separate consent/design. No combat, injury, undercover or mission-execution system
is authorized here. If an episode needs those missing systems, defer it instead
of inventing invulnerability, instant healing or a guaranteed rescue.

Operational secrecy is limited to actual delivered material and knowingly
accepted terms, not magical silence or immunity from all public records.
Compensation needs a real funded authority and one settlement receipt; a
promised review/commutation is not an approved sentence change. Keep ordinary
wages, housing, debts, care and legal outcomes authoritative. No repeat stipend,
recruitment signing-bonus farm, paid rerolls, contact grinding, real-time upgrade
timer or compulsory criminal acts to unlock a better life.

## 8. Alternate paths and softlock analysis

**Recommendation, not approval:** preserve E1–E5 as the named special route,
and allow a separately authored, equally source-backed institutional assessment
route when a specific famous encounter is unavailable. Alternatives do not mark
the missing special conditions complete or guarantee Squad membership.

| Blocker | Special route remains honest | Proposed alternate opportunity / limit |
| --- | --- | --- |
| Missed/unavailable Deadshot episode | E2 stays unmet/unknown; no substitute actor, proxy or repeated greeting | Another genuinely distinct future Lawton cause may occur; an authorized corrections/capability referral could reach a separate assessment route without pretending it is a Lawton meeting |
| Harley absent / no valid Arkham role | E3 not complete; no forced psychiatric admission or endlessly extended custody | Later lawful visit/work opportunity if compatible; or separate institutional referral based on actual records and relevant support competence |
| Severe White conflict or disputed history | E4 not erased by money, unrelated good deeds, elapsed days or a forged “peace” flag | Evidence-based resolution/mediation if safe and voluntarily chosen, or consideration for a genuinely different role/network through another assessment route. No need to perform harm for White |
| Applicable supervision conflicts with meeting/work | E5 not waived by Waller's name | Seek actual authorized modification/local interview, defer until lawful review/completion, or decline. Do not require a violation to progress |
| Old save lacks proof | Preserve unknown history and current behavior | Obtain legitimately available later records/prospective experience under a future adoption contract; do not invent past meetings, sentence conditions or dates |
| Candidate lacks program need/fit, or Waller unavailable | No automatic invite despite a completed checklist | Program may remain unavailable; ordinary careers/endings remain complete. An appropriate later handler/demand requires an actual new cause, not a reset persona |
| Player refuses the program | No surprise recruitment or all-career lock | Respect refusal; later reconsideration requires player choice and a genuine eligible offer, not harassment/referral spam |

A separate institutional route would still need demonstrated suitability,
attributable records/referrals, relevant role demand, actual authority, applicable
supervision compliance, informed consent and limited risk review. Whether it is
a full recruitment route or only a nonmember cooperation path is an approval
decision; a civilian service job must never silently become Squad membership.
No pure “pay/join/reputation” shortcut or universal entitlement to recruitment.

One missed scene must not softlock the entire game or all future consideration.
That does not require every continuity to supply every famous actor or guarantee
this optional program. Repaired relations, a later independent need and an
approved alternate route preserve credible possibilities rather than respawning
people, resetting failures or retroactively changing qualifications.

## 9. Future roadmap, dependencies and acceptance — not implementation

1. **Define and approve foundations:** compatible Waller-era/agency/corrections
   authority; criminal-record interpretation; sentence/supervision applicability
   and review; source-backed named encounters/relations and lawful institutional
   access. No large global NPC or legal rewrite merely to force recruitment.
2. **Smallest later slice:** one verified government-intermediary assessment,
   one scoped record/referral channel, a noncombat role-fit question, negotiation/
   refusal/report options and ordinary recovery. Offer no deployment, release
   change or membership until its own dependencies/authority are approved.
3. **Then consider the special route:** only after distinct Deadshot/Harley
   episodes and White conflict evidence genuinely exist, evaluate E1–E5 under
   explicit future adoption/validation. Review an alternate route at the same time.
4. **Operations later and separately:** risk, support, travel, institutional
   permissions, funding and any combat/health/mission needs require their own
   bounded contract. No M021 number or gameplay is assigned by this document.

Existing service/incident/source/ledger patterns are integration seams, not a
new government backend. Use stable identities, pinned definitions, actual cause/
command/order references, idempotent independent progression and exactly-once
effects. Inspection/rejections must not mutate state/RNG or refresh allowances.
No direct UI write, extra faction tick, new ordinary-life gate or automatic
historical adoption. Missing old facts stay missing under an explicit future
compatibility policy. Do not rename existing events or alter replay fingerprints.

Future acceptance must test five-condition conjunction and unknown handling;
convictions versus dismissed/pending cases; no heat/job-count/arrest farming;
distinct encounters versus duplicate stages; Harley absence/role/access;
White conflict/closure and scoped negative evidence; each actual supervision
condition, supported non-applicability and permission changes; government/
Waller/criminal/player knowledge separation; forged, reordered, duplicate and
late-corrected sources; all decision outcomes; independent cancellation;
same-cause retry purity; once-only pay/membership/relief; consent and ordinary
recovery; deterministic replay/disk resume; historical unknowns and explicit
adoption; stable budgets and unrelated legal/economic outcomes. These are
**unexecuted future test requirements**, not present test claims.

### Protected progression and other programs

The Court of Owls remains wholly separate under its
[existing final-third meaningful-progression secrecy rule](GOON_ROGUE_ENCOUNTERS_DESIGN.md#mission-026-approved-roster-restriction--design-only).
No dossier, agency briefing, rumor, assignment, handler, source lookup, symbol,
Talon, metadata hint or supposed government clearance may reveal it early or
create a new access route. Task Force X is not its recruitment ladder or gate.
No such player content is introduced. DARK, Joker initiation and Creature
Commandos are also separate; none automatically qualifies or enrolls the player.

## 10. Decisions requiring user approval

1. Select compatible comics/screen era, active Waller/Flag variant, agency mandate
   and institutional authority; decide whether Economos/Harcourt are present at all.
2. Define “substantial” record by meaningful severity/variety/relevance and a
   historical-unknown policy; no numeric crime/conviction/heat cutoff is approved.
3. Define “several” distinct consequential Deadshot contexts and permissible
   evidence/referrals without demanding assassinations or inventing thresholds.
4. Approve the Harley Arkham story role, lawful access basis, qualifying interaction
   and source-sharing consent, with an ordinary care/release path if she is absent.
5. Define severe/unresolved White conflict, review scope, corroborated closure,
   stale/hidden evidence and unknown handling without omniscient negative checks.
6. Approve actual supervision/order conditions, non-applicability proof and who
   can modify restrictions or grant a narrowly scoped later review/relief.
7. Decide which alternate institutional route exists and whether it can lead to
   membership or only separately consented nonmember cooperation.
8. Approve assessment role, action/time costs, finite opportunity windows,
   verifiable issuer, secrecy boundaries, funding/rewards and recovery terms.
9. Resolve canon coercion versus the voluntary player pathway, including any
   future control-device/depiction/withdrawal proposal; nothing is preauthorized.
10. Approve one later implementation slice, domain/source adapters, version/adoption
    and replay contract before any code, operations or legal expansion.

## 11. Paper scenario and gameplay-value review

An original intermediary offers to verify a candidate's records for a narrowly
scoped support vacancy. They possess a legitimate court copy and a limited
reference, not private conversations or medical notes. The player can authenticate
the office, seek an advocate, negotiate a local interview that respects actual
conditions, report a suspicious discrepancy, decline, or accept only the disclosed
assessment. An unavailable Harley record keeps the special route unresolved;
it does not prolong custody. A separately approved institutional route could
still assess genuine support competence without falsely completing E3.

Acceptance may create one bounded obligation/reference; refusal preserves ordinary
work; negotiation can change terms or fail; reporting informs a specific recipient;
an independent cancellation pays no fictional signing bonus. Different sources,
competing commitments, legal permissions and issuer reliability create variety,
not larger reward multipliers. Remaining shallow areas are authored assessments,
unapproved qualifications and absent sentence/rogue systems. No new meaningful
player decision or persistent consequence is implemented by this documentation.
