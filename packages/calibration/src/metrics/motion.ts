/**
 * The motion axis — declared in full, implemented in part.
 *
 * The methodology names six motion metrics. Five of them (response latency,
 * peak compression, overshoot, settling time, redirect continuity) are
 * statements about *timing*, and timing cannot be measured from the frames
 * alone: each needs a capture path that puts a trustworthy timestamp on the
 * input event and on every rendered frame, on both the native and the web side.
 * That capture path is C9's, and it is a substantial piece of work in its own
 * right.
 *
 * So this module declares the whole family as types — so the report schema, the
 * CLI and C9 all name the same six things — and implements exactly one:
 * `morphSilhouetteTrajectory`, which is the one metric in the family that is a
 * function of the frames themselves. It compares *where the shape went*, frame
 * by frame, which is enough to catch a morph that takes the wrong path even
 * before anyone can say whether it took the right amount of time.
 *
 * The five unimplemented metrics exist here as report *types* only. There are
 * deliberately no throwing stubs: a function that exists and always throws
 * shows up in an editor's completions as a capability, and C9 discovering it is
 * a lie at runtime is worse than not finding it at all.
 */

import { CalibrationError } from "../errors";
import { assertComparable, type CalibrationImage } from "../image";
import {
  extractSilhouette,
  silhouetteBounds,
  silhouetteCentroid,
  type SilhouetteExtractor,
} from "../silhouette";
import { aggregate, type Aggregate } from "../stats";
import { silhouetteIoU } from "./shape";

/** The six motion metrics the methodology names. */
export const MOTION_METRICS = [
  "response-latency",
  "peak-compression",
  "overshoot",
  "settling-time",
  "redirect-continuity",
  "morph-silhouette-trajectory",
] as const;

export type MotionMetricId = (typeof MOTION_METRICS)[number];

export interface MotionMetricDescriptor {
  readonly id: MotionMetricId;
  /** Unit of the metric's headline number. */
  readonly units: string;
  /** Which child implements it. Everything but the trajectory is C9's. */
  readonly implementedBy: "C7" | "C9";
  readonly summary: string;
}

/**
 * The family, as data — so a report can say which motion metrics a cell carries
 * and why the rest are absent, without that knowledge living in a comment.
 */
export const MOTION_METRIC_DESCRIPTORS: readonly MotionMetricDescriptor[] = [
  {
    id: "response-latency",
    units: "ms",
    implementedBy: "C9",
    summary: "Input event to first rendered movement. Needs an event-to-frame timebase.",
  },
  {
    id: "peak-compression",
    units: "ratio",
    implementedBy: "C9",
    summary: "Deepest press scale relative to rest.",
  },
  {
    id: "overshoot",
    units: "ratio",
    implementedBy: "C9",
    summary: "How far past the target the release springs, relative to the travel.",
  },
  {
    id: "settling-time",
    units: "ms",
    implementedBy: "C9",
    summary: "Time from release to staying inside a band around the target.",
  },
  {
    id: "redirect-continuity",
    units: "px/ms",
    implementedBy: "C9",
    summary: "Velocity discontinuity at a mid-flight direction reversal.",
  },
  {
    id: "morph-silhouette-trajectory",
    units: "px",
    implementedBy: "C7",
    summary: "Frame-by-frame agreement of the morphing silhouette's position, size and area.",
  },
];

/** C9: input event to first rendered movement. */
export interface ResponseLatencyReport {
  readonly latencyMs: number;
  readonly firstMovingFrameIndex: number;
}

/** C9: deepest press compression, as a scale ratio against rest. */
export interface PeakCompressionReport {
  readonly peakCompressionRatio: number;
  readonly peakFrameIndex: number;
}

/** C9: release overshoot past the target, as a fraction of the travel. */
export interface OvershootReport {
  readonly overshootRatio: number;
  readonly peakFrameIndex: number;
}

/** C9: time from release until the surface stays inside its settling band. */
export interface SettlingTimeReport {
  readonly settlingTimeMs: number;
}

/** C9: velocity discontinuity through a mid-flight redirect. */
export interface RedirectContinuityReport {
  readonly velocityDiscontinuityPxPerMs: number;
  readonly redirectFrameIndex: number;
}

