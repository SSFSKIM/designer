/**
 * **W42's body law, LT, on the GPU** — the stage `body-law-pass.ts` encodes before the optics pass
 * (G2 `implementation-design.md` §2.3–§2.6 as revised in §11 and §12; the CPU references are in
 * `body-law.ts` and the storage graph they were measured through is `u2_mirror.py`).
 *
 * Every tile is rgba32float in the form (value·weight, weight), and every read divides by the
 * weight. That is the normalised mode's numerator and weight (`forward.py` `_blur`) in one texel,
 * and the clamp mode is the same arithmetic with a weight of 1. rgba32float is not filterable
 * without `float32-filterable`, so every read is a load, and every in-between read is a bilinear
 * written out by hand.
 *
 * There are no transcendentals here: the Gaussian weights are the instrument's own
 * (`ndimage`'s truncated, normalised kernel), computed on the CPU in f64 and handed over per
 * pass, so the WGSL range class (claims §5.163) has nothing new to bound.
 */

/**
 * The capture and A's initial fill. Both read the pyramid's encoded level 0 (`pyramid.ts`
 * `PyramidResources.encoded`) at a device-pixel centre of the plane through the group's fit —
 * the silhouette tone's mapping (`silhouette-tone.ts`) — by manual bilinear. On both beds the
 * level-0 grid is the device grid, so the centre lands on a texel and the read is that texel.
 */
export const WGSL_BODY_LAW_CAPTURE = `struct CaptureUniforms {
  /// the viewport in device px (xy); the target's origin on the plane in device px (zw)
  viewport : vec4f,
  /// the group's fit into level 0: uv scale (xy), uv offset (zw)
  fit      : vec4f,
  /// 1 to decode to linear light before any averaging (D2 = 0, the identity) (x)
  mode     : vec4f,
};

@group(0) @binding(0) var<uniform> cu : CaptureUniforms;
@group(0) @binding(1) var encodedLevel0 : texture_2d<f32>;

fn load_level0(texel : vec2i) -> vec4f {
  let dims = vec2i(textureDimensions(encodedLevel0));
  return textureLoad(encodedLevel0, clamp(texel, vec2i(0), dims - vec2i(1)), 0);
}

fn sample_level0(p : vec2f) -> vec4f {
  let uv = clamp((p / cu.viewport.xy) * cu.fit.xy + cu.fit.zw, vec2f(0.0), vec2f(1.0));
  let at = uv * vec2f(textureDimensions(encodedLevel0)) - vec2f(0.5);
  let base = vec2i(floor(at));
  let f = at - floor(at);
  let a = load_level0(base);
  let b = load_level0(base + vec2i(1, 0));
  let c = load_level0(base + vec2i(0, 1));
  let d = load_level0(base + vec2i(1, 1));
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

/// S before its floor, in the form every tile carries: (value·α, α), value encoded (D2 = 1, LT as
/// declared) or linear (D2 = 0).
@fragment
fn fs_capture(in : FullscreenOut) -> @location(0) vec4f {
  let v = sample_level0(cu.viewport.zw + in.position.xy);
  if (cu.mode.x > 0.5) {
    let straight = v.rgb / max(v.a, 1e-9);
    return vec4f(srgb_to_linear(clamp(straight, vec3f(0.0), vec3f(1.0))) * v.a, v.a);
  }
  return v;
}

/// A's initial fill over the whole group texture (R2): the captured encoded backdrop, and its
/// luma where W's would be — the rehearsal's A_out = B and W_out = B before any surface writes
/// ('body.py' 'lt_argument'). A union pixel no surface owns keeps it.
@fragment
fn fs_init(in : FullscreenOut) -> @location(0) vec4f {
  let v = sample_level0(cu.viewport.zw + in.position.xy);
  let straight = v.rgb / max(v.a, 1e-9);
  return vec4f(straight, dot(straight, vec3f(0.2126, 0.7152, 0.0722)));
}
`;

/**
 * One separable Gaussian pass along one axis, into one or two targets. With two targets the
 * pair shares a pass: the horizontal pass reads one source for both widths, the vertical pass
 * reads each width's own horizontal result. The weights and radii are the instrument's
 * (`ndimage.gaussian_filter` with `truncate = 4`). Taps outside the tile read the edge texel in
 * the clamp mode and zero in the normalised mode, `ndimage`'s `nearest` and `constant`.
 */
