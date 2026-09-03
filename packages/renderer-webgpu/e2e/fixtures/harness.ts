/**
 * The in-page harness: everything that has to run where the GPU is.
 *
 * Playwright drives this over `page.evaluate`, so every entry point returns plain
 * JSON. Pixels come back as base64 rather than as an array of numbers — 384 000
 * numbers crossing the CDP bridge takes seconds, and the same bytes as base64 take
 * milliseconds.
 *
 * Rendering goes to an **offscreen `rgba8unorm` texture**, not to a canvas. That is
 * the sRGB lock of X5 made operational: a canvas would put the browser's own
 * compositing, colour management and DPR handling between the shader and the
 * golden, and none of those are what the golden is measuring. Reading back the
 * render target measures the renderer.
 */

import {
  createCopyProvider,
  createGradientProvider,
  createWebGPURenderer,
  createTimingCollector,
  linearGradientStops,
  linearToSrgbChannel,
  OUTPUT_TEXTURE_FORMAT,
  PASS_LABEL,
  supportsTimestamps,
  type BackdropProvider,
  type GlassRenderer,
  type MaterialProfilePatch,
} from "../../src/index";
import { CROSS_CHECK_WORKGROUP, crossCheckKernelModule } from "../../src/wgsl";
import { sceneByName, SCENE_NAMES, type BackdropSpec, type Scene } from "./scenes";

interface AdapterReport {
  readonly ok: boolean;
  readonly why?: string;
  readonly vendor?: string;
  readonly architecture?: string;
  /** `true` software, `false` measured hardware, `undefined` unmeasurable. */
  readonly isFallback?: boolean | undefined;
  readonly timestamps?: boolean;
}

let device: GPUDevice | undefined;
let adapterReport: AdapterReport = { ok: false, why: "not probed" };

/**
 * Is this adapter a CPU rasteriser? `undefined` means *nobody could tell*.
 *
 * `isFallbackAdapter` lives on `GPUAdapterInfo`; read off the `GPUAdapter` — as
 * this used to — it is `undefined` on current Chromium, so the gate in
 * `../support.ts` reported "hardware" for SwiftShader and never fired. Goldens
 * and benchmark numbers are what hangs on this, so `false` and `undefined` are
 * kept apart: a verdict nobody computed must not read as a clean bill of health.
 */
function softwareAdapter(info: GPUAdapterInfo): boolean | undefined {
  const flagged = (info as { isFallbackAdapter?: boolean }).isFallbackAdapter;
  if (typeof flagged === "boolean") return flagged;
  // The flag is the authority; this is only for a build that stops exposing it,
  // where Chromium's own software adapter still names itself.
  if (info.vendor === "google" && info.architecture === "swiftshader") return true;
  return undefined;
}

/**
 * WebGPU reports validation failures through an event, not an exception, so a
 * pipeline with a bad binding draws nothing and says nothing. Collecting them
 * here turns "the target is blank" into a message that names the pass.
 */
const gpuErrors: string[] = [];

async function ensureDevice(): Promise<GPUDevice> {
  if (device !== undefined) return device;
  if (navigator.gpu === undefined) throw new Error("navigator.gpu is undefined");

  const adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
  if (adapter === null) throw new Error("requestAdapter() returned null");

  const info = adapter.info ?? ({} as GPUAdapterInfo);
  const timestamps = adapter.features.has("timestamp-query");
  device = await adapter.requestDevice(
    timestamps ? { requiredFeatures: ["timestamp-query"] } : {},
  );
  const fallback = softwareAdapter(info);
  device.addEventListener("uncapturederror", (event) => {
    gpuErrors.push((event as GPUUncapturedErrorEvent).error.message);
  });
  adapterReport = {
    ok: true,
    vendor: info.vendor,
    architecture: info.architecture,
    isFallback: fallback,
    timestamps: supportsTimestamps(device),
  };
  return device;
}

// ---------------------------------------------------------------------------
// backdrops
// ---------------------------------------------------------------------------

