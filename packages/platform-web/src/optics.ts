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

import type { MaterialVariant, ResolvedMaterialPolicy } from "@vitreajs/vitrea";

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
  /**
   * The press glow's reach in CSS px and its peak alpha, at `glow` = 1.
   *
   * The renderer's own numbers, **unconverted** — see `MaterialSourceGlow`.
   */
  readonly glowRadius: number;
  readonly glowGain: number;
  /** The glow's colour, sRGB 0..255 — the profile's highlight, encoded. */
  readonly glow: Rgb255;
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
 * The author tint's tone map, mirrored — the curve that makes a tint a tint.
 *
 * Apple's tint is "a **range of tones** that are mapped to content brightness
 * underneath the tinted element" (S219), and a flat overlay of the author's
 * colour is the failure the same session names. So the seed is read through
 * this curve before anything composites it: over a dark backdrop the material
 * shows `floor` times the seed in linear light (a shade, hue intact), over a
 * bright one the seed `ceilMix` of the way to white, crossed with a smoothstep
 * between the two backdrop luminances.
 *
 * `reducedAdaptation` is how much of that excursion survives increased
 * contrast — the `ambientTint` axis, which already governs the material's
 * response to its surroundings, rather than a second policy of its own.
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.tintTone*` and
 * `.reducedTintAdaptation`, pinned in both directions by
 * `packages/calibration/test/tier-coherence.test.ts`.
 */
export interface TintToneConstants {
  readonly floor: number;
  readonly ceilMix: number;
  readonly low: number;
  readonly high: number;
  readonly reducedAdaptation: number;
}

export const TINT_TONE: TintToneConstants = {
  floor: 0.45,
  ceilMix: 0.45,
  low: 0.02,
  high: 0.65,
  reducedAdaptation: 0.35,
};

/**
 * Backdrop tone adaptation's curve, mirrored (W7).
 *
 * Apple's material takes the tone of a dark enough backdrop instead of sitting in
 * front of it, and it does so by size: over the settled bed's `dark-solid` the
 * reference's 44 px capsule adapts completely while its 96 px rrect keeps three
 * quarters of its own appearance. `sizeBias` is that gate, and it enters the
 * curve's argument rather than its amplitude — a thicker surface reads its
 * backdrop as brighter than it is.
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.backdropTone*`, pinned in
 * both directions by `packages/calibration/test/tier-coherence.test.ts`. The
 * numbers are authored there, with the measurement that chose them; this is a
 * mirror, not a second opinion.
 */
export interface BackdropToneConstants {
  readonly max: number;
  readonly low: number;
  readonly high: number;
  readonly sizeBias: number;
}

export const BACKDROP_TONE: BackdropToneConstants = {
  max: 1,
  low: 0.02,
  high: 0.14,
  sizeBias: 0.09,
};

/** The adaptation constants under a profile patch, by the renderer's merge rule. */
export function resolvedBackdropTone(patch?: RendererMaterialProfile): BackdropToneConstants {
  return {
    max: patch?.backdropToneMax ?? BACKDROP_TONE.max,
    low: patch?.backdropToneLow ?? BACKDROP_TONE.low,
    high: patch?.backdropToneHigh ?? BACKDROP_TONE.high,
    sizeBias: patch?.backdropToneSizeBias ?? BACKDROP_TONE.sizeBias,
  };
}

/**
 * How far the material's tint is pulled onto its backdrop, 0…1, before the
 * accessibility fold. Mirrors the renderer's `backdropToneAdaptation`.
 *
 * `thickness` is the size law's own factor, and it must be the **unfolded**
 * `sizeThickness`: the gate is geometric, and no preference changes how much
 * material stands between the viewer and the backdrop. (The shader is handed the
 * folded thickness and a bias pre-divided by the same cap; this tier has both
 * quantities in hand and takes the honest one directly.)
 */
export function backdropToneAdaptation(
  backdropLuminance: number,
  thickness: number,
  tone: BackdropToneConstants = BACKDROP_TONE,
): number {
  const x = backdropLuminance + tone.sizeBias * clamp01(thickness);
  const span = Math.max(tone.high - tone.low, 1e-6);
  const t = clamp01((x - tone.low) / span);
  return clamp01(tone.max) * (1 - t * t * (3 - 2 * t));
}

