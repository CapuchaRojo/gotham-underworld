# Content architecture recommendations

Mission 007 update: [M014 implements world/navigation](GOON_WORLD_RUNTIME.md).
Combat references below retain the historical M013.1 proposal and are deferred;
the [roadmap](GOON_MILESTONE_ROADMAP.md) assigns no combat milestone number.
Registry/navigation implement the location subset; the life, incident and intake
subsets are identified below. Broader catalogs and legal case adapters remain proposals.

**Status: broader M013.1 proposal; implemented M014–M020 subsets below.**
The broad catalogs below remain proposals outside the explicitly implemented
location/life/incident subsets. M014 retains the M013 legal/economic systems. This document supports the
[narrative bible](GOON_NARRATIVE_DESIGN_BIBLE.md) and the separately reviewable
[M014 combat contract](M014_COMBAT_DESIGN_CONTRACT.md).
The expanded proposals cover [careers](GOON_CRIMINAL_CAREER_WEB.md),
[opportunities](GOON_CONDITIONAL_OPPORTUNITIES.md),
[influence](GOON_VILLAIN_INFLUENCE_SYSTEM.md) and
[institutions/recovery](GOON_INSTITUTIONS_AND_RECOVERY.md). They do not enlarge M014.
The [rogue registry](GOON_ROGUES_GALLERY_REGISTRY.md),
[minor ecosystem](GOON_MINOR_CRIMINAL_ECOSYSTEM.md) and
[Joker recruitment proposal](GOON_JOKER_RECRUITMENT.md) add content-design
requirements only; no roster, economy or save migration is performed.
The [atlas](GOON_GOTHAM_ATLAS.md), [location registry](GOON_LOCATION_REGISTRY.md),
[travel](GOON_TRAVEL_NETWORK.md), [migration](GOON_MAP_SIMULATION_INTEGRATION.md),
[career geography](GOON_CAREER_GEOGRAPHY.md) and
[visual specification](GOON_MAP_VISUAL_SPEC.md) are likewise research/design only.
Location containment is not a travel edge; geography is not a territory account.
Future layers separate actual facts, public knowledge and sourced claims. No new
schema or loader is introduced by the Markdown registry.

## Current boundary and constraints

### Task Force X contract — research and design only

The [specialized contract](GOON_TASK_FORCE_X_RECRUITMENT_DESIGN.md) owns new
government/Squad context and the five-condition proposal. The [master index](GOON_MASTER_ROSTER.md)
links it while original rogue identities and criminal organization records stay
with their existing authorities. No program marker, loader, save field, event ID,
backend, new case type, law adapter or Waller actor is implemented.

Current legal outcomes can supply limited source material, not a full criminal
severity/sentence/supervision system. Any later assessment needs narrow approved
record/referral/authority adapters; use source-backed receipt/order and recipient
views rather than copying the whole world into an omniscient dossier. Missing
domains stay unknown, historical dates stay null, and canonical political power
never authorizes reading private contact memories. Proposed alternatives do not
silently complete the special route. Preserve atomic service mutation, budgets,
stable history, offline replay, explicit adoption and exactly-once effects.

### Master index and optional DARK design authority

The [master index](GOON_MASTER_ROSTER.md) is documentation navigation, not a
runtime catalogue or player-known projection. Pointer-valued affiliation and
relationship fields resolve to existing source owners, avoiding duplicate
biographies. Actors, bound pairs, personas, mantles, organizations, categories,
staff labels and vacant roles are distinct; index keys are never save IDs.
The [DARK canon registry](GOON_DARK_CANON_REGISTRY.md) owns new character research;
the [DARK contract](GOON_DARK_PROGRESSION_CONTRACT.md) owns proposed late opt-in,
recipient knowledge, consequences, refusal/recovery and approval questions.
No JSON definitions, loader, optional marker, global clock, magic/morality meter,
event IDs, budget or engine changes accompany these documents. Any later slice
needs its own bounded adoption/source-validation contract. Do not expose this
authoring index through the UI or treat canonical psychic powers as access to
all saved facts. Protected metadata remains outside ordinary/DARK discovery.

### Mission 029 organization-definition proposal

