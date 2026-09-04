/**
 * W17 G0 (f) — contract X4: the interior-mean reader's recovery of a known offset.
 *
 * The attribution in §1 of the findings is a table of differences between interior means, so the
 * reading is only worth what the reader is. This script validates the reader before any declined
 * render is read, and it does so through the production path rather than a re-implementation of
 * it: it calls `measureCell` — the same function `cli/compare.ts` calls, with the same declared
 * component region, the same native-silhouette mask and the same `interiorLevel` — twice on one
 * cell. Once on the capture as it was written, which must reproduce the number already recorded in
 * that run's matrix, and once on a copy of the same capture with a known offset lerped into it in
 * linear light, which must come back as that offset.
 *
 * **The offset, exactly.** Each capture pixel is decoded to linear light, raised by the nominal
 * 0.03, clamped to 1 and re-encoded to eight bits. Two things then separate the offset that was
 * asked for from the offset that is on disk: the clamp, where a pixel was already within 0.03 of
 * white, and the eight-bit quantisation. Both are properties of the doctored PNG and neither is
 * the reader's error, so the script computes the ACHIEVED offset independently — over the same
 * mask, from the bytes it actually wrote — and reports the reader's reading against both. The
 * nominal figure is what the contract names; the achieved figure is what the reader is entitled to
 * return; the gap between the two is the doctoring's, and it is printed rather than absorbed.
 *
 * Usage: `npx tsx x4-recovery.ts <captureRoot> <profileKey> <sceneId> [offset]`, run from
 * `packages/calibration`, with `<captureRoot>` a scratch capture root written by a compare run.
 * Nothing canonical is read for writing and nothing is written outside a scratch directory.
 */

import { createHash } from "node:crypto";
import { copyFileSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { PNG } from "pngjs";

import {
  DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
  DEFAULT_SILHOUETTE_THRESHOLD,
  measureCell,
} from "../../../cli/measure";
import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import {
  componentRegion,
  decodePng,
  extractSilhouette,
  interiorLevel,
  linearLuminance,
} from "../../../src/index";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

/** The sRGB transfer function, both directions — IEC 61966-2-1, as the harness states it. */
const decode = (e: number): number => (e <= 0.04045 ? e / 12.92 : ((e + 0.055) / 1.055) ** 2.4);
const encode = (l: number): number =>
  l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;


const [, , captureRoot, profileKey, sceneId, offsetArg] = process.argv;
if (captureRoot === undefined || profileKey === undefined || sceneId === undefined) {
  throw new Error("usage: x4-recovery.ts <captureRoot> <profileKey> <sceneId> [offset]");
}
const offset = offsetArg === undefined ? 0.03 : Number(offsetArg);

interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly {
    readonly profileKey: string;
    readonly display: { readonly actualBackingScale: number };
    readonly fixtures: readonly { readonly sceneId: string; readonly file: string }[];
  }[];
}
const manifest = JSON.parse(readFileSync(resolve(FIXTURES, "manifest.json"), "utf8")) as Manifest;
const geometry = readSceneGeometry(REFERENCE);

const profile = manifest.profiles.find((entry) => entry.profileKey === profileKey);
if (profile === undefined) throw new Error(`no manifest profile ${profileKey}`);
const fixture = profile.fixtures.find((entry) => entry.sceneId === sceneId);
if (fixture === undefined) throw new Error(`no fixture ${sceneId} under ${profileKey}`);
const scale = profile.display.actualBackingScale;

const scene = geometry.scenes.find((entry) => entry.id === sceneId);
if (scene === undefined) throw new Error(`scenes.json declares no scene ${sceneId}`);
const backgroundFile = manifest.backgrounds[`${scene.background}@${scale}x`];
if (backgroundFile === undefined) throw new Error(`no background for ${scene.background}@${scale}x`);

const captureDir = resolve(captureRoot, profileKey, sceneId);
const webPng = resolve(captureDir, `${sceneId}__webgpu.png`);
const webCell = resolve(captureDir, "cell__webgpu.json");

function read(webPath: string): number {
  const outcome = measureCell({
    nativePath: resolve(FIXTURES, fixture!.file),
    webPath,
    backgroundPath: resolve(FIXTURES, backgroundFile!),
    profileKey: profileKey!,
    sceneId: sceneId!,
    webCellPath: webCell,
    tier: "texture",
    fixtureSet: "calibration",
    blurAxis: "x",
    silhouetteThreshold: DEFAULT_SILHOUETTE_THRESHOLD,
    silhouetteChromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
    component: declaredComponentOf(geometry, sceneId!),
    canvas: geometry.canvas,
    scale,
  });
  const value = outcome.cell.material?.interiorMeanWeb?.value;
  if (value === undefined) throw new Error("the material axis is absent on this cell");
  return value;
}

