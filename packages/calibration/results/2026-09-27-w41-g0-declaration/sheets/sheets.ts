/** W41 clause 9 / §5.191. The CLI inventories metadata only; rendering has no native reader.
 * A later authorized exposure supplies bytes through readNative, never a raw-archive root.
 */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { resolve, join, relative, isAbsolute, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { PNG } from 'pngjs';
import { loadCurrentRows } from '../../../src/matrix-store';
import { linearRgbToOklab } from '../../../src/color';
import { createImage, decodePng, toLinearRgb, type CalibrationImage } from '../../../src/image';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const PACKAGE = resolve(HERE, '../../..');
const ROOT = resolve(PACKAGE, '../..');
export interface Document { kind: string; path: string; sha256: string }
export interface Cell {
  bed: string; profileKey: string; sceneId: string; documents: Document[]; pose: readonly string[];
  role?: string;
}
interface Row { key: { profileKey: string; sceneId: string;
  web: { renderer: string; capturePath: string } } }
interface Planned { profileKey: string; sceneId: string; role?: string }

function documents(path: string): Document[] {
  const found = [...path.matchAll(/(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])/g)]
    .map(m => ({ kind: m[1]!, path: m[2]!, sha256: m[3]! }));
  if (found.filter(d => d.kind === 'materialProfile').length !== 1 ||
      found.filter(d => d.kind === 'recededProfile').length > 1 ||
      found.length !== (path.match(/sha256:/g) ?? []).length ||
      found.length !== (path.match(/(?:materialProfile|recededProfile)=/g) ?? []).length) {
    throw new Error('document provenance is incomplete or malformed');
  }
  return found.sort((a, b) => a.kind.localeCompare(b.kind));
}
function signature(docs: Document[]) {
  return JSON.stringify([...docs].sort((a, b) => a.kind.localeCompare(b.kind)));
}
// Values may contain spaces and parentheses; only the next named clause ends one pose value.
const POSE = ['deviceScaleFactor', 'colorScheme', 'accessibility'].map(name =>
  [name, new RegExp(`${name}=(.*?)(?=,\\s*[A-Za-z][A-Za-z0-9]*=|$)`)] as const);
function poseOf(capturePath: string): readonly string[] {
  return POSE.map(([name, pattern]) => `${name}=${pattern.exec(capturePath)?.[1] ?? '(absent)'}`);
}
function completePose(pose: readonly string[]): boolean {
  return pose.length === POSE.length && pose.every((clause, i) =>
    clause.startsWith(`${POSE[i]![0]}=`) && clause.length > POSE[i]![0].length + 1 &&
    !clause.endsWith('=(absent)'));
}

/** One sheet per profile × scene, not one duplicate per tier. CSS-only rows stay in the bed. */
export function enumerateCells(rows: readonly Row[], planned: readonly Planned[]): Cell[] {
  const profiles = new Map<string, { documents: Document[]; pose: readonly string[] }>();
  const cells = new Map<string, Cell>();
  const gpuCells = new Set<string>();
  for (const row of rows) {
    const { profileKey, sceneId, web } = row.key;
    const docs = documents(web.capturePath);
    const pose = poseOf(web.capturePath);
    if (!completePose(pose)) throw new Error(`profile ${profileKey}: incomplete matrix row pose`);
    const prior = profiles.get(profileKey);
    if (prior && signature(prior.documents) !== signature(docs)) {
      throw new Error(`profile ${profileKey}: conflicting current document pairs`);
    }
    // W39 has no matrix row of its own. Do not select an arbitrary scene's pose for it.
    if (prior && JSON.stringify(prior.pose) !== JSON.stringify(pose)) {
      throw new Error(`profile ${profileKey}: conflicting current row pose`);
    }
    profiles.set(profileKey, { documents: docs, pose });
    const key = `${profileKey}/${sceneId}`;
    if (web.renderer === 'webgpu' || !gpuCells.has(key)) {
      cells.set(key, { bed: 'canonical', profileKey, sceneId, documents: docs, pose });
    }
    if (web.renderer === 'webgpu') gpuCells.add(key);
  }
  const result = [...cells.values()];
  for (const cell of planned) {
    const profile = profiles.get(cell.profileKey);
    if (!profile) throw new Error(`W39 profile ${cell.profileKey} has no current shipped documents`);
    result.push({ ...cell, bed: 'w39', ...profile });
  }
  return result.sort((a, b) => `${a.bed}/${a.profileKey}/${a.sceneId}`
    .localeCompare(`${b.bed}/${b.profileKey}/${b.sceneId}`));
}

