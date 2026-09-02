/**
 * Silhouettes: extracting them, and the two geometric operators every
 * silhouette metric is built from — an exact Euclidean distance transform and a
 * contour trace.
 *
 * ## Why extraction is configurable
 *
 * The shape axis needs a binary "where is the surface" mask, and the two sides
 * of the comparison hand it over differently. A web capture can be taken over a
 * transparent page, where alpha *is* the silhouette. A native capture cannot:
 * a screen capture is an opaque composite, so the silhouette has to be
 * recovered by differencing against the background raster the harness composited
 * it over — which the methodology guarantees exists, because native and web
 * renders are required to share identical pre-rendered raster backgrounds.
 * Hence two extractors over one mask type, rather than one extractor with a
 * hidden assumption.
 *
 * Both extractors take an optional **search region** (schema 5). The
 * luminance-delta rule's premise — anything differing from the background is the
 * surface — is false for a material that casts a shadow, and the region is what
 * bounds it back to the geometry the scene declares. See `component-region.ts`.
 *
 * ## Why the distance transform is exact
 *
 * Contour distance is the shape axis's headline number, so an approximate
 * transform (chamfer, 3-4 masks, city-block) would put an error floor of a few
 * percent under every reported figure and that floor would vary with contour
 * orientation. The Felzenszwalb–Huttenlocher lower-envelope algorithm is exact
 * for squared Euclidean distance between pixel centres and runs in O(n) per
 * dimension, so there is no reason to accept an approximation.
 *
 * The residual floor is the raster grid itself: distances are between pixel
 * *centres*, so a contour that truly sits half a pixel off reads as either 0 or
 * 1. Sub-pixel contour localisation is not attempted, and any figure below
 * ~0.5px should be read as "within the grid", not as a measurement.
 */

import { srgbByteToLinear, linearRgbLuminance, srgbByteToOklab } from "./color";
import { CalibrationError } from "./errors";
import { assertComparable, type CalibrationImage } from "./image";

/** A binary mask over an image-sized grid. `mask[i]` is 1 inside, 0 outside. */
export interface Silhouette {
  readonly width: number;
  readonly height: number;
  readonly mask: Uint8Array;
}

/**
 * Where the extractor is allowed to look.
 *
 * Both rules below answer "is this pixel the surface?" from the pixel alone, and
 * for the luminance-delta rule that answer became wrong when the reference
 * gained an outer shadow: shadowed backdrop differs from the backdrop, so the
 * rule returned the component *and its shadow* as one body (claims §5.11). A
 * search region is the ruled fix (wave Decision Log 15) — the scene's own
 * declared geometry, supplied by `componentRegion`, never anything derived from
 * the image being measured.
 *
 * A pixel outside the region is outside the silhouette whatever it contains.
 * That is the whole mechanism, and it is why area recovery becomes partly
 * assumed: see `component-region.ts` for what the axis no longer claims.
 */
interface RegionBounded {
  /** Absent means the whole canvas — the pre-schema-5 rule, unchanged. */
  readonly region?: Silhouette;
}

/** Alpha above a threshold is inside. For captures taken over transparency. */
export interface AlphaThresholdExtractor extends RegionBounded {
  readonly kind: "alpha";
  /** Normalised 0..1; 0.5 is the natural choice for an antialiased edge. */
  readonly threshold: number;
}

/**
 * Anything that differs from the known background by more than a threshold —
 * **and lies inside the search region** — is inside. For opaque native
 * composites over a shared raster background.
 */
export interface LuminanceDeltaExtractor extends RegionBounded {
  readonly kind: "luminance-delta";
  readonly background: CalibrationImage;
  /** Absolute linear-light luminance difference, 0..1. */
  readonly threshold: number;
  /**
   * The chroma arm (W11b, claims §5.40): a pixel whose OKLab a/b differs from
   * the background's by at least this is inside too, whatever its luminance.
   *
   * The luminance arm alone cuts a hole wherever a coloured surface meets its
   * own level in the backdrop — an opaque orange over the photo's orange region
   * — and it does so on the REFERENCE as much as on the web side. The arm is on
   * the a/b plane only, so it is orthogonal to the luminance rule and exactly
   * inert on neutral captures over neutral plates, whose a/b are zero on both
   * sides; the rule with it is a strict superset of the rule without it. Absent
   * means the pre-W11b rule, byte for byte.
   *
   * Not OKLab ΔE, deliberately: replacing the luminance arm with OKLab lightness
   * was measured to lose the light-solid reference almost entirely (dL/dY falls
   * with level, so a 0.02 luminance step near white is a 0.007 lightness step)
   * and to admit one code value of near-black noise.
   */
  readonly chromaThreshold?: number;
}

