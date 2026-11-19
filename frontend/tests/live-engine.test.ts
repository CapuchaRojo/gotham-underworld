import "./dom";
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { createElement, StrictMode } from "react";
import { act, cleanup, render } from "@testing-library/react";
import {
  LIVE_CONNECTION_LABELS,
  LIVE_CONNECTION_STATES,
  isFailClosed,
} from "../src/gameplay/connection";
import type { LiveConnectionState } from "../src/gameplay/connection";
import {
  createLiveEngineClient,
  liveEngineStatus,
  reconcileHostSession,
} from "../src/gameplay/liveEngine";
import type { LiveEngineContextValue } from "../src/gameplay/LiveEngineProvider";
import { LiveEngineProvider, useLiveEngine } from "../src/gameplay/LiveEngineProvider";
import type { GameplayContextValue } from "../src/gameplay/GameplayProvider";
import { useGameplay } from "../src/gameplay/GameplayProvider";
import { EngineProvider } from "../src/gameplay/EngineProvider";
import { CLIENT_BUNDLE_ID, CAPABILITY_STORAGE_KEY } from "../src/gameplay/host";
import type { HostClient, HostResult } from "../src/gameplay/host";
import { ENGINE_RELEASE } from "../src/gameplay/wire";
import type { BootstrapResponse, EngineEnvelope, HostSession } from "../src/gameplay/wire";

afterEach(() => {
  cleanup();
  try {
    window.sessionStorage.removeItem(CAPABILITY_STORAGE_KEY);
  } catch {
    // Ignore.
  }
});

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

// Shape-only reconciliation fixture (bundle matching is a provider concern).
const VALID_SESSION = {
  host_protocol_version: 1,
  bridge_protocol_version: 1,
  bundle_id: "bundle.1",
  manifest_sha256: "a".repeat(64),
  engine_release: ENGINE_RELEASE,
  instance_id: "inst.1",
  mode: "local_engine",
  session_lifetime: "process",
};

// The same session carrying THIS client's bundle (for the pairing lifecycle).
const CLIENT_SESSION: HostSession = { ...VALID_SESSION, bundle_id: CLIENT_BUNDLE_ID };
const CLIENT_BOOTSTRAP: BootstrapResponse = { ...CLIENT_SESSION, capability: "A".repeat(43) };

