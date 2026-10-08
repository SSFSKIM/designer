import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import * as numerical from "./numerical.ts";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import {
  FULL_DOMAIN, evaluateNumerical, readStructuredArguments, verifyPins, parseArguments, loadRuntime,
  type NumericalEndpoint, type StructuredArgument,
} from "./numerical.ts";

// The G0 synthetic exercise discovers only before sealing; after sealing it uses the authorised closure.
const sealed = existsSync(new URL("../declaration.sha256", import.meta.url)) ||
  existsSync(new URL("../fit-declaration.sha256", import.meta.url));
await loadRuntime({ discovery: !sealed });

const sha = (value: string) => createHash("sha256").update(value).digest("hex");
const candidates = ["a".repeat(64), "b".repeat(64)];
const profile = {
  lowEndStrength: 1,
  lowEnd44: [20 / 255, 28 / 255, 50 / 255, 64 / 255] as const,
  lowEnd96: [24 / 255, 32 / 255, 54 / 255, 68 / 255] as const,
  lowEnd160: [28 / 255, 36 / 255, 58 / 255, 72 / 255] as const,
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95] as const,
  backdropToneResponseThin: [0.08, 0.15, 0.2, 0.35] as const,
  backdropToneResponseThick: [0.1, 0.17, 0.25, 0.4] as const,
  backdropToneSizeBias: 1, backdropToneLow: 0, backdropToneHigh: 0.001,
  optics: { regular: { tint: [0.08, 0.08, 0.08] as const, tintAlpha: 0.8 } },
  sizeOcclusionGain: 0,
};
const endpoints: NumericalEndpoint[] = [0.25, 0.5].flatMap((position) =>
  (["active", "receded"] as const).map((pose) => ({ position, pose, profile })));
const domain = { ...FULL_DOMAIN, stepCode: 0.5, spanMin: 44, spanMax: 45 };
const records: StructuredArgument[] = endpoints.flatMap(({ position, pose }) => [1, 2].map((dpr) => {
  const profile = `apple-macos-27.0-${dpr}x-dark-standard-glass${position}`;
  const scene = `impulse__rrect-lg__${pose === "receded" ? "inactive" : "rest"}`;
  return { id: `${profile}|webgpu|${scene}`, profile, renderer: "webgpu", scene, variant: "regular",
    position, pose, dpr, span: 160, role: "calibration",
    encodedLuminance: 4 / 255, linearLuminance: 0.002, rgb: [0.002, 0.002, 0.002],
    candidateSha256: candidates[position === 0.25 ? 0 : 1]!,
  };
}));

test("synthetic composed response passes running-max and unclamped-neutral checks on a reduced helper domain", async () => {
  const report = await evaluateNumerical(endpoints, records, domain);
  assert.equal(report.samples, 4 * 2 * 2 * 129);
  assert.equal(report.status, "PASS");
  assert.ok(report.maxRunningDrawdownCode <= 1e-4);
  assert.ok(report.minimumRequestedNeutral! >= 0);
  assert.equal(report.fixedJoinPass, true);
  assert.equal(report.standDownPass, true);
  assert.equal(report.structuredArgumentPass, true);
});

test("ordered chart rows cannot hide a downward fixed join", async () => {
  const bad = { ...profile, lowEnd44: [0.1, 0.2, 0.5, 0.8] as const,
    lowEnd96: [0.1, 0.2, 0.5, 0.8] as const, lowEnd160: [0.1, 0.2, 0.5, 0.8] as const };
  const report = await evaluateNumerical(endpoints.map((endpoint) => ({ ...endpoint, profile: bad })),
    records, domain);
  assert.equal(report.status, "FAIL");
  assert.equal(report.fixedJoinPass, false);
  assert.ok(report.maxRunningDrawdownCode > 1);
});

test("the structured referee retains the independently measured linear mean and rejects a negative request", async () => {
  const report = await evaluateNumerical(endpoints,
    records.map((record) => ({ ...record, linearLuminance: 0.1, rgb: [0.1, 0.1, 0.1] })), domain);
  assert.equal(report.status, "FAIL");
  assert.ok(report.minimumRequestedNeutral! < 0);
  assert.equal(report.structuredArgumentPass, false);
  assert.ok(report.negativeRequests.some((reading) => reading.kind === "structured"));
});

