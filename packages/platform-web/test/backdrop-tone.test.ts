/**
 * The CSS tier's half of backdrop tone adaptation (W7): the reading it takes of
 * the backdrop, and the material that reading produces.
 *
 * The curve itself is pinned against the renderer's by
 * `packages/calibration/test/tier-coherence.test.ts` — one curve, mirrored, and a
 * second set of assertions here would be a second opinion. What belongs here is
 * what only this tier has: where the backdrop reading comes from, what it does
 * when there is none, and the composite the reading turns into.
 *
 * jsdom has no canvas 2-D context, so `sampleBackdropTone`'s *pixel* path is a
 * Playwright case (`e2e/pixel/backdrop-tone-pixels.spec.ts`); what is asserted
 * here is that its absence degrades to "no reading" rather than to a guess, which
 * is the property the whole axis is safe under.
 */

import { describe, expect, it } from "vitest";

import {
  releaseBackdropToneScratch,
  sampleBackdropTone,
  SAMPLE_EXTENT,
} from "../src/backdrop-tone";
import {
  adaptedSourceOptics,
  backdropToneAdaptation,
  BACKDROP_TONE,
  cssOpticsFromSource,
  CSS_TIER_MAPPING,
  cssTierOptics,
  collapsedRim,
  COLLAPSE_TRANSMISSION,
  resolvedCollapsedRim,
  RIM_COLLAPSED,
  RIM_COLLAPSED_TINTED,
  RIM_TINT_CHROMA,
  resolvedRimTintChroma,
  rimTintColour,
  rimAmplitude,
  sourceOptics,
} from "../src/optics";

describe("sampleBackdropTone", () => {
  it("reads nothing rather than guessing, wherever there are no pixels", () => {
    releaseBackdropToneScratch();
    expect(sampleBackdropTone(undefined)).toBeUndefined();
    // An <img> that has not decoded — `complete` would be true for a failed load
    // too, so the intrinsic size is what is checked.
    const image = document.createElement("img");
    expect(sampleBackdropTone({ kind: "image", image })).toBeUndefined();
    const canvas = document.createElement("canvas");
    canvas.width = 0;
    canvas.height = 0;
    expect(sampleBackdropTone({ kind: "canvas", canvas })).toBeUndefined();
    const video = document.createElement("video");
    expect(sampleBackdropTone({ kind: "video", video })).toBeUndefined();
  });

  it("draws at or below 1:1 — the cap is a ceiling, not a target", () => {
    // Once this guarded a measured trap (encoded-space downsampling under a
    // linear-mean convention read the impulse backdrop five times too dark).
    // W9 adopted the encoded-space mean as the model itself (claims §5.31), so
    // the extent now buys only rounding headroom and provenance continuity with
    // every committed capture. Still asserted, so that lowering it is a
    // deliberate act — a readback-cost change with the e2e pins re-verified —
    // with this comment attached.
    expect(SAMPLE_EXTENT).toBeGreaterThanOrEqual(512);
  });
});

