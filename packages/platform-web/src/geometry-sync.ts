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
 *
 * ## The clip chain (Decision Log #41(k))
 *
 * A border box says where a surface *is*, not what of it is *visible*. Under an
 * `overflow: scroll` ancestor the two are different things: the browser reports
 * the full box wherever it has scrolled to, including entirely outside the
 * scroller. Everything downstream believed the box — so a surface scrolled out
 * of view still claimed its area, still reported same-plane overlaps against
 * surfaces it could never touch, and still had a proxy painting glass outside
 * the scroller that was supposed to crop it.
 *
 * So each measured host is published with the clip windows its clipping
 * ancestors impose, and core's `clipRect` folds them. Two costs, both deliberate:
 *
 * - **The chain is cached per host, its rects are not.** Which ancestors clip is
 *   structural and changes rarely; where they are changes on every scroll. So
 *   the computed-style walk runs once per host and the rect reads run per
 *   measurement — the alternative was a style read per ancestor per scroll
 *   event, on exactly the page this feature is for.
 * - **A stale chain is possible**, and `invalidateClipChains` is the answer: the
 *   root calls it from the same mutation observer that re-runs the backdrop-root
 *   probe, because "an ancestor's `overflow` changed" and "an ancestor's
 *   `filter` changed" are the same class of event and neither has an observer of
 *   its own.
 *
 * The steady state is untouched: nothing dirty still measures nothing.
 */

import type { GlassScene, Rect } from "@vitreajs/vitrea";

