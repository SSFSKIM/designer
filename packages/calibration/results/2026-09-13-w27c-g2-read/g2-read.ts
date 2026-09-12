/**
 * W27c G2's checking-bed read (claims §5.139): the frozen inactive endpoint of
 * §5.130 against the 26.5 checking bed, on the WebGPU tier.
 *
 * The instrument is `results/2026-09-10-w27c-g1-run.ts` with its population
 * changed and nothing else loosened: the same declared viewport, the same
 * fail-closed capture integrity, the same refusal of a page that did not apply
 * the declared endpoint, the same refusal of a fallback adapter or a tier that
 * demoted. What changes is where the cells come from. G1's driver walked the G0
 * census of recovered fixtures; this one walks the checking bed itself, against
 * the fixtures the sitting published (claims §5.136 §10, materialised at
 * `2026-09-13-w27c-g2-read/materialize.log`).
 *
 * Three rules this driver carries that the bound (`bound.json` clause 5) or the
 * brief imposes, and that are worth naming because they are refusals rather than
 * behaviour:
 *
 *   - **Nothing canonical is written.** The matrix goes to `--out`, the captures
 *     to `VITREA_WEB_CAPTURES` or `--out`, and `results/matrix.json` is never
 *     opened. No profile, golden or fixture moves.
 *   - **The spent holdout is not re-read.** Three of the bed's ids carry the
 *     `holdout` role from §5.130's frozen split. They are supplying and
 *     attestation cells here, excluded from the bound's scoring by name — and no
 *     vitrea-against-native distance is computed for them at all, so this read
 *     cannot be a second spending of a holdout cell under another name. Their
 *     fresh native readings are published (that is what a supplying cell is for)
 *     and `native-attestation.py` compares their bytes with the recovered ones.
 *   - **The native bytes are the sitting's.** For a `probe` cell the published
 *     fixture IS the sitting's plurality, so the two are the same file. For a
 *     bed id that already carried a `calibration` role the bundle still holds the
 *     recovered fixture, which this read must not overwrite, so the comparison
 *     reads the plurality PNG out of the sitting directly and says so per row.
 *
 * Usage:
 *   pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx \
 *     results/2026-09-13-w27c-g2-read/g2-read.ts --out /tmp/w27c-g2 --label checking
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";
import { createServer } from "vite";
import { captureIntegrityRefusal } from "../../src/capture-integrity";
import { componentRegion, type DeclaredComponent } from "../../src/component-region";
import { decodePng, linearLuminance } from "../../src/image";
import { oklabDeltaE } from "../../src/metrics/perceptual";
import { srgbByteToOklab, oklabDistance, oklabChroma } from "../../src/color";
import { recededMaterialProfile } from "../../../platform-web/src/receded-profile";
import { mergeMaterialProfiles } from "../../../platform-web/src/color-scheme";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");
const arg = (name: string, fallback?: string): string => {
  const i = process.argv.indexOf(`--${name}`);
  const value = i < 0 ? fallback : process.argv[i + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};
const json = (file: string): any => JSON.parse(readFileSync(file, "utf8"));
const sha = (data: string | Buffer | Uint8Array): string =>
  createHash("sha256").update(data).digest("hex");

const out = resolve(arg("out"));
const label = arg("label", "checking");
const renderer = arg("renderer", "webgpu");
if (renderer !== "webgpu" && renderer !== "css") throw new Error("Unknown renderer");
const scenePattern = new RegExp(arg("cells", "."));
const profilePattern = new RegExp(arg("profiles", "."));
const sitting = resolve(arg("sitting", process.env["VITREA_SITTING_ROOT"] ?? "/Users/new/vitrea-w27-26.5-run"));

const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const manifest = json(resolve(repo, "apps/reference-apple/fixtures/manifest.json"));
const fixtures = resolve(repo, "apps/reference-apple/fixtures");
const bedSpec = json(resolve(here, "../2026-09-11-w27c-g1b/checking-bed.json"));
const plurality = json(resolve(here, "plurality.json"));

/** Every id the bed declares, with the group(s) it belongs to and its role. */
const groupsOf = new Map<string, string[]>();
for (const group of bedSpec.groups) {
  for (const id of group.scenes) groupsOf.set(id, [...(groupsOf.get(id) ?? []), group.id]);
  for (const id of group.alsoCaptureActive ?? []) {
    groupsOf.set(id, [...(groupsOf.get(id) ?? []), `${group.id}-active`]);
  }
}
const role = (id: string): string =>
  ["calibration", "validation", "holdout", "recorded", "probe"]
    .find((set) => (matrix.split[set] ?? []).includes(id)) ?? "unassigned";
