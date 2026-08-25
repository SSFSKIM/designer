/**
 * Calibration refuses rather than guesses.
 *
 * Every metric in this package is evidence for a fidelity claim, so a silent
 * accommodation — resizing a mismatched capture, defaulting an unparseable
 * profile key, fitting a slope through a constant — would produce a number that
 * looks like a measurement and is not one. Those are the only things this
 * package refuses, and it refuses them all the same way.
 */

export type CalibrationErrorCode =
  /** Two images (or an image and its background) do not have the same pixel dimensions. */
  | "dimension-mismatch"
  /** A PNG buffer decoded to something other than 8-bit RGBA of the declared size. */
  | "malformed-png"
  /** A metric was asked to summarise zero samples — an empty region, or an image smaller than the window. */
  | "empty-region"
  /** A cell key carried a profile string that the X9 grammar does not accept. */
  | "invalid-profile-key"
  /** Two frame sequences cannot be compared frame-for-frame (length or timebase). */
  | "frame-sequence-mismatch"
  /** A least-squares fit has no information: the independent variable does not vary. */
  | "degenerate-fit"
  /** A serialized result matrix does not carry the envelope this package writes. */
  | "malformed-report";

export class CalibrationError extends Error {
  readonly code: CalibrationErrorCode;

  constructor(code: CalibrationErrorCode, message: string) {
    super(message);
    this.name = "CalibrationError";
    this.code = code;
  }
}
