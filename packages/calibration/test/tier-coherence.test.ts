/**
 * The mirror between the two tiers' material numbers (corrective K5).
 *
 * C9a tuned the renderer's `tintAlpha` and the CSS tier kept its own untuned
 * copy, so a demotion from `webgpu` to `css` changed the material's opacity by
 * more than 2× — a gap that existed only because the two tiers each held their
 * own constants. K5 replaced the CSS tier's copies with a mapping from the one
 * profile the root carries, which closes it *provided the mapping's input is the
 * renderer's own profile*. That proviso is what this file holds.
 *
 * It cannot be held by an import. `@vitreajs/vitrea-web` has no dependency on
 * `@vitrea/renderer-webgpu` and must not gain one: the renderer loads behind
 * core's lazy seam so a CSS-tier visitor never downloads WGSL (X7), and a static
 * import of the renderer's material module from the package that serves the CSS
 * tier would put the GPU tier's code on the CSS tier's critical path. So
 * platform-web mirrors the slice it needs, and this test — in the one package
 * that legitimately depends on both — pins the mirror in both directions.
 *
 * The same shape as `tuned-profiles.test.ts`, one level along: that file pins
 * the recorded measurement to the renderer's default, this one pins the
 * renderer's default to the CSS tier's view of it. Together they make the
 * calibration profile, the GPU tier and the CSS tier one number rather than
 * three.
 */

import { NOMINAL_ACCESSIBILITY_POLICY, glassTint, resolveAccessibilityPolicy } from "@vitreajs/vitrea";
import {
  BACKDROP_TONE,
  CSS_TIER_MAPPING,
  FOREGROUND_INK,
  INCREASED_OCCLUSION_LIFT,
  adaptedSourceOptics,
  backdropToneAdaptation as cssBackdropToneAdaptation,
  backdropToneUnderPolicy as cssBackdropToneUnderPolicy,
  resolvedBackdropTone,
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_GLOW,
  MATERIAL_SOURCE_OPTICS,
  MATERIAL_SOURCE_OUTER_SHADOW,
  MATERIAL_SOURCE_SIZE,
  REDUCED_TRANSPARENCY_FROST,
  STRONG_BORDER,
  TINT_SHADE,
  authorTintLayer,
  cssOpticsFromSource,
  cssTierDeclarations,
  cssTierForegroundLevel,
  cssTierGroupShadowDeclarations,
  cssTierOptics,
  planCssTierShadow,
  sampledOuterShadowFactor,
  foregroundDeclarations,
  glowAlpha,
  gpuTierForegroundLevel,
  occlusionAlphaUnderPolicy,
  opticsUnderPolicy as cssTierOpticsUnderPolicy,
  OUTER_SHADOW_THICK_SPANS as CSS_OUTER_SHADOW_THICK_SPANS,
  OUTER_SHADOW_THIN_L as CSS_OUTER_SHADOW_THIN_L,
  OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE as CSS_UNMEASURED_BACKDROP,
  cssTierShadowAlpha,
  outerShadowAlpha as cssOuterShadowAlpha,
  outerShadowLiftRise as cssOuterShadowLiftRise,
  outerShadowFalloff as cssOuterShadowFalloff,
  outerShadowOcclusionAt as cssOuterShadowOcclusionAt,
  outerShadowThickOcclusion as cssOuterShadowThickOcclusion,
  outerShadowThinOcclusion as cssOuterShadowThinOcclusion,
  outerShadowUnderPolicy as cssOuterShadowUnderPolicy,
  sizeOuterShadowOcclusionAt as cssSizeOuterShadowOcclusionAt,
  sourceOuterShadow,
  requiredSamplingPadding,
  resolvedPolicyFold,
  resolvedTintShade,
  sizeOcclusionAlpha as cssSizeOcclusionAlpha,
  cssTierHeavyShareAt,
  cssTierHeavySigmaCssPx,
  cssTierHeavyStepSigmaCssPx,
  cssTierSharpSigmaCssPx,
  scatterHeavyEffectiveRatioAtScale,
  scatterHeavyEffectiveSigmaDevicePx,
  scatterDeepThickness as cssScatterDeepThickness,
  scatterFloorAtScale as cssScatterFloorAtScale,
  scatterGainAt as cssScatterGainAt,
  scatterGainAtScale as cssScatterGainAtScale,
  scatterGainFarAtScale as cssScatterGainFarAtScale,
  scatterRampAreaMean as cssScatterRampAreaMean,
  scatterRampReachDevicePx as cssScatterRampReachDevicePx,
  scatterRampStart as cssScatterRampStart,
  scatterSharpShare as cssScatterSharpShare,
  scatterSpanMaxAtScale as cssScatterSpanMaxAtScale,
  scatterThickness as cssScatterThickness,
  sizeScatterSigma as cssSizeScatterSigma,
  sizeScatterSigmaAt as cssSizeScatterSigmaAt,
  sizeThickness as cssSizeThickness,
  sizeThicknessUnderPolicy as cssSizeThicknessUnderPolicy,
  sourceGlow,
  sourceInteriorLight,
  sourceOptics,
  unsampledMaterials,
  sourceSize,
  cssTierFloorAlpha,
  cssTierTintTable,
  linearTint,
  tintedCssOptics,
  innerShadowedSourceOptics,
  interiorBandLight,
  interiorShadowKeep,
  resolvedBackdropToneResponse,
  sizeOcclusionAlphaAt as cssSizeOcclusionAlphaAt,
  toneRespondedSourceOptics,
  type CssTierInterior,
  type CssTierLayer,
  tintShadeLayer as cssTierTintShadeLayer,
  tintToneAdaptation as cssTierTintToneAdaptation,
} from "@vitreajs/vitrea-web";
import {
  DEFAULT_MATERIAL_PROFILE,
  INCREASED_OCCLUSION_LIFT as RENDERER_OCCLUSION_LIFT,
  MATERIAL_VARIANTS,
  adaptedTintAlpha,
  adaptedTintColour,
  backdropToneAdaptation as rendererBackdropToneAdaptation,
  backdropToneResponse as rendererBackdropToneResponse,
  backdropToneSolveWeight as rendererBackdropToneSolveWeight,
  backdropToneUnderPolicy as rendererBackdropToneUnderPolicy,
  occlusionAlphaUnderPolicy as rendererOcclusionAlphaUnderPolicy,
  opticsUnderPolicy as rendererOpticsUnderPolicy,
  OUTER_SHADOW_THICK_SPANS as RENDERER_OUTER_SHADOW_THICK_SPANS,
  OUTER_SHADOW_THIN_L as RENDERER_OUTER_SHADOW_THIN_L,
  OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE as RENDERER_UNMEASURED_BACKDROP,
  outerShadowAlpha as rendererOuterShadowAlpha,
  outerShadowLiftRise as rendererOuterShadowLiftRise,
  outerShadowFalloff as rendererOuterShadowFalloff,
  outerShadowOcclusionAt as rendererOuterShadowOcclusionAt,
  outerShadowThickOcclusion as rendererOuterShadowThickOcclusion,
  outerShadowThinOcclusion as rendererOuterShadowThinOcclusion,
  outerShadowUnderPolicy as rendererOuterShadowUnderPolicy,
  sizeOuterShadowOcclusionAt as rendererSizeOuterShadowOcclusionAt,
  NOMINAL_MATERIAL_POLICY as RENDERER_NOMINAL_POLICY,
  sizeOcclusionAlpha as rendererSizeOcclusionAlpha,
  sizeOcclusionAlphaAt as rendererSizeOcclusionAlphaAt,
  scatterDeepThickness as rendererScatterDeepThickness,
  scatterFloorAtScale as rendererScatterFloorAtScale,
  scatterGainAt as rendererScatterGainAt,
  scatterGainAtScale as rendererScatterGainAtScale,
  scatterGainFarAtScale as rendererScatterGainFarAtScale,
  scatterRampAreaMean as rendererScatterRampAreaMean,
  scatterRampReachDevicePx as rendererScatterRampReachDevicePx,
  scatterRampStart as rendererScatterRampStart,
  scatterSharpShare as rendererScatterSharpShare,
  scatterSpanMaxAtScale as rendererScatterSpanMaxAtScale,
  scatterThickness as rendererScatterThickness,
  sizeScatterSigma as rendererSizeScatterSigma,
  sizeScatterSigmaAt as rendererSizeScatterSigmaAt,
  sizeThickness as rendererSizeThickness,
  sizeThicknessUnderPolicy as rendererSizeThicknessUnderPolicy,
  tintShadeLayer as rendererTintShadeLayer,
  tintToneAdaptation as rendererTintToneAdaptation,
  withMaterialOverrides,
} from "@vitrea/renderer-webgpu";
import { describe, expect, it } from "vitest";

/** IEC 61966-2-1, encode direction — the same spec constant both tiers restate. */
const srgbEncode = (linear: number): number => {
  const clamped = Math.min(1, Math.max(0, linear));
  return clamped <= 0.0031308 ? clamped * 12.92 : 1.055 * clamped ** (1 / 2.4) - 0.055;
};

/** W14 G1's six amplitude anchors — three below the shadow's knee, three above. */
const AMPLITUDE_ANCHORS = [
  "thinOcclusionDark",
  "thinOcclusionMid",
  "thinOcclusionBright",
  "thickOcclusionAt96",
  "thickOcclusionAt128",
  "thickOcclusionAt160",
] as const;

