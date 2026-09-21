/**
 * W31 G2 — every transcendental in `src/wgsl/` is clamped or proven (claims
 * §5.163; the tracker's "Nothing checks that a WGSL transcendental's argument
 * stays inside f32", fix shape 1).
 *
 * W30 G3b fixed one `tanh`. This is the class it belongs to: no call of `exp`,
 * `exp2`, `pow`, `tanh`, `sinh`, `cosh`, `log`, `log2` or `inverseSqrt` in any
 * shader this package ships may have an argument that leaves the range where the
 * function is finite in f32 — and a site the source does not bound has to carry a
 * written proof of the bound, keyed to its own text and to the lines that hold
 * it up.
 *
 * `scan.ts`'s module note says what the evaluator is and why bare division is
 * outside it. `proofs.ts` carries the three proofs. What is here is the case.
 *
 * The self-test at the bottom is not decoration. A checker of this shape has one
 * failure mode that matters — passing everything — and the only way to know it
 * does not is to hand it sources that must fail. `exp(clamp(x, 0.0, 1e30))` is
 * the one to read: clamped, and still over f32's `exp` by twenty-nine orders of
 * magnitude.
 */

import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { DEFAULT_MATERIAL_PROFILE, MATERIAL_VARIANTS } from "../src/material";
import {
  describeInterval,
  scanSource,
  scanWgslDirectory,
  verdictFor,
  WGSL_DIR,
  type CallSite,
} from "./wgsl-range/scan";
import { LEAF_BOUNDS, RANGE_PROOFS } from "./wgsl-range/proofs";

const SITES = scanWgslDirectory();

/** Everything under `src/wgsl/`, concatenated — the witnesses are looked up here. */
const ALL_WGSL = readdirSync(WGSL_DIR)
  .filter((name) => name.endsWith(".ts"))
  .sort()
  .map((name) => readFileSync(join(WGSL_DIR, name), "utf8"))
  .join("\n");

const keyOf = (site: CallSite, argument: number): string =>
  `${site.file} :: ${site.call} :: arg${argument}`;

const proofFor = (site: CallSite, argument: number): (typeof RANGE_PROOFS)[number] | undefined =>
  RANGE_PROOFS.find(
    (proof) =>
      proof.file === site.file && proof.call === site.call && proof.argument === argument,
  );

describe("the WGSL range class (claims §5.163)", () => {
  it("finds the call sites at all, so a green run is not an empty one", () => {
    // A scanner that silently stopped matching would pass every case below. The
    // floor is stated rather than pinned to a count: a wave that adds a pass
    // should not have to edit an arithmetic fact to land.
    expect(SITES.length).toBeGreaterThanOrEqual(11);
    expect(new Set(SITES.map((site) => site.file)).size).toBeGreaterThanOrEqual(3);
  });

  it("bounds every argument of every call, by the source or by a written proof", () => {
    const stopped: string[] = [];
    for (const site of SITES) {
      const verdict = verdictFor(site.fn, site.ranges);
      if (verdict.finite) continue;
      for (const argument of verdict.unbounded) {
        if (proofFor(site, argument) !== undefined) continue;
        stopped.push(
          `${keyOf(site, argument)}\n    resolved ${describeInterval(
            site.ranges[argument] ?? { lo: 0, hi: 0 },
          )}\n    ${verdict.why}`,
        );
      }
    }
    expect(
      stopped,
      `${stopped.length} call site argument(s) are neither clamped to a finite range nor ` +
        `covered by a range proof. Clamp the argument where the clamp is the identity at ` +
        `every input the unclamped form evaluates finitely (W30 G3b's ±20 on tanh is the ` +
        `pattern), or add an entry to test/wgsl-range/proofs.ts naming the bound, what it ` +
        `depends on, and why it holds over any value a fit could produce:\n  ` +
        stopped.join("\n  "),
    ).toEqual([]);
  });

  it("carries no proof for a site that no longer needs one, or no longer exists", () => {
    // A proof that outlives its call site is worse than no proof: it reads as
    // coverage and is not.
    const stale = RANGE_PROOFS.filter((proof) => {
      const site = SITES.find(
        (candidate) => candidate.file === proof.file && candidate.call === proof.call,
      );
      if (site === undefined) return true;
      return verdictFor(site.fn, site.ranges).finite;
    }).map((proof) => `${proof.file} :: ${proof.call} :: arg${proof.argument}`);
    expect(stale, `stale range proofs:\n  ${stale.join("\n  ")}`).toEqual([]);
  });

  it("keeps every proof's witnesses present in the shaders", () => {
    // The proofs do not rest on their own call's text — they rest on a `select`
    // three lines away, on the field pass's normalisation two files away. The
    // witness is what makes an edit to those lines land here.
    const missing: string[] = [];
    for (const proof of RANGE_PROOFS) {
      for (const witness of proof.witness) {
        if (!ALL_WGSL.includes(witness)) {
          missing.push(`${proof.file} :: ${proof.call} :: arg${proof.argument}\n    ${witness}`);
        }
      }
    }
    expect(
      missing,
      `a range proof leans on shader text that is no longer there, so the proof is no ` +
        `longer one. Re-read it before re-stating it:\n  ${missing.join("\n  ")}`,
    ).toEqual([]);
  });

  it("classifies every site as clamped or proven, and reports the split", () => {
    let clamped = 0;
    let proven = 0;
    for (const site of SITES) {
      if (verdictFor(site.fn, site.ranges).finite) clamped += 1;
      else proven += 1;
    }
    expect(clamped + proven).toBe(SITES.length);
    // The split at §5.163: eight bounded by the source, three by a proof.
    expect(clamped).toBeGreaterThanOrEqual(8);
  });
});

