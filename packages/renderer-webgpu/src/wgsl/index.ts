/**
 * Shader-module assembly.
 *
 * Every module is `prelude + pass`, so the colour pipeline and the fullscreen
 * vertex stage are defined once and there is no way for a pass to acquire its own
 * private transfer function. Assembly is a plain string concatenation performed
 * on demand and cached by the pipeline cache — no build step, no bundler plugin,
 * and the WGSL stays greppable in the built artifact, which is what core's X7
 * bundle test relies on.
 */

import { WGSL_ANALYSIS_PASS } from "./analysis";
import { importPassSource, WGSL_DOWNSAMPLE_PASS } from "./backdrop";
import { fieldPassSource, WGSL_FIELD_KERNELS } from "./field";
import { WGSL_HIGHLIGHT_PASS } from "./highlight";
import { WGSL_OPTICS_PASS } from "./optics";
import { WGSL_PRELUDE } from "./prelude";

export * from "./analysis";
export * from "./backdrop";
export * from "./field";
export * from "./highlight";
export * from "./optics";
export * from "./prelude";

const withPrelude = (pass: string): string => `${WGSL_PRELUDE}\n${pass}\n`;

export type FieldFamily = "rsupn" | "rsup";

export const fieldModule = (family: FieldFamily): string => withPrelude(fieldPassSource(family));

export const importModule = (kind: "sampled" | "external"): string =>
  withPrelude(importPassSource(kind));

export const chainModule = (): string => withPrelude(WGSL_DOWNSAMPLE_PASS);

export const analysisModule = (): string => withPrelude(WGSL_ANALYSIS_PASS);

export const opticsModule = (): string => withPrelude(WGSL_OPTICS_PASS);

export const highlightModule = (): string => withPrelude(WGSL_HIGHLIGHT_PASS);

/**
 * The kernel-only module the f32 cross-check compiles (Decision Log #20).
 *
 * It is assembled from the same constants the field pass is, which is the point:
 * a check that compiled a different string from the one the renderer ships would
 * prove nothing about the shipped shader.
 */
export const crossCheckKernelModule = (): string => withPrelude(WGSL_FIELD_KERNELS);

/**
 * Every shader this package can compile, concatenated.
 *
 * Exposed as `GlassRenderer.shaderSource` — the seam's honest answer to "what
 * WGSL does this renderer carry", and the string core's bundle-shape test finds
 * the marker in.
 */
export function allShaderSource(): string {
  return [
    WGSL_PRELUDE,
    fieldPassSource("rsupn"),
    fieldPassSource("rsup"),
    importPassSource("sampled"),
    importPassSource("external"),
    WGSL_DOWNSAMPLE_PASS,
    WGSL_ANALYSIS_PASS,
    WGSL_OPTICS_PASS,
    WGSL_HIGHLIGHT_PASS,
  ].join("\n\n");
}
