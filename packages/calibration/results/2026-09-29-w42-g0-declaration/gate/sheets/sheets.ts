/** W42 G0 gate: the standing eye sheets chosen BY STRATUM (charter clause 10; X33, X34).
 *
 * Clause 10 asks for eye sheets over six strata (uniform, binary structure, text, impulse,
 * photo, gradient), each showing native | shipped | candidate with OKLab ΔE × 8. This module
 * extends W41 G2's adapter (§5.193) to that membership. It keeps W41 G0's fixed 2 × 3 table,
 * so G0's export-png.py draws the sheet unchanged, and it reuses G0's difference panel and
 * capture inspection, G2's bounded exporter and G1's pinned W39 sheet inventory.
 *
 * Membership is a declaration (strata.json). It is resolved from scenes.json, the W39 wave's
 * split and web plan, and the generation index's current documents, and `render` refuses a
 * declaration that no longer resolves to itself. A canonical cell's role is read from
 * scenes.json before any path is formed, and a holdout cell is dropped there, so no holdout
 * fixture or capture is ever stat'ed or opened. No stratum admits a recorded cell. W39 natives
 * come only through W41 G1's guarded bridge (native.py: Reader.read over calibration/validation)
 * and must hash to the PNG G1's sheet recorded for that cell.
 *
 * Read-only toward evidence: no browser, no capture, no matrix, generation, profile or fixture
 * write. Output goes to a fresh directory outside every git work tree. The per-cell OKLab
 * distances are a diagnostic beside the eye, never a referee.
 */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, isAbsolute, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';
import { canonicalRole, differencePanel, inspectCell, type Cell }
  from '../../../2026-09-27-w41-g0-declaration/sheets/sheets';
import { exportPng, g1Inventory } from '../../../2026-09-29-w41-g2-landing/sheets/sheets';
import { linearRgbToOklab } from '../../../../src/color';
import { componentRegion, type DeclaredComponent } from '../../../../src/component-region';
import { decodePng, toLinearRgb, type CalibrationImage } from '../../../../src/image';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(HERE, '../../../../../..');
const W39_WAVE = 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/wave.py';
const W39_SCENES = 'apps/reference-apple/scenes-w39-colour-edge.json';
const G1_NATIVE = resolve(HERE, '../../../2026-09-27-w41-g1-identification/sheets/native.py');
const GENERATIONS = 'packages/calibration/results/generations';
export const sha = (b: Uint8Array | string) => createHash('sha256').update(b).digest('hex');
const load = (path: string) => JSON.parse(readFileSync(path, 'utf8'));

export interface Document { kind: string; path: string; sha256: string }
export type StratumName = 'uniform' | 'binary' | 'text' | 'impulse' | 'photo' | 'gradient';
export interface StratumCell {
  profileKey: string; sceneId: string; role: string; pose: string; tint: string | null;
}
export interface Stratum {
  bed: 'canonical' | 'w39'; rule: string; roles: string[]; backgroundKind: string;
  backgrounds: string[]; tinted: string; excludedByRole: Record<string, number>;
  excludedByPlan?: Record<string, string>; noCurrentRow: string[]; cells: StratumCell[];
}
export interface Strata {
  schema: string; charter: string; tier: 'webgpu'; profiles: string[];
  inputs: Record<string, string>; shippedDocuments: Record<string, Document[]>;
  sources: typeof SOURCES; strata: Record<StratumName, Stratum>;
}

/** The four gated standard macOS 27 profiles clause 10 reads, both scales and schemes. */
export const PROFILES = ['apple-macos-27.0-1x-light-standard-glass0.5',
  'apple-macos-27.0-2x-light-standard-glass0.5', 'apple-macos-27.0-1x-dark-standard-glass0.5',
  'apple-macos-27.0-2x-dark-standard-glass0.5'];
const CAL_VAL = ['calibration', 'validation'];

