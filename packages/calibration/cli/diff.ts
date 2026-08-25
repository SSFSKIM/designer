/**
 * `diff` — the per-axis report CLI, and the thing that writes X9's result matrix.
 *
 * Usage — note that `pnpm --filter` runs in the package directory, so relative
 * paths resolve from `packages/calibration/`, not the repo root:
 *
 *   pnpm --filter @vitrea/calibration run diff -- \
 *     --native  ../../apps/reference-apple/fixtures/<profile>/<scene>.png \
 *     --web     web-captures/<scene>/capture.png \
 *     --background ../../apps/reference-apple/fixtures/backgrounds/<bg>@1x.png \
 *     --profile apple-macos-26.5-1x-light-standard \
 *     --scene   checkerboard__capsule-button__rest \
 *     --web-cell web-captures/<scene>/cell.json \
 *     --matrix  results/matrix.json
 *
 * Two design rules, both from the spec rather than convenience:
 *
 * **The background is a first-class input, not an optional extra.** Every
 * material metric is a comparison *against the backdrop the material sampled*,
 * and the silhouette of an opaque native composite can only be found by
 * differencing against that same backdrop. Without `--background` this reports
 * the shape and perceptual axes and says so; it does not guess a material number.
 *
 * **No thresholds and no verdict.** The exit code says whether the measurement
 * ran, never whether the numbers are good. What counts as close enough is per
 * tier and per engine cell, decided against holdout fixtures, and it is C9's.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname } from "node:path";

import {
  blurEdgeSpread,
  cornerCurvature,
  contourDistance,
  createResultMatrix,
  decodePng,
  deserializeResultMatrix,
  edgeWeightedDifference,
  extractSilhouette,
  luminanceTransfer,
  materialAxisReport,
  oklabDeltaE,
  parseProfileKey,
  perceptualAxisReport,
  resultCellKey,
  rimIntensity,
  serializeResultMatrix,
  shadowFalloff,
  shapeAxisReport,
  silhouetteArea,
  silhouetteBounds,
  silhouetteIoU,
  ssim,
  tintResponse,
  upsertCellResult,
  type CalibrationImage,
  type CellResult,
  type FidelityTier,
  type FixtureSet,
  type MaterialAxisReport,
  type PerceptualAxisReport,
  type ShapeAxisReport,
  type Silhouette,
  type WebCell,
} from "../src/index";

interface Args {
  readonly native: string;
  readonly web: string;
  readonly background?: string;
  readonly profile: string;
  readonly scene: string;
  readonly webCell: string;
  readonly matrix?: string;
  readonly out?: string;
  readonly tier: FidelityTier;
  readonly fixtureSet: FixtureSet;
  readonly blurAxis: "x" | "y";
  readonly blurRegion?: readonly [number, number, number, number];
  /**
   * Linear-light luminance delta that counts as "the component is here", used to
   * cut the silhouette out of an opaque composite. Exposed because the right
   * value depends on the background's own contrast: a glass body over a flat
   * light-solid backdrop differs from it far less than over a checkerboard.
   */
  readonly silhouetteThreshold: number;
}

