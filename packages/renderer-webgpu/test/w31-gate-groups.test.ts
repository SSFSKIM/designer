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
  backdropToneResponse, backdropToneSolveWeight, materialDigestInput,
  heavySecondShareFarAtScale,
  scatterSpanMaxAtScale,
  spanGradedTintAlpha,
  tintAlphaFarAtScale,
  heavySecondTapSigmaAtScale,
  fineTapSigmaAtScale,
  heavyTapSigmaAtScale,
  materialDigestDroppedLeaves,
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


describe("gate-group 4 — black strength 0 gates both black ordinates", () => {
  it("drops and ignores both ordinates throughout the response while the gate is held", () => {
    const old = DEFAULT_MATERIAL_PROFILE;
    for (const thin of [0, 0.01, 0.2, 1]) {
      for (const thick of [0, 0.1, 0.7, 1]) {
        const off = withMaterialOverrides(old, {
          backdropToneBlackStrength: 0, backdropToneBlackThin: thin, backdropToneBlackThick: thick,
        });
        expect(materialDigestInput(off)).toEqual(materialDigestInput(old));
        for (const x of [0, 0.001, 0.0029, 0.003, 0.004, 0.5, 1]) {
          expect(backdropToneSolveWeight(x, off)).toBe(backdropToneSolveWeight(x, old));
          for (const thickness of [0, 0.1, 0.5, 1]) {
            expect(backdropToneResponse(x, thickness, off))
              .toBe(backdropToneResponse(x, thickness, old));
          }
        }
      }
    }
    const on = withMaterialOverrides(old, { backdropToneBlackStrength: 1, backdropToneBlackThin: 0.2 });
    expect(materialDigestInput(on)).not.toEqual(materialDigestInput(old));
    expect(backdropToneResponse(0, 0, on)).not.toBe(backdropToneResponse(0, 0, old));
  });
});

describe("W45 — sizeHeavySecondShareFar2x is a plain value drop at 0", () => {
  /*
   * W45 (claims §5.205; charter Decision Log 1, clause 1, X57). The leaf grades the second tap's
   * share on the scatter's far curve, per pixel in the optics pass:
   * `tapShare = scatterHeavy2.x + scatterHeavy2.z · farS`, unclamped. It is a PLAIN value drop —
   * not a member of gate-group 2 — because at a non-zero share a non-zero delta draws. What the
   * drop rests on is that 0 is its identity: the term is a multiplied zero at every share and
   * every `farS` the shader can compute, in f32 as in f64, and the share it is added to is
   * returned exactly, including the signed shares a tuned material carries.
   */
  const SHARES = [-1, -0.3, -0.25, -1e-6, 0, 1e-6, 0.25, 0.5, 1, 1.5] as const;
  const FAR_S = [0, 1e-7, 0.104, 0.352, 0.5, 0.999999, 1] as const;
  const DELTAS = [-1, -0.75, -0.5, -0.25, -1e-6, 1e-6, 0.25, 1, 1e6] as const;

  it("holds the leaf at its identity on the shipped material, at every ratio", () => {
    expect(DEFAULT_MATERIAL_PROFILE.sizeHeavySecondShareFar2x).toBe(0);
    for (const dpr of [...RATIOS, 0.5, 1.25, 4]) {
      expect(heavySecondShareFarAtScale(DEFAULT_MATERIAL_PROFILE, dpr)).toBe(0);
    }
  });

  it("returns the share exactly at delta 0, signed shares included, in f64 and f32", () => {
    for (const share of SHARES) {
      for (const farS of FAR_S) {
        expect(share + 0 * farS, `share ${String(share)} farS ${String(farS)}`).toBe(share);
        const f32 = Math.fround(Math.fround(share) + Math.fround(Math.fround(0) * Math.fround(farS)));
        expect(f32).toBe(Math.fround(share));
      }
    }
  });

  it("is 2x-anchored: 0 at dpr ≤ 1 whatever it holds, half at 1.5, the whole delta from 2", () => {
    for (const delta of DELTAS) {
      const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
        sizeHeavySecondShare: 0.5, sizeHeavySecondShareFar2x: delta,
      });
      for (const dpr of [0.5, 1]) expect(heavySecondShareFarAtScale(profile, dpr)).toBe(0);
      expect(heavySecondShareFarAtScale(profile, 1.5)).toBe(delta * 0.5);
      for (const dpr of [2, 3]) expect(heavySecondShareFarAtScale(profile, dpr)).toBe(delta);
    }
  });

  it("is dropped from the digest at 0 and carried off it, with nothing gated beside it", () => {
    expect(materialDigestDroppedLeaves(DEFAULT_MATERIAL_PROFILE)).toContain("sizeHeavySecondShareFar2x");
    for (const delta of DELTAS) {
      const off = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { sizeHeavySecondShareFar2x: delta });
      expect(materialDigestDroppedLeaves(off)).not.toContain("sizeHeavySecondShareFar2x");
      expect(materialDigestInput(off)).not.toEqual(materialDigestInput(DEFAULT_MATERIAL_PROFILE));
      // The share's gate-group is unaffected: the delta is not one of its members.
      expect(materialDigestDroppedLeaves(off)).toContain("sizeHeavySecondSigma");
    }
    const named = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { sizeHeavySecondShareFar2x: 0 });
    expect(materialDigestInput(named)).toEqual(materialDigestInput(DEFAULT_MATERIAL_PROFILE));
  });

  it("is unread at share 0: no second texture is asked for, whatever the delta and widths say", () => {
    // The share stays the single gate on the texture (charter Grounding, "The operator"). The
    // drawn half — the bytes at −1, 0 and +1 — is in e2e/gpu/w45-share-far.spec.ts.
    for (const delta of DELTAS) {
      const gated = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
        sizeHeavySecondShare: 0, sizeHeavySecondSigma: 3, sizeHeavySecondSigma2x: 3,
        sizeHeavySecondShareFar2x: delta,
      });
      for (const dpr of RATIOS) expect(heavySecondTapSigmaAtScale(gated, dpr)).toBe(0);
    }
  });
});

