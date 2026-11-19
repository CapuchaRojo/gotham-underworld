// Fail-closed React provider for the live local engine.
//
// This is the distinct, explicit counterpart to the preview provider
// (`GameplayProvider.tsx`). It owns the live connection state machine and the
// GTG-18 pairing + authenticated session lifecycle (bootstrap, revalidation,
// authoritative state read). It never touches `Scenario`/`SCENARIOS`/
// `SCENARIO_BY_ID` and never falls back to synthetic career state.
//
// Pairing and revalidation are explicit events only â€” there is no mount effect
// that submits a bootstrap or a command (React StrictMode-safe). Reload
// recovery is a read (`revalidate`), never a mutation.

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import type { ReactNode } from "react";
import type { PlayerState } from "./types";
import type { LiveConnectionState } from "./connection";
import type {
  LiveEngineClient,
  LiveEngineStatus,
  SessionFailureKind,
} from "./liveEngine";
import {
  createLiveEngineClient,
  liveEngineStatus,
  reconcileHostSession,
} from "./liveEngine";
import {
  createCapabilityStore,
  sessionMatchesBundle,
} from "./host";
import type {
  CapabilityStore,
  HostClient,
  HostFailure,
} from "./host";
import type { EngineEnvelope, HostSession } from "./wire";
import { createInspectionHostClient } from "./inspectionHost";

export interface LiveEngineContextValue {
  /** Explicit discriminator so live can never be mistaken for preview. */
  mode: "live";
  client: LiveEngineClient;
  connectionState: LiveConnectionState;
  status: LiveEngineStatus;
  /** Always `null` at this phase â€” the projectionâ†’gameplay mapping lands in GTG-14. */
  playerState: PlayerState | null;
  /** The validated host session, or null until pairing/revalidation succeeds. */
  session: HostSession | null;
  /** The validated authoritative state envelope (read-only inspection surface). */
  engineState: EngineEnvelope | null;
  /** Submit the one-time console code (single-flight, explicit user event). */
  pair: (code: string) => Promise<void>;
  /** Revalidate a sessionStorage capability against the host (read-only). */
  revalidate: () => Promise<void>;
  lastSessionFailure: { failure: SessionFailureKind; reason: string } | null;
  /** Player-facing explanation of the most recent host/transport failure. */
  lastError: string | null;
}

const FALLBACK_CLIENT = createLiveEngineClient({
  getConnectionState: () => "disconnected",
});

/** Safe fallback so `useLiveEngine` outside a provider fails closed, not open. */
const FALLBACK: LiveEngineContextValue = {
  mode: "live",
  client: FALLBACK_CLIENT,
  connectionState: "disconnected",
  status: liveEngineStatus("disconnected"),
  playerState: null,
  session: null,
  engineState: null,
  pair: async () => {},
  revalidate: async () => {},
  lastSessionFailure: null,
  lastError: null,
};

const LiveEngineContext = createContext<LiveEngineContextValue>(FALLBACK);

export interface LiveEngineProviderProps {
  children: ReactNode;
  /** Test/dev override; defaults to `starting`. */
  initialState?: LiveConnectionState;
  /** Test override; defaults to a real same-origin host client. */
  hostClient?: HostClient;
}

