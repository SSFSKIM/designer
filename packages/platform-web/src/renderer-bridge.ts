/**
 * The bridge: `renderInput()` on one side, the WebGPU renderer on the other.
 *
 * Everything either half needs already existed — `root.renderInput()` publishes
 * measured, resolved, capped surfaces; `@vitrea/renderer-webgpu` consumes groups
 * of surfaces with channel values — and nothing joined them. This module is that
 * join, and it lives here rather than in `vitrea-react` because the bindings are
 * thin by law: a Vue or Web Components adapter must inherit a working GPU tier
 * without reimplementing it.
 *
 * ## What it owns
 *
 * - **The lazy load.** The renderer arrives through `vitrea`'s X7 seam and
 *   nowhere else. This file contains no static edge to the renderer package, so a
 *   CSS-tier bundle still never carries a byte of WGSL.
 * - **The canvases.** X1's sandwich gives every plane an optics canvas and a
 *   highlight canvas; the renderer wants texture views. Configuring those
 *   contexts, and unconfiguring them when the device dies, is what makes the
 *   fallback *visible* rather than a stale GPU image sitting over CSS glass.
 * - **The per-frame conversion**, which is pure and tested as such.
 * - **The backdrop providers.** core's `TextureBackdropSource` declares that a
 *   source *is* a texture; it carries no pixels, because core may not know what
 *   an `HTMLCanvasElement` is. The pixels arrive through `setBackdropTexture`,
 *   and this module turns them into X3 providers on the current device.
 *
 * ## Why it draws once per plane
 *
 * §The rendering contract: one compositor — one device, one pipeline cache, one
 * texture pool — serving *one canvas pair per plane*. So there is one renderer
 * and two draws, and a group is handed to the plane it has surfaces on and an
 * empty surface list everywhere else, which the renderer skips. Removing and
 * re-adding the group instead would throw away its cached field target twice a
 * frame.
 *
 * ## What it does not own
 *
 * X2's resolved state. core decides which tier a group is on, from a platform
 * probe about the *browser*, and this module reads that answer rather than
 * arguing with it. It raises exactly one capability fact of its own — the
 * renderer chunk failing to resolve, which is `no-webgpu` in substance and has
 * no other honest name. Everything else it can fail at costs it the drawing and
 * nothing more, because inventing a state X2 does not enumerate would be the
 * same pretence from the other direction.
 */

import {
  loadWebGPURendererModule,
  type BackdropProvider,
  type GlassPlane,
  type GlassRenderer,
  type WebGPURendererModule,
} from "vitrea";
import { groupUnionFromMergeDistance } from "@vitrea/geometry";

import { IDLE_CHANNELS, type SurfaceChannelValues } from "./channels";
import type { PlatformDiagnosticsChannel } from "./diagnostics";
import type { GlassLayerManager } from "./planes";
import type { GlassFrameRenderInput } from "./root";
import type { WebGPUStatus } from "./webgpu";

/**
 * The renderer's own input types, reached through its public interface rather
 * than re-declared. A changed signature in C6 then breaks this file's build,
 * which is the only kind of pin worth having across a dynamic-import seam.
 */
export type RendererGroupInput = Parameters<GlassRenderer["setGroup"]>[0];
export type RendererSurfaceInput = RendererGroupInput["surfaces"][number];
export type RendererResolution = NonNullable<
  Parameters<GlassRenderer["drawFrame"]>[0]["resolution"]
>;
/**
 * The renderer's optical-tunables patch. Read off `setMaterialProfile` for the
 * same reason as the types above — and because this file may hold no runtime
 * edge to the renderer package (X7), a derived type is the only kind of pin
 * available here.
 */
export type RendererMaterialProfile = Parameters<GlassRenderer["setMaterialProfile"]>[0];

/** One plane's worth of groups, in the order the renderer will draw them. */
export interface RendererPlaneGroups {
  readonly plane: GlassPlane;
  readonly groups: readonly RendererGroupInput[];
}

/**
 * The pixels behind a texture-configured backdrop source.
 *
 * The two arms are the two WebGPU import paths, and they are separate because
 * their semantics are (§GPU device ownership): a copied image or canvas arrives
 * premultiplied and the renderer owns the destination texture, while an imported
 * external texture expires at task end and is re-acquired every frame that
 * samples it.
 */