function contained(root: string, path: string): string {
  const full = resolve(root, path);
  const rel = relative(resolve(root), full);
  if (rel === '..' || rel.startsWith('../') || isAbsolute(rel)) throw new Error('path escapes root');
  return full;
}
function present(path: string) { return existsSync(path) && statSync(path).isFile(); }

/** MATCH means pose + document provenance + PNG presence, NOT decoded pixels or a capture-byte hash.
 * Stale metadata is refused even if the PNG is missing; missing metadata is UNMEASURED.
 */
export function inspectCell(cell: Cell, repositoryRoot: string, captureRoot: string) {
  const dir = contained(captureRoot, `${cell.profileKey}/${cell.sceneId}`);
  const pngPath = join(dir, `${cell.sceneId}__webgpu.png`);
  const metadataPath = join(dir, 'cell__webgpu.json');
  const absent = [metadataPath, pngPath].filter(p => !present(p));
  if (present(metadataPath)) {
    const meta = JSON.parse(readFileSync(metadataPath, 'utf8'));
    if (meta.sceneId !== cell.sceneId || meta.renderer !== 'webgpu' || meta.colorSpace !== 'srgb') {
      throw new Error(`${dir}: scene/renderer/colour-space metadata mismatch`);
    }
    const named = documents(typeof meta.capturePath === 'string' ? meta.capturePath : '');
    if (signature(named) !== signature(cell.documents)) {
      throw new Error(`${dir}: document provenance differs from current cell`);
    }
    const capturedPose = poseOf(typeof meta.capturePath === 'string' ? meta.capturePath : '');
    if (!completePose(cell.pose) || !completePose(capturedPose) ||
        capturedPose.some((clause, i) => clause !== cell.pose[i])) {
      throw new Error(`${dir}: capture pose differs from matrix row or is incomplete`);
    }
    for (const doc of named) {
      const path = contained(repositoryRoot, doc.path);
      const sha = createHash('sha256').update(readFileSync(path)).digest('hex').slice(0, 12);
      if (sha !== doc.sha256) throw new Error(`${dir}: capture does not name shipped bytes: ${doc.path}`);
    }
  }
  return { status: absent.length ? 'UNMEASURED' : 'MATCH', absent, pngPath, metadataPath };
}

/** The W31 sequential diagnostic: black = 0, white = ΔE >= 0.125; no categorical palette.
 * Every comparison is OKLab Euclidean distance, amplified by eight, without resizing.
 */
export function differencePanel(native: CalibrationImage, web: CalibrationImage): CalibrationImage {
  if (native.width !== web.width || native.height !== web.height) throw new Error('image dimensions differ');
  const a = toLinearRgb(native), b = toLinearRgb(web);
  const data = new Uint8Array(native.width * native.height * 4);
  for (let i = 0; i < native.width * native.height; i++) {
    const x = linearRgbToOklab(a[i * 3]!, a[i * 3 + 1]!, a[i * 3 + 2]!);
    const y = linearRgbToOklab(b[i * 3]!, b[i * 3 + 1]!, b[i * 3 + 2]!);
    const byte = Math.min(255, Math.round(Math.hypot(x.L - y.L, x.a - y.a, x.b - y.b) * 8 * 255));
    data.set([byte, byte, byte, 255], i * 4);
  }
  return createImage(native.width, native.height, data);
}
const escape = (s: string) => s.replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[c]!);
function encode(image: CalibrationImage): Buffer {
  const png = new PNG({ width: image.width, height: image.height });
  png.data = Buffer.from(image.data);
  return PNG.sync.write(png);
}
const imageTag = (image: CalibrationImage, label: string) =>
  `<img alt="${escape(label)}" width="${image.width}" height="${image.height}" ` +
  `src="data:image/png;base64,${encode(image).toString('base64')}">`;
