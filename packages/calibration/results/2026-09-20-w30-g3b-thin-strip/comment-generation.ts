/**
 * W30 G3b — record the renderer fix in the four macOS 27 documents, and prove
 * that doing so moves their BYTES and not their MATERIAL.
 *
 *   npx tsx results/2026-09-20-w30-g3b-thin-strip/comment-generation.ts <fix commit sha>
 *
 * Charter Decision Log 5 (b). A generation of `results/matrix.json` is keyed by
 * the profile document's own file hash, and a renderer fix does not move one —
 * so the rows this gate reads would key to the same cells as the rows W30 G3
 * read at the defective renderer, and `upsertCellResult` would overwrite a
 * recorded number rather than appending beside it. The ruling is to make the
 * document say what it is true of: a dated `$comment-w30-g3b` naming the defect,
 * the claims section that found it and the commit that fixed it. That is a true
 * statement about the conditions the rows beside it were read under, and it
 * moves the file hash for the right reason instead of by a spare field.
 *
 * **The inverse of the seal's own check.** `results/2026-09-20-w30-g3-operators/seal.ts`
 * asserts, before it writes, that the material each document resolves to
 * fingerprints to the digest the document carries. This file asserts the same
 * thing TWICE — once before the comment and once after — because the whole claim
 * of Decision Log 5 (b) is that one of the two hashes moves and the other does
 * not. A comment that changed `resolvedMaterialSha256` would mean the digest is
 * taken over the document rather than over the material, which would make every
 * pin in the runtime a pin on prose.
 *
 * Nothing under a macOS 26.5-keyed path is opened for writing (X1); the two
 * frozen documents are read and their pins re-asserted on every run, as the
 * seal does.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const PROFILES = resolve(import.meta.dirname, "..", "..", "profiles");

/** W29 G3's fingerprint, as `seal.ts` duplicates it: that file is committed evidence. */
function digest(resolved: unknown): string {
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
  return createHash("sha256").update(JSON.stringify(canonical(resolved))).digest("hex");
}

const fingerprint = (resolved: unknown): string => digest(resolved).slice(0, 16);

const path = (name: string): string => resolve(PROFILES, `${name}.json`);
const read = (name: string): Record<string, unknown> =>
  JSON.parse(readFileSync(path(name), "utf8")) as Record<string, unknown>;
const patchOf = (document: Record<string, unknown>): MaterialProfilePatch =>
  document["patch"] as MaterialProfilePatch;
const fileSha = (name: string): string =>
  createHash("sha256").update(readFileSync(path(name))).digest("hex");

const supersessions = (
  JSON.parse(readFileSync(resolve(PROFILES, "digest-supersessions.json"), "utf8")) as {
    supersessions: { profileKey: string; recordedSha256: string; currentSha256: string }[];
  }
).supersessions;

/** X1: the two frozen documents still record and resolve to what the record holds. */
for (const name of ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard"]) {
  const document = read(name);
  const record = supersessions.find((entry) => entry.profileKey === name);
  if (record === undefined) throw new Error(`${name}: no supersession record`);
  const got = fingerprint(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(document)));
  if (document["resolvedMaterialSha256"] !== record.recordedSha256 || got !== record.currentSha256) {
    throw new Error(
      `${name}: recorded ${String(document["resolvedMaterialSha256"])} / resolved ${got} ` +
        `against the record's ${record.recordedSha256} / ${record.currentSha256} — X1`,
    );
  }
  process.stdout.write(`X1 ok  ${name} records ${record.recordedSha256}, resolves to ${got}\n`);
}

const ACTIVE = {
  light: "apple-macos-27.0-1x-light-standard-glass0.5",
  dark: "apple-macos-27.0-1x-dark-standard-glass0.5",
} as const;

/**
 * The material a document resolves to, composed the way it is composed on the
 * page: an active patch over the renderer's default, a receded patch over the
 * active document of its own scheme.
 */