function parseArgs(argv: readonly string[]): Args {
  const map = new Map<string, string>();
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === undefined || !token.startsWith("--")) continue;
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) {
      map.set(token.slice(2), "true");
    } else {
      map.set(token.slice(2), next);
      i += 1;
    }
  }

  const need = (name: string): string => {
    const v = map.get(name);
    if (v === undefined) throw new Error(`diff: --${name} is required`);
    return v;
  };

  const profile = need("profile");
  if (parseProfileKey(profile) === null) {
    throw new Error(
      `diff: --profile '${profile}' does not match X9's profile-key grammar ` +
        `(apple-<platform>-<os>-<scale>x-<scheme>-<a11y>)`,
    );
  }

  const tier = map.get("tier") ?? "texture";
  if (tier !== "texture" && tier !== "dom") {
    throw new Error(`diff: --tier must be 'texture' or 'dom', got '${tier}'`);
  }

  const fixtureSet = map.get("fixture-set") ?? "calibration";
  if (fixtureSet !== "calibration" && fixtureSet !== "validation" && fixtureSet !== "holdout") {
    throw new Error(`diff: --fixture-set must be calibration|validation|holdout, got '${fixtureSet}'`);
  }

  const blurAxis = map.get("blur-axis") ?? "x";
  if (blurAxis !== "x" && blurAxis !== "y") {
    throw new Error(`diff: --blur-axis must be 'x' or 'y', got '${blurAxis}'`);
  }

  let blurRegion: readonly [number, number, number, number] | undefined;
  const rawRegion = map.get("blur-region");
  if (rawRegion !== undefined && rawRegion !== "true") {
    const parts = rawRegion.split(",").map((p) => Number.parseInt(p.trim(), 10));
    if (parts.length !== 4 || parts.some((p) => !Number.isFinite(p))) {
      throw new Error(`diff: --blur-region must be 'x,y,width,height', got '${rawRegion}'`);
    }
    blurRegion = [parts[0] as number, parts[1] as number, parts[2] as number, parts[3] as number];
  }

  // Optional fields are spread in only when present: `exactOptionalPropertyTypes`
  // distinguishes "absent" from "present and undefined", and that distinction is
  // one this package leans on everywhere else (an absent axis means not measured,
  // never measured as zero), so the CLI honours it too.
  const background = map.get("background");
  const matrix = map.get("matrix");
  const out = map.get("out");

  return {
    native: need("native"),
    web: need("web"),
    profile,
    scene: need("scene"),
    webCell: need("web-cell"),
    tier,
    fixtureSet,
    blurAxis,
    silhouetteThreshold: Number(map.get("silhouette-threshold") ?? "0.02"),
    ...(background === undefined ? {} : { background }),
    ...(matrix === undefined ? {} : { matrix }),
    ...(out === undefined ? {} : { out }),
    ...(blurRegion === undefined ? {} : { blurRegion }),
  };
}

function loadImage(path: string): CalibrationImage {
  return decodePng(readFileSync(path));
}

/**
 * Read the web cell descriptor the capture script wrote.
 *
 * Required, with no default, and that is the point. `WebCell.renderer` is a
 * closed `"webgpu" | "css"` — there is no honest "unknown" for which tier drew,
 * because the whole purpose of the web axis is that a fidelity claim names the
 * cell it was measured in. A cell defaulted to the common case would make every
 * row in the matrix a guess. So the capture script, which is the only thing that
 * actually knows, has to say.
 */
function loadWebCell(path: string): WebCell {
  const raw: unknown = JSON.parse(readFileSync(path, "utf8"));
  if (typeof raw !== "object" || raw === null) {
    throw new Error(`diff: --web-cell '${path}' is not a JSON object`);
  }
  const cell = raw as Partial<WebCell>;
  const missing = (["engine", "engineVersion", "renderer", "samplingBackend", "gpuAdapter", "colorSpace", "capturePath"] as const).filter(
    (field) => cell[field] === undefined,
  );
  if (missing.length > 0) {
    throw new Error(`diff: --web-cell '${path}' is missing: ${missing.join(", ")}`);
  }
  if (cell.renderer !== "webgpu" && cell.renderer !== "css") {
    throw new Error(`diff: --web-cell renderer must be 'webgpu' or 'css', got '${String(cell.renderer)}'`);
  }
  if (cell.colorSpace !== "srgb") {
    throw new Error(`diff: --web-cell colorSpace must be 'srgb' (X5 locks v1), got '${String(cell.colorSpace)}'`);
  }
  return cell as WebCell;
}

/**
 * A default blur-measurement region: a strip across the middle of the
 * component's interior.
 *
 * The material's blur is measured by looking at a *backdrop* step edge seen
 * through the glass, so the region has to sit inside the silhouette and cross an
 * edge of the background pattern. A strip through the interior centre does that
 * on the checkerboard and impulse scenes the spec mandates for exactly this
 * purpose. It is a default, not a claim — `--blur-region` overrides it, and the
 * report carries `blurFitResidual` so a region that contains no clean edge shows
 * up as a bad fit rather than a confident wrong sigma.
 */
function defaultBlurRegion(silhouette: Silhouette): readonly [number, number, number, number] | undefined {
  const { minX, minY, maxX, maxY } = silhouetteBounds(silhouette);
  const width = maxX - minX + 1;
  const height = maxY - minY + 1;
  if (!Number.isFinite(width) || width <= 4 || height <= 4) return undefined;
  const inset = Math.max(2, Math.round(Math.min(width, height) * 0.15));
  const y = Math.round(minY + height / 2 - 2);
  return [minX + inset, y, Math.max(4, width - 2 * inset), 4];
}

