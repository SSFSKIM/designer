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
 * The number is `aux.z`, the surface's span in CSS px, carried **per pixel**
 * through the field pass's union; this pass evaluates `material.ts`'s
 * `sizeThickness(span)` from it, and the scatter facet's own span curve beside
 * it. Since W13 the scattering reads the pixel's own depth under the contour as
 * well (`scatterSharpShare`, claims §5.61 §2): the span curve is the mix deep
 * inside the surface and the ramp is an excursion on it near the contour. The
 * span is what lets a 40 px button and a 320 px platter share one group's field
 * pass and still read as different thicknesses. The occlusion and the inner shadow
 * are applied below, each multiplied by `sizeK`, so both are exactly inert at
 * `sizeK = 0`; the scattering is applied by `kScatter`, which is per pixel and
 * whose floor keeps it at the material's own frost rather than at nothing. The inner
 * shadow's depth is W2's law, kept: `min(thickness * (1 + (gain − 1) * sizeK),
 * span / 2)`, with a square profile on it.
 *
 * ## The lens (W12 G2, claims §5.51)
 *
 * The lens reads its own law since W12 G2 — the reference's, taken from its
 * layer tree (§5.50) and fitted on the pixels (§5.51). Two clamped linear
 * functions of the span give the depth and the magnitude, scaled by the author's
 * thickness over the reference's unit of 8:
 *
 * ```
 * lensDepth = min((thickness / 8) * min(0.25 * span, 20), span / 2)     8 / 11 / 20 on 32 / 44 / ≥ 80
 * S         = lensRefractionGain * (thickness / 8) * min(0.8 * span, 60)  44.7 at saturation
 * D(u)      = S * max(0, 1 − u / (lensExtentGain * lensDepth)) ^ lensProfileExponent
 * ```
 *
 * One steep power (26.7 px extent, exponent 3.69 on a saturated span): the
 * reference's band is the plate folded from 34 / 24 / 12 px in at 2 / 4 / 8 px
 * from the contour (§5.49). It is the SAME two-component body the interior
 * shows, read at the displaced position — blur before displacement, measured.
 * The direction is not the field's normal alone: the reference ovalizes its SDF
 * gradient (`gradientOvalization`, 0.5 on thick shapes), which magnifies the
 * band *along* the edge by up to 1.31×; so the displacement runs along the
 * gradient of the field blended toward the oval inscribed in the surface's box,
 * `(1 − ω)·n̂ + ω·∇d_oval`, with the magnitude fixed. ω is `lensOvalization` on a
 * thick surface, 0 on a thin one, a smoothstep over the reference's knee at
 * 64–72 px between. The half-extent clamp is what keeps a small control from
 * being all lens: a 24 px-tall button cannot bend more than 12 px of backdrop
 * however thick it is authored — and the magnitude is clamped by the same
 * ratio, so the profile keeps its shape.
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
  /// refractionScale, lensRefractionGain (W12 G2: the gain on the reference's
  /// amount law), the inner shadow's depth gain (W2's lensSizeGainMax, which the
  /// shadow keeps), chainMaxLod
  lens : vec4f,
  /// fixed tint colour, linear light (xyz), tint alpha (w)
  tint : vec4f,
  /// adapted tint colour, linear light (xyz), adaptation strength (w)
  adapt : vec4f,
  /// author tint seed, linear light (xyz), tone adaptation under the contrast regime (w)
  seed : vec4f,
  /// the author tint's shade law (W10): tintShadeDark, tintShadeLight,
  /// tintShadeStrength (the profile's provenance gate); and (w) the size law's
  /// accessibility fold — the refraction ladder read at the preference's cap,
  /// which every facet's span-dependent rise is multiplied by (W11c)
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
  /// shadow's shift needs when it lands outside the texture; the body depth
  /// ramp's THICK start (z, W13 G1's third form — the thin end is scatter.y and
  /// this pass mixes the two by the pixel's own sizeThickness), and (w) the
  /// padding a uniform's vec4 alignment requires
  shadowSize : vec4f,
  /// the backdrop tone response's anchors (W9): the three solid anchors'
  /// ENCODED-space means (xyz), and the backdrop's linear-space mean (w) — the
  /// quantity the response solve composites against
  toneAnchor : vec4f,
  /// the response law's thin row: the reference's settled interior levels at the
  /// three anchors for a surface of sizeThickness 0 (xyz); w is the law's
  /// per-profile authority — 0 on dark profiles, whose response is unmeasured
  toneRowThin : vec4f,
  /// the thick row (sizeThickness saturated), same layout
  toneRowThick : vec4f,
  /// the size law's bands: the scatter facet's floor (x) and the depth ramp's
  /// THIN start s0 at the ratio this group draws at (y, W13 G1 — the CPU has
  /// already interpolated it between the profile's 1x and 2x anchors; the thick
  /// end is shadowSize.z), and the
  /// thickness curve's sizeSpanMin (z) and sizeSpanMax (w); the fold both
  /// multiply by is tone.w. The scatter span curve's own band top is lensOval.w,
  /// and it starts at the same z.
  scatter : vec4f,
  /// the lens law (W12 G2): the reference's height law (lensHeightPerSpan,
  /// lensHeightMax) and amount law (lensAmountPerSpan, lensAmountMax)
  lensLaw : vec4f,
  /// the lens profile (W12 G2): lensExtentGain, lensProfileExponent,
  /// lensOvalization, lensThicknessReference
  lensShape : vec4f,
  /// the ovalization's knee (W12 G2): spanMin (x), spanMax (y); the body depth
  /// ramp's reach in group-local CSS px (z, W13 G1) — the profile names it in
  /// device px and the CPU divides by the ratio, so that this shader can read
  /// the field's own CSS-px depth without a second conversion; the scatter span
  /// curve's band top sizeScatterSpanMax (w, W11c), which W13 G1 keeps
  /// underneath the ramp as its deep value
  lensOval : vec4f,
};

