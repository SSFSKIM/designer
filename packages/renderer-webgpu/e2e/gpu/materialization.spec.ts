/**
 * W27d — the presence channel, on a real adapter.
 *
 * This is the first proof that any MOTION channel reaches the WebGPU tier's
 * shaders as pixels. Every other channel is pinned on the CPU — the instance
 * buffer's bytes, the uniform's slots — and the shader that reads them is checked
 * as a string, which says the arithmetic is written and not that it runs. A
 * channel can be packed, bound, and still drop out at any of the seams between:
 * an attachment the pipeline does not declare, a target the field pass does not
 * write, a binding the optics pass does not read. Differencing one scene against
 * itself at two presences is what closes all of them at once.
 *
 * Two claims, and they are opposite claims:
 *
 *  - **At 0.35 the material is visibly different** — `maxChannelDelta > 8`, well
 *    past the 4-code tolerance the golden suite calls a rounding difference.
 *  - **At exactly 1 nothing moved.** Byte-identical to the scene drawn with no
 *    channel driven at all, which is the golden bed's own claim stated on the
 *    pixels rather than inferred from the arithmetic.
 *
 * What it measures on this machine's `apple / metal-3` adapter, against the same
 * scene at presence 1 — max channel delta, mean, and the fraction of pixels past
 * eight codes:
 *
 * | presence | max | mean | past 8 |
 * | --- | --- | --- | --- |
 * | 0.70 | 42 | 5.06 | 0.257 |
 * | 0.35 | 86 | 11.96 | 0.477 |
 * | 1e-6 | 235 | 29.67 | 0.660 |
 * | 0    | 255 | 88.27 | 0.672 |
 *
 * The last two rows are the endpoint and the step into it: at a millionth the
 * material is gone and the silhouette is whole, and at 0 the silhouette goes
 * too — which is the whole of the difference between those rows.
 *
 * The bounds asserted below are far under those, on the golden suite's own
 * argument: what is being pinned is that the channel reaches the pixels, and a
 * bound at the measured value would fail on the next material change for a
 * reason that has nothing to do with presence.
 *
 * The ENDPOINT is a different claim and a stronger one. Exactly 0 is
 * `Glass.identity` — the member leaves the group before the field pass, so the
 * render is byte-identical to a scene that never had the surface, and a group of
 * nothing but absent members draws nothing at all. One absent member of a
 * connected group leaves its neighbour the group it would have had alone, which
 * is the case a `GlassMorph` materialize transition puts on screen: a dissolving
 * source must not go on bending its destination's contour.
 *
 * **Two things are recorded here and deliberately not asserted**, because they
 * are properties of the mechanism this tier happens to use rather than contracts
 * a correct implementation has to keep. At a presence of a millionth the surface
 * still owns its whole silhouette at full canvas alpha and still grows its whole
 * neck toward a present neighbour — so the union's bulge is discontinuous at the
 * endpoint, and a low-presence member in an overlapping region still owns the
 * nearest field there. Whether that residual is closed, and how, is above this
 * package; a passing test asserting it would make the residual a requirement.
 *
 * The channel never touches `opacity`: there is no DOM in this package to touch,
 * and the host's half of contract X6 is asserted where the host lives. What is
 * here is the other half — that between the endpoints the material's optical
 * terms are what carry the transition, so a surface at 0.35 is a different
 * material rather than the same one at a lower opacity.
 */

import { createHash } from "node:crypto";
import { expect, test, type Page } from "@playwright/test";

import {
  assertNotBlank,
  compare,
  decodeCapture,
  openHarness,
  requireHardwareAdapter,
  type Raster,
} from "../support";

/**
 * The scene: a surface over a checkerboard texture, which is the backdrop every
 * term the channel scales is legible on. The lens bends the squares, the body
 * blurs them, the tint sits over them and the rim rides the contour — a flat
 * backdrop would hide the first two of those.
 */
const SCENE = "refraction-checkerboard";

/** One scene, one set of render options, one material profile. */
const render = async (
  page: Page,
  scene: string,
  options: Record<string, unknown>,
  materialProfile?: Record<string, unknown>,
): Promise<Raster> =>
  decodeCapture(
    await page.evaluate(
      (args) =>
        window.vitrea.renderScene(
          args.scene,
          undefined,
          args.materialProfile as never,
          args.options as never,
        ),
      { scene, options, materialProfile },
    ),
  );

const hashOf = (raster: Raster): string =>
  createHash("sha256").update(raster.data).digest("hex").slice(0, 32);

/** A half-open box in DEVICE pixels. */
interface Box {
  readonly x0: number;
  readonly y0: number;
  readonly x1: number;
  readonly y1: number;
}

/** The largest and mean channel difference inside a box. */
function boxDelta(a: Raster, b: Raster, box: Box): { max: number; mean: number } {
  let max = 0;
  let sum = 0;
  let n = 0;
  for (let y = box.y0; y < box.y1; y += 1) {
    for (let x = box.x0; x < box.x1; x += 1) {
      for (let c = 0; c < 4; c += 1) {
        const i = (y * a.width + x) * 4 + c;
        const delta = Math.abs((a.data[i] ?? 0) - (b.data[i] ?? 0));
        if (delta > max) max = delta;
        sum += delta;
        n += 1;
      }
    }
  }
  return { max, mean: n === 0 ? 0 : sum / n };
}

/** The largest alpha anywhere OUTSIDE a box — what a surface leaves on the page. */
function maxAlphaOutside(raster: Raster, box: Box): number {
  let max = 0;
  for (let y = 0; y < raster.height; y += 1) {
    for (let x = 0; x < raster.width; x += 1) {
      if (x >= box.x0 && x < box.x1 && y >= box.y0 && y < box.y1) continue;
      const alpha = raster.data[(y * raster.width + x) * 4 + 3] ?? 0;
      if (alpha > max) max = alpha;
    }
  }
  return max;
}

