/**
 * The probe: the page's signature element (DESIGN.md §0). One circular glass
 * surface the reader drags over the field, reading the field at its centre.
 *
 * It is a `<button>` under `GlassSurface asChild`, so it is focusable, named, and
 * moved with the arrow keys as well as the pointer. Position is written straight
 * to the element's `left` and `top` on every pointer event rather than through
 * React state: the runtime measures the box once per frame and fits the material
 * to it, so the only thing between the pointer and the glass is layout. The
 * reading is written into text nodes on the runtime's own ticker, a few times a
 * second, which is as fast as a number is readable.
 *
 * The initial box is inline from the first render, never the layer's origin: a
 * host measured before it is placed would overlap the nav for a frame, and the
 * radius is declared from the diameter rather than derived by `capsule`, which
 * reads the box the surface first had.
 *
 * The probe's group samples the registered field texture, so it never sits over
 * content: `layout.ts` clamps it to the field.
 */

import { GlassGroup, GlassSurface, useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useImperativeHandle, useRef, type ReactNode, type Ref } from "react";

import { formatBearing, formatLat, formatLon } from "../data";
import { fieldTime, type FieldClock } from "../field/clock";
import { FIELD_TEXTURE_ID } from "../field/Field";
import { sampleField } from "../field/noise";
import { layerById, REGION, type LayerId } from "../field/palettes";
import { clampProbe, fieldRect, probeDiameter } from "../layout";

export interface ProbeHandle {
  /** Move the probe to a viewport fraction: `u` across, `v` up. Clamped. */
  moveTo(u: number, v: number): void;
  reset(): void;
}

export interface ProbeProps {
  readonly layer: LayerId;
  readonly clock: FieldClock;
  readonly narrow: boolean;
  readonly hidden: boolean;
  readonly ref: Ref<ProbeHandle>;
}

const KEY_STEP = 16;
const KEY_STEP_LARGE = 64;
const READING_INTERVAL_MS = 120;

function fieldCentre(): { readonly x: number; readonly y: number } {
  const field = fieldRect(window.innerWidth, window.innerHeight);
  return { x: (field.left + field.right) / 2, y: (field.top + field.bottom) / 2 };
}

export function Probe(props: ProbeProps): ReactNode {
  const ticker = useGlassTicker();
  const hostRef = useRef<HTMLButtonElement>(null);
  const valueRef = useRef<HTMLSpanElement>(null);
  const bearingRef = useRef<HTMLSpanElement>(null);
  const positionRef = useRef<HTMLSpanElement>(null);
  const layerRef = useRef(props.layer);
  layerRef.current = props.layer;
  const { clock } = props;
  const diameter = probeDiameter(props.narrow ? 0 : Number.MAX_SAFE_INTEGER);

  /** Centre, in viewport px. */
  const centre = useRef(fieldCentre());

  const place = (x: number, y: number): void => {
    const host = hostRef.current;
    const clamped = clampProbe(x, y, diameter, fieldRect(window.innerWidth, window.innerHeight));
    centre.current = clamped;
    if (host === null) return;
    host.style.left = `${clamped.x - diameter / 2}px`;
    host.style.top = `${clamped.y - diameter / 2}px`;
  };

  const reset = (): void => {
    const initial = fieldCentre();
    place(initial.x, initial.y);
  };

  useImperativeHandle(props.ref, () => ({
    moveTo(u, v) {
      place(u * window.innerWidth, (1 - v) * window.innerHeight);
    },
    reset,
  }));

  useEffect(() => {
    const onResize = (): void => place(centre.current.x, centre.current.y);
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
    // `place` closes over refs and the diameter, which is the one real dependency.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [diameter]);

  useEffect(() => {
    let since = READING_INTERVAL_MS;
    return ticker.subscribe((dtMs) => {
      since += dtMs;
      if (since < READING_INTERVAL_MS) return;
      since = 0;
      const current = centre.current;
      const width = window.innerWidth;
      const height = window.innerHeight;
      const u = current.x / width;
      const v = 1 - current.y / height;
      const layer = layerById(layerRef.current);
      const sample = sampleField(layer, u, v, width / height, fieldTime(clock));
      const reading = layer.reading(sample.speed);
      if (valueRef.current !== null) valueRef.current.textContent = reading.toFixed(layer.decimals);
      if (bearingRef.current !== null) {
        bearingRef.current.textContent = layer.vector ? formatBearing(sample.bearing) : "";
      }
      if (positionRef.current !== null) {
        const lat = REGION.south + v * (REGION.north - REGION.south);
        const lon = REGION.west + u * (REGION.east - REGION.west);
        positionRef.current.textContent = `${formatLat(lat)} ${formatLon(lon)}`;
      }
    });
  }, [ticker, clock]);

  const dragging = useRef<{ readonly dx: number; readonly dy: number } | null>(null);

  const layer = layerById(props.layer);
  const initial = centre.current;

  return (
    <GlassGroup id="probe" backdrop={{ kind: "texture", id: FIELD_TEXTURE_ID }}>
      {/*
        `circular`, because the default continuous profile clamps a radius so its
        longer curve fits the box, and a disc is the one shape where that clamp
        turns a circle into a rounded square.
      */}
      <GlassSurface asChild profile="circular" radius={diameter / 2} thickness={26} interactive>
        <button
          ref={hostRef}
          type="button"
          className="probe"
          style={{
            width: diameter,
            height: diameter,
            left: initial.x - diameter / 2,
            top: initial.y - diameter / 2,
          }}
          aria-label={`Field probe. Drag it, or move it with the arrow keys, to read the ${layer.quantity.toLowerCase()} at a point.`}
          hidden={props.hidden}
          onPointerDown={(event) => {
            const current = centre.current;
            event.currentTarget.setPointerCapture(event.pointerId);
            dragging.current = { dx: current.x - event.clientX, dy: current.y - event.clientY };
          }}
          onPointerMove={(event) => {
            const drag = dragging.current;
            if (drag === null) return;
            place(event.clientX + drag.dx, event.clientY + drag.dy);
          }}
          onPointerUp={() => {
            dragging.current = null;
          }}
          onPointerCancel={() => {
            dragging.current = null;
          }}
          onKeyDown={(event) => {
            const current = centre.current;
            const step = event.shiftKey ? KEY_STEP_LARGE : KEY_STEP;
            const moves: Record<string, readonly [number, number]> = {
              ArrowLeft: [-step, 0],
              ArrowRight: [step, 0],
              ArrowUp: [0, -step],
              ArrowDown: [0, step],
            };
            const move = moves[event.key];
            if (move === undefined) return;
            event.preventDefault();
            place(current.x + move[0], current.y + move[1]);
          }}
        >
          <span className="probe__quantity">{layer.quantity}</span>
          <span className="probe__reading">
            <span className="probe__value" ref={valueRef}>
              {layer.min.toFixed(layer.decimals)}
            </span>
            <span className="probe__unit">{layer.unit}</span>
          </span>
          <span className="probe__meta">
            <span className="probe__bearing" ref={bearingRef} />
            <span className="probe__position" ref={positionRef} />
          </span>
        </button>
      </GlassSurface>
    </GlassGroup>
  );
}
