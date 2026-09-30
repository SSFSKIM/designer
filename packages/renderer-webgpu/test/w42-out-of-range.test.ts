/**
 * W42 G2 step 3, the U3/U4 review's fix wave, item 1 — an out-of-range argument, from the composite
 * through every tone, against the UNCLIPPED oracle (`implementation-design.md` §14;
 * `implementation-design/u4_out_of_range.py`, `fixtures/out-of-range.json`).
 *
 * Admitted parameters put the law's M outside [0, 1]: λ above 1 overshoots the per-channel knee,
 * and the luma composite adds W's chroma to a luma W does not have. The declared oracle hands M to
 * T unclipped (`forward.py:527`) and each tone clips where its own gamut step does (`body.py:513`,
 * `515`, `550`, `573`; `swap.py:219`, `233`), so A is stored unclipped and the CPU references the
 * shader transcribes are held here to that oracle on every such case.
 */

import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import {
  bodyLawComposite,
  bodyLawE3Codes,
  bodyToneTableCodesAt,
  landedToneLinear,
  type LandedToneInputs,
} from "../src/body-law";
import type { Rgb } from "../src/color";
import type { MaterialProfile } from "../src/material";
import { WGSL_BODY_LAW_COMPOSITE, WGSL_OPTICS_PASS } from "../src/wgsl";

const FIXTURES = new URL(
  "../../calibration/results/2026-09-30-w42-g2-identification/implementation-design/fixtures/",
  import.meta.url,
);
const fixture = <T>(name: string): T =>
  JSON.parse(readFileSync(new URL(`${name}.json`, FIXTURES), "utf8")) as T;

interface Case {
  readonly C: Rgb; readonly W: Rgb; readonly lam: number; readonly w: number;
  readonly hinge: number; readonly knee: number; readonly M: Rgb; readonly wideLuma: number;
}
interface OutOfRange {
  readonly cases: readonly Case[];
  readonly landed: Readonly<Record<string, readonly { sizeK: number; linear: Rgb[] }[]>>;
  readonly e3: {
    readonly gains: [number, number, number];
    readonly neutral: [number, number, number, number, number, number, number];
    readonly high: [number, number, number, number, number, number, number];
    readonly runs: readonly { strength: number; out: Rgb[] }[];
  };
  readonly table: {
    readonly levels: number[]; readonly spans: number[]; readonly codes: number[][];
    readonly gains: [number, number, number]; readonly scale: number;
    readonly out: Readonly<Record<string, Rgb[]>>;
  };
  readonly constant128: { readonly codes: number[][]; readonly out: Rgb[]; readonly clipped: Rgb[] };
}
interface LandedParams {
  readonly [endpoint: string]: { readonly params: {
    readonly tint: readonly number[]; readonly tintAlpha: number; readonly sizeOcclusionGain: number;
    readonly backdropToneLow: number; readonly backdropToneHigh: number;
    readonly backdropToneSizeBias: number; readonly backdropToneMax: number;
    readonly anchorX: readonly number[]; readonly thin: readonly number[];
    readonly thick: readonly number[]; readonly responseStrength: number;
    readonly black: readonly [number, number, number]; readonly bodyChromaRetention: number;
    readonly abscissa: unknown;
  } };
}

const doc = fixture<OutOfRange>("out-of-range");
const codesOf = (m: Rgb): Rgb => [m[0] * 255, m[1] * 255, m[2] * 255];

