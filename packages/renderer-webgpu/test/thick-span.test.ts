/**
 * W25's thick-span composite — the three mechanisms' shape, not their values
 * (claims §5.113; W25 Decision Log 3).
 *
 * The wave lands three terms and lands them INERT, so what this file pins is
 * what each of them is for and what none of them may reach:
 *
 *  1. **Inert at the defaults.** Each term is one multiplication by zero on top
 *     of a law an earlier wave fitted, so the resolved material renders the W24
 *     bed to the bit. The pins here are on the arithmetic; the 33 renderer
 *     goldens are the pin on the pixels.
 *  2. **The thin end does not move.** `sizeThickness` is exactly 0 at and below
 *     `sizeSpanMin`, so the share law and the along-side field are the identity
 *     on `rrect-sm` and on every smaller control at EVERY value of their
 *     constants — X5 discharged by the shape of the formula rather than by a
 *     capture, which is what lets a fit run without a thin cell at risk.
 *  3. **The field is antisymmetric, and its side mean is zero.** The reference's
 *     four sides read equal and opposite slopes, which a field linear in
 *     position cannot be; and because the product of the two normalised
 *     coordinates is odd along every side, W23's and W24's straight-span
 *     amplitudes keep the meaning they were fitted with and the CSS tier's one
 *     inset is coherent with the GPU tier's side mean without carrying the term.
 *  4. **The level term is exactly 0 at and below `sizeSpanMax`.** A smoothstep is
 *     zero at and below its own low edge, so no cell at or under span 96 can move
 *     on this constant however large it is — which is what makes the term
 *     fittable above the knee without touching the bed the rest of the material
 *     was fitted on.
 *
 * The fitted values are asserted nowhere here, on purpose: G2 fitted them to
 * scratch and G3 declares them against the bed.
 */

import { describe, expect, it } from "vitest";

import {
  backdropToneResponse,
  DEFAULT_MATERIAL_PROFILE,
  rimAlongSideFactor,
  rimAlongSideField,
  scatterDeepThickness,
  scatterHeavyShareThickAtScale,
  scatterThickness,
  sizeScatterSigma,
  sizeThickness,
  sizeToneLevelFar,
  withMaterialOverrides,
} from "../src/material";
import { WGSL_OPTICS_PASS } from "../src/wgsl";

const P = DEFAULT_MATERIAL_PROFILE;
const SPANS = [8, 16, 32, 44, 64, 96, 128, 130, 160, 256, 512];

