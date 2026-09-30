/**
 * W42 G2 — the black-join amendment of candidate 1's landed tone
 * (`candidate1-black-join-addendum.md`, the parent's pre-read ruling; its executable form
 * `implementation-design/candidate1_black_join.py` and fixture `fixtures/landed-bridged.json`).
 *
 * Inside W36's open interval below the black join, 0 < x < 0.003 on the branch's own abscissa,
 * the per-pixel landed tone is the straight line in x between the solve's value at black and its
 * value on the argument's own ray at the end. Held here:
 * - the CPU reference is the amended oracle;
 * - the bridge equals the solve at black, at the end and above it, and lies between its two ends;
 * - it stands down where the branch does;
 * - the shader carries the same interval and the same line;
 * - no digest moves.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import {
  landedToneAbscissa,
  landedToneLinear,
  landedToneSolveLinear,
  type LandedToneInputs,
} from "../src/body-law";
import type { Rgb } from "../src/color";
import {
  BACKDROP_TONE_BLACK_JOIN,
  DEFAULT_MATERIAL_PROFILE,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "../src/material";
import { WGSL_OPTICS_PASS } from "../src/wgsl";

const FIXTURES = new URL(
  "../../calibration/results/2026-09-30-w42-g2-identification/implementation-design/fixtures/",
  import.meta.url,
);
const fixture = <T>(name: string): T =>
  JSON.parse(readFileSync(new URL(`${name}.json`, FIXTURES), "utf8")) as T;

interface Params {
  readonly tint: readonly number[]; readonly tintAlpha: number; readonly sizeOcclusionGain: number;
  readonly backdropToneLow: number; readonly backdropToneHigh: number;
  readonly backdropToneSizeBias: number; readonly backdropToneMax: number;
  readonly anchorX: readonly number[]; readonly thin: readonly number[];
  readonly thick: readonly number[]; readonly responseStrength: number;
  readonly black: readonly [number, number, number]; readonly bodyChromaRetention: number;
  readonly abscissa: unknown;
}
const params = fixture<Record<string, { params: Params }>>("landed");
const bridged = fixture<Record<string, { cases: {
  sizeK: number; A: Rgb[]; linear: Rgb[]; inside: boolean[];
}[] }>>("landed-bridged");

const profileOf = (p: Params, blackStrength = p.black[0]) => ({
  backdropToneAnchorX: p.anchorX as unknown as MaterialProfile["backdropToneAnchorX"],
  backdropToneResponseThin: p.thin as unknown as MaterialProfile["backdropToneResponseThin"],
  backdropToneResponseThick: p.thick as unknown as MaterialProfile["backdropToneResponseThick"],
  backdropToneResponseStrength: p.responseStrength,
  backdropToneBlackStrength: blackStrength,
  backdropToneBlackThin: p.black[1],
  backdropToneBlackThick: p.black[2],
});
const inputsOf = (p: Params, sizeK: number): LandedToneInputs => ({
  sizeK, toneLevelFar: 0, neutral: [p.tint[0]!, p.tint[0]!, p.tint[0]!],
  tintAlpha: p.tintAlpha, sizeOcclusionGain: p.sizeOcclusionGain,
  toneStrength: p.backdropToneMax, toneLow: p.backdropToneLow, toneHigh: p.backdropToneHigh,
  toneSizeBias: p.backdropToneSizeBias, retention: p.bodyChromaRetention,
  abscissa: p.abscissa === "source(default)" ? "source" : "silhouette", presence: 1,
});
const grey = (v: number): Rgb => [v, v, v];
const X_END = BACKDROP_TONE_BLACK_JOIN;
const ENDPOINTS = Object.keys(params);
const SIZE_K = [0, 0.0923, 0.35, 1];

describe("W42 black-join amendment: candidate 1's landed tone inside W36's open interval", () => {
  it.each(ENDPOINTS)("%s: the CPU reference is the amended oracle, every sizeK and argument", (ep) => {
    const p = params[ep]!.params;
    let inside = 0;
    for (const run of bridged[ep]!.cases) {
      run.A.forEach((a, i) => {
        if (run.inside[i]) inside += 1;
        landedToneLinear(a, inputsOf(p, run.sizeK), profileOf(p)).forEach((v, c) =>
          expect(v, `${ep} sizeK ${run.sizeK} A ${a}`).toBeCloseTo(run.linear[i]![c]!, 12));
      });
    }
    expect(inside).toBeGreaterThan(40);
  });

  it.each(ENDPOINTS)("%s: the solve's own values at black and at and above the end", (ep) => {
    const p = params[ep]!.params;
    for (const sizeK of SIZE_K) {
      const inputs = inputsOf(p, sizeK);
      for (const v of [0, 0.0031, 0.0032, 0.004, 0.01, 0.2, 1]) {
        expect(landedToneLinear(grey(v), inputs, profileOf(p)))
          .toEqual(landedToneSolveLinear(grey(v), inputs, profileOf(p)));
      }
      // At the end itself the encoded luma of a grey is its value only to an ulp (the weights sum
      // to 1 in f64 only to an ulp), so a grey at 0.003 may read a hair inside: the line's end
      // is then the solve on A's own ray a hair further out, equal to the solve to 1e-14.
      const atEnd = landedToneLinear(grey(X_END), inputs, profileOf(p));
      const solved = landedToneSolveLinear(grey(X_END), inputs, profileOf(p));
      for (let c = 0; c < 3; c++) expect(atEnd[c]!).toBeCloseTo(solved[c]!, 14);
    }
  });

  it.each(ENDPOINTS)("%s: inside, the straight line between the two ends, per channel", (ep) => {
    const p = params[ep]!.params;
    for (const sizeK of SIZE_K) {
      const inputs = inputsOf(p, sizeK);
      const y0 = landedToneSolveLinear(grey(0), inputs, profileOf(p));
      const y1 = landedToneSolveLinear(grey(X_END), inputs, profileOf(p));
      for (let k = 1; k < 300; k++) {
        const v = (X_END * k) / 300;
        const x = landedToneAbscissa(grey(v), inputs.abscissa);
        const y = landedToneLinear(grey(v), inputs, profileOf(p));
        for (let c = 0; c < 3; c++) {
          expect(y[c]!).toBeGreaterThanOrEqual(Math.min(y0[c]!, y1[c]!) - 1e-15);
          expect(y[c]!).toBeLessThanOrEqual(Math.max(y0[c]!, y1[c]!) + 1e-15);
          expect(y[c]!).toBeCloseTo(y0[c]! + (x / X_END) * (y1[c]! - y0[c]!), 12);
        }
      }
      // Continuous at the end: the line arrives at the solve's own value there.
      const below = landedToneLinear(grey(X_END * (1 - 1e-9)), inputs, profileOf(p));
      for (let c = 0; c < 3; c++) expect(below[c]!).toBeCloseTo(y1[c]!, 6);
    }
  });

  it.each(ENDPOINTS)("%s: a chromatic argument inside rides its own ray to the end", (ep) => {
    const p = params[ep]!.params;
    const inputs = inputsOf(p, 0.35);
    let seen = 0;
    for (let i = 0; i < 400; i++) {
      const a: Rgb = [((i * 37) % 97) / 97 * 0.006, ((i * 53) % 89) / 89 * 0.004,
        ((i * 71) % 83) / 83 * 0.01];
      const x = landedToneAbscissa(a, inputs.abscissa);
      if (!(x > 0 && x < X_END)) continue;
      seen += 1;
      const scale = (X_END / x) * 1.0;
      // The end on the ray, found by bisection on the abscissa itself: no form of the ray assumed.
      let lo = 0, hi = scale * 4;
      for (let n = 0; n < 200; n++) {
        const mid = (lo + hi) / 2;
        const probe = rayPoint(a, mid, inputs.abscissa);
        if (landedToneAbscissa(probe, inputs.abscissa) < X_END) lo = mid; else hi = mid;
      }
      const end = rayPoint(a, hi, inputs.abscissa);
      const y0 = landedToneSolveLinear(grey(0), inputs, profileOf(p));
      const y1 = landedToneSolveLinear(end, inputs, profileOf(p));
      const y = landedToneLinear(a, inputs, profileOf(p));
      for (let c = 0; c < 3; c++) {
        expect(y[c]!).toBeCloseTo(y0[c]! + (x / X_END) * (y1[c]! - y0[c]!), 9);
      }
    }
    expect(seen).toBeGreaterThan(100);
  });

  it("stands down where the branch does: at strength 0 it is the solve everywhere", () => {
    const p = params[ENDPOINTS[0]!]!.params;
    const inputs = inputsOf(p, 0.35);
    for (let k = 0; k <= 40; k++) {
      const v = (X_END * k) / 30;
      expect(landedToneLinear(grey(v), inputs, profileOf(p, 0)))
        .toEqual(landedToneSolveLinear(grey(v), inputs, profileOf(p, 0)));
    }
  });

  it("is what the shader draws: the same end, the same abscissa and the same line", () => {
    expect(X_END).toBe(0.003);
    expect(WGSL_OPTICS_PASS).toContain("const LAW_BLACK_JOIN_END = 0.003;");
    // The shipped branch's own end, which the constant restates.
    expect(WGSL_OPTICS_PASS).toContain("if (ou.toneBlack.x > 0.0 && encodedInput < 0.003) {");
    const amended = WGSL_OPTICS_PASS.slice(WGSL_OPTICS_PASS.indexOf("fn body_law_landed("),
      WGSL_OPTICS_PASS.indexOf("fn body_law_body("));
    for (const line of [
      "if (ou.toneBlack.x <= 0.0) {",
      "if (silhouette) { level = srgb_to_linear(vec3f(clamp(encodedLuma, 0.0, 1.0))).x; }",
      "let x = srgb_encode(level);",
      "if (!(x > 0.0 && x < LAW_BLACK_JOIN_END)) {",
      "var atEnd = encoded * (LAW_BLACK_JOIN_END / encodedLuma);",
      "atEnd = linear_to_srgb(c * (endLevel / dot(c, LAW_LUMA)));",
      "let f = x / LAW_BLACK_JOIN_END;",
      "return mix(body_law_landed_solve(vec3f(0.0), sizeK, toneLevelFar, neutral),",
      "body_law_landed_solve(atEnd, sizeK, toneLevelFar, neutral), vec3f(f));",
    ]) expect(amended, line).toContain(line);
    // The body reads the amended tone, not the solve beneath it.
    expect(WGSL_OPTICS_PASS).toContain(
      "body = body_law_landed(lawArgument.rgb, sizeK, toneLevelFar, neutral);");
  });

  it.each([
    ["apple-macos-26.5-1x-light-standard", "b2b570e4adcea8fb"],
    ["apple-macos-26.5-1x-dark-standard", "874be66ea501621b"],
    ["apple-macos-27.0-1x-light-standard-glass0.5", "be13dae45098fc89"],
    ["apple-macos-27.0-1x-dark-standard-glass0.5", "2a4323f33df8d799"],
    ["apple-macos-27.0-1x-light-standard-glass0.5-receded", "b0d0d8dacc6a03af"],
    ["apple-macos-27.0-1x-dark-standard-glass0.5-receded", "7c454858a3cbad5b"],
  ])("moves no digest: %s still resolves to %s", (name, sha) => {
    const read = (file: string) => JSON.parse(readFileSync(new URL(
      `../../calibration/profiles/${file}.json`, import.meta.url), "utf8")) as {
      patch: MaterialProfilePatch; resolvedMaterialSha256: string; resolvedOverActiveDocument?: string;
    };
    const document = read(name);
    const base = document.resolvedOverActiveDocument
      ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
        read(document.resolvedOverActiveDocument.replace(/\.json$/, "")).patch)
      : DEFAULT_MATERIAL_PROFILE;
    const material = withMaterialOverrides(base, document.patch);
    expect(document.resolvedMaterialSha256).toBe(sha);
    expect(createHash("sha256").update(JSON.stringify(sorted(materialDigestInput(material))))
      .digest("hex").slice(0, 16)).toBe(sha);
  });
});

/** A point on the argument's own ray: encoded for the silhouette abscissa, linear for the source. */
function rayPoint(a: Rgb, t: number, abscissa: LandedToneInputs["abscissa"]): Rgb {
  if (abscissa === "silhouette") return [a[0] * t, a[1] * t, a[2] * t];
  const dec = (v: number) => (v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
  const enc = (v: number) => (v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(v, 1 / 2.4) - 0.055);
  return [enc(dec(a[0]) * t), enc(dec(a[1]) * t), enc(dec(a[2]) * t)];
}

function sorted(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sorted);
  if (value === null || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b))
    .map(([key, item]) => [key, sorted(item)]));
}