import { clipsContentOf } from "./probe/engine-defects";
import {
  readComputedStyle,
  readRect,
  readViewport,
  type LayoutReadMeter,
  type ViewportReading,
} from "./measure";

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
  /**
   * Forget which ancestors clip, so the next measurement re-walks for it.
   *
   * Which ancestors clip is structural: it changes when the app changes an
   * `overflow`, or moves a host into a different subtree. Neither has an
   * observer, and both are visible in the attribute mutations the root already
   * watches for the backdrop-root probe — so the root calls this from there.
   */
  invalidateClipChains(): void;
  /**
   * Measure a texture backdrop source's element alongside the hosts, so the GPU
   * tier can place the texture where its pixels are (claims §5.47). Dirtied by
   * the same events as a host — its own resize, any scroll that reaches it, a
   * viewport resize — and read in the same batch. A source whose element
   * measures to nothing (detached, `display: none`) has no placement.
   */
  trackSource(sourceId: string, element: Element): void;
  untrackSource(sourceId: string): void;
  hasSource(sourceId: string): boolean;
  /** The source element's last measured box, in viewport-relative CSS px. */
  placementOf(sourceId: string): Rect | undefined;
  /** The read phase. Measures every dirty host and source exactly once, then clears the sets. */
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
  /**
   * The clipping ancestors of each tracked host, nearest first — the elements,
   * not their rects. Absent until the host's first measurement.
   */
  const clipChains = new Map<string, readonly Element[]>();
  let viewport: ViewportReading | undefined;
  /** Set on the first read and whenever the viewport changes, so the DPR is fresh. */
  let viewportDirty = true;
  /** Texture sources with an element to measure, and where each last measured. */
  const sources = new Map<string, Element>();
  const dirtySources = new Set<string>();
  const placements = new Map<string, Rect>();

  const markDirty = (nodeId: string): void => {
    if (tracked.has(nodeId)) dirty.add(nodeId);
  };

  const markAllDirty = (): void => {
    for (const nodeId of tracked.keys()) dirty.add(nodeId);
    for (const sourceId of sources.keys()) dirtySources.add(sourceId);
    viewportDirty = true;
  };

  const sourcesByElement = (element: Element): void => {
    for (const [sourceId, candidate] of sources) {
      if (candidate === element) dirtySources.add(sourceId);
    }
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
      sourcesByElement(entry.target);
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
    for (const [sourceId, element] of sources) {
      if (target.contains(element)) dirtySources.add(sourceId);
    }
  };

  /**
   * The clipping ancestors between a host and the document, nearest first.
   *
   * The predicate is `clipsContentOf`, borrowed from layer 3's engine-defect scan
   * rather than written again: "any `overflow` token other than `visible` clips"
   * is the same question there and here, it is already unit-tested across the
   * `hidden` / `clip` / `auto` / `scroll` matrix and the three longhands, and two
   * definitions of "clips" would eventually disagree. Layer 3 needs the *rounded*
   * half on top of it, which is why `roundedClipOf` is now expressed over this
   * one rather than the other way round.
   *
   * The walk runs to the document element rather than stopping at the plane
   * layer. A host's clipping ancestors are the app's own elements, and the plane
   * layer is not one of them — vitrea appends into it, so a host's real
   * containment chain is the one the app built underneath. Stopping early would
   * miss a scroller the app wrapped the whole page in.
   */
  const clipChainOf = (element: Element): readonly Element[] => {
    const chain: Element[] = [];
    for (
      let ancestor = element.parentElement;
      ancestor !== null && ancestor !== view.document.documentElement;
      ancestor = ancestor.parentElement
    ) {
      // One computed style per ancestor, read through the meter like everything
      // else here, then queried several times off the same declaration.
      const style = readComputedStyle(meter, ancestor, view);
      if (clipsContentOf((property) => style.getPropertyValue(property)) !== undefined) {
        chain.push(ancestor);
      }
    }
    return chain;
  };

  const clipOf = (host: TrackedHost): readonly Rect[] | undefined => {
    let chain = clipChains.get(host.nodeId);
    if (chain === undefined) {
      chain = clipChainOf(host.element);
      clipChains.set(host.nodeId, chain);
    }
    if (chain.length === 0) return undefined;
    // Rects every time: which ancestors clip is structural, where they are is
    // not, and a scroll moves them without changing the set.
    return chain.map((ancestor) => readRect(meter, ancestor));
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
      // A re-registration under the same id may sit somewhere else entirely.
      clipChains.delete(host.nodeId);
      resizeObserver.observe(host.element);
    },

    untrack(nodeId) {
      const host = tracked.get(nodeId);
      if (host !== undefined) resizeObserver.unobserve(host.element);
      tracked.delete(nodeId);
      dirty.delete(nodeId);
      clipChains.delete(nodeId);
    },

    markDirty,
    markAllDirty,

    invalidateClipChains() {
      clipChains.clear();
    },

    read() {
      if (viewportDirty) {
        viewport = readViewport(meter, view);
        viewportDirty = false;
      }

      // Sources first: cheap, and a host measured in the same batch may be
      // sampling one of them this very frame.
      for (const sourceId of dirtySources) {
        const element = sources.get(sourceId);
        if (element === undefined) continue;
        const rect: Rect = readRect(meter, element);
        if (rect.width > 0 && rect.height > 0) placements.set(sourceId, rect);
        else placements.delete(sourceId);
      }
      dirtySources.clear();

      if (dirty.size === 0) return;

      const measured: string[] = [];
      for (const nodeId of dirty) {
        const host = tracked.get(nodeId);
        if (host === undefined) continue;
        const rect: Rect = readRect(meter, host.element);
        const clip = clipOf(host);
        scene.setNodeBounds(nodeId, rect, clip);
        measured.push(nodeId);
      }
      dirty.clear();

      if (measured.length > 0 && viewport !== undefined) onMeasured?.(measured, viewport);
    },

    trackSource(sourceId, element) {
      const previous = sources.get(sourceId);
      if (previous !== undefined && previous !== element) resizeObserver.unobserve(previous);
      sources.set(sourceId, element);
      placements.delete(sourceId);
      dirtySources.add(sourceId);
      resizeObserver.observe(element);
    },

    untrackSource(sourceId) {
      const element = sources.get(sourceId);
      // A host may share the element; only stop observing what nothing else watches.
      if (element !== undefined && byElement(element) === undefined) {
        resizeObserver.unobserve(element);
      }
      sources.delete(sourceId);
      dirtySources.delete(sourceId);
      placements.delete(sourceId);
    },

    hasSource(sourceId) {
      return sources.has(sourceId);
    },

    placementOf(sourceId) {
      return placements.get(sourceId);
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
      clipChains.clear();
      sources.clear();
      dirtySources.clear();
      placements.clear();
    },
  };
}
