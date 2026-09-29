// UNAPPLIED PROPOSAL. These functions assume three NEW E3-owned vec4s in
// OpticsUniforms: bodyE3 (strength,g0,g1,g2), bodyE3Neutral0 (F0..F3),
// bodyE3Neutral1 (F4..F6,padding). No existing uniform lane is reassigned.
// Input/output are ENCODED sRGB codes, not linear luminance or OKLab.
// This is only B1/E3. No fitted spatial, angular, size, or stroke term exists.

fn body_e3_neutral(level : f32) -> f32 {
  let knots = array<f32, 7>(40.0, 56.0, 72.0, 88.0, 104.0, 128.0, 150.0);
  let values = array<f32, 7>(ou.bodyE3Neutral0.x, ou.bodyE3Neutral0.y,
    ou.bodyE3Neutral0.z, ou.bodyE3Neutral0.w, ou.bodyE3Neutral1.x,
    ou.bodyE3Neutral1.y, ou.bodyE3Neutral1.z);
  var i = 0u;
  for (var j = 1u; j < 6u; j = j + 1u) {
    if (level >= knots[j]) { i = j; }
  }
  // Deliberately NOT clamped t: the first/last segment continues outside
  // the measured knots; only the resulting neutral ordinate is clipped.
  let t = (level - knots[i]) / (knots[i + 1u] - knots[i]);
  return clamp(mix(values[i], values[i + 1u], t), 0.0, 255.0);
}

fn body_e3_codes(encoded : vec3f) -> vec3f {
  let level = dot(encoded, vec3f(0.2126, 0.7152, 0.0722));
  var chroma = encoded - vec3f(level);
  // Matches body41.linear_design's explicit achromatic zero despite an ulp
  // left by the rounded luminance weights on some GPU arithmetic paths.
  if (encoded.x == encoded.y && encoded.y == encoded.z) { chroma = vec3f(0.0); }
  var gain = mix(ou.bodyE3.y, ou.bodyE3.z, clamp((level - 63.0) / 30.0, 0.0, 1.0));
  if (level > 93.0) {
    gain = mix(ou.bodyE3.z, ou.bodyE3.w, clamp((level - 93.0) / 25.0, 0.0, 1.0));
  }
  return clamp(vec3f(body_e3_neutral(level)) + gain * chroma,
    vec3f(0.0), vec3f(255.0));
}

// Proposed insertion: immediately AFTER body_chroma_retention(), BEFORE the
// DOM/layer branch and author tint. Gate 1 REPLACES the untinted composite;
// it does not add another retention or run the old neutral/tone solve again.
//
// PENDING PARENT RULING: effective policy/variant guard and presence extension.
// No callsite is executable until those choices and baseline freeze are recorded.
//
// if (ou.bodyE3.x > 0.0 && ou.flags.x > 0.5 && mat > 0.0) {
//   let encoded = linear_to_srgb(backdrop) * 255.0;
//   let target = srgb_to_linear(body_e3_codes(encoded) / 255.0);
//   let presentTarget = mix(backdrop, target, vec3f(mat));
//   colour = mix(colour, presentTarget, vec3f(ou.bodyE3.x));
// }
//
// Gate zero skips this block completely: existing colour, bodyAlpha, tint, rim,
// lens, shadow and output arithmetic execute unchanged. Sampled backdrop here
// already includes the existing refraction, blur/scatter mix and presence blur
// fade; this proposal changes no sampling coordinates or blur kernel.