/**
 * How much of the adaptation survives an accessibility regime — the mirror of the
 * renderer's `backdropToneUnderPolicy`, and the same two folds.
 *
 * `ambientTint` is the axis the wave's composition contract names for how far the
 * material may move its colour, and it is what carries increased contrast and
 * forced colours. The refraction ladder read at the accessibility cap carries
 * reduced transparency, which touches no tint axis at all: at full strength this
 * axis dissolves a surface into its backdrop, which is precisely the occlusion
 * that preference asked to be *raised*, so the preference wins.
 */
export function backdropToneUnderPolicy(
  material: ResolvedMaterialPolicy,
  tone: TintToneConstants = TINT_TONE,
  refractionScale: Readonly<Record<"none" | "approximate" | "true", number>> =
    MATERIAL_SOURCE_REFRACTION_SCALE,
): number {
  const rung =
    material.refraction === "nominal"
      ? "true"
      : material.refraction === "reduced"
        ? "approximate"
        : "none";
  return tintToneAdaptation(material.ambientTint, tone) * refractionScale[rung];
}

/**
 * The material with the backdrop's tone folded onto its neutral tint — step two
 * of the composition contract (colour scheme → **backdrop adaptation** → author
 * tint), and the mirror of the renderer's `adaptedTintColour` and
 * `adaptedTintAlpha`.
 *
 * `backdrop` is the backdrop's **average** colour in linear light, because a
 * fully adapted material shows its backdrop's tone and a tone is a mean.
 *
 * Both the colour and the alpha move, and the alpha is the half a cross-tier
 * measurement forced. An adapting material stops transmitting as it takes its
 * backdrop's tone — the settled reference over the `impulse` backdrop is a flat
 * body with the grid hidden behind it. Adapting the colour alone left the
 * material fully transparent at full strength, and a transparent material cannot
 * cohere across these two tiers: the renderer blurs its backdrop in linear light
 * and `backdrop-filter` blurs in the encoded space, so over a high-dynamic-range
 * backdrop they show different pixels by construction. Measured: GPU over CSS
 * interior ratio 23.5 against a gated band of 0.80…1.25. A material that shows a
 * colour is tier-independent; one that shows its backdrop is not.
 */
export function adaptedSourceOptics(
  source: MaterialSourceOptics,
  backdrop: LinearRgb | undefined,
  adaptation: number,
): MaterialSourceOptics {
  const k = clamp01(adaptation);
  if (backdrop === undefined || k <= 0) return source;
  const alpha = source.tintAlpha + k * (1 - source.tintAlpha);
  if (alpha <= 0) return source;
  // The pair that makes the interior CONVERGE on the backdrop's tone, rather than
  // two independently lerped parameters — see the renderer's `adaptedTintColour`
  // for the cells that caught the difference.
  const weight = (1 - k) * source.tintAlpha;
  const mix = (index: 0 | 1 | 2): number =>
    (source.tint[index] * weight + backdrop[index] * k) / alpha;
  return { ...source, tint: [mix(0), mix(1), mix(2)], tintAlpha: alpha };
}

/**
 * An author's seed in the working space.
 *
 * Core carries the colour the author wrote — sRGB-encoded, because that is what
 * a CSS colour is — and every optical stage on both sides of the tier boundary
 * works in linear light. One decode, at the edge where the seed enters the
 * optics, so no downstream stage has to know which space it was handed.
 */
export function linearTint(tint: {
  readonly color: readonly [number, number, number];
  readonly strength: number;
}): { readonly color: LinearRgb; readonly strength: number } {
  return {
    color: [
      srgbDecode(tint.color[0]),
      srgbDecode(tint.color[1]),
      srgbDecode(tint.color[2]),
    ],
    strength: clamp01(tint.strength),
  };
}

/** The tone constants under a profile patch, by the renderer's own merge rule. */
export function resolvedTintTone(patch?: RendererMaterialProfile): TintToneConstants {
  return {
    floor: patch?.tintToneFloor ?? TINT_TONE.floor,
    ceilMix: patch?.tintToneCeilMix ?? TINT_TONE.ceilMix,
    low: patch?.tintToneLow ?? TINT_TONE.low,
    high: patch?.tintToneHigh ?? TINT_TONE.high,
    reducedAdaptation: patch?.reducedTintAdaptation ?? TINT_TONE.reducedAdaptation,
  };
}

