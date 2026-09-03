/**
 * The size law's shape — the properties, not the fitted numbers (W2).
 *
 * The numbers live in the profile and move whenever the bed is re-measured; what
 * must not move is the *shape*, because the shape is what the claim is about.
 * Apple states one mechanism — as glass grows it "simulates a thicker, more
 * substantial material", casting deeper shadows, lensing harder, scattering more
 * softly and reading more opaque — so four properties are pinned here:
 *
 *  1. **One curve.** Every facet is a gain on `sizeThickness` and on nothing else,
 *     so a profile that flattens the curve flattens all four together. Two curves
 *     would be two mechanisms.
 *  2. **Monotone.** No facet may go backwards as a surface grows. A law that
 *     un-thickens somewhere in the middle is not the law Apple describes, and a
 *     smoothstep's own monotonicity is easy to lose behind an added term.
 *  3. **Inert below the band.** At or under `sizeSpanMin` every facet is exactly
 *     what it was before the law existed. That is what makes the law additive:
 *     a 44 px button's pixels did not move because a platter's had to.
 *  4. **Saturating.** At or over `sizeSpanMax` every facet is exactly its maximum,
 *     so nothing keeps growing off the end of a full-width platter.
 *
 * The fitted values are asserted nowhere here on purpose. `tuned-profiles.test.ts`
 * in the calibration package is where a number earns its place, against the bed.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  lensDepthPx,
  lensSizeGain,
  lensSizeGainFromThickness,
  NOMINAL_MATERIAL_POLICY,
  occlusionAlphaUnderPolicy,
  sizeOcclusionAlpha,
  sizeOuterShadowOcclusion,
  sizeOcclusionAlphaAt,
  sizeScatterSigma,
  sizeScatterSigmaAt,
  scatterRampAreaMean,
  scatterDeepThickness,
  scatterFloorAtScale,
  scatterGainAtScale,
  scatterSpanMaxAtScale,
  scatterRampReachDevicePx,
  scatterRampStart,
  scatterSharpShare,
  scatterThickness,
  sizeShadowDepth,
  sizeShadowDepthAt,
  sizeThickness,
  sizeThicknessUnderPolicy,
  withMaterialOverrides,
  type MaterialPolicyView,
  type MaterialProfile,
} from "../src/material";
import { packInstances, resolveSurfaces, INSTANCE_FLOATS } from "../src/instances";
import { chainLodForSigma, CHAIN_SIGMA_AT_LEVEL_1 } from "../src/pyramid-plan";
import type { GroupRenderInput, SurfaceInput } from "../src/render-model";

/** A profile whose every gain is real, so a term that is ignored shows up. */
const GAINED: MaterialProfile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
  sizeSpanMin: 40,
  sizeSpanMax: 200,
  lensSizeGainMax: 3,
  sizeScatterGainMax: 2.5,
  // The scatter facet rides neither the thickness band nor a span curve since
  // W13 — it is a ramp in depth, and it has its own describe further down. The
  // floor is off here so that a profile with every gain real still turns the
  // whole facet off when `sizeScatterGainMax` is 1.
  sizeScatterFloor: 0,
  sizeOcclusionGain: 0.4,
  sizeShadowGainMax: 1.8,
  outerShadow: { sizeGain: 0.6 },
});

const SPANS = [0, 1, 20, 40, 41, 60, 96, 120, 199, 200, 201, 400, 4000];

describe("the size curve", () => {
  it("is zero at and below the band, one at and above it", () => {
    expect(sizeThickness(0, GAINED)).toBe(0);
    expect(sizeThickness(40, GAINED)).toBe(0);
    expect(sizeThickness(200, GAINED)).toBe(1);
    expect(sizeThickness(4000, GAINED)).toBe(1);
  });

  it("rises monotonically across the band", () => {
    let previous = -1;
    for (const span of SPANS) {
      const t = sizeThickness(span, GAINED);
      expect(t, `span ${span}`).toBeGreaterThanOrEqual(previous);
      expect(t).toBeGreaterThanOrEqual(0);
      expect(t).toBeLessThanOrEqual(1);
      previous = t;
    }
  });

  it("degenerates safely when a profile collapses the band to a point", () => {
    const collapsed = withMaterialOverrides(GAINED, { sizeSpanMin: 100, sizeSpanMax: 100 });
    expect(sizeThickness(99, collapsed)).toBe(0);
    expect(sizeThickness(100, collapsed)).toBe(1);
  });
});

describe("every thickness-derived facet rides that one curve", () => {
  const facets: readonly {
    readonly name: string;
    readonly at: (span: number) => number;
    readonly nominal: number;
    readonly saturated: number;
  }[] = [
    {
      // W2's lens gain, which the inner shadow's depth keeps riding after the
      // lens took the reference's own span law (W12 G2).
      name: "inner-shadow depth",
      at: (span) => lensSizeGain(span, GAINED),
      nominal: 1,
      saturated: GAINED.lensSizeGainMax,
    },
    // The scattering is deliberately NOT in this table. Since W13 G1 it rides a
    // ramp in depth rather than the thickness band (claims §5.61 §2), so "inert
    // below the band, saturated above it" is not a property it has; its own
    // describe below states the properties it does have.
    {
      name: "occlusion",
      at: (span) => sizeOcclusionAlpha(0.5, span, GAINED),
      nominal: 0.5,
      saturated: 0.5 + GAINED.sizeOcclusionGain * 0.5,
    },
    {
      name: "inner shadow",
      at: (span) => sizeShadowDepth(0.35, span, GAINED),
      nominal: 0.35,
      saturated: 0.35 * GAINED.sizeShadowGainMax,
    },
    {
      // W8. The outer shadow's AMPLITUDE is the only part of it a span may move:
      // its offset, blur and spread are span-invariant in the reference across
      // 32…160 px, which is a measurement rather than an omission.
      name: "outer shadow",
      at: (span) => sizeOuterShadowOcclusion(0.33, span, GAINED),
      nominal: 0.33,
      saturated: 0.33 + GAINED.outerShadow.sizeGain * (1 - 0.33),
    },
  ];

  for (const facet of facets) {
    it(`${facet.name}: inert below the band, saturated above it, monotone between`, () => {
      expect(facet.at(0), "below").toBeCloseTo(facet.nominal, 12);
      expect(facet.at(GAINED.sizeSpanMin), "at the floor").toBeCloseTo(facet.nominal, 12);
      expect(facet.at(GAINED.sizeSpanMax), "at the ceiling").toBeCloseTo(facet.saturated, 12);
      expect(facet.at(4000), "far above").toBeCloseTo(facet.saturated, 12);

      let previous = -Infinity;
      for (const span of SPANS) {
        const value = facet.at(span);
        expect(value, `${facet.name} at span ${span}`).toBeGreaterThanOrEqual(previous - 1e-12);
        previous = value;
      }
      // The point of a *gain*: a larger surface is strictly further along than a
      // smaller one inside the band, not merely not-behind it.
      expect(facet.at(120)).toBeGreaterThan(facet.at(60));
    });
  }

  it("goes inert as one when the profile turns every gain off", () => {
    const off = withMaterialOverrides(GAINED, {
      lensSizeGainMax: 1,
      sizeScatterGainMax: 1,
      sizeOcclusionGain: 0,
      sizeShadowGainMax: 1,
      outerShadow: { sizeGain: 0 },
    });
    for (const span of SPANS) {
      expect(lensSizeGain(span, off)).toBeCloseTo(1, 12);
      expect(sizeScatterSigma(8, span, off)).toBeCloseTo(8, 12);
      expect(sizeOcclusionAlpha(0.5, span, off)).toBeCloseTo(0.5, 12);
      expect(sizeShadowDepth(0.35, span, off)).toBeCloseTo(0.35, 12);
      expect(sizeOuterShadowOcclusion(0.33, span, off)).toBeCloseTo(0.33, 12);
    }
  });
});

