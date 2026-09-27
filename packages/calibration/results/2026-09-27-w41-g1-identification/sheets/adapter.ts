/** G1 clause 9: additive offline adapter; G0 owns panel layout and difference encoding. */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, join, relative, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { canonicalRole, enumerateCells, inspectCell, renderCell, w39Plan,
  type Cell, type Document, type RenderOptions } from '../../2026-09-27-w41-g0-declaration/sheets/sheets';
import { loadCurrentRows } from '../../../src/matrix-store';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(HERE, '../../../../..');
const G0 = resolve(HERE, '../../2026-09-27-w41-g0-declaration/sheets');
const sha = (b: Uint8Array | string) => createHash('sha256').update(b).digest('hex');
const load = (p: string) => JSON.parse(readFileSync(p, 'utf8'));
const id = (c: Pick<Cell, 'profileKey' | 'sceneId'>) => `${c.profileKey}/${c.sceneId}`;
interface Capture { png: string; pngSha256: string; cellSha256: string; reportSha256: string }
interface Frozen { captures: Record<string, Capture> }
interface Pin { path: string; sha256: string }
interface Candidate { captureRoot: string; documents: Record<string, Document[]>; freeze: Pin }
export interface Options {
  baselineFreeze: Pin; baselineRoot: string; archiveRoot: string; repeat: number;
  outputRoot: string; canonicalRoot: string; candidate?: Candidate;
  canonicalCandidate?: Candidate;
}
function beneath(root: string, path: string) {
  const r = relative(resolve(root), resolve(path));
  return r === '' || (r !== '..' && !r.startsWith('../') && !isAbsolute(r));
}
function committed(pin: Pin) {
  if (!beneath(ROOT, pin.path)) throw new Error('pin outside checkout');
  const bytes = readFileSync(pin.path);
  const recorded = execFileSync('git', ['-C', ROOT, 'show', `HEAD:${relative(ROOT, pin.path)}`]);
  if (sha(bytes) !== pin.sha256 || sha(recorded) !== pin.sha256) {
    throw new Error('freeze must match supplied hash and committed bytes');
  }
  return JSON.parse(bytes.toString()) as Frozen;
}
export function plan() {
  if (process.env['VITREA_MATRIX_PATH']) throw new Error('unset VITREA_MATRIX_PATH');
  const preparation = load(resolve(HERE, '../baseline/preparation.json'));
  const admitted = new Set<string>(preparation.cells);
  const cells = enumerateCells(loadCurrentRows(), w39Plan()).filter(c => c.bed === 'w39' ||
    ['calibration', 'validation'].includes(canonicalRole(c.sceneId, ROOT)));
  const records = cells.map(c => ({ ...c,
    admitted: c.bed === 'canonical' || admitted.has(id(c)),
    ...(!admitted.has(id(c)) && c.bed === 'w39' ? {
      status: 'UNMEASURED', reason: preparation.excludedCells[id(c)] } : {}),
  }));
  if (records.filter(c => c.bed === 'canonical').length !== 330 ||
      records.filter(c => c.bed === 'w39').length !== 544 ||
      records.filter(c => c.bed === 'w39' && c.admitted).length !== 536 ||
      admitted.size !== 536) throw new Error('standing sheet membership changed');
  return { mode: 'metadata-only', nativePayloadsOpened: 0, pixelsOpened: 0,
    nativeGeneration: preparation.inventorySha256,
    preparationSha256: sha(readFileSync(resolve(HERE, '../baseline/preparation.json'))), records };
}

let w39Scope: { roles: Map<string, string | undefined>; admitted: Set<string> } | undefined;
function authoritativeW39Scope() {
  return w39Scope ??= {
    roles: new Map(w39Plan().map(cell => [id(cell), cell.role])),
    admitted: new Set<string>(load(resolve(HERE, '../baseline/preparation.json')).cells),
  };
}
/** Role and admission rejection precede all capture/native opens, even for forged caller fields. */
export async function renderAdmitted(cell: Cell, options: RenderOptions) {
  const scope = cell.bed === 'w39' ? authoritativeW39Scope() : undefined;
  const role = cell.bed === 'canonical' ? canonicalRole(cell.sceneId, options.repositoryRoot) :
    scope?.roles.get(id(cell));
  if (!['calibration', 'validation'].includes(role ?? '')) {
    throw new Error('sheets admit calibration/validation only');
  }
  if (scope && !scope.admitted.has(id(cell))) return undefined;
  return renderCell(cell, options);
}
function bindCapture(cell: Cell, root: string, frozen: Frozen) {
  const entry = frozen.captures[id(cell)];
  const expected = join(root, cell.profileKey, cell.sceneId, `${cell.sceneId}__webgpu.png`);
  if (!entry || resolve(entry.png) !== resolve(expected)) throw new Error('missing/wrong frozen capture');
  for (const [path, digest] of [[expected, entry.pngSha256],
    [join(root, cell.profileKey, cell.sceneId, 'cell__webgpu.json'), entry.cellSha256],
    [join(root, cell.profileKey, cell.sceneId, 'report__webgpu.json'), entry.reportSha256]]) {
    if (!digest || sha(readFileSync(path!)) !== digest) throw new Error('frozen capture bytes changed');
  }
  return entry;
}

