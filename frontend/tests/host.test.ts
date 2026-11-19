import { test } from "node:test";
import assert from "node:assert/strict";
import {
  CAPABILITY_STORAGE_KEY,
  CLIENT_BUNDLE_ID,
  createCapabilityStore,
  createHostClient,
} from "../src/gameplay/host";
import type { HostFailure } from "../src/gameplay/host";
import { ENGINE_RELEASE, HOST_PROTOCOL_VERSION } from "../src/gameplay/wire";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const VALID_SESSION = {
  host_protocol_version: 1,
  bridge_protocol_version: 1,
  bundle_id: CLIENT_BUNDLE_ID,
  manifest_sha256: "a".repeat(64),
  engine_release: ENGINE_RELEASE,
  instance_id: "inst.1",
  mode: "local_engine",
  session_lifetime: "process",
};

const VALID_BOOTSTRAP = { ...VALID_SESSION, capability: "A".repeat(43) };

const VALID_ENVELOPE = {
  protocol_version: 1,
  career_id: "career.a1",
  lineage_id: "lineage.1",
  revision: 0,
  allowed_commands: ["wait", "settle_in"],
  receipt: null,
  duplicate: false,
  state: {
    day: 1,
    player: { cash: 40, heat: 0, custody: "free" },
    budgets: { daily_actions: 3, actions_remaining: 3, daily_travel_units: 18, travel_units_remaining: null },
    location: null,
    systems: { navigation: "not_adopted", daily_life: "not_adopted", ordinary: "not_adopted", mobility: "not_adopted" },
    housing: null,
    contacts: [],
    opportunities: [],
    outcomes: [],
  },
};

// ---------------------------------------------------------------------------
// Mock fetch
// ---------------------------------------------------------------------------

type FakeResponse = { ok: boolean; status: number; text: () => Promise<string> };

function json(status: number, body: unknown): FakeResponse {
  return { ok: status >= 200 && status < 300, status, text: async () => JSON.stringify(body) };
}

function makeFetch() {
  const calls: { url: string; init: RequestInit }[] = [];
  const queue: FakeResponse[] = [];
  const fetchImpl = async (url: string, init?: RequestInit): Promise<Response> => {
    calls.push({ url, init: init ?? {} });
    const next = queue.shift();
    if (!next) throw new Error("no mocked response queued");
    return next as unknown as Response;
  };
  return { calls, fetchImpl, enqueue: (r: FakeResponse) => queue.push(r) };
}

function failureOf<T>(r: { ok: true; value: T } | { ok: false; failure: HostFailure }): HostFailure {
  assert.equal(r.ok, false, "expected a failure result");
  if (r.ok) throw new Error("unreachable");
  return r.failure;
}

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------

test("bootstrap POSTs the exact binding body, headers, and fetch policy", async () => {
  const m = makeFetch();
  m.enqueue(json(200, VALID_BOOTSTRAP));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const result = await client.bootstrap("c".repeat(43));

  assert.equal(result.ok, true);
  assert.deepEqual(m.calls[0].url, "/host/v1/bootstrap");
  assert.equal(m.calls[0].init.method, "POST");
  assert.deepEqual(m.calls[0].init.headers, { "Content-Type": "application/json" });
  assert.equal(m.calls[0].init.body, JSON.stringify({
    host_protocol_version: HOST_PROTOCOL_VERSION,
    bundle_id: CLIENT_BUNDLE_ID,
    code: "c".repeat(43),
  }));
  assert.equal(m.calls[0].init.credentials, "omit");
  assert.equal(m.calls[0].init.cache, "no-store");
  assert.equal(m.calls[0].init.redirect, "error");
});

test("bootstrap surfaces BOOTSTRAP_DENIED as a host_error with its client action", async () => {
  const m = makeFetch();
  m.enqueue(json(401, { host_protocol_version: 1, error: { code: "BOOTSTRAP_DENIED", message: "denied" } }));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const failure = failureOf(await client.bootstrap("c".repeat(43)));
  assert.equal(failure.kind, "host_error");
  if (failure.kind === "host_error") {
    assert.equal(failure.code, "BOOTSTRAP_DENIED");
    assert.equal(failure.http, 401);
    assert.equal(failure.action, "clear_code_request_fresh");
  }
});

test("bootstrap surfaces BOOTSTRAP_RATE_LIMIT as a host_error", async () => {
  const m = makeFetch();
  m.enqueue(json(429, { host_protocol_version: 1, error: { code: "BOOTSTRAP_RATE_LIMIT", message: "slow down" } }));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const failure = failureOf(await client.bootstrap("c".repeat(43)));
  assert.equal(failure.kind, "host_error");
  if (failure.kind === "host_error") assert.equal(failure.action, "pause_pairing");
});

test("bootstrap degrades non-JSON error bodies to a transport failure (never assumes JSON)", async () => {
  const m = makeFetch();
  m.enqueue({ ok: false, status: 500, text: async () => "<!DOCTYPE html><html></html>" });
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const failure = failureOf(await client.bootstrap("c".repeat(43)));
  assert.equal(failure.kind, "transport");
});

