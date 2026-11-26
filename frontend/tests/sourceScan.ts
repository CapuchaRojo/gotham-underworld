import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

/** Read a project source file relative to this helper (tests/), cwd-independent. */
export function readSource(rel: string): string {
  return readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf8");
}

/** Strip line + block comments so documentation may *name* forbidden modules. */
export function stripComments(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/[^\n]*/g, "$1");
}

/**
 * Tokens that may only appear in the live path. A presentational interaction
 * module must never import or invoke any of them.
 */
export const LIVE_TRANSPORT_TOKENS = [
  "liveEngine",
  "LiveEngineProvider",
  "host.ts",
  "outbox",
  "XMLHttpRequest",
  "fetch(",
] as const;

/** Return every live-transport token that appears in real code (comments ignored). */
export function findLiveTransportTokens(source: string): string[] {
  const code = stripComments(source);
  return LIVE_TRANSPORT_TOKENS.filter((token) => code.includes(token));
}
