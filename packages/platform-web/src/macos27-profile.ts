/**
 * The macOS 27 material, as a published package carries it.
 *
 * GENERATED — do not edit. `scripts/generate-macos27-profile.mjs` writes this
 * file from the four documents named below, whose `patch` blocks are the
 * authority for every number in it;
 * `packages/calibration/test/macos27-profile-export.test.ts` deep-equals each
 * pair in both directions, so a wave that re-records a document and forgets to
 * regenerate this module fails there.
 *
 * ## What these are
 *
 * Four **patches** over the renderer's `DEFAULT_MATERIAL_PROFILE`, which W29
 * Decision Log 1 (i) holds still at the macOS 26.5 light material so that the
 * frozen 26.5 documents keep their identity pin. "macOS 27 is the default" is
 * therefore a **selection** — `material-document.ts` assembles these four into
 * the document a root resolves when an app asks for nothing — and not a moved
 * constant.
 *
 * - the active material per colour scheme (`apple-macos-27.0-1x-light-standard-glass0.5`,
 *   `apple-macos-27.0-1x-dark-standard-glass0.5`), each serving both scales;
 * - the receded difference per colour scheme, applied OVER the active patch of
 *   the same scheme when the window loses focus (`apple-macos-27.0-1x-light-standard-glass0.5-receded`,
 *   `apple-macos-27.0-1x-dark-standard-glass0.5-receded`).
 *
 * The light document also records what this material costs to express on the
 * CSS tier, and that mapping is one per family rather than one per scheme.
 *
 * Reach for any of it through `createGlassRoot({ materialProfileDocument })`;
 * the constants are exported by name as well, for an app composing a material
 * of its own over one of them.
 */

import type { CssTierMapping } from "./optics";
import type { RendererMaterialProfile } from "./renderer-bridge";

/** The macOS 27 light-standard material, measured at `NSGlassTintAmount` 0.5. */
export const macos27LightMaterialProfile: RendererMaterialProfile = {
  optics: {
    regular: {
      blurSigma: 1.25,
      tintAlpha: 0.46,
      shadowAlpha: 0.05,
      specularGain: 0,
      rimAlpha: 0.115,
      rimLevelGain: -0.122,
      rimWidth2x: 5.85,
      rimLitExponent: 0.85,
      rimAlongSideSlope: 0.1,
      rimWidth: 6.5,
    },
  },
  adaptiveTintDark: [1, 1, 1],
  adaptiveTintLight: [1, 1, 1],
  sizeShadowGainMax: 1,
  backdropToneSizeBias: 0.05,
  rimCollapsed: 0.038,
  rimCollapsedTinted: 0.52,
  rimTintChroma: 1,
  tintShadeDark: 0.5289,
  tintShadeLight: 1.0175,
  tintShadeStrength: 1,
  outerShadow: {
    thinOcclusionDark: 0,
    thinOcclusionMid: 0.068,
    thinOcclusionBright: 0.0683,
    thickOcclusionAt96: 0.1158,
    thickOcclusionAt128: 0.1827,
    thickOcclusionAt160: 0.26,
    liftAmplitude: 0.001,
    liftSpanMin: 64,
    liftSpanFull: 118,
    liftBlurSigmaCss: 40,
    reducedTransparencyOcclusion: 0.087,
    offsetPx: 7.95,
    sigmaPx: 8.96,
    spreadPx: 3.1,
    sizeGain: 0,
    sigmaSlopePerSpan: 0.1314,
    sigmaSpanRefPx: 96,
    sigmaThinOffsetPx: -6.8328,
  },
  backdropToneLow: 0,
  increasedOcclusionLift: 0.75,
  sizeSpanMin: 32,
  sizeSpanMax: 96,
  lensSizeGainMax: 2.6,
  lensRefractionGain: 0.745,
  lensHeightPerSpan: 0.25,
  lensHeightMax: 20,
  lensAmountPerSpan: 0.8,
  lensAmountMax: 60,
  lensThicknessReference: 8,
  lensExtentGain: 1.337,
  lensProfileExponent: 3.69,
  lensOvalization: 0.8,
  lensOvalizationSpanMin: 64,
  lensOvalizationSpanMax: 72,
  sizeScatterGainMax: 8,
  sizeScatterFloor: 0.25,
  sizeScatterSpanMax: 256,
  sizeScatterGainMax2x: 4.8,
  sizeScatterFloor2x: 1,
  sizeScatterSpanMax2x: 256,
  sizeScatterGainFar2x: 9.9,
  sizeHeavyTapSigma: 14,
  sizeHeavyTapSigma2x: 20,
  sizeScatterRampStartThin1x: 0.72,
  sizeScatterRampStartThick1x: 0.52,
  sizeScatterRampStartThin2x: 0.46,
  sizeScatterRampStartThick2x: 0.21,
  sizeScatterRampStartFar1x: 0.2,
  sizeScatterRampStartFar2x: 0.21,
  sizeScatterRampReach1xPx: 80,
  sizeScatterRampReach2xPx: 100,
  sizeOcclusionGain: 0.05,
  backdropToneMax: 1,
  backdropToneHigh: 0.0001,
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
  backdropToneResponseThin: [0.214, 0.2835, 0.5383, 0.937],
  backdropToneResponseThick: [0.242, 0.3074, 0.5554, 0.957],
  backdropToneResponseStrength: 1,
  rimLitAxis: [-0.7071, -0.7071],
  collapseTransmission: 0.017,
  collapseTransmission2x: 0.07,
  sizeHeavySecondSigma: 0,
  sizeHeavySecondSigma2x: 0,
  sizeHeavySecondShare: 0,
  sizeScatterScaleGain: 0,
  sizeScatterScaleRef: 0.03,
};