/*
 * The fold, and it is here because leaving it out broke two adopted gates.
 *
 * The law was first landed unfolded and the full regeneration caught it: under
 * both accessibility profiles the large-span cells' ΔE crossed their bounds while
 * every light-standard cell improved. Under reduce-transparency Apple's material
 * is nearly opaque and its interior level is flat in span, so there is no depth
 * there for a size term to add — which is the same rule the rest of the material
 * already follows and the law was skipping.
 */
describe("the size law folds under the accessibility regime", () => {
  const under = (refraction: MaterialPolicyView["refraction"]): MaterialPolicyView => ({
    ...NOMINAL_MATERIAL_POLICY,
    refraction,
  });

  it("scales the whole law by the profile's own refraction ladder", () => {
    const full = sizeThickness(4000, GAINED);
    expect(sizeThicknessUnderPolicy(4000, under("nominal"), GAINED)).toBeCloseTo(full, 12);
    expect(sizeThicknessUnderPolicy(4000, under("reduced"), GAINED)).toBeCloseTo(
      full * GAINED.refractionScale.approximate,
      12,
    );
    expect(sizeThicknessUnderPolicy(4000, under("none"), GAINED)).toBe(0);
  });

  it("takes one fold, so every facet weakens together", () => {
    // The property that makes it one law: a regime that halves the thickness
    // halves what each facet adds, and none of them can be folded and another not.
    const reduced = sizeThicknessUnderPolicy(4000, under("reduced"), GAINED);
    const full = sizeThicknessUnderPolicy(4000, under("nominal"), GAINED);
    for (const [at, nominal] of [
      [(t: number) => lensSizeGainFromThickness(t, GAINED), 1],
      [(t: number) => sizeScatterSigmaAt(8, t, GAINED), 8],
      [(t: number) => sizeOcclusionAlphaAt(0.5, t, GAINED), 0.5],
      [(t: number) => sizeShadowDepthAt(0.35, t, GAINED), 0.35],
    ] as const) {
      const added = (t: number) => at(t) - nominal;
      expect(added(reduced)).toBeCloseTo(
        added(full) * GAINED.refractionScale.approximate,
        12,
      );
    }
  });

  it("reaches the surfaces, so a preference really does un-thicken a platter", () => {
    const platter = {
      groupId: "g",
      refraction: "true" as const,
      analysisExact: false,
      surfaces: [
        {
          nodeId: "platter",
          family: "fixed-rounded-rect" as const,
          shape: {
            center: [200, 200] as const,
            size: [400, 280] as const,
            radii: [8, 8, 8, 8] as const,
            smoothing: 0,
            thickness: 8,
          },
          reference: "figma-smoothing" as const,
        },
      ],
    };
    const nominal = resolveSurfaces(platter, "rsupn", GAINED, under("nominal"));
    const reduced = resolveSurfaces(platter, "rsupn", GAINED, under("reduced"));
    const none = resolveSurfaces(platter, "rsupn", GAINED, under("none"));

    expect(nominal[0]?.sizeThickness).toBe(1);
    expect(reduced[0]?.sizeThickness).toBeCloseTo(GAINED.refractionScale.approximate, 12);
    expect(none[0]?.sizeThickness).toBe(0);
    // And the lens depth follows, because it reads the same folded factor.
    expect(nominal[0]?.lensDepthPx).toBeGreaterThan(reduced[0]?.lensDepthPx as number);
    expect(reduced[0]?.lensDepthPx).toBeGreaterThan(none[0]?.lensDepthPx as number);
    // At `none` the surface is back to its authored thickness and nothing more.
    expect(none[0]?.lensDepthPx).toBeCloseTo(8, 12);
  });

  it("does not fold a group that was merely demoted", () => {
    // The dual cap's other half is the group's sampling capability, and it is
    // deliberately not read here: a group on a CSS proxy is drawing the same
    // material as one on a texture, and being demoted is not a statement about
    // how thick that material is.
    const demoted = {
      groupId: "g",
      refraction: "approximate" as const,
      analysisExact: false,
      surfaces: [
        {
          nodeId: "platter",
          family: "fixed-rounded-rect" as const,
          shape: {
            center: [200, 200] as const,
            size: [400, 280] as const,
            radii: [8, 8, 8, 8] as const,
            smoothing: 0,
            thickness: 8,
          },
          reference: "figma-smoothing" as const,
        },
      ],
    };
    expect(resolveSurfaces(demoted, "rsupn", GAINED, under("nominal"))[0]?.sizeThickness).toBe(1);
  });
});

