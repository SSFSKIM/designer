/**
 * The laws, evaluated for the readouts.
 *
 * Every function here is a thin call into the constants and curves
 * `@vitreajs/vitrea-web` publishes, so the number beside a control is the
 * runtime's own arithmetic and not a second opinion typed into the page. Nothing
 * is tuned here; the material-profile seam is read, never written.
 */

import {
  backdropToneResponseLevel,
  colorSchemeMaterialProfile,
  cssShadowBlurRadius,
  cssTierOptics,
  cssTierShadowAlpha,
  mergeMaterialProfiles,
  outerShadowFalloff,
  outerShadowOcclusionAt,
  outerShadowSigmaPx,
  outerShadowUnderPolicy,
  resolvedBackdropToneResponse,
  scatterThickness,
  sizeScatterSigmaAt,
  sizeThickness,
  sizeThicknessUnderPolicy,
  sourceOuterShadow,
  sourceSize,
  CSS_TIER_MAPPING,
  DEFAULT_MATERIAL_PROFILE_DOCUMENT,
  type GlassMaterialProfileDocument,
  type RendererMaterialProfile,
} from "@vitreajs/vitrea-web";

/**
 * The material half of the resolved accessibility policy, derived from the
 * function that consumes it rather than imported.
 *
 * `ResolvedMaterialPolicy` is core's type and neither `@vitreajs/vitrea-web` nor
 * `@vitreajs/vitrea-react` re-exports it, so a page that needs to name it has to
 * take it from a signature. This is the one both tiers' shadow fold reads, so it
 * cannot drift from what the runtime actually applies.
 */
type MaterialPolicy = Parameters<typeof outerShadowUnderPolicy>[1];

/**
 * The material this page is drawing, resolved rather than read off a module
 * constant (W29 G4).
 *
 * `MATERIAL_OPTICS` and `MATERIAL_SOURCE_SIZE` are the renderer's own defaults
 * through the shipped CSS mapping, and until 0.19.0 that WAS what a root drew.
 * It is not any more: the renderer's defaults are held still at the macOS 26.5
 * light material on purpose (W29 Decision Log 1 (i)) and a root resolves a
 * selected document over them, so a page that kept quoting the constants would
 * have printed one material's arithmetic beside another material's pixels —
 * exactly the second opinion this module's header says it is not.
 *
 * The light endpoint of the default document, because `laws/main.tsx` builds its
 * root with no `colorScheme` and the default is light. A scheme pin here would
 * have to move these three with it.
 */
/**
 * The document this page's root draws, named once.
 *
 * `laws/main.tsx` builds its root with no `materialProfileDocument`, so the root
 * resolves the package default — and that is the page's own construction rather
 * than a guess about the runtime. What is NOT assumed is which ENDPOINT of it
 * drew: `endpointByDigest` below takes that from the group's own reported digest
 * and refuses to name one when the digest matches none of the four.
 */
export const LAWS_DOCUMENT = DEFAULT_MATERIAL_PROFILE_DOCUMENT;

const LAW_PROFILE = colorSchemeMaterialProfile("light", LAWS_DOCUMENT);
export const LAW_OPTICS = cssTierOptics(LAW_PROFILE, {
  ...CSS_TIER_MAPPING,
  ...DEFAULT_MATERIAL_PROFILE_DOCUMENT.cssTierMapping,
});
export const LAW_SIZE = sourceSize(LAW_PROFILE);
export const LAW_SHADOW = sourceOuterShadow(LAW_PROFILE);
const LAW_RESPONSE = resolvedBackdropToneResponse(LAW_PROFILE);

/** Linear light to the sRGB transfer function, 0..1 in and out. */
export function srgbEncode(linear: number): number {
  const v = Math.min(1, Math.max(0, linear));
  return v <= 0.0031308 ? v * 12.92 : 1.055 * v ** (1 / 2.4) - 0.055;
}

/** The ground colour for a declared linear level: achromatic, so the hint is exact. */
export function groundFill(level: number): string {
  const channel = Math.round(srgbEncode(level) * 255);
  return `rgb(${channel} ${channel} ${channel})`;
}

/** The spans the tone stage compares: the size law's floor and past its ceiling. */
export const TONE_SPANS = { small: 40, large: 112 } as const;

export interface ToneLaw {
  /** The backdrop's level as the reference reads it: the mean in encoded sRGB. */
  readonly encoded: number;
  /** The interior level the law targets for the small plate. */
  readonly small: number;
  /** The same for the large plate, whose thickness sits at the law's ceiling. */
  readonly large: number;
}

