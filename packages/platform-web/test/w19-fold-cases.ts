/**
 * The surfaces W19 G1's pins are taken on, and the chain that resolves them.
 *
 * Not a test file (the vitest `include` is `test/**\/*.test.ts`): it is the bed
 * two things share. `author-tint-fold.test.ts` asserts against it, and the
 * recorder that produced `w19-pre-fold-declarations.json` walked the same list
 * on the tree as it stood before the fold landed. One list, so a pin against the
 * recorded strings is a pin on the same surface and not on a similar one.
 *
 * `resolveSurface` is `root.ts`'s chain from the profile to one surface's
 * declarations, in the shipped order, adapted from W19 G0's instrument
 * (`packages/calibration/results/2026-09-05-w19-author-tint-fold/g0/surface.ts`,
 * claims §5.80 §1). Every step is a shipped function of `optics.ts` called the
 * way `root.ts` calls it; the one literal is `DEFAULT_HOST_SHAPE.thickness`,
 * which nothing in this bed overrides. It returns exactly the four things
 * `cssTierDeclarations` is handed on a tinted surface: the interior triple the
 * transfer carries, the UNTINTED conversion `T`, the FOLDED conversion the tier
 * passed as `optics` before W19, and the author's own layer `(L, s)`.
 *
 * The backdrop is a uniform grey at each level, where the group's sampled tone
 * and the filtered backdrop under the surface are one number — the same choice
 * G0's closed form made, and for the same reason: on a structured backdrop the
 * two part company and the identity would be stated at an ambiguous `b`.
 */

import { NOMINAL_ACCESSIBILITY_POLICY, glassTint, type GlassTint } from "@vitreajs/vitrea";

import {
  cssTierFloorAlpha,
  type CssTierEngineCapabilities,
  type CssTierInterior,
  type CssTierSurface,
} from "../src/css-tier";
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
  linearTint,
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
  type MaterialOptics,
  type MaterialSourceOptics,
} from "../src/optics";

/** The engine the `linear` form is gated on — Chromium's conformance row (X9). */
export const CHROMIUM: CssTierEngineCapabilities = {
  referenceFilterInBackdrop: true,
  maskOnBackdropFilter: "yes",
};

/** Gecko's and WebKit's row: no reference filter, so the `rgba()` overlay draws. */
export const PLAIN_BLUR: CssTierEngineCapabilities = {
  referenceFilterInBackdrop: false,
  maskOnBackdropFilter: "no",
};

/** The canonical capsule of the bed the ladder was captured on (`scenes.json`). */
export const CAPSULE = {
  widthCssPx: 120,
  heightCssPx: 44,
  radiusCssPx: 22,
  /** `DEFAULT_HOST_SHAPE.thickness`; nothing on this bed overrides it. */
  thicknessCssPx: 8,
} as const;

/** The charter's six strengths — the bed's own 1.0 and 0.5 among them. */
export const STRENGTHS = [0.1, 0.2, 0.35, 0.5, 0.75, 1.0] as const;

/** The five swept backdrop levels of G0's closed form. */
export const BACKDROPS = [0.15, 0.3, 0.45, 0.6, 0.8] as const;

/** The bed's two seeds: systemOrange and systemBlue. */
export const SEEDS = [
  { id: "orange", srgb: [255, 149, 0] },
  { id: "blue", srgb: [10, 132, 255] },
] as const;

export interface ResolvedSurface {
  readonly interior: CssTierInterior;
  readonly untinted: MaterialOptics;
  readonly folded: MaterialOptics;
  readonly authorLayer:
    | { readonly color: readonly [number, number, number]; readonly strength: number }
    | undefined;
}

const clamp01 = (v: number): number => Math.min(1, Math.max(0, v));

export function resolveSurface(
  box: typeof CAPSULE,
  backdropLinear: number,
  tint: GlassTint | undefined,
): ResolvedSurface {
  const policy = NOMINAL_ACCESSIBILITY_POLICY;
  const size = sourceSize();
  const shade = resolvedTintShade();
  const toneConstants = resolvedBackdropTone();
  const gpuSource = MATERIAL_SOURCE_OPTICS.regular;
  const spanPx = Math.min(box.widthCssPx, box.heightCssPx);
  const tone = {
    rgb: [backdropLinear, backdropLinear, backdropLinear] as [number, number, number],
    luminance: backdropLinear,
    linearLuminance: backdropLinear,
  };

  const surfaceThickness = sizeThickness(spanPx, size);
  const foldedThickness = sizeThicknessUnderPolicy(spanPx, policy.material, size);
  const policyStrength = backdropToneUnderPolicy(policy.material, shade, size.refractionScale);
  const adaptation =
    backdropToneAdaptation(tone.luminance, surfaceThickness, toneConstants) * policyStrength;

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
    resolvedBackdropToneResponse(),
  );
  const adapted = adaptedSourceOptics(responded, tone.rgb, adaptation);
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
  const grip =
    tintToneAdaptation(policy.material.ambientTint, shade) * shade.strength * (1 - adaptation);
  const seedLinear = tint === undefined ? undefined : linearTint(tint);
  const untinted = cssOpticsFromSource(MATERIAL_OPTICS.regular, shadowed, CSS_TIER_MAPPING);
  return {
    interior,
    untinted,
    folded: tintedCssOptics(untinted, shadowed, seedLinear, tone.linearLuminance, grip, shade),
    authorLayer: authorTintLayer(shadowed, seedLinear, tone.linearLuminance, grip, shade),
  };
}

