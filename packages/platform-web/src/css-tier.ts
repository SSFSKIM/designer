/**
 * The CSS-tier renderer — the presentable fallback.
 *
 * Two doctrines meet here. The repo's effects policy says **the fallback is the
 * design**: this tier is where a browser without WebGPU lands, and it has to look
 * intentional. And S1's undetectable failure class says the same thing from the
 * other side: because no probe can catch "the engine renders nothing", a *missed*
 * demotion must be a fidelity loss rather than a broken UI. Both converge on one
 * rule, which the tests hold: **the surface always paints a real tint and a real
 * border, and never relies on the blur for contrast.** A group whose
 * `backdrop-filter` silently no-ops still reads as a legible surface.
 *
 * The tier applies `backdrop-filter` **in place**, on the host element itself. It
 * builds no proxies at all — which is exactly why `probe-failed` demotes to it
 * (core's note: "the very thing that failed is not on its path"), and why the
 * host's own text and icons stay above the filter without any layering work: an
 * element's `backdrop-filter` filters what is behind it, and its own children
 * paint on top.
 *
 * **This file holds no optical number of its own** (corrective K5). Every one it
 * paints with arrives on `surface.optics`, which `optics.ts` derives from the
 * material profile the root carries — so retuning the material moves this tier
 * too, instead of leaving it two-and-a-bit times more transparent than the GPU
 * tier the way C9a measured it. What is not derived is the *shape* of the
 * mapping from core's resolved policy regimes to declarations — that is
 * §Accessibility, applied, and it stays here.
 */

import type {
  BackdropTone,
  CornerRadii,
  ForegroundMode,
  GlassTint,
  ResolvedAccessibilityPolicy,
} from "@vitreajs/vitrea";

import { GLASS_CHANNEL_PROPERTIES } from "./channels";
import {
  boundedForegroundLevel,
  CSS_TIER_MAPPING,
  cssTierForegroundBounds,
  cssTierForegroundLevel,
  cssShadowBlurRadius,
  MATERIAL_SOURCE_OUTER_SHADOW,
  MATERIAL_SOURCE_SIZE,
  opticsUnderPolicy,
  outerShadowAlpha,
  outerShadowOcclusionAt,
  outerShadowUnderPolicy,
  sizeOcclusionAlphaAt,
  scatterThickness,
  sizeScatterSigmaAt,
  sizeThicknessUnderPolicy,
  type CssTierMapping,
  type MaterialOptics,
  type MaterialSourceOuterShadow,
  type MaterialSourceSize,
  type PolicyFoldConstants,
  type Rgb255,
} from "./optics";
import { accessibilityRefractionCap } from "./refraction";

/** The two ink tokens the adaptive foreground chooses between. */
export const FOREGROUND_INK = { dark: "#1c1c1e", light: "#f5f5f7" } as const;

/** What a surface with nothing to decide from keeps: `color-scheme` decides instead. */
const FOREGROUND_DEFAULT = `light-dark(${FOREGROUND_INK.dark}, ${FOREGROUND_INK.light})`;

/**
 * The custom properties the tier publishes. A GPU-tier surface writes the same
 * names, so an app styling against them does not have to know which tier drew
 * the glass — and the two tiers cannot drift into two vocabularies.
 */
export const CSS_TIER_TOKENS = [
  "--vitrea-tint",
  "--vitrea-occlusion",
  "--vitrea-border-color",
  "--vitrea-blur",
  "--vitrea-foreground",
] as const;

export type CssTierToken = (typeof CSS_TIER_TOKENS)[number];

/** Declarations as a plain record: property name to value, ready for `style.setProperty`. */
export type StyleDeclarations = Record<string, string>;

/**
 * X6's hint, already resolved by core — this tier consumes it, never
 * re-derives it. `tone` is absent whenever core resolved no hint (a
 * `fixed`-mode group, or `author-hint` with nothing to report).
 */
export interface CssTierForegroundHint {
  readonly mode: ForegroundMode;
  readonly tone?: BackdropTone;
  /**
   * X6's optional backdrop luminance, 0..1 linear, passed through from core. When
   * an app gives one the foreground decision uses it; otherwise the tone's coarse
   * reading (`CssTierMapping.toneLuminance`) stands in.
   */
  readonly luminance?: number;
}

