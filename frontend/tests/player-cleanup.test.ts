import "./dom";
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";
import App from "../src/App";
import { PresentationModeProvider } from "../src/presentation";
import { StreetsView } from "../src/components/StreetsView";
import { LifeView } from "../src/components/LifeView";
import { StoryView } from "../src/components/StoryView";
import { SCENARIO_BY_ID, SCENARIOS } from "../src/fixtures";
import { PLACES, REGIONS, placeById } from "../src/atlas";

afterEach(() => {
  cleanup();
});

function renderPlayerView(scenario: ScenarioLike, view: "streets" | "life" | "story") {
  const scenarioElement =
    view === "streets"
      ? createElement(StreetsView, { scenario })
      : view === "life"
        ? createElement(LifeView, { scenario })
        : createElement(StoryView, { scenario });
  return render(createElement(PresentationModeProvider, null, scenarioElement));
}

type ScenarioLike = (typeof SCENARIOS)[number];

test("default player mode leaks no raw goon identifiers and no profile legend", () => {
  const { container, queryByText } = render(createElement(App));
  assert.ok(!container.innerHTML.includes("goon."), "player mode must not render goon.* ids");
  assert.equal(queryByText(/Profile codes/), null, "profile-code legend must be hidden in player mode");
  assert.ok(container.innerHTML.includes("East Side Housing Cooperative"), "readable location label stays visible");
});

test("player mode hides raw access chips and profile codes but keeps the access summary", () => {
  const { queryAllByText } = render(createElement(App));
  assert.equal(queryAllByText("HOME").length, 0, "raw HOME access chip must be hidden");
  assert.equal(queryAllByText("Economy").length, 0, "raw profile code labels must be hidden");
  assert.ok(
    queryAllByText(/Private residence — home permission required/).length > 0,
    "human-readable access restriction must remain visible",
  );
});

test("developer inspection reveals raw ids, the profile legend, and access chips", () => {
  const { container, getByRole, getByText, queryAllByText } = render(createElement(App));
  fireEvent.click(getByRole("button", { name: "Developer Inspection" }));
  assert.ok(container.innerHTML.includes("goon.poi."), "developer mode must show authored ids");
  assert.ok(getByText(/Profile codes/), "profile-code legend must appear in developer mode");
  assert.ok(queryAllByText("HOME").length > 0, "raw access chips must appear in developer mode");
});

test("toggling presentation mode never mutates scenario fixtures", () => {
  const before = JSON.stringify(SCENARIOS);
  const { getByRole } = render(createElement(App));
  fireEvent.click(getByRole("button", { name: "Developer Inspection" }));
  fireEvent.click(getByRole("button", { name: "Exit Developer Inspection" }));
  assert.equal(JSON.stringify(SCENARIOS), before, "fixtures must be byte-for-byte unchanged");
});

test("player search finds places by visible name", () => {
  const { getByPlaceholderText, getByRole, getByText } = render(createElement(App));
  fireEvent.click(getByRole("tab", { name: "The Streets" }));
  fireEvent.change(getByPlaceholderText(/Search 176 places by name or type/), {
    target: { value: "Wayne Tower" },
  });
  assert.ok(getByText("Wayne Tower"), "search by name must resolve the place");
});

test("player search does not expose raw ids; developer id search remains available", () => {
  const { getByPlaceholderText, getByRole, queryByText, getByText } = render(createElement(App));

  fireEvent.click(getByRole("tab", { name: "The Streets" }));
  fireEvent.change(getByPlaceholderText(/Search 176 places by name or type/), {
    target: { value: "goon.poi.p031" },
  });
  assert.ok(queryByText(/No places match/), "player search must not resolve raw ids");

  fireEvent.click(getByRole("button", { name: "Developer Inspection" }));
  fireEvent.change(getByPlaceholderText(/Search 176 places by name, type or identifier/), {
    target: { value: "goon.poi.p031" },
  });
  assert.equal(queryByText(/No places match/), null, "developer search must resolve raw ids");
  assert.ok(getByText("goon.poi.p031"), "developer search must reveal the matching authored id");
});

test("region filter keeps narrowing the player-facing list", () => {
  const home = placeById.get("goon.poi.p031")!;
  const region = REGIONS.find((r) => r.id !== home.regionId)!;
  const inRegion = PLACES.find((p) => p.regionId === region.id && p.kind === "poi" && p.id !== home.id)!;
  const outRegion = PLACES.find((p) => p.regionId !== region.id && p.kind === "poi" && p.id !== home.id)!;
  assert.ok(region && inRegion && outRegion, "test needs one place inside and one outside the chosen region");

  const { getByRole, getByText, queryByText } = render(createElement(App));
  fireEvent.click(getByRole("tab", { name: "The Streets" }));
  fireEvent.change(getByRole("combobox"), { target: { value: region.label } });
  assert.ok(getByText(inRegion.label), "in-region place must remain visible");
  assert.equal(queryByText(outRegion.label), null, "out-of-region place must be filtered out");
});

test("player mode keeps restricted routes and travel requirements visible", () => {
  const pressure = SCENARIO_BY_ID.get("pressure")!;
  const { getByText, getAllByText } = renderPlayerView(pressure, "streets");
  assert.ok(getByText(/Restricted route/), "restricted route callout must remain");
  assert.ok(getByText(/Blackgate Controlled Ferry/), "restricted destination label must remain");
  assert.ok(
    getAllByText(/Private residence — home permission required/).length > 0,
    "known access requirement must remain visible",
  );
});

test("My Life keeps meaningful info and hides technical ids", () => {
  const pressure = SCENARIO_BY_ID.get("pressure")!;
  const { container, getByText, getAllByText } = renderPlayerView(pressure, "life");
  assert.ok(getByText("$11"), "cash must stay visible");
  assert.ok(getByText("overdue"), "housing status must stay visible");
  assert.ok(getByText("Travel Units"), "budget meter must stay visible");
  assert.ok(getAllByText("East Side Housing Cooperative").length > 0, "location label must stay visible");
  assert.ok(getByText(/North Borough Police Station/), "commitment detail must stay readable");
  assert.ok(!container.innerHTML.includes("goon."), "life view must not render goon.* ids");
  assert.ok(!container.innerHTML.includes("(p044)"), "life view must not render short place ids");
});

test("My Story keeps meaningful info and hides technical ids", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const { container, getByText } = renderPlayerView(stable, "story");
  assert.ok(getByText("Tess"), "contact name must stay visible");
  assert.ok(getByText("Marlon"), "contact name must stay visible");
  assert.ok(getByText("GCPD intake"), "institutional record must stay visible");
  assert.ok(getByText("Night Shift"), "observation title must stay visible");
  assert.ok(getByText(/Uptown General Store/), "contact note must stay readable");
  assert.ok(!container.innerHTML.includes("goon."), "story view must not render goon.* ids");
  assert.ok(!container.innerHTML.includes("(p032)"), "story view must not render short place ids");
});

test("contradictory observations and institutional uncertainty remain intact in player mode", () => {
  const uncertain = SCENARIO_BY_ID.get("uncertain")!;
  const { getAllByText, getByText } = renderPlayerView(uncertain, "story");
  assert.ok(getAllByText("Conflicts with another source").length > 0, "conflict flag must remain");
  assert.ok(getByText(/neither is marked true/), "uncertainty disclaimer must remain");
  assert.ok(getAllByText("unconfirmed").length > 0, "unconfirmed badges must remain");
});
