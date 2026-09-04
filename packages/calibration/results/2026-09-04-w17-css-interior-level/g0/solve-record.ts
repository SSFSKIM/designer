/**
 * W17 G0 (d) — the six probe cells' solves, recorded.
 *
 * The captures in §4 were taken with the solve running inside the tier; this script re-evaluates
 * the same two functions on the same inputs so the intercept and the slope are on the record as
 * numbers rather than only as a mechanism. The overlay is `cssTintAlpha` / `cssTintColor` at the
 * mapping's own `referenceBackdropLuminance`, which is what the tier converts before
 * `cssTierDeclarations` applies the size law's occlusion to the alpha — so these coefficients are
 * the solve's shape and are within that last fold of the ones the capture ran under.
 *
 * Usage: `npx tsx solve-record.ts <analyticJson> <outJson>`, from `packages/calibration`.
 */
import { readFileSync, writeFileSync } from "node:fs";

import { CSS_TIER_MAPPING, cssTintAlpha, cssTintColor, sourceOptics } from "@vitreajs/vitrea-web";

import { w17CarrierSolve, w17DerivedExcess } from "./carrier-patch/w17-carrier";

const PROBES = new Set([
  "checkerboard__rrect-md__rest",
  "checkerboard__capsule-button__rest",
  "checkerboard__rrect-ml__rest",
]);

const rows = (JSON.parse(readFileSync(process.argv[2]!, "utf8")) as {
  profileKey: string; sceneId: string; span: number; radius: number;
  toneLinearMean: number; shaderOrderAlpha: number; shaderOrderTintLuma: number;
}[]).filter((row) => PROBES.has(row.sceneId) && row.profileKey.includes("-light-standard"));

const BOUNDS: Record<string, [number, number]> = {
  "checkerboard__rrect-md__rest": [160, 96],
  "checkerboard__capsule-button__rest": [120, 44],
  "checkerboard__rrect-ml__rest": [240, 128],
};

const out = rows.map((row) => {
  const [w, h] = BOUNDS[row.sceneId]!;
  const source = {
    ...sourceOptics().regular,
    tint: [row.shaderOrderTintLuma, row.shaderOrderTintLuma, row.shaderOrderTintLuma] as const,
    tintAlpha: row.shaderOrderAlpha,
  };
  const cssAlpha = cssTintAlpha(source as never, CSS_TIER_MAPPING);
  const cssTint = cssTintColor(source as never, cssAlpha, CSS_TIER_MAPPING);
  const excess = w17DerivedExcess({
    widthCssPx: w, heightCssPx: h, radiusCssPx: row.radius, rimAlpha: 0.18, present: 1,
  });
  const transfer = w17CarrierSolve({
    backdropLuminance: row.toneLinearMean,
    rendererAlpha: row.shaderOrderAlpha,
    rendererTintLuminance: row.shaderOrderTintLuma,
    excess,
    cssAlpha,
    cssTintEncoded: (0.2126 * cssTint[0] + 0.7152 * cssTint[1] + 0.0722 * cssTint[2]) / 255,
  });
  return { ...row, boundsCssPx: [w, h], cssAlpha, cssTint, excess, transfer };
});

writeFileSync(process.argv[3]!, `${JSON.stringify(out, null, 1)}\n`);
for (const row of out) {
  process.stdout.write(
    `${row.profileKey.slice(17, 19)} ${row.sceneId.padEnd(34)} b0=${row.toneLinearMean.toFixed(4)} ` +
      `alpha=${row.shaderOrderAlpha.toFixed(4)} T=${row.shaderOrderTintLuma.toFixed(4)} ` +
      `X=${row.excess.toFixed(5)} cssAlpha=${row.cssAlpha.toFixed(4)} ` +
      `slope=${row.transfer?.slope.toFixed(4) ?? "—"} intercept=${row.transfer?.intercept.toFixed(4) ?? "—"}\n`,
  );
}
