import "./dom";
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { createElement, StrictMode } from "react";
import { act, cleanup, render, screen } from "@testing-library/react";
import LiveInspectionApp from "../src/LiveInspectionApp";
import {
  LocalEngineInspection,
  LocalEngineInspectionView,
} from "../src/components/LocalEngineInspectionView";
import type { LocalEngineInspectionViewProps } from "../src/components/LocalEngineInspectionView";
import {
  LiveEngineProvider,
  useLiveEngine,
} from "../src/gameplay/LiveEngineProvider";
import type { LiveEngineContextValue } from "../src/gameplay/LiveEngineProvider";
import { liveEngineStatus } from "../src/gameplay/liveEngine";
import { ENGINE_RELEASE } from "../src/gameplay/wire";
import type { BootstrapResponse, EngineEnvelope, HostSession } from "../src/gameplay/wire";
import { CAPABILITY_STORAGE_KEY, CLIENT_BUNDLE_ID } from "../src/gameplay/host";
import type { HostClient, HostResult } from "../src/gameplay/host";

afterEach(() => {
  cleanup();
  try {
    window.sessionStorage.removeItem(CAPABILITY_STORAGE_KEY);
  } catch {
    // Ignore.
  }
});

// ---------------------------------------------------------------------------
// Fixtures (validated Python host shapes — never authored `Scenario` fixtures)
// ---------------------------------------------------------------------------

const SESSION: HostSession = {
  host_protocol_version: 1,
  bridge_protocol_version: 1,
  bundle_id: CLIENT_BUNDLE_ID,
  manifest_sha256: "a".repeat(64),
  engine_release: ENGINE_RELEASE,
  instance_id: "inst.1",
  mode: "local_engine",
  session_lifetime: "process",
};

const BOOTSTRAP: BootstrapResponse = { ...SESSION, capability: "A".repeat(43) };

const FULL_ENVELOPE: EngineEnvelope = {
  protocol_version: 1,
  career_id: "career.a1",
  lineage_id: "lineage.1",
  revision: 99,
  allowed_commands: ["wait", "settle_in", "choose", "travel"],
  receipt: null,
  duplicate: false,
  state: {
    day: 42,
    player: { cash: 1337, heat: 6, custody: "free" },
    budgets: {
      daily_actions: 3,
      actions_remaining: 2,
      daily_travel_units: 18,
      travel_units_remaining: 9,
    },
    location: { id: "goon.poi.p032", label: "Uptown General Store" },
    systems: {
      navigation: "active",
      daily_life: "active",
      ordinary: "pending",
      mobility: "not_adopted",
    },
    housing: {
      status: "current",
      home_id: "goon.housing.room1",
      next_due_day: 15,
      arrears: 0,
      prepaid: 2,
    },
    contacts: [
      { id: "contact.tess", name: "Tess Navarro", role: "Fixer", standing: 2 },
      { id: "contact.cal", name: "Cal", role: "Contact", standing: 1 },
    ],
    opportunities: [
      {
        id: "goon.choice.0.opening_shift",
        title: "Opening shift",
        situation: "Need hands on the register.",
        speaker: "Tess",
        open_day: 1,
        expires_day: 10,
        state: "open",
        command: "choose",
        options: [
          {
            id: "goon.choice.0.opt.work",
            label: "Work the shift",
            availability: "available",
            reason: null,
            action_cost: 1,
            tradeoff: "Earn cash",
            arguments: {
              choice_id: "goon.choice.0",
              option_id: "goon.choice.0.opt.work",
            },
          },
          {
            id: "goon.choice.0.opt.decline",
            label: "Decline",
            availability: "unavailable",
            reason: "No reason to decline",
            action_cost: 0,
            tradeoff: "Skip it",
            arguments: {
              choice_id: "goon.choice.0",
              option_id: "goon.choice.0.opt.decline",
            },
          },
        ],
      },
    ],
    outcomes: [
      {
        choice_id: "goon.choice.0",
        option_id: "goon.choice.0.opt.work",
        day: 3,
        feedback: "Worked the register.",
      },
    ],
    ordinary: {
      employment: 1,
      assistance: { status: "unused", amount: 0, due_day: null },
    },
  },
};

