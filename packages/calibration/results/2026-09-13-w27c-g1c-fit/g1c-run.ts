/**
 * W27c G1c's model-form fit and its re-read (claims §5.141): a CANDIDATE
 * inactive endpoint against the 26.5 checking bed, on the WebGPU tier.
 *
 * The instrument is `results/2026-09-13-w27c-g2-read/g2-read.ts` with exactly
 * four changes and nothing else loosened.
 *
 *   - **`--patch <file>` names the endpoint under test.** The frozen G1 document
 *     is still the default, and with no `--patch` this driver reproduces the G2
 *     read's refusal that the exported profile IS the frozen one. With a
 *     candidate the refusal cannot apply — the whole point is that the document
 *     moved — so what replaces it is a record: the frozen and candidate resolved
 *     SHA-256s both travel in the matrix, per scheme, and the run stops if the
 *     candidate is not the document the page applied. The two ACTIVE fingerprint
 *     stops are untouched, because the endpoint is a difference over the active
 *     material and this child may not move that material at all.
 *   - **The machine's accessibility settings are read and recorded at launch.**
 *     The browser suites inherit macOS's own Reduce Transparency and Increase
 *     Contrast through the media-query policy feed, and a capture taken while
 *     either is on is not evidence even where this driver overrides the policy
 *     per cell. Both are read from `com.apple.universalaccess` before the first
 *     page opens; a non-zero reading refuses the run rather than qualifying it.
 *   - **`--controls <regex>` admits the declared control ids outside the bed**,
 *     on §5.130's recovered fixtures, so that what a candidate costs where the
 *     curve is already right can be measured at all. Documented in full at the
 *     pattern's own declaration below: never scored, never a bed id, and
 *     recording the absence of the plurality and pose proofs rather than
 *     asserting them.
 *   - **`--label` may name a sweep rung**, so a one-parameter ladder writes one
 *     matrix per rung into the same scratch directory.
 *
 * Everything else is the G2 read's: the same declared viewport, the same
 * fail-closed capture integrity, the same refusal of a page that did not apply
 * the declared endpoint, the same refusal of a fallback adapter or a tier that
 * demoted. What changes is where the cells come from. G1's driver walked the G0
 * census of recovered fixtures; this one walks the checking bed itself, against
 * the fixtures the sitting published (claims §5.136 §10, materialised at
 * `2026-09-13-w27c-g2-read/materialize.log`).
 *
 * Four rules this driver carries that the bound (`bound.json` clause 5) or the
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
 *     Every native PNG is hashed against that plurality before it is measured,
 *     and its attestation is quoted from the manifest that describes it.
 *   - **The pose and the endpoint are proved, not assumed.** A row whose native
 *     fixture does not attest the pose it is labelled with is refused before it
 *     is written, and the read stops if either active resolved fingerprint or the
 *     resolved endpoint has moved away from the frozen declaration.
 *
 * Usage:
 *   pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx \
 *     results/2026-09-13-w27c-g1c-fit/g1c-run.ts --out /tmp/w27c-g1c \
 *     --label t1-x0.93 --patch results/2026-09-13-w27c-g1c-fit/sweeps/t1-x0.93.json \
 *     --cells 'light-solid__(rrect-sm|capsule-button)' --profiles 'dark-standard'
 */
import { execFileSync } from "node:child_process";
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

const out = resolve(arg("out"));
const label = arg("label", "checking");
const renderer = arg("renderer", "webgpu");
if (renderer !== "webgpu" && renderer !== "css") throw new Error("Unknown renderer");
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
  } catch {
    return 0; // the default is absent, which is the setting being off
  }
}
const machineAccessibility = {
  reduceTransparency: accessibilityDefault("reduceTransparency"),
  increaseContrast: accessibilityDefault("increaseContrast"),
  readAt: new Date().toISOString(),
};
if (machineAccessibility.reduceTransparency !== 0 || machineAccessibility.increaseContrast !== 0) {
  throw new Error(
    `The machine's accessibility settings are on (reduceTransparency=` +
      `${machineAccessibility.reduceTransparency}, increaseContrast=` +
      `${machineAccessibility.increaseContrast}). The browser suites inherit them and a capture ` +
      `taken under either is not evidence. Turn both off and re-run.`,
  );
}

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

/**
 * `--controls <regex>`: the declared control ids that sit OUTSIDE the checking
 * bed, on §5.130's own recovered fixtures (`partition.json`, T1's controls).
 *
 * These are the cells the fit is refused ON rather than fitted on. The bed has
 * no dark thin cell over a structured backdrop that is not a checking cell, so
 * the only way to see what a candidate far ordinate costs where the curve is
 * already right is to read the recovered bed — which is exactly what §5.130
 * fitted against, and which W27 Decision Log 5 admits as pre-attestation
 * evidence.
 *
 * Three things follow, and each is a refusal or a record rather than a
 * relaxation. A control row is never `scored`: the bound scores group D and
 * nothing else, and these are not in it. Its native side has no sitting
 * plurality and no inactive-presentation attestation to check, because the
 * recovered entries carry neither, so the row records `preAttestationRecovered`
 * instead of pretending clause 5's proof exists for it. And a control id that
 * IS in the bed is refused outright, so this path can never quietly become a
 * second reading of a bed cell under a weaker rule.
 */
