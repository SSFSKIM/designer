/**
 * W43 G3 (i), step 3: build one scratch candidate — four `-glass0.25` endpoint documents and the
 * candidate declaration candidate mode draws (W43 G0 (f)).
 *
 *   cd packages/calibration
 *   npx tsx results/2026-10-02-w43-g3-refit/fit/build-candidate.ts <spec.json>
 *
 * The spec names a label and, per endpoint slot, the leaves that move from the slot's 0.5
 * document (`profiles/apple-macos-27.0-1x-<scheme>-standard-glass0.5[-receded].json`):
 *
 *   { "label": "c01", "note": "...",
 *     "overrides": { "active.light": { "backdropToneResponseThin": [..], "optics.regular.tintAlpha": 0.4 },
 *                    "receded.light": {..}, "active.dark": {..}, "receded.dark": {..} } }
 *
 * What it holds, each a refusal rather than a convention:
 * - **X44, one leaf space.** An override may only name a leaf the slot's 0.5 document already
 *   names, at the same shape (a number for a number, an array of the same length for an array).
 *   So the 0.25 documents name exactly the 0.5 documents' leaves and no operator is added.
 * - **Patches over the unmoved default** (Decision Log 6): each active document is a patch over
 *   `DEFAULT_MATERIAL_PROFILE`, each receded one a difference over its own scheme's NEW active
 *   document (Decision Log 7 item 8), and every `resolvedMaterialSha256` is computed here under
 *   the current digest rule (rule 2) by the same functions `scripts/candidate-document.ts` checks
 *   it with. The CSS mapping is the 0.5 light document's, unchanged unless the spec moves it.
 * - **The 0.25 keys.** Every `profileKey` carries the `-glass0.25` token and the declaration
 *   `glassTintAmount: 0.25`; the name is a scratch name, never a shipped document's.
 *
 * Output: `results/2026-10-02-w43-g3-refit/fit/candidates/<label>/` with the four documents,
 * `candidate.json`, and `spec.json` (the spec as given). Then `readCandidateDocument` — the
 * driver's own reader — reads the declaration back, so a candidate that would refuse at the
 * driver refuses here first. A label that already exists refuses: a candidate's bytes never move
 * after a render names them.
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
const OUT_ROOT = join(HERE, "candidates");

type Slot = "active.light" | "active.dark" | "receded.light" | "receded.dark";
const SLOTS: readonly Slot[] = ["active.light", "active.dark", "receded.light", "receded.dark"];
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

const sourceKey = (slot: Slot): string => {
  const [pose, scheme] = slot.split(".") as ["active" | "receded", "light" | "dark"];
  return `apple-macos-27.0-1x-${scheme}-standard-glass0.5${pose === "receded" ? "-receded" : ""}`;
};

const sha256 = (text: string | Buffer): string => createHash("sha256").update(text).digest("hex");
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

function setLeaf(patch: Record<string, Json>, path: string, value: Json, slot: Slot): void {
  const parts = path.split(".");
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
}

const specPath = process.argv[2];
if (specPath === undefined) throw new Error("usage: build-candidate.ts <spec.json>");
const specText = readFileSync(resolve(specPath), "utf8");
const spec = JSON.parse(specText) as {
  label: string;
  note?: string;
  overrides?: Partial<Record<Slot, Record<string, Json>>>;
  cssTierMapping?: Record<string, Json>;
};
if (!/^[a-z0-9][a-z0-9-]*$/.test(spec.label)) throw new Error(`label '${spec.label}' is not [a-z0-9-]`);
const extra = Object.keys(spec.overrides ?? {}).filter((slot) => !SLOTS.includes(slot as Slot));
if (extra.length > 0) throw new Error(`unknown slots ${extra.join(", ")}`);
const out = join(OUT_ROOT, spec.label);
if (existsSync(out)) throw new Error(`${out} exists; a candidate's bytes never move after it is built`);
mkdirSync(out, { recursive: true });

const sources = Object.fromEntries(SLOTS.map((slot) => {
  const file = join(PROFILES, `${sourceKey(slot)}.json`);
  const text = readFileSync(file, "utf8");
  return [slot, { file, sha256: sha256(text), doc: JSON.parse(text) as Record<string, Json> }];
})) as Record<Slot, { file: string; sha256: string; doc: Record<string, Json> }>;

const lightMapping = clone(sources["active.light"].doc["cssTierMapping"] as Record<string, Json>);
const mapping = spec.cssTierMapping === undefined ? lightMapping : { ...lightMapping, ...spec.cssTierMapping };
for (const key of Object.keys(spec.cssTierMapping ?? {})) {
  if (!(key in lightMapping)) throw new Error(`cssTierMapping.${key} is not a key the 0.5 mapping names (X44)`);
}

const endpoints: Record<string, { path: string; sha256: string }> = {};
const activeResolved: Record<string, unknown> = {};
const moved: Record<string, string[]> = {};
for (const slot of ["active.light", "active.dark", "receded.light", "receded.dark"] as const) {
  const [pose, scheme] = slot.split(".") as ["active" | "receded", "light" | "dark"];
  const source = sources[slot];
  const patch = clone(source.doc["patch"] as Record<string, Json>);
  const overrides = spec.overrides?.[slot] ?? {};
  for (const [path, value] of Object.entries(overrides)) setLeaf(patch, path, value, slot);
  moved[slot] = Object.keys(overrides).sort();
  const base = pose === "active" ? DEFAULT_MATERIAL_PROFILE : activeResolved[scheme];
  if (base === undefined) throw new Error(`${slot}: its scheme's active document was not built first`);
  const resolved = withMaterialOverrides(base as typeof DEFAULT_MATERIAL_PROFILE,
    patch as unknown as MaterialProfilePatch);
  if (pose === "active") activeResolved[scheme] = resolved;
  const key = `apple-macos-27.0-1x-${scheme}-standard-glass0.25${pose === "receded" ? "-receded" : ""}`;
  const activeFile = `apple-macos-27.0-1x-${scheme}-standard-glass0.25.json`;
  const document: Record<string, Json> = {
    "$comment": [
      `SCRATCH CANDIDATE ${spec.label}, W43 G3 (i) refit (charter clause 10, Decision Log 7 as RULED`,
      "2026-10-02). Not a sealed or shipped document; no publication stage names it.",
      `Built from ${sourceKey(slot)}.json (sha256 ${source.sha256.slice(0, 12)}) with these leaves moved:`,
      moved[slot]!.length > 0 ? moved[slot]!.join(", ") : "(none)",
    ],
    profileKey: key,
    schemaVersion: source.doc["schemaVersion"] ?? 1,
    recordedAt: new Date().toISOString(),
    recordedBy: `W43 G3 (i), scratch candidate ${spec.label}`,
    colorSpace: source.doc["colorSpace"] ?? "srgb",
    ...(pose === "receded"
      ? {
          kind: source.doc["kind"] ?? "receded-endpoint",
          appliesOver: `${activeFile} (this candidate's own active document, beside this file)`,
          resolvedOverActiveDocument: activeFile,
        }
      : { supersedesDefaultsOf: "@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE" }),
    derivedFrom: { path: `packages/calibration/profiles/${sourceKey(slot)}.json`, sha256: source.sha256 },
    movedLeaves: moved[slot]!,
    resolvedMaterialSha256: resolvedDigest(resolved),
    resolvedMaterialSha256Rule: source.doc["resolvedMaterialSha256Rule"] ?? 2,
    patch,
    // The dark document states only the keys its 0.5 twin states, each at the light value:
    // one material has one crossing, which is what the driver's reader refuses otherwise.
    ...(pose === "active" ? { cssTierMapping: scheme === "light" ? mapping : Object.fromEntries(
      Object.keys((source.doc["cssTierMapping"] as Record<string, Json> | undefined) ?? {})
        .map((key) => [key, clone(mapping[key]!)])) } : {}),
  };
  if (pose === "active" && scheme === "dark" && source.doc["cssTierMapping"] === undefined) {
    delete document["cssTierMapping"];
  }
  const file = `${slot}.json`;
  const text = `${JSON.stringify(document, null, 2)}\n`;
  writeFileSync(join(out, file), text);
  endpoints[slot] = { path: file, sha256: sha256(text) };
}

const declaration = {
  "$comment": `W43 G3 (i) scratch candidate ${spec.label}: ${spec.note ?? ""}`.trim(),
  kind: CANDIDATE_DECLARATION_KIND,
  schemaVersion: 1,
  name: `apple-macos-27.0-glass0.25-w43-g3-${spec.label}`,
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
}, null, 2));
