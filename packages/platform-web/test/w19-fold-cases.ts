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

/**
 * The band's source optics AT THE MATERIAL THE RECORDING WAS TAKEN ON, frozen.
 *
 * `w19-pre-fold-declarations.json` was recorded by walking this list on the tree
 * as it stood BEFORE the fold landed, and that tree cannot be re-run: the code
 * that produced it is gone, so the file can never be re-recorded and its bytes
 * are the whole of the "nothing else moved" claim. A bed that read the live
 * mirror would therefore turn every later material change into a failure of a
 * pin that is not about the material at all.
 *
 * So the constants the recording depended on are named here. `specularGain` is
 * the first one to move — W22 G1 fitted it 0.55 → 0 (claims §5.94 §3) and it
 * enters these declarations through `interiorBandLight`'s `addedLight` — and it
 * is frozen at the recorded value rather than tracked. What this bed asserts is
 * a DIFFERENCE (passing `untintedOptics` changes nothing), and a difference is
 * stated at fixed constants or it is not stated at all. The shipped value's own
 * pins are `interior-level.test.ts` and `tier-coherence.test.ts`.
 *
 * The lit edge joined it in W24 (claims §5.108 §1). The recording was taken on
 * a rim of one brightness the whole way round, so `rimLitExponent` is frozen at
 * 0 here — the value at which the directional factor is 1 for every normal — and
 * the collapse's transmission is frozen at 0 in the `adaptedSourceOptics` call
 * below for the same reason: a difference is stated at fixed constants or it is
 * not stated at all.
 *
 * The rim joined it in W23 (claims §5.100). The recording was taken while the
 * rim was the constant 0.18 and nothing else — no law, no gain on the surface's
 * own level, and nothing left of it once a material had collapsed — so all three
 * are frozen at what the recording held: `rimAlpha` 0.18, `rimLevelGain` 0, and
 * the collapsed rim 0 where `resolveSurface` calls `adaptedSourceOptics` below.
 * The rim reaches these declarations twice, through `interiorBandLight`'s
 * `addedLight` and through the border alpha, and the shipped constants' own pins
 * are `interior-level.test.ts`, `backdrop-tone.test.ts` and `tier-coherence.test.ts`.
 */
/**
 * The band's derived light the recording carried, frozen as a NUMBER because it
 * can no longer be derived (W24; claims §5.108 §1).
 *
 * `interiorBandLight` produced it at `specularGain` 0.55 over the rim of 0.18
 * above, and W24 retired the one-sided specular from the band with the rim it
 * modelled — so freezing the constants is no longer enough to reproduce the
 * recording and the value it produced is frozen instead. It is the same
 * 0.009278741795284628 every one of the 65 transfers in
 * `w19-pre-fold-declarations.json` carries, at the one box and the one presence
 * this bed declares; `interiorBandLight`'s own linearity in `present` is what
 * lets it be scaled rather than re-derived, and the shipped derivation's pins
 * are `interior-level.test.ts` and `tier-coherence.test.ts`.
 */
const RECORDED_BAND_LIGHT = 0.009278741795284628;

export const RECORDED_SOURCE_OPTICS: MaterialSourceOptics = {
  ...MATERIAL_SOURCE_OPTICS.regular,
  specularGain: 0.55,
  rimLitExponent: 0,
  rimAlpha: 0.18,
  rimLevelGain: 0,
};

/**
 * The mapping the recording was taken through, frozen for the same reason and in
 * the same breath as the rim (W23; claims §5.100 §4).
 *
 * `borderAlphaPerRimAlpha` is a ratio whose NUMERATOR changed scale: it converts
 * the renderer's resolved rim amplitude into this tier's one inset shadow, and
 * W23 re-based it 1.95 → 0.64 because the amplitude it divides into grew about
 * threefold when the rim became a law rather than a constant. The shipped border
 * is the same border either way; a bed frozen at the recording's 0.18 amplitude
 * has to be frozen at the recording's 1.95 with it, or it would state the old
 * rim through the new tier's scale and land on a border no tree ever drew.
 *
 * Per variant since the review fix, because the shipped constant is: the clear
 * variant's rim never became a law and keeps 1.95 in the shipped mapping too, so
 * only the regular entry is a freeze.
 */
