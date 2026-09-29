import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

/**
 * The CSS tier reads only the source pixels under its surfaces (the
 * demand-driven frames spec), and the claim that makes that safe is that the
 * reduction then sees the very bytes a whole-source read gave it. That is a
 * claim about the engine's `drawImage` — a cropped copy at 1:1 and integer
 * offsets must not resample — so it is checked in the engine, on a noisy and
 * partly transparent canvas where any resampling or off-by-one window would move
 * the numbers.
 */

const VIEWPORT = { width: 1440, height: 900, devicePixelRatio: 2 };

test("a windowed read reduces to exactly the whole-source reading", async ({ page }) => {
  await gotoHarness(page);
  const geometries = [
    // A toolbar under a cover-fit source.
    { bounds: { x: 420, y: 780, width: 600, height: 56 }, radius: 28, viewport: VIEWPORT },
    // A small capsule at a fractional position, over a placed source.
    {
      bounds: { x: 101.25, y: 37.5, width: 44, height: 44 }, radius: 22, viewport: VIEWPORT,
      placement: { x: 80, y: 20, width: 700, height: 430 },
    },
    // Straddling the source's own edge, where the taps clamp.
    {
      bounds: { x: 740, y: 400, width: 120, height: 90 }, radius: 16, viewport: VIEWPORT,
      placement: { x: 80, y: 20, width: 700, height: 430 },
    },
    // Straddling the viewport's edge.
    { bounds: { x: 1400, y: -10, width: 80, height: 60 }, radius: 12, viewport: VIEWPORT },
  ];
  const result = await page.evaluate((input) => window.h.toneWindowParity(input), geometries);

  expect(result.windowed).toEqual(result.whole);
  for (const sample of result.whole) expect(sample).toBeDefined();
  // And it is a window: each read is a small fraction of the source.
  for (const pixels of result.windowPixels) {
    expect(pixels).toBeGreaterThan(0);
    expect(pixels).toBeLessThan(result.sourcePixels / 4);
  }
});