/** The rules. Each is a background kind and the roles it admits; the cells are resolved. */
export const RULES: Record<StratumName, { bed: 'canonical' | 'w39'; backgroundKind: string;
  roles: string[]; rule: string; tinted: string }> = {
  uniform: { bed: 'canonical', backgroundKind: 'solid', roles: CAL_VAL,
    rule: 'canonical scenes over a solid backdrop (light-solid, dark-solid, mid-dark-solid, ' +
      'mid-light-solid, mid-chroma-solid) in the calibration or validation split. The mid-* ' +
      'solids resolve to no cell: mid-dark-solid capsule rest/inactive are holdout and every ' +
      'other mid-* scene is probe.',
    tinted: 'included (orange, both poses). Every declared family maps a constant backdrop to ' +
      'itself (clause 7), and the spatial operators sit before the tint composition, so a tinted ' +
      'solid shows whatever the candidate changes in T or at the edge under the tint too.' },
  binary: { bed: 'canonical', backgroundKind: 'checkerboard', roles: CAL_VAL,
    rule: 'canonical scenes over a two-level checkerboard in the calibration or validation ' +
      'split. Only `checkerboard` (16 px, 0/255) resolves: checkerboard-4/-8/-32/-64 and lc16 ' +
      'are probe, and rrect-lg and glass-over-glass are holdout.',
    tinted: 'included (orange and blue, both poses). The one-sided composite meets the tint ' +
      'composition here, and L1 reads every inactive checkerboard cell, tinted ones included.' },
  text: { bed: 'canonical', backgroundKind: 'text-rows', roles: ['probe'],
    rule: 'the canonical PROBE cells over hc-text, hc-text-7 and hc-text-28. Probe cells are ' +
      'calibration evidence that memo C read (X34): a look, never a referee. The hc-text ' +
      'capsule-button and rrect-md cells are holdout and excluded by role.',
    tinted: 'none exist: the only tinted text scenes (hc-text capsule, orange) are holdout.' },
  impulse: { bed: 'canonical', backgroundKind: 'impulse', roles: CAL_VAL,
    rule: 'canonical scenes over the impulse backdrop in the calibration or validation split; ' +
      'impulse rrect-sm/-ml/-lg are probe.',
    tinted: 'included (orange, both poses): L1\'s two named misses are the light inactive ' +
      'tinted-impulse cells.' },
  photo: { bed: 'canonical', backgroundKind: 'synthetic-photo', roles: CAL_VAL,
    rule: 'canonical scenes over the synthetic photo in the calibration or validation split; ' +
      'rrect-lg, its tint and glass-over-glass are holdout, pressed cells are recorded, ' +
      'photo rrect-ml inactive is probe.',
    tinted: 'included (orange, blue, orange-half, both poses): W41\'s E3 failed M2 on every ' +
      'light-inactive photo cell and its L1 growth reading includes the tinted photo inactive ' +
      'cells (§5.193 §3).' },
  gradient: { bed: 'w39', backgroundKind: 'linear-gradient', roles: CAL_VAL,
    rule: 'the W39 archive\'s web-plannable gradient cells: W39 scenes over v90/v270 in its ' +
      'calibration or validation split that its launch plan admits (the cells W41 G1 ' +
      'rendered), in the four gated profiles. A look, not a referee.',
    tinted: 'none exist: the W39 bed has no tinted gradient scene.' },
};

/** What each column is, declared with the document pair it names. */
export const SOURCES = {
  canonical: {
    native: 'the committed fixture apps/reference-apple/fixtures/<profileKey>/<sceneId>.png, ' +
      'opened only after scenes.json gives the scene a role its stratum admits',
    shipped: 'the canonical capture tree (the capture machine\'s packages/calibration/web-captures ' +
      'in the main checkout); every capture must name exactly the shippedDocuments pair of its ' +
      'profile. It was measured at the base of the generation it belongs to; clause 8 proves ' +
      'byte identity at G2\'s base on a declared sample before any candidate render.',
    candidate: 'the candidate\'s scratch stage capture tree, every capture naming exactly the ' +
      'candidate documents the run config declares for its profile',
  },
  gradient: {
    native: 'the W39 archive (release w39-archive; cache 489db938…/extracted/archive) through ' +
      'W41 G1\'s native.py, repeat ordinal 0, native generation 58329732…; the PNG must hash to ' +
      'the one G1\'s sheet recorded (render-inventory.json.gz, primary SHA-256 f52dbcb0…)',
    shipped: 'W41 G1\'s frozen baseline (/Users/new/vitrea-w41/g1-captures/baseline; ' +
      'frozen-baseline.json c921d671…, source revision 014e4104). All 16 captures name the ' +
      'shipped pairs, light 85ad7f7e3e0d / 30fbe05986ae and dark 0eac5b294cc2 / 5cec8c961201. ' +
      'W41 G2\'s identity capture re-rendered 12 of them byte-identically at its own base (the ' +
      '8 dark and the 4 light active); the 4 light inactive are attested at G1\'s base only, ' +
      'because G2\'s identity capture named E3 (003940b4c7da), which did not ship.',
    candidate: 'the candidate\'s render of the same 16 W39 cells, naming the declared candidate ' +
      'documents',
  },
};

const splitRoles = (spec: any) => {
  const roles = new Map<string, string>();
  for (const role of ['calibration', 'validation', 'holdout', 'recorded', 'probe']) {
    for (const id of spec.split?.[role] ?? []) {
      if (roles.has(id)) throw new Error(`${id}: canonical split role is ambiguous`);
      roles.set(id, role);
    }
  }
  return roles;
};

/** The generation index's current selection: documents per profile and each current WebGPU row's
 * capturePath, the latter only to record whether a shipped capture is the one a row names. */
export function currentState(repositoryRoot: string) {
  const index = load(join(repositoryRoot, GENERATIONS, 'index.json'));
  const documents: Record<string, Document[]> = {};
  const rows = new Map<string, string>();
  const read = new Map<string, any>();
  for (const profileKey of PROFILES) {
    const file = index.currentByProfile?.[profileKey];
    const entry = file && index.files?.[file];
    if (!entry || entry.status !== 'current') throw new Error(`${profileKey}: no current generation`);
    documents[profileKey] = (entry.documents as { path: string; sha256: string }[]).map(d => ({
      kind: d.path.endsWith('-receded.json') ? 'recededProfile' : 'materialProfile',
      path: d.path, sha256: d.sha256 })).sort((a, b) => a.kind.localeCompare(b.kind));
    if (!read.has(file)) {
      const bytes = readFileSync(join(repositoryRoot, GENERATIONS, file));
      if (sha(bytes) !== entry.sha256) throw new Error(`${file}: bytes differ from the index`);
      read.set(file, JSON.parse(bytes.toString('utf8')));
    }
  }
  for (const generation of read.values()) {
    for (const row of generation.cells) {
      if (row.key.web.renderer === 'webgpu') {
        rows.set(`${row.key.profileKey}/${row.key.sceneId}`, row.key.web.capturePath);
      }
    }
  }
  return { documents, rows };
}

