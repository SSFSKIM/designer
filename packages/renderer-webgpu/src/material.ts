/**
 * The optical constants, and the two foldings that decide what the shader
 * actually gets: the dual cap, and the size-parameterised lens.
 *
 * **Every number here is advisory and calibration-delegated (C7).** They are
 * chosen so the material is coherent out of the box — a plausible glass, not a
 * measured one — and §Calibration names exactly this kind of value as a delegated
 * unknown. They live as named constants so replacing them with fitted values is a
 * data change, and no shader carries a literal of its own.
 *
 * ## The dual cap (Decision Log #19)
 *
 * Two independent things cap refraction: the accessibility policy's regime
 * (`nominal | reduced | none`) and the group's resolved capability state
 * (`true | approximate | none` — what the sampling backend can actually deliver).
 * **The lower of the two wins**, and this module folds them into one scalar before
 * anything reaches a uniform, so the shader has no way to honour the wrong one.
 *
 * The ordering mirrors `platform-web`'s `REFRACTION_LADDER`, which serves the CSS
 * tier. It is restated rather than imported because this package sits *below*
 * core in the dependency graph and platform-web sits above it. That the two
 * copies must agree is a real (if small) seam — see the note in the C6 report.
 */

import type { Rgb } from "./color";
import { srgbToLinear } from "./color";

/** X2's `RefractionQuality`, restated. Weakest first — the declaration order IS the ladder. */
export const REFRACTION_LADDER = ["none", "approximate", "true"] as const;

export type RefractionQuality = (typeof REFRACTION_LADDER)[number];

export function refractionRank(quality: RefractionQuality): number {
  return REFRACTION_LADDER.indexOf(quality);
}

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

/** The accessibility regime as a rung on the same ladder. */
export function accessibilityRefractionCap(policy: MaterialPolicyView): RefractionQuality {
  switch (policy.refraction) {
    case "nominal":
      return "true";
    case "reduced":
      return "approximate";
    case "none":
      return "none";
  }
}

/** The lower of two caps. Symmetric — neither argument is privileged. */
export function effectiveRefraction(a: RefractionQuality, b: RefractionQuality): RefractionQuality {
  return refractionRank(a) <= refractionRank(b) ? a : b;
}

/**
 * How much of the lens the shader is allowed to apply.
 *
 * `approximate` is not "half of true": it is the rim-lensing approximation, a
 * shallower bend confined nearer the edge, which is what a group sampling a CSS
 * proxy can honestly claim. Reduced transparency lands here too, which is the
 * point of the ladder having three rungs and not two.
 */
export const REFRACTION_SCALE: Readonly<Record<RefractionQuality, number>> = {
  none: 0,
  approximate: 0.45,
  true: 1,
};

export type MaterialVariant = "regular" | "clear";

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

const SRGB_WHITE_TINT: Rgb = [1, 1, 1];
const SRGB_DARK_TINT: Rgb = [0.09, 0.09, 0.1];

/**
 * σ = 8 for the regular variant, which keeps this package's blur and
 * `platform-web`'s CSS-tier blur on the same number — and makes core's 24 px
 * `samplingPadding` advisory exactly the 3σ S1 measured. Clear is persistently
 * more transparent, so it frosts less and tints less.
 */
export const MATERIAL_OPTICS: Readonly<Record<MaterialVariant, MaterialOptics>> = {
  regular: {
    blurSigma: 8,
    tint: srgbToLinear(SRGB_WHITE_TINT),
    tintAlpha: 0.28,
    rimWidth: 1.5,
    rimAlpha: 0.18,
    specularPower: 6,
    specularGain: 0.55,
    shadowDepth: 0.35,
    shadowAlpha: 0.55,
    highlight: srgbToLinear(SRGB_WHITE_TINT),
  },
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
};

/** The two ends of adaptation: what the tint becomes over a dark and a light backdrop. */
export const ADAPTIVE_TINT_DARK: Rgb = srgbToLinear(SRGB_WHITE_TINT);
export const ADAPTIVE_TINT_LIGHT: Rgb = srgbToLinear(SRGB_DARK_TINT);

