import { expect, test, type Page } from "@playwright/test";

import { channelDelta, gotoHarness, sample } from "../support";

/**
 * Chromium-only pixel assertions for the CSS tier — the fallback that has to
 * look *intentional*.
 *
 * There are two independent reasons this tier's appearance is worth pixels
 * rather than only computed styles. The repo's effects-policy doctrine says the
 * fallback is the design. And S1's undetectable failure class says that because
 * no probe can catch "the engine renders nothing", a *missed* demotion must be a
 * fidelity loss and not a broken UI — which is only true if the surface reads as
 * a surface without its blur.
 */
test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

const PANEL = { x: 300, y: 200, width: 220, height: 120 };
/** The panel plus a 20px margin, so a sample can straddle its contour. */
const WIDE = { x: 280, y: 180, width: 260, height: 160 };

const buildCssTier = async (page: Page): Promise<void> => {
  await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g");
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 300,
      top: 200,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
    });
    window.h.frame(3);
  });
};

/**
 * The paint order the whole element model rests on (W16 G1; charter Decision Log
 * 2 (a)).
 *
 * The tier's three layers are `position: absolute` children with a NEGATIVE
 * `z-index` under a host that establishes a stacking context, which the CSS
 * painting order puts above the host's own background and border and below its
 * in-flow content. Both halves matter and both fail silently if the order is
 * wrong: layers below the host's background would be invisible under any app that
 * styles its own glass host, and layers above its content would bury the label.
 *
 * Asserted with an OPAQUE application background on the host, because that is the
 * decisive case: if the material painted below it the interior would read pure
 * black, and if it painted above it the interior reads the blurred page through
 * the tint. There is no ambiguity between those two answers.
 */
test("paints the material above the host's own background and below its content", async ({
  page,
}) => {
  await buildCssTier(page);
  await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    host?.style.setProperty("background-color", "rgb(0, 0, 0)");
    const label = document.createElement("span");
    label.id = "label";
    label.textContent = "\u2588\u2588\u2588\u2588";
    label.setAttribute(
      "style",
      "position:absolute;left:20px;top:40px;color:rgb(255,0,0);font-size:40px;line-height:40px",
    );
    host?.append(label);
    window.h.frame(3);
  });

  const panel = await sample(page, PANEL);
  const interior = panel.at(150, 30);
  const onLabel = panel.at(40, 60);

  const say = (rgb: { r: number; g: number; b: number }): string => `${rgb.r}, ${rgb.g}, ${rgb.b}`;
  // Above the host's background: the interior is the blurred page under the tint,
  // nowhere near the opaque black the app painted underneath.
  expect(
    Math.max(interior.r, interior.g, interior.b),
    `the interior read ${say(interior)} over an opaque black host background`,
  ).toBeGreaterThan(60);
  // Below the host's content: the label is still the label.
  expect(
    onLabel.r - Math.max(onLabel.g, onLabel.b),
    `the label read ${say(onLabel)}`,
  ).toBeGreaterThan(40);
});

/**
 * The depth ramp reaches the DOM as a real raster, and carries a real gradient
 * (W16 G1; charter Decision Log 2 (b), claims §5.71 §4).
 *
 * The unit suite pins the mask's k(u) against the renderer's law, but it runs in
 * jsdom, which has no canvas — so nothing below the declaration is exercised
 * there. This is the end-to-end half: the heavy layer really carries a
 * `mask-image`, its own `opacity` really went back to 1 because the mask is
 * carrying the weight, and the raster the tier drew really has the band in it.
 * The alpha is read back out of the image rather than sampled off the screen,
 * because that separates "the tier drew the right mask" from "the engine
 * composited it", and only the first is this test's subject.
 */
