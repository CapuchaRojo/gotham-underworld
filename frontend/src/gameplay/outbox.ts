// Durable request outbox for exactly-once command submission.
//
// GTG-19 scope: persist the exact seven-field CommandRequest in IndexedDB BEFORE
// any network transmission, keep one unresolved mutation per career+lineage
// across cooperating tabs (a read/write IndexedDB transaction is the lock), and
// recover a lost acknowledgment by the ORIGINAL request_id â€” never by
// reconstructing the envelope from current UI selections.
//
// A lost acknowledgment is treated as uncertain, not failed: once the envelope
// is durably persisted, a transport reset or unreadable/HTML/500 response leaves
// the record `transmitted` and only `recover()` (GET /api/v1/operations/{id})
// decides committed vs not_found. The authoritative revision is judged AFTER
// that lookup: a committed operation is recovered even when the revision has
// advanced, while a not_found operation may retry only when the original
// revision still matches (no rollback suspected).

import type {
  Command,
  CommandRequest,
  EngineEnvelope,
  OperationResponse,
  Receipt,
} from "./wire";
import { validateCommandRequest, validateEngineEnvelope, validateOperationResponse } from "./wire";
import { validStoredRecord, requireOutboxSchema } from "./outboxRecord";
import type { HostClient, HostFailure } from "./host";

export type OutboxRecordStatus =
  | "persisted"
  | "transmitted"
  | "committed"
  | "quarantined"
  | "superseded";

export interface OutboxRecord {
  request_id: string;
  /** `${career_id}\u0000${lineage_id}` â€” the scope of the exactly-once lock. */
  scope: string;
  career_id: string;
  lineage_id: string;
  /** The exact seven-field envelope â€” immutable once persisted. */
  envelope: CommandRequest;
  status: OutboxRecordStatus;
  receipt: Receipt | null;
  created_at: number;
  updated_at: number;
  last_error: string | null;
}

export type OutboxOutcome =
  | { kind: "committed"; requestId: string; receipt: Receipt; envelope: EngineEnvelope }
  | { kind: "outcome_uncertain"; requestId: string; message: string }
  | { kind: "stale_revision"; requestId: string; message: string }
  | { kind: "request_id_reused"; requestId: string; message: string }
  | { kind: "wrong_career"; requestId: string; message: string }
  | { kind: "quarantined"; requestId: string; message: string }
  | { kind: "storage_unavailable"; message: string }
  | { kind: "storage_failure"; message: string }
  | { kind: "conflicting_intent"; requestId: string; message: string }
  | { kind: "reauthorize_required"; requestId: string; message: string }
  | { kind: "adapter_defect"; code: string; message: string }
  | { kind: "nothing_to_recover" };

export interface OutboxSubmitInput {
  careerId: string;
  lineageId: string;
  /** Observed authoritative revision the command is built against. */
  revision: number;
  command: Command;
  arguments: Record<string, string>;
  capability: string;
}

export interface OutboxRecoverInput {
  /** The ORIGINAL request_id stored in the outbox (never a freshly generated one). */
  requestId: string;
  /** Fresh authoritative identity/revision, revalidated before any retry. */
  careerId: string;
  lineageId: string;
  revision: number;
  capability: string;
}

export interface Outbox {
  submit(input: OutboxSubmitInput): Promise<OutboxOutcome>;
  recover(input: OutboxRecoverInput): Promise<OutboxOutcome>;
}

export interface OutboxDeps {
  idbFactory?: IDBFactory;
  newRequestId?: () => string;
}

const DB_NAME = "goon.outbox.v1";
const STORE = "mutations";
const SCOPE_INDEX = "scope";

/** Only these statuses hold the per-scope exactly-once lock. */
const UNRESOLVED: readonly OutboxRecordStatus[] = ["persisted", "transmitted", "quarantined"];

class ConflictError extends Error {}

function scopeKey(careerId: string, lineageId: string): string {
  return `${careerId}\u0000${lineageId}`;
}

function describeError(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  return "Durable storage failed.";
}

