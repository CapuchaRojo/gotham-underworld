// Dev-only, read-only inspection surface for the M030-C1.3 Python browser host.
//
// This component renders ONLY validated host data (`HostSession` + `EngineEnvelope`
// `PlayerProjection`) promoted through the wire validators. It never imports or
// reads `Scenario`/`SCENARIOS`/`SCENARIO_BY_ID`, never constructs a synthetic
// fallback, and renders no mutation affordances of any kind — no wait/travel/
// choose buttons, no pairing control, no recovery trigger. A value the Python
// projection does not carry stays "unavailable"; a value the projection carries
// as `null` is shown as null (not fabricated).
//
// The presentational component (`LocalEngineInspectionView`) is a pure function
// of its props so display permutations (nullable fields, unavailable sections,
// option-level availability) can be unit-tested without a host. The connected
// wrapper (`LocalEngineInspection`) reads the live provider context.

import type { ReactNode } from "react";
import { useLiveEngine } from "../gameplay/LiveEngineProvider";
import type { LiveEngineStatus } from "../gameplay/liveEngine";
import type { SessionFailureKind } from "../gameplay/liveEngine";
import type {
  EngineEnvelope,
  HostSession,
  OpportunityOption,
  PlayerProjection,
  Receipt,
} from "../gameplay/wire";
import { StateBadge } from "./StateBadge";
import type { BadgeTone } from "./StateBadge";

// ---------------------------------------------------------------------------
// Props (pure display model)
// ---------------------------------------------------------------------------

export interface LocalEngineInspectionViewProps {
  status: LiveEngineStatus;
  session: HostSession | null;
  engineState: EngineEnvelope | null;
  lastSessionFailure: { failure: SessionFailureKind; reason: string } | null;
  lastError: string | null;
}

// ---------------------------------------------------------------------------
// Small presentational helpers
// ---------------------------------------------------------------------------

function Section({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <h3 className="mb-3 font-heading text-sm font-bold tracking-wide text-foreground">
        {title}
      </h3>
      <div className="flex flex-col gap-2">{children}</div>
    </section>
  );
}

function Field({
  label,
  testId,
  children,
}: {
  label: string;
  testId?: string;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-0.5 border-b border-border/50 pb-2 last:border-0 last:pb-0 sm:flex-row sm:items-baseline sm:justify-between sm:gap-4">
      <dt className="text-[11px] uppercase tracking-wide text-muted">{label}</dt>
      <dd
        data-testid={testId}
        className="break-words text-sm font-medium text-foreground"
      >
        {children}
      </dd>
    </div>
  );
}

function Unavailable({ detail }: { detail?: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-muted">
      <span className="font-semibold uppercase tracking-wide text-muted-strong">
        unavailable
      </span>
      {detail ? <span className="text-xs">— {detail}</span> : null}
    </span>
  );
}

/** Nullable numeric/string values stay visibly null rather than being fabricated. */
function Nullable({
  value,
  whenNull = "not yet active",
}: {
  value: number | string | null;
  whenNull?: string;
}) {
  if (value === null) {
    return <Unavailable detail={whenNull} />;
  }
  return <span>{value}</span>;
}

function optionArguments(args: OpportunityOption["arguments"]): string {
  if ("choice_id" in args) {
    return `choice_id=${args.choice_id}, option_id=${args.option_id}`;
  }
  return `offer_id=${args.offer_id}, option_id=${args.option_id}`;
}

const CONNECTION_TONE: Record<LiveEngineStatus["connectionState"], BadgeTone> = {
  starting: "info",
  pairing_required: "warning",
  pairing_in_progress: "info",
  rate_limited: "warning",
  incompatible: "danger",
  recovering: "info",
  ready: "positive",
  disconnected: "neutral",
  outcome_uncertain: "warning",
};

// ---------------------------------------------------------------------------
// Sub-renderers
// ---------------------------------------------------------------------------

function SessionPanel({ session }: { session: HostSession | null }) {
  return (
    <Section title="Host session">
      {session === null ? (
        <Field label="Session">
          <Unavailable detail="no validated host session yet" />
        </Field>
      ) : (
        <dl className="flex flex-col gap-2">
          <Field label="Engine release">{session.engine_release}</Field>
          <Field label="Host protocol">{session.host_protocol_version}</Field>
          <Field label="Bridge protocol">{session.bridge_protocol_version}</Field>
          <Field label="Bundle">{session.bundle_id}</Field>
          <Field label="Manifest sha256">{session.manifest_sha256}</Field>
          <Field label="Instance">{session.instance_id}</Field>
          <Field label="Mode">{session.mode}</Field>
          <Field label="Lifetime">{session.session_lifetime}</Field>
        </dl>
      )}
    </Section>
  );
}

function ReceiptPanel({ receipt }: { receipt: Receipt | null }) {
  return (
    <Field label="Receipt">
      {receipt === null ? (
        <span className="text-muted">none</span>
      ) : (
        <span>
          {receipt.command} (day {receipt.day}, rev {receipt.revision}, seq{" "}
          {receipt.command_sequence}, {receipt.request_id})
        </span>
      )}
    </Field>
  );
}

