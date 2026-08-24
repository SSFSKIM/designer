/**
 * The v1 pseudo-SDF field: `rsupn` (family D), and its un-normalized sibling
 * `rsup` (family C, the quality governor's first within-tier step).
 *
 * This is the canonical TypeScript implementation. `src/wgsl.ts` carries the
 * WGSL that C6 ships, and `test/wgsl-sync.test.ts` holds the two in step
 * against S2's committed f32 cross-check fixture, so "the shader computes the
 * same function" is asserted rather than assumed.
 *
 * ## The construction
 *
 * With half-extents `(halfW, halfH)` and a corner offset `re`:
 *
 *   q  = (|x| - (halfW - re), |y| - (halfH - re))
 *   qc = max(q, 0)
 *
 * `qc == 0` is the deep interior (the box branch); exactly one positive
 * component is the straight-edge region; both positive is the corner sector.
 * Both families reduce to the exact half-plane distance in the straight-edge
 * region, so they are EXACT against the straight edges by construction — the
 * entire approximation lives inside the corner sector.
 *
 * Inside the sector the corner's radius becomes a function of corner angle,
 * `R(theta) = re * (1 + s2^2 * poly(s2))` with `s2 = sin(2*theta)`, which
 * is the "radial support" the family is named for.
 *
 * ## Three design points that are load-bearing for the declared bound
 *
 * 1. **The corner offset is the true corner REACH `p = (1 + s_eff) * r`, not the
 *    radius `r`.** Anchoring at `r` leaves the corner's shoulder — the
 *    zero-curvature run where the cubic peels off the straight edge — outside
 *    the field's corner sector, where no angular correction can reach it, and
 *    the field then silently reports the straight-edge distance there. With
 *    `re = p` the sector coincides exactly with the true corner and
 *    `R(0) = R(pi/2) = p` is exact. `p` is derived CPU-side, so this costs the
 *    shader nothing.
 *
 * 2. **`sin 2theta` and `cos 2theta` come out of the clamped corner vector by
 *    division — no `atan2`, no trigonometry:**
 *    `s2 = 2*qc.x*qc.y / rho^2` and `c2 = (qc.x^2 - qc.y^2) / rho^2`. That is
 *    what makes an angular correction affordable at all.
 *
 * 3. **The only guard is a clamp on the squared corner radius**, which keeps the
 *    deep-interior case (`rho == 0`) from producing NaN without costing a
 *    branch. It is also why the straight-edge region needs no special case:
 *    there `s2 == 0`, so `R == re` and `dR/dtheta == 0`, and the expression
 *    collapses to the exact edge distance.
 *
 * ## The normalization
 *
 * Family D divides by `sqrt(1 + (R'/rho)^2)`, the first-order correction that
 * turns a level-set-correct field into a distance-correct one. It costs one
 * `rsqrt` and roughly doubles the corner arithmetic; it buys 3.4x on value
 * error, 1.5x on gradient error, and takes the eikonal defect from 7.9% to 2.7%.
 * Family C is the same field without it: same coefficient table, same zero level
 * set, 29% less total cost, and a bound of 0.57 px / 4.26 degrees.
 */

import { type CornerCoefficients, RSUP_BASIS_ORDER } from "./coefficients";
import type { Vec2 } from "./channels";

/**
 * Everything the field needs, in shape-local coordinates (origin at the shape's
 * centre). Derived CPU-side from `{ size, radii, smoothing }`; for C6 these are
 * exactly the six derived floats the instance buffer widens by (`reach` plus
 * five coefficients).
 */
export interface FieldParams {
  readonly halfW: number;
  readonly halfH: number;
  /** the corner offset — the true corner reach, see design point 1 above */
  readonly reach: number;
  readonly k: CornerCoefficients;
}

/** Guard on the squared corner radius. Mirrors the WGSL constant exactly. */
const R2_FLOOR = 1e-20;

