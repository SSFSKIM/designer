/**
 * The tint-and-ink band, in a browser (W27e G2).
 *
 * 0.16.0 published a tinted `GlassButton`, a `GlassGroup tint` and the four
 * named ink levels, and the release's own eye sheet found that no page in the
 * repository used any of them (the wave's Surprises, 2026-09-11). The
 * playground's band is that use, and this suite is the part of it a reader
 * cannot check by looking: that the group's seed reaches a member which
 * declares no colour, that the button's seed is the button's own, that all four
 * levels are published in order on one surface, and that the ink is chosen
 * against the material rather than against the page's colour scheme.
 *
 * Structural, so it runs on all three engines: every value below is a custom
 * property the runtime published or a computed `color` derived from one, never
 * a pixel. The tier is pinned to CSS by `gotoPlayground`, which is what makes
 * the properties readable at all on Gecko and WebKit (S1).
 */

import { expect, test, type Locator, type Page } from "@playwright/test";

import { gotoPlayground } from "./support";

const GROUNDS = ["light", "dark"] as const;

/** The seed the tier published for a host, as it wrote it. */
const tintOf = (page: Page, testId: string): Promise<string> =>
  page
    .getByTestId(testId)
    .evaluate((host) => host.style.getPropertyValue("--vitrea-tint").trim());

const groupOf = (page: Page, testId: string): Promise<string | null | undefined> =>
  page
    .getByTestId(testId)
    .evaluate((host) => host.closest("[data-vitrea-group]")?.getAttribute("data-vitrea-group"));

/** `rgb(r, g, b)` or `rgba(r, g, b, a)` as four numbers; alpha defaults to 1. */
function parseColor(value: string): readonly [number, number, number, number] {
  const parts = value
    .replace(/^rgba?\(/, "")
    .replace(/\)$/, "")
    .split(/[\s,/]+/)
    .filter((part) => part.length > 0)
    .map(Number);
  const [r = 0, g = 0, b = 0, a = 1] = parts;
  return [r, g, b, a];
}

