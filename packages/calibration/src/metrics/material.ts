/**
 * The material axis: system identification of the glass itself.
 *
 * Everything here is measured in **linear light**, converted explicitly from
 * the sRGB-encoded capture (X5). That is not a formality. A blur kernel, a rim
 * highlight and a shadow are all statements about how much light a pixel
 * receives, and averaging sRGB-encoded bytes computes a different quantity
 * whose error tracks the curvature of the transfer function — largest in the
 * dark quarter of the range, which is exactly where shadow falloff lives. C6
 * shipped a gradient that interpolated in encoded space; X5's lock is what made
 * that catchable, and it is what makes these five numbers comparable across
 * captures.
 *
 * The scenes these read are the ones the methodology mandates: an impulse and a
 * checkerboard expose the blur kernel and displacement field directly, and a
 * step edge over a known raster background makes the edge-spread function a
 * measurement rather than an inference.
 */

import { hueDifferenceDegrees, linearRgbToOklab, oklabChroma, oklabHueDegrees, type Oklab } from "../color";
import { CalibrationError } from "../errors";
import {
  assertComparable,
  clampRect,
  linearLuminance,
  toLinearRgb,
  type CalibrationImage,
  type PixelRect,
} from "../image";
import { distanceToSeeds, type Silhouette } from "../silhouette";
import { linearFit, minimiseGoldenSection, normalCdf, tryLinearFit, type LinearFit } from "../stats";

function assertSilhouetteMatches(image: CalibrationImage, silhouette: Silhouette, context: string): void {
  if (image.width !== silhouette.width || image.height !== silhouette.height) {
    throw new CalibrationError(
      "dimension-mismatch",
      `${context}: a ${silhouette.width}x${silhouette.height} silhouette cannot index a ${image.width}x${image.height} image.`,
    );
  }
}

// ---------------------------------------------------------------------------
// Blur edge spread
// ---------------------------------------------------------------------------

/** Which way the step runs, and where to look for it. */
export interface EdgeSpreadOptions {
  /**
   * The axis intensity varies along: `"x"` for a vertical edge (the profile
   * runs left to right), `"y"` for a horizontal one.
   */
  readonly axis: "x" | "y";
  /**
   * Scope the measurement to one step edge. Required in practice — a canonical
   * scene has several — and the region should span uniform background on both
   * sides of a single edge.
   */
  readonly region?: PixelRect;
}

export interface EdgeSpreadReport {
  /**
   * Gaussian-equivalent standard deviation in pixels: the σ whose error
   * function best fits the measured edge-spread function.
   */
  readonly sigmaPx: number;
  /** Where the fitted edge centre landed, in image coordinates along `axis`. */
  readonly edgeCentrePx: number;
  /**
   * RMS residual of the erf fit, as a fraction of the measured step height.
   * This is the number that says whether "Gaussian-equivalent σ" is a fair
   * description at all. On synthetic 8-bit ground truth a true Gaussian fits to
   * 4e-4..2e-3 of the step (rising with σ, as quantisation noise spreads over a
   * gentler slope), while a box kernel of the same equivalent width leaves
   * 7e-3..1.4e-2 — an order of magnitude, consistently.
   */
  readonly residualRms: number;
  /** Fitted plateaus, linear-light relative luminance. */
  readonly stepLow: number;
  readonly stepHigh: number;
  /** Samples in the averaged profile. */
  readonly profileLength: number;
}

/**
 * Estimate the effective blur width from a step edge.
 *
 * The measurement, in order: average the region along the edge direction to get
 * a 1-D edge-spread function in linear light (averaging along the edge is what
 * buys the signal-to-noise that makes an 8-bit capture usable); take the
 * first moment of its derivative as a starting guess for the edge centre and
 * the second central moment as a starting guess for σ; then refine both by
 * least squares against `low + (high - low) * Φ((x - centre)/σ)`, solving the
 * two plateau levels in closed form at each step so the search is only ever
 * two-dimensional.
 *
 * The moment estimates alone would be cheaper but are badly behaved on real
 * captures: the second moment weights the profile tails by x², so a few counts
 * of noise far from the edge inflate σ. The fit is insensitive to that, and it
 * produces the residual the report leans on.
 */
