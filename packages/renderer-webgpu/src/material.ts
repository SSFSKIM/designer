/**
 * The optical constants, and the two foldings that decide what the shader
 * actually gets: the dual cap, and the size-parameterised lens.
 *
 * **Every number here is advisory and calibration-delegated (C7).** They are
 * chosen so the material is coherent out of the box — a plausible glass, not a
 * measured one — and §Calibration names exactly this kind of value as a delegated
 * unknown. They live in one profile object (`MaterialProfile`) so replacing them
 * with fitted values is a data change (`withMaterialOverrides`), and no shader
 * carries a literal of its own. The named constants below are re-exports of that
 * profile's defaults, kept because a reader wants a name for σ = 8 more often
 * than a whole profile.
 *
 * ## The dual cap (Decision Log #19)
 *
 * Two independent things cap refraction: the accessibility policy's regime
 * (`nominal | reduced | none`) and the group's resolved capability state
 * (`true | approximate | none` — what the sampling backend can actually deliver).
 * **The lower of the two wins**, and this module folds them into one scalar before
 * anything reaches a uniform, so the shader has no way to honour the wrong one.
 *
 * The ordering is `@vitrea/policy`'s, and so is the fold. It used to be restated
 * here — this package sits *below* core in the dependency graph and platform-web
 * sits above it, so for most of v1 there was no module both tiers could see and
 * the CSS tier carried a second copy. Decision Log #23(d) closed that seam by
 * putting the ladder in a pure leaf underneath everything, which the renderer can
 * depend on directly (alongside `@vitrea/geometry`) with no cycle to close. The
 * two copies can no longer disagree because there is only one.
 */

import {
  accessibilityRefractionCap,
  DEFAULT_REFRACTION_SCALE,
  REFRACTION_LADDER,
  type RefractionQuality,
} from "@vitrea/policy";

import type { Rgb } from "./color";
import { srgbToLinear } from "./color";

// Re-exported under the names this package and its tests already know them by,
// so nothing downstream has to learn where the ladder went.
export {
  accessibilityRefractionCap,
  effectiveRefraction,
  REFRACTION_LADDER,
  refractionRank,
  type RefractionQuality,
} from "@vitrea/policy";

/**
 * The slice of core's `ResolvedAccessibilityPolicy["material"]` the renderer
 * reads. core's type is assignable to this; a test pins that.
 */
export interface MaterialPolicyView {
  readonly glass: "material" | "none";
  readonly frost: "nominal" | "increased" | "none";
  readonly refraction: "nominal" | "reduced" | "none";
  readonly occlusion: "nominal" | "increased" | "opaque";
  readonly border: "nominal" | "strong";
  readonly ambientTint: "nominal" | "reduced" | "none";
  readonly foreground: "adaptive" | "near-monochrome";
}

/** Nominal accessibility material policy — nothing capped. Mirrors core's. */
export const NOMINAL_MATERIAL_POLICY: MaterialPolicyView = {
  glass: "material",
  frost: "nominal",
  refraction: "nominal",
  occlusion: "nominal",
  border: "nominal",
  ambientTint: "nominal",
  foreground: "adaptive",
};

/** The two variants, declared as data so a profile merge can walk them. */
export const MATERIAL_VARIANTS = ["regular", "clear"] as const;

export type MaterialVariant = (typeof MATERIAL_VARIANTS)[number];

export interface MaterialOptics {
  /** Body blur σ in CSS px. Matches `platform-web`'s `MATERIAL_OPTICS.blurRadius`. */
  readonly blurSigma: number;
  /** Tint over the blurred backdrop, linear light. */
  readonly tint: Rgb;
  readonly tintAlpha: number;
  /** Rim band half-width in CSS px, and its ambient brightness. */
  readonly rimWidth: number;
  readonly rimAlpha: number;
  /** Specular exponent and gain on the rim. */
  readonly specularPower: number;
  readonly specularGain: number;
  /** Inner-shadow depth (0..1) and how much of it is applied. */
  readonly shadowDepth: number;
  readonly shadowAlpha: number;
  /** Highlight colour for the sweep and press glow, linear light. */
  readonly highlight: Rgb;
}

/** The rim a `border: "strong"` policy substitutes, whatever the variant asked for. */
export interface MaterialRim {
  readonly rimWidth: number;
  readonly rimAlpha: number;
}

/**
 * The outer shadow (W8) — the material's own occlusion of the backdrop *outside*
 * its contour, and the largest single facet the project has measured.
 *
 * Not the same quantity as `MaterialOptics.shadowDepth`/`shadowAlpha`, which are
 * the *inner* shadow: that one darkens the material's own body near its contour,
 * this one darkens what is behind and beside the surface. Profile-level rather
 * than per-variant, because the bed measures it per profile and never varied the
 * variant.
 *
 * ## The mechanism, as measured
 *
 * The reference's shadow is the component's OWN rounded silhouette, outset by
 * `spreadPx`, translated down by `offsetPx`, blurred by a Gaussian of standard
 * deviation `sigmaPx`, and applied MULTIPLICATIVELY: the backdrop keeps
 * `1 − occlusion·falloff` of its own light. Fitted in two dimensions against the
 * active bed, that model reproduces the reference to an RMS of 0.0021 in
 * occlusion over 142,550 pixels on the finest cell, and the same three lengths
 * describe every profile, backdrop, span and scale in the bed.
 *
 * **Multiplicative, and not additively.** Mirrored pixel pairs either side of a
 * capsule over the `photo` backdrop see the same shadow over different backdrop
 * luminances: the darkening's ratio tracks the backdrop's ratio to 4.5% while a
 * constant-subtraction model misses by 79% of the signal. So the shadow is
 * analytically INVISIBLE over black — `dark-solid` cells are byte-identical to
 * their background — and that property is what both tiers reproduce exactly,
 * because a fully transparent black composited over anything leaves it alone and
 * black times anything is black.
 *
 * ## Lengths, in points
 *
 * Every length below is in CSS px and the 2× bed proves it: `sigmaPx` measures
 * 15.5 at 1× and 31.0 at 2× device px, `offsetPx` 7.9 and 15.8. A shadow
 * specified in points is what doubles that way.
 *
 * They are also SPAN-INVARIANT, which is a positive measurement rather than an
 * absence: across spans of 32, 44, 96 and 160 px the fitted σ stays within
 * 15.4…15.9 and the offset within 6.9…8.1. The size law reaches the amplitude
 * (`sizeGain`) and nothing else.
 */
export interface MaterialOuterShadow {
  /** Downward translation of the shadow's silhouette, CSS px. */
  readonly offsetPx: number;
  /** Gaussian σ the silhouette is blurred by, CSS px. A `box-shadow` blur is 2σ. */
  readonly sigmaPx: number;
  /** Outward spread of the silhouette before the blur, CSS px. */
  readonly spreadPx: number;
  /**
   * Peak occlusion: the fraction of the backdrop's own LINEAR light removed deep
   * inside the shadow. Zero stands the whole facet down, pad and all.
   */
  readonly occlusion: number;
  /**
   * What reduced transparency does to `occlusion` — MEASURED, not assumed, which
   * is what the charter asked for before the fold was written.
   *
   * The reference's shadow under `reduce transparency` is the same shadow at
   * 0.566 of the amplitude: 0.1830/0.3259, 0.1884/0.3309 and 0.1882/0.3314 on the
   * three structured backdrops at a 44 px span, with σ, offset and spread
   * unmoved. It does not vanish and it does not intensify.
   *
   * The `increased contrast` reference reproduces the reduced-transparency
   * amplitude to four decimals (0.1830, 0.1884, 0.1882 — the same numbers), which
   * is Decision Log 8's finding again: macOS force-couples the two toggles, so the
   * contrast reference IS the reduced-transparency state and the bed cannot
   * separate them. The fold therefore keys on `frost`, the axis reduced
   * transparency alone sets, rather than on the contrast axes it would be
   * indistinguishable on here.
   */
  readonly reducedTransparencyOcclusion: number;
  /**
   * The size law's grip on the amplitude: the fraction of the REMAINING
   * transparency a full-thickness surface's shadow closes, on
   * `sizeOcclusionGain`'s relative form.
   *
   * Ships at 0 — the identity — and the reason is a measurement rather than an
   * absence of one. Fitted per scene at a frozen geometry, the amplitude's span
   * dependence points in OPPOSITE directions in the two colour schemes: light
   * standard falls from 0.326 to 0.196 between a 44 px and a 96 px span over
   * `photo` (and 0.331 → 0.285 over `checkerboard`, 0.331 → 0.245 over
   * `hc-text`), while dark standard RISES from 0.060 to 0.177 to 0.274 across 44,
   * 96 and 160 px. Under reduced transparency it is flat (0.183, 0.192, 0.165).
   * One monotone gain on one thickness curve cannot be all three, and any
   * non-zero value fitted to one scheme is wrong in the other — the same shape of
   * finding Decision Log 13 recorded for W7's curve ("surface size is its own
   * axis"). The seam ships so the cascade can fit it if a two-axis rework lands;
   * the value stays at the identity until something can identify it.
   */
  readonly sizeGain: number;
}

/**
 * Every number the material runs on, in one place.
 *
 * The same seam `@vitrea/motion`'s `MotionProfile` opens for the drivers, for the
 * optics: C7's harness measures these against `apple-macos-26.5-*` fixtures and
 * replaces what is here, so nothing downstream may hard-code an optical constant
 * of its own. A profile overrides every one of them (`withMaterialOverrides`),
 * which makes landing a calibrated set a data change rather than a code change.
 *
 * Units: CSS px for distance, linear light for colour, viewport coordinates with
 * y pointing down for direction.
 */
export interface MaterialProfile {
  /** Per-variant optics. `clear` is persistently more transparent than `regular`. */
  readonly optics: Readonly<Record<MaterialVariant, MaterialOptics>>;

  /** The two ends of adaptation: what the tint becomes over a dark and a light backdrop. */
  readonly adaptiveTintDark: Rgb;
  readonly adaptiveTintLight: Rgb;
  /** Luminance band the tint crosses over. Hysteresis in time is the driver's job. */
  readonly adaptiveLuminanceLow: number;
  readonly adaptiveLuminanceHigh: number;

  /**
   * How much of the lens the shader is allowed to apply, per rung.
   *
   * `approximate` is not "half of true": it is the rim-lensing approximation, a
   * shallower bend confined nearer the edge, which is what a group sampling a CSS
   * proxy can honestly claim. Reduced transparency lands here too, which is the
   * point of the ladder having three rungs and not two.
   */
  readonly refractionScale: Readonly<Record<RefractionQuality, number>>;