describe("W42 fix wave: an out-of-range argument is the oracle's, unclipped, through every tone", () => {
  it("has out-of-range arguments for every knee form, and composes them unclipped", () => {
    for (const knee of [0, 1, 2]) expect(doc.cases.some((c) => c.knee === knee)).toBe(true);
    for (const c of doc.cases) {
      expect(c.M.some((v) => v < 0 || v > 1)).toBe(true);
      const { argument } = bodyLawComposite(c.C, c.W, { bodyLawLambda: c.lam, bodyLawNormal: c.w,
        bodyLawHinge: c.hinge, bodyLawKnee: c.knee, bodyLawEncodedAveraging: 1 });
      argument.forEach((v, i) => expect(v).toBeCloseTo(c.M[i]!, 12));
    }
  });

  it("stores A unclipped in the shader, where the declared oracle hands M to T", () => {
    expect(WGSL_BODY_LAW_COMPOSITE).toContain("return vec4f(M, law_luma(W));");
    expect(WGSL_BODY_LAW_COMPOSITE).not.toContain("vec4f(clamp(M, vec3f(0.0), vec3f(1.0)), law_luma(W))");
    // The landed solve clips each channel and, separately, the luma, as body.py's dec does.
    expect(WGSL_OPTICS_PASS).toContain(
      "let c = srgb_to_linear(clamp(encoded, vec3f(0.0), vec3f(1.0)));");
    expect(WGSL_OPTICS_PASS).toContain(
      "level = srgb_to_linear(vec3f(clamp(dot(encoded, LAW_LUMA), 0.0, 1.0))).x;");
  });

  const params = fixture<LandedParams>("landed");
  it.each(Object.keys(doc.landed))("the landed solve at %s is landed_T's on the unclipped argument", (ep) => {
    const p = params[ep]!.params;
    const profile = {
      backdropToneAnchorX: p.anchorX as unknown as MaterialProfile["backdropToneAnchorX"],
      backdropToneResponseThin: p.thin as unknown as MaterialProfile["backdropToneResponseThin"],
      backdropToneResponseThick: p.thick as unknown as MaterialProfile["backdropToneResponseThick"],
      backdropToneResponseStrength: p.responseStrength,
      backdropToneBlackStrength: p.black[0],
      backdropToneBlackThin: p.black[1],
      backdropToneBlackThick: p.black[2],
    };
    for (const run of doc.landed[ep]!) {
      const inputs: LandedToneInputs = {
        sizeK: run.sizeK, toneLevelFar: 0, neutral: [p.tint[0]!, p.tint[0]!, p.tint[0]!],
        tintAlpha: p.tintAlpha, sizeOcclusionGain: p.sizeOcclusionGain,
        toneStrength: p.backdropToneMax, toneLow: p.backdropToneLow, toneHigh: p.backdropToneHigh,
        toneSizeBias: p.backdropToneSizeBias, retention: p.bodyChromaRetention,
        abscissa: p.abscissa === "source(default)" ? "source" : "silhouette", presence: 1,
      };
      doc.cases.forEach((c, i) => {
        landedToneLinear(c.M, inputs, profile).forEach((v, k) =>
          expect(v, `${ep} sizeK ${run.sizeK} M ${c.M}`).toBeCloseTo(run.linear[i]![k]!, 12));
      });
    }
  });

  it("E3 with the F extension takes the unclipped argument's luma and chroma", () => {
    for (const run of doc.e3.runs) {
      doc.cases.forEach((c, i) => {
        bodyLawE3Codes(codesOf(c.M), c.wideLuma * 255, { bodyE3Gains: doc.e3.gains,
          bodyE3Neutral: doc.e3.neutral, bodyE3HighStrength: run.strength,
          bodyE3NeutralHigh: doc.e3.high })
          .forEach((v, k) => expect(v).toBeCloseTo(run.out[i]![k]!, 9));
      });
    }
  });

  it("candidate 2's table does too, and a clip before its chroma term would move it", () => {
    const fields = (codes: number[][]) => ({
      bodyToneTableLevels: doc.table.levels as unknown as MaterialProfile["bodyToneTableLevels"],
      bodyToneTableSpans: doc.table.spans as unknown as MaterialProfile["bodyToneTableSpans"],
      bodyToneTableCodes: codes as unknown as MaterialProfile["bodyToneTableCodes"],
      bodyToneChromaGains: doc.table.gains, bodyToneChromaScale: doc.table.scale,
    });
    for (const [span, outs] of Object.entries(doc.table.out)) {
      doc.cases.forEach((c, i) => {
        bodyToneTableCodesAt(codesOf(c.M), Number(span), fields(doc.table.codes))
          .forEach((v, k) => expect(v).toBeCloseTo(outs[i]![k]!, 9));
      });
    }
    let moved = 0;
    doc.cases.forEach((c, i) => {
      const y = bodyToneTableCodesAt(codesOf(c.M), 96, fields(doc.constant128.codes));
      y.forEach((v, k) => expect(v).toBeCloseTo(doc.constant128.out[i]![k]!, 9));
      moved = Math.max(moved, ...y.map((v, k) => Math.abs(v - doc.constant128.clipped[i]![k]!)));
    });
    // What the clip the review found would have cost on this population (u4_out_of_range.py).
    expect(moved).toBeGreaterThan(40);
  });
});
