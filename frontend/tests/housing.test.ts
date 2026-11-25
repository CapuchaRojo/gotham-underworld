import "./dom";
import { createHousingHostClient } from "../src/gameplay/housingHost";
import { createInspectionHostClient } from "../src/gameplay/inspectionHost";
import { HOUSING_BUNDLE_ID, CLIENT_BUNDLE_ID } from "../src/gameplay/host";
import { ENGINE_RELEASE } from "../src/gameplay/wire";
import assert from "node:assert/strict";
import { test } from "node:test";
import { createHostClient } from "../src/gameplay/host";
import { canPayRoom, readHousing, readPaymentDetail } from "../src/gameplay/housing";
import { ROOM_PAYMENT_STATUSES, validateHousingOperation, validateHousingResponse } from "../src/gameplay/wire";
import type { EngineEnvelope, HousingOperationResponse, HousingResponse } from "../src/gameplay/wire";

const scope = { protocol_version: 1, career_id: "career-1", lineage_id: "lineage-1", revision: 7 } as const;
const balance = { cash: "900719925474099300000", arrears: 0, prepaid: 30, next_due_day: 10 };
const settlement = { day: 3, kind: "prepay", paid: 30, credit_applied: 0, balance_after: balance } as const;
const housing: HousingResponse = { ...scope, pay_room: "eligible", latest_settlement: settlement };
const receipt = { request_id: "pay-1", revision: 6, command_sequence: 12, command: "pay_room", day: 3, status: "committed" } as const;
const operation: HousingOperationResponse = { ...scope, receipt, settlements: [settlement] };
const state: EngineEnvelope = {
  ...scope, allowed_commands: ["pay_room"], receipt: null, duplicate: false,
  state: {
    day: 3,
    player: { cash: 20, heat: 0, custody: "free" },
    budgets: { daily_actions: 3, actions_remaining: 3, daily_travel_units: 18, travel_units_remaining: 18 },
    location: null, systems: { navigation: "active", daily_life: "active", ordinary: "not_adopted", mobility: "not_adopted" },
    housing: { status: "current", home_id: "home", next_due_day: 10, arrears: 0, prepaid: 30 },
    contacts: [], opportunities: [], outcomes: [],
  },
};

test("housing wire recognizes every authoritative status and preserves exact historical cash", () => {
  for (const pay_room of ROOM_PAYMENT_STATUSES) {
    const result = validateHousingResponse({ ...housing, pay_room });
    assert.equal(result.ok, true);
    if (result.ok) assert.equal(result.value.latest_settlement?.balance_after.cash, balance.cash);
  }
  assert.deepEqual(validateHousingResponse({ ...housing, latest_settlement: null }),
    { ok: true, value: { ...housing, latest_settlement: null } });
  assert.deepEqual(validateHousingOperation({ ...operation, settlements: [] }),
    { ok: true, value: { ...operation, settlements: [] } });
});

test("housing wire rejects missing/private fields, invalid scope and malformed settlement facts", () => {
  for (const invalid of [
    { ...housing, internal_events: [] }, { ...housing, pay_room: true }, { ...housing, pay_room: "outside" },
    { ...housing, protocol_version: 2 }, { ...housing, career_id: "career-1\n" },
    { ...housing, lineage_id: "lineage/key" }, { ...housing, revision: "7" }, { ...housing, revision: 2 ** 53 },
    { ...housing, latest_settlement: undefined },
  ]) assert.equal(validateHousingResponse(invalid).ok, false);
  for (const cash of [12, "+1", "-1", "01", "1.2", "1e3", " 1", "1\n", ""]) {
    assert.equal(validateHousingResponse({ ...housing, latest_settlement: {
      ...settlement, balance_after: { ...balance, cash },
    } }).ok, false);
  }
  for (const wrong of [
    { ...settlement, kind: "maintenance" }, { ...settlement, paid: "30" },
    { ...settlement, paid: 0 }, { ...settlement, day: -1 }, { ...settlement, credit_applied: 1 },
    { ...settlement, balance_after: { ...balance, private_id: "internal" } },
  ]) assert.equal(validateHousingOperation({ ...operation, settlements: [wrong] }).ok, false);
  assert.equal(validateHousingOperation({ ...operation, receipt: { ...receipt, revision: 8 } }).ok, false);
  assert.equal(validateHousingOperation({ ...operation, receipt: { ...receipt, private_frame: [] } }).ok, false);
  assert.equal(validateHousingOperation({ ...operation, receipt: { ...receipt, request_id: "pay-1\n" } }).ok, false);
});

test("housing reads are authenticated GETs and fail closed on path, authorization and response shape", async () => {
  const calls: Array<{ path: string; init?: RequestInit }> = [];
  const host = createHostClient({ fetchImpl: async (input, init) => {
    calls.push({ path: String(input), init });
    if (calls.length === 1) return Response.json(housing);
    if (calls.length === 2) return Response.json(operation);
    if (calls.length === 3) return Response.json({ protocol_version: 1, error: { code: "UNAUTHORIZED", message: "Authorization required." } }, { status: 401 });
    return Response.json({ ...housing, extra: true });
  } });
  assert.equal((await host.getHousing("cap")).ok, true);
  assert.equal((await host.getHousingOperation("cap", "pay-1")).ok, true);
  for (const invalid of ["../pay-1", "pay-1\n", "pay%2f1"]) {
    assert.equal((await host.getHousingOperation("cap", invalid)).ok, false);
  }
  assert.equal((await host.getHousing("cap")).ok, false);
  assert.equal((await host.getHousing("cap")).ok, false);
  assert.deepEqual(calls.map(({ path }) => path), [
    "/api/v1/housing", "/api/v1/housing/operations/pay-1", "/api/v1/housing", "/api/v1/housing",
  ]);
  for (const { init } of calls) assert.deepEqual(init, {
    method: "GET", headers: { Authorization: "Bearer cap" }, credentials: "omit", cache: "no-store", redirect: "error",
  });
});

