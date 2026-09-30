/**
 * W42 G2 step 3, U5 — the CSS body law's reference filter, proven as ALGEBRA against the
 * renderer's CPU references (implementation-design.md §5 as revised by §11's R5; test 7).
 *
 * The program `cssTierBodyLawFilter` writes is run through an emulator of SVG's own primitive
 * semantics (`w42-svg-filter-emulator.ts`: premultiplied arithmetic that clamps every channel,
 * alpha included; un-premultiplied transfers; per-primitive colour spaces) and compared with
 * `bodyLawComposite`, `bodyToneTableCodesAt`, `bodyLawE3Codes` and `landedToneLinear` from
 * `@vitrea/renderer-webgpu`. The blurs enter as supplied values, so what is proven is the chain
 * after them; whether an engine's `feGaussianBlur` and eight-bit intermediates deliver it is
 * charter Decision Log 4's measurement and not this file's.
 *
 * The verdicts, which `u5_css_algebra.md` beside the design note states with their derivation:
 *
 * - Knees 0 and 2, both hinges, every λ in [−0.5, 1.6] and w in [0, 1], both averaging spaces:
 *   the filter's argument IS clamp(M), channel by channel, to float precision. The only clamp
 *   in the chain is the final one. Knee 0 never needs it for λ in [0, 1]; λ > 1, and knee 2's
 *   chroma carried from W, can put M outside [0, 1], where the renderer's tones read the
 *   unclamped value and the filter cannot.
 * - Knee 1: the same, off a flip set — pixels whose hinge luma difference is under one code,
 *   where a step one code wide stands for the renderer's strict comparison (R1).
 * - T2 and E3: exact in form, to the millionth the tables are written at.
 * - The landed solve: an approximation, a luma curve plus one chroma gain per level; its
 *   residual on each shipped endpoint is bounded here and recorded in the note.
 */

import { describe, expect, it } from "vitest";

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import {
  DEFAULT_MATERIAL_PROFILE,
  bodyLawComposite,
  bodyLawE3Codes,
  bodyToneTableCodesAt,
  landedToneLinear,
  withMaterialOverrides,
} from "@vitrea/renderer-webgpu";
import {
  bodyLawAffineFilterFunctions,
  bodyLawToneAffine,
  cssLandedToneInputs,
  cssTierBodyLaw,
  cssTierBodyLawFilter,
  cssTierBodyLawStacked,
  macos27MaterialProfileDocument,
  resolvedBackdropToneResponse,
  resolvedBodyLaw,
  type CssTierBodyLawFilter,
  type CssTierFilterSpace,
} from "@vitreajs/vitrea-web";

import { emulateBodyLawFilter, type SuppliedResult } from "./w42-svg-filter-emulator";

type Rgb = readonly [number, number, number];
type Patch = Parameters<typeof resolvedBodyLaw>[0] & Record<string, unknown>;

