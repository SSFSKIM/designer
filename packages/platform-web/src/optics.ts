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

import type { MaterialVariant, ResolvedMaterialPolicy } from "vitrea";

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
   * two tiers differ, monotonically and measurably.
   *
   * **Its fitted value is not the physical reading of its name, and that is a
   * finding rather than a naming slip.** The form of the mapping comes from the
   * two transfer functions, so the name describes the mechanism exactly. But the
   * fitted scalar also absorbs every *other* difference between the two
   * pipelines — the CSS tier's `saturate()`, which the renderer has no
   * counterpart for, and the renderer's own body-blur LOD chain — so the level
   * that minimises the measured cross-tier difference (0.02) is far below any
   * canonical scene's mean backdrop. A reader who took 0.02 for "the typical
   * backdrop" would be reading it wrong.
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
   * **Zero, as of Decision Log #32(c).** The seam stays because a profile is
   * entitled to put one back; the shipped value is the reference's, which is
   * none. K5 measured what the shadow was costing: it owned the dom tier's whole
   * shape axis, and turning it off — nothing else — moved silhouette IoU from
   * 0.676 to 0.942 and contour p95 from 18.7px to 2.2px, with perceptual and
   * cross-tier agreement improving too. It had survived until then on the repo's
   * effects policy ("the fallback is the design", so it has to read as a floating
   * surface); the parent ruled fidelity-first is the tiebreaker and "reads as
   * Apple" outranks "reads as floating".
   *
   * The tier does not lose its contrast floor with it. What keeps a surface
   * legible when `backdrop-filter` no-ops is the tint and the border, which is
   * what `e2e/pixel/css-tier-pixels.spec.ts` asserts, and neither is a shadow.
   *
   * Absolute px rather than multiples of σ, so that a frost preference cannot
   * change the surface's apparent footprint if a profile does restore one.
   */
  readonly shadowOffset: number;
  readonly shadowBlur: number;
  readonly shadowAlpha: number;

  /**
   * The backdrop level an X6 hint's `tone` stands for when it carries no
   * `luminance`, in linear relative luminance. Only `dark` and `light` need one:
   * `mixed` has no single answer and keeps the `light-dark()` default.
   */
  readonly toneLuminance: { readonly dark: number; readonly light: number };
  /**
   * Where the foreground crosses from the light token to the dark one, measured
   * on the *encoded* level behind the glyphs (see `cssTierForegroundLevel`).
   *
   * Derived rather than chosen: 0.475 is where the two shipped ink tokens reach
   * equal WCAG contrast against the same surface. `#1c1c1e` sits at linear
   * 0.0116 and `#f5f5f7` at 0.898, so equal contrast needs
   * (L + 0.05)² = (0.898 + 0.05)(0.0116 + 0.05), giving L = 0.1917 and an encoded
   * 0.475. Below it the light token has more contrast, above it the dark one.
   */
  readonly foregroundCrossover: number;
}

