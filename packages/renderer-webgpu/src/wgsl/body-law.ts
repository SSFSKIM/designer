/**
 * **W42's body law, LT, on the GPU** — the stage `body-law-pass.ts` encodes before the optics pass
 * (G2 `implementation-design.md` §2.3–§2.6 as revised in §11 and §12, and rebuilt as compute in
 * §17; the CPU references are in `body-law.ts` and the storage graph they were measured through is
 * `u2_mirror.py`).
 *
 * Every tile is rgba32float in the form (value·weight, weight), and every read divides by the
 * weight. That is the normalised mode's numerator and weight (`forward.py` `_blur`) in one texel,
 * and the clamp mode is the same arithmetic with a weight of 1. rgba32float is not filterable
 * without `float32-filterable`, so every read is a load, and every in-between read is a bilinear
 * written out by hand.
 *
 * The stage is four compute entry points over job tables, so that one dispatch serves every law
 * surface of a group: `cs_floor` (the capture and its floor), `cs_decimate` (the block means),
 * `cs_blur` (every width's separable passes) and `cs_composite` (A), one compute pass per group
 * that rebuilds. On the Apple adapter a render pass costs about 50 µs whatever it
 * draws, and at eight surfaces the render-pass stage ran some eighty; what remains is bound by
 * the rgba32float tiles' traffic, which is why the capture and the floor's horizontal half never
 * leave the chip (§17).
 *
 * There are no transcendentals here: the Gaussian weights are the instrument's own
 * (`ndimage`'s truncated, normalised kernel), computed on the CPU in f64 and handed over per
 * job, so the WGSL range class (claims §5.163) has nothing new to bound.
 */

/** Outputs per workgroup along a blur job's line: four per lane, interleaved by the lane count. */
export const BODY_LAW_SEGMENT = 256;
/** Lanes per blur and decimate workgroup. */
export const BODY_LAW_LANES = 64;
/** The largest kernel radius a blur job may carry: the line cache holds a segment and both reaches. */
export const BODY_LAW_RADIUS_CAP = 128;
/** A dispatch's extent along x (`maxComputeWorkgroupsPerDimension`'s default). */
export const BODY_LAW_DISPATCH_ROW = 65535;
/** The floor's tile, outputs per workgroup, and the largest floor radius it holds (0.4 × 4 px). */
export const BODY_LAW_FLOOR_TILE = [16, 8] as const;
export const BODY_LAW_FLOOR_RADIUS_CAP = 6;
/** vec4i per job in the blur, floor and decimate job tables. */
export const BODY_LAW_JOB_VEC4S = 4;
/** vec4f per law surface in the composite's surface table. */
export const BODY_LAW_SURFACE_VEC4S = 19;

/**
 * The capture: the pyramid's encoded level 0 (`pyramid.ts` `PyramidResources.encoded`) at a
 * device-pixel centre of the plane through the group's fit — the silhouette tone's mapping
 * (`silhouette-tone.ts`) — by manual bilinear. On both beds the level-0 grid is the device grid, so
 * the centre lands on a texel and the read is that texel.
 */
const WGSL_BODY_LAW_LEVEL0 = `@group(0) @binding(3) var encodedLevel0 : texture_2d<f32>;

fn law_level0_texel(texel : vec2i) -> vec4f {
  let dims = vec2i(textureDimensions(encodedLevel0));
  return textureLoad(encodedLevel0, clamp(texel, vec2i(0), dims - vec2i(1)), 0);
}

fn law_level0(p : vec2f, viewport : vec2f, fit : vec4f) -> vec4f {
  let uv = clamp((p / viewport) * fit.xy + fit.zw, vec2f(0.0), vec2f(1.0));
  let at = uv * vec2f(textureDimensions(encodedLevel0)) - vec2f(0.5);
  let base = vec2i(floor(at));
  let f = at - floor(at);
  let a = law_level0_texel(base);
  // A centre on a texel centre, as on both beds: the bilinear is that texel, exactly.
  if (f.x == 0.0 && f.y == 0.0) { return a; }
  let b = law_level0_texel(base + vec2i(1, 0));
  let c = law_level0_texel(base + vec2i(0, 1));
  let d = law_level0_texel(base + vec2i(1, 1));
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
`;

