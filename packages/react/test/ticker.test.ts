/**
 * The ticker. Small, but it is the clock every surface in a tree shares, so its
 * two edge cases are worth pinning: a listener that unsubscribes itself
 * mid-tick, and a restart after a pause.
 */

import { describe, expect, it, vi } from "vitest";

import { createGlassTicker } from "../src/ticker";

describe("createGlassTicker", () => {
  it("advances every listener by hand, with the delta it was given", () => {
    const ticker = createGlassTicker();
    const seen: number[] = [];
    ticker.subscribe((dtMs) => seen.push(dtMs));

    ticker.advance(16);
    ticker.advance(33);
    // Non-positive deltas are no-ops — a clock that jumped backwards must not
    // integrate anything.
    ticker.advance(0);
    ticker.advance(-5);

    expect(seen).toEqual([16, 33]);
  });

  it("does not skip a listener when an earlier one unsubscribes mid-tick", () => {
    const ticker = createGlassTicker();
    const second = vi.fn();
    const unsubscribe = ticker.subscribe(() => unsubscribe());
    ticker.subscribe(second);

    ticker.advance(16);
    expect(second).toHaveBeenCalledTimes(1);
  });

  it("reports no delta on the first frame after a restart", () => {
    let frame: ((timeMs: number) => void) | undefined;
    const view = {
      requestAnimationFrame: (callback: (timeMs: number) => void) => {
        frame = callback;
        return 1;
      },
      cancelAnimationFrame: () => undefined,
    } as unknown as Window;

    const ticker = createGlassTicker({ window: view });
    const seen: number[] = [];
    ticker.subscribe((dtMs) => seen.push(dtMs));

    ticker.start();
    frame?.(1000);
    frame?.(1016);
    ticker.stop();
    ticker.start();
    // The pause is not a delta: honouring it would resolve the whole animation
    // during the stall the pause represents.
    frame?.(9000);
    frame?.(9016);

    expect(seen).toEqual([16, 16]);
  });
});

/*
 * Frames on demand. The ticker is where a binding's springs meet the root's
 * loop, so it carries the listeners' half of the demand: a listener that returns
 * `false` is done, anything else — including nothing — still wants frames, and a
 * request goes to whatever drives the ticker.
 */
describe("demand", () => {
  it("reports whether any listener wants another frame", () => {
    const ticker = createGlassTicker();
    expect(ticker.advance(16)).toBe(false);

    let travelling = true;
    ticker.subscribe(() => travelling);
    ticker.subscribe(() => false);
    expect(ticker.advance(16)).toBe(true);
    travelling = false;
    expect(ticker.advance(16)).toBe(false);

    // A listener written before any of this returns nothing, and keeps its frames.
    ticker.subscribe(() => {});
    expect(ticker.advance(16)).toBe(true);
  });

  it("owes its listeners a frame on a step that called none of them", () => {
    const ticker = createGlassTicker();
    ticker.subscribe(() => false);
    expect(ticker.advance(0)).toBe(true);
  });

  it("forwards requests to whatever it is bound to", () => {
    const ticker = createGlassTicker();
    const request = vi.fn();
    const unbind = ticker.bind(request);
    ticker.requestFrame();
    ticker.subscribe(() => false);
    expect(request).toHaveBeenCalledTimes(2);
    unbind();
    ticker.requestFrame();
    expect(request).toHaveBeenCalledTimes(2);
  });

  it("runs its own loop only while a listener wants it, and wakes on request", () => {
    const frames: ((timeMs: number) => void)[] = [];
    const view = {
      requestAnimationFrame: (callback: (timeMs: number) => void) => {
        frames.push(callback);
        return frames.length;
      },
      cancelAnimationFrame: () => undefined,
    } as unknown as Window;
    const flush = (timeMs: number): void => {
      const pending = frames.splice(0);
      for (const callback of pending) callback(timeMs);
    };

    const ticker = createGlassTicker({ window: view });
    let remaining = 2;
    const seen: number[] = [];
    ticker.subscribe((dtMs) => {
      seen.push(dtMs);
      remaining -= 1;
      return remaining > 0;
    });
    ticker.start();
    flush(1000);
    flush(1016);
    flush(1032);
    expect(seen).toEqual([16, 16]);
    expect(frames).toHaveLength(0);

    remaining = 1;
    ticker.requestFrame();
    expect(frames).toHaveLength(1);
    // The wake reports no delta for the idle gap; the next frame carries one.
    flush(9000);
    flush(9016);
    expect(seen).toEqual([16, 16, 16]);
  });
});
