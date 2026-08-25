/**
 * Keeping the WGSL and the TypeScript in step. C6 consumes the WGSL; this file is
 * what says the two compute the same function.
 *
 * Three layers, because no single one is sufficient in a unit test with no GPU:
 *
 *  1. **The numeric cross-check** (the strong one). S2's `bench/f32-check.json`
 *     holds f64 evaluation of exactly the arithmetic in the benchmarked WGSL, and
 *     the spike measured the real shader's f32 output against that column on a
 *     metal-3 adapter at 4.08e-5 px. `field.test.ts` asserts this package's field
 *     reproduces the column bit-for-bit, so the shader's function is pinned
 *     transitively. Repeated here as the sampled-output fingerprint below, so a
 *     change to the TS field trips this file too.
 *
 *  2. **A structural mirror check.** The TS and the WGSL are written as
 *     line-for-line mirrors — same clamp, same Horner order — so the WGSL's
 *     arithmetic tokens are extracted and checked against what the mirror
 *     requires. This catches an edit to the shader that a fingerprint alone would
 *     only report as "something changed".
 *
 *  3. **Fingerprints.** A hash of each shader string and of the TS field's
 *     sampled outputs. Editing either side alone fails, with a message saying to
 *     re-run the f32 cross-check before updating the constant. This is the layer
 *     that makes drift impossible to land silently; it is not the layer that
 *     proves correctness.
 */

import { describe, expect, it } from "vitest";

import { fingerprint, WGSL_FIELD_MODULE, WGSL_RSUP, WGSL_RSUPN, WGSL_SHAPE_STRUCT } from "../src/wgsl";
import { rsupField, rsupnField } from "../src/field";
import { APPLE_RSUPN } from "../src/coefficients";
import { CROSS_CHECK, crossCheckParams } from "./harness/cross-check";

/**
 * Committed fingerprints. To change either side deliberately:
 *   1. edit the WGSL and its TypeScript mirror together;
 *   2. re-establish the f32 evidence on real hardware — either by regenerating
 *      `bench/f32-check.json` in the spike and re-running its accuracy mode, or
 *      by the renderer's real-adapter field cross-check, which reads the shipped
 *      shader's own output back and compares it against this package's field;
 *   3. update the constants below.
 * Updating them without step 2 is how the shader and the kernel silently diverge.
 *
 * Last moved by the normalization anchor (`field.ts`, "The normalization").
 * `rsup`'s and the struct's fingerprints did not move, because neither changed.
 * The f32 evidence for that change is the renderer's real-adapter cross-check,
 * not a regenerated fixture: S2's column is left as it was measured, and the
 * assertion above says which half of it is still reproduced exactly.
 */
const EXPECTED = {
  rsupn: "9c24e278",
  rsup: "13c5190d",
  struct: "f0bd5d17",
  module: "e73d1af4",
  /** hash of the TS field's outputs over the whole cross-check point set */
  tsSamples: "44402664",
} as const;

/** Quantized so the hash is stable against last-bit noise but not against real change. */
function sampleFingerprint(field: (p: ReturnType<typeof crossCheckParams>[number], x: number, y: number) => number): string {
  const params = crossCheckParams();
  const parts: string[] = [];
  for (let i = 0; i < CROSS_CHECK.expected.length; i++) {
    const p = params[CROSS_CHECK.points[i * 3] as number]!;
    const x = CROSS_CHECK.points[i * 3 + 1] as number;
    const y = CROSS_CHECK.points[i * 3 + 2] as number;
    parts.push(field(p, x, y).toFixed(9));
  }
  return fingerprint(parts.join(","));
}

describe("the numeric cross-check pins the shader's function", () => {
  it("reproduces the f64 column the benchmarked shader was measured against, on and outside the level set", () => {
    // The same assertion field.test.ts makes, restated here because THIS is the
    // evidence behind the fingerprints: without it they would only prove that two
    // strings had not changed.
    //
    // Restricted to `rsupField >= 0` — on and outside the level set — because
    // that is exactly where the normalization's anchor is inert, and where the
    // agreement is therefore still exact rather than merely close. The inward
    // divergence is asserted in field.test.ts, with its magnitude and its
    // one-sidedness both pinned.
    const params = crossCheckParams();
    let worst = 0;
    let n = 0;
    for (let i = 0; i < CROSS_CHECK.expected.length; i++) {
      const p = params[CROSS_CHECK.points[i * 3] as number]!;
      const x = CROSS_CHECK.points[i * 3 + 1] as number;
      const y = CROSS_CHECK.points[i * 3 + 2] as number;
      if (rsupField(p, x, y) < 0) continue;
      n++;
      worst = Math.max(worst, Math.abs(rsupnField(p, x, y) - (CROSS_CHECK.expected[i] as number)));
    }
    expect(n).toBe(2926);
    expect(worst).toBe(0);
  });
});

