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
 * So the host keeps its geometry and the five tokens, and gains three children,
 * each `position: absolute` over the host's border box
 * with `border-radius: inherit`, `pointer-events: none`, `aria-hidden` and a
 * negative `z-index` under a host that establishes a stacking context — which
 * paints them above the host's own background and border and below its in-flow
 * content, so the author's text and icons still sit on top of the material:
 *
 *  - **L1**, the sharp `backdrop-filter`, and the material's `saturate()`;
 *  - **L2**, the heavy `backdrop-filter`, its share carried by a raster
 *    `mask-image` drawn from the renderer's own k(u) where the engine is known
 *    to compose one, and by a flat `opacity` where it is not;
 *  - **L3**, the tint, the press glow, the rim and — since W18 G1 — the outer
 *    shadow, above both filters, because anything the tier draws *beneath* them
 *    is blurred by them: a tint there darkens a ring 0.010–0.015 encoded deep
 *    over the first 4 CSS px (claims §5.71 §3), and a shadow there darkens the
 *    whole body by 0.0032 to 0.0096 (claims §5.77 §3).
 *
 * None of the three is focusable, hit-testable or announced, and none is a
 * proxy. The DOM that carries them is `css-tier-layers.ts`; this file stays pure
 * and decides only what each of them says.
 *
 * ## Where the outer shadow is painted (W18 G1; charter Decision Log 2 (1))
 *
 * A `backdrop-filter`'s backdrop is everything painted below the element, over
 * the region the kernel needs — so the shadow the tier drew on the host until W18
 * sat inside its own body's blur, and inside its neighbours': a host is a
 * stacking context, so a later host's backdrop contains every earlier host's
 * subtree whole. Two carriers take it out, both decided in `css-tier-shadow.ts`
 * and reported on `GlassGroupState.cssShadow`. **Carrier A** puts the shadow on
 * L3, painted after the filters, which closes a surface's own share and needs no
 * element; **carrier B**, where a group has more than one member, paints every
 * member's shadow from one child per member inside the group's LAST-painted host
 * — the only element that can be painted after every member's filters — clipped
 * out of every member's body. **The fallback** is the host, for a host whose own
 * `overflow` clips its children and would crop a shadow on L3 away; there the
 * shadow stays sampled and `sampledOuterShadowFactor` in `optics.ts` is the bound
 * on what that costs.
 *
 * ## Presence: the widths and the weights (W27d; wave §Presence, not alpha)
 *
 * `materialization` is a per-surface presence, and it is this tier's whole
 * answer to `Glass.identity` and to Apple's rule that a material arrives by
 * "gradually modulating the light bending and lensing" rather than by fading.
 * Every optical term the tier paints is multiplied by it — the body's two
 * widths, the two filtered layers' weight, the tint, the rim, the press glow
 * and the outer shadow — and no `opacity` is ever written on the host, because
 * a sub-1 opacity there forms a Backdrop Root and what would go with it is the
 * group's proxy sampling (contract X6).
 *
 * **The body carries it twice, and that is deliberate.** The widths scale
 * because the light bending is what a materializing surface has less of, and
 * this tier's widths are the renderer's own device-pixel quantities read
 * through functions that are linear in them, so a presence multiplies σ_sharp,
 * σ_heavy, the step between them and the published projection alike. The
 * weights scale because a `backdrop-filter`'s output composites into the
 * element's own group: an `opacity` on L1 and L2 mixes the filtered body toward
 * the raw backdrop, which is the same carrier W16 measured for L2's flat share
 * (claims §5.71 §1) and the term the wave's design names ("body mix toward the
 * unblurred backdrop"). The material's own size law couples the two the same
 * way — a thinner surface both scatters less and occludes less — so the pair is
 * one fold of thickness rather than a presence counted twice.
 *
 * **What a following width costs, and what pays for it.** On this tier's
 * fidelity path a width is a `<filter>` definition named by its own σ, so a σ
 * that follows a driver builds a definition per width per frame and the
 * frame-scoped sweep removes the one before it — bounded by construction, never
 * accumulating, and the whole of the cost is an element and its two attributes.
 * What is NOT rebuilt is the tint table those definitions carry: the transfer is
 * presence-invariant (below), and `css-tier-layers.ts` keeps each solved table
 * beside its transfer so the bisection runs once per material rather than once
 * per width.
 *
 * Three residuals, named rather than hidden:
 *
 *  1. The transit's shape is the product of the terms that carry it and has no
 *     reference at all — neither its duration nor its curve is measured (X8).
 *  2. L2 blurs L1's OUTPUT, so at an intermediate presence a `(1 − p)·p` share
 *     of the composite is the blurred RAW backdrop rather than the material — a
 *     ghost that vanishes at 0 and at 1.
 *  3. The sharp filter's table is solved at the floor the material keeps at
 *     rest while L3 paints that floor at `α₃·p`, so the linear form's identity
 *     (the floor and the remainder compose to the material) is exact at both
 *     endpoints and an approximation between them. Solving it at `α₃·p` instead
 *     would put the driver's value in the definition's own name, which is the
 *     one thing that turns a rebuild into a re-solve.
 *
 * The rim's WIDTH is layout and never scales: an author's content box does not
 * move because a surface is materializing. And at presence 0 the tier declares
 * no filter and no heavy layer at all, so a surface held at `Glass.identity`
 * costs the compositor nothing rather than drawing an invisible body.
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
  cssTierCompositeLevel,
  cssTintEncodedFormError,
  cssTintForm,
  linearChainReaches,
  CSS_TIER_MAPPING,
  cssTierForegroundBounds,
  cssTierForegroundLevel,
  cssShadowBlurRadius,
  cssTierShadowAlpha,
  MATERIAL_SOURCE_OUTER_SHADOW,
  MATERIAL_SOURCE_SIZE,
  opticsUnderPolicy,
  outerShadowUnderPolicy,
  cssTierHeavyShareAt,
  cssTierHeavySigmaCssPx,
  cssTierHeavyStepSigmaCssPx,
  cssTierSharpSigmaCssPx,
  cssTierForegroundColour,
  cssTierForegroundColourBounds,
  foldedOverlay,
  inkAlphaHoldingContrast,
  neutralComposite,
  WCAG_BODY_TEXT_CONTRAST,
  type EncodedRgb,
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

import type { CssTierShadowCarrier } from "./css-tier-shadow";

export type { CssTierShadowCarrier };

/**
 * The least tint this tier draws on the shipped profile — `MATERIAL_OPTICS.clear`'s
 * converted alpha, restated as a number because `MATERIAL_OPTICS` is derived in
 * `optics.ts` from the profile and this module may not import a value that
 * depends on it at module scope. `tier-coherence` pins the two together.
 */
const CSS_TIER_TINT_FLOOR_ALPHA = 0.2668228970218852;

/** The two ink tokens the adaptive foreground chooses between. */
export const FOREGROUND_INK = { dark: "#1c1c1e", light: "#f5f5f7" } as const;

/** The same two inks as channels, so a reduced-alpha level can be written from them. */
const FOREGROUND_INK_CHANNELS: Readonly<Record<"dark" | "light", Rgb255>> = {
  dark: [0x1c, 0x1c, 0x1e],
  light: [0xf5, 0xf5, 0xf7],
};

/** What a surface with nothing to decide from keeps: `color-scheme` decides instead. */
const FOREGROUND_DEFAULT = `light-dark(${FOREGROUND_INK.dark}, ${FOREGROUND_INK.light})`;

