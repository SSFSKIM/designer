/** Benchmark source/geometry contracts, without requesting a GPU or drawing a frame. */
import { afterAll, beforeAll, describe, expect, it, vi } from "vitest";
import type { benchScene as sceneFactory } from "../e2e/fixtures/harness";
import { resolveSurfaces } from "../src/instances";

let benchScene: typeof sceneFactory;
beforeAll(async () => {
  // The harness installs its browser entry point at import. These are its only
  // import-time DOM effects; the scene builder itself is plain data.
  vi.stubGlobal("window", {});
  vi.stubGlobal("document", { documentElement: { setAttribute() {} } });
  ({ benchScene } = await import("../e2e/fixtures/harness"));
});
afterAll(() => vi.unstubAllGlobals());

describe("benchmark scene coverage", () => {
  it("keeps the original eight-surface live scene when geometry is absent", () => {
    const scene = benchScene({ widthCss: 390, heightCss: 844, devicePixelRatio: 3 });
    expect(scene.backdrop).toEqual({ kind: "checkerboard", cell: 12, live: true });
    expect(scene.groups.map(g => g.surfaces.map(s => s.shape.size))).toEqual([
      Array.from({ length: 4 }, () => [65, 44]),
      Array.from({ length: 3 }, () => [78, 40]),
      [[234, 96]],
    ]);
    const morph = scene.groups.find(g => g.groupId === "morph")!;
    expect(resolveSurfaces(morph, "rsupn")[0]?.spanPx).toBeCloseTo(95.496, 12);
  });

  it.each([
    { widthCss: 390, heightCss: 844, devicePixelRatio: 3 },
    { widthCss: 1440, heightCss: 900, devicePixelRatio: 2 },
  ])("prices thick span 160 beside thin controls at $widthCss CSS px", view => {
    const config = { ...view, morphSpanCss: 160, morphPress: 0, backdropSize: 2048 };
    const scene = benchScene(config);
    expect(scene.backdrop).toEqual({ kind: "checkerboard", cell: 12, size: 2048, live: true });
    const shapes = scene.groups.flatMap(g => g.surfaces.map(s => s.shape));
    const spans = shapes.map(s => Math.min(...s.size));
    expect(spans).toEqual([44, 44, 44, 44, 40, 40, 40, 160]);
    const morph = scene.groups.find(g => g.groupId === "morph")!;
    // Span authority comes from the resolved shape, after press compression.
    expect(resolveSurfaces(morph, "rsupn")[0]?.spanPx).toBe(160);
    // An extra tap confined to thick pixels must be priced on substantial
    // coverage, not just allocated while every shaded pixel takes the old path.
    const area = (size: readonly number[]) => size[0]! * size[1]!;
    const thickArea = shapes.filter(s => Math.min(...s.size) === 160)
      .reduce((sum, s) => sum + area(s.size), 0);
    const totalArea = shapes.reduce((sum, s) => sum + area(s.size), 0);
    expect(thickArea / totalArea).toBeGreaterThan(0.6);
    for (const shape of shapes) {
      expect(shape.center[0] - shape.size[0] / 2).toBeGreaterThanOrEqual(0);
      expect(shape.center[0] + shape.size[0] / 2).toBeLessThanOrEqual(view.widthCss);
      expect(shape.center[1] - shape.size[1] / 2).toBeGreaterThanOrEqual(0);
      expect(shape.center[1] + shape.size[1] / 2).toBeLessThanOrEqual(view.heightCss);
    }
  });
});