function checkerboardImage(cell: number, size = 256): ImageData {
  const data = new Uint8ClampedArray(size * size * 4);
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const on = (Math.floor(x / cell) + Math.floor(y / cell)) % 2 === 0;
      // Encoded values, because copyExternalImageToTexture takes 8-bit sRGB and
      // the import pass decodes.
      const v = on ? 235 : 20;
      const i = (y * size + x) * 4;
      data[i] = v;
      data[i + 1] = v;
      data[i + 2] = v;
      data[i + 3] = 255;
    }
  }
  return new ImageData(data, size, size);
}

function flatImage(luminance: number, size = 64): ImageData {
  const v = Math.round(linearToSrgbChannel(luminance) * 255);
  const data = new Uint8ClampedArray(size * size * 4);
  for (let i = 0; i < data.length; i += 4) {
    data[i] = v;
    data[i + 1] = v;
    data[i + 2] = v;
    data[i + 3] = 255;
  }
  return new ImageData(data, size, size);
}

function providerFor(spec: BackdropSpec, gpu: GPUDevice): BackdropProvider | undefined {
  switch (spec.kind) {
    case "none":
      return undefined;
    case "checkerboard": {
      const image = checkerboardImage(spec.cell, spec.size);
      return createCopyProvider({
        id: "bg",
        // "canvas" is what makes a source live — dirty on every frame, which is
        // the video case the benchmark scene is defined around.
        kind: spec.live === true ? "canvas" : "image",
        device: gpu,
        source: image,
        width: image.width,
        height: image.height,
      });
    }
    case "flat": {
      const image = flatImage(spec.luminance);
      return createCopyProvider({
        id: "bg",
        kind: "image",
        device: gpu,
        source: image,
        width: image.width,
        height: image.height,
      });
    }
    case "gradient":
      return createGradientProvider({
        id: "bg",
        device: gpu,
        stops: linearGradientStops(spec.from, spec.to),
        direction: [0.6, 1],
        width: 128,
        height: 128,
      });
  }
}

// ---------------------------------------------------------------------------
// render targets and readback
// ---------------------------------------------------------------------------

interface Target {
  readonly texture: GPUTexture;
  readonly view: GPUTextureView;
}

function makeTarget(gpu: GPUDevice, width: number, height: number, label: string): Target {
  const texture = gpu.createTexture({
    label,
    size: { width, height, depthOrArrayLayers: 1 },
    format: OUTPUT_TEXTURE_FORMAT,
    usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC,
  });
  return { texture, view: texture.createView() };
}

/** `copyTextureToBuffer` needs 256-byte-aligned rows, so the copy is padded. */
async function readback(
  gpu: GPUDevice,
  texture: GPUTexture,
  width: number,
  height: number,
): Promise<Uint8Array> {
  const unpadded = width * 4;
  const padded = Math.ceil(unpadded / 256) * 256;
  const buffer = gpu.createBuffer({
    size: padded * height,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
  });

  const encoder = gpu.createCommandEncoder();
  encoder.copyTextureToBuffer(
    { texture },
    { buffer, bytesPerRow: padded, rowsPerImage: height },
    { width, height },
  );
  gpu.queue.submit([encoder.finish()]);

  await buffer.mapAsync(GPUMapMode.READ);
  const mapped = new Uint8Array(buffer.getMappedRange());
  const out = new Uint8Array(unpadded * height);
  for (let row = 0; row < height; row += 1) {
    out.set(mapped.subarray(row * padded, row * padded + unpadded), row * unpadded);
  }
  buffer.unmap();
  buffer.destroy();
  return out;
}

