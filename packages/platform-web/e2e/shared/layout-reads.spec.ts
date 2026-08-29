import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

/**
 * §Geometry's requirement is not "few reads at steady state" — it is **none**,
 * instrumented so the claim is checkable rather than asserted in a comment. The
 * meter counts every rect, computed style and viewport read in the package, and
 * an ESLint rule keeps every such read routed through it.
 */
test.describe("zero layout reads at steady state", () => {
  test("reads nothing across many idle frames", async ({ page }) => {
    const counts = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
      window.h.addSurface({ groupId: "g", left: 300, top: 100, width: 140, height: 44 });
      // Let the first frames settle: registration, the first measurement and the
      // first backdrop-root audit all legitimately read.
      window.h.frame(4);
      await window.h.settle();
      window.h.frame(1);
      window.h.resetMeter();
      window.h.frame(60);
      return window.h.meter();
    });

    expect(counts).toEqual({ rects: 0, styles: 0, viewport: 0, total: 0 });
  });

  test("reads nothing while vitrea's own transforms animate", async ({ page }) => {
    // A transform does not change a border-box rect, so ResizeObserver does not
    // fire for one and nothing here marks geometry dirty because of one. Press
    // compression and morph deformation therefore cost zero reads per frame,
    // however long they run.
    const counts = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 140,
        height: 44,
      });
      window.h.frame(4);
      await window.h.settle();
      window.h.frame(1);
      window.h.resetMeter();
      for (let index = 0; index < 60; index += 1) {
        const scale = 1 - 0.02 * Math.sin(index / 10);
        window.h.setOwnedTransform(nodeId, `scale(${scale})`);
        window.h.frame(1);
      }
      return window.h.meter();
    });

    expect(counts.total).toBe(0);
  });

  test("reads exactly the dirty host, once, when the app resizes it", async ({ page }) => {
    const counts = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      const first = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 140,
        height: 44,
      });
      window.h.addSurface({ groupId: "g", left: 300, top: 100, width: 140, height: 44 });
      window.h.frame(4);
      await window.h.settle();
      window.h.frame(1);
      window.h.resetMeter();
      window.h.invalidate(first);
      window.h.frame(1);
      // A second idle frame proves the dirty flag was consumed, not latched.
      window.h.frame(1);
      return window.h.meter();
    });

    expect(counts.rects).toBe(1);
    expect(counts.viewport).toBe(0);
  });

  test("marks every host dirty on a viewport resize, and only once", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    const counts = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
      window.h.addSurface({ groupId: "g", left: 300, top: 100, width: 140, height: 44 });
      window.h.frame(4);
      await window.h.settle();
      window.h.frame(1);
      window.h.resetMeter();
      window.dispatchEvent(new Event("resize"));
      window.h.frame(1);
      window.h.frame(1);
      return window.h.meter();
    });

    expect(counts.rects).toBe(2);
    expect(counts.viewport).toBe(1);
  });

  test("marks the hosts inside a scrolled subtree dirty, and no others", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      const glassRoot = window.h.requireRoot();

      // One host inside a scroller that lives in the plane, one outside it.
      const scroller = document.createElement("div");
      scroller.style.cssText =
        "position:absolute;left:0;top:0;width:400px;height:300px;overflow:auto;pointer-events:none";
      const tall = document.createElement("div");
      tall.style.height = "2000px";
      scroller.append(tall);
      glassRoot.plane("base").hostLayer.append(scroller);

      const inside = document.createElement("button");
      inside.style.cssText = "position:absolute;left:20px;top:40px;width:100px;height:40px";
      tall.append(inside);

      window.h.addGroup("g");
      glassRoot.registerHost({ host: inside, groupId: "g", nodeId: "inside" });
      window.h.addSurface({ groupId: "g", nodeId: "outside", left: 600, top: 40, width: 100, height: 40 });
      window.h.frame(4);
      await window.h.settle();
      window.h.frame(1);
      window.h.resetMeter();

      scroller.scrollTo(0, 120);
      // Poll rather than sleep: engines deliver a scroll event on their own
      // schedule, and a fixed wait either flakes or hides a missing event. The
      // assertion is still exact — one host measured, not "at least one".
      for (let attempt = 0; attempt < 20 && window.h.meter().rects === 0; attempt += 1) {
        await window.h.settle();
        window.h.frame(1);
      }
      return { meter: window.h.meter(), clip: window.h.nodeClip("inside") };
    });

    /*
     * Two rects, and the exact number is the point.
     *
     * One is the host inside the scrolled subtree — the only host that moved,
     * and `contains` answers which one without reading anything. The other is
     * the scroller itself: since Decision Log #41(k) a measured host publishes
     * the clip windows its ancestors impose, and a scroll moves the host
     * relative to the window without changing which ancestors clip it, so the
     * window's rect is re-read while the computed-style walk that found it is
     * not repeated.
     *
     * The host *outside* the scroller is still not measured, which is what this
     * test is about. Were it, this would read 3 — plus nothing for its clip
     * chain, because nothing clips it.
     */
    expect(result.meter.rects).toBe(2);
    expect(result.clip).toHaveLength(1);
    expect(result.meter.styles).toBe(0);
  });

  test("counts the backdrop-root audit's style reads as reads", async ({ page }) => {
    // A computed-style read is not a reflow, but "the steady state touches
    // nothing" is the claim worth defending — not "nothing except styles".
    const counts = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
      window.h.frame(4);
      await window.h.settle();
      window.h.frame(1);
      window.h.resetMeter();
      window.h.breakBackdropRoot("opacity", "0.5");
      await window.h.settle();
      window.h.frame(2);
      return window.h.meter();
    });

    expect(counts.styles).toBeGreaterThan(0);
  });
});
