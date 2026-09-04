/**
 * W17 G0 (d) — the carrier, as it was built and measured. **Reverted, kept here as evidence.**
 *
 * This file lived at `packages/platform-web/src/w17-carrier.ts` for the duration of §4's captures
 * and was deleted before anything was committed; `carrier-patch/call-sites.diff` beside it is the
 * two edits that reached it. It is preserved rather than described because §4's readings are only
 * as good as the arithmetic that produced them, and a paragraph is not that arithmetic.
 *
 * The carrier is the intercept and slope of an `feComponentTransfer` stage inside the CSS tier's
 * existing linear-light reference filter, solved from two equations so that the tier's encoded
 * output matches the RENDERER's linear-light composite in mean and in derivative with respect to
 * the backdrop level, at the group's own sampled level, with the renderer's derived excess added in
 * linear light first.
 *
 * ## Why the stage goes on the SHARP filter alone
 *
 * The tier's body is two layers: L1 filters the page at the sharp width, L2 filters L1's own output
 * at the heavy step and is masked by the renderer's ramp. A Gaussian is linear and normalised, so
 * `blur(m·b + c) = m·blur(b) + c` — an affine applied at L1 passes through L2 unchanged and reaches
 * the composite exactly once. Applying it at both layers would apply it twice (`m²b + mc + c`), and
 * applying it at L2 alone would leave the sharp share untransformed where the mask is open.
 *
 * ## The two equations
 *
 * Write `E` for the sRGB encode and `D` for its inverse. The renderer's composite at backdrop level
 * `b` is `M(b) = (1 − α)·b + α·T` in linear light, and the target this wave aims the tier at is
 * `G(b) = E(M(b) + X)` with `X` the derived excess of the terms the tier does not draw. The tier
 * lays its `rgba()` over the filtered backdrop in the ENCODED space, so its output is
 *
 *     F(b) = E(m·b + c)·(1 − α′) + Ec·α′
 *
 * with `α′` and `Ec` the conversion the tier already writes. Requiring `F(b₀) = G(b₀)` and
 * `F′(b₀) = G′(b₀)` gives the intercept and the slope in closed form, and no third unknown is
 * introduced — the overlay stays exactly what `cssTintAlpha` and `cssTintColor` produce today.
 *
 * Everything here is achromatic. The probe cells are untinted, the profile's tint is white and the
 * response solve's shift is achromatic, so one scalar per surface is the whole conversion; a
 * chromatic tint would need the same solve per channel and is not what this spike measured.
 */

export interface W17CarrierTransfer {
  readonly slope: number;
  readonly intercept: number;
}

const clamp01 = (x: number): number => Math.min(1, Math.max(0, x));
const encode = (l: number): number => {
  const v = clamp01(l);
  return v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(v, 1 / 2.4) - 0.055;
};
const decode = (e: number): number => {
  const v = clamp01(e);
  return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
};
/** d/dl of the encode, needed for the derivative equation. */
const encodeSlope = (l: number): number => {
  const v = clamp01(l);
  return v <= 0.0031308 ? 12.92 : (1.055 / 2.4) * Math.pow(Math.max(v, 1e-6), 1 / 2.4 - 1);
};

/**
 * The renderer's excess over its own body, from the profile's numbers and the surface's geometry
 * (W17 G0 (c)).
 *
 * The rim's ambient term and the highlight are the same 1.5 CSS px band, one flat and one lit, and
 * both are added in linear light. Their area means over a rounded rectangle come out of the co-area
 * formula: the inward offset of a rounded rectangle by `u` keeps its straight runs and shrinks only
 * its corner arcs, so `P(u) = 2(W − 2r) + 2(H − 2r) + 2π(r − u)` exactly, and
 * `∫₀^w (1 − u/w)²·P(u) du = P_s·w/3 + 2π(r·w/3 − w²/12)`. The highlight carries the specular
 * factor, which varies around the contour, so its band integral is the same weight times the
 * contour integral of `clamp(n̂ · lightDirection, 0, 1)^p`, evaluated on the contour itself: four
 * straight runs with axis-aligned normals and four quarter arcs sampled in angle.
 *
 * The lens contributes nothing to first order — a displacement moves the mean of a statistically
 * homogeneous backdrop by zero — and the outer shadow's lift is drawn outside the coverage and is
 * zero inside by construction. Both are omitted, and §3 records what they measure instead.
 *
 * `rimWidth`, `specularPower`, `specularGain` and the light direction are the renderer's, restated
 * here because `MaterialSourceOptics` mirrors only the four fields this tier converts. A landed
 * form would take them across the boundary properly; this was a spike.
 */
