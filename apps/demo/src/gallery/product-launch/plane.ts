/**
 * The live plane: one viewport-fixed canvas that paints the current photograph cover-fit, and the
 * arithmetic that says what any rectangle of it holds.
 *
 * The canvas is painted at its own box's size, so what the page shows and what the texture holds
 * are the same pixels at the same aspect, which is the one arrangement vitrea's texture path maps
 * exactly (`vitrea.md` §2: an in-document canvas is measured every read phase and the whole
 * texture is fitted to its box). A state change cross-dissolves the old photograph into the new
 * one; the dissolve is a content state, not glass motion, and it steps under Reduce Motion.
 *
 * The same geometry answers the CSS tier's question. That tier has no pixels, so each group
 * declares what it stands on, and the declaration describes the frame the canvas holds NOW: the
 * painter reports what it last painted (which photograph, which one dissolving out beneath it, at
 * what alpha, under what dim), and `measurePainted` recomposes exactly that over the rectangle a
 * group's host occupies, from a small sRGB grid of each photograph. Mid-dissolve that is the blend
 * of two photographs, not the one arriving. One function paints, one measures, both call `coverOf`.
 */

import type { BackdropHint } from "@vitreajs/vitrea-react";

import { PHOTOS, type PhotoId } from "./content";

export interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

interface Cover {
  readonly scale: number;
  readonly dx: number;
  readonly dy: number;
}

/** CSS `object-fit: cover` and `object-position: focus`, `zoom` times closer, in the box's px. */
function coverOf(
  imageWidth: number,
  imageHeight: number,
  boxWidth: number,
  boxHeight: number,
  focus: readonly [number, number],
  zoom = 1,
): Cover {
  const scale = Math.max(boxWidth / imageWidth, boxHeight / imageHeight) * zoom;
  return {
    scale,
    dx: (boxWidth - imageWidth * scale) * focus[0],
    dy: (boxHeight - imageHeight * scale) * focus[1],
  };
}

const coverFor = (photo: LoadedPhoto, width: number, height: number): Cover =>
  coverOf(
    photo.image.naturalWidth,
    photo.image.naturalHeight,
    width,
    height,
    PHOTOS[photo.id].focus,
    PHOTOS[photo.id].zoom,
  );

const srgbToLinear = (c: number): number =>
  c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;

/**
 * A photograph's encoded sRGB, sampled onto a grid about 200 cells wide. Encoded rather than
 * linear because the canvas composites in encoded values: the dissolve's alpha and the dark dim are
 * both applied there, so recomposing a painted frame has to happen there too.
 */
interface ColourGrid {
  readonly width: number;
  readonly height: number;
  /** Three values per cell, 0..1. */
  readonly rgb: Float32Array;
}

const GRID_WIDTH = 200;

function gridOf(image: HTMLImageElement): ColourGrid {
  const width = GRID_WIDTH;
  const height = Math.max(1, Math.round((GRID_WIDTH * image.naturalHeight) / image.naturalWidth));
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d", { willReadFrequently: true });
  const rgb = new Float32Array(width * height * 3);
  if (context === null) return { width, height, rgb };
  context.drawImage(image, 0, 0, width, height);
  const data = context.getImageData(0, 0, width, height).data;
  for (let i = 0; i < width * height; i += 1) {
    rgb[i * 3] = (data[i * 4] ?? 0) / 255;
    rgb[i * 3 + 1] = (data[i * 4 + 1] ?? 0) / 255;
    rgb[i * 3 + 2] = (data[i * 4 + 2] ?? 0) / 255;
  }
  return { width, height, rgb };
}

export interface LoadedPhoto {
  readonly id: PhotoId;
  readonly image: HTMLImageElement;
  readonly grid: ColourGrid;
}

/** Decode one photograph and take its grid. Same-origin, so the read cannot taint. */
export async function loadPhoto(id: PhotoId): Promise<LoadedPhoto> {
  const image = new Image();
  image.decoding = "async";
  image.src = PHOTOS[id].src;
  await image.decode();
  return { id, image, grid: gridOf(image) };
}

