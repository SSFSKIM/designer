/**
 * The optical constants of the material, the 3σ padding floor that follows from
 * one of them, and the mapping that carries a material profile across the tier
 * boundary.
 *
 * **This is the package that owns the blur radius.** core cannot: its
 * `samplingPadding` advisory (24px) is 3σ at an assumed σ = 8, and its own
 * comment says the actual check "cannot live here because core carries no blur
 * radius". So the enforcement split is: core checks what its data can see
 * (`mergeDistance ≥ samplingPadding`, neighbouring proxy-rect overlap), and the
 * `samplingPadding ≥ 3σ` floor is checked here.
 *
 * ## Why there is a mapping here at all (corrective K5)
 *
 * C9a tuned the GPU tier's `tintAlpha` from 0.28 to 0.62 and the CSS tier kept
 * its own untuned 0.28, so a root that demoted from `webgpu` to `css` changed
 * opacity by more than 2× (`docs/doperpowers/specs/c9a-fidelity-claims.md` §3).
 * Copying 0.62 across would have been worse than leaving the gap, because the
 * two tiers do not composite the same way: the renderer lerps toward the tint in
 * **linear light**, while the CSS tier lays `rgba()` over a `backdrop-filter`ed
 * backdrop that the page composites in **encoded sRGB**. The same alpha is a
 * different material.
 *
 * So the CSS tier does not hold a second copy of the material's numbers. It
 * derives them from the one profile the root carries — `createGlassRoot({
 * materialProfile })`, Decision Log #29(b) — through `cssTierOptics` below, and
 * the *mapping's* constants (`CssTierMapping`) are what calibration tunes. A
 * retuned profile now moves both tiers at once, which is the property the gap
 * was the absence of.
 *
 * ## What the mapping cannot do
 *
 * Exact coherence is unreachable, and the arithmetic says so before any capture
 * does. Matching the two composites for a white tint at α = 0.62 needs a CSS
 * alpha of 0.761 over a backdrop at linear luminance 0.05 and 0.635 over one at
 * 0.8 — a 1.2× spread with no single scalar in it, because one pipeline's
 * transfer function is applied before the blend and the other's after. The
 * mapping therefore agrees with the GPU tier at **one declared backdrop level**
 * (`referenceBackdropLuminance`) and is measurably off either side of it. That
 * floor is a fact about `backdrop-filter`, not a tuning failure, and it is what
 * the tier-coherence claim is worded around.
 */

import type { MaterialVariant, ResolvedMaterialPolicy } from "@vitrea/core";

import type { RendererMaterialProfile } from "./renderer-bridge";

/** Linear-light RGB, the units the renderer's profile states its colours in. */
export type LinearRgb = readonly [number, number, number];

/** sRGB, 0..255 per channel — what a `rgba()` declaration takes. */
export type Rgb255 = readonly [number, number, number];

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
  /** The tint's own colour, sRGB 0..255 — the profile's linear tint, encoded. */
  readonly tint: Rgb255;
  /** Rim/border alpha, 0..1. */
  readonly borderAlpha: number;
  /** The border's colour, sRGB 0..255 — from the profile's highlight, not its tint. */
  readonly border: Rgb255;
  /** Border width in CSS px. */
  readonly borderWidth: number;
  /** The ambient drop shadow: vertical offset and blur in CSS px, and its alpha. */
  readonly shadowOffset: number;
  readonly shadowBlur: number;
  readonly shadowAlpha: number;
}

/**
 * The slice of the renderer's per-variant optics this tier's mapping reads.
 *
 * A **mirror**, on the same doctrine that pins the calibration profile JSON to
 * the renderer's `DEFAULT_MATERIAL_PROFILE` (Decision Log #29(b)): the renderer
 * is the authority and these numbers restate the part of it the CSS tier needs.
 * platform-web has no dependency on `@vitrea/renderer-webgpu` — the renderer
 * loads behind core's lazy seam so a CSS-tier visitor never downloads it (X7) —
 * so the mirror cannot be an import. `packages/calibration/test/tier-coherence.test.ts`
 * pins it in both directions, which is what stops the two drifting in silence.
 */
export interface MaterialSourceOptics {
  /** The renderer's body blur σ, in CSS px. */
  readonly blurSigma: number;
  /** The tint the renderer lerps toward, in linear light. */
  readonly tint: LinearRgb;
  readonly tintAlpha: number;
  /** The renderer's ambient rim brightness, 0..1. */
  readonly rimAlpha: number;
  /** The renderer's highlight colour, in linear light. The rim reads from this. */
  readonly highlight: LinearRgb;
}

