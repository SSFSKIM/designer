import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { CSS_TIER_MAPPING } from "@vitreajs/vitrea-web";
import {
  LABEL_MATRICES,
  LABEL_OPERATOR_BY_SCHEME,
  LUMA_REC709,
  OPERATOR_TOLERANCE,
  PROBE_DUMP_DIRS,
  PROBE_1X_ARMS,
  PROBE_1X_DUMP_DIRS,
  applyColorMatrix,
  armOf,
  decompose,
  labelInk,
  labelOperatorFor,
  read,
} from "../scripts/vibrancy";

/**
 * W27e G1's browser proof, scored against the tolerance declared before it ran.
 * Read from the committed evidence rather than restated, so the assertions below
 * fail if the evidence moves.
 */
const verdict = JSON.parse(readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)),
    "../results/2026-09-12-w27e-g1/verdict.json"),
  "utf8",
)) as {
  declaredTolerance: { bound: number };
  A_passes: boolean;
  A_measuredTolerance: number;
  B_foldAgainstDeclaredPath: { maxAbsDiffCodeValues: number };
  C_alternativeReading: { blendSupport: Record<string, boolean> };
};

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

/**
 * The labelled probe run of §5.133 §7, taken on 2026-09-11 on the 26.5 capture
 * machine before it could be updated. A second corpus, never merged with G0's: the
 * numbers below are about 50 different files under a different configuration, and
 * pooling them would move a published count.
 */
const probe = read(PROBE_DUMP_DIRS, null);
const labels = probe.rows.filter((r) => r.role === "content-label");
const highlights = probe.rows.filter((r) => r.role === "surface-highlight");
const inScheme = (rows: typeof probe.rows, scheme: string) =>
  rows.filter((r) => r.colorScheme === scheme);

