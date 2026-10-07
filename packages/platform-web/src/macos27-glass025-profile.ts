/**
 * The macOS 27 material at the Glass appearance slider's 0.25 position (the clearer glass), as a
 * published package carries it.
 *
 * GENERATED — do not edit. `scripts/generate-macos27-glass025-profile.mjs` writes this file from
 * the four documents named below, whose `patch` blocks are the authority for every number in it;
 * `packages/calibration/test/macos27-profile-export.test.ts` deep-equals each pair in both
 * directions, so a wave that re-records a document and forgets to regenerate this module fails
 * there.
 *
 * Four **patches** over the renderer's `DEFAULT_MATERIAL_PROFILE`, exactly as the 0.5 material's
 * are, measured at `NSGlassTintAmount` 0.25 (W43, claims §5.199 to §5.201): the active material
 * per colour scheme (`apple-macos-27.0-1x-light-standard-glass0.25`, `apple-macos-27.0-1x-dark-standard-glass0.25`), each serving both scales, and
 * the receded difference per colour scheme, applied OVER the active patch of the same scheme
 * (`apple-macos-27.0-1x-light-standard-glass0.25-receded`, `apple-macos-27.0-1x-dark-standard-glass0.25-receded`). They name exactly the 0.5
 * material's leaves, so the two are points in one space.
 *
 * Not the default: a page chooses it through `createGlassRoot({ materialProfileDocument })`.
 */

import type { CssTierMapping } from "./optics";
import type { RendererMaterialProfile } from "./renderer-bridge";

