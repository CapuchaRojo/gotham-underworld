import type { InstitutionRecord, Scenario } from "../types";
import { placeById } from "../atlas";
import { usePresentationMode } from "../presentation";
import { ContactCard } from "./ContactCard";
import { ObservationCard } from "./ObservationCard";
import { StateBadge } from "./StateBadge";
import { FileTextIcon } from "./icons";

function statusLabel(s: InstitutionRecord["status"]) {
  switch (s) {
    case "queued":
      return "Queued";
    case "clarification_requested":
      return "Clarification requested";
    case "documented":
      return "Documented";
    case "closed_insufficient":
      return "Closed — insufficient";
  }
}

export function StoryView({ scenario }: { scenario: Scenario }) {
  const { isDeveloper } = usePresentationMode();
  // Group observations by incident so conflicting sources can be surfaced.
  const byIncident = new Map<string, typeof scenario.observations>();
  for (const o of scenario.observations) {
    const list = byIncident.get(o.incidentId) ?? [];
    list.push(o);
    byIncident.set(o.incidentId, list);
  }
  const conflicts = new Set(
    [...byIncident.values()].filter((list) => list.length > 1).flatMap((list) => list.map((o) => o.id)),
  );
  const confidenceCounts = scenario.observations.reduce<Record<string, number>>((acc, o) => {
    acc[o.confidence] = (acc[o.confidence] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <section aria-labelledby="contacts-heading">
        <h2 id="contacts-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Known contacts
        </h2>
        {scenario.contacts.length === 0 ? (
          <p className="noir-panel p-4 text-sm text-muted">
            No known contacts yet. Contacts appear here as you meet them in play.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {scenario.contacts.map((c) => (
              <ContactCard key={c.id} contact={c} />
            ))}
          </div>
        )}
      </section>

      <section aria-labelledby="observations-heading">
        <h2 id="observations-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Incident observations
        </h2>
        {scenario.observations.length > 0 ? (
          <p className="mb-2 text-[11px] text-muted">
            {scenario.observations.length} observation{scenario.observations.length === 1 ? "" : "s"} ·{" "}
            {confidenceCounts.documented ?? 0} documented · {confidenceCounts.unconfirmed ?? 0} unconfirmed ·{" "}
            {confidenceCounts.unknown ?? 0} unknown. Documented means a record backs it; unconfirmed means the claim is not verified.
            Confidence labels do not establish source count or make a claim true.
          </p>
        ) : null}
        {scenario.observations.length === 0 ? (
          <p className="noir-panel p-4 text-sm text-muted">
            No observations recorded. Incident observations you witness appear here with their source and
            uncertainty.
          </p>
        ) : (
          <div className="space-y-2">
            {scenario.observations.map((o) => (
              <ObservationCard key={o.id} observation={o} conflicting={conflicts.has(o.id)} />
            ))}
            {conflicts.size > 0 ? (
              <p className="text-[11px] text-muted">
                Where sources disagree, both are shown and neither is marked true.
              </p>
            ) : null}
          </div>
        )}
      </section>

      <section aria-labelledby="records-heading">
        <h2 id="records-heading" className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Institutional records
        </h2>
        {scenario.institutions.length === 0 ? (
          <p className="noir-panel p-4 text-sm text-muted">
            No institutional records. Official records (intake, desks) appear here in teal.
          </p>
        ) : (
          <ul className="space-y-2">
            {scenario.institutions.map((r) => {
              const place = placeById.get(r.placeId);
              return (
                <li
                  key={r.id}
                  className="rounded-lg border border-institutional/40 bg-institutional/10 p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <FileTextIcon className="h-4 w-4 text-institutional-strong" />
                      <div>
                        <div className="text-sm font-semibold text-foreground">{r.name}</div>
                        <div className="text-xs text-muted">
                          {r.kind === "police_intake" ? "Police intake" : "Civilian desk"} · {r.staff}
                        </div>
                      </div>
                    </div>
                    <StateBadge tone="institutional">{statusLabel(r.status)}</StateBadge>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
                    <span>
                      Classification: <span className="text-foreground">{r.classification}</span>
                    </span>
                    <span>
                      Credibility: <span className="text-foreground">{r.credibility}</span>
                    </span>
                    <span>
                      Location:{" "}
                      <span className="text-foreground">
                        {isDeveloper ? (place ? `${place.label} (${place.id})` : r.placeId) : place?.label}
                      </span>
                    </span>
                  </div>
                  <p className="mt-1.5 text-xs leading-relaxed text-muted-strong">{r.note}</p>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