/** A workgroup's job: the last one starting at or before it (the table is sorted by start). */
const WGSL_BODY_LAW_JOBS = `@group(0) @binding(5) var<storage, read> jobs : array<vec4i>;

fn law_job_of(g : i32, count : i32) -> i32 {
  var lo = 0;
  var hi = count - 1;
  loop {
    if (lo >= hi) { break; }
    let mid = (lo + hi + 1) / 2;
    if (jobs[mid * ${BODY_LAW_JOB_VEC4S}].x <= g) { lo = mid; } else { hi = mid - 1; }
  }
  return lo;
}
`;

/**
 * **One separable Gaussian pass along one axis, for every job at once.** A job is one width of
 * one surface: the lines it writes, the positions along them, the kernel and where its source and
 * target sit in their atlases. A workgroup takes one segment of one line, loads the segment and
 * both reaches into workgroup memory once, and each lane sums four outputs from there. The kernel
 * is symmetric, so each tap pair takes one weight.
 *
 * Taps outside the source's extent along the axis read the edge texel in the clamp mode and zero
 * in the normalised mode, `ndimage`'s `nearest` and `constant`. The weights and radii are the
 * instrument's (`ndimage.gaussian_filter` with `truncate = 4`), handed over as half kernels,
 * centre first.
 *
 * The job table, four vec4i per job: (first workgroup, segments per line, axis, zero | source << 1,
 * the source 0 for atlas A and 1 for atlas B); (first line, end line, first position, end
 * position); (the source's extent along the axis, the radius, the first weight, 0); (the source's
 * offset, the target's offset), an atlas texel being the grid texel plus its offset.
 */
export const WGSL_BODY_LAW_BLUR = `const LAW_SEGMENT : i32 = ${BODY_LAW_SEGMENT};
const LAW_LANES : i32 = ${BODY_LAW_LANES};

struct LawBlurUniforms {
  /// the number of jobs (x), the dispatch's workgroups (y)
  counts : vec4f,
};

@group(0) @binding(0) var<uniform> bu : LawBlurUniforms;
@group(0) @binding(1) var srcA : texture_2d<f32>;
@group(0) @binding(2) var srcB : texture_2d<f32>;
@group(0) @binding(4) var dst : texture_storage_2d<rgba32float, write>;
@group(0) @binding(6) var<storage, read> kernels : array<f32>;

var<workgroup> lineCache : array<vec4f, ${BODY_LAW_SEGMENT + 2 * BODY_LAW_RADIUS_CAP}>;
var<workgroup> kernelCache : array<f32, ${BODY_LAW_RADIUS_CAP + 1}>;

${WGSL_BODY_LAW_JOBS}
fn law_blur_texel(axis : i32, line : i32, pos : i32) -> vec2i {
  if (axis == 1) { return vec2i(line, pos); }
  return vec2i(pos, line);
}

fn law_blur_read(head : vec4i, extent : i32, src : vec2i, line : i32, pos : i32) -> vec4f {
  if ((head.w & 1) != 0 && (pos < 0 || pos >= extent)) { return vec4f(0.0); }
  let texel = law_blur_texel(head.z, line, clamp(pos, 0, extent - 1)) + src;
  if ((head.w >> 1u) == 1) { return textureLoad(srcB, texel, 0); }
  return textureLoad(srcA, texel, 0);
}

fn law_blur_store(axis : i32, offset : vec2i, line : i32, pos : i32, end : i32, v : vec4f) {
  if (pos >= end) { return; }
  textureStore(dst, law_blur_texel(axis, line, pos) + offset, v);
}

@compute @workgroup_size(${BODY_LAW_LANES})
fn cs_blur(@builtin(workgroup_id) wg : vec3u, @builtin(local_invocation_index) lane : u32) {
  let g = i32(wg.y) * ${BODY_LAW_DISPATCH_ROW} + i32(wg.x);
  if (g >= i32(bu.counts.y)) { return; }
  let job = law_job_of(g, i32(bu.counts.x)) * ${BODY_LAW_JOB_VEC4S};
  let head = jobs[job];
  let span = jobs[job + 1];
  let taps = jobs[job + 2];
  let offsets = jobs[job + 3];
  let local = g - head.x;
  let line = span.x + local / head.y;
  let base = span.z + (local % head.y) * LAW_SEGMENT;
  let r = taps.y;
  for (var i = i32(lane); i < LAW_SEGMENT + 2 * r; i = i + LAW_LANES) {
    lineCache[i] = law_blur_read(head, taps.x, offsets.xy, line, base - r + i);
  }
  for (var i = i32(lane); i <= r; i = i + LAW_LANES) { kernelCache[i] = kernels[taps.z + i]; }
  workgroupBarrier();

  let c = i32(lane) + r;
  let w0 = kernelCache[0];
  var s0 = w0 * lineCache[c];
  var s1 = w0 * lineCache[c + LAW_LANES];
  var s2 = w0 * lineCache[c + 2 * LAW_LANES];
  var s3 = w0 * lineCache[c + 3 * LAW_LANES];
  for (var k = 1; k <= r; k = k + 1) {
    let w = kernelCache[k];
    s0 = s0 + w * (lineCache[c - k] + lineCache[c + k]);
    s1 = s1 + w * (lineCache[c + LAW_LANES - k] + lineCache[c + LAW_LANES + k]);
    s2 = s2 + w * (lineCache[c + 2 * LAW_LANES - k] + lineCache[c + 2 * LAW_LANES + k]);
    s3 = s3 + w * (lineCache[c + 3 * LAW_LANES - k] + lineCache[c + 3 * LAW_LANES + k]);
  }
  let first = base + i32(lane);
  law_blur_store(head.z, offsets.zw, line, first, span.w, s0);
  law_blur_store(head.z, offsets.zw, line, first + LAW_LANES, span.w, s1);
  law_blur_store(head.z, offsets.zw, line, first + 2 * LAW_LANES, span.w, s2);
  law_blur_store(head.z, offsets.zw, line, first + 3 * LAW_LANES, span.w, s3);
}
`;

