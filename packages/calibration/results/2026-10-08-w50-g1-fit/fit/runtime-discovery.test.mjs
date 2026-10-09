import { test } from 'node:test';
import assert from 'node:assert/strict';
import { discoverRuntime } from './runtime-discovery.mjs';

test('separate runtime discovery exercises production joins, builder and held-material transfer', () => {
  const result = discoverRuntime();
  assert.equal(result.schema, 'w50-fit-runtime-closure-1');
  assert.equal(result.exercise.status, 'SYNTHETIC_PRODUCTION_BRIDGE_EXERCISED');
  assert.deepEqual(result.exercise.branches, {
    fixedJoinEndpoints: 4, builtCandidates: 2, heldTransfers: 2, heldMutationRefusals: 2,
  });
  assert.ok(result.sources.some(p => p.path.endsWith('/fit/runtime-bridge.ts')));
  assert.ok(result.sources.some(p => p.path.endsWith('/owner/node-guard.mjs')));
  assert.ok(result.sources.some(p => p.path.endsWith('/web/node-guard.mjs')));
  assert.ok(result.sources.some(p => p.path.endsWith('/scripts/candidate-document.ts')));
  assert.match(result.node.sha256, /^[a-f0-9]{64}$/);
  assert.equal(result.pixels, 'NONE');
});
