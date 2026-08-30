import { describe, expect, it } from "vitest";

import {
  classifyDifference,
  differenceSummary,
  resolveCell,
  type CaptureVariant,
  type VariantDifference,
} from "../src/plurality";

const W = 40;
const H = 30;

/** An opaque grey raster, the stand-in for one settled capture. */
function raster(level: number): Uint8Array {
  const data = new Uint8Array(W * H * 4);
  for (let p = 0; p < W * H; p += 1) {
    data[p * 4] = level;
    data[p * 4 + 1] = level;
    data[p * 4 + 2] = level;
    data[p * 4 + 3] = 255;
  }
  return data;
}

function withSpeckle(base: Uint8Array, pixels: readonly number[], delta: number): Uint8Array {
  const out = Uint8Array.from(base);
  for (const p of pixels) {
    for (let c = 0; c < 3; c += 1) out[p * 4 + c] = (out[p * 4 + c] ?? 0) + delta;
  }
  return out;
}

function withBlock(base: Uint8Array, x0: number, y0: number, w: number, h: number, delta: number): Uint8Array {
  const out = Uint8Array.from(base);
  for (let y = y0; y < y0 + h; y += 1) {
    for (let x = x0; x < x0 + w; x += 1) {
      const p = y * W + x;
      for (let c = 0; c < 3; c += 1) out[p * 4 + c] = (out[p * 4 + c] ?? 0) + delta;
    }
  }
  return out;
}

const variant = (sha: string, runs: string[], settled = true): CaptureVariant => ({
  sha256: sha,
  runs,
  settled,
});

describe("differenceSummary", () => {
  it("separates scattered speckle from a contiguous region by coherence", () => {
    const base = raster(120);
    // Pixels chosen far apart, so no two are 4-neighbours of each other.
    const speckle = differenceSummary(base, withSpeckle(base, [5, 200, 611, 900], 6), W, H);
    expect(speckle.changedPx).toBe(4);
    expect(speckle.coherence).toBe(0);

    const block = differenceSummary(base, withBlock(base, 8, 8, 10, 10, 6), W, H);
    expect(block.changedPx).toBe(100);
    expect(block.coherence).toBe(1);
  });

  it("reports the worst channel step, not an average", () => {
    const base = raster(120);
    const d = differenceSummary(base, withBlock(base, 0, 0, 2, 2, 40), W, H);
    expect(d.maxDelta).toBe(40);
    expect(d.changedPx).toBe(4);
  });

  it("reads two identical rasters as no difference at all", () => {
    const d = differenceSummary(raster(77), raster(77), W, H);
    expect(d).toEqual({ maxDelta: 0, changedPx: 0, coherence: 0 });
  });

  it("refuses rasters that are not the size they claim", () => {
    expect(() => differenceSummary(raster(10), new Uint8Array(8), W, H)).toThrow(/cannot both be/);
  });
});

describe("classifyDifference", () => {
  it("calls one 8-bit code incidental however coherent it is", () => {
    // A whole region off by a single code is the raster rounding, not a second
    // appearance: there is no material state that lives inside one code.
    const d: VariantDifference = { maxDelta: 1, changedPx: 900, coherence: 1 };
    expect(classifyDifference(d)).toBe("incidental");
  });

  it("calls a large scattered difference incidental", () => {
    expect(classifyDifference({ maxDelta: 60, changedPx: 12, coherence: 0 })).toBe("incidental");
  });

  it("calls a large coherent difference structured", () => {
    expect(classifyDifference({ maxDelta: 32, changedPx: 4000, coherence: 0.97 })).toBe("structured");
  });
});

describe("resolveCell", () => {
  const base = raster(120);

  /** The caller's job in the CLI, done here over synthetic rasters. */
  const differ = (images: Record<string, Uint8Array>) =>
    (a: CaptureVariant, b: CaptureVariant): VariantDifference =>
      differenceSummary(images[a.sha256] as Uint8Array, images[b.sha256] as Uint8Array, W, H);

  it("passes a unanimous cell straight through", () => {
    const out = resolveCell([variant("aaa", ["E", "F", "G"])], differ({ aaa: base }));
    expect(out.kind).toBe("agreed");
  });

  it("still resolves a noisy cell by majority", () => {
    // The case the doctrine was built for: two runs agree, the third differs by
    // a few codes on four isolated pixels. That is a wrong answer scattered
    // around a right one, and the majority finds the right one.
    const noisy = withSpeckle(base, [5, 200, 611, 900], 6);
    const out = resolveCell(
      [variant("majority", ["E", "G"]), variant("noise", ["F"])],
      differ({ majority: base, noise: noisy }),
    );
    expect(out.kind).toBe("voted");
    if (out.kind !== "voted") return;
    expect(out.chosen.sha256).toBe("majority");
    expect(out.outvoted.map((v) => v.sha256)).toEqual(["noise"]);
  });

  it("refuses a two-state cell and names both variants rather than voting", () => {
    // The 2026-08-31 case: run E returns one settled appearance, F and G return
    // another, 32 codes apart over the body. A majority exists and must not be
    // used — the reference would then be whichever state won two runs.
    const brighter = withBlock(base, 10, 8, 20, 14, 32);
    const out = resolveCell(
      [variant("dim", ["F", "G"]), variant("bright", ["E"])],
      differ({ dim: base, bright: brighter }),
    );
    expect(out.kind).toBe("refused");
    if (out.kind !== "refused") return;
    expect(out.stateAmbiguous).toBe(true);
    expect(out.variants.map((v) => v.sha256).sort()).toEqual(["bright", "dim"]);
    expect(out.reason).toMatch(/two settled appearances|2 settled appearances/);
  });

  it("votes rather than refusing when the minority was not settled inside its own run", () => {
    // Same pixels, but the odd run out never stabilised. A reading the harness
    // itself would not stand behind is not evidence of a second state.
    const brighter = withBlock(base, 10, 8, 20, 14, 32);
    const out = resolveCell(
      [variant("dim", ["F", "G"]), variant("bright", ["E"], false)],
      differ({ dim: base, bright: brighter }),
    );
    expect(out.kind).toBe("voted");
  });

  it("refuses a three-way split with no plurality, without calling it a state", () => {
    const a = withSpeckle(base, [5], 4);
    const b = withSpeckle(base, [900], 4);
    const out = resolveCell(
      [variant("x", ["E"]), variant("y", ["F"]), variant("z", ["G"])],
      differ({ x: base, y: a, z: b }),
    );
    expect(out.kind).toBe("refused");
    if (out.kind !== "refused") return;
    expect(out.stateAmbiguous).toBe(false);
    expect(out.reason).toMatch(/no variant holds a plurality/);
  });

  it("refuses on structure even when the structured variant is the one that won", () => {
    // Two settled states split 2-1 the other way. The count must not decide
    // which of them is real, so the answer is the same refusal either way.
    const brighter = withBlock(base, 10, 8, 20, 14, 32);
    const out = resolveCell(
      [variant("bright", ["E", "F"]), variant("dim", ["G"])],
      differ({ bright: brighter, dim: base }),
    );
    expect(out.kind).toBe("refused");
    if (out.kind !== "refused") return;
    expect(out.stateAmbiguous).toBe(true);
  });
});
