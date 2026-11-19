import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { loadJson } from "./helpers";

function readProjectFile(rel: string): string {
  return readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf8");
}

test("browser title is Gotham: The Goon with no my-app remnant", () => {
  const html = readProjectFile("../index.html");
  assert.match(
    html,
    /<title>Gotham: The Goon<\/title>/,
    "index.html must carry the corrected browser title",
  );
  assert.ok(
    !html.toLowerCase().includes("my-app"),
    "index.html must not retain the my-app placeholder",
  );
});

test("package name and typecheck script are finalized", () => {
  const pkg = loadJson<{ name: string; scripts: Record<string, string> }>("../package.json");
  assert.equal(pkg.name, "gotham-the-goon", "package.json name must be gotham-the-goon");
  assert.equal(pkg.scripts.typecheck, "tsc --noEmit", "typecheck script must run tsc --noEmit");
});
