/**
 * Candidate mode's driver half (W43 G0 (f); charter `2026-10-01-w43-glass-0-25-generation.md`).
 *
 * A fit or a pre-seal read draws a material no shipped document carries. Until W43 the only
 * way to do that was to inject one profile document's patch over whichever shipped document
 * the key's OS token selected, so the read borrowed the shipped document's receded endpoints
 * and CSS crossing. Candidate mode replaces the borrowing with a declaration: one JSON file
 * naming the four endpoint documents and the CSS mapping by hash, from which the page builds
 * a complete `GlassMaterialProfileDocument` and nothing else.
 *
 * The declaration (`kind: "vitrea-candidate-material-document"`, `schemaVersion: 1`):
 *
 *   {
 *     "name": "apple-macos-27.0-glass0.25", "platform": "macOS 27.0", "glassTintAmount": 0.25,
 *     "endpoints": {
 *       "active.light":  { "path": "<relative to this file>", "sha256": "<64 hex of the file>" },
 *       "active.dark":   { ... }, "receded.light": { ... }, "receded.dark": { ... }
 *     },
 *     "cssTierMappingSha256": "<64 hex of the canonical JSON of the assembled mapping>"
 *   }
 *
 * Each endpoint file is an ordinary calibration profile document. The refusals here are the
 * ones only the driver can make, before any browser opens:
 * - a declared file hash that the file does not have;
 * - an endpoint document the key guard in `material-profile-file.ts` refuses, or a receded
 *   one that carries a CSS mapping;
 * - an endpoint whose recorded `resolvedMaterialSha256` does not reproduce over the runtime's
 *   `DEFAULT_MATERIAL_PROFILE` (an active endpoint) or over that default with its scheme's
 *   active endpoint applied (a receded one), under the current digest rule. This is what
 *   makes "built over the unmoved default" a check rather than a description;
 * - a CSS mapping the active documents disagree about, or whose canonical hash is not the
 *   declared one. The mapping is assembled as `generate-macos27-profile.mjs` assembles the
 *   shipped one: the light document's whole mapping, with the dark document's keys required
 *   to agree.
 * Then `validateCandidateDocument` runs against the real shipped registry, the same function
 * the page runs again before it draws.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
import { SHIPPED_MATERIAL_PROFILE_DOCUMENTS } from "@vitreajs/vitrea-web";

import {
  MATERIAL_POSES,
  MATERIAL_SCHEMES,
  validateCandidateDocument,
  type MaterialDocumentLike,
  type MaterialPose,
  type MaterialScheme,
} from "../src/material-selection";
import {
  readMaterialProfileFile,
  readRecededProfileFile,
  type MaterialProfileSections,
} from "./material-profile-file";

export const CANDIDATE_DECLARATION_KIND = "vitrea-candidate-material-document";

/** The endpoint document a slot names, as the driver read and checked it. */
export interface CandidateEndpointFile {
  readonly path: string;
  readonly sha256: string;
  readonly profileKey: string;
  readonly resolvedMaterialSha256: string;
}

/** What the page is handed: the document, and the stamp every output carries. */
export interface CandidateDocument {
  readonly declarationPath: string;
  /** First twelve hex of the declaration file's SHA-256, the repository's document-hash width. */
  readonly declarationSha256: string;
  readonly document: MaterialDocumentLike & {
    readonly glassTintAmount: number;
    readonly cssTierMapping: Record<string, unknown>;
  };
  readonly endpoints: Readonly<Record<`${MaterialPose}.${MaterialScheme}`, CandidateEndpointFile>>;
  readonly cssTierMappingSha256: string;
}

const sha256 = (bytes: Buffer | string): string => createHash("sha256").update(bytes).digest("hex");

/** Keys sorted at every depth, so only content decides a hash. */
const canonical = (value: unknown): unknown =>
  Array.isArray(value)
    ? value.map(canonical)
    : value !== null && typeof value === "object"
      ? Object.fromEntries(
          Object.keys(value as object).sort()
            .map((key) => [key, canonical((value as Record<string, unknown>)[key])]),
        )
      : value;

/** The canonical-JSON SHA-256 a declaration states for its CSS mapping. */
export const cssTierMappingSha256 = (mapping: unknown): string =>
  sha256(JSON.stringify(canonical(mapping)));

/** The digest `tuned-profiles.test.ts` and the seal scripts take: rule 2, sixteen hex. */
export const resolvedDigest = (resolved: unknown): string =>
  sha256(JSON.stringify(canonical(materialDigestInput(resolved)))).slice(0, 16);

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

function refuse(path: string, why: string): never {
  throw new Error(`--candidate-document ${path}: ${why}`);
}