const VALID_ENVELOPE: EngineEnvelope = {
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

// Missing required fields → schema violation (malformed, not a version mismatch).
const MALFORMED_SESSION = { host_protocol_version: 1 };

// Valid shape but the wrong engine release → a real-but-incompatible host.
const INCOMPATIBLE_SESSION = { ...VALID_SESSION, engine_release: "b".repeat(64) };

const FAIL_CLOSED_STATES: LiveConnectionState[] = [
  "starting",
  "pairing_required",
  "pairing_in_progress",
  "rate_limited",
  "incompatible",
  "recovering",
  "disconnected",
  "outcome_uncertain",
];

// ---------------------------------------------------------------------------
// State model
// ---------------------------------------------------------------------------

test("live connection state enum is exactly the nine defined states", () => {
  assert.deepEqual(LIVE_CONNECTION_STATES, [
    "starting",
    "pairing_required",
    "pairing_in_progress",
    "rate_limited",
    "incompatible",
    "recovering",
    "ready",
    "disconnected",
    "outcome_uncertain",
  ]);
  assert.equal(LIVE_CONNECTION_LABELS.starting, "Starting");
  assert.equal(LIVE_CONNECTION_LABELS.pairing_required, "Pairing required");
  assert.equal(LIVE_CONNECTION_LABELS.pairing_in_progress, "Pairing in progress");
  assert.equal(LIVE_CONNECTION_LABELS.rate_limited, "Rate limited");
  assert.equal(LIVE_CONNECTION_LABELS.incompatible, "Incompatible");
  assert.equal(LIVE_CONNECTION_LABELS.recovering, "Recovering");
  assert.equal(LIVE_CONNECTION_LABELS.ready, "Ready");
  assert.equal(LIVE_CONNECTION_LABELS.disconnected, "Disconnected");
  assert.equal(LIVE_CONNECTION_LABELS.outcome_uncertain, "Outcome uncertain");
});

test("only `ready` is a trusted live state — everything else fails closed", () => {
  for (const state of LIVE_CONNECTION_STATES) {
    assert.equal(isFailClosed(state), state !== "ready", state);
  }
});

// ---------------------------------------------------------------------------
// Host-session reconciliation (the pure validation seam)
// ---------------------------------------------------------------------------

test("reconcileHostSession promotes a valid session and rejects malformed/incompatible input", () => {
  const ok = reconcileHostSession(VALID_SESSION);
  assert.equal(ok.ok, true);
  if (ok.ok) {
    assert.equal(ok.connectionState, "ready");
    assert.equal(ok.session.engine_release, ENGINE_RELEASE);
  }

  const malformedObject = reconcileHostSession(MALFORMED_SESSION);
  assert.equal(malformedObject.ok, false);
  if (!malformedObject.ok) {
    assert.equal(malformedObject.connectionState, "incompatible");
    assert.equal(malformedObject.failure, "malformed");
  }

  const nonObject = reconcileHostSession(null);
  assert.equal(nonObject.ok, false);
  if (!nonObject.ok) {
    assert.equal(nonObject.failure, "malformed");
  }

  const incompatible = reconcileHostSession(INCOMPATIBLE_SESSION);
  assert.equal(incompatible.ok, false);
  if (!incompatible.ok) {
    assert.equal(incompatible.connectionState, "incompatible");
    assert.equal(incompatible.failure, "incompatible");
  }

  // Protocol/version binding mismatches are incompatibility, not schema defects.
  const protocolMismatch = reconcileHostSession({ ...VALID_SESSION, host_protocol_version: 2 });
  assert.equal(protocolMismatch.ok, false);
  if (!protocolMismatch.ok) assert.equal(protocolMismatch.failure, "incompatible");
});

// ---------------------------------------------------------------------------
// Fail-closed client behavior (no synthetic career state, no gameplay)
// ---------------------------------------------------------------------------

test("live client fails closed in every non-ready state and never serves state", async () => {
  for (const state of FAIL_CLOSED_STATES) {
    const client = createLiveEngineClient({ getConnectionState: () => state });

    assert.equal(client.connectionState, state);
    assert.equal(client.getPlayerState(), null, `${state}: must not render career state`);

    const authorize = await client.authorizeTravel("goon.poi.p032");
    assert.equal(authorize.ok, false, `${state}: must not authorize travel`);
    if (!authorize.ok) {
      assert.equal(
        authorize.code,
        state === "incompatible" ? "session_incompatible" : "not_authorized",
        `${state}: authorizeTravel error code`,
      );
    }

    const execute = await client.executeAction({ choiceId: "work.store-repair", kind: "work" });
    assert.equal(execute.ok, false, `${state}: must not authorize gameplay`);
    if (!execute.ok) {
      assert.equal(
        execute.code,
        state === "incompatible" ? "session_incompatible" : "engine_unavailable",
        `${state}: executeAction error code`,
      );
    }

    assert.equal((await client.getRouteQuote("a", "b")).ok, false, state);
    assert.equal((await client.getEligibility("work.store-repair")).ok, false, state);
    assert.equal((await client.recover("req.1")).ok, false, state);
    assert.equal((await client.restore()).ok, false, state);
  }
});

test("live client never synthesizes career state even when ready", () => {
  const client = createLiveEngineClient({ getConnectionState: () => "ready" });
  assert.equal(client.getPlayerState(), null);
});

test("live status reports kind `live` and local-engine context for every state", () => {
  for (const state of LIVE_CONNECTION_STATES) {
    const status = liveEngineStatus(state);
    assert.equal(status.kind, "live", state);
    assert.equal(status.connectionState, state, state);
    assert.equal(status.contextLabel, "Local engine", state);
    assert.equal(status.label, LIVE_CONNECTION_LABELS[state], state);
  }
});

// ---------------------------------------------------------------------------
// Provider behavior
// ---------------------------------------------------------------------------

function makeLiveProbe(slot: { value?: LiveEngineContextValue }) {
  return function LiveProbe() {
    slot.value = useLiveEngine();
    return null;
  };
}

function makePreviewProbe(slot: { value?: GameplayContextValue }) {
  return function PreviewProbe() {
    slot.value = useGameplay();
    return null;
  };
}

function fakeHost(impl: Partial<HostClient>): HostClient {
  return {
    bootstrap: impl.bootstrap ?? (async () => {
      throw new Error("unexpected bootstrap call");
    }),
    getSession: impl.getSession ?? (async () => {
      throw new Error("unexpected getSession call");
    }),
    getState: impl.getState ?? (async () => {
      throw new Error("unexpected getState call");
    }),
  };
}

function ok<T>(value: T): HostResult<T> {
  return { ok: true, value };
}

const BOOTSTRAP_DENIED: HostResult<never> = {
  ok: false,
  failure: {
    kind: "host_error",
    code: "BOOTSTRAP_DENIED",
    http: 401,
    message: "denied",
    action: "clear_code_request_fresh",
  },
};

function renderLive(slot: { value?: LiveEngineContextValue }, host: HostClient) {
  return render(
    createElement(LiveEngineProvider, {
      hostClient: host,
      children: createElement(makeLiveProbe(slot)),
    }),
  );
}

test("LiveEngineProvider starts fail-closed and never transitions on mount (StrictMode-safe)", () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const Probe = makeLiveProbe(slot);

  render(
    createElement(
      StrictMode,
      null,
      createElement(LiveEngineProvider, { children: createElement(Probe) }),
    ),
  );

  assert.equal(slot.value!.mode, "live");
  assert.equal(slot.value!.connectionState, "starting");
  assert.equal(slot.value!.status.label, "Starting");
  assert.equal(slot.value!.status.kind, "live");
  assert.equal(slot.value!.playerState, null);
  assert.equal(slot.value!.session, null);
  assert.equal(slot.value!.engineState, null);
  assert.equal(slot.value!.lastSessionFailure, null);
  assert.equal(slot.value!.lastError, null);
});

