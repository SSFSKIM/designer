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

import {
  accessibilityRefractionCap,
  DEFAULT_REFRACTION_SCALE,
  REFRACTION_LADDER,
  type RefractionQuality,
  type RefractionScale,
} from "@vitrea/policy";
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
  /*
   * The five numbers below are the band's own geometry and the inner shadow's,
   * mirrored since W17 G1 (Decision Log 2 (b)–(c); claims §5.74 §3–§4).
   *
   * They were outside the mirror while this tier converted only the four fields
   * above, because it draws the rim as a one-pixel border and draws no inner
   * shadow at all. The interior LEVEL needs them anyway: the renderer's rim band
   * and its highlight are light added inside the silhouette, and its inner shadow
   * is a multiplicative darkening of the whole composite, so a tier that lands on
   * the renderer's interior has to carry all three as derived quantities even
   * though it draws none of them as features. `interiorBandLight` and
   * `interiorShadowKeep` are where they are read.
   */
  /** The rim band's half-width in CSS px — `MaterialOptics.rimWidth`. */
  readonly rimWidth: number;
  /** The specular exponent on the same band — `MaterialOptics.specularPower`. */
  readonly specularPower: number;
  /** The specular gain on the same band — `MaterialOptics.specularGain`. */
  readonly specularGain: number;
  /** The inner shadow's peak darkening at the contour — `MaterialOptics.shadowDepth`. */
  readonly shadowDepth: number;
  /** The inner shadow's own alpha — `MaterialOptics.shadowAlpha`. */
  readonly shadowAlpha: number;
}

/** Mirrors `@vitrea/renderer-webgpu`'s `DEFAULT_MATERIAL_PROFILE.optics`. */
export const MATERIAL_SOURCE_OPTICS: Readonly<Record<MaterialVariant, MaterialSourceOptics>> = {
  // σ = 3 and `tintAlpha` 0.46 are the recalibration cascade's active-bed values
  // (2026-08-31); carrying them here rather than a second advisory is the whole
  // point of K5. core's `samplingPadding` advisory derives from the resolved blur
  // (W6), so it follows this number down rather than needing its own edit.
  // σ 1.25 since W11c (claims §5.41): the reference's interior is a sharp
  // component near σ 1.25 plus a heavy one the scatter facet supplies; the
  // cascade's 3 was the one Gaussian that best split the difference.
  regular: {
    blurSigma: 1.25,
    tint: [1, 1, 1],
    tintAlpha: 0.46,
    rimAlpha: 0.18,
    highlight: [1, 1, 1],
    rimWidth: 1.5,
    specularPower: 6,
    specularGain: 0.55,
    shadowDepth: 0.35,
    // 0.55 → 0.05 in the 2026-08-31 refit: the inner shadow was darkening the
    // contour faster than the rim lit it. The number's reasons are authored in
    // the renderer's profile; this is the mirror.
    shadowAlpha: 0.05,
  },
  // Persistently more transparent, so it frosts less and tints less — and it
  // carries its own dimming policy from core. Uncalibrated in either tier: the
  // canonical scene matrix has no clear-variant scene.
  clear: {
    blurSigma: 4,
    tint: [1, 1, 1],
    tintAlpha: 0.1,
    rimAlpha: 0.14,
    highlight: [1, 1, 1],
    rimWidth: 1.25,
    specularPower: 8,
    specularGain: 0.45,
    shadowDepth: 0.22,
    shadowAlpha: 0.4,
  },
};

/**
 * The renderer's own light direction and the two size gains its inner shadow
 * rides, mirrored (W17 G1; Decision Log 2 (b)).
 *
 * A profile-level block rather than three fields on `MaterialSourceOptics`
 * because that is where the renderer keeps them: `lightDirection` lights every
 * variant's band from one place, and the two gains are size-law facets the
 * shadow reads. They reach this tier for one purpose only — the derived interior
 * light of `interiorBandLight` and the keep factor of `interiorShadowKeep` — and
 * nothing this tier DRAWS reads them.
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.lightDirection`,
 * `.lensSizeGainMax` and `.sizeShadowGainMax`, pinned in both directions by
 * `packages/calibration/test/tier-coherence.test.ts`.
 */
export interface MaterialSourceInteriorLight {
  /** The unit direction the band is lit from, in the surface's own 2D frame. */
  readonly lightDirection: readonly [number, number];
  /**
   * The inner shadow's DEPTH gain — `MaterialProfile.lensSizeGainMax`, which the
   * shader reads as `shadowLensDepth = thickness · (1 + (gain − 1) · sizeK)`.
   * It is the lens's constant by name and the shadow's by use; the lens stopped
   * reading it at W12 G2 and the occlusion kept it.
   */
  readonly shadowDepthGainMax: number;
  /**
   * The inner shadow's AMPLITUDE gain with the span —
   * `MaterialProfile.sizeShadowGainMax`, 1 on the landed profile, so the facet
   * is inert until a profile patches it.
   */
  readonly shadowAmplitudeGainMax: number;
}

/** Mirrors `@vitrea/renderer-webgpu`'s three profile-level interior constants. */
export const MATERIAL_SOURCE_INTERIOR_LIGHT: MaterialSourceInteriorLight = {
  lightDirection: [-0.3714, -0.9285],
  shadowDepthGainMax: 2.6,
  shadowAmplitudeGainMax: 1,
};

/** The same block, resolved against a material profile document. */
export function sourceInteriorLight(
  patch?: RendererMaterialProfile,
): MaterialSourceInteriorLight {
  return {
    lightDirection: patch?.lightDirection ?? MATERIAL_SOURCE_INTERIOR_LIGHT.lightDirection,
    shadowDepthGainMax:
      patch?.lensSizeGainMax ?? MATERIAL_SOURCE_INTERIOR_LIGHT.shadowDepthGainMax,
    shadowAmplitudeGainMax:
      patch?.sizeShadowGainMax ?? MATERIAL_SOURCE_INTERIOR_LIGHT.shadowAmplitudeGainMax,
  };
}

/**
 * The author tint's shade law, mirrored (W10) — what makes a tint a tint.
 *
 * Apple's tint is "a **range of tones** that are mapped to content brightness
 * underneath the tinted element" (S219), and the range was measured per pixel
 * (claims §5.36): the tinted material is an OPAQUE layer of the seed at a shade
 * linear in the luminance the untinted material shows at that pixel — `dark`
 * of the seed over black content, the seed itself over white, hue intact —
 * composited over the material at the author's opacity in the encoded space.
 * Over a checkerboard the reference shows light and dark orange, not orange
 * glass with the checker behind it.
 *
 * `strength` is the law's provenance gate (1 where measured, 0 on the dark
 * scheme, which renders the pure seed). `reducedAdaptation` is how much of the
 * excursion survives increased contrast — the `ambientTint` axis, which already
 * governs the material's response to its surroundings, rather than a second
 * policy of its own.
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.tintShade*` and
 * `.reducedTintAdaptation`, pinned in both directions by
 * `packages/calibration/test/tier-coherence.test.ts`.
 */
export interface TintShadeConstants {
  readonly dark: number;
  readonly light: number;
  readonly strength: number;
  readonly reducedAdaptation: number;
}

// MEASURED (W10, 2026-09-02): fitted on the W9 probe's five tinted cells,
// refereed by the canonical bed. The numbers are authored in the renderer's
// profile with the measurement that chose them; this is a mirror.
export const TINT_SHADE: TintShadeConstants = {
  dark: 0.5289,
  light: 1.0175,
  strength: 1,
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
  high: 0.055,
  sizeBias: 0.05,
};

/**
 * The backdrop tone response (W9), mirrored — the law that owns the interior
 * MEAN, where the four collapse constants above own texture and nothing else.
 *
 * `anchorX` is the three solid anchors' ENCODED-space backdrop means; `thin`
 * and `thick` are the reference's settled interior levels there at
 * `sizeThickness` 0 and saturated. Authored in the renderer's material.ts
 * (`backdropToneAnchorX` and friends, with the probe evidence); this is a
 * mirror, not a second opinion — pinned by `tier-coherence.test.ts`.
 */
export interface BackdropToneResponseConstants {
  readonly anchorX: readonly [number, number, number];
  readonly thin: readonly [number, number, number];
  readonly thick: readonly [number, number, number];
  /** The law's per-profile authority, 0…1 — 0 on dark profiles, whose response
   * is unmeasured (the anchors are LIGHT-reference measurements). */
  readonly strength: number;
}

export const BACKDROP_TONE_RESPONSE: BackdropToneResponseConstants = {
  anchorX: [0.1104, 0.2706, 0.9505],
  thin: [0.0126, 0.4561, 0.9713],
  thick: [0.4953, 0.5744, 0.9358],
  strength: 1,
};

/** The response constants under a profile patch, by the renderer's merge rule. */
export function resolvedBackdropToneResponse(
  patch?: RendererMaterialProfile,
): BackdropToneResponseConstants {
  return {
    anchorX: patch?.backdropToneAnchorX ?? BACKDROP_TONE_RESPONSE.anchorX,
    thin: patch?.backdropToneResponseThin ?? BACKDROP_TONE_RESPONSE.thin,
    thick: patch?.backdropToneResponseThick ?? BACKDROP_TONE_RESPONSE.thick,
    strength: patch?.backdropToneResponseStrength ?? BACKDROP_TONE_RESPONSE.strength,
  };
}

/**
 * The response curve `R(encodedInput, thickness)` — the settled interior level
 * the reference shows at this encoded-space backdrop mean. Mirrors the
 * renderer's `backdropToneResponse` term for term: monotone (Fritsch–Carlson)
 * interpolation through the anchors, clamped to their span, smoothstep between
 * the rows.
 */
export function backdropToneResponseLevel(
  encodedInput: number,
  thickness: number,
  response: BackdropToneResponseConstants = BACKDROP_TONE_RESPONSE,
): number {
  const xs = response.anchorX;
  const tk = clamp01(thickness);
  const f = tk * tk * (3 - 2 * tk);
  const ys = [0, 1, 2].map(
    (i) => (response.thin[i] ?? 0) + ((response.thick[i] ?? 0) - (response.thin[i] ?? 0)) * f,
  ) as [number, number, number];

  const x = Math.min(xs[2], Math.max(xs[0], encodedInput));
  const h0 = Math.max(xs[1] - xs[0], 1e-4);
  const h1 = Math.max(xs[2] - xs[1], 1e-4);
  const d0 = (ys[1] - ys[0]) / h0;
  const d1 = (ys[2] - ys[1]) / h1;
  const m1 = d0 * d1 <= 0 ? 0 : (2 * d0 * d1) / (d0 + d1);
  const seg = x <= xs[1] ? 0 : 1;
  const h = seg === 0 ? h0 : h1;
  const t = (x - (seg === 0 ? xs[0] : xs[1])) / h;
  const y0 = seg === 0 ? ys[0] : ys[1];
  const y1 = seg === 0 ? ys[1] : ys[2];
  const s0 = seg === 0 ? d0 : m1;
  const s1 = seg === 0 ? m1 : d1;
  return (
    y0 * (1 + 2 * t) * (1 - t) * (1 - t) +
    s0 * h * t * (1 - t) * (1 - t) +
    y1 * t * t * (3 - 2 * t) +
    s1 * h * t * t * (t - 1)
  );
}

/**
 * The response solve on a source's neutral tint (W9) — the CSS half of the
 * shader's `solvedNeutral`, mirrored on the same closed form. The composite
 * under `adaptedSourceOptics` reduces to
 * `mean = (1 − k)·((1 − α)·bgLinear + α·L(tint)) + k·toneLuminance`, so the
 * tint's luma is shifted, achromatically, to land the post-collapse mean on
 * `R(encodedInput, thickness)`. The solve's authority fades to zero below the
 * dark anchor (the impulse domain the collapse constants were fitted on) and
 * stands down entirely at k → 1, where the collapse owns the surface.
 */
