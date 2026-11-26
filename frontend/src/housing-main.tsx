import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { HousingPanel } from "./components/HousingPanel";
import { LocalEngineInspection } from "./components/LocalEngineInspectionView";
import { LiveEngineProvider } from "./gameplay/LiveEngineProvider";
import { createCapabilityStore, HOUSING_BUNDLE_ID } from "./gameplay/host";
import { createHousingHostClient } from "./gameplay/housingHost";
import { createOutbox } from "./gameplay/outbox";

function HousingApp() {
  const [host] = useState(createHousingHostClient);
  const [store] = useState(() => createCapabilityStore());
  const [outbox] = useState(() => createOutbox(host));
  return (
    <LiveEngineProvider hostClient={host} capabilityStore={store} bundleId={HOUSING_BUNDLE_ID}>
      <main className="noir-texture min-h-screen bg-background text-foreground">
        <HousingPanel host={host} store={store} outbox={outbox} />
        <LocalEngineInspection />
      </main>
    </LiveEngineProvider>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><HousingApp /></StrictMode>);
