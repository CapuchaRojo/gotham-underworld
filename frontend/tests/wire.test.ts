import { test } from "node:test";
import assert from "node:assert/strict";
import {
  BRIDGE_PROTOCOL_VERSION,
  ENGINE_RELEASE,
  ERROR_BY_CODE,
  HOST_PROTOCOL_VERSION,
  parseHostAuthority,
  parseJsonBody,
  validateApiErrorEnvelope,
  validateBootstrapRequest,
  validateBootstrapResponse,
  validateCommandRequest,
  validateEngineEnvelope,
  validateHostErrorEnvelope,
  validateHostSession,
  validateOperationResponse,
  validateQuoteResponse,
  validateTravelQuoteRequest,
} from "../src/gameplay/wire";

type OkResult<T> = { ok: true; value: T };
type ErrResult = { ok: false; error: { code: string; message: string; path: string } };

function expectOk<T>(r: OkResult<T> | ErrResult): T {
  assert.equal(r.ok, true, "expected an ok result");
  if (!r.ok) throw new Error("expected an ok result");
  return r.value;
}

function expectErr(r: OkResult<unknown> | ErrResult): ErrResult["error"] {
  assert.equal(r.ok, false, "expected an error result");
  if (r.ok) throw new Error("expected an error result");
  return r.error;
}

const validSettleIn = {
  protocol_version: 1,
  career_id: "career.a1",
  lineage_id: "lineage.1",
  request_id: "req.0001",
  expected_revision: 0,
  command: "settle_in",
  arguments: {},
};

const validJourney = {
  protocol_version: 1,
  career_id: "career.a1",
  lineage_id: "lineage.1",
  request_id: "req.0002",
  expected_revision: 3,
  command: "journey",
  arguments: {
    destination: "goon.poi.p032",
    profile: "fastest",
    vehicle_id: "v1",
    max_tu: "18",
    max_cash: "40",
    return_to: "goon.poi.p031",
    quote_token: "qt.1",
    request_id: "req.inner.9",
  },
};

const validHostSession = {
  host_protocol_version: 1,
  bridge_protocol_version: 1,
  bundle_id: "bundle.1",
  manifest_sha256: "a".repeat(64),
  engine_release: ENGINE_RELEASE,
  instance_id: "inst.1",
  mode: "local_engine",
  session_lifetime: "process",
};

const validProjection = {
  day: 4,
  player: { cash: 40, heat: 0, custody: "free" },
  budgets: { daily_actions: 3, actions_remaining: 2, daily_travel_units: 18, travel_units_remaining: 12 },
  location: { id: "goon.poi.p031", label: "Caldwell Grocery" },
  systems: { navigation: "active", daily_life: "active", ordinary: "not_adopted", mobility: "pending" },
  housing: { status: "current", home_id: "goon.poi.p031", next_due_day: 7, arrears: 0, prepaid: 0 },
  contacts: [{ id: "npc.tess", name: "Tess Navarro", role: "Fellow goon", standing: 0 }],
  opportunities: [
    {
      id: "goon.choice.0.opening_shift",
      title: "Opening shift",
      situation: "The store needs a hand.",
      speaker: "Tess",
      open_day: 4,
      expires_day: 5,
      state: "open",
      command: "choose",
      options: [
        {
          id: "opt.work",
          label: "Work the shift",
          availability: "available",
          reason: null,
          action_cost: 1,
          tradeoff: "Earn cash, spend the day.",
          arguments: { choice_id: "goon.choice.0.opening_shift", option_id: "opt.work" },
        },
      ],
    },
  ],
  outcomes: [{ choice_id: "goon.choice.0", option_id: "opt.work", day: 3, feedback: "Worked." }],
  ordinary: { employment: 0, assistance: { status: "unused", amount: 0, due_day: null } },
};

const validReceipt = {
  request_id: "req.0001",
  revision: 3,
  command_sequence: 3,
  command: "wait",
  day: 4,
  status: "committed",
};

const validEnvelope = {
  protocol_version: 1,
  career_id: "career.a1",
  lineage_id: "lineage.1",
  revision: 3,
  allowed_commands: ["wait", "travel", "choose"],
  receipt: validReceipt,
  duplicate: false,
  state: validProjection,
};

// ---------------------------------------------------------------------------
// Binding constants
// ---------------------------------------------------------------------------

test("binding constants are never substituted", () => {
  assert.equal(ENGINE_RELEASE, "1a129e83be6629b7a27c2826626856ec7fae85f7");
  assert.notEqual(ENGINE_RELEASE, "f2e75dd959c5");
  assert.equal(HOST_PROTOCOL_VERSION, 1);
  assert.equal(BRIDGE_PROTOCOL_VERSION, 1);
});

