/**
 * The identity table is APPEND-ONLY, and it is the table G0 declared (W31
 * Decision Log 1 (a) and 2 (c); claims §5.161 §7b, §5.164).
 *
 * `MATERIAL_IDENTITY_TABLE` lives beside `DEFAULT_MATERIAL_PROFILE` because a
 * post-seal leaf's default IS its identity, forever: the digests recorded
 * against it are taken with those leaves dropped at those values, so moving a
 * default off its identity — or removing an entry, or re-ordering one — would
 * move every shipped document's digest at once, silently and everywhere.
 *
 * G0 declared the table as `identity-table.json` in its own evidence directory
 * and proved the rule against the frozen digests before a leaf existed
 * (`digest-rule-proof.ts`). That file is committed evidence and is never
 * rewritten. This case is the join between it and the live constant: every
 * entry G0 declared is still here, in order, with the same gate, the same gated
 * leaves and the same law — and the one thing that legitimately moved is W31's
 * own `inertLawCase`, which G0 recorded as "TO BE COMMITTED BY W31 G3" because
 * the case could not exist before the leaf did.
 *
 * The append-only half is asserted as a PREFIX rather than as a length: a later
 * wave adds entries at the end and this case keeps working, while an edit to an
 * existing one fails.
 *
 * **And the file the prefix is compared against is itself pinned** (W31 G3c
 * review closure; claims §5.164 §13, finding N19). Every assertion below reads
 * `identity-table.json` and nothing read the JSON — a declaration edited to
 * match a live constant that had drifted would have made the whole file agree
 * with itself. It is committed evidence in a gate's own directory, so it has
 * exactly one correct value and that value is a literal here.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_DIGEST_RULE_VERSION,
  MATERIAL_IDENTITY_TABLE,
  materialDigestDroppedLeaves,
  materialLeafAt,
} from "@vitrea/renderer-webgpu";

interface DeclaredEntry {
  readonly wave: string;
  readonly gate: Readonly<Record<string, number>>;
  readonly gated: readonly string[];
  readonly law: string;
  readonly inertLawCase: string;
}

const DECLARATION = resolve(
  import.meta.dirname,
  "..",
  "results",
  "2026-09-21-w31-g0-chroma-cut",
  "identity-table.json",
);

const DECLARED = JSON.parse(readFileSync(DECLARATION, "utf8")) as {
  readonly rule: { readonly version: string };
  readonly entries: readonly DeclaredEntry[];
};

/**
 * G0's declaration, by its BYTES. Re-record this only with the reason a gate had
 * to edit committed evidence, which is a sentence nobody should be able to write
 * easily.
 */
const DECLARED_SHA256 = "09927a29a8add541b6278e779827181526c3f67ac3cb06e70a551996535a9489";

