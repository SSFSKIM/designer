/**
 * W19 G0 (b) — the closed form carried onto the captured ladder, per pixel.
 *
 * (a) evaluates the composite error analytically over a swept uniform backdrop. That is the
 * mechanism, but it is not the measurement, and the charter's acceptance asks for the closed form to
 * reproduce the MEASURED error per cell. This does that, and it does it without a second model of the
 * body: the prediction's only input from the captures is the tier's own UNTINTED cell.
 *
 * ## Why the untinted capture is `E(M)`
 *
 * On the linear form the untinted surface draws the table `F(b) = D((E(M) − α₃·E(T))/(1 − α₃))` in
 * its sharp layer and the floor overlay `rgba(T, α₃)` on L3, and those two composite back to `E(M)`
 * exactly — that identity is what W17 G1 solved the table for. So the untinted CSS capture IS the
 * tier's own `E(M)` per pixel, encoded, with the tier's own body, its own kernel, its own mask and
 * its own two-layer mix already inside it. Predicting the tinted cell from it therefore tests exactly
 * one thing — what the author layer and the table do to a material both cells share — and nothing
 * about the body, which this wave does not touch.
 *
 * Three quantities do NOT come from the capture and are resolved from the profile through
 * `surface.ts` at the scene's own sampled tone: `α₃`, `T` and `T_folded` (the untinted and folded
 * overlay colours) and the author layer `(L, s)`.
 *
 * ## The three predictions
 *
 * Per pixel and per channel, with `E(M)` the untinted capture's own byte:
 *
 *   today    = D( (1 − s)·clamp((E(M) − α₃·E(T_folded))/(1 − α₃)) + s·E(L) )
 *   intended = D( (1 − s)·E(M) + s·E(L) )
 *   folded   = D( (1 − α″)·clamp((E(M) − α₃·E(T))/(1 − α₃)) + α″·C″ )
 *
 * `today` against the measured tinted CSS capture is the closed form's own accuracy; `folded` minus
 * the measured capture is the derived share G1's S5 will hold each cell to.
 *
 * ## What it does not model
 *
 * The rim, the drawn border, the highlight and the outer shadow are painted outside the table, and
 * L3's overlay covers them differently at `s` than at `α₃`; the mask's antialiased contour is
 * likewise outside the identity. Both are contour effects on a mask whose interior is the quantity,
 * and the residual column is where they land. Nothing is fitted to close them.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g0/predict.ts <scenesJson> <gpuRoot> <cssRoot> \
 *     <scale> <outJson>
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { PNG } from "pngjs";
import { glassTint } from "@vitreajs/vitrea";
import { cssTierFloorAlpha, linearTint, MATERIAL_OPTICS } from "@vitreajs/vitrea-web";

import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { componentRegion, decodePng, interiorLevel, type CalibrationImage } from "../../../src/index";
import { resolveSurface } from "./surface";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const FIXTURES = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple", "fixtures");

const [, , scenesJson, gpuRoot, cssRoot, scaleArg, outJson] = process.argv;
if (scenesJson === undefined || gpuRoot === undefined || cssRoot === undefined ||
    scaleArg === undefined || outJson === undefined) {
  throw new Error("usage: predict.ts <scenesJson> <gpuRoot> <cssRoot> <scale> <outJson>");
}
const scale = Number(scaleArg);

const encode = (l: number): number =>
  l <= 0.0031308 ? 12.92 * l : 1.055 * Math.pow(l, 1 / 2.4) - 0.055;
const decode = (e: number): number =>
  e <= 0.04045 ? e / 12.92 : Math.pow((e + 0.055) / 1.055, 2.4);
const clamp01 = (v: number): number => Math.min(1, Math.max(0, v));
const luma = (r: number, g: number, b: number): number => 0.2126 * r + 0.7152 * g + 0.0722 * b;

const geometry = readSceneGeometry(scenesJson);
const matrix = JSON.parse(readFileSync(scenesJson, "utf8")) as {
  readonly tints: Readonly<Record<string, { readonly srgb: readonly number[]; readonly alpha?: number }>>;
  readonly scenes: readonly { readonly id: string; readonly background: string; readonly tint?: string }[];
};
const manifest = JSON.parse(readFileSync(resolve(FIXTURES, "manifest.json"), "utf8")) as {
  readonly backgrounds: Readonly<Record<string, string>>;
};

/** `sampleBackdropTone`'s two means over one background fixture, read at full resolution. */
const toneCache = new Map<string, { rgb: [number, number, number]; luminance: number; linearLuminance: number }>();
function toneOf(background: string): { rgb: [number, number, number]; luminance: number; linearLuminance: number } {
  const file = manifest.backgrounds[`${background}@${String(scale)}x`];
  if (file === undefined) throw new Error(`predict: no background fixture for ${background}@${String(scale)}x`);
  const cached = toneCache.get(file);
  if (cached !== undefined) return cached;
  const png = PNG.sync.read(readFileSync(resolve(FIXTURES, file)));
  let r = 0, g = 0, b = 0, er = 0, eg = 0, eb = 0, weight = 0;
  for (let i = 0; i < png.data.length; i += 4) {
    const a = (png.data[i + 3] as number) / 255;
    if (a <= 0) continue;
    const pr = (png.data[i] as number) / 255;
    const pg = (png.data[i + 1] as number) / 255;
    const pb = (png.data[i + 2] as number) / 255;
    er += pr * a; eg += pg * a; eb += pb * a;
    r += decode(pr) * a; g += decode(pg) * a; b += decode(pb) * a;
    weight += a;
  }
  const tone = {
    rgb: [r / weight, g / weight, b / weight] as [number, number, number],
    luminance: luma(decode(er / weight), decode(eg / weight), decode(eb / weight)),
    linearLuminance: luma(r / weight, g / weight, b / weight),
  };
  toneCache.set(file, tone);
  return tone;
}

