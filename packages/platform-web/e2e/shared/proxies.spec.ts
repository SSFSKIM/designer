import { expect, test } from "@playwright/test";

import {
  carriesBodyBlur,
  expectBox,
  expectedProxyBlur,
  gotoHarness,
  paddedBox,
} from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

/**
 * The proxy construction S1 made normative, asserted at the DOM level so it runs
 * on all three engines. Whether the resulting pixels are actually filtered is a
 * Chromium-only question (`e2e/pixel/`); whether the element is built to the
 * contract is not.
 */
test.describe("one masked proxy per sampling group", () => {
  test("builds exactly one proxy per group, in the group's plane, pointer-transparent", async ({
    page,
  }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("toolbar");
      window.h.addSurface({ groupId: "toolbar", left: 100, top: 100, width: 120, height: 44 });
      window.h.addSurface({ groupId: "toolbar", left: 260, top: 100, width: 120, height: 44 });
      window.h.frame(3);
      return {
        count: document.querySelectorAll("[data-vitrea-proxy]").length,
        style: window.h.proxyStyle("toolbar"),
        box: window.h.proxyBox("toolbar"),
      };
    });

    // Two members, one proxy. Never one per member.
    expect(result.count).toBe(1);
    expect(result.style?.parentLayer).toBe("backdrop-proxy");
    expect(result.style?.parentPlane).toBe("base");
    expect(result.style?.pointerEvents).toBe("none");
    expect(result.style?.clipPath).toContain("path(");
  });

  test("pads the border box and clips the mask to the shape union", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g", { samplingPadding: 30, mergeDistance: 30 });
      window.h.addSurface({ groupId: "g", left: 200, top: 200, width: 140, height: 44 });
      window.h.frame(3);
      return { box: window.h.proxyBox("g"), style: window.h.proxyStyle("g") };
    });

    // Box: the member union inflated by the padding.
    expect(result.box).toEqual({ x: 170, y: 170, width: 200, height: 104 });
    // Mask: the shape union only, in proxy-local coordinates — masking to
    // box+padding instead leaves a blurred rectangle standing proud of the glass
    // (S1 measured that halo at GAP mean 102.92/255).
    expect(result.style?.clipPath).toBeTruthy();
    const mask = result.style?.clipPath ?? "";
    // The subpath starts at the shape's own local origin, offset by the padding.
    expect(mask).toMatch(/M\s*(?:30|52)/);
  });

  test("raises a padding below 3σ of the group's blur, and says so", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      // Nominal is stated, not inherited: the machine's own reduced-transparency
      // setting reaches Chromium's media query and would move σ under this test.
      window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: false });
      window.h.addGroup("g", { samplingPadding: 4, mergeDistance: 40 });
      window.h.addSurface({ groupId: "g", left: 300, top: 300, width: 120, height: 40 });
      window.h.frame(3);
      return {
        box: window.h.proxyBox("g"),
        codes: window.h.diagnosticCodes(),
        message: window.h
          .diagnostics()
          .find((entry) => entry.code === "sampling-padding-below-3-sigma")?.message,
      };
    });

    // The floor is 3σ at the blur this group actually draws with — the material's
    // σ scattered by the size law at the member's 40 px span — not the authored 4.
    // Derived rather than written down: see `expectedProxyBlur`.
    const { padding } = expectedProxyBlur({
      spanPx: 40,
      extentsCssPx: [120, 40],
    });
    expect(padding).toBeGreaterThan(4);
    expectBox(result.box, paddedBox({ x: 300, y: 300, width: 120, height: 40 }, padding));
    expect(result.codes).toContain("sampling-padding-below-3-sigma");
    expect(result.message).toContain("3σ");
  });

  test("emits both spellings of the filter", async ({ page }) => {
    // WebKit answers CSS.supports only for the prefixed form; Chromium and Gecko
    // only for the unprefixed one. Emitting one of the two loses an engine.
    const inline = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: false });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 120, height: 40 });
      window.h.frame(3);
      return document.querySelector<HTMLElement>('[data-vitrea-proxy="g"]')?.getAttribute("style");
    });

    // The proxy is the CSS tier's blur in another position, so it carries the
    // same σ an in-place surface of this span renders with (W11c G1), and the
    // number is written exactly as the runtime computes it.
    const { sigma } = expectedProxyBlur({
      spanPx: 40,
      extentsCssPx: [120, 40],
    });
    expect(inline).toContain(`backdrop-filter:blur(${sigma}px) saturate(1.8)`);
    expect(inline).toContain(`-webkit-backdrop-filter:blur(${sigma}px) saturate(1.8)`);
    expect(inline).toContain("clip-path:");
    expect(inline).toContain("-webkit-clip-path:");
  });

  test("orders proxies deterministically, not by insertion", async ({ page }) => {
    // S1: swapping two sibling proxies' paint order shifts their gap-facing
    // bands by mean 0.5–1.0 with peaks of 7/255. Paint order is observable, so
    // for a fidelity-first library it is contract, not an artefact.
    const orders = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      // Registered late-then-early, with orders that say the opposite.
      window.h.addGroup("second");
      window.h.addGroup("first");
      window.h.addSurface({ groupId: "second", left: 400, top: 100, width: 100, height: 40, order: 9 });
      window.h.addSurface({ groupId: "first", left: 100, top: 100, width: 100, height: 40, order: 1 });
      window.h.frame(3);
      const initial = window.h.proxyOrder("base");
      window.h.frame(3);
      return { initial, stable: window.h.proxyOrder("base") };
    });

    expect(orders.initial).toEqual(["first", "second"]);
    // And it does not drift between frames.
    expect(orders.stable).toEqual(orders.initial);
  });

  test("gives a CSS-tier group no proxy at all", async ({ page }) => {
    // The CSS tier filters in place on the host, which is exactly why
    // probe-failed demotes to it: the proxy path that failed is not on its path.
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 140,
        height: 44,
      });
      window.h.frame(3);
      return {
        proxies: document.querySelectorAll("[data-vitrea-proxy]").length,
        host: window.h.hostStyle(nodeId),
        sharp: window.h.layerStyle(nodeId, "sharp"),
      };
    });

    expect(result.proxies).toBe(0);
    // Re-pointed at the sharp layer at W16 G1. The tier no longer filters the
    // host in place — it creates three children and puts the sharp
    // `backdrop-filter` on the first of them — but the doctrine this case is
    // about is unchanged and is why `probe-failed` still demotes here: the tier
    // builds NO PROXY, and its filters read what is behind the host rather than
    // a copy of it.
    expect(result.host?.backdropFilter).toBe("none");
    expect(carriesBodyBlur(result.sharp?.backdropFilter)).toBe(true);
  });

  test("removes a group's proxy when the group goes", async ({ page }) => {
    const remaining = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 120,
        height: 40,
      });
      window.h.frame(3);
      window.h.release(nodeId);
      window.h.frame(3);
      return document.querySelectorAll("[data-vitrea-proxy]").length;
    });

    expect(remaining).toBe(0);
  });
});

