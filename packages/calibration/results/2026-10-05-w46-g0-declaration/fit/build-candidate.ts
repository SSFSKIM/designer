/**
 * W46 G0 (a): build one scratch candidate — four endpoint documents and the candidate declaration
 * candidate mode draws. W45 G0's builder (`results/2026-10-03-w45-g0-operator/fit/build-candidate.ts`),
 * ported for W46 (charter clause 1; X60, X62, X64); W45's and W44's committed copies are untouched.
 * The ladders of clause 4, the level check and the fit of G1 all build through THIS file.
 *
 *   cd packages/calibration
 *   W46_CANDIDATE_ROOT=<dir> pnpm exec tsx results/2026-10-05-w46-g0-declaration/fit/build-candidate.ts <spec.json>
 *
 * The spec names a label and, per DARK endpoint slot, every leaf that moves from the slot's snapshot:
 *
 *   { "label": "i-ta0.8", "note": "...",
 *     "overrides": { "active.dark": { "optics.regular.tintAlpha": 0.8 },
 *                    "receded.dark": { "sizeScatterRampStartFar1x": 0.2 } } }
 *
 * **What W46 changes, and why:**
 * - **The starting point is the four snapshots (X62).** Every endpoint starts from
 *   `documents/<sha12>.json` (dark d0219cd684bf / f0b36a71772a, light ebc3d9105a4a / 12712d534b78),
 *   each checked against its full SHA-256 before it is read. The live `profiles/` 0.25 documents are
 *   never read: G1's seal replaces the dark pair there by design, and W45's builder, which read the
 *   live light pair as c05, failed its own declaration check after the freeze (the tracker's W45
 *   entry, closed here).
 * - **Only the dark material moves (X60).** An override in `active.light` or `receded.light`
 *   refuses; the light endpoints come out patch- and digest-identical to the light snapshots.
 * - **X64, exactly.** A dark slot may ADD the inherited leaves X64 lists for it, by name, and no
 *   other leaf its snapshot does not name: active `sizeScatterFloor2x`, the six ramp starts and
 *   `sizeHeavySecondShareFar2x`; receded `sizeScatterRampStartFar1x`, `sizeScatterFloor` and `…2x`,
 *   `sizeHeavyTapSigma`, `sizeHeavySecondShare`, `sizeHeavySecondShareFar2x`, `sizeHeavySecondSigma`
 *   and `…2x`, and `sizeScatterScaleGain`, each a difference over the active resolved material (which
 *   resolves every one of them). W45's operator key in the light slots and W44's receded second-tap
 *   condition are gone with the light slots. Materialised at its resolved value a leaf moves neither
 *   the material nor its digest (W31 Rule 2 drops identity leaves by RESOLVED value), only the file.
 * - **One label grammar** (`labels.json`, read here and by `search.py`): the tracker's W45 entry, a
 *   receded label the builder refused, is closed by stating the pattern and the marks once.
 * - **The root is explicit and never W44's, W45's or a profiles directory.** `W46_CANDIDATE_ROOT`.
 *
 * Unchanged from W45's builder, each a refusal rather than a convention: X44 at the base (each 0.25
 * snapshot names exactly its 0.5 twin's leaves, the light ones beside the keys W45's narrowing let
 * them add, which W45's landed pair names; the twins are read under `profiles/` and checked at
 * their X41-frozen hashes); an existing leaf moves only at its own shape and as finite numbers;
 * patches over the unmoved default, each receded endpoint a difference over its scheme's NEW active
 * document; the scratch key token `glass0.250` (candidate mode refuses a shipped key); a slot with no
 * leaf of its own moved over an unmoved base must read its snapshot's digest; a label that exists
 * refuses; `readCandidateDocument` reads the declaration back.
 *
 * Output: `<W46_CANDIDATE_ROOT>/<label>/` with the four documents, `candidate.json` and `spec.json`.
 */

import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

