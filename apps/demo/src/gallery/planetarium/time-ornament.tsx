/**
 * The Time ornament, hung below the window: the page's clock, an hour either way, and the night
 * in time-lapse. Pressed, its clock becomes the Timeline platter, where the whole night is a
 * scrubber from noon to noon with sunset and sunrise marked on it.
 *
 * The scrubber's night is taken once, when the platter opens, from the time at that moment, and
 * held while it stays open: a scale whose origin followed the scrubbed time would jump a day when
 * the thumb reached the end noon. Scrubbing stops five minutes short of that noon, inside the same
 * night; only a time the scrubber did not set (playing past noon, Now) takes a new night.
 */

const SCRUB_STEP_MINUTES = 5;

import { useGlassRootHandle, type BackdropHint } from "@vitreajs/vitrea-react";
import { useRef, useState, type ReactNode } from "react";

import { formatDate, formatDayMonth, formatTime, nightSpan, type Place } from "./astro";
import type { ClockMode } from "./clock";
import { ChevronGlyph, NowGlyph, PauseGlyph, PlayGlyph } from "./icons";
import { MorphOrnament } from "./morph-ornament";
import { usePlatterPress } from "./platter-press";
import type { GroupMaterial } from "./shared";
import type { Box } from "./sky/renderer";

export const TIME_HOST_CLASS = "time-morph";

export function TimeOrnament(props: {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly morphKey: string;
  readonly place: Place;
  readonly time: number;
  readonly clock: ClockMode;
  readonly sunset: Date | undefined;
  readonly sunrise: Date | undefined;
  readonly reducedMotion: boolean;
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly onHostBox: (box: Box | undefined) => void;
  readonly onStep: (hours: number) => void;
  readonly onScrub: (time: number) => void;
  readonly onPlay: (playing: boolean) => void;
  readonly onNow: () => void;
}): ReactNode {
  const { place, time, clock, open } = props;
  const { root } = useGlassRootHandle();
  const scrubber = useRef<HTMLInputElement>(null);
  usePlatterPress(root, `.${TIME_HOST_CLASS}`, open, props.reducedMotion);
  const zone = place.timeZone;
  const playing = clock.kind === "playing";

  // The night the open platter scrubs: seeded on opening, kept until it closes or the time leaves it.
  const [held, setHeld] = useState<{ readonly zone: string; readonly start: number; readonly end: number }>();
  if (!open && held !== undefined) setHeld(undefined);
  const holds = held !== undefined && held.zone === zone && time >= held.start && time < held.end;
  if (open && !holds) {
    const span = nightSpan(new Date(time), zone);
    setHeld({ zone, start: span.start.getTime(), end: span.end.getTime() });
  }
  const night = holds ? held : nightSpanOf(time, zone);
  const span = Math.round((night.end - night.start) / 60_000);
  const minutes = Math.max(0, Math.min(span, Math.round((time - night.start) / 60_000)));
  const scrubTo = (value: number): void => {
    const at = Math.min(night.start + value * 60_000, night.end - SCRUB_STEP_MINUTES * 60_000);
    props.onScrub(Math.max(night.start, at));
  };

  return (
    <MorphOrnament
      groupId="time"
      hostClass={TIME_HOST_CLASS}
      label="Time"
      box={props.box}
      hint={props.hint}
      material={props.material}
      morphKey={props.morphKey}
      placement="above-start"
      open={open}
      onOpenChange={props.onOpenChange}
      onHostBox={props.onHostBox}
      closed={(trigger, box) => (
        <div className="time-face" style={{ width: box.width, height: box.height }}>
          <button type="button" className="face-button" aria-label="An hour earlier" onClick={() => props.onStep(-1)}>
            −1 h
          </button>
          <button
            ref={trigger}
            type="button"
            className="face-trigger time-trigger"
            aria-haspopup="dialog"
            aria-expanded={false}
            aria-label={`Timeline: ${formatTime(new Date(time), zone)}, ${formatDate(new Date(time), zone)}${clock.kind === "live" ? ", now" : ""}`}
            onClick={() => props.onOpenChange(true)}
          >
            <span className="time-clock">{formatTime(new Date(time), zone)}</span>
            <span className="time-date">{formatDate(new Date(time), zone)}</span>
            <ChevronGlyph size={14} className="face-chevron" />
          </button>
          <button type="button" className="face-button" aria-label="An hour later" onClick={() => props.onStep(1)}>
            +1 h
          </button>
          <button
            type="button"
            className="face-button face-icon"
            aria-label={playing ? "Pause the night" : "Play the night"}
            aria-pressed={playing}
            onClick={() => props.onPlay(!playing)}
          >
            {playing ? <PauseGlyph size={16} /> : <PlayGlyph size={16} />}
          </button>
        </div>
      )}
      platter={(close) => (
        <div className="time-platter">
          <p className="platter-title">Timeline</p>
          <p className="platter-clock">{formatTime(new Date(time), zone)}</p>
          <p className="platter-date">
            {formatDayMonth(new Date(time), zone)} · {place.name}
            {clock.kind === "live" ? " · now" : playing ? " · playing" : ""}
          </p>
          <div className="scrub">
            <input
              ref={scrubber}
              className="scrub-range"
              type="range"
              min={0}
              max={span}
              step={SCRUB_STEP_MINUTES}
              value={minutes}
              aria-label="Time, from noon to the next noon"
              aria-valuetext={`${formatTime(new Date(time), zone)}, ${formatDate(new Date(time), zone)}`}
              onChange={(event) => scrubTo(Number(event.target.value))}
            />
            <div className="scrub-scale" aria-hidden="true">
              <span>Noon</span>
              <span className="scrub-mark" style={{ left: `${markAt(props.sunset, night)}%` }}>
                Sunset {props.sunset === undefined ? "—" : formatTime(props.sunset, zone)}
              </span>
              <span className="scrub-mark" style={{ left: `${markAt(props.sunrise, night)}%` }}>
                Sunrise {props.sunrise === undefined ? "—" : formatTime(props.sunrise, zone)}
              </span>
              <span>Noon</span>
            </div>
          </div>
          <div className="platter-actions">
            <button type="button" className="action" onClick={() => props.onPlay(!playing)} aria-pressed={playing}>
              {playing ? <PauseGlyph size={14} /> : <PlayGlyph size={14} />}
              {playing ? "Pause" : "Play the night"}
            </button>
            <button type="button" className="action" onClick={props.onNow} aria-pressed={clock.kind === "live"}>
              <NowGlyph size={14} />
              Now
            </button>
            <button type="button" className="action action-quiet" onClick={() => close(true)}>
              Done
            </button>
          </div>
        </div>
      )}
    />
  );
}

function nightSpanOf(time: number, zone: string): { readonly start: number; readonly end: number } {
  const span = nightSpan(new Date(time), zone);
  return { start: span.start.getTime(), end: span.end.getTime() };
}

/** A time's position on the noon-to-noon scale, per cent; off the scale when undefined. */
function markAt(date: Date | undefined, night: { readonly start: number; readonly end: number }): number {
  if (date === undefined) return -100;
  return Math.max(0, Math.min(100, ((date.getTime() - night.start) / (night.end - night.start)) * 100));
}