/*
 * The bound scores group D and nothing else (`bound.json` scope): the checking
 * cells, drawn from the 55 declared scenes that had no inactive counterpart, so
 * unspent by construction. `checkerboard__rrect-ml__inactive` is in groups B and
 * D both; it is read once and scored, which is what the declaration says.
 */
const checkingSet = new Set<string>(
  (bedSpec.groups.find((g: any) => g.id === "D")?.scenes ?? []) as string[],
);

/** Where a cell's native bytes live, and whether vitrea may be compared to them. */
function nativeFor(profileKey: string, sceneId: string): {
  path: string;
  source: "bundle" | "sitting";
  comparable: boolean;
} {
  const entry = manifest.profiles
    .find((p: any) => p.profileKey === profileKey)
    ?.fixtures.find((f: any) => f.sceneId === sceneId);
  if (entry !== undefined && entry.fixtureSet === "probe") {
    return { path: resolve(fixtures, entry.file), source: "bundle", comparable: true };
  }
  // Not published by this sitting: the bundle's copy is the recovered fixture of
  // §5.130 and must not be read as if it were this bed's. The sitting's own
  // plurality bytes are, so the row is read from there — except on a holdout id,
  // which is not compared at all.
  const cell = `${profileKey}/${sceneId}`;
  for (const pass of plurality.passes) {
    const tally = pass.cellTally[cell];
    if (tally === undefined) continue;
    const run = Object.entries(tally.perRunSha256).find(([, s]) => s === tally.pluralitySha256);
    if (run === undefined) continue;
    return {
      path: resolve(sitting, pass.dir, run[0], profileKey, `${sceneId}.png`),
      source: "sitting",
      comparable: role(sceneId) !== "holdout",
    };
  }
  throw new Error(`${cell}: neither the bundle nor the sitting holds this cell`);
}

interface Cell {
  profile: string;
  scene: string;
  scale: number;
  scheme: string;
  a11yMode: string;
}
const population: Cell[] = [];
for (const profile of manifest.profiles) {
  const scale = profile.profileKey.includes("-2x-") ? 2 : 1;
  for (const fixture of profile.fixtures) {
    if (!groupsOf.has(fixture.sceneId)) continue;
    if (!scenePattern.test(fixture.sceneId) || !profilePattern.test(profile.profileKey)) continue;
    if (role(fixture.sceneId) === "holdout") continue;
    population.push({
      profile: profile.profileKey,
      scene: fixture.sceneId,
      scale,
      scheme: profile.colorScheme,
      a11yMode: profile.a11yMode,
    });
  }
}
if (population.length === 0) throw new Error("Empty population");
population.sort((a, b) => `${a.profile}/${a.scene}`.localeCompare(`${b.profile}/${b.scene}`));

mkdirSync(out, { recursive: true });
const resultFile = resolve(out, `${label}.json`);
if (existsSync(resultFile)) throw new Error(`Refusing to replace ${resultFile}`);

const sourceSha256 = Object.fromEntries(
  [
    "packages/renderer-webgpu/src/material.ts",
    "packages/renderer-webgpu/src/wgsl/optics.ts",
    "packages/platform-web/src/root.ts",
    "packages/platform-web/src/optics.ts",
    "packages/platform-web/src/receded-profile.ts",
    "packages/calibration/web/scene.ts",
    "packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json",
    "packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json",
  ].map((file) => [file, sha(readFileSync(resolve(repo, file)))]),
);
/*
 * The endpoint this read is against, quoted from the frozen declaration rather
 * than recomputed: if the exported document had drifted from it, the resolved
 * SHA-256 below would not match and the run stops before its first capture.
 */
const frozen = json(resolve(pkg, "results/2026-09-10-w27c-g1-corrected-declaration.json"));
if (JSON.stringify(frozen.patch) !== JSON.stringify(recededMaterialProfile)) {
  throw new Error("The exported receded profile is not the frozen G1 endpoint");
}

