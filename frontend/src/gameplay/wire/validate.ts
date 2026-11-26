// Runtime validators for every Python host response. A value is promoted to
// trusted live state only after it passes the matching validator: unknown
// fields, wrong types, and unsafe values are all rejected. See
// docs/prd/m030-c2-gtg13a-liveengine.md §Integrations.

import {
  ARGUMENT_MAX_LENGTH,
  BRIDGE_PROTOCOL_VERSION,
  ENGINE_MODE,
  ENGINE_RELEASE,
  HOST_PROTOCOL_VERSION,
  ID_PATTERN,
  SESSION_LIFETIME,
  isBase64Url43,
} from "./constants";
import { COMMAND_ARGUMENTS, COMMANDS } from "./types";
import type {
  ApiErrorEnvelope,
  BootstrapRequest,
  BootstrapResponse,
  Command,
  CommandRequest,
  EngineEnvelope,
  HostErrorEnvelope,
  HostSession,
  OperationResponse,
  Opportunity,
  OpportunityOption,
  PlayerProjection,
  QuoteResponse,
  Receipt,
  TravelQuoteRequest,
} from "./types";

export interface ValidationError {
  code: string;
  message: string;
  path: string;
}

export type Result<T> = { ok: true; value: T } | { ok: false; error: ValidationError };

export function ok<T>(value: T): Result<T> {
  return { ok: true, value };
}

export function fail(code: string, message: string, path = "$"): Result<never> {
  return { ok: false, error: { code, message, path } };
}

// ---------------------------------------------------------------------------
// Primitive helpers
// ---------------------------------------------------------------------------

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasOwn(value: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(value, key);
}

function requiredField(value: Record<string, unknown>, key: string, path: string): Result<unknown> {
  if (!hasOwn(value, key)) return fail("missing_field", `${path}.${key} is required`, path);
  return ok(value[key]);
}

function assertExactKeys(
  value: Record<string, unknown>,
  allowed: readonly string[],
  path: string,
): Result<undefined> {
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) {
      return fail("unknown_field", `${path} has unexpected field ${JSON.stringify(key)}`, path);
    }
  }
  return ok(undefined);
}

function stringField(value: Record<string, unknown>, key: string, path: string): Result<string> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (typeof raw !== "string") return fail("invalid_type", `${path}.${key} must be a string`, path);
  return ok(raw);
}

function idField(value: Record<string, unknown>, key: string, path: string): Result<string> {
  const result = stringField(value, key, path);
  if (!result.ok) return result;
  if (!ID_PATTERN.test(result.value)) {
    return fail("invalid_id", `${path}.${key} must match ${ID_PATTERN}`, path);
  }
  return result;
}

function booleanField(value: Record<string, unknown>, key: string, path: string): Result<boolean> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (typeof raw !== "boolean") return fail("invalid_type", `${path}.${key} must be a boolean`, path);
  return ok(raw);
}

function numberField(value: Record<string, unknown>, key: string, path: string): Result<number> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (typeof raw !== "number" || !Number.isFinite(raw)) {
    return fail("invalid_number", `${path}.${key} must be a finite number`, path);
  }
  return ok(raw);
}

function integerField(
  value: Record<string, unknown>,
  key: string,
  path: string,
  options: { nonNegative?: boolean } = {},
): Result<number> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (typeof raw !== "number" || !Number.isSafeInteger(raw)) {
    return fail("invalid_integer", `${path}.${key} must be a safe integer`, path);
  }
  if (options.nonNegative && raw < 0) {
    return fail("invalid_value", `${path}.${key} must be >= 0`, path);
  }
  return ok(raw);
}

function nullableNumberField(
  value: Record<string, unknown>,
  key: string,
  path: string,
): Result<number | null> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (raw === null) return ok(null);
  if (typeof raw !== "number" || !Number.isFinite(raw)) {
    return fail("invalid_number", `${path}.${key} must be a finite number or null`, path);
  }
  return ok(raw);
}

function nullableIntegerField(
  value: Record<string, unknown>,
  key: string,
  path: string,
): Result<number | null> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (raw === null) return ok(null);
  if (typeof raw !== "number" || !Number.isSafeInteger(raw) || raw < 0) {
    return fail("invalid_integer", `${path}.${key} must be a nonnegative safe integer or null`, path);
  }
  return ok(raw);
}

function nullableStringField(
  value: Record<string, unknown>,
  key: string,
  path: string,
): Result<string | null> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (raw === null) return ok(null);
  if (typeof raw !== "string") return fail("invalid_type", `${path}.${key} must be a string or null`, path);
  return ok(raw);
}

function optionalBooleanField(
  value: Record<string, unknown>,
  key: string,
  path: string,
): Result<boolean | undefined> {
  const raw = value[key];
  if (raw === undefined) return ok(undefined);
  if (typeof raw !== "boolean") return fail("invalid_type", `${path}.${key} must be a boolean`, path);
  return ok(raw);
}