describe("the leaf bounds the range proofs lean on (claims §5.163)", () => {
  /**
   * The bounds are a property of the MATERIAL, not of the shader, so they are
   * checked where a material is: here on the runtime default that every shipped
   * document patches, and in `@vitrea/calibration` on the documents themselves.
   * A fit that moved one of these leaves out of range would otherwise be found
   * by a capture, or not at all.
   */
  it("the runtime default's lens profile exponent is strictly positive", () => {
    const value = DEFAULT_MATERIAL_PROFILE.lensProfileExponent;
    expect(value).toBeGreaterThan(LEAF_BOUNDS.lensProfileExponent.exclusiveMin);
    expect(value).toBeLessThanOrEqual(LEAF_BOUNDS.lensProfileExponent.max);
  });

  it("the runtime default's lit-edge axis is a short vector", () => {
    const [x, y] = DEFAULT_MATERIAL_PROFILE.rimLitAxis;
    expect(Math.hypot(x, y)).toBeLessThanOrEqual(LEAF_BOUNDS.rimLitAxisNorm.max);
  });

  it("every variant's lit-edge exponent is inside its window", () => {
    for (const variant of MATERIAL_VARIANTS) {
      const value = DEFAULT_MATERIAL_PROFILE.optics[variant].rimLitExponent;
      expect(value, variant).toBeGreaterThanOrEqual(LEAF_BOUNDS.rimLitExponent.min);
      expect(value, variant).toBeLessThanOrEqual(LEAF_BOUNDS.rimLitExponent.max);
    }
  });
});