const rows: any[] = [];
const record = (): void =>
  writeFileSync(
    resultFile,
    `${JSON.stringify(
      {
        gate: "W27c G2 read / claims §5.139",
        label,
        renderer,
        readAgainst: frozen.profiles,
        bed: "packages/calibration/results/2026-09-11-w27c-g1b/checking-bed.json",
        bound: "packages/calibration/results/2026-09-11-w27c-g1b/bound.json",
        sitting,
        engineVersion: browser.version(),
        sourceSha256,
        patchSha256: sha(JSON.stringify(recededMaterialProfile)),
        sceneSpecSha256: sha(JSON.stringify(matrix)),
        definitions: {
          deltaE: "Full-canvas mean per-pixel OKLab distance, canonical oklabDeltaE",
          bodyDeltaE: "Mean per-pixel OKLab distance over the declared union eroded 6 CSS px",
          body: "Declared union eroded 6 CSS px: linear Rec.709 Y mean and population SD, and mean per-pixel OKLab chroma",
          scale: "Device pixels per CSS px",
          geometry:
            "How the page was actually framed, read back per row: the viewport is the declared " +
            "matrix canvas, and a row exists only where the page reported no problems and agreed " +
            "with the declaration on canvas, requested scale and devicePixelRatio",
          notRead:
            "The three bed ids carrying §5.130's holdout role are captured by no row here: the " +
            "holdout is spent and this read does not produce a second vitrea-against-native " +
            "distance for one under another name",
        },
        rows,
      },
      null,
      2,
    )}\n`,
  );

