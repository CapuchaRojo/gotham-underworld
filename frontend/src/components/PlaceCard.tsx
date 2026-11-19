import type { Place } from "../types";
import { parentOf, placeById } from "../atlas";
import { accessState, accessSummary } from "../navigation";
import { usePresentationMode } from "../presentation";
import { StateBadge } from "./StateBadge";
import { BuildingIcon, EyeOffIcon, LockIcon, MapPinIcon } from "./icons";

function kindIcon(kind: Place["kind"]) {
  if (kind === "region") return <BuildingIcon className="h-4 w-4" />;
  return <MapPinIcon className="h-4 w-4" />;
}

function kindLabel(kind: Place["kind"]) {
  return kind === "region" ? "Region" : kind === "neighborhood" ? "Neighborhood" : "Place";
}

function breadcrumb(place: Place): string {
  const parts: string[] = [];
  const region = placeById.get(place.regionId);
  if (region) parts.push(region.label);
  if (place.kind === "poi") {
    const parent = parentOf(place.id);
    if (parent) parts.push(parent.label);
  } else if (place.kind === "neighborhood") {
    if (region) parts.push(region.label);
  }
  return [...new Set(parts)].join(" · ");
}

export function PlaceCard({
  place,
  current = false,
  undiscovered = false,
  selected = false,
  onClick,
}: {
  place: Place;
  current?: boolean;
  undiscovered?: boolean;
  selected?: boolean;
  onClick?: () => void;
}) {
  const { isDeveloper } = usePresentationMode();
  const state = accessState(place);
  const bc = breadcrumb(place);
  const Tag = onClick ? "button" : "div";

  return (
    <Tag
      type={onClick ? "button" : undefined}
      onClick={onClick}
      aria-pressed={onClick ? selected : undefined}
      className={`w-full text-left rounded-lg border p-3 transition-colors duration-200 ${
        onClick ? "cursor-pointer" : ""
      } ${
        selected
          ? "border-primary bg-surface-hover"
          : "border-border bg-surface hover:bg-surface-hover"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-muted">{kindIcon(place.kind)}</span>
          <div>
            <div className="text-sm font-semibold leading-tight text-foreground">
              {undiscovered ? "Undiscovered location" : place.label}
            </div>
            {isDeveloper ? (
              <div className="mt-0.5 font-mono text-[11px] text-muted">{place.id}</div>
            ) : null}
          </div>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          {current ? <StateBadge tone="warning">Current</StateBadge> : null}
          {undiscovered ? (
            <StateBadge tone="neutral" icon={<EyeOffIcon />}>
              Not discovered
            </StateBadge>
          ) : state === "restricted" ? (
            <StateBadge tone="danger" icon={<LockIcon />}>
              Restricted
            </StateBadge>
          ) : (
            <StateBadge tone="positive">Open</StateBadge>
          )}
        </div>
      </div>

      {!undiscovered && (
        <>
          <div className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted">
            <span>{kindLabel(place.kind)}</span>
            {place.type ? (
              <>
                <span aria-hidden="true">·</span>
                <span>{place.type}</span>
              </>
            ) : null}
            {bc ? (
              <>
                <span aria-hidden="true">·</span>
                <span>{bc}</span>
              </>
            ) : null}
          </div>

          <div className="mt-2 flex flex-wrap gap-1">
            {isDeveloper
              ? place.access.map((code) => (
                  <span
                    key={code}
                    className="rounded border border-border bg-background px-1.5 py-0.5 font-mono text-[10px] text-muted-strong"
                  >
                    {code}
                  </span>
                ))
              : null}
            <span className="px-1 py-0.5 text-[11px] text-muted">{accessSummary(place)}</span>
          </div>

          {isDeveloper ? (
            <dl className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 border-t border-border pt-2 text-[11px] sm:grid-cols-3">
              {([
                ["Economy", place.economy],
                ["Security", place.security],
                ["Criminal", place.criminal],
                ["Civilian", place.civilian],
                ["Presence", place.npcPool],
              ] as const).map(([k, v]) => (
                <div key={k} className="flex gap-1.5">
                  <dt className="text-muted">{k}</dt>
                  <dd className="text-muted-strong">{v.length ? v.join(" · ") : "—"}</dd>
                </div>
              ))}
            </dl>
          ) : null}
        </>
      )}
    </Tag>
  );
}
