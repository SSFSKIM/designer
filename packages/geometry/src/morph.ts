/**
 * Parametric morph: interpolation over the whole X8 channel vector.
 *
 * §Geometry: "Morphs in v1 are **parametric only** — interpolation over
 * `{ center, size, radii, smoothing, thickness }`: every channel numeric, so
 * every channel interpolates (capsule <-> rounded rect, button <-> menu platter,
 * indicator slides)." Contour resampling and topology-changing morphs are
 * post-v1.
 *
 * The whole solver is: interpolate the channels, then re-derive the corner
 * through the same budget clamp the authoring path uses. That second half is
 * what makes the morph safe rather than merely smooth:
 *
 *  - an interpolated shape is always a shape the resolver could have produced
 *    directly, so it is inside the measured error bound by construction;
 *  - the clamp is continuous in size, so a morph that shrinks a shape through
 *    the point where the budget starts biting does not snap;
 *  - because the AUTHORED smoothing rides on the channel and the clamp is
 *    applied at derivation, shrinking a shape and growing it back recovers the
 *    original corner exactly. Clamping the channel itself would quietly destroy
 *    that.
 *
 * ## Why a morph can refuse
 *
 * The two corner references are not two points on one axis (see `shape.ts`).
 * Interpolating between them would mean blending an Apple-direct coefficient set
 * with a Figma-axis one, producing a corner that is neither and whose error is
 * unmeasured. So `morphShapes` refuses that pair in dev mode rather than
 * inventing it. v1's morph pairs share a profile; a caller who needs an
 * Apple-like corner on the interpolable axis authors
 * `profile: APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing` instead.
 */

import { lerpShapeChannels, type ShapeChannels, type ShapeFamily } from "./channels";
import { GeometryError } from "./errors";
import {
  type CornerReference,
  type ResolveOptions,
  resolveFromChannels,
  type ResolvedShape,
} from "./shape";

export interface MorphOptions extends ResolveOptions {
  /**
   * Family to tag interpolated shapes with. Defaults to `"fixed-rounded-rect"`,
   * which is what a morph between any two v1 families actually is: a capsule
   * endpoint is reproduced exactly because its radius equals its budget, which
   * drives effective smoothing to 0 on its own.
   */
  readonly family?: ShapeFamily;
}

function sharedReference(
  a: ResolvedShape,
  b: ResolvedShape,
  devMode: boolean,
): CornerReference {
  if (a.corner.reference === b.corner.reference) return a.corner.reference;
  if (!devMode) return a.corner.reference;
  throw new GeometryError(
    "corner-reference-mismatch",
    `Cannot morph a "${a.corner.reference}" corner into a "${b.corner.reference}" one: the two ` +
      "reference curves are separate fits, not two points on one axis, so blending their " +
      "coefficients would produce a corner whose error is unmeasured. Give both endpoints the " +
      "same profile — or put the Apple-like endpoint on the interpolable axis with " +
      "profile: APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing.",
  );
}

/**
 * The morph itself. `t` is not clamped: callers driving this from a spring want
 * overshoot past 1 to produce the shape the spring actually asks for, and every
 * channel is meaningful outside [0, 1] (a negative radius clamps to 0, a size
 * past the target keeps growing).
 */
export function morphShapes(
  a: ResolvedShape,
  b: ResolvedShape,
  t: number,
  options: MorphOptions = {},
): ResolvedShape {
  const devMode = options.devMode ?? true;
  const reference = sharedReference(a, b, devMode);
  const channels = lerpShapeChannels(a.channels, b.channels, t);
  return resolveFromChannels(channels, reference, options.family ?? "fixed-rounded-rect", {
    devMode,
  });
}

/** Sample a morph at `steps + 1` evenly spaced values of t, inclusive. */
export function sampleMorph(
  a: ResolvedShape,
  b: ResolvedShape,
  steps: number,
  options: MorphOptions = {},
): ResolvedShape[] {
  const out: ResolvedShape[] = [];
  for (let i = 0; i <= steps; i++) out.push(morphShapes(a, b, i / steps, options));
  return out;
}

/**
 * The channel vector a morph travels through, for callers that drive channels
 * with per-channel motion drivers rather than one shared `t`. Exposed because
 * §Motion gives position, size and radius their own springs — they do not in
 * general share a parameter, and a solver that assumed they did would be wrong
 * about interruption.
 */
export function morphChannels(
  a: ShapeChannels,
  b: ShapeChannels,
  t: number,
): ShapeChannels {
  return lerpShapeChannels(a, b, t);
}
