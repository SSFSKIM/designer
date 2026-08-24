import { CHANNEL_ROLE, MOTION_CHANNELS, type MotionChannel } from "./channels";
import type { DriverConfig } from "./driver";
import { INTERACTION_STATES, type InteractionState, type StateTargets } from "./states";
import type { MotionProfile } from "./tunables";

/**
 * Apply the Reduced Motion policy (§Accessibility, §Motion, parent
 * acceptance #6).
 *
 * The policy is a **transform over the profile**, not a branch in the drivers.
 * Nothing downstream learns a second code path: `platform-web` resolves the
 * media query once, hands the machine a different set of numbers, and every
 * channel keeps the driver family the binding table gives it.
 *
 * What it does, and why each part is what §Accessibility asks for:
 *
 * - **Elastic overshoot goes.** Every spring's ζ is floored at
 *   `minDampingRatio` (1 by default — critically damped: the fastest arrival
 *   with no overshoot at all).
 * - **Deformation goes.** Every deformation channel's target is 0 in every
 *   state, so a press no longer compresses the surface.
 * - **Positional continuity stays.** Geometry channels remain springs rather
 *   than becoming steps or crossfades, so a morph still travels; its response
 *   time is scaled by `morphResponseFactor`, which is "shortens morphs to
 *   non-elastic interpolation".
 * - **Optical response stays.** Glow, lensing and tint are illumination, not
 *   motion. Removing them would leave a reduced-motion control with no feedback
 *   at all; reducing them is `prefers-reduced-transparency` and
 *   `prefers-contrast`, which are separate policies on separate queries.
 *
 * Shimmer travel, which §Motion also names, has no channel in v1 — the specular
 * sweep is the renderer's, so C6 removes it there against this same flag.
 * "Reserves crossfade for large plane shifts" is likewise C5's: which plane
 * change crossfades is not a decision the kernel can see.
 *
 * Idempotent, and it says so on the profile: `reducedMotionApplied` exists
 * because the damping floor tolerates a second pass and the response factor does
 * not. Apply app overrides first and this last — a patch applied afterwards is
 * taken at face value, since an app that overrides a reduced profile means it.
 */
export function withReducedMotion(profile: MotionProfile): MotionProfile {
  if (profile.reducedMotionApplied) return profile;

  const channels = {} as Record<MotionChannel, DriverConfig>;
  for (const channel of MOTION_CHANNELS) {
    channels[channel] = reduceDriverConfig(profile, channel);
  }

  const stateTargets = {} as Record<InteractionState, StateTargets>;
  for (const state of INTERACTION_STATES) {
    const targets: Record<string, number> = { ...profile.stateTargets[state] };
    for (const channel of Object.keys(targets)) {
      if (CHANNEL_ROLE[channel as MotionChannel] === "deformation") targets[channel] = 0;
    }
    stateTargets[state] = targets as StateTargets;
  }

  return { ...profile, channels, stateTargets, reducedMotionApplied: true };
}

function reduceDriverConfig(profile: MotionProfile, channel: MotionChannel): DriverConfig {
  const config = profile.channels[channel];
  if (config.kind !== "interruptible-spring" && config.kind !== "critically-damped") {
    return config;
  }

  const { minDampingRatio, morphResponseFactor } = profile.reducedMotion;
  const positional = CHANNEL_ROLE[channel] === "positional";
  return {
    ...config,
    dampingRatio: Math.max(config.dampingRatio, minDampingRatio),
    responseMs: positional ? config.responseMs * morphResponseFactor : config.responseMs,
  };
}
