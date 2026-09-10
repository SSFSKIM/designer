/**
 * The texture pool, with size-epoch invalidation.
 *
 * §GPU device ownership: "Resizes bump a size epoch that invalidates dependent
 * pyramid allocations." Two properties follow from taking that literally, and
 * both are what the pool exists for:
 *
 *  - **A texture is keyed by purpose, not by shape.** Callers ask for
 *    `"pyramid:bg-video:level-2"`, not for "a 512×256 rgba16float". So a resize
 *    replaces an allocation in place rather than leaking a second one beside it,
 *    and the leak is impossible rather than unlikely.
 *  - **The epoch is compared, not the size.** A texture allocated under an older
 *    epoch is destroyed even when its dimensions happen to match, because a size
 *    epoch also covers DPR changes and resolution-policy changes that leave the
 *    pixel count alone. Comparing sizes would silently keep a texture whose
 *    *meaning* changed.
 *
 * The pool is written over a two-method `TextureAllocator` rather than against
 * `GPUDevice` directly. That is not indirection for its own sake: it makes the
 * keying, the epoch sweep, and the destroy-exactly-once accounting testable
 * without a GPU, which is the half of this file most likely to harbour a leak.
 */

export interface TextureRequest {
  readonly width: number;
  readonly height: number;
  readonly format: GPUTextureFormat;
  readonly usage: GPUTextureUsageFlags;
  /** Mip levels. The blur chain is the only caller that asks for more than one. */
  readonly mipLevelCount?: number;
  readonly label?: string;
}

/** The slice of `GPUDevice` the pool needs. `GPUDevice` satisfies it as-is. */
export interface TextureAllocator {
  createTexture(descriptor: GPUTextureDescriptor): GPUTexture;
}

interface PoolEntry {
  readonly texture: GPUTexture;
  readonly request: TextureRequest;
  readonly epoch: number;
}

export interface TexturePoolStats {
  readonly live: number;
  readonly created: number;
  readonly destroyed: number;
  readonly reused: number;
  readonly epoch: number;
}

export interface TexturePool {
  readonly sizeEpoch: number;
  readonly stats: TexturePoolStats;
  /**
   * The texture for `key` at the current epoch, allocating or reallocating as
   * needed. Two calls with the same key and the same request in one epoch return
   * the same texture.
   */
  acquire(key: string, request: TextureRequest): GPUTexture;
  /** The texture for `key`, or undefined if nothing is allocated under it. */
  peek(key: string): GPUTexture | undefined;
  release(key: string): void;
  /** Bump the size epoch. Nothing is destroyed until the next `acquire` or `sweep`. */
  bumpSizeEpoch(): number;
  /** Destroy everything allocated under an older epoch. */
  sweep(): number;
  /** Destroy everything. Used by device-loss teardown and by `destroy`. */
  clear(): void;
}

const sameShape = (a: TextureRequest, b: TextureRequest): boolean =>
  a.width === b.width &&
  a.height === b.height &&
  a.format === b.format &&
  a.usage === b.usage &&
  (a.mipLevelCount ?? 1) === (b.mipLevelCount ?? 1);

export function createTexturePool(allocator: TextureAllocator): TexturePool {
  const entries = new Map<string, PoolEntry>();
  let epoch = 0;
  let created = 0;
  let destroyed = 0;
  let reused = 0;

  const destroy = (entry: PoolEntry): void => {
    entry.texture.destroy();
    destroyed += 1;
  };

  return {
    get sizeEpoch() {
      return epoch;
    },

    get stats() {
      return { live: entries.size, created, destroyed, reused, epoch };
    },

    acquire(key, request) {
      const existing = entries.get(key);
      if (existing !== undefined) {
        if (existing.epoch === epoch && sameShape(existing.request, request)) {
          reused += 1;
          return existing.texture;
        }
        destroy(existing);
      }

      const texture = allocator.createTexture({
        size: {
          width: Math.max(1, Math.floor(request.width)),
          height: Math.max(1, Math.floor(request.height)),
          depthOrArrayLayers: 1,
        },
        format: request.format,
        usage: request.usage,
        mipLevelCount: request.mipLevelCount ?? 1,
        ...(request.label === undefined ? {} : { label: request.label }),
      });
      created += 1;
      entries.set(key, { texture, request, epoch });
      return texture;
    },

    peek(key) {
      return entries.get(key)?.texture;
    },

    release(key) {
      const entry = entries.get(key);
      if (entry === undefined) return;
      destroy(entry);
      entries.delete(key);
    },

    bumpSizeEpoch() {
      epoch += 1;
      return epoch;
    },

    sweep() {
      let swept = 0;
      for (const [key, entry] of [...entries]) {
        if (entry.epoch === epoch) continue;
        destroy(entry);
        entries.delete(key);
        swept += 1;
      }
      return swept;
    },

    clear() {
      for (const entry of entries.values()) destroy(entry);
      entries.clear();
    },
  };
}

/** Pool keys, in one place so a typo is a compile error rather than a leak. */
export const poolKey = {
  backdropLevel0: (sourceId: string): string => `backdrop:${sourceId}:level0`,
  backdropChain: (sourceId: string): string => `backdrop:${sourceId}:chain`,
  backdropChainScratch: (sourceId: string, level: number): string =>
    `backdrop:${sourceId}:chain-scratch:${level}`,
  backdropBody: (sourceId: string): string => `backdrop:${sourceId}:body`,
  backdropBodyScratch: (sourceId: string): string => `backdrop:${sourceId}:body-scratch`,
  /** The heavy blur and its scratch (W26) — the body's pair, one width deeper. */
  backdropHeavy: (sourceId: string): string => `backdrop:${sourceId}:heavy`,
  backdropHeavyScratch: (sourceId: string): string => `backdrop:${sourceId}:heavy-scratch`,
  backdropUpload: (sourceId: string): string => `backdrop:${sourceId}:upload`,
  /*
   * The four field targets. Their key is a group's RESOURCE identity — the id
   * qualified by the plane it draws on (`groupResourceId`) — and not the group
   * id, because one group can draw on two planes in one frame and each plane's
   * field is its own size.
   */
  groupField: (resourceId: string): string => `group:${resourceId}:field`,
  groupAux: (resourceId: string): string => `group:${resourceId}:aux`,
  groupAux2: (resourceId: string): string => `group:${resourceId}:aux2`,
  /** The surface's presence per pixel (W27d) — the field pass's fourth target. */
  groupPresence: (resourceId: string): string => `group:${resourceId}:presence`,
} as const;
