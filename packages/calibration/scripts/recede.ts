/**
 * W27c G0 / claims §5.128: read the two DL14 trees, never the mutable fixture bed.
 * Run with `PYTHON=/path/to/python pnpm --filter @vitrea/calibration exec tsx scripts/recede.ts`.
 * Python needs numpy and Pillow, as does the unchanged W23 contour instrument imported below.
 * No fit, capture, or runtime material is changed. Output files are create-only evidence.
 * Set W27C_OUT to a scratch output prefix to reproduce without replacing the recorded table.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { componentRegion, type DeclaredComponent, type CanvasSize } from "../src/component-region";
import { oklabChroma, srgbByteToOklab } from "../src/color";
import { assertComparable, decodePng, encodedLuma, type CalibrationImage } from "../src/image";
import { interiorLevel, tintResponse } from "../src/metrics/material";
import type { Silhouette } from "../src/silhouette";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const FIXTURES = "apps/reference-apple/fixtures";
const ACTIVE = "973fd7e";
const INACTIVE = `${ACTIVE}^`;
const CONTOUR = "packages/calibration/results/2026-09-08-w23-collapsed-rim/g3/read-contour.py";
const OUT = "packages/calibration/results/2026-09-10-w27c-g0-recede";
interface Scene {
  id: string;
  background: string;
  component: string;
  state: string;
  tint?: unknown;
}
interface SceneSpec {
  canvas: CanvasSize;
  components: Record<string, DeclaredComponent>;
  scenes: Scene[];
  split: Record<string, string[]>;
}

function git(...args: string[]): Buffer {
  return execFileSync("git", args, { cwd: ROOT, maxBuffer: 32 * 1024 * 1024 });
}
function blob(tree: string, path: string): Buffer { return git("show", `${tree}:${path}`); }
function sha(bytes: Uint8Array): string { return createHash("sha256").update(bytes).digest("hex"); }

/** Same declared mask for the two poses and backdrop: invisibility cannot delete samples. */
export function readInterior(image: CalibrationImage, background: CalibrationImage, mask: Silhouette) {
  assertComparable(image, background);
  const linear = interiorLevel(image, { interior: mask });
  const encoded = encodedLuma(image);
  let sum = 0;
  let chroma = 0;
  let rgbRangeCodes = 0;
  let min = Infinity;
  let max = -Infinity;
  for (let i = 0; i < mask.mask.length; i += 1) {
    if (!mask.mask[i]) continue;
    const r = image.data[i * 4] ?? 0;
    const g = image.data[i * 4 + 1] ?? 0;
    const b = image.data[i * 4 + 2] ?? 0;
    const value = (encoded[i] ?? 0) / 255;
    sum += value;
    min = Math.min(min, value);
    max = Math.max(max, value);
    chroma += oklabChroma(srgbByteToOklab(r, g, b));
    rgbRangeCodes += Math.max(r, g, b) - Math.min(r, g, b);
  }
  const meanEncoded = sum / linear.sampleCount;
  let squares = 0;
  for (let i = 0; i < mask.mask.length; i += 1) {
    if (mask.mask[i]) squares += ((encoded[i] ?? 0) / 255 - meanEncoded) ** 2;
  }
  return {
    meanLinear: linear.mean,
    stdDevLinear: max === min ? 0 : linear.stdDev,
    meanEncoded,
    stdDevEncoded: Math.sqrt(squares / linear.sampleCount),
    encodedRange: max - min,
    meanOklabChroma: chroma / linear.sampleCount,
    chromaOfMeanLight: tintResponse(image, background, { interior: mask }).interiorChroma,
    meanRgbRangeCodes: rgbRangeCodes / linear.sampleCount,
    sampleCount: linear.sampleCount,
  };
}

/** A >1-code exterior count is evidence of exterior change, not a fitted shadow amplitude. */
export function difference(image: CalibrationImage, background: CalibrationImage, mask: Silhouette) {
  assertComparable(image, background);
  let differentRgbPixels = 0;
  let exteriorBeyondOneCode = 0;
  const exteriorBeyondOneCodePast2CssPx = 0;
  let maxChannelDelta = 0;
  const changed: number[] = [];
  for (let i = 0; i < mask.mask.length; i += 1) {
    let delta = 0;
    for (let c = 0; c < 3; c += 1) {
      delta = Math.max(delta, Math.abs((image.data[i * 4 + c] ?? 0) - (background.data[i * 4 + c] ?? 0)));
    }
    maxChannelDelta = Math.max(maxChannelDelta, delta);
    if (delta > 0) differentRgbPixels += 1;
    if (!mask.mask[i] && delta > 1) { exteriorBeyondOneCode += 1; changed.push(i); }
  }
  // The caller supplies the analytic distances for the supplementary edge-vs-shadow split.
  return { differentRgbPixels, maxChannelDelta, exteriorBeyondOneCode,
    exteriorBeyondOneCodePast2CssPx, changed };
}

