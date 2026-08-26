/**
 * `createGlassRoot`, driven by hand in jsdom.
 *
 * jsdom cannot lay out and cannot filter, so nothing here asserts a pixel or a
 * rect — the Playwright suite owns both. What it *can* do is run the real root
 * through its real lifecycle, which is where a whole class of defects lives: the
 * startup window before the GPU tier answers, the seam between supplying a
 * texture and marking it dirty, and which host writes cost a measurement. Every
 * one of those was invisible to the e2e harness for the same reason — it awaits
 * `root.ready()` before it asserts anything, so the interesting frames are the
 * ones it never looks at.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createGlassRoot, type GlassRoot, type GlassRootOptions } from "../src/root";
import type { MediaMatcher } from "../src/media-policy";

/** jsdom has no ResizeObserver, and `GeometrySync` builds one unconditionally. */
class StubResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

/** Every preference off, every query parseable. */
const matcher: MediaMatcher = () => ({
  matches: false,
  media: "(prefers-reduced-motion: reduce)",
  addEventListener: () => {},
  removeEventListener: () => {},
});

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];
/** Set while a test is running with stubbed canvas contexts; see below. */
let restoreCanvasContexts: (() => void) | undefined;

function root(options: GlassRootOptions = {}): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: () => {},
    ...options,
  });
  roots.push(created);
  return created;
}

/** A group with one host in it, ready to be framed. */
function withHost(
  instance: GlassRoot,
  options: { readonly groupId?: string; readonly sourceId?: string; readonly plane?: "base" | "overlay" } = {},
): HTMLElement {
  const groupId = options.groupId ?? "g1";
  const plane = options.plane ?? "base";
  const host = document.createElement("button");
  instance.plane(plane).hostLayer.append(host);
  instance.registerGroup({
    id: groupId,
    ...(options.sourceId === undefined ? {} : { backdropSourceId: options.sourceId }),
  });
  instance.registerHost({ host, groupId, plane });
  return host;
}

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
  // jsdom has no `ImageBitmap`, and the bridge narrows an image source against
  // it to read an extent. A constructor nothing is an instance of is all that
  // branch needs to answer correctly.
  (globalThis as { ImageBitmap?: unknown }).ImageBitmap ??= class ImageBitmap {};
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
  // Restored here rather than at the end of each test body: a failing assertion
  // would otherwise leak the patch into whatever runs next.
  restoreCanvasContexts?.();
  restoreCanvasContexts = undefined;
});

/**
 * A device that exists and never dies. Enough to open the window under test: the
 * lifecycle publishes `available` for it synchronously, while the bridge's own
 * module load, attach and canvas configuration are still queued.
 */
const idleDevice = (): GPUDevice =>
  ({ lost: new Promise<never>(() => {}), destroy: () => {} }) as unknown as GPUDevice;

