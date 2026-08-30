/**
 * The shadow axis: what the material does to the backdrop it does *not* cover.
 *
 * ## Why this is an axis and not a material sub-metric
 *
 * Through schema 4 the exterior shadow was one radial number on the material
 * axis, profiled outward from the *extracted* silhouette — which, on a reference
 * whose shadow the extractor had already swallowed, started beyond the shadow
 * and measured the bare backdrop. The active-pose bed made the shadow the
 * largest unmodelled facet in the project (claims §5.11: a downward-offset
 * occlusion covering 8.5–29.6% of the canvas, which vitrea renders as exactly
 * zero), and Decision Log 15 ruled it its own measured axis, fitted like any
 * other facet. So it is profiled from the **declared** contour, in four
 * directions, on both sides, with the same estimator.
 *
 * ## The quantity: occlusion, not darkening
 *
 * The reference's shadow is multiplicative — it removes a fraction of the light
 * the backdrop was sending, so the same shadow is a large absolute drop over a
 * bright backdrop and an invisible one over a dark one. Every directional figure
 * here is therefore normalised: `occlusion = (backdrop − rendered) / backdrop`,
 * in linear light. That makes a shadow's *description* comparable across the
 * five backdrops the bed puts the same surface over, which an absolute
 * darkening is not.
 *
 * The normalisation has an analytic floor. Over `dark-solid` (backdrop
 * luminance 0.0117) and `impulse` (0.0037) there is no light to remove, so no
 * shadow of any strength is recoverable — the axis reports its backdrop support
 * and leaves every normalised field **absent**, which is the honest reading and
 * not a zero. `meanDeparture` stays present on every scene because an absolute
 * difference is defined even where a ratio is not, and it is the figure claims
 * §5.11 quoted.
 *
 * ## No thresholds
 *
 * Two constants below select *where a measurement is possible* — the backdrop
 * level beneath which a ratio is arithmetic on no information, and the occlusion
 * level beneath which a ring is indistinguishable from an unshadowed one. They
 * are conditions on the estimator, not bounds on fidelity: nothing here decides
 * whether a shadow matches, and the axis has no adopted bound at all until the
 * cascade fits one after W8.
 */

import { CalibrationError } from "../errors";
import { assertComparable, linearLuminance, type CalibrationImage } from "../image";
import type { ComponentRegion } from "../component-region";

/** Which side of the component a ring sample sits on. */
export const SHADOW_DIRECTIONS = ["above", "below", "left", "right"] as const;
export type ShadowDirection = (typeof SHADOW_DIRECTIONS)[number];

/**
 * Backdrop luminance beneath which the multiplicative normalisation is not
 * identifiable, in linear light.
 *
 * 0.05 is a measured separation on this bed rather than a round number: it
 * places `light-solid` (0.891), the checkerboard's light squares (1.0), `photo`
 * (0.214) and `mid-dark-solid` (0.0595) inside the measurable set and
 * `dark-solid` (0.0117) and `impulse` (0.0037) outside it, which is exactly the
 * split the physics implies. At the floor itself a 1% occlusion is about a third
 * of an 8-bit code, so a per-pixel reading there is beneath the capture's
 * resolution and only the ring means below are meaningful.
 */
export const DEFAULT_SHADOW_BACKDROP_FLOOR = 0.05;

/**
 * The occlusion a ring must reach to count as shadowed, as a fraction of the
 * backdrop's own level.
 *
 * 1% is the smallest departure that survives the capture at the backdrop floor
 * once a ring's samples are averaged. It is what "the departure falls below
 * threshold" in the extent definition means, and it is deliberately expressed in
 * the normalised quantity so that the same shadow yields the same extent over
 * every backdrop bright enough to show it.
 */
export const DEFAULT_SHADOW_OCCLUSION_THRESHOLD = 0.01;

/** Fewer samples than this in a ring and the ring is skipped, not averaged. */
const DEFAULT_MIN_RING_SAMPLES = 4;

/**
 * Fraction of the exterior whose backdrop must clear the floor before any
 * normalised figure is reported.
 */
const DEFAULT_MIN_BACKDROP_SUPPORT = 0.1;

/**
 * Fraction of the supported exterior that must carry occlusion above the
 * threshold before the mass centroid is reported.
 *
 * Below it the centroid describes the backdrop's own support pattern rather than
 * the shadow: measured on `checkerboard__capsule-button__rest`, vitrea's 3 px
 * edge halo covers 1.7% of the supported exterior and its centroid lands 39 px
 * from the component's centre — an artefact of which checkerboard squares happen
 * to be light — where the reference's shadow covers 34% and lands 16 px below
 * centre, which is the real displacement.
 */
