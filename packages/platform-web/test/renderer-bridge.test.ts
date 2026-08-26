/**
 * The frame conversion: `renderInput()` → renderer groups.
 *
 * This is the half of the bridge with no device in it, and it carries the
 * decisions worth pinning — which groups the GPU draws at all, which of them
 * bind a backdrop, how a measured rect becomes X8's channel vector, and which
 * plane a surface lands on. The GPU half is exercised in the Playwright suite,
 * against a real adapter, because nothing short of one proves it.
 *
 * The renderer's own input types are reached through its public interface in
 * `renderer-bridge.ts`, so a signature change in C6 fails this file's *build*
 * rather than one of its assertions.
 */

import {
  NOMINAL_ACCESSIBILITY_POLICY,
  type BackdropProvider,
  type GlassGroupState,
  type GlassRenderer,
  type WebGPURendererModule,
} from "@vitreajs/vitrea";
import { DEFAULT_GROUP_UNION, groupUnionFromMergeDistance } from "@vitrea/geometry";
import { describe, expect, it, vi } from "vitest";

import { IDLE_CHANNELS } from "../src/channels";
import { createPlatformDiagnosticsChannel } from "../src/diagnostics";
import { MATERIAL_OPTICS } from "../src/optics";
import { createGlassLayerManager } from "../src/planes";
import {
  createGlassRendererBridge,
  toRendererGroups,
  toRendererResolution,
} from "../src/renderer-bridge";
import type {
  GlassFrameRenderInput,
  GlassGroupRenderInput,
  GlassNodeRenderInput,
  GlassPlaneRenderInput,
} from "../src/root";

const WEBGPU_TEXTURE_STATE: GlassGroupState = {
  configuredSource: "texture",
  activeRenderer: "webgpu",
  samplingBackend: "gpu-texture",
  refraction: "true",
  analysis: "exact",
  health: "ok",
};

const WEBGPU_DOM_STATE: GlassGroupState = {
  configuredSource: "dom",
  activeRenderer: "webgpu",
  samplingBackend: "css-backdrop",
  refraction: "approximate",
  analysis: "hint",
  health: "ok",
};

const CSS_STATE: GlassGroupState = {
  configuredSource: "dom",
  activeRenderer: "css",
  samplingBackend: "css-backdrop",
  refraction: "none",
  analysis: "none",
  health: "demoted",
  demotionReason: "no-webgpu",
};

const node = (overrides: Partial<GlassNodeRenderInput> = {}): GlassNodeRenderInput => ({
  nodeId: "n1",
  groupId: "g1",
  plane: "base",
  order: 0,
  bounds: { x: 100, y: 50, width: 200, height: 80 },
  shapeFamily: "fixed-rounded-rect",
  radii: [22, 22, 22, 22],
  smoothing: 0.6,
  thickness: 10,
  channels: IDLE_CHANNELS,
  material: { variant: "regular", adaptation: "adaptive" },
  foreground: { adaptation: { mode: "fixed" } },
  optics: MATERIAL_OPTICS.regular,
  refraction: { state: "true", accessibilityCap: "true", effective: "true" },
  ownedTransform: undefined,
  ...overrides,
});

const group = (overrides: Partial<GlassGroupRenderInput> = {}): GlassGroupRenderInput => ({
  groupId: "g1",
  state: WEBGPU_TEXTURE_STATE,
  probe: { groupId: "g1", verdict: "pass", breaks: [], reach: "verified" },
  backdropSourceId: "src",
  variant: "regular",
  samplingPadding: 24,
  mergeDistance: 24,
  declaredMergeDistance: undefined,
  blurRadius: 8,
  ...overrides,
});

const frame = (
  groups: readonly GlassGroupRenderInput[],
  planes: readonly { plane: GlassPlaneRenderInput["plane"]; nodes: readonly GlassNodeRenderInput[] }[],
): GlassFrameRenderInput => ({
  frame: { id: 1, timeMs: 16 },
  accessibility: NOMINAL_ACCESSIBILITY_POLICY,
  planes: planes.map((entry) => ({
    plane: entry.plane,
    // The layer DOM is never read by the conversion; it travels for the bridge's
    // own use, and a cast keeps this fixture from building a document.
    layers: undefined as unknown as GlassPlaneRenderInput["layers"],
    nodes: entry.nodes,
  })),
  groups,
  viewport: { width: 1280, height: 720, devicePixelRatio: 2 },
  device: undefined,
});

const always = (): boolean => true;
const never = (): boolean => false;

