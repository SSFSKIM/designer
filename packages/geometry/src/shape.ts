/**
 * ShapeSpec -> ResolvedShape: authoring input to the X8 channel vector plus
 * everything derived from it.
 *
 * A resolved shape carries three layers, and keeping them separate is what makes
 * morphs lossless:
 *
 *   - `channels`  — X8 exactly, holding the AUTHORED values. `smoothing` here is
 *                   what the author wrote, never the clamped value.
 *   - `corner`    — the derivation: budget, clamped radius, effective smoothing,
 *                   corner reach, and the five fitted coefficients. For C6 this
 *                   is the six derived floats the instance buffer widens by
 *                   (`reach` + `k`), recomputed per frame during a morph.
 *   - `reference` — which curve the corner is fit against.
 *
 * ## Two corner references, and why there are two
 *
 * S2 measured that the reference curve, not the field family, is the fidelity
 * bottleneck. That leaves a genuine tension the spec resolves in both
 * directions at once, so the kernel carries both:
 *
 *   - **`"figma-smoothing"`** — the interpolable authoring axis. `smoothing` is
 *     a free channel over [0, 1], the budget clamp applies to it, and this is
 *     the axis the declared error bound is measured on (§Geometry binds a
 *     continuous numeric corner profile clamped by a budget derived from size
 *     and radii).
 *   - **`"apple-continuous"`** — the Apple-direct fit. Apple's curve has no
 *     smoothing parameter, so `smoothing` is pinned at the seed and Apple's own
 *     budget policy applies (clamp the RADIUS, not the smoothing). This is what
 *     `profile: "continuous"` resolves to, per Decision Log #20.
 *
 * `profile: "circular"` is smoothing 0, which is the same exact circular corner
 * under either reference and is therefore the member they share.
 *
 * The two references are not points on one axis and the kernel does not pretend
 * otherwise: `morph.ts` refuses a morph that crosses them rather than inventing
 * a blend the error bound does not cover. In practice v1's morph pairs share a
 * profile, and `APPLE_BEST_FIGMA_SMOOTHING` is the documented way onto the
 * interpolable axis for a caller that needs one.
 */

import { APPLE_CONTINUOUS_SMOOTHING_SEED, APPLE_REACH } from "./apple";
import {
  APPLE_RSUP,
  APPLE_RSUPN,
  type CornerCoefficients,
  coefficientsAt,
  FIGMA_RSUP_TABLE,
  FIGMA_RSUPN_TABLE,
  ZERO_COEFFICIENTS,
} from "./coefficients";
import {
  type CornerProfile,
  type CornerRadii,
  halfExtents,
  type ShapeChannels,
  type ShapeFamily,
  uniformRadii,
  type Vec2,
} from "./channels";
import { type CornerConstruction, cornerBudget, resolveCornerConstruction } from "./corner";
import { buildReferenceContour, type Contour } from "./contour";
import { buildAppleContour } from "./apple";
import { GeometryError } from "./errors";
import type { FieldParams } from "./field";

export type CornerReference = "figma-smoothing" | "apple-continuous";

/** Which field family the coefficients are for. Family C is the governor's step. */
export type FieldFamily = "rsupn" | "rsup";

export interface ResolvedCorner extends CornerConstruction {
  readonly reference: CornerReference;
  /** the five fitted correction coefficients for family D */
  readonly k: CornerCoefficients;
  /** max |field| on the true contour in units of the radius, for this fit */
  readonly contourDevPerR: number;
}

export interface ResolvedShape {
  readonly family: ShapeFamily;
  readonly channels: ShapeChannels;
  readonly corner: ResolvedCorner;
}

export interface FixedRoundedRectSpec {
  readonly family: "fixed-rounded-rect";
  readonly center: Vec2;
  readonly size: Vec2;
  /** A scalar is spread to all four corners; the Vec4 shape is preserved (X8). */
  readonly radii: CornerRadii | number;
  /**
   * `"continuous"` and `"circular"` are the public sugar. A number authors
   * directly on the Figma smoothing axis, which is what interpolates.
   */
  readonly profile?: CornerProfile | number;
  readonly thickness?: number;
}