describe("W27e's labelled probe: does a label carry the operator at all", () => {
  it("differs from the G0 corpus in scale AND in window pose, which every comparison must carry", () => {
    // The pose is not a detail of how the probe was taken; it is the axis W27c is
    // measuring. Pinned here so that any later reading across the two corpora has
    // to acknowledge it rather than compare "1x against 2x".
    expect(new Set(probe.rows.map((r) => r.isKeyWindow))).toEqual(new Set([false]));
    expect(new Set(reading.rows.map((r) => r.isKeyWindow))).toEqual(new Set([true]));
    expect(new Set(probe.rows.map((r) => r.scale))).toEqual(new Set([2]));
    expect(new Set(reading.rows.map((r) => r.scale))).toEqual(new Set([1]));
  });

  it("reads both schemes of the run, and nothing else", () => {
    // The corpus is the run, so a dump added to it later has to come here and say
    // so — the same discipline the G0 trees are held to above.
    expect(probe.dumps.length).toBe(50);
    for (const scheme of ["light", "dark"]) {
      expect(probe.dumps.filter((d) => d.colorScheme === scheme).length).toBe(25);
    }
    expect(new Set(probe.rows.map((r) => r.scale))).toEqual(new Set([2]));
  });

  it("commits a label layer for every labelled scene, and only for those", () => {
    // The bare twin of every labelled scene is in the corpus precisely so that the
    // label's layer is identified by difference rather than by recognising a class.
    const declared = probe.dumps.filter((d) => d.declaredLabel != null);
    expect(declared.length).toBe(26);
    expect(declared.every((d) => d.labelLayers === 1)).toBe(true);
    expect(probe.dumps.filter((d) => d.declaredLabel == null)
      .every((d) => d.labelLayers === 0)).toBe(true);
  });

  it("puts a vibrantColorMatrix on the label — the answer §5.133 §8 (c) could not reach", () => {
    // §5.133 §2: "The committed dumps therefore do not contain a label's vibrancy
    // operator." That was a statement about a corpus rendered with `Color.clear`
    // inside every glassEffect. Here the label exists, and so does the operator.
    expect(labels.length).toBe(24);
    expect(probe.dumps.reduce((a, d) => a + d.labelLayersWithOperator, 0)).toBe(24);
  });

  it("puts NOTHING on a label whose colour the author named", () => {
    // The most consequential row in the run, and it is an absence: Apple installs
    // the operator on the automatic label colour and declines to rewrite one the
    // app chose. That is S284 read literally, and it is the root spec's Decision
    // Log #34(c) arriving as a reading of Apple's configuration rather than as a
    // vitrea design decision — so W27e G2 can cite Apple for leaving authored
    // colour alone instead of asserting it.
    const bare = probe.dumps.filter((d) => d.labelLayers > d.labelLayersWithOperator);
    expect(bare.map((d) => d.scene).sort())
      .toEqual(["mid-chroma-solid__capsule-button__rest-label-hot",
        "mid-chroma-solid__capsule-button__rest-label-hot"]);
    expect(bare.map((d) => d.colorScheme).sort()).toEqual(["dark", "light"]);
    expect(bare.every((d) => d.declaredLabel?.srgb != null)).toBe(true);
    // Every dump that took the automatic colour got one.
    expect(probe.dumps.filter((d) => d.declaredLabel != null && d.declaredLabel.srgb == null)
      .every((d) => d.labelLayersWithOperator === 1)).toBe(true);
  });

  it("states the two label operators in the form the ledger quotes", () => {
    // Not the affine-luma form the highlight's two operators take. These are the
    // identity with a unit offset — the whole output shifted a full range down in
    // light and up in dark — and the dark one also scales alpha. Written out in
    // full because a coefficient moving is the thing the pin exists to catch.
    const matrix = (scheme: string) => {
      const rows = inScheme(labels, scheme);
      const distinct = [...new Set(rows.map((r) => JSON.stringify(r.matrix)))];
      expect(distinct.length, scheme).toBe(1);
      return JSON.parse(distinct[0] as string) as number[];
    };
    expect(matrix("light")).toEqual([1, 0, 0, 0, -1, 0, 1, 0, 0, -1, 0, 0, 1, 0, -1, 0, 0, 0, 1, 0]);
    // The dark alpha coefficient is 0.949999988079071, which is 0.95 stored as a
    // float32 — compared to float32's own resolution rather than to the decimal,
    // because the decimal is the number Apple wrote and the float is what the
    // struct holds.
    const dark = matrix("dark");
    expect(dark.map((v, i) => (i === 18 ? 0.95 : v)))
      .toEqual([1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0.95, 0]);
    expect(dark[18]).toBeCloseTo(0.95, 7);
    for (const scheme of ["light", "dark"]) {
      const d = decompose(matrix(scheme));
      expect(d.chromaGain, scheme).toBeCloseTo(1, 12);
      expect(d.lumaGain.every((g) => Math.abs(g) < 1e-12), scheme).toBe(true);
      expect(d.maxResidual, scheme).toBeLessThan(1e-12);
    }
  });

  it("reads the backdrop beneath it, which the surface's own operator does not", () => {
    // §5.133 §2 records `inputBackdropAware` as UNSET on all 58 highlight
    // occurrences. On the label it is 1 on all 24 — the same flag the author
    // tint's colorize carries. A unit offset over a backdrop-aware input is an
    // operator that resolves against what is underneath at draw time, which is why
    // the selector below can be as coarse as it is.
    // `flags` travels in the row's index signature rather than as a named field,
    // because the reader publishes the filter's own declared keys verbatim and
    // narrowing them here would be this test deciding what a filter may declare.
    const flags = (r: (typeof labels)[number]) => r.flags as Record<string, unknown>;
    expect(labels.every((r) => flags(r)["inputBackdropAware"] === 1)).toBe(true);
    expect(labels.every((r) => flags(r)["inputClamp"] === 1)).toBe(true);
    expect(labels.every((r) => flags(r)["inputClampPreserveHue"] === null)).toBe(true);
    expect(new Set(labels.map((r) => r.input))).toEqual(new Set(["backdrop-beneath"]));
  });

  it("selects the label's operator by the colour scheme, and by nothing else the probe moved", () => {
    // The probe was built to refute this. It holds a dark-solid span ladder at
    // 44 / 48 / 64 / 80 / 96 — the interval §5.133 §4 says the corpus holds no cell
    // in, and the one where its two candidate selector laws disagree — crossed with
    // seven backdrops from linear 0.0033 to 0.891. If either span or tone entered
    // the label's selector, a scheme would carry more than one operator. Neither
    // does: each scheme carries exactly one across all of it.
    for (const scheme of ["light", "dark"]) {
      const rows = inScheme(labels, scheme);
      expect(rows.length, scheme).toBe(12);
      expect(new Set(rows.map((r) => r.operatorId)).size, scheme).toBe(1);
      expect([...new Set(rows.map((r) => r.surface.spanFromDump))].sort((a, b) => (a ?? 0) - (b ?? 0)))
        .toEqual([44, 48, 64, 80, 96]);
      expect(new Set(rows.map((r) => r.background)).size, scheme).toBe(7);
    }
    expect(new Set(labels.map((r) => r.operatorId)).size).toBe(2);
  });

  it("leaves the label's operator alone when the surface carries an author tint", () => {
    // §5.133 §9: the author tint does not enter the highlight operator, and what
    // W27e publishes for a tinted control's label "cannot cite Apple for it". It
    // can now: the tinted cell's label carries its untinted twin's operator.
    for (const scheme of ["light", "dark"]) {
      const at = (scene: string) => inScheme(labels, scheme).find((r) => r.scene === scene);
      const tinted = at("photo__capsule-button__rest-label-tint-orange");
      const plain = at("photo__capsule-button__rest-label");
      expect(tinted?.operatorId, scheme).toBe(plain?.operatorId);
    }
  });
});