function failureMessage(failure: HostFailure): string {
  if (failure.kind === "transport") return failure.message;
  if (failure.kind === "validation") return `host response invalid: ${failure.message}`;
  return failure.message;
}

/**
 * Generate a transport request_id matching [A-Za-z0-9][A-Za-z0-9._-]{0,127}.
 * `crypto.randomUUID()` (36 lowercase hex/hyphen chars) satisfies the pattern;
 * a fallback of 32 lowercase hex chars also satisfies it.
 */
export function generateRequestId(): string {
  const cryptoObj = globalThis.crypto;
  if (cryptoObj && typeof cryptoObj.randomUUID === "function") {
    return cryptoObj.randomUUID();
  }
  const bytes = new Uint8Array(16);
  if (cryptoObj && typeof cryptoObj.getRandomValues === "function") {
    cryptoObj.getRandomValues(bytes);
  } else {
    for (let i = 0; i < bytes.length; i += 1) {
      bytes[i] = Math.floor(Math.random() * 256);
    }
  }
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

// ---------------------------------------------------------------------------
// IndexedDB primitives
// ---------------------------------------------------------------------------

function openDatabase(factory: IDBFactory): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    let request: IDBOpenDBRequest;
    try {
      request = factory.open(DB_NAME, 1);
    } catch (error) {
      reject(error);
      return;
    }
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE)) {
        const store = db.createObjectStore(STORE, { keyPath: "request_id" });
        store.createIndex(SCOPE_INDEX, "scope", { unique: false });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB open failed"));
    request.onblocked = () => reject(new Error("IndexedDB open blocked"));
  });
}

function writeRecord(db: IDBDatabase, record: OutboxRecord): Promise<void> {
  return new Promise((resolve, reject) => {
    let tx: IDBTransaction;
    try {
      tx = db.transaction(STORE, "readwrite");
    } catch (error) {
      reject(error);
      return;
    }
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error("IndexedDB write failed"));
    tx.onabort = () => reject(tx.error ?? new Error("IndexedDB write aborted"));
    try {
      tx.objectStore(STORE).put(record);
    } catch (error) {
      reject(error);
    }
  });
}

function readRecord(db: IDBDatabase, requestId: string): Promise<OutboxRecord | null> {
  return new Promise((resolve, reject) => {
    let tx: IDBTransaction;
    try {
      tx = db.transaction(STORE, "readonly");
    } catch (error) {
      reject(error);
      return;
    }
    tx.onerror = () => reject(tx.error ?? new Error("IndexedDB read failed"));
    tx.onabort = () => reject(tx.error ?? new Error("IndexedDB read aborted"));
    let request: IDBRequest;
    try {
      const store = tx.objectStore(STORE);
      requireOutboxSchema(store);
      request = store.get(requestId);
    } catch (error) {
      reject(error);
      return;
    }
    let row: OutboxRecord | null = null;
    request.onsuccess = () => {
      if (request.result !== undefined && !validStoredRecord(request.result)) {
        tx.abort(); reject(new Error("Malformed stored intent")); return;
      }
      row = request.result ?? null;
    };
    tx.oncomplete = () => resolve(row);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB read failed"));
  });
}

/**
 * Persist a NEW record, using a read/write transaction as the exactly-once lock.
 * Rejects with `ConflictError` when another unresolved mutation already exists
 * for the same career+lineage scope (and therefore nothing is written).
 */
