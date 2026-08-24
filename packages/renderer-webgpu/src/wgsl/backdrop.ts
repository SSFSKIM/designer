/**
 * Backdrop import and the blur pyramid.
 *
 * ## Import (X3, X5)
 *
 * One pass normalises every source kind into level 0 of the pyramid:
 * **premultiplied, linear-light, sRGB-primaries `rgba16float`**. The three
 * things that differ between providers — encoding, alpha mode, colour space —
 * arrive as uniforms resolved on the CPU, where the provider's contract is
 * known, so no shader ever guesses at them. That is what X3's "the compositor
 * normalizes at import" means operationally: imported video is unpremultiplied
 * and copied images are premultiplied, and after this pass neither fact is
 * visible downstream.
 *
 * The unpremultiply happens *before* the transfer-function decode and the
 * re-premultiply *after* it. Decoding a premultiplied value is meaningless — the
 * curve is not linear, so `decode(c·a) != decode(c)·a` — and getting that order
 * wrong shows up as dark fringes on every soft edge.
 *
 * ## The chain
 *
 * Progressive downsample, 13 taps per level, sampled bilinearly so the 13 taps
 * cover a 4×4 footprint. This is the standard bloom-pyramid filter, and it is
 * here for the reason it exists there: it is the cheapest filter whose repeated
 * application does not produce the boxy, aliasing-prone result a naive 2×2 average
 * gives, and it is one pass per level rather than the three a
 * downsample-then-separable-blur chain needs.
 *
 * With `mipmapFilter: "linear"` on the sampler, `textureSampleLevel(chain, s, uv,
 * lod)` is then a continuously variable blur — which is exactly what the optics
 * pass needs for "LOD by thickness/size".
 *
 * ## The body blur
 *
 * The chain gives blur in powers of two. The material's own σ is not a power of
 * two, so the body — the large, flat region of frost behind a surface — gets one
 * dedicated separable Gaussian at the residual σ on top of the nearest chain
 * level. Two passes for the whole scene, not two per level: the refraction path
 * has no use for it, because a rim sample wants the sharpest level it can get.
 */

/**
 * `srcEncoded`: 1 when the sampled values are sRGB-encoded (every 8-bit copy and
 * every external video texture), 0 when they are already linear (an app-supplied
 * float view can be either, so the provider declares it).
 *
 * `alphaMode`: 0 premultiplied, 1 unpremultiplied, 2 opaque — the enumeration
 * `alphaNormalisationMode` in `color.ts` produces.
 */
export const WGSL_IMPORT_PASS = `struct ImportUniforms {
  m0     : vec4f,   // colour matrix row 0 (xyz), srcEncoded (w)
  m1     : vec4f,   // row 1 (xyz), alphaMode (w)
  m2     : vec4f,   // row 2 (xyz), unused (w)
  fit    : vec4f,   // uv scale (xy), uv offset (zw) — the source's fit into the target
};

@group(0) @binding(0) var<uniform> iu : ImportUniforms;
@group(0) @binding(1) var srcSampler : sampler;
@group(0) @binding(2) var srcTexture : SRC_TEXTURE_TYPE;

fn sample_src(uv : vec2f) -> vec4f {
  return SRC_SAMPLE_EXPR;
}

@fragment
fn fs_import(in : FullscreenOut) -> @location(0) vec4f {
  let uv = in.uv * iu.fit.xy + iu.fit.zw;
  var raw = sample_src(clamp(uv, vec2f(0.0), vec2f(1.0)));

  let alphaMode = iu.m1.w;
  var alpha = raw.a;
  var colour = raw.rgb;

  if (alphaMode > 1.5) {
    alpha = 1.0;
  } else if (alphaMode > 0.5) {
    // Already unpremultiplied: nothing to undo.
  } else {
    // Premultiplied input — undo it before the non-linear decode. A fully
    // transparent texel carries zero colour, so the floored divide returns zero
    // there without a branch.
    colour = colour / max(alpha, 1e-6);
  }

  if (iu.m0.w > 0.5) {
    colour = srgb_to_linear(clamp(colour, vec3f(0.0), vec3f(1.0)));
  }

  // Colour-space conversion in linear light. Identity for sRGB sources.
  colour = vec3f(dot(iu.m0.xyz, colour), dot(iu.m1.xyz, colour), dot(iu.m2.xyz, colour));

  return vec4f(max(colour, vec3f(0.0)) * alpha, alpha);
}`;

