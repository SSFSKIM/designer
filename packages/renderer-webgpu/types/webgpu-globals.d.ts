/**
 * The WebGPU flag namespaces, declared.
 *
 * TypeScript 6's `lib.dom.d.ts` ships the WebGPU *interfaces* — `GPUDevice`,
 * `GPUTexture`, `GPUExternalTexture`, `GPUTextureUsageFlags` and the rest — but
 * not the three global namespace objects that carry the bit values:
 * `GPUBufferUsage`, `GPUTextureUsage`, `GPUMapMode`. They exist in every browser
 * that implements WebGPU; the lib just does not declare them.
 *
 * So this file declares them rather than hardcoding the numbers in source. The
 * distinction matters: writing `0x10` for `RENDER_ATTACHMENT` would bake a
 * spec constant into this package, and a usage flag silently mismatched against
 * the runtime's own value fails at texture creation with a message that names
 * neither. Reading them off the runtime keeps the browser as the authority.
 *
 * The members are typed as `number` and not as literal bit values on purpose:
 * this file is asserting that the globals *exist*, not what they equal.
 *
 * Delete this when `lib.dom.d.ts` declares them.
 */

declare const GPUBufferUsage: {
  readonly MAP_READ: number;
  readonly MAP_WRITE: number;
  readonly COPY_SRC: number;
  readonly COPY_DST: number;
  readonly INDEX: number;
  readonly VERTEX: number;
  readonly UNIFORM: number;
  readonly STORAGE: number;
  readonly INDIRECT: number;
  readonly QUERY_RESOLVE: number;
};

declare const GPUTextureUsage: {
  readonly COPY_SRC: number;
  readonly COPY_DST: number;
  readonly TEXTURE_BINDING: number;
  readonly STORAGE_BINDING: number;
  readonly RENDER_ATTACHMENT: number;
};

declare const GPUMapMode: {
  readonly READ: number;
  readonly WRITE: number;
};