function persistNew(db: IDBDatabase, record: OutboxRecord): Promise<void> {
  return new Promise((resolve, reject) => {
    let tx: IDBTransaction;
    try {
      tx = db.transaction(STORE, "readwrite");
    } catch (error) {
      reject(error);
      return;
    }
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error("IndexedDB transaction failed"));
    tx.onabort = () => reject(tx.error ?? new Error("IndexedDB transaction aborted"));

    let store: IDBObjectStore;
    try {
      store = tx.objectStore(STORE);
    } catch (error) {
      reject(error);
      return;
    }

    requireOutboxSchema(store);
    const existingReq = store.getAll();
    existingReq.onsuccess = () => {
      const rows = existingReq.result as OutboxRecord[];
      if (rows.some(row => !validStoredRecord(row))) {
        tx.abort(); reject(new Error("Outbox contains malformed records; operator review required.")); return;
      }
      const conflict = rows.some((row) => row.scope === record.scope && (UNRESOLVED as readonly string[]).includes(row.status));
      if (conflict) {
        try {
          tx.abort();
        } catch {
          // Already ending.
        }
        reject(
          new ConflictError(
            `another unresolved command already exists for ${record.career_id}/${record.lineage_id}`,
          ),
        );
        return;
      }
      try {
        store.add(record);
      } catch (error) {
        reject(error);
      }
    };
    existingReq.onerror = () =>
      reject(existingReq.error ?? new Error("IndexedDB index read failed"));
  });
}

/** Best-effort status bookkeeping; the durable envelope is already committed. */
async function markStatus(
  db: IDBDatabase,
  record: OutboxRecord,
  patch: {
    status: OutboxRecordStatus;
    lastError?: string | null;
    receipt?: Receipt | null;
  },
): Promise<void> {
  const updated: OutboxRecord = {
    ...record,
    status: patch.status,
    receipt: patch.receipt !== undefined ? patch.receipt : record.receipt,
    last_error: patch.lastError !== undefined ? patch.lastError : record.last_error,
    updated_at: Date.now(),
  };
  try {
    await writeRecord(db, updated);
  } catch {
    // A failed status write leaves the record recoverable via the original ID;
    // recovery re-queries the host and re-records the outcome.
  }
}

// ---------------------------------------------------------------------------
// Envelope construction
// ---------------------------------------------------------------------------

type EnvelopeBuild =
  | { ok: true; value: CommandRequest }
  | { ok: false; code: string; message: string };

function buildEnvelope(input: OutboxSubmitInput, requestId: string): EnvelopeBuild {
  const envelope: CommandRequest = {
    protocol_version: 1,
    career_id: input.careerId,
    lineage_id: input.lineageId,
    request_id: requestId,
    expected_revision: input.revision,
    command: input.command,
    arguments: input.arguments,
  };
  const check = validateCommandRequest(envelope);
  if (!check.ok) return { ok: false, code: check.error.code, message: check.error.message };
  return { ok: true, value: check.value };
}

// ---------------------------------------------------------------------------
// Outbox
// ---------------------------------------------------------------------------