// The doctored capture, written into a scratch directory beside a copy of the cell report so
// `measureCell` reads the same pair of files it would in a run.
const scratch = mkdtempSync(resolve(tmpdir(), "w17-g0-x4-"));
const doctored = resolve(scratch, `${sceneId}__webgpu.png`);
copyFileSync(webCell, resolve(scratch, "cell__webgpu.json"));

const original = PNG.sync.read(readFileSync(webPng));
const raised = new PNG({ width: original.width, height: original.height });
let clamped = 0;
for (let i = 0; i < original.data.length; i += 4) {
  for (let c = 0; c < 3; c += 1) {
    const linear = decode((original.data[i + c] as number) / 255);
    const lifted = linear + offset;
    if (lifted > 1) clamped += 1;
    raised.data[i + c] = Math.round(encode(Math.min(1, lifted)) * 255);
  }
  raised.data[i + 3] = original.data[i + 3] as number;
}
writeFileSync(doctored, PNG.sync.write(raised));

/*
 * The ACHIEVED offset over the reader's OWN mask, reconstructed here rather than inferred.
 *
 * The reader is a plain masked mean of linear luminance and the mask is the NATIVE silhouette,
 * which the doctoring does not touch — so the difference of the two readings is already the mean
 * of the per-pixel change over that mask, and there is no separable "reader error" to look for.
 * What there IS is the doctoring's own loss: the clamp at white and the eight-bit round trip. So
 * the same mask is rebuilt through the harness's own extractor and the achieved offset computed
 * over it directly, which is what the reader's recovery is entitled to equal. The residual against
 * the nominal 0.03 is then attributed rather than tolerated.
 */
const nativeImage = decodePng(readFileSync(resolve(FIXTURES, fixture.file)));
const backgroundImage = decodePng(readFileSync(resolve(FIXTURES, backgroundFile)));
const region = componentRegion(declaredComponentOf(geometry, sceneId), {
  canvas: geometry.canvas,
  scale,
  width: nativeImage.width,
  height: nativeImage.height,
});
const nativeSilhouette = extractSilhouette(nativeImage, {
  kind: "luminance-delta",
  background: backgroundImage,
  threshold: DEFAULT_SILHOUETTE_THRESHOLD,
  chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
  region: region.silhouette,
});
const mask = nativeSilhouette.mask;

/*
 * The as-captured reading through the whole production path, and then the raised reading through
 * the reader alone.
 *
 * `measureCell` computes every axis, and the SHAPE axis refuses a doctored capture: raising the
 * whole image in linear light moves the web pixels away from the background everywhere, so the
 * luminance-delta extractor returns the whole declared region as the web silhouette and
 * `cornerCurvature` throws on a contour with no curvature in it. That is the shape axis correctly
 * saying the doctored file is not a capture, and it has nothing to do with the quantity under
 * test. So the as-captured reading goes through `measureCell` — which is what proves the mask and
 * the reader together reproduce the number already in the run's matrix — and the raised reading
 * goes through `interiorLevel` over the identical mask, which is the single line `measureCell`
 * itself runs for this metric. The direct reading of the UNDOCTORED capture is reported beside
 * both, so the two paths are shown to agree before either is trusted.
 */
const before = read(webPng);
const beforeDirect = interiorLevel(decodePng(readFileSync(webPng)), { interior: nativeSilhouette }).mean;
const after = interiorLevel(decodePng(readFileSync(doctored)), { interior: nativeSilhouette }).mean;

const luminanceBefore = linearLuminance(decodePng(readFileSync(webPng)));
const luminanceAfter = linearLuminance(decodePng(readFileSync(doctored)));
let achieved = 0;
let maskCount = 0;
let clampedInMask = 0;
for (let p = 0; p < mask.length; p += 1) {
  if ((mask[p] ?? 0) === 0) continue;
  achieved += (luminanceAfter[p] ?? 0) - (luminanceBefore[p] ?? 0);
  if ((luminanceBefore[p] ?? 0) + offset > 1) clampedInMask += 1;
  maskCount += 1;
}
achieved /= maskCount;

process.stdout.write(
  JSON.stringify(
    {
      captureRoot,
      profileKey,
      sceneId,
      capture: {
        path: webPng,
        sha256: createHash("sha256").update(readFileSync(webPng)).digest("hex").slice(0, 16),
      },
      nominalOffset: offset,
      interiorMeanAsCaptured: before,
      interiorMeanAsCapturedDirect: beforeDirect,
      measureCellMinusDirect: before - beforeDirect,
      interiorMeanRaised: after,
      readerRecovery: after - before,
      readerErrorAgainstNominal: after - before - offset,
      achievedOffsetOverMask: achieved,
      readerMinusAchieved: after - before - achieved,
      maskPixels: maskCount,
      maskPixelsClampedAtWhite: clampedInMask,
      clampedChannelSamplesWholeImage: clamped,
      totalChannelSamplesWholeImage: (original.data.length / 4) * 3,
      doctored,
    },
    null,
    2,
  ) + "\n",
);
