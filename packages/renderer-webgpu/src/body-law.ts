/**
 * **W42's spatial law, LT, on the CPU** — the declared constants, the per-surface plan the GPU
 * stage will run, the composite's algebra, the tones the law's argument is read through, and the
 * accessibility fold (charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`,
 * Design "The law" and "T"; the hashed declaration's items `law`, `kneeForms`, `accessibility`,
 * `candidate1`, `candidate2`, `candidate2Chroma`; G2's `implementation-design.md` §1–§4 with its
 * rulings §9, and `native-t-addendum.md`, all under
 * `packages/calibration/results/2026-09-30-w42-g2-identification/`).
 *
 * Nothing here draws. These are the references the shader is held to and the numbers the stage
 * is planned with; `test/w42-body-law.test.ts` holds each of them to the instrument's numpy forward
 * model (`instrument/forward.py`) and to the rehearsal's candidate construction
 * (`gate/rehearsal/body.py`) through fixtures generated beside the design note.
 *
 * Units: CSS px are points; device px are CSS px times the device ratio; encoded values are sRGB in
 * [0, 1] and codes are encoded values times 255; d is the SDF depth in points, negative inside.
 */

import type { Rgb } from "./color";
import { linearToSrgbChannel, srgbToLinearChannel } from "./color";
import {
  backdropToneResponse,
  type BodyE3Gains,
  type MaterialPolicyView,
  type MaterialProfile,
  type MaterialVariant,
} from "./material";

/**
 * **The law's declared constants** (declaration `law`; memo D's dump for the radii, the opacity
 * law, the margins and the capture texel; memo C for the floor; Decision Log 5e for the band).
 *
 * They are constants rather than material leaves because the declaration fixes every one and G2
 * fits none; a rival that frees one (a W-shape margin, a free σn) makes it a gated leaf then
 * (`implementation-design.md` Fork 2, ruled). The test pins each to the instrument's source.
 */
export const BODY_LAW_DECLARED = {
  /** BlurRadius 5 and BlurFill radius 8, scaled by k (σ = k·r in the D1 unit). */
  narrowRadius: 5,
  wideRadius: 8,
  /** t = clamp((s − spanKnot) / spanRange, 0, 1): nothing moves for s ≤ 64, saturated at 160. */
  spanKnotPx: 64,
  spanRangePx: 96,
  /** Active opacity: 0.8t at the centre (d = −s/2), 0.4t at 1 pt inside, 0.5 at the contour. */
  activeCentreOpacity: 0.8,
  activeEdgeOpacity: 0.4,
  activeEdgeDepthPt: 1,
  contourOpacity: 0.5,
  /** Receded opacity: 0.4 + 0.4t, flat in depth. */
  recededOpacityBase: 0.4,
  recededOpacitySlope: 0.4,
  /** R_fp's margin: active 0.35 s above s = 64, else 16 pt; receded one device px. */
  activeMarginPerSpan: 0.35,
  activeMarginMinPt: 16,
  recededMarginDevicePx: 1,
  /** The capture: 2 device px per texel, 4 on shapes at least 280 × 160; floor 0.4 texel. */
  captureTexelDevicePx: 2,
  largeCaptureTexelDevicePx: 4,
  largeShapeMinPx: [280, 160] as const,
  floorPerTexel: 0.4,
  /** The active band the law is eased in across, smoothstep(0, 20 pt, depth) (Decision Log 5e). */
  activeBandPt: 20,
} as const;

/**
 * **The realisation's own constants** (`implementation-design.md` §2.4 as revised in §11): six
 * interior levels uniform in σ, a contour level where o = 0.5 lies above them, a cubic in σ through
 * the four nearest, and a box decimation from 12 device px (q = 2) and 48 (q = 4), the oracle's own
 * rule (`forward.py:228`, `246–271`). Not declared by the law; chosen for the shader and bounded
 * against the exact Gaussian by the storage-graph mirror (`implementation-design/u2_mirror.txt`).
 * §2.4's first choice, four levels from 6 device px, put the landed tone 0.295 code from the oracle
 * near black, above the ~0.13-code target (`u2_mirror-l4-q6.txt`).
 */