describe("the material one backdrop reading produces", () => {
  const source = sourceOptics()["regular"];
  const base = cssTierOptics()["regular"];

  it("is the pre-W7 material, but for the rim's resolved amplitude, with no reading", () => {
    /*
     * The guard is unchanged in substance: a surface the tier read nothing for,
     * and a surface at zero adaptation, draw the material the profile ships and
     * not a guess at one. What no longer survives it is object identity, and the
     * reason is the rim's law (W23; claims §5.100 §4). `rimAlpha` is the law's
     * INTERCEPT everywhere upstream of `adaptedSourceOptics` and the resolved
     * amplitude everywhere downstream, so the law has to be evaluated here even
     * with nothing sampled — handing the intercept 0.844 on to
     * `borderAlphaPerRimAlpha` would put a near-opaque white outline around every
     * unsampled surface. Every other field is asserted untouched, which is the
     * half that was ever about the adaptation.
     */
    const unsampled = adaptedSourceOptics(source, undefined, 1);
    expect(unsampled).toEqual({
      ...source,
      rimAlpha: rimAmplitude(source, CSS_TIER_MAPPING.referenceBackdropLuminance),
    });
    // The level with nothing sampled is the mapping's reference, the one
    // `cssTintAlpha` already falls back to: 0.844 − 0.628 × 0.4708.
    expect(unsampled.rimAlpha).toBeCloseTo(0.5483, 4);
    // With a reading and no adaptation the same holds at the level that was read
    // rather than at the fallback — black, so the material's own luminance is its
    // tint alpha and the amplitude is 0.844 − 0.628 × 0.46.
    const unadapted = adaptedSourceOptics(source, [0, 0, 0], 0);
    expect(unadapted).toEqual({ ...source, rimAlpha: rimAmplitude(source, 0) });
    expect(unadapted.rimAlpha).toBeCloseTo(0.5551, 4);
  });

  it("is the backdrop itself at full adaptation, less the transmission it keeps", () => {
    /*
     * The collapse's target is the backdrop's tone and its opacity is one minus
     * what still comes through (W24; claims §5.108 §2). At full adaptation the
     * pair is `A' = 1 − c` and `T' = tone`, so the surface draws the tone over
     * `c` of whatever `backdrop-filter` has put beneath it — which is the
     * reference's collapsed capsule passing its backdrop's centre dot, and what
     * this tier was asserting the absence of.
     */
    const tone = [0.0117, 0.0117, 0.0125] as const;
    const adapted = adaptedSourceOptics(source, tone, 1);
    expect(adapted.tintAlpha).toBeCloseTo(1 - COLLAPSE_TRANSMISSION, 12);
    for (const index of [0, 1, 2] as const) {
      expect(adapted.tint[index]).toBeCloseTo(tone[index] as number, 12);
    }
    // And a profile that declines the transmission is opaque again, exactly as
    // W7 left it: the mechanism is one constant and it is the whole of it.
    const w7 = adaptedSourceOptics(source, tone, 1, undefined, undefined, 0);
    expect(w7.tintAlpha).toBeCloseTo(1, 12);
  });

  it("is a window at the transmission's far end, and not the tint at full opacity", () => {
    /*
     * The endpoint, which the pair states degenerately: `A' = A − k·c` reaches 0
     * where a fully collapsed surface transmits everything, and there is no
     * colour a zero-opacity layer shows. The alpha is written as 0 rather than
     * left at the material's own, because the second is what a surface meant to
     * be a window would draw — the untransformed tint over the whole of it.
     *
     * No shipped profile reaches this: `collapseTransmission` is 0.017 and the
     * far end is 1. It is pinned because the arithmetic passes through it and
     * the branch that handles it is unreachable from any capture on the bed.
     */
    const tone = [0.0117, 0.0117, 0.0125] as const;
    const open = adaptedSourceOptics(source, tone, 1, undefined, undefined, 1);
    expect(open.tintAlpha).toBe(0);
    // The rim is the collapsed one, because a collapsed surface keeps its rim
    // whatever it transmits — the transmission is the BODY's term.
    expect(open.rimAlpha).toBeCloseTo(RIM_COLLAPSED, 12);
  });

  it("darkens rather than brightens on the way there", () => {
    // The failure this pins: lerping the colour and the alpha independently makes
    // a partially adapted surface LIGHTER than the one it started from, because a
    // rising alpha over a still-mostly-neutral tint is just more white. Measured
    // on the 96 px cells at interior 0.4545 → 0.5179 against a reference of 0.4542.
    const tone = [0.0117, 0.0117, 0.0117] as const;
    const backdrop = 0.0117;
    let previous = Number.POSITIVE_INFINITY;
    for (const adaptation of [0, 0.1, 0.25, 0.5, 0.75, 1]) {
      const adapted = adaptedSourceOptics(source, tone, adaptation);
      const interior =
        backdrop * (1 - adapted.tintAlpha) + (adapted.tint[0] as number) * adapted.tintAlpha;
      expect(interior, `adaptation ${adaptation}`).toBeLessThanOrEqual(previous + 1e-12);
      previous = interior;
    }
  });

  it("fades the rim as it goes, because a vanished surface has no lit edge", () => {
    // The reference says so on a calibration cell rather than by inference: its
    // capsule over the dark-solid backdrop is byte-identical to that background,
    // rim included. Left in, this tier's border is a white outline around a
    // surface that is meant not to be there — which is exactly what it was, until
    // this axis made the body dark enough to see it against.
    //
    // What the fade ends AT moved in W23 (claims §5.100 §3): the reference's
    // collapsed capsule is byte-identical to its background in its body and still
    // keeps a contour rim of +0.020 linear, in both schemes at both scales. So
    // the fade is a trade between the two rims — `amplitude·(1 − k) +
    // rimCollapsed·k` — rather than a fade to nothing, and the endpoint it fades
    // FROM is the law's amplitude at this tone, not the law's intercept.
    const tone = [0.0117, 0.0117, 0.0117] as const;
    const amplitude = rimAmplitude(source, 0.0117);
    expect(amplitude).toBeCloseTo(0.5512, 4);
    expect(adaptedSourceOptics(source, tone, 1).rimAlpha).toBe(RIM_COLLAPSED);
    expect(adaptedSourceOptics(source, tone, 0.5).rimAlpha).toBeCloseTo(
      (amplitude + RIM_COLLAPSED) / 2,
      12,
    );
    expect(adaptedSourceOptics(source, tone, 0).rimAlpha).toBe(amplitude);
  });

  it("carries that fade into the declared border, and nowhere else", () => {
    const tone = [0.0117, 0.0117, 0.0117] as const;
    // The collapsed rim the reference keeps, through the one constant that
    // carries a rim across this boundary: 0.038 × 0.64 (W23; claims §5.100 §§3-4).
    expect(cssOpticsFromSource(base, adaptedSourceOptics(source, tone, 1)).borderAlpha).toBeCloseTo(
      RIM_COLLAPSED * CSS_TIER_MAPPING.borderAlphaPerRimAlpha.regular,
      12,
    );
    // …and an unadapted source declares the shipped border exactly, so the
    // conversion is not a second opinion about it. The source has to come through
    // `adaptedSourceOptics` to say that now: that is where the law is resolved,
    // and `cssOpticsFromSource` reads an amplitude rather than an intercept (W23).
    expect(cssOpticsFromSource(base, adaptedSourceOptics(source, undefined, 0)).borderAlpha)
      .toBeCloseTo(base.borderAlpha, 12);
  });

  it("reaches the CSS declaration through the one conversion the tier already has", () => {
    // `cssOpticsFromSource` is `tintedCssOptics`'s tail, split out so the
    // adaptation lands through the same alpha-and-colour solve the profile's own
    // tint does. An untinted, unadapted source must come back out as the shipped
    // material, or the conversion would be a second set of numbers.
    const converted = cssOpticsFromSource(base, source);
    expect(converted.tintAlpha).toBeCloseTo(base.tintAlpha, 12);
    for (const index of [0, 1, 2] as const) {
      expect(converted.tint[index]).toBe(base.tint[index]);
    }
  });

  it("declares a fully adapted surface AS its backdrop, all but what it transmits", () => {
    const tone = [0.0117, 0.0117, 0.0117] as const;
    const declared = cssOpticsFromSource(base, adaptedSourceOptics(source, tone, 1));
    // sRGB(0.0117) ≈ 0.1124 → 29/255. A near-opaque overlay of the backdrop's own
    // colour is what makes the surface vanish on a tier that cannot sample; the
    // `collapseTransmission` it stops short of opacity by is what still comes
    // through the `backdrop-filter` beneath it (W24; claims §5.108 §2).
    // 0.98 and not 0.983: the source's `1 − c` crosses the tier boundary through
    // `cssOpticsFromSource`'s own alpha solve, which is where the two composites'
    // transfer functions are reconciled.
    expect(declared.tintAlpha).toBeCloseTo(0.98, 4);
    for (const index of [0, 1, 2] as const) {
      expect(declared.tint[index]).toBeGreaterThanOrEqual(27);
      expect(declared.tint[index]).toBeLessThanOrEqual(31);
    }
  });
});

