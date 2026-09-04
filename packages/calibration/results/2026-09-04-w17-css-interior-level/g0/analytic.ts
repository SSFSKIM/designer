/**
 * W17 G0 (b) — the analytic composite, computed from the profile through `optics.ts`'s own
 * functions and compared with what the shader draws when all four terms are declined.
 *
 * The all-declined render is the shader with its lens, its ambient rim, its highlight and the outer
 * shadow's lift stood down. What is left is the body: the blurred backdrop lerped toward the
 * adapted tint in linear light, with the inner shadow on top of it. If the analytic model is the
 * shader's, the model's mean and that render's interior mean are the same number, and (a)'s
 * attribution can be read as an excess over a quantity the CSS tier can compute. If they are not,
 * the difference is the part of the body this wave's conversion cannot state, and it has to be
 * named rather than folded into the excess.
 *
 * ## The model, term for term
 *
 * The chain is `root.ts`'s, not a restatement of it: `sourceOptics` resolves the profile's optics,
 * `sizeThickness` the size law's factor from the surface's short span, `backdropToneAdaptation` the
 * collapse, `toneRespondedSourceOptics` the W9 response solve, `adaptedSourceOptics` the collapse's
 * (colour, alpha) pair and `sizeOcclusionAlphaAt` the size law's occlusion. The composite is then
 *
 *     mean = (1 − α) · b + α · L(tint)
 *
 * in linear light, with `L` Rec. 709 luminance — the renderer's own lerp, at the group's level.
 *
 * ## The two backdrop levels, and which is which
 *
 * There are two distinct backdrop quantities and conflating them is the model's easiest mistake.
 *
 *  - **The group's sampled tone** drives the response solve and the collapse. It is one number per
 *    backdrop SOURCE, taken over the whole texture, and it comes in the two spaces
 *    `BackdropToneSample` carries: `luminance`, the ENCODED-space mean decoded once, which is what
 *    the response curve's input is; and `linearLuminance`, the linear mean, which is what the
 *    collapse converges onto. This script recomputes both from the fixture background the scene
 *    declares, exactly as `sampleBackdropTone` does — alpha-weighted, both means accumulated in one
 *    pass — with one difference stated rather than hidden: the browser draws the texture down to
 *    `SAMPLE_EXTENT` = 512 on its longest edge first, and this reads every pixel. A box average of
 *    box averages is the same average up to rounding, and the 1x backgrounds are 320 × 200 and are
 *    not downsampled at all, so the two agree exactly there and to rounding at 2x.
 *  - **The level the lerp runs against** is what is behind the SURFACE, which is neither of those:
 *    it is the blurred backdrop under the silhouette. The harness already measures the unblurred
 *    form of it per cell as `material.interiorMeanBackdrop` — `interiorLevel` of the background
 *    image over the same native silhouette the web reading uses — so that is what this script
 *    lerps against, and the group-sampled linear mean is reported beside it so the difference is
 *    visible on the cells where the two part company (a photo, where the surface does not sit over
 *    an average patch of its own backdrop).
 *
 * ## What the model deliberately omits
 *
 * The inner shadow (`shadowAlpha`, `shadowDepth`) is in the shader and is not one of the four
 * declined terms, so it is in the all-declined render and not in this model. It is a multiplicative
 * darkening concentrated near the contour. If the residual comes out negative and largest on the
 * thin spans, that is the shape it would have, and §2 of the findings says so with the number
 * rather than leaving the reader to infer it.
 *
 * Usage: `npx tsx analytic.ts <matrixDir> <captureRoot> <outJson>`, from `packages/calibration`.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { PNG } from "pngjs";

import {
  adaptedSourceOptics,
  backdropToneAdaptation,
  backdropToneUnderPolicy,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  resolvedTintShade,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sourceOptics,
  sourceSize,
  toneRespondedSourceOptics,
} from "@vitreajs/vitrea-web";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const decode = (e: number): number => (e <= 0.04045 ? e / 12.92 : ((e + 0.055) / 1.055) ** 2.4);
const luma = (rgb: readonly [number, number, number]): number =>
  0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];

/** `sampleBackdropTone`'s two means, over a fixture background read at full resolution. */
function toneOf(path: string): { rgb: [number, number, number]; luminance: number; linearLuminance: number } {
  const png = PNG.sync.read(readFileSync(path));
  let r = 0, g = 0, b = 0, er = 0, eg = 0, eb = 0, weight = 0;
  for (let i = 0; i < png.data.length; i += 4) {
    const a = (png.data[i + 3] as number) / 255;
    if (a <= 0) continue;
    const pr = (png.data[i] as number) / 255;
    const pg = (png.data[i + 1] as number) / 255;
    const pb = (png.data[i + 2] as number) / 255;
    er += pr * a; eg += pg * a; eb += pb * a;
    r += decode(pr) * a; g += decode(pg) * a; b += decode(pb) * a;
    weight += a;
  }
  const rgb: [number, number, number] = [r / weight, g / weight, b / weight];
  const level: [number, number, number] = [decode(er / weight), decode(eg / weight), decode(eb / weight)];
  return { rgb, luminance: luma(level), linearLuminance: luma(rgb) };
}

