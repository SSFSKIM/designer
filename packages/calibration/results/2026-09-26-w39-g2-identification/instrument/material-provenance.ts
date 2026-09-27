/** Add a provenance sidecar without rewriting the already-recorded material input. */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { DEFAULT_MATERIAL_PROFILE, MATERIAL_DIGEST_RULE_VERSION,
  materialDigestInput, withMaterialOverrides } from '../../../../renderer-webgpu/src/material';
const here = fileURLToPath(new URL('.', import.meta.url));
const root = fileURLToPath(new URL('../../../../../', import.meta.url));
const profiles = root + 'packages/calibration/profiles/';
const sha = (bytes: string | Buffer) => createHash('sha256').update(bytes).digest('hex');
const sorted = (value: unknown): unknown => Array.isArray(value) ? value.map(sorted)
  : value !== null && typeof value === 'object'
    ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => [k, sorted(v)])) : value;
const materialBytes = readFileSync(here + 'resolved-materials.json');
const materials = JSON.parse(materialBytes.toString());
const documents = [];
for (const scheme of ['light', 'dark']) {
  const stem = `apple-macos-27.0-1x-${scheme}-standard-glass0.5`;
  const a = JSON.parse(readFileSync(profiles + stem + '.json', 'utf8'));
  const active = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, a.patch);
  for (const pose of ['active', 'inactive']) {
    const file = stem + (pose === 'inactive' ? '-receded' : '') + '.json';
    const bytes = readFileSync(profiles + file);
    const document = JSON.parse(bytes.toString());
    const resolved = pose === 'active' ? active : withMaterialOverrides(active, document.patch);
    if (JSON.stringify(resolved) !== JSON.stringify(materials[`${scheme}-${pose}`]))
      throw new Error('Recorded material is not the runtime resolution: ' + file);
    const digest = sha(JSON.stringify(sorted(materialDigestInput(resolved)))).slice(0, 16);
    if (digest !== document.resolvedMaterialSha256) throw new Error('Material digest mismatch: ' + file);
    documents.push({ path: 'packages/calibration/profiles/' + file, profileKey: document.profileKey,
      fileSha256: sha(bytes), contentDigest12: sha(bytes).slice(0, 12),
      resolvedMaterialSha256: digest, resolvedMaterialSha256Rule: document.resolvedMaterialSha256Rule });
  }
}
const sourceRevision = execFileSync('git', ['-C', root, 'rev-parse', '8169209d'], { encoding: 'utf8' }).trim();
const sources = ['packages/renderer-webgpu/src/material.ts', 'packages/renderer-webgpu/src/color.ts',
  'packages/renderer-webgpu/src/wgsl/optics.ts'];
const sourceFiles = sources.map(path => {
  const bytes = readFileSync(root + path);
  if (!bytes.equals(execFileSync('git', ['-C', root, 'show', `${sourceRevision}:${path}`])))
    throw new Error('Renderer source no longer matches resolution revision: ' + path);
  return { path, sha256: sha(bytes) };
});
const sidecar = { schema: 'w39-g2-resolved-materials-provenance-1',
  materialsFile: 'instrument/resolved-materials.json', materialsSha256: sha(materialBytes),
  resolverScriptSha256: sha(readFileSync(here + 'resolve-materials.ts')),
  identityTableRuleVersion: MATERIAL_DIGEST_RULE_VERSION, rendererSourceRevision: sourceRevision,
  sourceFiles, documents };
writeFileSync(here + 'resolved-materials.provenance.json', JSON.stringify(sidecar, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ materialsSha256: sidecar.materialsSha256,
  sidecarSha256: sha(readFileSync(here + 'resolved-materials.provenance.json')), documents: documents.length }));
