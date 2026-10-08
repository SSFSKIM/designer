/** Assemble an unsealed chart candidate, not a fit record or a numerical/gate verdict.
 * The caller supplies the content-pinned gate-zero baseline and both dark charts. This
 * function preserves every other material leaf and both light document byte streams.
 * Existing entries describe the baseline; they are not relabelled as new measurements.
 * The later selected-point record owns fitted/held provenance and owner-law evidence.
 */
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch,
} from '@vitrea/renderer-webgpu';
import { readCandidateDocument, resolvedDigest } from '../../../scripts/candidate-document.ts';

type Pin = { path: string; sha256: string };
type Row = readonly [number, number, number, number];
type Chart = readonly [Row, Row, Row];
type Charts = { active: Chart; receded: Chart };
const hash = (raw: Buffer | string) => createHash('sha256').update(raw).digest('hex');
const text = (value: unknown) => JSON.stringify(value, null, 2) + '\n';
const slots = ['active.light', 'active.dark', 'receded.light', 'receded.dark'] as const;

function validateCharts(value: unknown): asserts value is Charts {
  if (!value || typeof value !== 'object' ||
      Object.keys(value).sort().join(',') !== 'active,receded') {
    throw Error('Chart candidate requires exactly the active and receded rows');
  }
  for (const rows of Object.values(value)) {
    if (!Array.isArray(rows) || rows.length !== 3 || rows.some(row =>
      !Array.isArray(row) || row.length !== 4 || row.some((n, i) =>
        typeof n !== 'number' || !Number.isFinite(n) || n < 0 || n > 1 ||
        (i > 0 && n < row[i - 1])))) {
      throw Error('Chart candidate requires three nondecreasing finite four-ordinate rows');
    }
  }
}

export function buildCandidate(baseline: Pin, charts: unknown, output: string): Pin {
  validateCharts(charts);
  const baselinePath = resolve(baseline.path);
  const raw = readFileSync(baselinePath);
  if (hash(raw) !== baseline.sha256) throw Error('Changed candidate baseline pin');
  // This checks every endpoint hash, composed digest, CSS mapping and registry identity.
  const parsed = readCandidateDocument(baselinePath).document;
  if (![.25, .5].includes(parsed.glassTintAmount!)) throw Error('Undeclared glass position');
  const declaration = JSON.parse(raw.toString());
  const original: Record<string, { raw: Buffer; document: any }> = {};
  for (const slot of slots) {
    const bytes = readFileSync(resolve(dirname(baselinePath), declaration.endpoints[slot].path));
    original[slot] = { raw: bytes, document: JSON.parse(bytes.toString()) };
  }
  for (const scheme of ['light', 'dark'] as const) {
    let base = DEFAULT_MATERIAL_PROFILE;
    for (const pose of ['active', 'receded'] as const) {
      base = withMaterialOverrides(base, original[`${pose}.${scheme}`]!.document.patch);
      if (base.lowEndStrength !== 0) throw Error('Candidate baseline must hold the inert chart');
    }
  }
  const point = hash(JSON.stringify({ baseline: baseline.sha256,
    active: charts.active, receded: charts.receded }));
  const files: Record<string, Buffer | string> = {};
  const endpoints: Record<string, Pin> = {};
  for (const scheme of ['light', 'dark'] as const) {
    let base = DEFAULT_MATERIAL_PROFILE;
    for (const pose of ['active', 'receded'] as const) {
      const slot = `${pose}.${scheme}`;
      const source = original[slot]!;
      let bytes: Buffer | string = source.raw;
      if (scheme === 'dark') {
        const rows = charts[pose];
        const patch: MaterialProfilePatch = { ...source.document.patch, lowEndStrength: 1,
          lowEnd44: rows[0], lowEnd96: rows[1], lowEnd160: rows[2] };
        const material = withMaterialOverrides(base, patch);
        bytes = text({ ...source.document, patch, resolvedMaterialSha256: resolvedDigest(material),
          ...(pose === 'receded' ? { appliesOver: 'active.dark.json',
            resolvedOverActiveDocument: 'active.dark.json' } : {}),
          candidateAssembly: { status: 'UNSEALED_CANDIDATE', baselineSha256: baseline.sha256,
            pointSha256: point, measurementEntries: 'Retained baseline records; not a new seal' } });
        base = material;
      }
      files[`${slot}.json`] = bytes;
      endpoints[slot] = { path: `${slot}.json`, sha256: hash(bytes) };
    }
  }
  files['candidate.json'] = text({ ...declaration,
    name: `w50-chart-${point.slice(0, 12)}`, endpoints });
  output = resolve(output);
  if (existsSync(output)) throw Error('Candidate destination is write-once');
  mkdirSync(output, { recursive: true });
  for (const [name, bytes] of Object.entries(files)) {
    writeFileSync(join(output, name), bytes, { flag: 'wx' });
  }
  const path = join(output, 'candidate.json');
  readCandidateDocument(path);
  return { path, sha256: hash(files['candidate.json']!) };
}
