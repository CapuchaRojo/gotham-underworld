// Read-only transport for this milestone. No submission or automatic retry path.
import { createHostClient } from "./host";
import type { HostClient, HostClientOptions, HostResult } from "./host";
import type { EngineEnvelope } from "./wire";
import { ID_PATTERN } from "./wire/constants";

export const IDENTITY_KEY = "goon.inspection.identity.v1";

export function createInspectionHostClient(options: HostClientOptions = {}): HostClient {
  const host = createHostClient(options);
  return {
    ...host,
    async bootstrap(code) {
      const result = await host.bootstrap(code);
      if (!result.ok) return result;
      const verified = await host.getSession(result.value.capability);
      if (!verified.ok) return verified;
      if (Object.entries(verified.value).some(([key, value]) =>
          result.value[key as keyof typeof result.value] !== value)) {
        return { ok: false, failure: { kind: "validation", code: "invalid_value", path: "$",
          message: "Authenticated session differs from bootstrap metadata." } };
      }
      return result;
    },
    async postCommand() {
      return { ok: false, failure: { kind: "host_error", code: "COMMAND_NOT_ALLOWED",
        http: 400, message: "Gameplay commands are disabled in this inspection build.", action: null } };
    },
    async getState(capability): Promise<HostResult<EngineEnvelope>> {
      const result = await host.getState(capability);
      if (!result.ok) return result;
      const value = result.value;
      try {
        const saved = sessionStorage.getItem(IDENTITY_KEY);
        if (saved) {
          const previous = JSON.parse(saved);
          if (previous.career_id !== value.career_id || previous.lineage_id !== value.lineage_id ||
              !Number.isSafeInteger(previous.revision) || value.revision < previous.revision) {
            return { ok: false, failure: { kind: "validation", code: "invalid_value", path: "$",
              message: "Career identity changed or revision rolled back. Operator review is required; pending requests must be preserved." } };
          }
        }
        sessionStorage.setItem(IDENTITY_KEY, JSON.stringify({ career_id: value.career_id,
          lineage_id: value.lineage_id, revision: value.revision }));
      } catch {
        return { ok: false, failure: { kind: "validation", code: "storage_unavailable", path: "$",
          message: "Identity storage is unavailable or malformed; inspection is blocked." } };
      }
      return result;
    },
    async getOperation(capability, requestId) {
      if (!ID_PATTERN.test(requestId)) {
        return { ok: false, failure: { kind: "validation", code: "invalid_id", path: "$",
          message: "Invalid original request ID." } };
      }
      const result = await host.getOperation(capability, requestId);
      if (!result.ok) return result;
      try {
        const bound = JSON.parse(sessionStorage.getItem(IDENTITY_KEY) ?? "null");
        if (!bound || result.value.career_id !== bound.career_id || result.value.lineage_id !== bound.lineage_id ||
            !Number.isSafeInteger(bound.revision) || bound.revision < 0 || result.value.revision < bound.revision ||
            (result.value.receipt && result.value.receipt.request_id !== requestId)) throw new Error();
        sessionStorage.setItem(IDENTITY_KEY, JSON.stringify({ career_id: result.value.career_id,
          lineage_id: result.value.lineage_id, revision: result.value.revision }));
      } catch {
        return { ok: false, failure: { kind: "validation", code: "invalid_value", path: "$",
          message: "Operation lookup is not bound to the inspected career and original request." } };
      }
      return result;
    },
  };
}
