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
   * PROVISIONAL — the value is G0's measurement (claims §5.62 §4: linear
   * occlusion 0.379 on the checkerboard at span 96) and the sweep refines it,
   * because what G0 could identify at the bed's noise floor is the composite
   * transmission and the lift's peak amplitude, not the split into (black alpha,
   * vibrant alpha, vibrant colour): both terms ride one falloff and their shapes
   * correlate at 0.9998. So this constant is the BLACK term of a two-term
   * composite whose second term (`liftAmplitude`) is fitted beside it, and the
   * pair is what the referee reads.
   */
  readonly thickOcclusionAt96: number;
  /** The same at a casting span of 128 CSS px — 0.497 measured, PROVISIONAL for
   * `thickOcclusionAt96`'s reason. */
  readonly thickOcclusionAt128: number;
  /** The same at a casting span of 160 CSS px — 0.544 measured, PROVISIONAL for
   * `thickOcclusionAt96`'s reason. */
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
   * PROVISIONAL: 0.0073 is G0's +0.0038 of LINEAR lift at span 160 divided by
   * the ≈ 0.52 linear luminance the checkerboard's σ-40 blur sits at. The space
   * matters and this wave names it everywhere (claims §5.62 §3): §5.60's +0.039
   * is the same lift read in ENCODED luma. The sweep fits this against the
   * referee together with the three thick anchors.
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
   * PROVISIONAL. The measured rise is 0.52 / 0.96 / 1.00 of the span-160 value
   * at spans 96 / 128 / 160, against the layer tree's clamp((span − 64)/96)
   * = 0.33 / 0.67 / 1.00 — so the lift is NOT proportional to
   * `VibrancyContribution`; it rises and saturates, reaching 96% by span 128
   * (claims §5.62 §2). A smoothstep from `liftSpanMin` to 128 reproduces that
   * shape (0.42 at 96, 1.00 at 128) more nearly than the clamp does; the sweep
   * settles the reach.
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
   * What reduced transparency does to the black term's amplitude — MEASURED, not
   * assumed, which
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
   *
   * W14 G0 re-read it on the wider bed and it stands: under increased contrast
   * and reduced transparency alike the reference's exterior is flat at
   * 0.192–0.202, **thin and thick together** and over every backdrop (claims
   * §5.62 §5). So the fold multiplies all six amplitude anchors, and it also
   * stands the lift DOWN entirely — a preference under which the thick and the
   * thin regimes read the same number has no second term left in it.
   *
   * **The factor itself is now 15% high and is not changed here.** 0.70 was
   * fitted against W8's single 0.285 and reconciled two routes at 0.1995; the
   * mid anchor has moved to 0.33, so the folded amplitude is 0.231 against the
   * reference's directly measured 0.192–0.202. 0.60 would land 0.198. W14 G1
   * builds the law and does not fit it — the sweep refines this constant with
   * the six anchors, and `outer-shadow.test.ts` pins 0.231 so the gap is a
   * number somebody has to move rather than a rounding nobody sees.
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
   * spans, a band top past 96 — see `sizeScatterFloor`); it now rides its own,
   * from the same `sizeSpanMin`, and this band is untouched by it.
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
   * alone — see `sizeScatterFloor` and `sizeScatterSpanMax` below for the curve
   * it rides. 8: the heavy component of the reference's interior sits near σ 10
   * CSS px against a body σ of 1.25, and the gain sweep has a clear minimum at
   * 8 (RMS 0.0164 against 0.0180 at 6 and 0.0191 at 10 on the probe bed).
   */
  readonly sizeScatterGainMax: number;

  /**
   * **The scattering facet's own curve** (W11c G1, claims §5.41).
   *
   * The reference's interior over structured content is two components, read
   * off the W9 probe bed across four checkerboard pitches and five spans: a
   * sharp one near σ 1.25 CSS px and a heavy one near σ 10, mixed by a share
   * that is already ≈ 0.4 at spans of 32–44 and still rising at 160 (0.52 at
   * 96, 0.64 at 128, 0.76 at 160). `sizeThickness` — zero at `sizeSpanMin` and
   * saturated at `sizeSpanMax` = 96 — can express neither the floor nor a band
   * top past 96, and moving `sizeSpanMax` would move the lens, the occlusion,
   * the inner shadow and W9's thin/thick response rows with it. So the scatter
   * mix rides its own curve:
   *
   * ```
   * kScatter = floor + (1 − floor) · smoothstep(sizeSpanMin, sizeScatterSpanMax, span) · fold
   * ```
   *
   * The floor is the material's own frost and is **not** folded under an
   * accessibility preference; the span-dependent rise is a depth effect and
   * folds like every other facet (`scatterThickness`). Fitted with `rrect-lg`
   * held out: floor 0.40 (0.0175 at 0.3, 0.0174 at 0.45), band top 256 (0.0182
   * at 224, 0.0174 at 320); the held-out cell's residual 0.0366 → 0.0174.
   */
  readonly sizeScatterFloor: number;
  readonly sizeScatterSpanMax: number;

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
    thickOcclusionAt96: 0.379,
    thickOcclusionAt128: 0.497,
    thickOcclusionAt160: 0.544,
    liftAmplitude: 0.0073,
    liftSpanMin: 64,
    liftSpanFull: 128,
    liftBlurSigmaCss: 40,
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
export const SIZE_SCATTER_FLOOR = DEFAULT_MATERIAL_PROFILE.sizeScatterFloor;
export const SIZE_SCATTER_SPAN_MAX = DEFAULT_MATERIAL_PROFILE.sizeScatterSpanMax;
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
    sizeScatterFloor: patch.sizeScatterFloor ?? base.sizeScatterFloor,
    sizeScatterSpanMax: patch.sizeScatterSpanMax ?? base.sizeScatterSpanMax,
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
 */