function toBase64(bytes: Uint8Array): string {
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

// ---------------------------------------------------------------------------
// scene rendering
// ---------------------------------------------------------------------------

interface SceneRun {
  readonly renderer: GlassRenderer;
  readonly optics: Target;
  readonly highlight: Target;
  readonly width: number;
  readonly height: number;
  dispose(): void;
}

/** Per-render switches a spec can throw. */
export interface RenderOptions {
  /**
   * Render the scene with its `backdropPlacement` withheld, so the backdrop is
   * cover-fit to the viewport — the pre-§5.47 rule, kept reachable so a spec can
   * show the two renders differ and pin what the old one produced.
   */
  readonly ignorePlacement?: boolean;
}

async function setUpScene(
  scene: Scene,
  materialProfile?: MaterialProfilePatch,
  options?: RenderOptions,
): Promise<SceneRun> {
  const gpu = await ensureDevice();
  const renderer = createWebGPURenderer({
    familyCVerified: true,
    ...(materialProfile === undefined ? {} : { materialProfile }),
  });
  renderer.attachDevice(gpu, "app");
  renderer.setViewport({
    widthCss: scene.widthCss,
    heightCss: scene.heightCss,
    devicePixelRatio: scene.devicePixelRatio,
  });

  const provider = providerFor(scene.backdrop, gpu);
  if (provider !== undefined) renderer.registerBackdrop(provider);
  if (scene.backdropPlacement !== undefined && options?.ignorePlacement !== true) {
    renderer.setBackdropPlacement("bg", scene.backdropPlacement);
  }
  for (const group of scene.groups) renderer.setGroup(group);

  const width = Math.round(scene.widthCss * scene.devicePixelRatio);
  const height = Math.round(scene.heightCss * scene.devicePixelRatio);
  const optics = makeTarget(gpu, width, height, "harness:optics");
  const highlight = makeTarget(gpu, width, height, "harness:highlight");

  return {
    renderer,
    optics,
    highlight,
    width,
    height,
    dispose() {
      optics.texture.destroy();
      highlight.texture.destroy();
      renderer.destroy();
    },
  };
}

async function runScene(
  scene: Scene,
  family?: "rsupn" | "rsup",
  materialProfile?: MaterialProfilePatch,
  governorLevel?: number,
  options?: RenderOptions,
): Promise<SceneRun> {
  const run = await setUpScene(scene, materialProfile, options);
  // The rung first, the family second: a caller naming both means "this rung,
  // but hold the field family", which is how the family comparison isolates one
  // knob at a time.
  if (governorLevel !== undefined) run.renderer.governor.setLevel(governorLevel);
  if (family !== undefined) run.renderer.governor.set({ fieldFamily: family });
  const frames = scene.warmupFrames ?? 1;
  for (let frame = 1; frame <= frames; frame += 1) {
    run.renderer.drawFrame({
      frame: { id: frame, timeMs: frame * 16.7 },
      optics: run.optics.view,
      highlight: run.highlight.view,
    });
    // Adaptation reaches the shader through a readback, so the loop has to give
    // the map a chance to resolve between frames.
    await run.renderer.collectAdaptation();
  }
  return run;
}

// ---------------------------------------------------------------------------
// the API Playwright drives
// ---------------------------------------------------------------------------

const api = {
  async probe(): Promise<AdapterReport> {
    try {
      await ensureDevice();
      return adapterReport;
    } catch (error) {
      return { ok: false, why: error instanceof Error ? error.message : String(error) };
    }
  },

  sceneNames(): readonly string[] {
    return SCENE_NAMES;
  },

  /** Validation and out-of-memory errors seen since the device was created. */
  errors(): readonly string[] {
    return [...gpuErrors];
  },

  /**
   * Render one scene.
   *
   * `materialProfile` is the isolation-proof seam (Decision Log #31(a)): the same
   * `MaterialProfilePatch` `createGlassRoot` takes, so a caller can render a scene
   * with a *past* set of optical constants and compare the result against a golden
   * baked before they moved. Nothing else in the pipeline is parameterised, which
   * is what makes byte-identity under a patch an attribution rather than a hope.
   */
  async renderScene(
    name: string,
    family?: "rsupn" | "rsup",
    materialProfile?: MaterialProfilePatch,
    options?: RenderOptions,
  ): Promise<{
    readonly width: number;
    readonly height: number;
    readonly pixels: string;
  }> {
    const scene = sceneByName(name);
    const run = await runScene(scene, family, materialProfile, undefined, options);
    try {
      const target = scene.capture === "highlight" ? run.highlight : run.optics;
      const bytes = await readback(await ensureDevice(), target.texture, run.width, run.height);
      if (gpuErrors.length > 0) {
        throw new Error(`WebGPU reported ${gpuErrors.length} error(s): ${gpuErrors.join(" | ")}`);
      }
      return { width: run.width, height: run.height, pixels: toBase64(bytes) };
    } finally {
      run.dispose();
    }
  },

  /**
   * Render one scene at a rung of the governor's ladder.
   *
   * Rungs 2 and 3 turn `refractionResolutionScale` down, which rasterises the
   * group's field targets below device resolution and makes the optics and
   * highlight passes *filter* what they read instead of indexing it. That branch
   * exists only under the knob, so it is compiled and executed nowhere else — and
   * a WebGPU validation failure is an event rather than an exception, so nothing
   * but a real adapter can say whether the branch is legal. Hence this seam.
   */
  async renderAtGovernorLevel(
    name: string,
    level: number,
  ): Promise<{
    readonly width: number;
    readonly height: number;
    readonly pixels: string;
  }> {
    const scene = sceneByName(name);
    const run = await runScene(scene, undefined, undefined, level);
    try {
      const target = scene.capture === "highlight" ? run.highlight : run.optics;
      const bytes = await readback(await ensureDevice(), target.texture, run.width, run.height);
      if (gpuErrors.length > 0) {
        throw new Error(`WebGPU reported ${gpuErrors.length} error(s): ${gpuErrors.join(" | ")}`);
      }
      return { width: run.width, height: run.height, pixels: toBase64(bytes) };
    } finally {
      run.dispose();
    }
  },

  /**
   * How deep the lens reaches into each group, in CSS px.
   *
   * Measured by differencing the scene against itself with refraction switched
   * off, counting the pixels that moved, and dividing by the surface's perimeter.
   * That quotient IS the band's depth — and the band's depth is `lensDepthPx`,
   * which is what parent acceptance #2's "a larger surface shows ... stronger
   * lensing" means physically.
   *
   * A mean over each surface's whole area would be the wrong metric and would
   * report the opposite: the lens occupies a larger FRACTION of a small surface,
   * so averaging over area rewards being small.
   */
  async measureLensing(name: string): Promise<Record<string, { depthCss: number; maxDelta: number }>> {
    const scene = sceneByName(name);
    const gpu = await ensureDevice();

    const capture = async (refraction: "true" | "none"): Promise<Uint8Array> => {
      const run = await setUpScene({
        ...scene,
        groups: scene.groups.map((group) => ({ ...group, refraction })),
      });
      try {
        run.renderer.drawFrame({
          frame: { id: 1, timeMs: 16.7 },
          optics: run.optics.view,
          highlight: run.highlight.view,
        });
        return await readback(gpu, run.optics.texture, run.width, run.height);
      } finally {
        run.dispose();
      }
    };

    const lensed = await capture("true");
    const flat = await capture("none");

    const dpr = scene.devicePixelRatio;
    const width = Math.round(scene.widthCss * dpr);
    const height = Math.round(scene.heightCss * dpr);
    const out: Record<string, { depthCss: number; maxDelta: number }> = {};
    const THRESHOLD = 3;

    for (const group of scene.groups) {
      let moved = 0;
      let maxDelta = 0;
      let perimeterDevice = 0;

      for (const surface of group.surfaces) {
        const [cx, cy] = surface.shape.center;
        const [w, h] = surface.shape.size;
        perimeterDevice += 2 * (w + h) * dpr;

        const x0 = Math.max(0, Math.floor((cx - w / 2) * dpr) - 2);
        const x1 = Math.min(width, Math.ceil((cx + w / 2) * dpr) + 2);
        const y0 = Math.max(0, Math.floor((cy - h / 2) * dpr) - 2);
        const y1 = Math.min(height, Math.ceil((cy + h / 2) * dpr) + 2);

        for (let y = y0; y < y1; y += 1) {
          for (let x = x0; x < x1; x += 1) {
            const i = (y * width + x) * 4;
            const delta = Math.max(
              Math.abs((lensed[i] ?? 0) - (flat[i] ?? 0)),
              Math.abs((lensed[i + 1] ?? 0) - (flat[i + 1] ?? 0)),
              Math.abs((lensed[i + 2] ?? 0) - (flat[i + 2] ?? 0)),
            );
            if (delta > maxDelta) maxDelta = delta;
            if (delta > THRESHOLD) moved += 1;
          }
        }
      }

      out[group.groupId] = {
        depthCss: perimeterDevice === 0 ? 0 : moved / perimeterDevice / dpr,
        maxDelta,
      };
    }
    return out;
  },

  /**
   * The §Core model invariant on a real device.
   *
   * The source is registered as a **live** provider — dirty on every frame, the
   * way `importExternalTexture`'s expire-at-task-end makes a video dirty on every
   * frame that samples it. That matters for what is being measured: against a
   * static source the second request in a frame is declined as *clean* and the
   * ledger never sees it, so only a live source exercises the ledger's own
   * refusal. Both routes decline, and the invariant is that neither ever serves.
   *
   * Two groups sample the one source, and each frame is handed the request twice
   * — something core would never do, since `consumeDirtyBackdropSources` hands out
   * one pass per frame id. The point is that the renderer holds the line anyway.
   */
  async invariant(frames: number): Promise<{
    readonly rebuilds: number;
    readonly peak: number;
    readonly refused: number;
    readonly skippedClean: number;
    readonly framesDrawn: number;
  }> {
    const gpu = await ensureDevice();
    const scene = sceneByName("refraction-checkerboard");
    const run = await setUpScene({
      ...scene,
      backdrop: { kind: "none" },
      groups: [
        ...scene.groups,
        { ...(scene.groups[0] as (typeof scene.groups)[number]), groupId: "second" },
      ],
    });

    const image = checkerboardImage(12);
    run.renderer.registerBackdrop(
      createCopyProvider({
        id: "bg",
        // "canvas" is what makes it live: a canvas may be redrawn at any time, so
        // the provider reports dirty every frame.
        kind: "canvas",
        device: gpu,
        source: image,
        width: image.width,
        height: image.height,
      }),
    );

    try {
      for (let frame = 1; frame <= frames; frame += 1) {
        run.renderer.drawFrame({
          frame: { id: frame, timeMs: frame * 16.7 },
          optics: run.optics.view,
          highlight: run.highlight.view,
          rebuild: [
            { sourceId: "bg", epoch: frame, resolution: { scale: 1, maxDimension: 2048 }, groupIds: ["g", "second"] },
            { sourceId: "bg", epoch: frame, resolution: { scale: 1, maxDimension: 2048 }, groupIds: ["g", "second"] },
          ],
        });
      }
      const stats = run.renderer.instrumentation.pyramid;
      return {
        rebuilds: stats.rebuilds,
        peak: stats.peakRebuildsPerSourcePerFrame,
        refused: stats.refusedDuplicates,
        skippedClean: stats.skippedClean,
        framesDrawn: run.renderer.instrumentation.framesDrawn,
      };
    } finally {
      run.dispose();
    }
  },

  /** Device-loss recovery, both ownership modes, against a real device. */
  async deviceLoss(mode: "app" | "vitrea"): Promise<{
    readonly beforeHealth: string;
    readonly afterHealth: string;
    readonly afterWebgpu: string;
    readonly replacementPending: boolean;
    readonly recoveredHealth: string;
    readonly generations: number;
    readonly drewAfterRecovery: boolean;
  }> {
    // A GPUAdapter is consumed by `requestDevice`, so each device needs its own.
    const freshDevice = async (): Promise<GPUDevice> => {
      const adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
      if (adapter === null) throw new Error("no adapter for the loss test");
      return adapter.requestDevice();
    };

    // Devices of their own, so destroying one cannot take the shared one down.
    const first = await freshDevice();
    const replacement = await freshDevice();
    const scene = sceneByName("field-mask");
    const renderer = createWebGPURenderer(
      mode === "vitrea"
        ? { reacquire: async () => replacement }
        : { onReplacementNeeded: () => undefined },
    );
    renderer.attachDevice(first, mode);
    renderer.setViewport({
      widthCss: scene.widthCss,
      heightCss: scene.heightCss,
      devicePixelRatio: scene.devicePixelRatio,
    });
    for (const group of scene.groups) renderer.setGroup(group);

    const width = Math.round(scene.widthCss * scene.devicePixelRatio);
    const height = Math.round(scene.heightCss * scene.devicePixelRatio);
    let optics = makeTarget(first, width, height, "loss:optics");
    renderer.drawFrame({ frame: { id: 1, timeMs: 16.7 }, optics: optics.view });
    const beforeHealth = renderer.deviceStatus.deviceHealth;

    // `destroy()` resolves `lost` with reason "destroyed", which the host treats
    // as our own teardown — so the loss is provoked the way a real one arrives.
    first.destroy();
    await first.lost;
    await new Promise((resolve) => setTimeout(resolve, 50));

    const afterHealth = renderer.deviceStatus.deviceHealth;
    const afterWebgpu = renderer.deviceStatus.webgpu;
    const replacementPending = renderer.deviceStatus.replacementPending;

    // Both modes end with a replacement in hand: vitrea-owned would have
    // re-requested by itself for a genuine loss, and an app-owned one waits for
    // exactly this call.
    renderer.replaceDevice(replacement);

    optics.texture.destroy();
    optics = makeTarget(replacement, width, height, "loss:optics:2");
    let drew = false;
    try {
      renderer.drawFrame({ frame: { id: 2, timeMs: 33.4 }, optics: optics.view });
      drew = true;
    } catch {
      // Left false: a draw that throws after recovery is exactly what this
      // reports, and swallowing it here is what lets the spec name it.
    }

    const result = {
      beforeHealth,
      afterHealth,
      afterWebgpu,
      replacementPending,
      recoveredHealth: renderer.deviceStatus.deviceHealth,
      generations: renderer.deviceStatus.generation,
      drewAfterRecovery: drew,
    };
    optics.texture.destroy();
    renderer.destroy();
    return result;
  },

  /**
   * Decision Log #20's f32 cross-check, on the device: the shipped kernels over a
   * caller-supplied point set. The f64 reference and the verdict live in Node.
   */
  async crossCheck(input: {
    readonly shapes: readonly number[];
    readonly points: readonly number[];
    readonly count: number;
  }): Promise<{ readonly rsupn: readonly number[]; readonly rsup: readonly number[] }> {
    const gpu = await ensureDevice();
    const module = gpu.createShaderModule({ code: crossCheckKernelModule() });
    const pipeline = gpu.createComputePipeline({
      layout: "auto",
      compute: { module, entryPoint: "cs_cross_check" },
    });

    const storage = (data: Float32Array): GPUBuffer => {
      const buffer = gpu.createBuffer({
        size: data.byteLength,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
      });
      gpu.queue.writeBuffer(buffer, 0, data);
      return buffer;
    };

    const shapes = storage(new Float32Array(input.shapes));
    const points = storage(new Float32Array(input.points));
    const outBytes = input.count * 4;
    const makeOut = (): GPUBuffer =>
      gpu.createBuffer({
        size: outBytes,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC,
      });
    const outRsupn = makeOut();
    const outRsup = makeOut();

    const counts = gpu.createBuffer({
      size: 16,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });
    gpu.queue.writeBuffer(counts, 0, new Uint32Array([input.count, 0, 0, 0]));

    const encoder = gpu.createCommandEncoder();
    const pass = encoder.beginComputePass();
    pass.setPipeline(pipeline);
    pass.setBindGroup(
      0,
      gpu.createBindGroup({
        layout: pipeline.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: { buffer: shapes } },
          { binding: 1, resource: { buffer: points } },
          { binding: 2, resource: { buffer: outRsupn } },
          { binding: 3, resource: { buffer: outRsup } },
          { binding: 4, resource: { buffer: counts } },
        ],
      }),
    );
    pass.dispatchWorkgroups(Math.ceil(input.count / CROSS_CHECK_WORKGROUP));
    pass.end();

    const readOne = async (source: GPUBuffer): Promise<number[]> => {
      const staging = gpu.createBuffer({
        size: outBytes,
        usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
      });
      const copy = gpu.createCommandEncoder();
      copy.copyBufferToBuffer(source, 0, staging, 0, outBytes);
      gpu.queue.submit([copy.finish()]);
      await staging.mapAsync(GPUMapMode.READ);
      const values = [...new Float32Array(staging.getMappedRange().slice(0))];
      staging.unmap();
      staging.destroy();
      return values;
    };

    gpu.queue.submit([encoder.finish()]);
    const rsupn = await readOne(outRsupn);
    const rsup = await readOne(outRsup);

    for (const buffer of [shapes, points, outRsupn, outRsup, counts]) buffer.destroy();
    return { rsupn, rsup };
  },

  /**
   * The benchmark: §Performance envelope's scenes, measured pass by pass.
   *
   * **Interleaved, not sequential, and that is the whole methodology.** Running
   * each config to completion in turn measured the same config at 0.995 ms in the
   * first slot and 1.901 ms in the last — a 1.9x spread on identical work, because
   * a GPU that has been busy for several seconds is not in the clock state of one
   * that just woke up. Sequential rows are therefore not comparable with each
   * other at all, and the difference between two of them says more about when they
   * ran than about what they rendered.
   *
   * So every config is set up first, and then each round draws one frame of each.
   * Drift now hits all of them equally, and the per-config medians are comparable
   * because they are drawn from the same stretch of wall-clock time.
   *
   * The median rather than the mean, for the ordinary reason: one scheduling
   * hiccup should not move a summary of sixty frames.
   */
  async bench(input: {
    readonly configs: readonly {
      readonly label: string;
      readonly widthCss: number;
      readonly heightCss: number;
      readonly devicePixelRatio: number;
      readonly family?: "rsupn" | "rsup";
      /**
       * Optical constants for this row — the same seam the isolation proof uses.
       *
       * It is here so that the cost of a FACET can be measured rather than
       * argued: two rows differing only in a profile field are drawn interleaved
       * in one process, which is the only methodology this benchmark trusts (see
       * the spec's note on the 1.9x spread the sequential shape produced on
       * identical work). Comparing two runs in two trees measures the GPU's clock
       * state at least as much as it measures the renderer.
       */
      readonly materialProfile?: MaterialProfilePatch;
    }[];
    readonly rounds: number;
    readonly warmup: number;
  }): Promise<{
    readonly method: "timestamp-query" | "wall-clock";
    readonly rounds: number;
    readonly results: readonly {
      readonly label: string;
      readonly gpuMsPerFrame: number | undefined;
      readonly gpuP95: number | undefined;
      readonly wallMsPerFrame: number;
      readonly wallP95: number;
      readonly passMs: Record<string, number>;
      readonly anomalies: number;
    }[];
  }> {
    const gpu = await ensureDevice();
    const timestamps = supportsTimestamps(gpu);

    const runs = await Promise.all(
      input.configs.map(async (config) => {
        const run = await setUpScene(benchScene(config), config.materialProfile);
        if (config.family !== undefined) run.renderer.governor.set({ fieldFamily: config.family });
        return {
          config,
          run,
          wall: [] as number[],
          gpuFrames: [] as number[],
          passTotals: new Map<string, number>(),
          timedFrames: 0,
        };
      }),
    );

    // One collector for the whole benchmark, reset before each frame. A query set
    // per frame would allocate hundreds of them and, worse, read slots that this
    // frame's passes never wrote.
    const timing = timestamps ? createTimingCollector(gpu, 256) : undefined;

    try {
      let frameId = 0;

      for (let i = 0; i < input.warmup; i += 1) {
        for (const entry of runs) {
          frameId += 1;
          entry.run.renderer.drawFrame({
            frame: { id: frameId, timeMs: frameId * 16.7 },
            optics: entry.run.optics.view,
            highlight: entry.run.highlight.view,
          });
        }
      }
      await gpu.queue.onSubmittedWorkDone();

      for (let round = 0; round < input.rounds; round += 1) {
        for (const entry of runs) {
          frameId += 1;
          timing?.reset();
          const start = performance.now();
          entry.run.renderer.drawFrame({
            frame: { id: frameId, timeMs: frameId * 16.7 },
            optics: entry.run.optics.view,
            highlight: entry.run.highlight.view,
            ...(timing === undefined ? {} : { timing }),
          });
          await gpu.queue.onSubmittedWorkDone();
          entry.wall.push(performance.now() - start);

          if (timing !== undefined) {
            const read = await timing.read();
            let frameTotal = 0;
            for (const [label, nanos] of read) {
              entry.passTotals.set(label, (entry.passTotals.get(label) ?? 0) + nanos / 1e6);
              frameTotal += nanos / 1e6;
            }
            entry.gpuFrames.push(frameTotal);
            entry.timedFrames += 1;
          }
        }
      }

      const quantile = (values: number[], q: number): number => {
        if (values.length === 0) return 0;
        const sorted = [...values].sort((a, b) => a - b);
        return sorted[Math.min(sorted.length - 1, Math.floor(q * sorted.length))] ?? 0;
      };

      const anomalies = timing?.anomalies ?? 0;
      return {
        method: timestamps ? "timestamp-query" : "wall-clock",
        rounds: input.rounds,
        results: runs.map((entry) => {
          const passMs: Record<string, number> = {};
          for (const [label, total] of entry.passTotals) {
            passMs[label] = total / Math.max(entry.timedFrames, 1);
          }
          for (const label of Object.values(PASS_LABEL)) passMs[label] ??= 0;
          return {
            label: entry.config.label,
            gpuMsPerFrame: entry.timedFrames === 0 ? undefined : quantile(entry.gpuFrames, 0.5),
            gpuP95: entry.timedFrames === 0 ? undefined : quantile(entry.gpuFrames, 0.95),
            wallMsPerFrame: quantile(entry.wall, 0.5),
            wallP95: quantile(entry.wall, 0.95),
            passMs,
            // Reported per config for want of a per-config counter; it is a
            // property of the whole run, and what matters is whether it is zero.
            anomalies,
          };
        }),
      };
    } finally {
      timing?.destroy();
      for (const entry of runs) entry.run.dispose();
    }
  },

};