export const BODY_LAW_REALISATION = {
  activeInteriorLevels: 6,
  decimateFromDevicePx: 12,
  decimateBy4FromDevicePx: 48,
} as const;

/** The encoded Rec. 709 luma the law's knee and its tones read (the weights E3 uses). */
export const BODY_LAW_LUMA: Rgb = [0.2126, 0.7152, 0.0722];

const luma = (c: Rgb): number => c[0] * 0.2126 + c[1] * 0.7152 + c[2] * 0.0722;
const clamp = (x: number, low: number, high: number): number => Math.min(high, Math.max(low, x));

/** t = clamp((s − 64) / 96, 0, 1), the declared size variable. */
export function bodyLawSizeT(spanPx: number): number {
  const d = BODY_LAW_DECLARED;
  return clamp((spanPx - d.spanKnotPx) / d.spanRangePx, 0, 1);
}

/**
 * The declared opacity o(s, d, pose). Active: 0.8t at d = −s/2, falling linearly to 0.4t at
 * d = −1 pt, then to 0.5 at the contour and held there outside, as the rehearsal reads it
 * (`body.py:670`; `forward.py:85` holds 1 beyond the contour, where the band weight is 0).
 * Receded: 0.4 + 0.4t everywhere (`body.py:672`).
 */
export function bodyLawOpacity(depthPt: number, spanPx: number, receded: boolean): number {
  const d = BODY_LAW_DECLARED;
  const t = bodyLawSizeT(spanPx);
  if (receded) return d.recededOpacityBase + d.recededOpacitySlope * t;
  const centre = -spanPx / 2;
  const edge = -d.activeEdgeDepthPt;
  if (depthPt <= centre) return d.activeCentreOpacity * t;
  if (depthPt <= edge) {
    const a = (depthPt - centre) / (edge - centre);
    return d.activeCentreOpacity * t + (d.activeEdgeOpacity * t - d.activeCentreOpacity * t) * a;
  }
  if (depthPt <= 0) {
    const a = (depthPt - edge) / (0 - edge);
    return d.activeEdgeOpacity * t + (d.contourOpacity - d.activeEdgeOpacity * t) * a;
  }
  return d.contourOpacity;
}

/** Device px per capture texel: 4 on a shape at least 280 × 160 CSS px, else 2 (a named gap). */
export function bodyLawCaptureTexelDevicePx(widthPx: number, heightPx: number): number {
  const d = BODY_LAW_DECLARED;
  return widthPx >= d.largeShapeMinPx[0] && heightPx >= d.largeShapeMinPx[1]
    ? d.largeCaptureTexelDevicePx
    : d.captureTexelDevicePx;
}

/** Device px per unit of the law's widths, by D1: 0 device px, 1 CSS px (points), 2 texels. */
export function bodyLawUnitDevicePx(unit: number, devicePixelRatio: number, texelDevicePx: number): number {
  switch (unit) {
    case 0:
      return 1;
    case 1:
      return devicePixelRatio;
    case 2:
      return texelDevicePx;
    default:
      throw new RangeError(`bodyLawWidthUnit ${unit} is not 0, 1 or 2`);
  }
}

/** The box decimation a stored blur of this width takes: 1 (direct), 2 or 4. */
export function bodyLawDecimation(sigmaDevicePx: number): 1 | 2 | 4 {
  const r = BODY_LAW_REALISATION;
  if (sigmaDevicePx < r.decimateFromDevicePx) return 1;
  return sigmaDevicePx < r.decimateBy4FromDevicePx ? 2 : 4;
}

/**
 * The instrument rounds a margin with Python's `round`, which takes a half to the even integer
 * (`forward.py:165`). Mirrored so that a footprint is the oracle's to the pixel.
 */
export function roundHalfEven(x: number): number {
  const floor = Math.floor(x);
  const diff = x - floor;
  if (diff > 0.5) return floor + 1;
  if (diff < 0.5) return floor;
  return floor % 2 === 0 ? floor : floor + 1;
}

/** A device-pixel rectangle, [x0, x1) × [y0, y1). */
export interface BodyLawDeviceRect {
  readonly x0: number;
  readonly y0: number;
  readonly x1: number;
  readonly y1: number;
}

