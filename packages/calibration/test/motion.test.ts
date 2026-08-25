import { describe, expect, it } from "vitest";

import type { CalibrationError } from "../src/errors";
import {
  MOTION_METRICS,
  MOTION_METRIC_DESCRIPTORS,
  morphSilhouetteTrajectory,
  silhouetteTrajectory,
  type FrameSequence,
} from "../src/metrics/motion";
import type { SilhouetteExtractor } from "../src/silhouette";
import { alphaMaskImage, discPredicate } from "./synthesise";

const alpha: SilhouetteExtractor = { kind: "alpha", threshold: 0.5 };

/** A disc travelling in x and growing, one frame every 16ms. */
function morph(offsetX = 0, frames = 6): FrameSequence {
  return {
    frames: Array.from({ length: frames }, (_, i) =>
      alphaMaskImage(160, 80, discPredicate(40 + 4 * i + offsetX, 40, 12 + i)),
    ),
    frameTimesMs: Array.from({ length: frames }, (_, i) => i * 16),
  };
}

describe("the motion family", () => {
  it("declares all six metrics and attributes five of them to C9", () => {
    expect(MOTION_METRICS).toHaveLength(6);
    expect(MOTION_METRIC_DESCRIPTORS.map((descriptor) => descriptor.id)).toEqual([...MOTION_METRICS]);

    const mine = MOTION_METRIC_DESCRIPTORS.filter((descriptor) => descriptor.implementedBy === "C7");
    expect(mine.map((descriptor) => descriptor.id)).toEqual(["morph-silhouette-trajectory"]);
    expect(MOTION_METRIC_DESCRIPTORS.filter((descriptor) => descriptor.implementedBy === "C9")).toHaveLength(5);
  });
});

describe("silhouetteTrajectory", () => {
  it("tracks the centroid, bounds and area it was built with", () => {
    const trajectory = silhouetteTrajectory(morph(), alpha);
    for (let i = 0; i < 6; i += 1) {
      const radius = 12 + i;
      expect(trajectory.centroidXPx[i]).toBeCloseTo(40 + 4 * i, 6);
      expect(trajectory.centroidYPx[i]).toBeCloseTo(40, 6);
      expect(trajectory.minXPx[i]).toBe(40 + 4 * i - radius);
      expect(trajectory.maxXPx[i]).toBe(40 + 4 * i + radius);
      // A rasterised disc's area approaches πr² from below.
      expect(trajectory.areaPx2[i]).toBeGreaterThan(Math.PI * radius * radius * 0.95);
      expect(trajectory.areaPx2[i]).toBeLessThan(Math.PI * radius * radius * 1.05);
    }
  });

  it("names the frame when the surface is not visible in it", () => {
    const sequence: FrameSequence = {
      frames: [alphaMaskImage(40, 40, discPredicate(20, 20, 8)), alphaMaskImage(40, 40, () => false)],
      frameTimesMs: [0, 16],
    };
    let caught: unknown;
    try {
      silhouetteTrajectory(sequence, alpha);
    } catch (error) {
      caught = error;
    }
    expect((caught as CalibrationError).code).toBe("empty-region");
    expect((caught as CalibrationError).message).toMatch(/frame 1/);
  });

  it("refuses a sequence whose timestamps do not match its frames", () => {
    const sequence: FrameSequence = {
      frames: [alphaMaskImage(40, 40, discPredicate(20, 20, 8))],
      frameTimesMs: [0, 16],
    };
    expect(() => silhouetteTrajectory(sequence, alpha)).toThrowError(/1 frame\(s\) but 2 timestamp\(s\)/);
  });
});

describe("morphSilhouetteTrajectory", () => {
  it("is a perfect match against itself", () => {
    const report = morphSilhouetteTrajectory(morph(), morph(), alpha);
    expect(report.frameCount).toBe(6);
    expect(report.centroidDistancePx.max).toBe(0);
    expect(report.boundsDeltaPx.max).toBe(0);
    expect(report.areaRatio.min).toBe(1);
    expect(report.areaRatio.max).toBe(1);
    expect(report.silhouetteIoU.min).toBe(1);
    expect(report.frameTimeDeltaMaxMs).toBe(0);
  });

  it("recovers a known constant translation on every frame", () => {
    const report = morphSilhouetteTrajectory(morph(), morph(3), alpha);
    expect(report.centroidDistancePx.min).toBeCloseTo(3, 6);
    expect(report.centroidDistancePx.max).toBeCloseTo(3, 6);
    expect(report.boundsDeltaPx.max).toBe(3);
    // A pure translation preserves area exactly on this raster.
    expect(report.areaRatio.min).toBeCloseTo(1, 6);
    expect(report.silhouetteIoU.max).toBeLessThan(1);
  });

  it("reports the timebase gap rather than resampling across it", () => {
    const reference = morph();
    const shifted: FrameSequence = {
      frames: reference.frames,
      frameTimesMs: reference.frameTimesMs.map((time) => time + 7),
    };
    expect(morphSilhouetteTrajectory(reference, shifted, alpha).frameTimeDeltaMaxMs).toBe(7);
  });

  it("refuses two sequences of different length instead of interpolating", () => {
    let caught: unknown;
    try {
      morphSilhouetteTrajectory(morph(0, 6), morph(0, 5), alpha);
    } catch (error) {
      caught = error;
    }
    expect((caught as CalibrationError).code).toBe("frame-sequence-mismatch");
    expect((caught as CalibrationError).message).toMatch(/will not interpolate silhouettes/);
  });

  it("refuses two sequences whose frames are different sizes", () => {
    const wide: FrameSequence = {
      frames: [alphaMaskImage(200, 80, discPredicate(40, 40, 12))],
      frameTimesMs: [0],
    };
    const narrow: FrameSequence = {
      frames: [alphaMaskImage(160, 80, discPredicate(40, 40, 12))],
      frameTimesMs: [0],
    };
    expect(() => morphSilhouetteTrajectory(wide, narrow, alpha)).toThrowError(/frame 0/);
  });
});
