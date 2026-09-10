/*
 * W26 G2 — the resolved material's fingerprint for the two profile documents, at the candidate.
 *
 * W25 G3's `g3-fingerprint.mjs` with one addition: `--heavy <sigma1x> <sigma2x>` resolves the two
 * documents over a `DEFAULT_MATERIAL_PROFILE` whose heavy anchors carry the candidate, which is
 * what a landing produces — the light document names the two constants in its patch and the dark
 * document is a difference document that inherits them through the default (X7). Run without the
 * flag it prints what the working tree resolves to, which is how the landing is verified after the
 * edit.
 *
 * The digest is `tuned-profiles.test.ts`'s own: keys sorted at every depth, JSON, sha256, first
 * sixteen hex digits — restated here rather than imported, because the test is a test and this is
 * a tool, and a tool that imported it would make the pin circular.
 *
 *   pnpm exec tsx results/2026-09-10-w26-heavy-width/g2/g2-fingerprint.mjs [--heavy 9 9]
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
} from "../../../../renderer-webgpu/src/material.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROFILES = resolve(HERE, "..", "..", "..", "profiles");

const argv = process.argv.slice(2);
const heavyAt = argv.indexOf("--heavy");
const base =
  heavyAt === -1
    ? DEFAULT_MATERIAL_PROFILE
    : withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, {
        sizeHeavyTapSigma: Number(argv[heavyAt + 1]),
        sizeHeavyTapSigma2x: Number(argv[heavyAt + 2]),
      });

const canonical = (value) =>
  Array.isArray(value)
    ? value.map(canonical)
    : value !== null && typeof value === "object"
      ? Object.fromEntries(
          Object.keys(value)
            .sort()
            .map((key) => [key, canonical(value[key])]),
        )
      : value;

const fingerprint = (resolved) =>
  createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex").slice(0, 16);

for (const name of [
  "apple-macos-26.5-1x-light-standard.json",
  "apple-macos-26.5-1x-dark-standard.json",
]) {
  const document = JSON.parse(readFileSync(resolve(PROFILES, name), "utf8"));
  const patch =
    heavyAt === -1
      ? document.patch
      : name.includes("light")
        ? {
            ...document.patch,
            sizeHeavyTapSigma: base.sizeHeavyTapSigma,
            sizeHeavyTapSigma2x: base.sizeHeavyTapSigma2x,
          }
        : document.patch;
  const resolvedNow = fingerprint(withMaterialOverrides(base, patch));
  const recorded = document.resolvedMaterialSha256;
  console.log(
    `${name.padEnd(44)} recorded ${recorded}  resolves to ${resolvedNow}` +
      (recorded === resolvedNow ? "  (unchanged)" : "  (RE-RECORD)"),
  );
}
