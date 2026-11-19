import { SCENARIOS } from "../fixtures";
import type { Scenario } from "../types";

export function ScenarioSwitcher({
  activeId,
  onChange,
}: {
  activeId: Scenario["id"];
  onChange: (id: Scenario["id"]) => void;
}) {
  return (
    <div>
      <div className="mb-1.5 flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-institutional-strong">
          Developer Preview
        </span>
        <span className="text-[11px] text-muted">— QA scenarios, not gameplay modes</span>
      </div>
      <div
        role="group"
        aria-label="Developer Preview — QA scenarios"
        className="inline-flex rounded-lg border border-border bg-surface p-1"
      >
        {SCENARIOS.map((s) => {
          const active = s.id === activeId;
          return (
            <button
              key={s.id}
              type="button"
              onClick={() => onChange(s.id)}
              aria-pressed={active}
              className={`cursor-pointer rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-200 ${
                active
                  ? "bg-primary text-on-primary"
                  : "text-muted hover:text-foreground"
              }`}
            >
              {s.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