describe("what the axis does to an ordinary page", () => {
  it("nothing — every backdrop above the knee leaves the material alone", () => {
    for (const backdrop of [0.16, 0.2, 0.35, 0.5, 0.7, 0.9]) {
      for (const thickness of [0, 0.1, 0.5, 1]) {
        expect(backdropToneAdaptation(backdrop, thickness, BACKDROP_TONE)).toBe(0);
      }
    }
  });
});

describe("the collapsed rim's constants come from the profile the root was given (W23 G1 review)", () => {
  /*
   * The renderer reads `rimCollapsed` and `rimCollapsedTinted` off the material
   * profile it was handed, and this tier has to read the same two numbers off the
   * same document. Reading the mirrored defaults instead is invisible until an
   * app passes a profile that names either — including the profile that names
   * both as 0, which is how a caller asks for the pre-W23 collapse — and then the
   * two tiers draw different rims on the same surface with nothing to say so.
   */
  it("resolves both ends off the patch, and falls back to the mirror where it names neither", () => {
    expect(resolvedCollapsedRim()).toEqual({ bare: RIM_COLLAPSED, painted: RIM_COLLAPSED_TINTED });
    expect(resolvedCollapsedRim({})).toEqual({
      bare: RIM_COLLAPSED,
      painted: RIM_COLLAPSED_TINTED,
    });
    expect(resolvedCollapsedRim({ rimCollapsed: 0, rimCollapsedTinted: 0 })).toEqual({
      bare: 0,
      painted: 0,
    });
    // One named, one not: the patch's own merge rule, leaf by leaf.
    expect(resolvedCollapsedRim({ rimCollapsed: 0.02 })).toEqual({
      bare: 0.02,
      painted: RIM_COLLAPSED_TINTED,
    });
  });

  it("carries those constants into the collapsed rim and into the border", () => {
    const source = sourceOptics().regular;
    const tone = [0.0117, 0.0117, 0.0117] as const;
    const off = resolvedCollapsedRim({ rimCollapsed: 0, rimCollapsedTinted: 0 });
    // A profile that declines the collapsed rim draws no border on a collapsed
    // surface, painted or bare — which is what the renderer does with the same
    // document, and what this tier did NOT do while it read the mirror.
    for (const strength of [0, 0.5, 1]) {
      expect(collapsedRim(strength, off)).toBe(0);
      expect(
        adaptedSourceOptics(source, tone, 1, collapsedRim(strength, off)).rimAlpha,
      ).toBe(0);
    }
    // And the shipped constants still lerp between the two absolutes.
    const shipped = resolvedCollapsedRim();
    expect(collapsedRim(0, shipped)).toBe(RIM_COLLAPSED);
    expect(collapsedRim(1, shipped)).toBe(RIM_COLLAPSED_TINTED);
    expect(collapsedRim(0.5, shipped)).toBeCloseTo((RIM_COLLAPSED + RIM_COLLAPSED_TINTED) / 2, 12);
  });
});

