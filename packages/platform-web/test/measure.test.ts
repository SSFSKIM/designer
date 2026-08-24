import { describe, expect, it } from "vitest";

import { createLayoutReadMeter, readComputedStyle, readRect, readViewport } from "../src/measure";

describe("the layout-read meter", () => {
  it("starts at zero", () => {
    const meter = createLayoutReadMeter();

    expect(meter.total).toBe(0);
    expect(meter.counts).toEqual({ rects: 0, styles: 0, viewport: 0 });
  });

  it("counts a rect read", () => {
    const meter = createLayoutReadMeter();
    readRect(meter, document.createElement("div"));

    expect(meter.counts.rects).toBe(1);
    expect(meter.total).toBe(1);
  });

  it("counts one style read per call, not one per property", () => {
    const meter = createLayoutReadMeter();
    const element = document.createElement("div");
    const style = readComputedStyle(meter, element);
    style.getPropertyValue("opacity");
    style.getPropertyValue("filter");

    expect(meter.counts.styles).toBe(1);
  });

  it("counts a viewport read", () => {
    const meter = createLayoutReadMeter();
    readViewport(meter);

    expect(meter.counts.viewport).toBe(1);
    expect(meter.total).toBe(1);
  });

  it("resets", () => {
    const meter = createLayoutReadMeter();
    readRect(meter, document.createElement("div"));
    meter.reset();

    expect(meter.total).toBe(0);
  });

  it("returns the rect as core's plain Rect, not a live DOMRect", () => {
    const meter = createLayoutReadMeter();
    const rect = readRect(meter, document.createElement("div"));

    expect(Object.keys(rect).sort()).toEqual(["height", "width", "x", "y"]);
  });
});
