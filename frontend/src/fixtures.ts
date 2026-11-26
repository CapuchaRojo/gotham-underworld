// SYNTHETIC GAMEPLAY FIXTURES — three immutable scenarios, clearly labeled preview
// data. Every referenced place/corridor identifier is REAL and comes from
// `src/atlas.ts` / `src/navigation.ts`; the life-state values (cash, arrears, work
// availability, commitments, observations) are authored fixture values for display
// only. Nothing here is persisted or simulated.

import type { Scenario } from "./types";

export const HOME_PLACE_ID = "goon.poi.p031"; // East Side Housing Cooperative (Upper East Side, n13)

const TESS: Scenario["contacts"][number] = {
  id: "contact.tess",
  name: "Tess",
  role: "Repair worker and cooperative coordinator",
  personality: "Patient, keeps receipts, checks in before deadlines.",
  standing: 2,
  known: "Handles your support advance and follows up on the notice.",
};

const MARLON: Scenario["contacts"][number] = {
  id: "contact.marlon",
  name: "Marlon",
  role: "Store owner, Upper East Side",
  personality: "Fair, quiet, remembers who pays on time.",
  standing: 1,
  known: "Runs Uptown General Store (p032) and hands out repair work.",
};

export const SCENARIOS: Scenario[] = [
  // --------------------------------------------------------------------------
  // Stable life (default)
  // --------------------------------------------------------------------------
  {
    id: "stable",
    label: "Stable life",
    summary: "Rent current, cash on hand, steady store work available.",
    day: 4,
    locationId: HOME_PLACE_ID,
    money: { cash: 40, arrears: 0, supportDebt: 0, prepaid: 0 },
    housing: { status: "current", arrears: 0, prepaid: 0, nextDueDay: 7 },
    budget: { actionsUsed: 1, actionsMax: 3, tuUsed: 6, tuMax: 18 },
    adoption: "active",
    work: [
      {
        id: "work.store-repair",
        title: "Uptown General Store — shelf repair",
        pay: 20,
        actions: 1,
        placeId: "goon.poi.p032",
        availability: "available",
        note: "Marlon needs the back shelving fixed. One action, paid same day.",
      },
      {
        id: "work.stock-audit",
        title: "Stock audit — Wayne Tower mailroom",
        pay: 25,
        actions: 2,
        placeId: "goon.poi.p046",
        availability: "unavailable",
        reason: "Work reference required",
        expiry: "Until a work reference is filed",
        note: "Two actions; the site supervisor asks for a reference first.",
      },
      {
        id: "work.home-kit",
        title: "Weekly home-work kit",
        pay: 24,
        actions: 1,
        placeId: HOME_PLACE_ID,
        availability: "available",
        note: "Standing order with Tess — small pay, but dependable.",
      },
    ],
    commitments: [
      {
        id: "cm.night-shift",
        title: "Night Shift incident statement",
        state: "fulfilled",
        detail: "Filed at North Borough Police Station (p044).",
      },
      {
        id: "cm.wrong-notice",
        title: "Wrong Notice follow-up",
        state: "open",
        detail: "Awaiting GCPD intake classification.",
      },
    ],
    observations: [
      {
        id: "obs.night-shift.own",
        incidentId: "inc.night-shift",
        incidentTitle: "Night Shift",
        claim: "A dark van idled near the docks after curfew.",
        sourceId: "source.own",
        sourceName: "You",
        sourceKind: "own",
        confidence: "unconfirmed",
        limitation: "Seen at a distance, poor light.",
      },
    ],
    contacts: [TESS, MARLON],
    institutions: [
      {
        id: "inst.gcpd-wrong-notice",
        name: "GCPD intake",
        kind: "police_intake",
        staff: "Desk clerk",
        placeId: "goon.poi.p053",
        status: "queued",
        classification: "Wrong Notice",
        credibility: "unestablished",
        note: "Intake logged the report; no classification yet.",
      },
    ],
  },

  // --------------------------------------------------------------------------
  // Financial pressure
  // --------------------------------------------------------------------------
  {
    id: "pressure",
    label: "Financial pressure",
    summary: "Rent overdue, support advance coming due, work is thinner.",
    day: 6,
    locationId: HOME_PLACE_ID,
    money: { cash: 11, arrears: 30, supportDebt: 20, prepaid: 0 },
    housing: { status: "overdue", arrears: 30, prepaid: 0, nextDueDay: 7 },
    budget: { actionsUsed: 3, actionsMax: 3, tuUsed: 12, tuMax: 18 },
    adoption: "active",
    work: [
      {
        id: "work.store-repair",
        title: "Uptown General Store — shelf repair",
        pay: 20,
        actions: 1,
        placeId: "goon.poi.p032",
        availability: "available",
        note: "Marlon can only pay after the repair is done.",
      },
      {
        id: "work.stock-audit",
        title: "Stock audit — Wayne Tower mailroom",
        pay: 25,
        actions: 2,
        placeId: "goon.poi.p046",
        availability: "unavailable",
        reason: "Work reference required",
        expiry: "Until a work reference is filed",
        note: "Better pay, but still gated on a reference.",
      },
      {
        id: "work.home-kit",
        title: "Weekly home-work kit",
        pay: 28,
        actions: 1,
        placeId: HOME_PLACE_ID,
        availability: "unavailable",
        reason: "Arrears — standing order suspended",
        expiry: "Until arrears are cleared",
        note: "Tess paused the kit while rent is overdue.",
      },
    ],
    commitments: [
      {
        id: "cm.rent",
        title: "Rent — Day 5",
        state: "missed",
        dueDay: 5,
        detail: "$30 overdue since Day 5; the ledger shows no prepayment.",
      },
      {
        id: "cm.support-advance",
        title: "Tess support advance",
        state: "pending",
        dueDay: 7,
        detail: "$20 due tomorrow, separate from rent.",
      },
      {
        id: "cm.night-shift",
        title: "Night Shift incident statement",
        state: "fulfilled",
        detail: "Filed at North Borough Police Station (p044).",
      },
    ],
    observations: [
      {
        id: "obs.night-shift.own",
        incidentId: "inc.night-shift",
        incidentTitle: "Night Shift",
        claim: "A dark van idled near the docks after curfew.",
        sourceId: "source.own",
        sourceName: "You",
        sourceKind: "own",
        confidence: "unconfirmed",
        limitation: "Seen at a distance, poor light.",
      },
      {
        id: "obs.wrong-notice.tess",
        incidentId: "inc.wrong-notice",
        incidentTitle: "Wrong Notice",
        claim: "A notice was delivered to an old address, not your current one.",
        sourceId: "contact.tess",
        sourceName: "Tess",
        sourceKind: "contact",
        confidence: "unconfirmed",
        limitation: "Tess is relaying what she was told.",
      },
    ],
    contacts: [TESS, MARLON],
    institutions: [
      {
        id: "inst.gcpd-wrong-notice",
        name: "GCPD intake",
        kind: "police_intake",
        staff: "Desk clerk",
        placeId: "goon.poi.p053",
        status: "clarification_requested",
        classification: "Wrong Notice",
        credibility: "needs_documentation",
        note: "Intake asked for a document proving the current address.",
      },
    ],
    restrictedRoute: {
      edgeId: "goon.edge.e16",
      label: "Blackgate Controlled Ferry",
      reason: "Authorized ferry — visitation permission required.",
    },
  },

  // --------------------------------------------------------------------------
  // Uncertain information
  // --------------------------------------------------------------------------
  {
    id: "uncertain",
    label: "Uncertain information",
    summary: "Adoption terms pending; two sources disagree on the notice.",
    day: 5,
    locationId: HOME_PLACE_ID,
    money: { cash: 18, arrears: 0, supportDebt: 0, prepaid: 0 },
    housing: { status: "current", arrears: 0, prepaid: 0, nextDueDay: 7 },
    budget: { actionsUsed: 2, actionsMax: 3, tuUsed: 8, tuMax: 18 },
    adoption: "pending",
    work: [
      {
        id: "work.store-repair",
        title: "Uptown General Store — shelf repair",
        pay: 20,
        actions: 1,
        placeId: "goon.poi.p032",
        availability: "available",
        note: "Marlon is holding the job until you confirm.",
      },
      {
        id: "work.unadopted-terms",
        title: "Unadopted work terms",
        pay: null,
        actions: 0,
        placeId: HOME_PLACE_ID,
        availability: "unavailable",
        reason: "Terms not adopted",
        expiry: "Inactive until adopted",
        note: "Pending adoption never activates on view.",
      },
    ],
    commitments: [
      {
        id: "cm.home-kit",
        title: "Weekly home-work kit",
        state: "cancelled",
        detail: "Cancelled while adoption terms were unadopted.",
      },
      {
        id: "cm.wrong-notice",
        title: "Wrong Notice follow-up",
        state: "open",
        detail: "Two sources disagree; neither is marked true.",
      },
    ],
    observations: [
      {
        id: "obs.wrong-notice.tess",
        incidentId: "inc.wrong-notice",
        incidentTitle: "Wrong Notice",
        claim: "The notice names a different address.",
        sourceId: "contact.tess",
        sourceName: "Tess",
        sourceKind: "contact",
        confidence: "unconfirmed",
        limitation: "Secondhand, from a voicemail.",
      },
      {
        id: "obs.wrong-notice.gcpd",
        incidentId: "inc.wrong-notice",
        incidentTitle: "Wrong Notice",
        claim: "Intake logged the notice under your current address.",
        sourceId: "inst.gcpd-wrong-notice",
        sourceName: "GCPD intake",
        sourceKind: "institution",
        confidence: "unconfirmed",
        limitation: "Intake entry only; no supporting document attached.",
      },
    ],
    contacts: [TESS, MARLON],
    institutions: [
      {
        id: "inst.gcpd-wrong-notice",
        name: "GCPD intake",
        kind: "police_intake",
        staff: "Desk clerk",
        placeId: "goon.poi.p053",
        status: "queued",
        classification: "Wrong Notice",
        credibility: "unestablished",
        note: "Intake and Tess disagree on the address.",
      },
    ],
    undiscoveredPlaceId: "goon.poi.p048", // Iceberg Lounge (Diamond District, n20)
  },
];

export const SCENARIO_BY_ID: ReadonlyMap<Scenario["id"], Scenario> = new Map(
  SCENARIOS.map((s) => [s.id, s]),
);
