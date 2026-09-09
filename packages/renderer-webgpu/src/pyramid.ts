/**
 * The blur/analysis pyramid, one per `BackdropSource`, and the ledger that proves
 * the §Core model invariant.
 *
 * > **Invariant:** blur/analysis pyramids belong to `BackdropSource`, rebuilt **at
 * > most once per dirty source per frame** — never per group. Static backdrops
 * > rebuild nothing.
 *
 * core enforces half of that already: `consumeDirtyBackdropSources(frameId)`
 * hands out one pass over the dirty set per frame id, so however many
 * participants ask, the second call returns nothing. What core *cannot* see is
 * this side of the wire — a renderer that also rebuilt lazily on first draw, or
 * that rebuilt once per group from one request, would satisfy core's guard and
 * violate the invariant. So the ledger here counts rebuilds per source per frame
 * on the renderer's own books, refuses a second one, and exposes the counters.
 * That is what makes the invariant *instrumented* rather than asserted.
 *
 * ## Pass structure per rebuild
 *
 * ```
 * import      provider frame  ->  chain mip 0     (premultiplied linear, X5)
 * downsample  mip n-1         ->  chain mip n     (13-tap, one pass per level)
 * blur x2     chain[bodyLvl]  ->  body            (separable, residual sigma)
 * blur x2     chain[heavyLvl] ->  heavy           (separable, residual sigma; W26)
 * analysis    chain[anaLvl]   ->  stats buffer    (compute, one workgroup)
 * ```
 *
 * Reading mip n-1 while rendering into mip n is legal because they are distinct
 * subresources, and every view here is created with an explicit
 * `baseMipLevel`/`mipLevelCount: 1` so that is true by construction rather than by
 * the driver's interpretation of a full-texture view.
 */

import { ANALYSIS_STATS_FLOATS, ANALYSIS_GRID, ANALYSIS_WORKGROUP } from "./wgsl/analysis";
import {
  alphaNormalisationMode,
  importColorMatrix,
  WORKING_TEXTURE_FORMAT,
} from "./color";
import { statsFromBuffer, type BackdropStats } from "./analysis";
import type { BackdropFrame, BackdropProvider } from "./backdrop";
import { texelsPerCssPx, type BackdropPlacement } from "./backdrop-fit";
import { type GpuContext, createUniformSlot, type UniformSlot } from "./gpu-context";
import { pipelineKey } from "./pipeline-cache";
import {
  bodyBlurPlan,
  heavyTapPlan,
  planPyramid,
  type PyramidPlan,
  type ResolutionPolicyView,
} from "./pyramid-plan";
import { createRebuildLedger, type RebuildLedger } from "./rebuild-ledger";
import { poolKey } from "./texture-pool";
import { PASS_LABEL, type PassTimeline } from "./timing";
import { analysisModule, chainModule, importModule } from "./wgsl";

/** Computed on first use, not at module scope — see the note in `passes.ts`. */
const chainUsage = (): GPUTextureUsageFlags =>
  GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING;

