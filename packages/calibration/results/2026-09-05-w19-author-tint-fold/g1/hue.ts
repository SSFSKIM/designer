/**
 * W19 G1 — the ladder's cross-tier OKLab ΔE, before and after the fold.
 *
 * G0's Deferred names the gap this closes: §5.80 §2 reports the transfer table's
 * saturation per channel and its share per cell, but no ΔE was taken on the
 * ladder, and the saturation is a HUE error on the seed's darkest channel. An
 * interior mean under-reports it by construction — a channel that loses 0.08
 * encoded while the other two hold moves the Rec. 709 mean by a fraction of that
 * — so the quantity that says what a reader would see is a colour distance, not a
 * level.
 *
 * The reference is the GPU tier's own capture of the same cell, for the same
 * reason the ladder's level reading is CSS − GPU: most of this bed has no native
 * fixture and the target of this wave is the renderer's composite (charter
 * Decision Log 1, q0 (a)). The mask is the declared component region, the same
 * mask `ladder.ts` reads the means under.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g1/hue.ts <scenesJson> <gpuRoot> <cssRoot> \
 *     <scale> <outJson>
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { componentRegion, decodePng, oklabDistance, srgbByteToOklab } from "../../../src/index";

const [, , scenesJson, gpuRoot, cssRoot, scaleArg, outJson] = process.argv;
if (scenesJson === undefined || gpuRoot === undefined || cssRoot === undefined ||
    scaleArg === undefined || outJson === undefined) {
  throw new Error("usage: hue.ts <scenesJson> <gpuRoot> <cssRoot> <scale> <outJson>");
}
const scale = Number(scaleArg);
const geometry = readSceneGeometry(scenesJson);
const load = (path: string) => decodePng(readFileSync(path));

const rows: unknown[] = [];
for (const scene of geometry.scenes) {
  const gpuPath = resolve(gpuRoot, scene.id, `${scene.id}__webgpu.png`);
  const cssPath = resolve(cssRoot, scene.id, `${scene.id}__css.png`);
  if (!existsSync(gpuPath) || !existsSync(cssPath)) {
    rows.push({ scene: scene.id, dpr: scale, skipped: "a capture is missing" });
    continue;
  }
  const gpu = load(gpuPath);
  const css = load(cssPath);
  const region = componentRegion(declaredComponentOf(geometry, scene.id), {
    canvas: geometry.canvas,
    scale,
    width: gpu.width,
    height: gpu.height,
  });
  const mask = region.silhouette.mask;
  let sum = 0;
  let max = 0;
  let pixels = 0;
  for (let i = 0; i < mask.length; i += 1) {
    if ((mask[i] ?? 0) === 0) continue;
    const at = i * 4;
    const a = srgbByteToOklab(
      gpu.data[at] as number,
      gpu.data[at + 1] as number,
      gpu.data[at + 2] as number,
    );
    const b = srgbByteToOklab(
      css.data[at] as number,
      css.data[at + 1] as number,
      css.data[at + 2] as number,
    );
    const d = oklabDistance(a, b);
    sum += d;
    if (d > max) max = d;
    pixels += 1;
  }
  rows.push({
    scene: scene.id,
    dpr: scale,
    oklabDeltaEMean: pixels === 0 ? 0 : sum / pixels,
    oklabDeltaEMax: max,
    pixels,
  });
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} scenes -> ${outJson}\n`);
