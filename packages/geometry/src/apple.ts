/**
 * Apple's actual `.continuous` corner — the curve `profile: "continuous"` is fit
 * against.
 *
 * S2's most consequential finding was not the error bound. It was that the bound
 * is **smaller than the distance between the reference contour family and
 * Apple's actual corner**: the pseudo-SDF is not the limiting factor on
 * geometric fidelity, the choice of reference curve is. Routing
 * `profile: "continuous"` through the Figma family at its best-matching
 * smoothing costs 6.4x the value error of fitting the same field directly to
 * Apple's curve (0.670 px vs 0.104 px), which is why Decision Log #20 rebased
 * the seed onto a direct fit and rejected the intermediate family.
 *
 * ## Provenance
 *
 * The control points are a CGPath dump of
 * `RoundedRectangle(cornerRadius:style:.continuous)` on macOS 26, normalized by
 * the corner radius. The edge reach is not reverse-engineered folklore: Apple
 * publishes it as `+[CALayer cornerCurveExpansionFactor:]` for
 * `kCACornerCurveContinuous`. Every derived property is recomputed from these
 * numbers alone in `test/apple.test.ts`, so the dump is checked rather than
 * trusted:
 *
 *   - three cubics per corner, no arcs and no quadratics;
 *   - the MIDDLE cubic IS a circular arc — its handle length matches the exact
 *     arc-as-cubic identity `(4/3)*tan(sweep/4)*R` to 1.5e-7, at radius
 *     0.931253 r, centre 0.950002 r, sweep 50.0000 degrees. (The handle identity
 *     is the real proof; radius and centre alone could be a coincidence of
 *     symmetry.);
 *   - G2 — zero curvature — where the corner meets the straight edge. That is
 *     the join that reads visually, and Apple gets it right;
 *   - a **2.4532-degree tangent break** at both shoulder/arc joins. Apple's own
 *     path is not even G1 there.
 *
 * That last number is the most useful one in the whole spike, because it
 * calibrates the gradient budget: the curve vitrea is chasing carries a
 * 2.45-degree normal discontinuity of its own, and the field's worst rim-band
 * gradient error is 1.55 degrees. Chasing further precision on the normal is
 * chasing an artifact of the target.
 */

import {
  type Contour,
  type ContourSegment,
  type Point,
  ringFromCorner,
  translateSegment,
} from "./contour";
import type { CornerConstruction } from "./corner";
import type { Vec2 } from "./channels";

/** Apple's published corner-curve expansion factor for `.continuous`. */
export const APPLE_REACH = 1.52866495;

/**
 * The smoothing seed for `profile: "continuous"`.
 *
 * Expressed on the same scale as the `smoothing` channel — a corner of reach
 * `(1 + s) * r` — so the two references describe their corners in the same
 * units even though only one of them has a free smoothing parameter. This is
 * the value the public `profile: "continuous"` sugar resolves to; it is
 * internal and calibration-refinable, seeded here from S2's direct fit.
 */
export const APPLE_CONTINUOUS_SMOOTHING_SEED = APPLE_REACH - 1;

/**
 * Radius above which Apple can no longer honour the reach and the corner warps:
 * `reach * r` must fit in half the side. Apple's budget policy — clamp the
 * radius — differs from the reference family's, which clamps smoothing. Shapes
 * above this ratio are not comparable to Apple and C7 should measure them
 * separately or exclude them from fidelity claims.
 */
export const APPLE_SATURATION_RADIUS_RATIO = 1 / (2 * APPLE_REACH);

/**
 * The Figma smoothing that best reproduces Apple's corner — one of the spec's
 * named delegated unknowns, answered numerically ahead of C7.
 *
 * Informational now that the Apple-direct fit is what `profile: "continuous"`
 * renders, but recorded because the widely cited "Figma smoothing 0.6 = iOS" is
 * measurably wrong: 0.66 is nearly 2x closer. It is also the escape hatch for a
 * caller who needs an Apple-like corner ON the interpolable smoothing axis (see
 * `morph.ts` on why the two references do not morph into each other).
 */
export const APPLE_BEST_FIGMA_SMOOTHING = {
  radiusFixed: { smoothing: 0.66, hausdorffPerR: 0.00196015 },
  radiusFree: { smoothing: 0.6566210937500002, radiusScale: 0.99875, hausdorffPerR: 0.00174916 },
} as const;

/**
 * One corner, normalized by r, in a frame whose origin is the box corner and
 * whose interior lies toward +x/+y. Listed in the dump's own order: from the
 * vertical edge round to the horizontal edge.
 */
export const APPLE_CORNER_DUMP: readonly (readonly [number, number])[] = [
  [0, 1.52866495], // on the vertical edge
  [0, 1.08849001],
  [0, 0.86840701],
  [0.0749114, 0.63149399], // shoulder -> arc join
  [0.16906001, 0.37282401],
  [0.37282401, 0.16906001],
  [0.63149399, 0.0749114], // arc -> shoulder join
  [0.86840701, 0],
  [1.08849001, 0],
  [1.52866495, 0], // on the horizontal edge
];

/**
 * Top-right corner in the centred, y-up frame, emitted CLOCKWISE (top edge to
 * right edge) to match the ring builder's orientation. The dump runs the other
 * way round the corner, so it is reversed here.
 */
function appleTopRightCorner(halfW: number, halfH: number, radius: number): ContourSegment[] {
  const pts: Point[] = APPLE_CORNER_DUMP.map(([u, w]) => ({
    x: halfW - u * radius,
    y: halfH - w * radius,
  }));
  pts.reverse();
  const out: ContourSegment[] = [];
  for (let i = 0; i + 3 < pts.length; i += 3) {
    out.push({
      kind: "cubic",
      p0: pts[i] as Point,
      p1: pts[i + 1] as Point,
      p2: pts[i + 2] as Point,
      p3: pts[i + 3] as Point,
    });
  }
  return out;
}

export interface AppleContour extends Contour {
  /**
   * True when the requested radius exceeded what Apple's reach can fit. The real
   * thing warps past that point in a way this construction does not reproduce,
   * so it is reported rather than silently mismodelled.
   */
  readonly saturated: boolean;
}

/**
 * Apple's continuous-corner rounded rectangle. There is no smoothing parameter —
 * Apple's curve has none, which is exactly the point.
 */
export function buildAppleContour(
  halfW: number,
  halfH: number,
  radius: number,
  center: Vec2 = [0, 0],
): AppleContour {
  const budget = Math.min(halfW, halfH);
  const r = Math.max(0, Math.min(radius, budget / APPLE_REACH));
  const saturated = radius > budget / APPLE_REACH + 1e-12;
  const reach = APPLE_REACH * r;

  const local = ringFromCorner(halfW, halfH, reach, appleTopRightCorner(halfW, halfH, r));
  const segments =
    center[0] === 0 && center[1] === 0
      ? local
      : local.map((s) => translateSegment(s, center[0], center[1]));

  // a/b/c/d are the reference family's cubic offset scalars and have no Apple
  // analogue; the arc measure is Apple's own measured 50 degrees.
  const corner: CornerConstruction = {
    radius: r,
    smoothingEff: APPLE_CONTINUOUS_SMOOTHING_SEED,
    reach,
    a: 0,
    b: 0,
    c: 0,
    d: 0,
    arcSectionLength: 0,
    arcMeasure: (50 * Math.PI) / 180,
    budget,
  };

  return { segments, closed: true, winding: "clockwise-y-up", corner, center, saturated };
}