export type SilhouetteExtractor = AlphaThresholdExtractor | LuminanceDeltaExtractor;

/** Extract a silhouette under the given rule. */
export function extractSilhouette(image: CalibrationImage, extractor: SilhouetteExtractor): Silhouette {
  const count = image.width * image.height;
  const mask = new Uint8Array(count);
  const region = extractor.region;
  if (region !== undefined && (region.width !== image.width || region.height !== image.height)) {
    throw new CalibrationError(
      "dimension-mismatch",
      `extractSilhouette: a ${region.width}x${region.height} search region cannot bound a ` +
        `${image.width}x${image.height} capture.`,
    );
  }

  if (extractor.kind === "alpha") {
    const cutoff = extractor.threshold * 255;
    for (let i = 0; i < count; i += 1) {
      if (region !== undefined && (region.mask[i] ?? 0) === 0) continue;
      mask[i] = (image.data[i * 4 + 3] ?? 0) >= cutoff ? 1 : 0;
    }
    return { width: image.width, height: image.height, mask };
  }

  assertComparable(image, extractor.background, "extractSilhouette(luminance-delta)");
  const background = extractor.background;
  const chroma = extractor.chromaThreshold;
  for (let i = 0; i < count; i += 1) {
    if (region !== undefined && (region.mask[i] ?? 0) === 0) continue;
    const src = i * 4;
    const r = image.data[src] ?? 0;
    const g = image.data[src + 1] ?? 0;
    const b = image.data[src + 2] ?? 0;
    const br = background.data[src] ?? 0;
    const bg = background.data[src + 1] ?? 0;
    const bb = background.data[src + 2] ?? 0;
    const own = linearRgbLuminance(srgbByteToLinear(r), srgbByteToLinear(g), srgbByteToLinear(b));
    const base = linearRgbLuminance(srgbByteToLinear(br), srgbByteToLinear(bg), srgbByteToLinear(bb));
    if (Math.abs(own - base) >= extractor.threshold) {
      mask[i] = 1;
      continue;
    }
    // The chroma arm, asked only where the luminance arm said no. A neutral
    // pixel over a neutral plate is a no-op here: both a/b are exactly zero.
    if (chroma !== undefined && !(r === g && g === b && br === bg && bg === bb)) {
      const p = srgbByteToOklab(r, g, b);
      const q = srgbByteToOklab(br, bg, bb);
      const da = p.a - q.a;
      const db = p.b - q.b;
      if (Math.sqrt(da * da + db * db) >= chroma) mask[i] = 1;
    }
  }
  return { width: image.width, height: image.height, mask };
}

/**
 * The same silhouette with its interior holes filled — the region enclosed by
 * the mask's OUTER contour, which is what a contour comparison means to compare.
 *
 * "Outside" is the image border rather than any search region's border: a
 * bounded mask is surrounded by zeros that reach the border, so they are
 * correctly left alone, and anything the flood cannot reach is enclosed by the
 * mask. That is exactly a hole, with no extra argument needed to say so.
 *
 * 4-connected on the background, the conservative pairing against the mask's
 * 8-connected boundary tracing: a diagonal seam of excluded pixels stays
 * unfilled rather than being closed over, so this fills no more than it must.
 */
export function fillSilhouetteHoles(silhouette: Silhouette): Silhouette {
  const { width, height, mask } = silhouette;
  const outside = new Uint8Array(width * height);
  const stack: number[] = [];

  const push = (index: number): void => {
    if (outside[index] === 1 || (mask[index] ?? 0) !== 0) return;
    outside[index] = 1;
    stack.push(index);
  };
  for (let x = 0; x < width; x += 1) {
    push(x);
    push((height - 1) * width + x);
  }
  for (let y = 0; y < height; y += 1) {
    push(y * width);
    push(y * width + width - 1);
  }
  while (stack.length > 0) {
    const index = stack.pop() as number;
    const x = index % width;
    const y = (index - x) / width;
    if (x > 0) push(index - 1);
    if (x < width - 1) push(index + 1);
    if (y > 0) push(index - width);
    if (y < height - 1) push(index + width);
  }

  const filled = new Uint8Array(width * height);
  for (let i = 0; i < filled.length; i += 1) {
    filled[i] = (mask[i] ?? 0) !== 0 || outside[i] === 0 ? 1 : 0;
  }
  return { width, height, mask: filled };
}

