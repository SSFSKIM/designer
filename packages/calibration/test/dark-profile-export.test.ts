/**
 * X7 — one source: the shipped dark patch and the dark profile document are the
 * same numbers (W21 spec, G3 and Cross-Child Contract X7).
 *
 * The dark scheme is measured here and drawn there. `@vitreajs/vitrea-web`
 * exports `darkMaterialProfile` so that a host in dark mode gets the dark
 * material without reaching into a private, Node-shaped calibration package —
 * which means the numbers now exist in two files, and the same drift
 * `tuned-profiles.test.ts` opens by describing becomes possible one package
 * along.
 *
 * This is the pin. The export is GENERATED from the document by
 * `packages/platform-web/scripts/generate-dark-profile.mjs`, so closing the drift
 * is one command; this test is what makes forgetting to run it loud. A wave that
 * re-records the profile fails here until the module is regenerated and
 * committed.
 *
 * What is read here is the SHIPPED artifact: `@vitreajs/vitrea-web` resolves to
 * `dist/`, so this is the patch a consumer would install, and the chain runs
 * `build` before `test` for exactly that reason. The same comparison against the
 * source module — which needs no build and so cannot read a stale bundle — is
 * `packages/platform-web/test/color-scheme.test.ts`'s, one package along. Two
 * readings of one claim, and neither is redundant: a source module that matches
 * the document and a bundle that does not is a build nobody re-ran, which is a
 * real state and a shippable one.
 *
 * The comparison is deep and it runs in both directions on purpose. A subset
 * check either way would pass the two failures that actually matter: a constant
 * the document gained and the export never picked up (the material ships without
 * a measurement it claims to have), and a constant left in the export after the
 * document dropped it (the material ships a number nothing records).
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { darkMaterialProfile } from "@vitreajs/vitrea-web";
import type { MaterialProfilePatch } from "@vitrea/renderer-webgpu";

const DOCUMENT = JSON.parse(
  readFileSync(
    resolve(import.meta.dirname, "..", "profiles", "apple-macos-26.5-1x-dark-standard.json"),
    "utf8",
  ),
) as { readonly patch: MaterialProfilePatch };

/** Every leaf as a flat key path, so a missing one is named rather than diffed. */
const leaves = (patch: object, prefix = ""): string[] =>
  Object.entries(patch).flatMap(([key, value]) =>
    value !== null && typeof value === "object" && !Array.isArray(value)
      ? leaves(value as object, `${prefix}${key}.`)
      : [`${prefix}${key}`],
  );

describe("the shipped dark material and the dark profile document", () => {
  it("are the same patch, leaf for leaf", () => {
    expect(darkMaterialProfile).toEqual(DOCUMENT.patch);
  });

  it("name the same constants, in both directions", () => {
    const shipped = new Set(leaves(darkMaterialProfile as object));
    const recorded = new Set(leaves(DOCUMENT.patch as object));

    for (const constant of recorded) {
      expect(
        shipped,
        `${constant}: recorded in the dark profile document and absent from the shipped ` +
          `patch — regenerate packages/platform-web/src/dark-profile.ts ` +
          `(pnpm --filter @vitreajs/vitrea-web run profile:dark)`,
      ).toContain(constant);
    }
    for (const constant of shipped) {
      expect(
        recorded,
        `${constant}: shipped in the dark patch and recorded nowhere — a number with no ` +
          `provenance is not a measurement`,
      ).toContain(constant);
    }
  });
});
