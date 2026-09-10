/**
 * W27c's two new tint-shade fields, on the CSS mirror (corrective K5's own
 * discipline, applied to a fresh pair rather than an established one).
 *
 * `tintChromaScale` and `tintShadeCollapseRetention` land on
 * `@vitrea/renderer-webgpu`'s `MaterialProfile` (`material.ts`, doc comments
 * beside `tintShadeDark`/`tintShadeLight`) and are mirrored by
 * `@vitreajs/vitrea-web`'s `resolvedTintShade` (`optics.ts`, `TintShadeConstants
 * .chromaScale`/`.collapseRetention`) and consumed by `tintShadeLayer`'s chroma
 * fold. Both fields are declared IDENTITY when absent — chroma 1 (the seed's
 * own hue, untouched), retention 0 (the pre-W27c grip formula, unaffected by
 * this pair) — so that a profile document that does not name them keeps its
 * existing fingerprint (`withMaterialOverrides`, `material.ts` ~L2880-2884).
 *
 * This file is narrow on purpose. It does not pin the fitted retention or
 * chroma VALUES W27c's sweep is still converging on (`results/
 * 2026-09-10-w27c-g1-*`) — those are provisional and not this test's business.
 * What it pins is the DERIVATION: that the identity is really the identity on
 * both scheme bases, that an override reaches the CSS mirror exactly as it
 * reaches the renderer's own resolved profile, and that the two tiers' CPU
 * statements of the chroma fold agree at real (non-identity) values across
 * seed hues — the same shape `tier-coherence.test.ts` already holds the
 * established tint-shade fields to, extended to the pair W27c added beside
 * them. It deliberately does NOT restate `createGlassRoot`'s inline `tintGrip`
 * expression (`root.ts`, beside the `authorTintLayer` call, reading
 * `tintShade.collapseRetention`): a test built on a copy of that formula would
 * still pass if `root.ts` stopped applying retention, since it would only be
 * checking its own restatement. `collapseRetention`'s actual shader behaviour
 * is `packages/renderer-webgpu/e2e/golden/receded-tint.spec.ts`'s job, and the
 * CSS-tier wiring is checked through runtime capture/provenance rather than
 * here.
 */

import {
  darkMaterialProfile,
  colorSchemeMaterialProfile,
  mergeMaterialProfiles,
  resolvedTintShade,
  TINT_SHADE,
  tintShadeLayer as cssTintShadeLayer,
  type TintShadeConstants,
} from "@vitreajs/vitrea-web";
import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  tintShadeLayer as rendererTintShadeLayer,
  type MaterialProfile,
} from "@vitrea/renderer-webgpu";
import { describe, expect, it } from "vitest";

/** The two scheme bases root.ts actually resolves from (`activeProfile` in root.ts). */
const SCHEME_BASES = [
  { name: "light", base: colorSchemeMaterialProfile("light") },
  { name: "dark", base: colorSchemeMaterialProfile("dark") },
] as const;

