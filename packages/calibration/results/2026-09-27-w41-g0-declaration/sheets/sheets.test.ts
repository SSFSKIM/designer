import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { PNG } from 'pngjs';
import { enumerateCells, inspectCell, differencePanel, renderCell, configurationState } from './sheets';

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'w41-sheets-'));
  const active = 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json';
  const receded = 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json';
  mkdirSync(join(root, 'packages/calibration/profiles'), { recursive: true });
  writeFileSync(join(root, active), '{}');
  writeFileSync(join(root, receded), '{"pose":"receded"}');
  const sha = (s: string) => createHash('sha256').update(s).digest('hex').slice(0, 12);
  const documents = [
    { kind: 'materialProfile', path: active, sha256: sha('{}') },
    { kind: 'recededProfile', path: receded, sha256: sha('{"pose":"receded"}') },
  ];
  const pose = ['deviceScaleFactor=1', 'colorScheme=light', 'accessibility=browser-preferences'];
  const cell = { bed: 'canonical', profileKey: 'profile', sceneId: 'scene__inactive', documents, pose };
  mkdirSync(join(root, 'apps/reference-apple'), { recursive: true });
  writeFileSync(join(root, 'apps/reference-apple/scenes.json'), JSON.stringify({
    split: { calibration: [cell.sceneId], validation: [], holdout: [], recorded: [], probe: [] },
  }));
  const captureRoot = join(root, 'captures');
  const dir = join(captureRoot, cell.profileKey, cell.sceneId);
  mkdirSync(dir, { recursive: true });
  const metadata = { sceneId: cell.sceneId, renderer: 'webgpu', colorSpace: 'srgb',
    capturePath: 'playwright 151.0.7922.34 element screenshot of #stage, channel=chromium ' +
      '--enable-unsafe-webgpu --enable-features=Vulkan,WebGPU, viewport=320x200 ' +
      `${pose[0]}, ${pose[1]}, animations=disabled, frames=8, ${pose[2]}, ` +
      documents.map(d => `${d.kind}=${d.path} sha256:${d.sha256}`).join(', ') };
  const meta = () => writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify(metadata));
  const png = join(dir, `${cell.sceneId}__webgpu.png`);
  return { root, cell, captureRoot, metadata, meta, png, close: () => rmSync(root, { recursive: true }) };
}
function image(byte: number, width = 1) {
  return { width, height: 1, data: new Uint8Array(Array.from({ length: width }, () => [byte, byte, byte, 255]).flat()) };
}
function png(byte: number) {
  const value = new PNG({ width: 1, height: 1 });
  value.data = Buffer.from([byte, byte, byte, 255]);
  return PNG.sync.write(value);
}

test('inventory distinguishes absent PNG/metadata and never decodes present pixels', () => {
  const f = fixture();
  try {
    assert.equal(inspectCell(f.cell, f.root, f.captureRoot).status, 'UNMEASURED');
    f.meta();
    assert.equal(inspectCell(f.cell, f.root, f.captureRoot).status, 'UNMEASURED');
    writeFileSync(f.png, 'NOT PNG: inventory must not open this');
    assert.equal(inspectCell(f.cell, f.root, f.captureRoot).status, 'MATCH');
  } finally { f.close(); }
});

test('receded stale, missing, extra, malformed and wrong-cell metadata all refuse', () => {
  const f = fixture();
  try {
    writeFileSync(f.png, png(0));
    const good = f.metadata.capturePath;
    for (const bad of [good.replace(f.cell.documents[1]!.sha256, '000000000000'),
      good.split(', ')[0]!, `${good}, recededProfile=extra sha256:111111111111`,
      good.replace('sha256:', 'sha256:0')]) {
      f.metadata.capturePath = bad; f.meta();
      assert.throws(() => inspectCell(f.cell, f.root, f.captureRoot), /provenance|document/);
    }
    f.metadata.capturePath = good; f.metadata.sceneId = 'other'; f.meta();
    assert.throws(() => inspectCell(f.cell, f.root, f.captureRoot), /scene/);
    f.metadata.sceneId = f.cell.sceneId; f.meta();
    writeFileSync(join(f.root, f.cell.documents[1]!.path), 'changed');
    assert.throws(() => inspectCell(f.cell, f.root, f.captureRoot), /shipped/);
  } finally { f.close(); }
});

