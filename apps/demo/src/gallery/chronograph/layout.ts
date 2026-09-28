/**
 * Where everything sits: the watch on the bench, the loupe's resting place, and the glass
 * controls in the column beside the watch.
 *
 * Every number the painter and the glass share comes from here, so the crystal's circle and the
 * painted watch are one geometry. Two arrangements: `wide`, the watch left of centre with its
 * strap running off the top and bottom of the window and the controls in a column to its right;
 * and `stacked`, for a portrait or narrow window, the watch above and the controls below it. A
 * short landscape window, a phone held sideways, is wide with a compact column.
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

/**
 * The gaps for a viewport. The padding grows with a member's span, so the timing window's member
 * is its box on this viewport, not a fixed large one: a short window would otherwise be held apart
 * by the padding of a 700 px window it is not, and lose the height that padding takes.
 */
export function derivedGaps(
  document: GlassMaterialProfileDocument,
  scheme: "light" | "dark",
  material: ResolvedMaterialPolicy,
  viewport: { readonly width: number; readonly height: number },
): Gaps {
  const controls: readonly (readonly [number, number])[] = [
    [222, 44],
    [140, 44],
    [88, 88],
  ];
  return {
    window: windowGap(viewport.width, viewport.height, (timing) =>
      derivedGap(document, scheme, material, [timing, ...controls]),
    ),
    controls: derivedGap(document, scheme, material, controls),
  };
}

/**
 * The timing window's gap on this viewport. The stacked window's height is fixed by the viewport,
 * so its box is known. The wide window takes the height between the settings row and the buttons
 * less a gap on each side, so its box depends on the gap it is given: a larger gap leaves a
 * shorter window, whose padding is smaller. The gap is the smallest whole pixel that covers the
 * padding of the window it leaves, which is exactly what the runtime then derives for that window,
 * found by bisection because the window's padding only falls as the gap grows.
 */
function windowGap(width: number, height: number, gapFor: (timing: readonly [number, number]) => number): number {
  if (!isWide(width, height)) {
    const c = stackedColumn(width, height);
    return gapFor([c.columnWidth, c.timingHeight]);
  }
  const c = wideColumn(width, height);
  const available = c.buttonsY - c.button - (c.margin + c.settings);
  const windowAt = (gap: number): readonly [number, number] => [
    c.columnWidth,
    Math.max(MIN_TIMING_HEIGHT, available - gap * 2),
  ];
  let lo = 0;
  let hi = gapFor(windowAt(0));
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (gapFor(windowAt(mid)) <= mid) hi = mid;
    else lo = mid + 1;
  }
  return hi;
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

/**
 * The smallest case radius either layout draws. No real window is this small; the floor is there
 * so an absurd one overlaps rather than painting a negative circle, which the canvas refuses.
 */
const MIN_WATCH_RADIUS = 40;

/** The smallest timing window: its label and running time, with the laps scrolling under them. */
const MIN_TIMING_HEIGHT = 96;

/**
 * Below this height the wide layout compacts its column: smaller buttons and settings row, and a
 * larger share of the width, so the timing window keeps a usable height on a phone held sideways.
 * `chronograph.css` compacts the window's head and the crystal capsule at the same height.
 */
const SHORT_HEIGHT = 600;

/**
 * A window goes wide when it is landscape and wide enough for the watch and the column side by
 * side, which a phone held sideways is. Stacking it instead would leave the watch the height
 * between a settings row and a timing window, which on a short window is nothing.
 */
const isWide = (width: number, height: number): boolean => width >= 640 && width / height >= 1.15;

/**
 * The wide layout's column: its margin, its box, the settings row and the buttons' row. A short
 * column is never narrower than 284 px, which is what the settings row needs for the dial switch,
 * the gap and a capsule that still holds its longest crystal name ("Domed sapphire", the default).
 */
function wideColumn(width: number, height: number) {
  const short = height < SHORT_HEIGHT;
  const margin = clamp(width * 0.035, 24, 56);
  const columnWidth = short ? clamp(width * 0.34, 284, 392) : clamp(width * 0.26, 320, 392);
  const settings = short ? 40 : 44;
  const button = short ? 30 : 44;
  return {
    short,
    margin,
    columnWidth,
    columnX: width - margin - columnWidth,
    settings,
    dialWidth: short ? 120 : 140,
    button,
    buttonsY: height - margin - button,
  };
}

