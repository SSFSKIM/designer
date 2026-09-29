/** W41 G2 standing eye sheets (c9a §5.193): Native | Shipped pre-W41 | Shipped now (E3).
 *
 * G0's instrument (§5.191) fixed the sheet's shape and its OKLab ΔE × 8 encoding; G1 (§5.192
 * §19–§20) filled its third column with a scratch E3. G2 sealed E3 into the light receded
 * document, so the third column is now the SHIPPED material and the second is the one it
 * replaced. This module keeps G0's table shape (so G0's export-png.py draws it unchanged) and
 * G0's difference panel, and relabels the columns.
 *
 * Read-only toward evidence: no browser, no capture, no matrix/generation/profile/fixture
 * write. A canonical cell's role is read from scenes.json BEFORE any path is formed, and a
 * holdout cell is refused there, so no holdout fixture or capture is ever stat'ed or opened.
 * W39 natives come only through G1's guarded bridge (native.py, Reader.read, cal/val roles).
 */
import { createHash } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { closeSync, existsSync, mkdirSync, openSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { basename, isAbsolute, join, relative, resolve } from 'node:path';
import { gunzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';
import { canonicalRole, differencePanel } from '../../2026-09-27-w41-g0-declaration/sheets/sheets';
import { linearRgbToOklab } from '../../../src/color';
import { decodePng, toLinearRgb, type CalibrationImage } from '../../../src/image';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(HERE, '../../../../..');
const EXPORTER = resolve(HERE, '../../2026-09-27-w41-g0-declaration/sheets/export-png.py');
const G1_NATIVE = resolve(HERE, '../../2026-09-27-w41-g1-identification/sheets/native.py');
const RETIRED = 'packages/calibration/results/2026-09-29-w41-g2-landing/retired-documents';
export const sha = (b: Uint8Array | string) => createHash('sha256').update(b).digest('hex');

export interface Document { kind: string; path: string; sha256: string }
const ACTIVE_PATH = 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json';
const RECEDED_PATH = 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json';
/** The retired light generation (results/generations/85ad7f7e3e0d.json) and the sealed one. */
export const PRE_W41: Document[] = [{ kind: 'materialProfile', path: ACTIVE_PATH, sha256: '85ad7f7e3e0d' },
  { kind: 'recededProfile', path: RECEDED_PATH, sha256: '30fbe05986ae' }];
export const NOW_E3: Document[] = [{ kind: 'materialProfile', path: ACTIVE_PATH, sha256: '85ad7f7e3e0d' },
  { kind: 'recededProfile', path: RECEDED_PATH, sha256: '003940b4c7da' }];

function documents(capturePath: string): Document[] {
  const found = [...capturePath.matchAll(/(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])/g)]
    .map(m => ({ kind: m[1]!, path: m[2]!, sha256: m[3]! }));
  if (found.length !== (capturePath.match(/sha256:/g) ?? []).length) throw new Error('malformed document clause');
  return found.sort((a, b) => a.kind.localeCompare(b.kind));
}
const signature = (docs: Document[]) => JSON.stringify([...docs].sort((a, b) => a.kind.localeCompare(b.kind)));
const POSE = ['deviceScaleFactor', 'colorScheme', 'accessibility'].map(name =>
  [name, new RegExp(`${name}=(.*?)(?=,\\s*[A-Za-z][A-Za-z0-9]*=|$)`)] as const);
const poseOf = (capturePath: string) =>
  POSE.map(([name, pattern]) => `${name}=${pattern.exec(capturePath)?.[1] ?? '(absent)'}`);
function contained(root: string, path: string): string {
  const full = resolve(root, path);
  const rel = relative(resolve(root), full);
  if (rel === '..' || rel.startsWith('../') || isAbsolute(rel)) throw new Error('path escapes root');
  return full;
}
const present = (path: string) => existsSync(path) && statSync(path).isFile();

/** A clause names BYTES: the live file when it still holds them, else the copy the seal retired
 * beside ../retired-documents (the same resolver G2 gave the W37/W38 instruments). */
export function resolveDocument(repositoryRoot: string, doc: Document): string {
  const live = contained(repositoryRoot, doc.path);
  if (present(live) && sha(readFileSync(live)).slice(0, 12) === doc.sha256) return live;
  const retired = join(repositoryRoot, RETIRED, `${basename(doc.path, '.json')}.${doc.sha256}.json`);
  if (present(retired) && sha(readFileSync(retired)).slice(0, 12) === doc.sha256) return retired;
  throw new Error(`no file holds ${doc.path} at ${doc.sha256}`);
}

export interface Capture {
  png: string; pngSha256: string; cellSha256: string; pose: string[]; samplingBackend: string;
  documents: Document[];
}
/** undefined = absent. A present capture naming any other documents, scene or renderer refuses. */
export function inspectCapture(root: string, profileKey: string, sceneId: string, expected: Document[],
  repositoryRoot = ROOT): Capture | undefined {
  const dir = contained(root, join(profileKey, sceneId));
  const png = join(dir, `${sceneId}__webgpu.png`);
  const metadata = join(dir, 'cell__webgpu.json');
  if (!present(metadata) || !present(png)) return undefined;
  const bytes = readFileSync(metadata);
  const meta = JSON.parse(bytes.toString('utf8'));
  if (meta.sceneId !== sceneId || meta.renderer !== 'webgpu' || meta.colorSpace !== 'srgb') {
    throw new Error(`${dir}: scene/renderer/colour-space metadata mismatch`);
  }
  const named = documents(String(meta.capturePath ?? ''));
  if (signature(named) !== signature(expected)) throw new Error(`${dir}: names ${signature(named)}`);
  for (const doc of named) resolveDocument(repositoryRoot, doc);
  const pose = poseOf(meta.capturePath);
  if (pose.some(clause => clause.endsWith('=(absent)'))) throw new Error(`${dir}: incomplete pose`);
  return { png, pngSha256: sha(readFileSync(png)), cellSha256: sha(bytes), pose,
    samplingBackend: String(meta.samplingBackend), documents: named };
}

/** Whole-frame and changed-region OKLab distances to native. A diagnostic beside the eye, not a
 * referee: "changed" is every pixel whose RGBA differs between the two web columns, i.e. what
 * the seal moved; closerFraction is the share of those where now is nearer native than pre. */
export function distances(native: CalibrationImage, pre: CalibrationImage | undefined, now: CalibrationImage) {
  const n = native.width * native.height;
  const lab = (image: CalibrationImage) => {
    const linear = toLinearRgb(image);
    const out = new Float64Array(n * 3);
    for (let i = 0; i < n; i++) {
      const c = linearRgbToOklab(linear[i * 3]!, linear[i * 3 + 1]!, linear[i * 3 + 2]!);
      out.set([c.L, c.a, c.b], i * 3);
    }
    return out;
  };
  const reference = lab(native);
  const d = (other: Float64Array, i: number) => Math.hypot(reference[i * 3]! - other[i * 3]!,
    reference[i * 3 + 1]! - other[i * 3 + 1]!, reference[i * 3 + 2]! - other[i * 3 + 2]!);
  const nowLab = lab(now);
  const preLab = pre ? lab(pre) : undefined;
  let sumNow = 0, sumPre = 0, changed = 0, changedPre = 0, changedNow = 0, closer = 0;
  for (let i = 0; i < n; i++) {
    const dn = d(nowLab, i);
    sumNow += dn;
    if (!preLab || !pre) continue;
    const dp = d(preLab, i);
    sumPre += dp;
    const moved = pre.data[i * 4] !== now.data[i * 4] || pre.data[i * 4 + 1] !== now.data[i * 4 + 1] ||
      pre.data[i * 4 + 2] !== now.data[i * 4 + 2] || pre.data[i * 4 + 3] !== now.data[i * 4 + 3];
    if (!moved) continue;
    changed += 1; changedPre += dp; changedNow += dn; if (dn < dp) closer += 1;
  }
  const round = (x: number) => Math.round(x * 1e6) / 1e6;
  return { pixels: n, meanDeltaENow: round(sumNow / n),
    ...(pre ? { meanDeltaEPre: round(sumPre / n), changedPixels: changed,
      ...(changed ? { changedMeanDeltaEPre: round(changedPre / changed),
        changedMeanDeltaENow: round(changedNow / changed), closerFraction: round(closer / changed) } : {}) } : {}) };
}

const escape = (s: string) => s.replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!);
function encode(image: CalibrationImage): Buffer {
  const png = new PNG({ width: image.width, height: image.height });
  png.data = Buffer.from(image.data);
  return PNG.sync.write(png);
}
const imageTag = (image: CalibrationImage, label: string) =>
  `<img alt="${escape(label)}" width="${image.width}" height="${image.height}" ` +
  `src="data:image/png;base64,${encode(image).toString('base64')}">`;
