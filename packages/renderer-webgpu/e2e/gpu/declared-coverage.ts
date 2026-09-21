/**
 * W31 G2 — the declaration-conformance reading a range sweep asserts, shared
 * (claims §5.163 §2).
 *
 * The rule is W20's, read the way the calibration harness reads it per cell
 * (`declared-conformance.test.ts`, the alpha extractor at threshold 0.5): the
 * DRAWN silhouette — alpha at or above half of what the material composites at —
 * must CONTAIN the declared region. It is the invariant a sweep over a material
 * axis can assert without knowing what the axis does, which is the whole shape
 * of the instrument: **no constant of the material decides what the surface
 * covers.**
 *
 * **What this measures is CONTAINMENT, and the field said `iou` until
 * 2026-09-21** (review closure; claims §5.163 §8, finding N2). The number
 * returned is `intersection / declared.length` — the fraction of the DECLARED
 * mask that carries material, which is recall over the declaration and is
 * identically `1 − undrawn/declared`. It is not an intersection-over-union: the
 * union would add the drawn pixels outside the declaration, and those are
 * deliberately not counted, because the exterior there is the shadow — a facet,
 * not a silhouette. Two consequences worth stating rather than discovering. A
 * sweep that asserts `undrawn === 0` has already asserted `containment === 1`,
 * so the `≥ 0.99` clause beside it is implied and is there to say what the
 * reading MEANS rather than to catch anything the other clause would miss. And
 * OVER-draw is invisible to this number by construction; the instrument that
 * sees it is the calibration harness's silhouette metrics, not this one.
 *
 * `w30-thin-sigma-coverage.spec.ts` carries its own copy of these four
 * functions and deliberately keeps it. That case is the committed reading of a
 * defect — it records that the capsule left 652 of 4,780 declared px undrawn on
 * the unfixed renderer — and a reading of a defect should not be able to move
 * under a later refactor of somebody else's helper. New cases share this one;
 * that one is evidence and stays where it was measured.
 */

import type { Raster } from "../support";

export interface Region {
  readonly cx: number;
  readonly cy: number;
  readonly w: number;
  readonly h: number;
  readonly r: number;
}

/** The signed distance to a rounded rectangle, CSS px, negative inside. */
export const roundedRectDistance = (x: number, y: number, region: Region): number => {
  const dx = Math.abs(x - region.cx) - (region.w / 2 - region.r);
  const dy = Math.abs(y - region.cy) - (region.h / 2 - region.r);
  const ox = Math.max(dx, 0);
  const oy = Math.max(dy, 0);
  return Math.min(Math.max(dx, dy), 0) + Math.hypot(ox, oy) - region.r;
};

/**
 * The declared region as pixel indices.
 *
 * A pixel counts as declared when its CENTRE is at least half a pixel inside the
 * contour, which is the rule that keeps the antialiased ring out of the mask: a
 * partially covered pixel is evidence about the contour, not about coverage.
 */
export const declaredPixels = (regions: readonly Region[], width: number): number[] => {
  const out: number[] = [];
  for (const region of regions) {
    const x0 = Math.floor(region.cx - region.w / 2) - 1;
    const x1 = Math.ceil(region.cx + region.w / 2) + 1;
    const y0 = Math.floor(region.cy - region.h / 2) - 1;
    const y1 = Math.ceil(region.cy + region.h / 2) + 1;
    for (let y = y0; y <= y1; y += 1) {
      for (let x = x0; x <= x1; x += 1) {
        if (roundedRectDistance(x + 0.5, y + 0.5, region) <= -0.5) out.push(y * width + x);
      }
    }
  }
  return out;
};

/**
 * The drawn silhouette, at half the capture's own peak alpha.
 *
 * The scale is the capture's maximum rather than 255 because a group over a
 * transparent page emits the material's own alpha, which is well under one on
 * the unsampled path.
 */
export const drawnPixels = (raster: Raster): { readonly set: Set<number>; readonly peak: number } => {
  let peak = 0;
  for (let i = 3; i < raster.data.length; i += 4) peak = Math.max(peak, raster.data[i] ?? 0);
  const cutoff = peak / 2;
  const set = new Set<number>();
  for (let i = 0; i < raster.width * raster.height; i += 1) {
    if ((raster.data[i * 4 + 3] ?? 0) >= cutoff) set.add(i);
  }
  return { set, peak };
};

export interface Conformance {
  readonly undrawn: number;
  readonly declared: number;
  /** The declared mask's drawn fraction. Containment, not IoU — module note. */
  readonly containment: number;
  readonly peak: number;
}

/**
 * The clause, BOUNDED to the declared region: outside it nothing is recovered,
 * because the exterior there is the shadow, which is a facet and not a
 * silhouette.
 */
export const conformance = (raster: Raster, regions: readonly Region[]): Conformance => {
  const declared = declaredPixels(regions, raster.width);
  const { set, peak } = drawnPixels(raster);
  let intersection = 0;
  for (const index of declared) if (set.has(index)) intersection += 1;
  return {
    undrawn: declared.length - intersection,
    declared: declared.length,
    containment: declared.length === 0 ? 1 : intersection / declared.length,
    peak,
  };
};
