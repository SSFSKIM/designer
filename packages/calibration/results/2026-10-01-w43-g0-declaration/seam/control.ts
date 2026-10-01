/**
 * The byte-identity proof's sensitivity control (W43 G0 (f)).
 *
 *   cd packages/calibration && npx tsx results/2026-10-01-w43-g0-declaration/seam/control.ts
 *
 * Byte identity alone would also hold if candidate mode silently drew the shipped default
 * document, which is the 0.5 material too. So this control perturbs two pieces of the scratch
 * candidate and checks that the pixels follow the candidate, piece by piece:
 * - `receded.dark`: `optics.regular.tintAlpha` 0.89 -> 0.80, its digest re-sealed;
 * - the CSS mapping: `blurSigmaScale` 2.2 -> 2.6 in both active documents.
 * Declared expectation, against `prove.ts`'s strict-runtime-pose captures at 1x: on the
 * WebGPU tier a cell differs exactly when it is a dark inactive scene, the only endpoint
 * moved; on the CSS tier every structured-backdrop cell (photo, checkerboard, impulse)
 * differs, through the mapping; the uniform dark-solid cells on the CSS tier are reported
 * without an expectation, because blurring a uniform backdrop harder can leave it unchanged.
 * Writes `control.txt`.
 */

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch } from "@vitrea/renderer-webgpu";

import { cssTierMappingSha256, resolvedDigest } from "../../../scripts/candidate-document";

const HERE = dirname(fileURLToPath(import.meta.url));
const PACKAGE = resolve(HERE, "../../..");
const SOURCE = join(HERE, "scratch-candidate");
const PROOF = process.env["W43_SEAM_SCRATCH"] ?? "/tmp/w43-g0-seam";
const WORK = "/tmp/w43-g0-seam-control";
const sample = JSON.parse(readFileSync(join(HERE, "sample.json"), "utf8")) as { scenes: string[] };

rmSync(WORK, { recursive: true, force: true });
mkdirSync(join(WORK, "candidate"), { recursive: true });
const read = (slot: string) =>
  JSON.parse(readFileSync(join(SOURCE, `${slot}.json`), "utf8")) as Record<string, any>;
const docs: Record<string, Record<string, any>> = Object.fromEntries(
  ["active.light", "active.dark", "receded.light", "receded.dark"].map((s) => [s, read(s)]));
docs["active.light"]!["cssTierMapping"]["blurSigmaScale"] = 2.6;
docs["active.dark"]!["cssTierMapping"]["blurSigmaScale"] = 2.6;
docs["receded.dark"]!["patch"]["optics"]["regular"]["tintAlpha"] = 0.8;
docs["receded.dark"]!["resolvedMaterialSha256"] = resolvedDigest(withMaterialOverrides(
  withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, docs["active.dark"]!["patch"] as MaterialProfilePatch),
  docs["receded.dark"]!["patch"] as MaterialProfilePatch));
const endpoints: Record<string, { path: string; sha256: string }> = {};
for (const [slot, doc] of Object.entries(docs)) {
  const text = `${JSON.stringify(doc, null, 2)}\n`;
  writeFileSync(join(WORK, "candidate", `${slot}.json`), text);
  endpoints[slot] = { path: `${slot}.json`, sha256: createHash("sha256").update(text).digest("hex") };
}
const declaration = JSON.parse(readFileSync(join(SOURCE, "candidate.json"), "utf8")) as Record<string, unknown>;
declaration["name"] = "apple-macos-27.0-glass0.25-w43-g0-scratch-perturbed";
declaration["endpoints"] = endpoints;
declaration["cssTierMappingSha256"] = cssTierMappingSha256(docs["active.light"]!["cssTierMapping"]);
const candidate = join(WORK, "candidate", "candidate.json");
writeFileSync(candidate, `${JSON.stringify(declaration, null, 2)}\n`);

const sha = (path: string) => existsSync(path)
  ? createHash("sha256").update(readFileSync(path)).digest("hex") : null;
const lines = [`W43 G0 (f) sensitivity control, ${new Date().toISOString()}`];
let wrong = 0;
for (const scheme of ["light", "dark"] as const) {
  for (const tier of ["webgpu", "css"] as const) {
    const out = join(WORK, "captures", `${scheme}-1x-${tier}`);
    const run = spawnSync("npx", ["tsx", "scripts/capture-web.ts", ...sample.scenes, "--renderer", tier,
      "--color-scheme", scheme, "--scale", "1", "--out", out, "--candidate-document", candidate],
    { cwd: PACKAGE, encoding: "utf8" });
    if (run.status !== 0) {
      lines.push(`capture ${scheme} ${tier} exited ${String(run.status)}: ${run.stderr.slice(-400)}`);
      wrong += 1;
      continue;
    }
    for (const scene of sample.scenes) {
      const strict = sha(join(PROOF, "strict-runtime-pose", `${scheme}-1x-${tier}`, scene, `${scene}__${tier}.png`));
      const perturbed = sha(join(out, scene, `${scene}__${tier}.png`));
      const differs = strict !== perturbed;
      const inactive = scene.includes("__inactive");
      const expected = tier === "webgpu"
        ? (scheme === "dark" && inactive ? "differ" : "identical")
        : scene.startsWith("dark-solid") ? "(none)" : "differ";
      const ok = strict !== null && perturbed !== null &&
        (expected === "(none)" || (expected === "differ") === differs);
      if (!ok) wrong += 1;
      lines.push(`${ok ? "ok   " : "WRONG"} ${scheme} 1x ${tier} ${scene}: expected ${expected}, ` +
        `observed ${differs ? "differ" : "identical"}`);
    }
  }
}
lines.push(`wrong verdicts: ${wrong}`);
writeFileSync(join(HERE, "control.txt"), `${lines.join("\n")}\n`);
console.log(lines.join("\n"));
process.exitCode = wrong === 0 ? 0 : 1;