/** One surface as the plan needs it: its box in CSS px on the plane. */
export interface BodyLawSurfaceGeometry {
  readonly centre: readonly [number, number];
  readonly size: readonly [number, number];
}

/** What the stage runs for one surface. */
export interface BodyLawSurfacePlan {
  readonly spanPx: number;
  readonly t: number;
  readonly receded: boolean;
  readonly texelDevicePx: number;
  readonly floorSigmaDevicePx: number;
  readonly unitDevicePx: number;
  readonly marginDevicePx: number;
  /** The device pixels whose centres lie in the shape's box. */
  readonly box: BodyLawDeviceRect;
  /** R_fp: the box grown by the margin and clipped to the source's extent. */
  readonly footprint: BodyLawDeviceRect;
  readonly edge: "clamp" | "normalised";
  readonly wideSigmaDevicePx: number;
  /**
   * The narrow term's stored widths, ascending: one when receded; the interior levels plus the
   * contour level when active and t > 0; 0 and the contour level when active and t = 0.
   */
  readonly narrowSigmaDevicePx: readonly number[];
  /** How a pixel's width is read between the levels (§2.4). */
  readonly interpolation: "single" | "linear" | "cubic";
  readonly bandPt: number;
}

/**
 * **The per-surface plan** — `forward.py`'s `Cell` for one surface (`forward.py:120–171`,
 * `maps` at `346–393`) with the canvas replaced by the source's extent on the plane.
 */
export function bodyLawSurfacePlan(
  surface: BodyLawSurfaceGeometry,
  devicePixelRatio: number,
  material: Pick<MaterialProfile, "bodyLawK" | "bodyLawPose" | "bodyLawEdgeSwap" | "bodyLawWidthUnit">,
  sourceExtent?: BodyLawDeviceRect,
): BodyLawSurfacePlan {
  const d = BODY_LAW_DECLARED;
  const [w, h] = surface.size;
  const spanPx = Math.min(w, h);
  const t = bodyLawSizeT(spanPx);
  const receded = material.bodyLawPose === 1;
  const texelDevicePx = bodyLawCaptureTexelDevicePx(w, h);
  const unitDevicePx = bodyLawUnitDevicePx(material.bodyLawWidthUnit, devicePixelRatio, texelDevicePx);
  const [kn, kw] = material.bodyLawK;

  const edgeOf = (low: number, high: number) => ({
    start: Math.ceil(low * devicePixelRatio - 0.5),
    end: Math.floor(high * devicePixelRatio - 0.5) + 1,
  });
  const xs = edgeOf(surface.centre[0] - w / 2, surface.centre[0] + w / 2);
  const ys = edgeOf(surface.centre[1] - h / 2, surface.centre[1] + h / 2);
  const box = { x0: xs.start, y0: ys.start, x1: xs.end, y1: ys.end };

  const marginPt = receded
    ? d.recededMarginDevicePx / devicePixelRatio
    : spanPx > d.spanKnotPx ? d.activeMarginPerSpan * spanPx : d.activeMarginMinPt;
  const marginDevicePx = roundHalfEven(marginPt * devicePixelRatio);
  const grown = {
    x0: box.x0 - marginDevicePx, y0: box.y0 - marginDevicePx,
    x1: box.x1 + marginDevicePx, y1: box.y1 + marginDevicePx,
  };
  const footprint = sourceExtent === undefined ? grown : {
    x0: Math.max(grown.x0, sourceExtent.x0), y0: Math.max(grown.y0, sourceExtent.y0),
    x1: Math.min(grown.x1, sourceExtent.x1), y1: Math.min(grown.y1, sourceExtent.y1),
  };

  const clampMode = !receded !== (material.bodyLawEdgeSwap === 1);
  const scale = kn * d.narrowRadius * unitDevicePx;
  let narrow: number[];
  let interpolation: BodyLawSurfacePlan["interpolation"];
  if (receded) {
    narrow = [scale * (d.recededOpacityBase + d.recededOpacitySlope * t)];
    interpolation = "single";
  } else if (t === 0) {
    narrow = [0, scale * d.contourOpacity];
    interpolation = "linear";
  } else {
    const n = BODY_LAW_REALISATION.activeInteriorLevels;
    const low = scale * d.activeEdgeOpacity * t;
    const high = scale * d.activeCentreOpacity * t;
    narrow = Array.from({ length: n }, (_, i) => low + ((high - low) * i) / (n - 1));
    const contour = scale * d.contourOpacity;
    if (contour > high + 1e-9) narrow.push(contour);
    interpolation = "cubic";
  }

  return {
    spanPx, t, receded, texelDevicePx,
    floorSigmaDevicePx: d.floorPerTexel * texelDevicePx,
    unitDevicePx, marginDevicePx, box, footprint,
    edge: clampMode ? "clamp" : "normalised",
    wideSigmaDevicePx: kw * d.wideRadius * unitDevicePx,
    narrowSigmaDevicePx: narrow,
    interpolation,
    bandPt: receded ? 0 : d.activeBandPt,
  };
}

