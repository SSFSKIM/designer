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
import { captureIntegrityRefusal } from "../src/capture-integrity";
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
const renderer = arg("renderer", "webgpu");
if (renderer !== "webgpu" && renderer !== "css") throw new Error("Unknown renderer");
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
const sourceSha256 = Object.fromEntries([
  "packages/renderer-webgpu/src/material.ts", "packages/renderer-webgpu/src/wgsl/optics.ts",
  "packages/platform-web/src/root.ts", "packages/platform-web/src/optics.ts",
  "packages/platform-web/src/receded-profile.ts", "packages/calibration/web/scene.ts",
  "packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json",
  "packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json",
].map((file) => [file, sha(readFileSync(resolve(repo, file)))]));
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
  gate: "W27c G1 / claims §5.130", label, renderer, sets, patch,
  engineVersion: browser.version(), sourceSha256,
  patchSha256: sha(JSON.stringify(patch)), sceneSpecSha256: sha(JSON.stringify(matrix)),
  definitions: { deltaE: "Full-canvas mean per-pixel OKLab distance, canonical oklabDeltaE",
    body: "Declared union eroded 6 CSS px, linear Rec.709 Y, population SD",
    bodyDeltaE: "Mean per-pixel OKLab distance over the same eroded body",
    scale: "Device pixels per CSS px; accessibility evidence is 1x only",
    geometry: "How the page was actually framed, read back per row: the viewport is the " +
      "declared matrix canvas, and a row exists only where the page reported no problems " +
      "and agreed with the declaration on canvas, requested scale and devicePixelRatio" },
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
    /*
     * The viewport is the declared canvas exactly, never a convenient larger window.
     *
     * The renderer cover-fits the backdrop texture to the VIEWPORT (web/scene.ts's
     * viewport integrity note), so a window of another size maps the raster onto the
     * screen differently from the `<img>` the page composites and the glass refracts
     * pixels that are not the ones behind it. This driver's first sweep ran 800x600
     * around a 320x200 scene and measured a differently framed backdrop throughout;
     * scripts/capture-web.ts sets the same viewport for the same reason, and fitting
     * evidence is bound by the production contract rather than a looser one.
     */
    const context = await browser.newContext({
      viewport: { width: matrix.canvas.width, height: matrix.canvas.height },
      deviceScaleFactor: c.scale, colorScheme: profile.colorScheme });
    await context.addInitScript(({ active, receded, accessibility }) => {
      window.__vitreaMaterialProfile = active;
      window.__vitreaRecededMaterialProfile = receded;
      window.__vitreaAccessibilityOverrides = accessibility;
    }, { active: materialDoc.patch, receded: selectedPatch, accessibility: a11y });
    const name = inactiveId(c.scene);
    const nativeBytes = readFileSync(resolve(fixtures, c.profile, `${name}.png`));
    if (sha(nativeBytes) !== c.hashes.inactive) throw new Error("Recovered fixture hash changed");
    const backgroundBytes = readFileSync(resolve(fixtures, "backgrounds", `${scene.background}@${c.scale}x.png`));
    if (sha(backgroundBytes) !== c.hashes.background) throw new Error("Paired background hash changed");
    const native = decodePng(nativeBytes);
    const region = componentRegion(matrix.components[scene.component] as DeclaredComponent, {
      canvas: matrix.canvas, scale: c.scale, width: native.width, height: native.height,
    });
    let first: Buffer | undefined;
    let report: any;
    const count = process.argv.includes("--repeat") ? 2 : 1;
    for (let run = 0; run < count; run++) {
      const page = await context.newPage();
      await page.goto(`http://localhost:${port}/index.html?scene=${name}&renderer=${renderer}&scale=${c.scale}&frames=8`);
      await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", { state: "attached" });
      const failure = await page.getAttribute("html", "data-scene-error");
      if (failure !== null) throw new Error(failure);
      report = await page.evaluate(() => window.__vitreaCalibration.report);
      /*
       * A ready page is not a valid capture. The page's own integrity checks — the
       * viewport against the canvas, devicePixelRatio against the requested scale,
       * the committed raster against both — are reported rather than thrown, so a
       * driver that does not read them measures whatever happened to render.
       */
      const refusal = captureIntegrityRefusal(report, { canvas: matrix.canvas, scale: c.scale });
      if (refusal !== undefined) throw new Error(`${c.profile}/${name}: ${refusal}`);
      if (JSON.stringify(report.materialProfile) !==
          JSON.stringify(mergeMaterialProfiles(materialDoc.patch, selectedPatch))) {
        throw new Error("The page did not apply the declared inactive endpoint");
      }
      if ((renderer === "webgpu" && (!report.adapter.ok || report.adapter.isFallback !== false)) ||
          report.groups.some((g: any) => g.state?.activeRenderer !== renderer)) {
        throw new Error(`Capture did not draw on its declared tier: ${JSON.stringify(report)}`);
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
    /*
     * The two images are indexed by the same offsets below, so a size disagreement
     * would not be a blur — it would silently pair each web pixel with a native one
     * somewhere else. Checked here rather than assumed from the viewport above.
     */
    if (web.width !== native.width || web.height !== native.height ||
        web.width !== report.pixelSize[0] || web.height !== report.pixelSize[1]) {
      throw new Error(`${c.profile}/${name}: the capture is ${web.width}x${web.height} px where ` +
        `the native fixture is ${native.width}x${native.height} and the page reports ` +
        `${report.pixelSize[0]}x${report.pixelSize[1]}`);
    }
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
      // What actually framed this capture, from the page rather than from what the
      // driver asked for. A row that cannot say how it was framed cannot be read
      // beside one that can — which is the whole reason the first sweep was void.
      geometry: { viewport: matrix.canvas, canvas: report.canvas, pixelSize: report.pixelSize,
        requestedScale: report.requestedScale, devicePixelRatio: report.devicePixelRatio,
        background: report.background, capturedPixels: [web.width, web.height] },
      problems: report.problems, diagnostics: report.diagnostics,
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
