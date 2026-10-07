/**
 * W49a G0: build one scratch candidate — W48's builder
 * (`results/2026-10-06-w48-g0-declaration/fit/build-candidate.ts`) COPIED and re-bound to W49a (charter
 * `2026-10-07-w49-authorised-list-repair.md`, Decision Logs 1 and 3). W48's committed copy is untouched.
 * The probes P1 and P2 of part 1 and the seal's candidate all build through THIS file.
 *
 *   cd packages/calibration
 *   W49A_CANDIDATE_ROOT=<dir> pnpm exec tsx results/2026-10-07-w49a-g0-declaration/fit/build-candidate.ts <spec.json>
 *
 * The spec names a label, a base and, per DARK slot, every leaf that moves from the base's snapshot:
 *
 *   { "label": "p2-far0.09", "base": "b2d074", "note": "...",
 *     "overrides": { "receded.dark": { "tintAlphaFar1x": 0.09, "tintAlphaFar2x": 0.09 } } }
 *
 * **What W49a changes from W48's builder, and why:**
 * - **Two bases, each a pair of snapshots (X62 at this charter).** `b2d074` (the default) starts the dark
 *   slots from the shipped 0.28.0 pair `b2d074d2df24` / `29da6a888a23`, the start of family R; `d0219`
 *   starts them from the superseded `d0219cd684bf` / `f0b36a71772a`, which only probe P1 reads. The light
 *   slots start from `ebc3d9105a4a` / `12712d534b78` under both and never move (X60).
 * - **Only W49a's members move, inside their declared domains** (`MEMBERS`; Decision Logs 1 and 3). On
 *   `b2d074` exactly the receded dark `tintAlphaFar1x` / `tintAlphaFar2x`, each in the SIGNED domain
 *   [-0.3, 0.2] (W47's X68 said [0, 0.6]; neither tier validates the sign: the shader and both tiers'
 *   `spanGradedTintAlpha` clamp `alphaBase` into [0, 1] and nothing else reads the leaf); the active dark
 *   document does not move (DL1: the existing receded leaf alone). On `d0219` exactly the active dark span
 *   tops `sizeScatterSpanMax` / `…2x`, at the value {160} (probe P1). Every other override refuses: W48's
 *   rule that a leaf with no declared domain keeps W46's admission is gone, because W49a declares a family
 *   of one leaf pair and nothing else.
 * - **X75: no candidate that draws opaque glass is built.** Every endpoint, posed as the root poses it
 *   (a receded patch merged over its own active), must keep `alphaBase` at or under 0.95 at every span
 *   0..1024 CSS px, dpr 1 and 2, both variants, both tiers (`scripts/no-opaque-glass.ts`, the runtime
 *   test's own arithmetic). A violation refuses before anything is written.
 * - **X44 at the base admits the dark leaves W46-W48 added.** The `b2d074` dark pair names X64's and X67's
 *   keys beside its 0.5 twin's leaves (W48 materialised them), so the base check admits those keys as
 *   well as W45's light ones.
 * - **W49a's root, never W44's-W48's** (`W49A_CANDIDATE_ROOT`); the label grammar is W49a's
 *   (`fit/labels.json` beside this file).
 *
 * Unchanged from W48's builder, each a refusal rather than a convention: an existing leaf moves only at its
 * own shape and as finite numbers; an added leaf must be one the runtime knows and every override must read
 * back from the resolved material; patches over the unmoved default, each receded endpoint a difference over
 * its scheme's NEW active document; the scratch key token `glass0.250` (candidate mode refuses a shipped
 * key); a slot with no leaf of its own moved over an unmoved base must read its snapshot's digest; a label
 * that exists refuses; `readCandidateDocument` reads the declaration back.
 *
 * Output: `<W49A_CANDIDATE_ROOT>/<label>/` with the four documents, `candidate.json` and `spec.json`.
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
import { mergeMaterialProfiles } from "@vitreajs/vitrea-web";

import {
  CANDIDATE_DECLARATION_KIND,
  cssTierMappingSha256,
  readCandidateDocument,
  resolvedDigest,
} from "../../../scripts/candidate-document";
import { opaqueGlassViolations, summariseOpaqueGlass } from "../../../scripts/no-opaque-glass";

const HERE = resolve(fileURLToPath(new URL(".", import.meta.url)));
const EVIDENCE = resolve(HERE, "..");
const PROFILES = resolve(HERE, "../../../profiles");
const DOCUMENTS = join(EVIDENCE, "documents");
const LABELS = JSON.parse(readFileSync(join(HERE, "labels.json"), "utf8")) as { pattern: string };
const ROOT_ENV = process.env["W49A_CANDIDATE_ROOT"];
if (ROOT_ENV === undefined || ROOT_ENV === "") {
  throw new Error("W49A_CANDIDATE_ROOT names where the candidate is written; there is no default");
}
const OUT_ROOT = resolve(ROOT_ENV);
if (/(^|\/)2026-10-0[3567]-w4[45678]-[^/]*(\/|$)/.test(OUT_ROOT) || /(^|\/)vitrea-w4[45678](\/|$)/.test(OUT_ROOT)) {
  throw new Error(`${OUT_ROOT} is W44's-W48's evidence or scratch; W49a builds into its own`);
}
if (OUT_ROOT === PROFILES || OUT_ROOT.startsWith(`${PROFILES}/`)) {
  throw new Error(`${OUT_ROOT} is the profiles directory; a candidate is never written there (X62)`);
}
const SCRATCH_GLASS_TOKEN = "glass0.250";

type Slot = "active.light" | "active.dark" | "receded.light" | "receded.dark";
type DarkSlot = "active.dark" | "receded.dark";
type Base = "b2d074" | "d0219";
const SLOTS: readonly Slot[] = ["active.light", "active.dark", "receded.light", "receded.dark"];
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

const LIGHT = {
  "active.light": "ebc3d9105a4a40565278845071113c6a5368b304910362786b8cbfb4cc66bb44",
  "receded.light": "12712d534b78017f68fee440cb9d9d451178aae1b80db36c0043fdfb1b591203",
} as const;
/** The snapshots (X62 at this charter): base -> slot -> full SHA-256 of `documents/<sha12>.json`. */
const SNAPSHOTS: Readonly<Record<Base, Readonly<Record<Slot, string>>>> = {
  b2d074: {
    "active.dark": "b2d074d2df2444a614304d11e906b5f91d8968bce161efbd8f34fc8da5be9186",
    "receded.dark": "29da6a888a23a9a1b5fa3dba6128ed1eedf160030e3dd4fd2e2fc7cb6a6c2389",
    ...LIGHT,
  },
  d0219: {
    "active.dark": "d0219cd684bff75b2ba5c34d4f6cb2f6d49e32aab7cc27464220a05910f2638f",
    "receded.dark": "f0b36a71772a00a647c10a280ae73b92d21be1f0c65599334c4e3cdf36cb7f86",
    ...LIGHT,
  },
};
/** X41's frozen 0.5 twins: key -> twelve-hex file hash. */
const TWIN_05: Readonly<Record<string, string>> = {
  "apple-macos-27.0-1x-dark-standard-glass0.5": "0eac5b294cc2",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded": "5cec8c961201",
  "apple-macos-27.0-1x-light-standard-glass0.5": "85ad7f7e3e0d",
  "apple-macos-27.0-1x-light-standard-glass0.5-receded": "30fbe05986ae",
};
/** X64 and X67 (W48's `bindings.ADMITTED`): the keys a dark 0.25 document may name beside its twin's. */
const ADMITTED: Readonly<Record<DarkSlot, readonly string[]>> = {
  "active.dark": ["sizeScatterFloor2x", "sizeScatterRampStartThin1x", "sizeScatterRampStartThick1x",
    "sizeScatterRampStartFar1x", "sizeScatterRampStartThin2x", "sizeScatterRampStartThick2x",
    "sizeScatterRampStartFar2x", "sizeHeavySecondShareFar2x", "sizeOcclusionGain", "sizeScatterSpanMax",
    "sizeScatterSpanMax2x", "tintAlphaFar1x", "tintAlphaFar2x"],
  "receded.dark": ["sizeScatterRampStartFar1x", "sizeScatterFloor", "sizeScatterFloor2x", "sizeHeavyTapSigma",
    "sizeHeavySecondShare", "sizeHeavySecondShareFar2x", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x",
    "sizeScatterScaleGain", "optics.regular.blurSigma", "sizeScatterSpanMax", "sizeScatterSpanMax2x",
    "sizeOcclusionGain", "tintAlphaFar1x", "tintAlphaFar2x", "sizeFineTapShare", "sizeFineTapSigma",
    "sizeFineTapSigma2x"],
};
type DomainPart = readonly ["set", readonly number[]] | readonly ["interval", number, number];
/** Family R's signed domain (Decision Log 1). */
const R_DOMAIN: readonly DomainPart[] = [["interval", -0.3, 0.2]];
/**
 * W49a's members per base: the only leaves a spec may move, each with its declared domain (a value is
 * inside when some part holds it, closed intervals). `test_build_candidate.py` holds this table to the
 * declaration's part 1.
 */
