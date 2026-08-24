/**
 * Shader-module and pipeline caches.
 *
 * Pipeline creation is the single most expensive thing a WebGPU renderer can do
 * per frame, and this renderer's pipeline set is small and fixed: two field
 * families, two import kinds, the chain, the analysis reduction, optics,
 * highlight. So the cache is a plain memo keyed by a descriptor string, and the
 * only interesting part is what goes into that key.
 *
 * Two rules about keys, both learned the same way — a cache that returns a
 * pipeline compiled against a different target format fails at draw time with an
 * error that names neither the format nor the cache:
 *
 *  - **Every property that changes the compiled artefact is in the key.** Target
 *    format, blend state, and the entry points, not just the shader name.
 *  - **Nothing else is.** Uniform *values* never are; they travel in buffers. A
 *    key that grew a tint colour would make the cache a leak.
 *
 * Like the texture pool, this is written over the narrow slice of `GPUDevice` it
 * uses, so eviction and key discipline are testable without an adapter.
 */

/** The slice of `GPUDevice` the caches need. `GPUDevice` satisfies it as-is. */
export interface PipelineFactory {
  createShaderModule(descriptor: GPUShaderModuleDescriptor): GPUShaderModule;
  createRenderPipeline(descriptor: GPURenderPipelineDescriptor): GPURenderPipeline;
  createComputePipeline(descriptor: GPUComputePipelineDescriptor): GPUComputePipeline;
}

export interface PipelineCacheStats {
  readonly modules: number;
  readonly renderPipelines: number;
  readonly computePipelines: number;
  readonly hits: number;
  readonly misses: number;
}

export interface PipelineCache {
  readonly stats: PipelineCacheStats;
  module(key: string, source: () => string): GPUShaderModule;
  renderPipeline(key: string, describe: () => GPURenderPipelineDescriptor): GPURenderPipeline;
  computePipeline(key: string, describe: () => GPUComputePipelineDescriptor): GPUComputePipeline;
  clear(): void;
}

export function createPipelineCache(factory: PipelineFactory): PipelineCache {
  const modules = new Map<string, GPUShaderModule>();
  const renderPipelines = new Map<string, GPURenderPipeline>();
  const computePipelines = new Map<string, GPUComputePipeline>();
  let hits = 0;
  let misses = 0;

  function memo<T>(store: Map<string, T>, key: string, make: () => T): T {
    const existing = store.get(key);
    if (existing !== undefined) {
      hits += 1;
      return existing;
    }
    misses += 1;
    const made = make();
    store.set(key, made);
    return made;
  }

  return {
    get stats() {
      return {
        modules: modules.size,
        renderPipelines: renderPipelines.size,
        computePipelines: computePipelines.size,
        hits,
        misses,
      };
    },

    module(key, source) {
      return memo(modules, key, () => factory.createShaderModule({ label: key, code: source() }));
    },

    renderPipeline(key, describe) {
      return memo(renderPipelines, key, () => factory.createRenderPipeline(describe()));
    },

    computePipeline(key, describe) {
      return memo(computePipelines, key, () => factory.createComputePipeline(describe()));
    },

    clear() {
      // GPU pipelines and modules have no explicit destroy: dropping the last
      // reference is the release. Clearing the maps IS the teardown, and it has to
      // happen on device loss because objects from a lost device stay unusable
      // forever.
      modules.clear();
      renderPipelines.clear();
      computePipelines.clear();
    },
  };
}

/** Pipeline keys, so the "everything that changes the artefact" rule is visible. */
export const pipelineKey = {
  field: (family: string, format: GPUTextureFormat): string => `field:${family}:${format}`,
  import: (kind: string, format: GPUTextureFormat): string => `import:${kind}:${format}`,
  chain: (entry: string, format: GPUTextureFormat): string => `chain:${entry}:${format}`,
  analysis: (): string => "analysis",
  optics: (format: GPUTextureFormat, blend: string): string => `optics:${format}:${blend}`,
  highlight: (format: GPUTextureFormat, blend: string): string => `highlight:${format}:${blend}`,
} as const;