describe("the startup window before the GPU tier can paint", () => {
  it("keeps a webgpu root's CSS declarations painting until the bridge is genuinely active", () => {
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    const host = withHost(instance);

    // Deliberately not awaited: this is the window the e2e harness never
    // observes, because it awaits `ready()` before it asserts anything.
    // `webgpu:"available"` used to be published the moment the device landed, so
    // core resolved the group onto the GPU tier and the write phase stripped
    // these declarations while the bridge's serialised module load, attach and
    // configure had not finished — a blank glass surface on every GPU page load.
    instance.runFrame(0);

    expect(instance.webgpu?.available).toBe(true);
    expect(instance.rendererBridge?.active).toBe(false);
    expect(host.style.getPropertyValue("backdrop-filter")).not.toBe("");
    expect(host.style.getPropertyValue("--vitrea-tint")).not.toBe("");
  });

  it("reports CSS while pending as a choice, not as a fault", () => {
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    withHost(instance);
    instance.runFrame(0);

    const state = instance.capabilities("g1");
    expect(state?.activeRenderer).toBe("css");
    // `"unavailable"` here would resolve to `no-webgpu`, whose recovery is
    // honestly `"none"` — a terminal answer to a request still in flight.
    expect(state?.health).toBe("ok");
    expect(state?.demotionReason).toBeUndefined();
  });

  it("withdraws the tier when the bridge settles unable to paint", async () => {
    // jsdom's canvases refuse a `"webgpu"` context, which is the latched refusal
    // in the flesh. It used to be survived silently: the bridge stopped drawing,
    // core still believed WebGPU was live, and the CSS tier stayed stood down —
    // so neither tier painted for the session and every group read `health: "ok"`.
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    const host = withHost(instance);

    await instance.ready();
    instance.runFrame(16);

    expect(instance.rendererBridge?.active).toBe(false);
    const state = instance.capabilities("g1");
    expect(state?.activeRenderer).toBe("css");
    expect(state?.health).toBe("demoted");
    expect(state?.demotionReason).toBe("no-webgpu");
    expect(host.style.getPropertyValue("backdrop-filter")).not.toBe("");
  });

  it("answers unavailable straight away where there is no adapter at all", () => {
    // No `navigator.gpu` in jsdom, so the lifecycle knows synchronously. Pending
    // is for an answer in flight, not for every answer.
    const instance = root({ renderer: "webgpu" });
    withHost(instance);
    instance.runFrame(0);

    expect(instance.capabilities("g1")?.demotionReason).toBe("no-webgpu");
  });

  it("leaves a css root at not-requested, which pending must not be confused with", () => {
    const instance = root();
    withHost(instance);
    instance.runFrame(0);

    expect(instance.capabilities("g1")?.health).toBe("ok");
    expect(instance.rendererBridge).toBeUndefined();
  });
});

/**
 * jsdom canvases refuse every context, which is honest but leaves no way to reach
 * a live GPU tier. Handing them a configurable stub is what lets these tests
 * observe the states that only exist once the bridge is painting.
 */
const stubCanvasContexts = (): void => {
  const original = HTMLCanvasElement.prototype.getContext;
  (HTMLCanvasElement.prototype as { getContext: unknown }).getContext = () => ({
    configure: () => {},
    unconfigure: () => {},
    getCurrentTexture: () => ({ createView: () => ({}) }),
  });
  restoreCanvasContexts = () => {
    (HTMLCanvasElement.prototype as { getContext: unknown }).getContext = original;
  };
};

describe("a texture source with no pixels behind it", () => {
  const registerTexture = (instance: GlassRoot): void => {
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
  };

  it("resolves with nothing sampled and says why, on a live GPU tier", async () => {
    stubCanvasContexts();
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    registerTexture(instance);
    withHost(instance, { sourceId: "src" });
    await instance.ready();

    // React registers a texture source with a clean probe before the pixels
    // arrive, so this is the ordinary case rather than a corner: the group used
    // to publish gpu-texture / true / exact over a source nobody had supplied.
    expect(instance.rendererBridge?.active).toBe(true);
    expect(instance.capabilities("g1")).toEqual({
      configuredSource: "texture",
      activeRenderer: "webgpu",
      samplingBackend: "none",
      refraction: "none",
      analysis: "none",
      health: "demoted",
      demotionReason: "no-texture-supplied",
    });
  });

  it("recovers the moment the pixels are supplied, and demotes again on withdrawal", async () => {
    stubCanvasContexts();
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    registerTexture(instance);
    withHost(instance, { sourceId: "src" });
    await instance.ready();

    instance.setBackdropTexture("src", { kind: "canvas", canvas: document.createElement("canvas") });
    expect(instance.capabilities("g1")?.samplingBackend).toBe("gpu-texture");
    expect(instance.capabilities("g1")?.health).toBe("ok");

    // `setBackdropTexture(id, undefined)` used to leave the state untouched, so a
    // withdrawn source went on reporting exact analysis.
    instance.setBackdropTexture("src", undefined);
    expect(instance.capabilities("g1")?.demotionReason).toBe("no-texture-supplied");
  });

  it("is not claimed against a CSS-tier root, which never samples a texture anyway", () => {
    const instance = root();
    registerTexture(instance);
    withHost(instance, { sourceId: "src" });
    instance.runFrame(0);

    expect(instance.capabilities("g1")?.health).toBe("ok");
    expect(instance.capabilities("g1")?.demotionReason).toBeUndefined();
  });
});

