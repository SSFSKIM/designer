/**
 * The site's colour-scheme switch (W21 G3).
 *
 * The switch moves two things that are deliberately separate, and this asserts
 * both: the ROOT's material, which is vitrea's — `GlassRoot`'s `colorScheme`
 * prop reaching `createGlassRoot` through the bindings — and the PAGE's own
 * ground, which is the site's `data-color-scheme` attribute and its tokens. A
 * runtime cannot write a host's background, so every application that offers
 * "follow the system" owns the second half; the page is the worked example of
 * both halves moving together.
 *
 * Pinned to the CSS tier, as the demo's other declaration-reading suites are: the
 * material is read off the host's own computed style, and only the CSS tier
 * writes one. Whether the GPU tier's pixels move is `packages/calibration`'s
 * question and the wave's landing sheet's.
 */

import { expect, test, type Page } from "@playwright/test";

async function gotoSite(page: Page): Promise<void> {
  await page.goto("/?renderer=css");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

/** The material one glass host is drawing, as the CSS tier declared it. */
async function material(page: Page): Promise<Record<string, string>> {
  return page.evaluate(() => {
    const host = document.querySelector("[data-vitrea-node]");
    if (host === null) throw new Error("the page has no glass host");
    const style = getComputedStyle(host);
    return {
      backgroundColor: style.backgroundColor,
      backdropFilter: style.backdropFilter,
      boxShadow: style.boxShadow,
    };
  });
}

const select = (page: Page) => page.getByTestId("color-scheme-select");

test("opens light, whatever the visiting system prefers", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await gotoSite(page);

  // The daylight ground is this page's measured default, so a dark system does
  // not change it — the reader asks.
  await expect(select(page)).toHaveValue("light");
  await expect(page.locator("html")).toHaveAttribute("data-color-scheme", "light");
});

test("dark moves the runtime's material and the page's own ground together", async ({ page }) => {
  await gotoSite(page);
  const asLight = await material(page);

  await select(page).selectOption("dark");
  await expect(page.locator("html")).toHaveAttribute("data-color-scheme", "dark");
  await page.waitForTimeout(500);

  const asDark = await material(page);
  expect(asDark).not.toEqual(asLight);
  // The page's ground went down to meet it: the stage canvas clears to
  // `DARK_GROUND.fill`, which `--stage-0` has to agree with.
  const stage = await page
    .locator(".stage")
    .evaluate((element) => getComputedStyle(element).backgroundColor);
  expect(stage).toBe("rgb(27, 33, 38)");
});

test("auto follows the system, in both directions, without a reload", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" });
  await gotoSite(page);

  await select(page).selectOption("auto");
  await expect(page.locator("html")).toHaveAttribute("data-color-scheme", "light");
  const asLight = await material(page);

  await page.emulateMedia({ colorScheme: "dark" });
  await expect(page.locator("html")).toHaveAttribute("data-color-scheme", "dark");
  await page.waitForTimeout(500);
  const asDark = await material(page);
  expect(asDark).not.toEqual(asLight);

  await page.emulateMedia({ colorScheme: "light" });
  await expect(page.locator("html")).toHaveAttribute("data-color-scheme", "light");
  await page.waitForTimeout(500);
  expect(await material(page)).toEqual(asLight);
});
