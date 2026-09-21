/**
 * W31 G0 — the proof of what Decision Log 1 (a) ruled (claims §5.161 §6).
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/digest-rule-proof.ts
 *
 * The ruling: **the fingerprint drops a leaf whose resolved value equals its
 * declared inert identity**, so that adding an operator at its identity moves
 * no document's digest, the two frozen macOS 26.5 documents' recorded digests
 * are the live fingerprint again, and no wave spends an X1 exemption for an
 * inert leaf. G3 executes it; this file proves it computes the recorded digests
 * BEFORE G3 writes a line of it.
 *
 * Nothing here is a test or a document change. It reads
 * `identity-table.json` beside it, resolves each shipped document through the
 * renderer's own `withMaterialOverrides`, and fingerprints it with the same
 * canonicalising digest `seal.ts` and `tuned-profiles.test.ts` pin — so the
 * proof and the shipped fingerprint cannot disagree about what the material is.
 *
 * It prints five things:
 *
 *   1. The two frozen macOS 26.5 digests under the rule. They MUST read
 *      `b2b570e4adcea8fb` and `874be66ea501621b`, the documents' own recorded
 *      fields, and the script exits non-zero if they do not.
 *   2. The four macOS 27 documents' digests under the rule beside their current
 *      ones, with the leaves dropped in each named. They move once, in G3's
 *      merge.
 *   3. W30's objection answered by value: a run with a leaf's DEFAULT moved off
 *      its identity in memory, showing the macOS 26.5 digests MOVE. A pin blind
 *      to the schema would not.
 *   4. The reading of a leaf a document sets EXPLICITLY to its identity, which
 *      the macOS 27 light document exercises.
 *   5. The holes the rule does not cover.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "profiles");

interface IdentityEntry {
  readonly wave: string;
  readonly gate: Readonly<Record<string, number>>;
  readonly gated: readonly string[];
  readonly law: string;
  readonly inertLawCase: string;
  readonly whyGated: string;
  readonly claims: string;
}
const TABLE = JSON.parse(
  readFileSync(resolve(HERE, "identity-table.json"), "utf8"),
) as { rule: { version: string }; entries: readonly IdentityEntry[] };

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

function at(value: unknown, path: string): unknown {
  return path.split(".").reduce<unknown>(
    (node, key) =>
      node !== null && typeof node === "object" ? (node as Record<string, unknown>)[key] : undefined,
    value,
  );
}

/** A copy of `value` with the named dotted paths removed, `w30-operator-identity`'s `without`. */
function without(value: unknown, paths: readonly string[], prefix = ""): unknown {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return value;
  return Object.fromEntries(
    Object.entries(value)
      .map(([key, child]) => [prefix === "" ? key : `${prefix}.${key}`, key, child] as const)
      .filter(([path]) => !paths.includes(path))
      .map(([path, key, child]) => [key, without(child, paths, path)]),
  );
}

/**
 * The rule. For each entry, if EVERY gate leaf of the entry holds its declared
 * identity in this resolved material, drop the gate leaves and the gated leaves
 * together. A gated leaf is never dropped on its own: a gated leaf has no
 * identity of its own to be at, which is exactly why the charter's Grounding
 * says three of W30's eight have none.
 */
function droppedLeaves(resolved: unknown): readonly string[] {
  const dropped: string[] = [];
  for (const entry of TABLE.entries) {
    const gateHeld = Object.entries(entry.gate).every(([path, identity]) => {
      const value = at(resolved, path);
      // A leaf the material does not have is not "at its identity" — it is
      // absent, and an entry naming it is a table that has drifted from the
      // material. Reported by the completeness check below rather than silently
      // treated as held.
      return value !== undefined && value === identity;
    });
    if (gateHeld) dropped.push(...Object.keys(entry.gate), ...entry.gated);
  }
  return dropped.sort();
}

function digestUnderRule(resolved: unknown): { digest: string; dropped: readonly string[] } {
  const dropped = droppedLeaves(resolved);
  return { digest: fingerprint(without(resolved, dropped)), dropped };
}

const read = (name: string): { patch: MaterialProfilePatch; resolvedMaterialSha256: string } =>
  JSON.parse(readFileSync(resolve(PROFILES, `${name}.json`), "utf8")) as never;

const resolveDocument = (name: string, base = DEFAULT_MATERIAL_PROFILE): unknown =>
  withMaterialOverrides(base, read(name).patch);

let failures = 0;
const fail = (message: string): void => {
  failures += 1;
  console.log(`  FAIL ${message}`);
};

// ---------------------------------------------------------------------------
// 0. The table names leaves the material actually has, at values it can hold.
// ---------------------------------------------------------------------------

