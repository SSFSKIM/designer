/**
 * Host registration — the `asChild` seam.
 *
 * The app hands vitrea an element it authored: a real `<button>`, `<div>` or
 * whatever the control is. vitrea never creates it, never wraps it, and never
 * replaces its content. That is what keeps `vitrea-react`'s `GlassSurface
 * asChild` thin — it clones a child and calls `registerHost` — and what keeps a
 * future Vue or Web-Components adapter from duplicating anything.
 *
 * ## Where the element has to live
 *
 * Inside its plane's host layer. X1's sandwich puts the optics canvas below the
 * host and the highlight canvas above it, and DOM order is what orders them, so
 * a host outside the plane cannot be sequenced at all — its body would paint in
 * the wrong place. Registration therefore *checks* containment and reports a
 * dev-mode error naming the fix, rather than adopting the element: moving a node
 * a framework rendered breaks that framework's own removal path (React records
 * the parent it inserted into). The plane's `hostLayer` is public precisely so a
 * binding can portal into it.
 *
 * ## What the app declares, and what is measured
 *
 * The app declares the *material* half of the shape — family, corner radii,
 * smoothing, thickness — and never its position or size. Those come from the
 * measured rect, once per frame, in the read phase. One source of truth, and it
 * is the reason vitrea's own transforms (press compression, morph deformation)
 * are composed on top analytically instead of being written back into the shape:
 * `ResizeObserver` does not fire for a transform, so no owned animation dirties
 * the geometry it is animating and the frames it runs for stay at zero reads.
 *
 * What that reasoning does *not* license is measuring while one is live.
 * `getBoundingClientRect` reports the transformed box, not the border box, so a
 * read taken mid-press describes the compressed surface. Vitrea therefore
 * measures around its own transforms: never during one, and once on the edge
 * where one is cleared.
 *
 * ## vitrea owns `transform` on a registered host
 *
 * The press, lensing and morph drivers all write that one property, so an inline
 * `transform` the app puts on a host is overwritten while the host is registered
 * and removed when it is released — not composed with. Registration reports it in
 * dev mode. Put the app's own transform on an ancestor or a descendant instead.
 */

import type { ConcentricParent, CornerRadii, CornerReference, ForegroundAdaptation, GlassPlane, InteractionState, MaterialVariant, ShapeFamily } from "@vitreajs/vitrea";

/**
 * An author tint, as an app writes it: **any CSS colour the browser can parse**,
 * with its alpha read as the tint's strength (`rgb(255 149 0 / 50%)` is a
 * half-strength orange, exactly as `Color.orange.opacity(0.5)` is in SwiftUI).
 *
 * `null` clears a tint inherited from the group, the way `Glass.tint(nil)` does.
 * `undefined` inherits.
 */
export type TintDeclaration = string | null;

export interface GlassHostOptions {
  /** The app's own element. Must already be inside `plane(plane).hostLayer`. */
  readonly host: HTMLElement;
  readonly groupId: string;
  /** Generated when absent. Stable for the handle's lifetime either way. */
  readonly nodeId?: string;
  /** Defaults to `"base"`. */
  readonly plane?: GlassPlane;
  /** Paint sequence within the plane. Defaults to registration order. */
  readonly order?: number;
  readonly shapeFamily?: ShapeFamily;
  readonly radii?: CornerRadii;
  /** 0 = circular corners, 1 = maximum continuous-curvature smoothing. */
  readonly smoothing?: number;
  /**
   * Which of geometry's two corner references this shape is fit against.
   * Defaults to `"apple-continuous"`.
   *
   * `smoothing` alone does not determine this: the two references are separate
   * fits to different curves rather than two points on one axis (Decision Log
   * #22(a)), so a shape authored on the Figma smoothing axis and resolved
   * against the Apple fit is a shape drawn against a curve nobody asked for.
   * Until Decision Log #23(c) there was no way to say which, and every surface
   * got the Apple fit.
   */
  readonly reference?: CornerReference;
  /**
   * Draw this surface as a level set of another surface's field, inset by a
   * fixed distance (X8 rider 2) — a segmented control's indicator inside its
   * track, as one field rather than two shapes that happen to nest.
   *
   * The parent must be registered, and in the same group. Both are refused at
   * registration rather than at draw time.
   */
  readonly concentricOf?: ConcentricParent;
  /** Material thickness in CSS px, driving lensing depth and shadow. */
  readonly thickness?: number;
  readonly variant?: MaterialVariant;
  /** Overrides the group's tint seed. See `TintDeclaration`. */
  readonly tint?: TintDeclaration;
  readonly interaction?: InteractionState;
  readonly foreground?: ForegroundAdaptation;
  /**
   * Take over placement across a cross-plane promotion.
   *
   * Absent, vitrea moves the element into the destination plane's host layer
   * itself — the right default for imperative use. Present, vitrea touches no
   * DOM and the consumer re-places the element; that is the path a React
   * binding needs, because it owns where its own portal renders.
   */
  readonly onPlaneChange?: (plane: GlassPlane) => void;
}

