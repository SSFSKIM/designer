/**
 * The declaration-conformance reading, against injected ground truth (W20 G0
 * contract X4; claims §5.83).
 *
 * The shape axis's other rows compare the two sides to each other inside the
 * declared region, and are blind to a surface drawn LARGER than its
 * declaration: the region clips it, so it reads as a perfect fill. These rows
 * close that direction by comparing the web tier's own DRAWN silhouette — its
 * alpha over a transparent page — to the declared geometry, with no bound.
 *
 * Every case here is a construction whose answer is known by algebra, in the
 * package's own rule: a capture can only say a metric is stable, and only an
 * injected quantity can say it is right. Three constructions, and each is a
 * quantity the wave has to be able to see:
 *
 *   1. **Exact.** The declared geometry drawn as itself. IoU 1, contour 0.
 *   2. **The known dilation (X4).** The same geometry dilated by four device
 *      pixels — the injected excess the instrument must recover, both in area
 *      and as a contour distance of four.
 *   3. **The defect.** The 120 × 44 capsule at the radius the Apple reference's
 *      budget policy clamps it to, `22 / 1.52866495`. This is the shape the GPU
 *      tier actually draws, built here from the geometry rather than from a
 *      capture, so the numbers a real capture produces have an analytic
 *      counterpart to be checked against.
 *
 * `measureCell` is a CLI module and needs four files on disk, so what is
 * exercised here is the composition it performs — the alpha extractor with no
 * region, then `silhouetteIoU` and `contourDistance` against
 * `componentRegion(...).silhouette`. Those are the same calls in the same
 * order over the same masks; the run script under
 * `results/2026-09-05-w20-capsule-corner/g0/` does the end-to-end on real
 * captures.
 */

import { describe, expect, it } from "vitest";

import { componentRegion, type DeclaredComponent } from "../src/component-region";
import { contourDistance, silhouetteIoU } from "../src/metrics/shape";
import { extractSilhouette, silhouetteArea } from "../src/silhouette";
import { alphaMaskImage } from "./synthesise";

/** The bed's canvas and the capsule, exactly as `scenes.json` declares them. */
const CANVAS = { width: 320, height: 200 };
const CAPSULE: DeclaredComponent = { kind: "capsule", size: [120, 44] };
const RRECT_MD: DeclaredComponent = { kind: "rrect", size: [160, 96], radius: 20 };

/** The Apple corner reference's measured reach, from `@vitrea/geometry`. */
const APPLE_REACH = 1.52866495;

/**
 * Pixel-centre containment in a rounded rectangle centred on the canvas —
 * `component-region.ts`'s own placement and its own signed-distance form, so a
 * drawn shape and a declared one are rasterised by one rule and the test
 * measures the metric rather than two rasterisers disagreeing.
 */
function drawn(
  size: readonly [number, number],
  radius: number,
  scale: number,
  dilatePx = 0,
): (x: number, y: number) => boolean {
  const left = Math.round((CANVAS.width - size[0]) / 2);
  const top = Math.round((CANVAS.height - size[1]) / 2);
  const centreX = (left + size[0] / 2) * scale;
  const centreY = (top + size[1] / 2) * scale;
  const halfWidth = (size[0] / 2) * scale;
  const halfHeight = (size[1] / 2) * scale;
  const r = radius * scale;
  return (x, y) => {
    const qx = Math.abs(x + 0.5 - centreX) - (halfWidth - r);
    const qy = Math.abs(y + 0.5 - centreY) - (halfHeight - r);
    const distance =
      Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - r;
    return distance <= dilatePx;
  };
}

interface Conformance {
  readonly drawnArea: number;
  readonly declaredArea: number;
  readonly iou: number;
  readonly p95: number;
  readonly max: number;
}

/** The composition `measureCell` performs, over one synthetic conformance capture. */
function read(
  component: DeclaredComponent,
  inside: (x: number, y: number) => boolean,
  scale: number,
): Conformance {
  const width = CANVAS.width * scale;
  const height = CANVAS.height * scale;
  const region = componentRegion(component, { canvas: CANVAS, scale, width, height });
  const capture = alphaMaskImage(width, height, inside);
  // No region: seeing outside the declaration is the whole purpose.
  const silhouette = extractSilhouette(capture, { kind: "alpha", threshold: 0.5 });
  const against = contourDistance(silhouette, region.silhouette);
  return {
    drawnArea: silhouetteArea(silhouette),
    declaredArea: region.areaPx,
    iou: silhouetteIoU(silhouette, region.silhouette),
    p95: against.p95Px,
    max: against.maxPx,
  };
}

