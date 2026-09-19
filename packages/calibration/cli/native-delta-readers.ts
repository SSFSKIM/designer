/**
 * The two declared-geometry rim readers the 26.5 waves built, in TypeScript.
 *
 * W23 (claims §5.99–§5.106) read the rim **at the contour, per side, on the
 * straight span**; W24 (§5.107 onward) read it **around the whole boundary,
 * binned by the normal's angle**, which is the reading a per-side reader cannot
 * make because a light on the diagonal projects equally on all four sides. Both
 * instruments live in that wave's evidence directory as Python
 * (`results/2026-09-08-w23-collapsed-rim/g0/read-contour.py`,
 * `results/2026-09-09-w24-lit-edge/g0/read-angular.py`) and both are read off
 * the DECLARED geometry rather than off an extracted silhouette, which is what
 * makes them comparable between two beds of the same scene declaration.
 *
 * They are ported here rather than shelled out to for one reason that decides
 * it: the native delta's noise bar and the delta itself must be the same
 * function of a pair of captures, or the bar does not bound the delta. One
 * process, one metric module, both readings. The port is checked against the
 * committed 26.5 outputs of the Python originals — `verify-readers.ts` beside
 * the results, whose agreement is recorded in the ledger — so a divergence is a
 * measurement rather than a possibility.
 *
 * Everything is in LINEAR light. The rim is a compositing amplitude and only
 * adds in light; `linearLuminance` is the same Rec.709-on-linearised-sRGB
 * transfer the Python `luma_of_rgb` applies.
 */

import {
  CalibrationError,
  linearLuminance,
  type CalibrationImage,
  type CanvasSize,
  type DeclaredComponent,
} from "../src/index";

/** The sides W23 reads, in its own order. */
export const RIM_SIDES = ["top", "bottom", "left", "right"] as const;
export type RimSide = (typeof RIM_SIDES)[number];

/**
 * Sixteen bins of 22.5°, centred on the compass directions; index 0 is straight
 * up (the top side's outward normal) and the index increases clockwise, so 4 is
 * E, 8 is S and 12 is W.
 */
export const COMPASS = [
  "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
] as const;
export const ANGULAR_BINS = COMPASS.length;
const BIN_DEG = 360 / ANGULAR_BINS;

/** W23's and W24's shared window constants, at the values both waves fitted on. */
export const ERODE_CSS_PX = 6;
export const CONTOUR_DEPTH_CSS_PX = 2;
export const CONTOUR_CORNER_FACTOR = 1.6;
export const ANGULAR_OUTSIDE_CSS_PX = 1;
export const ANGULAR_DEPTH_CSS_PX = 4;
export const ANGULAR_STEP_CSS_PX = 0.25;
export const ANGULAR_SPACING_PX = 0.25;
export const ANGULAR_MIN_POINTS = 720;

/**
 * The declared box a single-body component occupies, in device pixels.
 *
 * `null` for a composite with no single box — `toolbar-group` is three capsules
 * with a gap and `glass-over-glass` is a pane on a pane, and neither has one
 * box whose interior is one body. The declared-geometry readers then have
 * nothing to say about that cell and say so, exactly as the Python originals
 * do, rather than inventing a rectangle.
 *
 * The centring is the declaration's own arithmetic and not `placeComponent`'s
 * rounded one, because these two readers' recorded 26.5 numbers were produced
 * by it; every size in the matrix centres to an integer, so the two agree on
 * this bed and the port stays checkable against those numbers.
 */
export interface DeclaredBox {
  readonly x0: number;
  readonly y0: number;
  readonly x1: number;
  readonly y1: number;
  /** Corner radius in device px. A capsule's is half its short side. */
  readonly radiusPx: number;
  readonly kind: string;
}

export function declaredBox(
  component: DeclaredComponent,
  canvas: CanvasSize,
  scale: number,
): DeclaredBox | null {
  if (!("size" in component)) return null;
  const [width, height] = component.size;
  const radius = component.kind === "rrect" ? (component.radius ?? 0) : Math.min(width, height) / 2;
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  return {
    x0: (cx - width / 2) * scale,
    y0: (cy - height / 2) * scale,
    x1: (cx + width / 2) * scale,
    y1: (cy + height / 2) * scale,
    radiusPx: radius * scale,
    kind: component.kind,
  };
}