/** Luminance band the tint crosses over. Hysteresis in time is the driver's job. */
export const ADAPTIVE_LUMINANCE_LOW = 0.12;
export const ADAPTIVE_LUMINANCE_HIGH = 0.42;

const REDUCED_TRANSPARENCY_FROST = 1.75;
const INCREASED_OCCLUSION_ALPHA = 0.62;
const STRONG_BORDER_RIM = { rimWidth: 2, rimAlpha: 0.95 } as const;
const REDUCED_TINT_ADAPTATION = 0.35;

/**
 * Fold core's resolved material *regime* onto this package's numbers.
 *
 * core decides which regime applies and nothing here re-decides it. One branch
 * per axis of `MaterialPolicyView`, so a new axis in core surfaces as a missing
 * branch here rather than as silence. The multipliers match `platform-web`'s CSS
 * tier so the two renderers degrade the same way under the same preference.
 */
export function opticsUnderPolicy(
  optics: MaterialOptics,
  policy: MaterialPolicyView,
): MaterialOptics {
  let next = optics;

  if (policy.frost === "increased") {
    next = { ...next, blurSigma: next.blurSigma * REDUCED_TRANSPARENCY_FROST };
  } else if (policy.frost === "none") {
    next = { ...next, blurSigma: 0 };
  }

  if (policy.occlusion === "increased") {
    next = { ...next, tintAlpha: Math.max(next.tintAlpha, INCREASED_OCCLUSION_ALPHA) };
  } else if (policy.occlusion === "opaque") {
    next = { ...next, tintAlpha: 1 };
  }

  if (policy.border === "strong") next = { ...next, ...STRONG_BORDER_RIM };

  return next;
}

/** How much of the analysis-driven tint is applied, under the contrast regime. */
export function adaptationStrength(policy: MaterialPolicyView, analysisExact: boolean): number {
  if (!analysisExact) return 0;
  switch (policy.ambientTint) {
    case "nominal":
      return 1;
    case "reduced":
      return REDUCED_TINT_ADAPTATION;
    case "none":
      return 0;
  }
}

/**
 * The size-parameterised lens depth — parent acceptance #2's mechanism.
 *
 * `span` is the surface's shorter extent in CSS px. Below `LENS_SPAN_MIN` a
 * surface gets its authored thickness and nothing more; above `LENS_SPAN_MAX` it
 * gets `LENS_SIZE_GAIN_MAX` times it. The final clamp to the shorter *half*
 * extent is what keeps a small control from being all lens: a 24 px-tall button
 * cannot bend more than 12 px of backdrop however thick it is authored.
 *
 * A smoothstep rather than a straight ratio, so two surfaces of nearly the same
 * size never read as differently thick, and so the gain saturates instead of
 * growing without bound on a full-width platter.
 */
export const LENS_SPAN_MIN = 28;
export const LENS_SPAN_MAX = 420;
export const LENS_SIZE_GAIN_MAX = 2.6;

/** Chain LOD per CSS px of lens depth, and how much sharper the rim samples. */
export const LENS_BODY_LOD_PER_PX = 0.16;
export const LENS_RIM_LOD_BIAS = 2.5;

const smoothstep = (edge0: number, edge1: number, x: number): number => {
  if (edge1 <= edge0) return x < edge0 ? 0 : 1;
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
};

export function lensSizeGain(spanPx: number): number {
  return 1 + (LENS_SIZE_GAIN_MAX - 1) * smoothstep(LENS_SPAN_MIN, LENS_SPAN_MAX, spanPx);
}

export function lensDepthPx(thicknessPx: number, spanPx: number): number {
  const gain = lensSizeGain(spanPx);
  return Math.min(Math.max(thicknessPx, 0) * gain, spanPx * 0.5);
}

/** Body blur LOD on the chain for a given lens depth — thicker glass diffuses more. */
export function bodyLod(lensDepth: number, maxLod: number): number {
  return Math.min(Math.max(lensDepth * LENS_BODY_LOD_PER_PX, 0), maxLod);
}
