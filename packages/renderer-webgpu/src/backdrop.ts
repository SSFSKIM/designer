/**
 * X3 — the BackdropFrame acquisition protocol, and a provider for every source
 * kind §Backdrop contracts names.
 *
 * The spec calls this contract "operational, not aspirational", and the reason is
 * a hard WebGPU fact: **there is no cross-device texture sharing.** So every
 * source, however it arrives, is normalised through one protocol —
 * `acquire(frame)` at frame start, `release()` after submit — and the frame
 * carries the four things a consumer cannot infer: the binding, the size epoch,
 * the colour space, and the alpha mode.
 *
 * ## The five kinds, and what is actually different about each
 *
 * | kind | mechanism | alpha | re-acquired |
 * | --- | --- | --- | --- |
 * | `image` | `copyExternalImageToTexture` | premultiplied | only when dirty |
 * | `video` | `importExternalTexture` | **unpremultiplied** | **every sampling frame** |
 * | `canvas` | `copyExternalImageToTexture` | premultiplied | every frame by default |
 * | `gradient` | `queue.writeTexture` of CPU-generated texels | opaque | never |
 * | `app-texture-view` | the app's own `GPUTexture` | declared by the app | every frame |
 *
 * Two of those cells are WebGPU semantics rather than choices, and §Surprises
 * records them as such: `importExternalTexture` handles **expire at task end**, so
 * a video must be re-imported on every frame that samples it; and imported video
 * arrives **unpremultiplied** while copied images arrive premultiplied. The import
 * pass normalises both to premultiplied linear, so nothing downstream branches on
 * either fact.
 *
 * ## VideoFrame ownership
 *
 * X3: "`VideoFrame` close ownership held by the provider." When the app hands in a
 * `VideoFrame`, this provider closes it in `release()` — after submit, because an
 * imported external texture must outlive the submission that samples it. When the
 * app hands in an `HTMLVideoElement` the browser owns the frames and the provider
 * closes nothing. Getting that backwards leaks decoder buffers until playback
 * stalls, which is why the two cases are separate provider inputs rather than one
 * permissive union.
 *
 * ## Validation at registration
 *
 * Also X3: app-supplied views "must satisfy declared usage/format/dimension
 * requirements — validated at registration with a typed error, never discovered at
 * draw time." `registerAppTexture` therefore takes the `GPUTexture`, not just a
 * view: a `GPUTextureView` exposes none of its own properties, so a contract that
 * accepted only a view could not be checked at all.
 */

import {
  type BackdropAlphaMode,
  type BackdropColorSpace,
  linearToSrgbChannel,
  srgbToLinearChannel,
} from "./color";
import { rendererError } from "./errors";

export const BACKDROP_KINDS = [
  "image",
  "video",
  "canvas",
  "gradient",
  "app-texture-view",
] as const;

export type BackdropKind = (typeof BACKDROP_KINDS)[number];

/** How the import pass binds the source. `external` needs its own pipeline. */
export type BackdropBinding =
  | { readonly kind: "sampled"; readonly view: GPUTextureView }
  | { readonly kind: "external"; readonly texture: GPUExternalTexture };

export interface BackdropFrame {
  readonly sourceId: string;
  readonly binding: BackdropBinding;
  /** Source extent in texture px. */
  readonly width: number;
  readonly height: number;
  /** Bumped when the extent changes; invalidates every dependent allocation. */
  readonly sizeEpoch: number;
  readonly colorSpace: BackdropColorSpace;
  readonly alphaMode: BackdropAlphaMode;
  /** True when the sampled values are sRGB-encoded rather than linear. */
  readonly encoded: boolean;
}

/** The frame facts a provider is handed. Matches core's `FrameInfo`. */
export interface FrameInfoView {
  readonly id: number;
  readonly timeMs: number;
}

export interface BackdropProvider {
  readonly id: string;
  readonly kind: BackdropKind;
  /** True when content may have changed since the last successful import. */
  isDirty(): boolean;
  /** X3: at frame start. Throws `source-unavailable` if the source cannot serve. */
  acquire(frame: FrameInfoView): BackdropFrame;
  /** X3: after submit. Releases whatever the acquire took ownership of. */
  release(): void;
  /** Called once the import pass has consumed the frame's pixels. */
  markImported(): void;
  /**
   * Re-declare the source's extent. Implemented where the renderer allocates the
   * storage (image, canvas); absent where the source declares its own size.
   */
  resize?(width: number, height: number): void;
  destroy(): void;
}

