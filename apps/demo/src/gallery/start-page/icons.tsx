/**
 * Glyphs, drawn in the ink they sit in (`currentColor`), so the runtime's label colour, Increase
 * Contrast's near-monochrome and forced colours' CanvasText all reach them without a second
 * rule. Weather glyphs are symbols for a figure beside them; they carry no meaning alone and are
 * hidden from assistive technology, which reads the condition's name instead.
 */

import type { ReactNode } from "react";

import type { Condition } from "./data";

interface GlyphProps {
  readonly size?: number;
  readonly className?: string;
}

function Svg({ size = 24, className, children }: GlyphProps & { children: ReactNode }): ReactNode {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...(className === undefined ? {} : { className })}
    >
      {children}
    </svg>
  );
}

const SUN_RAYS = [0, 45, 90, 135, 180, 225, 270, 315];

function Sun({ cx = 12, cy = 12, r = 4.2, ray = 3 }: { cx?: number; cy?: number; r?: number; ray?: number }): ReactNode {
  return (
    <>
      <circle cx={cx} cy={cy} r={r} fill="currentColor" stroke="none" />
      {SUN_RAYS.map((angle) => {
        const radians = (angle * Math.PI) / 180;
        const inner = r + 2;
        return (
          <line
            key={angle}
            x1={cx + Math.cos(radians) * inner}
            y1={cy + Math.sin(radians) * inner}
            x2={cx + Math.cos(radians) * (inner + ray)}
            y2={cy + Math.sin(radians) * (inner + ray)}
          />
        );
      })}
    </>
  );
}

const CLOUD = "M7.5 19h9.2a4.1 4.1 0 0 0 .6-8.15A5.6 5.6 0 0 0 6.6 12.2 3.4 3.4 0 0 0 7.5 19Z";

export function WeatherGlyph({ condition, night = false, ...props }: GlyphProps & { condition: Condition; night?: boolean }): ReactNode {
  switch (condition) {
    case "clear":
      return (
        <Svg {...props}>
          {night ? <path d="M19.5 14.6A7.6 7.6 0 0 1 9.4 4.5a7.6 7.6 0 1 0 10.1 10.1Z" fill="currentColor" stroke="none" /> : <Sun />}
        </Svg>
      );
    case "mostly-clear":
      return (
        <Svg {...props}>
          <Sun cx={9} cy={9} r={3.4} ray={2.2} />
          <path d="M10.5 20h6.8a3.2 3.2 0 0 0 .4-6.36 4.3 4.3 0 0 0-8.2 1.3 2.6 2.6 0 0 0 1 5.06Z" fill="currentColor" stroke="none" />
        </Svg>
      );
    case "partly-cloudy":
      return (
        <Svg {...props}>
          <Sun cx={8.5} cy={8} r={3} ray={2} />
          <path d={CLOUD} fill="currentColor" stroke="none" />
        </Svg>
      );
    case "cloudy":
      return (
        <Svg {...props}>
          <path d="M8 16.5h8.6a3.8 3.8 0 0 0 .5-7.56A5.2 5.2 0 0 0 7.1 10.2 3.2 3.2 0 0 0 8 16.5Z" fill="currentColor" stroke="none" />
          <path d="M5 20.2h14" />
        </Svg>
      );
    case "mist":
      return (
        <Svg {...props}>
          <path d="M4 8.5h16M6 12.5h13M4 16.5h12M8 20.5h10" />
        </Svg>
      );
    case "rain":
      return (
        <Svg {...props}>
          <path d="M7.5 14.5h9.2a3.9 3.9 0 0 0 .6-7.75A5.4 5.4 0 0 0 6.9 8 3.3 3.3 0 0 0 7.5 14.5Z" fill="currentColor" stroke="none" />
          <path d="M8.5 17.5l-1 3M12.5 17.5l-1 3M16.5 17.5l-1 3" />
        </Svg>
      );
  }
}

export function SearchGlyph(props: GlyphProps): ReactNode {
  return (
    <Svg {...props}>
      <circle cx="10.5" cy="10.5" r="6.2" strokeWidth={2.2} />
      <path d="M15.2 15.2 20 20" strokeWidth={2.4} />
    </Svg>
  );
}

export function ChevronGlyph({ up = false, ...props }: GlyphProps & { up?: boolean }): ReactNode {
  return (
    <Svg {...props}>
      <path d={up ? "M6.5 14.5 12 9l5.5 5.5" : "M6.5 9.5 12 15l5.5-5.5"} strokeWidth={2.2} />
    </Svg>
  );
}

export function CheckGlyph(props: GlyphProps): ReactNode {
  return (
    <Svg {...props}>
      <path d="M6 12.5l4 4 8-9" strokeWidth={2.6} />
    </Svg>
  );
}

export function ReturnGlyph(props: GlyphProps): ReactNode {
  return (
    <Svg {...props}>
      <path d="M19 5v6.5a3 3 0 0 1-3 3H6" strokeWidth={2} />
      <path d="M9.5 10.5 5.5 14.5l4 4" strokeWidth={2} />
    </Svg>
  );
}
