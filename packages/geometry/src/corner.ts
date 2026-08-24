/**
 * The corner: the rounding-and-smoothing budget clamp, and the cubic-offset
 * scalars of the reference contour construction.
 *
 * X8 rider 1 — `smoothing` is clamped by a budget derived from `size` and
 * `radii`. This is a real interaction between X8 channels and it is
 * load-bearing three times over:
 *
 *  - it is why a capsule is EXACT. At the capsule limit the radius equals the
 *    budget, so `budget / r - 1` is 0 and effective smoothing is forced to
 *    exactly 0: a capsule is always a true stadium, and every pseudo-SDF family
 *    is exact on a stadium (S2, §Capsule limit).
 *  - it bounds the worst-case corner radius, and the field's contour deviation
 *    is linear in that radius. Smoothing 1.0 is only reachable when
 *    `r <= 1/4` of the short side, which is what keeps the declared bound flat
 *    across three orders of magnitude of shape size.
 *  - it is CONTINUOUS in size (`d s_eff / d size = 1/r` while clamped, 0 once
 *    the clamp releases), so a morph that shrinks a shape through the clamp does
 *    not snap. Asserted in `test/corner.test.ts`.
 *
 * The authored smoothing is preserved on the channel and the clamp is applied
 * here, at derivation — so shrinking a shape and growing it back is lossless.
 *
 * The construction itself is Figma's ("Desperately seeking squircles"), which is
 * the family the spec names as the authoring parameterization: one corner is
 * straight edge -> cubic -> circular arc -> cubic -> straight edge, with the
 * cubics ramping curvature from 0 at the straight edge up to 1/r at the arc.
 * `smoothing = 0` degenerates the cubics to zero length and reproduces the plain
 * circular rounded rectangle exactly.
 */

const toRad = (deg: number): number => (deg * Math.PI) / 180;

/**
 * The rounding-and-smoothing budget for one corner. Figma splits each side
 * between its two corners in proportion to their radii; with a uniform radius
 * that is half the side, and the corner's budget is the min over its two sides.
 * In half-extents that is `min(halfW, halfH)`.
 */
export function cornerBudget(halfW: number, halfH: number): number {
  return Math.min(halfW, halfH);
}

/**
 * The continuous smoothing ceiling at a given radius and budget: the largest
 * smoothing whose corner reach `(1 + s) * r` still fits the budget.
 *
 * Exposed because it is the thing a morph must stay under, and a caller that
 * wants to check "will this shape be clamped?" should read the same function the
 * resolver reads rather than re-deriving it.
 */
export function smoothingCeiling(radius: number, budget: number): number {
  if (radius <= 0) return Number.POSITIVE_INFINITY;
  return Math.max(0, budget / radius - 1);
}

export interface CornerConstruction {
  /** radius actually used, after the budget clamp on the radius itself */
  readonly radius: number;
  /** smoothing actually used, after the budget clamp */
  readonly smoothingEff: number;
  /** how far the corner reaches along each adjacent edge from the corner vertex */
  readonly reach: number;
  /** cubic control-offset scalars of the reference construction */
  readonly a: number;
  readonly b: number;
  readonly c: number;
  readonly d: number;
  /** axis-aligned extent of the circular arc section (equal in x and y) */
  readonly arcSectionLength: number;
  /** central angle of the circular arc, radians */
  readonly arcMeasure: number;
  /** min(halfW, halfH) — the per-corner rounding-and-smoothing budget */
  readonly budget: number;
}

/**
 * Apply the budget clamp and derive the reference construction's scalars.
 *
 * `radius` and `smoothing` are the authored values; both are clamped here. The
 * radius is clamped first, because a radius larger than the budget cannot be
 * honoured at any smoothing.
 */
export function resolveCornerConstruction(
  halfW: number,
  halfH: number,
  radius: number,
  smoothing: number,
): CornerConstruction {
  const budget = cornerBudget(halfW, halfH);
  const r = Math.min(Math.max(radius, 0), budget);
  const requested = Math.min(Math.max(smoothing, 0), 1);
  const s = Math.min(requested, smoothingCeiling(r, budget));
  const reach = Math.min((1 + s) * r, budget);

  const arcMeasureDeg = 90 * (1 - s);
  const arcSectionLength = Math.sin(toRad(arcMeasureDeg / 2)) * r * Math.SQRT2;

  const angleAlpha = (90 - arcMeasureDeg) / 2;
  const p3ToP4Distance = r * Math.tan(toRad(angleAlpha / 2));

  const angleBeta = 45 * s;
  const c = p3ToP4Distance * Math.cos(toRad(angleBeta));
  const d = c * Math.tan(toRad(angleBeta));

  const b = (reach - arcSectionLength - c - d) / 3;
  const a = 2 * b;

  return {
    radius: r,
    smoothingEff: s,
    reach,
    a,
    b,
    c,
    d,
    arcSectionLength,
    arcMeasure: toRad(arcMeasureDeg),
    budget,
  };
}