function optionalNullableNumberField(
  value: Record<string, unknown>,
  key: string,
  path: string,
): Result<number | null | undefined> {
  const raw = value[key];
  if (raw === undefined) return ok(undefined);
  if (raw === null) return ok(null);
  if (typeof raw !== "number" || !Number.isFinite(raw)) {
    return fail("invalid_number", `${path}.${key} must be a finite number or null`, path);
  }
  return ok(raw);
}

function arrayField(value: Record<string, unknown>, key: string, path: string): Result<unknown[]> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (!Array.isArray(raw)) return fail("invalid_type", `${path}.${key} must be an array`, path);
  return ok(raw);
}

function literalField<T extends string | number>(
  value: Record<string, unknown>,
  key: string,
  path: string,
  allowed: readonly T[],
): Result<T> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (!(allowed as readonly unknown[]).includes(raw)) {
    return fail("invalid_value", `${path}.${key} must be one of ${JSON.stringify(allowed)}`, path);
  }
  return ok(raw as T);
}

function protocolVersionField(
  value: Record<string, unknown>,
  key: string,
  path: string,
  expected: number,
): Result<number> {
  const raw = value[key];
  if (raw === undefined) return fail("missing_field", `${path}.${key} is required`, path);
  if (raw !== expected) return fail("invalid_value", `${path}.${key} must be ${expected}`, path);
  return ok(raw as number);
}

function validateArray<T>(
  value: unknown[],
  _path: string,
  item: (entry: unknown, index: number) => Result<T>,
): Result<T[]> {
  const out: T[] = [];
  for (let i = 0; i < value.length; i += 1) {
    const result = item(value[i], i);
    if (!result.ok) return result;
    out.push(result.value);
  }
  return ok(out);
}

function validateStringRecord(value: unknown, path: string): Result<Record<string, string>> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const out: Record<string, string> = {};
  for (const [key, raw] of Object.entries(value)) {
    if (typeof raw !== "string") return fail("invalid_type", `${path}.${key} must be a string`, path);
    if (raw.length > ARGUMENT_MAX_LENGTH) {
      return fail("argument_too_long", `${path}.${key} exceeds ${ARGUMENT_MAX_LENGTH} chars`, path);
    }
    out[key] = raw;
  }
  return ok(out);
}

// ---------------------------------------------------------------------------
// Session / bootstrap
// ---------------------------------------------------------------------------

const HOST_SESSION_KEYS = [
  "host_protocol_version",
  "bridge_protocol_version",
  "bundle_id",
  "manifest_sha256",
  "engine_release",
  "instance_id",
  "mode",
  "session_lifetime",
] as const;

function validateHostSessionFields(value: Record<string, unknown>): Result<HostSession> {
  const hpv = protocolVersionField(value, "host_protocol_version", "$", HOST_PROTOCOL_VERSION);
  if (!hpv.ok) return hpv;
  const bpv = protocolVersionField(value, "bridge_protocol_version", "$", BRIDGE_PROTOCOL_VERSION);
  if (!bpv.ok) return bpv;
  const bundle = stringField(value, "bundle_id", "$");
  if (!bundle.ok) return bundle;
  const manifest = stringField(value, "manifest_sha256", "$");
  if (!manifest.ok) return manifest;
  if (!/^[0-9a-f]{64}$/.test(manifest.value)) {
    return fail("invalid_value", "$.manifest_sha256 must be 64-char lowercase hex", "$");
  }
  const release = stringField(value, "engine_release", "$");
  if (!release.ok) return release;
  if (release.value !== ENGINE_RELEASE) {
    return fail("invalid_value", "$.engine_release does not match the bound engine_release", "$");
  }
  const instance = stringField(value, "instance_id", "$");
  if (!instance.ok) return instance;
  const mode = literalField(value, "mode", "$", [ENGINE_MODE]);
  if (!mode.ok) return mode;
  const lifetime = literalField(value, "session_lifetime", "$", [SESSION_LIFETIME]);
  if (!lifetime.ok) return lifetime;
  return ok({
    host_protocol_version: 1,
    bridge_protocol_version: 1,
    bundle_id: bundle.value,
    manifest_sha256: manifest.value,
    engine_release: ENGINE_RELEASE,
    instance_id: instance.value,
    mode: "local_engine",
    session_lifetime: "process",
  });
}

export function validateHostSession(value: unknown): Result<HostSession> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected a host session object", "$");
  const exact = assertExactKeys(value, HOST_SESSION_KEYS, "$");
  if (!exact.ok) return exact;
  return validateHostSessionFields(value);
}

export function validateBootstrapResponse(value: unknown): Result<BootstrapResponse> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected a bootstrap response object", "$");
  const exact = assertExactKeys(value, [...HOST_SESSION_KEYS, "capability"], "$");
  if (!exact.ok) return exact;
  const session = validateHostSessionFields(value);
  if (!session.ok) return session;
  const capability = stringField(value, "capability", "$");
  if (!capability.ok) return capability;
  if (!isBase64Url43(capability.value)) {
    return fail("invalid_capability", "$.capability must be a 43-char base64url token", "$");
  }
  return ok({ ...session.value, capability: capability.value });
}