export interface PyramidResources {
  readonly sourceId: string;
  readonly plan: PyramidPlan;
  readonly chain: GPUTexture;
  readonly body: GPUTexture;
  /**
   * The **heavy** blur (W26; `MaterialProfile.sizeHeavyTapSigma`) — one more
   * texture beside the body, built by the same two separable passes from
   * whichever chain level `heavyTapPlan` names, and `undefined` where the
   * profile asked for no width.
   *
   * It is here rather than in the optics pass because the optics pass is a
   * fragment shader over the glass's own area: W26 G0 measured a 9 × 9 in-shader
   * grid at +1.1 ms on the mobile bench row against 0.070 ms for the two
   * separable passes the chain already runs (W26 Decision Log 2 (b)). The price
   * of building it here is that the width is **one per source** rather than one
   * per pixel — every group sampling this source gets the same heavy width,
   * because the texture is built before any group is drawn. The reference's heavy
   * width does not grade with the span at 1x (claims §5.113 §4), which is what
   * says the material can afford that.
   */
  readonly heavy: GPUTexture | undefined;
  readonly stats: GPUBuffer;
  /** Source size epoch this allocation was made for. */
  readonly sizeEpoch: number;
  /** The dirty epoch the last successful rebuild satisfied. */
  readonly builtEpoch: number;
  /**
   * The body blur's σ in **level-0 texels** — the CSS-px σ the material asked
   * for, through the same cover fit and plan downscale the build applied.
   *
   * Published because the conversion is only knowable here: it needs the frame's
   * real extent, which is exactly why `bodySigmaCss` arrives in CSS px. The size
   * law's scattering facet consumes it (W2) — the optics pass widens the body blur
   * per surface by sampling the chain, and it cannot find the level to measure
   * from without knowing where the body already sits.
   */
  readonly bodySigmaTexels: number;
  /**
   * Source texels per CSS px the build converted `bodySigmaCss` with — the placed
   * density where the source had a placement, the cover ratio where it did not
   * (`backdrop-fit.ts`) — and the source extent it was computed from. Recorded so
   * a later request can tell whether the body it would produce differs from the
   * one on the chain: a static image never re-dirties, so a placement whose SIZE
   * moved is the only signal that the σ in texels has gone stale.
   */
  readonly texelsPerCss: number;
  readonly sourceWidth: number;
  readonly sourceHeight: number;
  /**
   * The CSS-px σ the build converted with (W13 G1, review finding). The density
   * alone does not determine the body: since the widths became device-pixel
   * quantities (W12 G3, claims §5.56) the material's σ in CSS px is
   * `blurSigma / dpr`, so a window dragged from a 1x display to a 2x one asks
   * for a different body from the same source at the same density. A static
   * image never re-dirties, so this recorded σ is the only signal that the
   * chain's body and `bodyChainLod` belong to the previous scale.
   */
  readonly bodySigmaCss: number;
  /**
   * The heavy blur's σ in **CSS px** the build converted with, for `sameBody`'s
   * reason and by the same rule: the heavy width is a device-px quantity
   * (claims §5.113 §2), so `sizeHeavyTapSigma / dpr` is what reaches the source's
   * texels, and a window dragged between displays asks for a different heavy
   * texture from the same clean source.
   */
  readonly heavySigmaCss: number;
}

export interface PyramidInstrumentation {
  /** Successful rebuilds since the store was created. */
  readonly rebuilds: number;
  /** Rebuild attempts refused because the source had already rebuilt this frame. */
  readonly refusedDuplicates: number;
  /** Rebuilds skipped because the source was clean. */
  readonly skippedClean: number;
  readonly reallocations: number;
  /** Rebuild count for one source within the frame currently being recorded. */
  rebuildsInFrame(sourceId: string): number;
  /** Highest per-source rebuild count seen in any single frame. Must stay <= 1. */
  readonly peakRebuildsPerSourcePerFrame: number;
}

export interface PyramidBuildRequest {
  readonly sourceId: string;
  readonly epoch: number;
  readonly resolution: ResolutionPolicyView;
  /**
   * The material's body blur, in **CSS px**, with the viewport it is measured
   * against.
   *
   * Not in source texels, because the conversion between the two is a property of
   * the frame that has not been acquired yet: a 3840-wide video behind a 390 px
   * viewport packs ten source texels into every CSS px, so a σ of 8 texels would
   * be a σ of 0.8 CSS px on screen — a tenth of the frost the material asked for.
   * The build resolves it once the frame's real extent is known.
   */
  readonly bodySigmaCss: number;
  /**
   * The heavy blur's σ in **CSS px** (W26), 0 where the profile declines the
   * width — at which point nothing is allocated and nothing is drawn, so a
   * material that names no heavy width pays for none of this.
   */
  readonly heavySigmaCss: number;
  readonly viewportCss: readonly [number, number];
  /**
   * Where the source sits on the plane, in CSS px relative to the viewport, if
   * the host measured one. Absent, the source is cover-fit to the viewport.
   */
  readonly placement?: BackdropPlacement;
}

export type PyramidBuildOutcome =
  | { readonly status: "built"; readonly resources: PyramidResources }
  | { readonly status: "duplicate" }
  | { readonly status: "clean"; readonly resources: PyramidResources }
  | { readonly status: "unavailable"; readonly reason: string };

