import { describe, expect, it } from "vitest";

import {
  GLASS_PLANES,
  clipRect,
  compareZSlot,
  inflateRect,
  rectsOverlap,
  unionRect,
  type Rect,
  type ZSlot,
} from "../src/index";

const rect = (x: number, y: number, width: number, height: number): Rect => ({
  x,
  y,
  width,
  height,
});

describe("plane and z-slot model", () => {
  it("ships exactly the two v1 planes, base painting before overlay (X1)", () => {
    expect([...GLASS_PLANES]).toEqual(["base", "overlay"]);
  });

  it("orders z-slots by plane first, then by order within the plane", () => {
    const slots: ZSlot[] = [
      { plane: "overlay", order: 0 },
      { plane: "base", order: 5 },
      { plane: "base", order: 1 },
      { plane: "overlay", order: -2 },
    ];

    expect([...slots].sort(compareZSlot)).toEqual([
      { plane: "base", order: 1 },
      { plane: "base", order: 5 },
      { plane: "overlay", order: -2 },
      { plane: "overlay", order: 0 },
    ]);
  });
});

describe("rect overlap", () => {
  it("finds a genuine intersection", () => {
    expect(rectsOverlap(rect(0, 0, 10, 10), rect(5, 5, 10, 10))).toBe(true);
  });

  it("finds containment", () => {
    expect(rectsOverlap(rect(0, 0, 100, 100), rect(10, 10, 5, 5))).toBe(true);
  });

  it("does not count touching edges — adjacent surfaces are legal", () => {
    expect(rectsOverlap(rect(0, 0, 10, 10), rect(10, 0, 10, 10))).toBe(false);
    expect(rectsOverlap(rect(0, 0, 10, 10), rect(0, 10, 10, 10))).toBe(false);
  });

  it("does not count separated rects", () => {
    expect(rectsOverlap(rect(0, 0, 10, 10), rect(20, 20, 10, 10))).toBe(false);
  });

  it("does not count a degenerate rect — an unmeasured host cannot overlap anything", () => {
    expect(rectsOverlap(rect(0, 0, 0, 10), rect(0, 0, 10, 10))).toBe(false);
    expect(rectsOverlap(rect(0, 0, 10, 0), rect(0, 0, 10, 10))).toBe(false);
  });

  it("is symmetric", () => {
    const a = rect(0, 0, 10, 10);
    const b = rect(5, 5, 10, 10);
    expect(rectsOverlap(a, b)).toBe(rectsOverlap(b, a));
  });
});

describe("union and inflate — the proxy-box arithmetic", () => {
  it("unions two separated rects into the box that holds both", () => {
    expect(unionRect(rect(0, 0, 10, 10), rect(20, 30, 10, 10))).toEqual({
      x: 0,
      y: 0,
      width: 30,
      height: 40,
    });
  });

  it("leaves a contained rect making no difference", () => {
    const outer = rect(0, 0, 100, 100);
    expect(unionRect(outer, rect(10, 10, 5, 5))).toEqual(outer);
  });

  it("is symmetric", () => {
    const a = rect(0, 0, 10, 10);
    const b = rect(-5, 20, 10, 10);
    expect(unionRect(a, b)).toEqual(unionRect(b, a));
  });

  it("grows a rect on every side, so padding lands on the border box", () => {
    expect(inflateRect(rect(10, 10, 10, 10), 5)).toEqual({
      x: 5,
      y: 5,
      width: 20,
      height: 20,
    });
  });

  it("turns two adjacent rects into overlapping padded boxes — the double-filter case", () => {
    const left = inflateRect(rect(0, 0, 40, 40), 60);
    const right = inflateRect(rect(48, 0, 40, 40), 60);

    expect(rectsOverlap(left, right)).toBe(true);
    // The same pair stops overlapping once the gap exceeds both paddings.
    expect(rectsOverlap(left, inflateRect(rect(200, 0, 40, 40), 60))).toBe(false);
  });
});

/**
 * The clip chain's arithmetic (Decision Log #41(k)).
 *
 * A border box is measured unclipped, so it says where a surface is and not
 * what of it is visible. Everything downstream that reasons about area — the
 * overlap checks, the proxy's painted region — needs the second answer, and
 * this is the one place the two are reconciled.
 */
describe("clipping a rect to its ancestors' windows", () => {
  it("returns the rect untouched when nothing clips", () => {
    const box = rect(10, 10, 100, 40);

    // `undefined` and `[]` are the same statement, and the common case: a
    // surface with no clipping ancestor pays nothing for the feature.
    expect(clipRect(box, undefined)).toEqual(box);
    expect(clipRect(box, [])).toEqual(box);
  });

  it("crops to the window, edge by edge", () => {
    const box = rect(0, 0, 100, 100);

    expect(clipRect(box, [rect(20, 30, 100, 100)])).toEqual({
      x: 20,
      y: 30,
      width: 80,
      height: 70,
    });
  });

  it("intersects every window in the chain, not just the nearest", () => {
    const box = rect(0, 0, 100, 100);
    // Nested scrollers: the visible region is what survives both.
    const nested = clipRect(box, [rect(10, 0, 100, 100), rect(0, 0, 40, 100)]);

    expect(nested).toEqual({ x: 10, y: 0, width: 30, height: 100 });
  });

  /*
   * Zero rather than negative, and it matters downstream: `rectsOverlap`
   * refuses a zero-extent rect and the proxy geometry treats one as absent, so
   * "scrolled entirely out of view" needs no special case anywhere else.
   */
  it("collapses to zero extent when the windows exclude it entirely", () => {
    const outside = clipRect(rect(0, 0, 50, 50), [rect(200, 200, 50, 50)]);

    expect(outside.width).toBe(0);
    expect(outside.height).toBe(0);
    expect(rectsOverlap(outside, rect(200, 200, 50, 50))).toBe(false);
  });

  it("is idempotent, so folding a chain twice says the same thing", () => {
    const chain = [rect(10, 10, 60, 60)];
    const once = clipRect(rect(0, 0, 100, 100), chain);

    expect(clipRect(once, chain)).toEqual(once);
  });
});
