/**
 * A `GPUDevice` stand-in wide enough to drive a whole frame.
 *
 * Most of this package's resource discipline is already testable without one —
 * the pool, the caches and the ledger are written over narrow allocator slices
 * for exactly that reason. What is *not*, and what several of the failures worth
 * regression-testing live in, is the composition: which texture the pyramid binds
 * after a resize, whether a provider is re-pointed when the device generation
 * moves, what is released when the encode throws. Those are properties of
 * `renderer.ts` driving `passes.ts` and `pyramid.ts` together, and they need a
 * device-shaped object rather than a mock of one method.
 *
 * So this records rather than asserts. It hands out real object identities
 * (textures, buffers, bind groups) so a test can ask "is the texture bound this
 * frame the one that was destroyed", and it keeps a log of submits, bind-group
 * entries and destroyed handles. It validates nothing: a real adapter is what
 * says whether the WGSL compiles and whether a binding is legal, and `e2e/gpu/`
 * is where that question is asked.
 */

export interface FakeTexture {
  readonly id: number;
  readonly label: string;
  readonly width: number;
  readonly height: number;
  destroyed: boolean;
}

export interface FakeBuffer {
  readonly id: number;
  readonly label: string;
  destroyed: boolean;
}

export interface FakeBindGroup {
  readonly entries: readonly GPUBindGroupEntry[];
}

export interface FakePass {
  readonly label: string;
  readonly kind: "render" | "compute";
  readonly bindGroups: FakeBindGroup[];
}

export interface FakeGpu {
  readonly device: GPUDevice;
  /** Every texture ever created, in creation order. */
  readonly textures: FakeTexture[];
  readonly buffers: FakeBuffer[];
  /** Passes encoded since the last `reset()`. */
  readonly passes: FakePass[];
  readonly submits: number;
  /** Resolve the device's `lost` promise, the way a real loss does. */
  lose(reason?: GPUDeviceLostReason): void;
  /** Make the next `createCommandEncoder().finish()` throw, once. */
  failNextFinish(message?: string): void;
  /** Clear the per-frame log. Totals (`textures`, `buffers`) are cumulative. */
  reset(): void;
  /** The recorded fake behind a `GPUTexture` handle, if it came from here. */
  info(texture: GPUTexture): FakeTexture | undefined;
}