export function toneRespondedSourceOptics(
  source: MaterialSourceOptics,
  sample: { readonly luminance: number; readonly linearLuminance: number },
  thickness: number,
  adaptation: number,
  strength: number,
  response: BackdropToneResponseConstants = BACKDROP_TONE_RESPONSE,
): MaterialSourceOptics {
  const k = clamp01(adaptation);
  const alpha = source.tintAlpha;
  const responseStrength = clamp01(strength) * clamp01(response.strength);
  if (responseStrength <= 0 || alpha <= 1e-3 || k >= 0.995) return source;
  const encodedInput = srgbEncode(clamp01(sample.luminance));
  const anchor = Math.max(response.anchorX[0], 1e-4);
  const authorityT = clamp01((encodedInput - anchor * 0.5) / (anchor * 0.5));
  const authority = (authorityT * authorityT * (3 - 2 * authorityT)) * responseStrength;
  if (authority <= 0) return source;
  const target = backdropToneResponseLevel(encodedInput, thickness, response);
  // The collapse's mean pull is toward L(the LINEAR mean colour), not toward
  // the encoded level — the shader's own comment, mirrored.
  const preCollapse = (target - k * sample.linearLuminance) / (1 - k);
  const tintLuma =
    0.2126 * source.tint[0] + 0.7152 * source.tint[1] + 0.0722 * source.tint[2];
  const nominal = (1 - alpha) * sample.linearLuminance + alpha * tintLuma;
  const shift = ((preCollapse - nominal) / alpha) * authority * clamp01(strength);
  const tint: [number, number, number] = [
    clamp01(source.tint[0] + shift),
    clamp01(source.tint[1] + shift),
    clamp01(source.tint[2] + shift),
  ];
  // The light attractor needs OPACITY (the shader's own comment, mirrored): a
  // neutral already at white clamps every upward shift to nothing, and the
  // reference's light-adapted state is the material gone opaque-bright. The
  // truncated remainder is carried by the alpha, solved against the same
  // composite and folded by the same authority. One-sided: darkward opacity is
  // the collapse's axis.
  const solvedLuma = 0.2126 * tint[0] + 0.7152 * tint[1] + 0.0722 * tint[2];
  const achieved = (1 - alpha) * sample.linearLuminance + alpha * solvedLuma;
  let tintAlpha = source.tintAlpha;
  if (preCollapse > achieved + 1e-4 && solvedLuma > sample.linearLuminance + 1e-3) {
    const alphaTarget = Math.min(
      1,
      Math.max(alpha, (preCollapse - sample.linearLuminance) / (solvedLuma - sample.linearLuminance)),
    );
    tintAlpha = alpha + (alphaTarget - alpha) * authority * clamp01(strength);
  }
  return { ...source, tint, tintAlpha };
}

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
  shade: TintShadeConstants = TINT_SHADE,
  refractionScale: RefractionScale = MATERIAL_SOURCE_REFRACTION_SCALE,
): number {
  return tintToneAdaptation(material.ambientTint, shade) * refractionScale[accessibilityRefractionCap(material)];
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
  return {
    ...source,
    tint: [mix(0), mix(1), mix(2)],
    tintAlpha: alpha,
    // The rim fades with the adaptation, and it is this tier's border that reads
    // it (`borderAlphaPerRimAlpha`). A material that has taken its backdrop's tone
    // has no lit edge to show, and the reference agrees on a calibration cell
    // rather than by inference: `dark-solid__capsule-button__rest` is
    // byte-identical to its own background, rim included. Left in, the border is a
    // white outline around a surface that is meant not to be there.
    rimAlpha: source.rimAlpha * (1 - k),
  };
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

/** The shade constants under a profile patch, by the renderer's own merge rule. */
export function resolvedTintShade(patch?: RendererMaterialProfile): TintShadeConstants {
  return {
    dark: patch?.tintShadeDark ?? TINT_SHADE.dark,
    light: patch?.tintShadeLight ?? TINT_SHADE.light,
    strength: patch?.tintShadeStrength ?? TINT_SHADE.strength,
    reducedAdaptation: patch?.reducedTintAdaptation ?? TINT_SHADE.reducedAdaptation,
  };
}

/**
 * How much of the shade excursion the contrast regime allows.
 *
 * Mirrors the renderer's `tintToneAdaptation`. The author's colour is never
 * changed by a policy — only how far the material is allowed to move it.
 */
export function tintToneAdaptation(
  ambientTint: ResolvedMaterialPolicy["ambientTint"],
  shade: TintShadeConstants = TINT_SHADE,
): number {
  switch (ambientTint) {
    case "nominal":
      return 1;
    case "reduced":
      return shade.reducedAdaptation;
    case "none":
      return 0;
  }
}

/**
 * The shade a seed is painted at over a material of luminance `u`. Mirrors the
 * renderer's `tintShade`: linear between the two ends, clamped so a shade is
 * never brighter than the seed, folded toward 1 by `grip` (the regime's
 * adaptation × the profile's provenance gate × (1 − collapse)).
 */
export function tintShade(
  materialLuminance: number,
  grip: number,
  shade: TintShadeConstants = TINT_SHADE,
): number {
  const u = clamp01(materialLuminance);
  const level = clamp01(shade.dark + (shade.light - shade.dark) * u);
  return 1 + (level - 1) * clamp01(grip);
}

/** The opaque layer an author tint paints, linear light. Mirrors the renderer's `tintShadeLayer`. */
export function tintShadeLayer(
  seed: LinearRgb,
  materialLuminance: number,
  grip: number,
  shade: TintShadeConstants = TINT_SHADE,
): LinearRgb {
  const level = tintShade(materialLuminance, grip, shade);
  return [seed[0] * level, seed[1] * level, seed[2] * level];
}

/** The luminance the untinted material shows over a backdrop of the given luminance. */
function materialLuminance(source: MaterialSourceOptics, backdropLuminance: number): number {
  const alpha = clamp01(source.tintAlpha);
  return (1 - alpha) * backdropLuminance + alpha * luminance(source.tint);
}

/**
 * The renderer's material for one tinted surface, as one linear-light source —
 * the quantity the GPU tier's foreground decision is taken against.
 *
 * The author's layer is opaque and lands at the author's opacity (W10), so
 * both the colour AND the alpha move: the folded alpha is `1 − (1 − s)(1 − α)`
 * and the colour is the alpha-weighted mix of the material's tint and the
 * layer. That fold is exact in the encoded space the layer composites in
 * (`tintedCssOptics` does it there); this linear-light statement of it is
 * exact at strength 0 and 1 and a threshold-grade approximation between, which
 * is all the ink decision reads from it.
 */
export function tintedSourceOptics(
  source: MaterialSourceOptics,
  tint: { readonly color: LinearRgb; readonly strength: number } | undefined,
  backdropLuminance: number,
  grip: number,
  shade: TintShadeConstants = TINT_SHADE,
): MaterialSourceOptics {
  if (tint === undefined || tint.strength <= 0) return source;
  const s = clamp01(tint.strength);
  const layer = tintShadeLayer(tint.color, materialLuminance(source, backdropLuminance), grip, shade);
  const alpha = clamp01(source.tintAlpha);
  const folded = 1 - (1 - s) * (1 - alpha);
  const mix = (index: 0 | 1 | 2): number =>
    ((1 - s) * alpha * source.tint[index] + s * layer[index]) / folded;
  return { ...source, tint: [mix(0), mix(1), mix(2)], tintAlpha: folded };
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
 * `.sizeSpanMax`, `.sizeScatterGainMax`, `.sizeScatterFloor`, the four
 * `.sizeScatterRamp*` constants and `.sizeOcclusionGain`.
 */
export interface MaterialSourceSize {
  readonly sizeSpanMin: number;
  readonly sizeSpanMax: number;
  readonly sizeScatterGainMax: number;
  /**
   * The scatter facet's frost (W11c): the mix every surface carries whatever
   * its size, and the value the whole facet folds to under an accessibility
   * preference. See `scatterThickness`.
   */
  readonly sizeScatterFloor: number;
  /**
   * The scatter facet's span curve (W11c): the top of the band the frost rises
   * to, and since W13 G1 the depth ramp's deep value. See `scatterThickness`.
   */
  readonly sizeScatterSpanMax: number;
  /**
   * The body's second scale (W15 G1, claims §5.69 §1–§2, landed at §5.70 §8):
   * the heavy width's gain, the deep value's floor and the deep value's span
   * top, each read again at dpr 2, because the reference's 2x deep interior is
   * fully heavy on the two largest spans where the 1x curve leaves a sharp
   * share of 0.24–0.36. Interpolated by `rampAtScale` exactly as the ramp's
   * anchors are, and read only above dpr 1 — so nothing at dpr 1 moves at all.
   *
   * Since W16 G1 the CSS tier reads these at the **live** ratio like everything
   * else it draws (charter Decision Log 2 (c)): its two layers are device-pixel
   * widths and its mask is the renderer's own ramp at the ratio the page is
   * composited at, so a mirror that lagged the scale would be two materials.
   * `tier-coherence` pins the two mirrors over dpr {1, 1.5, 2, 3}.
   */
  readonly sizeScatterGainMax2x: number;
  readonly sizeScatterFloor2x: number;
  readonly sizeScatterSpanMax2x: number;
  /**
   * The 2x gain's own SPAN grading (W15 G1's re-form, claims §5.70 §4 and §7) —
   * the heavy width's gain at the top of the scatter span curve at dpr 2.
   *
   * The reference's heavy kernel is not one width: it grows from about 8 device
   * px at span 96 to about 11 at span 160 (claims §5.69 §1), and a single 2x
   * gain left the largest span's deep interior 40% too structured. So the gain
   * rises from `sizeScatterGainMax2x` at `sizeSpanMax` to this at
   * `sizeScatterSpanMax`, along the same smoothstep the ramp's far anchor
   * declines on, landed at 9.9 over a base gain of 4.8 (claims §5.70 §8).
   * Interpolated from the 1x gain, so at dpr ≤ 1 the two ends coincide and the
   * grading is flat — the wave's binding rule by construction.
   *
   * Mirrored here for the same reason the three above are, and since W16 G1 drawn
   * for the same reason too: the CSS tier's heavy layer takes its width from
   * `scatterGainAt` at the live ratio, so this grading reaches its output.
   */
  readonly sizeScatterGainFar2x: number;
  /**
   * The body's depth ramp (W13 G1, claims §5.61 §2, §5.64 §5): the sharp
   * component's share at the contour — graded from the thin anchor to the thick
   * one across `sizeThickness`, because G0 read that start much higher on thin
   * spans than thick ones — and the reach at which its excursion vanishes into
   * the span curve above. Each anchored at dpr 1 and dpr 2 and interpolated
   * between. This tier cannot render a ramp — one `backdrop-filter` has one σ —
   * so what it carries is the ramp's per-surface projection, which is what
   * `scatterThickness` computes on both tiers. See `scatterThickness`.
   */
  readonly sizeScatterRampStartThin1x: number;
  readonly sizeScatterRampStartThick1x: number;
  readonly sizeScatterRampStartFar1x: number;
  readonly sizeScatterRampStartThin2x: number;
  readonly sizeScatterRampStartThick2x: number;
  readonly sizeScatterRampStartFar2x: number;
  readonly sizeScatterRampReach1xPx: number;
  readonly sizeScatterRampReach2xPx: number;
  readonly sizeOcclusionGain: number;
  /**
   * The refraction ladder's scales, carried here because the size law folds under
   * the accessibility regime through them — see `sizeThicknessUnderPolicy`.
   */
  readonly refractionScale: RefractionScale;
}

export const MATERIAL_SOURCE_SIZE: MaterialSourceSize = {
  // MEASURED (W2; the scatter facet W11c). The band is where the settled
  // reference's own size-dependence happens. The scatter facet's gain, floor
  // and band top are the declared G1 fit on the W9 probe bed (claims §5.41).
  // The reasons are stated where the numbers are authored —
  // `@vitrea/renderer-webgpu`'s `DEFAULT_MATERIAL_PROFILE` — because this is a
  // mirror, not a second opinion.
  sizeSpanMin: 32,
  sizeSpanMax: 96,
  sizeScatterGainMax: 8,
  sizeScatterFloor: 0.4,
  sizeScatterSpanMax: 256,
  sizeScatterGainMax2x: 4.8,
  sizeScatterFloor2x: 1,
  sizeScatterSpanMax2x: 256,
  sizeScatterGainFar2x: 9.9,
  sizeScatterRampStartThin1x: 0.72,
  sizeScatterRampStartThick1x: 0.52,
  sizeScatterRampStartFar1x: 0.2,
  sizeScatterRampStartThin2x: 0.46,
  sizeScatterRampStartThick2x: 0.21,
  sizeScatterRampStartFar2x: 0.21,
  sizeScatterRampReach1xPx: 80,
  sizeScatterRampReach2xPx: 100,
  sizeOcclusionGain: 0.05,
  refractionScale: DEFAULT_REFRACTION_SCALE,
};

/**
 * How much of a depth simulation each rung of the refraction ladder allows.
 *
 * This tier never refracts, so it had no use for these until the size law needed
 * to fold under a preference (`sizeThicknessUnderPolicy`): the ladder is already
 * the profile's statement of how much depth a regime permits, and re-deriving a
 * second such number for the size law would be two answers to one question.
 *
 * It was a hand-written mirror of `@vitrea/renderer-webgpu`'s
 * `MaterialProfile.refractionScale` — in fact one of *three* copies of the same
 * table, counting the one `MATERIAL_SOURCE_SIZE` above carried — held together by
 * the tier-coherence test. Decision Log #23(d) made it the same table:
 * `@vitrea/policy` authors the default beside the ladder it is keyed by, and both
 * tiers name it. Nothing else about the mapping changed, and no number moved.
 *
 * Still patchable, and the merge below is still this tier's own: the two tiers
 * agreeing on the *default* is not the same claim as the two tiers merging a
 * calibration patch the same way, and tier-coherence goes on pinning the second.
 */
export const MATERIAL_SOURCE_REFRACTION_SCALE: RefractionScale = DEFAULT_REFRACTION_SCALE;

export function sourceRefractionScale(patch?: RendererMaterialProfile): RefractionScale {
  const scale = {} as Record<RefractionQuality, number>;
  for (const rung of REFRACTION_LADDER) {
    scale[rung] = patch?.refractionScale?.[rung] ?? MATERIAL_SOURCE_REFRACTION_SCALE[rung];
  }
  return scale;
}

/**
 * The outer shadow's constants, mirrored (W8).
 *
 * Mirrors `@vitrea/renderer-webgpu`'s `MaterialProfile.outerShadow`, field for
 * field and value for value, for `MaterialSourceOptics`'s reason — and this is
 * the mirror that matters most, because this is the one facet where the two tiers
 * paint the *same* thing by the *same* algebra rather than one approximating the
 * other. See `MaterialOuterShadow` for how the numbers were measured; the reasons
 * live where the numbers are authored, because this is a mirror.
 *
 * ## Why a `box-shadow` is an honest multiplicative occlusion
 *
 * The reference removes a fraction of the backdrop's own light — it darkens a
 * bright backdrop hard, a dark one barely, and a black one not at all. A
 * `box-shadow` is a constant colour composited source-over, which sounds like the
 * opposite; it is not, because the colour is BLACK:
 *
 *   out = (1 − α)·backdrop + α·black = backdrop·(1 − α)
 *
 * Source-over collapses onto multiply exactly when the source is zero, so this
 * tier's shadow is multiplicative by construction and vanishes over black for the
 * same reason the reference's does, with no branch for it. The `sd` the browser
 * blurs is the element's own border box with its own radii, which is the
 * silhouette the reference casts.
 *
 * The one real gap is the SPACE. The reference's fraction is of linear light; a
 * browser composites in encoded sRGB. `outerShadowAlpha` converts, and the
 * residual is 2.1 of 255 at worst across every backdrop level — stated, not
 * hidden, and below the reference bed's own ±4/255 reproducibility.
 *
 * The second gap is the KERNEL: `box-shadow` blurs with a browser-chosen
 * approximation of a Gaussian rather than a true one, so the two tiers agree on
 * the shadow's extent, offset, spread and amplitude, and only approximately on
 * the shape of its edge.
 */
export interface MaterialSourceOuterShadow {
  readonly offsetPx: number;
  readonly sigmaPx: number;
  readonly spreadPx: number;
  /** The black term's amplitude below the knee, by backdrop luminance (W14 G1). */
  readonly thinOcclusionDark: number;
  readonly thinOcclusionMid: number;
  readonly thinOcclusionBright: number;
  /** The composite's amplitude above the knee, by casting span (W14 G1). */
  readonly thickOcclusionAt96: number;
  readonly thickOcclusionAt128: number;
  readonly thickOcclusionAt160: number;
  /**
   * The lift's four constants (W14 G1). Mirrored so the two tiers resolve one
   * profile and a patch cannot mean different things on the two sides, and NOT
   * drawn here: a `box-shadow` takes one colour and one alpha and cannot reach
   * the backdrop outside the element it is on. Carrying it would take a
   * pseudo-element with `backdrop-filter: blur(40px)` masked to the falloff —
   * W14 Decision Log 1's question 2, decided (a): the CSS tier carries the
   * geometry and the adaptive alpha, which is the whole of the thin regime's gap
   * and needs no new element. W16 G1 gave the tier its second element and the
   * lift still is not drawn, because it cannot be: a blend mode does not reach a
   * `backdrop-filter`'s output (it blends the element's own content, and an empty
   * ring has none) and a blending ancestor is a backdrop root, so the additive
   * ring is unbuildable without a copy of the backdrop — which is a proxy, and
   * this tier's whole demotability rests on building none (claims §5.71 §6, W16
   * Decision Log 2 (d)). The share deferred is the lift alone: 0.029–0.048
   * encoded on the thick spans, nothing on the thin ones and nothing over a dark
   * backdrop.
   */
  readonly liftAmplitude: number;
  readonly liftSpanMin: number;
  readonly liftSpanFull: number;
  readonly liftBlurSigmaCss: number;
  /**
   * The shadow's amplitude UNDER reduced transparency — one absolute linear
   * occlusion replacing both regimes, not a factor on either. The renderer's
   * `MaterialOuterShadow.reducedTransparencyOcclusion` carries the measurement.
   */
  readonly reducedTransparencyOcclusion: number;
  readonly sizeGain: number;
}

/** Mirrors `@vitrea/renderer-webgpu`'s `DEFAULT_MATERIAL_PROFILE.outerShadow`. */
export const MATERIAL_SOURCE_OUTER_SHADOW: MaterialSourceOuterShadow = {
  offsetPx: 7.95,
  sigmaPx: 15.55,
  spreadPx: 3.1,
  thinOcclusionDark: 0,
  thinOcclusionMid: 0.33,
  thinOcclusionBright: 0.127,
  thickOcclusionAt96: 0.37,
  thickOcclusionAt128: 0.448,
  thickOcclusionAt160: 0.479,
  liftAmplitude: 0.01,
  liftSpanMin: 64,
  liftSpanFull: 118,
  liftBlurSigmaCss: 40,
  reducedTransparencyOcclusion: 0.197,
  sizeGain: 0,
};

/**
 * Where the thin regime's anchors sit on the backdrop luminance axis, and the
 * backdrop the law reads where the host measured none — mirrors the renderer's
 * `OUTER_SHADOW_THIN_L` and `OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE`, where
 * the reasons are.
 *
 * **What each tier keys on.** The renderer keys on the group's
 * `backdropToneLevel`: the backdrop's ENCODED-space mean, decoded to a linear
 * luminance, measured by the host. This tier keys on exactly the same number —
 * `cssTierDeclarations`'s `backdropLuminance`, which `root.ts` fills from the
 * same `BackdropToneSample.luminance` it hands the renderer, or from an author
 * hint's declared level where there is one. So the charter's third binding rule
 * — one luminance statistic, the one W9's face response already uses — holds on
 * both tiers with no second reading anywhere. Where neither a hint nor a sample
 * exists the two tiers fall back to the same constant, so they do not diverge on
 * an unsampled group either.
 */
export const OUTER_SHADOW_THIN_L = {
  inert: 0.02,
  midFrom: 0.06,
  midTo: 0.74,
  bright: 0.891,
} as const;

export const OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE = 0.3;

/** The three spans the thick regime's anchors were read at, CSS px. */
export const OUTER_SHADOW_THICK_SPANS = [96, 128, 160] as const;

/**
 * The black term's peak occlusion below the knee — the mirror of the renderer's
 * `outerShadowThinOcclusion`.
 */
export function outerShadowThinOcclusion(
  backdropLuminance: number | undefined,
  shadow: MaterialSourceOuterShadow = MATERIAL_SOURCE_OUTER_SHADOW,
): number {
  const l = backdropLuminance ?? OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE;
  const { inert, midFrom, midTo, bright } = OUTER_SHADOW_THIN_L;
  if (l <= inert) return shadow.thinOcclusionDark;
  if (l < midFrom) {
    const t = (l - inert) / (midFrom - inert);
    const s = t * t * (3 - 2 * t);
    return shadow.thinOcclusionDark + (shadow.thinOcclusionMid - shadow.thinOcclusionDark) * s;
  }
  if (l <= midTo) return shadow.thinOcclusionMid;
  if (l >= bright) return shadow.thinOcclusionBright;
  const t = (l - midTo) / (bright - midTo);
  return shadow.thinOcclusionMid + (shadow.thinOcclusionBright - shadow.thinOcclusionMid) * t;
}

/**
 * The composite's peak occlusion above the knee — the mirror of the renderer's
 * `outerShadowThickOcclusion`.
 */
export function outerShadowThickOcclusion(
  spanPx: number,
  shadow: MaterialSourceOuterShadow = MATERIAL_SOURCE_OUTER_SHADOW,
): number {
  const [s0, s1, s2] = OUTER_SHADOW_THICK_SPANS;
  const y0 = shadow.thickOcclusionAt96;
  const y1 = shadow.thickOcclusionAt128;
  const y2 = shadow.thickOcclusionAt160;
  if (spanPx <= s0) return y0;
  if (spanPx >= s2) return y2;
  if (spanPx <= s1) return y0 + ((y1 - y0) * (spanPx - s0)) / (s1 - s0);
  return y1 + ((y2 - y1) * (spanPx - s1)) / (s2 - s1);
}

/**
 * The outer shadow's peak LINEAR occlusion for one surface — the mirror of the
 * renderer's `outerShadowOcclusionAt`, and what this tier's `box-shadow` alpha
 * is written through.
 *
 * The GPU tier resolves the thin regime on the CPU and the thick one per pixel;
 * this tier has one surface and one declaration, so it resolves both here. The
 * result is the same number for the same span, backdrop and thickness, which is
 * what `tier-coherence.test.ts` pins.
 */
export function outerShadowOcclusionAt(
  shadow: MaterialSourceOuterShadow,
  backdropLuminance: number | undefined,
  spanPx: number,
  thickness: number,
): number {
  const thin = outerShadowThinOcclusion(backdropLuminance, shadow);
  const thick = outerShadowThickOcclusion(spanPx, shadow);
  const k = clamp01(thickness);
  const blend = k * k * (3 - 2 * k);
  return sizeOuterShadowOcclusionAt(thin + (thick - thin) * blend, thickness, shadow);
}

/**
 * The lift's span rise, 0…1 — the mirror of the renderer's `outerShadowLiftRise`.
 *
 * This tier does not paint the lift. It has to know how much of it the other tier
 * is painting, because that is what `cssTierShadowAlpha` subtracts from its own
 * multiply.
 */
export function outerShadowLiftRise(
  spanPx: number,
  shadow: MaterialSourceOuterShadow = MATERIAL_SOURCE_OUTER_SHADOW,
): number {
  return smoothstep(shadow.liftSpanMin, shadow.liftSpanFull, spanPx);
}

/**
 * The `box-shadow`'s compositing alpha — the profile's linear occlusion converted
 * into sRGB's encoded space and then FOLDED, so that one multiply stands in for
 * the two-term composite the other tier paints (claims §5.65 §2 and §6(ii)).
 *
 * Outside the coverage the GPU tier produces, in the compositing (encoded) domain,
 *
 *     out = B·(1 − α) + L
 *
 * where `α` is the black term's encoded alpha and `L` is the encoded contribution
 * of the lift — a blurred copy of the backdrop's own light, which this tier cannot
 * paint, because a `box-shadow` takes one colour and one alpha and cannot reach
 * the backdrop outside the element it is on (W14 Decision Log 4, user). One
 * multiply can only produce `out = B·(1 − α′)`, and equating the two at the
 * backdrop level `B` this tier already reads gives
 *
 *     α′ = α − L / B.
 *
 * That is a CONVERSION and not a second constant. Every quantity on the right is
 * the shared profile's own — `liftAmplitude`, the rise between `liftSpanMin` and
 * `liftSpanFull`, and the same sRGB encode the shader emits its lift through —
 * evaluated at the backdrop luminance this surface is over, which is the same
 * statistic the thin regime keys on. Nothing here is fitted, no anchor is
 * duplicated and there is no tier flag: the two tiers go on resolving one profile,
 * and they now agree above the knee as well as below it, which is K5's rule that
 * the tiers agree by conversion rather than by duplication.
 *
 * Without the fold this tier inherits an amplitude fitted on the tier that HAS a
 * lift, and over-darkens its thick spans by the whole of the light the other tier
 * adds back: band `3-6` below read 0.2439 / 0.3058 / 0.3364 at spans 96 / 128 /
 * 160 against the reference's 0.1925 / 0.2195 / 0.2117, where the same tier's
 * readings before the wave were 0.1840 / 0.1881 / 0.1925 (claims §5.65 §2).
 *
 * It cannot be exact for every pixel of a structured backdrop, because a single
 * multiply cannot reproduce a multiply plus an addition. The equality above is
 * solved at one backdrop level and at the falloff's peak, while `B` varies from
 * pixel to pixel — on the checkerboard between its black and its white squares —
 * and `L`, being encoded, is not proportional to the falloff the way `α` is. That
 * residual is this tier's own gap, and W16 G1 measured that it does NOT close
 * with a second element: no CSS construction adds a filtered backdrop's light to
 * a ring and keeps the backdrop (claims §5.71 §6). It is also not the sign the
 * fold was written for — over the shadow ring on `photo__rrect-md` this tier
 * reads 0.0112 encoded LIGHTER than the native where the GPU tier reads 0.0059
 * darker, so the conversion over-corrects there and added light would move it
 * the wrong way. The residual stays this tier's own, re-attributed to the
 * conversion (W16 Decision Log 2 (d)).
 *
 * The fold vanishes where the lift does: at and below `liftSpanMin` the rise is
 * zero, so every thin surface keeps exactly the alpha it had, and it shrinks with
 * the backdrop, so a surface over black is untouched. The result is clamped at
 * zero, since a backdrop dark enough would otherwise ask for a negative multiply.
 */
export function cssTierShadowAlpha(
  shadow: MaterialSourceOuterShadow,
  backdropLuminance: number | undefined,
  spanPx: number,
  thickness: number,
): number {
  const occlusion = outerShadowOcclusionAt(shadow, backdropLuminance, spanPx, thickness);
  const alpha = outerShadowAlpha(occlusion);
  const level = clamp01(backdropLuminance ?? OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE);
  const backdrop = srgbEncode(level);
  if (backdrop <= 0) return alpha;
  const rise = outerShadowLiftRise(spanPx, shadow);
  // The shader emits the lift premultiplied and a premultiplied layer may not
  // carry a channel above its own alpha, so its cap is mirrored here rather than
  // assumed inert at every amplitude a profile could name.
  const lift = Math.min(srgbEncode(level * shadow.liftAmplitude * rise), alpha);
  return Math.max(0, alpha - lift / backdrop);
}

/**
 * The outer shadow's constants under a profile patch, by the renderer's merge
 * rule — including its refusal of the leaves W14 G1 retired.
 *
 * Mirrored rather than imported for the reason every constant on this side is:
 * one profile document reaches both tiers, and a patch this tier accepted while
 * the renderer threw would be a profile that means two different things.
 * `withMaterialOverrides` carries the reasoning.
 */
export function sourceOuterShadow(patch?: RendererMaterialProfile): MaterialSourceOuterShadow {
  const shadow = patch?.outerShadow;
  if (shadow !== undefined && "occlusion" in shadow) {
    throw new Error(
      "outerShadow.occlusion was retired by W14 G1 (claims §5.62) and is replaced by " +
        "the six amplitude anchors (thinOcclusionDark, thinOcclusionMid, " +
        "thinOcclusionBright, thickOcclusionAt96, thickOcclusionAt128, " +
        "thickOcclusionAt160) and liftAmplitude for the second term. Applying this " +
        "patch would have rendered the default shadow while recording itself as " +
        "configured. It is refused rather than mapped: a single span-flat amplitude " +
        "is the material the measurement retired.",
    );
  }
  return { ...MATERIAL_SOURCE_OUTER_SHADOW, ...shadow };
}

/** sRGB's power-law exponent — the one `outerShadowAlpha` inverts. Mirrored. */
export const SRGB_ENCODING_EXPONENT = 2.4;

/**
 * The compositing-space alpha that reproduces a linear-light occlusion — the
 * mirror of the renderer's `outerShadowAlpha`, and the conversion this tier's
 * `box-shadow` is written through.
 */
export function outerShadowAlpha(occlusion: number): number {
  const occ = clamp01(occlusion);
  return 1 - Math.pow(1 - occ, 1 / SRGB_ENCODING_EXPONENT);
}

/**
 * The Gaussian CDF the shadow's edge falls off by — the mirror of the renderer's
 * `outerShadowFalloff`.
 *
 * This tier does not evaluate it to paint: `box-shadow` owns its own blur. It is
 * mirrored so the two tiers can be held to one curve where it matters — the
 * shadow's reach, and the analytic zero over black — rather than only to one set
 * of constants.
 */
export function outerShadowFalloff(signedDistancePx: number, sigmaPx: number): number {
  const x = -signedDistancePx / Math.max(sigmaPx, 1e-4);
  return 0.5 * (1 + Math.tanh(0.7978845608028654 * (x + 0.044715 * x * x * x)));
}

/**
 * `box-shadow`'s blur radius for a Gaussian σ.
 *
 * CSS Backgrounds 3 defines the blur radius as twice the standard deviation of
 * the Gaussian the shadow is blurred by — the opposite convention from
 * `filter: blur()`, whose parameter IS σ (see `MaterialOptics.blurRadius`). Two
 * lengths, two conventions, one profile: this is where they are reconciled, and
 * getting it wrong would halve or double the shadow's extent silently.
 */
export function cssShadowBlurRadius(sigmaPx: number): number {
  return 2 * sigmaPx;
}

/**
 * The outer shadow's peak occlusion at this thickness — the mirror of the
 * renderer's `sizeOuterShadowOcclusionAt`. Exactly the identity at the shipped
 * gain of 0.
 */
export function sizeOuterShadowOcclusionAt(
  occlusion: number,
  thickness: number,
  shadow: MaterialSourceOuterShadow = MATERIAL_SOURCE_OUTER_SHADOW,
): number {
  return Math.min(1, occlusion + shadow.sizeGain * thickness * (1 - occlusion));
}

/**
 * The outer shadow under an accessibility regime — the mirror of the renderer's
 * `outerShadowUnderPolicy`.
 *
 * `frost` is the axis reduced transparency alone sets, and the amplitude it
 * lands on is measured rather than assumed. Under forced colours the material is
 * gone and its shadow goes with it.
 *
 * One flat amplitude is written into all six anchors rather than a factor
 * applied to each, and the lift stands down with them — the renderer's
 * `outerShadowUnderPolicy` says why.
 */
export function outerShadowUnderPolicy(
  shadow: MaterialSourceOuterShadow,
  policy: ResolvedMaterialPolicy,
): MaterialSourceOuterShadow {
  if (policy.glass === "none" || policy.frost === "none") return flatOuterShadow(shadow, 0);
  if (policy.frost === "increased") {
    return flatOuterShadow(shadow, shadow.reducedTransparencyOcclusion);
  }
  return shadow;
}

/** Every amplitude anchor set to `amplitude`, with the lift stood down. */
function flatOuterShadow(
  shadow: MaterialSourceOuterShadow,
  amplitude: number,
): MaterialSourceOuterShadow {
  return {
    ...shadow,
    thinOcclusionDark: amplitude,
    thinOcclusionMid: amplitude,
    thinOcclusionBright: amplitude,
    thickOcclusionAt96: amplitude,
    thickOcclusionAt128: amplitude,
    thickOcclusionAt160: amplitude,
    liftAmplitude: 0,
  };
}

/** The size-law constants under a profile patch, by the renderer's merge rule. */
export function sourceSize(patch?: RendererMaterialProfile): MaterialSourceSize {
  return {
    sizeSpanMin: patch?.sizeSpanMin ?? MATERIAL_SOURCE_SIZE.sizeSpanMin,
    sizeSpanMax: patch?.sizeSpanMax ?? MATERIAL_SOURCE_SIZE.sizeSpanMax,
    sizeScatterGainMax: patch?.sizeScatterGainMax ?? MATERIAL_SOURCE_SIZE.sizeScatterGainMax,
    sizeScatterFloor: patch?.sizeScatterFloor ?? MATERIAL_SOURCE_SIZE.sizeScatterFloor,
    sizeScatterSpanMax: patch?.sizeScatterSpanMax ?? MATERIAL_SOURCE_SIZE.sizeScatterSpanMax,
    sizeScatterGainMax2x:
      patch?.sizeScatterGainMax2x ?? MATERIAL_SOURCE_SIZE.sizeScatterGainMax2x,
    sizeScatterFloor2x: patch?.sizeScatterFloor2x ?? MATERIAL_SOURCE_SIZE.sizeScatterFloor2x,
    sizeScatterSpanMax2x:
      patch?.sizeScatterSpanMax2x ?? MATERIAL_SOURCE_SIZE.sizeScatterSpanMax2x,
    sizeScatterGainFar2x:
      patch?.sizeScatterGainFar2x ?? MATERIAL_SOURCE_SIZE.sizeScatterGainFar2x,
    sizeScatterRampStartThin1x:
      patch?.sizeScatterRampStartThin1x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStartThin1x,
    sizeScatterRampStartThick1x:
      patch?.sizeScatterRampStartThick1x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStartThick1x,
    sizeScatterRampStartThin2x:
      patch?.sizeScatterRampStartThin2x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStartThin2x,
    sizeScatterRampStartThick2x:
      patch?.sizeScatterRampStartThick2x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStartThick2x,
    sizeScatterRampStartFar1x:
      patch?.sizeScatterRampStartFar1x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStartFar1x,
    sizeScatterRampStartFar2x:
      patch?.sizeScatterRampStartFar2x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStartFar2x,
    sizeScatterRampReach1xPx:
      patch?.sizeScatterRampReach1xPx ?? MATERIAL_SOURCE_SIZE.sizeScatterRampReach1xPx,
    sizeScatterRampReach2xPx:
      patch?.sizeScatterRampReach2xPx ?? MATERIAL_SOURCE_SIZE.sizeScatterRampReach2xPx,
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
 * The regime→rung map used to be re-inlined here, and again in
 * `backdropToneUnderPolicy` above, even though this package already exported the
 * function that does it: `refraction.ts` sat in the same package, and the copies
 * were kept anyway "for the same reason the optics are mirrored". That reason
 * never applied — the mirroring exists because the two *composites* differ, and
 * a three-arm map from a preference to a ladder rung is not a composite. Decision
 * Log #23(d) folded all of them onto `@vitrea/policy`'s one
 * `accessibilityRefractionCap`, which is the same function the shaders call.
 * `packages/calibration/test/tier-coherence.test.ts` still pins the numbers this
 * produces against the renderer's own.
 */
export function sizeThicknessUnderPolicy(
  spanPx: number,
  material: ResolvedMaterialPolicy,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return sizeThickness(spanPx, size) * size.refractionScale[accessibilityRefractionCap(material)];
}

/**
 * The `blur()` σ a surface of this span runs at — the scattering facet.
 *
 * Also what a group's `samplingPadding` floor has to be taken over, at the
 * group's **largest** member: S1's 3σ rule is about the widest kernel any member
 * will actually sample with, and a floor derived from the nominal σ would starve a
 * large surface's proxy by exactly the gain — and over the σ this tier will
 * really write.
 *
 * `devicePixelRatio` reaches the ramp's projection — its start and reach and,
 * since W15 G1, the deep value's floor and span top — and the heavy width's
 * gain, but never the width itself (see `sizeScatterSigmaAt`). It defaults to
 * 1, where the whole expression is the 1x law.
 */
export function sizeScatterSigma(
  sigmaPx: number,
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
  extentsCssPx?: readonly [number, number],
): number {
  return sizeScatterSigmaAt(
    sigmaPx,
    scatterThickness(spanPx, 1, size, devicePixelRatio, extentsCssPx),
    size,
    devicePixelRatio,
    spanPx,
  );
}

/**
 * **The device scale the WebGPU tier's DOM proxy projects the ramp at** — the
 * successor to W13's `CSS_TIER_RAMP_SCALE`, narrowed to the one consumer that
 * still wants it (W16 G1, charter Decision Log 2 (c)).
 *
 * `CSS_TIER_RAMP_SCALE` existed because the CSS tier drew one `backdrop-filter`
 * and had to pick one scale to project the ramp at; W13 Decision Log 5 picked
 * dpr 1 on measurement, and W15 Decision Log 3 kept it. W16 gives the tier two
 * layers and a mask, so the tier reads the law at the **live** ratio and that
 * constant has no meaning for its own draw any more.
 *
 * One consumer is left, and it is not the CSS tier: `groupScatterSigma` in
 * `root.ts` sizes the WebGPU tier's `css-backdrop` proxy — its `backdrop-filter`
 * and the 3σ padding floor `resolveProxyGeometry` enforces. That σ is bound
 * byte-identical by this wave's binding rule (the GPU tier does not move), so it
 * keeps the number it has always had, under a name that says whose it is. It is
 * **not** a projection of the CSS tier's own body any more, and moving the tier
 * must not reach it.
 *
 * Whether the proxy's σ should follow the device scale the way the renderer's
 * own body now does is a real question and a GPU-tier one: it belongs to the
 * wave that may move the GPU tier, not to this one.
 */
export const WEBGPU_PROXY_PROJECTION_SCALE = 1;

/**
 * The depth ramp's start at a device scale and a span — s₀(span, dpr), the
 * mirror of the renderer's `scatterRampStart` (W13 G1, claims §5.61 §2,
 * §5.64 §5).
 *
 * ```
 * s₀(span, dpr) = startThin(dpr) + (startThick(dpr) − startThin(dpr)) · sizeThickness(span)
 *               + (startFar(dpr) − startThick(dpr)) · smoothstep(sizeSpanMax, sizeScatterSpanMax, span)
 * ```
 *
 * In dpr: the reference was read at dpr 1 and dpr 2 and nowhere between, so
 * each anchor is interpolated linearly and held outside [1, 2]. In span: along
 * `sizeThickness`, the material's own thin/thick curve, because G0 read the
 * start much higher on thin surfaces than thick ones and a single start per
 * scale was refuted in the renderer (claims §5.64 §2).
 */
export function scatterRampStart(
  devicePixelRatio: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  spanPx = 0,
): number {
  const thin = rampAtScale(
    size.sizeScatterRampStartThin1x,
    size.sizeScatterRampStartThin2x,
    devicePixelRatio,
  );
  const thick = rampAtScale(
    size.sizeScatterRampStartThick1x,
    size.sizeScatterRampStartThick2x,
    devicePixelRatio,
  );
  const far = rampAtScale(
    size.sizeScatterRampStartFar1x,
    size.sizeScatterRampStartFar2x,
    devicePixelRatio,
  );
  // The fourth form: past the thickness knee the start declines along the
  // scatter span curve to `far` at its top (the renderer's comment has the why).
  const decline = smoothstep(
    size.sizeSpanMax,
    scatterSpanMaxAtScale(size, devicePixelRatio),
    spanPx,
  );
  return thin + (thick - thin) * sizeThickness(spanPx, size) + (far - thick) * decline;
}

/**
 * The depth ramp's reach at a device scale, in DEVICE px — the mirror of the
 * renderer's `scatterRampReachDevicePx`. In device pixels because that is how it
 * measured: between the two scales the reach roughly halves in CSS px, which is
 * one length in device pixels (claims §5.61 §2).
 */
export function scatterRampReachDevicePx(
  devicePixelRatio: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return rampAtScale(
    size.sizeScatterRampReach1xPx,
    size.sizeScatterRampReach2xPx,
    devicePixelRatio,
  );
}

/**
 * Linear in dpr between the 1x and 2x anchors, held outside [1, 2]. The two
 * anchors are returned exactly rather than through the interpolation, because
 * they are the values the reference was measured at and a profile that names
 * one should render it, not a float one ulp away from it.
 */
function rampAtScale(at1x: number, at2x: number, devicePixelRatio: number): number {
  const t = devicePixelRatio - 1;
  if (t <= 0) return at1x;
  if (t >= 1) return at2x;
  return at1x + (at2x - at1x) * t;
}

/**
 * The heavy width's gain at a device scale — the mirror of the renderer's
 * `scatterGainAtScale` (W15 G1, claims §5.69 §1). The two anchors are equal on
 * the landed material, so this is the 1x gain at every ratio until the sweep
 * fits the second scale.
 */
export function scatterGainAtScale(
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  return rampAtScale(size.sizeScatterGainMax, size.sizeScatterGainMax2x, devicePixelRatio);
}

/**
 * The heavy width's gain at the top of the scatter span curve, at a device scale
 * — the mirror of the renderer's `scatterGainFarAtScale` (W15 G1's re-form,
 * claims §5.70 §4 and §7). Interpolated from the 1x gain, which is what makes
 * the grading below flat at dpr ≤ 1.
 */
export function scatterGainFarAtScale(
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  return rampAtScale(size.sizeScatterGainMax, size.sizeScatterGainFar2x, devicePixelRatio);
}

/**
 * The heavy width's gain at a span and a device scale — the mirror of the
 * renderer's `scatterGainAt` (W15 G1's re-form, claims §5.70 §4 and §7).
 *
 * ```
 * gain(span, dpr) = gainAtScale(dpr)
 *                 + (gainFar(dpr) − gainAtScale(dpr))
 *                   · smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span)
 * ```
 *
 * The same curve the ramp's far anchor declines along, so the width and the
 * start are one span statistic read twice and this tier gains no new knee.
 */
export function scatterGainAt(
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  const near = scatterGainAtScale(size, devicePixelRatio);
  const far = scatterGainFarAtScale(size, devicePixelRatio);
  if (far === near) return near;
  return (
    near
    + (far - near)
      * smoothstep(size.sizeSpanMax, scatterSpanMaxAtScale(size, devicePixelRatio), spanPx)
  );
}

/**
 * The scatter facet's frost at a device scale — the mirror of the renderer's
 * `scatterFloorAtScale` (W15 G1, claims §5.69 §2). Read in two places that must
 * agree: the deep curve, and the value the whole facet folds to.
 */
export function scatterFloorAtScale(
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  return clamp01(rampAtScale(size.sizeScatterFloor, size.sizeScatterFloor2x, devicePixelRatio));
}

/**
 * The deep value's span top at a device scale — the mirror of the renderer's
 * `scatterSpanMaxAtScale` (W15 G1, claims §5.69 §2). One span statistic read
 * twice: the deep curve rises to it and the ramp's start declines to `far`
 * along the same smoothstep.
 */
export function scatterSpanMaxAtScale(
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  return rampAtScale(size.sizeScatterSpanMax, size.sizeScatterSpanMax2x, devicePixelRatio);
}

/**
 * The span law that supplies the ramp's deep value — kDeep(span), and the
 * mirror of the renderer's `scatterDeepThickness` (W11c; kept underneath the
 * ramp by W13 G1). Unfolded: the fold is applied once, on the whole mix.
 *
 * `devicePixelRatio` reaches the floor and the span top, which are per-scale
 * constants since W15 G1 (claims §5.69 §2). It defaults to 1, and the two
 * anchors are equal on the landed material, so every ratio returns the 1x law
 * until the sweep fits the second scale.
 */
export function scatterDeepThickness(
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  const floor = scatterFloorAtScale(size, devicePixelRatio);
  return (
    floor
    + (1 - floor)
      * smoothstep(size.sizeSpanMin, scatterSpanMaxAtScale(size, devicePixelRatio), spanPx)
  );
}

/**
 * The sharp component's share at a depth — s(u, span), the mirror of the
 * renderer's `scatterSharpShare` (W13 G1). This tier never evaluates it per
 * pixel; it is exported so that the projection below can be checked against the
 * law it projects, and so `tier-coherence` can pin the two tiers on the law
 * itself and not only on its average.
 */
export function scatterSharpShare(
  uDevicePx: number,
  devicePixelRatio: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  spanPx = 0,
): number {
  const deepSharp = 1 - scatterDeepThickness(spanPx, size, devicePixelRatio);
  const start = scatterRampStart(devicePixelRatio, size, spanPx);
  const reach = Math.max(scatterRampReachDevicePx(devicePixelRatio, size), 1e-6);
  const excursion = Math.max(start - deepSharp, 0) * Math.max(1 - Math.max(uDevicePx, 0) / reach, 0);
  return clamp01(deepSharp + excursion);
}

/**
 * The scatter facet's input — how far toward its heavy blur a surface of this
 * span mixes ON AVERAGE, 0…1: the depth ramp's projection onto one number per
 * surface, and the mirror of the renderer's `scatterThickness` (W13 G1).
 *
 * The GPU tier mixes per pixel; this tier has one `backdrop-filter` and so can
 * only carry the average, and every other consumer of the law — the sampling
 * proxy's 3σ padding floor, the demo's readout — is in the same position. One
 * law, two projections, which is what stops the tiers scattering differently.
 *
 * `fold` is the accessibility fold every facet takes. It scales the excursion
 * away from `sizeScatterFloor` and NOT the floor itself: the floor is the frost
 * the material has at any size, the rest is the depth a preference is entitled
 * to remove.
 */
export function scatterThickness(
  spanPx: number,
  fold: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
  extentsCssPx?: readonly [number, number],
): number {
  const floor = scatterFloorAtScale(size, devicePixelRatio);
  return clamp01(floor + (scatterRampAreaMean(spanPx, size, devicePixelRatio, extentsCssPx) - floor) * fold);
}

/**
 * The unfolded area average of the heavy share over a surface — the integral
 * `scatterThickness` documents, and the mirror of the renderer's
 * `scatterRampAreaMean`.
 *
 * The heavy share at depth u is `kDeep(span) − A · max(0, 1 − u / R)`, so the
 * average is `kDeep − A · T̄` and only the triangle has to be integrated; on a
 * rectangle the area at depth u has measure `P − 8u`, which closes it. The
 * corners are ignored, as the renderer's copy documents. `extentsCssPx` is the
 * surface's own width and height where the caller has them; where it does not,
 * the surface is taken to be a square of the span.
 */
export function scatterRampAreaMean(
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
  extentsCssPx?: readonly [number, number],
): number {
  const deep = scatterDeepThickness(spanPx, size, devicePixelRatio);
  const amplitude = Math.max(scatterRampStart(devicePixelRatio, size, spanPx) - (1 - deep), 0);
  if (amplitude <= 0) return clamp01(deep);
  const width = Math.max(extentsCssPx?.[0] ?? spanPx, 0);
  const height = Math.max(extentsCssPx?.[1] ?? spanPx, 0);
  const area = width * height;
  if (area <= 0) return clamp01(deep - amplitude);
  // The reach in CSS px, which is the unit a surface's extents arrive in: the
  // ratio u/U is scale-free, so dividing the device-px reach by the same dpr the
  // depth would have been multiplied by gives the identical number.
  const reach = Math.max(
    scatterRampReachDevicePx(devicePixelRatio, size) / Math.max(devicePixelRatio, 1e-3),
    1e-6,
  );
  const perimeter = 2 * (width + height);
  const limit = Math.min(reach, Math.min(width, height) / 2);
  const triangleMean =
    (perimeter * limit
      - 4 * limit * limit
      - (perimeter * limit * limit) / (2 * reach)
      + (8 * limit * limit * limit) / (3 * reach))
    / area;
  return clamp01(deep - amplitude * triangleMean);
}

/**
 * The same, for a caller that has already resolved the scatter thickness — which
 * is every caller that has a policy to fold under.
 *
 * The two-function shape is deliberate and it is the same on both tiers: the
 * thickness form is the law, and the span form is the convenience that computes
 * an unfolded thickness for it. One formula, so a policy fold cannot accidentally
 * be applied to one facet and not another.
 *
 * **The ratio never divides this σ**, on either tier. W12 G3 read the widths as
 * device-pixel quantities and this mirror divided by the ratio (claims §5.56
 * §1); W13 Decision Log 8 retired that on the bed, and W15 G1 restores it on
 * the GPU tier alone — inside the renderer's `bodySigmaCssFor`, not here —
 * because this is the SHARED projection and W15 Decision Log 2 leaves W13
 * Decision Log 5 in force until G1 predicts this tier's 2x σ. Dividing here
 * would move the tier away from its own measured 2x ceiling, which is LARGER in
 * CSS px than its 1x reading, not half of it (claims §5.69 §4).
 *
 * What the ratio does reach is the GAIN (`sizeScatterGainMax2x`, W15 G1), so at
 * mix 0 this returns `sigmaPx` at every ratio. Since W15 G1's landing the two
 * gains differ above dpr 1 (4.8 at dpr 2 against 8 at dpr 1, claims §5.70 §8),
 * but the CSS tier no longer projects its body onto one σ except under the cost
 * collapse (`css-tier.ts`), which reproduces exactly today's 1x form on purpose.
 * The tier's own two widths come from `cssTierSharpSigmaCssPx` and
 * `cssTierHeavySigmaCssPx` at the live ratio.
 *
 * `spanPx` is OPTIONAL and selects which gain, exactly as on the renderer's
 * mirror: given, the span-graded `scatterGainAt` (W15 G1's re-form, claims
 * §5.70 §4 and §7); omitted, the flat `scatterGainAtScale`. The two agree at
 * every span at dpr ≤ 1, so `css-tier.ts`'s single `blur()` — which has a mix
 * and no span, and reads at dpr 1 — keeps the meaning it had.
 */
export function sizeScatterSigmaAt(
  sigmaPx: number,
  scatter: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
  spanPx?: number,
): number {
  const mix = clamp01(scatter);
  const gain =
    spanPx === undefined
      ? scatterGainAtScale(size, devicePixelRatio)
      : scatterGainAt(spanPx, size, devicePixelRatio);
  return sigmaPx * (1 + (gain - 1) * mix);
}

/*
 * ---------------------------------------------------------------------------
 * The CSS tier's two-layer body (W16 G1, charter Decision Log 2 (a)–(c);
 * claims §5.71).
 * ---------------------------------------------------------------------------
 *
 * The tier draws the renderer's two components as two `backdrop-filter` layers
 * over the same backdrop, the heavy one painted after the sharp one so that it
 * blurs the sharp one's OUTPUT. Two Gaussians in series add in quadrature, so a
 * heavy layer at σ_step composes to √(σ_s² + σ_step²) — which is why the heavy
 * layer's own width below is a *step* and not the composed width, and why the
 * composed width is the only one that can be compared with the renderer's.
 *
 * Nothing here is fitted for this tier (K5). The sharp width, the gain, the
 * ramp's start, its reach and the deep value are the renderer's own functions
 * read at the live device ratio. The one conversion this tier makes is
 * `scatterHeavyEffectiveSigmaDevicePx`, and it is a measurement of the
 * renderer's kernel rather than a constant of this tier's — see its comment.
 */

/**
 * The renderer's heavy component's **effective** Gaussian width, from the
 * profile's nominal, in device px (W16 G1; charter Decision Log 2 (c)).
 *
 * The renderer's heavy component is a mip-chain tap, not a Gaussian, and it is
 * measurably wider than the σ the profile names: claims §5.69 §3 already read
 * the renderer's own nominal through a Gaussian estimator and got 8–11 device px
 * where the profile said 6, and §5.71 §5 showed a true Gaussian drawn at the
 * nominal landing narrow of the reference on every span by about the size of
 * that difference. A `backdrop-filter` blur IS a true Gaussian, so a tier that
 * drew the nominal would draw a narrower body than the tier it is supposed to
 * agree with — the coherence gap would be the conversion's, not the material's.
 *
 * So the tier draws what the renderer's kernel actually draws. The conversion is
 * a moment match measured on the renderer's own committed captures of the
 * checkerboard cells at both scales (the table and the residual are in this
 * function's own record below), and it carries **no constant of this tier's
 * own**: it is one number describing the other tier's kernel, in the same sense
 * `α′ = α − L/B` is one number describing the other tier's lift.
 *
 * **The conversion is a per-scale ratio, measured, and the bed it is measured on
 * is half the finding.**
 *
 * The first run used the checkerboard cells and produced a per-span spread of
 * 1.6x at dpr 2 and nothing at all at dpr 1. That was the BED, not the kernel: a
 * checkerboard is a single spatial frequency — pitch 16 CSS px — and a heavy
 * kernel of sigma 10 device px annihilates it at dpr 1, so no signal is left for a
 * width to be read out of. X4 says so directly rather than leaving it to
 * inference: on that bed the same instrument recovers a known width to +5% at
 * sigma 6, +8% at sigma 8, and at sigma 10 returns either 1.03 or the sweep's
 * ceiling for a truth of 10.00. Those readings are discarded, and discarding them
 * is a result: any future reading of this kernel needs a broadband bed.
 *
 * On the broadband `photo` cells the same instrument recovers a known law to
 * **-0.51% … +0.16% at dpr 1** and **+-0.04% at dpr 2**, and the answer is one
 * ratio per scale, flat in the span:
 *
 * | cell | span | dpr | nominal | effective | ratio | RMS | +-5% band |
 * | --- | --- | --- | --- | --- | --- | --- | --- |
 * | `rrect-sm` | 32 | 1 | 10.00 | 13.36-14.12 | 1.335-1.412 | 0.0020 | 11.50-16.50 |
 * | `capsule-button` | 44 | 1 | 10.00 | 13.66-14.03 | 1.366-1.403 | 0.0020 | 12.00-15.50 |
 * | `rrect-md` | 96 | 1 | 10.00 | 13.71-13.87 | 1.371-1.387 | 0.0021 | 13.00-15.00 |
 * | `rrect-ml` | 128 | 1 | 10.00 | 13.74-13.85 | 1.374-1.385 | 0.0021 | 13.00-14.50 |
 * | `rrect-lg` | 160 | 1 | 10.00 | 13.81-13.88 | 1.381-1.388 | 0.0021 | 13.50-14.50 |
 * | `rrect-sm` | 32 | 2 | 6.00 | 8.91-8.96 | 1.484-1.494 | 0.0020 | 8.00-9.50 |
 * | `capsule-button` | 44 | 2 | 6.00 | 8.97-9.00 | 1.495-1.500 | 0.0020 | 8.50-9.50 |
 * | `rrect-md` | 96 | 2 | 6.00 | 8.91-8.97 | 1.484-1.496 | 0.0021 | 8.50-9.00 |
 * | `rrect-ml` | 128 | 2 | **6.66** | **9.92-9.93** | **1.488-1.491** | 0.0021 | 9.50-10.00 |
 * | `rrect-lg` | 160 | 2 | **8.24** | **12.19-12.21** | **1.478-1.481** | 0.0022 | 12.00-12.5 |
 *
 * **The last two rows are the ones that decide the shape.** The other three cells
 * at dpr 2 share a nominal of 6.00, so a constant RATIO and a constant effective
 * WIDTH predict the same number for all of them and cannot be told apart. The 2x
 * gain is span-graded above the size law's knee, so `rrect-ml` is fitted at a
 * nominal of 6.663 and `rrect-lg` at 8.24 — and there the two predictions
 * separate hard. A constant ratio says 9.93 and 12.28; a constant width says 8.97
 * for both. They read 9.93 and 12.20. So the conversion is a ratio, three
 * different nominals give 1.478-1.500, and the checkerboard bed's
 * falling-with-span ratios were its degeneracy and nothing else.
 *
 * **The residuals, and why the rule is a ratio and is per scale.** Fitted by
 * least squares over the ten readings:
 *
 * | set | ratio | its residual | quadrature | its residual |
 * | --- | --- | --- | --- | --- |
 * | both scales | r = 1.412 | 0.417 device px (3.5%) | c = 8.470 | 0.992 device px (8.4%) |
 * | dpr 1 only | r = **1.380** | 0.091 device px (0.66%) | c = 9.507 | 0.091 device px (0.66%) |
 * | dpr 2 only | r = **1.485** | 0.035 device px (0.35%) | c = 7.287 | 0.685 device px (7.0%) |
 *
 * Two things to read off that. First, **the dpr 1 row cannot choose between the
 * two forms and must not be quoted as if it could**: the nominal heavy width is
 * exactly 10.000 device px at every 1x span, so with one nominal the two rules
 * are the same one-parameter fit and their residuals are identical by
 * construction. All of the discriminating power is at dpr 2, where the
 * span-graded gain makes the nominal genuinely vary (6.000, 6.663, 8.244) — and
 * there the ratio holds to 0.35% while the quadrature form is off by 7%.
 *
 * Second, the 3.5% pooled residual on a single ratio is not scatter but a clean
 * split by scale: every 1x cell sits below the pooled value and every 2x cell
 * above it. Within each scale the rule is essentially exact, so the honest law is
 * one ratio per scale rather than one ratio with a poor fit.
 *
 * Why the two scales differ by 7.6% is not explained by this measurement, and the
 * plausible mechanism is offered as a hypothesis rather than a finding: the heavy
 * tap lands on a fractional mip level, `scatterLod = size.w + log2(gain)`, and
 * dpr 1's gain of 8 is an exact power of two where dpr 2's are not, so the two
 * scales sample the chain's trilinear blend differently. The hypothesis does not
 * obviously predict that the three dpr 2 gains — whose log2 fractions span 0.26
 * to 0.72 — all give the same ratio, which they do.
 *
 * So this is a 1x/2x anchor pair interpolated by `rampAtScale`, which is the same
 * shape and the same interpolation every other scale-dependent quantity in this
 * material already takes (`sizeScatterGainMax`, `sizeScatterFloor`,
 * `sizeScatterSpanMax` and the ramp's own anchors). It is NOT a leaf of the
 * material profile, deliberately: it describes the renderer's kernel
 * implementation rather than the reference's material, so a profile patch has no
 * business moving it and a change to the renderer's mip chain would require
 * re-measuring it. That is also why it does not violate K5 — it is one number
 * describing the OTHER tier's kernel, in the same sense `alpha-prime = alpha -
 * L/B` is one number describing the other tier's lift, rather than a constant
 * fitted for this tier against the reference.
 *
 * **The SHARP width is kept nominal, and that too is a reading rather than an
 * assumption.** Fitted the same way — the heavy width held at its own fitted
 * value and the profile taken over sigma_s on a 0.05-device-px grid, so the
 * column cannot be a grid floor — it reads 1.60-1.70 against the profile's 1.25
 * at dpr 1, but every cell's +-5% band contains the nominal and the narrowest of
 * them is 1.15-1.95. At dpr 2 it is not identifiable at all: the bands run
 * 0.30-4.00, because the deep interior at that scale is FULLY heavy on every
 * cell (the fitted regions' deep sharp share is 0.000, which is claims §5.69 §2's
 * own finding), so there is no sharp component in the region being fitted for a
 * width to be read from. A 1.25 that sits inside every band it has at one scale
 * and is unconstrained at the other is a width that reads nominal, and the tier
 * draws it nominal.
 */
export const SCATTER_HEAVY_EFFECTIVE_RATIO_1X = 1.38;
export const SCATTER_HEAVY_EFFECTIVE_RATIO_2X = 1.485;

/**
 * The conversion at a device scale, interpolated between the two measured
 * anchors and held outside [1, 2] — `rampAtScale`, exactly as every other
 * per-scale constant in this material is read.
 */
export function scatterHeavyEffectiveRatioAtScale(devicePixelRatio = 1): number {
  return rampAtScale(
    SCATTER_HEAVY_EFFECTIVE_RATIO_1X,
    SCATTER_HEAVY_EFFECTIVE_RATIO_2X,
    devicePixelRatio,
  );
}

/** The effective width of a heavy component whose nominal is `nominalDevicePx`. */
export function scatterHeavyEffectiveSigmaDevicePx(
  nominalDevicePx: number,
  devicePixelRatio = 1,
): number {
  return nominalDevicePx * scatterHeavyEffectiveRatioAtScale(devicePixelRatio);
}

/**
 * L1's width in CSS px — the sharp component, a **device-pixel** quantity
 * (W16 G1; charter Decision Log 2 (c)).
 *
 * `sigmaDevicePx` is the profile's `blurSigma`, which the renderer treats as
 * device px at every scale since W15 G1. `backdrop-filter: blur()` takes CSS px,
 * so the division by the live ratio is the whole of the conversion — and it is
 * the conversion W13 Decision Log 5 refused for the single-blur form, on a
 * measurement about the single-blur form. That measurement does not reach here:
 * it said the tier's best SINGLE σ is larger in CSS px at 2x, which is a
 * statement about the projection of a mix onto one Gaussian, not about either
 * component's width.
 *
 * **The sharp component takes the same effective conversion as the heavy one**,
 * and the bed decided that where the width fit could not (W16 G1's re-form).
 * Profiled on its own, the sharp width reads 1.60-1.70 device px against the
 * profile's 1.25 at dpr 1 — about 1.3x, the same direction and roughly the same
 * size as the heavy component's 1.38 — but the nominal sits inside every cell's
 * +-5% band, so that reading could not exclude 1.0 and the width was first
 * landed nominal. At dpr 2 it cannot be read at all: `sizeScatterFloor2x` is 1,
 * so the deep interior is fully heavy and there is no sharp light in the fitted
 * region.
 *
 * The dry run then answered it from the other end. Drawing the sharp component
 * at the nominal put the tier's interior SPREAD 0.013-0.018 over native on four
 * cells, which is the stop the referee raised; drawing it through the same
 * conversion the heavy component takes puts the spread inside +-0.007 at 1x and
 * +-0.016 at 2x on every cell measured, and lands it within 0.001 of the GPU
 * tier's own spread at 2x. One kernel, one chain, one conversion — which is what
 * the mip-tap mechanism predicts and what the width fit was consistent with all
 * along.
 */
export function cssTierSharpSigmaCssPx(sigmaDevicePx: number, devicePixelRatio = 1): number {
  return (
    scatterHeavyEffectiveSigmaDevicePx(sigmaDevicePx, devicePixelRatio)
    / Math.max(devicePixelRatio, 1e-3)
  );
}

/**
 * L2's **composed** width in CSS px — what the sharp layer's output must end up
 * blurred to where the mask is opaque.
 *
 * The renderer's nominal heavy width is `blurSigma · gain(span, dpr)` in device
 * px, through the span-graded gain W15 G1 landed; the effective conversion turns
 * that into the width the mip chain really draws, and the ratio turns it into
 * CSS px.
 */
export function cssTierHeavySigmaCssPx(
  sigmaDevicePx: number,
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  const nominal = sigmaDevicePx * scatterGainAt(spanPx, size, devicePixelRatio);
  return (
    scatterHeavyEffectiveSigmaDevicePx(nominal, devicePixelRatio)
    / Math.max(devicePixelRatio, 1e-3)
  );
}

/**
 * L2's **own** blur radius in CSS px — the step that takes L1's output to the
 * composed heavy width.
 *
 * Two Gaussians in series compose in quadrature, and L2 is painted over L1's
 * result rather than over the page: `√(σ_s² + σ_step²) = σ_h`. Clamped at zero
 * because a profile whose gain is at or below 1 asks for a heavy component no
 * wider than the sharp one, which is a single blur and not an imaginary step.
 */
export function cssTierHeavyStepSigmaCssPx(sharpCssPx: number, heavyCssPx: number): number {
  return Math.sqrt(Math.max(heavyCssPx * heavyCssPx - sharpCssPx * sharpCssPx, 0));
}

/**
 * The heavy share at a depth, folded — L2's alpha at one point of the mask
 * (W16 G1; charter Decision Log 2 (b)).
 *
 * `scatterSharpShare` is the renderer's law and this is one minus it, under the
 * same accessibility fold `scatterThickness` applies to the projection: the fold
 * scales the excursion away from the floor and never the floor itself, so the
 * area mean of this function is exactly `scatterThickness`'s own number and the
 * mask cannot disagree with the projection it replaces.
 */
export function cssTierHeavyShareAt(
  uDevicePx: number,
  devicePixelRatio: number,
  fold: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  spanPx = 0,
): number {
  const floor = scatterFloorAtScale(size, devicePixelRatio);
  const heavy = 1 - scatterSharpShare(uDevicePx, devicePixelRatio, size, spanPx);
  return clamp01(floor + (heavy - floor) * fold);
}

/**
 * The σ a group's proxy blurs with: the widest σ any measured member samples
 * with, as the MAXIMUM of each member's own projected σ (review, W13 G1).
 *
 * The ramp's projection is its area average over the member's box, so it
 * depends on both extents: a 1200×160 strip projects heavier than a 160×160
 * square of the same short span. Picking the member by short span alone, as
 * the group did before, made the choice depend on registration order between
 * two such members and could hand the strip the square's smaller σ — and the
 * 3σ padding floor with it. A group with nothing measured has no span to take
 * and sits at the projection of span 0, exactly where the widest-member rule
 * left it.
 */
export function groupScatterSigma(
  sigmaPx: number,
  fold: number,
  members: readonly (readonly [number, number])[],
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  projectionScale = 1,
): number {
  let widest = sizeScatterSigmaAt(
    sigmaPx,
    scatterThickness(0, fold, size, projectionScale),
    size,
    1,
    0,
  );
  for (const [width, height] of members) {
    const span = Math.min(width, height);
    // The gain is graded by the member's own span since W15 G1's re-form, on the
    // same ratio the gain has always been read at here — dpr 1, which is now
    // `WEBGPU_PROXY_PROJECTION_SCALE` and is this proxy's own number rather than
    // a projection of the CSS tier's body (W16 G1: the tier moved to the live
    // ratio and the proxy is bound byte-identical). At that ratio the grading is
    // flat, so the σ is unchanged; passing the span is what keeps this the
    // per-member form of `sizeScatterSigma` rather than a second reading of the
    // law.
    const own = sizeScatterSigmaAt(
      sigmaPx,
      scatterThickness(span, fold, size, projectionScale, [width, height]),
      size,
      1,
      span,
    );
    widest = Math.max(widest, own);
  }
  return widest;
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
 * One surface's box, its radius and its authored thickness, in CSS px — the only
 * geometry the two interior derivations below need (W17 G1).
 *
 * A rounded rectangle and nothing more: both derivations are co-area integrals
 * over the inward offsets of the contour, and that integral is exact for a
 * rounded rectangle and for no other shape this tier draws. A surface whose
 * silhouette is a union of boxes — a toolbar group, glass over glass — is
 * outside the form, which is why the caller passes one box and the closed form's
 * residual is recorded against the cells that have one (claims §5.74 §4).
 */
export interface InteriorSurfaceGeometry {
  readonly widthCssPx: number;
  readonly heightCssPx: number;
  readonly radiusCssPx: number;
  /** The host's declared thickness — `GlassHostShape.thickness`, 8 CSS px by default. */
  readonly thicknessCssPx: number;
}

/** The rounded rectangle's area, its straight runs' total length, and its radius. */
function rrectMetrics(
  geometry: InteriorSurfaceGeometry,
): {
  area: number;
  straight: number;
  radius: number;
  span: number;
  width: number;
  height: number;
} {
  const { widthCssPx: w, heightCssPx: h } = geometry;
  const span = Math.min(w, h);
  const radius = Math.min(Math.max(geometry.radiusCssPx, 0), span / 2);
  return {
    area: Math.max(w * h - (4 - Math.PI) * radius * radius, 1e-6),
    straight: 2 * (w - 2 * radius) + 2 * (h - 2 * radius),
    radius,
    span,
    width: w,
    height: h,
  };
}

/**
 * The two moments the co-area integrals are built from, over `[a, b]`:
 * `∫ (1 − u/D)² du` and `∫ (1 − u/D)²·u du`, both in closed form.
 *
 * `∫ (1 − u/D)² du = −D(1 − u/D)³/3` and, by `t = 1 − u/D`,
 * `∫ u(1 − u/D)² du = −D²((1 − u/D)³/3 − (1 − u/D)⁴/4)`.
 */
function bandMoments(depth: number, from: number, to: number): { zeroth: number; first: number } {
  const d = Math.max(depth, 1e-9);
  const zeroth = (u: number): number => -(d * (1 - u / d) ** 3) / 3;
  const first = (u: number): number => -(d * d) * ((1 - u / d) ** 3 / 3 - (1 - u / d) ** 4 / 4);
  return { zeroth: zeroth(to) - zeroth(from), first: first(to) - first(from) };
}

/**
 * `∫₀^D (1 − u/D)² · P(u) du` for a rounded rectangle's inward offsets, exact.
 *
 * The inward offset of a rounded rectangle by `u` keeps its straight runs at
 * their full length and shrinks only its corner arcs, so up to the radius its
 * perimeter is `P(u) = straight + arcPerUnitRadius·(r − u)` — linear in `u`.
 * `arcPerUnitRadius` is `2π` where the weight is the same at every point of the
 * arc, which the ambient band and the inner shadow's profile both are, and the
 * specular factor's contour integral where it is not.
 *
 * Past the radius the offset is a plain rectangle of `(W − 2u) × (H − 2u)` and
 * its perimeter is `2(W + H) − 8u`, which is the same value at `u = r` and a
 * different slope after it. Both branches are here because the inner shadow's
 * depth reaches past most of the bed's radii (8 CSS px grown by the size law
 * against a 20 px corner) while the rim's 1.5 px band never does; a form that
 * carried only the first branch would run the arcs negative there.
 */
function coAreaBand(
  depth: number,
  geometry: { straight: number; radius: number; width: number; height: number },
  arcPerUnitRadius: number,
): number {
  const d = Math.max(depth, 0);
  const rounded = Math.min(d, geometry.radius);
  const inner = bandMoments(d, 0, rounded);
  let total =
    (geometry.straight + arcPerUnitRadius * geometry.radius) * inner.zeroth -
    arcPerUnitRadius * inner.first;
  if (d > geometry.radius) {
    const outer = bandMoments(d, geometry.radius, d);
    total += 2 * (geometry.width + geometry.height) * outer.zeroth - 8 * outer.first;
  }
  return total;
}

/**
 * `∮ clamp(n̂ · L, 0, 1)^p dθ` over one full turn of the unit normal — the corner
 * arcs' share of the specular contour integral, per unit of radius.
 *
 * Memoised on the exponent and the direction because it depends on neither the
 * surface's geometry nor its backdrop: every surface of one profile shares one
 * value, and this runs on the paint path. The quadrature is 2048 midpoints of a
 * smooth periodic integrand (the clamp's corner is `C^{p−1}` at `p` ≥ 6), which
 * agrees with the closed form `√π·Γ((p+1)/2)/Γ(p/2+1)` to 1e−12 at the profile's
 * exponents; it is written as a sum because that identity would need a gamma
 * function this package does not carry for a constant it evaluates once.
 */
const arcSpecularCache = new Map<string, number>();
function arcSpecularIntegral(power: number, light: readonly [number, number]): number {
  const key = `${power}|${light[0]}|${light[1]}`;
  const hit = arcSpecularCache.get(key);
  if (hit !== undefined) return hit;
  const exponent = Math.max(power, 1e-3);
  const samples = 2048;
  let total = 0;
  for (let index = 0; index < samples; index += 1) {
    const angle = ((index + 0.5) / samples) * 2 * Math.PI;
    const facing = clamp01(Math.cos(angle) * light[0] + Math.sin(angle) * light[1]);
    total += Math.pow(facing, exponent) * ((2 * Math.PI) / samples);
  }
  arcSpecularCache.set(key, total);
  return total;
}

/**
 * The light the renderer draws inside the silhouette that this tier does not —
 * `X`, in linear light, derived from the profile and the surface's own box
 * (W17 G1; Decision Log 2 (c), claims §5.74 §4).
 *
 * Four terms were measured on the renderer's own captures by declining each in
 * turn (claims §5.74 §2), and two of them are zero by construction rather than
 * by fit. **The outer shadow's lift** is drawn as `lift · (1 − coverage)` and is
 * outside the silhouette exactly; it measures zero inside on every cell of the
 * bed. **The lens** is a displacement and not light — it re-samples the blurred
 * backdrop and adds nothing of its own — so over a backdrop that is
 * statistically homogeneous across the band its mean shift is zero to first
 * order; it measured −0.0002 on every checkerboard cell and the backdrop's own
 * gradient at the contour on the photo cells (−0.0024…+0.0036), which is carried
 * as this derivation's residual rather than fitted to.
 *
 * What is left is the band, twice. The renderer adds `rw(d)·(rimAlpha + spec)`
 * with `rw(d) = clamp(1 − |d|/rimWidth, 0, 1)²`, so the ambient term's area mean
 * is the co-area integral of `rw` over the inward offsets and the lit term's is
 * the same integral with the specular factor carried around the contour: four
 * straight runs at the four axis normals, and the corner arcs sweeping one full
 * turn. `present` is the collapse's own fade — the reference paints no lit edge
 * on a material that has taken its backdrop's tone — and it is the caller's
 * because it is a property of the group's backdrop and not of the surface.
 *
 * **Residual, per cell, against the measurement:** the largest is +0.00605 on
 * `dark-solid__rrect-md` in the 1x dark profile (predicted +0.1404 against a
 * measured +0.1344) and no cell exceeds +0.01; it is systematically positive and
 * largest on the capsules (+0.0027…+0.0036), whose band is entirely corner arc
 * and whose predicted term is therefore the most sensitive to a pixel of
 * disagreement between the geometric contour and the measured silhouette. On the
 * three W16 probe cells the form reads +0.00462 / +0.00930 / +0.00339 against a
 * measured +0.00356 / +0.00521 / +0.00262 (claims §5.74 §4).
 */
export function interiorBandLight(
  source: MaterialSourceOptics,
  geometry: InteriorSurfaceGeometry,
  present: number,
  light: MaterialSourceInteriorLight = MATERIAL_SOURCE_INTERIOR_LIGHT,
): number {
  const metrics = rrectMetrics(geometry);
  const { area, radius, span } = metrics;
  // The band cannot reach past the half span, and past the corner's radius the
  // specular contour integral below would need the rectangle branch's own
  // normals. Inert on every calibration surface — the narrowest radius on the
  // bed is 8 CSS px against a 1.5 px band — and a guard rather than a law.
  const depth = Math.min(Math.max(source.rimWidth, 0), radius, span / 2);
  if (depth <= 0 || present <= 0) return 0;

  const direction = unitDirection(light.lightDirection);
  const lit = (nx: number, ny: number): number =>
    Math.pow(clamp01(nx * direction[0] + ny * direction[1]), Math.max(source.specularPower, 1e-3));
  const straightSpecular =
    (geometry.widthCssPx - 2 * radius) * (lit(0, -1) + lit(0, 1)) +
    (geometry.heightCssPx - 2 * radius) * (lit(-1, 0) + lit(1, 0));
  // The straight runs' specular weight is a length like `straight` is, and the
  // arcs' is the contour integral per unit radius — the same two slots the
  // ambient band fills with its own length and `2π`.
  const ambient = coAreaBand(depth, metrics, 2 * Math.PI);
  const specular = coAreaBand(
    depth,
    { ...metrics, straight: straightSpecular },
    arcSpecularIntegral(source.specularPower, direction),
  );
  return (present * (source.rimAlpha * ambient + source.specularGain * specular)) / area;
}

/** A direction, normalised — the shader's `light.xy` is a unit vector and this says so. */
function unitDirection(direction: readonly [number, number]): readonly [number, number] {
  const length = Math.hypot(direction[0], direction[1]);
  return length > 1e-6 ? [direction[0] / length, direction[1] / length] : [0, -1];
}

/**
 * The inner shadow's area mean, as the fraction of the composite it KEEPS —
 * the shader's own `shadowKeep`, integrated over the silhouette (W17 G1;
 * Decision Log 2 (b), claims §5.74 §3).
 *
 * The shader darkens the whole composite by
 * `1 − (1 − clamp(−d/D, 0, 1))²·shadowDepth·shadowAlpha·present`, with the depth
 * `D = min(thickness·(1 + (shadowDepthGainMax − 1)·sizeK), span/2)` — the
 * authored thickness grown by the size law and clamped to the shorter half
 * extent. The profile of the darkening is the same squared ramp the rim band
 * carries, so its area mean is the same co-area integral over the inward
 * offsets, and the keep factor is one minus it.
 *
 * This tier draws no inner shadow, and before W17 its mirror did not carry one
 * either: the composite it declared was the body without the shadow, which is a
 * term of the renderer's the tier was silently short of. It is small — 0.9964 to
 * 0.9973 on the three probe cells, so 0.0018 to 0.0025 of the level — and it is
 * carried because a composite that is missing a term is missing it whatever its
 * size.
 */
export function interiorShadowKeep(
  source: MaterialSourceOptics,
  geometry: InteriorSurfaceGeometry,
  thickness: number,
  present: number,
  light: MaterialSourceInteriorLight = MATERIAL_SOURCE_INTERIOR_LIGHT,
): number {
  const metrics = rrectMetrics(geometry);
  const { area, span } = metrics;
  const depth = Math.max(
    Math.min(
      geometry.thicknessCssPx * (1 + (light.shadowDepthGainMax - 1) * clamp01(thickness)),
      span / 2,
    ),
    1e-4,
  );
  const profileMean = coAreaBand(depth, metrics, 2 * Math.PI) / area;
  const amplitude =
    source.shadowDepth * (1 + (light.shadowAmplitudeGainMax - 1) * clamp01(thickness));
  return clamp01(1 - Math.max(profileMean, 0) * amplitude * source.shadowAlpha * clamp01(present));
}

/**
 * The (colour, alpha) pair that composites to the same thing the renderer's
 * inner shadow leaves — the shader's own layer identity, run on this tier's
 * mirror (W17 G1; Decision Log 2 (b)).
 *
 * The shader writes `colour · shadowKeep` over an opaque body and, where the
 * body is a layer, `(k·a·c, 1 − k·(1 − a))` — which composites to `k` times what
 * `(a·c, a)` would. Carrying the shadow as that pair rather than as a subtracted
 * quantity keeps the tier's composite an exact affine in the backdrop: the slope
 * becomes `k·(1 − α)` and the tint's contribution `k·α·T`, and no point on the
 * backdrop's distribution is privileged. A keep of 1 returns the source
 * unchanged.
 */
export function innerShadowedSourceOptics(
  source: MaterialSourceOptics,
  keep: number,
): MaterialSourceOptics {
  const k = clamp01(keep);
  if (k >= 1) return source;
  const alpha = clamp01(source.tintAlpha);
  const shadowed = 1 - k * (1 - alpha);
  if (shadowed <= 1e-6) return { ...source, tintAlpha: 0 };
  const scale = (k * alpha) / shadowed;
  return {
    ...source,
    tintAlpha: shadowed,
    tint: [source.tint[0] * scale, source.tint[1] * scale, source.tint[2] * scale],
  };
}

/**
 * The chain's own quantum at one composite level, in **encoded codes** — the
 * number that decides which form the tier draws (W17 G1; Decision Log 4 (c)).
 *
 * `color-interpolation-filters="linearRGB"` says what space the filter works in
 * and not what precision it works at, and the engines carry eight bits: the
 * intermediate's step is 1/255 **in linear light**, whose width in the encoded
 * buffer the page composites into is `E(L + 1/255) − E(L)`. That is 12.7 codes
 * at black, 2.5 codes at 0.05, and falls through one code at 0.244 — so a
 * composite the renderer draws at 12/255 is a value the chain cannot hold, and
 * `impulse__capsule-button` measured exactly that: 0.0037 linear drawn as 0
 * (claims, W17 Decision Log 4's evidence).
 */
export function linearChainQuantumCodes(compositeLevel: number): number {
  const level = clamp01(compositeLevel);
  return 255 * (srgbEncode(Math.min(1, level + 1 / 255)) - srgbEncode(level));
}

/**
 * The tolerance the boundary is declared against: **one encoded code**.
 *
 * Not fitted and not chosen for a cell. It is the page's own quantum: the buffer
 * this tier composites into holds eight bits per channel in the ENCODED space,
 * so a filter chain whose intermediate is coarser than that buffer is drawing a
 * material the page could have held and did not. One code is the point where the
 * two are equal, and it is the only value on this axis that is a statement about
 * the pipeline rather than about a threshold someone liked.
 */
export const LINEAR_CHAIN_CODE_TOLERANCE = 1;

/**
 * Which form the tier draws for a composite at this level (Decision Log 4 (c)).
 *
 * `linear` is the exact one — the remainder inside the linear-light filter — and
 * it is what every light cell of the bed takes. `encoded` is W16's form with W17's
 * ordering fix and inner shadow: one `rgba()` over the blurred backdrop,
 * composited in the page's own encoded space, whose conversion is exact at one
 * declared backdrop level and off either side of it. The dark scheme keeps the
 * second, and that is a named gap rather than a silent one — the group state and
 * the capture cell both report which form drew.
 *
 * The boundary is the quantum, not a level: solving
 * `E(L + 1/255) − E(L) = 1/255` puts it at **0.2443** in linear light on the
 * shipped transfer function, and the constant is written as the predicate rather
 * than as that number so a different tolerance moves it honestly.
 */
export function cssTintFormAt(
  compositeLevel: number,
  toleranceCodes: number = LINEAR_CHAIN_CODE_TOLERANCE,
): "linear" | "encoded" {
  return linearChainQuantumCodes(compositeLevel) > toleranceCodes ? "encoded" : "linear";
}

/**
 * The remainder the sharp layer's filter carries under an encoded overlay at the
 * floor alpha, sampled as an `feComponentTransfer` table (Decision Log 4 (a)).
 *
 * ## Why a table and not the affine
 *
 * The tier's doctrine is that the surface always paints a real tint and never
 * relies on the blur for contrast, because S1's failure class — an engine that
 * reports support and renders nothing — cannot be probed. W17's first form put
 * the whole tint inside the filter and the contrast-floor test read a channel
 * delta of zero. So the floor stays an element paint: L3 keeps an encoded
 * overlay at `α₃`, and the filter carries what is left.
 *
 * What is left is not an affine. The page composites
 * `E(F(b))·(1 − α₃) + E(T)·α₃`, and for that to equal the renderer's
 * `E(M(b) + X)` the filter has to draw
 *
 *     F(b) = D((E(M(b) + X) − E(T)·α₃) / (1 − α₃))
 *
 * which carries `E` and `D` and is therefore curved. An affine fitted to it
 * would reintroduce exactly the point condition Decision Log 2 removed — a match
 * at one backdrop level and a curvature error either side of it, first order on a
 * bimodal cell. A `type="table"` transfer is piecewise linear over N points and
 * approximates `F` to a bound the caller can name, with no privileged point.
 *
 * ## N, from the interpolation bound
 *
 * The table's error is the piecewise-linear interpolation error of `F`, and N is
 * raised until the measured worst error over the sampled midpoints is under
 * `maxError`. Measured rather than bounded symbolically because `F` carries two
 * transfer functions and a clamp, and a bound loose enough to hold through all
 * three would cost points nobody needs: the bisection evaluates the thing itself.
 * At the shipped profile and the light cells' composites this settles at 33
 * points; the count is reported so a reader can see it move with the material.
 *
 * ## What it is not
 *
 * Not defined below the boundary `cssTintFormAt` draws: where the chain's own
 * quantum exceeds the tolerance the tier draws the encoded form and never builds
 * a table. And the values are clamped at zero — the spec clamps a primitive's
 * result anyway — with the non-negativity the ruling names asserted by the tests
 * rather than assumed here.
 */
export function cssTierTintTable(
  options: {
    /** The lerp's alpha after every fold. */
    readonly tintAlpha: number;
    /** The lerp's tint in linear light, one channel. */
    readonly tint: number;
    /** `X`, the band's derived light, linear. */
    readonly addedLight: number;
    /** `α₃`, the floor the overlay keeps. */
    readonly floorAlpha: number;
    /** `E(T)` for this channel — the overlay's own encoded level, 0..1. */
    readonly floorEncoded: number;
  },
  maxError = 1e-4,
): readonly number[] {
  const keep = 1 - clamp01(options.floorAlpha);
  const remainder = (b: number): number => {
    if (keep <= 1e-6) return 0;
    const composite = clamp01((1 - options.tintAlpha) * b + options.tintAlpha * options.tint + options.addedLight);
    return srgbDecode(
      Math.max(0, (srgbEncode(composite) - options.floorEncoded * clamp01(options.floorAlpha)) / keep),
    );
  };
  // Bisection on the count: sample at N points, measure the interpolation error
  // at the midpoints the table will interpolate across, double until it is under
  // the bound. Capped at 257 — one point per eight-bit input plus the endpoint —
  // because past that the table is finer than the value it is sampling.
  let count = 5;
  let values = sample(remainder, count);
  while (count < 257 && interpolationError(remainder, values) > maxError) {
    count = Math.min(257, (count - 1) * 2 + 1);
    values = sample(remainder, count);
  }
  return values;
}

/** `f` at `count` equally spaced points over [0, 1], clamped into the legal range. */
function sample(f: (b: number) => number, count: number): number[] {
  const out = new Array<number>(count);
  for (let i = 0; i < count; i += 1) out[i] = clamp01(f(i / (count - 1)));
  return out;
}

/** The worst error the table's own linear interpolation makes, at the segment midpoints. */
function interpolationError(f: (b: number) => number, values: readonly number[]): number {
  const count = values.length;
  let worst = 0;
  for (let i = 0; i < count - 1; i += 1) {
    const mid = (i + 0.5) / (count - 1);
    worst = Math.max(worst, Math.abs((values[i]! + values[i + 1]!) / 2 - clamp01(f(mid))));
  }
  return worst;
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
   *
   * **W16 G1 tried to replace it with the physical level, and measured that it
   * should not be.** Under the linear-light body the layer beneath the tint
   * carries a level the tier can DERIVE rather than fit — it runs from the
   * backdrop's encoded mean where the body is sharp to its linear mean where the
   * body is heavy, both of which `BackdropToneSample` already measures, mixed at
   * the body's own heavy share. Anchoring there is exact by construction and it
   * does exactly what it claims: on `checkerboard__rrect-md` it moves the
   * interior level from +0.059 over native to -0.002 at 1x, and from +0.076 to
   * +0.009 at 2x.
   *
   * It also makes the tier worse, for a reason worth stating because it belongs
   * to the composite rather than to the fit. The renderer lerps in LINEAR light
   * and encodes last, so the encode compresses its interior's excursions; this
   * tier source-overs an `rgba()` in ENCODED sRGB, where the tint scales those
   * excursions instead of compressing them. One alpha can match the mean or the
   * slope and not both. Anchoring at the physical level spends the tier's single
   * degree of freedom on the mean, and leaves the interior's spread 0.024-0.041
   * over native where the fitted anchor leaves it inside 0.007; `ssimMean` on the
   * two thick checkerboard cells falls by 0.006-0.026 at both scales. Measured on
   * single cells: level-anchored 0.8949 / 0.9081 on `rrect-md` at 1x / 2x against
   * the fitted anchor's 0.9028 / 0.9149 and the W15 bed's 0.8963 / 0.9174.
   *
   * So the fitted value stays, and it wins for the reason its own text gives: it
   * is fitted against the CROSS-TIER difference, and the GPU tier is itself
   * +0.012 to +0.058 over native on these cells' interior level — so an anchor
   * that lands this tier on the physics lands it off the tier it is required to
   * agree with. What is left is a named gap rather than a fit: the tier's
   * interior level runs about +0.05 to +0.09 over native on a high-contrast
   * backdrop. Closing it needs a SECOND degree of freedom in the composite — a
   * contrast term in the sharp layer's filter list, solved jointly with the alpha
   * for the mean and the slope — which is a new optical term, and a decision this
   * wave did not charter.
   *
   * **W17 G1 closed it, and this constant is not on that path (Decision Log 2 (c),
   * (d)).** The second degree of freedom turned out not to be needed: the
   * renderer's composite is an affine in the backdrop and an `feComponentTransfer`
   * inside the sharp layer's linear-light filter is an affine, so the lerp itself
   * moves into the filter with no free parameter to solve and no privileged
   * backdrop level at all. **Wherever the engine's conformance row renders a
   * reference filter inside `backdrop-filter`, nothing reads this value**: the
   * tier's composite is `cssTierTintTransfer`'s and this mapping's conversion is
   * not evaluated. It is still the anchor of the one-alpha conversion the
   * plain-`blur()` engines keep (contract X9), and of `cssTintAlpha` and
   * `cssTintColor` wherever a caller reaches them directly.
   *
   * **Decision (W17 G1, on Decision Log 2 (d)'s advisory): the plain-`blur()`
   * anchor stays at 0.02.** The advisory was to move it to the group's own
   * sampled level, and the number that decides it is already recorded three
   * paragraphs above: W16 G1 measured exactly that anchor. It lands the level
   * (`checkerboard__rrect-md` +0.059 → −0.002 at 1x, +0.076 → +0.009 at 2x) and
   * costs the slope, leaving the interior's spread 0.024–0.041 over native
   * against the fitted anchor's 0.007 and dropping `ssimMean` by 0.006 to 0.026
   * on the two thick checkerboard cells. That trade is a property of the
   * composite and not of the alpha it is taken at — one encoded alpha can match
   * the mean or the slope and not both — so W17's ordering fix, which moves the
   * alpha this anchor converts, does not change its direction. And the engines
   * this now governs are the ones the harness cannot capture at all (Gecko and
   * WebKit render `backdrop-filter` as a no-op in every automatable path), so
   * moving them on an advisory would be a change no measurement could referee.
   * The gap it leaves is E's, named and unchanged: those engines' interior level
   * runs about +0.05 to +0.09 over native on a high-contrast backdrop.
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
  /*
   * The ambient drop shadow used to be a CSS-ONLY constant here — a triple of
   * 6 px / 24 px / 0.18 that Decision Log #32(c) then zeroed, on the measurement
   * that it "is the one thing this tier draws that the reference material does
   * not". W8 moved it out of this mapping altogether: the reference's ACTIVE
   * material does cast one, so it is a facet of the material rather than a
   * decoration of this tier, and it lives in the mirrored profile block
   * `MATERIAL_SOURCE_OUTER_SHADOW` where both tiers read one set of numbers. The
   * K5 measurement stands and its cause is now known — the extractor was
   * measuring the shadow's extent as the surface's shape, and the reference it was
   * measured against had none because the window was never key.
   */

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
 * This tier's numbers for a surface whose material carries an author tint (W10).
 *
 * `css` is the untinted material already converted (`cssOpticsFromSource`): one
 * `rgba()` layer over the blurred backdrop, composited encoded. The author's
 * layer is another `rgba()` — the seed at its shade, opaque, at the author's
 * opacity — over THAT, and two encoded-space layers fold into one exactly:
 *
 * ```
 * α″ = 1 − (1 − s)(1 − α′)
 * C″ = ((1 − s)·α′·C′ + s·E(layer)) / α″      per channel
 * ```
 *
 * Convex in both colours, so the fold never leaves the gamut — the clip §5.13
 * attributed the tinted coherence miss to cannot occur here. Everything but the
 * tint colour and its alpha is the untinted conversion, unchanged; a tint of
 * zero strength returns `css` identically.
 *
 * The shade is read at ONE luminance per source, this tier's granularity: the
 * GPU tier's tracks the checker cell by cell, this tier paints one orange. The
 * mean lands; the structure cost is the tier's known one.
 */
/**
 * The author's tint as its own encoded layer — the seed at the shade the
 * material's luminance puts it at, and the author's opacity.
 *
 * Split out of `tintedCssOptics` at W17 G1 because the fold and the layer are no
 * longer the same thing on every engine. Where the tier carries the material's
 * lerp inside its filter (Decision Log 2 (c)) the fold has nothing left to fold
 * — the material's `rgba()` is gone — and L3 draws this layer alone, at the
 * author's own opacity, over the filter's output. That composites to
 * `(1 − s)·(material) + s·(layer)`, which is exactly what the folded pair
 * composited to and is exactly what the shader writes; the difference is the
 * space the material's half was computed in, which is the whole of this wave.
 */
export function authorTintLayer(
  source: MaterialSourceOptics,
  tint: { readonly color: LinearRgb; readonly strength: number } | undefined,
  backdropLuminance: number,
  grip: number,
  shade: TintShadeConstants = TINT_SHADE,
): { readonly color: Rgb255; readonly strength: number } | undefined {
  if (tint === undefined || tint.strength <= 0) return undefined;
  return {
    color: encodeRgb(
      tintShadeLayer(tint.color, materialLuminance(source, backdropLuminance), grip, shade),
    ),
    strength: clamp01(tint.strength),
  };
}

export function tintedCssOptics(
  css: MaterialOptics,
  source: MaterialSourceOptics,
  tint: { readonly color: LinearRgb; readonly strength: number } | undefined,
  backdropLuminance: number,
  grip: number,
  shade: TintShadeConstants = TINT_SHADE,
): MaterialOptics {
  const author = authorTintLayer(source, tint, backdropLuminance, grip, shade);
  if (author === undefined) return css;
  const s = author.strength;
  const layer = author.color;
  const alpha = clamp01(css.tintAlpha);
  const folded = 1 - (1 - s) * (1 - alpha);
  const channel = (index: 0 | 1 | 2): number =>
    Math.round(((1 - s) * alpha * css.tint[index] + s * layer[index]) / folded);
  return { ...css, tintAlpha: folded, tint: [channel(0), channel(1), channel(2)] };
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
  return {
    ...base,
    tintAlpha: alpha,
    tint: cssTintColor(source, alpha, mapping),
    // Derived rather than inherited from `base`, because the backdrop adaptation
    // is allowed to move the rim and this is the one conversion it lands through.
    // Identical to `base`'s for every source that did not move it — the same
    // expression `cssTierOptics` uses, on the same constant.
    borderAlpha: clamp01(source.rimAlpha * mapping.borderAlphaPerRimAlpha),
  };
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

/** The pair a GPU-tier group that samples nothing writes as its layer (W11a). */
export interface UnsampledMaterial {
  /** The profile's tint, linear light — the renderer encodes it on the way out. */
  readonly tint: LinearRgb;
  /** The CSS tier's alpha for the same material: `cssTintAlpha` at the mapping's reference level. */
  readonly tintAlpha: number;
}

/**
 * The material as a GPU-tier group writes it when it has NO backdrop to sample
 * (W11a): a `css-backdrop` group, whose frost is a DOM proxy under the canvas,
 * or a `none` group over the page. The optics pass writes such a surface as a
 * premultiplied layer and the browser composites it in encoded sRGB — the same
 * space this tier's `rgba()` lands in, and the same reason `cssTintAlpha`
 * exists. So the pair is this tier's: the renderer's own tint (linear, encoded
 * once on output) at the alpha the mapping solved for the CSS tier, so a
 * nested surface reads the same on both tiers by construction rather than by
 * two fits. The renderer folds the accessibility policy over it exactly as
 * `cssTierDeclarations` folds it over the CSS tier's copy.
 */
export function unsampledMaterials(
  patch?: RendererMaterialProfile,
  mapping: CssTierMapping = CSS_TIER_MAPPING,
): Readonly<Record<MaterialVariant, UnsampledMaterial>> {
  const resolved = {} as Record<MaterialVariant, UnsampledMaterial>;
  for (const variant of ["regular", "clear"] as const) {
    const source = sourceOptics(patch)[variant];
    resolved[variant] = { tint: source.tint, tintAlpha: cssTintAlpha(source, mapping) };
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
// FITTED (round two, 2026-08-31) 0.4722 -> 0.75. The old value was the pre-C9a
// lift re-expressed as a fraction, never a measurement, and it under-occluded
// against the active bed on both accessibility profiles. Mirrors
// `@vitrea/renderer-webgpu`'s constant, where the fit is recorded.
export const INCREASED_OCCLUSION_LIFT = 0.75;

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