export interface CssTierSurface {
  readonly radii: CornerRadii;
  readonly optics: MaterialOptics;
  /**
   * The author tint this surface's `optics` were derived with
   * (`tintedCssOptics`) — the colour is already in there and is not read again
   * here.
   *
   * It travels anyway because one decision needs to know a tint was *declared*
   * rather than calibrated: the ink. See `boundedForegroundLevel`.
   */
  readonly tint?: GlassTint;
  readonly policy: ResolvedAccessibilityPolicy;
  /**
   * The group's resolved foreground adaptation (§Foreground adaptation). Absent
   * is the pre-K4 default: no hint reaches this tier, so it keeps the
   * `light-dark()` fallback unchanged.
   */
  readonly foreground?: CssTierForegroundHint;
  /**
   * The backdrop this surface is actually over, linear 0..1 — X6's declared hint
   * where there is one, otherwise the tone measured from the backdrop source the
   * app supplied (W7). Absent where neither exists.
   *
   * Distinct from `foreground` and strictly wider than it: `hintedBackdropLuminance`
   * answers only for an *author* hint, and the backdrop adaptation can move this
   * surface's material a long way on a tone nobody declared. The ink has to be
   * decided against the material the surface is actually drawing.
   */
  readonly backdropLuminance?: number;
  /**
   * The mapping the optics were derived through. Only its foreground constants
   * are read here — the rest already did their work in `cssTierOptics` — but the
   * two have to be the same document, or the ink would be chosen against a
   * material the surface is not drawing. Defaults to the shipped mapping.
   */
  readonly mapping?: CssTierMapping;
  /**
   * The policy constants of the profile `optics` came from
   * (`resolvedPolicyFold`). Both are patchable and the renderer already draws
   * with the patched values, so a surface whose optics came from a patched
   * profile has to fold the same numbers or this tier would paint a material the
   * GPU tier does not draw. Absent keeps the shipped set.
   */
  readonly policyFold?: PolicyFoldConstants;
  /**
   * The surface's **shorter** border-box extent in CSS px — the size law's input
   * (W2). A larger surface frosts more and occludes more, on this tier as on the
   * GPU one, through the same two functions.
   *
   * Absent means no size law: the declarations come out exactly as they did
   * before the law existed. That is the honest default for a caller who has not
   * measured the host, because this function is pure and cannot measure one
   * itself, and inventing a span would make a small control render as a slab.
   */
  readonly spanPx?: number;
  /**
   * The size-law constants `spanPx` is resolved against — the profile's, when the
   * root carries a patch. Defaults to the shipped mirror, like `mapping`.
   */
  readonly size?: MaterialSourceSize;
  /**
   * The outer shadow's constants (W8) — the profile's, when the root carries a
   * patch. Defaults to the shipped mirror.
   *
   * Unlike the size law this does NOT stand down when absent: the shadow is a
   * facet of the material rather than a function of a measurement the caller may
   * not have, so a surface that declares nothing still casts the shipped one. A
   * profile turns it off, on either tier, by standing its amplitude anchors down
   * — the six of them since W14 G1 replaced W8's single `occlusion` (claims
   * §5.62), and a patch still naming that retired leaf is refused rather than
   * quietly rendering the shipped shadow.
   */
  readonly outerShadow?: MaterialSourceOuterShadow;
}

/**
 * The backdrop level an X6 hint stands for, linear 0..1 — or nothing, where the
 * hint has no single answer to give (a `mixed` tone, a `fixed` or `sampled-async`
 * mode, no hint at all). Shared by both tiers so the *input* to the foreground
 * decision cannot differ between them either.
 */
export function hintedBackdropLuminance(
  hint: CssTierForegroundHint | undefined,
  mapping: CssTierMapping = CSS_TIER_MAPPING,
): number | undefined {
  const tone = hint?.mode === "author-hint" ? hint.tone : undefined;
  if (tone !== "dark" && tone !== "light") return undefined;
  return hint?.luminance ?? mapping.toneLuminance[tone];
}

