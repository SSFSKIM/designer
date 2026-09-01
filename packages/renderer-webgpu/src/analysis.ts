/**
 * Backdrop analysis on the CPU side: the stats a reduction produced, and the
 * temporal hysteresis that makes them usable.
 *
 * §Motion binds `backdrop-adaptation values` to the *exponential low-pass +
 * hysteresis* driver, and §Motion also puts every driver on the CPU. So the shape
 * is: the GPU reduces (exactly — X2's `analysis: "exact"`), the result is read
 * back at a low rate, and `LowPassHysteresisDriver` from `@vitrea/motion` — the
 * same class the rest of the runtime uses, not a reimplementation — smooths it.
 * The shader reads the driver's output as a uniform and never sees the raw stat.
 *
 * ## Why the readback is not a per-frame cost
 *
 * §Foreground adaptation caps the readback at an advisory 15 Hz (Decision Log
 * #19), and the governor lowers it further. That is not a performance
 * concession — it is what keeps the adaptation honest. A per-frame readback would
 * either stall the pipeline waiting for the map, or produce a value two frames old
 * and pretend it was current. At 15 Hz with a 500 ms low-pass the staleness is far
 * inside the filter's own time constant, so it is invisible in the output.
 *
 * ## The band is on the input, not the output
 *
 * `LowPassHysteresisDriver` commits a new observation only once it departs the
 * *committed* value by more than the band, then low-passes the committed
 * staircase. Measuring against the moving output instead would let a slow drift
 * leak through one small step at a time, which is exactly the foreground pumping
 * §Foreground adaptation rules out. That property is the driver's, and it is the
 * reason to use the driver rather than an `exp()` here.
 */

import { LowPassHysteresisDriver } from "@vitrea/motion";

import { DEFAULT_MATERIAL_PROFILE, type MaterialProfile } from "./material";
import { srgbToLinearChannel, type Rgb } from "./color";

/** The four floats the reduction writes. */
export interface BackdropStats {
  /** Mean linear luminance, 0..1-ish (an HDR-ish source can exceed 1). */
  readonly luminance: number;
  /** Variance of linear luminance. */
  readonly variance: number;
  /** Mean luminance-gradient magnitude per texel — the edge-density measure. */
  readonly edgeDensity: number;
  /** Samples the reduction actually took. 0 means "never reduced". */
  readonly sampleCount: number;
}

export const ZERO_STATS: BackdropStats = {
  luminance: 0,
  variance: 0,
  edgeDensity: 0,
  sampleCount: 0,
};

export function statsFromBuffer(values: ArrayLike<number>): BackdropStats {
  return {
    // The reduction publishes the ENCODED-space mean (the W9 model, claims
    // §5.31) and this is its one decode: every consumer downstream — the
    // drivers, `adaptiveTint`'s fitted thresholds — still speaks linear light,
    // and a solid backdrop reads identically under either convention.
    luminance: srgbToLinearChannel(values[0] ?? 0),
    variance: values[1] ?? 0,
    edgeDensity: values[2] ?? 0,
    sampleCount: values[3] ?? 0,
  };
}

/**
 * Driver configuration for the three adaptation channels.
 *
 * The time constant and band are §Motion's `backdropAdaptation` defaults — a long
 * constant and a wide band so scrolling past a contrast edge cannot pump the
 * material. Restated as a literal rather than read off `DEFAULT_MOTION_PROFILE`
 * because `edgeDensity` and `variance` live on different scales from luminance and
 * want their own bands; the *shape* is motion's, the widths are this package's.
 */
const LUMINANCE_CONFIG = {
  kind: "low-pass-hysteresis",
  timeConstantMs: 500,
  hysteresis: 0.04,
  restDistance: 1e-3,
} as const;

const VARIANCE_CONFIG = { ...LUMINANCE_CONFIG, hysteresis: 0.01 } as const;
const EDGE_CONFIG = { ...LUMINANCE_CONFIG, hysteresis: 0.01 } as const;

