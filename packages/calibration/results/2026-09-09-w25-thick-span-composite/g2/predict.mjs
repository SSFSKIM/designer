/*
 * W25 G2 — the levers, through the renderer's OWN material functions.
 *
 * WHAT THIS READS. `rows.json` beside it (spans and backdrop means, written by `rows.py` from the
 * backdrop rasters alone) and `packages/renderer-webgpu/src/material.ts` directly, by relative
 * import. Nothing else, and it writes only what it is told to on stdout.
 *
 * WHY THROUGH THE SOURCE. The W23 lesson is that a fit's condition is checked before the fit; the
 * only honest way to state a lever is to differentiate the function that will draw it. So this
 * imports `sizeThickness`, `scatterDeepThickness`, `scatterThickness`, `sizeScatterSigma`,
 * `backdropToneResponse`, `sizeToneLevelFar`, `lensDepthPx`, `sizeOcclusionAlpha`,
 * `sizeShadowDepth` and `sizeThicknessUnderPolicy` from the renderer's own module and takes
 * numerical derivatives of them at the landed material — no restatement of any law in this file.
 *
 * UNITS. Sigmas in CSS px as the shared projection returns them. Level levers in 8-BIT DISPLAY
 * CODES, because that is the unit the reference's residual above the knee was read in and the unit
 * the wave's stops are written in; the tone response's own output is already an encoded level, so a
 * code is 255 times a difference in it.
 *
 * Run:  pnpm exec tsx results/2026-09-09-w25-thick-span-composite/g2/predict.mjs <mode>
 *   mode = share | level | rides
 */

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE,
  backdropToneResponse,
  lensDepthPx,
  scatterDeepThickness,
  scatterThickness,
  sizeOcclusionAlpha,
  sizeScatterSigma,
  sizeShadowDepth,
  sizeThickness,
  withMaterialOverrides,
} from "../../../../renderer-webgpu/src/material.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const rows = JSON.parse(readFileSync(resolve(HERE, "rows.json"), "utf8"));

const P = DEFAULT_MATERIAL_PROFILE;
const encode = (v) => (v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(v, 1 / 2.4) - 0.055);
const smoothstep = (a, b, x) => {
  const t = Math.min(1, Math.max(0, (x - a) / Math.max(b - a, 1e-6)));
  return t * t * (3 - 2 * t);
};
const f3 = (v) => (Number.isFinite(v) ? v.toFixed(3) : "—");
const f4 = (v) => (Number.isFinite(v) ? v.toFixed(4) : "—");

const mode = process.argv[2] ?? "share";
const sigma = P.optics.regular.blurSigma;

