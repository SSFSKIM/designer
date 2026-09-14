/** W28 G2 refuses invalid evidence before measurement. Shared by live and dry paths. */
import { createHash } from "node:crypto";
import { existsSync, realpathSync, readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, relative, resolve, sep } from "node:path";
import { captureIntegrityRefusal, type DeclaredCapture } from "../../src/capture-integrity";

// This is G1d's canonical resolved-material encoding; raw patches retain their own key order.
export const canonical = (v: any): any => Array.isArray(v) ? v.map(canonical)
  : v !== null && typeof v === "object"
    ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, canonical(v[k])])) : v;
export const sha = (data: string | Buffer | Uint8Array): string =>
  createHash("sha256").update(data).digest("hex");
export const shaValue = (v: unknown): string => sha(JSON.stringify(canonical(v)));

export function fingerprint(name: string, actual: unknown, expected: unknown): void {
  if (typeof actual !== "string" || typeof expected !== "string" || actual !== expected) {
    throw new Error(`${name}: fingerprint mismatch (${String(actual)} != ${String(expected)})`);
  }
}
/** The pinned baseline, not a mutable working document, identifies active material records. */
export function activeDocument(name: string, doc: any, baseline: any): boolean {
  if (baseline?.schemaVersion !== 1 || typeof baseline?.profileKey !== "string" ||
      baseline?.patch === null || typeof baseline?.patch !== "object" ||
      typeof baseline?.resolvedMaterialSha256 !== "string") return false;
  fingerprint(`${name} active recorded vs main`, doc.resolvedMaterialSha256,
    baseline.resolvedMaterialSha256);
  return true;
}

/** Bind the fitted rung to the runtime that measured it; documentation commits do not matter. */
export function selectedSweep(matrix: any, selected: string, rung: any, repo: string): void {
  fingerprint("selected sweep label", matrix.label, selected);
  fingerprint("selected sweep tier", matrix.renderer, "webgpu");
  fingerprint("selected sweep inactive", matrix.inactiveSha256, rung.inactiveSha256);
  fingerprint("selected sweep patch", matrix.patchSha256, rung.patchSha256);
  if (!matrix.sourceSha256 || Object.keys(matrix.sourceSha256).length === 0) {
    throw new Error("Selected sweep source identity missing");
  }
  for (const [file, expected] of Object.entries(matrix.sourceSha256)) {
    fingerprint(`selected sweep source ${file}`, sha(readFileSync(resolve(repo, file))), expected);
  }
}

export const gitBlobOid = (bytes: Buffer): string => createHash("sha1")
  .update(`blob ${bytes.length}\0`).update(bytes).digest("hex");

export function machineReady(value: any): void {
  if (value?.reduceTransparency !== 0 || value?.increaseContrast !== 0) {
    throw new Error("Machine accessibility settings must both be proved off");
  }
}

export function nativeAdmission(value: {
  checking: boolean; isHoldout: boolean; recovered: boolean;
  run: { sha256: string } | undefined; entry: any; state: string;
}): { isControl: false; isHoldout: boolean; preAttestationRecovered: boolean } {
  if (value.checking && (value.recovered || value.run === undefined)) {
    throw new Error("A checking cell must carry its seven-run plurality");
  }
  if (value.recovered) {
    if (!value.isHoldout) throw new Error("Recovered evidence is admitted only for declared holdouts");
  } else {
    if (value.run === undefined) throw new Error("Bed cell plurality missing");
    attest(value.entry, value.state);
  }
  return { isControl: false, isHoldout: value.isHoldout, preAttestationRecovered: value.recovered };
}

export function admitRead(candidate: boolean, holdout: boolean): void {
  if (candidate && holdout) throw new Error("A candidate cannot read the frozen holdout");
}

/** G1d bound clause 5's presentation refusal, with no weakened recovered path for D. */
export function attest(entry: any, state: string): void {
  if (state !== "inactive") {
    if (entry?.presentedActive !== true) throw new Error("Native active presentation unproved");
    return;
  }
  const p = entry?.presentation;
  if (entry?.presentedActive !== false || p?.observedPose !== "inactive" ||
      p?.isKeyWindow !== false || p?.appIsActive !== false) {
    throw new Error("Native inactive presentation unproved (bound clause 5)");
  }
}

export function pageReady(report: any, declared: DeclaredCapture, renderer: string,
  ready: boolean): void {
  if (!ready) throw new Error("Page readiness not proved");
  if (!report?.canvas || !Array.isArray(report.problems)) throw new Error("Missing page report");
  const refusal = captureIntegrityRefusal(report, declared);
  if (refusal !== undefined) throw new Error(refusal);
  if (report.pixelSize?.[0] !== declared.canvas.width * declared.scale ||
      report.pixelSize?.[1] !== declared.canvas.height * declared.scale) {
    throw new Error("Page pixel dimensions differ from declaration");
  }
  if (!Array.isArray(report.groups) || report.groups.length === 0 ||
      report.groups.some((g: any) => g.state?.activeRenderer !== renderer) ||
      (renderer === "webgpu" && (report.adapter?.ok !== true || report.adapter?.isFallback !== false))) {
    throw new Error("Page did not draw on its declared hardware tier");
  }
}
export function repeated(first: Buffer | undefined, next: Buffer): void {
  if (first !== undefined && !first.equals(next)) throw new Error("Nondeterministic repeats");
}

export function captureBytes(row: any, bytes: Buffer): void {
  fingerprint("retained capture", sha(bytes), row.captureSha256);
}