describe("W27e's labelled probe: what it says about the SURFACE operator", () => {
  it("carries one highlight operator per scheme over the whole ladder", () => {
    // Read beside the label because it is the same 50 trees, and because it moves
    // §5.133 §4's premise. G0's corpus is 57 of 57 light at 1x, and two of its 58
    // highlight occurrences switch to the high-gain operator. Here, at 2x, NOTHING
    // switches inside a scheme — including the two scene ids that switch in G0 —
    // and the dark scheme carries the high-gain operator on every cell, over
    // backdrops up to linear 0.891 where no tone-based rule would put it.
    expect(highlights.length).toBe(50);
    for (const scheme of ["light", "dark"]) {
      const rows = inScheme(highlights, scheme);
      expect(rows.length, scheme).toBe(25);
      expect(new Set(rows.map((r) => r.operatorId)).size, scheme).toBe(1);
    }
  });

  it("reads both of G0's foreground operators, one per scheme, to the coefficient", () => {
    // The same two operators §5.133 §3 tabulates, so this is the same mechanism
    // seen from a second configuration rather than a third operator. Light carries
    // the default (m 1.5, a 0.1, b 0.9); dark carries the one G0 named "dark-glass"
    // (m 3.0, a 1.35, b 0.15) — on every cell.
    const at = (scheme: string) => decompose((inScheme(highlights, scheme)[0] as
      { matrix: readonly number[] }).matrix);
    const light = at("light");
    expect(light.chromaGain).toBeCloseTo(1.5, 4);
    expect(light.levelGain[1]).toBeCloseTo(0.1, 4);
    expect(light.offset.every((b) => Math.abs(b - 0.9) < 1e-6)).toBe(true);
    const dark = at("dark");
    expect(dark.chromaGain).toBeCloseTo(3, 4);
    expect(dark.levelGain[1]).toBeCloseTo(1.35, 4);
    expect(dark.offset.every((b) => Math.abs(b - 0.15) < 1e-6)).toBe(true);
  });

  it("refutes both of §5.133 §8's candidate selectors on the cells they disagree about", () => {
    // Both candidates predict the high-gain operator on light `dark-solid` at span
    // 44: vitrea's own predicate reads exactly 1.0 there, and Apple's `tracksLuma`
    // is 1. At 2x, in light, the cell carries the DEFAULT operator.
    //
    // WHAT THAT DOES NOT SETTLE. Two axes differ between the corpora, not one:
    // G0 is 1x through a KEY window, this run is 2x through a NON-KEY one (every
    // G0 dump records `isKeyWindow: true`; all 50 here record false). So "the
    // selector depends on scale" and "§5.133's selector holds in the active pose
    // and the recede collapses it to one operator per scheme" fit these rows
    // equally well — and the second is the variable this wave exists to measure.
    // What IS settled is that neither candidate law is the whole selector under
    // every pose and scale, which is what W27e G1 would otherwise have been
    // fitted on. The 1x re-run has to take BOTH poses to separate them.
    const light = inScheme(highlights, "light");
    const switching = light.filter((r) => r.scene === "dark-solid__capsule-button__rest"
      || r.scene === "impulse__capsule-button__rest");
    expect(switching.length).toBe(2);
    expect(switching.every((r) => r.vitrea.backdropToneAdaptation === 1)).toBe(true);
    expect(switching.every((r) => r.surface.tracksLuma === 1)).toBe(true);
    expect(new Set(switching.map((r) => r.operatorId)).size).toBe(1);
    expect(switching[0]?.operatorId).toBe(light[0]?.operatorId);
    // And the dark scheme puts the high-gain operator over light-solid, where both
    // candidates predict the default: the predicate reads 0 and `tracksLuma` alone
    // cannot select an operator without a tone term.
    const lightSolidDark = inScheme(highlights, "dark")
      .find((r) => r.scene === "light-solid__capsule-button__rest");
    expect(lightSolidDark?.vitrea.backdropToneAdaptation).toBe(0);
    expect(lightSolidDark?.operatorId).toBe(inScheme(highlights, "dark")[0]?.operatorId);
  });

  it("reads the surface operator off a layer that draws nothing in this pose", () => {
    // W27e G1's reading, and the reason the refutation above does not by itself
    // choose between its two explanations. The layer the surface operator sits on
    // is the `CASDFKeyFillHighlightEffect` layer, and across this corpus its own
    // `opacity` is 0 on every cell while G0's is 1 on every cell. §5.128 records
    // that the bright rim goes to zero in the receded pose in every profile at
    // both scales, and every dump here is non-key. A matrix on a layer that draws
    // nothing has no pixel consequence, so "one operator per scheme" may be the
    // configuration of a dormant layer rather than a selector at all — which is a
    // third reading beside scale dependence and a collapsing selector, and the
    // 1x both-pose pass has to separate all three.
    expect(new Set(highlights.map((r) => r.layerOpacity))).toEqual(new Set([0]));
    expect(new Set(reading.rows.filter((r) => r.role === "surface-highlight")
      .map((r) => r.layerOpacity))).toEqual(new Set([1]));
    // The label's own layer is fully opaque in both schemes, so nothing about the
    // label's reading rides on this.
    expect(new Set(labels.map((r) => r.layerOpacity))).toEqual(new Set([1]));
  });
});

