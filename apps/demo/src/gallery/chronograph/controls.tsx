/**
 * The glass controls beside the watch: the dial and crystal settings, the timing window, and the
 * two buttons that run the chronograph.
 *
 * All of it is ordinary Liquid Glass, over the bench and on the page's optical tuning: the
 * controls float over the mat's grid and bend it at their edges, the way the crystal bends the
 * dial. The timing window is the one reading surface. It sits over the mat's calm column, and its
 * group declares the level measured under its own footprint, because the whole canvas's average
 * (the bright dial included) is not what is behind it.
 */

import {
  APPLE_LIKE_SMOOTHING,
  GlassButton,
  GlassGroup,
  GlassMorph,
  GlassSegmentedControl,
  GlassSurface,
  useGlassRoot,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import { useEffect, useRef, type CSSProperties, type KeyboardEvent, type ReactNode } from "react";

import { elapsed, format, spoken, type ChronoState } from "./chrono";
import type { Box, Circle, CrystalId } from "./layout";
import type { Scheme } from "./palette";
import { BENCH_BACKDROP, CONTROL_THICKNESS, CRYSTALS, crystalById, TIMING_RADIUS, TIMING_THICKNESS } from "./shared";

export const CRYSTAL_MENU_CLASS = "crystal-morph";

/** The space between the crystal capsule and the platter it opens below. */
const PLATTER_GAP = 10;

export function DialSwitch(props: {
  readonly box: Box;
  readonly scheme: Scheme;
  readonly hint: BackdropHint | undefined;
  readonly onScheme: (scheme: Scheme) => void;
}): ReactNode {
  return (
    <GlassGroup id="dial" backdrop={BENCH_BACKDROP} hint={props.hint}>
      <div className="dial-switch">
        <GlassSegmentedControl
          style={{ left: props.box.x, top: props.box.y, width: props.box.width, height: props.box.height }}
          groupId="dial"
          aria-label="Dial"
          radius={20}
          thickness={CONTROL_THICKNESS}
          items={[
            { value: "light", label: "Day" },
            { value: "dark", label: "Night" },
          ]}
          value={props.scheme}
          onChange={props.onScheme}
          className="segmented"
          segmentClassName="segment"
          indicatorClassName="segment-indicator"
        />
      </div>
    </GlassGroup>
  );
}

/**
 * The crystal menu: a capsule naming the fitted crystal, which becomes the platter of crystals by
 * one matched-geometry morph in the overlay plane. Its lifecycle is the app's: Escape, a press
 * outside or a Tab out closes it, and focus returns to the capsule.
 */
export function CrystalMenu(props: {
  readonly anchor: Box;
  readonly crystal: CrystalId;
  readonly hint: BackdropHint | undefined;
  readonly open: boolean;
  readonly morphKey: string;
  readonly reducedTransparency: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly onCrystal: (id: CrystalId) => void;
  readonly onReducedTransparency: (value: boolean) => void;
}): ReactNode {
  const { anchor, crystal, open, onOpenChange } = props;
  const root = useGlassRoot();
  const trigger = useRef<HTMLButtonElement>(null);
  const platter = useRef<HTMLDivElement>(null);
  const returnFocus = useRef(false);
  const current = crystalById(crystal);

  // The morph renders its host itself; the role is written onto it after each frame.
  const role = open ? "platter" : "control";
  useEffect(() => {
    if (root === null) return;
    const write = (): void => {
      const host = document.querySelector(`.${CRYSTAL_MENU_CLASS}`);
      if (host !== null && host.getAttribute("data-glass-role") !== role) host.setAttribute("data-glass-role", role);
    };
    write();
    return root.subscribe(write);
  }, [root, role]);

  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent): void => {
      const target = event.target as Node | null;
      const host = document.querySelector(`.${CRYSTAL_MENU_CLASS}`);
      if (target !== null && host !== null && host.contains(target)) return;
      onOpenChange(false);
    };
    document.addEventListener("pointerdown", onPointer, true);
    return () => document.removeEventListener("pointerdown", onPointer, true);
  }, [open, onOpenChange]);

  useEffect(() => {
    if (open) {
      platter.current?.querySelector<HTMLElement>('[role="radio"][aria-checked="true"]')?.focus({ preventScroll: true });
    } else if (returnFocus.current) {
      returnFocus.current = false;
      trigger.current?.focus({ preventScroll: true });
    }
  }, [open]);

  const close = (focusTrigger: boolean): void => {
    returnFocus.current = focusTrigger;
    onOpenChange(false);
  };

  const onPlatterKey = (event: KeyboardEvent<HTMLDivElement>): void => {
    if (event.key === "Escape") {
      event.preventDefault();
      close(true);
      return;
    }
    const target = event.target as HTMLElement;
    if (target.getAttribute("role") !== "radio") return;
    const step =
      event.key === "ArrowDown" || event.key === "ArrowRight" ? 1 : event.key === "ArrowUp" || event.key === "ArrowLeft" ? -1 : 0;
    if (step === 0) return;
    event.preventDefault();
    const index = CRYSTALS.findIndex((c) => c.id === crystal);
    const next = CRYSTALS[(index + step + CRYSTALS.length) % CRYSTALS.length];
    if (next === undefined) return;
    props.onCrystal(next.id);
    requestAnimationFrame(() => {
      platter.current?.querySelector<HTMLElement>(`[data-crystal="${next.id}"]`)?.focus({ preventScroll: true });
    });
  };

  return (
    <GlassGroup id="crystal-menu" backdrop={BENCH_BACKDROP} hint={props.hint}>
      <div className="crystal-anchor" style={{ left: anchor.x, top: anchor.y }}>
        <GlassMorph
          key={props.morphKey}
          open={open}
          groupId="crystal-menu"
          plane="overlay"
          openPlane="overlay"
          radius={anchor.height / 2}
          openRadius={26}
          thickness={CONTROL_THICKNESS}
          openThickness={CONTROL_THICKNESS}
          profile={APPLE_LIKE_SMOOTHING}
          openProfile={APPLE_LIKE_SMOOTHING}
          placement="below-end"
          gap={PLATTER_GAP}
          className={`glass ${CRYSTAL_MENU_CLASS}`}
          aria-label="Crystal"
        >
          {({ open: isOpen }) =>
            isOpen ? (
              <div
                ref={platter}
                className="platter"
                style={{ "--platter-top": `${anchor.y + anchor.height + PLATTER_GAP}px` } as CSSProperties}
                role="dialog"
                aria-label="Crystal"
                onKeyDown={onPlatterKey}
                onBlur={(event) => {
                  const next = event.relatedTarget as Node | null;
                  if (next !== null && !event.currentTarget.contains(next)) close(false);
                }}
              >
                <p className="platter-title">Crystal</p>
                <div role="radiogroup" aria-label="Crystal">
                  {CRYSTALS.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      role="radio"
                      data-crystal={c.id}
                      aria-checked={c.id === crystal}
                      tabIndex={c.id === crystal ? 0 : -1}
                      className="platter-option"
                      onClick={() => props.onCrystal(c.id)}
                    >
                      <span className="option-mark" aria-hidden="true" />
                      <span className="option-text">
                        <span className="option-name">{c.name}</span>
                        <span className="option-note">{c.note}</span>
                      </span>
                    </button>
                  ))}
                </div>
                <p className="platter-note">
                  The three crystals are vitrea’s glass tuned toward clear optics; Apple’s glass is the
                  material as calibrated.
                </p>
                <div className="platter-rule" aria-hidden="true" />
                <label className="platter-switch">
                  <span>Reduce transparency</span>
                  <input
                    type="checkbox"
                    role="switch"
                    checked={props.reducedTransparency}
                    onChange={(event) => props.onReducedTransparency(event.currentTarget.checked)}
                  />
                </label>
              </div>
            ) : (
              <button
                ref={trigger}
                type="button"
                className="crystal-trigger"
                aria-haspopup="dialog"
                aria-expanded={false}
                style={{ width: anchor.width, height: anchor.height }}
                onClick={() => onOpenChange(true)}
              >
                <span className="trigger-label">Crystal</span>
                <span className="trigger-value">{current.name}</span>
              </button>
            )
          }
        </GlassMorph>
      </div>
    </GlassGroup>
  );
}

