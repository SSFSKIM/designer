/**
 * The viewport's strips (DESIGN.md §4), as numbers the probe's clamp and the
 * sheet's placement both read. The CSS carries the same values as custom
 * properties; these are the ones that have to be arithmetic.
 */

export const NAV_STRIP = 72;
export const TRANSPORT_STRIP = 88;
export const INSET = 24;
export const COLUMN_WIDTH = 480;
export const NARROW_BREAKPOINT = 720;

export interface Rect {
  readonly left: number;
  readonly top: number;
  readonly right: number;
  readonly bottom: number;
}

export function isNarrow(width: number): boolean {
  return width < NARROW_BREAKPOINT;
}

export function probeDiameter(width: number): number {
  return isNarrow(width) ? 132 : 220;
}

/**
 * Where the probe may travel. On a wide viewport the reading column on the left
 * is content (the hero block or a sheet) and glass never sits over content on the
 * texture tier, so the field starts to its right. On a narrow viewport the column
 * is the full width and the field is the band under the hero block.
 */
/**
 * Clear space the probe keeps from the other sampling groups. vitrea warns when
 * two groups on one plane come within a group's sampling padding of each other:
 * measured at about 36px at the nominal blur, so the field's edges sit 48px from
 * the nav above and the transport and layer controls below, the same clearance
 * the library's own demo holds.
 */
export const GROUP_GAP = 48;

export function fieldRect(width: number, height: number): Rect {
  if (isNarrow(width)) {
    return {
      left: INSET,
      top: NAV_STRIP + 232,
      right: width - INSET,
      // The transport row, the layer row above it (44px, 52px clear), and the gap.
      bottom: height - INSET - 44 - 52 - 44 - GROUP_GAP,
    };
  }
  return {
    left: INSET + COLUMN_WIDTH + INSET,
    top: NAV_STRIP + GROUP_GAP,
    right: width - INSET,
    // The transport sits 24px up from the bottom edge and is 44px tall.
    bottom: height - INSET - 44 - GROUP_GAP,
  };
}

/** Clamp a probe centre so the whole disc stays inside the field. */
export function clampProbe(
  x: number,
  y: number,
  diameter: number,
  field: Rect,
): { readonly x: number; readonly y: number } {
  const half = diameter / 2;
  const minX = field.left + half;
  const maxX = Math.max(minX, field.right - half);
  const minY = field.top + half;
  const maxY = Math.max(minY, field.bottom - half);
  return {
    x: Math.min(maxX, Math.max(minX, x)),
    y: Math.min(maxY, Math.max(minY, y)),
  };
}
