import { test } from "node:test";
import assert from "node:assert/strict";
import { findLiveTransportTokens, readSource } from "./sourceScan";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { SCENARIO_BY_ID } from "../src/fixtures";
import {
  GATED_STOCK_AUDIT,
  INTERACTION_STATES,
  OPENING_REPAIR_SHIFT,
  OPENING_REPAIR_SHIFT_SPEAKER,
  PREVIEW_INTERACTION_DEMOS,
  PREVIEW_INTERACTION_STORYBOARD,
  SYNTHETIC_PREVIEW_LABEL,
  previewOpportunityAdapter,
  toInteractionView,
} from "../src/gameplay/interaction";

// ---------------------------------------------------------------------------
// Character authority — Tess Navarro speaks; Marlon is not merged.
// ---------------------------------------------------------------------------

test("opening repair shift is spoken by Tess Navarro", () => {
  assert.equal(OPENING_REPAIR_SHIFT.speaker, "Tess Navarro");
  assert.equal(OPENING_REPAIR_SHIFT_SPEAKER, "Tess Navarro");
  assert.equal(PREVIEW_INTERACTION_DEMOS.choices.speaker, "Tess Navarro");
});

test("Marlon is not merged into Tess's role (both identities stay distinct)", () => {
  const stable = SCENARIO_BY_ID.get("stable")!;
  const marlon = stable.contacts.find((c) => c.id === "contact.marlon")!;
  const tess = stable.contacts.find((c) => c.id === "contact.tess")!;

  // Fixture identities are untouched...
  assert.equal(marlon.name, "Marlon");
  assert.equal(marlon.role, "Store owner, Upper East Side");
  assert.equal(tess.role, "Repair worker and cooperative coordinator");

  // ...and the interaction's speaker is not Marlon, nor Tess renamed to a
  // store-owner role.
  assert.notEqual(OPENING_REPAIR_SHIFT.speaker, marlon.name);
  assert.ok(!/store owner/i.test(OPENING_REPAIR_SHIFT_SPEAKER));
});

// ---------------------------------------------------------------------------
// Wire-shape fidelity — mirror Opportunity/OpportunityOption, no schema change.
// ---------------------------------------------------------------------------

test("authored scenario mirrors the wire Opportunity/OpportunityOption fields", () => {
  const opportunityKeys = [
    "id",
    "title",
    "situation",
    "speaker",
    "open_day",
    "expires_day",
    "state",
    "command",
    "options",
  ].sort();
  assert.deepEqual(Object.keys(OPENING_REPAIR_SHIFT).sort(), opportunityKeys);

  const optionKeys = [
    "id",
    "label",
    "availability",
    "reason",
    "action_cost",
    "tradeoff",
    "arguments",
  ].sort();
  for (const option of OPENING_REPAIR_SHIFT.options) {
    assert.deepEqual(Object.keys(option).sort(), optionKeys);
    // Daily-life `choose` arguments carry choice_id + option_id.
    assert.equal(OPENING_REPAIR_SHIFT.command, "choose");
    assert.ok("choice_id" in option.arguments && "option_id" in option.arguments);
  }
});

test("view-model mirrors wire field names through the adapter", () => {
  const view = previewOpportunityAdapter.toView(OPENING_REPAIR_SHIFT, "choices");
  assert.equal(view.opportunityId, OPENING_REPAIR_SHIFT.id);
  assert.equal(view.openDay, OPENING_REPAIR_SHIFT.open_day);
  assert.equal(view.expiresDay, OPENING_REPAIR_SHIFT.expires_day);
  assert.equal(view.engineState, OPENING_REPAIR_SHIFT.state);

  const wireOption = OPENING_REPAIR_SHIFT.options[0];
  const viewOption = view.options[0];
  assert.equal(viewOption.id, wireOption.id);
  assert.equal(viewOption.label, wireOption.label);
  assert.equal(viewOption.actionCost, wireOption.action_cost);
  assert.equal(viewOption.tradeoff, wireOption.tradeoff);
  assert.equal(viewOption.available, wireOption.availability === "available");
});

test("the interaction module never imports a live transport or calls fetch", () => {
  for (const file of ["adapter.ts", "scenario.ts", "types.ts", "constants.ts", "index.ts"]) {
    const source = readSource(`../src/gameplay/interaction/${file}`);
    const offending = findLiveTransportTokens(source);
    assert.deepEqual(offending, [], `${file} must not reference ${offending.join(", ")}`);
  }
});

