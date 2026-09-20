/**
 * W30 G2 — the σ law's CSS-tier mirror, at the inert leaves, as an algebraic
 * identity.
 *
 * The sibling of `packages/renderer-webgpu/test/w30-inert-laws.test.ts` on the
 * other tier. The shadow is the one facet where the two tiers paint the same
 * thing by the same algebra rather than one approximating the other, so the law
 * mirrors in full and its inertness has to be stated on both sides — a law that
 * was inert in the shader and not in the `box-shadow` would be a cross-tier
 * divergence, which is worse than a moved pixel because nothing gates on it.
 *
 * `w30-css-declaration-identity.test.ts` is the other half: it compares the
 * strings this tier emits against bytes recorded before the leaves existed. This
 * file is the law underneath those strings, swept far wider than any surface a
 * document can declare.
 */

import { describe, expect, it } from "vitest";

import {
  MATERIAL_SOURCE_OUTER_SHADOW,
  outerShadowSigmaPx,
  sampledOuterShadowFactor,
} from "../src/optics";

const SHADOW = MATERIAL_SOURCE_OUTER_SHADOW;

/** Spans 1…1000 CSS px — three decades either side of the material's own knee. */
const SPANS = Array.from({ length: 1000 }, (_, index) => index + 1);

describe("W30's σ law is the identity on the CSS tier too (claims §5.156 §2, §5.158)", () => {
  it("mirrors the renderer's three leaves at 0", () => {
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
    for (const spanPx of [0, -1, -10_000, 1e6, Number.MAX_SAFE_INTEGER]) {
      expect(outerShadowSigmaPx(SHADOW, spanPx), `span ${String(spanPx)}`).toBe(SHADOW.sigmaPx);
    }
  });

  it("leaves the sampled-shadow bound where it was, at every caster span", () => {
    // The bound on what a `backdrop-filter` still samples of a neighbour's
    // shadow (W18 G0 §6) reads the same σ, now at the caster's own span. At the
    // inert leaves the argument may not reach it — over a sweep that covers
    // every span a document can declare and three decades either side of it.
    for (const signedDistanceToShadowBoxPx of [-40, -5, 0, 5, 20, 60, 200]) {
      const base = sampledOuterShadowFactor({
        shadow: SHADOW,
        alpha: 0.2,
        signedDistanceToShadowBoxPx,
        insideCaster: false,
        casterSpanPx: 0,
      });
      for (const casterSpanPx of [0, 1, 32, 44, 96, 128, 160, 320, 1000]) {
        expect(
          sampledOuterShadowFactor({
            shadow: SHADOW,
            alpha: 0.2,
            signedDistanceToShadowBoxPx,
            insideCaster: false,
            casterSpanPx,
          }),
          `d ${String(signedDistanceToShadowBoxPx)} / span ${String(casterSpanPx)}`,
        ).toBe(base);
      }
    }
  });

  it("is not a deleted law: a fitted slope grades σ and the bound with the span", () => {
    const fitted = {
      ...SHADOW,
      sigmaPx: 8.8,
      sigmaSlopePerSpan: 0.133,
      sigmaSpanRefPx: 96,
      sigmaThinOffsetPx: -7,
    };
    expect(outerShadowSigmaPx(fitted, 96)).toBe(8.8);
    expect(outerShadowSigmaPx(fitted, 160)).toBeCloseTo(8.8 + 0.133 * 64, 10);
    expect(outerShadowSigmaPx(fitted, 32)).toBe(8.8 - 7);
    // A wider caster leaves more of its shadow in a neighbour's sampled page at
    // the same distance, because the blur reaches further.
    const at = (casterSpanPx: number): number =>
      sampledOuterShadowFactor({
        shadow: fitted,
        alpha: 0.2,
        signedDistanceToShadowBoxPx: 30,
        insideCaster: false,
        casterSpanPx,
      });
    expect(at(160)).toBeLessThan(at(44));
  });
});
