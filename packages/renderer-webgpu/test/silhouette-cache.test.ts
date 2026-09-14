import { describe, expect, it, vi } from "vitest";
import { createCopyProvider, createGradientProvider, linearGradientStops } from "../src/backdrop";
import { createWebGPURenderer } from "../src/renderer";
import type { GroupRenderInput } from "../src/render-model";
import { createFakeGpu } from "./harness/fake-gpu";

const GROUP: GroupRenderInput = {
  groupId: "g", backdropSourceId: "bg", refraction: "none", analysisExact: false,
  surfaces: [{ nodeId: "n", family: "fixed-rounded-rect", shape: {
    center: [200, 150], size: [160, 80], radii: [20, 20, 20, 20], smoothing: 0,
    thickness: 8,
  } }],
};

function setup(kind: "gradient" | "image" | "canvas" = "gradient") {
  const gpu = createFakeGpu();
  const copies = vi.fn();
  const createEncoder = gpu.device.createCommandEncoder.bind(gpu.device);
  vi.spyOn(gpu.device, "createCommandEncoder").mockImplementation((descriptor) => {
    const encoder = createEncoder(descriptor);
    vi.spyOn(encoder, "copyBufferToBuffer").mockImplementation(copies);
    return encoder;
  });
  const renderer = createWebGPURenderer({
    viewport: { widthCss: 400, heightCss: 300, devicePixelRatio: 1 },
    materialProfile: { backdropToneAbscissa: { kind: "silhouette" } },
  });
  renderer.attachDevice(gpu.device, "vitrea");
  renderer.setGroup(GROUP);
  const provider = kind === "gradient"
    ? createGradientProvider({ id: "bg", device: gpu.device,
        stops: linearGradientStops([0, 0, 0], [1, 1, 1]), generation: 1 })
    : createCopyProvider({ id: "bg", kind, device: gpu.device,
        source: {} as ImageBitmap, width: 400, height: 300, generation: 1 });
  renderer.registerBackdrop(provider);
  let id = 0;
  const draw = (timeMs: number) => renderer.drawFrame({
    frame: { id: ++id, timeMs }, optics: {} as GPUTextureView,
  });
  const reset = () => { gpu.reset(); copies.mockClear(); };
  const reductions = () => gpu.passes.filter((p) => p.label === "vitrea:silhouette-reduction");
  const toneCopies = () => copies.mock.calls.filter((call) => call[4] === 32);
  return { gpu, renderer, provider, draw, reset, reductions, toneCopies };
}

