/** G0 protects immutable canonical rows before either CLI captures or measures. */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFileSync, cpSync, existsSync, linkSync, mkdirSync, mkdtempSync, readFileSync,
  readdirSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
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
const mirrorSuperseded = join(mirrorPackage, "results/superseded");
const mirrorIndex = join(mirrorGenerations, "index.json");
const mirrorArchiveIndex = join(mirrorSuperseded, "index.json");
const canonicalFiles = [MATRIX, ...["generations", "superseded"].flatMap((directory) => {
  const path = resolve(PACKAGE_ROOT, "results", directory);
  return readdirSync(path).filter((name) => name.endsWith(".json")).map((name) => join(path, name));
})];
function canonicalDigests() {
  return canonicalFiles.map((path) => createHash("sha256").update(readFileSync(path)).digest("hex"));
}
let canonicalBefore: string[];
beforeAll(() => {
  // Run the actual CLIs from copied sources, never against the repository's
  // canonical evidence. A missed guard can damage only this disposable mirror.
  canonicalBefore = canonicalDigests();
  mkdirSync(join(mirrorRoot, "apps/reference-apple"), { recursive: true });
  mkdirSync(mirrorGenerations, { recursive: true });
  mkdirSync(mirrorSuperseded, { recursive: true });
  cpSync(join(PACKAGE_ROOT, "src"), join(mirrorPackage, "src"), { recursive: true });
  cpSync(join(PACKAGE_ROOT, "cli"), join(mirrorPackage, "cli"), { recursive: true });
  copyFileSync(join(PACKAGE_ROOT, "package.json"), join(mirrorPackage, "package.json"));
  symlinkSync(join(PACKAGE_ROOT, "node_modules"), join(mirrorPackage, "node_modules"), "dir");
  symlinkSync(join(REFERENCE, "scenes.json"),
    join(mirrorRoot, "apps/reference-apple/scenes.json"));
  writeFileSync(mirrorMatrix, '{"schemaVersion":5,"cells":[]}\n');
  writeFileSync(join(mirrorGenerations, "85ad7f7e3e0d.json"),
    '{"schemaVersion":5,"cells":[]}\n');
  writeFileSync(mirrorIndex, "{}\n");
  writeFileSync(mirrorArchiveIndex, "{}\n");
  writeFileSync(join(mirrorSuperseded, "aaaaaaaaaaaa.json"), "{}\n");
  linkSync(mirrorMatrix, join(scratch, "mirror-matrix-hardlink.json"));
  linkSync(join(mirrorGenerations, "85ad7f7e3e0d.json"),
    join(scratch, "mirror-generation-hardlink.json"));
  linkSync(mirrorIndex, join(scratch, "mirror-index-hardlink.json"));
  linkSync(join(mirrorSuperseded, "aaaaaaaaaaaa.json"), join(scratch, "mirror-archive-hardlink.json"));
  symlinkSync(mirrorMatrix, join(scratch, "mirror-matrix-alias.json"));
  symlinkSync(join(mirrorPackage, "results"), join(scratch, "mirror-results-alias"), "dir");
  symlinkSync(MATRIX, join(scratch, "frozen-alias.json"));
  symlinkSync(resolve(PACKAGE_ROOT, "results"), join(scratch, "results-alias"), "dir");
});
afterAll(() => {
  expect(canonicalDigests()).toEqual(canonicalBefore);
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
    if (existsSync(join(GENERATIONS, "INDEX.JSON"))) {
      expect(() => assertScratchDestination(resolve(PACKAGE_ROOT, "results/MATRIX.JSON")))
        .toThrow(/G1.*publish/i);
      expect(() => assertScratchDestination(join(GENERATIONS, "INDEX.JSON"))).toThrow(/G1.*publish/i);
      expect(() => assertScratchDestination(resolve(PACKAGE_ROOT, "results/SUPERSEDED/INDEX.JSON")))
        .toThrow(/G1.*publish/i);
      expect(() => assertScratchDestination(resolve(PACKAGE_ROOT, "results/GENERATIONS/unwritten.json")))
        .toThrow(/G1.*publish/i);
    }
    expect(() => assertScratchDestination(join(scratch, "subdir", "result.json"))).not.toThrow();
  });

  it("compare refuses its default and explicitly named canonical destinations before capturing", () => {
    for (const args of [compareArgs(), compareArgs(mirrorMatrix),
      compareArgs(join(mirrorGenerations, "85ad7f7e3e0d.json")),
      compareArgs(join(scratch, "mirror-matrix-alias.json")),
      compareArgs(join(scratch, "mirror-matrix-hardlink.json")),
      compareArgs(join(scratch, "mirror-generation-hardlink.json")),
      compareArgs(join(scratch, "mirror-index-hardlink.json")),
      compareArgs(join(scratch, "mirror-archive-hardlink.json")),
      ...(existsSync(join(mirrorGenerations, "INDEX.JSON")) ? [
        compareArgs(join(mirrorPackage, "results/MATRIX.JSON")),
        compareArgs(join(mirrorPackage, "results/GENERATIONS/85ad7f7e3e0d.JSON")),
        compareArgs(join(mirrorPackage, "results/GENERATIONS/INDEX.JSON")),
        compareArgs(join(mirrorPackage, "results/SUPERSEDED/aaaaaaaaaaaa.JSON")),
        compareArgs(join(mirrorPackage, "results/GENERATIONS/future.json")),
      ] : [])]) {
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
      join(scratch, "mirror-results-alias", "generations", "new.json"),
      join(scratch, "mirror-matrix-hardlink.json"),
      ...(existsSync(join(mirrorGenerations, "INDEX.JSON")) ? [
        join(mirrorPackage, "results/MATRIX.JSON"),
        join(mirrorPackage, "results/GENERATIONS/future.json"),
      ] : [])]) {
      const before = readFileSync(mirrorMatrix);
      const child = run("diff", [...diffArgs, "--matrix", dest]);
      expect(child.status).not.toBe(0);
      expect(child.stderr).toMatch(/G1.*publish/i);
      expect(child.stderr).not.toContain("report →");
      expect(readFileSync(mirrorMatrix).equals(before)).toBe(true);
    }
    for (const dest of [mirrorMatrix, join(mirrorGenerations, "new.json"),
      join(scratch, "mirror-index-hardlink.json"),
      ...(existsSync(join(mirrorSuperseded, "INDEX.JSON")) ? [
        join(mirrorPackage, "results/SUPERSEDED/INDEX.JSON"),
      ] : [])]) {
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

  it("imports a monolithic-only source mirror and keeps scratch and frozen aliases distinct", () => {
    const oldPackage = join(scratch, "monolithic/packages/calibration");
    const results = join(oldPackage, "results");
    mkdirSync(results, { recursive: true });
    cpSync(join(PACKAGE_ROOT, "src"), join(oldPackage, "src"), { recursive: true });
    copyFileSync(join(PACKAGE_ROOT, "package.json"), join(oldPackage, "package.json"));
    symlinkSync(join(PACKAGE_ROOT, "node_modules"), join(oldPackage, "node_modules"), "dir");
    writeFileSync(join(results, "matrix.json"), JSON.stringify({ schemaVersion: 5, cells: [{
      key: { profileKey: PROFILE, sceneId: SCENE, web: {
        engine: "chromium", engineVersion: "1", renderer: "webgpu",
        samplingBackend: "gpu-texture", gpuAdapter: "test", colorSpace: "srgb",
        capturePath: "materialProfile=profiles/active.json sha256:eeeeeeeeeeee",
      } },
    }] }));
    const scratchMatrix = join(oldPackage, "scratch.json");
    writeFileSync(scratchMatrix, '{"schemaVersion":5,"cells":[]}\n');
    const alias = join(oldPackage, "frozen-alias.json");
    symlinkSync(join(results, "matrix.json"), alias);
    const script = `
      import assert from "node:assert/strict";
      import { loadCurrentRows } from "./src/matrix-store.ts";
      import { assertScratchDestination } from "./src/matrix-write-guard.ts";
      assert.equal(loadCurrentRows({ resultsDir: ${JSON.stringify(results)} }).length, 1);
      assert.equal(loadCurrentRows({ resultsDir: ${JSON.stringify(results)},
        matrixPath: ${JSON.stringify(scratchMatrix)} }).length, 0);
      assert.throws(() => assertScratchDestination(${JSON.stringify(alias)}), /G1.*publish/i);
      assert.throws(() => assertScratchDestination(${JSON.stringify(join(results, "generations/future.json"))}),
        /G1.*publish/i);
      console.log("monolithic mirror passed");
    `;
    const child = spawnSync(process.execPath,
      ["--import", "tsx", "--input-type=module", "--eval", script],
      { cwd: oldPackage, encoding: "utf8" });
    expect(child.status, child.stderr).toBe(0);
    expect(child.stdout).toContain("monolithic mirror passed");
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
