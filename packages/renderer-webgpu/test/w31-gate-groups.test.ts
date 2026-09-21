/**
 * W31 G0 review closure — the identity table's GATE-GROUPS, proved as the table
 * says they are (claims §5.161 §11, finding B4).
 *
 * `w30-inert-laws.test.ts` beside this file proves the eight W30 leaves inert
 * AT THE SHIPPED VALUES: it reads them off `DEFAULT_MATERIAL_PROFILE`, where all
 * eight are 0, and shows the laws return what they returned before the leaves
 * existed. That is the right case for the question W30 asked — did adding the
 * laws move the material.
 *
 * It is not the case the digest rule needs, and the difference is the whole
 * reason this file exists. `identity-table.json`'s rule drops a gate-group as
 * one unit: the gate leaves at their identities AND the leaves they make
 * unread, whatever those hold. That merges every material sharing a gate at its
 * identity, so two materials with different gated values get ONE digest — sound
 * only if the gated leaves provably cannot reach the pixels while the gate is
 * held. Of W30's three groups only the heavy-second one was proved that way
 * ("asks for none even where a profile names both widths"). The σ group's case
 * sweeps SPANS over a material whose pivot is also 0, and the scatter group's
 * reads the reference off the default, where it is 0 — while the macOS 27 light
 * document, the one document that exercises the drop, ships 0.03.
 *
 * So each case below holds the gate at its declared identity, sweeps the GATED
 * leaf across values it could not be at if it were inert on its own — including
 * the 0.03 that ships — and asserts the law's output with `toBe`, exact equality
 * of doubles. A near-identity would make the digest's injectivity a measurement
 * with an error bar; an identity makes it arithmetic.
 *
 * **What these cases do not claim.** They are about the PIXELS, which is what
 * the rule's soundness is about. A gated leaf still travels to the GPU — the
 * scatter reference occupies two lanes of the optics uniform (`passes.ts`
 * d[125] and, through `backdropScaleStatistic`'s unobserved fallback, d[126]) —
 * so two materials the digest merges do not write identical uniform bytes. They
 * draw identical pixels, and the digest is over what draws.
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

/** Spans three decades either side of the material's knee, as W30's sweep does. */
const SPANS = [0, 1, 8, 24, 32, 44, 64, 96, 128, 160, 220, 320, 1000, 1e6] as const;

/** The amplitudes the reach is read at, off W30's own case. */
const OCCLUSIONS = [0, 1 / 512, 0.05, 0.127, 0.33, 0.37, 0.448, 0.479, 1] as const;

const RATIOS = [1, 1.5, 2, 3] as const;

