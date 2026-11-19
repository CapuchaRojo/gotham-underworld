import type { CommitmentState, Scenario } from "../types";
import { placeById } from "../atlas";
import { playerSafeText, usePresentationMode } from "../presentation";
import { BudgetMeters } from "./BudgetMeters";
import { MoneySummary } from "./MoneySummary";
import { WorkCard } from "./WorkCard";
import { StateBadge } from "./StateBadge";
import { CalendarIcon, CheckIcon, ClockIcon, InfoIcon, AlertIcon, XIcon } from "./icons";

function commitmentTone(s: CommitmentState) {
  switch (s) {
    case "fulfilled":
      return "positive" as const;
    case "missed":
      return "danger" as const;
    case "pending":
      return "warning" as const;
    case "open":
      return "info" as const;
    case "refused":
      return "danger" as const;
    default:
      return "neutral" as const;
  }
}

function commitmentIcon(s: CommitmentState) {
  if (s === "fulfilled") return <CheckIcon />;
  if (s === "missed" || s === "refused") return <XIcon />;
  if (s === "pending") return <ClockIcon />;
  if (s === "open") return <InfoIcon />;
  return <InfoIcon />;
}

function housingTone(status: Scenario["housing"]["status"]) {
  if (status === "current") return "positive" as const;
  if (status === "overdue") return "danger" as const;
  return "warning" as const;
}

export function LifeView({ scenario }: { scenario: Scenario }) {
  const { isDeveloper } = usePresentationMode();
  const location = placeById.get(scenario.locationId);
  return (
    <div className="space-y-4">
      {/* Day + location */}
      <div className="noir-panel flex flex-wrap items-center justify-between gap-3 p-3">
        <div className="flex items-center gap-2 text-sm">
          <CalendarIcon className="h-4 w-4 text-muted" />
          <span className="text-muted">Day</span>
          <span className="font-semibold text-foreground">{scenario.day}</span>
        </div>
        <div className="text-sm text-muted">
          Location:{" "}
          <span className="text-foreground">
            {location?.label}{" "}
            {isDeveloper ? (
              <span className="font-mono text-[11px] text-muted">({scenario.locationId})</span>
            ) : null}
          </span>
        </div>
      </div>

      <MoneySummary money={scenario.money} />
      <BudgetMeters
        actionsUsed={scenario.budget.actionsUsed}
        actionsMax={scenario.budget.actionsMax}
        tuUsed={scenario.budget.tuUsed}
        tuMax={scenario.budget.tuMax}
      />

      {/* Housing + adoption */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="noir-panel p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-muted">Housing</span>
            <StateBadge tone={housingTone(scenario.housing.status)}>{scenario.housing.status}</StateBadge>
          </div>
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
            <span>
              Arrears: <span className="text-foreground">${scenario.housing.arrears}</span>
            </span>
            <span>
              Prepaid: <span className="text-foreground">${scenario.housing.prepaid}</span>
            </span>
            <span>
              Next due: <span className="text-foreground">Day {scenario.housing.nextDueDay}</span>
            </span>
          </div>
        </div>

        <div className="noir-panel p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-muted">Adoption terms</span>
            <StateBadge tone={scenario.adoption === "active" ? "positive" : "warning"}>
              {scenario.adoption}
            </StateBadge>
          </div>
          <p className="mt-2 text-xs text-muted">
            {scenario.adoption === "pending"
              ? "Pending adoption stays inactive when viewed — nothing activates on view."
              : scenario.adoption === "active"
                ? "Terms are active for this fixture."
                : "Terms are not adopted in this fixture."}
          </p>
        </div>
      </div>

      {/* Work */}
      <section aria-labelledby="work-heading">
        <h2 id="work-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Work
        </h2>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {scenario.work.map((w) => (
            <WorkCard key={w.id} work={w} />
          ))}
        </div>
      </section>

      {/* Commitments */}
      <section aria-labelledby="commitments-heading">
        <h2 id="commitments-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Commitments
        </h2>
        <ul className="space-y-2">
          {scenario.commitments.map((c) => (
            <li key={c.id} className="noir-panel flex items-start justify-between gap-3 p-3">
              <div className="min-w-0">
                <div className="text-sm font-semibold text-foreground">{c.title}</div>
                <div className="mt-0.5 text-xs text-muted">
                  {c.dueDay !== undefined ? `Due day ${c.dueDay} · ` : ""}
                  {isDeveloper ? c.detail : playerSafeText(c.detail)}
                </div>
              </div>
              <div className="shrink-0">
                <StateBadge tone={commitmentTone(c.state)} icon={commitmentIcon(c.state)}>
                  {c.state}
                </StateBadge>
              </div>
            </li>
          ))}
        </ul>
      </section>

      {/* Support advance status is surfaced in the "Owed" total above. */}
      <p className="flex items-center gap-1.5 text-[11px] text-muted">
        <AlertIcon className="h-3.5 w-3.5" />
        Support advance is shown in “Owed”, separate from cash and never mixed into the balance.
      </p>
    </div>
  );
}
