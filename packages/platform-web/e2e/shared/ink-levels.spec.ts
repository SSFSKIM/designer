/**
 * The named ink levels in a real engine (W27a).
 *
 * Two things belong here rather than in the unit suite, and both are about the
 * platform rather than about the arithmetic.
 *
 * The tokens are **custom properties on the host**, so what an app can read is
 * what the engine's own CSSOM resolves, not what this package handed to
 * `setProperty`. And the quaternary diagnostic's opt-in is detected by scanning
 * the document's two sheet lists — including `document.adoptedStyleSheets`,
 * where a constructed `CSSStyleSheet` goes. jsdom implements neither the
 * constructor nor the property, so the unit suite stands a stub in the list's
 * place and the claim about the property's own semantics is made here.
 *
 * All three engines: this is CSSOM and custom properties, and nothing here needs
 * `backdrop-filter` to have rendered.
 */

import { expect, test, type Page } from "@playwright/test";

import { gotoHarness } from "../support";

/**
 * The size law is 0 at a span of 32 and 1 at 96, so its midpoint — 64 — is the
 * material's thin/thick knee. A 44 px-tall control is below it and a 96 px panel
 * is above, which is the pair the diagnostic distinguishes.
 */
const THIN = { x: 240, y: 160, width: 200, height: 44 };
const THICK = { x: 240, y: 260, width: 200, height: 96 };

const LEVEL_TOKENS = [
  "--vitrea-foreground-secondary",
  "--vitrea-foreground-tertiary",
  "--vitrea-foreground-quaternary",
] as const;

async function build(page: Page, box: typeof THIN, nodeId: string): Promise<void> {
  await page.evaluate(
    async ({ panel, id }) => {
      await window.h.createRoot({});
      window.h.addGroup("g", { backdrop: { tone: "dark" } });
      window.h.addSurface({
        groupId: "g",
        nodeId: id,
        left: panel.x,
        top: panel.y,
        width: panel.width,
        height: panel.height,
        radius: 18,
        label: "Publish",
      });
      window.h.frame(3);
    },
    { panel: box, id: nodeId },
  );
}

test("publishes all four ink levels where the engine's own CSSOM can read them", async ({
  page,
}) => {
  await gotoHarness(page);
  await build(page, THICK, "panel");

  const resolved = await page.evaluate((tokens) => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    if (host === null) return null;
    const computed = getComputedStyle(host);
    return Object.fromEntries(
      [...tokens, "--vitrea-foreground"].map((token) => [
        token,
        computed.getPropertyValue(token).trim(),
      ]),
    );
  }, LEVEL_TOKENS);

  expect(resolved, "the host must be registered and carry the tokens").not.toBeNull();
  expect(resolved?.["--vitrea-foreground"]).not.toBe("");
  for (const token of LEVEL_TOKENS) {
    // Resolved through the cascade, so a value the engine refused to parse would
    // read as the empty string here rather than as what was written.
    expect(resolved?.[token], `${token} must resolve`).toMatch(/^rgb\(|^light-dark\(/);
  }
});

test("finds the quaternary opt-in in an adopted stylesheet, on a thin surface", async ({
  page,
}) => {
  await gotoHarness(page);

  // A constructed sheet, adopted — the shape a framework shipping CSS-in-JS
  // produces, and the one `document.styleSheets` never contains.
  await page.evaluate(() => {
    const sheet = new CSSStyleSheet();
    sheet.replaceSync(".caption { color: var(--vitrea-foreground-quaternary); }");
    document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
  });

  await build(page, THIN, "toolbar");

  const codes = await page.evaluate(() => window.h.diagnosticCodes());
  expect(codes).toContain("quaternary-ink-on-thin-material");
});

test("stays silent on a surface above the knee, with the same adopted sheet", async ({ page }) => {
  await gotoHarness(page);

  await page.evaluate(() => {
    const sheet = new CSSStyleSheet();
    sheet.replaceSync(".caption { color: var(--vitrea-foreground-quaternary); }");
    document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
  });

  await build(page, THICK, "panel");

  // The opt-in is there and the thinness is not, which is what makes this the
  // control for the case above rather than a second version of it.
  const codes = await page.evaluate(() => window.h.diagnosticCodes());
  expect(codes).not.toContain("quaternary-ink-on-thin-material");
});