interface Cell {
  readonly tier: string;
  readonly key: { readonly profileKey: string; readonly sceneId: string };
  readonly material?: {
    readonly interiorMeanWeb: { readonly value: number };
    readonly interiorMeanBackdrop: { readonly value: number };
  };
}

const [, , matrixDir, captureRoot, outJson] = process.argv;
if (matrixDir === undefined || captureRoot === undefined || outJson === undefined) {
  throw new Error("usage: analytic.ts <matrixDir> <captureRoot> <outJson>");
}

const read = (name: string): Map<string, Cell> => {
  const cells = (JSON.parse(readFileSync(resolve(matrixDir, `${name}.json`), "utf8")) as {
    cells: Cell[];
  }).cells;
  const out = new Map<string, Cell>();
  for (const cell of cells) {
    if (cell.tier !== "texture") continue;
    out.set(`${cell.key.profileKey}|${cell.key.sceneId}`, cell);
  }
  return out;
};

const declined = read("all-declined");
const manifest = JSON.parse(readFileSync(resolve(FIXTURES, "manifest.json"), "utf8")) as {
  backgrounds: Record<string, string>;
  profiles: { profileKey: string; display: { actualBackingScale: number } }[];
};
const scenes = JSON.parse(readFileSync(resolve(REFERENCE, "scenes.json"), "utf8")) as {
  scenes: { id: string; background: string }[];
};

