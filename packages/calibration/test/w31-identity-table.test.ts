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
 */

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

const DECLARED = (
  JSON.parse(
    readFileSync(
      resolve(
        import.meta.dirname,
        "..",
        "results",
        "2026-09-21-w31-g0-chroma-cut",
        "identity-table.json",
      ),
      "utf8",
    ),
  ) as { readonly rule: { readonly version: string }; readonly entries: readonly DeclaredEntry[] }
);

describe("the material identity table (claims §5.161 §7b, §5.164)", () => {
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
