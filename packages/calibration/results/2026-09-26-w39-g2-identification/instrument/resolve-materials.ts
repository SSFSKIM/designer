/** W39 numerical inputs resolved by the runtime's own merge, never copied fitted constants. */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from '../../../../renderer-webgpu/src/material';
const here = fileURLToPath(new URL('.', import.meta.url));
const profiles = fileURLToPath(new URL('../../../profiles/', import.meta.url));
const out: Record<string, unknown> = { default: DEFAULT_MATERIAL_PROFILE };
for (const scheme of ['light', 'dark']) {
  const stem = `apple-macos-27.0-1x-${scheme}-standard-glass0.5`;
  const active = JSON.parse(readFileSync(profiles + stem + '.json', 'utf8'));
  const receded = JSON.parse(readFileSync(profiles + stem + '-receded.json', 'utf8'));
  const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active.patch);
  out[scheme + '-active'] = material;
  out[scheme + '-inactive'] = withMaterialOverrides(material, receded.patch);
}
writeFileSync(here + 'resolved-materials.json', JSON.stringify(out, null, 2) + '\n', { flag: 'wx' });