/** The narrow term's exact width at one depth, device px: k_n·5·o(s, d, pose)·u. */
export function bodyLawNarrowSigmaDevicePx(
  depthPt: number,
  plan: BodyLawSurfacePlan,
  material: Pick<MaterialProfile, "bodyLawK">,
): number {
  return material.bodyLawK[0] * BODY_LAW_DECLARED.narrowRadius *
    bodyLawOpacity(depthPt, plan.spanPx, plan.receded) * plan.unitDevicePx;
}

/**
 * **One pixel's narrow term from the stored levels** — linear between two, or the cubic in σ
 * through the four nearest (Lagrange; `narrow_interp.py`'s `lagrange`), clamped to [0, 1].
 * `values[i]` is level i's value at the pixel.
 */
export function bodyLawInterpolateLevels(
  sigma: number,
  levels: readonly number[],
  values: readonly number[],
  interpolation: BodyLawSurfacePlan["interpolation"],
): number {
  const n = levels.length;
  if (interpolation === "single" || n === 1) return values[0]!;
  const s = clamp(sigma, levels[0]!, levels[n - 1]!);
  let upper = 0;
  while (upper < n && levels[upper]! < s) upper++;
  if (interpolation === "linear" || n < 4) {
    const i = clamp(upper - 1, 0, n - 2);
    const a = levels[i]!, b = levels[i + 1]!;
    const w = (s - a) / (b - a);
    return clamp(values[i]! + w * (values[i + 1]! - values[i]!), 0, 1);
  }
  const start = clamp(upper - 2, 0, n - 4);
  let out = 0;
  for (let j = 0; j < 4; j++) {
    let wj = 1;
    const xj = levels[start + j]!;
    for (let m = 0; m < 4; m++) {
      if (m !== j) wj *= (s - levels[start + m]!) / (xj - levels[start + m]!);
    }
    out += wj * values[start + j]!;
  }
  return clamp(out, 0, 1);
}

/** The law's argument at one pixel and the wide term's luma E3's gain reads. */
export interface BodyLawArgument {
  /** A = M (encoded, [0, 1]): the argument every tone reads. */
  readonly argument: Rgb;
  /** L(W), encoded, the E3 gain's argument (candidate 1, light receded). */
  readonly wideLuma: number;
}

/**
 * **The composite: the knee and M** (`forward.py`'s `_hinge` and `compose`,
 * `forward.py:497–527`; the rehearsal's chroma-from-W form, `body.py:707–713`).
 *
 * C and W are in the law's averaging space: encoded when D2 is 1, linear light when D2 is 0, in
 * which case M is encoded at the end (the rejected F2, expressible and never landed).
 */
