/**
 * Which normal should C6 actually ship?
 *
 * The gradient bound in the findings is measured by central-differencing the
 * NORMALIZED field. A shader would rather not pay four extra field evaluations,
 * so the obvious shortcut is the closed-form level-set normal of the
 * UNNORMALIZED radial-support field:
 *
 *   normalize(rhoHat - (R'/rho) * thetaHat)
 *
 * with rhoHat the normalized clamped corner vector, thetaHat its perpendicular,
 * and R' = dR/dtheta -- a quantity the field already computes for its
 * normalization term, so the normal costs essentially nothing.
 *
 * This script prices that shortcut. It turns out to be exactly as good ON the
 * contour and materially worse off it, because the normalization changes the
 * level sets away from the zero set -- which is the whole reason family D beats
 * family C. Run it before deciding; do not assume either way.
 */

import { fieldGradient, rsupn, RSUP_NK } from './candidates.js';
import { FIGMA_TABLES } from './coefficients.js';
import { coeffAt, type FitRow } from './fit.js';
import { buildContour, cornerParams } from './contour.js';
import { angleDeg, DEFAULT_BAND, sampleBand } from './truth.js';
import { ASPECTS, R_FRACS, SIZES, SMOOTHINGS, specsFor } from './sweep.js';

const table: FitRow[] = FIGMA_TABLES['rsupn'].map((r) => ({
  sEff: r.sEff,
  coeff: r.coeff,
  contourDevPerR: r.devPerR,
}));

/** The closed form, written the way a shader would. */
function analyticNormal(
  prep: { W: number; H: number; re: number; k: number[] },
  x: number,
  y: number
): { x: number; y: number } {
  const sx = Math.sign(x) || 1;
  const sy = Math.sign(y) || 1;
  const qx = Math.abs(x) - (prep.W - prep.re);
  const qy = Math.abs(y) - (prep.H - prep.re);
  const cx = Math.max(qx, 0);
  const cy = Math.max(qy, 0);
  const r2 = Math.max(cx * cx + cy * cy, 1e-20);
  const rho = Math.sqrt(r2);
  if (cx <= 0 && cy <= 0) return qx > qy ? { x: sx, y: 0 } : { x: 0, y: sy };
  const inv = 1 / r2;
  const s2 = 2 * cx * cy * inv;
  const c2 = (cx * cx - cy * cy) * inv;
  let dacc = (RSUP_NK + 1) * prep.k[RSUP_NK - 1];
  for (let i = RSUP_NK - 2; i >= 0; i--) dacc = dacc * s2 + (i + 2) * prep.k[i];
  const dRdt = prep.re * s2 * dacc * (2 * c2);
  const rhoHat = { x: cx / rho, y: cy / rho };
  const g = dRdt / rho;
  const nx = rhoHat.x - g * -rhoHat.y;
  const ny = rhoHat.y - g * rhoHat.x;
  const l = Math.hypot(nx, ny);
  return { x: (sx * nx) / l, y: (sy * ny) / l };
}

const BANDS = [1, 4, 8];
const pct = (a: number[], q: number) =>
  a.length === 0 ? 0 : a[Math.min(a.length - 1, Math.max(0, Math.ceil(q * a.length) - 1))];

const acc: Record<string, { a: number[]; f: number[] }> = {};
for (const h of BANDS) acc[h] = { a: [], f: [] };
const worst: Record<string, { a: number; f: number }> = {};
for (const h of BANDS) worst[h] = { a: 0, f: 0 };

for (const size of SIZES)
  for (const aspect of ASPECTS)
    for (const rf of R_FRACS)
      for (const s of SMOOTHINGS) {
        const spec = specsFor(size, aspect, rf, s);
        const prep = rsupn.prepare(spec, coeffAt(table, cornerParams(spec).smoothingEff));
        const contour = buildContour(spec);
        const step = Math.max(1e-6, 1e-3 * Math.max(contour.params.r, 1));
        for (const smp of sampleBand(contour, {
          ...DEFAULT_BAND,
          offsets: 17,
          minPerCurve: 160,
          perPxStraight: 0.34,
        })) {
          const g = fieldGradient(rsupn, prep, smp.P.x, smp.P.y, step);
          if (g.kink) continue;
          const ae = angleDeg(analyticNormal(prep, smp.P.x, smp.P.y), smp.grad);
          const fe = angleDeg({ x: g.gx, y: g.gy }, smp.grad);
          for (const h of BANDS) {
            if (Math.abs(smp.d) <= h + 1e-12) {
              acc[h].a.push(ae);
              acc[h].f.push(fe);
              worst[h].a = Math.max(worst[h].a, ae);
              worst[h].f = Math.max(worst[h].f, fe);
            }
          }
        }
      }

console.log('Full matrix, family D. Gradient direction error, degrees.\n');
console.log('| band | closed form max | closed form p95 | normalized-field max | normalized-field p95 |');
console.log('| --- | --- | --- | --- | --- |');
for (const h of BANDS) {
  const a = acc[h].a.sort((x, y) => x - y);
  const f = acc[h].f.sort((x, y) => x - y);
  console.log(
    `| \\|d\\| <= ${h} px | ${worst[h].a.toFixed(3)} | ${pct(a, 0.95).toFixed(3)} | ` +
      `${worst[h].f.toFixed(3)} | ${pct(f, 0.95).toFixed(3)} |`
  );
}
