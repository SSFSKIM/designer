import type { ExponentialConfig, MotionDriver } from "../driver";

/**
 * Asymmetric first-order approach (§Motion: glow/illumination — "fast attack +
 * slow exponential decay").
 *
 * Rising toward a target uses `attackMs`; falling away uses `decayMs`. The
 * asymmetry is in the time constant only, so each leg is a clean exponential
 * and the closed form is exact for any step.
 *
 * Velocity is derived rather than stored: for a first-order filter it is fully
 * determined by the gap and the active constant, so it can never go stale after
 * a retarget flips the direction.
 */
export class ExponentialDriver implements MotionDriver {
  readonly config: ExponentialConfig;

  #value: number;
  #target: number;

  constructor(config: ExponentialConfig, initialValue: number) {
    this.config = config;
    this.#value = initialValue;
    this.#target = initialValue;
  }

  get value(): number {
    return this.#value;
  }

  get velocity(): number {
    const tau = this.#timeConstantMs();
    if (tau <= 0) return 0;
    return ((this.#target - this.#value) * 1000) / tau;
  }

  get target(): number {
    return this.#target;
  }

  get settled(): boolean {
    return Math.abs(this.#value - this.#target) <= this.config.restDistance;
  }

  retarget(input: number): void {
    this.#target = input;
  }

  jumpTo(value: number): void {
    this.#value = value;
  }

  advance(dtMs: number): void {
    if (!(dtMs > 0)) return;

    const tau = this.#timeConstantMs();
    if (tau <= 0) {
      this.#value = this.#target;
      return;
    }

    this.#value = this.#target + (this.#value - this.#target) * Math.exp(-dtMs / tau);
  }

  /** Which leg we are on. The gap's sign decides, and it cannot flip mid-step. */
  #timeConstantMs(): number {
    return this.#target > this.#value ? this.config.attackMs : this.config.decayMs;
  }
}
