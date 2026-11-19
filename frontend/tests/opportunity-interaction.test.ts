import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import "./dom";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { OpportunityInteraction } from "../src/components/OpportunityInteraction";
import { OpportunityInteractionDemo } from "../src/components/OpportunityInteractionDemo";
import {
  INTERACTION_STATES,
  OPENING_REPAIR_SHIFT,
  PREVIEW_INTERACTION_DEMOS,
  SYNTHETIC_PREVIEW_LABEL,
  toInteractionView,
} from "../src/gameplay/interaction";
import type { InteractionState } from "../src/gameplay/interaction";
import { findLiveTransportTokens, readSource } from "./sourceScan";

afterEach(() => cleanup());

function markup(state: InteractionState): string {
  return renderToStaticMarkup(
    createElement(OpportunityInteraction, { model: PREVIEW_INTERACTION_DEMOS[state] }),
  );
}

// Accessible-name fragments that uniquely identify the first and second option
// (their labels share a prefix, so the tradeoff text is used instead).
const FIRST_OPTION = /Work the repair shift/i;
const SECOND_OPTION = /Decline this shift/i;

// ---------------------------------------------------------------------------
// Each of the eight states renders in isolation with distinct, visible content.
// ---------------------------------------------------------------------------

const STATE_MARKER: Record<InteractionState, string> = {
  undiscovered: "surfaced yet",
  eligibility: "Not open to you",
  choices: "Your options",
  refusal: "Decline selected — not submitted.",
  pending: "Confirm is disabled",
  confirmed: "Outcome — demonstration only.",
  rejected: "Not accepted.",
  consequence: "Nothing here is persisted.",
};

test("all eight presentation states render their distinct content in isolation", () => {
  for (const state of INTERACTION_STATES) {
    const html = markup(state);
    assert.ok(html.includes(`data-state="${state}"`), `${state} should expose its state`);
    assert.ok(html.includes(STATE_MARKER[state]), `${state} should show "${STATE_MARKER[state]}"`);
    // Every authored surface carries the synthetic label.
    assert.ok(html.includes(SYNTHETIC_PREVIEW_LABEL), `${state} should carry the synthetic label`);
    // Never leaks a fabricated wage.
    assert.ok(!/wage (?:was )?paid:|cash (?:increased|earned)/i.test(html), `${state} must not fabricate a wage receipt`);
  }
});

test("the eight states are mutually distinguishable (no marker bleeds across states)", () => {
  const marks = Object.entries(STATE_MARKER) as [InteractionState, string][];
  for (const [state, marker] of marks) {
    const html = markup(state);
    assert.ok(html.includes(marker));
    for (const [other, otherMarker] of marks) {
      if (other === state) continue;
      assert.ok(!html.includes(otherMarker), `${state} must not render ${other}'s marker "${otherMarker}"`);
    }
  }
});

test("the eligibility state surfaces its player-safe block reason", () => {
  assert.ok(markup("eligibility").includes("Tess Navarro requires standing 2"));
});

test("the pending state confirms nothing was submitted and disables confirm", () => {
  const html = markup("pending");
  assert.ok(html.includes("not submitted"));
  assert.ok(html.includes("Confirm is disabled"));
  assert.ok(html.includes("disabled"), "the confirm affordance must be disabled");
});

test("the confirmed state is explicitly demonstration-only and shows no real effects", () => {
  const html = markup("confirmed");
  assert.ok(html.includes("demonstration only"));
  assert.ok(html.includes("no wages were paid"));
  assert.ok(!/\$[0-9]/.test(html));
});

// ---------------------------------------------------------------------------
// Missing-data path — never synthesise.
// ---------------------------------------------------------------------------

test("missing required fields render an explicit unavailable state, never invented data", () => {
  const model = { ...PREVIEW_INTERACTION_DEMOS.choices, title: "", missingData: ["title", "options"] };
  const html = renderToStaticMarkup(createElement(OpportunityInteraction, { model }));
  assert.ok(html.includes("data not provided"));
  assert.ok(html.includes("title"));
  assert.ok(html.includes("options"));
  // No selectable option is fabricated.
  assert.ok(!html.includes("Work the shift"));
});

