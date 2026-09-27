/**
 * Glyphs. Drawn at 16 px on a 16 unit grid in `currentColor`, so they take the
 * runtime's vibrant ink wherever they sit on glass.
 */
import type { ReactNode } from "react";
import type { Severity } from "./data";

const svg = (children: ReactNode, size = 16): ReactNode => (
  <svg width={size} height={size} viewBox="0 0 16 16" aria-hidden="true" focusable="false">
    {children}
  </svg>
);

export const SearchIcon = (): ReactNode =>
  svg(
    <g fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <circle cx="7" cy="7" r="4.6" />
      <path d="M10.4 10.4 14 14" />
    </g>,
  );

export const PlusIcon = (): ReactNode =>
  svg(<path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />);

export const MinusIcon = (): ReactNode =>
  svg(<path d="M3 8h10" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />);

export const FitIcon = (): ReactNode =>
  svg(
    <g fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2.5 6V2.5H6M10 2.5h3.5V6M13.5 10v3.5H10M6 13.5H2.5V10" />
      <circle cx="8" cy="8" r="1.6" fill="currentColor" stroke="none" />
    </g>,
  );

export const CloseIcon = (): ReactNode =>
  svg(<path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />, 14);

export const PhoneIcon = (): ReactNode =>
  svg(
    <path
      d="M5.2 2.2 3.4 2.6c-.6.1-1 .7-.9 1.3.8 4.6 4.4 8.3 9 9.1.6.1 1.2-.3 1.3-.9l.4-1.8c.1-.5-.2-1-.7-1.2l-2-.8c-.4-.2-.9 0-1.2.3l-.7.9C7.2 8.8 6.4 8 5.9 6.6l.9-.7c.3-.3.5-.8.3-1.2l-.8-2c-.2-.5-.6-.6-1.1-.5Z"
      fill="currentColor"
    />,
  );

export const HoldIcon = (): ReactNode =>
  svg(
    <g fill="currentColor">
      <rect x="4" y="3" width="2.6" height="10" rx="1" />
      <rect x="9.4" y="3" width="2.6" height="10" rx="1" />
    </g>,
  );

export const FollowIcon = (): ReactNode =>
  svg(<path d="M13.6 2.4 2.6 7.1c-.5.2-.4.9.1 1l4.1.9.9 4.1c.1.5.8.6 1 .1l4.9-10.8Z" fill="currentColor" />);

export const CameraIcon = (): ReactNode =>
  svg(
    <g fill="currentColor">
      <rect x="1.5" y="4" width="9" height="8" rx="2" />
      <path d="M11.2 7 14.5 4.8v6.4L11.2 9z" />
    </g>,
    14,
  );

/**
 * Severity, carried three ways at once: shape (octagon, triangle, circle), colour
 * (red, amber, ink) and the word in the row it sits in.
 */
export function SeverityGlyph(props: { readonly severity: Severity }): ReactNode {
  const { severity } = props;
  if (severity === "critical") {
    return (
      <svg className="glyph glyph--critical" width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
        <path d="M6 1.5h6L16.5 6v6L12 16.5H6L1.5 12V6Z" fill="var(--sev-critical)" />
        <path d="M9 5v5" stroke="#fff" strokeWidth="1.9" strokeLinecap="round" />
        <circle cx="9" cy="12.9" r="1.1" fill="#fff" />
      </svg>
    );
  }
  if (severity === "warning") {
    return (
      <svg className="glyph glyph--warning" width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
        <path d="M9 1.8c.5 0 .9.3 1.2.7l6.3 11.4c.5.9-.1 2-1.2 2H2.7c-1 0-1.7-1.1-1.2-2L7.8 2.5c.3-.4.7-.7 1.2-.7Z" fill="var(--sev-warning)" />
        <path d="M9 6.3v4.2" stroke="#2a1c00" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="9" cy="13" r="1" fill="#2a1c00" />
      </svg>
    );
  }
  return (
    <svg className="glyph glyph--info" width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
      <circle cx="9" cy="9" r="7.5" fill="currentColor" />
      <circle cx="9" cy="5.6" r="1.1" fill="var(--ink-inverse)" />
      <path d="M9 8.3v4.6" stroke="var(--ink-inverse)" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
