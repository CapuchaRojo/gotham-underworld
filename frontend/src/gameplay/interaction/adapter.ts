// PREVIEW OPPORTUNITY ADAPTER
//
// Maps an authored wire-shaped `Opportunity` (plus a chosen presentation state)
// into the normalised, player-safe `InteractionViewModel` the presentational
// component renders. A future `liveOpportunityAdapter` will produce the SAME
// view-model from validated `PlayerProjection.opportunities` + committed
// receipts — the component will not need to change.
//
// Boundary: this module is pure. It performs no network access, no persistence,
// and imports no transport/engine module.

import type { Opportunity } from "../wire/types";
import { INTERACTION_STATES, INTERACTION_STATE_LABELS, SYNTHETIC_PREVIEW_LABEL } from "./constants";
import {
  GATED_STOCK_AUDIT,
  OPENING_REPAIR_SHIFT,
  SYNTHETIC_DECLINE_OPTION_ID,
  SYNTHETIC_OUTCOME,
  SYNTHETIC_TAKE_OPTION_ID,
} from "./scenario";
import type { InteractionDemo, InteractionOptionView, InteractionState, InteractionViewModel } from "./types";

/** States whose rendering requires a referenced (selected) option. */
const SELECTED_OPTION_STATES: readonly InteractionState[] = [
  "refusal",
  "pending",
  "confirmed",
  "rejected",
  "consequence",
];

function toOptionView(option: Opportunity["options"][number]): InteractionOptionView {
  return {
    id: option.id,
    label: option.label,
    available: option.availability === "available",
    reason: option.reason,
    actionCost: option.action_cost,
    tradeoff: option.tradeoff,
  };
}

function collectBlockReasons(options: InteractionOptionView[]): string[] {
  const seen = new Set<string>();
  const reasons: string[] = [];
  for (const option of options) {
    if (!option.available && option.reason && !seen.has(option.reason)) {
      seen.add(option.reason);
      reasons.push(option.reason);
    }
  }
  return reasons;
}

/**
 * Fields required for a surfaced offer. `undiscovered` legitimately has no
 * offer detail, so it is exempt. Missing fields are surfaced, never invented.
 */
function computeMissingData(model: InteractionViewModel): string[] {
  if (model.state === "undiscovered") return [];
  const missing: string[] = [];
  for (const key of ["title", "situation", "speaker"] as const)
    if (!model[key]?.trim()) missing.push(key);
  if (!Number.isSafeInteger(model.openDay) || !Number.isSafeInteger(model.expiresDay) || model.expiresDay <= model.openDay)
    missing.push("offer dates");
  if (model.options.length === 0) missing.push("options");
  if (SELECTED_OPTION_STATES.includes(model.state) && !model.options.some(option => option.id === model.selectedOptionId))
    missing.push("selected option");
  if (model.options.some(option => !option.available && !option.reason)) missing.push("eligibility reason");
  return missing;
}

export type InteractionOverrides = Partial<Omit<InteractionViewModel, "state">>;

/**
 * Project a wire-shaped `Opportunity` and a presentation state into the
 * normalised view-model. Pure and side-effect-free; never mutates `opportunity`.
 */
export function toInteractionView(
  opportunity: Opportunity,
  state: InteractionState,
  overrides: InteractionOverrides = {},
): InteractionViewModel {
  const projectedOptions = (opportunity.options ?? []).map(toOptionView);
  const options = state === "undiscovered" ? [] : projectedOptions;

  const base: InteractionViewModel = {
    state,
    syntheticLabel: SYNTHETIC_PREVIEW_LABEL,
    submissionDisabled: true,
    pendingStatus: "not_submitted",
    opportunityId: opportunity.id,
    title: opportunity.title,
    situation: opportunity.situation,
    speaker: opportunity.speaker,
    openDay: opportunity.open_day,
    expiresDay: opportunity.expires_day,
    engineState: opportunity.state,
    options,
    blockReasons: collectBlockReasons(options),
    selectedOptionId: null,
    consequenceFeedback: null,
    missingData: [],
  };

  const merged: InteractionViewModel = { ...base, ...overrides, submissionDisabled: true, syntheticLabel: SYNTHETIC_PREVIEW_LABEL };
  merged.missingData = [...new Set([...(overrides.missingData ?? []), ...computeMissingData(merged)])];
  return merged;
}

