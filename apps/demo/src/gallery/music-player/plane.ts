/**
 * The content plane: one viewport canvas holding the sounding release's artwork, the scheme's
 * dimming and the album column's reading wash, all painted into the pixels the glass samples.
 *
 * Everything the lens should bend lives here and nowhere else. A wash laid over the canvas in CSS
 * would sit in front of the texture rather than in it, so the glass would refract the unwashed
 * photograph while the eye saw the washed one; painting it in keeps paint and sample one set of
 * pixels. The canvas is drawn at its own box's device size, so the renderer's fit of the texture
 * to the element's box is exact rather than a stretched crop.
 */

import type { BackdropHint } from "@vitreajs/vitrea-react";

import type { Release } from "./data";

export type Scheme = "light" | "dark";

export interface PlaneLook {
  readonly release: Release;
  readonly scheme: Scheme;
  /** `prefers-contrast: more`: the wash closes further so the column's type gains margin. */
  readonly contrast: boolean;
  /** The album column's right edge in CSS px: where the wash has to be gone by. */
  readonly columnRight: number;
}

const images = new Map<string, Promise<HTMLImageElement>>();

export function loadImage(url: string): Promise<HTMLImageElement> {
  const cached = images.get(url);
  if (cached !== undefined) return cached;
  const image = new Image();
  image.decoding = "async";
  image.src = url;
  const loaded = image.decode().then(() => image);
  images.set(url, loaded);
  return loaded;
}

export function deviceScale(): number {
  return Math.min(window.devicePixelRatio || 1, 2);
}

function hexToRgb(hex: string): readonly [number, number, number] {
  const value = Number.parseInt(hex.slice(1), 16);
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
}

/**
 * One release, one scheme, one viewport: the finished frame of the plane.
 *
 * Kept as its own canvas so a release change can dissolve between two finished frames. The hint
 * measurement reads these layers too, mixed as `present` last mixed them (see `PlaneFrame`).
 */
export function composeLayer(
  image: HTMLImageElement,
  look: PlaneLook,
  width: number,
  height: number,
  scale: number,
): HTMLCanvasElement {
  const layer = document.createElement("canvas");
  layer.width = Math.round(width * scale);
  layer.height = Math.round(height * scale);
  const context = layer.getContext("2d", { willReadFrequently: true });
  if (context === null) throw new Error("The music player's plane has no 2D context.");
  const W = layer.width;
  const H = layer.height;

  // The artwork, cover-fit and centred: a sleeve is the whole picture, so the crop is the least
  // the window's aspect demands and nothing more.
  const fit = Math.max(W / image.naturalWidth, H / image.naturalHeight);
  const drawW = image.naturalWidth * fit;
  const drawH = image.naturalHeight * fit;
  context.imageSmoothingQuality = "high";
  context.drawImage(image, (W - drawW) / 2, (H - drawH) / 2, drawW, drawH);

  if (look.scheme === "dark") {
    // The room's lamp dimmed, not the print replaced: a multiply keeps every crack and bubble
    // and their hue, at about a third of their daylight level. Dimmer than that and the dark
    // material's body, which follows its backdrop, sinks too; brighter and white ink on the
    // glass fell to 5:1 on the first measurement.
    context.globalCompositeOperation = "multiply";
    context.fillStyle = look.contrast ? "rgb(70 74 82)" : "rgb(84 90 100)";
    context.fillRect(0, 0, W, H);
    context.globalCompositeOperation = "source-over";
  }

  // The reading wash under the album column. Nearly opaque at the window edge, holding across the
  // column's text to its right-aligned durations, and gone within a short run past the column so
  // no glass stands on it. The first build began the fade 90 px inside the column and the
  // durations measured 3.7:1 over its tail.
  const [r, g, b] = hexToRgb(look.release.wash[look.scheme]);
  const edge = look.contrast ? 0.95 : look.scheme === "dark" ? 0.86 : 0.88;
  const hold = look.contrast ? 0.93 : look.scheme === "dark" ? 0.8 : 0.82;
  const column = (look.columnRight * scale) / W;
  const stop = (x: number): number => Math.min(1, Math.max(0, x));
  const wash = context.createLinearGradient(0, 0, W, 0);
  wash.addColorStop(0, `rgb(${r} ${g} ${b} / ${edge})`);
  wash.addColorStop(stop(column - (24 * scale) / W), `rgb(${r} ${g} ${b} / ${hold})`);
  wash.addColorStop(stop(column + (20 * scale) / W), `rgb(${r} ${g} ${b} / ${hold * 0.45})`);
  wash.addColorStop(stop(column + (72 * scale) / W), `rgb(${r} ${g} ${b} / 0)`);
  wash.addColorStop(1, `rgb(${r} ${g} ${b} / 0)`);
  context.fillStyle = wash;
  context.fillRect(0, 0, W, H);

  return layer;
}

