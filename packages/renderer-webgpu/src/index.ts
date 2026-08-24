/**
 * @vitrea/renderer-webgpu — skeleton (C1).
 *
 * This package is the lazy half of X7: nothing here may be reachable from
 * @vitrea/core's entry chunk, so a CSS-tier user never downloads WGSL. C6
 * replaces the placeholder with the real resource graph.
 */

export const OPTICS_PASS_ID = "vitrea.optics";
export const HIGHLIGHT_PASS_ID = "vitrea.highlight";

/**
 * Sentinel WGSL. Its marker comment is what
 * `packages/core/test/bundle-shape.test.ts` greps for to prove the shader text
 * lands in a lazy chunk and not in the entry chunk.
 */
export const PLACEHOLDER_WGSL = `// vitrea:wgsl-marker
fn vitrea_placeholder_optics(uv: vec2<f32>) -> vec4<f32> {
  return vec4<f32>(uv, 0.0, 1.0);
}`;

export interface GlassRenderer {
  readonly backend: "webgpu";
  /** False until C6 lands device acquisition; the seam is real, the renderer is not. */
  readonly ready: boolean;
  readonly passes: readonly string[];
  readonly shaderSource: string;
  destroy(): void;
}

/** Placeholder factory — the shape @vitrea/core's lazy seam resolves to. */
export function createWebGPURenderer(): GlassRenderer {
  return {
    backend: "webgpu",
    ready: false,
    passes: [OPTICS_PASS_ID, HIGHLIGHT_PASS_ID],
    shaderSource: PLACEHOLDER_WGSL,
    destroy: () => undefined,
  };
}
