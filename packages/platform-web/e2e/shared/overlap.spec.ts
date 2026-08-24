import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

/**
 * core owns the same-plane overlap check; this package owns feeding it real
 * measured rects and surfacing what it finds. The rule is load-bearing twice
 * over: the sandwich cannot put one surface's body above another's DOM label,
 * *and* S1 measured that overlapping proxies apply the filter exactly twice
 * (1.25² = 1.5625, paint-order dependent).
 */
test.describe("the same-plane overlap dev-error", () => {
  test("fires on two overlapping surfaces in one plane, naming both", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", nodeId: "left", left: 100, top: 100, width: 200, height: 60 });
      window.h.addSurface({ groupId: "g", nodeId: "right", left: 250, top: 120, width: 200, height: 60 });
      window.h.frame(2);
      return window.h.diagnostics().filter((entry) => entry.code === "same-plane-overlap");
    });

    expect(result).toHaveLength(1);
    expect(result[0]?.origin).toBe("core");
    expect(result[0]?.severity).toBe("error");
    expect([...(result[0]?.subjects ?? [])].sort()).toEqual(["left", "right"]);
  });

  test("stays quiet for adjacent surfaces that merely touch", async ({ page }) => {
    // A toolbar's buttons sit edge to edge; that is the common case and it is
    // legal. Only positive-area intersection is an overlap.
    const codes = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 100, height: 40 });
      window.h.addSurface({ groupId: "g", left: 200, top: 100, width: 100, height: 40 });
      window.h.frame(2);
      return window.h.diagnosticCodes();
    });

    expect(codes).not.toContain("same-plane-overlap");
  });

  test("stays quiet when the upper surface is on the overlay plane", async ({ page }) => {
    // The overlapping case *is* the cross-plane case: that is what the overlay
    // plane exists for, and it is the shape a menu over a toolbar takes.
    const codes = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("toolbar");
      window.h.addGroup("menu");
      window.h.addSurface({ groupId: "toolbar", left: 100, top: 100, width: 200, height: 60 });
      window.h.addSurface({
        groupId: "menu",
        plane: "overlay",
        left: 120,
        top: 110,
        width: 200,
        height: 160,
      });
      window.h.frame(2);
      return window.h.diagnosticCodes();
    });

    expect(codes).not.toContain("same-plane-overlap");
  });

  test("reports neighbouring groups whose padded proxies would double-filter", async ({ page }) => {
    // core's other half of X1's proxy geometry: mergeDistance only unions
    // members *inside* one group, so two one-node groups 8px apart still put two
    // padded proxies over the same pixels.
    const codes = await page.evaluate(async () => {
      await window.h.createRoot();
      window.h.addGroup("near-a");
      window.h.addGroup("near-b");
      window.h.addSurface({ groupId: "near-a", left: 100, top: 300, width: 120, height: 44 });
      window.h.addSurface({ groupId: "near-b", left: 228, top: 300, width: 120, height: 44 });
      window.h.frame(2);
      return window.h.diagnosticCodes();
    });

    expect(codes).toContain("group-proxy-overlap");
  });

  test("reports an overlap that only the 3σ floor creates", async ({ page }) => {
    // core checks proxy overlap against the *authored* padding. Raising a
    // padding to 3σ here can create a pair core never saw, and that pair
    // double-filters exactly as measurably as any other.
    const codes = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      // Authored padding of 2 keeps core's own check quiet at a 60px gap; the
      // 3σ floor for the regular material's σ = 8 raises it to 24, and 24 + 24
      // then exceeds the gap.
      window.h.addGroup("a", { samplingPadding: 2, mergeDistance: 2 });
      window.h.addGroup("b", { samplingPadding: 2, mergeDistance: 2 });
      window.h.addSurface({ groupId: "a", left: 100, top: 500, width: 100, height: 40 });
      window.h.addSurface({ groupId: "b", left: 240, top: 500, width: 100, height: 40 });
      window.h.frame(2);
      return window.h.diagnosticCodes();
    });

    expect(codes).toContain("sampling-padding-below-3-sigma");
    expect(codes).toContain("proxy-overlap-after-enforcement");
    // core could not have seen it: at the authored padding the boxes are 56px apart.
    expect(codes).not.toContain("group-proxy-overlap");
  });
});
