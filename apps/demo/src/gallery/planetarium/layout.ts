/**
 * Where the window, the module and the two ornaments stand, from the viewport and the runtime's
 * gap. The boxes are the design's; the GAP is the larger of the sampling paddings of the groups it
 * separates, derived by the runtime from the blur it will actually draw for this page's material
 * — the clear variant with its tuned base σ — so it moves with the colour scheme and rises under
 * Reduce Transparency, and never sits below the nominal policy's answer.
 */

import {
  DEFAULT_GROUP_SAMPLING,
  NOMINAL_ACCESSIBILITY_POLICY,
  type ResolvedMaterialPolicy,
} from "@vitreajs/vitrea";
import {
  samplingPaddingFor,
  type GlassMaterialProfileDocument,
  type RendererMaterialProfile,
} from "@vitreajs/vitrea-web";

import { MATERIAL_TUNE } from "./shared";
import type { Box } from "./sky/renderer";

export const DESIGN = {
  window: { width: 400, height: 560, minHeight: 430 },
  /** The compact arrangement's window: narrower and shorter, so a column of open sky stays. */
  compactWindow: { minWidth: 300, minHeight: 360 },
  module: { width: 320, height: 176 },
  ornament: { height: 48 },
  /**
   * The ornaments' closed faces are fixed boxes this size (the morph measures its closed face
   * once), each wide enough for its longest content at rest: "San Francisco · 37.8° N · 122.4° W".
   */
  place: { width: 320 },
  time: { width: 372 },
  /** The platters as they measure open, and the morphs' gap between an ornament and its platter. */
  timePlatter: { width: 400, height: 244 },
  placePlatter: { width: 400, height: 504 },
  platterGap: 8,
} as const;

const MARGIN = 48;
/** The narrowest margin the layout takes, at the viewport's edge. */
const MIN_MARGIN = 24;
/**
 * The standard arrangement's viewport, below which the compact one is tried first. The fit test
 * below is what protects the arrangement; the height here only says where a 560 px window stops
 * being the first thing tried (common laptop viewports, 1366 × 768 and 1440 × 780, keep it).
 */
const STANDARD_VIEWPORT = { width: 1240, height: 700 } as const;

export type Arrangement = "standard" | "compact" | "clamped";

export interface Layout {
  /** Which arrangement held: `clamped` is the compact one pressed inside a viewport it overflows. */
  readonly arrangement: Arrangement;
  readonly gap: number;
  readonly window: Box;
  readonly module: Box;
  readonly place: Box;
  readonly time: Box;
  /** Where each ornament's platter opens (`below-start` and `above-start` of its anchor). */
  readonly placePlatter: Box;
  readonly timePlatter: Box;
}

/** The tune this page draws, merged over an endpoint's patch as the root merges it. */
export function tunedPatch(patch: RendererMaterialProfile | undefined): RendererMaterialProfile {
  return {
    ...patch,
    ...MATERIAL_TUNE,
    optics: {
      ...patch?.optics,
      clear: { ...patch?.optics?.clear, ...MATERIAL_TUNE.optics?.clear },
    },
  };
}

export function derivedGap(
  document: GlassMaterialProfileDocument,
  scheme: "light" | "dark",
  material: ResolvedMaterialPolicy,
): number {
  const members: readonly (readonly [number, number])[] = [
    [DESIGN.window.width, DESIGN.window.height],
    [DESIGN.module.width, DESIGN.module.height],
    [DESIGN.place.width, DESIGN.ornament.height],
    [DESIGN.time.width, DESIGN.ornament.height],
    [DESIGN.timePlatter.width, DESIGN.timePlatter.height],
    [DESIGN.placePlatter.width, DESIGN.placePlatter.height],
  ];
  const endpoint = document.active[scheme];
  const profile = tunedPatch(endpoint.patch);
  let widest: number = DEFAULT_GROUP_SAMPLING.samplingPadding;
  for (const policy of [material, NOMINAL_ACCESSIBILITY_POLICY.material]) {
    for (const member of members) {
      widest = Math.max(
        widest,
        samplingPaddingFor({
          members: [member],
          material: policy,
          variant: "clear",
          profile,
          cssTierMapping: document.cssTierMapping,
        }),
      );
    }
  }
  return Math.ceil(widest);
}