export type GlassBackdropTexture =
  | {
      readonly kind: "canvas";
      readonly canvas: HTMLCanvasElement | OffscreenCanvas;
    }
  | {
      readonly kind: "image";
      readonly image: HTMLImageElement | ImageBitmap;
    }
  | {
      readonly kind: "video";
      readonly video: HTMLVideoElement;
    };

export interface GlassRendererBridgeOptions {
  readonly layers: GlassLayerManager;
  readonly diagnostics: PlatformDiagnosticsChannel;
  /**
   * Raised once, if the renderer chunk cannot be resolved at all.
   *
   * That is the one bridge-side failure with no honest name but `no-webgpu`:
   * there is no GPU tier in this session and nothing recovers it, which is
   * exactly what that reason's `"none"` recovery says. Everything else the
   * bridge can fail at — a canvas refusing a context, a device dying — either
   * has its own reason in X2 or is a transient, and neither may touch this. In
   * particular a lost device must not: core only raises `device-lost` where
   * `webgpu` is `"available"`, so withdrawing availability on loss would
   * collapse a fault whose recovery is `"device-restored"` into one whose
   * recovery is `"none"`.
   */
  readonly onRendererUnavailable: () => void;
  /** The X7 seam, swappable so a unit test needs no GPU. */
  readonly load?: () => Promise<WebGPURendererModule>;
  /**
   * Optical tunables the renderer should run on, forwarded verbatim.
   *
   * Forwarded and nothing else: the numbers belong to `material.ts` in the
   * renderer package, and a value restated here would be a second opinion about
   * a measurement this side never took.
   */
  readonly materialProfile?: RendererMaterialProfile;
}

export interface GlassRendererBridge {
  /** Attached, with a healthy device and configured canvases. */
  readonly active: boolean;
  readonly renderer: GlassRenderer | undefined;
  /** Resolves once the load attempt has settled, successfully or not. */
  ready(): Promise<void>;
  /** Follow the browser-side device lifecycle: attach, loss, replacement. */
  syncDevice(status: WebGPUStatus): void;
  setBackdropTexture(sourceId: string, texture: GlassBackdropTexture | undefined): void;
  /**
   * Replace the renderer's optical tunables. A patch replaces rather than
   * accumulates — that is the renderer's rule, and this only forwards it.
   * Applied to a renderer that has not loaded yet as soon as it does.
   */
  setMaterialProfile(profile: RendererMaterialProfile): void;
  /** The frame's `write` phase: CPU state only, no GPU work. */
  write(input: GlassFrameRenderInput, rebuilds: readonly RebuildRequest[]): void;
  /** The frame's `render` phase, with the scene graph frozen. */
  render(): void;
  destroy(): void;
}

/** core's `BackdropRebuildRequest`, as the renderer reads it. */
type RebuildRequest = NonNullable<Parameters<GlassRenderer["drawFrame"]>[0]["rebuild"]>[number];

// ---------------------------------------------------------------------------
// The conversion — pure, and the part worth unit-testing
// ---------------------------------------------------------------------------

/**
 * Whether a group draws on the GPU at all.
 *
 * `activeRenderer` is core's answer after the whole transition table, so this is
 * a read rather than a decision. A group that resolved to the CSS tier is having
 * its host styled by `root`'s write phase; drawing it here too would paint glass
 * twice, which is the one thing the tier split exists to prevent.
 */
const drawsOnGpu = (state: { readonly activeRenderer: "webgpu" | "css" }): boolean =>
  state.activeRenderer === "webgpu";

/**
 * Convert one frame's render input into per-plane renderer groups.
 *
 * `hasBackdrop` answers whether a registered provider exists for a source id.
 * The backdrop is bound only where core resolved `samplingBackend:
 * "gpu-texture"` *and* pixels were actually supplied: a dom-mode group binds no
 * source at all, so it builds no pyramid and the optics pass draws rim, tint and
 * glow over an unsampled backdrop — which is exactly what §honesty core promises
 * the `dom` + `hint` and `dom` + `none` states.
 *
 * `union` carries the group's own field-pass parameters, derived from its
 * declared `mergeDistance` via `groupUnionFromMergeDistance` (C7's flow-back
 * finding: nothing forwarded this before, so every group drew with the
 * renderer's hardcoded `DEFAULT_GROUP_UNION` regardless of what it declared).
 * A group with no declared `mergeDistance` gets `DEFAULT_GROUP_UNION` back
 * unchanged.
 */