export function createFakeGpu(): FakeGpu {
  const textures: FakeTexture[] = [];
  const buffers: FakeBuffer[] = [];
  const passes: FakePass[] = [];
  const backing = new WeakMap<object, FakeTexture>();
  let submits = 0;
  let failFinish: string | undefined;
  let resolveLost: (info: GPUDeviceLostInfo) => void = () => undefined;
  const lost = new Promise<GPUDeviceLostInfo>((resolve) => {
    resolveLost = resolve;
  });

  const makeTexture = (descriptor: GPUTextureDescriptor): GPUTexture => {
    const size = descriptor.size as GPUExtent3DDict;
    const record: FakeTexture = {
      id: textures.length,
      label: descriptor.label ?? "",
      width: size.width,
      height: size.height ?? 1,
      destroyed: false,
    };
    textures.push(record);
    const handle = {
      width: record.width,
      height: record.height,
      format: descriptor.format,
      usage: descriptor.usage,
      dimension: "2d",
      depthOrArrayLayers: 1,
      createView: () => ({ __texture: handle }) as unknown as GPUTextureView,
      destroy: () => {
        record.destroyed = true;
      },
    };
    backing.set(handle, record);
    return handle as unknown as GPUTexture;
  };

  const makeBuffer = (descriptor: GPUBufferDescriptor): GPUBuffer => {
    const record: FakeBuffer = {
      id: buffers.length,
      label: descriptor.label ?? "",
      destroyed: false,
    };
    buffers.push(record);
    const bytes = new ArrayBuffer(Number(descriptor.size));
    return {
      // On the handle as well as the record, the way a real `GPUBuffer` carries
      // it: a test intercepting `queue.writeBuffer` sees only the handle.
      label: record.label,
      size: descriptor.size,
      mapAsync: async () => undefined,
      getMappedRange: () => bytes,
      unmap: () => undefined,
      destroy: () => {
        record.destroyed = true;
      },
    } as unknown as GPUBuffer;
  };

  const makePass = (label: string, kind: "render" | "compute"): FakePass => {
    const pass: FakePass = { label, kind, bindGroups: [] };
    passes.push(pass);
    return pass;
  };

  const passEncoder = (pass: FakePass): Record<string, unknown> => ({
    setPipeline: () => undefined,
    setBindGroup: (_index: number, group: FakeBindGroup) => pass.bindGroups.push(group),
    setViewport: () => undefined,
    setScissorRect: () => undefined,
    draw: () => undefined,
    dispatchWorkgroups: () => undefined,
    end: () => undefined,
  });

  const device = {
    lost,
    limits: { maxTextureDimension2D: 8192 } as GPUSupportedLimits,
    features: new Set<string>(),
    queue: {
      submit: () => {
        submits += 1;
      },
      writeBuffer: () => undefined,
      writeTexture: () => undefined,
      copyExternalImageToTexture: () => undefined,
      onSubmittedWorkDone: async () => undefined,
    },
    createTexture: makeTexture,
    createBuffer: makeBuffer,
    createSampler: (descriptor: GPUSamplerDescriptor = {}) =>
      ({ label: descriptor.label }) as unknown as GPUSampler,
    createShaderModule: (descriptor: GPUShaderModuleDescriptor) =>
      ({ label: descriptor.label }) as unknown as GPUShaderModule,
    createRenderPipeline: (descriptor: GPURenderPipelineDescriptor) =>
      ({
        label: descriptor.label,
        getBindGroupLayout: () => ({}) as GPUBindGroupLayout,
      }) as unknown as GPURenderPipeline,
    createComputePipeline: (descriptor: GPUComputePipelineDescriptor) =>
      ({
        label: descriptor.label,
        getBindGroupLayout: () => ({}) as GPUBindGroupLayout,
      }) as unknown as GPUComputePipeline,
    createBindGroup: (descriptor: GPUBindGroupDescriptor) =>
      ({ entries: [...descriptor.entries] }) as unknown as GPUBindGroup,
    importExternalTexture: () => ({}) as GPUExternalTexture,
    createCommandEncoder: () => ({
      beginRenderPass: (descriptor: GPURenderPassDescriptor) =>
        passEncoder(makePass(descriptor.label ?? "", "render")),
      beginComputePass: (descriptor: GPUComputePassDescriptor = {}) =>
        passEncoder(makePass(descriptor.label ?? "", "compute")),
      copyBufferToBuffer: () => undefined,
      finish: () => {
        if (failFinish !== undefined) {
          const message = failFinish;
          failFinish = undefined;
          throw new Error(message);
        }
        return {} as GPUCommandBuffer;
      },
    }),
    destroy: () => undefined,
  };

  return {
    device: device as unknown as GPUDevice,
    textures,
    buffers,
    passes,
    get submits() {
      return submits;
    },
    lose(reason = "unknown") {
      resolveLost({ reason, message: "test" } as GPUDeviceLostInfo);
    },
    failNextFinish(message = "encode failed") {
      failFinish = message;
    },
    reset() {
      passes.length = 0;
    },
    info(texture) {
      return backing.get(texture as unknown as object);
    },
  };
}

/** The texture a view was created from, for a view this harness handed out. */
export function viewOwner(view: GPUTextureView): GPUTexture {
  return (view as unknown as { __texture: GPUTexture }).__texture;
}

/** Microtask flush, for the device host's loss handling. */
export const flush = async (): Promise<void> => {
  for (let i = 0; i < 4; i += 1) await Promise.resolve();
};
