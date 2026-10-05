/**
 * W46 G1 step 0: the masks the measurement itself uses for one cell, written for attribute.py.
 * The native silhouette (`extractSilhouette` with the luminance-delta extractor `measureCell` builds,
 * at compare's default thresholds, bounded to the declared component region) is the mask every
 * `interiorMean*` row of the cell is read over (`cli/measure.ts`: "One mask for both sides, and it
 * is the NATIVE silhouette"). The declared component region is written beside it.
 *
 *   cd packages/calibration
 *   pnpm exec tsx results/2026-10-05-w46-g1-refit/diagnosis/mask.ts <profile> <scene> <scale> <out.json>
 */
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { componentRegion, decodePng, extractSilhouette } from "../../../src/index";
import { DEFAULT_SILHOUETTE_CHROMA_THRESHOLD, DEFAULT_SILHOUETTE_THRESHOLD } from "../../../cli/measure";
import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { readFileSync } from "node:fs";

const [profile, sceneId, scaleText, out] = process.argv.slice(2);
const scale = Number(scaleText);
const root = resolve(import.meta.dirname, "../../../../..");
const geometry = readSceneGeometry(resolve(root, "apps/reference-apple/scenes.json"));
const scene = geometry.scenes.find((s) => s.id === sceneId)!;
const load = (path: string) => decodePng(readFileSync(path));
const native = load(resolve(root, `apps/reference-apple/fixtures/${profile}/${sceneId}.png`));
const background = load(resolve(root, `apps/reference-apple/fixtures/backgrounds/${scene.background}@${scale}x.png`));
const region = componentRegion(declaredComponentOf(geometry, sceneId!), {
  canvas: geometry.canvas, scale, width: native.width, height: native.height,
});
const sil = extractSilhouette(native, {
  kind: "luminance-delta", background, threshold: DEFAULT_SILHOUETTE_THRESHOLD,
  chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD, region: region.silhouette,
});
writeFileSync(out!, JSON.stringify({
  width: native.width, height: native.height,
  threshold: DEFAULT_SILHOUETTE_THRESHOLD, chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
  nativeSilhouette: Array.from(sil.mask), region: Array.from(region.silhouette.mask),
}));
