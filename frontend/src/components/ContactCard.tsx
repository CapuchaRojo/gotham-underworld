import type { ContactCard as ContactCardType } from "../types";
import { playerSafeText, usePresentationMode } from "../presentation";

export function ContactCard({ contact }: { contact: ContactCardType }) {
  const { isDeveloper } = usePresentationMode();
  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-foreground">{contact.name}</div>
          <div className="text-xs text-muted">{contact.role}</div>
        </div>
        <span className="rounded border border-border bg-background px-2 py-0.5 text-[11px] text-muted-strong">
          standing {contact.standing}
        </span>
      </div>
      <p className="mt-2 text-xs leading-relaxed text-muted">{contact.personality}</p>
      <p className="mt-1 text-xs leading-relaxed text-muted-strong">
        {isDeveloper ? contact.known : playerSafeText(contact.known)}
      </p>
    </div>
  );
}
