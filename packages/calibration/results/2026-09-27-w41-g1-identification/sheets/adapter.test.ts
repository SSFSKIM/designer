import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { renderAdmitted, diagnosticSheet } from './adapter';

test('forged W39 holdout and unadmitted cells cannot invoke native callback', async () => {
  const root = mkdtempSync(join(tmpdir(), 'g1-sheet-'));
  mkdirSync(join(root, 'apps/reference-apple'), { recursive: true });
  writeFileSync(join(root, 'apps/reference-apple/scenes.json'), JSON.stringify({
    split: { calibration: [], validation: [], holdout: ['closed'] } }));
  let reads = 0;
  const options = { repositoryRoot: root, captureRoot: join(root, 'absent'),
    readNative: async () => { reads++; throw new Error('native must stay closed'); } };
  const cell = { bed: 'w39', profileKey: 'apple-macos-27.0-1x-dark-standard-glass0.5',
    sceneId: 'g128-c-capsule-circular-160x96__rest', role: 'calibration',
    documents: [], pose: [] }; // Real W39 holdout, forged as calibration.
  try {
    await assert.rejects(renderAdmitted(cell, options), /calibration\/validation/);
    await assert.rejects(renderAdmitted({ ...cell, sceneId: 'factor-y0-c12-h0-colour__inactive',
      profileKey: 'not-a-W39-profile' }, options), /calibration\/validation/);
    await assert.rejects(renderAdmitted({ ...cell, bed: 'canonical', sceneId: 'closed' },
      options), /calibration\/validation/);
    assert.equal(await renderAdmitted({ ...cell, sceneId: 'phase-1x-zero__rest' },
      options), undefined); // Planned W39 cal/val, excluded by baseline preparation.
    assert.equal(reads, 0);
  } finally { rmSync(root, { recursive: true }); }
});

test('actual sheet adapter retains honest absent candidate and rejects stale provenance before native', async () => {
  const { createHash } = await import('node:crypto');
  const { PNG } = await import('pngjs');
  const root = mkdtempSync(join(tmpdir(), 'g1-sheet-panels-'));
  const documents = [{ kind: 'materialProfile', path: 'doc.json',
    sha256: createHash('sha256').update('{}').digest('hex').slice(0, 12) }];
  writeFileSync(join(root, 'doc.json'), '{}');
  const pose = ['deviceScaleFactor=1', 'colorScheme=light', 'accessibility=browser-preferences'];
  const cell = { bed: 'w39', profileKey: 'apple-macos-27.0-1x-dark-standard-glass0.5',
    sceneId: 'factor-y0-c12-h0-colour__inactive', role: 'holdout', documents, pose };
  // The W39 plan admits this member even though the caller forges the opposite role.
  const captureRoot = join(root, 'capture');
  const dir = join(captureRoot, cell.profileKey, cell.sceneId);
  mkdirSync(dir, { recursive: true });
  const image = new PNG({ width: 1, height: 1 }); image.data = Buffer.from([40, 50, 60, 255]);
  const bytes = PNG.sync.write(image);
  writeFileSync(join(dir, `${cell.sceneId}__webgpu.png`), bytes);
  const metadata = { sceneId: cell.sceneId, renderer: 'webgpu', colorSpace: 'srgb',
    capturePath: `${pose.join(', ')}, materialProfile=doc.json sha256:${documents[0]!.sha256}` };
  writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify(metadata));
  let reads = 0;
  const options = { repositoryRoot: root, captureRoot,
    readNative: async () => { reads++; return bytes; } };
  try {
    const html = await renderAdmitted(cell, options);
    assert.match(html!, /EMPTY — awaiting G2 document/);
    assert.equal((html!.match(/data:image\/png;base64,/g) ?? []).length, 3);
    assert.equal(reads, 1);
    writeFileSync(join(root, 'doc.json'), '{"stale":true}');
    await assert.rejects(renderAdmitted(cell, options), /shipped bytes/);
    assert.equal(reads, 1);
  } finally { rmSync(root, { recursive: true }); }
});


test('diagnostic labeling preserves embedded comparison pixels and does not add candidate data', () => {
  const original = '<h1>canonical test</h1><table><img src="data:image/png;base64,abcd"></table>';
  const labeled = diagnosticSheet(original);
  assert.match(labeled, /diagnostic candidate WEB for EYE/);
  assert.match(labeled, /not a canonical read or G2 material/);
  assert.equal(labeled.slice(labeled.indexOf('<table>')), original.slice(original.indexOf('<table>')));
});