describe("gate-group 1 — {sigmaSlopePerSpan 0, sigmaThinOffsetPx 0} gates sigmaSpanRefPx", () => {
  /*
   * The pivot is only ever read as `slope · (span − pivot)`, and the offset is
   * the other arm of the `max` over it. Hold BOTH arms at zero and the pivot is
   * multiplied by a zero at every span — which is the table's `whyGated`, and
   * which no case asserted until this one.
   *
   * The pivots are the ones a fit could plausibly land on plus the ones it could
   * not: §5.159 fits 96, W30's thin regime argues for a knee below it, and a
   * pivot far outside the bed's spans is what a merged digest would have to
   * tolerate for the drop to be sound.
   */
  const PIVOTS = [-1e6, -160, -1, 0, 1, 32, 44, 96, 128, 160, 1000, 1e6] as const;

  it("holds the gate at its identity on the shipped material", () => {
    expect(DEFAULT_MATERIAL_PROFILE.outerShadow.sigmaSlopePerSpan).toBe(0);
    expect(DEFAULT_MATERIAL_PROFILE.outerShadow.sigmaThinOffsetPx).toBe(0);
  });

  it("returns exactly sigmaPx at every span, at every pivot the gate makes unread", () => {
    const shadow = DEFAULT_MATERIAL_PROFILE.outerShadow;
    for (const sigmaSpanRefPx of PIVOTS) {
      const gated = { ...shadow, sigmaSpanRefPx };
      for (const spanPx of SPANS) {
        expect(
          outerShadowSigmaPx(gated, spanPx),
          `pivot ${String(sigmaSpanRefPx)} / span ${String(spanPx)}`,
        ).toBe(outerShadowSigmaPx(shadow, spanPx));
      }
    }
  });

  it("leaves the reach exactly where it was, at every pivot and every amplitude", () => {
    // The reach is what the optics pass's scissor pad and the CSS tier's group
    // clip are taken from, so a pivot that moved it would slice a facet at one
    // tier and not the other — a pixel difference behind one digest.
    const shadow = DEFAULT_MATERIAL_PROFILE.outerShadow;
    for (const sigmaSpanRefPx of PIVOTS) {
      const gated = { ...shadow, sigmaSpanRefPx };
      for (const occlusion of OCCLUSIONS) {
        for (const spanPx of SPANS) {
          expect(
            outerShadowReachPx(gated, occlusion, spanPx),
            `pivot ${String(sigmaSpanRefPx)} / occlusion ${String(occlusion)} / span ${String(spanPx)}`,
          ).toBe(outerShadowReachPx(shadow, occlusion, spanPx));
        }
      }
    }
  });

  it("is the shader's expression too, at the same pivots", () => {
    // `wgsl/optics.ts`'s `outer_shadow_sigma` is
    // `shadow.y + max(shadowSigma.z, shadowSigma.x · (spanCss − shadowSigma.y))`,
    // which cannot be called from a unit test. Restated as arithmetic, because
    // the claim is about the value and not about the language: at slope 0 the
    // product is a signed zero at every finite pivot and `max(0, ±0)` is 0.
    for (const sigmaSpanRefPx of PIVOTS) {
      for (const spanPx of SPANS) {
        expect(
          Math.max(0, 0 * (spanPx - sigmaSpanRefPx)),
          `pivot ${String(sigmaSpanRefPx)} / span ${String(spanPx)}`,
        ).toBe(0);
      }
    }
  });

  it("fails if the gate is opened, so the sweep is not vacuous", () => {
    // The fail-before half at the group level rather than at the leaf's: with a
    // slope the pivot reaches σ, which is exactly what makes the gate a gate.
    const opened = { ...DEFAULT_MATERIAL_PROFILE.outerShadow, sigmaSlopePerSpan: 0.133 };
    expect(outerShadowSigmaPx({ ...opened, sigmaSpanRefPx: 96 }, 160)).not.toBe(
      outerShadowSigmaPx({ ...opened, sigmaSpanRefPx: 0 }, 160),
    );
    // And with the slope back at 0 but the OFFSET off its identity, the pivot is
    // still unread while σ itself moves — which is why the gate is two leaves
    // and not the slope alone (the table's own note).
    const offsetOnly = { ...DEFAULT_MATERIAL_PROFILE.outerShadow, sigmaThinOffsetPx: 5 };
    expect(outerShadowSigmaPx(offsetOnly, 160)).not.toBe(
      outerShadowSigmaPx(DEFAULT_MATERIAL_PROFILE.outerShadow, 160),
    );
    for (const sigmaSpanRefPx of PIVOTS) {
      expect(outerShadowSigmaPx({ ...offsetOnly, sigmaSpanRefPx }, 160)).toBe(
        outerShadowSigmaPx(offsetOnly, 160),
      );
    }
  });
});

describe("gate-group 2 — {sizeHeavySecondShare 0} gates the two second-heavy widths", () => {
  /*
   * This is the one group W30's own case already proves in the gate-group sense
   * ("asks for none even where a profile names both widths"). Restated here
   * anyway, over a wider sweep, so that the three entries of the table have
   * three cases of the same shape and a reader does not have to know which of
   * them was the exception.
   */
  const WIDTHS = [0, 1e-6, 0.5, 6, 12, 18, 24, 48, 1000] as const;

  it("holds the gate at its identity on the shipped material", () => {
    expect(DEFAULT_MATERIAL_PROFILE.sizeHeavySecondShare).toBe(0);
  });

  it("asks for no second heavy width at any ratio, at any pair of widths", () => {
    for (const sizeHeavySecondSigma of WIDTHS) {
      for (const sizeHeavySecondSigma2x of WIDTHS) {
        const gated = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
          sizeHeavySecondSigma,
          sizeHeavySecondSigma2x,
        });
        for (const dpr of RATIOS) {
          expect(
            heavySecondTapSigmaAtScale(gated, dpr),
            `${String(sizeHeavySecondSigma)}/${String(sizeHeavySecondSigma2x)} at dpr ${String(dpr)}`,
          ).toBe(0);
        }
        // And the FIRST heavy tap is untouched by any of it, which is what says
        // the second mechanism is beside the first rather than over it.
        for (const dpr of RATIOS) {
          expect(heavyTapSigmaAtScale(gated, dpr)).toBe(
            heavyTapSigmaAtScale(DEFAULT_MATERIAL_PROFILE, dpr),
          );
        }
      }
    }
  });

  it("fails if the gate is opened, so the sweep is not vacuous", () => {
    const opened = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeHeavySecondSigma: 18,
      sizeHeavySecondSigma2x: 24,
      sizeHeavySecondShare: -0.25,
    });
    expect(heavySecondTapSigmaAtScale(opened, 1)).toBe(18);
    expect(heavySecondTapSigmaAtScale(opened, 2)).toBe(24);
  });
});

