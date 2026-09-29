/** Canonical cal/val metadata only. Never run compare or open fixture/capture pixels here. */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { plan } from '../sheets/adapter';
import { SHIPPED_MATERIAL_PROFILE_DOCUMENTS } from '../../../../platform-web/src/material-document';
import { canonicalRole } from '../../2026-09-27-w41-g0-declaration/sheets/sheets';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(HERE, '../../../../..');
const sha = (bytes: Uint8Array) => createHash('sha256').update(bytes).digest('hex');
export function capturePlan() {
  const candidate = 'packages/calibration/results/2026-09-27-w41-g1-identification/' +
    'body-leaf/candidate/apple-macos-27.0-1x-light-standard-glass0.5-receded.json';
  const reviewed = JSON.parse(readFileSync(resolve(HERE, '../candidate-capture/reviewed-inputs.json'), 'utf8'));
  const candidateSha = sha(readFileSync(resolve(ROOT, candidate)));
  if (reviewed.files[candidate] !== candidateSha) throw new Error('candidate differs from reviewed frozen E3');
  const spec = JSON.parse(readFileSync(resolve(ROOT, 'apps/reference-apple/scenes.json'), 'utf8'));
  const cells = plan().records.filter(c => c.bed === 'canonical').map(cell => {
    const role = canonicalRole(cell.sceneId, ROOT);
    if (!['calibration', 'validation'].includes(role)) throw new Error('cal/val only');
    const scene = spec.scenes.find((s: { id: string }) => s.id === cell.sceneId);
    if (!scene) throw new Error('missing declared scene');
    const scheme = cell.profileKey.includes('-dark-') ? 'dark' : 'light';
    const platform = cell.profileKey.startsWith('apple-macos-26.5-') ? 'macOS 26.5' : 'macOS 27.0';
    const runtime = SHIPPED_MATERIAL_PROFILE_DOCUMENTS.find(d => d.platform === platform);
    if (!runtime) throw new Error('unshipped platform');
    const runtimeInactive = scene.state === 'inactive' && cell.documents.length === 1;
    const endpoint = (runtimeInactive ? runtime.receded : runtime.active)[scheme];
    return { ...cell, role, state: scene.state, canvas: spec.canvas, background: scene.background,
      runtimeRecededPatch: runtimeInactive ? endpoint.patch : null,
      selectedEndpoint: { name: runtime.name, platform: runtime.platform,
        ...(endpoint.profileKey ? { profileKey: endpoint.profileKey } : {}),
        ...(endpoint.resolvedMaterialSha256 ? { resolvedMaterialSha256: endpoint.resolvedMaterialSha256 } : {}) },
      shippedDocuments: cell.documents,
      documents: cell.documents.map(doc => cell.profileKey.startsWith('apple-macos-27.0-') &&
        cell.profileKey.includes('-light-') && doc.kind === 'recededProfile' ?
        { ...doc, path: candidate, sha256: candidateSha.slice(0, 12) } : doc) };
  });
  return { schema: 'w41-canonical-diagnostic-plan-1',
    label: 'diagnostic candidate WEB for EYE; not a canonical read or G2 material',
    candidateSha256: candidateSha, nativePayloadReads: 0, cells };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.length !== 2) throw new Error('metadata planner accepts no capture or role overrides');
  console.log(JSON.stringify(capturePlan(), null, 2));
}
