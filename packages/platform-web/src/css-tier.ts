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
 * The tier builds **no proxy** — which is exactly why `probe-failed` demotes to
 * it (core's note: "the very thing that failed is not on its path"). Until W16
 * that doctrine was stated as "in place, nothing layered", because the tier put
 * every declaration on the author's host and created no element of its own. The
 * narrowing is deliberate and it is the whole of W16 G1: the tier now creates
 * three children of the host, and the doctrine that survives is the one that
 * carries the demotion — the filters still read what is *behind* the host, so
 * nothing here needs the thing that failed. The moment this tier wanted a
 * **copy** of the backdrop it would stop being demotable-to, which is why the
 * outer shadow's lift is not drawn here (claims §5.71 §6).
 *
 * ## The element model (W16 G1; charter Decision Log 2 (a), claims §5.71)
 *
 * The reference's body is two components — a sharp term at about one device
 * pixel and a heavy one at eight to ten — mixed by a share that is highest just
 * inside the contour and fades over a fixed reach to a span-graded deep value.
 * One `backdrop-filter` has one σ and cannot be both, and the single-σ
 * projection this tier drew until W16 was the worst single form on the probe bed
 * (claims §5.42 §5). Two sibling filtered layers can be: the second blurs the
 * first's **output**, so a heavy layer at σ_step composes to √(σ_s² + σ_step²),
 * and its alpha is the heavy share. The same layer as a *child* of the first is
 * inert, because a filtered parent is a backdrop root — which is why both layers
 * have to be children of a filter-free host rather than the host keeping one.
 *
 * So the host keeps its geometry, its outer shadow and the five tokens, and
 * gains three children, each `position: absolute` over the host's border box
 * with `border-radius: inherit`, `pointer-events: none`, `aria-hidden` and a
 * negative `z-index` under a host that establishes a stacking context — which
 * paints them above the host's own background and border and below its in-flow
 * content, so the author's text and icons still sit on top of the material:
 *
 *  - **L1**, the sharp `backdrop-filter`, and the material's `saturate()`;
 *  - **L2**, the heavy `backdrop-filter`, its share carried by a raster
 *    `mask-image` drawn from the renderer's own k(u) where the engine is known
 *    to compose one, and by a flat `opacity` where it is not;
 *  - **L3**, the tint, the press glow and the rim — above both filters, because
 *    a tint *beneath* them is blurred by them and darkens a ring 0.010–0.015
 *    encoded deep over the first 4 CSS px (claims §5.71 §3).
 *
 * None of the three is focusable, hit-testable or announced, and none is a
 * proxy. The DOM that carries them is `css-tier-layers.ts`; this file stays pure
 * and decides only what each of them says.
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
  cssTierShadowAlpha,
  MATERIAL_SOURCE_OUTER_SHADOW,
  MATERIAL_SOURCE_SIZE,
  opticsUnderPolicy,
  outerShadowUnderPolicy,
  sizeOcclusionAlphaAt,
  cssTierHeavyShareAt,
  cssTierHeavySigmaCssPx,
  cssTierHeavyStepSigmaCssPx,
  cssTierSharpSigmaCssPx,
  scatterDeepThickness,
  scatterRampReachDevicePx,
  scatterFloorAtScale,
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
 * The tier's three created layers, in paint order (W16 G1).
 *
 * The names are what each layer *is*, not where it sits, because the order is
 * carried by the DOM and by `CSS_TIER_LAYER_ORDER` rather than by these keys.
 */
export const CSS_TIER_LAYER_ORDER = ["sharp", "heavy", "overlay"] as const;

export type CssTierLayer = (typeof CSS_TIER_LAYER_ORDER)[number];

/**
 * The body's resolved form for one surface — the numbers the tier actually
 * drew, in the units it drew them in.
 *
 * Reported rather than inferred, for the honesty core's own reason: a capture
 * cell, a readout and a test must be able to read what drew instead of what was
 * asked for. The cost collapse and the two engine gates all change this record
 * and nothing else about the tier's contract.
 */
export interface CssTierBody {
  /** `two-layer` normally; `collapsed` under the area budget or a zero frost. */
  readonly form: "two-layer" | "collapsed";
  /** Which blur the layers carry — the linear-light reference filter, or `blur()`. */
  readonly filter: "reference-filter" | "blur";
  /** How the heavy share is carried: the exact raster ramp, or one flat alpha. */
  readonly share: "raster-mask" | "flat";
  /** L1's width, CSS px. */
  readonly sharpSigmaCssPx: number;
  /** L2's own width, CSS px — the step that composes L1's output to `heavySigmaCssPx`. */
  readonly heavyStepSigmaCssPx: number;
  /** The composed heavy width, CSS px. */
  readonly heavySigmaCssPx: number;
  /**
   * The flat heavy share — L2's `opacity` where the ramp is not carried, and the
   * mask's own area mean where it is.
   */
  readonly flatShare: number;
  /** The ramp, in the units the mask is drawn in. Absent where the tier draws no ramp. */
  readonly ramp?: CssTierRamp;
  /**
   * The single-σ projection this tier drew before W16 — the width the collapse
   * degrades to, and the number `--vitrea-blur` publishes.
   */
  readonly projectedSigmaCssPx: number;
}

/** The depth ramp as the mask carries it, all depths in DEVICE px (W16 G1). */
export interface CssTierRamp {
  /** The heavy share at the contour, `1 − s₀(span, dpr)`, folded. */
  readonly contourShare: number;
  /** The heavy share at and beyond the reach, `kDeep(span, dpr)`, folded. */
  readonly deepShare: number;
  /** The depth at which the excursion vanishes, device px. */
  readonly reachDevicePx: number;
  /** The ratio the ramp and the widths were read at. */
  readonly devicePixelRatio: number;
}

/**
 * What one engine is known to do with the two constructions this tier's body
 * depends on — read off the conformance table, never guessed (contract X9).
 *
 * Both fail closed: an engine that has not been measured draws the two layers
 * with a flat `opacity` through `blur()`, which is ordinary CSS everywhere and
 * whose failure mode is a flat mix rather than a broken surface.
 */
export interface CssTierEngineCapabilities {
  /** Chromium alone renders a reference filter inside `backdrop-filter` (claims §5.71 §2). */
  readonly referenceFilterInBackdrop: boolean;
  /** Whether a `mask-image` on a `backdrop-filter` layer composes (claims §5.71 §1). */
  readonly maskOnBackdropFilter: "yes" | "no" | "unverified";
}

/** The conservative capabilities: the form every engine can draw. */
export const CSS_TIER_UNVERIFIED_ENGINE: CssTierEngineCapabilities = {
  referenceFilterInBackdrop: false,
  maskOnBackdropFilter: "unverified",
};

/**
 * The root-level cost budget: the total **filtered** surface area, in device px
 * per frame, above which the heavy layer collapses into the single mixed σ
 * (W16 charter Decision Log 2, question 1 — the user's constant).
 *
 * Not an optical number and not fitted to the reference, which is why it lives
 * here rather than in `optics.ts`: it is a statement about a compositor. G0
 * measured one `backdrop-filter` per surface never leaving the display cadence
 * at any count, and two leaving it monotonically from 0.49–0.61 M filtered
 * device px per frame and saturating near 27 ms above 1.2 M. 0.4 M is under the
 * measured break with margin, and every page vitrea ships clears it by 2.5×
 * (the demo's densest CSS-tier page is 0.16 M at dpr 2).
 *
 * The collapse is a **declared** degradation: it is exactly the form this tier
 * drew before W16, the resolved `GlassGroupState` names it, and the capture
 * cells and the tests read it there.
 */
export const CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX = 400_000;

/**
 * Everything the tier writes for one surface: the host's own declarations, the
 * three created layers', and the body it resolved (W16 G1).
 *
 * `layers` is absent under forced colors, where the material is not a dimmer
 * version of itself but a different surface — system colours, a real border and
 * no glass — and the created layers are torn down rather than emptied.
 */
export interface CssTierRender {
  readonly host: StyleDeclarations;
  readonly layers?: Readonly<Record<CssTierLayer, StyleDeclarations>>;
  readonly body: CssTierBody;
}

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
   * The surface's measured border box in CSS px, `[width, height]` — the
   * extents the depth ramp's projection is integrated over (W13 G1).
   *
   * `spanPx` alone cannot say what the surface's area is, and the projection is
   * an area average: a 320×44 toolbar has far more of its area within the ramp's
   * reach of a contour than a 44×44 square does, so the two carry different
   * mixes even though their span is one number and the same. Where a caller has
   * measured the host it should declare both; absent, `scatterRampAreaMean`
   * falls back to a square of the span, which is exactly right on a square and
   * an over-estimate of the deep area on a strip.
   */
  readonly extentsCssPx?: readonly [number, number];
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
  /**
   * The ratio the page is composited at (W16 G1; charter Decision Log 2 (c)).
   *
   * The tier's two widths are **device-pixel** quantities and its mask is the
   * renderer's own ramp, so the live ratio reaches everything the body draws.
   * W13 Decision Log 5 refused exactly this for the single-blur form, on a
   * measurement about the single-blur form: the tier's best SINGLE σ is larger
   * in CSS px at 2x, which is a statement about projecting a mix onto one
   * Gaussian rather than about either component's width (claims §5.55 §5,
   * §5.69 §4). With the mix carried, the refusal has nothing left to say.
   *
   * Defaults to 1, which is what a caller with no viewport reading honestly has.
   */
  readonly devicePixelRatio?: number;
  /**
   * What the engine is known to do with a reference filter and with a mask on a
   * `backdrop-filter` layer. Defaults to the conservative pair, so a caller that
   * says nothing gets the form every engine can draw.
   */
  readonly engine?: CssTierEngineCapabilities;
  /**
   * Whether the root's cost budget has collapsed the heavy layer into the single
   * mixed σ (`CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX`). The decision is the
   * root's, because it is a statement about every surface at once; this function
   * is per surface and cannot make it.
   */
  readonly collapsed?: boolean;
  /**
   * The document-unique prefix the reference filters' `id`s are built from. One
   * root, one `<svg>` of definitions, one `<filter>` per distinct σ — and two
   * roots on a page must not name the same `id`.
   */
  readonly filterIdPrefix?: string;
}