  /**
   * **The size law's one curve** — the span band over which the material stops
   * reading as a thin sheet and starts reading as a thick slab (W2).
   *
   * Apple states one mechanism and lists its consequences: as glass "morphs to
   * larger sizes… its material characteristics change to simulate a thicker, more
   * substantial material. It casts deeper, richer shadows, has more pronounced
   * lensing and refraction effects, and a softer scattering of light" (S219). One
   * mechanism means one curve: `sizeThickness(span)` is a smoothstep from
   * `sizeSpanMin` to `sizeSpanMax`, and **every** thickness-derived facet is a
   * gain on it — the lens (`lensSizeGainMax`), the scattering
   * (`sizeScatterGainMax`), the occlusion (`sizeOcclusionGain`) and the inner
   * shadow (`sizeShadowGainMax`). Two curves would be two mechanisms, and the
   * reference only has one.
   *
   * A smoothstep rather than a straight ratio, so two surfaces of nearly the same
   * size never read as differently thick, and so every gain saturates instead of
   * growing without bound on a full-width platter. Below `sizeSpanMin` the whole
   * law is **exactly inert**: a small control renders as it did before the law
   * existed, which is what makes the law additive rather than a global retune.
   *
   * MEASURED (W2, on the settled bed): the band is where the reference's own
   * size-dependence happens. Over a fixed checkerboard backdrop the light-standard
   * reference passes 0.244 of the backdrop's contrast at a 32 px span, 0.230 at
   * 44 px and 0.144 at 96 px, and its backdrop correlation falls 0.634 → 0.606 →
   * 0.475 across the same three — so the movement is essentially complete by 96 px
   * and has barely started at 32. See the claims doc's size-law section.
   */
  readonly sizeSpanMin: number;
  readonly sizeSpanMax: number;

  /**
   * The lens's gain on the size curve — "more pronounced lensing and refraction".
   *
   * `lensDepthPx` is `thickness × lensSizeGain(span)`, clamped to the shorter
   * *half* extent. The clamp is what keeps a small control from being all lens: a
   * 24 px-tall button cannot bend more than 12 px of backdrop however thick it is
   * authored.
   */
  readonly lensSizeGainMax: number;

  /**
   * The scattering gain — "a softer scattering of light". How many times wider
   * the material's body blur runs at full size.
   *
   * **The facet the settled bed identifies most directly.** Two backdrops
   * disagree in exactly the way a widening kernel predicts and an opacity change
   * does not. Over the checkerboard — all of whose structure sits at one 16 px
   * period, and whose surroundings carry the same mean as its interior — the
   * reference's retained contrast falls 41% from a 32 px span to a 96 px one while
   * its interior *level* stays put (0.607 → 0.641). Over the synthetic photo —
   * broadband, and with surroundings whose mean differs from the mask's — the
   * retained contrast barely moves between 44 px and 96 px (0.546 → 0.544) while
   * the level converges toward the neighbourhood (0.585 → 0.628). A larger alpha
   * would have moved both backdrops' contrast together and pulled both levels
   * toward the tint; a wider kernel moves exactly what moved.
   *
   * Both tiers carry it, from one function (`sizeScatterSigma`): the CSS tier
   * multiplies its `blur()` σ, and the GPU tier lerps its body sample toward the
   * chain level whose blur is that σ.
   */
  readonly sizeScatterGainMax: number;

  /**
   * The occlusion gain — "a larger size is more opaque. A smaller size is
   * clearer" (S284). The fraction of the *remaining* transparency the size law
   * closes at full size.
   *
   * Relative rather than absolute, for `increasedOcclusionLift`'s reason: a floor
   * dies silently the moment nominal passes it, and a fraction of the headroom
   * cannot. It also composes correctly with the accessibility lift — under reduced
   * transparency nominal is already near 1, so the size law has almost no headroom
   * left to close, which is exactly what the reference does there (its transmission
   * reads 0.011 at a 44 px span and 0.014 at 96 px — no size dependence, because
   * there is none left to have).
   */
  readonly sizeOcclusionGain: number;

  /**
   * The inner shadow's gain — "casts deeper, richer shadows". A multiplier on
   * `shadowDepth` at full size.
   *
   * **Coupled by construction, not fitted, and the difference is stated rather
   * than hidden.** The fixtures cannot identify it: the reference's peak darkening
   * outside its contour measures 0.0000–0.0001 on almost every calibration scene
   * and vitrea's measures the same order (C9a, `shadowFalloff`), so there is no
   * measured gap for a sweep to close, and what this renderer's `shadowDepth`
   * scales is an *inner* shadow whose contribution to the interior level is
   * degenerate with the tint's — two constants, one observable. So the direction
   * comes from Apple's sentence and the magnitude is held to what the objective is
   * flat over, with that flatness recorded. GPU tier only: the CSS tier's shadow is
   * an outer `box-shadow` the reference does not cast at all (Decision Log #32(c)).
   */
  readonly sizeShadowGainMax: number;

  /** Chain LOD per CSS px of lens depth, and how much sharper the rim samples. */
  readonly lensBodyLodPerPx: number;
  readonly lensRimLodBias: number;

  /**
   * What each accessibility regime does to the numbers above. The multipliers
   * match `platform-web`'s CSS tier so the two renderers degrade the same way
   * under the same preference.
   */
  readonly reducedTransparencyFrost: number;
  /**
   * How much of the *remaining* transparency reduced transparency closes.
   *
   * **Relative, not absolute (Decision Log #32(d)).** This was
   * `increasedOcclusionAlpha`, an absolute floor of 0.62 applied as
   * `Math.max(nominal, floor)` — a real lift while nominal was the advisory 0.28,
   * and a no-op from the moment C9a measured nominal at 0.62. The policy died
   * without being touched and nothing noticed for a whole child. A fraction of the
   * headroom cannot die that way: it lifts strictly for every nominal below 1,
   * whatever a later tuning pass moves nominal to.
   *
   * The fraction is the pre-C9a lift, restored rather than invented:
   * (0.62 − 0.28) / (1 − 0.28) = 0.4722, which reproduces the old floor exactly at
   * the old nominal. At today's nominal it reads 0.62 → 0.799.
   *
   * Mirrored by `@vitreajs/vitrea-web`'s `INCREASED_OCCLUSION_LIFT`, and pinned in
   * both directions by `packages/calibration/test/tier-coherence.test.ts`.
   */
  readonly increasedOcclusionLift: number;
  readonly strongBorderRim: MaterialRim;
  readonly reducedTintAdaptation: number;

  /**
   * The author tint's tone map — Apple's "range of tones **mapped to content
   * brightness underneath**" (S219), as four numbers.
   *
   * The seed the author gives is not the colour the material paints. It is the
   * middle of a range: over a dark backdrop the material shows a shade of the
   * seed (`tintToneFloor`, a multiple of it in linear light, so hue and
   * chromaticity survive); over a bright one it shows the seed washed toward
   * white (`tintToneCeilMix`), which is what Apple's "changing its hue,
   * brightness and saturation… without deviating too much from the intended
   * color" describes. `tintToneLow`/`tintToneHigh` are the backdrop luminances
   * the two ends are reached at, crossed with a smoothstep for the same reason
   * `lensSpanMin`/`lensSpanMax` are.
   *
   * **Advisory and calibration-delegated**, like every other number in this
   * profile: they are chosen so a tinted surface reads as coloured glass rather
   * than as paint, and the tinted-capture extension fits them. Nothing here is
   * measured yet, and no claim rests on these values.
   */
  readonly tintToneFloor: number;
  readonly tintToneCeilMix: number;
  readonly tintToneLow: number;
  readonly tintToneHigh: number;

  /**
   * **Backdrop tone adaptation (W7)** — the axis Apple's material has and this
   * one did not: over a dark enough backdrop the material stops being a lighter
   * thing in front of it and takes the backdrop's own tone.
   *
   * The mechanism is one mix, and it is deliberately the *tint colour* rather
   * than the tint alpha: `backdropToneMax` at full strength makes the tint equal
   * the sampled backdrop, so `mix(backdrop, tint, tintAlpha)` collapses to the
   * backdrop exactly and the surface is left with its rim, its inner shadow and
   * its lensing and nothing else. That is what the settled reference does —
   * `dark-solid__capsule-button__rest` is byte-identical to its own background
   * in every standard profile, at both scales, in both colour schemes.
   *
   * `backdropToneLow`/`backdropToneHigh` are the backdrop luminances (linear)
   * the two ends are reached at, crossed with a smoothstep for the same reason
   * `tintToneLow`/`High` are.
   *
   * `backdropToneSizeBias` is the size gate, and it is not decoration: the same
   * backdrop moves a small surface and a large one by very different amounts.
   * Over `dark-solid` the reference's 44 px capsule adapts completely while its
   * 96 px rrect keeps three quarters of its own appearance, measured on both
   * scales independently and agreeing to three decimals. The bias enters the
   * curve's *argument* rather than its amplitude — a thicker surface behaves as
   * though its backdrop were brighter, which is what more material between the
   * viewer and the backdrop means — because an amplitude gate cannot reproduce
   * the second dark backdrop (`impulse`) and this does.
   *
   * The axis is WITHIN a colour scheme. The scheme picks the neutral; this moves
   * the material away from that neutral toward what is actually behind it. So the
   * dark profile runs the same law with the same constants and does not
   * double-adapt: over `dark-solid` its capsule collapses onto the backdrop too,
   * and the light and dark references become the same pixels there.
   */
  readonly backdropToneMax: number;
  readonly backdropToneLow: number;
  readonly backdropToneHigh: number;
  readonly backdropToneSizeBias: number;

