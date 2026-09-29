/**
 * Where the window stands and where its ornaments hang. The window is the person's to move and
 * resize; this file gives it a first position, keeps it and its ornaments inside the viewport, and
 * places each ornament outside the window's edge by the GAP — the larger of the sampling paddings
 * of the groups it separates, derived by the runtime from the blur it will actually draw for the
 * material in use, so it moves with the scheme and the glass and rises under Reduce Transparency.
 *
 * Every ornament is fitted to its window as well as to the viewport: the sessions' row runs
 * within the window's width, its tabs narrowing (their names ellipsised, then set aside for the
 * number alone) as sessions are added; the profile row wraps into as many rows as the window's
 * width needs, each centred under it. Wherever two groups meet — side by side or row above row —
 * they stand the gap apart, and the space the rows take is reserved by the same arithmetic that
 * places them (`lowerRows`), so the window is never sized for rows it does not get.
 */

import { DEFAULT_GROUP_SAMPLING, NOMINAL_ACCESSIBILITY_POLICY, type ResolvedMaterialPolicy } from "@vitreajs/vitrea";
import { samplingPaddingFor, type GlassMaterialProfileDocument, type RendererMaterialProfile } from "@vitreajs/vitrea-web";

import { clearTune, type Box } from "./shared";
import type { GlassKind, Scheme } from "./shell/types";

export const DESIGN = {
  /**
   * The window's size: the design's, and the smallest the person may make it where the viewport
   * has room. Where it has none the window takes what there is, down to `floor`.
   */
  window: { width: 880, height: 560, minWidth: 520, minHeight: 320 },
  /**
   * The window's absolute floor, below which no viewport takes it. 296 wide is the narrowest
   * phone in use (320 CSS px) less the margins, about 30 columns of text inside the lens band;
   * 160 tall is the title line and five rows of the grid. Both clear the span floor of 96 the
   * spatial register sets for a window. A viewport too small for the floor and its ornaments
   * scrolls nothing and shows what fits, with the window's top-left corner kept on screen.
   */
  floor: { width: 296, height: 160 },
  /** The ornaments' height, and the widths the controls in them are set to. */
  ornament: 44,
  tab: 116,
  /** The narrowest tab: a circle concentric with its capsule, holding the session's number. */
  minTab: 36,
  /** Below this width a tab sets its name aside and shows its number alone. */
  namedTab: 64,
  newSession: 44,
  glassSwitch: 184,
  appearanceSwitch: 164,
  transparency: 226,
  maxSessions: 4,
} as const;

/** The viewport's margin around the whole assembly, and the narrowest the layout takes. */
const MARGIN = 32;
const MIN_MARGIN = 12;
/**
 * The band kept clear along the viewport's foot for the data credit (`terminal.css`, `.credit`):
 * one line of it and its inset, so no ornament is placed over it.
 */
const CREDIT_BAND = 28;
/** The sessions' row is set in from the window's corners by this much. */
const TAB_INSET = 8;
/** The tabs capsule's padding, which makes a tab concentric with it: 22 − 4 = 18. */
const CAPSULE_PADDING = 4;

type LowerId = "glassSwitch" | "appearanceSwitch" | "transparency";
const LOWER: readonly LowerId[] = ["glassSwitch", "appearanceSwitch", "transparency"];

export interface Assembly {
  readonly window: Box;
  readonly sessions: Box;
  readonly newSession: Box;
  readonly glassSwitch: Box;
  readonly appearanceSwitch: Box;
  readonly transparency: Box;
  /** Whether the tabs are too narrow to show the sessions' names. */
  readonly compactTabs: boolean;
}

type Viewport = { readonly width: number; readonly height: number };

