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
 * It cannot be held by an import. `@vitrea/platform-web` has no dependency on
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

import { resolveAccessibilityPolicy } from "vitrea";
import {
  CSS_TIER_MAPPING,
  FOREGROUND_INK,
  INCREASED_OCCLUSION_LIFT,
  MATERIAL_SOURCE_OPTICS,
  REDUCED_TRANSPARENCY_FROST,
  cssTierOptics,
  foregroundDeclarations,
  gpuTierForegroundLevel,
  occlusionAlphaUnderPolicy,
  opticsUnderPolicy as cssTierOpticsUnderPolicy,
  resolvedPolicyFold,
  sourceOptics,
} from "@vitrea/platform-web";
import {
  DEFAULT_MATERIAL_PROFILE,
  INCREASED_OCCLUSION_LIFT as RENDERER_OCCLUSION_LIFT,
  MATERIAL_VARIANTS,
  occlusionAlphaUnderPolicy as rendererOcclusionAlphaUnderPolicy,
  opticsUnderPolicy as rendererOpticsUnderPolicy,
  withMaterialOverrides,
} from "@vitrea/renderer-webgpu";
import { describe, expect, it } from "vitest";

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

  it("keeps the two tiers on one blur sigma, which is also S1's 3σ floor", () => {
    // core's 24px `samplingPadding` advisory is 3σ at σ = 8. If the CSS tier's
    // blur ever stopped being the renderer's, that arithmetic would silently
    // stop holding for one of the two tiers.
    const css = cssTierOptics();
    expect(css.regular.blurRadius).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma);
    expect(css.regular.blurRadius * 3).toBe(24);
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
});
