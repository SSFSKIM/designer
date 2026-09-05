/**
 * W19 G0 (c) — Apple's own strength curve, and whether an encoded-space mix is it.
 *
 * The renderer's law is `tintedMaterialColour` — `decode(mix(encode(material), encode(layer), s))`
 * per pixel, the author layer opaque at the author's opacity in encoded space (claims §5.36
 * finding 3). Nobody has ever tested that shape against Apple, because the bed carries strengths 1.0
 * and 0.5 only. This does, and it does it without assuming anything about Apple's own shade: the two
 * ENDPOINTS are Apple's own captures — the untinted capsule from the canonical bed and the
 * full-strength tinted capsule from this wave's probe — so the hypothesis under test is purely the
 * INTERPOLATION, per pixel and per channel, in encoded space.
 *
 *     predicted(s) = D( (1 − s)·E(native untinted) + s·E(native at s = 1) )     per pixel, per channel
 *
 * A linear-light mix is computed beside it as the alternative that would be refuted, because "the mix
 * is in encoded space" is only a finding if the other space is measured and misses.
 *
 * The interior mean is read under the DECLARED component region on every row rather than under each
 * cell's own extracted silhouette: the four captures being differenced are the same geometry over the
 * same background, and one mask across all of them is what makes the residual a property of the
 * strength rather than of four extractions.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g0/native-ladder.ts <probeScenesJson> \
 *     <probeFixturesDir> <outJson>
 * Reads committed fixtures and the probe bed; writes only the file it is given.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { PNG } from "pngjs";

import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { componentRegion, decodePng, interiorLevel } from "../../../src/index";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const CANONICAL_FIXTURES = resolve(REFERENCE, "fixtures");
const PROFILE = "apple-macos-26.5-1x-light-standard";

const [, , probeScenes, probeFixtures, outJson] = process.argv;
if (probeScenes === undefined || probeFixtures === undefined || outJson === undefined) {
  throw new Error("usage: native-ladder.ts <probeScenesJson> <probeFixturesDir> <outJson>");
}

const encode = (l: number): number =>
  l <= 0.0031308 ? 12.92 * l : 1.055 * Math.pow(l, 1 / 2.4) - 0.055;
const decode = (e: number): number =>
  e <= 0.04045 ? e / 12.92 : Math.pow((e + 0.055) / 1.055, 2.4);
const clamp01 = (v: number): number => Math.min(1, Math.max(0, v));

const geometry = readSceneGeometry(probeScenes);
const matrix = JSON.parse(readFileSync(probeScenes, "utf8")) as {
  readonly tints: Readonly<Record<string, { readonly alpha?: number }>>;
  readonly scenes: readonly { readonly id: string; readonly background: string; readonly tint: string }[];
};

const nativeOf = (dir: string, sceneId: string): string =>
  resolve(dir, PROFILE, `${sceneId}.png`);

const rows: unknown[] = [];
for (const background of ["photo", "checkerboard"]) {
  const untintedId = `${background}__capsule-button__rest`;
  const fullId = `${background}__capsule-button__rest-tint-orange`;
  const untintedPath = nativeOf(CANONICAL_FIXTURES, untintedId);
  const fullPath = nativeOf(probeFixtures, fullId);
  if (!existsSync(untintedPath) || !existsSync(fullPath)) {
    rows.push({ background, skipped: "an endpoint fixture is missing" });
    continue;
  }
  const untinted = PNG.sync.read(readFileSync(untintedPath));
  const full = PNG.sync.read(readFileSync(fullPath));
  const { width, height } = untinted;

  // The declared region of the capsule, from the probe bed's own geometry: one mask for every row.
  const component = declaredComponentOf(geometry, fullId);
  const mask = componentRegion(component, { canvas: geometry.canvas, scale: 1, width, height })
    .silhouette.mask;
  const meanOf = (png: PNG): number =>
    interiorLevel(decodePng(PNG.sync.write(png)), { interior: { width, height, mask } }).mean;

  const endpoints = { untinted: meanOf(untinted), full: meanOf(full) };
  for (const scene of matrix.scenes) {
    if (scene.background !== background) continue;
    const strength = matrix.tints[scene.tint]?.alpha ?? 1;
    const path = nativeOf(probeFixtures, scene.id);
    if (!existsSync(path)) {
      rows.push({ scene: scene.id, skipped: "no native fixture" });
      continue;
    }
    const measured = PNG.sync.read(readFileSync(path));
    const encodedMix = new PNG({ width, height });
    const linearMix = new PNG({ width, height });
    for (let i = 0; i < untinted.data.length; i += 4) {
      for (let c = 0; c < 3; c += 1) {
        const a = (untinted.data[i + c] as number) / 255;
        const b = (full.data[i + c] as number) / 255;
        encodedMix.data[i + c] = Math.round(clamp01((1 - strength) * a + strength * b) * 255);
        linearMix.data[i + c] = Math.round(
          clamp01(encode((1 - strength) * decode(a) + strength * decode(b))) * 255,
        );
      }
      encodedMix.data[i + 3] = untinted.data[i + 3] as number;
      linearMix.data[i + 3] = untinted.data[i + 3] as number;
    }
    const measuredMean = meanOf(measured);
    rows.push({
      scene: scene.id,
      background,
      strength,
      nativeUntinted: endpoints.untinted,
      nativeFull: endpoints.full,
      nativeMeasured: measuredMean,
      encodedMix: meanOf(encodedMix),
      linearMix: meanOf(linearMix),
      encodedMixResidual: meanOf(encodedMix) - measuredMean,
      linearMixResidual: meanOf(linearMix) - measuredMean,
    });
  }
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} rows -> ${outJson}\n`);