The [employer matrix](GOON_FACTION_EMPLOYER_MATRIX.md#mission-029-organized-crime-candidate-registry)
is the single organization-candidate/source authority; the [minor registry](GOON_ROGUES_GALLERY_REGISTRY.md)
owns detailed minor-character identities and the [encounter contract](GOON_ROGUE_ENCOUNTERS_DESIGN.md)
owns proposed access/difficulty for its overlapping roster. Different research
sets are not duplicate runtime cast lists. Preserve existing person IDs when
an individual has a crew; aliases, personas and umbrella categories grant no
extra treasury, turn or resource authority.

Future definitions would separate selected continuity/era, people, organizations,
leadership edges, workplace terms, geography/influence, narrative text and assets.
Selection, actual availability and observer knowledge are separate. The
[organization integration contract](GOON_FACTION_EMPLOYER_MATRIX.md#mission-029-proposed-organization-integration-contract)
specifies consent, independent activity, succession, funds, sourced information
and recovery as proposals, not current JSON fields or a loader. Its first safe
implementation candidate is one original minor-crew commitment, subject to a
new approval and adoption/validation contract. No name-based engine branch,
parallel history authority, new save schema, altered content pin or global rumor
store is introduced. The protected late-progression restriction must precede
any future player-facing catalogue/discovery projection; author-only source
records must never be exposed wholesale as player knowledge.

### Implemented M020 ordinary-life adapters

`ordinary_life` extends the existing life authority with one optional version 1
work/support arrangement. It reuses `choice_engine` presentation and eligibility,
`game_service` candidate transactions, the existing post-life day phase, the
actual-cash ledger and Tess memories. It does not replace old rosters, room
receipts or incident dispatch, and does not send institutional reports.

`ordinary_content` pins local terms/text in `content/ordinary_life_v1.json`;
`ordinary_state` reconstructs employment from actual future repair choices and
replays new transitions against completed command/movement sources, action costs,
housing receipts and real money/memory effects. Stable IDs identify weekly funded
allocations, one-shot support, day processing and command effects. There is no
second cash account, relationship authority, global clock or generic scheduler.

Historical saves retain their behavior without explicit `enable_ordinary`.
Adopted saves require the new executable; compatibility is old-to-new. The
[daily-life contract](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md#m020-extension--ordinary-work-housing-and-support)
specifies implemented terms and [M020 evidence](M020_ORDINARY_GOTHAM_VALIDATION.md)
records executed tests and known limitations. Future faction/character content
does not control these mechanics.

### Implemented M019 institutional response

The [institution contract](GOON_INSTITUTIONS_AND_RECOVERY.md) is canonical for
the two implemented desks; custody/care/recovery proposals remain unimplemented.
`institution_sources.Sources` reconstructs actual source availability from existing
incident enrollment/transitions. It does not persist another world-truth authority
or inspect a private cause to invent a report. `institutional_response` owns the
institutional queue, local beliefs/credibility and receipt-time player views;
`institution_state` replays these against prior domain sources and command frames.

The optional marker/state is independent: `institution_version: 1` /
`institutions`. Adoption starts future automatic transmissions only; prior
source-backed player observations may still be explicitly submitted. Old incident
reducers, content pins and histories are unchanged. One post-incident daily hook
and a post-handler service synchronization reuse existing ordering and rollback.
No extra economy tick, RNG draw, payment, legal source or contact meter is added.

The institution pack separates stable IDs, names, staff, counter locations,
mandates and delays from mechanics. The explicit adapters support only the two
current incidents and two mandates. They are not an inference/rumor framework.
Player-facing institutional views exclude unreceived private processing and
preserve previous response snapshots. Full saves/debug snapshots retain audit
truth. See [executed validation](M019_INSTITUTIONAL_RESPONSE_VALIDATION.md).
The one certified-copy source is created only after an actual local response
hands it over. Replay derives the response first, then exposes that bounded
documentary source for a later command; a saved boolean cannot authenticate it.
This provides late record repair without a general knowledge/rumor network.

### Implemented M018 incident dispatch

The historical proposals in this file do not supersede the implemented service,
navigation, life or incident contracts. The bounded two-incident extension uses:

```text
game_service.execute_command (candidate copy, budget, rollback, validation)
  -> incident_dispatch (explicit definition/instance ownership)
     -> world_incidents | wrong_notice (domain reducer and assessment)
        -> incident_lifecycle (day progression, stages, settlement, receipts)
  -> existing daily_life memories + player cash + actual-cash ledger
  -> incident_state replay + independent domain-source validation
  -> detached player reports/events
```

`incident_dispatch.bindings()` explicitly binds two stable definition IDs to
their module, version marker, state slot and enrollment event. It performs no
dynamic imports from saves, scripting, plugin discovery or arbitrary content
execution. Both implement `initial`, `reduce`, `_assess`, `load`, `fingerprint`,
`report`, and `FACT_DELTAS`. This is a small internal Python adapter contract.
JSON holds original contacts, text, option IDs/costs and fixed pay; domain rules
remain explicit Python. There is no universal quest language.

| Definition | Optional marker / state | Enrollment |
| --- | --- | --- |
| `goon.incident.night_shift.v1` | `incident_version: 1` / `incidents` | Existing `enable_incidents`, or explicit generic `enable_incident` |
| `goon.incident.wrong_notice.v1` | `notice_version: 1` / `wrong_notice` | `enable_incident(definition_id)` only |

The old singleton shape is retained as a compatibility slot, not wrapped or
renumbered. Each adopted adapter runs once after daily life, in sorted definition
order. It stops ticking after all stages close. Each has its own enrollment,
transition IDs, source records and replay, so one cannot settle another's command
or borrow its occurrence tick. Identity ownership is validated before replay.
For the bounded slice there is one episode per definition per career.

Both share `discover_incident(incident_id, channel)` and
`incident_choose(incident_id, stage, option_id)`. Costs are computed by current
choice assessment and rechecked on the candidate. Replay reconstructs adapter
state from its own chronological events and compares exact results/effect IDs.
Delegated memories and nonzero payments are cross-checked against the existing
life authority. Stable IDs plus terminal stages prevent duplicate settlement;
no second cash balance, reputation metric or historical-location authority exists.

Night Shift preserves its content pin, IDs, receipt/event shapes and legacy
report shape when Wrong Notice is not adopted. A two-incident overview is used
only when the new optional marker is present; passing an instance ID returns
one adapter's report. Existing saves load without adoption or conversion.
Wrong Notice saves require an executable that supports their explicit version.

Source-backed discovery reuses M017-B's prior travel/command provenance; each
adapter determines what its source can actually say. Wrong Notice additionally
replays observations and targeted transmissions, rather than accepting saved
knowledge booleans. The player journal shows observed claims only. Private
automatic reactions are filtered from service events and contact summaries until
the final circular is received. Raw save data and `snapshot` remain detached
developer/audit world views; they are not a player knowledge API. A future UI must
use player projections rather than relabeling raw state as known information.

See the canonical [After Dark contract](GOON_GOTHAM_AFTER_DARK_LAW_BATFAMILY_DESIGN.md)
and [executed validation](M018_WRONG_NOTICE_VALIDATION.md). No DC character data,
global NPC inference, legal-case source, real-time scheduler or asset is added.

| Responsibility | Current implementation | Constraint for extensions |
| --- | --- | --- |
| Player transactions | [`game_service.py`](../game_service.py): create/load/save, `execute_command`, `advance_day`, detached `snapshot` | Reuse the boundary; rejected commands leave the entire world unchanged |
| Command contract | Registry of command IDs, daily costs, required string arguments, handler; detached result/event envelope and persisted command sequence | Extend a small explicit registry; no plugin execution framework or direct UI writes |
| Persistence | [`career_state.py`](../career_state.py), [`career_persistence.py`](../career_persistence.py) | Keep additive historical migrations, strict validation, backups and safe publication |
| Daily orchestration | [`gameplay.py`](../gameplay.py), [`legal_engine.py`](../legal_engine.py) | Preserve phase order and daily processing markers; GUI redraws never advance time |
| Events and base world | [`simulation.py`](../simulation.py) | Structured fields describe committed effects; messages are presentation, not an API |
| Jobs and investigations | [`consequence_engine.py`](../consequence_engine.py), legal modules | Preserve legacy job RNG; do not invent job attempts to represent new kinds of crime |
| Relations and NPC activity | [`relationship_engine.py`](../relationship_engine.py), [`npc_actions.py`](../npc_actions.py) | Current metrics concern NPC-to-player relationships; named threshold policies are not a general personality system |
| Economic identity | [`faction_profiles.py`](../faction_profiles.py), [`faction_competition.py`](../faction_competition.py) | Saved profile definitions/bindings already separate economic parameters from faction names |
| Territory | [`territory.py`](../territory.py), mission and warfare modules | Continue using the shared capture operation; story effects cannot bypass ownership invariants |
| Read models | [`city_intelligence.py`](../city_intelligence.py), strategy assessments | Reports remain detached and read-only; current reports expose actual world facts, not uncertain beliefs |
| Geographic definitions | [`location_registry.py`](../location_registry.py), local versioned atlas | Validate/pin IDs, references and profiles without adding territory accounts |
| Navigation | [`navigation.py`](../navigation.py), service travel/adoption commands and detached public views | Preserve three actions, separate TU, explicit old-career opt-in, safe committed routes and next-day activation |

The world is a mutable, JSON-shaped dictionary, not an entity framework. Several
current dictionary keys are display names. Base content, the legacy feud roster,
and some NPC policies are still embedded in Python. The engine is not already
fully content-independent. M013.1 documents the path without claiming to have
performed that migration. Existing repository/module names and save identifiers
remain intact.

## Separate definitions, state, knowledge, and presentation

Use four distinct responsibilities in future work:

1. **Definitions:** versioned, local data describing allowed content and rules.
   Treat definitions as immutable during a command.
2. **Runtime instances:** mutable career facts such as an employment agreement,
   injury, mission status, or relationship. Persist the definition ID/version and
   the instance's actual decisions and outcomes.
3. **Knowledge:** what each actor has observed or believes, including provenance,
   confidence and contradictions. A rumor does not rewrite the underlying fact.
4. **Presentation:** localized text, portraits, sound references, layout, and
   animation. Changing a label must not change identity, RNG, or simulation rules.

Core rules should depend on capabilities, parameters, and stable IDs. Licensed
names belong in an optional content definition's display/narrative fields. Avoid
rules such as `if employer_name == 'Penguin'`. An economic profile, recruitment
predicate, and behavior policy can describe an employer without naming one.

## Proposed definition catalog

These are minimum design responsibilities, not approved JSON schemas or a demand
for a new module per row. Introduce only the definitions a milestone uses.

| Definition | Proposed minimum fields and references | Mutable state lives elsewhere |
| --- | --- | --- |
| Faction | `id`, definition version, display label, economic-profile ID, culture tags, policy IDs | Treasury, power, holdings, relationships, daily markers |
| Character | `id`, display label, affiliation IDs, background tags, bounded trait parameters, behavior-policy ID | Health, memories, loyalty, observations, current assignments |
| Employer | `id`, faction/character reference, contract templates, compensation policy, recruitment reference | Accepted contract, wages owed/paid, obligations, rank |
| Recruitment | `id`, eligibility predicates, refusal/exit rules, initiation mission references | Attempts, decisions, promises, earned access |
| Mission | `id`, prerequisites, participants, bounded stages, allowed command IDs, outcome/effect IDs | Instance ID, accepted terms, completed stages, settled outcome |
| Dialogue | `id`, speaker reference, text/variant keys, knowledge predicates, choice-to-command mappings | Seen nodes and committed choices; text alone applies no effects |
| Rumor | `id`, claim type, subject references, source and spread policies | Each actor's belief, provenance, acquired day, confidence; truth is separate |
| City event | `id`, deterministic eligibility, finite phases, scope, mission/effect references | Trigger cause, phase, affected instances, settlement marker |
| Equipment | `id`, display label, slot, permitted actions, bounded modifiers, asset references | Ownership, selected loadout, condition if later approved |
| Progression | `id`, milestone predicates, unlock references, branching/exclusion rules | Earned qualifications, access, reputation, chosen commitments |
| Career specialization | `id`, skill/qualification references, work tags, transition and lawful-exit references | Demonstrated qualifications, contract history and selected goals; no immutable class |
| Skill | `id`, bounded scale, permitted check IDs, learning/proof rules | Earned capability and one-time proofs; no viewing/appointment XP |
| NPC personality | `id`, bounded preferences, priorities, boundaries, behavior-policy references | Individual decisions, changing goals, memories and commitments |
| Relationship | `id`, directed actor roles, metric bounds, knowledge/effect policies | Each pair's trust/boundaries, known facts, promises and causal history |
| Criminal reputation | `id`, audience/domain, eligible evidence and propagation rules | Audience-specific known acts and assessments; separate from criminal records |
| Personal code | `id`, explicit commitments, warning rules, conflicting-choice references | Voluntarily chosen commitments, honored/broken promises and revisions; no diagnostic/alignment score |
| Opportunity | `id`, eligibility predicates, demand/capacity, selection policy, terms, expiry and outcome references | Trigger/evaluation/instance IDs, committed draw, known offer, accepted terms and terminal result |
| Location | `id`, display label, access rules, available services and institution references | Presence/access and finite incident effects, when a travel/location system is approved |
| Injury | `id`, bounded effects, recovery references, conflict/stacking rules | Source, current severity, settlement and recovery markers; never inferred from faction power |
| Villain influence condition | `id`, fictional exposure/trigger/effect policies, severity bounds, consent safeguards, recovery references | Source event, bounded condition, chosen responses and residual vulnerability; allegiance separate |
| Institution | `id`, mandate, continuity version, entry/transfer/review/exit rules, role/service references | Episode, separate custody/care status, authority, review dates, participant availability |
| Treatment/recovery | `id`, fictional eligibility, consent/confidentiality terms, milestones, alternate-provider and safety references | Chosen plan, permissions, support, progress, disclosures, reviewed changes and exit |
| Character ending | `id`, predicates over commitments/situation, disclosed irreversible choices, continuation policy | Committed ending, reasons and relevant world/relationship facts |
| Minor crew | `id`, member/role references, membership policy, permitted contract/opportunity types | Actual members, promises, shared contract reservations, cohesion and availability; no mandatory faction treasury/power |
| Persona / mantle binding | `id`, underlying actor/variant reference, display alias, source/continuity constraints | Which actor uses an alias, what others know and when a binding changes; no duplicate person/payment |

Each definition also needs a schema version and provenance/content-pack metadata.
Asset references belong to a separate manifest containing source, rights status,
and optional local path. No network fetch should be necessary to load a career.
The M014 minimum can use neutral fixture definitions with no external media.

Illustrative definition, **not a current save format**:

```json
{
  "schema_version": 1,
  "id": "employer.example_dispatch",
  "definition_version": 1,
  "display_name": "Example Dispatch",
  "faction_id": "faction.harbor",
  "economic_profile_id": "trade_network",
  "recruitment_id": "recruitment.delivery_reference",
  "contract_ids": ["contract.local_delivery"],
  "policy_id": "policy.commercial",
  "content_pack_id": "prototype_examples"
}
```

`faction.harbor` illustrates a future identifier; the existing save key remains
`Harbor Syndicate`. No alias, employer, or delivery contract is added now.
The example's references would all have to resolve before accepting a real pack.

### Proposed rogues and operating-scale bindings

The registry's proposed IDs are content references, not renames of historical
keys. A selected content pack must record source/edition, continuity, actor or
persona type, supported capabilities and initial availability. Maintain separate
actors for distinct mantle holders; retain an unresolved legal identity as unknown.
For Terrible Trio, a crew references three actor IDs; Tweedledum and Tweedledee
remain two people; a Scarface persona references its selected underlying actor.
Do not give the puppet, handler and crew three copies of one economic reward.

Represent major faction participation as an explicit optional capability/binding.
A minor crew can reserve a bounded contract budget without a full treasury,
strategic planner, district or daily income tick. An individual needs none of
those merely to appear in a scene. Role tags such as boss/contractor/associate/
rival/wildcard are contextual relationship facts, not hardcoded actor subclasses
or automatic power levels. Fame is not an economic profile.

A later approved promotion to full faction status must validate funding/profile,
preserve the actor/crew identity, avoid two operations for one participant and
use shared territory rules for any real capture. Current legacy named policies
and the three-gang feud sampler still need explicit compatibility work before
assuming an expanded strategic roster is supported. No such work happens here.

Availability and active-subset selection use pinned definitions, canonical IDs,
recorded triggers and isolated RNG. Retirement, arrest, death and defection are
state transitions with causal references, not actor deletion or reroll triggers.
A missing optional cameo has an alternate path; do not replace a dead mantle
holder with another version because its display alias matches.

The source/reference metadata supports human content review. Runtime mechanics
must not fetch a wiki, publisher page, asset or external AI service. Bundle only
approved local definitions/provenance; listing a source does not grant a content
license or permission to distribute its images, scripts or character portrayal.

## IDs, compatibility, and validation

Keep IDs independent of display names. Use explicit canonical sorting for all
choices from registries; do not let JSON/dictionary order break ties. Prefer a
small closed vocabulary of capabilities and predicates to arbitrary scripts.
Handlers remain allowlisted Python functions in the engine. Content must never
request `eval`, dynamic imports, shell commands, or filesystem paths outside an
approved local asset root.

The first content migration requires its own reviewed plan. A safe direction is
to add explicit identity bindings alongside historical keys, preserve old keys
and references, and resolve aliases through one adapter. Never silently substitute
another character when a definition is missing or ambiguous. Validate unique IDs,
cross-references, bounded numeric values, valid stage transitions, and cycles
where cycles would prevent completion. Report the offending field/reference.

Pin each career's content/rules versions or persist the resolved parameters it
needs. M013 already copies economic profiles into saves. Editing global default
definitions must not retroactively alter an existing career's payouts, opponents,
or recruitment terms. Decide version upgrade behavior explicitly before shipping
editable packs. Unknown extension fields retained by current migration are not
permission to execute unvalidated new behavior.

Keep the existing outer save contract until an actual incompatibility requires
otherwise. New subsystem versions need explicit defaults, validators, unsupported-
version rejection and additive migration. Loading cannot award wages, rerun daily
phases, refresh actions, or invent historical injuries/crimes. Do not infer health
from faction power or treat an unknown old history as evidence of an injury.

## Commands, events, and proposed combat integration

### Future career, opportunity, and care ownership

Career qualifications derive from committed proofs, not speculative narration.
Personal code is a player commitment with explicit revision, not an irreversible
class. NPC personality parameters inform decisions within knowledge boundaries;
relationships belong to specific directed actors, and reputation belongs to an
audience. No generic reducer may convert one of these into every other metric.

Opportunity evaluation owns recorded eligibility/selection and capacity. Contracts
own accepted terms and exactly-once settlement. Influence owns exposure/condition
state; affiliation and informed consent require separate explicit decisions.
Institutions own valid admission/transfer/review/exit state, with criminal custody,
care and supervision stored separately. Recovery owns reviewed milestones; a
read-only care report cannot tick symptoms or pay a grant. Legal rules own case
facts and outcomes, with compatible incident sources rather than fabricated jobs.

These are proposed ownership boundaries, not a request for a framework or an
immediate set of Python modules. Introduce one approved domain at a time. Do not
infer diagnoses, qualifications, admissions, personal codes or consent from old
save histories. Add a versioned empty extension only when its feature is approved,
preserve unknown historical facts, and test every transition from historical saves.

Pin the selected continuity and each active definition's resolved parameters.
Validate opportunity references, staff availability, confidentiality permissions,
lawful transition reasons and finite review/exit routes before committing. A
missing optional villain must not invalidate an entire otherwise viable career;
required missing definitions need a clear compatibility error or an explicitly
reviewed migration, never an invented substitute.

### Existing callable boundary

Future campaign-specific recruitment can use generic, allowlisted predicates
over valid episode, direct encounter, actor availability, offer and player choice.
The Joker/Arkham binding lives in licensed campaign data, not a character-name
branch in `game_service` or faction strategy. Street association and cell contracts
remain separate from formal membership, and membership is separate from coercion
or treatment consent. A rejected gate check changes no records, clocks or RNG.
Current `join` behavior and historical affiliations are preserved; these predicates
are proposals, not registered commands or implemented save fields.

The existing callable interface is sufficient for a first GUI adapter:

```python
from game_service import create_career, execute_command, snapshot

world = create_career(seed=42)
response = execute_command(world, 'join', faction='Harbor Syndicate')
view = snapshot(world)
```

Current commands require named **string** arguments. New features should register
explicit commands and validate their arguments before committing. Rich structured
payloads would require a deliberate interface change; they are not available by
calling an undocumented command today. The transaction copy is appropriate at
this prototype scale; optimize only after measuring a real workload.

For proposed M014, charge one of the existing three daily actions to enter an
encounter. Tactical continuations use encounter stamina, without a second daily
charge; a player with zero remaining daily actions must still be able to finish,
escape, or surrender. Block conflicting city commands while combat is active.
Resolve a whole player turn and its NPC response in a single command transaction,
then emit a detached response. Details and exit guarantees are in the combat
contract. This is a proposed extension, not a new current command.

Current events have a kind, day, message, and domain metadata. `player_command`
adds a command sequence ID; there is no universal global event ID and the log is
not an event-sourcing database. Continue saving authoritative world state.
For a future domain, define event schema versions and stable domain-instance IDs
(such as encounter/turn IDs), before/after values, reason codes, command cause,
and optional source-event references. Preserve historical event records as they
are; do not rewrite old prose to reconstruct imaginary structured facts.

**Legal integration is a specific prerequisite, not a solved abstraction.**
Current pending career cases and investigation events require `source_attempt`,
referring to a witnessed job. Combat cannot safely create a case by omitting that
field or fabricating a collection attempt. Before combat can produce cases,
design and test an additive case-source adapter, for example a discriminated
`source` containing a kind and stable ID, with legacy job-source compatibility.
Update case validation, ordinary/NPC investigation, legal responses, court and
event metadata together. Preserve once-per-day evidence processing and one-time
court outcomes. No warrant, probation, parole, undercover, or vigilante subsystem
is implied by that adapter.

## Deterministic processing and ownership

The current daily order remains clock/legacy activity, legal review/cooling,
career investigation, NPC actions, economy/strategy/warfare, and court. Future
domains need an explicit place in that order and a persisted last-processed marker.
Repeated calls, reloads, or UI refreshes cannot pay wages or recover health twice.
Do not insert hidden day advances into dialogue or tactical animations.

Keep each new random domain isolated from existing job and feud draws. Derive a
local RNG from the career seed, rules version, domain-instance ID, turn, actor ID,
and effect ID, using an explicit stable encoding. Do not use Python's `hash`,
wall-clock time, event-list length, or iteration order as the seed. Persist the
counters/decisions necessary for replay. Record material rolls and thresholds.
Unrelated UI queries or flavor text must not consume simulation randomness.

An outcome should have one owner: combat settles health and encounter outcomes;
the legal adapter decides whether documented facts create a case; territory
effects use the shared capture operation. Do not have dialogue, UI, and daily
processing independently apply the same consequence. Persist settlement markers
so resume cannot repeat cash, reputation, injury, or legal effects.

## GUI, narrative, and knowledge adapters

A future GUI owns input, selection, accessibility, rendering and animation.
It calls the service serially, renders detached snapshots/responses, and uses the
same persistence API. It cannot hold mutable nested world references, independently
roll outcomes, or let two writers edit one save. Animation completion is not a
simulation event. A display clock does not become a real-time upgrade timer.

Narrative chooses eligible local text and presents choices; committed choices
invoke ordinary validated commands. Text variants cannot grant cash or change
loyalty as a side effect of being viewed. Mission completion requires persisted
state transitions and exactly-once effects, not a line of dialogue being reached.
Keep localized text keys and asset paths outside mechanical decision logic.

Future street intelligence needs an explicit player-knowledge read model.
Existing omniscient city reports cannot simply be relabeled rumors. A false claim
may cause a genuine player decision without changing the truth of the claim.
NPC decisions must specify whether they use facts, observations, or beliefs.
This was outside the historical M014 proposal. M018 implements only the small
local information adapter described above, not this proposed citywide layer.

## Small, reviewable adoption sequence

1. Review the M014 contract, especially action costs, exits, legal-source migration,
   and provisional numbers. Do not begin implementation as part of M013.1.
2. When separately authorized, add only the combat state/definitions and case
   adapter that its approved contract requires, with neutral test participants.
3. Introduce employer/contracts or mission definitions in their own later milestone,
   with compatibility adapters before moving existing content.
4. Add knowledge and narrative definitions when player-facing systems use them.
   Approve any licensed pack and distribution separately.

For every adoption, retain old fixtures; test malformed references, unsupported
versions, command rollback, exactly-once settlement, read isolation, JSON round
trips, fresh-process/hash-seed determinism, save/resume at decision boundaries,
and long campaigns. A small standard-library loader and explicit validators are
enough. No database, mandatory AI service, ECS, asynchronous framework, dependency,
or complete content rewrite is justified by this proposal.
