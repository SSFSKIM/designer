/**
 * The outer shadow (W8) — the facet the reference casts and vitrea rendered zero
 * of, across 8.5% to 29.6% of the canvas, on both tiers.
 *
 * What these pin is the MECHANISM, not the amplitude. The constants are
 * PROVISIONAL by charter — the recalibration cascade fits them under X1's holdout
 * discipline — so a test that pinned `occlusion` to 0.33 would fail the moment
 * the fit lands and would have proved nothing in the meantime. What must not move
 * without somebody noticing is the shape of the thing: a Gaussian-blurred copy of
 * the surface's own silhouette, offset downward, applied as a MULTIPLICATIVE
 * occlusion of whatever is behind it, and therefore exactly inert over black.
 *
 * The two-tier half of the claim lives in
 * `packages/calibration/test/tier-coherence.test.ts`, which is the one package
 * entitled to import both renderers.
 */

import { DEFAULT_GROUP_UNION } from "@vitrea/geometry";
import { describe, expect, it } from "vitest";

import { groupFieldRect, resolveSurfaces } from "../src/instances";
import {
  DEFAULT_MATERIAL_PROFILE,
  NOMINAL_MATERIAL_POLICY,
  OUTER_SHADOW,
  outerShadowAlpha,
  outerShadowFalloff,
  outerShadowReachPx,
  outerShadowUnderPolicy,
  sizeOuterShadowOcclusion,
  sizeOuterShadowOcclusionAt,
  SRGB_ENCODING_EXPONENT,
  withMaterialOverrides,
  type MaterialPolicyView,
} from "../src/material";
import type { GroupRenderInput, SurfaceInput } from "../src/render-model";
import { WGSL_OPTICS_PASS } from "../src/wgsl/optics";

const surface = (over: Partial<SurfaceInput> = {}): SurfaceInput => ({
  nodeId: "s1",
  family: "fixed-rounded-rect",
  shape: {
    center: [100, 60],
    size: [120, 40],
    radii: [20, 20, 20, 20],
    smoothing: 0,
    thickness: 8,
  },
  reference: "figma-smoothing",
  ...over,
});

const group = (surfaces: readonly SurfaceInput[]): GroupRenderInput => ({
  groupId: "g1",
  surfaces,
  refraction: "true",
  analysisExact: true,
});

const policy = (over: Partial<MaterialPolicyView> = {}): MaterialPolicyView => ({
  ...NOMINAL_MATERIAL_POLICY,
  ...over,
});

/**
 * The exact normal CDF, by Abramowitz & Stegun 7.1.26 on `erf`, so the shipped
 * tanh form is checked against something that is not itself.
 */
const exactNormalCdf = (x: number): number => {
  const z = x / Math.SQRT2;
  const sign = z < 0 ? -1 : 1;
  const a = Math.abs(z);
  const t = 1 / (1 + 0.3275911 * a);
  const erf =
    1 -
    ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) *
      t *
      Math.exp(-a * a);
  return 0.5 * (1 + sign * erf);
};

describe("the outer shadow's falloff is a blurred silhouette", () => {
  it("is the Gaussian's integral: half on the edge, monotone outward, gone by three sigma", () => {
    for (const sigma of [1, 8, 15.55, 40]) {
      expect(outerShadowFalloff(0, sigma), `sigma ${sigma}`).toBeCloseTo(0.5, 9);
      expect(outerShadowFalloff(-3 * sigma, sigma)).toBeGreaterThan(0.998);
      expect(outerShadowFalloff(3 * sigma, sigma)).toBeLessThan(0.002);

      let previous = 1;
      for (let d = -4 * sigma; d <= 4 * sigma; d += sigma / 16) {
        const value = outerShadowFalloff(d, sigma);
        expect(value, `sigma ${sigma} at ${d}`).toBeLessThanOrEqual(previous + 1e-15);
        expect(value).toBeGreaterThanOrEqual(0);
        expect(value).toBeLessThanOrEqual(1);
        previous = value;
      }
    }
  });

  it("is a Gaussian and not a smoothstep, to within a thousandth of a code step", () => {
    /*
     * The shape is the claim. WGSL has no `erf`, so the shader (and this mirror)
     * evaluate the tanh form of the normal CDF; a cheaper `smoothstep` would be
     * off by two per cent, which at the reference's amplitude is five 8-bit codes
     * — visible banding around every surface in the product.
     */
    let worst = 0;
    for (let x = -8; x <= 8; x += 0.001) {
      worst = Math.max(worst, Math.abs(outerShadowFalloff(-x, 1) - exactNormalCdf(x)));
    }
    expect(worst).toBeLessThan(2e-3);
    expect(worst * OUTER_SHADOW.occlusion * 255).toBeLessThan(0.2);
  });

  it("scales with sigma alone, so one profile length sets the whole edge", () => {
    // Self-similarity: the curve at 2σ and distance 2d is the curve at σ and d.
    for (const d of [-30, -5, 0, 5, 30]) {
      expect(outerShadowFalloff(2 * d, 2 * 15.55)).toBeCloseTo(outerShadowFalloff(d, 15.55), 12);
    }
  });
});