export async function render(options: Options) {
  const metadata = plan();
  const output = resolve(options.outputRoot);
  const scratch = '/Users/new/vitrea-w41/g1-captures/sheets';
  if (!beneath(scratch, output) || output === scratch || existsSync(output)) {
    throw new Error('output must be a fresh run directory beneath g1-captures/sheets');
  }
  if (!Number.isInteger(options.repeat) || options.repeat < 0 || options.repeat > 6) {
    throw new Error('explicit repeat ordinal 0..6 required');
  }
  const baseline = committed(options.baselineFreeze);
  const admittedIds = metadata.records.filter(c => c.bed === 'w39' && c.admitted).map(id).sort();
  if (JSON.stringify(Object.keys(baseline.captures).sort()) !== JSON.stringify(admittedIds)) {
    throw new Error('baseline must freeze exactly 536 admitted cal/val cells');
  }
  const next = options.candidate ? committed(options.candidate.freeze) : undefined;
  const canonicalNext = options.canonicalCandidate ? committed(options.canonicalCandidate.freeze) : undefined;
  for (const candidate of [options.candidate, options.canonicalCandidate]) {
    if (candidate && [options.baselineRoot, options.canonicalRoot].some(root =>
      beneath(root, candidate.captureRoot) || beneath(candidate.captureRoot, root))) {
      throw new Error('candidate needs a separate capture tree');
    }
  }
  mkdirSync(output, { recursive: true });
  const records = [];
  for (const cell of metadata.records) {
    if (!cell.admitted) { records.push(cell); continue; }
    const canonical = cell.bed === 'canonical';
    const captureRoot = canonical ? options.canonicalRoot : options.baselineRoot;
    const candidate = canonical ? options.canonicalCandidate : options.candidate;
    const frozenNext = canonical ? canonicalNext : next;
    const shipped = canonical ? undefined : bindCapture(cell, captureRoot, baseline);
    if (candidate && frozenNext) bindCapture(cell, candidate.captureRoot, frozenNext);
    if (candidate && !candidate.documents[cell.profileKey]) throw new Error('missing candidate document pair');
    let native: Record<string, unknown> | undefined;
    const html = await renderAdmitted(cell, { repositoryRoot: ROOT, captureRoot,
      ...(candidate ? { candidate: { captureRoot: candidate.captureRoot,
        documents: candidate.documents[cell.profileKey]! } } : {}),
      readNative: async () => {
        if (canonical) {
          const path = join(ROOT, 'apps/reference-apple/fixtures', cell.profileKey, `${cell.sceneId}.png`);
          const bytes = readFileSync(path);
          native = { path, pngSha256: sha(bytes), source: 'committed canonical cal/val fixture' };
          return bytes;
        }
        const result = JSON.parse(execFileSync('python3.12', [join(HERE, 'native.py'),
          '--archive-root', options.archiveRoot, '--generation', metadata.nativeGeneration,
          '--cell', id(cell), '--repeat', String(options.repeat)], { maxBuffer: 32 * 1024 * 1024 }).toString());
        const bytes = Buffer.from(result.png, 'base64');
        if (sha(bytes) !== result.provenance.pngSha256) throw new Error('native PNG bridge hash mismatch');
        native = result.provenance;
        return bytes;
      } });
    const filename = `${cell.bed}__${encodeURIComponent(cell.profileKey)}__${encodeURIComponent(cell.sceneId)}`;
    writeFileSync(join(output, `${filename}.html`), html!, { flag: 'wx' });
    const png = execFileSync('python3.12', [join(G0, 'export-png.py')],
      { input: html, maxBuffer: 32 * 1024 * 1024 });
    writeFileSync(join(output, `${filename}.png`), png, { flag: 'wx' });
    const inspected = inspectCell(cell, ROOT, captureRoot);
    records.push({ ...cell, status: inspected.status === 'MATCH' ? 'RENDERED' : 'UNMEASURED',
      native, shipped, shippedPngSha256: inspected.status === 'MATCH' ? sha(readFileSync(inspected.pngPath)) : null,
      candidate: candidate ? { documents: candidate.documents[cell.profileKey],
        capture: frozenNext!.captures[id(cell)] } : 'EMPTY — no candidate capture supplied',
      html: `${filename}.html`, htmlSha256: sha(html!), png: `${filename}.png`, pngSha256: sha(png) });
  }
  const report = { options, nativeGeneration: metadata.nativeGeneration,
    canonicalHoldoutPixelsOpened: 0, records };
  writeFileSync(join(output, 'inventory.json'), JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
  return { output, records: records.length };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [command, config] = process.argv.slice(2);
  if (command === 'inventory' && !config) console.log(JSON.stringify(plan(), null, 2));
  else if (command === 'render' && config) console.log(JSON.stringify(await render(load(config))));
  else throw new Error('usage: adapter.ts inventory | render <options.json>');
}