describe("the WGSL mirrors the TypeScript, structurally", () => {
  const arithmetic = (src: string): string =>
    src
      .replace(/\/\/[^\n]*/g, "")
      .replace(/\s+/g, "");

  it("uses the same guard constant on the squared corner radius", () => {
    // The field's only guard. If the shader's differed from the TS one, the deep
    // interior would disagree between CPU and GPU — invisible until it reached a
    // frame.
    expect(WGSL_RSUPN).toContain("max(dot(c, c), 1e-20)");
    expect(WGSL_RSUP).toContain("max(dot(c, c), 1e-20)");
  });

  it("derives sin and cos of 2*theta by division, with no transcendentals", () => {
    // What makes the angular correction affordable at all. A `atan2`, `sin` or
    // `cos` appearing here would mean the cost figures no longer apply.
    for (const src of [WGSL_RSUPN, WGSL_RSUP]) {
      expect(src).toMatch(/2\.0 \* c\.x \* c\.y/);
      // On the comment-stripped source: the comments legitimately say what the
      // divisions stand for ("sin(2*theta)"), and matching those would be a
      // test that fails on documentation.
      expect(arithmetic(src)).not.toMatch(/\b(atan2|sin|cos|pow|exp|log)\(/);
    }
    expect(WGSL_RSUPN).toContain("(c.x * c.x - c.y * c.y) * inv");
  });

  it("evaluates the correction by Horner in the same coefficient order", () => {
    // k4 first, then k.w, k.z, k.y, k.x — matching the TS loop's descending index.
    const order = arithmetic(WGSL_RSUPN).match(/acc=acc\*s2\+k\.(w|z|y|x)/g);
    expect(order).toEqual(["acc=acc*s2+k.w", "acc=acc*s2+k.z", "acc=acc*s2+k.y", "acc=acc*s2+k.x"]);
    expect(arithmetic(WGSL_RSUPN)).toContain("varacc=k4;");
  });

  it("differentiates the same polynomial with the (i+2) weights", () => {
    // The derivative chain must use exactly the weights the TS `hornerB` uses, or
    // the normalization is applied with the wrong slope.
    const a = arithmetic(WGSL_RSUPN);
    expect(a).toContain("vardac=6.0*k4;");
    expect(a).toContain("dac=dac*s2+5.0*k.w;");
    expect(a).toContain("dac=dac*s2+4.0*k.z;");
    expect(a).toContain("dac=dac*s2+3.0*k.y;");
    expect(a).toContain("dac=dac*s2+2.0*k.x;");
  });

  it("anchors the normalization at the contour radius, in both dialects", () => {
    // Load-bearing, and invisible in a fingerprint: without the anchor the
    // normalization divides by a sample radius that falls to zero at the corner
    // sector's vertex, and the field reports a point one corner reach deep as a
    // few px deep. Pinned structurally so it cannot be "simplified" back out.
    expect(arithmetic(WGSL_RSUPN)).toContain("letg=select(dRdt/R,dRdt*inv*sqrt(r2),sqrt(r2)>=R);");
    // and the TypeScript mirror selects on the same predicate
    const p = { halfW: 168, halfH: 84, reach: 39.7453, k: APPLE_RSUPN.k };
    // one corner reach in from the corner: the sector vertex, plus a hair along
    // the diagonal so the corner sector (not the box branch) is what answers
    const deep = rsupnField(p, p.halfW - p.reach + 2, p.halfH - p.reach + 2);
    expect(deep).toBeLessThan(-38);
  });

  it("is family C exactly minus the normalization", () => {
    // The two share a zero level set; C's shader must be D's without the final
    // divide, or "the governor's step is the same shape, cheaper" is not true.
    expect(WGSL_RSUP).not.toContain("inverseSqrt");
    expect(WGSL_RSUPN).toContain("inverseSqrt(1.0 + g * g)");
    expect(WGSL_RSUP).toContain("sqrt(r2) + min(max(q.x, q.y), 0.0) - R");
  });

  it("declares the six derived floats C6's instance buffer widens by", () => {
    for (const name of ["re", "k0", "k1", "k2", "k3", "k4"]) {
      expect(WGSL_SHAPE_STRUCT).toContain(name);
    }
  });
});

describe("fingerprints catch drift on either side", () => {
  it("pins each shader string", () => {
    const msg =
      "WGSL changed. Edit the TypeScript mirror in src/field.ts together with it, " +
      "re-run the spike's f32 cross-check on real hardware, then update EXPECTED.";
    expect(fingerprint(WGSL_RSUPN), msg).toBe(EXPECTED.rsupn);
    expect(fingerprint(WGSL_RSUP), msg).toBe(EXPECTED.rsup);
    expect(fingerprint(WGSL_SHAPE_STRUCT), msg).toBe(EXPECTED.struct);
    expect(fingerprint(WGSL_FIELD_MODULE), msg).toBe(EXPECTED.module);
  });

  it("pins the TypeScript field's sampled outputs", () => {
    const msg =
      "The TypeScript field's output changed. If deliberate, update the WGSL to match, " +
      "re-run the spike's f32 cross-check, then update EXPECTED.tsSamples.";
    expect(sampleFingerprint(rsupnField), msg).toBe(EXPECTED.tsSamples);
  });

  it("gives family C a different fingerprint, so neither can stand in for the other", () => {
    expect(sampleFingerprint(rsupField)).not.toBe(EXPECTED.tsSamples);
    expect(fingerprint(WGSL_RSUP)).not.toBe(fingerprint(WGSL_RSUPN));
  });

  it("has a fingerprint function that actually distinguishes near-identical strings", () => {
    // A tripwire is worthless if it does not trip.
    expect(fingerprint("acc = acc * s2 + k.w")).not.toBe(fingerprint("acc = acc * s2 + k.z"));
    expect(fingerprint("1e-20")).not.toBe(fingerprint("1e-19"));
    expect(fingerprint("")).toBe(fingerprint(""));
    expect(fingerprint(WGSL_RSUPN)).toHaveLength(8);
  });
});