/**
 * The three named levels below the primary ink — Apple's `secondaryLabel`,
 * `tertiaryLabel` and `quaternaryLabel`, on vitrea's material (W27a).
 *
 * One foreground level per surface was never the whole of what an interface
 * needs: a caption, a disabled row, a separator's label all sit *under* the
 * primary ink, and an app with one token either writes all of them at full
 * strength or invents its own scale against a material it cannot see. These are
 * the same ink at reduced alpha, published beside `--vitrea-foreground` on both
 * tiers, so the scale is derived from the level the runtime resolved rather than
 * guessed against it.
 */
export const FOREGROUND_LEVELS = ["secondary", "tertiary", "quaternary"] as const;

export type ForegroundLevel = (typeof FOREGROUND_LEVELS)[number];

/**
 * Apple's own label alphas, and why they cannot simply be copied.
 *
 * `secondaryLabel` is 60% of the label colour, `tertiaryLabel` 30%,
 * `quaternaryLabel` 18% (16% in the dark appearance; one number is published
 * here, because the token's two branches are the two *inks* and the difference
 * between 0.18 and 0.16 is a quarter of an 8-bit step at this ink's contrast).
 *
 * 0.6 is not an arbitrary number: the platform's ink over the platform's white
 * background reaches WCAG's 4.5 body-text floor at almost exactly that alpha
 * (`inkAlphaHoldingContrast` says 0.601 on a white surface). **Glass is never a
 * white background.** The dark ink is chosen where the level runs from
 * `foregroundCrossover` upward, and 60% of it lands at 4.49 over an encoded 1.0
 * and 3.21 over the shipped regular material's darkest reachable level of 0.665.
 * Publishing 0.6 flat would publish a token that fails the floor on the very
 * material it is published for.
 *
 * So **secondary is raised to whatever holds the floor against every colour the
 * surface can be sitting on**, and is Apple's 0.6 wherever that already does —
 * which is most of the dark appearance, where the light ink over a level of 0.23
 * has 4.5 in hand at 0.47. Two things that phrasing is careful about, both of
 * them W27a's review findings:
 *
 *  - **Colour, not level.** A ratio stops being a function of luminance the
 *    moment either side is chromatic, and this material is chromatic exactly
 *    when an author tinted it. `foregroundLevelInks` is given the composite the
 *    tier actually draws, so a full-strength magenta is solved against magenta.
 *  - **Every colour, not the resolved one.** Where the backdrop is unknown the
 *    surface's own bracket still is not, so the solve runs at both of its ends
 *    and takes the harder. That covers the `light-dark()` case, where the
 *    primary is chosen by colour scheme rather than by level and there is no
 *    single surface to be right about.
 *
 * Where even an opaque ink misses the floor, secondary collapses onto the
 * primary: a surface whose *first* level cannot carry body text has no second
 * one to offer, and saying so is better than publishing a level that lies. That
 * makes the guarantee relative and total at once — secondary is never worse than
 * the primary, and holds 4.5 wherever the primary can.
 *
 * Tertiary and quaternary are **not** raised. WCAG's 4.5 is the body-text floor
 * and these two are not body text — they are Apple's own supporting and
 * decorative tiers — so lifting them to it would collapse the whole scale onto
 * one value and destroy the thing being published. What they get instead is the
 * floor stated (here, and in the README) and, for quaternary, the diagnostic
 * Apple's own guidance asks for: it is too low-contrast on a thin material.
 */
const FOREGROUND_LEVEL_ALPHA: Readonly<Record<ForegroundLevel, number>> = {
  secondary: 0.6,
  tertiary: 0.3,
  quaternary: 0.18,
};

/** `--vitrea-foreground-secondary` and its two siblings, in level order. */
export const FOREGROUND_LEVEL_TOKENS = {
  secondary: "--vitrea-foreground-secondary",
  tertiary: "--vitrea-foreground-tertiary",
  quaternary: "--vitrea-foreground-quaternary",
} as const satisfies Record<ForegroundLevel, string>;

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
  FOREGROUND_LEVEL_TOKENS.secondary,
  FOREGROUND_LEVEL_TOKENS.tertiary,
  FOREGROUND_LEVEL_TOKENS.quaternary,
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
   * The affine the sharp layer's filter carries, where it carries one (W17 G1).
   *
   * Reported for the honesty core's own reason: with a transfer present the tint
   * is drawn inside the filter in linear light and L3 carries no tint at all,
   * and a capture cell or a readout has to be able to read which of the two
   * forms actually drew rather than infer it from the engine's row.
   */
  readonly tintTransfer?: CssTierTintTransfer;
  /**
   * Which form the tint drew (W17 G1; Decision Log 4 (c)) — the exact remainder
   * inside the linear-light filter, or W16's encoded overlay where the chain's
   * own quantum is coarser than the page's. Reported for the honesty core's
   * reason: the dark scheme keeps the second, and a readout has to say so.
   */
  readonly tintForm?: "linear" | "encoded";

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
  /**
   * The outer shadow this surface resolved, as a `box-shadow` value — the same
   * string the carrier above wrote, or `"none"` where the profile declines the
   * facet (W18 G1).
   *
   * It is reported rather than only written because carrier B paints a member's
   * shadow from a DIFFERENT element than the one this render describes: the
   * group's last-painted host holds one child per member, and that child has to
   * carry this member's own value. Handing back the resolved string is what keeps
   * the amplitude, the offset, the spread and the blur derived once here instead
   * of a second time beside the container.
   */
  readonly outerShadow: string;
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
  /**
   * This surface's material, with its ALPHA ALREADY FOLDED by the caller.
   *
   * `cssTierDeclarations` runs the accessibility fold over these optics but keeps
   * `optics.tintAlpha` exactly as it is given, discarding the alpha that
   * `opticsUnderPolicy` would have produced (W17 Decision Log 2 (b); the reason
   * is written out at `policyOptics` in that function). The reduced-transparency
   * and increased-contrast lift, and the size law's occlusion, both land on the
   * SOURCE alpha before the W9 response solve, which is upstream of anything this
   * function can see — `root.ts` does that folding where it builds
   * `occludedSource` and hands the result down.
   *
   * So a direct caller of this tier owes the same thing: under a reduced
   * transparency or increased contrast policy, pass optics whose `tintAlpha`
   * already carries the fold. Passing the nominal material and relying on
   * `policy` to raise it yields a surface drawn at nominal opacity, with the
   * policy honoured in every other declaration and not in the one the user asked
   * for.
   */
  readonly optics: MaterialOptics;
  /**
   * The same conversion BEFORE the author tint was folded into it — what
   * `cssOpticsFromSource` returned, which `optics` is `tintedCssOptics`' fold of
   * (W19 G1; claims §5.80 §7).
   *
   * Only the `linear` form reads it, and it reads it for one thing: the colour
   * `T` the transfer table is solved to composite back over. The table exists so
   * that L3's floor overlay `(T, α₃)` and the filter's remainder compose to the
   * material exactly, and that solve is a statement about the MATERIAL — the
   * author's tint is a second layer over the pair, not a change to either half of
   * it. Solving on the folded colour instead is what W19 found: on a saturated
   * seed `T_folded` is near zero in one channel, the table's argument
   * `(E(M) − α₃·E(T_folded))/(1 − α₃)` then exceeds one on that channel, and an
   * `feComponentTransfer` table clamps — a per-channel hue loss that fires inside
   * the filter, before the heavy layer's Gaussian, and is not recoverable from the
   * composite (claims §5.80 §2 (iv)).
   *
   * **Absent means today's behaviour, not a throw.** A direct caller that passes
   * only `optics` gets the declarations this function wrote before W19: the table
   * solved on `optics.tint` and L3 painting the author's layer at the author's own
   * strength. That caller has told this function nothing about which of the two
   * colours it holds, and guessing would be worse than leaving it where it was.
   * `root.ts` passes both.
   */
  readonly untintedOptics?: MaterialOptics;
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
  /**
   * The renderer's own composite for this surface, in linear light — what the
   * tint's lerp becomes when the tier carries it inside its filter (W17 G1;
   * Decision Log 2 (c)).
   *
   * Absent on a caller that has no backdrop chain to resolve it from, and
   * ignored on an engine that does not render a reference filter inside
   * `backdrop-filter`: both fall back to the `rgba()` overlay, which is the form
   * every engine can draw and the level the conformance rows record for it.
   */
  readonly interior?: CssTierInterior;
  /**
   * The author's tint as its own layer — the encoded shade the seed resolves to
   * and the author's opacity (W10, re-split by W17 G1).
   *
   * The tier folds that layer and the material's `rgba()` into one declaration
   * wherever it writes both (`tintedCssOptics`), and `optics` already carries the
   * fold. With the material's half inside the filter there is no fold left to
   * write, so the layer is needed unfolded — and only then. A caller that does
   * not pass one on a tinted surface with an interior draws no author tint,
   * which is why `root.ts` resolves the two together.
   */
  readonly authorLayer?: {
    readonly color: Rgb255;
    readonly strength: number;
  };
  /**
   * This surface's presence, 0..1 — how much of the material is there (W27d).
   *
   * The mechanism and its residuals are §Presence rides the weights, not the
   * widths, at the head of this file. What a caller owes is the number: absent
   * is 1, which is a fully materialized surface and exactly the declarations
   * this function wrote before the channel existed — every term is a
   * multiplication and 1 is its identity, so nothing at rest moves by a bit.
   *
   * At 0 the surface is `Glass.identity`: no filter, no tint, no rim, no glow,
   * and `outerShadow` comes back `"none"` on every carrier, so a container
   * painting a member's shadow paints nothing for it either.
   *
   * Out-of-range values are clamped rather than refused. The channel is driven
   * by a motion kernel and read from a custom property an app can write, and a
   * surface that vanished because a driver overshot to 1.0000001 would be a
   * failure this function is in a position to simply not have.
   */
  readonly materialization?: number;
  /**
   * Whether a driver is writing this surface's material every frame (W27d).
   *
   * A CSS transition is this tier's own interpolation between two RESTING
   * states, and a driver is already interpolating. Declared together the
   * transition chases each frame's value with its own ease, so the curve that
   * draws is neither the driver's nor the transition's and the material lands
   * late; while a driver runs the tier therefore declares no transition at all,
   * on the host and on all three layers.
   *
   * It is the caller's flag because only the caller knows a driver is running,
   * and it is separate from the presence because a presence can be authored and
   * held: a surface parked at 0.5 transitions like any other.
   */
  readonly driven?: boolean;
  /**
   * Which element carries this surface's outer shadow (W18 G1; charter Decision
   * Log 2 (1)). See `css-tier-shadow.ts` for the mechanism and the three values.
   *
   * `"layer"` is the default because it is the carrier every surface can have:
   * the shadow joins L3's `box-shadow` list and a surface's own filters, which
   * paint before L3, stop sampling it. `"host"` is the fallback a clipping host
   * forces and is what this tier drew everywhere before W18. `"group"` says the
   * group's last-painted member is painting this surface's shadow instead, so
   * neither the host nor L3 writes one — but the resolved value still comes back
   * on `CssTierRender.outerShadow` for that member to use.
   */
  readonly shadowCarrier?: CssTierShadowCarrier;
}