describe("the occlusion facet composes with the accessibility lift", () => {
  /*
   * Decision Log #32(d)'s lesson, applied to a second lift: both close a fraction
   * of whatever transparency is left, so neither can cancel the other and neither
   * can push past opaque — which is what stops the size law from quietly undoing
   * a preference, or a preference from making the size law inert.
   */
  it("lifts strictly, from any nominal, in either order", () => {
    for (const nominal of [0, 0.05, 0.28, 0.62, 0.9, 0.999]) {
      const sizeThenPolicy = occlusionAlphaUnderPolicy(
        sizeOcclusionAlpha(nominal, 4000, GAINED),
        "increased",
        GAINED.increasedOcclusionLift,
      );
      const policyThenSize = sizeOcclusionAlpha(
        occlusionAlphaUnderPolicy(nominal, "increased", GAINED.increasedOcclusionLift),
        4000,
        GAINED,
      );
      expect(sizeThenPolicy, `nominal ${nominal}`).toBeGreaterThan(nominal);
      expect(policyThenSize, `nominal ${nominal}`).toBeGreaterThan(nominal);
      expect(sizeThenPolicy).toBeLessThanOrEqual(1);
      expect(policyThenSize).toBeLessThanOrEqual(1);
      // Two fractions of the same headroom commute exactly.
      expect(sizeThenPolicy).toBeCloseTo(policyThenSize, 12);
    }
  });

  it("has nothing left to close on an already-opaque material", () => {
    expect(sizeOcclusionAlpha(1, 4000, GAINED)).toBe(1);
  });
});

/*
 * The body's depth ramp (W13 G1, from the measurement of claims §5.61 §2), and
 * the device-pixel widths it lands with (§5.56 §1, verified §5.58 §2).
 *
 * Four properties are asserted rather than described: the ramp's own shape, its
 * interpolation between the two scales the reference was read at, the fold
 * identity that carries `sizeScatterFloor`'s W11c semantics onto the new law,
 * and the area average — checked against a quadrature rather than against a
 * restatement of the closed form, so an algebra slip cannot pass by agreeing
 * with itself.
 */