function IdentityPanel({ engineState }: { engineState: EngineEnvelope | null }) {
  return (
    <Section title="Engine envelope">
      {engineState === null ? (
        <Field label="Projection">
          <Unavailable detail="no validated projection — no fixture fallback" />
        </Field>
      ) : (
        <dl className="flex flex-col gap-2">
          <Field label="Protocol version">{engineState.protocol_version}</Field>
          <Field label="Career" testId="career-id">
            {engineState.career_id}
          </Field>
          <Field label="Lineage" testId="lineage-id">
            {engineState.lineage_id}
          </Field>
          <Field label="Bridge revision" testId="bridge-revision">
            {engineState.revision}
          </Field>
          <Field label="Duplicate">{String(engineState.duplicate)}</Field>
          <Field label="Allowed commands">
            {engineState.allowed_commands.length > 0
              ? engineState.allowed_commands.join(", ")
              : "none"}
          </Field>
          <ReceiptPanel receipt={engineState.receipt} />
        </dl>
      )}
    </Section>
  );
}

function SystemsPanel({ state }: { state: PlayerProjection }) {
  const { systems } = state;
  return (
    <Section title="Systems adoption">
      <dl className="flex flex-col gap-2">
        <Field label="Navigation">{systems.navigation}</Field>
        <Field label="Daily life">{systems.daily_life}</Field>
        <Field label="Ordinary">{systems.ordinary}</Field>
        <Field label="Mobility">{systems.mobility}</Field>
      </dl>
    </Section>
  );
}