test("bootstrap treats a network throw as a transport failure", async () => {
  const calls: string[] = [];
  const client = createHostClient({
    fetchImpl: async () => {
      calls.push("fetch");
      throw new Error("connection refused");
    },
  });

  const failure = failureOf(await client.bootstrap("c".repeat(43)));
  assert.equal(failure.kind, "transport");
  if (failure.kind === "transport") assert.match(failure.message, /connection refused/);
});

test("bootstrap fails closed when a 200 body violates the response schema", async () => {
  const m = makeFetch();
  // Missing capability → invalid bootstrap response.
  m.enqueue(json(200, VALID_SESSION));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const failure = failureOf(await client.bootstrap("c".repeat(43)));
  assert.equal(failure.kind, "validation");
});

test("bootstrap rejects an incompatible engine_release as a validation failure", async () => {
  const m = makeFetch();
  m.enqueue(json(200, { ...VALID_BOOTSTRAP, engine_release: "b".repeat(64) }));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const failure = failureOf(await client.bootstrap("c".repeat(43)));
  assert.equal(failure.kind, "validation");
  if (failure.kind === "validation") assert.equal(failure.code, "invalid_value");
});

// ---------------------------------------------------------------------------
// Authenticated session + state GET
// ---------------------------------------------------------------------------

test("getSession GETs with a Bearer capability and returns a validated HostSession", async () => {
  const m = makeFetch();
  m.enqueue(json(200, VALID_SESSION));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const result = await client.getSession("A".repeat(43));

  assert.equal(result.ok, true);
  assert.equal(m.calls[0].url, "/host/v1/session");
  assert.equal(m.calls[0].init.method, "GET");
  assert.deepEqual(m.calls[0].init.headers, { Authorization: `Bearer ${"A".repeat(43)}` });
});

test("getSession surfaces UNAUTHORIZED (stale capability → re-pair)", async () => {
  const m = makeFetch();
  m.enqueue(json(401, { host_protocol_version: 1, error: { code: "UNAUTHORIZED", message: "stale" } }));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const failure = failureOf(await client.getSession("A".repeat(43)));
  assert.equal(failure.kind, "host_error");
  if (failure.kind === "host_error") {
    assert.equal(failure.code, "UNAUTHORIZED");
    assert.equal(failure.action, "reauthorize_retain_pending");
  }
});

test("getState GETs /api/v1/state and returns a validated EngineEnvelope", async () => {
  const m = makeFetch();
  m.enqueue(json(200, VALID_ENVELOPE));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const result = await client.getState("A".repeat(43));

  assert.equal(result.ok, true);
  assert.equal(m.calls[0].url, "/api/v1/state");
  assert.equal(m.calls[0].init.method, "GET");
  if (result.ok) assert.equal(result.value.state.day, 1);
});

test("getState fails closed on a malformed projection", async () => {
  const m = makeFetch();
  m.enqueue(json(200, { ...VALID_ENVELOPE, state: { day: "not-a-number" } }));
  const client = createHostClient({ fetchImpl: m.fetchImpl });

  const failure = failureOf(await client.getState("A".repeat(43)));
  assert.equal(failure.kind, "validation");
});

// ---------------------------------------------------------------------------
// Capability store (memory + sessionStorage only)
// ---------------------------------------------------------------------------

function makeMemoryStorage(): Storage {
  const map = new Map<string, string>();
  return {
    getItem: (k) => (map.has(k) ? map.get(k)! : null),
    setItem: (k, v) => void map.set(k, String(v)),
    removeItem: (k) => void map.delete(k),
    clear: () => map.clear(),
    key: () => null,
    get length() {
      return map.size;
    },
  };
}

test("capability store persists to sessionStorage and round-trips through memory", () => {
  const storage = makeMemoryStorage();
  const store = createCapabilityStore(storage);
  const capability = "A".repeat(43);

  store.set(capability);
  assert.equal(store.get(), capability);
  assert.equal(storage.getItem(CAPABILITY_STORAGE_KEY), capability);
});

test("capability store reads back from sessionStorage (reload simulation) and clears", () => {
  const storage = makeMemoryStorage();
  storage.setItem(CAPABILITY_STORAGE_KEY, "B".repeat(43));
  const store = createCapabilityStore(storage);

  assert.equal(store.get(), "B".repeat(43));

  store.clear();
  assert.equal(store.get(), null);
  assert.equal(storage.getItem(CAPABILITY_STORAGE_KEY), null);
});

test("capability store keeps a memory copy when storage throws", () => {
  const throwing: Storage = {
    getItem: () => {
      throw new Error("denied");
    },
    setItem: () => {
      throw new Error("denied");
    },
    removeItem: () => {
      throw new Error("denied");
    },
    clear: () => {},
    key: () => null,
    length: 0,
  };
  const store = createCapabilityStore(throwing);
  store.set("C".repeat(43));
  assert.equal(store.get(), "C".repeat(43));
});
