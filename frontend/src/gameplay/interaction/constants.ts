import type { InteractionState } from "./types";

/**
 * The mandatory label for every authored synthetic surface in this mission.
 * Nothing in the preview is persisted; the player must never mistake it for a
 * live career.
 */
export const SYNTHETIC_PREVIEW_LABEL = "Synthetic Preview — No Persistent Gameplay";

/** The eight canonical presentation states, in narrative order. */
export const INTERACTION_STATES: readonly InteractionState[] = [
  "undiscovered",
  "eligibility",
  "choices",
  "refusal",
  "pending",
  "confirmed",
  "rejected",
  "consequence",
];

/** Human-facing labels for each state. */
export const INTERACTION_STATE_LABELS: Record<InteractionState, string> = {
  undiscovered: "Undiscovered",
  eligibility: "Eligibility",
  choices: "Choices",
  refusal: "Refusal",
  pending: "Pending",
  confirmed: "Confirmed",
  rejected: "Rejected",
  consequence: "Consequence",
};
