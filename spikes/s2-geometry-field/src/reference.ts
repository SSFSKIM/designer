/**
 * How far the REFERENCE is from Apple.
 *
 * S2's job is to bound the pseudo-SDF's error against the reference contour. But
 * a bound is only worth what the reference is worth, so this module measures the
 * other half: the contour distance between Figma's family (at each smoothing)
 * and Apple's actual `.continuous` curve.
 *
 * If that gap exceeds the field-approximation error -- and it does -- then the
 * field is not the limiting factor for fidelity, and tightening it further buys
 * nothing until the reference family itself changes. That conclusion is the whole
 * reason to measure it here rather than leave it to C7.
 *
 * Method: two-sided Hausdorff distance, computed with the same exact solver used
 * for the error sweep. Reported in units of the corner radius, so it composes
 * with the field's own r-linear bound.
 */

import { buildContour, segPoint, type ShapeSpec } from './contour.js';
import { buildAppleContour } from './apple.js';
import { exactSignedDistance } from './truth.js';

/** Dense first-quadrant corner points of a contour. */
function cornerPoints(
  segments: { kind: string }[],
  sample: (i: number, t: number) => { x: number; y: number },
  perCurve: number
): { x: number; y: number }[] {
  const out: { x: number; y: number }[] = [];
  for (let i = 0; i < segments.length; i++) {
    if (segments[i].kind === 'line') continue;
    for (let k = 0; k <= perCurve; k++) {
      const q = sample(i, k / perCurve);
      if (q.x >= 0 && q.y >= 0) out.push(q);
    }
  }
  return out;
}

export interface RefGap {
  /** Figma smoothing under test */
  smoothing: number;
  /** radius scale applied to the Figma shape before comparing */
  radiusScale: number;
  /** two-sided Hausdorff distance, in units of Apple's corner radius */
  hausdorffPerR: number;
}

/**
 * Hausdorff distance between Figma(smoothing, r * radiusScale) and Apple(r),
 * per unit r. Uses a large box so neither family's budget clamp engages.
 */
export function figmaVsApple(smoothing: number, radiusScale = 1, r = 1, perCurve = 900): number {
  const box = 60 * r;
  const figmaSpec: ShapeSpec = { W: box, H: box, r: r * radiusScale, smoothing };
  const appleSpec: ShapeSpec = { W: box, H: box, r, smoothing: 0 };
  const figma = buildContour(figmaSpec);
  const apple = buildAppleContour(appleSpec);

  const fPts = cornerPoints(
    figma.segments,
    (i, t) => segPoint(figma.segments[i], t),
    perCurve
  );
  const aPts = cornerPoints(
    apple.segments,
    (i, t) => segPoint(apple.segments[i], t),
    perCurve
  );

  let worst = 0;
  for (const q of fPts) worst = Math.max(worst, exactSignedDistance(apple, q).dist);
  for (const q of aPts) worst = Math.max(worst, exactSignedDistance(figma, q).dist);
  return worst / r;
}

/**
 * Best Figma smoothing (and optionally radius scale) approximating Apple's
 * curve, by grid search then local refinement. Answers one of the spec's named
 * delegated unknowns -- "corner smoothing values" -- with a number.
 */
export function bestFigmaMatch(fitRadiusScale: boolean): RefGap {
  let best: RefGap = { smoothing: 0, radiusScale: 1, hausdorffPerR: Infinity };
  const scales = fitRadiusScale ? [0.9, 0.95, 1.0, 1.05, 1.1] : [1];
  for (let s = 0; s <= 1.0001; s += 0.02) {
    for (const sc of scales) {
      const h = figmaVsApple(Number(s.toFixed(3)), sc, 1, 400);
      if (h < best.hausdorffPerR) best = { smoothing: Number(s.toFixed(3)), radiusScale: sc, hausdorffPerR: h };
    }
  }
  // local refinement
  let stepS = 0.01;
  let stepC = fitRadiusScale ? 0.02 : 0;
  for (let it = 0; it < 60; it++) {
    let improved = false;
    for (const ds of [stepS, -stepS]) {
      const s = Math.min(1, Math.max(0, best.smoothing + ds));
      const h = figmaVsApple(s, best.radiusScale, 1, 900);
      if (h < best.hausdorffPerR) {
        best = { ...best, smoothing: s, hausdorffPerR: h };
        improved = true;
      }
    }
    if (stepC > 0) {
      for (const dc of [stepC, -stepC]) {
        const sc = best.radiusScale + dc;
        const h = figmaVsApple(best.smoothing, sc, 1, 900);
        if (h < best.hausdorffPerR) {
          best = { ...best, radiusScale: sc, hausdorffPerR: h };
          improved = true;
        }
      }
    }
    if (!improved) {
      stepS *= 0.5;
      stepC *= 0.5;
      if (stepS < 1e-5) break;
    }
  }
  return best;
}