/**
 * The renderer's interior composite for one surface, in linear light (W17 G1).
 *
 * Three numbers and nothing else, because that is the whole of what the tier's
 * filter can carry: the alpha and the tint of the lerp the shader runs — in the
 * SHADER's order, with the size law's occlusion inside the alpha before the W9
 * response solve and the inner shadow folded into the pair — and the derived
 * light of the terms the tier does not draw. `optics.ts` resolves all three;
 * this module turns them into a transfer and never computes one of them.
 */
export interface CssTierInterior {
  /** The lerp's alpha, after every fold, 0..1. */
  readonly tintAlpha: number;
  /** The lerp's tint, linear light, per channel. */
  readonly tint: readonly [number, number, number];
  /** `X` — the rim band's ambient light and the highlight's, linear (`interiorBandLight`). */
  readonly addedLight: number;
}

/**
 * The affine the sharp layer's reference filter applies to the filtered backdrop
 * in linear light — the tint's lerp itself, carried as a primitive rather than
 * converted into an encoded-space overlay (W17 G1; Decision Log 2 (c)).
 *
 * The renderer's composite is `(1 − α)·b + α·T + X` per channel in linear light,
 * which is an affine in `b`; an `feComponentTransfer` of `type="linear"` inside
 * a `color-interpolation-filters="linearRGB"` chain is exactly an affine in
 * linear light. So the conversion the tier used to solve — one encoded alpha
 * matched to a linear lerp at one declared backdrop level — has nothing left to
 * solve: the form is exact per pixel, with no free parameter and no privileged
 * point on the backdrop's distribution.
 *
 * **Exact per pixel is not exact per cell, and the two residuals that stand
 * between them are derived rather than assumed** (W17 G1, evaluated by
 * `results/2026-09-04-w17-css-interior-level/g1/residuals.ts` on the three W16
 * probe cells over the real fixture background, at the tier's own two widths and
 * its own ramp).
 *
 *  1. **The page's encoded-space mix of the two tinted layers under the mask.**
 *     L2 blurs L1's OUTPUT, and the compositor mixes the two by the mask's alpha
 *     in the page's encoded eight-bit space, where the renderer mixes its two
 *     components in linear light before it tints. The difference is second order
 *     in the sharp-heavy difference through the encode's curvature, and the
 *     affine scales that difference by `1 - alpha` before the encode sees it, so
 *     the same residual the untinted body carried at W16 is smaller here on both
 *     counts. Measured: **-0.0041 / -0.0040 / -0.0040 of the interior level at
 *     dpr 1 and -0.0009 / -0.0022 / -0.0009 at dpr 2** on `rrect-md`, the
 *     capsule and `rrect-ml`, against **-0.037 / -0.031 / -0.036** and
 *     **-0.013 / -0.026 / -0.012** for the same mix untinted -- a factor of 7 to
 *     14. Worst single pixel 0.0085 at dpr 1 and 0.0042 at dpr 2. It is
 *     one-signed and negative, which is the direction the tier's measured
 *     -0.006 against the GPU tier at dpr 1 sits in.
 *  2. **W16's effective kernel width.** The tier writes the renderer's kernel's
 *     effective Gaussian width through one ratio per scale (1.380 at dpr 1,
 *     1.485 at dpr 2), and each span's own reading differs from it by -0.50% to
 *     +0.50% at dpr 1 and -1.00% to -0.04% at dpr 2. A Gaussian is normalised,
 *     so that error moves no mean: re-blurring at each cell's own asked-for
 *     width moves the interior level by **0.000000 to 0.000003**. It is a spread
 *     residual and not a level one, which is why it is named here and gated by
 *     S3 rather than by the level clause.
 */
export interface CssTierTintTransfer {
  /** The lerp's alpha after every fold — the shader-order value. */
  readonly tintAlpha: number;
  /** The lerp's tint, linear light, per channel. */
  readonly tint: readonly [number, number, number];
  /** `X`, the band's derived light, linear. */
  readonly addedLight: number;
  /** `α₃`, the alpha the encoded overlay keeps on L3 (`cssTierFloorAlpha`). */
  readonly floorAlpha: number;
  /** `E(T)` per channel — the overlay's own encoded level, 0..1, as L3 writes it. */
  readonly floorEncoded: readonly [number, number, number];
}

