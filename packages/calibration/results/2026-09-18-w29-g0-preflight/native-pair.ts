/**
 * Two native capture roots, cell by cell — bytes first, then the metrics.
 *
 *   tsx results/2026-09-18-w29-g0-preflight/native-pair.ts \
 *     --a <root> --b <root> [--label-a granted --label-b sdk27] [--out pairs.json]
 *
 * G0 has three comparisons whose shape is the same and whose subject is not: one
 * bundle against another (c), one slider position against another (d), and one
 * run of the same configuration against the next, which is the spread the first
 * two have to beat (d again). All three are native against native, and
 * `measureCell` cannot take them — `ResultCellKey` requires a `WebCell`, so the
 * result matrix has no shape for a row with no web side in it (Grounding). This
 * is the same move `cli/tier-delta.ts` makes for the tier pair: the metric
 * primitives are image-pair generic, so they are called directly and the rows
 * live beside the matrix rather than in it.
 *
 * A root is a `VITREA_FIXTURES` directory: `<profile-key>/<scene>.png` beside a
 * `manifest.json`. Cells are joined on `<profile-key>/<scene>`; a cell present in
 * one root and not the other is reported rather than dropped, because in a
 * comparison of two bundles an absent cell is a finding about the bundle.
 *
 * Reported per cell, in the order a reader should take them:
 *
 * - **identical**, and `maxDelta` / `changedPx` when not. Bytes are the strongest
 *   statement available and the cheapest; the harness's own determinism check
 *   makes a repeat capture byte-stable, so a byte difference between two runs of
 *   one configuration is already the run-to-run spread rather than noise below it.
 * - **SSIM and OKLab ΔE**, whole canvas, and the mean/worst of the ΔE field. These
 *   are the metrics the fidelity read uses, run here so a difference can be
 *   stated in the same currency G2 will state Apple's change in.
 * - **interior level** under each image's own silhouette, in linear light — the
 *   quantity a tint or a slider position moves most directly.
 *
 * No thresholds and no verdicts: this package's standing rule is that a driver
 * prints a gap and a claims section decides what it means.
 */
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  decodePng,
  extractSilhouette,
  interiorLevel,
  oklabDeltaE,
  ssim,
  type CalibrationImage,
} from "../../src/index";

const here = dirname(fileURLToPath(import.meta.url));

const arg = (name: string, fallback?: string): string => {
  const index = process.argv.indexOf(`--${name}`);
  const value = index < 0 ? fallback : process.argv[index + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};

/** `<profile-key>/<scene>` → PNG path, for every cell a fixture root holds. */
const cellsOf = (root: string): Map<string, string> => {
  const found = new Map<string, string>();
  for (const profile of readdirSync(root, { withFileTypes: true })) {
    if (!profile.isDirectory() || profile.name === "backgrounds") continue;
    const dir = join(root, profile.name);
    for (const file of readdirSync(dir)) {
      if (file.endsWith(".png")) found.set(`${profile.name}/${file.slice(0, -4)}`, join(dir, file));
    }
  }
  return found;
};

/** Byte-level difference, the same currency `plurality.ts` classifies runs in. */
const bytes = (a: CalibrationImage, b: CalibrationImage) => {
  let changed = 0;
  let maxDelta = 0;
  let sum = 0;
  for (let i = 0; i < a.data.length; i += 4) {
    let cellMax = 0;
    for (let c = 0; c < 3; c += 1) {
      const d = Math.abs(a.data[i + c] - b.data[i + c]);
      sum += d;
      if (d > cellMax) cellMax = d;
    }
    if (cellMax > 0) changed += 1;
    if (cellMax > maxDelta) maxDelta = cellMax;
  }
  return { changedPx: changed, maxDelta, mad: sum / ((a.data.length / 4) * 3) };
};

const level = (image: CalibrationImage): number | null => {
  try {
    const silhouette = extractSilhouette(image, { kind: "alpha", threshold: 128 });
    return interiorLevel(image, silhouette).mean;
  } catch {
    return null;
  }
};

const rootA = resolve(arg("a"));
const rootB = resolve(arg("b"));
const labelA = arg("label-a", "a");
const labelB = arg("label-b", "b");
const outPath = arg("out", join(here, "pairs.json"));

const mapA = cellsOf(rootA);
const mapB = cellsOf(rootB);
const shared = [...mapA.keys()].filter((k) => mapB.has(k)).sort();
const onlyA = [...mapA.keys()].filter((k) => !mapB.has(k)).sort();
const onlyB = [...mapB.keys()].filter((k) => !mapA.has(k)).sort();

const rows = shared.map((cell) => {
  const a = decodePng(readFileSync(mapA.get(cell)!));
  const b = decodePng(readFileSync(mapB.get(cell)!));
  const rawA = readFileSync(mapA.get(cell)!);
  const rawB = readFileSync(mapB.get(cell)!);
  const identical = rawA.length === rawB.length && rawA.equals(rawB);
  const byte = bytes(a, b);
  const deltaE = oklabDeltaE(a, b);
  const structural = ssim(a, b);
  return {
    cell,
    identical,
    changedPx: byte.changedPx,
    maxDelta: byte.maxDelta,
    mad: byte.mad,
    ssim: structural.mean,
    deltaEMean: deltaE.mean,
    deltaEWorst: deltaE.max,
    interiorLevel: { [labelA]: level(a), [labelB]: level(b) },
  };
});

const report = {
  a: { label: labelA, root: rootA },
  b: { label: labelB, root: rootB },
  onlyInA: onlyA,
  onlyInB: onlyB,
  cells: rows,
  summary: {
    cells: rows.length,
    identical: rows.filter((r) => r.identical).length,
    worstMaxDelta: rows.reduce((m, r) => Math.max(m, r.maxDelta), 0),
    worstDeltaE: rows.reduce((m, r) => Math.max(m, r.deltaEWorst), 0),
    worstChangedPx: rows.reduce((m, r) => Math.max(m, r.changedPx), 0),
  },
};

for (const r of rows) {
  console.log(
    `${r.cell}: identical=${r.identical} changedPx=${r.changedPx} maxDelta=${r.maxDelta} ` +
      `mad=${r.mad.toFixed(4)} ssim=${r.ssim.toFixed(6)} dE=${r.deltaEMean.toFixed(6)}/${r.deltaEWorst.toFixed(6)}`,
  );
}
if (onlyA.length) console.log(`only in ${labelA}: ${onlyA.join(", ")}`);
if (onlyB.length) console.log(`only in ${labelB}: ${onlyB.join(", ")}`);
console.log(
  `${report.summary.identical} of ${report.summary.cells} cells byte-identical; ` +
    `worst maxDelta ${report.summary.worstMaxDelta}, worst ΔE ${report.summary.worstDeltaE.toFixed(6)}`,
);
if (existsSync(outPath)) console.log(`(overwriting ${outPath})`);
writeFileSync(outPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(`→ ${outPath}`);
