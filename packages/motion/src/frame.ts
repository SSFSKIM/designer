/**
 * The capped-step rule (§Motion: "closed-form or capped fixed-step so 60 Hz,
 * 120 Hz and dropped frames produce the same response").
 *
 * Every driver here is closed-form, so the cap is not a stability device — no
 * step size can make one explode. It is a semantic one. A backgrounded tab, a
 * blocking layout or a long task hands the next frame a gap of hundreds of
 * milliseconds, and honouring that gap exactly would resolve the whole animation
 * during the stall: the user looks away mid-press and looks back to find the
 * press already over. Capping resumes the animation instead of skipping it.
 *
 * The cap lives here, at the frame boundary, and never inside a driver.
 * `advance` stays exact for whatever delta it is given, which is what keeps
 * frame-rate invariance a property of the drivers rather than of the cap.
 */
export interface FramePolicy {
  /**
   * Longest delta a single frame may represent. Above two dropped 60 Hz frames
   * so ordinary jitter passes through untouched; below the slowest channel's
   * time constant so a stall cannot finish an animation.
   */
  readonly maxDeltaMs: number;
}

/**
 * Normalise a measured frame delta. Non-finite, zero and negative deltas — a
 * clock that jumped backwards, a first frame with no predecessor — become 0.
 */
export function clampFrameDelta(dtMs: number, policy: FramePolicy): number {
  if (!(dtMs > 0)) return 0;
  return Math.min(dtMs, policy.maxDeltaMs);
}