/** W39's own plan over calibration/validation (the constructor and launch_plan only, never a
 * Reader), narrowed to gradient scenes; holdout never enters select(). */
export function w39GradientPlan(repositoryRoot: string) {
  const script = `import importlib.util,json,sys
s=importlib.util.spec_from_file_location('w42_gate_wave',sys.argv[1])
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.default_wave(); ids,excluded=w.launch_plan(('calibration','validation'))
kind={k:v['kind'] for k,v in w.spec['backgrounds'].items()}
grad={sid for sid,sc in w.scenes.items() if kind[sc['background']]==sys.argv[2]}
print(json.dumps(dict(scenesSha256=w.scenes_sha,splitSha256=w.split_sha,
 cells=[dict(profileKey=p,sceneId=sid,role=w.roles[sid],pose=w.scenes[sid].get('state'),
  tint=w.scenes[sid].get('tint')) for sid in ids if sid in grad for p in sorted(w.profiles_of[sid])],
 excluded={sid:r for sid,r in sorted(excluded.items()) if sid in grad},
 holdout=sorted(sid for sid in grad if w.roles[sid]=='holdout'),
 backgrounds=sorted({w.scenes[sid]['background'] for sid in grad}))))`;
  return JSON.parse(execFileSync('python3.12', ['-B', '-c', script, join(repositoryRoot, W39_WAVE),
    RULES.gradient.backgroundKind], { encoding: 'utf8' })) as {
    scenesSha256: string; splitSha256: string; cells: StratumCell[]; excluded: Record<string, string>;
    holdout: string[]; backgrounds: string[] };
}

/** Resolve every rule. Reads scenes.json, W39 metadata and the generation index; forms no
 * capture or fixture path. */
export function resolveStrata(repositoryRoot = ROOT, gradient = w39GradientPlan(repositoryRoot)): Strata {
  const scenesBytes = readFileSync(join(repositoryRoot, 'apps/reference-apple/scenes.json'));
  const spec = JSON.parse(scenesBytes.toString('utf8'));
  const roles = splitRoles(spec);
  const scenes = new Map<string, any>(spec.scenes.map((s: any) => [s.id, s]));
  const members = new Map<string, string[]>(spec.profiles.map((p: any) => [p.key, p.scenes]));
  const current = currentState(repositoryRoot);
  const strata = {} as Record<StratumName, Stratum>;
  for (const [name, rule] of Object.entries(RULES) as [StratumName, typeof RULES[StratumName]][]) {
    const noRow = (c: StratumCell) => !current.rows.has(`${c.profileKey}/${c.sceneId}`);
    if (rule.bed === 'w39') {
      const cells = gradient.cells.filter(c => PROFILES.includes(c.profileKey))
        .map(c => ({ profileKey: c.profileKey, sceneId: c.sceneId, role: c.role, pose: c.pose,
          tint: c.tint ?? null }));
      strata[name] = { bed: 'w39', rule: rule.rule, roles: rule.roles, backgroundKind: rule.backgroundKind,
        backgrounds: gradient.backgrounds, tinted: rule.tinted,
        excludedByRole: { holdout: gradient.holdout.length }, excludedByPlan: gradient.excluded,
        noCurrentRow: [], cells };
      continue;
    }
    const cells: StratumCell[] = [];
    const excludedByRole: Record<string, number> = {};
    const backgrounds = new Set<string>();
    for (const profileKey of PROFILES) {
      for (const sceneId of members.get(profileKey) ?? []) {
        const scene = scenes.get(sceneId);
        if (spec.backgrounds[scene.background]?.kind !== rule.backgroundKind) continue;
        const role = roles.get(sceneId);
        if (!role) throw new Error(`${sceneId}: no canonical split role`);
        if (!rule.roles.includes(role)) {
          excludedByRole[role] = (excludedByRole[role] ?? 0) + 1;
          continue;
        }
        backgrounds.add(scene.background);
        cells.push({ profileKey, sceneId, role, pose: scene.state, tint: scene.tint ?? null });
      }
    }
    strata[name] = { bed: 'canonical', rule: rule.rule, roles: rule.roles,
      backgroundKind: rule.backgroundKind, backgrounds: [...backgrounds].sort(), tinted: rule.tinted,
      excludedByRole, noCurrentRow: cells.filter(noRow).map(c => `${c.profileKey}/${c.sceneId}`), cells };
  }
  return { schema: 'w42-g0-gate-strata-1',
    charter: 'docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md clause 10; X33, X34',
    tier: 'webgpu', profiles: PROFILES,
    inputs: { 'apps/reference-apple/scenes.json': sha(scenesBytes),
      [W39_SCENES]: gradient.scenesSha256,
      'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/split.json': gradient.splitSha256 },
    shippedDocuments: current.documents, sources: SOURCES, strata };
}