function materialOf(name: string): object {
  const document = read(name);
  const over = document["resolvedOverActiveDocument"];
  const base =
    typeof over === "string"
      ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(read(over.replace(/\.json$/, ""))))
      : DEFAULT_MATERIAL_PROFILE;
  return withMaterialOverrides(base, patchOf(document)) as object;
}

const NAMES = [ACTIVE.light, `${ACTIVE.light}-receded`, ACTIVE.dark, `${ACTIVE.dark}-receded`];

const commit = process.argv[2];
if (commit === undefined || !/^[0-9a-f]{7,40}$/.test(commit)) {
  throw new Error("comment-generation: name the fix commit's sha");
}

/** Before: every document's pin is the digest of the material it composes to. */
const before = new Map<string, { pin: string; material: string; file: string }>();
for (const name of NAMES) {
  const document = read(name);
  const pin = String(document["resolvedMaterialSha256"]);
  const material = fingerprint(materialOf(name));
  if (pin !== material) {
    throw new Error(
      `${name}: the material fingerprints to ${material} and the document pins ${pin} — ` +
        `this is not the construction the document was sealed under`,
    );
  }
  before.set(name, { pin, material, file: fileSha(name) });
  process.stdout.write(`construction ok  ${name}  pin ${pin} = material ${material}\n`);
}

const COMMENT =
  `2026-09-20, W30 G3b — the rows read at THESE bytes were captured at a renderer that ` +
  `draws the thin regime whole. At a casting span of 44 CSS px this document's own σ law ` +
  `draws σ = 2.13, and the optics pass's shadow falloff returned NaN more than 10.06 σ ` +
  `inside the shadow's silhouette — f32's exp overflowing inside tanh — which left a strip ` +
  `of a 44 px surface undrawn and put 170 texture cells outside W20's adopted declaration ` +
  `conformance (claims §5.159 §6, diagnosed and fixed in §5.159b, commit ${commit}). No ` +
  `constant of this document moved and no material moved: resolvedMaterialSha256 is ` +
  `unchanged and asserted unchanged by ` +
  `results/2026-09-20-w30-g3b-thin-strip/comment-generation.ts, which is what makes the ` +
  `re-read a generation of its own (charter Decision Log 5 (b)) rather than an overwrite ` +
  `of W30 G3's rows — those live in results/superseded/ by name.`;

for (const name of NAMES) {
  const document = read(name);
  if (document["$comment-w30-g3b"] !== undefined) {
    throw new Error(`${name}: already carries $comment-w30-g3b — this gate writes it once`);
  }
  document["$comment-w30-g3b"] = COMMENT;
  writeFileSync(path(name), `${JSON.stringify(document, null, 2)}\n`);
}

/** After: the file hash moved, and the material's did not. */
process.stdout.write("\n");
for (const name of NAMES) {
  const was = before.get(name);
  if (was === undefined) throw new Error(`${name}: no before reading`);
  const document = read(name);
  const pin = String(document["resolvedMaterialSha256"]);
  const material = fingerprint(materialOf(name));
  if (pin !== was.pin || material !== was.material || pin !== material) {
    throw new Error(
      `${name}: the comment moved the material — pin ${was.pin} -> ${pin}, material ` +
        `${was.material} -> ${material}`,
    );
  }
  const file = fileSha(name);
  if (file === was.file) {
    throw new Error(`${name}: the comment did not move the file hash, so the read would not append`);
  }
  process.stdout.write(
    `${name}\n` +
      `  resolvedMaterialSha256  ${was.pin} -> ${pin}   UNCHANGED\n` +
      `  resolved material       ${was.material} -> ${material}   UNCHANGED\n` +
      `  document sha256         ${was.file}\n` +
      `                       -> ${file}\n` +
      `  capturePath sha256      ${was.file.slice(0, 12)} -> ${file.slice(0, 12)}   MOVED\n`,
  );
}
