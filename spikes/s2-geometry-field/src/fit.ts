/**
 * Coefficient fitting.
 *
 * The whole corner problem is scale-invariant: for a fixed effective smoothing,
 * the corner contour in units of the radius is fixed, and every candidate field
 * is scale-covariant. So one coefficient table indexed by EFFECTIVE smoothing
 * generalizes to every size, aspect ratio and radius -- which the sweep then
 * verifies empirically rather than assuming.
 *
 * Objective: minimize the max |field| over dense samples ON the true contour,
 * i.e. drive the candidate's zero level set onto the true contour in the L-inf
 * sense. That is scale-free (it is a pure contour deviation, in units of r) and
 * it is the quantity rim lighting reads. Off-contour behaviour is then measured,
 * not fitted, so the reported band errors are not self-congratulatory.
 *
 * Families C and D share a zero level set, so they share one fit; D's
 * normalization only changes the field away from the contour.
 */

import { buildContour, segPoint, type ShapeSpec } from './contour.js';
import type { Candidate } from './candidates.js';

/** Canonical fitting geometry: unit radius, edges long enough that nothing caps. */
export function canonicalSpec(sEff: number): ShapeSpec {
  return { W: 64, H: 64, r: 1, smoothing: sEff };
}

/**
 * Dense samples on the true contour, restricted to the first quadrant: every
 * candidate field is built on |x|,|y| so it is mirror-symmetric by construction,
 * and one corner determines all four.
 */
export function contourSamples(spec: ShapeSpec, perCurve = 512): { x: number; y: number }[] {
  const c = buildContour(spec);
  const out: { x: number; y: number }[] = [];
  for (const s of c.segments) {
    const n = s.kind === 'line' ? 8 : perCurve;
    for (let i = 0; i <= n; i++) {
      const q = segPoint(s, i / n);
      if (q.x >= -1e-12 && q.y >= -1e-12) out.push(q);
    }
  }
  return out;
}

export type Objective = (coeff: number[]) => number;

export function makeContourObjective(
  cand: Candidate,
  sEff: number,
  ref?: { spec: ShapeSpec; pts: { x: number; y: number }[]; re: number }
): Objective {
  const spec = ref?.spec ?? canonicalSpec(sEff);
  const pts = ref?.pts ?? contourSamples(spec);
  // flat typed arrays: the objective is called tens of thousands of times
  const n = pts.length;
  const xs = new Float64Array(n);
  const ys = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    xs[i] = pts[i].x;
    ys[i] = pts[i].y;
  }
  return (coeff: number[]) => {
    const prep = cand.prepare(spec, coeff, ref?.re);
    let worst = 0;
    for (let i = 0; i < n; i++) {
      const e = Math.abs(cand.evalAt(prep, xs[i], ys[i]));
      if (e > worst) worst = e;
    }
    return Number.isFinite(worst) ? worst : 1e9;
  };
}

// ---------------------------------------------------------------------------
// Nelder-Mead (small dimension, non-smooth objective)
// ---------------------------------------------------------------------------

export function nelderMead(
  f: Objective,
  x0: number[],
  scale: number[],
  opts: { maxIter?: number; tol?: number } = {}
): { x: number[]; f: number } {
  const n = x0.length;
  const maxIter = opts.maxIter ?? 800;
  const tol = opts.tol ?? 1e-14;

  if (n === 0) return { x: [], f: f([]) };

  const simplex: { x: number[]; f: number }[] = [];
  const push = (x: number[]) => simplex.push({ x: x.slice(), f: f(x) });
  push(x0);
  for (let i = 0; i < n; i++) {
    const x = x0.slice();
    x[i] += scale[i];
    push(x);
  }

  const alpha = 1;
  const gamma = 2;
  const rho = 0.5;
  const sigma = 0.5;

  for (let iter = 0; iter < maxIter; iter++) {
    simplex.sort((a, b) => a.f - b.f);
    const best = simplex[0];
    const worst = simplex[n];
    if (Math.abs(worst.f - best.f) <= tol * (Math.abs(best.f) + tol)) break;

    const centroid = new Array<number>(n).fill(0);
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) centroid[j] += simplex[i].x[j] / n;
    }

    const reflect = centroid.map((c, j) => c + alpha * (c - worst.x[j]));
    const fr = f(reflect);
    if (fr < simplex[0].f) {
      const expand = centroid.map((c, j) => c + gamma * (reflect[j] - c));
      const fe = f(expand);
      simplex[n] = fe < fr ? { x: expand, f: fe } : { x: reflect, f: fr };
      continue;
    }
    if (fr < simplex[n - 1].f) {
      simplex[n] = { x: reflect, f: fr };
      continue;
    }
    const contract = centroid.map((c, j) => c + rho * (worst.x[j] - c));
    const fc = f(contract);
    if (fc < worst.f) {
      simplex[n] = { x: contract, f: fc };
      continue;
    }
    for (let i = 1; i <= n; i++) {
      const x = simplex[0].x.map((b, j) => b + sigma * (simplex[i].x[j] - b));
      simplex[i] = { x, f: f(x) };
    }
  }
  simplex.sort((a, b) => a.f - b.f);
  return { x: simplex[0].x, f: simplex[0].f };
}

