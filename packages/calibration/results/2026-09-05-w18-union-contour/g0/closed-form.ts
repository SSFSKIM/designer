/**
 * W18 G0 (d) — the closed forms, and their residuals per cell.
 *
 * (b) attributes the residual. This derives the attributed parts from the profile's own numbers and
 * the surface's own box, radius and neighbours, and records what each derivation misses.
 *
 * ## Part one — the shadow the tier samples through its own backdrop
 *
 * The decline in (b) reads the whole of the neighbours' term and a third to four fifths of the lone
 * box's onto one mechanism: the CSS tier draws the outer shadow as a `box-shadow` on the HOST, and
 * the host's own filter layers are its children, so the shadow is painted below them — and Chromium
 * samples a `backdrop-filter`'s backdrop over the region its kernel needs rather than over the
 * border box alone. The tier therefore blurs its own shadow, and its neighbours', into its own body.
 * The renderer does not: declining the shadow moves the GPU tier's interior by 0.00000 on every cell.
 *
 * The closed form is that statement evaluated. The page the tier's filter sees is the background
 * multiplied, in the encoded space a page composites in, by each host's shadow alpha —
 *
 *     E(P) = E(B) · Π_j (1 − a · C_j)
 *
 * with `a` the alpha `cssTierShadowAlpha` writes into the declaration and `C_j` the coverage of a
 * CSS box shadow: host j's border box grown by `spreadPx`, displaced by `offsetPx` down, blurred by
 * a Gaussian of standard deviation `sigmaPx` (CSS Backgrounds 3 defines the blur RADIUS as twice
 * that, which `cssShadowBlurRadius` is the reconciliation of), and not painted inside the casting
 * host's own border box. Every one of those numbers is the profile's, and the declaration string
 * this script reads them out of is `cssTierDeclarations`' own — not a second copy of the rule.
 *
 * That page is then put through the tier's own body — L1 at the sharp width, L2 at the heavy step
 * under the ramp's mask, the affine, the encode — and the same page WITHOUT the shadows through the
 * same chain. The difference of the two means over the surface's own mask is the prediction; the
 * measurement it is compared against is the CSS tier's default capture minus its `no-outer-shadow`
 * capture over that same mask, which is the same difference with the engine in place of the model.
 *
 * ## Part two — what the tier's per-surface terms do to the box
 *
 * M1 asks whether a term the tier carries as a function of the span is integrated per pixel over the
 * box by the renderer. Three candidates, and this reports all three on both boxes at both scales so
 * the doc can say which carries a box term and which does not: the band's derived light X
 * (`interiorBandLight`, already a co-area integral over the surface's own box and radius), the inner
 * shadow's keep (`interiorShadowKeep`, the same integral), and the depth ramp's area mean
 * (`scatterRampAreaMean`), which takes the extents and IGNORES the corners — on a circle the corners
 * are the whole surface. The exact co-area value of the ramp's mean over the rounded rectangle is
 * computed beside it, on the device grid, so the error the rectangle form carries is a number.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w18-union-contour/g0/closed-form.ts <scenesJson> <outJson>
 * Reads only committed fixtures and the profile's own functions; writes only the file it is given.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import {
  adaptedSourceOptics,
  backdropToneAdaptation,
  backdropToneUnderPolicy,
  cssTierDeclarations,
  innerShadowedSourceOptics,
  interiorBandLight,
  interiorShadowKeep,
  MATERIAL_OPTICS,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  resolvedTintShade,
  scatterRampAreaMean,
  scatterRampReachDevicePx,
  scatterDeepThickness,
  scatterRampStart,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sourceOptics,
  sourceSize,
  toneRespondedSourceOptics,
  type CssTierRamp,
  type InteriorSurfaceGeometry,
} from "@vitreajs/vitrea-web";
import { PNG } from "pngjs";

import { declaredComponentOf, readSceneGeometry } from "../../../cli/scene-geometry";
import { placeComponent, type PlacedShape } from "../../../src/index";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const FIXTURES = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple", "fixtures");

const [, , scenesJson, outJson] = process.argv;
if (scenesJson === undefined || outJson === undefined) {
  throw new Error("usage: closed-form.ts <scenesJson> <outJson>");
}

const encode = (l: number): number =>
  l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;
const decode = (e: number): number => (e <= 0.04045 ? e / 12.92 : ((e + 0.055) / 1.055) ** 2.4);
const clamp01 = (x: number): number => Math.min(1, Math.max(0, x));

/** A separable Gaussian at σ device px over one plane, edge-clamped. */
function blur(plane: Float64Array, width: number, height: number, sigma: number): Float64Array {
  if (sigma <= 1e-4) return plane;
  const radius = Math.max(1, Math.ceil(sigma * 3));
  const kernel = new Float64Array(radius * 2 + 1);
  let total = 0;
  for (let i = -radius; i <= radius; i += 1) {
    const value = Math.exp(-(i * i) / (2 * sigma * sigma));
    kernel[i + radius] = value;
    total += value;
  }
  for (let i = 0; i < kernel.length; i += 1) kernel[i]! /= total;

  const horizontal = new Float64Array(plane.length);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      let sum = 0;
      for (let i = -radius; i <= radius; i += 1) {
        sum += (plane[y * width + Math.min(width - 1, Math.max(0, x + i))] ?? 0) * kernel[i + radius]!;
      }
      horizontal[y * width + x] = sum;
    }
  }
  const vertical = new Float64Array(plane.length);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      let sum = 0;
      for (let i = -radius; i <= radius; i += 1) {
        sum += (horizontal[Math.min(height - 1, Math.max(0, y + i)) * width + x] ?? 0) * kernel[i + radius]!;
      }
      vertical[y * width + x] = sum;
    }
  }
  return vertical;
}

