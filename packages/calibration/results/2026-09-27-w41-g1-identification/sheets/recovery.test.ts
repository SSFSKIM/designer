import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { execFileSync } from 'node:child_process';
import { fileChild, recover, sha, pinCommitted, checkPins, recoverNative } from './recovery-core';

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'w41-recovery-synthetic-'));
  const output = join(root, 'output'); mkdirSync(output);
  const exporter = join(root, 'export.py');
  writeFileSync(exporter, `import os,sys,stat\nassert stat.S_ISREG(os.fstat(0).st_mode)\nassert stat.S_ISREG(os.fstat(1).st_mode)\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n`);
  const cells = ['done', 'pending', 'new'].map(sceneId => ({ bed: 'canonical',
    profileKey: 'synthetic', sceneId, admitted: true }));
  const stem = (c: typeof cells[number]) => `${c.bed}__${c.profileKey}__${c.sceneId}`;
  const preserved = cells.slice(0, 2).flatMap((c, i) => {
    const names = [stem(c) + '.html', ...(i === 0 ? [stem(c) + '.png'] : [])];
    return names.map(name => { const bytes = Buffer.from('synthetic ' + name);
      writeFileSync(join(output, name), bytes); return { path: join(output, name),
        bytes: bytes.length, sha256: sha(bytes) }; });
  });
  let fresh = 0, recovered = 0;
  const config = { output, binding: sha('synthetic-declaration'), cells, preserved,
    exporter: { command: 'python3', args: [exporter], timeout: 3000 },
    recoverRecord: async (cell: object, html: string) => {
      recovered++; return { ...cell, native: { source: 'recovered; no native read', html } }; },
    renderFresh: async (cell: object, _work: string) => {
      fresh++; return { html: 'fresh synthetic HTML', record: { ...cell, native: { source: 'new' } } }; } };
  return { root, output, config, stem, cells, counts: () => ({ fresh, recovered }),
    close: () => rmSync(root, { recursive: true, force: true }) };
}

test('regular file transport crosses pipe boundary with no input/output pipes', () => {
  const f = fixture();
  try {
    for (const size of [65535, 65536, 67100, 1048576]) {
      const input = join(f.root, `input-${size}`); writeFileSync(input, Buffer.alloc(size, 97));
      const output = join(f.root, `out-${size}`), error = output + '.log';
      fileChild({ ...f.config.exporter, input, output, error });
      assert.deepEqual(readFileSync(output), readFileSync(input));
    }
  } finally { f.close(); }
});

test('completed reuse and pending HTML export never invoke fresh/native renderer', async () => {
  const f = fixture();
  try {
    const result = await recover(f.config);
    assert.deepEqual(f.counts(), { fresh: 1, recovered: 2 });
    assert.equal(result.records.length, 3);
    assert.equal(readFileSync(join(f.output, f.stem(f.cells[0]!) + '.png'), 'utf8'),
      'synthetic canonical__synthetic__done.png');
    assert.equal(readFileSync(join(f.output, f.stem(f.cells[1]!) + '.png'), 'utf8'),
      'synthetic canonical__synthetic__pending.html');
    await recover({ ...f.config, renderFresh: async () => { throw Error('native reread'); },
      recoverRecord: async () => { throw Error('recovery repeated'); } });
    assert.deepEqual(f.counts(), { fresh: 1, recovered: 2 });
  } finally { f.close(); }
});

test('unadmitted entries stay UNMEASURED without any renderer invocation', async () => {
  const f = fixture();
  try {
    const result = await recover({ ...f.config, cells: [...f.cells,
      { bed: 'w39', profileKey: 'synthetic', sceneId: 'excluded', admitted: false,
        status: 'UNMEASURED', reason: 'unadmitted synthetic' }] });
    assert.equal(result.records.at(-1)!.status, 'UNMEASURED');
    assert.deepEqual(f.counts(), { fresh: 1, recovered: 2 });
  } finally { f.close(); }
});

