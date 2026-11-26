// Player-safe interaction view-model.
//
// This module defines the NORMALISED shape the presentational
// `OpportunityInteraction` component renders. It is deliberately free of any
// wire, transport, or engine detail: a presentational component must depend on
// this file only, never on `liveEngine.ts`, `host.ts`, `outbox.ts`, the live
// provider, or `fetch`.
//
// The view-model is derived from the *existing* wire contract
// (`Opportunity` / `OpportunityOption` in `src/gameplay/wire/types.ts`). It does
// NOT redefine that contract — see `adapter.ts` for the mapping. No engine rule
// is re-implemented here; this is a display projection only.

/**
 * The eight canonical UI presentation states (see
 * `docs/prd/preview-interaction-mission.md`). These are presentation states
 * derived from authored/preview data — none of them are new protocol states.
 */
export type InteractionState =
  | "undiscovered"
  | "eligibility"
  | "choices"
  | "refusal"
  | "pending"
  | "confirmed"
  | "rejected"
  | "consequence";

/** One selectable option, projected from wire `OpportunityOption`. */
export interface InteractionOptionView {
  /** Mirrors wire `OpportunityOption.id`. */
  id: string;
  /** Mirrors wire `OpportunityOption.label`. */
  label: string;
  /** Mirrors wire `OpportunityOption.availability === "available"`. */
  available: boolean;
  /** Mirrors wire `OpportunityOption.reason` (player-safe block reason). */
  reason: string | null;
  /** Mirrors wire `OpportunityOption.action_cost`. */
  actionCost: number;
  /** Mirrors wire `OpportunityOption.tradeoff`. */
  tradeoff: string;
}

/**
 * The single normalised view-model the interaction component renders. One
 * object always describes exactly one of the eight presentation states.
 */
export interface InteractionViewModel {
  /** Which of the eight presentation states is being rendered. */
  state: InteractionState;
  /** The authored synthetic label. Always present in preview. */
  syntheticLabel: string;
  /**
   * True in preview. The component must never present a live submission
   * affordance — command submission is disabled in this mission.
   */
  submissionDisabled: boolean;
  /** Unsent selection can be cancelled; transmitted uncertainty requires receipt recovery. */
  pendingStatus: "not_submitted" | "outcome_uncertain";
  /** Mirrors wire `Opportunity.id`. */
  opportunityId: string;
  /** Mirrors wire `Opportunity.title`. */
  title: string;
  /** Mirrors wire `Opportunity.situation`. */
  situation: string;
  /** Mirrors wire `Opportunity.speaker`. */
  speaker: string;
  /** Mirrors wire `Opportunity.open_day`. */
  openDay: number;
  /** Mirrors wire `Opportunity.expires_day`. */
  expiresDay: number;
  /** Mirrors wire `Opportunity.state` (arbitrary engine string). */
  engineState: string;
  /** Projected options. Empty for `undiscovered`. */
  options: InteractionOptionView[];
  /** Player-safe block reasons (unique), derived from unavailable options. */
  blockReasons: string[];
  /** The option referenced by pending/confirmed/rejected/consequence. */
  selectedOptionId: string | null;
  /** Recorded aftermath feedback (mirrors wire `outcomes[].feedback`). */
  consequenceFeedback: string | null;
  /**
   * Required offer fields that were absent. When non-empty the component
   * renders an explicit "unavailable — data not provided" state and never
   * synthesises a value.
   */
  missingData: string[];
}

/** An authored, directly-renderable example of one presentation state. */
export interface InteractionDemo {
  id: InteractionState;
  label: string;
  summary: string;
  model: InteractionViewModel;
}