/** The macOS 27 light-standard material, measured at `NSGlassTintAmount` 0.25. */
export const macos27Glass025LightMaterialProfile: RendererMaterialProfile = {
  optics: {
    regular: {
      blurSigma: 1.25,
      tintAlpha: 0.3,
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
    thinOcclusionMid: 0.0244,
    thinOcclusionBright: 0.0227,
    thickOcclusionAt96: 0.087,
    thickOcclusionAt128: 0.165,
    thickOcclusionAt160: 0.2518,
    liftAmplitude: 0,
    liftSpanMin: 64,
    liftSpanFull: 118,
    liftBlurSigmaCss: 40,
    reducedTransparencyOcclusion: 0.087,
    offsetPx: 7.95,
    sigmaPx: 8.96,
    spreadPx: 0.5,
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
  sizeScatterSpanMax2x: 128,
  sizeScatterGainFar2x: 9.9,
  sizeHeavyTapSigma: 14,
  sizeHeavyTapSigma2x: 20,
  sizeScatterRampStartThin1x: 0.72,
  sizeScatterRampStartThick1x: 0.52,
  sizeScatterRampStartThin2x: 0.65,
  sizeScatterRampStartThick2x: 0.21,
  sizeScatterRampStartFar1x: 0.2,
  sizeScatterRampStartFar2x: 0.21,
  sizeScatterRampReach1xPx: 80,
  sizeScatterRampReach2xPx: 100,
  sizeOcclusionGain: 0.05,
  backdropToneMax: 1,
  backdropToneHigh: 0.0001,
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
  backdropToneResponseThin: [0.1613, 0.2201, 0.5336, 0.9366],
  backdropToneResponseThick: [0.1871, 0.2338, 0.5159, 0.9401],
  backdropToneResponseStrength: 1,
  rimLitAxis: [-0.7071, -0.7071],
  collapseTransmission: 0.017,
  collapseTransmission2x: 0.07,
  sizeHeavySecondSigma: 0,
  sizeHeavySecondSigma2x: 2,
  sizeHeavySecondShare: 0.5,
  sizeScatterScaleGain: 0,
  sizeScatterScaleRef: 0.03,
  bodyChromaRetention: 0.282,
  backdropToneBlackStrength: 1,
  backdropToneBlackThin: 0.17804,
  backdropToneBlackThick: 0.17804,
  sizeHeavySecondShareFar2x: -0.25,
};

/** The macOS 27 dark-standard material at 0.25, in the same relation to the default. */
export const macos27Glass025DarkMaterialProfile: RendererMaterialProfile = {
  backdropToneAnchorX: [0.004, 0.11, 0.47, 0.95],
  backdropToneResponseThin: [0.036, 0.042, 0.199, 0.464],
  backdropToneResponseThick: [0.031, 0.0414, 0.173, 0.196],
  backdropToneResponseStrength: 1,
  tintShadeStrength: 0,
  optics: {
    regular: {
      tint: [0.05, 0.05, 0.05],
      tintAlpha: 0.7,
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
    thinOcclusionMid: 0.0196,
    thinOcclusionBright: 0.0231,
    thickOcclusionAt96: 0.1038,
    thickOcclusionAt128: 0.2188,
    thickOcclusionAt160: 0.3443,
    liftAmplitude: 0,
    liftSpanMin: 64,
    liftSpanFull: 118,
    liftBlurSigmaCss: 40,
    reducedTransparencyOcclusion: 0.038,
    sigmaPx: 9.04,
    sigmaSlopePerSpan: 0.1215,
    sigmaSpanRefPx: 96,
    sigmaThinOffsetPx: -6.318,
    spreadPx: 1.8,
    offsetPx: 7.95,
  },
  sizeHeavyTapSigma: 0,
  sizeHeavyTapSigma2x: 0,
  backdropToneLow: 0,
  backdropToneHigh: 0.0001,
  sizeScatterFloor: 0.34,
  sizeHeavySecondSigma: 0,
  sizeHeavySecondSigma2x: 0,
  sizeHeavySecondShare: 0,
  sizeScatterScaleGain: -0.5,
  sizeScatterScaleRef: 0.03,
  bodyChromaRetention: 0.336,
  backdropToneBlackStrength: 1,
  backdropToneBlackThin: 0.014443843596092545,
  backdropToneBlackThick: 0.014443843596092545,
  tintAlphaFar1x: 0.2,
  tintAlphaFar2x: 0.2,
  sizeScatterSpanMax: 160,
  sizeScatterSpanMax2x: 160,
  sizeOcclusionGain: 0.05,
  sizeScatterFloor2x: 1,
  sizeScatterRampStartThin1x: 0.72,
  sizeScatterRampStartThin2x: 0.46,
};

/**
 * The macOS 27 receded endpoints at 0.25: a difference over the ACTIVE 0.25 patch of the same
 * scheme, not a second material. They cast no exterior shadow, as at 0.5 (W32 Decision Log 2).
 */
export const macos27Glass025RecededMaterialProfile: Readonly<
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
      thinOcclusionMid: 0,
      thinOcclusionBright: 0,
      thickOcclusionAt96: 0,
      thickOcclusionAt128: 0,
      thickOcclusionAt160: 0,
      liftAmplitude: 0,
      reducedTransparencyOcclusion: 0,
    },
    sizeScatterRampStartThick1x: 0.3,
    sizeScatterRampStartThick2x: 0,
    sizeScatterRampStartFar2x: 0,
    sizeHeavyTapSigma2x: 18,
    tintShadeDark: 0.0288,
    tintShadeLight: 0.76,
    reducedTintAdaptation: 0.88,
    sizeScatterFloor: 1,
    sizeScatterRampStartThin1x: 0.55,
    sizeScatterRampStartThin2x: 0.1,
    backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
    backdropToneResponseThin: [0.1105, 0.2045, 0.4217, 0.8117],
    backdropToneResponseThick: [0.0894, 0.231, 0.4288, 0.8086],
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
    bodyChromaRetention: 0.349,
    backdropToneBlackStrength: 1,
    backdropToneBlackThin: 0.180351,
    backdropToneBlackThick: 0.180351,
    sizeHeavySecondShare: 0.25,
    sizeHeavySecondShareFar2x: -0.125,
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
        tintAlpha: 0.8,
        blurSigma: 1.25,
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
      thinOcclusionMid: 0,
      thinOcclusionBright: 0,
      thickOcclusionAt96: 0,
      thickOcclusionAt128: 0,
      thickOcclusionAt160: 0,
      liftAmplitude: 0,
      reducedTransparencyOcclusion: 0,
    },
    sizeScatterRampStartThick1x: 0.15,
    sizeScatterRampStartThick2x: 0.04,
    sizeScatterRampStartFar2x: 0.04,
    sizeHeavyTapSigma2x: 14,
    tintShadeDark: 0.0202,
    tintShadeLight: 1.46,
    sizeScatterRampStartThin1x: 0.4,
    sizeScatterRampStartThin2x: 0.4,
    sizeScatterHeavyShareThick1x: 0.25,
    backdropToneAnchorX: [0.004, 0.11, 0.47, 0.95],
    backdropToneResponseThin: [0, 0.0187, 0.192, 0.448],
    backdropToneResponseThick: [0, 0.0155, 0.167, 0.186],
    bodyChromaRetention: 0.142,
    backdropToneBlackStrength: 1,
    backdropToneBlackThin: 0.006995410187265387,
    backdropToneBlackThick: 0.006995410187265387,
    sizeScatterRampStartFar1x: 0.2,
    sizeScatterFloor: 0.5,
    sizeScatterFloor2x: 1,
    sizeHeavyTapSigma: 0,
    sizeHeavySecondShare: 0.25,
    sizeHeavySecondShareFar2x: 0,
    sizeHeavySecondSigma: 5,
    sizeHeavySecondSigma2x: 5,
    sizeScatterScaleGain: 0,
    sizeScatterSpanMax: 160,
    sizeScatterSpanMax2x: 160,
    sizeOcclusionGain: 0.05,
    tintAlphaFar1x: 0.2,
    tintAlphaFar2x: 0.2,
    sizeFineTapShare: 0,
    sizeFineTapSigma: 0,
    sizeFineTapSigma2x: 0,
  },
};

/** The CSS tier's crossing for the 0.25 material: the 0.5 one, unchanged by the refit. */
export const macos27Glass025CssTierMapping: Partial<CssTierMapping> = {
  referenceBackdropLuminance: 0.02,
  borderAlphaPerRimAlpha: {
    regular: 0.64,
    clear: 1.95,
  },
  blurSigmaScale: 2.2,
};

/**
 * Each endpoint's resolved-material digest, the documents' own `resolvedMaterialSha256` under
 * digest rule 2; the receded two over the composition the page performs (the receded difference
 * over the active 0.25 patch of the same scheme over the renderer's default).
 */
export const MACOS_27_GLASS025_RESOLVED_MATERIAL_SHA256 = {
  light: "3741b22934f17f4d",
  dark: "791cde91d97acbc7",
  recededLight: "c4ca0e1cd6791bde",
  recededDark: "be472bc8e42b618d",
} as const;
