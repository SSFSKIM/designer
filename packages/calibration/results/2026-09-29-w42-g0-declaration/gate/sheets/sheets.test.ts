import assert from 'node:assert/strict';
import { test } from 'node:test';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { PNG } from 'pngjs';
import { createImage, decodePng } from '../../../../src/image';
import { freshOutsideRepositories, PROFILES, renderRun, sheetHtml, type Document, type RunConfig,
  type Strata } from './sheets';

const sha = (s: string | Buffer) => createHash('sha256').update(s).digest('hex');
const PROFILE = PROFILES[0]!;
const ACTIVE = 'packages/calibration/profiles/active.json';
const RECEDED = 'packages/calibration/profiles/receded.json';
const CANDIDATE = 'scratch/candidate-receded.json';
const png = (width: number, height: number, value: number) => {
  const image = new PNG({ width, height });
  image.data = Buffer.from(new Uint8Array(width * height * 4).map((_, i) => i % 4 === 3 ? 255 : value));
  return PNG.sync.write(image);
};

/** A synthetic repository: one calibration and one holdout scene over a solid, both with a
 * fixture and a capture in every tree, so a path formed for the holdout cell would be seen. */
function repository() {
  const scratch = mkdtempSync(join(tmpdir(), 'w42-gate-sheets-'));
  const root = join(scratch, 'repository');
  const write = (path: string, bytes: string | Buffer) => {
    mkdirSync(join(scratch, path, '..'), { recursive: true });
    writeFileSync(join(scratch, path), bytes);
  };
  const inRepository = (path: string) => join('repository', path);
  write(inRepository(ACTIVE), 'active'); write(inRepository(RECEDED), 'receded');
  write(inRepository(CANDIDATE), 'candidate');
  write(inRepository('apps/reference-apple/scenes.json'), JSON.stringify({ canvas: { width: 8, height: 6 },
    backgrounds: { flat: { kind: 'solid', srgb: [9, 9, 9] } },
    components: { box: { kind: 'rrect', size: [4, 2], radius: 0 } },
    scenes: [{ id: 'a__rest', background: 'flat', component: 'box', state: 'rest' },
      { id: 'h__rest', background: 'flat', component: 'box', state: 'rest' }],
    profiles: [{ key: PROFILE, scenes: ['a__rest', 'h__rest'] }],
    split: { calibration: ['a__rest'], validation: [], holdout: ['h__rest'], recorded: [], probe: [] } }));
  const generation = JSON.stringify({ cells: [] });
  write(inRepository('packages/calibration/results/generations/g.json'), generation);
  write(inRepository('packages/calibration/results/generations/index.json'), JSON.stringify({
    files: { 'g.json': { status: 'current', sha256: sha(generation),
      documents: [{ path: RECEDED, sha256: sha('receded').slice(0, 12) },
        { path: ACTIVE, sha256: sha('active').slice(0, 12) }] } },
    currentByProfile: Object.fromEntries(PROFILES.map(p => [p, 'g.json'])) }));
  const shipped: Document[] = [{ kind: 'materialProfile', path: ACTIVE, sha256: sha('active').slice(0, 12) },
    { kind: 'recededProfile', path: RECEDED, sha256: sha('receded').slice(0, 12) }];
  const candidate: Document[] = [shipped[0]!,
    { kind: 'recededProfile', path: CANDIDATE, sha256: sha('candidate').slice(0, 12) }];
  const capture = (tree: string, sceneId: string, docs: Document[], value: number) => {
    const dir = join(tree, PROFILE, sceneId);
    write(join(dir, `${sceneId}__webgpu.png`), png(8, 6, value));
    write(join(dir, 'cell__webgpu.json'), JSON.stringify({ sceneId, renderer: 'webgpu', colorSpace: 'srgb',
      samplingBackend: 'gpu-texture', capturePath: 'viewport=8x6 deviceScaleFactor=1, colorScheme=light, ' +
        'animations=disabled, accessibility=browser-preferences, ' +
        docs.map(d => `${d.kind}=${d.path} sha256:${d.sha256}`).join(' sections=x, ') }));
  };
  for (const sceneId of ['a__rest', 'h__rest']) {
    write(inRepository(join('apps/reference-apple/fixtures', PROFILE, `${sceneId}.png`)), png(8, 6, 100));
    capture('shipped', sceneId, shipped, 90);
    capture('candidate', sceneId, candidate, 95);
  }
  const strata = (cells: { sceneId: string; role: string }[]) => ({ schema: 'test', charter: 'test',
    tier: 'webgpu', profiles: [PROFILE], inputs: {}, sources: {}, shippedDocuments: { [PROFILE]: shipped },
    strata: { uniform: { bed: 'canonical', rule: 'test', roles: ['calibration', 'validation'],
      backgroundKind: 'solid', backgrounds: ['flat'], tinted: 'none', excludedByRole: {}, noCurrentRow: [],
      cells: cells.map(c => ({ profileKey: PROFILE, ...c, pose: 'rest', tint: null })) } } }) as unknown as Strata;
  const config = (output: string, docs = candidate): RunConfig => ({ label: 'test',
    outputRoot: join(scratch, output), candidateDocuments: { [PROFILE]: docs },
    canonical: { shippedRoots: [join(scratch, 'shipped')], candidateRoot: join(scratch, 'candidate') } });
  return { root, scratch, shipped, candidate, capture, strata, config,
    close: () => rmSync(scratch, { recursive: true }) };
}

