// Single source of truth for the live-engine connection state model.
//
// The nine states below are the complete lifecycle a live local-engine client
// may occupy. The preview provider does NOT use these — it has its own,
// deliberately simpler "connected to in-memory fixtures" status. Keeping the
// live enum here (and separate from the provisional `ConnectionState` on the
// preview boundary) guarantees the two providers can never silently share a
// state machine or fall back into each other.

export const LIVE_CONNECTION_STATES = [
  "starting",
  "pairing_required",
  "pairing_in_progress",
  "rate_limited",
  "incompatible",
  "recovering",
  "ready",
  "disconnected",
  "outcome_uncertain",
] as const;

export type LiveConnectionState = (typeof LIVE_CONNECTION_STATES)[number];

/** Exact player-facing label for every state (verbatim from the PRD). */
export const LIVE_CONNECTION_LABELS: Readonly<Record<LiveConnectionState, string>> = {
  starting: "Starting",
  pairing_required: "Pairing required",
  pairing_in_progress: "Pairing in progress",
  rate_limited: "Rate limited",
  incompatible: "Incompatible",
  recovering: "Recovering",
  ready: "Ready",
  disconnected: "Disconnected",
  outcome_uncertain: "Outcome uncertain",
};

/** Short human explanation of each state, shown in the status tooltip. */
export const LIVE_CONNECTION_DETAILS: Readonly<Record<LiveConnectionState, string>> = {
  starting: "Connecting to the local engine.",
  pairing_required: "Pair with the local engine using the one-time console code.",
  pairing_in_progress: "Waiting for the host to accept the pairing code.",
  rate_limited: "Too many pairing attempts — wait before trying again.",
  incompatible: "This build can’t talk to the running engine version.",
  recovering: "Rechecking the last operation before any new action.",
  ready: "Connected to the local engine.",
  disconnected: "The local engine isn’t reachable — no career data is available.",
  outcome_uncertain: "The last action’s outcome is unknown — paused until it’s resolved.",
};

export function isLiveConnectionState(value: unknown): value is LiveConnectionState {
  return (
    typeof value === "string" &&
    (LIVE_CONNECTION_STATES as readonly string[]).includes(value)
  );
}

/**
 * Only `ready` represents a trusted live engine session. Every other state
 * must fail closed: no player state, no eligibility, no travel authorization,
 * and no mutations.
 */
export function isFailClosed(state: LiveConnectionState): boolean {
  return state !== "ready";
}
