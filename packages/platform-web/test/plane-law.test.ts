import { describe, expect, it } from "vitest";

import {
  GLASS_PLANES,
  paintOrderIndex,
  PLANE_PAINT_ORDER,
  POINTER_TRANSPARENT_LAYERS,
} from "../src/index";

describe("plane law (X1)", () => {
  it("ships exactly the base and overlay planes", () => {
    expect(GLASS_PLANES).toEqual(["base", "overlay"]);
  });

  it("paints the glass body below the semantic host and the highlight above it", () => {
    expect(paintOrderIndex("optics-canvas")).toBeLessThan(paintOrderIndex("semantic-host"));
    expect(paintOrderIndex("highlight-canvas")).toBeGreaterThan(paintOrderIndex("semantic-host"));
    expect(PLANE_PAINT_ORDER[0]).toBe("backdrop-proxy");
  });

  it("leaves only the semantic host hit-testable", () => {
    expect(POINTER_TRANSPARENT_LAYERS).not.toContain("semantic-host");
    expect(POINTER_TRANSPARENT_LAYERS).toHaveLength(PLANE_PAINT_ORDER.length - 1);
  });
});