export function blurEdgeSpread(image: CalibrationImage, options: EdgeSpreadOptions): EdgeSpreadReport {
  const rect = clampRect(image, options.region, "blurEdgeSpread");
  const luminance = linearLuminance(image);
  const alongX = options.axis === "x";
  const length = alongX ? rect.width : rect.height;
  const across = alongX ? rect.height : rect.width;

  if (length < 4) {
    throw new CalibrationError(
      "empty-region",
      `blurEdgeSpread: the profile is ${length} sample(s) long — a step edge needs a region that spans it.`,
    );
  }

  const esf = new Float64Array(length);
  for (let i = 0; i < length; i += 1) {
    let sum = 0;
    for (let j = 0; j < across; j += 1) {
      const x = alongX ? rect.x + i : rect.x + j;
      const y = alongX ? rect.y + j : rect.y + i;
      sum += luminance[y * image.width + x] ?? 0;
    }
    esf[i] = sum / across;
  }

  // The step height, measured from the profile's own tails. Every residual
  // below is normalised by this rather than by the fitted step: normalising by
  // the fit would let the search drive σ to infinity, where the error function
  // is locally linear and an arbitrarily large fitted step makes any relative
  // residual look small. A profile with no step at all is refused here, since
  // "the blur width of a flat region" is not a question with an answer.
  const tail = Math.max(1, Math.floor(length * 0.1));
  let lowTail = 0;
  let highTail = 0;
  for (let i = 0; i < tail; i += 1) {
    lowTail += esf[i] ?? 0;
    highTail += esf[length - 1 - i] ?? 0;
  }
  const stepHeight = Math.abs(highTail / tail - lowTail / tail);
  // One 8-bit code at the bottom of the range is ~3e-4 of linear light, so a
  // step below 1e-4 is beneath the capture's own resolution.
  if (stepHeight < 1e-4) {
    throw new CalibrationError(
      "degenerate-fit",
      `blurEdgeSpread: the region's profile rises by ${stepHeight.toExponential(2)} of linear luminance end to end — ` +
        `there is no step edge here, so no blur width is identifiable.`,
    );
  }

  // Moment initialisation on the derivative of the profile.
  let weightSum = 0;
  let firstMoment = 0;
  for (let i = 1; i < length - 1; i += 1) {
    const derivative = ((esf[i + 1] ?? 0) - (esf[i - 1] ?? 0)) / 2;
    weightSum += derivative;
    firstMoment += derivative * i;
  }
  const centreGuess = weightSum !== 0 ? firstMoment / weightSum : (length - 1) / 2;
  let secondMoment = 0;
  for (let i = 1; i < length - 1; i += 1) {
    const derivative = ((esf[i + 1] ?? 0) - (esf[i - 1] ?? 0)) / 2;
    secondMoment += derivative * (i - centreGuess) * (i - centreGuess);
  }
  const sigmaGuess = weightSum !== 0 ? Math.sqrt(Math.abs(secondMoment / weightSum)) : length / 8;

  const model = new Float64Array(length);
  const fitAt = (centre: number, sigma: number): LinearFit | null => {
    for (let i = 0; i < length; i += 1) model[i] = normalCdf((i - centre) / sigma);
    return tryLinearFit(model, esf);
  };
  const objective = (centre: number, sigma: number): number => {
    const fit = fitAt(centre, sigma);
    if (!fit) return Number.POSITIVE_INFINITY;
    let squares = 0;
    for (let i = 0; i < length; i += 1) {
      const predicted = fit.offset + fit.slope * (model[i] ?? 0);
      const residual = predicted - (esf[i] ?? 0);
      squares += residual * residual;
    }
    return Math.sqrt(squares / length) / stepHeight;
  };

  // Coordinate descent: each parameter's residual is unimodal given the other,
  // and three rounds are past convergence for the ranges involved.
  let centre = Math.min(Math.max(centreGuess, 0), length - 1);
  let sigma = Math.min(Math.max(sigmaGuess, 0.05), length / 2);
  const sigmaCeiling = Math.max(length / 2, sigmaGuess * 4);
  for (let round = 0; round < 3; round += 1) {
    const currentSigma = sigma;
    centre = minimiseGoldenSection((value) => objective(value, currentSigma), 0, length - 1);
    const currentCentre = centre;
    sigma = minimiseGoldenSection((value) => objective(currentCentre, value), 0.05, sigmaCeiling);
  }

  const finalFit = fitAt(centre, sigma);
  if (!finalFit) {
    throw new CalibrationError(
      "degenerate-fit",
      `blurEdgeSpread: the fitted model is constant at σ=${sigma.toFixed(3)}, so the step's width is not identifiable ` +
        `from this region.`,
    );
  }

  return {
    sigmaPx: sigma,
    edgeCentrePx: (alongX ? rect.x : rect.y) + centre,
    residualRms: objective(centre, sigma),
    stepLow: finalFit.offset,
    stepHigh: finalFit.offset + finalFit.slope,
    profileLength: length,
  };
}

