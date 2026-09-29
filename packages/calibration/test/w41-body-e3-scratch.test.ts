/** The candidate must preserve the complete posed material, not rebase E3 on active. */
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
function assertShippedPins(): void {
  expect(Object.keys(pins)).toHaveLength(6);
  for (const [name, pin] of Object.entries(pins)) {
    expect(sha(readFileSync(resolve(PROFILES, name))), name).toBe(pin.sha256);
    expect(document(PROFILES, name).resolvedMaterialSha256, name).toBe(pin.resolvedMaterialSha256);
    expect(digest(resolved(PROFILES, name)), name).toBe(pin.resolvedMaterialSha256);
  }
}

describe("W41 scratch-only E3 endpoint selection", () => {
  it("keeps all six shipped file and resolved pins, including both frozen 26.5 documents", () => {
    assertShippedPins();
  });

  it("copies unclaimed endpoints byte-for-byte and adds E3 only to the full light-receded patch", () => {
    const out = mkdtempSync(resolve(tmpdir(), "vitrea-w41-scratch-"));
    try {
      generateScratchCandidate(out);
      assertShippedPins();
      for (const name of [LIGHT, DARK, DARK_RECEDED]) {
        expect(readFileSync(resolve(out, name)).equals(readFileSync(resolve(PROFILES, name))), name)
          .toBe(true);
        expect(resolved(out, name), name).toStrictEqual(resolved(PROFILES, name));
        expect(resolved(out, name).bodyE3Strength, name).toBe(0);
      }
      const original = document(PROFILES, RECEDED);
      const scratch = document(out, RECEDED);
      const { bodyE3Strength, bodyE3Gains, bodyE3Neutral, ...existing } = scratch.patch;
      expect(existing).toStrictEqual(original.patch);
      expect(bodyE3Strength).toBe(1);
      expect(bodyE3Gains).toEqual([0.929205829365914, 0.9597570955316058, 0.9383102545096953]);
      expect(bodyE3Neutral).toEqual([150, 157, 164, 171, 178, 188, 197]);
      expect(scratch.resolvedOverActiveDocument).toBe(LIGHT);
      expect(resolve(CALIBRATION, "../..", scratch.appliesOver as string)).toBe(resolve(out, LIGHT));
      const candidate = resolved(out, RECEDED);
      expect(candidate.bodyE3Strength).toBe(1);
      expect(digest(candidate)).not.toBe(original.resolvedMaterialSha256);
      expect(scratch.resolvedMaterialSha256).toBe(digest(candidate));
      expect(scratch.resolvedMaterialSha256Rule).toBe(2);
      // Reset only the new group: every pre-existing posed field must equal baseline.
      expect(withMaterialOverrides(candidate, {
        bodyE3Strength: 0, bodyE3Gains: [1, 1, 1], bodyE3Neutral: [40, 56, 72, 88, 104, 128, 150],
      })).toStrictEqual(resolved(PROFILES, RECEDED));
      expect(readMaterialProfileFile(resolve(out, LIGHT)).patch).toEqual(document(out, LIGHT).patch);
      const loaded = readRecededProfileFile(resolve(out, RECEDED));
      expect(loaded.patch).toEqual(scratch.patch);
      const fullSha = sha(readFileSync(resolve(out, RECEDED)));
      expect(loaded.sha256).toBe(fullSha.slice(0, 12));
      expect(loaded.sha256).not.toBe(scratch.resolvedMaterialSha256);
      const evidence = JSON.parse(readFileSync(resolve(out, "evidence.json"), "utf8")) as {
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
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });
});
