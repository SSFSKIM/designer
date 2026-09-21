/**
 * W31 G0 — what the shader actually does at the photo cells (claims §5.161 §5).
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/mechanism.ts
 *
 * The charter's clause 2 asks G0 to state, from `optics.ts` and `material.ts`,
 * which of the two collapses the light and dark documents exercise at the photo
 * cells' levels, and whether `(1 − toneAdapt)` is the gate for a chroma
 * retention or whether none is needed. Those are arithmetic questions about
 * shipped constants and measured backdrops, so they are answered here by
 * evaluating the material's own exported functions rather than by reading the
 * WGSL and reasoning about it.
 *
 * Three quantities per cell:
 *
 *   `toneAdapt`  — `backdropToneAdaptation(level, sizeK)`, the backdrop tone
 *                  collapse, which acts on EVERY body. `1 − toneAdapt` is the
 *                  candidate gate.
 *   `sizeK`      — `sizeThickness(span)`, the size law's thickness.
 *   `sizedAlpha` — `tintAlpha + sizeOcclusionGain · sizeK · (1 − tintAlpha)`,
 *                  the plate's alpha before the tone solve moves it. This is
 *                  the factor that scales the backdrop's chromaticity in the
 *                  composite `mix(backdrop, adapted, presentAlpha)`, and it is
 *                  where the chroma is lost.
 */
import {
  DEFAULT_MATERIAL_PROFILE,
  backdropToneAdaptation,
  sizeThickness,
  withMaterialOverrides,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const PROFILES = resolve(import.meta.dirname, "..", "..", "profiles");
const read = (name: string): MaterialProfilePatch =>
  (JSON.parse(readFileSync(resolve(PROFILES, `${name}.json`), "utf8")) as { patch: MaterialProfilePatch })
    .patch;

const light = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read("apple-macos-27.0-1x-light-standard-glass0.5"));
const dark = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read("apple-macos-27.0-1x-dark-standard-glass0.5"));
const lightReceded = withMaterialOverrides(light, read("apple-macos-27.0-1x-light-standard-glass0.5-receded"));
const darkReceded = withMaterialOverrides(dark, read("apple-macos-27.0-1x-dark-standard-glass0.5-receded"));
const frozenLight = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read("apple-macos-26.5-1x-light-standard"));
const frozenDark = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read("apple-macos-26.5-1x-dark-standard"));

/**
 * The photo cells' measured backdrop levels, off the committed macOS 27 rows,
 * and their declared spans off `scenes.json`.
 */
const CELLS = [
  ["photo__capsule-button__rest", 44, 0.2212, 0.23307],
  ["photo__rrect-md__rest", 96, 0.2212, 0.23307],
  ["photo__rrect-ml__rest", 128, 0.2212, 0.23307],
  ["photo__rrect-lg__rest", 160, 0.2212, 0.23307],
] as const;

function row(profile: MaterialProfile, span: number, level: number): string {
  const k = sizeThickness(span, profile);
  const toneAdapt = backdropToneAdaptation(level, k, profile);
  const alpha = profile.optics.regular.tintAlpha;
  const sizedAlpha = alpha + profile.sizeOcclusionGain * k * (1 - alpha);
  return [
    `sizeK ${k.toFixed(4)}`,
    `tintAlpha ${alpha.toFixed(4)}`,
    `sizedAlpha ${sizedAlpha.toFixed(4)}`,
    `1−sizedAlpha ${(1 - sizedAlpha).toFixed(4)}`,
    `toneAdapt ${toneAdapt.toFixed(6)}`,
  ].join("  ");
}

console.log("== the composite's two factors at the photo cells, macOS 27 ==\n");
for (const [scheme, profile, levelIndex] of [
  ["light active  ", light, 2],
  ["light receded ", lightReceded, 2],
  ["dark  active  ", dark, 3],
  ["dark  receded ", darkReceded, 3],
] as const) {
  console.log(scheme);
  for (const cell of CELLS) {
    console.log(`  span ${String(cell[1]).padStart(3)}  ${cell[0].padEnd(30)} ${row(profile, cell[1], cell[levelIndex])}`);
  }
  console.log("");
}

console.log("== the gate question ==\n");
console.log("  backdropToneLow / backdropToneHigh / backdropToneMax, per document:");
for (const [name, profile] of [
  ["macOS 27 light ", light],
  ["macOS 27 dark  ", dark],
  ["macOS 26.5 light", frozenLight],
  ["macOS 26.5 dark ", frozenDark],
] as const) {
  console.log(
    `    ${name}  low ${profile.backdropToneLow}  high ${profile.backdropToneHigh}  max ${profile.backdropToneMax}  sizeBias ${profile.backdropToneSizeBias}`,
  );
}
console.log(`
  The macOS 27 documents set the collapse's band to [0, 0.0001]. The smoothstep
  argument is (level + sizeBias·sizeK − low) / (high − low), so ANY backdrop at
  or above 0.0001 of linear light saturates it at 1 and 'toneAdapt' is exactly
  0. The photo backdrop sits at 0.221 / 0.233. The collapse is therefore OFF at
  every photo cell of both macOS 27 documents — not small, zero — and it is off
  at every cell of the macOS 27 bed whose backdrop is not essentially black.
`);
console.log("  toneAdapt over the whole backdrop range, macOS 27 dark, span 96:");
for (const level of [0, 0.00005, 0.0001, 0.001, 0.01, 0.05, 0.1223, 0.2331, 0.5, 0.9]) {
  console.log(
    `    level ${String(level).padEnd(8)} toneAdapt ${backdropToneAdaptation(level, sizeThickness(96, dark), dark).toFixed(8)}`,
  );
}
console.log(`
  The same curve on the FROZEN macOS 26.5 dark document, for contrast — that
  material does adapt, over [0.02, 0.055]:`);
for (const level of [0.0, 0.01, 0.02, 0.0375, 0.055, 0.1223, 0.2331]) {
  console.log(
    `    level ${String(level).padEnd(8)} toneAdapt ${backdropToneAdaptation(level, sizeThickness(96, frozenDark), frozenDark).toFixed(8)}`,
  );
}
