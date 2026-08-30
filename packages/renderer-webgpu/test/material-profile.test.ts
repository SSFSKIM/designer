/**
 * The material profile seam: the override mechanism, not the numbers.
 *
 * What is worth pinning here is that a *partial* profile stays partial. C7 fits
 * one axis at a time — a tint alpha now, a rim width later — and the failure mode
 * of a merge that overwrites instead of merging is silent: the patch lands, the
 * material draws, and every sibling constant of the field that was named has
 * quietly become `undefined`. So each test names one field and asserts about its
 * neighbours.
 *
 * The other half is that a patch *replaces* rather than accumulates. A profile is
 * one set of measurements; half of one set over half of another describes no
 * material, so `setMaterialProfile` re-resolves from the defaults every time and
 * this file holds it to that.
 */

import { describe, expect, it } from "vitest";

import {
  bodyLod,
  DEFAULT_MATERIAL_PROFILE,
  INCREASED_OCCLUSION_LIFT,
  lensDepthPx,
  lensSizeGain,
  MATERIAL_OPTICS,
  MATERIAL_VARIANTS,
  occlusionAlphaUnderPolicy,
  opticsUnderPolicy,
  REFRACTION_LADDER,
  REFRACTION_SCALE,
  withMaterialOverrides,
  type MaterialProfile,
} from "../src/material";
import { adaptiveTint } from "../src/analysis";
import { createWebGPURenderer, NOMINAL_MATERIAL_POLICY } from "../src/renderer";

describe("the default profile", () => {
  it("is what the named constants are", () => {
    expect(MATERIAL_OPTICS).toBe(DEFAULT_MATERIAL_PROFILE.optics);
    expect(REFRACTION_SCALE).toBe(DEFAULT_MATERIAL_PROFILE.refractionScale);
  });

  it("declares every variant and every rung", () => {
    expect(Object.keys(DEFAULT_MATERIAL_PROFILE.optics).sort()).toEqual(
      [...MATERIAL_VARIANTS].sort(),
    );
    expect(Object.keys(DEFAULT_MATERIAL_PROFILE.refractionScale).sort()).toEqual(
      [...REFRACTION_LADDER].sort(),
    );
  });
});

describe("withMaterialOverrides", () => {
  it("is the identity on an empty patch", () => {
    expect(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {})).toEqual(
      DEFAULT_MATERIAL_PROFILE,
    );
  });

  it("keeps a variant's other optics when one field is named", () => {
    const next = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      optics: { regular: { tintAlpha: 0.6 } },
    });
    expect(next.optics.regular.tintAlpha).toBe(0.6);
    expect(next.optics.regular.blurSigma).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma);
    expect(next.optics.regular.rimWidth).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.rimWidth);
    expect(next.optics.regular.highlight).toEqual(
      DEFAULT_MATERIAL_PROFILE.optics.regular.highlight,
    );
    // And the variant nobody named is untouched.
    expect(next.optics.clear).toEqual(DEFAULT_MATERIAL_PROFILE.optics.clear);
  });

  it("keeps the other rungs when one refraction scale is named", () => {
    const next = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      refractionScale: { approximate: 0.3 },
    });
    expect(next.refractionScale).toEqual({
      none: DEFAULT_MATERIAL_PROFILE.refractionScale.none,
      approximate: 0.3,
      true: DEFAULT_MATERIAL_PROFILE.refractionScale.true,
    });
  });

  it("keeps the strong-border rim's other half", () => {
    const next = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      strongBorderRim: { rimAlpha: 0.5 },
    });
    expect(next.strongBorderRim).toEqual({
      rimWidth: DEFAULT_MATERIAL_PROFILE.strongBorderRim.rimWidth,
      rimAlpha: 0.5,
    });
  });

  it("replaces the flat leaves it is given and no others", () => {
    const next = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      lensSizeGainMax: 4,
      glowGain: 0.1,
    });
    expect(next.lensSizeGainMax).toBe(4);
    expect(next.glowGain).toBe(0.1);
    expect(next.sizeSpanMin).toBe(DEFAULT_MATERIAL_PROFILE.sizeSpanMin);
    expect(next.sizeSpanMax).toBe(DEFAULT_MATERIAL_PROFILE.sizeSpanMax);
    expect(next.sweepGain).toBe(DEFAULT_MATERIAL_PROFILE.sweepGain);
    expect(next.lightDirection).toEqual(DEFAULT_MATERIAL_PROFILE.lightDirection);
  });

  it("does not mutate the base", () => {
    const before = structuredClone(DEFAULT_MATERIAL_PROFILE) as MaterialProfile;
    withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      optics: { regular: { tintAlpha: 0.6 }, clear: { blurSigma: 99 } },
      refractionScale: { true: 0.1 },
      strongBorderRim: { rimWidth: 9 },
      adaptiveLuminanceLow: 0.5,
    });
    expect(DEFAULT_MATERIAL_PROFILE).toEqual(before);
  });

  it("composes onto a patched profile when a caller asks for that explicitly", () => {
    const once = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      optics: { regular: { tintAlpha: 0.6 } },
    });
    const twice = withMaterialOverrides(once, { optics: { regular: { rimAlpha: 0.9 } } });
    expect(twice.optics.regular.tintAlpha).toBe(0.6);
    expect(twice.optics.regular.rimAlpha).toBe(0.9);
  });
});

