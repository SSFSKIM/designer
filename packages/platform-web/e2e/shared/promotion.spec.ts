import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

/**
 * Cross-plane promotion moves a surface **as a unit** — body, semantic host and
 * highlight together — so the transition renders on one canvas pair and has no
 * seam. §rendering contract names promotion under scroll and under focus as a
 * required integration scenario, and both are here for a reason: moving a
 * focused element is the case where an engine can silently blur it, and a
 * scrolled page is the case where a stale rect is invisible until it is wrong.
 */
test.describe("unit promotion across planes", () => {
  test("moves the host, its node's plane and its group's proxy together", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("menu");
      const nodeId = window.h.addSurface({
        groupId: "menu",
        nodeId: "platter",
        left: 200,
        top: 200,
        width: 180,
        height: 120,
      });
      window.h.frame(3);

      const before = {
        hostPlane: window.h.hostPlane(nodeId),
        nodePlane: window.h.nodePlane(nodeId),
        proxyPlane: window.h.proxyStyle("menu")?.parentPlane,
        renderPlane: window.h
          .requireRoot()
          .renderInput()
          ?.planes.find((plane) => plane.nodes.some((node) => node.nodeId === nodeId))?.plane,
      };

      window.h.promote(nodeId, "overlay");
      window.h.frame(3);

      const after = {
        hostPlane: window.h.hostPlane(nodeId),
        nodePlane: window.h.nodePlane(nodeId),
        proxyPlane: window.h.proxyStyle("menu")?.parentPlane,
        renderPlane: window.h
          .requireRoot()
          .renderInput()
          ?.planes.find((plane) => plane.nodes.some((node) => node.nodeId === nodeId))?.plane,
      };

      return { before, after };
    });

    // The unit moves as one: the semantic host's DOM parent, the node's z-slot
    // in core, the group's proxy element, and the plane the renderer will draw
    // it on all agree before and after.
    expect(result.before).toEqual({
      hostPlane: "base",
      nodePlane: "base",
      proxyPlane: "base",
      renderPlane: "base",
    });
    expect(result.after).toEqual({
      hostPlane: "overlay",
      nodePlane: "overlay",
      proxyPlane: "overlay",
      renderPlane: "overlay",
    });
  });

  test("keeps focus on the promoted host", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        nodeId: "focused",
        left: 200,
        top: 200,
        width: 160,
        height: 44,
      });
      window.h.frame(2);
      window.h.focus(nodeId);
      const before = window.h.activeElement();

      window.h.promote(nodeId, "overlay");
      window.h.frame(2);

      return { before, after: window.h.activeElement(), plane: window.h.hostPlane(nodeId) };
    });

    expect(result.before).toBe("host:focused");
    expect(result.after).toBe("host:focused");
    expect(result.plane).toBe("overlay");
  });

  test("re-measures the promoted host under scroll rather than trusting a stale rect", async ({
    page,
  }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      const glassRoot = window.h.requireRoot();

      // A scroller inside the base plane, so promotion happens while the host's
      // viewport position is offset by a scroll the plane does not share.
      const scroller = document.createElement("div");
      scroller.style.cssText =
        "position:absolute;left:0;top:0;width:500px;height:400px;overflow:auto;pointer-events:none";
      const tall = document.createElement("div");
      tall.style.height = "3000px";
      scroller.append(tall);
      glassRoot.plane("base").hostLayer.append(scroller);

      const host = document.createElement("button");
      host.style.cssText = "position:absolute;left:40px;top:600px;width:160px;height:44px";
      host.textContent = "Menu";
      tall.append(host);

      window.h.addGroup("g");
      const handle = glassRoot.registerHost({ host, groupId: "g", nodeId: "scrolled" });
      window.h.frame(3);

      scroller.scrollTo(0, 500);
      await window.h.settle();
      window.h.frame(2);
      const scrolled = glassRoot.scene.glassNode("scrolled")?.bounds;

      handle.promoteTo("overlay");
      window.h.frame(3);

      return {
        scrolled,
        promoted: glassRoot.scene.glassNode("scrolled")?.bounds,
        hostPlane: window.h.hostPlane("scrolled"),
        focusSafe: window.h.activeElement(),
      };
    });

    // Scrolled 500px: y moves from 600 to 100 while it is still in the scroller.
    expect(result.scrolled).toMatchObject({ y: 100 });
    // Promoted out of the scroller into the overlay plane's host layer, the
    // element keeps its own left/top, so the measured rect follows the move
    // rather than staying at the scrolled position.
    expect(result.hostPlane).toBe("overlay");
    expect(result.promoted).toMatchObject({ x: 40, y: 600 });
  });

  test("hands placement to the consumer when it asked for it", async ({ page }) => {
    // A React binding owns where its portal renders, so vitrea must not move the
    // element out from under it: moving a node a framework inserted breaks that
    // framework's own removal path.
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      const glassRoot = window.h.requireRoot();
      window.h.addGroup("g");

      const host = document.createElement("button");
      host.style.cssText = "position:absolute;left:10px;top:10px;width:100px;height:40px";
      glassRoot.plane("base").hostLayer.append(host);

      const announced: string[] = [];
      const handle = glassRoot.registerHost({
        host,
        groupId: "g",
        nodeId: "external",
        onPlaneChange: (plane) => announced.push(plane),
      });
      window.h.frame(2);

      handle.promoteTo("overlay");
      const beforeConsumerActs = host.closest("[data-vitrea-layer='semantic-host']")
        ?.getAttribute("data-vitrea-plane");

      // The consumer now re-places its own element, as a re-render would.
      glassRoot.plane("overlay").hostLayer.append(host);
      window.h.frame(2);

      return {
        announced,
        beforeConsumerActs,
        after: window.h.requireRoot().scene.glassNode("external")?.descriptor.zSlot.plane,
        hostPlane: host
          .closest("[data-vitrea-layer='semantic-host']")
          ?.getAttribute("data-vitrea-plane"),
      };
    });

    expect(result.announced).toEqual(["overlay"]);
    // vitrea did not touch the DOM: the element was still where the consumer put it.
    expect(result.beforeConsumerActs).toBe("base");
    expect(result.after).toBe("overlay");
    expect(result.hostPlane).toBe("overlay");
  });

  test("reports a promotion to the plane the node is already on", async ({ page }) => {
    const codes = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({ groupId: "g", left: 10, top: 10, width: 100, height: 40 });
      window.h.frame(2);
      window.h.promote(nodeId, "base");
      return window.h.diagnosticCodes();
    });

    expect(codes).toContain("redundant-promotion");
  });
});
