import type { MoneyState } from "../types";

function formatMoney(n: number): string {
  return `$${n.toFixed(0)}`;
}

export function MoneySummary({ money }: { money: MoneyState }) {
  const owed = money.arrears + money.supportDebt;
  return (
    <div className="grid grid-cols-3 gap-3">
      <div className="rounded-lg border border-border bg-surface-raised p-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted">Cash</div>
        <div className="mt-1 text-lg font-semibold tabular-nums text-foreground">{formatMoney(money.cash)}</div>
      </div>
      <div
        className={`rounded-lg border p-3 ${
          owed > 0 ? "border-danger/40 bg-danger/10" : "border-border bg-surface-raised"
        }`}
      >
        <div className="text-xs font-semibold uppercase tracking-wide text-muted">Owed</div>
        <div className={`mt-1 text-lg font-semibold tabular-nums ${owed > 0 ? "text-danger-strong" : "text-foreground"}`}>
          {formatMoney(owed)}
        </div>
        {owed > 0 && (
          <div className="mt-0.5 text-[11px] leading-tight text-muted">
            Rent arrears {formatMoney(money.arrears)} · support {formatMoney(money.supportDebt)}
          </div>
        )}
      </div>
      <div className="rounded-lg border border-border bg-surface-raised p-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted">Prepaid</div>
        <div className="mt-1 text-lg font-semibold tabular-nums text-foreground">{formatMoney(money.prepaid)}</div>
      </div>
    </div>
  );
}
