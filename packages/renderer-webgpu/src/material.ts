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
   * The size-parameterised lens depth — parent acceptance #2's mechanism.
   *
   * Below `lensSpanMin` a surface gets its authored thickness and nothing more;
   * above `lensSpanMax` it gets `lensSizeGainMax` times it. The final clamp to the
   * shorter *half* extent is what keeps a small control from being all lens: a
   * 24 px-tall button cannot bend more than 12 px of backdrop however thick it is
   * authored.
   *
   * A smoothstep rather than a straight ratio, so two surfaces of nearly the same
   * size never read as differently thick, and so the gain saturates instead of
   * growing without bound on a full-width platter.
   */
  readonly lensSpanMin: number;
  readonly lensSpanMax: number;
  readonly lensSizeGainMax: number;

  /** Chain LOD per CSS px of lens depth, and how much sharper the rim samples. */
  readonly lensBodyLodPerPx: number;
  readonly lensRimLodBias: number;

  /**
   * What each accessibility regime does to the numbers above. The multipliers
   * match `platform-web`'s CSS tier so the two renderers degrade the same way
   * under the same preference.
   */
  readonly reducedTransparencyFrost: number;
  readonly increasedOcclusionAlpha: number;
  readonly strongBorderRim: MaterialRim;
  readonly reducedTintAdaptation: number;

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

export const DEFAULT_MATERIAL_PROFILE: MaterialProfile = {
  optics: {
    // σ = 8 for the regular variant, which keeps this package's blur and
    // `platform-web`'s CSS-tier blur on the same number — and makes core's 24 px
    // `samplingPadding` advisory exactly the 3σ S1 measured.
    regular: {
      blurSigma: 8,
      tint: srgbToLinear(SRGB_WHITE_TINT),
      // MEASURED (C9a), against apple-macos-26.5-1x-light-standard. The advisory
      // 0.28 made vitrea's regular material roughly half as opaque as the
      // reference: regressing interior level against backdrop level across the
      // calibration scenes puts Apple's transmission at 0.26 of the backdrop
      // where vitrea's was 0.70. 0.62 is the minimiser of the declared tuning
      // objective; see docs/doperpowers/specs/c9a-fidelity-claims.md, and note
      // that no single value can be right for every size — Apple's opacity falls
      // with surface span (0.88 at 32 px to 0.56 at 96 px) and this renderer has
      // no size term on the tint.
      tintAlpha: 0.62,
      rimWidth: 1.5,
      rimAlpha: 0.18,
      specularPower: 6,
      specularGain: 0.55,
      shadowDepth: 0.35,
      shadowAlpha: 0.55,
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

  refractionScale: {
    none: 0,
    approximate: 0.45,
    true: 1,
  },

  lensSpanMin: 28,
  lensSpanMax: 420,
  lensSizeGainMax: 2.6,

  lensBodyLodPerPx: 0.16,
  lensRimLodBias: 2.5,

  reducedTransparencyFrost: 1.75,
  increasedOcclusionAlpha: 0.62,
  strongBorderRim: { rimWidth: 2, rimAlpha: 0.95 },
  reducedTintAdaptation: 0.35,

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
export const LENS_SPAN_MIN = DEFAULT_MATERIAL_PROFILE.lensSpanMin;
export const LENS_SPAN_MAX = DEFAULT_MATERIAL_PROFILE.lensSpanMax;
export const LENS_SIZE_GAIN_MAX = DEFAULT_MATERIAL_PROFILE.lensSizeGainMax;
export const LENS_BODY_LOD_PER_PX = DEFAULT_MATERIAL_PROFILE.lensBodyLodPerPx;
export const LENS_RIM_LOD_BIAS = DEFAULT_MATERIAL_PROFILE.lensRimLodBias;

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
  readonly lensSpanMin?: number;
  readonly lensSpanMax?: number;
  readonly lensSizeGainMax?: number;
  readonly lensBodyLodPerPx?: number;
  readonly lensRimLodBias?: number;
  readonly reducedTransparencyFrost?: number;
  readonly increasedOcclusionAlpha?: number;
  readonly strongBorderRim?: Readonly<Partial<MaterialRim>>;
  readonly reducedTintAdaptation?: number;
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
    lensSpanMin: patch.lensSpanMin ?? base.lensSpanMin,
    lensSpanMax: patch.lensSpanMax ?? base.lensSpanMax,
    lensSizeGainMax: patch.lensSizeGainMax ?? base.lensSizeGainMax,
    lensBodyLodPerPx: patch.lensBodyLodPerPx ?? base.lensBodyLodPerPx,
    lensRimLodBias: patch.lensRimLodBias ?? base.lensRimLodBias,
    reducedTransparencyFrost: patch.reducedTransparencyFrost ?? base.reducedTransparencyFrost,
    increasedOcclusionAlpha: patch.increasedOcclusionAlpha ?? base.increasedOcclusionAlpha,
    strongBorderRim: { ...base.strongBorderRim, ...patch.strongBorderRim },
    reducedTintAdaptation: patch.reducedTintAdaptation ?? base.reducedTintAdaptation,
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

  if (policy.occlusion === "increased") {
    next = { ...next, tintAlpha: Math.max(next.tintAlpha, profile.increasedOcclusionAlpha) };
  } else if (policy.occlusion === "opaque") {
    next = { ...next, tintAlpha: 1 };
  }

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

const smoothstep = (edge0: number, edge1: number, x: number): number => {
  if (edge1 <= edge0) return x < edge0 ? 0 : 1;
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
};

/** The lens's size gain — see `MaterialProfile.lensSpanMin` for what it is for. */
export function lensSizeGain(
  spanPx: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): number {
  return (
    1 +
    (profile.lensSizeGainMax - 1) *
      smoothstep(profile.lensSpanMin, profile.lensSpanMax, spanPx)
  );
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
