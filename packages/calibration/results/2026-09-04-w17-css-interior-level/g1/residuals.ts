/**
 * W17 G1 — the two residuals of the landed form, evaluated on the three W16 probe cells.
 *
 * Decision Log 2 (c) says the tint's lerp inside the sharp layer's linear-light filter is exact
 * per pixel, "up to two residuals G1 derives and records". This script is where they get their
 * numbers, so the doc comments beside the code can cite an evaluation rather than an argument.
 *
 * ## Residual one — the page's encoded-space mix of the two TINTED layers under the mask
 *
 * The tier's body is two sibling layers over the page. L1 filters the page at the sharp width and
 * applies the affine; the browser writes its output into the page's own encoded eight-bit buffer.
 * L2 then filters THAT at the heavy step, under the ramp's raster mask, and the compositor mixes
 * the two by the mask's alpha — in the ENCODED space, because that is the space a page composites
 * in. The renderer mixes its two components in linear light before it tints. So the tier draws
 *
 *     D[(1 − m)·E(A(s)) + m·E(A(h))]        and the renderer draws     A((1 − m)·s + m·h)
 *
 * with `E` the sRGB encode, `D` its inverse, `A(b) = (1 − α)·b + α·T + X` the affine, `s` and `h`
 * the sharp and heavy blurred backdrops in linear light and `m` the ramp's share at that pixel.
 * The difference is second order in `s − h` through the encode's curvature, and the affine scales
 * that difference by `1 − α` before the encode sees it — so the same residual W16 carried on the
 * untinted body is smaller here, on both counts. This script evaluates it per pixel on the real
 * fixture background, at the tier's own two widths and its own ramp, and reports the mean over the
 * surface's silhouette, which is the statistic the interior level is.
 *
 * ## Residual two — W16's effective kernel width
 *
 * The tier's widths are the renderer's kernel's EFFECTIVE Gaussian width rather than the profile's
 * nominal one: a ratio per scale fitted on the renderer's own broadband captures, 1.380 at dpr 1
 * and 1.485 at dpr 2 (claims §5.72 §1). A ratio per scale is not a ratio per span, and the
 * per-span readings it was fitted over are in that table. This script reports what each probe
 * cell's own reading costs, in the only unit that matters to this wave: a Gaussian is normalised,
 * so a width error moves no mean on a statistically homogeneous backdrop and moves the interior's
 * SPREAD instead — the quantity S3 gates. Both numbers are reported per cell.
 *
 * Usage: `npx tsx results/2026-09-04-w17-css-interior-level/g1/residuals.ts <outJson>`, from
 * `packages/calibration`. Reads only the committed fixtures; writes only the file it is given.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  cssTierDeclarations,
  cssTierTintTransfer,
  innerShadowedSourceOptics,
  interiorBandLight,
  interiorShadowKeep,
  adaptedSourceOptics,
  backdropToneAdaptation,
  backdropToneUnderPolicy,
  MATERIAL_OPTICS,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  resolvedTintShade,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sourceOptics,
  sourceSize,
  toneRespondedSourceOptics,
  type CssTierRamp,
  type InteriorSurfaceGeometry,
} from "@vitreajs/vitrea-web";
import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import { PNG } from "pngjs";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
const FIXTURES = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple", "fixtures");

const encode = (l: number): number =>
  l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;
const decode = (e: number): number => (e <= 0.04045 ? e / 12.92 : ((e + 0.055) / 1.055) ** 2.4);
const clamp01 = (x: number): number => Math.min(1, Math.max(0, x));
const quantise = (l: number): number => decode(Math.round(clamp01(encode(clamp01(l))) * 255) / 255);

/*
 * The ramp's two helpers, restated from `css-tier-layers.ts` — the exact field the raster mask is
 * drawn from, and the two-point form of the heavy share along it. They are not on the package's
 * public surface because they are the DOM module's, and copying eight lines of geometry into a
 * scratch script is better than widening a published API for one measurement. `css-tier.test.ts`
 * pins `maskShareAt` against `cssTierHeavyShareAt` over a sweep of depths, so the law itself has an
 * owner and this is a transcription of it.
 */