// ---------------------------------------------------------------------------
// Luminance transfer
// ---------------------------------------------------------------------------

/** One side's backdrop-to-rendered luminance fit, in linear light. */
export interface LuminanceTransferFit {
  /** Slope: 1 passes the backdrop through, <1 is contrast compression. */
  readonly slope: number;
  /** Offset in linear-light relative luminance: the material's own emission. */
  readonly offset: number;
  /** How much of the rendered variance the affine model explains, 0..1. */
  readonly r2: number;
  readonly sampleCount: number;
}

export interface LuminanceTransferReport {
  readonly native: LuminanceTransferFit;
  readonly web: LuminanceTransferFit;
  /** Web minus native. Dimensionless; the contrast-compression mismatch. */
  readonly slopeDelta: number;
  /** Web minus native, linear-light relative luminance. */
  readonly offsetDelta: number;
}

/** Restrict a transfer fit to the pixels the material actually covers. */
export interface LuminanceTransferOptions {
  /**
   * Sample only inside this silhouette. Strongly advised: pixels outside the
   * glass sit on the identity line and drag the fit towards slope 1.
   */
  readonly interior?: Silhouette;
}

/**
 * Fit one rendered image's luminance against the backdrop it was composited
 * over: `rendered ≈ slope * backdrop + offset`, in linear light.
 *
 * Slope and offset are the two things a glass material does to what is behind
 * it — compress its contrast, and add its own light — so an affine model is the
 * right first-order description, and `r2` is the honest report of how well that
 * description holds. A low r² on a photo backdrop is informative rather than a
 * failure: it says the material's response is not a per-pixel function of
 * backdrop luminance, which is what a blur plus a refraction displacement
 * should look like.
 */
export function fitLuminanceTransfer(
  rendered: CalibrationImage,
  background: CalibrationImage,
  options: LuminanceTransferOptions = {},
): LuminanceTransferFit {
  assertComparable(rendered, background, "fitLuminanceTransfer");
  const interior = options.interior;
  if (interior) assertSilhouetteMatches(rendered, interior, "fitLuminanceTransfer");

  const renderedLuminance = linearLuminance(rendered);
  const backgroundLuminance = linearLuminance(background);

  const xs: number[] = [];
  const ys: number[] = [];
  for (let i = 0; i < renderedLuminance.length; i += 1) {
    if (interior && (interior.mask[i] ?? 0) === 0) continue;
    xs.push(backgroundLuminance[i] ?? 0);
    ys.push(renderedLuminance[i] ?? 0);
  }
  if (xs.length === 0) {
    throw new CalibrationError("empty-region", "fitLuminanceTransfer: the interior silhouette selected no pixels.");
  }

  const fit = linearFit(xs, ys, "fitLuminanceTransfer");
  return { slope: fit.slope, offset: fit.offset, r2: fit.r2, sampleCount: fit.sampleCount };
}

/**
 * The material axis's transfer comparison: fit both sides against the same
 * backdrop and report the pair plus the gap.
 *
 * Both sides are fitted against the *same* background image, which is what the
 * shared pre-rendered raster background guarantees. Comparing two independently
 * fitted transfers is stronger than diffing the two renders directly: it
 * separates "the glass is too transparent" (slope) from "the glass is too
 * bright" (offset), which a pixel difference conflates.
 */
export function luminanceTransfer(
  nativeImage: CalibrationImage,
  webImage: CalibrationImage,
  backgroundImage: CalibrationImage,
  options: LuminanceTransferOptions = {},
): LuminanceTransferReport {
  assertComparable(nativeImage, webImage, "luminanceTransfer(native vs web)");
  const native = fitLuminanceTransfer(nativeImage, backgroundImage, options);
  const web = fitLuminanceTransfer(webImage, backgroundImage, options);
  return {
    native,
    web,
    slopeDelta: web.slope - native.slope,
    offsetDelta: web.offset - native.offset,
  };
}

// ---------------------------------------------------------------------------
// Tint response
// ---------------------------------------------------------------------------