interface CornerLocal {
  /** signed corner coordinates */
  qx: number;
  qy: number;
  /** clamped corner coordinates, max(q, 0) */
  cx: number;
  cy: number;
  /** max(qx, qy) — the box branch's distance before clamping */
  m: number;
  r2: number;
  rho: number;
  inv: number;
  /** sin(2*theta) */
  s2: number;
  /** cos(2*theta) */
  c2: number;
}

function cornerLocal(p: FieldParams, x: number, y: number): CornerLocal {
  const qx = Math.abs(x) - (p.halfW - p.reach);
  const qy = Math.abs(y) - (p.halfH - p.reach);
  const cx = Math.max(qx, 0);
  const cy = Math.max(qy, 0);
  const r2 = Math.max(cx * cx + cy * cy, R2_FLOOR);
  const inv = 1 / r2;
  return {
    qx,
    qy,
    cx,
    cy,
    m: Math.max(qx, qy),
    r2,
    rho: Math.sqrt(r2),
    inv,
    s2: 2 * cx * cy * inv,
    c2: (cx * cx - cy * cy) * inv,
  };
}

/**
 * `R(theta) / re - 1 = s2^2 * poly(s2)` and its first two derivatives in `s2`,
 * all by Horner on the same coefficient list.
 *
 *   R    = re * (1 + s2^2 * A),   A = sum_i k_i s2^i
 *   dR   = re * s2 * B,           B = sum_i (i+2) k_i s2^i
 *   d2R  = re * C,                C = sum_i (i+1)(i+2) k_i s2^i
 */
function hornerA(k: CornerCoefficients, s2: number): number {
  let acc = 0;
  for (let i = RSUP_BASIS_ORDER - 1; i >= 0; i--) acc = acc * s2 + (k[i] as number);
  return acc;
}

function hornerB(k: CornerCoefficients, s2: number): number {
  let acc = 0;
  for (let i = RSUP_BASIS_ORDER - 1; i >= 0; i--) acc = acc * s2 + (i + 2) * (k[i] as number);
  return acc;
}

function hornerC(k: CornerCoefficients, s2: number): number {
  let acc = 0;
  for (let i = RSUP_BASIS_ORDER - 1; i >= 0; i--) acc = acc * s2 + (i + 1) * (i + 2) * (k[i] as number);
  return acc;
}

/** The radial support R(theta), evaluated from `s2 = sin(2*theta)`. */
export function cornerSupport(p: FieldParams, s2: number): number {
  return p.reach * (1 + s2 * s2 * hornerA(p.k, s2));
}

/**
 * Family C — `rsup`. The radial-support field without the gradient
 * normalization: same zero level set as family D, 29% cheaper, and the quality
 * governor's first step within the texture tier.
 *
 * NOTE for C6 (spec Decision Log #20): family C's WGSL is inspection-verified
 * only. It needs the f32 cross-check before it ships as a governor tier.
 */
export function rsupField(p: FieldParams, x: number, y: number): number {
  const l = cornerLocal(p, x, y);
  return l.rho + Math.min(l.m, 0) - cornerSupport(p, l.s2);
}

/**
 * Family D — `rsupn`. The v1 field.
 *
 * Branchless, and a line-for-line mirror of `sd_rsupn` in `src/wgsl.ts` — same
 * clamp, same Horner order — so the f32 cross-check compares the same
 * arithmetic rather than two dialects of it.
 */
export function rsupnField(p: FieldParams, x: number, y: number): number {
  const l = cornerLocal(p, x, y);
  const R = cornerSupport(p, l.s2);
  const dRdTheta = p.reach * l.s2 * hornerB(p.k, l.s2) * (2 * l.c2);
  const base = l.rho + Math.min(l.m, 0) - R;
  const g = dRdTheta * l.inv * l.rho;
  return base / Math.sqrt(1 + g * g);
}

