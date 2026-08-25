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
