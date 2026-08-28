/**
 * Whose `color` wins on a glass host — measured in a real cascade
 * (Decision Log #34(c)).
 *
 * The runtime decides what ink is readable on the material it is drawing, and
 * that decision is the library's. How it used to arrive was not: the resolved
 * colour went on as an inline `color`, which outranks every application rule
 * short of `!important`. So an app that wrote `.glass-host { color: … }` — the
 * one thing an app is most likely to write — watched the declaration parse,
 * cascade, and never apply, while the token it was told to build on sat on that
 * same element. The ink now arrives through one `:where()` rule that resolves
 * `--vitrea-foreground`, which is zero-specificity and first in the head.
 *
 * All three engines, because this is cascade rather than compositing: nothing
 * here needs `backdrop-filter` to have rendered.
 */

import { expect, test, type Page } from "@playwright/test";

import { gotoHarness } from "../support";

const PANEL = { x: 260, y: 180, width: 200, height: 110 };

/** The fixture page's own `.glass-host` ink, so the runtime's answer is visible. */
const RUNTIME_INK = "rgb(28, 28, 30)";

async function buildPanel(page: Page): Promise<void> {
  await page.evaluate(async (panel) => {
    await window.h.createRoot({});
    window.h.addGroup("g", { backdrop: { tone: "dark" } });
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: panel.x,
      top: panel.y,
      width: panel.width,
      height: panel.height,
      radius: 24,
      label: "Publish",
    });
    window.h.frame(3);
  }, PANEL);
}

test("an application's own rule on a glass host wins", async ({ page }) => {
  await gotoHarness(page);

  // Written before the root exists, the way an app's stylesheet is: one class,
  // the lowest-specificity selector that names the element at all.
  await page.addStyleTag({ content: ".glass-host { color: rgb(4, 5, 6); }" });
  await buildPanel(page);

  const style = await page.evaluate(() => window.h.hostStyle("panel"));

  // The app's ink is what the reader sees…
  expect(style?.color, "the application rule must reach the element").toBe("rgb(4, 5, 6)");
  // …and the runtime has not stopped answering. The token still carries what it
  // would have painted, which is what makes the seam usable rather than merely
  // present: an app can read it, ignore it, or blend it.
  expect(style?.foreground, "the runtime still publishes its own answer").toBe("#1c1c1e");
});

test("the runtime's ink still applies where the application writes none", async ({ page }) => {
  await gotoHarness(page);
  await buildPanel(page);

  // The fixture's `.glass-host` reads the token with the app's own ink as the
  // fallback, which is the documented pattern — so what lands is the runtime's
  // answer, substituted through the very token it publishes.
  const style = await page.evaluate(() => window.h.hostStyle("panel"));
  expect(style?.color).toBe(RUNTIME_INK);
  expect(style?.foreground).toBe("#1c1c1e");
});

test("the rule goes in first, so an equally weak app rule still wins", async ({ page }) => {
  await gotoHarness(page);
  await buildPanel(page);

  // The specificity half of the mechanism is pinned by the unit tests. This is
  // the source-order half: an application rule that is *also* zero-specificity
  // (`*`, or its own `:where()`) has nothing but order to win on, so the sheet
  // has to be first in the head rather than adopted — a constructed stylesheet
  // in `adoptedStyleSheets` sorts after every document sheet and would take
  // that tiebreak the wrong way.
  const placement = await page.evaluate(() => {
    const sheet = document.head.querySelector("style[data-vitrea-ink-stylesheet]");
    return {
      present: sheet !== null,
      first: document.head.firstElementChild === sheet,
      rule: sheet?.textContent ?? "",
    };
  });

  expect(placement.present, "the runtime installs its ink sheet").toBe(true);
  expect(placement.first, "and installs it ahead of the application's own").toBe(true);
  expect(placement.rule).toContain(":where([data-vitrea-node])");
});