export function bodyLawComposite(
  narrow: Rgb,
  wide: Rgb,
  material: Pick<MaterialProfile, "bodyLawLambda" | "bodyLawNormal" | "bodyLawHinge" |
    "bodyLawKnee" | "bodyLawEncodedAveraging">,
): BodyLawArgument {
  const h = material.bodyLawHinge;
  const lam = material.bodyLawLambda;
  const w = material.bodyLawNormal;
  const C = narrow, W = wide;
  let M: Rgb;
  switch (material.bodyLawKnee) {
    case 0: {
      const N = [0, 1, 2].map((i) => C[i]! + h * lam * Math.max(0, h * (W[i]! - C[i]!)));
      M = [0, 1, 2].map((i) => (1 - w) * N[i]! + w * W[i]!) as unknown as Rgb;
      break;
    }
    case 1: {
      const on = h * (luma(W) - luma(C)) > 0 ? 1 : 0;
      const N = [0, 1, 2].map((i) => C[i]! + lam * on * (W[i]! - C[i]!));
      M = [0, 1, 2].map((i) => (1 - w) * N[i]! + w * W[i]!) as unknown as Rgb;
      break;
    }
    case 2: {
      const CL = luma(C), WL = luma(W);
      const NL = CL + h * lam * Math.max(0, h * (WL - CL));
      const ML = (1 - w) * NL + w * WL;
      M = [0, 1, 2].map((i) => ML + (W[i]! - WL)) as unknown as Rgb;
      break;
    }
    default:
      throw new RangeError(`bodyLawKnee ${material.bodyLawKnee} is not 0, 1 or 2`);
  }
  if (material.bodyLawEncodedAveraging === 1) return { argument: M, wideLuma: luma(W) };
  const enc = (v: number): number => linearToSrgbChannel(clamp(v, 0, 1));
  return {
    argument: [enc(M[0]), enc(M[1]), enc(M[2])],
    wideLuma: luma([enc(W[0]), enc(W[1]), enc(W[2])]),
  };
}

/**
 * **The accessibility fold for every W42 gate** (declaration `accessibility`; §4; Fork 4 and
 * Fork 6, ruled). An exhaustive switch on the occlusion axis, on the model of
 * `bodyChromaRetentionUnderPolicy`: nominal keeps the strength where the group samples a texture
 * and the variant is `regular`; an occlusion lift (Reduce Transparency, `increased`) or forced
 * colours (`opaque`) return the identity. Increase Contrast alone moves no occlusion and keeps the
 * law. The F extension and candidate 2's table are read only under the law, and E3 under the law
 * reads `bodyLawE3StrengthUnderLaw`, so this one fold governs them all.
 */
export function bodyLawStrengthUnderPolicy(
  strength: number,
  policy: MaterialPolicyView,
  variant: MaterialVariant,
  sampled: boolean,
): number {
  switch (policy.occlusion) {
    case "nominal":
      return sampled && variant === "regular" ? strength : 0;
    case "increased":
    case "opaque":
      return 0;
  }
}

/**
 * E3's strength on the LAW's path: the document's, wherever the law's folded strength is above 0
 * (Fork 6, ruled). E3's own fold (`bodyE3StrengthUnderPolicy`) keeps governing the W41 path, where
 * it stands down under Increase Contrast alone; under the law that would draw the light-receded
 * fallback the parent struck.
 */
export function bodyLawE3StrengthUnderLaw(e3Strength: number, foldedLawStrength: number): number {
  return foldedLawStrength > 0 ? e3Strength : 0;
}

/** E3's gain g(L) over the knots 63, 93 and 118, held outside (`material.ts` `bodyE3Encoded`). */
export function bodyLawE3Gain(level: number, gains: BodyE3Gains): number {
  return level > 93
    ? gains[1] + Math.min(1, Math.max(0, (level - 93) / 25)) * (gains[2] - gains[1])
    : gains[0] + Math.min(1, Math.max(0, (level - 63) / 30)) * (gains[1] - gains[0]);
}

/**
 * **E3 with the law's argument and the F extension** (candidate 1, light receded; §2.8). F is
 * `bodyE3Encoded`'s, continued past its knots and clipped, and above encoded 150 it moves by
 * `bodyE3HighStrength` toward the table through (150, n₆), (160, h₀) … (255, h₆). g is read at
 * `gainLevel` (L(W) under the law) and scales the argument's own chroma A − L(A); an achromatic
 * argument has zero chroma exactly. At strength 0 and `gainLevel` = L(A) this is `bodyE3Encoded`.
 */
