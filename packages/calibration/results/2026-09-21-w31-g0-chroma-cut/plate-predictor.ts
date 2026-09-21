/**
 * W31 G0 review closure (2026-09-21) — the plate predictor, reproduced and
 * recorded for G3 (claims §5.161 §11, the carried-forward readings).
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/plate-predictor.ts
 *
 * §5 states that the chroma is lost in the plate's alpha and reads it off two
 * numbers: `1 − sizedAlpha` at 0.0950 dark and 0.5130 light against a measured
 * ratio (ii) of 0.106–0.119 and 0.25–0.32. That is a comparison of two ranges,
 * and the light one is 2.4× out — which the ledger explains with "the light
 * body loses chroma beyond the plate as well". The review found the sharper
 * statement, and it is the one G3 should fit against:
 *
 *     ratio (ii)_web  ≈  (1 − sizedAlpha) · (Y_web / Y_backdrop)^(−2/3)
 *
 * The exponent is not fitted. OKLab's `a` and `b` are linear in the cube roots
 * of the LMS responses, so for a colour at linear level `Y` carrying a small
 * chromaticity excursion `ε`, chroma ≈ `Y^(1/3)·|ε|/3`. The plate composite
 * `(1 − α)·backdrop + α·neutral` keeps the backdrop's ABSOLUTE chromatic
 * excursion scaled by `(1 − α)` while moving the level to `Y_web`, so the body's
 * relative excursion is `(1 − α)·Y_b·ε_b / Y_web` and
 *
 *     chroma_body / chroma_backdrop
 *       = (1 − α) · Y_b^(2/3) · Y_web^(−2/3)
 *       = (1 − α) · (Y_web / Y_b)^(−2/3).
 *
 * It is the same `−2/3` the instrument's own level correction carries (§1), and
 * it is why the light scheme looked like it was losing chroma beyond the plate:
 * the light body sits far ABOVE its backdrop (0.50–0.58 against 0.21–0.25), so
 * the level term divides the plate's transmission down by about a half, while
 * the dark body sits just below its backdrop and the term is near 1.
 *
 * **The bed.** The untinted `photo` cells of the four macOS 27 standard
 * profiles, both scales, all sets, both poses, on the WebGPU tier — minus the
 * two components whose silhouette is a union of bodies. `toolbar-group` and
 * `glass-over-glass` have no single casting span (`optics.ts`'s
 * `InteriorSurfaceGeometry` says so in its own words, claims §5.74 §4), so the
 * size law has no one `sizedAlpha` to evaluate for them and they are named as
 * excluded rather than given an invented span. That leaves 34 cells. The CSS
 * tier is tabled beside, unbounded: its plate alpha is the CONVERTED one and
 * the predictor is written on the renderer's.
 *
 * Reads `cut.json`, which is committed, and the four shipped documents. It
 * needs no capture and no scratch matrix.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  sizeThickness,
  withMaterialOverrides,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "profiles");

const read = (name: string): MaterialProfilePatch =>
  (JSON.parse(readFileSync(resolve(PROFILES, `${name}.json`), "utf8")) as { patch: MaterialProfilePatch })
    .patch;

const LIGHT = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read("apple-macos-27.0-1x-light-standard-glass0.5"));
const DARK = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read("apple-macos-27.0-1x-dark-standard-glass0.5"));
const DOCUMENTS = {
  "light/active": LIGHT,
  "light/inactive": withMaterialOverrides(LIGHT, read("apple-macos-27.0-1x-light-standard-glass0.5-receded")),
  "dark/active": DARK,
  "dark/inactive": withMaterialOverrides(DARK, read("apple-macos-27.0-1x-dark-standard-glass0.5-receded")),
} as const;

/** The two components whose silhouette is a union of bodies, named not skipped. */
const NO_SINGLE_SPAN = new Set(["toolbar-group", "glass-over-glass"]);

interface CutRow {
  readonly backdrop: string;
  readonly component: string;
  readonly pose: string;
  readonly span: number;
  readonly scheme: "light" | "dark";
  readonly scale: number;
  readonly os: string;
  readonly a11y: string;
  readonly tinted: boolean;
  readonly active: boolean;
  readonly set: string;
  readonly tier: "texture" | "dom";
  readonly ratioII_web: number;
  readonly interiorMeanWeb: number;
  readonly interiorMeanBackdrop: number;
}

const rows = (
  JSON.parse(readFileSync(resolve(HERE, "cut.json"), "utf8")) as { rows: readonly CutRow[] }
).rows;

function sizedAlpha(profile: MaterialProfile, span: number): number {
  const k = sizeThickness(span, profile);
  const alpha = profile.optics.regular.tintAlpha;
  return alpha + profile.sizeOcclusionGain * k * (1 - alpha);
}

