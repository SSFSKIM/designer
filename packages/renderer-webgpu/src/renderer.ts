/**
 * The renderer: device, resources, and the frame.
 *
 * Two entry points, deliberately:
 *
 *  - **`drawFrame`** — draw one frame into two texture views. No scene, no
 *    scheduler, no DOM. This is what the golden suite and the benchmark drive, and
 *    what makes the optical maths testable without standing up the whole runtime.
 *  - **`frameParticipant`** — the same work split across core's `write` and
 *    `render` phases, so `@vitrea/core`'s scheduler drives it alongside
 *    platform-web's DOM participant. Pyramid rebuilds land in `write` because that
 *    is the phase core hands them out in; drawing lands in `render`, with the graph
 *    frozen.
 *
 * The participant reads the frame's `resolution` when core supplies one, and
 * prefers it over the group input's own `refraction`/`analysis` — core is the
 * authority on resolved state (X2), and it is the frame's resolution that has been
 * through the whole transition table. The group input's copies are the fallback for
 * `drawFrame`, where there is no core.
 *
 * ## Device generations
 *
 * Everything GPU-shaped hangs off a `GpuContext` tagged with the device generation
 * that made it. On loss the context is dropped whole and every backdrop is marked
 * for re-import, so recovery flows through the ordinary
 * one-rebuild-per-dirty-source-per-frame path instead of a special case — which
 * means the recovery path is exercised by the same tests as the steady state.
 */

import { DEFAULT_GROUP_UNION, type GroupUnionParams } from "@vitrea/geometry";

import { createAdaptationState, readbackDue, type AdaptationState } from "./analysis";
import type { BackdropProvider } from "./backdrop";
import { OUTPUT_TEXTURE_FORMAT } from "./color";
import {
  createDeviceHost,
  type DeviceCapabilityInput,
  type DeviceHost,
  type DeviceOwnership,
  type RendererDeviceStatus,
} from "./device";
import { rendererError } from "./errors";
import { createGpuContext, type GpuContext } from "./gpu-context";
import { createGovernor, type Governor } from "./governor";
import {
  groupFieldRect,
  packInstances,
  resolveSurfaces,
  snapRectToDevicePixels,
  type ResolvedSurface,
} from "./instances";
import {
  accessibilityRefractionCap,
  adaptationStrength,
  effectiveRefraction,
  LENS_BODY_LOD_PER_PX,
  LENS_RIM_LOD_BIAS,
  MATERIAL_OPTICS,
  opticsUnderPolicy,
  REFRACTION_SCALE,
  type MaterialPolicyView,
  type MaterialVariant,
} from "./material";
import { createPassRunner, type DeviceRect, type PassRunner } from "./passes";
import { createPyramidStore, type PyramidStore } from "./pyramid";
import type {
  FrameContextView,
  FrameParticipantView,
  GroupRenderInput,
  RebuildRequestView,
  SceneResolutionView,
} from "./render-model";
import type { TimingCollector } from "./timing";
import { allShaderSource } from "./wgsl";

export const OPTICS_PASS_ID = "vitrea.optics";
export const HIGHLIGHT_PASS_ID = "vitrea.highlight";
export const FIELD_PASS_ID = "vitrea.field";
export const BACKDROP_PASS_ID = "vitrea.backdrop";
export const ANALYSIS_PASS_ID = "vitrea.analysis";

export const RENDERER_PASS_IDS = [
  BACKDROP_PASS_ID,
  ANALYSIS_PASS_ID,
  FIELD_PASS_ID,
  OPTICS_PASS_ID,
  HIGHLIGHT_PASS_ID,
] as const;

/** Nominal accessibility material policy — nothing capped. Mirrors core's. */
export const NOMINAL_MATERIAL_POLICY: MaterialPolicyView = {
  glass: "material",
  frost: "nominal",
  refraction: "nominal",
  occlusion: "nominal",
  border: "nominal",
  ambientTint: "nominal",
  foreground: "adaptive",
};

