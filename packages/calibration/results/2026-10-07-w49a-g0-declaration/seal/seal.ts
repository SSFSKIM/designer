/**
 * W49a G0: freeze a landed candidate as the dark `-glass0.25` RECEDED profile document — W48's seal
 * (`results/2026-10-06-w48-g0-declaration/seal/seal.ts`) COPIED and re-bound to W49a (charter
 * `2026-10-07-w49-authorised-list-repair.md`, Decision Logs 1 and 3). W48's committed copy is untouched.
 *
 *   cd packages/calibration
 *   pnpm exec tsx results/2026-10-07-w49a-g0-declaration/seal/seal.ts <label> <method.json> \
 *     --candidates DIR --manifest FILE [--profiles DIR]
 *
 * **What W49a changes from W48's seal, and why:**
 * - **Only the receded dark document is sealed** (Decision Log 1: family R is the receded far delta). The
 *   candidate's active dark endpoint must be the shipped `b2d074d2df24` snapshot's patch and digest, as the
 *   live active file must be its bytes; the light pair is untouched (X60). The receded file it replaces must
 *   be the shipped `29da6a888a23` bytes, so a seal runs once and never over a stranger's bytes.
 * - **X75 refuses an opaque endpoint** (Decision Log 3): the active, and the receded merged over it as the
 *   root poses it, keep `alphaBase` at or under 0.95 at every span 0..1024 CSS px, dpr 1 and 2, both
 *   variants and tiers (`scripts/no-opaque-glass.ts`), checked before the digest.
 * - **X76: no receded leaf is silently materialised** (Decision Log 3). W48's seal recorded a key named at
 *   the value its active resolves it to as `materialised`, with no method, and that is how the receded far
 *   deltas shipped at the active's 0.2. Here every such leaf, whether carried from the snapshot's record or
 *   newly named, must be HELD explicitly: `method.json` gives it as `{ "held": [<reading>, ...] }` and the
 *   record says `status: "held"` with that reading. Every leaf FITTED on the active (an `entries` record of
 *   status `measured` there) that the receded does not name is the receded's by inheritance and needs the
 *   same explicit hold. A leaf with neither a method nor a hold refuses. A moved leaf's method is a list of
 *   strings, as before.
 * - **No compiled-in G1 path**: `--candidates` and `--manifest` are required, never W44's-W48's.
 *
 * Unchanged from W48's seal: the leaf set is the 0.5 twin's plus X64's and X67's; every leaf moved from the
 * snapshot is one of the candidate's declared overrides; an added leaf must read back from the resolved
 * material; `resolvedMaterialSha256` under the current digest rule (the receded over the sealed active) must
 * equal the candidate's own endpoint digest; every check passes before the file is written.
 */

import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
import { mergeMaterialProfiles } from "@vitreajs/vitrea-web";

import { readCandidateDocument, resolvedDigest } from "../../../scripts/candidate-document";
import { opaqueGlassViolations, summariseOpaqueGlass } from "../../../scripts/no-opaque-glass";

const HERE = resolve(fileURLToPath(new URL(".", import.meta.url)));
const EVIDENCE = resolve(HERE, "..");
const PACKAGE = resolve(HERE, "../../..");
const REPO = resolve(PACKAGE, "../..");
const DOCUMENTS = join(EVIDENCE, "documents");
const CHARTER = "docs/doperpowers/specs/2026-10-07-w49-authorised-list-repair.md";
/** X64 and X67: the leaves the receded dark document may name beside its twin's. */
const MAY_ADD: readonly string[] = ["sizeScatterRampStartFar1x", "sizeScatterFloor", "sizeScatterFloor2x",
  "sizeHeavyTapSigma", "sizeHeavySecondShare", "sizeHeavySecondShareFar2x", "sizeHeavySecondSigma",
  "sizeHeavySecondSigma2x", "sizeScatterScaleGain", "optics.regular.blurSigma", "sizeScatterSpanMax",
  "sizeScatterSpanMax2x", "sizeOcclusionGain", "tintAlphaFar1x", "tintAlphaFar2x", "sizeFineTapShare",
  "sizeFineTapSigma", "sizeFineTapSigma2x"];
