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

import { MATERIAL_SOURCE_OPTICS, cssTierOptics } from "@vitrea/platform-web";
import { DEFAULT_MATERIAL_PROFILE, MATERIAL_VARIANTS } from "@vitrea/renderer-webgpu";
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
