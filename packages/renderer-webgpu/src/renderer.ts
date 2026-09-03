/**
 * The renderer: device, resources, and the frame.
 *
 * Two entry points, deliberately:
 *
 *  - **`drawFrame`** — draw one frame into two texture views. No scene, no
 *    scheduler, no DOM. This is what the golden suite and the benchmark drive, and
 *    what makes the optical maths testable without standing up the whole runtime.
 *  - **`frameParticipant`** — the same work split across core's `write` and
 *    `render` phases, so `vitrea`'s scheduler drives it alongside
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
 * that made it. On loss the context is dropped whole, and the first frame on the
 * replacement re-points every registered provider at the new device and marks it
 * for re-import — so recovery flows through the ordinary
 * one-rebuild-per-dirty-source-per-frame path instead of a special case, which
 * means the recovery path is exercised by the same tests as the steady state.
 *
 * `ensureContext` is where that happens rather than the loss teardown, and the
 * reason is timing: the teardown runs while there is no device to adopt, and this
 * is the one place that knows both that a generation was superseded and what
 * replaced it. It also runs before anything acquires on the new device, which the
 * teardown cannot promise.
 *
 * The one provider that cannot be re-pointed is a backdrop over the *app's* own
 * texture: WebGPU has no cross-device sharing and the renderer does not own the
 * texture, so that provider refuses instead, and the refused rebuild is reported
 * through `unbuiltSources` for the host to act on.
 */

import { DEFAULT_GROUP_UNION, type GroupUnionParams } from "@vitrea/geometry";

import { createAdaptationState, readbackDue, type AdaptationState } from "./analysis";
import type { BackdropProvider } from "./backdrop";
import {
  coverFit,
  isUsablePlacement,
  placementFit,
  samePlacement,
  texelsPerCssPx,
  type BackdropFit,
  type BackdropPlacement,
} from "./backdrop-fit";
import { OUTPUT_TEXTURE_FORMAT, relativeLuminance } from "./color";
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
  clipFieldRectToCanvas,
  groupFieldRect,
  packInstances,
  resolveSurfaces,
  snapRectToDevicePixels,
  type ResolvedSurface,
} from "./instances";
import {
  accessibilityRefractionCap,
  adaptationStrength,
  backdropToneSizeBiasUnderPolicy,
  backdropToneUnderPolicy,
  DEFAULT_MATERIAL_PROFILE,
  effectiveRefraction,
  NOMINAL_MATERIAL_POLICY,
  opticsUnderPolicy,
  outerShadowAlpha,
  outerShadowReachPx,
  outerShadowUnderPolicy,
  sizeOuterShadowOcclusionAt,
  tintToneAdaptation,
  withMaterialOverrides,
  type MaterialPolicyView,
  type MaterialProfile,
  type MaterialProfilePatch,
  type MaterialVariant,
} from "./material";
import { createPassRunner, type DeviceRect, type PassRunner } from "./passes";
import { createPyramidStore, type PyramidResources, type PyramidStore } from "./pyramid";
import { chainLodForSigma, type ResolutionPolicyView } from "./pyramid-plan";
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

/*
 * `NOMINAL_MATERIAL_POLICY` now lives in `material.ts` and is re-exported here so
 * every existing importer is unaffected. It moved because `instances.ts` needs it
 * as a default — the size law folds under the policy, so surface resolution takes
 * one — and instances sits below this module in the graph, so importing it from
 * here would have closed a cycle. It was always a material constant that happened
 * to be declared beside the renderer that first used it.
 */