function roundedRectDepth(
  x: number,
  y: number,
  halfWidth: number,
  halfHeight: number,
  radius: number,
): number {
  const r = Math.min(radius, Math.min(halfWidth, halfHeight));
  const qx = Math.abs(x) - (halfWidth - r);
  const qy = Math.abs(y) - (halfHeight - r);
  const outside = Math.hypot(Math.max(qx, 0), Math.max(qy, 0));
  const inside = Math.min(Math.max(qx, qy), 0);
  return r - (outside + inside);
}

function maskShareAt(uDevicePx: number, ramp: CssTierRamp): number {
  const reach = Math.max(ramp.reachDevicePx, 1e-6);
  const t = Math.min(Math.max(uDevicePx, 0) / reach, 1);
  return ramp.deepShare + (ramp.contourShare - ramp.deepShare) * (1 - t);
}

/** A separable Gaussian at σ device px, in linear light, over a single-channel plane. */
function blur(plane: Float64Array, width: number, height: number, sigma: number): Float64Array {
  if (sigma <= 1e-4) return plane;
  const radius = Math.max(1, Math.ceil(sigma * 3));
  const kernel = new Float64Array(radius * 2 + 1);
  let sum = 0;
  for (let i = -radius; i <= radius; i += 1) {
    const value = Math.exp(-(i * i) / (2 * sigma * sigma));
    kernel[i + radius] = value;
    sum += value;
  }
  for (let i = 0; i < kernel.length; i += 1) kernel[i]! /= sum;

  const horizontal = new Float64Array(plane.length);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      let total = 0;
      for (let i = -radius; i <= radius; i += 1) {
        const sx = Math.min(width - 1, Math.max(0, x + i));
        total += (plane[y * width + sx] ?? 0) * kernel[i + radius]!;
      }
      horizontal[y * width + x] = total;
    }
  }
  const vertical = new Float64Array(plane.length);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      let total = 0;
      for (let i = -radius; i <= radius; i += 1) {
        const sy = Math.min(height - 1, Math.max(0, y + i));
        total += (horizontal[sy * width + x] ?? 0) * kernel[i + radius]!;
      }
      vertical[y * width + x] = total;
    }
  }
  return vertical;
}

interface Probe {
  readonly cell: string;
  readonly geometry: InteriorSurfaceGeometry;
  /**
   * The surface's own measured border box in the capture's CSS-px frame, read off the run's
   * `report__css.json` rather than declared here — these are the numbers the runtime resolved the
   * body and the ramp from, so the residual is evaluated over the pixels the tier really drew.
   */
  readonly originCssPx: readonly [number, number];
  /** W16 G1 §1's per-span effective heavy width readings, nominal and measured. */
  readonly heavyEffective: { readonly [scale: string]: { nominal: number; effective: number } };
}

const PROBES: Probe[] = [
  {
    cell: "checkerboard__rrect-md__rest",
    geometry: { widthCssPx: 162, heightCssPx: 98, radiusCssPx: 20, thicknessCssPx: 8 },
    originCssPx: [80, 52],
    heavyEffective: { "1": { nominal: 10, effective: 13.869 }, "2": { nominal: 6, effective: 8.914 } },
  },
  {
    cell: "checkerboard__capsule-button__rest",
    geometry: { widthCssPx: 122, heightCssPx: 46, radiusCssPx: 22, thicknessCssPx: 8 },
    originCssPx: [100, 78],
    heavyEffective: { "1": { nominal: 10, effective: 13.731 }, "2": { nominal: 6, effective: 9.0 } },
  },
  {
    cell: "checkerboard__rrect-ml__rest",
    geometry: { widthCssPx: 226, heightCssPx: 130, radiusCssPx: 27, thicknessCssPx: 8 },
    originCssPx: [48, 36],
    heavyEffective: { "1": { nominal: 10, effective: 13.821 }, "2": { nominal: 6.663, effective: 9.917 } },
  },
];

/** The adopted per-scale ratio the tier writes (claims §5.72 §1). */
const ADOPTED_RATIO: Record<string, number> = { "1": 1.38, "2": 1.485 };