test("current Housing requires matching career, lineage and revision, exact wallet, and contextual access", async () => {
  for (const delta of [{}, { revision: 8 }, { lineage_id: "other-lineage" }, { career_id: "other-career" }]) {
    const host = createHostClient({ fetchImpl: async (url) =>
      Response.json(url === "/api/v1/state" ? state : { ...housing, ...delta }) });
    const result = await readHousing(host, "cap");
    assert.equal(result.ok, Object.keys(delta).length === 0);
  }
  assert.equal(canPayRoom({ state, housing }), true);
  for (const pay_room of ROOM_PAYMENT_STATUSES.filter((status) => status !== "eligible")) {
    assert.equal(canPayRoom({ state, housing: { ...housing, pay_room } }), false);
  }
  assert.equal(canPayRoom({ state: { ...state, allowed_commands: [] }, housing }), false);
  assert.equal(canPayRoom({ state: { ...state, state: { ...state.state, player: { ...state.state.player, cash: 2 ** 53 } } }, housing }), false);
});

test("historical detail matches the original receipt independently of the current wallet", async () => {
  for (const [payload, expected] of [
    [operation, true], [{ ...operation, revision: 6 }, false], [{ ...operation, settlements: [] }, false],
    [{ ...operation, receipt: { ...receipt, request_id: "unrelated" } }, false],
    [{ ...operation, receipt: { ...receipt, command_sequence: 13 } }, false],
    [{ ...operation, lineage_id: "other" }, false],
    [{ ...operation, settlements: [{ ...settlement, kind: "due", paid: 0, credit_applied: 30 }] }, false],
  ] as const) {
    const host = createHostClient({ fetchImpl: async () => Response.json(payload) });
    const result = await readPaymentDetail(host, "cap", state, receipt);
    assert.equal(result.ok, expected);
    if (result.ok) assert.equal(result.value.balance_after.cash, balance.cash);
  }
});

const paymentRequest = {
  protocol_version: 1, career_id: scope.career_id, lineage_id: scope.lineage_id,
  expected_revision: 7, request_id: "pay-1", command: "pay_room", arguments: {},
} as const;

test("inspection refuses valid payments without making a network call", async () => {
  const host = createInspectionHostClient({ fetchImpl: async () => { throw new Error("inspection attempted POST"); } });
  const result = await host.postCommand("cap", paymentRequest);
  assert.equal(result.ok, false);
  if (!result.ok && result.failure.kind === "host_error") assert.equal(result.failure.code, "COMMAND_NOT_ALLOWED");
});

test("Housing verifies bootstrap against session and submits only an identity-bound rent intent", async () => {
  Object.defineProperty(globalThis, "sessionStorage", { value: window.sessionStorage, configurable: true });
  sessionStorage.clear();
  const session = {
    host_protocol_version: 1, bridge_protocol_version: 1, bundle_id: HOUSING_BUNDLE_ID,
    manifest_sha256: "a".repeat(64), engine_release: ENGINE_RELEASE, mode: "local_engine",
    instance_id: "host-one", session_lifetime: "process",
  };
  let mismatch = true;
  let supplied = housing;
  let posts = 0;
  const host = createHousingHostClient({
    fetchImpl: async (url, init) => {
      if (url === "/host/v1/bootstrap") {
        assert.equal(JSON.parse(String(init?.body)).bundle_id, HOUSING_BUNDLE_ID);
        return Response.json({ ...session, capability: "A".repeat(43) });
      }
      if (url === "/host/v1/session") return Response.json({ ...session, bundle_id: mismatch ? CLIENT_BUNDLE_ID : HOUSING_BUNDLE_ID });
      if (url === "/api/v1/state") return Response.json(state);
      if (url === "/api/v1/housing") return Response.json(supplied);
      assert.equal(url, "/api/v1/commands");
      assert.equal(JSON.parse(String(init?.body)).command, "pay_room");
      posts++;
      return Response.json(state);
    },
  });
  assert.equal((await host.bootstrap("A".repeat(43))).ok, false);
  mismatch = false;
  assert.equal((await host.bootstrap("A".repeat(43))).ok, true);
  assert.equal((await host.postCommand("cap", paymentRequest)).ok, false);
  assert.equal((await host.getState("cap")).ok, true);
  assert.equal((await host.getHousing("cap")).ok, true);
  supplied = { ...housing, revision: 6 };
  assert.equal((await host.getHousing("cap")).ok, false);
  assert.equal((await host.postCommand("cap", { ...paymentRequest, command: "wait" })).ok, false);
  assert.equal((await host.postCommand("cap", { ...paymentRequest, expected_revision: 6 })).ok, false);
  assert.equal((await host.postCommand("cap", paymentRequest)).ok, true);
  assert.equal(posts, 1);
});
