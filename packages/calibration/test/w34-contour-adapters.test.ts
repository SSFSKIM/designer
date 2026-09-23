import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
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
  it("compare skips native controls before material-free validation or browser launch", () => {
    const root = mkdtempSync(join(tmpdir(), "w34-native-only-"));
    try {
      const spec = { canvas, components: { none: { kind: "none" } },
        scenes: [{ id: "control", background: "grey", component: "none", state: "rest" }],
        split: { calibration: [], validation: [], holdout: [], recorded: [], probe: ["control"] } };
      writeFileSync(join(root, "scenes.json"), JSON.stringify(spec));
      writeFileSync(join(root, "manifest.json"), JSON.stringify({ backgrounds: {}, profiles: [{
        profileKey: "apple-macos-27.0-2x-light-standard-glass0.5", colorScheme: "light",
        fixtures: [{ sceneId: "control", file: "must-not-open.png", fixtureSet: "probe",
          captureMethod: "screencapturekit", materialRendered: false }],
      }] }));
      const out = join(root, "matrix.json");
      const child = spawnSync(process.execPath, ["--import", "tsx", "cli/compare.ts",
        "--set", "probe", "--scene", "control", "--out-matrix", out], {
        cwd: resolve(import.meta.dirname, ".."), encoding: "utf8",
        env: { ...process.env, VITREA_SCENES: join(root, "scenes.json"),
          VITREA_FIXTURES: root, VITREA_WEB_CAPTURES: join(root, "web") },
      });
      expect(child.status).toBe(1);
      expect(child.stderr).toContain("filters selected no cells");
      expect(child.stderr).not.toContain("marked materialRendered: false");
      expect(existsSync(out)).toBe(false);
      expect(existsSync(join(root, "web"))).toBe(false);
    } finally { rmSync(root, { recursive: true, force: true }); }
  });
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
