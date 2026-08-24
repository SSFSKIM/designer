/**
 * X3 — the BackdropFrame protocol, and the five providers.
 *
 * Three things are being asserted, and only one of them needs a GPU (so it is not
 * here):
 *
 *  1. **Validation happens at registration.** X3: app-supplied views "must satisfy
 *     declared usage/format/dimension requirements — validated at registration
 *     with a typed error, never discovered at draw time." Every one of those
 *     checks reads only the texture's own declared properties, so all of them run
 *     without an adapter.
 *  2. **The alpha and re-acquisition rules are per kind, and they are WebGPU
 *     semantics rather than choices.** Imported video is unpremultiplied and
 *     expires at task end; copied images are premultiplied and only re-copied when
 *     dirty.
 *  3. **`VideoFrame` close ownership sits with the provider** — and only for the
 *     frames it was actually given ownership of.
 */

import { describe, expect, it, vi } from "vitest";

import {
  createAppTextureProvider,
  createCopyProvider,
  createGradientProvider,
  createVideoProvider,
  linearGradientStops,
  SUPPORTED_APP_TEXTURE_FORMATS,
  validateAppTexture,
  type BackdropDevice,
} from "../src/backdrop";
import { RendererError } from "../src/errors";

const USAGE = { TEXTURE_BINDING: 0x04, COPY_DST: 0x02, RENDER_ATTACHMENT: 0x10 };

interface FakeDeviceState {
  readonly device: BackdropDevice;
  readonly copies: unknown[];
  readonly writes: unknown[];
  readonly imports: unknown[];
  readonly textures: GPUTextureDescriptor[];
}

function fakeDevice(maxTextureDimension2D = 8192): FakeDeviceState {
  const copies: unknown[] = [];
  const writes: unknown[] = [];
  const imports: unknown[] = [];
  const textures: GPUTextureDescriptor[] = [];

  const device = {
    limits: { maxTextureDimension2D } as GPUSupportedLimits,
    queue: {
      copyExternalImageToTexture: (source: unknown, destination: unknown, size: unknown) =>
        copies.push({ source, destination, size }),
      writeTexture: (destination: unknown, data: unknown) => writes.push({ destination, data }),
    } as unknown as GPUQueue,
    createTexture: (descriptor: GPUTextureDescriptor) => {
      textures.push(descriptor);
      const size = descriptor.size as GPUExtent3DDict;
      return {
        width: size.width,
        height: size.height,
        createView: () => ({}) as GPUTextureView,
        destroy: () => undefined,
      } as unknown as GPUTexture;
    },
    importExternalTexture: (descriptor: GPUExternalTextureDescriptor) => {
      imports.push(descriptor);
      return {} as GPUExternalTexture;
    },
  } satisfies BackdropDevice;

  return { device, copies, writes, imports, textures };
}

const appTexture = (over: Partial<GPUTexture> = {}) =>
  ({
    width: 512,
    height: 256,
    format: "rgba8unorm",
    usage: USAGE.TEXTURE_BINDING,
    dimension: "2d",
    depthOrArrayLayers: 1,
    createView: () => ({}) as GPUTextureView,
    ...over,
  }) as unknown as GPUTexture;

describe("app-supplied textures are validated at registration", () => {
  const limits = { maxTextureDimension2D: 8192 } as GPUSupportedLimits;

  const expectCode = (fn: () => void, code: string): void => {
    expect(fn).toThrowError(RendererError);
    try {
      fn();
    } catch (error) {
      expect((error as RendererError).code).toBe(code);
      expect((error as RendererError).subject).toBe("bg");
    }
  };

  it("accepts a conforming texture", () => {
    expect(() => validateAppTexture(appTexture(), limits, "bg")).not.toThrow();
  });

  it("refuses a texture without TEXTURE_BINDING, and says what to add", () => {
    expectCode(() => validateAppTexture(appTexture({ usage: USAGE.COPY_DST }), limits, "bg"), "texture-usage");
    try {
      validateAppTexture(appTexture({ usage: USAGE.COPY_DST }), limits, "bg");
    } catch (error) {
      expect((error as RendererError).message).toContain("TEXTURE_BINDING");
    }
  });

  it("refuses an unsupported format and lists the supported ones", () => {
    expectCode(
      () => validateAppTexture(appTexture({ format: "r8unorm" }), limits, "bg"),
      "texture-format",
    );
    try {
      validateAppTexture(appTexture({ format: "r8unorm" }), limits, "bg");
    } catch (error) {
      expect((error as RendererError).message).toContain(SUPPORTED_APP_TEXTURE_FORMATS[0] as string);
    }
  });

  it("refuses a 3d texture and a multi-layer one", () => {
    expectCode(
      () => validateAppTexture(appTexture({ dimension: "3d" }), limits, "bg"),
      "texture-dimension",
    );
    expectCode(
      () => validateAppTexture(appTexture({ depthOrArrayLayers: 6 }), limits, "bg"),
      "texture-dimension",
    );
  });

  it("refuses a zero extent and one past the adapter's limit", () => {
    expectCode(() => validateAppTexture(appTexture({ width: 0 }), limits, "bg"), "texture-size");
    expectCode(
      () => validateAppTexture(appTexture({ width: 16384 }), limits, "bg"),
      "texture-size",
    );
  });

  it("throws when the provider is CREATED, not when a pass first binds it", () => {
    // The whole sentence in X3: never discovered at draw time.
    const { device } = fakeDevice();
    expect(() =>
      createAppTextureProvider({ id: "bg", device, texture: appTexture({ format: "r8unorm" }) }),
    ).toThrowError(RendererError);
  });

  it("reports a float texture as linear and an 8-bit one as encoded", () => {
    const { device } = fakeDevice();
    const float = createAppTextureProvider({
      id: "bg",
      device,
      texture: appTexture({ format: "rgba16float" }),
    });
    const bytes = createAppTextureProvider({ id: "bg2", device, texture: appTexture() });

    expect(float.acquire({ id: 0, timeMs: 0 }).encoded).toBe(false);
    expect(bytes.acquire({ id: 0, timeMs: 0 }).encoded).toBe(true);
  });

  it("never destroys a texture it was only lent", () => {
    const destroy = vi.fn();
    const { device } = fakeDevice();
    const provider = createAppTextureProvider({
      id: "bg",
      device,
      texture: appTexture({ destroy } as Partial<GPUTexture>),
    });
    provider.destroy();
    expect(destroy).not.toHaveBeenCalled();
  });
});

