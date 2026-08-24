/**
 * Band error measured against APPLE's corner rather than Figma's, for three
 * field configurations:
 *
 *   1. family D fit to Apple directly              -- what a fidelity-first
 *                                                     renderer would actually ship
 *   2. family D fit to Figma at its best-matching smoothing (0.66)
 *                                                  -- the spec's current path
 *   3. family A (plain rounded box) at its best radius
 *                                                  -- what a naive shader does
 *
 * This is the comparison that decides whether the pseudo-SDF or the choice of
 * reference family is the binding constraint on fidelity.
 */

import { APPLE_REACH, buildAppleContour } from './apple.js';
import { APPLE_TABLES, FIGMA_TABLES } from './coefficients.js';
import { rsupn, roundbox, type Candidate, type Prepared } from './candidates.js';
import { cornerParams, type ShapeSpec } from './contour.js';
import { angleDeg, DEFAULT_BAND, sampleBand } from './truth.js';
import { fieldGradient } from './candidates.js';

export interface AppleRow {
  label: string;
  valueMax: number;
  valueP95: number;
  gradMaxDeg: number;
  gradP95Deg: number;
}

function measureAgainstApple(
  label: string,
  cand: Candidate,
  prep: Prepared,
  spec: ShapeSpec,
  gradStep: number
): AppleRow {
  const contour = buildAppleContour(spec);
  const samples = sampleBand(contour, { ...DEFAULT_BAND, offsets: 21, minPerCurve: 256 });
  const ve: number[] = [];
  const ge: number[] = [];
  for (const s of samples) {
    ve.push(Math.abs(cand.evalAt(prep, s.P.x, s.P.y) - s.d));
    const g = fieldGradient(cand, prep, s.P.x, s.P.y, gradStep);
    if (!g.kink) ge.push(angleDeg({ x: g.gx, y: g.gy }, s.grad));
  }
  ve.sort((a, b) => a - b);
  ge.sort((a, b) => a - b);
  const pct = (arr: number[], q: number) =>
    arr.length === 0 ? 0 : arr[Math.min(arr.length - 1, Math.max(0, Math.ceil(q * arr.length) - 1))];
  return {
    label,
    valueMax: ve[ve.length - 1] ?? 0,
    valueP95: pct(ve, 0.95),
    gradMaxDeg: ge[ge.length - 1] ?? 0,
    gradP95Deg: pct(ge, 0.95),
  };
}

/** Sizes chosen so the Apple radius never saturates (r/side < 0.3271). */
const CASES: { size: number; aspect: number; r: number }[] = [
  { size: 64, aspect: 1, r: 12 },
  { size: 120, aspect: 3, r: 24 },
  { size: 600, aspect: 1, r: 150 },
];

export function buildAppleReferenceRows(quick = false): AppleRow[] {
  const cases = quick ? CASES.slice(0, 1) : CASES;
  const acc: Record<string, AppleRow> = {};

  for (const cs of cases) {
    const spec: ShapeSpec = { W: (cs.size * cs.aspect) / 2, H: cs.size / 2, r: cs.r, smoothing: 0 };
    const h = Math.max(1e-6, 1e-3 * Math.max(cs.r, 1));
    const appleReach = APPLE_REACH * cs.r;

    const variants: { label: string; cand: Candidate; prep: Prepared }[] = [
      {
        label: 'D rsupn, fit to Apple directly',
        cand: rsupn,
        prep: rsupn.prepare(spec, APPLE_TABLES['rsupn'].coeff, appleReach),
      },
      {
        label: 'D rsupn, fit to Figma at smoothing 0.66',
        cand: rsupn,
        // The Figma-fitted coefficients assume re = (1 + s) * r; use Figma's own
        // reach so this measures the reference-family gap, not a mismatched offset.
        prep: rsupn.prepare(
          { ...spec, smoothing: 0.66 },
          nearestFigmaCoeff('rsupn', 0.66),
          cornerParams({ ...spec, smoothing: 0.66 }).p
        ),
      },
      {
        label: 'A roundbox, best radius scale',
        cand: roundbox,
        prep: roundbox.prepare(spec, [1.0]),
      },
    ];

    for (const v of variants) {
      const r = measureAgainstApple(v.label, v.cand, v.prep, spec, h);
      const prev = acc[v.label];
      acc[v.label] = prev
        ? {
            label: v.label,
            valueMax: Math.max(prev.valueMax, r.valueMax),
            valueP95: Math.max(prev.valueP95, r.valueP95),
            gradMaxDeg: Math.max(prev.gradMaxDeg, r.gradMaxDeg),
            gradP95Deg: Math.max(prev.gradP95Deg, r.gradP95Deg),
          }
        : r;
    }
  }
  return Object.values(acc);
}

function nearestFigmaCoeff(id: string, sEff: number): number[] {
  const rows = FIGMA_TABLES[id];
  let best = rows[0];
  for (const r of rows) if (Math.abs(r.sEff - sEff) < Math.abs(best.sEff - sEff)) best = r;
  return best.coeff;
}
