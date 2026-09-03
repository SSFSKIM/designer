/**
 * Where a texture backdrop sits (claims §5.47), from the element the app handed
 * over to the number the renderer maps it through.
 *
 * Three seams, one property each: the geometry sync measures a source element
 * in its batch and forgets one that measures to nothing; the bridge forwards a
 * placement to the renderer, including one that arrived before the renderer
 * did; and the root resolves what to measure — the element, a declared box, or
 * nothing but a warning — when the texture is supplied.
 */
import type {
  BackdropProvider,
  GlassRenderer,
  Rect,
  WebGPURendererModule,
} from "@vitreajs/vitrea";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createPlatformDiagnosticsChannel, type PlatformDiagnostic } from "../src/diagnostics";
import { createGeometrySync } from "../src/geometry-sync";
import { createLayoutReadMeter } from "../src/measure";
import type { MediaMatcher } from "../src/media-policy";
import { createGlassLayerManager } from "../src/planes";
import { createGlassRendererBridge } from "../src/renderer-bridge";
import { createGlassRoot, type GlassRoot } from "../src/root";

class StubResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

const matcher: MediaMatcher = () => ({
  matches: false,
  media: "(prefers-reduced-motion: reduce)",
  addEventListener: () => {},
  removeEventListener: () => {},
});

/** jsdom lays nothing out, so a box is whatever the test says it is. */
function boxed<T extends Element>(element: T, rect: Rect): T {
  element.getBoundingClientRect = () =>
    ({ ...rect, top: rect.y, left: rect.x, right: rect.x + rect.width, bottom: rect.y + rect.height, toJSON: () => rect }) as DOMRect;
  return element;
}

/** A renderer stand-in that records what the bridge tells it about placement. */
function stubModule() {
  const placements: { id: string; placement: Rect | undefined }[] = [];
  const renderer = {
    deviceStatus: { generation: 1 },
    unbuiltSources: [],
    attachDevice: () => {},
    replaceDevice: () => {},
    markWebGPUUnavailable: () => {},
    registerBackdrop: () => {},
    unregisterBackdrop: () => {},
    setBackdropPlacement: (id: string, placement: Rect | undefined) => {
      placements.push({ id, placement });
    },
    setViewport: () => {},
    setAccessibility: () => {},
    setMaterialProfile: () => {},
    setGroup: () => {},
    removeGroup: () => {},
    drawFrame: () => ({ groupsDrawn: 0, rebuilds: 0, skipped: [], unbuilt: [] }),
    collectAdaptation: async () => {},
    destroy: () => {},
  };
  const module = {
    createWebGPURenderer: () => renderer as unknown as GlassRenderer,
    createCopyProvider: (options: { id: string; generation?: number }) =>
      ({ id: options.id, generation: options.generation ?? 0 }) as unknown as BackdropProvider,
    createVideoProvider: (options: { id: string; generation?: number }) =>
      ({ id: options.id, generation: options.generation ?? 0 }) as unknown as BackdropProvider,
  } satisfies WebGPURendererModule;
  return { module, placements };
}

const stubCanvasContexts = (): (() => void) => {
  const original = HTMLCanvasElement.prototype.getContext;
  (HTMLCanvasElement.prototype as { getContext: unknown }).getContext = () => ({
    configure: () => {},
    unconfigure: () => {},
    getCurrentTexture: () => ({ createView: () => ({}) }),
  });
  return () => {
    (HTMLCanvasElement.prototype as { getContext: unknown }).getContext = original;
  };
};

const idleDevice = (): GPUDevice =>
  ({ lost: new Promise<never>(() => {}), destroy: () => {} }) as unknown as GPUDevice;

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
  (globalThis as { ImageBitmap?: unknown }).ImageBitmap ??= class ImageBitmap {};
});

describe("the geometry sync measures a source element in its batch", () => {
  it("reads the element's box on the next read and answers it back", () => {
    const meter = createLayoutReadMeter();
    const scene = { setNodeBounds: () => {} } as unknown as Parameters<typeof createGeometrySync>[0]["scene"];
    const geometry = createGeometrySync({ scene, meter, window });
    const image = boxed(document.createElement("img"), { x: 681, y: 48, width: 320, height: 200 });
    document.body.append(image);

    geometry.trackSource("raster", image);
    expect(geometry.hasSource("raster")).toBe(true);
    expect(geometry.placementOf("raster")).toBeUndefined();

    geometry.read();
    expect(geometry.placementOf("raster")).toEqual({ x: 681, y: 48, width: 320, height: 200 });
    expect(meter.counts.rects).toBe(1);

    // Clean: the next read touches nothing.
    geometry.read();
    expect(meter.counts.rects).toBe(1);

    // Dirtied with everything else — a document scroll or a viewport resize
    // reaches `markAllDirty` — the new box replaces the old.
    boxed(image, { x: 681, y: -152, width: 320, height: 200 });
    geometry.markAllDirty();
    geometry.read();
    expect(geometry.placementOf("raster")?.y).toBe(-152);
    expect(meter.counts.rects).toBe(2);

    geometry.untrackSource("raster");
    expect(geometry.hasSource("raster")).toBe(false);
    expect(geometry.placementOf("raster")).toBeUndefined();
    geometry.destroy();
    image.remove();
  });

  it("has no placement for an element that measures to nothing", () => {
    const meter = createLayoutReadMeter();
    const scene = { setNodeBounds: () => {} } as unknown as Parameters<typeof createGeometrySync>[0]["scene"];
    const geometry = createGeometrySync({ scene, meter, window });
    const canvas = boxed(document.createElement("canvas"), { x: 0, y: 0, width: 0, height: 0 });
    document.body.append(canvas);
    geometry.trackSource("hidden", canvas);
    geometry.read();
    expect(geometry.hasSource("hidden")).toBe(true);
    expect(geometry.placementOf("hidden")).toBeUndefined();
    geometry.destroy();
    canvas.remove();
  });
});

