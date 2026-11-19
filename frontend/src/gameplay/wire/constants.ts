// Binding compatibility constants for the M030-C1.3 Python browser host.
// These values are authoritative and must never be substituted — see
// docs/prd/m030-c2-gtg13a-liveengine.md §Integrations.

/** Authoritative engine bundle release (NOT the merge SHA f2e75dd…, NOT a repo SHA). */
export const ENGINE_RELEASE = "1a129e83be6629b7a27c2826626856ec7fae85f7" as const;

export const HOST_PROTOCOL_VERSION = 1 as const;
export const BRIDGE_PROTOCOL_VERSION = 1 as const;

export const ENGINE_MODE = "local_engine" as const;
export const SESSION_LIFETIME = "process" as const;

/** Host authority scheme/host are fixed; only the persisted port varies. */
export const HOST_SCHEME = "http" as const;
export const HOST_HOSTNAME = "127.0.0.1" as const;

/** Request body size ceilings (bytes). */
export const BOOTSTRAP_BODY_MAX_BYTES = 1024;
export const API_BODY_MAX_BYTES = 16384;

/** Maximum length of any command `arguments` string value. */
export const ARGUMENT_MAX_LENGTH = 256;

/** career_id / lineage_id / request_id: [A-Za-z0-9][A-Za-z0-9._-]{0,127}. */
export const ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;

export interface HostAuthority {
  scheme: "http";
  host: "127.0.0.1";
  port: number;
}

/**
 * The host authority must be exactly `http://127.0.0.1:<port>`.
 * `localhost` is NOT interchangeable and must be rejected (403 UNSAFE_HOST).
 */
export function parseHostAuthority(value: string): HostAuthority | null {
  const match = /^http:\/\/127\.0\.0\.1:([0-9]{1,5})$/.exec(value);
  if (!match) return null;
  const port = Number(match[1]);
  if (!Number.isInteger(port) || port < 1 || port > 65535) return null;
  return { scheme: "http", host: "127.0.0.1", port };
}

/** `secrets.token_urlsafe(32)` => 43-char base64url (capability and bootstrap code). */
export function isBase64Url43(value: string): boolean {
  return /^[A-Za-z0-9_-]{43}$/.test(value);
}
