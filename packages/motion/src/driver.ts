import type { EasingName } from "./easing";

/**
 * One animated scalar over time.
 *
 * Two rules hold across every family:
 *
 * - `advance` is closed-form in `dtMs`. Advancing 33.4 ms in one call equals
 *   advancing it in two or four — the frame-rate invariance requirement in
 *   §Motion, and the reason nothing here integrates numerically.
 * - `retarget` never touches `value` or `velocity`. A redirect mid-flight
 *   continues from where the channel actually is, which is what makes an
 *   interrupted press continuous (parent acceptance #3).
 *
 * A driver holds no clock: `platform-web` owns scheduling (X4). Time enters
 * only as the `dtMs` a caller passes, and callers pass it through
 * `clampFrameDelta` so a stalled tab cannot hand a driver an arbitrary gap.
 */
export interface MotionDriver {
  /** Current value, in whatever unit the channel is expressed in. */
  readonly value: number;
  /** Current rate of change, in units per **second**, while `dtMs` is milliseconds. */
  readonly velocity: number;
  /** Where the driver is heading. For filtering families this is the committed input. */
  readonly target: number;
  /** True when further advancing would not visibly change the value. */
  readonly settled: boolean;
  /** Integrate forward. Non-positive and non-finite deltas are no-ops. */
  advance(dtMs: number): void;
  /**
   * Redirect. Position and velocity are preserved exactly; for the filtering
   * families the argument is the observed input rather than a destination.
   */
  retarget(input: number): void;
  /**
   * Discontinuously place the channel — initialisation, teardown, or a
   * reduced-motion re-seed. This is the only operation that breaks continuity,
   * and it is never called from a transition.
   */
  jumpTo(value: number, velocity?: number): void;
}

export interface SpringConfig {
  /** Period of the undamped oscillation. Smaller is snappier. */
  readonly responseMs: number;
  /** ζ. Below 1 overshoots, 1 is critical, above 1 crawls in. */
  readonly dampingRatio: number;
  /** Distance below which the channel counts as arrived. Channel units. */
  readonly restDistance: number;
  /** Speed below which the channel counts as stopped. Channel units per second. */
  readonly restVelocity: number;
}

export interface ExponentialConfig {
  /** Time constant while closing on a higher target — the fast half of a glow. */
  readonly attackMs: number;
  /** Time constant while falling away — the slow half. */
  readonly decayMs: number;
  readonly restDistance: number;
}

export interface LowPassConfig {
  /** Time constant of the output filter. */
  readonly timeConstantMs: number;
  /** Input band around the committed value. Changes inside it are rejected outright. */
  readonly hysteresis: number;
  readonly restDistance: number;
}

export interface ThresholdCrossfadeConfig {
  /** Input value at the centre of the switch. */
  readonly threshold: number;
  /** Total dead-band width; the switch sits at `threshold ± hysteresis / 2`. */
  readonly hysteresis: number;
  /** Time for a full 0 → 1 fade. */
  readonly crossfadeMs: number;
}

export interface EaseConfig {
  readonly durationMs: number;
  readonly easing: EasingName;
}

export interface StepConfig {
  /** Input band around the current value; 0 makes the driver a plain step. */
  readonly hysteresis: number;
  /** Minimum dwell before another change is accepted; 0 makes the driver a plain step. */
  readonly cooldownMs: number;
}

/** A driver family plus its constants — the unit a profile stores per channel. */
export type DriverConfig =
  | ({ readonly kind: "interruptible-spring" | "critically-damped" } & SpringConfig)
  | ({ readonly kind: "attack-decay" } & ExponentialConfig)
  | ({ readonly kind: "low-pass-hysteresis" } & LowPassConfig)
  | ({ readonly kind: "threshold-crossfade" } & ThresholdCrossfadeConfig)
  | ({ readonly kind: "monotonic-ease" } & EaseConfig)
  | ({ readonly kind: "step" | "hysteresis-cooldown" } & StepConfig);
