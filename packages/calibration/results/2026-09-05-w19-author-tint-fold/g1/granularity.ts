/**
 * W19 G1 — W10's tint-shade granularity, measured on the cell rather than swept.
 *
 * The two tiers read the tint's shade at different resolutions and always have
 * (claims §5.36, W10): `tintedMaterialColour` reads the material's luminance PER
 * PIXEL and shades the seed against it, while `authorTintLayer` reads one
 * luminance per source and paints one colour over the whole surface. On a flat
 * backdrop the two coincide; on the checkerboard, whose material swings between
 * the light and dark cells, they do not — and the difference is a term in
 * `CSS − GPU` that the fold neither creates nor removes.
 *
 * Decision Log 2 (7) is why it is measured here: S4 stays at 0.005 on every ladder
 * cell, and where a checkerboard cell misses that by no more than this term the
 * parent re-declares with the number rather than before it. So the number has to
 * exist, per cell, on the same pixels the level reading is taken over.
 *
 * **How.** The GPU tier's own UNTINTED capture is the material `M` per pixel, with
 * the renderer's body, kernel and mask already inside it — the same argument
 * `predict.ts` makes for the CSS side. Both strength laws are then evaluated on
 * those pixels: the renderer's, `tintedMaterialColour(M, seed, grip)`, whose shade
 * moves with `M`; and the tier's target, `D((1 − s)·E(M) + s·E(L))` with `L` the
 * one colour `authorTintLayer` resolved for this surface. The reported term is the
 * first's interior mean minus the second's — positive where the renderer's
 * per-pixel shade sits above the tier's one colour, which is the direction G0's
 * analytic sweep found (0.0000 to +0.0084, claims §5.80 §8).
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g1/granularity.ts <scenesJson> <gpuRoot> \
 *     <cssRoot> <scale> <outJson>
 *
 * `<cssRoot>` is read only for each cell's own `report__css.json`, which carries
 * the measured box the size law and the shade are resolved at.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { PNG } from "pngjs";
import { glassTint } from "@vitreajs/vitrea";
import { DEFAULT_MATERIAL_PROFILE, tintedMaterialColour } from "@vitrea/renderer-webgpu";
import { linearTint } from "@vitreajs/vitrea-web";

import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { componentRegion } from "../../../src/index";
import { resolveSurface } from "../g0/surface";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const FIXTURES = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple", "fixtures");

const [, , scenesJson, gpuRoot, cssRoot, scaleArg, outJson] = process.argv;
if (scenesJson === undefined || gpuRoot === undefined || cssRoot === undefined ||
    scaleArg === undefined || outJson === undefined) {
  throw new Error("usage: granularity.ts <scenesJson> <gpuRoot> <cssRoot> <scale> <outJson>");
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

/** The background's two means, as `sampleBackdropTone` takes them. */
const toneCache = new Map<string, { rgb: [number, number, number]; luminance: number; linearLuminance: number }>();
function toneOf(background: string): { rgb: [number, number, number]; luminance: number; linearLuminance: number } {
  const file = manifest.backgrounds[`${background}@${String(scale)}x`];
  if (file === undefined) throw new Error(`granularity: no background for ${background}@${String(scale)}x`);
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

const rows: unknown[] = [];
for (const scene of matrix.scenes) {
  if (scene.tint === undefined) continue;
  const untintedId = `${scene.background}__capsule-button__rest`;
  const untintedGpu = resolve(gpuRoot, untintedId, `${untintedId}__webgpu.png`);
  const reportPath = resolve(cssRoot, scene.id, "report__css.json");
  if (!existsSync(untintedGpu) || !existsSync(reportPath)) {
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
  if (author === undefined) throw new Error(`granularity: no author layer on ${scene.id}`);

  const png = PNG.sync.read(readFileSync(untintedGpu));
  const { width, height } = png;
  const mask = componentRegion(declaredComponentOf(geometry, scene.id), {
    canvas: geometry.canvas,
    scale,
    width,
    height,
  }).silhouette.mask;

  let rendererSum = 0;
  let tierSum = 0;
  let pixels = 0;
  for (let i = 0; i < mask.length; i += 1) {
    if ((mask[i] ?? 0) === 0) continue;
    const at = i * 4;
    const material: [number, number, number] = [
      decode((png.data[at] as number) / 255),
      decode((png.data[at + 1] as number) / 255),
      decode((png.data[at + 2] as number) / 255),
    ];
    const renderer = tintedMaterialColour(
      material,
      { color: seedLinear.color as never, strength },
      resolved.grip,
      DEFAULT_MATERIAL_PROFILE,
    );
    rendererSum += luma(renderer[0] as number, renderer[1] as number, renderer[2] as number);
    const tier = [0, 1, 2].map((c) =>
      decode(
        clamp01(
          (1 - strength) * encode(material[c as 0]) + strength * ((author.color[c] as number) / 255),
        ),
      ),
    );
    tierSum += luma(tier[0] as number, tier[1] as number, tier[2] as number);
    pixels += 1;
  }

  rows.push({
    scene: scene.id,
    dpr: scale,
    tint: scene.tint,
    strength,
    rendererPerPixelShade: pixels === 0 ? 0 : rendererSum / pixels,
    tierPerSourceShade: pixels === 0 ? 0 : tierSum / pixels,
    granularityTerm: pixels === 0 ? 0 : (rendererSum - tierSum) / pixels,
    pixels,
  });
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} tinted scenes -> ${outJson}\n`);
