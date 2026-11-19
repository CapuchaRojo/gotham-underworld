// Shared read-only display types for the Living Gotham Interface.
// Shapes mirror the authored engine's detached report structures; nothing here
// is runtime-simulated, persisted, or mutated.

export type PlaceKind = "region" | "neighborhood" | "poi";

export type AccessCode =
  | "PUB"
  | "HOME"
  | "WORK"
  | "CARE"
  | "ENT"
  | "SEC"
  | "HELP"
  | "VIS";

export interface Place {
  id: string;
  label: string;
  parentId: string | null;
  regionId: string;
  kind: PlaceKind;
  type: string;
  access: AccessCode[];
  economy: string[];
  security: string[];
  criminal: string[];
  civilian: string[];
  npcPool: string[];
  source: string;
}

/** Every travel mode present in the authored atlas. */
export type TravelMode = "walk" | "bus" | "rail" | "ferry" | "boat" | "car";
/** Modes that are actually implemented by the engine (car/boat are authored but not playable). */
export type ImplementedMode = "walk" | "bus" | "rail" | "ferry";

export type EdgeKind = "corridor" | "access";

export interface Edge {
  id: string;
  label: string;
  from: string;
  to: string;
  kind: EdgeKind;
  description: string;
  bidirectional: boolean;
  modes: Partial<Record<TravelMode, number>>;
  access: "public" | "authorized" | "location";
}

export type AccessState = "open" | "restricted" | "closed" | "not_discovered";

export interface RouteLeg {
  edgeId: string;
  label: string;
  from: string;
  to: string;
  mode: ImplementedMode;
  tu: number;
}

export interface RouteQuote {
  origin: string;
  destination: string;
  mode: ImplementedMode | "auto";
  cost: number;
  returnCost: number | null;
  roundTripCost: number;
  remainingTu: number;
  roundTripRemaining: number;
  affordable: boolean;
  roundTripAffordable: boolean;
  legs: RouteLeg[];
  modeChanges: number;
}

// ---------------------------------------------------------------------------
// Synthetic gameplay fixture types (display-only; clearly labeled preview data)
// ---------------------------------------------------------------------------

export type ScenarioId = "stable" | "pressure" | "uncertain";

export type WorkAvailability = "available" | "unavailable";

export interface WorkCard {
  id: string;
  title: string;
  pay: number | null;
  actions: number;
  placeId: string;
  availability: WorkAvailability;
  reason?: string;
  expiry?: string;
  note: string;
}

export type CommitmentState =
  | "open"
  | "pending"
  | "fulfilled"
  | "cancelled"
  | "refused"
  | "missed"
  | "withdrawn";

export interface Commitment {
  id: string;
  title: string;
  state: CommitmentState;
  detail: string;
  dueDay?: number;
}

export interface MoneyState {
  cash: number;
  arrears: number;
  supportDebt: number;
  prepaid: number;
}

export interface HousingState {
  status: "current" | "grace" | "overdue";
  arrears: number;
  prepaid: number;
  nextDueDay: number;
}

export interface BudgetState {
  actionsUsed: number;
  actionsMax: number;
  tuUsed: number;
  tuMax: number;
}

export type AdoptionState = "active" | "pending" | "not_adopted";

export type SourceKind = "contact" | "institution" | "own";
export type Confidence = "documented" | "unconfirmed" | "unknown";

export interface Observation {
  id: string;
  incidentId: string;
  incidentTitle: string;
  claim: string;
  sourceId: string;
  sourceName: string;
  sourceKind: SourceKind;
  confidence: Confidence;
  limitation: string;
}

export interface ContactCard {
  id: string;
  name: string;
  role: string;
  personality: string;
  standing: number;
  known: string;
}

export type InstitutionKind = "civilian" | "police_intake";

export interface InstitutionRecord {
  id: string;
  name: string;
  kind: InstitutionKind;
  staff: string;
  placeId: string;
  status: "queued" | "clarification_requested" | "documented" | "closed_insufficient";
  classification: string;
  credibility: "unestablished" | "needs_documentation" | "documented";
  note: string;
}

export interface RestrictedRoute {
  edgeId: string;
  label: string;
  reason: string;
}

export interface Scenario {
  id: ScenarioId;
  label: string;
  summary: string;
  day: number;
  locationId: string;
  money: MoneyState;
  housing: HousingState;
  budget: BudgetState;
  adoption: AdoptionState;
  work: WorkCard[];
  commitments: Commitment[];
  observations: Observation[];
  contacts: ContactCard[];
  institutions: InstitutionRecord[];
  restrictedRoute?: RestrictedRoute;
  undiscoveredPlaceId?: string;
}
