/**
 * The analysis reduction: luminance, variance and edge density off the blur
 * pyramid, into a four-float stats buffer per backdrop source.
 *
 * This is what `analysis: "exact"` means in X2 — a real reduction over the real
 * pixels, not an estimate. It runs once per pyramid rebuild, which by the §Core
 * model invariant is at most once per dirty source per frame.
 *
 * ## Why one workgroup
 *
 * The reduction reads a fixed 64×64 grid of bilinear samples off a chosen chain
 * level, whatever that level's real size is. That makes the pass's cost constant
 * — 4096 samples, one workgroup, one dispatch — instead of proportional to the
 * backdrop's resolution, and it makes the result independent of the resolution
 * policy, so raising or lowering `scale` does not move the tint. A grid rather
 * than every texel is the right trade because the values feed a tint and a
 * light/dark decision, both of which are already low-passed in time.
 *
 * ## Edge density
 *
 * Central differences of luminance on the same grid, averaged. Read off a
 * mid-chain level rather than the coarsest: the coarsest level has had every edge
 * blurred out of it, so an edge measurement there would report the same small
 * number for a photograph and for a solid colour. The level choice lives on the
 * CPU (`pyramid-plan.ts`) where the sizes are known.
 *
 * ## Variance
 *
 * Accumulated as the mean of squares and folded at the end, which is the
 * numerically shakier of the two standard routes — but the inputs are luminances
 * in [0, ~1] over 4096 samples, so the cancellation is nowhere near f32's
 * resolution, and it costs one accumulator instead of two passes.
 */

export const ANALYSIS_WORKGROUP = 64;
export const ANALYSIS_GRID = 64;

/**
 * `stats` layout: mean luminance (ENCODED-space mean, decoded once by the host —
 * the W9 model, claims §5.31), variance (linear), edge density, sample count.
 */
export const ANALYSIS_STATS_FLOATS = 4;

export const WGSL_ANALYSIS_PASS = `struct AnalysisUniforms {
  /// grid.xy = sample grid size, grid.z = source level, grid.w = 1/(grid-1)
  grid : vec4f,
  /// texel.xy = one texel of the sampled level, in uv
  texel : vec4f,
};

@group(0) @binding(0) var<uniform> au : AnalysisUniforms;
@group(0) @binding(1) var analysisSampler : sampler;
@group(0) @binding(2) var analysisTexture : texture_2d<f32>;
@group(0) @binding(3) var<storage, read_write> stats : array<f32>;

var<workgroup> partialLum  : array<f32, ${ANALYSIS_WORKGROUP}>;
var<workgroup> partialTone : array<f32, ${ANALYSIS_WORKGROUP}>;
var<workgroup> partialSq   : array<f32, ${ANALYSIS_WORKGROUP}>;
var<workgroup> partialEdge : array<f32, ${ANALYSIS_WORKGROUP}>;

fn lum_at(uv : vec2f) -> f32 {
  let s = textureSampleLevel(analysisTexture, analysisSampler, uv, au.grid.z);
  // Level 0 onwards is premultiplied linear; unpremultiplying keeps a
  // transparent backdrop region from reading as black rather than as absent.
  let colour = s.rgb / max(s.a, 1e-6);
  return luminance(colour);
}

@compute @workgroup_size(${ANALYSIS_WORKGROUP})
fn cs_analysis(@builtin(local_invocation_index) lane : u32) {
  let total = u32(au.grid.x * au.grid.y);
  var sumLum = 0.0;
  var sumTone = 0.0;
  var sumSq = 0.0;
  var sumEdge = 0.0;
  var n = 0.0;

  var i = lane;
  loop {
    if (i >= total) { break; }
    let gx = f32(i % u32(au.grid.x));
    let gy = f32(i / u32(au.grid.x));
    let uv = vec2f(gx, gy) * au.grid.w;

    let c = lum_at(uv);
    let dx = lum_at(uv + vec2f(au.texel.x, 0.0)) - lum_at(uv - vec2f(au.texel.x, 0.0));
    let dy = lum_at(uv + vec2f(0.0, au.texel.y)) - lum_at(uv - vec2f(0.0, au.texel.y));

    // The published luminance accumulates ENCODED — the W9 model (claims
    // 5.31): the reference's tone responses track the encoded-space mean of a
    // structured backdrop, not its linear mean. The host decodes the mean once
    // on readback, so every consumer downstream still speaks linear light.
    // The linear sum stays, because the variance fold below needs a mean in
    // the same space as its squares; variance and edge density stay linear —
    // nothing tonal reads them.
    sumLum = sumLum + c;
    sumTone = sumTone + linear_to_srgb(vec3f(c, c, c)).x;
    sumSq = sumSq + c * c;
    sumEdge = sumEdge + length(vec2f(dx, dy)) * 0.5;
    n = n + 1.0;

    i = i + ${ANALYSIS_WORKGROUP}u;
  }

  partialLum[lane] = sumLum;
  partialTone[lane] = sumTone;
  partialSq[lane] = sumSq;
  partialEdge[lane] = sumEdge;
  workgroupBarrier();

  // Tree reduction. ${ANALYSIS_WORKGROUP} is a power of two, so no tail case.
  var stride = ${ANALYSIS_WORKGROUP}u / 2u;
  loop {
    if (stride == 0u) { break; }
    if (lane < stride) {
      partialLum[lane] = partialLum[lane] + partialLum[lane + stride];
      partialTone[lane] = partialTone[lane] + partialTone[lane + stride];
      partialSq[lane] = partialSq[lane] + partialSq[lane + stride];
      partialEdge[lane] = partialEdge[lane] + partialEdge[lane + stride];
    }
    workgroupBarrier();
    stride = stride / 2u;
  }

  if (lane == 0u) {
    let count = max(f32(total), 1.0);
    let mean = partialLum[0] / count;
    // stats[0] is the ENCODED-space mean; the host decodes it once (W9).
    stats[0] = partialTone[0] / count;
    stats[1] = max(partialSq[0] / count - mean * mean, 0.0);
    stats[2] = partialEdge[0] / count;
    stats[3] = count;
  }
}`;