/** A seeded generator, so every run reads the same samples. */
function random(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const luma = (c: Rgb): number => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
const clamp01 = (x: number): number => Math.min(1, Math.max(0, x));
const encode = (x: number): number => {
  const c = clamp01(x);
  return c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
};

/** Random colours, plus the corners of the cube, greys and near-isoluminant pairs. */
function samples(seed: number, count: number): [Rgb, Rgb][] {
  const next = random(seed);
  const colour = (): Rgb => [next(), next(), next()];
  const pairs: [Rgb, Rgb][] = [];
  for (let i = 0; i < count; i++) pairs.push([colour(), colour()]);
  const corners: Rgb[] = [];
  for (let i = 0; i < 8; i++) corners.push([i & 1, (i >> 1) & 1, (i >> 2) & 1]);
  for (const a of corners) for (const b of corners) pairs.push([a, b]);
  for (let i = 0; i < 16; i++) {
    const g = next();
    pairs.push([[g, g, g], [next(), next(), next()]]);
    // Near-isoluminant: W moved along a luma-preserving chroma direction.
    const c = colour();
    const d = 0.05 * (next() - 0.5);
    pairs.push([c, [clamp01(c[0] + d), clamp01(c[1] - (0.2126 / 0.7152) * d), c[2]]]);
  }
  return pairs;
}

/** The law's derived filter for a patch, on one surface. */
function filterFor(patch: Patch, extents: readonly [number, number] = [160, 96], dpr = 2):
  CssTierBodyLawFilter {
  const leaves = resolvedBodyLaw(patch);
  const span = Math.min(extents[0], extents[1]);
  return cssTierBodyLawFilter(cssTierBodyLaw({
    leaves,
    strength: leaves.bodyLawStrength,
    widthCssPx: extents[0],
    heightCssPx: extents[1],
    radiusCssPx: 24,
    devicePixelRatio: dpr,
    landed: cssLandedToneInputs(patch, "regular", span, NOMINAL_ACCESSIBILITY_POLICY.material, dpr),
    response: resolvedBackdropToneResponse(patch),
  }));
}

const supplied = (filter: CssTierBodyLawFilter, C: Rgb, W: Rgb, space: CssTierFilterSpace):
  Record<string, SuppliedResult> => ({
  [filter.results.narrow]: { rgba: [C[0], C[1], C[2], 1], space },
  [filter.results.wide]: { rgba: [W[0], W[1], W[2], 1], space },
});

const LAMBDAS = [-0.5, -0.2, 0, 0.3, 0.9, 1, 1.3, 1.6] as const;
const NORMALS = [0, 0.5, 0.8, 1] as const;

describe("the knee and the Normal fill compose M with no clamp but the last (R5)", () => {
  for (const knee of [0, 1, 2] as const) {
    for (const hinge of [1, -1] as const) {
      for (const averaging of [1, 0] as const) {
        it(`knee ${knee}, hinge ${hinge}, D2 ${averaging}: the argument is clamp(M) exactly`, () => {
          const space: CssTierFilterSpace = averaging === 1 ? "sRGB" : "linearRGB";
          let compared = 0;
          let flips = 0;
          let outside = 0;
          let worst = 0;
          let convexOutside = 0;
          for (const lambda of LAMBDAS) {
            for (const normal of NORMALS) {
              const patch: Patch = {
                bodyLawStrength: 1, bodyLawKnee: knee, bodyLawHinge: hinge, bodyLawLambda: lambda,
                bodyLawNormal: normal, bodyLawEncodedAveraging: averaging, bodyLawWidthUnit: 1,
              };
              const filter = filterFor(patch);
              for (const [C, W] of samples(knee * 97 + hinge * 13 + averaging, 120)) {
                const cpu = bodyLawComposite(C, W, {
                  bodyLawLambda: lambda, bodyLawNormal: normal, bodyLawHinge: hinge,
                  bodyLawKnee: knee, bodyLawEncodedAveraging: averaging,
                });
                if (knee === 1) {
                  const difference = hinge * (luma(W) - luma(C));
                  // R1's flip set: under one code of luma difference the one-code step is a
                  // ramp where the renderer's comparison is strict.
                  if (difference > 0 && difference < 1 / 255) {
                    flips += 1;
                    continue;
                  }
                }
                const out = emulateBodyLawFilter(filter, supplied(filter, C, W, space))
                  .read(filter.results.argument);
                const expected = averaging === 1 ? cpu.argument.map(clamp01) : cpu.argument;
                if (cpu.argument.some((v) => v < 0 || v > 1)) outside += 1;
                for (let i = 0; i < 3; i++) {
                  worst = Math.max(worst, Math.abs(out[i]! - expected[i]!));
                }
                compared += 1;
                // Knee 0 at λ in [0, 1] is a convex combination: it never needs the final clamp.
                if (knee === 0 && lambda >= 0 && lambda <= 1 &&
                  cpu.argument.some((v) => v < -1e-12 || v > 1 + 1e-12)) convexOutside += 1;
              }
            }
          }
          expect(compared).toBeGreaterThan(5000);
          expect(worst).toBeLessThan(1e-9);
          expect(convexOutside).toBe(0);
          if (knee !== 1) expect(flips).toBe(0);
          // The clamp is exercised, so "exact up to the final clamp" is not vacuous. (In linear
          // light the renderer clamps M itself before encoding, so there is nothing to count.)
          if (averaging === 1) expect(outside).toBeGreaterThan(0);
        });
      }
    }
  }

  it("normalises a partial-alpha blur to its weight before any arithmetic reads it", () => {
    // The receded edge: `edgeMode="none"` leaves the blur's alpha as the kernel's weight inside
    // the box, and the opaque transfer un-premultiplies by it — `forward.py`'s num / den.
    for (const knee of [0, 1, 2] as const) {
      const patch: Patch = { bodyLawStrength: 1, bodyLawKnee: knee, bodyLawPose: 1,
        bodyLawEncodedAveraging: 1, bodyLawWidthUnit: 1 };
      const filter = filterFor(patch);
      expect(filter.parameters.edge).toBe("normalised");
      const next = random(7 + knee);
      for (let i = 0; i < 200; i++) {
        const C: Rgb = [next(), next(), next()];
        const W: Rgb = [next(), next(), next()];
        // Knee 1's flip set is the previous case's; this one is about the edge's weight.
        if (knee === 1 && Math.abs(luma(W) - luma(C)) < 1 / 255) continue;
        const weightC = 0.25 + 0.75 * next();
        const weightW = 0.25 + 0.75 * next();
        const raw = {
          [`${filter.results.narrow}-raw`]: { rgba: [C[0], C[1], C[2], weightC], space: "sRGB" },
          [`${filter.results.wide}-raw`]: { rgba: [W[0], W[1], W[2], weightW], space: "sRGB" },
        } as const satisfies Record<string, SuppliedResult>;
        const out = emulateBodyLawFilter(filter, raw).read(filter.results.argument);
        const cpu = bodyLawComposite(C, W, {
          bodyLawLambda: 0.9, bodyLawNormal: 0.5, bodyLawHinge: 1, bodyLawKnee: knee,
          bodyLawEncodedAveraging: 1,
        });
        for (let c = 0; c < 3; c++) expect(out[c]).toBeCloseTo(clamp01(cpu.argument[c]!), 9);
      }
    }
  });
});

/** Non-identity T2 and E3 leaves, the shapes a fit would produce. */
const TABLE_PATCH: Patch = {
  bodyLawStrength: 1, bodyLawEncodedAveraging: 1, bodyLawWidthUnit: 1,
  bodyToneTableStrength: 1,
  bodyToneTableCodes: [
    [0, 70, 101, 131, 161, 177, 192, 207, 222, 238, 254],
    [0, 68, 99, 130, 160, 176, 191, 207, 223, 239, 255],
    [2, 66, 97, 128, 159, 175, 191, 206, 222, 238, 253],
    [3, 64, 95, 126, 158, 174, 190, 206, 221, 237, 252],
    [4, 62, 94, 125, 157, 173, 189, 205, 221, 236, 251],
  ],
  bodyToneChromaGains: [0.8, 1.2, 1.5],
  bodyToneChromaScale: 1.3,
};

const E3_PATCH: Patch = {
  bodyLawStrength: 1, bodyLawEncodedAveraging: 1, bodyLawWidthUnit: 1,
  bodyE3Strength: 1,
  bodyE3Gains: [1.2, 0.9, 1.4],
  bodyE3Neutral: [30, 50, 70, 90, 110, 140, 165],
  bodyE3HighStrength: 1,
  bodyE3NeutralHigh: [170, 185, 200, 214, 228, 242, 252],
};

describe("T2 and E3 are the renderer's tones in form (§2.8, §2.9)", () => {
  const tones = [
    ["T2 at span 112, between two rows", TABLE_PATCH, [200, 112]],
    ["T2 at span 40, below the first row", TABLE_PATCH, [120, 40]],
    ["E3 with the F extension, g read at L(W)", E3_PATCH, [200, 112]],
  ] as const;
  for (const [name, patch, extents] of tones) {
    it(`${name}: the filter's output equals the CPU reference to the table's millionth`, () => {
      const filter = filterFor(patch, extents);
      const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch as never);
      const span = Math.min(extents[0], extents[1]);
      let worst = 0;
      for (const [A, W] of samples(31, 600)) {
        const out = emulateBodyLawFilter(filter, {
          [filter.results.argument]: { rgba: [A[0], A[1], A[2], 1], space: "sRGB" },
          [filter.results.wide]: { rgba: [W[0], W[1], W[2], 1], space: "sRGB" },
        }).output;
        const codes: Rgb = [A[0] * 255, A[1] * 255, A[2] * 255];
        const expected = filter.parameters.tone.kind === "table"
          ? bodyToneTableCodesAt(codes, span, material)
          : bodyLawE3Codes(codes, luma(W) * 255, material);
        for (let c = 0; c < 3; c++) worst = Math.max(worst, Math.abs(out[c]! * 255 - expected[c]!));
      }
      // One millionth of an encoded unit per table entry, times the largest gain.
      expect(worst).toBeLessThan(5e-3);
    });
  }

  it("composes end to end: two blurs to T2's codes, wherever the renderer's M is in range", () => {
    const filter = filterFor(TABLE_PATCH, [200, 112]);
    const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, TABLE_PATCH as never);
    let compared = 0;
    let worst = 0;
    for (const [C, W] of samples(5, 800)) {
      const cpu = bodyLawComposite(C, W, material);
      if (cpu.argument.some((v) => v < 0 || v > 1)) continue;
      const expected = bodyToneTableCodesAt(
        [cpu.argument[0] * 255, cpu.argument[1] * 255, cpu.argument[2] * 255], 112, material);
      const out = emulateBodyLawFilter(filter, supplied(filter, C, W, "sRGB")).output;
      for (let c = 0; c < 3; c++) worst = Math.max(worst, Math.abs(out[c]! * 255 - expected[c]!));
      compared += 1;
    }
    expect(compared).toBeGreaterThan(700);
    expect(worst).toBeLessThan(5e-3);
  });

  it("mixes a fractional T2 over E3 in linear light, the renderer's convention", () => {
    const patch: Patch = { ...E3_PATCH, ...TABLE_PATCH, bodyToneTableStrength: 0.4 };
    const filter = filterFor(patch, [200, 112]);
    expect(filter.parameters.tone.kind).toBe("table");
    expect(filter.parameters.tone.below?.tone.kind).toBe("e3");
    const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch as never);
    const decode = (x: number): number => (x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4));
    for (const [A, W] of samples(12, 200)) {
      const codes: Rgb = [A[0] * 255, A[1] * 255, A[2] * 255];
      const top = bodyToneTableCodesAt(codes, 112, material);
      const under = bodyLawE3Codes(codes, luma(W) * 255, material);
      const out = emulateBodyLawFilter(filter, {
        [filter.results.argument]: { rgba: [A[0], A[1], A[2], 1], space: "sRGB" },
        [filter.results.wide]: { rgba: [W[0], W[1], W[2], 1], space: "sRGB" },
      }).output;
      for (let c = 0; c < 3; c++) {
        const expected = encode(0.6 * decode(under[c]! / 255) + 0.4 * decode(top[c]! / 255));
        expect(Math.abs(out[c]! - expected) * 255).toBeLessThan(5e-3);
      }
    }
  });
});

