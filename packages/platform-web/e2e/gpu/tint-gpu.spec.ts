/**
 * The author tint on the WebGPU tier — the half no CSS declaration can prove.
 *
 * The CSS tier's tint is a colour on the host element, and `tint-pixels.spec.ts`
 * reads it back. The GPU tier's is a per-pixel term inside the optics pass:
 * the seed is a group uniform, the strength rides the field pass's union, and
 * the tone is taken against the very backdrop sample the material is already
 * refracting. None of that is visible anywhere but in the composited canvas, so
 * this is the only place the claim "tint participates in the optical stack on
 * both tiers" can actually be checked.
 *
 * Nothing here asserts a colour. The tone map's constants are advisory until the
 * tinted-capture extension fits them, so what is asserted is that the tint is in
 * the optics — the surface takes the hue, its untinted neighbour in the *same
 * group and same pass* does not, and the backdrop still varies through both.
 */

import { expect, test } from "@playwright/test";

import { channelDelta, gotoHarness, requireHardwareAdapter, sample } from "../support";

const TINTED = { x: 300, y: 200, width: 220, height: 120 };
const PLAIN = { x: 300, y: 360, width: 220, height: 120 };

const warmth = (pixel: { r: number; b: number }): number => pixel.r - pixel.b;

test("draws the tint inside the optics pass, per surface", async ({ page }) => {
  await gotoHarness(page);
  requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

  const built = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "webgpu" });
    window.h.addGroup("g");
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 300,
      top: 200,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
      tint: "#ff9500",
    });
    window.h.addSurface({
      groupId: "g",
      nodeId: "plain",
      left: 300,
      top: 360,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
    });
    window.h.frame(3);
    return window.h.capabilities("g");
  });

  // The tier under test, not the fallback. Without this the whole file would be
  // re-asserting the CSS tier.
  expect(built?.activeRenderer, `resolved ${JSON.stringify(built)}`).toBe("webgpu");

  const tinted = (await sample(page, TINTED)).at(110, 60);
  const plain = (await sample(page, PLAIN)).at(110, 60);

  // Per-surface, out of one optics pass: the strength is a per-pixel channel, so
  // one member of a group can be coloured and its neighbour left alone.
  expect(warmth(tinted)).toBeGreaterThan(warmth(plain) + 30);
});

test("stays glass on the GPU tier — a material, not a fill of the author's colour", async ({
  page,
}) => {
  // The harness page's backdrop under this panel is uniform, so the "backdrop
  // still varies through it" reading belongs to the CSS-tier spec, whose scene
  // has variation to show. What this scene *can* answer is the other half of the
  // same claim, and the sharper one: the surface is not the colour that was
  // asked for. A fill would be exactly `#ff9500`; a tint is that colour's tone
  // composited with what is behind it, inside a body that still has a rim.
  await gotoHarness(page);
  requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

  await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "webgpu" });
    window.h.addGroup("g");
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 300,
      top: 200,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
      tint: "#ff9500",
    });
    window.h.frame(3);
  });

  const panel = await sample(page, TINTED);
  const centre = panel.at(110, 60);
  const seed = { r: 255, g: 149, b: 0 };

  expect(
    channelDelta(centre, seed),
    `the surface reads ${JSON.stringify(centre)}, which is the seed itself`,
  ).toBeGreaterThan(8);

  // And the rim is still on it, which a fill has no way to produce.
  expect(channelDelta(centre, panel.at(2, 60))).toBeGreaterThan(2);
});

test("gives up the material and the colour together under forced colours", async ({ page }) => {
  // The policy that removes the material removes the tint with it — on the tier
  // that was drawing the tint inside a canvas, which is where "the tint vanishes"
  // has to mean the canvas stops painting rather than a declaration changing.
  await gotoHarness(page);
  requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));
  await page.emulateMedia({ forcedColors: "active" });

  await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "webgpu" });
    window.h.addGroup("g");
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 300,
      top: 200,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
      tint: "#ff9500",
    });
    window.h.frame(3);
  });

  const panel = await sample(page, TINTED);
  const centre = panel.at(110, 60);
  expect(warmth(centre)).toBeLessThan(30);
});