/** Signed distance to a placed rounded rectangle in device px, negative inside. */
function distanceTo(shape: PlacedShape, scale: number, x: number, y: number, grow = 0): number {
  const centreX = (shape.left + shape.width / 2) * scale;
  const centreY = (shape.top + shape.height / 2) * scale;
  const halfWidth = (shape.width / 2) * scale + grow;
  const halfHeight = (shape.height / 2) * scale + grow;
  const radius = Math.min(shape.radius * scale + grow, Math.min(halfWidth, halfHeight));
  const qx = Math.abs(x - centreX) - (halfWidth - radius);
  const qy = Math.abs(y - centreY) - (halfHeight - radius);
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius;
}

/** The ramp's share at an inward depth, restated from `css-tier-layers.ts`'s mask field. */
function maskShareAt(depthDevicePx: number, ramp: CssTierRamp): number {
  const reach = Math.max(ramp.reachDevicePx, 1e-6);
  const t = Math.min(Math.max(depthDevicePx, 0) / reach, 1);
  return ramp.deepShare + (ramp.contourShare - ramp.deepShare) * (1 - t);
}

/**
 * The interior composite the tier aims at, in the shader's own order — W17 G1's `residuals.ts`
 * routine, restated because it is the affine the body's output is put through and the shadow term
 * rides on its slope.
 */
function interiorOf(geometry: InteriorSurfaceGeometry, backdropLinear: number, backdropEncoded: number) {
  const base = sourceOptics().regular;
  const size = sourceSize();
  const span = Math.min(geometry.widthCssPx, geometry.heightCssPx);
  const thickness = sizeThickness(span, size);
  const sample = {
    rgb: [backdropLinear, backdropLinear, backdropLinear] as [number, number, number],
    luminance: backdropEncoded,
    linearLuminance: backdropLinear,
  };
  const occluded = { ...base, tintAlpha: sizeOcclusionAlphaAt(base.tintAlpha, thickness, size) };
  const toneConstants = resolvedBackdropTone();
  const strength = backdropToneUnderPolicy(
    NOMINAL_ACCESSIBILITY_POLICY.material,
    resolvedTintShade(),
    size.refractionScale,
  );
  const adaptation = backdropToneAdaptation(sample.luminance, thickness, toneConstants) * strength;
  const adapted = adaptedSourceOptics(
    toneRespondedSourceOptics(
      occluded,
      sample,
      thickness,
      adaptation,
      (strength >= 0.999 ? 1 : 0) * Math.min(1, Math.max(0, toneConstants.max)),
      resolvedBackdropToneResponse(),
    ),
    sample.rgb,
    adaptation,
  );
  const keep = interiorShadowKeep(base, geometry, thickness, 1 - adaptation);
  const shadowed = innerShadowedSourceOptics(adapted, keep);
  return {
    alpha: shadowed.tintAlpha,
    tint: shadowed.tint[1] as number,
    band: interiorBandLight(base, geometry, 1 - adaptation),
    keep,
    thickness,
  };
}