// ---------------------------------------------------------------------------
// Player projection
// ---------------------------------------------------------------------------

function validatePlayer(
  value: unknown,
  path: string,
): Result<PlayerProjection["player"]> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(value, ["cash", "heat", "custody"], path);
  if (!exact.ok) return exact;
  const cash = numberField(value, "cash", path);
  if (!cash.ok) return cash;
  const heat = numberField(value, "heat", path);
  if (!heat.ok) return heat;
  const custody = literalField(value, "custody", path, ["free", "pretrial"] as const);
  if (!custody.ok) return custody;
  return ok({ cash: cash.value, heat: heat.value, custody: custody.value });
}

function validateBudgets(
  value: unknown,
  path: string,
): Result<PlayerProjection["budgets"]> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(
    value,
    ["daily_actions", "actions_remaining", "daily_travel_units", "travel_units_remaining"],
    path,
  );
  if (!exact.ok) return exact;
  const daily = integerField(value, "daily_actions", path, { nonNegative: true });
  if (!daily.ok) return daily;
  const remaining = integerField(value, "actions_remaining", path, { nonNegative: true });
  if (!remaining.ok) return remaining;
  const dailyTu = integerField(value, "daily_travel_units", path, { nonNegative: true });
  if (!dailyTu.ok) return dailyTu;
  const tuRemaining = nullableIntegerField(value, "travel_units_remaining", path);
  if (!tuRemaining.ok) return tuRemaining;
  return ok({
    daily_actions: daily.value,
    actions_remaining: remaining.value,
    daily_travel_units: dailyTu.value,
    travel_units_remaining: tuRemaining.value,
  });
}

function validateLocation(
  value: unknown,
  path: string,
): Result<PlayerProjection["location"]> {
  if (value === null) return ok(null);
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object or null`, path);
  const exact = assertExactKeys(value, ["id", "label"], path);
  if (!exact.ok) return exact;
  const id = stringField(value, "id", path);
  if (!id.ok) return id;
  const label = stringField(value, "label", path);
  if (!label.ok) return label;
  return ok({ id: id.value, label: label.value });
}

function validateSystems(
  value: unknown,
  path: string,
): Result<PlayerProjection["systems"]> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(value, ["navigation", "daily_life", "ordinary", "mobility"], path);
  if (!exact.ok) return exact;
  const navigation = literalField(value, "navigation", path, ["not_adopted", "pending", "active"] as const);
  if (!navigation.ok) return navigation;
  const dailyLife = literalField(value, "daily_life", path, ["not_adopted", "pending", "active"] as const);
  if (!dailyLife.ok) return dailyLife;
  const ordinary = literalField(value, "ordinary", path, ["not_adopted", "pending", "active"] as const);
  if (!ordinary.ok) return ordinary;
  const mobility = literalField(value, "mobility", path, ["not_adopted", "pending", "active"] as const);
  if (!mobility.ok) return mobility;
  return ok({
    navigation: navigation.value,
    daily_life: dailyLife.value,
    ordinary: ordinary.value,
    mobility: mobility.value,
  });
}

function validateHousing(
  value: unknown,
  path: string,
): Result<PlayerProjection["housing"]> {
  if (value === null) return ok(null);
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object or null`, path);
  const exact = assertExactKeys(value, ["status", "home_id", "next_due_day", "arrears", "prepaid"], path);
  if (!exact.ok) return exact;
  const status = literalField(value, "status", path, ["current", "grace"] as const);
  if (!status.ok) return status;
  const homeId = stringField(value, "home_id", path);
  if (!homeId.ok) return homeId;
  const nextDueDay = integerField(value, "next_due_day", path, { nonNegative: true });
  if (!nextDueDay.ok) return nextDueDay;
  const arrears = numberField(value, "arrears", path);
  if (!arrears.ok) return arrears;
  const prepaid = numberField(value, "prepaid", path);
  if (!prepaid.ok) return prepaid;
  return ok({
    status: status.value,
    home_id: homeId.value,
    next_due_day: nextDueDay.value,
    arrears: arrears.value,
    prepaid: prepaid.value,
  });
}

function validateContacts(
  value: unknown,
  path: string,
): Result<PlayerProjection["contacts"]> {
  if (!Array.isArray(value)) return fail("invalid_type", `${path} must be an array`, path);
  return validateArray(value, path, (entry, index) => {
    const entryPath = `${path}[${index}]`;
    if (!isPlainObject(entry)) return fail("invalid_type", `${entryPath} must be an object`, entryPath);
    const exact = assertExactKeys(entry, ["id", "name", "role", "standing"], entryPath);
    if (!exact.ok) return exact;
    const id = stringField(entry, "id", entryPath);
    if (!id.ok) return id;
    const name = stringField(entry, "name", entryPath);
    if (!name.ok) return name;
    const role = stringField(entry, "role", entryPath);
    if (!role.ok) return role;
    const standing = numberField(entry, "standing", entryPath);
    if (!standing.ok) return standing;
    return ok({ id: id.value, name: name.value, role: role.value, standing: standing.value });
  });
}