/** The profile row's groups packed into rows no wider than the window, in order. */
function lowerRows(windowWidth: number, gap: number): LowerId[][] {
  const rows: LowerId[][] = [];
  let row: LowerId[] = [];
  let used = 0;
  for (const id of LOWER) {
    const width = DESIGN[id];
    if (row.length > 0 && used + gap + width > windowWidth) {
      rows.push(row);
      row = [];
      used = 0;
    }
    used += (row.length > 0 ? gap : 0) + width;
    row.push(id);
  }
  rows.push(row);
  return rows;
}

/** How much room the ornaments take above and below a window of this width. */
function bands(windowWidth: number, gap: number): { above: number; below: number } {
  const rows = lowerRows(windowWidth, gap).length;
  return { above: gap + DESIGN.ornament, below: rows * (gap + DESIGN.ornament) };
}

/** The margin at the viewport's foot: the side margin, or the credit's band where that is more. */
const footOf = (margin: number): number => Math.max(margin, CREDIT_BAND);

const clamp = (value: number, low: number, high: number): number => Math.max(low, Math.min(high, value));

/** The window's first box: as large as the design asks and the viewport allows, centred. */
export function firstWindow(viewport: Viewport, gap: number): Box {
  const margin = viewport.width < 640 ? MIN_MARGIN : MARGIN;
  const across = viewport.width - 2 * margin;
  const width = Math.max(DESIGN.floor.width, Math.min(DESIGN.window.width, across));
  const { above, below } = bands(width, gap);
  const room = viewport.height - margin - footOf(margin) - above - below;
  const height = Math.max(DESIGN.floor.height, Math.min(DESIGN.window.height, room));
  const x = Math.round((viewport.width - width) / 2);
  const y = Math.round(margin + above + Math.max(0, (room - height) / 2));
  return { x, y, width, height };
}

/**
 * A window's size for a top-left corner at (`left`, `top`): the size asked, no larger than the
 * room from that corner to the viewport's far margins with the ornaments' rows below, and no
 * smaller than the design's minimum where that fits or the floor where it does not.
 */
function sizeFrom(box: Box, viewport: Viewport, gap: number, left: number, top: number) {
  const widest = viewport.width - MIN_MARGIN - left;
  const width = Math.max(DESIGN.floor.width, clamp(box.width, Math.min(DESIGN.window.minWidth, widest), widest));
  const tallest = viewport.height - footOf(MIN_MARGIN) - bands(width, gap).below - top;
  const height = Math.max(DESIGN.floor.height, clamp(box.height, Math.min(DESIGN.window.minHeight, tallest), tallest));
  return { width: Math.round(width), height: Math.round(height) };
}

/**
 * Keeps a window the person moved inside the viewport with its ornaments: the size first, within
 * its minimum and the viewport, then the position. Where the viewport is too small for the floor,
 * the window's top-left corner stays on screen and the rest overflows.
 */
export function clampWindow(box: Box, viewport: Viewport, gap: number): Box {
  const { above } = bands(box.width, gap);
  const { width, height } = sizeFrom(box, viewport, gap, MIN_MARGIN, MIN_MARGIN + above);
  const { below } = bands(width, gap);
  const x = Math.round(clamp(box.x, MIN_MARGIN, viewport.width - MIN_MARGIN - width));
  const y = Math.round(clamp(box.y, MIN_MARGIN + above, viewport.height - footOf(MIN_MARGIN) - below - height));
  return { x, y, width, height };
}

/**
 * Keeps a window the person is resizing by its lower-right corner inside the viewport: its left and
 * top edges stay where they are and the width and height stop at the room there is, rather than
 * the window sliding away from the corner being dragged.
 */
export function clampResize(box: Box, viewport: Viewport, gap: number): Box {
  return clampWindow({ ...box, ...sizeFrom(box, viewport, gap, box.x, box.y) }, viewport, gap);
}

/** Each tab's width: the design's where the row has room, narrower down to a circle where not. */
function tabWidth(windowWidth: number, sessions: number, gap: number): number {
  const room = windowWidth - 2 * TAB_INSET - gap - DESIGN.newSession - 2 * CAPSULE_PADDING;
  return clamp(Math.floor(room / Math.max(1, sessions)), DESIGN.minTab, DESIGN.tab);
}

