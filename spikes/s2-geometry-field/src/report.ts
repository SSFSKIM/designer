/**
 * Emits the markdown tables for the S2 findings document. Run with
 * `npm run report` (add `--quick` for a reduced matrix while iterating).
 *
 * Reads the committed coefficient table; it does not refit. Run `npm run fit`
 * first if the families changed.
 */

import {
  APPLE_BEST_FIGMA_SMOOTHING,
  APPLE_TABLES,
  FIGMA_TABLES,
  RSUP_NK_GENERATED,
} from './coefficients.js';
import { CANDIDATES, RSUP_NK } from './candidates.js';
import type { FitRow } from './fit.js';
import { agg, ASPECTS, R_FRACS, SIZES, SMOOTHINGS, specsFor, sweep, type Row } from './sweep.js';
import { buildContour, contourCurvatureBreaks, contourTangentBreak, cornerParams } from './contour.js';
import { APPLE_REACH, buildAppleContour } from './apple.js';
import { figmaVsApple } from './reference.js';
import { buildAppleReferenceRows } from './apple-sweep.js';

const QUICK = process.argv.includes('--quick');
const tables: Record<string, FitRow[]> = {};
for (const [id, rows] of Object.entries(FIGMA_TABLES)) {
  tables[id] = rows.map((r) => ({ sEff: r.sEff, coeff: r.coeff, contourDevPerR: r.devPerR }));
}

const out: string[] = [];
const p = (s = '') => out.push(s);
const f = (x: number, d = 4) => x.toFixed(d);
const e = (x: number) => x.toExponential(3);

// ---------------------------------------------------------------------------
p('## A. Reference contour characterization');
p();
p('Figma family (the spec\'s seeded reference), radius r, uncapped:');
p();
p('| smoothing | reach p/r | arc sweep (deg) | max tangent break (deg) | max curvature break (x r) |');
p('| --- | --- | --- | --- | --- |');
for (const s of SMOOTHINGS) {
  const spec = { W: 64, H: 64, r: 1, smoothing: s };
  const c = buildContour(spec);
  const cp = cornerParams(spec);
  p(
    `| ${f(s, 2)} | ${f(cp.p, 4)} | ${f((cp.arcMeasure * 180) / Math.PI, 2)} | ` +
      `${e((contourTangentBreak(c) * 180) / Math.PI)} | ${f(Math.max(...contourCurvatureBreaks(c, 1)), 4)} |`
  );
}
p();
const ac = buildAppleContour({ W: 64, H: 64, r: 1, smoothing: 0 });
p(
  `Apple \`.continuous\` (verified from a macOS 26 CGPath dump; reach is Apple's own ` +
    `published \`cornerCurveExpansionFactor\`):`
);
p();
p(`- reach p/r = ${APPLE_REACH}`);
p(`- three cubics per corner; the middle one is a circular arc, r_arc = 0.931253 r, sweep 50.0000 deg`);
p(`- max tangent break = ${f((contourTangentBreak(ac) * 180) / Math.PI, 4)} deg (at both shoulder/arc joins)`);
p(`- max curvature break x r = ${f(Math.max(...contourCurvatureBreaks(ac, 1)), 4)}`);
p(`- G2 (zero curvature) where the corner meets the straight edge`);
p(`- radius saturates at r/side = ${f(1 / (2 * APPLE_REACH), 6)}`);
p();

// ---------------------------------------------------------------------------
p('## B. How far the reference is from Apple');
p();
p('Two-sided Hausdorff distance between Figma(smoothing) and Apple, in units of r:');
p();
p('| Figma smoothing | Hausdorff / r |');
p('| --- | --- |');
for (const s of [0, 0.2, 0.4, 0.6, 0.66, 0.8, 1.0]) {
  p(`| ${f(s, 2)} | ${e(figmaVsApple(s, 1, 1, QUICK ? 300 : 800))} |`);
}
p();
p(
  `Best match: smoothing = **${APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing}**, ` +
    `Hausdorff = **${e(APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.hausdorffPerR)} r**. ` +
    `With the radius free: smoothing ${f(APPLE_BEST_FIGMA_SMOOTHING.radiusFree.smoothing, 4)}, ` +
    `radius scale ${f(APPLE_BEST_FIGMA_SMOOTHING.radiusFree.radiusScale, 4)}, ` +
    `Hausdorff ${e(APPLE_BEST_FIGMA_SMOOTHING.radiusFree.hausdorffPerR)} r.`
);
p();

