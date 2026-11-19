import { test } from "node:test";
import assert from "node:assert/strict";
import { IDBFactory } from "fake-indexeddb";
import { createOutbox, generateRequestId } from "../src/gameplay/outbox";
import type { OutboxRecoverInput, OutboxSubmitInput } from "../src/gameplay/outbox";
import type { HostClient, HostFailure, HostResult } from "../src/gameplay/host";
import type {
  CommandRequest,
  EngineEnvelope,
  OperationResponse,
  Receipt,
} from "../src/gameplay/wire";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const INPUT: OutboxSubmitInput = {
  careerId: "career.a1",
  lineageId: "lineage.1",
  revision: 0,
  command: "wait",
  arguments: {},
  capability: "A".repeat(43),
};

function recoverInput(overrides: Partial<OutboxRecoverInput> = {}): OutboxRecoverInput {
  return {
    requestId: "req.1",
    careerId: INPUT.careerId,
    lineageId: INPUT.lineageId,
    revision: INPUT.revision,
    capability: INPUT.capability,
    ...overrides,
  };
}

const RECEIPT: Receipt = {
  request_id: "req.1",
  revision: 1,
  command_sequence: 1,
  command: "wait",
  day: 1,
  status: "committed",
};

function makeEnvelope(overrides: Partial<EngineEnvelope> = {}): EngineEnvelope {
  return {
    protocol_version: 1,
    career_id: "career.a1",
    lineage_id: "lineage.1",
    revision: 1,
    allowed_commands: ["wait", "settle_in"],
    receipt: RECEIPT,
    duplicate: false,
    state: {
      day: 1,
      player: { cash: 40, heat: 0, custody: "free" },
      budgets: {
        daily_actions: 3,
        actions_remaining: 3,
        daily_travel_units: 18,
        travel_units_remaining: null,
      },
      location: null,
      systems: {
        navigation: "not_adopted",
        daily_life: "not_adopted",
        ordinary: "not_adopted",
        mobility: "not_adopted",
      },
      housing: null,
      contacts: [],
      opportunities: [],
      outcomes: [],
    },
    ...overrides,
  };
}

const COMMITTED_ENVELOPE = makeEnvelope();
const COMMITTED_OPERATION: OperationResponse = {
  ...COMMITTED_ENVELOPE,
  operation_status: "committed",
};
const NOT_FOUND_OPERATION: OperationResponse = {
  ...makeEnvelope({ receipt: null, revision: 0 }),
  operation_status: "not_found",
};

function okResult<T>(value: T): HostResult<T> {
  return { ok: true, value };
}

function hostError(code: string, http: number, message: string): HostFailure {
  return { kind: "host_error", code, http, message, action: null };
}

const transportFailure = (message = "connection reset"): HostResult<never> => ({
  ok: false,
  failure: { kind: "transport", message },
});

function makeHost(impl: Partial<HostClient>): HostClient {
  return {
    bootstrap: impl.bootstrap ?? (async () => {
      throw new Error("unexpected bootstrap");
    }),
    getSession: impl.getSession ?? (async () => {
      throw new Error("unexpected getSession");
    }),
    getState: impl.getState ?? (async () => {
      throw new Error("unexpected getState");
    }),
    postCommand: impl.postCommand ?? (async () => {
      throw new Error("unexpected postCommand");
    }),
    getOperation: impl.getOperation ?? (async () => {
      throw new Error("unexpected getOperation");
    }),
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

async function waitFor(predicate: () => boolean, timeoutMs = 2000): Promise<void> {
  const start = Date.now();
  while (!predicate()) {
    if (Date.now() - start > timeoutMs) throw new Error("timed out waiting");
    await new Promise((resolve) => setTimeout(resolve, 5));
  }
}

// ---------------------------------------------------------------------------
// Request ID
// ---------------------------------------------------------------------------

test("generateRequestId produces IDs matching [A-Za-z0-9][A-Za-z0-9._-]{0,127}", () => {
  for (let i = 0; i < 100; i += 1) {
    assert.match(generateRequestId(), /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/);
  }
});

// ---------------------------------------------------------------------------
// No command on mount / reload
// ---------------------------------------------------------------------------

test("constructing the outbox never submits or recovers (no command on mount/reload)", async () => {
  let posts = 0;
  let ops = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return okResult(COMMITTED_ENVELOPE);
    },
    getOperation: async () => {
      ops += 1;
      return okResult(COMMITTED_OPERATION);
    },
  });

  createOutbox(host, { idbFactory: new IDBFactory(), newRequestId: () => "req.1" });

  // Let any stray microtasks/macrotasks run.
  await new Promise((resolve) => setTimeout(resolve, 10));
  assert.equal(posts, 0);
  assert.equal(ops, 0);
});