describe("W27c: tintChromaScale and tintShadeCollapseRetention on the CSS mirror", () => {
  it("darkMaterialProfile itself is silent on the new pair (the fit is still open)", () => {
    // Guards this file's own premise: if a landed fit had already patched the
    // dark document, the "identity absent" cases below would stop exercising
    // the absent branch on the dark base and this file would need extending,
    // not merely re-running.
    expect(darkMaterialProfile).not.toHaveProperty("tintChromaScale");
    expect(darkMaterialProfile).not.toHaveProperty("tintShadeCollapseRetention");
  });

  describe.each(SCHEME_BASES)("identity when absent, on the $name scheme base", ({ base }) => {
    it("resolves to chroma 1 / retention 0 on the mirror, and stays unmentioned on the resolved renderer profile", () => {
      const mirrored = resolvedTintShade(base);
      expect(mirrored.chromaScale).toBe(1);
      expect(mirrored.collapseRetention).toBe(0);

      const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, base ?? {});
      // The renderer's own doc comment: "Identity values are omitted from
      // resolved documents so the frozen active profiles keep their existing
      // fingerprints." An identity that leaked onto the resolved object would
      // still behave as 1/0 numerically, so the fingerprint claim needs the
      // stronger, structural check.
      expect(resolved).not.toHaveProperty("tintChromaScale");
      expect(resolved).not.toHaveProperty("tintShadeCollapseRetention");
    });

    it("leaves tintShadeLayer's chroma fold a no-op — the identity is behaviourally inert, not just numerically 1", () => {
      const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, base ?? {});
      const shade = resolvedTintShade(base);
      const seed = [0.86, 0.41, 0.09] as const; // an orange seed, W27c's own example hue
      for (const materialLuminance of [0, 0.2, 0.7, 1]) {
        for (const grip of [0, 0.5, 1]) {
          const renderer = rendererTintShadeLayer(seed, materialLuminance, grip, resolved);
          const mirror = cssTintShadeLayer(seed, materialLuminance, grip, shade);
          const plain = rendererTintShadeLayer(seed, materialLuminance, grip, DEFAULT_MATERIAL_PROFILE);
          for (const channel of [0, 1, 2] as const) {
            expect(renderer[channel]).toBeCloseTo(plain[channel], 12);
            expect(mirror[channel]).toBeCloseTo(renderer[channel], 12);
          }
        }
      }
    });
  });

  describe.each(SCHEME_BASES)("an explicit override, merged over the $name scheme base", ({ base }) => {
    // The real merge path an app's `materialProfile` patch takes in root.ts:
    // `mergeMaterialProfiles(colorSchemeMaterialProfile(scheme), hostProfile)`.
    const override = { tintChromaScale: 0.4, tintShadeCollapseRetention: 0.65 };
    const merged = mergeMaterialProfiles(base, override);

    it("reaches the CSS mirror at the same value the renderer's own resolved profile carries", () => {
      const mirrored = resolvedTintShade(merged);
      const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, merged ?? {});
      expect(mirrored.chromaScale).toBe(0.4);
      expect(mirrored.collapseRetention).toBe(0.65);
      expect(resolved.tintChromaScale).toBe(0.4);
      expect(resolved.tintShadeCollapseRetention).toBe(0.65);
      // Field-for-field parity, `tier-coherence.test.ts`'s own discipline for
      // every other tint-shade constant.
      expect(mirrored.chromaScale).toBe(resolved.tintChromaScale);
      expect(mirrored.collapseRetention).toBe(resolved.tintShadeCollapseRetention);
    });
  });

  describe("tintShadeLayer's chroma fold, real (non-identity) values, both seed hues", () => {
    // W27c's own probe pair (§5.130): an orange and a blue seed that collapse
    // to the SAME grey under full desaturation despite differing luminances —
    // exactly the property a hue-blind mirror bug would miss.
    const seeds = {
      orange: [0.86, 0.41, 0.09] as const,
      blue: [0.09, 0.41, 0.86] as const,
    };

    it("the two CPU statements agree at every chroma, material level and grip", () => {
      for (const [, seed] of Object.entries(seeds)) {
        for (const chromaScale of [1, 0.6, 0.25, 0]) {
          const rendererProfile: MaterialProfile = { ...DEFAULT_MATERIAL_PROFILE, tintChromaScale: chromaScale };
          const shade: TintShadeConstants = { ...TINT_SHADE, chromaScale };
          for (const materialLuminance of [0, 0.15, 0.5, 0.85, 1]) {
            for (const grip of [0, 0.35, 1]) {
              const renderer = rendererTintShadeLayer(seed, materialLuminance, grip, rendererProfile);
              const mirror = cssTintShadeLayer(seed, materialLuminance, grip, shade);
              for (const channel of [0, 1, 2] as const) {
                expect(
                  mirror[channel],
                  `chroma ${chromaScale} material ${materialLuminance} grip ${grip} channel ${channel}`,
                ).toBeCloseTo(renderer[channel], 12);
              }
            }
          }
        }
      }
    });

    it("chroma 0 collapses both hues to the SAME neutral (the property W27c measured)", () => {
      const grip = 1;
      const materialLuminance = 0.4;
      const shade: TintShadeConstants = { ...TINT_SHADE, chromaScale: 0 };
      const orangeLayer = cssTintShadeLayer(seeds.orange, materialLuminance, grip, shade);
      const blueLayer = cssTintShadeLayer(seeds.blue, materialLuminance, grip, shade);
      // Both seeds share the same maximum channel (0.86), so a correct
      // desaturation-to-neutral fold lands them on the same grey regardless of
      // which channel carried the hue.
      for (const channel of [0, 1, 2] as const) {
        expect(orangeLayer[channel]).toBeCloseTo(blueLayer[channel], 12);
        expect(orangeLayer[channel]).toBeCloseTo(orangeLayer[0], 12); // R=G=B: fully neutral
      }
    });

    it("chroma 1 (identity) preserves each seed's own chromaticity ratio", () => {
      const grip = 1;
      const materialLuminance = 0.4;
      const shade: TintShadeConstants = { ...TINT_SHADE, chromaScale: 1 };
      const layer = cssTintShadeLayer(seeds.orange, materialLuminance, grip, shade);
      const [r, g, b] = seeds.orange;
      // A uniform scalar shade must not bend the seed's own ratios.
      expect(layer[1] / layer[0]).toBeCloseTo(g / r, 10);
      expect(layer[2] / layer[0]).toBeCloseTo(b / r, 10);
    });
  });
});