describe("the border conversion is the variant's (W23 G1 review)", () => {
  /*
   * `borderAlphaPerRimAlpha` was re-based 1.95 → 0.64 because the REGULAR
   * variant's rim became a law and its amplitude tripled. The `clear` variant's
   * did not: it declares no scene on the calibration bed, so its `rimAlpha`
   * stands at 0.14 with a gain of 0. One ratio over both divided the clear
   * variant's border by three for a numerator that never moved.
   */
  it("keeps the clear variant's border where it has always been", () => {
    const clear = sourceOptics().clear;
    expect(clear.rimAlpha).toBe(0.14);
    expect(clear.rimLevelGain).toBe(0);
    expect(CSS_TIER_MAPPING.borderAlphaPerRimAlpha.clear).toBe(1.95);
    expect(cssTierOptics().clear.borderAlpha).toBeCloseTo(0.14 * 1.95, 12);
    // Through the adapted conversion too, on a surface with a measured backdrop:
    // the clear variant's amplitude is its intercept at every level.
    const adapted = adaptedSourceOptics(clear, [0.0117, 0.0117, 0.0117], 0);
    expect(adapted.rimAlpha).toBe(0.14);
    expect(
      cssOpticsFromSource(cssTierOptics().clear, adapted, CSS_TIER_MAPPING, undefined, "clear")
        .borderAlpha,
    ).toBeCloseTo(0.14 * 1.95, 12);
  });

  it("re-bases the regular variant only, and its product is the border it always drew", () => {
    const regular = sourceOptics().regular;
    expect(CSS_TIER_MAPPING.borderAlphaPerRimAlpha.regular).toBe(0.64);
    // 0.844 − 0.628 × materialLuminance(regular, 0.02) = 0.5483; × 0.64 = 0.3509,
    // against the 0.351 this tier has drawn since W6 (claims §5.100 §8).
    const amplitude = rimAmplitude(regular, CSS_TIER_MAPPING.referenceBackdropLuminance);
    expect(amplitude).toBeCloseTo(0.5483, 4);
    expect(cssTierOptics().regular.borderAlpha).toBeCloseTo(0.3509, 4);
    expect(cssTierOptics().regular.borderAlpha).toBeCloseTo(0.18 * 1.95, 3);
  });
});

