/**
 * The perceptual axis: three full-image comparisons that disagree usefully.
 *
 * A plain per-pixel difference is the wrong summary for glass. Most of a glass
 * surface is a slowly varying interior where a small luminance drift is
 * invisible, and its contour is a few hundred pixels where a one-pixel error is
 * the first thing anyone sees. So:
 *
 *   - `edgeWeightedDifference` re-weights the difference by edge energy, which
 *     buys the contour the attention a mean would spend on the interior;
 *   - `ssim` answers a different question — whether local structure survived —
 *     and is the one that notices a blur that is the wrong *width* even when
 *     its average level is right;
 *   - `oklabDeltaE` is the only one that sees colour, in the only space where
 *     equal numbers mean roughly equal visible steps.
 *
 * The human A/B half of this axis in the methodology is not a computed metric
 * and does not live here.
 */

import { srgbByteToOklab, oklabDistance } from "../color";
import { CalibrationError } from "../errors";
import {
  assertComparable,
  encodedLuma,
  linearLuminance,
  type CalibrationImage,
} from "../image";
import { aggregate, percentileOfSorted } from "../stats";

// ---------------------------------------------------------------------------
// Edge energy
// ---------------------------------------------------------------------------

/**
 * Sobel gradient magnitude of linear-light luminance, one float per pixel.
 *
 * Linear light because the gradient is standing in for "how much contrast is
 * here", and the encoded gradient exaggerates the dark end. Border pixels
 * replicate the edge sample rather than being dropped, so the field is the same
 * size as the image and the weighting below needs no special case.
 */
export function edgeEnergy(image: CalibrationImage): Float64Array {
  const { width, height } = image;
  const luminance = linearLuminance(image);
  const out = new Float64Array(width * height);
  const at = (x: number, y: number): number => {
    const cx = x < 0 ? 0 : x >= width ? width - 1 : x;
    const cy = y < 0 ? 0 : y >= height ? height - 1 : y;
    return luminance[cy * width + cx] ?? 0;
  };

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const gx =
        -at(x - 1, y - 1) - 2 * at(x - 1, y) - at(x - 1, y + 1) + at(x + 1, y - 1) + 2 * at(x + 1, y) + at(x + 1, y + 1);
      const gy =
        -at(x - 1, y - 1) - 2 * at(x, y - 1) - at(x + 1, y - 1) + at(x - 1, y + 1) + 2 * at(x, y + 1) + at(x + 1, y + 1);
      out[y * width + x] = Math.hypot(gx, gy) / 8;
    }
  }
  return out;
}

export interface EdgeWeightedDifferenceOptions {
  /**
   * How much a full-strength edge outweighs a flat pixel. The weight is
   * `1 + gain * normalisedEdgeEnergy`, so the default 4 makes the strongest
   * edge in the scene count five times a flat interior pixel.
   */
  readonly edgeGain?: number;
}

export interface EdgeWeightedDifferenceReport {
  /** Weighted mean absolute luminance difference, linear light. */
  readonly weightedMean: number;
  /** p95 of the per-pixel weighted difference, linear light. */
  readonly weightedP95: number;
  /** The same difference unweighted — the baseline the weighting moves from. */
  readonly unweightedMean: number;
  readonly edgeGain: number;
  readonly sampleCount: number;
}

/**
 * Per-pixel luminance difference, weighted by edge energy.
 *
 * The weight uses the *larger* of the two images' edge energy at each pixel.
 * Taking the reference's alone would under-weight the one error this metric
 * exists to catch: a contour that the candidate placed where the reference has
 * none. There the reference is flat, and only the candidate's edge marks the
 * spot.
 *
 * Normalising by the strongest edge in the scene makes the weight scene-
 * relative, which is what keeps the number comparable between a photo backdrop
 * (lots of edge energy everywhere) and a solid one (edge energy only at the
 * surface contour).
 */
