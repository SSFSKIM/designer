/**
 * Monotonic easing curves for the `monotonic-ease` family (§Motion:
 * opacity/materialization — "no overshoot").
 *
 * Every curve declares its own slope rather than leaving callers to difference
 * it: `EaseDriver` reports velocity analytically, so a numeric derivative would
 * make velocity depend on frame size — exactly what the frame-rate invariance
 * requirement rules out.
 */

export interface Easing {
  /** Maps normalised progress `p ∈ [0, 1]` to eased progress; `at(0) === 0`, `at(1) === 1`. */
  at(p: number): number;
  /** d(at)/dp. Non-negative everywhere, which is what makes the curve overshoot-free. */
  slope(p: number): number;
}

export const EASING_NAMES = ["linear", "easeOutQuad", "easeOutCubic", "easeInOutCubic"] as const;

export type EasingName = (typeof EASING_NAMES)[number];

export const EASINGS: Readonly<Record<EasingName, Easing>> = {
  linear: {
    at: (p) => p,
    slope: () => 1,
  },
  easeOutQuad: {
    at: (p) => 1 - (1 - p) * (1 - p),
    slope: (p) => 2 * (1 - p),
  },
  easeOutCubic: {
    at: (p) => 1 - (1 - p) ** 3,
    slope: (p) => 3 * (1 - p) ** 2,
  },
  easeInOutCubic: {
    at: (p) => (p < 0.5 ? 4 * p ** 3 : 1 - 4 * (1 - p) ** 3),
    slope: (p) => (p < 0.5 ? 12 * p ** 2 : 12 * (1 - p) ** 2),
  },
};
