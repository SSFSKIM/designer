/**
 * Candidate parametric pseudo-SDF families.
 *
 * All four share one corner-local setup. With half-extents (W, H) and a corner
 * offset `re`:
 *
 *   q  = (|x| - (W - re), |y| - (H - re))
 *   qc = max(q, 0)
 *
 * `qc == 0` is the deep interior (the box branch); exactly one positive
 * component is the straight-edge region; both positive is the corner sector.
 * Every family reduces to `qc.x - re` (i.e. `|x| - W`) in the straight-edge
 * region, so all four are EXACT against the straight edges by construction --
 * the entire contest is inside the corner sector.
 *
 * The families:
 *
 *  A `roundbox`  -- the standard analytic rounded-rect SDF, corner radius
 *                   reparameterized as `kr * r`. One fitted coefficient.
 *  B `superell`  -- superellipse exponent `n` mapped onto the same corner,
 *                   normalized by |grad| so the field reads as a distance.
 *                   Two fitted coefficients.
 *  C `rsup`      -- radial support field: the corner sector's radius becomes a
 *                   function of corner angle, `R(theta) = re * (1 + sum k_i v^i)`
 *                   with `v = sin^2(2*theta)`. `v` is computable from `qc`
 *                   with no transcendentals. Four fitted coefficients.
 *  D `rsupn`     -- C plus the first-order gradient normalization
 *                   `d = (rho - R) / sqrt(1 + (R'/rho)^2)`, which is what turns
 *                   a level-set-correct field into a distance-correct one.
 *
 * Why the corner offset matters: setting `re` to the corner REACH
 * `p = (1 + smoothing) * r` -- not the radius `r` -- makes the corner sector of
 * the field coincide with the true corner's extent, and makes `R(0) = R(pi/2) = p`
 * exact. Anchoring at `r` instead leaves the corner's "shoulder" (the
 * zero-curvature run where the cubic peels off the straight edge) outside the
 * sector, where no angular correction can reach it. The fits below are free to
 * discover `kr`, and for C/D they discover `kr ~ 1 + smoothing`.
 */

import { cornerParams, type ShapeSpec } from './contour.js';

export interface Prepared {
  W: number;
  H: number;
  /** corner offset actually used by the field */
  re: number;
  /** fitted coefficients, family-specific */
  k: number[];
}

export interface Candidate {
  id: string;
  label: string;
  /** number of fitted coefficients */
  nCoeff: number;
  /** initial guess + search scale for the fit, given effective smoothing */
  init(sEff: number): { x0: number[]; scale: number[] };
  /**
   * CPU-side derivation: authoring channels + coefficients -> shader uniforms.
   * `reOverride` lets the corner offset be pinned to a reference family's own
   * edge reach, so the same field family can be fit against Figma's corner or
   * Apple's without a second implementation.
   */
  prepare(spec: ShapeSpec, coeff: number[], reOverride?: number): Prepared;
  /** the field itself */
  evalAt(p: Prepared, x: number, y: number): number;
}

// ---------------------------------------------------------------------------
// shared corner-local algebra
// ---------------------------------------------------------------------------

/** Effective smoothing after Figma's rounding-and-smoothing budget clamp. */
export function effectiveSmoothing(spec: ShapeSpec): number {
  return cornerParams(spec).smoothingEff;
}

/** The corner reach p = (1 + s_eff) * r, clamped by the budget. */
export function cornerReach(spec: ShapeSpec): number {
  return cornerParams(spec).p;
}

interface Local {
  qx: number;
  qy: number;
  cx: number;
  cy: number;
  rho: number;
  /** max(qx, qy) */
  m: number;
}

function local(p: Prepared, x: number, y: number): Local {
  const qx = Math.abs(x) - (p.W - p.re);
  const qy = Math.abs(y) - (p.H - p.re);
  const cx = Math.max(qx, 0);
  const cy = Math.max(qy, 0);
  return { qx, qy, cx, cy, rho: Math.hypot(cx, cy), m: Math.max(qx, qy) };
}

/** v = sin^2(2*theta) from the clamped corner vector, no transcendentals. */
function vOf(l: Local): number {
  if (l.rho <= 0) return 0;
  const s2 = (2 * l.cx * l.cy) / (l.rho * l.rho);
  return s2 * s2;
}