/**
 * `gap` is the runtime's derived padding; the composition never goes below it and gives at least
 * `AIR` px between glass, the design's own number. `horizonAt(x)` is the screen row where the
 * drawn ridge crosses column `x` (`horizonYAt`): an ornament or module low in the scene stays 10
 * px above it at its own centre, over sky, so no glass sits on the ground's flat dark. The two
 * ornaments act on the whole scene, sky and window alike, so they hang at the edges of the open
 * sky: Place at the top, its platter opening downward into sky, Time at the bottom, its platter
 * opening upward — never over the window or the module (the spatial register's texture-path rule).
 *
 * Two arrangements, and a floor under both. STANDARD, on a viewport of at least 1240 × 820 whose
 * open sky between window and module holds a platter: the window top-left, the module top-right,
 * Place at the top of the sky between them and Time at the bottom centre of the sky right of the
 * window. COMPACT otherwise: the window and the module below it make a left column, and both
 * ornaments hang in the right column of open sky, which is kept at a platter's width by narrowing
 * the window first (to 300). Where neither fits without one footprint meeting another, the
 * compact boxes are CLAMPED inside the viewport and may overlap, the window rather than the edge
 * giving way; no box ever leaves the viewport or takes a negative size.
 */
const AIR = 32;

export function computeLayout(
  viewport: { readonly width: number; readonly height: number },
  derived: number,
  horizonAt: (x: number) => number | undefined,
): Layout {
  const gap = Math.max(derived, AIR);
  const margin = Math.max(MIN_MARGIN, Math.min(MARGIN, Math.round(viewport.width * 0.035)));
  if (viewport.width >= STANDARD_VIEWPORT.width && viewport.height >= STANDARD_VIEWPORT.height) {
    const standard = standardLayout(viewport, gap, margin, horizonAt);
    if (standard !== undefined && fits(standard, viewport)) return standard;
  }
  const compact = compactLayout(viewport, gap, margin, horizonAt);
  if (compact.fitsColumn && fits(compact.layout, viewport)) return compact.layout;
  return clampedLayout(compact.layout, viewport);
}

/** The standard arrangement, or `undefined` when the open sky between window and module is too
 * narrow for the Place platter. */
function standardLayout(
  viewport: { readonly width: number; readonly height: number },
  gap: number,
  margin: number,
  horizonAt: (x: number) => number | undefined,
): Layout | undefined {
  const { width, height } = viewport;
  const windowHeight = Math.max(DESIGN.window.minHeight, Math.min(DESIGN.window.height, height - 2 * margin));
  const windowWidth = Math.min(DESIGN.window.width, Math.max(320, width - 2 * margin - DESIGN.module.width - gap));
  const window: Box = { x: margin, y: margin, width: windowWidth, height: windowHeight };
  const skyLeft = window.x + window.width + gap;
  const skyRight = width - margin;
  const module: Box = {
    x: Math.max(skyLeft, skyRight - DESIGN.module.width),
    y: margin,
    width: DESIGN.module.width,
    height: DESIGN.module.height,
  };
  const placeRight = module.x - gap;
  if (placeRight - skyLeft < DESIGN.placePlatter.width || skyRight - skyLeft < DESIGN.timePlatter.width) return undefined;
  const place = hangTop(skyLeft, placeRight, margin);
  const time = clearOfPlatter(hangBottom(skyLeft, skyRight, height - margin, horizonAt), place, gap, height - MIN_MARGIN);
  return withPlatters("standard", gap, window, module, { place, time });
}

/** The compact arrangement, and whether its right column holds a platter. */
function compactLayout(
  viewport: { readonly width: number; readonly height: number },
  gap: number,
  margin: number,
  horizonAt: (x: number) => number | undefined,
): { readonly layout: Layout; readonly fitsColumn: boolean } {
  const { width, height } = viewport;
  const column = Math.max(DESIGN.placePlatter.width, DESIGN.timePlatter.width);
  const windowWidth = Math.max(
    0,
    Math.min(
      DESIGN.window.width,
      width - 2 * margin,
      Math.max(DESIGN.compactWindow.minWidth, width - 2 * margin - column - gap),
    ),
  );
  const moduleWidth = Math.min(DESIGN.module.width, windowWidth);
  const moduleBottom = Math.min(height - margin, (horizonAt(margin + moduleWidth / 2) ?? height) - 10);
  const windowHeight = Math.max(
    DESIGN.compactWindow.minHeight,
    Math.min(DESIGN.window.height, moduleBottom - DESIGN.module.height - gap - margin),
  );
  const window: Box = { x: margin, y: margin, width: windowWidth, height: windowHeight };
  const module: Box = { x: margin, y: window.y + window.height + gap, width: moduleWidth, height: DESIGN.module.height };
  const columnLeft = window.x + window.width + gap;
  const columnRight = width - margin;
  const place = hangTop(columnLeft, columnRight, margin);
  const time = clearOfPlatter(hangBottom(columnLeft, columnRight, height - margin, horizonAt), place, gap, height - MIN_MARGIN);
  return {
    fitsColumn: columnRight - columnLeft >= column,
    layout: withPlatters("compact", gap, window, module, { place, time }),
  };
}

/**
 * An ornament at the top of a span of sky: centred in it, moved left if its platter, which opens
 * from the ornament's start, would run past the span's end.
 */
