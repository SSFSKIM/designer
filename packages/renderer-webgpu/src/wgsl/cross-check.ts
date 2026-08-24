/**
 * The f32 cross-check pass (Decision Log #20's obligation on C6).
 *
 * S2 measured family D's WGSL against an f64 evaluation of the same arithmetic and
 * got 4.08e-5 px — 0.024% of the declared 0.170 px bound. Family C, the quality
 * governor's first within-tier step, was priced but only inspection-verified, and
 * the spec makes its shipping conditional on it going through the same check.
 *
 * The reason this pass lives in `src/` rather than in a test harness is the point
 * of the whole exercise: it compiles **the same kernel strings the renderer
 * ships** — `WGSL_FIELD_KERNELS`, the constants `fieldPassSource` is assembled
 * from — over a caller-supplied point set. A check that compiled a separate copy
 * of the algebra would prove something about the copy.
 *
 * It is a compute pass rather than a render pass because the output is numbers:
 * a render target would quantise them at whatever the attachment format is, and
 * `rgba16float` has ten mantissa bits, which is coarser than the difference being
 * measured by three orders of magnitude.
 */

export const CROSS_CHECK_SHAPE_FLOATS = 12;
export const CROSS_CHECK_WORKGROUP = 64;

export const WGSL_CROSS_CHECK_PASS = `struct CheckShape {
  centre : vec2f,
  half   : vec2f,
  re     : f32,
  k0     : f32,
  k1     : f32,
  k2     : f32,
  k3     : f32,
  k4     : f32,
  _pad0  : f32,
  _pad1  : f32,
};

/// point.xy = shape-local coordinates, point.z = shape index, point.w unused
@group(0) @binding(0) var<storage, read> checkShapes : array<CheckShape>;
@group(0) @binding(1) var<storage, read> checkPoints : array<vec4f>;
@group(0) @binding(2) var<storage, read_write> outRsupn : array<f32>;
@group(0) @binding(3) var<storage, read_write> outRsup  : array<f32>;
@group(0) @binding(4) var<uniform> checkCount : vec4u;

@compute @workgroup_size(${CROSS_CHECK_WORKGROUP})
fn cs_cross_check(@builtin(global_invocation_id) gid : vec3u) {
  let i = gid.x;
  if (i >= checkCount.x) { return; }

  let p = checkPoints[i];
  let s = checkShapes[u32(p.z)];
  let k = vec4f(s.k0, s.k1, s.k2, s.k3);
  let local = p.xy - s.centre;

  outRsupn[i] = sd_rsupn(local, s.half, s.re, k, s.k4);
  outRsup[i]  = sd_rsup(local, s.half, s.re, k, s.k4);
}`;