// Nullable/missing fields: location/housing/travel-units null, ordinary omitted.
const MINIMAL_ENVELOPE: EngineEnvelope = {
  protocol_version: 1,
  career_id: "career.min",
  lineage_id: "lineage.min",
  revision: 1,
  allowed_commands: ["wait"],
  receipt: null,
  duplicate: false,
  state: {
    day: 1,
    player: { cash: 40, heat: 0, custody: "free" },
    budgets: {
      daily_actions: 3,
      actions_remaining: 3,
      daily_travel_units: 18,
      travel_units_remaining: null,
    },
    location: null,
    systems: {
      navigation: "not_adopted",
      daily_life: "not_adopted",
      ordinary: "not_adopted",
      mobility: "not_adopted",
    },
    housing: null,
    contacts: [],
    opportunities: [],
    outcomes: [],
  },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderView(overrides: Partial<LocalEngineInspectionViewProps> = {}) {
  return render(
    createElement(LocalEngineInspectionView, {
      status: liveEngineStatus("ready"),
      session: SESSION,
      engineState: FULL_ENVELOPE,
      lastSessionFailure: null,
      lastError: null,
      ...overrides,
    }),
  );
}

function ok<T>(value: T): HostResult<T> {
  return { ok: true, value };
}

function fakeHost(impl: Partial<HostClient> = {}): HostClient {
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
    postCommand: impl.postCommand ?? (async () => {
      throw new Error("unexpected postCommand call");
    }),
    getOperation: impl.getOperation ?? (async () => {
      throw new Error("unexpected getOperation call");
    }),
  };
}

function makeProbe(slot: { value?: LiveEngineContextValue }) {
  return function Probe() {
    slot.value = useLiveEngine();
    return null;
  };
}

function renderConnected(slot: { value?: LiveEngineContextValue }, host: HostClient) {
  return render(
    createElement(
      LiveEngineProvider,
      { hostClient: host },
      createElement(
        "div",
        null,
        createElement(LocalEngineInspection),
        createElement(makeProbe(slot)),
      ),
    ),
  );
}

// ---------------------------------------------------------------------------
// Rendering the validated projection
// ---------------------------------------------------------------------------

test("renders the validated projection from a ready live engine", () => {
  renderView();

  assert.ok(screen.getByText("Local Engine Inspection"));
  assert.ok(screen.getByText("Ready"));

  assert.equal(screen.getByTestId("career-id").textContent, "career.a1");
  assert.equal(screen.getByTestId("lineage-id").textContent, "lineage.1");
  assert.equal(screen.getByTestId("bridge-revision").textContent, "99");
  assert.equal(screen.getByTestId("player-day").textContent, "42");
  assert.equal(screen.getByTestId("player-cash").textContent, "1337");
  assert.equal(screen.getByTestId("player-heat").textContent, "6");
  assert.equal(screen.getByTestId("player-custody").textContent, "free");
  assert.equal(screen.getByTestId("actions-remaining").textContent, "2 / 3");
  assert.equal(screen.getByTestId("travel-units-remaining").textContent, "9 / 18");

  assert.match(screen.getByTestId("location").textContent ?? "", /Uptown General Store/);
  assert.equal(screen.getByTestId("housing-status").textContent, "current");
  assert.equal(screen.getByTestId("housing-home").textContent, "goon.housing.room1");

  // Systems adoption state is shown verbatim.
  assert.equal(screen.getAllByText("active").length, 2);
  assert.ok(screen.getByText("pending"));
  assert.ok(screen.getByText("not_adopted"));

  // Contacts (Tess + Cal) and their standings.
  assert.ok(screen.getByText("Tess Navarro"));
  assert.ok(screen.getByText("Cal"));
  assert.ok(screen.getByText("standing 2"));
  assert.ok(screen.getByText("standing 1"));

  // Opportunities + option-level availability/cost/arguments.
  assert.ok(screen.getByText("Opening shift"));
  assert.ok(screen.getByText("available"));
  assert.ok(screen.getByText(/No reason to decline/));
  assert.ok(
    screen.getByText(/choice_id=goon\.choice\.0, option_id=goon\.choice\.0\.opt\.work/),
  );

  // Outcomes and ordinary-life projection are present.
  assert.ok(screen.getByText(/Worked the register/));
  assert.ok(screen.getByText("unused"));
});

test("renders nullable and missing projection fields as unavailable, never fabricated", () => {
  renderView({ engineState: MINIMAL_ENVELOPE });

  assert.equal(screen.getByTestId("player-day").textContent, "1");
  assert.match(screen.getByTestId("location").textContent ?? "", /unavailable/);
  assert.match(screen.getByTestId("housing").textContent ?? "", /unavailable/);
  assert.match(
    screen.getByTestId("travel-units-remaining").textContent ?? "",
    /unavailable/,
  );
  // `ordinary` is absent from the projection → unavailable, not synthesized.
  assert.ok(screen.getByText(/not yet enabled/));
});

test("labels observations, institutions, and commitments as unavailable (absent from projection)", () => {
  renderView();

  assert.ok(screen.getByText("Not in the projection"));
  assert.ok(screen.getByText("Observations"));
  assert.ok(screen.getByText("Institutions"));
  assert.ok(screen.getByText("Commitments"));
  assert.ok(screen.getAllByText("unavailable").length >= 3);
});

