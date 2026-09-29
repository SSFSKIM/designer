import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { createImage } from '../../../src/image';
import { canonicalCells, distances, exportPng, inspectCapture, sheetHtml, type Document } from './sheets';

const sha12 = (s: string) => createHash('sha256').update(s).digest('hex').slice(0, 12);
const ACTIVE = 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json';
const RECEDED = 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json';

function repository() {
  const root = mkdtempSync(join(tmpdir(), 'w41-g2-sheets-'));
  mkdirSync(join(root, 'packages/calibration/profiles'), { recursive: true });
  mkdirSync(join(root, 'packages/calibration/results/2026-09-29-w41-g2-landing/retired-documents'), { recursive: true });
  mkdirSync(join(root, 'apps/reference-apple'), { recursive: true });
  writeFileSync(join(root, ACTIVE), 'active');
  writeFileSync(join(root, RECEDED), 'sealed');
  writeFileSync(join(root, 'packages/calibration/results/2026-09-29-w41-g2-landing/retired-documents',
    `apple-macos-27.0-1x-light-standard-glass0.5-receded.${sha12('retired')}.json`), 'retired');
  writeFileSync(join(root, 'apps/reference-apple/scenes.json'), JSON.stringify({ split: {
    calibration: ['a__inactive'], validation: [], holdout: ['h__inactive'], recorded: [], probe: [] } }));
  const pre: Document[] = [{ kind: 'materialProfile', path: ACTIVE, sha256: sha12('active') },
    { kind: 'recededProfile', path: RECEDED, sha256: sha12('retired') }];
  const now: Document[] = [pre[0]!, { kind: 'recededProfile', path: RECEDED, sha256: sha12('sealed') }];
  const capture = (tree: string, docs: Document[], sceneId = 'a__inactive') => {
    const dir = join(root, tree, 'profile', sceneId);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, `${sceneId}__webgpu.png`), 'png');
    writeFileSync(join(dir, 'cell__webgpu.json'), JSON.stringify({ sceneId, renderer: 'webgpu', colorSpace: 'srgb',
      samplingBackend: 'gpu-texture', capturePath: 'viewport=320x200 deviceScaleFactor=1, colorScheme=light, ' +
        'animations=disabled, accessibility=browser-preferences, ' +
        docs.map(d => `${d.kind}=${d.path} sha256:${d.sha256}`).join(' sections=x, ') }));
  };
  return { root, pre, now, capture, close: () => rmSync(root, { recursive: true }) };
}

test('a retired receded clause resolves to the seal\'s retired copy, and nothing else is admitted', () => {
  const r = repository();
  try {
    r.capture('pre', r.pre);
    r.capture('now', r.now);
    assert.equal(inspectCapture(join(r.root, 'pre'), 'profile', 'a__inactive', r.pre, r.root)?.documents[1]?.sha256,
      sha12('retired'));
    assert.deepEqual(inspectCapture(join(r.root, 'now'), 'profile', 'a__inactive', r.now, r.root)?.pose,
      ['deviceScaleFactor=1', 'colorScheme=light', 'accessibility=browser-preferences']);
    assert.throws(() => inspectCapture(join(r.root, 'pre'), 'profile', 'a__inactive', r.now, r.root), /names/);
    const stale = [r.pre[0]!, { kind: 'recededProfile', path: RECEDED, sha256: sha12('neither') }];
    r.capture('stale', stale);
    assert.throws(() => inspectCapture(join(r.root, 'stale'), 'profile', 'a__inactive', stale, r.root), /no file holds/);
    assert.equal(inspectCapture(join(r.root, 'absent'), 'profile', 'a__inactive', r.now, r.root), undefined);
  } finally { r.close(); }
});

test('holdout is dropped by role before any path is formed; a stage set that disagrees refuses', () => {
  const r = repository();
  try {
    const stage = (cells: object[]) => {
      const path = join(r.root, 'membership.json');
      writeFileSync(path, JSON.stringify({ active: { sha256: '85ad7f7e3e0d' }, receded: { sha256: '003940b4c7da' },
        cells }));
      return path;
    };
    const cell = (sceneId: string, fixtureSet: string, renderer = 'webgpu') =>
      ({ profileKey: 'profile', sceneId, fixtureSet, renderer });
    const result = canonicalCells(stage([cell('a__inactive', 'calibration'), cell('h__inactive', 'holdout'),
      cell('a__inactive', 'calibration', 'css')]), r.root);
    assert.deepEqual(result, { declared: 2, holdout: 1,
      cells: [{ profileKey: 'profile', sceneId: 'a__inactive', role: 'calibration' }] });
    assert.throws(() => canonicalCells(stage([cell('h__inactive', 'probe')]), r.root), /is not holdout/);
  } finally { r.close(); }
});

test('distances split the region the seal moved from the rest', () => {
  const px = (...bytes: number[][]) => createImage(bytes.length, 1, new Uint8Array(bytes.flat()));
  const native = px([100, 100, 100, 255], [50, 50, 50, 255]);
  const pre = px([100, 100, 100, 255], [90, 90, 90, 255]);
  const now = px([100, 100, 100, 255], [60, 60, 60, 255]);
  const d = distances(native, pre, now);
  assert.equal(d.changedPixels, 1);
  assert.equal(d.closerFraction, 1);
  assert.ok(d.changedMeanDeltaENow! < d.changedMeanDeltaEPre!);
  assert.equal(distances(native, undefined, now).changedPixels, undefined);
});

test('the sheet keeps G0\'s table shape, so G0\'s exporter draws the relabelled columns', () => {
  const r = repository();
  try {
    const image = (v: number) => createImage(4, 3, new Uint8Array(4 * 3 * 4).map((_, i) => i % 4 === 3 ? 255 : v));
    for (const [name, pre] of [['full', image(90)], ['now-only', undefined]] as const) {
      const html = sheetHtml(`W41 G2 / ${name}`, image(100), pre, image(95), ['note'], 'UNMEASURED: none');
      assert.match(html, /<h2>Shipped pre-W41<\/h2>/);
      assert.match(html, /<h2>Shipped now \(E3\)<\/h2>/);
      writeFileSync(join(r.root, `${name}.html`), html);
      exportPng(join(r.root, `${name}.html`), join(r.root, `${name}.png`));
      assert.deepEqual([...readFileSync(join(r.root, `${name}.png`)).subarray(1, 4)], [0x50, 0x4e, 0x47]);
    }
    assert.throws(() => sheetHtml('bad', image(1), createImage(1, 1, new Uint8Array(4)), image(1), []),
      /dimensions differ/);
  } finally { r.close(); }
});