export const CSS_TIER_MAPPING: CssTierMapping = {
  /*
   * MEASURED (K5), against apple-macos-26.5-1x-light-standard on the CSS tier,
   * Chromium only — the one engine whose backdrop-filter output is capturable
   * (S1). See docs/doperpowers/specs/c9a-fidelity-claims.md §3.
   *
   * Fitted against the CROSS-TIER difference, not against the fixtures, and the
   * two disagree. Over 0.005 … 0.30 the cross-tier ΔE rises monotonically
   * (0.0078 → 0.0115) while the CSS tier's own ΔE against Apple *falls*
   * monotonically (0.0118 → 0.0094): coherence and independent fidelity pull
   * opposite ways, because the GPU tier is not itself exactly on the reference.
   *
   * Coherence wins, deliberately. A CSS tier fitted independently against Apple
   * is free to drift from the GPU tier again the moment either is retuned, which
   * is precisely how K5's gap opened; a converted one inherits the GPU tier's
   * fidelity by construction. The price is measured and small — the CSS tier's ΔE
   * against Apple ends at 0.0113 against the GPU tier's own 0.0097, well inside
   * the 0.07 threshold C9a proposed.
   *
   * 0.02 rather than the flat region's other candidates because it minimises the
   * cross-tier ΔE on the *worst cell* (0.0151), which is the per-cell criterion
   * the methodology asks for. The region 0.005 … 0.05 spans 1.10× on the mean —
   * flat, so this is picking the best worst case inside flatness rather than
   * claiming a sharp optimum.
   */
  referenceBackdropLuminance: 0.02,
  minimumTintContrast: 1e-3,
  // Left at 1: the two tiers stay on one σ, which is also what makes core's 24px
  // `samplingPadding` exactly S1's 3σ floor. C9a found σ unidentifiable from
  // this fixture set (§6.1) and nothing on the CSS tier changes that.
  blurSigmaScale: 1,
  saturation: { regular: 1.8, clear: 1.4 },
  /*
   * DECLINED (K5), on C9a's own precedent for the GPU tier's rim.
   *
   * Swept at 0, 0.6 and 1.95 with the tint frozen: the cross-tier ΔE spans
   * 0.00791 … 0.00796 and the fixture ΔE 0.01121 … 0.01131. A 1.01× grid — the
   * same flatness C9a measured on `rimAlpha` × `specularGain` — so the fixtures
   * do not identify it. Dropping it to zero buys 0.0001 of ΔE and costs the
   * tier its contrast floor: S1's undetectable failure class means an engine that
   * reports support and renders no filter must still leave a legible surface, and
   * the border is half of what carries that. Deleting the feature the estimator
   * measures to win a flat grid is fitting the estimator.
   */
  borderAlphaPerRimAlpha: 1.95,
  borderWidth: 1,
  /*
   * MEASURED (K5) and REMOVED (Decision Log #32(c)). See `CssTierMapping`'s
   * shadow fields for the numbers and the reasoning; the surface's own contrast
   * floor is the tint and the border, not this.
   */
  shadowOffset: 0,
  shadowBlur: 0,
  shadowAlpha: 0,
  // A hint that names only a tone is a coarse statement, and these are the coarse
  // readings of it: near-black and near-white. An app that wants the foreground
  // decided finely passes `luminance`, which X6's hint already carries.
  toneLuminance: { dark: 0.05, light: 0.9 },
  foregroundCrossover: 0.475,
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
 * The level the glyphs actually sit on, encoded sRGB 0..1 — one rule, one function
 * per compositing space (Decision Log #32(b)).
 *
 * **Why the foreground cannot be chosen from the backdrop alone.** X6's hint
 * describes what is *behind the group*, and K4 wired that straight to the
 * foreground token: a dark backdrop got the light ink. That was right while the
 * material was 28% opaque and the backdrop showed through it. At the material's
 * measured opacity it is wrong — what a reader sees behind the text is
 * `mix(backdrop, tint, α)`, and once α is 0.78 that is the tint. A dark hint over
 * a white-tinted material was producing near-white ink on a near-white surface;
 * measured on the demo, WCAG contrast 1.24 against a 4.5 floor, and measured again
 * on the GPU tier at 1.57 before that tier published a foreground at all.
 *
 * So the tone is one input to the decision rather than the decision. There are two
 * functions and not one because the two tiers genuinely composite in different
 * spaces — the same difference `cssTintAlpha` exists for — and the mix has to be
 * taken where it actually happens: luminance is a linear combination of channels,
 * so the encoded-space mix wants the luminance *of the encoded tint*, which is not
 * the encoding of the tint's linear luminance. Both roads end in an encoded level,
 * because that is what a reader is presented with and what
 * `CssTierMapping.foregroundCrossover` is measured on. What is shared is the
 * decision the level feeds: `foregroundDeclarations` in `css-tier.ts`, which both
 * tiers call.
 *
 * Precision is deliberately not the goal here: the output feeds one threshold
 * between two ink tokens, and what matters is that the decision follows the tint
 * once the tint dominates. It is not a contrast calculation and does not claim to
 * be one — an app that needs a guaranteed ratio sets the foreground itself.
 */

/** The CSS tier: `rgba()` over a `backdrop-filter`ed backdrop, composited encoded. */
export function cssTierForegroundLevel(
  optics: MaterialOptics,
  backdropLuminance: number,
): number {
  const tint = luminance([
    optics.tint[0] / 255,
    optics.tint[1] / 255,
    optics.tint[2] / 255,
  ]);
  // The tint arrives encoded (`Rgb255`), so its luminance is already the quantity
  // the encoded mix wants; only the backdrop, which X6 defines as linear, is
  // encoded on the way in.
  return (1 - optics.tintAlpha) * srgbEncode(backdropLuminance) + optics.tintAlpha * tint;
}

/** The renderer: a lerp toward the tint in linear light, encoded for display. */
export function gpuTierForegroundLevel(
  source: MaterialSourceOptics,
  backdropLuminance: number,
): number {
  const mixed =
    (1 - source.tintAlpha) * backdropLuminance + source.tintAlpha * luminance(source.tint);
  return srgbEncode(mixed);
}

/**
 * The renderer's own per-variant optics under a profile patch — the mirror,
 * merged, before the tier conversion.
 *
 * Exported because the GPU tier's foreground needs the material the *renderer* is
 * drawing rather than the CSS tier's conversion of it (Decision Log #32(b)), and
 * that is the only quantity on this side of the seam that describes it.
 */
export function sourceOptics(
  patch?: RendererMaterialProfile,
): Readonly<Record<MaterialVariant, MaterialSourceOptics>> {
  const resolved = {} as Record<MaterialVariant, MaterialSourceOptics>;
  for (const variant of ["regular", "clear"] as const) {
    resolved[variant] = { ...MATERIAL_SOURCE_OPTICS[variant], ...patch?.optics?.[variant] };
  }
  return resolved;
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
    const source = sourceOptics(patch)[variant];
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

/**
 * How much of the *remaining* transparency reduced transparency closes.
 *
 * **Relative, not absolute, and that is the whole point (Decision Log #32(d)).**
 * This used to be an absolute floor — `Math.max(nominal, 0.62)` — which was a real
 * lift while nominal was the advisory 0.28 and became a no-op the moment C9a
 * measured nominal at 0.62. The policy died without being touched, on both tiers,
 * and nothing noticed for a whole child. A fraction of the headroom cannot die
 * that way: it lifts strictly for every nominal below 1, whatever a later tuning
 * pass moves nominal to.
 *
 * The fraction is the pre-C9a lift, restored rather than invented:
 * (0.62 − 0.28) / (1 − 0.28) = 0.4722. At the pre-C9a nominal it reproduces the old
 * floor exactly, so this changes the *shape* of the policy and not its calibration.
 * At today's nominal it reads 0.62 → 0.799 on the renderer's material and
 * 0.781 → 0.884 on this tier's converted alpha.
 *
 * Each tier applies it in its own alpha space. A fraction of headroom is
 * dimensionless — "close 47% of what is left" means the same thing on either side
 * of the conversion — which is exactly why a relative form is the right shape here;
 * the residual between the two tiers' lifted composites is the coherence floor this
 * module's header already states, not a new one.
 *
 * Mirrored by `@vitrea/renderer-webgpu`'s `MaterialProfile.increasedOcclusionLift`
 * and pinned in both directions by `packages/calibration/test/tier-coherence.test.ts`.
 */
export const INCREASED_OCCLUSION_LIFT = 0.4722;

/**
 * The occlusion alpha a resolved policy asks for, given whatever nominal the
 * material carries. One derivation, both tiers.
 */
export function occlusionAlphaUnderPolicy(
  nominal: number,
  occlusion: ResolvedMaterialPolicy["occlusion"],
  lift: number = INCREASED_OCCLUSION_LIFT,
): number {
  switch (occlusion) {
    case "nominal":
      return nominal;
    case "increased":
      return nominal + lift * (1 - nominal);
    case "opaque":
      return 1;
  }
}

/**
 * The lift a profile patch resolves to, by the renderer's own merge rule
 * (`withMaterialOverrides`): a field the patch does not name keeps the mirrored
 * default.
 *
 * The lift is a *patchable* profile field, and the renderer composites with the
 * patched value. Anything on this side that models what the renderer drew — the
 * GPU tier's foreground decision — or that paints its own lifted material — the
 * CSS tier's fold — has to resolve it the same way, or a calibration patch would
 * move the material without moving the decision taken against it. That is the
 * decision-vs-render divergence Decision Log #32(b) exists to prevent, and the
 * tier gap K5 (#32(a)) closed, reappearing through the patch rather than through
 * a second copy of the constant.
 */
export function resolvedOcclusionLift(patch?: RendererMaterialProfile): number {
  return patch?.increasedOcclusionLift ?? INCREASED_OCCLUSION_LIFT;
}

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
 *
 * `lift` is the resolved `increasedOcclusionLift` of the profile these optics
 * were derived from (`resolvedOcclusionLift`). It is a parameter because this
 * function receives no profile: the optics arriving here are already converted to
 * this tier's alpha space, and the patch that produced them is only in scope at
 * the call site. The default is the shipped constant, so an unpatched caller
 * folds exactly the numbers it always did.
 */
export function opticsUnderPolicy(
  optics: MaterialOptics,
  policy: ResolvedMaterialPolicy,
  lift: number = INCREASED_OCCLUSION_LIFT,
): MaterialOptics {
  let next = optics;

  if (policy.frost === "increased") {
    next = { ...next, blurRadius: next.blurRadius * REDUCED_TRANSPARENCY_FROST };
  } else if (policy.frost === "none") {
    next = { ...next, blurRadius: 0 };
  }

  next = { ...next, tintAlpha: occlusionAlphaUnderPolicy(next.tintAlpha, policy.occlusion, lift) };

  if (policy.border === "strong") next = { ...next, ...STRONG_BORDER };

  if (policy.ambientTint === "reduced") next = { ...next, saturation: REDUCED_TINT_SATURATION };
  else if (policy.ambientTint === "none") next = { ...next, saturation: 1 };

  return next;
}
