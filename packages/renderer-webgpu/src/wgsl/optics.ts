/**
 * The optics pass: refraction, adaptive tint, inner shadow, rim and specular —
 * the glass body.
 *
 * Reads the group's two field targets (value + unit normal + coverage, and the
 * per-surface optical scalars) and the backdrop pyramid; writes premultiplied sRGB
 * into the optics canvas over the group's rect. Everything optical happens in
 * linear light and is encoded exactly once, on the way out (X5).
 *
 * The pass is scoped, not fullscreen: the render pass sets its viewport *and* its
 * scissor to the group's device-pixel rect, so `in.uv` runs 0..1 over the group
 * and indexes the group's own field textures one-to-one, while `in.position.xy`
 * stays in canvas device pixels and gives the backdrop coordinate. Nothing outside
 * the group's bounds is touched — §Performance envelope prices the field and
 * optics passes on exactly that assumption.
 *
 * ## The size law, and the four things it moves
 *
 * Parent acceptance #2 asks for the *mechanism*, not a look: "a larger surface
 * shows deeper shadow and stronger lensing than a small button over the same
 * backdrop." Apple states it as one mechanism with four consequences — a larger
 * surface "casts deeper, richer shadows, has more pronounced lensing and
 * refraction effects, and a softer scattering of light" (S219), and "a larger
 * size is more opaque. A smaller size is clearer" (S284) — so this pass reads one
 * per-pixel number and applies four gains to it.
 *
 * The number is `aux.z`, `material.ts`'s `sizeThickness(span)`, resolved per
 * surface on the CPU and carried **per pixel** through the field pass's union.
 * That is what lets a 40 px button and a 320 px platter share one group's field
 * pass and still read as different thicknesses. The lens's share of it arrives
 * pre-folded, because it is a length rather than a gain:
 *
 * ```
 * lensDepthPx = min(thickness * lensSizeGain(span), span / 2)
 * ```
 *
 * The clamp is what keeps a small control from being all lens: a 24 px-tall
 * button cannot bend more than 12 px of backdrop however thick it is authored.
 * The other three — scattering, occlusion, inner shadow — are applied below, each
 * multiplied by `sizeK`, so every one of them is exactly inert at `sizeK = 0`.
 *
 * The displacement is the normal times a profile that peaks at the rim and dies in
 * the interior, where the glass is flat and shows the backdrop straight through.
 * **Sampling LOD follows the same profile and the same depth**: the body sits at
 * `lensDepth * bodyLodPerPx` — thicker glass diffuses more — and the rim is biased
 * sharper, because a compressed backdrop reads as detail. That is the inverse of
 * the naive "blur more at the edge", and it is most of what makes an edge read as
 * glass rather than as a smudge.
 *
 * Every coefficient is advisory and calibration-delegated (C7), named on the CPU.
 *
 * ## The dual cap
 *
 * `refractionScale` arrives as one number the CPU already resolved through
 * `effectiveRefraction(accessibilityCap, stateQuality)` — Decision Log #19's rule
 * that renderers honour the lower of the two caps. The shader never sees them
 * separately, so it cannot honour the wrong one.
 */