/**
 * **The capture and its floor in one dispatch**, memo C's Gaussian at 0.4 capture texels in the
 * clamp mode (`forward.py` `Cell.S`): S. A workgroup captures its tile and the floor's reach on
 * every side into workgroup memory, runs the horizontal pass there over every row the vertical
 * pass reads, and the vertical pass from that, so neither the capture nor the horizontal half
 * leaves the chip. The reach's texels are the footprint's clamped ones, and a row above or below
 * the footprint is its clamped row's horizontal result, which is what the two separable passes
 * of the clamp mode compute.
 *
 * The job table, four vec4i per job: (first workgroup, tiles per row, radius, first weight); (the
 * footprint's extent, S's origin in its atlas); (the footprint's origin on the plane, 0, 0).
 */
export const WGSL_BODY_LAW_FLOOR = `const LAW_TILE = vec2i(${BODY_LAW_FLOOR_TILE[0]}, ${BODY_LAW_FLOOR_TILE[1]});
const LAW_TILE_LANES : i32 = ${BODY_LAW_FLOOR_TILE[0] * BODY_LAW_FLOOR_TILE[1]};

struct LawFloorUniforms {
  /// the viewport in device px (xy), the number of jobs (z), the dispatch's workgroups (w)
  viewport : vec4f,
  /// the group's fit into level 0: uv scale (xy), uv offset (zw)
  fit      : vec4f,
  /// 1 to decode the capture to linear light before any averaging (D2 = 0, the identity) (x)
  mode     : vec4f,
};

@group(0) @binding(0) var<uniform> fu : LawFloorUniforms;
@group(0) @binding(4) var floored : texture_storage_2d<rgba32float, write>;
@group(0) @binding(6) var<storage, read> kernels : array<f32>;

var<workgroup> captureCache : array<vec4f, ${(BODY_LAW_FLOOR_TILE[0] + 2 * BODY_LAW_FLOOR_RADIUS_CAP) * (BODY_LAW_FLOOR_TILE[1] + 2 * BODY_LAW_FLOOR_RADIUS_CAP)}>;
var<workgroup> rowCache : array<vec4f, ${BODY_LAW_FLOOR_TILE[0] * (BODY_LAW_FLOOR_TILE[1] + 2 * BODY_LAW_FLOOR_RADIUS_CAP)}>;
var<workgroup> floorKernel : array<f32, ${BODY_LAW_FLOOR_RADIUS_CAP + 1}>;

${WGSL_BODY_LAW_LEVEL0}
${WGSL_BODY_LAW_JOBS}
/// S0 at a plane pixel: (value·α, α), encoded, or linear light under D2 = 0.
fn law_capture(texel : vec2i) -> vec4f {
  let v = law_level0(vec2f(texel) + vec2f(0.5), fu.viewport.xy, fu.fit);
  if (fu.mode.x > 0.5) {
    let straight = v.rgb / max(v.a, 1e-9);
    return vec4f(srgb_to_linear(clamp(straight, vec3f(0.0), vec3f(1.0))) * v.a, v.a);
  }
  return v;
}

@compute @workgroup_size(${BODY_LAW_FLOOR_TILE[0]}, ${BODY_LAW_FLOOR_TILE[1]})
fn cs_floor(@builtin(workgroup_id) wg : vec3u, @builtin(local_invocation_id) local : vec3u,
  @builtin(local_invocation_index) lane : u32) {
  let g = i32(wg.y) * ${BODY_LAW_DISPATCH_ROW} + i32(wg.x);
  if (g >= i32(fu.viewport.w)) { return; }
  let job = law_job_of(g, i32(fu.viewport.z)) * ${BODY_LAW_JOB_VEC4S};
  let head = jobs[job];
  let extent = jobs[job + 1];
  let origin = jobs[job + 2].xy;
  let index = g - head.x;
  let tile = vec2i(index % head.y, index / head.y) * LAW_TILE;
  let r = head.z;
  let width = LAW_TILE.x + 2 * r;
  let rows = LAW_TILE.y + 2 * r;
  for (var i = i32(lane); i < width * rows; i = i + LAW_TILE_LANES) {
    let p = tile - vec2i(r) + vec2i(i % width, i / width);
    captureCache[i] = law_capture(clamp(p, vec2i(0), extent.xy - vec2i(1)) + origin);
  }
  for (var i = i32(lane); i <= r; i = i + LAW_TILE_LANES) { floorKernel[i] = kernels[head.w + i]; }
  workgroupBarrier();

  for (var i = i32(lane); i < LAW_TILE.x * rows; i = i + LAW_TILE_LANES) {
    let c = (i / LAW_TILE.x) * width + i % LAW_TILE.x + r;
    var sum = floorKernel[0] * captureCache[c];
    for (var k = 1; k <= r; k = k + 1) {
      sum = sum + floorKernel[k] * (captureCache[c - k] + captureCache[c + k]);
    }
    rowCache[i] = sum;
  }
  workgroupBarrier();

  let out = tile + vec2i(local.xy);
  if (any(out >= extent.xy)) { return; }
  let c = (i32(local.y) + r) * LAW_TILE.x + i32(local.x);
  var sum = floorKernel[0] * rowCache[c];
  for (var k = 1; k <= r; k = k + 1) {
    sum = sum + floorKernel[k] * (rowCache[c - k * LAW_TILE.x] + rowCache[c + k * LAW_TILE.x]);
  }
  textureStore(floored, out + extent.zw, sum);
}
`;

