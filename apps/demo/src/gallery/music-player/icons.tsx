/**
 * The player's glyphs, drawn to the proportions of the platform's own symbols: filled transport
 * shapes with softened corners, a speaker with its waves, and the queue's list-with-plus. They take
 * `currentColor`, so they are ink like the labels beside them and never a colour of their own.
 */

import type { ReactNode, SVGProps } from "react";

type IconProps = { readonly size?: number | undefined } & Omit<SVGProps<SVGSVGElement>, "children">;

function Icon(props: IconProps & { readonly children: ReactNode }) {
  const { size = 20, children, viewBox = "0 0 24 24", ...rest } = props;
  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      fill="currentColor"
      aria-hidden="true"
      focusable="false"
      {...rest}
    >
      {children}
    </svg>
  );
}

export const PlayIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M7.2 4.6c0-1.1 1.2-1.8 2.2-1.2l11 6.9c.9.6.9 1.9 0 2.5l-11 6.9c-1 .6-2.2-.1-2.2-1.2z" />
  </Icon>
);

export const PauseIcon = (props: IconProps) => (
  <Icon {...props}>
    <rect x="5.6" y="3.8" width="4.6" height="16.4" rx="1.3" />
    <rect x="13.8" y="3.8" width="4.6" height="16.4" rx="1.3" />
  </Icon>
);

export const PreviousIcon = (props: IconProps) => (
  <Icon {...props} viewBox="0 0 28 24">
    <path d="M13.2 5.3c0-.9-1-1.4-1.7-.9L3.3 10.9c-.6.5-.6 1.4 0 1.9l8.2 6.5c.7.5 1.7 0 1.7-.9z" />
    <path d="M25.2 5.3c0-.9-1-1.4-1.7-.9l-8.2 6.5c-.6.5-.6 1.4 0 1.9l8.2 6.5c.7.5 1.7 0 1.7-.9z" />
  </Icon>
);

export const NextIcon = (props: IconProps) => (
  <Icon {...props} viewBox="0 0 28 24">
    <path d="M2.8 5.3c0-.9 1-1.4 1.7-.9l8.2 6.5c.6.5.6 1.4 0 1.9l-8.2 6.5c-.7.5-1.7 0-1.7-.9z" />
    <path d="M14.8 5.3c0-.9 1-1.4 1.7-.9l8.2 6.5c.6.5.6 1.4 0 1.9l-8.2 6.5c-.7.5-1.7 0-1.7-.9z" />
  </Icon>
);

export const SpeakerIcon = (props: IconProps & { readonly muted?: boolean }) => {
  const { muted = false, ...rest } = props;
  return (
    <Icon {...rest}>
      <path d="M3.5 9.2c0-.7.5-1.2 1.2-1.2h2.6l4.1-3.6c.7-.6 1.8-.1 1.8.8v13.6c0 .9-1.1 1.4-1.8.8L7.3 16H4.7c-.7 0-1.2-.5-1.2-1.2z" />
      {muted ? (
        <path
          d="M16.2 9.2l5 5.6m0-5.6l-5 5.6"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          fill="none"
        />
      ) : (
        <>
          <path
            d="M16 9.1c.8.8 1.2 1.8 1.2 2.9s-.4 2.1-1.2 2.9"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M18.6 6.6c1.4 1.4 2.2 3.3 2.2 5.4s-.8 4-2.2 5.4"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            fill="none"
          />
        </>
      )}
    </Icon>
  );
};

export const QueueAddIcon = (props: IconProps) => (
  <Icon {...props}>
    <rect x="3" y="5" width="12" height="1.9" rx=".95" />
    <rect x="3" y="10.5" width="12" height="1.9" rx=".95" />
    <rect x="3" y="16" width="7.5" height="1.9" rx=".95" />
    <rect x="16.6" y="11.6" width="1.9" height="9" rx=".95" />
    <rect x="13.05" y="15.15" width="9" height="1.9" rx=".95" />
  </Icon>
);

export const ChevronDownIcon = (props: IconProps) => (
  <Icon {...props}>
    <path
      d="M6.5 9.5l5.5 5.5 5.5-5.5"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
  </Icon>
);

/** The sounding-now mark: three still bars. A status, so it does not animate. */
export const SoundingIcon = (props: IconProps) => (
  <Icon {...props}>
    <rect x="4" y="9" width="3.4" height="10" rx="1.2" />
    <rect x="10.3" y="4.5" width="3.4" height="14.5" rx="1.2" />
    <rect x="16.6" y="11.5" width="3.4" height="7.5" rx="1.2" />
  </Icon>
);
