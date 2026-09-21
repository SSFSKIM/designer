/**
 * W31 G3c — record the accessibility gate in the two LIGHT macOS 27 documents,
 * and prove that doing so moves their BYTES and not their MATERIAL.
 *
 *   npx tsx results/2026-09-21-w31-g3c-accessibility-gate/comment-generation.ts <fix commit sha>
 *
 * `results/2026-09-20-w30-g3b-thin-strip/comment-generation.ts` one rule along,
 * COPIED rather than reused on that file's own convention: nothing under
 * `results/` is edited after commit, and a script that hard-codes the documents
 * it moved is the only kind whose output a later reader can reproduce.
 *
 * **Why a comment at all.** A generation of `results/matrix.json` is keyed by
 * the profile document's own file hash, and a renderer change does not move one
 * — so the rows this gate reads would key to the same cells as W31 G3's and
 * `upsertCellResult` would overwrite a recorded number rather than appending
 * beside it. Decision Log 3 (d) rules the W30 G3b idiom: make the document say
 * what it is true of. The comment is a true statement about the conditions the
 * rows beside it were read under, and it moves the file hash for the right
 * reason instead of by a spare field.
 *
 * **Two documents and not four.** The gate changes what the LIGHT documents
 * draw under an accessibility policy — the two accessibility profiles are the
 * light material plus an occlusion lift, and there is no dark accessibility
 * profile in the bed. The dark documents draw byte-identically before and after,
 * so their rows are not superseded, they are not re-read in this branch, and
 * X10 keeps a document's bytes and the read at those bytes in one merge. Their
 * bytes are asserted unchanged here rather than left unsaid.
 *
 * **Three things this asserts, twice each.** The digest is taken under RULE 2
 * (`materialDigestInput`; W31 Decision Log 1 (a)), which is what these documents
 * now record, so the before/after check is against the function they were sealed
 * with. A comment that moved `resolvedMaterialSha256` would mean the digest is
 * taken over the document rather than over the material, which would make every
 * pin in the runtime a pin on prose.
 *
 * Nothing under a macOS 26.5-keyed path is opened for writing (X1); the two
 * frozen documents are read and their pins re-asserted on every run.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  materialDigestInput,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const PROFILES = resolve(import.meta.dirname, "..", "..", "profiles");

/** `seal.ts`'s fingerprint, verbatim: keys sorted, SHA-256, first 16 hex. */
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

const ruleDigest = (resolved: unknown): string => fingerprint(materialDigestInput(resolved));

const path = (name: string): string => resolve(PROFILES, `${name}.json`);
const read = (name: string): Record<string, unknown> =>
  JSON.parse(readFileSync(path(name), "utf8")) as Record<string, unknown>;
const patchOf = (document: Record<string, unknown>): MaterialProfilePatch =>
  document["patch"] as MaterialProfilePatch;
const fileSha = (name: string): string =>
  createHash("sha256").update(readFileSync(path(name))).digest("hex");

/** X1: the two frozen documents record what they resolve to, under the rule. */
for (const name of ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-1x-dark-standard"]) {
  const document = read(name);
  const got = ruleDigest(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(document)));
  if (got !== document["resolvedMaterialSha256"]) {
    throw new Error(
      `${name}: under rule ${String(MATERIAL_DIGEST_RULE_VERSION)} it resolves to ${got}, ` +
        `recorded ${String(document["resolvedMaterialSha256"])} — X1`,
    );
  }
  process.stdout.write(`X1 ok  ${name} records and resolves to ${got}\n`);
}

const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5";
const DARK = "apple-macos-27.0-1x-dark-standard-glass0.5";

/** The material a document resolves to, composed the way a root composes it. */
function materialOf(name: string): object {
  const document = read(name);
  const over = document["resolvedOverActiveDocument"];
  const base =
    typeof over === "string"
      ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(read(over.replace(/\.json$/, ""))))
      : DEFAULT_MATERIAL_PROFILE;
  return withMaterialOverrides(base, patchOf(document)) as object;
}

/** The two this gate writes, and the two it only watches. */
const MOVED = [LIGHT, `${LIGHT}-receded`];
const WATCHED = [DARK, `${DARK}-receded`];

const commit = process.argv[2];
if (commit === undefined || !/^[0-9a-f]{7,40}$/.test(commit)) {
  throw new Error("comment-generation: name the fix commit's sha");
}

