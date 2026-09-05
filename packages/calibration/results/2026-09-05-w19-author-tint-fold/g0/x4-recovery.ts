/**
 * W19 G0 — contract X4, on this wave's own reader.
 *
 * W18 G0's script, unchanged in construction and re-pointed at this wave's ladder. The masks are the
 * two `ladder.ts` uses: the DECLARED component region, which is the only mask the ladder's new rungs
 * admit, and the NATIVE silhouette, which is the mask the Grounding Baseline's numbers are under and
 * which the ladder's controls still carry a fixture for. A recovery contract that validated a reader
 * nothing in the findings uses would be a ceremony, so this validates the reader `ladder.ts` actually
 * calls, under every mask it actually uses, before a single rung is read.
 *
 * The construction is W17's unchanged: decode each capture pixel to linear light, raise it by a
 * nominal +0.03, clamp at white, re-encode to eight bits, and require the masked mean to come back
 * that much higher. Two things separate the offset asked for from the offset on disk — the clamp
 * where a pixel was already within 0.03 of white, and the eight-bit quantisation — so the ACHIEVED
 * offset is computed independently over the same mask from the bytes actually written, and the
 * reading is reported against both. The nominal figure is what the contract names; the achieved
 * figure is what the reader is entitled to return.
 *
 * `measureCell` is run beside it on the cells that have a native fixture, which proves this script's
 * own mask and the production path's agree before either is trusted.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g0/x4-recovery.ts <scenesJson> <captureRoot> \
 *     <tier> <sceneId> <scale> [offset]
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
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
  placeComponent,
  type CalibrationImage,
} from "../../../src/index";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const decode = (e: number): number => (e <= 0.04045 ? e / 12.92 : ((e + 0.055) / 1.055) ** 2.4);
const encode = (l: number): number =>
  l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;

const [, , scenesJson, captureRoot, tier, sceneId, scaleArg, offsetArg] = process.argv;
if (scenesJson === undefined || captureRoot === undefined || tier === undefined ||
    sceneId === undefined || scaleArg === undefined) {
  throw new Error("usage: x4-recovery.ts <scenesJson> <captureRoot> <tier> <sceneId> <scale> [offset]");
}
const scale = Number(scaleArg);
const offset = offsetArg === undefined ? 0.03 : Number(offsetArg);

const geometry = readSceneGeometry(scenesJson);
const component = declaredComponentOf(geometry, sceneId);
const capturePath = resolve(captureRoot, sceneId, `${sceneId}__${tier}.png`);
const original = decodePng(readFileSync(capturePath));
const { width, height } = original;

/** The doctored capture, in memory: the same construction W17 G0 wrote to disk. */
const doctoredPng = new PNG({ width, height });
const raw = PNG.sync.read(readFileSync(capturePath));
let clampedChannels = 0;
for (let i = 0; i < raw.data.length; i += 4) {
  for (let c = 0; c < 3; c += 1) {
    const lifted = decode((raw.data[i + c] as number) / 255) + offset;
    if (lifted > 1) clampedChannels += 1;
    doctoredPng.data[i + c] = Math.round(encode(Math.min(1, lifted)) * 255);
  }
  doctoredPng.data[i + 3] = raw.data[i + 3] as number;
}
const doctored: CalibrationImage = decodePng(PNG.sync.write(doctoredPng));

const before = linearLuminance(original);
const after = linearLuminance(doctored);

const region = componentRegion(component, { canvas: geometry.canvas, scale, width, height });

interface Reading {
  readonly mask: string;
  readonly pixels: number;
  readonly asCaptured: number;
  readonly raised: number;
  readonly readerRecovery: number;
  readonly readerErrorAgainstNominal: number;
  readonly achievedOffsetOverMask: number;
  readonly readerMinusAchieved: number;
  readonly maskPixelsClampedAtWhite: number;
}

function recover(label: string, mask: Uint8Array): Reading {
  const a = interiorLevel(original, { interior: { width, height, mask } }).mean;
  const b = interiorLevel(doctored, { interior: { width, height, mask } }).mean;
  let achieved = 0;
  let pixels = 0;
  let clamped = 0;
  for (let i = 0; i < mask.length; i += 1) {
    if ((mask[i] ?? 0) === 0) continue;
    achieved += (after[i] ?? 0) - (before[i] ?? 0);
    if ((before[i] ?? 0) + offset > 1) clamped += 1;
    pixels += 1;
  }
  achieved /= pixels;
  return {
    mask: label,
    pixels,
    asCaptured: a,
    raised: b,
    readerRecovery: b - a,
    readerErrorAgainstNominal: b - a - offset,
    achievedOffsetOverMask: achieved,
    readerMinusAchieved: b - a - achieved,
    maskPixelsClampedAtWhite: clamped,
  };
}

