// Exact wire-contract types for the M030-C1.3 Python browser host.
// Shapes are transcribed verbatim from docs/prd/m030-c2-gtg13a-liveengine.md
// §Integrations. This module is the single source of truth for the wire.

import { ENGINE_RELEASE } from "./constants";

// ---------------------------------------------------------------------------
// Command allowlist + exact argument keys
// ---------------------------------------------------------------------------

export const COMMAND_ARGUMENTS = {
  settle_in: [],
  wait: [],
  pay_room: [],
  enable_ordinary: [],
  choose: ["choice_id", "option_id"],
  ordinary_choose: ["offer_id", "option_id"],
  travel: ["destination", "mode"],
  enable_navigation: ["anchor"],
  enable_mobility: ["overlay_id", "request_id"],
  journey: [
    "destination",
    "profile",
    "vehicle_id",
    "max_tu",
    "max_cash",
    "return_to",
    "quote_token",
    "request_id",
  ],
} as const satisfies Record<string, readonly string[]>;

export type Command = keyof typeof COMMAND_ARGUMENTS;
export const COMMANDS = Object.keys(COMMAND_ARGUMENTS) as Command[];

/** The seven-field command envelope — exactly these fields, all required. */
export interface CommandRequest {
  protocol_version: 1;
  career_id: string;
  lineage_id: string;
  request_id: string;
  expected_revision: number;
  command: Command;
  arguments: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Session / bootstrap
// ---------------------------------------------------------------------------

export interface HostSession {
  host_protocol_version: 1;
  bridge_protocol_version: 1;
  bundle_id: string;
  manifest_sha256: string; // lowercase hex
  engine_release: typeof ENGINE_RELEASE;
  instance_id: string; // rotates on host restart
  mode: "local_engine";
  session_lifetime: "process";
}

export type BootstrapResponse = HostSession & { capability: string };

// ---------------------------------------------------------------------------
// Engine response / receipt / projection
// ---------------------------------------------------------------------------

export interface Receipt {
  request_id: string;
  revision: number;
  command_sequence: number; // engine sequence; may exceed bridge revision on imports
  command: string;
  day: number;
  status: "committed";
}

export type Custody = "free" | "pretrial";
export type AdoptionState = "not_adopted" | "pending" | "active";
export type HousingStatus = "current" | "grace";
export type AssistanceStatus = "unused" | "owed" | "overdue" | "repaid" | "declined";
export type OpportunityCommand = "choose" | "ordinary_choose";

export interface PlayerProjection {
  day: number;
  player: { cash: number; heat: number; custody: Custody };
  budgets: {
    daily_actions: number; // 3
    actions_remaining: number;
    daily_travel_units: number; // 18
    travel_units_remaining: number | null;
  };
  location: { id: string; label: string } | null;
  systems: {
    navigation: AdoptionState;
    daily_life: AdoptionState;
    ordinary: AdoptionState;
    mobility: AdoptionState;
  };
  housing: {
    status: HousingStatus;
    home_id: string;
    next_due_day: number;
    arrears: number;
    prepaid: number;
  } | null;
  contacts: { id: string; name: string; role: string; standing: number }[]; // Tess + Cal only
  opportunities: Opportunity[];
  outcomes: { choice_id: string; option_id: string; day: number; feedback: string }[]; // last 10
  ordinary?: {
    employment: number;
    assistance: {
      status: AssistanceStatus;
      amount: number;
      due_day: number | null;
    };
  };
}

export interface OpportunityOption {
  id: string;
  label: string;
  availability: "available" | "unavailable";
  reason: string | null;
  action_cost: number;
  tradeoff: string;
  arguments:
    | { choice_id: string; option_id: string }
    | { offer_id: string; option_id: string };
}

export interface Opportunity {
  id: string;
  title: string;
  situation: string;
  speaker: string;
  open_day: number;
  expires_day: number;
  state: string;
  command: OpportunityCommand;
  options: OpportunityOption[];
}

export interface EngineEnvelope {
  protocol_version: 1;
  career_id: string;
  lineage_id: string;
  revision: number;
  allowed_commands: string[];
  receipt: Receipt | null;
  duplicate: boolean;
  state: PlayerProjection;
}

export type OperationResponse = EngineEnvelope & { operation_status: "committed" | "not_found" };

// ---------------------------------------------------------------------------
// Travel quotes
// ---------------------------------------------------------------------------

export interface QuoteResponse {
  protocol_version: 1;
  career_id: string;
  lineage_id: string;
  revision: number;
  quote: {
    origin: string;
    destination: string;
    mode: string;
    cost: number | null;
    affordable: boolean;
    remaining_tu: number;
    return_cost: number | null;
    return_fits_today: boolean;
    fare?: number | null;
    return_fare?: number | null;
    can_return_today?: boolean;
    return_uncertain?: boolean;
    command: "travel" | "journey";
    arguments: Record<string, string>;
  };
}

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

export interface BootstrapRequest {
  host_protocol_version: 1;
  bundle_id: string;
  code: string;
}

export interface TravelQuoteRequest {
  protocol_version: 1;
  destination: string;
  mode: string;
}

// ---------------------------------------------------------------------------
// Error envelopes
// ---------------------------------------------------------------------------

export interface ApiErrorEnvelope {
  protocol_version: 1;
  error: { code: string; message: string };
}

export interface HostErrorEnvelope {
  host_protocol_version: 1;
  error: { code: string; message: string };
}

// ---------------------------------------------------------------------------
// Error code → HTTP → client action (verbatim from PRD §Integrations)
// ---------------------------------------------------------------------------

export type ErrorCode =
  | "BOOTSTRAP_DENIED"
  | "BOOTSTRAP_RATE_LIMIT"
  | "HOST_INCOMPATIBLE"
  | "PROTOCOL_MISMATCH"
  | "UNAUTHORIZED"
  | "UNSAFE_HOST"
  | "UNSAFE_ORIGIN"
  | "INVALID_REQUEST"
  | "INVALID_ARGUMENTS"
  | "COMMAND_NOT_ALLOWED"
  | "STALE_REVISION"
  | "REQUEST_ID_REUSED"
  | "WRONG_CAREER"
  | "CHECKPOINT_CHANGED"
  | "SESSION_CLOSED"
  | "COMMAND_REJECTED"
  | "ROUTE_UNAVAILABLE"
  | "OUTCOME_UNKNOWN"
  | "INVALID_CHECKPOINT"
  | "REQUEST_TOO_LARGE"
  | "INVALID_CONTENT_TYPE"
  | "INVALID_HEADERS"
  | "INVALID_LENGTH"
  | "MALFORMED_JSON"
  | "INVALID_PATH"
  | "NOT_FOUND"
  | "METHOD_NOT_ALLOWED"
  | "INTERNAL_ERROR";

export type ClientAction =
  | "clear_code_request_fresh"
  | "pause_pairing"
  | "block_incompatible_client"
  | "reauthorize_retain_pending"
  | "stop_never_weaken_checks"
  | "adapter_defect_no_auto_retry"
  | "refresh_require_new_decision"
  | "stop_conflicting_intent"
  | "quarantine_pending_intent"
  | "operator_reopen_recovery"
  | "reconnect_reopen"
  | "refresh_eligibility_no_effects"
  | "show_unavailable_no_local_fallback"
  | "block_mutations_recover_original"
  | "operator_intervention"
  | "fix_transport"
  | "fix_framing_retain_uncertain"
  | "endpoint_method_mismatch"
  | "treat_outcome_uncertain_if_after_transmit";

export interface ErrorInfo {
  code: ErrorCode;
  http: number;
  action: ClientAction;
}

export const ERROR_TABLE: readonly ErrorInfo[] = [
  { code: "BOOTSTRAP_DENIED", http: 401, action: "clear_code_request_fresh" },
  { code: "BOOTSTRAP_RATE_LIMIT", http: 429, action: "pause_pairing" },
  { code: "HOST_INCOMPATIBLE", http: 409, action: "block_incompatible_client" },
  { code: "PROTOCOL_MISMATCH", http: 409, action: "block_incompatible_client" },
  { code: "UNAUTHORIZED", http: 401, action: "reauthorize_retain_pending" },
  { code: "UNSAFE_HOST", http: 403, action: "stop_never_weaken_checks" },
  { code: "UNSAFE_ORIGIN", http: 403, action: "stop_never_weaken_checks" },
  { code: "INVALID_REQUEST", http: 400, action: "adapter_defect_no_auto_retry" },
  { code: "INVALID_ARGUMENTS", http: 400, action: "adapter_defect_no_auto_retry" },
  { code: "COMMAND_NOT_ALLOWED", http: 400, action: "adapter_defect_no_auto_retry" },
  { code: "STALE_REVISION", http: 409, action: "refresh_require_new_decision" },
  { code: "REQUEST_ID_REUSED", http: 409, action: "stop_conflicting_intent" },
  { code: "WRONG_CAREER", http: 409, action: "quarantine_pending_intent" },
  { code: "CHECKPOINT_CHANGED", http: 409, action: "operator_reopen_recovery" },
  { code: "SESSION_CLOSED", http: 409, action: "reconnect_reopen" },
  { code: "COMMAND_REJECTED", http: 422, action: "refresh_eligibility_no_effects" },
  { code: "ROUTE_UNAVAILABLE", http: 422, action: "show_unavailable_no_local_fallback" },
  { code: "OUTCOME_UNKNOWN", http: 503, action: "block_mutations_recover_original" },
  { code: "INVALID_CHECKPOINT", http: 503, action: "operator_intervention" },
  { code: "REQUEST_TOO_LARGE", http: 413, action: "fix_transport" },
  { code: "INVALID_CONTENT_TYPE", http: 415, action: "fix_transport" },
  { code: "INVALID_HEADERS", http: 400, action: "fix_framing_retain_uncertain" },
  { code: "INVALID_LENGTH", http: 400, action: "fix_framing_retain_uncertain" },
  { code: "MALFORMED_JSON", http: 400, action: "fix_framing_retain_uncertain" },
  { code: "INVALID_PATH", http: 404, action: "endpoint_method_mismatch" },
  { code: "NOT_FOUND", http: 404, action: "endpoint_method_mismatch" },
  { code: "METHOD_NOT_ALLOWED", http: 405, action: "endpoint_method_mismatch" },
  { code: "INTERNAL_ERROR", http: 500, action: "treat_outcome_uncertain_if_after_transmit" },
];

export const ERROR_BY_CODE: Readonly<Record<ErrorCode, ErrorInfo>> = Object.fromEntries(
  ERROR_TABLE.map((entry) => [entry.code, entry]),
) as Readonly<Record<ErrorCode, ErrorInfo>>;
