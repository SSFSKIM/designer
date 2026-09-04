/**
 * W18 G1's pre-check (2) — the interior's MEAN and its SPREAD, per tier, beside the backdrop's own.
 *
 * G0's `separation.ts` reads the mean, which is the quantity every bound in this wave is written
 * on. The pre-check asks for one more statistic and it asks for it for a specific reason: with the
 * outer shadow out of the sampled backdrop a remainder is left on the STRUCTURED backdrops and
 * essentially nothing on the solid one (M2's signature), and a level difference that comes from a
 * difference in the blur's effective width shows up in the spread before it shows up in the mean.
 * A tier whose kernel is narrower than the renderer's keeps more of the backdrop's structure, so
 * its interior standard deviation is higher; a tier that differs only in level moves the mean and
 * leaves the spread alone. The backdrop's own standard deviation under the identical mask is the
 * denominator that makes the two tiers' numbers comparable across backdrops.
 *
 * Everything else is `separation.ts`'s: the same two masks (the native silhouette where the
 * canonical bed has a fixture for this scene id and declares the same geometry, the declared
 * component region otherwise), the same per-surface shapes, the same linear-luminance space.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w18-union-contour/g1/spread.ts <scenesJson> <gpuRoot> <cssRoot> \
 *     <scale> <outJson>
 * Reads only captures and committed fixtures; writes only the file it is given.
 */

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
  placeComponent,
  type CalibrationImage,
  type PlacedShape,
  type Silhouette,
} from "../../../src/index";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const [, , scenesJson, gpuRoot, cssRoot, scaleArg, outJson] = process.argv;
if (scenesJson === undefined || gpuRoot === undefined || cssRoot === undefined ||
    scaleArg === undefined || outJson === undefined) {
  throw new Error("usage: spread.ts <scenesJson> <gpuRoot> <cssRoot> <scale> <outJson>");
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
const canonicalProfile = manifest.profiles.find(
  (profile) => profile.profileKey === `apple-macos-26.5-${scale}x-light-standard`,
);
const canonicalGeometry = readSceneGeometry(REFERENCE);
const geometry = readSceneGeometry(scenesJson);

const load = (path: string): CalibrationImage => decodePng(readFileSync(path));

/** Exact signed distance to one placed rounded rectangle, device px, negative inside. */
function shapeDistance(shape: PlacedShape, x: number, y: number): number {
  const centreX = (shape.left + shape.width / 2) * scale;
  const centreY = (shape.top + shape.height / 2) * scale;
  const halfWidth = (shape.width / 2) * scale;
  const halfHeight = (shape.height / 2) * scale;
  const radius = shape.radius * scale;
  const qx = Math.abs(x - centreX) - (halfWidth - radius);
  const qy = Math.abs(y - centreY) - (halfHeight - radius);
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius;
}

function maskOfShape(shape: PlacedShape, width: number, height: number): Uint8Array {
  const mask = new Uint8Array(width * height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (shapeDistance(shape, x + 0.5, y + 0.5) <= 0) mask[y * width + x] = 1;
    }
  }
  return mask;
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
  const placed = placeComponent(component, geometry.canvas);

  // The backdrop this scene stands over, under the very same mask: the denominator that turns a
  // standard deviation into "how much of the backdrop's structure survived".
  const backgroundKey = `${scene.id.split("__")[0] as string}@${scale}x`;
  const backgroundFile = manifest.backgrounds[backgroundKey];
  const background = backgroundFile === undefined ? undefined : load(resolve(FIXTURES, backgroundFile));

  let nativeMask: Silhouette | undefined;
  const fixture = canonicalProfile?.fixtures.find((entry) => entry.sceneId === scene.id);
  const canonicalScene = canonicalGeometry.scenes.find((entry) => entry.id === scene.id);
  const sameGeometry =
    canonicalScene !== undefined &&
    JSON.stringify(canonicalGeometry.components[canonicalScene.component]) ===
      JSON.stringify(component);
  if (fixture !== undefined && sameGeometry && background !== undefined) {
    nativeMask = extractSilhouette(load(resolve(FIXTURES, fixture.file)), {
      kind: "luminance-delta",
      background,
      threshold: DEFAULT_SILHOUETTE_THRESHOLD,
      chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
      region: region.silhouette,
    });
  }

  const under = (mask: Uint8Array): Record<string, number> => {
    const interior = { interior: { width, height, mask } };
    const a = interiorLevel(gpu, interior);
    const b = interiorLevel(css, interior);
    const backdrop = background === undefined ? undefined : interiorLevel(background, interior);
    return {
      gpuMean: a.mean,
      cssMean: b.mean,
      deltaMean: b.mean - a.mean,
      gpuSd: a.stdDev,
      cssSd: b.stdDev,
      deltaSd: b.stdDev - a.stdDev,
      ...(backdrop === undefined
        ? {}
        : {
            backdropMean: backdrop.mean,
            backdropSd: backdrop.stdDev,
            // What fraction of the backdrop's own structure each tier keeps.
            gpuKeep: backdrop.stdDev === 0 ? 0 : a.stdDev / backdrop.stdDev,
            cssKeep: backdrop.stdDev === 0 ? 0 : b.stdDev / backdrop.stdDev,
          }),
      pixels: a.sampleCount,
    };
  };

  rows.push({
    scene: scene.id,
    dpr: scale,
    whole: {
      declared: under(region.silhouette.mask),
      ...(nativeMask === undefined ? {} : { native: under(nativeMask.mask) }),
    },
    surfaces: placed.map((shape, index) => ({
      index,
      declared: under(maskOfShape(shape, width, height)),
    })),
  });
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} scenes -> ${outJson}\n`);