const controlPattern = process.argv.includes("--controls")
  ? new RegExp(arg("controls"))
  : undefined;

/**
 * The run whose bytes won this cell's seven-run plurality, and that plurality's
 * digest.
 *
 * Every row needs it, not only the ones read out of the sitting: it is what the
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
  const run = pluralityWinner(cell);
  const published = manifest.profiles
    .find((p: any) => p.profileKey === profileKey)
    ?.fixtures.find((f: any) => f.sceneId === sceneId);
  if (published !== undefined && published.fixtureSet === "probe") {
    const path = resolve(fixtures, published.file);
    return { cell, path, source: "bundle", entry: published, run };
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
function attestationRefusal(entry: any, state: string): string | undefined {
  const presented = String(entry.presentedActive);
  if (state !== "inactive") {
    return entry.presentedActive === true
      ? undefined
      : `the native fixture does not attest an active presentation (presentedActive=${presented})`;
  }
  if (entry.presentedActive !== false) {
    return `the native fixture does not attest an inactive presentation ` +
      `(presentedActive=${presented})`;
  }
  const presentation = entry.presentation;
  if (presentation === undefined || presentation === null) {
    return "the native fixture carries no presentation block";
  }
  if (
    presentation.observedPose !== "inactive" ||
    presentation.isKeyWindow !== false ||
    presentation.appIsActive !== false
  ) {
    return (
      `the native fixture's presentation block does not prove the inactive pose ` +
      `(observedPose=${String(presentation.observedPose)}, ` +
      `isKeyWindow=${String(presentation.isKeyWindow)}, ` +
      `appIsActive=${String(presentation.appIsActive)})`
    );
  }
  return undefined;
}

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
 * The holdout ids are the one subtraction. Three of the bed's ids carry the
 * `holdout` role from §5.130's frozen split; that holdout is spent, and this read
 * must produce no second vitrea-against-native distance for one of them under
 * another name. They are read natively by `native-attestation.py`, which compares
 * native against native and spends nothing.
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
    if (role(sceneId) === "holdout") continue;
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
 * The instrument, hashed into its own output.
 *
 * `sourceSha256` above pins what the runtime drew with. It says nothing about
 * what measured it, and this driver is a file in a results directory that anyone
 * may edit — the frozen G1 declaration pinned an `instrumentSha256` for exactly
 * that reason. Pinned with it: the bound and the bed, because a matrix read under
 * a different declaration is a different reading, and `plurality.json`, because
 * that is what selects which of the sitting's bytes a row is compared against.
 */
const instrumentSha256 = Object.fromEntries(
  [
    "packages/calibration/results/2026-09-13-w27c-g1c-fit/g1c-run.ts",
    "packages/calibration/results/2026-09-13-w27c-g1c-fit/partition.json",
    "packages/calibration/results/2026-09-13-w27c-g2-read/plurality.json",
    "packages/calibration/results/2026-09-11-w27c-g1b/bound.json",
    "packages/calibration/results/2026-09-11-w27c-g1b/checking-bed.json",
  ].map((file) => [file, sha(readFileSync(resolve(repo, file)))]),
);
/*
 * The endpoint this read is against, quoted from the frozen declaration rather
 * than recomputed: if the exported document had drifted from it, the resolved
 * SHA-256 below would not match and the run stops before its first capture.
 */
const frozen = json(resolve(pkg, "results/2026-09-10-w27c-g1-corrected-declaration.json"));
/*
 * The endpoint under test, and what is still refused about it.
 *
 * With no `--patch` this is the G2 read's refusal unchanged: the exported
 * document must BE the frozen G1 endpoint. With one, the candidate replaces the
 * exported document for this run and the refusal would be false by construction,
 * so what stands in its place is the record — `endpointUnderTest` below carries
 * the candidate's own resolved SHA-256 per scheme beside the frozen one, and the
 * per-cell check further down still refuses a page that applied anything other
 * than the candidate this file handed it.
 */
const patchFile = process.argv.includes("--patch") ? resolve(arg("patch")) : undefined;
const candidate: Record<"light" | "dark", any> =
  patchFile === undefined ? recededMaterialProfile : json(patchFile);