describe("W25 the share law", () => {
  it("is inert at the default: the deep value is the curve W11c fitted", () => {
    // The default is 0 at both anchors, so `scatterHeavyShareThickAtScale` is the
    // constant zero and `kDeep` is `floor + (1 − floor) · smoothstep(…)` exactly.
    for (const dpr of [1, 1.5, 2, 3]) {
      expect(scatterHeavyShareThickAtScale(P, dpr)).toBe(0);
    }
    const floor = P.sizeScatterFloor;
    const t = (96 - P.sizeSpanMin) / (P.sizeScatterSpanMax - P.sizeSpanMin);
    const expected = floor + (1 - floor) * (t * t * (3 - 2 * t));
    expect(scatterDeepThickness(96, P, 1)).toBeCloseTo(expected, 12);
  });

  it("rides `sizeThickness`, so the thin end cannot move at any lift (X5)", () => {
    for (const lift of [0.1, 0.25, 0.5, 1]) {
      const lifted = withMaterialOverrides(P, { sizeScatterHeavyShareThick1x: lift });
      for (const span of [0, 8, 16, 31, 32]) {
        // Exactly equal, not close: `sizeThickness` returns a hard 0 below the
        // band and the term is a multiplication by it.
        expect(scatterDeepThickness(span, lifted, 1)).toBe(scatterDeepThickness(span, P, 1));
        expect(sizeScatterSigma(1.25, span, lifted, 1)).toBe(sizeScatterSigma(1.25, span, P, 1));
      }
    }
  });

  it("lifts the thick end by exactly `lift · sizeThickness`, clamped to one", () => {
    const lift = 0.2;
    const lifted = withMaterialOverrides(P, { sizeScatterHeavyShareThick1x: lift });
    for (const span of SPANS) {
      const base = scatterDeepThickness(span, P, 1);
      const want = Math.min(1, base + lift * sizeThickness(span, P));
      expect(scatterDeepThickness(span, lifted, 1)).toBeCloseTo(want, 12);
    }
  });

  it("takes its second anchor at dpr 2 and reads the first below dpr 1", () => {
    const both = withMaterialOverrides(P, {
      sizeScatterHeavyShareThick1x: 0.2,
      sizeScatterHeavyShareThick2x: 0.6,
    });
    expect(scatterHeavyShareThickAtScale(both, 0.5)).toBeCloseTo(0.2, 12);
    expect(scatterHeavyShareThickAtScale(both, 1)).toBeCloseTo(0.2, 12);
    expect(scatterHeavyShareThickAtScale(both, 1.5)).toBeCloseTo(0.4, 12);
    expect(scatterHeavyShareThickAtScale(both, 2)).toBeCloseTo(0.6, 12);
    expect(scatterHeavyShareThickAtScale(both, 4)).toBeCloseTo(0.6, 12);
  });

  it("keeps the mix monotone in span and inside 0…1", () => {
    const lifted = withMaterialOverrides(P, { sizeScatterHeavyShareThick1x: 0.35 });
    let previous = -Infinity;
    for (const span of SPANS) {
      const k = scatterDeepThickness(span, lifted, 1);
      expect(k).toBeGreaterThanOrEqual(0);
      expect(k).toBeLessThanOrEqual(1);
      expect(k).toBeGreaterThanOrEqual(previous - 1e-12);
      previous = k;
      expect(scatterThickness(span, 1, lifted, 1)).toBeLessThanOrEqual(1);
    }
  });
});