describe("candidate 1's landed solve is an approximation, bounded on the shipped endpoints", () => {
  const endpoints = [
    ["active light", macos27MaterialProfileDocument.active.light.patch],
    ["active dark", macos27MaterialProfileDocument.active.dark.patch],
    ["receded light", macos27MaterialProfileDocument.receded?.light.patch],
    ["receded dark", macos27MaterialProfileDocument.receded?.dark.patch],
  ] as const;
  for (const [name, endpoint] of endpoints) {
    it(`${name}: exact on the greys, and within the recorded bound on chromatic arguments`, () => {
      const patch = { ...(endpoint ?? {}), bodyLawStrength: 1, bodyLawEncodedAveraging: 1,
        bodyLawWidthUnit: 1, bodyLawPose: name.startsWith("receded") ? 1 : 0 } as Patch;
      const extents = [200, 96] as const;
      const filter = filterFor(patch, extents);
      expect(filter.parameters.tone.kind).toBe("landed");
      expect(filter.parameters.tone.exactForm).toBe(false);
      const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch as never);
      const inputs = cssLandedToneInputs(patch, "regular", 96, NOMINAL_ACCESSIBILITY_POLICY.material, 2);
      const tone = (A: Rgb): Rgb => {
        const linear = landedToneLinear(A, inputs, material);
        return [encode(linear[0]) * 255, encode(linear[1]) * 255, encode(linear[2]) * 255];
      };
      const run = (A: Rgb): Rgb => {
        const out = emulateBodyLawFilter(filter, {
          [filter.results.argument]: { rgba: [A[0], A[1], A[2], 1], space: "sRGB" },
          [filter.results.wide]: { rgba: [A[0], A[1], A[2], 1], space: "sRGB" },
        }).output;
        return [out[0] * 255, out[1] * 255, out[2] * 255];
      };
      let greys = 0;
      for (let k = 0; k <= 255; k += 5) {
        const g = k / 255;
        const out = run([g, g, g]);
        const expected = tone([g, g, g]);
        for (let c = 0; c < 3; c++) greys = Math.max(greys, Math.abs(out[c]! - expected[c]!));
      }
      expect(greys).toBeLessThan(1e-3);
      let chromatic = 0;
      const steps = [0, 0.2, 0.4, 0.6, 0.8, 1];
      for (const r of steps) for (const g of steps) for (const b of steps) {
        const out = run([r, g, b]);
        const expected = tone([r, g, b]);
        for (let c = 0; c < 3; c++) chromatic = Math.max(chromatic, Math.abs(out[c]! - expected[c]!));
      }
      // Recorded in u5_css_algebra.md §4, per endpoint: a bound one code above the reading, so
      // a tone that moves re-opens the record instead of passing under a loose ceiling.
      const bound = LANDED_BOUND_CODES[name]!;
      expect(chromatic).toBeLessThan(bound);
      expect(chromatic).toBeGreaterThan(bound - 1.5);
    });
  }
});