export const WGSL_OPTICS_PASS = `struct OpticsUniforms {
  /// viewport size in device px (xy), CSS px per device px (z), coverage ramp px (w)
  screen : vec4f,
  /// backdrop uv transform on viewport-normalised coords: scale (xy), offset (zw)
  fit : vec4f,
  /// refractionScale, bodyLodPerPx, rimLodBias, chainMaxLod
  lens : vec4f,
  /// fixed tint colour, linear light (xyz), tint alpha (w)
  tint : vec4f,
  /// adapted tint colour, linear light (xyz), adaptation strength (w)
  adapt : vec4f,
  /// author tint seed, linear light (xyz), tone adaptation under the contrast regime (w)
  seed : vec4f,
  /// tintToneFloor, tintToneCeilMix, tintToneLow, tintToneHigh
  tone : vec4f,
  /// rimWidthPx, rimAlpha, specularPower, specularGain
  rim : vec4f,
  /// light direction, unit (xy), shadowDepth (z), shadowAlpha (w)
  light : vec4f,
  /// hasBackdrop, fieldSize.xy, fieldUpsampled
  flags : vec4f,
  /// the size law's gains (W2): scatterGainMax, occlusionGain, shadowGainMax,
  /// bodyChainLod — the last being the chain level whose blur already matches the
  /// body texture, which is what the scattering term measures its octaves from
  size : vec4f,
  /// backdrop tone adaptation (W7): backdropToneLow, backdropToneHigh, the size
  /// bias ALREADY divided by the accessibility refraction cap (so that it may be
  /// multiplied by the policy-folded 'sizeK' below and still mean the geometric
  /// thickness), and the strength the accessibility policy resolved — zero where
  /// the host could not measure a backdrop tone, which stands the axis down
  toneAdapt : vec4f,
  /// the backdrop source's own average colour, linear (xyz), and its luminance (w)
  toneColour : vec4f,
  /// the outer shadow (W8): its compositing-space alpha before the size law (x),
  /// the blur's sigma in group-local CSS px (y), the silhouette's outward spread
  /// in the same units (z), and the downward offset expressed in field-texture UV
  /// (w) — a UV so the offset silhouette is one texture read rather than a
  /// gradient extrapolation, which is exact only on a straight edge and a capsule
  /// is mostly not one
  shadow : vec4f,
  /// the outer shadow's size-law gain (x), read against the casting surface's own
  /// thickness, and the field rect's height in CSS px (y) — the conversion the
  /// shadow's shift needs when it lands outside the texture; z and w are the
  /// padding a uniform's vec4 alignment requires
  shadowSize : vec4f,
};

@group(0) @binding(0) var<uniform> ou : OpticsUniforms;
@group(0) @binding(1) var fieldTexture : texture_2d<f32>;
@group(0) @binding(2) var auxTexture : texture_2d<f32>;
@group(0) @binding(3) var backdropSampler : sampler;
@group(0) @binding(4) var backdropChain : texture_2d<f32>;
@group(0) @binding(5) var backdropBody : texture_2d<f32>;
@group(0) @binding(6) var fieldSampler : sampler;

/// Rim proximity: 1 exactly on the contour, falling to 0 by 'width' on either
/// side. Symmetric, so the rim is a band on the boundary rather than a plateau
/// that keeps burning outward where coverage has already faded.
fn rim_weight(d : f32, width : f32) -> f32 {
  let t = clamp(1.0 - abs(d) / max(width, 1e-4), 0.0, 1.0);
  return t * t;
}

/// The Gaussian CDF the outer shadow's edge falls off by: 1 deep inside the
/// shadow's silhouette, 0.5 exactly on it, 0 far outside. The tanh form of the
/// normal CDF — WGSL has no erf, and this is within 1.8e-4 of it everywhere,
/// which is 0.015 of one 8-bit code at the shipped occlusion. Mirrors
/// material.ts's 'outerShadowFalloff' term for term.
fn outer_shadow_falloff(signedDistance : f32, sigma : f32) -> f32 {
  let x = -signedDistance / max(sigma, 1e-4);
  return 0.5 * (1.0 + tanh(0.7978845608028654 * (x + 0.044715 * x * x * x)));
}

/// The outer shadow's alpha at this pixel (W8).
///
/// The shadow is the group's OWN field, translated down by 'shadow.w' in field
/// UV and outset by 'shadow.z', then blurred. Reading the offset silhouette from
/// the field texture rather than extrapolating the local distance along the
/// normal is what keeps a corner a corner: the first-order estimate is exact only
/// on a straight edge, and a capsule is mostly not one.
///
/// The value is an ALPHA on pure black, so what it composites to is the backdrop
/// times '1 - alpha' — multiplicative occlusion, and exactly zero over black,
/// with no branch for it.
fn outer_shadow_alpha(uv : vec2f, upsampled : f32, fieldSize : vec2f) -> f32 {
  if (ou.shadow.x <= 0.0) {
    return 0.0;
  }
  /*
   * The shift can leave the field texture, and clamping alone reads a lie there.
   *
   * Two ways it happens, and the second is not an edge case: the rect is clipped
   * to the canvas, so a surface within the shadow's reach of the viewport's TOP
   * has no rows above it to shift into; and even unclipped, the rect's pad is the
   * shadow's reach, so the topmost band of every group needs rows a further
   * 'offset' above that. Clamped, both repeat the edge texel — a distance that is
   * too SMALL, which reads as a flat, too-dark falloff exactly where the shadow
   * should be fading out, and diverges from the CSS tier, which has no texture to
   * run out of.
   *
   * Reconstructed instead of clamped. A signed distance field is 1-Lipschitz, and
   * in the region this happens in — directly above the surface — moving away from
   * it increases the distance by exactly the displacement. So adding back the
   * distance that was clamped off is exact there, and past the surface's corners
   * it over-estimates, which errs toward LESS shadow rather than more.
   */
  let shiftedY = uv.y - ou.shadow.w;
  let clampedOffCss =
    (max(0.0, -shiftedY) + max(0.0, shiftedY - 1.0)) * ou.shadowSize.y;
  let shadowUv = clamp(vec2f(uv.x, shiftedY), vec2f(0.0), vec2f(1.0));
  var shadowField : vec4f;
  var shadowAux : vec4f;
  if (upsampled > 0.5) {
    shadowField = textureSampleLevel(fieldTexture, fieldSampler, shadowUv, 0.0);
    shadowAux = textureSampleLevel(auxTexture, fieldSampler, shadowUv, 0.0);
  } else {
    let texel = clamp(vec2i(shadowUv * fieldSize), vec2i(0), vec2i(fieldSize) - vec2i(1));
    shadowField = textureLoad(fieldTexture, texel, 0);
    shadowAux = textureLoad(auxTexture, texel, 0);
  }

  // The size law reaches the amplitude and nothing else — the reference's three
  // lengths are span-invariant across 32…160 px. The gain rides the thickness of
  // the surface that CAST the shadow, which is the one read at the offset
  // position rather than the one under the pixel being shaded.
  //
  // Applied on '1 - alpha' rather than on the alpha: the gain is a fraction of
  // the remaining transparency in LINEAR light ('sizeOuterShadowOcclusionAt'),
  // and (1 - occ) is exactly what raising to 1/2.4 turns into (1 - alpha), so the
  // two forms are the same law and neither needs the other's space.
  let sizeK = clamp(shadowAux.z, 0.0, 1.0);
  let sizeFold = pow(max(1.0 - ou.shadowSize.x * sizeK, 0.0), 1.0 / 2.4);
  let alpha = 1.0 - (1.0 - ou.shadow.x) * sizeFold;

  return alpha * outer_shadow_falloff(shadowField.x + clampedOffCss - ou.shadow.z, ou.shadow.y);
}

@fragment
fn fs_optics(in : FullscreenOut) -> @location(0) vec4f {
  // Nominally the field is one texel per device pixel, so the read is an exact
  // load and no filter touches the distance or the normal. Under the governor's
  // 'refractionResolutionScale' the field was rasterised smaller than the group's
  // rect, and then it has to be filtered: a nearest read would quantise the
  // contour to the coarse grid and the rim would step along it.
  var field : vec4f;
  var aux : vec4f;
  if (ou.flags.w > 0.5) {
    field = textureSampleLevel(fieldTexture, fieldSampler, in.uv, 0.0);
    aux = textureSampleLevel(auxTexture, fieldSampler, in.uv, 0.0);
  } else {
    let texel = vec2i(in.uv * ou.flags.yz);
    field = textureLoad(fieldTexture, texel, 0);
    aux = textureLoad(auxTexture, texel, 0);
  }

  let d = field.x;
  let normal = field.yz;
  let coverage = field.w;

  /*
   * The outer shadow (W8) sits UNDER the material, so it is resolved before the
   * body and carried into the output's alpha rather than into its colour: the
   * pass writes premultiplied black there, and premultiplied black over the page
   * IS the multiplication. Outside the contour that is the whole of what this
   * pixel is; inside it the surface covers the shadow, exactly as a 'box-shadow'
   * is clipped out of its own border box, and the two meet across the coverage
   * ramp with no seam because it is one expression.
   */
  let shadowAlpha = outer_shadow_alpha(in.uv, ou.flags.w, ou.flags.yz);
  if (coverage <= 0.0) {
    return vec4f(0.0, 0.0, 0.0, shadowAlpha);
  }

  let viewport01 = in.position.xy / ou.screen.xy;
  let viewportCss = ou.screen.xy * ou.screen.z;

  // Per-pixel, unioned through the field pass. See the module note.
  let lensDepth = max(aux.x, 1e-4);
  // The size law's thickness factor for whichever surface owns this pixel, 0..1.
  // Zero on anything at or below the profile's 'sizeSpanMin', and every term
  // below multiplies by it — so a small control takes the pre-law path exactly.
  let sizeK = clamp(aux.z, 0.0, 1.0);
  // '-d' is depth inside the surface, so the profile runs 1 at the contour to 0
  // at 'lensDepth' inward, and the square makes the falloff read as curvature
  // rather than as a linear ramp.
  let depth = clamp(-d / lensDepth, 0.0, 1.0);
  let profile = (1.0 - depth) * (1.0 - depth);

  let displaceCss = -normal * lensDepth * profile * ou.lens.x;
  let refracted01 = viewport01 + displaceCss / viewportCss;

  let straightUv = clamp(viewport01 * ou.fit.xy + ou.fit.zw, vec2f(0.0), vec2f(1.0));
  let refractedUv = clamp(refracted01 * ou.fit.xy + ou.fit.zw, vec2f(0.0), vec2f(1.0));

  let bodyLod = clamp(lensDepth * ou.lens.y, 0.0, ou.lens.w);
  let lod = clamp(bodyLod - ou.lens.z * profile, 0.0, ou.lens.w);

  /*
   * The scattering facet of the size law: "a softer scattering of light".
   *
   * The body texture is one blur for the whole backdrop source — it is built once
   * per source per frame, so it cannot be per-surface. The chain beside it can:
   * 'size.w' is the chain level whose blur already matches that body, so
   * 'size.w + log2(scatterGain)' is the level whose blur is 'scatterGain' times
   * wider, and lerping the body toward it by 'sizeK' widens the kernel with the
   * surface. At sizeK = 0 the weight is zero and the body sample stands alone,
   * which is what makes the whole facet inert on a small control.
   */
  let scatterGain = 1.0 + (ou.size.x - 1.0) * sizeK;
  let scatterLod = clamp(ou.size.w + log2(max(scatterGain, 1e-4)), 0.0, ou.lens.w);

  var backdrop = vec3f(0.0);
  if (ou.flags.x > 0.5) {
    let lensSample = textureSampleLevel(backdropChain, backdropSampler, refractedUv, lod);
    let bodySample = textureSampleLevel(backdropBody, backdropSampler, straightUv, 0.0);
    let scatterSample = textureSampleLevel(backdropChain, backdropSampler, straightUv, scatterLod);
    // Premultiplied linear in, straight colour out: the material composites over
    // whatever is behind it, so a partially transparent backdrop must not darken
    // the glass.
    let lensColour = lensSample.rgb / max(lensSample.a, 1e-6);
    let scatterColour = scatterSample.rgb / max(scatterSample.a, 1e-6);
    let bodyColour = mix(bodySample.rgb / max(bodySample.a, 1e-6), scatterColour, sizeK);
    backdrop = mix(bodyColour, lensColour, profile);
  }

  // Adaptive tint. 'adapt.w' is the strength the accessibility policy and the
  // group's analysis quality already agreed on; at 0 the fixed tint stands, which
  // is what a 'hint' or 'none' group gets.
  let neutral = mix(ou.tint.rgb, ou.adapt.rgb, ou.adapt.w);

  let backdropLuma = dot(backdrop, vec3f(0.2126, 0.7152, 0.0722));

  /*
   * Backdrop tone adaptation (W7) — step two of the composition contract, between
   * the colour scheme's neutral and the author's tint.
   *
   * Read against 'toneColour': the backdrop SOURCE's own average, measured by the
   * host from the pixels it supplied and handed to both tiers as one number. Not a
   * per-pixel sample, and that is the load-bearing choice — see
   * 'GroupRenderInput.backdropTone' for the cross-tier measurement that settled
   * it, and note that the reference agrees: its capsule over a sparse bright grid
   * is a flat body rather than a window onto the grid.
   *
   * 'sizeK' is still per pixel, so a container holding a small control and a large
   * platter adapts each of them by its own thickness out of one pass.
   *
   * Strength is zero where the host measured no tone, and the whole axis stands
   * down where there is no backdrop at all rather than reading the zero vector as
   * a black backdrop and dissolving the surface into nothing.
   *
   * Written out instead of calling smoothstep() so that a profile patched with
   * low >= high degrades to a step rather than to NaN.
   */
  var toneAdapt = 0.0;
  if (ou.flags.x > 0.5 && ou.toneAdapt.w > 0.0) {
    let toneX = ou.toneColour.w + ou.toneAdapt.z * sizeK;
    let toneT = clamp(
      (toneX - ou.toneAdapt.x) / max(ou.toneAdapt.y - ou.toneAdapt.x, 1e-6),
      0.0,
      1.0,
    );
    toneAdapt = clamp(ou.toneAdapt.w, 0.0, 1.0) * (1.0 - toneT * toneT * (3.0 - 2.0 * toneT));
  }
  /*
   * Both the colour and the alpha move, together and not separately. What the
   * adaptation means is that the INTERIOR converges on the backdrop's tone —
   * mix(interior, tone, k) — and this is the (colour, alpha) pair that composites
   * to exactly that. Lerping the two independently makes a partially adapted
   * surface lighter than it started (more opaque toward a tint still mostly
   * neutral), which the 96 px cells caught at once: interior 0.4545 → 0.5179
   * against a reference of 0.4542. The alpha half is not a colour axis reaching
   * the occlusion axis — an adapting material stops transmitting, which is what
   * the reference's flat body over the impulse grid is. See 'adaptedTintColour'
   * and 'adaptedTintAlpha' in material.ts.
   */
  let sizedAlpha = ou.tint.w + ou.size.y * sizeK * (1.0 - ou.tint.w);
  let adaptedAlpha = sizedAlpha + toneAdapt * (1.0 - sizedAlpha);
  var adapted = neutral;
  if (toneAdapt > 0.0 && adaptedAlpha > 0.0) {
    adapted =
      (neutral * ((1.0 - toneAdapt) * sizedAlpha) + ou.toneColour.rgb * toneAdapt) / adaptedAlpha;
  }

  // The author tint. 'aux.w' is the per-pixel strength, unioned in the field pass,
  // so a toolbar can carry one tinted control among plain ones; the seed is a
  // group uniform. At strength 0 this is the identity and the material is the one
  // the calibration bed measures, byte for byte.
  //
  // Apple's mechanism, not a fill: the seed is the middle of a range of tones
  // 'mapped to content brightness underneath'. 'backdrop' is what this pixel is
  // actually looking through — lens-displaced, LOD-sampled, already the thing the
  // material transmits — so the tone is taken against the same light the tint is
  // about to be mixed into, and a tinted surface over a dark backdrop settles to a
  // shade of the author's colour rather than sitting on it as paint.
  //
  // That 'backdrop' is also where the size law's scattering has already been
  // applied (above), and that is the right order rather than a coincidence: a
  // large surface diffuses more of what is behind it, so the tone the tint maps
  // to should be the diffused light, not the sharp light nobody sees through it.
  //
  // It displaces the ADAPTED neutral, not the raw one: a full-strength tint is its
  // own adaptation and replaces this axis outright, while a partial one moves with
  // it. That order is the wave's composition contract, in one line.
  var tintColour = adapted;
  if (aux.w > 0.0) {
    let t = smoothstep(ou.tone.z, ou.tone.w, backdropLuma);
    let low = ou.seed.rgb * ou.tone.x;
    let high = ou.seed.rgb + (vec3f(1.0) - ou.seed.rgb) * ou.tone.y;
    // 'seed.w' is the contrast regime's grip on the excursion, never on the hue:
    // at 0 the material shows the author's colour flat and stops responding.
    let tone = mix(ou.seed.rgb, mix(low, high, t), clamp(ou.seed.w, 0.0, 1.0));
    tintColour = mix(adapted, tone, clamp(aux.w, 0.0, 1.0));
  }

  // The tint layer's ALPHA is untouched by the author's colour. It is the
  // material's occlusion — what reduced transparency lifts, and the axis the
  // system's own Clear-to-Tinted preference runs on — and an author choosing a
  // colour does not get to move it.
  //
  // The size law does move it, and the two do not collide: "a larger size is more
  // opaque, a smaller size is clearer" is a statement about how much material
  // there is, not about what colour it is. A fraction of whatever transparency
  // the resolved alpha still has, for the reason 'increasedOcclusionLift' is a
  // fraction — see material.ts.
  //
  // The backdrop adaptation moves it, above, and the author's colour does not.
  var colour = mix(backdrop, tintColour, adaptedAlpha);

  /*
   * Everything below is the surface's own APPEARANCE — the marks that say a
   * surface is here rather than what is behind it — and all of it fades with the
   * adaptation, on the one factor.
   *
   * That is not symmetry for its own sake; it is what the reference does, and it
   * is a calibration cell rather than an inference: the reference's capsule over
   * the dark-solid backdrop is byte-identical to that background, rim included. A
   * material that has taken its backdrop's tone has no lit edge to show, because
   * there is no light in front of it to show one with.
   *
   * The gap was invisible until this axis existed. A rim of up to 130/255 sat
   * unnoticed inside a bright capsule body; with the body gone it is a white
   * outline around a surface that should not be there at all — 595 pixels past
   * 2/255 on that one cell, and OKLab ΔE max 0.47 where p95 already read 0.0000.
   * The same lesson W3 recorded from the other direction: a term that happens to
   * be hidden is one feature away from being visible.
   */
  let present = 1.0 - toneAdapt;

  // Inner shadow: the material's own occlusion, deepest where the lens is
  // strongest, which is what makes a thicker surface read as heavier — and the
  // shadow facet of the size law deepens it further with the span.
  let shadowDepth = ou.light.z * (1.0 + (ou.size.z - 1.0) * sizeK);
  colour = colour * (1.0 - profile * shadowDepth * ou.light.w * present);

  // Rim and specular from the gradient. The rim is unlit ambient edge brightness;
  // the specular term is the same edge lit from 'light.xy'.
  let rw = rim_weight(d, ou.rim.x);
  let facing = dot(normal, ou.light.xy);
  let spec = pow(clamp(facing, 0.0, 1.0), max(ou.rim.z, 1e-3)) * ou.rim.w;
  colour = colour + vec3f(rw * (ou.rim.y + spec) * present);

  // The material over its own shadow over the page, in one premultiplied vector:
  // the colour is the surface's, weighted by its coverage, and the alpha is what
  // the two of them together leave the page — 'coverage' from the surface, and
  // the shadow filling whatever transparency is left.
  let body = encode_output(max(colour, vec3f(0.0)), coverage);
  return vec4f(body.rgb, body.a + shadowAlpha * (1.0 - body.a));
}`;
