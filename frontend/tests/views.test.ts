import { test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import App from "../src/App";
import { StreetsView } from "../src/components/StreetsView";
import { LifeView } from "../src/components/LifeView";
import { StoryView } from "../src/components/StoryView";
import { SCENARIO_BY_ID } from "../src/fixtures";

const FORBIDDEN = [
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

function assertClean(markup: string, label: string) {
  for (const token of FORBIDDEN) {
    assert.ok(!markup.includes(token), `${label} must not leak "${token}"`);
  }
}

test("App renders all three tabs and the default stable scenario", () => {
  const html = renderToStaticMarkup(createElement(App));
  for (const s of [
    "Gotham: The Goon",
    "The Streets",
    "My Life",
    "My Story",
    "Current location",
    "East Side Housing Cooperative",
  ]) {
    assert.ok(html.includes(s), `App should contain "${s}"`);
  }
  assertClean(html, "App");
});

test("App hides QA scenario controls in default player mode", () => {
  const html = renderToStaticMarkup(createElement(App));
  assert.ok(!html.includes("Developer Preview"), "player mode must not show the QA scenario section");
  assert.ok(!html.includes("QA scenarios, not gameplay modes"), "player mode must not show QA scenario copy");
  assert.ok(!html.includes("Financial pressure"), "player mode must not show the pressure scenario control");
  assert.ok(!html.includes("Uncertain information"), "player mode must not show the uncertain scenario control");
});

test("LifeView presents money/budget state correctly and leaks nothing", () => {
  const pressure = SCENARIO_BY_ID.get("pressure")!;
  const html = renderToStaticMarkup(createElement(LifeView, { scenario: pressure }));
  assert.ok(html.includes("overdue"), "housing status should be overdue");
  assert.ok(html.includes("$50"), "owed = $30 arrears + $20 support debt");
  assert.ok(html.includes("$11"), "cash should be $11");
  assert.ok(html.includes("Travel Units"), "TU meter should render");
  assertClean(html, "LifeView");
});

test("StoryView surfaces conflicting sources and marks neither true", () => {
  const uncertain = SCENARIO_BY_ID.get("uncertain")!;
  const html = renderToStaticMarkup(createElement(StoryView, { scenario: uncertain }));
  assert.ok(html.includes("Conflicts with another source"));
  assert.ok(html.includes("neither is marked true"));
  assert.ok(html.includes("Tess"));
  assert.ok(html.includes("GCPD intake"));
  assertClean(html, "StoryView");
});

test("StreetsView renders search, filters, and the restricted-route callout", () => {
  const pressure = SCENARIO_BY_ID.get("pressure")!;
  const html = renderToStaticMarkup(createElement(StreetsView, { scenario: pressure }));
  assert.ok(html.includes("Search 176 places"));
  assert.ok(html.includes("All regions"));
  assert.ok(html.includes("Current location"));
  assert.ok(html.includes("Restricted route"));
  assert.ok(html.includes("Blackgate Controlled Ferry"));
  assertClean(html, "StreetsView");
});
