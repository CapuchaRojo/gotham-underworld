import "./dom";
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";
import App from "../src/App";
import { PresentationModeProvider } from "../src/presentation";
import { TodayView } from "../src/components/TodayView";
import { ACCESS_LABELS, accessSummary } from "../src/navigation";
import { SCENARIO_BY_ID, SCENARIOS } from "../src/fixtures";
import { placeById } from "../src/atlas";

afterEach(() => {
  cleanup();
});

function renderToday(scenario: (typeof SCENARIOS)[number]) {
  return render(
    createElement(PresentationModeProvider, null, createElement(TodayView, { scenario })),
  );
}

test("Today is the default Player Mode landing view", () => {
  const { getAllByText, getByRole, getByText } = render(createElement(App));
  assert.equal(getByRole("tab", { name: "Today" }).getAttribute("aria-selected"), "true");
  assert.ok(getByText("What I have left today"));
  assert.ok(getAllByText("East Side Housing Cooperative").length > 0);
});

test("Streets, My Life, and My Story remain reachable", () => {
  const { getByRole } = render(createElement(App));
  assert.ok(getByRole("tab", { name: "The Streets" }));
  assert.ok(getByRole("tab", { name: "My Life" }));
  assert.ok(getByRole("tab", { name: "My Story" }));
});

test("Today shows current location and day from the fixture", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const { getAllByText, getByText } = renderToday(stable);
  assert.ok(getByText("Day 4"), "day must come from the fixture");
  assert.ok(getAllByText("East Side Housing Cooperative").length > 0, "location must use its readable name");
  assert.ok(getByText("Private residence — home permission required"), "access must read as words");
});

test("budget and money stay separate and match the selected fixture", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const { container, getByLabelText, getByText } = renderToday(stable);

  assert.ok(getByText("$40"), "cash must match the fixture");
  assert.ok(getByText("Cash"), "cash stays its own value");
  assert.ok(getByText("Owed"), "owed stays its own value");
  assert.ok(getByText("Prepaid"), "prepaid stays its own value");

  assert.ok(container.textContent?.includes("2 of 3"), "actions remaining");
  assert.ok(container.textContent?.includes("12 of 18"), "travel remaining");

  assert.equal(getByLabelText("Actions").getAttribute("aria-valuenow"), "2");
  assert.equal(getByLabelText("Actions").getAttribute("aria-valuemax"), "3");
  assert.equal(getByLabelText("Travel Units").getAttribute("aria-valuenow"), "12");
  assert.equal(getByLabelText("Travel Units").getAttribute("aria-valuemax"), "18");
});

test("housing and obligations reflect the fixture data", () => {
  const pressure = SCENARIO_BY_ID.get("pressure")!;
  const { getByText } = renderToday(pressure);
  assert.ok(getByText("Rent is overdue."), "housing pressure is readable");
  assert.ok(getByText("Rent — Day 5"), "missed rent is called out");
  assert.ok(getByText("Tess support advance"), "upcoming support advance is called out");
  assert.ok(getByText("missed"), "overdue state is labeled");
  assert.ok(getByText("pending"), "upcoming state is labeled");
});

test("available opportunities respect prerequisites and knowledge boundaries", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const stableView = renderToday(stable);
  assert.ok(stableView.getByText("Uptown General Store — shelf repair"), "available work stays visible");
  assert.ok(stableView.getByText("Stock audit — Wayne Tower mailroom"), "gated work stays visible");
  assert.ok(stableView.getByText("Work reference required"), "unmet prerequisite stays visible");
  stableView.unmount();

  const uncertain = SCENARIO_BY_ID.get("uncertain")!;
  const uncertainView = renderToday(uncertain);
  assert.ok(uncertainView.getByText("Undiscovered location"), "undiscovered opportunity is acknowledged");
  assert.ok(!uncertainView.container.innerHTML.includes("Iceberg Lounge"), "undiscovered name stays hidden");
  assert.ok(!uncertainView.container.innerHTML.includes("goon.poi.p048"), "undiscovered id stays hidden");
});

