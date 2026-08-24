/**
 * Emits the shader-cost markdown tables straight from bench/results.json, so the
 * findings document cites the committed measurement rather than a hand
 * transcription of it. Run with `npx tsx bench/report-cost.ts`.
 */

import { readFileSync } from 'node:fs';

interface Fit {
  slopeMsPerDrawPerEval: number;
  interceptMsPerDraw: number;
  r2: number;
  nsPerEvalPerPixel: number;
  ratioK32toK1: number;
  marginalShareAtMaxK: number;
  scalesWithK: boolean;
}
interface Variant {
  id: string;
  label: string;
  fit: Fit;
}
interface Resolution {
  label: string;
  width: number;
  height: number;
  pixels: number;
  variants: Variant[];
}

const file = process.argv[2] ?? new URL('./results.json', import.meta.url).pathname;
const d = JSON.parse(readFileSync(file, 'utf8')) as {
  generatedAt: string;
  resolutions: Resolution[];
  meta: { timingMethods: string[]; adapter: Record<string, string> };
  f32Check: { points: number; shapes: number; perCandidate: Record<string, Record<string, number>> };
};

/** The scene the spec pins: 8 surfaces, 3 groups. */
const SURFACES = 8;
const BUDGET_MS = 2;
/** Fraction of the frame a scoped set of per-group field passes plausibly covers. */
const SCOPED = 0.15;

const NAMES: Record<string, string> = {
  null: '`null` (loop + storage load only)',
  roundbox: 'A `roundbox`',
  rsup: 'C `rsup`',
  rsupn: '**D `rsupn`**',
  superell: 'B `superell`',
};
const ORDER = ['null', 'roundbox', 'rsup', 'rsupn', 'superell'];

const res = d.resolutions;
const get = (r: Resolution, id: string) => r.variants.find((v) => v.id === id);
const ids = ORDER.filter((id) => res.every((r) => get(r, id)));
const nullNs = (r: Resolution) => get(r, 'null')!.fit.nsPerEvalPerPixel;

const out: string[] = [];
const p = (s = '') => out.push(s);

p('### Cost per field evaluation per pixel');
p();
p(`| variant | ${res.map((r) => `${r.label.startsWith('mobile') ? 'mobile' : 'desktop'} ${r.width}×${r.height}`).join(' | net of loop | ')} | net of loop |`);
p(`| --- | ${res.map(() => '--- | ---').join(' | ')} |`);
for (const id of ids) {
  const cells: string[] = [];
  for (const r of res) {
    const ns = get(r, id)!.fit.nsPerEvalPerPixel;
    cells.push(`${ns.toFixed(5)} ns`);
    cells.push(id === 'null' ? '—' : `${(ns - nullNs(r)).toFixed(5)} ns`);
  }
  p(`| ${NAMES[id] ?? id} | ${cells.join(' | ')} |`);
}
p();
p('### One full-screen field pass, one evaluation per pixel');
p();
p(`| variant | ${res.map((r) => `${r.label.startsWith('mobile') ? 'mobile' : 'desktop'} (${(r.pixels / 1e6).toFixed(2)} Mpx)`).join(' | ')} |`);
p(`| --- | ${res.map(() => '---').join(' | ')} |`);
for (const id of ids) {
  if (id === 'null') continue;
  p(
    `| ${NAMES[id] ?? id} | ${res
      .map((r) => `${get(r, id)!.fit.slopeMsPerDrawPerEval.toFixed(4)} ms`)
      .join(' | ')} |`
  );
}
p();
p(`### Against the spec's benchmark scenes and the ~${BUDGET_MS} ms GPU budget`);
p();
p(`| | ${res.map((r) => `${r.label.startsWith('mobile') ? 'mobile' : 'desktop'}, share of ${BUDGET_MS} ms`).join(' | ')} |`);
p(`| --- | ${res.map(() => '---').join(' | ')} |`);
const scene = (id: string, frac: number) =>
  res
    .map((r) => {
      const ms = get(r, id)!.fit.slopeMsPerDrawPerEval * SURFACES * frac;
      return `${ms.toFixed(3)} ms — **${((ms / BUDGET_MS) * 100).toFixed(0)}%**`;
    })
    .join(' | ');
p(`| **Pessimistic** — all ${SURFACES} surfaces evaluated at *every* pixel of the frame | ${scene('rsupn', 1)} |`);
for (const id of ids) {
  if (id === 'null' || id === 'rsupn') continue;
  p(`| ${NAMES[id] ?? id}, same pessimistic bound | ${scene(id, 1)} |`);
}
p(`| **Scoped** — field passes covering ~${SCOPED * 100}% of the frame in total | ${scene('rsupn', SCOPED)} |`);
p();

const netRatio = res.map((r) => {
  const a = get(r, 'roundbox')!.fit.nsPerEvalPerPixel - nullNs(r);
  const dd = get(r, 'rsupn')!.fit.nsPerEvalPerPixel - nullNs(r);
  return dd / a;
});
p(
  `Family D costs ${netRatio.map((x) => x.toFixed(1)).join('x and ')}x family A's net field ` +
    `arithmetic across the two resolutions.`
);
p();
p('### f32 precision');
p();
p(`| candidate | max abs diff | p99 | p50 | max relative to corner reach |`);
p('| --- | --- | --- | --- | --- |');
for (const [k, v] of Object.entries(d.f32Check.perCandidate)) {
  p(
    `| ${NAMES[k] ?? k} | ${v.maxAbsDiff.toExponential(2)} px | ${v.p99AbsDiff.toExponential(2)} px | ` +
      `${v.p50AbsDiff.toExponential(2)} px | ${v.maxAbsDiffRelativeToRe.toExponential(2)} |`
  );
}
p();
p(
  `Source: \`bench/results.json\`, generated ${d.generatedAt}, timing method ` +
    `${d.meta.timingMethods.join(' + ')}, adapter ${d.meta.adapter.vendor}/${d.meta.adapter.architecture}. ` +
    `f32 check over ${d.f32Check.points} points on ${d.f32Check.shapes} shapes.`
);

console.log(out.join('\n'));
