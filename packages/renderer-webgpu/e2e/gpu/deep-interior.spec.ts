/**
 * The deep interior of a large surface, beyond the outer shadow falloff's
 * reproduced overflow boundary.
 *
 * The Apple GPU failure is consistent with `tanh(t)` evaluated as
 * (e^2t − 1) / (e^2t + 1), giving inf / inf = NaN past 2t ≈ 88.7; this does
 * not establish how every Metal compiler implements it. The cubic reaches
 * that limit at normalized inward shadow distance ≈10.060966: 156.448 px
 * at sigma 15.55, measured from the shifted, spread shadow silhouette.
 * Subtracting spread 3.10 gives 153.348 px from the shifted glass contour.
 * With downward offset 7.95, straight-edge glass insets are about 153.348 px
 * left/right, 161.298 px top and 145.398 px bottom, not equal on all sides.
 * Rounded contours depend on their actual field distance.
 * The NaN rode the falloff into alpha as NaN × (1 − coverage) = NaN × 0,
 * and the reproduced large surfaces drew a white interior block. The fix
 * clamps the normalized falloff argument to ±8 before the cubic, where the
 * curve is 1 to f32 exactly, so no pixel a healthy render produced moves.
 *
 * `lens-size-depth` already holds a 420 × 400 surface, and its own measurement
 * — a DIFFERENCE between a lensed and an unlensed capture — could not see the
 * defect: NaN differs from NaN by nothing. This reads the capture itself.
 */

import { expect, test } from "@playwright/test";

import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/** The wide surface of `lens-size-depth`: centre [390, 220], size [420, 400], DPR 1. */
const WIDE_CENTRE = [390, 220] as const;
const WIDE_HALF = [210, 200] as const;

const pixel = (raster: Raster, x: number, y: number): [number, number, number, number] => {
  const i = (y * raster.width + x) * 4;
  return [
    raster.data[i] ?? 0,
    raster.data[i + 1] ?? 0,
    raster.data[i + 2] ?? 0,
    raster.data[i + 3] ?? 0,
  ];
};

test.describe("@gpu the deep interior of a large surface", () => {
  test("is the same material 200 px from the edge as 100 px from it", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const raster = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("lens-size-depth")),
    );

    const [cx, cy] = WIDE_CENTRE;
    // 100 px inside the left edge: the healthy side of the old ~153.348 px left-edge line.
    const shallow = pixel(raster, cx - WIDE_HALF[0] + 100, cy);
    // The centre: 210 px from the nearest vertical edge, 200 from the horizontal.
    const deep = pixel(raster, cx, cy);

    // The pass composites the backdrop itself on a texture group, so the interior
    // is opaque on the healthy side and must be opaque at the centre too. NaN in
    // the alpha converted to 0 and the premultiplied-over blend then ADDED the
    // body to the page, which is where the white came from.
    expect(shallow[3], `alpha 100 px in: ${shallow.join(",")}`).toBe(255);
    expect(deep[3], `alpha at the centre: ${deep.join(",")}`).toBe(255);

    // The body over a 32 px checker is heavy scatter this deep on both sides:
    // one grey, a few codes apart at most. White is 60+ codes away from it.
    for (let c = 0; c < 3; c += 1) {
      expect(
        Math.abs((deep[c] ?? 0) - (shallow[c] ?? 0)),
        `channel ${c}: centre ${deep.join(",")} against 100 px in ${shallow.join(",")}`,
      ).toBeLessThanOrEqual(12);
    }
  });
});