/**
 * The runtime's ink for one surface, on **either** tier (Decision Log #32(b)).
 *
 * Split out of `cssTierDeclarations` because the decision is not the CSS tier's:
 * it is the runtime's answer to "what ink is readable on the material this group
 * is drawing", and the GPU tier draws a material too. Before this the GPU tier
 * published nothing at all, so an app following the documented
 * `var(--vitrea-foreground, …)` pattern fell back to its own ink there — measured
 * on a dark-hinted surface at WCAG 1.57 against a 4.5 floor, the same failure K5
 * fixed on the CSS tier and for the same reason.
 *
 * `level` is the encoded level behind the glyphs, from `foregroundLevel` in the
 * composite space of whichever tier is drawing. Absent means there was nothing to
 * decide from.
 */
export function foregroundInk(input: {
  readonly policy: ResolvedAccessibilityPolicy;
  readonly level?: number;
  readonly mapping?: CssTierMapping;
}): string {
  const mapping = input.mapping ?? CSS_TIER_MAPPING;
  const { material } = input.policy;

  // forced-colors takes the platform's palette, and it is not a dimmer version of
  // the adaptive answer — it is a different one.
  if (material.glass === "none") return "CanvasText";

  // Accessibility policy outranks the hint: near-monochrome is never overridden.
  return material.foreground === "near-monochrome"
    ? "light-dark(#000, #fff)"
    : input.level === undefined
      ? FOREGROUND_DEFAULT
      : input.level >= mapping.foregroundCrossover
        ? FOREGROUND_INK.dark
        : FOREGROUND_INK.light;
}

/**
 * The ink as the runtime writes it: **the token, and only the token**
 * (Decision Log #34(c)).
 *
 * This used to hand back `color` as well, and the host got both inline. The
 * colour was right and the precedence was wrong: an inline declaration outranks
 * every application rule short of `!important`, so an app styling a glass host
 * lost silently while being told to build on the token published on that same
 * element. The `color` now comes from `ink-stylesheet.ts`, one static
 * `:where()` rule that resolves this very token — so the seam is the mechanism
 * rather than a copy of it, and an app rule that names the host wins.
 */
export function foregroundDeclarations(input: {
  readonly policy: ResolvedAccessibilityPolicy;
  readonly level?: number;
  readonly mapping?: CssTierMapping;
}): StyleDeclarations {
  return { "--vitrea-foreground": foregroundInk(input) };
}

/**
 * Material transitions. Reduced Motion removes elastic overshoot rather than
 * movement, so the transition survives and its easing changes: the spring-ish
 * curve becomes monotonic and the duration shortens (§Motion, Reduced Motion —
 * "shortens morphs to non-elastic interpolation").
 */
const ELASTIC_EASING = "cubic-bezier(0.34, 1.56, 0.64, 1)";
const MONOTONIC_EASING = "cubic-bezier(0.4, 0, 0.2, 1)";
const NOMINAL_DURATION_MS = 240;
const REDUCED_DURATION_MS = 120;

const px = (value: number): string => `${Math.round(value * 100) / 100}px`;

const rgba = (rgb: Rgb255, alpha: number): string =>
  `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${Math.round(alpha * 1000) / 1000})`;

/**
 * Where the gradient samples the renderer's falloff. Five stops over a quadratic
 * is a piecewise-linear approximation whose worst error is `Δ²/8 · |f″|` = 1.6%
 * of the gain — under half a step of 8-bit alpha at the shipped 0.6, and well
 * inside the coherence floor the mapping's own header states.
 */
const GLOW_STOPS = [0, 0.25, 0.5, 0.75, 1] as const;