export const RECORDED_MAPPING = {
  ...CSS_TIER_MAPPING,
  borderAlphaPerRimAlpha: { regular: 1.95, clear: 1.95 },
} as const;

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
  const gpuSource = RECORDED_SOURCE_OPTICS;
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
  // `rimCollapsed` 0: the tree this bed was recorded on faded the rim to nothing,
  // and W23's 0.038 is a later reading of the reference (claims §5.100 §3).
  const adapted = adaptedSourceOptics(responded, tone.rgb, adaptation, 0, undefined, 0);
  const present = 1 - adaptation;
  const shadowed = innerShadowedSourceOptics(
    adapted,
    interiorShadowKeep(gpuSource, box, foldedThickness, present),
  );
  const interior: CssTierInterior = {
    tintAlpha: shadowed.tintAlpha,
    tint: [shadowed.tint[0], shadowed.tint[1], shadowed.tint[2]],
    addedLight: present * RECORDED_BAND_LIGHT,
  };
  const grip =
    tintToneAdaptation(policy.material.ambientTint, shade) * shade.strength * (1 - adaptation);
  const seedLinear = tint === undefined ? undefined : linearTint(tint);
  const untinted = cssOpticsFromSource(MATERIAL_OPTICS.regular, shadowed, RECORDED_MAPPING);
  return {
    interior,
    untinted,
    // `rimTintChroma` 0 is frozen with the rest of the recording (W23 G3): the
    // painted rim's colour landed after this JSON was taken, and a replay that
    // spent the rim's light in the paint would state today's border through
    // yesterday's tree — the same freeze `RECORDED_SOURCE_OPTICS` is.
    folded: tintedCssOptics(untinted, shadowed, seedLinear, tone.linearLuminance, grip, shade, 0),
    authorLayer: authorTintLayer(shadowed, seedLinear, tone.linearLuminance, grip, shade),
  };
}

/** The floor alpha every `linear` declaration on this bed keeps on L3. */
export const FLOOR_ALPHA = cssTierFloorAlpha(MATERIAL_OPTICS.regular);

/**
 * A dark interior, which puts the boundary on the `encoded` form — the path W19
 * must not touch, pinned by replay rather than by argument.
 */
export const DARK_INTERIOR: CssTierInterior = {
  tintAlpha: 0.95,
  tint: [0.04, 0.04, 0.04],
  addedLight: 0,
};

/**
 * The untinted conversion that DESCRIBES that interior (W21 Decision Log 4 (a)).
 *
 * The boundary is no longer the chain's reach alone but the nearer of the two
 * drawings, and the drawing the encoded form would make is read off the material's
 * own conversion — so a row that pairs one material's `optics` with another's
 * `interior` no longer states a boundary case, it states a contradiction. This is
 * the conversion of `DARK_INTERIOR` itself, exact at the mapping's own anchor by
 * `cssTintAlpha`'s construction, which is what makes the encoded form nearer
 * there. It changes no declaration: on the encoded form the untinted conversion
 * is read for the boundary and for nothing else, which is why the recorded bytes
 * still describe these rows.
 */
export const DARK_UNTINTED: MaterialOptics = cssOpticsFromSource(
  MATERIAL_OPTICS.regular,
  {
    ...RECORDED_SOURCE_OPTICS,
    tintAlpha: DARK_INTERIOR.tintAlpha,
    tint: DARK_INTERIOR.tint,
  },
  RECORDED_MAPPING,
);

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
  /**
   * The untinted conversion that describes THIS row's `optics` — `resolved`'s on
   * the two rows that draw the material it resolved, and `DARK_UNTINTED` on the
   * encoded row, whose interior is a different material by construction (W21
   * Decision Log 4 (a)).
   */
  readonly untinted: MaterialOptics;
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
          untinted: resolved.untinted,
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
          untinted: DARK_UNTINTED,
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
          untinted: resolved.untinted,
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
      untinted: resolved.untinted,
      strength: 0,
      backdrop,
      seed: "none",
      form: "linear",
    });
    cases.push({
      name: `plain-blur-untinted-b${String(backdrop)}`,
      args: { ...shared, engine: PLAIN_BLUR, interior: resolved.interior },
      resolved,
      untinted: resolved.untinted,
      strength: 0,
      backdrop,
      seed: "none",
      form: "plain-blur",
    });
  }
  return cases;
}
