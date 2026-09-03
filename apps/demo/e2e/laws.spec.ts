/**
 * The material-laws page, asserted rather than eyeballed.
 *
 * A smoke suite, on the CSS tier by query string so it reads the same on a runner
 * with no adapter as on a machine with one: the page loads, every law is on it,
 * the stage follows the reader, each control moves the value the runtime
 * publishes, and the page's own layout reports no dev-mode findings. The optical
 * results are not asserted here; the renderer's unit tests pin each law's shape
 * and `packages/calibration` measures its magnitude against the reference.
 */

import { expect, test, type Page } from "@playwright/test";

const SECTIONS = ["tone", "tint", "body", "lens", "nested"] as const;

async function gotoLaws(page: Page, query = "?renderer=css"): Promise<void> {
  await page.goto(`/laws/${query}`);
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await expect(page.getByRole("heading", { level: 1, name: "The material laws" })).toBeVisible();
}

/** Bring a section into the observation band and let the stage settle on it. */
async function showSection(page: Page, id: string): Promise<void> {
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");
  await expect(page.locator(`.stage[data-mode='${id}']`).first()).toBeVisible();
  await page.waitForTimeout(400);
}

const propertyOf = (page: Page, testId: string, property: string): Promise<string> =>
  page
    .getByTestId(testId)
    .evaluate((element, name) => (element as HTMLElement).style.getPropertyValue(name), property);

test("every law is on the page, and the stage follows the reader", async ({ page }) => {
  await gotoLaws(page);
  for (const id of SECTIONS) {
    await expect(page.locator(`#${id} h2`)).toBeVisible();
    await showSection(page, id);
  }
});

test("the ground control moves the tone the runtime declares", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "tone");

  await page.getByTestId("tone-level").fill("20");
  await expect(page.getByTestId("tone-level-readout")).toContainText("0.020 linear");
  await page.waitForTimeout(400);
  const dark = await propertyOf(page, "tone-small", "--vitrea-tint");

  await page.getByTestId("tone-level").fill("900");
  await expect(page.getByTestId("tone-level-readout")).toContainText("0.900 linear");
  await page.waitForTimeout(400);
  const light = await propertyOf(page, "tone-small", "--vitrea-tint");

  expect(dark).not.toBe("");
  expect(light).not.toBe(dark);

  // The law's readout moves with the control, and the two plates it evaluates
  // for are ordered by size wherever the curve is not flat.
  await expect(page.getByTestId("tone-law")).toContainText("0.9");
});

test("the tint strength moves the declared tint on both plates", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "tint");

  const full = {
    dark: await propertyOf(page, "tint-dark", "--vitrea-tint"),
    light: await propertyOf(page, "tint-light", "--vitrea-tint"),
  };
  expect(full.dark).not.toBe("");

  await page.getByTestId("tint-strength").fill("50");
  await expect(page.getByTestId("tint-readout")).toContainText("/ 50%");
  await page.waitForTimeout(400);
  const half = {
    dark: await propertyOf(page, "tint-dark", "--vitrea-tint"),
    light: await propertyOf(page, "tint-light", "--vitrea-tint"),
  };
  expect(half.dark).not.toBe(full.dark);
  expect(half.light).not.toBe(full.light);
});

test("the span control moves the surface and the blur it is given", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "body");

  const blurOf = async (): Promise<number> =>
    Number.parseFloat(await propertyOf(page, "body-plate", "--vitrea-blur"));

  await page.getByTestId("body-span").fill("40");
  await expect(page.getByTestId("body-span-readout")).toContainText("40px");
  await page.waitForTimeout(400);
  const small = await page.getByTestId("body-plate").boundingBox();
  const smallBlur = await blurOf();

  await page.getByTestId("body-span").fill("288");
  await expect(page.getByTestId("body-span-readout")).toContainText("288px");
  await page.waitForTimeout(400);
  const large = await page.getByTestId("body-plate").boundingBox();
  const largeBlur = await blurOf();

  if (small === null || large === null) throw new Error("the plate has no box");
  expect(Math.round(small.height)).toBe(40);
  expect(Math.round(large.height)).toBe(288);
  // The CSS tier's single width rides the mix, which rises with the span.
  expect(largeBlur).toBeGreaterThan(smallBlur);
  // And the page's own evaluation of the law agrees with what the tier wrote.
  await expect(page.getByTestId("body-single")).toContainText(`${largeBlur.toFixed(2)} px`);
});

test("the refraction rung is a policy result, and the readout says which", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "lens");

  // On the CSS tier the rung reads `none`, and it is the tier that says so.
  await expect(page.getByTestId("lens-rung")).toHaveValue("none");
  await expect(page.getByTestId("lens-regime")).toHaveText("nominal");

  // Arriving with the approximate rung asked for: the override is a construction
  // prop, so the page reads it from the URL, and the policy resolves to reduced.
  await gotoLaws(page, "?renderer=webgpu&rung=approximate");
  await showSection(page, "lens");
  await expect(page.getByTestId("lens-regime")).toHaveText("reduced");
  await expect(page.getByTestId("lens-cap")).toHaveText("approximate");
});

test("the pane sits on the overlay plane, over the base surface", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "nested");

  const base = page.getByTestId("nested-base");
  const over = page.getByTestId("nested-over");
  await expect(base).toHaveAttribute("data-vitrea-host-plane", "base");
  await expect(over).toHaveAttribute("data-vitrea-host-plane", "overlay");

  const baseBox = await base.boundingBox();
  const overBox = await over.boundingBox();
  if (baseBox === null || overBox === null) throw new Error("the nest has no box");
  expect(Math.round(baseBox.width)).toBe(220);
  expect(Math.round(overBox.width)).toBe(120);
  expect(overBox.x).toBeGreaterThan(baseBox.x);
  expect(overBox.x + overBox.width).toBeLessThan(baseBox.x + baseBox.width);
  expect(overBox.y).toBeGreaterThan(baseBox.y);
  expect(overBox.y + overBox.height).toBeLessThan(baseBox.y + baseBox.height);
});

test("the page's own layout reports no dev-mode findings", async ({ page }) => {
  const problems: string[] = [];
  page.on("console", (message) => {
    if (message.text().includes("[vitrea:")) problems.push(message.text());
  });
  page.on("pageerror", (error) => problems.push(`pageerror: ${error.message}`));

  await gotoLaws(page);
  for (const id of SECTIONS) await showSection(page, id);
  await showSection(page, "tone");

  await expect(page.getByTestId("authoring-findings")).toHaveCount(0);
  await expect(page.getByTestId("authoring-clean").first()).toBeVisible();
  expect(problems.filter((line) => line.includes("pageerror"))).toEqual([]);
});
