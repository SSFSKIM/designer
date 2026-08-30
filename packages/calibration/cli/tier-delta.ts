/**
 * `tier-delta` — how far apart the two tiers draw the same scene.
 *
 *   npx tsx cli/tier-delta.ts --profile apple-macos-26.5-1x-light-standard
 *   npx tsx cli/tier-delta.ts --scene checkerboard__rrect-md__rest
 *
 * ## Why this is a different measurement from `compare`
 *
 * Every other number in this package is a *fidelity* number: web against native.
 * Coherence is not that. Two tiers can each be within their own threshold of the
 * reference and still be visibly different from each other — and a demotion,
 * which is the one transition X2 promises to be honest about, is exactly where a
 * reader sees the two side by side rather than each beside Apple. So the pair
 * needs its own diff, web against web, with no fixture in it at all.
 *
 * C9a measured the gap this exists to watch: the CSS tier's `tintAlpha` was 0.28
 * while the renderer's had been tuned to 0.62, so a root that lost its GPU device
 * changed opacity by more than 2×. That is invisible to `compare`, which never
 * puts one tier's capture next to the other's.
 *
 * ## What it reports, and why those numbers
 *
 * Per scene, over the two captures `compare` already wrote:
 *
 * - **interior mean, per tier**, under the native silhouette. The material's
 *   level, in linear light — the quantity the >2× gap was *in*, and the only one
 *   here a reader can convert back into an alpha by hand.
 * - **SSIM and OKLab ΔE between the two tiers.** Whole-canvas, so the shadow that
 *   makes the dom tier's silhouette incomparable (claims §3) is included rather
 *   than masked out: a viewer sees it.
 * - **each tier's own ΔE against the native fixture**, alongside, because a
 *   coherence number is only good news if both tiers are still close to the
 *   reference. Coherence bought by dragging both tiers away from Apple is not a
 *   result, and printing the three columns together is what makes that legible.
 *
 * No thresholds, per this package's standing rule. This prints a gap; whether it
 * is small enough to word a claim around is C9's.
 */

import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  decodePng,
  extractSilhouette,
  interiorLevel,
  oklabDeltaE,
  parseProfileKey,
  silhouetteArea,
  ssim,
  type CalibrationImage,
  type Silhouette,
} from "../src/index";
import { componentRegionFor, readSceneGeometry } from "./scene-geometry";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const REFERENCE = resolve(REPO_ROOT, "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

/** The same detection threshold `compare` defaults to, so the masks agree. */
const SILHOUETTE_THRESHOLD = 0.02;

interface SceneEntry {
  readonly id: string;
  readonly background: string;
}

interface FixtureEntry {
  readonly sceneId: string;
  readonly file: string;
  readonly fixtureSet: string;
}

interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly {
    readonly profileKey: string;
    readonly colorScheme: "light" | "dark";
    readonly fixtures: readonly FixtureEntry[];
  }[];
}

