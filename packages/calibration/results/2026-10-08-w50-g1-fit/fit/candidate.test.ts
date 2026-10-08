import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { test } from 'node:test';
import { readCandidateDocument } from '../../../scripts/candidate-document.ts';
import { buildCandidate } from './candidate.ts';

const hash = (raw: Buffer | string) => createHash('sha256').update(raw).digest('hex');
const load = (path: string) => JSON.parse(readFileSync(path, 'utf8'));
const baseline = (position: number) => {
  const path = resolve(import.meta.dirname,
    `../inputs/current-material/${position === .25 ? 'glass025' : 'glass05'}/candidate.json`);
  return { path, sha256: hash(readFileSync(path)) };
};
// Deliberately synthetic ordinals: these tests never read native observations or select a fit.
const charts = {
  active: [[.10, .12, .18, .24], [.11, .13, .19, .25], [.12, .14, .20, .26]],
  receded: [[.05, .08, .14, .20], [.06, .09, .15, .21], [.07, .10, .16, .22]],
};
const leaves = ['lowEndStrength', 'lowEnd44', 'lowEnd96', 'lowEnd160'];
const held = (patch: Record<string, unknown>) =>
  Object.fromEntries(Object.entries(patch).filter(([key]) => !leaves.includes(key)));

for (const position of [.25, .5]) test(`assembles complete held-material candidate at ${position}`, () => {
  const scratch = mkdtempSync(join(tmpdir(), 'w50-candidate-builder-'));
  try {
    const before = baseline(position);
    const pin = buildCandidate(before, charts, join(scratch, 'point'));
    assert.equal(pin.sha256, hash(readFileSync(pin.path)));
    const result = readCandidateDocument(pin.path).document;
    assert.equal(result.glassTintAmount, position);
    const original = load(before.path);
    const candidate = load(pin.path);
    for (const slot of ['active.light', 'active.dark', 'receded.light', 'receded.dark']) {
      const oldBytes = readFileSync(join(dirname(before.path), original.endpoints[slot].path));
      const nextBytes = readFileSync(join(dirname(pin.path), candidate.endpoints[slot].path));
      const old = JSON.parse(oldBytes.toString());
      const next = JSON.parse(nextBytes.toString());
      if (slot.endsWith('.light')) assert.deepEqual(nextBytes, oldBytes);
      else {
        const pose = slot.startsWith('active') ? 'active' : 'receded';
        assert.deepEqual(held(next.patch), held(old.patch));
        assert.deepEqual(next.cssTierMapping, old.cssTierMapping);
        assert.equal(next.patch.lowEndStrength, 1);
        assert.deepEqual([next.patch.lowEnd44, next.patch.lowEnd96, next.patch.lowEnd160], charts[pose]);
        assert.deepEqual(next.entries, old.entries); // assembly does not invent measurement records
        assert.equal(next.candidateAssembly.status, 'UNSEALED_CANDIDATE');
        if (pose === 'receded') {
          assert.equal(next.appliesOver, 'active.dark.json');
          assert.equal(next.resolvedOverActiveDocument, 'active.dark.json');
        }
      }
    }
    const second = buildCandidate(before, charts, join(scratch, 'same-point'));
    assert.equal(second.sha256, pin.sha256); // destination/time cannot alter scientific identity
    assert.throws(() => buildCandidate(before, charts, join(scratch, 'point')), /write-once/);
    assert.throws(() => buildCandidate(pin, charts, join(scratch, 'not-a-baseline')), /inert/);
    assert.equal(existsSync(join(scratch, 'not-a-baseline')), false);
  } finally { rmSync(scratch, { recursive: true, force: true }); }
});

test('refuses malformed, foreign or changed inputs before creating candidate files', () => {
  const scratch = mkdtempSync(join(tmpdir(), 'w50-candidate-invalid-'));
  try {
    const before = baseline(.25);
    const invalid = [
      { ...charts, active: [[.2, .1, .3, .4], ...charts.active.slice(1)] },
      { ...charts, active: [[NaN, .1, .3, .4], ...charts.active.slice(1)] },
      { ...charts, active: [[-.1, .1, .3, .4], ...charts.active.slice(1)] },
      { ...charts, receded: charts.receded.slice(1) },
      { ...charts, extra: charts.active },
    ];
    for (const [i, value] of invalid.entries()) {
      const out = join(scratch, String(i));
      assert.throws(() => buildCandidate(before, value, out));
      assert.equal(existsSync(out), false);
    }
    assert.throws(() => buildCandidate({ ...before, sha256: '0'.repeat(64) }, charts,
      join(scratch, 'bad-pin')), /baseline/);
    const changed = join(scratch, 'changed.json');
    writeFileSync(changed, '{}\n');
    assert.throws(() => buildCandidate({ path: changed, sha256: hash(readFileSync(changed)) },
      charts, join(scratch, 'bad-kind')));
    assert.equal(existsSync(join(scratch, 'bad-kind')), false);
  } finally { rmSync(scratch, { recursive: true, force: true }); }
});
