/**
 * W31 G0 — the four claimed rows, decomposed (acceptance clause 3; claims §5.161 §4).
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/decompose-p95.ts
 *
 * `oklabDeltaEP95` is the 95th percentile of a per-pixel OKLab distance over the
 * WHOLE capture — interior, rim and exterior together — and four of the seven
 * rows 0.19.0 and 0.20.0 record as missed are one cell's, `photo__rrect-lg__rest`
 * on both dark profiles and both tiers. Before this wave declares any of them
 * CLAIMED it has to know how much of that distance the chroma lever can even
 * reach, and the distance is a Euclidean norm of two independent parts:
 *
 *     ΔE² = ΔL² + (Δa² + Δb²) = ΔL² + Δc²
 *
 * A chroma operator moves `Δc` and cannot move `ΔL` — the retention this wave
 * names is luma-preserving in linear luma by construction, which is the whole
 * reason for the renormalisation. So the BEST a chroma lever alone can do on a
 * row is drive `Δc` to zero at every pixel, leaving `ΔE = |ΔL|`, and the row's
 * reachable value is then the P95 of `|ΔL|` over the same population. That
 * number is the headroom, and it decides CLAIMED against "reachable if".
 *
 * It is a strict bound in one direction and honest about it: a real retention
 * will not zero `Δc` everywhere, so the reachable value is a floor rather than
 * a prediction. A row whose bound already sits above its threshold is
 * unreachable by this lever no matter how well it is fitted, and that is a
 * verdict the fit cannot argue with.
 *
 * Three regions, because the P95 of a whole-capture statistic can be owned by a
 * few hundred boundary pixels: `rim` is within `RIM_BAND_CSS_PX` of the
 * reference silhouette's contour on either side, `interior` is inside beyond
 * it, `exterior` is outside beyond it. The band is 8 CSS px, wider than the
 * widest shipped `rimWidth` (6.5 on the macOS 27 light document) so the whole
 * lit edge and its antialiasing fall in one region rather than being split
 * across two.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { linearRgbToOklab } from "../../src/color";
import { decodePng, toLinearRgb, type CalibrationImage } from "../../src/image";
import {
  boundaryMask,
  distanceToSeeds,
  extractSilhouette,
  fillSilhouetteHoles,
} from "../../src/silhouette";

const HERE = import.meta.dirname;
const PACKAGE = resolve(HERE, "..", "..");
const FIXTURES = resolve(PACKAGE, "..", "..", "apps", "reference-apple", "fixtures");
const BACKGROUNDS = resolve(FIXTURES, "backgrounds");
const SCRATCH = process.env["VITREA_WEB_CAPTURES"] ?? "/tmp/w31-g0-captures";

const RIM_BAND_CSS_PX = 8;
/** `measure.ts`'s own default, so the mask here is the mask the rows were read under. */
const SILHOUETTE_THRESHOLD = 0.02;
const SILHOUETTE_CHROMA_THRESHOLD = 0.03;

interface Row {
  readonly profileKey: string;
  readonly scale: number;
  readonly scene: string;
  readonly backdrop: string;
  readonly renderer: "webgpu" | "css";
  readonly tier: "texture" | "dom";
  readonly bound: number;
  readonly committed: number;
}