describe("the setBackdropTexture seam", () => {
  const canvasTexture = { kind: "canvas", canvas: document.createElement("canvas") } as const;

  it("marks the source dirty, so the pixels are actually imported", () => {
    const instance = root({ renderer: "webgpu" });
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    withHost(instance, { sourceId: "src" });

    // Before this, nothing in platform-web ever marked a source dirty: every
    // caller in the repo — including this package's own e2e harness — reached
    // through `root.scene.markBackdropSourceDirty` by hand, while the doc
    // comment claimed this was the only wiring the GPU tier needed.
    instance.setBackdropTexture("src", canvasTexture);

    expect(instance.scene.dirtyBackdropSources().map((source) => source.descriptor.id)).toEqual([
      "src",
    ]);
  });

  it("does not mark on withdrawal — there is nothing to import", () => {
    const instance = root({ renderer: "webgpu" });
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    withHost(instance, { sourceId: "src" });
    instance.setBackdropTexture("src", canvasTexture);
    instance.runFrame(0);
    instance.scene.consumeDirtyBackdropSources(999);

    instance.setBackdropTexture("src", undefined);

    expect(instance.scene.dirtyBackdropSources()).toEqual([]);
  });

  it("says nothing about a source the scene does not know", () => {
    const instance = root({ renderer: "webgpu" });

    expect(() => instance.setBackdropTexture("never-registered", canvasTexture)).not.toThrow();
  });
});

describe("app-owned device replacement", () => {
  it("forwards the replacement callback and delegates the replacement device", async () => {
    // A device stub is enough: nothing here draws, and what is under test is the
    // wiring between `GlassRootOptions.webgpu` and the lifecycle that already
    // implements both halves. Before this, neither half reached the root at all,
    // so app-owned device loss was terminal with a diagnostic naming an action
    // that had no API.
    let lost!: (info: { reason: string }) => void;
    const device = {
      lost: new Promise<{ reason: string }>((resolve) => {
        lost = resolve;
      }),
      destroy: () => {},
    } as unknown as GPUDevice;
    const onReplacementNeeded = vi.fn();

    const instance = root({ renderer: "webgpu", webgpu: { device, onReplacementNeeded } });
    await instance.ready();
    expect(instance.webgpu?.ownership).toBe("app");

    lost({ reason: "unknown" });
    await vi.waitFor(() => expect(onReplacementNeeded).toHaveBeenCalled());
    expect(instance.webgpu?.deviceHealth).toBe("lost");

    const replacement = {
      lost: new Promise<{ reason: string }>(() => {}),
      destroy: () => {},
    } as unknown as GPUDevice;
    instance.replaceDevice(replacement);

    expect(instance.webgpu?.device).toBe(replacement);
    expect(instance.webgpu?.deviceHealth).toBe("ok");
  });
});

/**
 * A renderer that consumes frames and draws nothing, reached through the root's
 * own X7 seam. jsdom has no adapter, and the accounting under test here is all on
 * this side of the wire.
 */
