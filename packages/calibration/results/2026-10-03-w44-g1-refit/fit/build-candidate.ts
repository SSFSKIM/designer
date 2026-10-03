/**
 * W44 G1 step 2: build one scratch fit candidate — four endpoint documents and the candidate
 * declaration candidate mode draws. G0's ladder builder
 * (`results/2026-10-03-w44-g0-declaration/ladders/build-candidate.ts`), copied; G0's copy, which
 * part 1 pins, is untouched. Part 2's one amendment pins THIS file, before any fit render.
 *
 *   cd packages/calibration
 *   npx tsx results/2026-10-03-w44-g1-refit/fit/build-candidate.ts <spec.json>
 *
 * The spec names a label and, per endpoint slot, every leaf that moves from the slot's PUBLISHED
 * 0.25 document, c05 (`profiles/apple-macos-27.0-1x-<scheme>-standard-glass0.25[-receded].json`):
 * a fit candidate is always stated whole against c05, so every other byte of its patch is c05's.
 *
 *   { "label": "m1-c-0.5-3", "note": "...",
 *     "overrides": { "active.light": { "sizeScatterFloor2x": 1, "sizeHeavySecondShare": 0.5,
 *                                      "sizeHeavySecondSigma2x": 3 },
 *                    "receded.light": { "sizeHeavySecondShare": 0 } } }
 *
 * The one change from G0's builder, and why (charter Decision Log 7 item 1; X44 narrowed by one
 * difference): G0's ladders showed the receded document inherits the second tap's share and width
 * from its active document and has no leaf to take them off, so a family C landing re-adds the
 * receded mid-pitch structure the floor removed (§5.202 §7). The ruling lets the receded light
 * document name the second tap as a difference over its active document. The guard below admits,
 * in `receded.light` ONLY, exactly the three second-tap keys the active document already names —
 * `sizeHeavySecondShare`, `sizeHeavySecondSigma`, `sizeHeavySecondSigma2x` — as leaves the
 * receded document adds; every other leaf a slot's document does not name is still refused, in
 * every slot (`test_build_candidate.py` holds the red cases). Part 2 searches only the share; the
 * floor, the reach and both widths stay inherited.
 *
 * Unchanged from G0's builder, each a refusal rather than a convention:
 * - **X44 at the base.** Before any override the builder asserts that each 0.25 document names
 *   exactly its 0.5 twin's leaves, so "a leaf the 0.25 document names" and "a leaf the 0.5
 *   document names" are one statement; an override may only name such a leaf, at its shape.
 * - **Patches over the unmoved default.** Each active document is a patch over
 *   `DEFAULT_MATERIAL_PROFILE`, each receded one a difference over its own scheme's NEW active
 *   document, every `resolvedMaterialSha256` computed under the current digest rule.
 * - **The scratch key token `glass0.250`.** Candidate mode refuses a candidate whose endpoint
 *   names a shipped key, so every endpoint is keyed `...-glass0.250[-receded]`: the same (macOS
 *   27.0, glass 0.25) position, not a shipped key. A candidate's identity to c05 is therefore
 *   patch-and-digest (Decision Log 7 item 5); byte identity is the sealed documents'.
 *
 * Output: `fit/candidates/<label>/` (or `$W44_G1_CANDIDATE_ROOT/<label>/`, the red cases' scratch)
 * with the four documents, `candidate.json` and `spec.json`. Then `readCandidateDocument` — the
 * driver's own reader — reads the declaration back. A label that already exists refuses: a
 * candidate's bytes never move after a render names them.
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
const PROFILES = resolve(HERE, "../../../profiles");
const OUT_ROOT = process.env["W44_G1_CANDIDATE_ROOT"] ?? join(HERE, "candidates");
/** The second tap's keys the receded light document may add (Decision Log 7 item 1). */
const RECEDED_SECOND_TAP = ["sizeHeavySecondShare", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x"];
const SCRATCH_GLASS_TOKEN = "glass0.250";

type Slot = "active.light" | "active.dark" | "receded.light" | "receded.dark";
const SLOTS: readonly Slot[] = ["active.light", "active.dark", "receded.light", "receded.dark"];
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

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

function setLeaf(patch: Record<string, Json>, path: string, value: Json, slot: Slot,
  active?: Record<string, Json>): "moved" | "added" {
  const parts = path.split(".");
  if (slot === "receded.light" && parts.length === 1 && patch[path] === undefined &&
      RECEDED_SECOND_TAP.includes(path)) {
    // Decision Log 7 item 1: the receded light document may name the second tap as a difference
    // over its active document; the active document names it, as a number.
    if (active === undefined || typeof active[path] !== "number") {
      throw new Error(`${slot}: '${path}' is not a number the active light document names`);
    }
    if (typeof value !== "number" || !Number.isFinite(value)) throw new Error(`${slot}: '${path}' is not finite`);
    patch[path] = value;
    return "added";
  }
  let node: Record<string, Json> = patch;
  for (const part of parts.slice(0, -1)) {
    const next = node[part];
    if (next === undefined || next === null || typeof next !== "object" || Array.isArray(next)) {
      throw new Error(`${slot}: '${path}' is not a leaf the 0.5 document names (X44)`);
    }
    node = next as Record<string, Json>;
  }
  const leaf = parts[parts.length - 1]!;
  const old = node[leaf];
  if (old === undefined) throw new Error(`${slot}: '${path}' is not a leaf the 0.5 document names (X44)`);
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
if (!/^[a-z0-9][a-z0-9.-]*$/.test(spec.label)) throw new Error(`label '${spec.label}' is not [a-z0-9.-]`);
const extra = Object.keys(spec.overrides ?? {}).filter((slot) => !SLOTS.includes(slot as Slot));
if (extra.length > 0) throw new Error(`unknown slots ${extra.join(", ")}`);
const out = join(OUT_ROOT, spec.label);
if (existsSync(out)) throw new Error(`${out} exists; a candidate's bytes never move after it is built`);

const sources = Object.fromEntries(SLOTS.map((slot) => {
  const file = join(PROFILES, `${sourceKey(slot, "0.25")}.json`);
  const text = readFileSync(file, "utf8");
  const twin = JSON.parse(readFileSync(join(PROFILES, `${sourceKey(slot, "0.5")}.json`), "utf8")) as
    Record<string, Json>;
  const doc = JSON.parse(text) as Record<string, Json>;
  // X44 at the base: the 0.25 document names exactly its 0.5 twin's leaves.
  if (JSON.stringify(leaves(doc["patch"] as Json)) !== JSON.stringify(leaves(twin["patch"] as Json))) {
    throw new Error(`${slot}: the 0.25 document does not name exactly its 0.5 twin's leaves (X44)`);
  }
  return [slot, { file, sha256: sha256(text), doc }];
})) as Record<Slot, { file: string; sha256: string; doc: Record<string, Json> }>;
mkdirSync(out, { recursive: true });

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
    if (setLeaf(patch, path, value, slot, sources["active.light"].doc["patch"] as Record<string, Json>) === "added") {
      added[slot]!.push(path);
    }
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
  const document: Record<string, Json> = {
    "$comment": [
      `SCRATCH CANDIDATE ${spec.label}, W44 G1 fit candidate (charter clause 5). Not a sealed or`,
      "shipped document; no publication stage names it. Keyed glass0.250 because candidate mode",
      "refuses the shipped 0.25 keys (build-candidate.ts).",
      `Built from ${sourceKey(slot, "0.25")}.json (sha256 ${source.sha256.slice(0, 12)}) with these leaves moved:`,
      moved[slot]!.length > 0 ? moved[slot]!.join(", ") : "(none)",
    ],
    profileKey: key,
    schemaVersion: source.doc["schemaVersion"] ?? 1,
    recordedBy: `W44 G1, scratch fit candidate ${spec.label}`,
    colorSpace: source.doc["colorSpace"] ?? "srgb",
    ...(pose === "receded"
      ? {
          kind: source.doc["kind"] ?? "receded-endpoint",
          appliesOver: `${activeFile} (this candidate's own active document, beside this file)`,
          resolvedOverActiveDocument: activeFile,
        }
      : { supersedesDefaultsOf: "@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE" }),
    derivedFrom: { path: `packages/calibration/profiles/${sourceKey(slot, "0.25")}.json`, sha256: source.sha256 },
    movedLeaves: moved[slot]!,
    ...(added[slot]!.length > 0 ? { addedLeaves: added[slot]! } : {}),
    resolvedMaterialSha256: resolvedDigest(resolved),
    resolvedMaterialSha256Rule: source.doc["resolvedMaterialSha256Rule"] ?? 2,
    patch,
    ...(pose === "active" && source.doc["cssTierMapping"] !== undefined
      ? { cssTierMapping: scheme === "light" ? mapping : clone(source.doc["cssTierMapping"]) }
      : {}),
  };
  // A slot resolved over an unmoved base with no leaf of its own moved must read c05's digest; a
  // receded slot whose active document moved resolves over the new active and reads its own.
  const baseMoved = pose === "receded" && moved[`active.${scheme}` as Slot]!.length > 0;
  if (moved[slot]!.length === 0 && !baseMoved &&
      document["resolvedMaterialSha256"] !== source.doc["resolvedMaterialSha256"]) {
    throw new Error(`${slot}: no leaf moved and the digest is not c05's`);
  }
  const file = `${slot}.json`;
  const text = `${JSON.stringify(document, null, 2)}\n`;
  writeFileSync(join(out, file), text);
  endpoints[slot] = { path: file, sha256: sha256(text) };
}

const declaration = {
  "$comment": `W44 G1 scratch fit candidate ${spec.label}: ${spec.note ?? ""}`.trim(),
  kind: CANDIDATE_DECLARATION_KIND,
  schemaVersion: 1,
  name: `apple-macos-27.0-glass0.25-w44-g1-${spec.label}`,
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