function OpportunitiesPanel({ state }: { state: PlayerProjection }) {
  if (state.opportunities.length === 0) {
    return (
      <Section title="Opportunities">
        <Field label="Opportunities">
          <span className="text-muted">none</span>
        </Field>
      </Section>
    );
  }

  return (
    <Section title="Opportunities">
      <div className="flex flex-col gap-3">
        {state.opportunities.map((opportunity) => (
          <article
            key={opportunity.id}
            className="rounded-md border border-border bg-surface-raised p-3"
          >
            <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
              <h4 className="font-heading text-sm font-bold text-foreground">
                {opportunity.title}
              </h4>
              <span className="text-[11px] text-muted">
                {opportunity.id} · {opportunity.command} · days{" "}
                {opportunity.open_day}–{opportunity.expires_day} ·{" "}
                {opportunity.state}
              </span>
            </div>
            <p className="mb-1 text-xs text-muted">
              <span className="font-semibold text-muted-strong">
                {opportunity.speaker}
              </span>
              {" — "}
              {opportunity.situation}
            </p>
            <ul className="mt-2 flex flex-col gap-1.5">
              {opportunity.options.map((option) => (
                <li
                  key={option.id}
                  className="flex flex-col gap-0.5 rounded border border-border/60 px-2.5 py-1.5"
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5">
                    <span className="text-sm font-medium text-foreground">
                      {option.label}
                      <span className="ml-1.5 text-[11px] text-muted">
                        {option.id}
                      </span>
                    </span>
                    <span className="text-[11px]">
                      {option.availability === "available" ? (
                        <span className="font-semibold text-money-strong">
                          available
                        </span>
                      ) : (
                        <span className="font-semibold text-danger-strong">
                          unavailable{option.reason ? ` — ${option.reason}` : ""}
                        </span>
                      )}
                    </span>
                  </div>
                  <span className="text-[11px] text-muted">
                    cost {option.action_cost} · {option.tradeoff}
                  </span>
                  <span className="text-[11px] text-muted">
                    {optionArguments(option.arguments)}
                  </span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </Section>
  );
}

function ProjectionPanel({ state }: { state: PlayerProjection }) {
  return (
    <>
      <Section title="Player projection">
        <dl className="flex flex-col gap-2">
          <Field label="Day" testId="player-day">
            {state.day}
          </Field>
          <Field label="Cash" testId="player-cash">
            {state.player.cash}
          </Field>
          <Field label="Heat" testId="player-heat">
            {state.player.heat}
          </Field>
          <Field label="Custody" testId="player-custody">
            {state.player.custody}
          </Field>
        </dl>
      </Section>

      <Section title="Budgets">
        <dl className="flex flex-col gap-2">
          <Field label="Actions remaining" testId="actions-remaining">
            {state.budgets.actions_remaining} / {state.budgets.daily_actions}
          </Field>
          <Field label="Travel units remaining" testId="travel-units-remaining">
            <Nullable
              value={state.budgets.travel_units_remaining}
              whenNull="navigation not yet active"
            />{" "}
            / {state.budgets.daily_travel_units}
          </Field>
        </dl>
      </Section>

      <Section title="Location">
        <dl className="flex flex-col gap-2">
          <Field label="Location" testId="location">
            {state.location === null ? (
              <Unavailable detail="navigation not yet active" />
            ) : (
              <span>
                {state.location.label} ({state.location.id})
              </span>
            )}
          </Field>
        </dl>
      </Section>

      <Section title="Housing">
        <dl className="flex flex-col gap-2">
          {state.housing === null ? (
            <Field label="Housing" testId="housing">
              <Unavailable detail="daily life not yet adopted" />
            </Field>
          ) : (
            <>
              <Field label="Status" testId="housing-status">
                {state.housing.status}
              </Field>
              <Field label="Home" testId="housing-home">
                {state.housing.home_id}
              </Field>
              <Field label="Next due day">{state.housing.next_due_day}</Field>
              <Field label="Arrears">{state.housing.arrears}</Field>
              <Field label="Prepaid">{state.housing.prepaid}</Field>
            </>
          )}
        </dl>
      </Section>

      <Section title="Contacts">
        {state.contacts.length === 0 ? (
          <Field label="Contacts">
            <span className="text-muted">none</span>
          </Field>
        ) : (
          <dl className="flex flex-col gap-2">
            {state.contacts.map((contact) => (
              <Field key={contact.id} label={contact.name}>
                <span className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                  <span className="text-xs text-muted">
                    {contact.id} · {contact.role}
                  </span>
                  <span className="text-xs">standing {contact.standing}</span>
                </span>
              </Field>
            ))}
          </dl>
        )}
      </Section>

      <Section title="Outcomes">
        {state.outcomes.length === 0 ? (
          <Field label="Outcomes">
            <span className="text-muted">none</span>
          </Field>
        ) : (
          <ul className="flex flex-col gap-1.5">
            {state.outcomes.map((outcome, index) => (
              <li
                key={`${outcome.choice_id}:${outcome.option_id}:${index}`}
                className="rounded border border-border/60 px-2.5 py-1.5 text-xs"
              >
                <span className="font-medium text-foreground">
                  {outcome.choice_id} → {outcome.option_id}
                </span>
                <span className="ml-2 text-muted">day {outcome.day}</span>
                <span className="mt-0.5 block text-muted">{outcome.feedback}</span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Ordinary life">
        <dl className="flex flex-col gap-2">
          {state.ordinary === undefined ? (
            <Field label="Ordinary">
              <Unavailable detail="not yet enabled" />
            </Field>
          ) : (
            <>
              <Field label="Employment">{state.ordinary.employment}</Field>
              <Field label="Assistance status">
                {state.ordinary.assistance.status}
              </Field>
              <Field label="Assistance amount">
                {state.ordinary.assistance.amount}
              </Field>
              <Field label="Assistance due day">
                <Nullable value={state.ordinary.assistance.due_day} />
              </Field>
            </>
          )}
        </dl>
      </Section>
    </>
  );
}

function AbsentSections() {
  return (
    <Section title="Not in the projection">
      <p className="mb-2 text-xs text-muted">
        These sections are absent from the Python host projection and are never
        synthesized from fixtures.
      </p>
      <dl className="flex flex-col gap-2">
        <Field label="Observations">
          <Unavailable />
        </Field>
        <Field label="Institutions">
          <Unavailable />
        </Field>
        <Field label="Commitments">
          <Unavailable />
        </Field>
      </dl>
    </Section>
  );
}

// ---------------------------------------------------------------------------
// Presentational component
// ---------------------------------------------------------------------------

export function LocalEngineInspectionView({
  status,
  session,
  engineState,
  lastSessionFailure,
  lastError,
}: LocalEngineInspectionViewProps) {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-6 sm:px-6">
      <header className="flex flex-col gap-2">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="font-heading text-xl font-bold leading-tight">
              Local Engine Inspection
            </h2>
            <p className="text-xs text-muted">
              Authoritative Python host — read-only transport validation surface
            </p>
          </div>
          <StateBadge tone={CONNECTION_TONE[status.connectionState]}>
            {status.label}
          </StateBadge>
        </div>
        <div className="flex flex-col gap-1.5 rounded-md border border-border bg-surface px-3 py-2 text-[11px] text-muted">
          <span>
            <span className="font-semibold uppercase tracking-wide text-muted-strong">
              {status.contextLabel}
            </span>
            {" — "}
            {status.detail}
          </span>
          {lastError ? (
            <span className="text-danger-strong">Last error: {lastError}</span>
          ) : null}
          {lastSessionFailure ? (
            <span className="text-danger-strong">
              Session failure ({lastSessionFailure.failure}):{" "}
              {lastSessionFailure.reason}
            </span>
          ) : null}
        </div>
      </header>

      <SessionPanel session={session} />
      <IdentityPanel engineState={engineState} />

      {engineState === null ? (
        <Section title="Player projection">
          <Field label="Projection">
            <Unavailable detail="no validated projection — no fixture fallback" />
          </Field>
        </Section>
      ) : (
        <>
          <ProjectionPanel state={engineState.state} />
          <SystemsPanel state={engineState.state} />
          <OpportunitiesPanel state={engineState.state} />
        </>
      )}

      <AbsentSections />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Connected wrapper (reads the live provider)
// ---------------------------------------------------------------------------

export function LocalEngineInspection() {
  const {
    status,
    session,
    engineState,
    lastSessionFailure,
    lastError,
  } = useLiveEngine();

  return (
    <LocalEngineInspectionView
      status={status}
      session={session}
      engineState={engineState}
      lastSessionFailure={lastSessionFailure}
      lastError={lastError}
    />
  );
}
