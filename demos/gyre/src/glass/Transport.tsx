/**
 * The transport: the one bottom toolbar. Pause, scrub an hour either way, and
 * return to the observation time. Each member is a real `<button>`; the icon-only
 * one carries its name in `aria-label` and its state in `aria-pressed`.
 */

import { GlassButton, GlassIconButton, GlassToolbar } from "@vitreajs/vitrea-react";
import type { ReactNode } from "react";

import { FIELD_TEXTURE_ID } from "../field/Field";

export interface TransportProps {
  readonly playing: boolean;
  readonly offsetHours: number;
  readonly onTogglePlaying: () => void;
  readonly onScrub: (deltaHours: number) => void;
  readonly onNow: () => void;
}

export const SCRUB_LIMIT_HOURS = 6;

export function Transport(props: TransportProps): ReactNode {
  return (
    <GlassToolbar
      aria-label="Time"
      className="transport"
      groupProps={{ id: "transport", backdrop: { kind: "texture", id: FIELD_TEXTURE_ID } }}
    >
      <GlassIconButton
        className="control control--icon"
        thickness={8}
        aria-label={props.playing ? "Pause the field" : "Play the field"}
        aria-pressed={!props.playing}
        onClick={props.onTogglePlaying}
      >
        {props.playing ? (
          <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">
            <path d="M4 3h3v10H4zM9 3h3v10H9z" fill="currentColor" />
          </svg>
        ) : (
          <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">
            <path d="M5 3l8 5-8 5z" fill="currentColor" />
          </svg>
        )}
      </GlassIconButton>
      <GlassButton
        className="control control--data"
        capsule
        thickness={8}
        disabled={props.offsetHours <= -SCRUB_LIMIT_HOURS}
        onClick={() => props.onScrub(-1)}
      >
        −1 h
      </GlassButton>
      <GlassButton
        className="control"
        capsule
        thickness={8}
        disabled={props.offsetHours === 0}
        onClick={props.onNow}
      >
        Now
      </GlassButton>
      <GlassButton
        className="control control--data"
        capsule
        thickness={8}
        disabled={props.offsetHours >= SCRUB_LIMIT_HOURS}
        onClick={() => props.onScrub(1)}
      >
        +1 h
      </GlassButton>
    </GlassToolbar>
  );
}