interface Raster {
  readonly luminance: Float64Array;
  readonly white: Uint8Array;
  readonly width: number;
  readonly height: number;
}

/** Linear luminance plus the all-three-channels-clipped mask, read once per capture. */
export function rasterOf(image: CalibrationImage): Raster {
  const luminance = linearLuminance(image);
  const count = image.width * image.height;
  const white = new Uint8Array(count);
  for (let i = 0; i < count; i += 1) {
    const src = i * 4;
    const clipped =
      (image.data[src] ?? 0) >= 254.5 &&
      (image.data[src + 1] ?? 0) >= 254.5 &&
      (image.data[src + 2] ?? 0) >= 254.5;
    white[i] = clipped ? 1 : 0;
  }
  return { luminance, white, width: image.width, height: image.height };
}

const at = (raster: Raster, x: number, y: number): number =>
  raster.luminance[y * raster.width + x] ?? 0;

/**
 * W21's body, which W23 and W24 both read against: the mean linear luminance
 * over the declared box eroded `ERODE_CSS_PX` on every side. Six px clears the
 * rim band and its blur shoulder.
 */
export function declaredBody(raster: Raster, box: DeclaredBox, scale: number): number {
  const e = ERODE_CSS_PX * scale;
  let sum = 0;
  let count = 0;
  for (let y = 0; y < raster.height; y += 1) {
    const yc = y + 0.5;
    if (yc < box.y0 + e || yc >= box.y1 - e) continue;
    for (let x = 0; x < raster.width; x += 1) {
      const xc = x + 0.5;
      if (xc < box.x0 + e || xc >= box.x1 - e) continue;
      sum += at(raster, x, y);
      count += 1;
    }
  }
  if (count === 0) {
    throw new CalibrationError("empty-region", "declaredBody: the eroded declared box is empty.");
  }
  return sum / count;
}

/** One side's contour reading. `NaN` where the straight span is empty. */
export interface ContourSideRead {
  /** The contour excess over the capture's own body, summed inward and divided by the scale. */
  readonly rim: number;
  /** The first contour row's own excess, undivided. */
  readonly row0: number;
  /** The same sum taken over the side's own neighbouring rows instead of the body. */
  readonly rimLocal: number;
  /** The level those neighbouring rows sit at. */
  readonly base: number;
  /** The fraction of the brightest contour row that is at 255 in all three channels. */
  readonly clip: number;
}

export interface ContourRimRead {
  readonly body: number;
  readonly sides: Readonly<Record<RimSide, ContourSideRead>>;
}

const EMPTY_SIDE: ContourSideRead = { rim: NaN, row0: NaN, rimLocal: NaN, base: NaN, clip: NaN };

/**
 * W23's reader: per side, the rows from the declared box's first pixel inside
 * the shape inward, each one's mean over the side's **straight span** minus the
 * capture's own body, summed over the first `CONTOUR_DEPTH_CSS_PX` and divided
 * by the scale — one linear number per side, in luminance per CSS px, so the 1x
 * and the 2x rows are comparable.
 *
 * The corner arcs are excluded by the declared radius times
 * `CONTOUR_CORNER_FACTOR`, because Apple's rounded rectangle is a continuous
 * corner whose curvature is spread well past the nominal radius (W23 measured
 * the read converging by 1.5 radii). On a capsule the left and right spans are
 * empty at any factor ≥ 1 and are reported as `NaN` rather than as a number
 * read across a semicircle.
 */