if (patchFile === undefined) {
  /*
   * With no candidate the exported document has to be a DECLARED endpoint, and
   * after this child there are two: the frozen G1 one and the one
   * `fitted-endpoint.json` freezes. Admitting only the first would refuse the
   * frozen re-read this child exists to produce; admitting anything would let an
   * uncommitted edit be measured as if it had been declared.
   */
  const declaredFile = resolve(here, "fitted-endpoint.json");
  const declared = existsSync(declaredFile)
    ? [frozen.patch, json(declaredFile).patch]
    : [frozen.patch];
  if (!declared.some((p) => JSON.stringify(p) === JSON.stringify(recededMaterialProfile))) {
    throw new Error(
      "The exported receded profile is neither the frozen G1 endpoint nor the endpoint " +
        "fitted-endpoint.json declares",
    );
  }
}
const endpointUnderTest: Record<string, unknown> = {
  source: patchFile === undefined
    ? "packages/platform-web/src/receded-profile.ts (the exported document)"
    : patchFile,
  patch: candidate,
  patchSha256: sha(JSON.stringify(candidate)),
  frozenPatchSha256: sha(JSON.stringify(frozen.patch)),
  isFrozenG1Endpoint: JSON.stringify(candidate) === JSON.stringify(frozen.patch),
};
/*
 * The receded patch alone does not fix the endpoint. It is applied THROUGH the
 * active documents, so the material this read measures is the active material
 * resolved over the runtime defaults with the patch on top — and `bound.json`
 * clause 5 stops the read if either active resolved fingerprint moves. The
 * per-row check further down cannot see that: it compares the patch the page
 * applied against the patch this file handed it, which a drift in
 * `DEFAULT_MATERIAL_PROFILE` or in an active document's own constants passes
 * unchanged. So both resolutions are recomputed here, the way the declaration
 * computed them, and compared with the digests it froze.
 */
for (const scheme of ["light", "dark"] as const) {
  const doc = json(resolve(pkg, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`));
  const declared = frozen.profiles[scheme];
  const activeResolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch);
  const activeSha256 = shaValue(activeResolved);
  if (activeSha256 !== declared.activeSha256) {
    throw new Error(
      `The ${scheme} ACTIVE material resolves to ${activeSha256} where the frozen declaration ` +
        `froze ${declared.activeSha256}. The endpoint is a patch over this material, so the read ` +
        `would not be against the declared endpoint.`,
    );
  }
  if (doc.resolvedMaterialSha256 !== declared.activeRecordedFingerprint) {
    throw new Error(
      `The ${scheme} active profile document records fingerprint ${doc.resolvedMaterialSha256} ` +
        `where the declaration froze ${declared.activeRecordedFingerprint}`,
    );
  }
  const inactiveSha256 = shaValue(withMaterialOverrides(activeResolved, candidate[scheme]));
  if (endpointUnderTest.isFrozenG1Endpoint === true && inactiveSha256 !== declared.inactiveSha256) {
    throw new Error(
      `The ${scheme} INACTIVE endpoint resolves to ${inactiveSha256} where the frozen ` +
        `declaration froze ${declared.inactiveSha256}`,
    );
  }
  (endpointUnderTest as any)[`${scheme}InactiveSha256`] = inactiveSha256;
  (endpointUnderTest as any)[`${scheme}FrozenInactiveSha256`] = declared.inactiveSha256;
}

const rows: any[] = [];
const record = (): void =>
  writeFileSync(
    resultFile,
    `${JSON.stringify(
      {
        gate: "W27c G1c fit / claims §5.141",
        label,
        renderer,
        readAgainst: frozen.profiles,
        endpointUnderTest,
        partition: "packages/calibration/results/2026-09-13-w27c-g1c-fit/partition.json",
        bed: "packages/calibration/results/2026-09-11-w27c-g1b/checking-bed.json",
        bound: "packages/calibration/results/2026-09-11-w27c-g1b/bound.json",
        machineAccessibility,
        sitting,
        engineVersion: browser.version(),
        sourceSha256,
        instrumentSha256,
        patchSha256: sha(JSON.stringify(candidate)),
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
    /*
     * Clause 5's attestation refusal, and the one population it cannot be asked
     * of. A control row's native side is §5.130's recovered fixture, whose pose
     * is inferred from the DL14 post-mortem and attested per cell by nothing —
     * that is what W27 Decision Log 5 admitted and what the checking bed exists
     * to check. Refusing those rows would delete the controls; asserting the
     * proof for them would be false. So the row carries the absence as a field.
     */
    const isControl = native.source === "recovered";
    const refused = isControl ? undefined : attestationRefusal(native.entry, scene.state);
    if (refused !== undefined) throw new Error(`${native.cell}: ${refused} (bound.json clause 5)`);

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
    if (native.run !== undefined && sha(nativeBytes) !== native.run.sha256) {
      throw new Error(
        `${native.cell}: the native bytes at ${native.path} hash ${sha(nativeBytes)} where the ` +
          `sitting's plurality for this cell is ${native.run.sha256}`,
      );
    }
    const backgroundName = `${scene.background}@${c.scale}x.png`;
    const backgroundBytes = readFileSync(resolve(fixtures, "backgrounds", backgroundName));
    if (native.run !== undefined) {
      const compositedOver = readFileSync(resolve(native.run.dir, "backgrounds", backgroundName));
      if (sha(backgroundBytes) !== sha(compositedOver)) {
        throw new Error(
          `${native.cell}: the bundle's ${backgroundName} is not the raster run ${native.run.run} ` +
            `composited over, so the row would be vitrea on one backdrop against native on another`,
        );
      }
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
      groups: isControl ? ["control"] : groupsOf.get(c.scene),
      role: role(c.scene),
      scored: !isControl && checkingSet.has(c.scene),
      isControl,
      preAttestationRecovered: isControl,
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