export interface FieldSample {
  /** the field value */
  readonly value: number;
  /** analytic d/dx */
  readonly gx: number;
  /** analytic d/dy */
  readonly gy: number;
  /**
   * True where the field is genuinely not differentiable: the interior
   * medial-axis seams of the box branch, where `max(qx, qy)` switches. A normal
   * read there is meaningless — but it is also deep inside the shape, far
   * outside the optical band.
   */
  readonly kink: boolean;
}

/**
 * Family D's value and its EXACT gradient, in one pass and with no extra field
 * evaluations.
 *
 * This closes the decision S2 left open for C6. The alternatives it priced were
 * (a) central-differencing the normalized field, which costs four extra field
 * evaluations — roughly five times the field's cost — for <= 2.92 degrees, and
 * (b) the closed-form level-set normal of the UN-normalized field
 * (`rsupLevelSetNormal` below), which is free but <= 4.26 degrees off, because
 * the normalization moves the level sets away from the zero set. S2's note was
 * that the analytic gradient of the normalized field "needs no extra field
 * evaluations either, just more algebra than this shortcut" — this is that
 * algebra, so C6 gets the <= 2.92 degree bound at the free normal's price.
 *
 * The chain, in the corner sector (masks below extend it to every region):
 *
 *   ds2/dcx = -2*cy*c2*inv      ds2/dcy =  2*cx*c2*inv
 *   dc2/dcx =  2*cx*inv*(1-c2)  dc2/dcy = -2*cy*inv*(1+c2)
 *   d = base * n,  n = (1 + g^2)^(-1/2),  dn/dg = -g * n^3
 *
 * The `min(max(qx,qy), 0)` term contributes only inside the box branch, where it
 * carries the whole gradient.
 */
export function rsupnFieldAndGradient(p: FieldParams, x: number, y: number): FieldSample {
  const l = cornerLocal(p, x, y);
  const { cx, cy, qx, qy, rho, r2, inv, s2, c2 } = l;

  const A = hornerA(p.k, s2);
  const B = hornerB(p.k, s2);
  const C = hornerC(p.k, s2);

  const R = p.reach * (1 + s2 * s2 * A);
  const dRds2 = p.reach * s2 * B;
  const d2Rds2 = p.reach * C;
  const dRdTheta = dRds2 * (2 * c2);

  const mm = Math.min(l.m, 0);
  const base = rho + mm - R;
  const g = dRdTheta * inv * rho;
  // `norm` is spelled as a division rather than folded into `n` so that `value`
  // below is bit-identical to `rsupnField` — which is the function the WGSL
  // cross-check pins, so the two must not drift by even a last bit.
  const norm = Math.sqrt(1 + g * g);
  const n = 1 / norm;

  // partials of the intermediate quantities with respect to the CLAMPED corner
  // coordinates; the masks below decide whether they reach x and y at all.
  const ds2dcx = -2 * cy * c2 * inv;
  const ds2dcy = 2 * cx * c2 * inv;
  const dc2dcx = 2 * cx * inv * (1 - c2);
  const dc2dcy = -2 * cy * inv * (1 + c2);

  const drhodcx = cx / rho;
  const drhodcy = cy / rho;

  const dRdcx = dRds2 * ds2dcx;
  const dRdcy = dRds2 * ds2dcy;

  const dThetaTermdcx = 2 * (d2Rds2 * ds2dcx * c2 + dRds2 * dc2dcx);
  const dThetaTermdcy = 2 * (d2Rds2 * ds2dcy * c2 + dRds2 * dc2dcy);

  const dgdcx = dThetaTermdcx / rho - (dRdTheta * drhodcx) / r2;
  const dgdcy = dThetaTermdcy / rho - (dRdTheta * drhodcy) / r2;

  const dbasedcx = drhodcx - dRdcx;
  const dbasedcy = drhodcy - dRdcy;

  const n3 = n * n * n;
  const dddcx = dbasedcx * n + base * (-g * n3 * dgdcx);
  const dddcy = dbasedcy * n + base * (-g * n3 * dgdcy);

  // Masks. cx only responds to x where qx > 0; the box-branch term only bites
  // where max(qx, qy) < 0, and there it follows whichever component is larger.
  const mx = qx > 0 ? 1 : 0;
  const my = qy > 0 ? 1 : 0;
  // `m <= 0`, not `m < 0`. At `m == 0` — a point exactly on the corner-sector
  // boundary with the other component negative — the clamped-coordinate terms
  // are both masked off, so the box-branch term has to carry the whole
  // derivative or the gradient reads (0, 0). The field is genuinely C1 there
  // (both one-sided derivatives are 1), so exactly one of the two paths must
  // fire, and at `m == 0` it is this one.
  const inBox = l.m <= 0 ? 1 : 0;
  const dmmdqx = inBox && qx >= qy ? 1 : 0;
  const dmmdqy = inBox && qy > qx ? 1 : 0;

  const sx = x < 0 ? -1 : 1;
  const sy = y < 0 ? -1 : 1;

  return {
    value: base / norm,
    gx: (dddcx * mx + n * dmmdqx) * sx,
    gy: (dddcy * my + n * dmmdqy) * sy,
    // The box branch's two components tie on the interior diagonal seam. That
    // is a real C1 kink of the field, not a numerical artifact.
    kink: inBox === 1 && Math.abs(qx - qy) < 1e-9 * Math.max(1, Math.abs(qx)),
  };
}

