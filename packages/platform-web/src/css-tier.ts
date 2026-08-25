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
 * Every number is an advisory default, calibration-delegated (C7). What is not
 * advisory is the *shape* of the mapping from core's resolved policy regimes to
 * declarations — that is §Accessibility, applied.
 */

import type {
  BackdropTone,
  CornerRadii,
  ForegroundMode,
  ResolvedAccessibilityPolicy,
} from "vitrea";

import { opticsUnderPolicy, type MaterialOptics } from "./optics";

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

/** Light-scheme glass tints toward white; the dark scheme is a token swap, not a branch. */
const TINT_RGB = "255, 255, 255";
const BORDER_RGB = "255, 255, 255";

const px = (value: number): string => `${Math.round(value * 100) / 100}px`;

const rgba = (rgb: string, alpha: number): string =>
  `rgba(${rgb}, ${Math.round(alpha * 1000) / 1000})`;

/**
 * The declarations for one surface on the CSS tier.
 *
 * Pure: the same surface always yields the same record, which is what makes the
 * accessibility mapping testable without a browser.
 */
export function cssTierDeclarations(surface: CssTierSurface): StyleDeclarations {
  const { policy } = surface;
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
      color: "CanvasText",
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
      "--vitrea-foreground": "CanvasText",
    };
  }

  const filter = `blur(${px(optics.blurRadius)}) saturate(${optics.saturation})`;
  const tint = rgba(TINT_RGB, optics.tintAlpha);
  const border = rgba(BORDER_RGB, optics.borderAlpha);

  // X6's one honesty-core mechanism, reaching the tier most visitors get
  // (Decision Log #28(b), corrective K4): an `author-hint` mode with a
  // declared light or dark tone gets that tier's explicit foreground token
  // instead of the `color-scheme`-driven `light-dark()` default — a dark
  // backdrop gets the light token and vice versa. A "mixed" tone, a "fixed" or
  // "sampled-async" mode, or no hint at all keep `light-dark()`: there is no
  // single explicit answer to prefer instead. Accessibility policy outranks
  // the hint — near-monochrome (increased contrast; forced-colors takes the
  // early return above) is never overridden by it.
  const hintedTone = surface.foreground?.mode === "author-hint" ? surface.foreground.tone : undefined;
  const adaptiveForeground =
    hintedTone === "dark" ? "#f5f5f7" : hintedTone === "light" ? "#1c1c1e" : "light-dark(#1c1c1e, #f5f5f7)";
  const foreground =
    policy.material.foreground === "near-monochrome" ? "light-dark(#000, #fff)" : adaptiveForeground;

  return {
    "border-radius": radius,
    // The tint is the contrast floor: it is here whether or not the blur lands.
    background: tint,
    color: foreground,
    "border-style": "solid",
    "border-width": px(optics.borderWidth),
    "border-color": border,
    "backdrop-filter": filter,
    "-webkit-backdrop-filter": filter,
    // A soft ambient shadow is what makes the fallback read as a floating
    // surface rather than a flat translucent box.
    "box-shadow": `0 ${px(optics.borderWidth * 6)} ${px(optics.blurRadius * 3)} rgba(0, 0, 0, 0.18)`,
    transition: transitionFor(policy),
    "--vitrea-tint": tint,
    "--vitrea-occlusion": String(Math.round(optics.tintAlpha * 1000) / 1000),
    "--vitrea-border-color": border,
    "--vitrea-blur": px(optics.blurRadius),
    "--vitrea-foreground": foreground,
  };
}

function transitionFor(policy: ResolvedAccessibilityPolicy): string {
  const elastic = policy.motion.overshoot === "elastic";
  const duration = elastic ? NOMINAL_DURATION_MS : REDUCED_DURATION_MS;
  const easing = elastic ? ELASTIC_EASING : MONOTONIC_EASING;
  const properties = ["background-color", "border-color", "box-shadow", "backdrop-filter"];

  return properties.map((property) => `${property} ${duration}ms ${easing}`).join(", ");
}
