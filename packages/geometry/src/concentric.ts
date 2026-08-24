/**
 * The concentric resolver: a child shape derived from its parent's field as a
 * **level-set offset**.
 *
 * ## Two paths, two different bounds — and the difference is measured
 *
 * X8 rider 2 says the inner contour's accuracy IS the field's value error at
 * `d = -inset`, so `thickness` needs no bound of its own. That is exactly true
 * for one of the two ways to draw a concentric child, and only approximately
 * true for the other. The distinction is not pedantic: at inset 8 px and
 * smoothing 1.0 the two differ by 2x.
 *
 *  - **`concentricField` — the level set itself.** The child's boundary is
 *    `parentField(p) + inset == 0` by definition, so its accuracy is identically
 *    the parent field's value error at depth `inset`: <= 0.170 px for
 *    `inset <= 8`, straight off the declared bound. This is what C6 should
 *    render, and it is what makes rider 2 true as written.
 *
 *  - **`resolveConcentric` — the child as its own resolved shape.** Needed for
 *    bounds, hit-testing, Contour IR export, and any case where the child is a
 *    separate instance rather than a level set of its parent. Here a SECOND
 *    approximation enters, and it is the one §Geometry warns about: exact inward
 *    offsets of continuous-corner cubics leave the cubic family, so no member of
 *    the family is the true offset of another member. Measured deviation from the
 *    parent's true offset, worst over profile:
 *
 *      inset 1 px -> 0.033 px | inset 2 -> 0.067 | inset 4 -> 0.138 | inset 8 -> 0.291
 *
 *    which composes with the field error to 0.105 / 0.132 / 0.190 / 0.326 px.
 *    Past about inset 4 with high smoothing that exceeds the field's own budget,
 *    and the family mismatch — not the pseudo-SDF — is the dominant term.
 *
 * Concentricity governs **radii, not the curve profile** — the research
 * explicitly refuted that conflation, so the child inherits the parent's
 * smoothing and reference rather than being re-profiled.
 *
 * An inset beyond 8 px is outside the band S2 measured and would need a wider
 * sweep before being claimed; `beyondMeasuredBand` reports that rather than
 * letting a caller assume coverage it does not have.
 */

import { halfExtents, type ShapeChannels, uniformRadii, type Vec2 } from "./channels";
import { cornerBudget } from "./corner";
import { rsupnField, rsupnFieldAndGradient } from "./field";
import { fieldParams, resolveCorner, type ResolvedShape } from "./shape";

/**
 * The band S2 measured, in px. An inset past this is not covered by the declared
 * bound.
 */
export const MEASURED_BAND_PX = 8;

/**
 * Advisory floor on a derived radius, in px. Calibration-delegated: it exists so
 * a deep inset does not collapse a corner to a visible sharp point, and the
 * value that reads right against the reference is C7's to fit. Named here the
 * way §Geometry names `samplingPadding`'s advisory default.
 */
export const DEFAULT_CONCENTRIC_MIN_RADIUS = 2;

export interface ConcentricSpec {
  /** Inward offset on every side, in px. */
  readonly inset: number;
  /** Floor on the derived radius. Defaults to `DEFAULT_CONCENTRIC_MIN_RADIUS`. */
  readonly minRadius?: number;
  /** Defaults to the parent's thickness. */
  readonly thickness?: number;
}

export interface ConcentricResult {
  readonly shape: ResolvedShape;
  /** True when the radius floor bit, so the child is no longer a pure offset. */
  readonly radiusFloored: boolean;
  /** True when the inset exceeds the band S2 measured (see above). */
  readonly beyondMeasuredBand: boolean;
}

/**
 * Derive the concentric child of a resolved parent.
 *
 * The offset itself is the simple part and is exact for circular corners: an
 * inward offset by `t` shrinks each side by `2t` and each corner's radius of
 * curvature by `t`. What makes it an approximation is only the smoothed corner,
 * and that residual is precisely the parent field's value error at depth `t`.
 */
export function resolveConcentric(
  parent: ResolvedShape,
  spec: ConcentricSpec,
): ConcentricResult {
  const inset = Math.max(spec.inset, 0);
  const minRadius = spec.minRadius ?? DEFAULT_CONCENTRIC_MIN_RADIUS;

  const size: Vec2 = [
    Math.max(parent.channels.size[0] - 2 * inset, 0),
    Math.max(parent.channels.size[1] - 2 * inset, 0),
  ];
  const { halfW, halfH } = halfExtents(size);
  const childBudget = cornerBudget(halfW, halfH);

  // The offset radius, floored — then capped at the child's own budget, because
  // a floor cannot ask for more corner than the child has side to spend.
  const offsetRadius = parent.corner.radius - inset;
  const floored = Math.max(offsetRadius, minRadius);
  const radius = Math.min(floored, childBudget);
  const radiusFloored = floored > offsetRadius + 1e-12;

  // Concentricity governs radii, not the profile: smoothing and reference are
  // inherited so the child's corner is the same KIND of curve as the parent's.
  const smoothing = parent.channels.smoothing;
  const channels: ShapeChannels = {
    center: parent.channels.center,
    size,
    radii: uniformRadii(radius),
    smoothing,
    thickness: spec.thickness ?? parent.channels.thickness,
  };

  return {
    shape: {
      family: "concentric-rounded-rect",
      channels,
      corner: resolveCorner(size, radius, smoothing, parent.corner.reference),
    },
    radiusFloored,
    beyondMeasuredBand: inset > MEASURED_BAND_PX,
  };
}

/**
 * The concentric child implied by a shape's own `thickness` channel — the inner
 * surface of the material.
 *
 * This is what X8 rider 2 means by "thickness needs no separate error bound":
 * the inner contour is a level set of the same field, so its accuracy is already
 * covered by the band bound.
 */
export function resolveThicknessInnerShape(shape: ResolvedShape): ConcentricResult {
  return resolveConcentric(shape, { inset: shape.channels.thickness });
}

/**
 * The concentric child as a level set of the parent's field — the exact path.
 *
 * `parentField(p) + inset` is zero precisely where the parent field reads
 * `-inset`, so this IS the offset boundary rather than an approximation of it.
 * Its accuracy is the parent field's value error at that depth and nothing more,
 * which is the whole content of X8 rider 2.
 *
 * Points are in the parent's coordinate space; the centre is applied here, since
 * a level set of the parent has no independent centre of its own.
 */
export function concentricField(
  parent: ResolvedShape,
  inset: number,
  x: number,
  y: number,
): number {
  const p = fieldParams(parent);
  return rsupnField(p, x - parent.channels.center[0], y - parent.channels.center[1]) + inset;
}

/**
 * The same level set with its exact gradient. The offset does not change the
 * gradient at all — it is a constant shift — so the normal at the inner surface
 * is the parent field's normal, at the parent field's accuracy.
 */
export function concentricFieldAndGradient(
  parent: ResolvedShape,
  inset: number,
  x: number,
  y: number,
): { value: number; gx: number; gy: number; kink: boolean } {
  const p = fieldParams(parent);
  const s = rsupnFieldAndGradient(
    p,
    x - parent.channels.center[0],
    y - parent.channels.center[1],
  );
  return { value: s.value + inset, gx: s.gx, gy: s.gy, kink: s.kink };
}