// ---------------------------------------------------------------------------
// Storage failure blocks transmission
// ---------------------------------------------------------------------------

test("unavailable IndexedDB blocks the command (never falls back to a volatile request)", async () => {
  let posts = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return okResult(COMMITTED_ENVELOPE);
    },
  });
  const unavailable = {
    open: () => {
      throw new Error("indexedDB disabled");
    },
  } as unknown as IDBFactory;

  const outbox = createOutbox(host, { idbFactory: unavailable, newRequestId: () => "req.1" });
  const result = await outbox.submit(INPUT);

  assert.equal(result.kind, "storage_unavailable");
  assert.equal(posts, 0);
});

test("a write failure during persistence blocks transmission", async () => {
  let posts = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return okResult(COMMITTED_ENVELOPE);
    },
  });
  const brokenWrite = {
    open: () => {
      const fakeDb = {
        objectStoreNames: { contains: () => false },
        createObjectStore: () => ({ createIndex: () => {} }),
        transaction: () => {
          throw new Error("cannot start write transaction");
        },
        close: () => {},
      };
      const request: Record<string, unknown> = { result: fakeDb };
      queueMicrotask(() => {
        if (typeof request.onupgradeneeded === "function") request.onupgradeneeded();
        if (typeof request.onsuccess === "function") request.onsuccess();
      });
      return request;
    },
  } as unknown as IDBFactory;

  const outbox = createOutbox(host, { idbFactory: brokenWrite, newRequestId: () => "req.1" });
  const result = await outbox.submit(INPUT);

  assert.equal(result.kind, "storage_failure");
  assert.equal(posts, 0);
});

// A read/write transaction is atomic: a failed first write rolls back cleanly,
// so a later submit (same store) proceeds with no leftover blocking record.
function makeFactoryFailingFirstTransaction(): IDBFactory {
  const real = new IDBFactory();
  let failNext = true;
  return {
    open: (name: string, version?: number) => {
      const request = real.open(name, version);
      return new Proxy(request, {
        get(target, prop, receiver) {
          if (prop === "result") {
            const db = Reflect.get(target, prop, receiver) as IDBDatabase | undefined;
            if (db) {
              return new Proxy(db, {
                get(dbTarget, dbProp, dbReceiver) {
                  if (dbProp === "transaction") {
                    return (...args: unknown[]) => {
                      if (failNext) {
                        failNext = false;
                        throw new Error("simulated write failure");
                      }
                      return (dbTarget as IDBDatabase).transaction(
                        ...(args as [string, IDBTransactionMode]),
                      );
                    };
                  }
                  const value = Reflect.get(dbTarget, dbProp, dbReceiver);
                  return typeof value === "function" ? value.bind(dbTarget) : value;
                },
              });
            }
            return db;
          }
          return Reflect.get(target, prop, receiver);
        },
      });
    },
  } as unknown as IDBFactory;
}

test("rollback: a failed write leaves no record and a later submit succeeds", async () => {
  let posts = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return okResult(COMMITTED_ENVELOPE);
    },
  });
  const factory = makeFactoryFailingFirstTransaction();
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  const first = await outbox.submit(INPUT);
  assert.equal(first.kind, "storage_failure");
  assert.equal(posts, 0);

  const second = await outbox.submit(INPUT);
  assert.equal(second.kind, "committed");
  assert.equal(posts, 1);
});

