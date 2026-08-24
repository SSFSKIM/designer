/**
 * X5 — the colour pipeline, CPU side.
 *
 * The contract in one line: **internal optical maths in linear light,
 * compositing premultiplied, output sRGB, v1 locked to the sRGB gamut.** Without
 * that lock golden images destabilise across GPUs and browsers and blur energy
 * drifts from the reference, which is the whole reason §Color pipeline exists.
 *
 * Three concrete consequences the rest of the renderer leans on:
 *
 * 1. **Every internal texture is `rgba16float` and holds linear light.** 8-bit
 *    linear would band visibly in a blur pyramid; `rgba16float` is renderable and
 *    filterable everywhere WebGPU is, so no adapter feature is required.
 * 2. **Alpha is normalised at import** (X3). `copyExternalImageToTexture`
 *    delivers premultiplied; `importExternalTexture` delivers unpremultiplied.
 *    Whichever arrives, level 0 of the pyramid is premultiplied linear — one
 *    invariant, checked once at import, instead of an alpha mode threaded
 *    through every downstream pass.
 * 3. **Output is encoded once, at the end of the last pass.** The optics and
 *    highlight canvases are configured `alphaMode: "premultiplied"` in a plain
 *    (non-`-srgb`) 8-bit format, and the browser composites those bytes as sRGB.
 *    So the final step is `encode(linear)` and then `* alpha` — premultiplying in
 *    the *encoded* space, which is what canvas compositing expects. Premultiplying
 *    in linear and then encoding would darken every edge pixel.
 *
 * The transfer functions here are the exact piecewise sRGB curve, not the 2.2
 * approximation: the WGSL uses the same piecewise form, and a test asserts the
 * two agree, so a golden regenerated on one and asserted on the other cannot
 * drift by a code unit.
 */

/**
 * The colour spaces v1 accepts on an imported backdrop.
 *
 * `display-p3` is *accepted and tagged*, never silently treated as sRGB — but v1
 * converts it into the sRGB working space rather than carrying a wide gamut
 * through the pipeline (§Color pipeline: "Display-P3 and HDR/extended-range are
 * future profiles"). Tagging it is what makes the future profile a data change.
 */
export const BACKDROP_COLOR_SPACES = ["srgb", "display-p3"] as const;

export type BackdropColorSpace = (typeof BACKDROP_COLOR_SPACES)[number];

/** How a provider's pixels arrive. Normalised to `premultiplied` at import. */
export const BACKDROP_ALPHA_MODES = ["premultiplied", "unpremultiplied", "opaque"] as const;

export type BackdropAlphaMode = (typeof BACKDROP_ALPHA_MODES)[number];

/** The one internal pixel format. See consequence 1 above. */
export const WORKING_TEXTURE_FORMAT: GPUTextureFormat = "rgba16float";

/** The presentation format for the plane canvases and for golden readback. */
export const OUTPUT_TEXTURE_FORMAT: GPUTextureFormat = "rgba8unorm";

const SRGB_LINEAR_CUTOFF = 0.0031308;
const SRGB_ENCODED_CUTOFF = 0.04045;
const SRGB_SLOPE = 12.92;
const SRGB_ALPHA = 1.055;
const SRGB_OFFSET = 0.055;
const SRGB_GAMMA = 2.4;

/** One channel, sRGB-encoded [0,1] → linear-light [0,1]. */
export function srgbToLinearChannel(c: number): number {
  if (c <= SRGB_ENCODED_CUTOFF) return c / SRGB_SLOPE;
  return Math.pow((c + SRGB_OFFSET) / SRGB_ALPHA, SRGB_GAMMA);
}

/** One channel, linear-light [0,1] → sRGB-encoded [0,1]. */
export function linearToSrgbChannel(c: number): number {
  if (c <= SRGB_LINEAR_CUTOFF) return c * SRGB_SLOPE;
  return SRGB_ALPHA * Math.pow(c, 1 / SRGB_GAMMA) - SRGB_OFFSET;
}

export type Rgb = readonly [r: number, g: number, b: number];

