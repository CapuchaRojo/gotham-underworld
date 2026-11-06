# Gotham: The Goon — Institutions and Recovery

**Status: M019 implements only the bounded intake/service desks below.** The
prison, care, supervision and recovery sections remain an M013.1 proposal.
M013 currently has accelerated
arrest/court resolution and a legal record, not prison episodes, psychiatric
admission, counseling, parole or treatment. These proposals do not change current
custody rules or authorize M014 expansion. They describe fictional Gotham rules,
not real legal or medical procedure.

## M019 implemented intake and knowledge contract

Mission 023 builds on merged M018 `d0723b1551fc4e1aedf2d0fa4a5b5e3758902f49`.
M017-B reached master through PR #18 (`8bc9700`); M018 through PR #19 (`d0723b1`).
M019 is local on `feature/m019-institutional-response`; no publication or merge
is authorized. This section describes executable behavior, not real procedure.

| Actor | Place / routine | Authority |
| --- | --- | --- |
| Neighborhood Civilian Desk, original clerk Ruth Bell | Public n13 counter; one daily board/resident round; one day to process a received report | Local notice and safety records, clarification, one dated correction copy for a documented delivery matter. |
| GCPD Intake Desk, original intake clerk Niko Shah | Existing public counter p044; next-day forwarded copies of Ada's actually delivered reports; two days to process | Log, classify and acknowledge alarm observations. No offender identification, guilt, case creation, warrant or arrest. Delivery administration belongs at the civilian desk. |

Names, staff, places, mandates and delays live in a separate pinned JSON pack;
mechanics use stable institution IDs. The public counter adds no access to
restricted interiors. Existing daily-life contacts/standing are unchanged.

### Explicit adoption and causal knowledge

`enable_institutions` requires active daily life and freedom. It costs zero and
refreshes neither the three gameplay actions nor eighteen travel units. Loading
an old career never adopts. Optional `institution_version: 1` / `institutions`
pins rules/content without changing the outer save version or old event IDs.
Compatibility is old-to-new. Use an M019-capable executable throughout an adopted
career; advancing it in an older executable is not supported.

Institutional knowledge is built from **received sources**, not world truth:

1. The world still owns the alarm cause and true delivery date.
2. An ephemeral source adapter replays existing incident transitions, finding
   actual public notices, observations, owner reports and issued circulars.
3. Each institutional transmission names its source event, observer, observed
   day, recipient, route, received day, credibility/limitation and processing day.
4. A desk keeps its own reports, beliefs and unresolved contradictions. Multiple
   conflicting unchecked dates request clarification, rather than choosing one
   because it matches world truth. Documented support can resolve a contradiction;
   the old claims and causal references remain recorded.
5. The player receives only their submission acknowledgment and explicit local
   follow-up snapshots. Automatic queue work stays out of service/CLI player
   events. Remote views retain receipt-time information; previews at a counter
   can explain its current submission policy without committing any interaction.

The civilian round collects the Wrong Notice board claim and Sam's actual
handbill, then later the issued public circular. It can also read the existing
shop alarm notice. The intake forwarding route copies the original incident
desk's received owner alarm report and later owner review. This is a new explicit
copy, not a rename of the legacy Civic Police desk or automatic sharing of all
its knowledge. Neither desk sees private inspections, player withholding, the
other desk's records, or unrelated contact memories unless supported transmission
actually occurs. A cause observation remains an observation, never legal guilt.

Only source events **after adoption** trigger automatic rounds/forwarding. Late
adoption does not fabricate old institutional records. A player may explicitly
submit an observation acquired earlier if its genuine source history survives.
Institutional replies are secondhand records in their own player journal; they
do not backfill the old incident's primary-inspection facts or unlock expired work.
A genuinely handed-over dated correction copy is an explicit, one-hop exception:
it becomes a documentary source usable at the civilian desk. Its source is the
actual received response, independently reconstructed during validation, not a
saved assistance flag. It lets a player repair an old desk record after the
original incident windows expire, without rewriting that incident or granting
another copy, reward or automatic recipient update.

### Player commands and consequences