describe("toRendererGroups", () => {
  it("turns a measured rect into X8's channel vector", () => {
    const [base] = toRendererGroups(frame([group()], [{ plane: "base", nodes: [node()] }]), always);
    const surface = base?.groups[0]?.surfaces[0];

    // `bounds` is a top-left rect; the shape channels are centre-and-extent.
    expect(surface?.shape.center).toEqual([200, 90]);
    expect(surface?.shape.size).toEqual([200, 80]);
    expect(surface?.shape.radii).toEqual([22, 22, 22, 22]);
    expect(surface?.shape.smoothing).toBe(0.6);
    expect(surface?.shape.thickness).toBe(10);
    expect(surface?.family).toBe("fixed-rounded-rect");
    expect(surface?.variant).toBe("regular");
  });

  it("carries the channel values straight through", () => {
    const channels = { press: 0.3, glow: 0.9, sweep: 0.1, lensStrength: 1.2, pressPoint: [150, 70] as const };
    const [base] = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node({ channels })] }]),
      always,
    );

    expect(base?.groups[0]?.surfaces[0]?.channels).toEqual(channels);
  });

  it("binds a backdrop only where the state sampled one and pixels were supplied", () => {
    const bound = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node()] }]),
      always,
    )[0]?.groups[0];
    expect(bound?.backdropSourceId).toBe("src");

    // Declared as a texture, but nobody ever called `setBackdropTexture`. Binding
    // the id anyway would ask the renderer to sample a source it has no provider
    // for, which is a skipped group rather than an honest state.
    const unsupplied = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node()] }]),
      never,
    )[0]?.groups[0];
    expect(unsupplied?.backdropSourceId).toBeUndefined();
  });

  it("gives a dom-mode group no source at all, so it builds no pyramid", () => {
    // §honesty core: in dom-backdrop mode the browser compositor does the blur
    // and the GPU renders rim, tint and glow. An unbound source is what makes
    // "the GPU builds no pyramid at all" true rather than described.
    const [base] = toRendererGroups(
      frame(
        [group({ state: WEBGPU_DOM_STATE, backdropSourceId: "vitrea.dom" })],
        [{ plane: "base", nodes: [node()] }],
      ),
      always,
    );

    expect(base?.groups[0]?.backdropSourceId).toBeUndefined();
    expect(base?.groups[0]?.refraction).toBe("approximate");
    expect(base?.groups[0]?.analysisExact).toBe(false);
  });

  it("omits a group core resolved to the CSS tier", () => {
    // The CSS tier is painting this group's host in the same frame. Drawing it
    // here too would put two materials on one surface.
    const [base] = toRendererGroups(
      frame([group({ state: CSS_STATE })], [{ plane: "base", nodes: [node()] }]),
      always,
    );

    expect(base?.groups).toHaveLength(0);
  });

  it("reports analysisExact only where X2 resolved exact analysis", () => {
    const exact = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node()] }]),
      always,
    )[0]?.groups[0];
    expect(exact?.analysisExact).toBe(true);
  });

  it("splits surfaces by plane and keeps the group on both", () => {
    // A group whose members straddle a promotion draws on each plane's canvas
    // pair. It keeps its entry on both — with an empty surface list where it has
    // nothing — because removing and re-adding it would discard the renderer's
    // cached field target twice a frame.
    const planes = toRendererGroups(
      frame(
        [group()],
        [
          { plane: "base", nodes: [node({ nodeId: "a" })] },
          { plane: "overlay", nodes: [node({ nodeId: "b", plane: "overlay" })] },
        ],
      ),
      always,
    );

    expect(planes.map((entry) => entry.plane)).toEqual(["base", "overlay"]);
    expect(planes[0]?.groups[0]?.surfaces.map((surface) => surface.nodeId)).toEqual(["a"]);
    expect(planes[1]?.groups[0]?.surfaces.map((surface) => surface.nodeId)).toEqual(["b"]);
  });

  it("forwards DEFAULT_GROUP_UNION when the group declared no mergeDistance", () => {
    // K3: before this wiring, the renderer's DEFAULT_GROUP_UNION was reached by
    // omission (the `union` field was simply absent). Now it is forwarded
    // explicitly, but the values — and the no-declaration case — must be
    // identical to what the renderer already defaulted to.
    const [base] = toRendererGroups(
      frame([group({ declaredMergeDistance: undefined })], [{ plane: "base", nodes: [node()] }]),
      always,
    );

    expect(base?.groups[0]?.union).toEqual(DEFAULT_GROUP_UNION);
  });

  it("derives the union params from a declared mergeDistance", () => {
    const [base] = toRendererGroups(
      frame([group({ declaredMergeDistance: 40 })], [{ plane: "base", nodes: [node()] }]),
      always,
    );

    expect(base?.groups[0]?.union).toEqual(groupUnionFromMergeDistance(40));
    expect(base?.groups[0]?.union).toEqual({
      neckWidth: 20,
      maxBulge: 5,
      separationThreshold: 40,
    });
  });

  it("leaves a plane's group empty rather than dropping it", () => {
    const planes = toRendererGroups(
      frame(
        [group()],
        [
          { plane: "base", nodes: [node()] },
          { plane: "overlay", nodes: [] },
        ],
      ),
      always,
    );

    expect(planes[1]?.groups).toHaveLength(1);
    expect(planes[1]?.groups[0]?.surfaces).toEqual([]);
  });
});