export function bodyLawBlurSource(targets: 1 | 2): string {
  const second = targets === 2;
  return `struct BlurData {
  /// the axis (xy); 1 for zero padding, the normalised mode (z)
  axis    : vec4f,
  /// the radius of each target's kernel (xy) and where its weights start (zw)
  taps    : vec4f,
  weights : array<f32>,
};

@group(0) @binding(0) var<storage, read> blur : BlurData;
@group(0) @binding(1) var src0 : texture_2d<f32>;
${second ? "@group(0) @binding(2) var src1 : texture_2d<f32>;\n" : ""}
fn blur_one(src : texture_2d<f32>, centre : vec2i, radius : i32, start : u32) -> vec4f {
  let dims = vec2i(textureDimensions(src));
  let axis = vec2i(i32(blur.axis.x), i32(blur.axis.y));
  let zero = blur.axis.z > 0.5;
  var sum = vec4f(0.0);
  for (var k = -radius; k <= radius; k = k + 1) {
    let t = centre + axis * k;
    let w = blur.weights[start + u32(k + radius)];
    if (zero) {
      if (all(t >= vec2i(0)) && all(t < dims)) { sum = sum + w * textureLoad(src, t, 0); }
    } else {
      sum = sum + w * textureLoad(src, clamp(t, vec2i(0), dims - vec2i(1)), 0);
    }
  }
  return sum;
}
${second ? `
struct BlurTargets {
  @location(0) near : vec4f,
  @location(1) far  : vec4f,
};

@fragment
fn fs_blur(in : FullscreenOut) -> BlurTargets {
  let centre = vec2i(floor(in.position.xy));
  var out : BlurTargets;
  out.near = blur_one(src0, centre, i32(blur.taps.x), u32(blur.taps.z));
  out.far = blur_one(src1, centre, i32(blur.taps.y), u32(blur.taps.w));
  return out;
}` : `
@fragment
fn fs_blur(in : FullscreenOut) -> @location(0) vec4f {
  return blur_one(src0, vec2i(floor(in.position.xy)), i32(blur.taps.x), u32(blur.taps.z));
}`}
`;
}

/**
 * `forward.py`'s `_blur_decimated` up to its Gaussian: the tile padded by P full-resolution
 * texels (edge texels in the clamp mode, zeros in the normalised mode), then the mean of each
 * q × q block. P is the largest any width of this q needs, a multiple of q, so the blocks are the
 * ones every width's own padding would have made and a narrower width's kernel never reaches the
 * extra rows (`body-law-pass.ts` says why).
 */
export const WGSL_BODY_LAW_DECIMATE = `struct DecimateUniforms {
  /// q (x), the padding P in full-resolution texels (y), 1 for zero padding (z)
  params : vec4f,
};

@group(0) @binding(0) var<uniform> du : DecimateUniforms;
@group(0) @binding(1) var tile : texture_2d<f32>;

@fragment
fn fs_decimate(in : FullscreenOut) -> @location(0) vec4f {
  let q = i32(du.params.x);
  let pad = i32(du.params.y);
  let zero = du.params.z > 0.5;
  let dims = vec2i(textureDimensions(tile));
  let block = vec2i(floor(in.position.xy)) * q - vec2i(pad);
  var sum = vec4f(0.0);
  for (var y = 0; y < q; y = y + 1) {
    for (var x = 0; x < q; x = x + 1) {
      let t = block + vec2i(x, y);
      if (zero) {
        if (all(t >= vec2i(0)) && all(t < dims)) { sum = sum + textureLoad(tile, t, 0); }
      } else {
        sum = sum + textureLoad(tile, clamp(t, vec2i(0), dims - vec2i(1)), 0);
      }
    }
  }
  return sum / f32(q * q);
}
`;

