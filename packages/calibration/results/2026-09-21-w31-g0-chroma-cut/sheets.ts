/**
 * W31 G0 — the sheets (acceptance clause 7; claims §5.161 §8).
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/sheets.ts
 *
 * Four panels left to right: **native | WebGPU | CSS | ×8 difference**, at 1x,
 * for the cells the cut reads hardest. The difference panel is the per-pixel
 * OKLab distance between the native fixture and the WEBGPU capture, scaled by 8
 * and written as a neutral grey — the tier this wave fits against, and the
 * amplification the charter names.
 *
 * The web panels come from the SCRATCH capture tree and say so here, in
 * `eye.md` and in the ledger. They are the current generation's pixels and they
 * reproduce the committed rows bit for bit (`reproduction-check.md`), but
 * nothing committed points at them.
 *
 * `eye.md` is written BEFORE any fit exists, which is the point of writing it
 * now: a sheet looked at after a change is a sheet looked at for the change.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { linearRgbToOklab } from "../../src/color";
import { createImage, decodePng, toLinearRgb, type CalibrationImage } from "../../src/image";
import { encodePng } from "../../test/synthesise";

const HERE = import.meta.dirname;
const PACKAGE = resolve(HERE, "..", "..");
const FIXTURES = resolve(PACKAGE, "..", "..", "apps", "reference-apple", "fixtures");
const SCRATCH = process.env["VITREA_WEB_CAPTURES"] ?? "/tmp/w31-g0-captures";

const DIFFERENCE_GAIN = 8;
const GUTTER = 6;

/**
 * The cells, at 1x in both schemes.
 *
 * `mid-chroma-solid__capsule-button__rest` is the charter's third cell and it
 * exists on the LIGHT macOS 27 profile only: the dark 27 bed carries four
 * `mid-chroma-solid` fixtures and every one of them is `__inactive`. The dark
 * sheet is therefore the inactive pose of the same component — the receded
 * material over the same saturated solid — and the substitution is named here
 * rather than left to be noticed.
 */
const SHEETS = [
  ["apple-macos-27.0-1x-light-standard-glass0.5", "photo__rrect-md__rest"],
  ["apple-macos-27.0-1x-dark-standard-glass0.5", "photo__rrect-md__rest"],
  ["apple-macos-27.0-1x-light-standard-glass0.5", "photo__rrect-lg__rest"],
  ["apple-macos-27.0-1x-dark-standard-glass0.5", "photo__rrect-lg__rest"],
  ["apple-macos-27.0-1x-light-standard-glass0.5", "mid-chroma-solid__capsule-button__rest"],
  ["apple-macos-27.0-1x-dark-standard-glass0.5", "mid-chroma-solid__capsule-button__inactive"],
] as const;

const load = (path: string): CalibrationImage => decodePng(readFileSync(path));

function differencePanel(native: CalibrationImage, web: CalibrationImage): CalibrationImage {
  const a = toLinearRgb(native);
  const b = toLinearRgb(web);
  const data = new Uint8Array(native.width * native.height * 4);
  for (let i = 0; i < native.width * native.height; i += 1) {
    const x = linearRgbToOklab(a[i * 3] ?? 0, a[i * 3 + 1] ?? 0, a[i * 3 + 2] ?? 0);
    const y = linearRgbToOklab(b[i * 3] ?? 0, b[i * 3 + 1] ?? 0, b[i * 3 + 2] ?? 0);
    const deltaE = Math.hypot(x.L - y.L, x.a - y.a, x.b - y.b);
    const byte = Math.min(255, Math.round(deltaE * DIFFERENCE_GAIN * 255));
    data[i * 4] = byte;
    data[i * 4 + 1] = byte;
    data[i * 4 + 2] = byte;
    data[i * 4 + 3] = 255;
  }
  return createImage(native.width, native.height, data);
}

function strip(panels: readonly CalibrationImage[]): CalibrationImage {
  const height = Math.max(...panels.map((p) => p.height));
  const width = panels.reduce((sum, p) => sum + p.width, 0) + GUTTER * (panels.length - 1);
  const data = new Uint8Array(width * height * 4).fill(0);
  for (let i = 3; i < data.length; i += 4) data[i] = 255;
  let x0 = 0;
  for (const panel of panels) {
    for (let y = 0; y < panel.height; y += 1) {
      for (let x = 0; x < panel.width; x += 1) {
        const from = (y * panel.width + x) * 4;
        const to = (y * width + x0 + x) * 4;
        data[to] = panel.data[from] ?? 0;
        data[to + 1] = panel.data[from + 1] ?? 0;
        data[to + 2] = panel.data[from + 2] ?? 0;
        data[to + 3] = 255;
      }
    }
    x0 += panel.width + GUTTER;
  }
  return createImage(width, height, data);
}

const written: string[] = [];
for (const [profileKey, scene] of SHEETS) {
  const nativePath = resolve(FIXTURES, profileKey, `${scene}.png`);
  const cellDir = resolve(SCRATCH, profileKey, scene);
  if (!readdirSync(resolve(FIXTURES, profileKey)).includes(`${scene}.png`)) {
    console.log(`SKIPPED ${profileKey} / ${scene}: no native fixture`);
    continue;
  }
  let files: string[];
  try {
    files = readdirSync(cellDir);
  } catch {
    console.log(`SKIPPED ${profileKey} / ${scene}: no scratch capture at ${cellDir}`);
    continue;
  }
  const webgpu = files.find((f) => f === `${scene}__webgpu.png`);
  const css = files.find((f) => f === `${scene}__css.png`);
  if (webgpu === undefined || css === undefined) {
    console.log(`SKIPPED ${profileKey} / ${scene}: tiers on disk are ${files.join(", ")}`);
    continue;
  }

  const native = load(nativePath);
  const gpu = load(resolve(cellDir, webgpu));
  const dom = load(resolve(cellDir, css));
  const sheet = strip([native, gpu, dom, differencePanel(native, gpu)]);
  const out = resolve(HERE, `sheet__${profileKey}__${scene}.png`);
  writeFileSync(out, encodePng(sheet));
  written.push(`sheet__${profileKey}__${scene}.png`);
  console.log(`wrote ${out.split("/").pop() ?? ""}  (${sheet.width}x${sheet.height})`);
}

console.log(`\n${written.length} sheet(s). Panels, left to right: native | WebGPU | CSS | OKLab ΔE × ${DIFFERENCE_GAIN} (native against WebGPU).`);
