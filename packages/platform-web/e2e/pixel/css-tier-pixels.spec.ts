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
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
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

  expect(style?.borderTopWidth).toBe("1px");
  expect(style?.borderTopColor).toContain("rgba(255, 255, 255");
});

test("renders system colors and no glass under forced colors", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active" });
  await buildCssTier(page);

  const style = await page.evaluate(() => window.h.hostStyle("panel"));

  expect(style?.backdropFilter).toBe("none");
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
