/** W28 G1 cost + input-only mip diagnostic. No native glass output is opened. */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { chromium } from "@playwright/test";
import { createServer } from "vite";
import { placeComponent } from "../../src/component-region";
import { requireHardwareAdapter } from "../../../renderer-webgpu/e2e/support";
import type { silhouetteCost, silhouettePyramidDiagnostic } from
  "../../../renderer-webgpu/e2e/fixtures/silhouette-evidence";
import { machinePreflight, here, repo } from "./browser";

const args = process.argv.slice(2);
if (args.includes("--help")) {
  console.log("Usage: pnpm --filter @vitrea/calibration exec tsx results/2026-09-14-w28-g1-silhouette/gpu-evidence.ts [--out gpu-evidence.json] [--rounds 96] [--warmup 24] [--port 5221]");
  process.exit(0);
}
const argument = (name: string, fallback: string) => {
  const i = args.indexOf(name);
  if (i < 0) return fallback;
  if (args[i + 1] === undefined) throw new Error(`Missing ${name} value`);
  return args[i + 1]!;
};
const output = resolve(here, argument("--out", "gpu-evidence.json"));
if (existsSync(output)) throw new Error(`Refusing to overwrite ${output}`);
const rounds = Number(argument("--rounds", "96"));
const warmup = Number(argument("--warmup", "24"));
const port = Number(argument("--port", "5221"));
if (![rounds, warmup, port].every(Number.isInteger) || rounds < 2 || warmup < 1 || port < 1024) {
  throw new Error("Invalid rounds, warmup or port");
}
const sha = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");
const matrix = JSON.parse(readFileSync(resolve(repo, "apps/reference-apple/scenes.json"), "utf8"));
const componentIds = ["rrect-sm", "rrect-md", "capsule-button"];
const shapes = componentIds.flatMap((id) => placeComponent(matrix.components[id], matrix.canvas)
  .map((shape) => ({ id, left: shape.left, top: shape.top,
    width: shape.width, height: shape.height, radius: shape.radius })));
const instrumentFiles = [
  "packages/calibration/results/2026-09-14-w28-g1-silhouette/gpu-evidence.ts",
  "packages/renderer-webgpu/e2e/fixtures/silhouette-evidence.ts",
  "packages/renderer-webgpu/src/renderer.ts",
  "packages/renderer-webgpu/src/silhouette-tone.ts",
  "packages/renderer-webgpu/src/wgsl/silhouette-tone.ts",
  "packages/renderer-webgpu/src/pyramid.ts",
  "packages/renderer-webgpu/src/pyramid-plan.ts",
  "packages/renderer-webgpu/src/material.ts",
];
const provenance = Object.fromEntries(instrumentFiles.map((file) =>
  [file, sha(readFileSync(resolve(repo, file)))]));
const machineAccessibility = machinePreflight("W28 GPU cost and analysis-mip input diagnostic");
const server = await createServer({
  configFile: resolve(repo, "packages/renderer-webgpu/e2e/vite.config.ts"),
  server: { port, strictPort: true },
});
await server.listen();
let browser: Awaited<ReturnType<typeof chromium.launch>> | undefined;
try {
  browser = await chromium.launch({ channel: "chromium", headless: false,
    args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"] });
  const page = await browser.newPage();
  page.on("pageerror", (error) => { throw error; });
  await page.goto(`http://localhost:${port}/e2e/fixtures/index.html`);
  await page.waitForSelector("html[data-vitrea-ready='1']");
  const adapter = await page.evaluate(() => window.vitrea.probe());
  requireHardwareAdapter(adapter);
  const bench = await page.evaluate(async (input) => {
    const path = "/e2e/fixtures/silhouette-evidence.ts";
    const module = await import(path) as { silhouetteCost: typeof silhouetteCost };
    return module.silhouetteCost(input);
  }, { canvas: matrix.canvas, rounds, warmup });
  if (bench.rows.some((row) => row.pyramidRebuilds !== 1)) {
    throw new Error("Not steady state: a cost row rebuilt its static source more than once");
  }
  const diagnostics = [];
  for (const background of ["checkerboard", "photo", "hc-text"]) for (const dpr of [1, 2]) {
    const path = `apps/reference-apple/fixtures/backgrounds/${background}@${dpr}x.png`;
    const bytes = readFileSync(resolve(repo, path));
    const result = await page.evaluate(async (input) => {
      const path = "/e2e/fixtures/silhouette-evidence.ts";
      const module = await import(path) as { silhouettePyramidDiagnostic: typeof silhouettePyramidDiagnostic };
      return module.silhouettePyramidDiagnostic(input);
    }, { pngDataUrl: `data:image/png;base64,${bytes.toString("base64")}`, dpr,
      // The broad non-D shapes already identify this input-only Jensen gap.
      shapes: shapes.filter((shape) => background !== "hc-text" || shape.id !== "rrect-sm") });
    diagnostics.push({ background, path, sha256: sha(bytes), ...result });
  }
  writeFileSync(output, JSON.stringify({
    gate: "W28 G1 / claims §5.145", kind: "cost and input-only mip diagnostic; no response fit",
    repositoryHead: execFileSync("git", ["-C", repo, "rev-parse", "HEAD"], { encoding: "utf8" }).trim(),
    command: process.argv, machineAccessibility, engineVersion: browser.version(), adapter, provenance,
    benchmark: bench,
    diagnosticMethod: "Unmodified production silhouette reducer, same full-resolution masks, bound to production pyramid mip 0 versus analysisLevel. This measures encoding after linear blur, not the legacy whole-source analysis shader.",
    diagnosticShapes: shapes,
    excludedDiagnostic: "hc-text/rrect-sm is a checking-set base; no diagnostic cell uses it.",
    diagnostics,
  }, null, 2) + "\n");
  console.log(JSON.stringify({ output, overheads: bench.differences,
    diagnostics: diagnostics.map((row) => ({ background: row.background, dpr: row.dpr,
      analysisLevel: row.analysisLevel, deltas: row.deltas })) }, null, 2));
} finally {
  await browser?.close();
  await server.close();
}