describe("toRendererResolution", () => {
  it("hands core's resolved state through as the renderer's authority", () => {
    const resolution = toRendererResolution(
      frame(
        [group(), group({ groupId: "g2", state: WEBGPU_DOM_STATE })],
        [{ plane: "base", nodes: [node()] }],
      ),
    );

    expect(resolution.groups).toEqual([
      { groupId: "g1", state: { refraction: "true", analysis: "exact", samplingBackend: "gpu-texture" } },
      {
        groupId: "g2",
        state: { refraction: "approximate", analysis: "hint", samplingBackend: "css-backdrop" },
      },
    ]);
  });

  it("carries the accessibility policy, which is the other half of the dual cap", () => {
    // Decision Log #19: the renderer honours the lower of the accessibility cap
    // and the state's refraction. Handing it a pre-collapsed number would take
    // that fold away from the side that owns it.
    const resolution = toRendererResolution(frame([group()], [{ plane: "base", nodes: [node()] }]));

    expect(resolution.accessibility.material).toBe(NOMINAL_ACCESSIBILITY_POLICY.material);
  });

  it("includes a CSS-tier group, so the renderer sees the whole frame's state", () => {
    const resolution = toRendererResolution(
      frame([group({ state: CSS_STATE })], [{ plane: "base", nodes: [] }]),
    );

    expect(resolution.groups).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// The bridge itself, against a stubbed X7 seam
// ---------------------------------------------------------------------------

/**
 * The `load` option exists so this half needs no adapter. What it buys is the
 * two decisions that are about *when* the bridge acts rather than what it
 * converts: whether a frame that cannot draw is allowed to spend core's rebuild
 * claims, and what the bridge answers about a source's pixels.
 */
function stubModule(): {
  readonly module: WebGPURendererModule;
  readonly renderer: {
    ready: boolean;
    unbuiltSources: readonly string[];
    readonly registered: { id: string; generation: number }[];
    readonly drawn: unknown[];
  };
} {
  const registered: { id: string; generation: number }[] = [];
  const drawn: unknown[] = [];
  const renderer = {
    backend: "webgpu" as const,
    ready: true,
    unbuiltSources: [] as readonly string[],
    registered,
    drawn,
    deviceStatus: { generation: 7 },
    attachDevice: () => {},
    replaceDevice: () => {},
    registerBackdrop: (provider: { id: string; generation: number }) => {
      registered.push({ id: provider.id, generation: provider.generation });
    },
    unregisterBackdrop: (sourceId: string) => {
      const at = registered.findIndex((entry) => entry.id === sourceId);
      if (at >= 0) registered.splice(at, 1);
    },
    setViewport: () => {},
    setAccessibility: () => {},
    setMaterialProfile: () => {},
    setGroup: () => {},
    removeGroup: () => {},
    drawFrame: (args: unknown) => {
      drawn.push(args);
      return { groupsDrawn: 0, rebuilds: 0, skipped: [], unbuilt: [] };
    },
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

  return { module, renderer };
}

/** jsdom canvases refuse every context; the bridge only needs a configurable one. */
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

async function attachedBridge(): Promise<{
  readonly bridge: ReturnType<typeof createGlassRendererBridge>;
  readonly renderer: ReturnType<typeof stubModule>["renderer"];
  readonly restore: () => void;
  readonly unavailable: () => number;
}> {
  const restore = stubCanvasContexts();
  const { module, renderer } = stubModule();
  let unavailable = 0;
  const bridge = createGlassRendererBridge({
    layers: createGlassLayerManager({ document }),
    diagnostics: createPlatformDiagnosticsChannel(),
    onRendererUnavailable: () => {
      unavailable += 1;
    },
    load: async () => module,
  });
  bridge.syncDevice({
    available: true,
    deviceHealth: "ok",
    ownership: "vitrea",
    device: idleDevice(),
  });
  await bridge.ready();
  return { bridge, renderer, restore, unavailable: () => unavailable };
}

describe("the dirty set is consumed only where something can build it", () => {
  it("does not consume on a bridge that cannot draw", () => {
    const bridge = createGlassRendererBridge({
      layers: createGlassLayerManager({ document }),
      diagnostics: createPlatformDiagnosticsChannel(),
      onRendererUnavailable: () => {},
      load: async () => stubModule().module,
    });
    const consume = vi.fn(() => []);

    // No device yet, so `active()` is false. Consuming here would still commit
    // `builtEpoch` in core — and the one-shot dirty mark a startup raster or a
    // device-loss recovery depends on would be spent on a frame that built
    // nothing, with nothing to mark it dirty again.
    bridge.write(frame([group()], [{ plane: "base", nodes: [node()] }]), consume);

    expect(consume).not.toHaveBeenCalled();
  });

  it("consumes exactly once on a bridge that can", async () => {
    const { bridge, restore } = await attachedBridge();
    const consume = vi.fn(() => []);

    expect(bridge.active).toBe(true);
    bridge.write(frame([group()], [{ plane: "base", nodes: [node()] }]), consume);

    expect(consume).toHaveBeenCalledTimes(1);
    restore();
  });

  it("carries the rebuilds on the first plane's draw and no other", async () => {
    const { bridge, renderer, restore } = await attachedBridge();
    const rebuild = { sourceId: "src", epoch: 1, resolution: "native", groupIds: ["g1"] };
    bridge.write(
      frame([group()], [{ plane: "base", nodes: [node()] }, { plane: "overlay", nodes: [] }]),
      () => [rebuild] as never,
    );
    bridge.render();

    const rebuilds = renderer.drawn.map((args) => (args as { rebuild: unknown[] }).rebuild);
    expect(rebuilds).toEqual([[rebuild], []]);
    restore();
  });

  it("hands back the sources the renderer could not build", async () => {
    const { bridge, renderer, restore } = await attachedBridge();
    renderer.unbuiltSources = ["src"];
    bridge.write(frame([group()], [{ plane: "base", nodes: [node()] }]), () => []);

    expect(bridge.render()).toEqual(["src"]);
    restore();
  });
});

describe("what the bridge knows about a source's pixels", () => {
  const canvas = { kind: "canvas", canvas: document.createElement("canvas") } as const;
  const image = { kind: "image", image: document.createElement("img") } as const;
  const video = { kind: "video", video: document.createElement("video") } as const;

  it("answers the supply question, not the provider question", () => {
    const bridge = createGlassRendererBridge({
      layers: createGlassLayerManager({ document }),
      diagnostics: createPlatformDiagnosticsChannel(),
      onRendererUnavailable: () => {},
      load: async () => stubModule().module,
    });

    expect(bridge.hasBackdropTexture("src")).toBe(false);
    // No device, so no provider was built — and the pixels are still supplied.
    // Reporting them absent would demote the group for the whole handshake.
    bridge.setBackdropTexture("src", canvas);
    expect(bridge.hasBackdropTexture("src")).toBe(true);
    bridge.setBackdropTexture("src", undefined);
    expect(bridge.hasBackdropTexture("src")).toBe(false);
  });

  it("names video and canvas as per-frame, and a decoded image as not", () => {
    const bridge = createGlassRendererBridge({
      layers: createGlassLayerManager({ document }),
      diagnostics: createPlatformDiagnosticsChannel(),
      onRendererUnavailable: () => {},
      load: async () => stubModule().module,
    });
    bridge.setBackdropTexture("live-canvas", canvas);
    bridge.setBackdropTexture("still", image);
    bridge.setBackdropTexture("clip", video);

    expect([...bridge.perFrameBackdropSources()].sort()).toEqual(["clip", "live-canvas"]);
  });

  it("builds providers at the renderer's current generation, not at zero", async () => {
    const { bridge, renderer, restore } = await attachedBridge();
    bridge.setBackdropTexture("src", canvas);
    bridge.setBackdropTexture("clip", video);

    // A provider left at generation 0 while the renderer is already past it is
    // invalidated on the first device replacement, throwing away storage that was
    // built for the live device.
    expect(renderer.registered).toEqual([
      { id: "src", generation: 7 },
      { id: "clip", generation: 7 },
    ]);
    restore();
  });
});