// ---------------------------------------------------------------------------
// A -- analytic rounded box, radius reparameterized
// ---------------------------------------------------------------------------

export const roundbox: Candidate = {
  id: 'roundbox',
  label: 'A: analytic rounded-rect SDF, radius reparameterized by smoothing',
  nCoeff: 1,
  init: (s) => ({ x0: [1 + 0.3 * s], scale: [0.25] }),
  prepare: (spec, k) => {
    const cp = cornerParams(spec);
    const re = Math.min(Math.max(k[0] * cp.r, 0), cp.budget);
    return { W: spec.W, H: spec.H, re, k: [] };
  },
  evalAt: (p, x, y) => {
    const l = local(p, x, y);
    return l.rho + Math.min(l.m, 0) - p.re;
  },
};

// ---------------------------------------------------------------------------
// B -- superellipse exponent, gradient-normalized
// ---------------------------------------------------------------------------

export const superell: Candidate = {
  id: 'superell',
  label: 'B: superellipse-exponent field on the same corner, |grad|-normalized',
  nCoeff: 2,
  init: (s) => ({ x0: [1 + 0.45 * s, 2 + 2.6 * s], scale: [0.25, 1.2] }),
  prepare: (spec, k) => {
    const cp = cornerParams(spec);
    const re = Math.min(Math.max(k[0] * cp.r, 1e-9), cp.budget);
    const n = Math.min(Math.max(k[1], 2), 24);
    return { W: spec.W, H: spec.H, re, k: [n] };
  },
  evalAt: (p, x, y) => {
    const l = local(p, x, y);
    if (l.rho <= 0) return l.m - p.re;
    const n = p.k[0];
    if (l.cx <= 0 || l.cy <= 0) return l.rho - p.re; // straight-edge region: exact
    const g = Math.pow(Math.pow(l.cx, n) + Math.pow(l.cy, n), 1 / n);
    // |grad g| for the normalized-implicit distance estimate
    const gx = Math.pow(l.cx / g, n - 1);
    const gy = Math.pow(l.cy / g, n - 1);
    const gm = Math.hypot(gx, gy);
    return (g - p.re) / (gm > 0 ? gm : 1);
  },
};

// ---------------------------------------------------------------------------
// C -- radial support field with a polynomial corner correction
// ---------------------------------------------------------------------------

/**
 * Number of correction terms. The basis is s2^2 .. s2^(NK+1) where
 * s2 = sin(2*theta). Starting at the SQUARE is not arbitrary: the true radial
 * support has R'(0) = 0, because the corner leaves the straight edge tangentially
 * AND with zero curvature, so any basis with a linear term in s2 would have to
 * cancel it. Including odd powers above that (s2^3, s2^5) matters because R is
 * not an even function of theta about 0 -- an s2^2-only (i.e. sin^2) basis
 * converges visibly more slowly.
 */
export const RSUP_NK = Number(process.env.RSUP_NK ?? 5);

/**
 * The corner offset is the TRUE corner reach p = (1 + s_eff) * r, not a fitted
 * radius. Two reasons, both structural:
 *
 *  - The field's corner sector then coincides exactly with the true corner's
 *    extent. Any smaller offset leaves the corner's "shoulder" -- the
 *    zero-curvature run where the cubic peels off the straight edge -- outside
 *    the sector, where the angular correction cannot reach it, and the field
 *    silently reports the straight-edge distance there.
 *  - R(0) = R(pi/2) = p becomes exact, so the corner joins the straight edges
 *    with no seam and no fitted degree of freedom spent on the join.
 *
 * It also removes a degenerate dimension from the fit (radius and correction
 * trade off against each other) and it costs the shader nothing: p is already
 * derived CPU-side.
 */
function rsupPrepare(spec: ShapeSpec, k: number[], reOverride?: number): Prepared {
  const cp = cornerParams(spec);
  return { W: spec.W, H: spec.H, re: reOverride ?? cp.p, k: k.slice() };
}

const rsupInit = (s: number) => ({
  x0: [0.5 * s, -0.2 * s, 0.1 * s, 0, 0].slice(0, RSUP_NK),
  scale: [0.2, 0.2, 0.15, 0.1, 0.08].slice(0, RSUP_NK),
});