/** The shader-order composite for one probe cell over the checkerboard. */
function interiorOf(probe: Probe): { alpha: number; tint: number; band: number; keep: number } {
  const base = sourceOptics().regular;
  const size = sourceSize();
  const span = Math.min(probe.geometry.widthCssPx, probe.geometry.heightCssPx);
  const thickness = sizeThickness(span, size);
  const sample = { rgb: [0.5, 0.5, 0.5] as [number, number, number], luminance: 0.21404114048223255, linearLuminance: 0.5 };
  const occluded = {
    ...base,
    tintAlpha: sizeOcclusionAlphaAt(base.tintAlpha, thickness, size),
  };
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
  const keep = interiorShadowKeep(base, probe.geometry, thickness, 1 - adaptation);
  const shadowed = innerShadowedSourceOptics(adapted, keep);
  return {
    alpha: shadowed.tintAlpha,
    tint: shadowed.tint[1],
    band: interiorBandLight(base, probe.geometry, 1 - adaptation),
    keep,
  };
}

const rows: unknown[] = [];
for (const scale of [1, 2] as const) {
  // The checkerboard background at this scale, in linear light — one channel, since the
  // background and the tint are both achromatic and the residual is a curvature of the encode.
  const png = PNG.sync.read(readFileSync(resolve(FIXTURES, `backgrounds/checkerboard@${scale}x.png`)));
  const plane = new Float64Array(png.width * png.height);
  for (let i = 0; i < plane.length; i += 1) plane[i] = decode((png.data[i * 4] ?? 0) / 255);

  for (const probe of PROBES) {
    const span = Math.min(probe.geometry.widthCssPx, probe.geometry.heightCssPx);
    const render = cssTierDeclarations({
      radii: [
        probe.geometry.radiusCssPx,
        probe.geometry.radiusCssPx,
        probe.geometry.radiusCssPx,
        probe.geometry.radiusCssPx,
      ],
      optics: MATERIAL_OPTICS.regular,
      policy: NOMINAL_ACCESSIBILITY_POLICY,
      spanPx: span,
      extentsCssPx: [probe.geometry.widthCssPx, probe.geometry.heightCssPx],
      devicePixelRatio: scale,
      engine: { referenceFilterInBackdrop: true, maskOnBackdropFilter: "yes" },
    });
    const body = render.body;
    const ramp = body.ramp as CssTierRamp | undefined;
    const interior = interiorOf(probe);
    const transfer = cssTierTintTransfer({
      tintAlpha: interior.alpha,
      tint: [interior.tint, interior.tint, interior.tint],
      addedLight: interior.band,
    });

    const sharp = blur(plane, png.width, png.height, body.sharpSigmaCssPx * scale);
    const heavy = blur(sharp, png.width, png.height, body.heavyStepSigmaCssPx * scale);
    // The same two widths without the tint, for the untinted mix W16 carried.
    const affine = (b: number): number => transfer.slope * b + transfer.intercept[1]!;

    const left = Math.round(probe.originCssPx[0] * scale);
    const top = Math.round(probe.originCssPx[1] * scale);
    const width = Math.round(probe.geometry.widthCssPx * scale);
    const height = Math.round(probe.geometry.heightCssPx * scale);
    let tiered = 0;
    let rendered = 0;
    let untieredGap = 0;
    let worst = 0;
    let count = 0;
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const index = (top + y) * png.width + (left + x);
        const s = sharp[index] ?? 0;
        const h = heavy[index] ?? 0;
        const depth = roundedRectDepth(
          x + 0.5 - width / 2,
          y + 0.5 - height / 2,
          width / 2,
          height / 2,
          probe.geometry.radiusCssPx * scale,
        );
        if (depth < 0) continue;
        const m = ramp === undefined ? body.flatShare : clamp01(maskShareAt(depth, ramp));
        // The page's mix, in the encoded eight-bit space the compositor works in.
        const mixed = decode((1 - m) * encode(clamp01(affine(s))) + m * encode(clamp01(affine(h))));
        const exact = affine((1 - m) * s + m * h);
        tiered += mixed;
        rendered += exact;
        worst = Math.max(worst, Math.abs(mixed - exact));
        // The same mix without the affine — W16's untinted residual, for the ratio.
        untieredGap += decode((1 - m) * encode(s) + m * encode(h)) - ((1 - m) * s + m * h);
        count += 1;
      }
    }

    const scaleKey = String(scale);
    const effective = probe.heavyEffective[scaleKey]!;
    const adopted = ADOPTED_RATIO[scaleKey]!;
    rows.push({
      cell: probe.cell,
      dpr: scale,
      sharpSigmaCssPx: body.sharpSigmaCssPx,
      heavyStepSigmaCssPx: body.heavyStepSigmaCssPx,
      heavySigmaCssPx: body.heavySigmaCssPx,
      transfer: { slope: transfer.slope, intercept: transfer.intercept[1] },
      interior,
      maskMix: {
        pixels: count,
        tieredMean: tiered / count,
        exactMean: rendered / count,
        residualMean: tiered / count - rendered / count,
        residualWorstPixel: worst,
        untintedResidualMean: untieredGap / count,
      },
      effectiveWidth: {
        adoptedRatio: adopted,
        cellRatio: effective.effective / effective.nominal,
        // What the adopted ratio writes against what this cell's own reading asks for, as a
        // fraction of the width — the quantity the spread carries.
        widthErrorFraction: (adopted * effective.nominal) / effective.effective - 1,
        sigmaWrittenDevicePx: body.heavySigmaCssPx * scale,
        sigmaCellAsksDevicePx: (effective.effective / effective.nominal / adopted) * body.heavySigmaCssPx * scale,
      },
      // A Gaussian is normalised, so a width error moves no mean over a homogeneous backdrop:
      // this is that statement, evaluated rather than asserted.
      widthErrorMeanShift: (() => {
        const asked = blur(
          sharp,
          png.width,
          png.height,
          Math.max(
            0,
            Math.sqrt(
              Math.max(
                ((effective.effective / effective.nominal / adopted) * body.heavySigmaCssPx * scale) ** 2 -
                  (body.sharpSigmaCssPx * scale) ** 2,
                0,
              ),
            ),
          ),
        );
        let a = 0;
        let b = 0;
        let n = 0;
        for (let y = 0; y < height; y += 1) {
          for (let x = 0; x < width; x += 1) {
            const index = (top + y) * png.width + (left + x);
            const depth = roundedRectDepth(
              x + 0.5 - width / 2,
              y + 0.5 - height / 2,
              width / 2,
              height / 2,
              probe.geometry.radiusCssPx * scale,
            );
            if (depth < 0) continue;
            const m = ramp === undefined ? body.flatShare : clamp01(maskShareAt(depth, ramp));
            a += affine((1 - m) * (sharp[index] ?? 0) + m * (heavy[index] ?? 0));
            b += affine((1 - m) * (sharp[index] ?? 0) + m * (asked[index] ?? 0));
            n += 1;
          }
        }
        return { written: a / n, cellAsks: b / n, shift: b / n - a / n };
      })(),
    });
    void quantise;
  }
}

const [, , outJson] = process.argv;
if (outJson === undefined) throw new Error("usage: residuals.ts <outJson>");
writeFileSync(outJson, `${JSON.stringify(rows, null, 1)}\n`);
process.stdout.write(`${rows.length} rows -> ${outJson}\n`);
for (const row of rows as { cell: string; dpr: number; maskMix: { residualMean: number; residualWorstPixel: number; untintedResidualMean: number }; widthErrorMeanShift: { shift: number }; effectiveWidth: { widthErrorFraction: number } }[]) {
  process.stdout.write(
    `${row.cell} dpr${row.dpr}  maskMix ${row.maskMix.residualMean.toFixed(6)}` +
      ` (untinted ${row.maskMix.untintedResidualMean.toFixed(6)}, worst px ${row.maskMix.residualWorstPixel.toFixed(6)})` +
      `  width ${(row.effectiveWidth.widthErrorFraction * 100).toFixed(2)}% -> mean ${row.widthErrorMeanShift.shift.toFixed(6)}\n`,
  );
}