test("pair() bootstraps, stores the capability, reads state, and reaches ready", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ok(CLIENT_BOOTSTRAP),
    getState: async () => ok(VALID_ENVELOPE),
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.equal(slot.value!.connectionState, "ready");
  assert.equal(slot.value!.session!.bundle_id, CLIENT_BUNDLE_ID);
  assert.equal(slot.value!.engineState!.state.day, 1);
  // Ready ≠ playable: no projection→gameplay mapping yet, so state stays null
  // and mutations stay blocked. There is NO fallback to authored fixtures.
  assert.equal(slot.value!.playerState, null);
  assert.equal((await slot.value!.client.executeAction({ choiceId: "x", kind: "work" })).ok, false);
  assert.equal((await slot.value!.client.authorizeTravel("goon.poi.p032")).ok, false);
  assert.equal(window.sessionStorage.getItem(CAPABILITY_STORAGE_KEY), "A".repeat(43));
});

test("pair() with a rejected code returns to pairing_required", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({ bootstrap: async () => BOOTSTRAP_DENIED });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.equal(slot.value!.connectionState, "pairing_required");
  assert.equal(slot.value!.session, null);
  assert.equal(slot.value!.engineState, null);
  assert.equal(slot.value!.lastError, "denied");
});

test("pair() with a rate limit surfaces rate_limited", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ({
      ok: false,
      failure: {
        kind: "host_error",
        code: "BOOTSTRAP_RATE_LIMIT",
        http: 429,
        message: "slow down",
        action: "pause_pairing",
      },
    }),
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.equal(slot.value!.connectionState, "rate_limited");
});

test("pair() with an incompatible host blocks the client", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ({
      ok: false,
      failure: {
        kind: "host_error",
        code: "HOST_INCOMPATIBLE",
        http: 409,
        message: "engine too old",
        action: "block_incompatible_client",
      },
    }),
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.equal(slot.value!.connectionState, "incompatible");
  assert.equal(slot.value!.lastSessionFailure!.failure, "incompatible");
});

test("pair() labels a schema-defective bootstrap as malformed and fails closed", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  // A 200 body missing `capability` reaches the validator and fails schema.
  const host = fakeHost({
    bootstrap: async () => ({
      ok: false,
      failure: { kind: "validation", code: "missing_field", message: "capability required", path: "$" },
    }),
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.equal(slot.value!.connectionState, "incompatible");
  assert.equal(slot.value!.lastSessionFailure!.failure, "malformed");
});

test("pair() labels a binding mismatch (wrong engine_release) as incompatible", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ({
      ok: false,
      failure: { kind: "validation", code: "invalid_value", message: "engine_release mismatch", path: "$" },
    }),
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.equal(slot.value!.connectionState, "incompatible");
  assert.equal(slot.value!.lastSessionFailure!.failure, "incompatible");
});

