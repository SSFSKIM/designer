/**
 * X7 — the lazy renderer seam.
 *
 * The static import below is type-only, so it is erased at build time; the
 * dynamic import is the only edge from core to the WebGPU renderer. That keeps
 * every byte of WGSL out of core's entry chunk, so a CSS-tier consumer never
 * downloads a shader. `packages/core/test/bundle-shape.test.ts` asserts it on
 * the built artifact rather than trusting this comment.
 */

import type { GlassRenderer } from "@vitrea/renderer-webgpu";

export type { GlassRenderer };

/** Resolve the WebGPU renderer. Call only after a capability probe says yes. */
export async function loadWebGPURenderer(): Promise<GlassRenderer> {
  const { createWebGPURenderer } = await import("@vitrea/renderer-webgpu");
  return createWebGPURenderer();
}