const pathValue = (node: unknown, path: string): unknown => path.split(".").reduce<unknown>(
  (at, part) => (at !== null && typeof at === "object" && !Array.isArray(at) ? (at as Record<string, unknown>)[part]
    : undefined), node);
/** The snapshots (X62 at this charter): the shipped 0.28.0 dark pair and the untouched light pair. */
const SNAPSHOT: Readonly<Record<string, string>> = {
  "active.dark": "b2d074d2df2444a614304d11e906b5f91d8968bce161efbd8f34fc8da5be9186",
  "receded.dark": "29da6a888a23a9a1b5fa3dba6128ed1eedf160030e3dd4fd2e2fc7cb6a6c2389",
  "active.light": "ebc3d9105a4a40565278845071113c6a5368b304910362786b8cbfb4cc66bb44",
  "receded.light": "12712d534b78017f68fee440cb9d9d451178aae1b80db36c0043fdfb1b591203",
};
const TWIN_RECEDED = { key: "apple-macos-27.0-1x-dark-standard-glass0.5-receded", sha12: "5cec8c961201" };

type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
type Method = string[] | { held: string[] };
const sha256 = (bytes: string | Buffer): string => createHash("sha256").update(bytes).digest("hex");
const rel = (path: string): string => relative(REPO, path);
const leaves = (patch: Json, prefix = ""): Record<string, Json> =>
  Object.fromEntries(Object.entries(patch as Record<string, Json>).flatMap(([key, value]) =>
    value !== null && typeof value === "object" && !Array.isArray(value)
      ? Object.entries(leaves(value, `${prefix}${key}.`))
      : [[`${prefix}${key}`, value]]));
const keyOf = (pose: "active" | "receded", scheme: "light" | "dark"): string =>
  `apple-macos-27.0-1x-${scheme}-standard-glass0.25${pose === "receded" ? "-receded" : ""}`;
const snapshot = (slot: string): { text: string; doc: Record<string, Json> } => {
  const text = readFileSync(join(DOCUMENTS, `${SNAPSHOT[slot]!.slice(0, 12)}.json`), "utf8");
  if (sha256(text) !== SNAPSHOT[slot]) throw new Error(`${slot}: the snapshot does not hash to its name (X62)`);
  return { text, doc: JSON.parse(text) as Record<string, Json> };
};
const ours = (path: string, what: string): string => {
  const full = resolve(path);
  if (/(^|\/)2026-10-0[3567]-w4[45678]-[^/]*(\/|$)/.test(full) || /(^|\/)vitrea-w4[45678](\/|$)/.test(full)) {
    throw new Error(`${what}: ${full} is W44's-W48's evidence or scratch; W49a seals its own`);
  }
  return full;
};
const isHold = (m: Method | undefined): m is { held: string[] } =>
  m !== undefined && !Array.isArray(m) && Array.isArray(m.held) && m.held.length > 0
  && m.held.every((line) => typeof line === "string" && line.trim() !== "");
const isMethod = (m: Method | undefined): m is string[] =>
  Array.isArray(m) && m.length > 0 && m.every((line) => typeof line === "string" && line.trim() !== "");

