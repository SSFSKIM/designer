/**
 * W18 G0 (a) and (c) — the separation reader.
 *
 * The wave's question is a difference between two web captures of one scene, so this reads pairs of
 * captures rather than cells of a matrix: `compare` plans its cells from the native manifest and
 * eight of this study's eighteen scenes have no native fixture, while the quantity under test —
 * CSS-tier interior mean minus GPU-tier interior mean — needs no reference at all.
 *
 * ## The two masks, and why both are reported
 *
 * `cli/measure.ts` reads the interior under the NATIVE silhouette: the reference's own composite cut
 * out of its background by a luminance delta, bounded by the declared region. That is the mask every
 * number in the bed is under, and it is the one this study must use wherever a fixture exists, or its
 * readings would not be comparable with the Grounding Baseline. Where no fixture exists — the lone
 * circle, the three-up at 40, the stack's two parts, everything over `light-solid` that the bed never
 * captured — the only mask available is the DECLARED component region, rasterised by pixel-centre
 * containment at margin 0 (`src/component-region.ts`), which is the same region that bounds the
 * native extractor's search.
 *
 * So both are computed on every cell that admits both, and every row says which it is under. The
 * difference between the two columns on the twins is itself a reading: it is what the mask choice
 * alone is worth, and it bounds the comparability of the rows that have only one of them.
 *
 * ## Per surface, and the annulus
 *
 * A group's declared region is the union of three circles and a stack's is a base with an overlay
 * across it, so a single interior mean over the component mixes surfaces that are not in the same
 * situation. Every reading is therefore also taken per surface, over that surface's own placed shape,
 * and — for W17 G1's diagnosis, which this extends — split into four annuli by the fraction of the
 * half extent (0.00-0.40, 0.40-0.70, 0.70-0.88, 0.88-1.00), so a broad interior offset can be told
 * from a contour band.
 *
 * The stack's base is reported twice: over its whole placed shape, and over the part of it the
 * overlay does not cover. The overlay's own footprint is not the base's material and averaging the
 * two would hide exactly the term M4 exists to find.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w18-union-contour/g0/separation.ts <scenesJson> <gpuRoot> <cssRoot> \
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
  throw new Error("usage: separation.ts <scenesJson> <gpuRoot> <cssRoot> <scale> <outJson>");
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
const canonicalProfileKey = `apple-macos-26.5-${scale}x-light-standard`;
const canonicalProfile = manifest.profiles.find((p) => p.profileKey === canonicalProfileKey);
const canonicalGeometry = readSceneGeometry(REFERENCE);

const geometry = readSceneGeometry(scenesJson);

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

interface ShapeMask {
  readonly mask: Uint8Array;
  /** Inward depth in device px at each masked pixel; the annulus split reads it. */
  readonly depth: Float64Array;
  readonly halfExtentPx: number;
}

function maskOfShape(shape: PlacedShape, width: number, height: number): ShapeMask {
  const mask = new Uint8Array(width * height);
  const depth = new Float64Array(width * height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const distance = shapeDistance(shape, x + 0.5, y + 0.5);
      const index = y * width + x;
      depth[index] = -distance;
      if (distance <= 0) mask[index] = 1;
    }
  }
  return {
    mask,
    depth,
    halfExtentPx: (Math.min(shape.width, shape.height) / 2) * scale,
  };
}

const load = (path: string): CalibrationImage => decodePng(readFileSync(path));

const meanOver = (image: CalibrationImage, mask: Uint8Array, width: number, height: number): number =>
  interiorLevel(image, { interior: { width, height, mask } }).mean;

const BANDS: readonly (readonly [number, number])[] = [
  [0.0, 0.4],
  [0.4, 0.7],
  [0.7, 0.88],
  [0.88, 1.0],
];