describe("the checker itself, on sources whose answer is known", () => {
  const scan = (body: string): CallSite[] => scanSource("synthetic.wgsl", body);
  const finite = (body: string): boolean =>
    scan(body).every((site) => verdictFor(site.fn, site.ranges).finite);

  it("passes a clamp to the function's own finite range", () => {
    expect(finite("fn f(x : f32) -> f32 { return exp(clamp(x, -50.0, 80.0)); }")).toBe(true);
    expect(finite("fn f(x : f32) -> f32 { return tanh(clamp(x, -20.0, 20.0)); }")).toBe(true);
    expect(finite("fn f(x : f32) -> f32 { return log2(max(x, 1e-4)); }")).toBe(true);
  });

  it("FAILS a clamp that is wide enough to overflow anyway", () => {
    // The case this file exists to be able to fail. Clamped, and thirty orders
    // of magnitude past where f32's `exp` stops being a number.
    expect(finite("fn f(x : f32) -> f32 { return exp(clamp(x, 0.0, 1e30)); }")).toBe(false);
    expect(finite("fn f(x : f32) -> f32 { return exp2(clamp(x, 0.0, 200.0)); }")).toBe(false);
  });

  it("FAILS an unbounded argument, whatever the function", () => {
    for (const call of ["exp(x)", "exp2(x)", "log(x)", "log2(x)", "sinh(x)", "cosh(x)"]) {
      expect(finite(`fn f(x : f32) -> f32 { return ${call}; }`), call).toBe(false);
    }
  });

  it("FAILS a tanh whose argument can reach the exp(2t) overflow — §5.159b's own defect", () => {
    // The unfixed shader, written out: a cubic in a distance with nothing
    // bounding the distance.
    expect(
      finite(
        "fn f(d : f32, s : f32) -> f32 { let x = -d / max(s, 1e-4); " +
          "return 0.5 * (1.0 + tanh(0.7978845608028654 * (x + 0.044715 * x * x * x))); }",
      ),
    ).toBe(false);
    // And the fix, at the same site.
    expect(
      finite(
        "fn f(d : f32, s : f32) -> f32 { let x = -d / max(s, 1e-4); " +
          "let t = clamp(0.7978845608028654 * (x + 0.044715 * x * x * x), -20.0, 20.0); " +
          "return 0.5 * (1.0 + tanh(t)); }",
      ),
    ).toBe(true);
    // A clamp past the lowering's own limit is not a fix: 50 > ln(f32max)/2.
    expect(finite("fn f(x : f32) -> f32 { return tanh(clamp(x, -50.0, 50.0)); }")).toBe(false);
  });

  it("FAILS a log or an inverse square root whose argument reaches its pole", () => {
    expect(finite("fn f(x : f32) -> f32 { return log(clamp(x, 0.0, 1.0)); }")).toBe(false);
    expect(finite("fn f(x : f32) -> f32 { return inverseSqrt(max(x, 0.0)); }")).toBe(false);
    expect(finite("fn f(x : f32) -> f32 { return inverseSqrt(max(x, 1e-6)); }")).toBe(true);
  });

  it("FAILS a pow whose base can be negative, and one whose base and exponent are both zero", () => {
    expect(finite("fn f(x : f32) -> f32 { return pow(x, 2.0); }")).toBe(false);
    expect(finite("fn f(x : f32) -> f32 { return pow(clamp(x, -1.0, 1.0), 2.0); }")).toBe(false);
    expect(finite("fn f(x : f32, e : f32) -> f32 { return pow(clamp(x, 0.0, 1.0), e); }")).toBe(
      false,
    );
    expect(finite("fn f(x : f32) -> f32 { return pow(clamp(x, 0.0, 1.0), 2.4); }")).toBe(true);
    // A floor alone is not enough when the exponent is above 1: the base's
    // CEILING is what f32max^2.4 overflows on.
    expect(finite("fn f(x : f32) -> f32 { return pow(max(x, 1e-6), 2.4); }")).toBe(false);
    expect(finite("fn f(x : f32) -> f32 { return pow(clamp(x, 1e-6, 1.0), 2.4); }")).toBe(true);
    // And an exponent under 1 makes the ceiling harmless — f32max^0.4167 is
    // 1.1e16, which is why `linear_to_srgb`'s own `pow` needs no ceiling.
    expect(finite("fn f(x : f32) -> f32 { return pow(max(x, 0.0), 1.0 / 2.4); }")).toBe(true);
  });

  it("reads comments as comments, which is how `exp(2t)` in a note stays a note", () => {
    // `optics.ts`'s own §5.159b paragraph contains this text. A scanner that
    // read it would classify prose, and — worse — would report coverage it does
    // not have the day the prose changes.
    expect(scan("// a backend that lowers tanh to (exp(2t) - 1)/(exp(2t) + 1)\n")).toEqual([]);
    expect(scan("/* pow(x, y) and log2(z) */\nfn f() -> f32 { return 1.0; }")).toEqual([]);
  });

  it("resolves through a binding, a helper and a scope, and not across two scopes", () => {
    // The three resolutions the real shaders need, and the one mistake that
    // would make the answer wrong: `optics.ts` has a `let t` in two functions.
    expect(finite("fn f(x : f32) -> f32 { let t = clamp(x, -1.0, 1.0); return exp(t); }")).toBe(
      true,
    );
    expect(
      finite(
        "fn g(a : f32) -> f32 { return clamp(a, -2.0, 2.0); }\n" +
          "fn f(x : f32) -> f32 { return exp(g(x)); }",
      ),
    ).toBe(true);
    expect(
      finite(
        "fn a(x : f32) -> f32 { let t = clamp(x, -1.0, 1.0); return t; }\n" +
          "fn b(x : f32) -> f32 { let t = x * 1e30; return exp(t); }",
      ),
    ).toBe(false);
  });
});
