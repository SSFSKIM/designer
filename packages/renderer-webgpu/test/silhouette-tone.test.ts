import { packToneShapes, toneReadingsFromBuffer } from "../src/silhouette-tone";
import { resolveSurfaces } from "../src/instances";
import { describe, expect, it } from "vitest";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch } from "../src/material";

describe("silhouette abscissa profile selection", () => {
  it("does not add a default property or change the empty patch's serialization", () => {
    expect(Object.hasOwn(DEFAULT_MATERIAL_PROFILE, "backdropToneAbscissa")).toBe(false);
    expect(Object.hasOwn(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {}), "backdropToneAbscissa")).toBe(false);
    expect(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {})).toEqual(DEFAULT_MATERIAL_PROFILE);
  });
  it("retains an opt-in through subsequent patches and can return to the source", () => {
    const local = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
      backdropToneAbscissa: { kind: "silhouette" },
    });
    expect(local.backdropToneAbscissa).toEqual({ kind: "silhouette" });
    expect(withMaterialOverrides(local, {}).backdropToneAbscissa).toEqual({ kind: "silhouette" });
    expect(withMaterialOverrides(local, { backdropToneAbscissa: "source" }).backdropToneAbscissa)
      .toBe("source");
  });
  it.each([null, "local", {}, { kind: "source" }, { kind: "silhouette", radius: 4 }, 0])(
    "rejects unsupported abscissa documents (%j) rather than silently drawing source", (value) => {
      expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
        backdropToneAbscissa: value,
      } as unknown as MaterialProfilePatch)).toThrow(/backdropToneAbscissa/);
    },
  );
});


describe("per-surface reduction boundary", () => {
  it("packs resolved device bounds rather than the shadow-padded group or another host", () => {
    const surfaces = resolveSurfaces({
      groupId: "g", refraction: "none", analysisExact: false,
      surfaces: [
        { nodeId: "rect", family: "fixed-rounded-rect", reference: "figma-smoothing",
          shape: { center: [20, 30], size: [12, 8], radii: [2, 2, 2, 2],
            smoothing: 0, thickness: 8 } },
        { nodeId: "capsule", family: "capsule",
          shape: { center: [70, 20], size: [40, 20], radii: [10, 10, 10, 10],
            smoothing: 0, thickness: 8 } },
      ],
    }, "rsupn");
    expect(Array.from(packToneShapes(surfaces, 2))).toEqual([
      28, 52, 24, 16, 4, 0, 0, 0,
      100, 20, 80, 40, 20, 0, 0, 0,
    ]);
  });

  it("keeps encoded input, linear colour and each host identity separate on readback", () => {
    const readings = toneReadingsFromBuffer(new Float32Array([
      0.5, 0.5, 0.5, 0.21404114, 0.5, 0.5, 100, 100,
      1, 0, 0, 0.03716728, 0.2126, 0.2126, 40, 40,
    ]), ["striped", "red"].map((surfaceId) => ({
      surfaceId, sourceWidth: 512, sourceHeight: 256, sampledWidth: 256, sampledHeight: 128,
    })));
    expect(readings.map((reading) => reading.surfaceId)).toEqual(["striped", "red"]);
    expect(readings[0]!.luminance).toBeCloseTo(0.21404114);
    expect(readings[0]!.encodedLuminance).toBe(0.5);
    expect(readings[1]!.color).toEqual([1, 0, 0]);
    expect(readings[1]!.encodedLuminance).toBeCloseTo(0.2126);
    expect(readings.map((reading) => reading.sampleCount)).toEqual([100, 40]);
    expect(readings[0]).toMatchObject({ level: 0, sourceWidth: 512, sampledWidth: 256 });
  });
});