/**
 * How much of the tone excursion the contrast regime allows.
 *
 * Mirrors the renderer's `tintToneAdaptation`. The author's colour is never
 * changed by a policy — only how far the material is allowed to move it.
 */
export function tintToneAdaptation(
  ambientTint: ResolvedMaterialPolicy["ambientTint"],
  tone: TintToneConstants = TINT_TONE,
): number {
  switch (ambientTint) {
    case "nominal":
      return 1;
    case "reduced":
      return tone.reducedAdaptation;
    case "none":
      return 0;
  }
}

/** The tone a seed shows over a given backdrop, linear light. Mirrors the renderer's `tintTone`. */
export function tintTone(
  seed: LinearRgb,
  backdropLuminance: number,
  toneAdaptation: number,
  tone: TintToneConstants = TINT_TONE,
): LinearRgb {
  const t = smoothstep(tone.low, tone.high, backdropLuminance);
  const k = clamp01(toneAdaptation);
  const channel = (index: 0 | 1 | 2): number => {
    const s = seed[index];
    const low = s * tone.floor;
    const high = s + (1 - s) * tone.ceilMix;
    return s + (low + (high - low) * t - s) * k;
  };
  return [channel(0), channel(1), channel(2)];
}

/**
 * The renderer's material for one tinted surface — the quantity this tier then
 * converts, and the quantity the GPU tier's foreground decision is taken against.
 *
 * The seed displaces the material's tint **colour** by its strength and leaves
 * the alpha exactly where the profile put it. That split is the whole design:
 * the colour axis is the author's (`Glass.tint(_:)`), the alpha axis is the
 * material's occlusion — what reduced transparency lifts, and where the system's
 * own Clear-to-Tinted preference will land.
 */
export function tintedSourceOptics(
  source: MaterialSourceOptics,
  tint: { readonly color: LinearRgb; readonly strength: number } | undefined,
  backdropLuminance: number,
  toneAdaptation: number,
  tone: TintToneConstants = TINT_TONE,
): MaterialSourceOptics {
  if (tint === undefined || tint.strength <= 0) return source;
  const shown = tintTone(tint.color, backdropLuminance, toneAdaptation, tone);
  const k = clamp01(tint.strength);
  const mix = (index: 0 | 1 | 2): number =>
    source.tint[index] + (shown[index] - source.tint[index]) * k;
  return { ...source, tint: [mix(0), mix(1), mix(2)] };
}

/**
 * The renderer's press-glow constants, mirrored — and the one slice of the
 * material that crosses this boundary with **no conversion at all**.
 *
 * `cssTintAlpha` exists because the body composites in two different spaces: the
 * renderer lerps toward the tint in linear light and the page lays an `rgba()`
 * overlay in encoded sRGB. The glow does not have that problem. The renderer's
 * highlight pass encodes before it blends — `encode_output` premultiplies
 * `linear_to_srgb(colour)` into a non-sRGB canvas format, so the blend runs on
 * encoded values under premultiplied source-over — which is exactly what a CSS
 * `rgba()` gradient over the tint does. The two are the same composite, so the
 * gain and the radius are the same numbers, and converting them would be
 * inventing a difference rather than correcting one.
 *
 * Top-level rather than per-variant because the renderer's profile carries them
 * there: one press glow, whichever variant the surface is drawn in.
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.glowRadiusCss` and
 * `.glowGain`, pinned in both directions by
 * `packages/calibration/test/tier-coherence.test.ts`.
 */
export interface MaterialSourceGlow {
  /** The glow's reach in CSS px, measured from the press point. */
  readonly radiusCss: number;
  /** Peak alpha at the press point, at `glow` = 1. */
  readonly gain: number;
}

export const MATERIAL_SOURCE_GLOW: MaterialSourceGlow = { radiusCss: 44, gain: 0.6 };

/** The glow constants under a profile patch, by the renderer's own merge rule. */
export function sourceGlow(patch?: RendererMaterialProfile): MaterialSourceGlow {
  return {
    radiusCss: patch?.glowRadiusCss ?? MATERIAL_SOURCE_GLOW.radiusCss,
    gain: patch?.glowGain ?? MATERIAL_SOURCE_GLOW.gain,
  };
}

