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
  OUTER_SHADOW_THIN_L,
  OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE,
  outerShadowAlpha,
  outerShadowFalloff,
  outerShadowLiftRise,
  outerShadowOcclusionAt,
  outerShadowReachPx,
  outerShadowThickOcclusion,
  outerShadowThinOcclusion,
  outerShadowUnderPolicy,
  sizeOuterShadowOcclusion,
  sizeOuterShadowOcclusionAt,
  sizeThickness,
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
    expect(worst * OUTER_SHADOW.thinOcclusionMid * 255).toBeLessThan(0.2);
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
    const alpha = outerShadowAlpha(OUTER_SHADOW.thinOcclusionMid);
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
    for (const occlusion of [0.06, 0.18, OUTER_SHADOW.thinOcclusionMid]) {
      expect(worstCodesAt(occlusion), `occlusion ${occlusion}`).toBeLessThan(3);
    }
    // And the honest shape of the limitation, rather than a bound chosen to hide
    // it: the residual grows with the amplitude, because the toe it comes from is
    // a larger share of a deeper shadow. A profile that fitted a much stronger
    // shadow than anything measured would pay more, and this says how much.
    expect(worstCodesAt(0.6)).toBeGreaterThan(worstCodesAt(OUTER_SHADOW.thinOcclusionMid));
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
  it("goes flat under reduced transparency at the measured level, not to six scaled anchors", () => {
    /*
     * MEASURED (claims §5.62 §5). Under increased contrast and reduced
     * transparency alike the reference's exterior is flat at 0.192–0.202 — thin
     * and thick together, over every backdrop it can be read on — so the
     * preference removes the material's adaptation and leaves ONE level. The
     * three lengths are unmoved; the shadow neither vanishes nor intensifies.
     */
    const nominal = outerShadowUnderPolicy(policy());
    expect(nominal).toEqual(OUTER_SHADOW);

    const reduced = outerShadowUnderPolicy(policy({ frost: "increased" }));
    // Every amplitude anchor becomes the same measured level, and the LIFT
    // stands down: a composite whose two regimes read one number has no second
    // term left in it.
    for (const key of [
      "thinOcclusionDark",
      "thinOcclusionMid",
      "thinOcclusionBright",
      "thickOcclusionAt96",
      "thickOcclusionAt128",
      "thickOcclusionAt160",
    ] as const) {
      expect(reduced[key], key).toBe(OUTER_SHADOW.reducedTransparencyOcclusion);
    }
    expect(reduced.liftAmplitude).toBe(0);
    expect(reduced.thinOcclusionMid).toBeCloseTo(0.197, 12);
    expect(reduced.thinOcclusionMid).toBeLessThan(nominal.thinOcclusionMid);

    /*
     * And the flatness is the point rather than a property of the anchors: the
     * resolved occlusion is that one level whatever the backdrop, the span and
     * the thickness are. A multiplier could not do this — it keeps exactly the
     * variation the preference removes, and 0.544 × 0.70 would put a span-160
     * surface at 0.38 against the reference's 0.20.
     */
    for (const backdrop of [0, 0.0117, 0.2141, 0.5, 0.891, 1]) {
      for (const span of [32, 44, 96, 128, 160, 4000]) {
        expect(
          outerShadowOcclusionAt(reduced, backdrop, span, sizeThickness(span)),
          `backdrop ${backdrop} / span ${span}`,
        ).toBeCloseTo(OUTER_SHADOW.reducedTransparencyOcclusion, 12);
      }
    }

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
    for (const flag of [{ glass: "none" }, { frost: "none" }] as const) {
      const off = outerShadowUnderPolicy(policy(flag));
      expect(outerShadowThinOcclusion(0.5, off), JSON.stringify(flag)).toBe(0);
      expect(outerShadowThickOcclusion(160, off)).toBe(0);
      expect(off.liftAmplitude).toBe(0);
    }
  });

  it("takes the preference's level from the profile that is drawing, not from the shipped one", () => {
    const patched = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      outerShadow: { thinOcclusionMid: 0.5, reducedTransparencyOcclusion: 0.25 },
    });
    // The patched level itself, not the patched level times anything: a profile
    // states what its material does under the preference, and the dark profile
    // states a different number from the light one because the two schemes'
    // materials cast different shadows.
    expect(
      outerShadowUnderPolicy(policy({ frost: "increased" }), patched).thinOcclusionMid,
    ).toBeCloseTo(0.25, 12);
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

  it("refuses a patch that still names W8's retired single amplitude", () => {
    /*
     * `{ outerShadow: { occlusion: 0 } }` was the way to stand the facet down,
     * and it is the shape a saved JSON profile or a JavaScript caller still has.
     * TypeScript rejects it at a call site that has types; nothing did at the
     * runtime boundary, so it merged into a patch that named no amplitude, was
     * hashed into a capture cell as the configuration that ran, and rendered the
     * DEFAULT shadow — the silently-measured-the-defaults failure, one level
     * below where the profile reader's guard was looking.
     *
     * It is refused rather than mapped: no value of a span-flat scalar is 0.33
     * below the knee and 0.544 above it, so a translation would be a reading
     * nobody took.
     */
    const retired = { outerShadow: { occlusion: 0 } } as unknown as Parameters<
      typeof withMaterialOverrides
    >[1];
    expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, retired)).toThrow(
      /outerShadow\.occlusion was retired/,
    );
    // The message has to name what replaced it, or the caller is told only that
    // their profile is wrong.
    expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, retired)).toThrow(
      /thinOcclusionMid.*thickOcclusionAt160.*liftAmplitude/s,
    );
    // And the six anchors themselves still merge, so the guard is on the retired
    // name rather than on the block.
    expect(
      withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { outerShadow: { thinOcclusionMid: 0 } })
        .outerShadow.thinOcclusionMid,
    ).toBe(0);
  });
});

