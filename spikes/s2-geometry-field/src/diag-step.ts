/**
 * Is the reported gradient error a property of the field, or of the
 * finite-difference step used to measure it?
 *
 * The field has a C2 break where the corner sector's max(q, 0) clamp engages, so
 * a central difference straddling that seam could inflate the figure. Sweeping
 * the step over two orders of magnitude settles it: if the numbers are stable,
 * the measurement is reading the field and not itself.
 */
import { rsupn } from './candidates.js';
import { FIGMA_TABLES } from './coefficients.js';
import { coeffAt, type FitRow } from './fit.js';
import { measure } from './metrics.js';
import { specsFor } from './sweep.js';
import { cornerParams } from './contour.js';

const table: FitRow[] = FIGMA_TABLES['rsupn'].map((r) => ({
  sEff: r.sEff,
  coeff: r.coeff,
  contourDevPerR: r.devPerR,
}));

const CASES = [
  specsFor(16, 1, 0.15, 1.0), // sets the gradient bound
  specsFor(600, 8, 0.3, 0.8), // sets the value bound
  specsFor(64, 1, 0.15, 0.6),
];

console.log('gradStepFrac | ' + CASES.map((_, i) => `case${i} val@8   grad@8`).join(' | '));
for (const frac of [1e-2, 1e-3, 1e-4, 1e-5, 1e-6]) {
  const cells = CASES.map((spec) => {
    const res = measure(rsupn, spec, coeffAt(table, cornerParams(spec).smoothingEff), {
      gradStepFrac: frac,
      band: { halfBand: 8, offsets: 21, minPerCurve: 192, perPxStraight: 0.34 },
    });
    const b = res.bands.find((x) => x.half === 8)!;
    return `${b.valueMax.toFixed(4)}  ${b.gradMaxDeg.toFixed(4)}`;
  });
  console.log(`${frac.toExponential(0).padStart(12)} | ${cells.join(' | ')}`);
}
