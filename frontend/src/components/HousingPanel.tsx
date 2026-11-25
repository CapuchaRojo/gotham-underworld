import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useLiveEngine } from "../gameplay/LiveEngineProvider";
import type { CapabilityStore, HostFailure, HousingHostClient } from "../gameplay/host";
import { canPayRoom, readHousing, readPaymentDetail, sameCareer, sameHousingSnapshot } from "../gameplay/housing";
import type { HousingSnapshot } from "../gameplay/housing";
import type { Outbox, OutboxOutcome } from "../gameplay/outbox";
import type { HousingSettlement, RoomPaymentStatus } from "../gameplay/wire";

const eligibility: Record<RoomPaymentStatus, string> = {
  not_adopted: "Housing has not been adopted for this career.",
  pending: "Your housing enrollment is pending.",
  detained: "Payment is unavailable while in custody.",
  away_from_home: "Return home to pay rent.",
  no_payable_balance: "There is no payable rent balance.",
  no_cash: "You have no cash available for rent.",
  eligible: "You can make a rent payment.",
};

const settlementKind: Record<HousingSettlement["kind"], string> = {
  prepay: "Rent prepayment",
  arrears_payment: "Arrears payment",
  due: "Automatic due-day settlement",
};

function Settlement({ title, row }: { title: string; row: HousingSettlement }) {
  return (
    <section aria-label={title} className="rounded border border-border p-3">
      <h3 className="font-semibold">{title}</h3>
      <p>{settlementKind[row.kind]} on day {row.day}</p>
      <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1">
        <dt>Amount paid</dt><dd>${row.paid}</dd>
        <dt>Credit applied</dt><dd>${row.credit_applied}</dd>
        <dt>Cash after settlement</dt><dd className="break-all">${row.balance_after.cash}</dd>
        <dt>Arrears after settlement</dt><dd>${row.balance_after.arrears}</dd>
        <dt>Prepaid credit after settlement</dt><dd>${row.balance_after.prepaid}</dd>
        <dt>Next due day after settlement</dt><dd>{row.balance_after.next_due_day}</dd>
      </dl>
    </section>
  );
}

interface Props {
  host: HousingHostClient;
  store: CapabilityStore;
  outbox: Outbox;
}

type ResultDisplay = { requestId: string; settlement: HousingSettlement };
type Confirmation = { snapshot: HousingSnapshot; retryId?: string };

