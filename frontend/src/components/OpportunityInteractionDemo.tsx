// OpportunityInteractionDemo — a small, self-contained state container for the
// synthetic preview. It holds the current presentation state and maps user
// actions to state transitions, then feeds the pure `OpportunityInteraction`
// component. It submits nothing, persists nothing, and reaches no engine.

import { useCallback, useMemo, useState } from "react";
import {
  INTERACTION_STATES,
  INTERACTION_STATE_LABELS,
  OPENING_REPAIR_SHIFT,
  SYNTHETIC_DECLINE_OPTION_ID,
  SYNTHETIC_TAKE_OPTION_ID,
  previewOpportunityAdapter,
} from "../gameplay/interaction";
import type { InteractionState, InteractionViewModel } from "../gameplay/interaction";
import { OpportunityInteraction } from "./OpportunityInteraction";
import type { OpportunityInteractionCallbacks } from "./OpportunityInteraction";

/** States that render a referenced (selected) option. */
const SELECTED_STATES: readonly InteractionState[] = ["pending", "confirmed", "rejected", "consequence"];

export function OpportunityInteractionDemo({ className }: { className?: string }) {
  const [state, setState] = useState<InteractionState>("choices");
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(SYNTHETIC_TAKE_OPTION_ID);
  const [pendingStatus, setPendingStatus] = useState<InteractionViewModel["pendingStatus"]>("not_submitted");

  const model = useMemo<InteractionViewModel>(() => {
    if (selectedOptionId && SELECTED_STATES.includes(state)) {
      return previewOpportunityAdapter.toView(OPENING_REPAIR_SHIFT, state, { ...previewOpportunityAdapter.forState(state), selectedOptionId, pendingStatus });
    }
    return previewOpportunityAdapter.forState(state);
  }, [state, selectedOptionId, pendingStatus]);

  const handleSelectOption = useCallback((optionId: string) => {
    if (!OPENING_REPAIR_SHIFT.options.some(option => option.id === optionId && option.availability === "available")) return;
    setPendingStatus("not_submitted");
    setSelectedOptionId(optionId);
    setState(optionId === SYNTHETIC_DECLINE_OPTION_ID ? "refusal" : "pending");
  }, []);

  const handleCancel = useCallback(() => { if (state === "pending" && pendingStatus === "not_submitted") setState("choices"); }, [state, pendingStatus]);
  const handleReset = useCallback(() => setState("choices"), []);
  const handleRefresh = useCallback(() => setState("choices"), []);
  // Submission is disabled in the preview; confirm is present but inert.
  const handleConfirm = useCallback(() => undefined, []);

  const callbacks: OpportunityInteractionCallbacks = {
    onSelectOption: handleSelectOption,
    onConfirm: handleConfirm,
    onCancel: handleCancel,
    onRefreshEligibility: handleRefresh,
    onReset: handleReset,
  };

  return (
    <div className={className}>
      <div
        role="group"
        aria-label="Preview interaction state (demonstration only)"
        className="mb-2 flex flex-wrap items-center gap-1.5"
      >
        <span className="mr-1 text-[11px] uppercase tracking-wide text-muted">Preview state</span>
        {INTERACTION_STATES.map((s) => (
          <button
            key={s}
            type="button"
            aria-pressed={state === s}
            onClick={() => { setPendingStatus("not_submitted"); setSelectedOptionId(s === "refusal" ? SYNTHETIC_DECLINE_OPTION_ID : SYNTHETIC_TAKE_OPTION_ID); setState(s); }}
            className={`cursor-pointer rounded-full border px-2.5 py-0.5 text-[11px] font-medium transition-colors duration-150 ${
              state === s
                ? "border-primary bg-primary/15 text-primary-strong"
                : "border-border bg-surface text-muted hover:border-primary hover:text-primary"
            }`}
          >
            {INTERACTION_STATE_LABELS[s]}
          </button>
        ))}
      </div>
      <p className="mb-2 text-xs text-muted">Tess Navarro: repair worker and cooperative coordinator. These examples do not change the career above.</p>
      {state === "pending" && pendingStatus === "not_submitted" ? (
        <button type="button" className="mb-2 rounded border border-border px-2 py-1 text-xs" onClick={() => setPendingStatus("outcome_uncertain")}>Show uncertain transmission example</button>
      ) : null}
      <OpportunityInteraction model={model} callbacks={callbacks} />
    </div>
  );
}
