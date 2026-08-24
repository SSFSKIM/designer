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

test("draws a border that bounds the shape", async ({ page }) => {
  await buildCssTier(page);
  const panel = await sample(page, PANEL);

  // A point on the top edge versus one 12px inside it: the drawn border makes
  // the boundaryreadable even where the backdrop behind both is the same cell.
  const onBorder = panel.at(110, 1);
  const inside = panel.at(110, 14);

  expect(channelDelta(onBorder, inside)).toBeGreaterThan(4);
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
