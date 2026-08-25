/**
 * Text contrast over live glass, measured on the rendered pixels.
 *
 * axe cannot answer this. Its contrast rule needs a computable background, and every
 * label on this page's glass sits on a translucent material over an animating
 * canvas, so axe reports "incomplete" and moves on. For the front page of a library
 * whose whole accessibility claim is that the material respects the reader, an
 * unchecked "incomplete" is not good enough.
 *
 * So: the ink is the element's *computed* `color` — whatever the runtime resolved
 * this frame, painted through a canvas and read back, because a colour authored in
 * OKLCH serialises as `oklch(...)` and no arithmetic over that string is a
 * luminance. The surface is the median luminance of the element's own rendered
 * pixels, which on a control is overwhelmingly material rather than type. A
 * percentile pair would not do: on an 80x44 button the glyphs are about six per cent
 * of the area, so both tails describe the surface and the ratio comes out flattering
 * and wrong.
 *
 * Sampled at several points in the backdrop's drift, and the worst is the one that
 * counts. The field moves, so a single sample measures one moment rather than the
 * page.
 */

import { expect, test, type Locator, type Page } from "@playwright/test";
import { PNG } from "pngjs";

/** WCAG AA: 4.5:1 for body text, 3:1 for large text. */
const BODY_FLOOR = 4.5;
const LARGE_FLOOR = 3;

/** Phases of the backdrop's drift, in ms. It has a nine-second period. */
const SAMPLE_DELAYS = [400, 2200, 4200, 6200];

const channel = (value: number): number => {
  const v = value / 255;
  return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
};

const luminance = (r: number, g: number, b: number): number =>
  0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);

const contrast = (a: number, b: number): number =>
  (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);

async function inkLuminance(target: Locator): Promise<number> {
  const rgb = await target.evaluate((element) => {
    const colour = getComputedStyle(element).color;
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const context = canvas.getContext("2d");
    if (context === null) return [0, 0, 0];
    context.fillStyle = colour;
    context.fillRect(0, 0, 1, 1);
    const data = context.getImageData(0, 0, 1, 1).data;
    return [data[0] ?? 0, data[1] ?? 0, data[2] ?? 0];
  });
  return luminance(rgb[0] ?? 0, rgb[1] ?? 0, rgb[2] ?? 0);
}

async function surfaceLuminance(target: Locator): Promise<number> {
  const png = PNG.sync.read(await target.screenshot());
  const values: number[] = [];
  for (let i = 0; i < png.data.length; i += 4) {
    if ((png.data[i + 3] ?? 0) < 200) continue;
    values.push(luminance(png.data[i] ?? 0, png.data[i + 1] ?? 0, png.data[i + 2] ?? 0));
  }
  values.sort((a, b) => a - b);
  return values[Math.floor(values.length / 2)] ?? 0;
}

/** The worst ratio any matching element reaches across the sampled phases. */
async function worstRatio(page: Page, selector: string): Promise<{ ratio: number; where: string }> {
  let worst = { ratio: Number.POSITIVE_INFINITY, where: selector };
  for (const delay of SAMPLE_DELAYS) {
    await page.waitForTimeout(delay);
    for (const target of await page.locator(selector).all()) {
      const found = contrast(await inkLuminance(target), await surfaceLuminance(target));
      if (found >= worst.ratio) continue;
      const label = (await target.innerText()).trim().replace(/\s+/g, " ") || selector;
      worst = { ratio: found, where: `${label} at +${delay}ms` };
    }
  }
  return worst;
}

async function showSection(page: Page, id: string): Promise<void> {
  await page.goto("/?renderer=css");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");
}

test("control labels on glass hold the body-text floor", async ({ page }) => {
  await showSection(page, "behavior");
  const worst = await worstRatio(page, ".control");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(BODY_FLOOR);
});

test("segment labels on glass hold the body-text floor, selected and not", async ({ page }) => {
  await showSection(page, "behavior");
  const worst = await worstRatio(page, ".segment");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(BODY_FLOOR);
});

test("the plates' labels hold the large-text floor", async ({ page }) => {
  await showSection(page, "material");
  const worst = await worstRatio(page, ".plate strong");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(LARGE_FLOOR);
});
