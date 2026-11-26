import { validStoredRecord, requireOutboxSchema } from "./outboxRecord";
// Probe the existing transport store without creating requests or sending them.
export async function inspectOutboxStorage(factory: IDBFactory = indexedDB): Promise<number> {
  return new Promise((resolve, reject) => {
    const request = factory.open("goon.outbox.v1", 1);
    request.onupgradeneeded = () => {
      const store = request.result.createObjectStore("mutations", { keyPath: "request_id" });
      store.createIndex("scope", "scope", { unique: false });
    };
    request.onerror = () => reject(new Error("Outbox unavailable"));
    request.onblocked = () => reject(new Error("Outbox blocked"));
    request.onsuccess = () => {
      const db = request.result;
      try {
        const tx = db.transaction("mutations", "readonly");
        const store = tx.objectStore("mutations");
        requireOutboxSchema(store);
        const rows = store.getAll();
        tx.oncomplete = () => { db.close();
          if (rows.result.some(row => !validStoredRecord(row))) reject(new Error("Malformed outbox; records preserved"));
          else resolve(rows.result.length);
        };
        tx.onerror = tx.onabort = () => { db.close(); reject(new Error("Outbox read failed")); };
      } catch (error) { db.close(); reject(error); }
    };
  });
}