export interface PyramidStore {
  readonly instrumentation: PyramidInstrumentation;
  /** The invariant's ledger, exposed so a test can drive it without a device. */
  readonly ledger: RebuildLedger;
  /** Start recording a new frame. Clears the per-frame rebuild tally. */
  beginFrame(frameId: number): void;
  /** Attach a timing collector for this frame, or `undefined` to time nothing. */
  setTimeline(timeline: PassTimeline | undefined): void;
  build(
    request: PyramidBuildRequest,
    provider: BackdropProvider,
    encoder: GPUCommandEncoder,
  ): PyramidBuildOutcome;
  /**
   * Release every provider acquired this frame.
   *
   * Split from `afterSubmit` because the two halves have opposite failure rules.
   * A release is owed whether or not the frame reached the queue — an acquired
   * `VideoFrame` held across a frame stalls decoding — so this belongs in a
   * `finally` around the whole encode/submit. Call it after `queue.submit` on the
   * success path: an imported external texture must outlive the submission that
   * samples it.
   */
  releaseAcquired(): void;
  /**
   * Start the analysis readback maps. **Success path only**: `mapAsync` makes a
   * buffer unavailable to submits from the moment it is called, so starting a map
   * for a copy that was never submitted is its own bug — see `requestStats`.
   */
  afterSubmit(): void;
  /**
   * The source's pyramid, or `undefined` when it has none the pool still owns.
   * A caller may bind what this returns without checking anything further.
   */
  resources(sourceId: string): PyramidResources | undefined;
  /** Copy a source's stats into a staging buffer and map it. Cadence-gated by the caller. */
  requestStats(sourceId: string, encoder: GPUCommandEncoder): boolean;
  /** Resolve any completed stats readbacks. Returns what arrived. */
  collectStats(): Promise<ReadonlyMap<string, BackdropStats>>;
  forget(sourceId: string): void;
  destroy(): void;
}

interface StatsReadback {
  readonly staging: GPUBuffer;
  inFlight: boolean;
}

const densityOf = (
  source: { readonly width: number; readonly height: number },
  request: PyramidBuildRequest,
): number =>
  texelsPerCssPx(
    source.width,
    source.height,
    request.placement,
    request.viewportCss[0],
    request.viewportCss[1],
  );

/** Relative-tolerance equality, the comparison both halves of the body key take. */
const same = (next: number, existing: number): boolean =>
  Math.abs(next - existing) <= 1e-6 * Math.max(1, Math.abs(existing));

/**
 * Whether a request would produce the body the chain already carries — the same
 * σ in CSS px converted at the same density. Both halves are needed: the density
 * moves when a placement is resized or withdrawn, and the σ moves when the
 * device pixel ratio does, because the body's widths are device-pixel quantities
 * on this tier (W12 G3, claims §5.56; W15 G1, claims §5.69 §1) and
 * `bodySigmaCss` is `blurSigma / dpr`.
 *
 * The frame is not acquired at the clean check, so the source extent is the one
 * recorded at build — the same extent the recorded density came from, so the
 * comparison is exact for a source whose size held, and a source whose size
 * moved re-dirties through its own epoch anyway.
 */
/**
 * Whether two heavy σ would produce the same heavy blur — the ON/OFF state
 * EXACTLY, and only then the tolerance.
 *
 * `same` is a relative tolerance, and a relative tolerance around zero is an
 * absolute one of 1e-6: it calls σ 1e-7 and σ 0 equal. Those two are not equal
 * here, because they differ in KIND rather than in width. At 0 there is no heavy
 * texture and the optics pass takes the chain tap; at 1e-7 there is one, and
 * `heavyTapPlan` resolves that σ to level 0 with no residual — an unsampled copy
 * of the backdrop, which is the narrowest thing the mechanism can draw and the
 * furthest from what σ 0 means. So a material returning to 0 from a tiny positive
 * width has to REBUILD, and the tolerance applies only between two widths that
 * are both on.
 *
 * Exported because `renderer.ts` asks the same question of a clean source before
 * it asks the store anything, and the two must not be able to disagree.
 */
export const sameHeavySigma = (next: number, existing: number): boolean =>
  next > 0 === existing > 0 && same(next, existing);

const sameBody = (existing: PyramidResources, request: PyramidBuildRequest): boolean =>
  same(densityOf({ width: existing.sourceWidth, height: existing.sourceHeight }, request), existing.texelsPerCss)
  && same(request.bodySigmaCss, existing.bodySigmaCss)
  // The heavy blur rides the same key: it is built from the same chain at the
  // same density, so a σ that moved makes the texture on the source stale in
  // exactly the way a moved body σ does.
  && sameHeavySigma(request.heavySigmaCss, existing.heavySigmaCss);