/**
 * §Performance envelope's benchmark scene: 8 surfaces, 3 groups, one video-like
 * (always-dirty) backdrop, one active morph.
 *
 * The morph is represented by a surface whose channels sit mid-transition, which
 * is what a morph costs the renderer: the corner is re-derived and the instance
 * repacked every frame, and there is no cheaper state than that.
 */
function benchScene(config: {
  readonly widthCss: number;
  readonly heightCss: number;
  readonly devicePixelRatio: number;
}): Scene {
  const { widthCss, heightCss } = config;
  const surfaces = (prefix: string, count: number, y: number, size: [number, number]) =>
    Array.from({ length: count }, (_, i) => ({
      nodeId: `${prefix}${i}`,
      family: "fixed-rounded-rect" as const,
      shape: {
        center: [
          (widthCss / (count + 1)) * (i + 1),
          y,
        ] as [number, number],
        size,
        radii: [14, 14, 14, 14] as [number, number, number, number],
        smoothing: 0.5,
        thickness: 10,
      },
      reference: "figma-smoothing" as const,
      channels: { press: 0.2, glow: 0.4, sweep: 0.3, lensStrength: 1 },
    }));

  return {
    name: "bench",
    widthCss,
    heightCss,
    devicePixelRatio: config.devicePixelRatio,
    // One video-like backdrop: dirty every frame, so the pyramid is rebuilt
    // every frame — which is most of what the budget is spent on.
    backdrop: { kind: "checkerboard", cell: 12, live: true },
    groups: [
      {
        groupId: "toolbar",
        surfaces: surfaces("t", 4, heightCss * 0.18, [Math.min(72, widthCss / 6), 44]),
        backdropSourceId: "bg",
        refraction: "true",
        analysisExact: true,
      },
      {
        groupId: "segmented",
        surfaces: surfaces("s", 3, heightCss * 0.5, [Math.min(84, widthCss / 5), 40]),
        backdropSourceId: "bg",
        refraction: "true",
        analysisExact: true,
      },
      {
        groupId: "morph",
        surfaces: [
          {
            nodeId: "m",
            family: "fixed-rounded-rect",
            shape: {
              center: [widthCss / 2, heightCss * 0.8],
              size: [widthCss * 0.6, 96],
              radii: [30, 30, 30, 30],
              smoothing: 0.62,
              thickness: 16,
            },
            reference: "figma-smoothing",
            channels: { press: 0.35, glow: 0.8, sweep: 0.6, lensStrength: 1 },
          },
        ],
        backdropSourceId: "bg",
        refraction: "true",
        analysisExact: true,
      },
    ],
  };
}

/** The shape Playwright drives. `e2e/support.ts` declares `Window.vitrea` as this. */
export type VitreaHarness = typeof api;

declare global {
  interface Window {
    vitrea: VitreaHarness;
  }
}

window.vitrea = api;
document.documentElement.setAttribute("data-vitrea-ready", "1");
