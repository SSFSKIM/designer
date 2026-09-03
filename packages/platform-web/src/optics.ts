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
  regular: { blurSigma: 1.25, tint: [1, 1, 1], tintAlpha: 0.46, rimAlpha: 0.18, highlight: [1, 1, 1] },
  // Persistently more transparent, so it frosts less and tints less — and it
  // carries its own dimming policy from core. Uncalibrated in either tier: the
  // canonical scene matrix has no clear-variant scene.
  clear: { blurSigma: 4, tint: [1, 1, 1], tintAlpha: 0.1, rimAlpha: 0.14, highlight: [1, 1, 1] },
};

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
   * The body's depth ramp (W13 G1, claims §5.61 §2): the sharp component's
   * share at the contour and the ramp's reach in DEVICE px, each anchored at
   * dpr 1 and dpr 2 and interpolated between. This tier cannot render a ramp —
   * one `backdrop-filter` has one σ — so what it carries is the ramp's
   * per-surface projection, which is what `scatterThickness` computes on both
   * tiers from these four numbers. See `scatterThickness`.
   */
  readonly sizeScatterRampStart1x: number;
  readonly sizeScatterRampStart2x: number;
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
  sizeScatterRampStart1x: 0.6,
  sizeScatterRampStart2x: 0.35,
  sizeScatterRampReach1xPx: 110,
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
  readonly occlusion: number;
  readonly reducedTransparencyOcclusion: number;
  readonly sizeGain: number;
}

/** Mirrors `@vitrea/renderer-webgpu`'s `DEFAULT_MATERIAL_PROFILE.outerShadow`. */
export const MATERIAL_SOURCE_OUTER_SHADOW: MaterialSourceOuterShadow = {
  offsetPx: 7.95,
  sigmaPx: 15.55,
  spreadPx: 3.1,
  occlusion: 0.285,
  reducedTransparencyOcclusion: 0.7,
  sizeGain: 0,
};

