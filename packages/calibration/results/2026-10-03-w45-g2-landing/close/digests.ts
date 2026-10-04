/**
 * The ten shipped material digests, computed rather than quoted (W45 G2's close; claims §5.207).
 *
 *     pnpm exec tsx results/2026-10-03-w45-g2-landing/close/digests.ts   (from packages/calibration)
 *
 * 0.25.0's step (`results/2026-09-29-release-0.25.0/digests.ts`) over all ten shipped documents:
 * W45 moved exactly the two light 0.25 ones (sealed at W45 G1 step 3, §5.206 §13) and no other.
 * For each document it composes the material the way `test/tuned-profiles.test.ts` does — a
 * receded document over the ACTIVE document of its own scheme, every other one over
 * `DEFAULT_MATERIAL_PROFILE` — takes the live rule-2 fingerprint over the built renderer, and
 * compares three things to the literal this landing is expected to carry: that fingerprint, the
 * document's own recorded field, and the runtime's shipped endpoint in `@vitreajs/vitrea-web`. It
 * also prints each document file's twelve-hex SHA-256. Exit 1 on any disagreement. Runs after
 * `pnpm -r build`, because both packages resolve to dist.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
import {
  macos26MaterialProfileDocument,
  macos27Glass025MaterialProfileDocument,
  macos27MaterialProfileDocument,
} from "@vitreajs/vitrea-web";

interface Document {
  readonly profileKey: string;
  readonly patch: MaterialProfilePatch;
  readonly resolvedMaterialSha256: string;
  readonly resolvedOverActiveDocument?: string;
}

const PROFILES = resolve(import.meta.dirname, "..", "..", "..", "profiles");

function fingerprint(resolved: unknown): string {
  const canonical = (value: unknown): unknown =>
    Array.isArray(value)
      ? value.map(canonical)
      : value !== null && typeof value === "object"
        ? Object.fromEntries(
            Object.keys(value as object)
              .sort()
              .map((key) => [key, canonical((value as Record<string, unknown>)[key])]),
          )
        : value;
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);
}

const raw = (key: string): Buffer => readFileSync(resolve(PROFILES, `${key}.json`));
const load = (key: string): Document => JSON.parse(raw(key).toString("utf8")) as Document;

const m27 = macos27MaterialProfileDocument;
const m26 = macos26MaterialProfileDocument;
const g25 = macos27Glass025MaterialProfileDocument;
const EXPECTED: readonly (readonly [string, string, string | undefined])[] = [
  ["apple-macos-27.0-1x-light-standard-glass0.5", "be13dae45098fc89",
    m27.active.light.resolvedMaterialSha256],
  ["apple-macos-27.0-1x-dark-standard-glass0.5", "2a4323f33df8d799",
    m27.active.dark.resolvedMaterialSha256],
  ["apple-macos-27.0-1x-light-standard-glass0.5-receded", "b0d0d8dacc6a03af",
    m27.receded.light.resolvedMaterialSha256],
  ["apple-macos-27.0-1x-dark-standard-glass0.5-receded", "7c454858a3cbad5b",
    m27.receded.dark.resolvedMaterialSha256],
  ["apple-macos-26.5-1x-light-standard", "b2b570e4adcea8fb",
    m26.active.light.resolvedMaterialSha256],
  ["apple-macos-26.5-1x-dark-standard", "874be66ea501621b",
    m26.active.dark.resolvedMaterialSha256],
  // W45: the light pair moved (from 50430fa62c1120bd / 5d8680980b7aeb55); the dark pair did not.
  ["apple-macos-27.0-1x-light-standard-glass0.25", "3741b22934f17f4d",
    g25.active.light.resolvedMaterialSha256],
  ["apple-macos-27.0-1x-light-standard-glass0.25-receded", "c4ca0e1cd6791bde",
    g25.receded.light.resolvedMaterialSha256],
  ["apple-macos-27.0-1x-dark-standard-glass0.25", "b074fc6913a91c66",
    g25.active.dark.resolvedMaterialSha256],
  ["apple-macos-27.0-1x-dark-standard-glass0.25-receded", "280f0fddf014e0f6",
    g25.receded.dark.resolvedMaterialSha256],
];

console.log(`digest rule ${String(MATERIAL_DIGEST_RULE_VERSION)}`);
let failures = 0;
for (const [key, expected, runtime] of EXPECTED) {
  const document = load(key);
  const over = document.resolvedOverActiveDocument;
  const base =
    over === undefined
      ? DEFAULT_MATERIAL_PROFILE
      : withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, load(over.replace(/\.json$/, "")).patch);
  const live = fingerprint(materialDigestInput(withMaterialOverrides(base, document.patch)));
  const file = createHash("sha256").update(raw(key)).digest("hex").slice(0, 12);
  const ok =
    live === expected && document.resolvedMaterialSha256 === expected && runtime === expected;
  if (!ok) failures += 1;
  console.log(
    `${ok ? "ok  " : "FAIL"} ${key.padEnd(52)} live ${live}  recorded ` +
      `${document.resolvedMaterialSha256}  runtime ${String(runtime)}  expected ${expected}  ` +
      `file ${file}`,
  );
}
console.log(failures === 0 ? "all ten digests at their expected values" : `${String(failures)} digest(s) disagree`);
process.exit(failures === 0 ? 0 : 1);
