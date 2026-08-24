import type { MotionDriver, ThresholdCrossfadeConfig } from "../driver";

export type CrossfadePhase = "low" | "high";

/**
 * Threshold + hysteresis + timed crossfade (§Motion: foreground light/dark,
 * §Foreground adaptation).
 *
 * The observed input picks a side through a dead band; the output crosses
 * between the two sides on a timer. `value` is the weight of the high side in
 * [0, 1] — the mix a consumer blends light and dark foreground tokens with.
 *
 * The mix is linear in time rather than eased. That is what makes a flip
 * mid-fade safe: the mix reverses from wherever it is, with no clock to restart
 * and no curve to re-anchor, so the visible value stays continuous through any
 * number of reversals. Easing a two-way crossfade would either restart on each
 * flip or read as a stall at the turn.
 */
export class ThresholdCrossfadeDriver implements MotionDriver {
  readonly config: ThresholdCrossfadeConfig;

  #value: number;
  #phase: CrossfadePhase;

  constructor(config: ThresholdCrossfadeConfig, initialValue: number) {
    this.config = config;
    this.#value = clamp01(initialValue);
    this.#phase = this.#value >= 0.5 ? "high" : "low";
  }

  get value(): number {
    return this.#value;
  }

  get velocity(): number {
    const target = this.target;
    if (this.#value === target || this.config.crossfadeMs <= 0) return 0;
    return ((target > this.#value ? 1 : -1) * 1000) / this.config.crossfadeMs;
  }

  /** The committed endpoint: 1 once the high side wins, 0 once the low side does. */
  get target(): number {
    return this.#phase === "high" ? 1 : 0;
  }

  /** Which side is committed. Consumers read this to pick a foreground token set. */
  get phase(): CrossfadePhase {
    return this.#phase;
  }

  get settled(): boolean {
    return this.#value === this.target;
  }

  retarget(input: number): void {
    const half = this.config.hysteresis / 2;
    if (this.#phase === "low" && input > this.config.threshold + half) {
      this.#phase = "high";
    } else if (this.#phase === "high" && input < this.config.threshold - half) {
      this.#phase = "low";
    }
  }

  jumpTo(value: number): void {
    this.#value = clamp01(value);
    this.#phase = this.#value >= 0.5 ? "high" : "low";
  }

  advance(dtMs: number): void {
    if (!(dtMs > 0)) return;

    const target = this.target;
    if (this.config.crossfadeMs <= 0) {
      this.#value = target;
      return;
    }

    const step = dtMs / this.config.crossfadeMs;
    this.#value =
      this.#value < target
        ? Math.min(target, this.#value + step)
        : Math.max(target, this.#value - step);
  }
}

const clamp01 = (value: number): number => Math.min(1, Math.max(0, value));