/** Formats the sampling path can read. Everything else is refused at registration. */
export const SUPPORTED_APP_TEXTURE_FORMATS: readonly GPUTextureFormat[] = [
  "rgba8unorm",
  "rgba8unorm-srgb",
  "bgra8unorm",
  "bgra8unorm-srgb",
  "rgba16float",
  "rgba32float",
];

/** The slice of `GPUDevice` the providers need. `GPUDevice` satisfies it as-is. */
export interface BackdropDevice {
  readonly queue: GPUQueue;
  readonly limits: GPUSupportedLimits;
  createTexture(descriptor: GPUTextureDescriptor): GPUTexture;
  importExternalTexture(descriptor: GPUExternalTextureDescriptor): GPUExternalTexture;
}

const COPY_USAGE =
  GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST | GPUTextureUsage.RENDER_ATTACHMENT;

interface SizeTracker {
  epoch: number;
  width: number;
  height: number;
}

function trackSize(tracker: SizeTracker, width: number, height: number): void {
  if (tracker.width === width && tracker.height === height) return;
  tracker.width = width;
  tracker.height = height;
  tracker.epoch += 1;
}

// ---------------------------------------------------------------------------
// image and canvas — copyExternalImageToTexture
// ---------------------------------------------------------------------------

/** Anything `copyExternalImageToTexture` accepts as a source. */
export type CopyableSource =
  | ImageBitmap
  | HTMLImageElement
  | HTMLCanvasElement
  | OffscreenCanvas
  | ImageData
  | VideoFrame;

export interface CopyProviderOptions {
  readonly id: string;
  readonly kind: "image" | "canvas";
  readonly device: BackdropDevice;
  readonly source: CopyableSource;
  readonly width: number;
  readonly height: number;
  readonly colorSpace?: BackdropColorSpace;
  /**
   * Whether content changes every frame. `true` for a live canvas, `false` for a
   * decoded image — which is what makes a static backdrop rebuild nothing at all
   * (§Core model invariant).
   */
  readonly live?: boolean;
}

export function createCopyProvider(options: CopyProviderOptions): BackdropProvider {
  const { device } = options;
  const size = { epoch: 0, width: options.width, height: options.height };
  const live = options.live ?? options.kind === "canvas";
  let dirty = true;
  let texture: GPUTexture | undefined;

  const ensureTexture = (): GPUTexture => {
    if (texture !== undefined && texture.width === size.width && texture.height === size.height) {
      return texture;
    }
    texture?.destroy();
    texture = device.createTexture({
      label: `vitrea:backdrop:${options.id}:upload`,
      size: { width: size.width, height: size.height, depthOrArrayLayers: 1 },
      // 8-bit is the honest storage for an image or a canvas: both are 8-bit
      // sources, and the import pass promotes to float on the way into level 0.
      format: "rgba8unorm",
      usage: COPY_USAGE,
    });
    return texture;
  };

  return {
    id: options.id,
    kind: options.kind,

    isDirty() {
      return dirty || live;
    },

    acquire() {
      if (size.width <= 0 || size.height <= 0) {
        throw rendererError(
          "source-unavailable",
          `Backdrop "${options.id}" has a zero extent (${size.width}×${size.height}); nothing can be copied from it.`,
          options.id,
        );
      }
      const target = ensureTexture();
      if (dirty || live) {
        device.queue.copyExternalImageToTexture(
          { source: options.source, flipY: false },
          {
            texture: target,
            colorSpace: options.colorSpace ?? "srgb",
            // X3: copied images arrive premultiplied. Declaring it here is what
            // makes that true rather than assumed — the copy performs the multiply
            // when the source is not already premultiplied.
            premultipliedAlpha: true,
          },
          { width: size.width, height: size.height },
        );
      }
      return {
        sourceId: options.id,
        binding: { kind: "sampled", view: target.createView() },
        width: size.width,
        height: size.height,
        sizeEpoch: size.epoch,
        colorSpace: options.colorSpace ?? "srgb",
        alphaMode: "premultiplied",
        encoded: true,
      };
    },

    release() {
      // Nothing to release: the destination texture is this provider's own and
      // outlives the frame.
    },

    markImported() {
      dirty = false;
    },

    resize(width, height) {
      const changed = size.width !== width || size.height !== height;
      trackSize(size, width, height);
      if (changed) dirty = true;
    },

    destroy() {
      texture?.destroy();
      texture = undefined;
    },
  };
}