const CONTOUR_READER = `
import importlib.util,json,math,sys
spec=importlib.util.spec_from_file_location("w23",sys.argv[1])
w23=importlib.util.module_from_spec(spec)
spec.loader.exec_module(w23)
jobs=json.load(open(sys.argv[2]))
def clean(x):
    if isinstance(x,float) and not math.isfinite(x): return None
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [clean(v) for v in x]
    return x
out=[]
for job in jobs:
    geom=w23.component_geometry(job["components"],job["component"])
    if geom is None:
        out.append({"applicable":False,"reason":"W23 has no single-box contour for groups or stacks"})
        continue
    pair={"applicable":True}
    for pose in ("active","inactive"):
        rgb=w23.rgb_of(job[pose])
        lum=w23.luma_of_rgb(rgb)
        body,sides=w23.contour_read(lum,rgb,job["canvas"],geom,job["scale"],6,2,1.6)
        valid=[s for s in sides.values() if math.isfinite(s["rim"])]
        pair[pose]={"bodyLinear":body,"sides":sides,
          "meanBandLinear":sum(sum(s["rows"])/len(s["rows"]) for s in valid)/len(valid),
          "meanRim":sum(s["rim"] for s in valid)/len(valid),
          "meanRimLocal":sum(s["rimLocal"] for s in valid)/len(valid)}
    out.append(pair)
json.dump(clean(out),sys.stdout,allow_nan=False)
`;
interface ContourPose { meanBandLinear: number; meanRim: number; meanRimLocal: number }
interface Contour { applicable: boolean; active?: ContourPose; inactive?: ContourPose }