/** The stacked layout's column: its margin, its box, the settings row and the timing window. */
function stackedColumn(width: number, height: number) {
  const margin = clamp(width * 0.05, 16, 40);
  const titled = width >= 600;
  return {
    margin,
    columnWidth: Math.min(width - margin * 2, 440),
    titled,
    settingsY: titled ? margin + 56 : margin,
    timingHeight: Math.round(clamp(height * 0.24, 168, 300)),
  };
}

export function computeLayout(width: number, height: number, gap: Gaps): Layout {
  return isWide(width, height) ? wideLayout(width, height, gap) : stackedLayout(width, height, gap);
}

function wideLayout(width: number, height: number, gap: Gaps): Layout {
  const { short, margin, columnWidth, columnX, settings, dialWidth, button, buttonsY } = wideColumn(width, height);
  // The watch fills the height it is given, leaving room for the crown and, on a window tall
  // enough to rest it on the mat, the loupe beside it. On a short one the loupe starts on the
  // dial, so the watch only keeps its own case and shadow off the left edge.
  const r = Math.max(MIN_WATCH_RADIUS, Math.round(Math.min(height * 0.4, (columnX - margin) * 0.36)));
  const cx = Math.round(Math.max(margin + r * (short ? 1.15 : 1.55), (columnX - margin * 0.5) * 0.53));
  const cy = Math.round(height / 2);

  const titleSize = clamp(width * 0.018, 20, 28);
  // The settings row heads the column: the dial on the left, the crystal on the right.
  const dial = { x: columnX, y: margin, width: dialWidth, height: settings };
  const menuWidth = Math.min(214, columnWidth - dialWidth - gap.controls);
  const crystalMenu = { x: columnX + columnWidth - menuWidth, y: margin, width: menuWidth, height: settings };
  // The timing window takes the height between the settings row and the buttons. On a short
  // window that can be little more than its running time; the laps then scroll inside it.
  const timingTop = margin + settings + gap.window;
  const timing = {
    x: columnX,
    y: timingTop,
    width: columnWidth,
    height: Math.max(MIN_TIMING_HEIGHT, buttonsY - button - gap.window - timingTop),
  };
  // On a short window the watch reaches from margin to margin and leaves the mat beside it no room
  // for the loupe's rest. The loupe then starts at work on the crystal over the date, as on a
  // stacked window. The title keeps the design's size here: bench.ts fits it beside the watch and
  // leaves it off where it cannot fit, as on a phone held sideways.
  const loupeR = Math.round(short ? clamp(r * 0.27, 44, 72) : clamp(r * 0.27, 64, 96));
  const loupeRest = short
    ? { cx: Math.round(cx + r * 0.42), cy: Math.round(cy + r * 0.42), r: loupeR }
    : {
        cx: Math.round(Math.max(margin + loupeR + 8, cx - r * 1.62)),
        cy: Math.round(height - margin - loupeR - 12),
        r: loupeR,
      };
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
    loupeRest,
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
  const { margin, columnWidth, titled, settingsY, timingHeight } = stackedColumn(width, height);
  const columnX = Math.round((width - columnWidth) / 2);
  const dialWidth = 132;
  const menuWidth = Math.min(214, columnWidth - dialWidth - gap.controls);
  const dial = { x: columnX, y: settingsY, width: dialWidth, height: 44 };
  const crystalMenu = { x: columnX + columnWidth - menuWidth, y: settingsY, width: menuWidth, height: 44 };
  const button = 40;
  const buttonsY = height - margin - button;
  const timing = {
    x: columnX,
    y: Math.round(buttonsY - button - gap.window - timingHeight),
    width: columnWidth,
    height: timingHeight,
  };
  // The watch between the settings row and the timing window, its crown inside the window. A
  // window too short for both (a landscape one narrower than the wide layout's minimum) leaves no
  // height between them; the watch then keeps its floor and overlaps rather than vanishing.
  const top = settingsY + 44 + gap.window;
  const bottom = timing.y - gap.window;
  const r = Math.max(MIN_WATCH_RADIUS, Math.round(Math.min(width / 2.35, (bottom - top) / 2.05)));
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
