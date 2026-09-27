/**
 * The environment: the painting the viewing room stands in, painted into one canvas.
 *
 * The canvas is the page's texture source (`environment`) and the thing the visitor sees, so
 * paint and sample are the same pixels by construction: it is painted at its own box's size in
 * device pixels, which is the cookbook's exact case (the renderer fits the whole texture to the
 * element's box, stretched, so any other size would make the lens reveal a different picture from
 * the one on screen).
 *
 * It paints three things, in order:
 *
 * 1. the current work, cover-fit, cropped vertically at the work's own focus (every work is
 *    landscape, so the cover fit only ever trims top and bottom at a desktop aspect);
 * 2. during a change of work, the next work over it at the dissolve's weight;
 * 3. the reading wash: a grade painted ONLY under the glass footprints, strongest behind the text
 *    and falling off toward the rim, so the painting is untouched wherever it is seen directly and
 *    the rim still has the painting's structure to bend.
 *
 * The wash is solved, not chosen per painting. Under each footprint the painting's own mean
 * encoded luma is read first; the wash is then just strong enough to bring that mean to the
 * scheme's target for that kind of surface (`TARGET`), never weaker than `FLOOR` (the area behind
 * text is always a little calmer than the rim) and never stronger than `CEILING` (the field under
 * the glass never goes flat). The targets are the part fitted on rendered pixels: they are the
 * painted levels at which the drawn window and ornament bodies measured clear of the published
 * ink's dead band with margin, in both poses (DESIGN.md, part two). Because the solve runs on
 * whatever is painted, it holds through a dissolve and at any viewport, not only at the eight
 * works at one size.
 *
 * And it measures what it painted. Each glass group's declared backdrop is the encoded Rec709 luma
 * averaged over that group's own rounded footprint and decoded once, which is the statistic the
 * runtime's own silhouette reading takes, read from a quarter-scale copy painted by the same code
 * at the same moment. The window covers a graded part of the plane, so the whole source's average,
 * which a texture group would otherwise use for its tone, is not the level under it.
 */

import type { BackdropHint } from "@vitreajs/vitrea-react";

import type { Work } from "./works";

export type Scheme = "light" | "dark";
export type SurfaceKind = "window" | "ornament";

/** A glass host's box in viewport CSS px, with its corner radius. */
export interface Footprint {
  readonly kind: SurfaceKind;
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly radius: number;
  /** The inset from the edge over which the wash rises from its rim value to its full value. */
  readonly feather: number;
}

/** A group's measurement: the declared hint and the numbers behind it, for the record. */
export interface FootprintReading {
  readonly hint: BackdropHint;
  /** Mean encoded Rec709 luma under the footprint as painted (washed), 0..1. */
  readonly encodedMean: number;
  /** Encoded luma standard deviation under the footprint as painted. */
  readonly encodedDeviation: number;
  /** The painting's own mean under the footprint before the wash. */
  readonly sourceUnder: number;
  /** The wash strength the solve chose. */
  readonly wash: number;
}

/** The colours the painting is graded toward under the glass: label-card white, evening. */
const WASH_COLOR: Record<Scheme, readonly [number, number, number]> = {
  light: [247, 243, 235],
  dark: [14, 17, 21],
};

/**
 * The painted mean (encoded luma) the wash brings each footprint to: at least this in the light
 * scheme, at most this in the dark. Fitted on rendered pixels; see DESIGN.md part two.
 */
const TARGET: Record<Scheme, Record<SurfaceKind, number>> = {
  light: { window: 0.5, ornament: 0.5 },
  dark: { window: 0.2, ornament: 0.16 },
};
const FLOOR = 0.12;
const CEILING = 0.82;
/** The wash at the footprint's outer edge, as a fraction of its full strength. */
const RIM = 0.35;

