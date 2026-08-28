// Renders results/results.json as the markdown tables in REPORT.md.
//   node harness/table.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const { version, rows } = JSON.parse(readFileSync(join(ROOT, 'results', 'results.json'), 'utf8'));

const cell = (c, k) => (c && c[k] ? `${c[k].mean} / ${c[k].p99} / ${c[k].max}` : '—');

console.log(`Chromium ${version}. Every number is mean / p99 / max of the per-pixel maximum`);
console.log('absolute per-channel difference, 0–255.\n');

const groups = new Map();
for (const row of rows) {
  const g = row.label.split('/').slice(0, 2).join('/');
  if (!groups.has(g)) groups.set(g, []);
  groups.get(g).push(row);
}

for (const [g, list] of groups) {
  console.log(`\n#### \`${g}\` — σ = ${list[0].sigma}, padding ${list[0].pad}\n`);
  console.log('| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |');
  console.log('| --- | --- | --- | --- | --- | --- | --- | --- |');
  for (const r of list) {
    const s = r['split-ab vs single'];
    const o = r['split-ab vs split-ba'];
    const note = r.repro ? ' ¹' : r.demo ? ' ²' : '';
    console.log(
      `| ${r.mult}σ${note} | ${r.gap}px | ${r.boxesOverlap ? 'yes' : 'no'} | ${r.paintReachesNeighbour ? 'yes' : 'no'} | ` +
      `${cell(s, 'B_inner_core')} | ${cell(o, 'B_inner_core')} | ${cell(s, 'A_inner_core')} | ${cell(s, 'B_all')} |`,
    );
  }
}

const nondet = rows.filter((r) => !r.deterministic);
console.log(`\n${rows.length} cells, ${rows.length - nondet.length} byte-identical across two capture passes.`);
if (nondet.length) console.log('NON-DETERMINISTIC:', nondet.map((r) => r.label).join(', '));
