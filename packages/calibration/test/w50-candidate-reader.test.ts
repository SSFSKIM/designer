/**
 * W50 DL4: live low-end charts must survive the real candidate-document reader,
 * not just the renderer's patch boundary. The source documents stay untouched;
 * complete four-endpoint candidates are assembled and hash-matched in scratch.
 */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

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
} from "../scripts/candidate-document";

const PROFILES = resolve(import.meta.dirname, "../profiles");
const GUARD = resolve(import.meta.dirname,
  "../results/2026-10-08-w50-g0-declaration/audit/numerical_guard.py");
const sha256 = (text: string) => createHash("sha256").update(text).digest("hex");

function writeCandidate(dir: string, glass: "0.25" | "0.5"): string {
  // Candidate mode refuses shipped key strings; these spellings preserve the actual positions.
  const candidateGlass = glass === "0.25" ? "0.250" : "0.500";
  const endpoints: Record<string, { path: string; sha256: string }> = {};
  let mapping: unknown;
  for (const scheme of ["light", "dark"] as const) {
    let base = DEFAULT_MATERIAL_PROFILE;
    for (const pose of ["active", "receded"] as const) {
      const key = `apple-macos-27.0-1x-${scheme}-standard-glass${glass}` +
        (pose === "receded" ? "-receded" : "");
      const document = JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as {
        profileKey: string;
        patch: MaterialProfilePatch;
        resolvedMaterialSha256: string;
        cssTierMapping?: unknown;
      };
      document.profileKey = document.profileKey.replace(`-glass${glass}`, `-glass${candidateGlass}`);
      if (scheme === "dark") {
        document.patch = { ...document.patch, ...(pose === "active" ? {
          lowEndStrength: 1,
          lowEnd44: [32 / 255, 40 / 255, 56 / 255, 69 / 255],
          lowEnd96: [33 / 255, 41 / 255, 57 / 255, 70 / 255],
          lowEnd160: [34 / 255, 42 / 255, 58 / 255, 71 / 255],
        } : {
          lowEndStrength: 1,
          lowEnd44: [20 / 255, 28 / 255, 48 / 255, 60 / 255],
          lowEnd96: [21 / 255, 29 / 255, 49 / 255, 61 / 255],
          lowEnd160: [22 / 255, 30 / 255, 50 / 255, 62 / 255],
        }) };
      }
      const material = withMaterialOverrides(base, document.patch);
      document.resolvedMaterialSha256 = resolvedDigest(material);
      if (pose === "active") base = material;
      if (pose === "active" && scheme === "light") mapping = document.cssTierMapping;
      const slot = `${pose}.${scheme}`;
      const text = `${JSON.stringify(document, null, 2)}\n`;
      writeFileSync(join(dir, `${slot}.json`), text);
      endpoints[slot] = { path: `${slot}.json`, sha256: sha256(text) };
    }
  }
  const path = join(dir, "candidate.json");
  writeFileSync(path, `${JSON.stringify({
    kind: CANDIDATE_DECLARATION_KIND,
    schemaVersion: 1,
    name: `w50-candidate-glass${candidateGlass}`,
    platform: "macOS 27.0",
    glassTintAmount: Number(glass),
    endpoints,
    cssTierMappingSha256: cssTierMappingSha256(mapping),
  }, null, 2)}\n`);
  return path;
}

describe("W50 candidate low-end charts", () => {
  it.each(["0.25", "0.5"] as const)(
    "reads and resolves all four low-end fields on the glass %s dark endpoint pair",
    (glass) => {
      const dir = mkdtempSync(join(tmpdir(), "w50-candidate-reader-"));
      try {
        const path = writeCandidate(dir, glass);
        const { document } = readCandidateDocument(path);
        expect(document.glassTintAmount).toBe(Number(glass));
        const expected = {
          active: {
            lowEndStrength: 1,
            lowEnd44: [32 / 255, 40 / 255, 56 / 255, 69 / 255],
            lowEnd96: [33 / 255, 41 / 255, 57 / 255, 70 / 255],
            lowEnd160: [34 / 255, 42 / 255, 58 / 255, 71 / 255],
          },
          receded: {
            lowEndStrength: 1,
            lowEnd44: [20 / 255, 28 / 255, 48 / 255, 60 / 255],
            lowEnd96: [21 / 255, 29 / 255, 49 / 255, 61 / 255],
            lowEnd160: [22 / 255, 30 / 255, 50 / 255, 62 / 255],
          },
        };
        for (const scheme of ["light", "dark"] as const) {
          let base = DEFAULT_MATERIAL_PROFILE;
          for (const pose of ["active", "receded"] as const) {
            const endpoint = document[pose][scheme];
            const material = withMaterialOverrides(base, endpoint.patch as MaterialProfilePatch);
            if (pose === "active") base = material;
            expect(resolvedDigest(material)).toBe(endpoint.resolvedMaterialSha256);
            if (scheme === "dark") {
              expect(endpoint.patch, `${pose}.dark parsed chart`).toMatchObject(expected[pose]);
              expect(material, `${pose}.dark resolved chart`).toMatchObject(expected[pose]);
            } else {
              expect(endpoint.patch).not.toHaveProperty("lowEndStrength");
              expect(material.lowEndStrength).toBe(0);
            }
          }
        }
        // Consume the identical reader-accepted bytes at the numerical guard's identity boundary.
        // No report, measured argument or numerical PASS is fabricated for this seam check.
        const consumer = spawnSync("python3", ["-I", "-c", `
import importlib.util
import json
from pathlib import Path
import sys
spec = importlib.util.spec_from_file_location("w50_numerical_guard", sys.argv[1])
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
path = Path(sys.argv[2])
candidate = json.loads(path.read_text())
for slot, pin in candidate["endpoints"].items():
    endpoint = json.loads((path.parent / pin["path"]).read_text())
    guard.validate_endpoint_identity(endpoint["profileKey"], slot, candidate["glassTintAmount"])
print(json.dumps({"position": candidate["glassTintAmount"], "slots": sorted(candidate["endpoints"])}))
`, GUARD, path], { encoding: "utf8", timeout: 10_000 });
        expect(consumer.status, consumer.stderr || String(consumer.error)).toBe(0);
        expect(JSON.parse(consumer.stdout)).toEqual({
          position: Number(glass),
          slots: ["active.dark", "active.light", "receded.dark", "receded.light"],
        });
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    },
  );
});