describe("tier coherence (K5)", () => {
  it("mirrors every renderer optic the CSS tier's mapping reads, per variant", () => {
    for (const variant of MATERIAL_VARIANTS) {
      const renderer = DEFAULT_MATERIAL_PROFILE.optics[variant];
      const mirrored = MATERIAL_SOURCE_OPTICS[variant];

      expect(mirrored.blurSigma, variant).toBe(renderer.blurSigma);
      expect(mirrored.tintAlpha, variant).toBe(renderer.tintAlpha);
      expect(mirrored.rimAlpha, variant).toBe(renderer.rimAlpha);
      expect([...mirrored.tint], variant).toEqual([...renderer.tint]);
      expect([...mirrored.highlight], variant).toEqual([...renderer.highlight]);
    }
  });

  it("covers exactly the renderer's variants — a new one must not default silently", () => {
    // A variant the renderer grows and the mirror does not would render on the
    // CSS tier with whatever `cssTierOptics` happened to iterate, which is the
    // quiet-divergence failure this file exists to make loud.
    expect(Object.keys(MATERIAL_SOURCE_OPTICS).sort()).toEqual([...MATERIAL_VARIANTS].sort());
  });

  it("keeps the two tiers on one blur sigma, and core's padding at 3σ of it", () => {
    /*
     * If the CSS tier's blur ever stopped being the renderer's, S1's 3σ sampling
     * floor would silently stop holding for one of the two tiers.
     *
     * This used to assert `blurRadius * 3 === 24`, which was the same invariant
     * with σ = 8 substituted into it. The recalibration cascade refitted σ to 3
     * against the active bed, and 24 was the only part of that line describing a
     * constant rather than a relationship — W6 already made core's advisory
     * DERIVE from the resolved blur precisely so this number follows the material
     * instead of being maintained beside it. The invariant is the multiple.
     */
    const css = cssTierOptics();
    expect(css.regular.blurRadius).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma);
    expect(requiredSamplingPadding(css.regular.blurRadius)).toBe(css.regular.blurRadius * 3);
    /*
     * **The per-layer rule (W16 G1).** This equality is between two numbers in
     * DEVICE px, and it stayed an equality when the CSS tier gained two layers
     * precisely because neither layer takes this σ raw: L1 divides it by the live
     * ratio and L2 multiplies it by the renderer's gain first. So the pin above is
     * the σ the two tiers agree on, and the two below are what each layer makes of
     * it — at dpr 1 the sharp layer writes exactly this number, and at any ratio it
     * writes the same device width.
     */
    for (const dpr of [1, 1.5, 2, 3]) {
      expect(cssTierSharpSigmaCssPx(css.regular.blurRadius, dpr) * dpr, `dpr ${dpr}`).toBeCloseTo(
        scatterHeavyEffectiveSigmaDevicePx(
          DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma,
          dpr,
        ),
        12,
      );
    }
  });

  it("writes an unsampled GPU-tier surface at the CSS tier's alpha and the renderer's tint (W11a)", () => {
    // A group with nothing to sample leaves the shader as a layer the browser
    // composites in encoded sRGB — the CSS tier's space — so its pair is the
    // CSS tier's alpha on the renderer's own linear tint: one number, two
    // tiers, for a nested surface. Pinned on the shipped profile and on a
    // patched one, so a recalibration cannot move one tier's layer alone.
    for (const patch of [undefined, { optics: { regular: { tintAlpha: 0.3 } } }] as const) {
      const layer = unsampledMaterials(patch);
      const css = cssTierOptics(patch);
      const source = sourceOptics(patch);
      for (const variant of ["regular", "clear"] as const) {
        expect(layer[variant].tintAlpha).toBe(css[variant].tintAlpha);
        expect(layer[variant].tint).toEqual(source[variant].tint);
      }
    }
    expect(unsampledMaterials().regular.tint).toEqual(DEFAULT_MATERIAL_PROFILE.optics.regular.tint);
  });

  it("derives a different alpha from the same profile, in the direction the composites imply", () => {
    // Not a tolerance check — the point is that the CSS tier is NOT a copy. An
    // sRGB overlay reaches a given level at a higher alpha than a linear-light
    // lerp does, so the converted alpha must sit above the profile's and below 1.
    const css = cssTierOptics();
    const gpu = DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha;

    expect(css.regular.tintAlpha).toBeGreaterThan(gpu);
    expect(css.regular.tintAlpha).toBeLessThan(1);
  });

  /*
   * Decision Log #32(d): the reduced-transparency lift is one derivation, and the
   * two tiers hold it as a mirror for the same reason they mirror the optics.
   * Pinned here because an absolute floor is exactly what silently died once
   * already, and a floor that dies on one tier and not the other would be worse.
   */
  it("lifts occlusion by the same relative derivation on both tiers", () => {
    expect(INCREASED_OCCLUSION_LIFT).toBe(RENDERER_OCCLUSION_LIFT);
    expect(DEFAULT_MATERIAL_PROFILE.increasedOcclusionLift).toBe(INCREASED_OCCLUSION_LIFT);

    for (const nominal of [0, 0.28, 0.62, 0.9, 1]) {
      expect(occlusionAlphaUnderPolicy(nominal, "increased"), `nominal ${nominal}`).toBeCloseTo(
        rendererOcclusionAlphaUnderPolicy(nominal, "increased"),
        12,
      );
    }
  });

  /*
   * Decision Log #32(b): one tier's ink is decided against that tier's own
   * material. The lift is a patchable profile field and the renderer composites
   * with the patched value, so a decision taken at the *default* lift models a
   * material the renderer did not draw — the same divergence #32(b) closed,
   * arriving through the patch instead of through a second constant. Held here
   * rather than in platform-web because only this package may read both sides.
   */
  it("decides the GPU tier's ink against the alpha the renderer composites, under a patched lift", () => {
    // A lift below the shipped one, on a low-alpha material, over a dark backdrop:
    // the region where the two answers are not merely different numbers but
    // different inks. Nothing selects such a profile today; a calibration pass
    // fitting the lift is exactly what the patch field exists for.
    const patch = { optics: { regular: { tintAlpha: 0.1 } }, increasedOcclusionLift: 0.05 };
    const policy = resolveAccessibilityPolicy({
      reducedTransparency: true,
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: false,
      reducedTransparencySupported: true,
    });
    expect(policy.material.occlusion).toBe("increased");

    // What the renderer composites: its own profile merge, its own fold.
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const rendered = rendererOpticsUnderPolicy(profile.optics.regular, policy.material, profile);

    // What platform-web decides the ink against. Same alpha, to the bit — not to
    // a tolerance: these are the same derivation over the same numbers, and any
    // gap at all is the profile field failing to reach one of the two.
    const decided = occlusionAlphaUnderPolicy(
      sourceOptics(patch).regular.tintAlpha,
      policy.material.occlusion,
      resolvedPolicyFold(patch).increasedOcclusionLift,
    );
    expect(decided).toBe(rendered.tintAlpha);

    // And the ink it buys, against the ink the default lift would have bought.
    const backdrop = 0.05;
    const levelAt = (tintAlpha: number): number =>
      gpuTierForegroundLevel({ ...sourceOptics(patch).regular, tintAlpha }, backdrop);
    const inkAt = (tintAlpha: number): string | undefined =>
      foregroundDeclarations({ policy, level: levelAt(tintAlpha) })["--vitrea-foreground"];
    const atDefaultLift = occlusionAlphaUnderPolicy(
      sourceOptics(patch).regular.tintAlpha,
      policy.material.occlusion,
      INCREASED_OCCLUSION_LIFT,
    );

    // The two levels straddle the crossover rather than sitting near it: the
    // divergence publishes the wrong ink, it does not merely round differently.
    expect(levelAt(rendered.tintAlpha)).toBeLessThan(CSS_TIER_MAPPING.foregroundCrossover);
    expect(levelAt(atDefaultLift)).toBeGreaterThan(CSS_TIER_MAPPING.foregroundCrossover);
    expect(inkAt(rendered.tintAlpha)).toBe(FOREGROUND_INK.light);
    expect(inkAt(atDefaultLift)).toBe(FOREGROUND_INK.dark);
  });

  /*
   * The frost multiplier, the same mirror one field along. Pinned here for the
   * reason the lift is: both are patchable profile fields the renderer already
   * honours, so a mirrored copy that does not follow the patch degrades the two
   * tiers differently under the same preference — which is what §Accessibility's
   * "more frosted" promise is worth on a demoted surface.
   */
  it("thickens the frost by the same multiplier on both tiers, patch included", () => {
    expect(REDUCED_TRANSPARENCY_FROST).toBe(DEFAULT_MATERIAL_PROFILE.reducedTransparencyFrost);

    const patch = { reducedTransparencyFrost: 3 };
    const policy = resolveAccessibilityPolicy({
      reducedTransparency: true,
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: false,
      reducedTransparencySupported: true,
    });
    expect(policy.material.frost).toBe("increased");

    // σ survives the tier conversion unscaled (`blurSigmaScale`, pinned above), so
    // the two folded blurs are the same quantity and comparable directly — which
    // is what makes this a mirror check rather than a coherence-floor one.
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const rendered = rendererOpticsUnderPolicy(profile.optics.regular, policy.material, profile);
    const painted = cssTierOpticsUnderPolicy(
      cssTierOptics(patch).regular,
      policy.material,
      resolvedPolicyFold(patch),
    );

    expect(painted.blurRadius).toBe(rendered.blurSigma);
    // And the patch actually moved something: at the shipped multiplier this same
    // surface frosts to a different σ, so an equality that ignored the patch would
    // not have passed by accident.
    expect(painted.blurRadius).not.toBe(
      cssTierOpticsUnderPolicy(cssTierOptics(patch).regular, policy.material).blurRadius,
    );
    /*
     * **The per-layer rule (W16 G1).** The frost multiplies the BASE σ, which is
     * the one number both of the CSS tier's layers are built from — L1 is it
     * divided by the ratio and L2 is it times the renderer's gain — so a frosted
     * surface widens both components by the same multiplier and the composed body
     * is the frosted body. That is the fold applying once on the composed mix,
     * which is what the charter's accessibility advisory asks for, and it is why
     * this case did not have to grow a branch per layer.
     *
     * The occlusion lift is the other half and it does NOT reach either filter:
     * it lifts the tint's alpha, which lives on L3 above them both.
     */
    for (const dpr of [1, 2]) {
      expect(
        cssTierSharpSigmaCssPx(painted.blurRadius, dpr) * dpr,
        `frosted L1 at dpr ${dpr}`,
      ).toBeCloseTo(scatterHeavyEffectiveSigmaDevicePx(rendered.blurSigma, dpr), 12);
      expect(
        cssTierHeavySigmaCssPx(painted.blurRadius, 96, sourceSize(patch), dpr) * dpr,
        `frosted L2 at dpr ${dpr}`,
      ).toBeCloseTo(
        scatterHeavyEffectiveSigmaDevicePx(
          rendered.blurSigma * rendererScatterGainAt(96, profile, dpr),
          dpr,
        ),
        12,
      );
    }
  });

  /*
   * The strong border, the last of the fold's mirrored constants — and the one
   * that crosses the boundary *unconverted*, deliberately. `borderAlphaPerRimAlpha`
   * is fitted for the nominal regime, where the renderer's ambient rim and this
   * tier's drawn border are different constructs; a near-opaque accessibility
   * floor is not that regime, and at α = 0.95 the compositing difference the
   * mapping corrects for has collapsed. So the pin is equality, and equality is
   * what makes the shipped pair byte-identical on both tiers.
   */
  it("draws one strong border on both tiers, patch included", () => {
    expect(STRONG_BORDER.borderWidth).toBe(DEFAULT_MATERIAL_PROFILE.strongBorderRim.rimWidth);
    expect(STRONG_BORDER.borderAlpha).toBe(DEFAULT_MATERIAL_PROFILE.strongBorderRim.rimAlpha);

    const patch = { strongBorderRim: { rimWidth: 4, rimAlpha: 0.5 } };
    const policy = resolveAccessibilityPolicy({
      reducedTransparency: false,
      reducedMotion: false,
      increasedContrast: true,
      forcedColors: false,
      reducedTransparencySupported: true,
    });
    expect(policy.material.border).toBe("strong");

    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const rendered = rendererOpticsUnderPolicy(profile.optics.regular, policy.material, profile);
    const painted = cssTierOpticsUnderPolicy(
      cssTierOptics(patch).regular,
      policy.material,
      resolvedPolicyFold(patch),
    );

    expect(painted.borderWidth).toBe(rendered.rimWidth);
    expect(painted.borderAlpha).toBe(rendered.rimAlpha);
    // And the patch actually moved both numbers, so the equality cannot be
    // passing on the shipped pair by accident.
    expect(painted.borderWidth).not.toBe(STRONG_BORDER.borderWidth);
    expect(painted.borderAlpha).not.toBe(STRONG_BORDER.borderAlpha);
  });

  /*
   * The press glow, and the reason this pin exists at all (W1/coherence, the
   * post-v1 wave's first cross-tier finding).
   *
   * The GPU tier drew the press illumination and the CSS tier drew none, so the
   * two tiers agreed on a resting surface and diverged the moment one was held
   * down. Invisible in the light scheme — a lerp toward white over a material
   * already at encoded 0.85 moves the interior by ~2% — and enormous in the dark
   * one, where the same lerp over encoded 0.26 nearly doubles it. The measured
   * cell: `photo__capsule-button__pressed`, interior level GPU/CSS 1.964 at 1×
   * and 1.985 at 2×, against 0.937 for the worst light profile on the same scene.
   *
   * Unlike `tintAlpha`, the glow crosses the boundary UNCONVERTED, and that is a
   * finding rather than an omission: the renderer's highlight pass encodes to
   * sRGB before it blends (`encode_output` premultiplies `linear_to_srgb(c)` and
   * the target is a non-sRGB canvas format), so it is already doing what an
   * `rgba()` layer does. `cssTintAlpha` exists because the body composites in
   * linear light; the glow does not, so there is nothing to solve for.
   */
  it("mirrors the renderer's press-glow constants, patch included", () => {
    expect(MATERIAL_SOURCE_GLOW.gain).toBe(DEFAULT_MATERIAL_PROFILE.glowGain);
    expect(MATERIAL_SOURCE_GLOW.radiusCss).toBe(DEFAULT_MATERIAL_PROFILE.glowRadiusCss);

    const patch = { glowGain: 0.25, glowRadiusCss: 12 };
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    expect(sourceGlow(patch).gain).toBe(profile.glowGain);
    expect(sourceGlow(patch).radiusCss).toBe(profile.glowRadiusCss);
    // And it reaches the numbers the tier actually paints with, not only the
    // mirror — the patch moved both, so neither equality is the default's.
    expect(cssTierOptics(patch).regular.glowGain).toBe(profile.glowGain);
    expect(cssTierOptics(patch).regular.glowRadius).toBe(profile.glowRadiusCss);
    expect(cssTierOptics(patch).regular.glowGain).not.toBe(MATERIAL_SOURCE_GLOW.gain);
    expect(cssTierOptics(patch).regular.glowRadius).not.toBe(MATERIAL_SOURCE_GLOW.radiusCss);
  });

  it("illuminates a held dark-scheme surface to the same level on both tiers", () => {
    // The reproduction of W1/coherence, as arithmetic rather than as a capture:
    // the dark profile a host passes for dark mode, over the `photo` backdrop's
    // measured level, at the pressed pose's settled glow of 1.
    const patch = {
      optics: { regular: { tint: [0.05, 0.05, 0.05] as const, tintAlpha: 0.97 } },
    };
    const backdrop = 0.2;
    const glow = 1;

    // Both tiers' glow is a source-over lerp toward the highlight in ENCODED
    // sRGB, so the level after it is the same arithmetic over each tier's own
    // pre-glow level. What must not differ is the alpha.
    const highlight = MATERIAL_SOURCE_OPTICS.regular.highlight;
    const encodedHighlight =
      0.2126 * srgbEncode(highlight[0]) +
      0.7152 * srgbEncode(highlight[1]) +
      0.0722 * srgbEncode(highlight[2]);
    const lit = (level: number, alpha: number): number =>
      level * (1 - alpha) + encodedHighlight * alpha;

    const gpu = lit(
      gpuTierForegroundLevel(sourceOptics(patch).regular, backdrop),
      sourceGlow(patch).gain * glow,
    );
    const css = lit(
      cssTierForegroundLevel(cssTierOptics(patch).regular, backdrop),
      glowAlpha(cssTierOptics(patch).regular, glow),
    );

    // The gated bound the light profiles are held to. Before the CSS tier drew
    // the glow this ratio was ~1.9 on the measured cell, and the arithmetic here
    // reproduces it: an unlit CSS level against a lit GPU one.
    expect(gpu / css).toBeGreaterThan(0.8);
    expect(gpu / css).toBeLessThan(1.25);

    // And the glow is doing the work rather than the bound being wide: the same
    // comparison with the CSS tier unlit — the defect — is outside it.
    const unlit = cssTierForegroundLevel(cssTierOptics(patch).regular, backdrop);
    expect(gpu / unlit).toBeGreaterThan(1.25);
  });

  /*
   * The size law's mirror (W2). The same doctrine one facet along: the law's
   * constants live in the renderer's profile, platform-web restates the slice it
   * needs, and a drift between the two would make a demoted platter scatter and
   * occlude differently from the one the GPU tier was drawing a frame earlier —
   * exactly K5's defect, on a new axis. Pinned in both directions, and through a
   * patch, so a retune moves both or neither.
   */
  it("mirrors the size law's constants, patch included", () => {
    expect(MATERIAL_SOURCE_SIZE.sizeSpanMin).toBe(DEFAULT_MATERIAL_PROFILE.sizeSpanMin);
    expect(MATERIAL_SOURCE_SIZE.sizeSpanMax).toBe(DEFAULT_MATERIAL_PROFILE.sizeSpanMax);
    expect(MATERIAL_SOURCE_SIZE.sizeScatterGainMax).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterGainMax,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterFloor).toBe(DEFAULT_MATERIAL_PROFILE.sizeScatterFloor);
    // The body's second scale (W15 G1, claims §5.69 §1–§2). Each defaults to
    // its 1x constant, so this equality is also the record that the landed
    // material is scale-free in all three.
    expect(MATERIAL_SOURCE_SIZE.sizeScatterGainMax2x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterGainMax2x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterFloor2x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterFloor2x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterSpanMax2x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterSpanMax2x,
    );
    // W15 G1's re-form: the 2x gain's own span grading (claims §5.70 §4, §7).
    expect(MATERIAL_SOURCE_SIZE.sizeScatterGainFar2x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterGainFar2x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampStartThin1x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThin1x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampStartThick1x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThick1x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampStartThin2x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThin2x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampStartThick2x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartThick2x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampStartFar1x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartFar1x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampStartFar2x).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampStartFar2x,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampReach1xPx).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampReach1xPx,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeScatterRampReach2xPx).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterRampReach2xPx,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeOcclusionGain).toBe(DEFAULT_MATERIAL_PROFILE.sizeOcclusionGain);

    const patch = {
      sizeSpanMin: 40,
      sizeSpanMax: 200,
      sizeScatterGainMax: 2.5,
      sizeScatterFloor: 0.25,
      sizeScatterGainMax2x: 3.5,
      sizeScatterFloor2x: 0.85,
      sizeScatterSpanMax2x: 180,
      sizeScatterGainFar2x: 6.5,
      sizeScatterRampStartThin1x: 0.7,
      sizeScatterRampStartThick1x: 0.55,
      sizeScatterRampStartThin2x: 0.3,
      sizeScatterRampStartThick2x: 0.15,
      sizeScatterRampStartFar1x: 0.45,
      sizeScatterRampStartFar2x: 0.1,
      sizeScatterRampReach1xPx: 90,
      sizeScatterRampReach2xPx: 130,
      sizeOcclusionGain: 0.4,
    };
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const mirrored = sourceSize(patch);
    expect(mirrored.sizeSpanMin).toBe(profile.sizeSpanMin);
    expect(mirrored.sizeSpanMax).toBe(profile.sizeSpanMax);
    expect(mirrored.sizeScatterGainMax).toBe(profile.sizeScatterGainMax);
    expect(mirrored.sizeScatterFloor).toBe(profile.sizeScatterFloor);
    expect(mirrored.sizeScatterGainMax2x).toBe(profile.sizeScatterGainMax2x);
    expect(mirrored.sizeScatterFloor2x).toBe(profile.sizeScatterFloor2x);
    expect(mirrored.sizeScatterSpanMax2x).toBe(profile.sizeScatterSpanMax2x);
    expect(mirrored.sizeScatterGainFar2x).toBe(profile.sizeScatterGainFar2x);
    expect(mirrored.sizeScatterRampStartThin1x).toBe(profile.sizeScatterRampStartThin1x);
    expect(mirrored.sizeScatterRampStartThick1x).toBe(profile.sizeScatterRampStartThick1x);
    expect(mirrored.sizeScatterRampStartThin2x).toBe(profile.sizeScatterRampStartThin2x);
    expect(mirrored.sizeScatterRampStartThick2x).toBe(profile.sizeScatterRampStartThick2x);
    expect(mirrored.sizeScatterRampStartFar1x).toBe(profile.sizeScatterRampStartFar1x);
    expect(mirrored.sizeScatterRampStartFar2x).toBe(profile.sizeScatterRampStartFar2x);
    expect(mirrored.sizeScatterRampReach1xPx).toBe(profile.sizeScatterRampReach1xPx);
    expect(mirrored.sizeScatterRampReach2xPx).toBe(profile.sizeScatterRampReach2xPx);
    expect(mirrored.sizeOcclusionGain).toBe(profile.sizeOcclusionGain);
    // And the patch really moved them, so none of the equalities above is the
    // default agreeing with itself.
    expect(mirrored.sizeSpanMax).not.toBe(MATERIAL_SOURCE_SIZE.sizeSpanMax);
  });

  /*
   * The body's depth ramp and its projection (W13 G1, claims §5.61 §2). The GPU
   * tier mixes per pixel and the CSS tier has one `blur()`, so what has to be
   * one law across the seam is the ramp itself AND the area average the CSS tier
   * renders in its place — a drift in either would make a demoted platter
   * scatter differently from the one the GPU tier was drawing a frame earlier,
   * which is K5's defect on the axis the reference's own kernel lives on.
   * Pinned over dpr ∈ {1, 1.5, 2, 3} and spans across the band, on the shipped
   * profile AND on a patch, so a sweep that fits the six constants moves both
   * mirrors together.
   */
  it("mixes toward the heavy blur by the same depth ramp on both tiers", () => {
    const patches = [
      undefined,
      {
        sizeSpanMin: 40,
        sizeSpanMax: 200,
        sizeScatterGainMax: 6,
        sizeScatterFloor: 0.25,
        sizeScatterSpanMax: 320,
        sizeScatterRampStartThin1x: 0.7,
        sizeScatterRampStartThick1x: 0.55,
        sizeScatterRampStartThin2x: 0.3,
        sizeScatterRampStartThick2x: 0.15,
        sizeScatterRampStartFar1x: 0.45,
        sizeScatterRampStartFar2x: 0.1,
        sizeScatterRampReach1xPx: 90,
        sizeScatterRampReach2xPx: 130,
      },
      /*
       * The body's second scale (W15 G1, claims §5.69 §1–§2), all three terms
       * off their 1x values at once. The 1x half of this patch is the shipped
       * material, so every quantity below at dpr 1 is the landed law and every
       * quantity at dpr 2 is the second scale's — which is the wave's binding
       * rule expressed as a mirror pin: the two tiers derive the same deep
       * value, the same share and the same projection at every ratio, and the
       * ratio moves them only through these three constants and the ramp's
       * anchors.
       */
      {
        sizeScatterGainMax2x: 5.5,
        sizeScatterFloor2x: 0.9,
        sizeScatterSpanMax2x: 120,
      },
      /*
       * And all FOUR at once (W15 G1's re-form, claims §5.70 §4 and §7): the 2x
       * gain graded in span on top of the three above, which is the case where
       * the σ the two mirrors project depends on the span through the WIDTH as
       * well as through the mix. If either mirror graded on a different curve —
       * or read a different span top — this is where the two would part.
       */
      {
        sizeScatterGainMax2x: 4.8,
        sizeScatterGainFar2x: 9.9,
        sizeScatterFloor2x: 1,
        sizeScatterSpanMax2x: 256,
      },
    ] as const;
    const SPANS = [32, 44, 96, 128, 160, 256] as const;
    const RATIOS = [1, 1.5, 2, 3] as const;
    for (const patch of patches) {
      const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch ?? {});
      const mirrored = sourceSize(patch);
      for (const dpr of RATIOS) {
        // The law itself, before any projection: the two anchors and the share
        // at a spread of depths through the reach.
        // s₀ grades with the span since the third form, so the mirror is
        // pinned across the span axis and not only at the thin end.
        for (const span of [0, 32, 44, 64, 96, 160, 400]) {
          expect(
            cssScatterRampStart(dpr, mirrored, span),
            `s0 at span ${span} dpr ${dpr}`,
          ).toBeCloseTo(rendererScatterRampStart(dpr, profile, span), 12);
        }
        expect(cssScatterRampReachDevicePx(dpr, mirrored), `U at dpr ${dpr}`).toBe(
          rendererScatterRampReachDevicePx(dpr, profile),
        );
        // The second scale's three constants, resolved (W15 G1): the deep
        // value's own curve is pinned across the span axis, not only through
        // the projection that averages it.
        expect(cssScatterFloorAtScale(mirrored, dpr), `floor at dpr ${dpr}`).toBeCloseTo(
          rendererScatterFloorAtScale(profile, dpr),
          12,
        );
        expect(cssScatterSpanMaxAtScale(mirrored, dpr), `span top at dpr ${dpr}`).toBeCloseTo(
          rendererScatterSpanMaxAtScale(profile, dpr),
          12,
        );
        expect(cssScatterGainAtScale(mirrored, dpr), `gain at dpr ${dpr}`).toBeCloseTo(
          rendererScatterGainAtScale(profile, dpr),
          12,
        );
        expect(cssScatterGainFarAtScale(mirrored, dpr), `far gain at dpr ${dpr}`).toBeCloseTo(
          rendererScatterGainFarAtScale(profile, dpr),
          12,
        );
        // The gain graded in span (W15 G1's re-form): pinned on the span axis
        // itself and not only through the σ that consumes it.
        for (const span of [0, 32, 44, 96, 128, 160, 256, 400]) {
          expect(
            cssScatterGainAt(span, mirrored, dpr),
            `gain at span ${span} dpr ${dpr}`,
          ).toBeCloseTo(rendererScatterGainAt(span, profile, dpr), 12);
        }
        for (const span of [0, 32, 44, 96, 128, 160, 256, 400]) {
          expect(
            cssScatterDeepThickness(span, mirrored, dpr),
            `kDeep at span ${span} dpr ${dpr}`,
          ).toBeCloseTo(rendererScatterDeepThickness(span, profile, dpr), 12);
        }
        // The share is a function of the depth AND the span since the ramp was
        // re-formed onto the span curve, so both axes are swept here.
        for (const u of [0, 4, 12, 24, 48, 96, 200, 400]) {
          for (const span of [0, 44, 160, 400]) {
            expect(
              cssScatterSharpShare(u, dpr, mirrored, span),
              `s(${u}) at span ${span} dpr ${dpr}`,
            ).toBeCloseTo(rendererScatterSharpShare(u, dpr, profile, span), 12);
          }
        }
        for (const span of SPANS) {
          expect(
            cssScatterRampAreaMean(span, mirrored, dpr),
            `projection at span ${span} dpr ${dpr}`,
          ).toBeCloseTo(rendererScatterRampAreaMean(span, profile, dpr), 12);
          // And over the surface's own extents, which is what the CSS tier
          // declares for a measured host: a strip is not a square of its span.
          for (const extents of [[span, span], [span * 4, span], [span, span * 7]] as const) {
            expect(
              cssScatterRampAreaMean(span, mirrored, dpr, extents),
              `projection at ${extents[0]}x${extents[1]} dpr ${dpr}`,
            ).toBeCloseTo(rendererScatterRampAreaMean(span, profile, dpr, extents), 12);
            expect(
              cssScatterThickness(span, 1, mirrored, dpr, extents),
              `thickness at ${extents[0]}x${extents[1]} dpr ${dpr}`,
            ).toBeCloseTo(rendererScatterThickness(span, 1, profile, dpr, extents), 12);
          }
          for (const fold of [0, 0.45, 1]) {
            const label = `span ${span} fold ${fold} dpr ${dpr}`;
            const css = cssScatterThickness(span, fold, mirrored, dpr);
            const gpu = rendererScatterThickness(span, fold, profile, dpr);
            expect(css, label).toBeCloseTo(gpu, 12);
            expect(cssSizeScatterSigmaAt(1.25, css, mirrored), `σ at ${label}`).toBeCloseTo(
              rendererSizeScatterSigmaAt(1.25, gpu, profile),
              12,
            );
            // And with the span handed over, which is the form `sizeScatterSigma`
            // uses since W15 G1's re-form: the heavy end of the mix is the gain
            // at THIS span, so the two mirrors have to grade it identically.
            expect(
              cssSizeScatterSigmaAt(1.25, css, mirrored, dpr, span),
              `graded σ at ${label}`,
            ).toBeCloseTo(rendererSizeScatterSigmaAt(1.25, gpu, profile, dpr, span), 12);
            expect(
              cssSizeScatterSigma(1.25, span, mirrored, dpr),
              `span form at ${label}`,
            ).toBeCloseTo(rendererSizeScatterSigma(1.25, span, profile, dpr), 12);
          }
          // The floor is unfolded on both tiers: fold 0 leaves it, and only it.
          // The floor is itself per-scale since W15 G1, so what fold 0 has to
          // land on is the floor THIS ratio resolves — which is the 1x constant
          // at dpr ≤ 1 and on the landed material at every ratio.
          expect(cssScatterThickness(span, 0, mirrored, dpr), `floor at span ${span}`).toBeCloseTo(
            cssScatterFloorAtScale(mirrored, dpr),
            12,
          );
          expect(
            rendererScatterThickness(span, 0, profile, dpr),
            `floor at span ${span} (renderer)`,
          ).toBeCloseTo(rendererScatterFloorAtScale(profile, dpr), 12);
        }
      }
    }
    // The shipped numbers, stated. The projection rises with the span on both
    // tiers, and in this SHARED projection the widths are 1.25 and 10 CSS px at
    // every device scale — so a fully heavy mix is 10 CSS px on both tiers
    // whatever the ratio. W15 G1 restored the device-pixel reading of the sharp
    // width on the GPU tier alone, inside the renderer's own `bodySigmaCssFor`;
    // this projection is what the CSS tier writes and what a proxy's padding is
    // taken over, and W15 Decision Log 2 leaves it at the 1x law until G1
    // predicts the tier's 2x σ.
    expect(rendererScatterThickness(160, 1)).toBeGreaterThan(rendererScatterThickness(96, 1));
    expect(rendererScatterThickness(96, 1)).toBeGreaterThan(rendererScatterThickness(44, 1));
    expect(cssScatterThickness(160, 1)).toBeGreaterThan(cssScatterThickness(96, 1));
    expect(cssSizeScatterSigmaAt(1.25, 1, MATERIAL_SOURCE_SIZE)).toBeCloseTo(10, 12);
    expect(rendererSizeScatterSigmaAt(1.25, 1, DEFAULT_MATERIAL_PROFILE)).toBeCloseTo(10, 12);
  });

  /*
   * The scattering facet's S1 consequence at a second device scale: the 3σ
   * padding floor is taken over the σ the tier will REALLY write. Since W13
   * Decision Log 8 the ratio never DIVIDES that σ in this shared projection;
   * what it reaches is the heavy width's gain, which W15 G1 fitted at dpr 2
   * (claims §5.70 §2). So what is pinned here is that both tiers resolve one
   * number at every ratio and span.
   *
   * Since W16 G1 this projection is no longer what the CSS tier writes — the
   * tier draws two layers at device-pixel widths through the live ratio, pinned
   * in the case below — and its remaining consumers are the WebGPU tier's proxy
   * (`WEBGPU_PROXY_PROJECTION_SCALE`, bound byte-identical by that wave) and the
   * `--vitrea-blur` token. The case keeps its name because the invariant it
   * holds is unchanged: whatever the projection is taken for, the two mirrors
   * resolve one number for it.
   */
  it("takes the 3σ padding floor over the σ the tier actually writes, at every device scale", () => {
    const shipped = cssTierOptics().regular.blurRadius;
    for (const dpr of [1, 1.5, 2, 3]) {
      const platter = cssSizeScatterSigma(shipped, 160, MATERIAL_SOURCE_SIZE, dpr);
      expect(platter, `dpr ${dpr}`).toBeCloseTo(
        rendererSizeScatterSigma(shipped, 160, DEFAULT_MATERIAL_PROFILE, dpr),
        12,
      );
      expect(requiredSamplingPadding(platter), `dpr ${dpr}`).toBeCloseTo(3 * platter, 12);
    }
    // At a fixed mix and a fixed ratio the width is one number on both tiers:
    // the thickness form takes no ratio of its own (W13 Decision Log 8 retired
    // the device-pixel widths on the bed), so the two mirrors cannot disagree
    // about what a padding floor is taken over.
    for (const mix of [0, 0.4, 1]) {
      expect(cssSizeScatterSigmaAt(shipped, mix, MATERIAL_SOURCE_SIZE), `mix ${mix}`).toBeCloseTo(
        rendererSizeScatterSigmaAt(shipped, mix, DEFAULT_MATERIAL_PROFILE),
        12,
      );
    }
    /*
     * The ratio this form does take (W15 G1) is the heavy width's GAIN and never
     * a division. The CSS mirror kept a fourth argument after W13 Decision Log 8
     * and divided by it, which is how the two mirrors came to disagree by the
     * ratio itself; what replaces that arity pin is the meaning it was standing
     * in for, stated at both ends of the mix.
     *
     * At mix 0 the sharp width is the profile's own σ at every ratio, on both
     * tiers and under a patch that moves the 2x gain — a division would halve
     * it. At mix 1 the σ is the ratio's own gain times that σ, so a fourth
     * argument is a parameter with exactly one meaning.
     */
    const gainPatch = { sizeScatterGainMax2x: 5.5 };
    const gainProfile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, gainPatch);
    const gainMirror = sourceSize(gainPatch);
    for (const dpr of [1, 1.5, 2, 3]) {
      expect(cssSizeScatterSigmaAt(1.25, 0, gainMirror, dpr), `sharp at ${dpr}`).toBeCloseTo(
        1.25,
        12,
      );
      expect(rendererSizeScatterSigmaAt(1.25, 0, gainProfile, dpr), `sharp at ${dpr}`).toBeCloseTo(
        1.25,
        12,
      );
      expect(cssSizeScatterSigmaAt(1.25, 1, gainMirror, dpr), `heavy at ${dpr}`).toBeCloseTo(
        rendererSizeScatterSigmaAt(1.25, 1, gainProfile, dpr),
        12,
      );
    }
    // 8 at dpr 1, 5.5 at dpr 2, linear between — the gain and nothing else.
    expect(rendererSizeScatterSigmaAt(1.25, 1, gainProfile, 1)).toBeCloseTo(10, 12);
    expect(rendererSizeScatterSigmaAt(1.25, 1, gainProfile, 1.5)).toBeCloseTo(1.25 * 6.75, 12);
    expect(rendererSizeScatterSigmaAt(1.25, 1, gainProfile, 2)).toBeCloseTo(1.25 * 5.5, 12);
    expect(rendererSizeScatterSigmaAt(1.25, 1, gainProfile, 3)).toBeCloseTo(1.25 * 5.5, 12);
    /*
     * **Retired at W16 G1: the area-mean projection sweep.** What stood here was
     * a loop asserting that the CSS tier's own declared σ is the 1x law's — 10
     * CSS px — at every ratio and every span, because the tier read the law at
     * `CSS_TIER_RAMP_SCALE`. That was W13 Decision Log 5 expressed as a pin, and
     * W16 G1 overturned the decision it pinned: the tier now draws two layers at
     * device-pixel widths through the live ratio, so a sweep asserting one σ at
     * every ratio would be asserting the opposite of what the tier does. Its
     * successor is the per-layer case below, which pins both widths and the share
     * against the renderer's own functions over the same ratios — a stronger
     * statement, because it constrains the two components rather than their
     * average.
     *
     * The SHARED projection does still move with the ratio — the 2x gain is 4.8
     * and its top 9.9 (claims §5.70 §8) — so the two mirrors stay pinned to each
     * other at every ratio and span. A disagreement between them is the failure
     * this case exists for.
     */
    for (const dpr of [1, 1.5, 2, 3]) {
      expect(
        cssSizeScatterSigmaAt(1.25, 1, MATERIAL_SOURCE_SIZE, dpr),
        `mirrors at ${dpr}`,
      ).toBeCloseTo(rendererSizeScatterSigmaAt(1.25, 1, DEFAULT_MATERIAL_PROFILE, dpr), 12);
      for (const span of [0, 32, 96, 160, 256, 400]) {
        expect(
          cssSizeScatterSigmaAt(1.25, 1, MATERIAL_SOURCE_SIZE, dpr, span),
          `mirrors at ${dpr} span ${span}`,
        ).toBeCloseTo(
          rendererSizeScatterSigmaAt(1.25, 1, DEFAULT_MATERIAL_PROFILE, dpr, span),
          12,
        );
      }
    }
    // The landed 2x body, stated: 6 device px of heavy width up to the knee and
    // growing above it, against 10 CSS px at dpr 1 (claims §5.70 §1, §8).
    expect(rendererSizeScatterSigmaAt(1.25, 1, DEFAULT_MATERIAL_PROFILE, 1)).toBeCloseTo(10, 12);
    expect(rendererSizeScatterSigmaAt(1.25, 1, DEFAULT_MATERIAL_PROFILE, 2, 96)).toBeCloseTo(
      1.25 * 4.8,
      12,
    );
    expect(rendererSizeScatterSigmaAt(1.25, 1, DEFAULT_MATERIAL_PROFILE, 2, 256)).toBeCloseTo(
      1.25 * 9.9,
      12,
    );
  });

  /**
   * **X7 — the two-layer body, pinned per layer over dpr {1, 1.5, 2, 3}**
   * (W16 G1; charter Decision Log 2 (c), contract X7).
   *
   * The CSS tier draws two `backdrop-filter` layers and a mask, and every
   * quantity in all three is the renderer's own read at the live ratio. This is
   * the case that says so, and it is the successor to the area-mean projection
   * sweep retired above: it constrains the two components rather than their
   * average, which is exactly the difference the wave landed.
   *
   * Four statements, and each one is a way the tiers could silently part:
   *
   *  1. **L1 is the profile's σ as a DEVICE-pixel width.** `sharpσ · dpr` is the
   *     renderer's `blurSigma` at every ratio. A tier that forgot the division
   *     would draw a sharp component twice as wide at dpr 2 as the renderer's.
   *  2. **L2's composed width is the renderer's kernel's effective one.** The
   *     nominal is `blurSigma · scatterGainAt(span, dpr)` in device px through
   *     the renderer's own span-graded gain; the conversion to what the mip chain
   *     really draws is `scatterHeavyEffectiveSigmaDevicePx`, and it is measured
   *     rather than fitted (claims §5.71 §5). A ratio, a gain or a grading that
   *     reached one tier and not the other shows up here at one span.
   *  3. **L2's own step composes to that width.** Two Gaussians in series add in
   *     quadrature and the heavy layer blurs the sharp layer's output, so
   *     `√(sharpσ² + stepσ²)` has to be the composed width exactly — the arithmetic
   *     the whole element model rests on (claims §5.42 §5).
   *  4. **The mask's share is the renderer's ramp, and its area mean is the
   *     projection.** The per-pixel share is one minus the renderer's own
   *     `scatterSharpShare` under the same fold `scatterThickness` applies, so
   *     the tier cannot draw a band the projection would not have averaged to.
   */
  it("draws the two-layer body at the renderer's own widths and share, over dpr {1, 1.5, 2, 3}", () => {
    const base = DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma;
    for (const dpr of [1, 1.5, 2, 3]) {
      const sharp = cssTierSharpSigmaCssPx(base, dpr);
      /*
       * L1 is the profile's σ as a device-pixel width, carried through the same
       * effective conversion the heavy component takes — one kernel, one mip
       * chain, one conversion (W16 G1's re-form; the sharp width at the nominal
       * put the interior spread 0.013–0.018 over native on four cells of the
       * dry run, and this puts it inside ±0.016 on every one).
       */
      expect(sharp * dpr, `L1 is a device width at dpr ${dpr}`).toBeCloseTo(
        scatterHeavyEffectiveSigmaDevicePx(base, dpr),
        12,
      );

      for (const span of [0, 32, 44, 96, 128, 160, 256, 400]) {
        const label = `dpr ${dpr}, span ${span}`;
        const nominalDevicePx = base * rendererScatterGainAt(span, DEFAULT_MATERIAL_PROFILE, dpr);
        const heavy = cssTierHeavySigmaCssPx(base, span, MATERIAL_SOURCE_SIZE, dpr);
        expect(heavy * dpr, `L2 composed at ${label}`).toBeCloseTo(
          scatterHeavyEffectiveSigmaDevicePx(nominalDevicePx, dpr),
          12,
        );
        // The gain the width is a multiple of is one law across the seam.
        expect(
          cssScatterGainAt(span, MATERIAL_SOURCE_SIZE, dpr),
          `gain at ${label}`,
        ).toBeCloseTo(rendererScatterGainAt(span, DEFAULT_MATERIAL_PROFILE, dpr), 12);

        const step = cssTierHeavyStepSigmaCssPx(sharp, heavy);
        expect(Math.hypot(sharp, step), `quadrature at ${label}`).toBeCloseTo(heavy, 12);

        // The share, at the contour, at the reach and across it. `fold` 1 is the
        // nominal regime; the fold is exercised on its own below.
        for (const u of [0, 4, 12, 40, 100, 400]) {
          expect(
            cssTierHeavyShareAt(u, dpr, 1, MATERIAL_SOURCE_SIZE, span),
            `share at u ${u}, ${label}`,
          ).toBeCloseTo(1 - rendererScatterSharpShare(u, dpr, DEFAULT_MATERIAL_PROFILE, span), 12);
        }
        // Beyond the reach the share is the deep value and nothing else.
        const reach = cssScatterRampReachDevicePx(dpr, MATERIAL_SOURCE_SIZE);
        expect(
          cssTierHeavyShareAt(reach + 1, dpr, 1, MATERIAL_SOURCE_SIZE, span),
          `deep at ${label}`,
        ).toBeCloseTo(cssScatterDeepThickness(span, MATERIAL_SOURCE_SIZE, dpr), 12);
      }

      /*
       * The accessibility fold is one fold on the mask too: it scales the
       * excursion away from the scatter floor and never the floor itself, which
       * is what makes the mask's area mean the projection `scatterThickness`
       * resolves rather than a second reading of the law.
       */
      for (const fold of [0, 0.35, 1]) {
        const floor = cssScatterFloorAtScale(MATERIAL_SOURCE_SIZE, dpr);
        for (const u of [0, 20, 400]) {
          const unfolded = cssTierHeavyShareAt(u, dpr, 1, MATERIAL_SOURCE_SIZE, 160);
          expect(
            cssTierHeavyShareAt(u, dpr, fold, MATERIAL_SOURCE_SIZE, 160),
            `folded share at u ${u}, dpr ${dpr}, fold ${fold}`,
          ).toBeCloseTo(Math.min(1, Math.max(0, floor + (unfolded - floor) * fold)), 12);
        }
      }
    }

    /*
     * The second scale, stated. At dpr 1 the tier's composed heavy width is the
     * 1x law's 10 CSS px through the effective conversion; at dpr 2 it is the 2x
     * gain's, halved into CSS px — which is the whole of what W15 Decision Log 3
     * held back and W16 G1 released.
     */
    expect(cssTierHeavySigmaCssPx(1.25, 96, MATERIAL_SOURCE_SIZE, 1)).toBeCloseTo(
      scatterHeavyEffectiveSigmaDevicePx(1.25 * 8, 1),
      12,
    );
    expect(cssTierHeavySigmaCssPx(1.25, 96, MATERIAL_SOURCE_SIZE, 2)).toBeCloseTo(
      scatterHeavyEffectiveSigmaDevicePx(1.25 * 4.8, 2) / 2,
      12,
    );
    expect(cssTierHeavySigmaCssPx(1.25, 256, MATERIAL_SOURCE_SIZE, 2)).toBeCloseTo(
      scatterHeavyEffectiveSigmaDevicePx(1.25 * 9.9, 2) / 2,
      12,
    );
    /*
     * The conversion itself, stated so the pins above cannot pass on a ratio of 1.
     * Measured on the renderer's own broadband captures with the instrument's
     * recovery of a known law beside it: 1.38 at dpr 1 and 1.49 at dpr 2, flat in
     * the span at each scale and interpolated between them exactly as every other
     * per-scale constant in this material is. 1.485 rather than 1.49 because that
     * is the least-squares fit over the five 2x cells, and the three different
     * nominals among them are what make the ratio distinguishable from a width
     * offset at all.
     */
    expect(scatterHeavyEffectiveRatioAtScale(1)).toBeCloseTo(1.38, 12);
    expect(scatterHeavyEffectiveRatioAtScale(2)).toBeCloseTo(1.485, 12);
    expect(scatterHeavyEffectiveRatioAtScale(1.5)).toBeCloseTo(1.4325, 12);
    expect(scatterHeavyEffectiveRatioAtScale(3)).toBeCloseTo(1.485, 12);
    // And it really reaches the width the tier writes: the 1x heavy component is
    // the profile's 10 device px carried to 13.8 by the conversion.
    expect(cssTierHeavySigmaCssPx(1.25, 96, MATERIAL_SOURCE_SIZE, 1)).toBeCloseTo(13.8, 12);
  });

  it("resolves one span to the same thickness, scatter and occlusion on both tiers", () => {
    const patch = { sizeSpanMin: 40, sizeSpanMax: 200, sizeScatterGainMax: 2.5, sizeOcclusionGain: 0.4 };
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const mirrored = sourceSize(patch);
    for (const span of [0, 40, 44, 96, 120, 200, 400]) {
      expect(cssSizeThickness(span, mirrored), `span ${span}`).toBeCloseTo(
        rendererSizeThickness(span, profile),
        12,
      );
      expect(cssSizeScatterSigma(8, span, mirrored), `span ${span}`).toBeCloseTo(
        rendererSizeScatterSigma(8, span, profile),
        12,
      );
      expect(cssSizeOcclusionAlpha(0.5, span, mirrored), `span ${span}`).toBeCloseTo(
        rendererSizeOcclusionAlpha(0.5, span, profile),
        12,
      );
    }
  });

  /*
   * The fold has to be one fold. Both tiers weaken the size law under a
   * preference through the refraction ladder, and the ladder is patchable — so a
   * profile that moved `refractionScale.approximate` and only one tier followed
   * would put a demoted platter at a different thickness from the one the GPU
   * tier had been drawing, which is K5's defect on this axis.
   */
  it("folds the size law under a preference identically on both tiers", () => {
    const patch = {
      sizeSpanMin: 40,
      sizeSpanMax: 200,
      sizeScatterGainMax: 2.5,
      refractionScale: { approximate: 0.3 },
    };
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const mirrored = sourceSize(patch);
    expect(mirrored.refractionScale.approximate).toBe(profile.refractionScale.approximate);

    const cases = [
      ["nominal", "nominal"],
      ["reduced", "reduced"],
      ["none", "none"],
    ] as const;
    for (const [cssRefraction, rendererRefraction] of cases) {
      for (const span of [0, 40, 96, 400]) {
        const css = cssSizeThicknessUnderPolicy(
          span,
          { ...NOMINAL_ACCESSIBILITY_POLICY.material, refraction: cssRefraction },
          mirrored,
        );
        const renderer = rendererSizeThicknessUnderPolicy(
          span,
          { ...RENDERER_NOMINAL_POLICY, refraction: rendererRefraction },
          profile,
        );
        expect(css, `${cssRefraction} at span ${span}`).toBeCloseTo(renderer, 12);
      }
    }
    // And the patched rung really is what both used, so neither equality above is
    // two defaults agreeing.
    expect(
      cssSizeThicknessUnderPolicy(
        400,
        { ...NOMINAL_ACCESSIBILITY_POLICY.material, refraction: "reduced" },
        mirrored,
      ),
    ).toBeCloseTo(0.3, 12);
  });

  /*
   * The scattering facet's own S1 consequence: a wider blur needs a wider proxy.
   * The CSS tier writes `blur(σ)` per surface and core's `samplingPadding` floor
   * is 3σ, so a group whose largest member scatters at the gain must pad for that
   * σ and not for the nominal. This pins the arithmetic the root applies.
   */
  it("keeps the 3σ padding floor over the σ a large surface will really use", () => {
    // The ramp turned off at the contour, so the mix is fully heavy at every
    // depth and the platter's σ is exactly the gain times the nominal — the
    // arithmetic under test here is the padding's, not the ramp's.
    const patch = {
      sizeSpanMin: 40,
      sizeSpanMax: 200,
      sizeScatterGainMax: 2.5,
      sizeScatterFloor: 0,
      sizeScatterRampStartThin1x: 0,
      sizeScatterRampStartThick1x: 0,
      sizeScatterRampStartThin2x: 0,
      sizeScatterRampStartThick2x: 0,
      sizeScatterRampStartFar1x: 0,
      sizeScatterRampStartFar2x: 0,
    };
    const mirrored = sourceSize(patch);
    const nominal = cssTierOptics(patch).regular.blurRadius;
    const platter = cssSizeScatterSigma(nominal, 400, mirrored);
    expect(platter).toBeCloseTo(nominal * 2.5, 12);
    expect(requiredSamplingPadding(platter)).toBeCloseTo(3 * platter, 12);
    expect(requiredSamplingPadding(platter)).toBeGreaterThan(requiredSamplingPadding(nominal));
    // On the shipped profile the floor is on and the ramp rides the span curve
    // above it. σ at the FOLD ANCHOR is 1.25 · (1 + 7 · floor) = 4.75, and the
    // smallest span's projection sits UNDER that rather than over it — 3.77 at
    // span 32 since W13 G1's third form raised the thin start to 0.72: the ramp
    // lifts the sharp share near the contour well above 1 − floor, which is the
    // band being sharper than the frost. So the floor is the fold's anchor and
    // not a pointwise minimum on the mix, and what the padding rule needs is only
    // that it is taken over the σ that will really be drawn — above the nominal
    // σ's 3.75 at every span, and growing with the span.
    const shipped = cssTierOptics().regular.blurRadius;
    expect(shipped).toBe(1.25);
    expect(cssSizeScatterSigmaAt(shipped, MATERIAL_SOURCE_SIZE.sizeScatterFloor)).toBeCloseTo(
      4.75,
      12,
    );
    expect(cssSizeScatterSigma(shipped, 32)).toBeGreaterThan(3.7);
    expect(cssSizeScatterSigma(shipped, 32)).toBeLessThan(4.75);
    expect(requiredSamplingPadding(cssSizeScatterSigma(shipped, 32))).toBeGreaterThan(11);
    expect(requiredSamplingPadding(cssSizeScatterSigma(shipped, 160))).toBeGreaterThan(
      requiredSamplingPadding(cssSizeScatterSigma(shipped, 32)),
    );
  });

  it("follows a profile patch on both sides at once", () => {
    // The property the gap was the absence of: one document, both tiers. The
    // dark profile is the real case — nothing in the runtime selects it yet
    // (C9a §4.3), so a host passing it must reach the CSS tier too.
    const patch = { optics: { regular: { tint: [0.05, 0.05, 0.05] as const, tintAlpha: 0.97 } } };
    const gpu = DEFAULT_MATERIAL_PROFILE.optics.regular;
    const css = cssTierOptics(patch).regular;

    expect(css.tintAlpha).toBeGreaterThan(cssTierOptics().regular.tintAlpha);
    expect(css.tint).not.toEqual(cssTierOptics().regular.tint);
    // And the renderer's own default is untouched by having been read.
    expect(DEFAULT_MATERIAL_PROFILE.optics.regular).toEqual(gpu);
  });

  /**
   * The author tint's shade law (W10) — the slice most exposed to drift,
   * because the law deliberately exists twice: once in the shader, evaluated
   * per pixel against the material it has just composited, and once on the
   * CPU, where the CSS tier's single colour and both tiers' ink decisions are
   * taken against it. A mirror that moved on one side would decide the ink
   * against a material nobody draws — Decision Log #32(b)'s failure, arriving
   * through a different door.
   */
  it("mirrors the renderer's tint shade constants, patch included", () => {
    expect(TINT_SHADE.dark).toBe(DEFAULT_MATERIAL_PROFILE.tintShadeDark);
    expect(TINT_SHADE.light).toBe(DEFAULT_MATERIAL_PROFILE.tintShadeLight);
    expect(TINT_SHADE.strength).toBe(DEFAULT_MATERIAL_PROFILE.tintShadeStrength);
    expect(TINT_SHADE.reducedAdaptation).toBe(DEFAULT_MATERIAL_PROFILE.reducedTintAdaptation);

    const patch = {
      tintShadeDark: 0.2,
      tintShadeLight: 0.8,
      tintShadeStrength: 0.5,
      reducedTintAdaptation: 0.6,
    };
    const rendered = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const mirrored = resolvedTintShade(patch);
    expect(mirrored.dark).toBe(rendered.tintShadeDark);
    expect(mirrored.light).toBe(rendered.tintShadeLight);
    expect(mirrored.strength).toBe(rendered.tintShadeStrength);
    expect(mirrored.reducedAdaptation).toBe(rendered.reducedTintAdaptation);
  });

  it("paints the same shaded layer on both sides, at both ends and in between", () => {
    const seed = [0.8, 0.2, 0.05] as const;
    for (const material of [0, 0.02, 0.2, 0.5, 0.9, 1]) {
      for (const grip of [0, 0.35, 1]) {
        const renderer = rendererTintShadeLayer(seed, material, grip);
        const mirror = cssTierTintShadeLayer(seed, material, grip);
        for (const index of [0, 1, 2] as const) {
          expect(mirror[index], `material ${material} grip ${grip}`).toBeCloseTo(renderer[index], 12);
        }
      }
    }
  });

  it("reads the accessibility regime the same way on both sides", () => {
    for (const ambientTint of ["nominal", "reduced", "none"] as const) {
      expect(cssTierTintToneAdaptation(ambientTint)).toBe(
        rendererTintToneAdaptation({
          glass: "material",
          frost: "nominal",
          refraction: "nominal",
          occlusion: "nominal",
          border: "nominal",
          ambientTint,
          foreground: "adaptive",
        }),
      );
    }
  });

  /*
   * ## Backdrop tone adaptation (W7)
   *
   * This axis is the one where a mirror drift is not a shade of difference but a
   * different picture: at full strength it replaces the material's colour with
   * the backdrop's own, so two tiers disagreeing about *how much* or *onto what*
   * draw two different surfaces. That is not hypothetical — it is what the
   * coherence gate caught while the axis was being fitted, at an interior level
   * ratio of 79 against a band of 0.80…1.25, and it is why the tone itself is
   * resolved once per group by the host and handed to both tiers rather than
   * sampled independently on each.
   */
  it("mirrors the renderer's backdrop-tone constants, patch included", () => {
    expect(BACKDROP_TONE.max).toBe(DEFAULT_MATERIAL_PROFILE.backdropToneMax);
    expect(BACKDROP_TONE.low).toBe(DEFAULT_MATERIAL_PROFILE.backdropToneLow);
    expect(BACKDROP_TONE.high).toBe(DEFAULT_MATERIAL_PROFILE.backdropToneHigh);
    expect(BACKDROP_TONE.sizeBias).toBe(DEFAULT_MATERIAL_PROFILE.backdropToneSizeBias);

    const patch = {
      backdropToneMax: 0.7,
      backdropToneLow: 0.05,
      backdropToneHigh: 0.3,
      backdropToneSizeBias: 0.2,
    };
    const rendered = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const mirrored = resolvedBackdropTone(patch);
    expect(mirrored.max).toBe(rendered.backdropToneMax);
    expect(mirrored.low).toBe(rendered.backdropToneLow);
    expect(mirrored.high).toBe(rendered.backdropToneHigh);
    expect(mirrored.sizeBias).toBe(rendered.backdropToneSizeBias);
    expect(mirrored.high).not.toBe(BACKDROP_TONE.high);
  });

  it("evaluates the same adaptation curve on both sides, at every span and every level", () => {
    const patch = { backdropToneLow: 0.05, backdropToneHigh: 0.3, backdropToneSizeBias: 0.2 };
    const rendered = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const mirrored = resolvedBackdropTone(patch);
    for (const profilePair of [
      [DEFAULT_MATERIAL_PROFILE, BACKDROP_TONE] as const,
      [rendered, mirrored] as const,
    ]) {
      const [rendererProfile, cssTone] = profilePair;
      for (const backdrop of [0, 0.004, 0.0117, 0.05, 0.1, 0.2, 0.5, 0.891, 1]) {
        for (const thickness of [0, 0.0923, 0.25, 0.5, 1]) {
          expect(
            cssBackdropToneAdaptation(backdrop, thickness, cssTone),
            `backdrop ${backdrop} thickness ${thickness}`,
          ).toBeCloseTo(
            rendererBackdropToneAdaptation(backdrop, thickness, rendererProfile),
            12,
          );
        }
      }
    }
  });

  it("folds the adaptation under a preference identically on both tiers", () => {
    // Two folds, both patchable: `ambientTint` for the contrast regimes and the
    // refraction ladder at the accessibility cap for reduced transparency. A
    // profile that moved either and only one tier followed would put a demoted
    // surface at a different adaptation from the one the GPU tier was drawing.
    const patch = { reducedTintAdaptation: 0.6, refractionScale: { approximate: 0.3 } };
    const rendered = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const preferences = (
      flags: Partial<Record<"reducedTransparency" | "increasedContrast" | "forcedColors", boolean>>,
    ) => ({
      reducedTransparency: false,
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: false,
      reducedTransparencySupported: true,
      ...flags,
    });
    for (const flags of [
      {},
      { reducedTransparency: true },
      { increasedContrast: true },
      { reducedTransparency: true, increasedContrast: true },
      { forcedColors: true },
    ]) {
      const policy = resolveAccessibilityPolicy(preferences(flags)).material;
      expect(
        cssBackdropToneUnderPolicy(
          policy,
          resolvedTintShade(patch),
          sourceSize(patch).refractionScale,
        ),
        JSON.stringify(flags),
      ).toBeCloseTo(rendererBackdropToneUnderPolicy(policy, rendered), 12);
    }
  });

  it("adapts one material onto one backdrop to the same colour and alpha on both tiers", () => {
    const backdrop = [0.02, 0.013, 0.03] as const;
    for (const adaptation of [0, 0.1, 0.256, 0.5, 0.9, 1]) {
      const source = sourceOptics()["regular"];
      const css = adaptedSourceOptics(source, backdrop, adaptation);
      const rendererColour = adaptedTintColour(
        DEFAULT_MATERIAL_PROFILE.optics.regular.tint,
        backdrop,
        adaptation,
        DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha,
      );
      expect(css.tintAlpha, `adaptation ${adaptation}`).toBeCloseTo(
        adaptedTintAlpha(DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha, adaptation),
        12,
      );
      for (const index of [0, 1, 2] as const) {
        expect(css.tint[index], `adaptation ${adaptation} channel ${index}`).toBeCloseTo(
          rendererColour[index] as number,
          12,
        );
      }
    }
  });

  it("converges the interior on the backdrop's tone — the property the pair exists for", () => {
    // Both tiers state the adaptation as a (colour, alpha) pair, and the pair is
    // only right if the composite it produces is the interior lerped toward the
    // backdrop's tone. Checked here rather than in either package because it is
    // the equation the two mirrors have to agree on, not a fact about one of them.
    const tone = [0.02, 0.013, 0.03] as const;
    const nominal = DEFAULT_MATERIAL_PROFILE.optics.regular;
    const sharpBackdrop = [0.5, 0.5, 0.5] as const;
    for (const adaptation of [0, 0.25, 0.5, 1]) {
      const alpha = adaptedTintAlpha(nominal.tintAlpha, adaptation);
      const colour = adaptedTintColour(nominal.tint, tone, adaptation, nominal.tintAlpha);
      for (const index of [0, 1, 2] as const) {
        const unadapted =
          sharpBackdrop[index] * (1 - nominal.tintAlpha) + nominal.tint[index] * nominal.tintAlpha;
        const expected = unadapted + (tone[index] - unadapted) * adaptation;
        const actual = sharpBackdrop[index] * (1 - alpha) + (colour[index] as number) * alpha;
        expect(actual, `adaptation ${adaptation} channel ${index}`).toBeCloseTo(expected, 12);
      }
    }
  });

  /*
   * The outer shadow (W8), and this is the mirror with the most riding on it.
   *
   * Every other facet here has the two tiers approximating one another — a
   * `backdrop-filter` is not a lens, a `border` is not a rim band. The shadow is
   * the one facet where both tiers do literally the same thing: composite a pure
   * black layer at one alpha over whatever is behind, which is a multiplicative
   * occlusion by compositing algebra alone. So they can be held to the same
   * numbers AND the same result, and the only stated residual is the blur kernel
   * (a browser approximates the Gaussian; the shader evaluates it).
   */
  it("mirrors the renderer's outer-shadow constants, patch included", () => {
    const renderer = DEFAULT_MATERIAL_PROFILE.outerShadow;
    expect(MATERIAL_SOURCE_OUTER_SHADOW.offsetPx).toBe(renderer.offsetPx);
    expect(MATERIAL_SOURCE_OUTER_SHADOW.sigmaPx).toBe(renderer.sigmaPx);
    expect(MATERIAL_SOURCE_OUTER_SHADOW.spreadPx).toBe(renderer.spreadPx);
    // W14 G1's ten: six amplitude anchors on two regimes and the lift's four.
    for (const key of [
      "thinOcclusionDark",
      "thinOcclusionMid",
      "thinOcclusionBright",
      "thickOcclusionAt96",
      "thickOcclusionAt128",
      "thickOcclusionAt160",
      "liftAmplitude",
      "liftSpanMin",
      "liftSpanFull",
      "liftBlurSigmaCss",
    ] as const) {
      expect(MATERIAL_SOURCE_OUTER_SHADOW[key], key).toBe(renderer[key]);
    }
    expect(MATERIAL_SOURCE_OUTER_SHADOW.reducedTransparencyOcclusion).toBe(
      renderer.reducedTransparencyOcclusion,
    );
    expect(MATERIAL_SOURCE_OUTER_SHADOW.sizeGain).toBe(renderer.sizeGain);
    // The anchors' own axis is mirrored too — a tier reading the plateau at a
    // different luminance would be a second luminance statistic by the back
    // door, which is exactly what the charter's third binding rule forbids.
    expect(CSS_OUTER_SHADOW_THIN_L).toEqual(RENDERER_OUTER_SHADOW_THIN_L);
    expect(CSS_OUTER_SHADOW_THICK_SPANS).toEqual(RENDERER_OUTER_SHADOW_THICK_SPANS);
    expect(CSS_UNMEASURED_BACKDROP).toBe(RENDERER_UNMEASURED_BACKDROP);
    // Field for field, so a constant the renderer grows cannot sit unmirrored.
    expect(Object.keys(MATERIAL_SOURCE_OUTER_SHADOW).sort()).toEqual(Object.keys(renderer).sort());

    const patch = {
      outerShadow: {
        offsetPx: 12,
        sigmaPx: 30,
        spreadPx: -2,
        thinOcclusionDark: 0.01,
        thinOcclusionMid: 0.5,
        thinOcclusionBright: 0.2,
        thickOcclusionAt96: 0.55,
        thickOcclusionAt128: 0.6,
        thickOcclusionAt160: 0.65,
        liftAmplitude: 0.02,
        liftSpanMin: 48,
        liftSpanFull: 144,
        liftBlurSigmaCss: 32,
        reducedTransparencyOcclusion: 0.25,
        sizeGain: 0.4,
      },
    };
    const rendered = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch).outerShadow;
    const mirrored = sourceOuterShadow(patch);
    expect(mirrored).toEqual({ ...rendered });
    expect(mirrored.sigmaPx).not.toBe(MATERIAL_SOURCE_OUTER_SHADOW.sigmaPx);

    // And a PARTIAL patch merges the same way on both sides — one named constant
    // keeps the other five, which is what makes a one-constant calibration patch
    // legal rather than a silent five-constant reset.
    const partial = { outerShadow: { thinOcclusionMid: 0.2 } };
    expect(sourceOuterShadow(partial)).toEqual({
      ...withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, partial).outerShadow,
    });
  });

  it("evaluates one falloff and one alpha conversion on both sides", () => {
    for (const sigma of [1, 8, 15.55, 31.1]) {
      for (const d of [-60, -31.1, -8, -1, 0, 1, 8, 31.1, 60]) {
        expect(cssOuterShadowFalloff(d, sigma), `sigma ${sigma} at ${d}`).toBe(
          rendererOuterShadowFalloff(d, sigma),
        );
      }
    }
    for (const occlusion of [0, 0.06, 0.18, 0.33, 0.5, 1]) {
      expect(cssOuterShadowAlpha(occlusion), `occlusion ${occlusion}`).toBe(
        rendererOuterShadowAlpha(occlusion),
      );
    }
  });

  it("folds the shadow under a preference identically on both tiers, patch included", () => {
    /*
     * The fold is a FLATTENING since W14 G1: under the preference the reference's
     * exterior is one level, thin and thick together and over every backdrop
     * (claims §5.62 §5), so both tiers write `reducedTransparencyOcclusion` into
     * all six anchors and stand the lift down. Two tiers that scaled instead
     * would still agree with each other and both be wrong, so the level is
     * asserted here beside the agreement.
     */
    const patch = { outerShadow: { thinOcclusionMid: 0.4, reducedTransparencyOcclusion: 0.3 } };
    for (const pair of [
      [DEFAULT_MATERIAL_PROFILE, MATERIAL_SOURCE_OUTER_SHADOW] as const,
      [withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch), sourceOuterShadow(patch)] as const,
    ]) {
      const [rendererProfile, cssShadow] = pair;
      for (const flags of [
        {},
        { reducedTransparency: true },
        { increasedContrast: true },
        { reducedTransparency: true, increasedContrast: true },
        { forcedColors: true },
      ]) {
        const resolved = resolveAccessibilityPolicy({
          reducedTransparency: false,
          reducedMotion: false,
          increasedContrast: false,
          forcedColors: false,
          reducedTransparencySupported: true,
          ...flags,
        });
        const css = cssOuterShadowUnderPolicy(cssShadow, resolved.material);
        const gpu = rendererOuterShadowUnderPolicy(resolved.material, rendererProfile);
        for (const key of [...AMPLITUDE_ANCHORS, "liftAmplitude"] as const) {
          expect(css[key], `${JSON.stringify(flags)} / ${key}`).toBe(gpu[key]);
        }
        expect(css.sigmaPx).toBe(gpu.sigmaPx);
        expect(css.offsetPx).toBe(gpu.offsetPx);
        expect(css.spreadPx).toBe(gpu.spreadPx);

        if (resolved.material.frost === "increased") {
          // One level in place of both regimes, on both tiers.
          for (const key of AMPLITUDE_ANCHORS) {
            expect(css[key], `${JSON.stringify(flags)} / ${key}`).toBe(
              cssShadow.reducedTransparencyOcclusion,
            );
          }
          expect(css.liftAmplitude).toBe(0);
        }
      }
    }
  });

  it("resolves one span to the same shadow amplitude on both tiers", () => {
    const patch = { outerShadow: { sizeGain: 0.5 } };
    const rendererProfile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const cssShadow = sourceOuterShadow(patch);
    for (const span of [0, 24, 32, 44, 64, 96, 160, 4000]) {
      const thickness = cssSizeThickness(span, MATERIAL_SOURCE_SIZE);
      expect(rendererSizeThickness(span), `span ${span}`).toBe(thickness);
      expect(cssSizeOuterShadowOcclusionAt(0.33, thickness, cssShadow), `span ${span}`).toBe(
        rendererSizeOuterShadowOcclusionAt(0.33, thickness, rendererProfile),
      );
    }
  });

  it("composites one backdrop to the same pixel on both tiers, and to black over black", () => {
    /*
     * The result, not just the constants — and in the space both tiers actually
     * composite in, which is encoded sRGB on each: a `box-shadow` under the
     * page's compositor, and a premultiplied canvas under the same one.
     *
     * The zero-over-black property is the reference's own signature — its
     * `dark-solid` cells are byte-identical to their background — and here it is
     * a consequence of the shadow's colour rather than a case either tier
     * handles.
     */
    const shadow = cssOuterShadowUnderPolicy(
      MATERIAL_SOURCE_OUTER_SHADOW,
      NOMINAL_ACCESSIBILITY_POLICY.material,
    );
    const alpha = cssOuterShadowAlpha(cssOuterShadowThinOcclusion(0.5, shadow));
    expect(alpha).toBe(
      rendererOuterShadowAlpha(
        rendererOuterShadowThinOcclusion(0.5, DEFAULT_MATERIAL_PROFILE.outerShadow),
      ),
    );

    for (const linear of [0, 0.0117, 0.2141, 0.5, 0.891, 1]) {
      const encoded = srgbEncode(linear);
      // The CSS tier: `box-shadow` of rgba(0,0,0,alpha), source-over.
      const css = encoded * (1 - alpha) + 0 * alpha;
      // The GPU tier: premultiplied (0,0,0,alpha) over the page, same algebra.
      const gpu = 0 + encoded * (1 - alpha);
      expect(css, `backdrop ${linear}`).toBeCloseTo(gpu, 15);
    }
    expect(srgbEncode(0) * (1 - alpha)).toBe(0);
  });

  /*
   * W14 G1's amplitude law, pinned across the whole grid it can be asked for
   * (claims §5.62). The two tiers now resolve a law rather than read a constant,
   * and the law has three inputs: the backdrop luminance the thin regime keys on
   * — the SAME statistic W9's face response uses, which is the charter's third
   * binding rule and the reason no second reading appears on either side — the
   * casting span the thick regime is a function of, and the accessibility fold.
   * A grid over all three is what makes "one profile, two renderers" a
   * measurement rather than a claim.
   */
  it("resolves one backdrop, span and fold to the same shadow amplitude on both tiers", () => {
    const luminances = [0.004, 0.012, 0.06, 0.214, 0.5, 0.74, 0.891, 1.0];
    const spans = [32, 44, 64, 96, 128, 160, 256];
    const folds = [0, 0.5, 1];
    // A patch on both sides, so the grid measures the law and not the shipped
    // numbers: a hard-coded default agreeing with itself would prove nothing.
    const patch = {
      outerShadow: {
        thinOcclusionDark: 0.02,
        thinOcclusionMid: 0.41,
        thinOcclusionBright: 0.09,
        thickOcclusionAt96: 0.44,
        thickOcclusionAt128: 0.52,
        thickOcclusionAt160: 0.61,
        sizeGain: 0.3,
      },
    };
    for (const [rendererProfile, cssShadow] of [
      [DEFAULT_MATERIAL_PROFILE, MATERIAL_SOURCE_OUTER_SHADOW] as const,
      [withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch), sourceOuterShadow(patch)] as const,
    ]) {
      for (const luminance of luminances) {
        for (const span of spans) {
          for (const fold of folds) {
            const thickness = rendererSizeThickness(span, rendererProfile) * fold;
            const label = `L ${luminance} span ${span} fold ${fold}`;
            expect(cssOuterShadowThinOcclusion(luminance, cssShadow), label).toBe(
              rendererOuterShadowThinOcclusion(luminance, rendererProfile.outerShadow),
            );
            expect(cssOuterShadowThickOcclusion(span, cssShadow), label).toBe(
              rendererOuterShadowThickOcclusion(span, rendererProfile.outerShadow),
            );
            const css = cssOuterShadowOcclusionAt(cssShadow, luminance, span, thickness);
            const gpu = rendererOuterShadowOcclusionAt(
              rendererProfile.outerShadow,
              luminance,
              span,
              thickness,
              rendererProfile,
            );
            expect(css, label).toBe(gpu);
            // And the alpha both tiers actually composite with, which is where a
            // space mismatch would show even if the occlusions agreed.
            expect(cssOuterShadowAlpha(css), label).toBe(rendererOuterShadowAlpha(gpu));
          }
        }
      }
      // The unmeasured-backdrop fallback is the same on both, so an unsampled
      // group does not split the tiers either.
      expect(cssOuterShadowThinOcclusion(undefined, cssShadow)).toBe(
        rendererOuterShadowThinOcclusion(undefined, rendererProfile.outerShadow),
      );
    }
  });

  /*
   * The thick regime, where the two tiers paint a DIFFERENT number of terms and
   * are still one profile (claims §5.65 §2 and §6(ii)).
   *
   * Above the knee the GPU tier composites two terms — the black multiply and the
   * lift, a blurred copy of the backdrop's own light — and the CSS tier can paint
   * only the first, because a `box-shadow` cannot reach the backdrop outside the
   * element it is on (W14 Decision Log 4, user). The anchors were fitted on the
   * tier that has a lift, so the CSS tier must not inherit them: it derives its
   * own multiply by matching the composite at the backdrop level it already
   * reads. This case pins that derivation as a RELATION rather than restating the
   * arithmetic — it computes what the other tier composites, from the renderer's
   * own constants, and requires the CSS tier's single multiply to land on it.
   *
   * The test's own encode is sRGB's, restated here for the reason both tiers
   * restate it: a spec constant is not a tunable, and importing one tier's copy
   * would make the assertion circular.
   *
   * **Kept at W16 G1, and now permanent rather than provisional.** W14 Decision
   * Log 4 deferred the lift to the wave that would decide the CSS tier's element
   * model, and W16 decided it: the lift is not drawn, because no CSS construction
   * adds a filtered backdrop's light to a ring and keeps the backdrop. A blend
   * mode does not reach a `backdrop-filter`'s output — it blends the element's
   * own content, and an empty ring has none — and a blending ancestor is a
   * backdrop root, so the only remaining expression needs a COPY of the backdrop,
   * which is a proxy and the one thing this tier does not build (claims §5.71 §6,
   * W16 Decision Log 2 (d)). So this fold is the CSS tier's answer for good, and
   * this case is the pin that keeps the two tiers on one profile while they paint
   * a different number of terms.
   */
  it("folds the lift the CSS tier cannot paint into the one alpha it can", () => {
    const encode = (linear: number): number => {
      const clamped = Math.min(1, Math.max(0, linear));
      return clamped <= 0.0031308 ? clamped * 12.92 : 1.055 * Math.pow(clamped, 1 / 2.4) - 0.055;
    };
    const luminances = [0.004, 0.012, 0.06, 0.214, 0.5, 0.74, 0.891, 1.0];
    const spans = [32, 44, 64, 96, 118, 128, 160, 256];
    const folds = [0, 0.5, 1];
    // A patch with a lift far larger than the shipped one, so the grid crosses
    // the clamp as well as the ordinary regime: at 0.5 of the backdrop's light
    // the fold asks for more than the black term has to give.
    const patch = {
      outerShadow: {
        thinOcclusionMid: 0.41,
        thickOcclusionAt96: 0.44,
        thickOcclusionAt128: 0.52,
        thickOcclusionAt160: 0.61,
        liftAmplitude: 0.5,
        liftSpanFull: 144,
      },
    };
    for (const [rendererProfile, cssShadow] of [
      [DEFAULT_MATERIAL_PROFILE, MATERIAL_SOURCE_OUTER_SHADOW] as const,
      [withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch), sourceOuterShadow(patch)] as const,
    ]) {
      const shadow = rendererProfile.outerShadow;
      for (const luminance of luminances) {
        for (const span of spans) {
          for (const fold of folds) {
            const thickness = rendererSizeThickness(span, rendererProfile) * fold;
            const label = `L ${luminance} span ${span} fold ${fold}`;
            // The rise is one law on both sides, so the CSS tier knows exactly
            // how much of the lift the other tier is putting on the pixel.
            expect(cssOuterShadowLiftRise(span, cssShadow), label).toBe(
              rendererOuterShadowLiftRise(span, shadow),
            );
            // What the GPU tier composites outside the coverage, at the falloff's
            // peak: 'B·(1 − α) + L', with the lift capped at the layer's own alpha
            // the way the shader caps it.
            const alpha = rendererOuterShadowAlpha(
              rendererOuterShadowOcclusionAt(shadow, luminance, span, thickness, rendererProfile),
            );
            const backdrop = encode(luminance);
            const lift = Math.min(
              encode(luminance * shadow.liftAmplitude * rendererOuterShadowLiftRise(span, shadow)),
              alpha,
            );
            const composite = backdrop * (1 - alpha) + lift;
            // And what the CSS tier composites with one multiply, which has to be
            // the same pixel wherever the multiply can reach it.
            const folded = cssTierShadowAlpha(cssShadow, luminance, span, thickness);
            const multiply = backdrop * (1 - folded);
            if (folded > 0) {
              expect(multiply, label).toBeCloseTo(composite, 12);
            } else {
              // Clamped: the lift adds back more light than the black term
              // removes, so the composite is BRIGHTER than the backdrop and no
              // multiply can reach it. The tier stops at no shadow at all rather
              // than going negative, which is as close as one multiply gets.
              expect(multiply, label).toBe(backdrop);
              expect(multiply, label).toBeLessThanOrEqual(composite + 1e-12);
            }
            // Where there is no lift there is no fold, and the two tiers are the
            // same number to the last bit: below the knee, and over a backdrop
            // black enough to have no light to copy.
            if (rendererOuterShadowLiftRise(span, shadow) === 0 || luminance === 0) {
              expect(folded, label).toBe(alpha);
            }
          }
        }
      }
    }
  });

});

