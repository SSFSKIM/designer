/**
 * The ornaments' symbols. Drawn in `currentColor` so they take the runtime's ink, and stroked
 * rather than filled so they survive forced colours as the system text colour.
 */

import type { ReactNode } from "react";

const common = {
  width: 22,
  height: 22,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2.25,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
  focusable: false,
};

export function PreviousIcon(): ReactNode {
  return (
    <svg {...common}>
      <path d="M15 5 8 12l7 7" />
    </svg>
  );
}

export function NextIcon(): ReactNode {
  return (
    <svg {...common}>
      <path d="m9 5 7 7-7 7" />
    </svg>
  );
}

export function PlayIcon(): ReactNode {
  return (
    <svg {...common} width={18} height={18}>
      <path d="M8 5.5v13l10.5-6.5z" fill="currentColor" strokeWidth={1.5} />
    </svg>
  );
}

export function PauseIcon(): ReactNode {
  return (
    <svg {...common} width={18} height={18}>
      <path d="M8.5 5.5v13M15.5 5.5v13" strokeWidth={3} />
    </svg>
  );
}

export function RestartIcon(): ReactNode {
  return (
    <svg {...common} width={20} height={20}>
      <path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3" />
      <path d="M4.5 4.5v4h4" />
    </svg>
  );
}
