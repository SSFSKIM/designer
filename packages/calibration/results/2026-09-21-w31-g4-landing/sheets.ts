/**
 * W31 G4 — the landing's sheets, from the CANONICAL capture tree (claims §5.165 §2).
 *
 *   VITREA_WEB_CAPTURES=<the capture machine's canonical tree> \
 *     npx tsx results/2026-09-21-w31-g4-landing/sheets.ts
 *
 * W31 G3's `sheets.ts` (`results/2026-09-21-w31-g3-chroma-fit/sheets.ts`), copied
 * rather than reused on that directory's own convention, with three changes.
 *
 * **The tree.** G3's web panels came from the tree its own read wrote, inside its
 * worktree. That tree is now the canonical `packages/calibration/web-captures/`
 * on the capture machine — the parent copied it at G3c's merge, which is the
 * first time since W29 that the canonical tree and the committed rows have been
 * the same generation (charter Surprises; tracker at this gate). So the panels
 * here are the pixels the committed rows beside them were measured off, read from
 * the tree `CLAUDE.md` says they are read from, and **the claim is checked rather
 * than assumed**: every cell's `cell__webgpu.json` has to name the SHIPPED
 * document bytes, and a cell whose capture names anything else is refused loudly
 * instead of photographed quietly.
 *
 * **The bed.** Three untinted `photo` components — `capsule-button` (span 44),
 * `rrect-md` (span 96) and `rrect-lg` (span 160) — on all four macOS 27 standard
 * profiles, so both schemes at both scales, which is what the acceptance clause
 * asks for and what makes the span story visible: the retention is one constant
 * per document and the span is the axis it does not condition on.
 *
 * **The accessibility band.** Four sheets of `photo__rrect-md` in both poses on
 * the two accessibility profiles, three panels instead of four (native | WebGPU |
 * ΔE × 8) because the question there is not a tier comparison. W31 Decision Log
 * 3 (c) rules that the regression the review found is FIXED by G3c's hard gate
 * and the numbers say so at the digit and at the byte; these sheets are the other
 * half of that, because a stand-down that restores 0.20.0's rendering exactly
 * should look like 0.20.0 and the metrics are not the whole verdict.
 *
 * **What is NOT here, named rather than left to be noticed.** `mid-chroma-solid`
 * is a PROBE scene. The canonical read is calibration + validation + the pitch
 * ladder (claims §5.164 §7), so the canonical tree carries no macOS 27
 * `mid-chroma-solid` capture at all, and X1 allows this gate no calibration
 * capture. G0's pre-fit sheets of it are committed at
 * `results/2026-09-21-w31-g0-chroma-cut/sheet__*__mid-chroma-solid__*.png` and
 * G0's hue-ROTATION finding on them stands open exactly as claims §5.164 §9
 * leaves it. `eye.md` carries the consequence.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve } from "node:path";

import { linearRgbToOklab } from "../../src/color";
import { createImage, decodePng, toLinearRgb, type CalibrationImage } from "../../src/image";
import { encodePng } from "../../test/synthesise";

const HERE = import.meta.dirname;
const PACKAGE = resolve(HERE, "..", "..");
const FIXTURES = resolve(PACKAGE, "..", "..", "apps", "reference-apple", "fixtures");
const CAPTURES = process.env["VITREA_WEB_CAPTURES"] ?? resolve(PACKAGE, "web-captures");

const DIFFERENCE_GAIN = 8;
const GUTTER = 6;

const STANDARD_PROFILES = [
  "apple-macos-27.0-1x-light-standard-glass0.5",
  "apple-macos-27.0-2x-light-standard-glass0.5",
  "apple-macos-27.0-1x-dark-standard-glass0.5",
  "apple-macos-27.0-2x-dark-standard-glass0.5",
] as const;

const STANDARD_SCENES = [
  "photo__capsule-button__rest",
  "photo__rrect-md__rest",
  "photo__rrect-lg__rest",
] as const;

const ACCESSIBILITY = [
  "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
] as const;

const ACCESSIBILITY_SCENES = ["photo__rrect-md__rest", "photo__rrect-md__inactive"] as const;

/**
 * The overshoot band: `photo__rrect-sm`, span 32 — the thinnest surface the bed
 * carries, and the three cells M1's per-cell ceiling declares MISSED at adoption
 * (claims §5.165 §1). The fourth, 1x light `__rest` at `R` 1.3567, is here
 * because a sheet of three failures and no near-miss beside them cannot show
 * what 1.40 is separating.
 *
 * The eye's question is specific and is not the one the other bands ask: an
 * over-restored body is not a body with a defect in it, it is a body with MORE
 * of the backdrop's colour than the reference has. If 1.45 and 1.36 look alike,
 * the ceiling is a statistic and not a picture — which is worth knowing either
 * way and is recorded as it reads.
 */
