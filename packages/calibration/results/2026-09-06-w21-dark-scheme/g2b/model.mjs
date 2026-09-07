// W21 G2b — the CSS tier's derivation, replayed off the shipped exports.
// Reproduces root.ts's per-surface chain for the reference harness's scenes so the
// emitted tint, alpha and CSS alpha can be read as numbers.
import {
  MATERIAL_SOURCE_OPTICS, CSS_TIER_MAPPING,
  sourceOptics, sourceSize, sourceInteriorLight,
  resolvedBackdropTone, resolvedBackdropToneResponse,
  sizeThickness, sizeOcclusionAlphaAt,
  backdropToneAdaptation, toneRespondedSourceOptics, adaptedSourceOptics,
  innerShadowedSourceOptics, interiorShadowKeep, interiorBandLight,
  cssOpticsFromSource, cssTintAlpha, cssTintColor, cssTierOptics,
  cssTintFormAt, linearChainQuantumCodes,
} from "/Users/new/Developer/GitHub/designer/packages/platform-web/dist/index.js";

export const E = (l) => { l = Math.min(1, Math.max(0, l)); return l <= 0.0031308 ? l * 12.92 : 1.055 * Math.pow(l, 1/2.4) - 0.055; };
export const D = (e) => { e = Math.min(1, Math.max(0, e)); return e <= 0.04045 ? e/12.92 : Math.pow((e+0.055)/1.055, 2.4); };
const lum = (c) => 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2];

export function derive(patch, geom, sample, mapping = CSS_TIER_MAPPING) {
  const gpu = sourceOptics(patch);            // per-variant source optics under the patch
  const sizeConstants = sourceSize(patch);
  const interiorLight = sourceInteriorLight(patch);
  const toneConstants = resolvedBackdropTone(patch);
  const response = resolvedBackdropToneResponse(patch);
  const base = cssTierOptics(patch, mapping);

  const span = Math.min(geom.width, geom.height);
  const surfaceThickness = sizeThickness(span, sizeConstants);
  const foldedThickness = surfaceThickness;   // standard regime: the policy fold is identity
  const adaptation = backdropToneAdaptation(sample.luminance, surfaceThickness, toneConstants);

  const occluded = {
    ...gpu.regular,
    tintAlpha: sizeOcclusionAlphaAt(gpu.regular.tintAlpha, foldedThickness, sizeConstants),
  };
  const responded = toneRespondedSourceOptics(
    occluded, sample, surfaceThickness, adaptation, Math.min(1, Math.max(0, toneConstants.max)), response,
  );
  const adapted = adaptedSourceOptics(responded, sample.rgb, adaptation);
  const ig = { widthCssPx: geom.width, heightCssPx: geom.height, radiusCssPx: geom.radius, thicknessCssPx: 8 };
  const present = 1 - adaptation;
  const shadowed = innerShadowedSourceOptics(
    adapted, interiorShadowKeep(gpu.regular, ig, foldedThickness, present, interiorLight),
  );
  const addedLight = interiorBandLight(gpu.regular, ig, present, interiorLight);
  const css = cssOpticsFromSource(base, shadowed, mapping);

  // The renderer's composite at the cell's own backdrop, linear.
  const gpuBody = (1 - shadowed.tintAlpha) * sample.linearLuminance
                + shadowed.tintAlpha * lum(shadowed.tint) + addedLight;
  // This tier's: one rgba() over a backdrop-filter, composited in encoded sRGB.
  const cssBodyEncoded = (1 - css.tintAlpha) * E(sample.luminance)
                       + css.tintAlpha * lum([css.tint[0]/255, css.tint[1]/255, css.tint[2]/255]);
  return {
    thickness: surfaceThickness, adaptation, occludedAlpha: occluded.tintAlpha,
    tint: shadowed.tint, alpha: shadowed.tintAlpha, addedLight,
    cssTint: css.tint, cssAlpha: css.tintAlpha,
    gpuBody, cssBody: D(cssBodyEncoded), cssBodyEncoded,
    form: cssTintFormAt(gpuBody), quantum: linearChainQuantumCodes(gpuBody),
  };
}
