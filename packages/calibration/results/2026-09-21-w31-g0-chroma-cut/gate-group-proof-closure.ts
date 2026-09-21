/**
 * W31 G0 review closure (2026-09-21) — what the σ gate-group's second leaf buys,
 * by value (claims §5.161 §11, finding B4). Beside `digest-rule-proof.ts`;
 * nothing that file wrote is rewritten.
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/gate-group-proof-closure.ts
 *
 * The G0 Revision Note says the charter is wrong in two places and names the
 * second as the σ gate-group: that Grounding "puts `sigmaThinOffsetPx` under
 * the slope's gate". **It does not.** Grounding names exactly three leaves as
 * having no standalone identity — `sigmaSpanRefPx`, `sizeHeavySecondSigma{,2x}`
 * and `sizeScatterScaleRef` — and `sigmaThinOffsetPx` is not among them, which
 * leaves it where a leaf with an identity belongs: an ordinary value drop, and
 * sound, because a plain value drop is injective for free. So the charter is
 * wrong in ONE place, not two, and the shipped two-leaf gate is a TIGHTENING of
 * a correct shape rather than a correction of a broken one.
 *
 * A tightening is still worth a number rather than a reading, and this file is
 * that number. It fingerprints one material under three groupings of the σ law:
 *
 *   SHIPPED    gate {sigmaSlopePerSpan 0, sigmaThinOffsetPx 0} → sigmaSpanRefPx
 *   GROUNDING  gate {sigmaSlopePerSpan 0} → sigmaSpanRefPx, with the offset an
 *              ordinary value drop at 0
 *   LOOSER     gate {sigmaSlopePerSpan 0} → {sigmaSpanRefPx, sigmaThinOffsetPx}
 *              — the shape the Revision Note ATTRIBUTES to Grounding
 *
 * The material is the frozen macOS 26.5 light document with its shadow's thin
 * offset moved to 5 CSS px in memory — a material that draws a σ five px wider
 * at every span, on both tiers, which is a visible change to every outer shadow
 * the bed carries. Under LOOSER it fingerprints to the FROZEN digest, because
 * the slope is still 0 and that grouping drops the offset with the pivot. Under
 * SHIPPED and under GROUNDING it does not.
 *
 * So the shape the Note attributes to the charter is UNSOUND and the shape the
 * charter actually carries is not; SHIPPED drops a strict subset of what
 * GROUNDING drops, which is what makes it a tightening. Nothing here moves a
 * document, a digest or a leaf — the override lives for the length of one
 * process, exactly as `digest-rule-proof.ts` §3's does.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  outerShadowSigmaPx,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "profiles");

interface IdentityEntry {
  readonly wave: string;
  readonly gate: Readonly<Record<string, number>>;
  readonly gated: readonly string[];
  readonly inertLawCase: string;
}
const TABLE = JSON.parse(readFileSync(resolve(HERE, "identity-table.json"), "utf8")) as {
  rule: { version: string };
  entries: readonly IdentityEntry[];
};

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

function without(value: unknown, paths: readonly string[], prefix = ""): unknown {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return value;
  return Object.fromEntries(
    Object.entries(value)
      .map(([key, child]) => [prefix === "" ? key : `${prefix}.${key}`, key, child] as const)
      .filter(([path]) => !paths.includes(path))
      .map(([path, key, child]) => [key, without(child, paths, path)]),
  );
}

interface Grouping {
  readonly gate: Readonly<Record<string, number>>;
  readonly gated: readonly string[];
}

/** The rule of `digest-rule-proof.ts`, over an arbitrary set of groupings. */
function digestUnder(resolved: unknown, groupings: readonly Grouping[]): string {
  const dropped: string[] = [];
  for (const entry of groupings) {
    const held = Object.entries(entry.gate).every(([path, identity]) => {
      const value = at(resolved, path);
      return value !== undefined && value === identity;
    });
    if (held) dropped.push(...Object.keys(entry.gate), ...entry.gated);
  }
  return fingerprint(without(resolved, dropped.sort()));
}

const SHIPPED: readonly Grouping[] = TABLE.entries
  .filter((entry) => Object.keys(entry.gate).every((path) => at(DEFAULT_MATERIAL_PROFILE, path) !== undefined))
  .map((entry) => ({ gate: entry.gate, gated: entry.gated }));

/** The shape the Revision Note ATTRIBUTES to Grounding: the slope gates both. */
const LOOSER: readonly Grouping[] = SHIPPED.map((entry) =>
  "outerShadow.sigmaSlopePerSpan" in entry.gate
    ? {
        gate: { "outerShadow.sigmaSlopePerSpan": 0 },
        gated: [...entry.gated, "outerShadow.sigmaThinOffsetPx"],
      }
    : entry,
);

/**
 * The shape Grounding actually carries: the slope gates the pivot, and the
 * offset is an ordinary value drop at its own identity — which is expressed
 * here as a gate-group with no gated leaves, the table's own idiom for one.
 */
const GROUNDING: readonly Grouping[] = SHIPPED.flatMap((entry) =>
  "outerShadow.sigmaSlopePerSpan" in entry.gate
    ? [
        { gate: { "outerShadow.sigmaSlopePerSpan": 0 }, gated: entry.gated },
        { gate: { "outerShadow.sigmaThinOffsetPx": 0 }, gated: [] },
      ]
    : [entry],
);

