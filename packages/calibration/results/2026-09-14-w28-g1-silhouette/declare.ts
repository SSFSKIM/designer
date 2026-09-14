/**
 * W28 G1 seal, derived from G1d declare.ts. Run only after the selected rungs are exported.
 * Raw patch order is recorded, not used to compare two equivalent resolved documents.
 * No native fixture is opened. Output is exclusive: a frozen endpoint is never overwritten.
 */
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { resolve, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { recededMaterialProfile } from "../../../platform-web/src/receded-profile";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../../renderer-webgpu/src/material";
import { fingerprint, sha, shaValue, outputAvailable, activeDocument, selectedSweep } from "./read-guards";
import { existsSync } from "node:fs";
import { admitFitRows } from "./admission";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");
const json = (path: string): any => JSON.parse(readFileSync(path, "utf8"));
const old = json(resolve(here, "../2026-09-14-w27c-g1d/fitted-endpoint.json"));
const declaration = json(resolve(here, "declaration.json"));
const partition = json(resolve(here, "partition.json"));
const cells: string[] = declaration.holdout.rows.map((r: any) => r.cell);
if (cells.length !== 6 || new Set(cells).size !== 6 ||
    shaValue([...cells].sort()) !== shaValue([...partition.holdout].sort())) {
  throw new Error("The six declared unread holdout ids must equal the fit partition's exclusions");
}
admitFitRows(partition.rows, new Set(cells));
const output = resolve(here, "fitted-endpoint.json");
outputAvailable(output, existsSync(output));
const activeDocuments: Record<string, unknown> = {};
const mainHead = execFileSync("git", ["-C", repo, "rev-parse", "main"], { encoding: "utf8" }).trim();
const baselineProfiles = execFileSync("git", ["-C", repo, "ls-tree", "-r", "--name-only",
  mainHead, "--", "packages/calibration/profiles"], { encoding: "utf8" }).trim().split("\n");
for (const path of baselineProfiles.filter((p) => p.endsWith(".json"))) {
  const file = path.slice(path.lastIndexOf("/") + 1);
  const doc = json(resolve(repo, path));
  const baseline = JSON.parse(execFileSync("git", ["-C", repo, "show", `${mainHead}:${path}`],
    { encoding: "utf8" }));
  if (!activeDocument(file, doc, baseline)) continue;
  // Also freeze the bytes, so later changes cannot hide behind an unchanged recorded SHA.
  activeDocuments[path] = { recordedFingerprint: doc.resolvedMaterialSha256,
    fileSha256: sha(readFileSync(resolve(repo, path))) };
}
// Only tree metadata is read for the recovered H rasters. G2 verifies their actual bytes.
const sceneSpec = json(resolve(repo, "apps/reference-apple/scenes.json"));
const baselineManifest = JSON.parse(execFileSync("git", ["-C", repo, "show",
  `${mainHead}:apps/reference-apple/fixtures/manifest.json`], { encoding: "utf8" }));
const bed = json(resolve(here, "../2026-09-11-w27c-g1b/checking-bed.json"));
const bedIds = new Set(bed.groups.flatMap((g: any) => [...g.scenes, ...(g.alsoCaptureActive ?? [])]));
const blobOid = (path: string): string => {
  const entry = execFileSync("git", ["-C", repo, "ls-tree", mainHead, "--", path],
    { encoding: "utf8" }).trim();
  const match = /^100644 blob ([a-f0-9]{40})\t/.exec(entry);
  if (!match) throw new Error(`No committed raster blob at ${path}`);
  return match[1]!;
};
const recoveredLineage: Record<string, unknown> = {};
for (const cell of cells) {
  const [profile, sceneId] = cell.split("/");
  if (bedIds.has(sceneId)) continue; // The checkerboard pair retains G1d's strict plurality path.
  const fixture = baselineManifest.profiles.find((p: any) => p.profileKey === profile)
    ?.fixtures.find((f: any) => f.sceneId === sceneId);
  if (!fixture?.recoveredProvenance) throw new Error(`${cell}: recovered lineage missing`);
  const scene = sceneSpec.scenes.find((s: any) => s.id === sceneId);
  const scale = profile!.includes("-2x-") ? 2 : 1;
  const nativePath = `apps/reference-apple/fixtures/${fixture.file}`;
  const backgroundPath = `apps/reference-apple/fixtures/backgrounds/${scene.background}@${scale}x.png`;
  recoveredLineage[cell] = { nativePath, backgroundPath,
    nativeBlobOid: blobOid(nativePath), backgroundBlobOid: blobOid(backgroundPath),
    preAttestationRecovered: true };
}
const profiles: Record<string, unknown> = {};
const selected: Record<string, unknown> = {};
for (const scheme of ["light", "dark"] as const) {
  const fitPath = resolve(here, `fit-${scheme}.json`);
  const fit = json(fitPath);
  if (typeof fit.selected !== "string" || fit.rungs[fit.selected]?.refused !== false) {
    throw new Error(`${scheme}: no selected admissible fitted rung`);
  }
  const candidatePath = resolve(here, "sweeps", `${fit.selected}.json`);
  const candidate = json(candidatePath);
  const sweepPath = resolve(here, "sweep-matrices", `${fit.selected}.json`);
  const sweep = json(sweepPath);
  selectedSweep(sweep, fit.selected, fit.rungs[fit.selected], repo);
  // fit-read refused dirty runtime before capture. Compare its commit's runtime too, so
  // paths absent from its explicit map (notably renderer-bridge.ts) cannot drift at seal.
  // Adopting the selected receded export is intentional and separately resolved-checked below.
  if (!/^[a-f0-9]{40}$/.test(sweep.repositoryHead ?? "")) {
    throw new Error(`${scheme}: selected sweep runtime commit missing`);
  }
  execFileSync("git", ["-C", repo, "diff", "--exit-code", sweep.repositoryHead, "--",
    "packages/core/src", "packages/renderer-webgpu/src", "packages/platform-web/src",
    "packages/calibration/web", ":(exclude)packages/platform-web/src/receded-profile.ts"]);
  fingerprint(`${scheme} selected partition`, sweep.partitionSha256,
    sha(readFileSync(resolve(here, "partition.json"))));
  fingerprint(`${scheme} selected instrument`, sweep.instrumentSha256,
    sha(readFileSync(resolve(here, "fit-read.ts"))));
  fingerprint(`${scheme} selected raw patch`, sha(JSON.stringify(candidate)), sweep.patchSha256);
  const doc = json(resolve(pkg, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`));
  const active = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch);
  const activeSha256 = shaValue(active);
  fingerprint(`${scheme} ACTIVE resolved`, activeSha256, old.profiles[scheme].activeSha256);
  fingerprint(`${scheme} ACTIVE recorded`, doc.resolvedMaterialSha256,
    old.profiles[scheme].activeRecordedFingerprint);
  const candidateResolved = withMaterialOverrides(active, candidate[scheme]);
  const exportedResolved = withMaterialOverrides(active, recededMaterialProfile[scheme]);
  fingerprint(`${scheme} selected rung resolved`, shaValue(candidateResolved),
    fit.rungs[fit.selected].inactiveSha256);
  fingerprint(`${scheme} exported vs selected resolved`, shaValue(exportedResolved),
    shaValue(candidateResolved));
  profiles[scheme] = { activeSha256, activeRecordedFingerprint: doc.resolvedMaterialSha256,
    inactiveSha256: shaValue(exportedResolved), resolvedMaterial: exportedResolved };
  selected[scheme] = { rung: fit.selected, fitSha256: sha(readFileSync(fitPath)),
    sweepFileSha256: sha(readFileSync(sweepPath)), sourceSha256: sweep.sourceSha256,
    candidateFileSha256: sha(readFileSync(candidatePath)), resolvedMaterial: candidateResolved };
}
const sourceSha256: Record<string, string> = {};
function sourceFiles(dir: string): void {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = resolve(dir, entry.name);
    if (entry.isDirectory()) sourceFiles(path);
    else if (/\.(ts|html)$/.test(entry.name)) sourceSha256[relative(repo, path)] = sha(readFileSync(path));
  }
}
for (const directory of ["packages/renderer-webgpu/src", "packages/platform-web/src",
  "packages/core/src", "packages/calibration/src", "packages/calibration/web"]) {
  sourceFiles(resolve(repo, directory));
}
const instrumentSha256 = Object.fromEntries([
  "declare.ts", "frozen-read.ts", "read-guards.ts", "dry-refusals.ts", "score-bound.py",
  "declaration.json", "partition.json", "sweep-plan.json",
  "../2026-09-14-w27c-g1d/plurality.json", "../2026-09-11-w27c-g1b/bound.json",
  "../2026-09-11-w27c-g1b/checking-bed.json", "../2026-09-11-w27c-g1b/decomposition.json",
].map((file) => [relative(repo, resolve(here, file)), sha(readFileSync(resolve(here, file)))]));
for (const file of ["apps/reference-apple/scenes.json", "apps/reference-apple/fixtures/manifest.json"]) {
  instrumentSha256[file] = sha(readFileSync(resolve(repo, file)));
}
writeFileSync(output, `${JSON.stringify({
  declaredIn: "W28 G1 / claims §5.145; W28 Decision Log 2 including (f); X10/X11",
  lineage: "2026-09-14-w27c-g1d/declare.ts; prior evidence immutable",
  frozenAt: new Date().toISOString(), repositoryHead: execFileSync("git",
    ["-C", repo, "rev-parse", "HEAD"], { encoding: "utf8" }).trim(), mainHead,
  patch: recededMaterialProfile, patchSha256: sha(JSON.stringify(recededMaterialProfile)),
  profiles, selected, activeDocuments, sourceSha256, instrumentSha256,
  sceneSpecSha256: shaValue(json(resolve(repo, "apps/reference-apple/scenes.json"))),
  holdout: { statusAtDeclaration: "unread", cells, recoveredLineage,
    rule: "one read per frozen configuration; no constant changes after the read",
    limitation: declaration.holdout.limitation },
  adoptsNoFloor: old.adoptsNoFloor,
}, null, 2)}\n`, { flag: "wx" });
console.log(JSON.stringify({ sealed: output, profiles, holdoutCells: cells }, null, 2));
