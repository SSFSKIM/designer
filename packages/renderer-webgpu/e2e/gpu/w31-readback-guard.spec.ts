/**
 * W31 G2 — the readback guard, wired (claims §5.163 §3; the tracker's WGSL
 * range class, fix shape 3).
 *
 * `test/alpha-holes.test.ts` proves the predicate on synthetic rasters, on both
 * sides, without an adapter. What is left to prove needs a GPU: that the
 * predicate is actually IN the readback path — that a raster carrying the
 * signature does not get past `renderScene` — and that it says nothing about
 * the scenes this package renders.
 *
 * ## How the NaN is seeded, and why it is seeded at the bytes
 *
 * A NaN written to an `rgba8unorm` attachment is a zero, so the guard reads a
 * signature and not a NaN. Seeding it at the shader would need a material that
 * reaches an unclamped transcendental, and there is no longer one to reach:
 * W30 G3b clamped `outer_shadow_falloff`'s `tanh` and this gate floored
 * `angle_delta`, so every path a profile can select is now bounded — which is
 * the point of the child that added the guard, and the reason the seam is a
 * harness hook rather than a profile. `seedAlphaHole` writes an enclosed zero
 * block into the next readback, in device px, before the guard reads it: the
 * exact bytes a NaN would have left, at a place no shader decides.
 *
 * The second case is the one that matters more in practice. A guard that fires
 * on a legitimate render is a guard that gets switched off, so the same scenes
 * the suite renders are rendered here with nothing seeded and the guard is
 * required to be silent — including the layer path's translucent interior and a
 * surface at presence 0, which are its two stand-downs.
 */

import { expect, test } from "@playwright/test";

import { openHarness, requireHardwareAdapter } from "../support";

test.describe("@gpu the readback guard refuses an enclosed zero-alpha region", () => {
  test("a seeded hole does not get past renderScene", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    // The scene renders clean first, so the failure below is attributable to
    // the seed and not to the scene.
    await page.evaluate(() => window.vitrea.renderScene("refraction-checkerboard"));

    const refusal = await page.evaluate(async () => {
      window.vitrea.seedAlphaHole({ x: 90, y: 60, w: 24, h: 12 });
      try {
        await window.vitrea.renderScene("refraction-checkerboard");
        return "no refusal";
      } catch (error) {
        return error instanceof Error ? error.message : String(error);
      }
    });

    expect(refusal).toContain("enclosed region(s) of ZERO alpha inside the drawn silhouette");
    expect(refusal).toContain("288 px in all");
    expect(refusal).toContain("renderScene(refraction-checkerboard)");
  });

  test("the seed is one shot, so the next render is clean again", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    await page.evaluate(async () => {
      window.vitrea.seedAlphaHole({ x: 90, y: 60, w: 8, h: 8 });
      try {
        await window.vitrea.renderScene("refraction-checkerboard");
      } catch {
        // expected
      }
    });
    // No seed armed: this must not throw.
    const ok = await page.evaluate(() => window.vitrea.renderScene("refraction-checkerboard"));
    expect(ok.width).toBeGreaterThan(0);
  });

  test("it is silent on every scene this package renders, and on both stand-downs", async ({
    page,
  }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    // Every golden scene, which is where a false positive would cost the most:
    // the guard sits in the path the 34 goldens read through.
    const names = await page.evaluate(() => window.vitrea.sceneNames());
    expect(names.length).toBeGreaterThanOrEqual(13);
    for (const name of names) {
      await expect(
        page.evaluate((scene) => window.vitrea.renderScene(scene), name),
        `the guard fired on the golden scene "${name}"`,
      ).resolves.toBeTruthy();
    }

    /*
     * Stand-down 1 — the unsampled layer path. `field-mask` is the golden whose
     * group has no backdrop at all, so the optics pass leaves a premultiplied
     * layer: the material's tint at its OWN alpha, well under one, over the
     * whole interior. A guard phrased as "low alpha" would refuse it on every
     * frame; this one reads exactly zero and does not see it.
     */
    await expect(
      page.evaluate(() => window.vitrea.renderScene("field-mask")),
      "the guard fired on the unsampled layer path",
    ).resolves.toBeTruthy();

    /*
     * Stand-down 2 — presence 0. The surface is not there, so its whole
     * footprint is zero alpha; but so is the page around it, which means the
     * region reaches the raster's border and is not ENCLOSED. Enclosure, not
     * emptiness, is what the predicate turns on.
     */
    await expect(
      page.evaluate(() =>
        window.vitrea.renderScene("refraction-checkerboard", undefined, undefined, {
          materialization: 0,
        }),
      ),
      "the guard fired on a surface at presence 0",
    ).resolves.toBeTruthy();

    // And at a presence between the two, where the interior is translucent and
    // the exterior is not yet drawn.
    for (const presence of [0.05, 0.5, 0.95]) {
      await expect(
        page.evaluate(
          (value) =>
            window.vitrea.renderScene("refraction-checkerboard", undefined, undefined, {
              materialization: value,
            }),
          presence,
        ),
        `the guard fired at presence ${presence}`,
      ).resolves.toBeTruthy();
    }
  });
});