console.log(`== the identity table (rule ${TABLE.rule.version}) ==`);
for (const entry of TABLE.entries) {
  const names = [...Object.keys(entry.gate), ...entry.gated];
  const live = names.filter((path) => at(DEFAULT_MATERIAL_PROFILE, path) !== undefined);
  const gateTag = Object.entries(entry.gate)
    .map(([path, identity]) => `${path} = ${String(identity)}`)
    .join(" and ");
  console.log(`  ${entry.wave}  gate: ${gateTag}`);
  console.log(`        gated: ${entry.gated.length === 0 ? "(none — a plain value drop)" : entry.gated.join(", ")}`);
  console.log(`        proof: ${entry.inertLawCase.split(" — ")[0] ?? ""}`);
  if (live.length !== names.length) {
    const missing = names.filter((path) => at(DEFAULT_MATERIAL_PROFILE, path) === undefined);
    // W31's own leaf is expected here: G0 names it, G3 adds it.
    console.log(`        NOT IN THE MATERIAL YET: ${missing.join(", ")} (W31 X2: G0 names, G3 adds)`);
  }
  for (const [path, identity] of Object.entries(entry.gate)) {
    const current = at(DEFAULT_MATERIAL_PROFILE, path);
    if (current !== undefined && current !== identity) {
      fail(`${path}: the default is ${String(current)}, the declared identity is ${String(identity)} — a post-seal leaf's default IS its identity`);
    }
  }
}

// ---------------------------------------------------------------------------
// 1. The frozen macOS 26.5 documents reproduce their recorded digests.
// ---------------------------------------------------------------------------

const FROZEN = [
  ["apple-macos-26.5-1x-light-standard", "b2b570e4adcea8fb"],
  ["apple-macos-26.5-1x-dark-standard", "874be66ea501621b"],
] as const;

console.log("\n== 1. the frozen macOS 26.5 documents, under the rule ==");
for (const [name, expected] of FROZEN) {
  const document = read(name);
  const resolved = resolveDocument(name);
  const live = fingerprint(resolved);
  const { digest, dropped } = digestUnderRule(resolved);
  console.log(`  ${name}`);
  console.log(`    recorded in the document   ${document.resolvedMaterialSha256}`);
  console.log(`    today's plain fingerprint  ${live}`);
  console.log(`    under the rule             ${digest}`);
  console.log(`    dropped (${dropped.length}): ${dropped.join(", ")}`);
  if (digest !== expected) fail(`${name}: under the rule ${digest}, recorded ${expected}`);
  if (document.resolvedMaterialSha256 !== expected) {
    fail(`${name}: the document records ${document.resolvedMaterialSha256}, not ${expected}`);
  }
}

// ---------------------------------------------------------------------------
// 2. The four macOS 27 documents under the rule, beside their current digests.
// ---------------------------------------------------------------------------

const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5";
const DARK = "apple-macos-27.0-1x-dark-standard-glass0.5";

console.log("\n== 2. the four macOS 27 documents, under the rule ==");
console.log("   They move ONCE, in G3's merge, re-sealed with history and the rule's version.");
for (const [name, base] of [
  [LIGHT, DEFAULT_MATERIAL_PROFILE],
  [DARK, DEFAULT_MATERIAL_PROFILE],
  [`${LIGHT}-receded`, withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read(LIGHT).patch)],
  [`${DARK}-receded`, withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read(DARK).patch)],
] as const) {
  const document = read(name);
  const resolved = withMaterialOverrides(base, document.patch);
  const { digest, dropped } = digestUnderRule(resolved);
  console.log(`  ${name}`);
  console.log(`    current (in the document)  ${document.resolvedMaterialSha256}`);
  console.log(`    under the rule             ${digest}`);
  console.log(`    dropped (${dropped.length}): ${dropped.length === 0 ? "nothing" : dropped.join(", ")}`);
  if (fingerprint(resolved) !== document.resolvedMaterialSha256) {
    fail(`${name}: the plain fingerprint does not reproduce the document's own field`);
  }
}

// ---------------------------------------------------------------------------
// 3. W30's objection, answered by value: move a DEFAULT off its identity.
// ---------------------------------------------------------------------------

