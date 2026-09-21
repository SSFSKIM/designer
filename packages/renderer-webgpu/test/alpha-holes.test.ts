/**
 * W31 G2 — the readback guard's predicate, on both sides (claims §5.163 §3, and
 * §8 finding N1 for the per-region wall).
 *
 * The guard refuses a raster with an ENCLOSED region of zero alpha inside a
 * surface the scene DECLARED. Its value depends entirely on being narrow: a
 * guard that also fired on a legitimately translucent interior, or on a surface
 * that drew nothing, would be switched off within a wave and would then be
 * catching nothing.
 *
 * So the cases come in pairs. Each fires-on case has a does-not-fire twin that
 * differs by the one property the predicate turns on — zero against low,
 * enclosed against reaching the border, and inside a declared surface against
 * outside every one — and the twins are the reason to trust the guard when it is
 * silent.
 *
 * The `@gpu` half is in `e2e/gpu/w31-readback-guard.spec.ts`: that the guard is
 * WIRED into the live readback, and that it says nothing across the scenes the
 * suite renders. This half is the predicate itself, and it needs no adapter.
 */

import { describe, expect, it } from "vitest";

import {
  alphaHoleRefusal,
  enclosedZeroAlphaRegions,
  type DeclaredRegion,
} from "../e2e/fixtures/alpha-holes";

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

/** The same rectangle, as the declaration the guard reads it against. */
const declared = (x0: number, y0: number, w: number, h: number): DeclaredRegion => ({
  cx: x0 + w / 2,
  cy: y0 + h / 2,
  w,
  h,
  r: 0,
});

/** The whole raster declared, for the cases whose subject is not the boundary. */
const WHOLE = [declared(0, 0, WIDTH, HEIGHT)];

