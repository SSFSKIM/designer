/**
 * Shared WGSL: the colour pipeline (X5) and the fullscreen-triangle vertex stage
 * every pass here uses.
 *
 * The marker comment on the first line is load-bearing beyond documentation:
 * `packages/core/test/bundle-shape.test.ts` greps built chunks for it to prove
 * that WGSL reaches exactly one lazily-imported chunk and never core's entry
 * chunk (X7). Keep it in a module every pass pulls in, and keep it spelled
 * exactly as it is.
 */

export const WGSL_PRELUDE = `// vitrea:wgsl-marker
// ---------------------------------------------------------------------------
// X5 colour pipeline. Piecewise sRGB, matching color.ts channel for channel:
// a golden regenerated against one and asserted against the other must not
// drift by a code unit, so the 2.2-gamma approximation is not used anywhere.
// ---------------------------------------------------------------------------

fn srgb_to_linear(c : vec3f) -> vec3f {
  let lo = c / 12.92;
  let hi = pow((c + vec3f(0.055)) / 1.055, vec3f(2.4));
  return select(hi, lo, c <= vec3f(0.04045));
}

fn linear_to_srgb(c : vec3f) -> vec3f {
  let lo = c * 12.92;
  let hi = 1.055 * pow(max(c, vec3f(0.0)), vec3f(1.0 / 2.4)) - vec3f(0.055);
  return select(hi, lo, c <= vec3f(0.0031308));
}

/// Rec.709 weights on LINEAR light. Weighting encoded values would make the
/// analysis pass measure something that is not energy.
fn luminance(linear : vec3f) -> f32 {
  return dot(linear, vec3f(0.2126, 0.7152, 0.0722));
}

/// The one output encoding: encode, then premultiply in the ENCODED space,
/// because that is the space the browser composites a canvas in. Premultiplying
/// in linear and encoding afterwards darkens every partially covered pixel.
fn encode_output(linear : vec3f, alpha : f32) -> vec4f {
  let a = clamp(alpha, 0.0, 1.0);
  return vec4f(linear_to_srgb(linear) * a, a);
}

// ---------------------------------------------------------------------------
// Fullscreen triangle. Three vertices, no vertex buffer, no index buffer: the
// oversized triangle is clipped to the target and costs one fewer primitive
// than a quad, and every pass here writes exactly one screen-space region.
// ---------------------------------------------------------------------------

struct FullscreenOut {
  @builtin(position) position : vec4f,
  @location(0)       uv       : vec2f,
};

@vertex
fn vs_fullscreen(@builtin(vertex_index) index : u32) -> FullscreenOut {
  // (-1,-1) (3,-1) (-1,3) in clip space; uv follows with y flipped so (0,0) is
  // the target's top-left, matching texture and viewport conventions.
  let x = f32((index << 1u) & 2u) * 2.0 - 1.0;
  let y = f32(index & 2u) * 2.0 - 1.0;
  var out : FullscreenOut;
  out.position = vec4f(x, y, 0.0, 1.0);
  out.uv = vec2f((x + 1.0) * 0.5, (1.0 - y) * 0.5);
  return out;
}
`;
