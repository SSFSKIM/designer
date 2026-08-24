import type { MotionDriver, SpringConfig } from "../driver";

/**
 * ζ within this of 1 takes the critical branch. Below it the underdamped and
 * overdamped forms divide by ωd or by (r₁ − r₂), both of which vanish at ζ = 1.
 */
const CRITICAL_EPSILON = 1e-6;

/**
 * The velocity-preserving interruptible spring (§Motion: position, size,
 * radius, press compression).
 *
 * Solves y'' + 2ζω y' + ω² y = 0 exactly, where y = value − target, so one
 * `advance(33.4)` and four `advance(8.35)` land on the same state to floating
 * point. No numerical integrator appears here, which is what makes 60 Hz,
 * 120 Hz and a dropped frame produce the same response rather than the same
 * response plus an integrator's error term.
 *
 * `retarget` moves only the target. Position and velocity carry across
 * untouched, so a release mid-press bends the trajectory instead of restarting
 * it — parent acceptance #3.
 */
export class SpringDriver implements MotionDriver {
  readonly config: SpringConfig;

  readonly #omega: number;
  #value: number;
  #velocity = 0;
  #target: number;

  constructor(config: SpringConfig, initialValue: number) {
    this.config = config;
    this.#omega = (2 * Math.PI * 1000) / config.responseMs;
    this.#value = initialValue;
    this.#target = initialValue;
  }

  get value(): number {
    return this.#value;
  }

  get velocity(): number {
    return this.#velocity;
  }

  get target(): number {
    return this.#target;
  }

  get settled(): boolean {
    return (
      Math.abs(this.#value - this.#target) <= this.config.restDistance &&
      Math.abs(this.#velocity) <= this.config.restVelocity
    );
  }

  retarget(input: number): void {
    this.#target = input;
  }

  jumpTo(value: number, velocity = 0): void {
    this.#value = value;
    this.#velocity = velocity;
  }

  advance(dtMs: number): void {
    if (!(dtMs > 0)) return;

    const t = dtMs / 1000;
    const w = this.#omega;
    const zeta = this.config.dampingRatio;
    const y0 = this.#value - this.#target;
    const v0 = this.#velocity;

    let y: number;
    let v: number;

    if (Math.abs(zeta - 1) < CRITICAL_EPSILON) {
      // y = (y₀ + (v₀ + ω y₀) t) e^(−ωt)
      const decay = Math.exp(-w * t);
      const c = v0 + w * y0;
      y = (y0 + c * t) * decay;
      v = (v0 - w * c * t) * decay;
    } else if (zeta < 1) {
      // Damped oscillation: e^(−ζωt) (A cos ω_d t + B sin ω_d t).
      const wd = w * Math.sqrt(1 - zeta * zeta);
      const decay = Math.exp(-zeta * w * t);
      const cos = Math.cos(wd * t);
      const sin = Math.sin(wd * t);
      const b = (v0 + zeta * w * y0) / wd;
      y = decay * (y0 * cos + b * sin);
      v = decay * ((b * wd - zeta * w * y0) * cos - (y0 * wd + zeta * w * b) * sin);
    } else {
      // Two real roots, both negative. Written as a sum of decaying
      // exponentials rather than e^(−ζωt) cosh(st): for a stiff, strongly
      // overdamped spring over a long step the cosh overflows while the
      // exponential underflows, and the product is NaN.
      const s = w * Math.sqrt(zeta * zeta - 1);
      const r1 = -zeta * w + s;
      const r2 = -zeta * w - s;
      const e1 = Math.exp(r1 * t);
      const e2 = Math.exp(r2 * t);
      const c1 = (v0 - r2 * y0) / (r1 - r2);
      const c2 = (v0 - r1 * y0) / (r1 - r2);
      y = c1 * e1 - c2 * e2;
      v = c1 * r1 * e1 - c2 * r2 * e2;
    }

    this.#value = this.#target + y;
    this.#velocity = v;
  }
}