/** The macOS 27 dark-standard material, in the same relation to the default. */
export const macos27DarkMaterialProfile: RendererMaterialProfile = {
  backdropToneAnchorX: [0.004, 0.11, 0.47, 0.95],
  backdropToneResponseThin: [0.036, 0.042, 0.199, 0.464],
  backdropToneResponseThick: [0.031, 0.035, 0.169, 0.196],
  backdropToneResponseStrength: 1,
  tintShadeStrength: 0,
  optics: {
    regular: {
      tint: [0.05, 0.05, 0.05],
      tintAlpha: 0.9,
      rimAlpha: 0.055,
      specularGain: 0,
      rimLevelGain: 0.44,
      rimWidth: 2.2,
    },
  },
  adaptiveTintDark: [0.05, 0.05, 0.05],
  adaptiveTintLight: [0.05, 0.05, 0.05],
  outerShadow: {
    thinOcclusionDark: 0,
    thinOcclusionMid: 0.0455,
    thinOcclusionBright: 0.0537,
    thickOcclusionAt96: 0.133,
    thickOcclusionAt128: 0.2263,
    thickOcclusionAt160: 0.3409,
    liftAmplitude: 0.0005,
    liftSpanMin: 64,
    liftSpanFull: 118,
    liftBlurSigmaCss: 40,
    reducedTransparencyOcclusion: 0.038,
    sigmaPx: 9.04,
    sigmaSlopePerSpan: 0.134,
    sigmaSpanRefPx: 96,
    sigmaThinOffsetPx: -6.968,
  },
  sizeHeavyTapSigma: 0,
  sizeHeavyTapSigma2x: 0,
  backdropToneLow: 0,
  backdropToneHigh: 0.0001,
  sizeScatterFloor: 0.34,
  sizeHeavySecondSigma: 0,
  sizeHeavySecondSigma2x: 0,
  sizeHeavySecondShare: 0,
  sizeScatterScaleGain: -2,
  sizeScatterScaleRef: 0.03,
};

/**
 * The macOS 27 receded endpoints: a difference over the ACTIVE patch of the same
 * scheme, not a second material. The largest single change from macOS 26.5 is
 * that a receded surface keeps its outer shadow, where the 26.5 endpoint removes
 * it (claims §5.154 §6).
 */
export const macos27RecededMaterialProfile: Readonly<
  Record<"light" | "dark", RendererMaterialProfile>