/** R(theta) = re * (1 + s2^2 * (k0 + k1*s2 + k2*s2^2 + ...)), by Horner. */
function rsupR(p: Prepared, s2: number): number {
  let acc = 0;
  for (let i = RSUP_NK - 1; i >= 0; i--) acc = acc * s2 + p.k[i];
  return p.re * (1 + s2 * s2 * acc);
}

/** dR/d(s2), needed for family D's normalization. */
function rsupdRds2(p: Prepared, s2: number): number {
  // d/ds2 [ sum_i k_i * s2^(i+2) ] = sum_i (i+2) * k_i * s2^(i+1)
  let acc = 0;
  for (let i = RSUP_NK - 1; i >= 0; i--) acc = acc * s2 + (i + 2) * p.k[i];
  return p.re * s2 * acc;
}

export const rsup: Candidate = {
  id: 'rsup',
  label: 'C: analytic rounded-rect SDF + polynomial corner correction in sin(2t)',
  nCoeff: RSUP_NK,
  init: rsupInit,
  prepare: rsupPrepare,
  evalAt: (p, x, y) => {
    const l = local(p, x, y);
    const s2 = l.rho > 0 ? (2 * l.cx * l.cy) / (l.rho * l.rho) : 0;
    return l.rho + Math.min(l.m, 0) - rsupR(p, s2);
  },
};

// ---------------------------------------------------------------------------
// D -- C plus first-order gradient normalization
// ---------------------------------------------------------------------------

export const rsupn: Candidate = {
  id: 'rsupn',
  label: 'D: C plus the first-order |grad| normalization (recommended shape)',
  nCoeff: RSUP_NK,
  init: rsupInit,
  prepare: rsupPrepare,
  // Branchless, and a line-for-line mirror of `sd_rsupn` in bench/shaders.wgsl
  // so the f32 cross-check compares the same arithmetic, not two dialects of it.
  // The straight-edge region needs no special case: there s2 == 0, so R == re and
  // dR/dtheta == 0, and the expression collapses to the exact edge distance.
  evalAt: (p, x, y) => {
    const l = local(p, x, y);
    const r2 = Math.max(l.cx * l.cx + l.cy * l.cy, 1e-20);
    const inv = 1 / r2;
    const s2 = 2 * l.cx * l.cy * inv;
    const c2 = (l.cx * l.cx - l.cy * l.cy) * inv;
    const R = rsupR(p, s2);
    const dRdt = rsupdRds2(p, s2) * (2 * c2);
    const rho = Math.sqrt(r2);
    const base = rho + Math.min(l.m, 0) - R;
    const g = dRdt * inv * rho;
    return base / Math.sqrt(1 + g * g);
  },
};

export const CANDIDATES: Candidate[] = [roundbox, superell, rsup, rsupn];

export function candidateById(id: string): Candidate {
  const c = CANDIDATES.find((x) => x.id === id);
  if (!c) throw new Error(`unknown candidate: ${id}`);
  return c;
}

// ---------------------------------------------------------------------------
// gradient by central differences of the field as returned
// ---------------------------------------------------------------------------

export interface GradResult {
  gx: number;
  gy: number;
  /** magnitude of the finite-difference gradient; a true SDF has 1 */
  mag: number;
  /**
   * true when the one-sided differences disagree materially, i.e. the sample
   * sits on a C1 kink of the field (these occur on the interior medial-axis
   * seams of the box branch)
   */
  kink: boolean;
}

export function fieldGradient(
  cand: Candidate,
  p: Prepared,
  x: number,
  y: number,
  h: number
): GradResult {
  const f = (a: number, b: number) => cand.evalAt(p, a, b);
  const fpx = f(x + h, y);
  const fmx = f(x - h, y);
  const fpy = f(x, y + h);
  const fmy = f(x, y - h);
  const f0 = f(x, y);
  const gx = (fpx - fmx) / (2 * h);
  const gy = (fpy - fmy) / (2 * h);
  // one-sided comparison for kink detection
  const fx1 = (fpx - f0) / h;
  const fx2 = (f0 - fmx) / h;
  const fy1 = (fpy - f0) / h;
  const fy2 = (f0 - fmy) / h;
  const kink = Math.abs(fx1 - fx2) > 0.02 || Math.abs(fy1 - fy2) > 0.02;
  return { gx, gy, mag: Math.hypot(gx, gy), kink };
}