test("uncertain observations remain uncertain", () => {
  const uncertain = SCENARIO_BY_ID.get("uncertain")!;
  const { getAllByText, getByText } = renderToday(uncertain);
  assert.ok(getAllByText("unconfirmed").length >= 2, "both conflicting sources stay unconfirmed");
  assert.ok(getByText(/Secondhand, from a voicemail/), "source limitation stays visible");
  assert.ok(getByText(/Intake entry only/), "institutional limitation stays visible");
});

test("all three QA scenarios produce distinct Today summaries", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const pressure = SCENARIO_BY_ID.get("pressure")!;
  const uncertain = SCENARIO_BY_ID.get("uncertain")!;

  const s = renderToday(stable);
  assert.ok(s.getByText("Day 4"));
  assert.ok(s.getByText("$40"));
  assert.ok(s.getByText("Rent is current."));
  assert.ok(s.getByText("Nothing overdue today."));
  s.unmount();

  const p = renderToday(pressure);
  assert.ok(p.getByText("Day 6"));
  assert.ok(p.getByText("$11"));
  assert.ok(p.getByText("Rent is overdue."));
  assert.ok(p.getByText("Blackgate Controlled Ferry"));
  p.unmount();

  const u = renderToday(uncertain);
  assert.ok(u.getByText("Day 5"));
  assert.ok(u.getByText("$18"));
  assert.ok(u.getByText("Undiscovered location"));
  u.unmount();
});

test("presentation-mode switching does not change gameplay state and returns to Today", () => {
  const before = JSON.stringify(SCENARIOS);
  const { getByRole } = render(createElement(App));

  fireEvent.click(getByRole("button", { name: "Developer Inspection" }));
  assert.equal(getByRole("tab", { name: "The Streets" }).getAttribute("aria-selected"), "true");

  fireEvent.click(getByRole("button", { name: "Exit Developer Inspection" }));
  assert.equal(getByRole("tab", { name: "Today" }).getAttribute("aria-selected"), "true");
  assert.equal(JSON.stringify(SCENARIOS), before, "fixtures must be unchanged by mode toggling");
});

test("navigation links switch to the other views", () => {
  const { getByRole, getByText, getByPlaceholderText } = render(createElement(App));

  fireEvent.click(getByRole("button", { name: "Open My Life" }));
  assert.ok(getByText("Adoption terms"), "My Life link reaches the life view");

  fireEvent.click(getByRole("tab", { name: "Today" }));
  fireEvent.click(getByRole("button", { name: "Open The Streets" }));
  assert.ok(getByPlaceholderText(/Search 176 places by name or type/), "Streets link reaches the streets view");

  fireEvent.click(getByRole("tab", { name: "Today" }));
  fireEvent.click(getByRole("button", { name: "Open My Story" }));
  assert.ok(getByText("Tess"), "Story link reaches the story view");
});

test("no raw IDs or developer-only diagnostics appear in Player Mode", () => {
  const { container, queryByText, queryByRole } = render(createElement(App));
  assert.ok(!container.innerHTML.includes("goon."), "player mode must not render goon.* ids");
  assert.equal(queryByText(/Profile codes/), null, "profile legend stays hidden");
  assert.equal(queryByText(/Developer Preview/), null, "QA section stays hidden");
  assert.equal(queryByRole("button", { name: "Stable life" }), null, "scenario switcher stays hidden");
});

test("access states read as words via ACCESS_LABELS", () => {
  const home = placeById.get("goon.poi.p031")!;
  assert.ok(home.access.includes("HOME"));
  assert.equal(ACCESS_LABELS.HOME, "Private residence — home permission required");
  assert.ok(accessSummary(home).includes("Private residence — home permission required"));

  const stable = SCENARIO_BY_ID.get("stable")!;
  const { getByText } = renderToday(stable);
  assert.ok(getByText("Private residence — home permission required"));
});