/**
 * W27e G1 / claims §5.137: the label operator, pinned to the dumps it came from.
 *
 * The operator needed no coefficient fit — §5.136 §4 read Apple's own numbers
 * with zero residual — so what has to be held is that the constants the evaluator
 * carries are still the corpus's own, and that the arithmetic around them is the
 * arithmetic `inputClamp` = 1 describes. Both are checked against the committed
 * dumps rather than against a transcription.
 */
describe("W27e G1: the label operator as a function", () => {
  it("carries the corpus's own matrices, float for float", () => {
    // Not a transcription check: the expected value is read out of the probe
    // corpus on this run, so an edit to either side fails.
    for (const [scheme, operator] of Object.entries(LABEL_OPERATOR_BY_SCHEME)) {
      const fromDumps = inScheme(labels, scheme);
      expect(fromDumps.length).toBe(12);
      for (const row of fromDumps) expect(row.matrix).toEqual(LABEL_MATRICES[operator]);
    }
  });

  it("selects the operator on the material's own composite level, not on a scheme", () => {
    // Apple selects by colour scheme; vitrea cannot, because a surface's own level
    // does not have to follow the document's. The crossover is a required argument
    // for the same reason a copy of it is not kept in the evaluator: it belongs to
    // the runtime and a second copy would go on agreeing with a number that moved.
    const crossover = CSS_TIER_MAPPING.foregroundCrossover;
    expect(labelOperatorFor(0.9, crossover)).toBe("darkening");
    expect(labelOperatorFor(crossover, crossover)).toBe("darkening");
    expect(labelOperatorFor(0.2, crossover)).toBe("lightening");
  });

  it("saturates: every in-gamut ink lands on black or on white", () => {
    // The whole of §5.137 §2 turns on this. A unit offset against a [0, 1] clamp
    // leaves nothing of the input colour, which is why the operator has no
    // backdrop term for the CSS tier's fold to lose.
    for (let v = 0; v <= 1.0001; v += 1 / 32) {
      const ink = { rgb: [v, v / 2, 1 - v] as const, alpha: 1 };
      expect(labelInk("darkening", ink).rgb).toEqual([0, 0, 0]);
      expect(labelInk("lightening", ink).rgb).toEqual([1, 1, 1]);
    }
  });

  it("passes alpha through in light and pulls it back by 0.95 in dark", () => {
    // The one coefficient that is not a saturation, and the one that tells the two
    // readings of `inputBackdropAware` apart: under the plus-lighter reading it is
    // inert, because that composite saturates to white whatever the alpha.
    for (const alpha of [1, 0.85, 0.6, 0.3, 0.18, 0]) {
      expect(labelInk("darkening", { rgb: [0, 0, 0], alpha }).alpha).toBe(alpha);
      expect(labelInk("lightening", { rgb: [1, 1, 1], alpha }).alpha)
        .toBeCloseTo(alpha * 0.949999988079071, 12);
    }
  });

  it("applies a CAColorMatrix as four rows of five columns, clamped", () => {
    // The convention is the module header's, and it is easy to get backwards: this
    // is the one assertion that would fail on a transposed matrix.
    const m = [0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 0.75, 0, 0, 0, 1, 0];
    const out = applyColorMatrix({ rgb: [1, 1, 1], alpha: 0.5 }, m);
    expect(out.rgb).toEqual([0.25, 0.5, 0.75]);
    expect(out.alpha).toBe(0.5);
    expect(() => applyColorMatrix({ rgb: [0, 0, 0], alpha: 1 }, [1, 2, 3]))
      .toThrow(/twenty floats/);
  });

  it("agrees with what Chromium composited, inside the tolerance declared before the run", () => {
    // The browser proof, read back from its own evidence rather than restated.
    // What it bounds is the analytic operator against the browser's composite of
    // it — never vitrea against macOS, for which no native label fixture exists
    // and, under the no-text fixture rule, none can.
    expect(verdict.declaredTolerance.bound).toBe(1);
    expect(verdict.A_passes).toBe(true);
    expect(verdict.A_measuredTolerance).toBeLessThanOrEqual(1);
    expect(verdict.B_foldAgainstDeclaredPath.maxAbsDiffCodeValues).toBeLessThanOrEqual(1);
    // And Chromium cannot express the alternative reading's light-scheme blend at
    // all, which is a fact about the web rather than about this run.
    expect(verdict.C_alternativeReading.blendSupport["mix-blend-mode: plus-darker"]).toBe(false);
  });
});

