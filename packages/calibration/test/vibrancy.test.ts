import { describe, expect, it } from "vitest";
import { LUMA_REC709, OPERATOR_TOLERANCE, decompose, read } from "../scripts/vibrancy";

/**
 * The corpus is committed evidence, so these numbers are what W27e G0 read and not
 * a target. A dump appearing, disappearing or changing moves one of them, which is
 * the point: the claim in §5.133 is about a specific 57 files, and a later wave
 * that adds a sixth dump tree has to come here and say so.
 */
const reading = read();

const matrix = (rows: readonly (readonly number[])[]) => rows.flat();
const luma = (r: number, g: number, b: number) =>
  LUMA_REC709[0] * r + LUMA_REC709[1] * g + LUMA_REC709[2] * b;

describe("W27e vibrantColorMatrix decomposition", () => {
  it("reads the identity as pure chroma gain with no luma term and no offset", () => {
    const d = decompose(matrix([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0]]));
    expect(d.chromaGain).toBeCloseTo(1, 12);
    expect(d.lumaGain.every((g) => Math.abs(g) < 1e-12)).toBe(true);
    expect(d.maxResidual).toBeLessThan(1e-12);
    expect(d.achromatic).toBe(true);
    expect(d.alphaRowIsIdentity).toBe(true);
  });

  it("reads a full desaturation as zero chroma gain on the Rec.709 weights", () => {
    const l = LUMA_REC709;
    const d = decompose(matrix([
      [l[0], l[1], l[2], 0, 0], [l[0], l[1], l[2], 0, 0], [l[0], l[1], l[2], 0, 0],
      [0, 0, 0, 1, 0],
    ]));
    expect(Math.abs(d.chromaGain)).toBeLessThan(1e-12);
    expect(d.lumaGain.every((g) => Math.abs(g - 1) < 1e-12)).toBe(true);
    expect(d.maxResidual).toBeLessThan(1e-12);
  });

  it("refuses a matrix that is not twenty floats", () => {
    expect(() => decompose([1, 0, 0])).toThrow(/twenty floats/);
  });

  it("reports a residual when the matrix does not factor through Rec.709 luma", () => {
    const d = decompose(matrix([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0.5, 0, 0.5, 0, 0],
      [0, 0, 0, 1, 0]]));
    expect(d.maxResidual).toBeGreaterThan(0.1);
  });

  it("evaluates the same map the matrix does", () => {
    const flat = reading.operators[0]?.matrix as readonly number[];
    const d = decompose(flat);
    for (const [c, expected] of [[[0, 0, 0], d.maps["black"]], [[1, 1, 1], d.maps["white"]]] as const) {
      const y = luma(c[0] as number, c[1] as number, c[2] as number);
      for (let i = 0; i < 3; i += 1) {
        const direct = (flat[i * 5] as number) * (c[0] as number)
          + (flat[i * 5 + 1] as number) * (c[1] as number)
          + (flat[i * 5 + 2] as number) * (c[2] as number) + (flat[i * 5 + 4] as number);
        const viaForm = d.chromaGain * (c[i] as number) + (d.lumaGain[i] as number) * y
          + (d.offset[i] as number);
        expect(viaForm).toBeCloseTo(direct, 3);
        expect((expected as readonly number[])[i]).toBeCloseTo(viaForm, 12);
      }
    }
  });
});

