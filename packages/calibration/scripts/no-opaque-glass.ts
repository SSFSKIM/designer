/**
 * **X75 — no opaque glass** (W49 charter Decision Log 3; claims §5.215): the one statement of the
 * invariant, read by the runtime test over every shipped endpoint
 * (`test/x75-no-opaque-glass.test.ts`) and by the refusals in W49a's builder and seal
 * (`results/2026-10-07-w49a-g0-declaration/{fit/build-candidate.ts,seal/seal.ts}`), so a candidate
 * that would draw opaque glass is never built, never sealed and never shipped.
 *
 * W47's operator 1 grades the body's transmission by span,
 * `alphaBase = clamp(tintAlpha + rampAtScale(tintAlphaFar1x, tintAlphaFar2x, dpr) · farS(span), 0, 1)`,
 * per pixel in the optics pass and per surface on the CSS tier. Nothing bounded the sum below the
 * clamp, and 0.28.0 shipped an endpoint that reaches it (the dark `-glass0.25` receded document,
 * W49 grounding F1). The bound is the parent's margin, 0.95, at every integer span 0..1024 CSS px,
 * at dpr 1 and 2, on both variants and both tiers: the WebGPU tier's alpha is what the renderer packs
 * (`opticsUnderPolicy` at the nominal policy, then the CPU statement of the shader's `alphaBase`
 * line), the CSS tier's what `materialAtBackdrop` hands its occlusion term. Since W49b D both
 * readers resolve the transmission's independent top (zero anchors follow their own scatter
 * top before DPR interpolation), so an earlier or later alpha top cannot evade this checker.
 * Nominal policy only:
 * Reduce Transparency's occlusion lift and forced colours raise the body toward opaque by design,
 * and they are the accessibility fold's to bound.
 */
import {
  occlusionAlphaUnderPolicy as cssOcclusionAlphaUnderPolicy,
  sourceOptics,
  sourceSize,
  spanGradedTintAlpha as cssSpanGradedTintAlpha,
} from "@vitreajs/vitrea-web";
import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_VARIANTS,
  NOMINAL_MATERIAL_POLICY,
  opticsUnderPolicy,
  spanGradedTintAlpha as rendererSpanGradedTintAlpha,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

/** The bound (W49 Decision Log 3): no endpoint's base alpha above this, at any span. */
export const X75_MAX_ALPHA_BASE = 0.95;
/**
 * The comparison's float allowance. The bound is a statement in real arithmetic, and a document
 * that names `tintAlpha` 0.8 and a far delta 0.15 sits exactly on it there while its f64 sum is
 * 0.9500000000000001; one part in 10⁹ admits the bound itself and nothing a fitted leaf can reach.
 */
export const X75_FLOAT_ALLOWANCE = 1e-9;
export const X75_SPAN_MAX_CSS_PX = 1024;
export const X75_DEVICE_PIXEL_RATIOS = [1, 2] as const;

export interface OpaqueGlassViolation {
  readonly tier: "webgpu" | "css";
  readonly variant: string;
  readonly dpr: number;
  readonly span: number;
  readonly alphaBase: number;
}

/**
 * Every (tier, variant, dpr, span) at which a POSED endpoint's base alpha exceeds the bound. `patch`
 * is the complete patch over `DEFAULT_MATERIAL_PROFILE` that draws: an active endpoint's own, or a
 * receded endpoint's merged over its active one, as the root poses it.
 */
export function opaqueGlassViolations(patch: MaterialProfilePatch | undefined): OpaqueGlassViolation[] {
  const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch ?? {});
  const cssPatch = patch as Parameters<typeof sourceSize>[0];
  const size = sourceSize(cssPatch);
  const css = sourceOptics(cssPatch);
  const out: OpaqueGlassViolation[] = [];
  for (const variant of MATERIAL_VARIANTS) {
    const gpuAlpha = opticsUnderPolicy(profile.optics[variant], NOMINAL_MATERIAL_POLICY, profile)
      .tintAlpha;
    const cssAlpha = cssOcclusionAlphaUnderPolicy(css[variant].tintAlpha, "nominal");
    for (const dpr of X75_DEVICE_PIXEL_RATIOS) {
      for (let span = 0; span <= X75_SPAN_MAX_CSS_PX; span += 1) {
        const gpu = rendererSpanGradedTintAlpha(gpuAlpha, span, profile, dpr);
        if (gpu > X75_MAX_ALPHA_BASE + X75_FLOAT_ALLOWANCE) {
          out.push({ tier: "webgpu", variant, dpr, span, alphaBase: gpu });
        }
        const cssBase = cssSpanGradedTintAlpha(cssAlpha, span, size, dpr);
        if (cssBase > X75_MAX_ALPHA_BASE + X75_FLOAT_ALLOWANCE) {
          out.push({ tier: "css", variant, dpr, span, alphaBase: cssBase });
        }
      }
    }
  }
  return out;
}

/** A readable summary: per (tier, variant, dpr), the first offending span and the maximum. */
export function summariseOpaqueGlass(found: readonly OpaqueGlassViolation[]): string[] {
  const groups = new Map<string, OpaqueGlassViolation[]>();
  for (const v of found) {
    const key = `${v.tier} ${v.variant} dpr ${v.dpr}`;
    groups.set(key, [...(groups.get(key) ?? []), v]);
  }
  return [...groups].map(([key, list]) =>
    `${key}: ${list.length} spans from ${list[0]!.span} CSS px, max alphaBase `
    + `${Math.max(...list.map((v) => v.alphaBase)).toFixed(4)}`);
}