/**
 * `forward.py`'s `_blur_decimated` up to its Gaussian: the floored tile padded by P
 * full-resolution texels (edge texels in the clamp mode, zeros in the normalised mode), then the
 * mean of each q × q block. P is the largest any width of this q needs, a multiple of q, so the
 * blocks are the ones every width's own padding would have made and a narrower width's kernel
 * never reaches the extra rows (`body-law-pass.ts` says why).
 *
 * The job table, four vec4i per job: (first workgroup, texels, q, P); (the grid's extent, the
 * floored tile's extent); (the floored tile's origin in its atlas, the grid's origin in its
 * atlas); (1 for zero padding, 0, 0, 0).
 */
export const WGSL_BODY_LAW_DECIMATE = `struct LawDecimateUniforms {
  /// the number of jobs (x), the dispatch's workgroups (y)
  counts : vec4f,
};

@group(0) @binding(0) var<uniform> du : LawDecimateUniforms;
@group(0) @binding(1) var floored : texture_2d<f32>;
@group(0) @binding(4) var grid : texture_storage_2d<rgba32float, write>;

${WGSL_BODY_LAW_JOBS}
@compute @workgroup_size(${BODY_LAW_LANES})
fn cs_decimate(@builtin(workgroup_id) wg : vec3u, @builtin(local_invocation_index) lane : u32) {
  let g = i32(wg.y) * ${BODY_LAW_DISPATCH_ROW} + i32(wg.x);
  if (g >= i32(du.counts.y)) { return; }
  let job = law_job_of(g, i32(du.counts.x)) * ${BODY_LAW_JOB_VEC4S};
  let head = jobs[job];
  let extents = jobs[job + 1];
  let offsets = jobs[job + 2];
  let zero = jobs[job + 3].x != 0;
  let t = (g - head.x) * ${BODY_LAW_LANES} + i32(lane);
  if (t >= head.y) { return; }
  let q = head.z;
  let at = vec2i(t % extents.x, t / extents.x);
  let dims = extents.zw;
  let block = at * q - vec2i(head.w);
  var sum = vec4f(0.0);
  for (var y = 0; y < q; y = y + 1) {
    for (var x = 0; x < q; x = x + 1) {
      let s = block + vec2i(x, y);
      if (zero) {
        if (all(s >= vec2i(0)) && all(s < dims)) {
          sum = sum + textureLoad(floored, s + offsets.xy, 0);
        }
      } else {
        sum = sum + textureLoad(floored, clamp(s, vec2i(0), dims - vec2i(1)) + offsets.xy, 0);
      }
    }
  }
  textureStore(grid, at + offsets.zw, sum / f32(q * q));
}
`;

