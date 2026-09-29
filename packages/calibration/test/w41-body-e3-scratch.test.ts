/**
 * The candidate must preserve the complete posed material, not rebase E3 on active.
 *
 * W41 G2 (c9a §5.193): the shipped light receded document now enables E3 at exactly this
 * candidate's patch. Before that seal the test regenerated the candidate from the shipped
 * documents; the generator refuses once its source pin moves, by design, so the committed
 * candidate is now what the sealed document is checked against, and G1's pre-seal pins stay
 * the witness that the seal moved E3 and no other leaf.
 */
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  DEFAULT_MATERIAL_PROFILE, materialDigestInput, withMaterialOverrides,
  type MaterialProfile, type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
import { readMaterialProfileFile, readRecededProfileFile } from "../scripts/material-profile-file";
import { generateScratchCandidate } from
  "../results/2026-09-27-w41-g1-identification/body-leaf/generate-scratch";

const CALIBRATION = resolve(import.meta.dirname, "..");
const LEAF = resolve(CALIBRATION, "results/2026-09-27-w41-g1-identification/body-leaf");
const PROFILES = resolve(CALIBRATION, "profiles");
const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5.json";
const RECEDED = LIGHT.replace(".json", "-receded.json");
const DARK = LIGHT.replace("light", "dark");
const DARK_RECEDED = DARK.replace(".json", "-receded.json");
interface Document {
  patch: MaterialProfilePatch;
  resolvedMaterialSha256: string;
  resolvedMaterialSha256Rule?: number;
  resolvedOverActiveDocument?: string;
  appliesOver?: string;
}
const document = (dir: string, name: string): Document =>
  JSON.parse(readFileSync(resolve(dir, name), "utf8")) as Document;
const sha = (bytes: string | Buffer): string => createHash("sha256").update(bytes).digest("hex");
function sorted(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sorted);
  if (value === null || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0)
    .map(([key, child]) => [key, sorted(child)]));
}
const digest = (material: MaterialProfile): string =>
  sha(JSON.stringify(sorted(materialDigestInput(material)))).slice(0, 16);
function resolved(dir: string, name: string): MaterialProfile {
  const doc = document(dir, name);
  const base = doc.resolvedOverActiveDocument === undefined ? DEFAULT_MATERIAL_PROFILE :
    resolved(dir, doc.resolvedOverActiveDocument);
  return withMaterialOverrides(base, doc.patch);
}

const pins = JSON.parse(readFileSync(resolve(LEAF, "source-document-pins.json"), "utf8")) as
  Record<string, { sha256: string; resolvedMaterialSha256: string }>;
const CANDIDATE = resolve(LEAF, "candidate");
const E3_IDENTITY: MaterialProfilePatch = {
  bodyE3Strength: 0, bodyE3Gains: [1, 1, 1], bodyE3Neutral: [40, 56, 72, 88, 104, 128, 150],
};
function assertShippedPins(): void {
  expect(Object.keys(pins)).toHaveLength(6);
  for (const [name, pin] of Object.entries(pins)) {
    if (name === RECEDED) continue;
    expect(sha(readFileSync(resolve(PROFILES, name))), name).toBe(pin.sha256);
    expect(document(PROFILES, name).resolvedMaterialSha256, name).toBe(pin.resolvedMaterialSha256);
    expect(digest(resolved(PROFILES, name)), name).toBe(pin.resolvedMaterialSha256);
  }
  // The sealed receded document is the candidate's patch; with its E3 group reset it is the
  // pre-seal material G1 pinned.
  const sealed = document(PROFILES, RECEDED);
  const candidate = document(CANDIDATE, RECEDED);
  expect(sealed.patch).toStrictEqual(candidate.patch);
  expect(sealed.resolvedMaterialSha256).toBe(candidate.resolvedMaterialSha256);
  expect(digest(resolved(PROFILES, RECEDED))).toBe(sealed.resolvedMaterialSha256);
  expect(digest(withMaterialOverrides(resolved(PROFILES, RECEDED), E3_IDENTITY)))
    .toBe(pins[RECEDED]!.resolvedMaterialSha256);
}