// ---------------------------------------------------------------------------
// Double-click + cross-tab single intent
// ---------------------------------------------------------------------------

test("double-click: a second submit while one is in flight is inert (single effect)", async () => {
  const gate = deferred<HostResult<EngineEnvelope>>();
  let posts = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return gate.promise;
    },
  });
  const outbox = createOutbox(host, {
    idbFactory: new IDBFactory(),
    newRequestId: () => "req.1",
  });

  const first = outbox.submit(INPUT);
  await waitFor(() => posts === 1);

  const second = await outbox.submit(INPUT);
  assert.equal(second.kind, "conflicting_intent");
  assert.equal(posts, 1);

  gate.resolve(okResult(COMMITTED_ENVELOPE));
  const firstResult = await first;
  assert.equal(firstResult.kind, "committed");
  assert.equal(posts, 1);
});

test("cross-tab: only one unresolved command per career+lineage across cooperating tabs", async () => {
  const factory = new IDBFactory();
  const gate = deferred<HostResult<EngineEnvelope>>();
  let posts = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return gate.promise;
    },
  });

  const tabA = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.tabA" });
  const tabB = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.tabB" });

  const first = tabA.submit(INPUT);
  await waitFor(() => posts === 1);

  const second = await tabB.submit(INPUT);
  assert.equal(second.kind, "conflicting_intent");
  assert.equal(posts, 1);

  gate.resolve(okResult(makeEnvelope({ receipt: { ...RECEIPT, request_id: "req.tabA" } })));
  assert.equal((await first).kind, "committed");
  assert.equal(posts, 1);
});

// ---------------------------------------------------------------------------
// Lost acknowledgments â†’ recovery by original request_id
// ---------------------------------------------------------------------------

test("lost ack: committed recovery by original id applies state without re-transmitting", async () => {
  const factory = new IDBFactory();
  let posts = 0;
  let ops = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return transportFailure("connection reset");
    },
    getOperation: async () => {
      ops += 1;
      return okResult(COMMITTED_OPERATION);
    },
  });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  const submitResult = await outbox.submit(INPUT);
  assert.equal(submitResult.kind, "outcome_uncertain");
  assert.equal(posts, 1);

  const recovered = await outbox.recover(recoverInput());
  assert.equal(recovered.kind, "committed");
  if (recovered.kind === "committed") {
    assert.equal(recovered.requestId, "req.1");
    assert.equal(recovered.receipt.request_id, "req.1");
    assert.equal(recovered.envelope.state.day, 1);
  }
  assert.equal(ops, 1);
  assert.equal(posts, 1); // identical lost-ack recovered without a duplicate effect
});

test("lost ack: not_found recovery retries the EXACT original envelope", async () => {
  const factory = new IDBFactory();
  let posts = 0;
  let lastPosted: CommandRequest | null = null;
  const host = makeHost({
    postCommand: async (_capability, request) => {
      posts += 1;
      lastPosted = request;
      if (posts === 1) return transportFailure("connection reset");
      return okResult(COMMITTED_ENVELOPE);
    },
    getOperation: async () => okResult(NOT_FOUND_OPERATION),
  });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  await outbox.submit(INPUT);
  const recovered = await outbox.recover(recoverInput());

  assert.equal(recovered.kind, "committed");
  assert.equal(posts, 2);
  assert.ok(lastPosted);
  assert.equal(lastPosted!.request_id, "req.1");
  assert.equal(lastPosted!.expected_revision, 0);
  assert.equal(lastPosted!.command, "wait");
  assert.deepEqual(lastPosted!.arguments, {});
});

// ---------------------------------------------------------------------------
// Stale revision / wrong lineage / host restart
// ---------------------------------------------------------------------------

