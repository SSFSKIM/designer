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
  cssTierOptics,
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
    // The trap this guards: `drawImage` downsamples in the texture's ENCODED
    // space, and the encoded mean of a block is not the encoded form of its
    // linear mean. At a small fixed extent the calibration bed's impulse backdrop
    // read five times too dark. The constant is asserted rather than described so
    // that lowering it is a deliberate act with this comment attached.
    expect(SAMPLE_EXTENT).toBeGreaterThanOrEqual(512);
  });
});

describe("the material one backdrop reading produces", () => {
  const source = sourceOptics()["regular"];
  const base = cssTierOptics()["regular"];

  it("is the pre-W7 material exactly, with no reading", () => {
    expect(adaptedSourceOptics(source, undefined, 1)).toBe(source);
    expect(adaptedSourceOptics(source, [0, 0, 0], 0)).toBe(source);
  });

  it("is the backdrop itself, opaquely, at full adaptation", () => {
    const tone = [0.0117, 0.0117, 0.0125] as const;
    const adapted = adaptedSourceOptics(source, tone, 1);
    expect(adapted.tintAlpha).toBeCloseTo(1, 12);
    for (const index of [0, 1, 2] as const) {
      expect(adapted.tint[index]).toBeCloseTo(tone[index] as number, 12);
    }
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
    const tone = [0.0117, 0.0117, 0.0117] as const;
    expect(adaptedSourceOptics(source, tone, 1).rimAlpha).toBe(0);
    expect(adaptedSourceOptics(source, tone, 0.5).rimAlpha).toBeCloseTo(source.rimAlpha / 2, 12);
    expect(adaptedSourceOptics(source, tone, 0).rimAlpha).toBe(source.rimAlpha);
  });

  it("carries that fade into the declared border, and nowhere else", () => {
    const tone = [0.0117, 0.0117, 0.0117] as const;
    expect(cssOpticsFromSource(base, adaptedSourceOptics(source, tone, 1)).borderAlpha).toBe(0);
    // …and an unadapted source declares the shipped border exactly, so the
    // conversion is not a second opinion about it.
    expect(cssOpticsFromSource(base, source).borderAlpha).toBeCloseTo(base.borderAlpha, 12);
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

  it("declares a fully adapted surface AS its backdrop", () => {
    const tone = [0.0117, 0.0117, 0.0117] as const;
    const declared = cssOpticsFromSource(base, adaptedSourceOptics(source, tone, 1));
    // sRGB(0.0117) ≈ 0.1124 → 29/255. An opaque overlay of the backdrop's own
    // colour is what makes the surface vanish on a tier that cannot sample.
    expect(declared.tintAlpha).toBeCloseTo(1, 6);
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
