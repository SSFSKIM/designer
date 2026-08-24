import { describe, expect, it } from "vitest";

import { lerpShapeChannels, SHAPE_FAMILIES, type ShapeChannels } from "../src/index";

const button: ShapeChannels = {
  center: [40, 20],
  size: [80, 40],
  radii: [20, 20, 20, 20],
  smoothing: 0.6,
  thickness: 4,
};

const platter: ShapeChannels = {
  center: [120, 90],
  size: [240, 180],
  radii: [28, 28, 28, 28],
  smoothing: 0.6,
  thickness: 10,
};

describe("shape channels (X8)", () => {
  it("names the three v1 shape families", () => {
    expect(SHAPE_FAMILIES).toEqual([
      "fixed-rounded-rect",
      "capsule",
      "concentric-rounded-rect",
    ]);
  });

  it("interpolates every channel — a morph never crossfades", () => {
    expect(lerpShapeChannels(button, platter, 0)).toEqual(button);
    expect(lerpShapeChannels(button, platter, 1)).toEqual(platter);

    const mid = lerpShapeChannels(button, platter, 0.5);
    expect(mid.center).toEqual([80, 55]);
    expect(mid.size).toEqual([160, 110]);
    expect(mid.radii).toEqual([24, 24, 24, 24]);
    expect(mid.thickness).toBe(7);
  });
});
