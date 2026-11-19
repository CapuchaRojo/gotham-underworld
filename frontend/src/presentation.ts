import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useState,
} from "react";
import type { ReactNode } from "react";

/**
 * Presentation mode controls how the same simulation is *displayed*.
 *
 * - `player`: the genuine player-facing interface (default on every fresh load).
 * - `developer`: Developer Inspection — QA scenarios, raw atlas IDs, and
 *   diagnostic details may appear here. This is presentation-only; it never
 *   changes scenario selection or any gameplay/fixture state.
 *
 * Mode is transient UI state only. It is never persisted (no localStorage,
 * sessionStorage, or cookies), so a refresh always returns to player mode.
 */
export type PresentationMode = "player" | "developer";

export const DEFAULT_PRESENTATION_MODE: PresentationMode = "player";

/** Pure flip used by the toggle; testable without rendering React. */
export function togglePresentationMode(mode: PresentationMode): PresentationMode {
  return mode === "player" ? "developer" : "player";
}

/**
 * Removes short internal identifier references that are embedded inside
 * otherwise player-readable copy (e.g. "Uptown General Store (p032)").
 * Player mode renders the human label only; Developer Inspection preserves the
 * raw reference. The pattern is deliberately narrow — a single letter followed
 * by 2–3 digits inside parentheses — so ordinary parentheticals are untouched.
 */
const INTERNAL_REF_PATTERN = /\s*\([a-z]\d{2,3}\)/g;

export function playerSafeText(text: string): string {
  return text.replace(INTERNAL_REF_PATTERN, "").replace(/\s{2,}/g, " ").trim();
}

export interface PresentationModeContextValue {
  mode: PresentationMode;
  isDeveloper: boolean;
  setMode: (mode: PresentationMode) => void;
  toggleMode: () => void;
}

/**
 * Safe fallback so `usePresentationMode` works outside a provider (e.g. in
 * isolated component tests) by always behaving like player mode.
 */
const FALLBACK: PresentationModeContextValue = {
  mode: DEFAULT_PRESENTATION_MODE,
  isDeveloper: false,
  setMode: () => {},
  toggleMode: () => {},
};

export const PresentationModeContext =
  createContext<PresentationModeContextValue>(FALLBACK);

export function PresentationModeProvider({
  initialMode = DEFAULT_PRESENTATION_MODE,
  children,
}: {
  initialMode?: PresentationMode;
  children: ReactNode;
}) {
  const [mode, setModeState] = useState<PresentationMode>(initialMode);

  const setMode = useCallback((next: PresentationMode) => {
    setModeState(next);
  }, []);

  const toggleMode = useCallback(() => {
    setModeState((current) => togglePresentationMode(current));
  }, []);

  const value: PresentationModeContextValue = {
    mode,
    isDeveloper: mode === "developer",
    setMode,
    toggleMode,
  };

  return createElement(
    PresentationModeContext.Provider,
    { value },
    children,
  );
}

export function usePresentationMode(): PresentationModeContextValue {
  return useContext(PresentationModeContext);
}