const OVERSHOOT = [
  ["apple-macos-27.0-1x-light-standard-glass0.5", "photo__rrect-sm__inactive"],
  ["apple-macos-27.0-2x-light-standard-glass0.5", "photo__rrect-sm__inactive"],
  ["apple-macos-27.0-2x-light-standard-glass0.5", "photo__rrect-sm__rest"],
  ["apple-macos-27.0-1x-light-standard-glass0.5", "photo__rrect-sm__rest"],
] as const;

/** The shipped documents' twelve-hex content hashes, derived and never typed. */
const SHIPPED = new Map(
  readdirSync(resolve(PACKAGE, "profiles"))
    .filter((file) => file.endsWith(".json"))
    .map(
      (file) =>
        [
          `packages/calibration/profiles/${file}`,
          createHash("sha256")
            .update(readFileSync(resolve(PACKAGE, "profiles", file)))
            .digest("hex")
            .slice(0, 12),
        ] as const,
    ),
);

/**
 * Which documents a cell's capture names, and whether every one of them is the
 * shipped bytes. The receded document is checked too: it is what an `__inactive`
 * panel actually drew.
 */
function documentsOf(cellDir: string, tier: "webgpu" | "css"): readonly string[] {
  const meta = JSON.parse(readFileSync(resolve(cellDir, `cell__${tier}.json`), "utf8")) as {
    capturePath: string;
  };
  const named = [
    ...meta.capturePath.matchAll(/(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g),
  ];
  const stale = named.filter((match) => SHIPPED.get(match[1] ?? "") !== match[2]);
  if (named.length === 0 || stale.length > 0) {
    throw new Error(
      `${cellDir}: the capture names ${named.length === 0 ? "no document" : "a document that is not shipped"}`
        + ` — ${named.map((match) => `${(match[1] ?? "").split("/").pop() ?? ""} ${match[2] ?? ""}`).join(", ")}`,
    );
  }
  return named.map((match) => `${(match[1] ?? "").split("/").pop() ?? ""} ${match[2] ?? ""}`);
}

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
  const height = Math.max(...panels.map((panel) => panel.height));
  const width = panels.reduce((sum, panel) => sum + panel.width, 0) + GUTTER * (panels.length - 1);
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

function sheet(profileKey: string, scene: string, tiers: "both" | "webgpu"): string {
  const nativePath = resolve(FIXTURES, profileKey, `${scene}.png`);
  const cellDir = resolve(CAPTURES, profileKey, scene);
  const documents = documentsOf(cellDir, "webgpu");
  const native = load(nativePath);
  const gpu = load(resolve(cellDir, `${scene}__webgpu.png`));
  const panels =
    tiers === "both"
      ? [native, gpu, load(resolve(cellDir, `${scene}__css.png`)), differencePanel(native, gpu)]
      : [native, gpu, differencePanel(native, gpu)];
  if (tiers === "both") documentsOf(cellDir, "css");
  const out = resolve(HERE, `sheet__${profileKey}__${scene}.png`);
  const image = strip(panels);
  writeFileSync(out, encodePng(image));
  const layout = tiers === "both" ? "native | WebGPU | CSS | dE x8" : "native | WebGPU | dE x8";
  console.log(
    `${profileKey} / ${scene}\n  ${layout}  ${image.width}x${image.height}\n  at ${documents.join(" + ")}`,
  );
  return out;
}


const written: string[] = [];
console.log(`captures: ${CAPTURES}\n`);
console.log("== the standard bed: three spans, both schemes, both scales ==\n");
for (const profileKey of STANDARD_PROFILES) {
  for (const scene of STANDARD_SCENES) written.push(sheet(profileKey, scene, "both"));
}
console.log("\n== the overshoot band: span 32, the three M1 declares missed and the one it does not ==\n");
for (const [profileKey, scene] of OVERSHOOT) written.push(sheet(profileKey, scene, "both"));
console.log("\n== the accessibility band (W31 Decision Log 3 (c)) ==\n");
for (const profileKey of ACCESSIBILITY) {
  for (const scene of ACCESSIBILITY_SCENES) written.push(sheet(profileKey, scene, "webgpu"));
}
console.log(
  `\n${written.length} sheet(s).`
    + `\nNOT here: mid-chroma-solid is a probe scene and the canonical read does not carry it,`
    + `\nso the canonical tree has no macOS 27 capture of it and X1 allows this gate none.`
    + `\nG0's pre-fit sheets of it are at results/2026-09-21-w31-g0-chroma-cut/ and its hue-rotation`
    + `\nfinding stands open exactly as claims §5.164 §9 leaves it.`,
);
