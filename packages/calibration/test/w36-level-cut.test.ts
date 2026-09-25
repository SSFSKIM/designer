/** W36 G0's populations and inversion boundaries, before any fit (§5.178). */
import { loadGeneration } from "../src/matrix-store";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const here = resolve(import.meta.dirname, "../results/2026-09-24-w36-g0-level-cut");
const read = (name: string) => JSON.parse(readFileSync(resolve(here, name), "utf8"));

describe("W36 level cut — measured populations, not copied memo numbers", () => {
  it("keeps both rasters and all 13 circular solid levels in all four endpoints", () => {
    const rows = read("solid-cut.json");
    expect(rows).toHaveLength(104);
    expect(new Set(rows.map((r: { cell: string }) => r.cell)).size).toBe(104);
    for (const r of rows) {
      expect(r.pixels).toBeGreaterThanOrEqual(4);
      expect(r.role).toMatch(/^(calibration|validation)$/);
      const other = rows.find((candidate: { cell: string }) => candidate.cell ===
        r.cell.replace(r.scale === 1 ? "-1x-" : "-2x-", r.scale === 1 ? "-2x-" : "-1x-"));
      expect(other.nativeMedian).toEqual(r.nativeMedian);
      expect(other.webMedian).toEqual(r.webMedian);
      expect(r.webMinusNativeEncoded).toEqual(r.webMedian.map((v: number, i: number) =>
        v - r.nativeMedian[i]));
    }
  });

  it("refuses full-RGB inversion for every cell with any censored channel", () => {
    const rows = read("chroma-cut.json");
    expect(rows).toHaveLength(48);
    for (const r of rows) {
      const censored = [0, 1, 2].filter(i => r.nativeMedian[i] === 255 || r.webMedian[i] === 255);
      expect(r.censoredChannels).toEqual(censored);
      if (censored.length) {
        expect(r.nativeRetention).toBeNull();
        expect(r.nativeLuma).toBeNull();
        expect(r.operatorRetentionRequired).toBeNull();
      } else {
        expect(r.nativeRetention).toBeGreaterThan(0.8);
        expect(r.nativeRetention).toBeCloseTo(r.qBase + (1 - r.qBase) *
          r.operatorRetentionRequired, 12);
      }
    }
    expect(rows.filter((r: { censoredChannels: number[] }) => r.censoredChannels.length)).toHaveLength(14);
    const expectedCensors = [1, 2].flatMap(scale => [
      ...["rest", "inactive"].flatMap(pose => ["red", "blue", "magenta"].map(colour =>
        `apple-macos-27.0-${scale}x-light-standard-glass0.5/${colour}__circular-120__${pose}`)),
      `apple-macos-27.0-${scale}x-dark-standard-glass0.5/blue__circular-120__rest`,
    ]).sort();
    expect(rows.filter((r: { censoredChannels: number[] }) => r.censoredChannels.length)
      .map((r: { cell: string }) => r.cell).sort()).toEqual(expectedCensors);
  });

  it("reconstructs the shader on the 48 non-black medians without fitting them", () => {
    const proof = read("mechanisms.json");
    expect(proof.responseChecks).toHaveLength(48);
    expect(Math.max(...proof.responseChecks.map((r: { errorCodes: number }) =>
      Math.abs(r.errorCodes)))).toBeLessThan(0.5);
    expect(proof.black.map((r: { fallbackCodes: number }) => Math.round(r.fallbackCodes)))
      .toEqual([181, 181, 60, 60]);
  });
});