const read = (name: string): { patch: MaterialProfilePatch; resolvedMaterialSha256: string } =>
  JSON.parse(readFileSync(resolve(PROFILES, `${name}.json`), "utf8")) as never;

let failures = 0;
const fail = (message: string): void => {
  failures += 1;
  console.log(`  FAIL ${message}`);
};

console.log(`== the identity table's citations, as this closure leaves them (rule ${TABLE.rule.version}) ==\n`);
for (const entry of TABLE.entries) {
  const gateTag = Object.entries(entry.gate)
    .map(([path, identity]) => `${path} = ${String(identity)}`)
    .join(" and ");
  console.log(`  ${entry.wave}  gate: ${gateTag}`);
  console.log(`        proof: ${entry.inertLawCase.split(" — ")[0] ?? ""}`);
}

console.log(`
== the three groupings, on one material that draws differently ==`);

const FROZEN = [
  ["apple-macos-26.5-1x-light-standard", "b2b570e4adcea8fb"],
  ["apple-macos-26.5-1x-dark-standard", "874be66ea501621b"],
] as const;

const SPANS = [1, 32, 44, 96, 128, 160, 320] as const;

for (const [name, recorded] of FROZEN) {
  const asShipped = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, read(name).patch);
  const moved = withMaterialOverrides(asShipped, { outerShadow: { sigmaThinOffsetPx: 5 } });

  console.log(`\n  ${name}`);
  console.log(`    recorded digest                                  ${recorded}`);
  console.log(`    as shipped, under the SHIPPED grouping           ${digestUnder(asShipped, SHIPPED)}`);
  console.log(`    as shipped, under GROUNDING's own shape          ${digestUnder(asShipped, GROUNDING)}`);
  console.log(`    as shipped, under the LOOSER grouping            ${digestUnder(asShipped, LOOSER)}`);
  console.log(`    with sigmaThinOffsetPx 5, SHIPPED grouping       ${digestUnder(moved, SHIPPED)}`);
  console.log(`    with sigmaThinOffsetPx 5, GROUNDING's shape      ${digestUnder(moved, GROUNDING)}`);
  console.log(`    with sigmaThinOffsetPx 5, LOOSER grouping        ${digestUnder(moved, LOOSER)}`);
  console.log(
    `    σ at spans ${SPANS.join("/")}: shipped ` +
      SPANS.map((span) => outerShadowSigmaPx(asShipped.outerShadow, span).toFixed(2)).join("/") +
      ` → moved ` +
      SPANS.map((span) => outerShadowSigmaPx(moved.outerShadow, span).toFixed(2)).join("/"),
  );

  if (digestUnder(asShipped, SHIPPED) !== recorded) {
    fail(`${name}: the shipped grouping does not reproduce the recorded digest`);
  }
  if (digestUnder(moved, LOOSER) !== recorded) {
    fail(`${name}: the looser grouping did NOT merge the moved material into the frozen digest`);
  }
  if (digestUnder(moved, SHIPPED) === recorded) {
    fail(`${name}: the shipped grouping merged a material that draws a different σ`);
  }
  if (digestUnder(asShipped, GROUNDING) !== recorded) {
    fail(`${name}: Grounding's own shape does not reproduce the recorded digest`);
  }
  if (digestUnder(moved, GROUNDING) === recorded) {
    fail(`${name}: Grounding's own shape merged a material that draws a different σ`);
  }
  const drawsDifferently = SPANS.some(
    (span) => outerShadowSigmaPx(moved.outerShadow, span) !== outerShadowSigmaPx(asShipped.outerShadow, span),
  );
  if (!drawsDifferently) fail(`${name}: the moved material draws the same σ, so the case is vacuous`);
}

console.log(`
== what this closes ==

  The Revision Note's premise is corrected. Grounding names three leaves as
  having no standalone identity and \`sigmaThinOffsetPx\` is not one of them, so
  the charter leaves it an ordinary value drop — which the lines above show
  reproduces the frozen digests and refuses the moved material, exactly as the
  shipped shape does. **"The charter is wrong in two places" reads one**, and
  the two-leaf gate is a TIGHTENING of a correct shape: it drops a strict subset
  of what Grounding drops, so every material the shipped rule merges Grounding
  merges too, and not the other way round.

  The tightening still earns its place, which is what the LOOSER column is for —
  the shape the Note attributes to the charter, where the slope alone gates both
  the pivot and the offset. Under it a macOS 26.5 light material with
  \`sigmaThinOffsetPx\` 5 — five CSS px of extra blur on every outer shadow the
  bed carries, at every span, on both tiers — fingerprints to
  \`b2b570e4adcea8fb\`, the frozen digest itself. That is the merge a gate-group
  drop risks when the gate is not the narrowest thing that closes the leaf, and
  it is the reason the σ entry's gate is two leaves.
`);

console.log(failures === 0 ? "CLOSURE PROOF OK — no failures" : `CLOSURE PROOF FAILED — ${failures} failure(s)`);
process.exit(failures === 0 ? 0 : 1);
