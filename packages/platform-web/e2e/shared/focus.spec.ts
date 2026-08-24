import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

/**
 * The property worth asserting is not "Tab reaches a glass button" — engines
 * disagree about that for reasons that have nothing to do with vitrea. Safari
 * ships with *Press Tab to highlight each item on a webpage* off, so Tab visits
 * text fields and lists only, and S1 recorded exactly this: Tab lands on the
 * button in Chromium and Firefox and on `BODY` in WebKit.
 *
 * So the property is **the sandwich does not change focus behaviour**: a glass
 * host is in the sequential focus order exactly where the same unwrapped element
 * would be, and no vitrea layer is ever in it. That holds in every engine, and it
 * is what would actually break if the plane DOM ever grew a `tabindex` or the
 * host layer started swallowing focus.
 */
test.describe("focus traversal", () => {
  test("puts a glass host in the tab order wherever the same plain element would be", async ({
    page,
  }) => {
    await page.evaluate(async () => {
      await window.h.createRoot();

      // First, ask this engine what it does with a plain button in the page.
      const control = document.createElement("button");
      control.id = "control";
      control.textContent = "control";
      document.getElementById("before")?.after(control);
      document.getElementById("before")?.focus();
    });

    await page.keyboard.press("Tab");
    const engineTabsToButtons = await page.evaluate(
      () => document.activeElement?.id === "control",
    );

    // Now the same question with a glass host in that position.
    await page.evaluate(async () => {
      document.getElementById("control")?.remove();
      window.h.addGroup("g");
      window.h.addSurface({
        groupId: "g",
        nodeId: "first",
        left: 200,
        top: 150,
        width: 120,
        height: 40,
        label: "One",
      });
      window.h.frame(2);
      document.getElementById("before")?.focus();
    });

    await page.keyboard.press("Tab");
    const landed = await page.evaluate(() => window.h.activeElement());

    if (engineTabsToButtons) {
      expect(landed).toBe("host:first");
    } else {
      // The engine skips buttons entirely; the sandwich must not be why. It
      // lands wherever it would have without vitrea — never on a glass layer.
      expect(landed.startsWith("layer:")).toBe(false);
      expect(landed.startsWith("proxy:")).toBe(false);
    }
  });

  test("reaches a text-field glass host by Tab, in every engine", async ({ page }) => {
    // Every engine includes text fields in the sequential focus order, so this is
    // the engine-independent proof that the sandwich preserves it.
    await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({
        groupId: "g",
        nodeId: "field",
        as: "input",
        left: 200,
        top: 150,
        width: 200,
        height: 40,
      });
      window.h.frame(2);
      document.getElementById("before")?.focus();
    });

    await page.keyboard.press("Tab");

    expect(await page.evaluate(() => window.h.activeElement())).toBe("host:field");
  });

  test("puts no vitrea layer in the tab order", async ({ page }) => {
    const tabbable = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 200, top: 150, width: 120, height: 40 });
      window.h.frame(2);
      return [
        ...document.querySelectorAll("[data-vitrea-layer], [data-vitrea-proxy], [data-vitrea-root]"),
      ].filter((element) => element.hasAttribute("tabindex")).length;
    });

    expect(tabbable).toBe(0);
  });

  test("focuses a glass host programmatically and keeps it focused", async ({ page }) => {
    const active = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({
        groupId: "g",
        nodeId: "focused",
        left: 200,
        top: 150,
        width: 120,
        height: 40,
      });
      window.h.frame(2);
      window.h.focus("focused");
      return window.h.activeElement();
    });

    expect(active).toBe("host:focused");
  });

  test("keeps a focused host focused across a re-measure", async ({ page }) => {
    const active = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({
        groupId: "g",
        nodeId: "focused",
        left: 200,
        top: 150,
        width: 120,
        height: 40,
      });
      window.h.frame(2);
      window.h.focus("focused");
      window.h.invalidate("focused");
      window.h.frame(3);
      return window.h.activeElement();
    });

    expect(active).toBe("host:focused");
  });
});
