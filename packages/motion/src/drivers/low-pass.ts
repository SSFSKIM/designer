import type { LowPassConfig, MotionDriver } from "../driver";

/**
 * Exponential low-pass behind a hysteresis band (§Motion:
 * backdrop-adaptation values).
 *
 * The band filters the *input*: a new observation is committed only once it
 * departs the committed value by more than `hysteresis`, so scroll jitter never
 * reaches the filter at all. The low-pass then smooths the committed staircase,
 * which is why the output moves continuously even though commitment is
 * discrete.
 *
 * The band is measured from the committed value, not the current output. Against
 * the moving output a slowly drifting input would leak through one small step at
 * a time — precisely the pumping §Foreground adaptation rules out.
 */
export class LowPassHysteresisDriver implements MotionDriver {
  readonly config: LowPassConfig;

  #value: number;
  #committed: number;

  constructor(config: LowPassConfig, initialValue: number) {
    this.config = config;
    this.#value = initialValue;
    this.#committed = initialValue;
  }

  get value(): number {
    return this.#value;
  }

  get velocity(): number {
    const tau = this.config.timeConstantMs;
    if (tau <= 0) return 0;
    return ((this.#committed - this.#value) * 1000) / tau;
  }

  get target(): number {
    return this.#committed;
  }

  get settled(): boolean {
    return Math.abs(this.#value - this.#committed) <= this.config.restDistance;
  }

  retarget(input: number): void {
    if (Math.abs(input - this.#committed) <= this.config.hysteresis) return;
    this.#committed = input;
  }

  jumpTo(value: number): void {
    this.#value = value;
    this.#committed = value;
  }

  advance(dtMs: number): void {
    if (!(dtMs > 0)) return;

    const tau = this.config.timeConstantMs;
    if (tau <= 0) {
      this.#value = this.#committed;
      return;
    }

    this.#value = this.#committed + (this.#value - this.#committed) * Math.exp(-dtMs / tau);
  }
}
