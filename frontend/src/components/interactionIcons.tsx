// Interaction-specific glyphs that don't exist in the shared `icons.tsx` set.
// Kept local so `OpportunityInteraction` stays dependency-light; every other
// glyph the component needs is reused from `./icons`.

import type { ReactNode } from "react";

interface IconProps {
  className?: string;
}

function Base({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  );
}

/** Choices — a list. */
export function ListIcon({ className }: IconProps) {
  return (
    <Base className={className}>
      <path d="M9 6h11M9 12h11M9 18h11" />
      <circle cx="4" cy="6" r="1.2" />
      <circle cx="4" cy="12" r="1.2" />
      <circle cx="4" cy="18" r="1.2" />
    </Base>
  );
}

/** Refusal — an abstention mark. */
export function AbstainIcon({ className }: IconProps) {
  return (
    <Base className={className}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M8 12h8" />
    </Base>
  );
}

/** Consequence — aftermath rippling out. */
export function TrailIcon({ className }: IconProps) {
  return (
    <Base className={className}>
      <path d="M3.5 9a8.5 8.5 0 0 1 17 0" />
      <path d="M6.5 13a5.5 5.5 0 0 1 11 0" />
      <path d="M9.5 17a2.5 2.5 0 0 1 5 0" />
    </Base>
  );
}
