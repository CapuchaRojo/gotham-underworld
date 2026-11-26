import { useEffect, useRef, useState } from "react";
import { LiveEngineProvider, useLiveEngine } from "./gameplay/LiveEngineProvider";
import { LocalEngineInspection } from "./components/LocalEngineInspectionView";
import { inspectOutboxStorage } from "./gameplay/inspectionStorage";

export function PairingControls() {
  const { pair, revalidate, connectionState } = useLiveEngine();
  const [code, setCode] = useState("");
  const [storage, setStorage] = useState("Checking transport storage");
  const started = useRef(false);
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void inspectOutboxStorage().then(count => setStorage(`Outbox available (${count} stored requests)`))
      .catch(() => setStorage("Outbox unavailable; gameplay remains disabled"));
    void revalidate(); // GET only; never redeem a code or submit a command on mount.
  }, [revalidate]);
  const busy = connectionState === "pairing_in_progress" || connectionState === "recovering";
  return <section aria-label="Browser pairing" className="mx-auto max-w-5xl p-4">
    <h1 className="text-xl font-bold">Gotham: The Goon — local inspection</h1>
    <p>Read-only. Gameplay, travel, adoption, and day advancement are disabled.</p>
    <p role="status">{storage}</p>
    <form onSubmit={event => { event.preventDefault(); const entered = code; setCode(""); void pair(entered); }}>
      <label htmlFor="pair-code">One-time console code</label>
      <input id="pair-code" type="password" autoComplete="off" maxLength={128} value={code}
        onChange={event => setCode(event.target.value)} className="m-2 border border-border bg-surface p-2" />
      <button type="submit" disabled={busy || !code} className="m-2 border border-border p-2">Pair browser</button>
      <button type="button" disabled={busy} onClick={() => void revalidate()} className="m-2 border border-border p-2">Refresh session and state</button>
    </form>
    <p>Codes expire after 120 seconds. Press Enter in the host console for a new code.
      Reauthorization preserves transport requests. This build never retries them.</p>
  </section>;
}

export default function LocalHostApp() {
  return <LiveEngineProvider><main className="noir-texture min-h-screen bg-background text-foreground">
    <PairingControls /><LocalEngineInspection />
  </main></LiveEngineProvider>;
}
