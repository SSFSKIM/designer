import { createStorageSlot, createUniformSlot, type GpuContext } from "./gpu-context";
import type { ResolvedSurface } from "./instances";
import type { FieldPassArgs, FieldTargets } from "./passes";
import type { PyramidResources } from "./pyramid";
import { silhouetteFieldModule, silhouetteReductionModule } from "./wgsl/silhouette-tone";

/** Structural twin of core's readout: the renderer cannot import its parent package. */
export interface SurfaceBackdropToneAbscissa {
  readonly surfaceId: string;
  readonly kind: "source" | "silhouette" | "hint";
  readonly encodedLuminance: number;
  readonly luminance: number;
  readonly linearLuminance: number;
  readonly color: readonly [number, number, number];
  readonly sampleCount: number;
  readonly level: number;
  readonly sourceWidth: number;
  readonly sourceHeight: number;
  readonly sampledWidth: number;
  readonly sampledHeight: number;
}

/** The mask follows the resolved surface's own bounds, including a concentric inset
 * or press compression, but retains G0's circular corner convention. */
export function packToneShapes(surfaces: readonly ResolvedSurface[], dpr: number): Float32Array {
  const data = new Float32Array(surfaces.length * 8);
  surfaces.forEach((surface, i) => {
    const [w, h] = surface.shape.channels.size;
    data.set([
      (surface.centre[0] - w / 2) * dpr, (surface.centre[1] - h / 2) * dpr,
      w * dpr, h * dpr, surface.shape.corner.radius * dpr, 0, 0, 0,
    ], i * 8);
  });
  return data;
}

interface DrawArgs {
  readonly groupId: string;
  readonly field: FieldPassArgs;
  readonly fields: FieldTargets;
  readonly surfaces: readonly ResolvedSurface[];
  readonly pyramid: PyramidResources;
  readonly viewportDevice: readonly [number, number];
  readonly fit: readonly [number, number, number, number];
  readonly fallbackTone: readonly [number, number, number, number];
}

type ReadingMetadata = Pick<SurfaceBackdropToneAbscissa,
  "surfaceId" | "sourceWidth" | "sourceHeight" | "sampledWidth" | "sampledHeight">;

export function toneReadingsFromBuffer(
  values: ArrayLike<number>, metadata: readonly ReadingMetadata[],
): readonly SurfaceBackdropToneAbscissa[] {
  return metadata.flatMap((meta, i) => values[i * 8 + 7]! <= 0 ? [] : [{
    ...meta, kind: "silhouette", level: 0,
    color: [values[i * 8]!, values[i * 8 + 1]!, values[i * 8 + 2]!],
    luminance: values[i * 8 + 3]!, encodedLuminance: values[i * 8 + 4]!,
    linearLuminance: values[i * 8 + 5]!, sampleCount: values[i * 8 + 6]!,
  }]);
}

