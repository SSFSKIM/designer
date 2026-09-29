/** Append-only offline recovery mechanics. No native reader or production paths live here. */
import { createHash } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { readFileSync, openSync, closeSync, fsyncSync, writeFileSync, existsSync, lstatSync,
  mkdirSync, readdirSync, linkSync, unlinkSync } from 'node:fs';
import { resolve, relative, join, basename, dirname, isAbsolute } from 'node:path';
import { decodePng } from '../../../src/image';

export const sha = (value: string | Uint8Array) => createHash('sha256').update(value).digest('hex');
export const load = (path: string) => JSON.parse(readFileSync(path, 'utf8'));
export interface Pin { path: string; sha256: string }
export interface FilePin extends Pin { bytes: number }
export interface Member { bed: string; profileKey: string; sceneId: string; admitted: boolean;
  [key: string]: unknown }
export const stem = (c: Pick<Member, 'bed' | 'profileKey' | 'sceneId'>) =>
  `${c.bed}__${encodeURIComponent(c.profileKey)}__${encodeURIComponent(c.sceneId)}`;
export function inside(root: string, path: string) {
  const rel = relative(resolve(root), resolve(root, path));
  if (rel === '..' || rel.startsWith('../') || isAbsolute(rel)) throw Error('path escapes root');
  return resolve(root, path);
}
function regular(path: string) {
  if (!lstatSync(path).isFile()) throw Error('regular file required: ' + path);
}
export function filePin(path: string): FilePin {
  regular(path); const bytes = readFileSync(path);
  return { path, bytes: bytes.length, sha256: sha(bytes) };
}
export function assertFile(pin: Pin & { bytes?: number }) {
  const actual = filePin(pin.path);
  if (actual.sha256 !== pin.sha256 || (pin.bytes !== undefined && actual.bytes !== pin.bytes)) {
    throw Error('changed bytes: ' + pin.path);
  }
}
export function pinCommitted(root: string, path: string, expected?: string): Pin {
  path = inside(root, path); regular(path);
  const bytes = readFileSync(path), digest = sha(bytes);
  const committed = execFileSync('git', ['-C', root, 'show', `HEAD:${relative(root, path)}`],
    { maxBuffer: 64 * 1024 * 1024, timeout: 30000 });
  if (sha(committed) !== digest || (expected !== undefined && expected !== digest)) {
    throw Error('input must match committed full hash: ' + path);
  }
  return { path: relative(root, path), sha256: digest };
}
export function checkPins(root: string, pins: Pin[]) {
  for (const pin of pins) pinCommitted(root, pin.path, pin.sha256);
}
export function fresh(path: string, bytes: string | Uint8Array) {
  const fd = openSync(path, 'wx');
  try { writeFileSync(fd, bytes); fsyncSync(fd); } finally { closeSync(fd); }
}
/** Companion hashes catch changed/torn checkpoints; committed input pins remain the authority. */
export function save(path: string, value: unknown) {
  const bytes = JSON.stringify(value, null, 2) + '\n';
  fresh(path, bytes); fresh(path + '.sha256', sha(bytes) + '\n');
}
export function sealed(path: string) {
  regular(path + '.sha256');
  assertFile({ path, sha256: readFileSync(path + '.sha256', 'utf8').trim() });
  return load(path);
}
export interface Child { command: string; args: string[]; timeout: number }
/** Both directions use regular files, including native.py's potentially large JSON response.
 * SIGKILL bounds a hung Python child even if it does not respond to SIGTERM. Outputs survive. */