test.describe("the CSS tier's own surface", () => {
  test("paints a tint and a border, not only a blur", async ({ page }) => {
    // No probe can catch "the engine renders nothing", so a missed demotion has
    // to be a fidelity loss and not a broken UI.
    const host = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 140,
        height: 44,
        radius: 18,
      });
      window.h.frame(3);
      return { host: window.h.hostStyle(nodeId), overlay: window.h.layerStyle(nodeId, "overlay") };
    });

    /*
     * Re-pointed at the overlay layer at W16 G1, and the property is unchanged.
     * The tier used to paint the tint as the host's own `background-color` and
     * the rim as its `border-color`; it now paints both on the third of three
     * created children, because a tint BENEATH the two filtered layers is
     * sampled by them and darkens a ring 0.010–0.015 encoded deep over the first
     * 4 CSS px (claims §5.71 §3), and because the host's border paints below
     * those children and would be covered. The border's WIDTH stays on the host,
     * where it is layout.
     */
    expect(host.overlay?.backgroundColor).not.toBe("rgba(0, 0, 0, 0)");
    expect(Number.parseFloat(host.host?.borderTopWidth ?? "0")).toBeGreaterThan(0);
    expect(host.overlay?.boxShadow).toContain("inset");
    expect(host.overlay?.boxShadow).not.toBe("none");
    expect(host.host?.borderRadius).toBe("18px");
    expect(host.host?.tint).toBeTruthy();
  });

  test("honours reduced transparency by frosting harder, and never occluding less", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 140,
        height: 44,
      });
      window.h.frame(2);
      const nominal = window.h.hostStyle(nodeId);

      window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: true });
      window.h.frame(2);
      // A change of material *is* what the tier transitions, so the computed
      // value walks to its target over the transition's duration rather than
      // jumping. Reading it immediately would read the old blur and call the
      // policy broken; waiting is what makes this an end-to-end assertion
      // instead of a re-run of the unit test.
      await new Promise((resolve) => setTimeout(resolve, 400));

      return {
        nominal,
        nominalSharp: window.h.layerStyle(nodeId, "sharp"),
        reduced: window.h.hostStyle(nodeId),
        reducedSharp: window.h.layerStyle(nodeId, "sharp"),
      };
    });

    const width = (value: string | undefined): number =>
      Number(/([\d.]+)px/.exec(value ?? "")?.[1] ?? 0);
    /*
     * Read on the published `--vitrea-blur` token since W16 G1, not out of a
     * filter string. The frost multiplies the BASE σ, which is the one number
     * both of the tier's layers are built from — the sharp layer is it divided by
     * the device ratio and the heavy one is it times the renderer's gain — so a
     * frosted surface widens both components, and the token is that same base
     * carried through the tier's single-σ projection. The filter string itself is
     * no longer a number on every engine: on Chromium the body blurs through a
     * reference filter, whose width lives in the `<filter>` definition.
     */
    expect(width(result.reduced?.blur)).toBeGreaterThan(width(result.nominal?.blur));
    // And both layers really are drawing in both regimes, which is what makes the
    // widening a change of material rather than a filter appearing.
    expect(carriesBodyBlur(result.nominalSharp?.backdropFilter)).toBe(true);
    expect(carriesBodyBlur(result.reducedSharp?.backdropFilter)).toBe(true);
    // Frost still moves; occlusion no longer does, because the material's tuned
    // nominal alpha overtook the 0.62 floor `occlusion: "increased"` raises it
    // to (C9a moved it to 0.62 on the GPU tier, K5 derives this tier from the
    // same profile). The reduced-transparency reader gets *more* absolute
    // occlusion than before the tune and no remaining difference from nominal on
    // this axis; re-basing the floor is the parent's, since it is one number
    // shared by both tiers and it sits in the frozen texture-tier set. Asserted
    // as `≥` with the current state pinned below, rather than deleted.
    expect(Number(result.reduced?.occlusion)).toBeGreaterThanOrEqual(
      Number(result.nominal?.occlusion),
    );
    expect(Number(result.nominal?.occlusion)).toBeGreaterThan(0.62);
  });

  test("strengthens the border under increased contrast", async ({ page }) => {
    const widths = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 140,
        height: 44,
      });
      window.h.frame(2);
      const nominal = window.h.hostStyle(nodeId)?.borderTopWidth;

      window.h.requireRoot().setAccessibilityOverrides({ increasedContrast: true });
      window.h.frame(2);

      return { nominal, strong: window.h.hostStyle(nodeId)?.borderTopWidth };
    });

    expect(Number.parseFloat(widths.strong ?? "0")).toBeGreaterThan(
      Number.parseFloat(widths.nominal ?? "0"),
    );
  });

  test("steps aside for a group the WebGPU tier is drawing", async ({ page }) => {
    // Painting both tiers would be the "silently pretending" this codebase
    // refuses — and it would double the material.
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 140,
        height: 44,
      });
      window.h.frame(3);
      const onGpu = window.h.hostStyle(nodeId);
      const onGpuLayers = window.h.layerCount(nodeId);

      window.h.loseDevice();
      await window.h.settle();
      window.h.frame(3);

      return { onGpu, onGpuLayers, afterLoss: window.h.layerStyle(nodeId, "sharp") };
    });

    expect(result.onGpu?.backdropFilter).toBe("none");
    expect(result.onGpu?.backgroundColor).toBe("rgba(0, 0, 0, 0)");
    // The WebGPU tier carries none of the CSS tier's layers at all: they are
    // created when this tier first paints and taken down when it steps aside
    // (W16 G1), which is what keeps the GPU tier's DOM exactly what it was.
    expect(result.onGpuLayers).toBe(0);
    // Losing the device demotes to the CSS tier, and the CSS tier then paints —
    // read on the sharp layer, which is where the filter went at W16 G1.
    expect(carriesBodyBlur(result.afterLoss?.backdropFilter)).toBe(true);
  });
});