const MEMBERS: Readonly<Record<Base, Partial<Record<DarkSlot, Readonly<Record<string, readonly DomainPart[]>>>>>> = {
  b2d074: { "receded.dark": { tintAlphaFar1x: R_DOMAIN, tintAlphaFar2x: R_DOMAIN } },
  d0219: { "active.dark": { sizeScatterSpanMax: [["set", [160]]], sizeScatterSpanMax2x: [["set", [160]]] } },
};
const inDomain = (parts: readonly DomainPart[], value: number): boolean => parts.some((part) =>
  part[0] === "set" ? part[1].some((v) => v === value) : part[1] <= value && value <= part[2]);
/** The value a dotted path names in a nested object, or undefined. */
const pathValue = (node: unknown, path: string): unknown => path.split(".").reduce<unknown>(
  (at, part) => (at !== null && typeof at === "object" && !Array.isArray(at) ? (at as Record<string, unknown>)[part]
    : undefined), node);

/** What W45's landing let each light document add over its 0.5 twin (its X44 narrowing), and nothing else. */
const W45_LIGHT_ADDED: Readonly<Partial<Record<Slot, readonly string[]>>> = {
  "active.light": ["sizeHeavySecondShareFar2x"],
  "receded.light": ["sizeHeavySecondShare", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x", "sizeHeavySecondShareFar2x"],
};
const mayExtend = (slot: Slot): readonly string[] =>
  slot === "active.dark" || slot === "receded.dark" ? ADMITTED[slot] : W45_LIGHT_ADDED[slot] ?? [];

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
  const parts = path.split(".");
  if (pathValue(patch, path) === undefined && (slot === "active.dark" || slot === "receded.dark")
      && ADMITTED[slot].includes(path)) {
    // X64, X67: an inherited leaf this dark document may name. Only a leaf the runtime knows: an unknown
    // key would be dropped from the resolved material silently.
    if (typeof value !== "number" || !Number.isFinite(value)) throw new Error(`${slot}: '${path}' is not finite`);
    if (typeof pathValue(DEFAULT_MATERIAL_PROFILE, path) !== "number") {
      throw new Error(`${slot}: '${path}' is an admitted key the runtime does not know`);
    }
    let node: Record<string, Json> = patch;
    for (const part of parts.slice(0, -1)) {
      const next = node[part];
      if (next === undefined) node[part] = {};
      else if (next === null || typeof next !== "object" || Array.isArray(next)) {
        throw new Error(`${slot}: '${path}' crosses a leaf`);
      }
      node = node[part] as Record<string, Json>;
    }
    node[parts[parts.length - 1]!] = value;
    return "added";
  }
  let node: Record<string, Json> = patch;
  for (const part of parts.slice(0, -1)) {
    const next = node[part];
    if (next === undefined || next === null || typeof next !== "object" || Array.isArray(next)) {
      throw new Error(`${slot}: '${path}' is neither a leaf the snapshot names nor an admitted key (X64, X67)`);
    }
    node = next as Record<string, Json>;
  }
  const leaf = parts[parts.length - 1]!;
  const old = node[leaf];
  if (old === undefined) {
    throw new Error(`${slot}: '${path}' is neither a leaf the snapshot names nor an admitted key (X64, X67)`);
  }
  const shape = (v: Json): string => (Array.isArray(v) ? `array[${v.length}]` : typeof v);
  if (shape(old) !== shape(value) || (typeof old === "object" && !Array.isArray(old))) {
    throw new Error(`${slot}: '${path}' is ${shape(old)} in the snapshot, the spec gives ${shape(value)}`);
  }
  if (typeof value === "number" && !Number.isFinite(value)) throw new Error(`${slot}: '${path}' is not finite`);
  node[leaf] = value;
  return "moved";
}

