/**
 * The deep interior of a large surface — the pixels more than ~150 px from
 * every edge, which only a surface over ~307 px in BOTH dimensions has.
 *
 * On Metal, `tanh` is evaluated as (e^2x − 1) / (e^2x + 1), which is inf / inf
 * = NaN once 2x passes ~88.7. The outer shadow's falloff feeds `tanh` a cubic in
 * depth over sigma, and at the shipped sigma of 15.55 that cubic crossed the
 * line at 10.07 σ ≈ 153 px of depth. The NaN rode the falloff into the pass's
 * alpha as NaN × (1 − coverage) — NaN × 0 is NaN — and the deep interior of
 * every large surface drew an opaque white rectangle inset ~153 px from its
 * edges. The fix clamps the falloff's argument to ±8 σ, where the curve is 1 to
 * f32 exactly, so no pixel a healthy render produced moves.
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
    // 100 px inside the left edge: the healthy side of the old 153 px line.
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
