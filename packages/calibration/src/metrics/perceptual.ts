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
import {
  boundaryMask,
  distanceToSeeds,
  fillSilhouetteHoles,
  type Silhouette,
} from "../silhouette";
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
 * The per-window SSIM field, before any averaging.
 *
 * Kept as its own value because the three SSIM rows this package reports are
 * one measurement windowed three ways: the whole crop (`ssimMean`), the lens
 * band and the deep interior (`ssimBand` / `ssimInterior`). Computing the map
 * once and averaging it over three regions is what makes those rows
 * comparable; three independent SSIM calls over three cropped images would not
 * be, because SSIM's windows straddle any crop boundary you introduce.
 *
 * The convolution is 'valid', so window `(x, y)` of the map is centred on image
 * pixel `(x + offset, y + offset)` with `offset = (SSIM_WINDOW - 1) / 2`. That
 * centre is how a window is assigned to a region below.
 */
export interface SsimMap {
  readonly data: Float64Array;
  readonly width: number;
  readonly height: number;
  /** Image coordinate of the map's origin — half the window, floored. */
  readonly offset: number;
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
export function ssimMap(a: CalibrationImage, b: CalibrationImage): SsimMap {
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

  const windowCount = meanA.data.length;
  const data = new Float64Array(windowCount);
  for (let i = 0; i < windowCount; i += 1) {
    const muA = meanA.data[i] ?? 0;
    const muB = meanB.data[i] ?? 0;
    const varA = (meanSquareA.data[i] ?? 0) - muA * muA;
    const varB = (meanSquareB.data[i] ?? 0) - muB * muB;
    const covariance = (meanProduct.data[i] ?? 0) - muA * muB;
    data[i] =
      ((2 * muA * muB + c1) * (2 * covariance + c2)) /
      ((muA * muA + muB * muB + c1) * (varA + varB + c2));
  }

  return { data, width: meanA.width, height: meanA.height, offset: (SSIM_WINDOW - 1) / 2 };
}

/** Mean and worst window over a whole SSIM map. */
export function ssimFromMap(map: SsimMap): SsimReport {
  let sum = 0;
  let min = Number.POSITIVE_INFINITY;
  for (let i = 0; i < map.data.length; i += 1) {
    const value = map.data[i] ?? 0;
    sum += value;
    if (value < min) min = value;
  }
  return { mean: sum / map.data.length, min, windowCount: map.data.length };
}

/**
 * Structural similarity over the whole image — `ssimMap` averaged.
 */
export function ssim(a: CalibrationImage, b: CalibrationImage): SsimReport {
  return ssimFromMap(ssimMap(a, b));
}

// ---------------------------------------------------------------------------
// The band-windowed rows (W13 X6)
// ---------------------------------------------------------------------------

/**
 * Where the lens band ends and the body's interior begins, in CSS px of depth
 * from the contour (W13 X6, Decision Log 1 question 3).
 *
 * Fixed at 24 rather than scaled with the span because the quantity it splits
 * is a fixed depth: the lens's displacement `D(u)` reaches zero by `u ≈ 20` on
 * every span (claims §5.49 §2), so 24 CSS px contains the whole of the band the
 * eye reads the material by, on every cell in the bed. A per-span split would
 * move with the lens depth and would hide a lens change inside a metric change;
 * a fixed number is also one a reader can check against a printed corner crop
 * with a ruler, which is what this row exists to make possible.
 *
 * In device px the split is this number times the fixture's backing scale, so
 * the same CSS-px band is twice as many rows of pixels at 2x. The scale comes
 * from the profile, never from the image.
 */
export const SSIM_BAND_SPLIT_CSS_PX = 24;

/** One SSIM window class: its mean and how many windows it held. */
export interface SsimWindowReport {
  readonly mean: number;
  readonly windowCount: number;
}

/**
 * `ssimBand`, `ssimInterior` and `ssimOutside`: the SSIM map averaged over three
 * regions defined by depth from the reference's own contour.
 *
 * Whole-crop `ssimMean` scores mostly the blurred interior and the untouched
 * backdrop, and cannot see the band where the eye reads the material: W12
 * Decision Log 6 recorded a lens change that lost 0.001–0.002 of SSIM
 * everywhere and that the user read as much closer to macOS. These rows
 * separate those populations without changing the measurement — same map, same
 * 11x11 Gaussian window, same constants.
 *
 * The three regions, by the class of a window's CENTRE pixel:
 *
 *   - `band` — inside the silhouette, within the split of the contour;
 *   - `interior` — inside the silhouette, deeper than the split;
 *   - `outside` — outside the silhouette, within the split of the contour.
 *
 * Together with the **far field** — outside the silhouette and farther than the
 * split, which no row counts — those three partition the crop exactly, so
 * `ssimMean` is their window-count-weighted mean including that far field, and
 * never the mean of the three rows alone. The far field is uncounted on purpose:
 * it is backdrop that neither side's material touches, it is most of the crop on
 * every small span, and averaging it in is precisely what makes `ssimMean` blind
 * to the material.
 *
 * The outward row exists because the eye reads one edge, not two. The band a
 * viewer sees straddles the contour — the rim's spill, the lens's outermost
 * displacement and the outer shadow are on the exterior side — and on the large
 * 2x cells that exterior half carries more of the whole-crop deficit than the
 * interior half does (W13 X6 baseline §5). A `ssimBand` that rose while the
 * exterior fell would otherwise read as an improvement.
 *
 * **The window is the NATIVE silhouette's distance transform.** The reference
 * defines where the band is. A web silhouette moves as the web side is tuned,
 * and a web silhouette that broke into pieces — which happens on the CSS tier
 * over a high-contrast backdrop, where the extractor punches interior holes
 * (see `contourDistance`) — would carry its own new contours and re-window the
 * metric mid-tuning. Holes are filled before the boundary is taken for the same
 * reason: an extraction hole is not an outline, so it must not be a band. The
 * outward distance is the same transform read on the other side of the same
 * boundary, so the two halves of the band are symmetric by construction.
 *
 * Any class can be legitimately empty and is then absent rather than zero: a
 * surface whose half-span is under 24 CSS px — `rrect-sm` and `capsule-button`
 * on this bed — is all band and has no interior to report.
 */
export function ssimDepthWindows(
  map: SsimMap,
  native: Silhouette,
  options: { readonly splitPx: number },
): { band?: SsimWindowReport; interior?: SsimWindowReport; outside?: SsimWindowReport } {
  if (native.width !== map.width + 2 * map.offset || native.height !== map.height + 2 * map.offset) {
    throw new CalibrationError(
      "dimension-mismatch",
      `ssimDepthWindows: the silhouette is ${native.width}x${native.height} but the SSIM map came ` +
        `from a ${String(map.width + 2 * map.offset)}x${String(map.height + 2 * map.offset)} image.`,
    );
  }

  const filled = fillSilhouetteHoles(native);
  const distance = distanceToSeeds(boundaryMask(filled), filled.width, filled.height);

  let bandSum = 0;
  let bandCount = 0;
  let interiorSum = 0;
  let interiorCount = 0;
  let outsideSum = 0;
  let outsideCount = 0;
  for (let y = 0; y < map.height; y += 1) {
    for (let x = 0; x < map.width; x += 1) {
      const pixel = (y + map.offset) * filled.width + (x + map.offset);
      const value = map.data[y * map.width + x] ?? 0;
      const near = (distance[pixel] ?? 0) <= options.splitPx;
      if ((filled.mask[pixel] ?? 0) === 0) {
        // Outside the silhouette: the exterior half of the band, or the far
        // field, which no row counts.
        if (near) {
          outsideSum += value;
          outsideCount += 1;
        }
      } else if (near) {
        bandSum += value;
        bandCount += 1;
      } else {
        interiorSum += value;
        interiorCount += 1;
      }
    }
  }

  return {
    ...(bandCount === 0 ? {} : { band: { mean: bandSum / bandCount, windowCount: bandCount } }),
    ...(interiorCount === 0
      ? {}
      : { interior: { mean: interiorSum / interiorCount, windowCount: interiorCount } }),
    ...(outsideCount === 0
      ? {}
      : { outside: { mean: outsideSum / outsideCount, windowCount: outsideCount } }),
  };
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
