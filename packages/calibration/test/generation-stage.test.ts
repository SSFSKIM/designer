/** Publication runs copied sources in disposable repositories, never on real evidence. */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { cpSync, existsSync, linkSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync,
  symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { afterAll, expect, it } from "vitest";

const pkg = resolve(import.meta.dirname, "..");
const scratch = mkdtempSync(join(tmpdir(), "w40-publisher-"));
const canonical = ["matrix.json", ...["generations", "superseded"].flatMap((d) =>
  readdirSync(join(pkg, "results", d)).map((n) => `${d}/${n}`))];
const digest = (b: Buffer | string) => createHash("sha256").update(b).digest("hex");
const before = canonical.map((p) => digest(readFileSync(join(pkg, "results", p))));
afterAll(() => {
  expect(canonical.map((p) => digest(readFileSync(join(pkg, "results", p))))).toEqual(before);
  rmSync(scratch, { recursive: true, force: true });
});
let sequence = 0;
function repo() {
  const root = join(scratch, String(sequence++));
  const copy = join(root, "packages/calibration");
  mkdirSync(join(copy, "results/generations"), { recursive: true });
  cpSync(join(pkg, "src"), join(copy, "src"), { recursive: true });
  cpSync(join(pkg, "cli"), join(copy, "cli"), { recursive: true });
  cpSync(join(pkg, "package.json"), join(copy, "package.json"));
  symlinkSync(join(pkg, "node_modules"), join(copy, "node_modules"));
  writeFileSync(join(copy, "results/matrix.json"), '{"schemaVersion":5,"cells":[]}\n');
  writeFileSync(join(copy, "results/generations/index.json"), JSON.stringify({
    schemaVersion: 1, files: {}, byDocumentSha256: {}, currentByProfile: {},
  }));
  const reference = join(root, "apps/reference-apple");
  mkdirSync(join(reference, "fixtures"), { recursive: true });
  writeFileSync(join(reference, "scenes.json"), JSON.stringify({ scenes: [
    { id: "cal", fixtureSet: "calibration" }, { id: "held", fixtureSet: "holdout" },
  ], split: { calibration: ["cal"], holdout: ["held"] } }));
  writeFileSync(join(reference, "fixtures/manifest.json"), JSON.stringify({ profiles: [{
    profileKey: "apple-macos-27.0-1x-light-standard-glass0.5", fixtures: [
      { sceneId: "cal", fixtureSet: "calibration" }, { sceneId: "held", fixtureSet: "holdout" },
    ],
  }] }));
  writeFileSync(join(copy, "active.json"), '{"candidate":1}\n');
  return copy;
}
const profile = "apple-macos-27.0-1x-light-standard-glass0.5";
function run(copy: string, args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", "cli/matrix.ts", ...args], {
    cwd: copy, encoding: "utf8", env: { ...process.env, VITREA_MATRIX_PATH: "" },
  });
}
function declare(copy: string, name = "stage") {
  const child = run(copy, ["stage", name, "--profile", profile, "--renderer", "webgpu,css",
    "--set", "calibration,holdout", "--material-profile", "active.json"]);
  expect(child.status, child.stderr).toBe(0);
}
function fill(copy: string, name = "stage", missing = false) {
  const hash = digest(readFileSync(join(copy, "active.json"))).slice(0, 12);
  const rows = ["webgpu", "css"].flatMap((renderer) => ["cal", "held"].map((sceneId) => ({
    key: { profileKey: profile, sceneId, web: { engine: "chromium", engineVersion: "1",
      renderer, samplingBackend: renderer === "css" ? "css-backdrop" : "gpu-texture",
      gpuAdapter: "test", colorSpace: "srgb",
      capturePath: `materialProfile=packages/calibration/active.json sha256:${hash}` } },
    fixtureSet: sceneId === "held" ? "holdout" : "calibration",
  })));
  if (missing) rows.pop();
  writeFileSync(join(copy, name, "matrix.json"), JSON.stringify({ schemaVersion: 5, cells: rows }, null, 2));
  return hash;
}
it("accepts a recorded canonical capture with unchanged active and receded document hashes", () => {
  const copy = repo();
  const root = resolve(copy, "../..");
  const source = resolve(pkg, "../..");
  cpSync(join(source, "apps/reference-apple/scenes.json"),
    join(root, "apps/reference-apple/scenes.json"));
  cpSync(join(source, "apps/reference-apple/fixtures/manifest.json"),
    join(root, "apps/reference-apple/fixtures/manifest.json"));
  mkdirSync(join(copy, "profiles"));
  const base = "apple-macos-27.0-1x-light-standard-glass0.5";
  for (const suffix of ["", "-receded"]) {
    cpSync(join(pkg, `profiles/${base}${suffix}.json`), join(copy, `profiles/${base}${suffix}.json`));
  }
  const sourceRows = JSON.parse(readFileSync(join(pkg, "results/generations/85ad7f7e3e0d.json"),
    "utf8"));
  const recorded = sourceRows.cells.find((row: { key: { profileKey: string; web: { renderer: string } };
    fixtureSet: string }) => row.key.profileKey === profile && row.key.web.renderer === "webgpu" &&
    row.fixtureSet === "calibration");
  expect(recorded).toBeDefined();
  expect(recorded.key.web.capturePath).toContain(
    `materialProfile=packages/calibration/profiles/${base}.json sha256:85ad7f7e3e0d`);
  expect(recorded.key.web.capturePath).toContain(
    `recededProfile=packages/calibration/profiles/${base}-receded.json sha256:30fbe05986ae`);
  const child = run(copy, ["stage", "stage", "--profile", profile, "--renderer", "webgpu",
    "--set", "calibration", "--material-profile", `profiles/${base}.json`,
    "--receded-profile", `profiles/${base}-receded.json`]);
  expect(child.status, child.stderr).toBe(0);
  const declared = JSON.parse(readFileSync(join(copy, "stage/membership.json"), "utf8"));
  expect(declared.active).toEqual({ path: `packages/calibration/profiles/${base}.json`,
    sha256: "85ad7f7e3e0d" });
  expect(declared.receded).toEqual({ path: `packages/calibration/profiles/${base}-receded.json`,
    sha256: "30fbe05986ae" });
  writeFileSync(join(copy, "stage/matrix.json"),
    JSON.stringify({ schemaVersion: 5, cells: [recorded] }));
  const status = run(copy, ["status", "stage"]);
  expect(status.status, status.stderr).toBe(0);
  expect(JSON.parse(status.stdout).present).toBe(1);
});
it("uses an absolute capture label for a document outside the repository", () => {
  const copy = repo();
  const outside = join(scratch, "outside-profile.json");
  writeFileSync(outside, '{"external":true}\n');
  const child = run(copy, ["stage", "outside-stage", "--profile", profile,
    "--renderer", "webgpu", "--set", "calibration", "--material-profile", outside]);
  expect(child.status, child.stderr).toBe(0);
  const membership = JSON.parse(readFileSync(join(copy, "outside-stage/membership.json"), "utf8"));
  expect(membership.active).toEqual({ path: outside,
    sha256: digest(readFileSync(outside)).slice(0, 12) });
  const row = { key: { profileKey: profile, sceneId: "cal", web: { engine: "chromium",
    engineVersion: "1", renderer: "webgpu", samplingBackend: "gpu-texture", gpuAdapter: "test",
    colorSpace: "srgb", capturePath: `materialProfile=${outside} sha256:${membership.active.sha256}` } },
    fixtureSet: "calibration" };
  writeFileSync(join(copy, "outside-stage/matrix.json"),
    JSON.stringify({ schemaVersion: 5, cells: [row] }));
  const status = run(copy, ["status", "outside-stage"]);
  expect(status.status, status.stderr).toBe(0);
  expect(JSON.parse(status.stdout).present).toBe(1);
});
it("refuses equal active and receded document hashes before creating a stage", () => {
  for (const receded of ["active.json", "identical.json"]) {
    const copy = repo();
    if (receded !== "active.json") cpSync(join(copy, "active.json"), join(copy, receded));
    const index = readFileSync(join(copy, "results/generations/index.json"));
    const matrix = readFileSync(join(copy, "results/matrix.json"));
    const child = run(copy, ["stage", "stage", "--profile", profile, "--renderer", "webgpu",
      "--set", "calibration", "--material-profile", "active.json", "--receded-profile", receded]);
    expect(child.status).toBe(1);
    expect(child.stderr).toMatch(/active and receded.*distinct/i);
    expect(existsSync(join(copy, "stage"))).toBe(false);
    expect(readFileSync(join(copy, "results/generations/index.json"))).toEqual(index);
    expect(readFileSync(join(copy, "results/matrix.json"))).toEqual(matrix);
    expect(readdirSync(join(copy, "results/generations"))).toEqual(["index.json"]);
  }
});
it("refuses an edited membership with equal role hashes without altering prior evidence", () => {
  const copy = repo(); declare(copy); const first = fill(copy);
  const published = run(copy, ["publish", "stage"]);
  expect(published.status, published.stderr).toBe(0);
  const priorPath = join(copy, `results/generations/${first}.json`);
  const prior = readFileSync(priorPath);
  const index = readFileSync(join(copy, "results/generations/index.json"));

  writeFileSync(join(copy, "active-next.json"), '{"candidate":2}\n');
  const next = digest(readFileSync(join(copy, "active-next.json"))).slice(0, 12);
  const declaration = run(copy, ["stage", "next", "--profile", profile,
    "--renderer", "webgpu,css", "--set", "calibration,holdout",
    "--material-profile", "active-next.json"]);
  expect(declaration.status, declaration.stderr).toBe(0);
  fill(copy, "next");
  const rowsPath = join(copy, "next/matrix.json");
  writeFileSync(rowsPath, readFileSync(rowsPath, "utf8").replaceAll(
    `active.json sha256:${first}`, `active-next.json sha256:${next}`));
  cpSync(join(copy, "active-next.json"), join(copy, "identical.json"));
  const membershipPath = join(copy, "next/membership.json");
  const membership = JSON.parse(readFileSync(membershipPath, "utf8"));
  membership.receded = { path: "packages/calibration/identical.json", sha256: next };
  writeFileSync(membershipPath, JSON.stringify(membership));

  const child = run(copy, ["publish", "next"]);
  expect(child.status).toBe(1);
  expect(child.stderr).toMatch(/active and receded.*distinct/i);
  expect(readFileSync(priorPath)).toEqual(prior);
  expect(readFileSync(join(copy, "results/generations/index.json"))).toEqual(index);
  expect(readdirSync(join(copy, "results/generations")).sort()).toEqual([`${first}.json`, "index.json"]);
});
it("declares all cells before runs and refuses incomplete publication and redeclaration", () => {
  const copy = repo(); declare(copy);
  expect(run(copy, ["stage", "stage", "--profile", profile]).status).toBe(1);
  fill(copy, "stage", true);
  const status = run(copy, ["status", "stage"]);
  expect(status.stdout).toContain('"missing": 1');
  const index = readFileSync(join(copy, "results/generations/index.json"));
  expect(run(copy, ["publish", "stage"]).stderr).toMatch(/incomplete/i);
  expect(readFileSync(join(copy, "results/generations/index.json"))).toEqual(index);
});
it("publishes once, preserving row slices, and retires the previous selection without changing its bytes", () => {
  const copy = repo(); declare(copy); const first = fill(copy);
  const published = run(copy, ["publish", "stage"]);
  expect(published.status, published.stderr).toBe(0);
  const file = join(copy, `results/generations/${first}.json`);
  const original = readFileSync(file);
  expect(published.stdout).toContain(digest(original));
  expect(run(copy, ["publish", "stage"]).status).toBe(1);
  writeFileSync(join(copy, "active.json"), '{"candidate":2}\n');
  declare(copy, "next"); const second = fill(copy, "next");
  const next = run(copy, ["publish", "next"]);
  expect(next.status, next.stderr).toBe(0);
  const index = JSON.parse(readFileSync(join(copy, "results/generations/index.json"), "utf8"));
  expect(index.files[`${first}.json`].status).toBe("retired");
  expect(index.currentByProfile[profile]).toBe(`${second}.json`);
  expect(readFileSync(file)).toEqual(original);
});
it("refuses altered documents and a colliding unindexed file without touching the index", () => {
  const copy = repo(); declare(copy); const hash = fill(copy);
  const index = readFileSync(join(copy, "results/generations/index.json"));
  writeFileSync(join(copy, `results/generations/${hash}.json`), "collision");
  expect(run(copy, ["publish", "stage"]).stderr).toMatch(/collid|exists/i);
  writeFileSync(join(copy, "active.json"), "changed");
  expect(run(copy, ["status", "stage"]).stderr).toMatch(/digest/i);
  expect(readFileSync(join(copy, "results/generations/index.json"))).toEqual(index);
});
it("refuses row document drift, undeclared rows, and existing authoritative keys", () => {
  const copy = repo(); declare(copy); fill(copy);
  const path = join(copy, "stage/matrix.json");
  const raw = readFileSync(path, "utf8");
  writeFileSync(path, raw.replace(/sha256:[0-9a-f]{12}/, "sha256:aaaaaaaaaaaa"));
  expect(run(copy, ["publish", "stage"]).stderr).toMatch(/row document digests/);
  writeFileSync(path, raw.replace('"sceneId": "cal"', '"sceneId": "wave-owned"'));
  expect(run(copy, ["publish", "stage"]).stderr).toMatch(/outside declared/);
  writeFileSync(path, raw);
  expect(run(copy, ["publish", "stage"]).status).toBe(0);
  expect(run(copy, ["publish", "stage"]).stderr).toMatch(/serialized key already exists/);
});
it("qualifies a receded-only reseal and preserves every alias owner", () => {
  const copy = repo(); declare(copy); const active = fill(copy);
  expect(run(copy, ["publish", "stage"]).status).toBe(0);
  writeFileSync(join(copy, "receded.json"), '{"receded":1}\n');
  const receded = digest(readFileSync(join(copy, "receded.json"))).slice(0, 12);
  expect(run(copy, ["stage", "next", "--profile", profile, "--renderer", "webgpu,css",
    "--set", "calibration,holdout", "--material-profile", "active.json",
    "--receded-profile", "receded.json"]).status).toBe(0);
  fill(copy, "next");
  const path = join(copy, "next/matrix.json");
  writeFileSync(path, readFileSync(path, "utf8").replaceAll(`sha256:${active}`,
    `sha256:${active} recededProfile=packages/calibration/receded.json sha256:${receded}`));
  const child = run(copy, ["publish", "next"]);
  expect(child.status, child.stderr).toBe(0);
  const index = JSON.parse(readFileSync(join(copy, "results/generations/index.json"), "utf8"));
  expect(index.byDocumentSha256[active]).toEqual([`${active}.json`, `${active}-${receded}.json`]);
});
it("refuses alias path repointing even with a new receded identity", () => {
  const copy = repo(); declare(copy); const active = fill(copy);
  expect(run(copy, ["publish", "stage"]).status).toBe(0);
  cpSync(join(copy, "active.json"), join(copy, "imposter.json"));
  writeFileSync(join(copy, "receded.json"), '{"receded":2}\n');
  const receded = digest(readFileSync(join(copy, "receded.json"))).slice(0, 12);
  expect(run(copy, ["stage", "next", "--profile", profile, "--renderer", "webgpu,css",
    "--set", "calibration,holdout", "--material-profile", "imposter.json",
    "--receded-profile", "receded.json"]).status).toBe(0);
  fill(copy, "next");
  const path = join(copy, "next/matrix.json");
  writeFileSync(path, readFileSync(path, "utf8").replaceAll(`active.json sha256:${active}`,
    `imposter.json sha256:${active} recededProfile=packages/calibration/receded.json sha256:${receded}`));
  expect(run(copy, ["publish", "next"]).stderr).toMatch(/alias repoint/);
});
it("rolls back a failure between generation installation and index commit", () => {
  const copy = repo(); declare(copy); fill(copy);
  const index = readFileSync(join(copy, "results/generations/index.json"));
  // Fail the real filesystem call, not a test-only branch in the publisher.
  writeFileSync(join(copy, "fault.mjs"), `import fs from "node:fs";
import { syncBuiltinESMExports } from "node:module";
const rename = fs.renameSync;
fs.renameSync = (from, to) => {
  if (String(from).endsWith(".index.tmp")) throw new Error("simulated index rename failure");
  return rename(from, to);
};
syncBuiltinESMExports();
const { publishGeneration } = await import("./src/matrix-write-guard.ts");
try { publishGeneration("stage"); process.exitCode = 2; }
catch (e) { console.log(e.message); }
`);
  const child = spawnSync(process.execPath, ["--import", "tsx", "fault.mjs"], { cwd: copy, encoding: "utf8" });
  expect(child.status, child.stderr).toBe(0);
  expect(child.stdout).toContain("simulated index rename failure");
  expect(readFileSync(join(copy, "results/generations/index.json"))).toEqual(index);
  expect(readdirSync(join(copy, "results/generations"))).toEqual(["index.json"]);
  expect(run(copy, ["publish", "stage"]).status).toBe(0);
});
it("refuses canonical generation-index output in the W39 wave launcher itself", () => {
  const copy = repo();
  const dir = "2026-09-26-w39-g0-colour-edge-bed";
  mkdirSync(join(copy, "results", dir));
  cpSync(join(pkg, "results", dir, "wave.py"), join(copy, "results", dir, "wave.py"));
  linkSync(join(copy, "results/generations/index.json"), join(copy, "index-hardlink.json"));
  symlinkSync(join(copy, "results/generations"), join(copy, "generation-alias"));
  const targets = [join(copy, "results/generations/index.json"),
    join(copy, "results/generations/future.json"), join(copy, "index-hardlink.json"),
    join(copy, "generation-alias/future.json"),
    ...(existsSync(join(copy, "results/GENERATIONS")) ? [join(copy, "results/GENERATIONS/future.json")] : [])];
  const child = spawnSync("python3.12", ["-c", `import importlib.util, pathlib
p = pathlib.Path(${JSON.stringify(join(copy, "results", dir, "wave.py"))})
s = importlib.util.spec_from_file_location('wave', p)
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
for target in ${JSON.stringify(targets)}:
    try: m.refuse_canonical(target)
    except ValueError as e: print(e)
    else: raise AssertionError('canonical path was admitted: ' + target)
`], { encoding: "utf8" });
  expect(child.status, child.stderr).toBe(0);
  expect(child.stdout).toContain("refuses canonical");
});
it("does not treat a new engine key as permission to append to a published identity", () => {
  const copy = repo(); declare(copy); fill(copy);
  expect(run(copy, ["publish", "stage"]).status).toBe(0);
  declare(copy, "late-holdout"); fill(copy, "late-holdout");
  const path = join(copy, "late-holdout/matrix.json");
  writeFileSync(path, readFileSync(path, "utf8").replaceAll('"engineVersion": "1"', '"engineVersion": "2"'));
  expect(run(copy, ["publish", "late-holdout"]).stderr).toMatch(/already published; append refused/);
});
it("refuses a staged compare's foreign document before any browser or fixture read", () => {
  const copy = repo(); declare(copy);
  writeFileSync(join(copy, "foreign.json"), "{}");
  const child = spawnSync(process.execPath, ["--import", "tsx", "cli/compare.ts", "--stage", "stage",
    "--profile", profile, "--renderer", "webgpu", "--set", "calibration",
    "--material-profile", "foreign.json"], { cwd: copy, encoding: "utf8" });
  expect(child.status).toBe(1);
  expect(child.stderr).toMatch(/run document digests differ/);
  expect(readdirSync(join(copy, "stage"))).toEqual(["membership.json"]);
});
it("cleans temporary partial bytes when a write fails before installation", () => {
  const copy = repo(); declare(copy); fill(copy);
  const index = readFileSync(join(copy, "results/generations/index.json"));
  writeFileSync(join(copy, "fault.mjs"), `import fs from "node:fs";
import { syncBuiltinESMExports } from "node:module";
const write = fs.writeFileSync;
fs.writeFileSync = (fd, raw, ...rest) => {
  if (typeof fd === "number") { fs.writeSync(fd, raw.subarray(0, 16)); throw new Error("simulated partial write"); }
  return write(fd, raw, ...rest);
};
syncBuiltinESMExports();
const { publishGeneration } = await import("./src/matrix-write-guard.ts");
try { publishGeneration("stage"); process.exitCode = 2; }
catch (e) { console.log(e.message); }
`);
  const child = spawnSync(process.execPath, ["--import", "tsx", "fault.mjs"], { cwd: copy, encoding: "utf8" });
  expect(child.status, child.stderr).toBe(0);
  expect(child.stdout).toContain("simulated partial write");
  expect(readFileSync(join(copy, "results/generations/index.json"))).toEqual(index);
  expect(readdirSync(join(copy, "results/generations"))).toEqual(["index.json"]);
});
it("does not accept a declaration that drops a required fixture or invents a wave-owned one", () => {
  const copy = repo(); declare(copy); fill(copy);
  const path = join(copy, "stage/membership.json");
  const membership = JSON.parse(readFileSync(path, "utf8"));
  membership.cells.pop();
  writeFileSync(path, JSON.stringify(membership));
  expect(run(copy, ["publish", "stage"]).stderr).toMatch(/canonical profile, tier and set membership/);
});
it("does not let a new indexed alias shadow a frozen document's owner", () => {
  const copy = repo(); declare(copy); fill(copy);
  const matrix = JSON.parse(readFileSync(join(copy, "stage/matrix.json"), "utf8"));
  const frozen = matrix.cells[0];
  frozen.key.profileKey = "apple-macos-26.5-1x-light-standard";
  writeFileSync(join(copy, "results/matrix.json"), JSON.stringify({ schemaVersion: 5, cells: [frozen] }));
  expect(run(copy, ["publish", "stage"]).stderr).toMatch(/frozen document identity/);
});