// ---------------------------------------------------------------------------------------------

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
export const LABELS = { native: 'Native', shipped: 'Shipped', candidate: 'Candidate',
  shippedDelta: 'Shipped ΔE × 8', candidateDelta: 'Candidate ΔE × 8' };

/** W41 G0's fixed 2 × 3 table (the exporter refuses any other shape), clause 10's columns. */
export function sheetHtml(title: string, native: CalibrationImage, shipped: CalibrationImage | undefined,
  candidate: CalibrationImage | undefined, notes: string[],
  missing = { shipped: 'UNMEASURED', candidate: 'UNMEASURED' }): string {
  for (const image of [shipped, candidate]) {
    if (image && (image.width !== native.width || image.height !== native.height)) {
      throw new Error(`${title}: image dimensions differ`);
    }
  }
  const panel = (image: CalibrationImage | undefined, label: string, absent: string) =>
    `<td><h2>${escape(label)}</h2>${image ? imageTag(image, label) : `<p>${escape(absent)}</p>`}</td>`;
  const delta = (web: CalibrationImage | undefined) => web && differencePanel(native, web);
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>${escape(title)}</title>
<style>body{font:14px system-ui;color:#111;background:white;margin:24px}table{border-spacing:8px}
 td{vertical-align:top;border:1px solid #aaa;padding:8px}h2{font-size:16px}img{display:block}
 code{overflow-wrap:anywhere}p{max-width:100ch}</style><h1>${escape(title)}</h1>
<p>ΔE × 8: OKLab distance; black = 0, white = 0.125 or greater (clipped). Original pixel dimensions.</p>
<table aria-label="Native and WebGPU comparison"><tr>${panel(native, LABELS.native, '')}
${panel(shipped, LABELS.shipped, missing.shipped)}${panel(candidate, LABELS.candidate, missing.candidate)}</tr>
<tr><td>Difference from native</td>${panel(delta(shipped), LABELS.shippedDelta, missing.shipped)}
${panel(delta(candidate), LABELS.candidateDelta, missing.candidate)}</tr></table>
${notes.map(note => `<p><code>${escape(note)}</code></p>`).join('\n')}</html>`;
}

/** Whole-body and whole-frame mean OKLab distance to native, per web column. The body is the
 * declared region (componentRegion, pixel-centre containment, no margin); `moved` counts body
 * pixels whose RGBA differs between shipped and candidate, `closerFraction` the share of those
 * where the candidate is nearer native. A diagnostic beside the eye, not a referee. */
export function bodyDistances(native: CalibrationImage, body: Uint8Array,
  shipped: CalibrationImage | undefined, candidate: CalibrationImage | undefined) {
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
  const distance = (other: Float64Array, i: number) => Math.hypot(reference[i * 3]! - other[i * 3]!,
    reference[i * 3 + 1]! - other[i * 3 + 1]!, reference[i * 3 + 2]! - other[i * 3 + 2]!);
  const s = shipped && lab(shipped);
  const c = candidate && lab(candidate);
  let bodyPixels = 0, bodyS = 0, bodyC = 0, frameS = 0, frameC = 0, moved = 0, closer = 0;
  for (let i = 0; i < n; i++) {
    const ds = s ? distance(s, i) : 0, dc = c ? distance(c, i) : 0;
    frameS += ds; frameC += dc;
    if (!body[i]) continue;
    bodyPixels += 1; bodyS += ds; bodyC += dc;
    if (!shipped || !candidate) continue;
    const differs = [0, 1, 2, 3].some(k => shipped.data[i * 4 + k] !== candidate.data[i * 4 + k]);
    if (differs) { moved += 1; if (dc < ds) closer += 1; }
  }
  const round = (x: number) => Math.round(x * 1e6) / 1e6;
  const column = (on: unknown, bodySum: number, frameSum: number) => on
    ? { bodyMeanDeltaE: round(bodySum / bodyPixels), frameMeanDeltaE: round(frameSum / n) } : null;
  return { bodyPixels, framePixels: n, shipped: column(s, bodyS, frameS), candidate: column(c, bodyC, frameC),
    ...(s && c ? { bodyCandidateMinusShipped: round((bodyC - bodyS) / bodyPixels), bodyMovedPixels: moved,
      bodyCloserFraction: moved ? round(closer / moved) : null } : {}) };
}

/** Refuse any output that is relative, already exists, or lies inside a git work tree. */
export function freshOutsideRepositories(outputRoot: string, repositoryRoot = ROOT) {
  if (!isAbsolute(outputRoot)) throw new Error('outputRoot must be absolute');
  const target = resolve(outputRoot);
  if (existsSync(target)) throw new Error('outputRoot must be a fresh directory');
  const rel = relative(resolve(repositoryRoot), target);
  if (rel === '' || (!rel.startsWith('..') && !isAbsolute(rel))) throw new Error('outputRoot is inside the repository');
  let ancestor = dirname(target);
  while (!existsSync(ancestor)) ancestor = dirname(ancestor);
  let inside = false;
  try {
    inside = execFileSync('git', ['-C', ancestor, 'rev-parse', '--is-inside-work-tree'],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim() === 'true';
  } catch { inside = false; }
  if (inside) throw new Error('outputRoot is inside a git work tree');
  mkdirSync(target, { recursive: true });
}

const scaleOf = (profileKey: string) => Number(/-(\d)x-/.exec(profileKey)?.[1] ?? NaN);
const schemeOf = (profileKey: string) => /-(light|dark)-/.exec(profileKey)?.[1] ?? '';
const poseOf = (profileKey: string) => [`deviceScaleFactor=${scaleOf(profileKey)}`,
  `colorScheme=${schemeOf(profileKey)}`, 'accessibility=browser-preferences'];

/** W39 declares a position; componentRegion centres and then offsets. */
function declaredComponent(spec: any, sceneId: string): DeclaredComponent {
  const scene = spec.scenes.find((s: any) => s.id === sceneId);
  const component = scene && spec.components[scene.component];
  if (!component) throw new Error(`${sceneId}: no declared component`);
  if (!component.position) return component;
  const { position, ...rest } = component;
  return { ...rest, offset: [position[0] - spec.canvas.width / 2, position[1] - spec.canvas.height / 2] };
}

export interface BedRoots { shippedRoots: string[]; candidateRoot: string }
export interface RunConfig {
  label: string; outputRoot: string; strata?: string;
  candidateDocuments: Record<string, Document[]>;
  canonical: BedRoots;
  gradient?: BedRoots & { archiveRoot: string; repeat: number; g1Inventory: { gzip: string; sha256: string };
    shippedFreeze?: { path: string; sha256: string } };
}
export interface RenderDependencies {
  repositoryRoot?: string;
  /** Called with every capture directory and native path the adapter forms, before use. */
  onPath?: (path: string) => void;
}

interface Captured { root: string; png: string; pngSha256: string; cellSha256: string; capturePath: string;
  samplingBackend: string; documents: Document[]; image: CalibrationImage }

/** The first root holding a complete capture of the cell. A present capture naming any other
 * documents, scene, renderer or pose refuses (W41 G0's inspectCell); absent is undefined. */
function capture(roots: string[], cell: Cell, repositoryRoot: string,
  onPath: (p: string) => void): Captured | undefined {
  for (const root of roots) {
    onPath(join(root, cell.profileKey, cell.sceneId));
    const found = inspectCell(cell, repositoryRoot, root);
    if (found.status !== 'MATCH') continue;
    const metadata = readFileSync(found.metadataPath);
    const meta = JSON.parse(metadata.toString('utf8'));
    const bytes = readFileSync(found.pngPath);
    return { root, png: found.pngPath, pngSha256: sha(bytes), cellSha256: sha(metadata),
      capturePath: String(meta.capturePath), samplingBackend: String(meta.samplingBackend),
      documents: cell.documents, image: decodePng(bytes) };
  }
  return undefined;
}

function checkDocuments(docs: Document[], repositoryRoot: string, context: string) {
  if (docs.filter(d => d.kind === 'materialProfile').length !== 1 ||
      docs.filter(d => d.kind === 'recededProfile').length > 1 || docs.some(d => !/^[0-9a-f]{12}$/.test(d.sha256))) {
    throw new Error(`${context}: a document pair is one materialProfile, at most one recededProfile, 12-hex hashes`);
  }
  for (const doc of docs) {
    const path = resolve(repositoryRoot, doc.path);
    const rel = relative(resolve(repositoryRoot), path);
    if (rel.startsWith('..') || isAbsolute(rel)) throw new Error(`${context}: ${doc.path} escapes the repository`);
    if (!existsSync(path) || sha(readFileSync(path)).slice(0, 12) !== doc.sha256) {
      throw new Error(`${context}: no file holds ${doc.path} at ${doc.sha256}`);
    }
  }
  // inspectCell compares JSON signatures, so the key order is fixed here, not by the caller.
  return docs.map(d => ({ kind: d.kind, path: d.path, sha256: d.sha256 }))
    .sort((a, b) => a.kind.localeCompare(b.kind));
}

const pairOf = (docs: Document[]) => docs.map(d => `${d.kind}=${d.sha256}`).join(' / ');
const absolute = (repositoryRoot: string, path: string) => isAbsolute(path) ? path : resolve(repositoryRoot, path);

/** Render every declared cell of every stratum. Holdout is dropped on scenes.json's role before
 * any path is formed; a cell whose role its stratum does not admit refuses. */
export function renderRun(config: RunConfig, strata: Strata, dependencies: RenderDependencies = {}) {
  const repositoryRoot = dependencies.repositoryRoot ?? ROOT;
  const onPath = dependencies.onPath ?? (() => {});
  freshOutsideRepositories(config.outputRoot, repositoryRoot);
  const shippedDocs: Record<string, Document[]> = {};
  const candidateDocs: Record<string, Document[]> = {};
  for (const profileKey of strata.profiles) {
    shippedDocs[profileKey] = checkDocuments(strata.shippedDocuments[profileKey] ?? [], repositoryRoot,
      `shipped ${profileKey}`);
    candidateDocs[profileKey] = checkDocuments(config.candidateDocuments[profileKey] ?? [], repositoryRoot,
      `candidate ${profileKey}`);
  }
  const current = currentState(repositoryRoot);
  const canonicalSpec = load(join(repositoryRoot, 'apps/reference-apple/scenes.json'));
  let gradient: { records: Record<string, any>; nativeGeneration: string; freeze?: Record<string, any>;
    spec: any } | undefined;
  const records: any[] = [];
  const dropped: Record<string, number> = {};
  for (const [name, stratum] of Object.entries(strata.strata) as [StratumName, Stratum][]) {
    mkdirSync(join(config.outputRoot, name));
    dropped[name] = 0;
    if (!stratum.cells.length) continue;
    const bed = stratum.bed === 'w39' ? config.gradient : config.canonical;
    if (!bed) throw new Error(`${name}: the run config names no roots for its bed`);
    if (stratum.bed === 'w39' && !gradient) {
      const g = config.gradient!;
      const inventory = g1Inventory({ gzip: absolute(repositoryRoot, g.g1Inventory.gzip),
        sha256: g.g1Inventory.sha256 });
      let freeze: Record<string, any> | undefined;
      if (g.shippedFreeze) {
        const bytes = readFileSync(absolute(repositoryRoot, g.shippedFreeze.path));
        if (sha(bytes) !== g.shippedFreeze.sha256) throw new Error('gradient shipped freeze hash differs');
        freeze = JSON.parse(bytes.toString('utf8')).captures;
      }
      gradient = { ...inventory, ...(freeze ? { freeze } : {}), spec: load(join(repositoryRoot, W39_SCENES)) };
    }
    const plan = stratum.bed === 'w39' ? w39GradientPlan(repositoryRoot) : undefined;
    const planned = new Map<string, string>(plan?.cells.map(c => [`${c.profileKey}/${c.sceneId}`, c.role] as const));
    for (const declared of stratum.cells) {
      const id = `${declared.profileKey}/${declared.sceneId}`;
      const role = stratum.bed === 'w39'
        ? (plan!.holdout.includes(declared.sceneId) ? 'holdout' : planned.get(id))
        : canonicalRole(declared.sceneId, repositoryRoot);
      if (role === 'holdout') { dropped[name] += 1; continue; }
      if (!role || role !== declared.role || !stratum.roles.includes(role)) {
        throw new Error(`${name} ${id}: role ${role ?? '(not planned)'} is not the declared ${declared.role}`);
      }
      if (!strata.profiles.includes(declared.profileKey)) throw new Error(`${id}: undeclared profile`);
      const base = { bed: stratum.bed, profileKey: declared.profileKey, sceneId: declared.sceneId };
      const pose = poseOf(declared.profileKey);
      const shipped = capture(bed.shippedRoots, { ...base, documents: shippedDocs[declared.profileKey]!, pose },
        repositoryRoot, onPath);
      const candidate = capture([bed.candidateRoot], { ...base, documents: candidateDocs[declared.profileKey]!,
        pose }, repositoryRoot, onPath);
      if (shipped && candidate && shipped.samplingBackend !== candidate.samplingBackend) {
        throw new Error(`${id}: shipped and candidate sampling backends differ`);
      }
      const describe = (c: Captured) => ({ root: c.root, png: c.png, pngSha256: c.pngSha256,
        cellSha256: c.cellSha256, documents: c.documents, samplingBackend: c.samplingBackend });
      const rowOf = (c: Captured) => !current.rows.has(id) ? 'absent'
        : current.rows.get(id) === c.capturePath ? 'names-this-capture' : 'names-another-capture';
      const record: any = { stratum: name, ...base, role, pose: declared.pose, tint: declared.tint };
      if (shipped) {
        record.shipped = { ...describe(shipped),
          ...(stratum.bed === 'canonical' ? { currentRow: rowOf(shipped) } : {}) };
      }
      if (candidate) record.candidate = describe(candidate);
      let nativeBytes: Buffer | undefined;
      if (stratum.bed === 'canonical') {
        const path = join(repositoryRoot, 'apps/reference-apple/fixtures', declared.profileKey,
          `${declared.sceneId}.png`);
        onPath(path);
        if (existsSync(path) && statSync(path).isFile()) {
          nativeBytes = readFileSync(path);
          record.native = { source: 'committed fixture', path: relative(repositoryRoot, path),
            pngSha256: sha(nativeBytes) };
        }
      } else {
        const g = config.gradient!;
        const g1 = gradient!.records[id];
        if (!g1 || g1.status !== 'RENDERED' || !CAL_VAL.includes(g1.role)) {
          throw new Error(`${id}: not an admitted G1 W39 sheet`);
        }
        if (gradient!.freeze && shipped) {
          const entry = gradient!.freeze[id];
          if (!entry || resolve(entry.png) !== resolve(shipped.png) || entry.pngSha256 !== shipped.pngSha256) {
            throw new Error(`${id}: the gradient shipped capture is not the one its freeze names`);
          }
        }
        onPath(`w39-native:${id}`);
        const bridged = JSON.parse(execFileSync('python3.12', ['-B', G1_NATIVE, '--archive-root', g.archiveRoot,
          '--generation', gradient!.nativeGeneration, '--cell', id, '--repeat', String(g.repeat)],
        { maxBuffer: 64 * 1024 * 1024 }).toString());
        nativeBytes = Buffer.from(bridged.png, 'base64');
        if (sha(nativeBytes) !== bridged.provenance.pngSha256 || sha(nativeBytes) !== g1.native.pngSha256) {
          throw new Error(`${id}: the native bridge returned a different PNG from G1's sheet`);
        }
        record.native = { source: 'W39 archive via W41 G1 native.py (Reader.read, cal/val roles)',
          repeat: g.repeat, generation: gradient!.nativeGeneration, cropSha256: bridged.provenance.cropSha256,
          pngSha256: sha(nativeBytes) };
      }
      if (!nativeBytes) { records.push({ ...record, status: 'NO-NATIVE' }); continue; }
      if (!shipped && !candidate) {
        records.push({ ...record, status: 'NOT-RENDERED',
          reason: 'no shipped root holds a capture at the shipped pair and the candidate tree holds none' });
        continue;
      }
      const native = decodePng(nativeBytes);
      const spec = stratum.bed === 'w39' ? gradient!.spec : canonicalSpec;
      const region = componentRegion(declaredComponent(spec, declared.sceneId), { canvas: spec.canvas,
        scale: scaleOf(declared.profileKey), width: native.width, height: native.height });
      const { profileKey, sceneId } = declared;
      const title = `W42 gate / ${name} / ${stratum.bed} ${role} / ${profileKey} / ${sceneId}`;
      const column = (c: Captured | undefined, absent: string) => c ? `${c.png} sha256 ${c.pngSha256}` : absent;
      const nativeName = record.native.path ?? `W39 ${id}, repeat ordinal ${config.gradient?.repeat}`;
      const html = sheetHtml(title, native, shipped?.image, candidate?.image, [
        `native: ${nativeName} sha256 ${record.native.pngSha256}`,
        `shipped (${pairOf(shippedDocs[profileKey]!)}): ${column(shipped, 'no capture at the shipped pair')}`,
        `candidate "${config.label}" (${pairOf(candidateDocs[profileKey]!)}): ${column(candidate, 'no capture')}`,
        `pose: ${poseOf(profileKey).join(', ')}; sampling ${(shipped ?? candidate)!.samplingBackend}`,
      ], { shipped: 'UNMEASURED: no capture at the shipped pair', candidate: 'UNMEASURED: no candidate capture' });
      const stem = `${encodeURIComponent(declared.profileKey)}__${encodeURIComponent(declared.sceneId)}`;
      const htmlPath = join(config.outputRoot, name, `${stem}.html`);
      writeFileSync(htmlPath, html, { flag: 'wx' });
      const pngSha256 = exportPng(htmlPath, join(config.outputRoot, name, `${stem}.png`));
      records.push({ ...record,
        status: shipped && candidate ? 'RENDERED' : shipped ? 'RENDERED-SHIPPED-ONLY' : 'RENDERED-CANDIDATE-ONLY',
        candidateEqualsShippedBytes: shipped && candidate ? shipped.pngSha256 === candidate.pngSha256 : null,
        distances: bodyDistances(native, region.silhouette.mask, shipped?.image, candidate?.image),
        sheet: { html: `${name}/${stem}.html`, htmlSha256: sha(html), png: `${name}/${stem}.png`, pngSha256 } });
    }
  }
  return { records, dropped, shippedDocs, candidateDocs };
}