const bytesOf = (path: string): PNG => PNG.sync.read(readFileSync(path));
const load = (path: string): CalibrationImage => decodePng(readFileSync(path));
const meanOver = (image: CalibrationImage, mask: Uint8Array, width: number, height: number): number =>
  interiorLevel(image, { interior: { width, height, mask } }).mean;

const floorAlpha = cssTierFloorAlpha(MATERIAL_OPTICS.regular);
const rows: unknown[] = [];

for (const scene of matrix.scenes) {
  if (scene.tint === undefined) continue;
  const untintedId = `${scene.background}__capsule-button__rest`;
  const tintedCss = resolve(cssRoot, scene.id, `${scene.id}__css.png`);
  const tintedGpu = resolve(gpuRoot, scene.id, `${scene.id}__webgpu.png`);
  const untintedCss = resolve(cssRoot, untintedId, `${untintedId}__css.png`);
  const reportPath = resolve(cssRoot, scene.id, "report__css.json");
  if (![tintedCss, tintedGpu, untintedCss, reportPath].every((p) => existsSync(p))) {
    rows.push({ scene: scene.id, dpr: scale, skipped: "a capture is missing" });
    continue;
  }

  const report = JSON.parse(readFileSync(reportPath, "utf8")) as {
    page: { surfaces: { radius: number; bounds: { width: number; height: number } }[] };
  };
  const surface = report.page.surfaces[0] as { radius: number; bounds: { width: number; height: number } };
  const box = {
    widthCssPx: surface.bounds.width,
    heightCssPx: surface.bounds.height,
    radiusCssPx: surface.radius,
    thicknessCssPx: 8,
  };

  const spec = matrix.tints[scene.tint] as { srgb: readonly number[]; alpha?: number };
  const strength = spec.alpha ?? 1;
  const seedLinear = linearTint(glassTint(spec.srgb.map((v) => v / 255) as never, strength));
  const resolved = resolveSurface(box, toneOf(scene.background), seedLinear as never);
  const author = resolved.authorLayer;
  if (author === undefined) throw new Error(`predict: no author layer on ${scene.id}`);

  const untinted = bytesOf(untintedCss);
  const { width, height } = untinted;
  const component = declaredComponentOf(geometry, scene.id);
  const mask = componentRegion(component, { canvas: geometry.canvas, scale, width, height }).silhouette.mask;

  const alphaDoublePrime = 1 - (1 - strength) * (1 - floorAlpha);
  /*
   * How much of the table's own range the two forms use.
   *
   * The clamp is not a cosmetic detail: `cssTierTintTable` clamps its samples into [0, 1] because an
   * `feComponentTransfer type="table"` cannot carry a value outside it, and the transfer sits inside
   * the SHARP layer's filter — before L2's Gaussian and before the mask mixes the two bodies. A
   * clamped table is not affine, so a saturating channel's loss does not pass through the blur
   * unchanged and cannot be recovered from the composite. These two counters say how much of each
   * cell is in that regime under today's table and under the fold's.
   */
  let clampedToday = 0;
  let clampedFold = 0;
  let samples = 0;
  const predictedToday = new PNG({ width, height });
  const predictedIntended = new PNG({ width, height });
  const predictedFold = new PNG({ width, height });
  for (let i = 0; i < untinted.data.length; i += 4) {
    for (let c = 0; c < 3; c += 1) {
      const eM = (untinted.data[i + c] as number) / 255;
      const eL = (author.color[c] as number) / 255;
      const eT = (resolved.untinted.tint[c] as number) / 255;
      const eTf = (resolved.folded.tint[c] as number) / 255;
      const argToday = (eM - floorAlpha * eTf) / (1 - floorAlpha);
      const argFold = (eM - floorAlpha * eT) / (1 - floorAlpha);
      if ((mask[i / 4] ?? 0) === 1) {
        samples += 1;
        if (argToday > 1 || argToday < 0) clampedToday += 1;
        if (argFold > 1 || argFold < 0) clampedFold += 1;
      }
      const today = (1 - strength) * clamp01(argToday) + strength * eL;
      const intended = (1 - strength) * eM + strength * eL;
      const cDouble = ((1 - strength) * floorAlpha * eT + strength * eL) / alphaDoublePrime;
      const fold = (1 - alphaDoublePrime) * clamp01(argFold) + alphaDoublePrime * cDouble;
      predictedToday.data[i + c] = Math.round(clamp01(today) * 255);
      predictedIntended.data[i + c] = Math.round(clamp01(intended) * 255);
      predictedFold.data[i + c] = Math.round(clamp01(fold) * 255);
    }
    for (const png of [predictedToday, predictedIntended, predictedFold]) {
      png.data[i + 3] = untinted.data[i + 3] as number;
    }
  }

  const measuredCss = meanOver(load(tintedCss), mask, width, height);
  const measuredGpu = meanOver(load(tintedGpu), mask, width, height);
  const untintedMean = meanOver(load(untintedCss), mask, width, height);
  const today = meanOver(decodePng(PNG.sync.write(predictedToday)), mask, width, height);
  const intended = meanOver(decodePng(PNG.sync.write(predictedIntended)), mask, width, height);
  const fold = meanOver(decodePng(PNG.sync.write(predictedFold)), mask, width, height);

  rows.push({
    scene: scene.id,
    dpr: scale,
    tint: scene.tint,
    strength,
    alphaDoublePrime,
    paintedAlphaToday: strength,
    underFloorToday: strength < floorAlpha,
    overlayToday: `rgba(${author.color.map(String).join(", ")}, ${String(strength)})`,
    untintedCssMean: untintedMean,
    measuredCss,
    measuredGpu,
    measuredCssMinusGpu: measuredCss - measuredGpu,
    predictedToday: today,
    predictedIntended: intended,
    predictedFold: fold,
    predictionResidual: today - measuredCss,
    predictedErrorToday: today - intended,
    derivedShare: fold - today,
    predictedFoldMinusGpu: fold - measuredGpu + (measuredCss - today),
    clampedChannelShareToday: samples === 0 ? 0 : clampedToday / (samples * 3),
    clampedChannelShareFold: samples === 0 ? 0 : clampedFold / (samples * 3),
  });
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} tinted scenes -> ${outJson}\n`);
