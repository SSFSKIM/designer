import { describe, expect, it } from "vitest";
import { silhouetteBackdropTone } from "../src/backdrop-tone";

const pixels = (values: readonly (readonly [number, number, number])[]) =>
  new Uint8ClampedArray(values.flatMap((rgb) => [...rgb, 255]));
const grey = (values: readonly number[]) => pixels(values.map((v) => [v, v, v]));
const viewport = { width: 4, height: 4, devicePixelRatio: 1 };

describe("silhouette backdrop tone", () => {
  it("excludes rounded corners at pixel centres rather than averaging the source", () => {
    const data = grey([255, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0, 0, 255, 0, 0, 255]);
    const sample = silhouetteBackdropTone(data, 4, 4, {
      bounds: { x: 0, y: 0, width: 4, height: 4 }, radius: 2, viewport,
    });
    expect(sample?.encodedLuminance).toBe(0);
    expect(sample?.luminance).toBe(0);
    expect(sample?.footprint?.sampleCount).toBe(12);
  });

  it("maps source placement, scaling and edge clamping before averaging", () => {
    const sample = silhouetteBackdropTone(grey([0, 255]), 2, 1, {
      bounds: { x: 3, y: 1, width: 3, height: 1 }, radius: 0,
      viewport: { width: 8, height: 4, devicePixelRatio: 1 },
      placement: { x: 1, y: 1, width: 4, height: 1 },
    });
    // The three centres read 0.75, 1 and the clamped edge 1.
    expect(sample?.encodedLuminance).toBeCloseTo(2.75 / 3, 12);
  });

  it("cover-fits an unplaced source and samples the device-pixel grid", () => {
    const sample = silhouetteBackdropTone(grey([0, 64, 192, 255]), 4, 1, {
      bounds: { x: 0, y: 0, width: 1, height: 1 }, radius: 0,
      viewport: { width: 1, height: 1, devicePixelRatio: 2 },
    });
    expect(sample?.encodedLuminance).toBeCloseTo(128 / 255, 12);
  });

  it("decodes encoded Rec709 luma once, but retains local linear colour", () => {
    const sample = silhouetteBackdropTone(pixels([[255, 0, 0]]), 1, 1, {
      bounds: { x: 0, y: 0, width: 1, height: 1 }, radius: 0, viewport,
      placement: { x: 0, y: 0, width: 1, height: 1 },
    });
    expect(sample?.encodedLuminance).toBeCloseTo(0.2126, 12);
    expect(sample?.luminance).toBeCloseTo(((0.2126 + 0.055) / 1.055) ** 2.4, 12);
    expect(sample?.rgb).toEqual([1, 0, 0]);
    expect(sample?.linearLuminance).toBeCloseTo(0.2126, 12);
  });
});
