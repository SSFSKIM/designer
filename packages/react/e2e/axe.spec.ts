/**
 * axe-core over the playground, in both of its states.
 *
 * An automated scan is a floor, not a ceiling — it catches missing names,
 * contrast failures and broken ARIA relationships, and it cannot tell whether a
 * control makes sense. The scans here are what the acceptance asks for
 * alongside the screen-reader-shaped assertions in `semantics.spec.ts`, which
 * are the part that is actually about being usable.
 */

import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

import { gotoPlayground, press } from "./support";

const scan = (page: Page) =>
  new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"])
    /*
     * `region` is disabled, and the reason is architectural rather than
     * convenient.
     *
     * X1 puts every glass surface in vitrea's own plane DOM, which is a sibling
     * of the app's tree and therefore outside every landmark the page wrote. The
     * playground gives its portalled containers landmarks — that is the pattern
     * an app should follow, and `PlanePortal`'s docblock says so — but a surface
     * promoted to the overlay plane mid-morph lands in a layer no app authored,
     * and no amount of markup on the app's side reaches it. Failing a
     * best-practice rule on a container the app cannot author would report the
     * architecture, not a defect. Every WCAG A and AA rule stays on.
     */
    .disableRules(["region"]);

/**
 * A violation as a readable line, with the elements it names.
 *
 * The assertion compares against `[]`, so the failure message *is* the report —
 * a bare count would send whoever broke it back to the browser to find out what.
 */
type AxeResults = Awaited<ReturnType<AxeBuilder["analyze"]>>;

const describeViolations = (violations: AxeResults["violations"]): string[] =>
  violations.map(
    (violation) =>
      `${violation.id}: ${violation.help} — ${violation.nodes
        .map((node) => node.target.join(" "))
        .join(", ")}`,
  );

test.beforeEach(async ({ page }) => {
  await gotoPlayground(page);
});

test("the playground has no axe violations at rest", async ({ page }) => {
  const results = await scan(page).analyze();
  expect(describeViolations(results.violations)).toEqual([]);
});

test("the playground has no axe violations with the menu open", async ({ page }) => {
  await press(page, page.getByRole("button", { name: "Actions" }));
  await expect(page.getByRole("menu")).toBeVisible();
  await page.waitForTimeout(600);

  const results = await scan(page).analyze();
  expect(describeViolations(results.violations)).toEqual([]);
});