export function LiveEngineProvider({
  children,
  initialState = "starting",
  hostClient,
}: LiveEngineProviderProps) {
  const [connectionState, setConnectionState] =
    useState<LiveConnectionState>(initialState);
  const [session, setSession] = useState<HostSession | null>(null);
  const [engineState, setEngineState] = useState<EngineEnvelope | null>(null);
  const [lastSessionFailure, setLastSessionFailure] = useState<{
    failure: SessionFailureKind;
    reason: string;
  } | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);

  const client = useMemo(
    () => createLiveEngineClient({ getConnectionState: () => connectionState }),
    [connectionState],
  );
  const host = useMemo(() => hostClient ?? createInspectionHostClient(), [hostClient]);
  const store = useMemo<CapabilityStore>(() => createCapabilityStore(), []);
  // Single-flight guard: a second `pair()` while one is in progress is a no-op.
  const pairingInFlight = useRef<Promise<void> | null>(null);

  const applyFailure = useCallback(
    (failure: HostFailure) => {
      setEngineState(null);
      setSession(null);
      if (failure.kind === "host_error") {
        switch (failure.code) {
          case "BOOTSTRAP_DENIED":
          case "UNAUTHORIZED":
            // Rejected code / rotated capability â†’ discard and request a fresh code.
            store.clear();
            setLastError(failure.message);
            setConnectionState("pairing_required");
            return;
          case "BOOTSTRAP_RATE_LIMIT":
            setLastError(failure.message);
            setConnectionState("rate_limited");
            return;
          case "HOST_INCOMPATIBLE":
          case "PROTOCOL_MISMATCH":
            setLastSessionFailure({ failure: "incompatible", reason: failure.message });
            setConnectionState("incompatible");
            return;
          case "SESSION_CLOSED":
            store.clear();
            setLastError(failure.message);
            setConnectionState("disconnected");
            return;
          default:
            setLastError(failure.message);
            setConnectionState("disconnected");
            return;
        }
      }
      if (failure.kind === "validation") {
        const kind: SessionFailureKind =
          failure.code === "invalid_value" ? "incompatible" : "malformed";
        setLastSessionFailure({ failure: kind, reason: failure.message });
        setConnectionState("incompatible");
        return;
      }
      // transport
      setLastError(failure.message);
      setConnectionState("disconnected");
    },
    [store],
  );

  /**
   * Promote a validated host session to trusted live state and read the
   * authoritative state projection. Every step fails closed: no state is served
   * until the projection passes its exact wire validator.
   */
  const establishSession = useCallback(
    async (capability: string, candidate: HostSession) => {
      if (!sessionMatchesBundle(candidate)) {
        setLastSessionFailure({
          failure: "incompatible",
          reason: "The host is serving a different bundle than this client.",
        });
        setConnectionState("incompatible");
        return;
      }

      const reconciled = reconcileHostSession(candidate);
      if (!reconciled.ok) {
        setLastSessionFailure({ failure: reconciled.failure, reason: reconciled.reason });
        setConnectionState("incompatible");
        return;
      }

      setSession(reconciled.session);
      setLastSessionFailure(null);
      setLastError(null);

      const state = await host.getState(capability);
      if (!state.ok) {
        applyFailure(state.failure);
        return;
      }
      setEngineState(state.value);
      setConnectionState("ready");
    },
    [host, applyFailure],
  );

  const pair = useCallback(
    async (code: string) => {
      if (pairingInFlight.current) return pairingInFlight.current;

      setConnectionState("pairing_in_progress");
      setEngineState(null);
      setSession(null);
      setLastError(null);
      setLastSessionFailure(null);

      const run = (async () => {
        const result = await host.bootstrap(code);
        if (!result.ok) {
          applyFailure(result.failure);
          return;
        }
        const { capability, ...hostSession } = result.value;
        store.set(capability);
        await establishSession(capability, hostSession);
      })();

      pairingInFlight.current = run;
      try {
        await run;
      } finally {
        pairingInFlight.current = null;
      }
    },
    [host, store, applyFailure, establishSession],
  );

  const revalidate = useCallback(async () => {
    if (pairingInFlight.current) return pairingInFlight.current;
    const run = (async () => {
      setEngineState(null);
      setSession(null);
      setConnectionState("recovering");
      const capability = store.get();
      if (!capability) {
        setLastError(null);
        setConnectionState("pairing_required");
        return;
      }

      const sessionResult = await host.getSession(capability);
      if (!sessionResult.ok) {
        applyFailure(sessionResult.failure);
        return;
      }
      await establishSession(capability, sessionResult.value);
    })();
    pairingInFlight.current = run;
    try { await run; } finally { pairingInFlight.current = null; }
  }, [store, host, applyFailure, establishSession]);

  const status = liveEngineStatus(connectionState);
  const playerState = client.getPlayerState();

  const value = useMemo<LiveEngineContextValue>(
    () => ({
      mode: "live",
      client,
      connectionState,
      status,
      playerState,
      session,
      engineState,
      pair,
      revalidate,
      lastSessionFailure,
      lastError,
    }),
    [
      client,
      connectionState,
      status,
      playerState,
      session,
      engineState,
      pair,
      revalidate,
      lastSessionFailure,
      lastError,
    ],
  );

  return (
    <LiveEngineContext.Provider value={value}>{children}</LiveEngineContext.Provider>
  );
}

export function useLiveEngine(): LiveEngineContextValue {
  return useContext(LiveEngineContext);
}
