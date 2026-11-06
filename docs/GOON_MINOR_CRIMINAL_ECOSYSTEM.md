# Gotham: The Goon — Minor Criminal Ecosystem

**Status: M013.1 design proposal only.** No crews, additional actors, promotion
rules or persistent fields are implemented here. Current M013 competition still
uses the existing three factions and districts. Read the
[rogue registry](GOON_ROGUES_GALLERY_REGISTRY.md),
[career web](GOON_CRIMINAL_CAREER_WEB.md), and
[opportunity contract](GOON_CONDITIONAL_OPPORTUNITIES.md) together.

**Mission 029 reconciliation:** the [existing employer matrix](GOON_FACTION_EMPLOYER_MATRIX.md#mission-029-organized-crime-candidate-registry)
now owns the 26 organized-crime candidate/category records and leadership/source
matrix. Its [bounded integration contract](GOON_FACTION_EMPLOYER_MATRIX.md#mission-029-proposed-organization-integration-contract)
extends these three scales; it does not turn every name into a district owner.
Four umbrella records are research classifications, never simulated actors.
Comics, TV and alternate-future groups are not one simultaneous starting cast.
The historical M013 wording above describes the origin of this proposal; M020
is now merged, with ordinary life and limited contacts/incident/intake adapters.
No new criminal organization, NPC graph or faction mechanic is implemented here.

## Three scales of participation

| Scale | Proposed responsibilities/state | Decisions and constraints | What is not required |
| --- | --- | --- | --- |
| Major district-owning faction | Explicit economic-profile binding, funded operations, organizational power, holdings and strategic objectives | Income/upkeep/recovery and territory use existing shared ownership rules when the actor is actually registered as a full faction | A famous name alone never creates this state or grants a district |
| Minor crew / emerging organization | Stable crew ID, actual member IDs, contacts, bounded contract commitments, cohesion and current opportunity | Hire, share a job, refuse, split, cooperate or compete over a specific promise/resource; settle funded contracts once | District ownership, recurring treasury income, faction power, a daily strategic planner and paid warfare are optional, not automatic |
| Individual criminal / independent specialist | Character ID, capabilities, relationships, knowledge, availability and personal commitments | Take or refuse work, recommend someone, compete, seek support, leave crime or change allegiance | A crew, faction membership, strategic action or simulation-wide wallet is not necessary for every actor |

A character can be a boss in a small crew, a contractor for a major faction and
a personal ally of the player at the same time. These are directed, dated
relationships, not mutually exclusive character classes. Operating scale is not
combat difficulty, fame, moral worth or a permanent hierarchy. An individual
supernatural threat can be more dangerous than a district owner without needing
an economic simulation. The [registry](GOON_ROGUES_GALLERY_REGISTRY.md) proposes
roles, not automatic faction assignments.

## Work and resources without a full treasury for everyone

A minor crew can use a bounded contract envelope: a known payer reserves an
agreed amount, an assignment owns that reservation, and one outcome releases,
pays or refunds it under pinned terms. This is a future design, not how current
job rewards are financed. A noncash promise is recorded as such; it cannot be
silently converted into unlimited money. Do not maintain a simulated bank account
for every background extra merely to display a conversation.

Major actors cannot fund the same share twice or lend ownership they do not have.
An unfunded crew can seek sponsorship, combine work with civilian wages, refuse
a job, dissolve or become inactive. No passive income appears just because a new
crew enters the cast. Lost funding changes future offers rather than deleting
its members or making them all attack the player.

Only actual district owners participate in income/control/warfare. A crew working
in a district does not own it. Local access, contacts, turf claims and rumors are
separate facts. Any later transfer to full faction status must reuse the single
shared capture/economic rules and be justified by resources and events.

## Original ordinary criminals

The following are original draft project characters, not DC figures, adaptations
of video narrators, implemented NPCs, or claims of legal/name clearance. All need
authored dialogue later; none borrows another creator's voice or catchphrases.

| Proposed ID / person | Work and distinct behavior | A choice, consequence and possible transition |
| --- | --- | --- |
| `goon.character.nia_bell` — Nia Bell | Driver who quotes a clear shift-end time and supports a younger sibling; dependable, unwilling to promise two pickups at once | Honor her agreed hours or negotiate a willing substitute; a kept promise earns a reference. She can coordinate a crew or return to civilian transport |
| `goon.character.oren_pike` — Oren Pike | Fence/appraiser who records ownership claims and refuses uncertain provenance more often than clients expect | Accept a delay, disclose a disputed claim or find another broker; trust/access change. He can sponsor lawful restoration work or retire |
| `goon.character.ada_mercer` — Ada Mercer | Cleaner/restoration worker with a practical wage ledger and firm boundaries against concealing harm | Pay for honest repairs, pressure her to cross a boundary, or support her refusal; employment and personal trust diverge. No evidence-removal methods are supplied |
| `goon.character.ivo_chen` — Ivo Chen | Informant and casual worker who labels firsthand knowledge separately from hearsay; cautious about naming a friend | Verify, withhold or transmit a claim; a mistaken report persists with provenance. He can withdraw cooperation or seek legitimate work |
| `goon.character.sera_danton` — Sera Danton, provisional alias Lantern Finch | Aspiring costumed criminal who budgets poorly for presentation and values being credited for useful work | Credit her contribution, exploit her enthusiasm or refuse a dangerous stunt; she can abandon the alias, become a reliable technician or form a small crew |
| `goon.character.luis_arden` — Luis Arden | Independent fixer who will not guarantee an outcome outside his authority; keeps exact reciprocal promises | Negotiate a bounded introduction or demand impossible immunity; a reference or refusal follows. He can mediate crew splits or move into lawful coordination |

These people have mixed motives and can change without becoming punchlines about
poverty, ethnicity, disability or illness. Existing draft coworkers Tess and Cal
remain separate people. Similar work does not imply kinship or a shared identity.

Proposed original crews: **Late Shift Dispatch** (`goon.crew.late_shift_dispatch`)
is Nia and willing coworkers sharing transport contracts; **Second Bell Repairs**
(`goon.crew.second_bell_repairs`) is Ada's occasional repair collective. Neither
starts with a district, faction power or daily treasury tick.
Membership requires each person's decision, not duplication of a name in a roster.
Any later naming/content clearance is separate from adopting generic mechanics.

## Rise, fall, defection, arrest and retirement

| Transition | Trigger and player decision | Persistent result / alternate route |
| --- | --- | --- |
| Individual to crew associate | A useful contract, mutual recommendation and accepted terms | Shared obligation and a specific reference; refusal leaves independent work |
| Crew growth | Repeated *different* fulfilled commitments and available demand | More participants or delegated responsibility; no rank/XP threshold creates free income |
| Emerging organization to major faction | An explicit later milestone authorizes registration, validates funding/profile, and resolves any actual territorial claim | One identity binding and auditable economic activation; no parallel copy of the crew taking two turns |
| Setback / dissolution | Funding loss, failed promises or departures | Remaining debts, trust and availability persist; members can recover, seek work or leave |
| Defection / divided loyalty | A character accepts another offer or refuses a harmful demand | Specific secrets/obligations and informed reactions; friendships are not all reset |
| Arrest / custody | A documented allegation and valid future legal outcome | Availability changes; crew chooses replacement, support or disengagement; no automatic psychiatric admission |
| Release / reintegration | A valid release/review and chosen support | Old memories remain; civilian work, restored contact or another crew can be available |
| Retirement / reform | A disclosed voluntary exit and settlement/review of obligations | Recorded departure and chosen contacts; no forced return merely to keep a villain roster full |
| Alliance / rivalry | Known acts, negotiations and conflicting interests | Actor-specific trust, promises or disputes; information must reach the reacting actor |

Fame, a single win or a joke costume never guarantees promotion to district owner.
Some rogues remain contractors throughout a career. A rising crew can become
important through people and access even if it never gains land. A retired or
arrested character is not replaced with an identical fresh reward dispenser.
No automatic revival of a dead actor or replacement of one mantle-holder by
another without continuity and identity validation.

## Activity, information and deterministic population

Author a finite roster per continuity/content pack and choose an active subset
from explicit initial conditions or recorded world triggers. Treat dormant,
working, unavailable, detained, retired and deceased as distinct states. A roster
entry is not proof that the person is alive or physically in Gotham this run.
No real-time spawning or obligation to show every research-registry entry.

Minor activity is demand/incident-driven, not dozens of copies of faction warfare
every day. Batch noninteractive background facts where useful, preserving stable
actor order and causal events. Reactivate only on a recorded relevant change.
Do not add a hidden strategic income tick to make a contact seem busy.

Use stable actor/crew/contract IDs and local versioned rules. Resolve selection
through an isolated RNG keyed by seed and causal trigger; persist results,
settlement and last-processed markers. Reports, dialogue previews and reloads
cannot reroll membership or availability. The player's street knowledge is not
the complete registry: a rumor of an arrest can be wrong while custody remains
an independently validated fact.

Named relationships with Penguin, Joker, Black Mask or other major employers are
optional dated edges, never implied canonical alliances. A Joker-cell coworker
does not confer membership; the [recruitment contract](GOON_JOKER_RECRUITMENT.md)
sets that distinct campaign gate. No core mechanic branches on those names.

## Ten-field review and paper scenario

| Criterion | Ecosystem contract |
| --- | --- |
| Meaningful decisions | Choose a coworker, sponsor, share, refusal, alliance or exit rather than collect villains |
| Observable consequences | Show actual terms, known availability, who learned what, and why a relationship/opportunity changed |
| Persistent state | Directed ties, commitments, unique contracts, actor availability and explicit scale changes |
| Alternative outcomes | Independent career, stable small crew, growth, defection, recovery, arrest, retirement or dissolution |
| Replayability | Different active subsets, demand, histories, loyalties and civilians' obligations |
| Grind risk | Contact/favor spam, clone crews, endless referrals; distinct proofs and once-settled contracts must matter |
| Determinism | Canonical IDs/order, recorded trigger selection, exactly-once resources/transitions, no wall-clock decisions |
| Save compatibility | Future additive versioned population/crew state; no invented old allies, treasuries or ownership; existing faction IDs stay intact |
| Offline operation | Local authored roster, policies and career-contained state; no live-service population or AI service |
| Exploits / agency | No duplicate actor across scales, unfunded money, automatic capture, compulsory gang or missing-contact softlock |

**Paper-only:** Nia's dispatch crew needs a second driver while a minor rogue
offers a risky subcontract. The player can honor the existing crew shift, seek
a consenting substitute, or refuse the rogue's undisclosed terms. One version
preserves a civilian reference; another earns a bounded share but damages Nia's
trust; a negotiated substitute creates a new personal obligation. Later, Nia may
hire the player, retire or support a crew split. No district changes hands merely
because either worker gains influence.

No new player decision or persistent consequence is implemented by this addendum.
Before a future implementation, test repeat triggers, scarce funding, actor/crew
identity across promotion, unavailable contacts, retirement/defection/resume,
no-territory crews, read isolation and insertion-order determinism. Finite role
tables and numerical trust alone will still be shallow without authored variation.