/** The four rows `MISSED_27_ROWS` holds on this cell, with their adopted bounds. */
const ROWS: readonly Row[] = [
  { profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5", scale: 1, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "webgpu", tier: "texture", bound: 0.17, committed: 0.21531 },
  { profileKey: "apple-macos-27.0-2x-dark-standard-glass0.5", scale: 2, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "webgpu", tier: "texture", bound: 0.17, committed: 0.21341 },
  { profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5", scale: 1, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "css", tier: "dom", bound: 0.18, committed: 0.20095 },
  { profileKey: "apple-macos-27.0-2x-dark-standard-glass0.5", scale: 2, scene: "photo__rrect-lg__rest", backdrop: "photo", renderer: "css", tier: "dom", bound: 0.19, committed: 0.19474 },
];

function load(path: string): CalibrationImage {
  return decodePng(readFileSync(path));
}

/**
 * The backdrop raster the harness rendered this profile's scenes over, keyed the
 * way `manifest.json` keys it: `<background>@<scale>x`, with the unsuffixed name
 * as the schema-2 fallback `compare` also honours.
 */
function backgroundFor(profileKey: string, backdrop: string): CalibrationImage {
  const scale = profileKey.includes("-2x-") ? 2 : 1;
  for (const name of [`${backdrop}@${scale}x.png`, `${backdrop}.png`]) {
    if (readdirSync(BACKGROUNDS).includes(name)) return load(resolve(BACKGROUNDS, name));
  }
  throw new Error(`no background raster for '${backdrop}' at ${scale}x`);
}

function percentile(values: Float64Array, q: number): number {
  const sorted = Float64Array.from(values).sort();
  if (sorted.length === 0) return Number.NaN;
  const index = Math.min(sorted.length - 1, Math.max(0, Math.ceil(q * sorted.length) - 1));
  return sorted[index] ?? Number.NaN;
}

interface RegionReport {
  readonly region: string;
  readonly pixels: number;
  readonly deltaEP95: number;
  readonly deltaLP95: number;
  readonly deltaChromaP95: number;
  /** The P95 of ΔE with Δc driven to zero — the chroma lever's floor on this region. */
  readonly reachableP95: number;
  /** Mean share of ΔE² owned by the chromatic part, over the pixels at or above the whole-capture P95. */
  readonly chromaShareAtP95: number;
}

function decompose(
  native: CalibrationImage,
  web: CalibrationImage,
  regions: ReadonlyMap<string, Uint8Array>,
): { whole: RegionReport; byRegion: readonly RegionReport[] } {
  const a = toLinearRgb(native);
  const b = toLinearRgb(web);
  const pixels = native.width * native.height;
  const deltaE = new Float64Array(pixels);
  const deltaL = new Float64Array(pixels);
  const deltaC = new Float64Array(pixels);
  for (let i = 0; i < pixels; i += 1) {
    const x = linearRgbToOklab(a[i * 3] ?? 0, a[i * 3 + 1] ?? 0, a[i * 3 + 2] ?? 0);
    const y = linearRgbToOklab(b[i * 3] ?? 0, b[i * 3 + 1] ?? 0, b[i * 3 + 2] ?? 0);
    const dl = x.L - y.L;
    const dc = Math.hypot(x.a - y.a, x.b - y.b);
    deltaL[i] = Math.abs(dl);
    deltaC[i] = dc;
    deltaE[i] = Math.hypot(dl, dc);
  }

  const wholeP95 = percentile(deltaE, 0.95);
  const report = (region: string, mask: Uint8Array | undefined): RegionReport => {
    const keep: number[] = [];
    for (let i = 0; i < pixels; i += 1) if (mask === undefined || (mask[i] ?? 0) === 1) keep.push(i);
    const pick = (source: Float64Array): Float64Array =>
      Float64Array.from(keep, (i) => source[i] ?? 0);
    const hot = keep.filter((i) => (deltaE[i] ?? 0) >= wholeP95);
    const share =
      hot.length === 0
        ? Number.NaN
        : hot.reduce((sum, i) => {
            const e2 = (deltaE[i] ?? 0) ** 2;
            return sum + (e2 === 0 ? 0 : (deltaC[i] ?? 0) ** 2 / e2);
          }, 0) / hot.length;
    return {
      region,
      pixels: keep.length,
      deltaEP95: percentile(pick(deltaE), 0.95),
      deltaLP95: percentile(pick(deltaL), 0.95),
      deltaChromaP95: percentile(pick(deltaC), 0.95),
      // With Δc at zero the distance IS |ΔL|, so the reachable P95 of ΔE over
      // this region is the P95 of |ΔL| over the same population.
      reachableP95: percentile(pick(deltaL), 0.95),
      chromaShareAtP95: share,
    };
  };

  return {
    whole: report("whole capture", undefined),
    byRegion: [...regions].map(([name, mask]) => report(name, mask)),
  };
}

const out: unknown[] = [];
for (const row of ROWS) {
  const nativePath = resolve(FIXTURES, row.profileKey, `${row.scene}.png`);
  const webPath = resolve(SCRATCH, row.profileKey, row.scene, `${row.scene}__${row.renderer}.png`);
  const native = load(nativePath);
  const web = load(webPath);
  const background = backgroundFor(row.profileKey, row.backdrop);

  /*
   * Holes filled before the contour is traced, which is claims §5.15's
   * correction applied to the region split.
   *
   * The luminance-delta rule's premise — anything differing from the background
   * is the surface — is false wherever the material's own level meets the
   * backdrop's, and a hole is exactly where that happened. This cell's
   * reference silhouette carries 68 of them, and an unfilled mask puts a
   * `RIM_BAND_CSS_PX` band around every one: the `rim` region then holds two
   * thirds of the body's interior and the split says nothing. Filling makes
   * `rim` the OUTLINE's band, which is what the three regions are supposed to
   * mean.
   */
  const silhouette = fillSilhouetteHoles(
    extractSilhouette(native, {
      kind: "luminance-delta",
      background,
      threshold: SILHOUETTE_THRESHOLD,
      chromaThreshold: SILHOUETTE_CHROMA_THRESHOLD,
    }),
  );
  const boundary = boundaryMask(silhouette);
  const distance = distanceToSeeds(boundary, silhouette.width, silhouette.height);
  const band = RIM_BAND_CSS_PX * row.scale;

  const pixels = native.width * native.height;
  const interior = new Uint8Array(pixels);
  const rim = new Uint8Array(pixels);
  const exterior = new Uint8Array(pixels);
  for (let i = 0; i < pixels; i += 1) {
    const inside = (silhouette.mask[i] ?? 0) === 1;
    const d = distance[i] ?? 0;
    if (d <= band) rim[i] = 1;
    else if (inside) interior[i] = 1;
    else exterior[i] = 1;
  }

  const { whole, byRegion } = decompose(
    native,
    web,
    new Map([
      ["interior", interior],
      ["rim", rim],
      ["exterior", exterior],
    ]),
  );

  const name = `${row.tier} / holdout / ${row.scene} / ${row.profileKey} :: oklabDeltaEP95`;
  console.log(`\n== ${name}`);
  console.log(`   bound ${row.bound}   committed ${row.committed}   scratch ${whole.deltaEP95.toFixed(5)}`);
  console.log(
    `   reproduction: ${(Math.abs(whole.deltaEP95 - row.committed) <= 0.0005 ? "OK" : "DIFFERS")} ` +
      `(|Δ| ${Math.abs(whole.deltaEP95 - row.committed).toFixed(6)})`,
  );
  console.log(
    `   whole capture: ΔE P95 ${whole.deltaEP95.toFixed(5)}  |ΔL| P95 ${whole.deltaLP95.toFixed(5)}  ` +
      `Δc P95 ${whole.deltaChromaP95.toFixed(5)}  chroma share of ΔE² at the P95 pixels ${(whole.chromaShareAtP95 * 100).toFixed(1)}%`,
  );
  console.log(
    `   REACHABLE by the chroma lever alone (Δc → 0): ${whole.reachableP95.toFixed(5)} against a bound of ${row.bound}` +
      `  → ${whole.reachableP95 <= row.bound ? "CLAIMABLE" : "NOT REACHABLE by this lever"}`,
  );
  for (const region of byRegion) {
    console.log(
      `     ${region.region.padEnd(9)} ${String(region.pixels).padStart(7)} px  ` +
        `ΔE P95 ${region.deltaEP95.toFixed(5)}  |ΔL| P95 ${region.deltaLP95.toFixed(5)}  ` +
        `Δc P95 ${region.deltaChromaP95.toFixed(5)}  chroma share at the P95 pixels ${(region.chromaShareAtP95 * 100).toFixed(1)}%`,
    );
  }
  out.push({ row: name, ...row, whole, byRegion });
}

writeFileSync(
  resolve(HERE, "decompose-p95.json"),
  `${JSON.stringify({ rimBandCssPx: RIM_BAND_CSS_PX, rows: out }, null, 2)}\n`,
);
console.log("\nwrote decompose-p95.json");