export function bodyLawE3Codes(
  argumentCodes: Rgb,
  gainLevel: number,
  material: Pick<MaterialProfile, "bodyE3Gains" | "bodyE3Neutral" | "bodyE3HighStrength" |
    "bodyE3NeutralHigh">,
): Rgb {
  const [r, g, b] = argumentCodes;
  const level = luma(argumentCodes);
  const knots = [40, 56, 72, 88, 104, 128, 150] as const;
  const neutral = material.bodyE3Neutral;
  let i = 0;
  for (let j = 1; j < 6; j++) if (level >= knots[j]!) i = j;
  const tt = (level - knots[i]!) / (knots[i + 1]! - knots[i]!);
  let f = Math.min(255, Math.max(0, neutral[i]! + tt * (neutral[i + 1]! - neutral[i]!)));
  const strength = material.bodyE3HighStrength;
  if (strength > 0 && level > 150) {
    const xs = [150, 160, 176, 192, 208, 224, 240, 255];
    const ys = [neutral[6], ...material.bodyE3NeutralHigh];
    let k = 0;
    while (k < xs.length - 2 && level > xs[k + 1]!) k++;
    const u = Math.min(1, (level - xs[k]!) / (xs[k + 1]! - xs[k]!));
    const table = ys[k]! + u * (ys[k + 1]! - ys[k]!);
    f = f + strength * (table - f);
  }
  if (r === g && g === b) return [f, f, f];
  const gain = bodyLawE3Gain(gainLevel, material.bodyE3Gains);
  const channel = (value: number): number => Math.min(255, Math.max(0, f + gain * (value - level)));
  return [channel(r), channel(g), channel(b)];
}

/** One table row read at a level: piecewise linear over the levels, held at the ends. */
function rowAt(level: number, levels: readonly number[], row: readonly number[]): number {
  const n = levels.length;
  if (level <= levels[0]!) return row[0]!;
  if (level >= levels[n - 1]!) return row[n - 1]!;
  let k = 0;
  while (level > levels[k + 1]!) k++;
  const u = (level - levels[k]!) / (levels[k + 1]! - levels[k]!);
  return row[k]! + u * (row[k + 1]! - row[k]!);
}

/**
 * **Candidate 2's tone** (§2.9; `native-t-addendum.md` §2 items 5–6): T at the argument's
 * encoded luma, linear in level within each span row and linear in span between the two rows
 * that bracket the surface's span (the first and last rows outside), then
 * y = clamp(T + scale·g(L)·(A − L), 0, 255) in E3's clipping order.
 */
export function bodyToneTableCodesAt(
  argumentCodes: Rgb,
  spanPx: number,
  material: Pick<MaterialProfile, "bodyToneTableLevels" | "bodyToneTableSpans" |
    "bodyToneTableCodes" | "bodyToneChromaGains" | "bodyToneChromaScale">,
): Rgb {
  const [r, g, b] = argumentCodes;
  const level = luma(argumentCodes);
  const spans = material.bodyToneTableSpans;
  const levels = material.bodyToneTableLevels;
  const rows = material.bodyToneTableCodes;
  let f: number;
  if (spanPx <= spans[0]) f = rowAt(level, levels, rows[0]);
  else if (spanPx >= spans[4]) f = rowAt(level, levels, rows[4]);
  else {
    let k = 0;
    while (spanPx > spans[k + 1]!) k++;
    const u = (spanPx - spans[k]!) / (spans[k + 1]! - spans[k]!);
    const lo = rowAt(level, levels, rows[k]!), hi = rowAt(level, levels, rows[k + 1]!);
    f = lo + u * (hi - lo);
  }
  f = Math.min(255, Math.max(0, f));
  if (r === g && g === b) return [f, f, f];
  const gain = material.bodyToneChromaScale * bodyLawE3Gain(level, material.bodyToneChromaGains);
  const channel = (value: number): number => Math.min(255, Math.max(0, f + gain * (value - level)));
  return [channel(r), channel(g), channel(b)];
}

/**
 * What the per-pixel landed tone reads that is not the pixel's own colour: the group's and the
 * pixel's values exactly as the optics pass holds them (`wgsl/optics.ts:868–874`, `959`, `1135`,
 * `1187`; the tone strength without the "no measured tone" gate, §2.8).
 */