export interface TintResponseReport {
  /** Mean OKLab of the material's interior. */
  readonly interior: Oklab;
  /** Mean OKLab of the backdrop under that same interior. */
  readonly backdrop: Oklab;
  /** Interior minus backdrop, per OKLab axis. */
  readonly deltaL: number;
  readonly deltaA: number;
  readonly deltaB: number;
  /** Chroma gained (positive) or lost (negative) passing through the material. */
  readonly chromaDelta: number;
  /**
   * Hue rotation in degrees, signed and wrapped to (-180, 180]. Meaningless at
   * near-zero chroma — read `chromaDelta` and the absolute chromas alongside.
   */
  readonly hueShiftDegrees: number;
  readonly interiorChroma: number;
  readonly backdropChroma: number;
  readonly sampleCount: number;
}

export interface TintResponseOptions {
  /** Sample only inside this silhouette; defaults to the whole image. */
  readonly interior?: Silhouette;
}

/**
 * The material's chromatic shift, in OKLab.
 *
 * Means are taken in *linear light* and converted to OKLab once, rather than
 * averaging OKLab per pixel: OKLab's cube root is non-linear, so a per-pixel
 * average would report the mean of a compressed signal, not the colour of the
 * mean light. Averaging light and then compressing is what "the colour of this
 * region" means physically, and it is what makes the number comparable between
 * a flat and a textured backdrop.
 */
export function tintResponse(
  image: CalibrationImage,
  backgroundImage: CalibrationImage,
  options: TintResponseOptions = {},
): TintResponseReport {
  assertComparable(image, backgroundImage, "tintResponse");
  const interiorMask = options.interior;
  if (interiorMask) assertSilhouetteMatches(image, interiorMask, "tintResponse");

  const imageLinear = toLinearRgb(image);
  const backgroundLinear = toLinearRgb(backgroundImage);

  let count = 0;
  let ir = 0;
  let ig = 0;
  let ib = 0;
  let br = 0;
  let bg = 0;
  let bb = 0;
  const pixels = image.width * image.height;
  for (let i = 0; i < pixels; i += 1) {
    if (interiorMask && (interiorMask.mask[i] ?? 0) === 0) continue;
    ir += imageLinear[i * 3] ?? 0;
    ig += imageLinear[i * 3 + 1] ?? 0;
    ib += imageLinear[i * 3 + 2] ?? 0;
    br += backgroundLinear[i * 3] ?? 0;
    bg += backgroundLinear[i * 3 + 1] ?? 0;
    bb += backgroundLinear[i * 3 + 2] ?? 0;
    count += 1;
  }
  if (count === 0) {
    throw new CalibrationError("empty-region", "tintResponse: the interior silhouette selected no pixels.");
  }

  const interior = linearRgbToOklab(ir / count, ig / count, ib / count);
  const backdrop = linearRgbToOklab(br / count, bg / count, bb / count);
  const interiorChroma = oklabChroma(interior);
  const backdropChroma = oklabChroma(backdrop);

  return {
    interior,
    backdrop,
    deltaL: interior.L - backdrop.L,
    deltaA: interior.a - backdrop.a,
    deltaB: interior.b - backdrop.b,
    chromaDelta: interiorChroma - backdropChroma,
    hueShiftDegrees: hueDifferenceDegrees(oklabHueDegrees(backdrop), oklabHueDegrees(interior)),
    interiorChroma,
    backdropChroma,
    sampleCount: count,
  };
}

// ---------------------------------------------------------------------------
// Radial profiles: rim and shadow
// ---------------------------------------------------------------------------

/**
 * One ring of a distance-bucketed radial profile. `value`'s meaning is stated
 * by whichever metric produced it — absolute luminance for the rim, luminance
 * *drop* for the shadow.
 */
export interface RadialProfileSample {
  /** Distance from the contour in pixels, rounded to the ring index. */
  readonly distancePx: number;
  readonly value: number;
  readonly sampleCount: number;
}