/** Band means over one shape: the fraction of the half extent, as W17 G1 split it. */
function bandMeans(
  image: CalibrationImage,
  shape: ShapeMask,
  and: Uint8Array | undefined,
  width: number,
  height: number,
): (number | null)[] {
  return BANDS.map(([low, high]) => {
    const mask = new Uint8Array(width * height);
    let count = 0;
    for (let i = 0; i < mask.length; i += 1) {
      if ((shape.mask[i] ?? 0) === 0) continue;
      if (and !== undefined && (and[i] ?? 0) === 0) continue;
      const fraction = 1 - (shape.depth[i] ?? 0) / shape.halfExtentPx;
      if (fraction >= low && fraction < high + (high === 1 ? 1e-9 : 0)) {
        mask[i] = 1;
        count += 1;
      }
    }
    if (count === 0) return null;
    return interiorLevel(image, { interior: { width, height, mask } }).mean;
  });
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

  /*
   * The native silhouette, where the canonical bed has a fixture for this exact scene id AND
   * declares the same geometry. Both conditions are checked rather than assumed: the twins in the
   * scratch bed are copied verbatim from `scenes.json`, and a component that had drifted would put
   * a native mask over a shape it does not describe.
   */
  let nativeMask: Silhouette | undefined;
  const fixture = canonicalProfile?.fixtures.find((f) => f.sceneId === scene.id);
  const canonicalScene = canonicalGeometry.scenes.find((s) => s.id === scene.id);
  const sameGeometry =
    canonicalScene !== undefined &&
    JSON.stringify(canonicalGeometry.components[canonicalScene.component]) ===
      JSON.stringify(component);
  if (fixture !== undefined && sameGeometry) {
    const backgroundKey = `${scene.id.split("__")[0] as string}@${scale}x`;
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

  const under = (mask: Uint8Array): { gpu: number; css: number; delta: number; pixels: number } => {
    const a = meanOver(gpu, mask, width, height);
    const b = meanOver(css, mask, width, height);
    let pixels = 0;
    for (const value of mask) pixels += value;
    return { gpu: a, css: b, delta: b - a, pixels };
  };

  const shapes = placed.map((shape) => maskOfShape(shape, width, height));
  const isStack = (component as { kind: string }).kind === "stack";

  const surfaces = shapes.map((shape, index) => {
    // The stack's base, minus the overlay's footprint: the overlay's pixels are not the base's
    // material, and M4's term is exactly the difference between the two.
    let and: Uint8Array | undefined;
    if (isStack && index === 0) {
      and = new Uint8Array(width * height);
      const over = shapes[1] as ShapeMask;
      for (let i = 0; i < and.length; i += 1) and[i] = (over.mask[i] ?? 0) === 0 ? 1 : 0;
    }
    const combined = new Uint8Array(width * height);
    for (let i = 0; i < combined.length; i += 1) {
      combined[i] = (shape.mask[i] ?? 0) === 1 && (and === undefined || (and[i] ?? 0) === 1) ? 1 : 0;
    }
    return {
      index,
      role: isStack ? (index === 0 ? "base (overlay excluded)" : "overlay") : `item-${index}`,
      declared: under(combined),
      ...(nativeMask === undefined
        ? {}
        : {
            native: under(
              (() => {
                const m = new Uint8Array(width * height);
                for (let i = 0; i < m.length; i += 1) {
                  m[i] = (combined[i] ?? 0) === 1 && (nativeMask.mask[i] ?? 0) === 1 ? 1 : 0;
                }
                return m;
              })(),
            ),
          }),
      annulusDeclared: {
        gpu: bandMeans(gpu, shape, and, width, height),
        css: bandMeans(css, shape, and, width, height),
      },
    };
  });

  rows.push({
    scene: scene.id,
    dpr: scale,
    component: (component as { kind: string }).kind,
    whole: {
      declared: under(region.silhouette.mask),
      ...(nativeMask === undefined ? {} : { native: under(nativeMask.mask) }),
    },
    nativeFixture: fixture?.file ?? null,
    surfaces,
  });
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} scenes -> ${outJson}\n`);
