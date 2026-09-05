/**
 * W19 G1 — what moved between two CSS-tier capture roots, per cell (S3 by capture).
 *
 * Decision Log 2 (4) re-declared S3 as a statement about pixels rather than about
 * declarations: every UNTINTED capture byte-identical to the pre-fold run, and
 * every FULL-STRENGTH tinted capture byte-identical or, failing that, within
 * 0.0005 in the interior mean with the differing pixels confined to the contour
 * ring. The reason it may fail to be byte-identical is named in claims §5.80 §7:
 * at `s = 1` L3's declaration is unchanged, but the transfer's floor colour moves
 * from the folded colour to the untinted one, so the table under an opaque layer
 * changes — and everywhere the layer is genuinely opaque that difference cannot
 * reach the screen, while at the mask's antialiased contour it can.
 *
 * So the reading is: the byte state, the count and the worst code difference, and
 * WHERE the differing pixels are. "Where" is answered against the declared
 * component region eroded by `ringDevicePx` — a pixel is `interior` if the whole
 * disc of that radius around it is inside the region, `ring` if it is in the
 * region but not interior, and `outside` otherwise. A cell whose whole difference
 * is `ring` and `outside` is the contour class the clause admits; one with
 * `interior` pixels is not, whatever its mean says.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g1/moved.ts <scenesJson> <beforeRoot> \
 *     <afterRoot> <scale> <tier> <outJson>
 */

import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { componentRegion, decodePng, interiorLevel } from "../../../src/index";

const [, , scenesJson, beforeRoot, afterRoot, scaleArg, tier, outJson] = process.argv;
if (scenesJson === undefined || beforeRoot === undefined || afterRoot === undefined ||
    scaleArg === undefined || tier === undefined || outJson === undefined) {
  throw new Error("usage: moved.ts <scenesJson> <beforeRoot> <afterRoot> <scale> <tier> <outJson>");
}
const scale = Number(scaleArg);
const RING_DEVICE_PX = 2;
const geometry = readSceneGeometry(scenesJson);
const load = (path: string) => decodePng(readFileSync(path));
const sha = (path: string): string =>
  createHash("sha256").update(readFileSync(path)).digest("hex").slice(0, 16);

/** The region eroded by `RING_DEVICE_PX`: the pixels a contour effect cannot reach. */
function erode(mask: Uint8Array, width: number, height: number): Uint8Array {
  const out = new Uint8Array(mask.length);
  const r = RING_DEVICE_PX;
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const index = y * width + x;
      if ((mask[index] ?? 0) === 0) continue;
      let keep = 1;
      for (let dy = -r; dy <= r && keep === 1; dy += 1) {
        for (let dx = -r; dx <= r; dx += 1) {
          if (dx * dx + dy * dy > r * r) continue;
          const nx = x + dx;
          const ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= width || ny >= height || (mask[ny * width + nx] ?? 0) === 0) {
            keep = 0;
            break;
          }
        }
      }
      out[index] = keep;
    }
  }
  return out;
}

const rows: unknown[] = [];
for (const scene of geometry.scenes) {
  const beforePath = resolve(beforeRoot, scene.id, `${scene.id}__${tier}.png`);
  const afterPath = resolve(afterRoot, scene.id, `${scene.id}__${tier}.png`);
  if (!existsSync(beforePath) || !existsSync(afterPath)) {
    rows.push({ scene: scene.id, dpr: scale, skipped: "a capture is missing" });
    continue;
  }
  const before = load(beforePath);
  const after = load(afterPath);
  const { width, height } = before;
  const region = componentRegion(declaredComponentOf(geometry, scene.id), {
    canvas: geometry.canvas,
    scale,
    width,
    height,
  });
  const mask = region.silhouette.mask;
  const inner = erode(mask, width, height);

  let differing = 0;
  let inMask = 0;
  let inInterior = 0;
  let worstCode = 0;
  for (let i = 0; i < mask.length; i += 1) {
    const at = i * 4;
    let delta = 0;
    for (let c = 0; c < 3; c += 1) {
      delta = Math.max(delta, Math.abs((before.data[at + c] as number) - (after.data[at + c] as number)));
    }
    if (delta === 0) continue;
    differing += 1;
    worstCode = Math.max(worstCode, delta);
    if ((mask[i] ?? 0) === 1) {
      inMask += 1;
      if ((inner[i] ?? 0) === 1) inInterior += 1;
    }
  }
  const meanBefore = interiorLevel(before, { interior: { width, height, mask } }).mean;
  const meanAfter = interiorLevel(after, { interior: { width, height, mask } }).mean;
  rows.push({
    scene: scene.id,
    dpr: scale,
    tier,
    identical: differing === 0,
    sha256Before: sha(beforePath),
    sha256After: sha(afterPath),
    differingPixels: differing,
    differingInRegion: inMask,
    differingInErodedInterior: inInterior,
    worstChannelCode: worstCode,
    interiorMeanBefore: meanBefore,
    interiorMeanAfter: meanAfter,
    interiorMeanMove: meanAfter - meanBefore,
    regionPixels: region.silhouette.mask.reduce((n, v) => n + v, 0),
    ringDevicePx: RING_DEVICE_PX,
  });
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} scenes -> ${outJson}\n`);
