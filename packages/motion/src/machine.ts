import { STATE_DRIVEN_CHANNELS, type MotionChannel } from "./channels";
import type { MotionDriver } from "./driver";
import { createDriver } from "./drivers/create";
import { clampFrameDelta } from "./frame";
import {
  canTransition,
  resolveInteractionState,
  type InteractionFlags,
  type InteractionState,
  type StateTargets,
} from "./states";
import { DEFAULT_MOTION_PROFILE, type MotionProfile } from "./tunables";

export interface InteractionMachineOptions {
  readonly profile?: MotionProfile;
  /** Where to start, placed rather than animated into. Defaults to `idle`. */
  readonly initialState?: InteractionState;
  /**
   * Which channels this machine carries. Defaults to the state-driven set; add
   * geometry channels when the machine should also carry a morph's targets.
   */
  readonly channels?: readonly MotionChannel[];
}

/**
 * One surface's motion state: the current interaction state and a driver per
 * channel it carries.
 *
 * A transition **only retargets**. Nothing here places a driver, so every state
 * change redirects the trajectory a channel is already on — which is what makes
 * an interrupted press continuous rather than a sequence of restarts (parent
 * acceptance #3). The one exception is construction, where a surface has no
 * history to be continuous with.
 */
export interface InteractionMachine {
  readonly profile: MotionProfile;
  readonly state: InteractionState;
  readonly channels: readonly MotionChannel[];
  /** True when every channel this machine carries has arrived. */
  readonly settled: boolean;
  /** The driver for a carried channel. Throws for one this machine does not carry. */
  driver(channel: MotionChannel): MotionDriver;
  value(channel: MotionChannel): number;
  canTransition(to: InteractionState): boolean;
  /**
   * Move to `to`, retargeting each carried channel to that state's vector.
   * Returns false, changing nothing, if the graph refuses the transition.
   *
   * `overrides` supplies targets the state table cannot know — a morph's
   * destination geometry, most of all. They win over the table, and they
   * retarget like everything else.
   */
  transition(to: InteractionState, overrides?: StateTargets): boolean;
  /** Collapse overlapping host flags and transition to the result. */
  applyFlags(flags: InteractionFlags): boolean;
  /** Advance every carried channel. Returns the delta actually applied. */
  advance(dtMs: number): number;
}

class Machine implements InteractionMachine {
  readonly profile: MotionProfile;
  readonly channels: readonly MotionChannel[];

  readonly #drivers: Map<MotionChannel, MotionDriver>;
  #state: InteractionState;

  constructor(options: InteractionMachineOptions) {
    this.profile = options.profile ?? DEFAULT_MOTION_PROFILE;
    this.channels = options.channels ?? STATE_DRIVEN_CHANNELS;
    this.#state = options.initialState ?? "idle";

    const seed = this.profile.stateTargets[this.#state];
    this.#drivers = new Map(
      this.channels.map((channel) => [
        channel,
        createDriver(this.profile.channels[channel], seed[channel] ?? 0),
      ]),
    );
  }

  get state(): InteractionState {
    return this.#state;
  }

  get settled(): boolean {
    for (const driver of this.#drivers.values()) {
      if (!driver.settled) return false;
    }
    return true;
  }

  driver(channel: MotionChannel): MotionDriver {
    const driver = this.#drivers.get(channel);
    if (driver === undefined) {
      throw new Error(
        `@vitrea/motion: this machine does not carry the "${channel}" channel — list it in options.channels.`,
      );
    }
    return driver;
  }

  value(channel: MotionChannel): number {
    return this.driver(channel).value;
  }

  canTransition(to: InteractionState): boolean {
    return canTransition(this.#state, to);
  }

  transition(to: InteractionState, overrides?: StateTargets): boolean {
    if (!canTransition(this.#state, to)) return false;

    this.#state = to;
    const targets = this.profile.stateTargets[to];
    for (const [channel, driver] of this.#drivers) {
      const target = overrides?.[channel] ?? targets[channel];
      // A channel neither the state nor the caller names keeps the target it
      // had: geometry follows layout, not interaction state.
      if (target !== undefined) driver.retarget(target);
    }
    return true;
  }

  applyFlags(flags: InteractionFlags): boolean {
    const next = resolveInteractionState(flags);
    if (canTransition(this.#state, next)) return this.transition(next);

    // `disabled` and `morphing` are only left through rest, and the host's flags
    // do not know that. Routing through `idle` costs one extra retarget with
    // nothing advanced in between, so it never shows in a value.
    if (!canTransition(this.#state, "idle") || !canTransition("idle", next)) return false;
    this.transition("idle");
    return this.transition(next);
  }

  advance(dtMs: number): number {
    const delta = clampFrameDelta(dtMs, this.profile.frame);
    if (delta > 0) {
      for (const driver of this.#drivers.values()) driver.advance(delta);
    }
    return delta;
  }
}

export function createInteractionMachine(
  options: InteractionMachineOptions = {},
): InteractionMachine {
  return new Machine(options);
}
