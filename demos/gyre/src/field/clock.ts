/**
 * The instrument's clock: one mutable record the field, the probe and the
 * transport all read, so that a pause or a scrub reaches every reader on the same
 * frame without a React render in between.
 */

export interface FieldClock {
  /** Field time, in seconds of animation. Advances only while playing. */
  elapsed: number;
  /** The scrub, in hours from the observation time. */
  offsetHours: number;
  playing: boolean;
}

/** How much field time one hour of scrub is worth. */
const SECONDS_PER_HOUR = 6;

export function createClock(): FieldClock {
  return { elapsed: 0, offsetHours: 0, playing: true };
}

/** The single number the shader and the sampler take as `time`. */
export function fieldTime(clock: FieldClock): number {
  return clock.elapsed * 0.12 + clock.offsetHours * SECONDS_PER_HOUR * 0.12;
}
