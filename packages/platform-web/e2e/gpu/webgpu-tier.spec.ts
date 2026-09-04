/**
 * The GPU tier, end to end, against a real adapter.
 *
 * Every other suite in this package can be true with nothing drawing: the
 * proxies, the probe, the plane sandwich and the read meter are all observable
 * without a renderer, and were, for as long as `renderer: "webgpu"` reached a
 * device and stopped there. This file is the one that cannot.
 *
 * What it asserts, and why each one is the honest mechanism:
 *
 *  - **Acceptance #2.** The optics canvas — the renderer's own canvas, read back
 *    directly — carries non-transparent pixels over a texture-backed group. A
 *    page screenshot would flatten alpha away, and "painted transparent black"
 *    and "painted nothing" are the same pixel once composited, so the alpha
 *    channel is the whole question.
 *  - **X7.** A session that asks for WebGPU and gets it fetches the renderer
 *    module; the CSS-tier half of that claim is in `e2e/shared`, where it holds
 *    on every engine.
 *  - **Acceptance #5, on the recoverable side.** Losing the device swaps the
 *    tier visibly — the GPU canvas stops carrying the surface and the host picks
 *    up the CSS tier's own declarations — and a fresh root draws again.
 *
 * **Every scene steps its frames and reads its pixels inside one
 * `page.evaluate`.** A WebGPU canvas can only be snapshotted while the texture
 * it drew into is still current: once the frame is presented, every readback
 * path hands back a fully transparent image over a canvas the page is visibly
 * still showing. Splitting the draw and the read across two evaluates therefore
 * produces a confident, wrong zero — which is exactly the failure a suite like
 * this exists to avoid, so the constraint is structural rather than advisory.
 *
 * The gate fails rather than skips on a software adapter, for C6's reason: a
 * GPU tier verified on a CPU rasteriser is not the thing acceptance #2 asks
 * about, and a suite that silently passes proves less than one that is not run.
 */

import { expect, test } from "@playwright/test";

import { gotoHarness, requireHardwareAdapter } from "../support";

const PLATE = { x: 300, y: 200, width: 260, height: 140 };

/** Away from the plate: the control that keeps "painted" from meaning "opaque". */
const EMPTY = { x: 20, y: 20, width: 80, height: 80 };

test.describe("the WebGPU tier draws", () => {
  test("paints the optics canvas over a texture-backed group", async ({ page }) => {
    await gotoHarness(page);
    requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

    const result = await page.evaluate(
      async ([plate, empty]) => {
        await window.h.createRoot({ renderer: "webgpu" });
        window.h.addTextureGroup({ groupId: "gpu", sourceId: "gpu.canvas" });
        window.h.addSurface({
          groupId: "gpu",
          nodeId: "plate",
          left: plate.x,
          top: plate.y,
          width: plate.width,
          height: plate.height,
          radius: 26,
          label: "",
        });
        // Three frames: the first measures, the second has a rect to draw from,
        // and the third is a steady state rather than a first frame.
        window.h.frame(3);

        return {
          state: window.h.capabilities("gpu"),
          active: window.h.rendererActive(),
          plate: window.h.canvasPixels("optics-canvas", "base", plate),
          empty: window.h.canvasPixels("optics-canvas", "base", empty),
        };
      },
      [PLATE, EMPTY] as const,
    );

    expect(result.state?.activeRenderer, `resolved state ${JSON.stringify(result.state)}`).toBe(
      "webgpu",
    );
    expect(result.state?.samplingBackend).toBe("gpu-texture");
    expect(result.state?.health).toBe("ok");
    expect(result.active, "the bridge reported no live renderer").toBe(true);

    // Most of the plate's area, not a stray pixel: a rim-only draw would leave
    // this near zero while a real body fills it.
    expect(
      result.plate.painted,
      `painted fraction ${result.plate.painted}, peak ${result.plate.peak.join(",")}`,
    ).toBeGreaterThan(0.5);
    expect(result.plate.maxAlpha, `max alpha ${result.plate.maxAlpha}`).toBeGreaterThan(16);

    // The control. Without it the assertion above would pass just as happily for
    // a canvas that is opaque everywhere, which is not glass.
    expect(
      result.empty.painted,
      `an empty region reported ${result.empty.painted} painted`,
    ).toBeLessThan(0.02);
  });

  test("fetches the renderer module where WebGPU was asked for and had", async ({ page }) => {
    // X7 from the other side. The CSS-tier half — that a css root fetches
    // nothing — is in e2e/shared, because it is true on every engine.
    const requested: string[] = [];
    page.on("request", (request) => requested.push(request.url()));

    await gotoHarness(page);
    requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

    await page.evaluate(async (plate) => {
      await window.h.createRoot({ renderer: "webgpu" });
      window.h.addTextureGroup({ groupId: "gpu", sourceId: "gpu.canvas" });
      window.h.addSurface({
        groupId: "gpu",
        left: plate.x,
        top: plate.y,
        width: plate.width,
        height: plate.height,
      });
      window.h.frame(3);
    }, PLATE);

    expect(
      requested.filter((url) => url.includes("renderer-webgpu")).length,
      "the renderer module was never fetched",
    ).toBeGreaterThan(0);
  });
});