const argv = process.argv.slice(2);
const flag = (name: string): string | undefined => {
  const at = argv.indexOf(`--${name}`);
  return at < 0 ? undefined : argv[at + 1];
};
const positional = argv.filter((a, i) => !a.startsWith("--") && !(i > 0 && argv[i - 1]!.startsWith("--")));
const [label, methodPath] = positional;
const candidatesFlag = flag("candidates");
const manifestFlag = flag("manifest");
if (label === undefined || methodPath === undefined || candidatesFlag === undefined || manifestFlag === undefined) {
  throw new Error("usage: seal.ts <label> <method.json> --candidates DIR --manifest FILE [--profiles DIR]");
}
const CANDIDATES = ours(candidatesFlag, "the candidates");
const PROFILES = ours(flag("profiles") ?? join(PACKAGE, "profiles"), "the profiles directory");
const MANIFEST = ours(manifestFlag, "the seal's record");
const METHOD = JSON.parse(readFileSync(resolve(methodPath), "utf8")) as Record<string, Method>;
const FOLDER = ours(join(CANDIDATES, label), "the candidate");
const CANDIDATE = join(FOLDER, "candidate.json");
const candidate = readCandidateDocument(CANDIDATE);
const candidateSha = sha256(readFileSync(CANDIDATE));
const spec = JSON.parse(readFileSync(join(FOLDER, "spec.json"), "utf8")) as {
  base?: string;
  overrides?: Record<string, Record<string, Json>>;
};
if ((spec.base ?? "b2d074") !== "b2d074") throw new Error(`${label}: base ${spec.base}; W49a seals over b2d074 only`);

// The active dark and both light endpoints: the snapshots' patches and digests, files untouched.
for (const slot of ["active.dark", "active.light", "receded.light"] as const) {
  if (Object.keys(spec.overrides?.[slot] ?? {}).length > 0) {
    throw new Error(`${slot}: the candidate's spec moves it; W49a seals the receded dark document only`);
  }
  const endpoint = JSON.parse(readFileSync(candidate.endpoints[slot].path, "utf8")) as Record<string, Json>;
  const { doc } = snapshot(slot);
  if (JSON.stringify(endpoint["patch"]) !== JSON.stringify(doc["patch"]) ||
      endpoint["resolvedMaterialSha256"] !== doc["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: the candidate's endpoint is not the snapshot`);
  }
  const live = join(PROFILES, `${keyOf(slot.startsWith("active") ? "active" : "receded",
    slot.endsWith("dark") ? "dark" : "light")}.json`);
  if (sha256(readFileSync(live)) !== SNAPSHOT[slot]) throw new Error(`${rel(live)} is not the snapshot's bytes`);
}

const slot = "receded.dark";
const key = keyOf("receded", "dark");
const out = join(PROFILES, `${key}.json`);
const liveSha = sha256(readFileSync(out));
if (liveSha !== SNAPSHOT[slot]) {
  throw new Error(`${rel(out)} hashes to ${liveSha.slice(0, 12)}, not the snapshot ${SNAPSHOT[slot]!.slice(0, 12)}; `
    + "the seal runs once, over the shipped receded dark 0.25 document (X62)");
}
const { doc: before0 } = snapshot(slot);
const { doc: active0 } = snapshot("active.dark");
const endpointFile = candidate.endpoints[slot].path;
const endpoint = JSON.parse(readFileSync(endpointFile, "utf8")) as Record<string, Json>;
const twinPath = join(PROFILES, `${TWIN_RECEDED.key}.json`);
const twinText = readFileSync(twinPath, "utf8");
if (!sha256(twinText).startsWith(TWIN_RECEDED.sha12)) throw new Error(`${rel(twinPath)} is not its X41-frozen bytes`);
const twin = JSON.parse(twinText) as Record<string, Json>;
const patch = endpoint["patch"] as Record<string, Json>;
const activePatch = active0["patch"] as Record<string, Json>;

const mine = leaves(patch);
const theirs = leaves(twin["patch"]!);
const before = leaves(before0["patch"]!);
const extra = Object.keys(mine).filter((k) => !(k in theirs)).sort();
const dropped = Object.keys(theirs).filter((k) => !(k in mine)).sort();
if (dropped.length > 0 || extra.some((k) => !MAY_ADD.includes(k))) {
  throw new Error(`${slot}: the leaf set is not the 0.5 twin's plus X64's and X67's: extra `
    + `${extra.join(", ") || "none"}, dropped ${dropped.join(", ") || "none"} (X44, X64, X67)`);
}
const movedFromSnapshot = Object.keys(mine).filter((k) => JSON.stringify(mine[k]) !== JSON.stringify(before[k])).sort();
const declared = Object.keys(spec.overrides?.[slot] ?? {});
const undeclared = movedFromSnapshot.filter((k) => !declared.includes(k));
if (undeclared.length > 0) throw new Error(`${slot}: moves undeclared leaves ${undeclared.join(", ")}`);

// X75, before the digest: neither the active nor the receded as posed draws opaque glass.
for (const [what, posed] of [["active.dark", activePatch],
  ["receded.dark", mergeMaterialProfiles(activePatch as never, patch as never)]] as const) {
  const opaque = summariseOpaqueGlass(opaqueGlassViolations(posed as unknown as MaterialProfilePatch));
  if (opaque.length > 0) throw new Error(`${what}: draws opaque glass, alphaBase above 0.95 (X75): ${opaque.join("; ")}`);
}

const activeResolved = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, activePatch as unknown as MaterialProfilePatch);
const resolvedMaterial = withMaterialOverrides(activeResolved, patch as unknown as MaterialProfilePatch);
for (const leaf of extra) {
  if (JSON.stringify(pathValue(resolvedMaterial, leaf)) !== JSON.stringify(mine[leaf])) {
    throw new Error(`${slot}: '${leaf}' does not read back from the resolved material (X67)`);
  }
}
const digest = resolvedDigest(resolvedMaterial);
if (digest !== endpoint["resolvedMaterialSha256"]) {
  throw new Error(`${slot}: resolves to ${digest}, and the candidate recorded ${String(endpoint["resolvedMaterialSha256"])}`);
}

