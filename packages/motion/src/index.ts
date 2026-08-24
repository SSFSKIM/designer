/**
 * @vitrea/motion — skeleton (C1).
 *
 * Encodes §Motion's binding driver-per-channel table and the v1 interaction
 * states so C2 implements against a fixed surface. Pure math and state: no DOM,
 * no timers, no rAF (X4) — platform-web owns scheduling.
 */

/** Animated channels. Each has exactly one driver family (§Motion, binding). */
export const MOTION_CHANNELS = [
  "position",
  "size",
  "radius",
  "pressCompression",
  "lensStrength",
  "glow",
  "backdropAdaptation",
  "foregroundTone",
  "materialization",
  "disabled",
  "qualityTier",
] as const;

export type MotionChannel = (typeof MOTION_CHANNELS)[number];

/**
 * Driver families. `interruptible-spring` is the velocity-preserving one:
 * a redirect continues from current position and velocity, never restarts.
 */
export type MotionDriverKind =
  | "interruptible-spring"
  | "critically-damped"
  | "attack-decay"
  | "low-pass-hysteresis"
  | "threshold-crossfade"
  | "monotonic-ease"
  | "step"
  | "hysteresis-cooldown";

export const MOTION_DRIVER_BY_CHANNEL: Readonly<Record<MotionChannel, MotionDriverKind>> = {
  position: "interruptible-spring",
  size: "interruptible-spring",
  radius: "interruptible-spring",
  pressCompression: "interruptible-spring",
  lensStrength: "critically-damped",
  glow: "attack-decay",
  backdropAdaptation: "low-pass-hysteresis",
  foregroundTone: "threshold-crossfade",
  materialization: "monotonic-ease",
  disabled: "step",
  qualityTier: "hysteresis-cooldown",
};

/** v1 interaction states (§Motion). Neighbor glow diffusion is post-v1. */
export const INTERACTION_STATES = [
  "idle",
  "hover",
  "pressed",
  "focused",
  "disabled",
  "morphing",
] as const;

export type InteractionState = (typeof INTERACTION_STATES)[number];

/** Channels whose driver must never overshoot, so Reduced Motion cannot regress them. */
export const NON_OVERSHOOTING_CHANNELS: readonly MotionChannel[] = MOTION_CHANNELS.filter(
  (channel) =>
    MOTION_DRIVER_BY_CHANNEL[channel] === "monotonic-ease" ||
    MOTION_DRIVER_BY_CHANNEL[channel] === "step",
);
