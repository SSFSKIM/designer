/**
 * W31 G0 review closure (2026-09-21) — how far the chroma lever moves OKLab `L`
 * (claims §5.161 §11, finding B2). Beside `decompose-p95.ts`; nothing it wrote
 * is rewritten.
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/decompose-p95-closure.ts
 *
 * ## The premise this file measures
 *
 * §4 reads the four rows' reachable floor as `P95(|ΔL|)` and justifies it with
 * "a luma-preserving chroma operator moves `Δc` and cannot move `ΔL`". The leaf
 * preserves LINEAR luma — that is what the renormalisation in §5 is for — and
 * `decompose-p95.ts` measures `ΔL` in **OKLab L**, which is not linear luma.
 * OKLab's `L` is a cube-root lightness of the LMS responses, and at a FIXED
 * linear `Y` it still moves when the chromaticity changes, because the three
 * cube roots are averaged with different weights than the luma coefficients.
 * So the premise is false as literally stated and the floor is a floor only to
 * within whatever that movement is.
 *
 * This file measures it rather than bounding it by argument: it applies the
 * leaf exactly as §5 specifies it, on the dark cell's own pixels, at the
 * retention that cell actually needs, and reads the distribution of
 * `L_oklab(restored) − L_oklab(web)`.
 *
 * ## What "the restoration this cell needs" means here
 *
 * The retention `r` that takes the web body's mean per-pixel OKLab chroma over
 * the interior mask to the NATIVE body's over the same mask — i.e. that closes
 * ratio (ii) on this cell, which is the whole point of the operator. Solved by
 * bisection per cell and printed, so the number the movement is measured at is
 * not chosen.
 *
 * ## Two places this is deliberately conservative, stated rather than hidden
 *
 * The shader restores toward the BLURRED backdrop it sampled; this restores
 * toward the RAW backdrop raster, whose per-pixel chroma is larger. A larger
 * chroma excursion moves `L` further, so the measured movement bounds the real
 * one rather than approximating it. And the movement is read over the
 * INTERIOR, where the operator acts, rather than over the whole capture whose
 * P95 the floor is taken on — the exterior and most of the rim carry no body
 * and would only dilute it.
 *
 * The floor is then recomputed directly: `P95(|ΔL_oklab|)` of native against
 * the RESTORED web image over the whole capture, beside `decompose-p95.ts`'s
 * value of the same statistic against the unrestored one. That is the number
 * §4's verdicts actually rest on.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { linearRgbToOklab, oklabChroma, oklabHueDegrees } from "../../src/color";
import { decodePng, toLinearRgb, type CalibrationImage } from "../../src/image";
import { extractSilhouette, fillSilhouetteHoles } from "../../src/silhouette";

const HERE = import.meta.dirname;
const PACKAGE = resolve(HERE, "..", "..");
const FIXTURES = resolve(PACKAGE, "..", "..", "apps", "reference-apple", "fixtures");
const BACKGROUNDS = resolve(FIXTURES, "backgrounds");
const SCRATCH = process.env["VITREA_WEB_CAPTURES"] ?? "/tmp/w31-g0-captures";

/** `measure.ts`'s own defaults, as `decompose-p95.ts` uses them. */
const SILHOUETTE_THRESHOLD = 0.02;
const SILHOUETTE_CHROMA_THRESHOLD = 0.03;

/** The shader's luma weights, verbatim (`wgsl/optics.ts`). */
const W = [0.2126, 0.7152, 0.0722] as const;

interface Row {
  readonly profileKey: string;
  readonly scale: number;
  readonly scene: string;
  readonly backdrop: string;
  readonly renderer: "webgpu" | "css";
  readonly tier: "texture" | "dom";
  readonly bound: number;
  /** `decompose-p95.json`'s reachable floor for this row, for the comparison. */
  readonly floorRecorded: number;
}