/**
 * The size law's constants, mirrored — the slice of the material profile that
 * depends on **how big a surface is** rather than on which variant it is (W2).
 *
 * A mirror for `MaterialSourceOptics`'s reason: platform-web cannot import the
 * renderer (X7 keeps it behind core's lazy seam), so the numbers are restated and
 * `packages/calibration/test/tier-coherence.test.ts` pins them in both directions.
 * Unlike the optics they are **not per variant**: a surface's span is a fact about
 * the surface, and Apple states the rule about the material ("a larger size is
 * more opaque… it casts deeper, richer shadows… and a softer scattering of
 * light"), not about regular versus clear.
 *
 * Two of the three facets reach this tier. The scattering multiplies `blur()`'s σ
 * and the occlusion lifts the tint alpha; the inner shadow has no counterpart to
 * gain here, because this tier's only shadow is an outer `box-shadow` the
 * reference does not cast and whose alpha ships at zero (Decision Log #32(c)).
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.sizeSpanMin`,
 * `.sizeSpanMax`, `.sizeScatterGainMax` and `.sizeOcclusionGain`.
 */
export interface MaterialSourceSize {
  readonly sizeSpanMin: number;
  readonly sizeSpanMax: number;
  readonly sizeScatterGainMax: number;
  readonly sizeOcclusionGain: number;
  /**
   * The refraction ladder's scales, carried here because the size law folds under
   * the accessibility regime through them — see `sizeThicknessUnderPolicy`.
   */
  readonly refractionScale: Readonly<Record<"none" | "approximate" | "true", number>>;
}

export const MATERIAL_SOURCE_SIZE: MaterialSourceSize = {
  // MEASURED (W2). The band is where the settled reference's own size-dependence
  // happens; both gains ship at the identity, one because the fixtures cannot
  // resolve it and one because the fit puts it there. The reasons are stated
  // where the numbers are authored — `@vitrea/renderer-webgpu`'s
  // `DEFAULT_MATERIAL_PROFILE` — because this is a mirror, not a second opinion.
  sizeSpanMin: 32,
  sizeSpanMax: 96,
  sizeScatterGainMax: 1,
  sizeOcclusionGain: 0,
  refractionScale: { none: 0, approximate: 0.45, true: 1 },
};

/**
 * How much of a depth simulation each rung of the refraction ladder allows —
 * mirroring `@vitrea/renderer-webgpu`'s `MaterialProfile.refractionScale`.
 *
 * This tier never refracts, so it had no use for these until the size law needed
 * to fold under a preference (`sizeThicknessUnderPolicy`): the ladder is already
 * the profile's statement of how much depth a regime permits, and re-deriving a
 * second such number for the size law would be two answers to one question.
 * Patchable, and pinned against the renderer's by the tier-coherence test.
 */
export const MATERIAL_SOURCE_REFRACTION_SCALE: Readonly<Record<"none" | "approximate" | "true", number>> =
  { none: 0, approximate: 0.45, true: 1 };

export function sourceRefractionScale(
  patch?: RendererMaterialProfile,
): Readonly<Record<"none" | "approximate" | "true", number>> {
  return {
    none: patch?.refractionScale?.none ?? MATERIAL_SOURCE_REFRACTION_SCALE.none,
    approximate: patch?.refractionScale?.approximate ?? MATERIAL_SOURCE_REFRACTION_SCALE.approximate,
    true: patch?.refractionScale?.true ?? MATERIAL_SOURCE_REFRACTION_SCALE.true,
  };
}

/** The size-law constants under a profile patch, by the renderer's merge rule. */
export function sourceSize(patch?: RendererMaterialProfile): MaterialSourceSize {
  return {
    sizeSpanMin: patch?.sizeSpanMin ?? MATERIAL_SOURCE_SIZE.sizeSpanMin,
    sizeSpanMax: patch?.sizeSpanMax ?? MATERIAL_SOURCE_SIZE.sizeSpanMax,
    sizeScatterGainMax: patch?.sizeScatterGainMax ?? MATERIAL_SOURCE_SIZE.sizeScatterGainMax,
    sizeOcclusionGain: patch?.sizeOcclusionGain ?? MATERIAL_SOURCE_SIZE.sizeOcclusionGain,
    refractionScale: sourceRefractionScale(patch),
  };
}