/** The cover-fit placement of a work in a viewport, in CSS px. */
export interface Placement {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export function placementFor(work: Work, viewport: { width: number; height: number }): Placement {
  const [iw, ih] = work.imageSize;
  const scale = Math.max(viewport.width / iw, viewport.height / ih);
  const width = iw * scale;
  const height = ih * scale;
  return {
    x: (viewport.width - width) / 2,
    y: (viewport.height - height) * work.focusY,
    width,
    height,
  };
}

/** The part of the work the viewport shows, as fractions of the image. */
export function visibleDetail(
  work: Work,
  viewport: { width: number; height: number },
): { x: number; y: number; width: number; height: number } {
  const p = placementFor(work, viewport);
  return {
    x: -p.x / p.width,
    y: -p.y / p.height,
    width: viewport.width / p.width,
    height: viewport.height / p.height,
  };
}

const ANALYSIS_SCALE = 0.25;

const srgbDecode = (value: number): number =>
  value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;

export interface EnvironmentState {
  readonly from: Work;
  /** The work being dissolved to, or none. */
  readonly to: Work | undefined;
  /** The dissolve's weight on `to`, 0..1. */
  readonly mix: number;
  readonly scheme: Scheme;
  readonly footprints: Readonly<Record<string, Footprint>>;
}

interface Stats {
  readonly mean: number;
  readonly deviation: number;
}

/** The strength that brings a footprint's painted mean to its target, within floor and ceiling. */
function solveWash(scheme: Scheme, kind: SurfaceKind, mean: number): number {
  const target = TARGET[scheme][kind];
  const color = WASH_COLOR[scheme];
  const washLuma = (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255;
  // The wash is a source-over mix toward one colour, and luma is linear in encoded RGB, so the
  // painted mean moves exactly linearly with strength: mean + s (washLuma - mean).
  const needed = scheme === "light"
    ? (target - mean) / (washLuma - mean)
    : (mean - target) / (mean - washLuma);
  const cumulative = Math.min(CEILING, Math.max(FLOOR, Number.isFinite(needed) ? needed : 0));
  return cumulative;
}

/**
 * Owns the two canvases and the decoded images. Stateless about the page: it paints and measures
 * whatever state it is handed, synchronously, so `setPhase` can show a work within the frame.
 */
export class EnvironmentPainter {
  readonly canvas: HTMLCanvasElement;
  private readonly analysis: HTMLCanvasElement;
  private readonly images = new Map<string, HTMLImageElement>();
  private readonly pending = new Map<string, Promise<HTMLImageElement>>();
  private last: { readings: Record<string, FootprintReading>; source: number } | undefined;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.analysis = document.createElement("canvas");
  }

  /** Start decoding a work's image; resolves when it can be drawn. */
  load(work: Work): Promise<HTMLImageElement> {
    const ready = this.images.get(work.id);
    if (ready !== undefined) return Promise.resolve(ready);
    const inFlight = this.pending.get(work.id);
    if (inFlight !== undefined) return inFlight;
    const image = new Image();
    image.decoding = "async";
    image.src = work.image;
    const promise = image
      .decode()
      .then(() => {
        this.images.set(work.id, image);
        return image;
      })
      .finally(() => this.pending.delete(work.id));
    this.pending.set(work.id, promise);
    return promise;
  }

  isLoaded(work: Work): boolean {
    return this.images.has(work.id);
  }

  /**
   * Paint both canvases for `state` and measure what was painted. Returns undefined when the base
   * work has not decoded yet.
   */
  paint(
    state: EnvironmentState,
  ): { readings: Record<string, FootprintReading>; source: number } | undefined {
    const base = this.images.get(state.from.id);
    if (base === undefined) return undefined;
    const viewport = { width: window.innerWidth, height: window.innerHeight };
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.round(viewport.width * dpr);
    const height = Math.round(viewport.height * dpr);
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
    const aw = Math.max(1, Math.round(viewport.width * ANALYSIS_SCALE));
    const ah = Math.max(1, Math.round(viewport.height * ANALYSIS_SCALE));
    if (this.analysis.width !== aw || this.analysis.height !== ah) {
      this.analysis.width = aw;
      this.analysis.height = ah;
    }
    const display = this.canvas.getContext("2d");
    const analysis = this.analysis.getContext("2d", { willReadFrequently: true });
    if (display === null || analysis === null) return undefined;

    const next = state.to === undefined ? undefined : this.images.get(state.to.id);
    const layers = (context: CanvasRenderingContext2D, scale: number): void => {
      context.setTransform(scale, 0, 0, scale, 0, 0);
      context.globalAlpha = 1;
      context.imageSmoothingEnabled = true;
      context.imageSmoothingQuality = "high";
      context.fillStyle = "#000";
      context.fillRect(0, 0, viewport.width, viewport.height);
      const draw = (work: Work, image: HTMLImageElement, alpha: number): void => {
        const p = placementFor(work, viewport);
        context.globalAlpha = alpha;
        context.drawImage(image, p.x, p.y, p.width, p.height);
      };
      draw(state.from, base, 1);
      if (state.to !== undefined && next !== undefined && state.mix > 0) {
        draw(state.to, next, state.mix);
      }
      context.globalAlpha = 1;
    };
    layers(display, dpr);
    layers(analysis, ANALYSIS_SCALE);

    // Read the painting under each footprint, solve its wash, and paint the wash on both.
    const strengths: Record<string, number> = {};
    const before: Record<string, Stats> = {};
    for (const [id, footprint] of Object.entries(state.footprints)) {
      const stats = footprintStats(analysis, footprint, this.analysis);
      if (stats === undefined) continue;
      before[id] = stats;
      strengths[id] = solveWash(state.scheme, footprint.kind, stats.mean);
    }
    const color = WASH_COLOR[state.scheme];
    for (const [id, footprint] of Object.entries(state.footprints)) {
      const strength = strengths[id];
      if (strength === undefined) continue;
      paintWash(display, dpr, footprint, color, strength);
      paintWash(analysis, ANALYSIS_SCALE, footprint, color, strength);
    }

    const readings: Record<string, FootprintReading> = {};
    for (const [id, footprint] of Object.entries(state.footprints)) {
      const stats = footprintStats(analysis, footprint, this.analysis);
      const source = before[id];
      if (stats === undefined || source === undefined) continue;
      // No `complexity`: the runtime consumes none, and a busyness number would have to be
      // invented on a scale nothing defines. The deviation is kept for the record instead.
      readings[id] = {
        hint: {
          tone: stats.mean >= 0.5 ? "light" : "dark",
          luminance: Math.round(srgbDecode(stats.mean) * 1000) / 1000,
        },
        encodedMean: stats.mean,
        encodedDeviation: stats.deviation,
        sourceUnder: source.mean,
        wash: strengths[id] ?? 0,
      };
    }
    const whole = footprintStats(
      analysis,
      {
        kind: "window",
        x: 0,
        y: 0,
        width: viewport.width,
        height: viewport.height,
        radius: 0,
        feather: 0,
      },
      this.analysis,
    );
    this.last = { readings, source: whole?.mean ?? 0 };
    return this.last;
  }

  /** The last measurement, for the record's instrument. */
  lastReadings(): { readings: Record<string, FootprintReading>; source: number } | undefined {
    return this.last;
  }
}

/**
 * The wash as nested rounded rectangles, each a thin layer, so the cumulative strength rises from
 * `RIM × strength` at the footprint's edge to `strength` at `feather` inward. Source-over layers
 * compose multiplicatively, so each ring's own alpha is solved from the cumulative target.
 */
function paintWash(
  context: CanvasRenderingContext2D,
  scale: number,
  footprint: Footprint,
  color: readonly [number, number, number],
  strength: number,
): void {
  if (strength <= 0) return;
  context.setTransform(scale, 0, 0, scale, 0, 0);
  const rings = 12;
  context.fillStyle = `rgb(${color[0]} ${color[1]} ${color[2]})`;
  let previous = 0;
  for (let i = 0; i < rings; i += 1) {
    const u = i / (rings - 1);
    const eased = u * u * (3 - 2 * u);
    const cumulative = strength * (RIM + (1 - RIM) * eased);
    const layer = previous >= 1 ? 0 : 1 - (1 - cumulative) / (1 - previous);
    previous = cumulative;
    if (layer <= 0) continue;
    const inset = footprint.feather * u;
    const width = footprint.width - inset * 2;
    const height = footprint.height - inset * 2;
    if (width <= 0 || height <= 0) break;
    const radius = Math.max(0, Math.min(footprint.radius - inset, width / 2, height / 2));
    context.globalAlpha = layer;
    context.beginPath();
    context.roundRect(footprint.x + inset, footprint.y + inset, width, height, radius);
    context.fill();
  }
  context.globalAlpha = 1;
}

function insideRoundedRect(px: number, py: number, f: Footprint): boolean {
  const cx = f.x + f.width / 2;
  const cy = f.y + f.height / 2;
  const radius = Math.min(f.radius, f.width / 2, f.height / 2);
  const qx = Math.abs(px - cx) - f.width / 2 + radius;
  const qy = Math.abs(py - cy) - f.height / 2 + radius;
  const distance =
    Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius;
  return distance <= 0;
}

/** Encoded Rec709 luma mean and deviation over a footprint's own rounded box. */
function footprintStats(
  context: CanvasRenderingContext2D,
  footprint: Footprint,
  canvas: HTMLCanvasElement,
): Stats | undefined {
  const s = ANALYSIS_SCALE;
  const x0 = Math.max(0, Math.floor(footprint.x * s));
  const y0 = Math.max(0, Math.floor(footprint.y * s));
  const x1 = Math.min(canvas.width, Math.ceil((footprint.x + footprint.width) * s));
  const y1 = Math.min(canvas.height, Math.ceil((footprint.y + footprint.height) * s));
  if (x1 <= x0 || y1 <= y0) return undefined;
  const data = context.getImageData(x0, y0, x1 - x0, y1 - y0).data;
  let sum = 0;
  let squares = 0;
  let count = 0;
  for (let y = y0; y < y1; y += 1) {
    for (let x = x0; x < x1; x += 1) {
      // Pixel centres, back in CSS px, tested against the host's own rounded box.
      if (!insideRoundedRect((x + 0.5) / s, (y + 0.5) / s, footprint)) continue;
      const i = ((y - y0) * (x1 - x0) + (x - x0)) * 4;
      const luma =
        (0.2126 * (data[i] ?? 0) + 0.7152 * (data[i + 1] ?? 0) + 0.0722 * (data[i + 2] ?? 0)) /
        255;
      sum += luma;
      squares += luma * luma;
      count += 1;
    }
  }
  if (count === 0) return undefined;
  const mean = sum / count;
  return { mean, deviation: Math.sqrt(Math.max(0, squares / count - mean * mean)) };
}
