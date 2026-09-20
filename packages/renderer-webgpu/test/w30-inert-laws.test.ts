/**
 * W30 G2 — the eight leaves, at the inert values, as ALGEBRAIC identities.
 *
 * Acceptance clause 1 asks for more than "the goldens did not move". A golden is
 * one render of one scene at one span: it says a law is inert where it was
 * looked at. These cases say the laws are inert everywhere, by evaluating them
 * against the expression they replaced over a sweep wide enough that no argument
 * the runtime can produce is outside it — and by asserting `toBe`, which is
 * exact equality of doubles and not a tolerance.
 *
 * The distinction matters because the wave's whole claim is that the exemption
 * is for the DIGEST and not for the material. A near-identity would make the
 * claim a measurement with an error bar; an identity makes it arithmetic.
 *
 * Each leaf's own argument for why its inert value is an identity is written
 * where the leaf is authored (`material.ts`). What is checked here is that the
 * argument is true of the code:
 *
 *   - `sigmaSlopePerSpan · (span − sigmaSpanRefPx)` is a multiplied zero, so the
 *     `max` sees two zeros and σ is `sigmaPx` at every span and every scale;
 *   - `sizeHeavySecondShare` is a multiplied zero AND the single gate on the
 *     second heavy texture, so `heavySecondTapSigmaAtScale` returns 0 at every
 *     ratio and the pyramid allocates nothing;
 *   - `sizeScatterScaleGain · (stat − sizeScatterScaleRef)` is a multiplied zero
 *     at every value of the statistic and of the reference.
 *
 * The law's non-inert behaviour is exercised too, on a patched profile: a test
 * that only ever saw zeros would pass against a law that had been deleted.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  heavySecondTapSigmaAtScale,
  heavyTapSigmaAtScale,
  outerShadowReachPx,
  outerShadowSigmaPx,
  withMaterialOverrides,
} from "../src/material";

/**
 * Spans 1…1000 in CSS px. The bed's declared spans run 32…160 and a root can be
 * handed any surface at all, so the sweep covers three decades either side of
 * the material's own knee rather than the bed's own range.
 */
const SPANS = Array.from({ length: 1000 }, (_, index) => index + 1);

/** The two device ratios the material is anchored at, and one between them. */
const RATIOS = [1, 1.5, 2, 3] as const;

const SHADOW = DEFAULT_MATERIAL_PROFILE.outerShadow;

describe("W30's σ law is the identity at the shipped leaves (claims §5.156 §2, §5.158)", () => {
  it("ships all three leaves at 0", () => {
    expect(SHADOW.sigmaSlopePerSpan).toBe(0);
    expect(SHADOW.sigmaSpanRefPx).toBe(0);
    expect(SHADOW.sigmaThinOffsetPx).toBe(0);
  });

  it("returns exactly sigmaPx at every span from 1 to 1000", () => {
    for (const spanPx of SPANS) {
      expect(outerShadowSigmaPx(SHADOW, spanPx), `span ${String(spanPx)}`).toBe(SHADOW.sigmaPx);
    }
  });

  it("returns exactly sigmaPx at a zero, a negative and an enormous span", () => {
    // The law takes whatever the caller has. A group with no members resolves a
    // span of 0; `sampledOuterShadowFactor`'s default is 0; a surface measured
    // mid-layout can be anything. None of them may be a special case.
    for (const spanPx of [0, -1, -10_000, 1e6, Number.MAX_SAFE_INTEGER]) {
      expect(outerShadowSigmaPx(SHADOW, spanPx), `span ${String(spanPx)}`).toBe(SHADOW.sigmaPx);
    }
  });

  it("takes no device ratio, so both scales read one width", () => {
    // The cut rejected the device-px reading of the thin regime in both
    // directions (claims §5.156 §2), so the law has no dpr argument at all and
    // there is no second length convention for the CSS tier to mirror. Stated as
    // a case because "the function has no such parameter" is the claim.
    expect(outerShadowSigmaPx.length).toBe(2);
  });

  it("leaves the reach exactly where it was, at every span and every amplitude", () => {
    // `outerShadowReachPx` gained a span argument, and the pad is what stops the
    // optics pass slicing the facet off at the scissor. At the inert leaves the
    // span may not reach it.
    for (const occlusion of [0, 1 / 512, 0.05, 0.127, 0.33, 0.37, 0.448, 0.479, 1]) {
      const base = outerShadowReachPx(SHADOW, occlusion);
      for (const spanPx of [0, 1, 32, 44, 96, 128, 130, 160, 320, 1000]) {
        expect(
          outerShadowReachPx(SHADOW, occlusion, spanPx),
          `occlusion ${String(occlusion)} / span ${String(spanPx)}`,
        ).toBe(base);
      }
    }
  });

  it("is not a deleted law: a fitted slope grades σ and the reach with the span", () => {
    // The fail-before half. §5.159 fits about 0.133 per CSS px with the
    // reference held at 96 (W30 Decision Log 3 (c)) and a floor below the knee,
    // so the law is exercised at the shape the fit will take.
    const fitted = {
      ...SHADOW,
      sigmaPx: 8.8,
      sigmaSlopePerSpan: 0.133,
      sigmaSpanRefPx: 96,
      sigmaThinOffsetPx: -7,
    };
    expect(outerShadowSigmaPx(fitted, 96)).toBe(8.8);
    expect(outerShadowSigmaPx(fitted, 160)).toBeCloseTo(8.8 + 0.133 * 64, 10);
    // Below the knee the floor holds it, and the knee is where the two arms
    // meet: `sigmaSpanRefPx + sigmaThinOffsetPx / sigmaSlopePerSpan`.
    const knee = 96 + -7 / 0.133;
    expect(outerShadowSigmaPx(fitted, knee - 10)).toBe(8.8 - 7);
    expect(outerShadowSigmaPx(fitted, knee + 10)).toBeCloseTo(8.8 + 0.133 * (knee + 10 - 96), 10);
    // And the reach follows it, which is what X8's two-sided recomputation is.
    expect(outerShadowReachPx(fitted, 0.293, 160)).toBeGreaterThan(
      outerShadowReachPx(fitted, 0.293, 44),
    );
  });
});

