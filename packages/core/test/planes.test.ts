import { describe, expect, it } from "vitest";

import { GLASS_PLANES, compareZSlot, rectsOverlap, type Rect, type ZSlot } from "../src/index";

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
