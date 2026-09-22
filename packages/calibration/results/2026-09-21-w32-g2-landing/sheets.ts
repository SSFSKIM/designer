/**
 * W32 G2 — the landing's sheets, from the CANONICAL capture tree (claims §5.169 §5).
 *
 *   npx tsx results/2026-09-21-w32-g2-landing/sheets.ts
 *
 * W31 G4's `sheets.ts` by way of W32 G1's, copied on `results/`'s own convention
 * — nothing under it is edited after commit — with its BED changed and one panel
 * of arithmetic added. The per-cell document-bytes assertion, the layout, the
 * ΔE × 8 difference panel and the refusal are W31 G4's, byte for byte, and they
 * are the reason that file was the one copied: a sheet that photographed a cell
 * drawn at documents other than the shipped ones would look right and would be
 * of a material nobody shipped.
 *
 * **The tree is the canonical `packages/calibration/web-captures/`** and not a
 * scratch one. G1's read wrote its tree, the parent copied it to the canonical
 * path at G1's merge — which is what `CLAUDE.md` says a merge that lands a read
 * has to do — so these panels are the pixels the committed rows beside them were
 * measured off. `VITREA_WEB_CAPTURES` still overrides, for a reader on another
 * machine.
 *
 * **The bed is the landing's**: `capsule-button` (span 44), `rrect-ml` (128) and
 * `rrect-lg` (160), in BOTH poses, on all four macOS 27 standard profiles — both
 * schemes at both scales, sixteen of the twenty-four cells on `photo` and the
 * rest on the ladder's `checkerboard-8` where a profile does not declare the
 * `photo` cell. Which backdrop a cell gets is read off the tree in a stated
 * preference order and NAMED, because a bed that silently substituted one
 * backdrop for another would make two profiles' sheets look comparable when they
 * are not (W32 G1's review closure, on `eye.md`'s own version of this).
 *
 * **The one-byte check beside every difference panel** (§5.168 §10, finding B-4).
 * A ΔE × 8 OKLab panel renders the distance from sRGB byte 0 to byte 1 as a
 * mid-grey, because OKLab takes a cube root of linear light and its derivative
 * diverges at zero — so the panel cannot distinguish "vitrea is one byte above
 * Apple's black" from a real residual, and W32 G1's `eye.md` read the wrong
 * verdict off exactly that. Every sheet therefore prints, over the EXTERIOR (the
 * canvas minus the component's declared rect, the construction `b4-black-floor.py`
 * uses), how many pixels Apple renders as exactly (0,0,0), how many of those
 * vitrea renders as exactly (1,1,1), how many above one byte, and the worst
 * channel difference among them. A sheet whose grey is the floor says so in
 * numbers under the picture.
 */

import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
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

/**
 * The landing's bed: three components, both poses, four standard profiles.
 *
 * `photo` first everywhere, because it is the backdrop every profile declares
 * most of and the one the eye reads a body over; the ladder's `checkerboard-8`
 * where a profile declares no `photo` cell for that component and pose, which is
 * a fact about `scenes.json`'s per-profile declarations and not a choice made
 * here. The chosen backdrop is printed beside every sheet.
 */
const BED = [
  { component: "capsule-button", span: 44, pose: "rest",
    scenes: ["photo__capsule-button__rest", "checkerboard-8__capsule-button__rest"] },
  { component: "capsule-button", span: 44, pose: "inactive",
    scenes: ["photo__capsule-button__inactive", "checkerboard__capsule-button__inactive"] },
  { component: "rrect-ml", span: 128, pose: "rest",
    scenes: ["photo__rrect-ml__rest", "checkerboard-8__rrect-ml__rest"] },
  { component: "rrect-ml", span: 128, pose: "inactive",
    scenes: ["photo__rrect-ml__inactive", "checkerboard__rrect-ml__inactive"] },
  { component: "rrect-lg", span: 160, pose: "rest",
    scenes: ["photo__rrect-lg__rest", "checkerboard-8__rrect-lg__rest"] },
  { component: "rrect-lg", span: 160, pose: "inactive",
    scenes: ["photo__rrect-lg__inactive", "checkerboard-8__rrect-lg__inactive"] },
] as const;

/** `scenes.json`'s canvas and component sizes — the exterior's own construction. */
const SCENES = JSON.parse(
  readFileSync(resolve(PACKAGE, "..", "..", "apps", "reference-apple", "scenes.json"), "utf8"),
) as {
  canvas: { width: number; height: number };
  components: Record<string, { size: readonly number[] }>;
};

/**
 * The black floor's own bed, on the profile it was measured on (§5.168 §10, B-4).
 *
 * `photo` has no native-black exterior pixel anywhere — every sheet above says so
 * in as many words — so the floor is invisible on the bed the rest of this file
 * photographs, and the cell that made it a finding is a `checkerboard-8` rung.
 * These three are B-4's own spans on 1x light: 160 and 128, where it measured
 * 3,334 of 9,440 and 2,188 of 17,532 pixels lifted, and **44, which is below
 * `liftSpanMin` 64 and read 0 of 29,330** — the control that makes the reading a
 * statement about `liftAmplitude` rather than about the renderer's black.
 */
const BLACK_FLOOR_BED = [
  { component: "capsule-button", scene: "checkerboard-8__capsule-button__rest" },
  { component: "rrect-ml", scene: "checkerboard-8__rrect-ml__rest" },
  { component: "rrect-lg", scene: "checkerboard-8__rrect-lg__rest" },
] as const;

const BLACK_FLOOR_PROFILE = "apple-macos-27.0-1x-light-standard-glass0.5";

