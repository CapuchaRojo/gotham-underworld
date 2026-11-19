import "./dom";
import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import ts from "typescript";
import { createElement } from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";
import { TodayView } from "../src/components/TodayView";
import { OpportunityInteraction } from "../src/components/OpportunityInteraction";
import { OpportunityInteractionDemo } from "../src/components/OpportunityInteractionDemo";
import { SCENARIOS } from "../src/fixtures";
import { GATED_STOCK_AUDIT, OPENING_REPAIR_SHIFT, SYNTHETIC_TAKE_OPTION_ID, toInteractionView } from "../src/gameplay/interaction";
import { relativeDays } from "../src/relativeTime";

const root = fileURLToPath(new URL("../../", import.meta.url));
const read = (name: string) => readFileSync(resolve(root, name), "utf8").replaceAll("\r\n", "\n");
afterEach(() => cleanup());

test("GTG-26 preserves the reviewed host, outbox, session, CSP and Python core", () => {
  const hashes = JSON.parse(read("frontend/tests/gtg26-protected-core.json")) as Record<string, string>;
  for (const [name, expected] of Object.entries(hashes))
    assert.equal(createHash("sha256").update(read(name)).digest("hex"), expected, `${name}: core changes require separate review`);
});

function graph(entry: string): Map<string, ts.SourceFile> {
  const visited = new Map<string, ts.SourceFile>();
  function visit(name: string) {
    if (visited.has(name)) return;
    const source = ts.createSourceFile(name, readFileSync(name, "utf8"), ts.ScriptTarget.Latest, true, name.endsWith(".tsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
    visited.set(name, source);
    for (const node of source.statements) {
      if (!ts.isImportDeclaration(node) && !ts.isExportDeclaration(node)) continue;
      if (ts.isImportDeclaration(node) && node.importClause?.isTypeOnly) continue;
      if (ts.isExportDeclaration(node) && node.isTypeOnly) continue;
      const spec = node.moduleSpecifier;
      if (!spec || !ts.isStringLiteral(spec)) continue;
      if (!spec.text.startsWith(".")) { assert.ok(["react", "react-dom/client"].includes(spec.text), name); continue; }
      if (spec.text.endsWith(".css")) { assert.equal(spec.text, "./index.css"); continue; }
      const base = resolve(dirname(name), spec.text);
      const dependency = [base + ".ts", base + ".tsx", resolve(base, "index.ts")].find(existsSync);
      assert.ok(dependency, `unresolved import ${spec.text}`);
      visit(dependency);
    }
  }
  visit(resolve(root, entry));
  return visited;
}

test("pure interaction graph has no reachable transport, network or persistent storage API", () => {
  const forbidden = new Set(["fetch", "XMLHttpRequest", "WebSocket", "localStorage", "sessionStorage", "indexedDB", "sendBeacon"]);
  for (const [name, source] of graph("frontend/src/components/OpportunityInteractionDemo.tsx")) {
    assert.doesNotMatch(name.replaceAll("\\", "/"), /\/(?:host|outbox|liveEngine|LiveEngineProvider|inspectionHost)\./);
    function inspect(node: ts.Node) {
      if (ts.isIdentifier(node)) assert.ok(!forbidden.has(node.text), `${name}: ${node.text}`);
      if (ts.isCallExpression(node)) assert.notEqual(node.expression.kind, ts.SyntaxKind.ImportKeyword, "no hidden dynamic transport import");
      ts.forEachChild(node, inspect);
    }
    inspect(source);
  }
});

test("local entry has no preview/interaction dependency and preview has no live host route", () => {
  for (const name of graph("frontend/src/local-main.tsx").keys())
    assert.doesNotMatch(name.replaceAll("\\", "/"), /\/interaction\/|\/OpportunityInteraction|\/fixtures\.ts|\/preview\.ts|\/App\.tsx$/);
  for (const name of graph("frontend/src/main.tsx").keys())
    assert.doesNotMatch(name.replaceAll("\\", "/"), /\/(?:host|outbox|liveEngine|LiveEngineProvider|LocalHostApp|inspectionHost)\./);
  assert.doesNotMatch(read("frontend/src/main.tsx"), /URLSearchParams|engine=live|location\.search/);
});

test("opening terms and late audit agree with authoritative Python content", () => {
  const content = JSON.parse(read("content/neighborhood_life_v1.json"));
  const opening = content.choices.opening_shift;
  assert.equal(OPENING_REPAIR_SHIFT.options.length, opening.options.length);
  assert.equal(OPENING_REPAIR_SHIFT.expires_day - OPENING_REPAIR_SHIFT.open_day, opening.duration);
  assert.equal(OPENING_REPAIR_SHIFT.situation, opening.situation);
  for (const offer of [OPENING_REPAIR_SHIFT, GATED_STOCK_AUDIT]) {
    assert.match(offer.id, /^preview\./);
    assert.equal(offer.command, "choose");
    for (const option of offer.options) {
      assert.match(option.id, /^preview\./);
      assert.deepEqual(Object.keys(option.arguments).sort(), ["choice_id", "option_id"]);
      assert.equal(option.arguments.choice_id, offer.id);
      assert.equal(option.arguments.option_id, option.id);
    }
  }
  for (const option of OPENING_REPAIR_SHIFT.options) {
    const authored = opening.options.find((row: {id: string}) => option.id.endsWith(`.${row.id}`));
    assert.ok(authored);
    assert.equal(option.label, authored.label);
    assert.equal(option.action_cost, authored.actions);
    if (authored.pay) assert.ok(option.tradeoff.includes(`$${authored.pay}`));
  }
  const audit = content.choices.late_work.options.find((x: {id: string}) => x.id === "audit");
  assert.equal(audit.place, "goon.poi.p032");
  assert.equal(audit.known, "tess_reference");
  assert.equal(GATED_STOCK_AUDIT.options[0].action_cost, audit.actions);
  assert.ok(GATED_STOCK_AUDIT.options[0].reason?.includes(`standing ${audit.minimum_standing}`));
  assert.ok(GATED_STOCK_AUDIT.options[0].tradeoff.includes(`$${audit.pay}`));
  assert.equal(SCENARIOS[0].contacts.find(x => x.id === "contact.tess")?.role, content.contacts["goon.contact.tess"].role);
  assert.equal(SCENARIOS[0].contacts.find(x => x.id === "contact.marlon")?.role, "Store owner, Upper East Side");
});

test("Today interaction is absent without explicit preview opt-in", () => {
  const view = render(createElement(TodayView, { scenario: SCENARIOS[0] }));
  assert.equal(view.queryByRole("group", {name: /Preview interaction state/}), null);
  view.rerender(createElement(TodayView, { scenario: SCENARIOS[0], showInteractionPreview: true }));
  assert.ok(view.getByRole("group", {name: /Preview interaction state/}));
});

test("transmitted uncertainty offers no Cancel and Escape cannot imply undo", () => {
  let cancelled = 0;
  const model = toInteractionView(OPENING_REPAIR_SHIFT, "pending", {selectedOptionId: SYNTHETIC_TAKE_OPTION_ID, pendingStatus: "outcome_uncertain"});
  const view = render(createElement(OpportunityInteraction, { model, callbacks: {onCancel: () => cancelled++} }));
  assert.ok(view.getByText(/Transmitted, outcome uncertain/));
  assert.equal(view.queryByRole("button", {name: /Cancel|Confirm|retry/i}), null);
  fireEvent.keyDown(view.container.querySelector("section")!, {key: "Escape"});
  assert.equal(cancelled, 0);
});

test("Confirm stays hard disabled even if a caller requests enablement", () => {
  let confirmed = 0;
  const model = {...toInteractionView(OPENING_REPAIR_SHIFT, "pending", {selectedOptionId: SYNTHETIC_TAKE_OPTION_ID}), submissionDisabled: false};
  const view = render(createElement(OpportunityInteraction, {model, callbacks: {onConfirm: () => confirmed++}}));
  const button = view.getByRole("button", {name: /Confirm:/}) as HTMLButtonElement;
  assert.ok(button.disabled);
  fireEvent.click(button);
  assert.equal(confirmed, 0);
  assert.equal(toInteractionView(OPENING_REPAIR_SHIFT, "choices", {submissionDisabled: false, syntheticLabel: "live"}).submissionDisabled, true);
});

test("missing selection IDs and suppressed missing-data overrides fail closed", () => {
  const model = toInteractionView(OPENING_REPAIR_SHIFT, "pending", {selectedOptionId: "preview.unknown", missingData: []});
  assert.ok(model.missingData.includes("selected option"));
  const view = render(createElement(OpportunityInteraction, {model}));
  assert.ok(view.getByText(/Unavailable/));
  assert.equal(view.queryByRole("button"), null);
});

test("unavailable options cannot invoke selection and undiscovered details stay hidden", () => {
  let selected = 0;
  const view = render(createElement(OpportunityInteraction, {model: toInteractionView(GATED_STOCK_AUDIT, "choices"), callbacks: {onSelectOption: () => selected++}}));
  const option = view.getByRole("button", {name: /Use Tess/}) as HTMLButtonElement;
  assert.ok(option.disabled);
  fireEvent.click(option);
  assert.equal(selected, 0);
  view.rerender(createElement(OpportunityInteraction, {model: toInteractionView(OPENING_REPAIR_SHIFT, "undiscovered")}));
  assert.ok(!view.container.textContent?.includes("Tess Navarro"));
  assert.ok(!view.container.textContent?.includes("Uptown General Store"));
});

test("preview transitions and input projection leave fixtures unchanged", () => {
  const before = JSON.stringify({SCENARIOS, OPENING_REPAIR_SHIFT, GATED_STOCK_AUDIT});
  const view = render(createElement(OpportunityInteractionDemo));
  fireEvent.click(view.getByRole("button", {name: /Work the repair shift/}));
  fireEvent.click(view.getByRole("button", {name: /Show uncertain/}));
  fireEvent.keyDown(view.container.querySelector("section")!, {key: "Escape"});
  assert.ok(view.getByText(/Transmitted, outcome uncertain/));
  assert.equal(JSON.stringify({SCENARIOS, OPENING_REPAIR_SHIFT, GATED_STOCK_AUDIT}), before);
});

test("relative due wording handles today, tomorrow, future and overdue dates", () => {
  assert.deepEqual([3,4,6,2,1].map(day => relativeDays(3,day)), ["due today","due tomorrow","in 3 days","1 day overdue","2 days overdue"]);
});

test("confidence wording does not invent the number of sources", () => {
  const source = read("frontend/src/components/StoryView.tsx");
  assert.ok(source.includes("Confidence labels do not establish source count"));
  assert.ok(!source.includes("single") && !source.includes("exactly one"));
});
