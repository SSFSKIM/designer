/**
 * The environment: the basin's relief map in one viewport-fixed canvas that the runtime samples
 * as its texture, the Clear profile's dimming layer painted into it under every footprint, and
 * the measurement of what each glass group is actually over.
 *
 * Three quantities stay apart (the materialist skill, spatial condition 1): the SOURCE is the map
 * as painted; the TONE INPUT each group declares is the level measured under its own box from a
 * quarter-scale copy of the composite, dimming included; and the DRAWN level behind a line of
 * text is neither, and is the audit's to read. The map itself is painted once per viewport and
 * scheme into a base canvas; what moves — the window and the layer under it — is composed over a
 * copy of that base, from the runtime's own frame loop.
 */

import { useGlassRoot, type BackdropHint } from "@vitreajs/vitrea-react";
import { useEffect, useLayoutEffect, useRef, type ReactNode } from "react";

import { loadRelief, paintRelief, reliefView, type Relief } from "./relief";
import { dimmingFor, ENVIRONMENT_ID, featherFor, type HostShape } from "./shared";
import type { GlassKind, Scheme } from "./shell/types";

/** How often the footprints are re-measured while something moves, ms. */
const MEASURE_EVERY_MS = 120;
const MEASURE_SCALE = 1 / 4;

export interface Level {
  /** The per-channel encoded mean, as luma. */
  readonly encoded: number;
  /** Relative (linear) luminance of the encoded mean, decoded once: the runtime's statistic. */
  readonly luminance: number;
}

export interface FootprintReading {
  readonly hint: BackdropHint;
  /** The dimming strength painted under this footprint, 0 where none is. */
  readonly strength: number;
  readonly raw: Level;
  readonly composite: Level;
}

export interface EnvironmentProps {
  readonly viewport: { readonly width: number; readonly height: number };
  readonly scheme: Scheme;
  readonly glass: GlassKind;
  /** Where Lake Tahoe's middle is placed: the window's first position. */
  readonly focus: { readonly x: number; readonly y: number };
  readonly shapes: readonly HostShape[];
  readonly onReadings: (readings: Readonly<Record<string, FootprintReading>>) => void;
  /** The first frame is painted and supplied, so the glass may materialise over it. */
  readonly onReady: () => void;
}

