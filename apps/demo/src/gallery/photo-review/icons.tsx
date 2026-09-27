/**
 * The control layer's symbols. Drawn in `currentColor`, so on glass they take the runtime's
 * published ink and on the ground the page's own; a symbol stands in for a word wherever a
 * photographer already knows one (the skill's type law), and every button still carries a name.
 */
import { useId, type ReactNode } from "react";

const Svg = ({ children, size = 20 }: { children: ReactNode; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 20 20" fill="none" stroke="currentColor"
    strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
    {children}
  </svg>
);

/** Exposure: a sun, its disc half filled, the photographer's shorthand for light. */
export const ExposureIcon = () => (
  <Svg>
    <circle cx="10" cy="10" r="3.6" />
    <path d="M10 6.4a3.6 3.6 0 0 1 0 7.2z" fill="currentColor" stroke="none" />
    <path d="M10 1.8v2M10 16.2v2M1.8 10h2M16.2 10h2M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M4.2 15.8l1.4-1.4M14.4 5.6l1.4-1.4" />
  </Svg>
);

/** White balance: a thermometer, for colour temperature. */
export const WhiteBalanceIcon = () => (
  <Svg>
    <path d="M8.2 11.6V4.2a1.8 1.8 0 0 1 3.6 0v7.4a3.4 3.4 0 1 1-3.6 0z" />
    <circle cx="10" cy="14.4" r="1.5" fill="currentColor" stroke="none" />
    <path d="M10 13V8" />
    <path d="M14.2 5h2M14.2 8h1.4" />
  </Svg>
);

/** Crop: the two overlapping corners every editor draws. */
export const CropIcon = () => (
  <Svg>
    <path d="M5.4 1.8v11.6a1 1 0 0 0 1 1h11.8" />
    <path d="M1.8 5.4h11a1 1 0 0 1 1 1v11.8" />
  </Svg>
);

/** Reject: a cross; when set, a disc with the cross cut out of it, so it needs no second ink. */
export function RejectIcon({ on }: { on: boolean }) {
  const mask = `reject-cut-${useId().replace(/[^a-zA-Z0-9_-]/g, "")}`;
  return (
    <Svg>
      {on ? (
        <>
          <mask id={mask}>
            <rect width="20" height="20" fill="white" />
            <path d="M7.2 7.2l5.6 5.6M12.8 7.2l-5.6 5.6" stroke="black" strokeWidth={1.8} />
          </mask>
          <circle cx="10" cy="10" r="7.8" fill="currentColor" stroke="none" mask={`url(#${mask})`} />
        </>
      ) : (
        <>
          <circle cx="10" cy="10" r="7.2" />
          <path d="M7.2 7.2l5.6 5.6M12.8 7.2l-5.6 5.6" />
        </>
      )}
    </Svg>
  );
}

export const PickIcon = ({ on }: { on: boolean }) => (
  <Svg>
    <path d="M5 18.2V2.6" />
    <path d="M5 3.2h10.2l-2.4 3.6 2.4 3.6H5" fill={on ? "currentColor" : "none"} />
  </Svg>
);

const STAR = "M10 2.2l2.35 4.9 5.35.72-3.9 3.72.97 5.32L10 14.3l-4.77 2.56.97-5.32-3.9-3.72 5.35-.72z";

export const StarIcon = ({ on, size = 20 }: { on: boolean; size?: number }) => (
  <Svg size={size}>
    <path d={STAR} fill={on ? "currentColor" : "none"} strokeWidth={on ? 1.2 : 1.4} />
  </Svg>
);