describe("W27e G0: how much of the committed corpus was read", () => {
  it("reads every dump in the five committed trees", () => {
    expect(reading.dumps.length).toBe(57);
    expect(new Set(reading.dumps.map((d) => d.path)).size).toBe(57);
    expect(new Set(reading.rows.map((r) => r.dump)).size).toBe(57);
  });

  it("finds sixty vibrantColorMatrix occurrences in four distinct matrices", () => {
    expect(reading.rows.length).toBe(60);
    expect(reading.operators.length).toBe(4);
    expect(reading.operators.map((o) => o.count).reduce((a, b) => a + b, 0)).toBe(60);
  });

  it("splits them into fifty-eight on the highlight and two on the author tint", () => {
    const by = (role: string) => reading.rows.filter((r) => r.role === role);
    expect(by("surface-highlight").length).toBe(58);
    expect(by("author-tint").length).toBe(2);
    expect(by("unclassified").length).toBe(0);
    expect(new Set(by("author-tint").map((r) => r.tint))).toEqual(new Set(["blue", "orange"]));
  });

  it("carries every occurrence on a CASDFLayer, never on a content layer", () => {
    expect(new Set(reading.rows.map((r) => r.layerClass))).toEqual(new Set(["CASDFLayer"]));
    expect(new Set(reading.rows.map((r) => r.layerEffect)))
      .toEqual(new Set(["CASDFKeyFillHighlightEffect", "CASDFGradientEffect"]));
  });

  it("finds exactly two distinct foreground operators, the second on two cells", () => {
    const foreground = reading.rows.filter((r) => r.role === "surface-highlight");
    const ids = [...new Set(foreground.map((r) => r.operatorId))];
    expect(ids.length).toBe(2);
    const counts = ids.map((id) => foreground.filter((r) => r.operatorId === id).length).sort();
    expect(counts).toEqual([2, 56]);
    const rare = ids.find((id) => foreground.filter((r) => r.operatorId === id).length === 2);
    expect(foreground.filter((r) => r.operatorId === rare).map((r) => r.scene).sort())
      .toEqual(["dark-solid__capsule-button__rest", "impulse__capsule-button__rest"]);
  });

  it("states the two foreground operators in the form the ledger quotes", () => {
    const foreground = reading.rows.filter((r) => r.role === "surface-highlight");
    const at = (scene: string) => {
      const row = foreground.find((r) => r.scene === scene);
      if (!row) throw new Error(`No highlight row for ${scene}`);
      return decompose(row.matrix);
    };
    const normal = at("checkerboard__rrect-md__rest");
    expect(normal.chromaGain).toBeCloseTo(1.5, 4);
    expect(normal.offset.every((b) => Math.abs(b - 0.9) < 1e-6)).toBe(true);
    expect(normal.levelGain[1]).toBeCloseTo(0.1, 4);
    const dark = at("dark-solid__capsule-button__rest");
    expect(dark.chromaGain).toBeCloseTo(3, 4);
    expect(dark.offset.every((b) => Math.abs(b - 0.15) < 1e-6)).toBe(true);
    expect(dark.levelGain[1]).toBeCloseTo(1.35, 4);
    for (const d of [normal, dark]) {
      expect(d.achromatic).toBe(true);
      expect(d.alphaRowIsIdentity).toBe(true);
      expect(d.alphaColumnIsZero).toBe(true);
      expect(d.maxResidual).toBeLessThan(3e-4);
    }
  });

  it("reads both author tints as a pure colorize with no chroma gain at all", () => {
    for (const row of reading.rows.filter((r) => r.role === "author-tint")) {
      const d = decompose(row.matrix);
      expect(Math.abs(d.chromaGain)).toBeLessThan(1e-5);
      expect(d.maxResidual).toBeLessThan(1e-8);
      expect(d.achromatic).toBe(false);
      expect(row.input).toBe("backdrop-beneath");
    }
    expect(new Set(reading.rows.filter((r) => r.role === "surface-highlight")
      .map((r) => r.input))).toEqual(new Set(["own-content"]));
  });

  it("agrees with every committed declaration about the surface's span", () => {
    expect(reading.rows.filter((r) => !r.surface.spanAgrees)).toEqual([]);
    const spans = new Set(reading.rows.map((r) => Math.round(r.surface.spanFromDump ?? NaN)));
    expect([...spans].sort((a, b) => a - b))
      .toEqual([32, 44, 48, 56, 64, 72, 80, 88, 96, 112, 128, 130, 160]);
  });

  it("records that the whole corpus is one scheme, one scale and one accessibility mode", () => {
    expect(new Set(reading.rows.map((r) => r.colorScheme))).toEqual(new Set(["light"]));
    expect(new Set(reading.rows.map((r) => r.scale))).toEqual(new Set([1]));
    expect(new Set(reading.rows.map((r) => r.a11y))).toEqual(new Set(["standard"]));
    expect(new Set(reading.rows.map((r) => r.isKeyWindow))).toEqual(new Set([true]));
    expect(new Set(reading.rows.map((r) => r.settleSeconds))).toEqual(new Set([8]));
  });

  it("separates the two operators with vitrea's own collapse predicate", () => {
    const foreground = reading.rows.filter((r) => r.role === "surface-highlight");
    const rare = [...new Set(foreground.map((r) => r.operatorId))]
      .find((id) => foreground.filter((r) => r.operatorId === id).length === 2);
    const value = (r: typeof foreground[number]) => r.vitrea.backdropToneAdaptation;
    expect(foreground.every((r) => value(r) !== null)).toBe(true);
    const on = (dark: boolean) => foreground
      .filter((r) => (r.operatorId === rare) === dark).map((r) => value(r) as number);
    expect(Math.min(...on(true))).toBe(1);
    expect(Math.max(...on(false))).toBeLessThan(0.01);
  });

  it("groups operators on float32 equality, not on a tolerance that could merge two", () => {
    const gaps = reading.operators.flatMap((a, i) => reading.operators.slice(i + 1).map((b) =>
      Math.max(...a.matrix.map((v, k) => Math.abs(v - (b.matrix[k] as number))))));
    expect(Math.min(...gaps)).toBeGreaterThan(OPERATOR_TOLERANCE * 1e5);
  });
});