test("a selected-option state without a selection is treated as missing data", () => {
  const model = toInteractionView({ ...OPENING_REPAIR_SHIFT, options: [] }, "confirmed");
  assert.ok(model.missingData.includes("options"));
  assert.ok(model.missingData.includes("selected option"));
  const html = renderToStaticMarkup(createElement(OpportunityInteraction, { model }));
  assert.ok(html.includes("data not provided"));
});

// ---------------------------------------------------------------------------
// Interactive behaviour: cancellation and keyboard accessibility.
// ---------------------------------------------------------------------------

test("selecting an option moves to pending; cancelling returns to choices with no side effects", () => {
  const { container } = render(createElement(OpportunityInteractionDemo));
  const stateOf = () => container.querySelector("[data-state]")?.getAttribute("data-state");

  assert.equal(stateOf(), "choices");

  fireEvent.click(screen.getByRole("button", { name: FIRST_OPTION }));
  assert.equal(stateOf(), "pending");
  // Nothing was committed.
  assert.ok(!container.textContent?.includes("demonstration only"));

  fireEvent.click(screen.getByRole("button", { name: /Cancel/i }));
  assert.equal(stateOf(), "choices");
  assert.ok(screen.getByRole("button", { name: FIRST_OPTION }));
});

test("Escape cancels a pending decision and returns to choices", () => {
  const { container } = render(createElement(OpportunityInteractionDemo));
  fireEvent.click(screen.getByRole("button", { name: FIRST_OPTION }));
  const pending = container.querySelector('[data-state="pending"]')!;
  assert.ok(pending);

  fireEvent.keyDown(pending, { key: "Escape" });
  assert.equal(container.querySelector("[data-state]")?.getAttribute("data-state"), "choices");
});

test("the pending confirm affordance is disabled and marked aria-disabled", () => {
  render(createElement(OpportunityInteractionDemo));
  fireEvent.click(screen.getByRole("button", { name: FIRST_OPTION }));
  const confirm = screen.getByRole("button", { name: /Confirm:/i }) as HTMLButtonElement;
  assert.equal(confirm.disabled, true);
  assert.equal(confirm.getAttribute("aria-disabled"), "true");
});

test("options are native focusable buttons and the panel exposes a polite live region", () => {
  const { container } = render(createElement(OpportunityInteractionDemo));
  for (const label of [FIRST_OPTION, SECOND_OPTION]) {
    const btn = screen.getByRole("button", { name: label }) as HTMLButtonElement;
    assert.equal(btn.tagName, "BUTTON");
    assert.equal(btn.disabled, false);
  }
  const live = container.querySelector('[aria-live="polite"]');
  assert.ok(live, "a polite live region must announce state changes");
  assert.ok(live?.getAttribute("aria-atomic"), "the live region should be atomic");

  const section = container.querySelector("section[data-synthetic]");
  assert.ok(section?.getAttribute("aria-labelledby"), "the panel must be labelled");
});

test("focus moves into the panel on a state transition", () => {
  const { container } = render(createElement(OpportunityInteractionDemo));
  fireEvent.click(screen.getByRole("button", { name: FIRST_OPTION }));
  const section = container.querySelector("section[data-synthetic]")!;
  assert.ok(section.contains(document.activeElement), "focus should land inside the panel");
});

// ---------------------------------------------------------------------------
// Boundary: the presentational component never reaches the live path.
// ---------------------------------------------------------------------------

test("the interaction component imports no live transport and calls no fetch", () => {
  for (const file of [
    "../src/components/OpportunityInteraction.tsx",
    "../src/components/OpportunityInteractionDemo.tsx",
    "../src/components/interactionIcons.tsx",
  ]) {
    const offending = findLiveTransportTokens(readSource(file));
    assert.deepEqual(offending, [], `${file} must not reference ${offending.join(", ")}`);
  }
});
