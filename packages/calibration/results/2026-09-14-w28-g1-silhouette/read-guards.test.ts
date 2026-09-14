import { test } from "node:test";
import assert from "node:assert/strict";
import { exerciseDryRefusals } from "./dry-refusals";
import { mkdtempSync, symlinkSync, rmSync, writeFileSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve, dirname } from "node:path";
import { execFileSync } from "node:child_process";
import * as guards from "./read-guards";

test("scratch refuses owning checkout and real symlink aliases from this worktree", () => {
  const temp = mkdtempSync(resolve(tmpdir(), "w28-guards-"));
  const repo = resolve(import.meta.dirname, "../../../..");
  const common = execFileSync("git", ["-C", repo, "rev-parse", "--path-format=absolute", "--git-common-dir"], { encoding: "utf8" }).trim();
  const owner = dirname(realpathSync(common));
  try {
    const alias = resolve(temp, "alias");
    symlinkSync(owner, alias);
    for (const root of [owner, repo, alias]) {
      assert.throws(() => guards.scratchPath(resolve(root, "packages/calibration/results/matrix.json"), repo), /outside the repository/);
    }
    guards.scratchPath(resolve(temp, "scratch/result.json"), repo);
  } finally { rmSync(temp, { recursive: true, force: true }); }
});

test("active admission uses baseline schema rather than advisory seed or mutable current schema", () => {
  const active = { schemaVersion: 1, profileKey: "profile", patch: {}, resolvedMaterialSha256: "abc" };
  const seed = { schemaVersion: 1, profileKey: "seed", material: {} };
  assert.equal(guards.activeDocument("seed", seed, seed), false);
  assert.equal(guards.activeDocument("active", active, active), true);
  assert.throws(() => guards.activeDocument("active", seed, active), /fingerprint mismatch/);
  assert.throws(() => guards.activeDocument("active", { ...active, resolvedMaterialSha256: "other" }, active), /fingerprint mismatch/);
});

test("selected sweep binds current source bytes and selected rung digests", () => {
  const temp = mkdtempSync(resolve(tmpdir(), "w28-source-"));
  try {
    writeFileSync(resolve(temp, "runtime.ts"), "original");
    const rung = { inactiveSha256: "resolved", patchSha256: "raw" };
    const matrix = { label: "chosen", renderer: "webgpu", ...rung,
      sourceSha256: { "runtime.ts": guards.sha("original") } };
    guards.selectedSweep(matrix, "chosen", rung, temp);
    for (const changed of [{ label: "other" }, { inactiveSha256: "other" },
      { patchSha256: "other" }, { sourceSha256: {} }, { renderer: "css" }]) {
      assert.throws(() => guards.selectedSweep({ ...matrix, ...changed }, "chosen", rung, temp));
    }
    writeFileSync(resolve(temp, "runtime.ts"), "changed");
    assert.throws(() => guards.selectedSweep(matrix, "chosen", rung, temp), /fingerprint mismatch/);
  } finally { rmSync(temp, { recursive: true, force: true }); }
});

test("native admission keeps checking plurality strict and recovered holdouts separate", () => {
  const entry = { presentedActive: false, presentation: {
    observedPose: "inactive", isKeyWindow: false, appIsActive: false } };
  const normal = { checking: true, isHoldout: false, recovered: false,
    run: { sha256: "digest" }, entry, state: "inactive" };
  guards.nativeAdmission(normal);
  assert.throws(() => guards.nativeAdmission({ ...normal, run: undefined }), /plurality/);
  assert.throws(() => guards.nativeAdmission({ ...normal, recovered: true }), /plurality/);
  assert.throws(() => guards.nativeAdmission({ ...normal, entry: {} }), /presentation/);
  assert.deepEqual(guards.nativeAdmission({ ...normal, checking: false, isHoldout: true,
    recovered: true, run: undefined, entry: {} }),
  { isControl: false, isHoldout: true, preAttestationRecovered: true });
  guards.attest({ presentedActive: true }, "active");
  assert.throws(() => guards.attest({ presentedActive: false }, "active"), /presentation/);
});

test("machine admission refuses enabled or unproved accessibility settings", () => {
  guards.machineReady({ reduceTransparency: 0, increaseContrast: 0 });
  for (const value of [1, null, undefined]) {
    assert.throws(() => guards.machineReady({ reduceTransparency: value, increaseContrast: 0 }));
    assert.throws(() => guards.machineReady({ reduceTransparency: 0, increaseContrast: value }));
  }
});

test("blob lineage includes the object header rather than a plain byte hash", () => {
  assert.equal(guards.gitBlobOid(Buffer.from("test\n")), "9daeafb9864cf43055ae93beb0afd6c7d144bfa4");
  assert.throws(() => guards.fingerprint("recovered native", guards.gitBlobOid(Buffer.from("changed")),
    "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"));
});

test("resume rejects placeholder holdouts and changed endpoint metadata", () => {
  const identity = { endpointUnderTest: { lightInactiveSha256: "sealed" } };
  const population = [{ profile: "p", scene: "s" }];
  assert.throws(() => guards.resumeRead({ ...identity,
    rows: [{ profile: "p", scene: "s", repeats: 2 }] }, identity, population), /evidence/);
  assert.throws(() => guards.resumeRead({ endpointUnderTest: { lightInactiveSha256: "other" },
    rows: [] }, identity, population), /fingerprint mismatch/);
});

test("retained capture verification detects changed persisted bytes", () => {
  const row = { captureSha256: guards.sha("original") };
  guards.captureBytes(row, Buffer.from("original"));
  assert.throws(() => guards.captureBytes(row, Buffer.from("changed")), /fingerprint mismatch/);
});

test("CSS excludes declared holdout pairs even when their scene belongs to the bed", () => {
  const holdout = new Set(["dark/checkerboard-64__rrect-lg__inactive", "light/hc-text__capsule-button__inactive"]);
  for (const cell of holdout) {
    assert.equal(guards.readCell("css", cell, holdout), false);
    assert.equal(guards.readCell("webgpu", cell, holdout), true);
  }
  assert.equal(guards.readCell("css", "light/checkerboard-64__rrect-lg__inactive", holdout), true);
  assert.throws(() => guards.admitScoring("css", true), /WebGPU/);
  guards.admitScoring("css", false);
});

test("real-reader guards reject corrupted contracts before capture or native I/O", () => {
  const evidence = exerciseDryRefusals();
  assert.ok(evidence.refusals.length >= 20);
  assert.equal(evidence.acceptedValidControl, true);
  assert.match(evidence.refusals.find((r) => r.name === "Python scorer rejects CSS")!.reason,
    /only WebGPU/);
});
