/** Assemble an unsealed chart candidate, not a fit record or a numerical/gate verdict.
 * The caller supplies the content-pinned gate-zero baseline, both dark charts and the
 * provenance lines of the point. This function preserves every other material leaf and both
 * light document byte streams. Existing entries describe the baseline and are kept verbatim.
 *
 * DL5o: every W50 candidate document carries X76's records itself. Each dark endpoint gains a
 * fitted method record for every chart leaf it names, and the receded dark endpoint gains an
 * explicit hold for each leaf it inherits from its active (W49a seal.ts 197-230; the owner port's
 * checkInheritance) that has no record in the baseline. With charts = null the identity
 * candidate is built: the dark patches are unchanged and only the holds are added.
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
type Entries = Record<string, any>;
const hash = (raw: Buffer | string) => createHash('sha256').update(raw).digest('hex');
const text = (value: unknown) => JSON.stringify(value, null, 2) + '\n';
const slots = ['active.light', 'active.dark', 'receded.light', 'receded.dark'] as const;
export const CHART_LEAVES = ['lowEndStrength', 'lowEnd44', 'lowEnd96', 'lowEnd160'] as const;
const CHARTER = 'docs/doperpowers/specs/2026-10-08-w50-dark-low-end-response.md';

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

function validateProvenance(value: unknown): asserts value is string[] {
  if (!Array.isArray(value) || !value.length ||
      value.some(line => typeof line !== 'string' || line.trim() === '')) {
    throw Error('A candidate names its point by nonempty provenance lines');
  }
}

const flatten = (node: any, prefix = '', out: Entries = {}): Entries => {
  for (const [key, value] of Object.entries(node)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === 'object' && !Array.isArray(value)) flatten(value, path, out);
    else out[path] = value;
  }
  return out;
};
const equal = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

/** The leaves a receded endpoint inherits from its active, as X76 reads them (W49a seal.ts
 * 197-230; owner/referee.ts checkInheritance): every leaf it names at the active's resolved
 * value without a 'measured' baseline record (or that moved), and every 'measured' active leaf
 * it does not name. */
export function inheritedLeaves(input: { activeResolved: any; activePatch: any; activeEntries: Entries;
  beforePatch: any; beforeEntries: Entries; candidatePatch: any }): string[] {
  const mine = flatten(input.candidatePatch), before = flatten(input.beforePatch);
  const active = flatten(input.activePatch), resolved = flatten(input.activeResolved);
  const moved = Object.keys(mine).filter(k => !equal(mine[k], before[k]));
  const inherited = Object.keys(mine).filter(k => equal(mine[k], resolved[k])
    && (input.beforeEntries[k]?.status !== 'measured' || moved.includes(k)));
  inherited.push(...Object.keys(active).filter(k => input.activeEntries[k]?.status === 'measured' && !(k in mine)));
  return [...new Set(inherited)].sort();
}

function fitted(leaf: string, value: unknown, previous: unknown, provenance: string[]) {
  const first = leaf === 'lowEndStrength'
    ? 'lowEndStrength: the compact low-end chart\'s declared strength 1 (part 2 candidateDomain.strength)'
    : `${leaf}: compact low-end chart row of the one W50 point (charter DL4), fitted within part 2 candidateDomain`;
  return { status: 'measured', value, previous: previous ?? null, method: [first, ...provenance] };
}

/** DL5o's records for one dark position: fitted chart leaves on both endpoints, and explicit
 * holds for the receded leaves inherited without a baseline record. A key never collides with
 * a baseline entry: nothing is relabelled. */
