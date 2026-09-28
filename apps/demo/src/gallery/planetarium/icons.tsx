/** The page's few glyphs, inline so they take the ink of the text beside them. */

import type { ReactNode } from "react";

interface GlyphProps {
  readonly size?: number;
  readonly className?: string;
}

function Glyph(props: GlyphProps & { readonly children: ReactNode; readonly stroke?: boolean }): ReactNode {
  const { size = 16, className, children, stroke = true } = props;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      className={className}
      aria-hidden="true"
      focusable="false"
      fill={stroke ? "none" : "currentColor"}
      stroke={stroke ? "currentColor" : "none"}
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {children}
    </svg>
  );
}

export function ChevronGlyph(props: GlyphProps): ReactNode {
  return (
    <Glyph {...props}>
      <path d="M4.5 6.5 8 10l3.5-3.5" />
    </Glyph>
  );
}

export function PlayGlyph(props: GlyphProps): ReactNode {
  return (
    <Glyph {...props} stroke={false}>
      <path d="M5 3.2v9.6a.6.6 0 0 0 .9.5l7.3-4.8a.6.6 0 0 0 0-1L5.9 2.7a.6.6 0 0 0-.9.5Z" />
    </Glyph>
  );
}

export function PauseGlyph(props: GlyphProps): ReactNode {
  return (
    <Glyph {...props} stroke={false}>
      <rect x="3.5" y="3" width="3.2" height="10" rx="0.8" />
      <rect x="9.3" y="3" width="3.2" height="10" rx="0.8" />
    </Glyph>
  );
}

export function LocateGlyph(props: GlyphProps): ReactNode {
  return (
    <Glyph {...props}>
      <circle cx="8" cy="8" r="4.2" />
      <path d="M8 1.5v2.3M8 12.2v2.3M1.5 8h2.3M12.2 8h2.3" />
      <circle cx="8" cy="8" r="1" fill="currentColor" stroke="none" />
    </Glyph>
  );
}

export function NowGlyph(props: GlyphProps): ReactNode {
  return (
    <Glyph {...props}>
      <circle cx="8" cy="8" r="5.5" />
      <path d="M8 5v3.2l2.2 1.3" />
    </Glyph>
  );
}

export function CheckGlyph(props: GlyphProps): ReactNode {
  return (
    <Glyph {...props}>
      <path d="M3.5 8.5 6.5 11.5 12.5 5" />
    </Glyph>
  );
}
