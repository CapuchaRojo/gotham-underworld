// Transport storage validation only; never reconstruct or repair an intent.
import type { OutboxRecord } from "./outbox";
import { validateCommandRequest } from "./wire";
export function validStoredRecord(value: unknown): value is OutboxRecord {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const row = value as OutboxRecord;
  const keys = ["request_id", "scope", "career_id", "lineage_id", "envelope", "status", "receipt", "created_at", "updated_at", "last_error"];
  if (Object.keys(row).length !== keys.length || keys.some(k => !Object.hasOwn(row, k))) return false;
  const checked = validateCommandRequest(row.envelope);
  if (!checked.ok) return false;
  const e = checked.value;
  if (row.request_id !== e.request_id || row.career_id !== e.career_id || row.lineage_id !== e.lineage_id ||
      row.scope !== `${e.career_id}\u0000${e.lineage_id}`) return false;
  if (!["persisted", "transmitted", "committed", "quarantined", "superseded"].includes(row.status) ||
      !Number.isSafeInteger(row.created_at) || row.created_at < 0 || !Number.isSafeInteger(row.updated_at) || row.updated_at < row.created_at ||
      (row.last_error !== null && typeof row.last_error !== "string")) return false;
  const receipt = row.receipt;
  if (receipt === null) return row.status !== "committed";
  if (!receipt || typeof receipt !== "object" || Object.keys(receipt).length !== 6) return false;
  return receipt.request_id === e.request_id && receipt.command === e.command && receipt.status === "committed" &&
    receipt.revision === e.expected_revision + 1 && Number.isSafeInteger(receipt.command_sequence) && receipt.command_sequence >= receipt.revision &&
    Number.isSafeInteger(receipt.day) && receipt.day >= 0;
}

export function requireOutboxSchema(store: IDBObjectStore): void {
  const index = store.index("scope");
  if (store.keyPath !== "request_id" || store.autoIncrement || index.keyPath !== "scope" || index.unique || index.multiEntry)
    throw new Error("Unexpected outbox schema; operator review required.");
}
