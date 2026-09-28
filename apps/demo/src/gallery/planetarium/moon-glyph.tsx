/**
 * The Moon's phase as a glyph: the lit part of a disc, the terminator an ellipse whose width is
 * the cosine of the phase. A waxing Moon is lit on the right as it is seen from the north; the
 * module states the hemisphere's reading in words beside it.
 */

import type { ReactNode } from "react";

export function MoonGlyph(props: { readonly phase: number; readonly size?: number; readonly className?: string }): ReactNode {
  const { phase, size = 56, className } = props;
  const r = 24;
  const radians = (phase * Math.PI) / 180;
  const lit = (1 - Math.cos(radians)) / 2;
  const waxing = phase < 180;
  const rx = Math.max(0.01, Math.abs(Math.cos(radians)) * r);
  // The right semicircle, then back along the terminator: it bulges toward the lit side when
  // the lit fraction is under a half and away from it when over.
  const sweep = lit < 0.5 ? 0 : 1;
  const path = `M0,-${r} A${r},${r} 0 0 1 0,${r} A${rx},${r} 0 0 ${sweep} 0,-${r} Z`;
  return (
    <svg width={size} height={size} viewBox="-28 -28 56 56" className={className} aria-hidden="true" focusable="false">
      <circle r={r} className="moon-glyph-dark" />
      <path d={path} className="moon-glyph-lit" transform={waxing ? undefined : "scale(-1 1)"} />
    </svg>
  );
}
