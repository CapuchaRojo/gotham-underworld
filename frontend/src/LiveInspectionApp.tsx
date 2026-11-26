// Dev-only mount for the read-only local-engine inspection surface. This is a
// SEPARATE top-level tree from the default synthetic preview (`App.tsx`) and is
// never mounted in the published preview. It contains no mutation controls of
// any kind — pairing/session lifecycle is driven externally in this gate (real
// host pairing is BLOCKED here and remains a separate acceptance gate).

import { LiveEngineProvider } from "./gameplay/LiveEngineProvider";
import { LocalEngineInspection } from "./components/LocalEngineInspectionView";

export default function LiveInspectionApp() {
  return (
    <div className="noir-texture min-h-screen bg-background text-foreground">
      <LiveEngineProvider>
        <LocalEngineInspection />
      </LiveEngineProvider>
    </div>
  );
}
