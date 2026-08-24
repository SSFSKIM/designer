/**
 * `@vitrea/motion` — the motion kernel (child C2 of
 * `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`).
 *
 * Pure time-domain math and state: the per-channel driver families of §Motion,
 * the six v1 interaction states with their interruption semantics, and the
 * Reduced Motion policy transform. No DOM, no timers, no requestAnimationFrame
 * (X4) — `platform-web` owns the clock and calls `advance` with the delta it
 * measured.
 *
 * The two properties everything else here is arranged around:
 *
 * 1. **Frame-rate invariance.** Every continuous family integrates in closed
 *    form, so one 33.4 ms step, two 16.7 ms steps and four 8.35 ms steps agree
 *    to floating point. The capped-step rule (`clampFrameDelta`) lives at the
 *    frame boundary and exists for a stalled tab's sake, not for stability.
 * 2. **Interruption without restart.** `retarget` moves only the target;
 *    position and velocity carry across untouched. A release mid-press and an
 *    immediate re-press redirect the same trajectory rather than starting new
 *    ones (parent acceptance #3).
 */

export {
  CHANNEL_ROLE,
  DEFORMATION_CHANNELS,
  MOTION_CHANNELS,
  MOTION_DRIVER_BY_CHANNEL,
  MOTION_DRIVER_KINDS,
  NON_OVERSHOOTING_CHANNELS,
  POSITIONAL_CHANNELS,
  STATE_DRIVEN_CHANNELS,
  type ChannelRole,
  type MotionChannel,
  type MotionDriverKind,
} from "./channels";

export {
  type DriverConfig,
  type EaseConfig,
  type ExponentialConfig,
  type LowPassConfig,
  type MotionDriver,
  type SpringConfig,
  type StepConfig,
  type ThresholdCrossfadeConfig,
} from "./driver";

export { EASINGS, EASING_NAMES, type Easing, type EasingName } from "./easing";

export { createDriver } from "./drivers/create";
export { EaseDriver } from "./drivers/ease";
export { ExponentialDriver } from "./drivers/exponential";
export { LowPassHysteresisDriver } from "./drivers/low-pass";
export { SpringDriver } from "./drivers/spring";
export { StepDriver } from "./drivers/step";
export { ThresholdCrossfadeDriver, type CrossfadePhase } from "./drivers/threshold-crossfade";

export { clampFrameDelta, type FramePolicy } from "./frame";

export {
  INTERACTION_STATES,
  LEGAL_TRANSITIONS,
  canTransition,
  channelsMovedBy,
  resolveInteractionState,
  type InteractionFlags,
  type InteractionState,
  type StateTargetTable,
  type StateTargets,
} from "./states";

export {
  DEFAULT_MOTION_PROFILE,
  withProfileOverrides,
  type DriverConfigPatch,
  type MotionProfile,
  type MotionProfilePatch,
  type ReducedMotionTunables,
} from "./tunables";
