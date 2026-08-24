import { expect, test } from "@playwright/test";

import { channelDelta, expectByteIdentical, gotoHarness, sample } from "../support";

/**
 * Pixel assertions — **Chromium only**, by the acceptance narrowing (Decision
 * Log #18). S1 measured Gecko and WebKit rendering `backdrop-filter` as a
 * complete no-op in every automatable capture path on this machine while
 * rendering it live, so a pixel assertion there would compare an unfiltered
 * scene against an unfiltered scene and pass for the wrong reason. The
 * `playwright.config.ts` projects enforce the split; this comment records why.
 *
 * The scene behind the glass is a 24px checkerboard: a starved blur only goes
 * visibly wrong where the content near a shape edge is busy, so a flat ground
 * would hide the property under test.
 */
test.describe("the padded proxy actually filters, and never leaks", () => {
  test.beforeEach(async ({ page }) => {
    await gotoHarness(page);
    await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g", { samplingPadding: 40, mergeDistance: 40 });
      window.h.addSurface({
        groupId: "g",
        nodeId: "panel",
        left: 300,
        top: 200,
        width: 200,
        height: 120,
        radius: 24,
      });
      window.h.frame(3);
    });
  });

  test("changes the pixels inside its mask", async ({ page }) => {
    // S1 impact item 6: assert that a padded proxy differs from the unfiltered
    // scene, so a *silently dropped* filter fails the suite instead of quietly
    // changing the baselines. Headless Chromium drops it above ~1.75 Mpx of
    // device-pixel proxy area, and it fails without a word.
    const clip = { x: 300, y: 200, width: 200, height: 120 };

    const filtered = await sample(page, clip);
    await page.evaluate(() => window.h.setProxiesVisible(false));
    const unfiltered = await sample(page, clip);

    // Sample well inside the shape, away from the corner radii.
    const points = [
      [100, 60],
      [60, 40],
      [140, 80],
    ] as const;
    const deltas = points.map(([x, y]) => channelDelta(filtered.at(x, y), unfiltered.at(x, y)));

    expect(Math.max(...deltas), `interior deltas were ${deltas.join(", ")}`).toBeGreaterThan(8);
  });

  test("leaves the padding ring byte-identical — the mask is the shape, not the box", async ({
    page,
  }) => {
    // Read literally, "masked to the union of member shapes + samplingPadding"
    // produces a 40%-strength blurred rectangle standing proud of the glass:
    // S1 measured GAP mean 102.92/255 for exactly that mistake. The box carries
    // the padding; the mask does not.
    const box = await page.evaluate(() => window.h.proxyBox("g"));
    expect(box).toEqual({ x: 260, y: 160, width: 280, height: 200 });

    const clip = { x: 260, y: 160, width: 280, height: 200 };
    const filtered = await sample(page, clip);
    await page.evaluate(() => window.h.setProxiesVisible(false));
    const unfiltered = await sample(page, clip);

    // Points inside the padded box but outside the shape: the top-left corner of
    // the ring, the mid-left of the ring, and just above the shape.
    for (const [x, y] of [
      [8, 8],
      [20, 100],
      [140, 12],
      [272, 192],
    ] as const) {
      expectByteIdentical(
        filtered.at(x, y),
        unfiltered.at(x, y),
        `padding ring at (${x}, ${y})`,
      );
    }
  });

  test("leaves the page outside the proxy box byte-identical", async ({ page }) => {
    const clip = { x: 40, y: 40, width: 160, height: 100 };
    const filtered = await sample(page, clip);
    await page.evaluate(() => window.h.setProxiesVisible(false));
    const unfiltered = await sample(page, clip);

    for (const [x, y] of [
      [10, 10],
      [80, 50],
      [150, 90],
    ] as const) {
      expectByteIdentical(filtered.at(x, y), unfiltered.at(x, y), `outside the box at (${x}, ${y})`);
    }
  });

  test("keeps the semantic label above the glass body", async ({ page }) => {
    // The sandwich's whole point: the optics layer is below the host DOM, so a
    // label is never blurred by its own surface's material.
    const text = await page.evaluate(() => {
      const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
      const proxy = document.querySelector<HTMLElement>('[data-vitrea-proxy="g"]');
      if (host === null || proxy === null) return undefined;
      const stack = document.elementsFromPoint(400, 260);
      return {
        topIsHost: stack[0] === host,
        proxyBelow: stack.indexOf(proxy),
        hostFilter: getComputedStyle(host).backdropFilter,
      };
    });

    expect(text?.topIsHost).toBe(true);
    // The proxy is not in the hit-test stack at all.
    expect(text?.proxyBelow).toBe(-1);
  });
});

test.describe("proxy construction, isolated from tier resolution", () => {
  test("a 3σ-padded proxy matches an over-padded one at the shape edge", async ({ page }) => {
    // S1's padding sweep: distance from an unstarvable proxy is byte-exact at
    // 3σ and within 0.2/255 mean at 2σ. This is the same measurement, reduced to
    // the one comparison worth regressing: the shipped floor against generous
    // padding, sampled where a starved blur goes wrong — the shape edge.
    await gotoHarness(page);

    const readEdge = async (padding: number) => {
      await page.evaluate(
        async (pad) => {
          window.h.reset();
          window.h.mountProxies([
            {
              groupId: "solo",
              plane: "base",
              order: 0,
              members: [
                {
                  nodeId: "n",
                  bounds: { x: 300, y: 200, width: 200, height: 120 },
                  radii: [24, 24, 24, 24],
                },
              ],
              samplingPadding: pad,
              mergeDistance: pad,
            },
          ]);
        },
        padding,
      );
      return sample(page, { x: 300, y: 200, width: 200, height: 120 });
    };

    const atFloor = await readEdge(24);
    const generous = await readEdge(120);

    // A 6px inset band all round the shape: this is the band that in-place
    // filtering gets wrong by up to 66/255, and where padding has to fix it.
    const edgePoints = [
      [6, 6],
      [100, 4],
      [194, 60],
      [100, 116],
      [4, 60],
    ] as const;

    for (const [x, y] of edgePoints) {
      expect(
        channelDelta(atFloor.at(x, y), generous.at(x, y)),
        `edge band at (${x}, ${y}) should agree between 3σ and generous padding`,
      ).toBeLessThanOrEqual(2);
    }
  });

  test("a proxy over the area cap is reported rather than silently dropped", async ({ page }) => {
    await gotoHarness(page);

    const result = await page.evaluate(() => {
      window.h.mountProxies([
        {
          groupId: "huge",
          plane: "base",
          order: 0,
          members: [
            {
              nodeId: "n",
              bounds: { x: 0, y: 0, width: 1200, height: 700 },
              radii: [0, 0, 0, 0],
            },
          ],
          samplingPadding: 400,
          mergeDistance: 400,
        },
      ]);
      return {
        codes: window.h.diagnosticCodes(),
        box: window.h.proxyBox("huge"),
      };
    });

    expect(result.codes).toContain("proxy-area-over-cap");
    // Trimmed, not abandoned: the padding never goes below 3σ, because a starved
    // blur is a visible artifact at every edge while an over-cap proxy is a
    // hazard on one rasteriser.
    expect(result.box?.width).toBeLessThan(1200 + 800);
    expect(result.box?.width).toBeGreaterThanOrEqual(1200 + 48);
  });
});
