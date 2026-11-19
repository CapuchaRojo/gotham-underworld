import { usePresentationMode } from "../presentation";
import { StateBadge } from "./StateBadge";
import { EyeOffIcon } from "./icons";

/**
 * Accessible, clearly labeled switch between player presentation and Developer
 * Inspection. Discoverable but never the primary control: in player mode it is
 * a muted text button; in developer mode it is unmistakably badged.
 */
export function DeveloperModeToggle() {
  const { isDeveloper, toggleMode } = usePresentationMode();

  return (
    <div className="flex flex-col items-end gap-1.5">
      <div className="flex items-center gap-2">
        {isDeveloper ? (
          <StateBadge tone="warning">Developer Inspection Mode</StateBadge>
        ) : null}
        <button
          type="button"
          onClick={toggleMode}
          aria-pressed={isDeveloper}
          className={`inline-flex cursor-pointer items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-medium transition-colors duration-200 ${
            isDeveloper
              ? "border-primary/50 bg-primary/10 text-primary-strong hover:bg-primary/20"
              : "border-border bg-surface text-muted hover:text-foreground"
          }`}
        >
          {isDeveloper ? (
            <>
              <EyeOffIcon className="h-3.5 w-3.5" />
              Exit Developer Inspection
            </>
          ) : (
            "Developer Inspection"
          )}
        </button>
      </div>
    </div>
  );
}