test('a capture naming any documents but the declared candidate pair is refused', () => {
  const r = repository();
  try {
    const cell = [{ sceneId: 'a__rest', role: 'calibration' }];
    // The candidate tree names the candidate pair; declaring the shipped pair as the candidate refuses.
    assert.throws(() => renderRun(r.config('out-1', r.shipped), r.strata(cell), { repositoryRoot: r.root }),
      /document provenance differs/);
    // A candidate document whose bytes exist nowhere refuses before any capture is read.
    const ghost = [r.shipped[0]!, { kind: 'recededProfile', path: CANDIDATE, sha256: 'abcdefabcdef' }];
    assert.throws(() => renderRun(r.config('out-2', ghost), r.strata(cell), { repositoryRoot: r.root }),
      /no file holds/);
    // A shipped capture naming the candidate's receded document refuses too.
    r.capture('shipped', 'a__rest', r.candidate, 90);
    assert.throws(() => renderRun(r.config('out-3'), r.strata(cell), { repositoryRoot: r.root }),
      /document provenance differs/);
  } finally { r.close(); }
});

test('a holdout cell is dropped on scenes.json\'s role before any path is formed', () => {
  const r = repository();
  try {
    const paths: string[] = [];
    // The declaration lies about h__rest's role; scenes.json's role decides, and it is holdout.
    const result = renderRun(r.config('out'), r.strata([{ sceneId: 'h__rest', role: 'calibration' },
      { sceneId: 'a__rest', role: 'calibration' }]), { repositoryRoot: r.root, onPath: p => paths.push(p) });
    assert.equal(result.dropped['uniform'], 1);
    assert.deepEqual(result.records.map(x => x.sceneId), ['a__rest']);
    assert.ok(paths.length >= 3 && paths.every(p => !p.includes('h__rest')), paths.join('\n'));
    // A declared role the stratum does not match refuses rather than being silently read.
    assert.throws(() => renderRun(r.config('out-2'), r.strata([{ sceneId: 'a__rest', role: 'validation' }]),
      { repositoryRoot: r.root }), /is not the declared validation/);
  } finally { r.close(); }
});

test('the sheet draws native | shipped | candidate with both ΔE panels, through G0\'s exporter', () => {
  const r = repository();
  try {
    const result = renderRun(r.config('out'), r.strata([{ sceneId: 'a__rest', role: 'calibration' }]),
      { repositoryRoot: r.root });
    const record = result.records[0];
    assert.equal(record.status, 'RENDERED');
    assert.equal(record.candidateEqualsShippedBytes, false);
    assert.equal(record.distances.bodyPixels, 8);
    assert.equal(record.distances.bodyMovedPixels, 8);
    assert.equal(record.distances.bodyCloserFraction, 1);
    const html = readFileSync(join(r.scratch, 'out', record.sheet.html), 'utf8');
    for (const label of ['Native', 'Shipped', 'Candidate', 'Shipped ΔE × 8', 'Candidate ΔE × 8']) {
      assert.match(html, new RegExp(`<h2>${label}</h2><img `));
    }
    const sheet = decodePng(readFileSync(join(r.scratch, 'out', record.sheet.png)));
    assert.ok(sheet.width > 3 * 8 && sheet.height > 2 * 6);
    // Identity: a candidate equal to shipped draws the same ΔE panel in both columns.
    const image = (v: number) => createImage(8, 6, new Uint8Array(8 * 6 * 4).map((_, i) => i % 4 === 3 ? 255 : v));
    const identity = sheetHtml('identity', image(100), image(90), image(90), []);
    const panels = [...identity.matchAll(/<h2>(?:Shipped|Candidate) ΔE × 8<\/h2><img [^>]*src="([^"]+)"/g)];
    assert.equal(panels.length, 2);
    assert.equal(panels[0]![1], panels[1]![1]);
    // A missing candidate keeps the table's shape and says so.
    assert.match(sheetHtml('missing', image(100), image(90), undefined, []), /<h2>Candidate<\/h2><p>UNMEASURED<\/p>/);
  } finally { r.close(); }
});

test('output inside a git work tree, or one that exists, is refused', () => {
  const r = repository();
  try {
    execFileSync('git', ['init', '-q', join(r.scratch, 'git')]);
    assert.throws(() => freshOutsideRepositories(join(r.scratch, 'git', 'a', 'b'), r.root),
      /inside a git work tree/);
    assert.throws(() => freshOutsideRepositories(join(r.scratch, 'shipped'), r.root), /fresh/);
    assert.throws(() => freshOutsideRepositories(join(r.root, 'x'), r.root), /inside the repository/);
    freshOutsideRepositories(join(r.scratch, 'fresh', 'run-1'), r.root);
  } finally { r.close(); }
});