// ---------------------------------------------------------------------------
// Linear Chebyshev fit (families C and D)
// ---------------------------------------------------------------------------

/** Solve a symmetric positive-definite system by Gaussian elimination. */
function solveSPD(A: number[][], b: number[]): number[] {
  const n = b.length;
  const M = A.map((row, i) => [...row, b[i]]);
  for (let c = 0; c < n; c++) {
    let piv = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
    [M[c], M[piv]] = [M[piv], M[c]];
    const d = M[c][c];
    if (Math.abs(d) < 1e-300) continue;
    for (let r = 0; r < n; r++) {
      if (r === c) continue;
      const f = M[r][c] / d;
      for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k];
    }
  }
  return M.map((row, i) => (Math.abs(row[i]) < 1e-300 ? 0 : row[n] / row[i]));
}

/**
 * Minimize ||b + A k||_inf by p-norm continuation: solve weighted least squares
 * with weights |e_j|^(p-2), ratcheting p from 2 upward. As p grows the solution
 * approaches the Chebyshev (L-inf) optimum, which is the right objective here --
 * the bound we report is a max, not an average. More robust than Lawson's
 * algorithm alone, which stalls on this problem's near-degenerate weightings.
 */
export function chebyshevLinearFit(A: number[][], b: number[]): { k: number[]; f: number } {
  const m = b.length;
  const n = A[0]?.length ?? 0;
  if (m === 0 || n === 0) return { k: new Array(n).fill(0), f: 0 };

  const residuals = (k: number[]) => {
    const res = new Array<number>(m);
    let worst = 0;
    for (let j = 0; j < m; j++) {
      let e = b[j];
      const row = A[j];
      for (let p = 0; p < n; p++) e += row[p] * k[p];
      res[j] = Math.abs(e);
      if (res[j] > worst) worst = res[j];
    }
    return { res, worst };
  };

  const wls = (w: number[]) => {
    const N: number[][] = Array.from({ length: n }, () => new Array<number>(n).fill(0));
    const rhs = new Array<number>(n).fill(0);
    for (let j = 0; j < m; j++) {
      const wj = w[j];
      if (!(wj > 0)) continue;
      const row = A[j];
      for (let p = 0; p < n; p++) {
        rhs[p] -= wj * row[p] * b[j];
        for (let q = 0; q < n; q++) N[p][q] += wj * row[p] * row[q];
      }
    }
    return solveSPD(N, rhs);
  };

  let k = wls(new Array<number>(m).fill(1));
  let best = { k: k.slice(), f: residuals(k).worst };

  for (const p of [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]) {
    for (let it = 0; it < 40; it++) {
      const { res, worst } = residuals(k);
      if (worst <= 0) break;
      const w = res.map((e) => Math.pow(Math.max(e, worst * 1e-12) / worst, p - 2));
      const kn = wls(w);
      if (!kn.every((x) => Number.isFinite(x))) break;
      k = kn;
      const f = residuals(k).worst;
      if (f < best.f) best = { k: k.slice(), f };
    }
    k = best.k.slice();
  }
  return best;
}

export interface FitRow {
  sEff: number;
  coeff: number[];
  /** max |field| on the true contour, in units of the corner radius */
  contourDevPerR: number;
}

/**
 * Fit one candidate at one effective-smoothing value.
 *
 * Families C and D are LINEAR in their coefficients once the corner offset is
 * pinned to the true reach p, so they get an exact Chebyshev solve. Families A
 * and B are nonlinear (a radius scale, an exponent), so they get a multi-start
 * Nelder-Mead. Using the exact solver where one exists is what stops the
 * comparison from measuring optimizer luck instead of family capability.
 */
