/**
 * Where everything sits: the watch on the bench, the loupe's resting place, and the glass
 * controls in the column beside the watch.
 *
 * Every number the painter and the glass share comes from here, so the crystal's circle and the
 * painted watch are one geometry. Two arrangements: `wide`, the watch left of centre with its
 * strap running off the top and bottom of the window and the controls in a column to its right;
 * and `stacked`, for a tall or narrow window, the watch above and the controls below it.
 */

export interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface Circle {
  readonly cx: number;
  readonly cy: number;
  readonly r: number;
}

/** The crystals a person can fit, and the calibrated material the page compares against. */
export type CrystalId = "flat" | "domed" | "box" | "apple";

export interface Layout {
  readonly width: number;
  readonly height: number;
  readonly mode: "wide" | "stacked";
  /** The case: `r` is the case's radius, the unit every part of the watch is drawn in. */
  readonly watch: Circle;
  /** The crystal's circle: inside the bezel, over the flange and the dial. */
  readonly crystal: Circle;
  /** The dial switch (Day, Night) and the crystal menu's capsule: the settings row. */
  readonly dial: Box;
  readonly crystalMenu: Box;
  /** The timing window: the running time and the laps. */
  readonly timing: Box;
  readonly lapButton: Circle;
  readonly startButton: Circle;
  /** Where the loupe rests when nobody holds it. */
  readonly loupeRest: Circle;
  /** The painted title's origin and size; size 0 paints none. */
  readonly title: { readonly x: number; readonly y: number; readonly size: number };
  /**
   * Whether the watch wears its strap, running off the top and bottom of the window. Without it
   * the head lies on the bench as a watchmaker works on it, spring bars bare between the lugs.
   */
  readonly strap: boolean;
}

import {
  DEFAULT_GROUP_SAMPLING,
  NOMINAL_ACCESSIBILITY_POLICY,
  type ResolvedMaterialPolicy,
} from "@vitreajs/vitrea";
import { samplingPaddingFor, type GlassMaterialProfileDocument } from "@vitreajs/vitrea-web";

/** The crystal's radius as a fraction of the case's (the bezel's inner edge). */
export const CRYSTAL_OF_CASE = 0.87;

const clamp = (v: number, lo: number, hi: number): number => Math.min(hi, Math.max(lo, v));

/**
 * The gap two neighbouring groups in the column need, from the runtime's own law: the larger
 * sampling padding of any member the column holds, under the policy in force and under the
 * nominal one, so a preference that removes blur never pulls the controls together. Taken on the
 * calibrated endpoint, which blurs more than the page's optical tuning, so one gap serves both
 * the tuned page and the calibrated comparison.
 */
export interface Gaps {
  /** Between the timing window and anything beside it. */
  readonly window: number;
  /** Between two controls, neither of them the window. */
  readonly controls: number;
}

export function derivedGaps(
  document: GlassMaterialProfileDocument,
  scheme: "light" | "dark",
  material: ResolvedMaterialPolicy,
): Gaps {
  const controls: readonly (readonly [number, number])[] = [
    [222, 44],
    [140, 44],
    [88, 88],
  ];
  return {
    window: derivedGap(document, scheme, material, [[392, 700], ...controls]),
    controls: derivedGap(document, scheme, material, controls),
  };
}

function derivedGap(
  document: GlassMaterialProfileDocument,
  scheme: "light" | "dark",
  material: ResolvedMaterialPolicy,
  members: readonly (readonly [number, number])[],
): number {
  const endpoint = document.active[scheme];
  let widest: number = DEFAULT_GROUP_SAMPLING.samplingPadding;
  for (const policy of [material, NOMINAL_ACCESSIBILITY_POLICY.material]) {
    for (const member of members) {
      widest = Math.max(
        widest,
        samplingPaddingFor({
          members: [member],
          material: policy,
          profile: endpoint.patch,
          cssTierMapping: document.cssTierMapping,
        }),
      );
    }
  }
  return Math.ceil(widest);
}

export function computeLayout(width: number, height: number, gap: Gaps): Layout {
  const wide = width >= 900 && width / height >= 1.15;
  return wide ? wideLayout(width, height, gap) : stackedLayout(width, height, gap);
}

