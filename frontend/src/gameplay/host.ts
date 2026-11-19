// Fail-closed same-origin transport for the M030-C1.3 Python browser host.
//
// GTG-18 scope: console-code pairing (POST /host/v1/bootstrap), authenticated
// session revalidation (GET /host/v1/session), and authoritative state read
// (GET /api/v1/state). Command submission, recovery, and travel quotes arrive
// in later gates and are intentionally absent here.
//
// Every endpoint, method, header rule, and fetch policy is transcribed from
// docs/prd/m030-c2-gtg13a-liveengine.md §Integrations (binding). Nothing in
// this module is a guessed substitution.

import {
  ERROR_BY_CODE,
  HOST_PROTOCOL_VERSION,
  parseJsonBody,
  validateBootstrapResponse,
  validateEngineEnvelope,
  validateErrorEnvelope,
  validateHostSession,
  validateOperationResponse,
} from "./wire";
import type {
  BootstrapResponse,
  CommandRequest,
  EngineEnvelope,
  ErrorCode,
  HostSession,
  OperationResponse,
} from "./wire";

// ---------------------------------------------------------------------------
// Client bundle identity (the "matches the client's own bundle" assertion)
// ---------------------------------------------------------------------------

/**
 * Bundle ID shared with tools/package_host.py. Local builds are release candidates
 * until the owner independently approves the manifest pin; a matching ID alone
 * is not release authenticity.
 */
export const CLIENT_BUNDLE_ID = "goon-c2b-inspection-v1" as const;

/** Assert the host is serving the same bundle as this client (fail closed). */
export function sessionMatchesBundle(session: HostSession): boolean {
  return session.bundle_id === CLIENT_BUNDLE_ID;
}

// ---------------------------------------------------------------------------
// Capability storage (memory + sessionStorage ONLY — never IndexedDB/localStorage)
// ---------------------------------------------------------------------------

export const CAPABILITY_STORAGE_KEY = "goon.host.capability.v1";

export interface CapabilityStore {
  get(): string | null;
  set(capability: string): void;
  clear(): void;
}

function defaultSessionStorage(): Storage | null {
  try {
    return typeof window !== "undefined" && window.sessionStorage
      ? window.sessionStorage
      : null;
  } catch {
    // sessionStorage can throw in privacy mode / sandboxed iframes.
    return null;
  }
}

/**
 * Capability held in memory + sessionStorage. The memory copy makes re-reads
 * synchronous and immune to a storage backend that is absent or throwing; the
 * sessionStorage copy survives reload so the client can attempt revalidation.
 */
export function createCapabilityStore(storage?: Storage | null): CapabilityStore {
  let memory: string | null = null;
  const target = storage ?? defaultSessionStorage();

  return {
    get() {
      if (memory !== null) return memory;
      try {
        const value = target?.getItem(CAPABILITY_STORAGE_KEY) ?? null;
        if (value !== null) memory = value;
        return value;
      } catch {
        return memory;
      }
    },
    set(capability) {
      memory = capability;
      try {
        target?.setItem(CAPABILITY_STORAGE_KEY, capability);
      } catch {
        // Storage unavailable: memory still holds the capability for this process.
      }
    },
    clear() {
      memory = null;
      try {
        target?.removeItem(CAPABILITY_STORAGE_KEY);
      } catch {
        // Nothing else to do.
      }
    },
  };
}

// ---------------------------------------------------------------------------
// Failures
// ---------------------------------------------------------------------------

export type HostFailure =
  | {
      /** A recognized host/API error envelope with a mapped client action. */
      kind: "host_error";
      code: string;
      http: number;
      message: string;
      action: string | null;
    }
  | {
      /** Network loss, unreadable body, or non-JSON response (never assume JSON). */
      kind: "transport";
      message: string;
    }
  | {
      /** A 200 body that failed the exact runtime validator. */
      kind: "validation";
      code: string;
      message: string;
      path: string;
    };

export type HostResult<T> =
  | { ok: true; value: T }
  | { ok: false; failure: HostFailure };

// ---------------------------------------------------------------------------
// Transport
// ---------------------------------------------------------------------------

export interface HostClient {
  /** POST /host/v1/bootstrap — one-time code, no Bearer. */
  bootstrap(code: string): Promise<HostResult<BootstrapResponse>>;
  /** GET /host/v1/session — Bearer capability, returns HostSession (no capability). */
  getSession(capability: string): Promise<HostResult<HostSession>>;
  /** GET /api/v1/state — Bearer capability, returns an EngineEnvelope (receipt null). */
  getState(capability: string): Promise<HostResult<EngineEnvelope>>;
  /** POST /api/v1/commands — Bearer capability, exactly-once revision-checked command. */
  postCommand(capability: string, request: CommandRequest): Promise<HostResult<EngineEnvelope>>;
  /** GET /api/v1/operations/{request_id} — Bearer capability, lost-ack recovery. */
  getOperation(capability: string, requestId: string): Promise<HostResult<OperationResponse>>;
}

