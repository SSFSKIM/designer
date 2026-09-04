import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

/**
 * The DOM the outer shadow's two carriers produce, in a real engine (W18 G1;
 * charter `2026-09-05-w18-union-contour-residual.md`, Decision Log 2 (1)).
 *
 * The unit tests pin what the tier decides and what it writes; this pins that the
 * decision reaches the page — which host holds a group's shadows, that no member
 * holds one of its own, and that a host whose `overflow` clips its children takes
 * the fallback and says so on the resolved state. It is a computed-style spec
 * rather than a pixel one and runs on every engine, because the carriers are
 * ordinary CSS: the mechanism they remove is Chromium's `backdrop-filter`
 * sampling, but nothing about where an element sits is engine-specific, and the
 * level this buys is measured by the calibration harness rather than here.
 */
test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

test("puts a lone surface's shadow on its overlay layer and builds no container", async ({
  page,
}) => {
  const read = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", nodeId: "solo", left: 60, top: 60, width: 120, height: 44 });
    window.h.frame(3);
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="solo"]');
    const overlay = host?.querySelector<HTMLElement>('[data-vitrea-css-layer="overlay"]');
    return {
      carrier: window.h.capabilities("g")?.cssShadow,
      hostShadow: host === null || host === undefined ? "" : getComputedStyle(host).boxShadow,
      overlayShadow: overlay === null || overlay === undefined ? "" : getComputedStyle(overlay).boxShadow,
      containers: document.querySelectorAll("[data-vitrea-css-group-shadow]").length,
    };
  });

  expect(read.carrier).toBe("layer");
  expect(read.hostShadow).toBe("none");
  // The rim first, then the outer shadow: an inset entry and an outset one on the
  // one element that is painted after both of this surface's filters.
  expect(read.overlayShadow).toContain("inset");
  expect(read.overlayShadow).toContain("rgba(0, 0, 0");
  expect(read.containers).toBe(0);
});

test("hangs a three-member group's shadows on its last host, clipped out of every body", async ({
  page,
}) => {
  const read = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g");
    for (const [index, nodeId] of ["a", "b", "c"].entries()) {
      window.h.addSurface({
        groupId: "g",
        nodeId,
        left: 60 + index * 56,
        top: 60,
        width: 44,
        height: 44,
      });
    }
    window.h.frame(3);
    const hostOf = (nodeId: string): HTMLElement | null =>
      document.querySelector<HTMLElement>(`[data-vitrea-node="${nodeId}"]`);
    const container = document.querySelector<HTMLElement>("[data-vitrea-css-group-shadow]");
    return {
      carrier: window.h.capabilities("g")?.cssShadow,
      // Which host holds the container: it must be the LAST in document order,
      // the only element painted after every member's filter layers.
      holder: container?.parentElement?.getAttribute("data-vitrea-node") ?? null,
      containers: document.querySelectorAll("[data-vitrea-css-group-shadow]").length,
      casters: [...(container?.querySelectorAll("[data-vitrea-css-shadow]") ?? [])].map(
        (element) => ({
          nodeId: element.getAttribute("data-vitrea-css-shadow"),
          shadow: getComputedStyle(element).boxShadow,
          hidden: element.getAttribute("aria-hidden"),
          box: element.getBoundingClientRect().toJSON() as { x: number; width: number },
        }),
      ),
      clip: container === null ? "" : getComputedStyle(container).clipPath,
      members: ["a", "b", "c"].map((nodeId) => {
        const host = hostOf(nodeId);
        const overlay = host?.querySelector<HTMLElement>('[data-vitrea-css-layer="overlay"]');
        return {
          nodeId,
          hostShadow: host === null ? "" : getComputedStyle(host).boxShadow,
          overlayShadow: overlay == null ? "" : getComputedStyle(overlay).boxShadow,
          box: host?.getBoundingClientRect().toJSON() as { x: number; width: number },
        };
      }),
    };
  });

  expect(read.carrier).toBe("group");
  expect(read.containers).toBe(1);
  expect(read.holder).toBe("c");
  expect(read.casters.map((caster) => caster.nodeId)).toEqual(["a", "b", "c"]);

  // Not one member draws a shadow of its own — a shadow on an earlier member is
  // in every later member's sampled backdrop, which is the whole neighbours' term.
  for (const member of read.members) {
    expect(member.hostShadow, member.nodeId).toBe("none");
    expect(member.overlayShadow, member.nodeId).not.toContain("rgba(0, 0, 0");
  }
  // Each caster stands exactly on its member's own box, so the shadow the group
  // paints is the shadow that member would have cast for itself.
  for (const [index, caster] of read.casters.entries()) {
    expect(caster.shadow, caster.nodeId ?? "").toContain("rgba(0, 0, 0");
    expect(caster.hidden).toBe("true");
    expect(caster.box.x).toBeCloseTo(read.members[index]!.box.x, 1);
    expect(caster.box.width).toBeCloseTo(read.members[index]!.box.width, 1);
  }
  // And the clip is even-odd with one hole per member: the renderer draws its
  // shadow as `lift · (1 − coverage)` and never on a member's body.
  expect(read.clip).toContain("evenodd");
  expect(read.clip.split("M ").length - 1).toBe(4);
});

