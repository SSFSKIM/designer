/**
 * Parent acceptance #1 — "Arbitrary DOM, zero setup."
 *
 * The claim is about semantics, so the assertions are made against the
 * accessibility tree and the platform's own behaviors, not against pixels. A
 * label announced as a button, text that can be selected, a field that accepts
 * input, focus that lands where the DOM says it should: those are the things a
 * canvas-drawn control loses, and they are what `asChild` over a real element
 * buys.
 */

import { expect, test } from "@playwright/test";

import { gotoPlayground } from "./support";

test.beforeEach(async ({ page }) => {
  await gotoPlayground(page);
});

test("controls are announced as the controls they are", async ({ page }) => {
  const toolbar = page.getByRole("toolbar", { name: "Playground actions" });
  await expect(toolbar).toBeVisible();

  await expect(page.getByRole("button", { name: "Share" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Add to favorites" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Actions" })).toBeVisible();
  await expect(page.getByRole("radiogroup", { name: "Time range" })).toBeVisible();
  await expect(page.getByRole("radio", { name: "Week" })).toHaveAttribute("aria-checked", "true");
});

test("the accessibility tree carries the roles and names, not the DOM shape", async ({ page }) => {
  // The a11y tree itself, as the platform computes it — the surface a screen
  // reader reads. The glass canvases do not appear in it at all, which is the
  // point: the body is decoration, the semantic host beneath it is the control.
  const tree = await page.getByRole("toolbar", { name: "Playground actions" }).ariaSnapshot();

  expect(tree).toContain('button "Share"');
  expect(tree).toContain('button "Add to favorites"');
  expect(tree).toContain('button "Disabled"');
  expect(tree).toContain('button "Actions"');
  expect(tree).not.toContain("canvas");
  expect(tree).not.toContain("img");
});

test("the glass canvases are inert to hit-testing and to the a11y tree", async ({ page }) => {
  const canvases = page.locator("[data-vitrea-root] canvas");
  await expect(canvases).toHaveCount(4);
  for (const handle of await canvases.all()) {
    await expect(handle).toHaveAttribute("aria-hidden", "true");
    expect(await handle.evaluate((element) => getComputedStyle(element).pointerEvents)).toBe("none");
  }
});

test("a label is a real text node, not a glyph painted into a canvas", async ({ page }) => {
  // The claim being checked is what a canvas-drawn control loses. Whether a
  // *button's* text can be selected is a UA decision — Firefox says no — so the
  // engine-neutral form of "real DOM" is that the label is a Text node the
  // document owns, and page prose is what the selection test below covers.
  const label = await page.evaluate(() => {
    const button = [...document.querySelectorAll("button")].find(
      (element) => element.textContent?.trim() === "Share",
    );
    const text = button?.firstChild;
    return text !== undefined && text !== null && text.nodeType === Node.TEXT_NODE
      ? text.textContent
      : null;
  });

  expect(label).toBe("Share");
});

test("prose behind the glass stays selectable page content", async ({ page }) => {
  const selected = await page.evaluate(() => {
    const paragraph = document.querySelector(".prose p");
    if (paragraph === null) return null;
    const range = document.createRange();
    range.selectNodeContents(paragraph);
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
    return selection?.toString() ?? null;
  });

  expect(selected).toContain("plain DOM");
});

test("focus reaches the toolbar once, and arrows move within it", async ({ page }) => {
  const share = page.getByRole("button", { name: "Share" });
  await share.focus();
  await expect(share).toBeFocused();

  await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("button", { name: "Add to favorites" })).toBeFocused();

  // The disabled button is skipped: it is not a tab stop and not an arrow stop.
  await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("button", { name: "Actions" })).toBeFocused();
});

test("a disabled control is disabled to the platform, not merely styled", async ({ page }) => {
  const disabled = page.getByRole("button", { name: "Disabled", disabled: true });
  await expect(disabled).toBeDisabled();
  expect(
    await disabled.evaluate((element) => element.getAttribute("data-vitrea-node") !== null),
  ).toBe(true);
});

test("every glass host lives inside its plane's host layer, where X1 can sequence it", async ({
  page,
}) => {
  const misplaced = await page.evaluate(() => {
    const hosts = [...document.querySelectorAll("[data-vitrea-node]")];
    return hosts
      .filter((host) => {
        const plane = host.getAttribute("data-vitrea-host-plane");
        const layer = host.closest('[data-vitrea-layer="semantic-host"]');
        return layer === null || layer.getAttribute("data-vitrea-plane") !== plane;
      })
      .map((host) => host.getAttribute("data-vitrea-node"));
  });

  expect(misplaced).toEqual([]);
});