export interface CapsuleSpec {
  readonly family: "capsule";
  readonly center: Vec2;
  readonly size: Vec2;
  readonly thickness?: number;
}

export type ShapeSpec = FixedRoundedRectSpec | CapsuleSpec;

export interface ResolveOptions {
  /**
   * Dev-only checks — the uniform-radii restriction. Default true: it is cheap,
   * and what it catches is a shape the v1 evaluator silently mis-renders.
   */
  readonly devMode?: boolean;
}

const DEFAULT_THICKNESS = 0;

function toRadii(r: CornerRadii | number): CornerRadii {
  return typeof r === "number" ? uniformRadii(r) : r;
}

/**
 * X8 rider 3 — v1's corner algebra is built on `|x|, |y|` and is therefore
 * mirror-symmetric by construction: it cannot express four different corners as
 * written. Per-corner radii would need the corner sector selected by quadrant
 * before the corner algebra runs, and the whole error sweep re-run. S2 asked for
 * this to be an explicit scope decision rather than an implementation detail, so
 * it is a refusal and not a silent average.
 */
export function assertUniformRadii(radii: CornerRadii): number {
  const [tl, tr, br, bl] = radii;
  const spread = Math.max(tl, tr, br, bl) - Math.min(tl, tr, br, bl);
  if (spread > 1e-9) {
    throw new GeometryError(
      "non-uniform-radii",
      `Per-corner radii are post-v1: got [${tl}, ${tr}, ${br}, ${bl}]. v1's corner algebra is ` +
        "mirror-symmetric (it reads |x| and |y|), so it cannot express four different corners, " +
        "and the declared error bound was swept for uniform radii only. Use one radius for all " +
        "four corners.",
    );
  }
  return tl;
}

function coefficientsFor(
  reference: CornerReference,
  family: FieldFamily,
  sEff: number,
  radius: number,
): { k: CornerCoefficients; contourDevPerR: number } {
  // A degenerate corner has no corner sector to correct — and zeroing the
  // coefficients is what makes `radius: 0` a plain rectangle rather than a
  // rectangle with a polynomial applied to nothing.
  if (radius <= 0) return { k: ZERO_COEFFICIENTS, contourDevPerR: 0 };
  if (reference === "apple-continuous") {
    const fit = family === "rsupn" ? APPLE_RSUPN : APPLE_RSUP;
    return { k: fit.k, contourDevPerR: fit.contourDevPerR };
  }
  return coefficientsAt(family === "rsupn" ? FIGMA_RSUPN_TABLE : FIGMA_RSUP_TABLE, sEff);
}

/**
 * Resolve a corner on a chosen reference. Exported because the concentric
 * resolver and the morph solver both re-derive corners from channel values and
 * must go through exactly the same clamp the authoring path does.
 */
export function resolveCorner(
  size: Vec2,
  radius: number,
  smoothing: number,
  reference: CornerReference,
  family: FieldFamily = "rsupn",
): ResolvedCorner {
  const { halfW, halfH } = halfExtents(size);

  if (reference === "apple-continuous") {
    // Apple clamps the RADIUS so the reach fits the side; it has no smoothing to
    // clamp. Past that the real corner warps, which this does not model —
    // `buildAppleContour` reports `saturated` for the same configuration.
    const budget = cornerBudget(halfW, halfH);
    const r = Math.max(0, Math.min(radius, budget / APPLE_REACH));
    const fit = coefficientsFor(reference, family, APPLE_CONTINUOUS_SMOOTHING_SEED, r);
    return {
      reference,
      radius: r,
      smoothingEff: r > 0 ? APPLE_CONTINUOUS_SMOOTHING_SEED : 0,
      reach: APPLE_REACH * r,
      a: 0,
      b: 0,
      c: 0,
      d: 0,
      arcSectionLength: 0,
      arcMeasure: (50 * Math.PI) / 180,
      budget,
      k: fit.k,
      contourDevPerR: fit.contourDevPerR,
    };
  }

  const construction = resolveCornerConstruction(halfW, halfH, radius, smoothing);
  const fit = coefficientsFor(reference, family, construction.smoothingEff, construction.radius);
  return { ...construction, reference, k: fit.k, contourDevPerR: fit.contourDevPerR };
}