test("required fixed64 controls retain their actual f32 arguments without expanding compact support", async () => {
  const join = records.map((record) => {
    const scene = `cell-grey-064-s160__${record.pose === "receded" ? "inactive" : "rest"}`;
    const linear = ((64 / 255 + 0.055) / 1.055) ** 2.4;
    return { ...record, id: `${record.profile}|${record.renderer}|${scene}`, scene,
      encodedLuminance: 64 / 255, linearLuminance: linear, rgb: [linear, linear, linear] as const };
  });
  const report = await evaluateNumerical(endpoints, [...records, ...join], domain);
  assert.equal(report.status, "PASS");
  assert.equal(report.fixedJoinPass, true);
  assert.equal(report.structuredArgumentIds.length, 16);
  const rounded = join.map((record) => ({ ...record, encodedLuminance: Math.fround(64 / 255) }));
  assert.equal((await evaluateNumerical(endpoints, [...records, ...rounded], domain)).status, "PASS");
  const { css } = await loadRuntime();
  const curve = css.resolvedBackdropToneResponse(profile);
  const source = css.sourceOptics(profile).regular;
  const encoded = Math.fround(64 / 255);
  const linear = ((encoded + 0.055) / 1.055) ** 2.4;
  assert.equal(css.lowEndNeutralRequest(source,
    { luminance: linear, linearLuminance: linear }, 1, 0, 1, curve, 0, 160), undefined);
  assert.equal(css.backdropToneResponseLevel(encoded, 1, curve, 0, 160),
    css.backdropToneResponseLevel(encoded, 1, { ...curve, lowEndStrength: 0 }, 0, 160));
  await assert.rejects(evaluateNumerical(endpoints,
    [...records, { ...join[0]!, encodedLuminance: 1.01 }], domain), /finite.*\[0,1\]/);
});

test("independently rounded f32 RGB and linear mean are retained, not replaced with a double dot", async () => {
  const authentic = records.map((record) => ({ ...record, encodedLuminance: 0.1104,
    rgb: [0.011612244881689548, 0.011612244881689548, 0.012983032502233982] as const,
    linearLuminance: 0.01171121560037136,
  }));
  const report = await evaluateNumerical(endpoints, authentic, domain);
  assert.equal(report.status, "PASS");
  // A materially inconsistent independent mean is not a precision exception.
  await assert.rejects(evaluateNumerical(endpoints,
    authentic.map((record) => ({ ...record, linearLuminance: 0.012 })), domain), /disagree/);
});

test("missing or incomplete measured argument cohorts cannot receive a pass", async () => {
  assert.equal((await evaluateNumerical(endpoints, [], domain)).status, "UNMEASURED");
  assert.equal((await evaluateNumerical(endpoints, records.slice(1), domain)).status, "UNMEASURED");
});

