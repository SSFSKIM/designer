/**
 * W27c G1c: the CPU mirror's prediction for each rung — a mechanism, not a
 * measurement (claims §5.141).
 *
 * `platform-web/src/optics.ts` carries a term-for-term mirror of the shader's
 * scalar laws, pinned to it by `tier-coherence.test.ts`. Evaluating it costs no
 * browser and no GPU, and it answers a question the pixels cannot: WHY a cell
 * reads what it reads. Every number here is the mirror's, and the mirror is one
 * tier's arithmetic rather than the fidelity target, so nothing in this file is
 * evidence of fidelity and nothing is fitted to it. It exists so that the GPU
 * sweep beside it can be read as confirming a mechanism rather than as a curve
 * that happened to move.
 *
 * Usage:
 *   pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx \
 *     results/2026-09-13-w27c-g1c-fit/mirror-predict.ts
 */
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { materialAtBackdrop } from "../../../platform-web/src/optics";
import { decodePng } from "../../src/image";
import { resolveAccessibilityPolicy } from "../../../core/src/accessibility";
import { mergeMaterialProfiles } from "../../../platform-web/src/color-scheme";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");
const json = (file: string): any => JSON.parse(readFileSync(file, "utf8"));

const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const native = json(resolve(here, "native-response.json"));
const light = json(resolve(pkg, "profiles/apple-macos-26.5-1x-light-standard.json")).patch;
const dark = json(resolve(pkg, "profiles/apple-macos-26.5-1x-dark-standard.json")).patch;

const published = json(resolve(pkg, "results/2026-09-13-w27c-g2-read/checking-matrix.json"));
const components = matrix.components;

/**
 * The reference's own reading for a cell.
 *
 * The native-only pass walks the bundle, and the bundle does not hold every bed
 * cell: `light-solid__capsule-button__inactive` has no recovered fixture in
 * either dark profile at all (claims §5.139 §4), which is exactly why its dark
 * pair was never fitted or checked before this bed. For those the reading comes
 * from the published G2 matrix, which is committed evidence of the same bytes.
 */
const nativeRow = (profile: string, scene: string): any => {
  const own = native.rows.find((r: any) => r.profile === profile && r.scene === scene);
  if (own !== undefined) return own;
  const row = published.rows.find((r: any) => r.profile === profile && r.scene === scene);
  if (row === undefined) return undefined;
  const component = components[matrix.scenes.find((s: any) => s.id === scene).component];
  return {
    profile, scene, scheme: row.scheme, a11y: row.a11yMode, scale: row.scale,
    span: Math.min(component.size[0], component.size[1]),
    encodedBackdropMean: native.rows.find(
      (r: any) => r.background === matrix.scenes.find((s: any) => s.id === scene).background
        && r.scale === row.scale,
    ).encodedBackdropMean,
    nativeBodyY: row.body.nativeY,
    source: "published G2 matrix (the bundle holds no recovered fixture for this cell)",
  };
};

/**
 * The three numbers a backdrop hands the material, read off the committed raster.
 *
 * They are not interchangeable and the mirror is wrong if they are confused.
 * `luminance` is the ENCODED-space mean DECODED — `backdropToneAnchorX`'s own
 * axis, which the response re-encodes and the adaptation reads as a level;
 * `linearLuminance` and `rgb` are the light the composite actually mixes. For a
 * uniform patch the two coincide to a rounding; for a checkerboard they are
 * 0.2140 and 0.5, and passing the wrong one moves the adaptation from saturated
 * to nothing.
 */
const srgbDecode = (v: number): number =>
  v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const toneCache = new Map<string, { luminance: number; linearLuminance: number; rgb: [number, number, number] }>();
function backdropTone(background: string, scale: number, encodedMean: number): {
  luminance: number; linearLuminance: number; rgb: [number, number, number];
} {
  const key = `${background}@${scale}x`;
  const held = toneCache.get(key);
  if (held !== undefined) return held;
  const png = decodePng(readFileSync(resolve(repo, "apps/reference-apple/fixtures/backgrounds", `${key}.png`)));
  let r = 0, g = 0, b = 0;
  for (let i = 0; i < png.width * png.height; i++) {
    const j = i * 4;
    r += srgbDecode(png.data[j]! / 255);
    g += srgbDecode(png.data[j + 1]! / 255);
    b += srgbDecode(png.data[j + 2]! / 255);
  }
  const n = png.width * png.height;
  const rgb: [number, number, number] = [r / n, g / n, b / n];
  const tone = {
    luminance: srgbDecode(encodedMean),
    linearLuminance: 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2],
    rgb,
  };
  toneCache.set(key, tone);
  return tone;
}

/**
 * The mirror's settled interior level for one cell under one candidate document.
 *
 * `tone.luminance` is the ENCODED-space mean the response's abscissa is measured
 * on and `tone.linearLuminance` is the light the composite actually mixes, which
 * is why both travel: `mid-dark-solid` is 0.2706 on the first axis and 0.0595 on
 * the second, and the two laws read different ones.
 */