export interface AdaptationValues {
  readonly luminance: number;
  readonly variance: number;
  readonly edgeDensity: number;
  /** The tint the optics pass should mix toward, in linear light. */
  readonly tint: Rgb;
  /** True once at least one reduction has been observed. */
  readonly observed: boolean;
}

export interface AdaptationState {
  /** Commit a fresh reduction. Cheap — the band may reject it outright. */
  observe(stats: BackdropStats): void;
  /** Advance the filters by a frame delta in ms. */
  advance(deltaMs: number): void;
  /** Jump the filters to a reduction with no transient. Used on the first frame. */
  reset(stats: BackdropStats): void;
  readonly values: AdaptationValues;
  readonly settled: boolean;
}

const smoothstep = (edge0: number, edge1: number, x: number): number => {
  if (edge1 <= edge0) return x < edge0 ? 0 : 1;
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
};

/**
 * The adaptive tint: a crossfade between the dark-backdrop and light-backdrop
 * tints across a luminance band.
 *
 * The crossfade is deliberately not a hard threshold. §Motion gives the
 * *foreground* light/dark decision a threshold-plus-crossfade driver because it
 * feeds a DOM `color`, which is discrete; the material's own tint is continuous
 * and can simply follow the smoothed luminance, so it does. One fewer driver, and
 * no risk of the tint and the foreground disagreeing at the threshold.
 */
export function adaptiveTint(
  luminance: number,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): Rgb {
  const dark = profile.adaptiveTintDark;
  const light = profile.adaptiveTintLight;
  const t = smoothstep(profile.adaptiveLuminanceLow, profile.adaptiveLuminanceHigh, luminance);
  return [
    dark[0] + (light[0] - dark[0]) * t,
    dark[1] + (light[1] - dark[1]) * t,
    dark[2] + (light[2] - dark[2]) * t,
  ];
}

export function createAdaptationState(
  initial: BackdropStats = ZERO_STATS,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): AdaptationState {
  const luminance = new LowPassHysteresisDriver(LUMINANCE_CONFIG, initial.luminance);
  const variance = new LowPassHysteresisDriver(VARIANCE_CONFIG, initial.variance);
  const edge = new LowPassHysteresisDriver(EDGE_CONFIG, initial.edgeDensity);
  let observed = initial.sampleCount > 0;

  return {
    observe(stats) {
      if (stats.sampleCount <= 0) return;
      observed = true;
      luminance.retarget(stats.luminance);
      variance.retarget(stats.variance);
      edge.retarget(stats.edgeDensity);
    },

    advance(deltaMs) {
      luminance.advance(deltaMs);
      variance.advance(deltaMs);
      edge.advance(deltaMs);
    },

    reset(stats) {
      observed = stats.sampleCount > 0;
      luminance.jumpTo(stats.luminance);
      variance.jumpTo(stats.variance);
      edge.jumpTo(stats.edgeDensity);
    },

    get values() {
      return {
        luminance: luminance.value,
        variance: variance.value,
        edgeDensity: edge.value,
        tint: adaptiveTint(luminance.value, profile),
        observed,
      };
    },

    get settled() {
      return luminance.settled && variance.settled && edge.settled;
    },
  };
}

/**
 * Whether a readback is due, given the governor's cadence.
 *
 * A single-slot gate rather than a queue: if the previous map has not resolved the
 * next one is simply skipped. Queueing readbacks under pressure is how a renderer
 * ends up with a backlog of stale buffers and a growing memory footprint, and the
 * consumer here cannot use two answers from the same frame anyway.
 */
export function readbackDue(
  lastAtMs: number | undefined,
  nowMs: number,
  cadenceHz: number,
): boolean {
  if (cadenceHz <= 0) return false;
  if (lastAtMs === undefined) return true;
  return nowMs - lastAtMs >= 1000 / cadenceHz;
}