export function contourRimRead(raster: Raster, box: DeclaredBox, scale: number): ContourRimRead {
  const body = declaredBody(raster, box, scale);
  const r = box.radiusPx * CONTOUR_CORNER_FACTOR;
  const spanX: readonly [number, number] = [Math.ceil(box.x0 + r), Math.floor(box.x1 - r)];
  const spanY: readonly [number, number] = [Math.ceil(box.y0 + r), Math.floor(box.y1 - r)];
  const rows = Math.round(CONTOUR_DEPTH_CSS_PX * scale);

  const strip = (side: RimSide, k: number): { mean: number; clip: number } => {
    let sum = 0;
    let clipped = 0;
    let count = 0;
    if (side === "top" || side === "bottom") {
      const index = side === "top" ? Math.floor(box.y0) + k : Math.ceil(box.y1) - 1 - k;
      for (let x = spanX[0]; x < spanX[1]; x += 1) {
        sum += at(raster, x, index);
        clipped += raster.white[index * raster.width + x] ?? 0;
        count += 1;
      }
    } else {
      const index = side === "left" ? Math.floor(box.x0) + k : Math.ceil(box.x1) - 1 - k;
      for (let y = spanY[0]; y < spanY[1]; y += 1) {
        sum += at(raster, index, y);
        clipped += raster.white[y * raster.width + index] ?? 0;
        count += 1;
      }
    }
    return { mean: sum / count, clip: clipped / count };
  };

  const sides = {} as Record<RimSide, ContourSideRead>;
  for (const side of RIM_SIDES) {
    const [lo, hi] = side === "top" || side === "bottom" ? spanX : spanY;
    if (hi - lo < 2) {
      sides[side] = EMPTY_SIDE;
      continue;
    }
    const lines: number[] = [];
    const clips: number[] = [];
    for (let k = 0; k < rows; k += 1) {
      const read = strip(side, k);
      lines.push(read.mean);
      clips.push(read.clip);
    }
    let baseSum = 0;
    for (let k = rows; k < 2 * rows; k += 1) baseSum += strip(side, k).mean;
    const base = baseSum / rows;

    let excessSum = 0;
    let localSum = 0;
    let peak = 0;
    for (let i = 0; i < lines.length; i += 1) {
      const value = lines[i] ?? 0;
      excessSum += value - body;
      localSum += value - base;
      if (value > (lines[peak] ?? 0)) peak = i;
    }
    sides[side] = {
      rim: excessSum / scale,
      row0: (lines[0] ?? 0) - body,
      rimLocal: localSum / scale,
      base,
      clip: clips[peak] ?? NaN,
    };
  }
  return { body, sides };
}

interface BoundarySample {
  readonly x: number;
  readonly y: number;
  readonly nx: number;
  readonly ny: number;
}

/**
 * The declared boundary, as points carrying the OUTWARD unit normal, in the
 * clockwise order the eye reads: top, top-right, right, bottom-right, bottom,
 * bottom-left, left, top-left. A capsule's left and right spans are empty by
 * construction, so it reduces to two spans and two semicircles with no special
 * case.
 */
function boundaryPoints(box: DeclaredBox): readonly BoundarySample[] {
  let r = box.radiusPx;
  if (box.kind === "capsule") r = Math.min(box.x1 - box.x0, box.y1 - box.y0) / 2;
  const sx = box.x1 - box.x0 - 2 * r;
  const sy = box.y1 - box.y0 - 2 * r;
  const quarter = (Math.PI / 2) * r;
  const segments: readonly (readonly [string, number])[] = [
    ["top", sx], ["tr", quarter], ["right", sy], ["br", quarter],
    ["bottom", sx], ["bl", quarter], ["left", sy], ["tl", quarter],
  ];
  let perimeter = 0;
  for (const [, length] of segments) perimeter += length;
  const n = Math.max(ANGULAR_MIN_POINTS, Math.ceil(perimeter / ANGULAR_SPACING_PX));
  const centres: Readonly<Record<string, readonly [number, number, number]>> = {
    tr: [box.x1 - r, box.y0 + r, -Math.PI / 2],
    br: [box.x1 - r, box.y1 - r, 0],
    bl: [box.x0 + r, box.y1 - r, Math.PI / 2],
    tl: [box.x0 + r, box.y0 + r, Math.PI],
  };

  const points: BoundarySample[] = [];
  for (let i = 0; i < n; i += 1) {
    const s = ((i + 0.5) / n) * perimeter;
    let acc = 0;
    for (const [name, length] of segments) {
      if (length <= 0) continue;
      if (s < acc + length) {
        const u = s - acc;
        if (name === "top") points.push({ x: box.x0 + r + u, y: box.y0, nx: 0, ny: -1 });
        else if (name === "right") points.push({ x: box.x1, y: box.y0 + r + u, nx: 1, ny: 0 });
        else if (name === "bottom") points.push({ x: box.x1 - r - u, y: box.y1, nx: 0, ny: 1 });
        else if (name === "left") points.push({ x: box.x0, y: box.y1 - r - u, nx: -1, ny: 0 });
        else {
          const centre = centres[name];
          if (centre === undefined) break;
          const a = centre[2] + u / r;
          points.push({
            x: centre[0] + r * Math.cos(a),
            y: centre[1] + r * Math.sin(a),
            nx: Math.cos(a),
            ny: Math.sin(a),
          });
        }
        break;
      }
      acc += length;
    }
  }
  return points;
}