test("hands the heavy layer a raster mask with the ramp really in it", async ({ page }) => {
  await buildCssTier(page);

  const mask = await page.evaluate(async () => {
    const heavy = document.querySelector<HTMLElement>('[data-vitrea-css-layer="heavy"]');
    const computed = heavy === null ? undefined : getComputedStyle(heavy);
    const image = computed?.maskImage ?? "";
    const url = /url\("(data:[^"]+)"\)/.exec(image)?.[1];
    if (url === undefined) return { url: image, opacity: computed?.opacity ?? "" };

    const bitmap = await createImageBitmap(await (await fetch(url)).blob());
    const canvas = new OffscreenCanvas(bitmap.width, bitmap.height);
    const context = canvas.getContext("2d");
    context?.drawImage(bitmap, 0, 0);
    const alphaAt = (x: number, y: number): number =>
      context?.getImageData(x, y, 1, 1).data[3] ?? -1;
    return {
      url: "data",
      opacity: computed?.opacity ?? "",
      width: bitmap.width,
      height: bitmap.height,
      // Six CSS px in from the contour on the short side, and the middle.
      nearContour: alphaAt(Math.round(bitmap.width / 2), 6),
      centre: alphaAt(Math.round(bitmap.width / 2), Math.round(bitmap.height / 2)),
      // Inside a corner, on the diagonal, where a gradient stack would have been
      // 0.06-0.19 low because `mask-composite` multiplies alphas (claims §5.71 §4).
      corner: alphaAt(8, 8),
    };
  });

  expect(mask.url).toBe("data");
  // The mask carries the whole weight, so the layer's own alpha is 1.
  expect(mask.opacity).toBe("1");
  expect(mask.width).toBe(220);
  expect(mask.height).toBe(120);
  // The band: the heavy share rises from `1 - s₀(span)` at the contour to
  // `kDeep(span)` at the reach, so a raster with no gradient in it would read the
  // same at both depths — which is exactly the surface this tier drew before W16.
  expect(
    (mask.centre ?? 0) - (mask.nearContour ?? 0),
    `mask alpha read ${String(mask.nearContour)} near the contour and ${String(mask.centre)} at the centre`,
  ).toBeGreaterThan(8);
  // And the corner is on the same profile as the sides at its own depth, rather
  // than the product of two of them.
  expect(mask.corner).toBeGreaterThan(0);
  expect(mask.corner).toBeLessThan(mask.centre ?? 0);
});

/**
 * The layers go away with the surface (W16 G1). A released host has to come out
 * of the exchange carrying nothing vitrea put on it — three positioned children
 * left behind would be the most visible possible version of that failure.
 */
test("takes its created layers off a released host", async ({ page }) => {
  await buildCssTier(page);
  const before = await page.evaluate(() => window.h.layerCount("panel"));
  const after = await page.evaluate(() => {
    window.h.release("panel");
    const host = document.querySelector('[data-vitrea-node="panel"]');
    return {
      layers: document.querySelectorAll("[data-vitrea-css-layer]").length,
      unregistered: host === null,
    };
  });

  expect(before).toBe(3);
  expect(after.layers).toBe(0);
  expect(after.unregistered).toBe(true);
});

test("renders a visible glass surface over the page", async ({ page }) => {
  const before = await sample(page, PANEL);
  await buildCssTier(page);
  const after = await sample(page, PANEL);

  const deltas = ([
    [110, 60],
    [40, 30],
    [180, 90],
  ] as const).map(([x, y]) => channelDelta(before.at(x, y), after.at(x, y)));

  expect(Math.max(...deltas), `interior deltas were ${deltas.join(", ")}`).toBeGreaterThan(8);
});

test("stays legible with the blur removed — the tint carries the contrast", async ({ page }) => {
  // The exact condition S1 says a probe can never detect: an engine that reports
  // full support and delivers no filter. Simulated by taking the blur away and
  // leaving everything else the tier drew.
  await buildCssTier(page);
  const withFilter = await sample(page, PANEL);

  await page.evaluate(() => {
    // Both filtered layers, since W16 G1: the tier draws the body as a sharp
    // `backdrop-filter` layer and a heavy one over it, so taking the filter off
    // the host would no longer simulate anything. The condition being simulated
    // is unchanged — an engine that reports full support and delivers no filter
    // — and it now means both layers rendering nothing.
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    for (const layer of host?.querySelectorAll<HTMLElement>("[data-vitrea-css-layer]") ?? []) {
      layer.style.setProperty("backdrop-filter", "none");
      layer.style.setProperty("-webkit-backdrop-filter", "none");
    }
    host?.style.setProperty("backdrop-filter", "none");
    host?.style.setProperty("-webkit-backdrop-filter", "none");
  });
  const withoutFilter = await sample(page, PANEL);
  const bare = await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    host?.style.setProperty("visibility", "hidden");
    return true;
  });
  expect(bare).toBe(true);
  const pageOnly = await sample(page, PANEL);

  // The surface is still clearly a surface: its interior differs from the raw
  // page it sits on, even with no filter at all.
  const stillVisible = ([
    [110, 60],
    [60, 40],
    [170, 85],
  ] as const).map(([x, y]) => channelDelta(withoutFilter.at(x, y), pageOnly.at(x, y)));

  expect(
    Math.min(...stillVisible),
    `an unfiltered CSS-tier surface must still read as a surface; deltas were ${stillVisible.join(", ")}`,
  ).toBeGreaterThan(8);

  // And the filter was doing something before it was removed, so the first
  // assertion is not passing because nothing was ever applied.
  const filterMattered = channelDelta(withFilter.at(110, 60), withoutFilter.at(110, 60));
  expect(filterMattered).toBeGreaterThan(0);
});