  /**
   * **The backdrop tone response (W9)** — the law that owns the interior MEAN,
   * where the four constants above own texture collapse and nothing else.
   *
   * The W9 probe falsified the mix-toward-backdrop form outright (claims
   * §5.33): six cells need mix strengths outside [0, 1], because the
   * reference adapts toward the material's own light/dark appearance, which
   * coincides with the backdrop's tone only over `dark-solid` — the one
   * background the mix was fitted on. What the probe measured instead is a
   * LAW: at equal encoded-space backdrop mean the reference's settled
   * interior is the same number regardless of the backdrop's structure
   * (checker vs text rows, 0.81 both at input 0.69), so the interior level is
   * a function `R(encodedMean, thickness)` and these constants are that
   * function's anchors.
   *
   * `backdropToneAnchorX` is the three solid anchors' encoded-space means —
   * measured backdrop luminances, not tuned. `backdropToneResponseThin` and
   * `...Thick` are the reference's settled interior levels at those anchors
   * for a thin surface (`sizeThickness` 0, the 32 px rrect) and a thick one
   * (saturated, the 96 px+ rrects pooled — their residual spread ±0.012 is
   * the accepted cost of `sizeSpanMax` saturation, claims §5.33). Between
   * the rows: smoothstep in thickness; between the anchors: monotone
   * (Fritsch–Carlson) interpolation in the ENCODED input, the space the
   * probe validated to RMS 0.034 with zero fitting.
   *
   * Below the dark anchor the surface has no data (the probe's grid floor
   * is `dark-solid`), and the one validation cell down there —
   * `impulse__rrect-md`, backdrop 0.0039, reference 0.4358 — reads DARKER
   * than the dark anchor's thick row, so clamping would regress it. The
   * solve's authority fades to zero from the dark anchor downward
   * (smoothstep over the anchor's own lower half, no new constant); the
   * extreme-dark region stays with the collapse constants that were fitted
   * on it.
   */
  readonly backdropToneAnchorX: readonly [number, number, number];
  readonly backdropToneResponseThin: readonly [number, number, number];
  readonly backdropToneResponseThick: readonly [number, number, number];

  /**
   * How much authority the response law has in THIS profile, 0…1 (W9).
   *
   * The anchors above are measurements of the LIGHT reference's settled
   * appearance. The dark scheme's material settles at its own levels over the
   * same backdrops (0.809 light against 0.055 dark over one checkerboard,
   * §5.8), so a dark profile running the light response surface brightens the
   * dark material toward the wrong scheme's appearance — measured on the
   * canonical dark bed as ΔE p95 0.08 → 0.58 before this constant existed.
   * The dark profiles set it to 0: the collapse (whose target is the
   * backdrop, not a scheme's appearance) still runs there, and a dark
   * response surface is follow-up work that needs the dark reference probed,
   * not an assumption.
   */
  readonly backdropToneResponseStrength: number;

  /** The outer shadow (W8) — see `MaterialOuterShadow`. */
  readonly outerShadow: MaterialOuterShadow;

  /**
   * Advisory light direction, in viewport coordinates with y pointing down: a
   * little left of straight overhead, which is where Apple's material reads its
   * specular from.
   */
  readonly lightDirection: readonly [number, number];
  /** Specular sweep band width in radians, and the press glow's reach in CSS px. */
  readonly sweepBandRadians: number;
  readonly glowRadiusCss: number;
  readonly glowGain: number;
  readonly sweepGain: number;
}

/*
 * There is no longer a dark counterpart to this constant. The old
 * `SRGB_DARK_TINT` ([0.09, 0.09, 0.1]) existed only as the light-backdrop end of
 * the adaptive crossover, and C9a measured that the reference does not invert its
 * tint against the backdrop at all — see `adaptiveTintLight` below. The
 * dark-SCHEME tint is a different quantity and lives with the profile that
 * carries it: packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json.
 */
const SRGB_WHITE_TINT: Rgb = [1, 1, 1];

/**
 * How much of the remaining transparency an `occlusion: "increased"` policy
 * closes. **FITTED (round two, 2026-08-31) — 0.4722 → 0.75.**
 *
 * The old number was never a measurement. It was the pre-C9a lift re-expressed as
 * a fraction, (0.62 − 0.28) / (1 − 0.28), chosen so the derivation reproduced the
 * old floor exactly at the old nominal — and no stage of the recalibration
 * cascade had refitted it, which is the gap claims §5.14 records against itself.
 * Against the active bed it under-occluded badly: the reference's interior sits
 * at 0.893 under reduced transparency and 0.957 under increased contrast where
 * vitrea reached 0.777 and 0.783.
 *
 * ## One constant, two references that want different things
 *
 * macOS force-couples the accessibility toggles (Decision Log 8), so BOTH
 * accessibility profiles resolve to `occlusion: "increased"` and both are served
 * by this one number. Fitted on each profile's own untinted calibration cells
 * against the declared objective, they disagree: increased contrast wants 0.80
 * (0.36045 → 0.23366 across the grid, a 1.54× spread) and reduced transparency
 * wants 0.70 (0.10940 → 0.04875, 2.76×). Their implied alphas differ too — 0.945
 * and 0.864 — which is a property of the two references, not of the fit.
 *
 * 0.75 is the minimiser of the two profiles' objectives summed at equal weight,
 * which is the honest tie-break when one constant serves two equally-gated
 * profiles: 0.70 → 0.31022, **0.75 → 0.29742**, 0.80 → 0.30347. Both checks agree
 * (ΔE 0.01087 and 0.00279 at the chosen point) and both profiles improve enormously
 * against the shipped 0.4722, which reads 0.46985 on the same sum.
 *
 * Mirrored by `@vitreajs/vitrea-web`'s `INCREASED_OCCLUSION_LIFT`, and pinned in
 * both directions by `packages/calibration/test/tier-coherence.test.ts`.
 */
export const INCREASED_OCCLUSION_LIFT = 0.75;

/**
 * The occlusion alpha a resolved policy asks for, given whatever nominal the
 * material carries. Mirrors `@vitreajs/vitrea-web`'s `occlusionAlphaUnderPolicy`.
 */