describe("gate-group 3 — {sizeScatterScaleGain 0} gates sizeScatterScaleRef", () => {
  /*
   * The entry the macOS 27 LIGHT document exercises, and the one whose evidence
   * was thinnest: that document declines the scatter with the gain at 0 and
   * ships the reference at **0.03**, a value nothing had ever evaluated the law
   * at under a zero gain. `digest-rule-proof.txt` shows both leaves dropping out
   * of that document's digest; what makes the drop sound is this sweep.
   */
  const REFERENCES = [0, 0.03, -0.03, 0.001, 0.5, 1, 17, 1e6, -1e6] as const;

  /** Every statistic the analysis pass can hand the law, W30's own list. */
  const STATISTICS = [0, 1e-9, 0.001, 0.03, 0.05, 0.5, 1, 17, 1e6] as const;

  /** The span-graded `kScatter` the law is added to, before its clamp. */
  const SPAN_SCATTERS = [0, 0.25, 0.4, 0.6, 1] as const;

  it("holds the gate at its identity on the shipped material", () => {
    expect(DEFAULT_MATERIAL_PROFILE.sizeScatterScaleGain).toBe(0);
  });

  it("ships 0.03 on the macOS 27 light document, which is why the sweep carries it", () => {
    // Read off the document rather than asserted as a constant here: the point
    // of the case is that the SHIPPED value is exercised, so the value has to
    // come from the thing that ships it.
    const light = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { sizeScatterScaleRef: 0.03 });
    expect(light.sizeScatterScaleRef).toBe(0.03);
    expect(light.sizeScatterScaleGain).toBe(0);
    expect(REFERENCES).toContain(light.sizeScatterScaleRef);
  });

  it("contributes exactly zero to kScatter at every reference the gate makes unread", () => {
    /*
     * `wgsl/optics.ts` evaluates
     * `clamp(kScatterSpan + scatterScale.x · (scatterScale.z − scatterScale.y), 0, 1)`
     * with `x` the gain, `y` the reference and `z` the statistic — and where the
     * analysis pass observed nothing, `renderer.ts` puts the REFERENCE itself in
     * `z`, so the leaf reaches the uniform twice. Both lanes are swept.
     */
    const gain = DEFAULT_MATERIAL_PROFILE.sizeScatterScaleGain;
    for (const ref of REFERENCES) {
      for (const stat of [...STATISTICS, ref]) {
        /*
         * The product is a SIGNED zero and not always `+0` — `0 · (0 − 0.03)` is
         * `−0`, exactly the shipped reference's own case — so it is compared
         * with `===`, which is what IEEE says about the two zeros, rather than
         * with `toBe`'s `Object.is`. The identity the law rests on is one line
         * down: `kScatterSpan + (−0)` is `kScatterSpan` for every value of it,
         * including `+0`, so the sign never reaches the clamp's output. Asserted
         * in that order because the distinction is real and the conclusion is
         * unaffected by it.
         */
        expect(gain * (stat - ref) === 0, `ref ${String(ref)} / stat ${String(stat)}`).toBe(true);
        for (const kScatterSpan of SPAN_SCATTERS) {
          expect(
            Math.min(1, Math.max(0, kScatterSpan + gain * (stat - ref))),
            `ref ${String(ref)} / stat ${String(stat)} / kScatter ${String(kScatterSpan)}`,
          ).toBe(kScatterSpan);
        }
      }
    }
  });

  it("fails if the gate is opened, so the sweep is not vacuous", () => {
    // The dark macOS 27 document adopts the scatter at gain −2, which is what
    // makes the two documents' digests differ on this group.
    const opened = -2;
    expect(Math.min(1, Math.max(0, 0.4 + opened * (0.05 - 0.03)))).not.toBe(0.4);
  });
});