test("error table carries the binding code→HTTP→action mapping", () => {
  assert.equal(ERROR_BY_CODE.BOOTSTRAP_DENIED.http, 401);
  assert.equal(ERROR_BY_CODE.BOOTSTRAP_DENIED.action, "clear_code_request_fresh");
  assert.equal(ERROR_BY_CODE.STALE_REVISION.http, 409);
  assert.equal(ERROR_BY_CODE.STALE_REVISION.action, "refresh_require_new_decision");
  assert.equal(ERROR_BY_CODE.REQUEST_TOO_LARGE.http, 413);
  assert.equal(ERROR_BY_CODE.INVALID_CONTENT_TYPE.http, 415);
  assert.equal(ERROR_BY_CODE.INTERNAL_ERROR.http, 500);
  assert.equal(ERROR_BY_CODE.INTERNAL_ERROR.action, "treat_outcome_uncertain_if_after_transmit");
});

test("host authority must be exactly http://127.0.0.1:<port>", () => {
  assert.deepEqual(parseHostAuthority("http://127.0.0.1:8787"), { scheme: "http", host: "127.0.0.1", port: 8787 });
  assert.equal(parseHostAuthority("http://localhost:8787"), null);
  assert.equal(parseHostAuthority("https://127.0.0.1:8787"), null);
  assert.equal(parseHostAuthority("http://127.0.0.1:0"), null);
  assert.equal(parseHostAuthority("http://127.0.0.1:99999"), null);
});

// ---------------------------------------------------------------------------
// Command request
// ---------------------------------------------------------------------------

test("command request accepts valid zero-arg and full-arg commands", () => {
  assert.deepEqual(expectOk(validateCommandRequest(validSettleIn)), validSettleIn);
  assert.deepEqual(expectOk(validateCommandRequest(validJourney)), validJourney);
});

test("command request preserves the distinct transport and inner mobility request_ids", () => {
  const journey = expectOk(validateCommandRequest(validJourney));
  assert.equal(journey.request_id, "req.0002");
  assert.equal(journey.arguments.request_id, "req.inner.9");
  assert.notEqual(journey.request_id, journey.arguments.request_id);
});

test("command request rejects missing fields", () => {
  const missing = { ...validSettleIn } as Record<string, unknown>;
  delete missing["request_id"];
  assert.equal(expectErr(validateCommandRequest(missing)).code, "missing_field");
});

test("command request rejects extra fields (no client-supplied economy)", () => {
  assert.equal(expectErr(validateCommandRequest({ ...validSettleIn, wage: 5 })).code, "unknown_field");
  assert.equal(
    expectErr(
      validateCommandRequest({
        ...validSettleIn,
        command: "choose",
        arguments: { choice_id: "c", option_id: "o", cash: "999" },
      }),
    ).code,
    "unknown_field",
  );
});

test("command request rejects non-integer or negative expected_revision", () => {
  assert.equal(expectErr(validateCommandRequest({ ...validSettleIn, expected_revision: 1.5 })).code, "invalid_integer");
  assert.equal(expectErr(validateCommandRequest({ ...validSettleIn, expected_revision: -1 })).code, "invalid_value");
});

test("command request rejects over-length argument values", () => {
  assert.equal(
    expectErr(
      validateCommandRequest({
        ...validJourney,
        arguments: { ...validJourney.arguments, destination: "x".repeat(257) },
      }),
    ).code,
    "argument_too_long",
  );
});

test("command request rejects invalid request_id", () => {
  assert.equal(expectErr(validateCommandRequest({ ...validSettleIn, request_id: "!bad" })).code, "invalid_id");
  assert.equal(expectErr(validateCommandRequest({ ...validSettleIn, request_id: "" })).code, "invalid_id");
});

test("command request rejects unknown commands", () => {
  assert.equal(
    expectErr(validateCommandRequest({ ...validSettleIn, command: "teleport", arguments: {} })).code,
    "unknown_command",
  );
});

test("command request enforces command-specific argument keys", () => {
  assert.equal(
    expectErr(validateCommandRequest({ ...validSettleIn, arguments: { anchor: "x" } })).code,
    "unknown_field",
  );
});

// ---------------------------------------------------------------------------
// Session / bootstrap
// ---------------------------------------------------------------------------

test("host session accepts valid shape and rejects deviations", () => {
  assert.deepEqual(expectOk(validateHostSession(validHostSession)), validHostSession);
  assert.equal(expectErr(validateHostSession({ ...validHostSession, extra: true })).code, "unknown_field");
  assert.equal(expectErr(validateHostSession({ ...validHostSession, mode: "remote" })).code, "invalid_value");
  assert.equal(
    expectErr(validateHostSession({ ...validHostSession, engine_release: "f2e75dd959c5" })).code,
    "invalid_value",
  );
  assert.equal(expectErr(validateHostSession({ ...validHostSession, host_protocol_version: 2 })).code, "invalid_value");
});

test("bootstrap response requires a 43-char base64url capability", () => {
  const valid = { ...validHostSession, capability: "A".repeat(43) };
  assert.deepEqual(expectOk(validateBootstrapResponse(valid)), valid);
  assert.equal(expectErr(validateBootstrapResponse({ ...validHostSession })).code, "missing_field");
  assert.equal(expectErr(validateBootstrapResponse({ ...validHostSession, capability: "short" })).code, "invalid_capability");
});

// ---------------------------------------------------------------------------
// Engine envelope / operation / quote / errors
// ---------------------------------------------------------------------------

