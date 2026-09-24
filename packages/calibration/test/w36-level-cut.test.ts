/** W36 G0's populations and inversion boundaries, before any fit (§5.178). */
import { readFileSync } from "node:fs";
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