/**
 * The landed approximation's worst reading on the 6³ grid, codes, plus one (u5_css_algebra.md
 * §4): 86.07, 47.00, 70.70 and 27.77. Every one is at a saturated corner of the grid.
 */
const LANDED_BOUND_CODES: Readonly<Record<string, number>> = {
  "active light": 87.07,
  "active dark": 48.0,
  "receded light": 71.7,
  "receded dark": 28.77,
};

/**
 * The landed solve BETWEEN the table's knots (the U3/U4 review's fix wave, item 2). Every tone
 * table carries one entry per code and the filter interpolates linearly between them, so a blurred
 * argument between two codes reads the chord. That is harmless where the response is smooth, and
 * not across W36's black branch, which rejoins the old solve before encoded 0.003 (0.77 code):
 * a response that moves by tens of codes inside the first code of input cannot be carried by a
 * chord from code 0 to code 1. The emulator's intermediates are float, as an engine's would have
 * to be for a fractional code to reach the table at all; an eight-bit chain quantises the argument
 * to the knots, where the table is exact. Recorded in u5_css_algebra.md §4 as a Decision Log 4
 * approximation, with these bounds.
 */
describe("the landed solve between the table's knots: fractional greys across W36's black join", () => {
  const endpoints = [
    ["active light", macos27MaterialProfileDocument.active.light.patch],
    ["active dark", macos27MaterialProfileDocument.active.dark.patch],
    ["receded light", macos27MaterialProfileDocument.receded?.light.patch],
    ["receded dark", macos27MaterialProfileDocument.receded?.dark.patch],
  ] as const;
  for (const [name, endpoint] of endpoints) {
    it(`${name}: the chord's miss below 4 codes and between the knots above, within the record`, () => {
      const patch = { ...(endpoint ?? {}), bodyLawStrength: 1, bodyLawEncodedAveraging: 1,
        bodyLawWidthUnit: 1, bodyLawPose: name.startsWith("receded") ? 1 : 0 } as Patch;
      const filter = filterFor(patch, [200, 96]);
      const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch as never);
      const inputs = cssLandedToneInputs(patch, "regular", 96, NOMINAL_ACCESSIBILITY_POLICY.material, 2);
      const miss = (code: number): number => {
        const g = code / 255;
        const out = emulateBodyLawFilter(filter, {
          [filter.results.argument]: { rgba: [g, g, g, 1], space: "sRGB" },
          [filter.results.wide]: { rgba: [g, g, g, 1], space: "sRGB" },
        }).output;
        const linear = landedToneLinear([g, g, g], inputs, material);
        return Math.max(...[0, 1, 2].map((c) => Math.abs(out[c]! - encode(linear[c]!)) * 255));
      };
      let black = 0;
      for (let i = 0; i <= 400; i++) black = Math.max(black, miss(i / 100));
      let above = 0;
      for (let k = 4; k < 255; k++) for (const f of [0.25, 0.5, 0.75]) above = Math.max(above, miss(k + f));
      const bound = FRACTIONAL_GREY_BOUND_CODES[name]!;
      // A bound a code above each reading, so a tone that moves re-opens the record.
      expect(black).toBeLessThan(bound.black);
      expect(black).toBeGreaterThan(bound.black - 1.5);
      expect(above).toBeLessThan(bound.above);
    });
  }
});

