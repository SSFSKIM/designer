/**
 * Colour transfer and OKLab, under X5.
 *
 * X5 locks v1 calibration to sRGB: captures arrive sRGB-encoded, and every
 * claim is stated in that space. That lock is what makes the encoding boundary
 * *checkable* — and it needs checking, because the two halves of the pipeline
 * want different spaces:
 *
 *   - **Optical math is linear-light.** Blur, edge-spread, rim energy, shadow
 *     falloff and luminance transfer are all statements about how much light
 *     arrives. Averaging sRGB-encoded bytes answers a different question, and
 *     answers it wrongly by roughly the curvature of the transfer function. C6
 *     shipped a gradient that interpolated in encoded space for exactly this
 *     reason; X5's lock is what made it catchable rather than a matter of taste.
 *   - **Perceptual difference is perceptually uniform.** ΔE and tint want a
 *     space where equal numeric steps look like equal steps, which is neither
 *     sRGB nor linear light. That is OKLab.
 *
 * So this module exposes both directions explicitly and every consumer names
 * which one it is using. Nothing here converts implicitly.
 */

/** sRGB inverse EOTF on normalised values: encoded 0..1 → linear-light 0..1. */
export function srgbEncodedToLinear(encoded: number): number {
  return encoded <= 0.04045 ? encoded / 12.92 : Math.pow((encoded + 0.055) / 1.055, 2.4);
}

/** sRGB EOTF on normalised values: linear-light 0..1 → encoded 0..1. */
export function linearToSrgbEncoded(linear: number): number {
  return linear <= 0.0031308 ? linear * 12.92 : 1.055 * Math.pow(linear, 1 / 2.4) - 0.055;
}

/**
 * The 256-entry table for the only conversion this package does per pixel.
 * Captures are 8-bit by X5, so the encoded domain is finite and a table is both
 * faster and exactly as accurate as calling `Math.pow` every time.
 */
const SRGB_BYTE_TO_LINEAR = ((): Float64Array => {
  const table = new Float64Array(256);
  for (let i = 0; i < 256; i += 1) table[i] = srgbEncodedToLinear(i / 255);
  return table;
})();

/** An sRGB-encoded 8-bit sample as linear light in 0..1. */
export function srgbByteToLinear(byte: number): number {
  return SRGB_BYTE_TO_LINEAR[byte] ?? 0;
}

/**
 * Rec.709 luminance weights — the same primaries sRGB is defined against, so
 * this is the correct relative luminance for a linear-light sRGB triple.
 */
export const LUMINANCE_COEFFICIENTS = { r: 0.2126, g: 0.7152, b: 0.0722 } as const;

/** Relative luminance of a linear-light sRGB triple, dimensionless in 0..1. */
export function linearRgbLuminance(r: number, g: number, b: number): number {
  return LUMINANCE_COEFFICIENTS.r * r + LUMINANCE_COEFFICIENTS.g * g + LUMINANCE_COEFFICIENTS.b * b;
}

/** A colour in OKLab. `L` is 0..1 for in-gamut sRGB; `a`/`b` are roughly ±0.4. */
export interface Oklab {
  readonly L: number;
  readonly a: number;
  readonly b: number;
}

/**
 * Linear-light sRGB → OKLab, with Björn Ottosson's published matrices verbatim.
 *
 * The two stages are a linear map into a cone-response-like LMS basis, a cube
 * root (the compressive non-linearity that does the perceptual work), and a
 * second linear map into the opponent Lab axes. Reference values the unit tests
 * pin: linear white → (1, 0, 0); sRGB #ff0000 → (0.62796, 0.22486, 0.12585).
 */
export function linearRgbToOklab(r: number, g: number, b: number): Oklab {
  const l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b;
  const m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b;
  const s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b;

  const lRoot = Math.cbrt(l);
  const mRoot = Math.cbrt(m);
  const sRoot = Math.cbrt(s);

  return {
    L: 0.2104542553 * lRoot + 0.793617785 * mRoot - 0.0040720468 * sRoot,
    a: 1.9779984951 * lRoot - 2.428592205 * mRoot + 0.4505937099 * sRoot,
    b: 0.0259040371 * lRoot + 0.7827717662 * mRoot - 0.808675766 * sRoot,
  };
}

/** An sRGB-encoded 8-bit triple → OKLab, through linear light. */
export function srgbByteToOklab(r: number, g: number, b: number): Oklab {
  return linearRgbToOklab(srgbByteToLinear(r), srgbByteToLinear(g), srgbByteToLinear(b));
}

/**
 * Euclidean distance in OKLab — ΔE_OK, the difference metric the space was
 * built for. Unitless; ~0.01 is around the just-noticeable step for large flat
 * fields, but this package states no thresholds (those are C9's).
 */
export function oklabDistance(x: Oklab, y: Oklab): number {
  const dL = x.L - y.L;
  const da = x.a - y.a;
  const db = x.b - y.b;
  return Math.sqrt(dL * dL + da * da + db * db);
}

/** Chroma: distance from the neutral axis in the OKLab a/b plane. */
export function oklabChroma(c: Oklab): number {
  return Math.hypot(c.a, c.b);
}

/**
 * Hue angle in degrees, 0 at +a (reddish) increasing towards +b (yellowish).
 * Meaningless at zero chroma — a neutral has no hue — so callers reading a hue
 * shift should read the chroma alongside it.
 */
export function oklabHueDegrees(c: Oklab): number {
  return (Math.atan2(c.b, c.a) * 180) / Math.PI;
}

/** Signed shortest angular difference in degrees, in (-180, 180]. */
export function hueDifferenceDegrees(from: number, to: number): number {
  let delta = (to - from) % 360;
  if (delta > 180) delta -= 360;
  if (delta <= -180) delta += 360;
  return delta;
}