describe("the body's mix is a span curve with a ramp in depth on it (W13 G1)", () => {
  const SHIPPED = DEFAULT_MATERIAL_PROFILE;
  const SIGMA = SHIPPED.optics.regular.blurSigma;
  /**
   * The same law with no frost under it, so the span curve runs the whole 0…1
   * and the ramp has an excursion to make at every span — which is the case a
   * quadrature can see the closed form's algebra in.
   */
  const RAMP: MaterialProfile = withMaterialOverrides(SHIPPED, { sizeScatterFloor: 0 });

  /**
   * The area average by midpoint quadrature over the same rectangle erosion the
   * closed form integrates: `k̄ = 1 − (1/WH) ∫ s(u, span)(P − 8u) du`. Written
   * from `scatterSharpShare` — the law itself — so an algebra slip in the closed
   * form cannot pass by agreeing with a restatement of itself.
   */
  const quadrature = (
    width: number,
    height: number,
    dpr: number,
    profile: MaterialProfile,
  ): number => {
    const span = Math.min(width, height);
    const deepest = span / 2;
    const perimeter = 2 * (width + height);
    const steps = 200000;
    let sum = 0;
    for (let i = 0; i < steps; i += 1) {
      const u = ((i + 0.5) / steps) * deepest;
      sum += scatterSharpShare(u * dpr, dpr, profile, span) * (perimeter - 8 * u);
    }
    return 1 - (sum * (deepest / steps)) / (width * height);
  };

  it("sits on the span curve deep inside and rises to s₀ at the contour", () => {
    for (const dpr of [1, 1.5, 2, 3]) {
      const reach = scatterRampReachDevicePx(dpr, SHIPPED);
      for (const span of [32, 96, 160, 256, 400]) {
        // The start grades with the span too, since the third form (§5.64 §5),
        // so it is read per span rather than once per scale.
        const start = scatterRampStart(dpr, SHIPPED, span);
        const deepSharp = 1 - scatterDeepThickness(span, SHIPPED);
        const label = `span ${span} at dpr ${dpr}`;
        // Deeper than the reach the body is exactly the W11c/W12 material.
        expect(scatterSharpShare(reach, dpr, SHIPPED, span), label).toBeCloseTo(deepSharp, 12);
        expect(scatterSharpShare(reach * 4, dpr, SHIPPED, span), label).toBeCloseTo(deepSharp, 12);
        // At the contour it is the start, or the deep value where the deep value
        // is already the sharper of the two and the excursion clamps off.
        expect(scatterSharpShare(0, dpr, SHIPPED, span), label).toBeCloseTo(
          Math.max(start, deepSharp),
          12,
        );
        // Halfway to the reach it is halfway between them.
        expect(scatterSharpShare(reach / 2, dpr, SHIPPED, span), label).toBeCloseTo(
          deepSharp + Math.max(start - deepSharp, 0) / 2,
          12,
        );
        // Outside the contour the field's distance is positive; the share is
        // clamped there rather than extrapolated past the start.
        expect(scatterSharpShare(-40, dpr, SHIPPED, span), label).toBeCloseTo(
          scatterSharpShare(0, dpr, SHIPPED, span),
          12,
        );
      }
    }
  });

  it("keeps the span curve W11c fitted as its deep value", () => {
    // Byte for byte the law the first form retired and the sweep asked back
    // (`results/2026-09-03-w13-ramp/g1/sweep/g1-sweep.md` §4, §7).
    const floor = SHIPPED.sizeScatterFloor;
    expect(scatterDeepThickness(0, SHIPPED)).toBeCloseTo(floor, 12);
    expect(scatterDeepThickness(SHIPPED.sizeSpanMin, SHIPPED)).toBeCloseTo(floor, 12);
    expect(scatterDeepThickness(SHIPPED.sizeScatterSpanMax, SHIPPED)).toBeCloseTo(1, 12);
    expect(scatterDeepThickness(4000, SHIPPED)).toBeCloseTo(1, 12);
    const mid = (SHIPPED.sizeSpanMin + SHIPPED.sizeScatterSpanMax) / 2;
    expect(scatterDeepThickness(mid, SHIPPED)).toBeCloseTo(floor + (1 - floor) * 0.5, 12);
    // And it is span-graded where the ramp alone was span-flat: 0.41 to 1.00
    // across the bed, which is the mechanism §4 named.
    expect(scatterDeepThickness(44, SHIPPED)).toBeLessThan(0.42);
    expect(scatterDeepThickness(280, SHIPPED)).toBe(1);
    // The deep value does not depend on the device scale; only the excursion does.
    for (const dpr of [1, 2, 3]) {
      expect(scatterSharpShare(1e6, dpr, SHIPPED, 160)).toBeCloseTo(
        1 - scatterDeepThickness(160, SHIPPED),
        12,
      );
    }
  });

  it("interpolates the two anchors linearly in dpr and holds outside them", () => {
    // Read at the two ends of the span grading: `sizeSpanMin` is the thin
    // anchor exactly and `sizeSpanMax` the thick one exactly, because
    // `sizeThickness` is 0 and 1 there.
    const THIN = SHIPPED.sizeSpanMin;
    const THICK = SHIPPED.sizeSpanMax;
    expect(scatterRampStart(1, SHIPPED, THIN)).toBe(SHIPPED.sizeScatterRampStartThin1x);
    expect(scatterRampStart(2, SHIPPED, THIN)).toBe(SHIPPED.sizeScatterRampStartThin2x);
    expect(scatterRampStart(1, SHIPPED, THICK)).toBeCloseTo(
      SHIPPED.sizeScatterRampStartThick1x,
      12,
    );
    expect(scatterRampStart(2, SHIPPED, THICK)).toBeCloseTo(
      SHIPPED.sizeScatterRampStartThick2x,
      12,
    );
    expect(scatterRampStart(1.5, SHIPPED, THIN)).toBeCloseTo(
      (SHIPPED.sizeScatterRampStartThin1x + SHIPPED.sizeScatterRampStartThin2x) / 2,
      12,
    );
    expect(scatterRampReachDevicePx(1, SHIPPED)).toBe(SHIPPED.sizeScatterRampReach1xPx);
    expect(scatterRampReachDevicePx(2, SHIPPED)).toBe(SHIPPED.sizeScatterRampReach2xPx);
    expect(scatterRampReachDevicePx(1.25, SHIPPED)).toBeCloseTo(
      SHIPPED.sizeScatterRampReach1xPx * 0.75 + SHIPPED.sizeScatterRampReach2xPx * 0.25,
      12,
    );
    // Held rather than extrapolated: the reference was read at 1 and at 2.
    for (const dpr of [2.5, 3, 4]) {
      expect(scatterRampStart(dpr, SHIPPED, THIN)).toBe(SHIPPED.sizeScatterRampStartThin2x);
      expect(scatterRampReachDevicePx(dpr, SHIPPED)).toBe(SHIPPED.sizeScatterRampReach2xPx);
    }
    expect(scatterRampStart(0.5, SHIPPED, THIN)).toBe(SHIPPED.sizeScatterRampStartThin1x);
  });

  it("grades the start along the material's own thin/thick curve", () => {
    // The third form's whole change (claims §5.64 §5): one start per scale
    // could not be above `rrect-sm`'s deep sharp share of 0.600 and below
    // `rrect-ml`'s crossing near 0.583 at once. The start now rides
    // `sizeThickness` — the SAME curve the lens, the occlusion and the tone
    // response ride, so no new span statistic enters the material — and, since
    // the fourth form, keeps falling above the knee along the scatter span
    // curve to `far` (claims §5.67 §4): both terms are asserted here.
    const decline = (span: number): number => {
      const t = Math.min(
        1,
        Math.max(0, (span - SHIPPED.sizeSpanMax) / (SHIPPED.sizeScatterSpanMax - SHIPPED.sizeSpanMax)),
      );
      return t * t * (3 - 2 * t);
    };
    for (const dpr of [1, 1.5, 2]) {
      const thin = scatterRampStart(dpr, SHIPPED, 0);
      const thick = scatterRampStart(dpr, SHIPPED, SHIPPED.sizeSpanMax);
      const far = scatterRampStart(dpr, SHIPPED, SHIPPED.sizeScatterSpanMax);
      for (const span of SPANS) {
        expect(scatterRampStart(dpr, SHIPPED, span), `span ${span} at ${dpr}`).toBeCloseTo(
          thin + (thick - thin) * sizeThickness(span, SHIPPED) + (far - thick) * decline(span),
          12,
        );
      }
      // Monotone down from thin through thick to far, and flat past the top.
      let previous = Infinity;
      for (const span of [0, 16, 32, 44, 64, 80, 96, 160, 256, 4000]) {
        const start = scatterRampStart(dpr, SHIPPED, span);
        expect(start, `span ${span} at ${dpr}`).toBeLessThanOrEqual(previous + 1e-12);
        previous = start;
      }
      expect(scatterRampStart(dpr, SHIPPED, 0)).toBe(scatterRampStart(dpr, SHIPPED, 32));
      expect(scatterRampStart(dpr, SHIPPED, SHIPPED.sizeScatterSpanMax)).toBeCloseTo(
        scatterRampStart(dpr, SHIPPED, 4000),
        12,
      );
    }
  });

  it("folds to the floor exactly at 0 and to the law exactly at 1", () => {
    for (const span of [0, 12, 32, 44, 96, 128, 160, 256, 4000]) {
      for (const dpr of [1, 1.5, 2, 3]) {
        const mean = scatterRampAreaMean(span, SHIPPED, dpr);
        expect(scatterThickness(span, 0, SHIPPED, dpr), `span ${span}`).toBeCloseTo(
          SHIPPED.sizeScatterFloor,
          12,
        );
        expect(scatterThickness(span, 1, SHIPPED, dpr), `span ${span}`).toBeCloseTo(mean, 12);
        expect(scatterThickness(span, 0.5, SHIPPED, dpr)).toBeCloseTo(
          SHIPPED.sizeScatterFloor + (mean - SHIPPED.sizeScatterFloor) * 0.5,
          12,
        );
      }
    }
  });

  it("projects the law onto the surface's area, and the closed form is the integral", () => {
    for (const profile of [RAMP, SHIPPED]) {
      for (const dpr of [1, 2]) {
        for (const [w, h] of [
          [32, 32],
          [44, 44],
          [96, 96],
          [160, 160],
          [256, 256],
          [400, 400],
          [320, 44],
          [44, 320],
        ] as const) {
          expect(
            scatterRampAreaMean(Math.min(w, h), profile, dpr, [w, h]),
            `${w}x${h} at dpr ${dpr}`,
          ).toBeCloseTo(quadrature(w, h, dpr, profile), 6);
        }
      }
    }
  });

  it("is the span curve exactly wherever the ramp has nothing to add", () => {
    // The excursion is `max(0, s₀ − sDeep)`, so on a span whose deep sharp share
    // already exceeds the start the projection IS the span curve — the ramp
    // never makes a surface heavier at the contour than in its own middle.
    for (const dpr of [1, 2]) {
      for (const span of [0, 8, 16, 32, 44, 96, 160, 256, 400]) {
        const start = scatterRampStart(dpr, SHIPPED, span);
        const deep = scatterDeepThickness(span, SHIPPED);
        if (1 - deep < start) continue;
        expect(scatterRampAreaMean(span, SHIPPED, dpr), `span ${span} at ${dpr}`).toBeCloseTo(
          deep,
          12,
        );
      }
    }
  });

  it("takes a square of the span where the caller has no extents, and says so", () => {
    for (const span of [32, 96, 160]) {
      expect(scatterRampAreaMean(span, RAMP, 1)).toBeCloseTo(
        scatterRampAreaMean(span, RAMP, 1, [span, span]),
        12,
      );
    }
    // A strip is not its own span squared: a 1200x160 bar has proportionally
    // more of its area within the ramp's reach of a long edge than a 160x160
    // square does, so the two do not project to the same number and the extents
    // matter where a caller has them. Read on a span the ramp acts on at all —
    // where the excursion clamps off the projection is the span curve, which is
    // one number per span by construction.
    expect(scatterRampAreaMean(160, RAMP, 1, [1200, 160])).not.toBeCloseTo(
      scatterRampAreaMean(160, RAMP, 1),
      3,
    );
  });

  it("rises monotonically with the span and approaches 1 by an edge term", () => {
    for (const dpr of [1, 2]) {
      let previous = -Infinity;
      for (const span of [8, 16, 32, 44, 64, 96, 128, 160, 200, 256, 400, 800, 4000]) {
        const mean = scatterRampAreaMean(span, RAMP, dpr);
        expect(mean, `span ${span} at dpr ${dpr}`).toBeGreaterThanOrEqual(previous);
        previous = mean;
      }
      // Far above the reach the sharp component survives only in a rim of
      // fixed width, so its share of the area falls like 1/span — the limit is
      // 1 minus an edge term, not 1.
      expect(scatterRampAreaMean(40000, RAMP, dpr)).toBeGreaterThan(0.97);
      expect(scatterRampAreaMean(40000, RAMP, dpr)).toBeLessThan(1);
      const deficit = (span: number) => 1 - scatterRampAreaMean(span, RAMP, dpr);
      expect(deficit(40000) * 2).toBeCloseTo(deficit(20000), 3);
    }
  });

  it("reproduces the fitted shape at the two scales", () => {
    // The numbers the profile's defaults carry: at 1x the sharp share at the
    // contour is 0.72 on a thin span and 0.52 on a thick one, over a reach of
    // 80 device px — the third sweep's fit over 44 points; at 2x 0.46 and 0.17
    // over 100, still provisional because the excursion is zero there and a
    // sweep cannot fit what does not move. Stated here so a refit moves a test.
    expect(scatterRampStart(1, SHIPPED, 0)).toBeCloseTo(0.72, 12);
    expect(scatterRampStart(1, SHIPPED, 96)).toBeCloseTo(0.52, 12);
    expect(scatterRampStart(2, SHIPPED, 0)).toBeCloseTo(0.46, 12);
    expect(scatterRampStart(2, SHIPPED, 96)).toBeCloseTo(0.17, 12);
    // The fourth form's far end, at the scatter span curve's top and beyond:
    // 0.20 at 1x, fitted on the W14 bed (the fourth sweep, claims §5.68).
    expect(scatterRampStart(1, SHIPPED, SHIPPED.sizeScatterSpanMax)).toBeCloseTo(0.2, 12);
    expect(scatterRampStart(1, SHIPPED, 4000)).toBeCloseTo(0.2, 12);
    expect(scatterRampStart(2, SHIPPED, SHIPPED.sizeScatterSpanMax)).toBeCloseTo(0.15, 12);
    expect(scatterRampReachDevicePx(1, SHIPPED)).toBe(80);
    expect(scatterRampReachDevicePx(2, SHIPPED)).toBe(100);
    // The reach in CSS px more than halves between the scales, which is what
    // "one length in device pixels" means for a consumer working in CSS px.
    expect(scatterRampReachDevicePx(2, SHIPPED) / 2).toBeLessThan(
      scatterRampReachDevicePx(1, SHIPPED),
    );
  });

  it("has no excursion at all at 2x on the calibration bed, by the law", () => {
    /*
     * Not a special case and not a disabled facet: at dpr 2 G0 read the
     * reference's own contour sharp share BELOW vitrea's deep value on every
     * cell of the bed (implied excursions −0.095 to −0.289, claims §5.64 §4),
     * so `max(0, s₀ − sDeep)` is zero there. The consequence is that the 2x gap
     * is a DEEP-VALUE gap — the span law's floor, knee and top — and no
     * one-signed excursion above that law can express it. Pinned so that a
     * change which quietly starts moving the 2x bed has to say so.
     */
    const BED = [32, 44, 96, 128, 130, 160];
    for (const span of BED) {
      const deepSharp = 1 - scatterDeepThickness(span, SHIPPED);
      expect(scatterRampStart(2, SHIPPED, span), `span ${span}`).toBeLessThan(deepSharp);
      for (const u of [0, 1, 10, 50, 200]) {
        expect(scatterSharpShare(u, 2, SHIPPED, span), `span ${span} at u ${u}`).toBeCloseTo(
          deepSharp,
          12,
        );
      }
      expect(scatterRampAreaMean(span, SHIPPED, 2), `span ${span}`).toBeCloseTo(
        scatterDeepThickness(span, SHIPPED),
        12,
      );
    }
    // And at 1x it acts on every one of them, which is the other half of the
    // third form's claim: the thin anchor clears `rrect-sm`'s 0.600 floor and
    // the thick anchor clears `rrect-md`'s 0.481.
    for (const span of BED) {
      expect(scatterRampStart(1, SHIPPED, span), `span ${span}`).toBeGreaterThan(
        1 - scatterDeepThickness(span, SHIPPED),
      );
    }
  });

  it("keeps falling past the thickness knee, along the scatter span curve", () => {
    /*
     * The fourth form (W13 Decision Log 6; claims §5.67 §4). The third form's
     * start was flat above `sizeSpanMax`, so spans 96 to 160 all started at
     * the thick anchor while the reference's start fell 0.512 → 0.501 → 0.410
     * across them; the excursion therefore GREW with span and `rrect-lg`
     * overshot its interior by 33% on the holdout. Now the start declines from
     * the thick anchor at `sizeSpanMax` to `far` at `sizeScatterSpanMax` along
     * the same smoothstep the deep value rises on.
     */
    const thick = scatterRampStart(1, SHIPPED, SHIPPED.sizeSpanMax);
    const far = scatterRampStart(1, SHIPPED, SHIPPED.sizeScatterSpanMax);
    expect(far).toBeLessThan(thick);
    let previous = thick;
    for (const span of [96, 112, 128, 144, 160, 192, 224, 256]) {
      const start = scatterRampStart(1, SHIPPED, span);
      expect(start, `span ${span}`).toBeLessThanOrEqual(previous + 1e-12);
      previous = start;
    }
    // Halfway along the band the decline is at the smoothstep's midpoint.
    const mid = (SHIPPED.sizeSpanMax + SHIPPED.sizeScatterSpanMax) / 2;
    expect(scatterRampStart(1, SHIPPED, mid)).toBeCloseTo((thick + far) / 2, 12);
    // Below the knee nothing changes from the third form: the thin end and the
    // thin/thick grading are untouched.
    expect(scatterRampStart(1, SHIPPED, 0)).toBeCloseTo(SHIPPED.sizeScatterRampStartThin1x, 12);
    expect(scatterRampStart(1, SHIPPED, 44)).toBeCloseTo(
      SHIPPED.sizeScatterRampStartThin1x +
        (SHIPPED.sizeScatterRampStartThick1x - SHIPPED.sizeScatterRampStartThin1x) *
          sizeThickness(44, SHIPPED),
      12,
    );
  });

  it("carries the eight constants through a profile patch", () => {
    const patched = withMaterialOverrides(SHIPPED, {
      sizeScatterSpanMax: 320,
      sizeScatterRampStartThin1x: 0.8,
      sizeScatterRampStartThick1x: 0.7,
      sizeScatterRampStartFar1x: 0.6,
      sizeScatterRampStartThin2x: 0.2,
      sizeScatterRampStartThick2x: 0.1,
      sizeScatterRampStartFar2x: 0.05,
      sizeScatterRampReach1xPx: 200,
      sizeScatterRampReach2xPx: 50,
    });
    expect(scatterRampStart(1, patched, 0)).toBe(0.8);
    expect(scatterRampStart(1, patched, 96)).toBeCloseTo(0.7, 12);
    expect(scatterRampStart(1, patched, 320)).toBeCloseTo(0.6, 12);
    expect(scatterRampStart(2, patched, 0)).toBe(0.2);
    expect(scatterRampStart(2, patched, 96)).toBeCloseTo(0.1, 12);
    expect(scatterRampStart(2, patched, 320)).toBeCloseTo(0.05, 12);
    expect(scatterRampReachDevicePx(1, patched)).toBe(200);
    expect(scatterRampReachDevicePx(2, patched)).toBe(50);
    expect(scatterDeepThickness(320, patched)).toBeCloseTo(1, 12);
    expect(scatterDeepThickness(320, SHIPPED)).toBe(1);
    // A span the curve saturates at under the patch: the deep sharp share is 0,
    // so the excursion is the whole start — which at the curve's top is the far
    // anchor — and it falls off over the reach.
    expect(scatterSharpShare(80, 1, patched, 320)).toBeCloseTo(0.6 * (1 - 80 / 200), 12);
  });

  it("never divides the shared projection's widths by the device ratio", () => {
    // The two widths are the σ the mix runs between: the sharp one at weight 0
    // and the heavy one at weight 1. W12 G3 read them as device-pixel
    // quantities and this function divided by the ratio; W13 Decision Log 8
    // retired that on the bed (claims §5.68 §5) and W15 G1 restored it on the
    // GPU tier's DRAW path alone — the renderer's `bodySigmaCssFor`, which is
    // where the pyramid's body σ comes from. This function is the shared
    // projection every other consumer reads, and a division here would move the
    // CSS tier, whose 2x σ W15 Decision Log 2 holds until G1 predicts it.
    expect(SIGMA).toBe(1.25);
    expect(SIGMA * SHIPPED.sizeScatterGainMax).toBe(10);
    for (const dpr of [1, 1.5, 2, 3]) {
      expect(sizeScatterSigmaAt(SIGMA, 0, SHIPPED, dpr), `sharp at ${dpr}`).toBeCloseTo(1.25, 12);
      expect(sizeScatterSigmaAt(SIGMA, 1, SHIPPED, dpr), `heavy at ${dpr}`).toBeCloseTo(10, 12);
    }
  });

  it("derives the single σ from the projection, so one law feeds both tiers", () => {
    // The ratio reaches the ramp's projection (its start and reach, and since
    // W15 G1 the deep value's floor and span top) and the heavy width's gain.
    for (const span of [32, 44, 96, 128, 160, 256]) {
      for (const dpr of [1, 1.5, 2, 3]) {
        expect(sizeScatterSigma(SIGMA, span, SHIPPED, dpr), `span ${span} at ${dpr}`).toBeCloseTo(
          sizeScatterSigmaAt(SIGMA, scatterThickness(span, 1, SHIPPED, dpr), SHIPPED, dpr),
          12,
        );
      }
    }
  });

  it("leaves the thickness curve, and every facet on it, untouched", () => {
    for (const span of SPANS) {
      expect(sizeThickness(span, RAMP)).toBe(sizeThickness(span, SHIPPED));
      expect(lensSizeGain(span, RAMP)).toBe(lensSizeGain(span, SHIPPED));
      expect(sizeOcclusionAlpha(0.5, span, RAMP)).toBe(sizeOcclusionAlpha(0.5, span, SHIPPED));
    }
  });
});

