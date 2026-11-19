// PROVISIONAL — reconcile against bridge source.
//
// The types below are the React-facing gameplay contract for M030-C2. They are
// deliberately *boundary-level* only: they name the operations the client needs
// and the shapes it renders, but they do NOT define any bridge wire details
// (HTTP methods/paths, headers, auth, request-ID serialization, or projection
// field names from `bridge_projection.py`). Those remain SOURCE REQUIRED and
// will be reconciled in M030-C2-02.

import type {
  BudgetState,
  Commitment,
  ContactCard,
  HousingState,
  InstitutionRecord,
  MoneyState,
  Observation,
  RouteQuote,
} from "../types";

// ---------------------------------------------------------------------------
// Connection lifecycle (client-facing)
// ---------------------------------------------------------------------------

// PROVISIONAL — reconcile against bridge source.
export type ConnectionState =
  | "connecting"
  | "connected"
  | "unavailable"
  | "incompatible";

/**
 * Whether the data a provider serves is live engine output or authored,
 * read-only synthetic fixtures. Every provider must label this so the player
 * can never mistake a preview for a live career.
 */
export type EngineKind = "synthetic" | "live";

/**
 * Which engine backs the mounted provider. `preview` serves authored,
 * read-only synthetic fixtures; `live` serves a fail-closed local-engine
 * client. The choice is made once at mount time and never auto-switches
 * (a dropped live connection must NOT fall back to preview).
 */
export type EngineMode = "preview" | "live";

export interface EngineStatus {
  kind: EngineKind;
  connectionState: ConnectionState;
  /** Full, unmistakable status line shown to the player. */
  label: string;
  /** Live-vs-synthetic context label (e.g. "Synthetic display data"). */
  contextLabel: string;
  /** Short human explanation of the current context. */
  detail: string;
}

// ---------------------------------------------------------------------------
// Per-intent submission state
// ---------------------------------------------------------------------------

// PROVISIONAL — reconcile against bridge source.
//
// idle → submitting → committed → saved, plus `outcome_uncertain` for
// submitted-but-unconfirmed. `submitting` is inert to further clicks; a
// timeout is NOT failure (it becomes `outcome_uncertain`).
export type SubmissionState =
  | "idle"
  | "submitting"
  | "committed"
  | "saved"
  | "outcome_uncertain";

// ---------------------------------------------------------------------------
// Player-safe state projection
// ---------------------------------------------------------------------------

/**
 * A player-safe, read-only projection of the current career. The client never
 * renders raw world snapshots or internal event dictionaries.
 *
 * PROVISIONAL — reconcile against bridge source.
 */
export interface Opportunity {
  id: string;
  title: string;
  pay: number | null;
  actions: number;
  placeId: string;
  /** Engine-decided; the client never recomputes eligibility. */
  executable: boolean;
  /** Player-safe block reasons, only present when not executable. */
  blockReasons: string[];
  expiry?: string;
  note: string;
}

// PROVISIONAL — reconcile against bridge source.
export interface PlayerState {
  day: number;
  locationId: string;
  money: MoneyState;
  budget: BudgetState;
  housing: HousingState;
  opportunities: Opportunity[];
  commitments: Commitment[];
  contacts: ContactCard[];
  /** Player-received only. */
  observations: Observation[];
  /** Player-known only. */
  institutions: InstitutionRecord[];
}

// ---------------------------------------------------------------------------
// Results, errors, and commands
// ---------------------------------------------------------------------------

// PROVISIONAL — reconcile against bridge source (exact codes TBD).
export type GameplayErrorCode =
  | "ineligible"
  | "stale_revision"
  | "unknown_request"
  | "session_incompatible"
  | "engine_unavailable"
  | "already_committed"
  | "not_authorized"
  | "unsupported";

export type GameplayResult<T> =
  | { ok: true; value: T }
  | { ok: false; code: GameplayErrorCode; message: string; reasons?: string[] };

export interface Eligibility {
  choiceId: string;
  executable: boolean;
  /** Player-safe reasons why the choice is blocked. */
  reasons: string[];
}

export type IntentKind = "work" | "decline" | "postpone";

export interface Intent {
  choiceId: string;
  kind: IntentKind;
}

export interface ActionReceipt {
  /** Client-generated, opaque; wire format is NOT defined here. */
  requestId: string;
  state: SubmissionState;
}

export interface TravelAuthorization {
  destination: string;
  authorized: boolean;
}

/**
 * React-facing gameplay contract. The exact same interface is implemented by
 * `PreviewGameplayProvider` (synthetic fixtures) today and by a
 * `LiveEngineProvider` (bridge client) once the bridge contract is reconciled.
 *
 * PROVISIONAL — reconcile against bridge source.
 */
export interface GameplayClient {
  readonly connectionState: ConnectionState;

  /** Player-safe state projection of the current career (null if unavailable). */
  getPlayerState(): PlayerState | null;

  /** Authoritative TU/permission/requirement quote for an origin→destination. */
  getRouteQuote(
    origin: string,
    destination: string,
  ): Promise<GameplayResult<RouteQuote>>;

  /** Explicitly authorize travel to a destination. */
  authorizeTravel(destination: string): Promise<GameplayResult<TravelAuthorization>>;

  /** Engine-decided eligibility for a given choice. */
  getEligibility(choiceId: string): Promise<GameplayResult<Eligibility>>;

  /** Submit a work/decline/postpone intent, exactly-once and revision-checked. */
  executeAction(intent: Intent): Promise<GameplayResult<ActionReceipt>>;

  /** Query an operation's outcome by request ID (lost-ack recovery). */
  recover(requestId: string): Promise<GameplayResult<ActionReceipt>>;

  /** Restore a persisted career on restart. */
  restore(): Promise<GameplayResult<PlayerState>>;
}
