import { describe, expect, it, vi } from "vitest";
import { componentRegion, placeComponent, type DeclaredComponent } from "../src/component-region";
import { resolveShape } from "../../geometry/src/index";

vi.mock("../../../apps/reference-apple/scenes.json", () => ({ default: {
  canvas: { width: 320, height: 200 }, tints: {},
  components: {
    circular: { kind: "capsule-circular", size: [120, 44], offset: [0.125, 0.375] },
    empty: { kind: "none" },
    opaque: { kind: "capsule-circular", size: [120, 44], opaque: true, fillSRGB: [0, 0, 0] },
  },
  scenes: ["circular", "empty", "opaque"].map((id) => ({
    id, component: id, background: "grey", state: "rest",
  })),
} }));
import { resolveScene, SCENE_IDS } from "../web/scenes";

const canvas = { width: 320, height: 200 };
describe("W34 native controls and circular counterpart", () => {
  it("preserves device-subpixel offsets on a circular stadium", () => {
    const placed = placeComponent({ kind: "capsule-circular", size: [120, 44],
      offset: [0.125, 0.375] }, canvas);
    expect(placed[0]).toMatchObject({ left: 100.125, top: 78.375, radius: 22 });
    const surface = resolveScene("circular").surfaces[0]!;
    expect(surface.family).toBe("capsule");
    const geometry = resolveShape({ family: "capsule", center: [160, 100],
      size: [surface.width, surface.height] });
    expect(geometry.channels.smoothing).toBe(0);
    expect(geometry.corner.radius).toBe(22);
  });
  it("skips native-only controls rather than inventing a glass or shape metric", () => {
    expect(SCENE_IDS).toEqual(["circular"]);
    for (const id of ["empty", "opaque"]) expect(() => resolveScene(id)).toThrow(/native-only/);
    for (const component of [
      { kind: "none" }, { kind: "capsule-circular", size: [120, 44], opaque: true },
    ] as DeclaredComponent[]) {
      expect(placeComponent(component, canvas)).toEqual([]);
      expect(() => componentRegion(component, { canvas, scale: 1, width: 320, height: 200 }))
        .toThrow(/native-only/);
    }
  });
});