describe("the bridge forwards a placement", () => {
  it("to the renderer it has, and to the one that arrives later", async () => {
    const restore = stubCanvasContexts();
    try {
      const { module, placements } = stubModule();
      const bridge = createGlassRendererBridge({
        layers: createGlassLayerManager({ document }),
        diagnostics: createPlatformDiagnosticsChannel(),
        onRendererUnavailable: () => {},
        load: async () => module,
      });
      const early = { x: 1, y: 2, width: 30, height: 40 };
      // Before the renderer exists: held, not lost.
      bridge.setBackdropPlacement("bg", early);
      expect(placements).toEqual([]);

      bridge.syncDevice({
        available: true,
        deviceHealth: "ok",
        ownership: "vitrea",
        device: idleDevice(),
      });
      await bridge.ready();
      expect(placements).toEqual([{ id: "bg", placement: early }]);

      const later = { x: 5, y: 6, width: 70, height: 80 };
      bridge.setBackdropPlacement("bg", later);
      bridge.setBackdropPlacement("bg", undefined);
      expect(placements.slice(1)).toEqual([
        { id: "bg", placement: later },
        { id: "bg", placement: undefined },
      ]);
      bridge.destroy();
    } finally {
      restore();
    }
  });
});

describe("the root decides what places a supplied texture", () => {
  let roots: GlassRoot[] = [];
  let containers: HTMLElement[] = [];
  let restore: (() => void) | undefined;

  const webgpuRoot = (): { root: GlassRoot; placements: ReturnType<typeof stubModule>["placements"]; findings: PlatformDiagnostic[] } => {
    restore ??= stubCanvasContexts();
    const { module, placements } = stubModule();
    const findings: PlatformDiagnostic[] = [];
    const container = document.createElement("div");
    document.body.append(container);
    containers.push(container);
    const root = createGlassRoot({
      container,
      autoStart: false,
      matcher,
      renderer: "webgpu",
      webgpu: { device: idleDevice(), load: async () => module },
      diagnosticSink: ({ diagnostic }) => {
        findings.push(diagnostic as PlatformDiagnostic);
      },
    });
    roots.push(root);
    return { root, placements, findings };
  };

  afterEach(() => {
    for (const root of roots) root.destroy();
    for (const container of containers) container.remove();
    roots = [];
    containers = [];
    restore?.();
    restore = undefined;
  });

  it("measures the element in the document and hands its box to the bridge each frame", async () => {
    const { root, placements, findings } = webgpuRoot();
    await root.ready();
    root.registerBackdropSource({
      id: "raster",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    const image = boxed(document.createElement("img"), { x: 681, y: 48, width: 320, height: 200 });
    document.body.append(image);
    root.setBackdropTexture("raster", { kind: "image", image });

    root.runFrame(16);
    expect(placements.at(-1)).toEqual({
      id: "raster",
      placement: { x: 681, y: 48, width: 320, height: 200 },
    });
    expect(findings.map((finding) => finding.code)).not.toContain("backdrop-texture-unplaced");

    // Withdrawn: the placement goes with it.
    root.setBackdropTexture("raster", undefined);
    expect(placements.at(-1)).toEqual({ id: "raster", placement: undefined });
    image.remove();
  });

  it("takes a declared box over the element, and an element declared in the source's place", async () => {
    const { root, placements } = webgpuRoot();
    await root.ready();
    root.registerBackdropSource({
      id: "bitmap",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    const canvas = boxed(document.createElement("canvas"), { x: 10, y: 20, width: 300, height: 100 });
    document.body.append(canvas);

    const rect = { x: 100, y: 200, width: 50, height: 25 };
    root.setBackdropTexture("bitmap", { kind: "canvas", canvas, placement: { kind: "rect", rect } });
    expect(placements.at(-1)).toEqual({ id: "bitmap", placement: rect });

    const stand = boxed(document.createElement("div"), { x: 7, y: 8, width: 90, height: 60 });
    document.body.append(stand);
    root.setBackdropTexture("bitmap", {
      kind: "canvas",
      canvas,
      placement: { kind: "element", element: stand },
    });
    root.runFrame(16);
    expect(placements.at(-1)).toEqual({ id: "bitmap", placement: { x: 7, y: 8, width: 90, height: 60 } });
    canvas.remove();
    stand.remove();
  });

  it("falls back to the cover fit for a source with no box, and says so once", async () => {
    const { root, placements, findings } = webgpuRoot();
    await root.ready();
    root.registerBackdropSource({
      id: "loose",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    // In the document is what makes an element a box; this one is not.
    const detached = boxed(document.createElement("img"), { x: 0, y: 0, width: 320, height: 200 });
    root.setBackdropTexture("loose", { kind: "image", image: detached });
    expect(placements.at(-1)).toEqual({ id: "loose", placement: undefined });
    const unplaced = findings.filter((finding) => finding.code === "backdrop-texture-unplaced");
    expect(unplaced).toHaveLength(1);
    expect(unplaced[0]?.subjects).toEqual(["loose"]);
    expect(unplaced[0]?.message).toContain("cover fit");

    // Supplied again the same way: the channel collapses the repeat.
    root.setBackdropTexture("loose", { kind: "image", image: detached });
    expect(findings.filter((finding) => finding.code === "backdrop-texture-unplaced")).toHaveLength(1);
  });
});
