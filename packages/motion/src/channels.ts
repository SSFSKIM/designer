/**
 * The binding driver-per-channel table (§Motion).
 *
 * Every animated channel names exactly one driver family. The table is the
 * contract; the constants that configure each driver live in `tunables.ts` and
 * are advisory until calibration (C7) replaces them.
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
export const MOTION_DRIVER_KINDS = [
  "interruptible-spring",
  "critically-damped",
  "attack-decay",
  "low-pass-hysteresis",
  "threshold-crossfade",
  "monotonic-ease",
  "step",
  "hysteresis-cooldown",
] as const;

export type MotionDriverKind = (typeof MOTION_DRIVER_KINDS)[number];

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

/**
 * What a channel does to the material, which is what Reduced Motion needs to
 * know: `deformation` is what it removes, `positional` is what it must keep
 * (spatial continuity survives the policy — §Accessibility).
 */
export type ChannelRole = "positional" | "deformation" | "optical" | "discrete";

export const CHANNEL_ROLE: Readonly<Record<MotionChannel, ChannelRole>> = {
  position: "positional",
  size: "positional",
  radius: "positional",
  pressCompression: "deformation",
  lensStrength: "optical",
  glow: "optical",
  backdropAdaptation: "optical",
  foregroundTone: "optical",
  materialization: "optical",
  disabled: "discrete",
  qualityTier: "discrete",
};

const channelsWithRole = (role: ChannelRole): readonly MotionChannel[] =>
  MOTION_CHANNELS.filter((channel) => CHANNEL_ROLE[channel] === role);

/** Geometry channels — Reduced Motion damps these but never stops them. */
export const POSITIONAL_CHANNELS: readonly MotionChannel[] = channelsWithRole("positional");

/** Shape-distorting channels — Reduced Motion zeroes these (§Accessibility). */
export const DEFORMATION_CHANNELS: readonly MotionChannel[] = channelsWithRole("deformation");

/** Channels whose driver must never overshoot, so Reduced Motion cannot regress them. */
export const NON_OVERSHOOTING_CHANNELS: readonly MotionChannel[] = MOTION_CHANNELS.filter(
  (channel) =>
    MOTION_DRIVER_BY_CHANNEL[channel] === "monotonic-ease" ||
    MOTION_DRIVER_BY_CHANNEL[channel] === "step",
);

/**
 * Channels the interaction state machine drives from its state table.
 *
 * The rest are driven from outside it: geometry follows layout and morph
 * targets, `backdropAdaptation` and `foregroundTone` follow the backdrop, and
 * `qualityTier` follows the governor. They still animate through this package's
 * drivers — they are just not a function of interaction state.
 */
export const STATE_DRIVEN_CHANNELS: readonly MotionChannel[] = [
  "pressCompression",
  "lensStrength",
  "glow",
  "materialization",
  "disabled",
];