export function createOutbox(host: HostClient, deps: OutboxDeps = {}): Outbox {
  const factory = deps.idbFactory ?? globalThis.indexedDB;
  const newRequestId = deps.newRequestId ?? generateRequestId;

  function responseBound(record: OutboxRecord, response: EngineEnvelope): boolean {
    const receipt = response.receipt;
    return response.career_id === record.career_id && response.lineage_id === record.lineage_id &&
      response.revision >= record.envelope.expected_revision && (!receipt ||
      (receipt.request_id === record.request_id && receipt.command === record.envelope.command &&
       receipt.revision === record.envelope.expected_revision + 1 && receipt.revision <= response.revision));
  }
  const unbound = { kind: "validation", code: "invalid_value", path: "$",
    message: "Response is not bound to the original intent; outcome remains uncertain." } as const;

  async function settlePost(
    db: IDBDatabase,
    record: OutboxRecord,
    result: Awaited<ReturnType<HostClient["postCommand"]>>,
  ): Promise<OutboxOutcome> {
    if (result.ok) {
      if (!validateEngineEnvelope(result.value).ok || !responseBound(record, result.value))
        return failureAfterTransmit(db, record, unbound);
      const receipt = result.value.receipt;
      if (receipt) {
        await markStatus(db, record, { status: "committed", receipt, lastError: null });
        return {
          kind: "committed",
          requestId: record.request_id,
          receipt,
          envelope: result.value,
        };
      }
      await markStatus(db, record, {
        status: "transmitted",
        lastError: "command response carried no receipt",
      });
      return {
        kind: "outcome_uncertain",
        requestId: record.request_id,
        message: "The command response carried no receipt â€” outcome is uncertain.",
      };
    }
    return failureAfterTransmit(db, record, result.failure);
  }

  async function failureAfterTransmit(
    db: IDBDatabase,
    record: OutboxRecord,
    failure: HostFailure,
  ): Promise<OutboxOutcome> {
    if (failure.kind === "host_error") {
      switch (failure.code) {
        case "STALE_REVISION":
          await markStatus(db, record, { status: "superseded", lastError: failure.message });
          return {
            kind: "stale_revision",
            requestId: record.request_id,
            message: failure.message,
          };
        case "REQUEST_ID_REUSED":
          // Stop â€” never replace the persisted payload.
          await markStatus(db, record, { status: "quarantined", lastError: failure.message });
          return {
            kind: "request_id_reused",
            requestId: record.request_id,
            message: failure.message,
          };
        case "WRONG_CAREER":
          await markStatus(db, record, { status: "quarantined", lastError: failure.message });
          return {
            kind: "wrong_career",
            requestId: record.request_id,
            message: failure.message,
          };
        case "UNAUTHORIZED":
          // Retain the pending intent; recovery resumes after re-pairing.
          await markStatus(db, record, { status: "transmitted", lastError: failure.message });
          return {
            kind: "reauthorize_required",
            requestId: record.request_id,
            message: failure.message,
          };
        case "OUTCOME_UNKNOWN":
          await markStatus(db, record, { status: "transmitted", lastError: failure.message });
          return {
            kind: "outcome_uncertain",
            requestId: record.request_id,
            message: failure.message,
          };
        case "INVALID_REQUEST":
        case "INVALID_ARGUMENTS":
        case "COMMAND_NOT_ALLOWED":
        case "COMMAND_REJECTED":
        case "ROUTE_UNAVAILABLE":
          // Definitively rejected before any effect â€” the envelope will never commit.
          await markStatus(db, record, { status: "superseded", lastError: failure.message });
          return { kind: "adapter_defect", code: failure.code, message: failure.message };
        default:
          // Anything else after transmission is uncertain, never an inferred failure.
          await markStatus(db, record, { status: "transmitted", lastError: failure.message });
          return {
            kind: "outcome_uncertain",
            requestId: record.request_id,
            message: failure.message,
          };
      }
    }

    // Transport or validation: cannot distinguish "never sent" from "ack lost".
    const message = failureMessage(failure);
    await markStatus(db, record, { status: "transmitted", lastError: message });
    return { kind: "outcome_uncertain", requestId: record.request_id, message };
  }

  async function settleOperation(
    db: IDBDatabase,
    record: OutboxRecord,
    op: OperationResponse,
    input: OutboxRecoverInput,
  ): Promise<OutboxOutcome> {
    if (!validateOperationResponse(op).ok || !responseBound(record, op) ||
        (op.operation_status === "not_found" && op.receipt !== null))
      return failureAfterRecovery(db, record, unbound);
    if (op.operation_status === "committed") {
      // Committed is authoritative even when the authoritative revision has
      // advanced past `expected_revision`: the command took effect, so record
      // the ORIGINAL receipt and reconcile the current state. Never re-POST.
      const receipt = op.receipt;
      if (receipt) {
        await markStatus(db, record, { status: "committed", receipt, lastError: null });
        return {
          kind: "committed",
          requestId: record.request_id,
          receipt,
          envelope: op,
        };
      }
      await markStatus(db, record, {
        status: "transmitted",
        lastError: "committed operation carried no receipt",
      });
      return {
        kind: "outcome_uncertain",
        requestId: record.request_id,
        message: "The committed operation carried no receipt â€” outcome is uncertain.",
      };
    }

    // not_found. A retry is safe ONLY when the original revision still matches
    // (and therefore no rollback is suspected). If the authoritative revision
    // advanced while the operation is not_found, the host moved on WITHOUT this
    // command â€” the original decision is stale and must never be replayed.
    if (record.receipt !== null) return failureAfterRecovery(db, record, unbound);
    if (record.envelope.expected_revision !== input.revision || record.envelope.expected_revision !== op.revision) {
      await markStatus(db, record, {
        status: "superseded",
        lastError: "revision changed during recovery",
      });
      return {
        kind: "stale_revision",
        requestId: record.request_id,
        message: "Revision advanced â€” a fresh decision is required.",
      };
    }

    // not_found with a matching revision â†’ retry the EXACT original envelope
    // (original request_id, payload, expected_revision, and arguments).
    const posted = await host.postCommand(input.capability, record.envelope);
    return settlePost(db, record, posted);
  }

  async function failureAfterRecovery(
    db: IDBDatabase,
    record: OutboxRecord,
    failure: HostFailure,
  ): Promise<OutboxOutcome> {
    if (failure.kind === "host_error" && failure.code === "UNAUTHORIZED") {
      await markStatus(db, record, { status: record.receipt !== null ? "committed" : "transmitted", lastError: failure.message });
      return {
        kind: "reauthorize_required",
        requestId: record.request_id,
        message: failure.message,
      };
    }
    const message = failureMessage(failure);
    await markStatus(db, record, { status: record.receipt !== null ? "committed" : "transmitted", lastError: message });
    return { kind: "outcome_uncertain", requestId: record.request_id, message };
  }

  return {
    async submit(input) {
      const requestId = newRequestId();
      const built = buildEnvelope(input, requestId);
      if (!built.ok) {
        return { kind: "adapter_defect", code: built.code, message: built.message };
      }

      let db: IDBDatabase;
      try {
        db = await openDatabase(factory);
      } catch {
        return {
          kind: "storage_unavailable",
          message: "Durable storage is unavailable â€” no command will be sent.",
        };
      }

      const record: OutboxRecord = {
        request_id: requestId,
        scope: scopeKey(input.careerId, input.lineageId),
        career_id: input.careerId,
        lineage_id: input.lineageId,
        envelope: built.value,
        status: "persisted",
        receipt: null,
        created_at: Date.now(),
        updated_at: Date.now(),
        last_error: null,
      };

      try {
        try {
          await persistNew(db, record);
        } catch (error) {
          if (error instanceof ConflictError) {
            return {
              kind: "conflicting_intent",
              requestId,
              message: error.message,
            };
          }
          return { kind: "storage_failure", message: describeError(error) };
        }

        // Durably committed â€” only now transmit.
        const posted = await host.postCommand(input.capability, built.value);
        return await settlePost(db, record, posted);
      } finally {
        db.close();
      }
    },

    async recover(input) {
      let db: IDBDatabase;
      try {
        db = await openDatabase(factory);
      } catch {
        return {
          kind: "storage_unavailable",
          message: "Durable storage is unavailable â€” recovery is blocked.",
        };
      }

      try {
        let record: OutboxRecord | null;
        try {
          record = await readRecord(db, input.requestId);
        } catch {
          return { kind: "storage_failure", message: "The outbox could not be read for recovery." };
        }
        if (!record) return { kind: "nothing_to_recover" };
        if (record.status === "quarantined") return { kind: "quarantined", requestId: record.request_id, message: "Operator review is required for this quarantined intent." };
        if (record.status === "superseded") return { kind: "stale_revision", requestId: record.request_id, message: "This intent was superseded and cannot be retried." };

        // 1. Validate career/lineage identity BEFORE any host lookup or retry.
        if (record.career_id !== input.careerId || record.lineage_id !== input.lineageId) {
          await markStatus(db, record, {
            status: "quarantined",
            lastError: "career/lineage mismatch during recovery",
          });
          return {
            kind: "quarantined",
            requestId: record.request_id,
            message: "The pending operation belongs to a different career/lineage.",
          };
        }

        // 2. Look up the ORIGINAL request_id BEFORE judging the revision. A
        // command that committed and advanced the revision must recover as
        // committed (record receipt + reconcile state), never be mistaken for a
        // stale decision.
        const op = await host.getOperation(input.capability, record.request_id);
        if (op.ok) return settleOperation(db, record, op.value, input);
        return failureAfterRecovery(db, record, op.failure);
      } finally {
        db.close();
      }
    },
  };
}
