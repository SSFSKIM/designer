import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { test } from 'node:test';
import { readCandidateDocument } from '../../../scripts/candidate-document.ts';
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from '@vitrea/renderer-webgpu';
import { buildCandidate, CHART_LEAVES } from './candidate.ts';
import { checkInheritance } from '../owner/referee.ts';
import { checkRecordApplicability } from '../owner/intrinsic.ts';

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
const provenance = ['synthetic test point; no W50 observation'];
// DL5o: the inherited leaves of the shipped receded documents that carry no baseline record.
const HOLDS: Record<string, string[]> = { '0.25': [], '0.5': ['backdropToneAnchorX', 'backdropToneBlackStrength',
  'optics.clear.rimLevelGain', 'outerShadow.liftAmplitude', 'outerShadow.thinOcclusionDark'] };
const added = (next: Record<string, any>, old: Record<string, any>) =>
  Object.keys(next).filter(key => !Object.hasOwn(old, key)).sort();
const endpoint = (pin: { path: string }, slot: string) =>
  load(join(dirname(pin.path), load(pin.path).endpoints[slot].path));
/** The receded methods and active fitting records the owner reads, from the candidate's entries. */
function x76(before: { path: string }, pin: { path: string; sha256: string }) {
  const [active, receded] = [endpoint(pin, 'active.dark'), endpoint(pin, 'receded.dark')];
  const [beforeActive, beforeReceded] = [endpoint(before, 'active.dark'), endpoint(before, 'receded.dark')];
  const methods: Record<string, any> = {};
  for (const [leaf, entry] of Object.entries<any>(receded.entries)) {
    if (entry.status === 'held' && Array.isArray(entry.reading)) methods[leaf] = { held: entry.reading };
    else if ((CHART_LEAVES as readonly string[]).includes(leaf)) methods[leaf] = entry.method;
  }
  const activeEntries = Object.fromEntries(Object.entries<any>(active.entries)
    .filter(([leaf, entry]) => entry.status === 'measured'));
  const activeResolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active.patch);
  return { methods, beforeActive, activeEntries, activeResolved, inheritance: checkInheritance({
    activeResolved, activePatch: active.patch, activeEntries, beforePatch: beforeReceded.patch,
    beforeEntries: beforeReceded.entries ?? {}, candidatePatch: receded.patch, methods }) };
}
const held = (patch: Record<string, unknown>) =>
  Object.fromEntries(Object.entries(patch).filter(([key]) => !leaves.includes(key)));