if (process.argv[2] === "--tables") {
  console.log(JSON.stringify({ MEMBERS, SNAPSHOTS }));
  process.exit(0);
}
const specPath = process.argv[2];
if (specPath === undefined) throw new Error("usage: build-candidate.ts <spec.json>");
const specText = readFileSync(resolve(specPath), "utf8");
const spec = JSON.parse(specText) as {
  label: string;
  base?: Base;
  note?: string;
  overrides?: Partial<Record<Slot, Record<string, Json>>>;
};
if (!new RegExp(LABELS.pattern).test(spec.label)) {
  throw new Error(`label '${spec.label}' does not match labels.json's pattern ${LABELS.pattern}`);
}
const base: Base = spec.base ?? "b2d074";
if (!(base in SNAPSHOTS)) throw new Error(`base '${String(base)}' is not one of ${Object.keys(SNAPSHOTS).join(", ")}`);
const SNAPSHOT = SNAPSHOTS[base];
const extra = Object.keys(spec.overrides ?? {}).filter((slot) => !SLOTS.includes(slot as Slot));
if (extra.length > 0) throw new Error(`unknown slots ${extra.join(", ")}`);
// W49a's members, inside their domains, checked before anything is read (Decision Logs 1 and 3).
for (const slot of SLOTS) {
  for (const [path, value] of Object.entries(spec.overrides?.[slot] ?? {})) {
    const parts = MEMBERS[base][slot as DarkSlot]?.[path];
    if (parts === undefined) {
      throw new Error(`${slot}: '${path}' is not a W49a member on base ${base} (members: `
        + `${JSON.stringify(MEMBERS[base])}; the light material never moves, X60)`);
    }
    if (typeof value !== "number" || !inDomain(parts, value)) {
      throw new Error(`${slot}: '${path}' ${JSON.stringify(value)} is outside its declared domain `
        + `${JSON.stringify(parts)} (Decision Log 1)`);
    }
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
  // X44 at the base, as narrowed: the 0.5 twin's leaves, beside the keys W45 (light) and X64 / X67 (dark)
  // let the 0.25 documents add.
  const mine = leaves(doc["patch"] as Json);
  const theirs = leaves(twin["patch"] as Json);
  const extras = mine.filter((k) => !theirs.includes(k));
  if (theirs.some((k) => !mine.includes(k)) || extras.some((k) => !mayExtend(slot).includes(k))) {
    throw new Error(`${slot}: the 0.25 snapshot does not name its 0.5 twin's leaves as narrowed (X44): extra `
      + `${extras.join(", ") || "none"}`);
  }
  return [slot, { file, sha256: SNAPSHOT[slot], doc }];
})) as Record<Slot, { file: string; sha256: string; doc: Record<string, Json> }>;
const texts: Record<string, string> = {};

