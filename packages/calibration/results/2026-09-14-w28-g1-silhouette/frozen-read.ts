/**
 * W28 G2 frozen reader. Capture and body-DeltaE arithmetic are G1d's, unchanged.
 * G1 invokes ONLY --dry: it exits before native/background I/O, Vite or Chromium.
 * A future authorized G2 invokes --read; the sealed configuration admits no candidate.
 * Outputs are scratch-only. Two deterministic captures use headed hardware Chromium.
 * Seven-run D plurality and native presentation attestations remain G1d's lineage.
 *
 * tsx results/2026-09-14-w28-g1-silhouette/frozen-read.ts --dry --out /tmp/w28-g2-dry
 * G2 only: --read defaults to WebGPU including all six holdouts. --renderer css is
 * record-only coherence and excludes every declared holdout pair on both scales.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";
import { createServer } from "vite";
import { fingerprint, admitRead, pageReady, repeated, resumeRead, machineReady, nativeAdmission,
  outputAvailable, scratchPath, gitBlobOid, captureBytes, measurementEvidence, readCell } from "./read-guards";
import { exerciseDryRefusals } from "./dry-refusals";
import { componentRegion, type DeclaredComponent } from "../../src/component-region";
import { decodePng, linearLuminance } from "../../src/image";
import { oklabDeltaE } from "../../src/metrics/perceptual";
import { srgbByteToOklab, oklabDistance, oklabChroma } from "../../src/color";
import { recededMaterialProfile } from "../../../platform-web/src/receded-profile";
import { mergeMaterialProfiles } from "../../../platform-web/src/color-scheme";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides,
} from "../../../renderer-webgpu/src/material";

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
/*
 * Key-sorted JSON, and a digest over it. This is the encoding
 * `results/2026-09-10-w27c-g1-corrected-declare.ts` froze the endpoint's digests
 * under, reproduced here so that the numbers below are comparable with the ones
 * in the declaration at all.
 */
const canonical = (v: any): any =>
  Array.isArray(v)
    ? v.map(canonical)
    : v !== null && typeof v === "object"
      ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, canonical(v[k])]))
      : v;
const shaValue = (v: unknown): string => sha(JSON.stringify(canonical(v)));

const dry = process.argv.includes("--dry");
if (!dry && !process.argv.includes("--read")) throw new Error("Use --dry in G1; --read requires G2 dispatch");
const out = resolve(arg("out"));
scratchPath(out, repo);
const capturesRoot = resolve(process.env["VITREA_WEB_CAPTURES"] ?? out);
scratchPath(capturesRoot, repo);
const label = arg("label", "checking");
const renderer = arg("renderer", "webgpu");
if (renderer !== "webgpu" && renderer !== "css") throw new Error("Use webgpu or record-only css");
const scenePattern = new RegExp(arg("cells", "."));
const profilePattern = new RegExp(arg("profiles", "."));
const sitting = resolve(arg("sitting", process.env["VITREA_SITTING_ROOT"] ?? "/Users/new/vitrea-w27-26.5-run"));

/*
 * The machine's own accessibility state, read before anything opens a page.
 *
 * vitrea's media-query policy feed reads the OS preference, and Playwright
 * cannot emulate either of these two (the repository's own CLAUDE.md says so).
 * This driver overrides the material policy per cell, so an OS preference does
 * not silently select a different fold — but it reaches the page by other paths
 * and a capture taken under it is not evidence of anything. So it is a refusal,
 * not a warning, and the reading travels in the matrix beside the rows it
 * admitted.
 */
function accessibilityDefault(key: string): number {
  try {
    return Number(
      execFileSync("defaults", ["read", "com.apple.universalaccess", key], { encoding: "utf8" })
        .trim(),
    );
  } catch (error) {
    const stderr = String((error as { stderr?: string | Buffer }).stderr ?? "");
    if (stderr.includes(`(com.apple.universalaccess, ${key}) does not exist`)) {
      return 0; // an absent preference key is the setting being off
    }
    throw error;
  }
}
const machineAccessibility = {
  reduceTransparency: dry ? null : accessibilityDefault("reduceTransparency"),
  increaseContrast: dry ? null : accessibilityDefault("increaseContrast"),
  readAt: new Date().toISOString(),
};
if (!dry) machineReady(machineAccessibility);