/** Mirrors `@vitrea/renderer-webgpu`'s `DEFAULT_MATERIAL_PROFILE.optics`. */
export const MATERIAL_SOURCE_OPTICS: Readonly<Record<MaterialVariant, MaterialSourceOptics>> = {
  // σ = 8 for the regular variant, which is what makes core's 24px advisory
  // exactly 3σ. `tintAlpha` 0.62 is C9a's measured value, and carrying it here
  // rather than a second advisory is the whole point of K5.
  regular: { blurSigma: 8, tint: [1, 1, 1], tintAlpha: 0.62, rimAlpha: 0.18, highlight: [1, 1, 1] },
  // Persistently more transparent, so it frosts less and tints less — and it
  // carries its own dimming policy from core. Uncalibrated in either tier: the
  // canonical scene matrix has no clear-variant scene.
  clear: { blurSigma: 4, tint: [1, 1, 1], tintAlpha: 0.1, rimAlpha: 0.14, highlight: [1, 1, 1] },
};

/**
 * Everything the tier boundary costs, as numbers.
 *
 * These are the CSS tier's own calibration-delegated unknowns. Two kinds live
 * here and the distinction matters when reading a tuned value: a **conversion**
 * constant expresses how a renderer quantity survives the crossing
 * (`referenceBackdropLuminance`, `blurSigmaScale`, `borderAlphaPerRimAlpha`),
 * and a **CSS-only** constant names something the renderer has no counterpart
 * for at all (`saturation`, `borderWidth`, the shadow triple) — for those the
 * mapping is not converting anything and the number is simply the tier's.
 */
export interface CssTierMapping {
  /**
   * The backdrop level, in linear relative luminance, at which the two tiers are
   * made to agree.
   *
   * The one constant that closes K5's gap. `cssTintAlpha` solves for the alpha
   * that reproduces the renderer's linear-light composite *at this backdrop
   * level* once the page has composited in encoded sRGB; either side of it the
   * two tiers differ, monotonically and measurably. Fitting it is fitting where
   * in the canonical backdrop range the agreement should be exact.
   */
  readonly referenceBackdropLuminance: number;
  /**
   * A guard, not a tunable: below this much encoded contrast between the tint
   * and the reference backdrop there is nothing to solve for in either pipeline,
   * so the alpha passes through unconverted rather than dividing by ~0.
   */
  readonly minimumTintContrast: number;
  /** CSS `blur()` σ per unit of the renderer's body σ. */
  readonly blurSigmaScale: number;
  /**
   * `backdrop-filter: saturate()`, per variant. CSS-only: the renderer's optics
   * carry no saturation term, so this is not a conversion of anything.
   */
  readonly saturation: Readonly<Record<MaterialVariant, number>>;
  /**
   * `border-color` alpha per unit of the renderer's `rimAlpha`. A conversion
   * with a wide seam: the renderer's rim is a `rimWidth`-wide band with a
   * specular term on top of it, and the CSS tier's is a hard 1px line with
   * neither, so the two are the same feature only in intent.
   */
  readonly borderAlphaPerRimAlpha: number;
  /**
   * `border-width` in CSS px. CSS-only: a box border is not the renderer's rim
   * band, and deriving one from the other would be arithmetic dressed as a
   * derivation.
   */
  readonly borderWidth: number;
  /**
   * The ambient drop shadow — offset and blur in CSS px, and its alpha.
   *
   * CSS-only, and the one place this tier deliberately draws something the
   * reference material does not: C9a measured both sides at ≈0 outside the
   * contour, while this shadow puts material outside it (which is why the dom
   * tier's silhouette runs up to 2.36× the declared component area and its shape
   * axis is not comparable to the texture tier's). It survives because the
   * fallback has to read as a floating surface — the repo's effects policy says
   * the fallback is the design — so it is a stated departure rather than an
   * unmeasured one. Absolute px rather than multiples of σ so that a frost
   * preference cannot change the surface's apparent footprint.
   */
  readonly shadowOffset: number;
  readonly shadowBlur: number;
  readonly shadowAlpha: number;
}

export const CSS_TIER_MAPPING: CssTierMapping = {
  // MEASURED (K5), against apple-macos-26.5-1x-light-standard on the CSS tier,
  // Chromium only — the one engine whose backdrop-filter output is capturable
  // (S1). See docs/doperpowers/specs/c9a-fidelity-claims.md §3.
  referenceBackdropLuminance: 0.18,
  minimumTintContrast: 1e-3,
  // Left at 1: the two tiers stay on one σ, which is also what makes core's 24px
  // `samplingPadding` exactly S1's 3σ floor. C9a found σ unidentifiable from
  // this fixture set (§6.1) and nothing on the CSS tier changes that.
  blurSigmaScale: 1,
  saturation: { regular: 1.8, clear: 1.4 },
  borderAlphaPerRimAlpha: 1.95,
  borderWidth: 1,
  shadowOffset: 6,
  shadowBlur: 24,
  shadowAlpha: 0.18,
};