describe("the shadow's reach sizes the rect the GPU tier draws into", () => {
  it("stops where the shadow stops moving a code, measured in the space it writes", () => {
    const reach = outerShadowReachPx(OUTER_SHADOW, OUTER_SHADOW.thinOcclusionMid);
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
    const alpha = outerShadowAlpha(OUTER_SHADOW.thinOcclusionMid);
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
      while (OUTER_SHADOW.thinOcclusionMid * outerShadowFalloff(d - 11.05, 15.55) * 255 > 1) {
        d += 0.01;
      }
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
    const base = outerShadowReachPx(OUTER_SHADOW, OUTER_SHADOW.thinOcclusionMid);

    const gained = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      outerShadow: { sizeGain: 1 },
    });
    const amplified = sizeOuterShadowOcclusionAt(OUTER_SHADOW.thinOcclusionMid, 1, gained);
    expect(amplified).toBe(1);
    const amplifiedReach = outerShadowReachPx(OUTER_SHADOW, amplified);
    expect(amplifiedReach).toBeGreaterThan(base);
    // The margin the base-amplitude pad would have sliced off.
    expect(amplifiedReach - base).toBeGreaterThan(4);

    // And the same for the amplitude the two REGIMES resolve to: a thick surface
    // over a mid backdrop occludes 0.379 where a thin one occludes 0.33, so a
    // pad taken from the thin regime alone would slice the thick member's shadow
    // (W14 G1).
    const thickOcc = outerShadowOcclusionAt(OUTER_SHADOW, 0.5, 160, 1);
    expect(thickOcc).toBeCloseTo(OUTER_SHADOW.thickOcclusionAt160, 12);
    expect(outerShadowReachPx(OUTER_SHADOW, thickOcc)).toBeGreaterThan(base);

    // Monotone in the amplitude, so a maximum over a group's members is a correct
    // upper bound however the gain is signed.
    let previous = 0;
    for (const occlusion of [0.05, 0.1, 0.2, 0.33, 0.5, 0.8, 1]) {
      const reach = outerShadowReachPx(OUTER_SHADOW, occlusion);
      expect(reach, `occlusion ${occlusion}`).toBeGreaterThanOrEqual(previous);
      previous = reach;
    }
  });

  it("is exactly zero when a profile declines the shadow, so nothing pays for it", () => {
    expect(outerShadowReachPx(OUTER_SHADOW, 0)).toBe(0);
    // And a shadow too faint to reach one code step anywhere is the same case.
    expect(outerShadowReachPx(OUTER_SHADOW, 1 / 512)).toBe(0);
  });

  it("grows with the blur, the offset and the spread", () => {
    const occ = OUTER_SHADOW.thinOcclusionMid;
    const base = outerShadowReachPx(OUTER_SHADOW, occ);
    expect(outerShadowReachPx({ ...OUTER_SHADOW, sigmaPx: 31.1 }, occ)).toBeGreaterThan(base);
    expect(
      outerShadowReachPx({ ...OUTER_SHADOW, offsetPx: OUTER_SHADOW.offsetPx + 10 }, occ),
    ).toBeCloseTo(base + 10, 6);
    expect(
      outerShadowReachPx({ ...OUTER_SHADOW, spreadPx: OUTER_SHADOW.spreadPx + 10 }, occ),
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
    const reach = outerShadowReachPx(OUTER_SHADOW, OUTER_SHADOW.thinOcclusionMid);

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
    expect(WGSL_OPTICS_PASS).toContain("fn outer_shadow(");
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
    // Outside the contour the pass returns `vec4f(lift, alpha)`. The BLACK term
    // is the alpha and nothing else — over the page that is `page · (1 - alpha)`,
    // the multiplication — and the lift is a separate premultiplied colour that
    // is exactly zero over a black backdrop and below the knee (W14 G1), so with
    // no lift the layer is premultiplied black again, byte for byte.
    expect(WGSL_OPTICS_PASS).toContain("return vec4f(liftEncoded, shadowAlpha);");
    // And across the coverage ramp BOTH terms fill whatever the surface's
    // COVERAGE leaves, rather than being switched off at the ramp and leaving a
    // seam — but only the coverage: a translucent surface (W11a's layer form)
    // shows the page through it, never its own shadow, exactly as a `box-shadow`
    // is clipped out of its border box.
    expect(WGSL_OPTICS_PASS).toContain("body.a + shadowAlpha * (1.0 - coverage)");
    expect(WGSL_OPTICS_PASS).toContain("body.rgb + liftEncoded * (1.0 - coverage)");
    expect(WGSL_OPTICS_PASS).not.toContain("shadowAlpha * (1.0 - body.a)");
  });

  it("declares the uniform it reads, so the pass and the shader cannot drift", () => {
    expect(WGSL_OPTICS_PASS).toContain("shadow : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("shadowSize : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("ou.shadowSize.x");
    // W14 G1's two new blocks, and every slot of them read.
    expect(WGSL_OPTICS_PASS).toContain("shadowThick : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("shadowLift : vec4f");
    expect(WGSL_OPTICS_PASS).toContain("ou.shadowThick.xyz");
    for (const slot of ["ou.shadowLift.x", "ou.shadowLift.y", "ou.shadowLift.z", "ou.shadowLift.w"]) {
      expect(WGSL_OPTICS_PASS, slot).toContain(slot);
    }
  });
});

/*
 * W14 G1 — the amplitude is a law and no longer a constant (claims §5.62).
 *
 * What these pin is again the MECHANISM and not the numbers: the thick anchors
 * and the lift's amplitude and reach are PROVISIONAL and the sweep sets them, so
 * the assertions are written against the profile's own constants wherever a
 * fitted value would otherwise be spelled out. What must not move unnoticed is
 * the shape: three anchors on the backdrop luminance below the knee, three on
 * the span above it, one knee shared with the face's response, and a second term
 * that is the backdrop's own light and is therefore nothing over black.
 */
describe("the outer shadow's amplitude adapts to the backdrop below the knee", () => {
  it("holds each measured anchor exactly, at the luminance it was measured at", () => {
    // The three backdrops the bed identifies, on the SAME statistic W9's face
    // response keys on: `mid-dark-solid` 0.0595 linear, `hc-text` 0.74, and
    // `light-solid` 0.891 — which are `backdropToneAnchorX`'s encoded 0.2706 and
    // 0.9505 decoded.
    expect(outerShadowThinOcclusion(OUTER_SHADOW_THIN_L.midFrom, OUTER_SHADOW)).toBe(
      OUTER_SHADOW.thinOcclusionMid,
    );
    expect(outerShadowThinOcclusion(OUTER_SHADOW_THIN_L.midTo, OUTER_SHADOW)).toBe(
      OUTER_SHADOW.thinOcclusionMid,
    );
    expect(outerShadowThinOcclusion(OUTER_SHADOW_THIN_L.bright, OUTER_SHADOW)).toBe(
      OUTER_SHADOW.thinOcclusionBright,
    );
    // Held beyond the bright anchor rather than extrapolated to zero: nothing was
    // measured past `light-solid` and a line through the last two anchors would
    // cross zero before white.
    expect(outerShadowThinOcclusion(1, OUTER_SHADOW)).toBe(OUTER_SHADOW.thinOcclusionBright);

    // The plateau really is flat across the four mid backdrops, which is the
    // measurement (0.327-0.347 pooled to one number), not an interpolation.
    for (const l of [0.06, 0.1, 0.214, 0.5, 0.7, 0.74]) {
      expect(outerShadowThinOcclusion(l, OUTER_SHADOW), `L ${l}`).toBe(
        OUTER_SHADOW.thinOcclusionMid,
      );
    }
  });

  it("is inert over black, and rises out of it by a smoothstep with a zero derivative", () => {
    expect(outerShadowThinOcclusion(0, OUTER_SHADOW)).toBe(0);
    expect(outerShadowThinOcclusion(OUTER_SHADOW_THIN_L.inert, OUTER_SHADOW)).toBe(0);
    // `dark-solid` (0.0039 linear) and `impulse` sit under the foot, so the
    // facet is exactly nothing there — the property W8 measured and W14 keeps.
    expect(outerShadowThinOcclusion(0.0039, OUTER_SHADOW)).toBe(0);

    // Smoothstep, not a step: the midpoint of the ramp is the midpoint of the
    // amplitude, and both ends leave flat.
    const mid = (OUTER_SHADOW_THIN_L.inert + OUTER_SHADOW_THIN_L.midFrom) / 2;
    expect(outerShadowThinOcclusion(mid, OUTER_SHADOW)).toBeCloseTo(
      OUTER_SHADOW.thinOcclusionMid / 2,
      12,
    );
    const foot = OUTER_SHADOW_THIN_L.inert + 1e-4;
    expect(outerShadowThinOcclusion(foot, OUTER_SHADOW)).toBeLessThan(
      OUTER_SHADOW.thinOcclusionMid * 1e-3,
    );
  });

  it("falls LINEARLY from the mid plateau to the bright anchor, which is a declared choice", () => {
    /*
     * The bed jumps from `hc-text` (0.74) to `light-solid` (0.891) with nothing
     * between, and the whole factor-of-2.6 drop happens in that gap — W14's
     * Deferred list says one backdrop between them would pin it. A straight line
     * is the least-committed curve through two endpoints, and this is the test
     * that has to be revisited when that cell exists.
     */
    const { midTo, bright } = OUTER_SHADOW_THIN_L;
    for (const t of [0.25, 0.5, 0.75]) {
      const l = midTo + (bright - midTo) * t;
      expect(outerShadowThinOcclusion(l, OUTER_SHADOW), `t ${t}`).toBeCloseTo(
        OUTER_SHADOW.thinOcclusionMid +
          (OUTER_SHADOW.thinOcclusionBright - OUTER_SHADOW.thinOcclusionMid) * t,
        12,
      );
    }
  });

  it("reads the mid plateau where the host measured no backdrop at all", () => {
    // Not black, which would delete the facet on every unsampled surface, and not
    // white, which would halve it. Both tiers fall back to the same constant so
    // they cannot diverge on an unsampled group.
    expect(outerShadowThinOcclusion(undefined, OUTER_SHADOW)).toBe(
      outerShadowThinOcclusion(OUTER_SHADOW_UNMEASURED_BACKDROP_LUMINANCE, OUTER_SHADOW),
    );
    expect(outerShadowThinOcclusion(undefined, OUTER_SHADOW)).toBe(
      OUTER_SHADOW.thinOcclusionMid,
    );
  });

  it("rises once out of black and falls once into the light, and never doubles back", () => {
    /*
     * The curve is not monotone over the whole axis and should not be: it climbs
     * out of the inert foot to the plateau and falls from the plateau to the
     * bright anchor. What must hold is that it does each of those exactly once,
     * so no backdrop between two others casts a deeper shadow than both.
     */
    let previous = -1;
    for (let l = 0; l <= OUTER_SHADOW_THIN_L.midFrom; l += 0.0005) {
      const value = outerShadowThinOcclusion(l, OUTER_SHADOW);
      expect(value, `rising at L ${l}`).toBeGreaterThanOrEqual(previous - 1e-12);
      previous = value;
    }
    previous = Infinity;
    for (let l = OUTER_SHADOW_THIN_L.midFrom; l <= 1; l += 0.002) {
      const value = outerShadowThinOcclusion(l, OUTER_SHADOW);
      expect(value, `falling at L ${l}`).toBeLessThanOrEqual(previous + 1e-12);
      previous = value;
    }
  });
});

describe("the outer shadow's amplitude above the knee is a span law", () => {
  it("passes through the three measured anchors and is held outside them", () => {
    expect(outerShadowThickOcclusion(96, OUTER_SHADOW)).toBe(OUTER_SHADOW.thickOcclusionAt96);
    expect(outerShadowThickOcclusion(128, OUTER_SHADOW)).toBe(OUTER_SHADOW.thickOcclusionAt128);
    expect(outerShadowThickOcclusion(160, OUTER_SHADOW)).toBe(OUTER_SHADOW.thickOcclusionAt160);
    expect(outerShadowThickOcclusion(0, OUTER_SHADOW)).toBe(OUTER_SHADOW.thickOcclusionAt96);
    expect(outerShadowThickOcclusion(4000, OUTER_SHADOW)).toBe(OUTER_SHADOW.thickOcclusionAt160);
  });

  it("is piecewise linear between them", () => {
    expect(outerShadowThickOcclusion(112, OUTER_SHADOW)).toBeCloseTo(
      (OUTER_SHADOW.thickOcclusionAt96 + OUTER_SHADOW.thickOcclusionAt128) / 2,
      12,
    );
    expect(outerShadowThickOcclusion(144, OUTER_SHADOW)).toBeCloseTo(
      (OUTER_SHADOW.thickOcclusionAt128 + OUTER_SHADOW.thickOcclusionAt160) / 2,
      12,
    );
  });

  it("blends out of the thin regime on the SAME knee the face's response uses", () => {
    /*
     * The charter's third binding rule, read from the other side: the shadow's
     * thin/thick crossover is `smoothstep(sizeThickness(span))`, which is exactly
     * what `backdropToneResponse` blends its own thin and thick rows across. One
     * knee for the face and the shadow, or the material grows two.
     */
    const l = 0.5;
    const blendAt = (span: number): number => {
      const k = sizeThickness(span);
      return k * k * (3 - 2 * k);
    };
    for (const span of [0, 32, 44, 64, 80, 96, 160]) {
      const f = blendAt(span);
      const expected =
        OUTER_SHADOW.thinOcclusionMid +
        (outerShadowThickOcclusion(span, OUTER_SHADOW) - OUTER_SHADOW.thinOcclusionMid) * f;
      expect(
        outerShadowOcclusionAt(OUTER_SHADOW, l, span, sizeThickness(span)),
        `span ${span}`,
      ).toBeCloseTo(expected, 12);
    }
    // Below `sizeSpanMin` the thin regime is the whole answer, and at
    // `sizeSpanMax` the thick one is.
    expect(outerShadowOcclusionAt(OUTER_SHADOW, l, 32, sizeThickness(32))).toBeCloseTo(
      OUTER_SHADOW.thinOcclusionMid,
      12,
    );
    expect(outerShadowOcclusionAt(OUTER_SHADOW, l, 96, sizeThickness(96))).toBeCloseTo(
      OUTER_SHADOW.thickOcclusionAt96,
      12,
    );
  });

  it("stays inert over black at every span, because both regimes end at zero there", () => {
    // The thick regime is a composite fitted on the checkerboard, and a composite
    // over black is nothing: the black term removes nothing and the lift adds
    // nothing. The BLEND has to preserve that or `dark-solid` and `impulse` move.
    const dark = outerShadowUnderPolicy(policy(), {
      ...DEFAULT_MATERIAL_PROFILE,
      outerShadow: {
        ...OUTER_SHADOW,
        thickOcclusionAt96: 0,
        thickOcclusionAt128: 0,
        thickOcclusionAt160: 0,
      },
    });
    for (const span of [32, 64, 96, 160]) {
      expect(
        outerShadowOcclusionAt(dark, 0.001, span, sizeThickness(span)),
        `span ${span}`,
      ).toBe(0);
    }
  });

  it("folds the size gain last, on the remaining transparency", () => {
    const gained = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      outerShadow: { sizeGain: 0.5 },
    });
    const resolved = outerShadowOcclusionAt(gained.outerShadow, 0.5, 160, 1, gained);
    const before = OUTER_SHADOW.thickOcclusionAt160;
    expect(resolved).toBeCloseTo(before + 0.5 * (1 - before), 12);
    // And the shipped gain of 0 leaves the law exactly alone.
    expect(outerShadowOcclusionAt(OUTER_SHADOW, 0.5, 160, 1)).toBeCloseTo(before, 12);
  });
});