/**
 * W9. A flat ground's encoded mean is its encoded value, so the response curve
 * can be evaluated exactly for the two plates the stage shows.
 */
export function toneLaw(level: number): ToneLaw {
  const encoded = srgbEncode(level);
  return {
    encoded,
    small: backdropToneResponseLevel(
      encoded,
      sizeThickness(TONE_SPANS.small, LAW_SIZE),
      LAW_RESPONSE,
    ),
    large: backdropToneResponseLevel(
      encoded,
      sizeThickness(TONE_SPANS.large, LAW_SIZE),
      LAW_RESPONSE,
    ),
  };
}

export interface BodyLaw {
  /** How much of the scatter component the mix carries at this span, 0..1. */
  readonly mix: number;
  /** The sharp component's width, CSS px. */
  readonly sharp: number;
  /** The scatter component's width, CSS px. */
  readonly scatter: number;
  /** The one width the CSS tier's single `backdrop-filter` takes instead. */
  readonly single: number;
  /**
   * The outer shadow's σ at the same span, CSS px (W30; claims §5.159 §1).
   *
   * On this page because this control is the only span axis it has, and because
   * the span is now an argument to two laws rather than one: the body's mix has
   * always ridden it, and since 0.20.0 so does the shadow's blur. Reading them
   * off one slider is what makes "the casting span" visible as a quantity the
   * material is a function of, rather than as two coincidences.
   */
  readonly shadowSigma: number;
}

/**
 * W11c G1. `fold` is the refraction scale the accessibility policy allows (1 at
 * nominal, less under reduce transparency), which is the same fold the
 * thickness facets ride.
 */
export function bodyLaw(
  spanPx: number,
  fold: number,
  extentsCssPx?: readonly [number, number],
): BodyLaw {
  const sharp = LAW_OPTICS.regular.blurRadius;
  // The mix is the depth ramp's per-surface projection (W13 G1) — its area
  // average over the plate's OWN box, which is why the extents come in: a plate
  // of 320 × span projects a different mix from a square of the span, and the
  // runtime writes the box's number. This readout reports it at dpr 1, which is
  // what the CSS tier renders and is NOT what the GPU tier mixes per pixel — the
  // readout's device-scale gap is already logged in `specs/tech-debt-tracker.md`.
  const mix = scatterThickness(spanPx, fold, LAW_SIZE, 1, extentsCssPx);
  return {
    mix,
    sharp,
    scatter: sharp * LAW_SIZE.sizeScatterGainMax,
    single: sizeScatterSigmaAt(sharp, mix, LAW_SIZE),
    // Not folded by the policy: the σ law is the material's own and the
    // accessibility fold applies to the refraction and the frost, not to the
    // shadow's width. `outerShadowSigmaPx` is the same function both tiers
    // evaluate, which is what keeps this a readout and not a second opinion.
    shadowSigma: shadowSigmaAt(spanPx),
  };
}

/**
 * The outer shadow's σ at one span, CSS px — `bodyLaw`'s own term, exported so
 * the prose beside the readout can be evaluated rather than typed.
 *
 * Added 2026-09-20 by the W30 G4 review closure (claims §5.160 §9): the note
 * above the readout quoted the two ends of the control as literals, which is
 * exactly the sentence a refit leaves stale while every number under it moves.
 */
export const shadowSigmaAt = (spanPx: number): number =>
  outerShadowSigmaPx(LAW_SHADOW, spanPx);

/** Three decimals, tabular, for the readouts. */
export const fixed = (value: number, places = 3): string => value.toFixed(places);

/* ── The outer shadow, at the endpoint the runtime says drew ───────────────── */

/**
 * The material an endpoint of a document resolves to, found by the DIGEST the
 * runtime reported for the group rather than by the page's own idea of which
 * pose is on.
 *
 * Every other readout on this page evaluates the light ACTIVE endpoint, because
 * every other law it shows is a property of the active material and the page
 * builds its root with no scheme. The shadow section cannot do that: its whole
 * second control is the window pose, and the two poses draw two different
 * documents. Rather than track the pose in page state and hope the root agrees,
 * the section asks the group what it drew — `GlassGroupState.materialDocument`
 * carries `resolvedMaterialSha256`, the digest over the fully resolved material
 * — and looks that digest up among the selected document's four endpoints. A
 * digest that matches none of them is an app that tuned the material, and the
 * readout says so instead of printing numbers from an endpoint nothing drew.
 *
 * A receded endpoint's patch is a DIFFERENCE over the active endpoint of its own
 * scheme (`material-document.ts`), never a whole material, so it is composed the
 * way the root composes it and never read alone.
 */
