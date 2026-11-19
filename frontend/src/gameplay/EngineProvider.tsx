// Explicit, mount-time selection of which engine backs the app.
//
// `preview` (the default) mounts the synthetic fixture provider; `live` mounts
// the fail-closed local-engine provider. This is the ONLY place the choice is
// made, and it never changes at runtime: a dropped live connection does NOT
// switch back to preview — the live provider simply reports `disconnected` and
// serves no career state.

import type { ReactNode } from "react";
import type { EngineMode } from "./types";
import { GameplayProvider } from "./GameplayProvider";
import { LiveEngineProvider } from "./LiveEngineProvider";

export type { EngineMode };

export interface EngineProviderProps {
  mode?: EngineMode;
  children: ReactNode;
}

export function EngineProvider({ mode = "preview", children }: EngineProviderProps) {
  if (mode === "live") {
    return <LiveEngineProvider>{children}</LiveEngineProvider>;
  }
  return <GameplayProvider>{children}</GameplayProvider>;
}