/** Read, check and assemble a candidate declaration. Throws on the first refusal. */
export function readCandidateDocument(path: string): CandidateDocument {
  const text = readFileSync(path, "utf8");
  const declaration: unknown = JSON.parse(text);
  if (!isRecord(declaration)) refuse(path, "is not a JSON object");
  if (declaration["kind"] !== CANDIDATE_DECLARATION_KIND || declaration["schemaVersion"] !== 1) {
    refuse(path, `is not a ${CANDIDATE_DECLARATION_KIND} schemaVersion 1 declaration`);
  }
  const declared = declaration["endpoints"];
  if (!isRecord(declared)) refuse(path, "partial: declares no endpoints");
  const slots = MATERIAL_POSES.flatMap((pose) => MATERIAL_SCHEMES.map((scheme) => `${pose}.${scheme}`));
  const missing = slots.filter((slot) => !isRecord(declared[slot]));
  if (missing.length > 0) refuse(path, `partial: no ${missing.join(", ")} endpoint`);
  const extra = Object.keys(declared).filter((slot) => !slots.includes(slot));
  if (extra.length > 0) refuse(path, `declares endpoint slots no document has: ${extra.join(", ")}`);

  const read = new Map<string, { file: CandidateEndpointFile; sections: MaterialProfileSections }>();
  for (const slot of slots) {
    const entry = declared[slot] as Record<string, unknown>;
    if (typeof entry["path"] !== "string" || typeof entry["sha256"] !== "string") {
      refuse(path, `partial: ${slot} names no path and sha256`);
    }
    const file = resolve(dirname(path), entry["path"]);
    const actual = sha256(readFileSync(file));
    if (actual !== entry["sha256"]) {
      refuse(path, `${slot} declares sha256 ${entry["sha256"]}, and ${file} has ${actual}`);
    }
    const sections = slot.startsWith("receded.")
      ? readRecededProfileFile(file)
      : readMaterialProfileFile(file);
    const recorded = (JSON.parse(readFileSync(file, "utf8")) as Record<string, unknown>)["resolvedMaterialSha256"];
    if (sections.profileKey === undefined) refuse(path, `partial: ${slot} document names no profileKey`);
    if (typeof recorded !== "string") refuse(path, `partial: ${slot} document records no resolvedMaterialSha256`);
    read.set(slot, {
      file: { path: file, sha256: actual, profileKey: sections.profileKey, resolvedMaterialSha256: recorded },
      sections,
    });
  }
  const slot = (pose: MaterialPose, scheme: MaterialScheme) => read.get(`${pose}.${scheme}`)!;

  for (const scheme of MATERIAL_SCHEMES) {
    const active = slot("active", scheme);
    const activeResolved = withMaterialOverrides(
      DEFAULT_MATERIAL_PROFILE, active.sections.patch as MaterialProfilePatch);
    const activeDigest = resolvedDigest(activeResolved);
    if (activeDigest !== active.file.resolvedMaterialSha256) {
      refuse(path, `active.${scheme} records resolvedMaterialSha256 ${active.file.resolvedMaterialSha256}, ` +
        `and its patch over the runtime's DEFAULT_MATERIAL_PROFILE resolves to ${activeDigest}`);
    }
    const receded = slot("receded", scheme);
    const recededDigest = resolvedDigest(
      withMaterialOverrides(activeResolved, receded.sections.patch as MaterialProfilePatch));
    if (recededDigest !== receded.file.resolvedMaterialSha256) {
      refuse(path, `receded.${scheme} records resolvedMaterialSha256 ${receded.file.resolvedMaterialSha256}, ` +
        `and its patch over active.${scheme} resolves to ${recededDigest}`);
    }
  }

  const light = slot("active", "light").sections.cssTierMapping;
  if (light === undefined || Object.keys(light).length === 0) {
    refuse(path, "partial: the active.light document carries no cssTierMapping, the candidate's crossing");
  }
  for (const [key, value] of Object.entries(slot("active", "dark").sections.cssTierMapping ?? {})) {
    if (JSON.stringify(canonical(value)) !== JSON.stringify(canonical(light[key]))) {
      refuse(path, `cssTierMapping.${key}: the active.light document says ${JSON.stringify(light[key])} ` +
        `and the active.dark document says ${JSON.stringify(value)}; one material has one crossing`);
    }
  }
  const mappingSha256 = cssTierMappingSha256(light);
  if (declaration["cssTierMappingSha256"] !== mappingSha256) {
    refuse(path, `declares cssTierMappingSha256 ${String(declaration["cssTierMappingSha256"])}, and the ` +
      `assembled mapping hashes to ${mappingSha256}`);
  }

  const endpoint = (pose: MaterialPose, scheme: MaterialScheme) => ({
    profileKey: slot(pose, scheme).file.profileKey,
    patch: slot(pose, scheme).sections.patch,
    resolvedMaterialSha256: slot(pose, scheme).file.resolvedMaterialSha256,
  });
  const document = {
    name: declaration["name"] as string,
    platform: declaration["platform"] as string,
    glassTintAmount: declaration["glassTintAmount"] as number,
    active: { light: endpoint("active", "light"), dark: endpoint("active", "dark") },
    receded: { light: endpoint("receded", "light"), dark: endpoint("receded", "dark") },
    cssTierMapping: light,
  };
  validateCandidateDocument(document, SHIPPED_MATERIAL_PROFILE_DOCUMENTS);

  return {
    declarationPath: path,
    declarationSha256: sha256(text).slice(0, 12),
    document,
    endpoints: Object.fromEntries(slots.map((s) => [s, read.get(s)!.file])) as CandidateDocument["endpoints"],
    cssTierMappingSha256: mappingSha256,
  };
}