function bucketByDistance(
  distance: Float64Array,
  select: (index: number) => boolean,
  value: (index: number) => number,
  maxDistancePx: number,
): RadialProfileSample[] {
  const sums = new Float64Array(maxDistancePx + 1);
  const counts = new Float64Array(maxDistancePx + 1);
  for (let i = 0; i < distance.length; i += 1) {
    if (!select(i)) continue;
    const ring = Math.round(distance[i] ?? 0);
    if (ring < 0 || ring > maxDistancePx) continue;
    sums[ring] = (sums[ring] ?? 0) + value(i);
    counts[ring] = (counts[ring] ?? 0) + 1;
  }

  const profile: RadialProfileSample[] = [];
  for (let ring = 0; ring <= maxDistancePx; ring += 1) {
    const count = counts[ring] ?? 0;
    if (count === 0) continue;
    profile.push({ distancePx: ring, value: (sums[ring] ?? 0) / count, sampleCount: count });
  }
  return profile;
}

/** Complement of a mask — the seeds for an inward distance transform. */
function complement(mask: Uint8Array): Uint8Array {
  const out = new Uint8Array(mask.length);
  for (let i = 0; i < mask.length; i += 1) out[i] = (mask[i] ?? 0) !== 0 ? 0 : 1;
  return out;
}

export interface RimIntensityOptions {
  /** How far inward to profile, in pixels. */
  readonly maxDistancePx?: number;
}

export interface RimIntensityReport {
  /** Peak rim luminance above the interior baseline, linear light. */
  readonly peakLuminance: number;
  /** The same peak un-baselined, linear light. */
  readonly peakAbsoluteLuminance: number;
  /** Depth inside the contour at which the peak sits, in pixels. */
  readonly peakDistancePx: number;
  /** Full width at half maximum of the rim above baseline, in pixels. */
  readonly fwhmPx: number;
  /**
   * False when the profile never fell back to half maximum inside the window,
   * in which case `fwhmPx` is a lower bound rather than a measurement.
   */
  readonly fwhmResolved: boolean;
  /** Interior luminance far from the contour, linear light. */
  readonly baselineLuminance: number;
  readonly profile: readonly RadialProfileSample[];
}

/**
 * The specular rim: how bright the highlight along the contour gets, and how
 * far in it reaches.
 *
 * Profiling by *distance to the exterior* rather than along a parameterised
 * contour is deliberate. The rim is a function of depth into the material, and
 * a distance transform gives that depth for every interior pixel at once —
 * including in the corners, where a contour-normal walk is exactly where it is
 * least well defined. Rings are averaged, so a rim that is bright on one side
 * and absent on the other reads as a moderate peak; the per-ring
 * `sampleCount` is reported so an implausibly small ring is visible.
 */
export function rimIntensity(
  image: CalibrationImage,
  silhouette: Silhouette,
  options: RimIntensityOptions = {},
): RimIntensityReport {
  assertSilhouetteMatches(image, silhouette, "rimIntensity");
  const maxDistancePx = options.maxDistancePx ?? 12;
  const luminance = linearLuminance(image);
  const depth = distanceToSeeds(complement(silhouette.mask), silhouette.width, silhouette.height);

  const profile = bucketByDistance(
    depth,
    (i) => (silhouette.mask[i] ?? 0) !== 0,
    (i) => luminance[i] ?? 0,
    maxDistancePx,
  );
  if (profile.length === 0) {
    throw new CalibrationError("empty-region", "rimIntensity: the silhouette has no interior pixels.");
  }

  // The deepest available ring is the interior the rim sits on top of.
  const baseline = profile[profile.length - 1]?.value ?? 0;

  let peakIndex = 0;
  let peakAbove = Number.NEGATIVE_INFINITY;
  for (let i = 0; i < profile.length; i += 1) {
    const above = (profile[i]?.value ?? 0) - baseline;
    if (above > peakAbove) {
      peakAbove = above;
      peakIndex = i;
    }
  }
  const peakSample = profile[peakIndex];
  const half = peakAbove / 2;

  const crossing = (from: number, step: number): { at: number; resolved: boolean } => {
    let previousDistance = profile[from]?.distancePx ?? 0;
    let previousAbove = (profile[from]?.value ?? 0) - baseline;
    for (let i = from + step; i >= 0 && i < profile.length; i += step) {
      const distance = profile[i]?.distancePx ?? 0;
      const above = (profile[i]?.value ?? 0) - baseline;
      if (above <= half) {
        const span = previousAbove - above;
        const t = span > 0 ? (previousAbove - half) / span : 0;
        return { at: previousDistance + (distance - previousDistance) * t, resolved: true };
      }
      previousDistance = distance;
      previousAbove = above;
    }
    return { at: previousDistance, resolved: false };
  };

  const inner = crossing(peakIndex, 1);
  const outer = crossing(peakIndex, -1);
  // Peak at the outermost ring: the outward half of the rim is off-image, so
  // report the inward half doubled rather than pretend to a symmetric measure.
  const fwhm = peakIndex === 0 ? 2 * Math.abs(inner.at - (peakSample?.distancePx ?? 0)) : Math.abs(inner.at - outer.at);

  return {
    peakLuminance: peakAbove,
    peakAbsoluteLuminance: peakSample?.value ?? 0,
    peakDistancePx: peakSample?.distancePx ?? 0,
    fwhmPx: fwhm,
    fwhmResolved: inner.resolved && (peakIndex === 0 || outer.resolved),
    baselineLuminance: baseline,
    profile,
  };
}