const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const manifest = json(resolve(repo, "apps/reference-apple/fixtures/manifest.json"));
const fixtures = resolve(repo, "apps/reference-apple/fixtures");
const bedSpec = json(resolve(here, "../2026-09-11-w27c-g1b/checking-bed.json"));
// The sitting's own plurality, read out of the read that established it rather
// than copied here: which of the seven runs won a cell is a fact about the
// sitting, and a second copy is a second thing to drift.
const plurality = json(resolve(here, "../2026-09-14-w27c-g1d/plurality.json"));

/** Every id the bed declares, with the group(s) it belongs to and its role. */
const groupsOf = new Map<string, string[]>();
for (const group of bedSpec.groups) {
  for (const id of group.scenes) groupsOf.set(id, [...(groupsOf.get(id) ?? []), group.id]);
  for (const id of group.alsoCaptureActive ?? []) {
    groupsOf.set(id, [...(groupsOf.get(id) ?? []), `${group.id}-active`]);
  }
}
for (const component of ["capsule-button", "rrect-sm", "rrect-ml", "rrect-lg"]) {
  groupsOf.set(`mid-light-solid__${component}__inactive`, ["F"]);
}
const includeDeclaredHoldout = renderer === "webgpu";
// Keep all six ids on both tiers: CSS must exclude even the checkerboard pair already in bed B.
const declaredHoldout = new Set<string>(json(resolve(here, "fitted-endpoint.json")).holdout.cells);
for (const cell of declaredHoldout) {
  const scene = cell.slice(cell.indexOf("/") + 1);
  if (!groupsOf.has(scene)) groupsOf.set(scene, ["H"]);
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

// G1d's control option is parsed only to refuse it before G2 evidence I/O.
const controlPattern = process.argv.includes("--controls")
  ? new RegExp(arg("controls"))
  : undefined;

/**
 * The run whose bytes won this cell's seven-run plurality, and that plurality's
 * digest.
 *
 * Every bed row needs it (recovered H has separately pinned blob lineage): it is what the
 * native bytes are checked against, and it names the run directory holding the
 * raster the native capture was composited over.
 */
function pluralityWinner(cell: string): { dir: string; run: string; sha256: string } {
  for (const pass of plurality.passes) {
    const tally = pass.cellTally[cell];
    if (tally === undefined) continue;
    const run = Object.entries(tally.perRunSha256).find(([, s]) => s === tally.pluralitySha256);
    if (run === undefined) break;
    return {
      dir: resolve(sitting, pass.dir, run[0]),
      run: run[0],
      sha256: tally.pluralitySha256 as string,
    };
  }
  throw new Error(`${cell}: the sitting's plurality does not hold this cell`);
}

/** A run's own manifest, read once and kept: it is the attestation of its bytes. */
const runManifests = new Map<string, any>();
function runEntry(dir: string, profileKey: string, sceneId: string): any {
  let doc = runManifests.get(dir);
  if (doc === undefined) {
    doc = json(resolve(dir, "manifest.json"));
    runManifests.set(dir, doc);
  }
  const entry = doc.profiles
    .find((p: any) => p.profileKey === profileKey)
    ?.fixtures.find((f: any) => f.sceneId === sceneId);
  if (entry === undefined) {
    throw new Error(`${profileKey}/${sceneId}: run ${dir} published bytes with no manifest entry`);
  }
  return entry;
}

/**
 * Where a cell's native bytes live, and the manifest entry that goes with THOSE
 * bytes.
 *
 * The two travel together deliberately. A bed id the bundle already held keeps
 * its recovered fixture, which this read must not overwrite and must not read as
 * if it were this bed's, so the comparison takes the sitting's plurality PNG —
 * and then the attestation has to come from the sitting's manifest too. Quoting
 * the bundle's recovered entry beside the sitting's bytes would publish the pose,
 * the idle and the determinism of a capture that produced no pixel in the row.
 */
function nativeFor(profileKey: string, sceneId: string): {
  cell: string;
  path: string;
  source: "bundle" | "sitting" | "recovered";
  entry: any;
  run: { dir: string; run: string; sha256: string } | undefined;
} {
  const cell = `${profileKey}/${sceneId}`;
  if (!groupsOf.has(sceneId)) {
    /*
     * A declared control outside the bed. Its bytes are §5.130's recovered
     * fixture and nothing in the sitting describes them, so there is no
     * plurality to hash against and no attestation to check — the row says so.
     */
    const recovered = manifest.profiles
      .find((p: any) => p.profileKey === profileKey)
      ?.fixtures.find((f: any) => f.sceneId === sceneId);
    if (recovered === undefined) {
      throw new Error(`${cell}: declared as a control and the bundle holds no fixture for it`);
    }
    return {
      cell, path: resolve(fixtures, recovered.file), source: "recovered",
      entry: recovered, run: undefined,
    };
  }
  const published = manifest.profiles
    .find((p: any) => p.profileKey === profileKey)
    ?.fixtures.find((f: any) => f.sceneId === sceneId);
  if (groupsOf.get(sceneId)?.includes("H")) {
    if (published === undefined) throw new Error(`${cell}: declared holdout has no fixture`);
    return {
      cell, path: resolve(fixtures, published.file), source: "recovered",
      entry: published, run: undefined,
    };
  }
  const run = pluralityWinner(cell);
  const publishedAgain = manifest.profiles
    .find((p: any) => p.profileKey === profileKey)
    ?.fixtures.find((f: any) => f.sceneId === sceneId);
  if (publishedAgain !== undefined && publishedAgain.fixtureSet === "probe") {
    const path = resolve(fixtures, publishedAgain.file);
    return { cell, path, source: "bundle", entry: publishedAgain, run };
  }
  return {
    cell,
    path: resolve(run.dir, profileKey, `${sceneId}.png`),
    source: "sitting",
    entry: runEntry(run.dir, profileKey, sceneId),
    run,
  };
}

/**
 * `bound.json` clause 5's attestation refusal, stated as a reason or `undefined`.
 *
 * The refusal is on the native fixture, not on the web capture: a row whose
 * native bytes cannot be shown to hold the pose they are labelled with is a
 * measurement against an unknown reference, and the bound refuses it before it
 * is written rather than qualifying it afterwards. For the inactive pose the
 * harness's proof is the presentation block — the window was not key and the app
 * not active when the shutter fired — and for the active pose it is the
 * complementary claim.
 */

interface Cell {
  profile: string;
  scene: string;
  scale: number;
  scheme: string;
  a11yMode: string;
}
/*
 * The population is the bed crossed with the DECLARATION, not with the bundle.
 *
 * `scenes.json` is the single source for which profile captures which scene, and
 * the sitting captured what it declares. Enumerating from the manifest's existing
 * entries instead silently drops every bed cell the sitting captured but the
 * bundle never held — the dark `light-solid__capsule-button__inactive` pair is
 * exactly that, declared by both dark profiles, captured seven times, and read by
 * no row. A read whose population is the old bundle can only ever confirm the old
 * bundle.
 *
 * Prior holdout-role cells remain excluded unless DL2(f) names them among the six
 * W28 holdouts. H is a holdout supplying group, never a fit or control population.
 */
const everyScene = matrix.scenes.map((s: any) => s.id as string);
const population: Cell[] = [];
for (const profile of matrix.profiles) {
  const scale = profile.key.includes("-2x-") ? 2 : 1;
  const declared: string[] = profile.scenes === "all" ? everyScene : profile.scenes;
  for (const sceneId of declared) {
    const isControl = controlPattern?.test(sceneId) === true && !groupsOf.has(sceneId);
    if (!groupsOf.has(sceneId) && !isControl) continue;
    if (controlPattern?.test(sceneId) === true && groupsOf.has(sceneId)) {
      throw new Error(
        `${sceneId} is a bed id and cannot be read as a control: the control path skips the ` +
          `plurality and attestation refusals a bed cell must pass`,
      );
    }
    if (isControl && matrix.scenes.find((s: any) => s.id === sceneId)?.state !== "inactive") {
      continue;
    }
    if (!scenePattern.test(sceneId) && !isControl) continue;
    if (!profilePattern.test(profile.key)) continue;
    /*
     * §5.130's spent holdout is excluded on every path, controls included: a
     * control is a cell the fit is refused on, and a spent holdout id read again
     * would be a second spending under another name whatever it is called here.
     */
    const cell = `${profile.key}/${sceneId}`;
    if (!readCell(renderer, cell, declaredHoldout)) continue;
    if (role(sceneId) === "holdout" && !declaredHoldout.has(cell)) continue;
    if (groupsOf.get(sceneId)?.includes("H") && !declaredHoldout.has(cell)) continue;
    population.push({
      profile: profile.key,
      scene: sceneId,
      scale,
      scheme: profile.colorScheme,
      a11yMode: profile.a11y,
    });
  }
}
if (population.length === 0) throw new Error("Empty population");
population.sort((a, b) => `${a.profile}/${a.scene}`.localeCompare(`${b.profile}/${b.scene}`));

const resultFile = resolve(out, `${label}.json`);
scratchPath(resultFile, repo);
outputAvailable(resultFile, existsSync(resultFile),
  process.argv.includes("--resume") ? resolve(arg("resume")) : undefined);

const frozen = json(resolve(here, "fitted-endpoint.json"));
const sourceSha256 = Object.fromEntries(Object.keys(frozen.sourceSha256).map((file) => {
  const current = sha(readFileSync(resolve(repo, file)));
  fingerprint(`source ${file}`, current, frozen.sourceSha256[file]);
  return [file, current];
}));
const instrumentSha256 = Object.fromEntries(Object.keys(frozen.instrumentSha256).map((file) => {
  const current = sha(readFileSync(resolve(repo, file)));
  fingerprint(`instrument ${file}`, current, frozen.instrumentSha256[file]);
  return [file, current];
}));
for (const [file, value] of Object.entries(frozen.activeDocuments) as [string, any][]) {
  const doc = json(resolve(repo, file));
  fingerprint(`active recorded ${file}`, doc.resolvedMaterialSha256, value.recordedFingerprint);
  fingerprint(`active bytes ${file}`, sha(readFileSync(resolve(repo, file))), value.fileSha256);
}
fingerprint("scene declaration", shaValue(matrix), frozen.sceneSpecSha256);
const patchFile = process.argv.includes("--patch") ? resolve(arg("patch")) : undefined;
admitRead(patchFile !== undefined, includeDeclaredHoldout);
if (patchFile !== undefined) throw new Error("The G2 reader admits only the sealed export, no candidate");
if (controlPattern !== undefined) throw new Error("G2 uses its declared population, not fit controls");
if (process.argv.includes("--once")) throw new Error("G2 requires two deterministic repeats");
const candidate = recededMaterialProfile;
fingerprint("raw patch", sha(JSON.stringify(candidate)), frozen.patchSha256);
const endpointUnderTest: Record<string, unknown> = {
  source: "packages/platform-web/src/receded-profile.ts (sealed exported document)",
  patch: candidate, patchSha256: frozen.patchSha256,
};
for (const scheme of ["light", "dark"] as const) {
  const doc = json(resolve(pkg, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`));
  const declared = frozen.profiles[scheme];
  const active = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch);
  fingerprint(`${scheme} active resolved`, shaValue(active), declared.activeSha256);
  fingerprint(`${scheme} active recorded`, doc.resolvedMaterialSha256, declared.activeRecordedFingerprint);
  const inactiveSha256 = shaValue(withMaterialOverrides(active, candidate[scheme]));
  fingerprint(`${scheme} inactive resolved`, inactiveSha256, declared.inactiveSha256);
  endpointUnderTest[`${scheme}InactiveSha256`] = inactiveSha256;
}

const resumeFile = process.argv.includes("--resume") ? resolve(arg("resume")) : undefined;
const resumed = resumeFile === undefined ? undefined : json(resumeFile);
const identity = { patchSha256: frozen.patchSha256, renderer, sourceSha256,
  instrumentSha256, sceneSpecSha256: shaValue(matrix), readAgainst: frozen.profiles, endpointUnderTest };
resumeRead(resumed, identity, population);
for (const row of resumed?.rows ?? []) {
  const cell = `${row.profile}/${row.scene}`;
  if (row.isHoldout !== declaredHoldout.has(cell) || row.scored !== (renderer === "webgpu" && checkingSet.has(row.scene))) {
    throw new Error(`${cell}: resumed role differs from declaration`);
  }
  if (row.preAttestationRecovered) {
    fingerprint("resume recovered lineage", shaValue(row.recoveredLineage),
      shaValue(frozen.holdout.recoveredLineage[cell] ?? null));
  } else {
    const winner = pluralityWinner(cell);
    fingerprint("resume native plurality", row.nativeSha256, winner.sha256);
    fingerprint("resume native run", row.nativeRun, winner.run);
  }
}
// This return boundary precedes every native/background PNG read, server and browser operation.
if (dry) {
  const evidence = exerciseDryRefusals();
  mkdirSync(out, { recursive: true });
  const dryFile = resolve(out, "dry-run.json");
  outputAvailable(dryFile, existsSync(dryFile));
  writeFileSync(dryFile, `${JSON.stringify({ mode: "DRY", ...evidence,
    sealedPatchSha256: frozen.patchSha256, sealedProfiles: frozen.profiles,
    sourceSha256, instrumentSha256, pagesOpened: 0, nativePngsOpened: 0,
    backgroundPngsOpened: 0, machineSettingsRead: false,
    plannedRows: population.map((c) => `${c.profile}/${c.scene}`),
    holdout: frozen.holdout, realReadExecuted: false,
  }, null, 2)}\n`, { flag: "wx" });
  console.log(`DRY passed ${evidence.refusals.length} exercised refusals; zero pages/native PNGs`);
  process.exit(0);
}
mkdirSync(out, { recursive: true });
const rows: any[] = resumed?.rows ?? [];
// Retained web bytes are checked only after DRY exits, and before Vite or any new page.
for (const row of rows) {
  scratchPath(row.capture, repo);
  captureBytes(row, readFileSync(row.capture));
}
const record = (): void =>
  writeFileSync(
    resultFile,
    `${JSON.stringify(
      {
        gate: "W28 G2 frozen read; G1 executes DRY only",
        label,
        renderer,
        readAgainst: frozen.profiles,
        endpointUnderTest,
        partition: "packages/calibration/results/2026-09-14-w28-g1-silhouette/partition.json",
        bed: "packages/calibration/results/2026-09-11-w27c-g1b/checking-bed.json",
        bound: "packages/calibration/results/2026-09-11-w27c-g1b/bound.json",
        machineAccessibility,
        sitting,
        engineVersion: browser.version(),
        sourceSha256,
        instrumentSha256,
        patchSha256: sha(JSON.stringify(candidate)),
        sceneSpecSha256: shaValue(matrix),
        definitions: {
          deltaE: "Full-canvas mean per-pixel OKLab distance, canonical oklabDeltaE",
          bodyDeltaE: "Mean per-pixel OKLab distance over the declared union eroded 6 CSS px",
          body: "Declared union eroded 6 CSS px: linear Rec.709 Y mean and population SD, and mean per-pixel OKLab chroma",
          scale: "Device pixels per CSS px",
          geometry:
            "How the page was actually framed, read back per row: the viewport is the declared " +
            "matrix canvas, and a row exists only where the page reported no problems and agreed " +
            "with the declaration on canvas, requested scale and devicePixelRatio",
          notRead: "Prior holdout-role cells outside the six W28-declared cells remain unread.",
          holdout: renderer === "webgpu"
            ? "Six cells read once on the W28 seal under DL2(f); four recovered H rows " +
              "carry preAttestationRecovered and pinned blob lineage, not a presentation proof."
            : "Record-only CSS coherence excludes all six W28 holdout pairs, including bed B.",
        },
        rows,
      },
      null,
      2,
    )}\n`,
  );

// Refuse orphan captures before launch too: a crash must not silently spend a holdout again.
for (const c of population) {
  if (rows.some((row) => row.profile === c.profile && row.scene === c.scene)) continue;
  const capture = resolve(capturesRoot, label, c.profile, `${c.scene}.png`);
  scratchPath(capture, repo);
  outputAvailable(capture, existsSync(capture));
}
const port = Number(arg("port", "5203"));
const server = await createServer({
  configFile: resolve(pkg, "web/vite.config.ts"),
  server: { port, strictPort: true },
});
await server.listen();
const browser = await chromium.launch({
  channel: "chromium",
  headless: false,
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
});
try {
  for (const c of population) {
    if (rows.some((row) => row.profile === c.profile && row.scene === c.scene)) continue;
    const scene = matrix.scenes.find((s: any) => s.id === c.scene);
    if (scene === undefined) throw new Error(`${c.scene}: not declared in scenes.json`);
    const inactive = scene.state === "inactive";
    const selectedPatch = inactive ? candidate[c.scheme as "light" | "dark"] : undefined;
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
    // DL2(f) admits recovered H without pretending its absent presentation proof exists.
    const { isControl, isHoldout, preAttestationRecovered } = nativeAdmission({
      checking: checkingSet.has(c.scene), isHoldout: declaredHoldout.has(native.cell),
      recovered: native.source === "recovered", run: native.run, entry: native.entry,
      state: scene.state,
    });

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
    /*
     * The bytes are verified, not merely located. `plurality.json` decided which
     * run won this cell; a path derived from that decision is not the same claim
     * as the bytes at the path being the ones it decided on, and the bundle can
     * hold a fixture that was republished since. The same for the backdrop: the
     * row records the raster's digest, and a digest recorded against nothing is a
     * number, so it is compared with the copy in the run directory the native
     * bytes came from — the raster the native capture was actually composited
     * over. Both are refusals, as the frozen G1 instrument made them.
     */
    const nativeBytes = readFileSync(native.path);
    if (native.run !== undefined) fingerprint("native plurality", sha(nativeBytes), native.run.sha256);
    const backgroundName = `${scene.background}@${c.scale}x.png`;
    const backgroundBytes = readFileSync(resolve(fixtures, "backgrounds", backgroundName));
    if (native.run !== undefined) {
      const compositedOver = readFileSync(resolve(native.run.dir, "backgrounds", backgroundName));
      fingerprint("background raster", sha(backgroundBytes), sha(compositedOver));
    }
    if (preAttestationRecovered) {
      const lineage = frozen.holdout.recoveredLineage[native.cell];
      fingerprint("recovered native blob", gitBlobOid(nativeBytes), lineage.nativeBlobOid);
      fingerprint("recovered background blob", gitBlobOid(backgroundBytes), lineage.backgroundBlobOid);
      fingerprint("recovered native path", native.path, resolve(repo, lineage.nativePath));
      fingerprint("recovered background path", resolve(fixtures, "backgrounds", backgroundName),
        resolve(repo, lineage.backgroundPath));
    }
    const nativeImage = decodePng(nativeBytes);
    const region = componentRegion(matrix.components[scene.component] as DeclaredComponent, {
      canvas: matrix.canvas,
      scale: c.scale,
      width: nativeImage.width,
      height: nativeImage.height,
    });
    let first: Buffer | undefined;
    let report: any;
    const count = 2;
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
      pageReady(report, { canvas: matrix.canvas, scale: c.scale }, renderer,
        await page.getAttribute("html", "data-scene-ready") === "1");
      const expected = inactive
        ? mergeMaterialProfiles(materialDoc.patch, selectedPatch)
        : materialDoc.patch;
      fingerprint("page endpoint", shaValue(report.materialProfile), shaValue(expected));
      const png = await page.locator("#stage").screenshot({ animations: "disabled" });
      repeated(first, png);
      first = png;
      await page.close();
    }
    await context.close();
    const capture = resolve(
      resolve(capturesRoot, label),
      c.profile,
      `${c.scene}.png`,
    );
    scratchPath(capture, repo);
    outputAvailable(capture, existsSync(capture));
    mkdirSync(dirname(capture), { recursive: true });
    writeFileSync(capture, first as Buffer, { flag: "wx" });
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
      scored: renderer === "webgpu" && checkingSet.has(c.scene),
      checkingSetMember: checkingSet.has(c.scene),
      isControl,
      isHoldout,
      preAttestationRecovered,
      recoveredLineage: preAttestationRecovered ? frozen.holdout.recoveredLineage[native.cell] : null,
      capture,
      captureSha256: sha(first as Buffer),
      nativeSource: native.source,
      nativePath: native.path,
      nativeSha256: sha(nativeBytes),
      nativeRun: native.run?.run ?? null,
      backgroundSha256: sha(backgroundBytes),
      // The attestation OF THESE BYTES: the pose the capture proved and the idle
      // it was taken under, quoted from the manifest whose entry describes the
      // file the row measured — the winning run's for a row read out of the
      // sitting, the bundle's for one the sitting published.
      nativeAttestation: {
        presentedActive: native.entry.presentedActive ?? null,
        presentation: native.entry.presentation ?? null,
        hidIdleSeconds: native.entry.hidIdleSeconds ?? null,
        deterministic: native.entry.deterministic ?? null,
        frequencySettled: native.entry.frequencySettled ?? false,
        stateFrequencies: native.entry.stateFrequencies ?? null,
        identicalToBackground: native.entry.identicalToBackground ?? null,
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
    measurementEvidence(row, renderer);
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