/** The outward normal's compass angle: 0 straight up, increasing clockwise, screen y down. */
function normalAngle(nx: number, ny: number): number {
  return ((Math.atan2(nx, -ny) * 180) / Math.PI + 360) % 360;
}

/**
 * Round half to even, which is what the Python reader's `np.rint` does and what
 * `Math.round` does not. It decides only the measure-zero case of a normal
 * landing exactly on a bin boundary, and it is matched so that the port has no
 * divergence from the original that has to be argued about rather than checked.
 */
function rint(value: number): number {
  const floor = Math.floor(value);
  const fraction = value - floor;
  if (fraction > 0.5) return floor + 1;
  if (fraction < 0.5) return floor;
  return floor % 2 === 0 ? floor : floor + 1;
}

export interface AngularRead {
  readonly body: number;
  /** Mean peak excess over the body, per 22.5° bin. `null` where the bin is empty. */
  readonly bins: readonly (number | null)[];
  /** The band integral beside the peak, in luminance per CSS px, per bin. */
  readonly integral: readonly (number | null)[];
  readonly counts: readonly number[];
  /** Fraction of each bin whose peak ran to the end of the inward window. */
  readonly truncatedFraction: readonly (number | null)[];
  /** Fraction of each bin whose peak pixel is clipped white. */
  readonly clipFraction: readonly (number | null)[];
  /** Fraction of each bin whose peak was found OUTSIDE the declared contour. */
  readonly outsideFraction: readonly (number | null)[];
  readonly brightestBin: number;
  readonly dimmestBin: number;
  readonly brightestAngleDeg: number;
  readonly peakBin: number;
  readonly floorBin: number;
  /** Brightest bin over dimmest. A drawn rim reads near 1; a lit one does not. */
  readonly ratio: number;
  readonly meanPeakDepthCssPx: number;
}

/**
 * W24's reader: at each boundary sample, the MAXIMUM linear luminance along the
 * inward normal from `ANGULAR_OUTSIDE_CSS_PX` outside the declared contour to
 * `ANGULAR_DEPTH_CSS_PX` inside it, minus the capture's own body — a peak and
 * not a sum, because this reader's question is the amplitude the edge reaches
 * in a given direction. The band integral inward from the contour is reported
 * beside it, because a rasterised curve spreads a one-pixel line over two
 * pixels at partial coverage and the integral is conserved under that spreading
 * where the peak is not.
 */