const DEFAULT_MIN_CENTROID_MASS_FRACTION = 0.1;

export interface ShadowFieldOptions {
  readonly backdropFloor?: number;
  readonly occlusionThreshold?: number;
  readonly minRingSamples?: number;
  readonly minBackdropSupport?: number;
  readonly minCentroidMassFraction?: number;
}

/** One ring of the occlusion profile, indexed by distance from the contour. */
export interface ShadowProfileSample {
  /** Inner edge of the one-pixel ring, in pixels outside the declared contour. */
  readonly distancePx: number;
  /** Mean occlusion over the ring's supported pixels, 0..1. */
  readonly occlusion: number;
  readonly sampleCount: number;
}

/**
 * One side's shadow, measured outside the declared component region.
 *
 * Optional fields mean **not identifiable on this scene**, never zero:
 *
 *   - everything normalised is absent when the backdrop cannot support a ratio
 *     (`backdropSupport` says how far short it fell);
 *   - `offset*` is absent when no direction reached the occlusion threshold at
 *     all, which is what a renderer that draws no shadow produces — an undefined
 *     displacement, recorded as undefined rather than as (0, 0);
 *   - `centroidOffset*` is absent when too little of the exterior is occluded
 *     for a mass centroid to describe the shadow rather than the backdrop;
 *   - `falloffLength*` is absent when fewer than three rings clear the threshold
 *     beyond the peak, or when the profile does not decay.
 */
export interface ShadowFieldReport {
  /** Pixels outside the declared region — the population every figure is over. */
  readonly exteriorAreaPx: number;
  /** Mean backdrop luminance over that exterior, linear light. */
  readonly backdropMeanLuminance: number;
  /** Fraction of the exterior whose backdrop clears the floor, 0..1. */
  readonly backdropSupport: number;
  /**
   * Mean `backdrop − rendered` over the whole exterior, linear light, signed.
   * Absolute, so it is defined over every backdrop; negative means the side
   * *brightens* its surround on balance.
   */
  readonly meanDeparture: number;
  /** Deepest ring-mean occlusion, and where it sits. */
  readonly strengthPeak?: number;
  readonly strengthPeakDistancePx?: number;
  readonly extentAbovePx?: number;
  readonly extentBelowPx?: number;
  readonly extentLeftPx?: number;
  readonly extentRightPx?: number;
  /** Displacement implied by the reach: half the difference of opposing extents. */
  readonly offsetXPx?: number;
  readonly offsetYPx?: number;
  /** Occlusion-mass centroid minus the component's centre, device px. */
  readonly centroidOffsetXPx?: number;
  readonly centroidOffsetYPx?: number;
  /** Exponential decay length fitted beyond the peak, in pixels. */
  readonly falloffLengthPx?: number;
  /** RMS fit residual as a fraction of the peak — how exponential it really is. */
  readonly falloffResidual?: number;
  /** The ring means the figures above are read off. */
  readonly profile: readonly ShadowProfileSample[];
  /** Why the normalised block is absent, when it is. */
  readonly unmeasurableReason?: string;
}

/** Sector of the exterior a pixel belongs to, by its own aspect-normalised angle. */
function directionOf(region: ComponentRegion, x: number, y: number): ShadowDirection {
  // Normalising by the component's own half-extents puts the sector boundaries
  // on the diagonals of its bounding box, so "beside" a wide capsule is the
  // region past its caps rather than a sliver level with its flat edges — which
  // an unnormalised angle would give, leaving the cap surrounds in no sector.
  const nx = (x + 0.5 - region.centreX) / region.halfWidth;
  const ny = (y + 0.5 - region.centreY) / region.halfHeight;
  if (Math.abs(nx) >= Math.abs(ny)) return nx < 0 ? "left" : "right";
  return ny < 0 ? "above" : "below";
}

/**
 * How far the departure reaches in one direction, in pixels from the declared
 * contour.
 *
 * The outermost ring of a qualifying *pair*, rather than the first crossing.
 * Both guards are earned: the innermost ring is where each side's own edge
 * lives, and it can read negative — the reference's rim spills one pixel past
 * the contour on `photo__capsule-button__rest` and reads −0.276 there, which a
 * first-crossing rule would report as a shadow of zero extent — while requiring
 * two consecutive qualifying rings keeps one noisy far ring from inventing
 * reach. A side with no shadow reads 0, which is a measurement.
 */