/**
 * Advisory light direction, in viewport coordinates with y pointing down: a little
 * left of straight overhead, which is where Apple's material reads its specular
 * from. Calibration-delegated (C7) like every other optical constant.
 */
const LIGHT_DIRECTION: readonly [number, number] = [-0.3714, -0.9285];

/** Specular sweep band width in radians, and the press glow's reach in CSS px. */
const SWEEP_BAND_RADIANS = 0.55;
const GLOW_RADIUS_CSS = 44;
const GLOW_GAIN = 0.6;
const SWEEP_GAIN = 0.85;

export interface ViewportState {
  /** Viewport size in CSS px. */
  readonly widthCss: number;
  readonly heightCss: number;
  readonly devicePixelRatio: number;
}

export interface RendererInstrumentation {
  readonly pyramid: PyramidStore["instrumentation"];
  readonly texturePool: { readonly live: number; readonly created: number; readonly destroyed: number };
  readonly pipelines: { readonly renderPipelines: number; readonly computePipelines: number };
  readonly framesDrawn: number;
  readonly deviceGenerations: number;
}

export interface DrawFrameArgs {
  readonly frame: { readonly id: number; readonly timeMs: number };
  /** The optics canvas' current texture view. */
  readonly optics: GPUTextureView;
  /** The highlight canvas' view. Omit to skip the highlight pass entirely. */
  readonly highlight?: GPUTextureView;
  readonly format?: GPUTextureFormat;
  /**
   * The rebuild requests core handed out. Omitted means "ask every registered
   * provider whether it is dirty", which is what `drawFrame` does standalone.
   */
  readonly rebuild?: readonly RebuildRequestView[];
  /** Core's resolved state for this frame. Overrides the group inputs' copies. */
  readonly resolution?: SceneResolutionView;
  readonly timing?: TimingCollector;
  /** Clear the targets first. Default true. */
  readonly clear?: boolean;
}

export interface DrawFrameResult {
  readonly groupsDrawn: number;
  readonly rebuilds: number;
  readonly skipped: readonly { readonly groupId: string; readonly reason: string }[];
}

export interface WebGPURendererOptions {
  /** An app-owned device. Given one, the renderer never requests its own. */
  readonly device?: GPUDevice;
  readonly ownership?: DeviceOwnership;
  /** Re-request a vitrea-owned device after loss. */
  readonly reacquire?: () => Promise<GPUDevice | undefined>;
  readonly onReplacementNeeded?: () => void;
  readonly onDeviceStatusChange?: (status: RendererDeviceStatus) => void;
  /** Whether family C's f32 cross-check has passed (Decision Log #20). */
  readonly familyCVerified?: boolean;
  readonly viewport?: ViewportState;
}

export interface GlassRenderer {
  readonly backend: "webgpu";
  /** True only with a live, unlost device attached. */
  readonly ready: boolean;
  readonly passes: readonly string[];
  readonly shaderSource: string;
  readonly deviceStatus: RendererDeviceStatus;
  /** The facts a host folds into core's `PlatformProbe`. */
  readonly capabilityInput: DeviceCapabilityInput;
  readonly governor: Governor;
  readonly instrumentation: RendererInstrumentation;

  attachDevice(device: GPUDevice, ownership?: DeviceOwnership): void;
  replaceDevice(device: GPUDevice): void;
  markWebGPUUnavailable(reason: "no-adapter" | "device-request-failed"): void;

  registerBackdrop(provider: BackdropProvider): void;
  unregisterBackdrop(sourceId: string): void;
  backdrop(sourceId: string): BackdropProvider | undefined;

  setViewport(viewport: ViewportState): void;
  readonly viewport: ViewportState;

  setGroup(input: GroupRenderInput): void;
  removeGroup(groupId: string): void;
  setAccessibility(policy: MaterialPolicyView): void;

  drawFrame(args: DrawFrameArgs): DrawFrameResult;
  /** Targets for the participant path, where core drives the phases. */
  setTargets(targets: { readonly optics: GPUTextureView; readonly highlight?: GPUTextureView; readonly format?: GPUTextureFormat }): void;
  frameParticipant(): FrameParticipantView;

