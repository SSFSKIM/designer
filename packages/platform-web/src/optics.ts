/**
 * The optical constants of the material, and the 3σ padding floor that follows
 * from one of them.
 *
 * **This is the package that owns the blur radius.** core cannot: its
 * `samplingPadding` advisory (24px) is 3σ at an assumed σ = 8, and its own
 * comment says the actual check "cannot live here because core carries no blur
 * radius". So the enforcement split is: core checks what its data can see
 * (`mergeDistance ≥ samplingPadding`, neighbouring proxy-rect overlap), and the
 * `samplingPadding ≥ 3σ` floor is checked here.
 *
 * Every number below is an **advisory default**, calibration-delegated (C7).
 * They are chosen so X1's constraints hold out of the box, not because they are
 * measured against Apple.
 */

import type { MaterialVariant, ResolvedMaterialPolicy } from "@vitrea/core";

export interface MaterialOptics {
  /**
   * The Gaussian **standard deviation** handed to `blur()`, in CSS px. Filter
   * Effects 1 says the `blur(<length>)` parameter *is* σ, and warns that it is
   * not `box-shadow`'s blur radius — which is why the 3σ arithmetic below is
   * simply `3 × this`.
   */
  readonly blurRadius: number;
  readonly saturation: number;
  /** Tint alpha laid over the blurred backdrop, 0..1. Also the occlusion knob. */
  readonly tintAlpha: number;
  /** Rim/border alpha, 0..1. */
  readonly borderAlpha: number;
  /** Border width in CSS px. */
  readonly borderWidth: number;
}

/**
 * σ = 8 for the regular variant, which is what makes core's 24px advisory
 * exactly 3σ. Clear is persistently more transparent, so it frosts less and
 * tints less — and it carries its own dimming policy from core.
 */
export const MATERIAL_OPTICS: Readonly<Record<MaterialVariant, MaterialOptics>> = {
  regular: { blurRadius: 8, saturation: 1.8, tintAlpha: 0.28, borderAlpha: 0.35, borderWidth: 1 },
  clear: { blurRadius: 4, saturation: 1.4, tintAlpha: 0.1, borderAlpha: 0.28, borderWidth: 1 },
};

/**
 * Standard Gaussian kernel truncation, and the number S1 measured: distance
 * from an unstarvable viewport-sized proxy is byte-exact at 3σ for
 * `blur(8px)`, `blur(20px)` and `blur(40px)` — three radii spanning 5×, which
 * is what makes it a rule rather than a fit.
 */
export const SAMPLING_PADDING_SIGMA_MULTIPLE = 3;

/** The floor a group's `samplingPadding` may not sit below, in CSS px. */
export function requiredSamplingPadding(blurRadius: number): number {
  return blurRadius * SAMPLING_PADDING_SIGMA_MULTIPLE;
}

/**
 * How much reduced transparency thickens the frost. §Accessibility says "more
 * frosted"; the regime is core's decision and the multiplier is this package's,
 * because it is a number about a blur radius.
 */
const REDUCED_TRANSPARENCY_FROST = 1.75;

/** Occlusion under reduced transparency: enough of the backdrop hidden to read against. */
const INCREASED_OCCLUSION_ALPHA = 0.62;

/** A drawn border rather than a rim highlight (§Accessibility: "stronger borders"). */
const STRONG_BORDER = { borderWidth: 2, borderAlpha: 0.95 } as const;

/** Ambient tint pulled back under increased contrast. */
const REDUCED_TINT_SATURATION = 1;

/**
 * Fold core's resolved material *regime* onto this package's numbers.
 *
 * core says which regime applies; nothing here re-decides that. Each branch is
 * one axis of `ResolvedMaterialPolicy`, so a new axis in core surfaces as a
 * missing branch here rather than as silence.
 */
export function opticsUnderPolicy(
  optics: MaterialOptics,
  policy: ResolvedMaterialPolicy,
): MaterialOptics {
  let next = optics;

  if (policy.frost === "increased") {
    next = { ...next, blurRadius: next.blurRadius * REDUCED_TRANSPARENCY_FROST };
  } else if (policy.frost === "none") {
    next = { ...next, blurRadius: 0 };
  }

  if (policy.occlusion === "increased") {
    next = { ...next, tintAlpha: Math.max(next.tintAlpha, INCREASED_OCCLUSION_ALPHA) };
  } else if (policy.occlusion === "opaque") {
    next = { ...next, tintAlpha: 1 };
  }

  if (policy.border === "strong") next = { ...next, ...STRONG_BORDER };

  if (policy.ambientTint === "reduced") next = { ...next, saturation: REDUCED_TINT_SATURATION };
  else if (policy.ambientTint === "none") next = { ...next, saturation: 1 };

  return next;
}