/** A captured animation: frames and the time each was presented at. */
export interface FrameSequence {
  readonly frames: readonly CalibrationImage[];
  /** Presentation time of each frame in milliseconds, on the capture's clock. */
  readonly frameTimesMs: readonly number[];
}

/** Where the silhouette was, frame by frame. All lengths equal the frame count. */
export interface SilhouetteTrajectory {
  readonly frameTimesMs: readonly number[];
  readonly centroidXPx: Float64Array;
  readonly centroidYPx: Float64Array;
  readonly areaPx2: Float64Array;
  readonly minXPx: Float64Array;
  readonly minYPx: Float64Array;
  readonly maxXPx: Float64Array;
  readonly maxYPx: Float64Array;
}

function assertWellFormed(sequence: FrameSequence, name: string): void {
  if (sequence.frames.length === 0) {
    throw new CalibrationError("frame-sequence-mismatch", `${name}: the sequence has no frames.`);
  }
  if (sequence.frames.length !== sequence.frameTimesMs.length) {
    throw new CalibrationError(
      "frame-sequence-mismatch",
      `${name}: ${sequence.frames.length} frame(s) but ${sequence.frameTimesMs.length} timestamp(s).`,
    );
  }
}

/**
 * Reduce a frame sequence to its silhouette trajectory.
 *
 * Three channels, because a morph moves in all of them and they fail
 * independently: the centroid catches a surface travelling along the wrong
 * path, the bounds catch it arriving at the wrong size, and the area catches a
 * corner radius or a shape family that is wrong while position and bounds are
 * both right.
 *
 * An empty silhouette on any frame is refused with the frame index. A morph
 * whose surface vanishes mid-flight is a bug worth a stack trace, and a NaN
 * centroid propagating into a trajectory summary would hide it.
 */
export function silhouetteTrajectory(
  sequence: FrameSequence,
  extractor: SilhouetteExtractor,
): SilhouetteTrajectory {
  assertWellFormed(sequence, "silhouetteTrajectory");
  const frameCount = sequence.frames.length;
  const centroidXPx = new Float64Array(frameCount);
  const centroidYPx = new Float64Array(frameCount);
  const areaPx2 = new Float64Array(frameCount);
  const minXPx = new Float64Array(frameCount);
  const minYPx = new Float64Array(frameCount);
  const maxXPx = new Float64Array(frameCount);
  const maxYPx = new Float64Array(frameCount);

  for (let i = 0; i < frameCount; i += 1) {
    const frame = sequence.frames[i];
    if (!frame) {
      throw new CalibrationError("frame-sequence-mismatch", `silhouetteTrajectory: frame ${i} is missing.`);
    }
    try {
      const silhouette = extractSilhouette(frame, extractor);
      const centroid = silhouetteCentroid(silhouette);
      const bounds = silhouetteBounds(silhouette);
      centroidXPx[i] = centroid.x;
      centroidYPx[i] = centroid.y;
      areaPx2[i] = centroid.area;
      minXPx[i] = bounds.minX;
      minYPx[i] = bounds.minY;
      maxXPx[i] = bounds.maxX;
      maxYPx[i] = bounds.maxY;
    } catch (error) {
      if (error instanceof CalibrationError && error.code === "empty-region") {
        throw new CalibrationError(
          "empty-region",
          `silhouetteTrajectory: frame ${i} has an empty silhouette — the surface is not visible there.`,
        );
      }
      throw error;
    }
  }

  return { frameTimesMs: sequence.frameTimesMs, centroidXPx, centroidYPx, areaPx2, minXPx, minYPx, maxXPx, maxYPx };
}

/** How two silhouette trajectories agree, frame by frame. */
export interface MorphSilhouetteTrajectoryReport {
  readonly frameCount: number;
  /**
   * Worst gap between the two sequences' presentation times. Nonzero means the
   * frames are being compared across a timebase offset, and every other number
   * here should be read with that in mind.
   */
  readonly frameTimeDeltaMaxMs: number;
  /** Centroid separation per frame, in pixels. */
  readonly centroidDistancePx: Aggregate;
  /** Candidate area over reference area per frame, dimensionless. */
  readonly areaRatio: Aggregate;
  /** Worst of the four bounding-box edge offsets per frame, in pixels. */
  readonly boundsDeltaPx: Aggregate;
  /** Per-frame silhouette IoU, 0..1. */
  readonly silhouetteIoU: Aggregate;
}