/** Authoritative canonical role: never trust a caller-provided role for exposure permission. */
export function canonicalRole(sceneId: string, repositoryRoot: string): string {
  const spec = JSON.parse(readFileSync(resolve(repositoryRoot, 'apps/reference-apple/scenes.json'), 'utf8'));
  const roles = ['calibration', 'validation', 'holdout', 'recorded', 'probe']
    .filter(role => Array.isArray(spec.split?.[role]) && spec.split[role].includes(sceneId));
  if (roles.length !== 1) throw new Error(`${sceneId}: canonical split role is missing or ambiguous`);
  return roles[0]!;
}
interface Configuration {
  documents: Record<string, string>; sourceSha256: string; sourceListSha256: string;
}
/** Reuse the cross-gate ledger's definition without invoking its record/show CLI or writing it. */
export function configurationState(repositoryRoot: string): Configuration {
  const script = `import importlib.util,json,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('sheet_configuration',sys.argv[1])
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=Path(sys.argv[2])
print(json.dumps(dict(documents=m.document_hashes(),sourceSha256=m.source_hash()[0],sourceListSha256=m.source_list_hash())))`;
  return JSON.parse(execFileSync('python3', ['-c', script,
    resolve(PACKAGE, 'results/holdout-configuration/configuration.py'), resolve(repositoryRoot)],
  { encoding: 'utf8' }));
}
function assertHoldoutCandidateRead(repositoryRoot: string, candidateDocuments: Document[]) {
  const path = resolve(repositoryRoot, 'packages/calibration/results/holdout-configuration/configuration-log.json');
  const refusal = 'canonical holdout candidate refused: configuration has no matching recorded read';
  if (!present(path)) throw new Error(refusal);
  const state = configurationState(repositoryRoot);
  const log = JSON.parse(readFileSync(path, 'utf8')) as { reads?: Configuration[] };
  const entries = (docs: Record<string, string>) => JSON.stringify(Object.entries(docs).sort());
  if (!log.reads?.some(read => read.sourceSha256 === state.sourceSha256 &&
      read.sourceListSha256 === state.sourceListSha256 && entries(read.documents) === entries(state.documents))) {
    throw new Error(refusal);
  }
  for (const doc of candidateDocuments) {
    const full = createHash('sha256').update(readFileSync(contained(repositoryRoot, doc.path))).digest('hex');
    if (state.documents[basename(doc.path)] !== full || !full.startsWith(doc.sha256)) throw new Error(refusal);
  }
}
export interface RenderOptions {
  repositoryRoot: string;
  captureRoot: string;
  /** The caller owns identification-role permission, repeat selection and exposure receipts. */
  readNative: (cell: Cell) => Promise<Uint8Array | undefined>;
  /** G2 supplies actual document clauses and a separately rooted candidate capture tree. */
  candidate?: { documents: Document[]; captureRoot: string };
}

/** Render one labeled, standalone HTML sheet. A caller loops over enumerateCells's full bed.
 * No image paths are handed to a browser: PNGs are embedded only after provenance succeeds.
 */