interface Reading {
  readonly cell: string;
  readonly tier: string;
  readonly scheme: string;
  readonly pose: string;
  readonly span: number;
  readonly sizedAlpha: number;
  readonly plate: number;
  readonly levelTerm: number;
  readonly predicted: number;
  readonly measured: number;
  readonly quality: number;
}

const readings: Reading[] = [];
const excluded: string[] = [];
for (const row of rows) {
  if (row.os !== "27" || row.a11y !== "standard") continue;
  if (row.backdrop !== "photo" || row.tinted) continue;
  const key = `${row.scale}x ${row.scheme} ${row.tier} ${row.component}__${row.pose}`;
  if (NO_SINGLE_SPAN.has(row.component)) {
    if (row.tier === "texture") excluded.push(key);
    continue;
  }
  const document = DOCUMENTS[`${row.scheme}/${row.active ? "active" : "inactive"}`];
  const alpha = sizedAlpha(document, row.span);
  const plate = 1 - alpha;
  const levelTerm = (row.interiorMeanWeb / row.interiorMeanBackdrop) ** (-2 / 3);
  const predicted = plate * levelTerm;
  readings.push({
    cell: key,
    tier: row.tier,
    scheme: row.scheme,
    pose: row.active ? "active" : "inactive",
    span: row.span,
    sizedAlpha: alpha,
    plate,
    levelTerm,
    predicted,
    measured: row.ratioII_web,
    quality: row.ratioII_web / predicted,
  });
}

function summarise(tier: string): void {
  const bed = readings.filter((reading) => reading.tier === tier);
  const quality = bed.map((reading) => reading.quality).sort((a, b) => a - b);
  console.log(
    `\n== ${tier} tier: ${String(bed.length)} cells, measured / predicted ` +
      `${(quality[0] ?? Number.NaN).toFixed(4)}–${(quality[quality.length - 1] ?? Number.NaN).toFixed(4)}, ` +
      `median ${(quality[Math.floor(quality.length / 2)] ?? Number.NaN).toFixed(4)} ==`,
  );
  console.log(
    "  cell".padEnd(44) +
      "span  1−sizedAlpha  (Yw/Yb)^-2/3  predicted  measured  meas/pred",
  );
  for (const reading of [...bed].sort((a, b) => a.quality - b.quality)) {
    console.log(
      `  ${reading.cell.padEnd(42)}${String(reading.span).padStart(4)}` +
        `${reading.plate.toFixed(4).padStart(14)}${reading.levelTerm.toFixed(4).padStart(14)}` +
        `${reading.predicted.toFixed(4).padStart(11)}${reading.measured.toFixed(4).padStart(10)}` +
        `${reading.quality.toFixed(4).padStart(11)}`,
    );
  }
}

console.log("== the plate predictor, ratio (ii)_web ≈ (1 − sizedAlpha)·(Y_web/Y_backdrop)^(−2/3) ==");
console.log(`\nexcluded, no single casting span: ${excluded.sort().join(", ")}`);
summarise("texture");
summarise("dom");

const gpu = readings.filter((reading) => reading.tier === "texture");
const low = Math.min(...gpu.map((reading) => reading.quality));
const high = Math.max(...gpu.map((reading) => reading.quality));
console.log(`
== what G3 takes from it ==

  On the WebGPU tier the measured ratio (ii) is ${low.toFixed(3)}–${high.toFixed(3)} of the predicted
  one on every one of the ${String(gpu.length)} cells, in both schemes and both poses, with no fitted
  parameter in the predictor at all. Three consequences for the fit:

  (a) **§5's reading is right and its arithmetic was incomplete.** The light
      scheme is not "losing chroma beyond the plate": it is sitting 2.4× above
      its own backdrop, and the −2/3 exponent is what turns 0.5130 of plate
      transmission into the 0.25–0.32 the cells read. The residual left over is
      the ${((1 - high) * 100).toFixed(1)}–${((1 - low) * 100).toFixed(1)} % the predictor does not account for, not a factor of two.

  (b) **The retention's target is predictable before it is fitted.** A retention
      \`r\` restores toward the backdrop's chromaticity at the body's own luma, so
      it moves the plate factor from \`1 − α\` toward 1 while the level term is
      untouched — the level is preserved by construction. The value that lands
      ratio (ii) on the reference's is therefore readable off this table rather
      than searched for.

  (c) **A fit that moves the level moves this statistic through the same
      exponent**, which is the level stop's reason stated one more way.
`);

writeFileSync(
  resolve(HERE, "plate-predictor.json"),
  `${JSON.stringify({ closure: "W31 G0 review closure, carried forward", excluded: excluded.sort(), readings }, null, 2)}\n`,
);
console.log("wrote plate-predictor.json");
