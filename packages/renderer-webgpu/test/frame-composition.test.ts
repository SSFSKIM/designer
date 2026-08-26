/**
 * The frame, composed — the properties that only exist when `renderer.ts`,
 * `passes.ts` and `pyramid.ts` run together.
 *
 * Every failure regression-tested here was invisible to the per-module suites and
 * would have been invisible to a golden too, because none of them changes a
 * steady-state pixel: they are a resize that strands a texture handle, a device
 * generation that leaves a provider pointing at a dead device, an encode that
 * throws while a video is held, a rebuild claim spent on nothing. What they have
 * in common is that the evidence is *which object* the next frame reaches for, so
 * the fake device hands out real identities and the assertions are about those.
 *
 * What this file cannot say: whether the bindings are legal, whether the WGSL
 * compiles, or what any of it looks like. `e2e/gpu/` and `e2e/golden/` answer
 * those on a real adapter, and where no adapter exists that is the honest gap.
 */

import { describe, expect, it } from "vitest";

import {
  createAppTextureProvider,
  createGradientProvider,
  linearGradientStops,
  type BackdropFrame,
  type BackdropProvider,
} from "../src/backdrop";
import { createGovernor } from "../src/governor";
import { createGpuContext } from "../src/gpu-context";
import { createPassRunner } from "../src/passes";
import { createPyramidStore } from "../src/pyramid";
import type { GroupRenderInput } from "../src/render-model";
import { createWebGPURenderer, type DrawFrameArgs, type GlassRenderer } from "../src/renderer";
import { poolKey } from "../src/texture-pool";

import { createFakeGpu, flush, viewOwner, type FakeGpu } from "./harness/fake-gpu";

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
  return renderer;
}

const gradientOn = (gpu: FakeGpu, generation: number): BackdropProvider =>
  createGradientProvider({
    id: "bg",
    device: gpu.device,
    stops: linearGradientStops([0, 0, 0], [1, 1, 1]),
    generation,
  });

/** The textures the optics pass bound as the backdrop this frame, if any. */
function backdropBindings(gpu: FakeGpu): readonly GPUTexture[] {
  const pass = gpu.passes.find((candidate) => candidate.label.startsWith("vitrea:pass:optics"));
  const entries = pass?.bindGroups[0]?.entries ?? [];
  return entries
    .filter((entry) => entry.binding === 4 || entry.binding === 5)
    .map((entry) => viewOwner(entry.resource as GPUTextureView));
}

const labelled = (gpu: FakeGpu, fragment: string) =>
  gpu.textures.filter((texture) => texture.label.includes(fragment));

describe("a resize with a static backdrop", () => {
  it("leaves the pyramid's textures alive for the frame that binds them", () => {
    // The eager sweep this replaces destroyed the chain and body immediately.
    // A static source rebuilds nothing — core hands out no request for a clean
    // one — so nothing reallocated them, and the very next frame bound two
    // destroyed textures: one validation error, and the whole plane's encoder
    // with it. Bumping the epoch without sweeping defers the destroy to the
    // `acquire` that replaces them, which is where it belongs.
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    renderer.registerBackdrop(gradientOn(gpu, 1));

    renderer.drawFrame(frameArgs(1));
    const built = labelled(gpu, "vitrea:pyramid:bg:chain");
    expect(built).toHaveLength(1);

    renderer.setViewport({ widthCss: 500, heightCss: 320, devicePixelRatio: 2 });
    expect(built[0]?.destroyed).toBe(false);

    gpu.reset();
    renderer.drawFrame(frameArgs(2));

    const bound = backdropBindings(gpu);
    expect(bound).toHaveLength(2);
    for (const texture of bound) expect(gpu.info(texture)?.destroyed).toBe(false);
  });

  it("still replaces the group's field targets, which is what the epoch is for", () => {
    // The bump has to keep doing its job: a field texture's device extent is a
    // function of the DPR, so a DPR change must reallocate it on next use.
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);

    renderer.drawFrame(frameArgs(1));
    const first = labelled(gpu, "vitrea:group:g:field");
    expect(first).toHaveLength(1);

    renderer.setViewport({ ...VIEWPORT, devicePixelRatio: 3 });
    renderer.drawFrame(frameArgs(2));

    expect(labelled(gpu, "vitrea:group:g:field")).toHaveLength(2);
    expect(first[0]?.destroyed).toBe(true);
  });
});

