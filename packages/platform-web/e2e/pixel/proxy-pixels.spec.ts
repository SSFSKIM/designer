import { expect, test, type Page } from "@playwright/test";

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

/**
 * Presence on the DOM proxy (W27d, contract X6).
 *
 * The gap this closes is only visible in pixels. On the WebGPU tier the shader
 * can take a surface's optics to nothing, and until this landed the group's
 * proxy — a sibling element, one per group per plane — went on filtering the
 * page underneath it, so `Glass.identity` left a blurred rectangle standing
 * exactly where the glass was supposed to have gone. Nothing in a unit test can
 * see that, because the filter is the one thing no in-page readback path can
 * observe (S1's Q5).
 *
 * Driven through `mountProxies` rather than through a registered group: the
 * question is what the proxy does with a presence, and the standalone mount is
 * the one path that asks it without a tier resolution in between.
 */
test.describe("presence attenuates the proxy, member by member", () => {
  /** The first member's box, and the sample points well inside its radii. */
  const FIRST = { x: 200, y: 200, width: 200, height: 120 };
  /** The second member's, 200px of clear ground away — no shared padding. */
  const SECOND = { x: 600, y: 200, width: 200, height: 120 };
  /** The padding ring to the left of the first member: sampled, never painted. */
  const RING = { x: 160, y: 160, width: 40, height: 200 };
  const INSIDE = [
    [100, 60],
    [60, 40],
    [140, 80],
  ] as const;

  /**
   * `"yes"` is Chromium's own conformance row (claims §5.71 §1), which is the
   * engine these assertions run on; the tests below that name `"unverified"` are
   * asserting the fallback every other engine takes.
   */
  const mount = async (
    page: Page,
    alphas: readonly number[],
    mask: "yes" | "unverified" = "yes",
  ): Promise<void> => {
    await page.evaluate(
      ({ values, maskRow }) => {
        window.h.reset();
        window.h.mountProxies(
          [
            {
              groupId: "presence",
              plane: "base",
              order: 0,
              members: values.map((materialization, index) => ({
                nodeId: `n${index}`,
                bounds: { x: 200 + index * 400, y: 200, width: 200, height: 120 },
                radii: [24, 24, 24, 24] as const,
                materialization,
              })),
              samplingPadding: 40,
              mergeDistance: 40,
            },
          ],
          maskRow,
        );
      },
      { values: alphas, maskRow: mask },
    );
  };

  /** The scene with the proxy layer taken out of the picture altogether. */
  const withoutProxies = async (page: Page, clip: typeof FIRST) => {
    await page.evaluate(() => window.h.setProxiesVisible(false));
    return sample(page, clip);
  };

  test("filters at 1 and leaves the page exactly as it found it at 0", async ({ page }) => {
    await gotoHarness(page);

    await mount(page, [1]);
    const whole = await sample(page, FIRST);
    await mount(page, [0]);
    const gone = await sample(page, FIRST);
    const unfiltered = await withoutProxies(page, FIRST);

    for (const [x, y] of INSIDE) {
      expect(
        channelDelta(whole.at(x, y), unfiltered.at(x, y)),
        `a fully present proxy should still filter at (${x}, ${y})`,
      ).toBeGreaterThan(8);
      // Not "close to": a dematerialized surface has to leave *no* trace, which
      // is what makes `Glass.identity` identity rather than a faint frost.
      expectByteIdentical(gone.at(x, y), unfiltered.at(x, y), `presence 0 at (${x}, ${y})`);
    }
  });

  test("lands between the endpoints in transit", async ({ page }) => {
    await gotoHarness(page);

    await mount(page, [1]);
    const whole = await sample(page, FIRST);
    await mount(page, [0.5]);
    const half = await sample(page, FIRST);
    const unfiltered = await withoutProxies(page, FIRST);

    const fromGround = (at: typeof whole): number =>
      Math.max(...INSIDE.map(([x, y]) => channelDelta(at.at(x, y), unfiltered.at(x, y))));

    const full = fromGround(whole);
    const partial = fromGround(half);

    expect(partial, `half presence measured ${partial}/255 from the ground`).toBeGreaterThan(0);
    expect(partial, `half presence measured ${partial} against ${full} at full`).toBeLessThan(full);
  });

  test("fades one member without touching its neighbour", async ({ page }) => {
    // The property the mask carrier exists for. A member at 0 must not blank a
    // member at 1, and — the half that is easy to lose — putting the carrier on
    // the element must not disturb the member that never faded.
    await gotoHarness(page);

    await mount(page, [1, 1]);
    const bothWhole = await sample(page, FIRST);
    const neighbourWhole = await sample(page, SECOND);

    await mount(page, [1, 0]);
    const stillWhole = await sample(page, FIRST);
    const faded = await sample(page, SECOND);
    // The mask is the silhouette here, so the property the clip path used to hold
    // has to hold through it: nothing filters outside the member shapes.
    const ring = await sample(page, RING);

    const unfilteredRing = await withoutProxies(page, RING);
    const unfiltered = await sample(page, SECOND);

    for (const [x, y] of INSIDE) {
      expectByteIdentical(
        stillWhole.at(x, y),
        bothWhole.at(x, y),
        `the member that never faded, at (${x}, ${y})`,
      );
      expectByteIdentical(faded.at(x, y), unfiltered.at(x, y), `the faded member at (${x}, ${y})`);
      // And the neighbour was genuinely filtered before, so the line above is a
      // statement about presence and not about a proxy that never drew.
      expect(channelDelta(neighbourWhole.at(x, y), unfiltered.at(x, y))).toBeGreaterThan(8);
    }

    for (const [x, y] of [
      [8, 8],
      [20, 100],
      [8, 190],
    ] as const) {
      expectByteIdentical(
        ring.at(x, y),
        unfilteredRing.at(x, y),
        `the padding ring under the mask carrier at (${x}, ${y})`,
      );
    }
  });

  test("reaches the same zero where a mask on a filtered layer is unverified", async ({ page }) => {
    // The fallback the other two engines take. Dropping the clip path for a mask
    // they might ignore would leave the padded box filtering at full strength —
    // S1's 102.92/255 halo — so a disagreeing group reduces to one alpha there.
    // What that reduction may *not* do is hold a dematerialized member at the
    // group's presence, so absence is carried by the painted shape instead and
    // this endpoint is the same on every engine.
    await gotoHarness(page);

    await mount(page, [1, 1], "unverified");
    const neighbourWhole = await sample(page, FIRST);

    await mount(page, [1, 0], "unverified");
    const neighbour = await sample(page, FIRST);
    const faded = await sample(page, SECOND);
    const ring = await sample(page, RING);

    const unfilteredSecond = await withoutProxies(page, SECOND);
    const unfilteredRing = await sample(page, RING);

    for (const [x, y] of INSIDE) {
      expectByteIdentical(faded.at(x, y), unfilteredSecond.at(x, y), `the 0 member at (${x}, ${y})`);
      expectByteIdentical(
        neighbour.at(x, y),
        neighbourWhole.at(x, y),
        `the member at 1 beside it, at (${x}, ${y})`,
      );
    }
    for (const [x, y] of [
      [8, 8],
      [20, 100],
      [8, 190],
    ] as const) {
      expectByteIdentical(ring.at(x, y), unfilteredRing.at(x, y), `the padding ring at (${x}, ${y})`);
    }
  });
});