export function toRendererGroups(
  input: GlassFrameRenderInput,
  hasBackdrop: (sourceId: string) => boolean,
): readonly RendererPlaneGroups[] {
  const surfacesByPlaneAndGroup = new Map<GlassPlane, Map<string, RendererSurfaceInput[]>>();

  for (const plane of input.planes) {
    const byGroup = new Map<string, RendererSurfaceInput[]>();
    for (const node of plane.nodes) {
      const list = byGroup.get(node.groupId) ?? [];
      list.push(toSurfaceInput(node));
      byGroup.set(node.groupId, list);
    }
    surfacesByPlaneAndGroup.set(plane.plane, byGroup);
  }

  return input.planes.map((plane) => ({
    plane: plane.plane,
    groups: input.groups
      .filter((group) => drawsOnGpu(group.state))
      .map((group) => {
        const sourceId = group.backdropSourceId;
        const sampled =
          sourceId !== undefined &&
          group.state.samplingBackend === "gpu-texture" &&
          hasBackdrop(sourceId);

        return {
          groupId: group.groupId,
          surfaces: surfacesByPlaneAndGroup.get(plane.plane)?.get(group.groupId) ?? [],
          refraction: group.state.refraction,
          analysisExact: group.state.analysis === "exact",
          variant: group.variant,
          union: groupUnionFromMergeDistance(group.declaredMergeDistance),
          ...(sampled ? { backdropSourceId: sourceId } : {}),
        };
      }),
  }));
}

/** X8's channel vector, lifted out of a measured rect. */
function toSurfaceInput(node: GlassFrameRenderInput["planes"][number]["nodes"][number]): RendererSurfaceInput {
  const { bounds } = node;
  return {
    nodeId: node.nodeId,
    family: node.shapeFamily,
    shape: {
      center: [bounds.x + bounds.width / 2, bounds.y + bounds.height / 2],
      size: [bounds.width, bounds.height],
      radii: node.radii,
      smoothing: node.smoothing,
      thickness: node.thickness,
    },
    variant: node.material.variant,
    channels: node.channels,
  };
}

/**
 * The frame's resolved state, in the renderer's structural view.
 *
 * The renderer prefers this over each group's own copy — core is the authority
 * on X2 — and it is also where the *other* half of the dual cap arrives, so the
 * renderer folds `min(accessibility cap, state refraction)` itself rather than
 * trusting a number this side pre-collapsed.
 */
export function toRendererResolution(input: GlassFrameRenderInput): RendererResolution {
  return {
    groups: input.groups.map((group) => ({
      groupId: group.groupId,
      state: {
        refraction: group.state.refraction,
        analysis: group.state.analysis,
        samplingBackend: group.state.samplingBackend,
      },
    })),
    accessibility: { material: input.accessibility.material },
  };
}

/** Idle channels, exported so a caller can name the default it is relying on. */
export const BRIDGE_IDLE_CHANNELS: SurfaceChannelValues = IDLE_CHANNELS;

// ---------------------------------------------------------------------------
// The bridge itself
// ---------------------------------------------------------------------------

interface PlaneContexts {
  readonly optics: GPUCanvasContext;
  readonly highlight: GPUCanvasContext;
}

const canvasContext = (canvas: HTMLCanvasElement): GPUCanvasContext | undefined => {
  // TypeScript's DOM lib still has no `"webgpu"` overload for `getContext`, the
  // same gap C6 records for the flag namespaces (Decision Log #23e). Drop the
  // assertion when the lib ships it.
  const context = canvas.getContext("webgpu") as GPUCanvasContext | null;
  return context === null ? undefined : context;
};