test('partial export failure checkpoints first, preserves logs, resumes without rendering twice', async () => {
  const f = fixture();
  try {
    // A real child fails once, then the identical exporter succeeds on the next attempt.
    const marker = join(f.root, 'once');
    writeFileSync(f.config.exporter.args[0]!, `import os,sys\np=${JSON.stringify(marker)}\nif not os.path.exists(p):\n open(p,'x').close()\n sys.stdout.write('partial')\n sys.stderr.write('synthetic failure')\n sys.exit(9)\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n`);
    await assert.rejects(recover(f.config), /child failed/);
    const dir = join(f.output, '.recovery', f.stem(f.cells[1]!));
    assert.ok(existsSync(join(dir, 'checkpoint.json')));
    assert.equal(readFileSync(join(dir, 'export-0', 'stdout'), 'utf8'), 'partial');
    const result = await recover(f.config);
    assert.equal(result.records.length, 3);
    assert.deepEqual(f.counts(), { fresh: 1, recovered: 2 });
    assert.equal(readFileSync(join(dir, 'export-0', 'stderr'), 'utf8'), 'synthetic failure');
    assert.ok(existsSync(join(dir, 'export-1', 'result.json')));
  } finally { f.close(); }
});

test('changed preserved/checkpoint/output bytes, unknown files, and options refuse before work', async () => {
  for (const kind of ['preserved', 'checkpoint', 'output', 'unknown', 'binding', 'missing']) {
    const f = fixture();
    try {
      if (kind !== 'preserved' && kind !== 'unknown') await recover(f.config);
      const dir = join(f.output, '.recovery', f.stem(f.cells[1]!));
      if (kind === 'preserved') writeFileSync(f.config.preserved[0]!.path, 'changed');
      if (kind === 'checkpoint') writeFileSync(join(dir, 'checkpoint.json'), '{}');
      if (kind === 'output') writeFileSync(join(f.output, f.stem(f.cells[1]!) + '.png'), 'changed');
      if (kind === 'unknown') writeFileSync(join(f.output, 'stranger'), 'unknown');
      if (kind === 'missing') rmSync(join(dir, 'checkpoint.json.sha256'));
      const counts = f.counts();
      await assert.rejects(recover({ ...f.config,
        ...(kind === 'binding' ? { binding: sha('different-options') } : {}) }));
      assert.deepEqual(f.counts(), counts);
    } finally { f.close(); }
  }
});

test('timeout preserves partial child output and stderr without hanging', () => {
  const f = fixture();
  try {
    const input = join(f.root, 'input'); writeFileSync(input, 'x');
    assert.throws(() => fileChild({ command: 'python3', args: ['-c',
      'import sys,time; print("partial",flush=True); time.sleep(10)'], timeout: 100,
      input, output: join(f.root, 'partial'), error: join(f.root, 'error') }), /child failed/);
    assert.equal(readFileSync(join(f.root, 'partial'), 'utf8'), 'partial\n');
  } finally { f.close(); }
});

test('committed full-byte input pins reject working changes and newly committed replacements', () => {
  const f = fixture();
  try {
    execFileSync('git', ['init', '-q', f.root]);
    execFileSync('git', ['-C', f.root, 'config', 'user.email', 'synthetic@example.invalid']);
    execFileSync('git', ['-C', f.root, 'config', 'user.name', 'Synthetic Test']);
    const path = join(f.root, 'inputs.json'); writeFileSync(path, '{"freeze":"original"}');
    execFileSync('git', ['-C', f.root, 'add', 'inputs.json']);
    execFileSync('git', ['-C', f.root, 'commit', '-qm', 'Synthetic input']);
    const pin = pinCommitted(f.root, path); checkPins(f.root, [pin]);
    writeFileSync(path, '{"freeze":"replacement"}');
    assert.throws(() => checkPins(f.root, [pin]));
    execFileSync('git', ['-C', f.root, 'add', 'inputs.json']);
    execFileSync('git', ['-C', f.root, 'commit', '-qm', 'Synthetic replacement']);
    assert.throws(() => checkPins(f.root, [pin]));
    assert.throws(() => pinCommitted(f.root, join(f.root, 'untracked')));
  } finally { f.close(); }
});

test('recovered native distinguishes re-encoded display hash from original G0 fixture hash', () => {
  const png = Buffer.from('synthetic display bytes');
  const html = `<td><h2>Native</h2><img alt="Native" width="1" height="1" src="data:image/png;base64,${png.toString('base64')}"></td>`;
  const cell = { bed: 'canonical', profileKey: 'synthetic', sceneId: 'done' };
  const rows = [{ ...cell, status: 'RENDERED', nativeSha256: sha('different fixture bytes') }];
  const native = recoverNative(cell, html, rows);
  assert.equal(native.displayPngSha256, sha(png));
  assert.equal(native.fixturePngSha256, rows[0]!.nativeSha256);
  assert.equal(native.newNativeRead, false);
  assert.throws(() => recoverNative(cell, html.replace('alt="Native"', 'alt="Other"'), rows));
  assert.throws(() => recoverNative(cell, html, []));
  assert.throws(() => recoverNative({ ...cell, bed: 'w39' }, html, rows));
});