function hangTop(left: number, right: number, top: number): Box {
  const width = DESIGN.place.width;
  const centred = Math.round(left + (right - left - width) / 2);
  return { x: Math.min(centred, right - DESIGN.placePlatter.width), y: top, width, height: DESIGN.ornament.height };
}

/** An ornament at the bottom of a span of sky, above the ridge at its own centre. */
function hangBottom(left: number, right: number, bottom: number, horizonAt: (x: number) => number | undefined): Box {
  const width = DESIGN.time.width;
  const centred = Math.round(left + (right - left - width) / 2);
  const x = Math.min(centred, right - DESIGN.timePlatter.width);
  const floor = Math.min(bottom, (horizonAt(x + width / 2) ?? Infinity) - 10);
  return { x, y: floor - DESIGN.ornament.height, width, height: DESIGN.ornament.height };
}

/**
 * The Time ornament kept a gap below the open Place platter where the two share the sky's width.
 * Where the ridge leaves no room for both, the ornament gives up the ridge before its clearance
 * and goes lower, onto the ground and into the margin if it must, as far as `bottom`: glass on the
 * ground's dark is a weaker composition, a platter over the ornament hides the platter's own Done.
 */
function clearOfPlatter(time: Box, place: Box, gap: number, bottom: number): Box {
  const platterBottom = place.y + place.height + DESIGN.platterGap + DESIGN.placePlatter.height;
  const shareWidth = time.x < place.x + DESIGN.placePlatter.width && place.x < time.x + time.width;
  if (!shareWidth || time.y >= platterBottom + gap) return time;
  return { ...time, y: Math.max(time.y, Math.min(platterBottom + gap, bottom - time.height)) };
}

function withPlatters(
  arrangement: Arrangement,
  gap: number,
  window: Box,
  module: Box,
  ornaments: { readonly place: Box; readonly time: Box },
): Layout {
  const { place, time } = ornaments;
  return {
    arrangement,
    gap,
    window,
    module,
    place,
    time,
    placePlatter: {
      x: place.x,
      y: place.y + place.height + DESIGN.platterGap,
      width: DESIGN.placePlatter.width,
      height: DESIGN.placePlatter.height,
    },
    timePlatter: {
      x: time.x,
      y: time.y - DESIGN.platterGap - DESIGN.timePlatter.height,
      width: DESIGN.timePlatter.width,
      height: DESIGN.timePlatter.height,
    },
  };
}

function inside(box: Box, viewport: { readonly width: number; readonly height: number }): boolean {
  return box.x >= 0 && box.y >= 0 && box.x + box.width <= viewport.width && box.y + box.height <= viewport.height;
}

export function meets(a: Box, b: Box): boolean {
  return a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
}

/**
 * Every footprint, closed and open, inside the viewport; no two closed ones meeting; and each
 * platter meeting none of the other three surfaces. Only one platter is open at a time.
 */
function fits(layout: Layout, viewport: { readonly width: number; readonly height: number }): boolean {
  const { window, module, place, time, placePlatter, timePlatter } = layout;
  const closed = [window, module, place, time];
  if (![...closed, placePlatter, timePlatter].every((box) => inside(box, viewport))) return false;
  for (let i = 0; i < closed.length; i += 1) {
    for (let j = i + 1; j < closed.length; j += 1) {
      if (meets(closed[i] as Box, closed[j] as Box)) return false;
    }
  }
  return (
    ![window, module, time].some((box) => meets(placePlatter, box)) &&
    ![window, module, place].some((box) => meets(timePlatter, box))
  );
}

/** Pressed inside the viewport: sizes bounded by it, and each ornament placed so its platter is too. */
function clampedLayout(layout: Layout, viewport: { readonly width: number; readonly height: number }): Layout {
  const { width, height } = viewport;
  const clamp = (box: Box, room: { readonly width: number; readonly height: number } = box): Box => {
    const w = Math.max(0, Math.min(box.width, width));
    const h = Math.max(0, Math.min(box.height, height));
    const roomW = Math.min(Math.max(w, room.width), width);
    return {
      x: Math.max(0, Math.min(box.x, width - roomW)),
      y: Math.max(0, Math.min(box.y, height - h)),
      width: w,
      height: h,
    };
  };
  const place = clamp(layout.place, DESIGN.placePlatter);
  const time = clamp(layout.time, DESIGN.timePlatter);
  const openBelow = DESIGN.ornament.height + DESIGN.platterGap + DESIGN.placePlatter.height;
  const openAbove = DESIGN.platterGap + DESIGN.timePlatter.height;
  return withPlatters(
    "clamped",
    layout.gap,
    clamp(layout.window),
    clamp(layout.module),
    {
      place: { ...place, y: Math.max(0, Math.min(place.y, height - openBelow)) },
      time: { ...time, y: Math.min(Math.max(time.y, openAbove), Math.max(0, height - time.height)) },
    },
  );
}