export function sizeScatterSigma(
  sigmaPx: number,
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return sizeScatterSigmaAt(sigmaPx, scatterThickness(spanPx, 1, profile), profile);
}

/**
 * **The scattering facet's input** (W11c G1): how far toward its heavy blur a
 * surface of this span mixes, 0…1 — `MaterialProfile.sizeScatterFloor`'s curve.
 *
 * `fold` is the accessibility fold every facet takes (the refraction ladder read
 * at the preference's cap, `sizeThicknessUnderPolicy`'s factor). It scales the
 * span-dependent rise and NOT the floor: the floor is the frost the material
 * has at any size, the rise is the depth a preference is entitled to remove.
 *
 * Mirrored by `@vitreajs/vitrea-web`'s `scatterThickness`, pinned by
 * `packages/calibration/test/tier-coherence.test.ts` over spans and folds.
 */
export function scatterThickness(
  spanPx: number,
  fold: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  const floor = Math.min(1, Math.max(0, profile.sizeScatterFloor));
  return floor + (1 - floor) * smoothstep(profile.sizeSpanMin, profile.sizeScatterSpanMax, spanPx) * fold;
}

/**
 * The same, for a caller that has already resolved the scatter thickness — which
 * is every caller with a policy to fold under.
 *
 * The two-function shape is deliberate and it is mirrored on the CSS tier: the
 * thickness form is the law, the span form is the convenience that computes an
 * unfolded thickness for it. One formula, so a policy fold cannot end up applied
 * to one facet and not another.
 */
export function sizeScatterSigmaAt(
  sigmaPx: number,
  scatter: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return sigmaPx * (1 + (profile.sizeScatterGainMax - 1) * scatter);
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
 * that scene does not exist). It costs nothing visible where it is wrong: a
 * multiply over a near-black backdrop removes near-nothing whatever its
 * amplitude, so the over-stated black term over `dark-solid` is 0.379 of 0.0039
 * of linear light. The dark PROFILE carries its own three anchors.
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
 * is the axis reduced transparency alone sets, and the amplitude it multiplies by
 * is measured — see `MaterialOuterShadow.reducedTransparencyOcclusion`. Under
 * forced colours the material is gone, so its shadow goes with it rather than
 * outliving the surface that cast it.
 *
 * The fold multiplies all six amplitude anchors rather than the resolved number,
 * which is the same thing: the law is a convex blend of its anchors in both
 * regimes, so scaling them scales the result exactly, and doing it here keeps
 * one folded `MaterialOuterShadow` as the single value every caller resolves
 * from. The LIFT is stood down rather than scaled — under the preference the
 * reference's thick and thin exteriors read the same flat number, which is a
 * composite with no second term in it (claims §5.62 §5).
 */
export function outerShadowUnderPolicy(
  policy: MaterialPolicyView,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): MaterialOuterShadow {
  const shadow = profile.outerShadow;
  if (policy.glass === "none" || policy.frost === "none") return scaledOuterShadow(shadow, 0);
  if (policy.frost === "increased") {
    return scaledOuterShadow(shadow, shadow.reducedTransparencyOcclusion);
  }
  return shadow;
}

/** Every amplitude anchor times `factor`, with the lift stood down below 1. */
function scaledOuterShadow(shadow: MaterialOuterShadow, factor: number): MaterialOuterShadow {
  return {
    ...shadow,
    thinOcclusionDark: shadow.thinOcclusionDark * factor,
    thinOcclusionMid: shadow.thinOcclusionMid * factor,
    thinOcclusionBright: shadow.thinOcclusionBright * factor,
    thickOcclusionAt96: shadow.thickOcclusionAt96 * factor,
    thickOcclusionAt128: shadow.thickOcclusionAt128 * factor,
    thickOcclusionAt160: shadow.thickOcclusionAt160 * factor,
    liftAmplitude: factor >= 1 ? shadow.liftAmplitude : 0,
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
