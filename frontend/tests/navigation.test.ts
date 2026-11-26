import { test } from "node:test";
import assert from "node:assert/strict";
import { placeById } from "../src/atlas";
import {
  DAILY_TU,
  DAILY_ACTIONS,
  IMPLEMENTED_MODES,
  MONORAIL_PILOT,
  accessState,
  isRestrictedAccess,
  planRoute,
} from "../src/navigation";
import { loadJson } from "./helpers";

interface JsonMobility {
  overlay_id: string;
  stations: { id: string; place_id: string; platform_id: string; gate_id: string }[];
  line: {
    id: string;
    ride_id: string;
    from_id: string;
    to_id: string;
    boarding_tu: number;
    fare: number;
    ride_tu: number;
    segments: { edge_id: string; from_id: string; to_id: string }[];
  };
}

const mobility = loadJson<JsonMobility>("../content/mobility_station_pilot_v1.json");

test("daily budget constants are stable", () => {
  assert.equal(DAILY_TU, 18);
  assert.equal(DAILY_ACTIONS, 3);
  assert.deepEqual(IMPLEMENTED_MODES, ["walk", "bus", "rail", "ferry"]);
});

test("access gating maps restricted codes correctly", () => {
  const restricted = ["HOME", "WORK", "VIS", "SEC"];
  const open = ["PUB", "ENT", "HELP", "CARE"];
  for (const code of restricted) assert.equal(isRestrictedAccess(code as never), true, code);
  for (const code of open) assert.equal(isRestrictedAccess(code as never), false, code);

  assert.equal(accessState(placeById.get("goon.poi.p031")!), "restricted"); // HOME
  assert.equal(accessState(placeById.get("goon.poi.p046")!), "open"); // ENT
  assert.equal(accessState(placeById.get("goon.poi.p112")!), "restricted"); // VIS
  assert.equal(accessState(placeById.get("goon.poi.p110")!), "open"); // CARE walk-in frontage
});

test("planRoute returns null for degenerate destinations", () => {
  assert.equal(planRoute("goon.poi.p031", "goon.poi.p031", "auto"), null);
  assert.equal(planRoute("goon.poi.p031", "not.a.place", "auto"), null);
});

test("planRoute quotes a real intra-neighborhood journey", () => {
  const q = planRoute("goon.poi.p031", "goon.poi.p032", "auto");
  assert.ok(q, "should quote a route");
  assert.ok(q.cost >= 1, "cost is clamped to at least 1 TU");
  assert.ok(q.legs.length >= 1);
  assert.equal(q.remainingTu, DAILY_TU - q.cost);
  assert.equal(q.affordable, q.cost <= DAILY_TU);
  for (const leg of q.legs) {
    assert.ok(placeById.has(leg.from), `leg from ${leg.from}`);
    assert.ok(placeById.has(leg.to), `leg to ${leg.to}`);
  }
});

test("combined outbound-and-return budget is calculated correctly", () => {
  // Full budget: the round trip fits.
  const full = planRoute("goon.poi.p031", "goon.poi.p032", "auto", DAILY_TU);
  assert.ok(full);
  assert.ok(full.returnCost !== null, "return leg should exist");
  assert.equal(full.roundTripCost, full.cost + (full.returnCost as number));
  assert.equal(full.roundTripAffordable, true);
  assert.equal(full.roundTripRemaining, DAILY_TU - full.roundTripCost);

  // Tight budget (only enough for the outbound leg): the return does NOT fit.
  const tight = planRoute("goon.poi.p031", "goon.poi.p032", "auto", full.cost);
  assert.ok(tight);
  assert.equal(tight.affordable, true);
  assert.equal(tight.roundTripAffordable, false);
  assert.equal(tight.roundTripRemaining, 0);
});

test("restricted destination (Blackgate) is unreachable from home", () => {
  // The only corridor into Blackgate Landing (n46) is e16, an authorized ferry
  // traversable only from the journey origin — never mid-route from home.
  const q = planRoute("goon.poi.p031", "goon.neighborhood.n46", "auto");
  assert.equal(q, null);
});

test("authorized ferry is traversable only from its own origin", () => {
  const q = planRoute("goon.neighborhood.n43", "goon.neighborhood.n46", "auto");
  assert.ok(q, "Blackgate should be reachable from Breakwater Village origin");
  assert.ok(q.legs.some((l) => l.edgeId === "goon.edge.e16"), "route must use e16");
});

test("monorail overlay matches the authored mobility JSON", () => {
  assert.equal(MONORAIL_PILOT.overlayId, mobility.overlay_id);
  assert.equal(MONORAIL_PILOT.lineId, mobility.line.id);
  assert.equal(MONORAIL_PILOT.rideId, mobility.line.ride_id);
  assert.equal(MONORAIL_PILOT.fromId, mobility.line.from_id);
  assert.equal(MONORAIL_PILOT.toId, mobility.line.to_id);
  assert.equal(MONORAIL_PILOT.boardingTu, mobility.line.boarding_tu);
  assert.equal(MONORAIL_PILOT.fare, mobility.line.fare);
  assert.equal(MONORAIL_PILOT.rideTu, mobility.line.ride_tu);

  assert.equal(MONORAIL_PILOT.stations.length, mobility.stations.length);
  assert.deepEqual(
    MONORAIL_PILOT.stations.map((s) => s.placeId),
    mobility.stations.map((s) => s.place_id),
  );
  assert.deepEqual(
    MONORAIL_PILOT.segments,
    mobility.line.segments.map((s) => ({ edgeId: s.edge_id, from: s.from_id, to: s.to_id })),
  );
});

test("monorail stations exist in the authored atlas", () => {
  for (const id of [MONORAIL_PILOT.fromId, MONORAIL_PILOT.toId]) {
    const p = placeById.get(id);
    assert.ok(p, `station ${id} must exist`);
    assert.ok(
      (p.type.includes("station") || p.type.includes("metro")),
      `station ${id} should be a station, got "${p.type}"`,
    );
  }
});

test("route quoting is pure — it never mutates authored atlas data", () => {
  const before = JSON.stringify(placeById.get("goon.poi.p031"));
  planRoute("goon.poi.p031", "goon.poi.p032", "auto");
  planRoute("goon.poi.p031", "goon.poi.p058", "rail");
  planRoute("goon.neighborhood.n43", "goon.neighborhood.n46", "auto");
  accessState(placeById.get("goon.poi.p112")!);
  assert.equal(JSON.stringify(placeById.get("goon.poi.p031")), before);
});