/**
 * The floor the encoded overlay keeps — **an existing constant of this tier,
 * named rather than derived** (W17 G1; Decision Log 4 (a)).
 *
 * It is `MATERIAL_OPTICS.clear.tintAlpha`: the least tint this tier draws on the
 * shipped profile, on the variant whose whole point is to be persistently more
 * transparent. "The surface always paints a real tint" is a statement about the
 * least it paints, so the least it paints is the number, and nothing here is new
 * or fitted to this wave.
 *
 * **Why the floor and not the group's own alpha**, which is the other reading of
 * the ruling and was measured first: the filter carries the REMAINDER after the
 * overlay, so everything the filter draws is amplified by `1/(1 − α₃)` on its way
 * into the composite — the two layers' encoded-space mix under the mask along
 * with it. At the regular variant's own alpha that factor is 2.99 and the probe
 * cells read +0.018 to +0.038 over the GPU tier; at the floor it is 1.36. The
 * floor is therefore the smallest alpha that satisfies the doctrine rather than
 * the largest, and that is the direction the arithmetic wants too.
 *
 * It is also `≤` the folded alpha of any group on either variant, which is the
 * ruling's non-negativity condition: every fold between the profile and the
 * composite — the response solve's alpha target, the collapse, the size law's
 * occlusion, the regime's lift — moves the source alpha upward and never
 * downward, and `cssTintAlpha` is monotone in it.
 */
export function cssTierFloorAlpha(optics: MaterialOptics): number {
  void optics;
  return CSS_TIER_TINT_FLOOR_ALPHA;
}

/**
 * The transfer's parameters for one interior composite and one floor.
 *
 * The numbers, not the table: `css-tier-layers.ts` samples them when it builds
 * the definition, because the count of points is chosen by measuring the
 * interpolation error and this module is on the paint path every frame. What
 * this module owns is which numbers the filter is built from, and the `id` that
 * names them.
 */
export function cssTierTintTransfer(
  interior: CssTierInterior,
  floorAlpha: number,
  floorEncoded: readonly [number, number, number],
): CssTierTintTransfer {
  return {
    tintAlpha: Math.min(1, Math.max(0, interior.tintAlpha)),
    tint: [
      Math.max(interior.tint[0], 0),
      Math.max(interior.tint[1], 0),
      Math.max(interior.tint[2], 0),
    ],
    addedLight: Math.max(interior.addedLight, 0),
    floorAlpha: Math.min(1, Math.max(0, floorAlpha)),
    floorEncoded: [floorEncoded[0], floorEncoded[1], floorEncoded[2]],
  };
}

/**
 * The `id` of the reference filter for one σ, in CSS px, and the transfer it
 * carries where it carries one.
 *
 * Deterministic in the σ and quantised the same way the declaration is, so the
 * declaration and the definition cannot name different numbers, and two surfaces
 * at the same width share one `<filter>` rather than each building its own.
 *
 * Since W17 G1 the sharp filter's definition is **per group** rather than per σ:
 * it carries the group's own tint, whose alpha and colour follow the backdrop
 * the group sampled, so two surfaces at one width over different backdrops need
 * different definitions and the `id` has to say so. The coefficients are
 * quantised to a ten-thousandth — a quarter of an eight-bit code at the top of
 * the range — so that a backdrop drifting inside the quantum reuses one
 * definition instead of rebuilding it every frame.
 */
export function referenceFilterId(
  prefix: string,
  sigmaCssPx: number,
  transfer?: CssTierTintTransfer,
): string {
  const quantised = (values: readonly number[]): string =>
    values.map((value) => String(Math.round(Math.max(value, 0) * 10000))).join("-");
  let id = `${prefix}-b${String(Math.round(sigmaCssPx * 100))}`;
  if (transfer !== undefined) {
    id += `-t${quantised([transfer.tintAlpha, ...transfer.tint, transfer.addedLight, transfer.floorAlpha, ...transfer.floorEncoded])}`;
  }
  return id;
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
  /**
   * The colour behind the glyphs and the pair the surface's bracket reaches —
   * what the named levels' contrast floor is solved against. The primary ink
   * does not read either: which ink is readable is a threshold on luminance, and
   * `level` carries that. See `foregroundLevelInks`.
   */
  readonly composite?: EncodedRgb;
  readonly compositeBounds?: readonly [EncodedRgb, EncodedRgb];
}): StyleDeclarations {
  const primary = foregroundInk(input);
  const levels = foregroundLevelInks(input);
  return {
    "--vitrea-foreground": primary,
    [FOREGROUND_LEVEL_TOKENS.secondary]: levels.secondary,
    [FOREGROUND_LEVEL_TOKENS.tertiary]: levels.tertiary,
    [FOREGROUND_LEVEL_TOKENS.quaternary]: levels.quaternary,
  };
}

/**
 * `rgb(28 28 30 / 0.6)` — the modern syntax, which every engine vitrea targets
 * parses. Rounded **up** rather than to nearest: the third decimal is finer than
 * an 8-bit step, and a value a hair more opaque than the solve is the only side
 * of it a contrast floor may land on.
 */
const inkAtAlpha = (ink: Rgb255, alpha: number): string =>
  `rgb(${ink[0]} ${ink[1]} ${ink[2]} / ${Math.ceil(Math.min(1, alpha) * 1000) / 1000})`;

/**
 * The alpha one named level is published at, against every colour the glyphs
 * could be sitting on.
 *
 * `surfaces` is one colour where the backdrop is known and the pair the bracket
 * reaches where it is not; the alpha taken is the largest any of them needs, so
 * the published floor holds over all of them rather than over a representative
 * one. See `FOREGROUND_LEVEL_ALPHA` for where the numbers come from and why only
 * secondary is raised, and `foregroundLevelInks` for why the bracket is always
 * available on a shipped path.
 *
 * `undefined` from `inkAlphaHoldingContrast` means an opaque ink misses the
 * floor on that colour too, and there `1` is the honest answer rather than the
 * largest number below it.
 */
function alphaFor(
  level: ForegroundLevel,
  ink: Rgb255,
  surfaces: readonly EncodedRgb[],
): number {
  const nominal = FOREGROUND_LEVEL_ALPHA[level];
  if (level !== "secondary") return nominal;

  let required = nominal;
  for (const surface of surfaces) {
    const holding = secondaryFloorAlpha(ink, surface);
    if (holding === undefined) return 1;
    required = Math.max(required, holding);
  }
  return required;
}

/**
 * `inkAlphaHoldingContrast`, memoised on the exact colour asked about.
 *
 * These declarations are recomputed for every surface on every frame — the tier
 * writes its whole material each frame so that nothing can be left stale — and
 * the solve is thirty halvings over three `Math.pow` each, so it is not
 * something to run per surface per frame unmemoised.
 *
 * Keyed on the colour **exactly** rather than on a quantisation of it. An
 * earlier form keyed on the level rounded to 1/2048 and had to argue about which
 * direction to round so that the cached answer could not land under the floor;
 * that argument was available for a scalar and is not for a triple, where "the
 * harder colour" is not a direction. The distinct colours a page produces are
 * the distinct (material, backdrop tone) pairs it draws, which is a small number
 * that changes when the page does, so an exact key hits in the steady state. The
 * cap is there for the pathological case — a backdrop tone that jitters every
 * frame — and clearing wholesale is right for it: the entries a jittering page
 * accumulated are exactly the ones it will not ask for again.
 */
const SECONDARY_FLOOR_CACHE_CAP = 4096;

const secondaryFloorAlphas = new Map<string, number | undefined>();

