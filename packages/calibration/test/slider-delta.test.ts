/**
 * The slider reading's instrument (W43 G2, charter clause 7): the rule that pairs a cell at one
 * Glass-slider position with the same cell at another, the two-sided bar, and the radial profile.
 *
 * The pairing is tested against `scenes.json` itself, as the native delta's is: a silently mispaired
 * cell would read two different scenes as one, and a hand-written expectation would carry the same
 * assumption as the code it checks.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { sliderCounterpartKey } from "../cli/native-delta-metrics";
import {
  metricBound,
  radialProfile,
  recedeBound,
  twoSided,
  RADIAL_BANDS,
} from "../cli/slider-delta";
import { componentRegion, type DeclaredComponent } from "../src/component-region";
import { fromLinearLuminance } from "./synthesise";

const REFERENCE = resolve(import.meta.dirname, "..", "..", "..", "apps", "reference-apple");

const spec = JSON.parse(readFileSync(resolve(REFERENCE, "scenes.json"), "utf8")) as {
  readonly profiles: readonly { readonly key: string; readonly scenes: readonly string[] }[];
};

describe("the pairing of a cell at one slider position with the same cell at another", () => {
  it("maps every declared glass0.25 key onto a declared glass0.5 key with the same scene list", () => {
    const byKey = new Map(spec.profiles.map((profile) => [profile.key, profile]));
    const subjects = spec.profiles.filter((profile) => profile.key.endsWith("-glass0.25"));
    expect(subjects).toHaveLength(4);
    for (const subject of subjects) {
      const reference = byKey.get(sliderCounterpartKey(subject.key, "0.5"));
      expect(reference?.key.endsWith("-standard-glass0.5")).toBe(true);
      expect(reference?.scenes).toEqual(subject.scenes);
    }
  });

  it("moves the slider token and nothing else", () => {
    expect(sliderCounterpartKey("apple-macos-27.0-2x-dark-standard-glass0.25", "0.5")).toBe(
      "apple-macos-27.0-2x-dark-standard-glass0.5",
    );
  });

  it("refuses a key with no slider axis, and a key already at the reference position", () => {
    expect(() => sliderCounterpartKey("apple-macos-26.5-1x-light-standard", "0.5")).toThrow(/no -glass/);
    expect(() => sliderCounterpartKey("apple-macos-27.0-1x-light-standard-glass0.5", "0.50")).toThrow(
      /already at/,
    );
    expect(() => sliderCounterpartKey("apple-macos-27.0-1x-light-standard-glass0.25", "half")).toThrow(
      /not a slider amount/,
    );
  });
});

describe("the two-sided bar", () => {
  const bar = { bedMinimumNonZeroBar: { ssimComplement: 1e-9 } };

  it("takes each side's own spread, else its bed minimum, else exactly zero", () => {
    const own = { pairwise: { ssimComplement: { n: 21, min: 0, median: 0, p95: 0.002, max: 0.003 } } };
    const zero = { pairwise: { ssimComplement: { n: 21, min: 0, median: 0, p95: 0, max: 0 } } };
    expect(metricBound(bar, own, "ssimComplement")).toEqual({ value: 0.003, level: "cell" });
    expect(metricBound(bar, zero, "ssimComplement")).toEqual({ value: 1e-9, level: "bed-minimum" });
    expect(metricBound({ bedMinimumNonZeroBar: {} }, zero, "ssimComplement")).toEqual({
      value: 0,
      level: "bed-zero",
    });
    expect(metricBound(bar, undefined, "ssimComplement")).toBeUndefined();
  });

  it("is the larger of the two sides, and says which side and level it came from", () => {
    expect(twoSided({ value: 0, level: "bed-zero" }, { value: 0.003, level: "cell" })).toEqual({
      value: 0.003,
      source: "reference:cell",
    });
    expect(twoSided({ value: 0.004, level: "cell" }, { value: 0.003, level: "cell" })).toEqual({
      value: 0.004,
      source: "subject:cell",
    });
    expect(twoSided({ value: 0, level: "bed-zero" }, { value: 0, level: "bed-zero" })).toEqual({
      value: 0,
      source: "both:bed-zero",
    });
    expect(twoSided(undefined, { value: 1e-9, level: "bed-minimum" })?.source).toBe("reference:bed-minimum");
    expect(twoSided(undefined, undefined)).toBeUndefined();
  });

  it("sums a recede's two cells, each falling back to the bed's minimum spread", () => {
    const stable = { readingSpread: { bodyLevel: 0 } };
    const noisy = { readingSpread: { bodyLevel: 0.002 } };
    expect(recedeBound(noisy, noisy, "bodyLevel", 1e-9)).toEqual({ value: 0.004, level: "cell" });
    expect(recedeBound(noisy, stable, "bodyLevel", 1e-9)).toEqual({ value: 0.002 + 1e-9, level: "bed-minimum" });
    expect(recedeBound(stable, stable, "bodyLevel", undefined)).toEqual({ value: 0, level: "bed-zero" });
  });
});

describe("the radial difference profile", () => {
  const canvas = { width: 320, height: 200 };
  const component: DeclaredComponent = { kind: "rrect", size: [160, 96], radius: 20 };
  const region = componentRegion(component, { canvas, scale: 1, width: 320, height: 200 });
  const cell = (body: number, exterior: number) =>
    fromLinearLuminance(320, 200, (x, y) => ((region.signedDistancePx[y * 320 + x] ?? 0) < 0 ? body : exterior));

  it("reads a capture against itself as identical in every band", () => {
    const image = cell(0.5, 0.1);
    const bands = radialProfile(image, image, region.signedDistancePx, 1);
    expect(bands.map((band) => band.band)).toEqual(RADIAL_BANDS.map((band) => band.name));
    for (const band of bands) expect(band.differing).toBe(0);
  });

  it("puts a body-only change inside the contour and nothing outside it", () => {
    const bands = radialProfile(cell(0.5, 0.1), cell(0.4, 0.1), region.signedDistancePx, 1);
    const named = new Map(bands.map((band) => [band.band, band]));
    for (const inside of ["deep", "shoulder", "edge"]) {
      expect(named.get(inside)?.differing).toBe(named.get(inside)?.pixels);
      expect(named.get(inside)?.meanSignedLuminance ?? 0).toBeLessThan(0);
    }
    for (const outside of ["near-exterior", "exterior", "far"]) expect(named.get(outside)?.differing).toBe(0);
  });
});