export const srgbToLinear = (c: Rgb): Rgb => [
  srgbToLinearChannel(c[0]),
  srgbToLinearChannel(c[1]),
  srgbToLinearChannel(c[2]),
];

export const linearToSrgb = (c: Rgb): Rgb => [
  linearToSrgbChannel(c[0]),
  linearToSrgbChannel(c[1]),
  linearToSrgbChannel(c[2]),
];

/**
 * Rec.709 luminance weights, applied to **linear** light.
 *
 * Stated explicitly because the common mistake is to weight sRGB-encoded values
 * — which gives a number that tracks perceived lightness loosely and blur energy
 * not at all. The analysis pass reduces linear luminance for the same reason the
 * blur runs in linear light: both are energy integrals.
 */
export const LUMINANCE_WEIGHTS: Rgb = [0.2126, 0.7152, 0.0722];

export function relativeLuminance(linear: Rgb): number {
  return (
    linear[0] * LUMINANCE_WEIGHTS[0] +
    linear[1] * LUMINANCE_WEIGHTS[1] +
    linear[2] * LUMINANCE_WEIGHTS[2]
  );
}

/**
 * Display-P3 → sRGB (linear light, both ends).
 *
 * The 3×3 is the product of P3-to-XYZ and XYZ-to-sRGB under D65. Out-of-gamut
 * results are clamped, which loses saturation on very saturated P3 content — the
 * honest v1 behaviour, and the reason the colour space is *tagged* rather than
 * assumed (a P3 profile can then convert differently without touching a shader).
 */
const P3_TO_SRGB: readonly Rgb[] = [
  [1.224940176280559, -0.224940176280559, 0],
  [-0.042056973821316, 1.042056973821316, 0],
  [-0.019637554590334, -0.078636046901105, 1.098273601491439],
];

export function displayP3ToSrgbLinear(linearP3: Rgb): Rgb {
  const out: number[] = [];
  for (const row of P3_TO_SRGB) {
    out.push(
      Math.min(1, Math.max(0, row[0] * linearP3[0] + row[1] * linearP3[1] + row[2] * linearP3[2])),
    );
  }
  return [out[0] as number, out[1] as number, out[2] as number];
}

/**
 * The colour-space conversion the import pass must apply, as data.
 *
 * Returned as a matrix (row-major 3×3) so the shader takes one uniform and has
 * no branch on colour space. Identity for sRGB — the overwhelmingly common case
 * costs three dot products, which is cheaper than the branch would be.
 */
export function importColorMatrix(space: BackdropColorSpace): Float32Array {
  if (space === "srgb") {
    return new Float32Array([1, 0, 0, 0, 1, 0, 0, 0, 1]);
  }
  const rows = P3_TO_SRGB;
  return new Float32Array([
    ...(rows[0] as Rgb),
    ...(rows[1] as Rgb),
    ...(rows[2] as Rgb),
  ]);
}

/**
 * The alpha normalisation the import pass must apply, as a scalar flag.
 *
 * `0` = already premultiplied, `1` = divide the colour by alpha first, `2` =
 * force alpha to 1. Three modes and one uniform, resolved on the CPU where the
 * provider's contract is known, so no shader ever guesses (X3).
 */
export function alphaNormalisationMode(mode: BackdropAlphaMode): number {
  switch (mode) {
    case "premultiplied":
      return 0;
    case "unpremultiplied":
      return 1;
    case "opaque":
      return 2;
  }
}

/**
 * Encode a linear-light colour and its alpha the way the output pass does, for
 * tests and for golden-image expectations computed on the CPU.
 */
export function encodeOutput(linear: Rgb, alpha: number): readonly [number, number, number, number] {
  const a = Math.min(1, Math.max(0, alpha));
  const encoded = linearToSrgb(linear);
  return [encoded[0] * a, encoded[1] * a, encoded[2] * a, a];
}

/** The same, quantised to the 8-bit bytes a golden PNG holds. */
export function encodeOutputBytes(linear: Rgb, alpha: number): readonly number[] {
  return encodeOutput(linear, alpha).map((c) => Math.round(Math.min(1, Math.max(0, c)) * 255));
}