export const LABELS = { native: 'Native', pre: 'Shipped pre-W41', now: 'Shipped now (E3)',
  preDelta: 'Pre-W41 ΔE × 8', nowDelta: 'Now (E3) ΔE × 8' };

/** G0's fixed 2 × 3 table (the exporter refuses any other shape), G2's column meanings. */
export function sheetHtml(title: string, native: CalibrationImage, pre: CalibrationImage | undefined,
  now: CalibrationImage, notes: string[], preMissing = 'UNMEASURED'): string {
  for (const image of [pre, now]) {
    if (image && (image.width !== native.width || image.height !== native.height)) {
      throw new Error(`${title}: image dimensions differ`);
    }
  }
  const panel = (image: CalibrationImage | undefined, label: string) =>
    `<td><h2>${escape(label)}</h2>${image ? imageTag(image, label) : `<p>${escape(preMissing)}</p>`}</td>`;
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>${escape(title)}</title>
<style>body{font:14px system-ui;color:#111;background:white;margin:24px}table{border-spacing:8px}
 td{vertical-align:top;border:1px solid #aaa;padding:8px}h2{font-size:16px}img{display:block}
 code{overflow-wrap:anywhere}p{max-width:100ch}</style><h1>${escape(title)}</h1>
<p>ΔE × 8: OKLab distance; black = 0, white = 0.125 or greater (clipped). Original pixel dimensions.
Pre-W41 is the retired light generation (receded 30fbe05986ae); now is the sealed E3 (receded 003940b4c7da).</p>
<table aria-label="Native and WebGPU comparison"><tr>${panel(native, LABELS.native)}${panel(pre, LABELS.pre)}
${panel(now, LABELS.now)}</tr>
<tr><td>Difference from native</td>${panel(pre && differencePanel(native, pre), LABELS.preDelta)}
${panel(differencePanel(native, now), LABELS.nowDelta)}</tr></table>
${notes.map(note => `<p><code>${escape(note)}</code></p>`).join('\n')}</html>`;
}

/** Regular-file stdin/stdout with a bounded timeout: G1's first run stalled on a pipe EOF. */
export function exportPng(htmlPath: string, pngPath: string) {
  const input = openSync(htmlPath, 'r');
  const output = openSync(pngPath, 'wx');
  try {
    const result = spawnSync('python3.12', [EXPORTER], { stdio: [input, output, 'pipe'], timeout: 120_000 });
    if (result.status !== 0) throw new Error(`export-png failed: ${result.stderr?.toString() ?? result.error}`);
  } finally {
    closeSync(input);
    closeSync(output);
  }
  return sha(readFileSync(pngPath));
}

function writeSheet(outputRoot: string, name: string, html: string) {
  const htmlPath = join(outputRoot, `${name}.html`);
  writeFileSync(htmlPath, html, { flag: 'wx' });
  const pngPath = join(outputRoot, `${name}.png`);
  return { html: `${name}.html`, htmlSha256: sha(html), png: `${name}.png`, pngSha256: exportPng(htmlPath, pngPath) };
}

export function freshOutput(outputRoot: string) {
  const scratch = '/Users/new/vitrea-w41/g2-captures/sheets';
  const rel = relative(scratch, resolve(outputRoot));
  if (rel === '' || rel.startsWith('..') || isAbsolute(rel) || existsSync(outputRoot)) {
    throw new Error('output must be a fresh run directory beneath g2-captures/sheets');
  }
  mkdirSync(outputRoot, { recursive: true });
}

export interface CanonicalOptions {
  membership: string; newRoot: string; preRoot: string; outputRoot: string;
  g1Diagnostic: { freeze: string; sha256: string }; repositoryRoot?: string;
}
interface Declared { profileKey: string; renderer: string; fixtureSet: string; sceneId: string }

/** Every light macOS 27 WebGPU cell the stage declares outside holdout. */
export function canonicalCells(membershipPath: string, repositoryRoot = ROOT) {
  const membership = JSON.parse(readFileSync(membershipPath, 'utf8'));
  if (membership.active.sha256 !== NOW_E3[0]!.sha256 || membership.receded.sha256 !== NOW_E3[1]!.sha256) {
    throw new Error('stage does not declare the sealed light pair');
  }
  const cells = (membership.cells as Declared[]).filter(c => c.renderer === 'webgpu');
  let holdout = 0;
  const admitted = [];
  for (const cell of cells) {
    const role = canonicalRole(cell.sceneId, repositoryRoot);
    if (role !== cell.fixtureSet) throw new Error(`${cell.sceneId}: stage set ${cell.fixtureSet} is not ${role}`);
    if (role === 'holdout') { holdout += 1; continue; }
    admitted.push({ profileKey: cell.profileKey, sceneId: cell.sceneId, role });
  }
  return { declared: cells.length, holdout, cells: admitted };
}

const pixelsEqual = (a: CalibrationImage, b: CalibrationImage) => a.width === b.width &&
  a.height === b.height && Buffer.compare(Buffer.from(a.data), Buffer.from(b.data)) === 0;

export function renderCanonical(options: CanonicalOptions) {
  const repositoryRoot = options.repositoryRoot ?? ROOT;
  freshOutput(options.outputRoot);
  const g1 = readFileSync(options.g1Diagnostic.freeze);
  if (sha(g1) !== options.g1Diagnostic.sha256) throw new Error('G1 diagnostic freeze hash differs');
  const g1Captures = JSON.parse(g1.toString('utf8')).captures as Record<string, { png: string; pngSha256: string }>;
  const { declared, holdout, cells } = canonicalCells(options.membership, repositoryRoot);
  const records = [];
  for (const cell of cells) {
    const id = `${cell.profileKey}/${cell.sceneId}`;
    const base = { bed: 'canonical', ...cell };
    const now = inspectCapture(options.newRoot, cell.profileKey, cell.sceneId, NOW_E3, repositoryRoot);
    if (!now) { records.push({ ...base, status: 'NOT-CAPTURED', reason: 'the new read has no WebGPU capture' }); continue; }
    const nativePath = contained(join(repositoryRoot, 'apps/reference-apple/fixtures'),
      join(cell.profileKey, `${cell.sceneId}.png`));
    if (!present(nativePath)) { records.push({ ...base, status: 'NO-NATIVE' }); continue; }
    const pre = inspectCapture(options.preRoot, cell.profileKey, cell.sceneId, PRE_W41, repositoryRoot);
    if (pre && (JSON.stringify(pre.pose) !== JSON.stringify(now.pose) ||
        pre.samplingBackend !== now.samplingBackend)) throw new Error(`${id}: pre-W41 and now poses differ`);
    const nativeBytes = readFileSync(nativePath);
    const native = decodePng(nativeBytes);
    const nowImage = decodePng(readFileSync(now.png));
    const preImage = pre ? decodePng(readFileSync(pre.png)) : undefined;
    const g1Entry = g1Captures[id];
    const g1Diagnostic = g1Entry ? { pngSha256: g1Entry.pngSha256,
      fileStillMatches: present(g1Entry.png) && sha(readFileSync(g1Entry.png)) === g1Entry.pngSha256,
      identicalToNow: g1Entry.pngSha256 === now.pngSha256 } : undefined;
    const title = `W41 G2 / canonical ${cell.role} / ${cell.profileKey} / ${cell.sceneId}`;
    const html = sheetHtml(title, native, preImage, nowImage, [
      `native: ${relative(repositoryRoot, nativePath)} sha256 ${sha(nativeBytes)}`,
      `pre-W41: ${pre ? `${pre.png} sha256 ${pre.pngSha256}` : 'no capture at the retired pair'}`,
      `now (E3): ${now.png} sha256 ${now.pngSha256}`,
      `pose: ${now.pose.join(', ')}; sampling ${now.samplingBackend}`,
    ], 'UNMEASURED: no capture at the retired pair');
    const name = `canonical__${encodeURIComponent(cell.profileKey)}__${encodeURIComponent(cell.sceneId)}`;
    records.push({ ...base, status: pre ? 'RENDERED' : 'RENDERED-NOW-ONLY', pose: now.pose,
      native: { path: relative(repositoryRoot, nativePath), pngSha256: sha(nativeBytes) },
      pre: pre ? { png: pre.png, pngSha256: pre.pngSha256, cellSha256: pre.cellSha256, documents: pre.documents } : null,
      now: { png: now.png, pngSha256: now.pngSha256, cellSha256: now.cellSha256, documents: now.documents },
      preEqualsNowBytes: pre ? pre.pngSha256 === now.pngSha256 : null,
      preEqualsNowPixels: preImage ? pixelsEqual(preImage, nowImage) : null,
      ...(g1Diagnostic ? { g1Diagnostic } : {}),
      distances: distances(native, preImage, nowImage),
      ...writeSheet(options.outputRoot, name, html) });
  }
  return { declaredWebgpu: declared, holdoutNotOpened: holdout, records };
}

export interface W39Options {
  examples: { profileKey: string; sceneId: string }[]; outputRoot: string;
  g1Inventory: { gzip: string; sha256: string }; archiveRoot: string; repeat: number;
  baselineFreeze: { path: string; sha256: string }; baselineRoot: string;
  identityRoot: string; identityComparison: string;
}

/** The declared W39 handful only. Native: G1's guarded bridge at G1's repeat, and it must return
 * the very PNG G1's sheet recorded. Pre-W41: G1's frozen baseline. Now: G2's identity capture. */
export function renderW39(options: W39Options, g1Records: Record<string, any>, nativeGeneration: string) {
  const baseline = readFileSync(options.baselineFreeze.path);
  if (sha(baseline) !== options.baselineFreeze.sha256) throw new Error('baseline freeze hash differs');
  const frozen = JSON.parse(baseline.toString('utf8')).captures;
  const comparison = JSON.parse(readFileSync(options.identityComparison, 'utf8')).cells;
  const records = [];
  for (const example of options.examples) {
    const id = `${example.profileKey}/${example.sceneId}`;
    const g1 = g1Records[id];
    if (!g1 || g1.status !== 'RENDERED' || g1.role === undefined ||
        !['calibration', 'validation'].includes(g1.role)) throw new Error(`${id}: not an admitted G1 W39 sheet`);
    const expected = join(options.baselineRoot, example.profileKey, example.sceneId, `${example.sceneId}__webgpu.png`);
    if (!frozen[id] || resolve(frozen[id].png) !== resolve(expected)) throw new Error(`${id}: baseline freeze names another path`);
    const pre = inspectCapture(options.baselineRoot, example.profileKey, example.sceneId, PRE_W41);
    const now = inspectCapture(options.identityRoot, example.profileKey, example.sceneId, NOW_E3);
    if (!pre || pre.pngSha256 !== frozen[id].pngSha256) throw new Error(`${id}: baseline capture differs from its freeze`);
    if (!now || now.pngSha256 !== comparison[id]?.pngSha256) throw new Error(`${id}: identity capture differs`);
    if (JSON.stringify(pre.pose) !== JSON.stringify(now.pose)) throw new Error(`${id}: poses differ`);
    const bridged = JSON.parse(execFileSync('python3.12', [G1_NATIVE, '--archive-root', options.archiveRoot,
      '--generation', nativeGeneration, '--cell', id, '--repeat', String(options.repeat)],
    { maxBuffer: 64 * 1024 * 1024 }).toString());
    const nativeBytes = Buffer.from(bridged.png, 'base64');
    if (sha(nativeBytes) !== bridged.provenance.pngSha256 || sha(nativeBytes) !== g1.native.pngSha256) {
      throw new Error(`${id}: native bridge returned a different PNG from G1's sheet`);
    }
    const native = decodePng(nativeBytes);
    const preImage = decodePng(readFileSync(pre.png));
    const nowImage = decodePng(readFileSync(now.png));
    const title = `W41 G2 / w39 ${g1.role} / ${example.profileKey} / ${example.sceneId}`;
    const html = sheetHtml(title, native, preImage, nowImage, [
      `native: W39 archive via G1 native.py, repeat ordinal ${options.repeat}, png sha256 ${sha(nativeBytes)}`,
      `pre-W41: ${pre.png} sha256 ${pre.pngSha256}`, `now (E3): ${now.png} sha256 ${now.pngSha256}`,
      `pose: ${now.pose.join(', ')}; sampling ${now.samplingBackend}`,
    ]);
    const name = `w39__${encodeURIComponent(example.profileKey)}__${encodeURIComponent(example.sceneId)}`;
    records.push({ bed: 'w39', ...example, role: g1.role, status: 'RENDERED', pose: now.pose,
      native: { source: 'G1 native.py (Reader.read, cal/val roles)', repeat: options.repeat,
        pngSha256: sha(nativeBytes), cropSha256: bridged.provenance.cropSha256, generation: nativeGeneration },
      pre: { png: pre.png, pngSha256: pre.pngSha256, cellSha256: pre.cellSha256, documents: pre.documents },
      now: { png: now.png, pngSha256: now.pngSha256, cellSha256: now.cellSha256, documents: now.documents },
      preEqualsNowBytes: pre.pngSha256 === now.pngSha256, preEqualsNowPixels: pixelsEqual(preImage, nowImage),
      g1Sheet: { html: g1.html, htmlSha256: g1.htmlSha256, png: g1.png, pngSha256: g1.pngSha256 },
      distances: distances(native, preImage, nowImage),
      ...writeSheet(options.outputRoot, name, html) });
  }
  return records;
}