/**
 * How many connected bodies a silhouette has, counting a hole-filled mask with
 * 8-connectivity — the same connectivity the contour tracer walks.
 *
 * The number the contour axis needs beside its distances. The metric compares
 * outlines; a mask the extractor has broken into pieces has more outlines than
 * the surface does, and the extra ones sit wherever the material's level
 * happened to coincide with the backdrop's rather than where a boundary is.
 * Measured on `photo__rrect-md__rest-tint-orange` at 2x: the reference is one
 * body and the CSS tier is four, and the largest fragment sits INSIDE a ring
 * punched through the surface's lower-right quadrant.
 *
 * Compared against the declared region's own count rather than against 1, so a
 * genuinely multi-body component passes: `toolbar-group` declares three capsules
 * and its region has three components, so three is correct there and two would
 * be a real loss. That is what makes this a conditioning statement with no
 * threshold in it — the count to beat is declared, not chosen.
 */
export function silhouetteBodyCount(silhouette: Silhouette): number {
  const filled = fillSilhouetteHoles(silhouette);
  const { width, height, mask } = filled;
  const seen = new Uint8Array(width * height);
  const stack: number[] = [];
  let bodies = 0;

  for (let start = 0; start < seen.length; start += 1) {
    if (seen[start] === 1 || (mask[start] ?? 0) === 0) continue;
    bodies += 1;
    seen[start] = 1;
    stack.push(start);
    while (stack.length > 0) {
      const index = stack.pop() as number;
      const x = index % width;
      const y = (index - x) / width;
      for (let dy = -1; dy <= 1; dy += 1) {
        for (let dx = -1; dx <= 1; dx += 1) {
          if (dx === 0 && dy === 0) continue;
          const nx = x + dx;
          const ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= width || ny >= height) continue;
          const neighbour = ny * width + nx;
          if (seen[neighbour] === 1 || (mask[neighbour] ?? 0) === 0) continue;
          seen[neighbour] = 1;
          stack.push(neighbour);
        }
      }
    }
  }
  return bodies;
}

/**
 * How many interior holes a silhouette has inside its search region.
 *
 * Kept, and no longer gated on. This is the measurement that motivated the
 * outer-contour metric (wave Decision Log 17): a topology ARM on the
 * conditioning predicate was built, measured to cost 77 cells and to leave the
 * increased-contrast contour rows gating nothing, and replaced by making the
 * metric itself immune. The counts stay on every cell because they are how a
 * reader tells an extractor that punched holes from one that merely missed area.
 *
 * A hole is a 4-connected run of region pixels the mask excludes that never
 * reaches the region's border. Counted rather than measured by area on purpose:
 * the quantity a contour metric is hostage to is the NUMBER of extra boundaries
 * it has to trace, not how much they enclose — 72 one-pixel holes cost the trace
 * far more than one hole of 72 pixels.
 *
 * 4-connectivity for the holes, which is the conservative pairing against the
 * mask's implicit 8-connectivity: a diagonal chain of excluded pixels is read as
 * separate holes rather than one, so this over-counts rather than under-counts,
 * and a predicate built on it fails safe.
 *
 * `region` bounds the search exactly as extraction did. Without it the whole
 * exterior would read as one enormous hole, which is why it is required rather
 * than optional.
 */
export function silhouetteHoleCount(silhouette: Silhouette, region: Silhouette): number {
  assertSameGrid(silhouette, region, "silhouetteHoleCount");
  const { width, height } = silhouette;
  const seen = new Uint8Array(width * height);
  const stack: number[] = [];
  let holes = 0;

  const excluded = (i: number): boolean =>
    (region.mask[i] ?? 0) !== 0 && (silhouette.mask[i] ?? 0) === 0;

  for (let start = 0; start < seen.length; start += 1) {
    if (seen[start] === 1 || !excluded(start)) continue;
    // One flood fill per component; `touchesBorder` decides after it completes,
    // so a component is never miscounted by the order its pixels are visited.
    let touchesBorder = false;
    seen[start] = 1;
    stack.push(start);
    while (stack.length > 0) {
      const index = stack.pop() as number;
      const x = index % width;
      const y = (index - x) / width;
      if (x === 0 || y === 0 || x === width - 1 || y === height - 1) touchesBorder = true;
      for (const neighbour of [
        x > 0 ? index - 1 : -1,
        x < width - 1 ? index + 1 : -1,
        y > 0 ? index - width : -1,
        y < height - 1 ? index + width : -1,
      ]) {
        if (neighbour < 0) continue;
        if (seen[neighbour] === 1) continue;
        // A neighbour outside the region is the region's edge, not a hole wall:
        // reaching one means this component is open to the outside.
        if ((region.mask[neighbour] ?? 0) === 0) {
          touchesBorder = true;
          continue;
        }
        if ((silhouette.mask[neighbour] ?? 0) !== 0) continue;
        seen[neighbour] = 1;
        stack.push(neighbour);
      }
    }
    if (!touchesBorder) holes += 1;
  }
  return holes;
}

