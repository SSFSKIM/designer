/**
 * @vitrea/platform-web — skeleton (C1).
 *
 * The only package allowed to touch the DOM. Encodes X1's plane law and paint
 * order so C5 builds the sandwich against a fixed contract.
 */

import type { GlassGroupState } from "@vitrea/core";

/** v1 ships exactly two managed stacking planes (X1). */
export const GLASS_PLANES = ["base", "overlay"] as const;

export type GlassPlane = (typeof GLASS_PLANES)[number];

/**
 * Paint order within one plane, back to front (X1). The semantic host sits
 * between the optics canvas and the highlight canvas — that sandwich is why
 * two glass surfaces may not overlap inside one plane.
 */
export const PLANE_PAINT_ORDER = [
  "backdrop-proxy",
  "optics-canvas",
  "semantic-host",
  "highlight-canvas",
] as const;

export type PlaneLayer = (typeof PLANE_PAINT_ORDER)[number];

export function paintOrderIndex(layer: PlaneLayer): number {
  return PLANE_PAINT_ORDER.indexOf(layer);
}

/** Layers the compositor owns; everything else in the sandwich is app DOM. */
export const POINTER_TRANSPARENT_LAYERS: readonly PlaneLayer[] = PLANE_PAINT_ORDER.filter(
  (layer) => layer !== "semantic-host",
);

/** What C5 registers per glass host. `host` is real DOM — this is the boundary X4 protects. */
export interface GlassHostRegistration {
  readonly host: HTMLElement;
  readonly plane: GlassPlane;
  readonly groupId: string;
  readonly state: GlassGroupState;
}