describe("the lift is the backdrop's own light, above the knee", () => {
  it("is zero at and below the knee and saturated at the reach", () => {
    expect(outerShadowLiftRise(0, OUTER_SHADOW)).toBe(0);
    expect(outerShadowLiftRise(32, OUTER_SHADOW)).toBe(0);
    expect(outerShadowLiftRise(44, OUTER_SHADOW)).toBe(0);
    expect(outerShadowLiftRise(OUTER_SHADOW.liftSpanMin, OUTER_SHADOW)).toBe(0);
    expect(outerShadowLiftRise(OUTER_SHADOW.liftSpanFull, OUTER_SHADOW)).toBe(1);
    expect(outerShadowLiftRise(4000, OUTER_SHADOW)).toBe(1);
    // The knee is EXACT at 64: the bed reads 0.0000 at spans 32 and 44 and a lift
    // at 96, and the layer tree's own clamp starts from the same number.
    expect(OUTER_SHADOW.liftSpanMin).toBe(64);
  });

  it("rises monotonically and saturates well before the bed's largest span", () => {
    let previous = -1;
    for (let span = 0; span <= 200; span += 1) {
      const rise = outerShadowLiftRise(span, OUTER_SHADOW);
      expect(rise, `span ${span}`).toBeGreaterThanOrEqual(previous);
      previous = rise;
    }
    // The measurement the shape is taken from: 0.52 of the span-160 value at 96
    // and 0.96 at 128, against the layer tree's clamp((span - 64)/96) = 0.33 and
    // 0.67 — the lift saturates and is NOT proportional to
    // `VibrancyContribution` (claims §5.62 §2). PROVISIONAL: the sweep fits the
    // reach, so this holds the direction rather than the numbers.
    expect(outerShadowLiftRise(96, OUTER_SHADOW)).toBeGreaterThan((96 - 64) / 96);
    expect(outerShadowLiftRise(128, OUTER_SHADOW)).toBeGreaterThan((128 - 64) / 96);
  });

  it("is nothing over black, by construction rather than by a branch", () => {
    /*
     * The whole term is `liftAmplitude · rise(span) · falloff(d) · V`, with `V`
     * the blurred backdrop's own light. Over `impulse` and `dark-solid` V is
     * zero, so the product is zero at every span and every distance — which is
     * why those cells stay byte-identical to their background with the second
     * term landed, exactly as they did with only the multiply.
     */
    const lift = (v: number, span: number, d: number): number =>
      OUTER_SHADOW.liftAmplitude *
      outerShadowLiftRise(span, OUTER_SHADOW) *
      outerShadowFalloff(d, OUTER_SHADOW.sigmaPx) *
      v;
    for (const span of [64, 96, 128, 160]) {
      for (const d of [-20, 0, 20]) {
        expect(lift(0, span, d), `span ${span} at ${d}`).toBe(0);
      }
    }
    // And it reproduces G0's own reading where the backdrop is not black: the
    // checkerboard's sigma-40 blur sits at 0.52 linear, and the ring below a
    // span-160 surface lifts 0.0038 in linear light (claims §5.62 §2-3).
    expect(lift(0.52, 160, -40)).toBeCloseTo(0.0038, 4);
  });

  it("rides the SAME falloff as the black term, not a second geometry", () => {
    // G0's free four-parameter fits return W8's lengths for both terms (sigma
    // 14.8-16.2 / offset 7.93-8.00 for the multiply, 14.1-17.1 / 7.6-8.4 for the
    // lift), and their shapes correlate at 0.9998. One function, evaluated once
    // per pixel — the shader takes `shadow.falloff` and multiplies both terms by
    // it.
    expect(WGSL_OPTICS_PASS).toContain("out.falloff = outer_shadow_falloff(");
    expect(WGSL_OPTICS_PASS).toContain("shadow.falloff");
    expect(WGSL_OPTICS_PASS.match(/outer_shadow_falloff\(/g)?.length).toBe(2);
  });

  it("samples the chain at the pixel's own position, at the CPU-resolved level", () => {
    /*
     * The copy is of the backdrop BENEATH the shadow, not of the backdrop under
     * the surface, so the sample is at `viewport01` through the chain's own fit
     * and never at the refracted position. The chain's transform is on
     * viewport-normalised coordinates and covers the whole viewport, so — unlike
     * the field texture, whose offset shift the shader has to reconstruct off the
     * top of — every pixel this pass draws has a valid sample and there is
     * nothing to clamp.
     */
    expect(WGSL_OPTICS_PASS).toContain("fn outer_shadow_lift(");
    expect(WGSL_OPTICS_PASS).toContain("clamp(viewport01 * ou.fit.xy + ou.fit.zw");
    expect(WGSL_OPTICS_PASS).toContain(
      "textureSampleLevel(backdropChain, backdropSampler, uv, ou.shadowLift.w)",
    );
    // And it stands down where the group has no chain to copy.
    expect(WGSL_OPTICS_PASS).toContain("ou.flags.x <= 0.5 || ou.shadowLift.x <= 0.0");
  });
});