export function angularRead(raster: Raster, box: DeclaredBox, scale: number): AngularRead {
  const body = declaredBody(raster, box, scale);
  const points = boundaryPoints(box);
  const offsets: number[] = [];
  for (
    let t = -ANGULAR_OUTSIDE_CSS_PX;
    t <= ANGULAR_DEPTH_CSS_PX + 1e-9;
    t += ANGULAR_STEP_CSS_PX
  ) {
    offsets.push(t);
  }

  const binSum = new Float64Array(ANGULAR_BINS);
  const binCount = new Float64Array(ANGULAR_BINS);
  const bandSum = new Float64Array(ANGULAR_BINS);
  const truncSum = new Float64Array(ANGULAR_BINS);
  const clipSum = new Float64Array(ANGULAR_BINS);
  const outsideSum = new Float64Array(ANGULAR_BINS);
  let depthSum = 0;
  let depthCount = 0;

  for (const point of points) {
    let best = Number.NEGATIVE_INFINITY;
    let bestAt = NaN;
    let bestClip = 0;
    let total = 0;
    for (const t of offsets) {
      const d = t * scale;
      const xi = Math.floor(point.x - point.nx * d);
      const yi = Math.floor(point.y - point.ny * d);
      if (yi < 0 || yi >= raster.height || xi < 0 || xi >= raster.width) continue;
      const value = at(raster, xi, yi);
      // Ties go to the offset NEAREST the declared contour: consecutive offsets
      // land on the same pixel wherever the step is finer than a device pixel,
      // and a tie broken by scan order would report a peak "outside the contour"
      // that is the very pixel just inside it.
      if (value > best || (value === best && Math.abs(t) < Math.abs(bestAt))) {
        best = value;
        bestAt = t;
        bestClip = raster.white[yi * raster.width + xi] ?? 0;
      }
      if (t >= 0) total += (value - body) * ANGULAR_STEP_CSS_PX;
    }
    if (!Number.isFinite(best)) continue;
    const bin =
      ((rint(normalAngle(point.nx, point.ny) / BIN_DEG) % ANGULAR_BINS) + ANGULAR_BINS) %
      ANGULAR_BINS;
    binSum[bin] = (binSum[bin] ?? 0) + (best - body);
    binCount[bin] = (binCount[bin] ?? 0) + 1;
    bandSum[bin] = (bandSum[bin] ?? 0) + total;
    truncSum[bin] = (truncSum[bin] ?? 0) + (bestAt >= ANGULAR_DEPTH_CSS_PX - 1e-9 ? 1 : 0);
    clipSum[bin] = (clipSum[bin] ?? 0) + bestClip;
    outsideSum[bin] = (outsideSum[bin] ?? 0) + (bestAt < 0 ? 1 : 0);
    depthSum += bestAt;
    depthCount += 1;
  }

  const mean = (sums: Float64Array, index: number): number | null => {
    const count = binCount[index] ?? 0;
    return count === 0 ? null : (sums[index] ?? 0) / count;
  };
  const bins: (number | null)[] = [];
  const integral: (number | null)[] = [];
  const truncated: (number | null)[] = [];
  const clipFraction: (number | null)[] = [];
  const outsideFraction: (number | null)[] = [];
  const counts: number[] = [];
  for (let k = 0; k < ANGULAR_BINS; k += 1) {
    counts.push(binCount[k] ?? 0);
    bins.push(mean(binSum, k));
    integral.push(mean(bandSum, k));
    truncated.push(mean(truncSum, k));
    clipFraction.push(mean(clipSum, k));
    outsideFraction.push(mean(outsideSum, k));
  }

  let brightest = 0;
  let dimmest = 0;
  for (let k = 0; k < ANGULAR_BINS; k += 1) {
    const value = bins[k];
    if (value === null || value === undefined) continue;
    if (bins[brightest] === null || value > (bins[brightest] ?? Number.NEGATIVE_INFINITY)) brightest = k;
    if (bins[dimmest] === null || value < (bins[dimmest] ?? Number.POSITIVE_INFINITY)) dimmest = k;
  }
  const peak = bins[brightest] ?? NaN;
  const floor = bins[dimmest] ?? NaN;

  return {
    body,
    bins,
    integral,
    counts,
    truncatedFraction: truncated,
    clipFraction,
    outsideFraction,
    brightestBin: brightest,
    dimmestBin: dimmest,
    brightestAngleDeg: brightest * BIN_DEG,
    peakBin: peak,
    floorBin: floor,
    ratio: floor > 1e-6 ? peak / floor : Number.POSITIVE_INFINITY,
    meanPeakDepthCssPx: depthCount === 0 ? NaN : depthSum / depthCount,
  };
}

/** Signed angular difference in degrees, wrapped to (-180, 180]. */
export function wrapDegrees(delta: number): number {
  let wrapped = ((delta + 180) % 360) - 180;
  if (wrapped <= -180) wrapped += 360;
  return wrapped;
}