const load = (path: string) => JSON.parse(readFileSync(path, 'utf8'));
export function g1Inventory(pin: { gzip: string; sha256: string }) {
  const raw = gunzipSync(readFileSync(pin.gzip));
  if (sha(raw) !== pin.sha256) throw new Error('G1 sheet inventory does not decompress to its pinned hash');
  const inventory = JSON.parse(raw.toString('utf8'));
  const records = Object.fromEntries((inventory.records as any[]).filter(r => r.bed === 'w39')
    .map(r => [`${r.profileKey}/${r.sceneId}`, r]));
  return { records, nativeGeneration: inventory.nativeGeneration as string };
}

/** run.json names every input; the command writes a fresh scratch run directory and its inventory. */
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [command, config] = process.argv.slice(2);
  if (!config || !['canonical', 'w39'].includes(command!)) throw new Error('usage: sheets.ts canonical|w39 <run.json>');
  const options = load(config);
  const started = new Date().toISOString();
  if (command === 'canonical') {
    const result = renderCanonical(options);
    const count = (status: string) => result.records.filter(r => r.status === status).length;
    const rendered = result.records.filter(r => r.status === 'RENDERED') as any[];
    const inactive = (r: any) => /__inactive/.test(r.sceneId);
    const report = { schema: 'w41-g2-canonical-sheets-1', started, completed: new Date().toISOString(),
      options, membershipSha256: sha(readFileSync(options.membership)), holdoutPixelsOpened: 0,
      browserOrCaptureStarted: false,
      summary: { declaredWebgpu: result.declaredWebgpu, holdoutNotOpened: result.holdoutNotOpened,
        admitted: result.records.length, rendered: count('RENDERED'), renderedNowOnly: count('RENDERED-NOW-ONLY'),
        notCaptured: count('NOT-CAPTURED'), noNative: count('NO-NATIVE'),
        activeControls: rendered.filter(r => !inactive(r)).length,
        activeControlsIdentical: rendered.filter(r => !inactive(r) && r.preEqualsNowBytes).length,
        activeControlsPixelIdentical: rendered.filter(r => !inactive(r) && r.preEqualsNowPixels).length,
        receded: rendered.filter(inactive).length,
        recededIdentical: rendered.filter(r => inactive(r) && r.preEqualsNowBytes).length,
        g1DiagnosticCells: result.records.filter((r: any) => r.g1Diagnostic).length,
        g1DiagnosticIdentical: result.records.filter((r: any) => r.g1Diagnostic?.identicalToNow).length },
      records: result.records };
    writeFileSync(join(options.outputRoot, 'inventory.json'), JSON.stringify(report, null, 1) + '\n', { flag: 'wx' });
    console.log(JSON.stringify(report.summary, null, 1));
  } else {
    const declaration = load(resolve(HERE, 'examples-declaration.json'));
    const examples = (declaration.examples as any[]).filter(e => e.bed === 'w39')
      .map(e => ({ profileKey: e.profileKey, sceneId: e.sceneId }));
    freshOutput(options.outputRoot);
    const { records, nativeGeneration } = g1Inventory(options.g1Inventory);
    const rendered = renderW39({ ...options, examples }, records, nativeGeneration);
    const report = { schema: 'w41-g2-w39-example-sheets-1', started, completed: new Date().toISOString(),
      options, nativeGeneration, holdoutOrBlindPixelsOpened: 0, records: rendered };
    writeFileSync(join(options.outputRoot, 'inventory.json'), JSON.stringify(report, null, 1) + '\n', { flag: 'wx' });
    console.log(JSON.stringify(rendered.map(r => ({ id: `${r.profileKey}/${r.sceneId}`, distances: r.distances,
      preEqualsNowBytes: r.preEqualsNowBytes })), null, 1));
  }
}