function predict(cell: { profile: string; scene: string }, patch: any): number {
  const row = nativeRow(cell.profile, cell.scene);
  if (row === undefined) throw new Error(`${cell.profile}/${cell.scene}: no native row`);
  const scene = matrix.scenes.find((s: any) => s.id === cell.scene);
  const scheme = row.scheme as "light" | "dark";
  const active = scheme === "dark" ? mergeMaterialProfiles(light, dark) : light;
  const profile = mergeMaterialProfiles(active, patch[scheme]);
  const policy = resolveAccessibilityPolicy({
    reducedTransparency: row.a11y !== "standard",
    reducedTransparencySupported: true,
    increasedContrast: row.a11y === "increased-contrast",
    reducedMotion: false,
    forcedColors: false,
  }).material;
  const tone = backdropTone(scene.background, row.scale, row.encodedBackdropMean);
  return materialAtBackdrop(profile, "regular", tone, row.span, policy, row.scale).level;
}

const cellsFor = (ids: string[], profiles: string[]): { profile: string; scene: string }[] =>
  profiles.flatMap((profile) => ids.map((scene) => ({ profile, scene })));

const t1Cells = cellsFor(
  ["light-solid__rrect-sm__inactive", "light-solid__capsule-button__inactive",
   "mid-dark-solid__rrect-sm__inactive", "dark-solid__rrect-sm__inactive",
   "checkerboard__capsule-button__inactive", "photo__capsule-button__inactive",
   "hc-text__rrect-sm__inactive"],
  ["apple-macos-26.5-1x-dark-standard"],
);
const t2Cells = cellsFor(
  ["dark-solid__rrect-48__inactive", "dark-solid__rrect-80__inactive",
   "checkerboard__rrect-md__inactive", "photo__rrect-md__inactive"],
  ["apple-macos-26.5-1x-light-increased-contrast",
   "apple-macos-26.5-1x-light-reduced-transparency"],
);

const out: any = {
  gate: "W27c G1c / claims §5.141",
  kind: "CPU-mirror prediction — the mechanism, not a measurement; nothing is fitted to it",
  mirror: "packages/platform-web/src/optics.ts `materialAtBackdrop`, pinned to the shader by tier-coherence.test.ts",
  rungs: {},
};
/*
 * One counterfactual that is NOT a rung and is never selected on.
 *
 * The refusal T1's ladder measures could be an artefact of the middle knot being
 * frozen at 0.089 where the bed now reads 0.04092 (§5.139 §5 (a), residual (a),
 * arm A3 — declared, unrun and out of this child's scope). If it were, the fit
 * would be blocked by scope rather than by the model, which is a different
 * finding and a different recommendation. So the mirror evaluates the far
 * ordinate at its measured value WITH the middle knot at its measured value too,
 * to say whether releasing the term this child may not touch would rescue the
 * one it may. No GPU rung is added for it and nothing is fitted to it.
 */
const counterfactual = JSON.parse(JSON.stringify(json(resolve(here, "sweeps/t1-far-0.93261.json"))));
counterfactual.dark.backdropToneResponseThin = [0.011, 0.04092, 0.93261];
const rungFiles = readdirSync(resolve(here, "sweeps")).sort();
for (const file of [...rungFiles, "counterfactual"]) {
  const label = file === "counterfactual"
    ? "t1-counterfactual-middle-0.04092-far-0.93261 (NOT A RUNG)"
    : file.replace(/\.json$/, "");
  const patch = file === "counterfactual" ? counterfactual : json(resolve(here, "sweeps", file));
  const cells = label.startsWith("t1") ? t1Cells : t2Cells;
  out.rungs[label] = cells.map((c) => {
    const row = nativeRow(c.profile, c.scene);
    const y = predict(c, patch);
    return {
      cell: `${c.profile}/${c.scene}`,
      span: row.span,
      encodedBackdropMean: row.encodedBackdropMean,
      toneLuminance: backdropTone(
        matrix.scenes.find((s2: any) => s2.id === c.scene).background, row.scale,
        row.encodedBackdropMean).luminance,
      predictedBodyY: y,
      nativeBodyY: row.nativeBodyY,
      signedMiss: y - row.nativeBodyY,
    };
  });
}
writeFileSync(resolve(here, "mirror-predict.json"), `${JSON.stringify(out, null, 2)}\n`);

for (const label of Object.keys(out.rungs)) {
  console.log(`\n${label}`);
  for (const r of out.rungs[label]) {
    console.log(
      `  ${r.cell.replace("apple-macos-26.5-", "").padEnd(58)} span ${String(r.span).padStart(3)} ` +
      `x=${r.encodedBackdropMean.toFixed(4)}  pred ${r.predictedBodyY.toFixed(5)}  ` +
      `native ${r.nativeBodyY.toFixed(5)}  miss ${r.signedMiss >= 0 ? "+" : ""}${r.signedMiss.toFixed(5)}`,
    );
  }
}
