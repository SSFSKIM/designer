import { describe, expect, it } from "vitest";
import {
  LUMA_REC709,
  OPERATOR_TOLERANCE,
  PROBE_DUMP_DIRS,
  decompose,
  read,
} from "../scripts/vibrancy";

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
});