const before = new Map<string, { pin: string; material: string; file: string }>();
for (const name of [...MOVED, ...WATCHED]) {
  const document = read(name);
  const pin = String(document["resolvedMaterialSha256"]);
  const material = ruleDigest(materialOf(name));
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
  `2026-09-21, W31 G3c — the rows read at THESE bytes were captured at a renderer in which ` +
  `bodyChromaRetention STANDS DOWN under an accessibility occlusion lift. W31 G3 applied the ` +
  `retention unconditionally, and Reduce Transparency and Increase Contrast are this document ` +
  `plus a lift of 0.75 (active) and 0.88/0.98 (receded, per preference), so the plate covers ` +
  `alpha + lift*(1 - alpha) of the backdrop there and the nominal retention restored a fraction ` +
  `of a chromaticity the preference had asked to have covered up: R went 0.9096 -> 3.0514 ` +
  `(reduced transparency, active), 0.8294 -> 2.1195 (its inactive pose) and 0.8147 -> 3.1700 ` +
  `(increased contrast, active), three beds inside the wave's own 0.80-1.20 band at 0.20.0. ` +
  `Decision Log 3 (d) ruled the fix and its fallback; the lift rule r*(1 - lift) was measured ` +
  `and left those beds at 1.7897 / 1.1507 / 1.8324, so the HARD GATE is what ships (claims ` +
  `§5.164 §13, commit ${commit}). No constant of this document moved and no material moved: ` +
  `resolvedMaterialSha256 is unchanged and asserted unchanged by ` +
  `results/2026-09-21-w31-g3c-accessibility-gate/comment-generation.ts, which is what makes the ` +
  `re-read a generation of its own rather than an overwrite of W31 G3's rows — those live in ` +
  `results/superseded/ by name. The two DARK documents carry no such line: the gate is the ` +
  `identity on every row they key, there is no dark accessibility profile in the bed, and their ` +
  `bytes are asserted unmoved by the same script.`;

/**
 * The review's finding N9, corrected BESIDE the line it is about rather than
 * over it (claims §5.164 §13). A recorded history line is evidence; this says
 * what is wrong with it and leaves it where it is. The dark documents carry the
 * same wrong parenthetical and are NOT edited here — X10 keeps a document's
 * bytes and the read at those bytes in one merge, and the dark bed is not
 * re-read at this gate. §13 carries the entry for the next re-seal.
 */
const HISTORY_CORRECTION =
  `2026-09-21, W31 G3c (review closure; claims §5.164 §13, finding N9). The LAST line of ` +
  `$comment-sha-history above reads "the reading under rule 2 (the plain resolved ` +
  `fingerprint)", and rule 2 is NOT the plain resolved fingerprint — it is the fingerprint of ` +
  `materialDigestInput(resolved), the material with MATERIAL_IDENTITY_TABLE's entries dropped ` +
  `where their gates hold their declared identities (W31 Decision Log 1 (a)). The parenthetical ` +
  `belongs to rule 1 alone and seal.ts's template appended it whatever rule the previous ` +
  `reading was taken under. The DIGESTS in that line are correct and are not restated here; ` +
  `only the description of the function is wrong. The corrected template is ` +
  `results/2026-09-21-w31-g3c-accessibility-gate/seal.ts.`;

for (const name of MOVED) {
  const document = read(name);
  if (document["$comment-w31-g3c"] !== undefined) {
    throw new Error(`${name}: already carries $comment-w31-g3c — this gate writes it once`);
  }
  document["$comment-w31-g3c"] = COMMENT;
  document["$comment-sha-history-correction"] = HISTORY_CORRECTION;
  writeFileSync(path(name), `${JSON.stringify(document, null, 2)}\n`);
}

process.stdout.write("\n== the two documents this gate moves ==\n");
for (const name of MOVED) {
  const was = before.get(name);
  if (was === undefined) throw new Error(`${name}: no before reading`);
  const document = read(name);
  const pin = String(document["resolvedMaterialSha256"]);
  const material = ruleDigest(materialOf(name));
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
      `  resolvedMaterialSha256  ${was.pin} -> ${pin}   UNCHANGED (rule ${String(MATERIAL_DIGEST_RULE_VERSION)})\n` +
      `  resolved material       ${was.material} -> ${material}   UNCHANGED\n` +
      `  document sha256         ${was.file}\n` +
      `                       -> ${file}\n` +
      `  capturePath sha256      ${was.file.slice(0, 12)} -> ${file.slice(0, 12)}   MOVED\n`,
  );
}

process.stdout.write("\n== the two this gate only watches (X10: not re-read, so not moved) ==\n");
for (const name of WATCHED) {
  const was = before.get(name);
  if (was === undefined) throw new Error(`${name}: no before reading`);
  const file = fileSha(name);
  if (file !== was.file) {
    throw new Error(`${name}: its bytes moved and this gate does not re-read it — X10`);
  }
  process.stdout.write(
    `${name}\n` +
      `  resolvedMaterialSha256  ${was.pin}   UNCHANGED\n` +
      `  document sha256         ${file}   UNCHANGED\n` +
      `  capturePath sha256      ${file.slice(0, 12)}   UNCHANGED\n`,
  );
}
