/**
 * W28's non-D candidate read, descended from W27c G1d/g1d-run.ts.
 * The body mask, OKLab arithmetic, target-byte checks, real-adapter refusal and
 * two-capture repeat check are unchanged. Admission happens before native PNGs
 * or browser pages; the G2 checking read is deliberately not a mode of this fit.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { componentRegion } from "../../src/component-region";
import { captureIntegrityRefusal } from "../../src/capture-integrity";
import { decodePng, linearLuminance } from "../../src/image";
import { srgbByteToOklab, oklabDistance, oklabChroma } from "../../src/color";
import { oklabDeltaE } from "../../src/metrics/perceptual";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../../renderer-webgpu/src/material";
import { mergeMaterialProfiles } from "../../../platform-web/src/color-scheme";
import { admitFitRows } from "./admission";
import { launch, here, pkg, repo } from "./browser";

const json = (path: string): any => JSON.parse(readFileSync(path, "utf8"));
const sha = (bytes: string | Buffer): string => createHash("sha256").update(bytes).digest("hex");
const canonical = (v: any): any => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object"
    ? Object.fromEntries(Object.keys(v).sort().map((key) => [key, canonical(v[key])])) : v;
const arg = (name: string, fallback?: string): string => {
  const i = process.argv.indexOf(`--${name}`);
  const value = i < 0 ? fallback : process.argv[i + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};
const label = arg("label");
const tier = arg("renderer", "webgpu");
if (tier !== "webgpu" && tier !== "css") throw new Error("Unknown renderer");
const scheme = arg("scheme");
if (scheme !== "light" && scheme !== "dark") throw new Error("Unknown scheme");
const policy = arg("policy", "standard");
const partition = json(resolve(here, "partition.json"));
const holdout = new Set<string>(partition.holdout);
const cells = partition.rows.filter((r: any) => r.scheme === scheme && r.a11yMode === policy);
admitFitRows(cells, holdout);
if (cells.length === 0) throw new Error("Empty fit population");
const mechanism = json(resolve(here, "mechanism-table.json"));
if (mechanism.passes !== true) throw new Error("The input check did not pass; fitting is refused");
const candidateFile = resolve(arg("patch"));
const candidate = json(candidateFile);
const baseline = json(resolve(here, "../2026-09-14-w27c-g1d/fitted-endpoint.json"));
const baseMatrix = json(resolve(here, "../2026-09-14-w27c-g1d/frozen-checking-matrix.json"));
const baseRows = new Map<string, any>(baseMatrix.rows.map((r: any) => [`${r.profile}/${r.scene}`, r]));
const active = json(resolve(pkg, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`));
const activeResolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active.patch);
if (sha(JSON.stringify(canonical(activeResolved))) !== baseline.profiles[scheme].activeSha256 ||
  active.resolvedMaterialSha256 !== baseline.profiles[scheme].activeRecordedFingerprint) {
  throw new Error("Active profile drift (X11)");
}
const patch = candidate[scheme];
const expected = mergeMaterialProfiles(active.patch, patch);
const inactiveSha256 = sha(JSON.stringify(canonical(withMaterialOverrides(activeResolved, patch))));
const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const output = resolve(here, "sweep-matrices", `${label}.json`);
if (existsSync(output)) throw new Error(`Refusing to replace ${output}`);
mkdirSync(dirname(output), { recursive: true });
const instrumentSha256 = sha(readFileSync(resolve(here, "fit-read.ts")));
const rows: any[] = [];
const run = await launch(label);
const record = () => writeFileSync(output, `${JSON.stringify({
  gate: "W28 G1 / claims §5.145", label, renderer: tier,
  patchSha256: sha(JSON.stringify(candidate)), inactiveSha256,
  activeSha256: baseline.profiles[scheme].activeSha256,
  instrumentSha256, partitionSha256: sha(readFileSync(resolve(here, "partition.json"))),
  machineAccessibility: run.machineAccessibility, engineVersion: run.browser.version(), rows,
}, null, 2)}\n`);
try {
  for (const cell of cells) {
    admitFitRows([cell], holdout);
    const nativeBase = baseRows.get(cell.cell);
    const nativePath = nativeBase?.nativePath ?? resolve(repo, "apps/reference-apple/fixtures", cell.nativeFile);
    const nativeBytes = readFileSync(nativePath);
    if (nativeBase !== undefined && sha(nativeBytes) !== nativeBase.nativeSha256) {
      throw new Error(`${cell.cell}: G1d target bytes changed`);
    }
    const native = decodePng(nativeBytes);
    const scene = matrix.scenes.find((s: any) => s.id === cell.scene);
    const background = readFileSync(resolve(repo, "apps/reference-apple/fixtures/backgrounds",
      `${scene.background}@${cell.scale}x.png`));
    if (nativeBase !== undefined && sha(background) !== nativeBase.backgroundSha256) {
      throw new Error(`${cell.cell}: backdrop is not G1d's committed raster`);
    }
    const region = componentRegion(matrix.components[scene.component], { canvas: matrix.canvas,
      scale: cell.scale, width: native.width, height: native.height });
    const context = await run.browser.newContext({ viewport: matrix.canvas,
      deviceScaleFactor: cell.scale, colorScheme: scheme });
    await context.addInitScript(({ activePatch, inactivePatch, accessibility }) => {
      window.__vitreaMaterialProfile = activePatch;
      window.__vitreaRecededMaterialProfile = inactivePatch;
      window.__vitreaAccessibilityOverrides = accessibility;
    }, { activePatch: active.patch, inactivePatch: patch,
      accessibility: { reducedTransparency: policy !== "standard",
        increasedContrast: policy === "increased-contrast", reducedMotion: false } });
    let first: Buffer | undefined;
    let report: any;
    try {
      for (let repeat = 0; repeat < 2; repeat++) {
        const page = await context.newPage();
        await page.goto(`${run.url}/index.html?scene=${cell.scene}&renderer=${tier}&scale=${cell.scale}&frames=16`);
        await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", { state: "attached" });
        const failure = await page.getAttribute("html", "data-scene-error");
        if (failure !== null) throw new Error(`${cell.cell}: ${failure}`);
        report = await page.evaluate(() => window.__vitreaCalibration.report);
        const refused = captureIntegrityRefusal(report, { canvas: matrix.canvas, scale: cell.scale });
        if (refused !== undefined) throw new Error(`${cell.cell}: ${refused}`);
        if (JSON.stringify(report.materialProfile) !== JSON.stringify(expected)) {
          throw new Error(`${cell.cell}: page applied another endpoint`);
        }
        if (report.groups.some((g: any) => g.state?.activeRenderer !== tier) ||
          (tier === "webgpu" && (!report.adapter.ok || report.adapter.isFallback !== false))) {
          throw new Error(`${cell.cell}: declared hardware tier did not draw`);
        }
        const png = await page.locator("#stage").screenshot({ animations: "disabled" });
        if (first !== undefined && !first.equals(png)) throw new Error(`${cell.cell}: nondeterministic capture`);
        first = png;
        await page.close();
      }
    } finally { await context.close(); }
    const capture = resolve(run.scratch, label, cell.profile, `${cell.scene}.png`);
    mkdirSync(dirname(capture), { recursive: true });
    writeFileSync(capture, first!);
    const web = decodePng(first!);
    if (web.width !== native.width || web.height !== native.height) throw new Error("Capture dimensions differ");
    const wy = linearLuminance(web);
    const ny = linearLuminance(native);
    let n = 0, w = 0, y = 0, w2 = 0, y2 = 0, de = 0, wc = 0, nc = 0;
    for (let i = 0; i < wy.length; i++) {
      if (region.signedDistancePx[i]! > -6 * cell.scale) continue;
      n++; w += wy[i]!; y += ny[i]!; w2 += wy[i]! ** 2; y2 += ny[i]! ** 2;
      const j = i * 4;
      const wl = srgbByteToOklab(web.data[j]!, web.data[j + 1]!, web.data[j + 2]!);
      const nl = srgbByteToOklab(native.data[j]!, native.data[j + 1]!, native.data[j + 2]!);
      de += oklabDistance(wl, nl); wc += oklabChroma(wl); nc += oklabChroma(nl);
    }
    const row = { ...cell, state: "inactive", scored: false, repeats: 2,
      capture, captureSha256: sha(first!), nativePath, nativeSha256: sha(nativeBytes),
      backgroundSha256: sha(background), nativeAttestation: nativeBase?.nativeAttestation ?? null,
      adapter: report.adapter, actualGroups: report.groups, geometry: report.surfaces,
      deltaE: oklabDeltaE(web, native), body: { n, webY: w / n, nativeY: y / n,
        webSD: Math.sqrt(Math.max(0, w2 / n - (w / n) ** 2)),
        nativeSD: Math.sqrt(Math.max(0, y2 / n - (y / n) ** 2)),
        webChroma: wc / n, nativeChroma: nc / n, deltaE: de / n } };
    rows.push(row); record();
    console.log(`${label} ${rows.length}/${cells.length} ${cell.cell} bodyDE=${row.body.deltaE.toFixed(6)}`);
  }
} finally {
  record();
  await run.browser.close();
  await run.server.close();
}