test('unchanged G0 exporter renders synthetic candidate panels through file FDs above pipe boundary', async () => {
  const { fileURLToPath } = await import('node:url');
  const { PNG } = await import('pngjs');
  const { renderAdmitted } = await import('./adapter');
  const f = fixture();
  try {
    const scenes = join(f.root, 'apps/reference-apple'); mkdirSync(scenes, { recursive: true });
    writeFileSync(join(scenes, 'scenes.json'), JSON.stringify({ split: { calibration: ['synthetic'] } }));
    writeFileSync(join(f.root, 'doc.json'), '{}');
    writeFileSync(join(f.root, 'candidate.json'), '{"candidate":true}');
    const documents = [{ kind: 'materialProfile', path: 'doc.json', sha256: sha('{}').slice(0, 12) }];
    const candidateDocuments = [{ kind: 'materialProfile', path: 'candidate.json',
      sha256: sha('{"candidate":true}').slice(0, 12) }];
    const pose = ['deviceScaleFactor=1', 'colorScheme=light', 'accessibility=browser-preferences'];
    const cell = { bed: 'canonical', profileKey: 'synthetic', sceneId: 'synthetic', documents, pose };
    const image = new PNG({ width: 128, height: 128 });
    let state = 72;
    for (let i = 0; i < image.data.length; i++) {
      state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
      image.data[i] = i % 4 === 3 ? 255 : state >>> 24;
    }
    const png = PNG.sync.write(image);
    for (const [name, docs] of [['shipped', documents], ['candidate', candidateDocuments]] as const) {
      const dir = join(f.root, name, 'synthetic/synthetic'); mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, 'synthetic__webgpu.png'), png);
      writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify({ sceneId: 'synthetic', renderer: 'webgpu',
        colorSpace: 'srgb', capturePath: `${pose.join(', ')}, materialProfile=${docs[0]!.path} sha256:${docs[0]!.sha256}` }));
    }
    const html = await renderAdmitted(cell, { repositoryRoot: f.root, captureRoot: join(f.root, 'shipped'),
      candidate: { captureRoot: join(f.root, 'candidate'), documents: candidateDocuments },
      readNative: async () => png });
    assert.ok(Buffer.byteLength(html!) > 67100);
    const input = join(f.root, 'sheet.html'); writeFileSync(input, html!);
    const output = join(f.root, 'sheet.png');
    fileChild({ command: 'python3.12', args: [fileURLToPath(new URL(
      '../../2026-09-27-w41-g0-declaration/sheets/export-png.py', import.meta.url))],
      timeout: 5000, input, output, error: join(f.root, 'export.log') });
    const rendered = PNG.sync.read(readFileSync(output));
    assert.ok(rendered.width > 3 * image.width);
    assert.ok(rendered.height > 2 * image.height);
    const recovered = recoverNative(cell, html!, [{ ...cell, status: 'RENDERED', nativeSha256: sha(png) }]);
    assert.equal(recovered.fixturePngSha256, sha(png));
    writeFileSync(join(f.root, 'candidate.json'), '{"stale":true}');
    await assert.rejects(renderAdmitted(cell, { repositoryRoot: f.root, captureRoot: join(f.root, 'shipped'),
      candidate: { captureRoot: join(f.root, 'candidate'), documents: candidateDocuments },
      readNative: async () => { throw Error('native must not be reopened for stale candidate'); } }), /shipped bytes/);
  } finally { f.close(); }
});