test("engine envelope accepts a full valid projection", () => {
  assert.deepEqual(expectOk(validateEngineEnvelope(validEnvelope)), validEnvelope);
});

test("engine envelope allows a null receipt for state inspection", () => {
  const stateOnly = { ...validEnvelope, receipt: null };
  assert.equal(expectOk(validateEngineEnvelope(stateOnly)).receipt, null);
});

test("engine envelope rejects bad enum, non-integer revision, extra field, missing field", () => {
  assert.equal(
    expectErr(validateEngineEnvelope({ ...validEnvelope, receipt: { ...validReceipt, status: "pending" } })).code,
    "invalid_value",
  );
  assert.equal(expectErr(validateEngineEnvelope({ ...validEnvelope, revision: 1.5 })).code, "invalid_integer");
  assert.equal(expectErr(validateEngineEnvelope({ ...validEnvelope, world: {} })).code, "unknown_field");
  const noState = { ...validEnvelope } as Record<string, unknown>;
  delete noState["state"];
  assert.equal(expectErr(validateEngineEnvelope(noState)).code, "missing_field");
});

test("operation response validates committed and not_found statuses", () => {
  assert.deepEqual(expectOk(validateOperationResponse({ ...validEnvelope, operation_status: "committed" })), {
    ...validEnvelope,
    operation_status: "committed",
  });
  assert.deepEqual(expectOk(validateOperationResponse({ ...validEnvelope, receipt: null, operation_status: "not_found" })), {
    ...validEnvelope,
    receipt: null,
    operation_status: "not_found",
  });
  assert.equal(
    expectErr(validateOperationResponse({ ...validEnvelope, operation_status: "unknown" })).code,
    "invalid_value",
  );
});

test("quote response accepts legacy travel and mobility journey shapes", () => {
  const travel = {
    protocol_version: 1,
    career_id: "career.a1",
    lineage_id: "lineage.1",
    revision: 3,
    quote: {
      origin: "goon.poi.p031",
      destination: "goon.poi.p032",
      mode: "walk",
      cost: 2,
      affordable: true,
      remaining_tu: 16,
      return_cost: 2,
      return_fits_today: true,
      command: "travel",
      arguments: { destination: "goon.poi.p032", mode: "walk" },
    },
  };
  assert.deepEqual(expectOk(validateQuoteResponse(travel)), travel);

  const mobility = {
    ...travel,
    quote: {
      ...travel.quote,
      cost: null,
      return_cost: null,
      fare: 5,
      return_fare: null,
      can_return_today: true,
      return_uncertain: false,
      command: "journey",
    },
  };
  assert.deepEqual(expectOk(validateQuoteResponse(mobility)), mobility);
});

test("quote response rejects a bad command enum", () => {
  const bad = {
    protocol_version: 1,
    career_id: "career.a1",
    lineage_id: "lineage.1",
    revision: 3,
    quote: {
      origin: "a",
      destination: "b",
      mode: "walk",
      cost: 1,
      affordable: true,
      remaining_tu: 16,
      return_cost: 1,
      return_fits_today: true,
      command: "fly",
      arguments: {},
    },
  };
  assert.equal(expectErr(validateQuoteResponse(bad)).code, "invalid_value");
});

test("error envelopes validate API and host shapes", () => {
  const api = { protocol_version: 1, error: { code: "STALE_REVISION", message: "refresh" } };
  assert.deepEqual(expectOk(validateApiErrorEnvelope(api)), api);
  const host = { host_protocol_version: 1, error: { code: "BOOTSTRAP_DENIED", message: "denied" } };
  assert.deepEqual(expectOk(validateHostErrorEnvelope(host)), host);
  assert.equal(
    expectErr(validateApiErrorEnvelope({ protocol_version: 1, error: { code: 1, message: "x" } })).code,
    "invalid_type",
  );
});

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

test("bootstrap request validates exact shape", () => {
  const valid = { host_protocol_version: 1, bundle_id: "bundle.1", code: "c".repeat(43) };
  assert.deepEqual(expectOk(validateBootstrapRequest(valid)), valid);
  assert.equal(expectErr(validateBootstrapRequest({ ...valid, extra: 1 })).code, "unknown_field");
  assert.equal(
    expectErr(validateBootstrapRequest({ host_protocol_version: 2, bundle_id: "b", code: "c".repeat(43) })).code,
    "invalid_value",
  );
});

test("travel quote request validates exact shape", () => {
  const valid = { protocol_version: 1, destination: "goon.poi.p032", mode: "walk" };
  assert.deepEqual(expectOk(validateTravelQuoteRequest(valid)), valid);
});

// ---------------------------------------------------------------------------
// Body decoding (never assume JSON)
// ---------------------------------------------------------------------------

test("parseJsonBody decodes JSON and degrades gracefully on HTML/empty/malformed", () => {
  assert.deepEqual(expectOk(parseJsonBody('{"a":1}')), { a: 1 });
  assert.equal(expectErr(parseJsonBody("<!DOCTYPE html><html></html>")).code, "non_json_body");
  assert.equal(expectErr(parseJsonBody("")).code, "empty_body");
  assert.equal(expectErr(parseJsonBody("{not json")).code, "invalid_json");
});