import {
  CANDIDATE_DECLARATION_KIND,
  cssTierMappingSha256,
  readCandidateDocument,
  resolvedDigest,
} from "../../../scripts/candidate-document";

const HERE = resolve(fileURLToPath(new URL(".", import.meta.url)));
const EVIDENCE = resolve(HERE, "..");
const PROFILES = resolve(HERE, "../../../profiles");
const DOCUMENTS = join(EVIDENCE, "documents");
const LABELS = JSON.parse(readFileSync(join(HERE, "labels.json"), "utf8")) as { pattern: string };
const ROOT_ENV = process.env["W46_CANDIDATE_ROOT"];
if (ROOT_ENV === undefined || ROOT_ENV === "") {
  throw new Error("W46_CANDIDATE_ROOT names where the candidate is written; there is no default (clause 1)");
}
const OUT_ROOT = resolve(ROOT_ENV);
if (/(^|\/)2026-10-03-w4[45]-[^/]*(\/|$)/.test(OUT_ROOT) || /(^|\/)vitrea-w4[45](\/|$)/.test(OUT_ROOT)) {
  throw new Error(`${OUT_ROOT} is W44's or W45's evidence or scratch; W46 builds into its own (clause 1)`);
}
if (OUT_ROOT === PROFILES || OUT_ROOT.startsWith(`${PROFILES}/`)) {
  throw new Error(`${OUT_ROOT} is the profiles directory; a candidate is never written there (X62)`);
}
const SCRATCH_GLASS_TOKEN = "glass0.250";

type Slot = "active.light" | "active.dark" | "receded.light" | "receded.dark";
const SLOTS: readonly Slot[] = ["active.light", "active.dark", "receded.light", "receded.dark"];
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

/** The snapshots (X62): slot -> full SHA-256 of `documents/<sha12>.json` (bindings.DOCUMENT_SHA). */
const SNAPSHOT: Readonly<Record<Slot, string>> = {
  "active.dark": "d0219cd684bff75b2ba5c34d4f6cb2f6d49e32aab7cc27464220a05910f2638f",
  "receded.dark": "f0b36a71772a00a647c10a280ae73b92d21be1f0c65599334c4e3cdf36cb7f86",
  "active.light": "ebc3d9105a4a40565278845071113c6a5368b304910362786b8cbfb4cc66bb44",
  "receded.light": "12712d534b78017f68fee440cb9d9d451178aae1b80db36c0043fdfb1b591203",
};
/** X41's frozen 0.5 twins (bindings.TWIN_05): key -> twelve-hex file hash. */
const TWIN_05: Readonly<Record<string, string>> = {
  "apple-macos-27.0-1x-dark-standard-glass0.5": "0eac5b294cc2",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded": "5cec8c961201",
  "apple-macos-27.0-1x-light-standard-glass0.5": "85ad7f7e3e0d",
  "apple-macos-27.0-1x-light-standard-glass0.5-receded": "30fbe05986ae",
};
/** X64: the inherited leaves each dark document may name (bindings.X64). */
const X64: Readonly<Record<"active.dark" | "receded.dark", readonly string[]>> = {
  "active.dark": ["sizeScatterFloor2x", "sizeScatterRampStartThin1x", "sizeScatterRampStartThick1x",
    "sizeScatterRampStartFar1x", "sizeScatterRampStartThin2x", "sizeScatterRampStartThick2x",
    "sizeScatterRampStartFar2x", "sizeHeavySecondShareFar2x"],
  "receded.dark": ["sizeScatterRampStartFar1x", "sizeScatterFloor", "sizeScatterFloor2x", "sizeHeavyTapSigma",
    "sizeHeavySecondShare", "sizeHeavySecondShareFar2x", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x",
    "sizeScatterScaleGain"],
};

