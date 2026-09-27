/** Exercise the runtime CPU-resolved thin anchors, not a second transcription. */
import { readFileSync } from 'node:fs';
import { outerShadowThinOcclusion, outerShadowOcclusionAt, sizeThickness,
  outerShadowSigmaPx } from '../../../../renderer-webgpu/src/material.ts';
import type { MaterialProfile } from '../../../../renderer-webgpu/src/material.ts';
const materials = JSON.parse(readFileSync(new URL(
  '../../2026-09-26-w39-g2-identification/instrument/resolved-materials.json', import.meta.url),
'utf8')) as Record<string, MaterialProfile>;
const rows = [];
for (const [endpoint, material] of Object.entries(materials)) {
  if (endpoint === 'default') continue;
  for (const span of [0, 32, 44, 64, 96, 112, 128, 144, 160, 200]) {
    for (const luminance of [0, .02, .04, .06, .3, .74, .8, .891, 1]) {
      const thickness = sizeThickness(span, material);
      rows.push({ endpoint, span, luminance, thickness,
        thin: outerShadowThinOcclusion(luminance, material.outerShadow),
        occlusion: outerShadowOcclusionAt(material.outerShadow, luminance, span, thickness, material),
        sigma: outerShadowSigmaPx(material.outerShadow, span) });
    }
  }
}
console.log(JSON.stringify(rows, null, 2));
