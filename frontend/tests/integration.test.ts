import "./dom";
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { IDBFactory } from "fake-indexeddb";
import { createInspectionHostClient, IDENTITY_KEY } from "../src/gameplay/inspectionHost";
import { inspectOutboxStorage } from "../src/gameplay/inspectionStorage";
import { CLIENT_BUNDLE_ID } from "../src/gameplay/host";
import { ENGINE_RELEASE } from "../src/gameplay/wire";
import { readFileSync } from "node:fs";

Object.defineProperty(globalThis, "sessionStorage", { value: window.sessionStorage, configurable: true });
afterEach(() => window.sessionStorage.clear());
const session = { host_protocol_version: 1, bridge_protocol_version: 1, bundle_id: CLIENT_BUNDLE_ID,
  manifest_sha256: "a".repeat(64), engine_release: ENGINE_RELEASE, instance_id: "instance1",
  mode: "local_engine", session_lifetime: "process" };
function envelope() {
  return { protocol_version: 1, career_id: "career1", lineage_id: "lineage1", revision: 2,
    allowed_commands: ["wait"], receipt: null, duplicate: false,
    state: { day: 2, player: { cash: 40, heat: 0, custody: "free" },
      budgets: { daily_actions: 3, actions_remaining: 3, daily_travel_units: 18, travel_units_remaining: null },
      location: null, housing: null, contacts: [], opportunities: [], outcomes: [],
      systems: { navigation: "not_adopted", daily_life: "not_adopted", ordinary: "not_adopted", mobility: "not_adopted" } } };
}
function client(body: unknown, calls: string[] = []) {
  return createInspectionHostClient({ fetchImpl: (async (path: string) => {
    calls.push(path); return new Response(JSON.stringify(body), { status: 200 });
  }) as typeof fetch });
}

test("inspection transport blocks all command transmission", async () => {
  const calls: string[] = [];
  const result = await client({}, calls).postCommand("A".repeat(43), {
    protocol_version: 1, career_id: "career1", lineage_id: "lineage1", request_id: "blocked",
    expected_revision: 2, command: "wait", arguments: {} });
  assert.equal(result.ok, false); assert.equal(calls.length, 0);
});
test("bootstrap verifies authenticated session before promotion", async () => {
  const calls: string[] = [];
  const host = createInspectionHostClient({ fetchImpl: (async (path: string) => {
    calls.push(path); return new Response(JSON.stringify(path.includes("bootstrap") ?
      { ...session, capability: "A".repeat(43) } : session));
  }) as typeof fetch });
  assert.equal((await host.bootstrap("B".repeat(43))).ok, true);
  assert.deepEqual(calls, ["/host/v1/bootstrap", "/host/v1/session"]);
});
test("authenticated metadata mismatch fails closed", async () => {
  const host = createInspectionHostClient({ fetchImpl: (async (path: string) => new Response(JSON.stringify(
    path.includes("bootstrap") ? { ...session, capability: "A".repeat(43) } : { ...session, instance_id: "different" }))) as typeof fetch });
  assert.equal((await host.bootstrap("B".repeat(43))).ok, false);
});
test("identity binding survives a new client after reload", async () => {
  assert.equal((await client(envelope()).getState("cap")).ok, true);
  assert.equal((await client(envelope()).getState("cap")).ok, true);
  assert.equal((await client({ ...envelope(), lineage_id: "other" }).getState("cap")).ok, false);
});
test("revision rollback and malformed identity storage fail closed", async () => {
  await client(envelope()).getState("cap");
  assert.equal((await client({ ...envelope(), revision: 1 }).getState("cap")).ok, false);
  sessionStorage.setItem(IDENTITY_KEY, "not json");
  assert.equal((await client(envelope()).getState("cap")).ok, false);
});
test("original-ID lookup is GET only and never retries a missing request", async () => {
  await client(envelope()).getState("cap");
  const calls: string[] = [];
  const result = await client({ ...envelope(), operation_status: "not_found" }, calls).getOperation("cap", "original-id");
  assert.equal(result.ok, true); assert.deepEqual(calls, ["/api/v1/operations/original-id"]);
});
test("outbox schema is persistent and inspection does not create requests", async () => {
  const factory = new IDBFactory();
  assert.equal(await inspectOutboxStorage(factory), 0);
  assert.equal(await inspectOutboxStorage(factory), 0);
});
test("separate source entries cannot escalate preview by query or environment", () => {
  const preview = readFileSync(new URL("../src/main.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(preview, /LiveInspectionApp|local-main|VITE_ENGINE|URLSearchParams|postMessage/);
  const local = readFileSync(new URL("../src/local-main.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(local, /fixtures|preview|\.\/App["']/);
  assert.match(local, /LocalHostApp/);
});


test("operation reads cannot roll back the last inspected revision", async () => {
  await client(envelope()).getState("cap");
  assert.equal((await client({ ...envelope(), revision: 1, operation_status: "not_found" }).getOperation("cap", "original-id")).ok, false);
});
test("operation reads advance the stored revision floor", async () => {
  await client(envelope()).getState("cap");
  assert.equal((await client({ ...envelope(), revision: 3, operation_status: "not_found" }).getOperation("cap", "original-id")).ok, true);
  assert.equal((await client(envelope()).getState("cap")).ok, false);
});
test("outbox inspection rejects malformed durable rows without deleting them", async () => {
  const factory = new IDBFactory(); await inspectOutboxStorage(factory);
  const db = await new Promise<IDBDatabase>(resolve => { const req = factory.open("goon.outbox.v1", 1); req.onsuccess = () => resolve(req.result); });
  await new Promise<void>(resolve => { const tx = db.transaction("mutations", "readwrite"); tx.objectStore("mutations").put({request_id:"broken",status:"transmitted"}); tx.oncomplete = () => resolve(); });
  db.close(); await assert.rejects(inspectOutboxStorage(factory)); await assert.rejects(inspectOutboxStorage(factory));
});

test("inspection rejects an incompatible IndexedDB key schema", async () => {
  const factory = new IDBFactory();
  const db = await new Promise<IDBDatabase>(resolve => {
    const req = factory.open("goon.outbox.v1", 1);
    req.onupgradeneeded = () => { const store = req.result.createObjectStore("mutations", {keyPath:"other"}); store.createIndex("scope", "scope"); };
    req.onsuccess = () => resolve(req.result);
  });
  db.close(); await assert.rejects(inspectOutboxStorage(factory));
});
