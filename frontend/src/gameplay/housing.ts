import type { HousingHostClient } from "./host";
import type { EngineEnvelope, HousingResponse, HousingScope, HousingSettlement, Receipt } from "./wire";

export function sameCareer(left: HousingScope, right: HousingScope): boolean {
  return left.career_id === right.career_id && left.lineage_id === right.lineage_id;
}

export function sameHousingSnapshot(left: HousingScope, right: HousingScope): boolean {
  return sameCareer(left, right) && left.revision === right.revision;
}

export type HousingSnapshot = { state: EngineEnvelope; housing: HousingResponse };

export function canPayRoom(snapshot: HousingSnapshot): boolean {
  return snapshot.housing.pay_room === "eligible" &&
    snapshot.state.allowed_commands.includes("pay_room") &&
    Number.isSafeInteger(snapshot.state.state.player.cash) &&
    snapshot.state.revision < Number.MAX_SAFE_INTEGER;
}

export async function readHousing(host: HousingHostClient, capability: string) {
  const [state, housing] = await Promise.all([host.getState(capability), host.getHousing(capability)]);
  if (!state.ok) return state;
  if (!housing.ok) return housing;
  if (!sameHousingSnapshot(state.value, housing.value) || state.value.receipt !== null) {
    return { ok: false, failure: { kind: "transport", message: "Housing and current state could not be matched. Refresh to try again." } } as const;
  }
  return { ok: true, value: { state: state.value, housing: housing.value } } as const;
}

export async function readPaymentDetail(
  host: HousingHostClient, capability: string, scope: HousingScope, receipt: Receipt,
) {
  const detail = await host.getHousingOperation(capability, receipt.request_id);
  if (!detail.ok) return detail;
  const original = detail.value.receipt;
  const settlement: HousingSettlement | undefined = detail.value.settlements[0];
  if (!sameCareer(scope, detail.value) || detail.value.revision < scope.revision ||
      original.request_id !== receipt.request_id || original.revision !== receipt.revision ||
      original.day !== receipt.day || original.command_sequence !== receipt.command_sequence ||
      original.command !== "pay_room" || receipt.command !== "pay_room" ||
      detail.value.settlements.length !== 1 || !settlement ||
      settlement.kind === "due" || settlement.day !== receipt.day) {
    return { ok: false, failure: { kind: "transport", message: "Settlement detail could not be matched to the committed payment." } } as const;
  }
  return { ok: true, value: settlement } as const;
}