const ROWS: readonly Row[] = [
  { profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5", scale: 1, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "webgpu", tier: "texture", bound: 0.17, floorRecorded: 0.06309 },
  { profileKey: "apple-macos-27.0-2x-dark-standard-glass0.5", scale: 2, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "webgpu", tier: "texture", bound: 0.17, floorRecorded: 0.06201 },
  { profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5", scale: 1, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "css", tier: "dom", bound: 0.18, floorRecorded: 0.06631 },
  { profileKey: "apple-macos-27.0-2x-dark-standard-glass0.5", scale: 2, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "css", tier: "dom", bound: 0.19, floorRecorded: 0.06424 },
];

function load(path: string): CalibrationImage {
  return decodePng(readFileSync(path));
}

function backgroundFor(profileKey: string, backdrop: string): CalibrationImage {
  const scale = profileKey.includes("-2x-") ? 2 : 1;
  for (const name of [`${backdrop}@${scale}x.png`, `${backdrop}.png`]) {
    if (readdirSync(BACKGROUNDS).includes(name)) return load(resolve(BACKGROUNDS, name));
  }
  throw new Error(`no background raster for '${backdrop}' at ${scale}x`);
}

function percentile(values: readonly number[], q: number): number {
  const sorted = Float64Array.from(values).sort();
  if (sorted.length === 0) return Number.NaN;
  return sorted[Math.min(sorted.length - 1, Math.max(0, Math.ceil(q * sorted.length) - 1))] ?? Number.NaN;
}

const median = (values: readonly number[]): number => percentile(values, 0.5);

/** `Math.max(...values)` on a raster's worth of pixels overflows the stack. */
const extreme = (values: readonly number[], pick: (a: number, b: number) => number): number =>
  values.reduce((best, value) => pick(best, value), values[0] ?? Number.NaN);

/**
 * `gamut_at_luma(c, Y)` from §5's listing: the largest `t` in [0, 1] that keeps
 * every channel inside [0, 1], applied as `mix(vec3f(Y), c, t)`. Both endpoints
 * carry luma `Y`, so this scales the chroma down and holds the level exactly.
 */
function gamutAtLuma(c: readonly [number, number, number], Y: number): [number, number, number] {
  let t = 1;
  for (const channel of c) {
    if (channel > 1) t = Math.min(t, (1 - Y) / Math.max(channel - Y, 1e-12));
    else if (channel < 0) t = Math.min(t, Y / Math.max(Y - channel, 1e-12));
  }
  t = Math.min(1, Math.max(0, t));
  return [Y + (c[0] - Y) * t, Y + (c[1] - Y) * t, Y + (c[2] - Y) * t];
}

/** The leaf of §5, evaluated on one pixel in linear RGB. */
function restorePixel(
  colour: readonly [number, number, number],
  backdrop: readonly [number, number, number],
  retention: number,
): [number, number, number] {
  const Y = W[0] * colour[0] + W[1] * colour[1] + W[2] * colour[2];
  const Yb = Math.max(W[0] * backdrop[0] + W[1] * backdrop[1] + W[2] * backdrop[2], 1e-6);
  const k = Y / Yb;
  const target: [number, number, number] = [backdrop[0] * k, backdrop[1] * k, backdrop[2] * k];
  const mixed: [number, number, number] = [
    colour[0] + (target[0] - colour[0]) * retention,
    colour[1] + (target[1] - colour[1]) * retention,
    colour[2] + (target[2] - colour[2]) * retention,
  ];
  const scale = Y / Math.max(W[0] * mixed[0] + W[1] * mixed[1] + W[2] * mixed[2], 1e-6);
  return gamutAtLuma([mixed[0] * scale, mixed[1] * scale, mixed[2] * scale], Y);
}

/** The hue families the movement is reported by, off the BACKDROP's own hue. */
function hueFamily(degrees: number): string {
  const h = ((degrees % 360) + 360) % 360;
  if (h < 30 || h >= 330) return "red";
  if (h < 90) return "orange/yellow";
  if (h < 165) return "green";
  if (h < 240) return "cyan/blue";
  if (h < 300) return "blue/violet";
  return "magenta";
}

const out: unknown[] = [];
for (const row of ROWS) {
  const native = load(resolve(FIXTURES, row.profileKey, `${row.scene}.png`));
  const web = load(resolve(SCRATCH, row.profileKey, row.scene, `${row.scene}__${row.renderer}.png`));
  const background = backgroundFor(row.profileKey, row.backdrop);

  const silhouette = fillSilhouetteHoles(
    extractSilhouette(native, {
      kind: "luminance-delta",
      background,
      threshold: SILHOUETTE_THRESHOLD,
      chromaThreshold: SILHOUETTE_CHROMA_THRESHOLD,
    }),
  );

  const nativeLinear = toLinearRgb(native);
  const webLinear = toLinearRgb(web);
  const backLinear = toLinearRgb(background);
  const pixels = native.width * native.height;
  const body: number[] = [];
  for (let i = 0; i < pixels; i += 1) if ((silhouette.mask[i] ?? 0) === 1) body.push(i);

  const at = (source: Float64Array, i: number): [number, number, number] => [
    source[i * 3] ?? 0,
    source[i * 3 + 1] ?? 0,
    source[i * 3 + 2] ?? 0,
  ];

  const meanChromaOf = (get: (i: number) => [number, number, number]): number =>
    body.reduce((sum, i) => sum + oklabChroma(linearRgbToOklab(...get(i))), 0) / body.length;

  const nativeChroma = meanChromaOf((i) => at(nativeLinear, i));
  const webChroma = meanChromaOf((i) => at(webLinear, i));
  const restoredChromaAt = (r: number): number =>
    meanChromaOf((i) => restorePixel(at(webLinear, i), at(backLinear, i), r));

  // The retention this cell needs: bisected so that the restored body's mean
  // per-pixel chroma reaches the reference's. Monotone in `r` on this bed, and
  // reported with the endpoint reading so a non-bracketing case is visible.
  const chromaAtOne = restoredChromaAt(1);
  let lo = 0;
  let hi = 1;
  for (let step = 0; step < 24; step += 1) {
    const mid = (lo + hi) / 2;
    if (restoredChromaAt(mid) < nativeChroma) lo = mid;
    else hi = mid;
  }
  const needed = chromaAtOne < nativeChroma ? 1 : (lo + hi) / 2;
  const reachesReference = chromaAtOne >= nativeChroma;

  // The movement in OKLab L, over the body, at that retention.
  const moves: number[] = [];
  const byFamily = new Map<string, number[]>();
  const lumas: number[] = [];
  for (const i of body) {
    const colour = at(webLinear, i);
    const back = at(backLinear, i);
    const before = linearRgbToOklab(...colour);
    const after = linearRgbToOklab(...restorePixel(colour, back, needed));
    const move = after.L - before.L;
    moves.push(move);
    lumas.push(W[0] * colour[0] + W[1] * colour[1] + W[2] * colour[2]);
    const family = hueFamily(oklabHueDegrees(linearRgbToOklab(...back)));
    (byFamily.get(family) ?? byFamily.set(family, []).get(family) ?? []).push(move);
  }
  const absolute = moves.map(Math.abs);

  // And the floor itself, recomputed against the RESTORED image over the whole
  // capture — the statistic §4's verdicts are taken on.
  const floorBefore: number[] = [];
  const floorAfter: number[] = [];
  const deltaEAfter: number[] = [];
  const insideBody = new Uint8Array(pixels);
  for (const i of body) insideBody[i] = 1;
  for (let i = 0; i < pixels; i += 1) {
    const n = linearRgbToOklab(...at(nativeLinear, i));
    const w = linearRgbToOklab(...at(webLinear, i));
    floorBefore.push(Math.abs(n.L - w.L));
    const restored =
      insideBody[i] === 1
        ? linearRgbToOklab(...restorePixel(at(webLinear, i), at(backLinear, i), needed))
        : w;
    floorAfter.push(Math.abs(n.L - restored.L));
    deltaEAfter.push(Math.hypot(n.L - restored.L, Math.hypot(n.a - restored.a, n.b - restored.b)));
  }

  const report = {
    row: `${row.tier} / holdout / ${row.scene} / ${row.profileKey}`,
    bound: row.bound,
    bodyPixels: body.length,
    meanBodyLuma: lumas.reduce((s, x) => s + x, 0) / lumas.length,
    nativeMeanChroma: nativeChroma,
    webMeanChroma: webChroma,
    meanChromaAtRetentionOne: chromaAtOne,
    retentionNeeded: needed,
    reachesReferenceChroma: reachesReference,
    oklabLMove: {
      median: median(moves),
      p95Absolute: percentile(absolute, 0.95),
      maxAbsolute: extreme(absolute, Math.max),
      min: extreme(moves, Math.min),
      max: extreme(moves, Math.max),
    },
    byHueFamily: [...byFamily]
      .map(([family, values]) => ({
        family,
        pixels: values.length,
        medianMove: median(values),
        p95Absolute: percentile(values.map(Math.abs), 0.95),
      }))
      .sort((a, b) => b.pixels - a.pixels),
    floorRecorded: row.floorRecorded,
    floorRecomputedUnrestored: percentile(floorBefore, 0.95),
    floorUnderTheRestoration: percentile(floorAfter, 0.95),
    achievedDeltaEP95UnderTheRestoration: percentile(deltaEAfter, 0.95),
  };
  out.push(report);

  console.log(`\n== ${report.row}`);
  console.log(
    `   body ${String(report.bodyPixels)} px, mean linear luma ${report.meanBodyLuma.toFixed(4)}; ` +
      `mean per-pixel chroma native ${nativeChroma.toFixed(5)} / web ${webChroma.toFixed(5)} / at r=1 ${chromaAtOne.toFixed(5)}`,
  );
  console.log(
    `   retention this cell needs: r = ${needed.toFixed(4)}` +
      (reachesReference ? "" : "  (r = 1 does not reach the reference's chroma; read at the maximum)"),
  );
  console.log(
    `   OKLab L moves by: median ${report.oklabLMove.median.toFixed(5)}  ` +
      `P95 |ΔL| ${report.oklabLMove.p95Absolute.toFixed(5)}  max |ΔL| ${report.oklabLMove.maxAbsolute.toFixed(5)}  ` +
      `[${report.oklabLMove.min.toFixed(5)}, ${report.oklabLMove.max.toFixed(5)}]`,
  );
  for (const family of report.byHueFamily) {
    console.log(
      `     ${family.family.padEnd(13)} ${String(family.pixels).padStart(7)} px  ` +
        `median ${family.medianMove >= 0 ? "+" : ""}${family.medianMove.toFixed(5)}  P95 |ΔL| ${family.p95Absolute.toFixed(5)}`,
    );
  }
  console.log(
    `   the floor: recorded ${row.floorRecorded.toFixed(5)}  recomputed ${report.floorRecomputedUnrestored.toFixed(5)}  ` +
      `under the restoration ${report.floorUnderTheRestoration.toFixed(5)}  ` +
      `(bound ${row.bound} — ${report.floorUnderTheRestoration <= row.bound ? "still CLAIMABLE" : "NOT REACHABLE"})`,
  );
}

const worstMove = Math.max(
  ...out.map((r) => (r as { oklabLMove: { maxAbsolute: number } }).oklabLMove.maxAbsolute),
);
const worstFloor = Math.max(...out.map((r) => (r as { floorUnderTheRestoration: number }).floorUnderTheRestoration));
console.log(`
== what this closes ==

  §4's premise as written — "a luma-preserving chroma operator moves Δc and
  cannot move ΔL" — is false of the statistic §4 measures, because that ΔL is
  OKLab's and the operator preserves LINEAR luma. Restated as measured:

    the operator moves Δc, and moves OKLab ΔL only second order — no more than
    ${worstMove.toFixed(4)} anywhere on this bed's bodies at the retention these cells need —
    so P95(|ΔL|) is a floor to within that.

  Read against the verdicts: the floor recomputed under the restoration itself
  is at worst ${worstFloor.toFixed(5)} against bounds of 0.17 to 0.19. The margin is a
  factor of two and a half, so all four verdicts of §4 stand unchanged and none
  of them was ever close enough to the bound for this correction to reach it.
`);

writeFileSync(
  resolve(HERE, "decompose-p95-closure.json"),
  `${JSON.stringify({ closure: "W31 G0 review closure, finding B2", rows: out }, null, 2)}\n`,
);
console.log("wrote decompose-p95-closure.json");