/**
 * Authored, directly-renderable example of every presentation state, used by
 * the Today view demo, the component tests, and the QA storyboard.
 */
export const PREVIEW_INTERACTION_DEMOS: Record<InteractionState, InteractionViewModel> = {
  undiscovered: toInteractionView(OPENING_REPAIR_SHIFT, "undiscovered"),
  eligibility: toInteractionView(GATED_STOCK_AUDIT, "eligibility"),
  choices: toInteractionView(OPENING_REPAIR_SHIFT, "choices"),
  refusal: toInteractionView(OPENING_REPAIR_SHIFT, "refusal", {
    selectedOptionId: SYNTHETIC_DECLINE_OPTION_ID,
  }),
  pending: toInteractionView(OPENING_REPAIR_SHIFT, "pending", {
    selectedOptionId: SYNTHETIC_TAKE_OPTION_ID,
  }),
  confirmed: toInteractionView(OPENING_REPAIR_SHIFT, "confirmed", {
    selectedOptionId: SYNTHETIC_TAKE_OPTION_ID,
    consequenceFeedback: SYNTHETIC_OUTCOME.feedback,
  }),
  rejected: toInteractionView(OPENING_REPAIR_SHIFT, "rejected", {
    selectedOptionId: SYNTHETIC_TAKE_OPTION_ID,
  }),
  consequence: toInteractionView(OPENING_REPAIR_SHIFT, "consequence", {
    selectedOptionId: SYNTHETIC_TAKE_OPTION_ID,
    consequenceFeedback: SYNTHETIC_OUTCOME.feedback,
  }),
};

/** Ordered demos, one per canonical presentation state. */
export const PREVIEW_INTERACTION_STORYBOARD: InteractionDemo[] = INTERACTION_STATES.map((id) => ({
  id,
  label: INTERACTION_STATE_LABELS[id],
  summary: summarise(id),
  model: PREVIEW_INTERACTION_DEMOS[id],
}));

function summarise(state: InteractionState): string {
  switch (state) {
    case "undiscovered":
      return "Work is rumoured here, but nothing has surfaced yet.";
    case "eligibility":
      return "The offer is visible but blocked — the reason is shown.";
    case "choices":
      return "The offer is open; options are selectable.";
    case "refusal":
      return "A synthetic refusal illustration: a genuine alternative with its own consequences.";
    case "pending":
      return "Selected, not submitted. Cancelling this unsent selection is distinct from receipt recovery after transmission.";
    case "confirmed":
      return "The committed outcome — demonstration only in preview.";
    case "rejected":
      return "Illustration of explicit rejection. A lost acknowledgment is uncertain and requires receipt recovery, not assumed failure.";
    case "consequence":
      return "The recorded aftermath, shown as a clearly-labelled preview.";
  }
}

/**
 * The preview adapter. Mirrors the shape a future `liveOpportunityAdapter` will
 * expose, so the component can consume either without a UI rewrite.
 */
export const previewOpportunityAdapter = {
  /** Build a view-model from any wire-shaped opportunity + state. */
  toView: toInteractionView,
  /** The authored demo for a given presentation state. */
  forState: (state: InteractionState): InteractionViewModel => PREVIEW_INTERACTION_DEMOS[state],
  /** Every authored demo, keyed by state. */
  demos: PREVIEW_INTERACTION_DEMOS,
  /** Ordered storyboard, one entry per state. */
  storyboard: PREVIEW_INTERACTION_STORYBOARD,
};