@group(0) @binding(0) var<uniform> ou : OpticsUniforms;
@group(0) @binding(1) var fieldTexture : texture_2d<f32>;
@group(0) @binding(2) var auxTexture : texture_2d<f32>;
@group(0) @binding(3) var backdropSampler : sampler;
@group(0) @binding(4) var backdropChain : texture_2d<f32>;
@group(0) @binding(5) var backdropBody : texture_2d<f32>;
@group(0) @binding(6) var fieldSampler : sampler;
/// The owning surface's box per pixel (W12 G2): the pixel's offset from its
/// centre (xy) and its half-extents (zw), group-local CSS px — the lens's oval.
@group(0) @binding(7) var aux2Texture : texture_2d<f32>;

/// One encoded sRGB channel from a linear one — the space the backdrop tone
/// response's anchors live in (W9). Mirrors material.ts's 'linearToSrgbChannel'.
fn srgb_encode(c : f32) -> f32 {
  let x = clamp(c, 0.0, 1.0);
  return select(1.055 * pow(x, 1.0 / 2.4) - 0.055, x * 12.92, x <= 0.0031308);
}

/// The backdrop tone response R(encodedInput, sizeK) (W9): monotone
/// (Fritsch–Carlson) interpolation through the three anchors, clamped to their
/// span; smoothstep between the thin and thick rows. Mirrors material.ts's
/// 'backdropToneResponse' term for term — the constants are authored there.
fn tone_response(x : f32, sizeK : f32) -> f32 {
  let f = sizeK * sizeK * (3.0 - 2.0 * sizeK);
  let ys = mix(ou.toneRowThin.xyz, ou.toneRowThick.xyz, vec3f(f));
  let xs = ou.toneAnchor.xyz;
  let xc = clamp(x, xs.x, xs.z);
  let h0 = max(xs.y - xs.x, 1e-4);
  let h1 = max(xs.z - xs.y, 1e-4);
  let d0 = (ys.y - ys.x) / h0;
  let d1 = (ys.z - ys.y) / h1;
  // The interior slope: the harmonic mean where the secants agree, 0 across a
  // sign change — what keeps the curve monotone between monotone anchors.
  var m1 = 0.0;
  if (d0 * d1 > 0.0) { m1 = 2.0 * d0 * d1 / (d0 + d1); }
  var h = h0; var t = (xc - xs.x) / h0;
  var y0 = ys.x; var y1 = ys.y; var s0 = d0; var s1 = m1;
  if (xc > xs.y) {
    h = h1; t = (xc - xs.y) / h1;
    y0 = ys.y; y1 = ys.z; s0 = m1; s1 = d1;
  }
  return y0 * (1.0 + 2.0 * t) * (1.0 - t) * (1.0 - t)
       + s0 * h * t * (1.0 - t) * (1.0 - t)
       + y1 * t * t * (3.0 - 2.0 * t)
       + s1 * h * t * t * (t - 1.0);
}

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
  // The thickness curve off the casting surface's span (W11c: the span rides
  // the field), written as the body's own is below.
  let castT = clamp(
    (shadowAux.z - ou.scatter.z) / max(ou.scatter.w - ou.scatter.z, 1e-6),
    0.0,
    1.0,
  );
  let sizeK = clamp(castT * castT * (3.0 - 2.0 * castT) * clamp(ou.tone.w, 0.0, 1.0), 0.0, 1.0);
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
  var aux2 : vec4f;
  if (ou.flags.w > 0.5) {
    field = textureSampleLevel(fieldTexture, fieldSampler, in.uv, 0.0);
    aux = textureSampleLevel(auxTexture, fieldSampler, in.uv, 0.0);
    aux2 = textureSampleLevel(aux2Texture, fieldSampler, in.uv, 0.0);
  } else {
    let texel = vec2i(in.uv * ou.flags.yz);
    field = textureLoad(fieldTexture, texel, 0);
    aux = textureLoad(auxTexture, texel, 0);
    aux2 = textureLoad(aux2Texture, texel, 0);
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

  // Per-pixel, unioned through the field pass. See the module note. 'aux.x' is
  // the authored thickness times the lensStrength channel (W12 G2); the lens's
  // depth and the inner shadow's are both evaluated from it and the span below.
  let lensThick = max(aux.x, 0.0);
  // The thickness curve off the span of whichever surface owns this pixel
  // (W11c). 'sizeK' is the thickness factor, 0..1: zero on anything at or below
  // the profile's 'sizeSpanMin', saturated at 'sizeSpanMax', folded under the
  // preference — the occlusion, the inner shadow and the tone response multiply
  // by it, so a small control takes the pre-law path exactly. Written out as a
  // smoothstep with a guarded denominator, so a profile that collapses the band
  // degrades to a step rather than to NaN.
  let span = aux.z;
  let fold = clamp(ou.tone.w, 0.0, 1.0);
  let thickT = clamp((span - ou.scatter.z) / max(ou.scatter.w - ou.scatter.z, 1e-6), 0.0, 1.0);
  // The unfolded curve, which the depth ramp's start grades along below, and the
  // folded factor every other facet multiplies by. One smoothstep, two readings.
  let sizeThick = thickT * thickT * (3.0 - 2.0 * thickT);
  let sizeK = clamp(sizeThick * fold, 0.0, 1.0);
  /*
   * The body's mix is the span curve W11c fitted with a ramp in DEPTH riding on
   * top of it near the contour (W13 G1, from the measurement of claims §5.61 §2
   * and the re-forming its first runtime sweep forced):
   *
   *   kDeep = floor + (1 - floor) * smoothstep(sizeSpanMin, sizeScatterSpanMax, span)
   *   s0    = startThin + (startThick - startThin) * sizeThickness(span)
   *   s(u)  = (1 - kDeep) + max(0, s0 - (1 - kDeep)) * max(0, 1 - u / U)
   *   k(u)  = 1 - s(u)
   *
   * The first form of the ramp replaced the span curve outright and its sweep
   * measured what that cost: the ramp's own projection onto one number per
   * surface runs 0.43-0.56 where the curve it replaced runs 0.41-1.00, so the
   * family is nearly span-flat where the bed is strongly span-graded and no
   * point in 81 reached the wave's stops. So the curve stays as the deep value
   * and the ramp is what it always measured as - a near-contour excursion.
   *
   * The SECOND form gave that excursion one start per scale, and its own sweep
   * refuted that arithmetically (claims §5.64 §2): the smallest cell's span is
   * exactly sizeSpanMin, so its deep sharp share is exactly 1 - floor and no
   * start at or below it can touch that cell, while the next span up only
   * improves BELOW a start lower still. So the start grades with span too, and
   * along the material's own thin/thick curve rather than a new one - the same
   * smoothstep 'sizeK' is built from above, unfolded, because s0 is a share the
   * reference has and not a rise a preference removes. The fold below still
   * applies once, on the composed mix.
   *
   * '-d' is the depth, in group-local CSS px and unclamped - the same quantity
   * the lens's 'lensT' and the inner shadow's 'shadowT' are evaluated from,
   * except that those two divide it by a depth of their own while this reads it
   * absolutely, because the reach measured as a LENGTH rather than as a fraction
   * of the span. The reach reaches this shader already divided by the device
   * ratio ('lensOval.z'), so the ratio 'u / U' is the same number in CSS px as
   * it is in the device px the profile names.
   *
   * 'max(s0 - sDeep, 0)' rather than a signed difference: the excursion is the
   * band the reference has ABOVE the body, and a span whose deep sharp share
   * already exceeds s0 has nothing to add rather than something to subtract.
   *
   * The fold keeps its W11c semantics on the composed law: the floor is the
   * frost the material has at any size and is not folded, everything above it -
   * the span curve's rise and the ramp's excursion alike - is depth and is, so
   * fold 1 renders the law and fold 0 sits at the floor exactly.
   */
  let scatterFloor = clamp(ou.scatter.x, 0.0, 1.0);
  let deepT = clamp((span - ou.scatter.z) / max(ou.lensOval.w - ou.scatter.z, 1e-6), 0.0, 1.0);
  let kDeep = scatterFloor + (1.0 - scatterFloor) * deepT * deepT * (3.0 - 2.0 * deepT);
  let sDeep = 1.0 - kDeep;
  let rampT = max(1.0 - max(-d, 0.0) / max(ou.lensOval.z, 1e-6), 0.0);
  let rampStart = ou.scatter.y + (ou.shadowSize.z - ou.scatter.y) * sizeThick;
  let sharpShare = clamp(sDeep + max(rampStart - sDeep, 0.0) * rampT, 0.0, 1.0);
  let kScatter = clamp(scatterFloor + ((1.0 - sharpShare) - scatterFloor) * fold, 0.0, 1.0);
  // The inner shadow's depth and profile: W2's law, byte for byte — the
  // thickness times the size gain (folded through 'sizeK'), clamped to the
  // shorter half extent, and a square on it. The lens ran on this until W12 G2;
  // the occlusion keeps it, because nothing measured it as wrong, and every
  // solid-backdrop cell renders exactly as it did.
  let shadowLensDepth = max(min(lensThick * (1.0 + (ou.lens.z - 1.0) * sizeK), span * 0.5), 1e-4);
  let shadowT = clamp(-d / shadowLensDepth, 0.0, 1.0);
  let shadowProfile = (1.0 - shadowT) * (1.0 - shadowT);

  // The lens (W12 G2, claims §5.51) — see the module note. The reference's
  // height and amount laws off the span, scaled by the thickness over the
  // reference's unit, folded like the W2 law (at fold 0 the depth is the
  // authored thickness and nothing more), and clamped to the shorter half
  // extent with the magnitude clamped by the same ratio.
  let thickScale = lensThick / max(ou.lensShape.w, 1e-4);
  let heightBase = min(ou.lensLaw.x * span, ou.lensLaw.y);
  let amountBase = min(ou.lensLaw.z * span, ou.lensLaw.w);
  let depthUnclamped = mix(lensThick, heightBase * thickScale, fold);
  let lensDepth = clamp(depthUnclamped, 0.0, span * 0.5);
  let clampRatio = select(0.0, lensDepth / depthUnclamped, depthUnclamped > 1e-6);
  let magnitude = ou.lens.y * mix(lensThick, amountBase * thickScale, fold) * clampRatio;
  let extent = max(ou.lensShape.x * lensDepth, 1e-4);
  // One steep power over the extent; '-d' is depth inside the surface.
  let lensT = max(1.0 - max(-d, 0.0) / extent, 0.0);
  let displacementCss = magnitude * pow(lensT, ou.lensShape.y) * ou.lens.x;

  // The direction: the field's gradient blended toward the oval inscribed in
  // the surface's box (the reference's 'gradientOvalization'), on from the
  // knee, with the magnitude fixed — which tilts the displacement toward the
  // edge's midpoint and magnifies the band along the edge.
  let ovalT = clamp((span - ou.lensOval.x) / max(ou.lensOval.y - ou.lensOval.x, 1e-6), 0.0, 1.0);
  let omega = ou.lensShape.z * ovalT * ovalT * (3.0 - 2.0 * ovalT);
  let halfExt = max(aux2.zw, vec2f(1e-4));
  let rel = aux2.xy;
  let unitR = max(length(rel / halfExt), 1e-6);
  let ovalGrad = (rel / (halfExt * halfExt)) * (min(halfExt.x, halfExt.y) / unitR);
  let blended = (1.0 - omega) * normal + omega * ovalGrad;
  let blendLen = length(blended);
  let direction = select(normal, blended / blendLen, blendLen > 1e-6);
  let displaceCss = -direction * displacementCss;
  let refracted01 = viewport01 + displaceCss / viewportCss;

  let refractedUv = clamp(refracted01 * ou.fit.xy + ou.fit.zw, vec2f(0.0), vec2f(1.0));

  /*
   * The scattering facet of the size law: "a softer scattering of light".
   *
   * The body texture is one blur for the whole backdrop source — it is built once
   * per source per frame, so it cannot be per-surface. The chain beside it can:
   * 'size.w' is the chain level whose blur already matches that body, so
   * 'size.w + log2(sizeScatterGainMax)' is the level whose blur is the gain times
   * wider — the HEAVY component, at one fixed level — and lerping the body toward
   * it by 'kScatter' is what the reference's interior measures (W11c, claims
   * §5.41): a sharp component near the body's σ and a heavy one near σ 10, mixed
   * by a share that is ≈ 0.4 on a small control and rises with the span. The
   * mix, not the level, is what the span moves.
   */
  let scatterLod = clamp(ou.size.w + log2(max(ou.size.x, 1e-4)), 0.0, ou.lens.w);

  var backdrop = vec3f(0.0);
  if (ou.flags.x > 0.5) {
    // Both components at the refracted position (W11c G2): the band and the
    // interior are one body, and the displacement alone is the lens.
    let bodySample = textureSampleLevel(backdropBody, backdropSampler, refractedUv, 0.0);
    let scatterSample = textureSampleLevel(backdropChain, backdropSampler, refractedUv, scatterLod);
    // Premultiplied linear in, straight colour out: the material composites over
    // whatever is behind it, so a partially transparent backdrop must not darken
    // the glass.
    let scatterColour = scatterSample.rgb / max(scatterSample.a, 1e-6);
    backdrop = mix(bodySample.rgb / max(bodySample.a, 1e-6), scatterColour, kScatter);
  }

  // Adaptive tint. 'adapt.w' is the strength the accessibility policy and the
  // group's analysis quality already agreed on; at 0 the fixed tint stands, which
  // is what a 'hint' or 'none' group gets.
  let neutral = mix(ou.tint.rgb, ou.adapt.rgb, ou.adapt.w);

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

  /*
   * The backdrop tone response solve (W9) — the law that owns the interior
   * MEAN, where the collapse below owns texture and nothing else (claims
   * §5.33). The composite under this mechanism reduces exactly to
   * mean = (1 − k)·M₀ + k·toneLuma with M₀ = (1 − α)·bgLinear + α·L(neutral),
   * so the neutral's tone is solved in closed form: shift its luma so the
   * post-collapse mean lands on R(encodedInput, sizeK), the reference's own
   * measured response. Chroma is untouched — the shift is achromatic — and
   * the author tint still displaces the result per the composition contract.
   *
   * Three stand-downs, each measured rather than defensive: the whole axis is
   * off where no backdrop tone was measured (same gate as the collapse); the
   * solve's authority fades to zero below the dark anchor, where the only
   * evidence is the impulse cell the collapse constants were fitted on; and
   * at k → 1 the collapse owns the pixel outright, so the solve's
   * extrapolation is never evaluated against a vanishing (1 − k).
   */
  var solvedNeutral = neutral;
  var solvedAlpha = sizedAlpha;
  if (ou.flags.x > 0.5 && ou.toneAdapt.w > 0.0 && ou.toneRowThin.w > 0.0 &&
      sizedAlpha > 1e-3 && toneAdapt < 0.995) {
    let encodedInput = srgb_encode(ou.toneColour.w);
    let anchor = max(ou.toneAnchor.x, 1e-4);
    let authority =
      smoothstep(anchor * 0.5, anchor, encodedInput) * clamp(ou.toneRowThin.w, 0.0, 1.0);
    if (authority > 0.0) {
      let response = tone_response(encodedInput, sizeK);
      // The collapse's mean pull is toward L(toneColour.rgb) — the LINEAR
      // mean, which toneAnchor.w carries — not toward the encoded level.
      let preCollapse = (response - toneAdapt * ou.toneAnchor.w) / (1.0 - toneAdapt);
      let neutralLuma = dot(neutral, vec3f(0.2126, 0.7152, 0.0722));
      let nominal = (1.0 - sizedAlpha) * ou.toneAnchor.w + sizedAlpha * neutralLuma;
      let shift = (preCollapse - nominal) / sizedAlpha * authority * ou.toneAdapt.w;
      solvedNeutral = clamp(neutral + vec3f(shift), vec3f(0.0), vec3f(1.0));
      /*
       * The light attractor needs OPACITY. The light scheme's neutral is
       * already at white, so an upward shift clamps to nothing — and the
       * reference's light-adapted state is the material gone opaque-bright,
       * the same "an adapting material stops transmitting" the collapse's
       * alpha half was measured on. Whatever the clamp truncated is carried
       * by the alpha, solved against the same composite and folded by the
       * same authority. One-sided by design: darkward opacity is the
       * collapse's own axis with its own fitted constants.
       */
      let solvedLuma = dot(solvedNeutral, vec3f(0.2126, 0.7152, 0.0722));
      let achieved = (1.0 - sizedAlpha) * ou.toneAnchor.w + sizedAlpha * solvedLuma;
      if (preCollapse > achieved + 1e-4 && solvedLuma > ou.toneAnchor.w + 1e-3) {
        let alphaTarget = clamp(
          (preCollapse - ou.toneAnchor.w) / (solvedLuma - ou.toneAnchor.w),
          sizedAlpha,
          1.0,
        );
        solvedAlpha = mix(sizedAlpha, alphaTarget, authority * ou.toneAdapt.w);
      }
    }
  }

  let adaptedAlpha = solvedAlpha + toneAdapt * (1.0 - solvedAlpha);
  var adapted = solvedNeutral;
  if (toneAdapt > 0.0 && adaptedAlpha > 0.0) {
    adapted =
      (solvedNeutral * ((1.0 - toneAdapt) * solvedAlpha) + ou.toneColour.rgb * toneAdapt) /
      adaptedAlpha;
  }

  // The material, untinted: the adapted neutral over what this pixel looks
  // through, at the material's own occlusion. That alpha is what reduced
  // transparency lifts and what the size law thickens ("a larger size is more
  // opaque" is a statement about how much material there is), and the backdrop
  // adaptation moved it above. The author's colour never touches it — but not
  // for the reason the composition contract first gave (claims §5.36).
  var colour = mix(backdrop, adapted, adaptedAlpha);
  /*
   * How much of this pixel the SURFACE owns, as the canvas will composite it.
   *
   * With a backdrop the composite above is the whole pixel — the pass sampled
   * what is behind the surface and mixed it in, so the output is opaque inside
   * the contour and the page beneath the canvas never shows. With no backdrop
   * the composite is not here to make: a 'css-backdrop' group's blurred
   * backdrop is a DOM proxy under this canvas, a 'none' group's is the page
   * itself, and the browser is the compositor. So the material leaves as a
   * LAYER — the adapted colour at the material's own alpha, premultiplied on
   * the way out — and every term below that would have shaped the composite
   * shapes the layer instead, in the form that composites to the same thing.
   *
   * Before W11a this path mixed the material over a black backdrop and wrote
   * it opaque: a nested surface over glass rendered as a flat 0.468 where the
   * reference reads 0.89 (claims §5.38 §5). The rows that floored were that
   * grey. The pair the layer is written at is the host's
   * ('GroupRenderInput.unsampledMaterial'): the browser composites this canvas
   * in encoded sRGB, so the alpha is the CSS tier's, not the linear profile's.
   */
  var bodyAlpha = 1.0;
  if (ou.flags.x <= 0.5) {
    colour = adapted;
    bodyAlpha = adaptedAlpha;
  }

  // The author tint (W10). 'aux.w' is the per-pixel strength, unioned in the
  // field pass, so a toolbar can carry one tinted control among plain ones; the
  // seed is a group uniform. At strength 0 this is the identity and the material
  // is the one the calibration bed measures, byte for byte.
  //
  // Apple's mechanism, measured per pixel: the tinted material is an OPAQUE
  // layer of the seed at a shade that is linear in the luminance the untinted
  // material shows at this pixel — about half the seed's light over black
  // content, the seed itself over white, the seed's chromaticity intact
  // throughout. That layer composites over the material at the AUTHOR's
  // opacity in the encoded space, which is what a CALayer with 'opacity' does
  // and how the reference's half-strength cell measures. So a tinted surface
  // over a checkerboard shows the checker as light and dark ORANGE, not as
  // orange glass with the checker behind it — the material's own alpha is not
  // what a tinted surface shows.
  //
  // 'seed.w' is the contrast regime's grip on the excursion, never on the hue;
  // 'tone.z' is the profile's provenance gate (the dark scheme renders the pure
  // seed); and '1 − toneAdapt' folds the shade out where the collapse has made
  // the material a dark body, where the reference renders the pure seed too.
  // At zero grip the layer is the bare seed — the author's colour, flat.
  if (aux.w > 0.0) {
    // The untinted material's luminance at this pixel. Over a backdrop that is
    // the composite; as a layer it is the layer over the tone the host measured
    // for the group — zero where nothing was measured, the same reference-level
    // convention the CSS tier's 'materialLuminance' takes (within its 0.02).
    let u = bodyAlpha * dot(colour, vec3f(0.2126, 0.7152, 0.0722)) + (1.0 - bodyAlpha) * ou.toneColour.w;
    let grip = clamp(ou.seed.w, 0.0, 1.0) * clamp(ou.tone.z, 0.0, 1.0) * (1.0 - toneAdapt);
    let shade = mix(1.0, clamp(mix(ou.tone.x, ou.tone.y, clamp(u, 0.0, 1.0)), 0.0, 1.0), grip);
    let layer = ou.seed.rgb * shade;
    let s = clamp(aux.w, 0.0, 1.0);
    let encodedMaterial = linear_to_srgb(clamp(colour, vec3f(0.0), vec3f(1.0)));
    let encodedLayer = linear_to_srgb(layer);
    if (ou.flags.x > 0.5) {
      colour = srgb_to_linear(mix(encodedMaterial, encodedLayer, vec3f(s)));
    } else {
      // The opaque layer at the author's opacity over the material's own layer,
      // premultiplied: the fold 'tintedCssOptics' makes into one rgba.
      let premultiplied = (1.0 - s) * bodyAlpha * encodedMaterial + s * encodedLayer;
      bodyAlpha = 1.0 - (1.0 - s) * (1.0 - bodyAlpha);
      colour = srgb_to_linear(premultiplied / max(bodyAlpha, 1e-6));
    }
  }

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
  // A multiplicative occlusion of the whole composite. As a layer that is the
  // colour scaled and the alpha raised — (k·a·c, 1 − k·(1 − a)) composites to
  // k times what (a·c, a) would — and at bodyAlpha 1 it is the plain product.
  let shadowKeep = 1.0 - shadowProfile * shadowDepth * ou.light.w * present;
  let shadowedAlpha = 1.0 - shadowKeep * (1.0 - bodyAlpha);
  colour = colour * (shadowKeep * bodyAlpha / max(shadowedAlpha, 1e-6));
  bodyAlpha = shadowedAlpha;

  // Rim and specular from the gradient. The rim is unlit ambient edge brightness;
  // the specular term is the same edge lit from 'light.xy'.
  let rw = rim_weight(d, ou.rim.x);
  let facing = dot(normal, ou.light.xy);
  let spec = pow(clamp(facing, 0.0, 1.0), max(ou.rim.z, 1e-3)) * ou.rim.w;
  let rim = rw * (ou.rim.y + spec) * present;
  if (ou.flags.x > 0.5) {
    colour = colour + vec3f(rim);
  } else {
    // Added light has no premultiplied form of its own — a canvas colour may
    // not exceed its alpha — so the layer carries the light in its opacity:
    // (a·c + rim, a + rim) composites to dst·(1 − a) + a·c + rim − rim·dst,
    // the additive term short of rim × dst. Exact wherever the layer is
    // opaque (an author tint at full strength, or a lit contour pixel whose
    // alpha the rim fills), and never further off than the rim times what
    // shows through — where the mix form ("white over the layer at the rim's
    // weight") is short by the rim times the whole composite, which halved
    // the rim on a tinted panel.
    let carried = clamp(bodyAlpha + rim, 0.0, 1.0);
    colour = min((colour * bodyAlpha + vec3f(rim)) / max(carried, 1e-6), vec3f(1.0));
    bodyAlpha = carried;
  }

  // The material over its own shadow over the page, in one premultiplied vector:
  // the colour is the surface's, weighted by its coverage and by however much of
  // the pixel the layer owns, and the alpha is what the two of them together
  // leave the page. The shadow fills only what the surface's COVERAGE leaves —
  // clipped out of the silhouette exactly as a 'box-shadow' is clipped out of
  // its border box — never what the layer's own transparency leaves: a
  // translucent surface shows the page through it, not its own shadow. (With
  // an opaque body the two are the same quantity, which is how the shadow was
  // first written and why the difference only surfaced with the layer form.)
  let body = encode_output(max(colour, vec3f(0.0)), coverage * bodyAlpha);
  return vec4f(body.rgb, body.a + shadowAlpha * (1.0 - coverage));
}`;