function validateOptionArguments(
  value: unknown,
  path: string,
): Result<OpportunityOption["arguments"]> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const keys = Object.keys(value).sort().join(",");
  if (keys === "choice_id,option_id") {
    const exact = assertExactKeys(value, ["choice_id", "option_id"], path);
    if (!exact.ok) return exact;
    const choiceId = stringField(value, "choice_id", path);
    if (!choiceId.ok) return choiceId;
    const optionId = stringField(value, "option_id", path);
    if (!optionId.ok) return optionId;
    return ok({ choice_id: choiceId.value, option_id: optionId.value });
  }
  if (keys === "offer_id,option_id") {
    const exact = assertExactKeys(value, ["offer_id", "option_id"], path);
    if (!exact.ok) return exact;
    const offerId = stringField(value, "offer_id", path);
    if (!offerId.ok) return offerId;
    const optionId = stringField(value, "option_id", path);
    if (!optionId.ok) return optionId;
    return ok({ offer_id: offerId.value, option_id: optionId.value });
  }
  return fail("invalid_value", `${path} must be {choice_id, option_id} or {offer_id, option_id}`, path);
}

function validateOption(value: unknown, path: string): Result<OpportunityOption> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(
    value,
    ["id", "label", "availability", "reason", "action_cost", "tradeoff", "arguments"],
    path,
  );
  if (!exact.ok) return exact;
  const id = stringField(value, "id", path);
  if (!id.ok) return id;
  const label = stringField(value, "label", path);
  if (!label.ok) return label;
  const availability = literalField(value, "availability", path, ["available", "unavailable"] as const);
  if (!availability.ok) return availability;
  const reason = nullableStringField(value, "reason", path);
  if (!reason.ok) return reason;
  const actionCost = numberField(value, "action_cost", path);
  if (!actionCost.ok) return actionCost;
  const tradeoff = stringField(value, "tradeoff", path);
  if (!tradeoff.ok) return tradeoff;
  const argsRaw = requiredField(value, "arguments", path);
  if (!argsRaw.ok) return argsRaw;
  const args = validateOptionArguments(argsRaw.value, `${path}.arguments`);
  if (!args.ok) return args;
  return ok({
    id: id.value,
    label: label.value,
    availability: availability.value,
    reason: reason.value,
    action_cost: actionCost.value,
    tradeoff: tradeoff.value,
    arguments: args.value,
  });
}

function validateOpportunities(value: unknown, path: string): Result<Opportunity[]> {
  if (!Array.isArray(value)) return fail("invalid_type", `${path} must be an array`, path);
  return validateArray(value, path, (entry, index) => {
    const entryPath = `${path}[${index}]`;
    if (!isPlainObject(entry)) return fail("invalid_type", `${entryPath} must be an object`, entryPath);
    const exact = assertExactKeys(
      entry,
      ["id", "title", "situation", "speaker", "open_day", "expires_day", "state", "command", "options"],
      entryPath,
    );
    if (!exact.ok) return exact;
    const id = stringField(entry, "id", entryPath);
    if (!id.ok) return id;
    const title = stringField(entry, "title", entryPath);
    if (!title.ok) return title;
    const situation = stringField(entry, "situation", entryPath);
    if (!situation.ok) return situation;
    const speaker = stringField(entry, "speaker", entryPath);
    if (!speaker.ok) return speaker;
    const openDay = integerField(entry, "open_day", entryPath, { nonNegative: true });
    if (!openDay.ok) return openDay;
    const expiresDay = integerField(entry, "expires_day", entryPath, { nonNegative: true });
    if (!expiresDay.ok) return expiresDay;
    const state = stringField(entry, "state", entryPath);
    if (!state.ok) return state;
    const command = literalField(entry, "command", entryPath, ["choose", "ordinary_choose"] as const);
    if (!command.ok) return command;
    const optionsRaw = requiredField(entry, "options", entryPath);
    if (!optionsRaw.ok) return optionsRaw;
    if (!Array.isArray(optionsRaw.value)) {
      return fail("invalid_type", `${entryPath}.options must be an array`, entryPath);
    }
    const options = validateArray(optionsRaw.value, `${entryPath}.options`, (opt, optIndex) =>
      validateOption(opt, `${entryPath}.options[${optIndex}]`),
    );
    if (!options.ok) return options;
    return ok({
      id: id.value,
      title: title.value,
      situation: situation.value,
      speaker: speaker.value,
      open_day: openDay.value,
      expires_day: expiresDay.value,
      state: state.value,
      command: command.value,
      options: options.value,
    });
  });
}