/**
 * The timing window: the running time, large, and the laps under it. The running figures change
 * every frame and are written straight to the element from the root's loop; they are hidden from
 * assistive technology, which hears the time when the chronograph stops and each lap as it is taken.
 */
export function TimingWindow(props: {
  readonly box: Box;
  readonly chrono: ChronoState;
  readonly hint: BackdropHint | undefined;
}): ReactNode {
  const { box, chrono } = props;
  const root = useGlassRoot();
  const readout = useRef<HTMLSpanElement>(null);
  const chronoRef = useRef(chrono);
  chronoRef.current = chrono;

  useEffect(() => {
    if (root === null) return;
    let last = "";
    return root.subscribe(() => {
      const text = format(elapsed(chronoRef.current, performance.now()));
      if (text !== last && readout.current !== null) {
        readout.current.textContent = text;
        last = text;
      }
    });
  }, [root]);

  const total = elapsed(chrono, performance.now());
  const status = chrono.running
    ? chrono.laps[0] === undefined
      ? "Running"
      : `Lap ${chrono.laps[0].index}, ${spoken(chrono.laps[0].split)}`
    : total > 0
      ? `Stopped at ${spoken(total)}`
      : "Ready";
  const fastest = chrono.laps.length > 1 ? Math.min(...chrono.laps.map((l) => l.split)) : null;
  const slowest = chrono.laps.length > 1 ? Math.max(...chrono.laps.map((l) => l.split)) : null;

  return (
    <GlassGroup id="timing" backdrop={BENCH_BACKDROP} hint={props.hint}>
      <GlassSurface asChild radius={TIMING_RADIUS} thickness={TIMING_THICKNESS} foreground="vibrant">
        <section
          className="timing"
          aria-label="Timing"
          data-glass-role="window"
          style={{ left: box.x, top: box.y, width: box.width, height: box.height }}
        >
          <div className="timing-head">
            <span className="timing-label">{chrono.running ? "Running" : total > 0 ? "Stopped" : "Chronograph"}</span>
            <span ref={readout} className="timing-readout" aria-hidden="true">
              {format(total)}
            </span>
            <span className="visually-hidden" aria-live="polite">
              {status}
            </span>
          </div>
          <div className="laps" tabIndex={chrono.laps.length > 0 ? 0 : -1} aria-label="Laps">
            {chrono.laps.length === 0 ? (
              <p className="laps-empty">Lap splits the second hand and keeps the chronograph running.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th scope="col">Lap</th>
                    <th scope="col">Split</th>
                    <th scope="col">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {chrono.laps.map((lap) => (
                    <tr
                      key={lap.index}
                      data-extreme={lap.split === fastest ? "fastest" : lap.split === slowest ? "slowest" : undefined}
                    >
                      <td>{lap.index}</td>
                      <td>{format(lap.split)}</td>
                      <td>{format(lap.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          <p className="timing-keys" aria-hidden="true">
            <kbd>Space</kbd> start and stop <span className="dot">·</span> <kbd>L</kbd> lap <span className="dot">·</span>{" "}
            <kbd>R</kbd> reset
          </p>
        </section>
      </GlassSurface>
    </GlassGroup>
  );
}

/** Lap (or Reset, once stopped) and Start (Stop while running): two round glass buttons. */
export function Pushers(props: {
  readonly lap: Circle;
  readonly start: Circle;
  readonly chrono: ChronoState;
  readonly hint: BackdropHint | undefined;
  readonly onStartStop: () => void;
  readonly onLapReset: () => void;
}): ReactNode {
  const { lap, start, chrono } = props;
  const canReset = !chrono.running && (chrono.banked > 0 || chrono.laps.length > 0);
  const circle = (c: Circle): React.CSSProperties => ({
    left: c.cx - c.r,
    top: c.cy - c.r,
    width: c.r * 2,
    height: c.r * 2,
  });
  return (
    <>
      <GlassGroup id="lap" backdrop={BENCH_BACKDROP} hint={props.hint}>
        <GlassButton
          capsule
          thickness={CONTROL_THICKNESS}
          className="pusher"
          data-glass-role="control"
          style={circle(lap)}
          disabled={!chrono.running && !canReset}
          aria-keyshortcuts={chrono.running ? "L" : "R"}
          onClick={props.onLapReset}
        >
          {chrono.running ? "Lap" : "Reset"}
        </GlassButton>
      </GlassGroup>
      <GlassGroup id="start" backdrop={BENCH_BACKDROP} hint={props.hint}>
        <GlassButton
          capsule
          thickness={CONTROL_THICKNESS}
          tint={chrono.running ? "rgb(255 69 58 / 0.6)" : "rgb(48 209 88 / 0.6)"}
          className="pusher pusher-primary"
          data-glass-role="control"
          style={circle(start)}
          aria-keyshortcuts="Space"
          onClick={props.onStartStop}
        >
          {chrono.running ? "Stop" : "Start"}
        </GlassButton>
      </GlassGroup>
    </>
  );
}
