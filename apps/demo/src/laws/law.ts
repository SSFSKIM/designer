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
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_SIZE,
  scatterThickness,
  sizeScatterSigmaAt,
  sizeThickness,
} from "@vitreajs/vitrea-web";

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
    small: backdropToneResponseLevel(encoded, sizeThickness(TONE_SPANS.small)),
    large: backdropToneResponseLevel(encoded, sizeThickness(TONE_SPANS.large)),
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
  const sharp = MATERIAL_OPTICS.regular.blurRadius;
  // The mix is the depth ramp's per-surface projection (W13 G1) — its area
  // average over the plate's OWN box, which is why the extents come in: a plate
  // of 320 × span projects a different mix from a square of the span, and the
  // runtime writes the box's number. This readout reports it at dpr 1, which is
  // what the CSS tier renders and is NOT what the GPU tier mixes per pixel — the
  // readout's device-scale gap is already logged in `specs/tech-debt-tracker.md`.
  const mix = scatterThickness(spanPx, fold, MATERIAL_SOURCE_SIZE, 1, extentsCssPx);
  return {
    mix,
    sharp,
    scatter: sharp * MATERIAL_SOURCE_SIZE.sizeScatterGainMax,
    single: sizeScatterSigmaAt(sharp, mix),
  };
}

/** Three decimals, tabular, for the readouts. */
export const fixed = (value: number, places = 3): string => value.toFixed(places);
