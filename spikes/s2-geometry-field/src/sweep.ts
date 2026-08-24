/**
 * The measurement matrix required by S2, and the shared coefficient tables.
 *
 * Sizes are the SHORT dimension; width = size * aspect. Radii are swept as a
 * fraction of the short dimension, which is what makes the rounding-and-
 * smoothing budget bite at the high end (rFrac 0.5 is the capsule limit).
 */

import type { ShapeSpec } from './contour.js';
import { CANDIDATES, type Candidate } from './candidates.js';
import { coeffAt, FIT_GRID, fitCandidate, type FitRow } from './fit.js';
import { measure, type ConfigResult } from './metrics.js';
import { cornerParams } from './contour.js';

export const SMOOTHINGS = [0, 0.2, 0.4, 0.6, 0.8, 1.0];
export const SIZES = [16, 32, 64, 120, 320, 600];
export const ASPECTS = [1, 3, 8];
/** radius as a fraction of the short dimension; 0.5 is the capsule limit */
export const R_FRACS = [0.15, 0.3, 0.5];

export function specsFor(size: number, aspect: number, rFrac: number, smoothing: number): ShapeSpec {
  return { W: (size * aspect) / 2, H: size / 2, r: rFrac * size, smoothing };
}

export function fullMatrix(): ShapeSpec[] {
  const out: ShapeSpec[] = [];
  for (const s of SMOOTHINGS)
    for (const size of SIZES)
      for (const a of ASPECTS) for (const rf of R_FRACS) out.push(specsFor(size, a, rf, s));
  return out;
}

export type Tables = Record<string, FitRow[]>;

/** Fit every candidate across the smoothing grid. Deterministic. */
export function fitAll(cands: Candidate[] = CANDIDATES): Tables {
  const t: Tables = {};
  for (const c of cands) t[c.id] = fitCandidate(c, FIT_GRID);
  return t;
}

export interface Row extends ConfigResult {
  candId: string;
  size: number;
  aspect: number;
  rFrac: number;
  requested: number;
  /** true when the budget clamped the requested smoothing */
  capped: boolean;
}

export function sweep(tables: Tables, cands: Candidate[] = CANDIDATES, specs = fullMatrix()): Row[] {
  const rows: Row[] = [];
  for (const spec of specs) {
    const size = spec.H * 2;
    const aspect = (spec.W * 2) / (spec.H * 2);
    const cp = cornerParams(spec);
    for (const c of cands) {
      const coeff = coeffAt(tables[c.id], cp.smoothingEff);
      const res = measure(c, spec, coeff, {
        band: { halfBand: 8, offsets: 21, minPerCurve: 192, perPxStraight: 0.34 },
      });
      rows.push({
        ...res,
        candId: c.id,
        size,
        aspect,
        rFrac: spec.r / size,
        requested: spec.smoothing,
        capped: cp.smoothingEff < spec.smoothing - 1e-9,
      });
    }
  }
  return rows;
}

export interface Agg {
  n: number;
  valueMax: number;
  valueP95: number;
  gradMaxDeg: number;
  gradP95Deg: number;
  eikonalMax: number;
}

export function agg(rows: Row[], half: number): Agg {
  let valueMax = 0;
  let valueP95 = 0;
  let gradMaxDeg = 0;
  let gradP95Deg = 0;
  let eikonalMax = 0;
  let n = 0;
  for (const r of rows) {
    const b = r.bands.find((x) => x.half === half);
    if (!b) continue;
    n++;
    valueMax = Math.max(valueMax, b.valueMax);
    valueP95 = Math.max(valueP95, b.valueP95);
    gradMaxDeg = Math.max(gradMaxDeg, b.gradMaxDeg);
    gradP95Deg = Math.max(gradP95Deg, b.gradP95Deg);
    eikonalMax = Math.max(eikonalMax, b.eikonalMax);
  }
  return { n, valueMax, valueP95, gradMaxDeg, gradP95Deg, eikonalMax };
}