/**
 * The same doctrine on a surface carrying a WEAK author tint (W19 G1; charter
 * Parent-Level Acceptance "the floor holds at every strength").
 *
 * The contrast floor is a statement about the ELEMENT paint: whatever the filter
 * does or fails to do, L3 keeps an `rgba()` overlay at the tier's floor alpha, so
 * an engine that reports full support and renders no filter still leaves a
 * surface. Before W19 an author tint replaced that overlay with the author's own
 * layer at the author's own strength — at 0.1 that is well under the floor of
 * 0.2668, so the one surface class the doctrine most protects, a lightly tinted
 * one, was the class that had lost it. The fold restores it by construction
 * (`α″ = 1 − (1 − s)(1 − α₃) ≥ α₃`), and this is that assertion in a real engine
 * rather than in the declaration: the strength is the ladder's lowest rung and
 * the filter is taken away exactly as the untinted test above takes it away.
 */
test("stays legible with the blur removed under a weak author tint", async ({ page }) => {
  const TINTED = { x: 300, y: 400, width: 220, height: 120 };
  await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("t");
    window.h.addSurface({
      groupId: "t",
      nodeId: "tinted",
      left: 300,
      top: 400,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
      // systemOrange at the ladder's lowest rung. A colour's alpha IS the
      // tint's strength on both harnesses.
      tint: "rgba(255, 149, 0, 0.1)",
    });
    window.h.frame(3);
  });

  // The floor, from the declaration the tier wrote — read before any pixel, so a
  // failure says which of the two halves broke.
  const overlay = await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="tinted"]');
    const layer = host?.querySelector<HTMLElement>('[data-vitrea-css-layer="overlay"]');
    const colour = layer === null || layer === undefined ? "" : getComputedStyle(layer).backgroundColor;
    const parts = /^rgba?\(([^)]*)\)$/.exec(colour)?.[1]?.split(",") ?? [];
    return { colour, alpha: parts.length === 4 ? Number(parts[3]) : 1 };
  });
  expect(
    overlay.alpha,
    `L3 painted ${overlay.colour} on a surface tinted at strength 0.1`,
  ).toBeGreaterThanOrEqual(0.2668);

  await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="tinted"]');
    for (const layer of host?.querySelectorAll<HTMLElement>("[data-vitrea-css-layer]") ?? []) {
      layer.style.setProperty("backdrop-filter", "none");
      layer.style.setProperty("-webkit-backdrop-filter", "none");
    }
    host?.style.setProperty("backdrop-filter", "none");
    host?.style.setProperty("-webkit-backdrop-filter", "none");
  });
  const withoutFilter = await sample(page, TINTED);
  await page.evaluate(() => {
    document
      .querySelector<HTMLElement>('[data-vitrea-node="tinted"]')
      ?.style.setProperty("visibility", "hidden");
  });
  const pageOnly = await sample(page, TINTED);

  const stillVisible = ([
    [110, 60],
    [60, 40],
    [170, 85],
  ] as const).map(([x, y]) => channelDelta(withoutFilter.at(x, y), pageOnly.at(x, y)));
  expect(
    Math.min(...stillVisible),
    `an unfiltered CSS-tier surface tinted at 0.1 must still read as a surface; deltas were ${stillVisible.join(", ")}`,
  ).toBeGreaterThan(8);
});

/*
 * The property is that the surface's boundary is discernible. What carries it
 * moved, and the assertion follows the property rather than the old mechanism.
 *
 * This used to compare a point on the drawn border against one 12px inside it,
 * and require > 4. At the material's tuned opacity that delta measures 1: the
 * border is white at alpha 0.35 laid over an interior that is already white at
 * alpha 0.78, so it has almost no headroom left. That is not a regression, and
 * it is what the reference does too — C9a measured Apple's light-scheme rim at
 * seven to twenty-six times *below* one 8-bit code step.
 *
 * What now carries the boundary is the interior itself: measured across the
 * contour, 147 to 178 of 255. The old assertion was a proxy for "you can see
 * where the surface ends", and it was the right proxy while the interior was 28%
 * opaque and nearly invisible. So: assert across the boundary, which is the
 * property, and pin the border's own collapsed contribution separately so that
 * its disappearance stays a recorded fact rather than an unnoticed one.
 */
test("bounds its shape visibly, whatever is doing the bounding", async ({ page }) => {
  const pageOnly = await sample(page, WIDE);
  await buildCssTier(page);
  const withGlass = await sample(page, WIDE);

  // WIDE starts 20px above the panel, so WIDE-local y=20 is the panel's top edge.
  const across = ([2, 6, 10, 14, 18] as const).map((dy) =>
    channelDelta(withGlass.at(130, 20 - dy), withGlass.at(130, 20 + dy)),
  );
  expect(
    Math.min(...across),
    `the boundary must be visible; deltas across it were ${across.join(", ")}`,
  ).toBeGreaterThan(20);

  // And the surface is a surface rather than the page showing through.
  expect(channelDelta(withGlass.at(130, 40), pageOnly.at(130, 40))).toBeGreaterThan(20);
});