/** The ornaments around a window: the sessions above its left end, the profile rows below. */
export function assemble(window: Box, sessions: number, gap: number): Assembly {
  const top = window.y - gap - DESIGN.ornament;
  const tab = tabWidth(window.width, sessions, gap);
  const sessionsBox: Box = {
    x: window.x + TAB_INSET,
    y: top,
    width: sessions * tab + 2 * CAPSULE_PADDING,
    height: DESIGN.ornament,
  };
  const newSession: Box = {
    x: sessionsBox.x + sessionsBox.width + gap,
    y: top,
    width: DESIGN.newSession,
    height: DESIGN.ornament,
  };
  const rows = lowerRows(window.width, gap);
  const placed = {} as Record<LowerId, Box>;
  const middle = window.x + window.width / 2;
  let y = window.y + window.height + gap;
  for (const row of rows) {
    const width = row.reduce((sum, id) => sum + DESIGN[id], 0) + (row.length - 1) * gap;
    let x = Math.round(middle - width / 2);
    for (const id of row) {
      placed[id] = { x, y, width: DESIGN[id], height: DESIGN.ornament };
      x += DESIGN[id] + gap;
    }
    y += DESIGN.ornament + gap;
  }
  return {
    window,
    sessions: sessionsBox,
    newSession,
    glassSwitch: placed.glassSwitch,
    appearanceSwitch: placed.appearanceSwitch,
    transparency: placed.transparency,
    compactTabs: tab < DESIGN.namedTab,
  };
}

/**
 * The gap between groups: the widest sampling padding among the page's members for the material
 * in use, never below the nominal policy's answer. The members are the design's sizes and, once
 * the person has moved or resized the window, the box they asked for: a window grown past the
 * design's size samples a wider padding (the size law's blur grows with span), and the gap has to
 * follow it. The asked box is the one read, not the clamped one, because the clamp takes the gap
 * as an input: reading its output would make the gap and the clamp chase each other, and the
 * padding only grows with size, so the box before the clamp bounds the one after it.
 */
export function derivedGap(
  document: GlassMaterialProfileDocument,
  scheme: Scheme,
  glass: GlassKind,
  material: ResolvedMaterialPolicy,
  asked: Box | undefined,
): number {
  const members: (readonly [number, number])[] = [
    [DESIGN.window.width, DESIGN.window.height],
    [DESIGN.window.minWidth, DESIGN.window.minHeight],
    [DESIGN.tab * DESIGN.maxSessions + 2 * CAPSULE_PADDING, DESIGN.ornament],
    [DESIGN.transparency, DESIGN.ornament],
    [DESIGN.newSession, DESIGN.ornament],
  ];
  if (asked !== undefined) members.push([asked.width, asked.height]);
  const endpoint = document.active[scheme];
  const profile = glass === "clear" ? tunedPatch(endpoint.patch) : endpoint.patch;
  let widest: number = DEFAULT_GROUP_SAMPLING.samplingPadding;
  for (const policy of [material, NOMINAL_ACCESSIBILITY_POLICY.material]) {
    for (const member of members) {
      widest = Math.max(
        widest,
        samplingPaddingFor({ members: [member], material: policy, variant: glass, ...(profile === undefined ? {} : { profile }), cssTierMapping: document.cssTierMapping }),
      );
    }
  }
  return Math.ceil(widest);
}

/** The Clear tune merged over an endpoint's patch, as the root merges it. */
function tunedPatch(patch: RendererMaterialProfile | undefined): RendererMaterialProfile {
  const tune = clearTune();
  return { ...patch, ...tune, optics: { ...patch?.optics, clear: { ...patch?.optics?.clear, ...tune.optics?.clear } } };
}