export interface ShadowFalloffOptions {
  /** How far outward to profile, in pixels. */
  readonly maxDistancePx?: number;
}

export interface ShadowFalloffReport {
  /** Deepest mean darkening against the background, linear-light luminance. */
  readonly peakDarkening: number;
  /** Distance outside the contour at which that peak sits, in pixels. */
  readonly peakDistancePx: number;
  /**
   * Distance beyond the peak at which the darkening has fallen to 1/e of it —
   * the exponential decay length, in pixels.
   */
  readonly decayLengthPx: number;
  /**
   * False when the darkening never reached 1/e inside the window, making
   * `decayLengthPx` a lower bound. A shadow wider than the window, or a
   * capture region that clips it, both look like this.
   */
  readonly decayResolved: boolean;
  /** `value` is the mean luminance *drop* against the background, per ring. */
  readonly profile: readonly RadialProfileSample[];
}

/**
 * The exterior shadow: how much darker than the bare background the surround
 * is, as a function of distance outside the contour.
 *
 * Measured as a difference against the known background rather than as an
 * absolute luminance, because the canonical scenes put the same surface over
 * light solids, dark solids and photos — the absolute figure would be a
 * property of the scene, and the difference is a property of the material.
 * 1/e is the reported decay point because an ambient-occlusion-shaped falloff
 * is approximately exponential; the profile is returned so a caller who
 * disbelieves that can fit their own model.
 */
export function shadowFalloff(
  image: CalibrationImage,
  silhouette: Silhouette,
  backgroundImage: CalibrationImage,
  options: ShadowFalloffOptions = {},
): ShadowFalloffReport {
  assertComparable(image, backgroundImage, "shadowFalloff");
  assertSilhouetteMatches(image, silhouette, "shadowFalloff");
  const maxDistancePx = options.maxDistancePx ?? 24;

  const luminance = linearLuminance(image);
  const backgroundLuminance = linearLuminance(backgroundImage);
  const outward = distanceToSeeds(silhouette.mask, silhouette.width, silhouette.height);

  const profile = bucketByDistance(
    outward,
    (i) => (silhouette.mask[i] ?? 0) === 0,
    (i) => (backgroundLuminance[i] ?? 0) - (luminance[i] ?? 0),
    maxDistancePx,
  );
  if (profile.length === 0) {
    throw new CalibrationError(
      "empty-region",
      "shadowFalloff: the silhouette covers the whole image, so there is no exterior to profile.",
    );
  }

  let peakIndex = 0;
  let peak = Number.NEGATIVE_INFINITY;
  for (let i = 0; i < profile.length; i += 1) {
    const value = profile[i]?.value ?? 0;
    if (value > peak) {
      peak = value;
      peakIndex = i;
    }
  }
  const peakDistance = profile[peakIndex]?.distancePx ?? 0;
  const target = peak / Math.E;

  let decayDistance = profile[profile.length - 1]?.distancePx ?? peakDistance;
  let resolved = false;
  let previousDistance = peakDistance;
  let previousValue = peak;
  for (let i = peakIndex + 1; i < profile.length; i += 1) {
    const distance = profile[i]?.distancePx ?? 0;
    const value = profile[i]?.value ?? 0;
    if (value <= target) {
      const span = previousValue - value;
      const t = span > 0 ? (previousValue - target) / span : 0;
      decayDistance = previousDistance + (distance - previousDistance) * t;
      resolved = true;
      break;
    }
    previousDistance = distance;
    previousValue = value;
  }

  return {
    peakDarkening: peak,
    peakDistancePx: peakDistance,
    decayLengthPx: decayDistance - peakDistance,
    decayResolved: resolved,
    profile,
  };
}
