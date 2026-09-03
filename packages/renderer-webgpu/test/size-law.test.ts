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
  // The scatter facet's own curve (W11c) collapsed onto the thickness band, so
  // the "one curve" properties below still test every facet on one band; the
  // floor and the separate top get their own describe further down.
  sizeScatterFloor: 0,
  sizeScatterSpanMax: 200,
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
    {
      name: "scattering",
      at: (span) => sizeScatterSigma(8, span, GAINED),
      nominal: 8,
      saturated: 8 * GAINED.sizeScatterGainMax,
    },
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

describe("the scattering facet's own curve (W11c)", () => {
  // The measured shape: a floor at small spans, a band top past the thickness
  // curve's, and a fold that reaches the rise and not the floor.
  const OWN: MaterialProfile = withMaterialOverrides(GAINED, {
    sizeScatterFloor: 0.4,
    sizeScatterSpanMax: 400,
  });

  it("starts at the floor below the band, not at zero", () => {
    expect(scatterThickness(0, 1, OWN)).toBeCloseTo(0.4, 12);
    expect(scatterThickness(OWN.sizeSpanMin, 1, OWN)).toBeCloseTo(0.4, 12);
    expect(sizeScatterSigma(8, OWN.sizeSpanMin, OWN)).toBeCloseTo(8 * (1 + 1.5 * 0.4), 12);
  });

  it("keeps rising past the thickness curve's top and saturates at its own", () => {
    // sizeSpanMax is 200 here; the thickness curve is done, the scatter is not.
    expect(sizeThickness(200, OWN)).toBe(1);
    expect(scatterThickness(200, 1, OWN)).toBeLessThan(1);
    expect(scatterThickness(300, 1, OWN)).toBeGreaterThan(scatterThickness(200, 1, OWN));
    expect(scatterThickness(400, 1, OWN)).toBeCloseTo(1, 12);
    expect(scatterThickness(4000, 1, OWN)).toBeCloseTo(1, 12);
    expect(sizeScatterSigma(8, 4000, OWN)).toBeCloseTo(8 * OWN.sizeScatterGainMax, 12);
  });

  it("folds the rise under a preference and never the floor", () => {
    expect(scatterThickness(4000, 0, OWN)).toBeCloseTo(0.4, 12);
    expect(scatterThickness(4000, 0.5, OWN)).toBeCloseTo(0.4 + 0.6 * 0.5, 12);
    expect(scatterThickness(OWN.sizeSpanMin, 0, OWN)).toBeCloseTo(0.4, 12);
  });

  it("collapses onto the thickness curve when the profile says so", () => {
    for (const span of SPANS) {
      expect(scatterThickness(span, 1, GAINED)).toBeCloseTo(sizeThickness(span, GAINED), 12);
    }
  });

  it("leaves the thickness curve, and every facet on it, untouched", () => {
    for (const span of SPANS) {
      expect(sizeThickness(span, OWN)).toBe(sizeThickness(span, GAINED));
      expect(lensSizeGain(span, OWN)).toBe(lensSizeGain(span, GAINED));
      expect(sizeOcclusionAlpha(0.5, span, OWN)).toBe(sizeOcclusionAlpha(0.5, span, GAINED));
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
    expect(base + Math.log2(2)).toBeCloseTo(chainLodForSigma(sizeScatterSigma(8, 4000, withMaterialOverrides(GAINED, { sizeScatterGainMax: 2 }))), 12);
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
