/**
 * Synthetic images with known ground truth.
 *
 * Every metric in this package is tested against an image whose answer is
 * derived analytically rather than against a committed capture. A capture can
 * only tell you a metric is *stable*; only a construction where the true σ, the
 * true translation or the true curvature is known by algebra can tell you the
 * metric is *right*. A metric nobody validated against a known answer is not
 * ground truth, however confidently it prints a number.
 *
 * All constructors take linear-light values and encode to sRGB on the way out,
 * because that is the direction a real capture came from (X5).
 */

import { PNG } from "pngjs";

import { linearToSrgbEncoded } from "../src/color";
import { createImage, type CalibrationImage } from "../src/image";
import type { Silhouette } from "../src/silhouette";

/** Linear-light 0..1 → the sRGB-encoded byte a capture would hold. */
export function encodeByte(linear: number): number {
  const clamped = Math.min(1, Math.max(0, linear));
  return Math.round(linearToSrgbEncoded(clamped) * 255);
}

/** Build an image from a per-pixel linear-light RGB function. Alpha is 255. */
export function fromLinearRgb(
  width: number,
  height: number,
  sample: (x: number, y: number) => readonly [number, number, number],
): CalibrationImage {
  const data = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const [r, g, b] = sample(x, y);
      const offset = (y * width + x) * 4;
      data[offset] = encodeByte(r);
      data[offset + 1] = encodeByte(g);
      data[offset + 2] = encodeByte(b);
      data[offset + 3] = 255;
    }
  }
  return createImage(width, height, data);
}

/**
 * A neutral grey image from a per-pixel linear-light luminance function. The
 * Rec.709 weights sum to 1, so an equal-channel grey has exactly the luminance
 * it was built with — which is what makes the material tests' algebra exact.
 */
export function fromLinearLuminance(
  width: number,
  height: number,
  sample: (x: number, y: number) => number,
): CalibrationImage {
  return fromLinearRgb(width, height, (x, y) => {
    const value = sample(x, y);
    return [value, value, value];
  });
}

/** A flat image at one linear-light luminance. */
export function solidLuminance(width: number, height: number, luminance: number): CalibrationImage {
  return fromLinearLuminance(width, height, () => luminance);
}

/** An RGBA image whose alpha is the silhouette: opaque inside, clear outside. */
export function alphaMaskImage(
  width: number,
  height: number,
  inside: (x: number, y: number) => boolean,
): CalibrationImage {
  const data = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const opaque = inside(x, y);
      data[offset] = 255;
      data[offset + 1] = 255;
      data[offset + 2] = 255;
      data[offset + 3] = opaque ? 255 : 0;
    }
  }
  return createImage(width, height, data);
}

/** A silhouette straight from a predicate, bypassing extraction. */
export function maskFromPredicate(
  width: number,
  height: number,
  inside: (x: number, y: number) => boolean,
): Silhouette {
  const mask = new Uint8Array(width * height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      mask[y * width + x] = inside(x, y) ? 1 : 0;
    }
  }
  return { width, height, mask };
}

/** Inclusive axis-aligned rectangle predicate. */
export function rectPredicate(
  x0: number,
  y0: number,
  x1: number,
  y1: number,
): (x: number, y: number) => boolean {
  return (x, y) => x >= x0 && x <= x1 && y >= y0 && y <= y1;
}

/** Rasterised disc predicate: pixel centres inside the circle. */
export function discPredicate(cx: number, cy: number, radius: number): (x: number, y: number) => boolean {
  return (x, y) => (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius;
}

/**
 * Euclidean distance from a pixel centre to the nearest pixel inside an
 * inclusive rectangle — the analytic answer the shadow-falloff test builds its
 * profile from, so the test never asks the distance transform to grade its own
 * homework.
 */
export function distanceOutsideRect(x: number, y: number, x0: number, y0: number, x1: number, y1: number): number {
  const dx = Math.max(x0 - x, 0, x - x1);
  const dy = Math.max(y0 - y, 0, y - y1);
  return Math.hypot(dx, dy);
}

/**
 * Depth of an interior pixel below the boundary of an inclusive rectangle: the
 * distance to the nearest pixel *outside* it. For a rectangle the nearest
 * exterior pixel is always axis-adjacent, so this is exact.
 */
export function depthInsideRect(x: number, y: number, x0: number, y0: number, x1: number, y1: number): number {
  return 1 + Math.min(x - x0, x1 - x, y - y0, y1 - y);
}

/** Standard normal CDF, for building an exactly-Gaussian edge. */
export function gaussianStep(x: number, centre: number, sigma: number): number {
  // Erf via the same A&S approximation the fit uses would make the test
  // circular, so this integrates the normal density directly instead.
  const z = (x - centre) / sigma;
  const steps = 4096;
  const limit = 8;
  if (z <= -limit) return 0;
  if (z >= limit) return 1;
  let sum = 0;
  const h = (z + limit) / steps;
  for (let i = 0; i <= steps; i += 1) {
    const t = -limit + i * h;
    const weight = i === 0 || i === steps ? 0.5 : 1;
    sum += weight * Math.exp(-0.5 * t * t);
  }
  return (sum * h) / Math.sqrt(2 * Math.PI);
}

/** Encode an image to a PNG buffer, for exercising the decode path. */
export function encodePng(image: CalibrationImage): Uint8Array {
  const png = new PNG({ width: image.width, height: image.height });
  png.data.set(image.data);
  return new Uint8Array(PNG.sync.write(png));
}