function validateOutcomes(
  value: unknown,
  path: string,
): Result<PlayerProjection["outcomes"]> {
  if (!Array.isArray(value)) return fail("invalid_type", `${path} must be an array`, path);
  return validateArray(value, path, (entry, index) => {
    const entryPath = `${path}[${index}]`;
    if (!isPlainObject(entry)) return fail("invalid_type", `${entryPath} must be an object`, entryPath);
    const exact = assertExactKeys(entry, ["choice_id", "option_id", "day", "feedback"], entryPath);
    if (!exact.ok) return exact;
    const choiceId = stringField(entry, "choice_id", entryPath);
    if (!choiceId.ok) return choiceId;
    const optionId = stringField(entry, "option_id", entryPath);
    if (!optionId.ok) return optionId;
    const day = integerField(entry, "day", entryPath, { nonNegative: true });
    if (!day.ok) return day;
    const feedback = stringField(entry, "feedback", entryPath);
    if (!feedback.ok) return feedback;
    return ok({ choice_id: choiceId.value, option_id: optionId.value, day: day.value, feedback: feedback.value });
  });
}

function validateOrdinary(
  value: unknown,
  path: string,
): Result<NonNullable<PlayerProjection["ordinary"]>> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(value, ["employment", "assistance"], path);
  if (!exact.ok) return exact;
  const employment = numberField(value, "employment", path);
  if (!employment.ok) return employment;
  const assistanceRaw = requiredField(value, "assistance", path);
  if (!assistanceRaw.ok) return assistanceRaw;
  if (!isPlainObject(assistanceRaw.value)) {
    return fail("invalid_type", `${path}.assistance must be an object`, path);
  }
  const assistance = assistanceRaw.value;
  const assistExact = assertExactKeys(assistance, ["status", "amount", "due_day"], `${path}.assistance`);
  if (!assistExact.ok) return assistExact;
  const status = literalField(assistance, "status", `${path}.assistance`, [
    "unused",
    "owed",
    "overdue",
    "repaid",
    "declined",
  ] as const);
  if (!status.ok) return status;
  const amount = numberField(assistance, "amount", `${path}.assistance`);
  if (!amount.ok) return amount;
  const dueDay = nullableIntegerField(assistance, "due_day", `${path}.assistance`);
  if (!dueDay.ok) return dueDay;
  return ok({
    employment: employment.value,
    assistance: { status: status.value, amount: amount.value, due_day: dueDay.value },
  });
}

function validatePlayerProjection(value: unknown, path: string): Result<PlayerProjection> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(
    value,
    ["day", "player", "budgets", "location", "systems", "housing", "contacts", "opportunities", "outcomes", "ordinary"],
    path,
  );
  if (!exact.ok) return exact;
  for (const key of ["day", "player", "budgets", "location", "systems", "housing", "contacts", "opportunities", "outcomes"]) {
    if (!hasOwn(value, key)) return fail("missing_field", `${path}.${key} is required`, path);
  }
  const day = integerField(value, "day", path, { nonNegative: true });
  if (!day.ok) return day;
  const player = validatePlayer(value["player"], `${path}.player`);
  if (!player.ok) return player;
  const budgets = validateBudgets(value["budgets"], `${path}.budgets`);
  if (!budgets.ok) return budgets;
  const location = validateLocation(value["location"], `${path}.location`);
  if (!location.ok) return location;
  const systems = validateSystems(value["systems"], `${path}.systems`);
  if (!systems.ok) return systems;
  const housing = validateHousing(value["housing"], `${path}.housing`);
  if (!housing.ok) return housing;
  const contacts = validateContacts(value["contacts"], `${path}.contacts`);
  if (!contacts.ok) return contacts;
  const opportunities = validateOpportunities(value["opportunities"], `${path}.opportunities`);
  if (!opportunities.ok) return opportunities;
  const outcomes = validateOutcomes(value["outcomes"], `${path}.outcomes`);
  if (!outcomes.ok) return outcomes;

  let ordinary: NonNullable<PlayerProjection["ordinary"]> | undefined;
  if (hasOwn(value, "ordinary")) {
    const result = validateOrdinary(value["ordinary"], `${path}.ordinary`);
    if (!result.ok) return result;
    ordinary = result.value;
  }

  return ok({
    day: day.value,
    player: player.value,
    budgets: budgets.value,
    location: location.value,
    systems: systems.value,
    housing: housing.value,
    contacts: contacts.value,
    opportunities: opportunities.value,
    outcomes: outcomes.value,
    ...(ordinary !== undefined ? { ordinary } : {}),
  });
}

// ---------------------------------------------------------------------------
// Engine envelope / receipts / operations
// ---------------------------------------------------------------------------