/** What the canvas holds after its last paint. */
export interface PaintedFrame {
  readonly current: PhotoId;
  /** The photograph dissolving out beneath `current`; absent once the dissolve has finished. */
  readonly previous: PhotoId | undefined;
  /** The alpha `current` was painted at over `previous`: 1 at rest. */
  readonly mix: number;
  /** The dark appearance's dim, painted over both. */
  readonly dim: number;
}

/** One sample every this many CSS px across a box: about half a grid cell at 1440 wide. */
const SAMPLE_STEP = 4;

/**
 * Mean and spread of relative luminance over a viewport rectangle of the frame the canvas holds,
 * recomposed the way the canvas composed it: `previous`, then `current` at `mix` over it, then the
 * dim, all in encoded sRGB, and only then linearised. Undefined until the photographs are decoded.
 */
export function measurePainted(
  photos: ReadonlyMap<PhotoId, LoadedPhoto>,
  frame: PaintedFrame,
  viewport: { readonly width: number; readonly height: number },
  rect: Box,
): { readonly mean: number; readonly spread: number } | undefined {
  const top = photos.get(frame.current);
  const under = frame.previous === undefined ? undefined : photos.get(frame.previous);
  if (top === undefined || (frame.previous !== undefined && under === undefined)) return undefined;
  const cellOf = (photo: LoadedPhoto): ((x: number, y: number) => number) => {
    const cover = coverFor(photo, viewport.width, viewport.height);
    const { grid, image } = photo;
    const toGrid = grid.width / image.naturalWidth;
    const clamp = (value: number, cells: number): number =>
      Math.min(cells - 1, Math.max(0, Math.floor(value * toGrid)));
    return (x, y) => {
      const gx = clamp((x - cover.dx) / cover.scale, grid.width);
      const gy = clamp((y - cover.dy) / cover.scale, grid.height);
      return (gy * grid.width + gx) * 3;
    };
  };
  const topCell = cellOf(top);
  const underCell = under === undefined ? undefined : cellOf(under);
  const keep = 1 - frame.dim;
  let sum = 0;
  let sumSq = 0;
  let n = 0;
  for (let y = rect.y + SAMPLE_STEP / 2; y < rect.y + rect.height; y += SAMPLE_STEP) {
    for (let x = rect.x + SAMPLE_STEP / 2; x < rect.x + rect.width; x += SAMPLE_STEP) {
      const t = topCell(x, y);
      let r = top.grid.rgb[t] ?? 0;
      let g = top.grid.rgb[t + 1] ?? 0;
      let b = top.grid.rgb[t + 2] ?? 0;
      if (under !== undefined && underCell !== undefined) {
        const u = underCell(x, y);
        r = (under.grid.rgb[u] ?? 0) * (1 - frame.mix) + r * frame.mix;
        g = (under.grid.rgb[u + 1] ?? 0) * (1 - frame.mix) + g * frame.mix;
        b = (under.grid.rgb[u + 2] ?? 0) * (1 - frame.mix) + b * frame.mix;
      }
      const v =
        0.2126 * srgbToLinear(r * keep) +
        0.7152 * srgbToLinear(g * keep) +
        0.0722 * srgbToLinear(b * keep);
      sum += v;
      sumSq += v * v;
      n += 1;
    }
  }
  if (n === 0) return undefined;
  const mean = sum / n;
  return { mean, spread: Math.sqrt(Math.max(0, sumSq / n - mean * mean)) };
}

/**
 * The declaration a group makes on the CSS tier: the measured mean as the luminance, the tone
 * classified at the middle grey that separates the two inks (encoded 0.46, linear 0.18), and the
 * spread as the complexity. `mixed` is never declared: the runtime's ink reads a luminance only
 * for `light` or `dark`, and a measured number is more honest than a third bucket.
 */
export function hintOf(measured: { readonly mean: number; readonly spread: number }): BackdropHint {
  const round = (value: number): number => Math.round(value * 1000) / 1000;
  return {
    tone: measured.mean >= 0.18 ? "light" : "dark",
    luminance: round(measured.mean),
    complexity: round(Math.min(1, measured.spread * 4)),
  };
}

const DISSOLVE_MS = 480;