test("measured arguments require unchanged evidence bytes, matching candidate cohort and exposed roles", () => {
  const root = mkdtempSync(join(tmpdir(), "w50-numerical-test-"));
  try {
    const measured = records.map((record, index) => {
      const path = `argument-${index}.json`;
      const text = JSON.stringify({ schema: "w50-measured-tone-argument-1", ...record });
      writeFileSync(join(root, path), text);
      return { ...record, evidence: { path, sha256: sha(text) } };
    });
    const inventory = JSON.stringify({ schema: "w50-reference-inventory-1", cells: records.map(
      ({ profile, renderer, scene, role }) => ({ profile, renderer, scene, role })) });
    writeFileSync(join(root, "references.json"), inventory);
    const references = { path: "references.json", sha256: sha(inventory) };
    const requiredIds = records.map(({ id }) => id).sort();
    const text = JSON.stringify({ schema: "w50-structured-arguments-1", candidateSha256s: candidates,
      references, requiredIds, records: measured });
    const manifest = join(root, "arguments.json");
    writeFileSync(manifest, text);
    assert.equal(readStructuredArguments(manifest, sha(text), candidates, root).records.length, 8);
    assert.throws(() => readStructuredArguments(manifest, "c".repeat(64), candidates, root), /hash|bytes/);
    assert.throws(() => readStructuredArguments(manifest, sha(text), ["c".repeat(64)], root), /cohort/);
    const partial = JSON.stringify({ schema: "w50-structured-arguments-1", candidateSha256s: candidates,
      references, requiredIds, records: measured.slice(1) });
    writeFileSync(manifest, partial);
    assert.throws(() => readStructuredArguments(manifest, sha(partial), candidates, root), /population/);
    writeFileSync(manifest, text);
    writeFileSync(join(root, measured[0]!.evidence.path), "{}");
    assert.throws(() => readStructuredArguments(manifest, sha(text), candidates, root), /hash|bytes/);
    const withheld = JSON.stringify({ schema: "w50-structured-arguments-1", candidateSha256s: candidates,
      references, requiredIds, records: measured.map((record) => ({ ...record, role: "blind" })) });
    writeFileSync(manifest, withheld);
    assert.throws(() => readStructuredArguments(manifest, sha(withheld), candidates, root), /role|withheld/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("source pins reject changed bytes and runtime closure comes from actual TypeScript loads", async () => {
  const runtime = await loadRuntime();
  const paths = [...runtime.sources.keys()];
  assert.ok(paths.some((path) => path.endsWith("packages/platform-web/src/optics.ts")));
  assert.ok(paths.some((path) => path.endsWith("packages/platform-web/src/material-document.ts")));
  assert.ok(paths.some((path) => path.endsWith("packages/renderer-webgpu/src/material.ts")));
  const root = mkdtempSync(join(tmpdir(), "w50-pin-test-"));
  try {
    writeFileSync(join(root, "source.ts"), "export const value = 1;");
    const pins = [{ path: "source.ts", sha256: sha(readFileSync(join(root, "source.ts"), "utf8")) }];
    verifyPins(root, pins);
    writeFileSync(join(root, "source.ts"), "export const value = 2;");
    assert.throws(() => verifyPins(root, pins), /changed|bytes/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("the source guard refuses changed and late new imports before their top-level marker executes", async () => {
  const root = mkdtempSync(join(tmpdir(), "w50-import-guard-"));
  const marker = join(root, "executed.txt");
  try {
    const allowed = join(root, "allowed.mjs");
    writeFileSync(allowed, "export const value = 1;");
    const hook = numerical.installSourceGuard(root, [{ path: "allowed.mjs", sha256: sha(readFileSync(allowed, "utf8")) }]);
    try {
      assert.equal((await import(pathToFileURL(allowed).href)).value, 1);
      // The initial import returned; the guard must still protect the later measurement branch.
      const late = join(root, "late.mjs");
      writeFileSync(late, `import { writeFileSync } from 'node:fs'; writeFileSync(${JSON.stringify(marker)}, 'BAD');`);
      await assert.rejects(import(pathToFileURL(late).href), /unsealed|Unsealed/);
      assert.equal(existsSync(marker), false);
    } finally {
      hook.deregister();
    }
    const changed = join(root, "changed.mjs");
    writeFileSync(changed, "export const value = 1;");
    const pin = { path: "changed.mjs", sha256: sha(readFileSync(changed, "utf8")) };
    writeFileSync(changed, `import { writeFileSync } from 'node:fs'; writeFileSync(${JSON.stringify(marker)}, 'BAD');`);
    const changedHook = numerical.installSourceGuard(root, [pin]);
    try {
      await assert.rejects(import(pathToFileURL(changed).href), /changed|Changed/);
      assert.equal(existsSync(marker), false);
    } finally {
      changedHook.deregister();
    }
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("CLI has no reduced-domain override and requires the candidate/argument cohort", () => {
  assert.throws(() => parseArguments(["--domain", "tiny"]), /Unknown/);
  assert.throws(() => parseArguments([]), /cohort/);
  assert.deepEqual(parseArguments(["--cohort", "cohort.json", "--out", "report.json"]),
    { cohort: "cohort.json", out: "report.json" });
  assert.deepEqual(FULL_DOMAIN, { inputCodeMin: 0, inputCodeMax: 64, stepCode: 1 / 64,
    spanMin: 32, spanMax: 224, scales: [1, 2], positions: [0.25, 0.5], poses: ["active", "receded"] });
});
