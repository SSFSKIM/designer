/**
 * The page's material: one tuning of vitrea's macOS 27 glass toward clear optics, and the
 * crystals it is fitted as.
 *
 * The runtime's default is Apple's measured macOS 27 material, a frosted body calibrated against
 * native captures. This page asks for glass you can see a dial through, so it changes the leaves
 * that make the body frosted and leaves the lens alone:
 *
 * - the body's own blur down to a fraction of a pixel, its white plate nearly gone, and the size
 *   law's extra opacity and heavy scatter off, so a large surface is as clear as a small one;
 * - the backdrop tone response off, so the body is the backdrop's own level rather than a
 *   material level solved toward it, and the body keeps all of the backdrop's colour;
 * - the lens's height law, capped at 20 px on the calibrated material, allowed to keep growing
 *   with the span to 160, so a large crystal refracts across a band as wide as its size asks.
 *
 * The lens's own profile, gain and reach are the calibrated ones, which is why a small control
 * here bends its backdrop exactly as it does on the default material. Every surface on the page
 * shares this tuning; thickness is the one per-surface lever, and each crystal is a thickness.
 * The runtime reports the result as `tuned`, and the Crystal menu's last choice puts the
 * calibrated material back on the whole page for comparison (DESIGN.md, "The material").
 */

import type { RendererMaterialProfile } from "@vitreajs/vitrea-web";

import type { CrystalId, Layout } from "./layout";

export const OPTICAL_PROFILE: RendererMaterialProfile = {
  optics: { regular: { blurSigma: 0.35, tintAlpha: 0.06, rimAlpha: 0.24 } },
  sizeOcclusionGain: 0,
  sizeScatterGainMax: 1,
  sizeScatterGainMax2x: 1,
  sizeScatterGainFar2x: 1,
  sizeHeavyTapSigma: 0,
  sizeHeavyTapSigma2x: 0,
  backdropToneResponseStrength: 0,
  bodyChromaRetention: 1,
  lensHeightMax: 160,
};

export interface Crystal {
  readonly id: CrystalId;
  readonly name: string;
  readonly note: string;
  /** The crystal's thickness in CSS px: on this material, how deep its lens reaches. */
  readonly thickness: number;
  /** Whether the page's optical tuning applies, or the calibrated material draws. */
  readonly tuned: boolean;
}

export const CRYSTALS: readonly Crystal[] = [
  { id: "flat", name: "Flat sapphire", note: "Thin; only the flange bends", thickness: 3, tuned: true },
  { id: "domed", name: "Domed sapphire", note: "The edge draws the dial outward", thickness: 6, tuned: true },
  { id: "box", name: "Box hesalite", note: "A tall acrylic dome", thickness: 12, tuned: true },
  {
    id: "apple",
    name: "Apple’s glass",
    note: "vitrea’s calibrated macOS 27 material",
    thickness: 8,
    tuned: false,
  },
];

export const crystalById = (id: CrystalId): Crystal => CRYSTALS.find((c) => c.id === id) ?? CRYSTALS[1]!;

/**
 * The crystal's thickness for the watch as drawn. A crystal's depth is a proportion of the watch,
 * so its thickness scales with the case, taken from the design's 348 px case radius; the
 * calibrated comparison keeps the material's reference thickness at every size.
 */
export const crystalThickness = (crystal: Crystal, layout: Layout): number =>
  crystal.tuned ? Math.max(1, Math.round(crystal.thickness * (layout.watch.r / 348) * 10) / 10) : crystal.thickness;

/** Everything on the page reads the one painted canvas. */
export const BENCH_TEXTURE = "bench";
export const BENCH_BACKDROP = { kind: "texture", id: BENCH_TEXTURE } as const;

/** Controls and windows keep the calibrated control thickness. */
export const CONTROL_THICKNESS = 8;
export const TIMING_THICKNESS = 6;
export const TIMING_RADIUS = 30;
/** The loupe: thick enough that its rim bends visibly, thin enough to leave its centre flat. */
export const LOUPE_THICKNESS = 4;