// ---------------------------------------------------------------------------
// video — importExternalTexture
// ---------------------------------------------------------------------------

export interface VideoProviderOptions {
  readonly id: string;
  readonly device: BackdropDevice;
  /**
   * Either a live element the browser keeps frames for, or a callback producing a
   * `VideoFrame` this provider then owns and closes. The two are separate because
   * their ownership rules are opposite — see the module note.
   */
  readonly source:
    | { readonly kind: "element"; readonly element: HTMLVideoElement }
    | { readonly kind: "frames"; readonly next: () => VideoFrame | undefined };
  readonly colorSpace?: BackdropColorSpace;
}

export function createVideoProvider(options: VideoProviderOptions): BackdropProvider {
  const { device } = options;
  const size = { epoch: 0, width: 0, height: 0 };
  let ownedFrame: VideoFrame | undefined;
  let acquired = false;

  return {
    id: options.id,
    kind: "video",

    isDirty() {
      // `importExternalTexture` handles expire at task end, so a video is dirty
      // on every frame that samples it. That is a WebGPU semantic, not a policy.
      return true;
    },

    acquire() {
      if (acquired) {
        throw rendererError(
          "frame-protocol",
          `Backdrop "${options.id}" was acquired twice without a release. X3 pairs one acquire per frame with one release after submit.`,
          options.id,
        );
      }

      let source: HTMLVideoElement | VideoFrame;
      if (options.source.kind === "element") {
        const element = options.source.element;
        if (element.readyState < 2 || element.videoWidth === 0) {
          throw rendererError(
            "source-unavailable",
            `Backdrop "${options.id}" is a video with no decoded frame yet (readyState ${element.readyState}). Wait for "loadeddata" before registering it, or let the group render without a backdrop until it arrives.`,
            options.id,
          );
        }
        trackSize(size, element.videoWidth, element.videoHeight);
        source = element;
      } else {
        const frame = options.source.next();
        if (frame === undefined) {
          throw rendererError(
            "source-unavailable",
            `Backdrop "${options.id}" produced no VideoFrame for this frame.`,
            options.id,
          );
        }
        ownedFrame = frame;
        trackSize(size, frame.displayWidth, frame.displayHeight);
        source = frame;
      }

      const texture = device.importExternalTexture({
        label: `vitrea:backdrop:${options.id}:external`,
        source,
        colorSpace: "srgb",
      });
      acquired = true;

      return {
        sourceId: options.id,
        binding: { kind: "external", texture },
        width: size.width,
        height: size.height,
        sizeEpoch: size.epoch,
        colorSpace: options.colorSpace ?? "srgb",
        // X3: imported video arrives UNPREMULTIPLIED.
        alphaMode: "unpremultiplied",
        encoded: true,
      };
    },

    release() {
      acquired = false;
      // After submit, and only for a frame this provider owns.
      ownedFrame?.close();
      ownedFrame = undefined;
    },

    markImported() {
      // A video is dirty again immediately; nothing to record.
    },

    destroy() {
      ownedFrame?.close();
      ownedFrame = undefined;
      acquired = false;
    },
  };
}

// ---------------------------------------------------------------------------
// gradient — procedural, generated once on the CPU
// ---------------------------------------------------------------------------

export interface GradientStop {
  /** 0..1 along the gradient axis. */
  readonly offset: number;
  /** sRGB-encoded 0..1, plus alpha. */
  readonly color: readonly [number, number, number, number];
}

export interface GradientProviderOptions {
  readonly id: string;
  readonly device: BackdropDevice;
  readonly stops: readonly GradientStop[];
  /** Gradient direction in the source's own uv space. Defaults to top-to-bottom. */
  readonly direction?: readonly [number, number];
  readonly width?: number;
  readonly height?: number;
}

/**
 * Generated on the CPU and uploaded once, rather than rendered with a pipeline of
 * its own.
 *
 * A procedural gradient is static by definition, so it rebuilds nothing after the
 * first frame and a whole render pipeline for it would be dead weight in the
 * pipeline cache. Interpolation is in **linear light** and the result is
 * re-encoded, because a gradient interpolated in sRGB has a visible dark band
 * through its middle — the one place where doing the maths in the wrong space is
 * obvious to the eye rather than to a metric.
 */
