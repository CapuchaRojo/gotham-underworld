// OpportunityInteraction — the single reusable, presentational component that
// renders one consequential opportunity across the eight canonical
// presentation states.
//
// Boundary (do not violate): this component renders from the normalised
// `InteractionViewModel` only. It performs no fetch, no persistence, and
// imports no transport/engine module. Command submission is disabled in the
// preview, so the "confirm" affordance is deliberately inert and disabled.
//
// Accessibility: the panel is a labelled region with a polite live region that
// announces each state transition; Escape cancels; every action is a native
// focusable control; no keyboard traps.

import { useEffect, useId, useRef } from "react";
import type { KeyboardEvent as ReactKeyboardEvent, ReactNode } from "react";
import { INTERACTION_STATE_LABELS } from "../gameplay/interaction/constants";
import type { InteractionOptionView, InteractionState, InteractionViewModel } from "../gameplay/interaction/types";
import { StateBadge } from "./StateBadge";
import type { BadgeTone } from "./StateBadge";
import { CheckIcon, ClockIcon, EyeOffIcon, InfoIcon, LockIcon, XIcon } from "./icons";
import { AbstainIcon, ListIcon, TrailIcon } from "./interactionIcons";

export interface OpportunityInteractionCallbacks {
  /** An option in the `choices` state was activated. */
  onSelectOption?: (optionId: string) => void;
  /** The (preview-disabled) confirm affordance — present but inert. */
  onConfirm?: () => void;
  /** Cancel an unsent selection only. Never undo a transmitted request. */
  onCancel?: () => void;
  /** Re-check eligibility after a rejection. */
  onRefreshEligibility?: () => void;
  /** Return to the stable state (e.g. `choices`). */
  onReset?: () => void;
}

export interface OpportunityInteractionProps {
  model: InteractionViewModel;
  callbacks?: OpportunityInteractionCallbacks;
  /** Heading level for the offer title. Defaults to 3. */
  headingLevel?: 2 | 3 | 4;
  className?: string;
}

const STATE_TONE: Record<InteractionState, BadgeTone> = {
  undiscovered: "neutral",
  eligibility: "info",
  choices: "positive",
  refusal: "neutral",
  pending: "warning",
  confirmed: "positive",
  rejected: "danger",
  consequence: "info",
};

function StateIcon({ state }: { state: InteractionState }): ReactNode {
  switch (state) {
    case "undiscovered":
      return <EyeOffIcon />;
    case "eligibility":
      return <LockIcon />;
    case "choices":
      return <ListIcon />;
    case "refusal":
      return <AbstainIcon />;
    case "pending":
      return <ClockIcon />;
    case "confirmed":
      return <CheckIcon />;
    case "rejected":
      return <XIcon />;
    case "consequence":
      return <TrailIcon />;
  }
}

function actionCostLabel(cost: number): string {
  if (cost <= 0) return "No action";
  return cost === 1 ? "1 action" : `${cost} actions`;
}

const BTN_PRIMARY =
  "cursor-pointer rounded-md bg-primary px-3 py-2 text-sm font-semibold text-on-primary transition-transform duration-150 hover:bg-primary-strong active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100";
const BTN_SECONDARY =
  "cursor-pointer rounded-md border border-border bg-surface px-3 py-2 text-sm font-medium text-foreground transition-colors duration-150 hover:border-primary hover:text-primary active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100";

function OptionButton({
  option,
  onSelect,
}: {
  option: InteractionOptionView;
  onSelect?: (id: string) => void;
}) {
  const reasonId = useId();
  return (
    <button
      type="button"
      disabled={!option.available}
      onClick={() => { if (option.available) onSelect?.(option.id); }}
      aria-describedby={option.available || !option.reason ? undefined : reasonId}
      className="w-full cursor-pointer rounded-lg border border-border bg-surface p-3 text-left transition-colors duration-150 hover:border-primary hover:bg-surface-hover active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:border-border disabled:hover:bg-surface disabled:active:scale-100"
    >
      <span className="flex items-start justify-between gap-3">
        <span className="min-w-0 text-sm font-semibold text-foreground">{option.label}</span>
        <span className="shrink-0 text-xs font-medium text-muted">{actionCostLabel(option.actionCost)}</span>
      </span>
      <span className="mt-1 block text-xs leading-relaxed text-muted">{option.tradeoff}</span>
      {!option.available && option.reason ? (
        <span id={reasonId} className="mt-2 block text-xs font-medium text-danger-strong">
          Blocked — {option.reason}
        </span>
      ) : null}
    </button>
  );
}