describe("the pyramid's handles, checked against the pool", () => {
  it("reports no resources once the pool no longer holds what was recorded", () => {
    // The pool owns the lifetime and can destroy without this store hearing about
    // it. Two identity compares turn "bind a destroyed texture" into "there is no
    // backdrop this frame", which the optics pass already has a placeholder for.
    const gpu = createFakeGpu();
    const context = createGpuContext(gpu.device, 1);
    const store = createPyramidStore(context);
    const encoder = gpu.device.createCommandEncoder();
    const provider = gradientOn(gpu, 1);

    store.beginFrame(1);
    const outcome = store.build(
      {
        sourceId: "bg",
        epoch: 1,
        resolution: { scale: 1, maxDimension: 2048 },
        bodySigmaCss: 8,
        viewportCss: [400, 300],
      },
      provider,
      encoder,
    );
    expect(outcome.status).toBe("built");
    expect(store.resources("bg")).toBeDefined();

    context.pool.release(poolKey.backdropChain("bg"));
    expect(store.resources("bg")).toBeUndefined();
  });

  it("rebuilds rather than reporting clean against a handle the pool dropped", () => {
    // The clean-skip is exactly what would stop the reallocation that heals it,
    // so a stale handle must not be allowed to satisfy one.
    const gpu = createFakeGpu();
    const context = createGpuContext(gpu.device, 1);
    const store = createPyramidStore(context);
    const provider = gradientOn(gpu, 1);
    const request = {
      sourceId: "bg",
      epoch: 1,
      resolution: { scale: 1, maxDimension: 2048 },
      bodySigmaCss: 8,
      viewportCss: [400, 300] as const,
    };

    store.beginFrame(1);
    store.build(request, provider, gpu.device.createCommandEncoder());
    provider.markImported();

    store.beginFrame(2);
    expect(store.build(request, provider, gpu.device.createCommandEncoder()).status).toBe("clean");

    context.pool.release(poolKey.backdropBody("bg"));
    store.beginFrame(3);
    expect(store.build(request, provider, gpu.device.createCommandEncoder()).status).toBe("built");
  });
});

describe("a device generation boundary", () => {
  it("re-points a renderer-owned provider at the new device and re-imports", async () => {
    // Every provider closes over the device it was built with, so a reset that
    // only cleared the dirty flags would re-import onto the dead device.
    const first = createFakeGpu();
    const second = createFakeGpu();
    const renderer = rendererOn(first);
    const gradient = gradientOn(first, 1);
    renderer.registerBackdrop(gradient);

    renderer.drawFrame(frameArgs(1));
    expect(gradient.isDirty()).toBe(false);
    expect(labelled(first, "vitrea:backdrop:bg:gradient")).toHaveLength(1);

    first.lose();
    await flush();
    renderer.replaceDevice(second.device);
    renderer.drawFrame(frameArgs(2));

    expect(gradient.generation).toBe(2);
    // Re-imported, on the new device — not reused from the dead one.
    expect(labelled(second, "vitrea:backdrop:bg:gradient")).toHaveLength(1);
    expect(gradient.isDirty()).toBe(false);
  });

  it("refuses an app-owned texture rather than binding a foreign-device view", async () => {
    // A GPUTextureView carries no evidence of the device that made it and binding
    // one from a superseded device produces no error the renderer can see — only
    // a pass that quietly renders nothing.
    const first = createFakeGpu();
    const second = createFakeGpu();
    const renderer = rendererOn(first);
    const app = createAppTextureProvider({
      id: "bg",
      device: first.device,
      texture: first.device.createTexture({
        label: "app",
        size: { width: 64, height: 64, depthOrArrayLayers: 1 },
        format: "rgba8unorm",
        usage: GPUTextureUsage.TEXTURE_BINDING,
      }),
      generation: 1,
    });
    renderer.registerBackdrop(app);

    expect(renderer.drawFrame(frameArgs(1)).unbuilt).toEqual([]);

    first.lose();
    await flush();
    renderer.replaceDevice(second.device);

    const after = renderer.drawFrame(frameArgs(2));
    expect(after.unbuilt).toEqual(["bg"]);
    expect(() => app.acquire({ id: 2, timeMs: 0 })).toThrowError(/cross-device/);
  });

  it("leaves a provider registered under the current generation alone", () => {
    // Nothing was superseded, so nothing is invalidated: a first attach is not a
    // replacement, and invalidating there would refuse every app texture
    // registered before the device arrived.
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    const gradient = gradientOn(gpu, 1);
    renderer.registerBackdrop(gradient);

    renderer.drawFrame(frameArgs(1));
    renderer.drawFrame(frameArgs(2));

    expect(gradient.generation).toBe(1);
    expect(labelled(gpu, "vitrea:backdrop:bg:gradient")).toHaveLength(1);
  });
});