test('input binding chain rejects detached scope, seal, payload, document, and canonical freeze', async () => {
  const { validateChain } = await import('./recovery');
  const h = (s: string) => sha('synthetic-' + s);
  const scope = { path: 'scope.json', sha256: h('scope') };
  const row = { primaryCapture: '/synthetic/calval/p/s/s__webgpu.png',
    png: 'capture.png', pngSha256: h('png'), descriptor: 'cell.json', descriptorSha256: h('cell'),
    report: 'report.json', reportSha256: h('report') };
  const seal = { inputs: { 'scope.json': scope.sha256, 'active.json': h('active'), 'receded.json': h('receded') },
    profiles: { p: { material: 'active.json', receded: 'receded.json' } } };
  const capture = { png: row.primaryCapture, pngSha256: row.pngSha256,
    cellSha256: row.descriptorSha256, reportSha256: row.reportSha256 };
  const original = { preparation: { cells: ['p/s'] }, preparationPin: scope,
    authoritySha256: h('authority'), baseline: { preparationSha256: scope.sha256,
      authoritySha256: h('authority'), captures: { 'p/s': capture } },
    derived: { admissionScope: scope, sourceSeal: { path: 'seal.json', sha256: h('seal') },
      sourceRawInventory: { path: 'raw.json', sha256: h('raw') }, captureRoot: '/synthetic/calval',
      captures: { 'p/s': capture }, documents: { p: [
        { kind: 'materialProfile', path: 'active.json', sha256: h('active').slice(0, 12) },
        { kind: 'recededProfile', path: 'receded.json', sha256: h('receded').slice(0, 12) }] } },
    frozen: { sealSha256: h('seal'), files: { 'seal.json': h('seal'), 'raw.json': h('raw'),
      'capture.png': row.pngSha256, 'cell.json': row.descriptorSha256, 'report.json': row.reportSha256 } },
    raw: { sealSha256: h('seal'), cells: { 'p/s': row } }, seal,
    canonical: { sealSha256: h('canonical') }, canonicalSealPin: { path: 'canonical.json', sha256: h('canonical') } };
  validateChain(original);
  for (const mutate of [
    (b: typeof original) => { b.baseline.preparationSha256 = h('wrong'); },
    (b: typeof original) => { b.frozen.files['raw.json'] = h('wrong'); },
    (b: typeof original) => { b.frozen.files['cell.json'] = h('wrong'); },
    (b: typeof original) => { b.raw.cells['p/s'].primaryCapture = '/synthetic/blind/p/s/s__webgpu.png'; },
    (b: typeof original) => { b.derived.documents.p[1]!.sha256 = h('wrong').slice(0, 12); },
    (b: typeof original) => { b.canonical.sealSha256 = h('wrong'); },
    (b: typeof original) => { b.preparation.cells = []; },
  ]) {
    const changed = structuredClone(original); mutate(changed);
    assert.throws(() => validateChain(changed));
  }
});

test('fresh-cell exporter failure resumes checkpointed native provenance without another native read', async () => {
  const f = fixture();
  try {
    for (const pin of f.config.preserved) rmSync(pin.path);
    const config = { ...f.config, cells: f.cells.slice(2), preserved: [] };
    const marker = join(f.root, 'once');
    writeFileSync(config.exporter.args[0]!, `import os,sys\np=${JSON.stringify(marker)}\nif not os.path.exists(p):\n open(p,'x').close()\n sys.exit(5)\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n`);
    await assert.rejects(recover(config), /child failed/);
    assert.deepEqual(f.counts(), { fresh: 1, recovered: 0 });
    const result = await recover(config);
    assert.deepEqual(result.records[0]!.native, { source: 'new' });
    assert.deepEqual(f.counts(), { fresh: 1, recovered: 0 });
  } finally { f.close(); }
});

test('a completed inventory cannot silently regenerate a deleted output companion', async () => {
  const f = fixture();
  try {
    await recover(f.config);
    rmSync(join(f.output, f.stem(f.cells[1]!) + '.png'));
    await assert.rejects(recover(f.config), /missing completed output/);
  } finally { f.close(); }
});