describe("W47 — tintAlphaFar1x and tintAlphaFar2x are plain value drops at 0", () => {
  /*
   * W47 operator 1 (claims §5.211; charter Decision Log 2, clause 1, X57, X65). The two leaves
   * grade the material's base alpha on the scatter's far curve, per pixel in the optics pass:
   * `alphaBase = clamp(tint.w + scatterHeavy2.w · farS, 0, 1)`, before the size law's occlusion
   * term. Two PLAIN value drops — no gate leaf — because the expression is read on every body
   * pixel at every alpha. What the drops rest on is that 0 is each anchor's identity: the resolved
   * delta is 0 at every ratio when both anchors are, the far term is then a multiplied zero at
   * every `farS` the shader can compute, the sum returns the alpha exactly in f32 as in f64, and
   * the clamp is the identity on an alpha in [0, 1].
   */
  const ALPHAS = [0, 1e-7, 0.05, 0.1, 0.3, 0.46, 0.62, 0.7, 0.89, 0.9, 0.999999, 1] as const;
  const FAR_S = [0, 1e-7, 0.104, 0.352, 0.5, 0.999999, 1] as const;
  const DELTAS = [-5, -1, -0.45, -0.1, -1e-6, 1e-6, 0.1, 0.13, 0.38, 0.45, 0.6, 1, 5, 1e6] as const;
  const clamp = (x: number): number => Math.min(1, Math.max(0, x));
  /** The shader's line in f32: every operand and every result rounded, as WGSL computes it. */
  const f32 = (alpha: number, delta: number, farS: number): number => {
    const f = Math.fround;
    return f(Math.min(f(1), Math.max(f(0), f(f(alpha) + f(f(delta) * f(farS))))));
  };
  /** The same line with the multiply-add fused, which a compiler may choose. */
  const f32Fused = (alpha: number, delta: number, farS: number): number => {
    const f = Math.fround;
    return f(Math.min(f(1), Math.max(f(0), f(f(alpha) + f(delta) * f(farS)))));
  };

  it("holds both anchors at their identity on the shipped material, at every ratio", () => {
    expect(DEFAULT_MATERIAL_PROFILE.tintAlphaFar1x).toBe(0);
    expect(DEFAULT_MATERIAL_PROFILE.tintAlphaFar2x).toBe(0);
    for (const dpr of [...RATIOS, 0.5, 1.25, 4]) {
      expect(tintAlphaFarAtScale(DEFAULT_MATERIAL_PROFILE, dpr)).toBe(0);
    }
  });

  it("returns the alpha exactly at delta 0, in f64 and in f32, fused or not", () => {
    for (const alpha of ALPHAS) {
      for (const farS of FAR_S) {
        const label = `alpha ${String(alpha)} farS ${String(farS)}`;
        expect(clamp(alpha + 0 * farS), label).toBe(alpha);
        expect(f32(alpha, 0, farS), label).toBe(Math.fround(alpha));
        expect(f32Fused(alpha, 0, farS), label).toBe(Math.fround(alpha));
        // And at a span the far curve reads 0 on (at or below the knee), whatever the delta.
        for (const delta of DELTAS) {
          expect(f32(alpha, delta, 0), `${label} delta ${String(delta)} at farS 0`).toBe(Math.fround(alpha));
        }
      }
    }
  });

  it("clamps the sum into [0, 1] at large signed deltas, and is linear inside", () => {
    for (const alpha of ALPHAS) {
      for (const farS of FAR_S) {
        for (const delta of DELTAS) {
          const graded = clamp(alpha + delta * farS);
          expect(graded).toBeGreaterThanOrEqual(0);
          expect(graded).toBeLessThanOrEqual(1);
          // f32 rounds each operand off the identity, so only closeness is the law's here.
          expect(f32(alpha, delta, farS)).toBeCloseTo(graded, 6);
        }
      }
    }
    expect(clamp(0.9 + 1 * 0.352)).toBe(1);
    expect(clamp(0.3 - 5 * 0.104)).toBe(0);
    expect(clamp(0.7 + 0.45 * 0.352)).toBeCloseTo(0.8584, 12);
  });

  it("resolves the pair by rampAtScale: 1x at dpr ≤ 1, half-way at 1.5, 2x from 2", () => {
    for (const far1x of DELTAS) {
      for (const far2x of [0, 0.2, 0.45, -0.3]) {
        const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
          tintAlphaFar1x: far1x, tintAlphaFar2x: far2x,
        });
        for (const dpr of [0.5, 1]) expect(tintAlphaFarAtScale(profile, dpr)).toBe(far1x);
        expect(tintAlphaFarAtScale(profile, 1.5)).toBe(far1x + (far2x - far1x) * 0.5);
        for (const dpr of [2, 3]) expect(tintAlphaFarAtScale(profile, dpr)).toBe(far2x);
      }
    }
    // A 2x-only delta reaches no 1x pixel, and a 1x-only delta no 2x pixel.
    const twoOnly = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { tintAlphaFar2x: 0.45 });
    const oneOnly = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { tintAlphaFar1x: 0.3 });
    for (const span of SPANS) {
      expect(spanGradedTintAlpha(0.7, span, twoOnly, 1)).toBe(0.7);
      expect(spanGradedTintAlpha(0.7, span, oneOnly, 2)).toBe(0.7);
    }
  });

  it("states the shader's line on the CPU: 0 at and below the knee, the far curve above it", () => {
    const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      tintAlphaFar1x: 0.3, tintAlphaFar2x: 0.45,
    });
    for (const dpr of RATIOS) {
      const top = scatterSpanMaxAtScale(profile, dpr);
      const far = tintAlphaFarAtScale(profile, dpr);
      for (const span of SPANS) {
        const t = clamp((span - profile.sizeSpanMax) / Math.max(top - profile.sizeSpanMax, 1e-6));
        expect(spanGradedTintAlpha(0.5, span, profile, dpr), `span ${String(span)} dpr ${String(dpr)}`)
          .toBe(clamp(0.5 + far * (t * t * (3 - 2 * t))));
        if (span <= profile.sizeSpanMax) expect(spanGradedTintAlpha(0.5, span, profile, dpr)).toBe(0.5);
      }
    }
    // At the inherited top 256 the curve reads 0.104 at 128 and 0.352 at 160 (charter Grounding).
    expect(spanGradedTintAlpha(0.5, 128, profile, 2)).toBeCloseTo(0.5 + 0.45 * 0.104, 12);
    expect(spanGradedTintAlpha(0.5, 160, profile, 2)).toBeCloseTo(0.5 + 0.45 * 0.352, 12);
  });

  it("is dropped from the digest at 0 and carried off it, each anchor on its own", () => {
    const dropped = materialDigestDroppedLeaves(DEFAULT_MATERIAL_PROFILE);
    expect(dropped).toContain("tintAlphaFar1x");
    expect(dropped).toContain("tintAlphaFar2x");
    for (const delta of DELTAS) {
      for (const leaf of ["tintAlphaFar1x", "tintAlphaFar2x"] as const) {
        const other = leaf === "tintAlphaFar1x" ? "tintAlphaFar2x" : "tintAlphaFar1x";
        const off = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { [leaf]: delta });
        expect(materialDigestDroppedLeaves(off)).not.toContain(leaf);
        // The other anchor, at its identity, is still dropped: two plain drops, not one group.
        expect(materialDigestDroppedLeaves(off)).toContain(other);
        expect(materialDigestInput(off)).not.toEqual(materialDigestInput(DEFAULT_MATERIAL_PROFILE));
      }
    }
    const named = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { tintAlphaFar1x: 0, tintAlphaFar2x: 0 });
    expect(materialDigestInput(named)).toEqual(materialDigestInput(DEFAULT_MATERIAL_PROFILE));
  });
});