const readings: Reading[] = [recover("declared component region", region.silhouette.mask)];

const placed = placeComponent(component, geometry.canvas);
placed.forEach((shape, index) => {
  const mask = new Uint8Array(width * height);
  const centreX = (shape.left + shape.width / 2) * scale;
  const centreY = (shape.top + shape.height / 2) * scale;
  const halfWidth = (shape.width / 2) * scale;
  const halfHeight = (shape.height / 2) * scale;
  const radius = shape.radius * scale;
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const qx = Math.abs(x + 0.5 - centreX) - (halfWidth - radius);
      const qy = Math.abs(y + 0.5 - centreY) - (halfHeight - radius);
      const distance =
        Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius;
      if (distance <= 0) mask[y * width + x] = 1;
    }
  }
  readings.push(recover(`declared surface ${String(index)}`, mask));
});

/*
 * The native silhouette and the production path, where the canonical bed has a fixture for this
 * scene. `measureCell` is called on the capture as written and must reproduce the direct reading
 * exactly; the raised reading goes through `interiorLevel` over the identical mask, because the
 * shape axis correctly refuses a doctored capture (W17 G0 recorded that finding and it is not the
 * quantity under test).
 */
interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly {
    readonly profileKey: string;
    readonly fixtures: readonly { readonly sceneId: string; readonly file: string }[];
  }[];
}
const manifest = JSON.parse(readFileSync(resolve(FIXTURES, "manifest.json"), "utf8")) as Manifest;
const profileKey = `apple-macos-26.5-${String(scale)}x-light-standard`;
const fixture = manifest.profiles
  .find((p) => p.profileKey === profileKey)
  ?.fixtures.find((f) => f.sceneId === sceneId);
const backgroundFile = manifest.backgrounds[`${sceneId.split("__")[0] as string}@${String(scale)}x`];

let productionPath: unknown = "no native fixture for this scene id — the declared masks are the study's";
if (fixture !== undefined && backgroundFile !== undefined) {
  const nativeSilhouette = extractSilhouette(decodePng(readFileSync(resolve(FIXTURES, fixture.file))), {
    kind: "luminance-delta",
    background: decodePng(readFileSync(resolve(FIXTURES, backgroundFile))),
    threshold: DEFAULT_SILHOUETTE_THRESHOLD,
    chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
    region: region.silhouette,
  });
  readings.push(recover("native silhouette", nativeSilhouette.mask));

  const outcome = measureCell({
    nativePath: resolve(FIXTURES, fixture.file),
    webPath: capturePath,
    backgroundPath: resolve(FIXTURES, backgroundFile),
    profileKey,
    sceneId,
    webCellPath: resolve(captureRoot, sceneId, `cell__${tier}.json`),
    tier: tier === "css" ? "dom" : "texture",
    fixtureSet: "recorded",
    blurAxis: "x",
    silhouetteThreshold: DEFAULT_SILHOUETTE_THRESHOLD,
    silhouetteChromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
    component: declaredComponentOf(readSceneGeometry(REFERENCE), sceneId),
    canvas: geometry.canvas,
    scale,
  });
  const value = outcome.cell.material?.interiorMeanWeb?.value;
  const direct = readings[readings.length - 1] as Reading;
  productionPath = {
    measureCellInteriorMeanWeb: value,
    thisScriptNativeMaskAsCaptured: direct.asCaptured,
    difference: value === undefined ? null : value - direct.asCaptured,
  };
}

process.stdout.write(
  JSON.stringify(
    {
      scenesJson,
      captureRoot,
      tier,
      sceneId,
      dpr: scale,
      nominalOffset: offset,
      capture: {
        path: capturePath,
        sha256: createHash("sha256").update(readFileSync(capturePath)).digest("hex").slice(0, 16),
      },
      clampedChannelSamplesWholeImage: clampedChannels,
      readings,
      productionPath,
    },
    null,
    2,
  ) + "\n",
);
