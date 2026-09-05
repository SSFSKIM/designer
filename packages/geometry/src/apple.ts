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
  buildReferenceContour,
  type Contour,
  type ContourSegment,
  type Point,
  ringFromCorner,
  translateSegment,
} from "./contour";
import { type CornerConstruction, resolveCornerConstruction } from "./corner";
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
 * The radius ratio at which Apple's published reach exactly fills the side:
 * `APPLE_REACH * r == min(halfW, halfH)`. It is the name of a CROSSING, not of a
 * clamp on the radius.
 *
 * The comment this replaces said Apple clamps the radius above the ratio and
 * that shapes above it are not comparable to Apple at all. W20 G0 measured that
 * on a ten-rung native ladder and it is wrong in the direction it asserts
 * (claims §5.84 §4–§6): Core Animation states the requested radius unclamped at
 * every rung, and on the pixels Apple KEEPS the radius and compresses the
 * shoulder, `reach = min(APPLE_REACH * r, budget)`, within the grid's 0.5 px
 * floor on both boxes and both backgrounds. That is the reference family's own
 * budget clamp, so above this ratio the Apple reference resolves through
 * `resolveCornerConstruction` at the effective smoothing `reach / r - 1`, which
 * reaches exactly 0 at the capsule limit and draws the true stadium Apple draws
 * there. Shapes above the ratio are comparable to Apple, and the ratio's job is
 * to say which of the two constructions a corner is on.
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
   * True when the requested radius is large enough that Apple's published reach
   * no longer fits the side, so THE SHOULDER IS COMPRESSED: the radius is kept
   * and the reach is pulled back to the corner's budget. It was previously the
   * flag on a radius clamp; W20 G0 measured the clamp to be the wrong policy
   * (claims §5.84), and the flag now names which of the two constructions built
   * the contour rather than warning that the contour is mismodelled.
   */
  readonly saturated: boolean;
}

/**
 * Apple's continuous-corner rounded rectangle. There is no smoothing parameter —
 * Apple's curve has none, which is exactly the point.
 *
 * Two constructions, and the crossing between them is `APPLE_SATURATION_RADIUS_
 * RATIO`. Below it the corner is S2's Apple-direct dump at the requested radius
 * with the published reach. Above it the reach would overflow the side — Apple's
 * own curve there self-intersects and leaves a straight spur, which is what the
 * probe's `apple-overflow` control shows — so the corner is the reference
 * family's construction at the same radius with the reach clamped to the budget,
 * the effective smoothing falling to `reach / r - 1`. W20 G0 measured that
 * against Apple's pixels at r 14…22 on a 120 × 44 and a 44 × 44 box, max 0.40 px
 * and p95 0.34 px, the same residual the exact capsule controls read against
 * their own stadium (claims §5.84 §5–§6).
 */
export function buildAppleContour(
  halfW: number,
  halfH: number,
  radius: number,
  center: Vec2 = [0, 0],
): AppleContour {
  const budget = Math.min(halfW, halfH);
  const r = Math.max(0, Math.min(radius, budget));
  const saturated = APPLE_REACH * r > budget + 1e-12;

  if (saturated) {
    // The seed is the requested smoothing; `resolveCornerConstruction`'s own
    // budget clamp is what compresses it, and at the capsule limit (r = budget)
    // it reaches exactly 0 and the cubics degenerate to the circular stadium
    // `Capsule()` measures.
    const seed = APPLE_CONTINUOUS_SMOOTHING_SEED;
    const construction = resolveCornerConstruction(halfW, halfH, r, seed);
    return { ...buildReferenceContour(halfW, halfH, construction, center), saturated };
  }

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