export function fitOne(cand: Candidate, sEff: number): FitRow {
  const spec = canonicalSpec(sEff);
  const obj = makeContourObjective(cand, sEff);

  if (cand.id === 'rsup' || cand.id === 'rsupn') {
    const n = cand.nCoeff;
    const prep0 = cand.prepare(spec, new Array(n).fill(0));
    const re = prep0.re;
    const pts = contourSamples(spec);
    const A: number[][] = [];
    const b: number[] = [];
    for (const q of pts) {
      const cx = Math.max(Math.abs(q.x) - (spec.W - re), 0);
      const cy = Math.max(Math.abs(q.y) - (spec.H - re), 0);
      const rho = Math.hypot(cx, cy);
      if (cx <= 0 || cy <= 0 || rho <= 0) continue; // straight edges: residual is 0
      const s2 = (2 * cx * cy) / (rho * rho);
      // field = rho - re * (1 + s2^2 * sum_i k_i s2^i)
      const row = new Array<number>(n);
      for (let i = 0; i < n; i++) row[i] = -re * Math.pow(s2, i + 2);
      A.push(row);
      b.push(rho - re);
    }
    const lin = chebyshevLinearFit(A, b);
    // Polish under the true objective (which also covers the straight edges and
    // the interior branch) in case the linear model missed anything.
    let best = { x: lin.k, f: obj(lin.k) };
    for (const sc of [0.05, 0.01, 2e-3, 4e-4]) {
      const r = nelderMead(obj, best.x, new Array(n).fill(sc));
      if (r.f < best.f) best = r;
    }
    return { sEff, coeff: best.x, contourDevPerR: best.f };
  }

  const { x0, scale } = cand.init(sEff);
  let best: { x: number[]; f: number } = { x: x0, f: obj(x0) };
  // deterministic multi-start: the objective is a max, so it has plateaus and
  // local minima that a single descent will sit down in
  const mults = [1, 0.4, 2.5];
  for (const m of mults) {
    for (const sgn of [1, -1]) {
      const start = x0.map((v, i) => v + sgn * (m - 1) * 0.25 * scale[i]);
      const r = nelderMead(obj, start, scale.map((v) => v * m));
      if (r.f < best.f) best = r;
    }
  }
  for (let round = 0; round < 3; round++) {
    const r = nelderMead(obj, best.x, scale.map((v) => v * Math.pow(0.05, round + 1)));
    if (r.f < best.f) best = r;
  }
  return { sEff, coeff: best.x, contourDevPerR: best.f };
}

/** Fit one candidate across a grid of effective smoothing values. */
export function fitCandidate(cand: Candidate, sGrid: number[]): FitRow[] {
  return sGrid.map((s) => fitOne(cand, s));
}

/**
 * Fit a radial-support family against an ARBITRARY reference corner rather than
 * Figma's. Used to answer the question the reference gap raises: if the field's
 * own error is smaller than the distance between Figma's family and Apple's real
 * curve, can the field simply be fit to Apple's curve directly and skip the
 * intermediate family? (It can -- see the findings.)
 */
export function fitToReference(
  cand: Candidate,
  refSpec: ShapeSpec,
  refPts: { x: number; y: number }[],
  re: number
): FitRow {
  const n = cand.nCoeff;
  const ref = { spec: refSpec, pts: refPts, re };
  const obj = makeContourObjective(cand, 0, ref);

  const A: number[][] = [];
  const b: number[] = [];
  for (const q of refPts) {
    const cx = Math.max(Math.abs(q.x) - (refSpec.W - re), 0);
    const cy = Math.max(Math.abs(q.y) - (refSpec.H - re), 0);
    const rho = Math.hypot(cx, cy);
    if (cx <= 0 || cy <= 0 || rho <= 0) continue;
    const s2 = (2 * cx * cy) / (rho * rho);
    const row = new Array<number>(n);
    for (let i = 0; i < n; i++) row[i] = -re * Math.pow(s2, i + 2);
    A.push(row);
    b.push(rho - re);
  }
  const lin = chebyshevLinearFit(A, b);
  let best = { x: lin.k, f: obj(lin.k) };
  for (const sc of [0.05, 0.01, 2e-3, 4e-4]) {
    const r = nelderMead(obj, best.x, new Array(n).fill(sc));
    if (r.f < best.f) best = r;
  }
  return { sEff: NaN, coeff: best.x, contourDevPerR: best.f / (refSpec.r || 1) };
}

/** Linear interpolation into a fitted table, by effective smoothing. */
export function coeffAt(table: FitRow[], sEff: number): number[] {
  if (table.length === 0) throw new Error('empty fit table');
  if (sEff <= table[0].sEff) return table[0].coeff.slice();
  const last = table[table.length - 1];
  if (sEff >= last.sEff) return last.coeff.slice();
  for (let i = 1; i < table.length; i++) {
    const a = table[i - 1];
    const b = table[i];
    if (sEff <= b.sEff) {
      const u = (sEff - a.sEff) / (b.sEff - a.sEff);
      return a.coeff.map((v, j) => v + u * (b.coeff[j] - v));
    }
  }
  return last.coeff.slice();
}

export const FIT_GRID = [
  0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
  0.9, 0.95, 1.0,
];
