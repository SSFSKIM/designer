/**
 * The site's colour-scheme switch (W21 G3).
 *
 * The switch moves three things that are deliberately separate, and this asserts
 * all three: the ROOT's material, which is vitrea's — `GlassRoot`'s `colorScheme`
 * prop reaching `createGlassRoot` through the bindings — the PAGE's own ground,
 * which is the site's `data-color-scheme` attribute and its tokens, and the
 * REFERENCE section's evidence, which has to be the resolved scheme's profile or
 * nothing at all.
 *
 * **Pinned to the CSS tier** (`?renderer=css`), and the pin is what makes the
 * material readable rather than a convenience. On the texture tier the material
 * is painted into the optics canvas and the host carries no declarations at all,
 * so a probe reading the host reports `none` under both schemes and would pass
 * for the wrong reason. The CSS tier writes the resolved material onto the host
 * as `--vitrea-tint` and `--vitrea-occlusion`, which is the same probe the tint
 * suite in `site.spec.ts` uses. What the GPU tier's own pixels do under the dark
 * profile is `packages/calibration`'s question and the wave's landing sheet's.
 */

import { expect, test, type Page } from "@playwright/test";

async function gotoSite(page: Page): Promise<void> {
  await page.goto("/?renderer=css");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

/** Bring a section into the observation band and let the stage settle on it. */
async function showSection(page: Page, id: string): Promise<void> {
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");
  await page.waitForTimeout(500);
}

/**
 * The material one plate is drawing, off the declarations the CSS tier wrote.
 *
 * The material stage's untinted plate, because it carries no author tint of its
 * own: what is left in `--vitrea-tint` is the material's own colour and alpha,
 * which is exactly what the colour scheme moves (the dark profile's tint is
 * 0.05 linear where the light one's is white).
 */
async function material(page: Page): Promise<{ tint: string; occlusion: string }> {
  await page.locator('[data-testid="untinted-plate"]').waitFor({ state: "attached" });
  return page.evaluate(() => {
    const plate = document.querySelector<HTMLElement>('[data-testid="untinted-plate"]');
    if (plate === null) throw new Error("the material stage has no untinted plate");
    return {
      tint: plate.style.getPropertyValue("--vitrea-tint"),
      occlusion: plate.style.getPropertyValue("--vitrea-occlusion"),
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
  expect(asLight.tint).not.toBe("");

  await select(page).selectOption("dark");
  await expect(page.locator("html")).toHaveAttribute("data-color-scheme", "dark");
  await page.waitForTimeout(500);

  const asDark = await material(page);
  expect(asDark).not.toEqual(asLight);
  // The page's ground went down to meet it: the stage canvas clears to
  // `DARK_GROUND.fill`, which `--stage-0` has to agree with. The ground element,
  // not the mirror beside it — the mirror paints no background by design.
  const stage = await page
    .locator(".stage:not(.stage--mirror)")
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

/**
 * The reference pair is evidence or it is nothing (W21 G3 review).
 *
 * A live surface drawing the dark material beside a capture of the light one,
 * under a figure measured in the light scheme, is not a fidelity comparison — it
 * is two experiments in one frame. So the section follows the resolved scheme:
 * the dark profile's capture and the dark profile's cell where the scene has one,
 * and no pair at all where it does not.
 */
test.describe("the reference section follows the resolved scheme", () => {
  test("shows the dark profile's capture and cell for a scene the dark bed carries", async ({
    page,
  }) => {
    await gotoSite(page);
    await select(page).selectOption("dark");
    await showSection(page, "reference");
    await page.getByLabel("Scene").selectOption("photo__capsule-button__rest");

    // The capture itself, named on the figure rather than only in the cell row.
    await expect(page.getByTestId("native-profile")).toContainText(
      "apple-macos-26.5-1x-dark-standard",
    );
    await expect(page.locator('.pair__cell[data-cell="native"] img')).toHaveAttribute(
      "src",
      "fixtures/apple-macos-26.5-1x-dark-standard/photo__capsule-button__rest.png",
    );

    // And the figures are that profile's, on the tier the page speaks for.
    const figures = page.locator(".readout--figures");
    await expect(figures).toContainText("apple-macos-26.5-1x-dark-standard");
    await expect(figures).toContainText("texture tier");
    await expect(page.getByTestId("no-dark-capture")).toHaveCount(0);
  });

  test("withdraws the pair for a scene the dark bed does not carry", async ({ page }) => {
    await gotoSite(page);
    await select(page).selectOption("dark");
    await showSection(page, "reference");
    await page.getByLabel("Scene").selectOption("light-solid__capsule-button__rest");

    await expect(page.getByTestId("no-dark-capture")).toBeVisible();
    // No pair in either tree: the ground's captions and the mirror's live surface
    // are one picture, and half of it would be a plate over an explanation.
    await expect(page.locator(".pair")).toHaveCount(0);
    await expect(page.locator('[data-testid="scene-surface"]')).toHaveCount(0);
    await expect(page.locator(".readout--figures")).toHaveCount(0);

    // Back to light and the same scene is a comparison again.
    await select(page).selectOption("light");
    await expect(page.getByTestId("no-dark-capture")).toHaveCount(0);
    await expect(page.getByTestId("native-profile")).toContainText(
      "apple-macos-26.5-1x-light-standard",
    );
  });
});
