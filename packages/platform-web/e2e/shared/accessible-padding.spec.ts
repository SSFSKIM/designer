/**
 * The library's own defaults, under the library's own accessibility mode.
 *
 * `samplingPadding` defaults to 3σ at the blur the group actually draws with,
 * and `mergeDistance` follows it — which is exactly the floor `proxy-geometry.ts`
 * enforces. The two agree because one is derived from the other. When this file
 * was written the derived default was a constant, 24, because σ was a constant,
 * 8; a 0.1.1 consumer flipped `reducedTransparency`, σ became 14, the floor 42,
 * and every group in the page that never declared a padding was suddenly below
 * a floor it was written to sit exactly on — seven warnings about geometry they
 * had never authored.
 *
 * Six of those seven were the default tripping the rule it was written from, and
 * they are what the derived default removes. The seventh — the cross-group
 * overlap warning at the demo's own 56px gap — was a false positive, and the
 * measurement that showed it is `spikes/s1-proxy-topology/overlap-experiment/`:
 * at σ = 14 and a 42px padding the two proxies are byte-identical whether they
 * are painted together or apart, because a proxy's box reaches its neighbour's
 * *painted* pixels only while the gap is under one padding. The check now says
 * that, so it still fires below one padding — where the leak is real — and stops
 * accusing a layout with clearance to spare.
 *
 * σ has moved twice since (8 → 3 before 0.2.0, then W11c G1's scattered σ per
 * span), and the literals this file carried went stale unseen — the CI
 * integration job matched no package from the W5a rename until the 0.3.0
 * release chain. Every number here is now derived from the law through
 * `expectedProxyBlur`, so the tests assert the mechanism rather than a material.
 *
 * Playwright rather than jsdom: proxies exist only where members have measured
 * rects, and a jsdom test here would be asserting a stubbed layout.
 */

import { expect, test, type Page } from "@playwright/test";

import {
  expectBox,
  expectedProxyBlur,
  gotoHarness,
  paddedBox,
} from "../support";

/** The playground's own gap between the toolbar group and the morph's group. */
const DEMO_GROUP_GAP = 56;

/**
 * A gap under one padding at the toolbar's span under reduced transparency, so
 * one group's box covers the other's shapes and the leak the warning names is
 * really there — measured at up to 3/255 around this separation, and larger as
 * it closes further.
 */
const TIGHT_GROUP_GAP = 16;

/** Comfortably past one padding, where every measured cell is byte-identical. */
const CLEAR_GROUP_GAP = 88;

/** The shorter side of the toolbar's members, which is the span the law reads. */
const TOOLBAR_SPAN = 44;

/** What the derived default fixes: the two findings about the default itself. */
const DEFAULT_PADDING_CODES = [
  "sampling-padding-below-3-sigma",
  "merge-distance-below-effective-padding",
] as const;

const ALL_PADDING_CODES = [...DEFAULT_PADDING_CODES, "proxy-overlap-after-enforcement"] as const;

/**
 * The demo's shape: a toolbar group of two controls, a second group one gap to
 * its right, and a third well clear of both — so exactly one pair is close
 * enough for an overlap finding to be about.
 */
async function buildDemoShapedScene(
  page: Page,
  options: { readonly gap?: number; readonly declarePadding?: number } = {},
): Promise<void> {
  await page.evaluate(
    async ([gap, declared]) => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      // The pre-flip state is stated rather than inherited. Chromium answers
      // `prefers-reduced-transparency` from the operating system's own setting,
      // so on a machine where a person (or another harness) has it switched on,
      // every "before" frame here would already be the "after" — and since the
      // diagnostics channel dedupes by code and subjects, the findings would all
      // land before the clear and none of these tests would see anything.
      window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: false });
      const group = (id: string): void => {
        window.h.addGroup(
          id,
          declared === undefined ? {} : { samplingPadding: declared, mergeDistance: declared },
        );
      };

      group("toolbar");
      window.h.addSurface({ groupId: "toolbar", left: 200, top: 400, width: 96, height: 44 });
      window.h.addSurface({ groupId: "toolbar", left: 308, top: 400, width: 96, height: 44 });

      // The morph's own group, one gap to the right of the toolbar's right edge.
      group("toolbar-menu");
      window.h.addSurface({
        groupId: "toolbar-menu",
        left: 404 + (gap as number),
        top: 400,
        width: 110,
        height: 44,
      });

      // Far enough away to be nobody's neighbour, so the overlap count stays a
      // statement about the one pair that is.
      group("hero");
      window.h.addSurface({ groupId: "hero", left: 200, top: 120, width: 200, height: 120 });

      window.h.frame(3);
      // Everything before the flip is startup noise; what is under test is what
      // the one prop change produces.
      window.h.clearDiagnostics();
      window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: true });
      window.h.frame(3);
    },
    [options.gap ?? DEMO_GROUP_GAP, options.declarePadding] as const,
  );
}

const findingsOf = (page: Page, codes: readonly string[]): Promise<readonly string[]> =>
  page.evaluate(
    (wanted) =>
      window.h
        .diagnostics()
        .filter((entry) => (wanted as readonly string[]).includes(entry.code))
        .map((entry) => `${entry.code}(${entry.subjects.join(",")})`),
    codes,
  );

test("flipping reduced transparency stops warning about the default it chose itself", async ({
  page,
}) => {
  await gotoHarness(page);
  await buildDemoShapedScene(page);

  // Before this fix, one prop flip produced three
  // `sampling-padding-below-3-sigma` and three
  // `merge-distance-below-effective-padding` — six findings about a number no
  // app in the scene had written.
  expect(await findingsOf(page, DEFAULT_PADDING_CODES)).toEqual([]);
});

