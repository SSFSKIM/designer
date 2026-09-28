/**
 * The family, the material and the one backdrop every group reads (`DESIGN.md`).
 */

import type { DimmingPolicy, GlassTextureBackdrop } from "@vitreajs/vitrea-react";
import type { RendererMaterialProfile } from "@vitreajs/vitrea-web";
import type { CSSProperties } from "react";

import type { Box } from "./sky/renderer";

/**
 * One thickness across the page, 14: the runtime's own open-morph thickness and the top of the
 * spatial register's stated range. The lens is what this page is for, and its depth and
 * displacement scale with thickness over the material's reference of 8 (`optics.md` §1).
 */
export const THICKNESS = 14;
/** The window and the module: one generous fixed corner, the page's concentric anchor. */
export const WINDOW_RADIUS = 28;
/** Platters: a multi-row surface keeps a rounded rectangle, smaller than the window's. */
export const PLATTER_RADIUS = 24;

export const ENVIRONMENT_ID = "tonight-sky";
export const ENVIRONMENT_BACKDROP: GlassTextureBackdrop = { kind: "texture", id: ENVIRONMENT_ID };

/**
 * The page's one tuning over the shipped material, and the reason the record gives for it.
 *
 * Every group is `clear`. The shipped clear variant's base blur is 4 CSS px against the calibrated
 * regular body's 1.25, and the size law multiplies a base σ by up to 8 at window span, so shipped
 * clear draws a window body at σ 30–38 px — the start page measured it and read it as the MORE
 * frosted material. Clear's constants are nominal, not fitted (no bed scene declares the variant),
 * so this page sets the one unfitted number that decides whether a window reads as a lens or as
 * fog: the base σ, to 1.0, which puts the window body at σ 7.5–9.6 px, beside the regular body's
 * measured 9.4–12. Nothing else moves. The runtime reports `tuned: true` for it and the page's
 * readout says so.
 */
export const CLEAR_BLUR_SIGMA = 0.6;
/** The shipped clear body is a tenth of white; over a night sky that is a grey plate (the sweep). */
export const CLEAR_TINT_ALPHA = 0.02;
/**
 * How much of the regular material's fitted tone response the clear body keeps: none. The runtime
 * resolves clear's adaptation as `constrained` and reads it nowhere, so the fitted response — which
 * solves the body's occlusion up until the body reaches Apple's measured level (a flat plate over
 * a dark sky; over black, the light material's quiet mid-grey of 132 codes) — applies to clear in
 * full. This page stands the response and its black branch down for clear and makes the dimming
 * layer the adaptation instead, as the variant's contract says: the body transmits, and the page
 * takes the legibility job (`DIMMING`). The light material's remaining lift on a night sky was
 * measured at encoded 0.42 with the response at a tenth — inside the ink dead band — so a tenth
 * was not enough.
 */
export const CLEAR_TONE_STRENGTH = 0;
export const MATERIAL_TUNE: RendererMaterialProfile = tuneWith(CLEAR_BLUR_SIGMA, CLEAR_TINT_ALPHA, CLEAR_TONE_STRENGTH);

/**
 * The body's heavy scatter component, stood down: the fitted regular body mixes a sharp blur with
 * a heavy one (the chain level `sizeScatterGainMax` times wider, a share that rises with span),
 * which is what turns a window-sized body into fog whatever its base σ. A gain of 1 makes the
 * heavy level the sharp one, so the clear body is a single blur at its base σ; the light
 * document's 14 device px heavy tap is stood down with it. The regular material is untouched by
 * this page; nothing here draws it.
 */
export function tuneWith(blurSigma: number, tintAlpha: number, toneStrength: number): RendererMaterialProfile {
  return {
    optics: { clear: { blurSigma, tintAlpha } },
    backdropToneResponseStrength: toneStrength,
    backdropToneBlackStrength: toneStrength,
    sizeScatterGainMax: 1,
    sizeScatterGainMax2x: 1,
    sizeScatterGainFar2x: 1,
    sizeHeavyTapSigma: 0,
    sizeHeavyTapSigma2x: 0,
    // The size law's occlusion facet (0.05 of the neutral at window span, fitted on regular): on
    // the light material that is a twentieth of white laid over a night sky, a plate.
    sizeOcclusionGain: 0,
  };
}

/**
 * The dimming layer the clear variant requires, painted by the page into the sky under each
 * footprint (neither tier draws a scrim). It is ADAPTIVE: the strength under each host is derived
 * from the undimmed level measured under that host so that the composite the glass samples stays
 * at or below `targetLuminance` (linear), never below `floor` and never above `max`. At night the
 * floor holds and the sky shows through; by day the same window shades a blue sky to a level its
 * white ink can be read on. Uncalibrated, and the record says so.
 */
export const DIMMING = {
  floor: 0.16,
  max: 0.92,
  /** Linear relative luminance of the composite under a footprint, encoded about 0.24. */
  targetLuminance: 0.046,
  /**
   * CSS px inside the footprint's edge over which the layer fades to nothing at the edge: a share
   * of the host's shorter span, so a 48 px capsule keeps its middle dimmed (a fixed 22 px feather
   * left it half undimmed and lifted its declared level into the light pole by day).
   */
  featherShare: 0.12,
  featherMin: 5,
  featherMax: 16,
} as const;

export function featherFor(span: number): number {
  return Math.max(DIMMING.featherMin, Math.min(DIMMING.featherMax, span * DIMMING.featherShare));
}

export function dimmingFor(rawLuminance: number): number {
  if (rawLuminance <= 0) return DIMMING.floor;
  return Math.min(DIMMING.max, Math.max(DIMMING.floor, 1 - DIMMING.targetLuminance / rawLuminance));
}

/** A host's box written as the inline offsets a fixed host needs; nothing else goes inline. */
export function boxStyle(box: Box): CSSProperties {
  return {
    position: "fixed",
    left: box.x,
    top: box.y,
    width: box.width,
    height: box.height,
    boxSizing: "border-box",
  };
}

/** A registered host's footprint as the glass draws it. */
export interface HostShape {
  readonly id: string;
  readonly box: Box;
  readonly radius: number;
}

/** What every group is told about its material: clear, and the dimming the page paints for it. */
export interface GroupMaterial {
  readonly variant: "clear";
  readonly dimming: DimmingPolicy;
}

export function groupMaterial(strength: number | undefined): GroupMaterial {
  return { variant: "clear", dimming: { scrim: Math.round((strength ?? DIMMING.floor) * 1000) / 1000, direction: "darken" } };
}