/*
 * The body's SECOND SCALE (W15 G1, claims §5.69 §1–§2).
 *
 * At 2x the reference's body is a different object: its deep interior is fully
 * heavy on the two largest spans where the 1x span curve leaves a sharp share
 * of 0.24–0.36, and its heavy component is 8–11 device px wide. So the gain,
 * the deep value's floor and the deep value's span top each get a second
 * reading, interpolated by the same `rampAtScale` the ramp's anchors use.
 *
 * The wave's binding rule is that the 1x material does not move, and here it is
 * a property rather than a promise: every case below pins the dpr-1 value of
 * every function against the same function on a profile that has no 2x terms at
 * all. What acts at dpr 2 and interpolates at 1.5 is pinned beside it, and the
 * last case pins the patch paths the runtime sweep will name as axes.
 */
describe("the body's second scale (W15 G1)", () => {
  const SHIPPED = DEFAULT_MATERIAL_PROFILE;
  const SIGMA = SHIPPED.optics.regular.blurSigma;
  /** All three second-scale terms off their 1x values at once. */
  const SECOND: MaterialProfile = withMaterialOverrides(SHIPPED, {
    sizeScatterGainMax2x: 4,
    sizeScatterFloor2x: 0.9,
    sizeScatterSpanMax2x: 128,
  });
  const SPANS_HERE = [0, 32, 44, 96, 128, 160, 256, 400] as const;
  const DEPTHS = [0, 4, 12, 24, 48, 96, 200] as const;

  it("ships equal to its own 1x constants, so the landed material is scale-free", () => {
    expect(SHIPPED.sizeScatterGainMax2x).toBe(SHIPPED.sizeScatterGainMax);
    expect(SHIPPED.sizeScatterFloor2x).toBe(SHIPPED.sizeScatterFloor);
    expect(SHIPPED.sizeScatterSpanMax2x).toBe(SHIPPED.sizeScatterSpanMax);
    for (const dpr of [1, 1.5, 2, 3]) {
      for (const span of SPANS_HERE) {
        expect(scatterDeepThickness(span, SHIPPED, dpr), `kDeep ${span} at ${dpr}`).toBe(
          scatterDeepThickness(span, SHIPPED, 1),
        );
      }
      expect(scatterGainAtScale(SHIPPED, dpr)).toBe(SHIPPED.sizeScatterGainMax);
      expect(scatterFloorAtScale(SHIPPED, dpr)).toBe(SHIPPED.sizeScatterFloor);
      expect(scatterSpanMaxAtScale(SHIPPED, dpr)).toBe(SHIPPED.sizeScatterSpanMax);
    }
  });

  it("changes nothing at dpr 1, whatever the second scale says", () => {
    // The binding rule, as arithmetic. Every function the second scale reaches,
    // read at dpr 1 on a profile whose three 2x terms are wild, against the
    // profile that has none of them.
    expect(scatterGainAtScale(SECOND, 1)).toBe(SHIPPED.sizeScatterGainMax);
    expect(scatterFloorAtScale(SECOND, 1)).toBe(SHIPPED.sizeScatterFloor);
    expect(scatterSpanMaxAtScale(SECOND, 1)).toBe(SHIPPED.sizeScatterSpanMax);
    // And below dpr 1 too: `rampAtScale` holds outside [1, 2].
    for (const dpr of [0.5, 1]) {
      for (const span of SPANS_HERE) {
        expect(scatterDeepThickness(span, SECOND, dpr), `kDeep ${span} at ${dpr}`).toBe(
          scatterDeepThickness(span, SHIPPED, dpr),
        );
        expect(scatterRampStart(dpr, SECOND, span), `s0 ${span} at ${dpr}`).toBe(
          scatterRampStart(dpr, SHIPPED, span),
        );
        expect(scatterRampAreaMean(span, SECOND, dpr), `mean ${span} at ${dpr}`).toBe(
          scatterRampAreaMean(span, SHIPPED, dpr),
        );
        for (const fold of [0, 0.45, 1]) {
          expect(
            scatterThickness(span, fold, SECOND, dpr),
            `k̄ ${span} fold ${fold} at ${dpr}`,
          ).toBe(scatterThickness(span, fold, SHIPPED, dpr));
        }
        for (const u of DEPTHS) {
          expect(scatterSharpShare(u, dpr, SECOND, span), `s(${u}) ${span} at ${dpr}`).toBe(
            scatterSharpShare(u, dpr, SHIPPED, span),
          );
        }
        expect(sizeScatterSigma(SIGMA, span, SECOND, dpr), `σ ${span} at ${dpr}`).toBe(
          sizeScatterSigma(SIGMA, span, SHIPPED, dpr),
        );
      }
    }
  });

  it("acts at dpr 2, on the deep value, the projection and the width", () => {
    // The floor: the deep value at a span below `sizeSpanMin` IS the floor, so
    // this reads it directly.
    expect(scatterDeepThickness(0, SECOND, 2)).toBeCloseTo(0.9, 12);
    expect(scatterDeepThickness(0, SHIPPED, 2)).toBeCloseTo(0.4, 12);
    // The span top: the deep value saturates at 128 under the second scale and
    // not until 256 without it.
    expect(scatterDeepThickness(128, SECOND, 2)).toBeCloseTo(1, 12);
    expect(scatterDeepThickness(128, SHIPPED, 2)).toBeLessThan(1);
    // A heavier deep value is a smaller deep SHARP share, which is what claims
    // §5.69 §2 measured the 2x reference to have — and it lifts the projection
    // on every span.
    for (const span of [32, 44, 96, 128, 160]) {
      expect(scatterRampAreaMean(span, SECOND, 2), `mean at ${span}`).toBeGreaterThan(
        scatterRampAreaMean(span, SHIPPED, 2),
      );
      expect(1 - scatterSharpShare(400, 2, SECOND, span), `deep k at ${span}`).toBeGreaterThan(
        1 - scatterSharpShare(400, 2, SHIPPED, span),
      );
    }
    // The gain: the heavy end of the width law at this ratio, and the sharp end
    // untouched, since the ratio never divides the σ here.
    expect(sizeScatterSigmaAt(SIGMA, 1, SECOND, 2)).toBeCloseTo(SIGMA * 4, 12);
    expect(sizeScatterSigmaAt(SIGMA, 0, SECOND, 2)).toBeCloseTo(SIGMA, 12);
    // And the fold still lands on the floor exactly — the floor this ratio
    // resolves, which is the W11c semantics carried onto the second scale.
    for (const span of SPANS_HERE) {
      expect(scatterThickness(span, 0, SECOND, 2), `fold 0 at ${span}`).toBeCloseTo(0.9, 12);
    }
  });

  it("interpolates linearly between the two scales the reference was read at", () => {
    expect(scatterFloorAtScale(SECOND, 1.5)).toBeCloseTo(0.65, 12);
    expect(scatterSpanMaxAtScale(SECOND, 1.5)).toBeCloseTo(192, 12);
    expect(scatterGainAtScale(SECOND, 1.5)).toBeCloseTo(6, 12);
    expect(scatterDeepThickness(0, SECOND, 1.5)).toBeCloseTo(0.65, 12);
    expect(sizeScatterSigmaAt(SIGMA, 1, SECOND, 1.5)).toBeCloseTo(SIGMA * 6, 12);
    // Held above dpr 2 rather than extrapolated, as the ramp's anchors are: an
    // extrapolation of a two-point fit past its own anchors is an invention.
    for (const dpr of [2, 3, 4]) {
      expect(scatterFloorAtScale(SECOND, dpr), `floor at ${dpr}`).toBeCloseTo(0.9, 12);
      expect(scatterGainAtScale(SECOND, dpr), `gain at ${dpr}`).toBeCloseTo(4, 12);
      expect(scatterSpanMaxAtScale(SECOND, dpr), `top at ${dpr}`).toBeCloseTo(128, 12);
    }
  });

  it("is reachable one term at a time by the patch path a sweep axis names", () => {
    /*
     * The sweep names each axis as a dotted path into the patch
     * (`--axis sizeScatterFloor2x=0.6,0.8`), so what has to hold is that a patch
     * carrying that one leaf lands it and moves nothing else. Checked here as a
     * unit rather than by running the sweep, which needs the GPU.
     */
    const axes = [
      ["sizeScatterGainMax2x", 7.2],
      ["sizeScatterFloor2x", 0.62],
      ["sizeScatterSpanMax2x", 144],
    ] as const;
    for (const [path, value] of axes) {
      const patched = withMaterialOverrides(SHIPPED, { [path]: value });
      expect(patched[path], path).toBe(value);
      // Every other constant of the material is the default's.
      for (const key of Object.keys(SHIPPED) as (keyof MaterialProfile)[]) {
        if (key === path) continue;
        expect(patched[key], `${path} moved ${String(key)}`).toEqual(SHIPPED[key]);
      }
      // And dpr 1 is untouched by any of them.
      for (const span of SPANS_HERE) {
        expect(scatterDeepThickness(span, patched, 1), `${path} at span ${span}`).toBe(
          scatterDeepThickness(span, SHIPPED, 1),
        );
      }
    }
  });
});