/**
 * The dark appearance dims the plane, the way iOS dims the wallpaper under Dark Mode, and for the
 * reason the measurement gave: under the dark material a mid-level photograph (the deck boards, the
 * satin nickel) lands the glass at a relative luminance of 0.19 to 0.29, the band where neither
 * the dark nor the light ink reaches 4.5:1 (measured 2.5 to 4.7 before this). Painted into the
 * canvas, so the texture the glass reads and the photograph the reader sees are the same dimmed
 * pixels; a scrim laid over the plane in CSS would not be behind the glass at all.
 */
export const DARK_PLANE_DIM = 0.4;

export interface PlanePainter {
  /** Show a photograph; dissolves from the current one unless `instant`. */
  show(id: PhotoId, instant: boolean): void;
  /** How far the dark appearance dims the plane, 0..1 (see `DARK_PLANE_DIM`). */
  setDim(dim: number): void;
  /** Advance the dissolve by one frame of the root's ticker. Returns whether it painted. */
  tick(dtMs: number): boolean;
  /** Re-size the backing store to the box and repaint. */
  resize(): void;
  /** What the canvas holds after the last paint, for `measurePainted`. */
  painted(): PaintedFrame;
  readonly current: PhotoId;
}

export function createPlanePainter(
  canvas: HTMLCanvasElement,
  photos: ReadonlyMap<PhotoId, LoadedPhoto>,
  initial: PhotoId,
  initialDim: number,
): PlanePainter {
  const context = canvas.getContext("2d");
  let dim = initialDim;
  let current: PhotoId = initial;
  let previous: PhotoId | undefined;
  let elapsed = DISSOLVE_MS;
  let cssWidth = 0;
  let cssHeight = 0;
  let dpr = 1;

  const draw = (id: PhotoId, alpha: number): void => {
    const photo = photos.get(id);
    if (context === null || photo === undefined) return;
    const { image } = photo;
    const cover = coverFor(photo, cssWidth, cssHeight);
    context.globalAlpha = alpha;
    context.drawImage(
      image,
      cover.dx,
      cover.dy,
      image.naturalWidth * cover.scale,
      image.naturalHeight * cover.scale,
    );
  };

  // Smoothstep: the dissolve has no overshoot and no linear start, the character of a critically
  // damped optical change rather than a tween.
  const mix = (): number => {
    const t = Math.min(1, elapsed / DISSOLVE_MS);
    return t * t * (3 - 2 * t);
  };

  const paint = (): void => {
    if (context === null || cssWidth === 0) return;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.imageSmoothingQuality = "high";
    const eased = mix();
    if (previous !== undefined && eased < 1) {
      draw(previous, 1);
      draw(current, eased);
    } else {
      draw(current, 1);
    }
    context.globalAlpha = 1;
    if (dim > 0) {
      context.fillStyle = `rgb(0 0 0 / ${dim})`;
      context.fillRect(0, 0, cssWidth, cssHeight);
    }
  };

  const resize = (): void => {
    const rect = canvas.getBoundingClientRect();
    cssWidth = rect.width;
    cssHeight = rect.height;
    dpr = Math.min(2, window.devicePixelRatio || 1);
    const backingWidth = Math.max(1, Math.round(cssWidth * dpr));
    const backingHeight = Math.max(1, Math.round(cssHeight * dpr));
    if (canvas.width !== backingWidth) canvas.width = backingWidth;
    if (canvas.height !== backingHeight) canvas.height = backingHeight;
    paint();
  };

  resize();

  return {
    get current() {
      return current;
    },
    show(id, instant) {
      if (id === current) return;
      previous = instant ? undefined : current;
      current = id;
      elapsed = instant ? DISSOLVE_MS : 0;
      paint();
    },
    tick(dtMs) {
      if (elapsed >= DISSOLVE_MS) return false;
      // A backgrounded tab hands back one enormous delta; the dissolve simply completes.
      elapsed = Math.min(DISSOLVE_MS, elapsed + Math.min(dtMs, 64));
      paint();
      if (elapsed >= DISSOLVE_MS) previous = undefined;
      return true;
    },
    setDim(next) {
      if (next === dim) return;
      dim = next;
      paint();
    },
    resize,
    painted() {
      const eased = mix();
      return {
        current,
        previous: previous !== undefined && eased < 1 ? previous : undefined,
        mix: eased,
        dim,
      };
    },
  };
}