function validateReceipt(value: unknown, path: string): Result<Receipt> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(value, ["request_id", "revision", "command_sequence", "command", "day", "status"], path);
  if (!exact.ok) return exact;
  const requestId = idField(value, "request_id", path);
  if (!requestId.ok) return requestId;
  const revision = integerField(value, "revision", path, { nonNegative: true });
  if (!revision.ok) return revision;
  const commandSequence = integerField(value, "command_sequence", path, { nonNegative: true });
  if (!commandSequence.ok) return commandSequence;
  const command = stringField(value, "command", path);
  if (!command.ok) return command;
  const day = integerField(value, "day", path, { nonNegative: true });
  if (!day.ok) return day;
  const status = literalField(value, "status", path, ["committed"] as const);
  if (!status.ok) return status;
  return ok({
    request_id: requestId.value,
    revision: revision.value,
    command_sequence: commandSequence.value,
    command: command.value,
    day: day.value,
    status: "committed",
  });
}

const ENGINE_ENVELOPE_KEYS = [
  "protocol_version",
  "career_id",
  "lineage_id",
  "revision",
  "allowed_commands",
  "receipt",
  "duplicate",
  "state",
] as const;

function validateEngineEnvelopeFields(value: Record<string, unknown>): Result<EngineEnvelope> {
  const pv = protocolVersionField(value, "protocol_version", "$", BRIDGE_PROTOCOL_VERSION);
  if (!pv.ok) return pv;
  const career = idField(value, "career_id", "$");
  if (!career.ok) return career;
  const lineage = idField(value, "lineage_id", "$");
  if (!lineage.ok) return lineage;
  const revision = integerField(value, "revision", "$", { nonNegative: true });
  if (!revision.ok) return revision;
  const allowedRaw = arrayField(value, "allowed_commands", "$");
  if (!allowedRaw.ok) return allowedRaw;
  const allowedCommands = validateArray(allowedRaw.value, "$.allowed_commands", (entry, index) => {
    if (typeof entry !== "string") {
      return fail("invalid_type", `$.allowed_commands[${index}] must be a string`, "$.allowed_commands");
    }
    return ok(entry);
  });
  if (!allowedCommands.ok) return allowedCommands;

  if (!hasOwn(value, "receipt")) return fail("missing_field", "$.receipt is required", "$");
  let receipt: Receipt | null;
  if (value["receipt"] === null) {
    receipt = null;
  } else {
    const result = validateReceipt(value["receipt"], "$.receipt");
    if (!result.ok) return result;
    receipt = result.value;
  }

  const duplicate = booleanField(value, "duplicate", "$");
  if (!duplicate.ok) return duplicate;
  const stateRaw = requiredField(value, "state", "$");
  if (!stateRaw.ok) return stateRaw;
  const state = validatePlayerProjection(stateRaw.value, "$.state");
  if (!state.ok) return state;

  return ok({
    protocol_version: 1,
    career_id: career.value,
    lineage_id: lineage.value,
    revision: revision.value,
    allowed_commands: allowedCommands.value,
    receipt,
    duplicate: duplicate.value,
    state: state.value,
  });
}

export function validateEngineEnvelope(value: unknown): Result<EngineEnvelope> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected an engine envelope", "$");
  const exact = assertExactKeys(value, ENGINE_ENVELOPE_KEYS, "$");
  if (!exact.ok) return exact;
  return validateEngineEnvelopeFields(value);
}

export function validateOperationResponse(value: unknown): Result<OperationResponse> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected an operation response", "$");
  const exact = assertExactKeys(value, [...ENGINE_ENVELOPE_KEYS, "operation_status"], "$");
  if (!exact.ok) return exact;
  const envelope = validateEngineEnvelopeFields(value);
  if (!envelope.ok) return envelope;
  const operationStatus = literalField(value, "operation_status", "$", ["committed", "not_found"] as const);
  if (!operationStatus.ok) return operationStatus;
  return ok({ ...envelope.value, operation_status: operationStatus.value });
}

// ---------------------------------------------------------------------------
// Travel quotes
// ---------------------------------------------------------------------------

const QUOTE_KEYS = [
  "origin",
  "destination",
  "mode",
  "cost",
  "affordable",
  "remaining_tu",
  "return_cost",
  "return_fits_today",
  "fare",
  "return_fare",
  "can_return_today",
  "return_uncertain",
  "command",
  "arguments",
] as const;