test("the seventh finding was a false positive, and the measurement is why it is gone", async ({
  page,
}) => {
  await gotoHarness(page);
  await buildDemoShapedScene(page);

  // 56px of gap against a 42px padding: the two padded boxes do intersect, but
  // only over a 28px strip outside both clips, which neither proxy paints into.
  // Rendered at exactly this σ and padding over a checkerboard and a photo-class
  // backdrop, the split and the single topology are byte-identical — the double
  // filtering the warning names does not happen here.
  expect(await findingsOf(page, ALL_PADDING_CODES)).toEqual([]);
});

test("and it still fires where the leak is real, under the very preference that grows it", async ({
  page,
}) => {
  await gotoHarness(page);
  // Close the gap to under one padding and the toolbar's box now covers the
  // menu group's own shapes. This is the conservatism that stays: the leak here
  // is small (single-digit /255) but real and paint-order dependent, and going
  // quiet about it under the preference that enlarged the blur would invert the
  // diagnostics doctrine.
  const { padding } = expectedProxyBlur({
    spanPx: TOOLBAR_SPAN,
    extentsCssPx: [96, 44],
    reducedTransparency: true,
  });
  expect(TIGHT_GROUP_GAP).toBeLessThan(padding);
  expect(DEMO_GROUP_GAP).toBeGreaterThan(padding);
  await buildDemoShapedScene(page, { gap: TIGHT_GROUP_GAP });

  expect(await findingsOf(page, ["proxy-overlap-after-enforcement"])).toEqual([
    "proxy-overlap-after-enforcement(toolbar,toolbar-menu)",
  ]);

  // And it goes when the layout gives it room — the advice it gives is the
  // advice that works.
  await buildDemoShapedScene(page, { gap: CLEAR_GROUP_GAP });
  expect(await findingsOf(page, ALL_PADDING_CODES)).toEqual([]);
});

test("the geometry really is at the floor, not merely unreported", async ({ page }) => {
  await gotoHarness(page);
  await buildDemoShapedScene(page);

  const boxes = await page.evaluate(() => ({
    toolbar: window.h.proxyBox("toolbar"),
    hero: window.h.proxyBox("hero"),
  }));

  // Under reduced transparency the frost multiplies σ, and the padding is 3σ at
  // each group's own widest member: 44 px for the toolbar's controls, 120 px
  // for the hero. The toolbar's members span 200..404 horizontally and 400..444
  // vertically.
  const toolbar = expectedProxyBlur({
    spanPx: TOOLBAR_SPAN,
    extentsCssPx: [96, 44],
    reducedTransparency: true,
  });
  const hero = expectedProxyBlur({
    spanPx: 120,
    extentsCssPx: [200, 120],
    reducedTransparency: true,
  });
  expect(hero.padding).toBeGreaterThan(toolbar.padding);
  expectBox(boxes.toolbar, paddedBox({ x: 200, y: 400, width: 204, height: 44 }, toolbar.padding));
  expectBox(boxes.hero, paddedBox({ x: 200, y: 120, width: 200, height: 120 }, hero.padding));
});

test("an author's own padding keeps their number, and keeps its warning", async ({ page }) => {
  await gotoHarness(page);
  // An author's own number is a statement about this app's geometry, and under a
  // blur it cannot cover it is still worth saying so. Deriving over the top of it
  // would be the runtime overruling an author, which is a different and worse
  // defect than the one being fixed.
  //
  // The declared number is taken from the floor rather than written down. It used
  // to be 24 with the assertion "24 is under the floor" beside it, and W12 G3
  // made that premise engine-dependent: the body's widths are device-pixel
  // quantities (claims §5.56), so under reduced transparency the toolbar's floor
  // is about 41 CSS px on a 1x context and about 21 on a 2x one — and WebKit's
  // Playwright descriptor composites at 2. A literal that is under the floor on
  // two engines and over it on the third tests the engines, not the runtime.
  const { padding } = expectedProxyBlur({
    spanPx: TOOLBAR_SPAN,
    extentsCssPx: [96, 44],
    reducedTransparency: true,
  });
  const declared = Math.max(1, Math.floor(padding) - 4);
  expect(declared).toBeLessThan(padding);
  await buildDemoShapedScene(page, { declarePadding: declared });

  const findings = await findingsOf(page, DEFAULT_PADDING_CODES);
  expect(findings).toContain("sampling-padding-below-3-sigma(toolbar)");
  expect(findings).toContain("merge-distance-below-effective-padding(toolbar)");
});

test("nothing moves at the nominal state, which is where every golden was taken", async ({
  page,
}) => {
  await gotoHarness(page);

  // The whole neutrality argument in one assertion: the derived default IS the
  // floor, 3σ at the group's own blur, so at the nominal state no group can sit
  // below it and nothing is raised or warned about. (When σ was the constant 8
  // this default was the constant 24 it replaced; the argument is the same, the
  // number now follows the law.)
  const result = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "webgpu", appDevice: true });
    // Nominal is stated, not inherited: the machine's own reduced-transparency
    // setting reaches Chromium's media query and would move σ under this test.
    window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: false });
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 200, top: 200, width: 140, height: 44 });
    window.h.frame(3);
    return { box: window.h.proxyBox("g"), codes: window.h.diagnosticCodes() };
  });

  const { padding } = expectedProxyBlur({
    extentsCssPx: [140, 44],
    spanPx: 44,
  });
  expectBox(result.box, paddedBox({ x: 200, y: 200, width: 140, height: 44 }, padding));
  for (const code of ALL_PADDING_CODES) expect(result.codes).not.toContain(code);
});