// ---------------------------------------------------------------------------
p('## C. Contour deviation of each candidate family (scale-free)');
p();
p(`Max |field| on the true contour, in units of r. RSUP_NK = ${RSUP_NK_GENERATED}.`);
p();
p('| smoothing | A roundbox | B superell | C rsup | D rsupn |');
p('| --- | --- | --- | --- | --- |');
for (const s of SMOOTHINGS) {
  const cells = ['roundbox', 'superell', 'rsup', 'rsupn'].map((id) => {
    const row = FIGMA_TABLES[id].find((r) => Math.abs(r.sEff - s) < 1e-9);
    return row ? e(row.devPerR) : '-';
  });
  p(`| ${f(s, 2)} | ${cells.join(' | ')} |`);
}
p();
p('Worst over the whole smoothing grid:');
p();
p('| family | worst dev / r | at smoothing | px at r=40 | px at r=150 |');
p('| --- | --- | --- | --- | --- |');
for (const id of ['roundbox', 'superell', 'rsup', 'rsupn']) {
  let w = 0;
  let ws = 0;
  for (const r of FIGMA_TABLES[id]) {
    if (r.devPerR > w) {
      w = r.devPerR;
      ws = r.sEff;
    }
  }
  p(`| ${id} | ${e(w)} | ${f(ws, 2)} | ${f(w * 40, 4)} | ${f(w * 150, 4)} |`);
}
p();
p('Fit directly to Apple\'s corner instead (single coefficient set, no smoothing axis):');
p();
p('| family | dev / r | px at r=40 | px at r=150 |');
p('| --- | --- | --- | --- |');
for (const id of ['rsup', 'rsupn']) {
  const a = APPLE_TABLES[id];
  p(`| ${id} | ${e(a.devPerR)} | ${f(a.devPerR * 40, 4)} | ${f(a.devPerR * 150, 4)} |`);
}
p();

// ---------------------------------------------------------------------------
p('## D. Band error over the required matrix');
p();
const specs = QUICK
  ? SMOOTHINGS.flatMap((s) => [specsFor(64, 1, 0.15, s), specsFor(320, 3, 0.3, s), specsFor(32, 8, 0.5, s)])
  : undefined;
const rows: Row[] = sweep(tables, CANDIDATES, specs);
p(
  `Matrix: smoothing ${JSON.stringify(SMOOTHINGS)} x size ${JSON.stringify(SIZES)} x aspect ` +
    `${JSON.stringify(ASPECTS)} x radius fraction ${JSON.stringify(R_FRACS)} of the short side ` +
    `= ${rows.length / CANDIDATES.length} shapes${QUICK ? ' (QUICK subset)' : ''}.`
);
p();
p('Aggregated as the worst over every shape in the matrix. `p95` is the worst shape\'s p95,');
p('measured over contour-uniform x offset-uniform samples inside the band.');
p();
for (const half of [1, 4, 8]) {
  p(`Band |d| <= ${half} px:`);
  p();
  p('| family | value max (px) | value p95 (px) | grad max (deg) | grad p95 (deg) | max \\|grad\\|-1 |');
  p('| --- | --- | --- | --- | --- | --- |');
  for (const c of CANDIDATES) {
    const a = agg(
      rows.filter((r) => r.candId === c.id),
      half
    );
    p(
      `| ${c.id} | ${f(a.valueMax)} | ${f(a.valueP95)} | ${f(a.gradMaxDeg, 3)} | ` +
        `${f(a.gradP95Deg, 3)} | ${f(a.eikonalMax, 4)} |`
    );
  }
  p();
}