function validateQuote(
  value: unknown,
  path: string,
): Result<QuoteResponse["quote"]> {
  if (!isPlainObject(value)) return fail("invalid_type", `${path} must be an object`, path);
  const exact = assertExactKeys(value, QUOTE_KEYS, path);
  if (!exact.ok) return exact;
  const origin = stringField(value, "origin", path);
  if (!origin.ok) return origin;
  const destination = stringField(value, "destination", path);
  if (!destination.ok) return destination;
  const mode = stringField(value, "mode", path);
  if (!mode.ok) return mode;
  const cost = nullableNumberField(value, "cost", path);
  if (!cost.ok) return cost;
  const affordable = booleanField(value, "affordable", path);
  if (!affordable.ok) return affordable;
  const remainingTu = integerField(value, "remaining_tu", path, { nonNegative: true });
  if (!remainingTu.ok) return remainingTu;
  const returnCost = nullableNumberField(value, "return_cost", path);
  if (!returnCost.ok) return returnCost;
  const returnFitsToday = booleanField(value, "return_fits_today", path);
  if (!returnFitsToday.ok) return returnFitsToday;
  const fare = optionalNullableNumberField(value, "fare", path);
  if (!fare.ok) return fare;
  const returnFare = optionalNullableNumberField(value, "return_fare", path);
  if (!returnFare.ok) return returnFare;
  const canReturnToday = optionalBooleanField(value, "can_return_today", path);
  if (!canReturnToday.ok) return canReturnToday;
  const returnUncertain = optionalBooleanField(value, "return_uncertain", path);
  if (!returnUncertain.ok) return returnUncertain;
  const command = literalField(value, "command", path, ["travel", "journey"] as const);
  if (!command.ok) return command;
  const argsRaw = requiredField(value, "arguments", path);
  if (!argsRaw.ok) return argsRaw;
  const arguments_ = validateStringRecord(argsRaw.value, `${path}.arguments`);
  if (!arguments_.ok) return arguments_;

  return ok({
    origin: origin.value,
    destination: destination.value,
    mode: mode.value,
    cost: cost.value,
    affordable: affordable.value,
    remaining_tu: remainingTu.value,
    return_cost: returnCost.value,
    return_fits_today: returnFitsToday.value,
    ...(fare.value !== undefined ? { fare: fare.value } : {}),
    ...(returnFare.value !== undefined ? { return_fare: returnFare.value } : {}),
    ...(canReturnToday.value !== undefined ? { can_return_today: canReturnToday.value } : {}),
    ...(returnUncertain.value !== undefined ? { return_uncertain: returnUncertain.value } : {}),
    command: command.value,
    arguments: arguments_.value,
  });
}

export function validateQuoteResponse(value: unknown): Result<QuoteResponse> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected a quote response", "$");
  const exact = assertExactKeys(value, ["protocol_version", "career_id", "lineage_id", "revision", "quote"], "$");
  if (!exact.ok) return exact;
  const pv = protocolVersionField(value, "protocol_version", "$", BRIDGE_PROTOCOL_VERSION);
  if (!pv.ok) return pv;
  const career = idField(value, "career_id", "$");
  if (!career.ok) return career;
  const lineage = idField(value, "lineage_id", "$");
  if (!lineage.ok) return lineage;
  const revision = integerField(value, "revision", "$", { nonNegative: true });
  if (!revision.ok) return revision;
  const quoteRaw = requiredField(value, "quote", "$");
  if (!quoteRaw.ok) return quoteRaw;
  const quote = validateQuote(quoteRaw.value, "$.quote");
  if (!quote.ok) return quote;
  return ok({
    protocol_version: 1,
    career_id: career.value,
    lineage_id: lineage.value,
    revision: revision.value,
    quote: quote.value,
  });
}

// ---------------------------------------------------------------------------
// Error envelopes
// ---------------------------------------------------------------------------

export function validateApiErrorEnvelope(value: unknown): Result<ApiErrorEnvelope> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected an API error envelope", "$");
  const exact = assertExactKeys(value, ["protocol_version", "error"], "$");
  if (!exact.ok) return exact;
  const pv = protocolVersionField(value, "protocol_version", "$", BRIDGE_PROTOCOL_VERSION);
  if (!pv.ok) return pv;
  const errorRaw = requiredField(value, "error", "$");
  if (!errorRaw.ok) return errorRaw;
  if (!isPlainObject(errorRaw.value)) return fail("invalid_type", "$.error must be an object", "$");
  const error = errorRaw.value;
  const errorExact = assertExactKeys(error, ["code", "message"], "$.error");
  if (!errorExact.ok) return errorExact;
  const code = stringField(error, "code", "$.error");
  if (!code.ok) return code;
  const message = stringField(error, "message", "$.error");
  if (!message.ok) return message;
  return ok({ protocol_version: 1, error: { code: code.value, message: message.value } });
}

export function validateHostErrorEnvelope(value: unknown): Result<HostErrorEnvelope> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected a host error envelope", "$");
  const exact = assertExactKeys(value, ["host_protocol_version", "error"], "$");
  if (!exact.ok) return exact;
  const pv = protocolVersionField(value, "host_protocol_version", "$", HOST_PROTOCOL_VERSION);
  if (!pv.ok) return pv;
  const errorRaw = requiredField(value, "error", "$");
  if (!errorRaw.ok) return errorRaw;
  if (!isPlainObject(errorRaw.value)) return fail("invalid_type", "$.error must be an object", "$");
  const error = errorRaw.value;
  const errorExact = assertExactKeys(error, ["code", "message"], "$.error");
  if (!errorExact.ok) return errorExact;
  const code = stringField(error, "code", "$.error");
  if (!code.ok) return code;
  const message = stringField(error, "message", "$.error");
  if (!message.ok) return message;
  return ok({ host_protocol_version: 1, error: { code: code.value, message: message.value } });
}

