/**
 * W19 G0 — `root.ts`'s chain from the profile to one surface's declarations, in one place.
 *
 * Two of this spike's scripts need the same resolution — the closed form (a, d) evaluates it over a
 * swept uniform backdrop, and the prediction (b) evaluates it at each captured cell's own sampled
 * tone — and a second copy of a fourteen-step chain is a second set of numbers to drift. Every step
 * below is the shipped function called in the shipped order; nothing here restates an expression
 * `optics.ts` owns, and the one literal is `DEFAULT_HOST_SHAPE.thickness`, which the calibration
 * pages never override.
 *
 * What it returns is exactly what `cssTierDeclarations` is handed on a tinted surface: the interior
 * triple the transfer carries, the UNTINTED conversion's optics (`T`), the FOLDED optics `root.ts`
 * passes today (`T_folded`), and the author's own layer (`L`, `s`).
 */

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import {
  CSS_TIER_MAPPING,
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_OPTICS,
  adaptedSourceOptics,
  authorTintLayer,
  backdropToneAdaptation,
  backdropToneUnderPolicy,
  cssOpticsFromSource,
  innerShadowedSourceOptics,
  interiorBandLight,
  interiorShadowKeep,
  occlusionAlphaUnderPolicy,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  resolvedTintShade,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sizeThicknessUnderPolicy,
  sourceSize,
  tintToneAdaptation,
  tintedCssOptics,
  toneRespondedSourceOptics,
  type CssTierInterior,
  type MaterialOptics,
  type MaterialSourceOptics,
} from "@vitreajs/vitrea-web";

/** The surface's own box, in CSS px — the measured border box `root.ts` reads the size law from. */
export interface SurfaceBox {
  readonly widthCssPx: number;
  readonly heightCssPx: number;
  readonly radiusCssPx: number;
  /** `DEFAULT_HOST_SHAPE.thickness` unless a page overrode it. */
  readonly thicknessCssPx: number;
}

export interface ResolvedSurface {
  readonly interior: CssTierInterior;
  readonly untinted: MaterialOptics;
  readonly folded: MaterialOptics;
  readonly authorLayer:
    | { readonly color: readonly [number, number, number]; readonly strength: number }
    | undefined;
  readonly grip: number;
  readonly policySource: MaterialSourceOptics;
}

const clamp01 = (v: number): number => Math.min(1, Math.max(0, v));

export function resolveSurface(
  box: SurfaceBox,
  tone: { readonly rgb: readonly [number, number, number]; readonly luminance: number; readonly linearLuminance: number },
  seedLinear: { readonly color: readonly [number, number, number]; readonly strength: number } | undefined,
): ResolvedSurface {
  const policy = NOMINAL_ACCESSIBILITY_POLICY;
  const size = sourceSize();
  const shade = resolvedTintShade();
  const toneConstants = resolvedBackdropTone();
  const response = resolvedBackdropToneResponse();
  const gpuSource = MATERIAL_SOURCE_OPTICS.regular;
  const spanPx = Math.min(box.widthCssPx, box.heightCssPx);

  const surfaceThickness = sizeThickness(spanPx, size);
  const foldedThickness = sizeThicknessUnderPolicy(spanPx, policy.material, size);
  const policyStrength = backdropToneUnderPolicy(policy.material, shade, size.refractionScale);
  const adaptation = backdropToneAdaptation(tone.luminance, surfaceThickness, toneConstants) * policyStrength;

  const occluded: MaterialSourceOptics = {
    ...gpuSource,
    tintAlpha: sizeOcclusionAlphaAt(
      occlusionAlphaUnderPolicy(gpuSource.tintAlpha, policy.material.occlusion),
      foldedThickness,
      size,
    ),
  };
  const responded = toneRespondedSourceOptics(
    occluded,
    tone,
    surfaceThickness,
    adaptation,
    (policyStrength >= 0.999 ? 1 : 0) * clamp01(toneConstants.max),
    response,
  );
  const adapted = adaptedSourceOptics(responded, tone.rgb as never, adaptation);
  const present = 1 - adaptation;
  const shadowed = innerShadowedSourceOptics(
    adapted,
    interiorShadowKeep(gpuSource, box, foldedThickness, present),
  );
  const interior: CssTierInterior = {
    tintAlpha: shadowed.tintAlpha,
    tint: [shadowed.tint[0], shadowed.tint[1], shadowed.tint[2]],
    addedLight: interiorBandLight(gpuSource, box, present),
  };
  const grip = tintToneAdaptation(policy.material.ambientTint, shade) * shade.strength * (1 - adaptation);
  const untinted = cssOpticsFromSource(MATERIAL_OPTICS.regular, shadowed, CSS_TIER_MAPPING);
  return {
    interior,
    untinted,
    folded: tintedCssOptics(untinted, shadowed, seedLinear as never, tone.linearLuminance, grip, shade),
    authorLayer: authorTintLayer(shadowed, seedLinear as never, tone.linearLuminance, grip, shade) as never,
    grip,
    policySource: shadowed,
  };
}