// ---------------------------------------------------------------------------
p('### D1. Recommended family (D rsupn), broken out by requested smoothing');
p();
p('| smoothing | shapes | value max (px) | value p95 (px) | grad max (deg) | grad p95 (deg) |');
p('| --- | --- | --- | --- | --- | --- |');
for (const s of SMOOTHINGS) {
  const sub = rows.filter((r) => r.candId === 'rsupn' && Math.abs(r.requested - s) < 1e-9);
  const a = agg(sub, 8);
  p(
    `| ${f(s, 2)} | ${sub.length} | ${f(a.valueMax)} | ${f(a.valueP95)} | ` +
      `${f(a.gradMaxDeg, 3)} | ${f(a.gradP95Deg, 3)} |`
  );
}
p();
p('### D2. Recommended family, broken out by size (short side)');
p();
p('| size px | shapes | max radius px | value max (px) | grad max (deg) |');
p('| --- | --- | --- | --- | --- |');
for (const size of SIZES) {
  const sub = rows.filter((r) => r.candId === 'rsupn' && r.size === size);
  if (sub.length === 0) continue;
  const a = agg(sub, 8);
  p(
    `| ${size} | ${sub.length} | ${f(Math.max(...sub.map((x) => x.r)), 1)} | ` +
      `${f(a.valueMax)} | ${f(a.gradMaxDeg, 3)} |`
  );
}
p();
p('### D3. Error scales linearly with the corner radius');
p();
p(
  'Aspect 1:1, radius fraction 0.15 of the short side (so the budget never clamps), requested ' +
    'smoothing 0.8. Value max divided by r is constant except where the fixed 8 px band stops ' +
    'being small relative to r -- which is exactly why the band error does NOT grow without ' +
    'bound as shapes get larger.'
);
p();
p('| size px | r px | s_eff | value max (px) | value max / r | grad max (deg) |');
p('| --- | --- | --- | --- | --- | --- |');
for (const size of SIZES) {
  const sub = rows.filter(
    (r) =>
      r.candId === 'rsupn' &&
      r.size === size &&
      r.aspect === 1 &&
      Math.abs(r.rFrac - 0.15) < 1e-9 &&
      Math.abs(r.requested - 0.8) < 1e-9
  );
  for (const s of sub) {
    const b = s.bands.find((x) => x.half === 8)!;
    p(
      `| ${size} | ${f(s.r, 2)} | ${f(s.sEff, 3)} | ${f(b.valueMax)} | ${e(b.valueMax / s.r)} | ${f(b.gradMaxDeg, 3)} |`
    );
  }
}
p();

// ---------------------------------------------------------------------------
p('### D4. Capsule limit');
p();
p(
  'At the capsule limit the requested radius equals the budget, so Figma clamps effective ' +
    'smoothing to 0 and the shape is an exact stadium. Every family is then exact to machine ' +
    'precision -- the capsule is not an approximation at all.'
);
p();
p('| family | requested smoothing | s_eff | value max (px) | grad max (deg) |');
p('| --- | --- | --- | --- | --- |');
for (const c of CANDIDATES) {
  const sub = rows.filter((r) => r.candId === c.id && Math.abs(r.rFrac - 0.5) < 1e-9);
  if (sub.length === 0) continue;
  const a = agg(sub, 8);
  p(
    `| ${c.id} | 0..1 (all) | ${f(Math.max(...sub.map((x) => x.sEff)), 6)} | ` +
      `${e(a.valueMax)} | ${e(a.gradMaxDeg)} |`
  );
}
p();

// ---------------------------------------------------------------------------
p('### D5. Measured against Apple\'s corner instead of Figma\'s');
p();
const appleRows = buildAppleReferenceRows(QUICK);
p('| field fit target | value max (px) | value p95 (px) | grad max (deg) | grad p95 (deg) |');
p('| --- | --- | --- | --- | --- |');
for (const r of appleRows) {
  p(
    `| ${r.label} | ${f(r.valueMax)} | ${f(r.valueP95)} | ${f(r.gradMaxDeg, 3)} | ${f(r.gradP95Deg, 3)} |`
  );
}
p();

// ---------------------------------------------------------------------------
p('## E. Shipping coefficient table (family D, fit against Figma)');
p();
p(`RSUP_NK = ${RSUP_NK}; corner offset re = p = (1 + s_eff) * r, derived CPU-side.`);
p();
p('| s_eff | k0 | k1 | k2 | k3 | k4 | dev/r |');
p('| --- | --- | --- | --- | --- | --- | --- |');
for (const r of FIGMA_TABLES['rsupn']) {
  p(`| ${f(r.sEff, 2)} | ${r.coeff.map((c) => f(c, 5)).join(' | ')} | ${e(r.devPerR)} |`);
}
p();
p('Apple-direct coefficients (family D): `[' + APPLE_TABLES['rsupn'].coeff.join(', ') + ']`');
p();
console.log(out.join('\n'));