/**
 * The free normal: the closed-form level-set normal of the UN-normalized
 * radial-support field, `normalize(rhoHat - (R'/rho) * thetaHat)`.
 *
 * Identical to the exact gradient ON the contour to four decimal places — the
 * normalization changes level sets only away from the zero set — so rim lighting
 * is indifferent between them, and the choice only affects refraction at depth,
 * where this is 1.5-1.7x worse (<= 4.26 degrees in the 8 px band). Carried
 * because it is family C's normal, and family C is the governor's first step:
 * taking this normal is taking family C's gradient while keeping family D's
 * values.
 */
export function rsupLevelSetNormal(p: FieldParams, x: number, y: number): Vec2 {
  const l = cornerLocal(p, x, y);
  const sx = x < 0 ? -1 : 1;
  const sy = y < 0 ? -1 : 1;

  if (l.cx <= 0 && l.cy <= 0) {
    return l.qx > l.qy ? [sx, 0] : [0, sy];
  }

  const dRdTheta = p.reach * l.s2 * hornerB(p.k, l.s2) * (2 * l.c2);
  const rhoHatX = l.cx / l.rho;
  const rhoHatY = l.cy / l.rho;
  const g = dRdTheta / l.rho;
  // thetaHat is rhoHat rotated a quarter turn: (-rhoHatY, rhoHatX).
  const nx = rhoHatX + g * rhoHatY;
  const ny = rhoHatY - g * rhoHatX;
  const len = Math.hypot(nx, ny);
  return [(sx * nx) / len, (sy * ny) / len];
}

/**
 * Central differences of a field, for tests and for anything that wants to
 * verify the analytic gradient. `kink` reports the one-sided differences
 * disagreeing materially, which is what a sample sitting on a C1 seam looks
 * like from the outside.
 */
export function centralGradient(
  field: (p: FieldParams, x: number, y: number) => number,
  p: FieldParams,
  x: number,
  y: number,
  h: number,
): { gx: number; gy: number; magnitude: number; kink: boolean } {
  const f0 = field(p, x, y);
  const fpx = field(p, x + h, y);
  const fmx = field(p, x - h, y);
  const fpy = field(p, x, y + h);
  const fmy = field(p, x, y - h);
  const gx = (fpx - fmx) / (2 * h);
  const gy = (fpy - fmy) / (2 * h);
  const kink =
    Math.abs((fpx - f0) / h - (f0 - fmx) / h) > 0.02 ||
    Math.abs((fpy - f0) / h - (f0 - fmy) / h) > 0.02;
  return { gx, gy, magnitude: Math.hypot(gx, gy), kink };
}
