import { expect, test } from "@playwright/test";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

const rgb = (r: Raster, x: number, y: number): number[] =>
  Array.from(r.data.slice((y * r.width + x) * 4, (y * r.width + x) * 4 + 3));

test("@golden the inactive tint loses hue without losing its collapsed level", async ({ page }) => {
  requireHardwareAdapter(await openHarness(page));
  const patch = { tintShadeDark: 0.03, tintShadeLight: 0.73, tintShadeStrength: 1,
    rimCollapsed: 0, rimCollapsedTinted: 0 };
  const render = async (p: typeof patch & { tintChromaScale?: number;
    tintShadeCollapseRetention?: number }): Promise<Raster> => decodeCapture(
    await page.evaluate((profile) => window.vitrea.renderScene("collapsed-tone", undefined, profile), p),
  );
  const active = await render(patch);
  const neutral = await render({ ...patch, tintChromaScale: 0 });
  const receded = await render({ ...patch, tintChromaScale: 0, tintShadeCollapseRetention: 1 });
  const identity = await render({ ...patch, tintChromaScale: 1, tintShadeCollapseRetention: 0 });
  expect(Array.from(identity.data)).toEqual(Array.from(active.data));
  // The neutral-only family exposes the unshaded seed at collapse. Retaining
  // the shade is what makes a grey near Y=.037 instead of white.
  // Centers (148,60) and (56,60) CSS px from the fixture, at its declared DPR 2.
  expect(rgb(neutral, 296, 120)).toEqual([255, 255, 255]);
  const shaded = rgb(receded, 296, 120);
  expect(shaded[0]).toBeGreaterThan(35);
  expect(shaded[0]).toBeLessThan(75);
  expect(shaded[1]).toBe(shaded[0]);
  expect(shaded[2]).toBe(shaded[0]);
  expect(rgb(receded, 112, 120)).toEqual(rgb(active, 112, 120));
  expect(rgb(active, 296, 120)[0]).toBeGreaterThan(rgb(active, 296, 120)[2]! + 100);

  const retired = decodeCapture(await page.evaluate((profile) => window.vitrea.renderScene(
    "collapsed-tone", undefined, profile,
  ), { ...patch, optics: { regular: { specularPower: 100, specularGain: 100 } } }));
  expect(Array.from(retired.data)).toEqual(Array.from(active.data));
});
