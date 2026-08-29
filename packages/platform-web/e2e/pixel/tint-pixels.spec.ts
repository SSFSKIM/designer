import { expect, test, type Page } from "@playwright/test";

import { channelDelta, gotoHarness, sample } from "../support";

/**
 * The author tint, in pixels, on the CSS tier.
 *
 * Everything else about the tint is arithmetic and is unit-tested as arithmetic.
 * What only a browser can answer is whether the result is still *glass*: a flat
 * fill is the failure Apple names, and the difference between a tint and a fill
 * is visible exactly where a unit test cannot look — in whether the backdrop is
 * still coming through the surface after the colour lands on it.
 *
 * So the assertions here are about relationships between sampled pixels rather
 * than about any particular colour. No constant in the tone map is measured yet;
 * the tinted-capture extension is what will fit them, and none of these tests
 * would have to change when it does.
 */
test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

const PANEL = { x: 300, y: 200, width: 220, height: 120 };

/**
 * Two surfaces over the same backdrop in one group, one tinted and one not.
 *
 * The pair is the point: it is the composition Apple's guidance describes (one
 * emphasised control among plain ones) and the one that proves tint strength is
 * a per-surface quantity rather than a property of the whole optics pass.
 */
const buildPair = async (page: Page, tint: string): Promise<void> => {
  await page.evaluate(async (colour) => {
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
      tint: colour,
    });
    window.h.addSurface({
      groupId: "g",
      nodeId: "plain",
      left: 300,
      top: 360,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
    });
    window.h.frame(3);
  }, tint);
};

const PLAIN = { x: 300, y: 360, width: 220, height: 120 };

test("colours the surface it is set on, and only that one", async ({ page }) => {
  await buildPair(page, "#ff9500");

  const tinted = (await sample(page, PANEL)).at(110, 60);
  const plain = (await sample(page, PLAIN)).at(110, 60);

  // Warmth rather than absolute channels: the harness page's own backdrop is not
  // neutral, so what a tint has to do is *add* warmth over whatever was there,
  // and what its neighbour has to do is not gain any.
  const warmth = (pixel: { r: number; b: number }): number => pixel.r - pixel.b;
  expect(warmth(tinted)).toBeGreaterThan(warmth(plain) + 40);

  // And the declarations agree: one surface's tint moved, the other's did not.
  const declared = await page.evaluate(() =>
    ["panel", "plain"].map(
      (id) =>
        document
          .querySelector<HTMLElement>(`[data-vitrea-node="${id}"]`)
          ?.style.getPropertyValue("--vitrea-tint") ?? "",
    ),
  );
  expect(declared[0]).not.toBe(declared[1]);
  expect(declared[1]).toContain("255, 255, 255");
});

test("stays glass — the backdrop still varies through a tinted surface", async ({ page }) => {
  // The whole claim, in one assertion. A solid fill is constant across the
  // surface whatever is behind it; a tint modulates a backdrop that is still
  // being transmitted, so two points over different backdrop content must still
  // differ. The harness page's backdrop is patterned, which is what makes this
  // measurable at all.
  await buildPair(page, "#ff9500");
  const tinted = await sample(page, PANEL);

  const points = ([
    [30, 30],
    [110, 60],
    [190, 90],
    [190, 30],
  ] as const).map(([x, y]) => tinted.at(x, y));

  const spread = Math.max(
    ...points.map((point) => Math.max(...points.map((other) => channelDelta(point, other)))),
  );
  expect(spread, "a tinted surface that varies nowhere is a fill, not a tint").toBeGreaterThan(2);
});

test("a half-strength tint lands between the untinted material and the full one", async ({
  page,
}) => {
  // The strength axis, end to end: the author writes it as the colour's alpha,
  // and it moves the material's tint colour rather than its opacity.
  const centreFor = async (tint: string | undefined): Promise<{ r: number; b: number }> => {
    await page.evaluate(async (colour) => {
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
        ...(colour === undefined ? {} : { tint: colour }),
      });
      window.h.frame(3);
    }, tint);
    return (await sample(page, PANEL)).at(110, 60);
  };

  const plain = await centreFor(undefined);
  const half = await centreFor("rgb(255 149 0 / 50%)");
  const full = await centreFor("#ff9500");

  const warmth = (pixel: { r: number; b: number }): number => pixel.r - pixel.b;
  expect(warmth(half)).toBeGreaterThan(warmth(plain));
  expect(warmth(full)).toBeGreaterThan(warmth(half));
});

test("keeps its declared opacity — a tint changes the colour, never the occlusion", async ({
  page,
}) => {
  const occlusionFor = async (tint: string | undefined): Promise<string | undefined> => {
    await page.evaluate(async (colour) => {
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
        ...(colour === undefined ? {} : { tint: colour }),
      });
      window.h.frame(3);
    }, tint);
    return page.evaluate(() => {
      const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
      return host?.style.getPropertyValue("--vitrea-blur");
    });
  };

  // The blur is the material's, not the tint's: whatever the conversion does to
  // the alpha to reproduce the renderer's composite, it must not touch the frost.
  expect(await occlusionFor("#ff9500")).toBe(await occlusionFor(undefined));
});

test("gives up the tint entirely under forced colours", async ({ page }) => {
  // The accessibility policy that removes the material removes the colour with
  // it: there is no glass to tint, and the palette is the platform's.
  await page.emulateMedia({ forcedColors: "active" });
  await buildPair(page, "#ff9500");

  const style = await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    return {
      tint: host?.style.getPropertyValue("--vitrea-tint"),
      ink: host?.style.getPropertyValue("--vitrea-foreground"),
    };
  });

  expect(style.tint).toBe("Canvas");
  expect(style.ink).toBe("CanvasText");

  // And the surface is flat, which is what "no glass" means in pixels.
  const panel = await sample(page, PANEL);
  expect(channelDelta(panel.at(110, 60), panel.at(40, 30))).toBe(0);
});

test("refuses a colour it cannot parse, and says so rather than inventing one", async ({
  page,
}) => {
  const findings = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css", devMode: true });
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
      tint: "definitely-not-a-colour",
    });
    window.h.frame(3);
    return window.h.diagnosticCodes();
  });

  expect(findings).toContain("tint-unparseable");

  // A browser parses everything else, including the keywords a numeric-only
  // parser would have had to refuse.
  await buildPair(page, "rebeccapurple");
  const tinted = (await sample(page, PANEL)).at(110, 60);
  expect(tinted.b).toBeGreaterThan(tinted.g + 10);
});