test('recovered shipped panel refuses same-metadata replacement pixels but accepts equal pixels in a different PNG encoding', async () => {
  const { PNG } = await import('pngjs');
  const { renderAdmitted } = await import('./adapter');
  const { inspectCell } = await import('../../2026-09-27-w41-g0-declaration/sheets/sheets');
  const { recoverShipped } = await import('./recovery-core');
  const f = fixture();
  try {
    const scenes = join(f.root, 'apps/reference-apple'); mkdirSync(scenes, { recursive: true });
    writeFileSync(join(scenes, 'scenes.json'), JSON.stringify({ split: { calibration: ['synthetic'] } }));
    writeFileSync(join(f.root, 'doc.json'), '{}');
    const documents = [{ kind: 'materialProfile', path: 'doc.json', sha256: sha('{}').slice(0, 12) }];
    const pose = ['deviceScaleFactor=1', 'colorScheme=light', 'accessibility=browser-preferences'];
    const cell = { bed: 'canonical', profileKey: 'synthetic', sceneId: 'synthetic', documents, pose };
    const dir = join(f.root, 'capture/synthetic/synthetic'); mkdirSync(dir, { recursive: true });
    const path = join(dir, 'synthetic__webgpu.png');
    writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify({ sceneId: 'synthetic', renderer: 'webgpu',
      colorSpace: 'srgb', capturePath: `${pose.join(', ')}, materialProfile=doc.json sha256:${documents[0]!.sha256}` }));
    const image = new PNG({ width: 16, height: 16 });
    for (let i = 0; i < image.data.length; i++) image.data[i] = i % 4 === 3 ? 255 : (i * 73) % 256;
    const original = PNG.sync.write(image, { filterType: 0 }); writeFileSync(path, original);
    const html = (await renderAdmitted(cell, { repositoryRoot: f.root,
      captureRoot: join(f.root, 'capture'), readNative: async () => original }))!;
    const encodedDisplay = Buffer.from(html.match(/alt="Shipped WebGPU"[^>]+base64,([A-Za-z0-9+/=]+)"/)![1]!, 'base64');
    const replacementEncoding = PNG.sync.write(image, { filterType: 1 });
    assert.notEqual(sha(replacementEncoding), sha(original));
    writeFileSync(path, replacementEncoding);
    assert.equal(inspectCell(cell, f.root, join(f.root, 'capture')).status, 'MATCH');
    const recovered = recoverShipped(html, readFileSync(path));
    assert.equal(recovered.displayPngSha256, sha(encodedDisplay));
    assert.equal(recovered.currentCapturePngSha256, sha(replacementEncoding));
    assert.equal(recovered.originalCapturePngSha256, null);
    assert.equal(recovered.pixelsMatch, true);
    image.data[0] = image.data[0]! ^ 1;
    writeFileSync(path, PNG.sync.write(image));
    assert.equal(inspectCell(cell, f.root, join(f.root, 'capture')).status, 'MATCH');
    assert.throws(() => recoverShipped(html, readFileSync(path)), /preserved Shipped WebGPU pixels differ/);
    assert.throws(() => recoverShipped(html.replace('alt="Shipped WebGPU"', 'alt="Other"'), original),
      /unique embedded Shipped WebGPU PNG/);
    assert.throws(() => recoverShipped(html, PNG.sync.write(new PNG({ width: 8, height: 32 }))),
      /preserved Shipped WebGPU pixels differ/);
  } finally { f.close(); }
});

test('baseline authority binds the exact sealed v2 artifact, refusing v1 and never falling back', async () => {
  const { baselineAuthority } = await import('./recovery');
  const f = fixture();
  try {
    execFileSync('git', ['init', '-q', f.root]);
    execFileSync('git', ['-C', f.root, 'config', 'user.email', 'synthetic@example.invalid']);
    execFileSync('git', ['-C', f.root, 'config', 'user.name', 'Synthetic Test']);
    const dir = join(f.root, 'baseline'); mkdirSync(dir);
    const v1 = '{"epoch":"synthetic original"}', v2 = '{"epoch":"synthetic actual seal"}';
    writeFileSync(join(dir, 'authority.json'), v1);
    writeFileSync(join(dir, 'authority-v2.json'), v2);
    execFileSync('git', ['-C', f.root, 'add', 'baseline']);
    execFileSync('git', ['-C', f.root, 'commit', '-qm', 'Synthetic authorities']);
    const actual = baselineAuthority(f.root, f.root, sha(v2));
    assert.deepEqual(actual, { path: 'baseline/authority-v2.json', sha256: sha(v2) });
    assert.throws(() => baselineAuthority(f.root, f.root, sha(v1)), /committed full hash/);
    writeFileSync(join(dir, 'authority-v2.json'), v1);
    assert.throws(() => baselineAuthority(f.root, f.root, sha(v2)), /committed full hash/);
    rmSync(join(dir, 'authority-v2.json'));
    assert.throws(() => baselineAuthority(f.root, f.root, sha(v1)));
  } finally { f.close(); }
});