export interface ResolvedEndpoint {
  readonly profileKey: string | undefined;
  readonly pose: "active" | "receded";
  readonly scheme: "light" | "dark";
  readonly patch: RendererMaterialProfile | undefined;
}

export function endpointByDigest(
  document: GlassMaterialProfileDocument,
  digest: string | undefined,
): ResolvedEndpoint | undefined {
  if (digest === undefined) return undefined;
  for (const scheme of ["light", "dark"] as const) {
    const active = document.active[scheme];
    if (active.resolvedMaterialSha256 === digest) {
      return { profileKey: active.profileKey, pose: "active", scheme, patch: active.patch };
    }
    const receded = document.receded[scheme];
    if (receded.resolvedMaterialSha256 === digest) {
      return {
        profileKey: receded.profileKey,
        pose: "receded",
        scheme,
        patch: mergeMaterialProfiles(active.patch, receded.patch),
      };
    }
  }
  return undefined;
}

/** Where the depth is read, in CSS px below the caster's own contour. */
export const SHADOW_DEPTHS_CSS_PX = [3, 12, 24] as const;

export interface ShadowLaw {
  /** `σ(span)`, CSS px — the law, evaluated at the endpoint that drew. */
  readonly sigmaPx: number;
  /** The blur radius the CSS tier writes for that σ: `2σ`, Backgrounds 3's convention. */
  readonly cssBlurPx: number;
  /** `spreadPx` — how far the shadow's silhouette is grown past the caster's. */
  readonly outsetPx: number;
  /** `offsetPx` — how far down it is displaced. */
  readonly offsetPx: number;
  /** The peak occlusion at this span and backdrop: the light the shadow removes at most. */
  readonly peakOcclusion: number;
  /** The compositing alpha the CSS tier writes, rounded as `outerShadowDeclaration` rounds it. */
  readonly cssAlpha: number;
  /** The occlusion at each of `SHADOW_DEPTHS_CSS_PX`, directly below the contour. */
  readonly depth: readonly number[];
}

/**
 * The exterior's own numbers at one span, from one endpoint's material.
 *
 * Every term is the runtime's own function evaluated on the runtime's own
 * constants — `outerShadowSigmaPx` is the law both tiers read, `outerShadowUnderPolicy`
 * is the accessibility fold the tier applies before it draws, `outerShadowOcclusionAt`
 * is the amplitude, `outerShadowFalloff` is the curve, and `cssTierShadowAlpha`
 * is exactly what becomes the `box-shadow`'s alpha. Nothing here is a second
 * opinion, which is why the page's e2e pin can assert the readout against the
 * shadow the tier actually drew.
 *
 * **The depth is read BELOW the caster, and the offset is why.** The shader
 * evaluates the falloff on the field's signed distance at the position shifted by
 * `offsetPx`, so a point `d` CSS px below the contour sits `d − offsetPx − spreadPx`
 * outside the shadow's own silhouette. Reading the three depths anywhere else
 * would need a different expression per side, and below is where the shadow is.
 */
export function shadowLaw(input: {
  readonly patch: RendererMaterialProfile | undefined;
  readonly spanPx: number;
  readonly backdropLuminance: number;
  readonly policy: MaterialPolicy | undefined;
}): ShadowLaw {
  const source = sourceOuterShadow(input.patch);
  const shadow =
    input.policy === undefined ? source : outerShadowUnderPolicy(source, input.policy);
  const thickness =
    input.policy === undefined
      ? sizeThickness(input.spanPx, LAW_SIZE)
      : sizeThicknessUnderPolicy(input.spanPx, input.policy, LAW_SIZE);
  const sigmaPx = outerShadowSigmaPx(shadow, input.spanPx);
  const peakOcclusion = outerShadowOcclusionAt(
    shadow,
    input.backdropLuminance,
    input.spanPx,
    thickness,
  );
  return {
    sigmaPx,
    cssBlurPx: cssShadowBlurRadius(sigmaPx),
    outsetPx: shadow.spreadPx,
    offsetPx: shadow.offsetPx,
    peakOcclusion,
    cssAlpha:
      Math.round(
        cssTierShadowAlpha(shadow, input.backdropLuminance, input.spanPx, thickness) * 1000,
      ) / 1000,
    depth: SHADOW_DEPTHS_CSS_PX.map(
      (distance) =>
        peakOcclusion
        * outerShadowFalloff(distance - shadow.offsetPx - shadow.spreadPx, sigmaPx),
    ),
  };
}
