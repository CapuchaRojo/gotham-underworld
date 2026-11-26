// REAL AUTHORED NAVIGATION — derived from the engine's `navigation.py` and
// `mobility/mobility_station_pilot_v1.json`. Encoded as static data (never executed
// as a live rule engine); this module only computes display values (route TU quotes,
// access states) from the authored graph. No travel is ever performed.

import type {
  AccessCode,
  AccessState,
  Edge,
  ImplementedMode,
  Place,
  RouteLeg,
  RouteQuote,
  TravelMode,
} from "./types";
import { NAMED_CORRIDORS, POIS, placeById } from "./atlas";
import { ACCESS_SPURS, LOCAL_CORRIDORS } from "./navigation_data";

export const DAILY_TU = 18;
export const DAILY_ACTIONS = 3;
export const MAX_RING = 8;

export const IMPLEMENTED_MODES: ImplementedMode[] = ["walk", "bus", "rail", "ferry"];
export const ALL_MODES: TravelMode[] = ["walk", "bus", "rail", "ferry", "boat", "car"];

// ---------------------------------------------------------------------------
// Access-state mapping
// ---------------------------------------------------------------------------
// Authoritative access gating, from `location_registry.py`:
//   RESTRICTED_ACCESS = frozenset(('HOME', 'WORK', 'VIS', 'SEC'))
// CARE / ENT / HELP / PUB are walk-in (frontage/reception only). Raw access
// codes are always shown verbatim next to this state so nothing is rewritten.
const RESTRICTED_ACCESS: AccessCode[] = ["HOME", "WORK", "VIS", "SEC"];

export const ACCESS_LABELS: Record<AccessCode, string> = {
  PUB: "Public — open entry",
  ENT: "Venue — open entry",
  HELP: "Support service — walk-in access",
  HOME: "Private residence — home permission required",
  WORK: "Workplace — work authorization required",
  CARE: "Care facility — walk-in frontage",
  SEC: "Secured facility — staff authorization required",
  VIS: "Visitation — authorized visitation required",
};

export function isRestrictedAccess(code: AccessCode): boolean {
  return RESTRICTED_ACCESS.includes(code);
}

export function accessState(place: Place): Extract<AccessState, "open" | "restricted"> {
  return place.access.some((a) => RESTRICTED_ACCESS.includes(a)) ? "restricted" : "open";
}

export function accessSummary(place: Place): string {
  return place.access.map((a) => ACCESS_LABELS[a]).join(" · ");
}

// ---------------------------------------------------------------------------
// Local street ring + POI access spurs
// ---------------------------------------------------------------------------
// Verbatim from `content/gotham_atlas_v1.json`, imported from `./navigation_data`
// so the authored mode/TU costs are preserved exactly — including the 12 local
// segments that carry rail. 46 local + 17 named = 63 corridors, plus 120 spurs.

