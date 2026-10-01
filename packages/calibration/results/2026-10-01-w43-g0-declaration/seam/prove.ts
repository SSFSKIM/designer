/**
 * The candidate path's byte-identity proof (W43 G0 (f)), over the sample `sample.json`
 * declares.
 *
 *   cd packages/calibration && npx tsx results/2026-10-01-w43-g0-declaration/seam/prove.ts
 *
 * Runs `capture-web` once per (scheme, tier, scale, mode) into a scratch tree, then compares
 * every cell's PNG between modes and writes `proof.json` (every cell's hashes, tier, adapter,
 * mode and drawn-material readout) and `proof.txt` (the verdict). Exit 1 on any cell that
 * breaks the rule or could not be compared honestly.
 */

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PACKAGE = resolve(HERE, "../../..");
const SCRATCH = process.env["W43_SEAM_SCRATCH"] ?? "/tmp/w43-g0-seam";

interface Sample {
  readonly schemes: readonly ("light" | "dark")[];
  readonly tiers: readonly ("webgpu" | "css")[];
  readonly scales: readonly number[];
  readonly modes: readonly Mode[];
  readonly scenes: readonly string[];
  readonly documents: Record<"light" | "dark", { readonly active: string; readonly receded: string }>;
  readonly candidate: string;
}
type Mode = "strict-runtime-pose" | "strict-recipe" | "candidate";

const sample = JSON.parse(readFileSync(join(HERE, "sample.json"), "utf8")) as Sample;
const sha = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");

function modeArgs(mode: Mode, scheme: "light" | "dark"): string[] {
  const docs = sample.documents[scheme];
  if (mode === "candidate") return ["--candidate-document", sample.candidate];
  return [
    "--material-profile", docs.active,
    ...(mode === "strict-recipe" ? ["--receded-profile", docs.receded] : []),
  ];
}

rmSync(SCRATCH, { recursive: true, force: true });
const log: string[] = [];
for (const scheme of sample.schemes) {
  for (const tier of sample.tiers) {
    for (const scale of sample.scales) {
      for (const mode of sample.modes) {
        const out = join(SCRATCH, mode, `${scheme}-${scale}x-${tier}`);
        const args = [
          "tsx", "scripts/capture-web.ts", ...sample.scenes,
          "--renderer", tier, "--color-scheme", scheme, "--scale", `${scale}`,
          "--out", out, ...modeArgs(mode, scheme),
        ];
        process.stderr.write(`capture ${mode} ${scheme} ${scale}x ${tier}\n`);
        const run = spawnSync("npx", args, { cwd: PACKAGE, encoding: "utf8" });
        log.push(`$ npx ${args.join(" ")}\nexit ${String(run.status)}\n${run.stdout}${run.stderr}`);
        if (run.status !== 0) process.stderr.write(`  exit ${String(run.status)}\n${run.stderr}\n`);
      }
    }
  }
}
writeFileSync(join(SCRATCH, "capture-log.txt"), log.join("\n"));

interface CellRecord {
  readonly scheme: string;
  readonly tier: string;
  readonly scale: number;
  readonly scene: string;
  readonly endpoint: string;
  readonly modes: Record<string, {
    readonly png: string | null;
    readonly renderer: string | null;
    readonly gpuAdapter: string | null;
    readonly deterministic: boolean | null;
    readonly materialMode: string | null;
    readonly material: unknown;
    readonly windowActivation: string | null;
    readonly problems: readonly string[];
  }>;
  readonly candidateEqualsRuntimePose: boolean;
  readonly candidateEqualsRecipe: boolean;
  readonly honest: boolean;
}

const cells: CellRecord[] = [];
for (const scheme of sample.schemes) {
  for (const tier of sample.tiers) {
    for (const scale of sample.scales) {
      for (const scene of sample.scenes) {
        const modes: CellRecord["modes"] = {};
        for (const mode of sample.modes) {
          const dir = join(SCRATCH, mode, `${scheme}-${scale}x-${tier}`, scene);
          const png = join(dir, `${scene}__${tier}.png`);
          const cellPath = join(dir, `cell__${tier}.json`);
          const reportPath = join(dir, `report__${tier}.json`);
          const cell = existsSync(cellPath) ? JSON.parse(readFileSync(cellPath, "utf8")) : undefined;
          const report = existsSync(reportPath) ? JSON.parse(readFileSync(reportPath, "utf8")) : undefined;
          modes[mode] = {
            png: existsSync(png) ? sha(readFileSync(png)) : null,
            renderer: cell?.renderer ?? null,
            gpuAdapter: cell?.gpuAdapter ?? null,
            deterministic: cell?.deterministic ?? null,
            materialMode: report?.page?.materialMode ?? null,
            material: report?.page?.material ?? null,
            windowActivation: report?.page?.windowActivation ?? null,
            problems: report?.problems ?? ["no report"],
          };
        }
        const all = Object.values(modes);
        const honest = all.every((m) =>
          m.png !== null && m.renderer === tier && m.problems.length === 0 &&
          m.deterministic === true &&
          (tier === "css" || (m.gpuAdapter !== null && !/^(software-fallback|unverified-class|unavailable)/.test(m.gpuAdapter))));
        cells.push({
          scheme, tier, scale, scene,
          endpoint: `${scene.includes("__inactive") ? "receded" : "active"}.${scheme}`,
          modes,
          candidateEqualsRuntimePose: modes["candidate"]!.png !== null &&
            modes["candidate"]!.png === modes["strict-runtime-pose"]!.png,
          candidateEqualsRecipe: modes["candidate"]!.png !== null &&
            modes["candidate"]!.png === modes["strict-recipe"]!.png,
          honest,
        });
      }
    }
  }
}

const failures = cells.filter((c) => !c.honest || !c.candidateEqualsRuntimePose);
const recipeDiffers = cells.filter((c) => !c.candidateEqualsRecipe);
const adapters = [...new Set(cells.flatMap((c) => Object.values(c.modes).map((m) => m.gpuAdapter)))];
const endpoints = [...new Set(cells.map((c) => c.endpoint))].sort();
writeFileSync(join(HERE, "proof.json"), `${JSON.stringify({ scratch: SCRATCH, cells }, null, 2)}\n`);
const lines = [
  `W43 G0 (f) candidate-path byte identity, ${new Date().toISOString()}`,
  `sample: ${sample.scenes.length} scenes x ${sample.schemes.length} schemes x ${sample.tiers.length} tiers x ` +
    `${sample.scales.length} scales = ${cells.length} cells, ${sample.modes.length} modes each`,
  `endpoints covered: ${endpoints.join(", ")}`,
  `adapters: ${adapters.map(String).join(" | ")}`,
  `candidate == strict-runtime-pose (the rule): ${cells.length - failures.length}/${cells.length}`,
  `candidate == strict-recipe (reported):       ${cells.length - recipeDiffers.length}/${cells.length}`,
  ...failures.map((c) => `FAIL ${c.scheme} ${c.scale}x ${c.tier} ${c.scene}: ` +
    (c.honest ? "bytes differ" : "not an honest comparison (fallback, problem, software adapter or missing)")),
  ...recipeDiffers.map((c) => `recipe differs: ${c.scheme} ${c.scale}x ${c.tier} ${c.scene}`),
  `verdict: ${failures.length === 0 ? "PASS" : "FAIL"}`,
];
writeFileSync(join(HERE, "proof.txt"), `${lines.join("\n")}\n`);
console.log(lines.join("\n"));
process.exitCode = failures.length === 0 ? 0 : 1;