export function fileChild(c: Child & { input: string; output: string; error: string }) {
  if (!Number.isInteger(c.timeout) || c.timeout <= 0 || c.timeout > 600000) {
    throw Error('bounded child timeout required (1..600000 ms)');
  }
  regular(c.input);
  const fds: number[] = [];
  try {
    fds.push(openSync(c.input, 'r')); fds.push(openSync(c.output, 'wx'));
    fds.push(openSync(c.error, 'wx'));
    const result = spawnSync(c.command, c.args, { stdio: fds as [number, number, number],
      timeout: c.timeout, killSignal: 'SIGKILL' });
    fsyncSync(fds[1]!); fsyncSync(fds[2]!);
    if (result.error || result.status !== 0) {
      throw Error(`child failed: ${result.error?.message ?? result.status ?? result.signal}`);
    }
  } finally { for (const fd of fds) closeSync(fd); }
}
export function recoverNative(cell: Pick<Member, 'bed' | 'profileKey' | 'sceneId'>,
  html: string, fixtures: Array<Record<string, unknown>>) {
  if (cell.bed !== 'canonical') throw Error('only canonical provenance can be recovered');
  const rows = fixtures.filter(r => r.bed === cell.bed && r.profileKey === cell.profileKey &&
    r.sceneId === cell.sceneId && r.status === 'RENDERED');
  if (rows.length !== 1 || !/^[a-f0-9]{64}$/.test(String(rows[0]!.nativeSha256))) {
    throw Error('unique committed G0 fixture hash required');
  }
  const images = [...html.matchAll(/<img alt="Native" width="\d+" height="\d+" src="data:image\/png;base64,([A-Za-z0-9+/=]+)">/g)];
  if (images.length !== 1) throw Error('unique embedded Native PNG required');
  const bytes = Buffer.from(images[0]![1]!, 'base64');
  if (bytes.toString('base64') !== images[0]![1]) throw Error('invalid embedded Native encoding');
  return { source: 'recovered from preserved HTML and committed G0 fixture inventory; not a new native read',
    newNativeRead: false, displayPngSha256: sha(bytes), fixturePngSha256: rows[0]!.nativeSha256,
    hashMeaning: 'Display PNG is renderCell re-encoding; fixture hash names original bytes, not display encoding.' };
}
interface Recovery {
  output: string; binding: string; cells: Member[]; preserved: FilePin[]; exporter: Child;
  context?: Record<string, unknown>;
  recoverRecord: (cell: Member, html: string) => Promise<Record<string, unknown>>;
  renderFresh: (cell: Member, work: string) => Promise<{ html: string; record: Record<string, unknown> }>;
}
function exactNames(dir: string, allowed: string[]) {
  if (!lstatSync(dir).isDirectory()) throw Error('regular directory required: ' + dir);
  const actual = readdirSync(dir).sort();
  if (JSON.stringify(actual) !== JSON.stringify([...allowed].sort())) {
    throw Error('unknown files or missing companions: ' + dir);
  }
}
function artifactPins(dir: string) {
  return readdirSync(dir).sort().map(name => ({ ...filePin(join(dir, name)), path: name }));
}
function checkArtifacts(dir: string, files: FilePin[]) {
  exactNames(dir, files.map(f => f.path));
  for (const f of files) assertFile({ ...f, path: inside(dir, f.path) });
}
/** Validate the whole existing tree before invoking any renderer, not merely the next cell. */
export function validateRecovery(c: Recovery) {
  const state = join(c.output, '.recovery');
  if (!lstatSync(c.output).isDirectory()) throw Error('output directory required');
  const cells = new Map(c.cells.filter(cell => cell.admitted).map(cell => [stem(cell), cell]));
  if (cells.size !== c.cells.filter(cell => cell.admitted).length) throw Error('duplicate sheet');
  const expected = new Set<string>();
  for (const pin of c.preserved) {
    if (dirname(pin.path) !== c.output || !cells.has(basename(pin.path).replace(/\.(html|png)$/, ''))) {
      throw Error('preserved file outside admitted membership');
    }
    if (expected.has(basename(pin.path))) throw Error('duplicate preserved path');
    expected.add(basename(pin.path)); assertFile(pin);
  }
  for (const name of expected) {
    if (name.endsWith('.png') && !expected.has(name.replace(/\.png$/, '.html'))) {
      throw Error('preserved PNG missing HTML companion');
    }
  }
  if (existsSync(state)) {
    if (!lstatSync(state).isDirectory()) throw Error('state directory required');
    expected.add('.recovery');
    const start = sealed(join(state, 'binding.json'));
    if (start.binding !== c.binding || JSON.stringify(start.cells) !== JSON.stringify(c.cells) ||
        JSON.stringify(start.exporter) !== JSON.stringify(c.exporter)) throw Error('different recovery options');
    const names = readdirSync(state);
    for (const name of names.filter(n => !['binding.json', 'binding.json.sha256'].includes(n))) {
      const cell = cells.get(name);
      if (!cell) throw Error('unknown checkpoint: ' + name);
      const dir = join(state, name);
      if (!lstatSync(dir).isDirectory()) throw Error('checkpoint directory required');
      const cp = sealed(join(dir, 'checkpoint.json'));
      if (cp.binding !== c.binding || JSON.stringify(cp.cell) !== JSON.stringify(cell)) {
        throw Error('checkpoint binding changed');
      }
      assertFile({ path: join(c.output, name + '.html'), sha256: cp.htmlSha256 });
      expected.add(name + '.html'); checkArtifacts(join(dir, 'work'), cp.artifacts);
      const attempts = readdirSync(dir).filter(n => /^export-\d+$/.test(n));
      exactNames(dir, ['checkpoint.json', 'checkpoint.json.sha256', 'work', ...attempts]);
      let success: string | undefined;
      for (let i = 0; i < attempts.length; i++) {
        const attempt = join(dir, `export-${i}`);
        exactNames(attempt, ['stdout', 'stderr', 'result.json', 'result.json.sha256']);
        const result = sealed(join(attempt, 'result.json'));
        if (result.checkpointSha256 !== filePin(join(dir, 'checkpoint.json')).sha256 || success) {
          throw Error('changed/out-of-order export checkpoint');
        }
        assertFile({ path: join(attempt, 'stdout'), sha256: result.stdoutSha256 });
        assertFile({ path: join(attempt, 'stderr'), sha256: result.stderrSha256 });
        if (result.ok === true) success = result.stdoutSha256;
        else if (result.ok !== false) throw Error('invalid export result');
      }
      const png = join(c.output, name + '.png');
      const prior = c.preserved.find(p => p.path === png);
      if (prior && attempts.length) throw Error('preserved PNG was exported again');
      if (existsSync(png)) {
        const digest = prior?.sha256 ?? success;
        if (!digest) throw Error('PNG without successful export checkpoint');
        assertFile({ path: png, sha256: digest }); expected.add(name + '.png');
      } else if (success) {
        // A completed export may have crashed before its no-clobber link into the final name.
      }
    }
  }
  for (const name of ['inventory-recovered.json', 'inventory-recovered.json.sha256']) {
    if (existsSync(join(c.output, name))) expected.add(name);
  }
  exactNames(c.output, [...expected]);
  if (existsSync(join(c.output, 'inventory-recovered.json'))) {
    const inventory = sealed(join(c.output, 'inventory-recovered.json'));
    if (inventory.binding !== c.binding) throw Error('inventory binding changed');
    for (const name of cells.keys()) {
      if (!existsSync(join(c.output, name + '.html')) || !existsSync(join(c.output, name + '.png'))) {
        throw Error('missing completed output companion: ' + name);
      }
    }
  } else if (existsSync(join(c.output, 'inventory-recovered.json.sha256'))) {
    throw Error('missing inventory companion');
  }
}
export async function recover(c: Recovery) {
  validateRecovery(c);
  const state = join(c.output, '.recovery');
  if (!existsSync(state)) {
    mkdirSync(state); save(join(state, 'binding.json'), {
      binding: c.binding, cells: c.cells, exporter: c.exporter });
  }
  // A live/crashed invocation is never automatically stolen. The lock is operational, not evidence.
  const lock = join(state, 'lock'); fresh(lock, String(process.pid));
  try {
    const records: Record<string, unknown>[] = [];
    for (const cell of c.cells) {
      if (!cell.admitted) { records.push({ ...cell, status: 'UNMEASURED' }); continue; }
      const name = stem(cell), dir = join(state, name);
      const htmlPath = join(c.output, name + '.html'), pngPath = join(c.output, name + '.png');
      const checkpoint = join(dir, 'checkpoint.json');
      if (!existsSync(checkpoint)) {
        mkdirSync(dir); const work = join(dir, 'work'); mkdirSync(work);
        const prior = c.preserved.some(p => p.path === htmlPath);
        let html: string, record: Record<string, unknown>;
        if (prior) {
          html = readFileSync(htmlPath, 'utf8'); record = await c.recoverRecord(cell, html);
        } else {
          ({ html, record } = await c.renderFresh(cell, work)); fresh(htmlPath, html);
        }
        // Persist ALL provenance before the fallible exporter. Incomplete writes refuse on resume.
        save(checkpoint, { binding: c.binding, cell, record, htmlSha256: sha(html),
          htmlOrigin: prior ? 'preserved-original' : 'new-renderAdmitted', artifacts: artifactPins(work) });
      }
      const cp = sealed(checkpoint);
      const preservedPng = c.preserved.some(p => p.path === pngPath);
      if (!existsSync(pngPath)) {
        const attempts = readdirSync(dir).filter(n => /^export-\d+$/.test(n));
        const last = attempts.length ? join(dir, `export-${attempts.length - 1}`) : undefined;
        if (last && sealed(join(last, 'result.json')).ok) {
          linkSync(join(last, 'stdout'), pngPath);
        } else {
          const attempt = join(dir, `export-${attempts.length}`); mkdirSync(attempt);
          let failure: unknown;
          try { fileChild({ ...c.exporter, input: htmlPath, output: join(attempt, 'stdout'),
            error: join(attempt, 'stderr') }); } catch (error) { failure = error; }
          save(join(attempt, 'result.json'), { checkpointSha256: filePin(checkpoint).sha256,
            ok: !failure, stdoutSha256: filePin(join(attempt, 'stdout')).sha256,
            stderrSha256: filePin(join(attempt, 'stderr')).sha256,
            ...(failure ? { error: String(failure) } : {}) });
          if (failure) throw failure;
          linkSync(join(attempt, 'stdout'), pngPath);
        }
      }
      records.push({ ...cp.record, html: name + '.html', htmlSha256: cp.htmlSha256,
        htmlOrigin: cp.htmlOrigin, png: name + '.png', pngSha256: filePin(pngPath).sha256,
        pngOrigin: preservedPng ? 'preserved-original' : 'recovery-file-FD-export',
        checkpointSha256: filePin(checkpoint).sha256 });
    }
    const result = { ...c.context, binding: c.binding, canonicalHoldoutPixelsOpened: 0, records };
    const inventory = join(c.output, 'inventory-recovered.json');
    if (existsSync(inventory)) {
      if (JSON.stringify(sealed(inventory)) !== JSON.stringify(result)) throw Error('inventory changed');
    } else save(inventory, result);
    return result;
  } finally { unlinkSync(lock); }
}