if (mode === "share") {
  /*
   * The share law's lever. The constant enters `kDeep` as `lift · sizeThickness(span)`, so the
   * derivative of the deep heavy share with respect to it is `sizeThickness` exactly and the
   * derivative of the shared single-σ projection is what a width reader would see. Both are
   * reported, together with the reader bound the row's own backdrop pitch imposes (G0 §1: reader C
   * identifies to about a quarter of the pitch and reader B to about an eighth, in device px).
   */
  const spans = [...new Set(rows.map((r) => r.spanCss))].sort((a, b) => a - b);
  console.log("span  sizeThickness  kDeep(0)  kDeep(+1)  mix(0)   mix(+1)  σ(0)    σ(+1)   dσ/dlift");
  for (const span of spans) {
    const lifted = withMaterialOverrides(P, { sizeScatterHeavyShareThick1x: 1 });
    const k0 = scatterDeepThickness(span, P, 1);
    const k1 = scatterDeepThickness(span, lifted, 1);
    const m0 = scatterThickness(span, 1, P, 1);
    const m1 = scatterThickness(span, 1, lifted, 1);
    const s0 = sizeScatterSigma(sigma, span, P, 1);
    const s1 = sizeScatterSigma(sigma, span, lifted, 1);
    console.log(
      `${String(span).padStart(4)}  ${f4(sizeThickness(span, P)).padStart(13)}  ` +
        `${f4(k0)}    ${f4(k1)}     ${f4(m0)}   ${f4(m1)}   ${f3(s0).padStart(6)}  ` +
        `${f3(s1).padStart(6)}  ${f3(s1 - s0).padStart(8)}`,
    );
  }
} else if (mode === "level") {
  /*
   * The level term's lever, per row: the change in the tone response's own target level, in 8-bit
   * codes, per unit of `sizeToneLevelFar`. The authority gate is applied, because a row whose
   * backdrop sits below half the dark anchor does not read the response at all and therefore does
   * not separate this constant however large its span is.
   */
  console.log(
    "bed          scene                                    span  bgLin    bgEnc   authority  " +
      "farS    codes/unit",
  );
  const seen = new Set();
  const levers = [];
  for (const r of rows) {
    if (r.holdout) continue;
    const key = `${r.bed}|${r.scene}|${r.sub}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const x = encode(Math.min(1, Math.max(0, r.backdropLinear)));
    const anchor = Math.max(P.backdropToneAnchorX[0], 1e-4);
    const authority = smoothstep(anchor * 0.5, anchor, x) * P.backdropToneResponseStrength;
    const farS = smoothstep(P.sizeSpanMax, P.sizeScatterSpanMax, r.spanCss);
    const thick = sizeThickness(r.spanCss, P);
    const base = backdropToneResponse(x, thick, P, 0);
    const moved = backdropToneResponse(x, thick, P, farS);
    const codes = (moved - base) * 255 * authority;
    console.log(
      `${r.bed.padEnd(12)} ${`${r.scene}${r.sub ? `/${r.sub}` : ""}`.padEnd(40)} ` +
        `${String(r.spanCss).padStart(4)}  ${f4(r.backdropLinear)}  ${f4(x)}  ` +
        `${f4(authority).padStart(9)}  ${f4(farS)}  ${f3(codes).padStart(10)}`,
    );
    levers.push({ bed: r.bed, scene: r.scene, sub: r.sub, span: r.spanCss, codesPerUnit: codes });
  }
  // The same table as machine-readable rows, which is what `fit.py --mode level` regresses on.
  writeFileSync(resolve(HERE, "levers.json"), `${JSON.stringify(levers, null, 1)}\n`);
} else if (mode === "rides") {
  /*
   * The four laws that ride `sizeThickness` (W25 risk register): the lens's depth, the occlusion's
   * alpha, the inner shadow's depth and the tone response's size bias, read at the landed material
   * and at the material with all three of W25's constants set to 1 — a value far outside any fit —
   * so that "none of them moves" is a measured statement about the code and not an argument about
   * the code's shape.
   */
  const moved = withMaterialOverrides(P, {
    sizeScatterHeavyShareThick1x: 1,
    sizeScatterHeavyShareThick2x: 1,
    sizeToneLevelFar: 1,
    optics: { regular: { rimAlongSideSlope: 1 } },
  });
  const spans = [...new Set(rows.map((r) => r.spanCss))].sort((a, b) => a - b);
  console.log("span  lensDepth(0)  lensDepth(1)  occl(0)   occl(1)   shadow(0)  shadow(1)  bias(0)   bias(1)");
  for (const span of spans) {
    const t = 8;
    const l0 = lensDepthPx(t, span, P, 1);
    const l1 = lensDepthPx(t, span, moved, 1);
    const o0 = sizeOcclusionAlpha(P.optics.regular.tintAlpha, span, P);
    const o1 = sizeOcclusionAlpha(moved.optics.regular.tintAlpha, span, moved);
    const s0 = sizeShadowDepth(P.optics.regular.shadowDepth, span, P);
    const s1 = sizeShadowDepth(moved.optics.regular.shadowDepth, span, moved);
    const b0 = P.backdropToneSizeBias * sizeThickness(span, P);
    const b1 = moved.backdropToneSizeBias * sizeThickness(span, moved);
    console.log(
      `${String(span).padStart(4)}  ${f4(l0).padStart(12)}  ${f4(l1).padStart(12)}  ` +
        `${f4(o0)}  ${f4(o1)}  ${f4(s0).padStart(9)}  ${f4(s1).padStart(9)}  ` +
        `${f4(b0)}  ${f4(b1)}`,
    );
  }
} else {
  throw new Error(`unknown mode ${mode}`);
}
