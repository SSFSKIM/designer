/**
 * The outer shadow's field extent (W8) — the one place the facet can be right
 * everywhere and still be wrong at the top of the screen.
 *
 * The shadow is not evaluated from the pixel's own distance. It is read from the
 * group's field texture at an OFFSET position, one shadow-offset above the pixel
 * being shaded, because a first-order extrapolation along the normal is exact
 * only on a straight edge and would round every corner it passed. That read can
 * leave the texture, for two reasons that are both ordinary rather than exotic:
 * the field rect is clipped to the canvas, so a surface near the viewport's top
 * has no rows above it; and the rect's pad is only the shadow's reach, so the
 * topmost band of EVERY group needs rows a further offset above that.
 *
 * Clamped, both read the edge texel again — a distance too SMALL, which is a
 * flat and too-dark falloff exactly where the shadow should be fading out, and a
 * divergence from the CSS tier, which has no texture to run out of. So the
 * shader adds back the distance it could not read, which is exact directly above
 * a surface because a signed distance field is 1-Lipschitz.
 *
 * These two scenes are the same surface at two heights. Whatever the shadow does
 * above one of them, it must do above the other.
 */

import { expect, test } from "@playwright/test";

import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/** Where each scene puts its surface's top edge, in CSS px. See `scenes.ts`. */
const TOP_EDGE_Y = 8;
const MID_CANVAS_Y = 108;

/**
 * The shadow's alpha down one column, from `fromY` upward.
 *
 * The alpha, not the colour: the pass writes premultiplied BLACK outside the
 * contour, so opacity is the whole of what the shadow puts on this canvas.
 */
const alphaAbove = (raster: Raster, x: number, fromY: number, rows: number): number[] => {
  const out: number[] = [];
  for (let i = 1; i <= rows; i += 1) {
    const y = fromY - i;
    out.push(raster.data[(y * raster.width + x) * 4 + 3] ?? 0);
  }
  return out;
};

test.describe("@gpu the outer shadow's field extent", () => {
  test("falls off the same way above a top-adjacent surface as above a free one", async ({
    page,
  }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const top = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("shadow-top-edge")),
    );
    const mid = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("shadow-mid-canvas")),
    );

    // Only as far as the top-adjacent surface has canvas above it.
    const rows = TOP_EDGE_Y - 1;
    const topProfile = alphaAbove(top, 120, TOP_EDGE_Y, rows);
    const midProfile = alphaAbove(mid, 120, MID_CANVAS_Y, rows);

    /*
     * The bug this pins produced a FLAT profile — the clamped read returns one
     * distance for every row above the rect, so the shadow stops changing. A
     * healthy one decreases upward, away from the surface.
     */
    expect(new Set(topProfile).size, `flat profile: ${topProfile.join(",")}`).toBeGreaterThan(1);
    for (let i = 1; i < topProfile.length; i += 1) {
      expect(topProfile[i] ?? 0, `row ${i} above the top-adjacent surface`).toBeLessThanOrEqual(
        topProfile[i - 1] ?? 0,
      );
    }

    // And it is the same falloff, not merely some falloff. One 8-bit code of
    // slack, which is the quantisation the alpha is stored at.
    for (let i = 0; i < rows; i += 1) {
      expect(
        Math.abs((topProfile[i] ?? 0) - (midProfile[i] ?? 0)),
        `row ${i}: top ${String(topProfile[i])} against mid ${String(midProfile[i])}`,
      ).toBeLessThanOrEqual(1);
    }

    // Not a vacuous comparison: there is a real shadow to compare.
    expect(midProfile[0] ?? 0).toBeGreaterThan(4);
  });

  test("keeps the shadow's own reach, and stops there", async ({ page }) => {
    /*
     * The other half of the extent claim, and the half the pad's arithmetic
     * decides: the rect has to be big enough that the shadow reaches its natural
     * end inside it rather than being cut off at the scissor.
     *
     * Asserted at the BOTTOM, where the offset points and the reach is longest,
     * on the surface that has room for it.
     */
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const mid = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("shadow-mid-canvas")),
    );

    const bottomEdge = MID_CANVAS_Y + 44;
    const below: number[] = [];
    for (let y = bottomEdge + 1; y < mid.height; y += 1) {
      below.push(mid.data[(y * mid.width + 120) * 4 + 3] ?? 0);
    }

    // It starts as a real shadow, decreases all the way, and arrives at nothing
    // — an edge sliced off at the scissor ends on a step instead.
    expect(below[0] ?? 0).toBeGreaterThan(8);
    for (let i = 1; i < below.length; i += 1) {
      expect(below[i] ?? 0, `row ${i} below`).toBeLessThanOrEqual(below[i - 1] ?? 0);
    }
    expect(below.at(-1) ?? 99).toBe(0);

    // The last non-zero row is the reach, and it lands where the profile's own
    // constants put it rather than where the canvas ran out.
    const lastLit = below.reduce((acc, value, index) => (value > 0 ? index : acc), -1);
    expect(lastLit).toBeGreaterThan(20);
    expect(lastLit).toBeLessThan(below.length - 2);
  });
});