/**
 * The `id` of the reference filter for one σ, in CSS px.
 *
 * Deterministic in the σ and quantised the same way the declaration is, so the
 * declaration and the definition cannot name different numbers, and two surfaces
 * at the same width share one `<filter>` rather than each building its own.
 */
export function referenceFilterId(prefix: string, sigmaCssPx: number): string {
  return `${prefix}-b${String(Math.round(sigmaCssPx * 100))}`;
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
 * Everything the CSS tier writes for one surface: the host's declarations, the
 * three created layers', and the body those layers resolved to (W16 G1).
 *
 * Pure: the same surface always yields the same record, which is what makes the
 * accessibility mapping — and now the element model, the second scale and the
 * cost collapse — testable without a browser.
 */
export function cssTierDeclarations(surface: CssTierSurface): CssTierRender {
  const { policy } = surface;
  const mapping = surface.mapping ?? CSS_TIER_MAPPING;
  const engine = surface.engine ?? CSS_TIER_UNVERIFIED_ENGINE;
  const dpr = Math.max(surface.devicePixelRatio ?? 1, 1e-3);
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
  const fold = size.refractionScale[accessibilityRefractionCap(policy.material)];
  /*
   * The scatter facet (W11c; W13 G1's ramp; W16 G1's two layers): a floor on any
   * surface with a span, rising under the same fold as the thickness — so a
   * spanless surface still keeps `policyOptics` untouched, and a small one with a
   * span frosts at the floor rather than at nothing.
   *
   * **Read at the live ratio since W16 G1** (charter Decision Log 2 (c)). W13
   * Decision Log 5 pinned this at dpr 1 and W15 Decision Log 3 kept it, on a
   * measurement about the form the tier had: with one `backdrop-filter` the tier
   * draws the ramp's area mean, and the mean's best single σ is *larger* in CSS
   * px at 2x (claims §5.55 §5, §5.69 §4), so following the device-pixel widths
   * with one layer moved the 2x rows the way the measurement said was wrong.
   * That argument is about the projection, not about either component: with the
   * mix carried by a second layer and a mask, both widths are device-pixel
   * quantities and the ratio reaches them.
   *
   * The projection itself survives for two consumers that still need one number:
   * `--vitrea-blur`, which an app matching the material with its own `blur()`
   * has to keep getting, and the cost collapse below.
   */
  const scatterK =
    surface.spanPx === undefined
      ? 0
      : scatterThickness(surface.spanPx, fold, size, dpr, surface.extentsCssPx);
  /*
   * The single-σ projection this tier drew before W16, at dpr 1 — kept exactly
   * as it was, because it is what the collapse degrades to and what the token
   * publishes, and a degradation that was also a re-derivation would be two
   * changes wearing one name.
   */
  const projectedScatterK =
    surface.spanPx === undefined
      ? 0
      : scatterThickness(surface.spanPx, fold, size, 1, surface.extentsCssPx);
  const projectedSigma =
    projectedScatterK === 0
      ? policyOptics.blurRadius
      : sizeScatterSigmaAt(policyOptics.blurRadius, projectedScatterK, size);
  const optics: MaterialOptics =
    sizeK === 0 && projectedScatterK === 0
      ? policyOptics
      : {
          ...policyOptics,
          blurRadius: projectedSigma,
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
   * knee. `cssTierShadowAlpha` folds the size gain too, which is what
   * `sizeOuterShadowOcclusionAt` was doing here alone, and it folds this tier's
   * missing lift into the one alpha it can paint — see that function for why
   * subtracting the other tier's second term is a conversion of the shared
   * profile rather than an amplitude of this tier's own.
   *
   * A surface with no span (`spanPx === undefined` leaves `sizeK` at 0) resolves
   * the thin regime, which is what a surface too small for the size law to reach
   * was already getting.
   */
  const shadowAlpha = cssTierShadowAlpha(
    shadowSource,
    surface.backdropLuminance,
    surface.spanPx ?? 0,
    sizeK,
  );
  const radius = surface.radii.map(px).join(" ");

  // forced-colors: "system colors, borders, no glass" (§Accessibility). Nothing
  // to frost, lens or tint, and the palette is the platform's — so this is not a
  // dimmer version of the material, it is a different surface, and the branch
  // says so instead of trying to parameterise its way there. The created layers
  // are torn down rather than emptied: a tier that left them up would leave glass
  // under system colours.
  if (policy.material.glass === "none") {
    return {
      host: {
        "border-radius": radius,
        "background-color": "Canvas",
        "background-image": "none",
        "border-style": "solid",
        "border-width": px(optics.borderWidth),
        "border-color": "CanvasText",
        "backdrop-filter": "none",
        "-webkit-backdrop-filter": "none",
        // Written at its initial value for the reason every other property in
        // this branch is: the material branch sets `isolation: isolate` to give
        // its created layers a stacking context, and a host that switched into
        // forced colors while keeping that inline would carry a stacking context
        // nothing on it needs. Harmless to look at and exactly the stale-value
        // class this file argues against everywhere else.
        isolation: "auto",
        "box-shadow": "none",
        transition: transitionFor(policy, ["background-color", "border-color", "box-shadow"]),
        "--vitrea-tint": "Canvas",
        "--vitrea-occlusion": "1",
        "--vitrea-border-color": "CanvasText",
        "--vitrea-blur": "0px",
        ...foregroundDeclarations({ policy, mapping }),
      },
      body: {
        form: "collapsed",
        filter: "blur",
        share: "flat",
        sharpSigmaCssPx: 0,
        heavyStepSigmaCssPx: 0,
        heavySigmaCssPx: 0,
        flatShare: 0,
        projectedSigmaCssPx: 0,
      },
    };
  }

  const body = resolveCssTierBody({
    baseSigmaDevicePx: policyOptics.blurRadius,
    projectedSigmaCssPx: projectedSigma,
    spanPx: surface.spanPx,
    scatterK,
    fold,
    size,
    dpr,
    engine,
    collapsed: surface.collapsed === true,
  });
  const prefix = surface.filterIdPrefix ?? DEFAULT_FILTER_ID_PREFIX;
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

  const host: StyleDeclarations = {
    "border-radius": radius,
    /*
     * The host paints no material of its own any more. Both properties are still
     * written, at their inert values, for the reason every declaration this tier
     * owns is written every frame: a material that stops writing one of its own
     * declarations leaves whatever was last there — a tier switch, or the
     * forced-colors branch stepping back out, would otherwise leave a stale tint
     * or a stale filter under the layers.
     */
    "background-color": "transparent",
    "background-image": "none",
    "backdrop-filter": "none",
    "-webkit-backdrop-filter": "none",
    /*
     * The stacking context the negative-`z-index` layers need, and the *only*
     * root-forming property that is safe here: `isolation: isolate` is not in
     * Filter Effects 2's backdrop-root trigger set, so it does not make the
     * children's own `backdrop-filter` inert (S1's D1 labelling measured exactly
     * that, and the conformance table's `backdropRootTriggers` records it).
     * `opacity`, a `filter`, a `mask` or a blend mode on the host would each have
     * cut the layers off from the page behind them.
     */
    isolation: "isolate",
    /*
     * The border stays on the host and stays `transparent`. It is LAYOUT — the
     * author's content box depends on it and no created layer may move it — but
     * the host's border paints *below* the negative-`z` children and would be
     * covered by them, so the rim's colour is redrawn as an inset `box-shadow` on
     * L3, which follows `border-radius` exactly and needs no box-sizing
     * arithmetic. This is the one change an author can observe in the computed
     * style of their own element.
     */
    "border-style": "solid",
    "border-width": px(optics.borderWidth),
    "border-color": "transparent",
    /*
     * The outer shadow (W8), and it is a `box-shadow` of pure BLACK on purpose,
     * not for want of a colour: black is what turns source-over into a multiply,
     * which is what makes this tier's shadow the reference's multiplicative
     * occlusion rather than a grey smear laid on top of the page. It is exactly
     * inert over a black backdrop, as the reference is, and no branch here
     * arranges that — see `MaterialSourceOuterShadow`.
     *
     * It stays on the HOST: it paints outside the border box and below the
     * background, and the created layers — clipped to their own boxes — never
     * cover it.
     *
     * `cssShadowBlurRadius` is where the two blur conventions meet: this property
     * takes twice the Gaussian's σ, while `filter: blur()` above takes σ itself.
     */
    "box-shadow": outerShadowDeclaration(shadowSource, shadowAlpha),
    // A transition is declared on the element that carries the property, so the
    // host keeps only the outer shadow's.
    transition: transitionFor(policy, ["box-shadow"]),
    "--vitrea-tint": tint,
    "--vitrea-occlusion": String(Math.round(optics.tintAlpha * 1000) / 1000),
    "--vitrea-border-color": border,
    /*
     * Still the single-σ projection, and deliberately not either layer's width:
     * an app matching the material with its own `blur()` has to keep getting one
     * number, and the body's two widths belong in the readout and the capture
     * cell (`CssTierBody`) rather than in a public token.
     */
    "--vitrea-blur": px(body.projectedSigmaCssPx),
    ...foregroundDeclarations({
      policy,
      mapping,
      ...(level === undefined ? {} : { level }),
    }),
  };

  return {
    host,
    layers: {
      sharp: sharpLayerDeclarations(body, optics, prefix, policy),
      heavy: heavyLayerDeclarations(body, optics.borderWidth, prefix, policy),
      overlay: overlayLayerDeclarations(optics, tint, border, policy),
    },
    body,
  };
}

/** Where a root that did not name itself puts its reference filters. */
const DEFAULT_FILTER_ID_PREFIX = "vitrea-css-tier";

/**
 * Below this the heavy step is not a blur, it is a rounding artefact: `px()`
 * writes two decimals, so a step under half of the last digit would be declared
 * as `0px` and cost a render surface to draw nothing.
 */
const SIGMA_QUANTUM_CSS_PX = 0.005;

/**
 * The shared geometry of all three layers: the host's border box, the host's
 * radius, inert to pointers, and under the host's own content.
 *
 * `inset: calc(-1 * <borderWidth>)` rather than `inset: 0` because an absolutely
 * positioned child's containing block is the host's **padding** box, so a child
 * at zero would leave the border area — where the rim is drawn — uncovered.
 *
 * The three `z-index` values are distinct rather than all `-1` so the order is
 * declared instead of inherited from DOM order. Every one of them is negative,
 * which is what puts the whole stack above the host's background and border and
 * below its in-flow content.
 *
 * One consequence an app can see, stated rather than worked around: a host with
 * `overflow: hidden` clips its children to its PADDING box, so on such a host the
 * layers lose the border-width ring they stand proud by — the rim thins to
 * nothing while the body and the tint are untouched. Clipping the material to the
 * padding box is what the author asked for; the alternative would be vitrea
 * overriding an author's `overflow`, which is a layout property this package does
 * not own.
 */
function layerFrame(borderWidth: number, zIndex: number): StyleDeclarations {
  return {
    position: "absolute",
    inset: `-${px(borderWidth)}`,
    "border-radius": "inherit",
    "pointer-events": "none",
    "z-index": String(zIndex),
  };
}

/**
 * L1 — the sharp component, and the material's `saturate()`.
 *
 * **Why the saturation sits here.** It is one operation on the composite and it
 * has to happen exactly once. A saturation is a matrix on the layer's channels
 * and a blur is a weighted sum of them, so the two commute: saturating the
 * backdrop before L2 blurs it gives the same result as saturating after, and
 * putting the term on the first layer therefore saturates the whole body once
 * rather than saturating the heavy component twice or the sharp one only. On L2
 * it would also have been scaled by the heavy share, which is a mix weight and
 * has nothing to do with colour.
 *
 * One residual, stated: `saturate()` is defined on sRGB values while the
 * reference filter blurs in linear light, so on the linear-light path the body is
 * blurred in linear light and then saturated in the encoded space, where the
 * renderer saturates in linear light throughout. It is the same operator in a
 * different space and the difference is a chroma one; it is a gap this tier
 * carries, not a choice made twice.
 */
function sharpLayerDeclarations(
  body: CssTierBody,
  optics: MaterialOptics,
  prefix: string,
  policy: ResolvedAccessibilityPolicy,
): StyleDeclarations {
  const blur = blurFunction(body.filter, body.sharpSigmaCssPx, prefix);
  const filter = `${blur} saturate(${optics.saturation})`;
  return {
    ...layerFrame(optics.borderWidth, -3),
    "backdrop-filter": filter,
    "-webkit-backdrop-filter": filter,
    transition: transitionFor(policy, ["backdrop-filter"]),
  };
}

/**
 * L2 — the heavy component, drawn after L1 so that it blurs L1's output.
 *
 * `display: none` when the body collapsed, rather than a transparent layer: the
 * collapse exists to buy back a render surface and a two-pass Gaussian, and a
 * layer at `opacity: 0` still costs both.
 *
 * The share is carried by the raster `mask-image` where the engine is known to
 * compose one and by a flat `opacity` where it is not. `mask-image` itself is set
 * by `css-tier-layers.ts`, which is the module with a canvas; what belongs here
 * is the rest of the mask's declaration, and the `opacity` that has to go back to
 * 1 when a mask is carrying the weight instead.
 */
function heavyLayerDeclarations(
  body: CssTierBody,
  borderWidth: number,
  prefix: string,
  policy: ResolvedAccessibilityPolicy,
): StyleDeclarations {
  if (body.form === "collapsed") return { ...layerFrame(borderWidth, -2), display: "none" };
  const blur = blurFunction(body.filter, body.heavyStepSigmaCssPx, prefix);
  const masked = body.share === "raster-mask";
  return {
    ...layerFrame(borderWidth, -2),
    display: "block",
    "backdrop-filter": blur,
    "-webkit-backdrop-filter": blur,
    opacity: masked ? "1" : String(Math.round(body.flatShare * 1000) / 1000),
    ...(masked
      ? {
          "mask-mode": "alpha",
          "mask-size": "100% 100%",
          "mask-repeat": "no-repeat",
          "-webkit-mask-size": "100% 100%",
          "-webkit-mask-repeat": "no-repeat",
        }
      : {}),
    transition: transitionFor(policy, ["backdrop-filter", "opacity"]),
  };
}

/**
 * L3 — the tint, the press glow and the rim, above both filters.
 *
 * Above them because a tint *beneath* a `backdrop-filter` is sampled by it: the
 * charter's linearity argument (a blur of a uniform shade over the backdrop is
 * the shade over the blurred backdrop) holds away from the contour and fails
 * inside a kernel's width of it, where the blur reaches outside the host and the
 * engine's edge mode decides. G0 measured the failure at 0.010–0.015 encoded over
 * the first 4 CSS px and 0.004–0.008 out to 8, decaying to a thousandth by 32
 * (claims §5.71 §3) — a band, which is the statistic this wave exists to fix.
 *
 * The rim is an inset `box-shadow` of the border's width rather than a `border`,
 * because the host's own border paints below these layers and would be covered.
 * An inset shadow follows `border-radius` exactly, which a redrawn border on an
 * inset box would not.
 */
function overlayLayerDeclarations(
  optics: MaterialOptics,
  tint: string,
  border: string,
  policy: ResolvedAccessibilityPolicy,
): StyleDeclarations {
  return {
    ...layerFrame(optics.borderWidth, -1),
    // The tint is the contrast floor: it is here whether or not the blur lands,
    // and it stays on its own longhand so nothing layered above it can take it
    // down — see `pressGlowLayer`.
    "background-color": tint,
    // A profile is entitled to switch the illumination off, and a zero gain is
    // then a layer that paints nothing every frame rather than an absent one.
    "background-image": optics.glowGain > 0 ? pressGlowLayer(optics) : "none",
    "box-shadow":
      optics.borderWidth > 0 && optics.borderAlpha > 0
        ? `inset 0 0 0 ${px(optics.borderWidth)} ${border}`
        : "none",
    transition: transitionFor(policy, ["background-color", "box-shadow"]),
  };
}

/**
 * The blur term of a layer's `backdrop-filter`: the linear-light reference
 * filter where the engine renders one, and `blur()` where it does not.
 *
 * The two are not equivalent and the difference is the body's largest single
 * residual. `backdrop-filter: blur()` operates on the page's ENCODED values,
 * while the reference's body — and everything the GPU tier draws — is linear in
 * luminance, so the same law blurred in the encoded space reads 2.4–2.8× the GPU
 * law's residual on the thick spans however the σ, the share and the mask are
 * chosen (claims §5.71 §2). An SVG `feGaussianBlur` at
 * `color-interpolation-filters="linearRGB"` blurs in linear light and closes it
 * to 1.10–1.50× at 1x and 0.97–1.03× at 2x. Only Chromium renders a reference
 * filter inside `backdrop-filter`, which is why this rides
 * `referenceFilterInBackdrop` and why that field stopped being a reserved seam
 * and became a fidelity dependency.
 */
function blurFunction(
  kind: CssTierBody["filter"],
  sigmaCssPx: number,
  prefix: string,
): string {
  if (kind === "blur") return `blur(${px(sigmaCssPx)})`;
  return `url(#${referenceFilterId(prefix, sigmaCssPx)})`;
}

/**
 * The body one surface resolves to (W16 G1; charter Decision Log 2 (a)–(c)).
 *
 * Every quantity is the renderer's own, read at the live ratio through
 * `optics.ts` — the sharp width, the gain the heavy width is a multiple of, the
 * ramp's start, its reach and the deep value. The one conversion is
 * `scatterHeavyEffectiveSigmaDevicePx`, which is a measurement of the renderer's
 * kernel and not a constant of this tier's (K5).
 */
function resolveCssTierBody(input: {
  readonly baseSigmaDevicePx: number;
  readonly projectedSigmaCssPx: number;
  readonly spanPx: number | undefined;
  readonly scatterK: number;
  readonly fold: number;
  readonly size: MaterialSourceSize;
  readonly dpr: number;
  readonly engine: CssTierEngineCapabilities;
  readonly collapsed: boolean;
}): CssTierBody {
  const { size, dpr, engine, spanPx } = input;
  const filter: CssTierBody["filter"] = engine.referenceFilterInBackdrop
    ? "reference-filter"
    : "blur";
  const sharp = cssTierSharpSigmaCssPx(input.baseSigmaDevicePx, dpr);
  const heavy =
    spanPx === undefined
      ? sharp
      : cssTierHeavySigmaCssPx(input.baseSigmaDevicePx, spanPx, size, dpr);
  const step = cssTierHeavyStepSigmaCssPx(sharp, heavy);
  const flatShare = clamp01(input.scatterK);

  /*
   * Three ways to end up with one layer, and they are the same form: the root's
   * cost budget said so; the surface has no span, so there is no size law and no
   * mix to carry; or the step rounds to nothing, which is a profile whose gain is
   * at or below 1 and a frost regime of `none` (`blurRadius` 0). In every one of
   * them the single layer draws the projection this tier drew before W16, which
   * is what makes the collapse a degradation to a known form rather than a third
   * material.
   */
  const collapsed =
    input.collapsed || spanPx === undefined || step < SIGMA_QUANTUM_CSS_PX || flatShare <= 0;
  if (collapsed) {
    return {
      form: "collapsed",
      filter,
      share: "flat",
      sharpSigmaCssPx: input.projectedSigmaCssPx,
      heavyStepSigmaCssPx: 0,
      heavySigmaCssPx: input.projectedSigmaCssPx,
      flatShare: 0,
      projectedSigmaCssPx: input.projectedSigmaCssPx,
    };
  }

  /*
   * The ramp is carried exactly where the engine is measured to compose a mask on
   * a filtered layer and flat where it is not — X9's fail-closed rule, and
   * Decision Log 2's question 2 answered: the two layers are ordinary CSS
   * everywhere, so an unverified engine still gets the body's two components; the
   * band is the only thing the labeled pass unlocks, and a mask an engine ignores
   * would render at alpha 1 rather than at the share, which is a wrong-looking
   * surface rather than a broken one.
   */
  const share: CssTierBody["share"] =
    engine.maskOnBackdropFilter === "yes" ? "raster-mask" : "flat";

  return {
    form: "two-layer",
    filter,
    share,
    sharpSigmaCssPx: sharp,
    heavyStepSigmaCssPx: step,
    heavySigmaCssPx: heavy,
    flatShare,
    ...(share === "raster-mask"
      ? {
          ramp: {
            contourShare: cssTierHeavyShareAt(0, dpr, input.fold, size, spanPx),
            deepShare: clamp01(
              scatterFloorFold(input.fold, size, dpr, scatterDeepThickness(spanPx, size, dpr)),
            ),
            reachDevicePx: scatterRampReachDevicePx(dpr, size),
            devicePixelRatio: dpr,
          },
        }
      : {}),
    projectedSigmaCssPx: input.projectedSigmaCssPx,
  };
}

/**
 * The accessibility fold on one heavy-share value — the same fold
 * `scatterThickness` applies to the projection, which scales the excursion away
 * from the scatter floor and never the floor itself.
 */
function scatterFloorFold(
  fold: number,
  size: MaterialSourceSize,
  dpr: number,
  share: number,
): number {
  const floor = scatterFloorAtScale(size, dpr);
  return floor + (share - floor) * fold;
}

const clamp01 = (value: number): number => Math.min(1, Math.max(0, value));

/**
 * The `box-shadow` value for a resolved outer shadow, from the compositing alpha
 * `cssTierShadowAlpha` resolved.
 *
 * `"none"` at zero alpha rather than a transparent shadow, so a profile that
 * declines the facet costs the compositor nothing — and so the property still
 * gets written every frame, because a material that stopped writing one of its
 * own declarations leaves whatever was last there.
 */
function outerShadowDeclaration(shadow: MaterialSourceOuterShadow, alpha: number): string {
  const rounded = Math.round(alpha * 1000) / 1000;
  if (!(rounded > 0)) return "none";
  return (
    `0 ${px(shadow.offsetPx)} ${px(cssShadowBlurRadius(shadow.sigmaPx))} ` +
    `${px(shadow.spreadPx)} rgba(0, 0, 0, ${rounded})`
  );
}

/**
 * The transition for one element's own properties.
 *
 * A transition has to be declared on the element that carries the property, so
 * W16's three layers split what used to be one list on the host: the outer
 * shadow stays with the host, the two filters go to L1 and L2, and the tint and
 * the rim go to L3. The duration and the easing are still one decision — the
 * material morphs as one thing, whichever element happens to carry a term of it.
 */
function transitionFor(
  policy: ResolvedAccessibilityPolicy,
  properties: readonly string[],
): string {
  const elastic = policy.motion.overshoot === "elastic";
  const duration = elastic ? NOMINAL_DURATION_MS : REDUCED_DURATION_MS;
  const easing = elastic ? ELASTIC_EASING : MONOTONIC_EASING;

  return properties.map((property) => `${property} ${duration}ms ${easing}`).join(", ");
}