/**
 * The interior composite, both tiers (X7, W17 G1; charter Decision Log 2 (b)–(c)).
 *
 * Every other block in this file pins a CONSTANT in both directions. That is
 * what let the ordering defect W17 G0 found live on the tier undetected: the two
 * mirrors agreed on the size law's occlusion gain, on the response curve's
 * anchors and on the collapse's constants, and disagreed about the order the
 * three are applied in — worth +0.015 to +0.027 of the CSS tier's interior level
 * (claims §5.74 §3). So this block pins the COMPOSITE, per backdrop level and
 * per device scale, which is the only statement that could have caught it.
 *
 * The renderer's side is restated from the shader's own sequence using the
 * renderer package's exported functions and constants — the response curve, its
 * authority, the size law's occlusion, the collapse's pair. It is a second copy
 * of the shader's equation on purpose, in the one place a second copy is the
 * instrument rather than the hazard: this test exists to fail when the tier's
 * mirror and the shader stop being the same arithmetic.
 */
describe("the interior composite (X7)", () => {
  const PROFILE = DEFAULT_MATERIAL_PROFILE;
  const luma = (rgb: readonly [number, number, number]): number =>
    0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
  const smoothstep = (edge0: number, edge1: number, x: number): number => {
    const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
    return t * t * (3 - 2 * t);
  };

  /** A backdrop sample at a declared linear level, with its encoded mean beside it. */
  const sampleAt = (
    linear: number,
  ): { rgb: [number, number, number]; luminance: number; linearLuminance: number } => ({
    rgb: [linear, linear, linear],
    // A flat patch's encoded mean decodes back to itself, which is the one
    // sample where the two spaces the tone carries coincide — deliberate, so
    // this pin is about the composite and not about how a checkerboard is read.
    luminance: linear,
    linearLuminance: linear,
  });

  /** The shader's own sequence, in TypeScript, from the renderer's own numbers. */
  function rendererComposite(
    spanPx: number,
    backdropLinear: number,
    policy = RENDERER_NOMINAL_POLICY,
  ): { alpha: number; tint: [number, number, number] } {
    const optics = rendererOpticsUnderPolicy(PROFILE.optics.regular, policy, PROFILE);
    const sizeK = rendererSizeThicknessUnderPolicy(spanPx, policy, PROFILE);
    const geometricK = rendererSizeThickness(spanPx, PROFILE);
    // `sizedAlpha` — before the solve, which is the whole of W17 G0's finding.
    const sizedAlpha = rendererSizeOcclusionAlphaAt(optics.tintAlpha, sizeK, PROFILE);
    const policyStrength = rendererBackdropToneUnderPolicy(policy, PROFILE);
    const toneAdapt =
      rendererBackdropToneAdaptation(backdropLinear, geometricK, PROFILE) * policyStrength;
    const gate =
      (policyStrength >= 0.999 ? 1 : 0) * Math.min(1, Math.max(0, PROFILE.backdropToneMax));
    const responseStrength = gate * PROFILE.backdropToneResponseStrength;

    let neutral: [number, number, number] = [...optics.tint] as [number, number, number];
    let solvedAlpha = sizedAlpha;
    if (responseStrength > 0 && sizedAlpha > 1e-3 && toneAdapt < 0.995) {
      const encodedInput = srgbEncode(backdropLinear);
      const authority = rendererBackdropToneSolveWeight(encodedInput, PROFILE) * responseStrength;
      if (authority > 0) {
        const response = rendererBackdropToneResponse(encodedInput, sizeK, PROFILE);
        const preCollapse = (response - toneAdapt * backdropLinear) / (1 - toneAdapt);
        const nominal = (1 - sizedAlpha) * backdropLinear + sizedAlpha * luma(neutral);
        const shift = ((preCollapse - nominal) / sizedAlpha) * authority;
        neutral = neutral.map((channel) => Math.min(1, Math.max(0, channel + shift))) as [
          number,
          number,
          number,
        ];
        const solvedLuma = luma(neutral);
        const achieved = (1 - sizedAlpha) * backdropLinear + sizedAlpha * solvedLuma;
        if (preCollapse > achieved + 1e-4 && solvedLuma > backdropLinear + 1e-3) {
          const target = Math.min(
            1,
            Math.max(sizedAlpha, (preCollapse - backdropLinear) / (solvedLuma - backdropLinear)),
          );
          solvedAlpha = sizedAlpha + (target - sizedAlpha) * authority;
        }
      }
    }
    void smoothstep;
    return {
      alpha: adaptedTintAlpha(solvedAlpha, toneAdapt),
      tint: adaptedTintColour(neutral, [backdropLinear, backdropLinear, backdropLinear], toneAdapt, solvedAlpha) as [
        number,
        number,
        number,
      ],
    };
  }

  /** The tier's side: `root.ts`'s chain, through `optics.ts`'s own functions. */
  function tierComposite(
    spanPx: number,
    backdropLinear: number,
    policy = NOMINAL_ACCESSIBILITY_POLICY.material,
  ): CssTierInterior {
    const base = sourceOptics()["regular"];
    const size = sourceSize();
    const sample = sampleAt(backdropLinear);
    const sizeK = cssSizeThicknessUnderPolicy(spanPx, policy, size);
    const geometricK = cssSizeThickness(spanPx, size);
    const occluded = {
      ...base,
      tintAlpha: cssSizeOcclusionAlphaAt(
        occlusionAlphaUnderPolicy(base.tintAlpha, policy.occlusion),
        sizeK,
        size,
      ),
    };
    const toneConstants = resolvedBackdropTone();
    const policyStrength = cssBackdropToneUnderPolicy(
      policy,
      resolvedTintShade(),
      size.refractionScale,
    );
    const adaptation =
      cssBackdropToneAdaptation(sample.luminance, geometricK, toneConstants) * policyStrength;
    const responded = toneRespondedSourceOptics(
      occluded,
      sample,
      sizeK,
      adaptation,
      (policyStrength >= 0.999 ? 1 : 0) * Math.min(1, Math.max(0, toneConstants.max)),
      resolvedBackdropToneResponse(),
    );
    const adapted = adaptedSourceOptics(responded, sample.rgb, adaptation);
    return {
      tintAlpha: adapted.tintAlpha,
      tint: [adapted.tint[0], adapted.tint[1], adapted.tint[2]],
      addedLight: 0,
    };
  }

  it("mirrors the band's and the inner shadow's own constants, patch included", () => {
    for (const variant of MATERIAL_VARIANTS) {
      const renderer = DEFAULT_MATERIAL_PROFILE.optics[variant];
      const mirror = sourceOptics()[variant];
      for (const key of ["rimWidth", "specularPower", "specularGain", "shadowDepth", "shadowAlpha"] as const) {
        expect(mirror[key], `${variant}.${key}`).toBe(renderer[key]);
      }
    }
    expect(sourceInteriorLight().lightDirection).toEqual(DEFAULT_MATERIAL_PROFILE.lightDirection);
    expect(sourceInteriorLight().shadowDepthGainMax).toBe(DEFAULT_MATERIAL_PROFILE.lensSizeGainMax);
    expect(sourceInteriorLight().shadowAmplitudeGainMax).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeShadowGainMax,
    );
    // And through a patch, by the renderer's own merge rule: a document that
    // moves the band moves this tier's derived light with it.
    const patch = {
      lightDirection: [0, -1] as const,
      lensSizeGainMax: 3.1,
      sizeShadowGainMax: 1.4,
      optics: { regular: { rimWidth: 2.5, specularGain: 0.7 } },
    };
    const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    expect(sourceInteriorLight(patch).lightDirection).toEqual(resolved.lightDirection);
    expect(sourceInteriorLight(patch).shadowDepthGainMax).toBe(resolved.lensSizeGainMax);
    expect(sourceInteriorLight(patch).shadowAmplitudeGainMax).toBe(resolved.sizeShadowGainMax);
    expect(sourceOptics(patch).regular.rimWidth).toBe(resolved.optics.regular.rimWidth);
    expect(sourceOptics(patch).regular.specularGain).toBe(resolved.optics.regular.specularGain);
  });

  it("resolves one span and one backdrop to the same composite on both tiers", () => {
    for (const spanPx of [44, 96, 128, 160]) {
      for (const backdrop of [0.05, 0.2, 0.5, 0.8]) {
        const renderer = rendererComposite(spanPx, backdrop);
        const tier = tierComposite(spanPx, backdrop);
        const where = `span ${spanPx} backdrop ${backdrop}`;
        expect(tier.tintAlpha, `${where} alpha`).toBeCloseTo(renderer.alpha, 12);
        for (const index of [0, 1, 2] as const) {
          expect(tier.tint[index], `${where} channel ${index}`).toBeCloseTo(
            renderer.tint[index],
            12,
          );
        }
      }
    }
  });

  it("draws the renderer's composite through the table, at every level and scale", () => {
    /*
     * What the form is FOR: the page's composite of L3's floor overlay over the
     * filter's remainder is the renderer's composite as a FUNCTION of the
     * backdrop, rather than at one declared level (W17 Decision Log 4 (a)). The
     * band's derived light rides on it and is a property of the surface's
     * geometry, so it is read at both scales through the same box in CSS px —
     * the size law is a CSS-px law and the derivation is one too.
     */
    const encode = (l: number): number =>
      l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;
    const floor = cssTierFloorAlpha(MATERIAL_OPTICS.regular);
    const floorEncoded = MATERIAL_OPTICS.regular.tint[1] / 255;
    for (const devicePixelRatio of [1, 2]) {
      for (const [spanPx, geometry] of [
        [96, { widthCssPx: 160, heightCssPx: 96, radiusCssPx: 20, thicknessCssPx: 8 }],
        [44, { widthCssPx: 120, heightCssPx: 44, radiusCssPx: 22, thicknessCssPx: 8 }],
      ] as const) {
        for (const backdrop of [0.05, 0.2, 0.5, 0.8]) {
          const renderer = rendererComposite(spanPx, backdrop);
          const keep = interiorShadowKeep(
            sourceOptics().regular,
            geometry,
            cssSizeThickness(spanPx, sourceSize()),
            1,
          );
          const band = interiorBandLight(sourceOptics().regular, geometry, 1);
          const tier = tierComposite(spanPx, backdrop);
          const shadowed = innerShadowedSourceOptics(
            { ...sourceOptics().regular, tintAlpha: tier.tintAlpha, tint: tier.tint },
            keep,
          );
          const table = cssTierTintTable({
            tintAlpha: shadowed.tintAlpha,
            tint: shadowed.tint[1],
            addedLight: band,
            floorAlpha: floor,
            floorEncoded,
          });
          const where = `dpr ${devicePixelRatio} span ${spanPx} backdrop ${backdrop}`;
          const expected =
            keep * ((1 - renderer.alpha) * backdrop + renderer.alpha * renderer.tint[1]) + band;
          const t = backdrop * (table.length - 1);
          const index = Math.min(table.length - 2, Math.floor(t));
          const drawn = table[index]! + (t - index) * (table[index + 1]! - table[index]!);
          expect(encode(drawn) * (1 - floor) + floorEncoded * floor, where).toBeCloseTo(
            encode(expected),
            3,
          );
        }
      }
    }
  });

  it("folds a preference into the same composite on both tiers", () => {
    for (const regime of ["increased", "opaque"] as const) {
      const rendererPolicy = { ...RENDERER_NOMINAL_POLICY, occlusion: regime };
      const tierPolicy = { ...NOMINAL_ACCESSIBILITY_POLICY.material, occlusion: regime };
      for (const backdrop of [0.05, 0.5, 0.8]) {
        const renderer = rendererComposite(96, backdrop, rendererPolicy);
        const tier = tierComposite(96, backdrop, tierPolicy);
        const where = `${regime} at ${backdrop}`;
        expect(tier.tintAlpha, `${where} alpha`).toBeCloseTo(renderer.alpha, 12);
        for (const index of [0, 1, 2] as const) {
          expect(tier.tint[index], `${where} channel ${index}`).toBeCloseTo(
            renderer.tint[index],
            12,
          );
        }
      }
    }
  });

  it("draws the renderer's tinted composite at every strength of the ladder (W19 X7)", () => {
    /*
     * The author tint on the `linear` form (W19; charter Decision Log 2 item 7,
     * claims §5.80 §7).
     *
     * The renderer's law is `tintedMaterialColour` — `D((1 − s)·E(material) +
     * s·E(layer))` per pixel — and the tier now composes to the same expression
     * at every strength rather than only at `s = 1`: the transfer table is solved
     * on the material's own overlay colour and L3 carries the author's layer
     * folded over that overlay, `α″ = 1 − (1 − s)(1 − α₃)` and `C″ = ((1 − s)·α₃·
     * E(T) + s·E(L))/α″`. This composes what the tier DECLARES — the table at the
     * cell's own backdrop, then L3 over it — and holds it to the renderer's
     * composite carried through that expression.
     *
     * **Stated against the tier's own `L`, deliberately.** `tintedMaterialColour`
     * reads the tint shade off the material's luminance PER PIXEL; `authorTintLayer`
     * reads it once per source, which is W10's known granularity and not this
     * wave's. On G0's analytic sweep the renderer's per-pixel shade sits
     * **0.0000 to +0.0084** above the tier's per-source one, rising with strength
     * and backdrop (claims §5.80 §8). Folding that difference into this pin would
     * be asserting the granularity rather than the fold, so the target carries the
     * tier's `L` and the renderer's own gap is recorded here in numbers.
     *
     * The tolerance is the chain's quantum: `C″` is written as a CSS colour and
     * rounds to `Rgb255`, worth 2.85e−3 of the identity (claims §5.80 §3), and the
     * table adds its own 1e−4 interpolation bound on top.
     */
    const encode = (l: number): number =>
      l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;
    const clamp01 = (v: number): number => Math.min(1, Math.max(0, v));
    const shade = resolvedTintShade();
    const size = sourceSize();
    const toneConstants = resolvedBackdropTone();
    const spanPx = 44;
    const geometry = { widthCssPx: 120, heightCssPx: 44, radiusCssPx: 22, thicknessCssPx: 8 };
    let worst = 0;
    for (const backdrop of [0.05, 0.2, 0.5, 0.8]) {
      const renderer = rendererComposite(spanPx, backdrop);
      const tier = tierComposite(spanPx, backdrop);
      const geometricK = cssSizeThickness(spanPx, size);
      const adaptation =
        cssBackdropToneAdaptation(backdrop, geometricK, toneConstants) *
        cssBackdropToneUnderPolicy(
          NOMINAL_ACCESSIBILITY_POLICY.material,
          shade,
          size.refractionScale,
        );
      const keep = interiorShadowKeep(sourceOptics().regular, geometry, geometricK, 1);
      const band = interiorBandLight(sourceOptics().regular, geometry, 1);
      const shadowed = innerShadowedSourceOptics(
        { ...sourceOptics().regular, tintAlpha: tier.tintAlpha, tint: tier.tint },
        keep,
      );
      const interior: CssTierInterior = {
        tintAlpha: shadowed.tintAlpha,
        tint: [shadowed.tint[0], shadowed.tint[1], shadowed.tint[2]],
        addedLight: band,
      };
      const untinted = cssOpticsFromSource(MATERIAL_OPTICS.regular, shadowed, CSS_TIER_MAPPING);
      const grip =
        cssTierTintToneAdaptation(NOMINAL_ACCESSIBILITY_POLICY.material.ambientTint, shade) *
        shade.strength *
        (1 - adaptation);
      for (const seed of [
        [255, 149, 0],
        [10, 132, 255],
      ] as const) {
        for (const strength of [0.1, 0.2, 0.35, 0.5, 0.75, 1.0]) {
          const tint = glassTint(
            [seed[0] / 255, seed[1] / 255, seed[2] / 255],
            strength,
          );
          const seedLinear = linearTint(tint);
          const author = authorTintLayer(shadowed, seedLinear, backdrop, grip, shade);
          if (author === undefined) throw new Error("X7: the author layer resolved to nothing");
          const render = cssTierDeclarations({
            radii: [22, 22, 22, 22],
            optics: tintedCssOptics(untinted, shadowed, seedLinear, backdrop, grip, shade),
            untintedOptics: untinted,
            tint,
            policy: NOMINAL_ACCESSIBILITY_POLICY,
            spanPx,
            extentsCssPx: [geometry.widthCssPx, geometry.heightCssPx],
            filterIdPrefix: "x7",
            engine: { referenceFilterInBackdrop: true, maskOnBackdropFilter: "yes" },
            interior,
            authorLayer: author,
            backdropLuminance: backdrop,
          });
          const where = `backdrop ${backdrop} seed ${seed.join("-")} strength ${strength}`;
          // No author layer moves the boundary: `cssTintFormAt` reads the
          // MATERIAL's composite level, which the tint does not touch.
          expect(render.body.tintForm, where).toBe("linear");
          const transfer = render.body.tintTransfer;
          const overlay = render.layers?.overlay["background-color"];
          if (transfer === undefined || overlay === undefined) {
            throw new Error(`X7: ${where} declared no transfer or no overlay`);
          }
          const parsed = /^rgba\((\d+), (\d+), (\d+), ([\d.]+)\)$/.exec(overlay);
          if (parsed === null) throw new Error(`X7: ${where} overlay is ${overlay}`);
          const alpha = Number(parsed[4]);
          expect(alpha, `${where} floor`).toBeGreaterThanOrEqual(cssTierFloorAlpha(untinted));
          for (const channel of [0, 1, 2] as const) {
            const values = cssTierTintTable({
              tintAlpha: transfer.tintAlpha,
              tint: transfer.tint[channel],
              addedLight: transfer.addedLight,
              floorAlpha: transfer.floorAlpha,
              floorEncoded: transfer.floorEncoded[channel],
            });
            const x = clamp01(backdrop) * (values.length - 1);
            const index = Math.min(Math.floor(x), values.length - 2);
            const table = values[index]! + (x - index) * (values[index + 1]! - values[index]!);
            const drawn =
              (1 - alpha) * encode(table) + alpha * (Number(parsed[channel + 1]) / 255);
            // The renderer's own composite for this channel, band and inner
            // shadow included — the same quantity the untinted clause above holds
            // the table to — carried through the renderer's strength law with the
            // tier's `L` in it.
            const material =
              keep *
                ((1 - renderer.alpha) * backdrop + renderer.alpha * renderer.tint[channel]) +
              band;
            const target =
              (1 - strength) * encode(clamp01(material)) +
              strength * (author.color[channel] / 255);
            expect(Math.abs(drawn - target), `${where} channel ${channel}`).toBeLessThan(0.004);
            worst = Math.max(worst, Math.abs(drawn - target));
          }
        }
      }
    }
    // The chain's own quantum is the floor under this clause and the reading is
    // recorded rather than only bounded.
    expect(worst).toBeLessThan(0.004);
  });
});