test("still paints a border, even though it no longer carries the boundary", async ({ page }) => {
  await buildCssTier(page);

  // Declared, not sampled. The border's pixel contribution against the tuned
  // interior is ~1/255, so a pixel assertion here would be measuring rounding —
  // but the declaration is what S1's undetectable failure class relies on, and it
  // has to still be there for a surface whose tint is ever made transparent again.
  const style = await page.evaluate(() => window.h.hostStyle("panel"));
  const overlay = await page.evaluate(() => window.h.layerStyle("panel", "overlay"));

  // The WIDTH stays on the host and stays layout: the author's content box
  // depends on it and no created layer may move it. The COLOUR moved at W16 G1,
  // because the host's border paints below the tier's negative-`z-index` children
  // and would be covered by them — so the rim is redrawn as an inset `box-shadow`
  // of the same width on the overlay layer, which follows `border-radius` exactly.
  // This is the one change an author can observe in the computed style of their
  // own element, and the property it is asserting is the same one: the surface
  // still declares a real border.
  expect(style?.borderTopWidth).toBe("1px");
  expect(style?.borderTopColor).toBe("rgba(0, 0, 0, 0)");
  expect(overlay?.boxShadow).toContain("rgba(255, 255, 255");
  expect(overlay?.boxShadow).toContain("inset");
});

test("renders system colors and no glass under forced colors", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active" });
  await buildCssTier(page);

  const style = await page.evaluate(() => window.h.hostStyle("panel"));
  const layers = await page.evaluate(() => window.h.layerCount("panel"));

  expect(style?.backdropFilter).toBe("none");
  // Forced colors is a different surface rather than a dimmer material, so the
  // tier's three created layers are torn down rather than emptied (W16 G1): a
  // tier that left them up would leave glass under system colours.
  expect(layers).toBe(0);
  // The flat system fill hides the backdrop completely — "no glass" means
  // maximal occlusion, not minimal.
  expect(style?.occlusion).toBe("1");

  const panel = await sample(page, PANEL);
  const centre = panel.at(110, 60);
  const corner = panel.at(115, 62);
  // A flat fill: two neighbouring interior points are the same colour, where the
  // checkerboard behind would have differed.
  expect(channelDelta(centre, corner)).toBe(0);
});

test("steers the foreground off an author-declared tone, and reaches a readable one", async ({
  page,
}) => {
  // X6's one honesty-core mechanism, reaching the tier most visitors get
  // (Decision Log #28(b), corrective K4): an author-declared backdrop tone must
  // steer the CSS tier's foreground, not just the WebGPU tier's.
  //
  // K5 changed which token that produces. The hint says the backdrop is dark;
  // the regular material is 78% opaque, so what the text sits on is the white
  // tint, and the readable ink is the dark one. The mechanism is what is under
  // test, so this asserts both halves: an explicit token rather than
  // `light-dark()`, AND that the ink actually contrasts with the surface — which
  // is the assertion that would have failed on the old rule at this opacity.
  await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g", { backdrop: { tone: "dark" } });
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 300,
      top: 200,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
    });
    window.h.frame(3);
  });

  const style = await page.evaluate(() => window.h.hostStyle("panel"));

  expect(style?.foreground).toBe("#1c1c1e");
  expect(style?.foreground).not.toContain("light-dark");

  const ink = await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    return host === null ? undefined : getComputedStyle(host).color;
  });
  const linear = (channel: number): number => {
    const value = channel / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  };
  const rgb = /(\d+), (\d+), (\d+)/.exec(ink ?? "");
  const inkLuminance =
    0.2126 * linear(Number(rgb?.[1])) +
    0.7152 * linear(Number(rgb?.[2])) +
    0.0722 * linear(Number(rgb?.[3]));

  const panel = await sample(page, PANEL);
  const surface = panel.at(110, 60);
  const surfaceLuminance =
    0.2126 * linear(surface.r) + 0.7152 * linear(surface.g) + 0.0722 * linear(surface.b);
  const contrast =
    (Math.max(inkLuminance, surfaceLuminance) + 0.05) /
    (Math.min(inkLuminance, surfaceLuminance) + 0.05);

  // WCAG AA for body text. The old rule reached 1.24 here.
  expect(contrast, `ink ${ink ?? "?"} on the measured surface`).toBeGreaterThanOrEqual(4.5);
});

test("shortens its transition under reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await buildCssTier(page);

  const declarations = await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    return host === null ? undefined : getComputedStyle(host).transitionDuration;
  });

  // Reduced Motion removes overshoot, not movement: the transition survives and
  // is shorter and monotonic.
  expect(declarations).toContain("0.12s");
});