/** The outer shadow's constants under a profile patch, by the renderer's merge rule. */
export function sourceOuterShadow(patch?: RendererMaterialProfile): MaterialSourceOuterShadow {
  return { ...MATERIAL_SOURCE_OUTER_SHADOW, ...patch?.outerShadow };
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
 * multiplies by is measured rather than assumed. Under forced colours the
 * material is gone and its shadow goes with it.
 */
export function outerShadowUnderPolicy(
  shadow: MaterialSourceOuterShadow,
  policy: ResolvedMaterialPolicy,
): MaterialSourceOuterShadow {
  if (policy.glass === "none" || policy.frost === "none") return { ...shadow, occlusion: 0 };
  if (policy.frost === "increased") {
    return { ...shadow, occlusion: shadow.occlusion * shadow.reducedTransparencyOcclusion };
  }
  return shadow;
}

/** The size-law constants under a profile patch, by the renderer's merge rule. */
export function sourceSize(patch?: RendererMaterialProfile): MaterialSourceSize {
  return {
    sizeSpanMin: patch?.sizeSpanMin ?? MATERIAL_SOURCE_SIZE.sizeSpanMin,
    sizeSpanMax: patch?.sizeSpanMax ?? MATERIAL_SOURCE_SIZE.sizeSpanMax,
    sizeScatterGainMax: patch?.sizeScatterGainMax ?? MATERIAL_SOURCE_SIZE.sizeScatterGainMax,
    sizeScatterFloor: patch?.sizeScatterFloor ?? MATERIAL_SOURCE_SIZE.sizeScatterFloor,
    sizeScatterRampStart1x:
      patch?.sizeScatterRampStart1x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStart1x,
    sizeScatterRampStart2x:
      patch?.sizeScatterRampStart2x ?? MATERIAL_SOURCE_SIZE.sizeScatterRampStart2x,
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
 * really write, which at dpr 2 is not the one it writes at dpr 1.
 *
 * `devicePixelRatio` is the scale the tier draws at (W12 G3, claims §5.56): the
 * widths are device-pixel quantities, so the σ in CSS px is `sigmaPx / dpr`
 * scaled by the weight `scatterThickness` projects. It defaults to 1, where the
 * expression is the 1x law exactly.
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
  );
}

/**
 * **The device scale this tier reads the body's depth ramp at** (W13 G1,
 * Decision Log 1 question 2 (a)).
 *
 * One `backdrop-filter` cannot carry a ramp, so this tier renders the ramp's
 * per-surface average — and it takes that average at dpr 1 whatever ratio the
 * page is composited at. The reason is measured rather than conservative: this
 * tier's own best single σ is *larger* in CSS px at 2x (claims §5.55 §5), the
 * opposite of the device-pixel widths, so projecting the ramp at the device
 * scale would move the 2x dom rows the way the measurement says is wrong. The
 * tier's claim is narrowed to "the CSS tier renders the 1x material" and its 2x
 * rows stay held by decision until the two-layer CSS body wave gives the tier a
 * form that can carry depth.
 *
 * This is deliberately one number in one place: flipping it to the live ratio is
 * the whole of decision 2 (b).
 */
export const CSS_TIER_RAMP_SCALE = 1;

/**
 * The depth ramp's start at a device scale — s₀(dpr), the mirror of the
 * renderer's `scatterRampStart` (W13 G1, claims §5.61 §2).
 *
 * The reference was read at dpr 1 and dpr 2 and nowhere between, so the law is
 * anchored at those two, interpolated linearly, and held outside [1, 2].
 */
export function scatterRampStart(
  devicePixelRatio: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  return rampAtScale(size.sizeScatterRampStart1x, size.sizeScatterRampStart2x, devicePixelRatio);
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
 * The sharp component's share at a depth — s(u), the mirror of the renderer's
 * `scatterSharpShare` (W13 G1). This tier never evaluates it per pixel; it is
 * exported so that the projection below can be checked against the law it
 * projects, and so `tier-coherence` can pin the two tiers on the law itself and
 * not only on its average.
 */
export function scatterSharpShare(
  uDevicePx: number,
  devicePixelRatio: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
): number {
  const start = scatterRampStart(devicePixelRatio, size);
  const reach = Math.max(scatterRampReachDevicePx(devicePixelRatio, size), 1e-6);
  return clamp01(start - Math.max(uDevicePx, 0) / reach);
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
 * The average is exact: on a rectangle the area at depth ≥ u is
 * `(W − 2u)(H − 2u)`, so the area at depth u has measure `P − 8u`, and s is
 * piecewise linear in u, so `k̄ = 1 − (1/WH) ∫ s(u)(P − 8u) du` integrates in
 * closed form. The corners are ignored, as the renderer's copy documents.
 * `extentsCssPx` is the surface's own width and height where the caller has
 * them; where it does not, the surface is taken to be a square of the span.
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
  const floor = clamp01(size.sizeScatterFloor);
  return clamp01(floor + (scatterRampAreaMean(spanPx, size, devicePixelRatio, extentsCssPx) - floor) * fold);
}

/**
 * The unfolded area average of the heavy share over a surface — the integral
 * `scatterThickness` documents, and the mirror of the renderer's
 * `scatterRampAreaMean`.
 */
export function scatterRampAreaMean(
  spanPx: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
  extentsCssPx?: readonly [number, number],
): number {
  const width = Math.max(extentsCssPx?.[0] ?? spanPx, 0);
  const height = Math.max(extentsCssPx?.[1] ?? spanPx, 0);
  const area = width * height;
  const start = scatterRampStart(devicePixelRatio, size);
  // The reach in CSS px, which is the unit a surface's extents arrive in: the
  // ratio u/U is scale-free, so dividing the device-px reach by the same dpr the
  // depth would have been multiplied by gives the identical number.
  const reach = Math.max(
    scatterRampReachDevicePx(devicePixelRatio, size) / Math.max(devicePixelRatio, 1e-3),
    1e-6,
  );
  if (area <= 0) return clamp01(1 - clamp01(start));
  const perimeter = 2 * (width + height);
  const deepest = Math.min(width, height) / 2;
  const saturated = Math.min(Math.max(reach * (start - 1), 0), deepest);
  const vanished = Math.min(Math.max(reach * start, 0), deepest);
  const flat = perimeter * saturated - 4 * saturated * saturated;
  const a = saturated;
  const b = vanished;
  const sloped =
    start * perimeter * (b - a)
    - ((8 * start + perimeter / reach) * (b * b - a * a)) / 2
    + ((8 / (3 * reach)) * (b * b * b - a * a * a));
  return clamp01(1 - (flat + sloped) / area);
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
 * `devicePixelRatio` divides the σ because the two widths are device-pixel
 * quantities (W12 G3, claims §5.56 §1, verified §5.58 §2).
 */
export function sizeScatterSigmaAt(
  sigmaPx: number,
  scatter: number,
  size: MaterialSourceSize = MATERIAL_SOURCE_SIZE,
  devicePixelRatio = 1,
): number {
  const mix = clamp01(scatter);
  return (sigmaPx / Math.max(devicePixelRatio, 1e-3)) * (1 + (size.sizeScatterGainMax - 1) * mix);
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
export function tintedCssOptics(
  css: MaterialOptics,
  source: MaterialSourceOptics,
  tint: { readonly color: LinearRgb; readonly strength: number } | undefined,
  backdropLuminance: number,
  grip: number,
  shade: TintShadeConstants = TINT_SHADE,
): MaterialOptics {
  if (tint === undefined || tint.strength <= 0) return css;
  const s = clamp01(tint.strength);
  const layer = encodeRgb(
    tintShadeLayer(tint.color, materialLuminance(source, backdropLuminance), grip, shade),
  );
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
