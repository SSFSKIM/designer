import { expect, test, type Page } from "@playwright/test";

import { gotoHarness, sample } from "../support";

/**
 * Backdrop tone adaptation (W7), in a browser, on the CSS tier.
 *
 * The curve is arithmetic and is unit-tested as arithmetic. Two things are not,
 * and both live here.
 *
 * The first is the **reading**. `sampleBackdropTone` draws the app's own backdrop
 * source into a scratch canvas and averages it in linear light, and a browser is
 * the only place that code runs at all — jsdom has no 2-D context. Its one
 * measured trap is that `drawImage` downsamples in the *encoded* space, so a small
 * draw extent reports a structured backdrop far darker than it is.
 *
 * The second is **continuity**. The reference bed samples backdrop luminance at
 * 0.004, 0.012 and then nothing until 0.205, so the shape of the knee between
 * them is a modelling choice rather than a measurement (see
 * `MaterialProfile.backdropToneLow`). What can be measured is that vitrea's own
 * response across that range is continuous and monotone rather than a switch, and
 * that is what the last case here does — on rendered pixels, not on the curve.
 *
 * **A fresh page per backdrop, deliberately.** The harness's `createRoot` leaves
 * the previous root's hosts in the document, so a loop that rebuilt the scene in
 * one page would read the *first* iteration's declarations off
 * `querySelector` while screenshotting the last iteration's pixels — which is a
 * fine way to prove a feature works when it does not.
 */

const SMALL = { x: 300, y: 200, width: 120, height: 44 };
const LARGE = { x: 300, y: 300, width: 260, height: 140 };

/**
 * One flat backdrop, one small surface over it and one large one.
 *
 * The pair is the point: the same backdrop moves them by very different amounts,
 * because the adaptation is size-gated — over the settled bed's `dark-solid` the
 * reference's 44 px capsule vanishes into its background while its 96 px rrect
 * keeps three quarters of its own appearance.
 *
 * The backdrop is a *registered texture source* and is never painted on the page,
 * which is what the harness's texture groups have always done. That is not a
 * limitation here: what the CSS tier does with the tone it reads is entirely in
 * its declarations, and a surface that has adapted all the way is opaque, so its
 * rendered pixels are its declared colour whatever lies behind it.
 */
const buildScene = async (page: Page, fill: string): Promise<void> => {
  await gotoHarness(page);
  await page.evaluate(async (colour) => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addTextureGroup({ groupId: "g", sourceId: "g.raster", fill: colour });
    window.h.addSurface({
      groupId: "g",
      nodeId: "small",
      left: 300,
      top: 200,
      width: 120,
      height: 44,
      radius: 22,
      label: "",
    });
    window.h.addSurface({
      groupId: "g",
      nodeId: "large",
      left: 300,
      top: 300,
      width: 260,
      height: 140,
      radius: 30,
      label: "",
    });
    window.h.frame(3);
  }, fill);
};

interface Declared {
  readonly occlusion: number;
  readonly tint: string;
}

const declared = (page: Page, nodeId: string): Promise<Declared> =>
  page.evaluate((id) => {
    const el = document.querySelector<HTMLElement>(`[data-vitrea-node="${id}"]`);
    return {
      occlusion: Number.parseFloat(el?.style.getPropertyValue("--vitrea-occlusion") ?? "0"),
      tint: el?.style.getPropertyValue("--vitrea-tint") ?? "",
    };
  }, nodeId);

const level = (pixel: { r: number; g: number; b: number }): number =>
  0.2126 * pixel.r + 0.7152 * pixel.g + 0.0722 * pixel.b;

