import type { WorkCard as WorkCardType } from "../types";
import { placeById } from "../atlas";
import { usePresentationMode } from "../presentation";
import { StateBadge } from "./StateBadge";
import { CheckIcon, ClockIcon, XIcon } from "./icons";

export function WorkCard({ work }: { work: WorkCardType }) {
  const { isDeveloper } = usePresentationMode();
  const place = placeById.get(work.placeId);
  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold leading-tight text-foreground">{work.title}</div>
          <div className="mt-0.5 text-xs text-muted">
            {isDeveloper ? (place ? `${place.label} (${place.id})` : work.placeId) : place?.label}
          </div>
        </div>
        <div className="shrink-0">
          {work.availability === "available" ? (
            <StateBadge tone="positive" icon={<CheckIcon />}>
              Available
            </StateBadge>
          ) : (
            <StateBadge tone="danger" icon={<XIcon />}>
              Unavailable
            </StateBadge>
          )}
        </div>
      </div>

      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
        <span>
          Pay: <span className="text-foreground">{work.pay === null ? "—" : `$${work.pay}`}</span>
        </span>
        <span>
          Actions: <span className="text-foreground">{work.actions}</span>
        </span>
      </div>

      {work.availability === "unavailable" && work.reason ? (
        <div className="mt-2 flex items-start gap-1.5 rounded-md bg-danger/10 px-2.5 py-1.5 text-xs text-danger-strong">
          <ClockIcon className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>
            <span className="font-semibold">{work.reason}</span>
            {work.expiry ? <span className="text-danger-strong/80"> — {work.expiry}</span> : null}
          </span>
        </div>
      ) : null}

      <p className="mt-2 text-xs leading-relaxed text-muted">{work.note}</p>
    </div>
  );
}