describe("W41 scratch-only E3 endpoint selection", () => {
  it("keeps the five unclaimed pins; the light receded document moved by E3 alone", () => {
    assertShippedPins();
  });

  it("the committed candidate copies unclaimed endpoints byte-for-byte and adds E3 only", () => {
    assertShippedPins();
    for (const name of [LIGHT, DARK, DARK_RECEDED]) {
      expect(readFileSync(resolve(CANDIDATE, name)).equals(readFileSync(resolve(PROFILES, name))),
        name).toBe(true);
      expect(resolved(CANDIDATE, name), name).toStrictEqual(resolved(PROFILES, name));
      expect(resolved(CANDIDATE, name).bodyE3Strength, name).toBe(0);
    }
    const scratch = document(CANDIDATE, RECEDED);
    const { bodyE3Strength, bodyE3Gains, bodyE3Neutral, ...existing } = scratch.patch;
    expect(digest(withMaterialOverrides(resolved(PROFILES, LIGHT), existing)))
      .toBe(pins[RECEDED]!.resolvedMaterialSha256);
    expect(bodyE3Strength).toBe(1);
    expect(bodyE3Gains).toEqual([0.929205829365914, 0.9597570955316058, 0.9383102545096953]);
    expect(bodyE3Neutral).toEqual([150, 157, 164, 171, 178, 188, 197]);
    expect(scratch.resolvedOverActiveDocument).toBe(LIGHT);
    expect(resolve(CALIBRATION, "../..", scratch.appliesOver as string))
      .toBe(resolve(CANDIDATE, LIGHT));
    const candidate = resolved(CANDIDATE, RECEDED);
    expect(candidate.bodyE3Strength).toBe(1);
    expect(digest(candidate)).not.toBe(pins[RECEDED]!.resolvedMaterialSha256);
    expect(scratch.resolvedMaterialSha256).toBe(digest(candidate));
    expect(scratch.resolvedMaterialSha256Rule).toBe(2);
    expect(readMaterialProfileFile(resolve(CANDIDATE, LIGHT)).patch)
      .toEqual(document(CANDIDATE, LIGHT).patch);
    const loaded = readRecededProfileFile(resolve(CANDIDATE, RECEDED));
    expect(loaded.patch).toEqual(scratch.patch);
    const fullSha = sha(readFileSync(resolve(CANDIDATE, RECEDED)));
    expect(fullSha).toBe("d34ebe3a73f281e542734737db6bbb92dbe4b432368307de067200eb31d571bd");
    expect(loaded.sha256).toBe(fullSha.slice(0, 12));
    expect(loaded.sha256).not.toBe(scratch.resolvedMaterialSha256);
    const evidence = JSON.parse(readFileSync(resolve(CANDIDATE, "evidence.json"), "utf8")) as {
      documents: Record<string, { sha256: string; captureSha256: string; resolvedMaterialSha256: string }>;
      neutralContinuation: { input: number; output: number; w36Native?: number }[];
    };
    expect(evidence.documents[RECEDED]).toMatchObject({
      sha256: fullSha, captureSha256: fullSha.slice(0, 12),
      resolvedMaterialSha256: scratch.resolvedMaterialSha256,
    });
    expect(evidence.neutralContinuation).toEqual([
      { input: 0, output: 132.5, w36Native: 133 },
      { input: 32, output: 146.5 },
      { input: 192, output: 2356 / 11 },
    ]);
  });

  it("the scratch generator refuses to regenerate over the sealed documents", () => {
    const out = mkdtempSync(resolve(tmpdir(), "vitrea-w41-scratch-"));
    try {
      expect(() => generateScratchCandidate(out))
        .toThrow(`W41 source pin changed: ${RECEDED}`);
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });
});