/**
 * W27e G2 / claims §5.138: the 1x both-pose corpus, the run Decision Log 15 (c)
 * held the selector decision behind.
 *
 * A third corpus, never merged with either of the two above: 150 dumps, the same
 * 25 probe scenes per scheme at 1x through three launches, holding scale,
 * accessibility, settle and scene set fixed so the window state is the only axis.
 * The pins below are the ones §5.138 reasons from — the arm counts, the pose
 * tallies, and the two laws the corpus reads — and they are taken from the
 * committed dumps rather than from the tables written beside them.
 */
const probe1x = read(PROBE_1X_DUMP_DIRS, null);
const arm1x = (row: { dump: string }) => armOf(PROBE_1X_ARMS, row.dump);
const pose1x = (row: { dump: string; colorScheme: string; isKeyWindow: boolean }) =>
  `${arm1x(row)}/${row.colorScheme}/${row.isKeyWindow ? "key" : "non-key"}`;
const highlights1x = probe1x.rows.filter((r) => r.role === "surface-highlight");
const labels1x = probe1x.rows.filter((r) => r.role === "content-label");
const tints1x = probe1x.rows.filter((r) => r.role === "author-tint");
/** The body's own adapted state, which the reader publishes in the row's index signature. */
const faceIsDark = (row: { body: unknown }) =>
  (row.body as Record<string, unknown>)["faceFillIsDark"] === true;