/**
 * The press illumination, as one background layer (W1/coherence).
 *
 * §Motion's `glow` channel is the fast-attack / slow-decay driver's output, and
 * until this the CSS tier ignored it: the GPU tier's highlight pass drew the
 * glow and this tier drew nothing, so the two tiers agreed on a resting surface
 * and diverged the moment one was held down. The divergence is invisible in the
 * light scheme and enormous in the dark one, for the reason a lerp toward white
 * always is — over a material already at encoded 0.85 it moves the interior by
 * ~2%, over one at 0.26 it nearly doubles it. Measured at 1.96× on
 * `photo__capsule-button__pressed` in both dark profiles.
 *
 * Three things make this a conversion-free reproduction rather than an
 * approximation of one (see `MaterialSourceGlow` for the composite):
 *
 *  - the renderer's fragment is `radial² · glowGain · glow` with
 *    `radial = clamp(1 − d/glowRadiusCss, 0, 1)`, so the stops carry `(1 − t)²`
 *    and the gradient's ending shape carries the radius;
 *  - `glow` stays a `var()` rather than being folded into the number, so the
 *    declarations remain frame-invariant — the browser tracks the driver, and
 *    root.ts's write cache is not defeated once per frame by a moving alpha;
 *  - the press point is the same fallback the renderer takes
 *    (`pressPoint ?? centre`): a binding publishes `--vitrea-press-x/y` in
 *    host-local px, and a surface pressed by anything else glows from its middle.
 *
 * Painted on `background-image` rather than folded into the `background`
 * shorthand deliberately. The channel is an app-writable custom property, and an
 * invalid one poisons the declaration that references it — on the shorthand that
 * would take the tint down with it, and the tint is this tier's contrast floor
 * when `backdrop-filter` no-ops (S1's undetectable failure class).
 *
 * Two residuals, stated rather than hidden. The host wears the press compression
 * as a `transform`, so this radius scales with the element while the renderer's
 * is in viewport px — 0.66px on 44 at the shipped `pressCompressionScale` of
 * 0.015. And a background layer sits *under* the host's own text, where X1 puts
 * the renderer's highlight canvas *over* it: on this tier a press does not light
 * the label. That is the sandwich's asymmetry (the CSS tier has no layer above
 * the semantic host at all), not a choice made here.
 */
function pressGlowLayer(optics: MaterialOptics): string {
  const stops = GLOW_STOPS.map((t) => {
    const falloff = Math.round((1 - t) ** 2 * optics.glowGain * 10000) / 10000;
    const [r, g, b] = optics.glow;
    const alpha =
      falloff === 0 ? "0" : `calc(var(${GLASS_CHANNEL_PROPERTIES.glow}, 0) * ${falloff})`;
    return `rgba(${r}, ${g}, ${b}, ${alpha}) ${t * 100}%`;
  });

  return (
    `radial-gradient(circle ${px(optics.glowRadius)} at ` +
    `var(${GLASS_CHANNEL_PROPERTIES.pressX}, 50%) var(${GLASS_CHANNEL_PROPERTIES.pressY}, 50%), ` +
    `${stops.join(", ")})`
  );
}

/**
 * The declarations for one surface on the CSS tier.
 *
 * Pure: the same surface always yields the same record, which is what makes the
 * accessibility mapping testable without a browser.
 */
