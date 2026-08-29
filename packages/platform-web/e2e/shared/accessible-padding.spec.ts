/**
 * The library's own defaults, under the library's own accessibility mode.
 *
 * `samplingPadding` defaults to 24 and `mergeDistance` follows it. 24 is not an
 * arbitrary number — it is 3σ at the regular material's nominal blur of σ = 8,
 * which is exactly the floor `proxy-geometry.ts` enforces. The two agreed
 * because one was written from the other.
 *
 * They stop agreeing the moment an accessibility preference moves the blur.
 * `reducedTransparency` multiplies frost by 1.75, so σ becomes 14 and the floor
 * becomes 42 — and every group in the page that never declared a padding is
 * suddenly below a floor it was written to sit exactly on. A 0.1.1 consumer
 * flipped one prop and got seven warnings about geometry they had never
 * authored.
 *
 * Six of those seven were the default tripping the rule it was written from, and
 * they are what the derived default removes. The seventh — the cross-group
 * overlap warning at the demo's own 56px gap — was a false positive, and the
 * measurement that showed it is `spikes/s1-proxy-topology/overlap-experiment/`:
 * at σ = 14 and a 42px padding the two proxies are byte-identical whether they
 * are painted together or apart, because a proxy's box reaches its neighbour's
 * *painted* pixels only while the gap is under one padding. The check now says
 * that, so it still fires below one padding — where the leak is real — and stops
 * accusing a layout with 14px of clearance to spare.
 *
 * Playwright rather than jsdom: proxies exist only where members have measured
 * rects, and a jsdom test here would be asserting a stubbed layout.
 */

import { expect, test, type Page } from "@playwright/test";

import { gotoHarness } from "../support";

/** The playground's own gap between the toolbar group and the morph's group. */
const DEMO_GROUP_GAP = 56;

/**
 * A gap under the σ = 14 padding of 42, so one group's box covers the other's
 * shapes and the leak the warning names is really there — measured at up to
 * 3/255 around this separation, and larger as it closes further.
 */
const TIGHT_GROUP_GAP = 28;

/** Comfortably past one padding, where every measured cell is byte-identical. */
const CLEAR_GROUP_GAP = 88;

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

  // σ = 8 × 1.75 = 14 under reduced transparency, so the padding is 42. The
  // toolbar's members span 200..404 horizontally and 400..444 vertically.
  expect(boxes.toolbar).toEqual({ x: 158, y: 358, width: 288, height: 128 });
  expect(boxes.hero).toEqual({ x: 158, y: 78, width: 284, height: 204 });
});

test("an author's own padding keeps their number, and keeps its warning", async ({ page }) => {
  await gotoHarness(page);
  // A declared 24 is a statement about this app's geometry, and under a blur it
  // cannot cover it is still worth saying so. Deriving over the top of it would
  // be the runtime overruling an author, which is a different and worse defect
  // than the one being fixed.
  await buildDemoShapedScene(page, { declarePadding: 24 });

  const findings = await findingsOf(page, DEFAULT_PADDING_CODES);
  expect(findings).toContain("sampling-padding-below-3-sigma(toolbar)");
  expect(findings).toContain("merge-distance-below-effective-padding(toolbar)");
});

test("nothing moves at the nominal state, which is where every golden was taken", async ({
  page,
}) => {
  await gotoHarness(page);

  // The whole neutrality argument in one assertion: the derived default at the
  // nominal blur is 3 × 8 = 24, which is the constant it replaces. Not "close
  // to" — the same number, so every committed box stays byte-identical.
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

  expect(result.box).toEqual({ x: 176, y: 176, width: 188, height: 92 });
  for (const code of ALL_PADDING_CODES) expect(result.codes).not.toContain(code);
});