test("keeps the shadow on a clipping host, and records the fallback", async ({ page }) => {
  const read = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", nodeId: "clipped", left: 60, top: 60, width: 120, height: 44 });
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="clipped"]');
    // The author's own `overflow`, which vitrea may not override: it is a layout
    // property this package does not own, and it clips the created layers to the
    // padding box — so a shadow on L3 would be cropped away rather than dimmed.
    host?.style.setProperty("overflow", "hidden");
    window.h.frame(4);
    const overlay = host?.querySelector<HTMLElement>('[data-vitrea-css-layer="overlay"]');
    return {
      carrier: window.h.capabilities("g")?.cssShadow,
      hostShadow: host == null ? "" : getComputedStyle(host).boxShadow,
      overlayShadow: overlay == null ? "" : getComputedStyle(overlay).boxShadow,
      containers: document.querySelectorAll("[data-vitrea-css-group-shadow]").length,
    };
  });

  expect(read.carrier).toBe("host");
  expect(read.hostShadow).toContain("rgba(0, 0, 0");
  expect(read.overlayShadow).not.toContain("rgba(0, 0, 0");
  expect(read.containers).toBe(0);
});

test("takes the container off a released host", async ({ page }) => {
  const after = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g");
    for (const [index, nodeId] of ["a", "b"].entries()) {
      window.h.addSurface({
        groupId: "g",
        nodeId,
        left: 60 + index * 56,
        top: 60,
        width: 44,
        height: 44,
      });
    }
    window.h.frame(3);
    const before = document.querySelectorAll("[data-vitrea-css-group-shadow]").length;
    // Releasing the LAST member takes the container with it, and the group falls
    // back to the per-surface carrier — one member has no sibling to hide from.
    window.h.release("b");
    window.h.frame(3);
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="a"]');
    const overlay = host?.querySelector<HTMLElement>('[data-vitrea-css-layer="overlay"]');
    return {
      before,
      containers: document.querySelectorAll("[data-vitrea-css-group-shadow]").length,
      casters: document.querySelectorAll("[data-vitrea-css-shadow]").length,
      carrier: window.h.capabilities("g")?.cssShadow,
      overlayShadow: overlay == null ? "" : getComputedStyle(overlay).boxShadow,
    };
  });

  expect(after.before).toBe(1);
  expect(after.containers).toBe(0);
  expect(after.casters).toBe(0);
  expect(after.carrier).toBe("layer");
  expect(after.overlayShadow).toContain("rgba(0, 0, 0");
});
