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
  screen : vec4f,
  /// sweep position 0..1 (x), band width in radians (y), sweep gain (z), rim width px (w)
  sweep : vec4f,
  /// press point in viewport CSS px (xy), glow radius px (z), glow gain (w)
  glow : vec4f,
  /// highlight colour, linear light (xyz), unused (w)
  colour : vec4f,
  /// fieldSize.xy, fieldUpsampled (z), unused (w)
  flags : vec4f,
  /// backdrop tone adaptation (W7), exactly as the optics pass takes it:
  /// backdropToneLow, backdropToneHigh, the size bias already divided by the
  /// accessibility refraction cap, and the resolved strength — zero where there
  /// is no measured backdrop tone, which stands the fade down
  toneAdapt : vec4f,
  /// the backdrop source's own average luminance (x); yzw unused
  toneLevel : vec4f,
  /// this pass's uv into the FIELD texture's uv: scale (xy), offset (zw).
  ///
  /// The identity for a pass whose scissor is the field's own rect, and not the
  /// identity since W8: the outer shadow made the field rect much larger than
  /// anything this pass draws in, so the highlight is scoped back to the rect it
  /// had before and reads the field through this remap instead. Derived from the
  /// two rects by highlightPass in passes.ts.
  fieldFit : vec4f,
};

@group(0) @binding(0) var<uniform> hu : HighlightUniforms;
@group(0) @binding(1) var fieldTexture : texture_2d<f32>;
@group(0) @binding(2) var auxTexture : texture_2d<f32>;
@group(0) @binding(3) var fieldSampler : sampler;

const TAU = 6.283185307179586;

/// Shortest angular distance, so the band wraps continuously past the seam
/// instead of stalling there for one revolution.
fn angle_delta(a : f32, b : f32) -> f32 {
  let raw = abs(a - b);
  return min(raw, TAU - raw);
}

@fragment
fn fs_highlight(in : FullscreenOut) -> @location(0) vec4f {
  // Exact load nominally; filtered when the governor's resolution knob had the
  // field rasterised below the group's rect. The sweep rides the rim, which is
  // the one place a nearest read of a coarse field would show its grid.
  let fieldUv = in.uv * hu.fieldFit.xy + hu.fieldFit.zw;
  var field : vec4f;
  var aux : vec4f;
  if (hu.flags.z > 0.5) {
    field = textureSampleLevel(fieldTexture, fieldSampler, fieldUv, 0.0);
    aux = textureSampleLevel(auxTexture, fieldSampler, fieldUv, 0.0);
  } else {
    let texel = vec2i(fieldUv * hu.flags.xy);
    field = textureLoad(fieldTexture, texel, 0);
    aux = textureLoad(auxTexture, texel, 0);
  }
  let d = field.x;
  let normal = field.yz;
  let coverage = field.w;

  if (coverage <= 0.0) {
    return vec4f(0.0);
  }

  // Specular sweep: a travelling band in the rim's angular coordinate.
  let rim = clamp(1.0 - abs(d) / max(hu.sweep.w, 1e-4), 0.0, 1.0);
  let theta = atan2(normal.y, normal.x) + TAU * 0.5;
  let centre = hu.sweep.x * TAU;
  let width = max(hu.sweep.y, 1e-4);
  let band = exp(-pow(angle_delta(theta, centre) / width, 2.0));
  let sweep = rim * rim * band * hu.sweep.z;

  // Press glow: radial, in CSS px, clipped by coverage so it cannot leak past
  // the material's edge.
  let posCss = in.position.xy * hu.screen.z;
  let dist = length(posCss - hu.glow.xy);
  let radial = clamp(1.0 - dist / max(hu.glow.z, 1e-4), 0.0, 1.0);
  // 'aux.y' is the per-pixel glow channel, unioned in the field pass, so a group
  // whose members glow independently does not need a pass each.
  let press = radial * radial * hu.glow.w * aux.y;

  /*
   * Backdrop tone adaptation (W7) fades this pass with the rest of the surface's
   * own appearance. A highlight is the material catching light, and a material
   * that has taken its backdrop's tone is not there to catch any — the settled
   * reference's capsule over a near-black backdrop is byte-identical to that
   * background, sweep included.
   *
   * The curve is the optics pass's, evaluated the same way off the same uniforms
   * and the same per-pixel 'sizeK', because two statements of one curve is how
   * they drift. This pass would otherwise have gone on drawing a bright crescent
   * around a surface the optics pass had made invisible — measured at 60 pixels
   * past 2/255, peaking at 97/255, on exactly that cell.
   */
  let sizeK = clamp(aux.z, 0.0, 1.0);
  var toneAdapt = 0.0;
  if (hu.toneAdapt.w > 0.0) {
    let toneX = hu.toneLevel.x + hu.toneAdapt.z * sizeK;
    let toneT = clamp(
      (toneX - hu.toneAdapt.x) / max(hu.toneAdapt.y - hu.toneAdapt.x, 1e-6),
      0.0,
      1.0,
    );
    toneAdapt = clamp(hu.toneAdapt.w, 0.0, 1.0) * (1.0 - toneT * toneT * (3.0 - 2.0 * toneT));
  }

  let intensity = clamp(sweep + press, 0.0, 1.0) * coverage * (1.0 - toneAdapt);
  if (intensity <= 0.0) {
    return vec4f(0.0);
  }
  return encode_output(hu.colour.rgb, intensity);
}`;