/** Records the acquire/release pairing X3 asks for, and nothing else. */
function recordingProvider(): BackdropProvider & { readonly log: string[] } {
  const log: string[] = [];
  let acquired = false;
  return {
    log,
    id: "bg",
    kind: "canvas",
    generation: 0,
    isDirty: () => true,
    acquire(): BackdropFrame {
      if (acquired) throw new Error("acquired twice without a release");
      acquired = true;
      log.push("acquire");
      return {
        sourceId: "bg",
        binding: { kind: "sampled", view: view() },
        width: 64,
        height: 64,
        sizeEpoch: 0,
        colorSpace: "srgb",
        alphaMode: "premultiplied",
        encoded: true,
      };
    },
    release() {
      acquired = false;
      log.push("release");
    },
    markImported: () => undefined,
    invalidate: () => undefined,
    destroy: () => undefined,
  };
}

describe("an encode that throws", () => {
  it("still releases what the frame acquired", () => {
    // The release is owed whether or not the frame reached the queue: an acquired
    // VideoFrame held across a frame stalls decoding, and the next acquire fails
    // the frame-protocol check — self-healing, but only after a wasted frame.
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    const provider = recordingProvider();
    renderer.registerBackdrop(provider);

    gpu.failNextFinish();
    expect(() => renderer.drawFrame(frameArgs(1))).toThrowError(/encode failed/);
    expect(provider.log).toEqual(["acquire", "release"]);

    // And the next frame is an ordinary one, not a frame-protocol failure.
    expect(() => renderer.drawFrame(frameArgs(2))).not.toThrow();
    expect(provider.log).toEqual(["acquire", "release", "acquire", "release"]);
  });
});