export function createPyramidStore(context: GpuContext): PyramidStore {
  const { device, pool, cache } = context;

  const resources = new Map<string, PyramidResources>();
  const uniforms = new Map<string, UniformSlot>();
  const readbacks = new Map<string, StatsReadback>();
  const pendingRelease: BackdropProvider[] = [];
  const pendingStats = new Map<string, Promise<BackdropStats | undefined>>();
  /** Readbacks whose copy is encoded but whose map must wait for the submit. */
  const pendingMaps: string[] = [];

  let timeline: PassTimeline | undefined;
  const timedRender = (label: string): { timestampWrites?: GPURenderPassTimestampWrites } => {
    const slot = timeline?.renderSlot(label);
    return slot === undefined ? {} : { timestampWrites: slot };
  };
  const timedCompute = (label: string): { timestampWrites?: GPUComputePassTimestampWrites } => {
    const slot = timeline?.computeSlot(label);
    return slot === undefined ? {} : { timestampWrites: slot };
  };

  let frameId = -1;
  let reallocations = 0;
  const ledger: RebuildLedger = createRebuildLedger();

  const uniformSlot = (key: string, floats: number): UniformSlot => {
    let slot = uniforms.get(key);
    if (slot === undefined) {
      slot = createUniformSlot(device, floats, `vitrea:uniform:${key}`);
      uniforms.set(key, slot);
    }
    return slot;
  };

  const importPipeline = (kind: "sampled" | "external"): GPURenderPipeline =>
    cache.renderPipeline(pipelineKey.import(kind, WORKING_TEXTURE_FORMAT), () => ({
      label: `vitrea:pipeline:import:${kind}`,
      layout: "auto",
      vertex: {
        module: cache.module(`module:import:${kind}`, () => importModule(kind)),
        entryPoint: "vs_fullscreen",
      },
      fragment: {
        module: cache.module(`module:import:${kind}`, () => importModule(kind)),
        entryPoint: "fs_import",
        targets: [{ format: WORKING_TEXTURE_FORMAT }],
      },
      primitive: { topology: "triangle-list" },
    }));

  const chainPipeline = (entry: "fs_downsample" | "fs_blur"): GPURenderPipeline =>
    cache.renderPipeline(pipelineKey.chain(entry, WORKING_TEXTURE_FORMAT), () => ({
      label: `vitrea:pipeline:chain:${entry}`,
      layout: "auto",
      vertex: {
        module: cache.module("module:chain", chainModule),
        entryPoint: "vs_fullscreen",
      },
      fragment: {
        module: cache.module("module:chain", chainModule),
        entryPoint: entry,
        targets: [{ format: WORKING_TEXTURE_FORMAT }],
      },
      primitive: { topology: "triangle-list" },
    }));

  const analysisPipeline = (): GPUComputePipeline =>
    cache.computePipeline(pipelineKey.analysis(), () => ({
      label: "vitrea:pipeline:analysis",
      layout: "auto",
      compute: {
        module: cache.module("module:analysis", analysisModule),
        entryPoint: "cs_analysis",
      },
    }));

  /**
   * The source's resources, or `undefined` when the handles it recorded are no
   * longer the pool's.
   *
   * The pool owns the lifetime of both textures and can destroy them without this
   * store hearing about it — a size-epoch sweep, a device-loss `clear()`. The
   * recorded handles then name destroyed textures, and binding one is a WebGPU
   * validation error that takes the whole plane's encoder down with it. Two
   * identity compares turn that into "there is no backdrop this frame", which the
   * optics pass already has a placeholder for: unrefracted glass for a frame,
   * rather than a dropped one.
   */
  const liveResources = (sourceId: string): PyramidResources | undefined => {
    const target = resources.get(sourceId);
    if (target === undefined) return undefined;
    if (pool.peek(poolKey.backdropChain(sourceId)) !== target.chain) return undefined;
    if (pool.peek(poolKey.backdropBody(sourceId)) !== target.body) return undefined;
    if (target.heavy !== undefined && pool.peek(poolKey.backdropHeavy(sourceId)) !== target.heavy) {
      return undefined;
    }
    return target;
  };

  const mipView = (texture: GPUTexture, level: number): GPUTextureView =>
    texture.createView({ baseMipLevel: level, mipLevelCount: 1, dimension: "2d" });

  function allocate(
    sourceId: string,
    plan: PyramidPlan,
    bodyLevel: number,
    sizeEpoch: number,
    builtEpoch: number,
    bodySigmaTexels: number,
    density: { readonly texelsPerCss: number; readonly sourceWidth: number; readonly sourceHeight: number },
    bodySigmaCss: number,
    heavyLevel: number | undefined,
    heavySigmaCss: number,
  ): PyramidResources {
    const existing = resources.get(sourceId);
    const levelSize = (level: number): { width: number; height: number } =>
      plan.levels[level] ?? (plan.levels[0] as { width: number; height: number });
    const bodyWidth = levelSize(bodyLevel).width;
    const bodyHeight = levelSize(bodyLevel).height;

    const chain = pool.acquire(poolKey.backdropChain(sourceId), {
      width: plan.width,
      height: plan.height,
      format: WORKING_TEXTURE_FORMAT,
      usage: chainUsage(),
      mipLevelCount: plan.levelCount,
      label: `vitrea:pyramid:${sourceId}:chain`,
    });
    const body = pool.acquire(poolKey.backdropBody(sourceId), {
      width: bodyWidth,
      height: bodyHeight,
      format: WORKING_TEXTURE_FORMAT,
      usage: chainUsage(),
      label: `vitrea:pyramid:${sourceId}:body`,
    });

    /*
     * The heavy blur's texture (W26), acquired only where the profile named a
     * width. `undefined` is the landed material's answer, and it is what makes
     * the mechanism cost nothing there: no allocation, no two passes, and the
     * optics pass takes the single `textureSampleLevel` it has always taken.
     */
    let heavy: GPUTexture | undefined;
    if (heavyLevel === undefined) {
      // And RELEASED where it is not, rather than merely dropped from the record.
      // A material that sets the width back to 0 leaves a source whose pool still
      // holds the heavy texture and its scratch — two more full-level allocations
      // that nothing will ever bind and that only `forget` would reclaim, so they
      // would be held until the source is unregistered. The pool tolerates a
      // release of a key it does not hold, so this is also the path a source that
      // never had a heavy blur takes.
      pool.release(poolKey.backdropHeavy(sourceId));
      pool.release(poolKey.backdropHeavyScratch(sourceId));
    } else {
      heavy = pool.acquire(poolKey.backdropHeavy(sourceId), {
        width: levelSize(heavyLevel).width,
        height: levelSize(heavyLevel).height,
        format: WORKING_TEXTURE_FORMAT,
        usage: chainUsage(),
        label: `vitrea:pyramid:${sourceId}:heavy`,
      });
    }

    let stats = existing?.stats;
    if (stats === undefined) {
      stats = device.createBuffer({
        label: `vitrea:pyramid:${sourceId}:stats`,
        size: ANALYSIS_STATS_FLOATS * 4,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC,
      });
    }

    if (
      existing === undefined ||
      existing.chain !== chain ||
      existing.body !== body ||
      existing.heavy !== heavy
    ) {
      reallocations += 1;
    }

    const next: PyramidResources = {
      sourceId,
      plan,
      chain,
      body,
      heavy,
      stats,
      sizeEpoch,
      builtEpoch,
      bodySigmaTexels,
      texelsPerCss: density.texelsPerCss,
      sourceWidth: density.sourceWidth,
      sourceHeight: density.sourceHeight,
      bodySigmaCss,
      heavySigmaCss,
    };
    resources.set(sourceId, next);
    return next;
  }

  function runImport(
    encoder: GPUCommandEncoder,
    sourceId: string,
    frame: BackdropFrame,
    chain: GPUTexture,
  ): void {
    const kind = frame.binding.kind;
    const pipeline = importPipeline(kind);
    const slot = uniformSlot(`import:${sourceId}`, 16);
    const matrix = importColorMatrix(frame.colorSpace);

    slot.data[0] = matrix[0] as number;
    slot.data[1] = matrix[1] as number;
    slot.data[2] = matrix[2] as number;
    slot.data[3] = frame.encoded ? 1 : 0;
    slot.data[4] = matrix[3] as number;
    slot.data[5] = matrix[4] as number;
    slot.data[6] = matrix[5] as number;
    slot.data[7] = alphaNormalisationMode(frame.alphaMode);
    slot.data[8] = matrix[6] as number;
    slot.data[9] = matrix[7] as number;
    slot.data[10] = matrix[8] as number;
    slot.data[11] = 0;
    // Stretch fit: level 0 IS the source, resampled to the planned extent, so the
    // uv transform is the identity. A group's own framing of the backdrop happens
    // in the optics pass, where the viewport is known.
    slot.data[12] = 1;
    slot.data[13] = 1;
    slot.data[14] = 0;
    slot.data[15] = 0;
    slot.write();

    const entries: GPUBindGroupEntry[] = [
      { binding: 0, resource: { buffer: slot.buffer } },
      { binding: 1, resource: context.flatSampler },
      {
        binding: 2,
        resource:
          frame.binding.kind === "external" ? frame.binding.texture : frame.binding.view,
      },
    ];

    const pass = encoder.beginRenderPass({
      label: `vitrea:pass:import:${sourceId}`,
      ...timedRender(PASS_LABEL.import),
      colorAttachments: [
        { view: mipView(chain, 0), loadOp: "clear", storeOp: "store", clearValue: { r: 0, g: 0, b: 0, a: 0 } },
      ],
    });
    pass.setPipeline(pipeline);
    pass.setBindGroup(0, device.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries }));
    pass.draw(3);
    pass.end();
  }

  function runChain(
    encoder: GPUCommandEncoder,
    sourceId: string,
    plan: PyramidPlan,
    chain: GPUTexture,
  ): void {
    const pipeline = chainPipeline("fs_downsample");
    for (let level = 1; level < plan.levelCount; level += 1) {
      const source = plan.levels[level - 1] as { width: number; height: number };
      const slot = uniformSlot(`chain:${sourceId}:${level}`, 8);
      slot.data[0] = 1 / source.width;
      slot.data[1] = 1 / source.height;
      slot.data[2] = 0;
      slot.data[3] = 0;
      slot.data[4] = 0;
      slot.data[5] = 0;
      slot.data[6] = 0;
      slot.data[7] = 0;
      slot.write();

      const pass = encoder.beginRenderPass({
        label: `vitrea:pass:downsample:${sourceId}:${level}`,
        ...timedRender(PASS_LABEL.chain),
        colorAttachments: [
          { view: mipView(chain, level), loadOp: "clear", storeOp: "store", clearValue: { r: 0, g: 0, b: 0, a: 0 } },
        ],
      });
      pass.setPipeline(pipeline);
      pass.setBindGroup(
        0,
        device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: { buffer: slot.buffer } },
            { binding: 1, resource: context.flatSampler },
            { binding: 2, resource: mipView(chain, level - 1) },
          ],
        }),
      );
      pass.draw(3);
      pass.end();
    }
  }

  /**
   * The separable blur that takes one chain level up to an exact σ — two passes,
   * horizontal into a scratch of the level's own extent and vertical out of it.
   *
   * Parameterised by `kind` because W26 gave the pyramid a second one: the body
   * (`bodyBlurPlan`) and the heavy blur (`heavyTapPlan`) differ only in which
   * level they start from, which σ they finish at and which texture they land in,
   * so one function draws both and the pool keys, the uniform slots and the pass
   * labels are keyed by the kind rather than duplicated.
   */
  function runSeparableBlur(
    encoder: GPUCommandEncoder,
    sourceId: string,
    kind: "body" | "heavy",
    plan: PyramidPlan,
    chain: GPUTexture,
    target: GPUTexture,
    level: number,
    residualSigmaTexels: number,
  ): void {
    const pipeline = chainPipeline("fs_blur");
    const size = plan.levels[level] ?? (plan.levels[0] as { width: number; height: number });
    const scratchKey =
      kind === "body" ? poolKey.backdropBodyScratch(sourceId) : poolKey.backdropHeavyScratch(sourceId);
    const scratch = pool.acquire(scratchKey, {
      width: size.width,
      height: size.height,
      format: WORKING_TEXTURE_FORMAT,
      usage: chainUsage(),
      label: `vitrea:pyramid:${sourceId}:${kind}-scratch`,
    });

    const stages: { target: GPUTexture; source: GPUTextureView; dir: [number, number]; tag: string }[] = [
      { target: scratch, source: mipView(chain, level), dir: [1, 0], tag: "h" },
      { target, source: scratch.createView(), dir: [0, 1], tag: "v" },
    ];

    for (const stage of stages) {
      const slot = uniformSlot(`${kind}:${sourceId}:${stage.tag}`, 8);
      slot.data[0] = 1 / size.width;
      slot.data[1] = 1 / size.height;
      slot.data[2] = 0;
      slot.data[3] = 0;
      slot.data[4] = residualSigmaTexels;
      slot.data[5] = stage.dir[0];
      slot.data[6] = stage.dir[1];
      slot.data[7] = 0;
      slot.write();

      const pass = encoder.beginRenderPass({
        label: `vitrea:pass:${kind}-blur-${stage.tag}:${sourceId}`,
        ...timedRender(PASS_LABEL.bodyBlur),
        colorAttachments: [
          { view: stage.target.createView(), loadOp: "clear", storeOp: "store", clearValue: { r: 0, g: 0, b: 0, a: 0 } },
        ],
      });
      pass.setPipeline(pipeline);
      pass.setBindGroup(
        0,
        device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: { buffer: slot.buffer } },
            { binding: 1, resource: context.flatSampler },
            { binding: 2, resource: stage.source },
          ],
        }),
      );
      pass.draw(3);
      pass.end();
    }
  }

  function runAnalysis(
    encoder: GPUCommandEncoder,
    sourceId: string,
    plan: PyramidPlan,
    chain: GPUTexture,
    stats: GPUBuffer,
  ): void {
    const pipeline = analysisPipeline();
    const level = plan.levels[plan.analysisLevel] ?? (plan.levels[0] as { width: number; height: number });
    const slot = uniformSlot(`analysis:${sourceId}`, 8);
    slot.data[0] = ANALYSIS_GRID;
    slot.data[1] = ANALYSIS_GRID;
    slot.data[2] = plan.analysisLevel;
    slot.data[3] = 1 / (ANALYSIS_GRID - 1);
    slot.data[4] = 1 / level.width;
    slot.data[5] = 1 / level.height;
    slot.data[6] = 0;
    slot.data[7] = 0;
    slot.write();

    const pass = encoder.beginComputePass({
      label: `vitrea:pass:analysis:${sourceId}`,
      ...timedCompute(PASS_LABEL.analysis),
    });
    pass.setPipeline(pipeline);
    pass.setBindGroup(
      0,
      device.createBindGroup({
        layout: pipeline.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: { buffer: slot.buffer } },
          { binding: 1, resource: context.flatSampler },
          { binding: 2, resource: chain.createView() },
          { binding: 3, resource: { buffer: stats } },
        ],
      }),
    );
    // One workgroup: the reduction reads a fixed grid, so its cost does not
    // follow the backdrop's resolution. See wgsl/analysis.ts.
    pass.dispatchWorkgroups(1);
    pass.end();
  }

  return {
    instrumentation: {
      get rebuilds() {
        return ledger.rebuilds;
      },
      get refusedDuplicates() {
        return ledger.refusedDuplicates;
      },
      get skippedClean() {
        return ledger.skippedClean;
      },
      get reallocations() {
        return reallocations;
      },
      rebuildsInFrame(sourceId) {
        return ledger.countInFrame(sourceId);
      },
      get peakRebuildsPerSourcePerFrame() {
        return ledger.peakPerSourcePerFrame;
      },
    },

    /** The ledger the invariant is asserted against. See `rebuild-ledger.ts`. */
    ledger,

    beginFrame(next) {
      frameId = next;
      ledger.beginFrame(next);
    },

    setTimeline(next) {
      timeline = next;
    },

    build(request, provider, encoder) {
      // The LIVE resources, not merely the recorded ones: a clean-skip against a
      // handle the pool has already destroyed would leave the source with no
      // usable pyramid and no way back — the skip is exactly what stops the
      // reallocation that would heal it.
      const existing = liveResources(request.sourceId);
      if (
        existing !== undefined &&
        existing.builtEpoch >= request.epoch &&
        !provider.isDirty() &&
        sameBody(existing, request)
      ) {
        ledger.recordClean();
        return { status: "clean", resources: existing };
      }

      // Claimed BEFORE any pass is encoded: the ledger is the guard, not a
      // counter kept alongside one.
      if (!ledger.claim(request.sourceId)) {
        return { status: "duplicate" };
      }

      let frame: BackdropFrame;
      try {
        frame = provider.acquire({ id: frameId, timeMs: 0 });
      } catch (error) {
        return {
          status: "unavailable",
          reason: error instanceof Error ? error.message : String(error),
        };
      }
      pendingRelease.push(provider);

      const plan = planPyramid(frame.width, frame.height, request.resolution);
      // Source texels per CSS px — the placed density where the host measured a
      // placement, the cover ratio the optics pass samples with where it did not
      // (`backdrop-fit.ts`) — times the downscale the plan actually applied
      // (which includes `maxDimension`, not just the policy's `scale`).
      const texelsPerCss = densityOf(frame, request);
      const planScale = frame.width > 0 ? plan.width / frame.width : 1;
      const bodySigmaTexels = request.bodySigmaCss * texelsPerCss * planScale;
      const bodyPlan = bodyBlurPlan(bodySigmaTexels, plan);
      // The heavy blur (W26), through the identical conversion — the same density
      // and the same plan downscale, because it is the same chain read one or two
      // levels deeper. At σ 0 there is no plan, no texture and no pass.
      const heavyPlan =
        request.heavySigmaCss > 0
          ? heavyTapPlan(request.heavySigmaCss * texelsPerCss * planScale, plan)
          : undefined;
      const target = allocate(
        request.sourceId,
        plan,
        bodyPlan.level,
        frame.sizeEpoch,
        request.epoch,
        bodySigmaTexels,
        { texelsPerCss, sourceWidth: frame.width, sourceHeight: frame.height },
        request.bodySigmaCss,
        heavyPlan?.level,
        request.heavySigmaCss,
      );

      runImport(encoder, request.sourceId, frame, target.chain);
      runChain(encoder, request.sourceId, plan, target.chain);
      runSeparableBlur(
        encoder,
        request.sourceId,
        "body",
        plan,
        target.chain,
        target.body,
        bodyPlan.level,
        bodyPlan.residualSigmaTexels,
      );
      if (heavyPlan !== undefined && target.heavy !== undefined) {
        runSeparableBlur(
          encoder,
          request.sourceId,
          "heavy",
          plan,
          target.chain,
          target.heavy,
          heavyPlan.level,
          heavyPlan.residualSigmaTexels,
        );
      }
      runAnalysis(encoder, request.sourceId, plan, target.chain, target.stats);

      provider.markImported();
      return { status: "built", resources: target };
    },

    releaseAcquired() {
      // In acquisition order. A provider that throws on release must not strand
      // the others — a leaked VideoFrame stalls decoding.
      while (pendingRelease.length > 0) {
        const provider = pendingRelease.shift();
        try {
          provider?.release();
        } catch {
          // Deliberately swallowed; see above.
        }
      }
    },

    afterSubmit() {
      // The readback maps, now that the copies they read are in the queue.
      while (pendingMaps.length > 0) {
        const sourceId = pendingMaps.shift();
        if (sourceId === undefined) continue;
        const slot = readbacks.get(sourceId);
        if (slot === undefined) continue;
        const staging = slot.staging;
        pendingStats.set(
          sourceId,
          (async () => {
            try {
              await staging.mapAsync(GPUMapMode.READ);
              const values = new Float32Array(staging.getMappedRange().slice(0));
              staging.unmap();
              return statsFromBuffer(values);
            } catch {
              return undefined;
            } finally {
              slot.inFlight = false;
            }
          })(),
        );
      }
    },

    resources(sourceId) {
      return liveResources(sourceId);
    },

    requestStats(sourceId, encoder) {
      const target = liveResources(sourceId);
      if (target === undefined) return false;

      let readback = readbacks.get(sourceId);
      if (readback === undefined) {
        readback = {
          staging: device.createBuffer({
            label: `vitrea:pyramid:${sourceId}:stats-staging`,
            size: ANALYSIS_STATS_FLOATS * 4,
            usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST,
          }),
          inFlight: false,
        };
        readbacks.set(sourceId, readback);
      }
      // Single slot, no queue: if the previous map has not resolved, this frame's
      // readback is simply skipped. Queueing them is how a renderer under pressure
      // accumulates stale buffers, and two answers from the same frame are no more
      // useful than one.
      if (readback.inFlight) return false;

      encoder.copyBufferToBuffer(target.stats, 0, readback.staging, 0, ANALYSIS_STATS_FLOATS * 4);
      readback.inFlight = true;
      // The map is NOT started here. `mapAsync` makes a buffer unavailable to
      // submits from the moment it is called, and the copy just encoded has not
      // been submitted yet — starting the map now makes this frame's own submit
      // invalid with "used in submit while mapped". So the map is deferred to
      // `afterSubmit`.
      pendingMaps.push(sourceId);
      return true;
    },

    async collectStats() {
      const out = new Map<string, BackdropStats>();
      const entries = [...pendingStats];
      pendingStats.clear();
      for (const [sourceId, promise] of entries) {
        const stats = await promise;
        if (stats !== undefined) out.set(sourceId, stats);
      }
      return out;
    },

    forget(sourceId) {
      pool.release(poolKey.backdropChain(sourceId));
      pool.release(poolKey.backdropBody(sourceId));
      pool.release(poolKey.backdropBodyScratch(sourceId));
      pool.release(poolKey.backdropHeavy(sourceId));
      pool.release(poolKey.backdropHeavyScratch(sourceId));
      resources.get(sourceId)?.stats.destroy();
      resources.delete(sourceId);
      readbacks.get(sourceId)?.staging.destroy();
      readbacks.delete(sourceId);
      pendingStats.delete(sourceId);
      const queued = pendingMaps.indexOf(sourceId);
      if (queued >= 0) pendingMaps.splice(queued, 1);
    },

    destroy() {
      for (const sourceId of [...resources.keys()]) this.forget(sourceId);
      for (const slot of uniforms.values()) slot.buffer.destroy();
      uniforms.clear();
      pendingRelease.length = 0;
      pendingMaps.length = 0;
    },
  };
}

/** Exposed so a test can assert the workgroup size the reduction was written for. */
export const ANALYSIS_DISPATCH = { workgroupSize: ANALYSIS_WORKGROUP, workgroups: 1 } as const;