export function createGlassRendererBridge(
  options: GlassRendererBridgeOptions,
): GlassRendererBridge {
  const load = options.load ?? loadWebGPURendererModule;

  let moduleLoad: Promise<WebGPURendererModule | undefined> | undefined;
  let rendererModule: WebGPURendererModule | undefined;
  let renderer: GlassRenderer | undefined;
  let device: GPUDevice | undefined;
  let format: GPUTextureFormat | undefined;
  let destroyed = false;
  /** Latched: a canvas that refused a context will not accept one later either. */
  let canvasesRefused = false;
  /** The tunables to hand the renderer, whenever it arrives. Never interpreted here. */
  let materialProfile: RendererMaterialProfile | undefined = options.materialProfile;

  const contexts = new Map<GlassPlane, PlaneContexts>();
  const textures = new Map<string, GlassBackdropTexture>();
  const providers = new Map<string, BackdropProvider>();
  const liveGroups = new Set<string>();

  let pending:
    | {
        readonly input: GlassFrameRenderInput;
        readonly rebuilds: readonly RebuildRequest[];
        readonly planes: readonly RendererPlaneGroups[];
      }
    | undefined;

  const active = (): boolean =>
    !destroyed && renderer !== undefined && renderer.ready && contexts.size > 0;

  // -- canvases -------------------------------------------------------------

  /**
   * Give every plane's canvas pair a configured `"webgpu"` context.
   *
   * Failure here is reported and survived rather than thrown. It is not a
   * platform fact — X2 has no reason for it and none of the enumerated states
   * describes it — so what it costs is the drawing, not the state: `active()`
   * goes false, the CSS tier is untouched, and the diagnostic names what
   * happened. Refusing to build the root over it would take down an app for a
   * fault it cannot act on.
   */
  const configureCanvases = (gpu: GPUDevice): void => {
    // `getPreferredCanvasFormat` is the format the compositor does not have to
    // convert. The renderer's pipelines are keyed by target format, so handing it
    // the canvas' own format costs one more cached pipeline and no copy.
    format = navigator.gpu?.getPreferredCanvasFormat() ?? "bgra8unorm";
    contexts.clear();
    if (canvasesRefused) return;

    for (const layers of options.layers.planes) {
      const optics = canvasContext(layers.opticsCanvas);
      const highlight = canvasContext(layers.highlightCanvas);
      try {
        if (optics === undefined || highlight === undefined) {
          throw new Error('getContext("webgpu") returned null');
        }
        // Premultiplied because that is what the optics pass writes (X5: linear
        // premultiplied light, sRGB-encoded on the way out) and what its
        // `PREMULTIPLIED_OVER` blend assumes. Declaring "opaque" would make the
        // glass a solid rectangle over the page.
        for (const context of [optics, highlight]) {
          context.configure({ device: gpu, format, alphaMode: "premultiplied" });
        }
        contexts.set(layers.plane, { optics, highlight });
      } catch (error) {
        options.diagnostics.report({
          code: "webgpu-canvas-unavailable",
          severity: "warning",
          subjects: [layers.plane],
          message: `The "${layers.plane}" plane's canvases could not be configured for WebGPU (${error instanceof Error ? error.message : String(error)}), so the GPU tier cannot paint into X1's sandwich.`,
        });
        // Latched: no replacement device makes a canvas that refused a context
        // accept one, and retrying every frame would be a diagnostic storm.
        canvasesRefused = true;
        contexts.clear();
        return;
      }
    }
  };

  /**
   * Release the contexts and blank the canvases.
   *
   * Both halves are needed, and the second one is the surprise: `unconfigure()`
   * hands the device back, but the last presented frame stays on screen —
   * measured, over a canvas whose context was already released. Left there it
   * would sit above the CSS-tier glass that just took over, showing two
   * materials at once with nothing to say which is live. Acceptance #5 asks for
   * a degradation that looks intentional, and a ghost of the tier that just died
   * is the opposite.
   *
   * Resizing is what actually clears a canvas' backing store, whatever context
   * it holds. 1×1 rather than 0 because a zero-sized canvas is not a legal
   * WebGPU surface, and the next frame's `resizeCanvases` restores the real
   * extent either way.
   */
  const unconfigureCanvases = (): void => {
    for (const plane of contexts.values()) {
      plane.optics.unconfigure();
      plane.highlight.unconfigure();
    }
    contexts.clear();

    for (const layers of options.layers.planes) {
      for (const canvas of [layers.opticsCanvas, layers.highlightCanvas]) {
        canvas.width = 1;
        canvas.height = 1;
      }
    }
  };

  // -- backdrop providers ---------------------------------------------------

  const dropProviders = (): void => {
    for (const sourceId of [...providers.keys()]) {
      renderer?.unregisterBackdrop(sourceId);
      providers.delete(sourceId);
    }
  };

  /**
   * Build the provider for one texture source on the current device.
   *
   * Rebuilt from scratch on every device generation rather than patched: WebGPU
   * has no cross-device resource sharing, so a provider from a dead device holds
   * textures that can never be sampled again and would fail silently.
   */
  const buildProvider = (sourceId: string, texture: GlassBackdropTexture): void => {
    if (rendererModule === undefined || device === undefined || renderer === undefined) return;

    const provider =
      texture.kind === "video"
        ? rendererModule.createVideoProvider({
            id: sourceId,
            device,
            source: { kind: "element", element: texture.video },
          })
        : rendererModule.createCopyProvider({
            id: sourceId,
            kind: texture.kind === "canvas" ? "canvas" : "image",
            device,
            source: texture.kind === "canvas" ? texture.canvas : texture.image,
            ...sourceExtent(texture),
            // A canvas is repainted by its owner and a decoded image never
            // changes; that difference is what lets a static backdrop rebuild
            // nothing at all (§Core model's invariant).
            live: texture.kind === "canvas",
          });

    renderer.registerBackdrop(provider);
    providers.set(sourceId, provider);
  };

  const rebuildProviders = (): void => {
    dropProviders();
    for (const [sourceId, texture] of textures) buildProvider(sourceId, texture);
  };

  /**
   * Re-declare each copied source's extent before the frame acquires it.
   *
   * A live canvas is resized by its owner — the demo's backdrop tracks DPR — and
   * the provider allocates its destination texture from the declared extent, so
   * a stale one would copy a subrectangle for as long as the size held.
   */
  const refreshExtents = (): void => {
    for (const [sourceId, texture] of textures) {
      const provider = providers.get(sourceId);
      if (provider?.resize === undefined || texture.kind === "video") continue;
      const extent = sourceExtent(texture);
      provider.resize(extent.width, extent.height);
    }
  };

  // -- device lifecycle -----------------------------------------------------

  const attach = (gpu: GPUDevice, ownership: WebGPUStatus["ownership"]): void => {
    if (renderer === undefined || destroyed) return;
    device = gpu;
    renderer.attachDevice(gpu, ownership);
    configureCanvases(gpu);
    rebuildProviders();
  };

  const detach = (): void => {
    // Order matters: the providers hold resources from the device that just
    // died, and unconfiguring is what actually clears the pixels. A configured
    // canvas keeps its last frame on screen, which over CSS-tier glass would be
    // two materials at once and no way to tell which is live.
    dropProviders();
    unconfigureCanvases();
    device = undefined;
    liveGroups.clear();
    pending = undefined;
  };

  const ensureModule = async (): Promise<WebGPURendererModule | undefined> => {
    moduleLoad ??= load().then(
      (loaded) => loaded,
      (error: unknown) => {
        options.diagnostics.report({
          code: "webgpu-renderer-load-failed",
          severity: "warning",
          subjects: [],
          message: `The WebGPU renderer could not be loaded (${error instanceof Error ? error.message : String(error)}). This session renders on the CSS tier; core reports demotionReason "no-webgpu", whose recovery is honestly "none".`,
        });
        options.onRendererUnavailable();
        return undefined;
      },
    );
    const loaded = await moduleLoad;
    if (loaded === undefined || destroyed) return undefined;
    rendererModule ??= loaded;
    if (renderer === undefined) {
      renderer = loaded.createWebGPURenderer();
      // X7's seam declares `createWebGPURenderer()` with no arguments, so the
      // tunables arrive on the line after construction — which is still before the
      // renderer has a device, let alone a frame, so no frame ever draws on the
      // defaults when a profile was configured.
      if (materialProfile !== undefined) renderer.setMaterialProfile(materialProfile);
    }
    return loaded;
  };

  let deviceSync: Promise<void> = Promise.resolve();

  const syncDevice = (status: WebGPUStatus): void => {
    deviceSync = deviceSync.then(async () => {
      if (destroyed) return;

      if (status.device === undefined || status.deviceHealth !== "ok") {
        if (renderer !== undefined) detach();
        return;
      }
      if (status.device === device) return;

      if ((await ensureModule()) === undefined) return;
      // A second device on the same renderer is a replacement, and the renderer
      // draws a generation boundary at that point — every resource built under
      // the old one is unusable, which is why the providers are rebuilt above.
      if (device !== undefined) renderer?.replaceDevice(status.device);
      attach(status.device, status.ownership);
    });
  };

  // -- the frame ------------------------------------------------------------

  const write = (input: GlassFrameRenderInput, rebuilds: readonly RebuildRequest[]): void => {
    if (!active() || renderer === undefined) {
      pending = undefined;
      return;
    }

    const viewport = input.viewport;
    if (viewport !== undefined) {
      // A viewport change bumps the texture pool's size epoch, which is what
      // invalidates every dependent allocation (§GPU device ownership). The DPR
      // is part of it: a monitor swap changes the device extent of every group
      // field without changing a single CSS px.
      renderer.setViewport({
        widthCss: viewport.width,
        heightCss: viewport.height,
        devicePixelRatio: viewport.devicePixelRatio,
      });
    }
    renderer.setAccessibility(input.accessibility.material);
    refreshExtents();

    pending = {
      input,
      rebuilds,
      planes: toRendererGroups(input, (sourceId) => providers.has(sourceId)),
    };
  };

  const render = (): void => {
    const frame = pending;
    pending = undefined;
    if (frame === undefined || !active() || renderer === undefined) return;

    const drawn = new Set<string>();
    for (const group of frame.planes[0]?.groups ?? []) drawn.add(group.groupId);
    for (const groupId of liveGroups) {
      if (!drawn.has(groupId)) renderer.removeGroup(groupId);
    }
    liveGroups.clear();
    for (const groupId of drawn) liveGroups.add(groupId);

    const resolution = toRendererResolution(frame.input);
    let first = true;

    for (const plane of frame.planes) {
      const targets = contexts.get(plane.plane);
      if (targets === undefined) continue;
      for (const group of plane.groups) renderer.setGroup(group);

      renderer.drawFrame({
        frame: { id: frame.input.frame.id, timeMs: frame.input.frame.timeMs },
        optics: targets.optics.getCurrentTexture().createView(),
        highlight: targets.highlight.getCurrentTexture().createView(),
        ...(format === undefined ? {} : { format }),
        // The dirty set is handed out once per frame by contract, so only the
        // first plane's draw carries it. Passing it twice would have the ledger
        // refuse the duplicate every frame — correct, but it would report a
        // violation this code committed on purpose.
        rebuild: first ? frame.rebuilds : [],
        resolution,
        clear: true,
      });
      first = false;
    }

    // Analysis stats come back asynchronously and drive the adaptive tint; the
    // renderer resolves whatever has landed and never blocks on it.
    void renderer.collectAdaptation();
  };

  return {
    get active() {
      return active();
    },

    get renderer() {
      return renderer;
    },

    /**
     * Awaits the device handshake and whatever it started — deliberately without
     * starting a load of its own.
     *
     * A session with no adapter must download no WGSL. Forcing the import here
     * to have something to await would do exactly that, on the one machine where
     * the bytes can never be used, and X7's whole promise is about that machine.
     */
    async ready() {
      await deviceSync;
    },

    syncDevice,

    setBackdropTexture(sourceId, texture) {
      const existing = providers.get(sourceId);
      if (existing !== undefined) {
        renderer?.unregisterBackdrop(sourceId);
        providers.delete(sourceId);
      }
      if (texture === undefined) {
        textures.delete(sourceId);
        return;
      }
      textures.set(sourceId, texture);
      buildProvider(sourceId, texture);
    },

    setMaterialProfile(profile) {
      materialProfile = profile;
      renderer?.setMaterialProfile(profile);
    },

    write,
    render,

    destroy() {
      destroyed = true;
      pending = undefined;
      dropProviders();
      unconfigureCanvases();
      textures.clear();
      liveGroups.clear();
      renderer?.destroy();
      renderer = undefined;
      device = undefined;
    },
  };
}

/**
 * Declared extent of a copied source, in texture px.
 *
 * Never a layout read: a canvas' backing store and an image's intrinsic size are
 * attributes, not geometry, so nothing here goes through `measure.ts`. Video is
 * excluded by type — an external texture declares its own size.
 */
function sourceExtent(texture: Extract<GlassBackdropTexture, { kind: "canvas" | "image" }>): {
  readonly width: number;
  readonly height: number;
} {
  if (texture.kind === "canvas") {
    return { width: texture.canvas.width, height: texture.canvas.height };
  }
  const image = texture.image;
  return image instanceof ImageBitmap
    ? { width: image.width, height: image.height }
    : { width: image.naturalWidth, height: image.naturalHeight };
}
