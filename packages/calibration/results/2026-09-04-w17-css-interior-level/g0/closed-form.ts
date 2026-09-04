/**
 * W17 G0 (c) — the closed form for each declined term, derived from the profile's numbers and the
 * surface's geometry, and its residual against the measured attribution of (a).
 *
 * A lookup table of measured excesses is not admissible (the charter's binding K5 clause), so every
 * number below is computed from `DEFAULT_MATERIAL_PROFILE` as the profile document patches it and
 * from the surface's own box and radius. The measurement in (a) validates it; it does not supply it.
 *
 * ## The three terms that have a closed form, and the one that does not
 *
 * **The rim's ambient term.** The shader adds `rw(d) * rimAlpha * present` in linear light, with
 * `rw(d) = clamp(1 - |d| / rimWidth, 0, 1)^2` and `d` the signed distance in CSS px. Added light
 * survives the encode and the reader decodes it back, so the term's contribution to the interior
 * mean is the area mean of that expression over the reader's mask:
 *
 *     rim = rimAlpha * present * (1 / |M|) * sum_{p in M} rw(d(p))^2
 *
 * evaluated on the DEVICE pixel grid rather than as a continuous integral, because a 1.5 CSS px
 * band is one and a half samples wide at dpr 1 and the difference between the integral and the sum
 * is 10 % of the term. `present = 1 - toneAdapt`, the collapse's own fade, which is zero on every
 * standard-profile cell of this bed except where the backdrop is dark enough to collapse.
 *
 * **The highlight.** The same band, lit: `rw(d) * spec * present` with
 * `spec = clamp(n̂ · lightDirection, 0, 1)^specularPower * specularGain` and `n̂` the field's
 * gradient, which for a rounded rectangle is the outward normal of the nearest boundary point —
 * axis-aligned on the straight runs and radial on the corner arcs. Same sum, same mask.
 *
 * **The outer shadow's lift.** The shader adds it as `liftEncoded * (1 - coverage)`, so its closed
 * form inside the silhouette is exactly zero, and what (a) measures is the anti-aliased contour
 * ring where the coverage is not 1. The prediction is 0 and the residual is that ring.
 *
 * **The lens.** The lens is a displacement, not light: it re-samples the blurred backdrop at
 * `x - n̂ * D(d)` and adds nothing of its own. On a backdrop that is statistically homogeneous over
 * the band — every checkerboard cell of this bed — the warp moves the mean by zero to first order,
 * and what is left is the second-order term in the backdrop's curvature and the Jacobian of the
 * warp over the band. This script therefore predicts **zero** for the lens and records the measured
 * departure as the derivation's own residual rather than fitting a coefficient to it: the term is
 * −0.0024 … +0.0036 across the whole bed, which is inside the charter's 0.01 by itself, and a
 * closed form for it needs the renderer's own two-component body, which is W16's measurement and
 * not this profile's number.
 *
 * ## The quantisation, modelled rather than tolerated
 *
 * The measured differences are between two eight-bit captures. A term of 0.002 in linear light over
 * a body at 0.69 is about half of one code, so rounding does not average out — it truncates the
 * band's tail, where `rw` is small. So each term is reported twice: the area mean in linear light
 * (the closed form as such), and the same term added to the all-declined capture, encoded, rounded
 * to eight bits, decoded and re-read (the closed form as the raster carries it). The second is what
 * (a) can be compared with; the first is what the derivation says.
 *
 * Usage: `npx tsx closed-form.ts <matrixDir> <captureRoot> <outJson>`, from `packages/calibration`.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
  DEFAULT_SILHOUETTE_THRESHOLD,
} from "../../../cli/measure";
import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { componentRegion, decodePng, extractSilhouette, linearLuminance } from "../../../src/index";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "@vitrea/renderer-webgpu";
import {
  backdropToneAdaptation,
  backdropToneUnderPolicy,
  resolvedBackdropTone,
  resolvedTintShade,
  sizeThickness,
  sourceOptics,
  sourceSize,
} from "@vitreajs/vitrea-web";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const encode = (l: number): number =>
  l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;
const decode = (e: number): number => (e <= 0.04045 ? e / 12.92 : ((e + 0.055) / 1.055) ** 2.4);
const clamp01 = (x: number): number => Math.min(1, Math.max(0, x));

/*
 * The rim's width, its ambient alpha, the specular exponent and gain, and the light direction come
 * from the RENDERER's resolved profile rather than from `platform-web`'s mirror: the mirror carries
 * only the four fields the CSS tier converts (`MaterialSourceOptics`), and `rimWidth`,
 * `specularPower` and `specularGain` are not among them — they are the band's own geometry, which
 * this tier draws as a 1 px border and never converts. Reading them off `withMaterialOverrides` is
 * reading the same resolved material the shader was handed.
 */

const [, , matrixDir, captureRoot, outJson] = process.argv;
if (matrixDir === undefined || captureRoot === undefined || outJson === undefined) {
  throw new Error("usage: closed-form.ts <matrixDir> <captureRoot> <outJson>");
}

