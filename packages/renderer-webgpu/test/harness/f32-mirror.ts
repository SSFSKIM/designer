/**
 * f32-emulated mirrors of `sd_rsupn` and `sd_rsup`, plus the check's point set.
 *
 * ## What this is for
 *
 * Decision Log #20 makes family C's shipping conditional on C6 running the f32
 * cross-check on its WGSL. The check has two halves, and this is the one that runs
 * everywhere:
 *
 *  - **Here (CPU):** every arithmetic operation of the shader, rounded to f32
 *    through `Math.fround`, against `@vitrea/geometry`'s f64 kernels. This answers
 *    "does single precision eat the error budget?" deterministically, on any
 *    machine, in the ordinary unit suite.
 *  - **`e2e/gpu/cross-check.spec.ts` (GPU):** the real shader on a real adapter,
 *    which is what S2 did for family D.
 *
 * ## Why both, honestly
 *
 * The emulation is not a substitute for the device run and the report says so. It
 * rounds after each operation, which is what IEEE 754 single precision with
 * round-to-nearest does — but a GPU may **fuse** a multiply and an add (one
 * rounding instead of two, so *more* accurate than this), and may implement
 * `inverseSqrt` and division with lower-precision approximations (so *less*
 * accurate). The emulation therefore brackets the question rather than settling
 * it: a large disagreement here would be a genuine precision problem, and a small
 * one leaves only hardware-specific instruction behaviour, which is what the
 * device run measures.
 *
 * The mirrors are transcribed from `wgsl/field.ts` line by line, in the same order,
 * because the check's value depends on both sides computing the same *sequence* of
 * operations and not merely the same function.
 */

import {
  type FieldParams,
  fieldParams,
  governorFieldParams,
  resolveShape,
  segmentNormal,
  segmentPoint,
  toContour,
} from "@vitrea/geometry";

const f = Math.fround;

/** `a * b` in f32. Separate rounding per operation — no fusing. */
const mul = (a: number, b: number): number => f(a * b);
const add = (a: number, b: number): number => f(a + b);
const sub = (a: number, b: number): number => f(a - b);
const div = (a: number, b: number): number => f(a / b);

/** Horner over `[k0..k4]` with per-term weights, in f32. */
function horner(k: readonly number[], s2: number, weight: (i: number) => number): number {
  let acc = f(weight(4) * (k[4] as number));
  for (let i = 3; i >= 0; i -= 1) {
    acc = add(mul(acc, s2), f(weight(i) * (k[i] as number)));
  }
  return acc;
}

/** `sd_rsupn`, f32-emulated. Mirrors `WGSL_RSUPN` operation for operation. */
export function rsupnF32(p: FieldParams, x: number, y: number): number {
  const halfW = f(p.halfW);
  const halfH = f(p.halfH);
  const re = f(p.reach);
  const k = p.k.map(f);

  const qx = add(sub(f(Math.abs(f(x))), halfW), re);
  const qy = add(sub(f(Math.abs(f(y))), halfH), re);
  const cx = Math.max(qx, 0);
  const cy = Math.max(qy, 0);
  const r2 = Math.max(add(mul(cx, cx), mul(cy, cy)), 1e-20);
  const inv = div(1, r2);
  const s2 = mul(mul(mul(f(2), cx), cy), inv);
  const c2 = mul(sub(mul(cx, cx), mul(cy, cy)), inv);

  const accA = horner(k, s2, () => 1);
  const R = mul(re, add(1, mul(mul(s2, s2), accA)));

  const accB = horner(k, s2, (i) => i + 2);
  const dRdt = mul(mul(mul(re, s2), accB), mul(f(2), c2));

  const base = sub(add(f(Math.sqrt(r2)), Math.min(Math.max(qx, qy), 0)), R);
  // the normalization's anchor: `select(dRdt / R, dRdt * inv * rho, rho >= R)`
  const rho = f(Math.sqrt(r2));
  const g = rho >= R ? mul(mul(dRdt, inv), rho) : div(dRdt, R);
  return mul(base, f(1 / Math.sqrt(add(1, mul(g, g)))));
}

