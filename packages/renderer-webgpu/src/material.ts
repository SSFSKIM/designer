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
import { linearToSrgbChannel, relativeLuminance, srgbToLinear, srgbToLinearChannel } from "./color";

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
 * ## Two terms on ONE falloff (W14 G0, claims §5.62)
 *
 * The description above holds where W8 measured it and misses two things the bed
 * has since shown, both of which live in the AMPLITUDE and neither of which
 * moves a length. Outside the coverage, in the compositing (encoded) domain:
 *
 *     out = bg · (1 − α_b(backdrop, span) · F(d))  +  A_v(span) · F(d) · V
 *
 * with **one** falloff `F` — W8's own, at 15.55 / 7.95 / 3.1, re-read free and
 * unmoved on both terms (σ 14.8–16.2 and offset 7.93–8.00 for the black term,
 * σ 14.1–17.1 and offset 7.6–8.4 for the lift) — and `V` the backdrop's own
 * light blurred at `liftBlurSigmaCss`.
 *
 * The first term's amplitude ADAPTS below the knee: the reference's fill alpha
 * is 0.33 over the mid backdrops, 0.127 over `light-solid` and nothing over
 * black, keyed on the SAME backdrop luminance statistic W9's face response uses
 * (the ENCODED-space mean, decoded — `backdropToneAnchorX`'s own axis), through
 * the same thickness curve that gates that regime. Above the knee it is the
 * composite's transmission by span. The second term is the lift, GPU-tier only,
 * and it is exactly zero below the knee and exactly zero over black, so the
 * facet's "invisible over a black backdrop" property survives both terms.
 *
 * The layer tree's `inputShadowAmount` and `inputShadowHeight` are NOT either
 * term's spatial extent — the charter's advisory was wrong there, and G0's free
 * fits overturned it. Only `inputShadowBlurRadius` 40 belongs to the lift, as
 * the blur of the backdrop it copies.
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
   * The black term's peak occlusion below the knee, over a backdrop the material
   * cannot see (linear luminance ≤ `OUTER_SHADOW_THIN_L.inert`): zero. Inert
   * over `dark-solid` and `impulse`, which is what the reference does — it
   * removes at most one or two of 255 codes there (claims §5.62 §5).
   */
  readonly thinOcclusionDark: number;
  /**
   * The black term's peak occlusion below the knee over the MID plateau —
   * backdrop linear luminance `OUTER_SHADOW_THIN_L.midFrom` … `midTo`.
   *
   * MEASURED (claims §5.62 §5): linear occlusion 0.347 over `mid-dark-solid`,
   * 0.334–0.339 over `photo`, 0.327–0.328 over the checkerboard and 0.329 over
   * `hc-text` — flat across a backdrop luminance range of 0.06…0.74, and a
   * constant 1.16–1.19× the fill alpha §5.50 §2 read off the layer tree.
   */
  readonly thinOcclusionMid: number;
  /**
   * The black term's peak occlusion below the knee over a BRIGHT backdrop, at
   * `OUTER_SHADOW_THIN_L.bright` and above.
   *
   * MEASURED (claims §5.62 §5): 0.127 over `light-solid` (linear luminance
   * 0.891), against the layer tree's tabulated 0.05 — so the reference's shadow
   * there is 0.39 of its shadow over the checkerboard, not one sixth. W8's
   * single 0.285 everywhere is 2.24× this, which is the whole of the user's
   * by-eye "the shadow is darker on the light-solid capsule" and, by the free
   * geometry fit on that cell (σ 14.81 / offset 7.97 / spread 3.17), no part of
   * it is shape.
   */
  readonly thinOcclusionBright: number;
  /**
   * The COMPOSITE occlusion above the knee at a casting span of 96 CSS px.
   *
   * FITTED in the renderer (claims §5.65), from G0's measurement of the
   * composite's transmission (0.379 on the checkerboard at span 96) to **0.370**.
   * It had to be fitted rather than adopted, because what G0 could identify at
   * the bed's noise floor is the composite transmission and the lift's peak
   * amplitude, not the split into (black alpha, vibrant alpha, vibrant colour):
   * both terms ride one falloff and their shapes correlate at 0.9998. So this
   * constant is the BLACK term of a two-term composite whose second term
   * (`liftAmplitude`) was fitted beside it, on X7's affine pair, and the pair is
   * what the referee reads.
   */
  readonly thickOcclusionAt96: number;
  /** The same at a casting span of 128 CSS px — FITTED to 0.448 from G0's
   * measured 0.497, for `thickOcclusionAt96`'s reason (claims §5.65). */
  readonly thickOcclusionAt128: number;
  /**
   * The same at a casting span of 160 CSS px — **UNFITTED**, and the one anchor
   * in this block that no calibration cell reaches.
   *
   * Every span above 128 in the bed is holdout, so 0.479 is carried by the stated
   * derivation from the two fitted anchors and not by a fit. The holdout, read
   * once and fitted to nothing, says it is 15% heavy (band `1 − a` 0.2436 against
   * the reference's 0.2117) and implies about 0.437 — which is BELOW the fitted
   * At128 and which no extrapolation from the calibration cells would have
   * produced. That reading is recorded and deliberately not adopted (claims §5.65
   * §4(b) and §6(iv)); closing it needs a calibration cell above span 128.
   */
  readonly thickOcclusionAt160: number;
  /**
   * **The lift (W14)** — the peak amplitude of the second term, in LINEAR light,
   * as a fraction of the backdrop's own blurred luminance. GPU tier only.
   *
   * The reference's thick shadow does not only remove light: on the
   * checkerboard's black squares, where a multiply is inert by construction, it
   * ADDS 7.4 of 255 (claims §5.62 §2). Pooled over six backdrops the addition
   * regresses on the σ-40 blurred backdrop at slope 0.0444 with intercept
   * −0.0042 and R² 0.983 — it is the backdrop's own light, blurred, composited
   * under the shadow, with no fixed colour left over. Zero over `impulse`, zero
   * over `dark-solid`, and zero below the knee, so the facet stays exactly inert
   * over black the way W8's multiply is.
   *
   * FITTED to **0.0100** in the renderer over seventeen sweep passes, read on
   * X7's affine pair together with the three thick anchors (claims §5.65). The
   * provisional 0.0073 was G0's +0.0038 of LINEAR lift at span 160 divided by
   * the ≈ 0.52 linear luminance the checkerboard's σ-40 blur sits at, and the fit
   * is 37% larger. The space matters and this wave names it everywhere (claims
   * §5.62 §3): §5.60's +0.039 is the same lift read in ENCODED luma.
   */
  readonly liftAmplitude: number;
  /**
   * Where the lift starts, in casting span, CSS px — the thin/thick knee, and it
   * is exact: the lift reads 0.0000 at spans 32 and 44 and is present at 96
   * (claims §5.62 §2). The layer tree's own `VibrancyContribution` clamps from
   * the same 64.
   */
  readonly liftSpanMin: number;
  /**
   * Where the lift saturates, in casting span, CSS px.
   *
   * FITTED to **118** (claims §5.65), from a provisional 128. The measured rise
   * is 0.52 / 0.96 / 1.00 of the span-160 value at spans 96 / 128 / 160, against
   * the layer tree's clamp((span − 64)/96) = 0.33 / 0.67 / 1.00 — so the lift is
   * NOT proportional to `VibrancyContribution`; it rises and saturates, reaching
   * 96% by span 128 (claims §5.62 §2), which a smoothstep from `liftSpanMin`
   * reproduces and the clamp does not. The holdout says the reach saturates a
   * little early — the lift's own residual there is one-signed and small, 5% low
   * at span 130 and 9% at 160 (claims §5.65 §4(d)) — and it was not refitted
   * after that reading.
   */
  readonly liftSpanFull: number;
  /**
   * The σ, in CSS px, of the blur the lift copies the backdrop through.
   *
   * MEASURED at 40 ± 8 CSS px on `rrect-lg` at both scales and in two rings, by
   * the probes' pitch axis — the pooled residual has a real minimum there, 12%
   * below the flat-copy residual (claims §5.62 §3). It is the layer tree's
   * `inputShadowBlurRadius` 40 read as a Gaussian standard deviation. NOT
   * identifiable on the mid spans (flat to 0.7%), and reported as such rather
   * than fitted there.
   */
  readonly liftBlurSigmaCss: number;
  /**
   * The shadow's amplitude UNDER reduced transparency — one absolute linear
   * occlusion that replaces both regimes, not a factor on either. MEASURED,
   * which is what the charter asked for before the fold was written.
   *
   * **0.197 (measured 0.192–0.202).** W14 G0 read the preference on the wider
   * bed and what it found is a flat number: the reference's exterior is
   * 0.192–0.202 under increased contrast and reduced transparency alike, **thin
   * and thick together** and over every backdrop it can be read on (claims §5.62
   * §5). The preference removes the material's adaptation, so the shadow it
   * leaves has neither the thin regime's backdrop keying nor the thick regime's
   * span law in it — one amplitude for every surface over every backdrop, which
   * is what `outerShadowUnderPolicy` writes into all six anchors. The lift goes
   * with it: a composite whose two regimes read the same number has no second
   * term left in it.
   *
   * It is stated as an ABSOLUTE occlusion rather than as a ratio because W8's
   * 0.70 multiplier was fitted when the amplitude was one span-flat number and a
   * ratio was the same thing as a level. It is not any more: multiplying six
   * unequal anchors keeps exactly the backdrop and span variation the preference
   * removes, and a span-160 surface over a mid-tone backdrop folded to 0.38
   * against the reference's 0.20. The number the reference states is a level, so
   * this constant is a level.
   *
   * Nothing is special-cased for a dark backdrop and nothing needs to be: an
   * occlusion is a fraction of the backdrop's own light, so a flat 0.197 over
   * black still removes nothing, and the facet stays as inert there as the thin
   * regime's own zero anchor makes it without the preference.
   *
   * The `increased contrast` reference reproduces the reduced-transparency
   * amplitude to four decimals (0.1830, 0.1884, 0.1882 on the three structured
   * backdrops at a 44 px span, with σ, offset and spread unmoved), which is
   * Decision Log 8's finding again: macOS force-couples the two toggles, so the
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
   * `sizeSpanMin` to `sizeSpanMax`, and the thickness-derived facets are gains
   * on it — the lens (`lensSizeGainMax`), the occlusion (`sizeOcclusionGain`)
   * and the inner shadow (`sizeShadowGainMax`). The scattering was one of them
   * until W11c measured its curve to be a different one (a floor at small
   * spans, a rise past 96) and W13 measured that curve to be the projection of a
   * ramp in depth — see `sizeScatterFloor` and `sizeScatterRampStartThin1x`; the
   * scattering now rides its own law entirely, and this band is untouched by it.
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
   * The inner shadow's depth gain on the size curve — and, until W12 G2, the
   * lens's too.
   *
   * The inner shadow's depth is `thickness × (1 + (lensSizeGainMax − 1) ×
   * sizeThickness)`, clamped to the shorter *half* extent, and its profile is
   * `(1 − depth)²` on that depth: the landed law of W2, kept byte-for-byte for the
   * occlusion because nothing measured it as wrong. The LENS no longer reads it —
   * the reference's own lens height is a clamped linear function of the span
   * (`lensHeightPerSpan`, `lensHeightMax`), read straight from its layer tree
   * (claims §5.50), and the lens takes that law from W12 G2 on. The name stays so
   * the profile documents keep naming the constant they measured.
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
   *
   * MEASURED (W11c G1, claims §5.41), and no longer a gain on `sizeThickness`
   * alone — see `sizeScatterFloor` and `sizeScatterRampStartThin1x` below for the
   * law it rides. 8: the heavy component of the reference's interior sits near
   * σ 10 device px against a body σ of 1.25, and the gain sweep has a clear
   * minimum at 8 (RMS 0.0164 against 0.0180 at 6 and 0.0191 at 10 on the probe
   * bed).
   */
  readonly sizeScatterGainMax: number;

  /**
   * **The scattering facet's frost** (W11c G1, claims §5.41; re-read by W13 G1).
   *
   * The reference's interior over structured content is two components, read
   * off the W9 probe bed across four checkerboard pitches and five spans: a
   * sharp one near σ 1.25 device px and a heavy one near σ 10, mixed by a share
   * that is already ≈ 0.4 at spans of 32–44 and still rising at 160. W11c
   * carried that mix as one number per span, a floor rising by a smoothstep to
   * a band top (`sizeScatterSpanMax`); W13 G0 measured the mix **per depth** on
   * both probes and found a ramp under the contour that the span law had been
   * summarising (claims §5.61 §2). W13 G1's first form replaced the span law
   * with the ramp outright and its runtime sweep refuted that: the ramp's own
   * projection onto one number per surface runs 0.43–0.56 where the span law it
   * replaced runs 0.41–1.00, so a ramp with a start and a reach is nearly
   * span-flat where the bed is strongly span-graded, and no point in 81 reached
   * the wave's stops (`results/2026-09-03-w13-ramp/g1/sweep/g1-sweep.md` §4,
   * §7). So the two are kept **together**: the span law is the ramp's DEEP
   * value and the ramp is a near-contour excursion above it. This floor is
   * unchanged in value and in meaning under either: the mix a surface carries
   * at any size, the material's own frost.
   *
   * It keeps its fold semantics, and they are now written on the ramp rather
   * than on a span curve:
   *
   * ```
   * kScatter(u) = floor + (k(u) − floor) · fold
   * ```
   *
   * — so at fold 1 the ramp is rendered exactly and at fold 0 the material sits
   * at this floor exactly, which is what the landed law did at fold 0 too. The
   * floor is the frost the material has whatever its size, and is **not**
   * folded under an accessibility preference; the excursion away from it is
   * depth, and is. Fitted with `rrect-lg` held out (W11c G1): 0.40 (0.0175 at
   * 0.3, 0.0174 at 0.45).
   */
  readonly sizeScatterFloor: number;

  /**
   * **The scattering facet's span curve** (W11c G1, claims §5.41) — the top of
   * the band the frost rises to, and, since W13 G1's re-forming, the span law
   * that supplies the depth ramp's DEEP value:
   *
   * ```
   * kDeep(span) = floor + (1 − floor) · smoothstep(sizeSpanMin, sizeScatterSpanMax, span)
   * ```
   *
   * — byte for byte the curve W11c fitted and W13 G1's first form retired. It
   * came back because the sweep measured what retiring it cost (§4 of
   * `results/2026-09-03-w13-ramp/g1/sweep/g1-sweep.md`): the span dependence of
   * the bed is real and strong, and the ramp's four constants cannot carry it
   * at the same time as the band's near-contour excursion. What the ramp adds
   * is what this curve never could — the depth structure inside one surface —
   * and it now adds it on top of this rather than instead of it, so the deep
   * interior of every span is exactly where W11c and W12 put it.
   *
   * `sizeThickness` — zero at `sizeSpanMin` and saturated at `sizeSpanMax` = 96
   * — can express neither the floor nor a band top past 96, and moving
   * `sizeSpanMax` would move the lens, the occlusion, the inner shadow and W9's
   * thin/thick response rows with it, which is why the scatter mix has its own
   * curve at all. Fitted with `rrect-lg` held out (W11c G1): band top 256
   * (0.0182 at 224, 0.0174 at 320); the held-out cell's residual 0.0366 →
   * 0.0174.
   */
  readonly sizeScatterSpanMax: number;

  /**
   * **The body's second scale** (W15 G1, from the measurement of claims §5.69
   * §1–§2) — the heavy width's gain, the deep value's floor and the deep
   * value's span top, each read again at dpr 2.
   *
   * At 2x the reference's body is a different object from the one the three
   * constants above describe, and §5.69 measured all of it: the deep interior
   * is FULLY heavy on the two largest spans and 0.90–0.95 heavy on `rrect-md`
   * (§2), where the 1x span curve leaves a sharp share of 0.24–0.36 there, and
   * the heavy component's own width is 8–11 device px against the 1x law's 10
   * CSS px (§1). One curve fitted at 1x cannot be both, so the deep value's two
   * constants and the gain get a second reading rather than a scale factor —
   * the same shape the ramp's anchors already have.
   *
   * Each is interpolated by `rampAtScale`: held at the 1x constant at dpr ≤ 1,
   * at this one from dpr 2 up, linear between. **At dpr 1 every one of them is
   * inert by construction, whatever it says** — W15's binding rule — so the 1x
   * material is byte-identical to the W13 bed and the landing's confirmation
   * measured exactly that: 49 of 49 1x GPU cells identical to the bed with
   * every capture byte-identical (claims §5.70 §8).
   *
   * Consumed at draw time, not folded into a constant: `scatterDeepThickness`
   * takes the ratio for the floor and the span top, the renderer resolves all
   * three from the viewport's own ratio and hands them to the optics pass
   * through the uniforms the shader already reads (`scatter.x`, `lensOval.w`
   * and `size.x`), and `scatterThickness`, `scatterSharpShare` and the ramp's
   * area-average projection read the resolved deep value.
   *
   * **FITTED** by W15 G1's runtime sweep at
   * `--profile apple-macos-26.5-2x-light-standard` on the calibration set, the
   * holdout untouched, and landed at the values below (claims §5.70 §2 and §8;
   * the four sweeps `results/2026-09-04-w15-body-2x/g1/stage1..stage3` and the
   * confirmation `confirm-3`, whose 2x holdout was read once for this
   * configuration). The rule W13 wrote after the paper model over-credited the
   * mip chain's heavy tap (§5.58 §1) held: no constant here lands on a paper
   * prediction, and the sweep contradicted the paper estimate.
   *
   * **The gain, 4.8.** Stage 2c swept it over 4.0 / 4.4 / 4.8 / 5.2 at the
   * chosen base and found an INTERIOR MINIMUM at 4.8 — the interior spread
   * against native reading 0.0335 / 0.0214 / 0.0120 / 0.0217 with the band's
   * rise at its top too. Through `bodySigmaCssFor` that is a heavy width of
   * **6 device px** at dpr 2, NARROWER than the 8–11 device px §5.69 §1
   * bounded as a Gaussian: the estimator carries ±40% on a real capture of a
   * known law (§5.69 §3) and the mip chain's tap is not a Gaussian, so the
   * renderer is the fitting instrument and 6 is the width it draws best.
   *
   * **The floor, 1.0** — the deep value FULLY heavy at dpr 2, which is what
   * G0's deep windows read on the two largest spans (§5.69 §2). `kDeep` is
   * therefore 1 at every span at this ratio, and the depth ramp above it is the
   * whole body (§5.70 §1).
   *
   * **The span top, 256** — the 1x value, unchanged, because a floor of 1
   * leaves the deep value nothing to rise to and the top has no work at this
   * ratio. Stage 1 swept it against 128 and the bed did not ask for the change.
   */
  readonly sizeScatterGainMax2x: number;
  readonly sizeScatterFloor2x: number;
  readonly sizeScatterSpanMax2x: number;

  /**
   * **The heavy width's gain at the TOP of the scatter span curve, at dpr 2**
   * (W15 G1's re-form, from claims §5.70 §4 and §7 and the measurement of
   * §5.69 §1) — the second-scale term that lets the 2x heavy width GROW with
   * the span instead of being one number for the whole bed.
   *
   * `sizeScatterGainMax2x` above is one gain at dpr 2, and the sweep that fitted
   * it read the calibration cells, whose spans are 32–128. The reference's heavy
   * kernel is not one width: §5.69 §1's bounded per-span fit reads 8.0 / 7.5 /
   * 8.0 / 9.0 / 11.0 device px across the bed's spans, a ratio of 1.375 between
   * span 160 and span 96. Landing the single gain accordingly left the largest
   * span's deep interior about 40% too structured (`rrect-lg` at 2x, spread
   * 0.1134 against the reference's 0.0810, claims §5.70 §4) while every smaller
   * cell rose. So the gain takes a second grading, in SPAN:
   *
   * ```
   * gain(span, dpr) = gainAtScale(dpr)
   *                 + (gainFar(dpr) − gainAtScale(dpr))
   *                   · smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span)
   * ```
   *
   * with `gainAtScale` the existing `scatterGainAtScale` and `gainFar` this
   * constant interpolated by `rampAtScale` from `sizeScatterGainMax`. The curve
   * is not a new span statistic: it is the same smoothstep the fourth form's
   * far-anchor decline already rides (`scatterRampStart`), so the width and the
   * ramp's start move along one curve above the thickness knee.
   *
   * **Inert at dpr 1 by construction.** `gainFar` interpolates from
   * `sizeScatterGainMax` — the 1x gain, not this constant — so at dpr ≤ 1 the
   * far gain IS the base gain and the whole term is a flat no-op whatever this
   * says. That is W15's binding rule (the 1x material does not move) discharged
   * by the shape of the formula rather than by a capture.
   *
   * **LANDED at 9.9** (claims §5.70 §8; W15 Decision Log 3, the user's landing
   * "the re-form"), and the value is G0's rather than the holdout row's: §5.69
   * §1's bounded per-span reading is 8 device px at span 96 and 11 at 160, a
   * ratio of 1.375, and this curve reads 0.352 at span 160, so 4.8 + (9.9 −
   * 4.8) · 0.352 reproduces that ratio over the base gain of 6 device px. The
   * heavy width at dpr 2 is therefore 6.0 device px at spans ≤ 96, 6.7 at 128,
   * 8.2 at 160 and 12.4 at 256 and beyond. The calibration cells neither chose
   * the value nor rejected it — `stage3` swept 4.8 / 7.5 / 9.9 / 12.5 and only
   * `rrect-ml` (span 128, a tenth of the grading) moves, its interior spread
   * 0.1125 → 0.0993 against native 0.1018 at 9.9, which is the sweep's best on
   * its own objective. The confirmation's holdout `rrect-lg` rose 0.9661 →
   * 0.9762 with its interior spread 0.0721 against native 0.0810.
   */
  readonly sizeScatterGainFar2x: number;

  /**
   * **The body's depth ramp** (W13 G1, from the measurement of claims §5.61 §2
   * and the re-forming its runtime sweep forced) — a near-contour excursion on
   * the sharp component's share, riding on top of the span law
   * `sizeScatterSpanMax` supplies rather than replacing it.
   *
   * ```
   * kDeep(span) = sizeScatterFloor + (1 − sizeScatterFloor)
   *               · smoothstep(sizeSpanMin, sizeScatterSpanMax, span)
   * sDeep(span) = 1 − kDeep(span)
   * s₀(span)    = startThin + (startThick − startThin) · sizeThickness(span)
   * s(u, span)  = sDeep + max(0, s₀(span) − sDeep) · max(0, 1 − u / U(dpr))
   * k(u, span)  = 1 − s(u, span)
   * ```
   *
   * with `u` the pixel's depth under the contour and `U` the reach, both in
   * DEVICE px. `s₀` is the sharp share **at the contour** and `U` is where the
   * excursion vanishes into the deep value — not where a line from the start
   * would hit zero, which is what the first form's reach meant. Deep inside any
   * surface the body is exactly the W11c/W12 material; within `U` of the
   * contour the sharp component is lifted toward `s₀`, which is the band the
   * reference has and the uniform share does not.
   *
   * **Why the start grades with the span, in the third form.** The second form
   * gave the excursion one start per scale and its runtime sweep refuted that
   * too, arithmetically rather than for want of a better point (claims §5.64
   * §2): `rrect-sm`'s span is exactly `sizeSpanMin`, so its deep sharp share is
   * exactly `1 − sizeScatterFloor` = 0.600 and no start at or below 0.600 can
   * touch it, while `rrect-ml`'s band only improves below a start near 0.583.
   * The window where both hold is empty, and the reach cannot open it — the
   * reach decides how much of a surface the excursion covers, never which
   * surfaces it touches, because `max(0, s₀ − sDeep(span))` has no reach in it.
   * G0 read the reference's start as strongly graded by span (0.637 / 0.642 on
   * the thin cells against 0.512 / 0.501 / 0.410 on the thick ones at 1x), so
   * the start is given exactly that grading — across `sizeThickness`, the
   * material's OWN thin/thick curve with its knee at 64, the one the face's
   * tone response and the outer shadow already blend across. Reusing it is the
   * point: it introduces no new span statistic, and `sizeSpanMax` stays where
   * every other facet reads it.
   *
   * **Why this form and not the ramp alone.** W13 G0 measured a ramp with a
   * free start, reach and floor (H2) and the first implementation took the free
   * start and reach with a floor of zero, retiring the span law. Its runtime
   * sweep — 81 points, both scales, the real renderer — could not reach the
   * wave's stops at any point, and named the mechanism: the ramp's projection
   * onto one number per surface runs 0.43–0.56 at 1x where the retired span law
   * ran 0.41–1.00, so the family is nearly span-flat and the bed is strongly
   * span-graded; small spans want a high start and large spans a low one and no
   * pair can be both (`.../g1/sweep/g1-sweep.md` §4). §7 of the same report
   * asked for exactly this: "the ramp's DEEP value wants to be the span-graded
   * heavy share the retired law supplied, and its near-contour excursion the
   * sharp term the band asks for." The floor H2 left free is therefore not one
   * more constant but the span law itself, which is already fitted.
   *
   * The reach stays a LENGTH in device pixels, which is the reading that did
   * survive the sweep: the free fits' reaches in absolute depth spread by 1.3×
   * across the spans (108 / 115 / 144 CSS px at 1x on `rrect-lg` / `-ml` /
   * `-md`) where the reaches as a fraction of the half-span spread by 2.2×, and
   * between the two scales that length roughly halves in CSS px — one length in
   * device pixels, the same reading as the widths (§5.55 §1, §5.56 §1).
   *
   * The start and the reach are anchored at the two scales the reference was
   * measured at rather than given a scale term: `…1x` is the value at dpr 1,
   * `…2x` at dpr 2, the pair interpolated linearly in dpr and held constant
   * outside [1, 2] (`scatterRampStart`, `scatterRampReachDevicePx`).
   *
   * **The FOURTH form: the start keeps falling past the thickness knee (W13
   * Decision Log 6; claims §5.67 §4, §6).** The third form's holdout failed on
   * one row for the form's own arithmetic: `sizeThickness` saturates at
   * `sizeSpanMax` 96, so spans 96, 128, 130 and 160 all received the identical
   * thick start while G0 read the reference's start FALLING across exactly
   * those spans (0.512 → 0.501 → 0.410), and because the deep value keeps
   * falling to `sizeScatterSpanMax` the excursion GREW with span (0.039 →
   * 0.156 → 0.284) where the reference's shrinks — `rrect-lg` overshot its
   * interior by 33%. So the start gets a slow decline along the scatter
   * facet's own curve above the knee, `startFar` being its value at span ≥
   * `sizeScatterSpanMax`:
   *
   *   s₀(span) = thin + (thick − thin) · sizeThickness(span)
   *            + (far − thick) · smoothstep(sizeSpanMax, sizeScatterSpanMax, span)
   *
   * Two curves the material already has, one more constant per scale, and no
   * new span statistic. At 2x the decline is switched off rather than inverted:
   * `far` and `thick` carry the same number since W15 G1, because G0 read the
   * reference's 2x start FLAT across the thick spans (claims §5.69 §2, §5.70 §6
   * (iv)) — the decline is a 1x feature of this form.
   *
   * The 1x three are FITTED (W13 G1's third and fourth sweeps) and the 2x four
   * are FITTED or read from G0 by W15 G1 (claims §5.70 §2 and §8); no constant
   * here lands on a paper prediction, because the paper model over-credited the
   * mip chain's heavy tap once already (§5.58 §1). What they carry:
   *
   * **1x — thin 0.64, thick 0.52, reach 120 device px.** G0's own start
   * readings are 0.637 on `rrect-sm` and 0.642 on the capsule at the thin end
   * and 0.512 / 0.501 / 0.410 on `rrect-md` / `-ml` / `-lg` at the thick end.
   * A thick anchor fitted to all three thick cells jointly comes out near 0.47,
   * and 0.47 sits 0.011 *below* `rrect-md`'s own deep sharp share of 0.481,
   * which would clamp the excursion to zero on that one cell. 0.52 is above it
   * and is also G0's reading on that cell, so the fit is not traded against the
   * form's own arithmetic.
   *
   * **2x — thin 0.46, thick 0.21, far 0.21, reach 100 device px, and the ramp
   * is now the WHOLE body above the deep value** (W15 G1, claims §5.70 §1–§2).
   * W13 left these inert for the deep value's sake: at `sizeScatterFloor2x` 0.4
   * every anchor sat below its cell's deep sharp share and `max(0, s₀ − sDeep)`
   * was bit-exactly zero on the whole bed. W15 G1 fitted that deep value fully
   * heavy (`sizeScatterFloor2x` 1.0), so the deep sharp share at dpr 2 is 0 and
   * the anchors act on the numbers they were carrying — which is why the wave's
   * three gaps turned out to be one gap (§5.70 §6 (i)).
   *
   * The values are G0's readings where the sweep was flat and the sweep's where
   * it was not. **Thin 0.46** is G0's u 6 reading exactly (0.494 / 0.468 on the
   * thin cells) and stage 2b's best, over a top nine points within 0.002 of
   * each other. **Thick and far 0.21**: G0's 2x starts on the thick cells are
   * 0.163 / 0.199 / 0.210 at their own widths and 0.192 / 0.199 / 0.195 at one
   * common width — flat with span, not declining — so the two anchors take one
   * number and the fourth form's decline is off at this scale; stage 2a
   * measured the objective flat over 0.17–0.25 and worse at 0.33. **Reach 100
   * device px** = 50 CSS px against G0's measured 49 / 53 / 56, and stage 2b
   * found 100 and 130 indifferent.
   *
   * **far — 0.20 at 1x (FITTED on the W14 bed), 0.21 at 2x.** The fourth
   * sweep (`results/2026-09-03-w13-ramp/g1/sweep-4/`) swept far over eight
   * points from 0.52 (the third form) down to 0.15: S1 and S4 pass at every
   * one, only `rrect-ml`'s rows move and they improve monotonically as far
   * falls, and the band is flat within the bed's noise below 0.30. The cell
   * the constant exists for is holdout, so the tie inside the noise is broken
   * by the reference's own reading — G0's `rrect-lg` start of 0.410 at span 160
   * is far = 0.207 through this form — and 0.20 is the measured grid point that
   * carries it. The confirmation read `rrect-lg` at `ssimMean` +0.0056 against
   * the W14 bed (the third form: −0.0026) with its interior 12% over the
   * reference (from 33% over). At 2x far equals the thick anchor, so the start
   * is flat past the knee at that scale — G0's own reading (§5.69 §2), and the
   * holdout's band supports it (`rrect-lg` +0.0106, claims §5.70 §8).
   *
   * At dpr 1 none of the 2x four is read at all: `rampAtScale` holds every one
   * of them at its 1x anchor below dpr 1, so the 1x material is byte-identical
   * to the W13 bed and the landing's confirmation measured that on 49 of 49 1x
   * GPU cells (claims §5.70 §8).
   */
  readonly sizeScatterRampStartThin1x: number;
  readonly sizeScatterRampStartThick1x: number;
  readonly sizeScatterRampStartFar1x: number;
  readonly sizeScatterRampStartThin2x: number;
  readonly sizeScatterRampStartThick2x: number;
  readonly sizeScatterRampStartFar2x: number;
  readonly sizeScatterRampReach1xPx: number;
  readonly sizeScatterRampReach2xPx: number;

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

  /**
   * The lens (W12 G2, claims §5.51) — one steep power on the reference's own
   * span law, along a direction the reference ovalizes.
   *
   * The reference's `glassBackground` filter takes an inner refraction *amount*
   * and *height* that are clamped linear functions of the shape's shorter side
   * (claims §5.50: amount −min(0.8·span, 60), height min(0.25·span, 20)). What
   * those two numbers do spatially is not in the tree; measured as a field on
   * the captures (§5.49) and ranked on the pixels (§5.51), the band is
   *
   *   D(u) = S · max(0, 1 − u / L′)^p,   S = lensRefractionGain · A(span),
   *                                       L′ = lensExtentGain · lensDepth,
   *
   * with `lensDepth = (thickness / lensThicknessReference) × H(span)` the
   * reference's height law scaled by the author's thickness (8 is the default
   * and the reference's unit — at 8 the depth IS Apple's height, 8 / 11 / 20 on
   * spans 32 / 44 / ≥ 80), `A(span)` the amount law scaled the same way, and
   * `p = lensProfileExponent`. Apple's own two-term profile at its literal
   * amounts was ranked too and lost on the pixels and the holdout; its span law
   * is adopted, its shape is not (§5.51 §2).
   *
   * `lensRefractionGain` is therefore re-based: it was 1.6 lens depths on the
   * W11c square profile (S = 1.6 × 20.8 = 33.3 at saturation), it is now the
   * scale on the reference's amount (S = 0.745 × 60 = 44.7), fitted on
   * `rrect-md` + `-ml` at 1x with `rrect-lg` held out.
   */
  readonly lensRefractionGain: number;
  /** The reference's inner refraction height law: `min(lensHeightPerSpan · span, lensHeightMax)`. */
  readonly lensHeightPerSpan: number;
  readonly lensHeightMax: number;
  /** The reference's inner refraction amount law: `min(lensAmountPerSpan · span, lensAmountMax)`. */
  readonly lensAmountPerSpan: number;
  readonly lensAmountMax: number;
  /**
   * The author `thickness` at which the lens depth equals the reference's own
   * height — the host's default, and what the bed was captured at. A thicker
   * authoring scales the depth and the magnitude together.
   */
  readonly lensThicknessReference: number;
  /** The profile's extent over the lens depth: D reaches zero at `lensExtentGain × lensDepth`. */
  readonly lensExtentGain: number;
  /** The profile's exponent — the square of W11c became a steeper power (§5.49 §2). */
  readonly lensProfileExponent: number;
  /**
   * The direction's ovalization (§5.49 §3, §5.50): the reference's SDF element
   * carries `gradientOvalization`, and the band is magnified *along* the edge by
   * up to 1.31× as a result. The shader displaces along the gradient of the
   * blended field `(1 − ω)·d_rrect + ω·d_oval`, `d_oval` the signed distance of
   * the ellipse inscribed in the surface's box, with the magnitude fixed. The
   * reference's value is 0.5 on thick shapes and 0 on thin ones; 0.6 is what the
   * pixels want on the box-inscribed ellipse (Apple's oval is more curved at the
   * edge midpoint than that ellipse). The switch is a step in the reference
   * between spans 64 and 72; here it is a smoothstep over that band, the same at
   * both ends and continuous through a morph.
   */
  readonly lensOvalization: number;
  readonly lensOvalizationSpanMin: number;
  readonly lensOvalizationSpanMax: number;

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
   * The author tint's shade law (W10) — Apple's "range of tones **mapped to
   * content brightness underneath**" (S219), measured per pixel on the frozen
   * bed and the W9 probe (claims §5.36).
   *
   * The tinted material is an OPAQUE, hue-preserving shade of the seed: the seed
   * times a scalar, and the scalar is linear in the luminance the untinted
   * material shows at the same pixel — `mix(tintShadeDark, tintShadeLight, u)`,
   * clamped so a shade is never brighter than the seed. Over black content the
   * reference shows about half the seed's light; over white it shows the seed
   * itself; over a checkerboard it shows both, cell by cell, with the seed's
   * chromaticity intact to three decimals at every pitch measured. That layer
   * composites over the material at the AUTHOR's opacity (the colour's alpha) in
   * the encoded space — the half-strength cell is the 0.501 encoded-space mix
   * of its untinted and full-tinted twins, per channel — so the material's own
   * alpha is not what a tinted surface shows.
   *
   * `tintShadeStrength` is the law's provenance gate: 1 where the constants were
   * measured (the light scheme), 0 where they were not — the dark scheme
   * renders the pure seed over every backdrop it was measured on, which is
   * consistent with "a shade relative to the material's own body level" but is
   * not yet separable from "no shading in the dark scheme". The collapse (W7)
   * folds the shade out the same way, because a collapsed material IS a dark
   * body and the reference renders the pure seed there too.
   *
   * MEASURED, both scales, twelve light-standard cells across three pitches:
   * fitted on the five probe cells only (17 700 px, RMS 0.0035) and refereed by
   * every canonical tinted row. Mirrored by `@vitreajs/vitrea-web`'s
   * `TINT_SHADE`, pinned in both directions by
   * `packages/calibration/test/tier-coherence.test.ts`.
   */
  readonly tintShadeDark: number;
  readonly tintShadeLight: number;
  readonly tintShadeStrength: number;

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
      // 1.25 since W11c G1 (claims §5.41): the reference's interior over
      // structured content is a sharp component near σ 1.25 plus a heavy one
      // the scatter facet now supplies (`sizeScatterFloor`); the cascade's 3
      // (claims §5.16) was the one Gaussian that best split the difference on
      // a bed with no pitch axis to tell the two apart.
      blurSigma: 1.25,
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
  // The inner shadow's depth gain since W12 G2 (the lens reads its own law
  // below); the value is W2's, unchanged.
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
  // MEASURED (W11c G1, claims §5.41): the scatter facet off the identity, on
  // its own curve — see `MaterialProfile.sizeScatterFloor`. The paragraph
  // above records why the identity was the right answer while `blurSigma`
  // was 3 and the bed had no pitch axis; the W9 probe's pitch axis is what
  // identified the two-component interior this expresses.
  sizeScatterGainMax: 8,
  sizeScatterFloor: 0.4,
  sizeScatterSpanMax: 256,
  // The second scale, FITTED by W15 G1's runtime sweep at dpr 2 and landed
  // (claims §5.70 §2 and §8): the gain 4.8 — a heavy width of 6 device px, the
  // sweep's own interior minimum and narrower than G0's Gaussian estimate — the
  // deep value fully heavy, and the span top left at the 1x value because a
  // floor of 1 leaves it nothing to rise to. Read only above dpr 1, so the 1x
  // material is byte-identical to the W13 bed (see
  // `MaterialProfile.sizeScatterFloor2x`).
  sizeScatterGainMax2x: 4.8,
  sizeScatterFloor2x: 1,
  sizeScatterSpanMax2x: 256,
  // The 2x gain's own span grading (W15 G1's re-form, claims §5.70 §8; W15
  // Decision Log 3), set from G0's independent per-span reading — 8 device px
  // at span 96 and 11 at 160 — and not from the holdout row it fixes.
  sizeScatterGainFar2x: 9.9,
  // The 1x three FITTED in the renderer (W13 G1's third sweep, 44 points over
  // the calibration bed: `results/2026-09-03-w13-ramp/g1/sweep-3/g1-sweep-3.md`
  // §3); the 2x three PROVISIONAL still, because at them the excursion is
  // bit-exactly zero on the whole bed and a sweep cannot fit what does not
  // move (§4). The thin anchor 0.72 is above G0's read-off of 0.637–0.642: the
  // grid runs 0.60 / 0.64 / 0.68 and the refinement 0.72 / 0.76, and 0.72 is an
  // interior optimum of both the interior objective and the interior gap. The
  // thick anchor 0.52 is G0's `rrect-md` reading and is above that cell's deep
  // sharp share of 0.481, where the joint thick fit of 0.47 would have clamped
  // it to nothing. The 2x three are G0's readings, LANDED by W15 G1 (claims
  // §5.70 §2): thin is G0's u 6 reading and stage 2b's best, thick and far are
  // one number because G0 read the 2x start flat across the thick spans, and
  // with the deep value now fully heavy at that ratio the ramp is the whole
  // body above it rather than the null W13 recorded. See
  // `MaterialProfile.sizeScatterRampStartThin1x`.
  sizeScatterRampStartThin1x: 0.72,
  sizeScatterRampStartThick1x: 0.52,
  sizeScatterRampStartFar1x: 0.2,
  sizeScatterRampStartThin2x: 0.46,
  sizeScatterRampStartThick2x: 0.21,
  sizeScatterRampStartFar2x: 0.21,
  sizeScatterRampReach1xPx: 80,
  sizeScatterRampReach2xPx: 100,
  sizeOcclusionGain: 0.05,
  sizeShadowGainMax: 1,

  /*
   * The lens (W12 G2, claims §5.51; Decision Log 3 of the W12 spec).
   *
   * MEASURED from the reference's own layer tree (§5.50): the inner refraction
   * amount and height laws, verified on spans 32 / 44 / 48 … 112 / 128 / 160
   * and the nested base at 130, and the ovalization's knee (0 through span 64,
   * 0.5 from 72). FITTED on the pixels (§5.51, a 2-D band renderer validated on
   * this renderer's own capture): the gain, the extent and the exponent, on
   * `rrect-md` + `-ml` at 1x pitches 16 and 32 with `rrect-lg` held out at both
   * scales; the ovalization's effective value on the box-inscribed ellipse.
   * Predicted before the landing capture: checkerboard SSIM 1x md / ml / lg
   * 0.954 / 0.931 / 0.929 → 0.970 / 0.946 / 0.942, 2x 0.939 / 0.902 / 0.901 →
   * 0.950 / 0.918 / 0.918, the capsule 0.977 → 0.985.
   *
   * What W11c G2 recorded here — 1.6 lens depths on the square profile, fitted
   * per depth shell — was the band's mean, not its shape (§5.48, §5.49); it is
   * kept in git history and in claims §5.43.
   */
  lensRefractionGain: 0.745,
  lensHeightPerSpan: 0.25,
  lensHeightMax: 20,
  lensAmountPerSpan: 0.8,
  lensAmountMax: 60,
  lensThicknessReference: 8,
  lensExtentGain: 1.337,
  lensProfileExponent: 3.69,
  // 0.8 by eye (W12 Decision Log 6). The pixels preferred 0.6 by a hair — every
  // texture row that can see ω scores 0.001–0.002 lower at 0.8 (claims §5.54) —
  // but the field's measured tilt sits at 0.8–1.0 (§5.49 §3) and the user read
  // the 0.8 sheet as much closer to macOS; the eye overrides a margin that small,
  // and §5.54 §1's rows are the recorded cost.
  lensOvalization: 0.8,
  lensOvalizationSpanMin: 64,
  lensOvalizationSpanMax: 72,

  reducedTransparencyFrost: 1.75,
  increasedOcclusionLift: INCREASED_OCCLUSION_LIFT,
  strongBorderRim: { rimWidth: 2, rimAlpha: 0.95 },
  reducedTintAdaptation: 0.35,

  /*
   * MEASURED (W10, 2026-09-02) — per-pixel least squares of the reference's
   * tinted pixel against its own untinted pixel on the five W9-probe tinted
   * checkerboard cells (pitch 4…64 px, 17 700 px): shade = 0.5289 + 0.4886·u,
   * RMS 0.0035. Out of sample on the canonical bed the orange cells fit at
   * RMS 0.003 with zero bias; blue sits 0.011 darker (the second hue's
   * residual, recorded and unmodelled). The light end extrapolates past 1 and
   * is clamped in `tintShade`. Claims §5.36.
   *
   * §5.13's earlier "the curve is the identity" fit was made on the material's
   * MEAN over solid backdrops, where u is either ~0.97 (shade 1.0) or the
   * collapse has already folded the shade out — the identity was the law's
   * two endpoints, seen without anything between them.
   */
  tintShadeDark: 0.5289,
  tintShadeLight: 1.0175,
  tintShadeStrength: 1,

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
   * `reducedTransparencyOcclusion` 0.70 was sharp where the amplitude was flat: a
   * 3.83× spread over 0.45…0.95 with a clear minimum. It also reconciled two
   * routes — 0.285 × 0.70 = 0.1995 against the reference's directly measured
   * reduce-transparency amplitude of 0.203 at a 44 px span. W8's 0.566 was the
   * ratio of the reference's two amplitudes; that was the ratio that made
   * vitrea's shadow match the reference's under the preference, and the two
   * differed because the base amplitude is a compromise across scenes whose
   * spread is much wider in the standard profile than under reduced transparency.
   * **W14 G1 re-forms the constant as the LEVEL those routes were reconciling
   * to** — 0.197 absolute, replacing both regimes rather than scaling them — for
   * the reason its doc comment gives: a ratio and a level stopped being the same
   * thing when the single amplitude became six unequal anchors.
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
   *
   * **W14 G1 answers that open question and replaces `occlusion`.** "Over the
   * flat near-white `light-solid` backdrop the same fit reads 0.123 rather than
   * 0.33 … it is not a function of the backdrop's luminance" was read on a bed
   * that had no backdrop between `hc-text` (linear 0.74) and `light-solid`
   * (0.891): it IS a function of the backdrop's luminance, and the whole factor
   * of 2.6 happens inside the gap the bed cannot see (claims §5.62 §5). The
   * single amplitude becomes six anchors on two regimes — three in backdrop
   * luminance below the knee, three in span above it — plus the lift's four
   * constants. The three lengths are untouched; G0 re-read them free on both
   * terms and they came back at W8's values.
   */
  outerShadow: {
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
export const SIZE_SCATTER_FLOOR = DEFAULT_MATERIAL_PROFILE.sizeScatterFloor;
export const SIZE_SCATTER_SPAN_MAX = DEFAULT_MATERIAL_PROFILE.sizeScatterSpanMax;
export const SIZE_SCATTER_GAIN_MAX_2X = DEFAULT_MATERIAL_PROFILE.sizeScatterGainMax2x;
export const SIZE_SCATTER_GAIN_FAR_2X = DEFAULT_MATERIAL_PROFILE.sizeScatterGainFar2x;
export const SIZE_SCATTER_FLOOR_2X = DEFAULT_MATERIAL_PROFILE.sizeScatterFloor2x;
export const SIZE_SCATTER_SPAN_MAX_2X = DEFAULT_MATERIAL_PROFILE.sizeScatterSpanMax2x;
export const SIZE_SCATTER_RAMP_START_THIN_1X = DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThin1x;
export const SIZE_SCATTER_RAMP_START_THICK_1X =
  DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThick1x;
export const SIZE_SCATTER_RAMP_START_THIN_2X = DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThin2x;
export const SIZE_SCATTER_RAMP_START_THICK_2X =
  DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThick2x;
export const SIZE_SCATTER_RAMP_START_FAR_1X = DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartFar1x;
export const SIZE_SCATTER_RAMP_START_FAR_2X = DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartFar2x;
export const SIZE_SCATTER_RAMP_REACH_1X_PX = DEFAULT_MATERIAL_PROFILE.sizeScatterRampReach1xPx;
export const SIZE_SCATTER_RAMP_REACH_2X_PX = DEFAULT_MATERIAL_PROFILE.sizeScatterRampReach2xPx;
export const SIZE_OCCLUSION_GAIN = DEFAULT_MATERIAL_PROFILE.sizeOcclusionGain;
export const SIZE_SHADOW_GAIN_MAX = DEFAULT_MATERIAL_PROFILE.sizeShadowGainMax;
export const LENS_REFRACTION_GAIN = DEFAULT_MATERIAL_PROFILE.lensRefractionGain;
export const LENS_HEIGHT_PER_SPAN = DEFAULT_MATERIAL_PROFILE.lensHeightPerSpan;
export const LENS_HEIGHT_MAX = DEFAULT_MATERIAL_PROFILE.lensHeightMax;
export const LENS_AMOUNT_PER_SPAN = DEFAULT_MATERIAL_PROFILE.lensAmountPerSpan;
export const LENS_AMOUNT_MAX = DEFAULT_MATERIAL_PROFILE.lensAmountMax;
export const LENS_THICKNESS_REFERENCE = DEFAULT_MATERIAL_PROFILE.lensThicknessReference;
export const LENS_EXTENT_GAIN = DEFAULT_MATERIAL_PROFILE.lensExtentGain;
export const LENS_PROFILE_EXPONENT = DEFAULT_MATERIAL_PROFILE.lensProfileExponent;
export const LENS_OVALIZATION = DEFAULT_MATERIAL_PROFILE.lensOvalization;
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
  readonly sizeScatterFloor?: number;
  readonly sizeScatterSpanMax?: number;
  readonly sizeScatterGainMax2x?: number;
  readonly sizeScatterFloor2x?: number;
  readonly sizeScatterSpanMax2x?: number;
  readonly sizeScatterGainFar2x?: number;
  readonly sizeScatterRampStartThin1x?: number;
  readonly sizeScatterRampStartThick1x?: number;
  readonly sizeScatterRampStartFar1x?: number;
  readonly sizeScatterRampStartThin2x?: number;
  readonly sizeScatterRampStartThick2x?: number;
  readonly sizeScatterRampStartFar2x?: number;
  readonly sizeScatterRampReach1xPx?: number;
  readonly sizeScatterRampReach2xPx?: number;
  readonly sizeOcclusionGain?: number;
  readonly sizeShadowGainMax?: number;
  readonly lensRefractionGain?: number;
  readonly lensHeightPerSpan?: number;
  readonly lensHeightMax?: number;
  readonly lensAmountPerSpan?: number;
  readonly lensAmountMax?: number;
  readonly lensThicknessReference?: number;
  readonly lensExtentGain?: number;
  readonly lensProfileExponent?: number;
  readonly lensOvalization?: number;
  readonly lensOvalizationSpanMin?: number;
  readonly lensOvalizationSpanMax?: number;
  readonly reducedTransparencyFrost?: number;
  readonly increasedOcclusionLift?: number;
  readonly strongBorderRim?: Readonly<Partial<MaterialRim>>;
  readonly reducedTintAdaptation?: number;
  readonly tintShadeDark?: number;
  readonly tintShadeLight?: number;
  readonly tintShadeStrength?: number;
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
 * The names `outerShadow` no longer answers to, and what each was replaced by.
 *
 * `occlusion` was W8's single span-flat amplitude, and it is the leaf a caller
 * reaches for to stand the facet down (`{ outerShadow: { occlusion: 0 } }`).
 * W14 G1 retired it: the amplitude is a two-regime law now, and a patch naming
 * the retired leaf would type-check nowhere but pass through JSON, get hashed
 * into a capture cell as the configuration that ran, and render the DEFAULT
 * shadow — a silently-measured-the-defaults failure of exactly the shape
 * `capture-web.ts`'s unknown-key guard exists for, one level deeper.
 *
 * It is refused rather than mapped. A span-flat scalar is the material the
 * measurement retired: there is no value of it that reproduces 0.33 below the
 * knee and 0.544 above it, so translating one would be inventing a reading, and
 * the project carries no compatibility shims.
 */
const RETIRED_OUTER_SHADOW_LEAVES: Readonly<Record<string, string>> = {
  occlusion:
    "the six amplitude anchors (thinOcclusionDark, thinOcclusionMid, " +
    "thinOcclusionBright, thickOcclusionAt96, thickOcclusionAt128, " +
    "thickOcclusionAt160) and liftAmplitude for the second term",
};

/** Throw if an `outerShadow` patch names a leaf W14 G1 retired (claims §5.62). */
function rejectRetiredOuterShadowLeaves(patch: object | undefined): void {
  if (patch === undefined) return;
  for (const [leaf, replacement] of Object.entries(RETIRED_OUTER_SHADOW_LEAVES)) {
    if (!(leaf in patch)) continue;
    throw new Error(
      `outerShadow.${leaf} was retired by W14 G1 (claims §5.62) and is replaced by ` +
        `${replacement}. Applying this patch would have rendered the default shadow ` +
        `while recording itself as configured. It is refused rather than mapped: a ` +
        `single span-flat amplitude is the material the measurement retired.`,
    );
  }
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
  rejectRetiredOuterShadowLeaves(patch.outerShadow);

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
    sizeScatterFloor: patch.sizeScatterFloor ?? base.sizeScatterFloor,
    sizeScatterSpanMax: patch.sizeScatterSpanMax ?? base.sizeScatterSpanMax,
    sizeScatterGainMax2x: patch.sizeScatterGainMax2x ?? base.sizeScatterGainMax2x,
    sizeScatterFloor2x: patch.sizeScatterFloor2x ?? base.sizeScatterFloor2x,
    sizeScatterSpanMax2x: patch.sizeScatterSpanMax2x ?? base.sizeScatterSpanMax2x,
    sizeScatterGainFar2x: patch.sizeScatterGainFar2x ?? base.sizeScatterGainFar2x,
    sizeScatterRampStartThin1x:
      patch.sizeScatterRampStartThin1x ?? base.sizeScatterRampStartThin1x,
    sizeScatterRampStartThick1x:
      patch.sizeScatterRampStartThick1x ?? base.sizeScatterRampStartThick1x,
    sizeScatterRampStartThin2x:
      patch.sizeScatterRampStartThin2x ?? base.sizeScatterRampStartThin2x,
    sizeScatterRampStartThick2x:
      patch.sizeScatterRampStartThick2x ?? base.sizeScatterRampStartThick2x,
    sizeScatterRampStartFar1x: patch.sizeScatterRampStartFar1x ?? base.sizeScatterRampStartFar1x,
    sizeScatterRampStartFar2x: patch.sizeScatterRampStartFar2x ?? base.sizeScatterRampStartFar2x,
    sizeScatterRampReach1xPx: patch.sizeScatterRampReach1xPx ?? base.sizeScatterRampReach1xPx,
    sizeScatterRampReach2xPx: patch.sizeScatterRampReach2xPx ?? base.sizeScatterRampReach2xPx,
    sizeOcclusionGain: patch.sizeOcclusionGain ?? base.sizeOcclusionGain,
    sizeShadowGainMax: patch.sizeShadowGainMax ?? base.sizeShadowGainMax,
    lensRefractionGain: patch.lensRefractionGain ?? base.lensRefractionGain,
    lensHeightPerSpan: patch.lensHeightPerSpan ?? base.lensHeightPerSpan,
    lensHeightMax: patch.lensHeightMax ?? base.lensHeightMax,
    lensAmountPerSpan: patch.lensAmountPerSpan ?? base.lensAmountPerSpan,
    lensAmountMax: patch.lensAmountMax ?? base.lensAmountMax,
    lensThicknessReference: patch.lensThicknessReference ?? base.lensThicknessReference,
    lensExtentGain: patch.lensExtentGain ?? base.lensExtentGain,
    lensProfileExponent: patch.lensProfileExponent ?? base.lensProfileExponent,
    lensOvalization: patch.lensOvalization ?? base.lensOvalization,
    lensOvalizationSpanMin: patch.lensOvalizationSpanMin ?? base.lensOvalizationSpanMin,
    lensOvalizationSpanMax: patch.lensOvalizationSpanMax ?? base.lensOvalizationSpanMax,
    reducedTransparencyFrost: patch.reducedTransparencyFrost ?? base.reducedTransparencyFrost,
    increasedOcclusionLift: patch.increasedOcclusionLift ?? base.increasedOcclusionLift,
    strongBorderRim: { ...base.strongBorderRim, ...patch.strongBorderRim },
    reducedTintAdaptation: patch.reducedTintAdaptation ?? base.reducedTintAdaptation,
    tintShadeDark: patch.tintShadeDark ?? base.tintShadeDark,
    tintShadeLight: patch.tintShadeLight ?? base.tintShadeLight,
    tintShadeStrength: patch.tintShadeStrength ?? base.tintShadeStrength,
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
 * The shade the seed is shown at over a material of luminance `u` (W10) — the
 * CPU statement of what `WGSL_OPTICS_PASS` evaluates per pixel.
 *
 * `u` is the linear luminance of the UNTINTED material at the pixel — what the
 * surface would show with no author tint, backdrop included. `grip` is how much
 * of the excursion is allowed: the contrast regime's `tintToneAdaptation`, the
 * profile's provenance gate `tintShadeStrength`, and `(1 − collapse)` for W7's
 * axis, multiplied by the caller; at 0 the shade is 1 and the layer is the bare
 * seed. Clamped at 1 because a shade brighter than the seed is not a shade — the
 * fitted light end sits just past 1 (claims §5.36).
 *
 * Exported because two other things have to agree with the shader without being
 * it: the CSS tier folds this layer into its one `rgba()`, and the foreground
 * decision has to be taken against the material the surface actually shows. A
 * second implementation is how those two drift, so there is one, here.
 */
export function tintShade(
  materialLuminance: number,
  grip: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const u = Math.min(1, Math.max(0, materialLuminance));
  const shade = Math.min(1, Math.max(0, profile.tintShadeDark + (profile.tintShadeLight - profile.tintShadeDark) * u));
  const k = Math.min(1, Math.max(0, grip));
  return 1 + (shade - 1) * k;
}

/** The opaque layer an author tint paints: the seed at its shade, linear light. */
export function tintShadeLayer(
  seed: Rgb,
  materialLuminance: number,
  grip: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): Rgb {
  const shade = tintShade(materialLuminance, grip, profile);
  return [seed[0] * shade, seed[1] * shade, seed[2] * shade];
}

/**
 * The tinted material's colour once the author's layer composites over it.
 *
 * The layer is opaque and lands at the AUTHOR's opacity (`strength`), in the
 * encoded space — a `CALayer` with `opacity` over the material, which is how the
 * reference's half-strength cell measures (claims §5.36 finding 3). `material`
 * is the untinted composite at this pixel, linear; the result is linear too.
 * At strength 0 the material is returned untouched, so an untinted surface is
 * byte-identical to before this axis existed.
 */
export function tintedMaterialColour(
  material: Rgb,
  tint: { readonly color: Rgb; readonly strength: number } | undefined,
  grip: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): Rgb {
  if (tint === undefined || tint.strength <= 0) return material;
  const s = Math.min(1, Math.max(0, tint.strength));
  const layer = tintShadeLayer(tint.color, relativeLuminance(material), grip, profile);
  const clamp01 = (value: number): number => Math.min(1, Math.max(0, value));
  const channel = (index: 0 | 1 | 2): number => {
    const from = linearToSrgbChannel(clamp01(material[index]));
    const to = linearToSrgbChannel(clamp01(layer[index]));
    return srgbToLinearChannel(from + (to - from) * s);
  };
  return [channel(0), channel(1), channel(2)];
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

/**
 * The inner shadow's size gain — see `MaterialProfile.lensSizeGainMax`. The
 * name is the constant's; the lens has read its own law since W12 G2.
 */
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
 * The inner shadow's depth in CSS px — the law the lens ran on until W12 G2,
 * kept for the occlusion exactly as it was: the thickness times the size gain,
 * clamped to the shorter half extent. `thickness` here is the policy-folded
 * factor (`sizeThicknessUnderPolicy`), as the shader's `sizeK` is.
 */
export function shadowDepthPx(
  thicknessPx: number,
  spanPx: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return Math.min(
    Math.max(thicknessPx, 0) * lensSizeGainFromThickness(thickness, profile),
    spanPx * 0.5,
  );
}

/** The reference's inner refraction height for a span: `min(lensHeightPerSpan · span, lensHeightMax)`. */
export function lensHeightBasePx(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return Math.min(profile.lensHeightPerSpan * Math.max(spanPx, 0), profile.lensHeightMax);
}

/** The reference's inner refraction amount for a span: `min(lensAmountPerSpan · span, lensAmountMax)`. */
export function lensAmountBasePx(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return Math.min(profile.lensAmountPerSpan * Math.max(spanPx, 0), profile.lensAmountMax);
}

/**
 * The lens's ovalization for a span (W12 G2): `lensOvalization` on a thick
 * surface, 0 on a thin one, a smoothstep over the reference's knee between.
 */
export function lensOvalizationAt(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return profile.lensOvalization * smoothstep(profile.lensOvalizationSpanMin, profile.lensOvalizationSpanMax, spanPx);
}

/**
 * The lens's magnitude at the contour, in CSS px (W12 G2): the reference's
 * amount law scaled by the author's thickness and by `lensRefractionGain`,
 * under the same accessibility fold and half-extent clamp the depth takes —
 * see `lensDepthPx`. 44.7 at saturation on the default thickness.
 */
export function lensMagnitudePx(
  thicknessPx: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  fold = 1,
): number {
  const thick = Math.max(thicknessPx, 0);
  if (thick <= 0) return 0;
  const scale = thick / profile.lensThicknessReference;
  // The height and the amount are scaled together; a clamped depth scales the
  // amount by the same ratio so the profile's shape survives the clamp.
  const unclamped = thick + (lensHeightBasePx(spanPx, profile) * scale - thick) * fold;
  const depth = lensDepthPx(thicknessPx, spanPx, profile, fold);
  const amount = thick + (lensAmountBasePx(spanPx, profile) * scale - thick) * fold;
  return profile.lensRefractionGain * amount * (unclamped > 0 ? depth / unclamped : 0);
}

/** The lens profile's extent: D reaches zero `lensExtentGain` lens depths in. */
export function lensExtentPx(
  thicknessPx: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  fold = 1,
): number {
  return profile.lensExtentGain * lensDepthPx(thicknessPx, spanPx, profile, fold);
}

/**
 * The direction the lens displaces along at a pixel (W12 G2): the gradient of
 * the blended field `(1 − ω)·d_rrect + ω·d_oval`, where `d_oval` is the signed
 * distance of the ellipse inscribed in the surface's box —
 * `min(a, b)·(√((x/a)² + (y/b)²) − 1)` — and the rounded rectangle's gradient is
 * the field pass's unit normal. `offset` is the pixel relative to the surface's
 * centre and `half` the half-extents, both in CSS px. Returns a unit vector;
 * the shader's arithmetic, on the CPU for the tests.
 */
export function lensDirection(
  normal: readonly [number, number],
  offset: readonly [number, number],
  half: readonly [number, number],
  ovalization: number,
): [number, number] {
  const a = Math.max(half[0], 1e-6);
  const b = Math.max(half[1], 1e-6);
  const ex = offset[0] / (a * a);
  const ey = offset[1] / (b * b);
  const r = Math.max(Math.hypot(offset[0] / a, offset[1] / b), 1e-6);
  const scale = Math.min(a, b) / r;
  const gx = (1 - ovalization) * normal[0] + ovalization * ex * scale;
  const gy = (1 - ovalization) * normal[1] + ovalization * ey * scale;
  const len = Math.hypot(gx, gy);
  return len > 1e-9 ? [gx / len, gy / len] : [normal[0], normal[1]];
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
 *
 * `devicePixelRatio` reaches the ramp's projection — the ramp's start and reach
 * and, since W15 G1, the deep value's floor and span top are per-scale
 * constants — and the heavy width's gain, but never the width itself, which is
 * CSS px at every scale in this shared projection (see `sizeScatterSigmaAt`).
 * It defaults to 1, where the whole expression is the 1x law.
 *
 * The span reaches the gain as well as the mix since W15 G1's re-form (claims
 * §5.70 §4 and §7): the reference's heavy kernel grows with the span, so this
 * hands `spanPx` on to `sizeScatterSigmaAt`. At dpr ≤ 1 that grading is flat and
 * the σ is what it always was.
 */
export function sizeScatterSigma(
  sigmaPx: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
  extentsCssPx?: readonly [number, number],
): number {
  return sizeScatterSigmaAt(
    sigmaPx,
    scatterThickness(spanPx, 1, profile, devicePixelRatio, extentsCssPx),
    profile,
    devicePixelRatio,
    spanPx,
  );
}

/**
 * **The depth ramp's start at a device scale and a span** — s₀(span, dpr), the
 * sharp component's share at the contour (W13 G1, claims §5.61 §2, §5.64 §5).
 *
 * ```
 * s₀(span, dpr) = startThin(dpr) + (startThick(dpr) − startThin(dpr)) · sizeThickness(span)
 * ```
 *
 * Two gradings, and they are different quantities. **In dpr**: the reference
 * was read at dpr 1 and dpr 2 and nowhere between, so each anchor is
 * interpolated linearly between its two readings and held outside [1, 2],
 * because an extrapolation of a two-point fit past its own anchors would be an
 * invention rather than a measurement. **In span**: G0 read the start much
 * higher on the thin surfaces than on the thick ones, and the curve it grades
 * along is `sizeThickness` — the material's existing knee at 64, not a new
 * statistic. A single start per scale was the second form and its sweep refuted
 * it (claims §5.64 §2). And past that knee the start keeps FALLING, along the
 * scatter facet's own curve to `far` at `sizeScatterSpanMax` — the fourth form,
 * from the third's one holdout failure (claims §5.67 §4).
 *
 * `scatterRampReachDevicePx` carries the dpr rule on the reach; the two are
 * separate functions so a sweep can move one without the other, and the reach
 * has no span grading because it measured as one length (§5.61 §2).
 */
export function scatterRampStart(
  devicePixelRatio: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  spanPx = 0,
): number {
  const thin = rampAtScale(
    profile.sizeScatterRampStartThin1x,
    profile.sizeScatterRampStartThin2x,
    devicePixelRatio,
  );
  const thick = rampAtScale(
    profile.sizeScatterRampStartThick1x,
    profile.sizeScatterRampStartThick2x,
    devicePixelRatio,
  );
  const far = rampAtScale(
    profile.sizeScatterRampStartFar1x,
    profile.sizeScatterRampStartFar2x,
    devicePixelRatio,
  );
  // The fourth form (W13 Decision Log 6): past the thickness knee the start keeps
  // falling along the scatter facet's own curve, from the thick anchor at
  // `sizeSpanMax` to `far` at `sizeScatterSpanMax`. Same curve the deep value
  // rises along, so the two are one span statistic read twice.
  const decline = smoothstep(
    profile.sizeSpanMax,
    scatterSpanMaxAtScale(profile, devicePixelRatio),
    spanPx,
  );
  return thin + (thick - thin) * sizeThickness(spanPx, profile) + (far - thick) * decline;
}

/**
 * **The depth ramp's reach at a device scale**, in DEVICE px — U(dpr), the depth
 * at which the sharp share would reach zero if it started at 1 (W13 G1).
 *
 * In device pixels because that is how it measured: the per-span reaches in
 * absolute depth spread by 1.3× where the reaches as a fraction of the half-span
 * spread by 2.2×, and between the two scales the length roughly halves in CSS px
 * — one length in device pixels fits both beds where one in CSS px does not
 * (claims §5.61 §2). Callers working in CSS px divide by the same dpr.
 */
export function scatterRampReachDevicePx(
  devicePixelRatio: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return rampAtScale(
    profile.sizeScatterRampReach1xPx,
    profile.sizeScatterRampReach2xPx,
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
 * **The heavy width's gain at a device scale** (W15 G1, claims §5.69 §1).
 *
 * The gain multiplies the sharp width to give the heavy component's σ, and the
 * reference's heavy component is a different width at 2x than the 1x gain of 8
 * makes it once the sharp width is read in device pixels. Interpolated by
 * `rampAtScale`, so a profile that names only the 1x gain returns it at every
 * ratio and this function is the identity on the landed material.
 */
export function scatterGainAtScale(
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
): number {
  return rampAtScale(profile.sizeScatterGainMax, profile.sizeScatterGainMax2x, devicePixelRatio);
}

/**
 * **The heavy width's gain at the top of the scatter span curve, at a device
 * scale** (W15 G1's re-form, claims §5.70 §4 and §7).
 *
 * The far end of `scatterGainAt`'s span grading. Interpolated from
 * `sizeScatterGainMax` — the 1x gain — rather than from the 2x one, which is
 * what makes the whole grading inert at dpr 1: there the far gain and the base
 * gain are the same number, so the curve between them is flat whatever
 * `sizeScatterGainFar2x` says.
 */
export function scatterGainFarAtScale(
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
): number {
  return rampAtScale(profile.sizeScatterGainMax, profile.sizeScatterGainFar2x, devicePixelRatio);
}

/**
 * **The heavy width's gain at a span and a device scale** (W15 G1's re-form,
 * claims §5.70 §4 and §7) — the width law the body's heavy component actually
 * runs at.
 *
 * ```
 * gain(span, dpr) = gainAtScale(dpr)
 *                 + (gainFar(dpr) − gainAtScale(dpr))
 *                   · smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span)
 * ```
 *
 * The reference's heavy kernel GROWS with the span — 8.0 / 7.5 / 8.0 / 9.0 /
 * 11.0 device px across the bed (claims §5.69 §1) — and W15 G1's first landing
 * carried one number for it, which left the largest span's deep interior 40%
 * too structured (§5.70 §4). The curve the gain grades along is the one the
 * fourth form's far anchor already declines along, from `sizeSpanMax` to
 * `sizeScatterSpanMax` at scale, so the width and the ramp's start are one span
 * statistic read twice and no new knee enters the material.
 *
 * At dpr ≤ 1 both ends are `sizeScatterGainMax` and this is that constant at
 * every span, which is the binding rule of the wave expressed as arithmetic.
 */
export function scatterGainAt(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
): number {
  const near = scatterGainAtScale(profile, devicePixelRatio);
  const far = scatterGainFarAtScale(profile, devicePixelRatio);
  if (far === near) return near;
  return (
    near
    + (far - near)
      * smoothstep(
        profile.sizeSpanMax,
        scatterSpanMaxAtScale(profile, devicePixelRatio),
        spanPx,
      )
  );
}

/**
 * **The scatter facet's frost at a device scale** (W15 G1, claims §5.69 §2) —
 * the deep value's floor, and the value the whole facet folds to.
 *
 * One function rather than two reads of the profile, because the floor is read
 * in three places that must agree: the deep curve below, the fold in
 * `scatterThickness`, and the uniform the shader takes for both.
 */
export function scatterFloorAtScale(
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
): number {
  return clampUnit(
    rampAtScale(profile.sizeScatterFloor, profile.sizeScatterFloor2x, devicePixelRatio),
  );
}

/**
 * **The deep value's span top at a device scale** (W15 G1, claims §5.69 §2) —
 * the span at which the deep value reaches 1, fully heavy.
 *
 * It is one span statistic read twice, here as at 1x: the deep curve rises to
 * it and the ramp's start declines to `far` along the same smoothstep, so a
 * sweep that moves the top at 2x moves both together, which is the relation the
 * fourth form was built on (`scatterRampStart`).
 */
export function scatterSpanMaxAtScale(
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
): number {
  return rampAtScale(profile.sizeScatterSpanMax, profile.sizeScatterSpanMax2x, devicePixelRatio);
}

/**
 * **The span law that supplies the ramp's deep value** — kDeep(span), the heavy
 * share the body mixes by everywhere deeper than the ramp's reach (W11c G1,
 * claims §5.41; kept underneath the ramp by W13 G1).
 *
 * `sizeScatterFloor` + (1 − floor) · smoothstep(`sizeSpanMin`,
 * `sizeScatterSpanMax`, span), unfolded — exactly the curve W11c fitted and W12
 * landed. The accessibility fold is applied once, by `scatterThickness` and by
 * the shader, on the whole mix rather than on this term alone.
 *
 * `devicePixelRatio` reaches the floor and the span top, which are per-scale
 * constants since W15 G1 (claims §5.69 §2: the reference's 2x deep interior is
 * fully heavy on the two largest spans where this curve leaves a sharp share of
 * 0.24–0.36). It defaults to 1, where the whole expression is the 1x law, and
 * the two anchors are equal on the landed material, so every ratio returns that
 * law until the sweep fits the second scale.
 */
export function scatterDeepThickness(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
): number {
  const floor = scatterFloorAtScale(profile, devicePixelRatio);
  return (
    floor
    + (1 - floor)
      * smoothstep(profile.sizeSpanMin, scatterSpanMaxAtScale(profile, devicePixelRatio), spanPx)
  );
}

/**
 * **The sharp component's share at a depth** — s(u, span), the law the GPU
 * tier's optics pass evaluates per pixel (W13 G1, claims §5.61 §2).
 *
 * ```
 * s(u, span) = sDeep(span) + max(0, s₀(span) − sDeep(span)) · max(0, 1 − u / U)
 * ```
 *
 * with `sDeep = 1 − scatterDeepThickness(span)` and `s₀` the span-graded start
 * `scatterRampStart` resolves. Deeper than the reach the
 * surface reads its span law exactly; within it the sharp component is lifted
 * toward the contour value `s₀`. `max(0, s₀ − sDeep)` rather than a signed
 * difference: the excursion is the band the reference has *above* the body, and
 * on a span whose deep sharp share already exceeds `s₀` there is nothing to add
 * — the alternative would quietly make the small spans heavier at the contour
 * than in their own middle, which is the opposite of what §5.61 §2 measured.
 *
 * `uDevicePx` is the pixel's depth under the contour in DEVICE pixels, which is
 * the field's own signed distance (negative inside) read in CSS px and
 * multiplied by the ratio the tier draws at. Zero and negative depths — the
 * contour and everything outside it — read the start value, because the body
 * outside the silhouette is not drawn at all.
 *
 * The heavy share the body mixes by is 1 − s(u, span), before the accessibility
 * fold `scatterThickness` and the shader apply.
 */
export function scatterSharpShare(
  uDevicePx: number,
  devicePixelRatio: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  spanPx = 0,
): number {
  const deepSharp = 1 - scatterDeepThickness(spanPx, profile, devicePixelRatio);
  const start = scatterRampStart(devicePixelRatio, profile, spanPx);
  const reach = Math.max(scatterRampReachDevicePx(devicePixelRatio, profile), 1e-6);
  const excursion = Math.max(start - deepSharp, 0) * Math.max(1 - Math.max(uDevicePx, 0) / reach, 0);
  return clampUnit(deepSharp + excursion);
}

/**
 * **The scattering facet's input** — how far toward its heavy blur a surface of
 * this span mixes ON AVERAGE, 0…1: the depth ramp's projection onto one number
 * per surface (W13 G1; the binding rule "the span law is the ramp's projection,
 * on both tiers").
 *
 * The GPU tier mixes per pixel and needs no projection; every other consumer
 * does — the CSS tier's single `blur()` σ, the sampling proxy's 3σ padding
 * floor, the demo's law readout — and if each of them invented its own the two
 * tiers would scatter differently. So this is the area average of the ramp over
 * the surface. Because the ramp now rides on the span law rather than replacing
 * it, the average is that law minus the excursion's average, and on a surface
 * far larger than the reach it is the span law almost exactly — which is what
 * keeps the CSS tier's large spans where W11c and W12 put them.
 *
 * `fold` is the accessibility fold every facet takes (the refraction ladder read
 * at the preference's cap, `sizeThicknessUnderPolicy`'s factor). It scales the
 * excursion away from `sizeScatterFloor` and NOT the floor itself: the floor is
 * the frost the material has at any size, the rest is depth a preference is
 * entitled to remove. At fold 1 this is the ramp's own average and at fold 0 it
 * is the floor exactly.
 *
 * Mirrored by `@vitreajs/vitrea-web`'s `scatterThickness`, pinned by
 * `packages/calibration/test/tier-coherence.test.ts` over spans, folds and dpr.
 */
export function scatterThickness(
  spanPx: number,
  fold: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
  extentsCssPx?: readonly [number, number],
): number {
  const floor = scatterFloorAtScale(profile, devicePixelRatio);
  const mean = scatterRampAreaMean(spanPx, profile, devicePixelRatio, extentsCssPx);
  return clampUnit(floor + (mean - floor) * fold);
}

/**
 * The unfolded area average of the heavy share over a surface — the integral
 * `scatterThickness` documents, separated so a reader can check the closed form
 * against a quadrature and so the fold stays one multiplication.
 *
 * The average is exact rather than sampled. The heavy share at depth u is
 * `kDeep(span) − A · T(u)` with `A = max(0, s₀ − sDeep)` the excursion's
 * amplitude and `T(u) = max(0, 1 − u / R)` its triangle in depth, so the area
 * average is `kDeep − A · T̄` and only `T̄` has to be integrated — the amplitude
 * is one number per surface even though the start grades with span, because a
 * surface has one span. On a rectangle
 * the area at depth ≥ u is `(W − 2u)(H − 2u)`, so the area *at* depth u has
 * measure `P − 8u` with `P = 2(W + H)`, and
 *
 * ```
 * T̄ = (1 / WH) ∫₀^{min(R, min(W,H)/2)} (1 − u / R) · (P − 8u) du
 *    = (1 / WH) · [ P·m − 4m² − P·m² / (2R) + (8/3)·m³ / R ]
 * ```
 *
 * with `m` that upper limit: a surface shallower than the reach integrates only
 * the depth it has. The corners are ignored — a rounded rect's erosion keeps the
 * corner radius shrinking with the depth and the exact measure differs from
 * `P − 8u` only inside the corner quarter-disks — which is the same
 * approximation the spec's design states and costs less than the ramp's own
 * measurement error.
 *
 * `extentsCssPx` is the surface's own width and height where the caller has
 * them. Where it does not — and most callers do not, because a group's law is
 * taken over its *widest member's span* and a span is one number — the surface
 * is taken to be a square of the span, which is the honest reading of "a
 * surface of this span" and is exactly right on the calibration bed's square
 * components.
 */
export function scatterRampAreaMean(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
  extentsCssPx?: readonly [number, number],
): number {
  const deep = scatterDeepThickness(spanPx, profile, devicePixelRatio);
  const amplitude = Math.max(scatterRampStart(devicePixelRatio, profile, spanPx) - (1 - deep), 0);
  if (amplitude <= 0) return clampUnit(deep);
  const width = Math.max(extentsCssPx?.[0] ?? spanPx, 0);
  const height = Math.max(extentsCssPx?.[1] ?? spanPx, 0);
  const area = width * height;
  if (area <= 0) return clampUnit(deep - amplitude);
  // The reach in CSS px, which is the unit the depth arrives in: u_device / U =
  // u_css · dpr / U, so the CSS-space reach is U / dpr and the ratio is the same
  // number the shader computes.
  const reach = Math.max(
    scatterRampReachDevicePx(devicePixelRatio, profile) / Math.max(devicePixelRatio, 1e-3),
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
  return clampUnit(deep - amplitude * triangleMean);
}

/**
 * The same, for a caller that has already resolved the scatter thickness — which
 * is every caller with a policy to fold under.
 *
 * The two-function shape is deliberate and it is mirrored on the CSS tier: the
 * thickness form is the law, the span form is the convenience that computes an
 * unfolded thickness for it. One formula, so a policy fold cannot end up applied
 * to one facet and not another.
 *
 * **The ratio never divides this σ.** W12 G3 read the widths as device-pixel
 * quantities (claims §5.56 §1) and this form divided by the ratio; W13 Decision
 * Log 8 (user-decided, 2026-09-04) retired that on the bed, and W15 G1 restores
 * the device-pixel reading on the GPU tier alone, where the renderer's
 * `bodySigmaCssFor` divides the sharp width by the viewport's own ratio. This
 * function is the SHARED projection — the CSS tier's single `blur()` σ, a
 * group's 3σ padding floor, the demo's readout — and W15 Decision Log 2 leaves
 * W13 Decision Log 5 in force until G1 predicts the CSS tier's 2x σ, so a
 * division here would move the CSS tier the way claims §5.69 §4 says is wrong
 * (its own measured 2x ceiling is 3–5 CSS px, LARGER than the 1x reading, not
 * half of it).
 *
 * What the ratio does reach is the GAIN: `sizeScatterGainMax2x` is the heavy
 * width's multiplier at dpr 2 (claims §5.69 §1), so at mix 0 this returns
 * `sigmaPx` at every ratio and at mix 1 it returns the ratio's own heavy width.
 * On the landed material the two gains are equal and every ratio returns the 1x
 * σ, which is what `tier-coherence` pins.
 *
 * `spanPx` is OPTIONAL and it selects which gain: given, the span-graded one
 * `scatterGainAt` resolves (W15 G1's re-form, claims §5.70 §4 and §7); omitted,
 * the flat `scatterGainAtScale`. The two are the same number at every span at
 * dpr ≤ 1 and on any profile whose far gain equals its base gain, so a caller
 * that has no span — `css-tier.ts`'s single `blur()`, the demo's readout —
 * keeps exactly the meaning it had, and a caller that has one gets the width
 * the reference's own kernel has at that span. The parameter rather than a
 * second function because this is the mix's own end point and there is one of
 * it.
 */
export function sizeScatterSigmaAt(
  sigmaPx: number,
  scatter: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  devicePixelRatio = 1,
  spanPx?: number,
): number {
  const mix = clampUnit(scatter);
  const gain =
    spanPx === undefined
      ? scatterGainAtScale(profile, devicePixelRatio)
      : scatterGainAt(spanPx, profile, devicePixelRatio);
  return sigmaPx * (1 + (gain - 1) * mix);
}

/** 0…1, the clamp every share in this facet takes. */
function clampUnit(value: number): number {
  return Math.min(1, Math.max(0, value));
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
 * Where the thin regime's three amplitude anchors sit on the backdrop luminance
 * axis, and where the two interpolations between them run (W14 G1).
 *
 * The axis is the SAME statistic W9's face response keys on — the backdrop's
 * ENCODED-space mean, decoded to a linear luminance — which is the charter's
 * third binding rule ("no second luminance statistic is introduced for the
 * shadow"). `MaterialProfile.backdropToneAnchorX` names the same three solids in
 * the encoded space: 0.1104 / 0.2706 / 0.9505 encoded are 0.0117 / 0.0595 /
 * 0.891 linear, which is `inert` / `midFrom` / `bright` below.
 *
 * `midFrom` … `midTo` is a plateau the bed MEASURED at four backdrops
 * (`mid-dark-solid` 0.06, checkerboard and `photo` in between, `hc-text` 0.74),
 * flat to 0.02 in occlusion. The two interpolations either side of it are
 * **declared choices, not measurements**, and the bed does not constrain either:
 *
 *  - `midTo` → `bright` (0.74 → 0.891) is taken LINEAR in luminance. The bed
 *    jumps straight from `hc-text` to `light-solid` with nothing between, and
 *    the whole factor-of-2.6 drop happens in that gap (claims §5.62, W14
 *    Deferred: "one backdrop between them would pin it"). A linear ramp is the
 *    least-committed curve through two endpoints; a smoothstep would assert a
 *    knee at each end that nothing measured.
 *  - `inert` → `midFrom` (0.02 → 0.06) is taken by SMOOTHSTEP. Below `inert` the
 *    reference removes at most one or two of 255 codes and the compare's shadow
 *    axis reports nothing at all (its backdrop floor is 0.05), so this ramp is
 *    unmeasured over its whole length; it is a smoothstep so that the facet
 *    arrives with a zero derivative at the black end and a scene fading from
 *    `dark-solid` to `mid-dark-solid` does not show the shadow switching on.
 */
export const OUTER_SHADOW_THIN_L = {
  /** At and below this backdrop luminance the black term is `thinOcclusionDark`. */
  inert: 0.02,
  /** From here the mid plateau holds. */
  midFrom: 0.06,
  /** To here — `hc-text`'s own linear luminance. */
  midTo: 0.74,
  /** `light-solid`'s linear luminance, where 0.127 was measured; held above. */
  bright: 0.891,
} as const;

/**
 * The backdrop luminance the law reads where the host measured none.
 *
 * Neither tier can adapt a shadow to a backdrop nobody declared or sampled, and
 * guessing black would delete the facet on every unsampled surface while
 * guessing white would halve it. The mid plateau is what four of the bed's seven
 * backdrops sit on and what W8's single amplitude was a compromise across, so an
 * unmeasured group keeps the closest thing to the shadow it had.
 */
export const OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE = 0.3;

/**
 * The black term's peak occlusion below the knee, at a backdrop luminance — see
 * `OUTER_SHADOW_THIN_L` for the anchors and for which parts of this curve are
 * measured and which are declared.
 */
export function outerShadowThinOcclusion(
  backdropLuminance: number | undefined,
  shadow: MaterialOuterShadow,
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

/** The three spans the thick regime's anchors were read at, CSS px (claims §5.62 §4). */
export const OUTER_SHADOW_THICK_SPANS = [96, 128, 160] as const;

/**
 * The composite's peak occlusion above the knee, at a casting span — piecewise
 * linear through the three measured anchors and held flat outside them.
 *
 * Held rather than extrapolated at both ends: below 96 the thin regime is what
 * the blend is walking away from and an extrapolated line would cross it, and
 * above 160 the bed has no cell at all, where the measured rise is already
 * flattening (0.379 → 0.497 → 0.544 costs 0.118 over the first 32 px of span and
 * 0.047 over the next 32).
 *
 * Not keyed on the backdrop, unlike the thin regime: the anchors are the
 * composite's transmission measured on the checkerboard, and the bed has no
 * thick cell over a dark backdrop to key against (claims §5.62 §4 — a span-128
 * or 160 surface over `impulse` would separate the composite's two terms, and
 * that scene does not exist). The dark PROFILE carries its own three anchors.
 *
 * **What it costs where it is wrong, measured.** An earlier form of this comment
 * claimed it costs nothing visible, on the argument that a multiply over a
 * near-black backdrop removes near-nothing whatever its amplitude. X7's affine
 * pair contradicts that argument on the one calibration cell that tests it:
 * `dark-solid__rrect-md`, a span-96 surface over a backdrop of linear 0.0117,
 * where vitrea now removes 0.1645 at the `3-6` band against the reference's
 * 0.1094 and against the 0.1260 the W12 close removed — the thick path over a
 * near-black backdrop went from 15% light to **50% heavy** (claims §5.65 §5).
 * In absolute terms it is 0.7 of a code and no perceptual row in the matrix
 * notices, so it is a small error, not an invisible one; it is recorded as a gap
 * and it closes with a thick cell over a dark backdrop to key against.
 */
export function outerShadowThickOcclusion(
  spanPx: number,
  shadow: MaterialOuterShadow,
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
 * The outer shadow's peak LINEAR occlusion for one casting surface (W14 G1) —
 * the thin regime's backdrop-keyed amplitude, the thick regime's span law, and
 * the size law's gain, in that order.
 *
 * `thickness` is the size law's own curve for the casting surface, folded under
 * the accessibility policy exactly as every other span-dependent facet folds it
 * (`sizeThicknessUnderPolicy`); the blend between the two regimes is the
 * smoothstep of it — the SAME curve `backdropToneResponse` blends its thin and
 * thick rows across, so the shadow's knee and the face's knee are one knee.
 *
 * `backdropLuminance` is the statistic W9's response keys on, and `undefined`
 * means the host measured no backdrop — see
 * `OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE`.
 */
export function outerShadowOcclusionAt(
  shadow: MaterialOuterShadow,
  backdropLuminance: number | undefined,
  spanPx: number,
  thickness: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const thin = outerShadowThinOcclusion(backdropLuminance, shadow);
  const thick = outerShadowThickOcclusion(spanPx, shadow);
  const k = Math.min(1, Math.max(0, thickness));
  const blend = k * k * (3 - 2 * k);
  return sizeOuterShadowOcclusionAt(thin + (thick - thin) * blend, thickness, profile);
}

/**
 * The lift's span rise, 0…1 — the fraction of `liftAmplitude` a surface of this
 * casting span adds. Zero at and below `liftSpanMin`, one at and above
 * `liftSpanFull`, a smoothstep between; see `MaterialOuterShadow.liftSpanFull`
 * for why a smoothstep rather than the layer tree's own linear clamp.
 */
export function outerShadowLiftRise(spanPx: number, shadow: MaterialOuterShadow): number {
  return smoothstep(shadow.liftSpanMin, shadow.liftSpanFull, spanPx);
}

/**
 * The outer shadow under an accessibility regime.
 *
 * One branch per axis that can reach it, on `opticsUnderPolicy`'s rule. `frost`
 * is the axis reduced transparency alone sets, and the amplitude it lands on is
 * measured — see `MaterialOuterShadow.reducedTransparencyOcclusion`. Under
 * forced colours the material is gone, so its shadow goes with it rather than
 * outliving the surface that cast it.
 *
 * The fold writes ONE amplitude into all six anchors rather than scaling them,
 * because that is what the reference does: under the preference its exterior is
 * flat at 0.192–0.202 thin and thick together and over every backdrop, so the
 * law's two regimes collapse onto one level and neither the backdrop keying nor
 * the span rise survives (claims §5.62 §5). Flattening the anchors here keeps
 * one folded `MaterialOuterShadow` as the single value every caller resolves
 * from, and the resolved occlusion is then that level for any span, any backdrop
 * and any thickness, since a blend between equal ends is the end. The LIFT
 * stands down with them — a composite whose two regimes read the same number has
 * no second term in it.
 */
export function outerShadowUnderPolicy(
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): MaterialOuterShadow {
  const shadow = profile.outerShadow;
  if (policy.glass === "none" || policy.frost === "none") return flatOuterShadow(shadow, 0);
  if (policy.frost === "increased") {
    return flatOuterShadow(shadow, shadow.reducedTransparencyOcclusion);
  }
  return shadow;
}

/** Every amplitude anchor set to `amplitude`, with the lift stood down. */
function flatOuterShadow(shadow: MaterialOuterShadow, amplitude: number): MaterialOuterShadow {
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
 * `occlusion` must be the EFFECTIVE amplitude — after the accessibility fold,
 * after the backdrop key and the span law, and after the size law — which is the
 * caller's to resolve, because only it knows the group's membership and the
 * backdrop it sits over. A pad taken from the base amplitude while the shader
 * emits an amplified one slices the deepest surface's shadow off at the scissor,
 * while the CSS tier, which has no scissor, goes on drawing it. It is a separate
 * argument since W14 G1, because a `MaterialOuterShadow` no longer carries one
 * amplitude to read.
 *
 * The solve runs over the signed distance to the shadow's OWN silhouette, which
 * may be negative — a pixel just outside the contour is already inside the
 * offset, spread silhouette — so `occlusion = 0`, and any amplitude too faint to
 * move a code anywhere, both fall out as a reach of zero rather than needing a
 * case of their own.
 */
export function outerShadowReachPx(shadow: MaterialOuterShadow, occlusion: number): number {
  const alpha = outerShadowAlpha(occlusion);
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

/**
 * The lens depth in CSS px (W12 G2): the reference's own height law,
 * `min(lensHeightPerSpan · span, lensHeightMax)`, scaled by the author's
 * thickness over `lensThicknessReference`, clamped to the shorter half extent.
 * 8 / 11 / 20 on spans 32 / 44 / ≥ 80 at the default thickness — the numbers
 * read from the reference's layer tree (claims §5.50).
 *
 * `fold` is the accessibility regime's factor on the size-dependent part (the
 * refraction ladder at the preference's cap, `sizeThicknessUnderPolicy`'s
 * factor): at 1 the depth is the law's, at 0 it is the authored thickness and
 * nothing more — the same shape the W2 law folded by, so a reduced regime
 * keeps the lens it had.
 */
export function lensDepthPx(
  thicknessPx: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  fold = 1,
): number {
  const thick = Math.max(thicknessPx, 0);
  const scale = thick / profile.lensThicknessReference;
  const depth = thick + (lensHeightBasePx(spanPx, profile) * scale - thick) * fold;
  return Math.min(Math.max(depth, 0), spanPx * 0.5);
}

/**
 * How far inside the surface the shader reads the body for a pixel `depthPx`
 * in from the contour (W12 G2), in CSS px — `S · max(0, 1 − depthPx / L′)^p`
 * with `S = lensMagnitudePx`, `L′ = lensExtentPx` and `p` the profile's
 * exponent, times the refraction scale the policy resolved. At the default
 * thickness on a 96 px span: 33.7 / 24.3 / 11.9 at 2 / 4 / 8 px in, zero from
 * 26.7 px in — the reference's crossings read 34 / 24 / 12 (claims §5.49).
 */
export function lensDisplacementPx(
  depthPx: number,
  spanPx: number,
  thicknessPx: number,
  refractionScale: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
  fold = 1,
): number {
  const extent = lensExtentPx(thicknessPx, spanPx, profile, fold);
  if (extent <= 0) return 0;
  const t = Math.max(0, 1 - Math.max(depthPx, 0) / extent);
  return (
    lensMagnitudePx(thicknessPx, spanPx, profile, fold) *
    Math.pow(t, profile.lensProfileExponent) *
    refractionScale
  );
}