/** The floor alpha every `linear` declaration on this bed keeps on L3. */
export const FLOOR_ALPHA = cssTierFloorAlpha(MATERIAL_OPTICS.regular);

/**
 * A dark interior, which puts `cssTintFormAt` on the `encoded` form — the path
 * this wave must not touch, pinned by replay rather than by argument.
 */
export const DARK_INTERIOR: CssTierInterior = {
  tintAlpha: 0.95,
  tint: [0.04, 0.04, 0.04],
  addedLight: 0,
};

/**
 * One case: a name, the `cssTierDeclarations` argument as the tier was called
 * before W19, and the resolution behind it so a test can state the identity in
 * the same terms the declarations were built from.
 *
 * The argument deliberately carries NO `untintedOptics`. That is what makes the
 * recorded file a pin on today's behaviour: replaying these arguments after the
 * change must return the recorded declarations byte for byte, and a test that
 * wants the fold adds the field itself.
 */
export interface FoldCase {
  readonly name: string;
  readonly args: CssTierSurface;
  readonly resolved: ResolvedSurface;
  readonly strength: number;
  readonly backdrop: number;
  readonly seed: string;
  readonly form: "linear" | "encoded" | "plain-blur";
}

export function foldCases(): FoldCase[] {
  const cases: FoldCase[] = [];
  const base = {
    radii: [
      CAPSULE.radiusCssPx,
      CAPSULE.radiusCssPx,
      CAPSULE.radiusCssPx,
      CAPSULE.radiusCssPx,
    ] as const,
    policy: NOMINAL_ACCESSIBILITY_POLICY,
    spanPx: Math.min(CAPSULE.widthCssPx, CAPSULE.heightCssPx),
    extentsCssPx: [CAPSULE.widthCssPx, CAPSULE.heightCssPx] as const,
    filterIdPrefix: "w19",
  };
  for (const seed of SEEDS) {
    for (const strength of STRENGTHS) {
      for (const backdrop of BACKDROPS) {
        const tint = glassTint(
          [seed.srgb[0] / 255, seed.srgb[1] / 255, seed.srgb[2] / 255],
          strength,
        );
        const resolved = resolveSurface(CAPSULE, backdrop, tint);
        const authorLayer = resolved.authorLayer;
        if (authorLayer === undefined) {
          throw new Error(`w19-fold-cases: no author layer at strength ${String(strength)}`);
        }
        const shared = {
          ...base,
          tint,
          authorLayer: {
            color: [...authorLayer.color] as [number, number, number],
            strength: authorLayer.strength,
          },
          backdropLuminance: backdrop,
        };
        const where = `${seed.id}-s${String(strength)}-b${String(backdrop)}`;
        cases.push({
          name: `linear-${where}`,
          args: {
            ...shared,
            optics: resolved.folded,
            engine: CHROMIUM,
            interior: resolved.interior,
          },
          resolved,
          strength,
          backdrop,
          seed: seed.id,
          form: "linear",
        });
        cases.push({
          name: `encoded-${where}`,
          args: {
            ...shared,
            optics: resolved.folded,
            engine: CHROMIUM,
            interior: DARK_INTERIOR,
            backdropLuminance: 0.02,
          },
          resolved,
          strength,
          backdrop,
          seed: seed.id,
          form: "encoded",
        });
        cases.push({
          name: `plain-blur-${where}`,
          args: {
            ...shared,
            optics: resolved.folded,
            engine: PLAIN_BLUR,
            interior: resolved.interior,
          },
          resolved,
          strength,
          backdrop,
          seed: seed.id,
          form: "plain-blur",
        });
      }
    }
  }
  // The untinted controls, on all three rows: no author layer anywhere, and the
  // `optics` the tier passes is the untinted conversion itself.
  for (const backdrop of BACKDROPS) {
    const resolved = resolveSurface(CAPSULE, backdrop, undefined);
    const shared = { ...base, optics: resolved.untinted, backdropLuminance: backdrop };
    cases.push({
      name: `linear-untinted-b${String(backdrop)}`,
      args: { ...shared, engine: CHROMIUM, interior: resolved.interior },
      resolved,
      strength: 0,
      backdrop,
      seed: "none",
      form: "linear",
    });
    cases.push({
      name: `plain-blur-untinted-b${String(backdrop)}`,
      args: { ...shared, engine: PLAIN_BLUR, interior: resolved.interior },
      resolved,
      strength: 0,
      backdrop,
      seed: "none",
      form: "plain-blur",
    });
  }
  return cases;
}