function stubGpu(): {
  readonly load: () => Promise<never>;
  readonly renderer: { unbuiltSources: readonly string[] };
  /** The rebuild source ids each frame carried, in frame order. */
  readonly rebuildsPerFrame: () => string[][];
} {
  const draws: { readonly frameId: number; readonly sources: readonly string[] }[] = [];
  const renderer = {
    backend: "webgpu",
    ready: true,
    deviceStatus: { generation: 1 },
    unbuiltSources: [] as readonly string[],
    attachDevice: () => {},
    replaceDevice: () => {},
    registerBackdrop: () => {},
    unregisterBackdrop: () => {},
    backdrop: () => undefined,
    setViewport: () => {},
    setGroup: () => {},
    removeGroup: () => {},
    setAccessibility: () => {},
    setMaterialProfile: () => {},
    drawFrame: (args: {
      frame: { id: number };
      rebuild?: readonly { sourceId: string }[];
    }) => {
      draws.push({
        frameId: args.frame.id,
        sources: (args.rebuild ?? []).map((request) => request.sourceId),
      });
      return { groupsDrawn: 0, rebuilds: 0, skipped: [], unbuilt: [] };
    },
    collectAdaptation: async () => {},
    destroy: () => {},
  };
  const module = {
    createWebGPURenderer: () => renderer,
    createCopyProvider: (options: { id: string }) => ({ id: options.id }),
    createVideoProvider: (options: { id: string }) => ({ id: options.id }),
  };
  return {
    load: () => Promise.resolve(module) as unknown as Promise<never>,
    renderer,
    // One draw per plane, so the frame's claims are the union across its planes.
    rebuildsPerFrame: () => {
      const byFrame = new Map<number, string[]>();
      for (const draw of draws) {
        byFrame.set(draw.frameId, [...(byFrame.get(draw.frameId) ?? []), ...draw.sources]);
      }
      return [...byFrame.values()];
    },
  };
}

describe("keeping the dirty-epoch ledger honest across the wire", () => {
  const gpuRoot = async (): Promise<{
    readonly instance: GlassRoot;
    readonly gpu: ReturnType<typeof stubGpu>;
  }> => {
    stubCanvasContexts();
    const gpu = stubGpu();
    const instance = root({
      renderer: "webgpu",
      webgpu: { device: idleDevice(), load: gpu.load },
    });
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    withHost(instance, { sourceId: "src" });
    await instance.ready();
    return { instance, gpu };
  };

  it("re-marks a live canvas every frame, so it does not freeze after one import", async () => {
    const { instance, gpu } = await gpuRoot();
    instance.setBackdropTexture("src", {
      kind: "canvas",
      canvas: document.createElement("canvas"),
    });

    instance.runFrame(0);
    instance.runFrame(16);
    instance.runFrame(32);

    // A video's external texture expires at task end and a canvas is repainted
    // by its owner. Nothing else marked them, and the app is not required to: a
    // video source froze on its first imported frame forever.
    expect(gpu.rebuildsPerFrame()).toEqual([["src"], ["src"], ["src"]]);
  });

  it("leaves a decoded image alone after its one import", async () => {
    const { instance, gpu } = await gpuRoot();
    instance.setBackdropTexture("src", { kind: "image", image: document.createElement("img") });

    instance.runFrame(0);
    instance.runFrame(16);

    expect(gpu.rebuildsPerFrame()).toEqual([["src"], []]);
  });

  it("re-dirties a source the renderer was handed and could not build", async () => {
    const { instance, gpu } = await gpuRoot();
    instance.setBackdropTexture("src", { kind: "image", image: document.createElement("img") });
    gpu.renderer.unbuiltSources = ["src"];

    instance.runFrame(0);

    // core commits `builtEpoch` when it hands the request out, so a request the
    // renderer dropped leaves the source clean at an epoch nobody imported. One
    // frame of latency, and no new core surface.
    expect(instance.scene.dirtyBackdropSources().map((source) => source.descriptor.id)).toEqual([
      "src",
    ]);
    gpu.renderer.unbuiltSources = [];
    instance.runFrame(16);
    expect(gpu.rebuildsPerFrame()).toEqual([["src"], ["src"]]);
  });

  it("does not spend the claim on a frame the bridge cannot draw", async () => {
    // No canvas stub, so the bridge's canvases refuse and it never becomes
    // active. Consuming anyway would commit `builtEpoch` for a frame that built
    // nothing, and the one-shot import would be gone for good.
    const gpu = stubGpu();
    const instance = root({
      renderer: "webgpu",
      webgpu: { device: idleDevice(), load: gpu.load },
    });
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    withHost(instance, { sourceId: "src" });
    await instance.ready();
    instance.setBackdropTexture("src", { kind: "image", image: document.createElement("img") });

    instance.runFrame(0);

    expect(instance.rendererBridge?.active).toBe(false);
    expect(instance.scene.backdropSource("src")?.builtEpoch).toBe(0);
    expect(instance.scene.dirtyBackdropSources().map((source) => source.descriptor.id)).toEqual([
      "src",
    ]);
  });
});