test("a small surface over a near-black backdrop becomes that backdrop", async ({ page }) => {
  // `dark-solid` (28, 28, 30) — the calibration backdrop where the reference's own
  // capsule is byte-identical to its background. Fully adapted, the CSS tier
  // declares the backdrop's own colour at an opacity of 1, so the surface renders
  // as its backdrop rather than as a body in front of it.
  await buildScene(page, "rgb(28, 28, 30)");

  const small = await declared(page, "small");
  expect(small.occlusion).toBeCloseTo(1, 3);
  // Not "close to" the backdrop — the backdrop's own bytes, at an opacity of 1.
  // The reading, the curve and the linear-lerp-to-sRGB-overlay conversion all
  // have to be right for this string to come out.
  expect(small.tint).toBe("rgba(28, 28, 30, 1)");

  const pixel = (await sample(page, SMALL)).at(60, 22);
  expect(Math.abs(level(pixel) - level({ r: 28, g: 28, b: 30 }))).toBeLessThan(4);
});

test("a large surface over the same backdrop keeps most of its own appearance", async ({
  page,
}) => {
  await buildScene(page, "rgb(28, 28, 30)");

  const large = await declared(page, "large");
  const small = await declared(page, "small");

  // The size gate. Same backdrop, same material, and the large surface is still
  // mostly its own colour where the small one is entirely its backdrop's.
  expect(large.occlusion).toBeLessThan(small.occlusion);
  expect(large.tint).not.toBe(small.tint);
  expect(level((await sample(page, LARGE)).at(130, 70))).toBeGreaterThan(
    level((await sample(page, SMALL)).at(60, 22)) + 60,
  );
});

test("an ordinary backdrop moves nothing at all", async ({ page }) => {
  await buildScene(page, "rgb(140, 140, 140)");

  // Above the curve's high edge the axis is exactly inert, which is the property
  // every already-passing calibration cell depends on: the shipped material,
  // untouched, and identical on a surface of either size.
  const small = await declared(page, "small");
  const large = await declared(page, "large");
  expect(small.tint).toBe("rgba(255, 255, 255, 0.781)");
  expect(large.tint).toBe(small.tint);
  expect(small.occlusion).toBe(large.occlusion);
});

test("the response across the transition is continuous and monotone", async ({ page }) => {
  /*
   * The evidence the reference bed cannot give. Twelve flat backdrops from black
   * to a mid grey, which straddles the whole transition (the curve turns on below
   * a linear 0.14 and is fully on below 0.02), read as the surface's declared
   * occlusion and as its rendered level.
   *
   * Two claims, and they are different: monotone says the material never moves
   * the wrong way as its backdrop darkens, and bounded-step says it never jumps —
   * a switch would show as one large gap however monotone the sequence was.
   */
  const steps = 12;
  const occlusions: number[] = [];
  const levels: number[] = [];
  for (let i = 0; i < steps; i += 1) {
    const value = Math.round((i / (steps - 1)) * 140);
    await buildScene(page, `rgb(${value}, ${value}, ${value})`);
    occlusions.push((await declared(page, "small")).occlusion);
    levels.push(level((await sample(page, SMALL)).at(60, 22)));
  }

  for (let i = 1; i < steps; i += 1) {
    expect(occlusions[i] as number, `occlusion ${i}`).toBeLessThanOrEqual(
      (occlusions[i - 1] as number) + 1e-6,
    );
    expect(levels[i] as number, `level ${i}`).toBeGreaterThanOrEqual((levels[i - 1] as number) - 1);
  }

  // The ends are the two states the axis exists to move between…
  expect(occlusions[0] as number).toBeCloseTo(1, 3);
  expect(occlusions[steps - 1] as number).toBeLessThan(0.79);

  // …and it is a slope, not a step: no single move is more than a third of the
  // whole excursion, in either quantity.
  const widest = (series: readonly number[]): number => {
    let most = 0;
    for (let i = 1; i < series.length; i += 1) {
      most = Math.max(most, Math.abs((series[i] as number) - (series[i - 1] as number)));
    }
    return most;
  };
  const occlusionSpan = (occlusions[0] as number) - (occlusions[steps - 1] as number);
  expect(occlusionSpan).toBeGreaterThan(0.15);
  expect(widest(occlusions)).toBeLessThan(occlusionSpan / 3);
});
