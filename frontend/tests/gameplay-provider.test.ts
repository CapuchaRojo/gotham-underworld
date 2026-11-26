import "./dom";
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { cleanup, render } from "@testing-library/react";
import App from "../src/App";
import { SCENARIO_BY_ID, SCENARIOS } from "../src/fixtures";
import {
  createPreviewGameplayClient,
  scenarioToPlayerState,
} from "../src/gameplay/preview";
import type { GameplayResult } from "../src/gameplay/types";
import type { Scenario } from "../src/types";

afterEach(() => {
  cleanup();
});

function expectOk<T>(r: GameplayResult<T>): T {
  assert.equal(r.ok, true, "expected an ok result");
  if (!r.ok) throw new Error(r.message);
  return r.value;
}

function expectErr(r: GameplayResult<unknown>) {
  assert.equal(r.ok, false, "expected an error result");
  if (r.ok) throw new Error("expected an error result");
  return r;
}

test("scenarioToPlayerState projects work into eligible opportunities", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const ps = scenarioToPlayerState(stable);

  assert.equal(ps.day, 4);
  assert.equal(ps.locationId, "goon.poi.p031");
  assert.deepEqual(ps.money, { cash: 40, arrears: 0, supportDebt: 0, prepaid: 0 });
  assert.deepEqual(ps.budget, { actionsUsed: 1, actionsMax: 3, tuUsed: 6, tuMax: 18 });
  assert.deepEqual(ps.housing, {
    status: "current",
    arrears: 0,
    prepaid: 0,
    nextDueDay: 7,
  });

  assert.equal(ps.opportunities.length, 3);

  const repair = ps.opportunities.find((o) => o.id === "work.store-repair")!;
  assert.equal(repair.executable, true);
  assert.deepEqual(repair.blockReasons, []);

  const audit = ps.opportunities.find((o) => o.id === "work.stock-audit")!;
  assert.equal(audit.executable, false);
  assert.deepEqual(audit.blockReasons, ["Work reference required"]);

  // Observations/institutions pass through player-safe as authored.
  assert.equal(ps.observations.length, stable.observations.length);
  assert.equal(ps.institutions.length, stable.institutions.length);
});

test("preview eligibility is a read-only projection of fixture availability", async () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const client = createPreviewGameplayClient({ getScenario: () => stable });

  const available = expectOk(await client.getEligibility("work.store-repair"));
  assert.equal(available.executable, true);
  assert.deepEqual(available.reasons, []);

  const gated = expectOk(await client.getEligibility("work.stock-audit"));
  assert.equal(gated.executable, false);
  assert.deepEqual(gated.reasons, ["Work reference required"]);

  const missing = expectErr(await client.getEligibility("does.not.exist"));
  assert.equal(missing.code, "ineligible");
});

test("preview mutations are unsupported and never mutate the career", async () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const before: Scenario = structuredClone(stable);
  let current: Scenario = stable;
  const client = createPreviewGameplayClient({ getScenario: () => current });

  const playerBefore = client.getPlayerState()!;

  const results = await Promise.all([
    client.getRouteQuote("goon.poi.p031", "goon.poi.p032"),
    client.authorizeTravel("goon.poi.p032"),
    client.executeAction({ choiceId: "work.store-repair", kind: "work" }),
    client.recover("request-id"),
    client.restore(),
  ]);

  for (const result of results) {
    assert.equal(result.ok, false);
    assert.equal(expectErr(result).code, "unsupported");
  }

  assert.deepEqual(current, before, "the scenario must not be mutated");
  assert.deepEqual(
    client.getPlayerState(),
    playerBefore,
    "the projected player state must not be mutated",
  );
});

test("preview provider never contacts the network or writes storage", async () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const client = createPreviewGameplayClient({ getScenario: () => stable });

  let networkCalls = 0;
  let storageWrites = 0;

  const originalFetch = globalThis.fetch;
  globalThis.fetch = (() => {
    networkCalls += 1;
    throw new Error("network access is disallowed for the preview provider");
  }) as typeof fetch;

  const win = (globalThis as { window?: Window }).window;
  const storageTargets = [win?.localStorage, win?.sessionStorage].filter(
    (s): s is Storage => s !== undefined,
  );
  const originals = storageTargets.map((s) => ({ target: s, set: s.setItem.bind(s) }));
  for (const s of storageTargets) {
    s.setItem = (() => {
      storageWrites += 1;
    }) as Storage["setItem"];
  }

  try {
    // Exercise every operation the client exposes.
    client.getPlayerState();
    await client.getRouteQuote("a", "b");
    await client.authorizeTravel("b");
    await client.getEligibility("work.store-repair");
    await client.executeAction({ choiceId: "work.store-repair", kind: "decline" });
    await client.recover("request-id");
    await client.restore();
  } finally {
    globalThis.fetch = originalFetch;
    for (const o of originals) o.target.setItem = o.set;
  }

  assert.equal(networkCalls, 0, "the preview provider must never contact a network endpoint");
  assert.equal(storageWrites, 0, "the preview provider must never write to storage");
});

test("scenario selection stays within the authored synthetic set", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  let current = stable;
  const source = {
    getScenario: () => current,
    selectScenario: (id: Scenario["id"]) => {
      current = SCENARIOS.find((s) => s.id === id) ?? stable;
    },
  };
  const client = createPreviewGameplayClient({ getScenario: source.getScenario });

  source.selectScenario("pressure");
  assert.equal(client.getPlayerState()!.day, 6);
  assert.equal(client.getPlayerState()!.money.cash, 11);

  source.selectScenario("uncertain");
  assert.equal(client.getPlayerState()!.day, 5);

  // Unknown id falls back to the source's default without throwing.
  source.selectScenario("stable");
  assert.equal(client.getPlayerState()!.day, 4);
});

test("App renders the synthetic preview and live-vs-synthetic context label", () => {
  const { getByText } = render(createElement(App));

  assert.ok(getByText("Synthetic preview — simulated display data"));
  assert.ok(getByText("Synthetic display data"));
});