export function createGradientProvider(options: GradientProviderOptions): BackdropProvider {
  const width = Math.max(1, options.width ?? 64);
  const height = Math.max(1, options.height ?? 64);
  const direction = options.direction ?? [0, 1];
  const stops = [...options.stops].sort((a, b) => a.offset - b.offset);

  if (stops.length === 0) {
    throw rendererError(
      "source-unavailable",
      `Gradient backdrop "${options.id}" has no stops.`,
      options.id,
    );
  }

  const texels = new Uint8Array(width * height * 4);
  const axisLength = Math.hypot(direction[0], direction[1]) || 1;
  const ax = direction[0] / axisLength;
  const ay = direction[1] / axisLength;

  const sample = (t: number): readonly [number, number, number, number] => {
    const clamped = Math.min(1, Math.max(0, t));
    let lower = stops[0] as GradientStop;
    let upper = stops[stops.length - 1] as GradientStop;
    for (let i = 0; i < stops.length - 1; i += 1) {
      const a = stops[i] as GradientStop;
      const b = stops[i + 1] as GradientStop;
      if (clamped >= a.offset && clamped <= b.offset) {
        lower = a;
        upper = b;
        break;
      }
    }
    const span = upper.offset - lower.offset;
    const local = span <= 0 ? 0 : (clamped - lower.offset) / span;
    const mix = (from: number, to: number): number => from + (to - from) * local;
    // Colour channels are decoded, mixed, and re-encoded; alpha is already
    // linear and is mixed as-is. Mixing the encoded values instead puts a
    // visible dark band through the middle of every gradient — the one place
    // where working in the wrong space is obvious to the eye rather than to a
    // metric.
    const channel = (index: 0 | 1 | 2): number =>
      linearToSrgbChannel(
        mix(srgbToLinearChannel(lower.color[index]), srgbToLinearChannel(upper.color[index])),
      );
    return [channel(0), channel(1), channel(2), mix(lower.color[3], upper.color[3])];
  };

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const u = width === 1 ? 0 : x / (width - 1);
      const v = height === 1 ? 0 : y / (height - 1);
      // Project onto the axis and rescale so the endpoints of the projected
      // range land on stops 0 and 1 whatever the direction.
      const t = (u * ax + v * ay + Math.max(0, -ax) + Math.max(0, -ay)) / (Math.abs(ax) + Math.abs(ay) || 1);
      const [r, g, b, a] = sample(t);
      const index = (y * width + x) * 4;
      texels[index + 0] = Math.round(Math.min(1, Math.max(0, r)) * 255);
      texels[index + 1] = Math.round(Math.min(1, Math.max(0, g)) * 255);
      texels[index + 2] = Math.round(Math.min(1, Math.max(0, b)) * 255);
      texels[index + 3] = Math.round(Math.min(1, Math.max(0, a)) * 255);
    }
  }

  let texture: GPUTexture | undefined;
  let uploaded = false;

  return {
    id: options.id,
    kind: "gradient",

    isDirty() {
      return !uploaded;
    },

    acquire() {
      texture ??= options.device.createTexture({
        label: `vitrea:backdrop:${options.id}:gradient`,
        size: { width, height, depthOrArrayLayers: 1 },
        format: "rgba8unorm",
        usage: COPY_USAGE,
      });
      if (!uploaded) {
        options.device.queue.writeTexture(
          { texture },
          texels,
          { bytesPerRow: width * 4, rowsPerImage: height },
          { width, height },
        );
      }
      return {
        sourceId: options.id,
        binding: { kind: "sampled", view: texture.createView() },
        width,
        height,
        sizeEpoch: 0,
        colorSpace: "srgb",
        alphaMode: "premultiplied",
        encoded: true,
      };
    },

    release() {
      // Nothing acquired that needs releasing.
    },

    markImported() {
      uploaded = true;
    },

    destroy() {
      texture?.destroy();
      texture = undefined;
      uploaded = false;
    },
  };
}

/** Two-stop convenience, in linear light, for tests and for the golden scenes. */
export function linearGradientStops(
  from: readonly [number, number, number],
  to: readonly [number, number, number],
): readonly GradientStop[] {
  const encode = (c: readonly [number, number, number]): readonly [number, number, number, number] =>
    [linearToSrgbChannel(c[0]), linearToSrgbChannel(c[1]), linearToSrgbChannel(c[2]), 1];
  return [
    { offset: 0, color: encode(from) },
    { offset: 1, color: encode(to) },
  ];
}

