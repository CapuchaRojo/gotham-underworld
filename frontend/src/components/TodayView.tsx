import type { CommitmentState, Scenario } from "../types";
import { placeById } from "../atlas";
import { accessSummary } from "../navigation";
import { playerSafeText, usePresentationMode } from "../presentation";
import { relativeDays } from "../relativeTime";
import { MoneySummary } from "./MoneySummary";
import { BudgetMeters } from "./BudgetMeters";
import { WorkCard } from "./WorkCard";
import { OpportunityInteractionDemo } from "./OpportunityInteractionDemo";
import { StateBadge } from "./StateBadge";
import type { BadgeTone } from "./StateBadge";
import { ArrowRightIcon, CalendarIcon, EyeOffIcon, InfoIcon, LockIcon, MapPinIcon } from "./icons";

export type TodayNavTarget = "streets" | "life" | "story";

const URGENT_STATES: CommitmentState[] = ["missed", "pending"];

function commitmentTone(state: CommitmentState): BadgeTone {
  switch (state) {
    case "missed":
    case "refused":
      return "danger";
    case "pending":
      return "warning";
    case "fulfilled":
      return "positive";
    case "open":
      return "info";
    default:
      return "neutral";
  }
}

function housingTone(status: Scenario["housing"]["status"]): BadgeTone {
  if (status === "current") return "positive";
  if (status === "overdue") return "danger";
  return "warning";
}

function housingLine(housing: Scenario["housing"]): string {
  switch (housing.status) {
    case "current":
      return "Rent is current.";
    case "grace":
      return "In a grace period on rent.";
    case "overdue":
      return "Rent is overdue.";
  }
}

function confidenceTone(confidence: Scenario["observations"][number]["confidence"]): BadgeTone {
  if (confidence === "documented") return "positive";
  if (confidence === "unconfirmed") return "warning";
  return "neutral";
}

