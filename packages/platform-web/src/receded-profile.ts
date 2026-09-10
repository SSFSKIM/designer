import type { RendererMaterialProfile } from "./renderer-bridge";

/**
 * The terms shared by the two frozen inactive-window endpoints (W27c G1,
 * claims §5.130). The outer shadow and bright rim disappear; tint strength
 * survives as an achromatic shade, including on a collapsed body.
 *
 * The increased-contrast outline is a signed, one-pixel dark band. On the 1x
 * photo capsule the native first interior row is about 89/255 and the next is
 * 254/255. A width of one and amplitude -3.5 give that narrow subtraction in
 * the existing quadratic rim law. It is not a negative alpha compositor.
 * Accessibility was measured only at 1x, and only in the light scheme.
 */
const common: RendererMaterialProfile = {
  tintChromaScale: 0,
  tintShadeCollapseRetention: 1,
  tintShadeStrength: 1,
  optics: {
    regular: { rimAlpha: 0, rimLevelGain: 0, shadowAlpha: 0 },
    clear: { rimAlpha: 0, rimLevelGain: 0, shadowAlpha: 0 },
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
  increasedOcclusionLift: 0.92,
  strongBorderRim: { rimWidth: 1, rimAlpha: -3.5 },
  sizeScatterRampStartThick1x: 0.3,
  sizeScatterRampStartThick2x: 0.04,
  sizeScatterRampStartFar2x: 0.04,
  sizeHeavyTapSigma2x: 14,
};

/**
 * Differences over the active material, selected AFTER resolving colour scheme.
 * Each scheme has exactly two fixed endpoints; this is not an interpolated pose.
 * A single flat difference could not move the light body down while moving the
 * dark one up through their different response curves, so the scheme seam that
 * already chooses the active document also chooses its inactive difference.
 *
 * The fit and its limits, including the pre-attestation native provenance, are
 * in claims §5.130. G2 applies the selected difference through applyMaterialProfile;
 * G1's calibration harness performs the same merge until that runtime path lands.
 */
export const recededMaterialProfile: Readonly<Record<"light" | "dark", RendererMaterialProfile>> = {
  light: {
    ...common,
    tintShadeDark: 0.0288,
    tintShadeLight: 0.76,
    reducedTintAdaptation: 0.88,
    sizeScatterFloor: 0.7,
    sizeScatterRampStartThin1x: 0.55,
    sizeScatterRampStartThin2x: 0.7,
    backdropToneResponseThin: [0.0126, 0.42, 0.929],
    backdropToneResponseThick: [0.4553, 0.5394, 0.9],
  },
  dark: {
    ...common,
    optics: { ...common.optics, regular: { ...common.optics?.regular, tintAlpha: 0.89 } },
    tintShadeDark: 0.0202,
    tintShadeLight: 1.46,
    reducedTintAdaptation: 0.8,
    sizeScatterFloor: 0.4,
    sizeScatterRampStartThin1x: 1,
    sizeScatterRampStartThin2x: 1,
    sizeScatterHeavyShareThick1x: 0.4,
    backdropToneResponseThin: [0.011, 0.089, 0.1611],
    backdropToneResponseThick: [0.0215, 0.065, 0.02],
  },
};
