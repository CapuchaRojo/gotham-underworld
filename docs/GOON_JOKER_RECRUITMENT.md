# Gotham: The Goon — Joker Recruitment Contract

**Status: original campaign rule proposed by the M013.1 addendum; unimplemented.**
This is not an established DC-universe recruitment law. No Joker, Arkham episode,
street cell, membership gate or new command is added to the executable. The
[employer matrix](GOON_FACTION_EMPLOYER_MATRIX.md),
[opportunity contract](GOON_CONDITIONAL_OPPORTUNITIES.md) and
[institution rules](GOON_INSTITUTIONS_AND_RECOVERY.md) must be read consistently
with this proposal. The existing original factions and immediate joining behavior
remain unchanged.

## Campaign rule

1. Joker-affiliated street opportunities form a citywide pool throughout Gotham,
   not only in a district owned by a Joker organization. Particular offers depend
   on local demand, world state and recorded eligibility; they are not guaranteed
   in every location on every day.
2. The player can encounter and work alongside Joker goons, take a bounded cell
   contract, refuse it or become a coworker's friend **without formal membership**.
3. Formal Joker-gang initiation requires a **direct encounter with Joker during
   an Arkham storyline**. A rumor, proxy, recording, costume, prior street job or
   relationship score cannot satisfy that gate.
4. That encounter is necessary, not sufficient. Joker may withhold an invitation;
   the player may be ineligible; the offer may become invalid. No encounter or
   recruitment is guaranteed.
5. Joker's presence, availability and role must match the selected continuity and
   current world state. An absent/deceased/unavailable Joker cannot be spawned
   merely because the player reaches a reputation threshold.
6. The player can decline initiation. Refusal leaves viable independent, civilian,
   other-employer and campaign-completion routes. Disclosed, bounded fallout may
   remain; it cannot turn refusal into an irreversible no-input punishment.
7. Joker-affiliated cells may operate autonomously during his absence. They have
   their own participants, demand and bounded commitments; a street cell cannot
   automatically initiate members on Joker's behalf.
8. Accepted formal membership has meaningful, persistent and explainable effects
   on reputation, specific relationships, personal safety and legal exposure.

This contract is intentionally stricter than the generic referral proposal. It
belongs in proposed DC-specific campaign data/policy, not a name check inside
the engine or a rule applied to every employer. No license is claimed.

## What counts as the Arkham gate

A future authored episode records an actual, direct in-person encounter with the
correct Joker actor instance, in a valid Arkham storyline/location and continuity.
The gate is committed when that encounter resolves, not when its description is
previewed. Save the encounter ID, participant ID, campaign/continuity version and
relevant outcome. A lookalike or unreliable account remains a different fact.

Arkham participation does **not** require the player to become a psychiatric
patient. Valid visitor/work/story access, evaluation, lawful transfer or admission
must each satisfy their own fictional rules. Conviction, distress or desire for
recruitment cannot auto-commit someone. Committing crimes, repeatedly seeking
admission or choosing treatment must not be an optimal invitation-farming loop.
An ordinary advocate/provider and campaign exit remain available if Joker is absent.

Proposed formal initiation occurs only through an eligible authored offer in that
direct encounter, with explicit player acceptance before its terms expire. If
presence, legal access or consent conditions change before commitment, reject
atomically and record any later withdrawal as a separate valid transition. A
previous encounter is not an evergreen coupon for a remote recruiter to bypass
Joker. No later reload, proxy or street reputation can silently complete initiation.

## Association, work and membership are different facts

| Fact | What it permits | What it cannot prove |
| --- | --- | --- |
| Street contact | Learn about an offer or meet a goon | Authentic authorization, trust or membership |
| Cell contract | Perform/decline the accepted work under its actual terms | Joker's personal approval or future availability |
| Personal relationship | A particular coworker may recommend, warn or help | Automatic allegiance of an entire organization |
| Arkham encounter | Satisfy one necessary recorded gate | A guaranteed offer or accepted initiation |
| Valid offer | Review declared benefits, obligations, risks and refusal | Consent or immunity from consequences |
| Explicit accepted initiation | Gain the defined membership/access and obligations | Universal knowledge, psychiatric consent, erased evidence or permanent protection |

