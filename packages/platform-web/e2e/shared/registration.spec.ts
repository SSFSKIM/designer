import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

test.describe("host registration and teardown", () => {
  test("builds X1's sandwich per plane, in paint order, with inert canvases", async ({ page }) => {
    await page.evaluate(async () => {
      await window.h.createRoot();
    });

    const planes = await page.evaluate(() =>
      [...document.querySelectorAll("[data-vitrea-plane-root]")].map((planeRoot) => ({
        plane: planeRoot.getAttribute("data-vitrea-plane-root"),
        layers: [...planeRoot.children].map((child) => child.getAttribute("data-vitrea-layer")),
        canvasesInert: [...planeRoot.querySelectorAll("canvas")].every(
          (canvas) =>
            canvas.getAttribute("aria-hidden") === "true" &&
            getComputedStyle(canvas).pointerEvents === "none" &&
            !canvas.hasAttribute("tabindex"),
        ),
      })),
    );

    // v1 ships exactly two managed planes; more overlays are out of scope.
    expect(planes.map((entry) => entry.plane)).toEqual(["base", "overlay"]);
    for (const entry of planes) {
      expect(entry.layers).toEqual([
        "backdrop-proxy",
        "optics-canvas",
        "semantic-host",
        "highlight-canvas",
      ]);
      expect(entry.canvasesInert).toBe(true);
    }
  });

  test("registers a semantic host as a glass node, keeping it real DOM", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("toolbar");
      const nodeId = window.h.addSurface({
        groupId: "toolbar",
        left: 100,
        top: 200,
        width: 140,
        height: 44,
        label: "Send",
      });
      window.h.frame(1);
      const node = window.h.requireRoot().scene.glassNode(nodeId);
      const host = document.querySelector<HTMLElement>(`[data-vitrea-node="${nodeId}"]`);
      return {
        nodeId,
        registered: node !== undefined,
        groupAttribute: host?.getAttribute("data-vitrea-group"),
        planeAttribute: host?.getAttribute("data-vitrea-host-plane"),
        tag: host?.tagName,
        text: host?.textContent,
        role: host?.getAttribute("type"),
        bounds: node?.bounds,
        pointerEvents: host === null ? undefined : getComputedStyle(host).pointerEvents,
      };
    });

    expect(result.registered).toBe(true);
    expect(result.groupAttribute).toBe("toolbar");
    expect(result.planeAttribute).toBe("base");
    // The label stays a real button: selectable, focusable, IME-capable,
    // announced as a button. That is acceptance #1's whole point.
    expect(result.tag).toBe("BUTTON");
    expect(result.text).toBe("Send");
    expect(result.role).toBe("button");
    // Measured in the read phase and handed to core as data.
    expect(result.bounds).toMatchObject({ x: 100, y: 200, width: 140, height: 44 });
    // The host layer passes pointers through its gaps; a host opts back in.
    expect(result.pointerEvents).toBe("auto");
  });

  test("measures a host that the app resizes, without being told", async ({ page }) => {
    const bounds = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({ groupId: "g", left: 40, top: 40, width: 100, height: 40 });
      window.h.frame(1);
      window.h.resizeSurface(nodeId, 220, 60);
      // ResizeObserver callbacks are delivered after the frame's rAF callbacks,
      // so waiting one animation frame is not enough to see the delivery.
      await window.h.settle();
      window.h.frame(1);
      return window.h.requireRoot().scene.glassNode(nodeId)?.bounds;
    });

    expect(bounds).toMatchObject({ width: 220, height: 60 });
  });

  test("tears down completely: node gone, attributes gone, observers gone", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({ groupId: "g", left: 10, top: 10, width: 80, height: 32 });
      window.h.frame(1);

      const host = document.querySelector<HTMLElement>(`[data-vitrea-node="${nodeId}"]`);
      window.h.release(nodeId);
      window.h.frame(1);

      return {
        nodeGone: window.h.requireRoot().scene.glassNode(nodeId) === undefined,
        attributesGone:
          host === null ||
          (!host.hasAttribute("data-vitrea-node") &&
            !host.hasAttribute("data-vitrea-group") &&
            !host.hasAttribute("data-vitrea-host-plane")),
        hostsLeft: document.querySelectorAll("[data-vitrea-node]").length,
      };
    });

    expect(result.nodeGone).toBe(true);
    expect(result.attributesGone).toBe(true);
    expect(result.hostsLeft).toBe(0);
  });

  test("removes the whole glass root on destroy", async ({ page }) => {
    const remaining = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 10, top: 10, width: 80, height: 32 });
      window.h.frame(1);
      window.h.reset();
      return document.querySelectorAll("[data-vitrea-root]").length;
    });

    expect(remaining).toBe(0);
  });

  test("reports a host placed outside its plane instead of moving it", async ({ page }) => {
    // Moving an element a framework rendered breaks that framework's own removal
    // path, so registration checks placement and names the fix.
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const host = document.createElement("button");
      host.style.cssText = "position:absolute;left:10px;top:10px;width:60px;height:30px";
      document.body.append(host);
      window.h.requireRoot().registerHost({ host, groupId: "g", nodeId: "stray" });
      window.h.frame(1);
      return {
        codes: window.h.diagnosticCodes(),
        stillInBody: host.parentElement === document.body,
      };
    });

    expect(result.codes).toContain("host-outside-plane");
    expect(result.stillInBody).toBe(true);
  });
});
