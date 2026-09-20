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
  cssTierOptics,
  resolvedBackdropToneResponse,
  scatterThickness,
  sizeScatterSigmaAt,
  sizeThickness,
  sourceSize,
  CSS_TIER_MAPPING,
  DEFAULT_MATERIAL_PROFILE_DOCUMENT,
} from "@vitreajs/vitrea-web";

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
const LAW_PROFILE = colorSchemeMaterialProfile("light", DEFAULT_MATERIAL_PROFILE_DOCUMENT);
export const LAW_OPTICS = cssTierOptics(LAW_PROFILE, {
  ...CSS_TIER_MAPPING,
  ...DEFAULT_MATERIAL_PROFILE_DOCUMENT.cssTierMapping,
});
export const LAW_SIZE = sourceSize(LAW_PROFILE);
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
  };
}

/** Three decimals, tabular, for the readouts. */
export const fixed = (value: number, places = 3): string => value.toFixed(places);
