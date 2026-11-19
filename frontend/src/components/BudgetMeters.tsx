interface MeterProps {
  label: string;
  remaining: number;
  max: number;
  tone: "primary" | "institutional";
}

function Meter({ label, remaining, max, tone }: MeterProps) {
  const pct = max > 0 ? Math.min(100, Math.round((remaining / max) * 100)) : 0;
  const bar = tone === "primary" ? "bg-primary" : "bg-institutional";
  return (
    <div className="rounded-lg border border-border bg-surface-raised p-3">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</span>
        <span className="text-sm tabular-nums text-foreground">
          {remaining}
          <span className="text-muted"> of {max} left</span>
        </span>
      </div>
      <div
        role="meter"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-valuenow={remaining}
        className="mt-2 h-2 w-full overflow-hidden rounded-full bg-background"
      >
        <div
          className={`h-full rounded-full transition-[width] duration-300 ${bar}`}
          data-fill={pct}
        />
      </div>
    </div>
  );
}

export function BudgetMeters({
  actionsUsed,
  actionsMax,
  tuUsed,
  tuMax,
}: {
  actionsUsed: number;
  actionsMax: number;
  tuUsed: number;
  tuMax: number;
}) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Meter label="Actions" remaining={actionsMax - actionsUsed} max={actionsMax} tone="primary" />
      <Meter label="Travel Units" remaining={tuMax - tuUsed} max={tuMax} tone="institutional" />
    </div>
  );
}