export function HousingPanel({ host, store, outbox }: Props) {
  const { connectionState, session, pair, revalidate } = useLiveEngine();
  const pairing = connectionState === "pairing_in_progress" || connectionState === "recovering";
  const instance = connectionState === "ready" ? session?.instance_id : undefined;
  const [code, setCode] = useState("");
  const [snapshot, setSnapshot] = useState<HousingSnapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [blocked, setBlocked] = useState(true);
  const [retry, setRetry] = useState<string>();
  const [historical, setHistorical] = useState<ResultDisplay | null>(null);
  const [confirmation, setConfirmation] = useState<Confirmation | null>(null);
  const running = useRef(false);

  const run = useCallback(async (task: () => Promise<void>) => {
    if (running.current) return;
    running.current = true;
    setBusy(true);
    try {
      await task();
    } catch {
      setBlocked(true);
      setMessage("Housing is unavailable. Refresh to check the payment record before trying again.");
    } finally {
      setBusy(false);
      running.current = false;
    }
  }, []);

  useEffect(() => {
    void revalidate();
  }, [revalidate]);

  const authFailure = useCallback(async (failure: HostFailure) => {
    if (failure.kind === "host_error" && failure.code === "UNAUTHORIZED") await revalidate();
  }, [revalidate]);

  const readCurrent = useCallback(async (capability: string) => {
    const read = await readHousing(host, capability);
    if (!read.ok) {
      setSnapshot(null);
      setBlocked(true);
      await authFailure(read.failure);
      return null;
    }
    setSnapshot(read.value);
    return read.value;
  }, [host, authFailure]);

  const reconcile = useCallback(async (outcome: OutboxOutcome, capability: string, current: HousingSnapshot, refresh: boolean) => {
    setRetry(undefined);
    if (outcome.kind === "committed") {
      const detail = await readPaymentDetail(host, capability, outcome.envelope, outcome.receipt);
      setHistorical(detail.ok ? { requestId: outcome.requestId, settlement: detail.value } : null);
      if (refresh) {
        const updated = await readCurrent(capability);
        if (!updated || !sameCareer(current.state, updated.state) || updated.state.revision < outcome.receipt.revision) {
          setSnapshot(null);
          setBlocked(true);
          setMessage("Payment confirmed. Current housing could not be refreshed.");
          return;
        }
        await revalidate();
      }
      setBlocked(false);
      setMessage(detail.ok ? "Payment confirmed." : "Payment confirmed. Settlement detail is unavailable. Refresh to read it again.");
      if (!detail.ok) await authFailure(detail.failure);
      return;
    }

    switch (outcome.kind) {
      case "retry_available":
        setRetry(outcome.requestId);
        setMessage("The host has no record of this payment. You can explicitly retry the original request if payment is available.");
        break;
      case "stale_revision":
      case "adapter_defect":
        await readCurrent(capability);
        setBlocked(false);
        setMessage(outcome.kind === "stale_revision" ?
          "The original payment decision expired. Review current housing before starting again." :
          "The engine refused this payment. Review current housing before starting again.");
        break;
      case "reauthorize_required":
        setMessage("Pair again to check the original payment.");
        await revalidate();
        break;
      case "storage_unavailable":
      case "storage_failure":
        setMessage("Payment storage is unavailable. Refresh before trying again.");
        break;
      case "ambiguous":
      case "quarantined":
      case "wrong_career":
      case "request_id_reused":
        setMessage("The original payment cannot be matched to this checkpoint history. Payment is paused. Refresh to check again.");
        break;
      case "conflicting_intent":
        setMessage("Another request is pending. Refresh to check the original payment.");
        break;
      default:
        setMessage("The payment outcome is uncertain. Refresh to check the original request. Payment is paused.");
    }
  }, [host, readCurrent, revalidate, authFailure]);

  const inspect = useCallback(async () => {
    const capability = store.get();
    if (!instance || !capability) return;
    setBlocked(true);
    setConfirmation(null);
    setMessage("Checking current housing and saved payments...");
    setRetry(undefined);
    setHistorical(null);
    const current = await readCurrent(capability);
    if (!current) {
      setMessage("Current housing is unavailable. Refresh or pair again.");
      return;
    }
    const { career_id, lineage_id, revision } = current.state;
    const record = await outbox.findHousing(career_id, lineage_id);
    if (!record) {
      setBlocked(false);
      setMessage("");
      return;
    }
    const outcome = await outbox.recover({
      requestId: record.request_id, careerId: career_id, lineageId: lineage_id, revision, capability,
      housing: { hostInstanceId: instance, retry: false },
    });
    await reconcile(outcome, capability, current,
      outcome.kind === "committed" && outcome.envelope.revision !== revision);
  }, [instance, store, readCurrent, outbox, reconcile]);

  useEffect(() => {
    if (instance) void run(inspect);
  }, [instance, run, inspect]);

  function submitCode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const submitted = code.trim();
    if (!submitted) return;
    setCode("");
    setSnapshot(null);
    setHistorical(null);
    setConfirmation(null);
    setBlocked(true);
    setMessage("");
    void pair(submitted);
  }

  function confirmPayment() {
    if (!confirmation || !instance) return;
    void run(async () => {
      setConfirmation(null);
      setBlocked(true);
      setMessage("Checking the confirmed payment...");
      const capability = store.get();
      if (!capability) {
        setMessage("Pair again before paying.");
        return;
      }
      const current = await readCurrent(capability);
      if (!current) {
        setMessage("Current housing is unavailable. No payment was sent.");
        return;
      }
      if (!sameHousingSnapshot(confirmation.snapshot.state, current.state) || !canPayRoom(current)) {
        setMessage("Housing changed before confirmation. Refresh and review it before paying.");
        return;
      }
      const { career_id, lineage_id, revision } = current.state;
      const identity = { careerId: career_id, lineageId: lineage_id, revision, capability };
      setMessage("Submitting the confirmed payment...");
      setSnapshot(null);
      const outcome = confirmation.retryId
        ? await outbox.recover({ ...identity, requestId: confirmation.retryId, housing: { hostInstanceId: instance, retry: true } })
        : await outbox.submit({ ...identity, command: "pay_room", arguments: {}, hostInstanceId: instance });
      await reconcile(outcome, capability, current, true);
    });
  }

  const data = instance ? snapshot : null;
  const wallet = data?.state.state.player.cash;
  const room = data?.state.state.housing;
  const eligible = data && canPayRoom(data);
  const button = "rounded border border-border px-3 py-2 disabled:opacity-50";
  return (
    <section aria-labelledby="housing-heading" className="mx-auto grid max-w-3xl gap-4 p-5">
      <h1 id="housing-heading" className="text-2xl font-semibold">Housing</h1>
      {!instance && (
        <form onSubmit={submitCode} autoComplete="off" className="flex flex-wrap items-end gap-2">
          <label className="grid gap-1">One-time console code
            <input type="password" maxLength={128} value={code} onChange={(event) => setCode(event.target.value)}
              className="rounded border border-border bg-background px-3 py-2" />
          </label>
          <button className={button} disabled={pairing || !code.trim()}>Pair local engine</button>
          <button type="button" className={button} disabled={pairing}
            onClick={() => void revalidate()}>Reconnect</button>
        </form>
      )}
      {instance && (
        <div>
          <button className={button} disabled={busy || !!confirmation} onClick={() => void run(inspect)}>Refresh housing</button>
        </div>
      )}
      <p role="status" className="min-h-6">{message || (instance && busy ? "Loading housing..." : !instance ? "Pair with the local engine to view housing." : "")}</p>
      {data && (
        <>
          <dl aria-label="Current housing" className="grid grid-cols-2 gap-x-4 gap-y-1 rounded border border-border p-3">
            <dt>Current cash</dt><dd>{Number.isSafeInteger(wallet) ? `$${wallet}` : "Exact wallet unavailable"}</dd>
            <dt>Housing status</dt><dd>{data.housing.pay_room === "pending" ? "Enrollment pending" : !room ? "Not adopted" : room.status === "grace" ? "Grace" : "Current"}</dd>
            <dt>Outstanding arrears</dt><dd>{room ? `$${room.arrears}` : "Unavailable"}</dd>
            <dt>Prepaid rent credit</dt><dd>{room ? `$${room.prepaid}` : "Unavailable"}</dd>
            <dt>Next due day</dt><dd>{room?.next_due_day ?? "Unavailable"}</dd>
          </dl>
          <p>{data.housing.pay_room === "eligible" && !eligible ? "Payment is unavailable until current wallet and command access can be verified." : eligibility[data.housing.pay_room]}</p>
          {eligible && !blocked && !confirmation &&
            <div><button className={button} disabled={busy} onClick={() => setConfirmation({ snapshot: data })}>Pay rent</button></div>}
          {eligible && retry && !confirmation &&
            <div><button className={button} disabled={busy} onClick={() => setConfirmation({ snapshot: data, retryId: retry })}>Retry original payment</button></div>}
          {confirmation &&
            <section aria-label="Confirm rent payment" className="grid gap-2 rounded border border-border p-3">
              <h2 className="font-semibold">Confirm rent payment</h2>
              <p>The engine determines and deducts the payable amount from your current cash.</p>
              <div className="flex gap-2">
                <button className={button} disabled={busy} onClick={confirmPayment}>Confirm payment</button>
                <button className={button} disabled={busy} onClick={() => setConfirmation(null)}>Cancel</button>
              </div>
            </section>}
          {data.housing.latest_settlement
            ? <Settlement title="Latest recorded settlement" row={data.housing.latest_settlement} />
            : <p>No rent settlements recorded.</p>}
        </>
      )}
      {instance && historical && (
        <div className="grid gap-2">
          <Settlement title="Result for this payment" row={historical.settlement} />
          <p className="break-all text-sm">Request {historical.requestId}</p>
        </div>
      )}
    </section>
  );
}
