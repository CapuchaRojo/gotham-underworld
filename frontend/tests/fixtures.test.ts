import { test } from "node:test";
import assert from "node:assert/strict";
import { SCENARIOS, SCENARIO_BY_ID } from "../src/fixtures";
import { placeById } from "../src/atlas";
import { planRoute } from "../src/navigation";

test("exactly three scenarios with stable identifiers", () => {
  assert.equal(SCENARIOS.length, 3);
  assert.deepEqual(
    SCENARIOS.map((s) => s.id),
    ["stable", "pressure", "uncertain"],
  );
  assert.equal(new Set(SCENARIOS.map((s) => s.label)).size, 3, "labels must be distinct");
  for (const s of SCENARIOS) {
    assert.equal(SCENARIO_BY_ID.get(s.id), s, `${s.id} must be resolvable by id`);
  }
});

test("scenario location references are all authored places", () => {
  for (const s of SCENARIOS) {
    assert.ok(placeById.has(s.locationId), `${s.id} locationId ${s.locationId}`);
    for (const w of s.work) {
      assert.ok(placeById.has(w.placeId), `${s.id} work ${w.id} -> ${w.placeId}`);
    }
    for (const r of s.institutions) {
      assert.ok(placeById.has(r.placeId), `${s.id} institution ${r.id} -> ${r.placeId}`);
    }
    if (s.undiscoveredPlaceId) {
      assert.ok(placeById.has(s.undiscoveredPlaceId), `${s.id} undiscoveredPlaceId`);
    }
    if (s.restrictedRoute) {
      assert.equal(s.restrictedRoute.edgeId, "goon.edge.e16", "restricted route must be the authorized ferry");
    }
  }
});

test("travel budget presentation uses DAILY_TU=18 / DAILY_ACTIONS=3", () => {
  for (const s of SCENARIOS) {
    assert.equal(s.budget.tuMax, 18, `${s.id} tuMax`);
    assert.equal(s.budget.actionsMax, 3, `${s.id} actionsMax`);
    assert.ok(s.budget.tuUsed >= 0 && s.budget.tuUsed <= s.budget.tuMax);
    assert.ok(s.budget.actionsUsed >= 0 && s.budget.actionsUsed <= s.budget.actionsMax);
  }
});

test("observation fields stay within the documented player-visible schema", () => {
  const allowed = new Set([
    "id",
    "incidentId",
    "incidentTitle",
    "claim",
    "sourceId",
    "sourceName",
    "sourceKind",
    "confidence",
    "limitation",
  ]);
  for (const s of SCENARIOS) {
    for (const o of s.observations) {
      for (const k of Object.keys(o)) {
        assert.ok(allowed.has(k), `unexpected observation field "${k}"`);
      }
      assert.ok(["documented", "unconfirmed", "unknown"].includes(o.confidence));
      assert.ok(["contact", "institution", "own"].includes(o.sourceKind));
    }
  }
});

test("no hidden institutional/engine knowledge leaks into fixture strings", () => {
  const forbidden = [
    "atlas_fingerprint",
    "world[",
    "career_state",
    "mobility_state",
    "institutional_response",
    "game_service",
    "navigation_version",
    "tu_used",
    "journey_sequence",
    "command_id",
    "heappush",
    "heapq",
    "profile_descriptions",
    "_search",
    "Deno.",
  ];
  const blob = JSON.stringify(SCENARIOS);
  for (const token of forbidden) {
    assert.ok(!blob.includes(token), `fixtures must not leak "${token}"`);
  }
});

test("route quoting does not mutate scenario state", () => {
  const before = JSON.stringify(SCENARIOS);
  planRoute("goon.poi.p031", "goon.poi.p032", "auto");
  planRoute("goon.poi.p031", "goon.poi.p058", "rail");
  planRoute("goon.neighborhood.n43", "goon.neighborhood.n46", "auto");
  assert.equal(JSON.stringify(SCENARIOS), before);
});
