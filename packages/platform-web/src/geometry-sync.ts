/**
 * GeometrySync — batched dirty reads, and zero of them at steady state.
 *
 * §Geometry's requirement is not "few reads"; it is **none** once nothing has
 * changed, instrumented so the claim is checkable. The shape that gets there is
 * a dirty set plus one read phase:
 *
 * - Something changes → the source marks the affected hosts dirty. Marking is
 *   pure bookkeeping: a `Set.add` and, for scroll, a `contains` call. No read.
 * - The frame's `read` phase measures **only** the dirty hosts, once each, and
 *   hands the rects to core as data. Nothing dirty means nothing measured.
 * - Everything downstream — proxies, canvases, the CSS tier — consumes those
 *   rects. Nobody else measures.
 *
 * The dirty sources are the ones the spec names, and each is here because
 * nothing else can see what it sees:
 *
 * | source | sees |
 * | --- | --- |
 * | `ResizeObserver` | a host's own border box changing, for any reason |
 * | ancestor scroll | a host moving without resizing |
 * | viewport resize | every host's viewport-space position changing at once |
 * | font / layout completion | text metrics arriving late and reflowing hosts |
 * | `invalidateGeometry()` | whatever no observer can see |
 *
 * **Vitrea-owned transforms never re-read the DOM while they run.** A
 * `transform` does not change a border-box rect, so `ResizeObserver` does not
 * fire for one and this module never marks anything dirty because of one. Press
 * compression, lensing deformation and morph interpolation therefore run at zero
 * reads per frame, no matter how many frames they run for.
 *
 * Their *end* is a read, and has to be. `getBoundingClientRect` reports the
 * transformed box, so whatever was measured while one was live describes the
 * deformed surface; `root`'s `setOwnedTransform` marks the host dirty on the
 * edge where the transform is cleared, which costs one read per gesture and
 * leaves the steady state untouched.
 */

import type { GlassScene, Rect } from "@vitreajs/vitrea";

import { readRect, readViewport, type LayoutReadMeter, type ViewportReading } from "./measure";

export interface TrackedHost {
  readonly nodeId: string;
  readonly element: HTMLElement;
}

export interface GeometrySyncOptions {
  readonly scene: GlassScene;
  readonly meter: LayoutReadMeter;
  /** Called after a read phase that measured at least one host. */
  readonly onMeasured?: (nodeIds: readonly string[], viewport: ViewportReading) => void;
  readonly window?: Window;
}

export interface GeometrySync {
  track(host: TrackedHost): void;
  untrack(nodeId: string): void;
  markDirty(nodeId: string): void;
  markAllDirty(): void;
  /** The read phase. Measures every dirty host exactly once, then clears the set. */
  read(): void;
  /** Last measured viewport, or `undefined` before the first read. */
  readonly viewport: ViewportReading | undefined;
  readonly dirtyCount: number;
  destroy(): void;
}

export function createGeometrySync(options: GeometrySyncOptions): GeometrySync {
  const { scene, meter, onMeasured } = options;
  const view = options.window ?? window;

  const tracked = new Map<string, TrackedHost>();
  const dirty = new Set<string>();
  let viewport: ViewportReading | undefined;
  /** Set on the first read and whenever the viewport changes, so the DPR is fresh. */
  let viewportDirty = true;

  const markDirty = (nodeId: string): void => {
    if (tracked.has(nodeId)) dirty.add(nodeId);
  };

  const markAllDirty = (): void => {
    for (const nodeId of tracked.keys()) dirty.add(nodeId);
    viewportDirty = true;
  };

  const byElement = (element: Element): string | undefined => {
    for (const [nodeId, host] of tracked) if (host.element === element) return nodeId;
    return undefined;
  };

  /**
   * One observer for every host. `ResizeObserver` reports border-box changes and
   * nothing else, which is exactly the boundary this module wants: an app
   * resizing a toolbar dirties it, a vitrea-owned transform does not.
   */
  const resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const nodeId = byElement(entry.target);
      if (nodeId !== undefined) dirty.add(nodeId);
    }
  });

  /**
   * Scroll does not bubble, but it does capture — so one capturing listener at
   * the window sees every scroller in the document. Only the hosts inside the
   * scrolled subtree moved, and `contains` answers that without a read.
   */
  const onScroll = (event: Event): void => {
    const target = event.target;
    if (target === view.document || target === view.document.documentElement || target === view) {
      markAllDirty();
      return;
    }
    if (!(target instanceof Element)) return;
    for (const [nodeId, host] of tracked) {
      if (target.contains(host.element)) dirty.add(nodeId);
    }
  };

  const onViewportResize = (): void => markAllDirty();

  // Text metrics arriving late reflow hosts after the frame that registered
  // them, and no other source sees it.
  const onFontsDone = (): void => markAllDirty();

  view.addEventListener("scroll", onScroll, { capture: true, passive: true });
  view.addEventListener("resize", onViewportResize, { passive: true });
  const fonts = view.document.fonts;
  fonts?.addEventListener("loadingdone", onFontsDone);
  void fonts?.ready.then(onFontsDone);

  return {
    track(host) {
      tracked.set(host.nodeId, host);
      dirty.add(host.nodeId);
      resizeObserver.observe(host.element);
    },

    untrack(nodeId) {
      const host = tracked.get(nodeId);
      if (host !== undefined) resizeObserver.unobserve(host.element);
      tracked.delete(nodeId);
      dirty.delete(nodeId);
    },

    markDirty,
    markAllDirty,

    read() {
      if (viewportDirty) {
        viewport = readViewport(meter, view);
        viewportDirty = false;
      }
      if (dirty.size === 0) return;

      const measured: string[] = [];
      for (const nodeId of dirty) {
        const host = tracked.get(nodeId);
        if (host === undefined) continue;
        const rect: Rect = readRect(meter, host.element);
        scene.setNodeBounds(nodeId, rect);
        measured.push(nodeId);
      }
      dirty.clear();

      if (measured.length > 0 && viewport !== undefined) onMeasured?.(measured, viewport);
    },

    get viewport() {
      return viewport;
    },

    get dirtyCount() {
      return dirty.size;
    },

    destroy() {
      resizeObserver.disconnect();
      view.removeEventListener("scroll", onScroll, { capture: true });
      view.removeEventListener("resize", onViewportResize);
      fonts?.removeEventListener("loadingdone", onFontsDone);
      tracked.clear();
      dirty.clear();
    },
  };
}
