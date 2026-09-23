import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { isNativeOnly, type DeclaredComponent } from "../src/component-region";

const root = resolve(import.meta.dirname, "../../..");
const evidence = join(root, "packages/calibration/results/2026-09-23-w34-g0-contour-bed");
const scenesFile = join(root, "apps/reference-apple/scenes-w34-contour.json");
const sha = (path: string): string => createHash("sha256").update(readFileSync(path)).digest("hex");
interface Scene { id: string; background: string; component: string; state: string }
interface Spec {
  version: number;
  canvas: { width: number; height: number };
  scenes: Scene[];
  components: Record<string, DeclaredComponent>;
  backgrounds: Record<string, unknown>;
  profiles: { key: string; colorScheme: string; a11y: string; scenes: string[] }[];
  split: Record<string, string[]>;
}
const spec = JSON.parse(readFileSync(scenesFile, "utf8")) as Spec;
const split = JSON.parse(readFileSync(join(evidence, "split.json"), "utf8")) as Record<string, string[]>;
const clean = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(clean);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).filter(([key]) => !key.startsWith("$"))
      .map(([key, v]) => [key, clean(v)]));
  }
  return value;
};
const signature = (matrix: Spec, scene: Scene): string => JSON.stringify({
  component: clean(matrix.components[scene.component]), background: clean(matrix.backgrounds[scene.background]),
});

function python(script: string): void {
  const result = spawnSync("python3", [join(evidence, script)], { encoding: "utf8" });
  expect(result.stderr, result.stdout).not.toContain("FAILED");
  expect(result.status, result.stderr).toBe(0);
}

describe("W34's declared probe bed and identification boundary", () => {
  it("pins both independent declarations and covers every scene once", () => {
    expect(sha(scenesFile)).toBe("a1ba37513bac2d42c612c9fe08f9c3d711ef59d5539735479aff8e9be520d7c6");
    expect(sha(join(evidence, "split.json"))).toBe("6a75043191b471da5344312aa21a55c89191746f6b449f5078b15d4837a29c73");
    const assigned = ["calibration", "validation", "holdout"].flatMap((role) => split[role] ?? []);
    expect(assigned.length).toBe(new Set(assigned).size);
    expect([...assigned].sort()).toEqual(spec.scenes.map((s) => s.id).sort());
    expect([...spec.split["probe"]!].sort()).toEqual([...assigned].sort());
    for (const role of ["calibration", "validation", "holdout"]) expect(spec.split[role]).toEqual([]);
  });
  it("declares four standard profiles and prices the full sparse pass without dropping controls", () => {
    expect(spec.version).toBe(1);
    expect(spec.canvas).toEqual({ width: 320, height: 200 });
    expect(spec.profiles.map((p) => p.key).sort()).toEqual([1, 2].flatMap((scale) =>
      ["dark", "light"].map((scheme) => `apple-macos-27.0-${scale}x-${scheme}-standard-glass0.5`)).sort());
    for (const p of spec.profiles) expect(p.a11y).toBe("standard");
    for (const scale of [1, 2]) for (const pose of ["rest", "inactive"]) {
      const ids = new Set(spec.scenes.filter((s) => s.state === pose).map((s) => s.id));
      const cells = spec.profiles.filter((p) => p.key.includes(`-${scale}x-`))
        .flatMap((p) => p.scenes.filter((s) => ids.has(s)));
      expect(cells).toHaveLength(148);
    }
  });
  it("keeps every canonical geometry/backdrop holdout twin out of fitting even across tint or pose", () => {
    const canonical = JSON.parse(readFileSync(join(root, "apps/reference-apple/scenes.json"), "utf8")) as Spec;
    const held = new Set(canonical.split["holdout"]);
    const signatures = new Set(canonical.scenes.filter((s) => held.has(s.id)).map((s) => signature(canonical, s)));
    const fit = new Set([...(split["calibration"] ?? []), ...(split["validation"] ?? [])]);
    const twins = spec.scenes.filter((s) => !isNativeOnly(spec.components[s.component]!) && signatures.has(signature(spec, s)));
    expect(twins.map((s) => s.id).sort()).toEqual([
      "dark-solid__capsule-button__inactive", "dark-solid__capsule-button__rest",
    ]);
    expect(twins.filter((s) => fit.has(s.id))).toEqual([]);
  });
  it("executes negative PNG crop statistics hash membership publication and receipt tests", () => python("test-wave.py"));
  it("executes the sitting's state drift pose and missing-cell refusals", () => python("test-sitting.py"));
  it("refuses protected aliases case variants and failed signing before advertising a build", () => python("test-build-guard.py"));
});

const numeric = spawnSync("python3.12", ["-c", "import numpy, PIL"], { encoding: "utf8" }).status === 0;
it.skipIf(!numeric)("replays numerical geometry absolute residual and forward-model laws", () => {
  const result = spawnSync("python3.12", [join(evidence, "test-instrument.py")], { encoding: "utf8" });
  expect(result.status, result.stderr).toBe(0);
});
const harness = join(homedir(), "vitrea-w34/side/harness");
it.skipIf(process.platform !== "darwin" || !existsSync(harness))("decodes new native kinds on the pinned side binary without capture", () => {
  const result = spawnSync(harness, ["self-check"], { encoding: "utf8", env: {
    ...process.env, VITREA_SCENES: scenesFile, VITREA_FIXTURES: tmpdir(),
  } });
  expect(result.status, result.stderr).toBe(0);
  expect(result.stdout).toContain("all rows hold.");
  expect(result.stdout).not.toContain("FAIL");
});