function wideLayout(width: number, height: number, gap: Gaps): Layout {
  const margin = clamp(width * 0.035, 24, 56);
  const columnWidth = clamp(width * 0.26, 320, 392);
  const columnX = width - margin - columnWidth;
  // The watch fills the height it is given, leaving room for the crown and the loupe beside it.
  const r = Math.round(Math.min(height * 0.4, (columnX - margin) * 0.36));
  const cx = Math.round(Math.max(margin + r * 1.55, (columnX - margin * 0.5) * 0.53));
  const cy = Math.round(height / 2);

  const titleSize = clamp(width * 0.018, 20, 28);
  // The settings row heads the column: the dial on the left, the crystal on the right.
  const dial = { x: columnX, y: margin, width: 140, height: 44 };
  const menuWidth = Math.min(214, columnWidth - 140 - gap.controls);
  const crystalMenu = { x: columnX + columnWidth - menuWidth, y: margin, width: menuWidth, height: 44 };
  const button = 44;
  const buttonsY = height - margin - button;
  const timingTop = margin + 44 + gap.window;
  const timing = {
    x: columnX,
    y: timingTop,
    width: columnWidth,
    height: Math.max(220, buttonsY - button - gap.window - timingTop),
  };
  const loupeR = Math.round(clamp(r * 0.27, 64, 96));
  return {
    width,
    height,
    mode: "wide",
    watch: { cx, cy, r },
    crystal: { cx, cy, r: Math.round(r * CRYSTAL_OF_CASE) },
    dial,
    crystalMenu,
    timing,
    lapButton: { cx: columnX + button, cy: buttonsY, r: button },
    startButton: { cx: columnX + columnWidth - button, cy: buttonsY, r: button },
    loupeRest: {
      cx: Math.round(Math.max(margin + loupeR + 8, cx - r * 1.62)),
      cy: Math.round(height - margin - loupeR - 12),
      r: loupeR,
    },
    title: { x: margin, y: margin + titleSize * 0.8, size: titleSize },
    strap: true,
  };
}

/**
 * A tall or narrow window: the settings row on top, the timing window and the two buttons at the
 * foot, and the watch as large as the height between them allows. The watch lies here without
 * its strap, so no glass sits over leather.
 */
function stackedLayout(width: number, height: number, gap: Gaps): Layout {
  const margin = clamp(width * 0.05, 16, 40);
  const columnWidth = Math.min(width - margin * 2, 440);
  const columnX = Math.round((width - columnWidth) / 2);
  const titled = width >= 600;
  const settingsY = titled ? margin + 56 : margin;
  const dialWidth = 132;
  const menuWidth = Math.min(214, columnWidth - dialWidth - gap.controls);
  const dial = { x: columnX, y: settingsY, width: dialWidth, height: 44 };
  const crystalMenu = { x: columnX + columnWidth - menuWidth, y: settingsY, width: menuWidth, height: 44 };
  const button = 40;
  const buttonsY = height - margin - button;
  const timingHeight = Math.round(clamp(height * 0.24, 168, 300));
  const timing = {
    x: columnX,
    y: Math.round(buttonsY - button - gap.window - timingHeight),
    width: columnWidth,
    height: timingHeight,
  };
  // The watch between the settings row and the timing window, its crown inside the window.
  const top = settingsY + 44 + gap.window;
  const bottom = timing.y - gap.window;
  const r = Math.round(Math.min(width / 2.35, (bottom - top) / 2.05));
  const cx = Math.round(width / 2 - r * 0.05);
  const cy = Math.round((top + bottom) / 2);
  const loupeR = Math.round(clamp(r * 0.27, 44, 72));
  return {
    width,
    height,
    mode: "stacked",
    watch: { cx, cy, r },
    crystal: { cx, cy, r: Math.round(r * CRYSTAL_OF_CASE) },
    dial,
    crystalMenu,
    timing,
    lapButton: { cx: columnX + button, cy: buttonsY, r: button },
    startButton: { cx: columnX + columnWidth - button, cy: buttonsY, r: button },
    // At rest on the crystal, over the date: on a small screen the loupe starts at work.
    loupeRest: { cx: Math.round(cx + r * 0.42), cy: Math.round(cy + r * 0.42), r: loupeR },
    title: { x: margin, y: margin + 14, size: titled ? 18 : 0 },
    strap: false,
  };
}
