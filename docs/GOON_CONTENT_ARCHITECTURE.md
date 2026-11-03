# Content architecture recommendations

**Status: M013.1 proposal only.** No registries, schemas, commands, migrations,
or content packs described as proposed below are implemented by this milestone.
The current runtime remains M013. This document supports the
[narrative bible](GOON_NARRATIVE_DESIGN_BIBLE.md) and the separately reviewable
[M014 combat contract](M014_COMBAT_DESIGN_CONTRACT.md).

## Current boundary and constraints

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
for ten new modules at once. Introduce only the definitions a milestone uses.

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
This is outside M014's minimum combat scope and adds no misinformation now.

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
