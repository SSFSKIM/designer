/** Invalid inputs to the same guards the live G2 reader calls. No image I/O. */
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import {
  fingerprint, admitRead, attest, pageReady, repeated, resumeRead, outputAvailable, scratchPath, machineReady, nativeAdmission, captureBytes, sha, readCell,
} from "./read-guards";

export function exerciseDryRefusals() {
  const refusals: { name: string; reason: string }[] = [];
  const rejects = (name: string, run: () => void) => {
    let reason: string | undefined;
    try { run(); } catch (error) { reason = String(error); }
    assert.ok(reason, `${name}: invalid input was admitted`);
    refusals.push({ name, reason });
  };
  for (const name of ["active resolved", "active recorded", "inactive resolved", "raw patch",
    "native plurality", "background raster", "page endpoint"]) {
    fingerprint(name, "expected", "expected");
    rejects(name, () => fingerprint(name, "changed", "expected"));
  }
  admitRead(false, true);
  rejects("candidate attempting holdout", () => admitRead(true, true));
  machineReady({ reduceTransparency: 0, increaseContrast: 0 });
  rejects("machine reduce transparency", () => machineReady({ reduceTransparency: 1, increaseContrast: 0 }));
  rejects("machine increase contrast", () => machineReady({ reduceTransparency: 0, increaseContrast: 1 }));
  attest({ presentedActive: true }, "active");
  rejects("native active attestation", () => attest({ presentedActive: false }, "active"));
  rejects("checking plurality", () => nativeAdmission({ checking: true, isHoldout: false,
    recovered: false, run: undefined, entry: {}, state: "inactive" }));
  const native = { presentedActive: false, presentation: {
    observedPose: "inactive", isKeyWindow: false, appIsActive: false } };
  attest(native, "inactive");
  rejects("native attestation", () => attest({ ...native, presentedActive: true }, "inactive"));
  rejects("missing presentation", () => attest({ presentedActive: false }, "inactive"));
  const declared = { canvas: { width: 800, height: 600 }, scale: 2 };
  const report = { canvas: declared.canvas, requestedScale: 2, devicePixelRatio: 2,
    problems: [], pixelSize: [1600, 1200], adapter: { ok: true, isFallback: false },
    groups: [{ state: { activeRenderer: "webgpu" } }] };
  pageReady(report, declared, "webgpu", true);
  rejects("page dimensions", () => pageReady({ ...report, canvas: { width: 801, height: 600 } }, declared, "webgpu", true));
  rejects("pixel dimensions", () => pageReady({ ...report, pixelSize: [800, 600] }, declared, "webgpu", true));
  rejects("page scale", () => pageReady({ ...report, requestedScale: 1 }, declared, "webgpu", true));
  rejects("device scale", () => pageReady({ ...report, devicePixelRatio: 1 }, declared, "webgpu", true));
  rejects("page readiness", () => pageReady(report, declared, "webgpu", false));
  rejects("missing report", () => pageReady(undefined, declared, "webgpu", true));
  rejects("page problems", () => pageReady({ ...report, problems: ["bad framing"] }, declared, "webgpu", true));
  rejects("wrong tier", () => pageReady({ ...report, groups: [{ state: { activeRenderer: "css" } }] }, declared, "webgpu", true));
  rejects("empty tier proof", () => pageReady({ ...report, groups: [] }, declared, "webgpu", true));
  rejects("fallback adapter", () => pageReady({ ...report, adapter: { ok: true, isFallback: true } }, declared, "webgpu", true));
  repeated(Buffer.from("a"), Buffer.from("a"));
  rejects("nondeterministic repeats", () => repeated(Buffer.from("a"), Buffer.from("b")));
  const identity = { patchSha256: "patch", renderer: "webgpu", sourceSha256: { a: "a" },
    instrumentSha256: { b: "b" }, sceneSpecSha256: "scene", readAgainst: { light: "resolved" },
    endpointUnderTest: { lightInactiveSha256: "resolved" } };
  const population = [{ profile: "p", scene: "s" }];
  const row = { profile: "p", scene: "s", repeats: 2, scale: 1, state: "inactive",
    isControl: false, isHoldout: false, preAttestationRecovered: false, scored: true, groups: ["D"],
    deltaE: { mean: 0.1 }, body: { n: 1, deltaE: 0.1, webY: 0.5, nativeY: 0.5,
      webSD: 0.1, nativeSD: 0.1, webChroma: 0.1, nativeChroma: 0.1 },
    capture: "/tmp/synthetic-web", nativePath: "/synthetic-native",
    captureSha256: sha("web"), nativeSha256: sha("native"), backgroundSha256: sha("background"),
    nativeSource: "sitting", nativeRun: "run-1", nativeAttestation: native,
    geometry: { capturedPixels: [2, 2], pixelSize: [2, 2], requestedScale: 1,
      devicePixelRatio: 1, canvas: { width: 2, height: 2 } },
    adapter: { ok: true, isFallback: false },
    actualGroups: [{ state: { activeRenderer: "webgpu" } }], problems: [] };
  captureBytes(row, Buffer.from("web"));
  rejects("retained capture bytes", () => captureBytes(row, Buffer.from("changed")));
  rejects("resume stub", () => resumeRead({ ...identity,
    rows: [{ profile: "p", scene: "s", repeats: 2 }] }, identity, population));
  rejects("resume non-finite metric", () => resumeRead({ ...identity,
    rows: [{ ...row, deltaE: { mean: NaN } }] }, identity, population));
  rejects("resume missing geometry", () => resumeRead({ ...identity,
    rows: [{ ...row, geometry: {} }] }, identity, population));
  resumeRead({ ...identity, rows: [row] }, identity, population);
  // Profile/cell exclusion applies regardless of whether a scene already belongs to bed B.
  const cssHoldout = new Set(["dark/checkerboard-64__rrect-lg__inactive", "light/hc-text__capsule-button__inactive"]);
  for (const cell of cssHoldout) {
    assert.equal(readCell("css", cell, cssHoldout), false);
    assert.equal(readCell("webgpu", cell, cssHoldout), true);
  }
  // Exercise the scorer's own guard-only dispatch, not a TypeScript approximation of it.
  const scorer = resolve(import.meta.dirname, "score-bound.py");
  execFileSync("python3", [scorer, "--check-renderer", "webgpu"], { stdio: "pipe" });
  rejects("Python scorer rejects CSS", () => {
    execFileSync("python3", [scorer, "--check-renderer", "css"], { stdio: "pipe" });
  });
  const cssIdentity = { ...identity, renderer: "css" };
  const cssRow = { ...row, scored: false, adapter: null,
    actualGroups: [{ state: { activeRenderer: "css" } }] };
  resumeRead({ ...cssIdentity, rows: [cssRow] }, cssIdentity, population);
  rejects("CSS wrong-tier scoring", () => resumeRead({ ...cssIdentity,
    rows: [{ ...cssRow, scored: true }] }, cssIdentity, population));
  rejects("CSS holdout resume", () => resumeRead({ ...cssIdentity,
    rows: [{ ...cssRow, isHoldout: true }] }, cssIdentity, population));
  rejects("CSS inactive presentation", () => resumeRead({ ...cssIdentity,
    rows: [{ ...cssRow, nativeAttestation: {} }] }, cssIdentity, population));
  resumeRead({ ...identity, rows: [{ ...row, state: "rest",
    nativeAttestation: { presentedActive: true } }] }, identity, population);
  const recovered = { ...row, isHoldout: true, scored: false, groups: ["H"],
    preAttestationRecovered: true, nativeSource: "recovered", nativeRun: null,
    nativeAttestation: {}, recoveredLineage: {
      nativeBlobOid: "a".repeat(40), backgroundBlobOid: "b".repeat(40) } };
  resumeRead({ ...identity, rows: [recovered] }, identity, population);
  rejects("recovered missing lineage", () => resumeRead({ ...identity,
    rows: [{ ...recovered, recoveredLineage: null }] }, identity, population));
  rejects("recovered masquerading as checking", () => resumeRead({ ...identity,
    rows: [{ ...recovered, scored: true }] }, identity, population));
  rejects("duplicate resume", () => resumeRead({ ...identity, rows: [row, row] }, identity, population));
  for (const key of Object.keys(identity)) {
    rejects(`resume ${key}`, () => resumeRead({ ...identity, [key]: "other", rows: [] }, identity, population));
  }
  rejects("resume unnamed row", () => resumeRead({ ...identity, rows: [{ ...row, scene: "other" }] }, identity, population));
  rejects("resume missing repeats", () => resumeRead({ ...identity, rows: [{ ...row, repeats: 1 }] }, identity, population));
  outputAvailable("/tmp/result.json", false);
  rejects("output overwrite", () => outputAvailable("/tmp/result.json", true));
  const repo = resolve(import.meta.dirname, "../../../..");
  scratchPath("/tmp/w28-dry-synthetic", repo);
  rejects("canonical output", () => scratchPath(resolve(repo, "packages/calibration/results/matrix.json"), repo));
  return { acceptedValidControl: true, refusals };
}