All mutations use `game_service.execute_command`. Counter commands recheck
current location, lawful access, freedom, remaining actions and actual source
knowledge. CLI aliases `civilian` / `intake` resolve to stable actor IDs.

| Command | Cost and effect |
| --- | --- |
| `institution_submit(institution_id, source_id)` | One action at the appropriate counter. Submit an actually observed claim; the claim may be incomplete or false. An acknowledgment is not endorsement. No cash reward. |
| `institution_correct(institution_id, report_id, source_id)` | One action. A known original report at this recipient needs documented, conflicting evidence for the same incident/topic. Own queued reports can be corrected; another sender's report must first be received in a local follow-up. No correction chains or repeated corrections. |
| `institution_followup(institution_id, incident_id)` | One action at the counter for a known incident and an unread response version. Receives queued/clarification/closed/documented records and their limits. A documented civilian delivery matter issues one correction copy, recorded as assistance, not inventory, money or a world-wide correction. |
| `institution_withhold(institution_id, incident_id)` | Zero actions, once per known matter. Private player intent only; no notice to the institution, promise, debt, penalty or permanent refusal lock. |

Credibility is local administrative access, not a second faction/contact meter.
An actually contradicted, uncorrected player claim puts that desk's unchecked
submission route under `needs_documentation`. Documentary submissions remain
possible; a processed verified correction repairs the record. A supported player
record establishes `documented` access. The other desk and ordinary careers are
unaffected. There is no score stacking or payment for reporting.

### Bounded independent operation and validation

After existing daily life and incident phases, each received source queues once.
No new daily action is charged. Due work processes once per day; unanswered
matters close for insufficient information after three clarification days.
Additional unchecked reports do not extend that deadline. A later genuine
document can reopen/resolve the record. No automatic notification spam or global
clock is added. Closed idle queues generate no daily history. The two one-shot
incidents provide a finite source set; each recipient/source and original
correction settles once. Follow-up cannot repeatedly grant assistance.

Replay validates source availability at transmission time, original command
frames and completed movement, recipient, delay, processing order, response
snapshots and the final state. Recorded flags are not proof of source knowledge.
Receipt/processing days must match the day already established by prior domain
events; source acquisition and arrival cannot come from a later day. This is
ephemeral proof over the existing log, not another clock or saved history.
Mission 024 additionally verifies every player-observation catalogue entry,
including unsubmitted and pre-adoption observations. Each acquisition must sit
inside its own completed, player-attributed command frame. Its location must
follow completed player travel/journey receipts at that acquisition, not a later
counter visit. Historical anchor adoption must likewise finish in its own
player command before activation. A later submission cannot legitimize an
unverifiable acquisition, nor may a preview offer one as available evidence.
Unverifiable/contradictory edits reject without changing the save. This proves
consistency, not cryptographic authenticity of a completely rewritten career;
it does not reconstruct all historical legal/access/action predicates.

The existing atomic writer/backup is reused. No rent, wages, heat, investigations,
custody, faction resources, travel policy or old incident settlement is changed.
See [content architecture](GOON_CONTENT_ARCHITECTURE.md),
[incident integration](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md) and
[M019 validation](M019_INSTITUTIONAL_RESPONSE_VALIDATION.md) for executed evidence.

## Continuity and fictional legal contract

The [Task Force X proposal](GOON_TASK_FORCE_X_RECRUITMENT_DESIGN.md) reuses these
institutional distinctions without implementing prison, care or supervision.
Its Harley/Arkham condition requires actual authorized access and an appropriate
available actor, not psychiatric confinement from conviction. Blackgate, Arkham
and the separately researched Belle Reve are not interchangeable. A government
invitation does not waive actual sentence/conditions; modification/transfer or
any relief needs its own explicit authority. Missing supervision data is not a
compliance certificate. Existing M019 desks do not already process this new topic.

Before implementation, choose a versioned project continuity and document each
institution's mandate, available staff/characters, admission authority, review
interval, confidentiality exceptions and release/transfer rules. No continuity
is selected by this milestone. Do not combine incompatible versions of a named
character or assume one universal DC sentencing/admission law.