export { NOMINAL_MATERIAL_POLICY } from "./material";

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
  /**
   * Source ids core handed out a rebuild for that this frame did **not** build.
   * The same list as `GlassRenderer.unbuiltSources` — see it for what a caller
   * owes.
   */
  readonly unbuilt: readonly string[];
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
  /**
   * Optical tunables to override, on top of `DEFAULT_MATERIAL_PROFILE`. This is
   * where a calibrated set lands (C7): a patch, not a whole profile, so a host
   * naming one tint alpha inherits every number it did not measure.
   */
  readonly materialProfile?: MaterialProfilePatch;
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
  /**
   * The source ids the most recent frame was handed a rebuild for and did not
   * build — because no provider is registered under the id, or because the
   * provider could not serve a frame.
   *
   * This exists because core commits `builtEpoch` when it *hands out* the
   * request, not when the renderer finishes: a request dropped here is a claim
   * spent on nothing, and the source would sit clean at an epoch whose pixels
   * were never imported. Core has no view of this side of the wire, so the
   * renderer names the losses and the platform layer re-dirties them — one frame
   * of latency, and no new core surface.
   *
   * Accumulated across the frame's planes, not per `drawFrame` call: a host draws
   * one plane per call with the same frame id and hands the dirty set to the
   * first of them only, so a later plane's empty answer must not erase what the
   * first one found. Read after the frame's last plane, or after the
   * participant's `render` phase. Empty on every ordinary frame.
   */
  readonly unbuiltSources: readonly string[];

  attachDevice(device: GPUDevice, ownership?: DeviceOwnership): void;
  replaceDevice(device: GPUDevice): void;
  markWebGPUUnavailable(reason: "no-adapter" | "device-request-failed"): void;

  registerBackdrop(provider: BackdropProvider): void;
  unregisterBackdrop(sourceId: string): void;
  backdrop(sourceId: string): BackdropProvider | undefined;
  /**
   * Where a source's pixels sit on the plane, in CSS px relative to the viewport
   * (`backdrop-fit.ts`). Set every read phase by a host that measured the source
   * element's box; `undefined` (or never set) is the cover fit, the rule every
   * golden and calibration capture was taken under. Accepted before the provider
   * is registered and kept across device generations; cleared by
   * `unregisterBackdrop`.
   */
  setBackdropPlacement(sourceId: string, placement: BackdropPlacement | undefined): void;
  backdropPlacement(sourceId: string): BackdropPlacement | undefined;

  setViewport(viewport: ViewportState): void;
  readonly viewport: ViewportState;

  setGroup(input: GroupRenderInput): void;
  removeGroup(groupId: string): void;
  setAccessibility(policy: MaterialPolicyView): void;
  /**
   * Replace the optical tunables. The patch is applied to
   * `DEFAULT_MATERIAL_PROFILE`, never to the profile currently in force, so two
   * calls do not compound — a profile is a set of measurements, and half of one
   * measurement set over half of another describes no material.
   */
  setMaterialProfile(patch: MaterialProfilePatch): void;
  /** The tunables in force. Read-only; `setMaterialProfile` is the way in. */
  readonly materialProfile: MaterialProfile;

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

/** The resolution policy a renderer driven without a host applies to every source. */
const STANDALONE_RESOLUTION: ResolutionPolicyView = { scale: 1, maxDimension: 2048 };