function main(): void {
  const specPath = "apps/reference-apple/scenes.json";
  const specBytes = readFileSync(join(ROOT, specPath));
  const spec = JSON.parse(specBytes.toString()) as SceneSpec;
  const list = (tree: string) => git("ls-tree", "-r", "--name-only", tree, FIXTURES)
    .toString().trim().split("\n").filter((p) => /\/apple-[^/]+\/[^/]+\.png$/.test(p));
  const prior = new Set(list(INACTIVE));
  const paths = list(ACTIVE).filter((p) => prior.has(p)).sort();
  const scratch = mkdtempSync(join(tmpdir(), "w27c-recede-"));
  try {
    const jobs: { active: string; inactive: string; components: SceneSpec["components"];
      component: string; canvas: CanvasSize; scale: number }[] = [];
    const rows = paths.map((path, index) => {
      const profile = path.split("/").at(-2) as string;
      const id = path.split("/").at(-1)?.replace(/\.png$/, "");
      const scene = spec.scenes.find((s) => s.id === id);
      if (!scene) throw new Error(`Undeclared scene ${id}`);
      const component = spec.components[scene.component];
      if (!component) throw new Error(`Undeclared component ${scene.component}`);
      const scale = Number(profile.match(/-(\d+)x-/)?.[1]);
      const backgroundPath = `${FIXTURES}/backgrounds/${scene.background}@${scale}x.png`;
      const bgBytes = blob(ACTIVE, backgroundPath);
      if (!bgBytes.equals(blob(INACTIVE, backgroundPath))) throw new Error(`Background moved: ${backgroundPath}`);
      const activeBytes = blob(ACTIVE, path);
      const inactiveBytes = blob(INACTIVE, path);
      const background = decodePng(bgBytes);
      const active = decodePng(activeBytes);
      const inactive = decodePng(inactiveBytes);
      const region = componentRegion(component, { canvas: spec.canvas, scale,
        width: active.width, height: active.height });
      const interior = region.silhouette;
      const eroded: Silhouette = { ...interior,
        mask: Uint8Array.from(region.signedDistancePx, (d) => d <= -6 * scale ? 1 : 0) };
      const bg = readInterior(background, background, interior);
      const pose = (image: CalibrationImage) => {
        const stats = readInterior(image, background, interior);
        const delta = difference(image, background, interior);
        const { changed, ...counts } = delta;
        counts.exteriorBeyondOneCodePast2CssPx = changed.filter(
          (i) => (region.signedDistancePx[i] ?? 0) > 2 * scale).length;
        return { ...stats,
          structureLinear: bg.encodedRange === 0 ? null : stats.stdDevLinear / bg.stdDevLinear,
          structureEncoded: bg.encodedRange === 0 ? null : stats.stdDevEncoded / bg.stdDevEncoded,
          ...counts,
          backgroundIdentical: counts.differentRgbPixels === 0,
          eroded6CssPx: readInterior(image, background, eroded),
        };
      };
      const activePath = join(scratch, `${index}-active.png`);
      const inactivePath = join(scratch, `${index}-inactive.png`);
      writeFileSync(activePath, activeBytes);
      writeFileSync(inactivePath, inactiveBytes);
      jobs.push({ active: activePath, inactive: inactivePath, components: spec.components,
        component: scene.component, canvas: spec.canvas, scale });
      return { profile, scene: scene.id, component: scene.component, background: scene.background,
        state: scene.state, tinted: scene.tint !== undefined, scale,
        set: Object.entries(spec.split).find(([, ids]) => ids.includes(scene.id))?.[0] ?? "unassigned",
        hashes: { active: sha(activeBytes), inactive: sha(inactiveBytes), background: sha(bgBytes) },
        fixturesIdentical: activeBytes.equals(inactiveBytes),
        backdrop: bg, active: pose(active), inactive: pose(inactive),
        erodedBackdrop6CssPx: readInterior(background, background, eroded),
      };
    });
    const jobPath = join(scratch, "contours.json");
    writeFileSync(jobPath, JSON.stringify(jobs));
    const contours = JSON.parse(execFileSync(process.env["PYTHON"] ?? "python3",
      ["-c", CONTOUR_READER, join(ROOT, CONTOUR), jobPath], { maxBuffer: 32 * 1024 * 1024 }).toString()) as Contour[];
    const cells = rows.map((r, i) => ({ ...r, contour: contours[i] as Contour }));
    const mean = (xs: (number | null | undefined)[]) => {
      const values = xs.filter((x): x is number => x != null);
      return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;
    };
    const profiles = [...new Set(cells.map((c) => c.profile))].map((profile) => {
      const group = cells.filter((c) => c.profile === profile);
      const aggregate = (pose: "active" | "inactive") => ({
        meanLinear: mean(group.map((c) => c[pose].meanLinear)),
        meanEncoded: mean(group.map((c) => c[pose].meanEncoded)),
        liftLinear: mean(group.map((c) => c[pose].meanLinear - c.backdrop.meanLinear)),
        structureLinear: mean(group.map((c) => c[pose].structureLinear)),
        meanOklabChroma: mean(group.map((c) => c[pose].meanOklabChroma)),
        exteriorBeyondOneCode: mean(group.map((c) => c[pose].exteriorBeyondOneCode)),
        exteriorBeyondOneCodePast2CssPx: mean(group.map((c) => c[pose].exteriorBeyondOneCodePast2CssPx)),
        contourBandLinear: mean(group.map((c) => c.contour[pose]?.meanBandLinear)),
        rimLocal: mean(group.map((c) => c.contour[pose]?.meanRimLocal)),
      });
      return { profile, count: group.length,
        structureCount: group.filter((c) => c.active.structureLinear !== null).length,
        contourCount: group.filter((c) => c.contour.applicable).length,
        backdropMeanLinear: mean(group.map((c) => c.backdrop.meanLinear)),
        active: aggregate("active"), inactive: aggregate("inactive") };
    });
    const result = {
      declaredIn: "W27 coverage wave, W27c G0; claims §5.128; Decision Logs 5 and 7; X1/X3/X7/X8",
      provenance: { activeTree: git("rev-parse", ACTIVE).toString().trim(),
        inactiveTree: git("rev-parse", INACTIVE).toString().trim(),
        sceneSpecSha256: sha(specBytes), contourInstrumentSha256: sha(readFileSync(join(ROOT, CONTOUR))),
        schemaVersion: 2, runsPerCell: 1, pose: "Inferred from DL14 post-mortem, not attested per cell",
        matchedCells: cells.length, matchedScenes: new Set(cells.map((c) => c.scene)).size,
        currentScenes: spec.scenes.length, backgroundsByteIdentical: true },
      definitions: {
        interior: "Pixel-centre containment in declared componentRegion, margin 0; unions for groups and stacks. No image-derived silhouette. Rim is included; eroded6CssPx is a supplementary body check.",
        luminance: "Linear Rec.709 Y in [0,1]; encoded is mean Rec.709-weighted sRGB channels /255, not encode(mean Y). Population standard deviations on the same mask.",
        structure: "Interior stdDev / backdrop stdDev; null on uniform-luma backdrops. Profile means omit nulls, not zero-fill them.",
        chroma: "Mean of per-pixel OKLab hypot(a,b), native OKLab scale; chromaOfMeanLight is the existing tintResponse reader. meanRgbRangeCodes is a separate legacy RGB max-minus-min diagnostic, not OKLab.",
        exterior: "Outside the declared union, count pixels with any RGB channel differing by >1 code. Includes edge antialiasing/corner mismatch and toolbar bridges; >2 CSS px supplementary count separates immediate edges, not a shadow fit. Device pixel counts, canvas-limited.",
        identical: "Every decoded RGB pixel equals background, over whole canvas, zero tolerance; alpha is not optical evidence.",
        contour: "Unmodified W23 G3 reader: erode 6, depth 2 CSS px, corner factor 1.6; equal mean over applicable sides. Band mean is raw Y; rim and rimLocal are excess integrals per CSS px. Empty capsule sides null, composites inapplicable.",
        aggregation: "Equal-weight arithmetic means of cells per profile, including tinted/pressed/composite cells; not balanced by component or backdrop. No material fit and no new frozen holdout configuration.",
      },
      profiles, backgroundIdenticalInactive: cells.filter((c) => c.inactive.backgroundIdentical)
        .map((c) => ({ profile: c.profile, scene: c.scene })), cells,
    };
    const n = (x: number | null | undefined) => x == null ? "—" : x.toFixed(5);
    const pair = (a: number | null | undefined, b: number | null | undefined) => `${n(a)} → ${n(b)}`;
    const markdown = ["# W27c G0: the DL14 matched-pair recede (2026-09-10)", "",
      "Active → inactive. Definitions, hashes, per-side contours and supplementary eroded-body reads are in the JSON beside this table.",
      "Linear means and OKLab chroma are [0,1]-scale; exterior counts are device pixels. `—` means unidentifiable/inapplicable, never zero.", "",
      "| profile | n | backdrop Y | interior Y | encoded mean | lift Y | structure × | OKLab C | exterior >1 | contour band Y | local rim |",
      "| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
      ...profiles.map((p) => `| ${p.profile} | ${p.count} | ${n(p.backdropMeanLinear)} | ${pair(p.active.meanLinear,p.inactive.meanLinear)} | ${pair(p.active.meanEncoded,p.inactive.meanEncoded)} | ${pair(p.active.liftLinear,p.inactive.liftLinear)} | ${pair(p.active.structureLinear,p.inactive.structureLinear)} | ${pair(p.active.meanOklabChroma,p.inactive.meanOklabChroma)} | ${pair(p.active.exteriorBeyondOneCode,p.inactive.exteriorBeyondOneCode)} | ${pair(p.active.contourBandLinear,p.inactive.contourBandLinear)} | ${pair(p.active.rimLocal,p.inactive.rimLocal)} |`),
      "", "## Cells", "",
      "| profile / scene | backdrop Y / encoded | interior Y | encoded mean | structure linear × | structure encoded × | OKLab C | exterior >1 | contour band Y | local rim | inactive identical |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
      ...cells.map((c) => `| ${c.profile} / ${c.scene} | ${n(c.backdrop.meanLinear)} / ${n(c.backdrop.meanEncoded)} | ${pair(c.active.meanLinear,c.inactive.meanLinear)} | ${pair(c.active.meanEncoded,c.inactive.meanEncoded)} | ${pair(c.active.structureLinear,c.inactive.structureLinear)} | ${pair(c.active.structureEncoded,c.inactive.structureEncoded)} | ${pair(c.active.meanOklabChroma,c.inactive.meanOklabChroma)} | ${c.active.exteriorBeyondOneCode} → ${c.inactive.exteriorBeyondOneCode} | ${pair(c.contour.active?.meanBandLinear,c.contour.inactive?.meanBandLinear)} | ${pair(c.contour.active?.meanRimLocal,c.contour.inactive?.meanRimLocal)} | ${c.inactive.backgroundIdentical} |`), "",
    ].join("\n");
    writeFileSync(resolve(ROOT, `${process.env["W27C_OUT"] ?? OUT}.json`), `${JSON.stringify(result, null, 2)}\n`, { flag: "wx" });
    writeFileSync(resolve(ROOT, `${process.env["W27C_OUT"] ?? OUT}.md`), markdown, { flag: "wx" });
    process.stdout.write(`${cells.length} pairs, ${result.provenance.matchedScenes} scenes; ${result.backgroundIdenticalInactive.length} inactive background-identical cells.\n`);
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