export function edgeWeightedDifference(
  a: CalibrationImage,
  b: CalibrationImage,
  options: EdgeWeightedDifferenceOptions = {},
): EdgeWeightedDifferenceReport {
  assertComparable(a, b, "edgeWeightedDifference");
  const edgeGain = options.edgeGain ?? 4;

  const luminanceA = linearLuminance(a);
  const luminanceB = linearLuminance(b);
  const energyA = edgeEnergy(a);
  const energyB = edgeEnergy(b);
  const count = luminanceA.length;

  let peakEnergy = 0;
  for (let i = 0; i < count; i += 1) {
    peakEnergy = Math.max(peakEnergy, energyA[i] ?? 0, energyB[i] ?? 0);
  }

  const weighted = new Float64Array(count);
  let weightSum = 0;
  let weightedSum = 0;
  let plainSum = 0;
  for (let i = 0; i < count; i += 1) {
    const difference = Math.abs((luminanceA[i] ?? 0) - (luminanceB[i] ?? 0));
    const energy = Math.max(energyA[i] ?? 0, energyB[i] ?? 0);
    // A perfectly flat pair has no edges anywhere; weight everything equally.
    const weight = 1 + edgeGain * (peakEnergy > 0 ? energy / peakEnergy : 0);
    weighted[i] = weight * difference;
    weightSum += weight;
    weightedSum += weight * difference;
    plainSum += difference;
  }

  const sorted = Float64Array.from(weighted);
  sorted.sort();

  return {
    weightedMean: weightedSum / weightSum,
    weightedP95: percentileOfSorted(sorted, 0.95),
    unweightedMean: plainSum / count,
    edgeGain,
    sampleCount: count,
  };
}

// ---------------------------------------------------------------------------
// SSIM
// ---------------------------------------------------------------------------

const SSIM_WINDOW = 11;
const SSIM_SIGMA = 1.5;
const SSIM_DYNAMIC_RANGE = 255;
const SSIM_K1 = 0.01;
const SSIM_K2 = 0.03;

/** The canonical 11-tap Gaussian, σ = 1.5, normalised to unit sum. */
function ssimKernel(): Float64Array {
  const kernel = new Float64Array(SSIM_WINDOW);
  const centre = (SSIM_WINDOW - 1) / 2;
  let sum = 0;
  for (let i = 0; i < SSIM_WINDOW; i += 1) {
    const d = i - centre;
    const value = Math.exp(-(d * d) / (2 * SSIM_SIGMA * SSIM_SIGMA));
    kernel[i] = value;
    sum += value;
  }
  for (let i = 0; i < SSIM_WINDOW; i += 1) kernel[i] = (kernel[i] ?? 0) / sum;
  return kernel;
}

/**
 * Separable 'valid' convolution: the output holds only the positions where the
 * whole kernel fits, so every SSIM statistic below is a full weighted window
 * and no boundary convention can leak into the result.
 */
function convolveValid(
  source: Float64Array,
  width: number,
  height: number,
  kernel: Float64Array,
): { data: Float64Array; width: number; height: number } {
  const taps = kernel.length;
  const midWidth = width - taps + 1;
  const rows = new Float64Array(midWidth * height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < midWidth; x += 1) {
      let sum = 0;
      for (let k = 0; k < taps; k += 1) sum += (kernel[k] ?? 0) * (source[y * width + x + k] ?? 0);
      rows[y * midWidth + x] = sum;
    }
  }

  const outHeight = height - taps + 1;
  const out = new Float64Array(midWidth * outHeight);
  for (let y = 0; y < outHeight; y += 1) {
    for (let x = 0; x < midWidth; x += 1) {
      let sum = 0;
      for (let k = 0; k < taps; k += 1) sum += (kernel[k] ?? 0) * (rows[(y + k) * midWidth + x] ?? 0);
      out[y * midWidth + x] = sum;
    }
  }
  return { data: out, width: midWidth, height: outHeight };
}

export interface SsimReport {
  /** Mean SSIM over every full window, in -1..1; 1 is identical. */
  readonly mean: number;
  /**
   * The worst single window. The number that survives averaging: a surface
   * occupying 5% of the frame can be badly wrong while the mean stays near 1.
   */
  readonly min: number;
  readonly windowCount: number;
}

