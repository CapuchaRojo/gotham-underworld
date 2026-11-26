import { createHostClient, HOUSING_BUNDLE_ID } from "./host";
import type { HostClientOptions, HousingHostClient, HostResult } from "./host";
import { bindHostReads } from "./inspectionHost";
import { ID_PATTERN, validateCommandRequest } from "./wire";
import type { HousingScope } from "./wire";

const HOUSING_IDENTITY_KEY = "goon.housing.identity.v1";

function identityMatches(scope: HousingScope, exactRevision: boolean): boolean {
  try {
    const saved = JSON.parse(sessionStorage.getItem(HOUSING_IDENTITY_KEY) ?? "null");
    return !!saved && saved.career_id === scope.career_id && saved.lineage_id === scope.lineage_id &&
      Number.isSafeInteger(saved.revision) && saved.revision >= 0 &&
      (exactRevision ? scope.revision === saved.revision : scope.revision >= saved.revision);
  } catch {
    return false;
  }
}

function bindHousingResult<T extends HousingScope>(result: HostResult<T>): HostResult<T> {
  if (!result.ok || identityMatches(result.value, false)) return result;
  return { ok: false, failure: { kind: "validation", code: "invalid_value", path: "$",
    message: "Housing data is not bound to the paired career and revision." } };
}

export function createHousingHostClient(options: HostClientOptions = {}): HousingHostClient {
  const host = bindHostReads(createHostClient(options, HOUSING_BUNDLE_ID), HOUSING_IDENTITY_KEY);
  return {
    ...host,
    async getHousing(capability) {
      return bindHousingResult(await host.getHousing(capability));
    },
    async getHousingOperation(capability, requestId) {
      const result = bindHousingResult(await host.getHousingOperation(capability, requestId));
      if (!result.ok || result.value.receipt.request_id === requestId) return result;
      return { ok: false, failure: { kind: "validation", code: "invalid_value", path: "$.receipt.request_id",
        message: "Housing receipt belongs to a different request." } };
    },
    async getOperation(capability, requestId) {
      if (!ID_PATTERN.test(requestId) || /[^A-Za-z0-9._-]/.test(requestId)) {
        return { ok: false, failure: { kind: "validation", code: "invalid_id", path: "$",
          message: "Invalid original request ID." } };
      }
      return host.getOperation(capability, requestId);
    },
    async postCommand(capability, request) {
      const validated = validateCommandRequest(request);
      if (!validated.ok || request.command !== "pay_room" || Object.keys(request.arguments).length !== 0) {
        return { ok: false, failure: { kind: "host_error", code: "COMMAND_NOT_ALLOWED", http: 400,
          message: "This Housing build only accepts the rent payment command.", action: null } };
      }
      if (!identityMatches({ ...request, revision: request.expected_revision }, true)) {
        return { ok: false, failure: { kind: "host_error", code: "STALE_REVISION", http: 409,
          message: "The payment does not match the paired career and revision.", action: null } };
      }
      return host.postCommand(capability, validated.value);
    },
  };
}
