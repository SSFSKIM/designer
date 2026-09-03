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
  DEFAULT_MATERIAL_PROFILE,
  INCREASED_OCCLUSION_LIFT,
  lensDepthPx,
  lensDirection,
  lensDisplacementPx,
  lensExtentPx,
  lensMagnitudePx,
  lensOvalizationAt,
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
    expect(next.sizeScatterFloor).toBe(DEFAULT_MATERIAL_PROFILE.sizeScatterFloor);
    expect(next.sizeScatterRampReach1xPx).toBe(DEFAULT_MATERIAL_PROFILE.sizeScatterRampReach1xPx);
    const scatter = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeScatterFloor: 0.1,
      sizeScatterRampReach1xPx: 500,
    });
    expect(scatter.sizeScatterFloor).toBe(0.1);
    expect(scatter.sizeScatterRampReach1xPx).toBe(500);
    expect(scatter.sizeSpanMax).toBe(DEFAULT_MATERIAL_PROFILE.sizeSpanMax);
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
    lensRefractionGain: 2,
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

  it("keeps the inner shadow's size gain on the profile's saturation, and scales the lens by its refraction gain", () => {
    // Well past `sizeSpanMax`, so the smoothstep has saturated and the gain is
    // exactly the profile's maximum — the inner shadow's depth gain since W12 G2.
    expect(lensSizeGain(4000, profile)).toBeCloseTo(4, 12);
    // The lens depth is the reference's height law, which this profile leaves at
    // its default: 20 at saturation on the default thickness.
    expect(lensDepthPx(8, 4000, profile)).toBeCloseTo(20, 12);
    // At the contour the displacement is the profile's gain on the reference's
    // amount law (60 at saturation): 2 × 60.
    expect(lensDisplacementPx(0, 4000, 8, 1, profile)).toBeCloseTo(120, 12);
  });

  it("displaces the body on the reference's span law along one steep power (W12 G2)", () => {
    // The shipped default on a 96-px-span surface of the host's 8 px thickness:
    // the reference's inner height there is 20 CSS px (claims §5.50) and its
    // amount 60, scaled 0.745 → 44.7 at the contour, dying as (1 − u/26.74)^3.69
    // — the crossings read 34 / 24 / 12 at 2 / 4 / 8 (claims §5.49).
    expect(lensDepthPx(8, 96)).toBeCloseTo(20, 12);
    expect(lensMagnitudePx(8, 96)).toBeCloseTo(44.7, 12);
    expect(lensExtentPx(8, 96)).toBeCloseTo(26.74, 12);
    expect(lensDisplacementPx(0, 96, 8, 1)).toBeCloseTo(44.7, 12);
    expect(lensDisplacementPx(2, 96, 8, 1)).toBeCloseTo(33.7, 0);
    expect(lensDisplacementPx(4, 96, 8, 1)).toBeCloseTo(24.3, 0);
    expect(lensDisplacementPx(8, 96, 8, 1)).toBeCloseTo(11.9, 0);
    for (const u of [4, 8, 12, 16]) {
      expect(lensDisplacementPx(u, 96, 8, 1)).toBeCloseTo(44.7 * (1 - u / 26.74) ** 3.69, 10);
    }
    // Zero from the extent inward.
    expect(lensDisplacementPx(26.74, 96, 8, 1)).toBe(0);
    expect(lensDisplacementPx(40, 96, 8, 1)).toBe(0);
    // The policy's refraction scale multiplies it, and a zero rung removes it.
    expect(lensDisplacementPx(0, 96, 8, 0.45)).toBeCloseTo(44.7 * 0.45, 12);
    expect(lensDisplacementPx(0, 96, 8, 0)).toBe(0);
  });

  it("takes the reference's own depths on the small spans, and clamps by the thickness it is given", () => {
    // min(0.25·span, 20) at the default thickness: the layer tree's 8 / 11 / 20.
    expect(lensDepthPx(8, 32)).toBeCloseTo(8, 12);
    expect(lensDepthPx(8, 44)).toBeCloseTo(11, 12);
    expect(lensDepthPx(8, 80)).toBeCloseTo(20, 12);
    expect(lensDepthPx(8, 160)).toBeCloseTo(20, 12);
    // A thicker authoring scales the depth and the magnitude together.
    expect(lensDepthPx(16, 96)).toBeCloseTo(40, 12);
    expect(lensMagnitudePx(16, 96)).toBeCloseTo(89.4, 12);
    // The half-extent clamp still holds, and the magnitude follows it by ratio.
    expect(lensDepthPx(80, 24)).toBe(12);
    expect(lensMagnitudePx(80, 24) / lensMagnitudePx(8, 24)).toBeCloseTo(12 / 6, 12);
    // The accessibility fold: at 0 the depth is the authored thickness alone.
    expect(lensDepthPx(8, 96, DEFAULT_MATERIAL_PROFILE, 0)).toBeCloseTo(8, 12);
    expect(lensDepthPx(8, 96, DEFAULT_MATERIAL_PROFILE, 0.5)).toBeCloseTo(14, 12);
  });

  it("ovalizes the direction on thick surfaces only, toward the surface's centre (W12 G2)", () => {
    expect(lensOvalizationAt(32)).toBe(0);
    expect(lensOvalizationAt(64)).toBe(0);
    // ω 0.8, landed by eye (W12 Decision Log 6, claims §5.54); the saturated
    // value is `lensOvalization` and the knee's midpoint is half of it.
    expect(lensOvalizationAt(68)).toBeCloseTo(0.4, 12);
    expect(lensOvalizationAt(72)).toBeCloseTo(0.8, 12);
    expect(lensOvalizationAt(160)).toBeCloseTo(0.8, 12);
    // At an edge's midpoint the oval's gradient is the normal, so the blend is
    // the normal at any ω; away from the midpoint it tilts toward the centre.
    const up: [number, number] = [0, -1];
    expect(lensDirection(up, [0, -48], [80, 48], 0.6)).toEqual([0, -1]);
    const tilted = lensDirection(up, [64, -46], [80, 48], 0.6);
    expect(tilted[0]).toBeGreaterThan(0.1);
    expect(tilted[1]).toBeLessThan(0);
    expect(Math.hypot(tilted[0], tilted[1])).toBeCloseTo(1, 12);
    // The tilt is toward the centre (x = 0), so on the other side it flips.
    expect(lensDirection(up, [-64, -46], [80, 48], 0.6)[0]).toBeCloseTo(-tilted[0], 12);
    // A thin surface keeps the normal.
    expect(lensDirection(up, [64, -46], [80, 48], 0)).toEqual([0, -1]);
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
