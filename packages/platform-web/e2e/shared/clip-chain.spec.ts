/**
 * The overflow-scroller scenario (Decision Log #41(k)).
 *
 * `GlassNodeRecord.clip` was spec'd in v1 and built on neither end: the read
 * phase never passed a third argument to `setNodeBounds`, and nothing ever read
 * the field. A fix on either side alone is inert, so this spec exercises both —
 * the walk that produces the chain, and the three consumers that act on it.
 *
 * What the scenario is: a glass surface inside an `overflow: auto` ancestor.
 * `getBoundingClientRect` reports the surface's border box wherever it has
 * scrolled to, including entirely outside the scroller, so a pipeline that
 * believed the box believed three false things at once —
 *
 *  1. the surface's proxy painted glass outside the box that was cropping it;
 *  2. `same-plane-overlap` fired, as a hard error, between surfaces that could
 *     never touch;
 *  3. `group-proxy-overlap`'s predicate rests on "a proxy paints only inside its
 *     own clip union", and a union of unclipped boxes made that sentence false.
 *
 * All three engines, because none of it is a pixel assertion — Gecko and WebKit
 * render `backdrop-filter` as a no-op in every automatable capture path
 * (Decision Log #18), and the geometry is observable everywhere.
 */

import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

/** A 400×300 scroller at the plane origin, with one surface 80px down inside it. */
async function scrolled(page: Parameters<typeof gotoHarness>[0]): Promise<void> {
  await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addScroller({ id: "box", left: 40, top: 40, width: 400, height: 300 });
    window.h.addGroup("inside");
    window.h.addSurface({
      nodeId: "inner",
      groupId: "inside",
      into: "box",
      left: 20,
      top: 80,
      width: 160,
      height: 44,
    });
    window.h.frame(2);
  });
}