function readJson<T>(path: string): T {
  if (!existsSync(path)) throw new Error(`tier-delta: ${path} does not exist`);
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function load(path: string): CalibrationImage {
  return decodePng(readFileSync(path));
}

interface Row {
  readonly profileKey: string;
  readonly sceneId: string;
  readonly fixtureSet: string;
  readonly interiorGpu: number;
  readonly interiorCss: number;
  readonly ssimBetweenTiers: number;
  readonly deltaEBetweenTiers: number;
  readonly deltaEGpuVsNative: number;
  readonly deltaECssVsNative: number;
}

function main(): void {
  const argv = process.argv.slice(2);
  const flag = (name: string): string | undefined => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const list = (name: string): readonly string[] | undefined => {
    const raw = flag(name);
    return raw === undefined ? undefined : raw.split(",").map((s) => s.trim()).filter(Boolean);
  };
  const scenes = list("scene");
  const profileKeys = list("profile");
  const capturesRoot = resolve(PACKAGE_ROOT, flag("captures") ?? "web-captures");
  /**
   * The suffix `compare --web-accessibility` gave a profile's capture tree, for
   * reading back a non-default accessibility run. Passed rather than derived:
   * this CLI reads captures off disk and has no opinion about which web-side
   * accessibility state produced them.
   */
  const variantSuffix = flag("variant") ?? "";

  const spec = readJson<{ readonly scenes: readonly SceneEntry[] }>(resolve(REFERENCE, "scenes.json"));
  const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
  const geometry = readSceneGeometry(REFERENCE);

  const rows: Row[] = [];
  const skipped: string[] = [];

  for (const profile of manifest.profiles) {
    if (profileKeys !== undefined && !profileKeys.includes(profile.profileKey)) continue;
    for (const fixture of profile.fixtures) {
      if (scenes !== undefined && !scenes.includes(fixture.sceneId)) continue;

      // Keyed by profile key, exactly as `compare` writes them (see its
      // captureDirFor): every profile shares the same scene ids, so anything
      // narrower would pair one profile's GPU capture with another's CSS one.
      const directory = resolve(
        capturesRoot,
        `${profile.profileKey}${variantSuffix}`,
        fixture.sceneId,
      );
      const gpuPath = resolve(directory, `${fixture.sceneId}__webgpu.png`);
      const cssPath = resolve(directory, `${fixture.sceneId}__css.png`);
      if (!existsSync(gpuPath) || !existsSync(cssPath)) {
        // A scene captured on one tier only is not a coherence data point, and
        // guessing the other half from the same tier would be measuring nothing.
        skipped.push(
          `${profile.profileKey} / ${fixture.sceneId}: needs both tiers on disk ` +
            `(${existsSync(gpuPath) ? "css" : "webgpu"} capture missing)`,
        );
        continue;
      }

      const scene = spec.scenes.find((entry) => entry.id === fixture.sceneId);
      // Scaled key first (schema-2 merged manifests), bare name as the schema-1 fallback.
      const scaleToken = /-(\d+)x-/.exec(profile.profileKey)?.[1] ?? "1";
      const backgroundFile =
        scene === undefined
          ? undefined
          : (manifest.backgrounds[`${scene.background}@${scaleToken}x`] ??
             manifest.backgrounds[scene.background]);
      if (backgroundFile === undefined) {
        skipped.push(`${profile.profileKey} / ${fixture.sceneId}: no background on record`);
        continue;
      }

      const gpu = load(gpuPath);
      const css = load(cssPath);
      const native = load(resolve(FIXTURES, fixture.file));
      const background = load(resolve(FIXTURES, backgroundFile));

      /*
       * The NATIVE silhouette masks both interiors, which is the same choice
       * `measure` makes and for the same reason: two different masks would let
       * the two tiers report levels over different pixel sets, and the whole
       * question is what each tier does over the *same* region. It also keeps
       * each side's shadow out of the level, so the interior columns compare
       * material to material.
       *
       * Bounded to the declared component region (schema 5), for the reason the
       * whole instrument now is: differencing against the backdrop finds the
       * shadow as well as the component, and an interior level averaged over
       * half-shadowed backdrop is not an interior level.
       */
      const scale = parseProfileKey(profile.profileKey)?.scale;
      if (scale === undefined) {
        skipped.push(`${profile.profileKey}: not a profile key, so no backing scale to place the region at`);
        continue;
      }
      const region = componentRegionFor(geometry, fixture.sceneId, {
        scale,
        width: native.width,
        height: native.height,
      });
      const interior: Silhouette = extractSilhouette(native, {
        kind: "luminance-delta",
        background,
        threshold: SILHOUETTE_THRESHOLD,
        region: region.silhouette,
      });
      if (silhouetteArea(interior) === 0) {
        // Real and informative: over a solid backdrop of its own tone the
        // reference is within 0.02 of it, so there is no interior to sample.
        skipped.push(
          `${profile.profileKey} / ${fixture.sceneId}: the native silhouette is empty at ` +
            `threshold ${SILHOUETTE_THRESHOLD}, so no interior level exists on either tier`,
        );
        continue;
      }

      rows.push({
        profileKey: profile.profileKey,
        sceneId: fixture.sceneId,
        fixtureSet: fixture.fixtureSet,
        interiorGpu: interiorLevel(gpu, { interior }).mean,
        interiorCss: interiorLevel(css, { interior }).mean,
        ssimBetweenTiers: ssim(gpu, css).mean,
        deltaEBetweenTiers: oklabDeltaE(gpu, css).mean,
        deltaEGpuVsNative: oklabDeltaE(native, gpu).mean,
        deltaECssVsNative: oklabDeltaE(native, css).mean,
      });
    }
  }

  const say = (line: string): void => void process.stdout.write(`${line}\n`);
  if (rows.length === 0) {
    say("tier-delta: no scene had captures on both tiers. Run `compare` twice, once per --renderer.");
    for (const note of skipped) say(`  skipped — ${note}`);
    process.exitCode = 1;
    return;
  }

  say("");
  say("web-vs-web: how differently the two tiers draw the same scene. No fixture in the first four columns.");
  say("");
  say(
    "set          profile                       scene                                        interior gpu/css   ratio    SSIM     dE(tiers)   dE vs native gpu/css",
  );
  say("-".repeat(172));
  for (const row of rows.sort(
    (a, b) => a.profileKey.localeCompare(b.profileKey) || a.sceneId.localeCompare(b.sceneId),
  )) {
    const ratio = row.interiorCss === 0 ? Number.POSITIVE_INFINITY : row.interiorGpu / row.interiorCss;
    say(
      [
        row.fixtureSet.padEnd(12),
        row.profileKey.replace(/^apple-macos-[\d.]+-/, "").padEnd(29),
        row.sceneId.padEnd(44),
        `${row.interiorGpu.toFixed(4)}/${row.interiorCss.toFixed(4)}`.padStart(15),
        ratio.toFixed(3).padStart(8),
        row.ssimBetweenTiers.toFixed(4).padStart(8),
        row.deltaEBetweenTiers.toFixed(5).padStart(11),
        `${row.deltaEGpuVsNative.toFixed(4)}/${row.deltaECssVsNative.toFixed(4)}`.padStart(20),
      ].join(" "),
    );
  }

  const mean = (values: readonly number[]): number => values.reduce((a, b) => a + b, 0) / values.length;
  const worst = (values: readonly number[], pick: "min" | "max"): number =>
    pick === "min" ? Math.min(...values) : Math.max(...values);

  /*
   * The interior ratio is the headline: it is the quantity the gap was in, and
   * the one a reader can restate as "the CSS tier is N× as transparent".
   *
   * Its worst case is the largest DEPARTURE FROM ONE in either direction, not the
   * largest ratio. Reporting `max` alone hid every cell where the CSS tier had
   * become the more opaque of the two — which after tuning is most of them, so
   * the honest worst case was being understated. The two directions are also
   * reported separately, because "the fallback is heavier" and "the fallback is
   * lighter" are different things for a reader to see on a demotion.
   */
  const ratios = rows.map((row) => row.interiorGpu / row.interiorCss);
  const departures = ratios.map((ratio) => Math.abs(ratio - 1));
  say("");
  say(
    `n=${rows.length}  interior ratio gpu/css mean ${mean(ratios).toFixed(3)} worst departure ` +
      `${worst(departures, "max").toFixed(3)} (range ${worst(ratios, "min").toFixed(3)}…` +
      `${worst(ratios, "max").toFixed(3)})   ` +
      `cross-tier SSIM mean ${mean(rows.map((r) => r.ssimBetweenTiers)).toFixed(4)} worst ` +
      `${worst(rows.map((r) => r.ssimBetweenTiers), "min").toFixed(4)}   ` +
      `cross-tier dE mean ${mean(rows.map((r) => r.deltaEBetweenTiers)).toFixed(5)} worst ` +
      `${worst(rows.map((r) => r.deltaEBetweenTiers), "max").toFixed(5)}`,
  );
  say(
    `        against the reference: dE mean gpu ${mean(rows.map((r) => r.deltaEGpuVsNative)).toFixed(5)} / ` +
      `css ${mean(rows.map((r) => r.deltaECssVsNative)).toFixed(5)} — coherence bought by moving both ` +
      `tiers away from Apple would show here.`,
  );

  if (skipped.length > 0) {
    say("");
    say(`── ${skipped.length} scene(s) not measured ────────────`);
    for (const note of skipped) say(`  ${note}`);
  }
}

try {
  main();
} catch (error) {
  process.stderr.write(`tier-delta: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}
