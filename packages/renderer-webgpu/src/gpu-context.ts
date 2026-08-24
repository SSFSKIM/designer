/**
 * Everything that belongs to one device generation, in one object.
 *
 * A device loss makes every GPU object made from that device permanently
 * unusable, and the failure is *silent* — bindings simply stop producing pixels.
 * So the pool, the pipeline cache, the samplers and the uniform buffers are held
 * together with the generation they were made under, and recovery replaces the
 * whole context rather than reaching into it. That makes "did I just bind a
 * resource from a dead device" impossible to get wrong instead of merely unlikely.
 */

import { createPipelineCache, type PipelineCache } from "./pipeline-cache";
import { createTexturePool, type TexturePool } from "./texture-pool";

export interface GpuContext {
  readonly device: GPUDevice;
  /** The device generation this context belongs to. */
  readonly generation: number;
  readonly pool: TexturePool;
  readonly cache: PipelineCache;
  /** Linear min/mag with linear mip filtering — the pyramid's sampler. */
  readonly chainSampler: GPUSampler;
  /** Linear min/mag, no mips — the body blur and import samplers. */
  readonly flatSampler: GPUSampler;
  destroy(): void;
}

export function createGpuContext(device: GPUDevice, generation: number): GpuContext {
  const pool = createTexturePool(device);
  const cache = createPipelineCache(device);

  // Clamp-to-edge on every axis. A repeating pyramid would wrap the backdrop
  // across the refraction offset at a group's edge, which reads as a hard seam
  // exactly where the lens is strongest.
  const chainSampler = device.createSampler({
    label: "vitrea:sampler:chain",
    magFilter: "linear",
    minFilter: "linear",
    mipmapFilter: "linear",
    addressModeU: "clamp-to-edge",
    addressModeV: "clamp-to-edge",
  });

  const flatSampler = device.createSampler({
    label: "vitrea:sampler:flat",
    magFilter: "linear",
    minFilter: "linear",
    addressModeU: "clamp-to-edge",
    addressModeV: "clamp-to-edge",
  });

  return {
    device,
    generation,
    pool,
    cache,
    chainSampler,
    flatSampler,
    destroy() {
      pool.clear();
      cache.clear();
    },
  };
}

/** A uniform buffer sized to a fixed float count, reused across frames. */
export interface UniformSlot {
  readonly buffer: GPUBuffer;
  readonly data: Float32Array;
  write(): void;
}

export function createUniformSlot(
  device: GPUDevice,
  floats: number,
  label: string,
): UniformSlot {
  // Uniform buffers must be a multiple of 16 bytes, and every struct in this
  // package is laid out as vec4 rows precisely so this rounding never silently
  // truncates a member.
  const size = Math.ceil((floats * 4) / 16) * 16;
  const buffer = device.createBuffer({
    label,
    size,
    usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
  });
  const data = new Float32Array(size / 4);
  return {
    buffer,
    data,
    write() {
      device.queue.writeBuffer(buffer, 0, data.buffer, data.byteOffset, data.byteLength);
    },
  };
}

/** A storage buffer that grows in place when the instance count outgrows it. */
export interface StorageSlot {
  readonly buffer: GPUBuffer;
  ensure(byteLength: number): GPUBuffer;
  write(data: Float32Array, floatCount: number): void;
  destroy(): void;
}

export function createStorageSlot(
  device: GPUDevice,
  initialBytes: number,
  label: string,
): StorageSlot {
  let capacity = Math.max(initialBytes, 256);
  let buffer = device.createBuffer({
    label,
    size: capacity,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
  });

  return {
    get buffer() {
      return buffer;
    },
    ensure(byteLength) {
      if (byteLength <= capacity) return buffer;
      buffer.destroy();
      // Grow in powers of two: a group that gains one surface per frame during a
      // morph would otherwise reallocate every frame.
      capacity = 1 << Math.ceil(Math.log2(byteLength));
      buffer = device.createBuffer({
        label,
        size: capacity,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
      });
      return buffer;
    },
    write(data, floatCount) {
      device.queue.writeBuffer(buffer, 0, data.buffer, data.byteOffset, floatCount * 4);
    },
    destroy() {
      buffer.destroy();
    },
  };
}