test("never leaks synthetic preview or fixture content into the inspection surface", () => {
  renderView();

  assert.equal(screen.queryByText(/Synthetic preview/i), null);
  assert.equal(screen.queryByText(/Fixture-driven/i), null);
  assert.equal(screen.queryByText(/Stable life/i), null);
  assert.equal(screen.queryByText(/simulated display data/i), null);
});

test("with no engine state shows unavailable, not a fabricated projection", () => {
  renderView({
    status: liveEngineStatus("disconnected"),
    session: null,
    engineState: null,
  });

  assert.ok(screen.getByText("Disconnected"));
  assert.ok(screen.getByText(/no validated host session/));
  assert.ok(screen.getAllByText(/no validated projection/).length >= 1);
  assert.equal(screen.queryByText(/Uptown General Store/), null);
  assert.equal(screen.queryByTestId("bridge-revision"), null);
});

// ---------------------------------------------------------------------------
// Read-only + no-mutation guarantees
// ---------------------------------------------------------------------------

test("the inspection surface renders no mutation affordances", () => {
  const { container } = renderView();
  assert.equal(container.querySelectorAll("button, input, select, textarea").length, 0);
});

test("mounting the inspection surface makes no host calls (StrictMode-safe, read-only reload)", () => {
  let calls = 0;
  const throwingHost: HostClient = {
    bootstrap: async () => {
      calls += 1;
      throw new Error("unexpected bootstrap call");
    },
    getSession: async () => {
      calls += 1;
      throw new Error("unexpected getSession call");
    },
    getState: async () => {
      calls += 1;
      throw new Error("unexpected getState call");
    },
    postCommand: async () => {
      calls += 1;
      throw new Error("unexpected postCommand call");
    },
    getOperation: async () => {
      calls += 1;
      throw new Error("unexpected getOperation call");
    },
  };

  render(
    createElement(
      StrictMode,
      null,
      createElement(
        LiveEngineProvider,
        { hostClient: throwingHost },
        createElement(LocalEngineInspection),
      ),
    ),
  );

  assert.ok(screen.getByText("Local Engine Inspection"));
  assert.ok(screen.getByText("Starting"));
  assert.equal(calls, 0);
});

test("LiveInspectionApp mounts the read-only surface fail-closed at Starting", () => {
  const { container } = render(createElement(LiveInspectionApp));
  assert.ok(screen.getByText("Local Engine Inspection"));
  assert.ok(screen.getByText("Starting"));
  assert.equal(container.querySelectorAll("button, input, select, textarea").length, 0);
});

// ---------------------------------------------------------------------------
// Session transitions + disconnected / incompatible / inaccessible conditions
// ---------------------------------------------------------------------------

test("a successful pair transitions the surface from Starting to Ready with the projection", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ok(BOOTSTRAP),
    getState: async () => ok(FULL_ENVELOPE),
  });
  renderConnected(slot, host);

  assert.ok(screen.getByText("Starting"));

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.ok(screen.getByText("Ready"));
  assert.equal(screen.getByTestId("career-id").textContent, "career.a1");
  assert.equal(screen.getByTestId("bridge-revision").textContent, "99");
  assert.equal(screen.getByText("career.a1"), screen.getByTestId("career-id"));
});

test("a transport failure during pairing surfaces Disconnected with no projection and no fixtures", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ({
      ok: false,
      failure: { kind: "transport", message: "connection refused" },
    }),
  });
  renderConnected(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.ok(screen.getByText("Disconnected"));
  assert.ok(screen.getByText(/connection refused/));
  assert.ok(screen.getAllByText(/no validated projection/).length >= 1);
  assert.equal(screen.queryByText(/Uptown General Store/), null);
});

test("an inaccessible engine after a valid session fails closed to Disconnected", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ok(BOOTSTRAP),
    getState: async () => ({
      ok: false,
      failure: { kind: "transport", message: "host unreachable" },
    }),
  });
  renderConnected(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.ok(screen.getByText("Disconnected"));
  assert.ok(screen.getByText(/host unreachable/));
  assert.equal(screen.queryByTestId("bridge-revision"), null);
});

test("invalid projection data fails closed to Incompatible and never renders a projection", async () => {
  const slot: { value?: LiveEngineContextValue } = {};
  const host = fakeHost({
    bootstrap: async () => ok(BOOTSTRAP),
    getState: async () => ({
      ok: false,
      failure: {
        kind: "validation",
        code: "invalid_integer",
        message: "$.state.day must be a safe integer",
        path: "$.state.day",
      },
    }),
  });
  renderConnected(slot, host);

  await act(async () => {
    await slot.value!.pair("c".repeat(43));
  });

  assert.ok(screen.getByText("Incompatible"));
  assert.ok(screen.getByText(/Session failure/));
  assert.equal(screen.queryByTestId("bridge-revision"), null);
  assert.ok(screen.getAllByText(/no validated projection/).length >= 1);
});