/**
 * How thick a surface of this span reads, 0…1 — the size law's one input, and the
 * mirror of the renderer's `sizeThickness`.
 *
 * `spanPx` is the surface's **shorter** border-box extent, which is what the
 * renderer takes too: a 320×44 toolbar is a thin strip whichever way it is long.
 */
export function sizeThickness(
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return smoothstep(size.sizeSpanMin, size.sizeSpanMax, spanPx);
}

/**
 * The size law under an accessibility regime — the fold every other optic gets,
 * and the mirror of the renderer's `sizeThicknessUnderPolicy`.
 *
 * The scale is the refraction ladder read at the **accessibility** cap, because
 * that is already the number meaning "how much depth this preference allows" and
 * the whole law is a depth simulation. It is measured rather than assumed: with
 * the law unfolded, both accessibility profiles' large-span cells crossed their
 * adopted ΔE bounds while every light-standard cell improved — under
 * reduce-transparency Apple's material is nearly opaque and its interior level is
 * flat in span (0.9465 at 44 px, 0.9526 at 96), so there is no depth there for a
 * size term to add.
 *
 * Restated rather than imported from `refraction.ts`'s ladder for the same reason
 * the optics are mirrored, and pinned against the renderer's own numbers by
 * `packages/calibration/test/tier-coherence.test.ts`.
 */
export function sizeThicknessUnderPolicy(
  spanPx: number,
  material: ResolvedMaterialPolicy,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  const rung =
    material.refraction === "nominal"
      ? "true"
      : material.refraction === "reduced"
        ? "approximate"
        : "none";
  return sizeThickness(spanPx, size) * size.refractionScale[rung];
}

/**
 * The `blur()` σ a surface of this span runs at — the scattering facet.
 *
 * Also what a group's `samplingPadding` floor has to be taken over, at the
 * group's **largest** member: S1's 3σ rule is about the widest kernel any member
 * will actually sample with, and a floor derived from the nominal σ would starve a
 * large surface's proxy by exactly the gain.
 */
export function sizeScatterSigma(
  sigmaPx: number,
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return sizeScatterSigmaAt(sigmaPx, sizeThickness(spanPx, size), size);
}

/**
 * The same, for a caller that has already resolved the thickness factor — which
 * is every caller that has a policy to fold under.
 *
 * The two-function shape is deliberate and it is the same on both tiers: the
 * thickness form is the law, and the span form is the convenience that computes
 * an unfolded thickness for it. One formula, so a policy fold cannot accidentally
 * be applied to one facet and not another.
 */
export function sizeScatterSigmaAt(
  sigmaPx: number,
  thickness: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return sigmaPx * (1 + (size.sizeScatterGainMax - 1) * thickness);
}

/**
 * The tint alpha a surface of this span carries — the occlusion facet.
 *
 * Applied **after** `opticsUnderPolicy`, on this tier's own converted alpha,
 * which is where `occlusionAlphaUnderPolicy` already applies the accessibility
 * lift. Both close a fraction of whatever transparency is left, so they compose
 * in either order to within less than either term, and a preference outranking a
 * material law is the order that reads correctly.
 */
export function sizeOcclusionAlpha(
  alpha: number,
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return sizeOcclusionAlphaAt(alpha, sizeThickness(spanPx, size), size);
}

/** The same, for a caller that has already resolved the thickness factor. */
export function sizeOcclusionAlphaAt(
  alpha: number,
  thickness: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return clamp01(alpha + size.sizeOcclusionGain * thickness * (1 - alpha));
}

/**
 * The glow's alpha at the press point for a given `glow` channel value.
 *
 * The renderer's fragment is `radial² · glowGain · glow`; this is that product at
 * `radial` = 1, which is the peak the CSS tier's gradient starts from. Exported
 * for the same reason `cssTintAlpha` is: a reader checking the tiers against each
 * other should be able to evaluate the quantity rather than read it off a
 * gradient string.
 */
export function glowAlpha(optics: MaterialOptics, glow: number): number {
  return clamp01(optics.glowGain) * clamp01(glow);
}

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

/** The same transfer function, decode direction — an author's colour into the working space. */
function srgbDecode(encoded: number): number {
  const clamped = Math.min(1, Math.max(0, encoded));
  return clamped <= 0.04045 ? clamped / 12.92 : Math.pow((clamped + 0.055) / 1.055, 2.4);
}

