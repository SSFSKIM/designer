/**
 * The per-pixel chroma instrument (W31 G0, claims §5.161).
 *
 * `metrics/material.ts`'s `tintResponse` averages the interior's LINEAR light
 * first and converts the one mean to OKLab, which is the right definition of
 * "the colour of this region" and the wrong instrument for the residual this
 * wave exists to close. Over a balanced photograph the mean colour is nearly
 * neutral on both sides, so a body that passes every hue through and a body
 * that renders a flat grey of the same level read almost the same number. What
 * the eye sees on those two cells is a per-pixel property: Apple's macOS 27
 * dark material carries green and magenta through the plate, and vitrea's
 * carries a warm grey.
 *
 * So this module converts EVERY pixel of the masked interior to OKLab and reads
 * the population, not the mean: the mean per-pixel chroma, and the standard
 * deviations of the opponent axes `a` and `b`.
 *
 * ## The three ratios, and why the bound is declared on the first
 *
 * **(i) The chroma-to-structure ratio**, `sqrt(sd(a)² + sd(b)²) / sd(L_linear)`,
 * taken over one image's own interior. It is a per-SIDE reading, compared web
 * against native on the same cell and never against 1.
 *
 * Its purpose is that the BLUR cancels. vitrea passes about a quarter of the
 * reference's interior structure on the dark photo cells, and this wave
 * declines to touch that (W31 X3): a chroma statistic taken against the RAW
 * backdrop measures the blur and the chroma loss together, so a retention
 * fitted to close it would absorb the structure deficit as saturation and call
 * it a result. A linear blur attenuates chromatic and luminous deviations by
 * the same factor to first order, so it divides out of this ratio and does not
 * out of the raw one.
 *
 * **What it is NOT invariant to, measured rather than assumed.** A luma-only
 * darkening — every pixel's linear RGB multiplied by one scalar `c`, which
 * changes no pixel's chromaticity — scales this ratio by exactly `c^(−2/3)`.
 * OKLab's `a`, `b` and `L` are all linear in the cube roots of the LMS
 * responses, so all three scale by exactly `c^(1/3)`, while the denominator
 * here is LINEAR luma and scales by `c`. The exponent is exact, not
 * approximate, and `chroma.test.ts` pins it. The consequence for a fit is
 * stated rather than hidden: two sides at different interior levels are not
 * directly comparable on this ratio, and the level-induced part of the
 * difference is `(meanWeb / meanNative)^(2/3)`. This wave's level stop (claims
 * §5.161 §7) is what holds the two levels together so the residual is read on
 * the chroma and not on the level.
 *
 * `oklabLStdDev` is reported beside it for exactly that reason: the same
 * numerator over `sd(L_oklab)` IS exactly invariant to a luma-only darkening,
 * so the pair says which part of a movement was level and which was chroma.
 * The bound is declared on the linear-luma form, because that is the form in
 * which the residual is visible — under the OKLab-L denominator the plate
 * composite very nearly cancels, and an instrument that cancels the mechanism
 * it is measuring is not an instrument.
 *
 * **2026-09-21, the review closure (claims §5.161 §11, finding N3): the last
 * clause above is wrong and the declared form is kept for a different reason.**
 * The OKLab-L denominator does NOT cancel the plate composite. Measured on the
 * tolerance's own bed (`results/2026-09-21-w31-g0-chroma-cut/
 * closure-readings.txt`), the twin `chromaSpread / oklabLStdDev` reads web
 * against native at medians of **0.498 / 0.488 light and 0.266 / 0.491 dark**
 * — below the declared form's 0.551 / 0.514 / 0.333 / 0.584 on every one of the
 * four beds, so it separates the residual at least as sharply — and its
 * 1x-against-2x reproducibility is comparable (light 3.85 % against 4.59 %,
 * dark 8.94 % against 8.60 %). The form here stays the declared one on the
 * reason that survives measurement: its denominator is `interiorStdDev`, the
 * quantity the wave's **structure stop** bounds and the quantity the matrix has
 * carried since W7, so a fit cannot move the denominator out from under the
 * statistic. Nothing bounds `sd(L_oklab)`. The twin is a reading G3 takes
 * BESIDE `R` rather than instead of it — where the two disagree, the difference
 * is the part of a movement that lives in the level.
 *
 * **(ii) The raw ratio**: the interior's mean per-pixel chroma over the RAW
 * backdrop's under the same mask. The confounded one, kept and tabled so the
 * confound stays visible: a fit that moves only this one has moved the blur.
 *
 * **(iii) The blurred-reference ratio**: the same quantity against a backdrop
 * blurred to the side's OWN measured structure, so "how much chroma survived,
 * given how much this side blurred" is a question with an answer. A body that
 * only blurs reads 1; a body that also removes chroma reads below 1.
 *
 * The reference radius is FITTED per side and not read off the material
 * document, and that is a finding rather than a shortcut: no number in a
 * profile document is "the material's blur radius". The body samples a
 * two-component pyramid — `optics.blurSigma`'s light tap and a
 * `sizeHeavyTapSigma` heavy tap — mixed by a `kScatter` that eight leaves grade
 * by span and by backing scale, and on the macOS 27 dark document by an adopted
 * `sizeScatterScaleGain` keyed to a per-source statistic the CPU reads at run
 * time. So the radius is recovered from the pixels: the σ at which the
 * backdrop's own interior luma spread equals this side's.
 */

