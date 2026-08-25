/**
 * The frame ticker the bindings drive their motion from.
 *
 * `platform-web`'s root runs its own `requestAnimationFrame` loop for the five
 * scene phases, and it exposes no way to join it — `createFrameScheduler` is
 * private to `createGlassRoot`. So the bindings run one loop of their own, and
 * one is all it takes: every surface, indicator and morph in a tree shares this
 * ticker, so the cost is a single rAF callback whatever the surface count.
 *
 * The delta arrives raw. `@vitrea/motion` applies the capped-step rule at the
 * frame boundary — `InteractionMachine.advance` clamps with the profile's own
 * `FramePolicy` and returns what it applied — so nothing here second-guesses it
 * (clamping twice would make the cap depend on how many loops a value passed
 * through).
 *
 * `advance` is the manual entry point. A test with no animation frames, and a
 * root configured `autoStart={false}`, steps time by hand through it.
 */

export type GlassTickListener = (dtMs: number, timeMs: number) => void;

export interface GlassTicker {
  subscribe(listener: GlassTickListener): () => void;
  /** Step every listener by hand. The path a test without rAF takes. */
  advance(dtMs: number): void;
  start(): void;
  stop(): void;
  readonly running: boolean;
  destroy(): void;
}

export interface GlassTickerOptions {
  readonly window?: Window;
}

export function createGlassTicker(options: GlassTickerOptions = {}): GlassTicker {
  const view = options.window ?? window;
  const listeners = new Set<GlassTickListener>();

  let handle: number | undefined;
  let previousMs: number | undefined;
  let clock = 0;

  const notify = (dtMs: number, timeMs: number): void => {
    // Copied before iterating: a listener that unsubscribes itself mid-tick —
    // a surface unmounting on a click — must not skip the listener after it.
    for (const listener of [...listeners]) listener(dtMs, timeMs);
  };

  const loop = (timeMs: number): void => {
    handle = view.requestAnimationFrame(loop);
    const dtMs = previousMs === undefined ? 0 : timeMs - previousMs;
    previousMs = timeMs;
    clock = timeMs;
    if (dtMs > 0) notify(dtMs, timeMs);
  };

  return {
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },

    advance(dtMs) {
      clock += dtMs;
      if (dtMs > 0) notify(dtMs, clock);
    },

    start() {
      if (handle !== undefined) return;
      // Cleared so the first frame after a restart reports no delta rather than
      // the whole pause: the drivers would resolve the stall in one step.
      previousMs = undefined;
      handle = view.requestAnimationFrame(loop);
    },

    stop() {
      if (handle === undefined) return;
      view.cancelAnimationFrame(handle);
      handle = undefined;
    },

    get running() {
      return handle !== undefined;
    },

    destroy() {
      this.stop();
      listeners.clear();
    },
  };
}
