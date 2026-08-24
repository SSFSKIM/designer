/**
 * The WebGPU flag namespaces, for Node.
 *
 * `src/` reads `GPUTextureUsage.TEXTURE_BINDING` and friends off the runtime
 * rather than hardcoding the bit values, so that the browser stays the authority
 * on them — a usage flag silently mismatched against the real one fails at texture
 * creation with a message that names neither. The cost of that choice is that the
 * globals are absent under Node, and any module that computes a usage mask at
 * import time throws.
 *
 * So the values live here, in a **test-only** shim, where hardcoding them is a
 * statement about the spec rather than a fact this package depends on. They are
 * the normative constants from the WebGPU specification's `GPUBufferUsage`,
 * `GPUTextureUsage` and `GPUMapMode` namespaces.
 */

const define = (name: string, value: Record<string, number>): void => {
  if (name in globalThis) return;
  Object.defineProperty(globalThis, name, { value: Object.freeze(value), configurable: true });
};

define("GPUBufferUsage", {
  MAP_READ: 0x0001,
  MAP_WRITE: 0x0002,
  COPY_SRC: 0x0004,
  COPY_DST: 0x0008,
  INDEX: 0x0010,
  VERTEX: 0x0020,
  UNIFORM: 0x0040,
  STORAGE: 0x0080,
  INDIRECT: 0x0100,
  QUERY_RESOLVE: 0x0200,
});

define("GPUTextureUsage", {
  COPY_SRC: 0x01,
  COPY_DST: 0x02,
  TEXTURE_BINDING: 0x04,
  STORAGE_BINDING: 0x08,
  RENDER_ATTACHMENT: 0x10,
});

define("GPUMapMode", {
  READ: 0x0001,
  WRITE: 0x0002,
});