/**
 * The fractional-grey readings (u5_css_algebra.md §4): below 4 codes, across the black join, one
 * code above each reading (43.20, 16.03, 53.08 and 200.61, every one between code 0 and code 1);
 * between the knots above 4 codes, 0.065 at worst, bounded at 0.1.
 */
const FRACTIONAL_GREY_BOUND_CODES: Readonly<Record<string, { black: number; above: number }>> = {
  "active light": { black: 44.2, above: 0.1 },
  "active dark": { black: 17.03, above: 0.1 },
  "receded light": { black: 54.09, above: 0.1 },
  "receded dark": { black: 201.62, above: 0.1 },
};

describe("the stacked approximation, where no reference filter renders (§5)", () => {
  it("draws N exactly for knee 0 with λ in [0, 1] — a lighten at opacity λ over C", () => {
    for (const hinge of [1, -1] as const) {
      for (const lambda of LAMBDAS) {
        const opacity = clamp01(lambda);
        for (const [C, W] of samples(3, 200)) {
          const blended = [0, 1, 2].map((i) =>
            (1 - opacity) * C[i]! +
            opacity * (hinge > 0 ? Math.max(C[i]!, W[i]!) : Math.min(C[i]!, W[i]!)));
          const cpu = bodyLawComposite(C, W, {
            bodyLawLambda: opacity, bodyLawNormal: 0, bodyLawHinge: hinge, bodyLawKnee: 0,
            bodyLawEncodedAveraging: 1,
          });
          for (let i = 0; i < 3; i++) expect(blended[i]).toBeCloseTo(cpu.argument[i]!, 12);
        }
      }
    }
  });

  it("over-fills the Normal step by exactly the blurred hinge term, w·h·λ·G*D_h", () => {
    // One dimension is enough: every step is linear in the signal but the hinge's max.
    const next = random(99);
    const backdrop = Array.from({ length: 256 }, () => next());
    const gaussian = (signal: readonly number[], sigma: number): number[] => {
      const reach = Math.ceil(4 * sigma);
      const kernel = Array.from({ length: 2 * reach + 1 }, (_, i) =>
        Math.exp(-((i - reach) ** 2) / (2 * sigma * sigma)));
      const total = kernel.reduce((a, b) => a + b, 0);
      return signal.map((_, x) => kernel.reduce((sum, k, i) => {
        const at = Math.min(signal.length - 1, Math.max(0, x + i - reach));
        return sum + (k / total) * signal[at]!;
      }, 0));
    };
    const [sn, sw, lambda, normal] = [4, 16, 0.9, 0.5];
    const step = Math.sqrt(sw * sw - sn * sn);
    for (const hinge of [1, -1] as const) {
      const C = gaussian(backdrop, sn);
      const W = gaussian(C, step);
      const N = C.map((c, x) =>
        (1 - lambda) * c + lambda * (hinge > 0 ? Math.max(c, W[x]!) : Math.min(c, W[x]!)));
      const blurredN = gaussian(N, step);
      const stacked = N.map((n, x) => (1 - normal) * n + normal * blurredN[x]!);
      const exact = N.map((n, x) => (1 - normal) * n + normal * W[x]!);
      const hingeTerm = gaussian(C.map((c, x) => Math.max(0, hinge * (W[x]! - c))), step);
      for (let x = 0; x < C.length; x++) {
        expect(stacked[x]! - exact[x]!).toBeCloseTo(normal * hinge * lambda * hingeTerm[x]!, 12);
      }
    }
  });

  it("writes W41's affine as two filter functions with no premature clamp, in either order", () => {
    const apply = (functions: string, x: number): number => {
      let value = x;
      for (const match of functions.matchAll(/(contrast|brightness)\(([-\d.e]+)\)/g)) {
        const k = Number(match[2]);
        value = clamp01(match[1] === "contrast" ? k * value + (1 - k) / 2 : k * value);
      }
      return value;
    };
    for (const slope of [0, 0.4, 1, 1.3, 2.2]) {
      for (const intercept of [-0.6, -0.1, 0, 0.05, 0.3]) {
        const functions = bodyLawAffineFilterFunctions(slope, intercept);
        expect(functions.startsWith(intercept >= 0 ? "contrast" : "brightness")).toBe(true);
        for (let k = 0; k <= 50; k++) {
          const x = k / 50;
          expect(apply(functions, x)).toBeCloseTo(clamp01(slope * x + intercept), 5);
        }
      }
    }
  });

  it("reads T exactly at the surface's level, and only there", () => {
    const filter = filterFor(TABLE_PATCH, [200, 112]);
    const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, TABLE_PATCH as never);
    for (const level of [0.2, 0.45, 0.7]) {
      const { slope, intercept } = bodyLawToneAffine(filter.parameters.tone, level);
      // A colour whose luma is the level: the affine is T's chroma slope about T's own value.
      const colour: Rgb = [level + 0.1, level - (0.2126 / 0.7152) * 0.1, level];
      const expected = bodyToneTableCodesAt(
        [colour[0] * 255, colour[1] * 255, colour[2] * 255], 112, material);
      for (let c = 0; c < 3; c++) {
        expect((slope * colour[c]! + intercept) * 255).toBeCloseTo(expected[c]!, 2);
      }
    }
    const layers = cssTierBodyLawStacked(filter.parameters, 0.45);
    expect(layers.map((layer) => layer.role)).toEqual(["narrow", "hinge", "normal", "tone"]);
    expect(cssTierBodyLawStacked(filter.parameters).map((layer) => layer.role))
      .toEqual(["narrow", "hinge", "normal"]);
  });
});