test.describe("@gpu W27d presence reaches the shader", () => {
  test("a surface at 0.35 draws a different material from the same surface at 1", async ({
    page,
  }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const present = await render(page, SCENE, { materialization: 1 });
    const partial = await render(page, SCENE, { materialization: 0.35 });

    const difference = compare(present, partial, 8);
    expect(
      difference.maxChannelDelta,
      `${SCENE}: presence 0.35 against presence 1`,
    ).toBeGreaterThan(8);
    // And it is the material that moved rather than a stray pixel: the channel
    // scales the lens, the body, the alpha, the rim and both shadows, so a
    // measurable fraction of the surface has to move with it.
    expect(difference.outlierFraction, `${SCENE}: pixels past 8 codes`).toBeGreaterThan(0.01);
  });

  test("the channel is monotone: 0 moves at least as far as 0.35", async ({ page }) => {
    // `Glass.identity` is the end of the same ramp `.materialize` runs, not a
    // separate state, so the material cannot come back on the way to absent.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const present = await render(page, SCENE, { materialization: 1 });
    const partial = await render(page, SCENE, { materialization: 0.35 });
    const absent = await render(page, SCENE, { materialization: 0 });

    expect(compare(absent, present, 8).maxChannelDelta).toBeGreaterThanOrEqual(
      compare(partial, present, 8).maxChannelDelta,
    );
    expect(compare(absent, present, 8).meanChannelDelta).toBeGreaterThan(
      compare(partial, present, 8).meanChannelDelta,
    );
  });

  test("driving the channel to 1 renders the bytes of a scene nobody drove", async ({ page }) => {
    // The byte-identity the whole wave rests on, measured rather than argued: at
    // presence 1 every term the channel multiplies is a multiplication by exactly
    // one and the extra backdrop tap is not taken at all, so the resting material
    // — and every golden in `e2e/goldens/` — is the material that had no channel.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const undriven = await render(page, SCENE, {});
    const driven = await render(page, SCENE, { materialization: 1 });

    expect(hashOf(driven)).toBe(hashOf(undriven));
  });
});

/** Excludes nothing, so `maxAlphaOutside` reads the whole raster. */
const EMPTY_BOX: Box = { x0: 0, y0: 0, x1: 0, y1: 0 };

test.describe("@gpu W27d the identity endpoint", () => {
  test("at 0 the surface is not there at all", async ({ page }) => {
    /*
     * `Glass.identity`, exactly: a surface at presence 0 is dropped before the
     * field pass, so the render is the render of a scene that never had it —
     * byte for byte, not to a tolerance. Nothing is left to argue about: no
     * silhouette, no shadow, no resampled copy of the backdrop standing in for
     * the page it is over.
     *
     * That is a stronger claim than "every optical term multiplied by zero", and
     * it is stronger in the way that matters: a material scaled to nothing would
     * still have OWNED its pixels, and the honesty of the endpoint would then
     * depend on how faithfully the group's own backdrop sample reproduced what
     * was already behind it.
     */
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const absent = await render(page, SCENE, { materialization: 0 });
    const noSurface = await render(page, SCENE, { omitNodes: ["s"] });

    expect(hashOf(absent)).toBe(hashOf(noSurface));
    // Nothing anywhere on the canvas: the group's only member is gone, so the
    // group is skipped and the plane is what the page will show. `EMPTY_BOX`
    // excludes nothing, so this reads the whole raster.
    expect(maxAlphaOutside(absent, EMPTY_BOX)).toBe(0);

    // The scene draws something when the surface is present — without this the
    // identity above would hold for a harness that had stopped rendering.
    const present = await render(page, SCENE, { materialization: 1 });
    expect(maxAlphaOutside(present, EMPTY_BOX)).toBeGreaterThan(0);
  });

});

/*
 * `union-pair`: two 64 × 52 CSS surfaces at x 72 and x 128, overlapping by 8 CSS
 * px, in one group over a gradient — the scene the bounded smooth union is
 * pinned on. At DPR 2 `A_SIDE` is the part of the canvas the left member owns,
 * short of the seam the two grow between them.
 */
const A_SIDE: Box = { x0: 80, y0: 68, x1: 190, y1: 172 };

test.describe("@gpu W27d one absent member of a connected group", () => {
  test("leaves its present neighbour the group it would have had alone", async ({ page }) => {
    /*
     * The case a materialize transition puts on screen: a `GlassMorph`'s source
     * and its destination are alive at once, in one group, close enough to grow a
     * neck. The arriving surface must draw what it would have drawn alone — not a
     * contour bent toward a surface that is no longer there, and not a neck to
     * nothing.
     *
     * Byte-identical rather than close, because the member leaves the group
     * before the field pass: the same instance buffer, the same field rect, the
     * same pixels. There is no seam left for a tolerance to hide in.
     */
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const withAbsent = await render(page, "union-pair", { materializationByNode: { a: 0 } });
    const alone = await render(page, "union-pair", { omitNodes: ["a"] });

    expect(hashOf(withAbsent)).toBe(hashOf(alone));
    // Nothing of `a` is drawn — no silhouette of its own and no bulge toward it.
    expect(boxDelta(withAbsent, alone, A_SIDE).max).toBe(0);
    // And `b` is: an identity between two blank canvases would prove nothing.
    assertNotBlank(withAbsent, "union-pair with an absent member");
  });

});