describe("the outer shadow is a multiplicative occlusion", () => {
  it("removes a fraction of the backdrop's own light, and none of nothing", () => {
    /*
     * The property the reference measures and the reason the facet is invisible
     * over `dark-solid`: mirrored pixel pairs either side of a capsule over a
     * structured backdrop show darkening whose RATIO tracks the backdrop's ratio
     * to 4.5%, where a constant subtraction misses by 79% of the signal.
     *
     * Both tiers reach it the same way — a pure BLACK layer at some alpha,
     * composited source-over — because `(1 - a)·backdrop + a·0` is
     * `backdrop·(1 - a)`. So this is the algebra, asserted directly.
     */
    const alpha = outerShadowAlpha(OUTER_SHADOW.occlusion);
    const composite = (backdrop: number, a: number): number => (1 - a) * backdrop + a * 0;

    expect(composite(0, alpha)).toBe(0);
    for (const backdrop of [0.02, 0.2, 0.5, 1]) {
      expect(composite(backdrop, alpha)).toBeCloseTo(backdrop * (1 - alpha), 12);
    }
    // Proportional, at every strength: doubling the light behind doubles the
    // light removed.
    for (const a of [0, 0.1, alpha, 0.9, 1]) {
      expect(composite(1, a) - composite(0.5, a)).toBeCloseTo(composite(0.5, a), 12);
    }
  });

  it("converts the reference's linear occlusion into a compositing-space alpha", () => {
    /*
     * The one honest gap, and it is a colour SPACE rather than a mechanism: the
     * reference removes a fraction of LINEAR light, and both a `box-shadow` and a
     * premultiplied canvas composite in ENCODED sRGB. Inverting the transfer
     * function's power law makes the conversion backdrop-independent, and what is
     * left is the transfer function's linear toe near black.
     *
     * Measured here across the whole backdrop range and held under three 8-bit
     * codes, against a reference bed whose own reproducibility is +/-4 of 255
     * (Decision Log 10) — so the residual is under the noise the bed is read at.
     */
    const encode = (linear: number): number =>
      linear <= 0.0031308 ? 12.92 * linear : 1.055 * linear ** (1 / SRGB_ENCODING_EXPONENT) - 0.055;

    const worstCodesAt = (occlusion: number): number => {
      const alpha = outerShadowAlpha(occlusion);
      let worst = 0;
      for (let i = 0; i <= 400; i += 1) {
        const linear = 0.004 * (1 / 0.004) ** (i / 400);
        worst = Math.max(
          worst,
          Math.abs(encode(linear * (1 - occlusion)) - encode(linear) * (1 - alpha)) * 255,
        );
      }
      return worst;
    };

    // The three amplitudes the bed actually measured: dark standard, reduced
    // transparency, light standard.
    for (const occlusion of [0.06, 0.18, OUTER_SHADOW.occlusion]) {
      expect(worstCodesAt(occlusion), `occlusion ${occlusion}`).toBeLessThan(3);
    }
    // And the honest shape of the limitation, rather than a bound chosen to hide
    // it: the residual grows with the amplitude, because the toe it comes from is
    // a larger share of a deeper shadow. A profile that fitted a much stronger
    // shadow than anything measured would pay more, and this says how much.
    expect(worstCodesAt(0.6)).toBeGreaterThan(worstCodesAt(OUTER_SHADOW.occlusion));
    expect(worstCodesAt(0.6)).toBeLessThan(5);

    // Monotone, and exact at both ends whatever the cascade fits: no occlusion is
    // no shadow, total occlusion is opaque black.
    expect(outerShadowAlpha(0)).toBe(0);
    expect(outerShadowAlpha(1)).toBe(1);
    let previous = -1;
    for (let occ = 0; occ <= 1; occ += 0.01) {
      const alpha = outerShadowAlpha(occ);
      expect(alpha).toBeGreaterThanOrEqual(previous);
      previous = alpha;
    }
    // Clamped rather than extrapolated: a patched profile cannot ask for a
    // negative alpha or one past opacity.
    expect(outerShadowAlpha(-1)).toBe(0);
    expect(outerShadowAlpha(2)).toBe(1);
  });
});

