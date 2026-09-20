/** W28 evidence only. No runtime branch or diagnostic profile option is added. */
import { createWebGPURenderer } from "../../src/renderer";
import { createCopyProvider } from "../../src/backdrop";
import { srgbToLinearChannel } from "../../src/color";
import { createGpuContext, createUniformSlot } from "../../src/gpu-context";
import { resolveSurfaces } from "../../src/instances";
import { createPyramidStore } from "../../src/pyramid";
import { packToneShapes, toneReadingsFromBuffer } from "../../src/silhouette-tone";
import { silhouetteReductionModule } from "../../src/wgsl/silhouette-tone";
import type { MaterialProfilePatch } from "../../src/material";
import type { SurfaceInput } from "../../src/render-model";

const makeDevice = async () => {
  const adapter = await navigator.gpu.requestAdapter();
  if (adapter === null) throw new Error("No GPU adapter");
  return adapter.requestDevice();
};

const surface = (id: string, x: number, y: number, w: number, h: number, radius: number): SurfaceInput => ({
  nodeId: id, family: "fixed-rounded-rect", reference: "figma-smoothing",
  shape: { center: [x, y], size: [w, h], radii: [radius, radius, radius, radius],
    smoothing: 0, thickness: 8 },
});

const quantile = (values: readonly number[], q: number) => {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor(q * sorted.length))]!;
};

/** Queue-completion WALL latency, not a partial sum of timestamped passes. The
 * production tone reduction/field do not register timestamp slots, so summing the
 * existing pass collector would omit exactly the work this experiment measures.
 * All rows are warmed up, then interleaved; order reverses on alternate rounds.
 * Shader compilation, texture upload, setup and explicit readback waits are outside
 * each measured interval. Runtime-internal copies/maps remain part of normal draw.
 */
