import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

/**
 * The sandwich puts two canvases and a proxy layer over the page, one of them
 * *above* the semantic host. If any of them were hit-testable, every glass
 * control would be dead. S1 verified this in all three engines and so does this
 * spec, because it costs nothing and it is the property that would break first
 * if the layer styles were ever "tidied".
 */
test.describe("hit-testing through the inert layers", () => {
  test("returns the semantic host at a surface's centre, in every engine", async ({ page }) => {
    const hit = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 200,
        top: 150,
        width: 160,
        height: 48,
      });
      window.h.frame(2);
      return { nodeId, ...window.h.hitTest(280, 174) };
    });

    expect(hit.top).toBe(`host:${hit.nodeId}`);
    // Neither canvas nor proxy appears anywhere in the stack.
    expect(hit.stack.filter((entry) => entry.startsWith("layer:"))).toEqual([]);
    expect(hit.stack.filter((entry) => entry.startsWith("proxy:"))).toEqual([]);
  });

  test("delivers a real click to the host", async ({ page }) => {
    await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 200,
        top: 150,
        width: 160,
        height: 48,
        label: "Click me",
      });
      window.h.frame(2);
      const host = document.querySelector(`[data-vitrea-node="${nodeId}"]`);
      host?.addEventListener("click", () => {
        document.documentElement.setAttribute("data-clicked", "1");
      });
    });

    await page.mouse.click(280, 174);

    await expect(page.locator("html")).toHaveAttribute("data-clicked", "1");
  });

  test("lets a pointer through the gaps between surfaces to the page beneath", async ({ page }) => {
    // The host layer is pointer-events:none and each host opts back in, so a
    // toolbar does not become an invisible full-viewport click shield.
    const hit = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 200, top: 150, width: 160, height: 48 });
      window.h.frame(2);
      return window.h.hitTest(700, 500);
    });

    expect(hit.top.startsWith("host:")).toBe(false);
    expect(hit.stack.filter((entry) => entry.startsWith("layer:"))).toEqual([]);
  });

  test("keeps a group's proxy out of the hit-test stack", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 200,
        top: 150,
        width: 160,
        height: 48,
      });
      window.h.frame(2);
      return {
        nodeId,
        proxy: window.h.proxyStyle("g"),
        hit: window.h.hitTest(280, 174),
      };
    });

    expect(result.proxy?.pointerEvents).toBe("none");
    expect(result.hit.top).toBe(`host:${result.nodeId}`);
    expect(result.hit.stack.filter((entry) => entry.startsWith("proxy:"))).toEqual([]);
  });
});
