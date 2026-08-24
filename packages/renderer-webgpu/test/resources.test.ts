/**
 * The texture pool and the pipeline cache.
 *
 * Both are written over a narrow slice of `GPUDevice` precisely so this file can
 * exist: leak accounting and epoch discipline are the half of the resource graph
 * most likely to be quietly wrong, and they are testable with no adapter at all.
 */

import { describe, expect, it } from "vitest";

import { createPipelineCache, pipelineKey, type PipelineFactory } from "../src/pipeline-cache";
import { createTexturePool, poolKey, type TextureAllocator } from "../src/texture-pool";

interface FakeTexture {
  readonly id: number;
  readonly descriptor: GPUTextureDescriptor;
  destroyed: boolean;
}

function fakeAllocator(): { allocator: TextureAllocator; textures: FakeTexture[] } {
  const textures: FakeTexture[] = [];
  const allocator: TextureAllocator = {
    createTexture(descriptor) {
      const texture: FakeTexture = { id: textures.length, descriptor, destroyed: false };
      textures.push(texture);
      return {
        destroy: () => {
          texture.destroyed = true;
        },
      } as unknown as GPUTexture;
    },
  };
  return { allocator, textures };
}

const request = (width: number, height: number) => ({
  width,
  height,
  format: "rgba16float" as GPUTextureFormat,
  usage: 0x10,
});

describe("the texture pool", () => {
  it("returns the same texture for the same key and shape within an epoch", () => {
    const { allocator, textures } = fakeAllocator();
    const pool = createTexturePool(allocator);

    const first = pool.acquire("a", request(64, 32));
    const second = pool.acquire("a", request(64, 32));

    expect(second).toBe(first);
    expect(textures).toHaveLength(1);
    expect(pool.stats.reused).toBe(1);
  });

  it("reallocates when the shape changes and destroys the old one", () => {
    const { allocator, textures } = fakeAllocator();
    const pool = createTexturePool(allocator);

    pool.acquire("a", request(64, 32));
    pool.acquire("a", request(128, 32));

    expect(textures).toHaveLength(2);
    expect(textures[0]?.destroyed).toBe(true);
    expect(pool.stats.live).toBe(1);
    expect(pool.stats.destroyed).toBe(1);
  });

  it("invalidates on the size epoch even when the dimensions are identical", () => {
    // The property the whole module exists for. A size epoch also covers DPR and
    // resolution-policy changes that leave the pixel count alone, so comparing
    // sizes would silently keep a texture whose MEANING changed.
    const { allocator, textures } = fakeAllocator();
    const pool = createTexturePool(allocator);

    const before = pool.acquire("a", request(64, 32));
    pool.bumpSizeEpoch();
    const after = pool.acquire("a", request(64, 32));

    expect(after).not.toBe(before);
    expect(textures[0]?.destroyed).toBe(true);
    expect(textures).toHaveLength(2);
  });

  it("sweeps every stale allocation and leaves the fresh ones alone", () => {
    const { allocator, textures } = fakeAllocator();
    const pool = createTexturePool(allocator);

    pool.acquire("a", request(8, 8));
    pool.acquire("b", request(8, 8));
    pool.bumpSizeEpoch();
    pool.acquire("a", request(8, 8));

    expect(pool.sweep()).toBe(1);
    expect(pool.stats.live).toBe(1);
    expect(textures.filter((texture) => texture.destroyed)).toHaveLength(2);
  });

  it("destroys exactly once on release and tolerates releasing nothing", () => {
    const { allocator, textures } = fakeAllocator();
    const pool = createTexturePool(allocator);

    pool.acquire("a", request(8, 8));
    pool.release("a");
    pool.release("a");
    pool.release("never-allocated");

    expect(pool.stats.destroyed).toBe(1);
    expect(textures.filter((texture) => texture.destroyed)).toHaveLength(1);
  });

  it("clears everything, which is what device-loss teardown needs", () => {
    const { allocator, textures } = fakeAllocator();
    const pool = createTexturePool(allocator);

    pool.acquire("a", request(8, 8));
    pool.acquire("b", request(8, 8));
    pool.clear();

    expect(pool.stats.live).toBe(0);
    expect(textures.every((texture) => texture.destroyed)).toBe(true);
  });

  it("floors dimensions to at least one pixel", () => {
    const { allocator, textures } = fakeAllocator();
    const pool = createTexturePool(allocator);

    pool.acquire("a", { ...request(0, 0) });
    const size = textures[0]?.descriptor.size as GPUExtent3DDict;
    expect(size.width).toBe(1);
    expect(size.height).toBe(1);
  });

  it("keys every purpose separately so two sources cannot collide", () => {
    const keys = [
      poolKey.backdropChain("a"),
      poolKey.backdropChain("b"),
      poolKey.backdropBody("a"),
      poolKey.groupField("a"),
      poolKey.groupAux("a"),
    ];
    expect(new Set(keys).size).toBe(keys.length);
  });
});