describe("the scattering facet reaches the chain the optics pass samples", () => {
  it("names the level whose blur is the σ asked for, continuously", () => {
    expect(chainLodForSigma(0)).toBe(0);
    expect(chainLodForSigma(CHAIN_SIGMA_AT_LEVEL_1)).toBeCloseTo(1, 12);
    expect(chainLodForSigma(CHAIN_SIGMA_AT_LEVEL_1 * 2)).toBeCloseTo(2, 12);
    expect(chainLodForSigma(CHAIN_SIGMA_AT_LEVEL_1 * 4)).toBeCloseTo(3, 12);
    let previous = -Infinity;
    for (const sigma of [0, 0.3, 1.2, 2, 4.8, 10, 40, 400]) {
      const lod = chainLodForSigma(sigma);
      expect(lod, `σ ${sigma}`).toBeGreaterThanOrEqual(previous);
      previous = lod;
    }
  });

  /*
   * The shader adds `log2(scatterGain)` to that level. This is the arithmetic it
   * relies on, checked here rather than trusted: one octave of LOD is one doubling
   * of σ, so the gain the CSS tier multiplies its blur by and the level the GPU
   * tier samples describe the same kernel.
   */
  it("puts one doubling of σ exactly one level up", () => {
    const base = chainLodForSigma(8);
    expect(chainLodForSigma(16) - base).toBeCloseTo(1, 12);
    // A profile whose ramp has already run out at the contour, so the mix is
    // fully heavy everywhere and the σ is exactly the gain times the base.
    const allHeavy = withMaterialOverrides(GAINED, {
      sizeScatterGainMax: 2,
      sizeScatterRampStartThin1x: 0,
      sizeScatterRampStartThick1x: 0,
      sizeScatterRampStartThin2x: 0,
      sizeScatterRampStartThick2x: 0,
      sizeScatterRampStartFar1x: 0,
      sizeScatterRampStartFar2x: 0,
    });
    expect(base + Math.log2(2)).toBeCloseTo(chainLodForSigma(sizeScatterSigma(8, 4000, allHeavy)), 12);
  });
});