describe("W30's scatter leaves are inert at the shipped values (claims §5.156 §3, §5.158)", () => {
  it("ships all five at 0", () => {
    expect(DEFAULT_MATERIAL_PROFILE.sizeHeavySecondSigma).toBe(0);
    expect(DEFAULT_MATERIAL_PROFILE.sizeHeavySecondSigma2x).toBe(0);
    expect(DEFAULT_MATERIAL_PROFILE.sizeHeavySecondShare).toBe(0);
    expect(DEFAULT_MATERIAL_PROFILE.sizeScatterScaleGain).toBe(0);
    expect(DEFAULT_MATERIAL_PROFILE.sizeScatterScaleRef).toBe(0);
  });

  it("asks for no second heavy width at any device ratio", () => {
    for (const dpr of RATIOS) {
      expect(heavySecondTapSigmaAtScale(DEFAULT_MATERIAL_PROFILE, dpr), `dpr ${String(dpr)}`).toBe(
        0,
      );
    }
  });

  it("asks for none even where a profile names both widths, because the share gates it", () => {
    // The share is the SINGLE off condition (claims §5.158). A width named
    // beside a zero share must produce nothing at all — W26 Decision Log 6 (c)
    // is what happens when a near-zero width is read as a switch instead.
    const widthsOnly = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeHeavySecondSigma: 18,
      sizeHeavySecondSigma2x: 24,
    });
    for (const dpr of RATIOS) {
      expect(heavySecondTapSigmaAtScale(widthsOnly, dpr), `dpr ${String(dpr)}`).toBe(0);
    }
    // And the FIRST heavy width is untouched by any of it, which is what says
    // the second mechanism is beside the first rather than over it.
    for (const dpr of RATIOS) {
      expect(heavyTapSigmaAtScale(widthsOnly, dpr)).toBe(
        heavyTapSigmaAtScale(DEFAULT_MATERIAL_PROFILE, dpr),
      );
    }
  });

  it("is not a deleted mechanism: a share opens the width at both anchors", () => {
    const on = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeHeavySecondSigma: 18,
      sizeHeavySecondSigma2x: 24,
      sizeHeavySecondShare: -0.25,
    });
    expect(heavySecondTapSigmaAtScale(on, 1)).toBe(18);
    expect(heavySecondTapSigmaAtScale(on, 2)).toBe(24);
    expect(heavySecondTapSigmaAtScale(on, 1.5)).toBeGreaterThan(18);
    expect(heavySecondTapSigmaAtScale(on, 1.5)).toBeLessThan(24);
  });

  it("contributes exactly zero to kScatter at every statistic the analysis pass can read", () => {
    /*
     * The shader evaluates `kScatter + gain · (stat − ref)` and clamps. The gain
     * is 0, so the added term is a multiplied zero at every statistic and every
     * reference — restated here as arithmetic, because the shader's copy of it
     * cannot be called from a unit test and the claim is about the value rather
     * than about the language it is written in. The clamp that follows is the
     * identity on a value already clamped to the same interval, which is what
     * makes the shader's line bit-identical and not merely close.
     */
    const { sizeScatterScaleGain: gain, sizeScatterScaleRef: ref } = DEFAULT_MATERIAL_PROFILE;
    for (const stat of [0, 1e-9, 0.001, 0.05, 0.5, 1, 17, 1e6]) {
      expect(gain * (stat - ref), `edge density ${String(stat)}`).toBe(0);
      for (const kScatter of [0, 0.25, 0.4, 0.6, 1]) {
        expect(Math.min(1, Math.max(0, kScatter + gain * (stat - ref)))).toBe(kScatter);
      }
    }
  });
});