test('enumeration folds tier rows but retains CSS-only cells and W39 membership', () => {
  const f = fixture();
  try {
    const web = { capturePath: f.metadata.capturePath, renderer: 'css' };
    const rows = [{ key: { profileKey: 'profile', sceneId: 'one', web } },
      { key: { profileKey: 'profile', sceneId: 'one', web: { ...web, renderer: 'webgpu' } } },
      { key: { profileKey: 'profile', sceneId: 'two', web } }];
    const cells = enumerateCells(rows, [{ profileKey: 'profile', sceneId: 'w39', role: 'validation' }]);
    assert.equal(cells.length, 3);
    assert.equal(cells.filter(c => c.bed === 'canonical').length, 2);
    assert.equal(cells.find(c => c.bed === 'w39')?.role, 'validation');
    assert.deepEqual(cells.find(c => c.bed === 'w39')?.pose, f.cell.pose);
    assert.deepEqual(cells.find(c => c.sceneId === 'two')?.pose, f.cell.pose);
    assert.throws(() => enumerateCells(rows, [{ profileKey: 'unknown', sceneId: 'w39' }]), /profile/);
  } finally { f.close(); }
});

test('a same-scene capture copied across profiles with shared documents is refused by pose', () => {
  const f = fixture();
  try {
    const rows = ['profile', 'other-profile'].map(profileKey => ({ key: {
      profileKey, sceneId: f.cell.sceneId, web: { renderer: 'webgpu',
        capturePath: profileKey === 'profile' ? f.metadata.capturePath :
          f.metadata.capturePath.replace('deviceScaleFactor=1', 'deviceScaleFactor=2') },
    } }));
    const cells = enumerateCells(rows, [{ profileKey: 'other-profile', sceneId: 'w39' }]);
    const other = cells.find(c => c.bed === 'canonical' && c.profileKey === 'other-profile')!;
    assert.deepEqual(cells.find(c => c.bed === 'w39')?.pose, other.pose);
    assert.equal(other.pose[0], 'deviceScaleFactor=2');
    const dir = join(f.captureRoot, other.profileKey, other.sceneId);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify(f.metadata));
    writeFileSync(join(dir, `${other.sceneId}__webgpu.png`), 'NOT PNG');
    assert.throws(() => inspectCell(other, f.root, f.captureRoot), /pose/);
    f.metadata.capturePath = f.metadata.capturePath.replace('deviceScaleFactor=1', 'deviceScaleFactor=2');
    writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify(f.metadata));
    assert.equal(inspectCell(other, f.root, f.captureRoot).status, 'MATCH');
    for (const [from, to] of [
      ['colorScheme=light', 'colorScheme=dark'],
      ['accessibility=browser-preferences',
        'accessibility=reducedTransparency+increasedContrast (others explicitly off)'],
    ] as const) {
      const wrong = { ...other, pose: other.pose.map(p => p === from ? to : p) };
      assert.throws(() => inspectCell(wrong, f.root, f.captureRoot), /pose/);
    }
  } finally { f.close(); }
});

test('missing pose in capture or matrix row is never an agreement', () => {
  const f = fixture();
  try {
    f.meta(); writeFileSync(f.png, 'NOT PNG');
    for (const clause of f.cell.pose) {
      f.metadata.capturePath = f.metadata.capturePath.replace(`${clause}, `, '');
      f.meta();
      assert.throws(() => inspectCell(f.cell, f.root, f.captureRoot), /pose/);
      f.metadata.capturePath = f.metadata.capturePath.replace('viewport=320x200 ',
        `viewport=320x200 ${clause}, `);
    }
    const row = { key: { profileKey: f.cell.profileKey, sceneId: f.cell.sceneId,
      web: { renderer: 'webgpu', capturePath: f.metadata.capturePath } } };
    for (const clause of f.cell.pose) {
      const incomplete = { key: { ...row.key,
        web: { ...row.key.web, capturePath: row.key.web.capturePath.replace(`${clause}, `, '') } } };
      assert.throws(() => enumerateCells([incomplete], []), /pose/);
    }
  } finally { f.close(); }
});

test('profile pose disagreements refuse ambiguous W39 inheritance', () => {
  const f = fixture();
  try {
    const row = { key: { profileKey: f.cell.profileKey, sceneId: 'one',
      web: { renderer: 'webgpu', capturePath: f.metadata.capturePath } } };
    const differing = { key: { ...row.key, sceneId: 'two', web: { ...row.key.web,
      capturePath: row.key.web.capturePath.replace('deviceScaleFactor=1', 'deviceScaleFactor=2') } } };
    assert.throws(() => enumerateCells([row, differing],
      [{ profileKey: f.cell.profileKey, sceneId: 'w39' }]), /conflicting.*pose/);
  } finally { f.close(); }
});

test('OKLab delta is zero for equality, amplified and saturated at eight, not RGB distance', () => {
  assert.deepEqual([...differencePanel(image(0), image(0)).data], [0, 0, 0, 255]);
  assert.deepEqual([...differencePanel(image(0), image(255)).data], [255, 255, 255, 255]);
  // Neutral encoded code 1 has linear Y=1/(255*12.92); OKLab L=cuberoot(Y).
  const expected = Math.round(Math.cbrt(1 / (255 * 12.92)) * 8 * 255);
  assert.equal(differencePanel(image(0), image(1)).data[0], expected);
  assert.throws(() => differencePanel(image(0), image(0, 2)), /dimension/);
});