/** Two silhouettes must be the same size to be compared. */
export function assertSameGrid(a: Silhouette, b: Silhouette, context = "silhouette comparison"): void {
  if (a.width !== b.width || a.height !== b.height) {
    throw new CalibrationError(
      "dimension-mismatch",
      `${context}: silhouettes are ${a.width}x${a.height} and ${b.width}x${b.height}. Calibration never resizes.`,
    );
  }
}

/** Number of inside pixels. */
export function silhouetteArea(silhouette: Silhouette): number {
  let area = 0;
  for (let i = 0; i < silhouette.mask.length; i += 1) area += silhouette.mask[i] ?? 0;
  return area;
}

/** Centroid of the inside pixels, in pixel coordinates. */
export function silhouetteCentroid(silhouette: Silhouette): { x: number; y: number; area: number } {
  let sumX = 0;
  let sumY = 0;
  let area = 0;
  for (let y = 0; y < silhouette.height; y += 1) {
    for (let x = 0; x < silhouette.width; x += 1) {
      if ((silhouette.mask[y * silhouette.width + x] ?? 0) === 0) continue;
      sumX += x;
      sumY += y;
      area += 1;
    }
  }
  if (area === 0) {
    throw new CalibrationError("empty-region", "silhouetteCentroid: the silhouette is empty.");
  }
  return { x: sumX / area, y: sumY / area, area };
}

/** Axis-aligned bounds of the inside pixels, inclusive. */
export interface SilhouetteBounds {
  readonly minX: number;
  readonly minY: number;
  readonly maxX: number;
  readonly maxY: number;
}

export function silhouetteBounds(silhouette: Silhouette): SilhouetteBounds {
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;
  for (let y = 0; y < silhouette.height; y += 1) {
    for (let x = 0; x < silhouette.width; x += 1) {
      if ((silhouette.mask[y * silhouette.width + x] ?? 0) === 0) continue;
      if (x < minX) minX = x;
      if (x > maxX) maxX = x;
      if (y < minY) minY = y;
      if (y > maxY) maxY = y;
    }
  }
  if (maxX < minX) {
    throw new CalibrationError("empty-region", "silhouetteBounds: the silhouette is empty.");
  }
  return { minX, minY, maxX, maxY };
}

/**
 * The boundary: inside pixels with at least one 4-neighbour outside.
 *
 * 4-connectivity for the *boundary test* pairs with 8-connectivity for the
 * contour *walk* below — the standard pairing, and the one that keeps a
 * diagonal staircase from reporting every pixel as boundary.
 *
 * A pixel on the image border counts as boundary, because a silhouette clipped
 * by the capture region has a real edge there and pretending otherwise would
 * hide a framing mistake in the harness.
 */
export function boundaryMask(silhouette: Silhouette): Uint8Array {
  const { width, height, mask } = silhouette;
  const out = new Uint8Array(mask.length);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const index = y * width + x;
      if ((mask[index] ?? 0) === 0) continue;
      const atBorder = x === 0 || y === 0 || x === width - 1 || y === height - 1;
      const touchesOutside =
        atBorder ||
        (mask[index - 1] ?? 0) === 0 ||
        (mask[index + 1] ?? 0) === 0 ||
        (mask[index - width] ?? 0) === 0 ||
        (mask[index + width] ?? 0) === 0;
      out[index] = touchesOutside ? 1 : 0;
    }
  }
  return out;
}

/** Stand-in for infinity that survives the parabola arithmetic below. */
const LARGE = 1e20;

/**
 * One-dimensional lower envelope of parabolas — the inner loop of
 * Felzenszwalb & Huttenlocher's distance transform of sampled functions
 * (2004). Computes `d[q] = min_p ((q - p)² + f[p])` exactly, in O(n).
 */
