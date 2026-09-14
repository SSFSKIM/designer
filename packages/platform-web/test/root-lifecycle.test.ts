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
import type { SurfaceBackdropToneAbscissa } from "@vitreajs/vitrea";

import { createGlassRoot, type GlassRoot, type GlassRootOptions } from "../src/root";
import type { MediaMatcher } from "../src/media-policy";
import { COLOR_SCHEME_MEDIA_QUERY } from "../src/color-scheme";

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

  /*
   * Supply, then declare (#41(k)).
   *
   * Both READMEs promise the two halves commute — "the id joins the two halves;
   * the order does not matter" — and every path in this repo happens to declare
   * first, which is exactly why the other order was never exercised. A cached
   * `<img>` whose `onLoad` fires before the group's effect has run is the
   * ordinary way an app arrives at it.
   */
  /**
   * An **image** source, deliberately, because it is the only kind that stays
   * stuck. A canvas or video source is re-marked every frame by kind
   * (`perFrameBackdropSources`), so it recovers on the next frame whatever the
   * declaration order; a decoded image is handed over exactly once, and if that
   * hand-over raises no epoch nothing ever raises one.
   */
  const imageTexture = { kind: "image", image: document.createElement("img") } as const;

  const declareSource = (instance: GlassRoot): void => {
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
  };

  it("imports an image handed over before its source was declared", () => {
    const instance = root({ renderer: "webgpu" });

    instance.setBackdropTexture("src", imageTexture);
    declareSource(instance);
    withHost(instance, { sourceId: "src" });

    // The bridge held the pixels all along — that half always worked, and is
    // what made the failure so quiet: the group reported a supplied source and
    // full health while nothing was ever imported.
    expect(instance.rendererBridge?.hasBackdropTexture("src")).toBe(true);

    // The half that was missing.
    expect(instance.scene.dirtyBackdropSources().map((source) => source.descriptor.id)).toEqual([
      "src",
    ]);
  });

  it("hands that image to the renderer for rebuild, once", () => {
    // The observable an app actually cares about: the pixels reach a rebuild.
    // Asserting the epoch alone would leave the seam between the ledger and the
    // hand-out untested, and that seam is where a doubled mark would show — the
    // source would still read dirty after the frame that rebuilt it.
    const instance = root({ renderer: "webgpu" });

    instance.setBackdropTexture("src", imageTexture);
    declareSource(instance);
    withHost(instance, { sourceId: "src" });

    instance.runFrame(0);
    expect(instance.scene.consumeDirtyBackdropSources(999).map((entry) => entry.sourceId)).toEqual([
      "src",
    ]);
    expect(instance.scene.dirtyBackdropSources()).toEqual([]);

    instance.runFrame(16);
    expect(instance.scene.dirtyBackdropSources()).toEqual([]);
  });

  it("declares clean where nothing was ever supplied", () => {
    // The guard is `hasBackdropTexture`, not "this is a texture source": a
    // declaration on its own has no pixels to import and must not claim a
    // rebuild the renderer would then do over nothing.
    const instance = root({ renderer: "webgpu" });

    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    withHost(instance, { sourceId: "src" });

    expect(instance.scene.dirtyBackdropSources()).toEqual([]);
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
  readonly renderer: { unbuiltSources: readonly string[];
    backdropToneAbscissae(groupId: string): readonly SurfaceBackdropToneAbscissa[] };
  /** The rebuild source ids each frame carried, in frame order. */
  readonly rebuildsPerFrame: () => string[][];
} {
  const draws: { readonly frameId: number; readonly sources: readonly string[] }[] = [];
  const renderer = {
    backend: "webgpu",
    ready: true,
    deviceStatus: { generation: 1 },
    unbuiltSources: [] as readonly string[],
    backdropToneAbscissae: (): readonly SurfaceBackdropToneAbscissa[] => [],
    attachDevice: () => {},
    replaceDevice: () => {},
    registerBackdrop: () => {},
    unregisterBackdrop: () => {},
    setBackdropPlacement: () => {},
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

  it("keeps only the shared source fallback on an active GPU silhouette group", async () => {
    const { instance } = await gpuRoot();
    instance.setMaterialProfile({ backdropToneAbscissa: { kind: "silhouette" } });
    const original = HTMLCanvasElement.prototype.getContext;
    let reads = 0;
    HTMLCanvasElement.prototype.getContext = (() => ({
      configure() {}, unconfigure() {}, clearRect() {}, drawImage() {},
      getImageData() {
        reads += 1;
        return { data: new Uint8ClampedArray([128, 128, 128, 255]) };
      },
    })) as unknown as typeof original;
    try {
      for (let i = 0; i < 2; i += 1) {
        const host = document.createElement("div");
        host.getBoundingClientRect = () => ({ x: i * 10, y: 0, width: 10, height: 10,
          left: i * 10, right: i * 10 + 10, top: 0, bottom: 10, toJSON() {} });
        instance.plane("base").hostLayer.append(host);
        instance.registerHost({ host, groupId: "g1" });
      }
      const canvas = document.createElement("canvas");
      canvas.width = canvas.height = 1;
      instance.setBackdropTexture("src", { kind: "canvas", canvas });
      instance.runFrame(16);
      expect(instance.capabilities("g1")?.activeRenderer).toBe("webgpu");
      expect(reads).toBe(1);
      expect(instance.renderInput()?.groups[0]?.backdropToneLevel).toBeGreaterThan(0);
    } finally {
      HTMLCanvasElement.prototype.getContext = original;
    }
  });

  it("uses completed GPU local readings for the DOM overlays above each host", async () => {
    const { instance, gpu } = await gpuRoot();
    instance.setMaterialProfile({ backdropToneAbscissa: { kind: "silhouette" } });
    const canvas = document.createElement("canvas");
    instance.setBackdropTexture("src", { kind: "canvas", canvas });
    const inputs: SurfaceBackdropToneAbscissa[] = [];
    for (let i = 0; i < 2; i += 1) {
      const host = document.createElement("div");
      const rect = () => ({ x: i * 100, y: 0, width: 80, height: 80,
        left: i * 100, right: i * 100 + 80, top: 0, bottom: 80, toJSON() {} });
      host.getBoundingClientRect = rect;
      instance.plane("base").hostLayer.append(host);
      const handle = instance.registerHost({ host, groupId: "g1" });
      inputs.push({ surfaceId: handle.nodeId, kind: "silhouette", encodedLuminance: i,
        luminance: i, linearLuminance: i, color: [i, i, i], sampleCount: 6400,
        level: 0, sourceWidth: 300, sourceHeight: 150, sampledWidth: 300, sampledHeight: 150 });
      const overlay = withHost(instance, { groupId: `above-${i}`, plane: "overlay" });
      overlay.getBoundingClientRect = rect;
    }
    instance.runFrame(16);
    gpu.renderer.backdropToneAbscissae = (groupId) => groupId === "g1" ? inputs : [];
    instance.runFrame(32);
    const groups = instance.renderInput()!.groups;
    const low = groups.find((g) => g.groupId === "above-0");
    const high = groups.find((g) => g.groupId === "above-1");
    expect(instance.capabilities("g1")?.activeRenderer).toBe("webgpu");
    expect(low?.state.samplingBackend).toBe("css-backdrop");
    expect(low?.backdropToneLevel).toBeDefined();
    expect(high?.backdropToneLevel).toBeGreaterThan(low!.backdropToneLevel!);
  });

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

describe("a material profile the root cannot draw", () => {
  /*
   * `setMaterialProfile` re-derives every binding on both tiers from one patch,
   * and the response rows are resolved LAZILY — per host, per frame, inside
   * `materialAtBackdrop`, and only where the group has a backdrop reading. So a
   * patch whose three rows resolve to different knot counts would be accepted
   * here, replace the material that was drawing, and only fail later: once the
   * page has a reading, on every frame, from inside the write phase, with no
   * caller left to hand the error to. The refusal has to happen at the call the
   * app made, and it has to happen before anything moves.
   */
  const mixed = { backdropToneAnchorX: [0.1, 0.3, 0.7, 0.95] } as const;

  it("is refused at the call, and does not displace the material already applied", () => {
    const instance = root();
    const host = withHost(instance);
    // A patch the root CAN draw, so there is a material to lose.
    instance.setMaterialProfile({ optics: { regular: { tintAlpha: 0.8 } } });
    instance.runFrame(0);
    const applied = host.style.getPropertyValue("--vitrea-occlusion");
    expect(Number(applied)).toBeGreaterThan(0);

    expect(() => instance.setMaterialProfile(mixed)).toThrow(/backdrop tone response/);

    // The refused patch names no optics, so a root that had retained it would
    // publish the default occlusion on the next frame instead of this one.
    instance.runFrame(16);
    expect(host.style.getPropertyValue("--vitrea-occlusion")).toBe(applied);
  });

  it("does not survive the setter's refusal to poison a later scheme change", () => {
    /*
     * `setMaterialProfile` assigns the app's patch and THEN re-derives, so a
     * refusal used to leave the rejected patch held as the host profile. Nothing
     * looks wrong until the scheme changes: `setColorScheme` recomposes the
     * scheme's material with whatever host patch is held, so the root would throw
     * again — from a call that has nothing to do with the bad patch, and from
     * inside the system's own media listener when the scheme is "auto". One
     * refused call is a refusal; a refused call that poisons every later one is a
     * root the app cannot recover.
     */
    const instance = root();
    const host = withHost(instance);
    instance.setMaterialProfile({ optics: { regular: { tintAlpha: 0.8 } } });
    instance.runFrame(0);
    const applied = host.style.getPropertyValue("--vitrea-occlusion");

    expect(() => instance.setMaterialProfile(mixed)).toThrow(/backdrop tone response/);

    // The scheme change the refused patch must not reach.
    expect(() => instance.setColorScheme("dark")).not.toThrow();
    instance.runFrame(16);
    expect(instance.colorScheme).toBe("dark");
    // Back to light, where the patch that IS held is the one that was accepted.
    instance.setColorScheme("light");
    instance.runFrame(32);
    expect(host.style.getPropertyValue("--vitrea-occlusion")).toBe(applied);
  });

  it("is refused at construction too, where the bindings are built without the setter", () => {
    // `createGlassRoot` does not route its `materialProfile` option through
    // `applyMaterialProfile` — it initialises each binding from it directly — so
    // the setter's refusal does not cover the option. Same patch, same failure,
    // and a constructor that returns a root nobody can frame is the worse of the
    // two: there is no earlier call to attribute it to.
    expect(() => root({ materialProfile: mixed })).toThrow(/backdrop tone response/);
  });

  it("refuses before it builds a layer, installs a stylesheet or takes a listener", () => {
    /*
     * A constructor that throws never hands back the root, so `destroy()` is
     * unreachable and everything it would have released is leaked: the layer
     * elements in the caller's container, the ink stylesheet in the document, and
     * a media listener per preference feed. The refusal has to come before the
     * first of those, which means it cannot read the resolved scheme off the
     * colour-scheme feed — that feed IS one of the listeners. So both schemes are
     * checked instead, which is the stronger claim anyway: under "auto" the
     * system can flip the scheme later, and that recomposition runs inside the
     * media listener where a throw has no caller to reach.
     */
    const styles = (): number => document.querySelectorAll("style").length;
    let listeners = 0;
    const counting: MediaMatcher = (media) => ({
      matches: media === COLOR_SCHEME_MEDIA_QUERY,
      media,
      addEventListener: () => { listeners += 1; },
      removeEventListener: () => { listeners -= 1; },
    });

    for (const colorScheme of ["light", "dark", "auto"] as const) {
      const container = document.createElement("div");
      document.body.append(container);
      const before = styles();
      expect(() => createGlassRoot({
        container, autoStart: false, diagnosticSink: () => {},
        matcher: counting, colorScheme, materialProfile: mixed,
      }), colorScheme).toThrow(/backdrop tone response/);
      expect(container.childElementCount, colorScheme).toBe(0);
      expect(styles(), colorScheme).toBe(before);
      expect(listeners, colorScheme).toBe(0);
      container.remove();
    }
  });

  it("leaves the root able to take the next profile it is given", () => {
    const instance = root();
    const host = withHost(instance);
    expect(() => instance.setMaterialProfile(mixed)).toThrow(/backdrop tone response/);
    instance.setMaterialProfile({ optics: { regular: { tintAlpha: 0.8 } } });
    instance.runFrame(0);
    expect(Number(host.style.getPropertyValue("--vitrea-occlusion"))).toBeGreaterThan(0);
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
