/**
 * Every layout and style read in this package, and a meter that counts them.
 *
 * §Geometry asks for "zero layout reads at steady state (instrument and assert
 * it)". An instrument only counts what routes through it, so this module is the
 * single door: the package's own ESLint config forbids `getBoundingClientRect`,
 * `getClientRects` and `getComputedStyle` everywhere else in `src/`. Without
 * that rule the meter would be a comment, and the test asserting zero would be
 * asserting nothing.
 *
 * Style reads are counted alongside rects on purpose. A computed-style read is
 * not a layout read in the reflow sense, but the probe's backdrop-root audit
 * performs plenty of them, and "the steady state touches nothing" is the claim
 * worth defending — not "the steady state touches nothing except styles".
 */

import type { Rect } from "@vitreajs/vitrea";

export interface LayoutReadCounters {
  readonly rects: number;
  readonly styles: number;
  readonly viewport: number;
}

export interface LayoutReadMeter {
  readonly counts: LayoutReadCounters;
  readonly total: number;
  reset(): void;
}

/** Internal write side. Kept off `LayoutReadMeter` so a consumer cannot forge counts. */
interface MutableMeter extends LayoutReadMeter {
  bump(kind: keyof LayoutReadCounters): void;
}

export function createLayoutReadMeter(): LayoutReadMeter {
  let rects = 0;
  let styles = 0;
  let viewport = 0;

  const meter: MutableMeter = {
    get counts() {
      return { rects, styles, viewport };
    },
    get total() {
      return rects + styles + viewport;
    },
    reset() {
      rects = 0;
      styles = 0;
      viewport = 0;
    },
    bump(kind) {
      if (kind === "rects") rects += 1;
      else if (kind === "styles") styles += 1;
      else viewport += 1;
    },
  };

  return meter;
}

const bump = (meter: LayoutReadMeter, kind: keyof LayoutReadCounters): void => {
  (meter as MutableMeter).bump(kind);
};

/**
 * A viewport rect as core's plain `Rect`. Copied rather than passed through:
 * a `DOMRect` is live in some engines, and core's contract is data.
 */
export function readRect(meter: LayoutReadMeter, element: Element): Rect {
  bump(meter, "rects");
  const rect = element.getBoundingClientRect();
  return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
}

/**
 * `view` is threaded rather than read off the module scope, like every other
 * browser handle in this package. A root can be driven against a document in
 * another window — an iframe, a popped-out panel, a test's own jsdom instance —
 * and a style or viewport read that reached for the ambient global there would
 * silently describe a different window than the one being measured.
 */
export function readComputedStyle(
  meter: LayoutReadMeter,
  element: Element,
  view: Window,
): CSSStyleDeclaration {
  bump(meter, "styles");
  return view.getComputedStyle(element);
}

/**
 * Force the browser to resolve pending style writes, and count it as the read it
 * is.
 *
 * Used once per host, at materialization. Style writes are batched, so writing a
 * surface's final values and then arming its CSS transition in the same tick
 * makes the browser see one aggregate change *with* the transition — and every
 * glass surface fades in from the initial transparent, unblurred values it
 * happened to start with. Flushing between the two writes is what makes the
 * transition apply to state changes rather than to existing at all.
 */
export function flushStyle(meter: LayoutReadMeter, element: Element, view: Window): void {
  bump(meter, "styles");
  // Reading any resolved value forces the recalc; `opacity` is cheap and has no
  // layout dependency.
  void view.getComputedStyle(element).opacity;
}

export interface ViewportReading {
  readonly width: number;
  readonly height: number;
  readonly devicePixelRatio: number;
}

export function readViewport(meter: LayoutReadMeter, view: Window): ViewportReading {
  bump(meter, "viewport");
  return {
    width: view.innerWidth,
    height: view.innerHeight,
    devicePixelRatio: view.devicePixelRatio,
  };
}