test("stale revision on submit: refresh then a new decision (envelope never rewritten)", async () => {
  const factory = new IDBFactory();
  const host = makeHost({
    postCommand: async () => ({ ok: false, failure: hostError("STALE_REVISION", 409, "stale") }),
  });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  const result = await outbox.submit(INPUT);
  assert.equal(result.kind, "stale_revision");
});

test("committed operation after revision advancement is recovered without re-transmitting", async () => {
  const factory = new IDBFactory();
  let posts = 0;
  let ops = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return transportFailure("connection reset");
    },
    getOperation: async () => {
      ops += 1;
      return okResult(COMMITTED_OPERATION);
    },
  });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  await outbox.submit(INPUT); // ack lost at revision 0

  // The command committed and advanced the authoritative revision to 1, but the
  // browser lost the acknowledgment. Recovery must accept the committed receipt
  // and reconcile current state â€” never mistake it for a stale decision.
  const result = await outbox.recover(recoverInput({ revision: 1 }));
  assert.equal(result.kind, "committed");
  if (result.kind === "committed") {
    assert.equal(result.requestId, "req.1");
    assert.equal(result.receipt.request_id, "req.1");
    assert.equal(result.receipt.revision, 1);
    assert.equal(result.envelope.revision, 1);
  }
  assert.equal(ops, 1);
  assert.equal(posts, 1); // a committed lookup must never result in another POST
});

test("not_found with an advanced revision requires a fresh decision and never retries", async () => {
  const factory = new IDBFactory();
  let posts = 0;
  let ops = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return transportFailure("connection reset");
    },
    getOperation: async () => {
      ops += 1;
      return okResult(NOT_FOUND_OPERATION);
    },
  });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  await outbox.submit(INPUT); // ack lost at revision 0

  // Revision advanced but the operation was never found: the host moved on
  // WITHOUT this command. Do NOT replay the original envelope.
  const result = await outbox.recover(recoverInput({ revision: 1 }));
  assert.equal(result.kind, "stale_revision");
  assert.equal(ops, 1); // looked up BEFORE judging the revision
  assert.equal(posts, 1); // never retried
});

test("wrong lineage during recovery quarantines the pending intent", async () => {
  const factory = new IDBFactory();
  let posts = 0;
  let ops = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      return transportFailure();
    },
    getOperation: async () => {
      ops += 1;
      return okResult(COMMITTED_OPERATION);
    },
  });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  await outbox.submit(INPUT);

  const result = await outbox.recover(recoverInput({ lineageId: "lineage.OTHER" }));
  assert.equal(result.kind, "quarantined");
  assert.equal(ops, 0);
  assert.equal(posts, 1);
});

test("host restart: UNAUTHORIZED retains the pending intent for recovery after re-pair", async () => {
  const factory = new IDBFactory();
  let posts = 0;
  let ops = 0;
  const host = makeHost({
    postCommand: async () => {
      posts += 1;
      if (posts === 1) return { ok: false, failure: hostError("UNAUTHORIZED", 401, "rotated") };
      return okResult(COMMITTED_ENVELOPE);
    },
    getOperation: async () => {
      ops += 1;
      return okResult(COMMITTED_OPERATION);
    },
  });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });

  const submitResult = await outbox.submit(INPUT);
  assert.equal(submitResult.kind, "reauthorize_required");

  // Re-pair with a fresh capability, then recover the SAME original request.
  const recovered = await outbox.recover(recoverInput({ capability: "B".repeat(43) }));
  assert.equal(recovered.kind, "committed");
  assert.equal(ops, 1);
  assert.equal(posts, 1); // no duplicate transmit
});