export function validateErrorEnvelope(value: unknown): Result<ApiErrorEnvelope | HostErrorEnvelope> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected an error envelope", "$");
  if (hasOwn(value, "host_protocol_version")) return validateHostErrorEnvelope(value);
  return validateApiErrorEnvelope(value);
}

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

export function validateCommandRequest(value: unknown): Result<CommandRequest> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected a command request", "$");
  const exact = assertExactKeys(
    value,
    ["protocol_version", "career_id", "lineage_id", "request_id", "expected_revision", "command", "arguments"],
    "$",
  );
  if (!exact.ok) return exact;
  const pv = protocolVersionField(value, "protocol_version", "$", BRIDGE_PROTOCOL_VERSION);
  if (!pv.ok) return pv;
  const career = idField(value, "career_id", "$");
  if (!career.ok) return career;
  const lineage = idField(value, "lineage_id", "$");
  if (!lineage.ok) return lineage;
  const request = idField(value, "request_id", "$");
  if (!request.ok) return request;
  const revision = integerField(value, "expected_revision", "$", { nonNegative: true });
  if (!revision.ok) return revision;
  const commandField = stringField(value, "command", "$");
  if (!commandField.ok) return commandField;
  if (!(COMMANDS as readonly string[]).includes(commandField.value)) {
    return fail("unknown_command", `$.command ${JSON.stringify(commandField.value)} is not allowlisted`, "$");
  }
  const command = commandField.value as Command;

  if (!hasOwn(value, "arguments")) return fail("missing_field", "$.arguments is required", "$");
  const argsRaw = value["arguments"];
  if (!isPlainObject(argsRaw)) return fail("invalid_type", "$.arguments must be an object", "$");

  const allowedKeys = COMMAND_ARGUMENTS[command] as readonly string[];
  const argsExact = assertExactKeys(argsRaw, allowedKeys, "$.arguments");
  if (!argsExact.ok) return argsExact;

  const args: Record<string, string> = {};
  for (const key of allowedKeys) {
    const raw = argsRaw[key];
    if (typeof raw !== "string") {
      return fail("invalid_type", `$.arguments.${key} must be a string`, "$.arguments");
    }
    if (raw.length > ARGUMENT_MAX_LENGTH) {
      return fail("argument_too_long", `$.arguments.${key} exceeds ${ARGUMENT_MAX_LENGTH} chars`, "$.arguments");
    }
    args[key] = raw;
  }

  return ok({
    protocol_version: 1,
    career_id: career.value,
    lineage_id: lineage.value,
    request_id: request.value,
    expected_revision: revision.value,
    command,
    arguments: args,
  });
}

export function validateBootstrapRequest(value: unknown): Result<BootstrapRequest> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected a bootstrap request", "$");
  const exact = assertExactKeys(value, ["host_protocol_version", "bundle_id", "code"], "$");
  if (!exact.ok) return exact;
  const pv = protocolVersionField(value, "host_protocol_version", "$", HOST_PROTOCOL_VERSION);
  if (!pv.ok) return pv;
  const bundleId = stringField(value, "bundle_id", "$");
  if (!bundleId.ok) return bundleId;
  const code = stringField(value, "code", "$");
  if (!code.ok) return code;
  if (!isBase64Url43(code.value)) {
    return fail("invalid_code", "$.code must be a 43-char base64url token", "$");
  }
  return ok({ host_protocol_version: 1, bundle_id: bundleId.value, code: code.value });
}

export function validateTravelQuoteRequest(value: unknown): Result<TravelQuoteRequest> {
  if (!isPlainObject(value)) return fail("invalid_type", "expected a travel quote request", "$");
  const exact = assertExactKeys(value, ["protocol_version", "destination", "mode"], "$");
  if (!exact.ok) return exact;
  const pv = protocolVersionField(value, "protocol_version", "$", BRIDGE_PROTOCOL_VERSION);
  if (!pv.ok) return pv;
  const destination = stringField(value, "destination", "$");
  if (!destination.ok) return destination;
  const mode = stringField(value, "mode", "$");
  if (!mode.ok) return mode;
  return ok({ protocol_version: 1, destination: destination.value, mode: mode.value });
}

// ---------------------------------------------------------------------------
// Body decoding (never assume JSON — failures may be HTML or a dropped conn)
// ---------------------------------------------------------------------------

export function parseJsonBody(text: string): Result<unknown> {
  if (typeof text !== "string") return fail("invalid_body", "response body is not a string", "$");
  const trimmed = text.trim();
  if (trimmed === "") return fail("empty_body", "response body is empty", "$");
  if (/^\s*</.test(trimmed)) {
    return fail("non_json_body", "response body looks like HTML/XML, not JSON", "$");
  }
  try {
    return ok(JSON.parse(text));
  } catch {
    return fail("invalid_json", "response body is not valid JSON", "$");
  }
}
