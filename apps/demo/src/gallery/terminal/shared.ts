/**
 * The family, the two materials, the dimming law and the one backdrop every group reads
 * (`DESIGN.md`).
 */

import type { DimmingPolicy, GlassTextureBackdrop } from "@vitreajs/vitrea-react";
import type { RendererMaterialProfile } from "@vitreajs/vitrea-web";
import type { CSSProperties } from "react";

import type { GlassKind, ProfileId, Scheme } from "./shell/types";

export interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/** The window's corner: a working window's, tighter than a glance surface's, and the anchor. */
export const WINDOW_RADIUS = 22;
/**
 * The window's thickness. The lens is what the Clear profile is for, and its band's width scales
 * with thickness; 12 shows the shores bending at the rim of a window this size while the band
 * still fits inside the padding the terminal's grid is set in from the edge.
 */
export const WINDOW_THICKNESS = 12;
/** The ornaments: the material's reference thickness. */
export const ORNAMENT_THICKNESS = 8;

export const ENVIRONMENT_ID = "tahoe-relief";
export const ENVIRONMENT_BACKDROP: GlassTextureBackdrop = { kind: "texture", id: ENVIRONMENT_ID };

export interface Profile {
  readonly id: ProfileId;
  readonly name: string;
  readonly note: string;
  readonly glass: GlassKind;
  readonly scheme: Scheme;
}

export const PROFILES: readonly Profile[] = [
  { id: "clear-dark", name: "Clear Dark", note: "clear glass, the map darkened under it", glass: "clear", scheme: "dark" },
  { id: "clear-light", name: "Clear Light", note: "clear glass, the map lightened under it", glass: "clear", scheme: "light" },
  { id: "regular-dark", name: "Regular Dark", note: "vitrea’s calibrated macOS 27 glass, dark", glass: "regular", scheme: "dark" },
  { id: "regular-light", name: "Regular Light", note: "vitrea’s calibrated macOS 27 glass, light", glass: "regular", scheme: "light" },
];

export const profileOf = (glass: GlassKind, scheme: Scheme): Profile =>
  PROFILES.find((p) => p.glass === glass && p.scheme === scheme) ?? (PROFILES[0] as Profile);

/**
 * The Clear material: the shipped clear variant with the leaves that make a window-sized body a
 * plate stood down, as the planetarium found them (its `shared.ts` and the tracker entry of
 * 2026-09-28): the heavy scatter component, the size law's occlusion facet, and the fitted tone
 * response with its black branch. Its base σ is this page's own: a terminal's text sits over the
 * map at every point of the window, so the body keeps enough blur that a contour line behind a
 * glyph reads as a soft band rather than a second stroke, where the planetarium's stars wanted
 * 0.6. The runtime reports `tuned: true`; Regular is drawn with no tune at all.
 */
export const CLEAR_BLUR_SIGMA = 1.4;
export const CLEAR_TINT_ALPHA = 0.02;

export function clearTune(blurSigma: number = CLEAR_BLUR_SIGMA): RendererMaterialProfile {
  return {
    optics: { clear: { blurSigma, tintAlpha: CLEAR_TINT_ALPHA } },
    backdropToneResponseStrength: 0,
    backdropToneBlackStrength: 0,
    sizeScatterGainMax: 1,
    sizeScatterGainMax2x: 1,
    sizeScatterGainFar2x: 1,
    sizeHeavyTapSigma: 0,
    sizeHeavyTapSigma2x: 0,
    sizeOcclusionGain: 0,
  };
}

/**
 * The dimming layer Clear requires, painted by the page into the map under each footprint (no
 * tier draws one). Dark darkens and Light lightens, each toward a target in ENCODED terms,
 * because the canvas composites encoded values: the strength under a footprint is solved from the
 * encoded level measured there so the composite lands at the target, floored so the glass always
 * reads as dimmed and capped so the map always shows through. Uncalibrated, and the record says so.
 */
export const DIMMING = {
  dark: { target: 0.19, floor: 0.2, max: 0.9 },
  light: { target: 0.86, floor: 0.2, max: 0.9 },
  /**
   * An ornament's floor: its labels sit on a small surface the size law keeps nearly sharp, so a
   * map label or a contour under a word reads as a second word unless the layer takes it down
   * further than the window's.
   */
  ornamentFloor: 0.62,
  /** The ramp inward from a footprint's edge: a share of its shorter span, within bounds. */
  featherShare: 0.12,
  featherMin: 5,
  featherMax: 18,
} as const;

export function featherFor(span: number): number {
  return Math.max(DIMMING.featherMin, Math.min(DIMMING.featherMax, span * DIMMING.featherShare));
}

/** The strength that takes an encoded level to the scheme's target, within floor and cap. */
export function dimmingFor(scheme: Scheme, encoded: number, ornament = false): number {
  const law = DIMMING[scheme];
  const floor = ornament ? DIMMING.ornamentFloor : law.floor;
  const solved =
    scheme === "dark"
      ? encoded <= 0
        ? 0
        : 1 - law.target / encoded
      : encoded >= 1
        ? 0
        : (law.target - encoded) / (1 - encoded);
  return Math.min(law.max, Math.max(floor, solved));
}

/** What every group is told about its material. */
export type GroupMaterial = { readonly variant: "clear"; readonly dimming: DimmingPolicy } | { readonly variant: "regular" };

export function groupMaterial(glass: GlassKind, scheme: Scheme, strength: number | undefined): GroupMaterial {
  if (glass === "regular") return { variant: "regular" };
  const scrim = Math.round((strength ?? DIMMING[scheme].floor) * 1000) / 1000;
  return { variant: "clear", dimming: { scrim, direction: scheme === "dark" ? "darken" : "lighten" } };
}

/** A host's box as the inline offsets a fixed host needs; nothing else goes inline. */
export function boxStyle(box: Box): CSSProperties {
  return { position: "fixed", left: box.x, top: box.y, width: box.width, height: box.height, boxSizing: "border-box" };
}

/** A registered host's footprint as the glass draws it, for the dimming layer and the readings. */
export interface HostShape {
  readonly id: string;
  readonly box: Box;
  readonly radius: number;
}
