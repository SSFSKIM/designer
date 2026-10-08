/** The production bridge on freshly generated SYNTHETIC material documents only.
 * No W50 candidate/native/reference/config path is an input. Output directories are external
 * temporary probe fixtures, not a fit point, execution root, seal or scientific observation.
 */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, realpathSync, writeFileSync } from 'node:fs';
import { isAbsolute, relative, resolve } from 'node:path';
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from '@vitrea/renderer-webgpu';
import { cssTierMappingSha256, resolvedDigest } from '../../../scripts/candidate-document.ts';
import { assembleCandidate, fixedGate0Joins, proveTransfer } from './runtime-bridge.ts';

const hash = (raw: string) => createHash('sha256').update(raw).digest('hex');
const scratch = realpathSync(process.argv[2]!);
const repo = realpathSync(new URL('../../../../../', import.meta.url).pathname);
if (!isAbsolute(scratch) || !relative(repo, scratch).startsWith('..')) {
  throw Error('Synthetic runtime probe requires external scratch');
}
function write(path: string, value: unknown) {
  const raw = JSON.stringify(value, null, 2)+'\n';
  writeFileSync(path, raw, { flag: 'wx' });
  return { path, sha256: hash(raw) };
}
function baseline(position: number, suffix: string, changedSampling = false) {
  const directory = resolve(scratch, `synthetic-${position}-${suffix}`);
  mkdirSync(directory);
  const endpoints: Record<string, {path: string; sha256: string}> = {};
  const mapping = { blurSigmaScale: 1 };
  for (const scheme of ['light', 'dark'] as const) {
    let base = DEFAULT_MATERIAL_PROFILE;
    for (const pose of ['active', 'receded'] as const) {
      const patch = { lowEndStrength: 0,
        ...(changedSampling && scheme === 'dark' && pose === 'active' ? { sizeScatterFloor2x: .5 } : {}) };
      base = withMaterialOverrides(base, patch);
      const filename = `${pose}.${scheme}.json`;
      const pin = write(resolve(directory, filename), {
        profileKey: `apple-macos-27.0-1x-${scheme}-standard-glass${position.toFixed(3)}${pose === 'receded' ? '-receded' : ''}`,
        patch, resolvedMaterialSha256: resolvedDigest(base),
        ...(pose === 'active' ? { cssTierMapping: mapping } : {}),
      });
      endpoints[`${pose}.${scheme}`] = { path: filename, sha256: pin.sha256 };
    }
  }
  return write(resolve(directory, 'candidate.json'), {
    kind: 'vitrea-candidate-material-document', schemaVersion: 1,
    name: `synthetic-runtime-probe-${position}-${suffix}`, platform: 'macOS 27.0',
    glassTintAmount: position, endpoints, cssTierMappingSha256: cssTierMappingSha256(mapping),
  });
}
const charts = {
  active: [[.05,.1,.15,.2],[.06,.11,.16,.21],[.07,.12,.17,.22]],
  receded: [[.04,.09,.14,.19],[.05,.1,.15,.2],[.06,.11,.16,.21]],
};
const provenance = ['synthetic runtime probe point; no W50 observation'];
const branches = { fixedJoinEndpoints: 0, builtCandidates: 0, heldTransfers: 0, heldMutationRefusals: 0 };
for (const position of [.25,.5]) {
  const before = baseline(position, 'before');
  const joins = await fixedGate0Joins(before);
  assert.equal(joins.position, position);
  for (const values of Object.values(joins.joins) as {span:number;dpr:number;value:number}[][]) {
    assert.equal(values.length, 386);
    assert.equal(new Set(values.map(r => `${r.span}/${r.dpr}`)).size, 386);
    assert.ok(values.every(r => Number.isFinite(r.value)));
    branches.fixedJoinEndpoints++;
  }
  const candidate = await assembleCandidate(before, charts, resolve(scratch, `built-${position}`), provenance);
  branches.builtCandidates++;
  const proof = await proveTransfer(before, candidate);
  assert.equal(proof.position, position);
  assert.equal(proof.capturedCandidate.sha256, before.sha256);
  assert.equal(proof.evaluationCandidate.sha256, candidate.sha256);
  branches.heldTransfers++;
  const different = baseline(position, 'changed-sampling', true);
  const changed = await assembleCandidate(different, charts, resolve(scratch, `changed-${position}`), provenance);
  await assert.rejects(proveTransfer(before, changed), /held material\/sampling/);
  branches.heldMutationRefusals++;
}
process.stdout.write(JSON.stringify({status:'SYNTHETIC_PRODUCTION_BRIDGE_EXERCISED', branches, pixels:'NONE'})+'\n');