/**
 * The shadow's paint order, from the tier's own output (X7, restated by W18
 * Decision Log 2 (5); charter `2026-09-05-w18-union-contour-residual.md`).
 *
 * X7 was chartered as a pin on the tier's per-surface terms, on the belief that
 * the union-contour residual was a term this tier computes by the span where the
 * renderer integrates it over the box. G0 refuted that — declining all five of
 * those terms makes the residual worse, and the whole of the neighbours' share
 * belongs to a thing the tier PAINTS and then re-reads (claims §5.77 §3). So the
 * pin is the paint order instead, and it is asserted by construction rather than
 * by a capture: **no filter layer of a group may be painted after a shadow the
 * tier paints for that group.**
 *
 * The order this reads is CSS's own. Inside a stacking context — and each host is
 * one, because the tier writes `isolation: isolate` — the element's background
 * and border paint first, then its negative-`z` children in `z-index` order, then
 * its in-flow content. A sibling host's whole subtree paints before the next
 * host begins. Those two sentences are the whole of the derivation, and every
 * assertion below is one of them applied to the declarations the tier returns.
 */
describe("the outer shadow's paint order (X7)", () => {
  const policy = NOMINAL_ACCESSIBILITY_POLICY;
  const surfaceAt = (spanPx: number) => ({
    radii: [22, 22, 22, 22] as const,
    optics: MATERIAL_OPTICS.regular,
    policy,
    spanPx,
    extentsCssPx: [spanPx, spanPx] as const,
    devicePixelRatio: 1,
  });

  /** The `z-index` each of the tier's three layers declares, as numbers. */
  const layerDepths = (
    render: ReturnType<typeof cssTierDeclarations>,
  ): Record<CssTierLayer, number> => {
    const layers = render.layers;
    if (layers === undefined) throw new Error("the material branch draws three layers");
    return {
      sharp: Number(layers.sharp["z-index"]),
      heavy: Number(layers.heavy["z-index"]),
      overlay: Number(layers.overlay["z-index"]),
    };
  };

  it("paints a lone surface's shadow after both of its own filters", () => {
    const plan = planCssTierShadow([{ nodeId: "solo", clipsChildren: false }]);
    expect(plan.carrier).toBe("layer");

    const render = cssTierDeclarations({
      ...surfaceAt(44),
      shadowCarrier: plan.members[0]![1],
    });
    const depths = layerDepths(render);
    const layers = render.layers!;

    // The shadow is on the overlay and on nothing else, and the overlay is above
    // both filters — so the filters sample a page this shadow is not yet in.
    expect(render.host["box-shadow"]).toBe("none");
    expect(layers.overlay["box-shadow"]).toContain(render.outerShadow);
    expect(depths.overlay).toBeGreaterThan(depths.sharp);
    expect(depths.overlay).toBeGreaterThan(depths.heavy);
    expect(layers.sharp["backdrop-filter"]).toBeTruthy();
    expect(layers.heavy["backdrop-filter"]).toBeTruthy();
  });

  it("paints every member's shadow after every member's filters, in a group", () => {
    const members = ["a", "b", "c"].map((nodeId) => ({ nodeId, clipsChildren: false }));
    const plan = planCssTierShadow(members);
    expect(plan.carrier).toBe("group");
    // The container's host is the LAST member in document order, which is the
    // only element in the group painted after every member's subtree.
    expect(plan.groupHostNodeId).toBe("c");

    const renders = plan.members.map(([nodeId, carrier]) => ({
      nodeId,
      render: cssTierDeclarations({ ...surfaceAt(44), shadowCarrier: carrier }),
    }));
    // Not one member draws a shadow of its own: it would be sampled by every
    // LATER member's filters, which is the neighbours' term G0 measured at
    // −0.0058 on the three-up and +0.0005 with the shadow out.
    for (const { nodeId, render } of renders) {
      expect(render.host["box-shadow"], nodeId).toBe("none");
      expect(render.layers!.overlay["box-shadow"], nodeId).not.toContain("rgba(0, 0, 0,");
      expect(render.outerShadow, nodeId).toContain("rgba(0, 0, 0,");
    }

    const casts = renders.map(({ nodeId, render }, index) => ({
      nodeId,
      bounds: { x: 100 + index * 56, y: 200, width: 44, height: 44 },
      radii: [22, 22, 22, 22] as const,
      shadow: render.outerShadow,
    }));
    const container = cssTierGroupShadowDeclarations({
      hostBounds: casts[2]!.bounds,
      hostBorderWidthCssPx: MATERIAL_OPTICS.regular.borderWidth,
      casts,
      reachCssPx: 42.5,
    });

    // The container sits above the hosting member's own filters, so that host
    // does not sample it either; and it carries every member's own value.
    expect(Number(container.container["z-index"])).toBeGreaterThan(
      layerDepths(renders[2]!.render).heavy,
    );
    expect(container.casters.map((caster) => caster.nodeId)).toEqual(["a", "b", "c"]);
    for (const [index, caster] of container.casters.entries()) {
      expect(caster.style["box-shadow"]).toBe(renders[index]!.render.outerShadow);
    }

    // And no member's BODY is inside the shadow: the clip is even-odd with one
    // hole per member, which is the renderer's `lift · (1 − coverage)`.
    const clip = container.container["clip-path"] ?? "";
    expect(clip.startsWith("path(evenodd, ")).toBe(true);
    expect(clip.split("M ").length - 1).toBe(casts.length + 1);
  });

  it("bounds what a clipping host still samples, by G0 §6's closed form", () => {
    /*
     * The one place a shadow stays inside the tier's own sampled backdrop, and
     * the reason the closed form stays in `optics.ts` rather than being deleted
     * with the defect. A host whose `overflow` clips its children would crop a
     * shadow on L3 away entirely, so the shadow stays on the host and the page
     * its filters read is the page below multiplied by `1 − a·C` — the same form
     * that predicts the removal to 0.0014 on every surface with no close
     * neighbour and to 0.0004 on three at a non-merging gap (claims §5.77 §6).
     */
    const plan = planCssTierShadow([{ nodeId: "clipped", clipsChildren: true }]);
    expect(plan.carrier).toBe("host");
    const render = cssTierDeclarations({
      ...surfaceAt(44),
      shadowCarrier: plan.members[0]![1],
    });
    expect(render.host["box-shadow"]).toBe(render.outerShadow);

    const shadow = sourceOuterShadow();
    const alpha = cssTierShadowAlpha(shadow, 0.5, 44, 0);
    const factorAt = (signedDistanceToShadowBoxPx: number, insideCaster = false): number =>
      sampledOuterShadowFactor({ shadow, alpha, signedDistanceToShadowBoxPx, insideCaster });

    // Inside the casting host's own border box a `box-shadow` is not painted at
    // all, so the page is untouched there whatever the distance says.
    expect(factorAt(-10, true)).toBe(1);
    // Outside it the factor is a multiply that weakens with distance and is
    // exactly the Gaussian's integral the renderer's own falloff mirrors.
    expect(factorAt(0)).toBeCloseTo(1 - alpha * cssOuterShadowFalloff(0, shadow.sigmaPx), 12);
    expect(factorAt(0)).toBeLessThan(1);
    for (const distance of [0, 5, 10, 20, 40]) {
      expect(factorAt(distance)).toBeLessThanOrEqual(factorAt(distance + 5) + 1e-12);
    }
    // And it vanishes where the shadow does — a profile that declines the facet
    // leaves the sampled page exactly the page.
    expect(
      sampledOuterShadowFactor({
        shadow,
        alpha: 0,
        signedDistanceToShadowBoxPx: 0,
        insideCaster: false,
      }),
    ).toBe(1);
  });
});