describe("W36 frozen declaration and independent referees", () => {
  it("pins the pre-fit declaration by its bytes", () => {
    expect(createHash("sha256").update(readFileSync(resolve(here, "bounds-declaration.md")))
      .digest("hex")).toBe("15e1c72f7faf8ee8ab74e487af8b2d527764692addf625db5610e6ca36d2a3bb");
  });

  it("re-derives L1's baseline from its named generation, not the future fitted one", () => {
    const d = read("l1-declaration.json");
    const baseline = read("l1-baseline.json");
    expect(d.sets).toEqual(["calibration", "validation"]);
    expect(d.absoluteBound).toBe(0.055);
    expect(d.growthBound).toBe(0.005);
    expect(baseline).toHaveLength(140);
    expect(baseline.filter((r: { absoluteError: number | null }) => r.absoluteError !== null))
      .toHaveLength(136);
    expect(d.absoluteMisses.map((r: { cell: string }) => r.cell)).toEqual([1, 2].map(scale =>
      `apple-macos-27.0-${scale}x-light-standard-glass0.5/impulse__capsule-button__inactive-tint-orange`));
    const root = resolve(here, "../../../..");
    for (const scheme of ["light", "dark"]) {
      const generation = d.baselineGeneration[scheme];
      const source = { cells: loadGeneration(generation.active, generation.receded) };
      const spec = JSON.parse(readFileSync(resolve(root, "apps/reference-apple/scenes.json"), "utf8"));
      const allowed = new Set([...spec.split.calibration, ...spec.split.validation]);
      const selected = source.cells.filter((c: { key: { profileKey: string; sceneId: string;
        web: { renderer: string; capturePath: string } }; tier: string }) =>
        allowed.has(c.key.sceneId) && c.key.profileKey.includes(`-${scheme}-standard-`) &&
        c.key.profileKey.startsWith("apple-macos-27.0-") && c.tier === "texture" &&
        c.key.web.renderer === "webgpu" && c.key.web.capturePath.includes(`sha256:${generation.active}`));
      expect(selected).toHaveLength(scheme === "light" ? 98 : 42);
      for (const c of selected) {
        const b = baseline.find((r: { cell: string }) => r.cell === `${c.key.profileKey}/${c.key.sceneId}`);
        expect(b).toBeDefined();
        expect(c.key.web.capturePath).toContain(`sha256:${generation.receded}`);
        const n = c.material?.interiorMeanNative?.value;
        const w = c.material?.interiorMeanWeb?.value;
        expect(b.absoluteError).toBe(n === undefined || w === undefined ? null : Math.abs(w - n));
      }
    }
  });

  it("never admits validation or a backdrop-name scheme alias to the fit", () => {
    const fits = read("candidate-fit.json");
    expect(fits).toHaveLength(4);
    for (const f of fits) {
      expect(f.fitParameters).toBe(3);
      expect(f.jacobianRank).toBe(3);
      for (const r of f.readings) {
        expect(r.cell.split("/")[0]).toContain(`-${f.scheme}-standard-`);
        if (r.role === "validation") expect(r.cell).toContain("grey-96__circular-120__");
        else expect(r.cell).toMatch(/\/(grey-(32|64|128|160|255)__circular-120|(?:light|dark|mid-dark)-solid__rrect-md)__/);
      }
    }
  });

  it("keeps both abscissa formulas on one domain and never imputes clipped luminance", () => {
    const rows = read("abscissa-comparison.json");
    const censored = new Set(read("censoring.json").cells.map((r: { cell: string }) => r.cell));
    for (const r of rows) {
      expect(censored.has(r.cell)).toBe(false);
      expect(r.encodedLuma).toBeGreaterThanOrEqual(r.encodedChannelSum - 1e-12);
      if (r.cell.includes("/grey-")) expect(r.encodedLuma).toBeCloseTo(r.encodedChannelSum, 12);
    }
    const canonical = read("canonical-solids.json");
    expect(canonical).toHaveLength(39);
    for (const r of canonical.filter((r: { censoredChannels: number[] }) => r.censoredChannels.length)) {
      expect(r.nativeLuma).toBeNull();
      expect(r.webLuma).toBeNull();
    }
  });

  it("records the failed candidate rather than certifying a subset as the whole gate", () => {
    const grey = read("candidate-greys.json");
    const structured = read("candidate-structured.json");
    expect(grey).toHaveLength(40);
    expect(structured).toHaveLength(24);
    expect(structured.every((r: { nativeMatchesBaseline: boolean }) => r.nativeMatchesBaseline)).toBe(true);
    expect(structured.filter((r: { cell: string; growth: number }) =>
      r.cell.includes("-light-") && r.cell.includes("/photo__") && r.growth > 0.005)).toHaveLength(4);
    expect(structured.filter((r: { cell: string; structureDelta: number }) =>
      r.cell.includes("-dark-") && r.cell.endsWith("/photo__rrect-md__rest") &&
      r.structureDelta > 0.02)).toHaveLength(2);
    const exterior = read("exterior-check.json").rows;
    expect(exterior).toHaveLength(24);
    expect(exterior.reduce((sum: number, r: { changed: number }) => sum + r.changed, 0)).toBe(0);
    const bars = read("deep-median-bars.json");
    expect(bars).toHaveLength(120);
    expect(bars.every((r: { observations: number; pixels: number }) =>
      r.observations === 7 && r.pixels >= 4)).toBe(true);
  });
});
