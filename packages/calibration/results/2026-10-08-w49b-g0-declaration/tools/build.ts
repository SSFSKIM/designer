/** W49b scratch builder. The supplied batch enumerates a finite domain; no default batch exists.
 *
 *   pnpm exec tsx results/2026-10-08-w49b-g0-declaration/tools/build.ts batch.json /scratch/new-batch
 *
 * All points resolve and pass X75 BEFORE any file is written. Every endpoint starts at a
 * byte-pinned grounding snapshot. No sealed document, generation or runtime source is written.
 * Active/receded difference composition and candidate validation are the driver's real readers.
 */
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { dirname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import {
  DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
import { mergeMaterialProfiles } from "@vitreajs/vitrea-web";
import {
  CANDIDATE_DECLARATION_KIND, cssTierMappingSha256, readCandidateDocument, resolvedDigest,
} from "../../../scripts/candidate-document";
import { opaqueGlassViolations, summariseOpaqueGlass } from "../../../scripts/no-opaque-glass";

const HERE = dirname(fileURLToPath(import.meta.url));
const CAL = resolve(HERE, "../../..");
const ROOT = resolve(CAL, "../..");
const slots = ["active.light", "active.dark", "receded.light", "receded.dark"] as const;
type Slot = typeof slots[number];
type Patch = Record<string, number | unknown>;
type Point = { label: string; scales: number[]; pose: string; overrides: Partial<Record<Slot, Patch>> };
type Pin = { path: string; sha256: string; source?: string };
type ProfileDocument = Record<string, unknown> & {
  profileKey: string; patch: Patch; cssTierMapping?: Record<string, unknown>;
  resolvedMaterialSha256: string;
};
const sha = (text: string | Buffer): string => createHash("sha256").update(text).digest("hex");
const encode = (value: unknown): string => JSON.stringify(value, null, 2) + "\n";
const [batchArg, outArg] = process.argv.slice(2);
if (!batchArg || !outArg || process.argv.length !== 4) {
  throw new Error("Usage: build.ts <supplied-batch.json> <new-scratch-batch-directory>");
}
const batchPath = resolve(batchArg);
const batch = JSON.parse(execFileSync("python3", ["-I", join(HERE, "common.py"),
  "validate-batch", batchPath], { encoding: "utf8" })) as { id: string; points: Point[] };
const out = resolve(outArg);
// Resolve existing ancestors, so a symlink cannot disguise a canonical destination.
function realDestination(path: string): string {
  if (existsSync(path)) return realpathSync(path);
  return join(realDestination(dirname(path)), path.slice(dirname(path).length + 1));
}
const destination = realDestination(out);
const commonGit = execFileSync("git", ["rev-parse", "--path-format=absolute", "--git-common-dir"],
  { cwd: CAL, encoding: "utf8" }).trim();
for (const forbidden of [ROOT, dirname(commonGit)]) {
  if (destination === forbidden || destination.startsWith(forbidden + sep)) {
    throw new Error("Candidates must be outside every authoritative checkout");
  }
}
if (/(^|\/)(profiles|generations|web-captures|web-captures-superseded)(\/|$)/.test(destination)) {
  throw new Error("Candidate destination names sealed documents or capture evidence");
}
if (existsSync(out)) throw new Error(`Refuse existing output ${out}`);
const registryPath = resolve(HERE, "../references.json");
const registry = JSON.parse(readFileSync(registryPath, "utf8")) as {
  inputs: Record<string, Pin>; endpoints: Record<Slot, Pin>;
};
const readPin = (pin: Pin): string => {
  const path = resolve(CAL, pin.path);
  const text = readFileSync(path, "utf8");
  if (sha(text) !== pin.sha256) throw new Error(`Changed byte snapshot ${path}`);
  return text;
};
for (const pin of Object.values(registry.inputs)) readPin(pin);
const sources = Object.fromEntries(slots.map(slot => [slot, {
  pin: registry.endpoints[slot], doc: JSON.parse(readPin(registry.endpoints[slot])),
}])) as Record<Slot, { pin: Pin; doc: ProfileDocument }>;
const prepared: { point: Point; files: Record<string, string>; digests: Record<Slot, string> }[] = [];
for (const point of batch.points) {
  const patches = {} as Record<Slot, Patch>;
  const materials = {} as Record<Slot, typeof DEFAULT_MATERIAL_PROFILE>;
  const files: Record<string, string> = {};
  const endpoints = {} as Record<Slot, { path: string; sha256: string }>;
  for (const slot of slots) {
    const [pose, scheme] = slot.split(".");
    const source = sources[slot];
    const overrides = point.overrides[slot] ?? {};
    for (const [leaf, value] of Object.entries(overrides)) {
      if (!(leaf in DEFAULT_MATERIAL_PROFILE)) {
        throw new Error(`Runtime build lacks ${leaf}; build the operator before this batch`);
      }
      if (typeof value !== "number" || !Number.isFinite(value)) throw new Error(`Invalid ${leaf}`);
    }
    const patch = { ...source.doc.patch, ...overrides };
    patches[slot] = patch;
    const material = withMaterialOverrides(pose === "active" ? DEFAULT_MATERIAL_PROFILE
      : materials[`active.${scheme}` as Slot], patch as MaterialProfilePatch);
    for (const [leaf, value] of Object.entries(overrides)) {
      if ((material as unknown as Record<string, unknown>)[leaf] !== value) {
        throw new Error(`Runtime did not resolve ${slot}.${leaf}=${value}`);
      }
    }
    materials[slot] = material;
    const posed = pose === "active" ? patch : mergeMaterialProfiles(
      patches[`active.${scheme}` as Slot], patch);
    const violations = opaqueGlassViolations(posed as MaterialProfilePatch);
    if (violations.length) throw new Error(`${point.label} ${slot} violates X75: ` +
      summariseOpaqueGlass(violations).join("; "));
    if (Object.keys(overrides).length === 0 && (pose === "active" ||
        Object.keys(point.overrides[`active.${scheme}` as Slot] ?? {}).length === 0) &&
        resolvedDigest(material) !== source.doc.resolvedMaterialSha256) {
      throw new Error(`Unmoved ${slot} no longer resolves to its snapshot`);
    }
    const doc = { ...source.doc,
      profileKey: source.doc.profileKey.replace("glass0.25", "glass0.250"),
      recordedBy: `W49b G0 scratch ${batch.id}/${point.label}; not a sealed document`,
      ...(pose === "receded" ? { resolvedOverActiveDocument: `active.${scheme}.json` } : {}),
      derivedFrom: { path: source.pin.source, sha256: source.pin.sha256 },
      patch, resolvedMaterialSha256: resolvedDigest(material),
    };
    const bytes = encode(doc);
    files[`${slot}.json`] = bytes;
    endpoints[slot] = { path: `${slot}.json`, sha256: sha(bytes) };
  }
  const unrequested = point.pose === "rest" ? "receded.dark"
    : point.pose === "inactive" ? "active.dark" : undefined;
  if (unrequested && resolvedDigest(materials[unrequested]) !== sources[unrequested].doc.resolvedMaterialSha256) {
    throw new Error(`${point.label} changes unrequested ${unrequested}; request both poses or explicitly hold it`);
  }
  files["candidate.json"] = encode({ kind: CANDIDATE_DECLARATION_KIND, schemaVersion: 1,
    name: `apple-macos-27.0-glass0.25-w49b-${batch.id}-${point.label}`,
    platform: "macOS 27.0", glassTintAmount: 0.25, endpoints,
    cssTierMappingSha256: cssTierMappingSha256(sources["active.light"].doc.cssTierMapping),
  });
  files["point.json"] = encode(point);
  prepared.push({ point, files, digests: Object.fromEntries(slots.map(s =>
    [s, resolvedDigest(materials[s])])) as Record<Slot, string> });
}
mkdirSync(out, { recursive: false });
writeFileSync(join(out, "batch.json"), readFileSync(batchPath), { flag: "wx" });
writeFileSync(join(out, "build.json"), encode({ schemaVersion: 1, batchSha256: sha(readFileSync(batchPath)),
  referencesSha256: sha(readFileSync(registryPath)), builderSha256: sha(readFileSync(fileURLToPath(import.meta.url))),
  points: prepared.map(p => ({ label: p.point.label, digests: p.digests,
    candidateSha256: sha(p.files["candidate.json"]!), pointSha256: sha(p.files["point.json"]!) })) }), { flag: "wx" });
for (const { point, files } of prepared) {
  const folder = join(out, point.label);
  mkdirSync(folder);
  for (const [name, bytes] of Object.entries(files)) writeFileSync(join(folder, name), bytes, { flag: "wx" });
  readCandidateDocument(join(folder, "candidate.json"));
}
process.stdout.write(JSON.stringify({ built: prepared.length, root: out,
  candidates: prepared.map(p => ({ label: p.point.label, digests: p.digests })) }, null, 2) + "\n");