const ACCESSIBILITY = [
  "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
  "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
] as const;

const ACCESSIBILITY_SCENES = ["photo__capsule-button__rest", "photo__capsule-button__inactive"] as const;


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

/**
 * The one-byte check the difference panel cannot make (§5.168 §10, finding B-4).
 *
 * Over the EXTERIOR — the canvas minus the component's declared rect, scaled by
 * the capture's own pixel size, which is `b4-black-floor.py`'s construction —
 * count the pixels Apple renders as exactly (0, 0, 0), and split what vitrea
 * renders there into "exactly one byte up", "more than one byte up" and the
 * worst channel difference. A ΔE × 8 OKLab panel draws one byte at black as a
 * mid-grey, so a panel that looks like a residual over black squares may be
 * this; the numbers under the picture are what tells the two apart.
 */
function blackFloor(
  component: string,
  native: CalibrationImage,
  web: CalibrationImage,
): string {
  const size = SCENES.components[component]?.size ?? [0, 0];
  const scale = native.width / SCENES.canvas.width;
  const x0 = ((SCENES.canvas.width - (size[0] ?? 0)) / 2) * scale;
  const y0 = ((SCENES.canvas.height - (size[1] ?? 0)) / 2) * scale;
  const x1 = x0 + (size[0] ?? 0) * scale;
  const y1 = y0 + (size[1] ?? 0) * scale;
  let black = 0;
  let one = 0;
  let above = 0;
  let worst = 0;
  for (let y = 0; y < native.height; y += 1) {
    for (let x = 0; x < native.width; x += 1) {
      if (y >= y0 && y < y1 && x >= x0 && x < x1) continue;
      const i = (y * native.width + x) * 4;
      if ((native.data[i] ?? 0) !== 0 || (native.data[i + 1] ?? 0) !== 0
          || (native.data[i + 2] ?? 0) !== 0) continue;
      black += 1;
      const top = Math.max(web.data[i] ?? 0, web.data[i + 1] ?? 0, web.data[i + 2] ?? 0);
      if (top === 1) one += 1;
      else if (top > 1) above += 1;
      worst = Math.max(worst, top);
    }
  }
  return black === 0
    ? "no native-black exterior pixel on this bed"
    : `black exterior ${black}: web at exactly 1 on ${one}, above 1 on ${above}, worst byte ${worst}`;
}

function sheet(
  profileKey: string,
  component: string,
  scene: string,
  tiers: "both" | "webgpu",
): string {
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
    `${profileKey} / ${scene}\n  ${layout}  ${image.width}x${image.height}\n`
      + `  at ${documents.join(" + ")}\n  ${blackFloor(component, native, gpu)}`,
  );
  return out;
}


const written: string[] = [];
console.log(`captures: ${CAPTURES}\n`);
/*
 * Which tiers a cell can be photographed at is a property of the READ and not a
 * choice made here, so it is read off the tree rather than tabled: the canonical
 * read takes both tiers on the calibration, validation and holdout sets of every
 * profile and the CSS tier of the ladder's probe scenes on the two 1x standard
 * profiles alone. A cell a profile does not declare has no capture at all and is
 * NAMED rather than skipped quietly — the dark documents declare no `photo`
 * `rrect-ml` and no holdout `checkerboard__rrect-lg`, which is a fact about
 * `scenes.json` and is what a reader of the sheets needs to know when a bed is
 * missing a panel.
 */
const has = (profileKey: string, scene: string, tier: "webgpu" | "css"): boolean =>
  existsSync(resolve(CAPTURES, profileKey, scene, `cell__${tier}.json`));

console.log("== the landing's bed: three spans, both poses, both schemes, both scales ==\n");
for (const profileKey of STANDARD_PROFILES) {
  for (const entry of BED) {
    const scene = entry.scenes.find((candidate) => has(profileKey, candidate, "webgpu"));
    if (scene === undefined) {
      console.log(
        `${profileKey} / ${entry.component} ${entry.pose}\n`
          + `  no capture in the read for any of ${entry.scenes.join(", ")}`,
      );
      continue;
    }
    if (scene !== entry.scenes[0]) {
      console.log(`  (${profileKey} declares no ${entry.scenes[0]}; the ladder's rung is used)`);
    }
    written.push(
      sheet(profileKey, entry.component, scene, has(profileKey, scene, "css") ? "both" : "webgpu"),
    );
  }
}
console.log("\n== the black floor's own bed: B-4's three spans on the profile it was read on ==\n");
for (const entry of BLACK_FLOOR_BED) {
  if (!has(BLACK_FLOOR_PROFILE, entry.scene, "webgpu")) {
    console.log(`${BLACK_FLOOR_PROFILE} / ${entry.scene}\n  no capture in the read`);
    continue;
  }
  written.push(
    sheet(
      BLACK_FLOOR_PROFILE,
      entry.component,
      entry.scene,
      has(BLACK_FLOOR_PROFILE, entry.scene, "css") ? "both" : "webgpu",
    ),
  );
}

console.log("\n== the accessibility band: the thin caster, where the thin stop's worst cell lives ==\n");
for (const profileKey of ACCESSIBILITY) {
  for (const scene of ACCESSIBILITY_SCENES) {
    written.push(sheet(profileKey, "capsule-button", scene, "webgpu"));
  }
}
console.log(
  `\n${written.length} sheet(s).`
    + `\nNOT here: the span-32 rrect-sm band and the chroma bed, which this wave does not move.`
    + `\nW31 G4's sheets of both are committed at results/2026-09-21-w31-g4-landing/.`,
);
