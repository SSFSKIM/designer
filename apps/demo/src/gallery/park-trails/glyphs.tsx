/**
 * The planner's symbols: a route, a disclosure chevron and four skies. Drawn in `currentColor`
 * with a 1.6 px stroke so they take the runtime's ink exactly as the words beside them do.
 */

import type { ReactNode } from "react";

import type { Sky } from "./data";

const STROKE = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round",
  strokeLinejoin: "round",
} as const;

export function RouteGlyph(): ReactNode {
  return (
    <svg className="pt-glyph" viewBox="0 0 20 20" aria-hidden="true">
      <path {...STROKE} d="M2.5 16.5 7.5 7l3 5 2-3 5 7.5Z" />
      <path {...STROKE} d="M6 16.5c1.5-2 3.5-2.5 5-2s3 .2 4-1" strokeDasharray="1.4 2" />
    </svg>
  );
}

export function Chevron(): ReactNode {
  return (
    <svg className="pt-glyph pt-glyph--chevron" viewBox="0 0 20 20" aria-hidden="true">
      <path {...STROKE} d="m6 8 4 4 4-4" />
    </svg>
  );
}

export function SkyGlyph(props: { readonly sky: Sky }): ReactNode {
  const cloud = <path {...STROKE} d="M6 14.5h8.2a3 3 0 0 0 .3-6 4.2 4.2 0 0 0-8-.4A3.2 3.2 0 0 0 6 14.5Z" />;
  switch (props.sky) {
    case "sun":
      return (
        <svg className="pt-glyph" viewBox="0 0 20 20" aria-hidden="true">
          <circle {...STROKE} cx="10" cy="10" r="3.4" />
          <path
            {...STROKE}
            d="M10 2.5v1.8M10 15.7v1.8M2.5 10h1.8M15.7 10h1.8M4.7 4.7 6 6M14 14l1.3 1.3M4.7 15.3 6 14M14 6l1.3-1.3"
          />
        </svg>
      );
    case "showers":
      return (
        <svg className="pt-glyph" viewBox="0 0 20 20" aria-hidden="true">
          <path {...STROKE} d="M13.2 4.2a3 3 0 0 1 3.6 3.4" />
          {cloud}
          <path {...STROKE} d="m7.5 16.8-.6 1.4M11 16.8l-.6 1.4" />
        </svg>
      );
    case "clearing":
      return (
        <svg className="pt-glyph" viewBox="0 0 20 20" aria-hidden="true">
          <path {...STROKE} d="M13.2 4.2a3 3 0 0 1 3.6 3.4" />
          {cloud}
        </svg>
      );
    case "rain":
      return (
        <svg className="pt-glyph" viewBox="0 0 20 20" aria-hidden="true">
          {cloud}
          <path {...STROKE} d="m7 16.6-.8 1.8M10.2 16.6l-.8 1.8M13.4 16.6l-.8 1.8" />
        </svg>
      );
    case "snow":
    case "snow-showers":
      return (
        <svg className="pt-glyph" viewBox="0 0 20 20" aria-hidden="true">
          {cloud}
          <path {...STROKE} d="M7 17.4h.01M10.2 17.8h.01M13.4 17.4h.01" strokeWidth={2.4} />
        </svg>
      );
  }
}
