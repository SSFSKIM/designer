/**
 * The two playback housings: the transport and the volume.
 *
 * Each is one capsule of glass with plain controls inside it. The housing is `interactive`, so a
 * press lights the glass from the pointer and flexes it on the runtime's spring, and that is the
 * whole press: the buttons inside show a quiet plate on hover and focus, a fill because the glass
 * is already the material, and add no colour and no scale of their own when pressed. Sliders are
 * native range inputs drawn as fills: the skill's sanctioned lift of a knob into glass has no
 * nested form in vitrea, so the knob stays a fill that grows while held, and the record says so.
 */

import { GlassSurface } from "@vitreajs/vitrea-react";
import type { CSSProperties, ReactNode } from "react";

import { clock } from "./data";
import { NextIcon, PauseIcon, PlayIcon, PreviousIcon, SpeakerIcon } from "./icons";

export interface TransportProps {
  readonly title: string;
  readonly artist: string;
  readonly seconds: number;
  readonly elapsed: number;
  readonly playing: boolean;
  readonly canGoBack: boolean;
  readonly canGoForward: boolean;
  readonly onToggle: () => void;
  readonly onPrevious: () => void;
  readonly onNext: () => void;
  readonly onSeek: (seconds: number) => void;
}

const fraction = (value: number, max: number): string =>
  `${max <= 0 ? 0 : Math.min(100, Math.max(0, (value / max) * 100)).toFixed(2)}%`;

export function Transport(props: TransportProps): ReactNode {
  const { title, artist, seconds, elapsed, playing, canGoBack, canGoForward } = props;
  const remaining = Math.max(0, seconds - Math.floor(elapsed));
  return (
    <GlassSurface
      capsule
      interactive
      thickness={8}
      className="mp-transport"
      data-mp-group="transport"
      role="group"
      aria-label="Transport"
    >
      <div className="mp-housing-inner mp-transport-inner">
        <button
          type="button"
          className="mp-tbtn mp-tbtn-skip"
          aria-label={elapsed > 3 || !canGoBack ? "Restart track" : "Previous track"}
          onClick={props.onPrevious}
        >
          <PreviousIcon size={22} />
        </button>
        <button
          type="button"
          className="mp-tbtn mp-tbtn-play"
          aria-label={playing ? "Pause" : "Play"}
          onClick={props.onToggle}
        >
          {playing ? <PauseIcon size={26} /> : <PlayIcon size={28} />}
        </button>
        <button
          type="button"
          className="mp-tbtn mp-tbtn-skip"
          aria-label="Next track"
          disabled={!canGoForward}
          onClick={props.onNext}
        >
          <NextIcon size={22} />
        </button>
        <span className="mp-time" aria-hidden="true">
          {clock(elapsed)}
        </span>
        <input
          type="range"
          className="mp-range mp-scrub"
          min={0}
          max={seconds}
          step={1}
          value={Math.floor(elapsed)}
          aria-label={`Position in ${title} by ${artist}`}
          aria-valuetext={`${clock(elapsed)} of ${clock(seconds)}`}
          style={{ "--mp-fill": fraction(elapsed, seconds) } as CSSProperties}
          onChange={(event) => props.onSeek(Number(event.currentTarget.value))}
        />
        <span className="mp-time mp-time-remaining" aria-hidden="true">
          −{clock(remaining)}
        </span>
      </div>
    </GlassSurface>
  );
}

export interface VolumeProps {
  readonly level: number;
  readonly muted: boolean;
  readonly onLevel: (level: number) => void;
  readonly onMute: (muted: boolean) => void;
}

export function Volume(props: VolumeProps): ReactNode {
  const { level, muted } = props;
  const shown = muted ? 0 : level;
  return (
    <GlassSurface
      capsule
      interactive
      thickness={8}
      className="mp-volume"
      data-mp-group="volume"
      role="group"
      aria-label="Volume"
    >
      <div className="mp-housing-inner mp-volume-inner">
        <button
          type="button"
          className="mp-vbtn"
          aria-label="Mute"
          aria-pressed={muted}
          onClick={() => props.onMute(!muted)}
        >
          <SpeakerIcon size={20} muted={muted || level === 0} />
        </button>
        <input
          type="range"
          className="mp-range mp-level"
          min={0}
          max={100}
          step={1}
          value={shown}
          aria-label="Volume"
          aria-valuetext={muted ? "Muted" : `${shown} percent`}
          style={{ "--mp-fill": fraction(shown, 100) } as CSSProperties}
          onChange={(event) => {
            const next = Number(event.currentTarget.value);
            props.onLevel(next);
            if (muted && next > 0) props.onMute(false);
          }}
        />
      </div>
    </GlassSurface>
  );
}