export function EnvironmentCanvas(props: EnvironmentProps): ReactNode {
  const root = useGlassRoot();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const latest = useRef(props);
  latest.current = props;
  const relief = useRef<Relief | null>(null);
  const base = useRef<{ canvas: HTMLCanvasElement; small: ImageData; key: string } | null>(null);
  /** The composite needs painting again: something it is drawn from changed. */
  const dirty = useRef(true);
  /** The footprints' readings are out of date: something they are read from changed. */
  const stale = useRef(true);
  const sinceMeasure = useRef(Infinity);
  const ready = useRef(false);
  const lastReadings = useRef<Record<string, FootprintReading>>({});

  useEffect(() => {
    let live = true;
    void loadRelief().then(
      (loaded) => {
        if (!live) return;
        relief.current = loaded;
        dirty.current = true;
      },
      (error: unknown) => console.error(error),
    );
    return () => {
      live = false;
    };
  }, []);

  // The canvas is the texture, supplied once its first frame is painted (an unpainted canvas has
  // no pixels to import) and re-imported by the runtime every frame it samples after that. When
  // it is withdrawn — the root rebuilt, or this component re-mounted by Fast Refresh — the next
  // painted frame supplies it again, to whichever root is there then.
  useEffect(() => {
    if (root === null) return;
    return () => {
      root.setBackdropTexture(ENVIRONMENT_ID, undefined);
      ready.current = false;
      dirty.current = true;
    };
  }, [root]);

  useLayoutEffect(() => {
    dirty.current = true;
    stale.current = true;
  }, [props.viewport, props.scheme, props.glass, props.focus, props.shapes]);

  // One pass per frame from the runtime's own loop. At rest it returns before reading anything:
  // the composite is painted when something it is drawn from changed, which during a drag is
  // every frame, and the footprints are read at most once per `MEASURE_EVERY_MS` while they keep
  // changing, with one more reading after the last change so the final place is always measured.
  useEffect(() => {
    if (root === null) return;
    return root.subscribe(({ deltaMs }) => {
      sinceMeasure.current += deltaMs;
      const canvas = canvasRef.current;
      const data = relief.current;
      if (canvas === null || data === null) return;
      const measure = stale.current && sinceMeasure.current >= MEASURE_EVERY_MS;
      if (!dirty.current && !measure) return;
      const { viewport, scheme, glass, focus, shapes } = latest.current;
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      const width = Math.round(viewport.width * dpr);
      const height = Math.round(viewport.height * dpr);
      const view = reliefView(viewport, focus);
      const baseKey = `${String(width)}×${String(height)}|${scheme}|${String(view.x)},${String(view.y)}`;
      if (base.current?.key !== baseKey) base.current = paintBase(data, view, scheme, dpr, width, height, baseKey);
      const painted = base.current;

      // Strengths come from the base's quarter-scale copy, so the layer can follow a drag every
      // frame without reading pixels back from the canvas it is painting.
      const strengths = new Map<string, number>();
      const raw = new Map<string, Level>();
      for (const shape of shapes) {
        const level = levelUnder(painted.small, shape, dpr);
        raw.set(shape.id, level);
        strengths.set(shape.id, glass === "clear" ? dimmingFor(scheme, level.encoded, shape.id !== "terminal") : 0);
      }

      if (dirty.current) {
        if (canvas.width !== width || canvas.height !== height) {
          canvas.width = width;
          canvas.height = height;
        }
        const ctx = canvas.getContext("2d");
        if (ctx === null) return;
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.drawImage(painted.canvas, 0, 0);
        paintDimming(ctx, shapes, strengths, scheme, dpr);
        dirty.current = false;
        if (!ready.current) {
          ready.current = true;
          root.setBackdropTexture(ENVIRONMENT_ID, { kind: "canvas", canvas });
          latest.current.onReady();
        }
      }

      if (!measure) return;
      sinceMeasure.current = 0;
      stale.current = false;
      const composite = compositeSmall(painted, shapes, strengths, scheme, dpr);
      const readings: Record<string, FootprintReading> = {};
      let changed = Object.keys(lastReadings.current).length !== shapes.length;
      for (const shape of shapes) {
        const c = levelUnder(composite, shape, dpr);
        const reading: FootprintReading = {
          hint: hintFrom(c),
          strength: strengths.get(shape.id) ?? 0,
          raw: raw.get(shape.id) as Level,
          composite: c,
        };
        readings[shape.id] = reading;
        const was = lastReadings.current[shape.id];
        if (
          was === undefined ||
          Math.abs((was.hint.luminance ?? 0) - (reading.hint.luminance ?? 0)) > 0.002 ||
          was.hint.tone !== reading.hint.tone ||
          Math.abs(was.strength - reading.strength) > 0.01
        ) {
          changed = true;
        }
      }
      if (changed) {
        lastReadings.current = readings;
        latest.current.onReadings(readings);
      }
    });
  }, [root]);

  // The element is sized to the viewport the painter paints (`innerWidth` × `innerHeight`), never
  // to `100vh`, which on a mobile browser is the viewport with its toolbar retracted and would
  // stretch the map the glass samples away from the map on the screen.
  return (
    <canvas
      ref={canvasRef}
      className="relief"
      style={{ width: props.viewport.width, height: props.viewport.height }}
      role="img"
      aria-label="A relief map of the Lake Tahoe basin: the lake at 1,898 metres, the Sierra Nevada to the west and the Carson Range to the east, with contours every 50 metres."
    />
  );
}

function paintBase(relief: Relief, view: ReturnType<typeof reliefView>, scheme: Scheme, dpr: number, width: number, height: number, key: string) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (ctx === null) throw new Error("The relief map needs a 2D canvas.");
  paintRelief(ctx, relief, view, scheme, dpr);
  const small = shrink(canvas, width, height);
  return { canvas, small, key };
}