export function createSilhouetteTonePass(context: GpuContext) {
  const { device, cache, pool } = context;
  const createEntry = (count: number, groupId: string) => ({
    groupId, count,
    shapes: createStorageSlot(device, count * 32, "vitrea:tone-shapes"),
    instances: createStorageSlot(device, count * 72, "vitrea:tone-instances"),
    uniform: createUniformSlot(device, 8, "vitrea:tone-uniform"),
    fieldUniform: createUniformSlot(device, 16, "vitrea:tone-field-uniform"),
    tones: device.createBuffer({ size: count * 32,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC }),
    readback: device.createBuffer({ size: count * 32,
      usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ }),
    metadata: [] as ReadingMetadata[],
    readings: [] as readonly SurfaceBackdropToneAbscissa[],
    queued: false,
    pending: undefined as Promise<void> | undefined,
  });
  const entries = new Map<string, ReturnType<typeof createEntry>>();
  const destroyEntry = (entry: ReturnType<typeof createEntry>) => {
    entry.shapes.destroy();
    entry.instances.destroy();
    entry.uniform.buffer.destroy();
    entry.fieldUniform.buffer.destroy();
    entry.tones.destroy();
    entry.readback.destroy();
  };
  const forget = (resourceId: string) => {
    const entry = entries.get(resourceId);
    if (entry !== undefined) destroyEntry(entry);
    entries.delete(resourceId);
    pool.release(`tone-field:${resourceId}`);
  };

  return {
    draw(encoder: GPUCommandEncoder, args: DrawArgs): GPUTextureView {
      const { field, pyramid, fields } = args;
      let entry = entries.get(field.resourceId);
      if (entry !== undefined && entry.count !== field.instanceCount) {
        forget(field.resourceId);
        entry = undefined;
      }
      if (entry === undefined) {
        entry = createEntry(field.instanceCount, args.groupId);
        entries.set(field.resourceId, entry);
      }
      const shapeData = packToneShapes(args.surfaces, 1 / field.cssPerDevice);
      entry.shapes.write(shapeData, shapeData.length);
      entry.instances.write(field.instances, field.instanceCount * 18);
      entry.uniform.data.set([...args.viewportDevice, 0, 0, ...args.fit]);
      entry.uniform.write();
      const pipeline = cache.computePipeline("silhouette-reduction", () => ({
        layout: "auto",
        compute: { module: cache.module("silhouette-reduction", silhouetteReductionModule),
          entryPoint: "reduce_tone" },
      }));
      const pass = encoder.beginComputePass({ label: "vitrea:silhouette-reduction" });
      pass.setPipeline(pipeline);
      pass.setBindGroup(0, device.createBindGroup({
        layout: pipeline.getBindGroupLayout(0), entries: [
          { binding: 0, resource: { buffer: entry.uniform.buffer } },
          { binding: 1, resource: pyramid.chain.createView({ baseMipLevel: 0, mipLevelCount: 1 }) },
          { binding: 3, resource: { buffer: entry.shapes.buffer } },
          { binding: 4, resource: { buffer: entry.tones } },
        ],
      }));
      pass.dispatchWorkgroups(field.instanceCount);
      pass.end();

      // Copy only into an idle readback buffer. Metadata belongs to this submitted
      // draw, never to the newer geometry that may exist when mapping completes.
      if (!entry.queued && entry.pending === undefined) {
        entry.metadata = args.surfaces.map((surface) => ({
          surfaceId: surface.nodeId,
          sourceWidth: pyramid.sourceWidth, sourceHeight: pyramid.sourceHeight,
          sampledWidth: pyramid.plan.width, sampledHeight: pyramid.plan.height,
        }));
        encoder.copyBufferToBuffer(entry.tones, 0, entry.readback, 0, entry.count * 32);
        entry.queued = true;
      }

      const texture = pool.acquire(`tone-field:${field.resourceId}`, {
        width: fields.width, height: fields.height, format: "rgba16float",
        usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING,
      });
      const u = entry.fieldUniform;
      u.data.set([field.rectDevice.width, field.rectDevice.height, field.cssPerDevice, 0,
        field.union.neckWidth, field.union.maxBulge, field.union.separationThreshold, 0]);
      new Uint32Array(u.data.buffer)[8] = field.instanceCount;
      u.data.set(args.fallbackTone, 12);
      u.write();
      const fieldPipeline = cache.renderPipeline(`silhouette-field:${field.family}`, () => ({
        layout: "auto",
        vertex: { module: cache.module(`silhouette-field:${field.family}`,
          () => silhouetteFieldModule(field.family)), entryPoint: "vs_fullscreen" },
        fragment: { module: cache.module(`silhouette-field:${field.family}`,
          () => silhouetteFieldModule(field.family)), entryPoint: "fs_tone",
          targets: [{ format: "rgba16float" }] },
        primitive: { topology: "triangle-list" },
      }));
      const view = texture.createView();
      const fieldPass = encoder.beginRenderPass({ label: "vitrea:silhouette-field",
        colorAttachments: [{ view, loadOp: "clear", storeOp: "store" }] });
      fieldPass.setPipeline(fieldPipeline);
      fieldPass.setBindGroup(0, device.createBindGroup({
        layout: fieldPipeline.getBindGroupLayout(0), entries: [
          { binding: 0, resource: { buffer: u.buffer } },
          { binding: 1, resource: { buffer: entry.instances.buffer } },
          { binding: 2, resource: { buffer: entry.tones } },
        ],
      }));
      fieldPass.draw(3);
      fieldPass.end();
      return view;
    },
    afterSubmit() {
      for (const entry of entries.values()) {
        if (!entry.queued) continue;
        entry.queued = false;
        entry.pending = entry.readback.mapAsync(GPUMapMode.READ).then(() => {
          entry.readings = toneReadingsFromBuffer(
            new Float32Array(entry.readback.getMappedRange()), entry.metadata,
          );
          entry.readback.unmap();
        }).catch(() => {
          // Removal or device loss invalidates the observation, not the next draw.
          entry.readings = [];
        }).finally(() => { entry.pending = undefined; });
      }
    },
    cancelQueued() {
      for (const entry of entries.values()) entry.queued = false;
    },
    async collect() {
      await Promise.all([...entries.values()].map((entry) => entry.pending));
    },
    readings(groupId: string): readonly SurfaceBackdropToneAbscissa[] {
      return [...entries.values()].filter((entry) => entry.groupId === groupId)
        .flatMap((entry) => entry.readings);
    },
    forget,
    destroy() {
      for (const resourceId of entries.keys()) forget(resourceId);
    },
  };
}
