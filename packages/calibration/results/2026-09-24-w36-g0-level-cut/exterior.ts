/** Same native-mask exterior before/after; guarded pixel transport (§5.178 clause 4). */
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { componentRegion, decodePng, extractSilhouette, distanceToSeeds,
  type DeclaredComponent, type CanvasSize } from "../../src/index";
import { DEFAULT_SILHOUETTE_THRESHOLD, DEFAULT_SILHOUETTE_CHROMA_THRESHOLD } from "../../cli/measure";
const here = import.meta.dirname;
for (const name of ["exterior-check.json"]) {
  if (existsSync(resolve(here, name))) throw new Error(`Refuse to overwrite recorded ${name}`);
}
const projection = JSON.parse(readFileSync(resolve(here, "projection.json"), "utf8"));
const rows = [];
for (const item of projection) {
  if (item.origin !== "canonical") continue;
  const p = spawnSync("python3.12", [resolve(here, "export-candidate.py"), item.cell],
    { encoding: "utf8", maxBuffer: 30 * 1024 * 1024 });
  if (p.status !== 0) throw new Error(p.stderr);
  const input = JSON.parse(p.stdout);
  const native = decodePng(Buffer.from(input.native, "base64"));
  const background = decodePng(Buffer.from(input.background, "base64"));
  const old = decodePng(Buffer.from(input.web, "base64"));
  const candidate = decodePng(Buffer.from(input.candidate, "base64"));
  const region = componentRegion(input.component as DeclaredComponent,
    { canvas: input.canvas as CanvasSize, scale: input.scale, width: native.width, height: native.height });
  const sil = extractSilhouette(native, { kind: "luminance-delta", background,
    threshold: DEFAULT_SILHOUETTE_THRESHOLD, chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
    region: region.silhouette });
  const nativeDistance = distanceToSeeds(sil.mask, native.width, native.height);
  const declaredDistance = distanceToSeeds(region.silhouette.mask, native.width, native.height);
  let count = 0, changed = 0, maxDelta = 0, nativeBlack = 0, candidateNonzero = 0;
  for (let i = 0; i < sil.mask.length; i++) {
    // The comparison lies outside BOTH silhouettes. A hole or empty native
    // extraction must not turn body pixels into an exterior claim.
    if (nativeDistance[i]! < 3 * input.scale || declaredDistance[i]! < 3 * input.scale) continue;
    count++;
    let delta = 0;
    for (let c = 0; c < 3; c++) delta = Math.max(delta,
      Math.abs(old.data[4 * i + c]! - candidate.data[4 * i + c]!));
    if (delta > 0) changed++;
    maxDelta = Math.max(maxDelta, delta);
    if ([0, 1, 2].every(c => background.data[4 * i + c] === 0 && native.data[4 * i + c] === 0)) {
      nativeBlack++;
      if ([0, 1, 2].some(c => candidate.data[4 * i + c] !== 0)) candidateNonzero++;
    }
  }
  rows.push({ cell: item.cell, pixels: count, changed, maxDelta, nativeBlack, candidateNonzero });
}
writeFileSync(resolve(here, "exterior-check.json"), JSON.stringify({
  domain: "at least 3 CSS px outside both fixed native and declared silhouettes", rows,
  qualification: "Scratch-subset pixel identity, not regenerated full C1/X1; B1 leaves unchanged",
}, null, 2) + "\n");
console.log(JSON.stringify(rows, null, 2));