function secondaryFloorAlpha(ink: Rgb255, surface: EncodedRgb): number | undefined {
  const key = `${ink === FOREGROUND_INK_CHANNELS.dark ? "d" : "l"}:${String(surface[0])}:${String(surface[1])}:${String(surface[2])}`;
  if (secondaryFloorAlphas.has(key)) return secondaryFloorAlphas.get(key);
  const solved = inkAlphaHoldingContrast(ink, surface, WCAG_BODY_TEXT_CONTRAST);
  if (secondaryFloorAlphas.size >= SECONDARY_FLOOR_CACHE_CAP) secondaryFloorAlphas.clear();
  secondaryFloorAlphas.set(key, solved);
  return solved;
}

/**
 * The three named levels, in the same four regimes the primary ink resolves in
 * (W27a). Split out of `foregroundDeclarations` so the arithmetic is testable on
 * its own, exactly as `foregroundInk` is.
 *
 * Two regimes publish the primary ink unchanged at every level, and both are
 * accessibility rather than aesthetics. Under **forced colours** there is no
 * glass and the palette is the platform's; a reduced-alpha `CanvasText` is
 * precisely the thing forced colours exists to prevent. Under **increased
 * contrast** the preference asked for more contrast, and answering it with three
 * dimmer inks would be answering the opposite question. In both the scale
 * collapses, deliberately, and an app that reads a level token gets a legible
 * colour rather than nothing.
 *
 * ## What the floor is solved against
 *
 * `composite` is the colour the glyphs sit on where the backdrop is known — a
 * declared hint or a measured tone. Where it is not, `compositeBounds` is the
 * pair the surface's own bracket reaches, over the darkest backdrop and the
 * brightest, and **the floor is solved against both and the harder answer
 * taken**. That is a real guarantee rather than a representative one: every
 * colour the surface can reach lies between those two, on a ratio that is
 * monotone in the backdrop, so an alpha holding at both ends holds everywhere
 * between them.
 *
 * It matters most in exactly the case the primary ink cannot decide. There the
 * primary is `light-dark()` and the browser picks by colour scheme rather than
 * by level, so **each branch is solved separately, against the end that is worse
 * for that branch's ink**. Publishing Apple's flat 0.6 on both — which is what
 * this did before the review — published 4.49-over-white on a surface that may
 * be nowhere near white.
 *
 * A caller that passes neither falls back to `level` as a neutral, and to
 * Apple's own alphas where there is no level either. Both are direct-caller
 * fallbacks and neither is reachable from the runtime: `cssTierDeclarations` and
 * `root.ts` always pass the bounds, because a surface always has them — they are
 * a function of its material alone and need no backdrop at all.
 */