import { linearRgbToOklab, oklabChroma } from "../color";
import { CalibrationError } from "../errors";
import { assertComparable, linearLuminance, toLinearRgb, type CalibrationImage } from "../image";
import type { Silhouette } from "../silhouette";

/** One image's masked interior, read per pixel in OKLab. */
export interface PerPixelChromaReport {
  /** Mean over the mask of each pixel's own OKLab chroma, `hypot(a, b)`. */
  readonly meanChroma: number;
  readonly sdA: number;
  readonly sdB: number;
  /** `sqrt(sd(a)² + sd(b)²)` — the numerator of ratio (i). */
  readonly chromaSpread: number;
  /** Population sd of LINEAR relative luminance: ratio (i)'s denominator. */
  readonly luminanceStdDev: number;
  /** Population sd of OKLab `L`, the darkening-invariant denominator. */
  readonly oklabLStdDev: number;
  /**
   * Ratio (i). Absent-as-zero is impossible here because a zero denominator is
   * refused: over a solid backdrop the interior has no structure and the
   * question "how much chroma per unit structure" has no answer.
   */
  readonly chromaToStructure: number | undefined;
  readonly sampleCount: number;
}

function assertGrid(image: CalibrationImage, mask: Silhouette, context: string): void {
  if (image.width !== mask.width || image.height !== mask.height) {
    throw new CalibrationError(
      "dimension-mismatch",
      `${context}: a ${mask.width}x${mask.height} silhouette cannot index a ` +
        `${image.width}x${image.height} image.`,
    );
  }
}

/**
 * The spread below which ratio (i) is refused rather than reported.
 *
 * In linear relative luminance, and a hair above the quantisation an 8-bit
 * capture can carry: one code value at the dark end of the transfer function is
 * about 3·10⁻⁴ of linear light, so a mask whose luma sd is under 10⁻⁴ is a flat
 * region and the ratio would be a number divided by rounding. Refused, not
 * clamped — the solid-backdrop scenes are exactly this case and "this scene
 * does not measure structure" is the honest reading.
 */
export const MIN_STRUCTURE_STDDEV = 1e-4;

export function perPixelChroma(
  image: CalibrationImage,
  mask: Silhouette,
  context = "perPixelChroma",
): PerPixelChromaReport {
  assertGrid(image, mask, context);
  const linear = toLinearRgb(image);
  const luma = linearLuminance(image);

  let count = 0;
  let sumChroma = 0;
  let sumA = 0;
  let sumB = 0;
  let sumAA = 0;
  let sumBB = 0;
  let sumY = 0;
  let sumYY = 0;
  let sumL = 0;
  let sumLL = 0;
  const pixels = image.width * image.height;
  for (let i = 0; i < pixels; i += 1) {
    if ((mask.mask[i] ?? 0) === 0) continue;
    const lab = linearRgbToOklab(linear[i * 3] ?? 0, linear[i * 3 + 1] ?? 0, linear[i * 3 + 2] ?? 0);
    const y = luma[i] ?? 0;
    sumChroma += oklabChroma(lab);
    sumA += lab.a;
    sumB += lab.b;
    sumAA += lab.a * lab.a;
    sumBB += lab.b * lab.b;
    sumL += lab.L;
    sumLL += lab.L * lab.L;
    sumY += y;
    sumYY += y * y;
    count += 1;
  }
  if (count === 0) {
    throw new CalibrationError("empty-region", `${context}: the interior mask selected no pixels.`);
  }

  // Clamped at zero for `interiorLevel`'s reason: the two-pass identity can go a
  // few ulps negative on a genuinely constant region, and a negative variance
  // would surface as NaN rather than as the flat field it is.
  const sd = (sum: number, sumSquares: number): number =>
    Math.sqrt(Math.max(0, sumSquares / count - (sum / count) * (sum / count)));
  const sdA = sd(sumA, sumAA);
  const sdB = sd(sumB, sumBB);
  const chromaSpread = Math.hypot(sdA, sdB);
  const luminanceStdDev = sd(sumY, sumYY);

  return {
    meanChroma: sumChroma / count,
    sdA,
    sdB,
    chromaSpread,
    luminanceStdDev,
    oklabLStdDev: sd(sumL, sumLL),
    chromaToStructure:
      luminanceStdDev < MIN_STRUCTURE_STDDEV ? undefined : chromaSpread / luminanceStdDev,
    sampleCount: count,
  };
}

