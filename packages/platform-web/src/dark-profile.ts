/**
 * The dark-standard material, as a published package carries it.
 *
 * GENERATED — do not edit. `scripts/generate-dark-profile.mjs` writes this file
 * from `packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json`,
 * whose `patch` block is the authority for every number below;
 * `packages/calibration/test/dark-profile-export.test.ts` deep-equals the two in
 * both directions, so a wave that re-records the document and forgets to
 * regenerate this module fails there.
 *
 * ## What it is, and what it is not
 *
 * A **patch** over the renderer's `DEFAULT_MATERIAL_PROFILE`, exactly like the
 * one an app passes as `createGlassRoot({ materialProfile })` — not a second
 * material. Only one colour scheme's numbers can be the runtime default and the
 * default is light-standard, so this document holds the difference: what
 * measurement found the dark reference does differently. The light scheme needs
 * no counterpart, because the light profile document IS the identity with the
 * runtime default (`identityWithRuntimeDefault`, pinned by
 * `tuned-profiles.test.ts`) — "light" is the absence of a patch, not another one.
 *
 * Reach for it through `createGlassRoot({ colorScheme: "dark" | "auto" })`, which
 * selects it and merges an app's own `materialProfile` over the top. It is
 * exported by name as well, because an app that resolves its scheme somewhere
 * vitrea cannot see should be able to hand the patch over directly.
 *
 * A backdrop `hint` and this are different things: the hint states the tone of
 * what is BEHIND the surface, and the scheme states which material the surface
 * is made of.
 */

import type { RendererMaterialProfile } from "./renderer-bridge";

export const darkMaterialProfile: RendererMaterialProfile = {
  backdropToneAnchorX: [0.1104, 0.2706, 0.9505],
  backdropToneResponseThin: [0.011, 0.0284, 0.1611],
  backdropToneResponseThick: [0.0131, 0.0238, 0.1006],
  backdropToneResponseStrength: 1,
  tintShadeStrength: 0,
  optics: {
    regular: {
      tint: [0.05, 0.05, 0.05],
      tintAlpha: 0.9,
      rimAlpha: 0.0265,
      specularGain: 0,
      rimLevelGain: 2.334,
    },
  },
  adaptiveTintDark: [0.05, 0.05, 0.05],
  adaptiveTintLight: [0.05, 0.05, 0.05],
  outerShadow: {
    thinOcclusionDark: 0,
    thinOcclusionMid: 0.063,
    thinOcclusionBright: 0.063,
    thickOcclusionAt96: 0.278,
    thickOcclusionAt128: 0.301,
    thickOcclusionAt160: 0.324,
    liftAmplitude: 0.0051,
    liftSpanMin: 64,
    liftSpanFull: 118,
    liftBlurSigmaCss: 40,
    reducedTransparencyOcclusion: 0.038,
  },
  sizeHeavyTapSigma: 0,
  sizeHeavyTapSigma2x: 0,
};