export interface HostClientOptions {
  /** Injectable for mocked-transport tests; defaults to the ambient fetch. */
  fetchImpl?: typeof fetch;
  /** Absolute origin prefix; default "" means exact relative URLs (same-origin). */
  baseUrl?: string;
}

const BOOTSTRAP_PATH = "/host/v1/bootstrap";
const SESSION_PATH = "/host/v1/session";
const STATE_PATH = "/api/v1/state";
const COMMANDS_PATH = "/api/v1/commands";
const OPERATIONS_PATH = "/api/v1/operations";

type Validator<T> = (
  value: unknown,
) => { ok: true; value: T } | { ok: false; error: { code: string; message: string; path: string } };

function describeError(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  return "The engine host could not be reached.";
}

export function createHostClient(options: HostClientOptions = {}): HostClient {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;
  const baseUrl = options.baseUrl ?? "";

  // Binding fetch policy: credentials omitted, responses never cached, and a
  // redirect is treated as a transport failure rather than silently followed.
  const policy = {
    credentials: "omit",
    cache: "no-store",
    redirect: "error",
  } as const;

  async function request<T>(
    path: string,
    init: RequestInit,
    validate: Validator<T>,
  ): Promise<HostResult<T>> {
    let response: Response;
    try {
      response = await fetchImpl(baseUrl + path, init);
    } catch (error) {
      return { ok: false, failure: { kind: "transport", message: describeError(error) } };
    }

    let text: string;
    try {
      text = await response.text();
    } catch {
      return {
        ok: false,
        failure: { kind: "transport", message: "The host response body could not be read." },
      };
    }

    if (!response.ok) {
      // Non-200: try the host/API error envelope; degrade to transport if the
      // body is HTML or otherwise unreadable (the PRD requires this tolerance).
      const parsed = parseJsonBody(text);
      if (parsed.ok) {
        const envelope = validateErrorEnvelope(parsed.value);
        if (envelope.ok) {
          const code = envelope.value.error.code;
          const info = ERROR_BY_CODE[code as ErrorCode];
          return {
            ok: false,
            failure: {
              kind: "host_error",
              code,
              http: response.status,
              message: envelope.value.error.message,
              action: info ? info.action : null,
            },
          };
        }
      }
      return {
        ok: false,
        failure: {
          kind: "transport",
          message: `The host returned HTTP ${response.status} with an unreadable body.`,
        },
      };
    }

    const parsed = parseJsonBody(text);
    if (!parsed.ok) {
      return { ok: false, failure: { kind: "transport", message: parsed.error.message } };
    }
    const result = validate(parsed.value);
    if (!result.ok) {
      return {
        ok: false,
        failure: {
          kind: "validation",
          code: result.error.code,
          message: result.error.message,
          path: result.error.path,
        },
      };
    }
    return { ok: true, value: result.value };
  }

  function authHeaders(capability: string): Record<string, string> {
    return { Authorization: `Bearer ${capability}` };
  }

  return {
    async bootstrap(code) {
      const body = JSON.stringify({
        host_protocol_version: HOST_PROTOCOL_VERSION,
        bundle_id: CLIENT_BUNDLE_ID,
        code,
      });
      return request(
        BOOTSTRAP_PATH,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
          ...policy,
        },
        validateBootstrapResponse,
      );
    },

    async getSession(capability) {
      return request(
        SESSION_PATH,
        { method: "GET", headers: authHeaders(capability), ...policy },
        validateHostSession,
      );
    },

    async getState(capability) {
      return request(
        STATE_PATH,
        { method: "GET", headers: authHeaders(capability), ...policy },
        validateEngineEnvelope,
      );
    },

    async postCommand(capability, commandRequest) {
      return request(
        COMMANDS_PATH,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", ...authHeaders(capability) },
          body: JSON.stringify(commandRequest),
          ...policy,
        },
        validateEngineEnvelope,
      );
    },

    async getOperation(capability, requestId) {
      return request(
        `${OPERATIONS_PATH}/${requestId}`,
        { method: "GET", headers: authHeaders(capability), ...policy },
        validateOperationResponse,
      );
    },
  };
}