export function OpportunityInteraction({
  model,
  callbacks,
  headingLevel = 3,
  className,
}: OpportunityInteractionProps) {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const instanceId = useId();
  const previous = useRef(`${model.state}:${model.pendingStatus}`);

  // Orient keyboard/AT users on a state transition (not on first mount).
  useEffect(() => {
    const current = `${model.state}:${model.pendingStatus}`;
    if (previous.current !== current) headingRef.current?.focus();
    previous.current = current;
  }, [model.state, model.pendingStatus]);

  const handleKeyDown = (event: ReactKeyboardEvent<HTMLElement>) => {
    if (event.key === "Escape" && model.state === "pending" && model.pendingStatus === "not_submitted" && model.missingData.length === 0 && callbacks?.onCancel) {
      event.stopPropagation();
      callbacks.onCancel();
    }
  };

  const Heading = `h${headingLevel}` as "h2" | "h3" | "h4";
  const stateLabel = INTERACTION_STATE_LABELS[model.state];
  const headingId = `opp-interaction-${instanceId}`;
  const dataMissing = model.missingData.length > 0;

  const selectedOption = model.selectedOptionId
    ? model.options.find((o) => o.id === model.selectedOptionId) ?? null
    : null;

  const title = model.state === "undiscovered" ? "Undiscovered opportunity" : model.title;
  const subtitle = model.state === "undiscovered" ? "Details not discovered." : [
    `Spoken by ${model.speaker}`,
    `Day ${model.openDay} to before day ${model.expiresDay}`,
  ].join(" · ");

  return (
    <section
      data-state={model.state}
      data-synthetic="true"
      aria-labelledby={headingId}
      onKeyDown={handleKeyDown}
      className={`noir-panel p-4 ${className ?? ""}`}
    >
      {/* Synthetic honesty chip — every authored surface carries this. */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-institutional/40 bg-institutional/10 px-2.5 py-0.5 text-[11px] font-medium text-institutional-strong">
          <InfoIcon className="h-3.5 w-3.5" aria-hidden="true" />
          {model.syntheticLabel}
        </span>
        <StateBadge tone={STATE_TONE[model.state]} icon={<StateIcon state={model.state} />}>
          {stateLabel}
        </StateBadge>
      </div>

      {/* Polite live region: announces the state transition to screen readers. */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {`Opportunity state: ${stateLabel}. ${title}.`}
      </div>

      <div className="mt-3">
        <Heading ref={headingRef} tabIndex={-1} id={headingId} className="text-base font-semibold text-foreground">
          {title}
        </Heading>
        <p className="mt-0.5 text-xs text-muted">{subtitle}</p>
      </div>

      <div className="mt-3">
        {dataMissing ? (
          <DataMissing missing={model.missingData} />
        ) : (
          <Body model={model} selectedOption={selectedOption} callbacks={callbacks} />
        )}
      </div>

      {dataMissing ? null : (
        <Footer model={model} selectedOption={selectedOption} callbacks={callbacks} />
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// State bodies
// ---------------------------------------------------------------------------

function DataMissing({ missing }: { missing: string[] }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted">
      <InfoIcon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>
        <span className="font-semibold text-foreground">Unavailable — data not provided.</span>{" "}
        This offer can’t be shown because required detail is missing: {missing.join(", ")}.
      </span>
    </div>
  );
}

function Body({
  model,
  selectedOption,
  callbacks,
}: {
  model: InteractionViewModel;
  selectedOption: InteractionOptionView | null;
  callbacks?: OpportunityInteractionCallbacks;
}) {
  switch (model.state) {
    case "undiscovered":
      return (
        <p className="flex items-start gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted">
          <EyeOffIcon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <span>
            You’ve heard there’s work here, but nothing’s surfaced yet. Keep your ears open — it
            hasn’t opened to you.
          </span>
        </p>
      );

    case "eligibility":
      return model.blockReasons.length > 0 ? (
        <div className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm">
          <p className="font-semibold text-danger-strong">Not open to you — yet.</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-5 text-danger-strong/90">
            {model.blockReasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
          <p className="mt-1 text-xs text-muted">{model.situation}</p>
        </div>
      ) : (
        <div className="rounded-lg border border-money/40 bg-money/10 px-3 py-2 text-sm">
          <p className="font-semibold text-money-strong">You qualify for this shift.</p>
          <p className="mt-1 text-xs text-muted">{model.situation}</p>
        </div>
      );

    case "choices":
      return (
        <div>
          <p className="mb-2 text-sm leading-relaxed text-muted">{model.situation}</p>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted">Your options</p>
          <ul className="space-y-2">
            {model.options.map((option) => (
              <li key={option.id}>
                <OptionButton option={option} onSelect={(id) => callbacks?.onSelectOption?.(id)} />
              </li>
            ))}
          </ul>
        </div>
      );

    case "refusal":
      return (
        <div className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted">
          <p className="font-semibold text-foreground">Decline selected — not submitted.</p>
          <p className="mt-1">
            Declining is a genuine alternative: no wage, and this offer would close. Later local work
            remains possible. A refusal can have consequences; it is not a promise to reserve the shift.
            This is a synthetic illustration, so no refusal has been recorded.
          </p>
        </div>
      );

    case "pending":
      if (model.pendingStatus === "outcome_uncertain") return (
        <div className="rounded-lg border border-institutional/40 bg-institutional/10 px-3 py-2 text-sm">
          <p className="font-semibold">Transmitted, outcome uncertain — illustration only.</p>
          <p>A lost acknowledgment is not a rejection. Recover the original request receipt before any further action.
            Cancel cannot undo an in-flight or committed request. This preview sends nothing.</p>
        </div>
      );
      return (
        <div className="rounded-lg border border-primary/40 bg-primary/10 px-3 py-2 text-sm">
          <p className="font-semibold text-primary-strong">
            {selectedOption ? selectedOption.label : "Your choice"} — not submitted.
          </p>
          <p className="mt-1 text-xs text-muted">
            Nothing has been sent. Confirm is disabled in the synthetic preview; there is no live
            engine to commit to.
          </p>
        </div>
      );

    case "confirmed":
      return (
        <div className="rounded-lg border border-money/40 bg-money/10 px-3 py-2 text-sm">
          <p className="font-semibold text-money-strong">Outcome — demonstration only.</p>
          <p className="mt-1 text-xs text-muted">
            In a live build this state renders from a committed receipt. Here it is an illustration:
            no wages were paid and no effects were applied.
          </p>
          {model.consequenceFeedback ? (
            <p className="mt-2 border-t border-border pt-2 text-xs italic text-muted">
              Illustrative result: {model.consequenceFeedback}
            </p>
          ) : null}
        </div>
      );

    case "rejected":
      return (
        <div className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm">
          <p className="font-semibold text-danger-strong">Not accepted.</p>
          <p className="mt-1 text-danger-strong/90">
            This illustrates an explicit rejection from the engine. A transport failure or lost acknowledgment
            instead leaves the outcome uncertain and requires original-request receipt recovery. No request was sent here.
          </p>
        </div>
      );

    case "consequence":
      return (
        <div className="rounded-lg border border-institutional/40 bg-institutional/10 px-3 py-2 text-sm">
          <p className="font-semibold text-institutional-strong">Aftermath — preview illustration.</p>
          {model.consequenceFeedback ? (
            <p className="mt-1 text-xs text-muted">{model.consequenceFeedback}</p>
          ) : (
            <p className="mt-1 text-xs text-muted">No aftermath recorded.</p>
          )}
          <p className="mt-1 text-xs text-muted">Nothing here is persisted.</p>
        </div>
      );
  }
}

// ---------------------------------------------------------------------------
// State footers (actions)
// ---------------------------------------------------------------------------

function Footer({
  model,
  selectedOption,
  callbacks,
}: {
  model: InteractionViewModel;
  selectedOption: InteractionOptionView | null;
  callbacks?: OpportunityInteractionCallbacks;
}) {
  switch (model.state) {
    case "undiscovered":
      return (
        <p className="mt-3 text-xs text-muted">Nothing to do here yet.</p>
      );

    case "eligibility":
      return model.blockReasons.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            className={BTN_SECONDARY}
            onClick={() => callbacks?.onRefreshEligibility?.()}
          >
            Check again
          </button>
        </div>
      ) : null;

    case "choices":
      return (
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            className={BTN_SECONDARY}
            onClick={() => callbacks?.onReset?.()}
          >
            Leave it for now
          </button>
        </div>
      );

    case "refusal":
      return (
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className={BTN_SECONDARY} onClick={() => callbacks?.onReset?.()}>
            Return to preview choices
          </button>
        </div>
      );

    case "pending":
      if (model.pendingStatus === "outcome_uncertain") return (
        <p className="mt-3 text-xs text-muted">Receipt recovery is unavailable in this synthetic preview. No cancel or retry is offered.</p>
      );
      return (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button
            type="button"
            className={BTN_PRIMARY}
            disabled
            aria-disabled="true"
            title="Command submission is disabled in the synthetic preview."
          >
            {selectedOption ? `Confirm: ${selectedOption.label}` : "Confirm"}
          </button>
          <button type="button" className={BTN_SECONDARY} onClick={() => callbacks?.onCancel?.()}>
            Cancel <span className="text-muted">(Esc)</span>
          </button>
        </div>
      );

    case "confirmed":
      return (
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className={BTN_SECONDARY} onClick={() => callbacks?.onReset?.()}>
            Start over
          </button>
        </div>
      );

    case "rejected":
      return (
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            className={BTN_PRIMARY}
            onClick={() => callbacks?.onRefreshEligibility?.()}
          >
            Refresh eligibility
          </button>
          <button type="button" className={BTN_SECONDARY} onClick={() => callbacks?.onReset?.()}>
            Start over
          </button>
        </div>
      );

    case "consequence":
      return (
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className={BTN_SECONDARY} onClick={() => callbacks?.onReset?.()}>
            Start over
          </button>
        </div>
      );
  }
}