describe("image and canvas providers", () => {
  const source = {} as ImageBitmap;

  it("declares a premultiplied destination, which is what X3 promises", () => {
    const { device, copies } = fakeDevice();
    const provider = createCopyProvider({
      id: "img",
      kind: "image",
      device,
      source,
      width: 64,
      height: 32,
    });

    const frame = provider.acquire({ id: 1, timeMs: 0 });

    expect(frame.alphaMode).toBe("premultiplied");
    expect(frame.encoded).toBe(true);
    expect(frame.binding.kind).toBe("sampled");
    expect(copies).toHaveLength(1);
    expect((copies[0] as { destination: { premultipliedAlpha: boolean } }).destination.premultipliedAlpha).toBe(true);
  });

  it("stops copying a static image once it has been imported", () => {
    // §Core model: "Static backdrops rebuild nothing."
    const { device, copies } = fakeDevice();
    const provider = createCopyProvider({
      id: "img",
      kind: "image",
      device,
      source,
      width: 64,
      height: 32,
    });

    provider.acquire({ id: 1, timeMs: 0 });
    provider.markImported();
    expect(provider.isDirty()).toBe(false);

    provider.acquire({ id: 2, timeMs: 16 });
    expect(copies).toHaveLength(1);
  });

  it("keeps a live canvas dirty every frame", () => {
    const { device, copies } = fakeDevice();
    const provider = createCopyProvider({
      id: "cv",
      kind: "canvas",
      device,
      source: {} as HTMLCanvasElement,
      width: 32,
      height: 32,
    });

    provider.acquire({ id: 1, timeMs: 0 });
    provider.markImported();
    expect(provider.isDirty()).toBe(true);
    provider.acquire({ id: 2, timeMs: 16 });
    expect(copies).toHaveLength(2);
  });

  it("bumps the size epoch on a resize, which invalidates the pyramid", () => {
    const { device } = fakeDevice();
    const provider = createCopyProvider({
      id: "img",
      kind: "image",
      device,
      source,
      width: 64,
      height: 32,
    });

    const before = provider.acquire({ id: 1, timeMs: 0 }).sizeEpoch;
    provider.markImported();
    expect(provider.isDirty()).toBe(false);

    provider.resize?.(128, 64);
    // A resize is also a content change: the new extent has never been copied.
    expect(provider.isDirty()).toBe(true);

    const after = provider.acquire({ id: 2, timeMs: 16 });
    expect(after.sizeEpoch).toBeGreaterThan(before);
    expect(after.width).toBe(128);
  });

  it("refuses to acquire a zero-extent source", () => {
    const { device } = fakeDevice();
    const provider = createCopyProvider({
      id: "img",
      kind: "image",
      device,
      source,
      width: 0,
      height: 0,
    });
    expect(() => provider.acquire({ id: 1, timeMs: 0 })).toThrowError(/zero extent/);
  });
});

