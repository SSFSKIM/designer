import type { MotionDriver, StepConfig } from "../driver";

/**
 * Discrete channels (§Motion).
 *
 * Two table rows, one family, separated only by configuration:
 *
 * - `disabled` — plain step. `{ hysteresis: 0, cooldownMs: 0 }` accepts every
 *   change instantly, which is what an on/off channel wants.
 * - `qualityTier` — "long hysteresis + cooldown". The band rejects small
 *   fluctuations in the governor's signal; the cooldown enforces a minimum dwell
 *   so the tier cannot flap, and §Performance's "never mid-interaction" holds
 *   because the caller stops offering changes during one.
 *
 * The cooldown counts elapsed milliseconds, not calls, so it lasts the same wall
 * time at 30 Hz and at 120 Hz. A rejected offer is forgotten rather than queued:
 * a governor re-evaluates every frame, so remembering a stale verdict would fire
 * a change the evidence no longer supports.
 */
export class StepDriver implements MotionDriver {
  readonly config: StepConfig;

  #value: number;
  /** Infinity so the first change never waits out a cooldown it never started. */
  #sinceChangeMs = Number.POSITIVE_INFINITY;

  constructor(config: StepConfig, initialValue: number) {
    this.config = config;
    this.#value = initialValue;
  }

  get value(): number {
    return this.#value;
  }

  get velocity(): number {
    return 0;
  }

  get target(): number {
    return this.#value;
  }

  get settled(): boolean {
    return true;
  }

  retarget(input: number): void {
    if (Math.abs(input - this.#value) <= this.config.hysteresis) return;
    if (this.#sinceChangeMs < this.config.cooldownMs) return;
    this.#value = input;
    this.#sinceChangeMs = 0;
  }

  jumpTo(value: number): void {
    this.#value = value;
    this.#sinceChangeMs = Number.POSITIVE_INFINITY;
  }

  advance(dtMs: number): void {
    if (!(dtMs > 0)) return;
    this.#sinceChangeMs += dtMs;
  }
}