export interface LandedToneInputs {
  /** The folded thickness factor at the pixel's span, `sizeK`. */
  readonly sizeK: number;
  /** W25's level term at the pixel, `toneLevelFar`. */
  readonly toneLevelFar: number;
  /** The group's neutral, mix(tint, adapted tint, adaptation strength), linear. */
  readonly neutral: Rgb;
  /** The policy-folded tint alpha and the size law's occlusion gain. */
  readonly tintAlpha: number;
  readonly sizeOcclusionGain: number;
  /** backdropToneUnderPolicy × backdropToneMax: the law's argument is always a measured tone. */
  readonly toneStrength: number;
  readonly toneLow: number;
  readonly toneHigh: number;
  /** The size bias already divided by the accessibility cap, as the uniform carries it. */
  readonly toneSizeBias: number;
  /** The policy-folded body chroma retention. */
  readonly retention: number;
  /** The abscissa kind: the silhouette reads dec(L_enc(A)), the source L_lin(dec A). */
  readonly abscissa: "source" | "silhouette";
  /** The surface's presence. */
  readonly presence: number;
}

/**
 * **Candidate 1's landed T at one pixel** (§2.8): the shipped solve's uniform response evaluated
 * at the law's argument, as the rehearsal's `landed_T` does (`body.py:504–537`). Each pixel is
 * toned as the shipped material tones a uniform backdrop of colour dec(A): the solve at
 * `wgsl/optics.ts:1165–1262`, the collapse target and adapted colour at `1292–1303`, the composite
 * at `1318–1319` and the retention at `1369`, transcribed in their order with the tone colour, the
 * linear mean and the composited backdrop all dec(A). Returns linear light.
 */