describe("rebuild claims the renderer could not spend", () => {
  it("names a source no provider is registered under", () => {
    // Core commits `builtEpoch` when it hands the request out, so a request
    // dropped here leaves the source clean at an epoch whose pixels were never
    // imported. Naming it is what lets the platform layer re-dirty it.
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);

    const result = renderer.drawFrame({
      ...frameArgs(1),
      rebuild: [
        {
          sourceId: "ghost",
          epoch: 4,
          resolution: { scale: 1, maxDimension: 2048 },
          groupIds: ["g"],
        },
      ],
    });

    expect(result.unbuilt).toEqual(["ghost"]);
    expect(renderer.unbuiltSources).toEqual(["ghost"]);
  });

  it("names a source whose provider could not serve a frame", () => {
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    const provider = recordingProvider();
    renderer.registerBackdrop({
      ...provider,
      acquire() {
        throw new Error("no decoded frame yet");
      },
    });

    expect(renderer.drawFrame(frameArgs(1)).unbuilt).toEqual(["bg"]);
  });

  it("survives the frame's later planes, which carry no dirty set", () => {
    // A host draws one plane per `drawFrame` with the same frame id and hands the
    // dirty set to the first of them only. A per-call field would be cleared by
    // plane two every time, so the report would always be empty by the time the
    // host read it.
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    const request = {
      sourceId: "ghost",
      epoch: 4,
      resolution: { scale: 1, maxDimension: 2048 },
      groupIds: ["g"],
    };

    renderer.drawFrame({ ...frameArgs(1), rebuild: [request] });
    const second = renderer.drawFrame({ ...frameArgs(1), rebuild: [] });

    expect(second.unbuilt).toEqual(["ghost"]);
    expect(renderer.unbuiltSources).toEqual(["ghost"]);

    // And the next frame starts clean.
    expect(renderer.drawFrame({ ...frameArgs(2), rebuild: [] }).unbuilt).toEqual([]);
  });

  it("is empty on an ordinary frame", () => {
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);
    renderer.registerBackdrop(gradientOn(gpu, 1));

    expect(renderer.drawFrame(frameArgs(1)).unbuilt).toEqual([]);
    expect(renderer.unbuiltSources).toEqual([]);
  });
});

describe("the governor's refraction resolution scale", () => {
  const fieldArgs = (renderScale: number) => ({
    groupId: "g",
    family: "rsupn" as const,
    rectDevice: { x: 0, y: 0, width: 400, height: 200 },
    cssPerDevice: 0.5,
    coverageRampCss: 0.5,
    renderScale,
    instances: new Float32Array(16),
    instanceCount: 1,
    union: { neckWidth: 8, maxBulge: 4, separationThreshold: 12 },
  });

  it("allocates the field targets at the rect's own extent when it is 1", () => {
    const gpu = createFakeGpu();
    const runner = createPassRunner(createGpuContext(gpu.device, 1));
    const targets = runner.fieldPass(gpu.device.createCommandEncoder(), fieldArgs(1));

    expect([targets.width, targets.height]).toEqual([400, 200]);
    // The nominal path reads the field by exact texel index, as it always has.
    expect(targets.upsampled).toBe(false);
  });

  it("shrinks them by the knob, and says the read has to filter", () => {
    const gpu = createFakeGpu();
    const runner = createPassRunner(createGpuContext(gpu.device, 1));
    const targets = runner.fieldPass(gpu.device.createCommandEncoder(), fieldArgs(0.5));

    expect([targets.width, targets.height]).toEqual([200, 100]);
    expect(targets.upsampled).toBe(true);
  });

  it("is what ladder rung 2 turns, end to end", () => {
    // The knob was defined and never read: rungs 2 and 3 delivered a cadence
    // saving and nothing else. This is the assertion that it reaches an
    // allocation.
    const gpu = createFakeGpu();
    const renderer = rendererOn(gpu);

    renderer.drawFrame(frameArgs(1));
    const nominal = labelled(gpu, "vitrea:group:g:field")[0];

    const knobs = renderer.governor.setLevel(2);
    expect(knobs.refractionResolutionScale).toBe(0.75);
    renderer.drawFrame(frameArgs(2));

    const scaled = labelled(gpu, "vitrea:group:g:field")[1];
    expect(scaled?.width).toBe(Math.round((nominal?.width ?? 0) * 0.75));
    expect(scaled?.height).toBe(Math.round((nominal?.height ?? 0) * 0.75));
    // The group still covers the same pixels; only the field's grid is coarser.
    expect(nominal?.destroyed).toBe(true);
  });

  it("keeps the nominal rung at full device resolution", () => {
    const governor = createGovernor();
    expect(governor.setLevel(0).refractionResolutionScale).toBe(1);
    expect(governor.setLevel(1).refractionResolutionScale).toBe(1);
  });
});