/** `sd_rsup`, f32-emulated. Mirrors `WGSL_RSUP` operation for operation. */
export function rsupF32(p: FieldParams, x: number, y: number): number {
  const halfW = f(p.halfW);
  const halfH = f(p.halfH);
  const re = f(p.reach);
  const k = p.k.map(f);

  const qx = add(sub(f(Math.abs(f(x))), halfW), re);
  const qy = add(sub(f(Math.abs(f(y))), halfH), re);
  const cx = Math.max(qx, 0);
  const cy = Math.max(qy, 0);
  const r2 = Math.max(add(mul(cx, cx), mul(cy, cy)), 1e-20);
  const s2 = div(mul(mul(f(2), cx), cy), r2);

  const accA = horner(k, s2, () => 1);
  const R = mul(re, add(1, mul(mul(s2, s2), accA)));

  return sub(add(f(Math.sqrt(r2)), Math.min(Math.max(qx, qy), 0)), R);
}

/**
 * The check's shapes — the same three regimes S2's `make-f32-check.ts` used, one
 * per smoothing band, so the two runs are comparable.
 *
 * `W`/`H` are HALF-extents there, which is why the sizes below are doubled.
 */
export const CHECK_SPECS = [
  { halfW: 96, halfH: 24, radius: 8, smoothing: 0 },
  { halfW: 100, halfH: 100, radius: 28, smoothing: 0.5 },
  { halfW: 320, halfH: 180, radius: 48, smoothing: 1 },
] as const;

/** Contour-relative offsets, in units of the radius. S2's set. */
const DELTAS = [-1.5, -0.5, -0.1, -0.01, 0, 0.01, 0.1, 0.5, 1.5];
const T_STEPS = 12;
const GRID = 17;

export interface CheckShape {
  readonly rsupn: FieldParams;
  readonly rsup: FieldParams;
  readonly radius: number;
}

export interface CheckPoint {
  readonly shape: number;
  readonly x: number;
  readonly y: number;
}

export interface CheckSet {
  readonly shapes: readonly CheckShape[];
  readonly points: readonly CheckPoint[];
}

/**
 * Points on and around the true contour of each shape, plus a coarse grid over the
 * first quadrant and a margin.
 *
 * Dense near the contour because that is where the corner sector's arithmetic
 * lives and where a precision loss would land inside the optical band; the grid
 * covers the straight-edge and deep-interior branches, which take different paths
 * through the clamp.
 */
export function buildCheckSet(): CheckSet {
  const shapes: CheckShape[] = [];
  const points: CheckPoint[] = [];

  for (const spec of CHECK_SPECS) {
    const shape = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [spec.halfW * 2, spec.halfH * 2],
      radii: spec.radius,
      profile: spec.smoothing,
      thickness: 0,
    });
    const index = shapes.length;
    shapes.push({
      rsupn: fieldParams(shape),
      rsup: governorFieldParams(shape),
      radius: shape.corner.radius,
    });

    const push = (x: number, y: number): void => {
      if (!Number.isFinite(x) || !Number.isFinite(y)) return;
      points.push({ shape: index, x, y });
    };

    for (const segment of toContour(shape).segments) {
      for (let i = 0; i <= T_STEPS; i += 1) {
        const t = i / T_STEPS;
        const q = segmentPoint(segment, t);
        const n = segmentNormal(segment, t);
        if (n.x === 0 && n.y === 0) continue;
        for (const delta of DELTAS) {
          push(q.x + n.x * delta * spec.radius, q.y + n.y * delta * spec.radius);
        }
      }
    }

    for (let i = 0; i <= GRID; i += 1) {
      for (let j = 0; j <= GRID; j += 1) {
        push(
          (i / GRID) * (spec.halfW + 2 * spec.radius),
          (j / GRID) * (spec.halfH + 2 * spec.radius),
        );
      }
    }
  }

  return { shapes, points };
}

export interface CheckStats {
  readonly n: number;
  readonly maxAbsDiff: number;
  readonly p99AbsDiff: number;
  readonly meanAbsDiff: number;
  readonly maxRelativeToReach: number;
}

export function summarise(
  diffs: readonly number[],
  reaches: readonly number[],
): CheckStats {
  const sorted = [...diffs].sort((a, b) => a - b);
  const quantile = (q: number): number =>
    sorted[Math.min(sorted.length - 1, Math.max(0, Math.round(q * (sorted.length - 1))))] ?? 0;

  let max = 0;
  let sum = 0;
  let maxRelative = 0;
  for (let i = 0; i < diffs.length; i += 1) {
    const d = diffs[i] ?? 0;
    sum += d;
    if (d > max) max = d;
    const reach = reaches[i] ?? 0;
    if (reach > 0) maxRelative = Math.max(maxRelative, d / reach);
  }

  return {
    n: diffs.length,
    maxAbsDiff: max,
    p99AbsDiff: quantile(0.99),
    meanAbsDiff: diffs.length === 0 ? 0 : sum / diffs.length,
    maxRelativeToReach: maxRelative,
  };
}