const margin = (row: { surface: unknown }) =>
  (row.surface as Record<string, unknown>)["marginWidth"] as number;

describe("W27e G2's 1x both-pose corpus: the arms and the poses", () => {
  it("reads 25 dumps in each of the six arm-and-scheme directories, and nothing else", () => {
    expect(probe1x.dumps.length).toBe(150);
    expect(new Set(probe1x.dumps.map((d) => d.path)).size).toBe(150);
    for (const arm of Object.keys(PROBE_1X_ARMS)) {
      for (const scheme of ["light", "dark"]) {
        expect(probe1x.dumps.filter((d) => armOf(PROBE_1X_ARMS, d.path) === arm
          && d.colorScheme === scheme).length, `${arm}/${scheme}`).toBe(25);
      }
    }
    // Every dump carries a matrix, so no cell is invisible to the row-level tallies.
    expect(new Set(probe1x.rows.map((r) => r.dump)).size).toBe(150);
    expect(probe1x.rows.filter((r) => r.role === "unclassified")).toEqual([]);
  });

  it("pins the corpus's IDENTITY, not only its shape", () => {
    // Every assertion around this one reads a count or an invariant, so a dump
    // that changed while keeping them — a label's text, canvas metadata, a tint
    // coefficient nothing here asserts — would leave the suite green while the
    // committed evidence claims §5.138 reasons from had moved. The reader already
    // hashes every dump it reads; this is one digest over the sorted
    // `path sha256` pairs, so any byte under the corpus fails here. A deliberate
    // change to the corpus comes to this line and says so.
    const manifest = probe1x.dumps.map((d) => `${d.path} ${d.sha256}`).sort().join("\n");
    expect(createHash("sha256").update(manifest).digest("hex"))
      .toBe("0ab83eb52f1385e4c35befe41e959b823e424f712dadb6446479cb6a91ff16d9");
  });

  it("refuses a dump path that belongs to none of the declared arms", () => {
    expect(() => armOf(PROBE_1X_ARMS, "packages/calibration/results/elsewhere/x.json"))
      .toThrow(/none of the declared arms/);
  });

  it("holds everything but the window state fixed, which is what makes the pose readable", () => {
    expect(new Set(probe1x.rows.map((r) => r.scale))).toEqual(new Set([1]));
    expect(new Set(probe1x.rows.map((r) => r.a11y))).toEqual(new Set(["standard"]));
    expect(new Set(probe1x.rows.map((r) => r.settleSeconds))).toEqual(new Set([8]));
    expect(new Set(probe1x.rows.map((r) => r.os)))
      .toEqual(new Set(["Version 26.5.2 (Build 25F84)"]));
  });

  it("records the pose tallies the corpus index states, per dump and not per run", () => {
    // `active/light` lost key after its ninth scene: 9 key and 16 not, in ONE arm,
    // which is the internal proof that `isKeyWindow` is sampled per dump. The
    // tallies are pinned because every reading in §5.138 partitions on them.
    const tally = (arm: string, scheme: string, key: boolean) => probe1x.dumps.filter((d) =>
      armOf(PROBE_1X_ARMS, d.path) === arm && d.colorScheme === scheme
      && d.isKeyWindow === key).length;
    expect([tally("active", "light", true), tally("active", "light", false)]).toEqual([9, 16]);
    expect([tally("active", "dark", true), tally("active", "dark", false)]).toEqual([25, 0]);
    expect([tally("policy-only", "light", true), tally("policy-only", "dark", true)])
      .toEqual([25, 25]);
    expect([tally("recede", "light", false), tally("recede", "dark", false)]).toEqual([25, 25]);
    expect(probe1x.dumps.filter((d) => d.isKeyWindow).length).toBe(84);
  });

  it("carries the two new pose fields on the recede arm only, and never invents them", () => {
    // A dump taken before the harness gained the fields states nothing about the
    // application's activation; the reader omits the keys rather than writing false.
    const recede = probe1x.rows.filter((r) => arm1x(r) === "recede");
    expect(recede.length).toBeGreaterThan(0);
    expect(recede.every((r) => r.appIsActive === false)).toBe(true);
    expect(recede.every((r) => r.activationPolicy === "accessory")).toBe(true);
    expect(probe1x.rows.filter((r) => arm1x(r) !== "recede")
      .every((r) => r.appIsActive === undefined && r.activationPolicy === undefined)).toBe(true);
  });
});