/** `SRC_TEXTURE_TYPE`/`SRC_SAMPLE_EXPR` per source kind. */
export function importPassSource(kind: "sampled" | "external"): string {
  const type = kind === "external" ? "texture_external" : "texture_2d<f32>";
  const expr =
    kind === "external"
      ? "textureSampleBaseClampToEdge(srcTexture, srcSampler, uv)"
      : "textureSampleLevel(srcTexture, srcSampler, uv, 0.0)";
  return WGSL_IMPORT_PASS.replace("SRC_TEXTURE_TYPE", type).replace("SRC_SAMPLE_EXPR", expr);
}

/**
 * 13-tap progressive downsample. Offsets are in the SOURCE level's texels; the
 * caller passes `1 / srcSize` so the pass needs no texture-dimension query.
 */
export const WGSL_DOWNSAMPLE_PASS = `struct ChainUniforms {
  texel : vec4f,   // 1/srcSize (xy), unused (zw)
  params : vec4f,  // sigma in texels (x), direction (yz), unused (w)
};

@group(0) @binding(0) var<uniform> cu : ChainUniforms;
@group(0) @binding(1) var chainSampler : sampler;
@group(0) @binding(2) var chainTexture : texture_2d<f32>;

fn tap(uv : vec2f, o : vec2f) -> vec4f {
  return textureSampleLevel(chainTexture, chainSampler, uv + o * cu.texel.xy, 0.0);
}

@fragment
fn fs_downsample(in : FullscreenOut) -> @location(0) vec4f {
  let uv = in.uv;

  let a = tap(uv, vec2f(-2.0,  2.0));
  let b = tap(uv, vec2f( 0.0,  2.0));
  let c = tap(uv, vec2f( 2.0,  2.0));
  let d = tap(uv, vec2f(-2.0,  0.0));
  let e = tap(uv, vec2f( 0.0,  0.0));
  let f = tap(uv, vec2f( 2.0,  0.0));
  let g = tap(uv, vec2f(-2.0, -2.0));
  let h = tap(uv, vec2f( 0.0, -2.0));
  let i = tap(uv, vec2f( 2.0, -2.0));
  let j = tap(uv, vec2f(-1.0,  1.0));
  let k = tap(uv, vec2f( 1.0,  1.0));
  let l = tap(uv, vec2f(-1.0, -1.0));
  let m = tap(uv, vec2f( 1.0, -1.0));

  // Weights: the centre cross carries 0.5 across four inner taps, the corners
  // and edges the remaining 0.5. Sums to exactly 1, so the chain neither gains
  // nor loses energy — which is what keeps the analysis pass's luminance honest
  // however many levels it reads through.
  var out = (j + k + l + m) * 0.5 * 0.25;
  out = out + (a + b + d + e) * 0.125 * 0.25;
  out = out + (b + c + e + f) * 0.125 * 0.25;
  out = out + (d + e + g + h) * 0.125 * 0.25;
  out = out + (e + f + h + i) * 0.125 * 0.25;
  return out;
}

/// Separable Gaussian, nine taps, run once horizontally and once vertically to
/// take the nearest chain level up to the material's exact sigma.
@fragment
fn fs_blur(in : FullscreenOut) -> @location(0) vec4f {
  let dir = cu.params.yz;
  let sigma = max(cu.params.x, 1e-4);
  let inv = -0.5 / (sigma * sigma);

  var sum = vec4f(0.0);
  var weight = 0.0;
  for (var t = -4; t <= 4; t = t + 1) {
    let ft = f32(t);
    let w = exp(ft * ft * inv);
    sum = sum + textureSampleLevel(chainTexture, chainSampler, in.uv + dir * ft * cu.texel.xy, 0.0) * w;
    weight = weight + w;
  }
  return sum / weight;
}`;
