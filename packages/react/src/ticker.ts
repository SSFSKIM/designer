/**
 * The frame ticker the bindings drive their motion from.
 *
 * This is a fan-out, not a clock. Every surface, indicator and morph in a tree
 * subscribes here, and `GlassRoot` advances it from the *root's* frame loop
 * (`GlassRoot.subscribe`) — so a mounted tree costs one wake-up per frame and
 * the springs step in a defined order, after the scene has resolved. Before that
 * seam existed this module ran a second `requestAnimationFrame` beside the
 * root's, which is what `start()` below still does for a consumer driving a bare
 * ticker with no root to borrow a loop from.
 *
 * The delta arrives raw. `@vitrea/motion` applies the capped-step rule at the
 * frame boundary — `InteractionMachine.advance` clamps with the profile's own
 * `FramePolicy` and returns what it applied — so nothing here second-guesses it
 * (clamping twice would make the cap depend on how many loops a value passed
 * through).
 *
 * `advance` is the manual entry point. A test with no animation frames, and a
 * root configured `autoStart={false}`, steps time by hand through it.
 *
 * ## Frames on demand
 *
 * The root draws a frame only when something asks for one (`GlassRoot.requestFrame`),
 * and a listener here is part of that demand. Returning `false` says it needs no
 * further frame; anything else — including returning nothing — keeps frames
 * coming on every frame, which is what every listener written before
 * demand-driven frames expects, so an animation that never heard of this keeps
 * animating. A listener whose work is done until something changes returns
 * `false` and calls `requestFrame()` when it has work again: a spring that was
 * retargeted, a canvas that went stale.
 */

/**
 * A per-frame callback. The return value is read for one thing: `false` means no
 * further frame is needed on this listener's account. Typed `unknown` so that an
 * expression-bodied listener — `(dt) => (elapsed += dt)` — still type-checks and
 * keeps the per-frame behaviour it was written for.
 */
export type GlassTickListener = (dtMs: number, timeMs: number) => unknown;

export interface GlassTicker {
  /** Subscribing asks for a frame, so a new listener is always called at least once. */
  subscribe(listener: GlassTickListener): () => void;
  /**
   * Step every listener by hand. The path a test without rAF takes, and the one
   * `GlassRoot` drives from the root's frames. Returns whether any listener wants
   * another frame (see the module note); a zero step calls no listener and
   * reports that they are still owed one.
   */
  advance(dtMs: number): boolean;
  /**
   * Ask for a frame: the root's, when a `GlassRoot` drives this ticker, and this
   * ticker's own `requestAnimationFrame` when it runs by itself.
   */
  requestFrame(): void;
  /**
   * Hand frame requests to whatever drives this ticker — `GlassRoot` passes its
   * root's `requestFrame`. Returns the unbind; unbound, requests arm this
   * ticker's own loop while it is started.
   */
  bind(requestFrame: () => void): () => void;
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
  let started = false;
  let driver: (() => void) | undefined;

  const notify = (dtMs: number, timeMs: number): boolean => {
    let wantsMore = false;
    // Copied before iterating: a listener that unsubscribes itself mid-tick —
    // a surface unmounting on a click — must not skip the listener after it.
    for (const listener of [...listeners]) {
      try {
        if (listener(dtMs, timeMs) !== false) wantsMore = true;
      } catch (error) {
        // One subscriber must not take the bus down with it. Every surface,
        // indicator and morph in a tree shares this loop, so a throw here would
        // silently freeze every listener registered after the failing one —
        // which reads as "the morph does not animate", not as "there is a bug".
        // Rethrowing on a microtask keeps the error intact for devtools and for
        // whatever reports uncaught errors, and keeps the frame going.
        queueMicrotask(() => {
          throw error;
        });
      }
    }
    return wantsMore;
  };

  /** A zero step calls nobody, so whoever is subscribed is still owed a frame. */
  const step = (dtMs: number, timeMs: number): boolean =>
    dtMs > 0 ? notify(dtMs, timeMs) : listeners.size > 0;

  const loop = (timeMs: number): void => {
    handle = undefined;
    const dtMs = previousMs === undefined ? 0 : timeMs - previousMs;
    previousMs = timeMs;
    clock = timeMs;
    if (step(dtMs, timeMs) && started && handle === undefined) {
      handle = view.requestAnimationFrame(loop);
    } else if (handle === undefined) {
      // Idle: the next frame is a wake, and reports no delta rather than the
      // whole pause, for the same reason a restart does.
      previousMs = undefined;
    }
  };

  const requestFrame = (): void => {
    if (driver !== undefined) {
      driver();
      return;
    }
    if (!started || handle !== undefined) return;
    handle = view.requestAnimationFrame(loop);
  };

  return {
    subscribe(listener) {
      listeners.add(listener);
      requestFrame();
      return () => listeners.delete(listener);
    },

    advance(dtMs) {
      clock += dtMs;
      return step(dtMs, clock);
    },

    requestFrame,

    bind(next) {
      driver = next;
      return () => {
        if (driver === next) driver = undefined;
      };
    },

    start() {
      if (started) return;
      started = true;
      // Cleared so the first frame after a restart reports no delta rather than
      // the whole pause: the drivers would resolve the stall in one step.
      previousMs = undefined;
      if (handle === undefined) handle = view.requestAnimationFrame(loop);
    },

    stop() {
      started = false;
      if (handle === undefined) return;
      view.cancelAnimationFrame(handle);
      handle = undefined;
    },

    get running() {
      return started;
    },

    destroy() {
      this.stop();
      driver = undefined;
      listeners.clear();
    },
  };
}
