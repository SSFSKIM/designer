/**
 * X8's public sugar: `profile`, one uniform `radius`, `capsule`.
 *
 * `@vitrea/geometry` already owns the mapping from `profile` to a corner
 * reference and a smoothing number — but it owns it inside `resolveShape`, and
 * `platform-web`'s host registration takes a bare `smoothing` number rather than
 * a `ShapeSpec`. Decision Log #23c is why: the corner *reference* is a render
 * input in v1, not a scene-model field, so it never reaches core. This module is
 * the one place that gap is bridged, and it mirrors geometry's private
 * `referenceFor` exactly rather than inventing a second mapping.
 *
 * The consequence a caller has to know about is the morph rule (Decision Log
 * #22a): `"circular"` sits on the Figma smoothing axis and `"continuous"` on the
 * Apple-direct fit, and the two are separate fits rather than two points on one
 * axis — so a morph across them has no measured error bound and geometry throws.
 * `assertSharedCornerReference` raises that as a dev-mode error at the API
 * boundary, where the prop that caused it is still visible.
 */

import {
  APPLE_BEST_FIGMA_SMOOTHING,
  APPLE_CONTINUOUS_SMOOTHING_SEED,
  type CornerProfile,
  type CornerRadii,
  type CornerReference,
  uniformRadii,
} from "@vitrea/geometry";

/** `"continuous" | "circular"`, or a number authoring straight onto the Figma axis. */
export type GlassCornerProfile = CornerProfile | number;

/**
 * The interpolable stand-in for Apple's curve. A morph pair that wants an
 * Apple-like corner at both ends authors this number rather than
 * `"continuous"` — it is the same corner to within 1.96e-3·r and it lives on the
 * axis the error bound was measured on.
 */
export const APPLE_LIKE_SMOOTHING: number = APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing;

/** Which of geometry's two corner references a `profile` value resolves to. */
export function cornerReferenceFor(profile: GlassCornerProfile | undefined): CornerReference {
  return profile === undefined || profile === "continuous" ? "apple-continuous" : "figma-smoothing";
}

/** The `smoothing` channel a `profile` value resolves to, matching geometry's own table. */
export function smoothingFor(profile: GlassCornerProfile | undefined): number {
  if (profile === undefined || profile === "continuous") return APPLE_CONTINUOUS_SMOOTHING_SEED;
  if (profile === "circular") return 0;
  return Math.min(Math.max(profile, 0), 1);
}

/**
 * v1 radii are uniform (X8 rider 3) and the public sugar says so: one number,
 * spread to the Vec4 the channel set preserves.
 */
export function radiiFor(radius: number): CornerRadii {
  return uniformRadii(Math.max(radius, 0));
}

/**
 * The radius that makes a rect of this size a capsule.
 *
 * Half the shorter side is the corner budget, and a radius at the budget forces
 * effective smoothing to 0 — which is what makes a capsule an exact stadium
 * under either reference rather than an approximation of one.
 */
export function capsuleRadius(width: number, height: number): number {
  return Math.max(Math.min(width, height), 0) / 2;
}

export interface CornerEndpoint {
  readonly label: string;
  readonly profile: GlassCornerProfile | undefined;
}

/**
 * Refuse a morph whose two ends are fit against different reference curves.
 *
 * geometry throws the same refusal from `morphShapes`, but a binding that only
 * ever hands `platform-web` a smoothing *number* never reaches that check — the
 * reference does not travel with the shape in v1. Raising it here keeps the
 * guarantee, and does it while the offending prop is still nameable.
 */
export function assertSharedCornerReference(
  a: CornerEndpoint,
  b: CornerEndpoint,
): CornerReference {
  const referenceA = cornerReferenceFor(a.profile);
  const referenceB = cornerReferenceFor(b.profile);
  if (referenceA === referenceB) return referenceA;

  throw new Error(
    `vitrea-react: a morph's two ends must share a corner reference, but ${a.label} resolves to ` +
      `"${referenceA}" and ${b.label} to "${referenceB}". The two are separate fits to different ` +
      "curves, not two points on one axis, so an interpolated corner between them has no measured " +
      `error bound (X8, Decision Log #22a). Give both ends the same profile — profile={${APPLE_LIKE_SMOOTHING}} ` +
      "(APPLE_LIKE_SMOOTHING) is the Apple-matching value on the interpolable axis.",
  );
}
