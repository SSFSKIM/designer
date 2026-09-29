/** Recovery of the stopped G1 sheet run only. Preparation reads metadata/source, not pixels.
 * The original adapter, renderer, native reader, exporter and capture verifier stay unchanged. */
import { execFileSync } from 'node:child_process';
import { readFileSync, readdirSync } from 'node:fs';
import { resolve, join, relative, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { plan, renderAdmitted, diagnosticSheet, type Options } from './adapter';
import { inspectCell, type Cell } from '../../2026-09-27-w41-g0-declaration/sheets/sheets';
import { sha, load, pinCommitted, checkPins, filePin, assertFile, fresh, fileChild,
  recoverNative, recoverShipped, recover, validateRecovery, stem, type Pin, type FilePin, type Member } from './recovery-core';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(HERE, '../../../../..');
const G1 = resolve(HERE, '..');
const G0 = resolve(HERE, '../../2026-09-27-w41-g0-declaration/sheets');
const OUTPUT = '/Users/new/vitrea-w41/g1-captures/sheets/run-1';
const LABEL = 'diagnostic candidate WEB for EYE; not a canonical read or G2 material';
const FREEZE = 'packages/calibration/results/2026-09-16-w29-freeze/sha256.txt';
const id = (c: { profileKey: string; sceneId: string }) => `${c.profileKey}/${c.sceneId}`;
const equal = (a: unknown, b: unknown, message: string) => {
  if (JSON.stringify(a) !== JSON.stringify(b)) throw Error(message);
};
const keys = (value: object) => Object.keys(value).sort();
interface Capture { png: string; pngSha256: string; cellSha256: string; reportSha256: string }
interface Frozen { captures: Record<string, Capture>; [key: string]: any }
interface Declaration {
  schema: string; pins: Pin[]; planSha256: string; preservationSha256: string;
  output: string; timeout: number; counts: { html: number; png: number; admitted: number; unmeasured: number };
  policy: string;
}

/** Check the full candidate derivation, not just the convenient derived capture map.
 * No file or image reads: callers first bind all supplied JSON bytes to committed pins. */
export function validateChain(b: {
  preparation: any; preparationPin: Pin; baseline: any; authoritySha256: string;
  derived: any; frozen: any; raw: any; seal: any; canonical: any; canonicalSealPin: Pin;
}) {
  const { preparation, preparationPin, baseline, derived, frozen, raw, seal, canonical } = b;
  if (baseline.preparationSha256 !== preparationPin.sha256 ||
      baseline.authoritySha256 !== b.authoritySha256 ||
      derived.admissionScope.path !== preparationPin.path ||
      derived.admissionScope.sha256 !== preparationPin.sha256 ||
      seal.inputs[preparationPin.path] !== preparationPin.sha256) throw Error('admission chain changed');
  if (frozen.sealSha256 !== derived.sourceSeal.sha256 ||
      raw.sealSha256 !== derived.sourceSeal.sha256 ||
      frozen.files[derived.sourceSeal.path] !== derived.sourceSeal.sha256 ||
      frozen.files[derived.sourceRawInventory.path] !== derived.sourceRawInventory.sha256 ||
      canonical.sealSha256 !== b.canonicalSealPin.sha256) throw Error('freeze input chain changed');
  const selected = [...preparation.cells].sort();
  equal(keys(baseline.captures), selected, 'baseline membership changed');
  equal(keys(derived.captures), selected, 'candidate membership changed');
  for (const cell of selected) {
    const capture = derived.captures[cell], row = raw.cells[cell];
    if (!row || row.primaryCapture !== capture.png || !capture.png.startsWith(derived.captureRoot + '/')) {
      throw Error('candidate capture path changed');
    }
    for (const [source, destination] of [['png', 'png'], ['descriptor', 'cell'], ['report', 'report']]) {
      if (frozen.files[row[source!]] !== row[source! + 'Sha256'] ||
          row[source! + 'Sha256'] !== capture[destination! + 'Sha256']) {
        throw Error('candidate payload chain changed');
      }
    }
    const profile = cell.split('/')[0], pair = seal.profiles[profile];
    const documents = [['material', 'materialProfile'], ['receded', 'recededProfile']].map(([key, kind]) =>
      ({ kind, path: pair[key!], sha256: seal.inputs[pair[key!]].slice(0, 12) }));
    equal(derived.documents[profile], documents, 'candidate document chain changed');
  }
}

// The actual baseline freeze names this epoch, as shipped_freezes in the unchanged driver
// does. Never search for a matching/latest authority or silently fall back to the v1 seal.
export function baselineAuthority(root: string, g1: string, digest: string): Pin {
  return pinCommitted(root, join(g1, 'baseline/authority-v2.json'), digest);
}

/** Metadata-only seal construction. The preserved files are NOT reopened here: their committed
 * preservation inventory is the byte witness. verify/run checks those bytes before continuing. */
function inputs() {
  const pins = new Map<string, Pin>();
  function pin(path: string, expected?: string) {
    const p = pinCommitted(ROOT, path, expected); pins.set(p.path, p); return p;
  }
  function metadata(path: string, expected?: string) {
    const p = pin(path, expected); return load(resolve(ROOT, p.path));
  }
  // These are the new declaration's inputs, allowed to be uncommitted only during prepare.
  for (const name of [...readdirSync(HERE).filter(n => /^recovery.*\.(ts|txt)$/.test(n)),
    'render-options.json', 'partial-output-preservation.json', 'recovery-ruling.json']) {
    const p = filePin(join(HERE, name));
    pins.set(relative(ROOT, p.path), { path: relative(ROOT, p.path), sha256: p.sha256 });
  }
  const options = load(join(HERE, 'render-options.json')) as Options;
  const preserved = load(join(HERE, 'partial-output-preservation.json'));
  if (options.outputRoot !== OUTPUT || preserved.runRoot !== OUTPUT || options.repeat !== 0 ||
      !options.candidate || !options.canonicalCandidate) throw Error('original run options required');
  const selection = metadata(join(HERE, 'representative-selection.json'));
  if (selection.nativeRepeatOrdinal !== options.repeat || selection.cells.length !== 9) {
    throw Error('representative selection changed');
  }
  const baseline = metadata(options.baselineFreeze.path, options.baselineFreeze.sha256) as Frozen;
  const derived = metadata(options.candidate.freeze.path, options.candidate.freeze.sha256) as Frozen;
  const canonical = metadata(options.canonicalCandidate.freeze.path, options.canonicalCandidate.freeze.sha256) as Frozen;
  const preparationPin = pin(join(G1, 'baseline/preparation.json'));
  const preparation = load(resolve(ROOT, preparationPin.path));
  const authority = baselineAuthority(ROOT, G1, baseline.authoritySha256);
  pins.set(authority.path, authority);
  const frozen = metadata(derived.sourceFrozen.path, derived.sourceFrozen.sha256);
  const raw = metadata(derived.sourceRawInventory.path, derived.sourceRawInventory.sha256);
  const seal = metadata(derived.sourceSeal.path, derived.sourceSeal.sha256);
  const canonicalSealPin = pin(join(dirname(options.canonicalCandidate.freeze.path), 'seal.json'), canonical.sealSha256);
  const canonicalSeal = load(resolve(ROOT, canonicalSealPin.path));
  validateChain({ preparation, preparationPin, baseline, authoritySha256: authority.sha256,
    derived, frozen, raw, seal, canonical, canonicalSealPin });
  if (canonical.label !== LABEL || canonical.captureRoot !== options.canonicalCandidate.captureRoot ||
      derived.captureRoot !== options.candidate.captureRoot) throw Error('candidate identity changed');
  equal(options.candidate.documents, derived.documents, 'W39 candidate document selection changed');
  equal(options.canonicalCandidate.documents, canonical.documents, 'canonical document selection changed');
  const metadataPlan = plan();
  if (metadataPlan.preparationSha256 !== preparationPin.sha256) throw Error('plan preparation changed');
  const cells = metadataPlan.records;
  const canonicalIds = cells.filter(c => c.bed === 'canonical').map(id).sort();
  equal(keys(canonical.captures), canonicalIds, 'canonical freeze membership changed');
  equal(canonicalSeal.plan.cells.map(id).sort(), canonicalIds, 'canonical seal membership changed');
  if (cells.filter(c => c.admitted).length !== 866 || cells.filter(c => !c.admitted).length !== 8) {
    throw Error('original 866+8 scope changed');
  }
  const names = new Map<string, FilePin>();
  for (const p of preserved.files as FilePin[]) {
    if (names.has(p.path) || dirname(p.path) !== OUTPUT || !/^[0-9a-f]{64}$/.test(p.sha256) ||
        !Number.isInteger(p.bytes) || p.bytes <= 0) throw Error('invalid preservation entry');
    names.set(p.path, p);
  }
  const admitted = cells.filter(c => c.admitted);
  const expectedNames = admitted.slice(0, 125).flatMap((c, i) => [join(OUTPUT, stem(c) + '.html'),
    ...(i < 124 ? [join(OUTPUT, stem(c) + '.png')] : [])]).sort();
  equal([...names.keys()].sort(), expectedNames, 'preserved prefix is not 125 HTML / 124 PNG');
  if (admitted.slice(0, 125).some(c => c.bed !== 'canonical' || !c.profileKey.startsWith('apple-macos-26.5-'))) {
    throw Error('recovery provenance only covers preserved canonical 26.5 cells');
  }
  const fixtures = metadata(join(G0, 'render-inventory.json'));
  const freezePin = pin(FREEZE);
  const fixtureHashes = new Map(readFileSync(resolve(ROOT, freezePin.path), 'utf8').trim().split('\n')
    .map(line => { const [digest, path] = line.split('  '); return [path!, digest!]; }));
  for (const cell of admitted.slice(0, 125)) {
    const rows = fixtures.records.filter((r: any) => r.bed === 'canonical' && id(r) === id(cell));
    const path = `apps/reference-apple/fixtures/${cell.profileKey}/${cell.sceneId}.png`;
    if (rows.length !== 1 || rows[0].nativeSha256 !== fixtureHashes.get(path)) {
      throw Error('G0 fixture provenance differs from frozen 26.5 witness');
    }
  }
  for (const cell of cells) for (const doc of cell.documents) pin(doc.path);
  for (const candidate of [options.candidate, options.canonicalCandidate]) {
    for (const pair of Object.values(candidate.documents)) for (const doc of pair) {
      if (!pin(doc.path).sha256.startsWith(doc.sha256)) throw Error('candidate document bytes changed');
    }
  }
  // Bind unchanged original source and public metadata. Historical capture source epochs remain
  // inside their whole frozen/seal files; they are not recast as today's renderer source.
  for (const path of [join(HERE, 'adapter.ts'), join(HERE, 'native.py'), join(G0, 'sheets.ts'),
    join(G0, 'export-png.py'), join(G1, 'canonical-diagnostic/driver.py'),
    join(G1, 'canonical-diagnostic/plan.ts'), join(ROOT, 'apps/reference-apple/scenes.json'),
    join(ROOT, 'packages/calibration/results/generations/index.json'),
    join(ROOT, 'packages/calibration/results/matrix.json'),
    join(ROOT, 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/wave.py'),
    join(ROOT, 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/w39_archive.py')]) pin(path);
  return { pins: [...pins.values()].sort((a, b) => a.path.localeCompare(b.path)), options,
    preserved: preserved.files as FilePin[], metadataPlan, baseline, derived, canonical, fixtures };
}
export function prepare(path: string) {
  if (resolve(path) !== join(HERE, 'recovery-declaration.json')) throw Error('fixed additive declaration path required');
  const input = inputs();
  const declaration: Declaration = { schema: 'w41-sheet-recovery-1', pins: input.pins,
    planSha256: sha(JSON.stringify(input.metadataPlan)),
    preservationSha256: sha(readFileSync(join(HERE, 'partial-output-preservation.json'))),
    output: OUTPUT, timeout: 120000, counts: { html: 125, png: 124, admitted: 866, unmeasured: 8 },
    policy: 'Reuse 125 HTML and 124 PNG unchanged; export one pending HTML; render only remaining 741 admitted cells. No completed-native reread, holdout, probe, browser, capture or matrix writes.' };
  fresh(path, JSON.stringify(declaration, null, 2) + '\n');
  return { declaration: path, status: 'PREPARED metadata only; review and commit all pins before verify/run' };
}
function capture(cell: Cell, root: string, frozen: Frozen) {
  const entry = frozen.captures[id(cell)];
  const png = join(root, cell.profileKey, cell.sceneId, `${cell.sceneId}__webgpu.png`);
  if (!entry || entry.png !== png) throw Error('missing/wrong frozen capture');
  assertFile({ path: png, sha256: entry.pngSha256 });
  assertFile({ path: join(dirname(png), 'cell__webgpu.json'), sha256: entry.cellSha256 });
  assertFile({ path: join(dirname(png), 'report__webgpu.json'), sha256: entry.reportSha256 });
  return entry;
}
function job(declaration: Declaration, binding: string, input: ReturnType<typeof inputs>) {
  const { options, baseline, derived, canonical, metadataPlan, fixtures } = input;
  function columns(cell: Cell, preservedHtml?: string) {
    const isCanonical = cell.bed === 'canonical';
    const root = isCanonical ? options.canonicalRoot : options.baselineRoot;
    const next = isCanonical ? options.canonicalCandidate! : options.candidate!;
    const shipped = isCanonical ? undefined : capture(cell, root, baseline);
    const candidateCapture = capture(cell, next.captureRoot, isCanonical ? canonical : derived);
    const docs = next.documents[cell.profileKey];
    if (!docs) throw Error('missing candidate document pair');
    const inspected = inspectCell(cell, ROOT, root);
    const candidateInspection = inspectCell({ ...cell, documents: docs }, ROOT, next.captureRoot);
    if (inspected.status !== 'MATCH' || candidateInspection.status !== 'MATCH') {
      throw Error('admitted capture missing; preserve rather than export blank panel');
    }
    return { root, next, candidateCapture, record: { ...cell, status: 'RENDERED', shipped,
      ...(preservedHtml === undefined ? { shippedPngSha256: filePin(inspected.pngPath).sha256 } : {
        shippedDisplay: { ...recoverShipped(preservedHtml, readFileSync(inspected.pngPath)),
          currentCapturePath: inspected.pngPath } }),
      candidate: { ...(isCanonical ? { label: LABEL } : {}), documents: docs, capture: candidateCapture } } };
  }
  return { output: OUTPUT, binding, context: { options, nativeGeneration: metadataPlan.nativeGeneration,
      declaration: relative(ROOT, join(HERE, 'recovery-declaration.json')),
      originalHtmlReused: 125, originalPngReused: 124, newHtml: 741, newPng: 742 }, cells: metadataPlan.records as Member[], preserved: input.preserved,
    exporter: { command: 'python3.12', args: [join(G0, 'export-png.py')], timeout: declaration.timeout },
    recoverRecord: async (member: Member, html: string) => {
      const cell = member as unknown as Cell;
      const { record } = columns(cell, html);
      return { ...record, native: { ...recoverNative(cell, html, fixtures.records),
        fixtureInventory: relative(ROOT, join(G0, 'render-inventory.json')),
        fixtureInventorySha256: filePin(join(G0, 'render-inventory.json')).sha256,
        frozenFixtureWitness: FREEZE, frozenFixtureWitnessSha256: filePin(join(ROOT, FREEZE)).sha256 } };
    },
    renderFresh: async (member: Member, work: string) => {
      const cell = member as unknown as Cell;
      const { root, next, record } = columns(cell);
      let native: Record<string, unknown> | undefined;
      const rendered = await renderAdmitted(cell, { repositoryRoot: ROOT, captureRoot: root,
        candidate: { captureRoot: next.captureRoot, documents: next.documents[cell.profileKey]! },
        readNative: async () => {
          if (cell.bed === 'canonical') {
            const path = join(ROOT, 'apps/reference-apple/fixtures', cell.profileKey, cell.sceneId + '.png');
            const bytes = readFileSync(path);
            native = { path, pngSha256: sha(bytes), source: 'committed canonical cal/val fixture', newNativeRead: true };
            return bytes;
          }
          const stdin = join(work, 'native.stdin'); fresh(stdin, '');
          const output = join(work, 'native.stdout.json'), error = join(work, 'native.stderr.log');
          fileChild({ command: 'python3.12', args: [join(HERE, 'native.py'), '--archive-root', options.archiveRoot,
            '--generation', metadataPlan.nativeGeneration, '--cell', id(cell), '--repeat', String(options.repeat)],
            timeout: declaration.timeout, input: stdin, output, error });
          const result = load(output), bytes = Buffer.from(result.png, 'base64');
          if (sha(bytes) !== result.provenance.pngSha256) throw Error('native bridge hash mismatch');
          native = { ...result.provenance, newNativeRead: true }; return bytes;
        } });
      if (!rendered || !native) throw Error('admitted cell did not render native panel');
      return { html: cell.bed === 'canonical' ? diagnosticSheet(rendered) : rendered,
        record: { ...record, native } };
    } };
}
export function verify(path: string) {
  if (resolve(path) !== join(HERE, 'recovery-declaration.json')) throw Error('fixed recovery declaration required');
  const declarationPin = pinCommitted(ROOT, path);
  const declaration = load(path) as Declaration;
  if (declaration.schema !== 'w41-sheet-recovery-1' || declaration.output !== OUTPUT ||
      declaration.timeout !== 120000) throw Error('recovery declaration changed');
  checkPins(ROOT, declaration.pins);
  const input = inputs();
  equal(input.pins, declaration.pins, 'declaration input frontier changed');
  if (sha(JSON.stringify(input.metadataPlan)) !== declaration.planSha256 ||
      sha(readFileSync(join(HERE, 'partial-output-preservation.json'))) !== declaration.preservationSha256) {
    throw Error('declaration plan/preservation changed');
  }
  // This is the ORIGINAL verify verb, never assemble/capture. It may read frozen WEB backgrounds
  // and source bytes, but does not open canonical native fixtures or archive payloads.
  execFileSync('python3.12', [join(G1, 'canonical-diagnostic/driver.py'), 'verify', 'attempt-1'],
    { cwd: ROOT, stdio: 'inherit', timeout: 600000, killSignal: 'SIGKILL' });
  const config = job(declaration, declarationPin.sha256, input);
  validateRecovery(config);
  return config;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [operation, path, ...extra] = process.argv.slice(2);
  if (!path || extra.length) throw Error('usage: recovery.ts prepare|verify|run <recovery-declaration.json>');
  if (operation === 'prepare') console.log(JSON.stringify(prepare(resolve(path)), null, 2));
  else if (operation === 'verify') {
    verify(resolve(path)); console.log('VERIFIED; no sheet render or native read');
  } else if (operation === 'run') {
    const result = await recover(verify(resolve(path)));
    console.log(JSON.stringify({ records: result.records.length, output: OUTPUT }));
  } else throw Error('unknown recovery operation');
}
