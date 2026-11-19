// SYNTHETIC PREVIEW ONLY. Terms mirror content/neighborhood_life_v1.json.
// Python issues real choice IDs and eligibility; these preview.* IDs are never submitted.
import type { Opportunity, PlayerProjection } from "../wire/types";

export const OPENING_REPAIR_SHIFT_ID = "preview.choice.opening_shift";
export const OPENING_REPAIR_SHIFT_PLACE_ID = "goon.poi.p032";
export const OPENING_REPAIR_SHIFT_SPEAKER = "Tess Navarro";
export const SYNTHETIC_TAKE_OPTION_ID = "preview.option.work";
export const SYNTHETIC_DECLINE_OPTION_ID = "preview.option.decline";

// Illustrative activation day 1: Python start=0, duration=1; expires_day is exclusive.
export const OPENING_REPAIR_SHIFT: Opportunity = {
  id: OPENING_REPAIR_SHIFT_ID,
  title: "Uptown General Store — opening repair shift",
  situation: "The store has one funded repair shift. Tess needs a worker, not a declaration of lifelong loyalty.",
  speaker: OPENING_REPAIR_SHIFT_SPEAKER,
  open_day: 1,
  expires_day: 2,
  state: "open",
  command: "choose",
  options: [
    {
      id: SYNTHETIC_TAKE_OPTION_ID,
      label: "Work the repair shift",
      availability: "available",
      reason: null,
      action_cost: 1,
      tradeoff: "$20 guaranteed from the store's roster; one action and this shift slot. Preview terms only; no wage is paid here.",
      arguments: { choice_id: OPENING_REPAIR_SHIFT_ID, option_id: SYNTHETIC_TAKE_OPTION_ID },
    },
    {
      id: SYNTHETIC_DECLINE_OPTION_ID,
      label: "Decline this shift",
      availability: "available",
      reason: null,
      action_cost: 0,
      tradeoff: "No wage; later local work remains possible. Declining closes this offer; it does not reserve the shift.",
      arguments: { choice_id: OPENING_REPAIR_SHIFT_ID, option_id: SYNTHETIC_DECLINE_OPTION_ID },
    },
  ],
};

// A distinct late_work audit option: reference known, but illustrative standing 1 < 2.
// It is not an opening-shift option and does not imply a new Wayne Tower work site.
export const GATED_STOCK_AUDIT: Opportunity = {
  id: "preview.choice.late_work",
  title: "Late-week stock audit — Uptown General Store",
  situation: "A separate late-week audit at Uptown General Store requires Tess's reference and standing of at least 2. In this synthetic example the reference is known, but standing is 1.",
  speaker: OPENING_REPAIR_SHIFT_SPEAKER,
  open_day: 5,
  expires_day: 7,
  state: "open",
  command: "choose",
  options: [{
    id: "preview.option.audit",
    label: "Use Tess's reference for the stock audit",
    availability: "unavailable",
    reason: "Tess Navarro requires standing 2; current known standing is 1. Inspect the other listed options.",
    action_cost: 2,
    tradeoff: "$25; two actions for the more involved audit. Needs Tess's standing at least 2 and uses this offer's only allocation. Preview terms only.",
    arguments: { choice_id: "preview.choice.late_work", option_id: "preview.option.audit" },
  }],
};

export const SYNTHETIC_OUTCOME: PlayerProjection["outcomes"][number] = {
  choice_id: OPENING_REPAIR_SHIFT_ID,
  option_id: SYNTHETIC_TAKE_OPTION_ID,
  day: 1,
  feedback: "Illustration of a recorded repair-shift outcome. No wage was paid, no standing changed and nothing was persisted. A real result must come from Python's committed receipt.",
};