function fakeFactory(): { factory: PipelineFactory; calls: string[] } {
  const calls: string[] = [];
  const factory: PipelineFactory = {
    createShaderModule(descriptor) {
      calls.push(`module:${descriptor.label ?? "?"}`);
      return {} as GPUShaderModule;
    },
    createRenderPipeline(descriptor) {
      calls.push(`render:${descriptor.label ?? "?"}`);
      return {} as GPURenderPipeline;
    },
    createComputePipeline(descriptor) {
      calls.push(`compute:${descriptor.label ?? "?"}`);
      return {} as GPUComputePipeline;
    },
  };
  return { factory, calls };
}

describe("the pipeline cache", () => {
  it("compiles a module once per key", () => {
    const { factory, calls } = fakeFactory();
    const cache = createPipelineCache(factory);

    const first = cache.module("field:rsupn", () => "code");
    const second = cache.module("field:rsupn", () => "code");

    expect(second).toBe(first);
    expect(calls).toHaveLength(1);
    expect(cache.stats.hits).toBe(1);
    expect(cache.stats.misses).toBe(1);
  });

  it("never calls the source thunk on a hit", () => {
    const { factory } = fakeFactory();
    const cache = createPipelineCache(factory);
    let built = 0;

    cache.module("k", () => {
      built += 1;
      return "code";
    });
    cache.module("k", () => {
      built += 1;
      return "code";
    });

    expect(built).toBe(1);
  });

  it("separates render and compute pipelines under the same key text", () => {
    const { factory, calls } = fakeFactory();
    const cache = createPipelineCache(factory);

    cache.renderPipeline("x", () => ({ label: "r" }) as GPURenderPipelineDescriptor);
    cache.computePipeline("x", () => ({ label: "c" }) as GPUComputePipelineDescriptor);

    expect(calls).toEqual(["render:r", "compute:c"]);
    expect(cache.stats.renderPipelines).toBe(1);
    expect(cache.stats.computePipelines).toBe(1);
  });

  it("puts every artefact-changing property in the key and nothing else", () => {
    // Target format changes the compiled pipeline, so it is in the key; a tint
    // colour does not, and a key that grew one would make the cache a leak.
    expect(pipelineKey.field("rsupn", "rgba16float")).not.toBe(
      pipelineKey.field("rsup", "rgba16float"),
    );
    expect(pipelineKey.optics("rgba8unorm", "over")).not.toBe(
      pipelineKey.optics("bgra8unorm", "over"),
    );
    expect(pipelineKey.optics("rgba8unorm", "over")).not.toBe(
      pipelineKey.optics("rgba8unorm", "none"),
    );
  });

  it("clears, because objects from a lost device stay unusable forever", () => {
    const { factory } = fakeFactory();
    const cache = createPipelineCache(factory);

    cache.module("k", () => "code");
    cache.clear();

    expect(cache.stats.modules).toBe(0);
    cache.module("k", () => "code");
    expect(cache.stats.misses).toBe(2);
  });
});
