import { MOTION_CHANNELS, type MotionChannel } from "./channels";
import type {
  DriverConfig,
  EaseConfig,
  ExponentialConfig,
  LowPassConfig,
  SpringConfig,
  StepConfig,
  ThresholdCrossfadeConfig,
} from "./driver";
import type { FramePolicy } from "./frame";
import { INTERACTION_STATES, type InteractionState, type StateTargetTable } from "./states";

/**
 * Every number the motion kernel runs on, in one place.
 *
 * **These values are advisory.** §Calibration names spring constants and
 * hysteresis rates as delegated unknowns: C7's harness measures them against
 * `apple-macos-26.5-*` fixtures and replaces what is here. Nothing downstream
 * may hard-code a constant of its own — a profile object overrides every one of
 * them (`withProfileOverrides`), so replacing the whole calibrated set later is
 * a data change, not a code change.
 *
 * Units: milliseconds for time, channel units for distance, channel units per
 * second for velocity.
 */
export interface ReducedMotionTunables {
  /**
   * Floor applied to every spring's ζ. At 1 the spring is critically damped:
   * fastest arrival with no overshoot, which is the elastic term §Accessibility
   * removes.
   */
  readonly minDampingRatio: number;
  /**
   * Multiplier on positional response times — "shortens morphs to non-elastic
   * interpolation". Below 1 shortens.
   */
  readonly morphResponseFactor: number;
}

export interface MotionProfile {
  readonly frame: FramePolicy;
  /** One driver configuration per channel. Its `kind` must match the binding table. */
  readonly channels: Readonly<Record<MotionChannel, DriverConfig>>;
  readonly stateTargets: StateTargetTable;
  readonly reducedMotion: ReducedMotionTunables;
  /**
   * Geometric scale removed at full press compression — the "~1–2%" of parent
   * acceptance #3. The `pressCompression` channel runs 0…1; this is what 1
   * means, so the renderer needs no constant of its own.
   */
  readonly pressCompressionScale: number;
  /**
   * Whether `withReducedMotion` has run over this profile. Derived, not a
   * tunable: it keeps the policy idempotent, and it lets a consumer report which
   * profile is actually in force rather than inferring it from a media query it
   * may not have been the one to read.
   */
  readonly reducedMotionApplied: boolean;
}

export const DEFAULT_MOTION_PROFILE: MotionProfile = {
  frame: { maxDeltaMs: 50 },

  channels: {
    // Layout and morph geometry. Slightly underdamped: a trace of overshoot is
    // what reads as material rather than as a tween.
    position: {
      kind: "interruptible-spring",
      responseMs: 420,
      dampingRatio: 0.82,
      restDistance: 0.02,
      restVelocity: 0.05,
    },
    size: {
      kind: "interruptible-spring",
      responseMs: 460,
      dampingRatio: 0.85,
      restDistance: 0.02,
      restVelocity: 0.05,
    },
    radius: {
      kind: "interruptible-spring",
      responseMs: 460,
      dampingRatio: 0.9,
      restDistance: 0.02,
      restVelocity: 0.05,
    },

    // Press compression. Faster and looser than layout — the release bounce is
    // most of what makes a press feel physical.
    pressCompression: {
      kind: "interruptible-spring",
      responseMs: 260,
      dampingRatio: 0.72,
      restDistance: 1e-3,
      restVelocity: 5e-3,
    },

    // Optical strength must not overshoot: past 1 the lens visibly over-bends.
    lensStrength: {
      kind: "critically-damped",
      responseMs: 300,
      dampingRatio: 1,
      restDistance: 1e-3,
      restVelocity: 5e-3,
    },

    // Fast attack, slow decay: light arrives with the finger and lingers after.
    glow: { kind: "attack-decay", attackMs: 70, decayMs: 320, restDistance: 1e-3 },

    // Backdrop adaptation. Long constant and a wide band so scrolling past a
    // contrast edge cannot pump the material.
    backdropAdaptation: {
      kind: "low-pass-hysteresis",
      timeConstantMs: 500,
      hysteresis: 0.04,
      restDistance: 1e-3,
    },

    // Foreground light/dark. Band wide enough that mid-luminance backdrops do
    // not oscillate the text colour.
    foregroundTone: {
      kind: "threshold-crossfade",
      threshold: 0.5,
      hysteresis: 0.08,
      crossfadeMs: 180,
    },

    materialization: { kind: "monotonic-ease", durationMs: 220, easing: "easeOutCubic" },

    disabled: { kind: "step", hysteresis: 0, cooldownMs: 0 },

    // Quality tier. Long dwell, half-a-tier band: §Performance's governor
    // switches tiers only with long hysteresis and cooldown.
    qualityTier: { kind: "hysteresis-cooldown", hysteresis: 0.5, cooldownMs: 2500 },
  },

  // Interaction-driven targets. Geometry, backdrop and governor channels are
  // absent because interaction state does not decide them (§channels).
  stateTargets: {
    idle: {
      pressCompression: 0,
      lensStrength: 1,
      glow: 0,
      materialization: 1,
      disabled: 0,
    },
    hover: {
      pressCompression: 0,
      lensStrength: 1.06,
      glow: 0.28,
      materialization: 1,
      disabled: 0,
    },
    pressed: {
      pressCompression: 1,
      lensStrength: 1.14,
      glow: 1,
      materialization: 1,
      disabled: 0,
    },
    focused: {
      pressCompression: 0,
      lensStrength: 1.03,
      glow: 0.16,
      materialization: 1,
      disabled: 0,
    },
    disabled: {
      pressCompression: 0,
      lensStrength: 0.5,
      glow: 0,
      materialization: 1,
      disabled: 1,
    },
    morphing: {
      pressCompression: 0,
      lensStrength: 1.1,
      glow: 0.35,
      materialization: 1,
      disabled: 0,
    },
  },

  reducedMotion: { minDampingRatio: 1, morphResponseFactor: 0.7 },

  pressCompressionScale: 0.015,

  reducedMotionApplied: false,
};

