// PROVISIONAL — reconcile against bridge source.
//
// Behavior-preserving preview provider over the three synthetic QA scenarios.
// It serves the same read-only fixture data the app already renders, but behind
// the `GameplayClient` boundary. Mutations are explicitly UNSUPPORTED: the
// preview never simulates a successful mutation, never mutates a career, and
// never persists. There is no network access of any kind here.

import type { Scenario, ScenarioId } from "../types";
import type {
  ActionReceipt,
  ConnectionState,
  Eligibility,
  EngineStatus,
  GameplayClient,
  GameplayErrorCode,
  GameplayResult,
  PlayerState,
  TravelAuthorization,
} from "./types";

export const PREVIEW_CONNECTION_STATE: ConnectionState = "connected";

/**
 * The preview's "connection" is to in-memory fixtures, not a live bridge. The
 * connection state is `connected` only in that sense — the label below makes
 * the synthetic context unmistakable.
 */
export const PREVIEW_ENGINE_STATUS: EngineStatus = {
  kind: "synthetic",
  connectionState: PREVIEW_CONNECTION_STATE,
  label: "Synthetic preview — simulated display data",
  contextLabel: "Synthetic display data",
  detail: "Fixture-driven preview. No live engine connection, no persistence.",
};

export const UNSUPPORTED_MESSAGE =
  "That action can’t be taken in the synthetic preview — there is no live engine to commit it to.";

function success<T>(value: T): GameplayResult<T> {
  return { ok: true, value };
}

function fail<T>(
  code: GameplayErrorCode,
  message: string,
  reasons?: string[],
): GameplayResult<T> {
  return reasons ? { ok: false, code, message, reasons } : { ok: false, code, message };
}

/** `GameplayResult<never>` is assignable to any `GameplayResult<T>`. */
function unsupported(message = UNSUPPORTED_MESSAGE): GameplayResult<never> {
  return { ok: false, code: "unsupported", message };
}

/**
 * Player-safe projection of a synthetic scenario into the provisional
 * `PlayerState`. Pure and side-effect-free.
 */
export function scenarioToPlayerState(scenario: Scenario): PlayerState {
  return {
    day: scenario.day,
    locationId: scenario.locationId,
    money: { ...scenario.money },
    budget: { ...scenario.budget },
    housing: { ...scenario.housing },
    opportunities: scenario.work.map((w) => ({
      id: w.id,
      title: w.title,
      pay: w.pay,
      actions: w.actions,
      placeId: w.placeId,
      executable: w.availability === "available",
      blockReasons:
        w.availability === "available" ? [] : [w.reason ?? "Unavailable"],
      ...(w.expiry !== undefined ? { expiry: w.expiry } : {}),
      note: w.note,
    })),
    commitments: scenario.commitments,
    contacts: scenario.contacts,
    observations: scenario.observations,
    institutions: scenario.institutions,
  };
}

/** Minimal read handle the preview client uses to observe the active scenario. */
export interface PreviewScenarioSource {
  getScenario(): Scenario;
}

/**
 * Build the preview implementation of `GameplayClient`. Selection of which
 * synthetic scenario is active lives with the React provider (see
 * `GameplayProvider.tsx`); this client only observes it through `source`.
 */
export function createPreviewGameplayClient(
  source: PreviewScenarioSource,
): GameplayClient {
  return {
    connectionState: PREVIEW_CONNECTION_STATE,

    getPlayerState(): PlayerState {
      return scenarioToPlayerState(source.getScenario());
    },

    async getRouteQuote() {
      // The preview has no authoritative engine route quote; the existing
      // client-side Dijkstra remains a clearly-labeled non-authoritative
      // preview only. We never claim authority here.
      return unsupported();
    },

    async authorizeTravel(): Promise<GameplayResult<TravelAuthorization>> {
      return unsupported();
    },

    async getEligibility(choiceId: string): Promise<GameplayResult<Eligibility>> {
      const work = source.getScenario().work.find((w) => w.id === choiceId);
      if (!work) {
        return fail<Eligibility>("ineligible", "That choice isn’t part of this scenario.", [
          "Choice not found",
        ]);
      }
      return success({
        choiceId,
        executable: work.availability === "available",
        reasons:
          work.availability === "available" ? [] : [work.reason ?? "Unavailable"],
      });
    },

    async executeAction(): Promise<GameplayResult<ActionReceipt>> {
      return unsupported();
    },

    async recover(): Promise<GameplayResult<ActionReceipt>> {
      return unsupported();
    },

    async restore(): Promise<GameplayResult<PlayerState>> {
      return unsupported(
        "Save restore isn’t available in the synthetic preview — there is no persisted career.",
      );
    },
  };
}

/** Convenience for selecting a scenario by id from the authored set. */
export function resolveScenario(
  scenarios: Scenario[],
  id: ScenarioId,
): Scenario {
  return scenarios.find((s) => s.id === id) ?? scenarios[0];
}