describe("the law reaches the shader per surface, not per group", () => {
  const surfaceAt = (nodeId: string, size: readonly [number, number]): SurfaceInput => ({
    nodeId,
    family: "fixed-rounded-rect",
    shape: {
      center: [200, 200],
      size,
      radii: [8, 8, 8, 8],
      smoothing: 0,
      thickness: 8,
    },
    reference: "figma-smoothing",
  });

  const group: GroupRenderInput = {
    groupId: "mixed",
    refraction: "true",
    analysisExact: false,
    surfaces: [
      // 40 is this profile's `sizeSpanMin`, so the button is exactly at the law's
      // zero — the "a small control did not move" case, stated as data.
      surfaceAt("button", [120, 40]),
      surfaceAt("platter", [400, 280]),
    ],
  };

  it("gives a button and a platter in one group different thicknesses", () => {
    const resolved = resolveSurfaces(group, "rsupn", GAINED);
    const button = resolved.find((s) => s.nodeId === "button");
    const platter = resolved.find((s) => s.nodeId === "platter");
    expect(button?.sizeThickness).toBe(0);
    expect(platter?.sizeThickness).toBe(1);
    expect(platter?.lensDepthPx).toBeGreaterThan(button?.lensDepthPx as number);
  });

  it("packs the span where the field pass reads it, so the shader evaluates both curves", () => {
    // W11c: the slot used to carry the folded thickness; it carries the span now,
    // because the scatter facet's curve has a band top the thickness curve does
    // not, and only the span can be evaluated on both.
    const resolved = resolveSurfaces(group, "rsupn", GAINED);
    const packed = packInstances(resolved, [0, 0]);
    for (const [index, surface] of resolved.entries()) {
      expect(packed.data[index * INSTANCE_FLOATS + 16]).toBeCloseTo(surface.spanPx, 6);
    }
    expect(resolved.find((s) => s.nodeId === "button")?.spanPx).toBe(40);
    expect(resolved.find((s) => s.nodeId === "platter")?.spanPx).toBe(280);
  });

  it("still clamps the lens to the shorter half extent, however thick it is authored", () => {
    const thick = resolveSurfaces(
      { ...group, surfaces: [surfaceAt("stubby", [400, 24])] },
      "rsupn",
      GAINED,
    );
    // Span 24 is under `sizeSpanMin`, so the gain is 1 and the depth is the
    // authored thickness — under the 12 px half-extent clamp either way.
    expect(thick[0]?.sizeThickness).toBe(0);
    expect(lensDepthPx(80, 24, GAINED)).toBe(12);
  });
});
