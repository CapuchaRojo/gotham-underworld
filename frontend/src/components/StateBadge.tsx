import type { ReactNode } from "react";

export type BadgeTone =
  | "neutral"
  | "positive"
  | "danger"
  | "info"
  | "institutional"
  | "warning";

const TONES: Record<BadgeTone, string> = {
  neutral: "text-muted border-border bg-surface-raised",
  positive: "text-money-strong border-money/40 bg-money/10",
  danger: "text-danger-strong border-danger/40 bg-danger/10",
  info: "text-institutional-strong border-institutional/40 bg-institutional/10",
  institutional: "text-institutional-strong border-institutional/40 bg-institutional/10",
  warning: "text-primary-strong border-primary/40 bg-primary/10",
};

export function StateBadge({
  tone = "neutral",
  icon,
  children,
}: {
  tone?: BadgeTone;
  icon?: ReactNode;
  children: ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${TONES[tone]}`}
    >
      {icon ? <span className="shrink-0 [&>svg]:h-3.5 [&>svg]:w-3.5">{icon}</span> : null}
      <span>{children}</span>
    </span>
  );
}
