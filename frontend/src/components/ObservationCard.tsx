import { useState } from "react";
import type { Observation } from "../types";
import { StateBadge } from "./StateBadge";
import { AlertIcon, ChevronDownIcon } from "./icons";

function confidenceTone(c: Observation["confidence"]) {
  if (c === "documented") return "positive" as const;
  if (c === "unconfirmed") return "warning" as const;
  return "neutral" as const;
}

function sourceKindLabel(k: Observation["sourceKind"]) {
  if (k === "contact") return "Contact";
  if (k === "institution") return "Institution";
  return "Own account";
}

export function ObservationCard({
  observation,
  conflicting = false,
}: {
  observation: Observation;
  conflicting?: boolean;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-border bg-surface">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={`obs-detail-${observation.id}`}
        className="flex w-full cursor-pointer items-start justify-between gap-3 p-3 text-left"
      >
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-foreground">{observation.incidentTitle}</span>
            <StateBadge tone={confidenceTone(observation.confidence)}>
              {observation.confidence}
            </StateBadge>
            {conflicting ? (
              <StateBadge tone="danger" icon={<AlertIcon />}>
                Conflicts with another source
              </StateBadge>
            ) : null}
          </div>
          <p className="mt-1 text-xs leading-relaxed text-muted-strong">{observation.claim}</p>
        </div>
        <ChevronDownIcon
          className={`mt-0.5 h-4 w-4 shrink-0 text-muted transition-transform duration-200 ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>

      {open ? (
        <div
          id={`obs-detail-${observation.id}`}
          className="border-t border-border px-3 py-2 text-xs text-muted"
        >
          <div className="flex flex-wrap gap-x-3 gap-y-1">
            <span>
              Source: <span className="text-muted-strong">{observation.sourceName}</span>
            </span>
            <span>
              Kind: <span className="text-muted-strong">{sourceKindLabel(observation.sourceKind)}</span>
            </span>
          </div>
          <p className="mt-1.5">
            <span className="font-semibold text-muted">Limitation:</span>{" "}
            <span>{observation.limitation}</span>
          </p>
        </div>
      ) : null}
    </div>
  );
}