function referenceFor(profile: CornerProfile | number | undefined): {
  reference: CornerReference;
  smoothing: number;
} {
  if (profile === undefined || profile === "continuous") {
    return { reference: "apple-continuous", smoothing: APPLE_CONTINUOUS_SMOOTHING_SEED };
  }
  if (profile === "circular") return { reference: "figma-smoothing", smoothing: 0 };
  return { reference: "figma-smoothing", smoothing: profile };
}

export function resolveShape(spec: ShapeSpec, options: ResolveOptions = {}): ResolvedShape {
  const devMode = options.devMode ?? true;

  if (spec.family === "capsule") {
    // A capsule's radius IS the budget, which forces effective smoothing to
    // exactly 0 — so a capsule is a true stadium and the field is exact on it,
    // for any smoothing the author might have wanted. That is a property of the
    // budget clamp, not a special case in the evaluator.
    const { halfW, halfH } = halfExtents(spec.size);
    const r = cornerBudget(halfW, halfH);
    return {
      family: "capsule",
      channels: {
        center: spec.center,
        size: spec.size,
        radii: uniformRadii(r),
        smoothing: 0,
        thickness: spec.thickness ?? DEFAULT_THICKNESS,
      },
      corner: resolveCorner(spec.size, r, 0, "figma-smoothing"),
    };
  }

  const radii = toRadii(spec.radii);
  const radius = devMode ? assertUniformRadii(radii) : (radii[0] ?? 0);
  const { reference, smoothing } = referenceFor(spec.profile);

  return {
    family: "fixed-rounded-rect",
    channels: {
      center: spec.center,
      size: spec.size,
      radii,
      smoothing,
      thickness: spec.thickness ?? DEFAULT_THICKNESS,
    },
    corner: resolveCorner(spec.size, radius, smoothing, reference),
  };
}

/**
 * Re-resolve a shape from a channel vector. This is the path a morph takes every
 * frame: interpolate channels, then derive the corner through the same clamp the
 * authoring path uses, so an interpolated shape is never a shape the resolver
 * could not have produced directly.
 */
export function resolveFromChannels(
  channels: ShapeChannels,
  reference: CornerReference,
  family: ShapeFamily = "fixed-rounded-rect",
  options: ResolveOptions = {},
): ResolvedShape {
  const devMode = options.devMode ?? true;
  const radius = devMode ? assertUniformRadii(channels.radii) : (channels.radii[0] ?? 0);
  return {
    family,
    channels,
    corner: resolveCorner(channels.size, radius, channels.smoothing, reference),
  };
}

/**
 * The shader-side parameters: half-extents plus the six derived floats. In
 * SHAPE-LOCAL coordinates — the field is evaluated about the shape's own centre,
 * so a caller subtracts `channels.center` first (or uses `sampleField`).
 */
export function fieldParams(shape: ResolvedShape): FieldParams {
  const { halfW, halfH } = halfExtents(shape.channels.size);
  return { halfW, halfH, reach: shape.corner.reach, k: shape.corner.k };
}

/** Field parameters for family C, the quality governor's first within-tier step. */
export function governorFieldParams(shape: ResolvedShape): FieldParams {
  const { halfW, halfH } = halfExtents(shape.channels.size);
  const corner = resolveCorner(
    shape.channels.size,
    shape.corner.radius,
    shape.channels.smoothing,
    shape.corner.reference,
    "rsup",
  );
  return { halfW, halfH, reach: corner.reach, k: corner.k };
}

/** The Contour IR for a resolved shape, in the shape's own coordinate space. */
export function toContour(shape: ResolvedShape): Contour {
  const { halfW, halfH } = halfExtents(shape.channels.size);
  if (shape.corner.reference === "apple-continuous") {
    return buildAppleContour(halfW, halfH, shape.corner.radius, shape.channels.center);
  }
  return buildReferenceContour(halfW, halfH, shape.corner, shape.channels.center);
}