describe("the outer shadow under the accessibility regime and the size law", () => {
  it("dims under reduced transparency by the measured factor, not by a guess", () => {
    /*
     * MEASURED. The reference's shadow under `reduce transparency` is the same
     * shadow at 0.566 of the amplitude — 0.1830/0.3259, 0.1884/0.3309 and
     * 0.1882/0.3314 on the three structured backdrops at a 44 px span, with the
     * three lengths unmoved. It neither vanishes nor intensifies.
     */
    const nominal = outerShadowUnderPolicy(policy());
    expect(nominal).toEqual(OUTER_SHADOW);

    const reduced = outerShadowUnderPolicy(policy({ frost: "increased" }));
    expect(reduced.occlusion).toBeCloseTo(
      OUTER_SHADOW.occlusion * OUTER_SHADOW.reducedTransparencyOcclusion,
      12,
    );
    expect(reduced.occlusion).toBeGreaterThan(0);
    expect(reduced.occlusion).toBeLessThan(nominal.occlusion);
    // Only the amplitude moves. The reference's sigma, offset and spread read the
    // same under the preference as without it.
    expect(reduced.sigmaPx).toBe(nominal.sigmaPx);
    expect(reduced.offsetPx).toBe(nominal.offsetPx);
    expect(reduced.spreadPx).toBe(nominal.spreadPx);
  });

  it("goes out with the material under forced colours", () => {
    // Not a dimmer shadow — no shadow. A surface that has become a flat system
    // fill has no elevation to cast one from, and a shadow that outlived the
    // glass would be exactly the composition the regime exists to prevent.
    expect(outerShadowUnderPolicy(policy({ glass: "none" })).occlusion).toBe(0);
    expect(outerShadowUnderPolicy(policy({ frost: "none" })).occlusion).toBe(0);
  });

  it("takes its multiplier from the profile that is drawing, not from the shipped one", () => {
    const patched = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      outerShadow: { occlusion: 0.5, reducedTransparencyOcclusion: 0.25 },
    });
    expect(outerShadowUnderPolicy(policy({ frost: "increased" }), patched).occlusion).toBeCloseTo(
      0.125,
      12,
    );
    // A partial patch keeps every field it does not name — the renderer's own
    // merge rule, and what makes a one-constant calibration patch legal.
    expect(patched.outerShadow.sigmaPx).toBe(OUTER_SHADOW.sigmaPx);
    expect(patched.outerShadow.offsetPx).toBe(OUTER_SHADOW.offsetPx);
  });

  it("rides the size law's one curve on the amplitude, and ships inert", () => {
    /*
     * The seam and its measured emptiness, both. The reference's three LENGTHS
     * are span-invariant (fitted sigma 15.4…15.9 across spans of 32, 44, 96 and
     * 160 px), so only the amplitude may couple — and the amplitude's coupling
     * points in OPPOSITE directions in the two colour schemes, so the shipped
     * gain is the identity until something can identify it.
     */
    expect(OUTER_SHADOW.sizeGain).toBe(0);
    for (const span of [0, 32, 44, 96, 160, 4000]) {
      expect(sizeOuterShadowOcclusion(0.33, span)).toBeCloseTo(0.33, 12);
    }

    const gained = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      outerShadow: { sizeGain: 0.5 },
    });
    expect(sizeOuterShadowOcclusion(0.33, 0, gained)).toBeCloseTo(0.33, 12);
    expect(sizeOuterShadowOcclusion(0.33, 4000, gained)).toBeCloseTo(0.33 + 0.5 * 0.67, 12);
    // Relative to the remaining headroom, like every other occlusion gain in the
    // profile, so it cannot take a nearly-opaque shadow past opacity.
    expect(sizeOuterShadowOcclusion(1, 4000, gained)).toBeCloseTo(1, 12);
  });
});