describe("measuring around vitrea's own transforms", () => {
  /** Run frames until the geometry sync has nothing left to measure. */
  const settle = (instance: GlassRoot): void => {
    for (let frame = 0; frame < 3; frame += 1) instance.runFrame(frame * 16);
  };

  /** One registered host in one group, with its own handle. */
  const hostHandle = (instance: GlassRoot) => {
    const host = document.createElement("button");
    instance.plane("base").hostLayer.append(host);
    instance.registerGroup({ id: "g1" });
    return instance.registerHost({ host, groupId: "g1" });
  };

  it("does not re-measure on a host patch, because no patch field moves the border box", () => {
    const instance = root();
    const handle = hostHandle(instance);
    settle(instance);

    const before = instance.readMeter.counts.rects;
    handle.update({ thickness: 12 });
    instance.runFrame(64);

    expect(instance.readMeter.counts.rects).toBe(before);
  });

  it("does not re-measure while an owned transform is live", () => {
    const instance = root();
    const handle = hostHandle(instance);
    settle(instance);

    const before = instance.readMeter.counts.rects;
    handle.setOwnedTransform("scale(0.96)");
    instance.runFrame(64);
    handle.setOwnedTransform("scale(0.98)");
    instance.runFrame(80);

    // The frames a press or a morph runs for are exactly the frames that have to
    // stay at zero reads.
    expect(instance.readMeter.counts.rects).toBe(before);
  });

  it("re-measures exactly once when the owned transform is cleared", () => {
    const instance = root();
    const handle = hostHandle(instance);
    settle(instance);
    handle.setOwnedTransform("scale(0.96)");
    instance.runFrame(64);

    const before = instance.readMeter.counts.rects;
    // `getBoundingClientRect` reports the *transformed* box, so every rect taken
    // while the press spring was live described the compressed surface. Nothing
    // re-read the real one, so the compressed bounds persisted indefinitely.
    handle.setOwnedTransform(undefined);
    instance.runFrame(80);
    expect(instance.readMeter.counts.rects).toBe(before + 1);

    // And only once: clearing an already-cleared transform is not an edge.
    handle.setOwnedTransform(undefined);
    instance.runFrame(96);
    expect(instance.readMeter.counts.rects).toBe(before + 1);
  });
});

describe("vitrea's ownership of the transform property", () => {
  it("reports a host registered carrying an inline transform it did not write", () => {
    const reported: string[] = [];
    const instance = root({ diagnosticSink: ({ diagnostic }) => reported.push(diagnostic.code) });
    const host = document.createElement("button");
    host.style.transform = "translateY(-2px)";
    instance.plane("base").hostLayer.append(host);
    instance.registerGroup({ id: "g1" });
    instance.registerHost({ host, groupId: "g1" });

    expect(reported).toContain("host-inline-transform");
  });

  it("says nothing about a host with no transform of its own", () => {
    const reported: string[] = [];
    const instance = root({ diagnosticSink: ({ diagnostic }) => reported.push(diagnostic.code) });
    withHost(instance);

    expect(reported).not.toContain("host-inline-transform");
  });
});