/** The `box-shadow` the tier declares, parsed out of its own declaration string. */
function shadowOf(render: { host: Record<string, string> }): {
  offsetPx: number;
  blurPx: number;
  spreadPx: number;
  alpha: number;
} | undefined {
  const declaration = render.host["box-shadow"];
  if (declaration === undefined || declaration === "none") return undefined;
  const numbers = declaration.match(/-?\d+(?:\.\d+)?/g);
  if (numbers === null || numbers.length < 8) {
    throw new Error(`closed-form: cannot read the tier's box-shadow "${declaration}"`);
  }
  return {
    offsetPx: Number(numbers[1]),
    blurPx: Number(numbers[2]),
    spreadPx: Number(numbers[3]),
    alpha: Number(numbers[7]),
  };
}

const geometryMatrix = readSceneGeometry(scenesJson);
const rows: unknown[] = [];

for (const scene of geometryMatrix.scenes) {
  const component = declaredComponentOf(geometryMatrix, scene.id);
  const placed = placeComponent(component, geometryMatrix.canvas);
  const backgroundId = scene.id.split("__")[0] as string;

  for (const scale of [1, 2] as const) {
    const png = PNG.sync.read(readFileSync(resolve(FIXTURES, `backgrounds/${backgroundId}@${scale}x.png`)));
    const { width, height } = png;
    // One luminance plane: the reading is a linear-luminance mean and the shadow, the tint and the
    // ramp are all achromatic, so the chromatic channels would carry the same difference.
    const background = new Float64Array(width * height);
    for (let i = 0; i < background.length; i += 1) {
      background[i] =
        0.2126 * decode((png.data[i * 4] ?? 0) / 255) +
        0.7152 * decode((png.data[i * 4 + 1] ?? 0) / 255) +
        0.0722 * decode((png.data[i * 4 + 2] ?? 0) / 255);
    }
    let backdropLinear = 0;
    for (const value of background) backdropLinear += value;
    backdropLinear /= background.length;
    let backdropEncoded = 0;
    for (let i = 0; i < background.length; i += 1) backdropEncoded += encode(background[i] ?? 0);
    backdropEncoded /= background.length;

    // Every host's declaration, resolved exactly as the runtime resolves it.
    const renders = placed.map((shape) =>
      cssTierDeclarations({
        radii: [shape.radius, shape.radius, shape.radius, shape.radius],
        optics: MATERIAL_OPTICS.regular,
        policy: NOMINAL_ACCESSIBILITY_POLICY,
        spanPx: Math.min(shape.width, shape.height),
        extentsCssPx: [shape.width, shape.height],
        devicePixelRatio: scale,
        backdropLuminance: backdropLinear,
        engine: { referenceFilterInBackdrop: true, maskOnBackdropFilter: "yes" },
      }),
    );

    // The page with every host's shadow on it, in the encoded space a page composites in.
    const shadowed = new Float64Array(background.length);
    for (let i = 0; i < shadowed.length; i += 1) shadowed[i] = encode(background[i] ?? 0);
    placed.forEach((shape, index) => {
      const shadow = shadowOf(renders[index] as { host: Record<string, string> });
      if (shadow === undefined) return;
      // The coverage: the box grown by the spread and displaced, blurred at the standard deviation
      // the CSS blur radius is twice of, then removed from inside the casting box.
      const coverage = new Float64Array(background.length);
      const displaced: PlacedShape = { ...shape, top: shape.top + shadow.offsetPx };
      for (let y = 0; y < height; y += 1) {
        for (let x = 0; x < width; x += 1) {
          coverage[y * width + x] =
            distanceTo(displaced, scale, x + 0.5, y + 0.5, shadow.spreadPx * scale) <= 0 ? 1 : 0;
        }
      }
      const blurred = blur(coverage, width, height, (shadow.blurPx / 2) * scale);
      for (let y = 0; y < height; y += 1) {
        for (let x = 0; x < width; x += 1) {
          const index2 = y * width + x;
          if (distanceTo(shape, scale, x + 0.5, y + 0.5) <= 0) continue; // clipped inside the caster
          shadowed[index2] = (shadowed[index2] ?? 0) * (1 - shadow.alpha * (blurred[index2] ?? 0));
        }
      }
    });
    const pageWith = new Float64Array(background.length);
    for (let i = 0; i < pageWith.length; i += 1) pageWith[i] = decode(clamp01(shadowed[i] ?? 0));

    placed.forEach((shape, index) => {
      const render = renders[index] as ReturnType<typeof cssTierDeclarations>;
      const body = render.body;
      const ramp = body.ramp as CssTierRamp | undefined;
      const interiorGeometry: InteriorSurfaceGeometry = {
        widthCssPx: shape.width,
        heightCssPx: shape.height,
        radiusCssPx: shape.radius,
        thicknessCssPx: 8,
      };
      const interior = interiorOf(interiorGeometry, backdropLinear, backdropEncoded);
      const slope = 1 - interior.alpha;
      const intercept = interior.alpha * interior.tint + interior.band;
      const affine = (b: number): number => clamp01(slope * b + intercept);

      const chain = (page: Float64Array): number => {
        const sharp = blur(page, width, height, body.sharpSigmaCssPx * scale);
        const heavy = blur(sharp, width, height, body.heavyStepSigmaCssPx * scale);
        let sum = 0;
        let count = 0;
        for (let y = 0; y < height; y += 1) {
          for (let x = 0; x < width; x += 1) {
            const depth = -distanceTo(shape, scale, x + 0.5, y + 0.5);
            if (depth < 0) continue;
            const i2 = y * width + x;
            const m = ramp === undefined ? body.flatShare : clamp01(maskShareAt(depth, ramp));
            sum += affine((1 - m) * (sharp[i2] ?? 0) + m * (heavy[i2] ?? 0));
            count += 1;
          }
        }
        return sum / count;
      };

      const withShadow = chain(pageWith);
      const withoutShadow = chain(background);

      // The depth ramp's area mean: what `optics.ts` carries (the extents, no corners) against the
      // exact co-area value over the rounded rectangle, evaluated on the device grid.
      const size = sourceSize();
      const span = Math.min(shape.width, shape.height);
      const deep = scatterDeepThickness(span, size, scale);
      const amplitude = Math.max(scatterRampStart(scale, size, span) - (1 - deep), 0);
      const reachCssPx = scatterRampReachDevicePx(scale, size) / Math.max(scale, 1e-3);
      let exact = 0;
      let exactCount = 0;
      for (let y = 0; y < height; y += 1) {
        for (let x = 0; x < width; x += 1) {
          const depth = -distanceTo(shape, scale, x + 0.5, y + 0.5) / scale;
          if (depth < 0) continue;
          exact += clamp01(deep - amplitude * Math.max(0, 1 - depth / Math.max(reachCssPx, 1e-6)));
          exactCount += 1;
        }
      }

      rows.push({
        scene: scene.id,
        dpr: scale,
        surface: index,
        box: [shape.width, shape.height],
        radiusCssPx: shape.radius,
        backdropLinear,
        shadow: shadowOf(render as { host: Record<string, string> }),
        body: {
          sharpSigmaCssPx: body.sharpSigmaCssPx,
          heavyStepSigmaCssPx: body.heavyStepSigmaCssPx,
          heavySigmaCssPx: body.heavySigmaCssPx,
          flatShare: body.flatShare,
          ramp: ramp ?? null,
        },
        interior,
        shadowTermPredicted: withShadow - withoutShadow,
        rampAreaMean: {
          opticsCarries: scatterRampAreaMean(span, size, scale, [shape.width, shape.height]),
          exactOverTheBox: exact / exactCount,
          difference: scatterRampAreaMean(span, size, scale, [shape.width, shape.height]) - exact / exactCount,
        },
      });
    });
  }
}

writeFileSync(outJson, `${JSON.stringify(rows, null, 2)}\n`);
process.stdout.write(`${String(rows.length)} rows -> ${outJson}\n`);
