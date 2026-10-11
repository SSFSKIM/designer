/** Replay production native-fixture admission, never capture or compare a material. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {selectFixtures, admitNative} from
  '../../2026-10-08-w50-g1-current3/canonical/native-admission.ts';

const output = resolve(process.argv[2]!);
const root = resolve(output, 'native-fixtures');
const read = (path: string) => JSON.parse(readFileSync(path, 'utf8'));
const pin = (path: string) => ({path, sha256: createHash('sha256').update(readFileSync(path)).digest('hex')});
const scenes = read(resolve(output, 'scenes.json'));
const inventory = read(resolve(output, 'inventory.json'));
const manifestPin = pin(resolve(root, 'manifest.json'));
let count = 0;
for (const profile of scenes.profiles) {
  const native = profile.scenes.map((scene: string) => {
    const row = inventory.cells.find((r: {profile: string; scene: string}) =>
      r.profile === profile.key && r.scene === scene);
    return {scene, ...row.nativeEvidence};
  });
  const request = {profile: profile.key, scenes: profile.scenes, sets: ['calibration'], native,
    fixtures: {path: root, manifest: manifestPin}};
  const selected = selectFixtures(request);
  assert.equal(admitNative(scenes, selected.manifest, selected.root, request).status, 'ADMITTED');
  const changed = structuredClone(selected.manifest);
  const member = changed.profiles.find(p => p.profileKey === profile.key)!;
  // A fixture that omits its body must not count as a native material reading.
  (member.fixtures[0] as {materialRendered: boolean}).materialRendered = false;
  assert.throws(() => admitNative(scenes, changed, selected.root, request));
  count += native.length;
}
assert.equal(count, 8);
console.log(JSON.stringify({admittedSyntheticCells: count}));
