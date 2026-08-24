import type { EaseConfig, MotionDriver } from "../driver";
import { EASINGS, type Easing } from "../easing";

/**
 * Monotonic time-based ramp (§Motion: opacity/materialization — "no
 * overshoot").
 *
 * Progress is linear in time and the curve is non-decreasing, so the value can
 * never leave the interval between where it started and where it is going.
 *
 * A redirect re-anchors on the current value and restarts progress. That is a
 * velocity discontinuity, and it is the right trade here: a materialising
 * surface must not overshoot its opacity, and only a monotone curve over a
 * bounded interval guarantees that. Channels that need velocity carried across a
 * redirect are the spring's, per the driver table.
 */
export class EaseDriver implements MotionDriver {
  readonly config: EaseConfig;

  readonly #easing: Easing;
  #from: number;
  #to: number;
  #progress: number;

  constructor(config: EaseConfig, initialValue: number) {
    this.config = config;
    this.#easing = EASINGS[config.easing];
    this.#from = initialValue;
    this.#to = initialValue;
    this.#progress = 1;
  }

  get value(): number {
    // `from + (to - from) * 1` is not exactly `to` in floating point, and a
    // finished materialization has to land on its opacity exactly.
    if (this.#progress >= 1) return this.#to;
    return this.#from + (this.#to - this.#from) * this.#easing.at(this.#progress);
  }

  get velocity(): number {
    // A finished ramp is at rest even under a curve whose slope at p = 1 is not
    // zero, so `settled` and `velocity === 0` never disagree.
    if (this.#progress >= 1 || this.config.durationMs <= 0) return 0;
    return (
      ((this.#to - this.#from) * this.#easing.slope(this.#progress) * 1000) / this.config.durationMs
    );
  }

  get target(): number {
    return this.#to;
  }

  get settled(): boolean {
    return this.#progress >= 1;
  }

  retarget(input: number): void {
    if (input === this.#to) return;
    this.#from = this.value;
    this.#to = input;
    this.#progress = 0;
  }

  jumpTo(value: number): void {
    this.#from = value;
    this.#to = value;
    this.#progress = 1;
  }

  advance(dtMs: number): void {
    if (!(dtMs > 0)) return;

    if (this.config.durationMs <= 0) {
      this.#progress = 1;
      return;
    }

    this.#progress = Math.min(1, this.#progress + dtMs / this.config.durationMs);
  }
}
