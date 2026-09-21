/**
 * W31 G2 — the readback guard's predicate, on both sides (claims §5.163 §3).
 *
 * The guard refuses a raster with an ENCLOSED region of zero alpha inside drawn
 * material. Its value depends entirely on being narrow: a guard that also fired
 * on a legitimately translucent interior, or on a surface at presence 0, would
 * be switched off within a wave and would then be catching nothing.
 *
 * So the cases come in pairs. Each fires-on case has a does-not-fire twin that
 * differs by the one property the predicate turns on — zero against low, and
 * enclosed against reaching the border — and the twins are the reason to trust
 * the guard when it is silent.
 *
 * The `@gpu` half is in `e2e/gpu/w31-readback-guard.spec.ts`: that the guard is
 * WIRED into the live readback, and that it says nothing across the scenes the
 * suite renders. This half is the predicate itself, and it needs no adapter.
 */

import { describe, expect, it } from "vitest";

import { alphaHoleRefusal, enclosedZeroAlphaRegions } from "../e2e/fixtures/alpha-holes";

const WIDTH = 32;
const HEIGHT = 24;

/** A raster whose every pixel carries `alpha`. */
const uniform = (alpha: number): { width: number; height: number; data: Uint8Array } => {
  const data = new Uint8Array(WIDTH * HEIGHT * 4);
  for (let i = 0; i < WIDTH * HEIGHT; i += 1) {
    data[i * 4 + 3] = alpha;
    data[i * 4] = 128;
  }
  return { width: WIDTH, height: HEIGHT, data };
};

/** Set a rectangle's alpha, in pixels. */
const block = (
  raster: { width: number; height: number; data: Uint8Array },
  x0: number,
  y0: number,
  w: number,
  h: number,
  alpha: number,
): void => {
  for (let y = y0; y < y0 + h; y += 1) {
    for (let x = x0; x < x0 + w; x += 1) raster.data[(y * raster.width + x) * 4 + 3] = alpha;
  }
};

