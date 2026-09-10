/**
 * W27c G1 runtime fitting instrument (claims §5.130). This reads only declared
 * calibration rows by default. Validation and holdout require an explicit set;
 * holdout also requires a frozen declaration file and creates a one-shot marker.
 * Matrices and PNGs are scratch output, never results/matrix.json.
 *
 * pnpm --filter @vitrea/calibration exec tsx results/2026-09-10-w27c-g1-run.ts \
 *   --config /tmp/patch.json --label candidate --out /tmp/w27c-g1
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";
import { createServer } from "vite";
import { componentRegion, type DeclaredComponent } from "../src/component-region";
import { decodePng, linearLuminance } from "../src/image";
import { oklabDeltaE } from "../src/metrics/perceptual";
import { srgbByteToOklab, oklabDistance } from "../src/color";
import { recededMaterialProfile } from "../../platform-web/src/receded-profile";
import { mergeMaterialProfiles } from "../../platform-web/src/color-scheme";

const pkg = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repo = resolve(pkg, "../..");
const arg = (name: string, fallback?: string): string => {
  const i = process.argv.indexOf(`--${name}`);
  const value = i < 0 ? fallback : process.argv[i + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};
const json = (file: string): any => JSON.parse(readFileSync(file, "utf8"));
const sha = (data: string | Buffer): string => createHash("sha256").update(data).digest("hex");
const out = resolve(arg("out"));
const label = arg("label");
const sets = arg("set", "calibration").split(",");
const scenePattern = new RegExp(arg("cells", "."));
const profilePattern = new RegExp(arg("profiles", "."));
const patch = process.argv.includes("--config") ? json(resolve(arg("config"))) : recededMaterialProfile;
const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const census = json(resolve(pkg, "results/2026-09-10-w27c-g0-recede.json"));
const manifest = json(resolve(repo, "apps/reference-apple/fixtures/manifest.json"));
const fixtures = resolve(repo, "apps/reference-apple/fixtures");
const minority = (c: any): boolean => c.profile === "apple-macos-26.5-2x-dark-standard" &&
  c.scene === "photo__capsule-button__rest";
const inactiveId = (id: string): string => id.replace("__rest", "__inactive")
  .replace("__pressed", "__inactive-pressed");
const role = (id: string): string => ["calibration", "validation", "holdout", "recorded"]
  .find((set) => matrix.split[set].includes(id)) ?? "unassigned";
const population = census.cells.filter((c: any) => sets.includes(role(c.scene)) &&
  scenePattern.test(c.scene) && profilePattern.test(c.profile) && !minority(c));
if (population.length === 0) throw new Error("Empty fitting population");
if (sets.includes("recorded")) throw new Error("Recorded interaction copies are not fitting evidence");
mkdirSync(out, { recursive: true });
const resultFile = resolve(out, `${label}.json`);
if (existsSync(resultFile)) throw new Error(`Refusing to replace ${resultFile}`);
if (sets.includes("holdout")) {
  const frozen = readFileSync(resolve(arg("frozen")), "utf8");
  if (JSON.stringify(JSON.parse(frozen).patch) !== JSON.stringify(patch)) {
    throw new Error("Holdout patch differs from frozen declaration");
  }
  writeFileSync(resolve(out, `holdout-spent-${sha(JSON.stringify(patch))}.json`),
    JSON.stringify({ label, startedAt: new Date().toISOString(), frozenSha256: sha(frozen) }), { flag: "wx" });
}
const rows: any[] = [];
const endpointAudit: any[] = [];
for (const c of population) {
  const p = manifest.profiles.find((p: any) => p.profileKey === c.profile);
  const f = p.fixtures.find((f: any) => f.sceneId === c.scene);
  const current = sha(readFileSync(resolve(fixtures, f.file)));
  const states = f.stateFrequencies ?? [];
  const majority = [...states].sort((a: any, b: any) => b.runs - a.runs)[0];
  endpointAudit.push({ profile: c.profile, scene: c.scene, scale: c.scale,
    historicalActiveSha256: c.hashes.active, currentActiveSha256: current,
    frequencySettled: f.frequencySettled ?? false,
    majoritySha256: majority?.sha256 ?? null,
    currentIsMajority: majority === undefined ? null : current === majority.sha256,
    historicalIsCurrent: c.hashes.active === current });
  if (majority !== undefined && majority.sha256 !== current) throw new Error("Current active file is not majority");
}
const record = (): void => writeFileSync(resultFile, JSON.stringify({
  gate: "W27c G1 / claims §5.130", label, sets, patch,
  patchSha256: sha(JSON.stringify(patch)), sceneSpecSha256: sha(JSON.stringify(matrix)),
  definitions: { deltaE: "Full-canvas mean per-pixel OKLab distance, canonical oklabDeltaE",
    body: "Declared union eroded 6 CSS px, linear Rec.709 Y, population SD",
    bodyDeltaE: "Mean per-pixel OKLab distance over the same eroded body",
    scale: "Device pixels per CSS px; accessibility evidence is 1x only" },
  endpointAudit, rows,
}, null, 2) + "\n");
const port = Number(arg("port", "5197"));
const server = await createServer({ configFile: resolve(pkg, "web/vite.config.ts"),
  server: { port, strictPort: true } });
await server.listen();
const browser = await chromium.launch({ channel: "chromium", headless: true,
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"] });
try {
  for (const c of population) {
    const scene = matrix.scenes.find((s: any) => s.id === c.scene);
    const profile = manifest.profiles.find((p: any) => p.profileKey === c.profile);
    const selectedPatch = patch.light !== undefined && patch.dark !== undefined
      ? patch[profile.colorScheme] : patch;
    const materialDoc = json(resolve(pkg, "profiles", profile.colorScheme === "dark"
      ? "apple-macos-26.5-1x-dark-standard.json" : "apple-macos-26.5-1x-light-standard.json"));
    const a11y = { reducedTransparency: profile.a11yMode !== "standard",
      increasedContrast: profile.a11yMode === "increased-contrast", reducedMotion: false };
    const context = await browser.newContext({ viewport: { width: 800, height: 600 },
      deviceScaleFactor: c.scale, colorScheme: profile.colorScheme });
    await context.addInitScript(({ active, receded, accessibility }) => {
      window.__vitreaMaterialProfile = active;
      window.__vitreaRecededMaterialProfile = receded;
      window.__vitreaAccessibilityOverrides = accessibility;
    }, { active: materialDoc.patch, receded: selectedPatch, accessibility: a11y });
    const name = inactiveId(c.scene);
    const native = decodePng(readFileSync(resolve(fixtures, c.profile, `${name}.png`)));
    const region = componentRegion(matrix.components[scene.component] as DeclaredComponent, {
      canvas: matrix.canvas, scale: c.scale, width: native.width, height: native.height,
    });
    let first: Buffer | undefined;
    let report: any;
    const count = process.argv.includes("--repeat") ? 2 : 1;
    for (let run = 0; run < count; run++) {
      const page = await context.newPage();
      await page.goto(`http://localhost:${port}/index.html?scene=${name}&renderer=webgpu&scale=${c.scale}&frames=8`);
      await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", { state: "attached" });
      const failure = await page.getAttribute("html", "data-scene-error");
      if (failure !== null) throw new Error(failure);
      report = await page.evaluate(() => window.__vitreaCalibration.report);
      if (JSON.stringify(report.materialProfile) !==
          JSON.stringify(mergeMaterialProfiles(materialDoc.patch, selectedPatch))) {
        throw new Error("The page did not apply the declared inactive endpoint");
      }
      if (!report.adapter.ok || report.adapter.isFallback ||
          report.groups.some((g: any) => g.state?.activeRenderer !== "webgpu")) {
        throw new Error(`Not a hardware WebGPU capture: ${JSON.stringify(report)}`);
      }
      const png = await page.locator("#stage").screenshot({ animations: "disabled" });
      if (first !== undefined && !first.equals(png)) throw new Error(`Nondeterministic ${c.profile}/${name}`);
      first = png;
      await page.close();
    }
    await context.close();
    const capture = resolve(out, label, c.profile, `${name}.png`);
    mkdirSync(dirname(capture), { recursive: true });
    writeFileSync(capture, first!);
    const web = decodePng(first!);
    const wy = linearLuminance(web), ny = linearLuminance(native);
    let n = 0, w = 0, nY = 0, w2 = 0, n2 = 0, de = 0;
    for (let i = 0; i < wy.length; i++) {
      if (region.signedDistancePx[i]! > -6 * c.scale) continue;
      n++; w += wy[i]!; nY += ny[i]!; w2 += wy[i]! ** 2; n2 += ny[i]! ** 2;
      const j = i * 4;
      de += oklabDistance(srgbByteToOklab(web.data[j]!, web.data[j+1]!, web.data[j+2]!),
        srgbByteToOklab(native.data[j]!, native.data[j+1]!, native.data[j+2]!));
    }
    const row = { profile: c.profile, scene: name, sourceScene: c.scene, set: role(c.scene), scale: c.scale,
      capture, captureSha256: sha(first!), nativeSha256: c.hashes.inactive,
      adapter: report.adapter, repeats: count, actualGroups: report.groups,
      deltaE: oklabDeltaE(web, native),
      body: { n, webY: w/n, nativeY: nY/n, webSD: Math.sqrt(Math.max(0,w2/n-(w/n)**2)),
        nativeSD: Math.sqrt(Math.max(0,n2/n-(nY/n)**2)), deltaE: de/n } };
    rows.push(row); record();
    console.log(`${label} ${c.profile} ${name} DE=${row.deltaE.mean.toFixed(5)} body=${row.body.webY.toFixed(5)}/${row.body.nativeY.toFixed(5)} SD=${row.body.webSD.toFixed(5)}/${row.body.nativeSD.toFixed(5)}`);
  }
} finally {
  await browser.close();
  await server.close();
}
