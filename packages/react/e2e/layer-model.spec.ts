/**
 * The layer model, checked against the acceptance harness itself.
 *
 * `glass-inside-glass` and `glass-in-content-layer` are dev-mode findings, and a
 * finding nobody ever sees on a correct page is worth exactly as much as its
 * false-positive rate. This suite is the other half of the unit tests that prove
 * the two codes fire: it proves they stay quiet over the composition vitrea
 * itself ships — a toolbar of sibling surfaces, plates with ordinary DOM inside
 * them, a segmented control whose indicator is deliberately not glass, and a
 * morph platter promoted to the overlay plane while its trigger stays on base.
 *
 * The surface count matters as much as the silence. An empty findings list on a
 * page with no registered hosts would prove nothing, so the assertion is
 * "several surfaces were registered and neither code fired", in both of the
 * playground's states.
 */

import { expect, test, type Page } from "@playwright/test";

import { gotoPlayground, morphSettled, press } from "./support";

const LAYER_MODEL_CODES = ["glass-inside-glass", "glass-in-content-layer"];

/** Every dev-mode line the runtime logged, in order. */
function collectFindings(page: Page): string[] {
  const lines: string[] = [];
  page.on("console", (message) => {
    if (message.text().includes("[vitrea:")) lines.push(message.text());
  });
  return lines;
}

const layerModelFindings = (lines: readonly string[]): string[] =>
  lines.filter((line) => LAYER_MODEL_CODES.some((code) => line.includes(code)));

test("the playground's composition obeys the layer model at rest", async ({ page }) => {
  const lines = collectFindings(page);
  await gotoPlayground(page);

  // There is something to check: the checks run on registration, so silence only
  // means anything once hosts have registered.
  await expect(page.locator("[data-vitrea-node]")).not.toHaveCount(0);
  const surfaces = await page.locator("[data-vitrea-node]").count();
  expect(surfaces).toBeGreaterThan(3);

  expect(layerModelFindings(lines)).toEqual([]);
});

test("and still obeys it with the morph promoted to the overlay plane", async ({ page }) => {
  const lines = collectFindings(page);
  await gotoPlayground(page);

  // The composition most at risk of a false positive: the platter is a glass
  // surface that starts in the toolbar's flow and is promoted across planes,
  // and its trigger is another glass surface a few pixels away.
  await press(page, page.getByRole("button", { name: "Actions" }));
  await morphSettled(page);
  await expect(page.locator("[data-vitrea-morph]")).toBeVisible();

  expect(layerModelFindings(lines)).toEqual([]);
});