describe("the foldings read the profile they are given", () => {
  const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
    reducedTransparencyFrost: 3,
    increasedOcclusionLift: 0.5,
    reducedTintAdaptation: 0.1,
    lensSizeGainMax: 4,
    lensBodyLodPerPx: 1,
    adaptiveLuminanceLow: 0,
    adaptiveLuminanceHigh: 1,
  });

  it("frosts by the profile's multiplier", () => {
    const optics = opticsUnderPolicy(
      profile.optics.regular,
      { ...NOMINAL_MATERIAL_POLICY, frost: "increased" },
      profile,
    );
    expect(optics.blurSigma).toBeCloseTo(profile.optics.regular.blurSigma * 3, 12);
  });

  it("occludes by the profile's lift, which is a fraction of the headroom", () => {
    const nominal = profile.optics.regular.tintAlpha;
    const optics = opticsUnderPolicy(
      profile.optics.regular,
      { ...NOMINAL_MATERIAL_POLICY, occlusion: "increased" },
      profile,
    );
    expect(optics.tintAlpha).toBeCloseTo(nominal + 0.5 * (1 - nominal), 12);
    expect(optics.tintAlpha).toBeGreaterThan(nominal);
  });

  /*
   * Decision Log #32(d). The lift used to be an absolute floor, which C9a's tint
   * tune silently walked past: nominal became the floor, `Math.max` became the
   * identity, and the accessibility policy stopped doing anything without anyone
   * touching it. This is the test that would have caught that, and it is written
   * over nominals no tuning pass has reached rather than over the shipped one.
   */
  it("lifts at any nominal, so a retune cannot make it inert", () => {
    for (const tintAlpha of [0, 0.05, 0.28, 0.62, 0.9, 0.999]) {
      const optics = opticsUnderPolicy(
        { ...DEFAULT_MATERIAL_PROFILE.optics.regular, tintAlpha },
        { ...NOMINAL_MATERIAL_POLICY, occlusion: "increased" },
      );
      expect(optics.tintAlpha, `tintAlpha ${tintAlpha}`).toBeGreaterThan(tintAlpha);
    }
    // A material with nothing left to hide is the one place it cannot lift.
    expect(occlusionAlphaUnderPolicy(1, "increased")).toBe(1);
  });

  it("is a fitted lift now, not the pre-C9a floor re-expressed", () => {
    /*
     * This asserted that the relative form reproduced the old absolute floor
     * exactly — `occlusionAlphaUnderPolicy(0.28, "increased") === 0.62`, and the
     * constant equal to (0.62 − 0.28) / (1 − 0.28). That was the right assertion
     * for a number whose only justification was continuity: it had never been
     * measured against anything.
     *
     * Round two fitted it against the active bed (2026-08-31) on both
     * accessibility profiles' calibration cells, under the protocol declared in
     * claims §5.15, and it moved 0.4722 → 0.75. The old identity is false by
     * construction now, so what is pinned is the property the relative form
     * exists for rather than the number it used to reproduce.
     */
    expect(INCREASED_OCCLUSION_LIFT).toBeCloseTo(0.75, 6);

    // The form's whole point: a FRACTION of the remaining transparency, which
    // cannot die silently the way an absolute floor does once nominal passes it.
    for (const nominal of [0.1, 0.28, 0.46, 0.8]) {
      expect(occlusionAlphaUnderPolicy(nominal, "increased"), `nominal ${nominal}`).toBeCloseTo(
        nominal + INCREASED_OCCLUSION_LIFT * (1 - nominal),
        12,
      );
    }
    // At the shipped nominal, which is what the accessibility profiles run on.
    expect(occlusionAlphaUnderPolicy(0.46, "increased")).toBeCloseTo(0.865, 3);
  });

  it("gains the lens by the profile's saturation, and lods by its rate", () => {
    // Well past `sizeSpanMax`, so the smoothstep has saturated and the gain is
    // exactly the profile's maximum.
    expect(lensSizeGain(4000, profile)).toBeCloseTo(4, 12);
    expect(lensDepthPx(8, 4000, profile)).toBeCloseTo(32, 12);
    expect(bodyLod(3, 10, profile)).toBeCloseTo(3, 12);
  });

  it("crosses the tint over the profile's own luminance band", () => {
    // With the band opened to 0…1, mid-luminance is the halfway mix rather than
    // the default band's saturated light end.
    const mid = adaptiveTint(0.5, profile);
    const expected =
      (profile.adaptiveTintDark[0] + profile.adaptiveTintLight[0]) / 2;
    expect(mid[0]).toBeCloseTo(expected, 12);
  });

  it("falls back to the defaults when no profile is passed", () => {
    expect(lensSizeGain(4000)).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.lensSizeGainMax, 12);
    expect(adaptiveTint(0.5)).toEqual(adaptiveTint(0.5, DEFAULT_MATERIAL_PROFILE));
  });
});