export function foregroundLevelInks(input: {
  readonly policy: ResolvedAccessibilityPolicy;
  readonly level?: number;
  readonly mapping?: CssTierMapping;
  /** The colour behind the glyphs, where the backdrop is known. */
  readonly composite?: EncodedRgb;
  /** The colours it reaches over the darkest and brightest backdrops. */
  readonly compositeBounds?: readonly [EncodedRgb, EncodedRgb];
}): Readonly<Record<ForegroundLevel, string>> {
  const mapping = input.mapping ?? CSS_TIER_MAPPING;
  const { material } = input.policy;
  const flat = (value: string): Readonly<Record<ForegroundLevel, string>> => ({
    secondary: value,
    tertiary: value,
    quaternary: value,
  });

  if (material.glass === "none") return flat("CanvasText");
  if (material.foreground === "near-monochrome") return flat("light-dark(#000, #fff)");

  /**
   * The colours one branch's ink has to hold its floor against. The exact
   * composite where there is one; otherwise the bracket's two ends, which
   * between them cover every colour the surface can reach.
   */
  const surfacesFor = (fallbackLevel: number | undefined): readonly EncodedRgb[] => {
    if (input.composite !== undefined) return [input.composite];
    if (input.compositeBounds !== undefined) return input.compositeBounds;
    return fallbackLevel === undefined ? [] : [neutralComposite(fallbackLevel)];
  };

  if (input.level === undefined) {
    // No level means no single ink: `light-dark()` hands the choice to the colour
    // scheme, so both branches are published and each has to hold on its own.
    const surfaces = surfacesFor(undefined);
    const branch = (level: ForegroundLevel): string => {
      const dark = inkAtAlpha(
        FOREGROUND_INK_CHANNELS.dark,
        alphaFor(level, FOREGROUND_INK_CHANNELS.dark, surfaces),
      );
      const light = inkAtAlpha(
        FOREGROUND_INK_CHANNELS.light,
        alphaFor(level, FOREGROUND_INK_CHANNELS.light, surfaces),
      );
      return `light-dark(${dark}, ${light})`;
    };
    return {
      secondary: branch("secondary"),
      tertiary: branch("tertiary"),
      quaternary: branch("quaternary"),
    };
  }

  const surfaceLevel = input.level;
  const ink =
    surfaceLevel >= mapping.foregroundCrossover
      ? FOREGROUND_INK_CHANNELS.dark
      : FOREGROUND_INK_CHANNELS.light;
  const surfaces = surfacesFor(surfaceLevel);
  return {
    secondary: inkAtAlpha(ink, alphaFor("secondary", ink, surfaces)),
    tertiary: inkAtAlpha(ink, alphaFor("tertiary", ink, surfaces)),
    quaternary: inkAtAlpha(ink, alphaFor("quaternary", ink, surfaces)),
  };
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
  /*
   * A declared presence and a presence of 1 are the same material and not the
   * same record (W27d). L1 has no weight of its own until this channel exists,
   * and a caller that has never heard of it must keep the declarations this
   * function wrote before it did — the same rule `spanPx` follows for the size
   * law, and the reason the pre-fold declarations W19 recorded still compare.
   *
   * What a caller owes in exchange is consistency: a caller that declares a
   * presence on one frame declares one on every frame, because a property that
   * stopped being written would leave the driver's last value on the element.
   * `root.ts` passes the channel's value unconditionally.
   */
  const declaredPresence =
    surface.materialization === undefined ? undefined : clamp01(surface.materialization);
  const presence = declaredPresence ?? 1;
  const driven = surface.driven === true;
  /*
   * The accessibility fold, minus its occlusion arm (W17 G1; Decision Log 2 (b)).
   *
   * The regime's lift and the size law's occlusion both land on the SOURCE alpha
   * now, before the W9 response solve, which is where the shader puts them: the
   * solve exists to land the composite's mean on the measured response, and an
   * alpha raised after it lands the mean above the response by the raise times
   * the tint's excess over the backdrop — worth +0.015 to +0.027 of this tier's
   * interior level, one-signed, on 15 of the 44 untinted cells of the bed
   * (claims §5.74 §3). The alpha this function receives is therefore already
   * lifted, sized and converted, and `opticsUnderPolicy` folds five things of
   * which the caller now owns exactly one — so the alpha is put back rather than
   * the fold being forked into two functions that could drift.
   */
  const policyOptics: MaterialOptics = opticsAtPresence(
    {
      ...opticsUnderPolicy(surface.optics, policy.material, surface.policyFold),
      tintAlpha: surface.optics.tintAlpha,
    },
    presence,
  );
  /*
   * The size law's scattering facet, applied after the accessibility fold and
   * before anything is written (W2). Its occlusion facet used to be applied here
   * too and is the caller's since W17 G1 — see `policyOptics` above.
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
      : { ...policyOptics, blurRadius: projectedSigma };
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
  /*
   * The presence scales the compositing alpha and not the shadow's lengths
   * (W27d). The offset, the blur and the spread are the caster's own geometry —
   * a materializing surface sits where it sits and is lit from where it is lit —
   * and what a half-present surface occludes is half of what a present one does.
   * `outerShadowDeclaration` rounds to a thousandth, so a presence small enough
   * to round the alpha away resolves `"none"` on every carrier by itself.
   */
  const shadowAlpha =
    cssTierShadowAlpha(shadowSource, surface.backdropLuminance, surface.spanPx ?? 0, sizeK)
    * presence;
  /*
   * The resolved shadow, and which element paints it (W18 G1).
   *
   * The value is derived once here on every carrier, because it is the material's
   * and not the element's: carrier B hands it to the group's last-painted member
   * and carrier A to L3, and a second derivation beside either of them would be a
   * second copy of the profile's own numbers. The default carrier is `layer` —
   * the one every surface can have — so a caller that says nothing gets the
   * shadow out of its own sampled backdrop.
   */
  const shadow = outerShadowDeclaration(shadowSource, shadowAlpha);
  const shadowCarrier: CssTierShadowCarrier = surface.shadowCarrier ?? "layer";
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
        transition: transitionFor(
          policy,
          ["background-color", "border-color", "box-shadow"],
          driven,
        ),
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
      outerShadow: "none",
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
    presence,
  });
  const prefix = surface.filterIdPrefix ?? DEFAULT_FILTER_ID_PREFIX;
  const tint = rgba(optics.tint, optics.tintAlpha);
  const border = rgba(optics.border, optics.borderAlpha);
  /*
   * Where the tint is drawn (W17 G1; Decision Log 2 (c)).
   *
   * With the interior composite resolved and a reference filter to carry it, the
   * lerp itself goes into the SHARP layer's filter as an affine in linear light
   * and L3 stops carrying a tint: the two are the same quantity and drawing both
   * would draw it twice. A Gaussian is linear and normalised, so an affine at L1
   * passes through L2's heavy step unchanged and reaches the composite exactly
   * once — which is why the stage goes on the sharp filter alone rather than on
   * both (that would apply it twice) or on the heavy one (that would leave the
   * sharp share untransformed wherever the mask is open).
   *
   * The author's tint (W10) is the one thing still laid on L3 there, and it is
   * laid as the author's own layer rather than as the fold: the material's half
   * of that fold now lives in the filter, so `tintedCssOptics`'s one `rgba()` is
   * no longer this layer's to write. The two forms compose to the same
   * expression — `(1 − s)·(material composite) + s·layer` — with the material
   * composite taken in linear light instead of encoded, which is the change this
   * wave is.
   */
  /*
   * Which form draws, and what each half of it carries (W21 Decision Log 4 (a);
   * W17 Decision Log 4 (a), (c), superseded in part; claims §5.90 §6).
   *
   * `encoded` is W16's: one `rgba()` over the blurred backdrop at the group's
   * whole converted alpha, composited in the page's own space. `linear` is W17's
   * re-form: L3 keeps that same overlay at the FLOOR alpha, which is the tint
   * this tier painted at rest and is what the contrast-floor doctrine asks for,
   * and the sharp layer's filter carries the exact remainder as a table.
   *
   * **The choice between them is a comparison of the two forms' errors**, taken
   * at this surface's own backdrop and in one unit. It used to be the chain's
   * quantum against the page's alone, which weighed the linear form's error and
   * never the encoded form's — right wherever the encoded form is nearly exact,
   * and wrong by two to four times the level over a structured dark backdrop,
   * which is what sent the whole dark scheme to the worse drawing (§5.90 §6).
   * `cssTintForm` reads both: the linear chain's half-step against
   * `cssTintEncodedFormError`, which is what the `rgba()` this tier would lay
   * down actually composites to, against what the renderer draws.
   *
   * The error is measured on the UNTINTED conversion, for the same reason the
   * table below is solved on it (W19 G1): `interior` states the MATERIAL's
   * composite, so the drawing it is compared against has to be the material's
   * overlay and not the author's fold over it — otherwise a strong author tint
   * would move the boundary, which W19 measured it must not.
   *
   * Which is also why a caller that passes no `untintedOptics` keeps the reach
   * (`linearChainReaches`) instead. It has said nothing about which of the two
   * colours its `optics` holds, so the tier has no pair it can honestly compare
   * and falls back to the question W17 answered with the same information. The
   * runtime always passes it (`root.ts`), so this is a direct caller's fallback
   * and not a second rule on any shipped path.
   */
  const interior = surface.interior;
  const formBackdrop = surface.backdropLuminance ?? mapping.referenceBackdropLuminance;
  const material = surface.untintedOptics;
  const nearerForm: "linear" | "encoded" | undefined =
    interior === undefined
      ? undefined
      : material === undefined
        ? linearChainReaches(cssTierCompositeLevel(interior, formBackdrop))
          ? "linear"
          : "encoded"
        : cssTintForm(cssTintEncodedFormError(material, interior, formBackdrop));
  const tintForm: "linear" | "encoded" =
    nearerForm === "linear" && body.filter === "reference-filter" ? "linear" : "encoded";
  const floorAlpha = cssTierFloorAlpha(optics);
  /*
   * The presence is on L3's overlay and NOT on the transfer the filter carries
   * (W27d; §Presence rides the weights, residual 3).
   *
   * The table is solved so that the floor and the remainder compose to the
   * material, and its parameters are the definition's own name: solving it at
   * `α₃·p` would make the sharp filter's `id` a function of the driver, which is
   * a `<filter>` rebuilt and a table re-solved every frame of every transit. So
   * the definition stays the resting material's, L3's overlay carries the
   * presence alone, and the identity the two hold together is exact at 1, exact
   * at 0 and an approximation between.
   */
  const overlayFloorAlpha = floorAlpha * presence;
  /*
   * Which colour the floor overlay is, and what L3 paints over the table (W19 G1;
   * claims §5.80 §7, charter Decision Log 2).
   *
   * `floorOptics` is the UNTINTED conversion wherever the caller passed one, and
   * `optics` — which on an untinted surface is the same object — wherever it did
   * not. The two matter only on a tinted surface, and there the whole of W19 is
   * that the table must be solved on the material's own colour: `(1 − α₃)·F(b) +
   * α₃·E(T) = E(M)` is the identity W17 solved for, and it is an identity about
   * the material, so the colour in it is the material's.
   *
   * L3 then carries the author's layer folded over that same floor overlay rather
   * than laid on the table's output at the author's own strength. The composite is
   * the algebra of the fold and nothing else:
   *
   *     (1 − α″)·F + α″·C″ = (1 − s)(1 − α₃)·F + (1 − s)·α₃·E(T) + s·E(L)
   *                        = (1 − s)·E(M) + s·E(L)
   *
   * which is `tintedMaterialColour`'s expression, at every strength rather than
   * only at `s = 1` where the opaque layer covered the table's output anyway. The
   * floor survives the change by construction, because `α″ = 1 − (1 − s)(1 − α₃)`
   * is at least `α₃` for every strength (`foldedOverlay`) — W17 Decision Log 4
   * (a)'s doctrine held at strengths this tier used to paint under it, measured at
   * six of eighteen captured tinted cells before the fold.
   *
   * What it costs is the eight-bit quantum: `C″` is written as a CSS colour and
   * rounds to `Rgb255`, worth 2.85e−3 of linear luminance in the identity — the
   * same quantum `rgba(L, s)` carried in the same measure, so nothing is spent
   * that the previous form was not already spending.
   *
   * W27c's inactive endpoint arrives through the same `authorLayer`: optics.ts
   * neutralizes the seed before shading it, and root.ts retains that shade
   * through collapse when the profile requests it. This fold still preserves
   * author strength. Its one uniform colour cannot follow the WebGPU shade's
   * per-pixel body luminance; that spatial residual is recorded in claims §5.130.
   */
  const floorOptics = surface.untintedOptics ?? optics;
  const transfer =
    tintForm === "linear" && interior !== undefined
      ? cssTierTintTransfer(interior, floorAlpha, [
          floorOptics.tint[0] / 255,
          floorOptics.tint[1] / 255,
          floorOptics.tint[2] / 255,
        ])
      : undefined;
  /*
   * The author's own layer is a term of the material like any other, so the
   * presence scales its strength and not its colour (W27d): a tinted surface
   * materializes as the tinted material rather than arriving through a hue the
   * profile never draws.
   */
  const authorLayer =
    surface.authorLayer === undefined
      ? undefined
      : { ...surface.authorLayer, strength: surface.authorLayer.strength * presence };
  const foldedAuthorLayer =
    transfer === undefined || authorLayer === undefined || surface.untintedOptics === undefined
      ? undefined
      : foldedOverlay({ tint: floorOptics.tint, tintAlpha: overlayFloorAlpha }, authorLayer);
  const overlayTint =
    transfer === undefined
      ? tint
      : foldedAuthorLayer !== undefined
        ? rgba(foldedAuthorLayer.tint, foldedAuthorLayer.tintAlpha)
        : authorLayer === undefined
          ? rgba(floorOptics.tint, overlayFloorAlpha)
          : rgba(authorLayer.color, authorLayer.strength);

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
   * A surface with no hint is not undecidable. The level is monotonic in the
   * backdrop, so bracketing it over the whole range often decides the ink
   * outright. Where the bracket straddles the crossover the backdrop really does
   * decide, and the `light-dark()` default stands.
   *
   * **The bracket is taken on every surface, tinted or not** (W27a; closes the
   * tech-debt entry "The untinted material's ink is still decided by the colour
   * scheme"). W3 wired this in for author-tinted surfaces only and left the
   * untinted material where it was, on the reasoning that the profile's neutral
   * tint is a calibration constant rather than a declaration. That distinction
   * does not survive the material's measured opacity: what a reader sees behind
   * the glyphs is `mix(backdrop, tint, α)`, and at this tier's converted alpha
   * the neutral white tint dominates it just as an author's colour would. The
   * ink was then chosen by `light-dark()` — that is, by the colour scheme — so a
   * hintless surface in a dark scheme wore the light ink on a near-white body.
   * That is K5's failure class reached through the no-hint path, and the bracket
   * closes it with the same arithmetic on the same monotonicity: nothing is
   * guessed, because a bracket that lands wholly on one side of the crossover is
   * the answer the hinted path would have produced for any backdrop whatsoever.
   */
  const level =
    hintedLuminance !== undefined
      ? cssTierForegroundLevel(optics, hintedLuminance)
      : boundedForegroundLevel(cssTierForegroundBounds(optics), mapping.foregroundCrossover);
  /*
   * The same two questions as colours rather than levels, for the named ink
   * levels' contrast floor (W27a, review fix). The primary ink needs only the
   * level, because which ink is readable is a threshold on luminance; a *ratio*
   * is not a function of luminance once the surface is chromatic, and this
   * material is chromatic exactly when an author tinted it. `optics` here is the
   * tinted conversion, so this is the colour the tier actually lays down.
   *
   * The bounds are passed unconditionally, including on the hinted path where
   * they go unused: they cost two multiplies and they are what makes the
   * bracket's guarantee available wherever the backdrop is not known.
   */
  const compositeBounds = cssTierForegroundColourBounds(optics);
  const composite =
    hintedLuminance === undefined ? undefined : cssTierForegroundColour(optics, hintedLuminance);

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
     * **It no longer stays on the HOST, and that is W18 G1** (charter Decision
     * Log 2 (1)). It paints outside the border box, but the host's three filter
     * layers are the host's own children and are painted after it, and Chromium
     * samples a `backdrop-filter`'s backdrop over the region its kernel needs —
     * so a shadow on the host is inside its own body's blur, worth 0.0032 to
     * 0.0096 of this tier's interior level where the renderer moves by 0.00000
     * (claims §5.77 §3). The carriers that take it out of that backdrop are in
     * `css-tier-shadow.ts`; here the host writes the shadow only where the page
     * forces the fallback — a host whose `overflow` clips its children would crop
     * a shadow on L3 to the padding box, which is no shadow rather than a dimmer
     * one — and writes `none` otherwise, every frame, so a surface that changes
     * carrier does not leave the other one's value behind.
     *
     * `cssShadowBlurRadius` is where the two blur conventions meet: this property
     * takes twice the Gaussian's σ, while `filter: blur()` above takes σ itself.
     */
    "box-shadow": shadowCarrier === "host" ? shadow : "none",
    // A transition is declared on the element that carries the property, and the
    // host keeps the outer shadow's on every carrier: it is the property this
    // element writes, whether at its value or at `none`, and L3 declares its own.
    transition: transitionFor(policy, ["box-shadow"], driven),
    "--vitrea-tint": tint,
    "--vitrea-occlusion": String(Math.round(optics.tintAlpha * 1000) / 1000),
    "--vitrea-border-color": border,
    /*
     * Still the single-σ projection, and deliberately not either layer's width:
     * an app matching the material with its own `blur()` has to keep getting one
     * number, and the body's two widths belong in the readout and the capture
     * cell (`CssTierBody`) rather than in a public token.
     *
     * A presence IS folded into it, by the rule this token has always followed:
     * it publishes the width that is drawn, and at a presence the width drawn is
     * the presence's own. An app matching a materializing surface with its own
     * `blur()` therefore tracks it without reading the channel, and at zero the
     * token is zero because there the body is gone rather than lighter.
     */
    "--vitrea-blur": px(body.projectedSigmaCssPx),
    ...foregroundDeclarations({
      policy,
      mapping,
      compositeBounds,
      ...(level === undefined ? {} : { level }),
      ...(composite === undefined ? {} : { composite }),
    }),
  };

  return {
    host,
    layers: {
      sharp: sharpLayerDeclarations(
        body,
        optics,
        prefix,
        policy,
        declaredPresence,
        driven,
        transfer,
      ),
      heavy: heavyLayerDeclarations(body, optics.borderWidth, prefix, policy, presence, driven),
      overlay: overlayLayerDeclarations(
        optics,
        overlayTint,
        border,
        policy,
        shadowCarrier === "layer" ? shadow : "none",
        driven,
      ),
    },
    body: { ...body, tintForm, ...(transfer === undefined ? {} : { tintTransfer: transfer }) },
    outerShadow: shadow,
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
 *
 * Since W18 G1 that clip decides one more thing, and it is why the carrier is a
 * decision rather than a rule: a shadow on L3 under such a host is cropped to the
 * padding box, which is not a thinner shadow but no shadow at all. So a clipping
 * host keeps its shadow on the host, keeps sampling it, and says so
 * (`GlassGroupState.cssShadow: "host"`).
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
  presence: number | undefined,
  driven: boolean,
  transfer?: CssTierTintTransfer,
): StyleDeclarations {
  const weight = presence ?? 1;
  const blur = blurFunction(body.filter, body.sharpSigmaCssPx, prefix, transfer);
  /*
   * At zero presence the property is written at `none` rather than at a zero
   * width (W27d). `blur(0px)` and a `saturate()` still cost a render surface and
   * a pass over the backdrop to draw a surface the tier has decided draws
   * nothing, and the layer's own `opacity` below would hide the result either
   * way — so the honest declaration and the cheap one are the same one.
   */
  const filter = weight <= 0 ? "none" : `${blur} saturate(${optics.saturation})`;
  return {
    ...layerFrame(optics.borderWidth, -3),
    "backdrop-filter": filter,
    "-webkit-backdrop-filter": filter,
    /*
     * The body's presence, and the reason it is this property rather than the
     * width (§Presence rides the weights). A `backdrop-filter`'s output
     * composites into the element's own group, which is what makes an `opacity`
     * here a mix of the filtered body toward the raw backdrop — the same
     * mechanism W16 measured for L2's flat share, bit-identical to a uniform
     * mask (claims §5.71 §1), rather than a second one taken on trust.
     *
     * Written at every declared presence including 1, and absent only where the
     * caller declared none: the property is this layer's, so once it exists it
     * has to be rewritten every frame or a driver's last value stays on the
     * element.
     *
     * The saturation is deliberately NOT scaled with it. This mix already takes
     * the saturated body toward the raw backdrop, and a saturation folded toward
     * 1 on top of it would count the same presence twice.
     */
    ...(presence === undefined ? {} : { opacity: String(Math.round(presence * 1000) / 1000) }),
    transition: transitionFor(policy, ["backdrop-filter"], driven),
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
  presence: number,
  driven: boolean,
): StyleDeclarations {
  if (body.form === "collapsed") return { ...layerFrame(borderWidth, -2), display: "none" };
  const blur = blurFunction(body.filter, body.heavyStepSigmaCssPx, prefix);
  const masked = body.share === "raster-mask";
  /*
   * The presence multiplies the share, on both carriers (W27d). This layer
   * blurs L1's OUTPUT rather than the page, so a heavy layer left at its full
   * weight over a half-present sharp one would keep blurring the raw backdrop at
   * that weight — a body that never left, however far the presence fell. Where
   * the mask carries the share the product is the mask's alpha times this
   * `opacity`, which is the same scaling by construction.
   */
  const share = (masked ? 1 : body.flatShare) * presence;
  return {
    ...layerFrame(borderWidth, -2),
    display: "block",
    "backdrop-filter": blur,
    "-webkit-backdrop-filter": blur,
    opacity: String(Math.round(share * 1000) / 1000),
    ...(masked
      ? {
          "mask-mode": "alpha",
          "mask-size": "100% 100%",
          "mask-repeat": "no-repeat",
          "-webkit-mask-size": "100% 100%",
          "-webkit-mask-repeat": "no-repeat",
        }
      : {}),
    transition: transitionFor(policy, ["backdrop-filter", "opacity"], driven),
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
 *
 * **And, since W18 G1, the OUTER shadow too, on carrier A** (charter Decision Log
 * 2 (1)). It rides here for the same reason the tint does — this layer is painted
 * after both filters, so nothing the tier draws on it is sampled by the body it
 * sits on. The two shadows share one property and need no arithmetic between
 * them: `layerFrame` insets this layer by the border width from the host's
 * padding box, so its border box IS the host's border box, and the outer shadow's
 * caster box and corner radius are therefore the host's own with no spread or
 * radius correction. The inset rim is written first so the list reads from the
 * inside out; an inset and an outset shadow occupy disjoint regions, so the order
 * is legibility rather than compositing.
 */
function overlayLayerDeclarations(
  optics: MaterialOptics,
  tint: string,
  border: string,
  policy: ResolvedAccessibilityPolicy,
  outerShadow: string,
  driven: boolean,
): StyleDeclarations {
  const rim =
    optics.borderWidth > 0 && optics.borderAlpha > 0
      ? `inset 0 0 0 ${px(optics.borderWidth)} ${border}`
      : undefined;
  const shadows = [rim, outerShadow === "none" ? undefined : outerShadow].filter(
    (value): value is string => value !== undefined,
  );
  return {
    ...layerFrame(optics.borderWidth, -1),
    // The tint is the contrast floor: it is here whether or not the blur lands,
    // and it stays on its own longhand so nothing layered above it can take it
    // down — see `pressGlowLayer`.
    "background-color": tint,
    // A profile is entitled to switch the illumination off, and a zero gain is
    // then a layer that paints nothing every frame rather than an absent one.
    "background-image": optics.glowGain > 0 ? pressGlowLayer(optics) : "none",
    "box-shadow": shadows.length === 0 ? "none" : shadows.join(", "),
    transition: transitionFor(policy, ["background-color", "box-shadow"], driven),
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
  transfer?: CssTierTintTransfer,
): string {
  if (kind === "blur") return `blur(${px(sigmaCssPx)})`;
  return `url(#${referenceFilterId(prefix, sigmaCssPx, transfer)})`;
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
  readonly presence: number;
}): CssTierBody {
  const { size, dpr, engine, spanPx } = input;
  /*
   * A surface at zero presence has no body at all, and the record says so
   * rather than describing a body drawn at zero weight (W27d).
   *
   * It is what the two consumers of this record need to read. `blur` is the
   * honest answer to "which blur do the layers carry" when they carry none, and
   * it is also what keeps `referenceFilterSpecs` from asking a root to build a
   * `<filter>` for a width nothing names; the zeroed widths are what the public
   * `--vitrea-blur` publishes, so an app matching this surface with its own
   * `blur()` matches the nothing that is drawn.
   */
  if (input.presence <= 0) {
    return {
      form: "collapsed",
      filter: "blur",
      share: "flat",
      sharpSigmaCssPx: 0,
      heavyStepSigmaCssPx: 0,
      heavySigmaCssPx: 0,
      flatShare: 0,
      projectedSigmaCssPx: 0,
    };
  }
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
 * The material at one presence — every optical term this tier paints, scaled
 * (W27d; §Presence: the widths and the weights).
 *
 * The blur width is the light bending, and it is the profile's `blurSigma` that
 * every one of the body's widths is derived from through functions linear in
 * it, so scaling it here scales L1's σ, L2's composed width, the step between
 * them and the projection `--vitrea-blur` publishes, all by the same factor and
 * with no second law. The tint's alpha, the rim's alpha and the press glow's
 * gain are the strengths L3 paints with; the outer shadow's is scaled where it
 * is resolved, because it is not carried on this record.
 *
 * Two things are deliberately left alone. The rim's WIDTH is layout and would
 * move the author's content box. The saturation is one operation on the
 * composite that the layers' own weight already mixes toward the raw backdrop,
 * and folding it toward 1 as well would count the same presence twice.
 *
 * Identity at 1 is exact rather than nearly so: every term is a multiplication,
 * and a multiplication by 1 returns the same double. The record at rest is
 * therefore the one this tier wrote before the channel existed, bit for bit.
 */
function opticsAtPresence(optics: MaterialOptics, presence: number): MaterialOptics {
  if (presence >= 1) return optics;
  return {
    ...optics,
    blurRadius: optics.blurRadius * presence,
    tintAlpha: optics.tintAlpha * presence,
    borderAlpha: optics.borderAlpha * presence,
    glowGain: optics.glowGain * presence,
  };
}

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
 * W16's three layers split what used to be one list on the host: the two filters
 * go to L1 and L2, and the tint, the rim and — since W18 G1 — the outer shadow go
 * to L3. The host keeps a `box-shadow` transition of its own because it still
 * writes that property on every carrier, at its value under the fallback and at
 * `none` otherwise. The duration and the easing are still one decision — the
 * material morphs as one thing, whichever element happens to carry a term of it.
 *
 * And it is one decision in the other direction too (W27d): while a driver is
 * writing this material every frame, no element declares a transition at all.
 * Suppressing only the properties a presence moves would leave the rest chasing
 * the same driver's frames through the interaction channels, and a transition
 * over a value that is already interpolated is a second ease laid over the
 * first — the material lands late and on neither curve.
 */
function transitionFor(
  policy: ResolvedAccessibilityPolicy,
  properties: readonly string[],
  driven = false,
): string {
  if (driven) return "none";
  const elastic = policy.motion.overshoot === "elastic";
  const duration = elastic ? NOMINAL_DURATION_MS : REDUCED_DURATION_MS;
  const easing = elastic ? ELASTIC_EASING : MONOTONIC_EASING;

  return properties.map((property) => `${property} ${duration}ms ${easing}`).join(", ");
}