// ---------------------------------------------------------------------------------------------

const fmt = (x: number | null | undefined) => x === null || x === undefined ? '—' : x.toFixed(4);

/** One page per stratum: the rule, a table of every declared cell, and the sheets themselves. */
export function stratumIndex(name: StratumName, stratum: Stratum, records: any[], dropped: number, label: string) {
  const rows = records.map((r, i) => `<tr><td>${i + 1}</td><td>${escape(r.profileKey)}</td>
<td>${escape(r.sceneId)}</td><td>${escape(r.role)}</td><td>${escape(r.pose)}</td><td>${escape(r.tint ?? '')}</td>
<td>${escape(r.status)}</td><td>${fmt(r.distances?.shipped?.bodyMeanDeltaE)}</td>
<td>${fmt(r.distances?.candidate?.bodyMeanDeltaE)}</td><td>${fmt(r.distances?.bodyCandidateMinusShipped)}</td>
<td>${r.distances?.bodyMovedPixels ?? '—'}</td>
<td>${r.sheet ? `<a href="${escape(r.sheet.html.slice(name.length + 1))}">sheet</a>` : escape(r.reason ?? '')}</td></tr>`);
  const figures = records.filter(r => r.sheet).map(r => `<figure><figcaption>${escape(r.profileKey)} / ` +
    `${escape(r.sceneId)}</figcaption><a href="${escape(r.sheet.html.slice(name.length + 1))}">` +
    `<img alt="${escape(r.sceneId)}" style="max-width:100%" loading="lazy" ` +
    `src="${escape(r.sheet.png.slice(name.length + 1))}"></a></figure>`);
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>W42 gate eye sheets / ${name}</title>
<style>body{font:14px system-ui;color:#111;background:white;margin:24px}table{border-collapse:collapse}
 td,th{border:1px solid #aaa;padding:4px 6px;text-align:left}p{max-width:110ch}figure{margin:24px 0}</style>
<h1>W42 gate eye sheets / ${name}</h1>
<p>${escape(stratum.rule)}</p><p>Tinted: ${escape(stratum.tinted)}</p>
<p>Candidate: ${escape(label)}. Declared cells ${stratum.cells.length}; holdout dropped unopened ${dropped};
sheets ${records.filter(r => r.sheet).length}. Body ΔE is the mean OKLab distance to native over the declared
body region: a diagnostic beside the eye, not a referee.</p>
<table><tr><th>#</th><th>profile</th><th>scene</th><th>role</th><th>pose</th><th>tint</th><th>status</th>
<th>body ΔE shipped</th><th>body ΔE candidate</th><th>candidate − shipped</th><th>body px moved</th><th></th></tr>
${rows.join('\n')}</table>
${figures.join('\n')}</html>`;
}

function summarise(records: any[], stratum: Stratum, dropped: number) {
  const count = (status: string) => records.filter(r => r.status === status).length;
  const both = records.filter(r => r.status === 'RENDERED');
  const deltas = both.map(r => r.distances.bodyCandidateMinusShipped as number);
  return { declared: stratum.cells.length, holdoutDroppedUnopened: dropped, rendered: count('RENDERED'),
    renderedShippedOnly: count('RENDERED-SHIPPED-ONLY'), renderedCandidateOnly: count('RENDERED-CANDIDATE-ONLY'),
    notRendered: count('NOT-RENDERED'), noNative: count('NO-NATIVE'),
    candidateEqualsShippedBytes: both.filter(r => r.candidateEqualsShippedBytes).length,
    bodyFartherThanShipped: deltas.filter(d => d > 0).length,
    maxBodyCandidateMinusShipped: deltas.length ? Math.max(...deltas) : null,
    shippedRowNamesAnotherCapture: records.filter(r => r.shipped?.currentRow === 'names-another-capture').length };
}

/** `declare <strata.json>` writes the resolved declaration (refusing to overwrite);
 * `check [<strata.json>]` exits 1 unless it still resolves to itself;
 * `render <run.json>` checks the declaration, then writes sheets, indexes and inventory.json. */
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [command, argument] = process.argv.slice(2);
  const canonicalJson = (value: unknown) => JSON.stringify(value, null, 1) + '\n';
  const declared = (path: string) => {
    const bytes = readFileSync(path, 'utf8');
    if (bytes !== canonicalJson(resolveStrata())) throw new Error(`${path} no longer resolves to itself; re-declare`);
    return { strata: JSON.parse(bytes) as Strata, sha256: sha(bytes) };
  };
  if (command === 'declare' && argument) {
    writeFileSync(argument, canonicalJson(resolveStrata()), { flag: 'wx' });
  } else if (command === 'check') {
    const { strata, sha256 } = declared(argument ?? join(HERE, 'strata.json'));
    console.log(JSON.stringify({ sha256, cells: Object.fromEntries(Object.entries(strata.strata)
      .map(([name, s]) => [name, s.cells.length])) }));
  } else if (command === 'render' && argument) {
    const configBytes = readFileSync(argument);
    const config = JSON.parse(configBytes.toString('utf8')) as RunConfig;
    const strataPath = absolute(ROOT, config.strata ?? join(HERE, 'strata.json'));
    const { strata, sha256 } = declared(strataPath);
    const started = new Date().toISOString();
    const result = renderRun(config, strata);
    const indexes: Record<string, { html: string; htmlSha256: string }> = {};
    const summary: Record<string, unknown> = {};
    for (const [name, stratum] of Object.entries(strata.strata) as [StratumName, Stratum][]) {
      const records = result.records.filter(r => r.stratum === name);
      const html = stratumIndex(name, stratum, records, result.dropped[name] ?? 0, config.label);
      writeFileSync(join(config.outputRoot, name, 'index.html'), html, { flag: 'wx' });
      indexes[name] = { html: `${name}/index.html`, htmlSha256: sha(html) };
      summary[name] = summarise(records, stratum, result.dropped[name] ?? 0);
    }
    const top = `<!doctype html><html lang="en"><meta charset="utf-8"><title>W42 gate eye sheets</title>
<h1>W42 gate eye sheets: ${escape(config.label)}</h1><ul>${Object.keys(indexes).map(name =>
      `<li><a href="${name}/index.html">${name}</a>: ${escape(JSON.stringify(summary[name]))}</li>`).join('')}</ul></html>`;
    writeFileSync(join(config.outputRoot, 'index.html'), top, { flag: 'wx' });
    const report = { schema: 'w42-g0-gate-eye-sheets-1', started, completed: new Date().toISOString(),
      runConfig: { path: resolve(argument), sha256: sha(configBytes), config },
      strata: { path: relative(ROOT, strataPath), sha256 }, browserOrCaptureStarted: false,
      canonicalHoldoutOrRecordedPixelsOpened: 0, shippedDocuments: result.shippedDocs,
      candidateDocuments: result.candidateDocs,
      index: { html: 'index.html', htmlSha256: sha(top) }, stratumIndexes: indexes, summary,
      distanceMeaning: 'mean OKLab distance to native over the declared body region and the whole ' +
        'frame; a diagnostic beside the eye, not a referee', records: result.records };
    writeFileSync(join(config.outputRoot, 'inventory.json'), JSON.stringify(report, null, 1) + '\n', { flag: 'wx' });
    console.log(JSON.stringify(summary, null, 1));
  } else {
    throw new Error('usage: sheets.ts declare <strata.json> | check [<strata.json>] | render <run.json>');
  }
}