describe("the shadow's reach sizes the rect the GPU tier draws into", () => {
  it("stops where the shadow stops moving a code, measured in the space it writes", () => {
    const reach = outerShadowReachPx(OUTER_SHADOW);
    // Far enough to draw the facet: the reference's own measured extent runs to
    // roughly 45 px below a 1x surface.
    expect(reach).toBeGreaterThan(35);
    expect(reach).toBeLessThan(55);

    /*
     * The threshold is on the COMPOSITING-SPACE alpha, not on the linear
     * occlusion, and the difference is not academic — it is five CSS px of pad on
     * every edge of every group, on a facet measured at 3.2x the frame's GPU
     * time. What the canvas writes is `page × (1 − α·falloff)`, so one 8-bit code
     * moves when `α·falloff` reaches 1/255; the linear occlusion is a larger
     * number and thresholding it reaches further than anything can be seen at.
     */
    const alpha = outerShadowAlpha(OUTER_SHADOW.occlusion);
    const codesAt = (d: number): number =>
      alpha *
      outerShadowFalloff(
        d - OUTER_SHADOW.offsetPx - OUTER_SHADOW.spreadPx,
        OUTER_SHADOW.sigmaPx,
      ) *
      255;
    expect(codesAt(reach)).toBeLessThan(1);
    expect(codesAt(reach - 4)).toBeGreaterThan(1);

    // And it is strictly tighter than the same solve run on the linear occlusion,
    // which is the bug this replaced.
    const linearThresholded = (() => {
      let d = 0;
      while (OUTER_SHADOW.occlusion * outerShadowFalloff(d - 11.05, 15.55) * 255 > 1) d += 0.01;
      return d;
    })();
    expect(reach).toBeLessThan(linearThresholded);
    expect(linearThresholded - reach).toBeGreaterThan(3);
  });

  it("covers the deepest shadow the size law can amplify a member to", () => {
    /*
     * The pad is the scissor, and the shader amplifies the amplitude per surface
     * against the CASTING surface's thickness. A rect padded from the group's BASE
     * amplitude while a thick member emits more slices that member's shadow off at
     * the scissor — and the CSS tier, which has no scissor, goes on drawing it, so
     * the two tiers disagree on a facet they otherwise draw identically.
     *
     * The gain ships at the identity, so today the two are equal; the property
     * that has to hold is that the reach FOLLOWS the amplitude, for whatever the
     * cascade fits.
     */
    expect(outerShadowReachPx({ ...OUTER_SHADOW, occlusion: OUTER_SHADOW.occlusion })).toBe(
      outerShadowReachPx(OUTER_SHADOW),
    );

    const gained = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      outerShadow: { sizeGain: 1 },
    });
    const amplified = sizeOuterShadowOcclusionAt(OUTER_SHADOW.occlusion, 1, gained);
    expect(amplified).toBe(1);
    const amplifiedReach = outerShadowReachPx({ ...OUTER_SHADOW, occlusion: amplified });
    expect(amplifiedReach).toBeGreaterThan(outerShadowReachPx(OUTER_SHADOW));
    // The margin the base-amplitude pad would have sliced off.
    expect(amplifiedReach - outerShadowReachPx(OUTER_SHADOW)).toBeGreaterThan(4);

    // Monotone in the amplitude, so a maximum over a group's members is a correct
    // upper bound however the gain is signed.
    let previous = 0;
    for (const occlusion of [0.05, 0.1, 0.2, 0.33, 0.5, 0.8, 1]) {
      const reach = outerShadowReachPx({ ...OUTER_SHADOW, occlusion });
      expect(reach, `occlusion ${occlusion}`).toBeGreaterThanOrEqual(previous);
      previous = reach;
    }
  });

  it("is exactly zero when a profile declines the shadow, so nothing pays for it", () => {
    const off = { ...OUTER_SHADOW, occlusion: 0 };
    expect(outerShadowReachPx(off)).toBe(0);
    // And a shadow too faint to reach one code step anywhere is the same case.
    expect(outerShadowReachPx({ ...OUTER_SHADOW, occlusion: 1 / 512 })).toBe(0);
  });

  it("grows with the blur, the offset and the spread", () => {
    const base = outerShadowReachPx(OUTER_SHADOW);
    expect(outerShadowReachPx({ ...OUTER_SHADOW, sigmaPx: 31.1 })).toBeGreaterThan(base);
    expect(
      outerShadowReachPx({ ...OUTER_SHADOW, offsetPx: OUTER_SHADOW.offsetPx + 10 }),
    ).toBeCloseTo(base + 10, 6);
    expect(
      outerShadowReachPx({ ...OUTER_SHADOW, spreadPx: OUTER_SHADOW.spreadPx + 10 }),
    ).toBeCloseTo(base + 10, 6);
  });

  it("pads the field rect, because the optics pass scissors to it", () => {
    /*
     * The one place this facet could be implemented perfectly and still draw
     * nothing. `opticsPass` sets this rect as both the viewport and the scissor,
     * so a rect padded only by the rim and the union's bulge — about 3 px — would
     * slice a 45 px shadow off at the contour.
     */
    const resolved = resolveSurfaces(group([surface()]), "rsupn");
    const reach = outerShadowReachPx(OUTER_SHADOW);

    const bare = groupFieldRect(resolved, DEFAULT_GROUP_UNION, 2, 0);
    const shadowed = groupFieldRect(resolved, DEFAULT_GROUP_UNION, 2, reach);

    // Members span x 40..160, y 40..80.
    expect(shadowed.x).toBeCloseTo(40 - reach, 10);
    expect(shadowed.width).toBeCloseTo(120 + 2 * reach, 10);
    expect(shadowed.y).toBeCloseTo(40 - reach, 10);
    expect(shadowed.height).toBeCloseTo(40 + 2 * reach, 10);
    expect(shadowed.width).toBeGreaterThan(bare.width);

    // A reach smaller than the rim-and-bulge margin never shrinks the rect: the
    // shadow adds to what already had to be there rather than replacing it.
    expect(groupFieldRect(resolved, DEFAULT_GROUP_UNION, 2, 0)).toEqual(
      groupFieldRect(resolved, DEFAULT_GROUP_UNION, 2),
    );
    expect(groupFieldRect(resolved, DEFAULT_GROUP_UNION, 2, 1).width).toBe(bare.width);
  });
});