describe("the enclosed-zero-alpha predicate (claims §5.163 §3)", () => {
  it("fires on a hole inside drawn material — §5.159b's own signature", () => {
    // A 44 px capsule with a strip through it is what W30 G3 shipped and G3b
    // diagnosed; this is that, in miniature.
    const raster = uniform(200);
    block(raster, 10, 8, 6, 4, 0);
    const holes = enclosedZeroAlphaRegions(raster);
    expect(holes).toHaveLength(1);
    expect(holes[0]?.area).toBe(24);
    expect(holes[0]).toMatchObject({ x0: 10, y0: 8, x1: 15, y1: 11 });
    expect(alphaHoleRefusal(raster, "test")).toContain("enclosed region(s) of ZERO alpha");
  });

  it("STANDS DOWN on a rounding event in the outer shadow's tail — measured, not supposed", () => {
    /*
     * The guard's first form had no silhouette clause and fired here, on two of
     * `page-material.spec.ts`'s six scalar cases (W31 G2; claims §5.163 §3).
     * Reproduced from that reading: 170 CSS px out from the surfaces, the
     * composited shadow alpha is 1 and 2 of 255 and one pixel of it rounds to 0
     * with 1s and 2s all round it.
     *
     * Enclosed by *something*, walled in by nothing drawn. Refusing it would
     * have made the guard a source of noise on a scene nobody had changed, which
     * is how a guard gets switched off.
     */
    const raster = uniform(0);
    block(raster, 4, 3, 10, 8, 255); // the material
    block(raster, 16, 12, 12, 10, 1); // the shadow's tail, one and two codes
    block(raster, 20, 15, 4, 3, 2);
    block(raster, 22, 16, 1, 1, 0); // the pixel that rounded to zero
    expect(enclosedZeroAlphaRegions(raster)).toEqual([]);
    expect(alphaHoleRefusal(raster, "test")).toBeUndefined();

    // And the same pixel INSIDE the material is refused, which is the clause
    // doing work rather than switching the guard off.
    const inside = uniform(0);
    block(inside, 4, 3, 10, 8, 255);
    block(inside, 8, 6, 1, 1, 0);
    expect(enclosedZeroAlphaRegions(inside)).toHaveLength(1);
  });

  it("fires on a single enclosed pixel, because a NaN does not have to be large", () => {
    const raster = uniform(200);
    block(raster, 17, 13, 1, 1, 0);
    expect(enclosedZeroAlphaRegions(raster)).toHaveLength(1);
  });

  it("STANDS DOWN on a translucent interior — the unsampled layer path", () => {
    // `bodyAlpha = presentAlpha` writes an interior that is deliberately faint,
    // sometimes a single code over a large area. The predicate reads alpha
    // EXACTLY zero and never a threshold, which is the whole of this stand-down.
    const raster = uniform(255);
    block(raster, 6, 4, 20, 16, 1);
    expect(enclosedZeroAlphaRegions(raster)).toEqual([]);
    expect(alphaHoleRefusal(raster, "test")).toBeUndefined();
  });

  it("STANDS DOWN at presence 0, where the whole surface and the page are zero", () => {
    // `dom_material_alpha` is legitimately 0 where the material is not there.
    // The surface's zero region then reaches the raster's border through the
    // transparent page around it, and reaching the border is not enclosure.
    const empty = uniform(0);
    expect(enclosedZeroAlphaRegions(empty)).toEqual([]);

    // The same, with a surface drawn beside the absent one rather than around
    // it: still connected to the border, still nothing to refuse.
    const beside = uniform(0);
    block(beside, 2, 2, 8, 8, 255);
    expect(enclosedZeroAlphaRegions(beside)).toEqual([]);
  });

  it("STANDS DOWN on a surface whose transparent exterior touches the border", () => {
    // The ordinary render: material in the middle, nothing around it.
    const raster = uniform(0);
    block(raster, 8, 6, 16, 12, 220);
    expect(alphaHoleRefusal(raster, "test")).toBeUndefined();
  });

  it("tells a hole apart from a notch open to the edge of the material", () => {
    // A bite taken out of a surface reaches the exterior and is not a hole; the
    // same bite one pixel in from the contour is. The pair is the enclosure
    // half of the predicate stated as a difference.
    const notched = uniform(0);
    block(notched, 8, 6, 16, 12, 220);
    block(notched, 8, 10, 5, 3, 0);
    expect(enclosedZeroAlphaRegions(notched)).toEqual([]);

    const holed = uniform(0);
    block(holed, 8, 6, 16, 12, 220);
    block(holed, 9, 10, 5, 3, 0);
    expect(enclosedZeroAlphaRegions(holed)).toHaveLength(1);
  });

  it("reports several holes, largest first, and counts them all", () => {
    const raster = uniform(200);
    block(raster, 4, 4, 2, 2, 0);
    block(raster, 20, 14, 5, 5, 0);
    const holes = enclosedZeroAlphaRegions(raster);
    expect(holes.map((hole) => hole.area)).toEqual([25, 4]);
    const refusal = alphaHoleRefusal(raster, "scene-x") ?? "";
    expect(refusal).toContain("scene-x");
    expect(refusal).toContain("2 enclosed region(s)");
    expect(refusal).toContain("29 px in all");
  });

  it("survives a raster that is one enormous zero region, without recursing", () => {
    // A recursive flood fill overflows the stack on a full-target region, and a
    // guard that crashes on a blank render is worse than one that is silent.
    const wide = { width: 900, height: 700, data: new Uint8Array(900 * 700 * 4) };
    expect(enclosedZeroAlphaRegions(wide)).toEqual([]);
  });

  it("says nothing about a raster with no pixels", () => {
    expect(enclosedZeroAlphaRegions({ width: 0, height: 0, data: new Uint8Array(0) })).toEqual([]);
  });
});
