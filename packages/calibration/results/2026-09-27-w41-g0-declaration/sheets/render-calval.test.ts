import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { PNG } from 'pngjs';
import { renderCalval } from './render-calval';

test('G0 batch renders canonical cal/val only, never holdout, probe, or W39 pixels', async () => {
  const root = mkdtempSync(join(tmpdir(), 'w41-batch-'));
  try {
    const fixtures = join(root, 'fixtures');
    const captures = join(root, 'captures');
    const output = join(root, 'sheets');
    mkdirSync(join(root, 'apps/reference-apple'), { recursive: true });
    const roles = ['calibration', 'validation', 'holdout', 'probe'];
    const split = Object.fromEntries(roles.map(r => [r, [r]]));
    writeFileSync(join(root, 'apps/reference-apple/scenes.json'), JSON.stringify({ split }));
    const doc = 'material.json'; writeFileSync(join(root, doc), '{}');
    const sha256 = createHash('sha256').update('{}').digest('hex').slice(0, 12);
    const pose = ['deviceScaleFactor=1', 'colorScheme=light', 'accessibility=browser-preferences'];
    const cells = [...roles.map(sceneId => ({ bed: 'canonical', sceneId })),
      { bed: 'w39', sceneId: 'w39' }].map(c => ({ ...c, profileKey: 'profile', pose,
        documents: [{ kind: 'materialProfile', path: doc, sha256 }] }));
    const image = new PNG({ width: 1, height: 1 }); image.data = Buffer.from([127, 127, 127, 255]);
    mkdirSync(join(fixtures, 'profile'), { recursive: true });
    for (const cell of cells) {
      const allowed = ['calibration', 'validation'].includes(cell.sceneId);
      const bytes = allowed ? PNG.sync.write(image) : Buffer.from('FORBIDDEN INVALID PNG');
      writeFileSync(join(fixtures, 'profile', `${cell.sceneId}.png`), bytes);
      const dir = join(captures, 'profile', cell.sceneId); mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, `${cell.sceneId}__webgpu.png`), bytes);
      writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify({ sceneId: cell.sceneId,
        renderer: 'webgpu', colorSpace: 'srgb', capturePath:
          `${pose.join(', ')}, materialProfile=${doc} sha256:${sha256}` }));
    }
    const report = await renderCalval(cells, { repositoryRoot: root, fixtureRoot: fixtures,
      captureRoot: captures, outputRoot: output });
    assert.equal(report.filter(r => r.status === 'RENDERED').length, 2);
    assert.equal(report.find(r => r.sceneId === 'holdout')?.status, 'SKIPPED');
    assert.equal(report.find(r => r.sceneId === 'w39')?.status, 'UNMEASURED');
    assert.equal(readdirSync(output).length, 2);
    const html = readFileSync(join(output, 'profile__validation.html'), 'utf8');
    assert.match(html, /Shipped ΔE × 8/);
    assert.match(html, /EMPTY.*G2/);
    const pngOutput = join(root, 'sheets-with-png');
    await renderCalval(cells, { repositoryRoot: root, fixtureRoot: fixtures,
      captureRoot: captures, outputRoot: pngOutput, png: true });
    assert.equal(readdirSync(pngOutput).length, 4);
    const raster = PNG.sync.read(readFileSync(join(pngOutput, 'profile__validation.png')));
    assert.ok(raster.width > 3 && raster.height > 2);
  } finally { rmSync(root, { recursive: true }); }
});