export async function silhouetteCost(input: {
  canvas: { width: number; height: number }; warmup: number; rounds: number;
}) {
  if (input.warmup < 1 || input.rounds < 2) throw new Error("Need warmup and repeated rounds");
  const device = await makeDevice();
  device.pushErrorScope("validation");
  const entries = [];
  for (const geometry of ["two-host", "full-canvas"] as const) {
    const widthCss = geometry === "two-host" ? 128 : input.canvas.width;
    const heightCss = geometry === "two-host" ? 64 : input.canvas.height;
    const surfaces = geometry === "two-host"
      ? [surface("host-0", 32, 32, 48, 32, 8), surface("host-1", 96, 32, 48, 32, 8)]
      : [surface("full-canvas", widthCss / 2, heightCss / 2, widthCss, heightCss, 0)];
    for (const dpr of [1, 2]) for (const mode of ["source", "silhouette"] as const) {
      const width = widthCss * dpr, height = heightCss * dpr;
      const pixels = new Uint8Array(width * height * 4);
      for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
        const c = x < width / 2 ? (Math.floor(x / dpr) % 2) * 255 : 191;
        pixels.set([c, c, c, 255], (y * width + x) * 4);
      }
      const image = new ImageData(new Uint8ClampedArray(pixels), width, height);
      let sourceEncoded = 0, sourceLinear = 0;
      for (let i = 0; i < pixels.length; i += 4) {
        sourceEncoded += pixels[i]! / 255;
        sourceLinear += srgbToLinearChannel(pixels[i]! / 255);
      }
      sourceEncoded /= width * height;
      sourceLinear /= width * height;
      const patch: MaterialProfilePatch = {
        backdropToneAbscissa: mode === "source" ? "source" : { kind: "silhouette" },
        outerShadow: { thinOcclusionDark: 0, thinOcclusionMid: 0, thinOcclusionBright: 0,
          thickOcclusionAt96: 0, thickOcclusionAt128: 0, thickOcclusionAt160: 0, liftAmplitude: 0 },
        optics: { regular: { rimAlpha: 0, shadowAlpha: 0 } },
      };
      const renderer = createWebGPURenderer({ materialProfile: patch });
      renderer.attachDevice(device, "app");
      renderer.setViewport({ widthCss, heightCss, devicePixelRatio: dpr });
      renderer.registerBackdrop(createCopyProvider({ id: "bg", kind: "image", device,
        source: image, width, height }));
      renderer.setGroup({ groupId: "g", surfaces, backdropSourceId: "bg", refraction: "none",
        analysisExact: false, backdropTone: [sourceLinear, sourceLinear, sourceLinear],
        backdropToneLevel: srgbToLinearChannel(sourceEncoded), backdropToneLinearLuminance: sourceLinear,
        union: { neckWidth: 0, maxBulge: 0, separationThreshold: 0 } });
      const target = device.createTexture({ size: [width, height], format: "rgba8unorm",
        usage: GPUTextureUsage.RENDER_ATTACHMENT });
      entries.push({ geometry, dpr, mode, width, height, surfaces, patch, target,
        view: target.createView(), renderer, samples: [] as number[] });
    }
  }
  let frameId = 0;
  try {
    for (let round = -input.warmup; round < input.rounds; round++) {
      const ordered = round % 2 === 0 ? entries : [...entries].reverse();
      for (const entry of ordered) {
        await device.queue.onSubmittedWorkDone();
        frameId++;
        const start = performance.now();
        entry.renderer.drawFrame({ frame: { id: frameId, timeMs: frameId * 16.7 }, optics: entry.view });
        await device.queue.onSubmittedWorkDone();
        const elapsed = performance.now() - start;
        if (round >= 0) entry.samples.push(elapsed);
        // Do not put a map/readback wait or a screenshot inside the timed interval.
        await entry.renderer.collectAdaptation();
      }
    }
    const error = await device.popErrorScope();
    if (error !== null) throw new Error(error.message);
    const rows = entries.map((entry) => ({ geometry: entry.geometry, dpr: entry.dpr,
      mode: entry.mode, width: entry.width, height: entry.height, surfaces: entry.surfaces,
      materialPatch: entry.patch, wallMedianMs: quantile(entry.samples, 0.5),
      wallP95Ms: quantile(entry.samples, 0.95), samplesMs: entry.samples,
      pyramidRebuilds: entry.renderer.instrumentation.pyramid.rebuilds,
    }));
    const differences = rows.filter((row) => row.mode === "silhouette").map((local) => {
      const source = rows.find((row) => row.mode === "source" && row.geometry === local.geometry &&
        row.dpr === local.dpr)!;
      const paired = local.samplesMs.map((value, i) => value - source.samplesMs[i]!);
      return { geometry: local.geometry, dpr: local.dpr,
        medianPairedOverheadMs: quantile(paired, 0.5), p95PairedOverheadMs: quantile(paired, 0.95),
        pairedOverheadMs: paired };
    });
    return { method: "wall-clock through GPU queue completion; not GPU-only timestamps",
      timedWork: "CPU encode/submit and complete production GPU draw, including intrinsic runtime readback copies",
      excluded: "setup, uploads, warmup, explicit collectAdaptation waits, screenshots",
      warmup: input.warmup, rounds: input.rounds, rows, differences };
  } finally {
    for (const entry of entries) {
      entry.renderer.destroy(); entry.target.destroy();
    }
    device.destroy();
  }
}

/** Bind another view of the production pyramid to the UNMODIFIED production
 * silhouette reducer. Only the input mip changes. The grid and mask remain full
 * device resolution, so this isolates encoding after the pyramid's linear blur
 * from sparse-grid or geometry error. This is not the legacy whole-source
 * analysis shader, nor a profile option, and its result is never drawn or fitted.
 */