/**
 * **The composite into A** (§2.6, R2): one draw per law surface over its own footprint. A
 * fragment computes every law surface's circular-corner SDF and draws only where its own is the
 * smallest, the first on a tie — the rehearsal's owner rule (`body.py`'s `np.argmin`). Then:
 *
 * - σn at the pixel from the declared opacity law at its own depth, and C by the interpolation
 *   the plan names through the stored levels (`bodyLawInterpolateLevels`);
 * - W from its tile;
 * - the knee and M by `bodyLawComposite`, term for term;
 * - A = (clamp(M, 0, 1), L(W)), encoded.
 *
 * A level stored at q = 1 is read at the pixel's own texel. A decimated one is read at
 * `forward.py`'s return coordinate, (P + i + 0.5) / q − 0.5 on its grid, bilinear with the edge
 * held (`map_coordinates`, `order = 1`, `nearest`).
 */
export const WGSL_BODY_LAW_COMPOSITE = `struct LawShape {
  /// the box in device px on the plane: origin (xy), size (zw)
  rect   : vec4f,
  /// the corner radius in device px (x)
  radius : vec4f,
};

struct CompositeUniforms {
  /// the footprint's origin on the plane (xy); A's origin on the plane (zw), device px
  origins : vec4f,
  /// this surface's index (x), the number of law surfaces (y), the device ratio (z), 1 receded (w)
  surface : vec4f,
  /// the span in points (x), t (y), k_n·5·u in device px (z), the number of stored levels (w)
  law     : vec4f,
  /// λ (x), the Normal fill w (y), the hinge h (z), the knee form (w)
  knee    : vec4f,
  /// the interpolation, 0 single, 1 linear, 2 cubic (x); D2 (y); W's q (z) and padding (w)
  mode    : vec4f,
  sigma0  : vec4f,
  sigma1  : vec4f,
  q0      : vec4f,
  q1      : vec4f,
  pad0    : vec4f,
  pad1    : vec4f,
};

@group(0) @binding(0) var<uniform> lu : CompositeUniforms;
@group(0) @binding(1) var<storage, read> shapes : array<LawShape>;
@group(0) @binding(2) var level0 : texture_2d<f32>;
@group(0) @binding(3) var level1 : texture_2d<f32>;
@group(0) @binding(4) var level2 : texture_2d<f32>;
@group(0) @binding(5) var level3 : texture_2d<f32>;
@group(0) @binding(6) var level4 : texture_2d<f32>;
@group(0) @binding(7) var level5 : texture_2d<f32>;
@group(0) @binding(8) var level6 : texture_2d<f32>;
@group(0) @binding(9) var wide : texture_2d<f32>;

fn law_sdf(p : vec2f, shape : LawShape) -> f32 {
  let half = shape.rect.zw * 0.5;
  let centre = shape.rect.xy + half;
  let radius = min(shape.radius.x, min(half.x, half.y));
  let q = abs(p - centre) - half + vec2f(radius);
  return length(max(q, vec2f(0.0))) + min(max(q.x, q.y), 0.0) - radius;
}

fn clamped_load(t : texture_2d<f32>, texel : vec2i) -> vec4f {
  let dims = vec2i(textureDimensions(t));
  return textureLoad(t, clamp(texel, vec2i(0), dims - vec2i(1)), 0);
}

fn level_texel(k : u32, texel : vec2i) -> vec4f {
  switch k {
    case 0u: { return clamped_load(level0, texel); }
    case 1u: { return clamped_load(level1, texel); }
    case 2u: { return clamped_load(level2, texel); }
    case 3u: { return clamped_load(level3, texel); }
    case 4u: { return clamped_load(level4, texel); }
    case 5u: { return clamped_load(level5, texel); }
    case 6u: { return clamped_load(level6, texel); }
    default: { return clamped_load(wide, texel); }
  }
}

fn level_sigma(k : u32) -> f32 {
  if (k < 4u) { return lu.sigma0[k]; }
  return lu.sigma1[k - 4u];
}

/// The value a stored tile holds at the footprint pixel i, weight divided out. k = 7 is W.
fn tile_value(k : u32, i : vec2i) -> vec3f {
  var q = lu.mode.z;
  var pad = lu.mode.w;
  if (k < 4u) { q = lu.q0[k]; pad = lu.pad0[k]; }
  else if (k < 7u) { q = lu.q1[k - 4u]; pad = lu.pad1[k - 4u]; }
  var v : vec4f;
  if (q < 1.5) {
    v = level_texel(k, i);
  } else {
    let at = (vec2f(i) + vec2f(pad + 0.5)) / q - vec2f(0.5);
    let base = vec2i(floor(at));
    let f = at - floor(at);
    let a = level_texel(k, base);
    let b = level_texel(k, base + vec2i(1, 0));
    let c = level_texel(k, base + vec2i(0, 1));
    let d = level_texel(k, base + vec2i(1, 1));
    v = mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }
  return v.rgb / max(v.a, 1e-9);
}

/// The declared opacity o(s, d, pose) ('bodyLawOpacity'), d in points.
fn law_opacity(d : f32) -> f32 {
  let t = lu.law.y;
  if (lu.surface.w > 0.5) { return 0.4 + 0.4 * t; }
  let centre = -lu.law.x * 0.5;
  if (d <= centre) { return 0.8 * t; }
  if (d <= -1.0) { return 0.8 * t + (0.4 * t - 0.8 * t) * ((d - centre) / (-1.0 - centre)); }
  if (d <= 0.0) { return 0.4 * t + (0.5 - 0.4 * t) * ((d + 1.0) / 1.0); }
  return 0.5;
}

/// C at the footprint pixel i for a width sigma ('bodyLawInterpolateLevels').
fn narrow_at(sigma : f32, i : vec2i) -> vec3f {
  let n = u32(lu.law.w);
  if (lu.mode.x < 0.5 || n == 1u) { return tile_value(0u, i); }
  let s = clamp(sigma, level_sigma(0u), level_sigma(n - 1u));
  var upper = 0u;
  loop {
    if (upper >= n || level_sigma(upper) >= s) { break; }
    upper = upper + 1u;
  }
  if (lu.mode.x < 1.5 || n < 4u) {
    let k = u32(clamp(i32(upper) - 1, 0, i32(n) - 2));
    let a = level_sigma(k);
    let b = level_sigma(k + 1u);
    let w = (s - a) / (b - a);
    let va = tile_value(k, i);
    return clamp(va + w * (tile_value(k + 1u, i) - va), vec3f(0.0), vec3f(1.0));
  }
  let start = u32(clamp(i32(upper) - 2, 0, i32(n) - 4));
  var out = vec3f(0.0);
  for (var j = 0u; j < 4u; j = j + 1u) {
    var wj = 1.0;
    let xj = level_sigma(start + j);
    for (var m = 0u; m < 4u; m = m + 1u) {
      if (m != j) {
        let xm = level_sigma(start + m);
        wj = wj * (s - xm) / (xj - xm);
      }
    }
    out = out + wj * tile_value(start + j, i);
  }
  return clamp(out, vec3f(0.0), vec3f(1.0));
}

fn law_luma(c : vec3f) -> f32 {
  return dot(c, vec3f(0.2126, 0.7152, 0.0722));
}

@fragment
fn fs_composite(in : FullscreenOut) -> @location(0) vec4f {
  let texel = lu.origins.zw + floor(in.position.xy);
  let p = texel + vec2f(0.5);
  let own = u32(lu.surface.x);
  let count = u32(lu.surface.y);
  var owner = 0u;
  var best = law_sdf(p, shapes[0]);
  var mine = best;
  for (var j = 1u; j < count; j = j + 1u) {
    let dj = law_sdf(p, shapes[j]);
    if (j == own) { mine = dj; }
    if (dj < best) { best = dj; owner = j; }
  }
  if (owner != own) { discard; }
  let i = vec2i(texel - lu.origins.xy);

  let depthPt = mine / lu.surface.z;
  let C = narrow_at(lu.law.z * law_opacity(depthPt), i);
  let W = tile_value(7u, i);

  let lam = lu.knee.x;
  let w = lu.knee.y;
  let h = lu.knee.z;
  var M : vec3f;
  if (lu.knee.w < 0.5) {
    let N = C + h * lam * max(vec3f(0.0), h * (W - C));
    M = (1.0 - w) * N + w * W;
  } else if (lu.knee.w < 1.5) {
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
  if (lu.mode.y > 0.5) {
    return vec4f(clamp(M, vec3f(0.0), vec3f(1.0)), law_luma(W));
  }
  // D2 = 0: C and W were averaged in linear light, and A is encoded here (the rejected F2).
  let We = linear_to_srgb(clamp(W, vec3f(0.0), vec3f(1.0)));
  return vec4f(linear_to_srgb(clamp(M, vec3f(0.0), vec3f(1.0))), law_luma(We));
}
`;