for (const position of [.25, .5]) test(`assembles complete held-material candidate at ${position}`, () => {
  const scratch = mkdtempSync(join(tmpdir(), 'w50-candidate-builder-'));
  try {
    const before = baseline(position);
    const pin = buildCandidate(before, charts, join(scratch, 'point'), provenance);
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
        // Baseline records are kept verbatim; DL5o adds only the chart and hold records.
        for (const [key, value] of Object.entries(old.entries)) assert.deepEqual(next.entries[key], value);
        assert.deepEqual(added(next.entries, old.entries),
          [...leaves, ...(pose === 'receded' ? HOLDS[String(position)]! : [])].sort());
        for (const leaf of leaves) {
          assert.equal(next.entries[leaf].status, 'measured');
          assert.deepEqual(next.entries[leaf].value, next.patch[leaf]);
          assert.ok(next.entries[leaf].method.length > 1 && next.entries[leaf].method.includes(provenance[0]));
        }
        for (const leaf of pose === 'receded' ? HOLDS[String(position)]! : []) {
          assert.equal(next.entries[leaf].status, 'held');
          assert.ok(next.entries[leaf].reading.every((line: string) => line.trim() !== ''));
        }
        assert.equal(next.candidateAssembly.status, 'UNSEALED_CANDIDATE');
        if (pose === 'receded') {
          assert.equal(next.appliesOver, 'active.dark.json');
          assert.equal(next.resolvedOverActiveDocument, 'active.dark.json');
        }
      }
    }
    const second = buildCandidate(before, charts, join(scratch, 'same-point'), provenance);
    assert.equal(second.sha256, pin.sha256); // destination/time cannot alter scientific identity
    assert.throws(() => buildCandidate(before, charts, join(scratch, 'point'), provenance), /write-once/);
    assert.throws(() => buildCandidate(pin, charts, join(scratch, 'not-a-baseline'), provenance), /inert/);
    // X76 on the receded endpoint reads within from the candidate's own records alone.
    const { inheritance } = x76(before, pin);
    assert.equal(inheritance.verdict, 'within', JSON.stringify(inheritance.missing));
    assert.deepEqual(inheritance.moved, [...leaves].sort());
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
      assert.throws(() => buildCandidate(before, value, out, provenance));
      assert.equal(existsSync(out), false);
    }
    assert.throws(() => buildCandidate({ ...before, sha256: '0'.repeat(64) }, charts,
      join(scratch, 'bad-pin'), provenance), /baseline/);
    for (const bad of [undefined, [], [''], ['  '], 'line', [1]]) {
      assert.throws(() => buildCandidate(before, charts, join(scratch, 'bad-provenance'), bad), /provenance/);
      assert.equal(existsSync(join(scratch, 'bad-provenance')), false);
    }
    const changed = join(scratch, 'changed.json');
    writeFileSync(changed, '{}\n');
    assert.throws(() => buildCandidate({ path: changed, sha256: hash(readFileSync(changed)) },
      charts, join(scratch, 'bad-kind'), provenance));
    assert.equal(existsSync(join(scratch, 'bad-kind')), false);
  } finally { rmSync(scratch, { recursive: true, force: true }); }
});

for (const position of [.25, .5]) test(`identity candidate at ${position} carries only the DL5o holds`, () => {
  const scratch = mkdtempSync(join(tmpdir(), 'w50-candidate-identity-'));
  try {
    const before = baseline(position);
    const pin = buildCandidate(before, null, join(scratch, 'identity'), provenance);
    assert.match(load(pin.path).name, /^w50-identity-/);
    for (const slot of ['active.dark', 'receded.dark']) {
      const [old, next] = [endpoint(before, slot), endpoint(pin, slot)];
      assert.deepEqual(next.patch, old.patch);
      assert.equal(next.resolvedMaterialSha256, old.resolvedMaterialSha256);
      assert.deepEqual(added(next.entries, old.entries), slot === 'receded.dark' ? HOLDS[String(position)] : []);
    }
    const { inheritance, beforeActive, activeResolved } = x76(before, pin);
    assert.equal(inheritance.verdict, 'within', JSON.stringify(inheritance.missing));
    assert.deepEqual(inheritance.moved, []);
    if (position === .25) {
      // The leaf-keyed 0.25 history reads MEASURED on the frozen applicability check as is.
      const active = endpoint(pin, 'active.dark'), receded = endpoint(pin, 'receded.dark');
      const retained = Object.fromEntries(Object.entries<any>(beforeActive.entries)
        .filter(([, entry]) => entry.status === 'measured'));
      const result = checkRecordApplicability({ activeSha256: load(pin.path).endpoints['active.dark'].sha256,
        recededSha256: load(pin.path).endpoints['receded.dark'].sha256, activeResolved,
        beforeResolved: withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, beforeActive.patch),
        beforeEntries: beforeActive.entries, recededRecords: { endpointSha256:
          load(pin.path).endpoints['receded.dark'].sha256, methods: x76(before, pin).methods },
        activeRecords: { endpointSha256: load(pin.path).endpoints['active.dark'].sha256,
          retainedMeasuredEntries: retained, fittedEntries: {} } });
      assert.equal(result.state, 'MEASURED');
      assert.deepEqual([active.patch, receded.patch].map(p => p.lowEndStrength), [undefined, undefined]);
    }
  } finally { rmSync(scratch, { recursive: true, force: true }); }
});
