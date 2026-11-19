import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import "./dom";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { LifeView } from "../src/components/LifeView";
import { StoryView } from "../src/components/StoryView";
import { StreetsView } from "../src/components/StreetsView";
import { SCENARIO_BY_ID } from "../src/fixtures";
import { PLACES } from "../src/atlas";

afterEach(() => cleanup());

const stable = () => SCENARIO_BY_ID.get("stable")!;
const pressure = () => SCENARIO_BY_ID.get("pressure")!;
const uncertain = () => SCENARIO_BY_ID.get("uncertain")!;

function markup(Component: typeof StreetsView, scenario = stable()): string {
  return renderToStaticMarkup(createElement(Component, { scenario }));
}

// ---------------------------------------------------------------------------
// The Streets
// ---------------------------------------------------------------------------

test("The Streets shows a result count and hides Clear filters until filtering", () => {
  const html = markup(StreetsView);
  assert.ok(html.includes(`of ${PLACES.length} places`), "an at-a-glance result count is shown");
  assert.ok(!html.includes("Clear filters"), "no clear-filters affordance while unfiltered");
  // Copy pinned by views.test.ts must survive.
  assert.ok(html.includes("Search 176 places"));
  assert.ok(html.includes("All regions"));
  assert.ok(html.includes("Neighborhoods"));
});

test("The Streets offers Clear filters when a search yields nothing, and it restores the list", () => {
  render(createElement(StreetsView, { scenario: stable() }));
  const input = screen.getByPlaceholderText(/Search 176 places/);

  fireEvent.change(input, { target: { value: "zzzz-no-such-place" } });
  assert.ok(screen.getByText(/No places match/), "empty result is explained");
  const clear = screen.getByRole("button", { name: /Clear filters and show all places/i });

  fireEvent.click(clear);
  assert.equal(screen.queryByText(/No places match/), null, "clearing restores results");
  assert.ok(screen.queryByRole("button", { name: /Clear filters/i }) === null, "clear affordance hides again");
});

// ---------------------------------------------------------------------------
// My Life
// ---------------------------------------------------------------------------

test("My Life explains resources and reads due days relatively", () => {
  const html = markup(LifeView as unknown as typeof StreetsView, pressure());
  assert.ok(html.includes("Cash, “Owed”, and prepaid stay separate"), "money framing is explained");
  assert.ok(html.includes("(due tomorrow)"), "housing due date reads relatively");
  assert.ok(html.includes("1 day overdue"), "a missed commitment reads as overdue");
});

// ---------------------------------------------------------------------------
// My Story
// ---------------------------------------------------------------------------

test("My Story summarises observation confidence and defines the terms", () => {
  const html = markup(StoryView as unknown as typeof StreetsView, uncertain());
  assert.ok(html.includes("2 observations"), "observation count is summarised");
  assert.ok(html.includes("2 unconfirmed"), "confidence mix is summarised");
  assert.ok(html.includes("Documented means a record backs it"), "the terms are defined");
  // Copy pinned by views.test.ts must survive.
  assert.ok(html.includes("neither is marked true"));
  assert.ok(html.includes("Tess"));
  assert.ok(html.includes("GCPD intake"));
});
