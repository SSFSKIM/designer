/**
 * W19 G0 (b) — the strength ladder's reader.
 *
 * W18 G0's `separation.ts` with its rows re-aimed. The quantity is the same kind — a CSS-tier minus
 * GPU-tier interior mean over one declared component, which needs no native reference — and the two
 * masks are the same two, for the same reason: where the canonical bed has a fixture for the scene id
 * AND declares the same geometry, the reading is taken under the NATIVE silhouette, which is the mask
 * every number in the Grounding Baseline is under; where it does not (every new rung of the ladder),
 * the only mask is the DECLARED component region, rasterised by pixel-centre containment at margin 0,
 * which is the same region that bounds the native extractor's own search. Both are reported on every
 * cell that admits both, so the mask choice's own worth is visible on the controls.
 *
 * What is new here is the third column the charter asks for: **the form each CSS cell drew**, read
 * off the capture's own report (`page.groups[].state.cssTint`) rather than predicted. The boundary
 * `cssTintFormAt` draws is read at the MATERIAL's composite level, so an author layer at low strength
 * should not move it; that is a claim about the shipped code and this makes it a reading.
 *
 * The per-surface split and the annulus bands W18 needed are not carried: every scene on this bed is
 * one capsule, so the component region and the surface's own shape are the same mask, and the
 * quantity under test is a level rather than a contour band. The population standard deviation is
 * reported beside each mean because the fold changes L3's colour and alpha on every tinted surface
 * and a spread that moves is a structure cost the mean would hide.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g0/ladder.ts <scenesJson> <gpuRoot> <cssRoot> \
 *     <scale> <outJson>
 * Reads only captures and committed fixtures; writes only the file it is given.
 */

import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
  DEFAULT_SILHOUETTE_THRESHOLD,
} from "../../../cli/measure";
import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import {
  componentRegion,
  decodePng,
  extractSilhouette,
  interiorLevel,
  linearLuminance,
  type CalibrationImage,
  type Silhouette,
} from "../../../src/index";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const [, , scenesJson, gpuRoot, cssRoot, scaleArg, outJson] = process.argv;
if (scenesJson === undefined || gpuRoot === undefined || cssRoot === undefined ||
    scaleArg === undefined || outJson === undefined) {
  throw new Error("usage: ladder.ts <scenesJson> <gpuRoot> <cssRoot> <scale> <outJson>");
}
const scale = Number(scaleArg);

interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly {
    readonly profileKey: string;
    readonly fixtures: readonly { readonly sceneId: string; readonly file: string }[];
  }[];
}
const manifest = JSON.parse(readFileSync(resolve(FIXTURES, "manifest.json"), "utf8")) as Manifest;
const canonicalProfileKey = `apple-macos-26.5-${String(scale)}x-light-standard`;
const canonicalProfile = manifest.profiles.find((p) => p.profileKey === canonicalProfileKey);
const canonicalGeometry = readSceneGeometry(REFERENCE);
const geometry = readSceneGeometry(scenesJson);

const load = (path: string): CalibrationImage => decodePng(readFileSync(path));

/** Mean and population standard deviation of linear luminance under one mask. */
function statsOver(
  image: CalibrationImage,
  mask: Uint8Array,
  width: number,
  height: number,
): { mean: number; sd: number; pixels: number } {
  const mean = interiorLevel(image, { interior: { width, height, mask } }).mean;
  const luminance = linearLuminance(image);
  let sum = 0;
  let pixels = 0;
  for (let i = 0; i < mask.length; i += 1) {
    if ((mask[i] ?? 0) === 0) continue;
    const d = (luminance[i] ?? 0) - mean;
    sum += d * d;
    pixels += 1;
  }
  return { mean, sd: pixels === 0 ? 0 : Math.sqrt(sum / pixels), pixels };
}

/** The resolved tint form the CSS capture's own report published, per group. */
function cssTintForms(reportPath: string): string[] {
  if (!existsSync(reportPath)) return [];
  const report = JSON.parse(readFileSync(reportPath, "utf8")) as {
    page?: { groups?: { state?: { cssTint?: string } }[] };
  };
  return (report.page?.groups ?? []).map((group) => group.state?.cssTint ?? "none");
}

const rows: unknown[] = [];
for (const scene of geometry.scenes) {
  const gpuPath = resolve(gpuRoot, scene.id, `${scene.id}__webgpu.png`);
  const cssPath = resolve(cssRoot, scene.id, `${scene.id}__css.png`);
  if (!existsSync(gpuPath) || !existsSync(cssPath)) {
    rows.push({ scene: scene.id, dpr: scale, skipped: "a capture is missing" });
    continue;
  }
  const gpu = load(gpuPath);
  const css = load(cssPath);
  const { width, height } = gpu;

  const component = declaredComponentOf(geometry, scene.id);
  const region = componentRegion(component, { canvas: geometry.canvas, scale, width, height });

  /*
   * The native silhouette, where the canonical bed has a fixture for this exact scene id AND
   * declares the same geometry. Both are checked rather than assumed: the ladder's controls are the
   * canonical ids verbatim, and a component that had drifted would put a native mask over a shape it
   * does not describe.
   */
  let nativeMask: Silhouette | undefined;
  const fixture = canonicalProfile?.fixtures.find((f) => f.sceneId === scene.id);
  const canonicalScene = canonicalGeometry.scenes.find((s) => s.id === scene.id);
  const sameGeometry =
    canonicalScene !== undefined &&
    JSON.stringify(canonicalGeometry.components[canonicalScene.component]) === JSON.stringify(component);
  if (fixture !== undefined && sameGeometry) {
    const backgroundKey = `${scene.id.split("__")[0] as string}@${String(scale)}x`;
    const backgroundFile = manifest.backgrounds[backgroundKey];
    if (backgroundFile !== undefined) {
      nativeMask = extractSilhouette(load(resolve(FIXTURES, fixture.file)), {
        kind: "luminance-delta",
        background: load(resolve(FIXTURES, backgroundFile)),
        threshold: DEFAULT_SILHOUETTE_THRESHOLD,
        chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
        region: region.silhouette,
      });
    }
  }

  const under = (mask: Uint8Array): unknown => {
    const a = statsOver(gpu, mask, width, height);
    const b = statsOver(css, mask, width, height);
    return { gpu: a.mean, css: b.mean, delta: b.mean - a.mean, sdGpu: a.sd, sdCss: b.sd, pixels: a.pixels };
  };

  rows.push({
    scene: scene.id,
    dpr: scale,
    tint: (geometry as unknown as { scenes: { id: string; tint?: string }[] }).scenes
      .find((s) => s.id === scene.id)?.tint ?? null,
    whole: {
      declared: under(region.silhouette.mask),
      ...(nativeMask === undefined ? {} : { native: under(nativeMask.mask) }),
    },
    nativeFixture: fixture?.file ?? null,
    cssTint: cssTintForms(resolve(cssRoot, scene.id, "report__css.json")),
    sha256: {
      gpu: createHash("sha256").update(readFileSync(gpuPath)).digest("hex").slice(0, 16),
      css: createHash("sha256").update(readFileSync(cssPath)).digest("hex").slice(0, 16),
    },
  });
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} scenes -> ${outJson}\n`);