Coercion, fear, fictional chemical influence and a character's claim of devotion
are not voluntary membership consent. A disputed claim can affect what an NPC
believes, but it cannot rewrite the authoritative membership record. Autonomous
cells cannot manufacture a direct-encounter record to grant access.

## Persistent consequences, with information boundaries

| Domain | Proposed effect | Safeguard / alternative |
| --- | --- | --- |
| Reputation | Known initiation/work changes how a particular employer or community assesses the player | No citywide telepathy; show who learned the relevant fact and why |
| Relationships | A coworker may welcome access while a friend questions the commitment | Reactions depend on known facts, personal goals and earlier promises; no automatic reset of every friendship |
| Safety | Orders, rival attention and unreliable promises create new risks and obligations | Signal known hazards, preserve refusal/exit/support routes and bound losses; membership is not safety armor |
| Legal exposure | Documented acts, witnesses or a justified inquiry can connect the player to a case | Affiliation/heat alone does not convict or create evidence; existing case-source/court invariants require explicit future integration |
| Opportunities | Open some cell responsibilities while closing conflicting trusted work | No employer is required for an ending; legitimate work and other contacts remain plausible |

The exact deltas and initiation scene require later approval. Do not copy an
existing Joker scene, joke, dialogue or game plot. An original encounter must
preserve recognizable danger without assigning unexplained punishment through
an unseeded roll or treating psychiatric patients as recruitment collectibles.

## Determinism, compatibility and future acceptance checks

Implement eligibility as ordinary allowlisted predicates over stable IDs, actor
availability, valid episode/encounter state and explicit choices. Selection uses
its own recorded trigger/draw under the opportunity contract. Revalidate at the
command boundary, settle membership once, emit structured before/after/cause
events and return a detached result. Viewing an offer never advances a phase.

No current save changes. A later versioned extension must preserve historical
affiliations and introduce no retroactive Joker contacts, institutional admissions
or invitation draws. Never reinterpret Carnival Crew as a Joker cell. Pin the
content/continuity definitions needed for offline resume. Current three-action
boundaries remain; a later episode contract must specify costs and safe exit
when the daily allowance is exhausted, without creating a paid waiting gate.

| Ten-field review | Proposed answer |
| --- | --- |
| Decision | Work alongside, verify, refuse, pursue eligible contact, accept or decline initiation |
| Observable consequence | Separate contract, encounter, offer and membership states; explain known terms and reactions |
| Persistent state | Encounter/offer/consent provenance, membership, obligations and informed relationship/legal effects |
| Alternatives | Street association without membership, no encounter, no invitation, refusal or a different career |
| Replayability | Continuity, Joker availability, cell demand, contacts and conflicting commitments |
| Grind risk | Job/reputation, admission and referral farming; no repeat reward or guaranteed invitation |
| Determinism | Stable episode/actor IDs, recorded eligibility/draws and exactly-once acceptance |
| Save compatibility | Future additive state; no inferred gate, auto-admission or placeholder-faction rename |
| Offline | Local content and policies, simulation-day expiry, complete non-Joker career routes |
| Exploits / agency | No proxy initiation, forged gate, absent-Joker spawn, coercion-as-consent or refusal softlock |

Future tests must reject formal initiation without the direct Arkham encounter,
wrong actor/continuity/location, absent Joker, missing offer, declined/expired
terms or exhausted applicable action budget **without mutating the world**.
Test repeat acceptance, cell autonomy while Joker is absent, street work without
membership, unavailable Arkham actors, read isolation, deterministic resume and
a complete campaign without recruitment. These are future acceptance criteria,
not executed gameplay tests.

**Paper-only scenario:** a driver works a Joker-cell shift and befriends a goon.
That relationship may produce a sourced lead but no membership. In one career,
a valid Arkham episode later permits a direct encounter; Joker offers nothing.
In another, an eligible offer appears and the player declines to protect a
civilian reference. A third accepts, gains conditional access and loses a known
contact's trust while retaining responsibility for witnessed acts. The cells
continue their own work during Joker's absence in all three careers.