// ---------------------------------------------------------------------------
// The eight presentation states.
// ---------------------------------------------------------------------------

test("exactly eight canonical presentation states are authored", () => {
  assert.equal(INTERACTION_STATES.length, 8);
  assert.equal(new Set(INTERACTION_STATES).size, 8);
  assert.deepEqual(
    [...INTERACTION_STATES].sort(),
    Object.keys(PREVIEW_INTERACTION_DEMOS).sort(),
  );
  assert.equal(PREVIEW_INTERACTION_STORYBOARD.length, 8);
});

test("every authored demo carries the synthetic label and disables submission", () => {
  for (const state of INTERACTION_STATES) {
    const model = PREVIEW_INTERACTION_DEMOS[state];
    assert.equal(model.state, state);
    assert.equal(model.syntheticLabel, SYNTHETIC_PREVIEW_LABEL);
    assert.equal(model.submissionDisabled, true);
    assert.deepEqual(model.missingData, []);
  }
});

test("undiscovered surfaces no options", () => {
  assert.deepEqual(PREVIEW_INTERACTION_DEMOS.undiscovered.options, []);
});

test("eligibility shows a blocked offer with its player-safe reason", () => {
  const view = toInteractionView(GATED_STOCK_AUDIT, "eligibility");
  assert.deepEqual(view.blockReasons, [GATED_STOCK_AUDIT.options[0].reason]);
  assert.equal(view.options[0].available, false);
  assert.equal(view.options[0].reason, GATED_STOCK_AUDIT.options[0].reason);
});

test("states that reference a selected option expose it; the rest do not", () => {
  for (const state of ["pending", "confirmed", "rejected", "consequence"] as const) {
    assert.ok(PREVIEW_INTERACTION_DEMOS[state].selectedOptionId, `${state} needs a selection`);
  }
  assert.equal(PREVIEW_INTERACTION_DEMOS.choices.selectedOptionId, null);
  assert.equal(PREVIEW_INTERACTION_DEMOS.undiscovered.selectedOptionId, null);
});

test("consequence/confirmed demos expose authored aftermath feedback", () => {
  assert.ok(PREVIEW_INTERACTION_DEMOS.consequence.consequenceFeedback);
  assert.ok(PREVIEW_INTERACTION_DEMOS.confirmed.consequenceFeedback);
  // Choices have no aftermath.
  assert.equal(PREVIEW_INTERACTION_DEMOS.choices.consequenceFeedback, null);
});

// ---------------------------------------------------------------------------
// Alternate paths: missing data, purity.
// ---------------------------------------------------------------------------

test("missing required offer fields surface an explicit missing-data list", () => {
  const incomplete = { ...OPENING_REPAIR_SHIFT, title: "", options: [] };
  const view = toInteractionView(incomplete, "choices");
  assert.ok(view.missingData.includes("title"));
  assert.ok(view.missingData.includes("options"));
});

test("a selected-option state without a selection is flagged, not invented", () => {
  const view = toInteractionView(OPENING_REPAIR_SHIFT, "confirmed");
  assert.equal(view.selectedOptionId, null);
  assert.ok(view.missingData.includes("selected option"));
});

test("the adapter is pure and never mutates its input", () => {
  const before = JSON.stringify(OPENING_REPAIR_SHIFT);
  const a = toInteractionView(OPENING_REPAIR_SHIFT, "choices");
  const b = toInteractionView(OPENING_REPAIR_SHIFT, "choices");
  assert.deepEqual(a, b);
  assert.equal(JSON.stringify(OPENING_REPAIR_SHIFT), before);
});

// ---------------------------------------------------------------------------
// Smoke: the demos are directly renderable as visible text.
// ---------------------------------------------------------------------------

test("each presentation state renders as visible, non-empty markup", () => {
  for (const state of INTERACTION_STATES) {
    const model = PREVIEW_INTERACTION_DEMOS[state];
    const html = renderToStaticMarkup(
      createElement("div", { "data-state": state }, [
        createElement("span", { key: "label" }, model.syntheticLabel),
        createElement("strong", { key: "title" }, model.title),
      ]),
    );
    assert.ok(html.includes(SYNTHETIC_PREVIEW_LABEL), `${state} should surface the label`);
    assert.ok(html.includes(model.title), `${state} should surface the offer title`);
  }
});