describe("the video provider", () => {
  const videoElement = (over: Partial<HTMLVideoElement> = {}) =>
    ({ readyState: 4, videoWidth: 640, videoHeight: 360, ...over }) as HTMLVideoElement;

  /** A live element whose extent can change between frames, as a real one does. */
  const resizableVideoElement = (): { element: HTMLVideoElement; setWidth: (w: number) => void } => {
    let width = 640;
    const element = { readyState: 4, videoHeight: 360 } as HTMLVideoElement;
    Object.defineProperty(element, "videoWidth", { get: () => width });
    return { element, setWidth: (w) => (width = w) };
  };

  it("is always dirty, because importExternalTexture expires at task end", () => {
    const { device } = fakeDevice();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "element", element: videoElement() },
    });

    expect(provider.isDirty()).toBe(true);
    provider.acquire({ id: 1, timeMs: 0 });
    provider.markImported();
    provider.release();
    expect(provider.isDirty()).toBe(true);
  });

  it("reports unpremultiplied alpha and an external binding", () => {
    const { device, imports } = fakeDevice();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "element", element: videoElement() },
    });

    const frame = provider.acquire({ id: 1, timeMs: 0 });

    expect(frame.alphaMode).toBe("unpremultiplied");
    expect(frame.binding.kind).toBe("external");
    expect(frame.width).toBe(640);
    expect(imports).toHaveLength(1);
  });

  it("refuses a video with no decoded frame yet, and says what to wait for", () => {
    const { device } = fakeDevice();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "element", element: videoElement({ readyState: 0, videoWidth: 0 }) },
    });
    expect(() => provider.acquire({ id: 1, timeMs: 0 })).toThrowError(/loadeddata/);
  });

  it("refuses a second acquire without a release", () => {
    const { device } = fakeDevice();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "element", element: videoElement() },
    });

    provider.acquire({ id: 1, timeMs: 0 });
    expect(() => provider.acquire({ id: 1, timeMs: 0 })).toThrowError(RendererError);
    try {
      provider.acquire({ id: 1, timeMs: 0 });
    } catch (error) {
      expect((error as RendererError).code).toBe("frame-protocol");
    }
  });

  it("closes a VideoFrame it owns, on release and not before", () => {
    // X3: "VideoFrame close ownership held by the provider." Closing before submit
    // would pull the texture out from under the pass that samples it.
    const { device } = fakeDevice();
    const close = vi.fn();
    const frame = { displayWidth: 320, displayHeight: 180, close } as unknown as VideoFrame;
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "frames", next: () => frame },
    });

    provider.acquire({ id: 1, timeMs: 0 });
    expect(close).not.toHaveBeenCalled();
    provider.release();
    expect(close).toHaveBeenCalledTimes(1);
  });

  it("closes nothing when the browser owns the frames", () => {
    const { device } = fakeDevice();
    const element = videoElement();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "element", element },
    });

    provider.acquire({ id: 1, timeMs: 0 });
    expect(() => provider.release()).not.toThrow();
  });

  it("closes an outstanding owned frame on destroy, so a decoder cannot stall", () => {
    const { device } = fakeDevice();
    const close = vi.fn();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: {
        kind: "frames",
        next: () => ({ displayWidth: 8, displayHeight: 8, close }) as unknown as VideoFrame,
      },
    });

    provider.acquire({ id: 1, timeMs: 0 });
    provider.destroy();
    expect(close).toHaveBeenCalledTimes(1);
  });

  it("bumps the size epoch when the video's own extent changes", () => {
    const { device } = fakeDevice();
    const live = resizableVideoElement();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "element", element: live.element },
    });

    const first = provider.acquire({ id: 1, timeMs: 0 }).sizeEpoch;
    provider.release();
    live.setWidth(1280);
    const second = provider.acquire({ id: 2, timeMs: 16 }).sizeEpoch;

    expect(second).toBeGreaterThan(first);
  });

  it("refuses when the frame source runs dry", () => {
    const { device } = fakeDevice();
    const provider = createVideoProvider({
      id: "vid",
      device,
      source: { kind: "frames", next: () => undefined },
    });
    expect(() => provider.acquire({ id: 1, timeMs: 0 })).toThrowError(/no VideoFrame/);
  });
});

describe("the procedural gradient provider", () => {
  it("uploads once and then rebuilds nothing", () => {
    const { device, writes } = fakeDevice();
    const provider = createGradientProvider({
      id: "grad",
      device,
      stops: linearGradientStops([0, 0, 0], [1, 1, 1]),
    });

    expect(provider.isDirty()).toBe(true);
    provider.acquire({ id: 1, timeMs: 0 });
    provider.markImported();
    expect(provider.isDirty()).toBe(false);

    provider.acquire({ id: 2, timeMs: 16 });
    expect(writes).toHaveLength(1);
  });

  it("interpolates in linear light, so the middle is not a dark band", () => {
    const { device, writes } = fakeDevice();
    createGradientProvider({
      id: "grad",
      device,
      stops: linearGradientStops([0, 0, 0], [1, 1, 1]),
      width: 1,
      height: 3,
    }).acquire({ id: 1, timeMs: 0 });

    const data = (writes[0] as { data: Uint8Array }).data;
    // Linear 0.5 encodes to ~0.7354 → 188, not to 128.
    expect(data[4]).toBeGreaterThan(180);
    expect(data[4]).toBeLessThan(196);
  });

  it("refuses a gradient with no stops", () => {
    const { device } = fakeDevice();
    expect(() => createGradientProvider({ id: "grad", device, stops: [] })).toThrowError(
      RendererError,
    );
  });

  it("reports premultiplied opaque texels", () => {
    const { device } = fakeDevice();
    const frame = createGradientProvider({
      id: "grad",
      device,
      stops: linearGradientStops([0, 0, 0], [1, 1, 1]),
    }).acquire({ id: 1, timeMs: 0 });

    expect(frame.alphaMode).toBe("premultiplied");
    expect(frame.sizeEpoch).toBe(0);
  });
});
