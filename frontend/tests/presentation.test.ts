import { test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import {
  DEFAULT_PRESENTATION_MODE,
  togglePresentationMode,
  PresentationModeProvider,
  usePresentationMode,
} from "../src/presentation";
import { DeveloperModeToggle } from "../src/components/DeveloperModeToggle";
import { SCENARIO_BY_ID, SCENARIOS } from "../src/fixtures";

function ModeProbe() {
  const { mode, isDeveloper } = usePresentationMode();
  return createElement("span", null, `${mode}:${isDeveloper ? "dev" : "player"}`);
}

function ScenarioProbe() {
  const { mode } = usePresentationMode();
  const s = SCENARIO_BY_ID.get("stable")!;
  return createElement("span", null, `${mode}|${s.id}|${s.locationId}|${s.money.cash}`);
}

test("default presentation mode is player", () => {
  assert.equal(DEFAULT_PRESENTATION_MODE, "player");
});

test("togglePresentationMode flips player <-> developer", () => {
  assert.equal(togglePresentationMode("player"), "developer");
  assert.equal(togglePresentationMode("developer"), "player");
});

test("provider defaults to player mode", () => {
  const html = renderToStaticMarkup(
    createElement(PresentationModeProvider, null, createElement(ModeProbe)),
  );
  assert.ok(html.includes("player:player"), "provider should render player mode by default");
});

test("usePresentationMode falls back to player without a provider", () => {
  const html = renderToStaticMarkup(createElement(ModeProbe));
  assert.ok(html.includes("player:player"), "hook should degrade to player outside a provider");
});

test("developer badge appears only in developer mode", () => {
  const dev = renderToStaticMarkup(
    createElement(
      PresentationModeProvider,
      { initialMode: "developer" },
      createElement(DeveloperModeToggle),
    ),
  );
  assert.ok(dev.includes("Developer Inspection Mode"), "developer badge should show");
  assert.ok(dev.includes("Exit Developer Inspection"), "exit control should show");

  const player = renderToStaticMarkup(
    createElement(PresentationModeProvider, null, createElement(DeveloperModeToggle)),
  );
  assert.ok(!player.includes("Developer Inspection Mode"), "no badge in player mode");
  assert.ok(player.includes("Developer Inspection"), "toggle should be discoverable in player mode");
});

test("scenario-derived data is identical in player and developer mode", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const player = renderToStaticMarkup(
    createElement(PresentationModeProvider, null, createElement(ScenarioProbe)),
  );
  const developer = renderToStaticMarkup(
    createElement(
      PresentationModeProvider,
      { initialMode: "developer" },
      createElement(ScenarioProbe),
    ),
  );

  const suffix = `${stable.id}|${stable.locationId}|${stable.money.cash}`;
  assert.ok(player.includes(`player|${suffix}`));
  assert.ok(developer.includes(`developer|${suffix}`));
});

test("toggling mode never mutates scenario fixtures", () => {
  const before = JSON.stringify(SCENARIOS);
  togglePresentationMode("player");
  togglePresentationMode("developer");
  assert.equal(JSON.stringify(SCENARIOS), before);
});
