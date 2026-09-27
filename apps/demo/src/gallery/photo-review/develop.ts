/**
 * The develop step: what the stage canvas paints, and what the page measures off it.
 *
 * Everything the glass sits over is painted here, into the canvas the three groups read as
 * their texture: the frame with its exposure, white balance and straighten applied in linear
 * light, the crop matte, and in crop mode the crop frame and its thirds grid. Painting them
 * rather than laying them over the canvas in CSS is what puts them behind the glass, where the
 * lens can bend them (materialist skill, "The live plane"). The canvas is painted at its own
 * box's device size, so the texture the runtime imports and the pixels on screen are the same.
 *
 * The same pixels are what each group's hint is measured from (`regionReading`), so the
 * declaration both tiers adapt to is a reading of the frame under that group rather than a
 * guess about the shoot.
 */
import type { BackdropHint } from "@vitreajs/vitrea-react";

import type { Develop, Frame, Framing } from "./data";

export interface Rect {
  readonly x: number;
  readonly y: number;
  readonly w: number;
  readonly h: number;
}

/** sRGB code to linear light, per 8-bit code. */
const DECODE = new Float32Array(256);
for (let i = 0; i < 256; i += 1) {
  const c = i / 255;
  DECODE[i] = c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** Linear light to sRGB code, tabulated finely enough that the shadows keep their steps. */
const ENCODE_STEPS = 8192;
const ENCODE = new Uint8ClampedArray(ENCODE_STEPS + 1);
for (let i = 0; i <= ENCODE_STEPS; i += 1) {
  const l = i / ENCODE_STEPS;
  const c = l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;
  ENCODE[i] = Math.round(c * 255);
}

const encode = (linear: number): number =>
  ENCODE[Math.min(ENCODE_STEPS, Math.max(0, Math.round(linear * ENCODE_STEPS)))] ?? 0;
const decode = (code: number): number => DECODE[code] ?? 0;

/** A blackbody's colour in linear RGB (Tanner Helland's fit, decoded), for white balance. */
function kelvin(k: number): [number, number, number] {
  const t = k / 100;
  const r = t <= 66 ? 255 : 329.698727446 * (t - 60) ** -0.1332047592;
  const g = t <= 66 ? 99.4708025861 * Math.log(t) - 161.1195681661 : 288.1221695283 * (t - 60) ** -0.0755148492;
  const b = t >= 66 ? 255 : t <= 19 ? 0 : 138.5177312231 * Math.log(t - 10) - 305.0447927307;
  const lin = (v: number): number => decode(Math.round(Math.min(255, Math.max(1, v))));
  return [lin(r), lin(g), lin(b)];
}

/**
 * Per-channel gains in linear light. White balance divides the target illuminant out and the
 * as-shot one back in, so a higher temperature warms the frame as it does in every raw
 * converter; the gains are normalised to unit luminance so white balance never moves exposure.
 */
export function channelGains(develop: Develop, asShotTemp: number, bracket: number, before: boolean): [number, number, number] {
  const exposure = 2 ** (bracket + (before ? 0 : develop.ev));
  if (before) return [exposure, exposure, exposure];
  const shot = kelvin(asShotTemp);
  const target = kelvin(develop.temp);
  const gains: [number, number, number] = [shot[0] / target[0], shot[1] / target[1], shot[2] / target[2]];
  gains[1] *= 2 ** (-develop.tint / 120);
  const y = 0.2126 * gains[0] + 0.7152 * gains[1] + 0.0722 * gains[2];
  return [(gains[0] / y) * exposure, (gains[1] / y) * exposure, (gains[2] / y) * exposure];
}

function lutFor(gain: number): Uint8ClampedArray {
  const lut = new Uint8ClampedArray(256);
  for (let i = 0; i < 256; i += 1) lut[i] = encode(Math.min(1, decode(i) * gain));
  return lut;
}

export function applyGains(data: ImageData, gains: readonly [number, number, number]): void {
  if (gains.every((g) => Math.abs(g - 1) < 1e-4)) return;
  const [lr, lg, lb] = gains.map(lutFor) as [Uint8ClampedArray, Uint8ClampedArray, Uint8ClampedArray];
  const d = data.data;
  for (let i = 0; i < d.length; i += 4) {
    d[i] = lr[d[i] ?? 0] ?? 0;
    d[i + 1] = lg[d[i + 1] ?? 0] ?? 0;
    d[i + 2] = lb[d[i + 2] ?? 0] ?? 0;
  }
}

const RATIOS: Record<Develop["aspect"], number> = { original: 1.5, "1:1": 1, "4:5": 0.8, "16:9": 16 / 9 };

/** The crop in the frame's own units (0..1 on both axes), clamped inside the frame. */
export function cropRect(develop: Develop): Rect {
  const relative = RATIOS[develop.aspect] / 1.5;
  let w = relative >= 1 ? 1 : relative;
  let h = relative >= 1 ? 1 / relative : 1;
  w *= develop.scale;
  h *= develop.scale;
  const x = Math.min(1 - w, Math.max(0, develop.cx - w / 2));
  const y = Math.min(1 - h, Math.max(0, develop.cy - h / 2));
  return { x, y, w, h };
}

export const hasCrop = (develop: Develop): boolean => develop.aspect !== "original" || develop.scale < 0.999;

/**
 * Draw a burst member into a w x h context: the file re-framed by its framing, then rotated by
 * the straighten angle and scaled just enough that no corner of the frame shows empty.
 */
export function drawFraming(
  ctx: CanvasRenderingContext2D,
  image: HTMLImageElement,
  framing: Framing,
  angleDeg: number,
  w: number,
  h: number,
): void {
  const W = image.naturalWidth;
  const H = image.naturalHeight;
  const sw = W / framing.zoom;
  const sh = H / framing.zoom;
  const sx = Math.min(W - sw, Math.max(0, (W - sw) / 2 + framing.ox * W));
  const sy = Math.min(H - sh, Math.max(0, (H - sh) / 2 + framing.oy * H));
  const theta = (angleDeg * Math.PI) / 180;
  const cover = Math.cos(Math.abs(theta)) + (w / h) * Math.sin(Math.abs(theta));
  ctx.save();
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";
  ctx.translate(w / 2, h / 2);
  ctx.rotate(theta);
  ctx.scale(cover, cover);
  ctx.drawImage(image, sx, sy, sw, sh, -w / 2, -h / 2, w, h);
  ctx.restore();
}

export interface Histogram {
  readonly r: Uint32Array;
  readonly g: Uint32Array;
  readonly b: Uint32Array;
  readonly luma: Uint32Array;
  /** Share of pixels with a channel at the top code, and with every channel at the bottom. */
  readonly clippedHigh: number;
  readonly clippedLow: number;
}

export const HISTOGRAM_BINS = 64;

const bump = (bins: Uint32Array, at: number): void => {
  bins[at] = (bins[at] ?? 0) + 1;
};

export function histogramOf(data: ImageData): Histogram {
  const r = new Uint32Array(HISTOGRAM_BINS);
  const g = new Uint32Array(HISTOGRAM_BINS);
  const b = new Uint32Array(HISTOGRAM_BINS);
  const luma = new Uint32Array(HISTOGRAM_BINS);
  const d = data.data;
  const shift = 256 / HISTOGRAM_BINS;
  let high = 0;
  let low = 0;
  let n = 0;
  for (let i = 0; i < d.length; i += 16) {
    const R = d[i] ?? 0;
    const G = d[i + 1] ?? 0;
    const B = d[i + 2] ?? 0;
    const y = encode(0.2126 * decode(R) + 0.7152 * decode(G) + 0.0722 * decode(B));
    bump(r, Math.floor(R / shift));
    bump(g, Math.floor(G / shift));
    bump(b, Math.floor(B / shift));
    bump(luma, Math.floor(y / shift));
    if (R >= 254 || G >= 254 || B >= 254) high += 1;
    if (R <= 1 && G <= 1 && B <= 1) low += 1;
    n += 1;
  }
  return { r, g, b, luma, clippedHigh: n === 0 ? 0 : high / n, clippedLow: n === 0 ? 0 : low / n };
}

/**
 * The exposure that places the frame's brightest half-percent just under white: expose to the
 * right, which on firelit frames keeps the fire and lifts the shop rather than averaging the
 * frame to grey and blowing the hearth.
 */
export function autoExposure(data: ImageData, currentEv: number): number {
  const d = data.data;
  const values: number[] = [];
  for (let i = 0; i < d.length; i += 64) {
    values.push(Math.max(decode(d[i] ?? 0), decode(d[i + 1] ?? 0), decode(d[i + 2] ?? 0)));
  }
  values.sort((a, c) => a - c);
  const p = values[Math.floor(values.length * 0.995)] ?? 1;
  const stops = Math.log2(0.92 / Math.max(p, 1e-4));
  const next = currentEv + stops;
  return Math.round(Math.min(1.5, Math.max(-1.5, next)) * 20) / 20;
}

export interface StagePaint {
  readonly frame: Frame;
  readonly image: HTMLImageElement;
  readonly before: boolean;
  readonly cropMode: boolean;
  /** The ground, as a CSS colour: the surround the frame sits in and the matte's colour. */
  readonly ground: string;
  readonly dpr: number;
  /** The frame's rectangle in the canvas, in CSS px. */
  readonly photo: Rect;
}

/** Device-pixel rectangle of a CSS rectangle on this canvas. */
export function devicePx(rect: Rect, dpr: number): Rect {
  const x = Math.round(rect.x * dpr);
  const y = Math.round(rect.y * dpr);
  return { x, y, w: Math.round((rect.x + rect.w) * dpr) - x, h: Math.round((rect.y + rect.h) * dpr) - y };
}

/**
 * Paint the stage and return the developed frame's pixels (before the matte), which the
 * histogram and the auto exposure read.
 */
export function paintStage(canvas: HTMLCanvasElement, work: HTMLCanvasElement, paint: StagePaint): ImageData | null {
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const wctx = work.getContext("2d", { willReadFrequently: true });
  if (ctx === null || wctx === null) return null;
  const { frame, image, before, cropMode, ground, dpr } = paint;
  const develop = frame.develop;

  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.fillStyle = ground;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const px = devicePx(paint.photo, dpr);
  if (px.w <= 0 || px.h <= 0) return null;
  if (work.width !== px.w || work.height !== px.h) {
    work.width = px.w;
    work.height = px.h;
  }
  wctx.setTransform(1, 0, 0, 1, 0, 0);
  wctx.clearRect(0, 0, px.w, px.h);
  drawFraming(wctx, image, frame.framing, before ? 0 : develop.angle, px.w, px.h);
  const data = wctx.getImageData(0, 0, px.w, px.h);
  applyGains(data, channelGains(develop, frame.photo.asShotTemp, frame.framing.bracket, before));
  ctx.putImageData(data, px.x, px.y);

  if (!before && (cropMode || hasCrop(develop))) paintCrop(ctx, px, cropRect(develop), ground, dpr, cropMode);
  return data;
}

/**
 * The crop matte, and in crop mode the frame, its corners and the thirds grid. The matte washes
 * the cropped-away frame toward the ground rather than hiding it, so the frame's rectangle, and
 * every control placed on it, holds still whatever the crop (`DESIGN.md`, decisions).
 */
function paintCrop(ctx: CanvasRenderingContext2D, px: Rect, crop: Rect, ground: string, dpr: number, cropMode: boolean): void {
  const cx = px.x + Math.round(crop.x * px.w);
  const cy = px.y + Math.round(crop.y * px.h);
  const cw = Math.round(crop.w * px.w);
  const ch = Math.round(crop.h * px.h);
  ctx.save();
  ctx.fillStyle = ground;
  ctx.globalAlpha = cropMode ? 0.5 : 0.66;
  ctx.fillRect(px.x, px.y, px.w, cy - px.y);
  ctx.fillRect(px.x, cy + ch, px.w, px.y + px.h - (cy + ch));
  ctx.fillRect(px.x, cy, cx - px.x, ch);
  ctx.fillRect(cx + cw, cy, px.x + px.w - (cx + cw), ch);
  ctx.globalAlpha = 1;
  if (cropMode) {
    const line = Math.max(1, Math.round(dpr));
    ctx.fillStyle = "rgba(255, 255, 255, 0.42)";
    for (const f of [1 / 3, 2 / 3]) {
      ctx.fillRect(cx + Math.round(cw * f), cy, line, ch);
      ctx.fillRect(cx, cy + Math.round(ch * f), cw, line);
    }
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
    ctx.fillRect(cx, cy, cw, line);
    ctx.fillRect(cx, cy + ch - line, cw, line);
    ctx.fillRect(cx, cy, line, ch);
    ctx.fillRect(cx + cw - line, cy, line, ch);
    const arm = Math.round(18 * dpr);
    const t = Math.round(3 * dpr);
    ctx.fillStyle = "#ffffff";
    for (const [x, y, sx, sy] of [
      [cx, cy, 1, 1],
      [cx + cw, cy, -1, 1],
      [cx, cy + ch, 1, -1],
      [cx + cw, cy + ch, -1, -1],
    ] as const) {
      ctx.fillRect(sx > 0 ? x : x - arm, sy > 0 ? y : y - t, arm, t);
      ctx.fillRect(sx > 0 ? x : x - t, sy > 0 ? y : y - arm, t, arm);
    }
  }
  ctx.restore();
}

/** What the plane holds under one box, and the hint that states it. */
export interface RegionReading {
  /** The encoded mean of the pixels' luminance, 0..1. */
  readonly mean: number;
  /**
   * The encoded standard deviation of the pixels' luminance, 0..1: how much structure the
   * lens has to bend under the box. `DESIGN.md`'s flat-phase table is a list of these.
   */
  readonly deviation: number;
  readonly hint: BackdropHint;
}

/**
 * A group's backdrop declaration, measured off the painted canvas under the box the runtime
 * drew the group at: mean linear luminance (what the hint's `luminance` is), a tone from the
 * encoded mean and the share of light and dark pixels, and a complexity from the encoded
 * deviation. The box is the drawn one, never the one the layout intended, because a declared
 * hint overrides the runtime's own tone reading on both tiers and so must describe the pixels
 * actually under the glass.
 */
export function regionReading(canvas: HTMLCanvasElement, rect: Rect, dpr: number): RegionReading | undefined {
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (ctx === null) return undefined;
  const px = devicePx(rect, dpr);
  const x = Math.max(0, px.x);
  const y = Math.max(0, px.y);
  const w = Math.min(canvas.width - x, px.w);
  const h = Math.min(canvas.height - y, px.h);
  if (w <= 0 || h <= 0) return undefined;
  const d = ctx.getImageData(x, y, w, h).data;
  let sumLin = 0;
  let sumEnc = 0;
  let sumEnc2 = 0;
  let light = 0;
  let dark = 0;
  let n = 0;
  for (let i = 0; i < d.length; i += 8) {
    const lin = 0.2126 * decode(d[i] ?? 0) + 0.7152 * decode(d[i + 1] ?? 0) + 0.0722 * decode(d[i + 2] ?? 0);
    const enc = encode(lin) / 255;
    sumLin += lin;
    sumEnc += enc;
    sumEnc2 += enc * enc;
    if (enc > 0.7) light += 1;
    if (enc < 0.25) dark += 1;
    n += 1;
  }
  if (n === 0) return undefined;
  const meanEnc = sumEnc / n;
  const sd = Math.sqrt(Math.max(0, sumEnc2 / n - meanEnc * meanEnc));
  const tone: BackdropHint["tone"] =
    light / n > 0.2 && dark / n > 0.2 ? "mixed" : meanEnc >= 0.6 ? "light" : meanEnc <= 0.4 ? "dark" : "mixed";
  const round = (v: number): number => Math.round(v * 100) / 100;
  return {
    mean: meanEnc,
    deviation: sd,
    hint: { tone, luminance: round(sumLin / n), complexity: round(Math.min(1, sd / 0.25)) },
  };
}

/**
 * A filmstrip thumbnail: the same develop at thumbnail size, cropped and fit into the cell,
 * so the strip shows what each frame will export as.
 */
export function paintThumb(canvas: HTMLCanvasElement, work: HTMLCanvasElement, image: HTMLImageElement, frame: Frame, ground: string): void {
  const ctx = canvas.getContext("2d");
  const wctx = work.getContext("2d", { willReadFrequently: true });
  if (ctx === null || wctx === null) return;
  const w = canvas.width;
  const h = canvas.height;
  if (work.width !== w || work.height !== h) {
    work.width = w;
    work.height = h;
  }
  const develop = frame.develop;
  wctx.setTransform(1, 0, 0, 1, 0, 0);
  wctx.clearRect(0, 0, w, h);
  drawFraming(wctx, image, frame.framing, develop.angle, w, h);
  const data = wctx.getImageData(0, 0, w, h);
  applyGains(data, channelGains(develop, frame.photo.asShotTemp, frame.framing.bracket, false));
  wctx.putImageData(data, 0, 0);
  ctx.fillStyle = ground;
  ctx.fillRect(0, 0, w, h);
  if (!hasCrop(develop)) {
    ctx.drawImage(work, 0, 0);
    return;
  }
  const crop = cropRect(develop);
  const sw = crop.w * w;
  const sh = crop.h * h;
  const fit = Math.min(w / sw, h / sh);
  const dw = sw * fit;
  const dh = sh * fit;
  ctx.drawImage(work, crop.x * w, crop.y * h, sw, sh, (w - dw) / 2, (h - dh) / 2, dw, dh);
}