/**
 * The sRGB transfer function (IEC 61966-2-1), encode direction.
 *
 * Restated rather than imported for the reason the mirror above exists: this
 * package must not depend on the renderer. It is a spec constant and not a
 * tunable, so the duplication carries no drift risk — unlike an optical number,
 * there is no second value it could become.
 */
function srgbEncode(linear: number): number {
  const clamped = Math.min(1, Math.max(0, linear));
  return clamped <= 0.0031308 ? clamped * 12.92 : 1.055 * Math.pow(clamped, 1 / 2.4) - 0.055;
}

/** Rec. 709 relative luminance, the weighting X5's linear-light pipeline uses. */
function luminance(rgb: LinearRgb): number {
  return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
}

const clamp01 = (value: number): number => Math.min(1, Math.max(0, value));

function encodeRgb(rgb: LinearRgb): Rgb255 {
  return [
    Math.round(srgbEncode(rgb[0]) * 255),
    Math.round(srgbEncode(rgb[1]) * 255),
    Math.round(srgbEncode(rgb[2]) * 255),
  ];
}

/**
 * The alpha that makes an sRGB-composited overlay match a linear-light lerp, at
 * one declared backdrop level.
 *
 * The renderer produces `b(1−α) + t·α` in linear light and the page shows
 * `E(that)`. The CSS tier produces `E(b)(1−α′) + E(t)·α′` directly. Solving the
 * two for α′ at `b = referenceBackdropLuminance` is the whole conversion, and
 * the residual either side of that level is the coherence floor named in this
 * module's header.
 *
 * Exported because it is the mapping's substance: a reader checking whether a
 * tuned `referenceBackdropLuminance` is doing what it claims should be able to
 * evaluate this rather than infer it from a screenshot.
 */
export function cssTintAlpha(
  source: MaterialSourceOptics,
  mapping: CssTierMapping = CSS_TIER_MAPPING,
): number {
  const backdrop = mapping.referenceBackdropLuminance;
  const tint = luminance(source.tint);
  const encodedBackdrop = srgbEncode(backdrop);
  const span = srgbEncode(tint) - encodedBackdrop;
  // A tint sitting at the reference backdrop's own level is invisible in both
  // pipelines, so there is no alpha to solve for and the renderer's passes
  // through. Only reachable from a profile that tints to the reference level.
  if (Math.abs(span) < mapping.minimumTintContrast) return clamp01(source.tintAlpha);

  const composited = backdrop * (1 - source.tintAlpha) + tint * source.tintAlpha;
  return clamp01((srgbEncode(composited) - encodedBackdrop) / span);
}

/**
 * The whole mapping: one material profile in, this tier's declarations' numbers
 * out.
 *
 * `patch` is exactly what `createGlassRoot({ materialProfile })` takes and what
 * the renderer receives, so the two tiers read one document. A field the patch
 * does not name keeps the mirrored default, which is the same merge rule the
 * renderer's own `withMaterialOverrides` follows.
 */
export function cssTierOptics(
  patch?: RendererMaterialProfile,
  mapping: CssTierMapping = CSS_TIER_MAPPING,
): Readonly<Record<MaterialVariant, MaterialOptics>> {
  const resolved = {} as Record<MaterialVariant, MaterialOptics>;
  for (const variant of ["regular", "clear"] as const) {
    const source: MaterialSourceOptics = {
      ...MATERIAL_SOURCE_OPTICS[variant],
      ...patch?.optics?.[variant],
    };
    resolved[variant] = {
      blurRadius: source.blurSigma * mapping.blurSigmaScale,
      saturation: mapping.saturation[variant],
      tintAlpha: cssTintAlpha(source, mapping),
      tint: encodeRgb(source.tint),
      borderAlpha: clamp01(source.rimAlpha * mapping.borderAlphaPerRimAlpha),
      border: encodeRgb(source.highlight),
      borderWidth: mapping.borderWidth,
      shadowOffset: mapping.shadowOffset,
      shadowBlur: mapping.shadowBlur,
      shadowAlpha: mapping.shadowAlpha,
    };
  }
  return resolved;
}

/**
 * This tier's numbers under the shipped profile and the shipped mapping.
 *
 * Derived rather than written out, so there is no second place for the CSS tier
 * and the material profile to disagree.
 */
export const MATERIAL_OPTICS: Readonly<Record<MaterialVariant, MaterialOptics>> = cssTierOptics();

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