/** Metadata MATCH cannot identify the pixels used in an old sheet. Compare decoded RGBA
 * with that sheet's embedded panel, allowing byte-different lossless PNG encodings. The
 * current file hash is observed now; the original capture file's encoding is not recoverable. */
export function recoverShipped(html: string, currentCapture: Uint8Array) {
  const images = [...html.matchAll(/<img alt="Shipped WebGPU" width="(\d+)" height="(\d+)" src="data:image\/png;base64,([A-Za-z0-9+/=]+)">/g)];
  if (images.length !== 1) throw Error('unique embedded Shipped WebGPU PNG required');
  const embedded = Buffer.from(images[0]![3]!, 'base64');
  if (embedded.toString('base64') !== images[0]![3]) throw Error('invalid embedded Shipped WebGPU encoding');
  const saved = decodePng(embedded), current = decodePng(currentCapture);
  if (saved.width !== Number(images[0]![1]) || saved.height !== Number(images[0]![2]) ||
      saved.width !== current.width || saved.height !== current.height ||
      !Buffer.from(saved.data).equals(Buffer.from(current.data))) {
    throw Error('preserved Shipped WebGPU pixels differ from current capture');
  }
  return { displayPngSha256: sha(embedded), currentCapturePngSha256: sha(currentCapture),
    originalCapturePngSha256: null, pixelsMatch: true,
    source: 'recovered display PNG; current capture verified pixel-identical without rerendering',
    hashMeaning: 'Current capture hash is observed during recovery, not the unknown original file encoding.' };
}