function lowerEnvelope1d(f: Float64Array, n: number, out: Float64Array): void {
  const vertices = new Int32Array(n);
  const breaks = new Float64Array(n + 1);
  let k = 0;
  vertices[0] = 0;
  breaks[0] = -LARGE;
  breaks[1] = LARGE;

  for (let q = 1; q < n; q += 1) {
    const fq = f[q] ?? 0;
    let v = vertices[k] ?? 0;
    let s = (fq + q * q - ((f[v] ?? 0) + v * v)) / (2 * q - 2 * v);
    while (s <= (breaks[k] ?? -LARGE)) {
      k -= 1;
      v = vertices[k] ?? 0;
      s = (fq + q * q - ((f[v] ?? 0) + v * v)) / (2 * q - 2 * v);
    }
    k += 1;
    vertices[k] = q;
    breaks[k] = s;
    breaks[k + 1] = LARGE;
  }

  k = 0;
  for (let q = 0; q < n; q += 1) {
    while ((breaks[k + 1] ?? LARGE) < q) k += 1;
    const v = vertices[k] ?? 0;
    out[q] = (q - v) * (q - v) + (f[v] ?? 0);
  }
}

/**
 * Exact squared Euclidean distance from every pixel to the nearest seed pixel,
 * by two passes of the lower envelope (columns, then rows). Seeds are the
 * non-zero entries of `seeds`; a grid with no seeds returns `LARGE` everywhere,
 * which the callers all guard against by construction.
 */
export function squaredEuclideanDistanceTransform(seeds: Uint8Array, width: number, height: number): Float64Array {
  const result = new Float64Array(width * height);
  for (let i = 0; i < result.length; i += 1) result[i] = (seeds[i] ?? 0) !== 0 ? 0 : LARGE;

  const column = new Float64Array(height);
  const columnOut = new Float64Array(height);
  for (let x = 0; x < width; x += 1) {
    for (let y = 0; y < height; y += 1) column[y] = result[y * width + x] ?? 0;
    lowerEnvelope1d(column, height, columnOut);
    for (let y = 0; y < height; y += 1) result[y * width + x] = columnOut[y] ?? 0;
  }

  const row = new Float64Array(width);
  const rowOut = new Float64Array(width);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) row[x] = result[y * width + x] ?? 0;
    lowerEnvelope1d(row, width, rowOut);
    for (let x = 0; x < width; x += 1) result[y * width + x] = rowOut[x] ?? 0;
  }

  return result;
}

/** Euclidean (not squared) distance to the nearest seed, in pixels. */
export function distanceToSeeds(seeds: Uint8Array, width: number, height: number): Float64Array {
  const squared = squaredEuclideanDistanceTransform(seeds, width, height);
  const out = new Float64Array(squared.length);
  for (let i = 0; i < squared.length; i += 1) out[i] = Math.sqrt(squared[i] ?? 0);
  return out;
}

/** An ordered, closed loop of boundary pixel centres. */
export interface ContourPath {
  readonly xs: Float64Array;
  readonly ys: Float64Array;
  /** Cumulative arc length at each point, starting at 0. */
  readonly arcLength: Float64Array;
  /** Total closed-loop perimeter in pixels. */
  readonly perimeterPx: number;
}

/** Clockwise 8-neighbourhood, starting north (y grows downwards). */
const RING_X = [0, 1, 1, 1, 0, -1, -1, -1] as const;
const RING_Y = [-1, -1, 0, 1, 1, 1, 0, -1] as const;

/**
 * Ring index of a unit-ring offset. Consecutive ring entries always differ by
 * another ring offset, which is what lets the Moore trace re-express "the
 * background pixel I examined last" in the *new* pixel's frame without a
 * search.
 */
function ringIndexOf(dx: number, dy: number): number {
  for (let i = 0; i < 8; i += 1) {
    if (RING_X[i] === dx && RING_Y[i] === dy) return i;
  }
  return 0;
}

/**
 * Moore-neighbour contour trace of the outer boundary.
 *
 * The start pixel is the first inside pixel in row-major order — the
 * topmost-then-leftmost one — and the walk begins having "come from" its west
 * neighbour, which is outside by construction. Both choices are canonical, and
 * that matters more than it looks: the curvature comparison aligns two contours
 * by normalised arc length from their start points, so a start that depended on
 * anything but the mask would make the alignment depend on it too.
 *
 * Only the outer boundary of the component containing the start pixel is
 * traced. v1 silhouettes are single connected surfaces; a scene with two
 * disjoint surfaces needs them scoped to separate regions before measuring.
 */