/** What W45's landing let each light document add over its 0.5 twin (its X44 narrowing), and nothing else. */
const W45_LIGHT_ADDED: Readonly<Partial<Record<Slot, readonly string[]>>> = {
  "active.light": ["sizeHeavySecondShareFar2x"],
  "receded.light": ["sizeHeavySecondShare", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x", "sizeHeavySecondShareFar2x"],
};

const sourceKey = (slot: Slot, glass: "0.25" | "0.5"): string => {
  const [pose, scheme] = slot.split(".") as ["active" | "receded", "light" | "dark"];
  return `apple-macos-27.0-1x-${scheme}-standard-glass${glass}${pose === "receded" ? "-receded" : ""}`;
};

const sha256 = (text: string | Buffer): string => createHash("sha256").update(text).digest("hex");
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

function leaves(node: Json, prefix = ""): string[] {
  if (node === null || typeof node !== "object" || Array.isArray(node)) return [prefix];
  return Object.entries(node).flatMap(([k, v]) => leaves(v, prefix ? `${prefix}.${k}` : k)).sort();
}

function setLeaf(patch: Record<string, Json>, path: string, value: Json, slot: Slot): "moved" | "added" {
  if (slot === "active.light" || slot === "receded.light") {
    throw new Error(`${slot}: '${path}': the light material never moves in W46 (X60)`);
  }
  const parts = path.split(".");
  if (parts.length === 1 && patch[path] === undefined && X64[slot].includes(path)) {
    // X64: an inherited leaf this dark document may now name, first at its resolved value.
    if (typeof value !== "number" || !Number.isFinite(value)) throw new Error(`${slot}: '${path}' is not finite`);
    patch[path] = value;
    return "added";
  }
  let node: Record<string, Json> = patch;
  for (const part of parts.slice(0, -1)) {
    const next = node[part];
    if (next === undefined || next === null || typeof next !== "object" || Array.isArray(next)) {
      throw new Error(`${slot}: '${path}' is neither a leaf the 0.5 document names (X44) nor an X64 key`);
    }
    node = next as Record<string, Json>;
  }
  const leaf = parts[parts.length - 1]!;
  const old = node[leaf];
  if (old === undefined) {
    throw new Error(`${slot}: '${path}' is neither a leaf the 0.5 document names (X44) nor an X64 key`);
  }
  const shape = (v: Json): string => (Array.isArray(v) ? `array[${v.length}]` : typeof v);
  if (shape(old) !== shape(value) || (typeof old === "object" && !Array.isArray(old))) {
    throw new Error(`${slot}: '${path}' is ${shape(old)} in the 0.5 document, the spec gives ${shape(value)}`);
  }
  if (Array.isArray(value) && value.some((v) => typeof v !== "number" || !Number.isFinite(v))) {
    throw new Error(`${slot}: '${path}' must be finite numbers`);
  }
  if (typeof value === "number" && !Number.isFinite(value)) throw new Error(`${slot}: '${path}' is not finite`);
  node[leaf] = value;
  return "moved";
}

const specPath = process.argv[2];
if (specPath === undefined) throw new Error("usage: build-candidate.ts <spec.json>");
const specText = readFileSync(resolve(specPath), "utf8");
const spec = JSON.parse(specText) as {
  label: string;
  note?: string;
  overrides?: Partial<Record<Slot, Record<string, Json>>>;
};
if (!new RegExp(LABELS.pattern).test(spec.label)) {
  throw new Error(`label '${spec.label}' does not match labels.json's pattern ${LABELS.pattern}`);
}
const extra = Object.keys(spec.overrides ?? {}).filter((slot) => !SLOTS.includes(slot as Slot));
if (extra.length > 0) throw new Error(`unknown slots ${extra.join(", ")}`);
for (const slot of ["active.light", "receded.light"] as const) {
  if (Object.keys(spec.overrides?.[slot] ?? {}).length > 0) {
    throw new Error(`${slot}: the light material never moves in W46 (X60)`);
  }
}
const out = join(OUT_ROOT, spec.label);
if (existsSync(out)) throw new Error(`${out} exists; a candidate's bytes never move after it is built`);

const sources = Object.fromEntries(SLOTS.map((slot) => {
  const file = join(DOCUMENTS, `${SNAPSHOT[slot].slice(0, 12)}.json`);
  const text = readFileSync(file, "utf8");
  if (sha256(text) !== SNAPSHOT[slot]) {
    throw new Error(`${slot}: the snapshot ${file} does not hash to ${SNAPSHOT[slot].slice(0, 12)} (X62)`);
  }
  const twinKey = sourceKey(slot, "0.5");
  const twinText = readFileSync(join(PROFILES, `${twinKey}.json`), "utf8");
  if (!sha256(twinText).startsWith(TWIN_05[twinKey]!)) {
    throw new Error(`${twinKey}.json is not its X41-frozen ${TWIN_05[twinKey]}`);
  }
  const twin = JSON.parse(twinText) as Record<string, Json>;
  const doc = JSON.parse(text) as Record<string, Json>;
  if (doc["profileKey"] !== sourceKey(slot, "0.25")) throw new Error(`${slot}: the snapshot is ${String(doc["profileKey"])}`);
  // X44 at the base: the 0.25 snapshot names exactly its 0.5 twin's leaves, beside the leaves W45's
  // narrowing let the LIGHT documents add (W45 Decision Log 2 and Decision Log 7 item 6 there), which
  // W45's landed light pair names and which W46 never moves (X60).
  const mine = leaves(doc["patch"] as Json);
  const theirs = leaves(twin["patch"] as Json);
  const extras = mine.filter((k) => !theirs.includes(k));
  if (theirs.some((k) => !mine.includes(k)) || extras.some((k) => !(W45_LIGHT_ADDED[slot] ?? []).includes(k))) {
    throw new Error(`${slot}: the 0.25 snapshot does not name exactly its 0.5 twin's leaves (X44): extra `
      + `${extras.join(", ") || "none"}`);
  }
  return [slot, { file, sha256: SNAPSHOT[slot], doc }];
})) as Record<Slot, { file: string; sha256: string; doc: Record<string, Json> }>;
// Every endpoint is built and checked in memory first; nothing is written unless all four pass.
const texts: Record<string, string> = {};

const mapping = clone(sources["active.light"].doc["cssTierMapping"] as Record<string, Json>);
const endpoints: Record<string, { path: string; sha256: string }> = {};
const activeResolved: Record<string, unknown> = {};
const moved: Record<string, string[]> = {};
const added: Record<string, string[]> = {};
for (const slot of ["active.light", "active.dark", "receded.light", "receded.dark"] as const) {
  const [pose, scheme] = slot.split(".") as ["active" | "receded", "light" | "dark"];
  const source = sources[slot];
  const patch = clone(source.doc["patch"] as Record<string, Json>);
  const overrides = spec.overrides?.[slot] ?? {};
  added[slot] = [];
  for (const [path, value] of Object.entries(overrides)) {
    if (setLeaf(patch, path, value, slot) === "added") added[slot]!.push(path);
  }
  added[slot]!.sort();
  moved[slot] = Object.keys(overrides).sort();
  const base = pose === "active" ? DEFAULT_MATERIAL_PROFILE : activeResolved[scheme];
  if (base === undefined) throw new Error(`${slot}: its scheme's active document was not built first`);
  const resolved = withMaterialOverrides(base as typeof DEFAULT_MATERIAL_PROFILE,
    patch as unknown as MaterialProfilePatch);
  if (pose === "active") activeResolved[scheme] = resolved;
  const key = `apple-macos-27.0-1x-${scheme}-standard-${SCRATCH_GLASS_TOKEN}${pose === "receded" ? "-receded" : ""}`;
  const activeFile = `active.${scheme}.json`;
  const snapshotRel = `packages/calibration/results/2026-10-05-w46-g0-declaration/documents/${source.sha256.slice(0, 12)}.json`;
  const document: Record<string, Json> = {
    "$comment": [
      `SCRATCH CANDIDATE ${spec.label}, W46 candidate (charter clauses 4-5). Not a sealed or`,
      "shipped document; no publication stage names it. Keyed glass0.250 because candidate mode",
      "refuses the shipped 0.25 keys (build-candidate.ts).",
      `Built from the snapshot ${snapshotRel} (X62) with these leaves moved:`,
      moved[slot]!.length > 0 ? moved[slot]!.join(", ") : "(none)",
    ],
    profileKey: key,
    schemaVersion: source.doc["schemaVersion"] ?? 1,
    recordedBy: `W46, scratch candidate ${spec.label}`,
    colorSpace: source.doc["colorSpace"] ?? "srgb",
    ...(pose === "receded"
      ? {
          kind: source.doc["kind"] ?? "receded-endpoint",
          appliesOver: `${activeFile} (this candidate's own active document, beside this file)`,
          resolvedOverActiveDocument: activeFile,
        }
      : { supersedesDefaultsOf: "@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE" }),
    derivedFrom: { path: snapshotRel, sha256: source.sha256, profileKey: sourceKey(slot, "0.25") },
    movedLeaves: moved[slot]!,
    ...(added[slot]!.length > 0 ? { addedLeaves: added[slot]! } : {}),
    resolvedMaterialSha256: resolvedDigest(resolved),
    resolvedMaterialSha256Rule: source.doc["resolvedMaterialSha256Rule"] ?? 2,
    patch,
    ...(pose === "active" && source.doc["cssTierMapping"] !== undefined
      ? { cssTierMapping: scheme === "light" ? mapping : clone(source.doc["cssTierMapping"]) }
      : {}),
  };
  // A slot resolved over an unmoved base with no leaf of its own moved must read its snapshot's
  // digest; a receded slot whose active document moved resolves over the new active and reads its own.
  const baseMoved = pose === "receded" && moved[`active.${scheme}` as Slot]!.length > 0;
  if (moved[slot]!.length === 0 && !baseMoved &&
      document["resolvedMaterialSha256"] !== source.doc["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: no leaf moved and the digest is not the snapshot's`);
  }
  if (scheme === "light" && (JSON.stringify(patch) !== JSON.stringify(source.doc["patch"]) ||
      document["resolvedMaterialSha256"] !== source.doc["resolvedMaterialSha256"])) {
    throw new Error(`${slot}: the light endpoint is not the light snapshot's patch and digest (X60)`);
  }
  const file = `${slot}.json`;
  const text = `${JSON.stringify(document, null, 2)}\n`;
  texts[file] = text;
  endpoints[slot] = { path: file, sha256: sha256(text) };
}
mkdirSync(out, { recursive: true });
for (const [file, text] of Object.entries(texts)) writeFileSync(join(out, file), text);

const declaration = {
  "$comment": `W46 scratch candidate ${spec.label}: ${spec.note ?? ""}`.trim(),
  kind: CANDIDATE_DECLARATION_KIND,
  schemaVersion: 1,
  name: `apple-macos-27.0-glass0.25-w46-${spec.label}`,
  platform: "macOS 27.0",
  glassTintAmount: 0.25,
  endpoints,
  cssTierMappingSha256: cssTierMappingSha256(mapping),
};
writeFileSync(join(out, "candidate.json"), `${JSON.stringify(declaration, null, 2)}\n`);
writeFileSync(join(out, "spec.json"), specText);
const read = readCandidateDocument(join(out, "candidate.json"));
console.log(JSON.stringify({
  label: spec.label,
  candidate: join(out, "candidate.json"),
  declarationSha256: read.declarationSha256,
  digests: Object.fromEntries(Object.entries(read.endpoints).map(([slot, e]) => [slot, e.resolvedMaterialSha256])),
  moved,
  added,
}, null, 2));