/** Rec. 709 relative luminance, the weighting X5's linear-light pipeline uses. */
function luminance(rgb: LinearRgb): number {
  return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
}

const clamp01 = (value: number): number => Math.min(1, Math.max(0, value));

/** The renderer's own `smoothstep`, restated — same degradation to a step at a zero span. */
function smoothstep(edge0: number, edge1: number, x: number): number {
  if (edge1 <= edge0) return x < edge0 ? 0 : 1;
  const t = clamp01((x - edge0) / (edge1 - edge0));
  return t * t * (3 - 2 * t);
}

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
 * The encoded colour that reproduces the renderer's composite, channel for
 * channel, at the declared reference backdrop.
 *
 * `cssTintAlpha` solves one scalar on **luminance**, which is all a white tint
 * ever needed — an achromatic overlay at the solved alpha lands on the right
 * colour by construction. A chromatic tint does not: the alpha that matches the
 * luminance leaves the hue sitting wherever the two transfer functions put it,
 * and the error grows with saturation. So the colour is solved too, from the
 * same equation and the same alpha:
 *
 * ```
 * E(b)(1 − α′) + C′·α′ = E(b(1 − α) + t·α)      per channel
 * ```
 *
 * For an achromatic tint this returns exactly `encodeRgb(tint)` — the solve is
 * the same equation `cssTintAlpha` already satisfied — so it is a strict
 * extension of the mapping rather than a second one, and the untinted material
 * is untouched by it. Where a channel's answer falls outside the gamut it
 * clamps, and the two tiers then differ on that channel by whatever the clamp
 * cost; that is the same coherence floor this module's header states, reached by
 * saturation instead of by backdrop.
 */
export function cssTintColor(
  source: MaterialSourceOptics,
  cssAlpha: number,
  mapping: CssTierMapping = CSS_TIER_MAPPING,
): Rgb255 {
  if (cssAlpha <= mapping.minimumTintContrast) return encodeRgb(source.tint);
  const backdrop = mapping.referenceBackdropLuminance;
  const encodedBackdrop = srgbEncode(backdrop);
  const channel = (index: 0 | 1 | 2): number => {
    const composited = backdrop * (1 - source.tintAlpha) + source.tint[index] * source.tintAlpha;
    const solved = (srgbEncode(composited) - encodedBackdrop * (1 - cssAlpha)) / cssAlpha;
    return Math.round(clamp01(solved) * 255);
  };
  return [channel(0), channel(1), channel(2)];
}

/**
 * This tier's numbers for a surface whose material carries an author tint.
 *
 * Everything but the tint colour and its alpha is the untinted conversion,
 * unchanged, because nothing else about the material moved. The two that do move
 * go through the **same** mapping the profile's own tint goes through — the
 * alpha through `cssTintAlpha`, the colour through `cssTintColor` — so the tier
 * stays derived rather than gaining a second set of numbers to drift. A tint of
 * zero strength returns the base optics identically.
 */
export function tintedCssOptics(
  base: MaterialOptics,
  source: MaterialSourceOptics,
  tint: { readonly color: LinearRgb; readonly strength: number } | undefined,
  backdropLuminance: number,
  toneAdaptation: number,
  mapping: CssTierMapping = CSS_TIER_MAPPING,
  tone: TintToneConstants = TINT_TONE,
): MaterialOptics {
  if (tint === undefined || tint.strength <= 0) return base;
  return cssOpticsFromSource(
    base,
    tintedSourceOptics(source, tint, backdropLuminance, toneAdaptation, tone),
    mapping,
  );
}

/**
 * The same conversion, for a source the caller has already displaced — the
 * backdrop adaptation reaches this tier through here (W7), and the author tint
 * through `tintedCssOptics` above.
 *
 * Split out because the adaptation moves the material's colour on a surface that
 * carries no author tint at all, and every displacement has to land through one
 * conversion or the tier would gain a second set of numbers to drift.
 */
