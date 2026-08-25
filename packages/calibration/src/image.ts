/**
 * The one image representation this package measures, and the conversions off
 * it.
 *
 * A calibration image is deliberately the *capture* format and nothing more:
 * 8-bit RGBA, non-premultiplied, sRGB-encoded — what a PNG off either harness
 * actually contains under X5. Every metric derives the field it needs (linear
 * light, luminance, alpha, OKLab) from this one value, so there is exactly one
 * place where the encoding boundary is crossed and it is always crossed
 * explicitly.
 *
 * Note the asymmetry with the renderers: internal optical math is
 * premultiplied linear light (X5), but that is the *compositing* domain. What
 * lands in a capture is the composited, encoded result, and un-premultiplying
 * an 8-bit composite would invent precision. So the harness compares encoded
 * captures and converts forward, never backwards.
 */

import { Buffer } from "node:buffer";
import { PNG } from "pngjs";

import { linearRgbLuminance, srgbByteToLinear } from "./color";
import { CalibrationError } from "./errors";

/**
 * A decoded capture. `data` is RGBA8 in row-major order, non-premultiplied,
 * sRGB-encoded (X5).
 */
export interface CalibrationImage {
  readonly width: number;
  readonly height: number;
  readonly data: Uint8Array;
}

/** A pixel-space rectangle, used to scope a metric to part of a scene. */
export interface PixelRect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/** Wrap a raw RGBA8 buffer, checking that it is the size it claims to be. */
export function createImage(width: number, height: number, data: Uint8Array): CalibrationImage {
  const expected = width * height * 4;
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0) {
    throw new CalibrationError("malformed-png", `createImage: ${width}x${height} is not a positive integer size.`);
  }
  if (data.length !== expected) {
    throw new CalibrationError(
      "malformed-png",
      `createImage: ${width}x${height} needs ${expected} RGBA bytes, got ${data.length}.`,
    );
  }
  return { width, height, data };
}

/**
 * Decode a PNG buffer. The only I/O-adjacent function in the package — reading
 * the file is the caller's job, so every metric stays a pure function of bytes.
 *
 * pngjs normalises palette, grayscale and 16-bit sources to 8-bit RGBA, which
 * is what makes one internal representation sufficient.
 */
export function decodePng(buffer: Uint8Array): CalibrationImage {
  const png = PNG.sync.read(Buffer.from(buffer.buffer, buffer.byteOffset, buffer.byteLength));
  const data = new Uint8Array(png.data.buffer, png.data.byteOffset, png.data.byteLength);
  return createImage(png.width, png.height, data);
}

/**
 * The comparison guard.
 *
 * Two captures of different size are not a comparison this package can make.
 * Resizing one to match would fabricate the very thing the shape axis measures
 * — contour position to sub-pixel precision — so a mismatch is a refusal, and
 * the message names both sizes and the metric that asked, because in practice
 * the cause is a DPR or capture-region mistake in the harness that produced
 * them.
 */
export function assertComparable(a: CalibrationImage, b: CalibrationImage, context = "comparison"): void {
  if (a.width !== b.width || a.height !== b.height) {
    throw new CalibrationError(
      "dimension-mismatch",
      `${context}: images are ${a.width}x${a.height} and ${b.width}x${b.height}. ` +
        `Calibration never resizes — capture both sides at the same size and scale (check the profile's DPR).`,
    );
  }
}

/** Byte offset of a pixel's red channel. */
export function pixelOffset(image: CalibrationImage, x: number, y: number): number {
  return (y * image.width + x) * 4;
}

/** Clamp a rectangle to the image, refusing one that lands entirely outside. */
export function clampRect(image: CalibrationImage, rect: PixelRect | undefined, context = "region"): PixelRect {
  if (!rect) return { x: 0, y: 0, width: image.width, height: image.height };

  const x = Math.max(0, Math.min(image.width, Math.floor(rect.x)));
  const y = Math.max(0, Math.min(image.height, Math.floor(rect.y)));
  const width = Math.max(0, Math.min(image.width - x, Math.floor(rect.width)));
  const height = Math.max(0, Math.min(image.height - y, Math.floor(rect.height)));
  if (width === 0 || height === 0) {
    throw new CalibrationError(
      "empty-region",
      `${context}: the requested rect ${rect.x},${rect.y} ${rect.width}x${rect.height} does not overlap the ` +
        `${image.width}x${image.height} image.`,
    );
  }
  return { x, y, width, height };
}

/**
 * Linear-light RGB, three floats per pixel in 0..1.
 *
 * This is the domain for anything that adds or averages light: blur kernels,
 * edge-spread, rim energy, shadow falloff, transfer fits. Alpha is dropped —
 * a composite capture has no meaningful alpha, and where alpha *is* meaningful
 * (a silhouette render) it is read as its own channel.
 */
export function toLinearRgb(image: CalibrationImage): Float64Array {
  const count = image.width * image.height;
  const out = new Float64Array(count * 3);
  for (let i = 0; i < count; i += 1) {
    const src = i * 4;
    out[i * 3] = srgbByteToLinear(image.data[src] ?? 0);
    out[i * 3 + 1] = srgbByteToLinear(image.data[src + 1] ?? 0);
    out[i * 3 + 2] = srgbByteToLinear(image.data[src + 2] ?? 0);
  }
  return out;
}

/** Relative luminance in linear light, one float per pixel in 0..1. */
export function linearLuminance(image: CalibrationImage): Float64Array {
  const count = image.width * image.height;
  const out = new Float64Array(count);
  for (let i = 0; i < count; i += 1) {
    const src = i * 4;
    out[i] = linearRgbLuminance(
      srgbByteToLinear(image.data[src] ?? 0),
      srgbByteToLinear(image.data[src + 1] ?? 0),
      srgbByteToLinear(image.data[src + 2] ?? 0),
    );
  }
  return out;
}

/**
 * Luma on the *encoded* values, 0..255.
 *
 * The one place this package deliberately stays in encoded space. SSIM's
 * stabilising constants are defined as fractions of the dynamic range of the
 * stored signal (K1·L)², and its contrast and structure terms were validated
 * against gamma-encoded imagery; recomputing it in linear light silently
 * changes what the number means and makes it incomparable with every published
 * SSIM figure. So SSIM reads this, and everything optical reads
 * `linearLuminance`.
 */
export function encodedLuma(image: CalibrationImage): Float64Array {
  const count = image.width * image.height;
  const out = new Float64Array(count);
  for (let i = 0; i < count; i += 1) {
    const src = i * 4;
    out[i] =
      0.2126 * (image.data[src] ?? 0) + 0.7152 * (image.data[src + 1] ?? 0) + 0.0722 * (image.data[src + 2] ?? 0);
  }
  return out;
}

/** The alpha channel as-is, one byte per pixel. */
export function alphaChannel(image: CalibrationImage): Uint8Array {
  const count = image.width * image.height;
  const out = new Uint8Array(count);
  for (let i = 0; i < count; i += 1) out[i] = image.data[i * 4 + 3] ?? 0;
  return out;
}
