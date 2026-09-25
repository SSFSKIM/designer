import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

const root = resolve(import.meta.dirname, "../../..");
const evidence = join(root, "packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed");
interface Shape {
  kind: string; size?: number[]; position?: number[]; offset?: number[];
  opaque?: boolean; fillSRGB?: number[]; items?: Shape[];
}
interface Scene {
  id: string; component: string; background: string; state: string;
  $class: string; $scale?: number; $pair?: string; $phaseAxis?: string; $bridge?: boolean;
}
interface Spec {
  canvas: { width: number; height: number }; components: Record<string, Shape>;
  backgrounds: Record<string, { srgb?: number[] }>; scenes: Scene[];
  profiles: { key: string; scenes: string[] }[]; split: Record<string, string[]>;
}
const load = (file: string): Spec => JSON.parse(readFileSync(file, "utf8")) as Spec;
const specPath = join(root, "apps/reference-apple/scenes-w39-colour-edge.json");
const preflightPath = join(root, "apps/reference-apple/scenes-w39-preflight.json");
const sha = (path: string): string => createHash("sha256").update(readFileSync(path)).digest("hex");

describe("W39 colour/edge capture declaration", () => {
  it("retains every control and reference at both schemes/scales without canonical roles", () => {
    const spec = load(specPath);
    expect(spec.canvas).toEqual({ width: 320, height: 280 });
    expect(spec.profiles).toHaveLength(4);
    expect(spec.split.probe?.slice().sort()).toEqual(spec.scenes.map((s) => s.id).sort());
    for (const role of ["calibration", "validation", "holdout"]) expect(spec.split[role]).toEqual([]);
    for (const profile of spec.profiles) for (const state of ["rest", "inactive"]) {
      const cells = spec.scenes.filter((s) => s.state === state && profile.scenes.includes(s.id));
      expect(cells.filter((s) => s.$class === "edge")).toHaveLength(40);
      expect(cells.filter((s) => s.$class === "colour")).toHaveLength(63);
      expect(cells.filter((s) => s.$class === "colour-reference")).toHaveLength(63);
      expect(cells.filter((s) => s.$class === "phase")).toHaveLength(14);
      for (const s of cells.filter((s) => s.$class === "colour" && !s.$bridge)) {
        const rgb = spec.backgrounds[s.background]?.srgb;
        expect(rgb).toHaveLength(3);
        expect(rgb?.every((v) => v >= 40 && v <= 150)).toBe(true);
      }
    }
  });
  it("keeps the pair's role and enforces dependency direction before pixels", () => {
    const spec = load(specPath);
    const split = JSON.parse(readFileSync(join(evidence, "split.json"), "utf8")) as {
      calibration: string[]; validation: string[]; holdout: string[];
      dependencies: Record<string, { noGlass: string; opaque: string }>;
    };
    const roles = [split.calibration, split.validation, split.holdout];
    const assigned = roles.flat();
    expect(new Set(assigned).size).toBe(assigned.length);
    expect(assigned.slice().sort()).toEqual(spec.scenes.map((s) => s.id).sort());
    const role = (id: string): number => roles.findIndex((r) => r.includes(id));
    for (const s of spec.scenes) {
      if (s.$pair) expect(role(s.id)).toBe(role(s.$pair));
      const shape = spec.components[s.component]!;
      if (shape.kind === "none" || shape.opaque || shape.items?.some((v) => v.opaque)) continue;
      const dep = split.dependencies[s.id]!;
      expect(dep).toBeDefined();
      for (const id of [dep.noGlass, dep.opaque]) {
        expect(role(id)).toBeGreaterThanOrEqual(0);
        expect(role(id)).toBeLessThanOrEqual(role(s.id));
        for (const p of spec.profiles.filter((p) => p.scenes.includes(s.id))) expect(p.scenes).toContain(id);
      }
    }
    for (const stem of ["g255-b-c44", "g255-c-circular-200x44", "g128-c-capsule-circular-160x96"]) {
      for (const state of ["rest", "inactive"]) for (const suffix of ["", "-opaque"]) {
        expect(split.holdout).toContain(`${stem}${suffix}__${state}`);
      }
    }
  });
  it("uses layout positions with scale-normalized fractional size and nine preflight geometries", () => {
    const spec = load(specPath); const preflight = load(preflightPath);
    for (const doc of [spec, preflight]) for (const shape of Object.values(doc.components)) {
      for (const item of shape.items ?? [shape]) {
        if (item.kind === "none") continue;
        expect(item.position).toHaveLength(2); expect(item.offset).toBeUndefined();
        for (const axis of [0, 1]) {
          const half = item.size![axis]! / 2; const centre = item.position![axis]!;
          expect(centre - half).toBeGreaterThanOrEqual(0);
          expect(centre + half).toBeLessThanOrEqual(axis === 0 ? 320 : 280);
        }
      }
    }
    for (const scale of [1, 2]) {
      const profile = preflight.profiles.find((p) => p.key.includes(`-${scale}x-`))!;
      expect(profile.scenes).toHaveLength(18);
      const cells = preflight.scenes.filter((s) => profile.scenes.includes(s.id));
      expect(cells.filter((s) => !preflight.components[s.component]!.opaque)).toHaveLength(9);
      for (const scene of cells.filter((s) => s.$phaseAxis === "x" || s.$phaseAxis === "y")) {
        const c = preflight.components[scene.component]!;
        expect(c.position![0]! - c.size![0]! / 2).toBe(100);
        expect(c.position![1]! - c.size![1]! / 2).toBe(118);
      }
    }
  });
  it("binds the independent split and preflight to their generated bytes", () => {
    const pins = JSON.parse(readFileSync(join(evidence, "pins.json"), "utf8")) as Record<string, string>;
    expect(sha(specPath)).toBe(pins.scenesSha256);
    expect(sha(preflightPath)).toBe(pins.preflightScenesSha256);
    expect(sha(join(evidence, "split.json"))).toBe(pins.splitSha256);
    expect(sha(join(evidence, "bounds-declaration.txt"))).toBe(pins.boundsDeclarationSha256);
  });
});