const port = Number(arg("port", "5203"));
const server = await createServer({
  configFile: resolve(pkg, "web/vite.config.ts"),
  server: { port, strictPort: true },
});
await server.listen();
const browser = await chromium.launch({
  channel: "chromium",
  headless: true,
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
});
try {
  for (const c of population) {
    const scene = matrix.scenes.find((s: any) => s.id === c.scene);
    if (scene === undefined) throw new Error(`${c.scene}: not declared in scenes.json`);
    const profile = manifest.profiles.find((p: any) => p.profileKey === c.profile);
    const entry = profile.fixtures.find((f: any) => f.sceneId === c.scene);
    const inactive = scene.state === "inactive";
    const selectedPatch = inactive ? recededMaterialProfile[c.scheme] : undefined;
    const materialDoc = json(
      resolve(pkg, "profiles", c.scheme === "dark"
        ? "apple-macos-26.5-1x-dark-standard.json"
        : "apple-macos-26.5-1x-light-standard.json"),
    );
    const a11y = {
      reducedTransparency: c.a11yMode !== "standard",
      increasedContrast: c.a11yMode === "increased-contrast",
      reducedMotion: false,
    };
    const native = nativeFor(c.profile, c.scene);
    if (!native.comparable) continue;

    const context = await browser.newContext({
      viewport: { width: matrix.canvas.width, height: matrix.canvas.height },
      deviceScaleFactor: c.scale,
      colorScheme: c.scheme as "light" | "dark",
    });
    await context.addInitScript(
      ({ active, receded, accessibility }) => {
        window.__vitreaMaterialProfile = active;
        if (receded !== undefined) window.__vitreaRecededMaterialProfile = receded;
        window.__vitreaAccessibilityOverrides = accessibility;
      },
      { active: materialDoc.patch, receded: selectedPatch, accessibility: a11y },
    );
    const nativeBytes = readFileSync(native.path);
    const backgroundBytes = readFileSync(
      resolve(fixtures, "backgrounds", `${scene.background}@${c.scale}x.png`),
    );
    const nativeImage = decodePng(nativeBytes);
    const region = componentRegion(matrix.components[scene.component] as DeclaredComponent, {
      canvas: matrix.canvas,
      scale: c.scale,
      width: nativeImage.width,
      height: nativeImage.height,
    });
    let first: Buffer | undefined;
    let report: any;
    const count = process.argv.includes("--once") ? 1 : 2;
    for (let run = 0; run < count; run++) {
      const page = await context.newPage();
      await page.goto(
        `http://localhost:${port}/index.html?scene=${c.scene}&renderer=${renderer}&scale=${c.scale}&frames=8`,
      );
      await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", {
        state: "attached",
      });
      const failure = await page.getAttribute("html", "data-scene-error");
      if (failure !== null) throw new Error(`${c.profile}/${c.scene}: ${failure}`);
      report = await page.evaluate(() => window.__vitreaCalibration.report);
      const refusal = captureIntegrityRefusal(report, { canvas: matrix.canvas, scale: c.scale });
      if (refusal !== undefined) throw new Error(`${c.profile}/${c.scene}: ${refusal}`);
      const expected = inactive
        ? mergeMaterialProfiles(materialDoc.patch, selectedPatch)
        : materialDoc.patch;
      if (JSON.stringify(report.materialProfile) !== JSON.stringify(expected)) {
        throw new Error(`${c.profile}/${c.scene}: the page did not apply the declared endpoint`);
      }
      if (
        (renderer === "webgpu" && (!report.adapter.ok || report.adapter.isFallback !== false)) ||
        report.groups.some((g: any) => g.state?.activeRenderer !== renderer)
      ) {
        throw new Error(`${c.profile}/${c.scene}: did not draw on its declared tier`);
      }
      const png = await page.locator("#stage").screenshot({ animations: "disabled" });
      if (first !== undefined && !first.equals(png)) {
        throw new Error(`Nondeterministic ${c.profile}/${c.scene}`);
      }
      first = png;
      await page.close();
    }
    await context.close();
    const capture = resolve(
      process.env["VITREA_WEB_CAPTURES"] ?? resolve(out, label),
      c.profile,
      `${c.scene}.png`,
    );
    mkdirSync(dirname(capture), { recursive: true });
    writeFileSync(capture, first as Buffer);
    const web = decodePng(first as Buffer);
    if (
      web.width !== nativeImage.width ||
      web.height !== nativeImage.height ||
      web.width !== report.pixelSize[0] ||
      web.height !== report.pixelSize[1]
    ) {
      throw new Error(
        `${c.profile}/${c.scene}: the capture is ${web.width}x${web.height} px where the native ` +
          `fixture is ${nativeImage.width}x${nativeImage.height} and the page reports ` +
          `${report.pixelSize[0]}x${report.pixelSize[1]}`,
      );
    }
    const wy = linearLuminance(web);
    const ny = linearLuminance(nativeImage);
    let n = 0, w = 0, nY = 0, w2 = 0, n2 = 0, de = 0, wc = 0, nc = 0;
    for (let i = 0; i < wy.length; i++) {
      if (region.signedDistancePx[i]! > -6 * c.scale) continue;
      n++;
      w += wy[i]!;
      nY += ny[i]!;
      w2 += wy[i]! ** 2;
      n2 += ny[i]! ** 2;
      const j = i * 4;
      const webLab = srgbByteToOklab(web.data[j]!, web.data[j + 1]!, web.data[j + 2]!);
      const natLab = srgbByteToOklab(
        nativeImage.data[j]!, nativeImage.data[j + 1]!, nativeImage.data[j + 2]!,
      );
      de += oklabDistance(webLab, natLab);
      wc += oklabChroma(webLab);
      nc += oklabChroma(natLab);
    }
    const row = {
      profile: c.profile,
      scene: c.scene,
      scale: c.scale,
      scheme: c.scheme,
      a11yMode: c.a11yMode,
      state: scene.state,
      groups: groupsOf.get(c.scene),
      role: role(c.scene),
      scored: checkingSet.has(c.scene),
      capture,
      captureSha256: sha(first as Buffer),
      nativeSource: native.source,
      nativePath: native.path,
      nativeSha256: sha(nativeBytes),
      backgroundSha256: sha(backgroundBytes),
      // The native cell's own per-cell attestation, quoted from the manifest the
      // sitting wrote: the pose it proved, and the idle it was taken under.
      nativeAttestation: {
        presentedActive: entry.presentedActive ?? null,
        presentation: entry.presentation ?? null,
        hidIdleSeconds: entry.hidIdleSeconds ?? null,
        deterministic: entry.deterministic ?? null,
        frequencySettled: entry.frequencySettled ?? false,
        stateFrequencies: entry.stateFrequencies ?? null,
        identicalToBackground: entry.identicalToBackground ?? null,
      },
      adapter: report.adapter,
      repeats: count,
      actualGroups: report.groups,
      geometry: {
        viewport: matrix.canvas,
        canvas: report.canvas,
        pixelSize: report.pixelSize,
        requestedScale: report.requestedScale,
        devicePixelRatio: report.devicePixelRatio,
        background: report.background,
        capturedPixels: [web.width, web.height],
      },
      problems: report.problems,
      diagnostics: report.diagnostics,
      deltaE: oklabDeltaE(web, nativeImage),
      body: {
        n,
        webY: w / n,
        nativeY: nY / n,
        webSD: Math.sqrt(Math.max(0, w2 / n - (w / n) ** 2)),
        nativeSD: Math.sqrt(Math.max(0, n2 / n - (nY / n) ** 2)),
        webChroma: wc / n,
        nativeChroma: nc / n,
        deltaE: de / n,
      },
    };
    rows.push(row);
    record();
    console.log(
      `${label} ${c.profile} ${c.scene} DE=${row.deltaE.mean.toFixed(5)} ` +
        `body=${row.body.deltaE.toFixed(5)} Y=${row.body.webY.toFixed(5)}/${row.body.nativeY.toFixed(5)}` +
        (row.scored ? " [scored]" : ""),
    );
  }
} finally {
  await browser.close();
  await server.close();
}