export function TodayView({
  scenario,
  onNavigate,
  showInteractionPreview = false,
}: {
  scenario: Scenario;
  /** Explicit opt-in from the synthetic preview shell only. */
  showInteractionPreview?: boolean;
  onNavigate?: (tab: TodayNavTarget) => void;
}) {
  const { isDeveloper } = usePresentationMode();
  const location = placeById.get(scenario.locationId);
  const neighborhood = location?.parentId ? placeById.get(location.parentId) : undefined;
  const access = location ? accessSummary(location) : "";

  const urgent = scenario.commitments.filter((c) => URGENT_STATES.includes(c.state));
  const ongoing = scenario.commitments.filter((c) => c.state === "open");
  const availableWork = scenario.work.filter((w) => w.availability === "available");
  const gatedWork = scenario.work.filter((w) => w.availability === "unavailable");
  const recent = scenario.observations.slice(0, 2);
  const lockedCount =
    gatedWork.length + (scenario.restrictedRoute ? 1 : 0) + (scenario.undiscoveredPlaceId ? 1 : 0);

  const navTargets: { id: TodayNavTarget; label: string }[] = [
    { id: "streets", label: "Open The Streets" },
    { id: "life", label: "Open My Life" },
    { id: "story", label: "Open My Story" },
  ];

  return (
    <div className="space-y-5">
      {/* A. Where am I? */}
      <div className="noir-panel p-4">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted">
          <CalendarIcon className="h-4 w-4" />
          <span>Today</span>
          <span className="text-foreground">Day {scenario.day}</span>
        </div>
        <div className="mt-3 flex items-start gap-3">
          <span className="mt-0.5 text-primary">
            <MapPinIcon className="h-5 w-5" />
          </span>
          <div className="min-w-0">
            <div className="text-xs font-semibold uppercase tracking-wide text-muted">Current location</div>
            <div className="text-base font-semibold text-foreground">
              {location?.label ?? "Unknown location"}
              {isDeveloper && location ? (
                <span className="ml-1 font-mono text-[11px] font-normal text-muted">({location.id})</span>
              ) : null}
            </div>
            {location ? (
              <div className="text-xs text-muted">
                {location.type}
                {neighborhood ? ` · ${neighborhood.label}` : ""}
              </div>
            ) : null}
            {access ? <div className="mt-1 text-xs text-muted">{access}</div> : null}
          </div>
        </div>
      </div>

      {/* B. What do I have left today? */}
      <section aria-labelledby="resources-heading">
        <h2 id="resources-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          What I have left today
        </h2>
        <MoneySummary money={scenario.money} />
        <div className="mt-3">
          <BudgetMeters
            actionsUsed={scenario.budget.actionsUsed}
            actionsMax={scenario.budget.actionsMax}
            tuUsed={scenario.budget.tuUsed}
            tuMax={scenario.budget.tuMax}
          />
        </div>
        <p className="mt-1.5 text-xs text-muted">
          Actions are what you can get done today; travel units are how far you can move.
        </p>
      </section>

      {/* C. Where am I sleeping? */}
      <section aria-labelledby="housing-heading">
        <h2 id="housing-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Where I’m sleeping
        </h2>
        <div className="noir-panel p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="text-sm font-semibold text-foreground">Housing</span>
            <StateBadge tone={housingTone(scenario.housing.status)}>{scenario.housing.status}</StateBadge>
          </div>
          <p className="mt-1 text-sm text-foreground">{housingLine(scenario.housing)}</p>
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
            <span>
              Arrears: <span className="text-foreground">${scenario.housing.arrears}</span>
            </span>
            <span>
              Prepaid: <span className="text-foreground">${scenario.housing.prepaid}</span>
            </span>
            <span>
              Next due: <span className="text-foreground">Day {scenario.housing.nextDueDay}</span>{" "}
              <span className="text-muted">({relativeDays(scenario.day, scenario.housing.nextDueDay)})</span>
            </span>
          </div>
        </div>
      </section>

      {/* D. What needs attention? */}
      <section aria-labelledby="attention-heading">
        <h2 id="attention-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          What needs attention
        </h2>
        {urgent.length > 0 ? (
          <p className="mb-2 text-xs text-muted">
            <span className="font-semibold text-foreground">{urgent.length}</span>{" "}
            item{urgent.length === 1 ? " needs" : "s need"} attention today.
          </p>
        ) : null}
        {urgent.length === 0 ? (
          <div className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted">
            <InfoIcon className="h-4 w-4" />
            Nothing overdue today.
          </div>
        ) : (
          <ul className="space-y-2">
            {urgent.map((c) => (
              <li key={c.id} className="noir-panel flex items-start justify-between gap-3 border-l-2 border-l-danger p-3">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-foreground">{c.title}</div>
                  <div className="mt-0.5 text-xs text-muted">
                    {c.dueDay !== undefined ? `Due day ${c.dueDay} · ` : ""}
                    {isDeveloper ? c.detail : playerSafeText(c.detail)}
                  </div>
                </div>
                <StateBadge tone={commitmentTone(c.state)}>{c.state}</StateBadge>
              </li>
            ))}
          </ul>
        )}
        {ongoing.length > 0 ? (
          <ul className="mt-2 space-y-2">
            {ongoing.map((c) => (
              <li key={c.id} className="noir-panel flex items-start justify-between gap-3 p-3">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-foreground">{c.title}</div>
                  <div className="mt-0.5 text-xs text-muted">
                    {c.dueDay !== undefined ? `Due day ${c.dueDay} · ` : ""}
                    {isDeveloper ? c.detail : playerSafeText(c.detail)}
                  </div>
                </div>
                <StateBadge tone={commitmentTone(c.state)}>{c.state}</StateBadge>
              </li>
            ))}
          </ul>
        ) : null}
      </section>

      {/* E. What could I do? */}
      <section aria-labelledby="opportunities-heading">
        <h2 id="opportunities-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          What I could do
        </h2>

        {showInteractionPreview ? <>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">A consequential offer</h3>
        <div className="mb-4">
          <p className="mb-2 text-xs text-muted">Separate synthetic opening-day example; not an offer in the career shown above.</p>
          <OpportunityInteractionDemo />
        </div>
        </> : null}

        {availableWork.length > 0 ? (
          <>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Available work</h3>
            <p className="mb-2 text-xs text-muted">
              <span className="font-semibold text-foreground">{availableWork.length}</span>{" "}
              shift{availableWork.length === 1 ? "" : "s"} open today.
            </p>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {availableWork.map((w) => (
                <WorkCard key={w.id} work={w} />
              ))}
            </div>
          </>
        ) : (
          <p className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted">
            No work available right now.
          </p>
        )}

        <h3 className="mb-2 mt-4 text-xs font-semibold uppercase tracking-wide text-muted">Still out of reach</h3>
        {lockedCount > 0 ? (
          <p className="mb-2 text-xs text-muted">
            <span className="font-semibold text-foreground">{lockedCount}</span> thing
            {lockedCount === 1 ? "" : "s"} you can’t reach yet — here’s why.
          </p>
        ) : null}
        <ul className="space-y-2">
          {gatedWork.map((w) => (
            <li key={w.id}>
              <WorkCard work={w} />
            </li>
          ))}
          {scenario.restrictedRoute ? (
            <li className="flex items-start gap-2 rounded-lg border border-institutional/30 bg-institutional/10 px-3 py-2 text-xs text-institutional-strong">
              <LockIcon className="mt-0.5 h-4 w-4 shrink-0" />
              <span>
                <span className="font-semibold">{scenario.restrictedRoute.label}</span> —{" "}
                {scenario.restrictedRoute.reason}
              </span>
            </li>
          ) : null}
          {scenario.undiscoveredPlaceId ? (
            <li className="flex items-start gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-xs text-muted">
              <EyeOffIcon className="mt-0.5 h-4 w-4 shrink-0" />
              <span>
                <span className="font-semibold">Undiscovered location</span> — you’ve heard of somewhere, but you don’t
                know where it is yet.
              </span>
            </li>
          ) : null}
        </ul>
      </section>

      {/* F. What happened recently? */}
      <section aria-labelledby="recent-heading">
        <h2 id="recent-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Recently
        </h2>
        {recent.length === 0 ? (
          <p className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted">Nothing new.</p>
        ) : (
          <ul className="space-y-2">
            {recent.map((o) => (
              <li key={o.id} className="noir-panel p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold text-foreground">{o.incidentTitle}</span>
                  <StateBadge tone={confidenceTone(o.confidence)}>{o.confidence}</StateBadge>
                </div>
                <p className="mt-1 text-sm leading-relaxed text-muted">“{o.claim}”</p>
                <div className="mt-1 text-xs text-muted">
                  Source: {o.sourceName} · {o.limitation}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Jump links to the other existing views. */}
      <nav aria-label="Jump to another view" className="flex flex-wrap items-center gap-2 border-t border-border pt-3">
        <span className="text-xs uppercase tracking-wide text-muted">Jump to</span>
        {navTargets.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => onNavigate?.(t.id)}
            className="flex cursor-pointer items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-foreground transition-colors duration-200 hover:border-primary hover:text-primary"
          >
            {t.label}
            <ArrowRightIcon className="h-4 w-4" />
          </button>
        ))}
      </nav>
    </div>
  );
}