describe("the renderer's profile", () => {
  it("resolves the constructor's patch over the defaults", () => {
    const renderer = createWebGPURenderer({
      materialProfile: { optics: { regular: { tintAlpha: 0.6 } } },
    });
    expect(renderer.materialProfile.optics.regular.tintAlpha).toBe(0.6);
    expect(renderer.materialProfile.optics.regular.blurSigma).toBe(
      DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma,
    );
  });

  it("defaults to exactly DEFAULT_MATERIAL_PROFILE", () => {
    expect(createWebGPURenderer().materialProfile).toEqual(DEFAULT_MATERIAL_PROFILE);
  });

  it("replaces rather than accumulates", () => {
    const renderer = createWebGPURenderer();
    renderer.setMaterialProfile({ optics: { regular: { tintAlpha: 0.6 } } });
    renderer.setMaterialProfile({ optics: { regular: { rimAlpha: 0.9 } } });

    expect(renderer.materialProfile.optics.regular.rimAlpha).toBe(0.9);
    // The first patch is gone, not compounded: this is the default again.
    expect(renderer.materialProfile.optics.regular.tintAlpha).toBe(
      DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha,
    );
  });

  it("returns to the defaults on an empty patch", () => {
    const renderer = createWebGPURenderer({ materialProfile: { glowGain: 0.1 } });
    renderer.setMaterialProfile({});
    expect(renderer.materialProfile).toEqual(DEFAULT_MATERIAL_PROFILE);
  });
});