/** A profile patch: any subset, to any depth, of what a profile holds. */
export interface MotionProfilePatch {
  readonly frame?: Partial<FramePolicy>;
  readonly channels?: Readonly<Partial<Record<MotionChannel, DriverConfigPatch>>>;
  readonly stateTargets?: Readonly<Partial<Record<InteractionState, Readonly<Partial<Record<MotionChannel, number>>>>>>;
  readonly reducedMotion?: Partial<ReducedMotionTunables>;
  readonly pressCompressionScale?: number;
}

/**
 * A patch to one channel's driver configuration: either a subset of one
 * family's constants, or a whole replacement configuration.
 *
 * Written as a union of the families rather than `Partial<Omit<DriverConfig,
 * "kind">>`, which collapses to `{}` — the union members share only `kind`, so
 * omitting it leaves nothing to be partial about, and every typo would pass.
 *
 * Naming a different `kind` replaces the configuration outright: half a
 * spring's constants merged onto an ease would type-check and mean nothing.
 */
export type DriverConfigPatch =
  | DriverConfig
  | Readonly<Partial<SpringConfig>>
  | Readonly<Partial<ExponentialConfig>>
  | Readonly<Partial<LowPassConfig>>
  | Readonly<Partial<ThresholdCrossfadeConfig>>
  | Readonly<Partial<EaseConfig>>
  | Readonly<Partial<StepConfig>>;

/**
 * Apply a patch. This is how a calibration profile lands: C7 emits the measured
 * numbers, the app passes them here, and every constant above is replaceable
 * without touching this file.
 */
export function withProfileOverrides(
  base: MotionProfile,
  patch: MotionProfilePatch,
): MotionProfile {
  const channels = {} as Record<MotionChannel, DriverConfig>;
  for (const channel of MOTION_CHANNELS) {
    channels[channel] = mergeDriverConfig(base.channels[channel], patch.channels?.[channel]);
  }

  const stateTargets = {} as Record<InteractionState, Readonly<Partial<Record<MotionChannel, number>>>>;
  for (const state of INTERACTION_STATES) {
    stateTargets[state] = { ...base.stateTargets[state], ...patch.stateTargets?.[state] };
  }

  return {
    frame: { ...base.frame, ...patch.frame },
    channels,
    stateTargets,
    reducedMotion: { ...base.reducedMotion, ...patch.reducedMotion },
    pressCompressionScale: patch.pressCompressionScale ?? base.pressCompressionScale,
    // Derived, so a patch cannot claim it. Patching a reduced profile keeps it
    // reduced, and the patch's own numbers are taken at face value.
    reducedMotionApplied: base.reducedMotionApplied,
  };
}

function mergeDriverConfig(
  base: DriverConfig,
  patch: DriverConfigPatch | undefined,
): DriverConfig {
  if (patch === undefined) return base;

  // Only one union member carries `kind`, and reading it is the whole
  // discrimination, so probe for it rather than narrowing seven branches.
  const patchKind = (patch as { readonly kind?: DriverConfig["kind"] }).kind;
  if (patchKind !== undefined && patchKind !== base.kind) return patch as DriverConfig;

  return { ...base, ...patch } as DriverConfig;
}
