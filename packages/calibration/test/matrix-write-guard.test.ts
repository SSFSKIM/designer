/** G0 protects immutable canonical rows before either CLI captures or measures. */
import { spawnSync } from "node:child_process";
import { copyFileSync, cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

import { assertScratchDestination } from "../src/matrix-write-guard";

const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
const REFERENCE = resolve(PACKAGE_ROOT, "..", "..", "apps", "reference-apple");
const MATRIX = resolve(PACKAGE_ROOT, "results/matrix.json");
const GENERATIONS = resolve(PACKAGE_ROOT, "results/generations");
const PROFILE = "apple-macos-26.5-1x-light-standard";
const SCENE = "light-solid__rrect-md__rest";
const FIXTURE = resolve(REFERENCE, "fixtures", PROFILE, `${SCENE}.png`);
const scratch = mkdtempSync(join(tmpdir(), "w40-write-guard-"));
const mirrorRoot = join(scratch, "repo");
const mirrorPackage = join(mirrorRoot, "packages/calibration");
const mirrorMatrix = join(mirrorPackage, "results/matrix.json");
const mirrorGenerations = join(mirrorPackage, "results/generations");
let canonicalBefore: Buffer;
beforeAll(() => {
  // Run the actual CLIs from copied sources, never against the repository's
  // canonical evidence. A missed guard can damage only this disposable mirror.
  canonicalBefore = readFileSync(MATRIX);
  mkdirSync(join(mirrorRoot, "apps/reference-apple"), { recursive: true });
  mkdirSync(mirrorGenerations, { recursive: true });
  cpSync(join(PACKAGE_ROOT, "src"), join(mirrorPackage, "src"), { recursive: true });
  cpSync(join(PACKAGE_ROOT, "cli"), join(mirrorPackage, "cli"), { recursive: true });
  copyFileSync(join(PACKAGE_ROOT, "package.json"), join(mirrorPackage, "package.json"));
  symlinkSync(join(PACKAGE_ROOT, "node_modules"), join(mirrorPackage, "node_modules"), "dir");
  symlinkSync(join(REFERENCE, "scenes.json"),
    join(mirrorRoot, "apps/reference-apple/scenes.json"));
  writeFileSync(mirrorMatrix, '{"schemaVersion":5,"cells":[]}\n');
  writeFileSync(join(mirrorGenerations, "85ad7f7e3e0d.json"),
    '{"schemaVersion":5,"cells":[]}\n');
  symlinkSync(mirrorMatrix, join(scratch, "mirror-matrix-alias.json"));
  symlinkSync(join(mirrorPackage, "results"), join(scratch, "mirror-results-alias"), "dir");
  symlinkSync(MATRIX, join(scratch, "frozen-alias.json"));
  symlinkSync(resolve(PACKAGE_ROOT, "results"), join(scratch, "results-alias"), "dir");
});
afterAll(() => {
  expect(readFileSync(MATRIX).equals(canonicalBefore)).toBe(true);
  rmSync(scratch, { recursive: true, force: true });
});

function run(cli: "compare" | "diff", flags: readonly string[], env = process.env) {
  return spawnSync(process.execPath, ["--import", "tsx", `cli/${cli}.ts`, ...flags], {
    cwd: mirrorPackage, encoding: "utf8", env,
  });
}

const diffArgs = [
  "--native", FIXTURE, "--web", FIXTURE, "--profile", PROFILE,
  "--scene", SCENE, "--web-cell", join(scratch, "cell.json"),
];
writeFileSync(join(scratch, "cell.json"), JSON.stringify({
  engine: "chromium", engineVersion: "151.0.0.0", renderer: "webgpu",
  samplingBackend: "gpu-texture", gpuAdapter: "apple/metal-3", colorSpace: "srgb",
  capturePath: "test scratch capture", sceneId: SCENE, pixelSize: [320, 200],
  deterministic: true, repeatNoise: 0,
}));

function compareArgs(out?: string): string[] {
  return ["--profile", PROFILE, "--scene", SCENE, "--set", "calibration", "--skip-capture",
    ...(out === undefined ? [] : ["--out-matrix", out])];
}

describe("G0 immutable destinations", () => {
  it("refuses frozen and generation JSON even when addressed by symlink or uncreated filename", () => {
    expect(() => assertScratchDestination(MATRIX)).toThrow(/G1.*publish/i);
    expect(() => assertScratchDestination(join(GENERATIONS, "new-sha.json"))).toThrow(/G1.*publish/i);
    expect(() => assertScratchDestination(join(GENERATIONS, "index.json"))).toThrow(/G1.*publish/i);
    expect(() => assertScratchDestination(resolve(PACKAGE_ROOT, "results/superseded/index.json")))
      .toThrow(/G1.*publish/i);
    expect(() => assertScratchDestination(join(scratch, "frozen-alias.json"))).toThrow(/G1.*publish/i);
    expect(() => assertScratchDestination(join(scratch, "results-alias", "generations", "new.json")))
      .toThrow(/G1.*publish/i);
    expect(() => assertScratchDestination(join(scratch, "subdir", "result.json"))).not.toThrow();
  });

  it("compare refuses its default and explicitly named canonical destinations before capturing", () => {
    for (const args of [compareArgs(), compareArgs(mirrorMatrix),
      compareArgs(join(mirrorGenerations, "85ad7f7e3e0d.json")),
      compareArgs(join(scratch, "mirror-matrix-alias.json"))]) {
      const before = readFileSync(mirrorMatrix);
      const child = run("compare", args);
      expect(child.status).toBe(1);
      expect(child.stderr).toMatch(/G1.*publish/i);
      expect(child.stderr).not.toContain("── measure");
      expect(readFileSync(mirrorMatrix).equals(before)).toBe(true);
    }
  });

  it("diff refuses canonical matrix and report destinations before measurement", () => {
    for (const dest of [mirrorMatrix, join(mirrorGenerations, "85ad7f7e3e0d.json"),
      join(scratch, "mirror-results-alias", "generations", "new.json")]) {
      const before = readFileSync(mirrorMatrix);
      const child = run("diff", [...diffArgs, "--matrix", dest]);
      expect(child.status).not.toBe(0);
      expect(child.stderr).toMatch(/G1.*publish/i);
      expect(child.stderr).not.toContain("report →");
      expect(readFileSync(mirrorMatrix).equals(before)).toBe(true);
    }
    for (const dest of [mirrorMatrix, join(mirrorGenerations, "new.json")]) {
      const before = readFileSync(mirrorMatrix);
      const report = run("diff", [...diffArgs, "--out", dest]);
      expect(report.status).not.toBe(0);
      expect(report.stderr).toMatch(/G1.*publish/i);
      expect(readFileSync(mirrorMatrix).equals(before)).toBe(true);
    }
    const report = run("diff", diffArgs);
    expect(report.status).toBe(0);
    expect(JSON.parse(report.stdout)).toHaveProperty("key.sceneId", SCENE);
  });

  it("both CLIs write an ordinary scratch matrix and leave the canonical file unchanged", () => {
    const diffOutput = join(scratch, "diff", "matrix.json");
    const diff = run("diff", [...diffArgs, "--matrix", diffOutput]);
    expect(diff.status, diff.stderr).toBe(0);
    expect(JSON.parse(readFileSync(diffOutput, "utf8"))).toMatchObject({
      schemaVersion: 5, cells: [{ key: { sceneId: SCENE } }],
    });

    const captureDir = join(scratch, "captures", PROFILE, SCENE);
    mkdirSync(captureDir, { recursive: true });
    copyFileSync(FIXTURE, join(captureDir, `${SCENE}__webgpu.png`));
    copyFileSync(join(scratch, "cell.json"), join(captureDir, "cell__webgpu.json"));
    const compareOutput = join(scratch, "compare", "matrix.json");
    const compare = run("compare", compareArgs(compareOutput), {
      ...process.env, VITREA_FIXTURES: resolve(REFERENCE, "fixtures"),
      VITREA_WEB_CAPTURES: join(scratch, "captures"),
    });
    expect(compare.status, `${compare.stderr}\n${compare.stdout}`).toBe(0);
    expect(JSON.parse(readFileSync(compareOutput, "utf8"))).toMatchObject({
      schemaVersion: 5, cells: [{ key: { sceneId: SCENE } }],
    });
    expect(readFileSync(mirrorMatrix, "utf8")).toBe('{"schemaVersion":5,"cells":[]}\n');
  });
});