const mapping = clone(sources["active.light"].doc["cssTierMapping"] as Record<string, Json>);
const endpoints: Record<string, { path: string; sha256: string }> = {};
const activeResolved: Record<string, unknown> = {};
const activePatch: Record<string, Record<string, Json>> = {};
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

  const resolvedBase = pose === "active" ? DEFAULT_MATERIAL_PROFILE : activeResolved[scheme];
  if (resolvedBase === undefined) throw new Error(`${slot}: its scheme's active document was not built first`);
  const resolved = withMaterialOverrides(resolvedBase as typeof DEFAULT_MATERIAL_PROFILE,
    patch as unknown as MaterialProfilePatch);
  if (pose === "active") {
    activeResolved[scheme] = resolved;
    activePatch[scheme] = patch;
  }
  for (const [path, value] of Object.entries(overrides)) {
    if (JSON.stringify(pathValue(resolved, path)) !== JSON.stringify(value)) {
      throw new Error(`${slot}: '${path}' does not read back from the resolved material `
        + `(${JSON.stringify(pathValue(resolved, path))} where the spec gives ${JSON.stringify(value)})`);
    }
  }
  // X75 (Decision Log 3): the endpoint as the root poses it draws no opaque glass, on either tier.
  const posed = pose === "active" ? patch
    : mergeMaterialProfiles(activePatch[scheme] as never, patch as never);
  const opaque = summariseOpaqueGlass(opaqueGlassViolations(posed as unknown as MaterialProfilePatch));
  if (opaque.length > 0) {
    throw new Error(`${slot}: draws opaque glass, alphaBase above 0.95 (X75): ${opaque.join("; ")}`);
  }
  const key = `apple-macos-27.0-1x-${scheme}-standard-${SCRATCH_GLASS_TOKEN}${pose === "receded" ? "-receded" : ""}`;
  const activeFile = `active.${scheme}.json`;
  const snapshotRel = `packages/calibration/results/2026-10-07-w49a-g0-declaration/documents/${source.sha256.slice(0, 12)}.json`;
  const document: Record<string, Json> = {
    "$comment": [
      `SCRATCH CANDIDATE ${spec.label}, W49a candidate on base ${base}. Not a sealed or`,
      "shipped document; no publication stage names it. Keyed glass0.250 because candidate mode",
      "refuses the shipped 0.25 keys (build-candidate.ts).",
      `Built from the snapshot ${snapshotRel} (X62) with these leaves moved:`,
      moved[slot]!.length > 0 ? moved[slot]!.join(", ") : "(none)",
    ],
    profileKey: key,
    schemaVersion: source.doc["schemaVersion"] ?? 1,
    recordedBy: `W49a, scratch candidate ${spec.label}`,
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
  "$comment": `W49a scratch candidate ${spec.label} (base ${base}): ${spec.note ?? ""}`.trim(),
  kind: CANDIDATE_DECLARATION_KIND,
  schemaVersion: 1,
  name: `apple-macos-27.0-glass0.25-w49a-${spec.label}`,
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
  base,
  candidate: join(out, "candidate.json"),
  declarationSha256: read.declarationSha256,
  digests: Object.fromEntries(Object.entries(read.endpoints).map(([slot, e]) => [slot, e.resolvedMaterialSha256])),
  moved,
  added,
}, null, 2));
