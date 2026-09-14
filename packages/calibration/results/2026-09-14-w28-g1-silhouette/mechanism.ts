/**
 * W28 G1's INPUT check, before any response knot changes (claims §5.145).
 *
 * The population and expected numbers are G0's committed declaration. Native
 * fixture PNGs are never opened: a holdout's input is not its output. Every page
 * uses the canonical raster at the fixture's declared pixel size; no matrix row
 * is written. The active profile is patched in memory for this counterfactual,
 * never on disk, and neither pose's response rows are refitted here.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { decodePng } from "../../src/image";
import { componentRegion, placeComponent } from "../../src/component-region";
import { captureIntegrityRefusal } from "../../src/capture-integrity";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../../renderer-webgpu/src/material";
import { recededMaterialProfile } from "../../../platform-web/src/receded-profile";
import { admitSelection } from "./admission";
import { launch, here, pkg, repo } from "./browser";

const json = (path: string): any => JSON.parse(readFileSync(path, "utf8"));
const canonical = (v: any): any => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object"
    ? Object.fromEntries(Object.keys(v).sort().map((key) => [key, canonical(v[key])])) : v;
const sha = (data: string | Buffer): string => createHash("sha256").update(data).digest("hex");
const g0 = resolve(here, "../2026-09-14-w28-g0-abscissa");
const population = json(resolve(g0, "population.json"));
const expected = new Map<string, any>(json(resolve(g0, "per-cell.json")).rows.map((r: any) => [r.id, r]));
const baseline = json(resolve(here, "../2026-09-14-w27c-g1d/fitted-endpoint.json"));
const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const args = process.argv.slice(2);
const tier = args[args.indexOf("--renderer") + 1];
if (tier !== "webgpu" && tier !== "css") throw new Error("Name --renderer webgpu or css");
const labelIndex = args.indexOf("--label");
const label = labelIndex < 0 ? `mechanism-${tier}` : args[labelIndex + 1]!;
const limitIndex = args.indexOf("--limit");
const limit = limitIndex < 0 ? Infinity : Number(args[limitIndex + 1]);
const output = resolve(here, `${label}.json`);
if (existsSync(output)) throw new Error(`Refusing to overwrite ${output}`);

const active: Record<string, any> = {};
for (const scheme of ["light", "dark"] as const) {
  active[scheme] = json(resolve(pkg, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`));
  const resolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active[scheme].patch);
  if (sha(JSON.stringify(canonical(resolved))) !== baseline.profiles[scheme].activeSha256) {
    throw new Error(`${scheme}: active material moved (X11)`);
  }
  const { backdropToneAbscissa: _abscissa, ...rest } = recededMaterialProfile[scheme] as any;
  if (JSON.stringify(rest) !== JSON.stringify(baseline.patch[scheme])) {
    throw new Error(`${scheme}: response rows moved before the mechanism check`);
  }
}
for (const row of population.rows) admitSelection(row.scene);
const sceneIndex = args.indexOf("--scene");
const sceneFilter = sceneIndex < 0 ? undefined : args[sceneIndex + 1];
const cells = population.rows.filter((r: any) => r.bed === "canonical" &&
  (sceneFilter === undefined || r.scene === sceneFilter)).slice(0, limit);
const aliases = population.rows.filter((r: any) => r.bed === "w9").map((r: any) => ({
  id: r.id, canonicalId: `canonical/${r.profile}/${r.scene}`,
  reason: "The W9 id has the same declared geometry and committed raster as its canonical counterpart; its native output is not consumed.",
}));
const instrumentSha256 = sha(readFileSync(resolve(here, "mechanism.ts")));
const run = await launch(label);
const rows: any[] = [];
const record = () => writeFileSync(output, `${JSON.stringify({
  gate: "W28 G1 / claims §5.145", kind: "input-only; not a fit or holdout output read",
  repositoryHead: execFileSync("git", ["-C", repo, "rev-parse", "HEAD"], { encoding: "utf8" }).trim(),
  tier, limit: Number.isFinite(limit) ? limit : null, engineVersion: run.browser.version(),
  machineAccessibility: run.machineAccessibility,
  populationSha256: sha(readFileSync(resolve(g0, "population.json"))),
  expectedSha256: sha(readFileSync(resolve(g0, "per-cell.json"))),
  instrumentSha256,
  aliases, rows,
}, null, 2)}\n`);
try {
  for (const c of cells) {
    const target = expected.get(c.id);
    const background = readFileSync(resolve(repo, c.background));
    if (sha(background) !== json(resolve(g0, "inputs.json")).sha256[c.background]) {
      throw new Error(`${c.id}: background bytes differ from G0`);
    }
    const context = await run.browser.newContext({ viewport: matrix.canvas,
      deviceScaleFactor: c.scale, colorScheme: c.scheme });
    await context.addInitScript(({ patch, receded, a11y }) => {
      window.__vitreaMaterialProfile = patch;
      window.__vitreaRecededMaterialProfile = receded;
      window.__vitreaAccessibilityOverrides = a11y;
    }, {
      patch: { ...active[c.scheme].patch, backdropToneAbscissa: { kind: "silhouette" } },
      receded: { ...baseline.patch[c.scheme], backdropToneAbscissa: { kind: "silhouette" } },
      a11y: { reducedTransparency: c.policy !== "standard",
        increasedContrast: c.policy === "increased-contrast", reducedMotion: false },
    });
    try {
      const page = await context.newPage();
      const started = performance.now();
      await page.goto(`${run.url}/index.html?scene=${c.scene}&renderer=${tier}&scale=${c.scale}&frames=16`);
      await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", { state: "attached" });
      const failure = await page.getAttribute("html", "data-scene-error");
      if (failure !== null) throw new Error(`${c.id}: ${failure}`);
      const report = await page.evaluate(() => window.__vitreaCalibration.report);
      if (report === undefined) throw new Error(`${c.id}: no capture report`);
      const refusal = captureIntegrityRefusal(report, { canvas: matrix.canvas, scale: c.scale });
      if (refusal !== undefined) throw new Error(`${c.id}: ${refusal}`);
      const placed = placeComponent(matrix.components[target.component], matrix.canvas);
      const geometryDifferences: any[] = [];
      report.surfaces.forEach((surface: any, index: number) => {
        const declared = placed[index]!;
        if (surface.bounds?.width !== declared.width || surface.bounds?.height !== declared.height ||
          surface.bounds?.x !== declared.left || surface.bounds?.y !== declared.top) {
          geometryDifferences.push({ surfaceId: surface.nodeId, actual: surface.bounds, declared });
          if (!target.flags.includes("interaction")) {
            throw new Error(`${c.id}: host geometry differs from G0: ` +
              JSON.stringify(geometryDifferences));
          }
        }
      });
      if (tier === "webgpu" && (!report.adapter.ok || report.adapter.isFallback !== false)) {
        throw new Error(`${c.id}: real GPU adapter was not proved`);
      }
      const raster = decodePng(background);
      const expectedSurfaces = placed.map((shape, index) => {
        const component = { kind: shape.kind, size: [shape.width, shape.height],
          radius: shape.radius, offset: [shape.left - Math.round((matrix.canvas.width - shape.width) / 2),
            shape.top - Math.round((matrix.canvas.height - shape.height) / 2)] };
        const region = componentRegion(component as any, { canvas: matrix.canvas, scale: c.scale,
          width: raster.width, height: raster.height });
        let sum = 0;
        for (let i = 0; i < region.silhouette.mask.length; i++) {
          if (region.silhouette.mask[i] === 0) continue;
          sum += (0.2126 * raster.data[i * 4]! + 0.7152 * raster.data[i * 4 + 1]! +
            0.0722 * raster.data[i * 4 + 2]!) / 255;
        }
        return { surfaceId: report.surfaces[index]!.nodeId, sampleCount: region.areaPx,
          encodedLuminance: sum / region.areaPx };
      });
      const capture = resolve(run.scratch, label, c.profile, `${c.scene}.png`);
      mkdirSync(dirname(capture), { recursive: true });
      await page.locator("#stage").screenshot({ path: capture, animations: "disabled" });
      rows.push({ id: c.id, profile: c.profile, scene: c.scene, scheme: c.scheme,
        pose: c.pose, policy: c.policy, scale: c.scale, component: target.component,
        flags: target.flags, geometryDifferences, expectedEncoded: target.predictors.encoded.silhouette,
        sourceEncoded: target.predictors.encoded.source,
        backgroundSha256: sha(background), pixelSize: report.pixelSize,
        surfaces: report.surfaces, expectedSurfaces, groups: report.groups, adapter: report.adapter,
        elapsedMs: performance.now() - started, capture });
      record();
      console.log(`${label} ${rows.length}/${cells.length} ${c.id}`);
    } finally { await context.close(); }
  }
} finally {
  record();
  await run.browser.close();
  await run.server.close();
}
