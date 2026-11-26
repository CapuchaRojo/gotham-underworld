// Fail-closed live-engine client for the M030-C1.3 Python browser host.
//
// This is the local-engine sibling of `preview.ts`. It sits behind the same
// gameplay method surface as the preview client, but it NEVER constructs a
// fixture `Scenario`, NEVER reads `SCENARIOS`/`SCENARIO_BY_ID`, and NEVER falls
// back to synthetic career state — not on `disconnected`, not on `incompatible`,
// not on a malformed host session. A live client that cannot talk to the engine
// serves `null` player state and refuses every mutation. No exceptions.
//
// Pairing/transport (the actual HTTP calls) arrives in GTG-13A-3/4; this module
// is the state model + validation seam they will plug into.

import type {
  ActionReceipt,
  Eligibility,
  GameplayClient,
  GameplayResult,
  Intent,
  PlayerState,
  TravelAuthorization,
} from "./types";
import type { LiveConnectionState } from "./connection";
import {
  LIVE_CONNECTION_DETAILS,
  LIVE_CONNECTION_LABELS,
} from "./connection";
import { validateHostSession } from "./wire";
import type { HostSession } from "./wire";

// ---------------------------------------------------------------------------
// Status (distinct from the preview's synthetic `EngineStatus`)
// ---------------------------------------------------------------------------

export interface LiveEngineStatus {
  kind: "live";
  connectionState: LiveConnectionState;
  /** Full, unmistakable status line shown to the player. */
  label: string;
  /** Live-vs-synthetic context label (always "Local engine" here). */
  contextLabel: string;
  /** Short human explanation of the current context. */
  detail: string;
}

export function liveEngineStatus(state: LiveConnectionState): LiveEngineStatus {
  return {
    kind: "live",
    connectionState: state,
    label: LIVE_CONNECTION_LABELS[state],
    contextLabel: "Local engine",
    detail: LIVE_CONNECTION_DETAILS[state],
  };
}

// ---------------------------------------------------------------------------
// Host-session reconciliation (the validation seam pairing will use)
// ---------------------------------------------------------------------------

export type SessionFailureKind = "malformed" | "incompatible";

export type HostSessionReconciliation =
  | { ok: true; connectionState: "ready"; session: HostSession }
  | {
      ok: false;
      connectionState: "incompatible";
      failure: SessionFailureKind;
      reason: string;
    };

/**
 * Promote a candidate host session to trusted live state ONLY after it passes
 * the exact wire validator. A value that fails for a binding mismatch
 * (`invalid_value` — wrong engine_release, protocol version, mode, lifetime)
 * is labeled `incompatible`; everything else is labeled `malformed`. Both fail
 * closed to the `incompatible` connection state — never to a preview.
 */
export function reconcileHostSession(candidate: unknown): HostSessionReconciliation {
  const result = validateHostSession(candidate);
  if (result.ok) {
    return { ok: true, connectionState: "ready", session: result.value };
  }
  return {
    ok: false,
    connectionState: "incompatible",
    failure: result.error.code === "invalid_value" ? "incompatible" : "malformed",
    reason: result.error.message,
  };
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export interface LiveEngineClient extends Omit<GameplayClient, "connectionState"> {
  readonly connectionState: LiveConnectionState;
}

export interface LiveEngineClientSource {
  getConnectionState(): LiveConnectionState;
}

function liveFailure(
  state: LiveConnectionState,
  operation: "authorize" | "read" | "mutate",
): GameplayResult<never> {
  if (state === "incompatible") {
    return {
      ok: false,
      code: "session_incompatible",
      message:
        "This client can’t talk to the running engine — the host version is incompatible.",
    };
  }
  if (operation === "authorize") {
    return {
      ok: false,
      code: "not_authorized",
      message:
        "Travel can only be authorized by the live engine, which isn’t connected.",
    };
  }
  return {
    ok: false,
    code: "engine_unavailable",
    message: "The live engine isn’t available — no career state or gameplay right now.",
  };
}

/**
 * Build the fail-closed live client. It observes the current connection state
 * through `source` (the React provider owns the actual state) and refuses to
 * serve or authorize anything until GTG-13A-3/4 wire up a validated session and
 * a committed receipt. `getPlayerState()` is always `null` at this phase —
 * including in `ready` — because there is no projection transport yet, and
 * synthesizing one from fixtures is forbidden.
 */
export function createLiveEngineClient(source: LiveEngineClientSource): LiveEngineClient {
  return {
    get connectionState(): LiveConnectionState {
      return source.getConnectionState();
    },

    getPlayerState(): PlayerState | null {
      return null;
    },

    async getRouteQuote() {
      return liveFailure(source.getConnectionState(), "read");
    },

    async authorizeTravel(): Promise<GameplayResult<TravelAuthorization>> {
      return liveFailure(source.getConnectionState(), "authorize");
    },

    async getEligibility(): Promise<GameplayResult<Eligibility>> {
      return liveFailure(source.getConnectionState(), "read");
    },

    async executeAction(_intent: Intent): Promise<GameplayResult<ActionReceipt>> {
      return liveFailure(source.getConnectionState(), "mutate");
    },

    async recover(): Promise<GameplayResult<ActionReceipt>> {
      return liveFailure(source.getConnectionState(), "read");
    },

    async restore(): Promise<GameplayResult<PlayerState>> {
      return liveFailure(source.getConnectionState(), "read");
    },
  };
}
