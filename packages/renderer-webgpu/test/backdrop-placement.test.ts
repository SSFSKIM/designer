/**
 * The placement seam on the renderer (claims §5.47): what `setBackdropPlacement`
 * holds, what it clears, and when a placement change costs a pyramid rebuild.
 *
 * Only the SIZE of a placement changes the body's σ in texels, so only a size
 * change rebuilds; a source that scrolls across the page keeps its chain. That
 * distinction is the whole point of carrying the density on the resources,
 * and it is only observable through the store's rebuild count, which the fake
 * device is enough to drive.
 */
import { describe, expect, it } from "vitest";
import { createGradientProvider, linearGradientStops } from "../src/backdrop";
import type { GroupRenderInput } from "../src/render-model";
import { createWebGPURenderer, type DrawFrameArgs, type GlassRenderer } from "../src/renderer";
import { createFakeGpu, type FakeGpu } from "./harness/fake-gpu";

const VIEWPORT = { widthCss: 400, heightCss: 300, devicePixelRatio: 2 };

const GROUP: GroupRenderInput = {
  groupId: "g",
  surfaces: [
    {
      nodeId: "n",
      family: "fixed-rounded-rect",
      shape: {
        center: [200, 150],
        size: [160, 80],
        radii: [20, 20, 20, 20],
        smoothing: 0.5,
        thickness: 10,
      },
    },
  ],
  backdropSourceId: "bg",
  refraction: "true",
  analysisExact: true,
};

const view = () => ({}) as GPUTextureView;
const frameArgs = (id: number): DrawFrameArgs => ({
  frame: { id, timeMs: id * 16.7 },
  optics: view(),
  highlight: view(),
});

function rendererOn(gpu: FakeGpu): GlassRenderer {
  const renderer = createWebGPURenderer({ viewport: VIEWPORT });
  renderer.attachDevice(gpu.device, "vitrea");
  renderer.setGroup(GROUP);
  renderer.registerBackdrop(
    createGradientProvider({
      id: "bg",
      device: gpu.device,
      stops: linearGradientStops([0, 0, 0], [1, 1, 1]),
      generation: 1,
      width: 128,
      height: 128,
    }),
  );
  return renderer;
}

describe("holding a placement", () => {
  it("keeps a copy, answers it back, and forgets it with the source", () => {
    const renderer = rendererOn(createFakeGpu());
    const placement = { x: 40, y: 30, width: 128, height: 128 };
    renderer.setBackdropPlacement("bg", placement);
    expect(renderer.backdropPlacement("bg")).toEqual(placement);
    expect(renderer.backdropPlacement("bg")).not.toBe(placement);

    renderer.setBackdropPlacement("bg", undefined);
    expect(renderer.backdropPlacement("bg")).toBeUndefined();

    renderer.setBackdropPlacement("bg", placement);
    renderer.unregisterBackdrop("bg");
    expect(renderer.backdropPlacement("bg")).toBeUndefined();
  });

  it("accepts a placement for a source that has not registered yet", () => {
    const gpu = createFakeGpu();
    const renderer = createWebGPURenderer({ viewport: VIEWPORT });
    renderer.attachDevice(gpu.device, "vitrea");
    renderer.setBackdropPlacement("later", { x: 0, y: 0, width: 10, height: 10 });
    expect(renderer.backdropPlacement("later")).toEqual({ x: 0, y: 0, width: 10, height: 10 });
  });
});

describe("what a placement change costs", () => {
  it("rebuilds the pyramid when the placed size changes, and not when only its position does", () => {
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    renderer.setBackdropPlacement("bg", { x: 0, y: 0, width: 128, height: 128 });
    renderer.drawFrame(frameArgs(1));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(1);

    // A static source drawn again: clean, no rebuild.
    renderer.drawFrame(frameArgs(2));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(1);

    // Scrolled: the box moved, its size did not. One texel is still one CSS px.
    renderer.setBackdropPlacement("bg", { x: 90, y: 40, width: 128, height: 128 });
    renderer.drawFrame(frameArgs(3));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(1);

    // Resized: half the CSS px per texel, so the body σ in texels doubled and
    // the chain the material asked for is no longer the one on the store.
    renderer.setBackdropPlacement("bg", { x: 90, y: 40, width: 64, height: 64 });
    renderer.drawFrame(frameArgs(4));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(2);

    // And settles again.
    renderer.drawFrame(frameArgs(5));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(2);
  });

  it("rebuilds when the device pixel ratio changes, and not when the viewport only resizes at it", () => {
    /*
     * The body's widths are DEVICE-pixel quantities (W12 G3, claims §5.56), so
     * the CSS-px σ the pyramid converts to texels is `blurSigma / dpr` (restored
     * by W15 G1, claims §5.69 §1): a window dragged from a 1x display to a 2x
     * one asks for a different body from the same source at the same density,
     * and a static image never re-dirties to say so (W13 G1, review finding).
     */
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    // Placed at its own size, so the density is pinned to 1 and cannot be what
    // moves below.
    renderer.setBackdropPlacement("bg", { x: 0, y: 0, width: 128, height: 128 });
    renderer.drawFrame(frameArgs(1));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(1);

    // The same ratio again: clean.
    renderer.setViewport({ ...VIEWPORT });
    renderer.drawFrame(frameArgs(2));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(1);

    // Moved to a 1x display: same source, same placement, same density — but
    // twice the body σ in CSS px, so the chain on the store is the old scale's.
    // (W13 Decision Log 8 withdrew the division and this was a clean frame for
    // one wave; W15 G1 restores it, claims §5.69 §1.)
    renderer.setViewport({ ...VIEWPORT, devicePixelRatio: 1 });
    renderer.drawFrame(frameArgs(3));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(2);

    // And settles there.
    renderer.drawFrame(frameArgs(4));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(2);

    // Back to 2x: the σ moves again.
    renderer.setViewport({ ...VIEWPORT, devicePixelRatio: 2 });
    renderer.drawFrame(frameArgs(5));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(3);
  });

  it("rebuilds when a placement first arrives for a source built under cover fit", () => {
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    renderer.drawFrame(frameArgs(1));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(1);

    // Cover on a 400×300 viewport is 128/400 = 0.32 texels per CSS px; placed
    // at its own size it is 1. Different body, so a rebuild.
    renderer.setBackdropPlacement("bg", { x: 10, y: 10, width: 128, height: 128 });
    renderer.drawFrame(frameArgs(2));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(2);

    // Withdrawn: back to cover, and back to a rebuild.
    renderer.setBackdropPlacement("bg", undefined);
    renderer.drawFrame(frameArgs(3));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(3);
  });

  it("does not rebuild for a placement whose density is the cover ratio's", () => {
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    // Cover on 400×300 keeps the axis the crop preserves: 128/300 texels per
    // CSS px. A 128-texel square placed 300 CSS px wide has the same density,
    // so the fit moves (it is per frame, and free) and the body does not.
    renderer.drawFrame(frameArgs(1));
    renderer.setBackdropPlacement("bg", { x: 0, y: 0, width: 300, height: 300 });
    renderer.drawFrame(frameArgs(2));
    expect(renderer.instrumentation.pyramid.rebuilds).toBe(1);
  });
});