/**
 * **A** (§2.6, R2): one invocation per texel of the group's surface rect. It computes every law
 * surface's circular-corner SDF and takes the smallest, the first on a tie — the rehearsal's owner
 * rule (`body.py`'s `np.argmin`). Where the owner's footprint holds the texel, A is the law's
 * argument there; everywhere else it is the captured backdrop, and its luma where W's would be:
 * the rehearsal's A_out = B and W_out = B before any surface writes (`body.py` `lt_argument`).
 * The argument:
 *
 * - σn at the pixel from the declared opacity law at its own depth, and C by the interpolation
 *   the plan names through the stored levels (`bodyLawInterpolateLevels`);
 * - W from its tile;
 * - the knee and M by `bodyLawComposite`, term for term;
 * - A = (M, L(W)), encoded and NOT clipped: the declared oracle passes M to T unclipped
 *   (`forward.py:527`, `T(255 * M)`; the rehearsal's argument, `body.py:706`, `713`), and each tone
 *   clips where its own gamut step does (`body.py:513`, `515`, `550`, `573`; `swap.py:219`, `233`).
 *   A clip here would move an out-of-range argument's chroma term before the tone reads it.
 *
 * A level stored at q = 1 is read at the pixel's own texel. A decimated one is read at
 * `forward.py`'s return coordinate, (P + i + 0.5) / q − 0.5 on its grid, bilinear with the edge
 * held (`map_coordinates`, `order = 1`, `nearest`). Every read is clamped to its grid and then
 * offset into its atlas, and the stage stores exactly the texels these reads reach
 * (`bodyLawRegions`).
 *
 * The surface table, nineteen vec4f per surface: the footprint's origin on the plane and its size
 * (a size of 0 is a surface the stage did not build); (the span in points, t, k_n·5·u in device
 * px, the number of stored levels); (the interpolation, 0 single, 1 linear, 2 cubic; 1 receded);
 * then two vec4f per level k, 0…6 and W at 7: (σ, q, P, 1 where the level is the floored tile
 * itself) and (its atlas offset, its grid's extent).
 */