test.describe("a glass surface inside an overflow scroller", () => {
  test("publishes the scroller's box as the node's clip chain", async ({ page }) => {
    await gotoHarness(page);
    await scrolled(page);

    const measured = await page.evaluate(() => ({
      bounds: window.h.nodeBounds("inner"),
      clip: window.h.nodeClip("inner"),
    }));

    expect(measured.bounds).toMatchObject({ width: 160, height: 44 });
    expect(measured.clip).toHaveLength(1);
    // The scroller's own border box, in viewport space — the window this
    // surface is visible through.
    expect(measured.clip?.[0]).toMatchObject({ x: 40, y: 40, width: 400, height: 300 });
  });

  test("reports no chain for a surface nothing clips", async ({ page }) => {
    await gotoHarness(page);
    await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("plain");
      window.h.addSurface({
        nodeId: "free",
        groupId: "plain",
        left: 500,
        top: 60,
        width: 160,
        height: 44,
      });
      window.h.frame(2);
    });

    // Absent rather than "the viewport": a chain of one trivial window would
    // cost a rect read per frame to say nothing.
    expect(await page.evaluate(() => window.h.nodeClip("free"))).toBeUndefined();
  });

  /*
   * The chain follows the scroll, because the rects are re-read on every
   * measurement while the *set* of clipping ancestors is cached. A chain that
   * only tracked structure would report the scroller's start position forever.
   */
  test("keeps the chain true as the scroller scrolls", async ({ page }) => {
    await gotoHarness(page);
    await scrolled(page);

    const after = await page.evaluate(async () => {
      window.h.scrollScroller("box", 120);
      await window.h.settle();
      window.h.frame(1);
      return { bounds: window.h.nodeBounds("inner"), clip: window.h.nodeClip("inner") };
    });

    // The surface moved up with the content; the window did not move at all.
    expect(after.bounds?.y).toBeCloseTo(0, 0);
    expect(after.clip?.[0]).toMatchObject({ x: 40, y: 40, width: 400, height: 300 });
  });

  /*
   * The proxy is the visible half. It lives in the plane layer, not inside the
   * app's scroller, so nothing crops it for us: before the chain travelled, a
   * surface straddling the scroller's edge had its glass painted in full,
   * hanging outside the container that was supposed to contain it.
   */
  test("crops the group's proxy to what the scroller is showing", async ({ page }) => {
    await gotoHarness(page);

    /*
     * The same surface twice — once straddling a scroller's bottom edge, once
     * with nothing clipping it — and the difference between the two proxies is
     * the assertion. Comparing the pair rather than checking one against a
     * computed expectation keeps the padding, the 3σ floor and the area cap out
     * of the test: whatever they resolve to, they resolve to the same thing on
     * both sides, so the only variable left is the crop.
     */
    const boxes = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addScroller({ id: "box", left: 40, top: 40, width: 400, height: 300 });
      window.h.addGroup("clipped");
      window.h.addGroup("free");
      // 24 of these 44 rows sit below the scroller's bottom edge (40 + 300).
      window.h.addSurface({
        nodeId: "inner",
        groupId: "clipped",
        into: "box",
        left: 20,
        top: 280,
        width: 160,
        height: 44,
      });
      // The identical surface, far enough away to share nothing, unclipped.
      window.h.addSurface({
        nodeId: "outer",
        groupId: "free",
        left: 700,
        top: 320,
        width: 160,
        height: 44,
      });
      window.h.frame(2);
      await window.h.settle();
      window.h.frame(1);
      return { clipped: window.h.proxyBox("clipped"), free: window.h.proxyBox("free") };
    });

    test.skip(
      boxes.clipped === undefined || boxes.free === undefined,
      "this engine resolved the group off the proxy path",
    );

    // 20 rows of glass instead of 44: the 24 the scroller is hiding are gone.
    expect((boxes.free?.height ?? 0) - (boxes.clipped?.height ?? 0)).toBeCloseTo(24, 0);
    // And it stops at the scroller's edge rather than hanging below it.
    expect((boxes.clipped?.y ?? 0) + (boxes.clipped?.height ?? 0)).toBeLessThan(
      40 + 300 + ((boxes.free?.height ?? 44) - 44) / 2 + 1,
    );
  });

  /*
   * The diagnostics half. Two surfaces whose *boxes* overlap, one of them
   * scrolled clean out of its scroller — a legitimate layout that used to
   * produce a hard `same-plane-overlap` error naming a collision that is not on
   * screen, plus a `group-proxy-overlap` warning about double-filtering a region
   * neither group paints.
   */
  test("stops accusing a surface that is scrolled out of view", async ({ page }) => {
    await gotoHarness(page);

    const reported = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addScroller({ id: "box", left: 40, top: 40, width: 400, height: 200 });
      window.h.addGroup("inside");
      window.h.addGroup("outside");
      // Inside the scroller, and scrolled far past its bottom edge.
      window.h.addSurface({
        nodeId: "hidden",
        groupId: "inside",
        into: "box",
        left: 20,
        top: 600,
        width: 160,
        height: 44,
      });
      // Sitting exactly where the hidden surface's unclipped box lands.
      window.h.addSurface({
        nodeId: "visible",
        groupId: "outside",
        left: 60,
        top: 640,
        width: 160,
        height: 44,
      });
      window.h.frame(2);
      await window.h.settle();
      window.h.frame(1);
      return window.h.diagnosticCodes();
    });

    expect(reported).not.toContain("same-plane-overlap");
    expect(reported).not.toContain("group-proxy-overlap");
  });

  /*
   * Teeth. Without this the test above passes for a scene that simply has no
   * overlapping surfaces at all — the same geometry with nothing clipping it
   * has to still be reported, or the fix would read as "the checks went quiet".
   */
  test("still accuses the same geometry when nothing clips it", async ({ page }) => {
    await gotoHarness(page);

    const reported = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("a");
      window.h.addGroup("b");
      window.h.addSurface({
        nodeId: "one",
        groupId: "a",
        left: 20,
        top: 600,
        width: 160,
        height: 44,
      });
      window.h.addSurface({
        nodeId: "two",
        groupId: "b",
        left: 60,
        top: 640,
        width: 160,
        height: 44,
      });
      window.h.frame(2);
      await window.h.settle();
      window.h.frame(1);
      return window.h.diagnosticCodes();
    });

    expect(reported).toContain("same-plane-overlap");
  });

  /*
   * The steady state is the claim §Geometry actually makes, and the clip chain
   * costs reads — a rect per clipping ancestor per measurement, plus a computed
   * style per ancestor the first time a host is measured. None of that may
   * survive into a settled frame.
   */
  test("costs nothing once nothing has changed", async ({ page }) => {
    await gotoHarness(page);
    await scrolled(page);

    const meter = await page.evaluate(async () => {
      await window.h.settle();
      window.h.frame(1);
      window.h.resetMeter();
      window.h.frame(6);
      return window.h.meter();
    });

    expect(meter.total).toBe(0);
  });
});