/**
 * Structural similarity on luminance, with the standard 11x11 Gaussian window
 * at σ = 1.5 and the standard constants (K1 = 0.01, K2 = 0.03, L = 255).
 *
 * Computed on *encoded* luma, which is the one deliberate exception to this
 * package's linear-light rule — see `encodedLuma` for why: SSIM's stabilising
 * constants are fractions of the stored signal's dynamic range, so moving the
 * signal changes what the number means and makes it incomparable with every
 * published SSIM figure.
 */
export function ssim(a: CalibrationImage, b: CalibrationImage): SsimReport {
  assertComparable(a, b, "ssim");
  if (a.width < SSIM_WINDOW || a.height < SSIM_WINDOW) {
    throw new CalibrationError(
      "empty-region",
      `ssim: a ${a.width}x${a.height} image is smaller than the ${SSIM_WINDOW}x${SSIM_WINDOW} window, so no full window exists.`,
    );
  }

  const kernel = ssimKernel();
  const lumaA = encodedLuma(a);
  const lumaB = encodedLuma(b);
  const count = lumaA.length;

  const squareA = new Float64Array(count);
  const squareB = new Float64Array(count);
  const product = new Float64Array(count);
  for (let i = 0; i < count; i += 1) {
    const x = lumaA[i] ?? 0;
    const y = lumaB[i] ?? 0;
    squareA[i] = x * x;
    squareB[i] = y * y;
    product[i] = x * y;
  }

  const meanA = convolveValid(lumaA, a.width, a.height, kernel);
  const meanB = convolveValid(lumaB, a.width, a.height, kernel);
  const meanSquareA = convolveValid(squareA, a.width, a.height, kernel);
  const meanSquareB = convolveValid(squareB, a.width, a.height, kernel);
  const meanProduct = convolveValid(product, a.width, a.height, kernel);

  const c1 = (SSIM_K1 * SSIM_DYNAMIC_RANGE) ** 2;
  const c2 = (SSIM_K2 * SSIM_DYNAMIC_RANGE) ** 2;

  let sum = 0;
  let min = Number.POSITIVE_INFINITY;
  const windowCount = meanA.data.length;
  for (let i = 0; i < windowCount; i += 1) {
    const muA = meanA.data[i] ?? 0;
    const muB = meanB.data[i] ?? 0;
    const varA = (meanSquareA.data[i] ?? 0) - muA * muA;
    const varB = (meanSquareB.data[i] ?? 0) - muB * muB;
    const covariance = (meanProduct.data[i] ?? 0) - muA * muB;
    const value =
      ((2 * muA * muB + c1) * (2 * covariance + c2)) /
      ((muA * muA + muB * muB + c1) * (varA + varB + c2));
    sum += value;
    if (value < min) min = value;
  }

  return { mean: sum / windowCount, min, windowCount };
}

// ---------------------------------------------------------------------------
// OKLab ΔE
// ---------------------------------------------------------------------------

export interface OklabDeltaEReport {
  /** Mean ΔE_OK over every pixel. Unitless OKLab distance. */
  readonly mean: number;
  readonly p95: number;
  readonly max: number;
  readonly sampleCount: number;
}

/**
 * Per-pixel colour difference in OKLab, through the correct
 * sRGB → linear → LMS → cube-root → Lab chain (see `linearRgbToOklab`).
 *
 * Alpha is not compared. Captures under this methodology are opaque composites
 * over a shared background, so a difference in alpha would mean the harness
 * captured the wrong thing, which the shape axis's silhouette extraction is the
 * place to notice.
 */
export function oklabDeltaE(a: CalibrationImage, b: CalibrationImage): OklabDeltaEReport {
  assertComparable(a, b, "oklabDeltaE");
  const count = a.width * a.height;
  const deltas = new Float64Array(count);
  for (let i = 0; i < count; i += 1) {
    const src = i * 4;
    deltas[i] = oklabDistance(
      srgbByteToOklab(a.data[src] ?? 0, a.data[src + 1] ?? 0, a.data[src + 2] ?? 0),
      srgbByteToOklab(b.data[src] ?? 0, b.data[src + 1] ?? 0, b.data[src + 2] ?? 0),
    );
  }
  const stats = aggregate(deltas, "oklabDeltaE");
  return { mean: stats.mean, p95: stats.p95, max: stats.max, sampleCount: stats.count };
}