describe("W27e G2: what the pose moves, and what it does not", () => {
  it("switches the highlight layer off with KEY, not with the application's activation", () => {
    // §5.128's receded bright rim, in Apple's configuration. The 66 non-key dumps
    // are the 50 of the accessory `recede` arm AND the 16 of `active/light` that
    // lost key while the application stayed active — indistinguishable here.
    expect(highlights1x.length).toBe(150);
    expect(new Set(highlights1x.filter((r) => r.isKeyWindow).map((r) => r.layerOpacity)))
      .toEqual(new Set([1]));
    expect(new Set(highlights1x.filter((r) => !r.isKeyWindow).map((r) => r.layerOpacity)))
      .toEqual(new Set([0]));
    expect(highlights1x.filter((r) => !r.isKeyWindow).length).toBe(66);
    // The backdrop layer's own margin collapses with it, and the label's layer
    // does not: the label goes on drawing in the recede.
    expect(new Set(highlights1x.filter((r) => !r.isKeyWindow).map(margin))).toEqual(new Set([0]));
    expect(highlights1x.filter((r) => r.isKeyWindow).every((r) => margin(r) > 0)).toBe(true);
    expect(new Set(labels1x.map((r) => r.layerOpacity))).toEqual(new Set([1]));
  });

  it("keeps BOTH surface operators in both schemes and in every window state", () => {
    // This is the refutation of "one operator per scheme", which the 2x corpus
    // read and §5.136 §5 could not attribute to the scale or to the pose. At 1x
    // neither pose is flat: the partition survives the recede.
    for (const group of [...new Set(highlights1x.map(pose1x))]) {
      const rows = highlights1x.filter((r) => pose1x(r) === group);
      expect(new Set(rows.map((r) => r.operatorId)).size, group).toBe(2);
    }
    expect(new Set(highlights1x.map(pose1x)).size).toBe(7);
  });

  it("agrees on the operator between the third window state and the recede, 16 of 16", () => {
    // `active/light`'s 16 non-key dumps are the recede reached by losing key
    // alone, under the regular policy with the application still active.
    const third = highlights1x.filter((r) => pose1x(r) === "active/light/non-key");
    const recede = highlights1x.filter((r) => pose1x(r) === "recede/light/non-key");
    expect(third.length).toBe(16);
    expect(third.every((r) => recede.find((x) => x.scene === r.scene)?.operatorId
      === r.operatorId)).toBe(true);
    expect(new Set(third.map((r) => r.layerOpacity))).toEqual(new Set([0]));
    expect(new Set(third.map(margin))).toEqual(new Set([0]));
  });

  it("names the three cells whose operator is not unanimous across the window states", () => {
    // Two of the three put two arms of the SAME pose on opposite sides, so none of
    // them is evidence of a pose effect — they bound how tightly any selector law
    // can be declared, and §5.138 §7 carries them as the gap.
    const split = [...new Set(highlights1x.map((r) => `${r.colorScheme} ${r.scene}`))]
      .filter((key) => new Set(highlights1x
        .filter((r) => `${r.colorScheme} ${r.scene}` === key).map((r) => r.operatorId)).size > 1);
    expect(split.sort()).toEqual([
      "dark light-solid__capsule-button__rest",
      "light dark-solid__capsule-button__rest",
      "light dark-solid__rrect-48__rest-label",
    ]);
  });
});