describe("an eight-bit chain, as one model of an engine's intermediates (not a measurement)", () => {
  it("stays within a few codes of the float chain for the carried knee on each tone", () => {
    const cases = [
      ["T2", TABLE_PATCH],
      ["E3", E3_PATCH],
      ["landed, active light", { ...macos27MaterialProfileDocument.active.light.patch,
        bodyLawStrength: 1, bodyLawEncodedAveraging: 1, bodyLawWidthUnit: 1 }],
    ] as const;
    for (const [name, patch] of cases) {
      const filter = filterFor(patch as Patch, [200, 112]);
      let worst = 0;
      for (const [C, W] of samples(77, 400)) {
        const float = emulateBodyLawFilter(filter, supplied(filter, C, W, "sRGB")).output;
        const quantised = (x: number): number => Math.round(x * 255) / 255;
        const eight = emulateBodyLawFilter(filter, supplied(filter, C.map(quantised) as never,
          W.map(quantised) as never, "sRGB"), { eightBit: true }).output;
        for (let c = 0; c < 3; c++) worst = Math.max(worst, Math.abs(float[c]! - eight[c]!) * 255);
      }
      expect(worst, name).toBeLessThan(EIGHT_BIT_BOUND_CODES);
    }
  });
});

/** The eight-bit model's worst reading was 2.91 / 3.06 / 3.81 codes (u5_css_algebra.md §6). */
const EIGHT_BIT_BOUND_CODES = 5;