export function recordedEntries(input: { activeSource: any; recededSource: any; activePatch: any;
  recededPatch: any; activeResolved: any; previous: { active: any; receded: any }; provenance: string[] }) {
  validateProvenance(input.provenance);
  const add = (entries: Entries, leaf: string, value: unknown) => {
    if (Object.hasOwn(entries, leaf)) throw Error(`A baseline record already names ${leaf}`);
    entries[leaf] = value;
  };
  const active: Entries = { ...(input.activeSource.entries ?? {}) };
  const receded: Entries = { ...(input.recededSource.entries ?? {}) };
  for (const leaf of CHART_LEAVES) {
    if (Object.hasOwn(input.activePatch, leaf)) {
      add(active, leaf, fitted(leaf, input.activePatch[leaf], input.previous.active[leaf], input.provenance));
    }
    if (Object.hasOwn(input.recededPatch, leaf)) {
      add(receded, leaf, fitted(leaf, input.recededPatch[leaf], input.previous.receded[leaf], input.provenance));
    }
  }
  const resolved = flatten(input.activeResolved), mine = flatten(input.recededPatch);
  const baseline = input.recededSource.entries ?? {};
  for (const leaf of inheritedLeaves({ activeResolved: input.activeResolved, activePatch: input.activePatch,
    activeEntries: active, beforePatch: input.recededSource.patch, beforeEntries: baseline,
    candidatePatch: input.recededPatch })) {
    if ((CHART_LEAVES as readonly string[]).includes(leaf) || baseline[leaf]?.status === 'held') continue;
    add(receded, leaf, { status: 'held', value: leaf in mine ? mine[leaf] : resolved[leaf],
      inheritedFrom: 'active.dark.json (resolved)', named: leaf in mine,
      reading: [`W50 DL5o: ${leaf} explicitly held at its inherited active value; this candidate moves `
        + `only the compact low-end chart leaves (${CHART_LEAVES.join(', ')}).`, `Charter ${CHARTER}, DL5o.`] });
  }
  return { active, receded };
}

export function buildCandidate(baseline: Pin, charts: unknown, output: string, provenance: unknown): Pin {
  if (charts !== null) validateCharts(charts);
  validateProvenance(provenance);
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
  const before: Record<string, any> = {};
  for (const scheme of ['light', 'dark'] as const) {
    let base = DEFAULT_MATERIAL_PROFILE;
    for (const pose of ['active', 'receded'] as const) {
      base = before[`${pose}.${scheme}`] = withMaterialOverrides(base, original[`${pose}.${scheme}`]!.document.patch);
      if (base.lowEndStrength !== 0) throw Error('Candidate baseline must hold the inert chart');
    }
  }
  const chart = charts as Charts | null;
  const point = hash(JSON.stringify({ baseline: baseline.sha256,
    active: chart === null ? null : chart.active, receded: chart === null ? null : chart.receded }));
  const patches: Record<string, any> = {}, materials: Record<string, any> = {};
  for (const scheme of ['light', 'dark'] as const) {
    let base = DEFAULT_MATERIAL_PROFILE;
    for (const pose of ['active', 'receded'] as const) {
      const slot = `${pose}.${scheme}`, source = original[slot]!.document;
      const rows = chart === null ? null : chart[pose];
      patches[slot] = scheme === 'dark' && rows !== null ? { ...source.patch, lowEndStrength: 1,
        lowEnd44: rows[0], lowEnd96: rows[1], lowEnd160: rows[2] } as MaterialProfilePatch : source.patch;
      base = materials[slot] = withMaterialOverrides(base, patches[slot]);
    }
  }
  const entries: Record<string, Entries> = recordedEntries({ activeSource: original['active.dark']!.document,
    recededSource: original['receded.dark']!.document, activePatch: patches['active.dark'],
    recededPatch: patches['receded.dark'], activeResolved: materials['active.dark'],
    previous: { active: before['active.dark'], receded: before['receded.dark'] }, provenance });
  const files: Record<string, Buffer | string> = {};
  const endpoints: Record<string, Pin> = {};
  for (const scheme of ['light', 'dark'] as const) {
    for (const pose of ['active', 'receded'] as const) {
      const slot = `${pose}.${scheme}`;
      const source = original[slot]!;
      let bytes: Buffer | string = source.raw;
      if (scheme === 'dark') {
        bytes = text({ ...source.document, patch: patches[slot], entries: entries[pose],
          resolvedMaterialSha256: resolvedDigest(materials[slot]),
          ...(pose === 'receded' ? { appliesOver: 'active.dark.json',
            resolvedOverActiveDocument: 'active.dark.json' } : {}),
          candidateAssembly: { status: 'UNSEALED_CANDIDATE', baselineSha256: baseline.sha256,
            pointSha256: point, identity: chart === null,
            measurementEntries: 'Baseline records retained verbatim; DL5o adds the fitted chart and explicit '
              + 'hold records. Not a new seal' } });
      }
      files[`${slot}.json`] = bytes;
      endpoints[slot] = { path: `${slot}.json`, sha256: hash(bytes) };
    }
  }
  files['candidate.json'] = text({ ...declaration,
    name: `w50-${chart === null ? 'identity' : 'chart'}-${point.slice(0, 12)}`, endpoints });
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