export const WGSL_BODY_LAW_COMPOSITE = `struct LawShape {
  /// the box in device px on the plane: origin (xy), size (zw)
  rect   : vec4f,
  /// the corner radius in device px (x)
  radius : vec4f,
};

struct LawCompositeUniforms {
  /// the viewport in device px (xy); A's origin on the plane, device px (zw)
  viewport : vec4f,
  /// the group's fit into level 0: uv scale (xy), uv offset (zw)
  fit      : vec4f,
  /// the number of law surfaces (x), the device ratio (y), D2 (z)
  group    : vec4f,
  /// λ (x), the Normal fill w (y), the hinge h (z), the knee form (w)
  knee     : vec4f,
};

@group(0) @binding(0) var<uniform> cu : LawCompositeUniforms;
@group(0) @binding(1) var<storage, read> shapes : array<LawShape>;
@group(0) @binding(2) var<storage, read> lawSurfaces : array<vec4f>;
@group(0) @binding(4) var flooredAtlas : texture_2d<f32>;
@group(0) @binding(5) var levelAtlas : texture_2d<f32>;
@group(0) @binding(6) var argumentA : texture_storage_2d<rgba32float, write>;

const LAW_SURFACE : u32 = ${BODY_LAW_SURFACE_VEC4S}u;

${WGSL_BODY_LAW_LEVEL0}
fn law_sdf(p : vec2f, shape : LawShape) -> f32 {
  let half = shape.rect.zw * 0.5;
  let centre = shape.rect.xy + half;
  let radius = min(shape.radius.x, min(half.x, half.y));
  let q = abs(p - centre) - half + vec2f(radius);
  return length(max(q, vec2f(0.0))) + min(max(q.x, q.y), 0.0) - radius;
}

fn level_head(s : u32, k : u32) -> vec4f {
  return lawSurfaces[s * LAW_SURFACE + 3u + 2u * k];
}

fn level_texel(s : u32, k : u32, texel : vec2i) -> vec4f {
  let head = level_head(s, k);
  let place = lawSurfaces[s * LAW_SURFACE + 4u + 2u * k];
  let at = clamp(texel, vec2i(0), vec2i(place.zw) - vec2i(1)) + vec2i(place.xy);
  if (head.w > 0.5) { return textureLoad(flooredAtlas, at, 0); }
  return textureLoad(levelAtlas, at, 0);
}

fn level_sigma(s : u32, k : u32) -> f32 {
  return level_head(s, k).x;
}

/// The value a stored level holds at the footprint pixel i, weight divided out. k = 7 is W.
fn tile_value(s : u32, k : u32, i : vec2i) -> vec3f {
  let head = level_head(s, k);
  let q = head.y;
  let pad = head.z;
  var v : vec4f;
  if (q < 1.5) {
    v = level_texel(s, k, i);
  } else {
    let at = (vec2f(i) + vec2f(pad + 0.5)) / q - vec2f(0.5);
    let base = vec2i(floor(at));
    let f = at - floor(at);
    let a = level_texel(s, k, base);
    let b = level_texel(s, k, base + vec2i(1, 0));
    let c = level_texel(s, k, base + vec2i(0, 1));
    let d = level_texel(s, k, base + vec2i(1, 1));
    v = mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }
  return v.rgb / max(v.a, 1e-9);
}

/// The declared opacity o(s, d, pose) ('bodyLawOpacity'), d in points.
fn law_opacity(s : u32, d : f32) -> f32 {
  let law = lawSurfaces[s * LAW_SURFACE + 1u];
  let t = law.y;
  if (lawSurfaces[s * LAW_SURFACE + 2u].y > 0.5) { return 0.4 + 0.4 * t; }
  let centre = -law.x * 0.5;
  if (d <= centre) { return 0.8 * t; }
  if (d <= -1.0) { return 0.8 * t + (0.4 * t - 0.8 * t) * ((d - centre) / (-1.0 - centre)); }
  if (d <= 0.0) { return 0.4 * t + (0.5 - 0.4 * t) * ((d + 1.0) / 1.0); }
  return 0.5;
}

/// C at the footprint pixel i for a width sigma ('bodyLawInterpolateLevels').
fn narrow_at(s : u32, sigma : f32, i : vec2i) -> vec3f {
  let n = u32(lawSurfaces[s * LAW_SURFACE + 1u].w);
  let interpolation = lawSurfaces[s * LAW_SURFACE + 2u].x;
  if (interpolation < 0.5 || n == 1u) { return tile_value(s, 0u, i); }
  let x = clamp(sigma, level_sigma(s, 0u), level_sigma(s, n - 1u));
  var upper = 0u;
  loop {
    if (upper >= n || level_sigma(s, upper) >= x) { break; }
    upper = upper + 1u;
  }
  if (interpolation < 1.5 || n < 4u) {
    let k = u32(clamp(i32(upper) - 1, 0, i32(n) - 2));
    let a = level_sigma(s, k);
    let b = level_sigma(s, k + 1u);
    let w = (x - a) / (b - a);
    let va = tile_value(s, k, i);
    return clamp(va + w * (tile_value(s, k + 1u, i) - va), vec3f(0.0), vec3f(1.0));
  }
  let start = u32(clamp(i32(upper) - 2, 0, i32(n) - 4));
  var out = vec3f(0.0);
  for (var j = 0u; j < 4u; j = j + 1u) {
    var wj = 1.0;
    let xj = level_sigma(s, start + j);
    for (var m = 0u; m < 4u; m = m + 1u) {
      if (m != j) {
        let xm = level_sigma(s, start + m);
        wj = wj * (x - xm) / (xj - xm);
      }
    }
    out = out + wj * tile_value(s, start + j, i);
  }
  return clamp(out, vec3f(0.0), vec3f(1.0));
}

fn law_luma(c : vec3f) -> f32 {
  return dot(c, vec3f(0.2126, 0.7152, 0.0722));
}

/// The argument at the footprint pixel i of surface s, whose signed distance there is d, device px.
fn law_argument(s : u32, i : vec2i, d : f32) -> vec4f {
  let unit = lawSurfaces[s * LAW_SURFACE + 1u].z;
  let C = narrow_at(s, unit * law_opacity(s, d / cu.group.y), i);
  let W = tile_value(s, 7u, i);

  let lam = cu.knee.x;
  let w = cu.knee.y;
  let h = cu.knee.z;
  var M : vec3f;
  if (cu.knee.w < 0.5) {
    let N = C + h * lam * max(vec3f(0.0), h * (W - C));
    M = (1.0 - w) * N + w * W;
  } else if (cu.knee.w < 1.5) {
    let on = select(0.0, 1.0, h * (law_luma(W) - law_luma(C)) > 0.0);
    let N = C + lam * on * (W - C);
    M = (1.0 - w) * N + w * W;
  } else {
    let CL = law_luma(C);
    let WL = law_luma(W);
    let NL = CL + h * lam * max(0.0, h * (WL - CL));
    let ML = (1.0 - w) * NL + w * WL;
    M = vec3f(ML) + (W - vec3f(WL));
  }
  if (cu.group.z > 0.5) {
    // Unclipped: rgba32float carries an out-of-range M to the tone, which clips where it clips.
    return vec4f(M, law_luma(W));
  }
  // D2 = 0: C and W were averaged in linear light, and A is encoded here (the rejected F2).
  let We = linear_to_srgb(clamp(W, vec3f(0.0), vec3f(1.0)));
  return vec4f(linear_to_srgb(clamp(M, vec3f(0.0), vec3f(1.0))), law_luma(We));
}

@compute @workgroup_size(8, 8)
fn cs_composite(@builtin(global_invocation_id) id : vec3u) {
  let size = textureDimensions(argumentA);
  if (id.x >= size.x || id.y >= size.y) { return; }
  let texel = cu.viewport.zw + vec2f(id.xy);
  let p = texel + vec2f(0.5);
  let count = u32(cu.group.x);
  var owner = 0u;
  var best = law_sdf(p, shapes[0]);
  for (var j = 1u; j < count; j = j + 1u) {
    let dj = law_sdf(p, shapes[j]);
    if (dj < best) { best = dj; owner = j; }
  }
  let footprint = lawSurfaces[owner * LAW_SURFACE];
  let i = vec2i(texel - footprint.xy);
  var out : vec4f;
  if (all(i >= vec2i(0)) && all(i < vec2i(footprint.zw))) {
    out = law_argument(owner, i, best);
  } else {
    let v = law_level0(p, cu.viewport.xy, cu.fit);
    let straight = v.rgb / max(v.a, 1e-9);
    out = vec4f(straight, law_luma(straight));
  }
  textureStore(argumentA, vec2i(id.xy), out);
}
`;