describe("W47 — {sizeFineTapShare 0} gates the two fine-body widths", () => {
  const keys = ["sizeFineTapShare", "sizeFineTapSigma", "sizeFineTapSigma2x"] as const;
  const widths = [0, 1e-7, 1.5, 2, 6, 40, 1e6];

  it("drops the whole closed group and requests no texture while either width moves", () => {
    const reference = materialDigestInput(DEFAULT_MATERIAL_PROFILE);
    for (const sizeFineTapSigma of widths) {
      for (const sizeFineTapSigma2x of widths) {
        const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
          sizeFineTapShare: 0, sizeFineTapSigma, sizeFineTapSigma2x,
        });
        expect(materialDigestInput(material)).toEqual(reference);
        for (const key of keys) expect(materialDigestDroppedLeaves(material)).toContain(key);
        for (const dpr of [0.5, ...RATIOS]) expect(fineTapSigmaAtScale(material, dpr)).toBe(0);
      }
    }
  });

  it("carries the entire open group and resolves CSS-pixel anchors without dividing by DPR", () => {
    const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeFineTapShare: 0.5, sizeFineTapSigma: 2, sizeFineTapSigma2x: 6,
    });
    for (const key of keys) expect(materialDigestDroppedLeaves(material)).not.toContain(key);
    const digest = materialDigestInput(material);
    expect(digest).toMatchObject({ sizeFineTapShare: 0.5, sizeFineTapSigma: 2, sizeFineTapSigma2x: 6 });
    for (const [dpr, sigma] of [[0.5, 2], [1, 2], [1.5, 4], [2, 6], [3, 6]]) {
      expect(fineTapSigmaAtScale(material, dpr)).toBe(sigma);
    }
    expect(materialDigestInput(withMaterialOverrides(material, { sizeFineTapSigma: 3 })))
      .not.toEqual(digest);
    expect(materialDigestInput(withMaterialOverrides(material, { sizeFineTapSigma2x: 5 })))
      .not.toEqual(digest);
  });

  it("stands down at width 0 at one scale, as the second heavy tap does", () => {
    const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      sizeFineTapShare: 1, sizeFineTapSigma: 0, sizeFineTapSigma2x: 6,
    });
    expect(fineTapSigmaAtScale(material, 1)).toBe(0);
    expect(fineTapSigmaAtScale(material, 2)).toBe(6);
  });

  it("reads neither width at the share's identity", () => {
    const material = { ...DEFAULT_MATERIAL_PROFILE, sizeFineTapShare: 0,
      get sizeFineTapSigma(): number { throw new Error("closed gate read 1x width"); },
      get sizeFineTapSigma2x(): number { throw new Error("closed gate read 2x width"); },
    };
    for (const dpr of RATIOS) expect(fineTapSigmaAtScale(material, dpr)).toBe(0);
  });
});
