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
import { type GpuContext, createUniformSlot, type UniformSlot } from "./gpu-context";
import { pipelineKey } from "./pipeline-cache";
import { bodyBlurPlan, planPyramid, type PyramidPlan, type ResolutionPolicyView } from "./pyramid-plan";
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
  readonly stats: GPUBuffer;
  /** Source size epoch this allocation was made for. */
  readonly sizeEpoch: number;
  /** The dirty epoch the last successful rebuild satisfied. */
  readonly builtEpoch: number;
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
  readonly viewportCss: readonly [number, number];
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
  ): PyramidResources {
    const existing = resources.get(sourceId);
    const bodyWidth = (plan.levels[bodyLevel] ?? plan.levels[0] as { width: number; height: number }).width;
    const bodyHeight = (plan.levels[bodyLevel] ?? plan.levels[0] as { width: number; height: number }).height;

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

    let stats = existing?.stats;
    if (stats === undefined) {
      stats = device.createBuffer({
        label: `vitrea:pyramid:${sourceId}:stats`,
        size: ANALYSIS_STATS_FLOATS * 4,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC,
      });
    }

    if (existing === undefined || existing.chain !== chain || existing.body !== body) {
      reallocations += 1;
    }

    const next: PyramidResources = {
      sourceId,
      plan,
      chain,
      body,
      stats,
      sizeEpoch,
      builtEpoch,
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

  function runBodyBlur(
    encoder: GPUCommandEncoder,
    sourceId: string,
    plan: PyramidPlan,
    chain: GPUTexture,
    body: GPUTexture,
    level: number,
    residualSigmaTexels: number,
  ): void {
    const pipeline = chainPipeline("fs_blur");
    const size = plan.levels[level] ?? (plan.levels[0] as { width: number; height: number });
    const scratch = pool.acquire(poolKey.backdropBodyScratch(sourceId), {
      width: size.width,
      height: size.height,
      format: WORKING_TEXTURE_FORMAT,
      usage: chainUsage(),
      label: `vitrea:pyramid:${sourceId}:body-scratch`,
    });

    const stages: { target: GPUTexture; source: GPUTextureView; dir: [number, number]; tag: string }[] = [
      { target: scratch, source: mipView(chain, level), dir: [1, 0], tag: "h" },
      { target: body, source: scratch.createView(), dir: [0, 1], tag: "v" },
    ];

    for (const stage of stages) {
      const slot = uniformSlot(`body:${sourceId}:${stage.tag}`, 8);
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
        label: `vitrea:pass:body-blur-${stage.tag}:${sourceId}`,
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
        !provider.isDirty()
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
      // Source texels per CSS px, under the same cover fit the optics pass
      // samples with, times the downscale the plan actually applied (which
      // includes `maxDimension`, not just the policy's `scale`).
      const [viewportW, viewportH] = request.viewportCss;
      const cover =
        viewportW > 0 && viewportH > 0
          ? Math.max(frame.width / viewportW, frame.height / viewportH)
          : 1;
      const planScale = frame.width > 0 ? plan.width / frame.width : 1;
      const bodyPlan = bodyBlurPlan(request.bodySigmaCss * cover * planScale, plan);
      const target = allocate(
        request.sourceId,
        plan,
        bodyPlan.level,
        frame.sizeEpoch,
        request.epoch,
      );

      runImport(encoder, request.sourceId, frame, target.chain);
      runChain(encoder, request.sourceId, plan, target.chain);
      runBodyBlur(
        encoder,
        request.sourceId,
        plan,
        target.chain,
        target.body,
        bodyPlan.level,
        bodyPlan.residualSigmaTexels,
      );
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