export async function renderCell(cell: Cell, options: RenderOptions): Promise<string> {
  if (cell.bed === 'canonical' && canonicalRole(cell.sceneId, options.repositoryRoot) === 'holdout' &&
      options.candidate) assertHoldoutCandidateRead(options.repositoryRoot, options.candidate.documents);
  const shipped = inspectCell(cell, options.repositoryRoot, options.captureRoot);
  const candidate = options.candidate ? inspectCell({ ...cell, documents: options.candidate.documents },
    options.repositoryRoot, options.candidate.captureRoot) : undefined;
  const bytes = await options.readNative(cell);
  const native = bytes ? decodePng(bytes) : undefined;
  const gpu = shipped.status === 'MATCH' ? decodePng(readFileSync(shipped.pngPath)) : undefined;
  const next = candidate?.status === 'MATCH' ? decodePng(readFileSync(candidate.pngPath)) : undefined;
  const panel = (image: CalibrationImage | undefined, label: string, missing = 'UNMEASURED') =>
    `<td><h2>${label}</h2>${image ? imageTag(image, label) : `<p>${missing}</p>`}</td>`;
  const delta = (web: CalibrationImage | undefined) => native && web ? differencePanel(native, web) : undefined;
  const title = `${cell.bed} / ${cell.profileKey} / ${cell.sceneId}`;
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>${escape(title)}</title>
<style>body{font:14px system-ui;color:#111;background:white;margin:24px}table{border-spacing:8px}
 td{vertical-align:top;border:1px solid #aaa;padding:8px}h2{font-size:16px}img{display:block}
 code{overflow-wrap:anywhere}p{max-width:100ch}</style><h1>${escape(title)}</h1>
<p>ΔE × 8: OKLab distance; black = 0, white = 0.125 or greater (clipped). Original pixel dimensions.
The native reader, not this sheet, owns exposure authorization and repeat selection.</p>
<table aria-label="Native and WebGPU comparison"><tr>${panel(native, 'Native')}${panel(gpu, 'Shipped WebGPU')}
${panel(next, 'Candidate', candidate ? 'UNMEASURED' : 'EMPTY — awaiting G2 document')}</tr>
<tr><td>Difference from native</td>${panel(delta(gpu), 'Shipped ΔE × 8')}
${panel(delta(next), 'Candidate ΔE × 8', candidate ? 'UNMEASURED' : 'EMPTY — awaiting G2 document')}</tr></table>
<p>Shipped documents: <code>${escape(signature(cell.documents))}</code></p>
<p>Candidate documents: <code>${escape(options.candidate ? signature(options.candidate.documents) : 'none')}</code></p>
<p>Capture root: <code>${escape(options.captureRoot)}</code>. Missing captures are UNMEASURED, never blank successes.</p></html>`;
}

/** Invoke only W39's metadata constructor and launch_plan, never Reader or a payload root. */
export function w39Plan(): Planned[] {
  const script = `import importlib.util,json,sys
p=sys.argv[1]
s=importlib.util.spec_from_file_location('w41_sheet_wave',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.default_wave(); ids,_=w.launch_plan(('calibration','validation'))
assert len(ids)==138, 'W39 plan membership changed'
print(json.dumps([dict(profileKey=p,sceneId=s,role=w.roles[s]) for s in ids for p in sorted(w.profiles_of[s])]))`;
  return JSON.parse(execFileSync('python3', ['-c', script,
    resolve(HERE, '../../2026-09-26-w39-g0-colour-edge-bed/wave.py')], { encoding: 'utf8' }));
}

export function inventory(repositoryRoot: string, captureRoot: string, w39CaptureRoot: string) {
  if (process.env['VITREA_MATRIX_PATH']) throw new Error('inventory requires current union; unset VITREA_MATRIX_PATH');
  const rows = loadCurrentRows();
  const planned = w39Plan();
  const cells = enumerateCells(rows, planned).map(cell => ({ ...cell,
    ...inspectCell(cell, repositoryRoot, cell.bed === 'w39' ? w39CaptureRoot : captureRoot) }));
  const count = (bed: string) => {
    const selected = cells.filter(c => c.bed === bed);
    return { cells: selected.length, matches: selected.filter(c => c.status === 'MATCH').length,
      UNMEASURED: selected.filter(c => c.status === 'UNMEASURED').length };
  };
  return { mode: 'inventory-only', pixelsRead: 0, nativePayloadsOpened: 0,
    repositoryRoot, captureRoot, captureRootExists: existsSync(captureRoot),
    w39CaptureRoot, w39CaptureRootExists: existsSync(w39CaptureRoot),
    currentUnionRows: rows.length, canonical: count('canonical'),
    w39SceneIds: new Set(planned.map(c => c.sceneId)).size, w39: count('w39'),
    candidate: 'EMPTY — awaiting G2 document',
    matchMeaning: 'metadata pose/document/receded provenance and PNG presence only; not capture-byte identity', cells };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: {
    'repository-root': { type: 'string', default: ROOT },
    'capture-root': { type: 'string', default: resolve(PACKAGE, 'web-captures') },
    'w39-capture-root': { type: 'string', default: resolve(HERE, 'absent-w39-captures') },
  } });
  if (positionals.length !== 1 || positionals[0] !== 'inventory') {
    throw new Error('G0 CLI supports inventory only; rendering requires an authorized readNative API caller');
  }
  console.log(JSON.stringify(inventory(resolve(values['repository-root']!), resolve(values['capture-root']!),
    resolve(values['w39-capture-root']!)), null, 2));
}