describe("the enclosed-zero-alpha predicate (claims §5.163 §3)", () => {
  it("fires on a hole inside drawn material — §5.159b's own signature", () => {
    // A 44 px capsule with a strip through it is what W30 G3 shipped and G3b
    // diagnosed; this is that, in miniature.
    const raster = uniform(200);
    block(raster, 10, 8, 6, 4, 0);
    const holes = enclosedZeroAlphaRegions(raster, WHOLE);
    expect(holes).toHaveLength(1);
    expect(holes[0]?.area).toBe(24);
    expect(holes[0]).toMatchObject({ x0: 10, y0: 8, x1: 15, y1: 11 });
    expect(alphaHoleRefusal(raster, "test", WHOLE)).toContain("enclosed region(s) of ZERO alpha");
  });

  it("STANDS DOWN on a rounding event in the outer shadow's tail — measured, not supposed", () => {
    /*
     * The guard's first form had no silhouette clause and fired here, on two of
     * `page-material.spec.ts`'s six scalar cases (W31 G2; claims §5.163 §3).
     * Reproduced from that reading: 170 CSS px out from the surfaces, the
     * composited shadow alpha is 1 and 2 of 255 and one pixel of it rounds to 0
     * with 1s and 2s all round it.
     *
     * Enclosed by *something*, and outside every surface the scene declared. It
     * is a rounding event in a facet, not a hole in a silhouette. Refusing it
     * would have made the guard a source of noise on a scene nobody had changed,
     * which is how a guard gets switched off.
     */
    const raster = uniform(0);
    block(raster, 4, 3, 10, 8, 255); // the material
    block(raster, 16, 12, 12, 10, 1); // the shadow's tail, one and two codes
    block(raster, 20, 15, 4, 3, 2);
    block(raster, 22, 16, 1, 1, 0); // the pixel that rounded to zero
    const surface = [declared(4, 3, 10, 8)];
    expect(enclosedZeroAlphaRegions(raster, surface)).toEqual([]);
    expect(alphaHoleRefusal(raster, "test", surface)).toBeUndefined();

    // And the same pixel INSIDE the material is refused, which is the clause
    // doing work rather than switching the guard off.
    const inside = uniform(0);
    block(inside, 4, 3, 10, 8, 255);
    block(inside, 8, 6, 1, 1, 0);
    expect(enclosedZeroAlphaRegions(inside, surface)).toHaveLength(1);
  });

  it("reads each declared surface's wall from its OWN peak, not the raster's", () => {
    /*
     * Finding N1, measured by the independent review of this gate and closed
     * here (claims §5.163 §8).
     *
     * The first shipped form took one cutoff for the whole raster — half of the
     * WHOLE raster's peak. With a bright surface at alpha 255 anywhere in the
     * frame the cutoff is 128, a dim surface at alpha 100 is then not a wall at
     * all, and a hole punched clean through the dim one reads as ZERO holes.
     * The review measured exactly this pair: the scene below read 0 and its
     * twin (the dim surface alone) read 1, so the guard's sensitivity on a
     * surface depended on what else was in the frame. `glass-over-glass`, the
     * scene the bed's own shadow residual sits on, is a two-surface scene.
     *
     * With the wall read per declared region both read 1, which is the property
     * the guard is supposed to have.
     */
    const withBright = uniform(0);
    block(withBright, 2, 2, 12, 12, 100); // the dim surface
    block(withBright, 5, 5, 4, 4, 0); // the hole through it
    block(withBright, 18, 8, 10, 10, 255); // the bright one, elsewhere
    const both = [declared(2, 2, 12, 12), declared(18, 8, 10, 10)];
    const holes = enclosedZeroAlphaRegions(withBright, both);
    expect(holes, "a hole inside a dim surface escaped past a bright one").toHaveLength(1);
    expect(holes[0]?.area).toBe(16);

    // The twin: the same dim surface, with nothing bright in the frame. The two
    // readings have to agree, and under the raster-wide wall they did not.
    const alone = uniform(0);
    block(alone, 2, 2, 12, 12, 100);
    block(alone, 5, 5, 4, 4, 0);
    const dim = [declared(2, 2, 12, 12)];
    expect(enclosedZeroAlphaRegions(alone, dim)).toHaveLength(1);
    expect(enclosedZeroAlphaRegions(alone, dim)[0]?.area).toBe(16);
  });

  it("fires on a single enclosed pixel, because a NaN does not have to be large", () => {
    const raster = uniform(200);
    block(raster, 17, 13, 1, 1, 0);
    expect(enclosedZeroAlphaRegions(raster, WHOLE)).toHaveLength(1);
  });

  it("STANDS DOWN on a translucent interior — the unsampled layer path", () => {
    // `bodyAlpha = presentAlpha` writes an interior that is deliberately faint,
    // sometimes a single code over a large area. The predicate reads alpha
    // EXACTLY zero and never a threshold, which is the whole of this stand-down.
    const raster = uniform(255);
    block(raster, 6, 4, 20, 16, 1);
    expect(enclosedZeroAlphaRegions(raster, WHOLE)).toEqual([]);
    expect(alphaHoleRefusal(raster, "test", WHOLE)).toBeUndefined();
  });

  it("STANDS DOWN at presence 0, where the declared surface drew nothing at all", () => {
    // `dom_material_alpha` is legitimately 0 where the material is not there.
    // A declared region whose own peak is zero has no silhouette for anything to
    // be a hole in, so it is not read — which is the per-region form of the
    // one-code floor, and exact rather than incidental.
    const empty = uniform(0);
    expect(enclosedZeroAlphaRegions(empty, WHOLE)).toEqual([]);

    // The same, with a surface drawn beside the absent one rather than around
    // it: the absent one is still not read, and the drawn one has no hole.
    const beside = uniform(0);
    block(beside, 2, 2, 8, 8, 255);
    expect(
      enclosedZeroAlphaRegions(beside, [declared(2, 2, 8, 8), declared(18, 10, 8, 8)]),
    ).toEqual([]);
  });

  it("STANDS DOWN on a surface whose transparent exterior touches the border", () => {
    // The ordinary render: material in the middle, nothing around it.
    const raster = uniform(0);
    block(raster, 8, 6, 16, 12, 220);
    expect(alphaHoleRefusal(raster, "test", [declared(8, 6, 16, 12)])).toBeUndefined();
  });

  it("tells a hole apart from a notch open to the edge of the material", () => {
    // A bite taken out of a surface reaches the exterior and is not a hole; the
    // same bite one pixel in from the contour is. The pair is the enclosure
    // half of the predicate stated as a difference.
    const surface = [declared(8, 6, 16, 12)];
    const notched = uniform(0);
    block(notched, 8, 6, 16, 12, 220);
    block(notched, 8, 10, 5, 3, 0);
    expect(enclosedZeroAlphaRegions(notched, surface)).toEqual([]);

    const holed = uniform(0);
    block(holed, 8, 6, 16, 12, 220);
    block(holed, 9, 10, 5, 3, 0);
    expect(enclosedZeroAlphaRegions(holed, surface)).toHaveLength(1);
  });

  it("reports several holes, largest first, and counts them all", () => {
    const raster = uniform(200);
    block(raster, 4, 4, 2, 2, 0);
    block(raster, 20, 14, 5, 5, 0);
    const holes = enclosedZeroAlphaRegions(raster, WHOLE);
    expect(holes.map((hole) => hole.area)).toEqual([25, 4]);
    const refusal = alphaHoleRefusal(raster, "scene-x", WHOLE) ?? "";
    expect(refusal).toContain("scene-x");
    expect(refusal).toContain("2 enclosed region(s)");
    expect(refusal).toContain("29 px in all");
  });

  it("counts a hole once when two declared surfaces overlap it", () => {
    // Two regions can share a cutoff or not, and either way the component is one
    // component. Reporting it twice would make the message's own arithmetic
    // ("N regions, M px in all") wrong.
    const raster = uniform(200);
    block(raster, 14, 10, 4, 4, 0);
    const overlapping = [declared(4, 4, 20, 16), declared(10, 6, 16, 14)];
    expect(enclosedZeroAlphaRegions(raster, overlapping)).toHaveLength(1);
  });

  it("survives a raster that is one enormous zero region, without recursing", () => {
    // A recursive flood fill overflows the stack on a full-target region, and a
    // guard that crashes on a blank render is worse than one that is silent.
    const wide = { width: 900, height: 700, data: new Uint8Array(900 * 700 * 4) };
    expect(enclosedZeroAlphaRegions(wide, [{ cx: 450, cy: 350, w: 900, h: 700, r: 0 }])).toEqual([]);
  });

  it("survives two enormous declared regions at one cutoff, and still finds the hole", () => {
    /*
     * The other stack overflow this module can have, and it is not the flood
     * fill: merging two masks at the same cutoff with `push(...mask)` is an
     * apply, and a 340 px caster's mask is 115,432 arguments. It took the
     * `@gpu` suite down on `w30-heavy-second-tap` the first time this predicate
     * ran there (review closure, 2026-09-21; claims §5.163 §8, finding N1).
     */
    const width = 900;
    const height = 700;
    const data = new Uint8Array(width * height * 4);
    for (let i = 0; i < width * height; i += 1) data[i * 4 + 3] = 200;
    for (let y = 300; y < 340; y += 1) {
      for (let x = 300; x < 340; x += 1) data[(y * width + x) * 4 + 3] = 0;
    }
    const raster = { width, height, data };
    const twoHalves = [
      { cx: 224.5, cy: 350, w: 449, h: 700, r: 0 },
      { cx: 674.5, cy: 350, w: 449, h: 700, r: 0 },
    ];
    const holes = enclosedZeroAlphaRegions(raster, twoHalves);
    expect(holes).toHaveLength(1);
    expect(holes[0]?.area).toBe(1600);
  });

  it("says nothing about a raster with no pixels, or a scene that declared none", () => {
    expect(enclosedZeroAlphaRegions({ width: 0, height: 0, data: new Uint8Array(0) }, [])).toEqual(
      [],
    );
    const raster = uniform(200);
    block(raster, 10, 8, 6, 4, 0);
    expect(enclosedZeroAlphaRegions(raster, [])).toEqual([]);
  });
});
