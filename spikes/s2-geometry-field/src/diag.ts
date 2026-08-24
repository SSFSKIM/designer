/** Disclosure numbers for the findings doc: kink fractions and worst-case locations. */
import { rsupn } from './candidates.js';
import { FIGMA_TABLES } from './coefficients.js';
import { coeffAt, type FitRow } from './fit.js';
import { measure } from './metrics.js';
import { ASPECTS, R_FRACS, SIZES, SMOOTHINGS, specsFor } from './sweep.js';
import { cornerParams } from './contour.js';

const table: FitRow[] = FIGMA_TABLES['rsupn'].map((r) => ({
  sEff: r.sEff,
  coeff: r.coeff,
  contourDevPerR: r.devPerR,
}));

interface Hit {
  desc: string;
  v1: number;
  v8: number;
  g1: number;
  g8: number;
  kink1: number;
  kink8: number;
  at1: string;
}
const hits: Hit[] = [];

for (const size of SIZES)
  for (const a of ASPECTS)
    for (const rf of R_FRACS)
      for (const s of SMOOTHINGS) {
        const spec = specsFor(size, a, rf, s);
        const res = measure(rsupn, spec, coeffAt(table, cornerParams(spec).smoothingEff), {
          band: { halfBand: 8, offsets: 21, minPerCurve: 192, perPxStraight: 0.34 },
        });
        const b1 = res.bands.find((b) => b.half === 1)!;
        const b8 = res.bands.find((b) => b.half === 8)!;
        hits.push({
          desc: `size=${size} aspect=${a}:1 rFrac=${rf} s=${s} r=${res.r.toFixed(1)} sEff=${res.sEff.toFixed(3)}`,
          v1: b1.valueMax,
          v8: b8.valueMax,
          g1: b1.gradMaxDeg,
          g8: b8.gradMaxDeg,
          kink1: b1.kinkFraction,
          kink8: b8.kinkFraction,
          at1: `(${b1.worstAt.x.toFixed(1)},${b1.worstAt.y.toFixed(1)}) d=${b1.worstAt.d.toFixed(2)}`,
        });
      }

console.log('=== worst 6 by value error inside the RIM band |d| <= 1 px ===');
for (const h of [...hits].sort((x, y) => y.v1 - x.v1).slice(0, 6))
  console.log(`  ${h.v1.toFixed(4)}px  grad ${h.g1.toFixed(2)}deg  at ${h.at1}  | ${h.desc}`);

console.log('\n=== worst 6 by gradient error inside |d| <= 8 px ===');
for (const h of [...hits].sort((x, y) => y.g8 - x.g8).slice(0, 6))
  console.log(`  ${h.g8.toFixed(3)}deg  value ${h.v8.toFixed(4)}px  | ${h.desc}`);

console.log('\n=== highest C1-kink sample fractions (excluded from gradient stats) ===');
for (const h of [...hits].sort((x, y) => y.kink8 - x.kink8).slice(0, 6))
  console.log(
    `  |d|<=8: ${(h.kink8 * 100).toFixed(1)}%   |d|<=1: ${(h.kink1 * 100).toFixed(1)}%  | ${h.desc}`
  );

const nz = hits.filter((h) => h.kink8 > 0).length;
console.log(`\n${nz} of ${hits.length} shapes have any kink samples inside |d| <= 8.`);