console.log("\n== 3. a default moved off its identity, in memory ==");
console.log("   W30's objection to a schema-blind pin was that it would hide a leaf that");
console.log("   started drawing. Under this rule it cannot: the leaf reappears in the");
console.log("   digest the moment its resolved value leaves the identity, and every");
console.log("   document that does not patch it moves with it.");
const moved = { ...DEFAULT_MATERIAL_PROFILE, sizeHeavySecondShare: 0.1 };
for (const [name, expected] of FROZEN) {
  const resolved = withMaterialOverrides(moved, read(name).patch);
  const { digest, dropped } = digestUnderRule(resolved);
  console.log(`  ${name} with sizeHeavySecondShare defaulting to 0.1`);
  console.log(`    under the rule             ${digest}  (was ${expected})`);
  console.log(`    dropped (${dropped.length}): ${dropped.join(", ")}`);
  if (digest === expected) fail(`${name}: the digest did NOT move when a default left its identity`);
}

// ---------------------------------------------------------------------------
// 4. A leaf a document sets EXPLICITLY to its identity, and the light 27 one.
// ---------------------------------------------------------------------------

console.log("\n== 4. an explicit identity reads as absent ==");
{
  const lightPatch = read(LIGHT).patch as Record<string, unknown>;
  const resolved = resolveDocument(LIGHT);
  const { dropped } = digestUnderRule(resolved);
  console.log(`  the macOS 27 light document declines the scatter:`);
  console.log(`    sizeScatterScaleGain = ${String(lightPatch["sizeScatterScaleGain"])} (the gate, at its identity)`);
  console.log(`    sizeScatterScaleRef  = ${String(lightPatch["sizeScatterScaleRef"])} (gated, and off any would-be standalone identity)`);
  console.log(`  Under gate-groups BOTH drop: ${dropped.includes("sizeScatterScaleGain") && dropped.includes("sizeScatterScaleRef")}`);
  console.log("  The digest is over what DRAWS, and a declined operator draws nothing — so a");
  console.log("  document that names the reference it declined at reads the same as one that");
  console.log("  never named it. The decline is not lost: it is a MEASUREMENT and it lives in");
  console.log("  the document's own patch and in the ledger, which is where a decline belongs.");
  console.log("  The same document's DARK sibling adopts the scatter (gain -2), so the group");
  console.log("  is kept there and the two documents' digests differ on it, as they must.");
  const darkDropped = digestUnderRule(resolveDocument(DARK)).dropped;
  if (darkDropped.includes("sizeScatterScaleGain")) {
    fail("the dark 27 document dropped the scatter group, which it adopts");
  }
}

// ---------------------------------------------------------------------------
// 5. The holes.
// ---------------------------------------------------------------------------

console.log(`
== 5. what the rule does not catch ==

  (a) A MIS-DECLARED IDENTITY, and it is the only hole with teeth. A plain value
      drop is injective for free — every resolved material carries every key, so
      two materials with the same post-drop object hold the identity on every
      dropped leaf and therefore agree everywhere. A GATE-GROUP drop is not: it
      merges every material sharing a gate at its identity, whatever the gated
      leaves hold, and is sound only because those leaves provably cannot reach
      the pixels. If a gate is declared where none exists, two materials that
      draw differently get one digest. Mitigated by the table requiring the
      inert-law unit case per entry, and by the gate being the narrowest thing
      that closes the leaf — which is why the sigma entry's gate is TWO leaves
      and not the slope alone (see the table's comment).

  (b) A DEFAULT THAT MOVES TO A VALUE SOME DOCUMENT EXPLICITLY CARRIED. The
      document's leaf then resolves to the new default, and if the identity
      moved with it the leaf drops out of that document's digest. **This is a
      hole in the digest and not in the material**, and it is narrow: the
      identity is a committed append-only constant, not the default, so moving
      a default to a value is not moving the identity to it, and a leaf whose
      default leaves its identity reappears in EVERY document's digest (case 3
      above). The residue is the case where a wave moves both together, which
      is a re-declaration of what the leaf's off state means and belongs in a
      Decision Log rather than in a diff.

  (c) A LEAF ADDED WITHOUT A TABLE ENTRY. It is carried in the digest at
      whatever it holds, so every document's digest moves — the loud failure,
      not the quiet one, and the one W30 actually hit. Not a hole; the cost of
      the rule is that an inert leaf must be DECLARED inert to be free.

  (d) THE RULE'S OWN VERSION. Two runs of two rule versions produce two digests
      over one material, and a recorded digest that does not name its function
      is ambiguous. Closed by construction rather than by care: the version is
      recorded in every document re-sealed under the rule
      (\`resolvedMaterialSha256Rule\`, or the history idiom), which G3 carries.
      The two macOS 26.5 documents are the exception that needs no field —
      their recorded digests equal BOTH definitions' output, which is the whole
      content of section 1.
`);

console.log(failures === 0 ? "PROOF OK — no failures" : `PROOF FAILED — ${failures} failure(s)`);
process.exit(failures === 0 ? 0 : 1);
