/** Scratch-only W49b grounding on the current four endpoints; probes.json is the finite domain.
 * No profile, runtime source or generation is changed. Candidate mode verifies all four digests.
 */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch } from "@vitrea/renderer-webgpu";
import { mergeMaterialProfiles } from "@vitreajs/vitrea-web";
import { CANDIDATE_DECLARATION_KIND, cssTierMappingSha256, readCandidateDocument, resolvedDigest } from "../../scripts/candidate-document";
import { opaqueGlassViolations } from "../../scripts/no-opaque-glass";

const here = dirname(fileURLToPath(import.meta.url));
const cal = resolve(here, "../..");
const outRoot = process.argv[2];
if (!outRoot || !resolve(outRoot).startsWith("/Users/new/vitrea-w49/b-grounding-scratch/")) {
  throw new Error("Output must be in the dedicated W49b scratch directory");
}
const sha = (s: string) => createHash("sha256").update(s).digest("hex");
const slots = ["active.light", "active.dark", "receded.light", "receded.dark"] as const;
type Slot = typeof slots[number];
type Patch = Record<string, unknown>;
const snapshots = JSON.parse(readFileSync(join(here, "documents/index.json"), "utf8"));
const sources = Object.fromEntries(slots.map(slot => {
  const snapshot = snapshots[slot];
  const file = join(here, `documents/${snapshot.sha256.slice(0, 12)}.json`);
  const bytes = readFileSync(file, "utf8");
  if (sha(bytes) !== snapshot.sha256) throw new Error(`Changed snapshot ${slot}`);
  // Retain the original source pathname recorded by the exploratory builder. The bytes now
  // come from a pinned snapshot so a later seal cannot change a replay's starting material.
  return [slot, { doc: JSON.parse(bytes), sha256: snapshot.sha256,
    path: join(cal, snapshot.source) }];
}));
const probes = JSON.parse(readFileSync(join(here, process.argv[3] ?? "probes.json"), "utf8"));
for (const point of probes.points) {
  const out = join(outRoot, point.label);
  if (existsSync(out)) throw new Error(`Refuse existing candidate ${out}`);
  const patches: Record<string, Patch> = {};
  const materials: Record<string, typeof DEFAULT_MATERIAL_PROFILE> = {};
  const endpoints: Record<string, unknown> = {};
  mkdirSync(out, { recursive: true });
  for (const slot of slots) {
    const [pose, scheme] = slot.split(".");
    const source = sources[slot];
    const overrides = point.overrides[slot] ?? {};
    for (const [key, value] of Object.entries(overrides)) {
      if (!(key in DEFAULT_MATERIAL_PROFILE) || typeof value !== "number" || !Number.isFinite(value)) {
        throw new Error(`Unknown or invalid leaf ${key}`);
      }
    }
    const patch = { ...source.doc.patch, ...overrides };
    patches[slot] = patch;
    const material = withMaterialOverrides(pose === "active" ? DEFAULT_MATERIAL_PROFILE
      : materials[`active.${scheme}`]!, patch as MaterialProfilePatch);
    materials[slot] = material;
    const posed = pose === "active" ? patch : mergeMaterialProfiles(patches[`active.${scheme}`]!, patch);
    if (opaqueGlassViolations(posed as MaterialProfilePatch).length) throw new Error(`${slot} violates X75`);
    const doc = {
      ...source.doc,
      profileKey: source.doc.profileKey.replace("glass0.25", "glass0.250"),
      recordedBy: `W49b exploratory grounding ${point.label}; not a sealed document`,
      ...(pose === "receded" ? { resolvedOverActiveDocument: `active.${scheme}.json` } : {}),
      derivedFrom: { path: source.path, sha256: source.sha256 },
      patch,
      resolvedMaterialSha256: resolvedDigest(material),
    };
    const bytes = JSON.stringify(doc, null, 2) + "\n";
    writeFileSync(join(out, `${slot}.json`), bytes);
    endpoints[slot] = { path: `${slot}.json`, sha256: sha(bytes) };
  }
  writeFileSync(join(out, "candidate.json"), JSON.stringify({
    kind: CANDIDATE_DECLARATION_KIND, schemaVersion: 1,
    name: `apple-macos-27.0-glass0.25-w49b-grounding-${point.label}`,
    platform: "macOS 27.0", glassTintAmount: 0.25, endpoints,
    cssTierMappingSha256: cssTierMappingSha256(sources["active.light"].doc.cssTierMapping),
  }, null, 2) + "\n");
  readCandidateDocument(join(out, "candidate.json"));
  console.log(point.label, Object.fromEntries(slots.map(s => [s, resolvedDigest(materials[s]!)])));
}