describe("the shader draws the shadow the CPU resolved", () => {
  it("reads the offset silhouette from the field, not from the local gradient", () => {
    /*
     * A first-order estimate — `d + offset·normal.y` — is exact only on a
     * straight edge, and a capsule is mostly not one; it would round every corner
     * the shadow passed. The shader samples the group's own field at the offset
     * position instead, which is exact everywhere for the cost of one read.
     */
    expect(WGSL_OPTICS_PASS).toContain("fn outer_shadow_falloff(");
    expect(WGSL_OPTICS_PASS).toContain("fn outer_shadow_alpha(");
    expect(WGSL_OPTICS_PASS).toContain("uv.y - ou.shadow.w");
    /*
     * And the shift's own edge case, which is not an edge case: the field rect is
     * clipped to the canvas AND padded only by the shadow's reach, so the rows the
     * shift needs are missing both for a surface near the viewport's top and, for
     * every group, in its topmost band. A clamp alone repeats the edge texel — a
     * distance too SMALL, which paints a flat, too-dark falloff exactly where the
     * shadow should be fading out. The distance that was clamped off is added
     * back, which is exact directly above a surface because a signed distance
     * field is 1-Lipschitz.
     */
    expect(WGSL_OPTICS_PASS).toContain("clampedOffCss");
    expect(WGSL_OPTICS_PASS).toContain("shadowField.x + clampedOffCss - ou.shadow.z");
    // The tanh form's coefficients, mirrored digit for digit from
    // `outerShadowFalloff` — the two evaluate one curve or they evaluate two.
    expect(WGSL_OPTICS_PASS).toContain("0.7978845608028654");
    expect(WGSL_OPTICS_PASS).toContain("0.044715");
  });

  it("emits premultiplied BLACK, which is what makes the composite a multiply", () => {
    // Outside the contour the pass returns `vec4f(0, 0, 0, alpha)`: zero colour
    // and the shadow's alpha. Over the page that is `page · (1 - alpha)` — the
    // multiplication — and over nothing it is nothing.
    expect(WGSL_OPTICS_PASS).toContain("return vec4f(0.0, 0.0, 0.0, shadowAlpha);");
    // And across the coverage ramp it fills whatever the surface's COVERAGE
    // leaves, rather than being switched off at the ramp and leaving a seam —
    // but only the coverage: a translucent surface (W11a's layer form) shows
    // the page through it, never its own shadow, exactly as a `box-shadow` is
    // clipped out of its border box.
    expect(WGSL_OPTICS_PASS).toContain("body.a + shadowAlpha * (1.0 - coverage)");
    expect(WGSL_OPTICS_PASS).not.toContain("shadowAlpha * (1.0 - body.a)");
  });

  it("declares the uniform it reads, so the pass and the shader cannot drift", () => {
    expect(WGSL_OPTICS_PASS).toContain("shadow : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("shadowSize : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("ou.shadowSize.x");
  });
});
