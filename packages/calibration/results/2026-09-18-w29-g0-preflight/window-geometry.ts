/**
 * G0 (e) — does macOS 27's window geometry reach into the capture region?
 *
 *   tsx results/2026-09-18-w29-g0-preflight/window-geometry.ts \
 *     --root <fixture-root> [--backgrounds <dir>] [--out geometry.json]
 *
 * The charter asks whether the tighter window corner or the changed shadow enters
 * a scene's capture region. The region is decided in `Sources/Capture.swift`: the
 * window is borderless and sized exactly to the canvas, `hasShadow` is false, the
 * filter is `SCContentFilter(desktopIndependentWindow:)` with
 * `ignoreShadowsSingleWindow = true`, and the configuration's width and height are
 * the canvas's pixel size with `scalesToFit = false`. So the capture is the
 * window's own rectangle and nothing outside it — *if* the window server still
 * hands back a full rectangle on this OS.
 *
 * Both failure modes are visible against one reference, and the reference is the
 * background raster the harness composited into that same window: a rounded window
 * corner removes or darkens pixels the raster has, and a shadow that leaked into
 * the region darkens the outer ring. So per scene this reports, over rings of
 * increasing depth from the edge:
 *
 * - the four corner pixels of the capture and of the raster, channel by channel;
 * - the worst |delta| and the count of pixels differing by more than 2 (the noise
 *   the harness's own repeat-capture check tolerates), per ring depth 1…8;
 * - the minimum alpha on the outer ring, because a window clipped to a rounded
 *   rectangle composites its corners transparent rather than dark.
 *
 * A difference here is only geometry if the component does not itself reach the
 * ring. The scenes this is run on are chosen so it does not: the largest component
 * in the declaration is `rrect-lg` at 280x160 on a 320x200 canvas, centred, so 20
 * points of raster clear it on every side — which is also why `rrect-lg` is the
 * right scene to ask with, since its shadow is the closest any scene's is to the
 * edge.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { decodePng, type CalibrationImage } from "../../src/index";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");

const arg = (name: string, fallback?: string): string => {
  const index = process.argv.indexOf(`--${name}`);
  const value = index < 0 ? fallback : process.argv[index + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};

const root = resolve(arg("root"));
const backgroundsDir = resolve(arg("backgrounds", join(root, "backgrounds")));
const outPath = arg("out", join(here, "geometry.json"));

const declaration = JSON.parse(
  readFileSync(resolve(repo, "apps/reference-apple/scenes.json"), "utf8"),
) as { readonly scenes: readonly { readonly id: string; readonly background: string }[] };
const backgroundOf = new Map(declaration.scenes.map((s) => [s.id, s.background]));

const px = (image: CalibrationImage, x: number, y: number): number[] => {
  const i = (y * image.width + x) * 4;
  return [image.data[i], image.data[i + 1], image.data[i + 2], image.data[i + 3]];
};

/** Pixels within `depth` of any edge. */
const ring = (image: CalibrationImage, depth: number): number[] => {
  const out: number[] = [];
  for (let y = 0; y < image.height; y += 1) {
    for (let x = 0; x < image.width; x += 1) {
      if (x < depth || y < depth || x >= image.width - depth || y >= image.height - depth) {
        out.push((y * image.width + x) * 4);
      }
    }
  }
  return out;
};

const rows: unknown[] = [];
for (const profile of readdirSync(root, { withFileTypes: true })) {
  if (!profile.isDirectory() || profile.name === "backgrounds") continue;
  const scale = profile.name.includes("-2x-") ? 2 : 1;
  for (const file of readdirSync(join(root, profile.name))) {
    if (!file.endsWith(".png")) continue;
    const scene = file.slice(0, -4);
    const background = backgroundOf.get(scene);
    if (!background) continue;
    const capture = decodePng(readFileSync(join(root, profile.name, file)));
    const rasterPath = join(backgroundsDir, `${background}@${scale}x.png`);
    const raster = decodePng(readFileSync(rasterPath));
    if (raster.width !== capture.width || raster.height !== capture.height) {
      rows.push({ cell: `${profile.name}/${scene}`, error: "size mismatch" });
      continue;
    }

    const depths: Record<string, { worst: number; over2: number; minAlpha: number }> = {};
    for (let depth = 1; depth <= 8; depth += 1) {
      let worst = 0;
      let over2 = 0;
      let minAlpha = 255;
      for (const i of ring(capture, depth)) {
        let cellMax = 0;
        for (let c = 0; c < 3; c += 1) {
          const d = Math.abs(capture.data[i + c] - raster.data[i + c]);
          if (d > cellMax) cellMax = d;
        }
        if (cellMax > worst) worst = cellMax;
        if (cellMax > 2) over2 += 1;
        if (capture.data[i + 3] < minAlpha) minAlpha = capture.data[i + 3];
      }
      depths[String(depth)] = { worst, over2, minAlpha };
    }

    const corners = {
      topLeft: { capture: px(capture, 0, 0), raster: px(raster, 0, 0) },
      topRight: { capture: px(capture, capture.width - 1, 0), raster: px(raster, raster.width - 1, 0) },
      bottomLeft: { capture: px(capture, 0, capture.height - 1), raster: px(raster, 0, raster.height - 1) },
      bottomRight: {
        capture: px(capture, capture.width - 1, capture.height - 1),
        raster: px(raster, raster.width - 1, raster.height - 1),
      },
    };
    rows.push({ cell: `${profile.name}/${scene}`, background, corners, rings: depths });
    console.log(
      `${profile.name}/${scene}: ring1 worst=${depths["1"].worst} over2=${depths["1"].over2} ` +
        `minAlpha=${depths["1"].minAlpha}  ring8 worst=${depths["8"].worst} over2=${depths["8"].over2}` +
        `  corners ${JSON.stringify(corners.topLeft.capture)} vs raster ${JSON.stringify(corners.topLeft.raster)}`,
    );
  }
}

writeFileSync(outPath, `${JSON.stringify({ root, backgroundsDir, cells: rows }, null, 2)}\n`);
console.log(`→ ${outPath}`);