describe("W27e G2: the operator is the glass's own adapted state, read out", () => {
  it("puts the high-gain operator on exactly the surfaces whose body has adapted", () => {
    // 150 of 150 here, on both of the body's own keys, in three window states and
    // two schemes. §5.133 §4 saw this on two cells and called it agreement.
    const high = [...new Set(highlights1x.map((r) => r.operatorId))]
      .find((id) => Math.abs((highlights1x.find((r) => r.operatorId === id)
        ?.matrix[4] as number) - 0.15) < 1e-6);
    expect(high).toBeDefined();
    for (const row of highlights1x) {
      expect((row.operatorId === high), `${pose1x(row)} ${row.scene}`).toBe(faceIsDark(row));
      expect((row.operatorId === high), `${pose1x(row)} ${row.scene}`)
        .toBe((row.body as Record<string, unknown>)["shadowFill"] === null);
    }
    // And the same law holds on the two corpora read before this one.
    for (const corpus of [reading.rows, probe.rows]) {
      const rows = corpus.filter((r) => r.role === "surface-highlight");
      const id = [...new Set(rows.map((r) => r.operatorId))]
        .find((x) => Math.abs((rows.find((r) => r.operatorId === x)?.matrix[4] as number)
          - 0.15) < 1e-6);
      for (const row of rows) expect(row.operatorId === id).toBe(faceIsDark(row));
    }
  });

  it("selects the LABEL operator on the same bit, which is not the colour scheme", () => {
    // §5.136 §4 read the label's selector as the colour scheme, on a corpus where
    // no surface adapted so scheme and material state coincided. At 1x the light
    // scheme carries both label matrices and so does the dark one, and on 72 of 72
    // the lightening matrix sits exactly where the body's face fill is black.
    expect(labels1x.length).toBe(72);
    for (const row of labels1x) {
      const surface = highlights1x.find((r) => r.dump === row.dump);
      expect(surface, row.dump).toBeDefined();
      const lightening = (row.matrix[4] as number) === 1;
      expect(lightening, `${pose1x(row)} ${row.scene}`).toBe(faceIsDark(surface!));
    }
    for (const scheme of ["light", "dark"]) {
      expect(new Set(labels1x.filter((r) => r.colorScheme === scheme)
        .map((r) => r.operatorId)).size, scheme).toBe(2);
    }
  });

  it("leaves the two label matrices exactly where §5.136 §4 read them", () => {
    // The pair did not move; only its selector did. Compared to the evaluator's
    // own constants, so an edit to either side fails.
    const distinct = [...new Set(labels1x.map((r) => JSON.stringify(r.matrix)))]
      .map((m) => JSON.parse(m) as number[]);
    expect(distinct.length).toBe(2);
    expect(distinct.some((m) => JSON.stringify(m)
      === JSON.stringify(LABEL_MATRICES.darkening))).toBe(true);
    expect(distinct.some((m) => JSON.stringify(m)
      === JSON.stringify(LABEL_MATRICES.lightening))).toBe(true);
    const flags = (r: (typeof labels1x)[number]) => r.flags as Record<string, unknown>;
    expect(labels1x.every((r) => flags(r)["inputBackdropAware"] === 1
      && flags(r)["inputClamp"] === 1 && flags(r)["inputClampPreserveHue"] === null)).toBe(true);
  });

  it("still installs nothing over a label whose colour the author named, in every arm", () => {
    const hot = probe1x.dumps.filter((d) => d.scene.endsWith("label-hot"));
    expect(hot.length).toBe(6);
    expect(hot.every((d) => d.labelLayers === 1 && d.labelLayersWithOperator === 0)).toBe(true);
    expect(hot.every((d) => d.declaredLabel?.srgb != null)).toBe(true);
  });

  it("strips the author tint's hue in the recede and keeps its layer drawing", () => {
    // §5.130 measured that an author tint loses its hue entirely in the receded
    // pose while its darkening stays. Here it is in Apple's configuration: the
    // key pose carries the rank-one colorize W12 §5 read, and the non-key pose
    // carries an achromatic level map — on a layer that is still at opacity 1.
    expect(tints1x.length).toBe(12);
    expect(new Set(tints1x.map((r) => r.layerOpacity))).toEqual(new Set([1]));
    for (const row of tints1x) {
      const d = decompose(row.matrix);
      if (row.isKeyWindow) {
        expect(Math.abs(d.chromaGain), row.dump).toBeLessThan(1e-5);
        expect(d.achromatic, row.dump).toBe(false);
      } else {
        expect(d.chromaGain, row.dump).toBeCloseTo(0.7, 4);
        expect(d.achromatic, row.dump).toBe(true);
        expect(Math.abs(Math.abs(d.offset[0] as number) - 0.1), row.dump).toBeLessThan(1e-6);
      }
    }
  });
});