describe("W25 the level term above the knee", () => {
  it("is inert at the default and exactly 0 at and below `sizeSpanMax`", () => {
    for (const span of SPANS) {
      expect(sizeToneLevelFar(span, P, 1)).toBe(0);
    }
    const moved = withMaterialOverrides(P, { sizeToneLevelFar: 3 });
    for (const span of [0, 32, 44, 64, 95.999, 96]) {
      expect(sizeToneLevelFar(span, moved, 1)).toBe(0);
    }
    for (const span of [97, 128, 160, 256]) {
      expect(sizeToneLevelFar(span, moved, 1)).toBeGreaterThan(0);
    }
  });

  it("leaves the tone response BIT-identical at every span on the shipped material", () => {
    // The inertness pin the golden suite cannot give on its own: on the landed
    // profile `sizeToneLevelFar` resolves to 0 at every span and every ratio, so
    // the offset is `+ 0.0` and the curve returns the same float it did before
    // the term existed. Exact equality, not closeness.
    for (const span of SPANS) {
      for (const dpr of [1, 1.5, 2, 3]) {
        const far = sizeToneLevelFar(span, P, dpr);
        expect(far).toBe(0);
        for (const x of [0, 0.05, 0.11, 0.3, 0.5, 0.74, 0.95, 1]) {
          for (const thickness of [0, 0.0923, 0.5, 1]) {
            expect(backdropToneResponse(x, thickness, P, far)).toBe(
              backdropToneResponse(x, thickness, P),
            );
          }
        }
      }
    }
  });

  it("leaves the tone response untouched at every span at or under the knee", () => {
    // The response is the law that owns the interior mean, and the term is a
    // continuation of its own thin-to-thick blend. Below the knee the
    // continuation is zero, so the curve is the one W9 fitted, bit for bit.
    const moved = withMaterialOverrides(P, { sizeToneLevelFar: 1.5 });
    for (const x of [0.05, 0.11, 0.3, 0.5, 0.74, 0.95, 1]) {
      for (const span of [32, 44, 96]) {
        const thick = sizeThickness(span, moved);
        const far = sizeToneLevelFar(span, moved, 1);
        expect(backdropToneResponse(x, thick, moved, far)).toBe(
          backdropToneResponse(x, thick, P, 0),
        );
      }
    }
  });

  it("offsets the settled level by the same amount at every backdrop", () => {
    // Backdrop-INDEPENDENT is the shape the rows chose (`fit-level.txt`): the
    // residual against vitrea above span 96 is +2.2…+4.2 codes over backdrops
    // spanning 0.012 to 0.89 linear, where the response's own thin-to-thick step
    // points a different way at every one of them. So the term is an offset on
    // the response's output and the pin is that it is exactly that — the same
    // number at every backdrop, and the curve untouched in shape.
    const moved = withMaterialOverrides(P, { sizeToneLevelFar: 0.02 });
    const far = sizeToneLevelFar(160, moved, 1);
    expect(far).toBeGreaterThan(0);
    for (const x of [0.05, 0.11, 0.27, 0.5, 0.74, 0.95, 1]) {
      expect(backdropToneResponse(x, 1, moved, far)).toBeCloseTo(
        backdropToneResponse(x, 1, P, 0) + far,
        12,
      );
    }
    // And it is an offset on the response and not on its blend: the thin-to-thick
    // step the curve carries is the same with the term as without it.
    const step = (profile: typeof P, level: number, x: number): number =>
      backdropToneResponse(x, 1, profile, level) - backdropToneResponse(x, 0, profile, level);
    for (const x of P.backdropToneAnchorX) {
      expect(step(moved, far, x)).toBeCloseTo(step(P, 0, x), 12);
    }
  });

  it("folds with the response it extends", () => {
    const moved = withMaterialOverrides(P, { sizeToneLevelFar: 1 });
    expect(sizeToneLevelFar(160, moved, 1, 0)).toBe(0);
    expect(sizeToneLevelFar(160, moved, 1, 0.5)).toBeCloseTo(
      sizeToneLevelFar(160, moved, 1, 1) / 2,
      12,
    );
  });
});