  /** Resolve any completed analysis readbacks into the adaptation drivers. */
  collectAdaptation(): Promise<number>;
  destroy(): void;
}

interface GroupEntry {
  readonly input: GroupRenderInput;
}

export function createWebGPURenderer(options: WebGPURendererOptions = {}): GlassRenderer {
  const providers = new Map<string, BackdropProvider>();
  const groups = new Map<string, GroupEntry>();
  const adaptation = new Map<string, AdaptationState>();
  const lastReadbackAt = new Map<string, number>();

  let accessibility: MaterialPolicyView = NOMINAL_MATERIAL_POLICY;
  let viewport: ViewportState = options.viewport ?? {
    widthCss: 0,
    heightCss: 0,
    devicePixelRatio: 1,
  };
  let context: GpuContext | undefined;
  let store: PyramidStore | undefined;
  let runner: PassRunner | undefined;
  let framesDrawn = 0;
  let generations = 0;
  let lastFrameTimeMs: number | undefined;
  let targets:
    | { optics: GPUTextureView; highlight?: GPUTextureView; format: GPUTextureFormat }
    | undefined;
  let pendingEncoder: GPUCommandEncoder | undefined;
  let pendingRebuilds = 0;

  const governor = createGovernor({
    ...(options.familyCVerified === undefined ? {} : { familyCVerified: options.familyCVerified }),
  });

  const dropContext = (): void => {
    store?.destroy();
    runner?.destroy();
    context?.destroy();
    store = undefined;
    runner = undefined;
    context = undefined;
    pendingEncoder = undefined;
  };

  const host: DeviceHost = createDeviceHost({
    ...(options.reacquire === undefined ? {} : { reacquire: options.reacquire }),
    ...(options.onReplacementNeeded === undefined
      ? {}
      : { onReplacementNeeded: options.onReplacementNeeded }),
    onStatusChange: (status) => {
      if (status.generation !== generations) generations = status.generation;
      options.onDeviceStatusChange?.(status);
    },
  });

  // Loss teardown: drop every resource, and mark every backdrop for re-import so
  // recovery uses the ordinary dirty path. Registered once — the hook survives
  // every generation, because the host outlives the contexts.
  host.addTeardownHook(() => {
    dropContext();
    adaptation.clear();
    lastReadbackAt.clear();
  });

  const ensureContext = (): { context: GpuContext; store: PyramidStore; runner: PassRunner } => {
    const device = host.requireDevice();
    const generation = host.status.generation;
    if (context === undefined || context.generation !== generation) {
      dropContext();
      context = createGpuContext(device, generation);
      store = createPyramidStore(context);
      runner = createPassRunner(context);
    }
    return {
      context,
      store: store as PyramidStore,
      runner: runner as PassRunner,
    };
  };

  const adaptationFor = (sourceId: string): AdaptationState => {
    let state = adaptation.get(sourceId);
    if (state === undefined) {
      state = createAdaptationState();
      adaptation.set(sourceId, state);
    }
    return state;
  };

  /**
   * Cover fit: the backdrop fills the viewport and the overflow is cropped
   * symmetrically. Returned as a scale/offset on viewport-normalised coordinates,
   * which is the form the optics shader applies.
   */
  const coverFit = (
    sourceWidth: number,
    sourceHeight: number,
  ): readonly [number, number, number, number] => {
    const viewportAspect =
      viewport.heightCss > 0 ? viewport.widthCss / viewport.heightCss : 1;
    const sourceAspect = sourceHeight > 0 ? sourceWidth / sourceHeight : 1;
    if (sourceAspect > viewportAspect) {
      const scaleX = viewportAspect / sourceAspect;
      return [scaleX, 1, (1 - scaleX) / 2, 0];
    }
    const scaleY = sourceAspect / viewportAspect;
    return [1, scaleY, 0, (1 - scaleY) / 2];
  };

  const unionOf = (input: GroupRenderInput): GroupUnionParams =>
    input.union ?? DEFAULT_GROUP_UNION;

  const variantOf = (input: GroupRenderInput): MaterialVariant => input.variant ?? "regular";

  const stateOf = (
    input: GroupRenderInput,
    resolution: SceneResolutionView | undefined,
  ): { refraction: GroupRenderInput["refraction"]; analysisExact: boolean } => {
    const resolved = resolution?.groups.find((group) => group.groupId === input.groupId);
    if (resolved === undefined) {
      return { refraction: input.refraction, analysisExact: input.analysisExact };
    }
    return {
      refraction: resolved.state.refraction,
      analysisExact: resolved.state.analysis === "exact",
    };
  };

  function rebuildRequests(explicit: readonly RebuildRequestView[] | undefined): readonly RebuildRequestView[] {
    if (explicit !== undefined) return explicit;
    // Standalone path: ask each provider a group actually samples.
    const sampled = new Set<string>();
    for (const entry of groups.values()) {
      const id = entry.input.backdropSourceId;
      if (id !== undefined) sampled.add(id);
    }
    const requests: RebuildRequestView[] = [];
    for (const sourceId of sampled) {
      const provider = providers.get(sourceId);
      if (provider === undefined || !provider.isDirty()) continue;
      requests.push({
        sourceId,
        // Standalone, every dirty acquire is its own epoch: there is no core
        // keeping the books, so a monotonically rising number is the honest
        // stand-in and it keeps `build`'s clean-skip from firing spuriously.
        epoch: framesDrawn + 1,
        resolution: { scale: 1, maxDimension: 2048 },
        groupIds: [...groups.values()]
          .filter((entry) => entry.input.backdropSourceId === sourceId)
          .map((entry) => entry.input.groupId),
      });
    }
    return requests;
  }

  function runRebuilds(
    encoder: GPUCommandEncoder,
    requests: readonly RebuildRequestView[],
    frameTimeMs: number,
  ): number {
    const { store: pyramids } = ensureContext();
    let built = 0;

    for (const request of requests) {
      const provider = providers.get(request.sourceId);
      if (provider === undefined) continue;

      const variant = variantOf(
        [...groups.values()].find(
          (entry) => entry.input.backdropSourceId === request.sourceId,
        )?.input ?? { groupId: "", surfaces: [], refraction: "none", analysisExact: false },
      );
      const optics = opticsUnderPolicy(MATERIAL_OPTICS[variant], accessibility);

      const outcome = pyramids.build(
        {
          sourceId: request.sourceId,
          epoch: request.epoch,
          resolution: request.resolution,
          bodySigmaCss: optics.blurSigma,
          viewportCss: [viewport.widthCss, viewport.heightCss],
        },
        provider,
        encoder,
      );
      if (outcome.status === "built") built += 1;
    }

    // Analysis readback, cadence-gated by the governor. Every source with a
    // pyramid is eligible, whether or not it rebuilt this frame — a static
    // backdrop still needs its stats read once.
    const cadence = governor.knobs.adaptationCadenceHz;
    for (const sourceId of providers.keys()) {
      if (pyramids.resources(sourceId) === undefined) continue;
      if (!readbackDue(lastReadbackAt.get(sourceId), frameTimeMs, cadence)) continue;
      if (pyramids.requestStats(sourceId, encoder)) lastReadbackAt.set(sourceId, frameTimeMs);
    }

    return built;
  }

  function drawGroups(
    encoder: GPUCommandEncoder,
    resolution: SceneResolutionView | undefined,
  ): DrawFrameResult {
    const { store: pyramids, runner: passes } = ensureContext();
    const active = targets;
    if (active === undefined) {
      throw rendererError(
        "pass-input",
        "No render targets are set. Call setTargets() (or pass views to drawFrame) before drawing.",
      );
    }

    const dpr = Math.max(viewport.devicePixelRatio, 1e-3);
    const cssPerDevice = 1 / dpr;
    const viewportDevice: readonly [number, number] = [
      Math.max(1, Math.round(viewport.widthCss * dpr)),
      Math.max(1, Math.round(viewport.heightCss * dpr)),
    ];

    const skipped: { groupId: string; reason: string }[] = [];
    let drawn = 0;

    for (const entry of groups.values()) {
      const input = entry.input;
      if (input.surfaces.length === 0) continue;

      let surfaces: readonly ResolvedSurface[];
      try {
        surfaces = resolveSurfaces(input, governor.knobs.fieldFamily);
      } catch (error) {
        skipped.push({
          groupId: input.groupId,
          reason: error instanceof Error ? error.message : String(error),
        });
        continue;
      }

      const union = unionOf(input);
      const rectCss = snapRectToDevicePixels(groupFieldRect(surfaces, union), dpr);
      const rectDevice: DeviceRect = {
        x: Math.round(rectCss.x * dpr),
        y: Math.round(rectCss.y * dpr),
        width: Math.max(1, Math.round(rectCss.width * dpr)),
        height: Math.max(1, Math.round(rectCss.height * dpr)),
      };
      if (rectDevice.width <= 0 || rectDevice.height <= 0) continue;

      const packed = packInstances(surfaces, [rectCss.x, rectCss.y]);
      const fields = passes.fieldPass(encoder, {
        groupId: input.groupId,
        family: governor.knobs.fieldFamily,
        rectDevice,
        cssPerDevice,
        coverageRampCss: cssPerDevice,
        instances: packed.data,
        instanceCount: packed.count,
        union,
      });

      const state = stateOf(input, resolution);
      const policy = resolution?.accessibility.material ?? accessibility;
      const variant = variantOf(input);
      const optics = opticsUnderPolicy(MATERIAL_OPTICS[variant], policy);

      // Decision Log #19's dual cap, resolved once, on the CPU.
      const refraction = effectiveRefraction(
        accessibilityRefractionCap(policy),
        state.refraction,
      );
      const refractionScale = REFRACTION_SCALE[refraction];

      const sourceId = input.backdropSourceId;
      const pyramid = sourceId === undefined ? undefined : pyramids.resources(sourceId);
      const adapt =
        sourceId === undefined ? undefined : adaptationFor(sourceId).values;

      passes.opticsPass(encoder, {
        groupId: input.groupId,
        target: active.optics,
        targetFormat: active.format,
        rectDevice,
        fields,
        viewportDevice,
        cssPerDevice,
        coverageRampCss: cssPerDevice,
        fit:
          pyramid === undefined
            ? [1, 1, 0, 0]
            : coverFit(pyramid.plan.width, pyramid.plan.height),
        refractionScale,
        bodyLodPerPx: LENS_BODY_LOD_PER_PX,
        rimLodBias: LENS_RIM_LOD_BIAS,
        chainMaxLod: pyramid?.plan.maxLod ?? 0,
        tint: optics.tint,
        tintAlpha: optics.tintAlpha,
        adaptTint: adapt?.tint ?? optics.tint,
        adaptStrength:
          adapt?.observed === true ? adaptationStrength(policy, state.analysisExact) : 0,
        rimWidth: optics.rimWidth,
        rimAlpha: optics.rimAlpha,
        specularPower: optics.specularPower,
        specularGain: optics.specularGain,
        lightDirection: LIGHT_DIRECTION,
        shadowDepth: optics.shadowDepth,
        shadowAlpha: optics.shadowAlpha,
        backdrop:
          pyramid === undefined || policy.glass === "none"
            ? undefined
            : {
                chain: pyramid.chain.createView(),
                body: pyramid.body.createView(),
              },
      });

      if (active.highlight !== undefined) {
        // One sweep phase and one press point per group: there is one pointer, and
        // a sweep travelling the container's unioned contour is what a
        // GlassEffectContainer is for. The per-pixel glow comes off the aux target.
        const lead = surfaces.reduce(
          (best, surface) => (surface.channels.glow > best.channels.glow ? surface : best),
          surfaces[0] as ResolvedSurface,
        );
        passes.highlightPass(encoder, {
          groupId: input.groupId,
          target: active.highlight,
          targetFormat: active.format,
          rectDevice,
          fields,
          viewportDevice,
          cssPerDevice,
          sweep: lead.channels.sweep,
          sweepBandRadians: SWEEP_BAND_RADIANS,
          // Reduced Motion removes shimmer travel outright rather than freezing it.
          sweepGain: policy.glass === "none" ? 0 : SWEEP_GAIN,
          rimWidth: optics.rimWidth,
          pressPointCss: lead.channels.pressPoint ?? lead.centre,
          glowRadiusCss: GLOW_RADIUS_CSS,
          glowGain: GLOW_GAIN,
          colour: optics.highlight,
        });
      }

      drawn += 1;
    }

    return { groupsDrawn: drawn, rebuilds: pendingRebuilds, skipped };
  }

  return {
    backend: "webgpu",

    get ready() {
      return host.status.device !== undefined && host.status.deviceHealth === "ok";
    },

    passes: RENDERER_PASS_IDS,
    shaderSource: allShaderSource(),

    get deviceStatus() {
      return host.status;
    },

    get capabilityInput() {
      return host.capabilityInput;
    },

    governor,

    get instrumentation() {
      const pool = context?.pool.stats;
      const cache = context?.cache.stats;
      return {
        pyramid:
          store?.instrumentation ?? {
            rebuilds: 0,
            refusedDuplicates: 0,
            skippedClean: 0,
            reallocations: 0,
            rebuildsInFrame: () => 0,
            peakRebuildsPerSourcePerFrame: 0,
          },
        texturePool: {
          live: pool?.live ?? 0,
          created: pool?.created ?? 0,
          destroyed: pool?.destroyed ?? 0,
        },
        pipelines: {
          renderPipelines: cache?.renderPipelines ?? 0,
          computePipelines: cache?.computePipelines ?? 0,
        },
        framesDrawn,
        deviceGenerations: generations,
      };
    },

    attachDevice(device, ownership) {
      host.attach(device, ownership ?? options.ownership ?? (options.device === device ? "app" : "vitrea"));
    },

    replaceDevice(device) {
      host.replaceDevice(device);
    },

    markWebGPUUnavailable(reason) {
      host.markUnavailable(reason);
    },

    registerBackdrop(provider) {
      if (providers.has(provider.id)) {
        throw rendererError(
          "source-identity",
          `Backdrop source "${provider.id}" is already registered. Unregister it first, or register the replacement under a new id.`,
          provider.id,
        );
      }
      providers.set(provider.id, provider);
    },

    unregisterBackdrop(sourceId) {
      const provider = providers.get(sourceId);
      if (provider === undefined) return;
      provider.destroy();
      providers.delete(sourceId);
      store?.forget(sourceId);
      adaptation.delete(sourceId);
      lastReadbackAt.delete(sourceId);
    },

    backdrop(sourceId) {
      return providers.get(sourceId);
    },

    setViewport(next) {
      const changed =
        next.widthCss !== viewport.widthCss ||
        next.heightCss !== viewport.heightCss ||
        next.devicePixelRatio !== viewport.devicePixelRatio;
      viewport = next;
      if (!changed) return;
      // A resize bumps the size epoch, which is what invalidates every dependent
      // allocation (§GPU device ownership) — group field textures included, since
      // their device extent is a function of the DPR.
      context?.pool.bumpSizeEpoch();
      context?.pool.sweep();
    },

    get viewport() {
      return viewport;
    },

    setGroup(input) {
      groups.set(input.groupId, { input });
    },

    removeGroup(groupId) {
      groups.delete(groupId);
      runner?.forget(groupId);
    },

    setAccessibility(policy) {
      accessibility = policy;
    },

    setTargets(next) {
      targets = {
        optics: next.optics,
        ...(next.highlight === undefined ? {} : { highlight: next.highlight }),
        format: next.format ?? OUTPUT_TEXTURE_FORMAT,
      };
    },

    drawFrame(args) {
      const { context: gpu, store: pyramids, runner: passes } = ensureContext();
      targets = {
        optics: args.optics,
        ...(args.highlight === undefined ? {} : { highlight: args.highlight }),
        format: args.format ?? OUTPUT_TEXTURE_FORMAT,
      };

      pyramids.beginFrame(args.frame.id);
      pyramids.setTimeline(args.timing);
      passes.setTimeline(args.timing);

      const encoder = gpu.device.createCommandEncoder({
        label: `vitrea:frame:${args.frame.id}`,
      });

      pendingRebuilds = runRebuilds(encoder, rebuildRequests(args.rebuild), args.frame.timeMs);

      if (args.clear !== false) {
        passes.clearPass(encoder, args.optics);
        if (args.highlight !== undefined) passes.clearPass(encoder, args.highlight);
      }

      const result = drawGroups(encoder, args.resolution);

      args.timing?.resolve(encoder);
      gpu.device.queue.submit([encoder.finish()]);
      pyramids.afterSubmit();

      // Advance the adaptation filters by the real frame delta. The drivers are
      // frame-rate invariant by construction (§Motion), so a dropped frame and two
      // short ones produce the same value.
      const delta = lastFrameTimeMs === undefined ? 0 : args.frame.timeMs - lastFrameTimeMs;
      lastFrameTimeMs = args.frame.timeMs;
      if (delta > 0) {
        for (const state of adaptation.values()) state.advance(delta);
      }

      framesDrawn += 1;
      pyramids.setTimeline(undefined);
      passes.setTimeline(undefined);
      return result;
    },

    frameParticipant() {
      return {
        id: "vitrea.renderer-webgpu",

        write: (frameContext: FrameContextView) => {
          if (host.status.device === undefined || host.status.deviceHealth !== "ok") return;
          const { context: gpu, store: pyramids, runner: passes } = ensureContext();

          pyramids.beginFrame(frameContext.frame.id);
          pyramids.setTimeline(undefined);
          passes.setTimeline(undefined);

          pendingEncoder = gpu.device.createCommandEncoder({
            label: `vitrea:frame:${frameContext.frame.id}`,
          });
          // Core hands out the frame's rebuilds here and only here: one pass over
          // the dirty set per frame id, which is the §Core model invariant's other
          // half. This renderer's own ledger is what proves it kept its side.
          pendingRebuilds = runRebuilds(
            pendingEncoder,
            frameContext.consumeDirtyBackdropSources(),
            frameContext.frame.timeMs,
          );
        },

        render: (frameContext: FrameContextView) => {
          const encoder = pendingEncoder;
          pendingEncoder = undefined;
          if (encoder === undefined || context === undefined) return;
          const passes = runner as PassRunner;
          const pyramids = store as PyramidStore;

          if (targets !== undefined) {
            passes.clearPass(encoder, targets.optics);
            if (targets.highlight !== undefined) passes.clearPass(encoder, targets.highlight);
            drawGroups(encoder, frameContext.resolution);
          }

          context.device.queue.submit([encoder.finish()]);
          pyramids.afterSubmit();

          const delta =
            lastFrameTimeMs === undefined ? 0 : frameContext.frame.timeMs - lastFrameTimeMs;
          lastFrameTimeMs = frameContext.frame.timeMs;
          if (delta > 0) {
            for (const state of adaptation.values()) state.advance(delta);
          }
          framesDrawn += 1;
        },
      };
    },

    async collectAdaptation() {
      if (store === undefined) return 0;
      const stats = await store.collectStats();
      for (const [sourceId, value] of stats) {
        const state = adaptationFor(sourceId);
        // The first observation jumps rather than filters: a 500 ms low-pass
        // starting from zero would fade the material in from black over half a
        // second on every page load.
        if (state.values.observed) state.observe(value);
        else state.reset(value);
      }
      return stats.size;
    },

    destroy() {
      for (const provider of providers.values()) provider.destroy();
      providers.clear();
      groups.clear();
      adaptation.clear();
      lastReadbackAt.clear();
      dropContext();
      host.destroy();
    },
  };
}