export function w17DerivedExcess(options: {
  readonly widthCssPx: number;
  readonly heightCssPx: number;
  readonly radiusCssPx: number;
  readonly rimAlpha: number;
  readonly present: number;
}): number {
  const { widthCssPx: w, heightCssPx: h } = options;
  const r = Math.min(options.radiusCssPx, Math.min(w, h) / 2);
  const RIM_WIDTH = 1.5;
  const SPECULAR_POWER = 6;
  const SPECULAR_GAIN = 0.55;
  const LIGHT: readonly [number, number] = [-0.3714, -0.9285];

  const area = w * h - (4 - Math.PI) * r * r;
  const straight = 2 * (w - 2 * r) + 2 * (h - 2 * r);
  // The band's depth weight, ∫₀^w (1 − u/w)² du = w/3, and the corner arcs' shrinkage.
  const bandStraight = (RIM_WIDTH / 3) * straight;
  const bandCorners = 2 * Math.PI * ((r * RIM_WIDTH) / 3 - (RIM_WIDTH * RIM_WIDTH) / 12);
  const rim = (options.rimAlpha * options.present * (bandStraight + bandCorners)) / area;

  // The specular's contour integral. The straight runs' normals are the four axes; the corner arcs
  // sweep a quarter turn each, and together they are one full turn sampled uniformly.
  const lit = (nx: number, ny: number): number =>
    Math.pow(Math.max(0, nx * LIGHT[0] + ny * LIGHT[1]), SPECULAR_POWER);
  let specContour =
    (w - 2 * r) * (lit(0, -1) + lit(0, 1)) + (h - 2 * r) * (lit(-1, 0) + lit(1, 0));
  const samples = 2048;
  for (let i = 0; i < samples; i += 1) {
    const angle = ((i + 0.5) / samples) * 2 * Math.PI;
    specContour += lit(Math.cos(angle), Math.sin(angle)) * ((2 * Math.PI * r) / samples);
  }
  const highlight = (SPECULAR_GAIN * options.present * (RIM_WIDTH / 3) * specContour) / area;

  return rim + highlight;
}

/**
 * The overlay's alpha and its encoded level, read back off the `rgba()` the tier wrote.
 *
 * The declaration is the tier's own final word on the layer — after the size law's occlusion, after
 * the accessibility folds and after the author-tint fold — so parsing it is the only way to
 * condition the solve on the overlay that will actually composite. A malformed or absent
 * declaration returns an opaque overlay, which the solve then declines rather than guessing.
 */
export function w17Overlay(
  backgroundColor: string | undefined,
): { readonly cssAlpha: number; readonly cssTintEncoded: number } {
  const match = backgroundColor?.match(
    /rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:[\s,/]+([\d.]+))?\s*\)/,
  );
  if (match === null || match === undefined) return { cssAlpha: 1, cssTintEncoded: 1 };
  const channel = (index: number): number => Number(match[index]) / 255;
  return {
    cssAlpha: match[4] === undefined ? 1 : Number(match[4]),
    cssTintEncoded: 0.2126 * channel(1) + 0.7152 * channel(2) + 0.0722 * channel(3),
  };
}

/**
 * The intercept and the slope, or `undefined` where the solve has no answer — a fully opaque
 * overlay leaves the filtered backdrop invisible and there is nothing to transfer.
 */
export function w17CarrierSolve(options: {
  /** The group's own sampled backdrop level, linear light. */
  readonly backdropLuminance: number;
  /** The renderer's composite: its adapted alpha and its adapted tint's luminance. */
  readonly rendererAlpha: number;
  readonly rendererTintLuminance: number;
  /** The derived excess, linear light. */
  readonly excess: number;
  /** The overlay this tier already writes: its alpha and its encoded level, 0..1. */
  readonly cssAlpha: number;
  readonly cssTintEncoded: number;
}): W17CarrierTransfer | undefined {
  const { backdropLuminance: b0, rendererAlpha: a, rendererTintLuminance: t } = options;
  const keep = 1 - options.cssAlpha;
  if (keep <= 1e-4) return undefined;

  const composite = (1 - a) * b0 + a * t + options.excess;
  const target = encode(composite);
  const y0 = (target - options.cssTintEncoded * options.cssAlpha) / keep;
  if (y0 <= 0 || y0 >= 1) return undefined;
  const v0 = decode(y0);
  const slope = (encodeSlope(composite) * (1 - a)) / (encodeSlope(v0) * keep);
  const intercept = v0 - slope * b0;
  if (!Number.isFinite(slope) || !Number.isFinite(intercept)) return undefined;
  return { slope, intercept };
}