interface Cell {
  readonly tier: string;
  readonly key: { readonly profileKey: string; readonly sceneId: string };
  readonly material?: { readonly interiorMeanWeb: { readonly value: number } };
}
const readMatrix = (name: string): Map<string, Cell> => {
  const cells = (JSON.parse(readFileSync(resolve(matrixDir, `${name}.json`), "utf8")) as {
    cells: Cell[];
  }).cells;
  const out = new Map<string, Cell>();
  for (const cell of cells) if (cell.tier === "texture") out.set(`${cell.key.profileKey}|${cell.key.sceneId}`, cell);
  return out;
};
const CONFIGS = ["default", "no-lens", "no-rim", "no-highlight", "no-lift", "all-declined"] as const;
const matrices = Object.fromEntries(CONFIGS.map((name) => [name, readMatrix(name)])) as Record<
  (typeof CONFIGS)[number],
  Map<string, Cell>
>;

const manifest = JSON.parse(readFileSync(resolve(FIXTURES, "manifest.json"), "utf8")) as {
  backgrounds: Record<string, string>;
  profiles: {
    profileKey: string;
    display: { actualBackingScale: number };
    fixtures: { sceneId: string; file: string }[];
  }[];
};
const scenes = JSON.parse(readFileSync(resolve(REFERENCE, "scenes.json"), "utf8")) as {
  scenes: { id: string; background: string }[];
};
const geometry = readSceneGeometry(REFERENCE);