export function createWebGPURenderer(options: WebGPURendererOptions = {}): GlassRenderer {
  const providers = new Map<string, BackdropProvider>();
  /** Where each source sits on the plane, where the host has said (`backdrop-fit.ts`). */
  const placements = new Map<string, BackdropPlacement>();
  /** The resolution policy each source was last built under, for a rebuild this side names. */
  const lastResolution = new Map<string, ResolutionPolicyView>();
  const groups = new Map<string, GroupEntry>();
  const adaptation = new Map<string, AdaptationState>();
  const lastReadbackAt = new Map<string, number>();

  let accessibility: MaterialPolicyView = NOMINAL_MATERIAL_POLICY;
  let material: MaterialProfile = withMaterialOverrides(
    DEFAULT_MATERIAL_PROFILE,
    options.materialProfile ?? {},
  );
  let viewport: ViewportState = options.viewport ?? {
    widthCss: 0,
    heightCss: 0,
    devicePixelRatio: 1,
  };
  let context: GpuContext | undefined;
  /**
   * The last device generation a context was built for. Kept apart from
   * `context` because it has to survive `dropContext()` — the loss teardown runs
   * long before the replacement arrives, and "which generation did the providers
   * build against" is the question the replacement has to answer.
   */
  let builtGeneration: number | undefined;
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
  let pendingUnbuilt: string[] = [];
  let unbuiltFrameId: number | undefined;

  /**
   * Accumulate the frame's unbuilt sources, across planes.
   *
   * A host draws one plane per `drawFrame` with the same frame id and hands the
   * dirty set to the first of them only, so the later planes' empty lists must
   * not erase what the first one found. Same rule as the rebuild ledger's, for
   * the same reason: a repeated frame id is one frame.
   */
  const recordUnbuilt = (frameId: number, ids: readonly string[]): void => {
    if (unbuiltFrameId !== frameId) {
      unbuiltFrameId = frameId;
      pendingUnbuilt = [];
    }
    for (const id of ids) if (!pendingUnbuilt.includes(id)) pendingUnbuilt.push(id);
  };

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
      const superseded = builtGeneration;
      dropContext();
      context = createGpuContext(device, generation);
      builtGeneration = generation;
      store = createPyramidStore(context);
      runner = createPassRunner(context);
      // The providers outlive the context, and every one of them closes over the
      // device it was built with. Re-pointing them here — rather than in the loss
      // teardown — is what makes the timing right: this is the one place that
      // knows both that a device generation was superseded and what replaced it,
      // and it runs before any provider is acquired on the new device.
      //
      // Only a real transition invalidates. A provider registered before any
      // device existed has built nothing to throw away, and one already tagged
      // with this generation was built for this device.
      if (superseded !== undefined && superseded !== generation) {
        for (const provider of providers.values()) {
          if (provider.generation !== generation) provider.invalidate(generation, device);
        }
      }
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
      state = createAdaptationState(undefined, material);
      adaptation.set(sourceId, state);
    }
    return state;
  };

  /**
   * The uv transform the optics pass samples a source through: the placed fit
   * where the host measured where the source sits on the plane, the cover fit
   * where it did not (`backdrop-fit.ts`). Cover is computed from the PLAN's
   * extent, as it always was — the plan may have downscaled the source, and the
   * rounding of that downscale is part of every golden's bytes.
   */
  const fitFor = (sourceId: string, pyramid: PyramidResources): BackdropFit => {
    const placement = placements.get(sourceId);
    return isUsablePlacement(placement)
      ? placementFit(placement, viewport.widthCss, viewport.heightCss)
      : coverFit(pyramid.plan.width, pyramid.plan.height, viewport.widthCss, viewport.heightCss);
  };

  /**
   * A source whose placement changed SIZE since its pyramid was built carries a
   * body σ in texels that no longer matches the material's CSS-px σ, and a
   * static image never re-dirties to fix it. Named here as its own rebuild
   * request, at the epoch the chain already holds so the store's clean check
   * falls through to the density comparison rather than to the epoch.
   */
  const densityRebuilds = (
    explicit: readonly RebuildRequestView[],
    pyramids: PyramidStore,
  ): readonly RebuildRequestView[] => {
    const requests: RebuildRequestView[] = [];
    const named = new Set(explicit.map((request) => request.sourceId));
    // Every registered source, not only the placed ones: a placement WITHDRAWN
    // moves the density back to the cover ratio, and that is a change too.
    for (const sourceId of providers.keys()) {
      if (named.has(sourceId)) continue;
      const existing = pyramids.resources(sourceId);
      if (existing === undefined) continue;
      const next = texelsPerCssPx(
        existing.sourceWidth,
        existing.sourceHeight,
        placements.get(sourceId),
        viewport.widthCss,
        viewport.heightCss,
      );
      if (Math.abs(next - existing.texelsPerCss) <= 1e-6 * Math.max(1, existing.texelsPerCss)) continue;
      requests.push({
        sourceId,
        epoch: existing.builtEpoch,
        resolution: lastResolution.get(sourceId) ?? STANDALONE_RESOLUTION,
        groupIds: [...groups.values()]
          .filter((entry) => entry.input.backdropSourceId === sourceId)
          .map((entry) => entry.input.groupId),
      });
    }
    return requests;
  };

  const unionOf = (input: GroupRenderInput): GroupUnionParams =>
    input.union ?? DEFAULT_GROUP_UNION;

  const variantOf = (input: GroupRenderInput): MaterialVariant => input.variant ?? "regular";

  /**
   * The one tint seed this group's optics pass draws with.
   *
   * A group is one pass and one uniform, so the seed is per group while the
   * strength is per pixel — enough for the composition Apple's guidance actually
   * describes (one emphasised control among plain ones) and not enough for two
   * hues in one container, which core reports as `tint-mixing`. The first tinted
   * drawn member wins, deterministically, rather than an average nobody chose.
   */
  const groupTintSeed = (input: GroupRenderInput): readonly [number, number, number] | undefined =>
    input.surfaces.find(
      (surface) => surface.fieldReferenceOnly !== true && (surface.tint?.strength ?? 0) > 0,
    )?.tint?.color;

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
    const base = explicit ?? standaloneRequests();
    const { store: pyramids } = ensureContext();
    const density = densityRebuilds(base, pyramids);
    return density.length === 0 ? base : [...base, ...density];
  }

  function standaloneRequests(): readonly RebuildRequestView[] {
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
        resolution: STANDALONE_RESOLUTION,
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
  ): { built: number; unbuilt: readonly string[] } {
    const { store: pyramids } = ensureContext();
    let built = 0;
    const unbuilt: string[] = [];

    for (const request of requests) {
      const provider = providers.get(request.sourceId);
      if (provider === undefined) {
        // Core spent the claim on a source this renderer has never heard of — a
        // group registered ahead of its backdrop, or a source unregistered
        // between the hand-out and here.
        unbuilt.push(request.sourceId);
        continue;
      }

      const variant = variantOf(
        [...groups.values()].find(
          (entry) => entry.input.backdropSourceId === request.sourceId,
        )?.input ?? { groupId: "", surfaces: [], refraction: "none", analysisExact: false },
      );
      const optics = opticsUnderPolicy(material.optics[variant], accessibility, material);
      lastResolution.set(request.sourceId, request.resolution);

      const placement = placements.get(request.sourceId);
      const outcome = pyramids.build(
        {
          sourceId: request.sourceId,
          epoch: request.epoch,
          resolution: request.resolution,
          bodySigmaCss: optics.blurSigma,
          viewportCss: [viewport.widthCss, viewport.heightCss],
          ...(isUsablePlacement(placement) ? { placement } : {}),
        },
        provider,
        encoder,
      );
      if (outcome.status === "built") built += 1;
      // "clean" and "duplicate" are both honest answers — the source already has
      // the pixels this epoch asked for. "unavailable" is not: the claim is spent
      // and nothing was imported.
      else if (outcome.status === "unavailable") unbuilt.push(request.sourceId);
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

    return { built, unbuilt };
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

      // The frame's resolved material policy, read before the surfaces rather
      // than after: the size law folds under it (W2), so surface resolution needs
      // it to decide how thick each member reads.
      const policy = resolution?.accessibility.material ?? accessibility;

      let surfaces: readonly ResolvedSurface[];
      try {
        surfaces = resolveSurfaces(input, governor.knobs.fieldFamily, material, policy);
      } catch (error) {
        skipped.push({
          groupId: input.groupId,
          reason: error instanceof Error ? error.message : String(error),
        });
        continue;
      }

      const union = unionOf(input);
      /*
       * Clipped to the plane canvas, and clipped once, so that three things go on
       * describing the same rectangle.
       *
       * `groupFieldRect` grows the surface union by the rim and bulge margin, so a
       * surface within a few CSS px of the viewport's top or left edge produces a
       * rect with a negative origin. `opticsPass` and `highlightPass` scissor to
       * this rect on the plane canvas and `setScissorRect` takes unsigned values,
       * so an unclipped rect is a hard `RangeError` out of the WebGPU binding
       * rather than a clipped draw. A toolbar pinned to the left edge is enough to
       * hit it.
       *
       * The clip has to reach the instance frame too. The field texture is
       * allocated at this rect's size and `fs_optics` reads it by `uv` over the
       * *viewport*, so moving the viewport without moving the texture and the
       * instance origin with it would stretch the glass instead of clipping it.
       * That is why the origin handed to `packInstances` is derived from the
       * clipped device rect rather than from the CSS rect it came from. What is
       * lost is the part of the field that lies outside the canvas, which is the
       * part nothing can see.
       *
       * A group entirely on screen is unaffected: `snapRectToDevicePixels` has
       * already put both edges on device-pixel boundaries, so the arithmetic below
       * reproduces the previous origin and extent exactly.
       */
      /*
       * The outer shadow (W8) is resolved before the rect, because it is what
       * sizes the rect: the optics pass scissors to this rectangle, so the pad has
       * to reach as far as the shadow draws or the facet is sliced off at the
       * contour. Both folds land here on the CPU — the accessibility regime and
       * the linear-to-compositing-space conversion — so the shader carries the
       * curve and not the regime, as every other axis does.
       */
      const shadow = outerShadowUnderPolicy(policy, material);
      /*
       * The pad covers the DEEPEST shadow any member of this group can emit,
       * which is not the group's base amplitude. The size law amplifies the
       * amplitude per surface and the shader reads the CASTING surface's own
       * thickness, so a rect padded from the base while a thick platter emitted
       * more would slice that surface's shadow off at the scissor — and the CSS
       * tier, having no scissor, would go on drawing it, which is a cross-tier
       * divergence rather than a cost. The gain ships at the identity, so this is
       * inert today and correct for whatever the cascade fits.
       *
       * A maximum over the members rather than the thickest member's value,
       * because a profile is entitled to a negative gain and then the THINNEST
       * surface is the one that reaches furthest.
       */
      let reachOcclusion = shadow.occlusion;
      for (const surface of surfaces) {
        reachOcclusion = Math.max(
          reachOcclusion,
          sizeOuterShadowOcclusionAt(shadow.occlusion, surface.sizeThickness, material),
        );
      }
      const shadowReachPx = outerShadowReachPx({ ...shadow, occlusion: reachOcclusion });

      const snapped = snapRectToDevicePixels(
        groupFieldRect(surfaces, union, undefined, shadowReachPx),
        dpr,
      );
      const rectDevice: DeviceRect | undefined = clipFieldRectToCanvas(snapped, dpr, viewportDevice);
      if (rectDevice === undefined) continue;

      /*
       * The surface's OWN rect — the rect every pass used before W8, and the one
       * the highlight pass still uses.
       *
       * The shadow made the field rect several times larger on a small control,
       * and the highlight draws nothing out there: `fs_highlight` returns on
       * `coverage <= 0`, so those fragments were rasterised, read twice and
       * thrown away. On the benchmark's mobile scene that was 1.0 ms of a 3.1 ms
       * frame, interleaved against the same scene with the shadow declined. The
       * optics pass cannot be scoped this way — it is what draws the shadow.
       */
      const surfaceRectDevice: DeviceRect =
        shadowReachPx === 0
          ? rectDevice
          : (clipFieldRectToCanvas(
              snapRectToDevicePixels(groupFieldRect(surfaces, union), dpr),
              dpr,
              viewportDevice,
            ) ?? rectDevice);

      const packed = packInstances(surfaces, [
        rectDevice.x * cssPerDevice,
        rectDevice.y * cssPerDevice,
      ]);
      const fields = passes.fieldPass(encoder, {
        groupId: input.groupId,
        family: governor.knobs.fieldFamily,
        rectDevice,
        cssPerDevice,
        coverageRampCss: cssPerDevice,
        // Ladder rungs 2 and 3 turn this down; rung 0 and 1 leave it at 1, which
        // is the extent the group's rect already had.
        renderScale: governor.knobs.refractionResolutionScale,
        instances: packed.data,
        instanceCount: packed.count,
        union,
      });

      const state = stateOf(input, resolution);
      const variant = variantOf(input);
      const sourceId = input.backdropSourceId;
      const pyramid = sourceId === undefined ? undefined : pyramids.resources(sourceId);
      const adapt =
        sourceId === undefined ? undefined : adaptationFor(sourceId).values;
      /*
       * A group with no pyramid to sample writes its material as a layer the
       * browser composites (W11a; see `GroupRenderInput.unsampledMaterial`), so
       * where the host resolved the compositing-space pair it replaces the
       * profile's — before the policy fold, which then lands on it exactly as
       * the CSS tier's fold lands on the same numbers.
       */
      const nominalOptics = material.optics[variant];
      const optics = opticsUnderPolicy(
        pyramid === undefined && input.unsampledMaterial !== undefined
          ? {
              ...nominalOptics,
              tint: input.unsampledMaterial.tint,
              tintAlpha: input.unsampledMaterial.tintAlpha,
            }
          : nominalOptics,
        policy,
        material,
      );

      /*
       * Backdrop tone adaptation (W7). Both policy folds resolve here, on the
       * CPU, so the shaders carry the curve and not the regime — and the optics
       * and highlight passes are handed the same four numbers, because a
       * highlight that outlived the surface it belongs to is exactly what two
       * copies of one curve produce.
       *
       * The strength is zero unless the host measured a backdrop tone for this
       * group. That is not a defensive default: this axis moves the material onto
       * a colour, and the only colour it may move onto is one somebody measured.
       */
      const backdropTone: readonly [number, number, number, number] = [
        material.backdropToneLow,
        material.backdropToneHigh,
        backdropToneSizeBiasUnderPolicy(policy, material),
        input.backdropTone === undefined
          ? 0
          : backdropToneUnderPolicy(policy, material) * material.backdropToneMax,
      ];
      // The tone LEVEL is the encoded-space reading (W9); the tone COLOUR stays
      // the physical linear mean the collapse converges onto. Hosts that predate
      // the split fall back to the colour's own luminance.
      const backdropToneLevel =
        input.backdropTone === undefined
          ? 0
          : (input.backdropToneLevel ?? relativeLuminance(input.backdropTone));
      // Decision Log #19's dual cap, resolved once, on the CPU.
      const refraction = effectiveRefraction(
        accessibilityRefractionCap(policy),
        state.refraction,
      );
      const refractionScale = material.refractionScale[refraction];

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
          pyramid === undefined || sourceId === undefined
            ? [1, 1, 0, 0]
            : fitFor(sourceId, pyramid),
        refractionScale,
        lensRefractionGain: material.lensRefractionGain,
        // The lens law (W12 G2) and the inner shadow's own depth gain, both
        // evaluated per pixel in the shader from the thickness and the span.
        lensHeightPerSpan: material.lensHeightPerSpan,
        lensHeightMax: material.lensHeightMax,
        lensAmountPerSpan: material.lensAmountPerSpan,
        lensAmountMax: material.lensAmountMax,
        lensThicknessReference: material.lensThicknessReference,
        lensExtentGain: material.lensExtentGain,
        lensProfileExponent: material.lensProfileExponent,
        lensOvalization: material.lensOvalization,
        lensOvalizationSpanMin: material.lensOvalizationSpanMin,
        lensOvalizationSpanMax: material.lensOvalizationSpanMax,
        shadowDepthSizeGainMax: material.lensSizeGainMax,
        chainMaxLod: pyramid?.plan.maxLod ?? 0,
        tint: optics.tint,
        tintAlpha: optics.tintAlpha,
        adaptTint: adapt?.tint ?? optics.tint,
        adaptStrength:
          adapt?.observed === true
            ? adaptationStrength(policy, state.analysisExact, material)
            : 0,
        /*
         * `glass: "none"` is forced colours, and it takes the author's tint with
         * the rest of the material.
         *
         * The pass keeps running — it is what paints the surface at all on this
         * tier — but with no backdrop and an opaque occlusion, so whatever colour
         * sits here IS the surface. An author tint arriving into that lands as a
         * flat fill of the author's colour where the platform's palette is
         * required, which is the one composition forced colours exists to
         * prevent. Falling back to the material's own tint reproduces exactly
         * what an untinted surface draws.
         */
        tintSeed: (policy.glass === "none" ? undefined : groupTintSeed(input)) ?? optics.tint,
        tintToneAdaptation: tintToneAdaptation(policy, material),
        tintShade: [material.tintShadeDark, material.tintShadeLight, material.tintShadeStrength],
        rimWidth: optics.rimWidth,
        rimAlpha: optics.rimAlpha,
        specularPower: optics.specularPower,
        specularGain: optics.specularGain,
        lightDirection: material.lightDirection,
        shadowDepth: optics.shadowDepth,
        shadowAlpha: optics.shadowAlpha,
        // The size law's gains, per group (W2); the per-pixel factor they
        // multiply rides the field pass's aux channel, so one uniform serves a
        // group whose members are not one size. `bodyChainLod` is where the body
        // blur already sits on the chain — only the pyramid that built it knows
        // the CSS-px-to-texel conversion, so it publishes the σ and this converts.
        sizeScatterGainMax: material.sizeScatterGainMax,
        sizeOcclusionGain: material.sizeOcclusionGain,
        sizeShadowGainMax: material.sizeShadowGainMax,
        bodyChainLod: chainLodForSigma(pyramid?.bodySigmaTexels ?? 0),
        // The size law's curves (W11c): the shader evaluates the thickness and
        // the scatter mix per pixel from the span the field carries, under the
        // same fold `sizeThicknessUnderPolicy` applies on the CPU.
        sizeSpanMin: material.sizeSpanMin,
        sizeSpanMax: material.sizeSpanMax,
        sizeScatterFloor: material.sizeScatterFloor,
        sizeScatterSpanMax: material.sizeScatterSpanMax,
        sizeFold: material.refractionScale[accessibilityRefractionCap(policy)],
        backdropTone,
        backdropToneColour: [
          input.backdropTone?.[0] ?? 0,
          input.backdropTone?.[1] ?? 0,
          input.backdropTone?.[2] ?? 0,
          backdropToneLevel,
        ],
        // The response law's anchors (W9) and the linear backdrop mean its
        // solve composites against. The shader re-derives the encoded input
        // from `backdropToneLevel`, so the fourth slot carries the linear
        // mean — the one quantity the solve needs that the tone colour does
        // not already hold.
        backdropToneAnchorX: material.backdropToneAnchorX,
        backdropToneResponseThin: material.backdropToneResponseThin,
        backdropToneResponseThick: material.backdropToneResponseThick,
        // The response law rides only the UN-DEGRADED regime, for the same
        // provenance reason the dark profiles set its strength to 0: the
        // anchors are standard-light-reference measurements, and the
        // accessibility references behave differently (nearly opaque, flat in
        // span — W2). Measured before this gate existed: reduced-transparency
        // photo ΔE p95 0.007 → 0.048 and cross-tier ratio 0.99 → 0.86. Where
        // any policy fold touches the tone axis, the solve stands down and the
        // collapse alone runs, exactly the pre-W9 behaviour those profiles
        // were fitted on.
        backdropToneResponseStrength:
          backdropToneUnderPolicy(policy, material) >= 0.999
            ? material.backdropToneResponseStrength
            : 0,
        backdropToneLinearMean:
          input.backdropToneLinearLuminance ?? backdropToneLevel,
        outerShadow: [
          outerShadowAlpha(shadow.occlusion),
          shadow.sigmaPx,
          shadow.spreadPx,
          // The offset in field-texture UV. The field spans exactly this rect, so
          // one CSS px is one over the rect's CSS height however the governor
          // scaled the rasterisation.
          shadow.offsetPx / Math.max(rectDevice.height * cssPerDevice, 1e-6),
        ],
        outerShadowSizeGain: shadow.sizeGain,
        outerShadowRectCssHeight: rectDevice.height * cssPerDevice,
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
          // The surface's own rect, not the shadow's — see `surfaceRectDevice`.
          rectDevice: surfaceRectDevice,
          fieldRectDevice: rectDevice,
          fields,
          viewportDevice,
          cssPerDevice,
          sweep: lead.channels.sweep,
          sweepBandRadians: material.sweepBandRadians,
          // Reduced Motion removes shimmer travel outright rather than freezing it.
          sweepGain: policy.glass === "none" ? 0 : material.sweepGain,
          rimWidth: optics.rimWidth,
          pressPointCss: lead.channels.pressPoint ?? lead.centre,
          glowRadiusCss: material.glowRadiusCss,
          glowGain: material.glowGain,
          colour: optics.highlight,
          // The same four numbers the optics pass took, so the two passes fade
          // the surface on one curve rather than on two copies of it — and the
          // same band and fold, since the curve is evaluated off the span.
          backdropTone,
          backdropToneLevel,
          sizeSpanMin: material.sizeSpanMin,
          sizeSpanMax: material.sizeSpanMax,
          sizeFold: material.refractionScale[accessibilityRefractionCap(policy)],
        });
      }

      drawn += 1;
    }

    return { groupsDrawn: drawn, rebuilds: pendingRebuilds, skipped, unbuilt: [...pendingUnbuilt] };
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

    get unbuiltSources() {
      return pendingUnbuilt;
    },

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
      placements.delete(sourceId);
      lastResolution.delete(sourceId);
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

    setBackdropPlacement(sourceId, placement) {
      if (samePlacement(placements.get(sourceId), placement)) return;
      if (placement === undefined) placements.delete(sourceId);
      else placements.set(sourceId, { ...placement });
    },

    backdropPlacement(sourceId) {
      return placements.get(sourceId);
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
      //
      // The bump alone, deliberately: `pool.acquire` destroys and reallocates a
      // stale-epoch entry on next use, so every allocation is replaced exactly
      // when it is next needed. Sweeping here instead destroyed the backdrop
      // chain and body textures *immediately*, and a static source rebuilds
      // nothing — so the very next frame bound two destroyed textures and lost
      // the whole plane's encoder to a validation error. Deferring costs one
      // frame's worth of superseded textures and nothing else.
      context?.pool.bumpSizeEpoch();
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

    setMaterialProfile(patch) {
      material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
      // The adaptation filters carry the old profile's tint ends, so they are
      // dropped rather than left to interpolate between two materials. Everything
      // else on the draw path reads the profile per frame, so the next frame
      // redraws with the new numbers on its own.
      adaptation.clear();
    },

    get materialProfile() {
      return material;
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

      let result: DrawFrameResult;
      try {
        const rebuilt = runRebuilds(encoder, rebuildRequests(args.rebuild), args.frame.timeMs);
        pendingRebuilds = rebuilt.built;
        recordUnbuilt(args.frame.id, rebuilt.unbuilt);

        if (args.clear !== false) {
          passes.clearPass(encoder, args.optics);
          if (args.highlight !== undefined) passes.clearPass(encoder, args.highlight);
        }

        result = drawGroups(encoder, args.resolution);

        args.timing?.resolve(encoder);
        gpu.device.queue.submit([encoder.finish()]);
        // Success path only: starting a readback map for a copy that never
        // reached the queue is its own bug (see `requestStats`).
        pyramids.afterSubmit();
      } finally {
        // Owed whether or not the frame reached the queue. A throw anywhere above
        // leaves an acquired video held across the frame, and the next acquire
        // then fails the frame-protocol check — self-healing, but only after a
        // wasted frame and a decoder buffer nobody released.
        pyramids.releaseAcquired();
      }

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
          try {
            const rebuilt = runRebuilds(
              pendingEncoder,
              frameContext.consumeDirtyBackdropSources(),
              frameContext.frame.timeMs,
            );
            pendingRebuilds = rebuilt.built;
            recordUnbuilt(frameContext.frame.id, rebuilt.unbuilt);
          } catch (error) {
            // Nothing will submit this encoder, so the releases owed for what was
            // already acquired have to happen here rather than in `render`.
            pendingEncoder = undefined;
            pyramids.releaseAcquired();
            throw error;
          }
        },

        render: (frameContext: FrameContextView) => {
          const encoder = pendingEncoder;
          pendingEncoder = undefined;
          if (encoder === undefined || context === undefined) return;
          const passes = runner as PassRunner;
          const pyramids = store as PyramidStore;

          try {
            if (targets !== undefined) {
              passes.clearPass(encoder, targets.optics);
              if (targets.highlight !== undefined) passes.clearPass(encoder, targets.highlight);
              drawGroups(encoder, frameContext.resolution);
            }

            context.device.queue.submit([encoder.finish()]);
            pyramids.afterSubmit();
          } finally {
            pyramids.releaseAcquired();
          }

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
      pendingUnbuilt = [];
      unbuiltFrameId = undefined;
      builtGeneration = undefined;
      dropContext();
      host.destroy();
    },
  };
}