/** CSS is a record-only coherence read and must never spend a sealed holdout pair. */
export function readCell(renderer: string, cell: string, holdout: ReadonlySet<string>): boolean {
  if (renderer !== "webgpu" && renderer !== "css") throw new Error("Unknown renderer");
  return renderer === "webgpu" || !holdout.has(cell);
}

export function admitScoring(renderer: string, scored: boolean): void {
  if (scored && renderer !== "webgpu") throw new Error("Only WebGPU rows may be scored by the bound");
}

/** A retained id is not a measurement. Require the evidence the live writer actually emits. */
export function measurementEvidence(row: any, renderer = "webgpu"): void {
  const bad = () => { throw new Error("Incomplete or invalid measurement evidence"); };
  if (!["webgpu", "css"].includes(renderer) || (renderer === "css" && row?.isHoldout)) bad();
  admitScoring(renderer, row?.scored);
  const positivePair = (v: any) => Array.isArray(v) && v.length === 2 &&
    v.every((n: any) => Number.isInteger(n) && n > 0);
  if (!row || !Number.isFinite(row.deltaE?.mean) || row.deltaE.mean < 0 ||
      !Number.isInteger(row.body?.n) || row.body.n <= 0 || row.repeats !== 2 ||
      typeof row.capture !== "string" || typeof row.nativePath !== "string" ||
      typeof row.isHoldout !== "boolean" || row.isControl !== false ||
      typeof row.preAttestationRecovered !== "boolean" || typeof row.scored !== "boolean" ||
      !Array.isArray(row.groups) || row.groups.length === 0) bad();
  for (const key of ["deltaE", "webY", "nativeY", "webSD", "nativeSD", "webChroma", "nativeChroma"]) {
    if (!Number.isFinite(row.body[key]) || row.body[key] < 0) bad();
  }
  for (const key of ["captureSha256", "nativeSha256", "backgroundSha256"]) {
    if (typeof row[key] !== "string" || !/^[a-f0-9]{64}$/.test(row[key])) bad();
  }
  const g = row.geometry;
  if (!positivePair(g?.capturedPixels) || !positivePair(g?.pixelSize) ||
      shaValue(g.capturedPixels) !== shaValue(g.pixelSize) ||
      row.body.n > g.capturedPixels[0] * g.capturedPixels[1] ||
      ![1, 2].includes(row.scale) || g.requestedScale !== row.scale ||
      g.devicePixelRatio !== row.scale ||
      g.canvas?.width * row.scale !== g.pixelSize[0] ||
      g.canvas?.height * row.scale !== g.pixelSize[1] ||
      (renderer === "webgpu" && (row.adapter?.ok !== true || row.adapter?.isFallback !== false)) ||
      !Array.isArray(row.actualGroups) || row.actualGroups.length === 0 ||
      row.actualGroups.some((group: any) => group.state?.activeRenderer !== renderer) ||
      !Array.isArray(row.problems) || row.problems.length !== 0) bad();
  if (row.preAttestationRecovered) {
    if (!row.isHoldout || row.scored || row.nativeSource !== "recovered" ||
        !row.groups.includes("H") || row.nativeRun !== null ||
        !/^[a-f0-9]{40}$/.test(row.recoveredLineage?.nativeBlobOid ?? "") ||
        !/^[a-f0-9]{40}$/.test(row.recoveredLineage?.backgroundBlobOid ?? "")) bad();
  } else {
    if (!["bundle", "sitting"].includes(row.nativeSource) ||
        typeof row.nativeRun !== "string" || !row.nativeRun ||
        !["rest", "pressed", "inactive"].includes(row.state)) bad();
    attest(row.nativeAttestation, row.state);
  }
}

export function resumeRead(resumed: any, identity: any,
  population: readonly { profile: string; scene: string }[]): void {
  if (resumed === undefined) return;
  for (const key of Object.keys(identity)) {
    fingerprint(`resume ${key}`, shaValue(resumed[key] ?? null), shaValue(identity[key]));
  }
  const permitted = new Set(population.map((c) => `${c.profile}/${c.scene}`));
  const seen = new Set<string>();
  if (!Array.isArray(resumed.rows)) throw new Error("Resume rows missing");
  for (const row of resumed.rows) {
    const cell = `${row.profile}/${row.scene}`;
    if (seen.has(cell)) throw new Error(`Duplicate resume row ${cell}`);
    if (!permitted.has(cell) || row.repeats !== 2) throw new Error(`Invalid resume row ${cell}`);
    measurementEvidence(row, identity.renderer ?? "webgpu");
    seen.add(cell);
  }
}
export function outputAvailable(path: string, exists: boolean, resumePath?: string): void {
  if (exists && (resumePath === undefined || resolve(path) !== resolve(resumePath))) {
    throw new Error(`Refusing output overwrite ${path}`);
  }
}

/** Resolve existing ancestors so a scratch symlink cannot route writes into the repository. */
export function scratchPath(path: string, repo: string): void {
  const physical = (p: string): string => {
    let ancestor = resolve(p);
    while (!existsSync(ancestor) && dirname(ancestor) !== ancestor) ancestor = dirname(ancestor);
    return resolve(realpathSync(ancestor), relative(ancestor, resolve(p)));
  };
  const common = execFileSync("git", ["-C", repo, "rev-parse", "--path-format=absolute",
    "--git-common-dir"], { encoding: "utf8" }).trim();
  const roots = [physical(repo), dirname(physical(common))];
  const destination = physical(path);
  if (roots.some((root) => destination === root || destination.startsWith(`${root}${sep}`))) {
    throw new Error(`Scratch output must be outside the repository: ${path}`);
  }
}