export function occlusionAlphaUnderPolicy(
  nominal: number,
  occlusion: MaterialPolicyView["occlusion"],
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

export const DEFAULT_MATERIAL_PROFILE: MaterialProfile = {
  optics: {
    // σ = 8 for the regular variant, which keeps this package's blur and
    // `platform-web`'s CSS-tier blur on the same number — and makes core's 24 px
    // `samplingPadding` advisory exactly the 3σ S1 measured.
    regular: {
      /*
       * REFITTED (recalibration cascade, 2026-08-31) against the ACTIVE-pose bed.
       * C9a's 0.62 and σ = 8 were fitted against the inactive material and are
       * kept in git history, not here.
       *
       * `blurSigma` 3 is the first value this constant has ever had that the
       * fixtures could identify. §6.1 called it unidentifiable because the
       * inactive reference passed almost no backdrop structure; the active one
       * passes a great deal (interior standard deviation 0.1358 over the
       * checkerboard against vitrea's 0.0176 at σ = 8), so the objective's spread
       * term now bites — it triples from σ = 3 to σ = 6 at a fixed alpha.
       *
       * `tintAlpha` 0.46 is the minimiser over the eight tone-inert untinted rest
       * calibration cells, a genuine interior optimum (0.38 → 0.16945, 0.46 →
       * 0.15704, 0.54 → 0.17248) with ΔE and SSIM agreeing. It remains true that
       * no single value is right for every scene: a lerp toward one tint colour
       * implies an alpha of 0.24 over the checkerboard and 0.47 over the photo at
       * the same 44 px span, which is the lerp-versus-multiply question C9a
       * recorded and nobody has acted on. Claims §5.13.
       */
      blurSigma: 3,
      tint: srgbToLinear(SRGB_WHITE_TINT),
      tintAlpha: 0.46,
      rimWidth: 1.5,
      rimAlpha: 0.18,
      specularPower: 6,
      specularGain: 0.55,
      shadowDepth: 0.35,
      /*
       * REFITTED 0.55 → 0.05 (2026-08-31), and it is the largest single
       * improvement in the cascade: the objective falls 0.14615 → 0.09333 with
       * ΔE and SSIM both improving.
       *
       * The active reference's contour is BRIGHTER than its own body — a rim peak
       * of 0.025…0.129 above baseline, always at one pixel deep. vitrea's read
       * 0.0000 with its peak 8-12 px in, meaning it had no edge feature at all:
       * the inner shadow at 0.55 was darkening the contour faster than the rim lit
       * it. The rim constants themselves did not move; the thing suppressing them
       * did. On the inactive bed the reference's rim was 0.0000…0.0041 and this
       * was invisible, which is what §6.2 recorded as "below quantisation".
       */
      shadowAlpha: 0.05,
      highlight: srgbToLinear(SRGB_WHITE_TINT),
    },
    // Persistently more transparent, so it frosts less and tints less.
    clear: {
      blurSigma: 4,
      tint: srgbToLinear(SRGB_WHITE_TINT),
      tintAlpha: 0.1,
      rimWidth: 1.25,
      rimAlpha: 0.14,
      specularPower: 8,
      specularGain: 0.45,
      shadowDepth: 0.22,
      shadowAlpha: 0.4,
      highlight: srgbToLinear(SRGB_WHITE_TINT),
    },
  },

  /*
   * MEASURED (C9a): both ends are the same tint, which makes the crossover inert
   * by default. That is a finding, not a shortcut.
   *
   * The two ends used to straddle the backdrop — white over a dark backdrop,
   * near-black over a light one — so the material always contrasted with what was
   * behind it. Apple's Regular material does not do that. Its interior rises
   * monotonically with the backdrop across the whole canonical range (0.680 at a
   * backdrop of 0.003, 0.932 at 0.891, light scheme), which is a fixed tint at
   * partial transmission. What it keys on instead is the COLOUR SCHEME: over the
   * same bright checkerboard the reference sits at 0.809 in light and 0.055 in
   * dark. Leaving the inversion on cost more than the whole tint tune was worth —
   * it drove the light-scheme error from 0.348 to 0.449 on the interior-level
   * term alone.
   *
   * So the scheme picks the tint, and the calibration profiles carry one set of
   * numbers per scheme (packages/calibration/profiles/). The crossover mechanism
   * is untouched and still available to a profile that wants it; the default
   * simply no longer claims a behaviour the reference does not have.
   *
   * Two limits worth naming. The ends are global rather than per-variant, so the
   * clear variant inherits this — and clear has no calibration scenes at all, so
   * it is uncalibrated either way. And nothing yet selects a profile from the
   * scheme; that is C9a's parent-impact item.
   */
  adaptiveTintDark: srgbToLinear(SRGB_WHITE_TINT),
  adaptiveTintLight: srgbToLinear(SRGB_WHITE_TINT),
  adaptiveLuminanceLow: 0.12,
  adaptiveLuminanceHigh: 0.42,

  // Authored in `@vitrea/policy` alongside the ladder it is keyed by, because the
  // CSS tier needs the same table and used to hold two more copies of it
  // (Decision Log #23(d)). The profile is still what the shaders read and still
  // what `withMaterialOverrides` replaces — only the *default* literal moved, and
  // it moved unchanged.
  refractionScale: DEFAULT_REFRACTION_SCALE,

  /*
   * MEASURED (W2), against the settled apple-macos-26.5 bed, and set from the
   * REFERENCE's own size-dependence rather than from the objective's minimum.
   *
   * The band was 28…420 while it served the lens alone and nothing had measured
   * it, which put the whole canonical range (32…160 px) inside the first 17% of
   * the curve. What the settled reference actually does, over a fixed checkerboard
   * backdrop: it passes 0.244 of the backdrop's contrast at a 32 px span, 0.230 at
   * 44 px and 0.144 at 96 px. So 6% of the movement happens between 32 and 44 and
   * the rest between 44 and 96, and it is finished by 96 — which is what these two
   * numbers are. `sizeSpanMin` is also the smallest canonical component's span, so
   * that component is the law's exact zero by construction.
   *
   * The tuning objective would rather have 64 (0.1568 against 0.1637 on the rest
   * cells, a 4% win inside a grid that spans 1.07×). Declined, and the reason is
   * recorded rather than the win taken: the gain comes entirely from the interior
   * *level* term, whose residual is the backdrop tone-adaptation gap that wave
   * child W7 is chartered to close — so a band fitted to 64 would be using the
   * size law as a proxy for a mechanism vitrea does not have yet, against the
   * reference's own measurement of where its size-dependence lives, and W7 would
   * have to unpick it. See the claims doc's size-law section.
   */
  sizeSpanMin: 32,
  sizeSpanMax: 96,
  lensSizeGainMax: 2.6,

  /*
   * MEASURED (W2), each with its own status — see the fields' notes.
   *
   * `sizeScatterGainMax` = 1: implemented on both tiers and inert, because the
   * canonical fixtures cannot resolve it. The objective is flat to 1.00× over
   * gains 1…6, and that is not the backdrop chain's depth talking: re-run with the
   * chain deepened (MIN_LEVEL_EXTENT 8 → 4, which lifts the reachable σ on the
   * 320×200 canvas from 1.2× to 2.4×) the grid is still flat to 1.00× and still
   * best at 1. A number the fixtures cannot see is a number that will be met by
   * accident, so this ships at the identity with the mechanism in place.
   *
   * `sizeOcclusionGain` = 0: fitted, and the fit is a boundary optimum with real
   * leverage against it — the objective rises monotonically, 0.168 → 0.224 across
   * 0…0.5, a 1.33× spread. The diagnosis is not a tuning failure: vitrea's
   * interior sits 0.16–0.19 above the reference's at every span because the
   * reference's level is set by backdrop tone adaptation toward roughly 0.63 while
   * vitrea lerps toward a white tint, so making a large surface *more* opaque can
   * only take it further from the reference. The facet is Apple's ("a larger size
   * is more opaque"); the axis that would let it fit is W7's.
   *
   * `sizeShadowGainMax` = 1.4: fitted on the calibration REST cells, where the
   * grid 1.0/1.2/1.4/1.6/1.8/2.2 reads 0.1577/0.1551/0.1533/0.1530/0.1529/0.1531.
   * 1.4 through 2.2 are one flat region (0.25% apart); 1.4 is the point inside it
   * that costs the checks least (ΔE 0.01282 against the baseline's 0.01290, SSIM
   * 0.9671 against 0.9689) and it is the per-cell minimum on both well-conditioned
   * span-96 rest cells. The pressed cells prefer 2.4 monotonically and are
   * excluded from the fit on §6.3's grounds — their native side carries no press
   * pose, so they compare two different states and cannot arbitrate a material
   * constant.
   *
   * ## Re-fitted against the ACTIVE bed (2026-08-31)
   *
   * `sizeScatterGainMax` stays 1 and is now POSITIVELY identified rather than
   * flat: with `blurSigma` refitted to 3 the objective rises 6-7% at gains 2 and
   * 4, so the identity is the optimum instead of a tie.
   *
   * `sizeOcclusionGain` stays 0, a boundary result for the fourth time and for a
   * fourth distinct reason. The reasoning above is retired: the per-cell residual
   * now points the gain's way in every backdrop (web − reference falls with span
   * — checkerboard +0.105/+0.112/+0.046 at 32/44/96 px, photo −0.004/−0.087,
   * light-solid −0.028/+0.001), so the facet finally has the right sign. What it
   * does not have is magnitude: over 0/0.05/0.10/0.15 × spans ending 96/128/160
   * the whole grid is flat to 1.04×, and a 0.2% preference is not evidence. It
   * ships at the identity because the bed cannot identify it, not because the
   * mechanism is wrong.
   *
   * ## Re-fitted against the FROZEN bed (2026-09-01)
   *
   * `sizeOcclusionGain` 0 → **0.05**, and this is the first time the bed could
   * see it. Every earlier fit was a boundary result because calibration held no
   * span above `sizeSpanMax`, so the curve this gain rides was saturated at every
   * cell that could vote. The frozen bed adds three span-128 `rrect-ml`
   * calibration cells, and with them the grid stops being flat: 0.05 is the
   * optimum at **both** backing scales independently — 1× 0.08288 against the
   * identity's 0.08374, 2× 0.09338 against 0.09557 — and ΔE and SSIM move the
   * same way at both.
   *
   * It is still a small number and it is reported as one: a 1.0% preference at
   * 1×, against the 0.2% this doc rightly refused a round ago. What changed is
   * not the margin's size but that it now reproduces on an independent profile
   * instead of resting on one flat grid.
   *
   * `sizeSpanMax` stays 96, and that is now a measurement rather than an
   * assumption. With a span-128 cell voting, the grid rises monotonically —
   * 96/112/128/144/160/192 reading 0.0837/0.0858/0.0943/0.1060/0.1171/0.1300 —
   * so the band's top is where it was, and the suspicion that the bed simply
   * could not see above it is answered rather than inherited.
   *
   * `sizeShadowGainMax` 1.4 → 1. Its evidence dissolved rather than reversing:
   * this is a gain on the INNER SHADOW, and the inner shadow was refitted from
   * `shadowAlpha` 0.55 to 0.05, so there is almost nothing left for it to gain
   * on. The grid 1.0/1.4/2.2 is flat to 0.2%. Carrying a fitted-looking 1.4 whose
   * measurement no longer exists would be the worse of the two errors.
   */
  sizeScatterGainMax: 1,
  sizeOcclusionGain: 0.05,
  sizeShadowGainMax: 1,

  lensBodyLodPerPx: 0.16,
  lensRimLodBias: 2.5,

  reducedTransparencyFrost: 1.75,
  increasedOcclusionLift: INCREASED_OCCLUSION_LIFT,
  strongBorderRim: { rimWidth: 2, rimAlpha: 0.95 },
  reducedTintAdaptation: 0.35,

  // ADVISORY (W3). The span 0.02 … 0.65 covers most of the canonical backdrop
  // range (0.003 … 0.891 linear), and the two ends are deliberately symmetric —
  // 0.45 of the seed's brightness at the dark end, 0.45 of the way to white at
  // the bright end — so the seed itself sits mid-range and the excursion reads
  // as glass rather than as two different colours.
  /*
   * FITTED (2026-08-31, active bed) — and the fit is that THE CURVE IS THE
   * IDENTITY. `floor` → 1 and `ceilMix` → 0 make `tintTone` return the seed
   * unchanged at every backdrop, which leaves `low` and `high` describing
   * nothing at all; they keep their provisional values so a bed that can
   * identify them has somewhere to land, exactly as `adaptiveTint` keeps two
   * equal ends.
   *
   * Monotone and uncontested over floor ∈ {0.45, 0.7, 0.85, 1} × ceilMix ∈
   * {0, 0.2, 0.45}: objective 0.26523 → 0.12676, a 2.09× spread, with ΔE
   * (0.01331 → 0.00831) and SSIM (0.9749 → 0.9788) agreeing. The reference
   * says the same thing directly — on three of the five calibration backdrops
   * its tinted interior is the declared seed EXACTLY in linear light, at a
   * per-channel standard deviation of 0.000. Apple's tint is the author's
   * colour, not a range of tones mapped to it; S219's wording described the
   * inactive material's residue. Claims §5.13.
   */
  tintToneFloor: 1,
  tintToneCeilMix: 0,
  tintToneLow: 0.02,
  tintToneHigh: 0.65,

  /*
   * MEASURED (W7), against the settled apple-macos-26.5 bed, on the light and
   * dark standard profiles jointly and at both scales.
   *
   * The observable these four are set from is the one quantity in this bed that
   * isolates adaptation from everything else: the *separation* between the light
   * and dark references over the same backdrop, on the same component. Under this
   * mechanism that separation is `(1 − tintAlpha)(1 − a)(tintLight − tintDark)`,
   * so the material's transmission, the backdrop's structure and each scheme's
   * own tint all cancel and what is left is `a`. Normalised at the checkerboard,
   * where nothing adapts, it reads:
   *
   *   span 44: 0.000 at backdrop 0.500, 0.030 at 0.205, 1.000 at 0.0117, 1.000 at 0.0049
   *   span 96: 0.000 at backdrop 0.500, 0.028 at 0.216, 0.256 at 0.0117
   *
   * and the 2× bed reproduces every one of those to three decimals (0.2553
   * against 0.2556 on the one that is not a boundary). Two facts follow. The
   * adaptation is off across the whole ordinary range and turns on only below
   * roughly a fifth of the backdrop scale — so it cannot disturb a cell that
   * already passes. And it is size-gated hard: same backdrop, same material, 1.000
   * against 0.256.
   *
   * The band's dark end is not identifiable from this bed and the fit says so:
   * the reference's backdrops jump from 0.0117 to 0.205 with nothing in between,
   * so `backdropToneLow` is bounded only by "at or below the darkest calibration
   * backdrop". What the two dark backdrops DO pin is the curve's slope near zero —
   * the 96 px surface reads 0.256 at 0.0117 and 0.356 at 0.0039, which is a
   * measured intermediate rather than a step, and it is what fixes
   * `backdropToneSizeBias` against `backdropToneHigh`. `impulse__rrect-md__rest`
   * is a VALIDATION cell and was not fitted to: the calibration set predicts
   * 0.34 there and the cell reads 0.356.
   */
  /*
   * RE-SCOPED (W9, claims §5.33). The four mix constants now own TEXTURE
   * COLLAPSE alone — the interior mean moved to the response law below — and
   * their band contracts to the one domain the collapse is real in: full at
   * `dark-solid` (0.0117) for thin surfaces including the 44 px capsule
   * (byte-identical collapse, arg 0.0164 ≤ low with margin), zero by
   * `mid-dark-solid` (0.0595), where the reference's small surface keeps a
   * textured body at 0.4561 and the old band's partial collapse (k = 0.81)
   * was the measured 0.1375-vs-0.4561 overshoot. `impulse__rrect-md`
   * (arg 0.0539) keeps k ≈ 0.003 against the old band's 0.008 — the same
   * unadapted render that cell validated.
   */
  backdropToneMax: 1,
  backdropToneLow: 0.02,
  backdropToneHigh: 0.055,
  /*
   * REFITTED 0.09 → 0.13 (2026-08-31, active bed). The law's SHAPE is untouched
   * (Decision Log 13 stands; the two-axis rework is next wave) and `max`, `low`
   * and `high` are unmoved — only the size gate widened.
   *
   * What it changes is one cell: a 96 pt surface over the darkest backdrop now
   * barely adapts, where at 0.09 it adapted by a quarter. Two independent reads
   * of the reference disagreed about that and the validation set broke the tie.
   * The light-versus-dark separation estimator §5.8 fitted on says the 96 pt
   * surface adapts by 0.30; the reference's own interior LEVEL says it does not
   * (0.4844, against 0.466 for an unadapted surface at the refitted tint alpha
   * and 0.3566 for an adapted one). Measured once on
   * `impulse__rrect-md__rest`, which is validation and was fitted to by
   * neither: 0.09 renders 0.2858 against a reference of 0.4358 at ΔE 0.02344;
   * 0.13 renders 0.4594 at ΔE 0.00378, six times better. The separation
   * estimator's algebra assumes the two colour schemes share one tint alpha,
   * and this profile pair does not (0.46 against 0.97) — recorded in §5.13 as
   * the reason it is no longer the primary evidence for this constant.
   *
   * RE-SCOPED 0.13 → 0.05 with the band above (W9): the bias's one remaining
   * job is keeping the thick surface's collapse argument above `high` at the
   * dark anchor (0.0117 + 0.05 = 0.0617 > 0.055) while the thin capsule's
   * stays below `low` — the near-binary size snap the probe measured
   * (claims §5.33). The smooth size trend on structured backdrops, which the
   * old wide band tried and failed to carry, belongs to the response law's
   * thickness axis now.
   */
  backdropToneSizeBias: 0.05,

  /*
   * MEASURED (W9 probe, claims §5.30–§5.33): the anchors are the probe bed's
   * settled reference levels, frequency-settled over seven attested runs,
   * under the probe's own native-mask interior. Thick rows pool the 96 px
   * and 160 px rrects (±0.012). Not tuned; re-measured only by a new probe.
   */
  backdropToneAnchorX: [0.1104, 0.2706, 0.9505],
  backdropToneResponseThin: [0.0126, 0.4561, 0.9713],
  backdropToneResponseThick: [0.4953, 0.5744, 0.9358],
  backdropToneResponseStrength: 1,

  /*
   * FITTED (recalibration cascade, 2026-08-31). W8's geometry SURVIVES the fit
   * unchanged — `sigmaPx` 15.55, `offsetPx` 7.95, `spreadPx` 3.10 — and only the
   * two amplitudes moved: `occlusion` 0.33 → 0.285 and
   * `reducedTransparencyOcclusion` 0.566 → 0.70. The dark scheme's amplitude
   * (0.09) lands as a profile patch, not as a branch here.
   *
   * The fit is `scripts/sweep.ts --objective shadow`, whose term is the mean over
   * calibration cells of |Δ meanDeparture| — the light each side removes from the
   * whole exterior, in linear light, which is the one commensurate quantity the
   * facet has. The amplitude is a genuine interior optimum over 0.18…0.44 (a
   * 2.23× spread) and flat to 1.04% across 0.255…0.315, which is exactly the
   * scene-to-scene amplitude spread the reference itself shows. The geometry is
   * NOT identifiable against this objective — σ ∈ {13.5, 15.55, 17.5} × offset ∈
   * {6.5, 7.95, 9.4} spans 1.04× with 15.55 the argmin — because an integral over
   * the exterior is insensitive to how the darkening is distributed within it.
   * W8's own two-dimensional fit against the occlusion field measures the
   * geometry far more powerfully (RMS 0.0021 over 142,550 pixels), and the
   * instrument's independent shadow axis agrees, so the geometry stands on those
   * two and this objective is not asked to re-decide it.
   *
   * `reducedTransparencyOcclusion` 0.70 is sharp where the amplitude is flat: a
   * 3.83× spread over 0.45…0.95 with a clear minimum. It also reconciles two
   * routes — 0.285 × 0.70 = 0.1995 against the reference's directly measured
   * reduce-transparency amplitude of 0.203 at a 44 px span. W8's 0.566 was the
   * ratio of the reference's two amplitudes; this is the ratio that makes
   * vitrea's shadow match the reference's under the preference, and the two
   * differ because the base amplitude is a compromise across scenes whose spread
   * is much wider in the standard profile than under reduced transparency.
   *
   * Extracted from the active bed's native fixtures directly —
   * `results/2026-08-31-active-bed-stage0.json` measured the gap, these numbers
   * measure the facet — and left provisional deliberately: X1 gives the fit to
   * the recalibration cascade, which owns the holdout discipline. This child owns
   * the mechanism.
   *
   * Method: for each `rest` fixture, the occlusion field `1 − L_capture/L_background`
   * in linear Rec.709 luminance, over every pixel outside the declared component
   * geometry with a backdrop bright enough to carry a signal; fitted in two
   * dimensions against `occlusion · Φ(−sd/σ)`, where `sd` is the signed distance
   * to the component's own rounded silhouette translated down by `offsetPx` and
   * outset by `spreadPx`.
   *
   * The fit and its residual, on `1x-light-standard` and `2x-light-standard`:
   *
   *   backdrop      span   occlusion   σ (1×/2×)   offset (1×/2×)   RMS
   *   photo           44     0.323     15.5/31.1     7.9/15.8     0.0021
   *   checkerboard    44     0.338     15.7/31.0     8.0/15.9     0.0016
   *   hc-text         44     0.339     15.7/31.1     8.0/15.9     0.0014
   *   photo           32     0.321     15.5/30.9     8.1/16.2     0.0018
   *   mid-dark-solid  44     0.310        —            —          0.0079
   *
   * — against a peak occlusion of 0.24, so the model carries the facet to under
   * 1% of its own amplitude, over up to 142,550 pixels per cell. The three
   * lengths are the consensus across every well-conditioned cell; `occlusion` is
   * the light-standard amplitude at a span the size law leaves alone.
   *
   * What the amplitude does NOT yet have is a mechanism for its scene-to-scene
   * spread. Over the flat near-white `light-solid` backdrop the same fit reads
   * 0.123 rather than 0.33, reproducibly and at both scales, while the other flat
   * backdrop (`mid-dark-solid`, linear 0.0595) reads 0.310 — so it is not a
   * function of the backdrop's luminance, its structure, or the material's
   * interior level, and no compositing model in either colour space produces both.
   * The dark-scheme profile is a separate amplitude entirely (0.046…0.061 at a
   * 44 px span — the dark material's shadow is nearly invisible) and lands as a
   * profile patch, not as a branch here. Both are stated in the claims doc as the
   * open question the cascade's fit inherits.
   */
  outerShadow: {
    offsetPx: 7.95,
    sigmaPx: 15.55,
    spreadPx: 3.1,
    occlusion: 0.285,
    reducedTransparencyOcclusion: 0.7,
    sizeGain: 0,
  },

  lightDirection: [-0.3714, -0.9285],
  sweepBandRadians: 0.55,
  glowRadiusCss: 44,
  glowGain: 0.6,
  sweepGain: 0.85,
};

// The default profile's numbers, under the names the rest of the package and its
// tests already know them by. Derived rather than duplicated: a re-tuned default
// moves both at once, and there is no second place for the two to disagree.
export const REFRACTION_SCALE = DEFAULT_MATERIAL_PROFILE.refractionScale;
export const MATERIAL_OPTICS = DEFAULT_MATERIAL_PROFILE.optics;
export const ADAPTIVE_TINT_DARK = DEFAULT_MATERIAL_PROFILE.adaptiveTintDark;
export const ADAPTIVE_TINT_LIGHT = DEFAULT_MATERIAL_PROFILE.adaptiveTintLight;
export const ADAPTIVE_LUMINANCE_LOW = DEFAULT_MATERIAL_PROFILE.adaptiveLuminanceLow;
export const ADAPTIVE_LUMINANCE_HIGH = DEFAULT_MATERIAL_PROFILE.adaptiveLuminanceHigh;
export const SIZE_SPAN_MIN = DEFAULT_MATERIAL_PROFILE.sizeSpanMin;
export const SIZE_SPAN_MAX = DEFAULT_MATERIAL_PROFILE.sizeSpanMax;
export const LENS_SIZE_GAIN_MAX = DEFAULT_MATERIAL_PROFILE.lensSizeGainMax;
export const SIZE_SCATTER_GAIN_MAX = DEFAULT_MATERIAL_PROFILE.sizeScatterGainMax;
export const SIZE_OCCLUSION_GAIN = DEFAULT_MATERIAL_PROFILE.sizeOcclusionGain;
export const SIZE_SHADOW_GAIN_MAX = DEFAULT_MATERIAL_PROFILE.sizeShadowGainMax;
export const LENS_BODY_LOD_PER_PX = DEFAULT_MATERIAL_PROFILE.lensBodyLodPerPx;
export const LENS_RIM_LOD_BIAS = DEFAULT_MATERIAL_PROFILE.lensRimLodBias;
export const BACKDROP_TONE_MAX = DEFAULT_MATERIAL_PROFILE.backdropToneMax;
export const BACKDROP_TONE_LOW = DEFAULT_MATERIAL_PROFILE.backdropToneLow;
export const BACKDROP_TONE_HIGH = DEFAULT_MATERIAL_PROFILE.backdropToneHigh;
export const BACKDROP_TONE_SIZE_BIAS = DEFAULT_MATERIAL_PROFILE.backdropToneSizeBias;
export const BACKDROP_TONE_ANCHOR_X = DEFAULT_MATERIAL_PROFILE.backdropToneAnchorX;
export const BACKDROP_TONE_RESPONSE_THIN = DEFAULT_MATERIAL_PROFILE.backdropToneResponseThin;
export const BACKDROP_TONE_RESPONSE_THICK = DEFAULT_MATERIAL_PROFILE.backdropToneResponseThick;
export const BACKDROP_TONE_RESPONSE_STRENGTH =
  DEFAULT_MATERIAL_PROFILE.backdropToneResponseStrength;
export const OUTER_SHADOW = DEFAULT_MATERIAL_PROFILE.outerShadow;

/**
 * A profile patch: any subset, to any depth, of what a profile holds.
 *
 * A colour is one leaf, not three: patching a tint means naming the whole triple,
 * because two channels of a fitted colour and one of the default is not a colour
 * anybody measured.
 */
export interface MaterialProfilePatch {
  readonly optics?: Readonly<Partial<Record<MaterialVariant, Readonly<Partial<MaterialOptics>>>>>;
  readonly adaptiveTintDark?: Rgb;
  readonly adaptiveTintLight?: Rgb;
  readonly adaptiveLuminanceLow?: number;
  readonly adaptiveLuminanceHigh?: number;
  readonly refractionScale?: Readonly<Partial<Record<RefractionQuality, number>>>;
  readonly sizeSpanMin?: number;
  readonly sizeSpanMax?: number;
  readonly lensSizeGainMax?: number;
  readonly sizeScatterGainMax?: number;
  readonly sizeOcclusionGain?: number;
  readonly sizeShadowGainMax?: number;
  readonly lensBodyLodPerPx?: number;
  readonly lensRimLodBias?: number;
  readonly reducedTransparencyFrost?: number;
  readonly increasedOcclusionLift?: number;
  readonly strongBorderRim?: Readonly<Partial<MaterialRim>>;
  readonly reducedTintAdaptation?: number;
  readonly tintToneFloor?: number;
  readonly tintToneCeilMix?: number;
  readonly tintToneLow?: number;
  readonly tintToneHigh?: number;
  readonly backdropToneMax?: number;
  readonly backdropToneLow?: number;
  readonly backdropToneHigh?: number;
  readonly backdropToneSizeBias?: number;
  readonly backdropToneAnchorX?: readonly [number, number, number];
  readonly backdropToneResponseThin?: readonly [number, number, number];
  readonly backdropToneResponseThick?: readonly [number, number, number];
  readonly backdropToneResponseStrength?: number;
  readonly outerShadow?: Readonly<Partial<MaterialOuterShadow>>;
  readonly lightDirection?: readonly [number, number];
  readonly sweepBandRadians?: number;
  readonly glowRadiusCss?: number;
  readonly glowGain?: number;
  readonly sweepGain?: number;
}

/**
 * Apply a patch. This is how a calibration profile lands: C7 emits the measured
 * numbers, the host passes them here, and every constant above is replaceable
 * without touching this file.
 *
 * The nested records merge per field and per rung, so a patch naming one tint
 * alpha keeps that variant's blur, rim and specular rather than dropping them.
 */
export function withMaterialOverrides(
  base: MaterialProfile,
  patch: MaterialProfilePatch,
): MaterialProfile {
  const optics = {} as Record<MaterialVariant, MaterialOptics>;
  for (const variant of MATERIAL_VARIANTS) {
    optics[variant] = { ...base.optics[variant], ...patch.optics?.[variant] };
  }

  const refractionScale = {} as Record<RefractionQuality, number>;
  for (const rung of REFRACTION_LADDER) {
    refractionScale[rung] = patch.refractionScale?.[rung] ?? base.refractionScale[rung];
  }

  return {
    optics,
    adaptiveTintDark: patch.adaptiveTintDark ?? base.adaptiveTintDark,
    adaptiveTintLight: patch.adaptiveTintLight ?? base.adaptiveTintLight,
    adaptiveLuminanceLow: patch.adaptiveLuminanceLow ?? base.adaptiveLuminanceLow,
    adaptiveLuminanceHigh: patch.adaptiveLuminanceHigh ?? base.adaptiveLuminanceHigh,
    refractionScale,
    sizeSpanMin: patch.sizeSpanMin ?? base.sizeSpanMin,
    sizeSpanMax: patch.sizeSpanMax ?? base.sizeSpanMax,
    lensSizeGainMax: patch.lensSizeGainMax ?? base.lensSizeGainMax,
    sizeScatterGainMax: patch.sizeScatterGainMax ?? base.sizeScatterGainMax,
    sizeOcclusionGain: patch.sizeOcclusionGain ?? base.sizeOcclusionGain,
    sizeShadowGainMax: patch.sizeShadowGainMax ?? base.sizeShadowGainMax,
    lensBodyLodPerPx: patch.lensBodyLodPerPx ?? base.lensBodyLodPerPx,
    lensRimLodBias: patch.lensRimLodBias ?? base.lensRimLodBias,
    reducedTransparencyFrost: patch.reducedTransparencyFrost ?? base.reducedTransparencyFrost,
    increasedOcclusionLift: patch.increasedOcclusionLift ?? base.increasedOcclusionLift,
    strongBorderRim: { ...base.strongBorderRim, ...patch.strongBorderRim },
    reducedTintAdaptation: patch.reducedTintAdaptation ?? base.reducedTintAdaptation,
    tintToneFloor: patch.tintToneFloor ?? base.tintToneFloor,
    tintToneCeilMix: patch.tintToneCeilMix ?? base.tintToneCeilMix,
    tintToneLow: patch.tintToneLow ?? base.tintToneLow,
    tintToneHigh: patch.tintToneHigh ?? base.tintToneHigh,
    backdropToneMax: patch.backdropToneMax ?? base.backdropToneMax,
    backdropToneLow: patch.backdropToneLow ?? base.backdropToneLow,
    backdropToneHigh: patch.backdropToneHigh ?? base.backdropToneHigh,
    backdropToneSizeBias: patch.backdropToneSizeBias ?? base.backdropToneSizeBias,
    backdropToneAnchorX: patch.backdropToneAnchorX ?? base.backdropToneAnchorX,
    backdropToneResponseThin: patch.backdropToneResponseThin ?? base.backdropToneResponseThin,
    backdropToneResponseThick: patch.backdropToneResponseThick ?? base.backdropToneResponseThick,
    backdropToneResponseStrength:
      patch.backdropToneResponseStrength ?? base.backdropToneResponseStrength,
    outerShadow: { ...base.outerShadow, ...patch.outerShadow },
    lightDirection: patch.lightDirection ?? base.lightDirection,
    sweepBandRadians: patch.sweepBandRadians ?? base.sweepBandRadians,
    glowRadiusCss: patch.glowRadiusCss ?? base.glowRadiusCss,
    glowGain: patch.glowGain ?? base.glowGain,
    sweepGain: patch.sweepGain ?? base.sweepGain,
  };
}

/**
 * Fold core's resolved material *regime* onto this package's numbers.
 *
 * core decides which regime applies and nothing here re-decides it. One branch
 * per axis of `MaterialPolicyView`, so a new axis in core surfaces as a missing
 * branch here rather than as silence.
 */
export function opticsUnderPolicy(
  optics: MaterialOptics,
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): MaterialOptics {
  let next = optics;

  if (policy.frost === "increased") {
    next = { ...next, blurSigma: next.blurSigma * profile.reducedTransparencyFrost };
  } else if (policy.frost === "none") {
    next = { ...next, blurSigma: 0 };
  }

  next = {
    ...next,
    tintAlpha: occlusionAlphaUnderPolicy(
      next.tintAlpha,
      policy.occlusion,
      profile.increasedOcclusionLift,
    ),
  };

  if (policy.border === "strong") next = { ...next, ...profile.strongBorderRim };

  return next;
}

/** How much of the analysis-driven tint is applied, under the contrast regime. */
export function adaptationStrength(
  policy: MaterialPolicyView,
  analysisExact: boolean,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  if (!analysisExact) return 0;
  switch (policy.ambientTint) {
    case "nominal":
      return 1;
    case "reduced":
      return profile.reducedTintAdaptation;
    case "none":
      return 0;
  }
}

/**
 * How much of the tint's tone excursion survives the contrast regime.
 *
 * The tone map is the tinted material's response to what is behind it, so it
 * rides the axis that already governs exactly that — `ambientTint` — rather
 * than inventing a second one. Under increased contrast the range narrows
 * toward the bare seed, which is the direction W1 measured Apple's own
 * accessibility material moving (its interior "has all but stopped
 * transmitting the backdrop"); under forced colours there is no material to
 * tint at all and the caller never reaches here.
 *
 * The author's colour is never changed by a policy. Only how far the material
 * is allowed to move it is.
 */
export function tintToneAdaptation(
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  switch (policy.ambientTint) {
    case "nominal":
      return 1;
    case "reduced":
      return profile.reducedTintAdaptation;
    case "none":
      return 0;
  }
}

/**
 * The tone the seed shows over a given backdrop, in linear light — the CPU
 * statement of what `WGSL_OPTICS_PASS` evaluates per pixel.
 *
 * Exported because two other things have to agree with the shader without being
 * it: the CSS tier converts this quantity into one flat `rgba()`, and the
 * foreground decision has to be taken against the material the surface actually
 * shows. A second implementation of the curve is how those two drift, so there
 * is one, here, and the shader mirrors it line for line.
 */
export function tintTone(
  seed: Rgb,
  backdropLuminance: number,
  toneAdaptation: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): Rgb {
  const t = smoothstep(profile.tintToneLow, profile.tintToneHigh, backdropLuminance);
  const k = Math.min(1, Math.max(0, toneAdaptation));
  const channel = (index: 0 | 1 | 2): number => {
    const s = seed[index];
    const low = s * profile.tintToneFloor;
    const high = s + (1 - s) * profile.tintToneCeilMix;
    return s + (low + (high - low) * t - s) * k;
  };
  return [channel(0), channel(1), channel(2)];
}

/**
 * The material's tint colour once an author tint is folded onto the neutral one.
 *
 * `neutral` is what the material would tint with on its own — the profile's
 * tint, already crossed with whatever adaptation the renderer resolved. The
 * author's tone displaces it by `strength` and nothing else: the tint alpha,
 * which is the material's occlusion and the axis every accessibility policy and
 * the system's own Clear/Tinted preference operate on, is untouched here by
 * construction.
 */
export function tintedTintColour(
  neutral: Rgb,
  tint: { readonly color: Rgb; readonly strength: number } | undefined,
  backdropLuminance: number,
  toneAdaptation: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): Rgb {
  if (tint === undefined) return neutral;
  const tone = tintTone(tint.color, backdropLuminance, toneAdaptation, profile);
  const k = Math.min(1, Math.max(0, tint.strength));
  return [
    neutral[0] + (tone[0] - neutral[0]) * k,
    neutral[1] + (tone[1] - neutral[1]) * k,
    neutral[2] + (tone[2] - neutral[2]) * k,
  ];
}

/**
 * **Backdrop tone adaptation, the curve** — how far this surface's tint is pulled
 * onto the backdrop it is looking at, 0…1, before any accessibility fold.
 *
 * `thickness` is the size law's own factor (`sizeThickness`), and it enters the
 * curve's argument rather than scaling its result: a thicker surface reads its
 * backdrop as brighter than it is, so it holds its own appearance longer. See
 * `MaterialProfile.backdropToneSizeBias` for the measurement that shape came from.
 *
 * Exported for the same reason `tintTone` is: the CSS tier evaluates it at one
 * backdrop level, the foreground decision has to be taken against the material the
 * surface actually shows, and `WGSL_OPTICS_PASS` mirrors it per pixel. One curve,
 * three consumers, no second implementation.
 */
export function backdropToneAdaptation(
  backdropLuminance: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const x = backdropLuminance + profile.backdropToneSizeBias * Math.min(1, Math.max(0, thickness));
  const span = Math.max(profile.backdropToneHigh - profile.backdropToneLow, 1e-6);
  const t = Math.min(1, Math.max(0, (x - profile.backdropToneLow) / span));
  return Math.min(1, Math.max(0, profile.backdropToneMax)) * (1 - t * t * (3 - 2 * t));
}

/**
 * How much of the backdrop adaptation survives an accessibility regime.
 *
 * Two folds, each with its own reason, and the product is what the material gets.
 *
 * `ambientTint` is the axis the wave's composition contract names for "how far
 * the material may move its colour", and it is what carries increased contrast
 * (narrowed toward the scheme's own neutral) and forced colours (no material to
 * adapt — the optics pass stands down before it reaches here).
 *
 * The refraction ladder read at the **accessibility cap** carries reduced
 * transparency, which touches no tint axis at all and would otherwise get the
 * adaptation at full strength — and adaptation at full strength dissolves the
 * surface into its backdrop, which is precisely the occlusion that preference
 * asked to be *raised*. A policy has to win against a material law, so it does.
 * The same cap, for the same reason, that `sizeThicknessUnderPolicy` reads.
 *
 * Deliberately unmeasured rather than fitted: neither accessibility profile's
 * scene set contains a backdrop dark enough for this axis to act on, so the fold
 * is a statement about which way to be wrong, not a number the bed chose. It is
 * named in the claims doc with the capture that would close it.
 */
export function backdropToneUnderPolicy(
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return tintToneAdaptation(policy, profile) * profile.refractionScale[accessibilityRefractionCap(policy)];
}

/**
 * The size bias to hand a consumer that will multiply it by a **policy-folded**
 * thickness (`sizeThicknessUnderPolicy`) — the shader and the CSS tier both do.
 *
 * The gate is geometric: it says how much material stands between the viewer and
 * the backdrop, which no preference changes. But there is one thickness in the
 * pipeline and it is the folded one (it rides `aux.z` through the field pass's
 * union, and widening `aux` for a second copy of the same quantity would be a
 * per-pixel channel spent on arithmetic). Dividing the bias by the same cap
 * restores the geometric product exactly: `bias' * thickness_folded ===
 * bias * thickness_raw`, pinned as a test rather than promised here.
 *
 * At `cap = none` the fold above is already 0, so the adaptation is off and the
 * bias is not read; 0 is returned rather than an infinity.
 */
export function backdropToneSizeBiasUnderPolicy(
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const cap = profile.refractionScale[accessibilityRefractionCap(policy)];
  return cap <= 0 ? 0 : profile.backdropToneSizeBias / cap;
}

/**
 * The neutral tint after the backdrop has had its say — step two of the wave's
 * composition contract (colour scheme → **backdrop adaptation** → author tint).
 *
 * `backdrop` is the **averaged** light the surface's body transmits, not one
 * pixel's lens-displaced sample: a fully adapted material shows its backdrop's
 * tone, and a tone is a mean. Over a flat backdrop the two are the same value and
 * the surface disappears into it exactly, which is what the reference's capsule
 * over `dark-solid` does — byte-identical to its own background.
 */
export function adaptedTintColour(
  neutral: Rgb,
  backdrop: Rgb,
  adaptation: number,
  tintAlpha: number,
): Rgb {
  const k = Math.min(1, Math.max(0, adaptation));
  if (k === 0) return neutral;
  // The pair (colour, alpha) that makes the interior composite CONVERGE on the
  // backdrop's tone: mix(mix(b, T, α), M, k) === mix(b, T', α') exactly, with α'
  // from `adaptedTintAlpha`. Solving it here rather than lerping the two
  // parameters separately is the difference between an adaptation and a
  // brightening — a lerped alpha over a still-mostly-neutral tint makes a
  // partially adapted surface *lighter* than the one it started from, which the
  // 96 px cells caught immediately (interior 0.4545 → 0.5179 against a reference
  // of 0.4542).
  const alpha = adaptedTintAlpha(tintAlpha, k);
  if (alpha <= 0) return neutral;
  const wNeutral = (1 - k) * tintAlpha;
  return [
    (neutral[0] * wNeutral + backdrop[0] * k) / alpha,
    (neutral[1] * wNeutral + backdrop[1] * k) / alpha,
    (neutral[2] * wNeutral + backdrop[2] * k) / alpha,
  ];
}

/**
 * The material's occlusion once the backdrop has had its say — the second half of
 * the adaptation, and the half a cross-tier measurement forced.
 *
 * An adapting material does not merely take its backdrop's colour, it stops
 * transmitting: the settled reference's capsule over the `impulse` backdrop is a
 * flat body at its backdrop's own mean, with the impulse grid *hidden* behind it
 * (interior standard deviation 0.0008 against the backdrop's 0.056), not a
 * transparent pane showing it through.
 *
 * Adapting the colour alone made the material fully transparent at full strength,
 * and that is where the two tiers part company: this one blurs its backdrop in
 * linear light and the CSS tier's `backdrop-filter` blurs in the encoded space, so
 * over a high-dynamic-range backdrop a transparent material renders *different
 * pixels* on the two tiers by construction. Measured on that cell, GPU over CSS
 * interior ratio 23.5 against a gated band of 0.80…1.25 — a hard failure of the
 * cross-tier bound, and the reason this exists. A material that shows its
 * backdrop's mean is a colour, and a colour is tier-independent.
 *
 * The same "fraction of what is left" shape as `increasedOcclusionLift`, and for
 * the same reason: it lifts strictly for every nominal below 1, whatever a later
 * tuning pass moves nominal to.
 *
 * This is the one place a colour axis reaches the alpha, and it is not an
 * exception to the composition contract's rule that an author's tint may not:
 * that rule is about an *author's* choice not moving the material's occlusion.
 * This is the material's own response to its surroundings, which is what the
 * occlusion axis is for.
 */
export function adaptedTintAlpha(tintAlpha: number, adaptation: number): number {
  const k = Math.min(1, Math.max(0, adaptation));
  return tintAlpha + k * (1 - tintAlpha);
}

const smoothstep = (edge0: number, edge1: number, x: number): number => {
  if (edge1 <= edge0) return x < edge0 ? 0 : 1;
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
};

/**
 * **The size law's one input**: how thick a surface of this span reads, 0…1.
 *
 * Every thickness-derived facet is a gain on this number and on nothing else —
 * see `MaterialProfile.sizeSpanMin`. Exactly 0 at or below `sizeSpanMin`, so the
 * whole law is inert on a small control, and exactly 1 at or above `sizeSpanMax`,
 * so nothing keeps growing off the end of the canonical range.
 *
 * Mirrored by `@vitreajs/vitrea-web`'s `sizeThickness`, pinned in both directions
 * by `packages/calibration/test/tier-coherence.test.ts`.
 */
export function sizeThickness(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return smoothstep(profile.sizeSpanMin, profile.sizeSpanMax, spanPx);
}

/**
 * The backdrop tone response `R(encodedInput, thickness)` (W9) — the settled
 * interior level the reference shows over a backdrop whose ENCODED-space mean
 * is `encodedInput`, for a surface of the given (unfolded) thickness. See
 * `MaterialProfile.backdropToneAnchorX` for what the anchors are and where the
 * law's authority ends.
 *
 * Monotone (Fritsch–Carlson) interpolation through the three anchors, clamped
 * to their span; smoothstep between the thin and thick rows. Mirrored by
 * `@vitreajs/vitrea-web` and by the optics shader, pinned by
 * `tier-coherence.test.ts`.
 */
export function backdropToneResponse(
  encodedInput: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const xs = profile.backdropToneAnchorX;
  const f = smoothstep(0, 1, thickness);
  const ys = [0, 1, 2].map(
    (i) =>
      (profile.backdropToneResponseThin[i] ?? 0) +
      ((profile.backdropToneResponseThick[i] ?? 0) - (profile.backdropToneResponseThin[i] ?? 0)) *
        f,
  ) as [number, number, number];

  const x = Math.min(xs[2], Math.max(xs[0], encodedInput));
  const h0 = xs[1] - xs[0];
  const h1 = xs[2] - xs[1];
  const d0 = (ys[1] - ys[0]) / h0;
  const d1 = (ys[2] - ys[1]) / h1;
  // Interior slope: the Fritsch–Carlson harmonic mean, 0 across a sign change,
  // which is what keeps the curve monotone between monotone anchors.
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
 * How much authority the response law has at this input, 0…1 (W9).
 *
 * Full on its measured domain (the dark anchor upward), fading to zero over
 * the dark anchor's own lower half — below it the only evidence is
 * `impulse__rrect-md`, which the collapse constants were fitted on and the
 * response surface would contradict. Derived from the anchor, not a constant.
 */
export function backdropToneSolveWeight(
  encodedInput: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const anchor = profile.backdropToneAnchorX[0];
  return smoothstep(anchor * 0.5, anchor, encodedInput);
}

/**
 * The size law under an accessibility regime — the fold every other optic gets,
 * and the law does not get to skip it.
 *
 * **MEASURED (W2), and it was measured the hard way.** The law was first landed
 * unfolded, and the regeneration caught it: under both accessibility profiles the
 * large-span cells' ΔE p95 rose past their adopted bounds while every
 * light-standard cell improved. The reason is legible in the reference. Under
 * reduce-transparency Apple's material is nearly opaque and its interior level is
 * *flat* in span (0.9465 at a 44 px span, 0.9526 at 96), where in the standard
 * profile it is not — so a size term that deepens the material's own shadow is
 * modelling something the accessibility reference does not do, and vitrea's
 * accessibility fold already under-occludes against it (W1's Surprise), so the
 * extra depth compounds an error instead of closing one.
 *
 * The scale is the profile's own refraction ladder rather than a new constant,
 * read at the **accessibility** cap alone: 1 nominal, 0.45 reduced, 0 none. That
 * is the number that already means "how much depth this preference allows", and
 * the law is nothing but a depth simulation. Deliberately not the *resolved* cap,
 * which also carries the group's sampling capability — a group demoted to a CSS
 * proxy should still look as thick as it is, because being demoted is not a
 * statement about the material.
 *
 * One consequence, stated rather than hidden: the lens displacement is scaled by
 * `refractionScale` again in the shader, so under a reduced regime the size
 * gain's contribution to it is scaled twice. That is the safe direction — a
 * preference asking for less refraction gets less — and the base thickness, which
 * is most of the depth, is scaled exactly once.
 */
export function sizeThicknessUnderPolicy(
  spanPx: number,
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return (
    sizeThickness(spanPx, profile) * profile.refractionScale[accessibilityRefractionCap(policy)]
  );
}

/** The lens's size gain — see `MaterialProfile.lensSizeGainMax`. */
export function lensSizeGain(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return 1 + (profile.lensSizeGainMax - 1) * sizeThickness(spanPx, profile);
}

/** `lensSizeGain` for a surface whose thickness factor the policy has already folded. */
export function lensSizeGainFromThickness(
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return 1 + (profile.lensSizeGainMax - 1) * thickness;
}

/**
 * The body blur σ a surface of this span actually runs at — the scattering facet.
 *
 * One function for both tiers, which is what stops them scattering differently:
 * `platform-web` calls its mirror of this to write `blur()`, and this package
 * calls it to derive the chain level the optics pass lerps its body sample
 * toward. It is also what a group's `samplingPadding` floor must be taken over —
 * a wider blur needs a wider proxy, and the group's floor is set by its *largest*
 * member (S1's 3σ rule, applied to the σ the material will really use).
 */
export function sizeScatterSigma(
  sigmaPx: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return sizeScatterSigmaAt(sigmaPx, sizeThickness(spanPx, profile), profile);
}

/**
 * The same, for a caller that has already resolved the thickness factor — which
 * is every caller with a policy to fold under.
 *
 * The two-function shape is deliberate and it is mirrored on the CSS tier: the
 * thickness form is the law, the span form is the convenience that computes an
 * unfolded thickness for it. One formula, so a policy fold cannot end up applied
 * to one facet and not another.
 */
export function sizeScatterSigmaAt(
  sigmaPx: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return sigmaPx * (1 + (profile.sizeScatterGainMax - 1) * thickness);
}

/**
 * The occlusion alpha a surface of this span carries — the opacity facet.
 *
 * Composes with `occlusionAlphaUnderPolicy` rather than replacing it: both close
 * a fraction of whatever transparency is left, so the order they are applied in
 * changes the result by less than either term and neither can cancel the other.
 * The accessibility policy is applied first, because a preference outranks a
 * material law.
 */
export function sizeOcclusionAlpha(
  alpha: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return sizeOcclusionAlphaAt(alpha, sizeThickness(spanPx, profile), profile);
}

/** The same, for a caller that has already resolved the thickness factor. */
export function sizeOcclusionAlphaAt(
  alpha: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return Math.min(1, alpha + profile.sizeOcclusionGain * thickness * (1 - alpha));
}

/** The inner shadow's depth at this span — see `MaterialProfile.sizeShadowGainMax`. */
export function sizeShadowDepth(
  shadowDepth: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return sizeShadowDepthAt(shadowDepth, sizeThickness(spanPx, profile), profile);
}

/** The same, for a caller that has already resolved the thickness factor. */
export function sizeShadowDepthAt(
  shadowDepth: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return shadowDepth * (1 + (profile.sizeShadowGainMax - 1) * thickness);
}

/**
 * The outer shadow's peak occlusion at this span — see
 * `MaterialOuterShadow.sizeGain`. At the shipped gain of 0 this is the identity,
 * exactly, which is the point.
 */
export function sizeOuterShadowOcclusion(
  occlusion: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return sizeOuterShadowOcclusionAt(occlusion, sizeThickness(spanPx, profile), profile);
}

/** The same, for a caller that has already resolved the thickness factor. */
export function sizeOuterShadowOcclusionAt(
  occlusion: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return Math.min(1, occlusion + profile.outerShadow.sizeGain * thickness * (1 - occlusion));
}

/**
 * The outer shadow under an accessibility regime.
 *
 * One branch per axis that can reach it, on `opticsUnderPolicy`'s rule. `frost`
 * is the axis reduced transparency alone sets, and the amplitude it multiplies by
 * is measured — see `MaterialOuterShadow.reducedTransparencyOcclusion`. Under
 * forced colours the material is gone, so its shadow goes with it rather than
 * outliving the surface that cast it.
 */
export function outerShadowUnderPolicy(
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): MaterialOuterShadow {
  const shadow = profile.outerShadow;
  if (policy.glass === "none" || policy.frost === "none") return { ...shadow, occlusion: 0 };
  if (policy.frost === "increased") {
    return { ...shadow, occlusion: shadow.occlusion * shadow.reducedTransparencyOcclusion };
  }
  return shadow;
}

/**
 * The Gaussian CDF the shadow's edge falls off by, at a signed distance OUTSIDE
 * the shadow's own silhouette: 1 deep inside, 0.5 exactly on it, 0 far outside.
 *
 * A Gaussian-blurred silhouette is what `box-shadow` specifies and what the
 * reference measures, so this is the one curve, evaluated identically by both
 * tiers and by the shader. Written as the tanh form rather than as `erf` because
 * WGSL has no `erf` and a curve the shader cannot evaluate is not one shape: the
 * approximation's worst error is 1.8e-4 across the whole line, which at the
 * shipped occlusion is 0.015 of one 8-bit code.
 */
/** sRGB's power-law exponent — the one `outerShadowAlpha` inverts. */
export const SRGB_ENCODING_EXPONENT = 2.4;

export function outerShadowFalloff(signedDistancePx: number, sigmaPx: number): number {
  const x = -signedDistancePx / Math.max(sigmaPx, 1e-4);
  return 0.5 * (1 + Math.tanh(0.7978845608028654 * (x + 0.044715 * x * x * x)));
}

/**
 * The compositing-space alpha that reproduces a linear-light occlusion.
 *
 * Both tiers paint the shadow the same way — a pure BLACK layer at some alpha,
 * composited source-over — and that is already a multiplicative occlusion by
 * compositing algebra alone: `out = (1 − α)·backdrop + α·0 = backdrop·(1 − α)`.
 * The shadow's colour being zero is what collapses source-over onto multiply, and
 * it is also why the facet is exactly inert over black on both tiers, with no
 * special case anywhere.
 *
 * What does NOT come free is the space. The reference removes a fraction of the
 * backdrop's LINEAR light; a browser composites a `box-shadow` — and a
 * premultiplied canvas — in ENCODED sRGB. So the same visual result needs a
 * different alpha, and the conversion is exact under sRGB's power law:
 * `enc(L(1−occ)) = enc(L)·(1−α)` gives `α = 1 − (1−occ)^(1/2.4)`, independent of
 * the backdrop, which is the same conversion `cssTintAlpha` performs for the tint
 * and the same reason it exists.
 *
 * The residual is the transfer function's linear toe, and it is small and stated:
 * across every backdrop level from 0.004 to 1.0 the worst departure from the
 * reference's own composite is 2.1 of 255 at the shipped occlusion, against a bed
 * whose own reproducibility is ±4 of 255 (Decision Log 10). A per-pixel exact
 * conversion is not available to either tier — `box-shadow` takes one alpha, and
 * the canvas composites outside the shader — so this is the honest floor rather
 * than a shortcut.
 */
export function outerShadowAlpha(occlusion: number): number {
  const occ = Math.min(1, Math.max(0, occlusion));
  return 1 - Math.pow(1 - occ, 1 / SRGB_ENCODING_EXPONENT);
}

/**
 * How far past a surface's own contour the shadow can still change a pixel, CSS
 * px — the margin the GPU tier has to rasterise into, since a scissor rect that
 * stops at the contour would slice the facet off.
 *
 * The cut-off is where the shadow stops moving an 8-bit code over a white
 * backdrop, and it is taken against the **compositing-space alpha** rather than
 * against the linear occlusion, because the alpha is what the canvas actually
 * writes: `page × (1 − α·falloff)` moves one code when `α·falloff` reaches
 * 1/255. Thresholding the linear occlusion instead over-allocated by about 5 CSS
 * px on every edge at the shipped constants — pure cost on a facet already
 * measured at 3.2× the frame's GPU time.
 *
 * `shadow.occlusion` must be the EFFECTIVE amplitude — after the accessibility
 * fold and after the size law — which is the caller's to resolve, because only
 * it knows the group's membership. A pad taken from the base amplitude while the
 * shader emits an amplified one slices the deepest surface's shadow off at the
 * scissor, while the CSS tier, which has no scissor, goes on drawing it.
 *
 * The solve runs over the signed distance to the shadow's OWN silhouette, which
 * may be negative — a pixel just outside the contour is already inside the
 * offset, spread silhouette — so `occlusion = 0`, and any amplitude too faint to
 * move a code anywhere, both fall out as a reach of zero rather than needing a
 * case of their own.
 */
export function outerShadowReachPx(shadow: MaterialOuterShadow): number {
  const alpha = outerShadowAlpha(shadow.occlusion);
  if (!(alpha > 0)) return 0;
  const cutoff = 1 / 255 / alpha;
  // Even a pixel the silhouette covers outright cannot move a code.
  if (cutoff >= 1) return 0;

  const sigma = Math.max(shadow.sigmaPx, 1e-4);
  // Bisected on the falloff itself, so the reach cannot disagree with what the
  // shader draws.
  let lo = -(8 * sigma + Math.abs(shadow.offsetPx) + Math.abs(shadow.spreadPx));
  let hi = 8 * sigma;
  for (let i = 0; i < 48; i += 1) {
    const mid = (lo + hi) / 2;
    if (outerShadowFalloff(mid, sigma) > cutoff) lo = mid;
    else hi = mid;
  }

  /*
   * Back to a distance from the COMPONENT's contour, in whichever direction
   * reaches furthest — the pad is applied to all four edges, so one bound has to
   * cover them all. The offset enters by magnitude (downward when positive,
   * upward when negative) and the spread carries its own sign, because a
   * negative spread pulls every direction in together.
   */
  return Math.max(0, hi + Math.abs(shadow.offsetPx) + shadow.spreadPx);
}

export function lensDepthPx(
  thicknessPx: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const gain = lensSizeGain(spanPx, profile);
  return Math.min(Math.max(thicknessPx, 0) * gain, spanPx * 0.5);
}

/** Body blur LOD on the chain for a given lens depth — thicker glass diffuses more. */
export function bodyLod(
  lensDepth: number,
  maxLod: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return Math.min(Math.max(lensDepth * profile.lensBodyLodPerPx, 0), maxLod);
}