test('sheet output has labeled triptych, delta beneath, and an empty candidate', async () => {
  const f = fixture();
  try {
    f.meta(); writeFileSync(f.png, png(0));
    const html = await renderCell(f.cell, { repositoryRoot: f.root, captureRoot: f.captureRoot,
      readNative: async () => png(0) });
    assert.match(html, /Native/); assert.match(html, /Shipped WebGPU/);
    assert.match(html, /Candidate/); assert.match(html, /EMPTY.*G2/);
    assert.match(html, /ΔE × 8/); assert.match(html, /data:image\/png;base64/);
    const missing = await renderCell(f.cell, { repositoryRoot: f.root, captureRoot: f.captureRoot,
      readNative: async () => undefined });
    assert.match(missing, /UNMEASURED/);
    // Refusal precedes native-byte access, including when the PNG is absent.
    f.metadata.capturePath = ''; f.meta();
    let read = false;
    await assert.rejects(renderCell(f.cell, { repositoryRoot: f.root, captureRoot: f.captureRoot,
      readNative: async () => { read = true; return png(0); } }), /document|provenance/);
    assert.equal(read, false);
  } finally { f.close(); }
});


test('canonical holdout candidate refuses before all pixels even if caller mislabels its role', async () => {
  const f = fixture();
  try {
    f.meta(); writeFileSync(f.png, png(0));
    writeFileSync(join(f.root, 'apps/reference-apple/scenes.json'), JSON.stringify({
      split: { calibration: [], validation: [], holdout: [f.cell.sceneId], recorded: [], probe: [] },
    }));
    let opened = false;
    await assert.rejects(renderCell({ ...f.cell, role: 'calibration' }, {
      repositoryRoot: f.root, captureRoot: f.captureRoot,
      readNative: async () => { opened = true; return png(0); },
      candidate: { documents: f.cell.documents, captureRoot: f.captureRoot },
    }), /holdout.*configuration/i);
    assert.equal(opened, false);
    // Shipped-only has no candidate exposure; the G0 batch command separately excludes holdout.
    const shippedOnly = await renderCell(f.cell, { repositoryRoot: f.root,
      captureRoot: f.captureRoot, readNative: async () => png(0) });
    assert.match(shippedOnly, /EMPTY.*G2/);
  } finally { f.close(); }
});


test('canonical candidate requires the exact logged documents AND renderer-source configuration', async () => {
  const f = fixture();
  try {
    f.meta(); writeFileSync(f.png, png(0));
    writeFileSync(join(f.root, 'apps/reference-apple/scenes.json'), JSON.stringify({
      split: { calibration: [], validation: [], holdout: [f.cell.sceneId], recorded: [], probe: [] },
    }));
    const profiles = join(f.root, 'packages/calibration/profiles');
    for (const suffix of ['', '-receded']) writeFileSync(join(profiles,
      `apple-macos-27.0-1x-dark-standard-glass0.5${suffix}.json`), '{}');
    mkdirSync(join(f.root, 'packages/renderer-webgpu/src/wgsl'), { recursive: true });
    mkdirSync(join(f.root, 'packages/platform-web/src'), { recursive: true });
    for (const name of ['material.ts', 'renderer.ts', 'passes.ts']) {
      writeFileSync(join(f.root, 'packages/renderer-webgpu/src', name), 'synthetic');
    }
    for (const name of ['optics.ts', 'css-tier.ts']) {
      writeFileSync(join(f.root, 'packages/platform-web/src', name), 'synthetic');
    }
    const logDir = join(f.root, 'packages/calibration/results/holdout-configuration');
    mkdirSync(logDir, { recursive: true });
    const state = configurationState(f.root);
    writeFileSync(join(logDir, 'configuration-log.json'), JSON.stringify({ reads: [state] }));
    const options = { repositoryRoot: f.root, captureRoot: f.captureRoot,
      readNative: async () => png(0),
      candidate: { documents: f.cell.documents, captureRoot: f.captureRoot } };
    assert.match(await renderCell(f.cell, options), /Candidate ΔE/);
    writeFileSync(join(f.root, 'packages/renderer-webgpu/src/material.ts'), 'moved');
    await assert.rejects(renderCell(f.cell, options), /holdout.*configuration/i);
    writeFileSync(join(f.root, 'packages/renderer-webgpu/src/material.ts'), 'synthetic');
    writeFileSync(join(profiles, 'apple-macos-27.0-1x-dark-standard-glass0.5.json'), 'moved');
    await assert.rejects(renderCell(f.cell, options), /holdout.*configuration/i);
  } finally { f.close(); }
});