// X76: every leaf the receded states at its active's resolved value, and every active-fitted leaf it does
// not name, is HELD with a reading; nothing is materialised silently. A moved leaf carries its method.
const inheritedValue = (leaf: string): unknown => pathValue(activeResolved, leaf);
const recordOf = (leaf: string): string | undefined =>
  ((before0["entries"] ?? {}) as Record<string, { status?: string }>)[leaf]?.status;
// A leaf the snapshot MEASURED keeps its record even where its value happens to equal the active's.
const atActive = Object.keys(mine).filter((k) => MAY_ADD.includes(k)
  && JSON.stringify(inheritedValue(k)) === JSON.stringify(mine[k])
  && (recordOf(k) !== "measured" || movedFromSnapshot.includes(k))).sort();
const activeEntries = (active0["entries"] ?? {}) as Record<string, { status?: string }>;
const activeFitted = Object.keys(leaves(activePatch)).filter((k) => activeEntries[k]?.status === "measured"
  && !(k in mine)).sort();
const silent: string[] = [];
const entries: Record<string, Json> = {};
const beforeEntries = (before0["entries"] ?? {}) as Record<string, Json>;
for (const [leaf, entry] of Object.entries(beforeEntries)) {
  if (leaf !== "held" && !movedFromSnapshot.includes(leaf) && !atActive.includes(leaf)) entries[leaf] = entry;
}
for (const leaf of [...atActive, ...activeFitted]) {
  const m = METHOD[leaf];
  if (movedFromSnapshot.includes(leaf) && isMethod(m)) continue;   // moved TO the active's value, by a fit
  if (!isHold(m)) {
    silent.push(leaf);
    continue;
  }
  entries[leaf] = { status: "held", value: (mine[leaf] ?? inheritedValue(leaf)) as Json,
    inheritedFrom: `${keyOf("active", "dark")}.json (resolved)`, named: leaf in mine, reading: m.held };
}
if (silent.length > 0) {
  throw new Error(`${slot}: ${silent.length} leaf/leaves would be inherited from the active silently: `
    + `${silent.join(", ")}; give each an explicit { "held": [<reading>] } in the method record (X76)`);
}
for (const leaf of movedFromSnapshot) {
  if (entries[leaf] !== undefined) continue;
  const m = METHOD[leaf];
  if (!isMethod(m)) throw new Error(`${slot}: no method recorded for the moved leaf ${leaf}`);
  entries[leaf] = { status: "measured", value: mine[leaf]!, previous: before[leaf] ?? null,
    previousAt05: theirs[leaf] ?? null, method: m };
}
entries["held"] = beforeEntries["held"] ?? { status: "held" };
const activeFile = `${keyOf("active", "dark")}.json`;
const document: Record<string, Json> = {
  "$comment": [
    "The macOS 27 dark RECEDED material at the Glass appearance slider's 0.25 position",
    `(\`NSGlassTintAmount\` 0.25), as a difference over ${activeFile}, its own scheme's 0.25 active document.`,
    "",
    "W49a G1: the receded far delta (family R) refitted so the unfocused body never draws opaque (X75),",
    "over b2d074d2df24 unmoved. It supersedes the document named in `supersedes`; `entries` keeps the",
    "snapshot's record for every leaf left where it was, records each moved leaf with its method, and",
    "records every leaf the receded inherits from the active as an explicit hold with its reading (X76).",
  ],
  profileKey: key,
  schemaVersion: (before0["schemaVersion"] as number | undefined) ?? 1,
  recordedAt: new Date().toISOString().slice(0, 10),
  recordedBy: "W49a G1",
  colorSpace: (before0["colorSpace"] as string | undefined) ?? "srgb",
  kind: (before0["kind"] as string | undefined) ?? "receded-endpoint",
  appliesOver: `packages/calibration/profiles/${activeFile}`,
  resolvedOverActiveDocument: activeFile,
  glassTintAmount: 0.25,
  twin: { path: rel(twinPath), sha256: sha256(twinText) },
  derivedFromCandidate: {
    declaration: rel(CANDIDATE), declarationSha256: candidateSha,
    endpoint: rel(endpointFile), endpointSha256: candidate.endpoints[slot].sha256,
  },
  supersedes: { path: `packages/calibration/profiles/${key}.json`, sha256: liveSha,
    resolvedMaterialSha256: before0["resolvedMaterialSha256"]!,
    generation: "packages/calibration/results/generations/b2d074d2df24.json" },
  resolvedMaterialSha256: digest,
  resolvedMaterialSha256Rule: MATERIAL_DIGEST_RULE_VERSION,
  measurement: {
    gate: `W49a G1; charter ${CHARTER}; Decision Logs 2 and 4 (part 2's landing and selection rules)`,
    candidate: rel(CANDIDATE),
  },
  entries,
  patch,
};
const text = `${JSON.stringify(document, null, 2)}\n`;
if (existsSync(MANIFEST)) throw new Error(`${rel(MANIFEST)} exists; a seal's record is written once`);
writeFileSync(out, text);
writeFileSync(MANIFEST, `${JSON.stringify({
  what: `W49a G1: candidate ${label} sealed as the dark -glass0.25 receded document; the active and light untouched`,
  charter: CHARTER,
  candidate: { declaration: rel(CANDIDATE), sha256: candidateSha },
  profiles: rel(PROFILES),
  digestRule: MATERIAL_DIGEST_RULE_VERSION,
  document: { file: `${key}.json`, fileSha256: sha256(text), resolvedMaterialSha256: digest,
    previousResolvedMaterialSha256: before0["resolvedMaterialSha256"]!, movedFromSnapshot,
    heldUnderX76: [...atActive, ...activeFitted].filter((k) => !movedFromSnapshot.includes(k)),
    supersedes: liveSha, candidateEndpointSha256: candidate.endpoints[slot].sha256 },
}, null, 2)}\n`);
console.log(JSON.stringify({ file: rel(out), digest, movedFromSnapshot, heldUnderX76: Object.keys(entries)
  .filter((k) => (entries[k] as { status?: string })?.status === "held" && k !== "held") }, null, 2));