export function cssOpticsFromSource(
  base: MaterialOptics,
  source: MaterialSourceOptics,
  mapping: CssTierMapping = CSS_TIER_MAPPING,
): MaterialOptics {
  const alpha = cssTintAlpha(source, mapping);
  return { ...base, tintAlpha: alpha, tint: cssTintColor(source, alpha, mapping) };
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
 * A level the ink can be chosen from **without knowing the backdrop** — or
 * nothing, where the backdrop still decides it.
 *
 * Both level functions are monotonic in the backdrop, so evaluating them at 0
 * and at 1 brackets every level the surface can reach. When the whole bracket
 * lands on one side of the crossover the ink is decided for any backdrop
 * whatsoever, and returning a level from inside it is not a guess: it is the
 * answer the hinted path would have produced, established from the material
 * alone.
 *
 * **Used only where the material carries an author tint**, deliberately. A tint
 * is the app declaring what colour this surface is, and taking the ink decision
 * from a declaration is honouring it — the alternative is a saturated surface
 * wearing `light-dark()` ink chosen by a colour scheme that knows nothing about
 * it. The profile's own neutral tint is a different thing: a calibration
 * constant, on the material the measured bed describes, and the same bracket
 * would silently re-decide the ink on every untinted surface in the library.
 * That change is real and probably right — an untinted surface at the measured
 * 0.62 is already too opaque for the scheme to be deciding — but it belongs with
 * the adaptation work that owns the untinted material's behaviour, not here.
 */
export function boundedForegroundLevel(
  bounds: readonly [number, number],
  crossover: number,
): number | undefined {
  if (bounds[0] >= crossover) return bounds[0];
  if (bounds[1] < crossover) return bounds[1];
  return undefined;
}

/** Every level this tier's surface can reach, over the darkest and brightest backdrops. */
export function cssTierForegroundBounds(optics: MaterialOptics): readonly [number, number] {
  return [cssTierForegroundLevel(optics, 0), cssTierForegroundLevel(optics, 1)];
}

/** The same bracket on the renderer's composite. */
export function gpuTierForegroundBounds(
  source: MaterialSourceOptics,
): readonly [number, number] {
  return [gpuTierForegroundLevel(source, 0), gpuTierForegroundLevel(source, 1)];
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
  const glow = sourceGlow(patch);
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
      // Unconverted, and the mapping carries no constant for them — see
      // `MaterialSourceGlow`. The colour is the highlight, which is also what the
      // border reads: one highlight, two features that use it.
      glowRadius: glow.radiusCss,
      glowGain: clamp01(glow.gain),
      glow: encodeRgb(source.highlight),
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
 *
 * Mirrored by `@vitrea/renderer-webgpu`'s `MaterialProfile.reducedTransparencyFrost`
 * and pinned in both directions by `packages/calibration/test/tier-coherence.test.ts`.
 */
export const REDUCED_TRANSPARENCY_FROST = 1.75;

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
 * A drawn border rather than a rim highlight (§Accessibility: "stronger borders").
 *
 * **These cross the tier boundary unconverted, and that is a decision.** Every
 * other renderer quantity this tier reads goes through `CssTierMapping` —
 * `rimAlpha` in particular becomes `borderAlpha` via `borderAlphaPerRimAlpha`.
 * That constant is fitted for the *nominal* regime, where the renderer's ambient
 * rim highlight and this tier's drawn border are different constructs and the
 * fitted number is what absorbs the difference. The strong-border regime is not
 * that: it is an accessibility floor stated in near-opaque terms, and at near
 * opacity the thing the mapping exists to correct for stops existing — a line at
 * α = 0.95 reads the same whether it composites in linear light or in encoded
 * sRGB. A constant fitted on the nominal rim has nothing true to say about it,
 * and applying one anyway would cost the identity that makes this safe: 0.95
 * would stop being 0.95.
 *
 * The trade, stated rather than hidden: an author who patches
 * `strongBorderRim.rimAlpha` well below opaque leaves the near-opaque regime the
 * identity is justified by, and the two tiers will then measurably diverge. That
 * is their informed choice about an accessibility floor they chose to lower, not
 * something the mapping should silently correct.
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.strongBorderRim`
 * (`rimWidth`, `rimAlpha`) and is pinned in both directions by
 * `packages/calibration/test/tier-coherence.test.ts`.
 */
export const STRONG_BORDER: Pick<MaterialOptics, "borderWidth" | "borderAlpha"> = {
  borderWidth: 2,
  borderAlpha: 0.95,
};

/**
 * The profile fields the *policy* fold reads, as opposed to the ones the tier
 * conversion reads.
 *
 * `cssTierOptics` converts a profile's per-variant optics into this tier's alpha
 * space and hands back numbers. These are different: they are what the
 * accessibility regime does to whatever numbers it is given, so they survive the
 * conversion — as multipliers, or in the strong border's case as an identity —
 * and cannot ride along inside the converted optics. They therefore travel
 * beside them, as one value rather than as loose scalars: bare `number`s side by
 * side at a call site are one transposition away from being the bug they exist
 * to prevent.
 */
export interface PolicyFoldConstants {
  readonly increasedOcclusionLift: number;
  readonly reducedTransparencyFrost: number;
  readonly strongBorder: Pick<MaterialOptics, "borderWidth" | "borderAlpha">;
}

/** The shipped profile's policy constants — the mirrored defaults. */
export const POLICY_FOLD_CONSTANTS: PolicyFoldConstants = {
  increasedOcclusionLift: INCREASED_OCCLUSION_LIFT,
  reducedTransparencyFrost: REDUCED_TRANSPARENCY_FROST,
  strongBorder: STRONG_BORDER,
};

/**
 * What a profile patch resolves them to, by the renderer's own merge rule
 * (`withMaterialOverrides`): a field the patch does not name keeps the mirrored
 * default.
 *
 * All three are *patchable* profile fields and the renderer already honours the
 * patched values. Anything on this side that models what the renderer drew — the
 * GPU tier's foreground decision — or that paints its own folded material — the
 * CSS tier — has to resolve them the same way, or a calibration patch would move
 * the material without moving the decision taken against it. That is the
 * decision-vs-render divergence Decision Log #32(b) exists to prevent, and the
 * tier gap K5 (#32(a)) closed, reappearing through the patch rather than through
 * a second copy of the constant.
 *
 * The strong border merges per field, not as a whole, because the renderer's
 * `withMaterialOverrides` does: a patch naming only the width keeps the mirrored
 * alpha rather than dropping it.
 */
export function resolvedPolicyFold(patch?: RendererMaterialProfile): PolicyFoldConstants {
  return {
    increasedOcclusionLift: patch?.increasedOcclusionLift ?? INCREASED_OCCLUSION_LIFT,
    reducedTransparencyFrost: patch?.reducedTransparencyFrost ?? REDUCED_TRANSPARENCY_FROST,
    strongBorder: {
      borderWidth: patch?.strongBorderRim?.rimWidth ?? STRONG_BORDER.borderWidth,
      borderAlpha: patch?.strongBorderRim?.rimAlpha ?? STRONG_BORDER.borderAlpha,
    },
  };
}

/** Ambient tint pulled back under increased contrast. */
const REDUCED_TINT_SATURATION = 1;

/**
 * Fold core's resolved material *regime* onto this package's numbers.
 *
 * core says which regime applies; nothing here re-decides that. Each branch is
 * one axis of `ResolvedMaterialPolicy`, so a new axis in core surfaces as a
 * missing branch here rather than as silence.
 *
 * `fold` is the policy constants of the profile these optics were derived from
 * (`resolvedPolicyFold`). They are a parameter because this function receives no
 * profile: the optics arriving here are already converted to this tier's alpha
 * space, and the patch that produced them is only in scope at the call site. The
 * default is the shipped set, so an unpatched caller folds exactly the numbers it
 * always did.
 */
export function opticsUnderPolicy(
  optics: MaterialOptics,
  policy: ResolvedMaterialPolicy,
  fold: PolicyFoldConstants = POLICY_FOLD_CONSTANTS,
): MaterialOptics {
  let next = optics;

  if (policy.frost === "increased") {
    next = { ...next, blurRadius: next.blurRadius * fold.reducedTransparencyFrost };
  } else if (policy.frost === "none") {
    next = { ...next, blurRadius: 0 };
  }

  next = {
    ...next,
    tintAlpha: occlusionAlphaUnderPolicy(
      next.tintAlpha,
      policy.occlusion,
      fold.increasedOcclusionLift,
    ),
  };

  if (policy.border === "strong") next = { ...next, ...fold.strongBorder };

  if (policy.ambientTint === "reduced") next = { ...next, saturation: REDUCED_TINT_SATURATION };
  else if (policy.ambientTint === "none") next = { ...next, saturation: 1 };

  return next;
}
