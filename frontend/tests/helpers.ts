import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

/** Load a JSON fixture relative to this file (tests/), so paths are cwd-independent. */
export function loadJson<T = unknown>(rel: string): T {
  const url = new URL(rel.startsWith("../content/") ? "../" + rel : rel, import.meta.url);
  return JSON.parse(readFileSync(fileURLToPath(url), "utf8")) as T;
}