function extentOf(means: readonly (number | undefined)[], threshold: number): number {
  let extent = 0;
  let previousQualified = true;
  for (let ring = 0; ring < means.length; ring += 1) {
    const mean = means[ring];
    if (mean === undefined) continue;
    const qualified = mean >= threshold;
    if (qualified && previousQualified) extent = ring + 1;
    previousQualified = qualified;
  }
  return extent;
}

/** Least-squares fit of `ln(occlusion)` against distance, from the peak outward. */
function fitExponentialDecay(
  profile: readonly ShadowProfileSample[],
  peakIndex: number,
  threshold: number,
): { readonly lengthPx: number; readonly residual: number } | undefined {
  const points = profile.slice(peakIndex).filter((sample) => sample.occlusion > threshold);
  if (points.length < 3) return undefined;

  let sumX = 0;
  let sumY = 0;
  for (const point of points) {
    sumX += point.distancePx;
    sumY += Math.log(point.occlusion);
  }
  const meanX = sumX / points.length;
  const meanY = sumY / points.length;
  let covariance = 0;
  let variance = 0;
  for (const point of points) {
    const dx = point.distancePx - meanX;
    covariance += dx * (Math.log(point.occlusion) - meanY);
    variance += dx * dx;
  }
  if (variance === 0) return undefined;
  const slope = covariance / variance;
  // A profile that grows outward is not a falloff, and 1/slope would be a
  // confident number describing something this fit does not model.
  if (slope >= 0) return undefined;

  const intercept = meanY - slope * meanX;
  const peak = profile[peakIndex]?.occlusion ?? 0;
  let squares = 0;
  for (const point of points) {
    const predicted = Math.exp(intercept + slope * point.distancePx);
    squares += (predicted - point.occlusion) ** 2;
  }
  return {
    lengthPx: -1 / slope,
    residual: peak > 0 ? Math.sqrt(squares / points.length) / peak : Number.POSITIVE_INFINITY,
  };
}

/**
 * Measure one render's occlusion of its own backdrop, outside the declared
 * component region.
 *
 * Both sides of a cell are measured by this same function over the same region
 * and the same backdrop, so "the gap" is a difference of like quantities — the
 * rule the material axis learned in C9a and the reason its sub-metrics are
 * two-sided.
 */
