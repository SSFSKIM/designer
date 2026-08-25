/**
 * X7 — the lazy renderer seam.
 *
 * The static import below is type-only, so it is erased at build time; the
 * dynamic import is the only edge from core to the WebGPU renderer. That keeps
 * every byte of WGSL out of core's entry chunk, so a CSS-tier consumer never
 * downloads a shader. `packages/core/test/bundle-shape.test.ts` asserts it on
 * the built artifact rather than trusting this comment.
 */

import type {
  BackdropProvider,
  CopyProviderOptions,
  GlassRenderer,
  VideoProviderOptions,
} from "@vitrea/renderer-webgpu";

export type { BackdropProvider, CopyProviderOptions, GlassRenderer, VideoProviderOptions };

/**
 * The renderer's constructors, as the seam's consumers need them.
 *
 * A host that attaches the renderer to real canvases also has to build the
 * backdrop providers that feed it, and both must come through the *same* dynamic
 * import — a second entry edge would emit a second chunk and split the renderer
 * in two. Declared as an interface rather than `typeof import(...)` so the seam
 * states exactly what it promises, and the real module is checked against it.
 */
export interface WebGPURendererModule {
  createWebGPURenderer(): GlassRenderer;
  createCopyProvider(options: CopyProviderOptions): BackdropProvider;
  createVideoProvider(options: VideoProviderOptions): BackdropProvider;
}

/** Resolve the renderer module. Call only after a capability probe says yes. */
export async function loadWebGPURendererModule(): Promise<WebGPURendererModule> {
  return import("@vitrea/renderer-webgpu");
}

/** Resolve the WebGPU renderer. Call only after a capability probe says yes. */
export async function loadWebGPURenderer(): Promise<GlassRenderer> {
  const { createWebGPURenderer } = await loadWebGPURendererModule();
  return createWebGPURenderer();
}