describe("silhouette reduction invalidation", () => {
  it("does not reduce or read back unchanged static frames again", async () => {
    const h = setup();
    h.draw(0);
    expect(h.reductions()).toHaveLength(1);
    expect(h.toneCopies()).toHaveLength(1);
    await h.renderer.collectAdaptation();
    h.reset();
    h.draw(1000);
    await h.renderer.collectAdaptation();
    expect(h.reductions()).toHaveLength(0);
    expect(h.toneCopies()).toHaveLength(0);
    h.renderer.destroy();
  });

  it("retries a reduction whose command encoder was never submitted", async () => {
    const h = setup();
    h.gpu.failNextFinish();
    expect(() => h.draw(0)).toThrow("encode failed");
    h.reset();
    h.draw(1);
    expect(h.reductions()).toHaveLength(1);
    await h.renderer.collectAdaptation();
    h.renderer.destroy();
  });

  it.each(["geometry", "fit", "viewport"])(
    "invalidates changed %s immediately, before adaptation is due", async (change) => {
      const h = setup();
      h.draw(0);
      await h.renderer.collectAdaptation();
      h.reset();
      if (change === "geometry") h.renderer.setGroup({ ...GROUP,
        surfaces: GROUP.surfaces.map((surface) => ({ ...surface,
          shape: { ...surface.shape, center: [210, 150] },
        })),
      });
      if (change === "fit") h.renderer.setBackdropPlacement("bg", {
        x: 20, y: 0, width: 400, height: 300,
      });
      if (change === "viewport") h.renderer.setViewport({
        widthCss: 420, heightCss: 300, devicePixelRatio: 1,
      });
      h.draw(1);
      expect(h.reductions()).toHaveLength(1);
      h.renderer.destroy();
    },
  );

  it("never reports a replaced host's old identity even when its geometry is identical", async () => {
    const h = setup();
    const group = { ...GROUP, backdropTone: [0.3, 0.3, 0.3] as const };
    h.renderer.setGroup(group);
    h.draw(0);
    await h.renderer.collectAdaptation();
    expect(h.renderer.backdropToneAbscissae("g").map((reading) => reading.surfaceId))
      .toEqual(["n"]);
    h.reset();
    h.renderer.setGroup({ ...group,
      surfaces: GROUP.surfaces.map((surface) => ({ ...surface, nodeId: "replacement" })),
    });
    h.draw(1);
    expect(h.renderer.backdropToneAbscissae("g")).toEqual([]);
    await h.renderer.collectAdaptation();
    expect(h.renderer.backdropToneAbscissae("g").map((reading) => reading.surfaceId))
      .toEqual(["replacement"]);
    h.renderer.destroy();
  });

  it("refreshes a replaced source resource even when its source id and extent match", async () => {
    const h = setup();
    h.draw(0);
    await h.renderer.collectAdaptation();
    h.reset();
    h.renderer.unregisterBackdrop("bg");
    h.renderer.registerBackdrop(createGradientProvider({ id: "bg", device: h.gpu.device,
      stops: linearGradientStops([1, 0, 0], [0, 0, 1]), generation: 1 }));
    h.draw(1);
    expect(h.reductions()).toHaveLength(1);
    expect(h.toneCopies()).toHaveLength(1);
    h.renderer.destroy();
  });

  it("catches up a busy readback without reducing the unchanged geometry again", async () => {
    const h = setup();
    h.draw(0);
    // No await: the first observation is still mapping when the next frame moves.
    h.reset();
    h.renderer.setGroup({ ...GROUP, surfaces: GROUP.surfaces.map((surface) => ({
      ...surface, nodeId: "moved", shape: { ...surface.shape, center: [210, 150] },
    })), backdropTone: [0.3, 0.3, 0.3], backdropToneLevel: 0.07 });
    h.draw(1);
    expect(h.reductions()).toHaveLength(1);
    expect(h.toneCopies()).toHaveLength(0);
    await h.renderer.collectAdaptation();
    expect(h.renderer.backdropToneAbscissae("g")).toEqual([]);
    h.reset();
    h.draw(2);
    expect(h.reductions()).toHaveLength(0);
    expect(h.toneCopies()).toHaveLength(1);
    await h.renderer.collectAdaptation();
    expect(h.renderer.backdropToneAbscissae("g").map((reading) => reading.surfaceId))
      .toEqual(["moved"]);
    h.renderer.destroy();
  });

  it("updates a cached zero-weight member's fallback without inventing a new reduction", async () => {
    const h = setup();
    h.renderer.setGroup({ ...GROUP, backdropTone: [0.3, 0.3, 0.3], backdropToneLevel: 0.07,
      backdropToneLinearLuminance: 0.9 });
    h.draw(0);
    await h.renderer.collectAdaptation();
    // The fake GPU's untouched storage is zero-weight, so the actual renderer's
    // source fallback path is observable without pretending to execute WGSL.
    expect(h.renderer.backdropToneAbscissae("g")[0]).toMatchObject({
      kind: "source", color: [0.3, 0.3, 0.3], luminance: 0.07, linearLuminance: 0.3,
    });
    h.reset();
    h.renderer.setGroup({ ...GROUP, backdropTone: [0.8, 0.8, 0.8], backdropToneLevel: 0.6 });
    h.draw(1);
    expect(h.reductions()).toHaveLength(0);
    expect(h.toneCopies()).toHaveLength(0);
    expect(h.renderer.backdropToneAbscissae("g")[0]).toMatchObject({
      kind: "source", color: [0.8, 0.8, 0.8], luminance: 0.6,
    });
    h.renderer.setGroup(GROUP);
    h.draw(2);
    expect(h.renderer.backdropToneAbscissae("g")).toEqual([]);
    h.renderer.destroy();
  });

  it("refreshes resized live-source resources immediately instead of waiting for cadence", async () => {
    const h = setup("canvas");
    h.draw(0);
    await h.renderer.collectAdaptation();
    h.reset();
    h.provider.resize!(800, 600);
    h.draw(1);
    expect(h.reductions()).toHaveLength(1);
    expect(h.toneCopies()).toHaveLength(1);
    h.renderer.destroy();
  });

  it("refreshes changed static image pixels immediately at the same size and fit", async () => {
    const h = setup("image");
    h.draw(0);
    await h.renderer.collectAdaptation();
    h.reset();
    h.provider.invalidate(1, h.gpu.device);
    h.draw(1);
    expect(h.reductions()).toHaveLength(1);
    expect(h.toneCopies()).toHaveLength(1);
    h.renderer.destroy();
  });

  it("gates dirty source epochs at the existing governor adaptation cadence", async () => {
    const h = setup("canvas");
    h.renderer.governor.set({ adaptationCadenceHz: 4 });
    h.draw(0);
    await h.renderer.collectAdaptation();
    h.reset();
    h.provider.invalidate(1, h.gpu.device);
    h.draw(10);
    expect(h.reductions()).toHaveLength(0);
    expect(h.toneCopies()).toHaveLength(0);
    h.draw(249);
    expect(h.reductions()).toHaveLength(0);
    h.draw(250);
    expect(h.reductions()).toHaveLength(1);
    expect(h.toneCopies()).toHaveLength(1);
    await h.renderer.collectAdaptation();
    h.reset();
    h.draw(251);
    expect(h.reductions()).toHaveLength(0);
    h.draw(500);
    expect(h.reductions()).toHaveLength(1);
    h.renderer.destroy();
  });
});