export function shadowField(
  image: CalibrationImage,
  background: CalibrationImage,
  region: ComponentRegion,
  options: ShadowFieldOptions = {},
): ShadowFieldReport {
  assertComparable(image, background, "shadowField");
  const { width, height } = image;
  if (region.silhouette.width !== width || region.silhouette.height !== height) {
    throw new CalibrationError(
      "dimension-mismatch",
      `shadowField: a ${region.silhouette.width}x${region.silhouette.height} region cannot bound a ` +
        `${width}x${height} capture.`,
    );
  }

  const floor = options.backdropFloor ?? DEFAULT_SHADOW_BACKDROP_FLOOR;
  const threshold = options.occlusionThreshold ?? DEFAULT_SHADOW_OCCLUSION_THRESHOLD;
  const minRingSamples = options.minRingSamples ?? DEFAULT_MIN_RING_SAMPLES;
  const minSupport = options.minBackdropSupport ?? DEFAULT_MIN_BACKDROP_SUPPORT;
  const minMass = options.minCentroidMassFraction ?? DEFAULT_MIN_CENTROID_MASS_FRACTION;

  const rendered = linearLuminance(image);
  const backdrop = linearLuminance(background);

  let exteriorCount = 0;
  let supportedCount = 0;
  let backdropSum = 0;
  let departureSum = 0;
  let maxRing = 0;
  for (let i = 0; i < rendered.length; i += 1) {
    if ((region.silhouette.mask[i] ?? 0) !== 0) continue;
    exteriorCount += 1;
    const base = backdrop[i] ?? 0;
    backdropSum += base;
    departureSum += base - (rendered[i] ?? 0);
    if (base >= floor) {
      supportedCount += 1;
      const ring = Math.floor(region.signedDistancePx[i] ?? 0);
      if (ring > maxRing) maxRing = ring;
    }
  }
  if (exteriorCount === 0) {
    throw new CalibrationError(
      "empty-region",
      "shadowField: the declared region covers the whole capture, so there is no exterior to profile.",
    );
  }

  const base: ShadowFieldReport = {
    exteriorAreaPx: exteriorCount,
    backdropMeanLuminance: backdropSum / exteriorCount,
    backdropSupport: supportedCount / exteriorCount,
    meanDeparture: departureSum / exteriorCount,
    profile: [],
  };
  if (base.backdropSupport < minSupport) {
    return {
      ...base,
      unmeasurableReason:
        `only ${(base.backdropSupport * 100).toFixed(1)}% of the exterior has a backdrop above ` +
        `${floor} linear luminance, so an occlusion ratio is not identifiable here — a shadow removes a ` +
        `fraction of the light behind it, and over this backdrop there is none to remove.`,
    };
  }

  // Ring means, pooled over the whole exterior and again per direction. Rings
  // are unit-wide and indexed by the floor of the exact distance to the declared
  // contour, so ring 0 is the first pixel outside it.
  const ringSum = new Float64Array(maxRing + 1);
  const ringCount = new Float64Array(maxRing + 1);
  const directionSum = new Map<ShadowDirection, Float64Array>();
  const directionCount = new Map<ShadowDirection, Float64Array>();
  for (const direction of SHADOW_DIRECTIONS) {
    directionSum.set(direction, new Float64Array(maxRing + 1));
    directionCount.set(direction, new Float64Array(maxRing + 1));
  }

  let mass = 0;
  let massCount = 0;
  let massX = 0;
  let massY = 0;
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = y * width + x;
      if ((region.silhouette.mask[i] ?? 0) !== 0) continue;
      const level = backdrop[i] ?? 0;
      if (level < floor) continue;
      const occlusion = (level - (rendered[i] ?? 0)) / level;
      const ring = Math.floor(region.signedDistancePx[i] ?? 0);
      if (ring < 0 || ring > maxRing) continue;

      ringSum[ring] = (ringSum[ring] ?? 0) + occlusion;
      ringCount[ring] = (ringCount[ring] ?? 0) + 1;
      const direction = directionOf(region, x, y);
      const sums = directionSum.get(direction);
      const counts = directionCount.get(direction);
      if (sums && counts) {
        sums[ring] = (sums[ring] ?? 0) + occlusion;
        counts[ring] = (counts[ring] ?? 0) + 1;
      }

      const weight = occlusion - threshold;
      if (weight > 0) {
        mass += weight;
        massCount += 1;
        massX += weight * (x + 0.5);
        massY += weight * (y + 0.5);
      }
    }
  }

  const meansOf = (sums: Float64Array, counts: Float64Array): (number | undefined)[] =>
    [...counts].map((count, ring) =>
      count >= minRingSamples ? (sums[ring] ?? 0) / count : undefined,
    );

  const pooled = meansOf(ringSum, ringCount);
  const profile: ShadowProfileSample[] = [];
  for (let ring = 0; ring <= maxRing; ring += 1) {
    const mean = pooled[ring];
    if (mean === undefined) continue;
    profile.push({ distancePx: ring, occlusion: mean, sampleCount: ringCount[ring] ?? 0 });
  }
  if (profile.length === 0) {
    return {
      ...base,
      unmeasurableReason:
        `no ring outside the declared region holds ${minRingSamples} supported samples, so no ` +
        `occlusion profile exists.`,
    };
  }

  let peakIndex = 0;
  for (let i = 1; i < profile.length; i += 1) {
    if ((profile[i]?.occlusion ?? 0) > (profile[peakIndex]?.occlusion ?? 0)) peakIndex = i;
  }
  const peak = profile[peakIndex] as ShadowProfileSample;

  const extents = new Map<ShadowDirection, number>();
  for (const direction of SHADOW_DIRECTIONS) {
    const sums = directionSum.get(direction);
    const counts = directionCount.get(direction);
    extents.set(direction, sums && counts ? extentOf(meansOf(sums, counts), threshold) : 0);
  }
  const above = extents.get("above") ?? 0;
  const below = extents.get("below") ?? 0;
  const left = extents.get("left") ?? 0;
  const right = extents.get("right") ?? 0;
  const reached = Math.max(above, below, left, right) > 0;

  const decay = fitExponentialDecay(profile, peakIndex, threshold);
  const massFraction = supportedCount > 0 ? massCount / supportedCount : 0;

  return {
    ...base,
    strengthPeak: peak.occlusion,
    strengthPeakDistancePx: peak.distancePx,
    extentAbovePx: above,
    extentBelowPx: below,
    extentLeftPx: left,
    extentRightPx: right,
    ...(reached
      ? { offsetXPx: (right - left) / 2, offsetYPx: (below - above) / 2 }
      : {}),
    ...(mass > 0 && massFraction >= minMass
      ? {
          centroidOffsetXPx: massX / mass - region.centreX,
          centroidOffsetYPx: massY / mass - region.centreY,
        }
      : {}),
    ...(decay === undefined ? {} : { falloffLengthPx: decay.lengthPx, falloffResidual: decay.residual }),
    profile,
  };
}