/**
 * Compare two captured morphs, frame for frame.
 *
 * Frames are paired by *index*, not by timestamp, and the worst timestamp gap
 * is reported alongside. Pairing by index is the only honest choice without a
 * shared clock: resampling one sequence onto the other's timebase would
 * interpolate silhouettes, and an interpolated silhouette is not something
 * either renderer ever drew. Getting the two capture paths onto a common
 * timebase is part of what C9 owns; until then `frameTimeDeltaMaxMs` says how
 * much to trust the pairing.
 */
export function morphSilhouetteTrajectory(
  reference: FrameSequence,
  candidate: FrameSequence,
  extractor: SilhouetteExtractor,
): MorphSilhouetteTrajectoryReport {
  assertWellFormed(reference, "morphSilhouetteTrajectory(reference)");
  assertWellFormed(candidate, "morphSilhouetteTrajectory(candidate)");
  if (reference.frames.length !== candidate.frames.length) {
    throw new CalibrationError(
      "frame-sequence-mismatch",
      `morphSilhouetteTrajectory: ${reference.frames.length} reference frame(s) against ` +
        `${candidate.frames.length} candidate frame(s). Capture both sides at the same frame count, ` +
        `or resample before measuring — this metric will not interpolate silhouettes.`,
    );
  }

  const frameCount = reference.frames.length;
  const centroidDistance = new Float64Array(frameCount);
  const areaRatio = new Float64Array(frameCount);
  const boundsDelta = new Float64Array(frameCount);
  const iou = new Float64Array(frameCount);
  let frameTimeDeltaMax = 0;

  for (let i = 0; i < frameCount; i += 1) {
    const referenceFrame = reference.frames[i];
    const candidateFrame = candidate.frames[i];
    if (!referenceFrame || !candidateFrame) {
      throw new CalibrationError("frame-sequence-mismatch", `morphSilhouetteTrajectory: frame ${i} is missing.`);
    }
    assertComparable(referenceFrame, candidateFrame, `morphSilhouetteTrajectory(frame ${i})`);

    const referenceSilhouette = extractSilhouette(referenceFrame, extractor);
    const candidateSilhouette = extractSilhouette(candidateFrame, extractor);
    const referenceCentroid = silhouetteCentroid(referenceSilhouette);
    const candidateCentroid = silhouetteCentroid(candidateSilhouette);
    const referenceBounds = silhouetteBounds(referenceSilhouette);
    const candidateBounds = silhouetteBounds(candidateSilhouette);

    centroidDistance[i] = Math.hypot(
      candidateCentroid.x - referenceCentroid.x,
      candidateCentroid.y - referenceCentroid.y,
    );
    areaRatio[i] = candidateCentroid.area / referenceCentroid.area;
    boundsDelta[i] = Math.max(
      Math.abs(candidateBounds.minX - referenceBounds.minX),
      Math.abs(candidateBounds.minY - referenceBounds.minY),
      Math.abs(candidateBounds.maxX - referenceBounds.maxX),
      Math.abs(candidateBounds.maxY - referenceBounds.maxY),
    );
    iou[i] = silhouetteIoU(referenceSilhouette, candidateSilhouette);
    frameTimeDeltaMax = Math.max(
      frameTimeDeltaMax,
      Math.abs((candidate.frameTimesMs[i] ?? 0) - (reference.frameTimesMs[i] ?? 0)),
    );
  }

  return {
    frameCount,
    frameTimeDeltaMaxMs: frameTimeDeltaMax,
    centroidDistancePx: aggregate(centroidDistance, "morphSilhouetteTrajectory(centroid)"),
    areaRatio: aggregate(areaRatio, "morphSilhouetteTrajectory(area)"),
    boundsDeltaPx: aggregate(boundsDelta, "morphSilhouetteTrajectory(bounds)"),
    silhouetteIoU: aggregate(iou, "morphSilhouetteTrajectory(iou)"),
  };
}
