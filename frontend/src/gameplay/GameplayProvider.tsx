// PROVISIONAL — reconcile against bridge source.
//
// React provider boundary for the SYNTHETIC PREVIEW. It resolves to the
// behavior-preserving `createPreviewGameplayClient` and serves authored
// fixtures only — never live engine data. The live engine has its own,
// distinct provider (`LiveEngineProvider.tsx`) and is NOT routed through this
// file; `EngineProvider.tsx` is the explicit mount-time selection point.

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import type { ReactNode } from "react";
import { SCENARIOS } from "../fixtures";
import type { Scenario, ScenarioId } from "../types";
import type {
  ConnectionState,
  EngineMode,
  EngineStatus,
  GameplayClient,
  PlayerState,
} from "./types";
import {
  PREVIEW_ENGINE_STATUS,
  createPreviewGameplayClient,
  resolveScenario,
  scenarioToPlayerState,
} from "./preview";

export interface GameplayContextValue {
  /** Explicit discriminator: this provider always serves synthetic preview. */
  mode: EngineMode;
  /** React-facing gameplay contract (currently the preview implementation). */
  client: GameplayClient;
  connectionState: ConnectionState;
  engineStatus: EngineStatus;
  /**
   * The authored read-only fixture currently on screen. Existing views read
   * this shape directly; they will migrate to `playerState` in a later task.
   */
  scenario: Scenario;
  /** Player-safe projection of the current scenario (provisional contract). */
  playerState: PlayerState;
  availableScenarios: Scenario[];
  /** Dev/QA-only scenario selection (the UI gates this behind Developer mode). */
  selectScenario: (id: ScenarioId) => void;
}

const DEFAULT_SCENARIO_ID: ScenarioId = "stable";
const DEFAULT_SCENARIO = resolveScenario(SCENARIOS, DEFAULT_SCENARIO_ID);

const FALLBACK_CLIENT = createPreviewGameplayClient({
  getScenario: () => DEFAULT_SCENARIO,
});

/** Safe fallback so `useGameplay` works outside a provider (player-safe default). */
const FALLBACK: GameplayContextValue = {
  mode: "preview",
  client: FALLBACK_CLIENT,
  connectionState: FALLBACK_CLIENT.connectionState,
  engineStatus: PREVIEW_ENGINE_STATUS,
  scenario: DEFAULT_SCENARIO,
  playerState: scenarioToPlayerState(DEFAULT_SCENARIO),
  availableScenarios: SCENARIOS,
  selectScenario: () => {},
};

const GameplayContext = createContext<GameplayContextValue>(FALLBACK);

export function GameplayProvider({ children }: { children: ReactNode }) {
  const [scenario, setScenarioState] = useState<Scenario>(DEFAULT_SCENARIO);
  const scenarioRef = useRef<Scenario>(scenario);

  const selectScenario = useCallback((id: ScenarioId) => {
    const next = resolveScenario(SCENARIOS, id);
    scenarioRef.current = next;
    setScenarioState(next);
  }, []);

  // Stable across renders: the client observes the live scenario through the
  // ref, so it never needs to be rebuilt when selection changes.
  const client = useMemo<GameplayClient>(
    () => createPreviewGameplayClient({ getScenario: () => scenarioRef.current }),
    [],
  );

  const playerState = useMemo(() => scenarioToPlayerState(scenario), [scenario]);

  const value = useMemo<GameplayContextValue>(
    () => ({
      mode: "preview",
      client,
      connectionState: client.connectionState,
      engineStatus: PREVIEW_ENGINE_STATUS,
      scenario,
      playerState,
      availableScenarios: SCENARIOS,
      selectScenario,
    }),
    [client, scenario, playerState, selectScenario],
  );

  return (
    <GameplayContext.Provider value={value}>{children}</GameplayContext.Provider>
  );
}

export function useGameplay(): GameplayContextValue {
  return useContext(GameplayContext);
}

/** Explicit alias: `GameplayProvider` IS the preview engine. */
export const PreviewGameplayProvider = GameplayProvider;