export function traceContour(silhouette: Silhouette): ContourPath {
  const { width, height, mask } = silhouette;

  let start = -1;
  for (let i = 0; i < mask.length; i += 1) {
    if ((mask[i] ?? 0) !== 0) {
      start = i;
      break;
    }
  }
  if (start < 0) {
    throw new CalibrationError("empty-region", "traceContour: the silhouette is empty.");
  }

  const inside = (x: number, y: number): boolean =>
    x >= 0 && y >= 0 && x < width && y < height && (mask[y * width + x] ?? 0) !== 0;

  const startX = start % width;
  const startY = Math.floor(start / width);
  const xs: number[] = [startX];
  const ys: number[] = [startY];

  // `backtrack` is the ring index of the neighbour we arrived from: west.
  let currentX = startX;
  let currentY = startY;
  let backtrack = 6;
  const initialBacktrack = backtrack;
  const maxSteps = mask.length * 4;

  for (let step = 0; step < maxSteps; step += 1) {
    let foundIndex = -1;
    let previousIndex = backtrack;
    for (let offset = 1; offset <= 8; offset += 1) {
      const candidate = (backtrack + offset) % 8;
      const nx = currentX + (RING_X[candidate] ?? 0);
      const ny = currentY + (RING_Y[candidate] ?? 0);
      if (inside(nx, ny)) {
        foundIndex = candidate;
        break;
      }
      previousIndex = candidate;
    }
    // An isolated pixel has no inside neighbour; its contour is itself.
    if (foundIndex < 0) break;

    currentX += RING_X[foundIndex] ?? 0;
    currentY += RING_Y[foundIndex] ?? 0;
    backtrack = ringIndexOf(
      (RING_X[previousIndex] ?? 0) - (RING_X[foundIndex] ?? 0),
      (RING_Y[previousIndex] ?? 0) - (RING_Y[foundIndex] ?? 0),
    );
    // Jacob's stopping criterion: back at the start, entered the same way.
    if (currentX === startX && currentY === startY && backtrack === initialBacktrack) break;
    xs.push(currentX);
    ys.push(currentY);
  }

  const n = xs.length;
  const outX = new Float64Array(n);
  const outY = new Float64Array(n);
  const arcLength = new Float64Array(n);
  for (let i = 0; i < n; i += 1) {
    outX[i] = xs[i] ?? 0;
    outY[i] = ys[i] ?? 0;
    if (i > 0) {
      arcLength[i] = (arcLength[i - 1] ?? 0) + Math.hypot((xs[i] ?? 0) - (xs[i - 1] ?? 0), (ys[i] ?? 0) - (ys[i - 1] ?? 0));
    }
  }
  const closingStep = n > 1 ? Math.hypot((xs[0] ?? 0) - (xs[n - 1] ?? 0), (ys[0] ?? 0) - (ys[n - 1] ?? 0)) : 0;

  return {
    xs: outX,
    ys: outY,
    arcLength,
    perimeterPx: (arcLength[n - 1] ?? 0) + closingStep,
  };
}

/**
 * Sample the closed contour at a given arc-length position, interpolating
 * linearly between the two bracketing pixel centres. Positions outside
 * `[0, perimeterPx)` wrap, because the contour is a loop.
 */
export function sampleContourAt(path: ContourPath, position: number): { x: number; y: number } {
  const n = path.xs.length;
  if (n === 1) return { x: path.xs[0] ?? 0, y: path.ys[0] ?? 0 };

  const perimeter = path.perimeterPx;
  let s = position % perimeter;
  if (s < 0) s += perimeter;

  // Binary search for the last vertex at or before `s`.
  let low = 0;
  let high = n - 1;
  while (low < high) {
    const mid = (low + high + 1) >> 1;
    if ((path.arcLength[mid] ?? 0) <= s) low = mid;
    else high = mid - 1;
  }

  const startArc = path.arcLength[low] ?? 0;
  const nextIndex = (low + 1) % n;
  const endArc = low + 1 < n ? (path.arcLength[low + 1] ?? 0) : perimeter;
  const span = endArc - startArc;
  const t = span > 0 ? (s - startArc) / span : 0;
  const x0 = path.xs[low] ?? 0;
  const y0 = path.ys[low] ?? 0;
  const x1 = path.xs[nextIndex] ?? 0;
  const y1 = path.ys[nextIndex] ?? 0;
  return { x: x0 + (x1 - x0) * t, y: y0 + (y1 - y0) * t };
}
