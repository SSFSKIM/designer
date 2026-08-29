/**
 * The framework-agnostic entry, proven by running it (Decision Log #30(c)).
 *
 * `e2e/fixtures/vanilla.ts` mounts a glass root from plain JavaScript through the
 * published specifier `@vitreajs/vitrea-web`, with no framework anywhere in the
 * page. What this spec asserts is that the *whole* path works and not merely
 * that the module imports: the scene registered, the material reached the app's
 * own element, the frame loop is running, the interaction channel moves, and
 * teardown leaves the page as it found it.
 *
 * On all three engines, because that is the claim. Nothing here reads a pixel —
 * Gecko and WebKit render `backdrop-filter` as a no-op in every automatable
 * capture path (Decision Log #18), so the assertions are on declarations and
 * state, which are genuinely observable everywhere.
 */

import { expect, test, type Page } from "@playwright/test";

async function gotoVanilla(page: Page): Promise<void> {
  await page.goto("/e2e/fixtures/vanilla.html");
  await page.waitForSelector("html[data-vanilla-ready='1']");
}

test.describe("a glass root mounted without a framework", () => {
  test("registers the app's own element into the scene", async ({ page }) => {
    await gotoVanilla(page);

    const button = page.locator("#vanilla-button");
    // Still the app's `<button>`: focusable, labelled, announced as a button.
    // The material is applied *to* it rather than wrapped around it.
    await expect(button).toHaveJSProperty("tagName", "BUTTON");
    await expect(button).toHaveText("Share");
    await expect(button).toHaveAttribute("data-vitrea-group", "controls");
    await expect(button).toHaveAttribute("data-vitrea-host-plane", "base");

    const nodeId = await button.getAttribute("data-vitrea-node");
    expect(nodeId).not.toBeNull();

    const registered = await page.evaluate(
      (id) => window.v.root.scene.glassNode(id ?? "") !== undefined,
      nodeId,
    );
    expect(registered).toBe(true);
  });

  test("paints the CSS tier onto it, and measures it", async ({ page }) => {
    await gotoVanilla(page);

    const applied = await page.evaluate(() => {
      const element = document.querySelector<HTMLElement>("#vanilla-button");
      const style = element === null ? undefined : getComputedStyle(element);
      // WebKit answers on the prefixed property and TypeScript's DOM lib does
      // not declare it, so it is read by name rather than by property access.
      return {
        backdropFilter:
          style?.backdropFilter !== undefined && style.backdropFilter !== ""
            ? style.backdropFilter
            : (style?.getPropertyValue("-webkit-backdrop-filter") ?? ""),
        borderRadius: style?.borderRadius ?? "",
      };
    });

    expect(applied.backdropFilter).toContain("blur");
    expect(applied.borderRadius).toContain("14px");

    // The read phase measured the app's element without being told to: the
    // handle carries no geometry, the `ResizeObserver` does.
    const bounds = await page.evaluate(
      () => window.v.root.scene.glassNode(window.v.handle.nodeId)?.bounds,
    );
    expect(bounds).toMatchObject({ width: 160, height: 44 });
  });

  /*
   * One loop, not two. This is the seam the react bindings used to work around
   * by running their own `requestAnimationFrame`: `subscribe` hands an adapter
   * the root's own cadence, so the count below rises without the page ever
   * calling `requestAnimationFrame` itself.
   */
  test("drives the app's per-frame work from the root's own loop", async ({ page }) => {
    await gotoVanilla(page);

    const first = await page.evaluate(() => window.v.frames);
    await page.waitForFunction((seen) => window.v.frames > seen + 3, first);

    const advanced = await page.evaluate(() => ({
      frames: window.v.frames,
      elapsedMs: window.v.elapsedMs,
    }));
    expect(advanced.frames).toBeGreaterThan(first);
    // Time is passing, not just frames: `deltaMs` is a real gap after the first.
    expect(advanced.elapsedMs).toBeGreaterThan(0);
  });

  test("moves the press channel the material reads", async ({ page }) => {
    await gotoVanilla(page);

    const channel = (): Promise<number> =>
      page.evaluate(() => {
        const element = document.querySelector<HTMLElement>("#vanilla-button");
        return Number.parseFloat(element?.style.getPropertyValue("--vitrea-press") ?? "0");
      });

    await page.locator("#vanilla-button").hover();
    await page.mouse.down();
    await page.waitForFunction(() => {
      const element = document.querySelector<HTMLElement>("#vanilla-button");
      return Number.parseFloat(element?.style.getPropertyValue("--vitrea-press") ?? "0") > 0.5;
    });
    expect(await channel()).toBeGreaterThan(0.5);

    await page.mouse.up();
    await page.waitForFunction(() => {
      const element = document.querySelector<HTMLElement>("#vanilla-button");
      return Number.parseFloat(element?.style.getPropertyValue("--vitrea-press") ?? "0") < 0.1;
    });
  });

  test("reports nothing on a page that follows the placement rules", async ({ page }) => {
    await gotoVanilla(page);
    await page.waitForFunction(() => window.v.frames > 2);

    const reported = await page.evaluate(() =>
      window.v.diagnostics.map((entry) => `${entry.origin}:${entry.diagnostic.code}`),
    );
    // `backdrop-filter` is universal in these three engines, so a clean page is
    // genuinely clean rather than clean-except-for-a-capability-warning.
    expect(reported).toEqual([]);
  });

  test("tears down completely — node gone, attributes gone, loop stopped", async ({ page }) => {
    await gotoVanilla(page);
    await page.waitForFunction(() => window.v.frames > 2);

    const after = await page.evaluate(async () => {
      const at = window.v.frames;
      window.v.teardown();
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return {
        framesAfterTeardown: window.v.frames - at,
        button: document.querySelector("#vanilla-button") !== null,
        layers: document.querySelectorAll("[data-vitrea-layer]").length,
        hosts: document.querySelectorAll("[data-vitrea-node]").length,
      };
    });

    expect(after).toEqual({ framesAfterTeardown: 0, button: false, layers: 0, hosts: 0 });
  });
});
