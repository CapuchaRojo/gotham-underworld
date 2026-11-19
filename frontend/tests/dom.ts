import { JSDOM } from "jsdom";

// Install a jsdom window onto the Node global so @testing-library/react can
// render into a real DOM. node:test runs each test file in its own process, so
// this global setup stays isolated per file.
const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "http://localhost/",
  pretendToBeVisual: true,
});

const win = dom.window;
const g = globalThis as unknown as Record<string, unknown>;

for (const key of [
  "window",
  "document",
  "navigator",
  "HTMLElement",
  "SVGElement",
  "Element",
  "Node",
  "DocumentFragment",
  "Text",
  "Comment",
  "getComputedStyle",
  "requestAnimationFrame",
  "cancelAnimationFrame",
  "MutationObserver",
  "Event",
  "CustomEvent",
  "MouseEvent",
  "KeyboardEvent",
  "FocusEvent",
  "InputEvent",
]) {
  try {
    Object.defineProperty(g, key, {
      value: (win as unknown as Record<string, unknown>)[key],
      writable: true,
      configurable: true,
    });
  } catch {
    // Some globals (e.g. `navigator` in Node 21+) are read-only getters; skip.
  }
}

// React 18's act() environment flag; silences act warnings under RTL.
(g as unknown as { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT =
  true;