/**
 * What the visible canvas is showing: one finished layer, or the dissolve's mix of two.
 *
 * A declared hint overrides the runtime's own tone reading on both tiers, so it has to describe
 * the picture on screen, including the frames of a dissolve, not the layer the dissolve is heading
 * to. `present` returns the frame it drew and `measureRegion` reads exactly that.
 */
export interface PlaneFrame {
  readonly to: HTMLCanvasElement;
  /** The layer being dissolved away from, or null when `to` is shown alone. */
  readonly from: HTMLCanvasElement | null;
  /** The weight `to` was drawn with over `from`; 1 when `from` is null. */
  readonly t: number;
}

/** Paint the visible canvas: the settled layer, or a dissolve from one layer to the next. */
export function present(
  canvas: HTMLCanvasElement,
  to: HTMLCanvasElement,
  from: HTMLCanvasElement | null,
  t: number,
): PlaneFrame {
  if (canvas.width !== to.width || canvas.height !== to.height) {
    canvas.width = to.width;
    canvas.height = to.height;
  }
  const blending = from !== null && t < 1 && from.width === to.width && from.height === to.height;
  const context = canvas.getContext("2d");
  if (context === null) return { to, from: null, t: 1 };
  context.globalAlpha = 1;
  if (blending) {
    context.drawImage(from, 0, 0);
    context.globalAlpha = t;
  }
  context.drawImage(to, 0, 0);
  context.globalAlpha = 1;
  return blending ? { to, from, t } : { to, from: null, t: 1 };
}

const srgbDecode = (encoded: number): number =>
  encoded <= 0.04045 ? encoded / 12.92 : ((encoded + 0.055) / 1.055) ** 2.4;

export interface MeasuredRegion {
  readonly hint: BackdropHint;
  /** The encoded mean, kept for the record: the level the eye and the tone response read. */
  readonly encoded: number;
  readonly min: number;
  readonly max: number;
}

/**
 * What is behind one group, read off the frame the canvas is showing under its box.
 *
 * The runtime's convention for a declared luminance is its own reading's: encoded Rec. 709 luma
 * averaged, then decoded once. Tone follows the encoded level, so a surface over the mid-grey
 * cracks says `mixed` rather than claiming light it does not have. Complexity is the encoded
 * luma's spread, which the 0.24.0 runtime records without consuming; it is declared because it is
 * true, not because anything moves with it.
 *
 * During a dissolve the region is read from both layers and mixed per pixel by the weight
 * `present` drew with. Canvas 2D composites in encoded values and luma is linear in them, so the
 * mixed luma is the luma of the pixel on screen to within the canvas's 8-bit rounding. Reading the
 * two CPU-side layers rather than the visible canvas avoids reading back the canvas the renderer
 * uploads from every frame.
 */
export function measureRegion(
  frame: PlaneFrame,
  rect: { readonly x: number; readonly y: number; readonly width: number; readonly height: number },
  scale: number,
): MeasuredRegion | undefined {
  const { to, from, t } = frame;
  const x = Math.max(0, Math.floor(rect.x * scale));
  const y = Math.max(0, Math.floor(rect.y * scale));
  const w = Math.min(to.width - x, Math.ceil(rect.width * scale));
  const h = Math.min(to.height - y, Math.ceil(rect.height * scale));
  if (w <= 0 || h <= 0) return undefined;
  const read = (layer: HTMLCanvasElement): Uint8ClampedArray | undefined =>
    layer.getContext("2d", { willReadFrequently: true })?.getImageData(x, y, w, h).data;
  const data = read(to);
  const under = from === null ? undefined : read(from);
  if (data === undefined) return undefined;
  const luma = (pixels: Uint8ClampedArray, i: number): number =>
    (0.2126 * (pixels[i] ?? 0) + 0.7152 * (pixels[i + 1] ?? 0) + 0.0722 * (pixels[i + 2] ?? 0)) /
    255;

  let sum = 0;
  let sumSq = 0;
  let count = 0;
  let min = 1;
  let max = 0;
  for (let i = 0; i < data.length; i += 8) {
    const value = under === undefined ? luma(data, i) : t * luma(data, i) + (1 - t) * luma(under, i);
    sum += value;
    sumSq += value * value;
    count += 1;
    if (value < min) min = value;
    if (value > max) max = value;
  }
  if (count === 0) return undefined;
  const mean = sum / count;
  const spread = Math.sqrt(Math.max(0, sumSq / count - mean * mean));
  const round = (value: number): number => Math.round(value * 100) / 100;
  const tone = mean >= 0.62 ? "light" : mean <= 0.38 ? "dark" : "mixed";
  return {
    hint: {
      tone,
      luminance: round(srgbDecode(mean)),
      complexity: round(Math.min(1, spread / 0.25)),
    },
    encoded: round(mean),
    min: round(min),
    max: round(max),
  };
}