describe("a surface drawn exactly as declared", () => {
  it("reads 1.000 and zero on the capsule at 1x and 2x", () => {
    for (const scale of [1, 2]) {
      const reading = read(CAPSULE, drawn([120, 44], 22, scale), scale);
      expect(reading.drawnArea).toBe(reading.declaredArea);
      expect(reading.iou).toBe(1);
      expect(reading.max).toBe(0);
    }
  });

  it("reads 1.000 and zero on a rounded rectangle", () => {
    const reading = read(RRECT_MD, drawn([160, 96], 20, 1), 1);
    expect(reading.iou).toBe(1);
    expect(reading.max).toBe(0);
  });
});

describe("X4 — a known dilation, injected and recovered", () => {
  it("recovers four device pixels of dilation as four pixels of contour distance", () => {
    const reading = read(CAPSULE, drawn([120, 44], 22, 1, 4), 1);
    // The contour moved out by exactly four and the metric reads 4.243, which
    // is 3√2: the metric is a distance between BOUNDARY PIXEL rings on the
    // raster, so an outer corner pixel's nearest inner boundary pixel is a
    // diagonal away and the grid's own √2 is the residual. It recovers the
    // injected quantity to within the floor `silhouette.ts` already declares —
    // it does not merely increase with it.
    expect(reading.max).toBeCloseTo(4.2426, 3);
    expect(reading.p95).toBeCloseTo(4.1231, 3);
    // And the area grew by the perimeter times the dilation, to the raster: a
    // 120 × 44 stadium has a 2·(120 − 44) + π·44 = 290.2 px perimeter, so four
    // pixels out adds about 1210 px including the corner sweep.
    expect(reading.drawnArea - reading.declaredArea).toBeGreaterThan(1150);
    expect(reading.drawnArea - reading.declaredArea).toBeLessThan(1300);
    expect(reading.iou).toBeCloseTo(reading.declaredArea / reading.drawnArea, 3);
  });

  it("recovers the same dilation at 2x, in device pixels", () => {
    const reading = read(CAPSULE, drawn([120, 44], 22, 2, 4), 2);
    // Four DEVICE pixels at 2x is two CSS px, so the contour figure is the same
    // 4.243 and the area excess is not four times the 1x one: the reading is in
    // device pixels on both scales, which is what lets the two beds be compared.
    expect(reading.max).toBeCloseTo(4.2426, 3);
    expect(reading.drawnArea - reading.declaredArea).toBeGreaterThan(2300);
  });

  it("sees a dilation of one device pixel, which is the axis's own floor", () => {
    const reading = read(CAPSULE, drawn([120, 44], 22, 1, 1), 1);
    // √2 — one pixel of dilation is one pixel of boundary displacement, read
    // across the grid's diagonal. Below this nothing is separable from the
    // raster, which is the floor the axis has always declared.
    expect(reading.max).toBeCloseTo(1.4142, 3);
    expect(reading.iou).toBeLessThan(1);
  });
});

describe("the defect, built from the geometry rather than from a capture", () => {
  /*
   * The GPU tier draws this capsule at `min(halfW, halfH) / APPLE_REACH` because
   * `resolveFromChannels` never reads the shape family and the Apple reference
   * clamps the radius (claims §5.83 section 2). A smaller radius in the same box
   * is a FULLER shape, so the drawn silhouette is a superset of the stadium and
   * the excess is four shoulders at the ends.
   */
  const clamped = 22 / APPLE_REACH;

  it("reads the clamped capsule as larger than declared, by the shoulders", () => {
    const reading = read(CAPSULE, drawn([120, 44], clamped, 1), 1);
    expect(clamped).toBeCloseTo(14.3916, 4);
    expect(reading.declaredArea).toBe(4872);
    // 232 px of shoulder at 1x — the same excess `finding/shoulders.py` measured
    // off the canonical captures, here derived from the geometry alone.
    expect(reading.drawnArea).toBe(5104);
    expect(reading.drawnArea - reading.declaredArea).toBe(232);
    expect(reading.iou).toBeCloseTo(0.9545, 4);
    // The departure is on the diagonal and nowhere else, which is why the max
    // carries it and the p95 — pooled over two full boundaries, most of which
    // are the straight edges — reads a third of it.
    expect(reading.max).toBeGreaterThan(2.8);
    expect(reading.p95).toBeLessThan(reading.max);
  });

  it("reads it at 2x as the same defect at twice the scale", () => {
    const reading = read(CAPSULE, drawn([120, 44], clamped, 2), 2);
    expect(reading.drawnArea - reading.declaredArea).toBe(948);
    expect(reading.max).toBeGreaterThan(5.8);
  });

  it("leaves a rounded rectangle untouched, because its ratio is under the clamp", () => {
    // rrect-md's r/min is 0.208 against Apple's 0.327 saturation ratio, so the
    // clamp does not reach it and the drawn shape is the declared one.
    const clampedRrect = Math.min(20, 48 / APPLE_REACH);
    expect(clampedRrect).toBe(20);
    const reading = read(RRECT_MD, drawn([160, 96], clampedRrect, 1), 1);
    expect(reading.iou).toBe(1);
    expect(reading.max).toBe(0);
  });
});
