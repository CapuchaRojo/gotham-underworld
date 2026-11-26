import "./dom";
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";
import App from "../src/App";

afterEach(() => {
  cleanup();
});

test("player mode is the default and hides QA scenario controls", () => {
  const { getByRole, queryByRole, queryByText } = render(createElement(App));

  // The real player shell and its three views remain present.
  assert.ok(getByRole("heading", { name: "Gotham: The Goon" }));
  assert.ok(getByRole("tab", { name: "The Streets" }));
  assert.ok(getByRole("tab", { name: "My Life" }));
  assert.ok(getByRole("tab", { name: "My Story" }));

  // No QA scenario menu, section label, or individual controls in player mode.
  assert.equal(queryByRole("button", { name: "Stable life" }), null);
  assert.equal(queryByRole("button", { name: "Financial pressure" }), null);
  assert.equal(queryByRole("button", { name: "Uncertain information" }), null);
  assert.equal(queryByText(/Developer Preview/), null);
  assert.equal(queryByText(/QA scenarios/), null);

  // The developer entry control stays available.
  assert.ok(getByRole("button", { name: "Developer Inspection" }));
});

test("entering Developer Inspection reveals all three QA scenarios", () => {
  const { getByRole, getByText } = render(createElement(App));

  fireEvent.click(getByRole("button", { name: "Developer Inspection" }));

  assert.ok(getByText(/Developer Preview/));
  assert.ok(getByText(/QA scenarios/));
  assert.ok(getByRole("button", { name: "Stable life" }));
  assert.ok(getByRole("button", { name: "Financial pressure" }));
  assert.ok(getByRole("button", { name: "Uncertain information" }));

  // Default fixture is selected on entry.
  assert.equal(
    getByRole("button", { name: "Stable life" }).getAttribute("aria-pressed"),
    "true",
  );
  assert.equal(
    getByRole("button", { name: "Financial pressure" }).getAttribute("aria-pressed"),
    "false",
  );
  assert.equal(
    getByRole("button", { name: "Uncertain information" }).getAttribute("aria-pressed"),
    "false",
  );

  // The developer badge + exit control are visible.
  assert.ok(getByText("Developer Inspection Mode"));
  assert.ok(getByRole("button", { name: "Exit Developer Inspection" }));
});

test("scenario selection works and survives exiting and re-entering Developer Inspection", () => {
  const { getByRole, getByText, queryByRole, queryByText } = render(createElement(App));

  // Enter developer mode and select Financial pressure.
  fireEvent.click(getByRole("button", { name: "Developer Inspection" }));
  fireEvent.click(getByRole("button", { name: "Financial pressure" }));
  assert.equal(
    getByRole("button", { name: "Financial pressure" }).getAttribute("aria-pressed"),
    "true",
  );

  // The pressure fixture is what's actually on screen (cash $11, housing overdue).
  fireEvent.click(getByRole("tab", { name: "My Life" }));
  assert.ok(getByText("$11"), "pressure cash should be displayed");
  assert.ok(getByText("overdue"), "pressure housing status should be displayed");

  // Exiting hides the controls but keeps the selected fixture on screen.
  fireEvent.click(getByRole("button", { name: "Exit Developer Inspection" }));
  assert.equal(queryByRole("button", { name: "Stable life" }), null);
  assert.equal(queryByRole("button", { name: "Financial pressure" }), null);
  assert.equal(queryByRole("button", { name: "Uncertain information" }), null);
  assert.equal(queryByText(/QA scenarios/), null);
  assert.ok(getByText("$11"), "selected fixture must survive leaving developer mode");

  // Re-entering restores the controls with the same selected fixture.
  fireEvent.click(getByRole("button", { name: "Developer Inspection" }));
  assert.equal(
    getByRole("button", { name: "Financial pressure" }).getAttribute("aria-pressed"),
    "true",
  );
  assert.equal(
    getByRole("button", { name: "Stable life" }).getAttribute("aria-pressed"),
    "false",
  );
});
