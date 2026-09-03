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

import { NOMINAL_ACCESSIBILITY_POLICY, resolveAccessibilityPolicy } from "@vitreajs/vitrea";
import {
  BACKDROP_TONE,
  CSS_TIER_MAPPING,
  FOREGROUND_INK,
  INCREASED_OCCLUSION_LIFT,
  adaptedSourceOptics,
  backdropToneAdaptation as cssBackdropToneAdaptation,
  backdropToneUnderPolicy as cssBackdropToneUnderPolicy,
  resolvedBackdropTone,
  MATERIAL_SOURCE_GLOW,
  MATERIAL_SOURCE_OPTICS,
  MATERIAL_SOURCE_OUTER_SHADOW,
  MATERIAL_SOURCE_SIZE,
  REDUCED_TRANSPARENCY_FROST,
  STRONG_BORDER,
  TINT_SHADE,
  cssTierForegroundLevel,
  cssTierOptics,
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
  scatterThickness as cssScatterThickness,
  sizeScatterSigma as cssSizeScatterSigma,
  sizeScatterSigmaAt as cssSizeScatterSigmaAt,
  sizeThickness as cssSizeThickness,
  sizeThicknessUnderPolicy as cssSizeThicknessUnderPolicy,
  sourceGlow,
  sourceOptics,
  unsampledMaterials,
  sourceSize,
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
    expect(MATERIAL_SOURCE_SIZE.sizeScatterSpanMax).toBe(
      DEFAULT_MATERIAL_PROFILE.sizeScatterSpanMax,
    );
    expect(MATERIAL_SOURCE_SIZE.sizeOcclusionGain).toBe(DEFAULT_MATERIAL_PROFILE.sizeOcclusionGain);

    const patch = {
      sizeSpanMin: 40,
      sizeSpanMax: 200,
      sizeScatterGainMax: 2.5,
      sizeScatterFloor: 0.25,
      sizeScatterSpanMax: 320,
      sizeOcclusionGain: 0.4,
    };
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    const mirrored = sourceSize(patch);
    expect(mirrored.sizeSpanMin).toBe(profile.sizeSpanMin);
    expect(mirrored.sizeSpanMax).toBe(profile.sizeSpanMax);
    expect(mirrored.sizeScatterGainMax).toBe(profile.sizeScatterGainMax);
    expect(mirrored.sizeScatterFloor).toBe(profile.sizeScatterFloor);
    expect(mirrored.sizeScatterSpanMax).toBe(profile.sizeScatterSpanMax);
    expect(mirrored.sizeOcclusionGain).toBe(profile.sizeOcclusionGain);
    // And the patch really moved them, so none of the equalities above is the
    // default agreeing with itself.
    expect(mirrored.sizeSpanMax).not.toBe(MATERIAL_SOURCE_SIZE.sizeSpanMax);
  });

  /*
   * The scatter facet's own curve (W11c, claims §5.41): a floor at any span and
   * a band top past the thickness curve's, folded on the rise and not on the
   * floor. One function shape on both tiers, pinned over spans and folds, on
   * the shipped profile AND on a patch — so a retune of the floor or the top
   * moves the CSS tier's `blur()` and the GPU tier's chain mix together.
   */
  it("mixes toward the heavy blur by the same scatter thickness on both tiers", () => {
    const patches = [
      undefined,
      { sizeSpanMin: 40, sizeSpanMax: 200, sizeScatterGainMax: 6, sizeScatterFloor: 0.25, sizeScatterSpanMax: 320 },
    ] as const;
    for (const patch of patches) {
      const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch ?? {});
      const mirrored = sourceSize(patch);
      for (const span of [24, 32, 44, 96, 128, 160, 256, 400]) {
        for (const fold of [0, 0.45, 1]) {
          const css = cssScatterThickness(span, fold, mirrored);
          const gpu = rendererScatterThickness(span, fold, profile);
          expect(css, `span ${span} fold ${fold}`).toBeCloseTo(gpu, 12);
          expect(cssSizeScatterSigmaAt(1.25, css, mirrored), `σ at span ${span} fold ${fold}`).toBeCloseTo(
            rendererSizeScatterSigmaAt(1.25, gpu, profile),
            12,
          );
        }
        // The floor is unfolded on both tiers: fold 0 leaves it, and only it.
        expect(cssScatterThickness(span, 0, mirrored)).toBeCloseTo(mirrored.sizeScatterFloor, 12);
      }
    }
    // The shipped numbers, stated: the floor's σ and the platter's.
    expect(cssSizeScatterSigma(1.25, 32)).toBeCloseTo(1.25 * (1 + 7 * 0.4), 12);
    expect(rendererScatterThickness(160, 1)).toBeGreaterThan(rendererScatterThickness(96, 1));
    expect(rendererScatterThickness(96, 1)).toBeGreaterThan(rendererScatterThickness(44, 1));
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
    const patch = { sizeSpanMin: 40, sizeSpanMax: 200, sizeScatterGainMax: 2.5, sizeScatterFloor: 0, sizeScatterSpanMax: 200 };
    const mirrored = sourceSize(patch);
    const nominal = cssTierOptics(patch).regular.blurRadius;
    const platter = cssSizeScatterSigma(nominal, 400, mirrored);
    expect(platter).toBeCloseTo(nominal * 2.5, 12);
    expect(requiredSamplingPadding(platter)).toBeCloseTo(3 * platter, 12);
    expect(requiredSamplingPadding(platter)).toBeGreaterThan(requiredSamplingPadding(nominal));
    // With the floor off, a small control is unchanged, which is what makes the
    // wider floor a cost only the surfaces that earn it pay.
    expect(cssSizeScatterSigma(nominal, 40, mirrored)).toBeCloseTo(nominal, 12);

    // And on the shipped profile the floor is on: every surface with a span
    // frosts at σ 1.25 · (1 + 7 · 0.4) = 4.75 at least, so the padding a group
    // needs is 3σ of THAT — 14.25 CSS px on a small control, ~23.7 on a 160 px
    // platter — never the nominal σ's 3.75. core's advisory 24 still clears both.
    const shipped = cssTierOptics().regular.blurRadius;
    expect(shipped).toBe(1.25);
    expect(cssSizeScatterSigma(shipped, 32)).toBeCloseTo(4.75, 12);
    expect(requiredSamplingPadding(cssSizeScatterSigma(shipped, 32))).toBeCloseTo(14.25, 12);
    expect(requiredSamplingPadding(cssSizeScatterSigma(shipped, 160))).toBeLessThanOrEqual(24);
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