function buildDirectedEdges(closedEdgeId?: string): Edge[] {
  const base = [...NAMED_CORRIDORS, ...LOCAL_CORRIDORS, ...ACCESS_SPURS];
  const out: Edge[] = [];
  const isClosed = (e: Edge) =>
    !!closedEdgeId && (e.id === closedEdgeId || e.id === `${closedEdgeId}.rev`);
  for (const e of base) {
    if (isClosed(e)) continue;
    out.push(e);
    if (e.bidirectional) {
      out.push({ ...e, id: `${e.id}.rev`, from: e.to, to: e.from });
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// Route search — faithful port of navigation.py `_search`
// ---------------------------------------------------------------------------
interface Node {
  cost: number;
  steps: number;
  place: string;
  mode: ImplementedMode;
}

interface PrevEntry {
  edge: Edge;
  mode: ImplementedMode;
  tu: number;
  from: string;
}

function runSearch(
  origin: string,
  destination: string,
  mode: ImplementedMode | "auto",
  closedEdgeId?: string,
): { best: Map<string, { cost: number; mode: ImplementedMode }>; prev: Map<string, PrevEntry> } {
  const graph = buildDirectedEdges(closedEdgeId);
  const rank: Node[] = [{ cost: 0, steps: 0, place: origin, mode: "walk" }];
  const best = new Map<string, { cost: number; mode: ImplementedMode }>([
    [origin, { cost: 0, mode: "walk" }],
  ]);
  const prev = new Map<string, PrevEntry>();

  while (rank.length) {
    rank.sort((a, b) => a.cost - b.cost);
    const cur = rank.shift() as Node;
    if (cur.place === destination) break;
    if (cur.steps > MAX_RING) continue;

    for (const e of graph) {
      if (e.from !== cur.place) continue;
      // Authorized edges (e.g. Blackgate Controlled Ferry) are only traversable while
      // walking and only from the journey origin. Access spurs carry access "location"
      // and are gated separately below, so only "authorized" is checked here.
      if (e.access === "authorized" && !(cur.mode === "walk" && cur.place === origin)) continue;
      // Access spurs are only usable at the start or end of a journey, never mid-route.
      // The gate applies to the spur's POI endpoint (its authored `to`), not the
      // directed edge's `to` — so leaving a POI origin via its reverse spur is allowed.
      if (e.kind === "access") {
        const spurPoiEnd = placeById.get(e.from)?.kind === "poi" ? e.from : e.to;
        if (spurPoiEnd !== origin && spurPoiEnd !== destination) continue;
      }
      if (e.kind === "corridor" && e.to === origin) continue;
      if (e.kind === "corridor" && best.has(e.to) && (best.get(e.to) as { cost: number }).cost < cur.cost) {
        continue;
      }

      const modes: ImplementedMode[] = mode === "auto" ? IMPLEMENTED_MODES : [mode];
      for (const m of modes) {
        if (e.modes[m] === undefined) continue;
        const edgeCost = e.modes[m] as number;
        // Boarding/transfer cost: +1 when switching onto a non-walk mode.
        const change = m !== "walk" && m !== cur.mode ? 1 : 0;
        const total = cur.cost + edgeCost + change;
        const candidate = e.to;
        const known = best.get(candidate);
        if (!known || total < known.cost) {
          best.set(candidate, { cost: total, mode: m });
          prev.set(candidate, { edge: e, mode: m, tu: edgeCost + change, from: cur.place });
          rank.push({ cost: total, steps: cur.steps + 1, place: candidate, mode: m });
        }
      }
    }
  }
  return { best, prev };
}

function reconstructLegs(
  origin: string,
  destination: string,
  prev: Map<string, PrevEntry>,
): RouteLeg[] {
  const legs: RouteLeg[] = [];
  let node = destination;
  let guard = 0;
  while (node !== origin && guard < MAX_RING + 2) {
    const p = prev.get(node);
    if (!p) break;
    legs.unshift({
      edgeId: p.edge.id.replace(/\.rev$/, ""),
      label: p.edge.label,
      from: p.from,
      to: node,
      mode: p.mode,
      tu: p.tu,
    });
    node = p.from;
    guard += 1;
  }
  return legs;
}

export function planRoute(
  origin: string,
  destination: string,
  mode: ImplementedMode | "auto",
  tuRemaining = DAILY_TU,
  closedEdgeId?: string,
): RouteQuote | null {
  if (origin === destination || !placeById.has(origin) || !placeById.has(destination)) {
    return null;
  }
  const out = runSearch(origin, destination, mode, closedEdgeId);
  const bestDest = out.best.get(destination);
  if (!bestDest) return null;

  const cost = Math.max(1, bestDest.cost);
  const legs = reconstructLegs(origin, destination, out.prev);

  const ret = runSearch(destination, origin, mode, closedEdgeId);
  const retBest = ret.best.get(origin);
  const returnCost = retBest ? Math.max(1, retBest.cost) : null;

  let modeChanges = 0;
  let lastMode: ImplementedMode | null = null;
  for (const leg of legs) {
    if (leg.mode !== "walk" && leg.mode !== lastMode) modeChanges += 1;
    lastMode = leg.mode;
  }

  // Combined outbound + return travel-budget calculation. The return leg must fit
  // within the TU that remains AFTER the outbound leg is paid for.
  const roundTripCost = returnCost !== null ? cost + returnCost : cost;
  const roundTripAffordable = returnCost !== null && roundTripCost <= tuRemaining;

  return {
    origin,
    destination,
    mode,
    cost,
    returnCost,
    roundTripCost,
    remainingTu: Math.max(0, tuRemaining - cost),
    roundTripRemaining: Math.max(0, tuRemaining - roundTripCost),
    affordable: cost <= tuRemaining,
    roundTripAffordable,
    legs,
    modeChanges,
  };
}

export function sameNeighborhoodPois(neighborhoodId: string): Place[] {
  return POIS.filter((p) => p.parentId === neighborhoodId);
}

export function incidentNeighborhoods(placeId: string): { from: Edge[]; to: Edge[] } {
  const from = [...NAMED_CORRIDORS, ...LOCAL_CORRIDORS].filter((e) => e.from === placeId);
  const to = [...NAMED_CORRIDORS, ...LOCAL_CORRIDORS].filter((e) => e.to === placeId);
  return { from, to };
}

export function corridorLabel(edgeId: string): string {
  const base = edgeId.replace(/\.rev$/, "");
  const found = [...NAMED_CORRIDORS, ...LOCAL_CORRIDORS].find((e) => e.id === base);
  return found ? found.label : base;
}

// ---------------------------------------------------------------------------
// Monorail pilot (M016-A) — authoritative overlay, content/mobility_station_pilot_v1.json
// ---------------------------------------------------------------------------
export const MONORAIL_PILOT = {
  overlayId: "goon.mobility.overlay.station_pilot.v1",
  overlayVersion: 1,
  rulesVersion: 1,
  baseAtlasVersion: 1,
  baseAtlasFingerprint: "14a38c5376989351d83bf90ed172c557a3dbf13c1323a115d2c2144f5136860a",
  lineId: "goon.mobility.line.highbridge_south_gate.v1",
  rideId: "goon.mobility.ride.highbridge_south_gate.v1",
  fromId: "goon.poi.p039",
  toId: "goon.poi.p071",
  fromLabel: "Highbridge Metro Stop",
  toLabel: "South Gate Subway Stop",
  stations: [
    { id: "goon.mobility.station.p039", placeId: "goon.poi.p039", platformId: "goon.mobility.node.p039.platform", gateId: "goon.mobility.gate.p039" },
    { id: "goon.mobility.station.p071", placeId: "goon.poi.p071", platformId: "goon.mobility.node.p071.platform", gateId: "goon.mobility.gate.p071" },
  ],
  boardingTu: 1,
  fare: 2,
  rideTu: 6,
  segments: [
    { edgeId: "goon.edge.local.r03.05", from: "goon.neighborhood.n17", to: "goon.neighborhood.n18" },
    { edgeId: "goon.edge.e06", from: "goon.neighborhood.n18", to: "goon.neighborhood.n23" },
    { edgeId: "goon.edge.local.r04.04", from: "goon.neighborhood.n23", to: "goon.neighborhood.n22" },
    { edgeId: "goon.edge.e08", from: "goon.neighborhood.n22", to: "goon.neighborhood.n30" },
  ],
} as const;