// Stabilization regressions: durable state and response binding.
async function editStored(factory: IDBFactory, change: (row: any) => void) {
  const db = await new Promise<IDBDatabase>((resolve, reject) => {
    const req = factory.open("goon.outbox.v1", 1); req.onsuccess = () => resolve(req.result); req.onerror = () => reject(req.error);
  });
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction("mutations", "readwrite"); const store = tx.objectStore("mutations");
    const req = store.get("req.1"); req.onsuccess = () => { change(req.result); store.put(req.result); };
    tx.oncomplete = () => resolve(); tx.onerror = () => reject(tx.error);
  }); db.close();
}
test("request ID collision never replaces an already committed envelope", async () => {
  let posts = 0; const host = makeHost({ postCommand: async () => { posts++; return okResult(COMMITTED_ENVELOPE); } });
  const outbox = createOutbox(host, { idbFactory: new IDBFactory(), newRequestId: () => "req.1" });
  assert.equal((await outbox.submit(INPUT)).kind, "committed");
  assert.equal((await outbox.submit({ ...INPUT, revision: 1 })).kind, "storage_failure");
  assert.equal(posts, 1);
});
test("corrupt stored envelope cannot reach any recovery network call", async () => {
  const factory = new IDBFactory(); let lookups = 0;
  const host = makeHost({ postCommand: async () => transportFailure(), getOperation: async () => { lookups++; return okResult(COMMITTED_OPERATION); } });
  const outbox = createOutbox(host, { idbFactory: factory, newRequestId: () => "req.1" });
  await outbox.submit(INPUT); await editStored(factory, row => { row.envelope.request_id = "different"; });
  assert.equal((await outbox.recover(recoverInput())).kind, "storage_failure"); assert.equal(lookups, 0);
});
test("not_found uses the operation response revision as well as the caller revision", async () => {
  let posts = 0; const host = makeHost({ postCommand: async () => { posts++; return transportFailure(); },
    getOperation: async () => okResult({ ...NOT_FOUND_OPERATION, revision: 1 }) });
  const outbox = createOutbox(host, { idbFactory: new IDBFactory(), newRequestId: () => "req.1" });
  await outbox.submit(INPUT); assert.equal((await outbox.recover(recoverInput())).kind, "stale_revision"); assert.equal(posts, 1);
});
test("receipt for another request is never accepted as this command's success", async () => {
  const host = makeHost({ postCommand: async () => okResult(makeEnvelope({ receipt: { ...RECEIPT, request_id: "other" } })) });
  const outbox = createOutbox(host, { idbFactory: new IDBFactory(), newRequestId: () => "req.1" });
  assert.equal((await outbox.submit(INPUT)).kind, "outcome_uncertain");
});
test("operation from another lineage cannot settle a pending command", async () => {
  const host = makeHost({ postCommand: async () => transportFailure(), getOperation: async () => okResult({ ...COMMITTED_OPERATION, lineage_id: "other" }) });
  const outbox = createOutbox(host, { idbFactory: new IDBFactory(), newRequestId: () => "req.1" });
  await outbox.submit(INPUT); assert.equal((await outbox.recover(recoverInput())).kind, "outcome_uncertain");
});
test("superseded records cannot be resubmitted by later recovery", async () => {
  let posts = 0; const host = makeHost({ postCommand: async () => { posts++; return { ok: false, failure: hostError("STALE_REVISION", 409, "stale") }; }, getOperation: async () => okResult(NOT_FOUND_OPERATION) });
  const outbox = createOutbox(host, { idbFactory: new IDBFactory(), newRequestId: () => "req.1" });
  await outbox.submit(INPUT); await outbox.recover(recoverInput()); assert.equal(posts, 1);
});

test("a previously committed intent is never replayed after repeated missing-operation lookups", async () => {
  let posts = 0;
  const host = makeHost({ postCommand: async () => { posts++; return okResult(COMMITTED_ENVELOPE); }, getOperation: async () => okResult(NOT_FOUND_OPERATION) });
  const outbox = createOutbox(host, { idbFactory: new IDBFactory(), newRequestId: () => "req.1" });
  assert.equal((await outbox.submit(INPUT)).kind, "committed");
  assert.equal((await outbox.recover(recoverInput())).kind, "outcome_uncertain");
  assert.equal((await outbox.recover(recoverInput())).kind, "outcome_uncertain");
  assert.equal(posts, 1);
});