function main(): void {
  const args = parseArgs(process.argv.slice(2));

  const native = loadImage(args.native);
  const web = loadImage(args.web);
  const background = args.background === undefined ? undefined : loadImage(args.background);

  // Silhouettes. With a background we can difference against it, which is the
  // only way to find the component in an opaque native composite; without one we
  // fall back to alpha, which only works for a capture taken over transparency.
  const extractor = background
    ? ({ kind: "luminance-delta", background, threshold: args.silhouetteThreshold } as const)
    : ({ kind: "alpha", threshold: 0.5 } as const);

  const nativeSil = extractSilhouette(native, extractor);
  const webSil = extractSilhouette(web, extractor);
  const nativeArea = silhouetteArea(nativeSil);
  const webArea = silhouetteArea(webSil);

  // An empty silhouette is a real, informative outcome, not an error: it means
  // that side's capture contains nothing distinguishable from its background.
  // That is exactly the current state of the native fixtures, so the shape axis
  // is reported as ABSENT with the reason, rather than crashing the run or —
  // worse — inventing an IoU of 0 that would read like a measured mismatch. The
  // other axes still measure what they legitimately can.
  const notes: string[] = [];
  let shape: ShapeAxisReport | undefined;
  if (nativeArea === 0 || webArea === 0) {
    const empty = [nativeArea === 0 ? "native" : undefined, webArea === 0 ? "web" : undefined]
      .filter((s): s is string => s !== undefined)
      .join(" and ");
    notes.push(
      `shape axis NOT MEASURED: the ${empty} silhouette is empty at threshold ` +
        `${String(args.silhouetteThreshold)} — that capture is indistinguishable from its ` +
        `background, so there is no contour to compare.`,
    );
  } else {
    shape = shapeAxisReport({
      silhouetteIoU: silhouetteIoU(nativeSil, webSil),
      contourDistance: contourDistance(nativeSil, webSil),
      cornerCurvature: cornerCurvature(nativeSil, webSil),
    });
  }

  const perceptual: PerceptualAxisReport = perceptualAxisReport({
    edgeWeighted: edgeWeightedDifference(native, web),
    ssim: ssim(native, web),
    oklabDeltaE: oklabDeltaE(native, web),
  });

  let material: MaterialAxisReport | undefined;
  if (background !== undefined && webArea > 0) {
    const region = args.blurRegion ?? defaultBlurRegion(webSil);
    const blur = blurEdgeSpread(
      web,
      region === undefined
        ? { axis: args.blurAxis }
        : { axis: args.blurAxis, region: { x: region[0], y: region[1], width: region[2], height: region[3] } },
    );
    material = materialAxisReport({
      blur,
      luminance: luminanceTransfer(native, web, background, { interior: webSil }),
      tint: tintResponse(web, background, { interior: webSil }),
      rim: rimIntensity(web, webSil),
      shadow: shadowFalloff(web, webSil, background),
    });
  }

  const cell: CellResult = {
    key: resultCellKey(args.profile, loadWebCell(args.webCell), args.scene),
    fixtureSet: args.fixtureSet,
    tier: args.tier,
    capturedAt: new Date().toISOString(),
    perceptual,
    // Absent axes mean "not measured", which is what the schema's optional axes
    // are for — never "measured as zero". No motion axis: this is a still pair.
    ...(shape === undefined ? {} : { shape }),
    ...(material === undefined ? {} : { material }),
  };

  const reportJson = JSON.stringify(cell, null, 2);
  if (args.out !== undefined) {
    mkdirSync(dirname(args.out), { recursive: true });
    writeFileSync(args.out, `${reportJson}\n`);
    process.stderr.write(`report → ${args.out}\n`);
  } else {
    process.stdout.write(`${reportJson}\n`);
  }

  if (args.matrix !== undefined) {
    const existing =
      existsSync(args.matrix) ? deserializeResultMatrix(readFileSync(args.matrix, "utf8")) : createResultMatrix();
    const updated = upsertCellResult(existing, cell);
    mkdirSync(dirname(args.matrix), { recursive: true });
    writeFileSync(args.matrix, `${serializeResultMatrix(updated, { pretty: true })}\n`);
    process.stderr.write(`matrix → ${args.matrix}\n`);
  }

  if (material === undefined) {
    notes.push(
      background === undefined
        ? "material axis NOT MEASURED: no --background given (absent, not zero)."
        : "material axis NOT MEASURED: the web silhouette is empty, so there is no interior to sample.",
    );
  }
  for (const note of notes) process.stderr.write(`note: ${note}\n`);
}

main();