/**
 * A separable Gaussian blur of an image's linear-light RGB, edges clamped.
 *
 * Only ever applied to the BACKDROP, and only to build ratio (iii)'s reference.
 * It returns linear RGB rather than an image, because the reference is read in
 * OKLab and re-encoding to 8-bit sRGB in between would quantise the very
 * chroma the ratio is about.
 */
export function blurLinearRgb(
  image: CalibrationImage,
  sigmaPx: number,
): { readonly rgb: Float64Array; readonly width: number; readonly height: number } {
  const { width, height } = image;
  const source = toLinearRgb(image);
  if (sigmaPx <= 0) return { rgb: source, width, height };

  const radius = Math.max(1, Math.ceil(sigmaPx * 3));
  const kernel = new Float64Array(radius * 2 + 1);
  let total = 0;
  for (let k = -radius; k <= radius; k += 1) {
    const w = Math.exp(-(k * k) / (2 * sigmaPx * sigmaPx));
    kernel[k + radius] = w;
    total += w;
  }
  for (let k = 0; k < kernel.length; k += 1) kernel[k] = (kernel[k] ?? 0) / total;

  const pass = (input: Float64Array, horizontal: boolean): Float64Array => {
    const out = new Float64Array(input.length);
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        let r = 0;
        let g = 0;
        let b = 0;
        for (let k = -radius; k <= radius; k += 1) {
          const sx = horizontal ? Math.min(width - 1, Math.max(0, x + k)) : x;
          const sy = horizontal ? y : Math.min(height - 1, Math.max(0, y + k));
          const w = kernel[k + radius] ?? 0;
          const o = (sy * width + sx) * 3;
          r += w * (input[o] ?? 0);
          g += w * (input[o + 1] ?? 0);
          b += w * (input[o + 2] ?? 0);
        }
        const o = (y * width + x) * 3;
        out[o] = r;
        out[o + 1] = g;
        out[o + 2] = b;
      }
    }
    return out;
  };

  return { rgb: pass(pass(source, true), false), width, height };
}

/** Mean per-pixel chroma and linear-luma sd of a linear-RGB buffer under a mask. */
function chromaOfLinear(
  rgb: Float64Array,
  mask: Silhouette,
): { readonly meanChroma: number; readonly luminanceStdDev: number } {
  let count = 0;
  let sumChroma = 0;
  let sumY = 0;
  let sumYY = 0;
  const pixels = mask.width * mask.height;
  for (let i = 0; i < pixels; i += 1) {
    if ((mask.mask[i] ?? 0) === 0) continue;
    const r = rgb[i * 3] ?? 0;
    const g = rgb[i * 3 + 1] ?? 0;
    const b = rgb[i * 3 + 2] ?? 0;
    sumChroma += oklabChroma(linearRgbToOklab(r, g, b));
    const y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    sumY += y;
    sumYY += y * y;
    count += 1;
  }
  if (count === 0) {
    throw new CalibrationError("empty-region", "chromaOfLinear: the mask selected no pixels.");
  }
  const mean = sumY / count;
  return {
    meanChroma: sumChroma / count,
    luminanceStdDev: Math.sqrt(Math.max(0, sumYY / count - mean * mean)),
  };
}

/** Ratio (iii)'s reference: the radius, and the chroma that survives it. */
export interface BlurredReferenceReport {
  /** The σ at which the blurred backdrop's interior luma spread matches the side's. */
  readonly sigmaPx: number;
  /** Mean per-pixel chroma of the backdrop blurred at that σ, under the same mask. */
  readonly meanChroma: number;
  /** The side's own mean per-pixel chroma over this one. 1 means "only blurred". */
  readonly ratio: number;
}