export async function silhouettePyramidDiagnostic(input: {
  pngDataUrl: string; dpr: number;
  shapes: readonly { id: string; left: number; top: number; width: number; height: number; radius: number }[];
}) {
  const bitmap = await createImageBitmap(await (await fetch(input.pngDataUrl)).blob());
  const device = await makeDevice();
  device.pushErrorScope("validation");
  const context = createGpuContext(device, 0);
  const store = createPyramidStore(context);
  const provider = createCopyProvider({ id: "bg", kind: "image", device, source: bitmap,
    width: bitmap.width, height: bitmap.height });
  const surfaces = resolveSurfaces({ groupId: "diagnostic", refraction: "none", analysisExact: false,
    surfaces: input.shapes.map((shape) => surface(shape.id, shape.left + shape.width / 2,
      shape.top + shape.height / 2, shape.width, shape.height, shape.radius)) }, "rsupn");
  const shapeData = packToneShapes(surfaces, input.dpr);
  const shapes = device.createBuffer({ size: shapeData.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST });
  device.queue.writeBuffer(shapes, 0, shapeData.buffer);
  const uniform = createUniformSlot(device, 8, "evidence:tone-diagnostic");
  uniform.data.set([bitmap.width, bitmap.height, 0, 0, 1, 1, 0, 0]);
  uniform.write();
  const byteLength = surfaces.length * 32;
  const output = device.createBuffer({ size: byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC });
  const readback = device.createBuffer({ size: byteLength,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
  try {
    store.beginFrame(1);
    const build = device.createCommandEncoder();
    const result = store.build({ sourceId: "bg", epoch: 1,
      resolution: { scale: 1, maxDimension: Math.max(bitmap.width, bitmap.height) },
      bodySigmaCss: 1.25 / input.dpr, heavySigmaCss: 0, heavy2SigmaCss: 0,
      viewportCss: [bitmap.width / input.dpr, bitmap.height / input.dpr] }, provider, build);
    if (result.status !== "built") throw new Error(`Pyramid build returned ${result.status}`);
    device.queue.submit([build.finish()]);
    store.afterSubmit(); store.releaseAcquired();
    await device.queue.onSubmittedWorkDone();
    const pyramid = result.resources;
    const pipeline = device.createComputePipeline({ layout: "auto",
      compute: { module: device.createShaderModule({ code: silhouetteReductionModule() }),
        entryPoint: "reduce_tone" } });
    const levels: { level: number; readings: ReturnType<typeof toneReadingsFromBuffer> }[] = [];
    for (const level of [0, pyramid.plan.analysisLevel]) {
      const encoder = device.createCommandEncoder();
      const pass = encoder.beginComputePass();
      pass.setPipeline(pipeline);
      pass.setBindGroup(0, device.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries: [
        { binding: 0, resource: { buffer: uniform.buffer } },
        { binding: 1, resource: pyramid.chain.createView({ baseMipLevel: level, mipLevelCount: 1 }) },
        { binding: 3, resource: { buffer: shapes } }, { binding: 4, resource: { buffer: output } },
      ] }));
      pass.dispatchWorkgroups(surfaces.length); pass.end();
      encoder.copyBufferToBuffer(output, 0, readback, 0, byteLength);
      device.queue.submit([encoder.finish()]);
      await readback.mapAsync(GPUMapMode.READ);
      const readings = toneReadingsFromBuffer(new Float32Array(readback.getMappedRange()),
        surfaces.map((shape) => ({ surfaceId: shape.nodeId,
          sourceWidth: bitmap.width, sourceHeight: bitmap.height,
          sampledWidth: pyramid.plan.levels[level]!.width,
          sampledHeight: pyramid.plan.levels[level]!.height,
        }))).map((reading) => ({ ...reading, level }));
      readback.unmap();
      levels.push({ level, readings });
    }
    const error = await device.popErrorScope();
    if (error !== null) throw new Error(error.message);
    return { dpr: input.dpr, sourceWidth: bitmap.width, sourceHeight: bitmap.height,
      analysisLevel: pyramid.plan.analysisLevel, levels,
      deltas: levels[0]!.readings.map((raw, i) => ({ surfaceId: raw.surfaceId,
        rawEncoded: raw.encodedLuminance, blurredEncoded: levels[1]!.readings[i]!.encodedLuminance,
        encodedDifference: levels[1]!.readings[i]!.encodedLuminance - raw.encodedLuminance,
        rawSampleCount: raw.sampleCount, blurredSampleCount: levels[1]!.readings[i]!.sampleCount,
      })) };
  } finally {
    store.releaseAcquired(); store.destroy(); provider.destroy(); context.destroy();
    shapes.destroy(); uniform.buffer.destroy(); output.destroy(); readback.destroy();
    bitmap.close(); device.destroy();
  }
}