/** The renderer patch a profile was rendered under — light document for light, dark for dark. */
const patchOf = (profileKey: string): Record<string, unknown> => {
  const scheme = profileKey.includes("-dark-") ? "dark" : "light";
  const document = JSON.parse(
    readFileSync(resolve(PACKAGE_ROOT, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`), "utf8"),
  ) as { patch: Record<string, unknown> };
  return document.patch;
};

const NOMINAL = {
  glass: "material",
  frost: "nominal",
  refraction: "nominal",
  occlusion: "nominal",
  border: "nominal",
  ambientTint: "nominal",
  foreground: "adaptive",
} as const;

const toneCache = new Map<string, ReturnType<typeof toneOf>>();
const rows: unknown[] = [];

for (const [key, cell] of [...declined].sort(([a], [b]) => a.localeCompare(b))) {
  if (cell.material === undefined) continue;
  const { profileKey, sceneId } = cell.key;
  const scene = scenes.scenes.find((entry) => entry.id === sceneId);
  const profile = manifest.profiles.find((entry) => entry.profileKey === profileKey);
  if (scene === undefined || profile === undefined) continue;
  const scale = profile.display.actualBackingScale;

  const backgroundFile = manifest.backgrounds[`${scene.background}@${scale}x`];
  if (backgroundFile === undefined) continue;
  let tone = toneCache.get(backgroundFile);
  if (tone === undefined) {
    tone = toneOf(resolve(FIXTURES, backgroundFile));
    toneCache.set(backgroundFile, tone);
  }

  // The surface's own box, off the capture's report — the same measured border box `root.ts` reads
  // the size law from, in CSS px.
  const report = JSON.parse(
    readFileSync(resolve(captureRoot, "all-declined", profileKey, sceneId, "report__webgpu.json"), "utf8"),
  ) as { page: { surfaces: { radius: number; bounds: { width: number; height: number } }[] } };
  const surfaces = report.page.surfaces;
  const bounds = surfaces[surfaces.length - 1]!.bounds;
  const radius = surfaces[surfaces.length - 1]!.radius;
  const span = Math.min(bounds.width, bounds.height);

  const patch = patchOf(profileKey) as never;
  const size = sourceSize(patch);
  const shade = resolvedTintShade(patch);
  const toneConstants = resolvedBackdropTone(patch);
  const response = resolvedBackdropToneResponse(patch);
  const gpu = sourceOptics(patch).regular;

  const thickness = sizeThickness(span, size);
  /*
   * The size law's occlusion, applied in the SHADER's order as well as the tier's.
   *
   * `root.ts` runs `sizeOcclusionAlphaAt` LAST, on the alpha that `adaptedSourceOptics` returned;
   * the shader runs it FIRST — `sizedAlpha = tint.w + size.y * sizeK * (1 - tint.w)` is computed
   * before the W9 response solve, and the solve then shifts the neutral so that the composite AT
   * THAT ALPHA lands on the response. The two orders are not the same composite: the solve's whole
   * purpose is to land the mean on `R`, and a solve run at 0.46 followed by a raise to 0.487 lands
   * the mean above `R` by the raise times the tint's excess over the backdrop. Both are computed
   * here so the difference is a reading rather than an argument.
   */
  const shaderOrderStart = { ...gpu, tintAlpha: sizeOcclusionAlphaAt(gpu.tintAlpha, thickness, size) };
  const policyStrength = backdropToneUnderPolicy(NOMINAL as never, shade, size.refractionScale);
  const adaptation = backdropToneAdaptation(tone.luminance, thickness, toneConstants) * policyStrength;
  const responded = toneRespondedSourceOptics(
    gpu,
    tone,
    thickness,
    adaptation,
    (policyStrength >= 0.999 ? 1 : 0) * Math.min(1, Math.max(0, toneConstants.max)),
    response,
  );
  const adapted = adaptedSourceOptics(responded, tone.rgb, adaptation);
  const alpha = sizeOcclusionAlphaAt(adapted.tintAlpha, thickness, size);

  const shaderResponded = toneRespondedSourceOptics(
    shaderOrderStart,
    tone,
    thickness,
    adaptation,
    (policyStrength >= 0.999 ? 1 : 0) * Math.min(1, Math.max(0, toneConstants.max)),
    response,
  );
  const shaderAdapted = adaptedSourceOptics(shaderResponded, tone.rgb, adaptation);

  /*
   * The inner shadow, which is in the all-declined render and in neither composite above.
   *
   * `shadowKeep = 1 - shadowProfile * shadowDepth * shadowAlpha * present` with
   * `shadowProfile = (1 - clamp(-d / shadowLensDepth))^2` and
   * `shadowLensDepth = min(thickness * (1 + (lensSizeGainMax - 1) * sizeK), span / 2)` — a
   * multiplicative darkening whose area mean over a convex silhouette is the co-area integral
   * `(1/A) * int_0^D (1 - u/D)^2 * P(u) du` with `P(u)` the inward offset's perimeter. For a
   * rounded rectangle of box W x H and radius r the straight runs do not shorten under an inward
   * offset and only the corner arcs do, so `P(u) = 2(W - 2r) + 2(H - 2r) + 2*pi*(r - u)`, exactly.
   * The authored thickness is `DEFAULT_HOST_SHAPE.thickness` = 8 CSS px, which the calibration
   * pages never override.
   */
  const depth = Math.min(8 * (1 + (2.6 - 1) * thickness), span / 2);
  const straight = 2 * (bounds.width - 2 * radius) + 2 * (bounds.height - 2 * radius);
  const area = bounds.width * bounds.height - (4 - Math.PI) * radius * radius;
  const profileMean =
    (straight * (depth / 3) + 2 * Math.PI * (radius * (depth / 3) - depth * depth / 12)) / area;
  const innerShadowKeep = 1 - Math.max(0, profileMean) * 0.35 * 0.05;

  const backdropUnderSurface = cell.material.interiorMeanBackdrop.value;
  const composite = (b: number): number => (1 - alpha) * b + alpha * luma(adapted.tint);
  const shaderComposite = (b: number): number =>
    (1 - shaderAdapted.tintAlpha) * b + shaderAdapted.tintAlpha * luma(shaderAdapted.tint);
  const rendered = cell.material.interiorMeanWeb.value;

  rows.push({
    profileKey,
    sceneId,
    span,
    thickness,
    adaptation,
    tintAlpha: alpha,
    tintLuma: luma(adapted.tint),
    toneEncodedMeanDecoded: tone.luminance,
    toneLinearMean: tone.linearLuminance,
    backdropUnderSurface,
    allDeclinedRendered: rendered,
    analyticAtSurfaceBackdrop: composite(backdropUnderSurface),
    analyticAtGroupLinearMean: composite(tone.linearLuminance),
    residualAtSurfaceBackdrop: composite(backdropUnderSurface) - rendered,
    residualAtGroupLinearMean: composite(tone.linearLuminance) - rendered,
    shaderOrderAlpha: shaderAdapted.tintAlpha,
    shaderOrderTintLuma: luma(shaderAdapted.tint),
    shaderOrderAnalytic: shaderComposite(backdropUnderSurface),
    shaderOrderResidual: shaderComposite(backdropUnderSurface) - rendered,
    innerShadowKeep,
    shaderOrderWithInnerShadow: shaderComposite(backdropUnderSurface) * innerShadowKeep,
    shaderOrderWithInnerShadowResidual:
      shaderComposite(backdropUnderSurface) * innerShadowKeep - rendered,
    surfaceCount: surfaces.length,
    radius,
  });
  void key;
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 1)}\n`);
process.stdout.write(`${rows.length} cells -> ${outJson}\n`);