describe("the rim's colour on a painted surface (W23 G3)", () => {
  /*
   * Apple's rim on a tinted capsule is the paint LIFTED — an orange of
   * (255, 148, 0) rises to (254, 188, 0) with its blue channel still at 0 — and
   * vitrea drew (255, 192, 130), the same rim in white. This tier draws the rim
   * as one inset `box-shadow`, so what it has to get right is the shadow's
   * COLOUR, and the expression is the shader's own read once per surface.
   */
  it("is white at chroma 0, the paint's CHROMATICITY at 1, and the mix between", () => {
    const white: [number, number, number] = [255, 255, 255];
    const orange = { color: [255, 148, 0] as [number, number, number], strength: 1 };
    expect(rimTintColour(white, orange, 0)).toEqual(white);
    /*
     * Normalised by the paint's own LUMINANCE and not by its brightest channel,
     * which is what the rows chose (claims §5.102): the rim keeps its AMOUNT and
     * takes only its hue. That orange is (1, 0.2961, 0) in linear light at a
     * luminance of 0.4244, so the gains are (2.356, 0.698, 0) — red saturates,
     * green takes 0.70 of the light and blue takes none, which is the ratio the
     * reference's own contour row carries. A normalisation by the brightest
     * channel would have given green 0.30 and divided the rim's luminance by the
     * paint's, which the collapsed orange capsule measured as 0.115 → 0.030.
     */
    const [r, g, b] = rimTintColour(white, orange, 1);
    expect(r).toBe(255);
    expect(g / 255).toBeCloseTo(0.698, 2);
    expect(b).toBe(0);
    // Half the chroma is half the way from white to that.
    const [hr, hg, hb] = rimTintColour(white, orange, 0.5);
    expect(hr).toBe(255);
    expect(hg / 255).toBeCloseTo((1 + 0.698) / 2, 2);
    expect(hb / 255).toBeCloseTo(0.5, 2);
  });

  it("is the pixel's own tint strength that gates it, so an untinted surface is untouched", () => {
    const white: [number, number, number] = [255, 255, 255];
    for (const chroma of [0, 0.5, 1]) {
      expect(rimTintColour(white, { color: [255, 148, 0], strength: 0 }, chroma)).toEqual(white);
    }
    // Half a coverage takes half the hue, which is the shader's `chroma × s`.
    expect(rimTintColour(white, { color: [255, 148, 0], strength: 0.5 }, 1)).toEqual(
      rimTintColour(white, { color: [255, 148, 0], strength: 1 }, 0.5),
    );
  });

  it("reads the constant off the profile the root was given", () => {
    expect(resolvedRimTintChroma()).toBe(RIM_TINT_CHROMA);
    expect(resolvedRimTintChroma({})).toBe(RIM_TINT_CHROMA);
    expect(resolvedRimTintChroma({ rimTintChroma: 1 })).toBe(1);
  });
});