describe("the material identity table (claims §5.161 §7b, §5.164)", () => {
  it("compares against the declaration G0 committed, byte for byte", () => {
    const bytes = readFileSync(DECLARATION);
    expect(
      createHash("sha256").update(bytes).digest("hex"),
      "identity-table.json has been edited — it is G0's committed declaration and the whole " +
        "append-only proof below is a comparison against it",
    ).toBe(DECLARED_SHA256);
  });

  it("carries every entry G0 declared, in order, unedited", () => {
    expect(MATERIAL_IDENTITY_TABLE.length).toBeGreaterThanOrEqual(DECLARED.entries.length);
    DECLARED.entries.forEach((declared, index) => {
      const live = MATERIAL_IDENTITY_TABLE[index];
      expect(live, `entry ${String(index)} is missing`).toBeDefined();
      expect(live?.wave).toBe(declared.wave);
      expect(live?.gate).toStrictEqual(declared.gate);
      expect([...(live?.gated ?? [])]).toStrictEqual([...declared.gated]);
      // The rule-bearing fields are append-only and never edited. `law` is
      // prose about them: where a wave sharpened it into the shipped function's
      // own names, the declaration is kept verbatim in `declaredFirstAs` rather
      // than overwritten — which is `identity-table.json`'s own idiom, one file
      // along.
      if (live?.law !== declared.law) {
        expect(live?.declaredFirstAs?.law, `${declared.wave}: law edited without a record`).toBe(
          declared.law,
        );
        expect(live?.declaredFirstAs?.inertLawCase).toBe(declared.inertLawCase);
      }
    });
  });

  it("pins each entry's identity as a LITERAL, not only as the default's value", () => {
    /*
     * W31 G3c review closure (claims §5.164 §13, finding N19). The case below
     * asserts that `DEFAULT_MATERIAL_PROFILE` holds each gate at the identity
     * the TABLE records — a comparison of two things that move together, since
     * a wave editing the table to follow a moved default satisfies it. The
     * identities are recorded here as literals too, so the pair can only agree
     * with a number a human wrote down.
     *
     * Append a line when a wave appends an entry; never edit one. Every value
     * is 0 today and that is not an accident — a post-seal leaf's inert
     * identity is what its default is sealed at — but the zero is written out
     * rather than looped over, because a table of zeroes checked by a loop over
     * zeroes proves nothing about the entry that is not one.
     */
    const IDENTITIES: Readonly<Record<string, number>> = {
      "outerShadow.sigmaSlopePerSpan": 0,
      "outerShadow.sigmaThinOffsetPx": 0,
      sizeHeavySecondShare: 0,
      sizeScatterScaleGain: 0,
      bodyChromaRetention: 0,
      backdropToneBlackStrength: 0,
    };
    const gates = MATERIAL_IDENTITY_TABLE.flatMap((entry) => Object.entries(entry.gate));
    for (const [path, identity] of gates) {
      expect(
        IDENTITIES[path],
        `${path}: gated by the table and pinned by no literal here — add one, with the wave`,
      ).toBe(identity);
    }
    for (const path of Object.keys(IDENTITIES)) {
      expect(
        gates.map(([name]) => name),
        `${path}: pinned here and no longer a gate in the table — an entry was removed`,
      ).toContain(path);
    }
  });

  it("names a committed case for every entry, W31's included", () => {
    // G0 could not name W31's case — the leaf did not exist — and recorded the
    // gap in words. The gap is what this case closes: every entry now points at
    // a file and a case name, and the three W30 entries still point at the ones
    // the review closure moved them to.
    for (const entry of MATERIAL_IDENTITY_TABLE) {
      expect(entry.inertLawCase, `${entry.wave}: no case named`).toMatch(/\.test\.ts|\.spec\.ts/);
      expect(entry.inertLawCase).not.toContain("TO BE COMMITTED");
    }
    const w31 = MATERIAL_IDENTITY_TABLE.filter((entry) => entry.wave === "W31");
    expect(w31.length).toBe(1);
    expect(w31[0]?.inertLawCase).toContain("w31-body-chroma.test.ts");
  });

  it("holds every gate leaf at its declared identity in the runtime default", () => {
    // The append-only constraint, stated as the thing that would break: a
    // default that moves off an identity moves every document's digest.
    for (const entry of MATERIAL_IDENTITY_TABLE) {
      for (const [path, identity] of Object.entries(entry.gate)) {
        expect(
          materialLeafAt(DEFAULT_MATERIAL_PROFILE, path),
          `${path}: the default has moved off the identity the table records`,
        ).toBe(identity);
      }
      for (const gated of entry.gated) {
        expect(
          materialLeafAt(DEFAULT_MATERIAL_PROFILE, gated),
          `${gated}: named as gated, absent from the material`,
        ).not.toBe(undefined);
      }
    }
  });

  it("drops every named leaf on the runtime default, and the rule has a version", () => {
    const dropped = new Set(materialDigestDroppedLeaves(DEFAULT_MATERIAL_PROFILE));
    const named = MATERIAL_IDENTITY_TABLE.flatMap((entry) => [
      ...Object.keys(entry.gate),
      ...entry.gated,
    ]);
    for (const leaf of named) expect(dropped, `${leaf}`).toContain(leaf);
    expect(dropped.size).toBe(named.length);
    expect(MATERIAL_DIGEST_RULE_VERSION).toBe(2);
    // G0's declaration names the rule's own revision; the numeric version above
    // is what a document RECORDS, and rule 1 is the plain resolved digest.
    expect(DECLARED.rule.version).toBe("w31-identity-1");
  });

  it("drops nothing where a gate is off its identity, so the rule discriminates", () => {
    for (const entry of MATERIAL_IDENTITY_TABLE) {
      const [path] = Object.keys(entry.gate);
      if (path === undefined) continue;
      const opened = structuredClone(DEFAULT_MATERIAL_PROFILE) as unknown as Record<string, unknown>;
      const parts = path.split(".");
      let node = opened;
      for (const key of parts.slice(0, -1)) node = node[key] as Record<string, unknown>;
      const leaf = parts[parts.length - 1] as string;
      node[leaf] = (node[leaf] as number) + 1;
      const dropped = materialDigestDroppedLeaves(opened);
      for (const name of [...Object.keys(entry.gate), ...entry.gated]) {
        expect(dropped, `${name}: dropped while ${path} is off its identity`).not.toContain(name);
      }
    }
  });
});