export function landedToneLinear(
  argumentEncoded: Rgb,
  inputs: LandedToneInputs,
  profile: Pick<MaterialProfile, "backdropToneAnchorX" | "backdropToneResponseThin" |
    "backdropToneResponseThick" | "backdropToneResponseStrength" | "backdropToneBlackStrength" |
    "backdropToneBlackThin" | "backdropToneBlackThick">,
): Rgb {
  const c: Rgb = [
    srgbToLinearChannel(clamp(argumentEncoded[0], 0, 1)),
    srgbToLinearChannel(clamp(argumentEncoded[1], 0, 1)),
    srgbToLinearChannel(clamp(argumentEncoded[2], 0, 1)),
  ];
  const lin = luma(c);
  const level = inputs.abscissa === "silhouette"
    ? srgbToLinearChannel(clamp(luma(argumentEncoded), 0, 1))
    : lin;
  const sizeK = inputs.sizeK;
  const toneStrength = inputs.toneStrength;

  let toneAdapt = 0;
  if (toneStrength > 0) {
    const toneX = level + inputs.toneSizeBias * sizeK;
    const toneT = clamp((toneX - inputs.toneLow) / Math.max(inputs.toneHigh - inputs.toneLow, 1e-6), 0, 1);
    toneAdapt = clamp(toneStrength, 0, 1) * (1 - toneT * toneT * (3 - 2 * toneT));
  }
  const sizedAlpha = inputs.tintAlpha + inputs.sizeOcclusionGain * sizeK * (1 - inputs.tintAlpha);
  const neutral = inputs.neutral;
  let solvedNeutral: Rgb = neutral;
  let solvedAlpha = sizedAlpha;
  const rs = clamp(profile.backdropToneResponseStrength, 0, 1);
  if (toneStrength > 0 && profile.backdropToneResponseStrength > 0 && sizedAlpha > 1e-3 &&
      toneAdapt < 0.995) {
    const encodedInput = linearToSrgbChannel(clamp(level, 0, 1));
    const anchor = Math.max(profile.backdropToneAnchorX[0], 1e-4);
    const ss = (e0: number, e1: number, x: number): number => {
      const u = clamp((x - e0) / (e1 - e0), 0, 1);
      return u * u * (3 - 2 * u);
    };
    let authority = ss(anchor * 0.5, anchor, encodedInput) * rs;
    if (profile.backdropToneBlackStrength > 0 && encodedInput < 0.003) {
      // W36's authority blend; the response's own black blend is inside backdropToneResponse.
      const blackWeight =
        clamp(profile.backdropToneBlackStrength, 0, 1) * (1 - ss(0, 0.003, encodedInput));
      authority = authority + (rs - authority) * blackWeight;
    }
    if (authority > 0) {
      // `backdropToneResponse` carries the same black blend the shader applies after
      // `tone_response`, and is pinned to that shader by tier-coherence.test.ts.
      const response = backdropToneResponse(encodedInput, sizeK, profile as MaterialProfile,
        inputs.toneLevelFar);
      const preCollapse = (response - toneAdapt * lin) / (1 - toneAdapt);
      const neutralLuma = luma(neutral);
      const nominal = (1 - sizedAlpha) * lin + sizedAlpha * neutralLuma;
      const shift = ((preCollapse - nominal) / sizedAlpha) * authority * toneStrength;
      solvedNeutral = [
        clamp(neutral[0] + shift, 0, 1), clamp(neutral[1] + shift, 0, 1), clamp(neutral[2] + shift, 0, 1),
      ];
      const solvedLuma = luma(solvedNeutral);
      const achieved = (1 - sizedAlpha) * lin + sizedAlpha * solvedLuma;
      if (preCollapse > achieved + 1e-4 && solvedLuma > lin + 1e-3) {
        const alphaTarget = clamp((preCollapse - lin) / (solvedLuma - lin), sizedAlpha, 1);
        solvedAlpha = sizedAlpha + (alphaTarget - sizedAlpha) * authority * toneStrength;
      }
    }
  }
  // The collapse's target is mix(toneColour, backdrop, collapseTransmission), and both are
  // dec(A) here, so the transmission cannot move it: inert by construction (§3).
  const toneTarget = c;
  const adaptedAlpha = solvedAlpha + toneAdapt * (1 - solvedAlpha);
  let adapted: Rgb = solvedNeutral;
  if (toneAdapt > 0 && adaptedAlpha > 0) {
    adapted = [0, 1, 2].map((i) =>
      (solvedNeutral[i]! * ((1 - toneAdapt) * solvedAlpha) + toneTarget[i]! * toneAdapt) / adaptedAlpha,
    ) as unknown as Rgb;
  }
  const presentAlpha = adaptedAlpha * inputs.presence;
  const colour: Rgb = [0, 1, 2].map((i) => c[i]! + (adapted[i]! - c[i]!) * presentAlpha) as unknown as Rgb;
  return bodyLawChromaRetention(colour, c, inputs.retention);
}

/**
 * `body_chroma_retention` (`wgsl/optics.ts:711–724`) with `gamut_at_luma` (`701–709`), term for
 * term, for the landed tone's pixel. The shipped path's own CPU reference is the shader, pinned
 * by `w31-body-chroma.test.ts`; this copy exists so the per-pixel tone has one.
 */
export function bodyLawChromaRetention(colour: Rgb, backdrop: Rgb, retention: number): Rgb {
  if (retention <= 0) return colour;
  const Y = luma(colour);
  if (!(Y > 1e-6 && Y <= 1)) return colour;
  const Yb = luma(backdrop);
  if (Yb <= 1e-6) return colour;
  const r = clamp(retention, 0, 1);
  const toward = [0, 1, 2].map((i) => backdrop[i]! * (Y / Yb));
  let restored = [0, 1, 2].map((i) => colour[i]! + (toward[i]! - colour[i]!) * r);
  const Yr = luma(restored as unknown as Rgb);
  if (Yr > 1e-6) restored = restored.map((v) => v * (Y / Yr));
  let t = 1;
  for (let i = 0; i < 3; i++) {
    const d = restored[i]! - Y;
    if (d > 1e-7) t = Math.min(t, (1 - Y) / d);
    else if (d < -1e-7) t = Math.min(t, -Y / d);
  }
  const k = clamp(t, 0, 1);
  return [0, 1, 2].map((i) => Y + (restored[i]! - Y) * k) as unknown as Rgb;
}
