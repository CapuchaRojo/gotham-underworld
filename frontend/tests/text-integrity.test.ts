import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../../", import.meta.url));
const decoder = new TextDecoder("utf-8", { fatal: true });
// Escaped signatures keep the detector itself valid UTF-8 source.
const artifacts = /\ufffd|\u00e2[\u0080\u20ac\u2020]|\u00c3\u00a2|\u00c2[\u0080-\u00bf]/u;
const brokenMilestoneHeading = /^#{1,6}\s+M030-C2B[^\r\n]* \? /mu;

function files(directory: string, extension: RegExp): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? files(path, extension) : extension.test(entry.name) ? [path] : [];
  });
}

function text(path: string): string {
  return decoder.decode(readFileSync(path));
}

test("text integrity detector distinguishes corruption from valid Unicode and questions", () => {
  for (const corrupted of ["\u00e2\u20ac\u201d", "\u00e2\u2020\u2019", "\u00c3\u00a2\u20ac", "\ufffd"])
    assert.match(corrupted, artifacts);
  assert.doesNotMatch("Gotham \u2014 recovery \u2192 ready?", artifacts);
  assert.match("## M030-C2B isolated stabilization ? 2026-11-19", brokenMilestoneHeading);
  assert.doesNotMatch("## 5. Gameplay test: is one block actually fun?", brokenMilestoneHeading);
  assert.throws(() => decoder.decode(Uint8Array.of(0xc3, 0x28)), TypeError);
});

test("frontend source and tests are valid UTF-8 without known mojibake", () => {
  for (const path of [...files(join(root, "frontend/src"), /\.tsx?$/), ...files(join(root, "frontend/tests"), /\.tsx?$/)])
    assert.doesNotMatch(text(path), artifacts, path);
});

test("M030-C2B milestone headings retain their intended punctuation", () => {
  for (const path of [join(root, "README.md"), join(root, "PROJECT_STATE.md"), ...files(join(root, "docs"), /\.md$/)])
    assert.doesNotMatch(text(path), brokenMilestoneHeading, path);
});
