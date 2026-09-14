import { WGSL_FIELD_KERNELS } from "./field";
import { WGSL_PRELUDE } from "./prelude";

/** W28: reduce raw level-zero pixels, encoding EACH RGB before the Rec.709 sum.
 * Encoding a linear-light mip mean instead measures a different abscissa (Jensen's inequality).
 * The mask is G0's circular rounded rectangle, not the optical field's continuous shoulder.
 * Samples are full-resolution device-pixel centres; the field governor never thins this grid.
 */
export const silhouetteReductionModule = (): string => `${WGSL_PRELUDE}
struct ToneShape { rect : vec4f, radius : vec4f };
struct ToneStat { colour : vec4f, stats : vec4f };
struct ToneUniforms { viewport : vec4f, fit : vec4f };
@group(0) @binding(0) var<uniform> u : ToneUniforms;
@group(0) @binding(1) var source : texture_2d<f32>;
@group(0) @binding(3) var<storage, read> shapes : array<ToneShape>;
@group(0) @binding(4) var<storage, read_write> tones : array<ToneStat>;
var<workgroup> sums : array<vec4f, 256>;
var<workgroup> counts : array<f32, 256>;
var<workgroup> weights : array<f32, 256>;
struct RawTone { value : vec4f, alpha : f32 };

fn raw_tone(texel : vec2i) -> RawTone {
  let dims = vec2i(textureDimensions(source));
  let rgba = textureLoad(source, clamp(texel, vec2i(0), dims - 1), 0);
  let rgb = rgba.rgb / max(rgba.a, 1e-6);
  return RawTone(vec4f(rgb, dot(linear_to_srgb(rgb), vec3f(0.2126, 0.7152, 0.0722))) * rgba.a, rgba.a);
}

@compute @workgroup_size(256)
fn reduce_tone(@builtin(local_invocation_index) lane : u32,
               @builtin(workgroup_id) group : vec3u) {
  let shape = shapes[group.x];
  // G0 clips to the capture raster. Clip BEFORE deriving the iteration area so
  // offscreen geometry cannot create unbounded work or overflow its u32 product.
  // In-bounds rectangles retain exactly the same lane assignment and arithmetic.
  let lo = vec2i(clamp(floor(shape.rect.xy), vec2f(0.0), u.viewport.xy));
  let hi = vec2i(clamp(ceil(shape.rect.xy + shape.rect.zw), vec2f(0.0), u.viewport.xy));
  let extent = vec2u(max(hi - lo, vec2i(0)));
  let half = shape.rect.zw * 0.5;
  let centre = shape.rect.xy + half;
  let radius = min(shape.radius.x, min(half.x, half.y));
  var sum = vec4f(0.0);
  var count = 0.0;
  var weight = 0.0;
  for (var i = lane; i < extent.x * extent.y; i += 256u) {
    let pixel = lo + vec2i(vec2u(i % extent.x, i / extent.x));
    let p = vec2f(pixel) + 0.5;
    let q = abs(p - centre) - half + radius;
    let distance = length(max(q, vec2f(0.0))) + min(max(q.x, q.y), 0.0) - radius;
    if (distance > 0.0) { continue; }
    let uv = (p / u.viewport.xy) * u.fit.xy + u.fit.zw;
    // Interpolate encoded and linear statistics separately. Encoding after
    // bilinear filtering would reintroduce a Jensen gap on a scaled source.
    let at = uv * vec2f(textureDimensions(source)) - 0.5;
    let base = vec2i(floor(at));
    let f = fract(at);
    let a = raw_tone(base);
    let b = raw_tone(base + vec2i(1, 0));
    let c = raw_tone(base + vec2i(0, 1));
    let d = raw_tone(base + vec2i(1, 1));
    sum += mix(mix(a.value, b.value, f.x), mix(c.value, d.value, f.x), f.y);
    weight += mix(mix(a.alpha, b.alpha, f.x), mix(c.alpha, d.alpha, f.x), f.y);
    count += 1.0;
  }
  sums[lane] = sum;
  counts[lane] = count;
  weights[lane] = weight;
  workgroupBarrier();
  for (var stride = 128u; stride > 0u; stride /= 2u) {
    if (lane < stride) {
      sums[lane] += sums[lane + stride];
      counts[lane] += counts[lane + stride];
      weights[lane] += weights[lane + stride];
    }
    workgroupBarrier();
  }
  if (lane == 0u) {
    let mean = sums[0] / max(weights[0], 1e-6);
    let level = srgb_to_linear(vec3f(mean.w)).x;
    tones[group.x].colour = vec4f(mean.rgb, level);
    tones[group.x].stats = vec4f(mean.w, luminance(mean.rgb), counts[0], weights[0]);
  }
}
`;

/** A separate field avoids exceeding WebGPU's 32-byte colour-attachment budget.
 * The same geometry kernels and union fold carry all four reference channels through a seam.
 * No nearest-member shortcut: merged members retain their own colour AND encoded level.
 */
export const silhouetteFieldModule = (family: "rsupn" | "rsup"): string => `${WGSL_PRELUDE}
${WGSL_FIELD_KERNELS}
struct FieldUniforms { screen : vec4f, unionP : vec4f, counts : vec4u, fallback : vec4f };
struct ToneStat { colour : vec4f, stats : vec4f };
@group(0) @binding(0) var<uniform> u : FieldUniforms;
@group(0) @binding(1) var<storage, read> instances : array<Instance>;
@group(0) @binding(2) var<storage, read> tones : array<ToneStat>;
fn member_distance(i : u32, p : vec2f) -> f32 {
  let s = instances[i];
  return ${family === "rsupn" ? "sd_rsupn_grad" : "sd_rsup_grad"}(
    p - s.centre, s.half, s.re, vec4f(s.k0, s.k1, s.k2, s.k3), s.k4).d + s.inset;
}
fn member_tone(i : u32) -> vec4f {
  return select(u.fallback, tones[i].colour, tones[i].stats.w > 0.0);
}
@fragment
fn fs_tone(in : FullscreenOut) -> @location(0) vec4f {
  let p = in.uv * u.screen.xy * u.screen.z;
  var distance = member_distance(0u, p);
  var colour = member_tone(0u);
  for (var i = 1u; i < u.counts.x; i += 1u) {
    let blend = union_blend(distance, member_distance(i, p), u.unionP.xyz);
    distance = blend.x;
    colour = mix(member_tone(i), colour, blend.y);
  }
  return colour;
}
`;