export function cssTierDeclarations(surface: CssTierSurface): StyleDeclarations {
  const { policy } = surface;
  const mapping = surface.mapping ?? CSS_TIER_MAPPING;
  const policyOptics = opticsUnderPolicy(surface.optics, policy.material, surface.policyFold);
  /*
   * The size law, applied after the accessibility fold and before anything is
   * written (W2). Two facets reach this tier — a wider blur and a higher tint
   * alpha — and both come from the same functions the GPU tier resolves its own
   * from, so the two tiers cannot scatter or occlude differently for one span.
   *
   * A surface with no declared span keeps `policyOptics` untouched, which is what
   * makes every existing caller and every golden unchanged by the law's landing.
   */
  const size = surface.size ?? MATERIAL_SOURCE_SIZE;
  const sizeK =
    surface.spanPx === undefined
      ? 0
      : sizeThicknessUnderPolicy(surface.spanPx, policy.material, size);
  // The scatter facet's own curve (W11c): a floor on any surface with a span,
  // rising under the same fold as the thickness — so a spanless surface still
  // keeps `policyOptics` untouched, and a small one with a span frosts at the
  // floor rather than at nothing.
  const scatterK =
    surface.spanPx === undefined
      ? 0
      : scatterThickness(
          surface.spanPx,
          size.refractionScale[accessibilityRefractionCap(policy.material)],
          size,
        );
  const optics: MaterialOptics =
    sizeK === 0 && scatterK === 0
      ? policyOptics
      : {
          ...policyOptics,
          blurRadius: sizeScatterSigmaAt(policyOptics.blurRadius, scatterK, size),
          tintAlpha: sizeOcclusionAlphaAt(policyOptics.tintAlpha, sizeK, size),
        };
  /*
   * The outer shadow (W8), through the same two folds and in the same order: the
   * accessibility regime first, because a preference outranks a material law, and
   * the size law on the result.
   *
   * The declaration is written from the profile's own lengths rather than from
   * anything of this tier's, which is the whole point of the facet moving out of
   * `CssTierMapping` — one shadow, two renderers.
   */
  const shadowSource = outerShadowUnderPolicy(
    surface.outerShadow ?? MATERIAL_SOURCE_OUTER_SHADOW,
    policy.material,
  );
  /*
   * The amplitude is a law and no longer a constant (W14 G1, claims §5.62): the
   * thin regime's occlusion is keyed on the backdrop this surface is over — the
   * same statistic W9's face response keys on, `surface.backdropLuminance`, an
   * author hint's declared level or the tone measured from the backdrop source —
   * and the thick regime's on the casting span, blended across the size law's own
   * knee. `outerShadowOcclusionAt` folds the size gain too, which is what
   * `sizeOuterShadowOcclusionAt` was doing here alone.
   *
   * A surface with no span (`spanPx === undefined` leaves `sizeK` at 0) resolves
   * the thin regime, which is what a surface too small for the size law to reach
   * was already getting.
   */
  const shadowOcclusion = outerShadowOcclusionAt(
    shadowSource,
    surface.backdropLuminance,
    surface.spanPx ?? 0,
    sizeK,
  );
  const radius = surface.radii.map(px).join(" ");

  // forced-colors: "system colors, borders, no glass" (§Accessibility). Nothing
  // to frost, lens or tint, and the palette is the platform's — so this is not a
  // dimmer version of the material, it is a different surface, and the branch
  // says so instead of trying to parameterise its way there.
  if (policy.material.glass === "none") {
    return {
      "border-radius": radius,
      "background-color": "Canvas",
      "background-image": "none",
      "border-style": "solid",
      "border-width": px(optics.borderWidth),
      "border-color": "CanvasText",
      "backdrop-filter": "none",
      "-webkit-backdrop-filter": "none",
      "box-shadow": "none",
      transition: transitionFor(policy),
      "--vitrea-tint": "Canvas",
      "--vitrea-occlusion": "1",
      "--vitrea-border-color": "CanvasText",
      "--vitrea-blur": "0px",
      ...foregroundDeclarations({ policy, mapping }),
    };
  }

  const filter = `blur(${px(optics.blurRadius)}) saturate(${optics.saturation})`;
  const tint = rgba(optics.tint, optics.tintAlpha);
  const border = rgba(optics.border, optics.borderAlpha);

  /*
   * X6's one honesty-core mechanism, reaching the tier most visitors get
   * (Decision Log #28(b), corrective K4): an `author-hint` mode with a declared
   * light or dark tone gets an explicit foreground token instead of the
   * `color-scheme`-driven `light-dark()` default. A "mixed" tone, a "fixed" or
   * "sampled-async" mode, or no hint at all keep `light-dark()` — there is no
   * single explicit answer to prefer instead. Accessibility policy outranks the
   * hint: near-monochrome (increased contrast; forced-colors takes the early
   * return above) is never overridden by it.
   *
   * K5 changed the arithmetic and not the mechanism. K4 read the tone straight
   * through — a dark backdrop got the light token — which was right while the
   * material was 28% opaque enough to see the backdrop through. At the material's
   * measured opacity the glyphs sit on the tint, not on the backdrop, so the tone
   * is now one input to the level behind the text rather than the answer. Both
   * regimes are still reachable and both are correct: a clear variant over a dark
   * backdrop still resolves to the light token, because at its alpha the backdrop
   * really does dominate.
   *
   * The decision itself moved out to `foregroundDeclarations` in C9d, unchanged:
   * the GPU tier needs the same answer over its own composite, and one rule with
   * two composite spaces is what stops the tiers disagreeing about the ink.
   */
  /*
   * A *measured* backdrop tone counts here exactly as a declared one does (W7).
   * `hintedBackdropLuminance` answers for an author hint and nothing else, so
   * without this a group whose backdrop vitrea had actually measured — and whose
   * material had just adapted onto it — fell through to the `light-dark()`
   * default. The adaptation can take a surface from near-white to near-black, and
   * ink that stays where the colour scheme put it is the K4/#32(b) failure
   * arriving through a third door.
   */
  const hintedLuminance =
    surface.backdropLuminance ?? hintedBackdropLuminance(surface.foreground, mapping);
  /*
   * A tinted surface with no hint is not undecidable. The level is monotonic in
   * the backdrop, so bracketing it over the whole range often decides the ink
   * outright — and a surface the app declared a colour for is exactly the case
   * where taking that decision is honouring the declaration rather than guessing.
   * Where the bracket straddles the crossover the backdrop really does decide,
   * and the `light-dark()` default stands.
   */
  const level =
    hintedLuminance !== undefined
      ? cssTierForegroundLevel(optics, hintedLuminance)
      : surface.tint === undefined
        ? undefined
        : boundedForegroundLevel(cssTierForegroundBounds(optics), mapping.foregroundCrossover);

  return {
    "border-radius": radius,
    // The tint is the contrast floor: it is here whether or not the blur lands,
    // and it stays on its own longhand so nothing layered above it can take it
    // down — see `pressGlowLayer`.
    "background-color": tint,
    // A profile is entitled to switch the illumination off, and a zero gain is
    // then a layer that paints nothing every frame rather than an absent one.
    "background-image": optics.glowGain > 0 ? pressGlowLayer(optics) : "none",
    "border-style": "solid",
    "border-width": px(optics.borderWidth),
    "border-color": border,
    "backdrop-filter": filter,
    "-webkit-backdrop-filter": filter,
    /*
     * The outer shadow (W8), and it is a `box-shadow` of pure BLACK on purpose,
     * not for want of a colour: black is what turns source-over into a multiply,
     * which is what makes this tier's shadow the reference's multiplicative
     * occlusion rather than a grey smear laid on top of the page. It is exactly
     * inert over a black backdrop, as the reference is, and no branch here
     * arranges that — see `MaterialSourceOuterShadow`.
     *
     * `cssShadowBlurRadius` is where the two blur conventions meet: this property
     * takes twice the Gaussian's σ, while `filter: blur()` above takes σ itself.
     */
    "box-shadow": outerShadowDeclaration(shadowSource, shadowOcclusion),
    transition: transitionFor(policy),
    "--vitrea-tint": tint,
    "--vitrea-occlusion": String(Math.round(optics.tintAlpha * 1000) / 1000),
    "--vitrea-border-color": border,
    "--vitrea-blur": px(optics.blurRadius),
    ...foregroundDeclarations({
      policy,
      mapping,
      ...(level === undefined ? {} : { level }),
    }),
  };
}