describe("W25 the along-side field", () => {
  const half = [80, 48] as const;

  it("is +1 at the top-left and bottom-right corners and −1 at the other two", () => {
    expect(rimAlongSideField([-80, -48], half)).toBeCloseTo(1, 12);
    expect(rimAlongSideField([80, 48], half)).toBeCloseTo(1, 12);
    expect(rimAlongSideField([80, -48], half)).toBeCloseTo(-1, 12);
    expect(rimAlongSideField([-80, 48], half)).toBeCloseTo(-1, 12);
    expect(rimAlongSideField([0, 0], half)).toBe(0);
  });

  it("gives opposite sides equal and opposite slopes — the reference's own signature", () => {
    // Along the top side (y = −hh) the field falls with x; along the bottom
    // (y = +hh) it rises with x by the same amount, and likewise for left and
    // right in y. A field linear in position — `a·x + b·y` — gives the top and
    // the bottom the SAME slope, which is what the reference refutes.
    const slope = (a: readonly [number, number], b: readonly [number, number]): number =>
      (rimAlongSideField(b, half) - rimAlongSideField(a, half))
      / (b[0] - a[0] + (b[1] - a[1]));
    const top = slope([-60, -48], [60, -48]);
    const bottom = slope([-60, 48], [60, 48]);
    const left = slope([-80, -28], [-80, 28]);
    const right = slope([80, -28], [80, 28]);
    expect(top).toBeCloseTo(-bottom, 12);
    expect(left).toBeCloseTo(-right, 12);
    // And the two magnitudes stand in the box's own aspect, which is the
    // prediction G0's 0.000192 / 0.000379 pair tests.
    expect(Math.abs(left / top)).toBeCloseTo(half[0] / half[1], 12);
  });

  it("has mean zero along every straight side, so no fitted amplitude moves", () => {
    for (const side of [
      { from: [-60, -48], to: [60, -48] },
      { from: [-60, 48], to: [60, 48] },
      { from: [-80, -28], to: [-80, 28] },
      { from: [80, -28], to: [80, 28] },
    ] as const) {
      let sum = 0;
      const steps = 200;
      for (let i = 0; i <= steps; i += 1) {
        const t = i / steps;
        sum += rimAlongSideField(
          [
            side.from[0] + (side.to[0] - side.from[0]) * t,
            side.from[1] + (side.to[1] - side.from[1]) * t,
          ],
          half,
        );
      }
      expect(sum / (steps + 1)).toBeCloseTo(0, 12);
    }
  });

  it("is exactly 1 at the default slope and at every span at or below the band", () => {
    const lit = withMaterialOverrides(P, { optics: { regular: { rimAlongSideSlope: 0.7 } } });
    for (const span of SPANS) {
      expect(rimAlongSideFactor(0.8, span, P.optics.regular, P)).toBe(1);
    }
    for (const span of [0, 8, 16, 31, 32]) {
      expect(rimAlongSideFactor(0.8, span, lit.optics.regular, lit)).toBe(1);
      expect(rimAlongSideFactor(-1, span, lit.optics.regular, lit)).toBe(1);
    }
    // And at 44 — the capsule, the thin end's whole exposure — it is the
    // thickness curve's own 0.0923 of the slope and nothing more.
    expect(rimAlongSideFactor(1, 44, lit.optics.regular, lit)).toBeCloseTo(
      1 + 0.7 * sizeThickness(44, P),
      12,
    );
  });

  it("never takes the rim's amplitude negative", () => {
    const shouted = withMaterialOverrides(P, { optics: { regular: { rimAlongSideSlope: 4 } } });
    for (const field of [-1, -0.5, 0, 0.5, 1]) {
      expect(rimAlongSideFactor(field, 160, shouted.optics.regular, shouted)).toBeGreaterThanOrEqual(
        0,
      );
    }
  });
});

describe("W25 the shader carries the same three terms", () => {
  /*
   * The CPU functions above are the law and the shader is what draws it, so the
   * three terms are pinned in the WGSL text as well: a shader that lost one of
   * them would leave every unit test here green while the renderer drew the W24
   * material. Each pin is the expression itself, not a name, because a name can
   * be kept over an expression that has changed.
   */
  it("lifts kDeep on the unfolded thickness curve", () => {
    expect(WGSL_OPTICS_PASS).toContain("+ ou.thickSpan.x * sizeThick");
  });

  it("offsets the tone response's settled level on the above-knee curve", () => {
    expect(WGSL_OPTICS_PASS).toContain("let toneLevelFar = ou.thickSpan.y * farS * fold;");
    expect(WGSL_OPTICS_PASS).toContain("tone_response(encodedInput, sizeK, toneLevelFar)");
    // On the RETURN, not on the blend: the blend stays the one W9 fitted.
    expect(WGSL_OPTICS_PASS).toContain("       + levelFar;");
    expect(WGSL_OPTICS_PASS).toContain("let f = sizeK * sizeK * (3.0 - 2.0 * sizeK);");
  });

  it("grades the rim by the surface's own normalised diagonal product", () => {
    expect(WGSL_OPTICS_PASS).toContain(
      "let alongSide = clamp((rel.x / halfExt.x) * (rel.y / halfExt.y), -1.0, 1.0);",
    );
    expect(WGSL_OPTICS_PASS).toContain(
      "let alongFactor = max(1.0 + ou.rimLit.w * sizeThick * alongSide, 0.0);",
    );
  });
});
