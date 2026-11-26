import { useState } from "react";
import type { ImplementedMode, RouteQuote, Scenario } from "../types";
import { PLACES, REGIONS, placeById } from "../atlas";
import { MONORAIL_PILOT, planRoute } from "../navigation";
import { usePresentationMode } from "../presentation";
import { PlaceCard } from "./PlaceCard";
import { BusIcon, ClockIcon, LockIcon, MapPinIcon, SearchIcon, ShipIcon, TrainIcon, WalkIcon } from "./icons";

const MODE_ICONS = { walk: WalkIcon, bus: BusIcon, rail: TrainIcon, ferry: ShipIcon } as const;
const MODE_LABELS: Record<ImplementedMode, string> = {
  walk: "Walk",
  bus: "Bus",
  rail: "Rail",
  ferry: "Ferry",
};

type KindFilter = "all" | "region" | "neighborhood" | "poi";

const REGION_BY_LABEL = new Map(REGIONS.map((r) => [r.label, r.id]));

function displayLabel(label: string, undiscovered: boolean): string {
  return undiscovered ? "undiscovered location" : label;
}

function legsSummary(q: RouteQuote): string {
  return q.legs.map((l) => `${l.label} (${MODE_LABELS[l.mode]})`).join(" → ");
}

export function StreetsView({ scenario }: { scenario: Scenario }) {
  const { isDeveloper } = usePresentationMode();
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState<KindFilter>("all");
  const [region, setRegion] = useState<string>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const origin = placeById.get(scenario.locationId);
  const selected = selectedId ? placeById.get(selectedId) : undefined;
  const undiscoveredId = scenario.undiscoveredPlaceId;
  const tuRemaining = scenario.budget.tuMax - scenario.budget.tuUsed;
  const regionValue =
    region === "all" ? "all" : isDeveloper ? region : placeById.get(region)?.label ?? "all";

  const q = query.trim().toLowerCase();
  const filtered = PLACES.filter((p) => {
    if (kind !== "all" && p.kind !== kind) return false;
    if (region !== "all" && p.regionId !== region) return false;
    const isUndiscovered = p.id === undiscoveredId;
    if (q) {
      const hay = isDeveloper
        ? `${displayLabel(p.label, isUndiscovered)} ${p.id} ${p.type}`.toLowerCase()
        : `${displayLabel(p.label, isUndiscovered)} ${p.type}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  const selectedUndiscovered = selected?.id === undiscoveredId;
  const isMonorailStation =
    selected?.id === MONORAIL_PILOT.fromId || selected?.id === MONORAIL_PILOT.toId;

  const filtersActive = query.trim() !== "" || kind !== "all" || region !== "all";
  const clearFilters = () => {
    setQuery("");
    setKind("all");
    setRegion("all");
  };

  return (
    <div className="space-y-4">
      {/* Current location */}
      {origin ? (
        <div className="noir-panel flex items-start gap-3 p-3">
          <span className="mt-0.5 text-primary">
            <MapPinIcon className="h-5 w-5" />
          </span>
          <div className="min-w-0">
            <div className="text-xs font-semibold uppercase tracking-wide text-muted">Current location</div>
            <div className="text-sm font-semibold text-foreground">
              {origin.label}{" "}
              {isDeveloper ? (
                <span className="font-mono text-[11px] font-normal text-muted">({origin.id})</span>
              ) : null}
            </div>
            <div className="text-xs text-muted">
              {origin.type} · {placeById.get(origin.parentId ?? "")?.label}
            </div>
          </div>
        </div>
      ) : null}

      {/* Restricted route callout (real authored authorized ferry) */}
      {scenario.restrictedRoute ? (
        <div className="flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-xs text-danger-strong">
          <LockIcon className="mt-0.5 h-4 w-4 shrink-0" />
          <span>
            <span className="font-semibold">Restricted route:</span> {scenario.restrictedRoute.label} —{" "}
            {scenario.restrictedRoute.reason}
          </span>
        </div>
      ) : null}

      {/* Filters */}
      <div className="space-y-2">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="relative flex-1">
            <span className="sr-only">Search places</span>
            <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                isDeveloper
                  ? "Search 176 places by name, type or identifier…"
                  : "Search 176 places by name or type…"
              }
              className="w-full rounded-lg border border-border bg-surface py-2 pl-9 pr-3 text-sm text-foreground placeholder:text-muted focus:border-primary"
            />
          </label>
          <label className="flex items-center gap-2 text-sm text-muted">
            <span className="text-xs uppercase tracking-wide">Region</span>
            <select
              value={regionValue}
              onChange={(e) => {
                const v = e.target.value;
                if (v === "all") setRegion("all");
                else setRegion(isDeveloper ? v : REGION_BY_LABEL.get(v) ?? "all");
              }}
              className="cursor-pointer rounded-lg border border-border bg-surface px-2 py-2 text-sm text-foreground"
            >
              <option value="all">All regions</option>
              {REGIONS.map((r) => (
                <option key={r.id} value={isDeveloper ? r.id : r.label}>
                  {r.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div role="group" aria-label="Filter by kind" className="flex flex-wrap gap-1">
          {(
            [
              ["all", "All"],
              ["region", "Regions"],
              ["neighborhood", "Neighborhoods"],
              ["poi", "Places"],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setKind(value)}
              aria-pressed={kind === value}
              className={`cursor-pointer rounded-md px-2.5 py-1 text-xs font-medium transition-colors duration-200 ${
                kind === value ? "bg-primary text-on-primary" : "bg-surface text-muted hover:text-foreground"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted">
          <span>
            <span className="font-semibold text-foreground">{filtered.length}</span> of {PLACES.length} places
            shown.
          </span>
          {filtersActive ? (
            <button
              type="button"
              onClick={clearFilters}
              className="cursor-pointer rounded-md border border-border bg-surface px-2 py-0.5 font-medium text-foreground transition-colors duration-150 hover:border-primary hover:text-primary active:scale-[0.97]"
            >
              Clear filters
            </button>
          ) : null}
        </div>

        {isDeveloper ? (
          <p className="text-[11px] text-muted">
            Profile codes: Economy (E) · Security (S) · Criminal (C) · Civilian (V) · Presence (N). Codes are
            authored; see README for the reconstruction note.
          </p>
        ) : null}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_1.1fr]">
        {/* List */}
        <div className="max-h-[70vh] space-y-2 overflow-y-auto pr-1">
          {filtered.length === 0 ? (
            <div className="noir-panel p-6 text-center text-sm text-muted">
              {query.trim() ? `No places match “${query}”. ` : "No places match the current filters. "}
              {isDeveloper ? "Try a different name, type, or identifier." : "Try a different name or type."}
              {filtersActive ? (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="mt-2 block w-full cursor-pointer rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-foreground transition-colors duration-150 hover:border-primary hover:text-primary active:scale-[0.99]"
                >
                  Clear filters and show all places
                </button>
              ) : null}
            </div>
          ) : (
            filtered.map((p) => (
              <PlaceCard
                key={p.id}
                place={p}
                current={p.id === scenario.locationId}
                undiscovered={p.id === undiscoveredId}
                selected={p.id === selectedId}
                onClick={() => setSelectedId(p.id)}
              />
            ))
          )}
        </div>

        {/* Detail + travel */}
        <div className="space-y-3">
          {selected ? (
            <>
              <PlaceCard
                place={selected}
                current={selected.id === scenario.locationId}
                undiscovered={selectedUndiscovered}
              />
              {selected.id !== scenario.locationId && !selectedUndiscovered && selected.kind !== "region" && origin ? (
                <div className="noir-panel p-3">
                  <h3 className="text-sm font-semibold text-foreground">Travel from {origin.label}</h3>
                  <p className="mb-2 text-xs text-muted">
                    Display only — modes and TU costs are authored; no travel is performed.
                  </p>
                  <ul className="space-y-1.5">
                    {(["walk", "bus", "rail", "ferry", "auto"] as const).map((m) => {
                      const quote = planRoute(scenario.locationId, selected.id, m, tuRemaining);
                      const Icon = m === "auto" ? ClockIcon : MODE_ICONS[m];
                      return (
                        <li
                          key={m}
                          className="flex items-center justify-between gap-2 rounded-md bg-surface-raised px-2.5 py-1.5 text-sm"
                        >
                          <span className="flex items-center gap-2 text-muted">
                            <Icon className="h-4 w-4" />
                            {m === "auto" ? "Fastest (auto)" : MODE_LABELS[m]}
                          </span>
                          {quote ? (
                            <span className="text-right">
                              <span className="font-semibold tabular-nums text-foreground">{quote.cost} TU</span>
                              {quote.returnCost !== null && m !== "auto" ? (
                                <span className="ml-1 text-xs text-muted">
                                  + {quote.returnCost} return = {quote.roundTripCost} TU
                                </span>
                              ) : null}
                            </span>
                          ) : (
                            <span className="text-xs text-muted">No route</span>
                          )}
                        </li>
                      );
                    })}
                  </ul>

                  {(() => {
                    const fastest = planRoute(scenario.locationId, selected.id, "auto", tuRemaining);
                    if (!fastest || fastest.legs.length === 0) return null;
                    return (
                      <div className="mt-2 border-t border-border pt-2 text-xs text-muted">
                        <span className="font-semibold text-muted">Route:</span> {legsSummary(fastest)}
                        <div className="mt-1">
                          {fastest.roundTripAffordable ? (
                            <span className="text-money-strong">Round trip fits today’s budget</span>
                          ) : fastest.affordable ? (
                            <span className="text-institutional-strong">
                              Outbound fits, but the return exceeds today’s TU
                            </span>
                          ) : (
                            <span className="text-danger-strong">Exceeds today’s remaining TU</span>
                          )}
                          <span className="text-muted">
                            {" · "}
                            {fastest.cost} + {fastest.returnCost ?? fastest.cost} = {fastest.roundTripCost} TU round
                            trip
                            {" · "}
                            {fastest.roundTripRemaining} TU left after
                          </span>
                        </div>
                      </div>
                    );
                  })()}

                  {isMonorailStation ? (
                    <div className="mt-2 rounded-md border border-institutional/30 bg-institutional/10 px-2.5 py-2 text-xs text-institutional-strong">
                      <span className="font-semibold">
                        {isDeveloper ? "Monorail pilot (M016-A):" : "Monorail pilot:"}
                      </span>{" "}
                      {MONORAIL_PILOT.fromLabel} ↔ {MONORAIL_PILOT.toLabel} — boarding {MONORAIL_PILOT.boardingTu} TU
                      + ride {MONORAIL_PILOT.rideTu} TU, fare ${MONORAIL_PILOT.fare}.
                    </div>
                  ) : null}
                </div>
              ) : null}
            </>
          ) : (
            <div className="noir-panel flex flex-col items-center justify-center p-8 text-center">
              <MapPinIcon className="h-8 w-8 text-muted" />
              <p className="mt-2 text-sm text-muted">
                {isDeveloper
                  ? "Select a place to see its authored identifier, access state, and real travel options."
                  : "Select a place to see its access and real travel options."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