/** What the app declares about a surface's material shape. Position is measured. */
export interface HostShapeDeclaration {
  readonly shapeFamily: ShapeFamily;
  readonly radii: CornerRadii;
  readonly smoothing: number;
  readonly thickness: number;
}

export const DEFAULT_HOST_SHAPE: HostShapeDeclaration = {
  shapeFamily: "fixed-rounded-rect",
  radii: [12, 12, 12, 12],
  smoothing: 0,
  thickness: 8,
};

/** Patchable after registration. `undefined` clears an override, as core's patches do. */
export interface GlassHostPatch {
  readonly radii?: CornerRadii;
  readonly smoothing?: number;
  /** `undefined` clears the override, returning the surface to the default fit. */
  readonly reference?: CornerReference | undefined;
  /** `undefined` clears the link, returning the surface to a shape of its own. */
  readonly concentricOf?: ConcentricParent | undefined;
  readonly thickness?: number;
  readonly variant?: MaterialVariant | undefined;
  readonly tint?: TintDeclaration | undefined;
  readonly interaction?: InteractionState | undefined;
  readonly foreground?: ForegroundAdaptation | undefined;
  readonly order?: number;
}

export interface GlassHostHandle {
  readonly nodeId: string;
  readonly groupId: string;
  readonly host: HTMLElement;
  readonly plane: GlassPlane;
  /**
   * Patch the declared material shape. Never re-measures: no field here can move
   * the host's border box, and measuring anyway is how a press-time update wrote
   * a transform-compressed rect into the scene.
   */
  update(patch: GlassHostPatch): void;
  /**
   * Mark this host's geometry stale. The escape hatch for a layout change no
   * observer can see — a sibling reflow, a canvas-driven layout, an app that
   * knows something moved before the browser notices.
   */
  invalidateGeometry(): void;
  /** Cross-plane promotion, as a unit: body, semantic host and highlight together. */
  promoteTo(plane: GlassPlane): void;
  /**
   * Vitrea-owned visual transform, composed on top of the measured rect.
   *
   * Setting or changing one never dirties geometry, which is the point: an
   * animation that re-measured every frame would defeat the zero-read steady
   * state. *Clearing* one marks the host dirty exactly once, because
   * `getBoundingClientRect` reports the transformed box and any rect measured
   * while the transform was live describes the deformed surface rather than the
   * real one.
   */
  setOwnedTransform(transform: string | undefined): void;
  release(): void;
}

/** Attribute markers. Public, because tests and dev tooling both read them. */
export const HOST_ATTRIBUTES = {
  node: "data-vitrea-node",
  group: "data-vitrea-group",
  plane: "data-vitrea-host-plane",
} as const;

let sequence = 0;

/** Ids only have to be unique within a scene; core throws on a duplicate. */
export function nextNodeId(prefix = "vitrea-node"): string {
  sequence += 1;
  return `${prefix}-${sequence}`;
}
