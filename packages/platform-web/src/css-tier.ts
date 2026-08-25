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
  ResolvedAccessibilityPolicy,
} from "vitrea";

import {
  CSS_TIER_MAPPING,
  cssTierForegroundLevel,
  opticsUnderPolicy,
  type CssTierMapping,
  type MaterialOptics,
  type Rgb255,
} from "./optics";

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
  readonly policy: ResolvedAccessibilityPolicy;
  /**
   * The group's resolved foreground adaptation (§Foreground adaptation). Absent
   * is the pre-K4 default: no hint reaches this tier, so it keeps the
   * `light-dark()` fallback unchanged.
   */
  readonly foreground?: CssTierForegroundHint;
  /**
   * The mapping the optics were derived through. Only its foreground constants
   * are read here — the rest already did their work in `cssTierOptics` — but the
   * two have to be the same document, or the ink would be chosen against a
   * material the surface is not drawing. Defaults to the shipped mapping.
   */
  readonly mapping?: CssTierMapping;
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
 * The foreground pair — `color` and the token an app styles against — for one
 * surface, on **either** tier (Decision Log #32(b)).
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
export function foregroundDeclarations(input: {
  readonly policy: ResolvedAccessibilityPolicy;
  readonly level?: number;
  readonly mapping?: CssTierMapping;
}): StyleDeclarations {
  const mapping = input.mapping ?? CSS_TIER_MAPPING;
  const { material } = input.policy;

  // forced-colors takes the platform's palette, and it is not a dimmer version of
  // the adaptive answer — it is a different one.
  if (material.glass === "none") return { color: "CanvasText", "--vitrea-foreground": "CanvasText" };

  // Accessibility policy outranks the hint: near-monochrome is never overridden.
  const colour =
    material.foreground === "near-monochrome"
      ? "light-dark(#000, #fff)"
      : input.level === undefined
        ? FOREGROUND_DEFAULT
        : input.level >= mapping.foregroundCrossover
          ? FOREGROUND_INK.dark
          : FOREGROUND_INK.light;

  return { color: colour, "--vitrea-foreground": colour };
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
 * The declarations for one surface on the CSS tier.
 *
 * Pure: the same surface always yields the same record, which is what makes the
 * accessibility mapping testable without a browser.
 */
export function cssTierDeclarations(surface: CssTierSurface): StyleDeclarations {
  const { policy } = surface;
  const mapping = surface.mapping ?? CSS_TIER_MAPPING;
  const optics = opticsUnderPolicy(surface.optics, policy.material);
  const radius = surface.radii.map(px).join(" ");

  // forced-colors: "system colors, borders, no glass" (§Accessibility). Nothing
  // to frost, lens or tint, and the palette is the platform's — so this is not a
  // dimmer version of the material, it is a different surface, and the branch
  // says so instead of trying to parameterise its way there.
  if (policy.material.glass === "none") {
    return {
      "border-radius": radius,
      background: "Canvas",
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
  const hintedLuminance = hintedBackdropLuminance(surface.foreground, mapping);

  return {
    "border-radius": radius,
    // The tint is the contrast floor: it is here whether or not the blur lands.
    background: tint,
    "border-style": "solid",
    "border-width": px(optics.borderWidth),
    "border-color": border,
    "backdrop-filter": filter,
    "-webkit-backdrop-filter": filter,
    /*
     * No ambient shadow (Decision Log #32(c)). The reference material casts none,
     * and K5 measured this one owning the dom tier's entire shape axis — see
     * `CssTierMapping`'s shadow fields. The declaration stays rather than being
     * dropped, because a profile is entitled to restore one and the property then
     * has to be written every frame like the rest of the material.
     */
    "box-shadow":
      optics.shadowAlpha === 0
        ? "none"
        : `0 ${px(optics.shadowOffset)} ${px(optics.shadowBlur)} rgba(0, 0, 0, ${optics.shadowAlpha})`,
    transition: transitionFor(policy),
    "--vitrea-tint": tint,
    "--vitrea-occlusion": String(Math.round(optics.tintAlpha * 1000) / 1000),
    "--vitrea-border-color": border,
    "--vitrea-blur": px(optics.blurRadius),
    ...foregroundDeclarations({
      policy,
      mapping,
      ...(hintedLuminance === undefined
        ? {}
        : { level: cssTierForegroundLevel(optics, hintedLuminance) }),
    }),
  };
}

function transitionFor(policy: ResolvedAccessibilityPolicy): string {
  const elastic = policy.motion.overshoot === "elastic";
  const duration = elastic ? NOMINAL_DURATION_MS : REDUCED_DURATION_MS;
  const easing = elastic ? ELASTIC_EASING : MONOTONIC_EASING;
  const properties = ["background-color", "border-color", "box-shadow", "backdrop-filter"];

  return properties.map((property) => `${property} ${duration}ms ${easing}`).join(", ");
}