function shrink(source: HTMLCanvasElement, width: number, height: number): ImageData {
  const w = Math.max(1, Math.round(width * MEASURE_SCALE));
  const h = Math.max(1, Math.round(height * MEASURE_SCALE));
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (ctx === null) throw new Error("The relief map needs a 2D canvas.");
  ctx.imageSmoothingQuality = "high";
  ctx.drawImage(source, 0, 0, w, h);
  return ctx.getImageData(0, 0, w, h);
}

/** The same layer at a quarter of the scale, for the composite's reading. */
function compositeSmall(painted: { small: ImageData }, shapes: readonly HostShape[], strengths: ReadonlyMap<string, number>, scheme: Scheme, dpr: number): ImageData {
  const { width, height } = painted.small;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (ctx === null) throw new Error("The relief map needs a 2D canvas.");
  ctx.putImageData(painted.small, 0, 0);
  paintDimming(ctx, shapes, strengths, scheme, dpr * MEASURE_SCALE);
  return ctx.getImageData(0, 0, width, height);
}

/**
 * The layer: under each footprint a rounded rectangle of black (Dark) or white (Light) at the
 * footprint's strength, ramping from nothing at the edge to full strength a feather inside it —
 * an inset shape blurred by half the feather, so it never spills outside the glass.
 */
function paintDimming(ctx: CanvasRenderingContext2D, shapes: readonly HostShape[], strengths: ReadonlyMap<string, number>, scheme: Scheme, scale: number): void {
  const colour = scheme === "dark" ? "0 0 0" : "255 255 255";
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  for (const shape of shapes) {
    const strength = strengths.get(shape.id) ?? 0;
    if (strength <= 0) continue;
    const feather = featherFor(Math.min(shape.box.width, shape.box.height));
    const inset = feather / 2;
    const { x, y, width, height } = shape.box;
    ctx.filter = `blur(${String((feather / 4) * scale)}px)`;
    ctx.fillStyle = `rgb(${colour} / ${String(strength)})`;
    ctx.beginPath();
    ctx.roundRect((x + inset) * scale, (y + inset) * scale, (width - 2 * inset) * scale, (height - 2 * inset) * scale, Math.max(0, shape.radius - inset) * scale);
    ctx.fill();
  }
  ctx.restore();
}

/** The level under a footprint, from a quarter-scale image of the viewport. */
function levelUnder(image: ImageData, shape: HostShape, dpr: number): Level {
  const k = dpr * MEASURE_SCALE;
  const x0 = Math.max(0, Math.floor(shape.box.x * k));
  const y0 = Math.max(0, Math.floor(shape.box.y * k));
  const x1 = Math.min(image.width, Math.ceil((shape.box.x + shape.box.width) * k));
  const y1 = Math.min(image.height, Math.ceil((shape.box.y + shape.box.height) * k));
  let r = 0;
  let g = 0;
  let b = 0;
  let n = 0;
  for (let y = y0; y < y1; y++) {
    for (let x = x0; x < x1; x++) {
      const o = (y * image.width + x) * 4;
      r += image.data[o] as number;
      g += image.data[o + 1] as number;
      b += image.data[o + 2] as number;
      n++;
    }
  }
  if (n === 0) return { encoded: 0, luminance: 0 };
  const [er, eg, eb] = [r / n / 255, g / n / 255, b / n / 255];
  return {
    encoded: 0.2126 * er + 0.7152 * eg + 0.0722 * eb,
    luminance: 0.2126 * decode(er) + 0.7152 * decode(eg) + 0.0722 * decode(eb),
  };
}

function decode(e: number): number {
  return e <= 0.04045 ? e / 12.92 : Math.pow((e + 0.055) / 1.055, 2.4);
}

/** The declaration a group makes from its footprint: the measured level, and the pole it is on. */
export function hintFrom(level: Level): BackdropHint {
  return { tone: level.luminance >= 0.18 ? "light" : "dark", luminance: Math.round(level.luminance * 1000) / 1000 };
}