test("pair() rejects a host serving a different bundle", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  let stateRead = false;
  const host = fakeHost({
    bootstrap: async () => ok({ ...CLIENT_BOOTSTRAP, bundle_id: "other.bundle" }),
    getState: async () => {
      stateRead = true;
      return ok(VALID_ENVELOPE);
    },
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.equal(slot.value!.connectionState, "incompatible");
  assert.equal(slot.value!.lastSessionFailure!.failure, "incompatible");
  // Bundle attestation fails BEFORE any state read.
  assert.equal(stateRead, false);
});

test("pair() is single-flight — a concurrent second call does not re-bootstrap", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  let bootstraps = 0;
  const host = fakeHost({
    bootstrap: async () => {
      bootstraps += 1;
      return ok(CLIENT_BOOTSTRAP);
    },
    getState: async () => ok(VALID_ENVELOPE),
  });
  renderLive(slot, host);

  await act(async () => {
    const first = slot.value!.pair("c".repeat(43));
    const second = slot.value!.pair("c".repeat(43));
    await Promise.all([first, second]);
  });

  assert.equal(bootstraps, 1);
  assert.equal(slot.value!.connectionState, "ready");
});

test("revalidate() with no capability returns to pairing_required", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  renderLive(slot, fakeHost({}));

  await act(async () => {
    await slot.value!.revalidate();
  });

  assert.equal(slot.value!.connectionState, "pairing_required");
});

test("revalidate() re-validates a stored capability and reaches ready", async () => {
  window.sessionStorage.setItem(CAPABILITY_STORAGE_KEY, "A".repeat(43));
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    getSession: async () => ok(CLIENT_SESSION),
    getState: async () => ok(VALID_ENVELOPE),
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.revalidate();
  });

  assert.equal(slot.value!.connectionState, "ready");
  assert.equal(slot.value!.session!.instance_id, "inst.1");
  assert.equal(slot.value!.engineState!.state.day, 1);
});

test("revalidate() discards a rotated capability on UNAUTHORIZED and re-pairs", async () => {
  window.sessionStorage.setItem(CAPABILITY_STORAGE_KEY, "A".repeat(43));
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    getSession: async () => ({
      ok: false,
      failure: {
        kind: "host_error",
        code: "UNAUTHORIZED",
        http: 401,
        message: "rotated",
        action: "reauthorize_retain_pending",
      },
    }),
  });
  renderLive(slot, host);

  await act(async () => {
    await slot.value!.revalidate();
  });

  assert.equal(slot.value!.connectionState, "pairing_required");
  assert.equal(slot.value!.session, null);
  assert.equal(window.sessionStorage.getItem(CAPABILITY_STORAGE_KEY), null);
});

test("EngineProvider selects preview vs live distinctly with no shared state", () => {
  const liveSlot: { value?: LiveEngineContextValue } = {};
  const previewSlot: { value?: GameplayContextValue } = {};

  const live = render(
    createElement(EngineProvider, {
      mode: "live",
      children: createElement(makeLiveProbe(liveSlot)),
    }),
  );
  assert.equal(liveSlot.value!.mode, "live");
  assert.equal(liveSlot.value!.connectionState, "starting");
  assert.equal(liveSlot.value!.playerState, null);
  live.unmount();

  const preview = render(
    createElement(EngineProvider, {
      mode: "preview",
      children: createElement(makePreviewProbe(previewSlot)),
    }),
  );
  assert.equal(previewSlot.value!.mode, "preview");
  assert.ok(previewSlot.value!.scenario, "preview still serves its authored scenario");
  preview.unmount();
});


test("concurrent session refreshes are single-flight", async () => {
  window.sessionStorage.setItem(CAPABILITY_STORAGE_KEY, "A".repeat(43));
  const slot: { value?: LiveEngineContextValue } = {}; let reads = 0;
  const host = fakeHost({ getSession: async () => { reads++; return ok(CLIENT_SESSION); }, getState: async () => ok(VALID_ENVELOPE) });
  renderLive(slot, host);
  await act(async () => { await Promise.all([slot.value!.revalidate(), slot.value!.revalidate()]); });
  assert.equal(reads, 1); assert.equal(slot.value!.connectionState, "ready");
});