test.describe("device loss swaps the tier and recovers", () => {
  test("stops drawing and hands the surface to the CSS tier", async ({ page }) => {
    await gotoHarness(page);
    requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

    const result = await page.evaluate(async (plate) => {
      await window.h.createRoot({ renderer: "webgpu" });
      window.h.addTextureGroup({ groupId: "gpu", sourceId: "gpu.canvas" });
      window.h.addSurface({
        groupId: "gpu",
        nodeId: "plate",
        left: plate.x,
        top: plate.y,
        width: plate.width,
        height: plate.height,
        radius: 26,
        label: "",
      });
      window.h.frame(3);
      const before = window.h.canvasPixels("optics-canvas", "base", plate);

      await window.h.loseRealDevice();
      window.h.frame(3);

      return {
        before,
        after: window.h.canvasPixels("optics-canvas", "base", plate),
        state: window.h.capabilities("gpu"),
        active: window.h.rendererActive(),
        host: window.h.hostStyle("plate"),
        sharp: window.h.layerStyle("plate", "sharp"),
      };
    }, PLATE);

    expect(result.before.painted, "nothing was drawn before the loss").toBeGreaterThan(0.5);

    // core's side of the swap: a recoverable fault, named, with
    // `configuredSource` preserved — not collapsed into the unrecoverable
    // `no-webgpu`, whose recovery would honestly be "none".
    expect(result.state?.health).toBe("demoted");
    expect(result.state?.demotionReason).toBe("device-lost");
    expect(result.state?.activeRenderer).toBe("css");
    expect(result.state?.configuredSource).toBe("texture");

    // The visible half. Unconfiguring the context is what clears it; a canvas
    // left configured would keep its last GPU frame sitting over CSS glass, and
    // nothing on screen would say which material was live.
    expect(result.active).toBe(false);
    expect(
      result.after.painted,
      `the GPU canvas still carried ${result.after.painted}`,
    ).toBeLessThan(0.02);

    // And the CSS tier stepped in, rather than the surface simply vanishing —
    // read on its sharp layer, which is where W16 G1 moved the filter to.
    expect(result.sharp?.backdropFilter ?? "none").not.toBe("none");
  });

  test("draws again once a device is restored", async ({ page }) => {
    // Recovery is re-resolution: the same inputs, with a live device again. A
    // fresh root is how a page gets one — the lifecycle deliberately does not
    // re-request after a `destroy()`, since that reason is our own teardown.
    await gotoHarness(page);
    requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

    const result = await page.evaluate(async (plate) => {
      const build = (): void => {
        window.h.addTextureGroup({ groupId: "gpu", sourceId: "gpu.canvas" });
        window.h.addSurface({
          groupId: "gpu",
          nodeId: "plate",
          left: plate.x,
          top: plate.y,
          width: plate.width,
          height: plate.height,
          radius: 26,
          label: "",
        });
      };

      await window.h.createRoot({ renderer: "webgpu" });
      build();
      window.h.frame(3);
      await window.h.loseRealDevice();
      window.h.frame(2);
      const lost = window.h.capabilities("gpu");

      window.h.reset();

      await window.h.createRoot({ renderer: "webgpu" });
      build();
      window.h.frame(3);

      return {
        lost,
        state: window.h.capabilities("gpu"),
        pixels: window.h.canvasPixels("optics-canvas", "base", plate),
      };
    }, PLATE);

    expect(result.lost?.demotionReason, "the device was not actually lost").toBe("device-lost");
    expect(result.state?.health).toBe("ok");
    expect(result.state?.activeRenderer).toBe("webgpu");
    expect(
      result.pixels.painted,
      `after recovery the canvas carried ${result.pixels.painted}`,
    ).toBeGreaterThan(0.5);
  });
});
