/**
 * W31 G0 — did Apple move the chroma between macOS 26.5 and 27, or did vitrea
 * never have it? (acceptance clause 1; claims §5.161 §3.)
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/native-chroma-delta.ts
 *
 * The whole wave is chartered on a residual measured against macOS 27. If the
 * reference's own body carried the same chroma on macOS 26.5, then the gap is
 * vitrea's and always was, and the 1,818 frozen macOS 26.5 rows have been
 * carrying it invisibly. If it moved, the wave is closing a NEW gap and the
 * frozen bed is not implicated. That is a question about Apple's pixels alone,
 * so it is answered from the native fixture pairs with no web side in the
 * comparison at all — and therefore with no capture: X5 holds, every fixture is
 * on disk from W29.
 *
 * The statistic is this wave's own, plus the mean-OKLab one it replaces, on the
 * same mask, so the ledger can say why the per-pixel instrument was needed
 * rather than assert it.
 *
 * ONE MASK PER PAIR, AND IT IS THE macOS 27 SIDE'S. `measure.ts`'s rule is that
 * the mask is the reference's and never the moving side's; here BOTH sides are
 * references, so the rule needs a tie-break. The macOS 27 silhouette is the one
 * chosen because macOS 27 is what the wave fits against, and a statistic read
 * under two different masks would mix a shape difference into a chroma one. The
 * two silhouettes' areas are printed so the choice is visible rather than
 * silent.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { decodePng, type CalibrationImage } from "../../src/image";
import { chromaStructure } from "../../src/metrics/chroma";
import { tintResponse } from "../../src/metrics/material";
import { extractSilhouette, silhouetteArea } from "../../src/silhouette";

const HERE = import.meta.dirname;
const PACKAGE = resolve(HERE, "..", "..");
const FIXTURES = resolve(PACKAGE, "..", "..", "apps", "reference-apple", "fixtures");
const BACKGROUNDS = resolve(FIXTURES, "backgrounds");

const PAIRS = [
  ["apple-macos-26.5-1x-light-standard", "apple-macos-27.0-1x-light-standard-glass0.5", 1],
  ["apple-macos-26.5-2x-light-standard", "apple-macos-27.0-2x-light-standard-glass0.5", 2],
  ["apple-macos-26.5-1x-dark-standard", "apple-macos-27.0-1x-dark-standard-glass0.5", 1],
  ["apple-macos-26.5-2x-dark-standard", "apple-macos-27.0-2x-dark-standard-glass0.5", 2],
] as const;

const CHROMA = /^(photo|mid-chroma-solid)__/;
const SILHOUETTE_THRESHOLD = 0.02;
const SILHOUETTE_CHROMA_THRESHOLD = 0.03;

const load = (path: string): CalibrationImage => decodePng(readFileSync(path));

function backgroundFor(scene: string, scale: number): CalibrationImage {
  const backdrop = scene.split("__")[0] ?? "";
  for (const name of [`${backdrop}@${scale}x.png`, `${backdrop}.png`]) {
    if (readdirSync(BACKGROUNDS).includes(name)) return load(resolve(BACKGROUNDS, name));
  }
  throw new Error(`no background raster for '${backdrop}' at ${scale}x`);
}

const out: unknown[] = [];
console.log("== the reference's own chroma, macOS 26.5 against macOS 27 ==");
console.log("   the mask is the macOS 27 side's; both sides read under it.\n");

for (const [old, current, scale] of PAIRS) {
  const oldScenes = new Set(readdirSync(resolve(FIXTURES, old)));
  const scenes = readdirSync(resolve(FIXTURES, current))
    .filter((file) => file.endsWith(".png") && CHROMA.test(file) && oldScenes.has(file))
    .sort();
  console.log(`-- ${old}  →  ${current}   (${scenes.length} shared chroma scenes)`);
  console.log(
    "   scene                                     area 26.5 / 27   " +
      "(i) 26.5   (i) 27    Δ(i)     (ii) 26.5  (ii) 27   Δ(ii)    chroma 26.5 / 27   " +
      "mean-OKLab chromaDelta 26.5 / 27",
  );
  for (const file of scenes) {
    const scene = file.replace(/\.png$/, "");
    const before = load(resolve(FIXTURES, old, file));
    const after = load(resolve(FIXTURES, current, file));
    if (before.width !== after.width || before.height !== after.height) {
      console.log(`   ${scene.padEnd(42)} SKIPPED: ${before.width}x${before.height} against ${after.width}x${after.height}`);
      continue;
    }
    const background = backgroundFor(scene, scale);
    const extractor = {
      kind: "luminance-delta",
      background,
      threshold: SILHOUETTE_THRESHOLD,
      chromaThreshold: SILHOUETTE_CHROMA_THRESHOLD,
    } as const;
    const maskBefore = extractSilhouette(before, extractor);
    const mask = extractSilhouette(after, extractor);
    if (silhouetteArea(mask) === 0) {
      console.log(`   ${scene.padEnd(42)} SKIPPED: the macOS 27 silhouette is empty at ${SILHOUETTE_THRESHOLD}`);
      continue;
    }

    // `chromaStructure` takes (native, web, backdrop): here "native" is the
    // macOS 26.5 fixture and "web" is the macOS 27 one, so the two sides of its
    // report are the two REFERENCES and nothing of vitrea enters.
    const chroma = chromaStructure(before, after, background, mask);
    const tintBefore = tintResponse(before, background, { interior: mask });
    const tintAfter = tintResponse(after, background, { interior: mask });

    const f = (x: number | undefined, p = 3): string =>
      x === undefined || !Number.isFinite(x) ? "—".padStart(8) : x.toFixed(p).padStart(8);
    console.log(
      `   ${scene.padEnd(42)} ${String(silhouetteArea(maskBefore)).padStart(6)} /${String(silhouetteArea(mask)).padStart(6)}  ` +
        `${f(chroma.native.chromaToStructure)} ${f(chroma.web.chromaToStructure)} ` +
        `${f(
          chroma.web.chromaToStructure !== undefined && chroma.native.chromaToStructure
            ? chroma.web.chromaToStructure - chroma.native.chromaToStructure
            : undefined,
        )}  ${f(chroma.rawRatioNative)} ${f(chroma.rawRatioWeb)} ` +
        `${f(
          chroma.rawRatioWeb !== undefined && chroma.rawRatioNative !== undefined
            ? chroma.rawRatioWeb - chroma.rawRatioNative
            : undefined,
        )}  ${f(chroma.native.meanChroma, 4)} /${f(chroma.web.meanChroma, 4)}  ` +
        `${f(tintBefore.chromaDelta, 5)} /${f(tintAfter.chromaDelta, 5)}`,
    );

    out.push({
      pair: [old, current],
      scene,
      scale,
      areaBefore: silhouetteArea(maskBefore),
      areaAfter: silhouetteArea(mask),
      chromaToStructure: { "26.5": chroma.native.chromaToStructure, "27": chroma.web.chromaToStructure, backdrop: chroma.backdrop.chromaToStructure },
      rawRatio: { "26.5": chroma.rawRatioNative, "27": chroma.rawRatioWeb },
      meanPerPixelChroma: { "26.5": chroma.native.meanChroma, "27": chroma.web.meanChroma, backdrop: chroma.backdrop.meanChroma },
      interiorStdDev: { "26.5": chroma.native.luminanceStdDev, "27": chroma.web.luminanceStdDev, backdrop: chroma.backdrop.luminanceStdDev },
      meanOklabChromaDelta: { "26.5": tintBefore.chromaDelta, "27": tintAfter.chromaDelta },
      meanOklabInteriorChroma: { "26.5": tintBefore.interiorChroma, "27": tintAfter.interiorChroma, backdrop: tintAfter.backdropChroma },
    });
  }
  console.log("");
}

writeFileSync(resolve(HERE, "native-chroma-delta.json"), `${JSON.stringify(out, null, 1)}\n`);
console.log("wrote native-chroma-delta.json");