/** The widest σ the search will consider, in device px. */
const MAX_REFERENCE_SIGMA_PX = 64;

/**
 * Find the Gaussian σ at which the backdrop's masked interior carries the same
 * linear-luma spread as `targetStdDev`, and read the chroma that survives it.
 *
 * Bisection on σ rather than a closed form, because the backdrop is a finite
 * raster read under an arbitrary mask and its spread is not an analytic
 * function of the radius. Monotone in σ in practice — a wider kernel removes
 * more structure — and the bisection is bounded either way rather than trusting
 * that: absent when the target spread is above the unblurred backdrop's (the
 * side has MORE structure than its own source, which no blur can produce) or
 * still below it at `MAX_REFERENCE_SIGMA_PX`.
 */
export function blurredChromaReference(
  backdrop: CalibrationImage,
  mask: Silhouette,
  targetStdDev: number,
  sideMeanChroma: number,
): BlurredReferenceReport | undefined {
  assertGrid(backdrop, mask, "blurredChromaReference");
  const at = (sigma: number): { meanChroma: number; luminanceStdDev: number } =>
    chromaOfLinear(blurLinearRgb(backdrop, sigma).rgb, mask);

  const raw = at(0);
  if (targetStdDev >= raw.luminanceStdDev) return undefined;
  if (at(MAX_REFERENCE_SIGMA_PX).luminanceStdDev > targetStdDev) return undefined;

  let low = 0;
  let high = MAX_REFERENCE_SIGMA_PX;
  let best = at(high);
  let sigma = high;
  // Twenty halvings of a 64 px bracket resolve σ to under 10⁻⁴ px, which is
  // far below any difference the 8-bit capture could express.
  for (let step = 0; step < 20; step += 1) {
    sigma = (low + high) / 2;
    best = at(sigma);
    if (best.luminanceStdDev > targetStdDev) low = sigma;
    else high = sigma;
  }
  return {
    sigmaPx: sigma,
    meanChroma: best.meanChroma,
    ratio: best.meanChroma === 0 ? Number.NaN : sideMeanChroma / best.meanChroma,
  };
}

/** The whole reading for one cell: both sides, the backdrop, and the ratios. */
export interface ChromaStructureReport {
  readonly native: PerPixelChromaReport;
  readonly web: PerPixelChromaReport;
  readonly backdrop: PerPixelChromaReport;
  /** Ratio (ii), per side: the side's mean per-pixel chroma over the RAW backdrop's. */
  readonly rawRatioNative: number | undefined;
  readonly rawRatioWeb: number | undefined;
  /** Ratio (iii), per side. Absent where the reference radius is not identifiable. */
  readonly blurredNative: BlurredReferenceReport | undefined;
  readonly blurredWeb: BlurredReferenceReport | undefined;
}

export interface ChromaStructureOptions {
  /** Compute ratio (iii). Off by default: it costs two bisections of blurs. */
  readonly blurredReference?: boolean;
}

export function chromaStructure(
  native: CalibrationImage,
  web: CalibrationImage,
  backdrop: CalibrationImage,
  mask: Silhouette,
  options: ChromaStructureOptions = {},
): ChromaStructureReport {
  assertComparable(native, web, "chromaStructure");
  assertComparable(native, backdrop, "chromaStructure");

  const nativeRead = perPixelChroma(native, mask, "chromaStructure/native");
  const webRead = perPixelChroma(web, mask, "chromaStructure/web");
  const backdropRead = perPixelChroma(backdrop, mask, "chromaStructure/backdrop");

  const raw = (side: PerPixelChromaReport): number | undefined =>
    backdropRead.meanChroma === 0 ? undefined : side.meanChroma / backdropRead.meanChroma;

  return {
    native: nativeRead,
    web: webRead,
    backdrop: backdropRead,
    rawRatioNative: raw(nativeRead),
    rawRatioWeb: raw(webRead),
    blurredNative:
      options.blurredReference === true
        ? blurredChromaReference(backdrop, mask, nativeRead.luminanceStdDev, nativeRead.meanChroma)
        : undefined,
    blurredWeb:
      options.blurredReference === true
        ? blurredChromaReference(backdrop, mask, webRead.luminanceStdDev, webRead.meanChroma)
        : undefined,
  };
}
