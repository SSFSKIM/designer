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

import type { Rect } from "@vitrea/core";

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

export function readComputedStyle(meter: LayoutReadMeter, element: Element): CSSStyleDeclaration {
  bump(meter, "styles");
  return getComputedStyle(element);
}

export interface ViewportReading {
  readonly width: number;
  readonly height: number;
  readonly devicePixelRatio: number;
}

export function readViewport(meter: LayoutReadMeter): ViewportReading {
  bump(meter, "viewport");
  return {
    width: window.innerWidth,
    height: window.innerHeight,
    devicePixelRatio: window.devicePixelRatio,
  };
}