/**
 * The `box-shadow` value for a resolved outer shadow.
 *
 * `"none"` at zero occlusion rather than a transparent shadow, so a profile that
 * declines the facet costs the compositor nothing — and so the property still
 * gets written every frame, because a material that stopped writing one of its
 * own declarations leaves whatever was last there.
 */
function outerShadowDeclaration(shadow: MaterialSourceOuterShadow, occlusion: number): string {
  if (!(occlusion > 0)) return "none";
  const alpha = Math.round(outerShadowAlpha(occlusion) * 1000) / 1000;
  if (alpha <= 0) return "none";
  return (
    `0 ${px(shadow.offsetPx)} ${px(cssShadowBlurRadius(shadow.sigmaPx))} ` +
    `${px(shadow.spreadPx)} rgba(0, 0, 0, ${alpha})`
  );
}

function transitionFor(policy: ResolvedAccessibilityPolicy): string {
  const elastic = policy.motion.overshoot === "elastic";
  const duration = elastic ? NOMINAL_DURATION_MS : REDUCED_DURATION_MS;
  const easing = elastic ? ELASTIC_EASING : MONOTONIC_EASING;
  const properties = ["background-color", "border-color", "box-shadow", "backdrop-filter"];

  return properties.map((property) => `${property} ${duration}ms ${easing}`).join(", ");
}
