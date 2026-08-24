/**
 * The highlight pass: specular sweep and press glow.
 *
 * X1 puts this canvas **above** the semantic host DOM, which is the whole reason
 * it is a separate pass and not three more lines in the optics shader: a
 * highlight has to fall across the label, and the label is real DOM sitting
 * between the two canvases. Nothing else about the material does.
 *
 * Both effects are driven by motion-driver *outputs*, never by time (§Motion —
 * the renderer consumes driver values as data):
 *
 *  - **`sweep`** ∈ [0, 1] is the shimmer's position along the rim. The band is a
 *    Gaussian in the angular coordinate of the gradient, so it travels around the
 *    contour rather than sliding across a bounding box, and it exists only where
 *    the rim exists. Reduced Motion sets `shimmer: "none"`, which the CPU turns
 *    into a zero gain — the band is not drawn stationary, it is not drawn.
 *  - **`glow`** ∈ [0, 1] is the press illumination, from the fast-attack /
 *    slow-decay driver. It arrives **per pixel**, unioned through the field pass,
 *    multiplied by a radial falloff around the press point and clipped to the
 *    surface's coverage so it never leaks past the material's edge.
 *
 * The sweep phase and the press *point* are per group rather than per surface:
 * there is one pointer, and a sweep travelling around a `GlassEffectContainer`'s
 * unioned contour is the behaviour the container exists to produce. v1's
 * components never register two simultaneous presses inside one group.
 *
 * Output is additive over the page: premultiplied with the glow's own alpha, so a
 * zero-intensity highlight writes nothing at all rather than a transparent black
 * that a wrong blend state could darken with.
 */

export const WGSL_HIGHLIGHT_PASS = `struct HighlightUniforms {
  /// viewport size in device px (xy), CSS px per device px (z), unused (w)
  target : vec4f,
  /// sweep position 0..1 (x), band width in radians (y), sweep gain (z), rim width px (w)
  sweep : vec4f,
  /// press point in viewport CSS px (xy), glow radius px (z), glow gain (w)
  glow : vec4f,
  /// highlight colour, linear light (xyz), unused (w)
  colour : vec4f,
  /// fieldSize.xy, unused (zw)
  flags : vec4f,
};

@group(0) @binding(0) var<uniform> hu : HighlightUniforms;
@group(0) @binding(1) var fieldTexture : texture_2d<f32>;
@group(0) @binding(2) var auxTexture : texture_2d<f32>;

const TAU = 6.283185307179586;

/// Shortest angular distance, so the band wraps continuously past the seam
/// instead of stalling there for one revolution.
fn angle_delta(a : f32, b : f32) -> f32 {
  let raw = abs(a - b);
  return min(raw, TAU - raw);
}

@fragment
fn fs_highlight(in : FullscreenOut) -> @location(0) vec4f {
  let texel = vec2i(in.uv * hu.flags.xy);
  let field = textureLoad(fieldTexture, texel, 0);
  let aux = textureLoad(auxTexture, texel, 0);
  let d = field.x;
  let normal = field.yz;
  let coverage = field.w;

  if (coverage <= 0.0) {
    return vec4f(0.0);
  }

  // Specular sweep: a travelling band in the rim's angular coordinate.
  let rim = clamp(1.0 - abs(d) / max(hu.sweep.w, 1e-4), 0.0, 1.0);
  let theta = atan2(normal.y, normal.x) + TAU * 0.5;
  let target = hu.sweep.x * TAU;
  let width = max(hu.sweep.y, 1e-4);
  let band = exp(-pow(angle_delta(theta, target) / width, 2.0));
  let sweep = rim * rim * band * hu.sweep.z;

  // Press glow: radial, in CSS px, clipped by coverage so it cannot leak past
  // the material's edge.
  let posCss = in.position.xy * hu.target.z;
  let dist = length(posCss - hu.glow.xy);
  let radial = clamp(1.0 - dist / max(hu.glow.z, 1e-4), 0.0, 1.0);
  // 'aux.y' is the per-pixel glow channel, unioned in the field pass, so a group
  // whose members glow independently does not need a pass each.
  let press = radial * radial * hu.glow.w * aux.y;

  let intensity = clamp(sweep + press, 0.0, 1.0) * coverage;
  if (intensity <= 0.0) {
    return vec4f(0.0);
  }
  return encode_output(hu.colour.rgb, intensity);
}`;