/** WCAG relative luminance, which is what "darker ink" has to mean to be checkable. */
function relativeLuminance([r, g, b]: readonly [number, number, number, number]): number {
  const channel = (value: number): number => {
    const scaled = value / 255;
    return scaled <= 0.04045 ? scaled / 12.92 : ((scaled + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

const specimen = (page: Page, ground: string, level: string): Locator =>
  page.getByTestId(`ink-plate-${ground}`).locator(`.ink-level--${level} .ink-level__specimen`);

test.beforeEach(async ({ page }) => {
  await gotoPlayground(page);
});

test("a group's seed colours the member that declares no colour of its own", async ({ page }) => {
  for (const ground of GROUNDS) {
    // The plate and the bookmark are one group with one seed on the group; the
    // tinted button is the group it has to step out into to carry a second.
    expect(await groupOf(page, `ink-plate-${ground}`)).toBe(`ink-${ground}`);
    expect(await groupOf(page, `ink-bookmark-${ground}`)).toBe(`ink-${ground}`);
    expect(await groupOf(page, `ink-publish-${ground}`)).toBe(`ink-${ground}-action`);

    expect(await tintOf(page, `ink-plate-${ground}`)).not.toBe("");
    expect(await tintOf(page, `ink-bookmark-${ground}`)).not.toBe("");
    expect(await tintOf(page, `ink-publish-${ground}`)).not.toBe("");
  }
});

test("the group's tint is operable, and moves only the group's members", async ({ page }) => {
  const before = {
    plate: await tintOf(page, "ink-plate-light"),
    bookmark: await tintOf(page, "ink-bookmark-light"),
    publish: await tintOf(page, "ink-publish-light"),
  };

  await page.getByTestId("group-tint-strength").fill("100");
  await expect(page.getByTestId("group-tint-value")).toContainText("/ 100%");

  await expect.poll(() => tintOf(page, "ink-plate-light")).not.toBe(before.plate);
  await expect.poll(() => tintOf(page, "ink-bookmark-light")).not.toBe(before.bookmark);
  expect(await tintOf(page, "ink-publish-light")).toBe(before.publish);
});

test("the button's tint is the button's own", async ({ page }) => {
  const before = {
    plate: await tintOf(page, "ink-plate-dark"),
    publish: await tintOf(page, "ink-publish-dark"),
  };

  await page.getByTestId("button-tint-strength").fill("35");
  await expect(page.getByTestId("button-tint-value")).toContainText("/ 35%");

  await expect.poll(() => tintOf(page, "ink-publish-dark")).not.toBe(before.publish);
  expect(await tintOf(page, "ink-plate-dark")).toBe(before.plate);
});

test("all four ink levels are published on one surface, in order", async ({ page }) => {
  for (const ground of GROUNDS) {
    const plate = page.getByTestId(`ink-plate-${ground}`);
    for (const token of [
      "--vitrea-foreground",
      "--vitrea-foreground-secondary",
      "--vitrea-foreground-tertiary",
      "--vitrea-foreground-quaternary",
    ]) {
      const published = await plate.evaluate(
        (host, name) => host.style.getPropertyValue(name).trim(),
        token,
      );
      expect(published, `${token} on the ${ground} ground`).not.toBe("");
    }

    const levels = ["primary", "secondary", "tertiary", "quaternary"] as const;
    const colors = [];
    for (const level of levels) {
      colors.push(
        parseColor(await specimen(page, ground, level).evaluate((el) => getComputedStyle(el).color)),
      );
    }

    // One ink at four strengths: the same colour throughout, and a scale that
    // never rises. Secondary is allowed to collapse onto the primary — that is
    // the published guarantee where the primary itself cannot hold the floor —
    // so only the bottom of the ladder is asserted strictly.
    for (const [index, color] of colors.entries()) {
      expect(color.slice(0, 3), `${levels[index]!} ink on the ${ground} ground`).toEqual(
        colors[0]!.slice(0, 3),
      );
      if (index > 0) expect(color[3]).toBeLessThanOrEqual(colors[index - 1]![3]);
    }
    expect(colors[3]![3]).toBeLessThan(colors[1]![3]);
  }
});

test("the ink follows the material, so the tint decides it", async ({ page }) => {
  // Both grounds resolve the dark ink at rest, and that is the material's own
  // answer rather than a missing one: a regular body over a dark backdrop is a
  // bright body, so the dark ink is right over both. What moves the answer is
  // the thing the README says moves it — the author's colour — and a page that
  // declares nothing gets the flip for free.
  const inkOf = async (ground: string): Promise<number> =>
    relativeLuminance(
      parseColor(
        await specimen(page, ground, "primary").evaluate((el) => getComputedStyle(el).color),
      ),
    );

  const atRest = { light: await inkOf("light"), dark: await inkOf("dark") };
  expect(atRest.light).toBeLessThan(0.5);
  expect(atRest.dark).toBeLessThan(0.5);

  await page.getByTestId("group-tint-seed").fill("#0d0d12");
  await page.getByTestId("group-tint-strength").fill("100");
  await expect(page.getByTestId("group-tint-value")).toHaveText("rgb(13 13 18 / 100%)");

  await expect.poll(() => inkOf("light")).toBeGreaterThan(0.5);
  expect(await inkOf("dark")).toBeGreaterThan(0.5);
});

test("secondary is solved per surface; tertiary and quaternary are Apple's fixed alphas", async ({
  page,
}) => {
  const alphaOf = async (ground: string, level: string): Promise<number> =>
    parseColor(await specimen(page, ground, level).evaluate((el) => getComputedStyle(el).color))[3];

  // The same declaration on two grounds. Secondary is solved against the colour
  // each surface is actually drawing, so the two answers differ and both are at
  // or above Apple's 0.6; the two levels below it carry no floor and are the
  // platform's numbers unchanged, which is the difference the band is showing.
  const secondary = { light: await alphaOf("light", "secondary"), dark: await alphaOf("dark", "secondary") };
  expect(secondary.light).toBeGreaterThanOrEqual(0.6);
  expect(secondary.dark).toBeGreaterThanOrEqual(0.6);
  expect(secondary.light).not.toBeCloseTo(secondary.dark, 2);

  expect(await alphaOf("light", "tertiary")).toBeCloseTo(await alphaOf("dark", "tertiary"), 5);
  expect(await alphaOf("light", "quaternary")).toBeCloseTo(await alphaOf("dark", "quaternary"), 5);
});

test("the band names the tier that drew it", async ({ page }) => {
  for (const ground of GROUNDS) {
    const readout = page.getByTestId(`ink-tier-${ground}`);
    // `gotoPlayground` asks for the CSS tier, and the readout reads the resolved
    // group state rather than the request — so this also says the request was met.
    await expect(readout).toHaveText("css · css-backdrop");
  }
});
