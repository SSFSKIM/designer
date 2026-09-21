/**
 * W31 G0 — is the interior mask adequate for a per-pixel chroma statistic on
 * the cells the shape rows refuse? (acceptance clause 1; claims §5.161 §3.)
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/mask-adequacy.ts
 *
 * EVERY untinted `photo` cell of both macOS 27 dark profiles fails the
 * conditioning predicate, at both scales, in both poses and on both tiers. The
 * refusal is an AREA-and-BODIES refusal: the luminance-delta rule loses the
 * pixels where the material's own level meets the backdrop's, so the reference
 * silhouette comes back a few per cent short of the declared region and
 * perforated with holes. The charter asks G0 to say, with evidence, whether a
 * mask the shape rows refuse can carry this statistic.
 *
 * The question is answerable directly rather than by argument, because the
 * declared region is available and is complete by construction: it is built
 * from `scenes.json` and the backing scale and contains no hole and no missing
 * pixel. So the statistic is computed twice per cell — once under the native
 * silhouette the rows use, once under the declared region — and the two are
 * compared. If the mask's missing pixels were a biased sample of the interior
 * the two readings would separate; if they are not, the refusal is about the
 * shape axis and does not reach this one.
 *
 * The bias has a direction worth stating in advance. The pixels the rule drops
 * are the ones where the two sides AGREE in luminance, and over a photograph
 * those are not obviously more or less chromatic than the rest — but the
 * declared region also contains pixels OUTSIDE the drawn body near the corners,
 * where the backdrop shows through at full chroma. So the declared-region
 * reading should sit slightly HIGHER on ratio (ii) than the silhouette's on
 * both sides, and what matters is whether it moves the two sides together.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { componentRegion } from "../../src/component-region";
import { decodePng, type CalibrationImage } from "../../src/image";
import { chromaStructure } from "../../src/metrics/chroma";
import { extractSilhouette, silhouetteArea, silhouetteHoleCount } from "../../src/silhouette";

const HERE = import.meta.dirname;
const PACKAGE = resolve(HERE, "..", "..");
const REFERENCE = resolve(PACKAGE, "..", "..", "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");
const BACKGROUNDS = resolve(FIXTURES, "backgrounds");
const SCRATCH = process.env["VITREA_WEB_CAPTURES"] ?? "/tmp/w31-g0-captures";

const scenes = JSON.parse(readFileSync(resolve(REFERENCE, "scenes.json"), "utf8")) as {
  canvas: { width: number; height: number };
  components: Record<string, unknown>;
};

const CELLS = [
  ["apple-macos-27.0-1x-dark-standard-glass0.5", 1, "photo__capsule-button__rest"],
  ["apple-macos-27.0-1x-dark-standard-glass0.5", 1, "photo__rrect-md__rest"],
  ["apple-macos-27.0-1x-dark-standard-glass0.5", 1, "photo__rrect-lg__rest"],
  ["apple-macos-27.0-1x-dark-standard-glass0.5", 1, "photo__rrect-md__inactive"],
  ["apple-macos-27.0-2x-dark-standard-glass0.5", 2, "photo__rrect-md__rest"],
  ["apple-macos-27.0-2x-dark-standard-glass0.5", 2, "photo__rrect-lg__rest"],
  // Two light cells the predicate ACCEPTS, as the control: if the two masks
  // agree here and disagree on the dark cells, the disagreement is the
  // refusal's; if they agree on both, the refusal does not reach this axis.
  ["apple-macos-27.0-1x-light-standard-glass0.5", 1, "photo__rrect-md__rest"],
  ["apple-macos-27.0-1x-light-standard-glass0.5", 1, "photo__rrect-lg__rest"],
] as const;

const load = (path: string): CalibrationImage => decodePng(readFileSync(path));

function backgroundFor(scene: string, scale: number): CalibrationImage {
  const backdrop = scene.split("__")[0] ?? "";
  for (const name of [`${backdrop}@${scale}x.png`, `${backdrop}.png`]) {
    if (readdirSync(BACKGROUNDS).includes(name)) return load(resolve(BACKGROUNDS, name));
  }
  throw new Error(`no background raster for '${backdrop}' at ${scale}x`);
}

const out: unknown[] = [];
console.log("== the same statistic under two masks: the native silhouette, and the declared region ==\n");
console.log(
  "  cell                                              tier     mask        area  holes   " +
    "(i) N   (i) W   w/n     (ii) N  (ii) W",
);
for (const [profileKey, scale, scene] of CELLS) {
  const native = load(resolve(FIXTURES, profileKey, `${scene}.png`));
  const background = backgroundFor(scene, scale);
  const component = scenes.components[scene.split("__")[1] ?? ""];
  const region = componentRegion(component as never, {
    canvas: scenes.canvas,
    scale,
    width: native.width,
    height: native.height,
  });
  const silhouette = extractSilhouette(native, {
    kind: "luminance-delta",
    background,
    threshold: 0.02,
    chromaThreshold: 0.03,
    region: region.silhouette,
  });

  for (const tier of ["webgpu", "css"] as const) {
    const web = load(resolve(SCRATCH, profileKey, scene, `${scene}__${tier}.png`));
    for (const [label, mask] of [
      ["silhouette", silhouette],
      ["region", region.silhouette],
    ] as const) {
      const report = chromaStructure(native, web, background, mask);
      const wn =
        report.web.chromaToStructure !== undefined && report.native.chromaToStructure
          ? report.web.chromaToStructure / report.native.chromaToStructure
          : Number.NaN;
      const f = (x: number | undefined): string =>
        x === undefined || !Number.isFinite(x) ? "     —" : x.toFixed(3).padStart(6);
      console.log(
        `  ${`${profileKey.replace("apple-macos-", "")} ${scene}`.padEnd(48)} ${tier.padEnd(7)} ` +
          `${label.padEnd(11)} ${String(silhouetteArea(mask)).padStart(6)} ` +
          `${String(silhouetteHoleCount(mask, region.silhouette)).padStart(5)}  ` +
          `${f(report.native.chromaToStructure)}  ${f(report.web.chromaToStructure)}  ${f(wn)}  ` +
          `${f(report.rawRatioNative)}  ${f(report.rawRatioWeb)}`,
      );
      out.push({ profileKey, scene, scale, tier, mask: label, area: silhouetteArea(mask),
        holes: silhouetteHoleCount(mask, region.silhouette),
        ratioI: { native: report.native.chromaToStructure, web: report.web.chromaToStructure, webOverNative: wn },
        ratioII: { native: report.rawRatioNative, web: report.rawRatioWeb } });
    }
  }
  console.log("");
}

writeFileSync(resolve(HERE, "mask-adequacy.json"), `${JSON.stringify(out, null, 1)}\n`);
console.log("wrote mask-adequacy.json");