Broad anchors only: DC describes Blackgate as a prison in the
[Arkham Origins Blackgate setting](https://www.dc.com/games/batman-arkham-origins-blackgate-2013)
and Arkham as a psychiatric institution in its
[Gotham location guide](https://www.dc.com/blog/2021/03/29/take-a-tour-of-batmans-hometown-with-exploring-gotham-city).
These references establish setting motifs, not the fictional admission,
protection or release rules proposed here. No published prison plot is copied.

Treat criminal custody, care/admission and legal supervision as separate axes.
Someone can have a criminal record while seeking voluntary counseling, or receive
psychiatric care without a conviction. Conviction alone never commits someone
to Arkham; a symptom tag, employer accusation or villain influence alone never
authorizes detention. Fictional lawful commitment requires its own qualifying
facts, independent assessment, recorded authority, representation and review.

| Path | Proposed entry authority/prerequisite | Player choices and protections | Proposed reviewed exit |
| --- | --- | --- | --- |
| Criminal incarceration / Blackgate | A custodial outcome under separately approved fictional court rules | Understand sentence, contact advocate, choose work/education/associates, seek appeal; finite review date | Release at recorded term, successful appeal, or an explicitly authorized transfer |
| Court-ordered evaluation | A specific recorded order and question under the selected legal rules | See purpose/limits, request advocate or independent assessment, contest errors | Completed evaluation returns to the appropriate legal/care path; no automatic commitment |
| Lawful psychiatric commitment | Qualifying facts plus independent authorized decision and time-bounded review | Explain decision, appeal, care choices within actual restrictions, protected contact | Reviewed discharge, less restrictive care or lawful transfer with recorded reasons |
| Institutional transfer | Distinct receiving criteria and recorded legal/care approvals | Notice, access to advice and challenge, preserve medical confidentiality boundaries | Receiving authority accepts; missing criteria retain the valid prior state |
| Voluntary admission | Informed agreement to an eligible care plan; no arrest required | Choose consent scope, ask questions, seek another practitioner, request discharge/review | Agreed discharge process or separately justified lawful review; never a surprise indefinite hold |
| Voluntary outpatient counseling | Player request and an available ethical provider | Goals, confidentiality terms, practical support and provider choice | Continue, change or end care with a safety/support plan |
| Parole / legal supervision | A distinct conditional-release order under future rules | Understand conditions, review appointments, seek modification and lawful work | Scheduled completion/review; violations require facts and process, not automatic game-over |
| Story visit / institutional work | A valid visitor, employment or investigation opportunity | Refuse a task, retain visitor status and leave within known safety rules | Normal departure; presence is not admission or custody |

These are normative project proposals, not assertions about current game state,
all DC stories, or actual jurisdictions. Specific legal eligibility and review
durations require a later design contract; indefinite forced waiting is prohibited.

## A. Blackgate as a playable chapter

Incarceration should change the player's work and social context without erasing
their personhood. Propose a finite episode with a small number of authored
decisions per advanced day, a clearly displayed review/release horizon, and an
explicit option to advance through uneventful time. The outside city continues
on its existing daily pipeline exactly once. No real-world timer or prison-chore
quota is necessary to reach release.

| Experience | Decision | Observable and persistent effect |
| --- | --- | --- |
| Prison relationships | Help, refuse, mediate or seek support | Specific trust, boundaries and future contacts; no universal prison loyalty stat |
| Rival recruitment | Accept, question or decline an offer | A known promise/affiliation and later access; no required villain encounter |
| Protection/reputation | Choose trusted assistance or an institutional safety route | A bounded obligation or reported incident; being broke cannot force exploitation |
| Appeal/review | Submit an existing documented ground or request advocacy | A scheduled review and reasoned result, not repeated paid rerolls |
| Education/rehabilitation | Choose a qualification or support goal | Once-earned milestone, civilian reference and reentry approach |
| Work and release planning | Negotiate a lawful role and contact a chosen person | Pinned wage/reference terms and a housing/support referral |
| Supervision/reentry | Address a conflict between a known condition and an employer demand | A reviewed plan, modification request or documented breach under future rules |

Crew membership cannot be the only safe route. Ethical staff, peers and advocates
must be available alongside corruption and violence. Some contacts refuse help
for understandable reasons; that cannot remove every safety path. Release does
not erase criminal records or force return to the same gang. A prospective employer
can reject a reference while other legitimate work remains plausible.

## B. Arkham as a distinct care institution

Arkham can be dangerous and narratively rich without making every patient violent
or every practitioner corrupt. Entry routes are the separate evaluation,
commitment, transfer, voluntary or visitor paths above. A criminal career label,
high heat, dependency, unusual belief or failed resistance roll is not an
automatic admission criterion.

Proposed play concerns selecting support, setting confidentiality boundaries,
maintaining outside ties, questioning a recommendation, pursuing independent
review, protecting someone or refusing an unethical request. Care progress and
custody/release authority are separate. A good treatment decision cannot be
nullified merely to prolong a villain storyline. If treatment does not meet a
need, offer review and alternatives rather than presenting it as proof that all
care fails.

Potential participants include ethical psychiatrists and other care staff,
corrupt individuals, ordinary patients, specific dangerous patients, guards,
administrators, investigators, advocates and institutional informants. Any danger
is attributed to conduct and context, never to diagnosis alone. Staff/patients have
privacy and agency; befriending someone does not grant access to their records.

Hugo Strange may appear only if the selected continuity, role, location and
opportunity make it plausible. Harley Quinn can be a former practitioner, patient,
visitor or other participant only when that continuity supports the role; she
must not be simultaneously assigned incompatible jobs or always present. Her
history changes across portrayals; [DC's profile](https://www.dc.com/characters/harley-quinn)
is an anchor, not a staffing schedule. Strange's role in the Arkham games is one
[continuity-specific example](https://www.dc.com/blog/2022/03/18/the-worst-mayors-of-gotham-city-ever),
not a mandate for this game's institution. No named encounter is guaranteed.

An unavailable villain cannot block evaluation, ethical treatment or discharge.
Clinical/administrative progress must have ordinary staff and valid alternate
routes. A story visitor or informant opportunity cannot silently convert the
player into a committed patient.

The [Joker recruitment proposal](GOON_JOKER_RECRUITMENT.md) requires a direct
encounter during an Arkham storyline for formal initiation, not for treatment or
release. An eligible visitor/work/story route can satisfy lawful access without
admission as a patient. Joker's absence or refusal does not block care, discharge,
reentry or campaign completion. No repeated admission/release grants invitations.

## C. Voluntary counseling and credible improvement

Seeking help never requires arrest. Possible motivations include fictional fear-
toxin or botanical exposure, dependency, trauma, stress, compulsive behavior,
persistent influence, relationship strain or a wish to leave crime. These are
story motivations, not diagnoses or a prescription for a particular intervention.

An ethical care path explains proposed goals, consent and confidentiality before
commitment. Let players choose a goal, ask for an independent opinion, maintain
a trusted contact and change practitioners. Improvement can reduce a fictional
condition's impact, add coping milestones, support a relationship, reduce a
specific manipulation vulnerability, or open education/work opportunities.
Voluntary treatment is not a reputation penalty or evidence of guilt.

Progress may be uneven but must be attainable. Setbacks have recorded causes and
revised options rather than a compulsory relapse roll. Basic support needs a
zero-cash route, finite useful choices and alternatives if one provider is absent.
No premium rescue, forced exposure, endless appointment grinding or real-time
timer. Partial improvement and ongoing care are valid outcomes; the player does
not need a perfect cure to work, build relationships or finish a campaign.

## D. Dangerous practitioners and routes to safety

Individual corrupt/villainous providers can misuse authority, disclose confidential
facts, recruit vulnerable people, misrepresent outcomes or attempt fictional
conditioning/experiments. Such episodes require authored content review and
bounded choices. Do not make a real treatment technique into a harmful recipe
or claim that ordinary mental-health professionals behave this way.

Show knowable warning signs and the source/uncertainty of a referral. Options
include limiting consent, asking an advocate, declining, requesting a different
provider, documenting a complaint, seeking independent review and contacting a
trusted person. Provide an ethical alternate provider and a practical safety
route even after exploitation. Never require participation in an experiment as
the sole path to release, recovery or a campaign ending.

Record confidentiality permissions and actual disclosures separately. Proposed
exceptions require an explicit fictional rule and reason; they are not a blanket
transfer of private notes to every employer, police officer or narrator. Illegal
leaks have an actor/source and consequences. The UI distinguishes a known fact
from a practitioner's unverified claim. Summarizing a disturbing scene preserves
the player's chosen outcome and does not force viewing its depiction.

## E. State, continuity, and integration proposals

Future definitions describe institution mandate, available services, participant
roles, lawful entry/transfer/review rules and protection policies. Runtime episodes
record actor, admission basis/authority, legal/care status separately, consent,
review/release dates, milestones, decisions and outcome IDs. Pin continuity and
rule versions; evaluate named participants through conditional opportunities.
No inference from a crime label or faction name can override admission criteria.

All consequential choices use the game service with an explicit future action/time
policy. This document sets no new command or daily cost. A later contract must
explain how the existing three-action allowance is used in institutions, which
choices are free, and how advice/appeal/discharge remain reachable when actions
are exhausted. Queries and refusals cannot initialize state or change clocks.
Use whole-command transactions for admission, transfer and release so no player
can simultaneously occupy incompatible custody states or disappear between them.

The city's existing court system resolves cases automatically and has no sentence
episodes. A prison milestone would therefore need an explicitly approved additive
legal extension, including the distinction between conviction and custody term.
Do not rewrite historical fines/convictions into invented prison terms. The
combat case-source adapter alone does not implement this institutional model.

Choose a place in the daily pipeline for future reviews, care and episode progress;
persist last-processed markers and exactly-once outcomes. Advancing several days
explicitly must run the city once for each day, preserving event order. Save/resume
does not shorten a term, regenerate grants or reset confidentiality/consent.
All time is simulation time; no external service or wall clock is authoritative.

## F. Endings, reentry, and the ten-field review

Possible later endings include recovery and freedom, supported living/ongoing care,
lawful employment, retirement, renewed criminal involvement, fugitive life after
an explicitly chosen breach, institutional exploitation with accountability,
or personal reinvention. Incarceration/treatment can be a chapter rather than the
ending. Do not present illness or ongoing support as a failed life. Institutional
exploitation must not imply recovery was impossible or remove every way to seek help.

| Criterion | Institutional/recovery contract |
| --- | --- |
| Meaningful decisions | Choose contacts, work/education, appeal, support, care goals, consent, provider or reentry commitments. |
| Observable consequences | Show legal basis, review horizon, care terms, actual progress, references and reasons for decisions. |
| Persistent state | Separate custody/care/supervision status, permissions, episode decisions, review dates, milestones and exit record. |
| Alternative outcomes | Review upheld/revised, ethical improvement, changed provider, release, ongoing care, reentry, crime or retirement. |
| Replayability | Different prior relationships, evidence, qualifications, available staff and outside obligations. |
| Grind risk | Repeated chores, appointments or appeal fees; favor finite decisions and explicit advancement past uneventful time. |
| Determinism | Stable episode/review IDs, pinned continuity and policies, canonical actor ordering and once-per-day processing. |
| Save compatibility | Later independent versioned state; preserve historical legal records, no retroactive admission/sentence; migrate each new status explicitly. |
| Offline operation | Local schedules, content and rules; every care/release route works without server time, accounts or AI. |
| Exploits and agency | Reject invalid transfers atomically; no duplicate grants, automatic commitment from conviction, indefinite detention loop or villain-exclusive cure. |

Each path above inherits this contract. Its later implementation must additionally
test a finite exit/review from every allowed entry, zero-cash support, unavailable
named characters, consent/confidentiality boundaries, failed transfers, simultaneous
case constraints, deterministic resume and long city advancement. None of those
future institutional tests has been implemented or executed in M013.1. The
[worked release scenario](GOON_CRIMINAL_CAREER_WEB.md#scenario-3--a-place-after-release)
is a paper exercise only.