const patchOf = (profileKey: string): never => {
  const scheme = profileKey.includes("-dark-") ? "dark" : "light";
  return (
    JSON.parse(
      readFileSync(resolve(PACKAGE_ROOT, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`), "utf8"),
    ) as { patch: unknown }
  ).patch as never;
};

const NOMINAL = {
  glass: "material", frost: "nominal", refraction: "nominal", occlusion: "nominal",
  border: "nominal", ambientTint: "nominal", foreground: "adaptive",
} as const;

/** The rounded rectangle's signed distance in CSS px, and its outward normal. */
function rrect(
  x: number, y: number, cx: number, cy: number, hw: number, hh: number, r: number,
): { d: number; nx: number; ny: number } {
  const qx = Math.abs(x - cx) - (hw - r);
  const qy = Math.abs(y - cy) - (hh - r);
  const mx = Math.max(qx, 0);
  const my = Math.max(qy, 0);
  const outside = Math.hypot(mx, my);
  const d = outside + Math.min(Math.max(qx, qy), 0) - r;
  // The gradient of the same expression, carried back through the two absolute values.
  let gx: number;
  let gy: number;
  if (qx > 0 && qy > 0) {
    gx = mx / Math.max(outside, 1e-6);
    gy = my / Math.max(outside, 1e-6);
  } else if (qx > qy) {
    gx = 1; gy = 0;
  } else {
    gx = 0; gy = 1;
  }
  const sx = x >= cx ? 1 : -1;
  const sy = y >= cy ? 1 : -1;
  const nx = gx * sx;
  const ny = gy * sy;
  const len = Math.hypot(nx, ny) || 1;
  return { d, nx: nx / len, ny: ny / len };
}

const rows: unknown[] = [];
const skipped: { key: string; why: string }[] = [];

for (const key of [...matrices["all-declined"].keys()].sort()) {
  const [profileKey, sceneId] = key.split("|") as [string, string];
  if (sceneId.includes("-tint")) {
    skipped.push({ key, why: "author tint (W10) — this model does not carry the seed's layer" });
    continue;
  }
  const declinedCell = matrices["all-declined"].get(key);
  if (declinedCell?.material === undefined) {
    skipped.push({ key, why: "no material axis on this cell" });
    continue;
  }
  const scene = scenes.scenes.find((entry) => entry.id === sceneId);
  const profile = manifest.profiles.find((entry) => entry.profileKey === profileKey);
  if (scene === undefined || profile === undefined) continue;
  const scale = profile.display.actualBackingScale;
  const fixture = profile.fixtures.find((entry) => entry.sceneId === sceneId);
  const backgroundFile = manifest.backgrounds[`${scene.background}@${scale}x`];
  if (fixture === undefined || backgroundFile === undefined) continue;

  const report = JSON.parse(
    readFileSync(resolve(captureRoot, "all-declined", profileKey, sceneId, "report__webgpu.json"), "utf8"),
  ) as {
    page: {
      surfaces: { family: string; radius: number; bounds: { x: number; y: number; width: number; height: number } }[];
    };
  };
  if (report.page.surfaces.length !== 1) {
    skipped.push({ key, why: `${report.page.surfaces.length} surfaces — the band is a union, not one contour` });
    continue;
  }
  const surface = report.page.surfaces[0]!;
  const { x, y, width, height } = surface.bounds;
  const radius = Math.min(surface.radius, Math.min(width, height) / 2);
  const span = Math.min(width, height);

  // The reader's mask: the native silhouette, exactly as `measureCell` builds it.
  const nativeImage = decodePng(readFileSync(resolve(FIXTURES, fixture.file)));
  const backgroundImage = decodePng(readFileSync(resolve(FIXTURES, backgroundFile)));
  const region = componentRegion(declaredComponentOf(geometry, sceneId), {
    canvas: geometry.canvas, scale, width: nativeImage.width, height: nativeImage.height,
  });
  const mask = extractSilhouette(nativeImage, {
    kind: "luminance-delta",
    background: backgroundImage,
    threshold: DEFAULT_SILHOUETTE_THRESHOLD,
    chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
    region: region.silhouette,
  }).mask;

  // The profile's own constants, and the collapse's fade.
  const patch = patchOf(profileKey);
  const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
  const optics = resolved.optics.regular;
  const LIGHT = resolved.lightDirection;
  const size = sourceSize(patch);
  const shade = resolvedTintShade(patch);
  const toneConstants = resolvedBackdropTone(patch);
  const toneImage = decodePng(readFileSync(resolve(FIXTURES, backgroundFile)));
  // `BackdropToneSample.luminance` — the encoded-space mean, decoded once.
  let er = 0, eg = 0, eb = 0, weight = 0;
  for (let i = 0; i < toneImage.data.length; i += 4) {
    const a = (toneImage.data[i + 3] as number) / 255;
    if (a <= 0) continue;
    er += ((toneImage.data[i] as number) / 255) * a;
    eg += ((toneImage.data[i + 1] as number) / 255) * a;
    eb += ((toneImage.data[i + 2] as number) / 255) * a;
    weight += a;
  }
  const toneLuminance =
    0.2126 * decode(er / weight) + 0.7152 * decode(eg / weight) + 0.0722 * decode(eb / weight);
  const thickness = sizeThickness(span, size);
  const policyStrength = backdropToneUnderPolicy(NOMINAL as never, shade, size.refractionScale);
  const toneAdapt = backdropToneAdaptation(toneLuminance, thickness, toneConstants) * policyStrength;
  const present = 1 - toneAdapt;

  // The two bands, summed over the reader's mask on the device grid.
  const capture = decodePng(readFileSync(
    resolve(captureRoot, "all-declined", profileKey, sceneId, `${sceneId}__webgpu.png`),
  ));
  const base = linearLuminance(capture);
  const cx = x + width / 2;
  const cy = y + height / 2;
  const hw = width / 2;
  const hh = height / 2;

  let count = 0;
  let rimSum = 0;
  let specSum = 0;
  let baseSum = 0;
  let rimQuantSum = 0;
  let specQuantSum = 0;
  for (let py = 0; py < capture.height; py += 1) {
    for (let px = 0; px < capture.width; px += 1) {
      const p = py * capture.width + px;
      if ((mask[p] ?? 0) === 0) continue;
      const { d, nx, ny } = rrect((px + 0.5) / scale, (py + 0.5) / scale, cx, cy, hw, hh, radius);
      const t = clamp01(1 - Math.abs(d) / Math.max(optics.rimWidth, 1e-4));
      const rw = t * t;
      const facing = clamp01(nx * LIGHT[0] + ny * LIGHT[1]);
      const spec = facing ** Math.max(optics.specularPower, 1e-3) * optics.specularGain;
      const rim = rw * optics.rimAlpha * present;
      const highlight = rw * spec * present;
      rimSum += rim;
      specSum += highlight;
      // The same light as the raster carries it: added to the drawn body, encoded, rounded to
      // eight bits, decoded, and differenced. `base[p]` is the all-declined capture's own linear
      // luminance at this pixel, which is the body the term would have been added to.
      const b = base[p] ?? 0;
      const round = (added: number): number =>
        decode(Math.round(encode(clamp01(b + added)) * 255) / 255) -
        decode(Math.round(encode(clamp01(b)) * 255) / 255);
      rimQuantSum += round(rim);
      specQuantSum += round(highlight);
      baseSum += b;
      count += 1;
    }
  }

  const value = (config: (typeof CONFIGS)[number]): number =>
    matrices[config].get(key)!.material!.interiorMeanWeb.value;
  const measured = {
    lens: value("default") - value("no-lens"),
    rim: value("default") - value("no-rim"),
    highlight: value("default") - value("no-highlight"),
    lift: value("default") - value("no-lift"),
    whole: value("default") - value("all-declined"),
  };
  const predicted = {
    lens: 0,
    rim: rimQuantSum / count,
    highlight: specQuantSum / count,
    lift: 0,
  };

  rows.push({
    profileKey, sceneId, span, radius, scale, toneAdapt, present,
    maskPixels: count,
    maskMeanFromCapture: baseSum / count,
    closedFormLinearLight: { rim: rimSum / count, highlight: specSum / count, lens: 0, lift: 0 },
    closedFormAsRastered: predicted,
    measured,
    residual: {
      lens: predicted.lens - measured.lens,
      rim: predicted.rim - measured.rim,
      highlight: predicted.highlight - measured.highlight,
      lift: predicted.lift - measured.lift,
    },
    predictedWhole: predicted.rim + predicted.highlight,
    residualWhole: predicted.rim + predicted.highlight - measured.whole,
  });
}

writeFileSync(outJson, `${JSON.stringify({ skipped, rows }, null, 1)}\n`);
process.stdout.write(`${rows.length} cells, ${skipped.length} skipped -> ${outJson}\n`);
