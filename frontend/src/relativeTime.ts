// Shared, player-facing relative-time phrasing used across the views so a day
// number reads as "in 3 days" / "due tomorrow" / "1 day overdue" instead of a
// bare integer. Pure and dependency-free.

/** Human relative-time phrase between the current day and a target day. */
export function relativeDays(day: number, target: number): string {
  const diff = target - day;
  if (diff === 0) return "due today";
  if (diff === 1) return "due tomorrow";
  if (diff > 1) return `in ${diff} days`;
  if (diff === -1) return "1 day overdue";
  return `${-diff} days overdue`;
}