// ---------------------------------------------------------------------------
// app-texture-view — validated at registration
// ---------------------------------------------------------------------------

export interface AppTextureProviderOptions {
  readonly id: string;
  readonly device: BackdropDevice;
  /**
   * The app's texture. Required rather than a bare view because a
   * `GPUTextureView` exposes none of its own properties, so a view-only contract
   * could not be validated at all — and X3 requires validation at registration.
   */
  readonly texture: GPUTexture;
  /** Optional pre-made view. One is created per acquire when absent. */
  readonly view?: GPUTextureView;
  readonly colorSpace?: BackdropColorSpace;
  readonly alphaMode?: BackdropAlphaMode;
  /** Whether the app's values are sRGB-encoded. A float target is usually linear. */
  readonly encoded?: boolean;
}

/**
 * Validate an app-supplied texture against the sampling path's requirements.
 *
 * Exported separately so a host can check before it registers, and so the checks
 * are testable without a device — every one of them reads only the texture's own
 * declared properties.
 */
export function validateAppTexture(
  texture: Pick<GPUTexture, "width" | "height" | "format" | "usage" | "dimension" | "depthOrArrayLayers">,
  limits: Pick<GPUSupportedLimits, "maxTextureDimension2D">,
  subject: string,
): void {
  if (texture.dimension !== "2d") {
    throw rendererError(
      "texture-dimension",
      `Backdrop "${subject}" supplied a ${texture.dimension} texture. The sampling path binds a 2d texture; register a 2d texture or a 2d view of one slice.`,
      subject,
    );
  }
  if (texture.depthOrArrayLayers !== 1) {
    throw rendererError(
      "texture-dimension",
      `Backdrop "${subject}" supplied a texture with ${texture.depthOrArrayLayers} array layers. Bind a single-layer view.`,
      subject,
    );
  }
  if ((texture.usage & GPUTextureUsage.TEXTURE_BINDING) === 0) {
    throw rendererError(
      "texture-usage",
      `Backdrop "${subject}" supplied a texture without GPUTextureUsage.TEXTURE_BINDING, so it cannot be sampled. Add TEXTURE_BINDING to the texture's usage when you create it.`,
      subject,
    );
  }
  if (!SUPPORTED_APP_TEXTURE_FORMATS.includes(texture.format)) {
    throw rendererError(
      "texture-format",
      `Backdrop "${subject}" supplied a "${texture.format}" texture. Supported formats are ${SUPPORTED_APP_TEXTURE_FORMATS.join(", ")}.`,
      subject,
    );
  }
  if (texture.width <= 0 || texture.height <= 0) {
    throw rendererError(
      "texture-size",
      `Backdrop "${subject}" supplied a ${texture.width}×${texture.height} texture.`,
      subject,
    );
  }
  const max = limits.maxTextureDimension2D;
  if (texture.width > max || texture.height > max) {
    throw rendererError(
      "texture-size",
      `Backdrop "${subject}" supplied a ${texture.width}×${texture.height} texture, past this adapter's maxTextureDimension2D of ${max}.`,
      subject,
    );
  }
}

export function createAppTextureProvider(options: AppTextureProviderOptions): BackdropProvider {
  // Registration-time validation. Throwing here — not at draw time — is the whole
  // point of X3's sentence about app-supplied views.
  validateAppTexture(options.texture, options.device.limits, options.id);

  const encoded = options.encoded ?? !options.texture.format.includes("float");
  const size = {
    epoch: 0,
    width: options.texture.width,
    height: options.texture.height,
  };

  return {
    id: options.id,
    kind: "app-texture-view",

    isDirty() {
      // The app may redraw into its own texture at any time and the renderer has
      // no way to know. Assuming dirty is the honest default; an app that knows
      // better re-registers with a static source.
      return true;
    },

    acquire() {
      return {
        sourceId: options.id,
        binding: {
          kind: "sampled",
          view: options.view ?? options.texture.createView(),
        },
        width: size.width,
        height: size.height,
        sizeEpoch: size.epoch,
        colorSpace: options.colorSpace ?? "srgb",
        alphaMode: options.alphaMode ?? "premultiplied",
        encoded,
      };
    },

    release() {
      // The app owns the texture; the renderer releases nothing.
    },

    markImported() {
      // Nothing to record.
    },

    destroy() {
      // The app owns the texture; destroying it here would be taking ownership we
      // were never given.
    },
  };
}