> = {
  light: {
    backdropToneAbscissa: {
      kind: "silhouette",
    },
    tintChromaScale: 0,
    tintShadeCollapseRetention: 1,
    tintShadeStrength: 1,
    optics: {
      regular: {
        rimAlpha: 0,
        rimLevelGain: 0,
        shadowAlpha: 0,
      },
      clear: {
        rimAlpha: 0,
        rimLevelGain: 0,
        shadowAlpha: 0,
      },
    },
    rimCollapsed: 0,
    rimCollapsedTinted: 0,
    outerShadow: {
      thinOcclusionDark: 0,
      thinOcclusionMid: 0.068,
      thinOcclusionBright: 0.0683,
      thickOcclusionAt96: 0.1158,
      thickOcclusionAt128: 0.1827,
      thickOcclusionAt160: 0.26,
      liftAmplitude: 0.001,
      reducedTransparencyOcclusion: 0.087,
    },
    sizeScatterRampStartThick1x: 0.3,
    sizeScatterRampStartThick2x: 0.04,
    sizeScatterRampStartFar2x: 0.04,
    sizeHeavyTapSigma2x: 14,
    tintShadeDark: 0.0288,
    tintShadeLight: 0.76,
    reducedTintAdaptation: 0.88,
    sizeScatterFloor: 0.7,
    sizeScatterRampStartThin1x: 0.55,
    sizeScatterRampStartThin2x: 0.7,
    backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
    backdropToneResponseThin: [0.1647, 0.2809, 0.4775, 0.8293],
    backdropToneResponseThick: [0.1442, 0.2823, 0.4695, 0.832],
    refractionScale: {
      approximate: 0,
    },
    increasedOcclusionLift: 0.96,
    increasedOcclusionLiftByPolicy: {
      reduceTransparency: 0.88,
      increaseContrast: 0.98,
    },
    strongBorderRim: {
      rimWidth: 1,
      rimAlpha: -3.5,
    },
  },
  dark: {
    backdropToneAbscissa: {
      kind: "silhouette",
    },
    tintChromaScale: 0,
    tintShadeCollapseRetention: 1,
    tintShadeStrength: 1,
    optics: {
      regular: {
        rimAlpha: 0,
        rimLevelGain: 0,
        shadowAlpha: 0,
        tintAlpha: 0.89,
      },
      clear: {
        rimAlpha: 0,
        rimLevelGain: 0,
        shadowAlpha: 0,
      },
    },
    rimCollapsed: 0,
    rimCollapsedTinted: 0,
    outerShadow: {
      thinOcclusionDark: 0,
      thinOcclusionMid: 0.0455,
      thinOcclusionBright: 0.0537,
      thickOcclusionAt96: 0.133,
      thickOcclusionAt128: 0.2263,
      thickOcclusionAt160: 0.3409,
      liftAmplitude: 0.0005,
      reducedTransparencyOcclusion: 0.038,
    },
    sizeScatterRampStartThick1x: 0.3,
    sizeScatterRampStartThick2x: 0.04,
    sizeScatterRampStartFar2x: 0.04,
    sizeHeavyTapSigma2x: 14,
    tintShadeDark: 0.0202,
    tintShadeLight: 1.46,
    sizeScatterRampStartThin1x: 1,
    sizeScatterRampStartThin2x: 1,
    sizeScatterHeavyShareThick1x: 0.25,
    backdropToneAnchorX: [0.004, 0.11, 0.47, 0.95],
    backdropToneResponseThin: [0, 0.0187, 0.192, 0.448],
    backdropToneResponseThick: [0, 0.0155, 0.164, 0.186],
  },
};

/**
 * What the macOS 27 material costs to express as one `backdrop-filter` plus an
 * `rgba()` overlay. `blurSigmaScale` is the constant that carries the CSS
 * tier's whole share of the 27 diffusion refit (claims §5.153 §2).
 */
export const macos27CssTierMapping: Partial<CssTierMapping> = {
  referenceBackdropLuminance: 0.02,
  borderAlphaPerRimAlpha: {
    regular: 0.64,
    clear: 1.95,
  },
  blurSigmaScale: 2.2,
};

/**
 * Each endpoint's resolved-material digest — over the material it resolves to,
 * not over the patch. Reported by the root's material readout so a capture, a
 * test or the demo's capabilities panel can say which document drew.
 *
 * **These are the documents' own `resolvedMaterialSha256` fields**, read from
 * the four macOS 27 documents on disk, each sealed under digest rule 2 (W31
 * Decision Log 1 (a); claims §5.164). Between W30 G2 and W31 G3 they came from
 * `packages/calibration/profiles/digest-supersessions.json` instead, because a
 * leaf added at an algebraic identity moved every document's fingerprint while
 * moving no pixel and a frozen document's bytes could not be re-recorded. Under
 * the rule that no longer happens, so every document's own field is what the pin
 * resolves to and this module names what draws.
 * `packages/calibration/test/macos27-profile-export.test.ts` pins these against
 * the documents and `tuned-profiles.test.ts` recomputes each from the material
 * itself, so the chain ends at a material and not at a field.
 *
 * The two receded digests are taken over the COMPOSITION the page performs —
 * the receded difference over the ACTIVE patch of the same scheme over the
 * renderer's default — because that is the material a root hands the renderer
 * when the window loses focus, and it is what `window-activation.spec.ts` reads
 * back from the browser.
 */
export const MACOS_27_RESOLVED_MATERIAL_SHA256 = {
  light: "62e684744954580b",
  dark: "c61194f820d77280",
  recededLight: "183c8949f194ff43",
  recededDark: "1a64247df6786fc2",
} as const;
