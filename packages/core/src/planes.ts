/**
 * The z-slot model (§Core model: `z-slot (plane + order)`) and the geometry
 * primitives core needs to reason about it.
 *
 * Plane identity lives here rather than in platform-web because it is part of
 * the scene model: a GlassNode's slot is (plane, order), and the same-plane
 * overlap check is a core invariant. platform-web owns the *DOM realisation* of
 * a plane — the canvas pair and the paint order inside it (X1) — and re-exports
 * these names so there is one vocabulary.
 *
 * `Rect` is plain data. The numbers arrive from platform-web's batched layout
 * read; core never measures anything (X4).
 */

/** v1 ships exactly two managed stacking planes (X1). More overlays are out of scope. */
export const GLASS_PLANES = ["base", "overlay"] as const;

export type GlassPlane = (typeof GLASS_PLANES)[number];

/**
 * Where a node sits. `plane` picks the canvas pair; `order` sequences nodes
 * within it. Nodes in one plane must not overlap (X1) — order breaks ties for
 * paint sequence, it does not license stacking.
 */
export interface ZSlot {
  readonly plane: GlassPlane;
  readonly order: number;
}

/** Viewport-space rectangle in CSS px, measured by platform-web and handed in as data. */
export interface Rect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

const planeIndex = (plane: GlassPlane): number => GLASS_PLANES.indexOf(plane);

/** Back-to-front ordering: every base node before every overlay node, then by `order`. */
export function compareZSlot(a: ZSlot, b: ZSlot): number {
  const byPlane = planeIndex(a.plane) - planeIndex(b.plane);
  return byPlane !== 0 ? byPlane : a.order - b.order;
}

/** Smallest rect containing both. */
export function unionRect(a: Rect, b: Rect): Rect {
  const x = Math.min(a.x, b.x);
  const y = Math.min(a.y, b.y);
  return {
    x,
    y,
    width: Math.max(a.x + a.width, b.x + b.width) - x,
    height: Math.max(a.y + a.height, b.y + b.height) - y,
  };
}

/** Grow a rect outwards on every side — how a group's proxy gets its padding. */
export function inflateRect(rect: Rect, by: number): Rect {
  return {
    x: rect.x - by,
    y: rect.y - by,
    width: rect.width + by * 2,
    height: rect.height + by * 2,
  };
}

/**
 * Positive-area intersection. Touching edges are not an overlap — adjacent
 * surfaces in a toolbar are the common case and are legal. A degenerate rect
 * (an unmeasured or collapsed host) overlaps nothing.
 */
export function rectsOverlap(a: Rect, b: Rect): boolean {
  if (a.width <= 0 || a.height <= 0 || b.width <= 0 || b.height <= 0) return false;
  return (
    a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height
  );
}
